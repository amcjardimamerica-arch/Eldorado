"""MISSÕES ESPECIAIS — resgate de edital incompleto.

Os outros 28 motores acham editais o tempo todo, mas muitos chegam pela metade: o título
está lá, a página oficial não; o prazo não foi lido; ninguém sabe que documentos anexar.
Sem isso o edital não serve para nada — não dá para decidir se vale concorrer.

Este módulo monta a FILA DE RESGATE: todo edital do acervo a que falte informação mínima
entra aqui, e o Piloto atende essa fila ANTES de sair explorando. Resgatar um edital que já
temos vale mais do que descobrir um que ainda não sabemos usar.

O MÍNIMO que um edital precisa ter para o sistema trabalhar com ele:
    página oficial · prazo de inscrição · quem pode concorrer · documentos exigidos ·
    valor ou faixa de valor · como se inscreve

O que o Piloto completa vai para a ficha do edital na Biblioteca de Alexandria.
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json

FILA = ROOT / "estado/sindico/fila_resgate.json"
PUB = ROOT / "docs/dados/resgates_piloto.json"
MINIMO = ("pagina_oficial", "prazo", "quem_pode", "documentos", "valor", "como_inscrever")
PESO = {"pagina_oficial": 5, "prazo": 5, "documentos": 3, "como_inscrever": 3, "quem_pode": 2, "valor": 2}


def _falta(e: dict) -> list[str]:
    """O que impede este edital de ser usado."""
    f = []
    if not (e.get("pagina_oficial") or e.get("url") or e.get("onde")):
        f.append("pagina_oficial")
    if not (e.get("prazo") or e.get("fim") or e.get("inscricoes_ate")):
        f.append("prazo")
    if not (e.get("quem_pode") or e.get("publico")):
        f.append("quem_pode")
    if not (e.get("documentos") or e.get("anexos")):
        f.append("documentos")
    if not (e.get("valor") or e.get("valor_total") or e.get("faixa")):
        f.append("valor")
    if not (e.get("como_inscrever") or e.get("onde_inscrever") or e.get("inscricao")):
        f.append("como_inscrever")
    return f


# A associação é de assistência social e cultura. Um credenciamento de leiloeiros ou um
# cadastro de profissionais de saúde é edital incompleto, sim — mas nao serve para nada aqui.
# Sem este filtro, 25 das 60 missoes foram gastas resgatando papel que nunca seria usado.
SERVE = ("assistência social", "assistencia social", "cultura", "cultural", "esporte", "lazer",
         "criança", "crianca", "adolescente", "idoso", "juventude", "pessoa com deficiência",
         "organização da sociedade civil", "organizacao da sociedade civil", "osc", "terceiro setor",
         "fomento", "colaboração", "colaboracao", "parceria", "mrosc", "chamamento público de projetos",
         "seleção de projetos", "selecao de projetos", "subvenção", "subvencao", "emenda",
         "oficina", "capacitação", "capacitacao", "inclusão", "inclusao", "vulnerabilidade",
         "convivência", "convivencia", "socioeducativ", "socioassistencial", "cras", "creas",
         "patrocínio", "patrocinio", "edital de apoio", "prêmio", "premio")
NAO_SERVE = ("leiloeiro", "profissionais de saúde", "profissionais de saude", "médico", "medico",
             "medicamento", "insumo hospitalar", "órtese", "ortese", "prótese", "protese",
             "locação de veículo", "locacao de veiculo", "combustível", "combustivel",
             "obra", "pavimentação", "pavimentacao", "reforma predial", "merenda", "gênero alimentício",
             "genero alimenticio", "material de expediente", "coleta de lixo", "engenharia",
             "estabelecimento de saúde", "estabelecimento de saude", "laboratório", "laboratorio",
             "exames", "consulta médica", "consulta medica", "transporte escolar", "vigilância", "vigilancia")


def _relevante(e: dict) -> tuple[bool, str]:
    """Este edital serve à nossa associação? Devolve (serve, por quê)."""
    txt = " ".join(str(e.get(c) or "") for c in ("titulo", "objeto", "orgao", "familia")).lower()
    for n in NAO_SERVE:
        if n in txt:
            return False, f"fora do nosso objeto ({n})"
    achou = [s for s in SERVE if s in txt]
    if achou:
        return True, "serve: " + ", ".join(achou[:3])
    return False, "não diz respeito a projeto de OSC"


def _urgencia(e: dict, falta: list[str]) -> int:
    """Quanto este resgate importa. Falta grave pesa mais; edital de Goiás e recente pesa mais."""
    p = sum(PESO.get(x, 1) for x in falta)
    if (e.get("uf") or "").upper() == "GO":
        p += 6
    if str(e.get("prazo") or e.get("fim") or "") >= date.today().isoformat():
        p += 8                                        # ainda dá tempo de concorrer: prioridade máxima
    if (e.get("veredito") or "") in ("aprovado", "atencao"):
        p += 4
    if (e.get("familia") or "") in ("cultura", "assistencia", "esporte", "terceiro_setor"):
        p += 3
    return p


def _acervo() -> list[dict]:
    """Os editais que o sistema já conhece, venham de onde vierem."""
    saida = []
    base = sorted((ROOT / "dados/editais").glob("*-eldorado-*-completo.json"), reverse=True)
    if base:
        itens = load_json(base[0]).get("itens") or {}
        for k, e in (itens.items() if isinstance(itens, dict) else enumerate(itens)):
            saida.append({"id": str(k), "titulo": (e.get("objeto") or "")[:130], "uf": e.get("uf"),
                          "orgao": e.get("orgao"), "pagina_oficial": e.get("pagina_oficial"),
                          "prazo": e.get("fim"), "veredito": e.get("veredito"), "familia": e.get("familia"),
                          "origem": "acervo PNCP/motores", **{c: e.get(c) for c in ("quem_pode", "documentos", "valor", "como_inscrever") if e.get(c)}})
    ach = ROOT / "docs/dados/achados_dia.json"
    if ach.exists():
        d = load_json(ach)
        for e in (d.get("itens") or d.get("achados") or [])[:400]:
            saida.append({"id": "achado-" + re.sub(r"[^a-z0-9]", "", str(e.get("titulo", "")).lower())[:30],
                          "titulo": (e.get("titulo") or "")[:130], "uf": e.get("uf"),
                          "pagina_oficial": e.get("url") or e.get("onde"), "prazo": e.get("prazo"),
                          "origem": f"motor {e.get('motor') or '?'}"})
    return saida


def montar_fila(limite: int = 60) -> dict:
    """Varre o acervo e separa o que está incompleto, do mais urgente ao menos."""
    ja = load_json(FILA) if FILA.exists() else {}
    descartados: dict[str, int] = {}
    feitos = {k for k, v in (ja.get("itens") or {}).items() if v.get("estado") == "resgatado"}
    tentados = {k: v.get("tentativas", 0) for k, v in (ja.get("itens") or {}).items()}
    itens = {}
    for e in _acervo():
        if e["id"] in feitos or tentados.get(e["id"], 0) >= 3:      # três tentativas e a gente desiste
            continue
        f = _falta(e)
        if not f or not e.get("titulo"):
            continue
        serve, porque = _relevante(e)
        if not serve:
            descartados[porque[:40]] = descartados.get(porque[:40], 0) + 1
            continue
        itens[e["id"]] = {**e, "falta": f, "urgencia": _urgencia(e, f), "serve_porque": porque,
                          "estado": "aguardando", "tentativas": tentados.get(e["id"], 0)}
    ordenada = dict(sorted(itens.items(), key=lambda kv: -kv[1]["urgencia"])[:limite])
    d = {"em": now_iso(), "total_incompletos": len(itens), "na_fila": len(ordenada),
         "descartados_por_nao_servirem": descartados,
         "regra": "o Piloto atende esta fila ANTES de explorar: completar um edital que já temos vale mais que achar outro pela metade",
         "itens": {**{k: v for k, v in (ja.get("itens") or {}).items() if v.get("estado") == "resgatado"}, **ordenada}}
    write_json(FILA, d)
    return {k: v for k, v in d.items() if k != "itens"}


def proximo(reservar: bool = True) -> dict | None:
    """O edital mais urgente à espera de resgate. Por padrão RESERVA o item (grava
    'em_resgate' no arquivo), senão a próxima chamada devolveria o mesmo de novo — foi
    assim que o voo saía com um resgate só em vez dos seis."""
    if not FILA.exists():
        montar_fila()
    d = load_json(FILA)
    pend = [(k, v) for k, v in (d.get("itens") or {}).items() if v.get("estado") == "aguardando"]
    if not pend:
        return None
    k, v = max(pend, key=lambda kv: kv[1].get("urgencia", 0))
    if reservar:
        d["itens"][k]["estado"] = "em_resgate"
        write_json(FILA, d)
    return {"id": k, **v}


def plano_de_voo(ia, alvo: dict) -> dict:
    """O briefing da missão especial: o Piloto decide COMO achar o que falta neste edital."""
    r = ia.perguntar(
        "MISSÃO ESPECIAL — RESGATE DE EDITAL. Um edital já está no nosso acervo, mas incompleto, "
        "e sem esses dados ele não serve para decidir se vale concorrer.\n\n"
        f"EDITAL: {alvo.get('titulo')}\n"
        f"ÓRGÃO/FONTE: {alvo.get('orgao') or alvo.get('origem')}\n"
        f"UF: {alvo.get('uf') or '?'}\n"
        f"JÁ TEMOS: {json.dumps({k: v for k, v in alvo.items() if k in MINIMO and v}, ensure_ascii=False)}\n"
        f"FALTA: {alvo.get('falta')}\n\n"
        "Escreva consultas de busca que levem à PÁGINA OFICIAL deste edital específico (não a notícia sobre ele): "
        "o site do órgão, o portal onde foi publicado, o PDF do edital, a página de inscrições. "
        "Use o nome do órgão e o número ou nome do edital nas consultas.",
        '{"consultas": ["consulta 1", "consulta 2", "consulta 3"], '
        '"onde_provavelmente_esta": "site ou portal onde isto costuma ser publicado", '
        '"o_que_ler_na_pagina": ["prazo", "documentos exigidos", "..."]}')
    return {"id": "resgate-" + str(alvo.get("id"))[:28],
            "pergunta": f"Onde está a página oficial de: {alvo.get('titulo')} ({alvo.get('orgao') or ''})? "
                        f"Preciso de {', '.join(alvo.get('falta') or [])}.",
            "consultas_sugeridas": [c for c in ((r or {}).get("consultas") or []) if isinstance(c, str)][:3],
            "onde_procurar": (r or {}).get("onde_provavelmente_esta"),
            "o_que_ler": (r or {}).get("o_que_ler_na_pagina") or list(alvo.get("falta") or []),
            "nivel": "resgate", "alvo": "edital", "origem": "missao_especial", "edital": alvo}


def devolver_a_fila(alvo_id: str) -> None:
    """Item reservado mas não atendido (o voo acabou antes) volta a aguardar."""
    if not FILA.exists():
        return
    d = load_json(FILA)
    it = (d.get("itens") or {}).get(alvo_id)
    if it and it.get("estado") == "em_resgate":
        it["estado"] = "aguardando"
        write_json(FILA, d)


def registrar_resgate(alvo_id: str, dados: dict, achou: bool) -> dict:
    d = load_json(FILA) if FILA.exists() else {"itens": {}}
    it = (d.get("itens") or {}).get(alvo_id)
    if not it:
        return {}
    it["tentativas"] = it.get("tentativas", 0) + 1
    if achou:
        it.update({k: v for k, v in dados.items() if v})
        it["falta"] = _falta(it)
        it["estado"] = "resgatado" if not it["falta"] else "parcial"
        it["resgatado_em"] = now_iso()[:16]
        if it["estado"] == "resgatado":
            _para_biblioteca(alvo_id, it)
    else:
        it["estado"] = "aguardando" if it["tentativas"] < 3 else "sem_sucesso"
    d["em"] = now_iso()
    write_json(FILA, d)
    publicar()
    return it


def _para_biblioteca(alvo_id: str, it: dict) -> None:
    """Edital completo vira ficha na Biblioteca de Alexandria."""
    pasta = ROOT / "biblioteca_alexandria/oportunidades" / re.sub(r"[^a-z0-9-]", "-", str(it.get("titulo", ""))[:60].lower()).strip("-") / str(date.today().year)
    pasta.mkdir(parents=True, exist_ok=True)
    write_json(pasta / "ficha.json", {
        "titulo": it.get("titulo"), "orgao": it.get("orgao"), "uf": it.get("uf"),
        "pagina_oficial": it.get("pagina_oficial"), "prazo": it.get("prazo"),
        "quem_pode": it.get("quem_pode"), "documentos": it.get("documentos"),
        "valor": it.get("valor"), "como_inscrever": it.get("como_inscrever"),
        "situacao": "aberta" if str(it.get("prazo") or "") >= date.today().isoformat() else "arquivada",
        "completado_por": "Piloto (missão especial de resgate)", "em": now_iso(), "id_fila": alvo_id})


def publicar() -> dict:
    d = load_json(FILA) if FILA.exists() else {"itens": {}}
    its = d.get("itens") or {}
    por = {}
    for v in its.values():
        por[v.get("estado") or "?"] = por.get(v.get("estado") or "?", 0) + 1
    saida = {"em": now_iso(), "total": len(its), "por_estado": por,
             "regra": "missão especial tem prioridade sobre exploração",
             "fila": [{"id": k, "titulo": v.get("titulo"), "uf": v.get("uf"), "orgao": v.get("orgao"),
                       "falta": v.get("falta"), "urgencia": v.get("urgencia"), "estado": v.get("estado"),
                       "tentativas": v.get("tentativas"), "pagina_oficial": v.get("pagina_oficial")}
                      for k, v in sorted(its.items(), key=lambda kv: (kv[1].get("estado") != "aguardando", -(kv[1].get("urgencia") or 0)))[:60]]}
    write_json(PUB, saida)
    return {k: v for k, v in saida.items() if k != "fila"}


if __name__ == "__main__":
    print(json.dumps({**montar_fila(), **publicar()}, ensure_ascii=False, indent=1))
