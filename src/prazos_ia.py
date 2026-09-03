"""Busca de PRAZO por IA — para o chamamento que existiu, mas não tem prazo.

Regra do titular: um ícone no calendário sem faixa contínua confirma que houve
um chamamento — e o prazo tem de ser perseguido de imediato, em níveis:

  1. modelo SIMPLES (barato) com prompt feito para achar EXATAMENTE o local de
     publicação original do edital — o diário, a página do órgão, o link que
     está disponível — e dele o prazo de inscrição;
  2. se não obtiver, a resposta entra no HISTÓRICO da oportunidade e sobe para
     o modelo AVANÇADO com a regra do conselho: por que a tentativa simples não
     achou o edital ou a fonte, e qual a forma de obter.

Estado: `estado/prazos_ia.json` — { edital_id: {tentativas:[...], prazo?, url?, status} }.
Só oportunidades do núcleo com evento registrado e situação 'possível'; cap por
saída para economizar tokens. Prazo obtido só vale depois que o sensor abrir o
link e confirmar — aqui ele fica como 'prazo indicado pela IA (a confirmar)'.
"""
from __future__ import annotations

import json
import os
import re
from datetime import date

from .nucleo import ROOT, load_json, now_iso, write_json
from .opressores import _chamar

ESTADO = ROOT / "estado/prazos_ia.json"


def _prompt_simples(e: dict) -> str:
    return (f"Oportunidade: {e.get('titulo')}\nÓrgão/fonte: {e.get('fonte_nome') or e.get('orgao')} — {e.get('uf') or 'Brasil'} ({e.get('nivel')}).\n"
            f"Publicação conhecida: {e.get('url') or 'nenhuma'}; evidência: {(e.get('objeto') or e.get('resumo') or '')[:300]}.\n"
            "Encontre EXATAMENTE o local de publicação ORIGINAL deste edital/chamamento (diário oficial e edição, página do órgão, "
            "ou o link disponível) e extraia o PERÍODO DE INSCRIÇÃO. Responda SOMENTE JSON: "
            "{\"url_publicacao\": <URL oficial ou null>, \"inicio\": <AAAA-MM-DD ou null>, \"fim\": <AAAA-MM-DD ou null>, "
            "\"onde\": <\"diário oficial\"|\"site do órgão\"|\"PNCP\"|\"outro\">, \"trecho\": <frase do edital com o prazo ou null>}. Nunca invente.")


def _prompt_conselho(e: dict, historico: list[dict]) -> str:
    return (f"Conselho de sete lentes (extremamente pessimista a extremamente otimista; um neutro decide). Oportunidade: "
            f"{e.get('titulo')} — {e.get('fonte_nome')} ({e.get('uf') or 'Brasil'}). Um modelo simples NÃO obteve o edital nem o prazo; "
            f"histórico: {json.dumps(historico, ensure_ascii=False)[:1200]}.\n"
            "Cada lente diz em uma frase POR QUE não se achou (edital só em PDF da edição? página do órgão sem listagem? "
            "chamamento por dispensa, sem prazo? nome diferente na publicação? bloqueio a robô?). O neutro decide a forma de obter "
            "— qual diário/edição/data, qual URL, qual termo — e TENTA agora com busca na web. Responda SOMENTE JSON: "
            "{\"lentes\": {<lente>: <frase>}, \"decisao\": <texto>, \"url_publicacao\": <URL ou null>, \"inicio\": <AAAA-MM-DD ou null>, "
            "\"fim\": <AAAA-MM-DD ou null>, \"trecho\": <frase ou null>}.")


def candidatos(dados: dict, limite: int) -> list[dict]:
    """Editais do núcleo com evento registrado (chamamento existiu) e sem prazo confirmado."""
    ids_ev = {ev.get("edital_id") for ev in dados.get("eventos", [])}
    est = load_json(ESTADO) if ESTADO.exists() else {}
    saida = []
    for e in dados.get("editais", []):
        if e["id"] not in ids_ev or e.get("situacao_inscricao") != "possivel":
            continue
        # regra anual / janela confirmada / permanente já tem prazo (só não abriu ainda)
        if e.get("sem_edital") or e.get("janela_confirmada") or e.get("regra_anos") \
                or e.get("regime_inscricao") in ("anual", "janela_confirmada", "permanente"):
            continue
        r = est.get(e["id"], {})
        if r.get("status") in ("prazo_indicado", "conselho_emitido"):
            continue
        saida.append(e)
    saida.sort(key=lambda e: (e.get("uf") != "GO", e.get("publicado_em") or ""), reverse=False)
    return saida[:limite]


def run(limite: int = 12) -> dict:
    dd = ROOT / "docs/dashboard-dados.json"
    if not dd.exists():
        return {"erro": "painel ainda não gerado"}
    dados = load_json(dd)
    est = load_json(ESTADO) if ESTADO.exists() else {}
    cfg = load_json(ROOT / "config/ia.json") if (ROOT / "config/ia.json").exists() else {}
    cadeia = (cfg.get("escalada_busca") or {}).get("cadeia") or []
    simples = cadeia[0]["modelo"] if cadeia else "claude-haiku-4-5"
    avancado = (cfg.get("modelos") or {}).get("conselho_recursos", "claude-fable-5-1")
    n_simples = n_conselho = n_prazo = 0
    for e in candidatos(dados, limite):
        r = est.setdefault(e["id"], {"titulo": (e.get("titulo") or "")[:120], "tentativas": []})
        # nível 1 — modelo simples, prompt do local de publicação
        if not any(t["nivel"] == "simples" for t in r["tentativas"]):
            resp = _chamar(simples, _prompt_simples(e), 600)
            n_simples += 1
            ok = bool(resp.get("fim"))
            r["tentativas"].append({"nivel": "simples", "modelo": simples, "em": now_iso(), "status": resp.get("status"),
                                    "obteve_prazo": ok, "url": resp.get("url_publicacao"), "onde": resp.get("onde"),
                                    "resumo": f'{resp.get("status")}: {"prazo "+resp["fim"] if ok else "sem prazo"}'})
            if ok:
                r.update({"status": "prazo_indicado", "inicio": resp.get("inicio"), "fim": resp["fim"],
                          "url": resp.get("url_publicacao"), "trecho": resp.get("trecho"),
                          "nota": "prazo indicado pela IA — vale após o sensor abrir o link e confirmar"})
                n_prazo += 1
                continue
            if "credencial" in str(resp.get("status")):
                r["status"] = "aguardando_credencial"; continue
            r["status"] = "simples_sem_resultado"
        # nível 2 — avançado com a regra do conselho (por que não achou) e nova tentativa
        if r.get("status") == "simples_sem_resultado" and not r.get("conselho"):
            resp = _chamar(avancado, _prompt_conselho(e, r["tentativas"]), 1400)
            n_conselho += 1
            r["conselho"] = {"modelo": avancado, "em": now_iso(), "lentes": resp.get("lentes"), "decisao": resp.get("decisao"),
                             "status": resp.get("status")}
            r["tentativas"].append({"nivel": "conselho", "modelo": avancado, "em": now_iso(), "status": resp.get("status"),
                                    "obteve_prazo": bool(resp.get("fim")), "url": resp.get("url_publicacao"),
                                    "resumo": f'{resp.get("status")}: {"prazo "+resp["fim"] if resp.get("fim") else "sem prazo"}'})
            if resp.get("fim"):
                r.update({"status": "prazo_indicado", "inicio": resp.get("inicio"), "fim": resp["fim"],
                          "url": resp.get("url_publicacao"), "trecho": resp.get("trecho"),
                          "nota": "prazo indicado pelo conselho — vale após o sensor confirmar"})
                n_prazo += 1
            else:
                r["status"] = "conselho_emitido"
    est_meta = {k: v for k, v in est.items() if not k.startswith("_")}
    est_meta["_atualizado_em"] = now_iso()
    write_json(ESTADO, est_meta)
    return {"simples": n_simples, "conselho": n_conselho, "prazos_indicados": n_prazo, "executado_em": now_iso()}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
