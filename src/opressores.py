"""Disjuntores dos Motores Opressores — a chave que liga um recurso por 30 dias.

Regra do titular: quando um Motor Opressor é acionado — automaticamente (época
prevista ou menção nos motores regulares) ou manualmente (poça de óleo → fogo)
— ele fica LIGADO por 30 dias, pesquisando todos os dias. A cada 3 dias entra
uma IA com um prompt feito para AQUELE recurso (economizando tokens: modelo
barato, pergunta fechada, só o que ainda falta). No 3º acionamento da IA (dia
9) entra o modelo forte (Fable 5.1) com a opinião do conselho sobre por que as
duas primeiras tentativas não obtiveram resultado — e a decisão mais
inteligente para fechar os 12 itens do recurso.

Estado: `estado/opressores.json`
  { "ligados": { fonte_id: { "desde", "ate", "origem", "dias": N,
                              "ia": [ {dia, modelo, resultado, itens_obtidos} ],
                              "conselho": {...}, "itens": {...} } } }
"""
from __future__ import annotations

import json
import os
import re
from datetime import date, timedelta

from .nucleo import ROOT, load_json, now_iso, write_json

ESTADO = ROOT / "estado/opressores.json"
DURACAO = 30
INTERVALO_IA = 3
ITENS = ("Objeto", "Prazo de inscrição", "Resultado", "Prazo de recurso", "Valor", "Órgão / financiador",
         "Território", "Esfera", "Requisitos", "Anexos", "Destinação", "Área de atuação")


def _estado() -> dict:
    return load_json(ESTADO) if ESTADO.exists() else {"ligados": {}}


def _fontes() -> dict[str, dict]:
    m = ROOT / "biblioteca_alexandria/fontes/motores.json"
    return {x["id"]: x for x in load_json(m).get("motores", [])} if m.exists() else {}


def _regramento(fonte: dict) -> dict | None:
    rg = ROOT / "config/regramentos.json"
    if not rg.exists():
        return None
    toks = {t for t in re.findall(r"[a-zà-ú]{5,}", (fonte.get("programa") or "").lower())}
    melhor, nota = None, 0
    for r in load_json(rg).get("regramentos", []):
        n = len(toks & {t for t in re.findall(r"[a-zà-ú]{5,}", r["fonte"].lower())})
        if n > nota:
            melhor, nota = r, n
    return melhor


def proximidade(fonte: dict, hoje: date) -> str:
    """cinza: sem época prevista · rosa: época nos próximos 45 dias (ainda não
    ligado) · (ligado é tratado à parte)."""
    pd = fonte.get("proxima_data") or {}
    ini = pd.get("inicio") or (pd.get("mes") + "-01" if pd.get("mes") else None)
    if not ini:
        return "cinza"
    try:
        d = date.fromisoformat(ini[:10])
    except ValueError:
        return "cinza"
    return "rosa" if 0 <= (d - hoje).days <= 45 else "cinza"


def sincronizar(hoje: date | None = None) -> dict:
    """Liga (30 dias) o que a ativação automática ou o titular acionou; desliga
    o que expirou. Fonte de verdade das decisões manuais: config/motores_ativos.json."""
    hoje = hoje or date.today()
    est = _estado()
    fontes = _fontes()
    auto = load_json(ROOT / "estado/ativacao_fontes.json").get("ativas", {}) if (ROOT / "estado/ativacao_fontes.json").exists() else {}
    man = load_json(ROOT / "config/motores_ativos.json") if (ROOT / "config/motores_ativos.json").exists() else {}
    acesos = man.get("acesos_manualmente") or []
    desligados = set(man.get("inativos") or [])
    for fid, motivo in auto.items():
        if fid in desligados or fid in est["ligados"]:
            continue
        est["ligados"][fid] = {"desde": hoje.isoformat(), "ate": (hoje + timedelta(days=DURACAO)).isoformat(),
                              "origem": f"automática: {motivo}", "dias": 0, "ia": [], "itens": {}}
    for a in acesos:
        fid = a["id"] if isinstance(a, dict) else a
        em = (a.get("em") if isinstance(a, dict) else None) or hoje.isoformat()
        if fid in est["ligados"] or fid not in fontes:
            continue
        d0 = date.fromisoformat(em[:10])
        if (hoje - d0).days >= DURACAO:
            continue
        est["ligados"][fid] = {"desde": d0.isoformat(), "ate": (d0 + timedelta(days=DURACAO)).isoformat(),
                              "origem": "manual: acionado pelo titular", "dias": (hoje - d0).days, "ia": [], "itens": {}}
    for fid in list(est["ligados"]):
        if est["ligados"][fid]["ate"] < hoje.isoformat() or fid in desligados:
            est.setdefault("historico", []).append({**est["ligados"].pop(fid), "id": fid, "desligado_em": hoje.isoformat()})
    est["historico"] = (est.get("historico") or [])[-200:]
    write_json(ESTADO, est)
    return {"ligados": len(est["ligados"])}


def prompt_para_fonte(fonte: dict, reg: dict | None, faltam: list[str], tentativas: list[dict]) -> str:
    """Prompt sob medida para o recurso — muda a cada caso: nome, órgão, norma,
    léxico próprio, o que já se tem e o que ainda falta."""
    return (f"Recurso: {fonte.get('programa')} — órgão: {fonte.get('orgao')} ({fonte.get('esfera')}, {fonte.get('natureza')}).\n"
            + (f"Norma que rege: {', '.join(n['ref'] for n in reg.get('normas', []))}. Página oficial: {reg.get('pagina_oficial')}. "
               f"Léxico próprio: {', '.join(reg.get('lexico_proprio', [])[:10])}.\n" if reg else
               f"Página conhecida: {fonte.get('pagina')}.\n")
            + f"Itens que AINDA FALTAM (só estes): {', '.join(faltam)}.\n"
            + (f"Tentativas anteriores sem resultado: {'; '.join(t.get('resumo','') for t in tentativas)}.\n" if tentativas else "")
            + "Encontre o edital/ato VIGENTE ou o mais recente deste recurso em fonte oficial e devolva SOMENTE JSON: "
              "{\"url_edital\": <URL oficial ou null>, \"itens\": {<item>: <valor ou null>}, \"onde_publica\": [URLs]}. "
              "Nunca invente; sem fonte oficial, use null.")


def prompt_conselho(fonte: dict, reg: dict | None, tentativas: list[dict], faltam: list[str]) -> str:
    return (f"Você é um conselho de sete lentes (extremamente pessimista a extremamente otimista, com um neutro decisor) "
            f"sobre a captação do recurso '{fonte.get('programa')}' ({fonte.get('orgao')}). Duas buscas por IA não obtiveram "
            f"os itens: {', '.join(faltam)}. O que foi tentado: {json.dumps(tentativas, ensure_ascii=False)[:1500]}.\n"
            + (f"Norma: {', '.join(n['ref'] for n in reg.get('normas', []))}; página oficial {reg.get('pagina_oficial')}.\n" if reg else "")
            + "Cada lente explica em uma frase POR QUE as tentativas falharam (página bloqueada? edital não publicado neste "
              "ano? fonte só publica em diário? nome do programa mudou? recurso é permanente sem edital?). O neutro decide "
              "a forma mais inteligente de obter TODOS os dados — qual URL abrir, qual termo buscar, qual diário/seção/data, "
              "se cabe pedido LAI — e tenta obtê-los agora com busca na web. Devolva JSON: "
              "{\"lentes\": {<lente>: <frase>}, \"decisao\": <texto>, \"url_edital\": <URL ou null>, \"itens\": {<item>: <valor ou null>}}.")


def _orcamento(tarefa: str | None) -> dict:
    """5% do limite do período por edital/tarefa (regra do titular). Lê o consumo já
    registrado em estado/ia_uso.jsonl no mês corrente."""
    cfg = load_json(ROOT / "config/ia.json") if (ROOT / "config/ia.json").exists() else {}
    o = cfg.get("orcamento") or {}
    limite = int(os.environ.get((o.get("limite_tokens_periodo") or {}).get("env", "FAROL_AI_LIMITE_TOKENS"), 0) or (o.get("limite_tokens_periodo") or {}).get("padrao", 2_000_000))
    teto = int(limite * float(o.get("percentual_por_edital", 0.05)))
    gasto = 0
    arq = ROOT / "estado/ia_uso.jsonl"
    mes = now_iso()[:7]
    if arq.exists() and tarefa:
        for l in arq.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(l)
                if r.get("tarefa") == tarefa and (r.get("em") or "")[:7] == mes:
                    u = r.get("uso") or {}; gasto += int(u.get("input_tokens", 0)) + int(u.get("output_tokens", 0))
            except Exception:
                pass
    return {"limite_periodo": limite, "teto_tarefa": teto, "gasto_tarefa": gasto, "disponivel": max(0, teto - gasto)}


def _chamar(modelo: str, prompt: str, max_tokens: int = 900, web: bool = False, tarefa: str | None = None) -> dict:
    import urllib.request
    if not os.environ.get("FAROL_AI_API_KEY"):
        return {"status": "aguardando credencial FAROL_AI_API_KEY"}
    orc = _orcamento(tarefa)
    if tarefa and orc["disponivel"] < 500:
        return {"status": f"orçamento do edital esgotado ({orc['gasto_tarefa']}/{orc['teto_tarefa']} tokens no período)", "orcamento": orc}
    corpo = {"model": modelo, "max_tokens": min(max_tokens, max(300, orc["disponivel"]) if tarefa else max_tokens),
             "messages": [{"role": "user", "content": prompt}]}
    if web:
        corpo["tools"] = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 3}]
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=json.dumps(corpo).encode(),
                                 headers={"content-type": "application/json", "x-api-key": os.environ["FAROL_AI_API_KEY"],
                                          "anthropic-version": "2023-06-01"})
    try:
        with urllib.request.urlopen(req, timeout=150) as r:
            dados = json.loads(r.read())
    except Exception as exc:
        return {"status": f"falha: {type(exc).__name__}"}
    texto = " ".join(b.get("text", "") for b in dados.get("content", []) if b.get("type") == "text")
    with (ROOT / "estado/ia_uso.jsonl").open("a", encoding="utf-8") as h:
        h.write(json.dumps({"em": now_iso(), "modelo": modelo, "tarefa": tarefa or "opressor", "uso": dados.get("usage", {})}, ensure_ascii=False) + "\n")
    try:
        js = json.loads(re.sub(r"^```(?:json)?|```$", "", texto.strip(), flags=re.M).strip())
        return {"status": "respondeu", **js, "uso": dados.get("usage", {})}
    except Exception:
        return {"status": "resposta não estruturada", "texto": texto[:600]}


def run(hoje: date | None = None) -> dict:
    """Um dia de trabalho dos disjuntores: conta o dia de cada ligado; a cada 3
    dias aciona a IA com prompt do caso; na 3ª IA (dia 9) o conselho Fable 5.1."""
    hoje = hoje or date.today()
    sincronizar(hoje)
    est = _estado()
    fontes = _fontes()
    cfg = load_json(ROOT / "config/ia.json") if (ROOT / "config/ia.json").exists() else {}
    cadeia = (cfg.get("escalada_busca") or {}).get("cadeia") or []
    modelo_barato = (cadeia[0]["modelo"] if cadeia else "claude-haiku-4-5")
    modelo_medio = (cadeia[1]["modelo"] if len(cadeia) > 1 else "claude-sonnet-4-5")
    modelo_conselho = (cfg.get("modelos") or {}).get("conselho_recursos", "claude-fable-5-1")
    resumo = {"ligados": 0, "ia_hoje": 0, "conselho_hoje": 0, "completos": 0}
    for fid, reg in est["ligados"].items():
        f = fontes.get(fid, {"id": fid, "programa": fid})
        d0 = date.fromisoformat(reg["desde"])
        reg["dias"] = (hoje - d0).days + 1
        faltam = [i for i in ITENS if not reg["itens"].get(i)] or []
        if not faltam:
            resumo["completos"] += 1; continue
        resumo["ligados"] += 1
        # IA a cada 3 dias (dias 3, 6, 9, …); 3ª vez → conselho
        if reg["dias"] % INTERVALO_IA == 0 and not any(t["dia"] == reg["dias"] for t in reg["ia"]):
            regr = _regramento(f)
            n_ia = len(reg["ia"]) + 1
            if n_ia >= 3 and not reg.get("conselho"):
                r = _chamar(modelo_conselho, prompt_conselho(f, regr, reg["ia"], faltam), 1600, web=True, tarefa=f"opressor:{fid}")
                reg["conselho"] = {"dia": reg["dias"], "modelo": modelo_conselho, "em": now_iso(),
                                   "lentes": r.get("lentes"), "decisao": r.get("decisao"), "status": r.get("status")}
                resumo["conselho_hoje"] += 1
            else:
                modelo = modelo_barato if n_ia == 1 else modelo_medio
                r = _chamar(modelo, prompt_para_fonte(f, regr, faltam, reg["ia"]), web=True, tarefa=f"opressor:{fid}")
                resumo["ia_hoje"] += 1
            obtidos = {k: v for k, v in (r.get("itens") or {}).items() if v}
            reg["itens"].update(obtidos)
            if r.get("url_edital"):
                reg["url_edital"] = r["url_edital"]
            reg["ia"].append({"dia": reg["dias"], "modelo": (r.get("modelo") or ("conselho" if n_ia >= 3 else modelo)),
                              "resultado": r.get("status"), "itens_obtidos": len(obtidos),
                              "resumo": f"{r.get('status')}: {len(obtidos)} item(ns); url {'sim' if r.get('url_edital') else 'não'}"})
    est["atualizado_em"] = now_iso()
    write_json(ESTADO, est)
    return {**resumo, "executado_em": now_iso()}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
