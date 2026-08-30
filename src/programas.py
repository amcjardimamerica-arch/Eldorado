"""Identificação de programa, lei de regência e modalidade de cada edital.

Um mesmo programa publica vários editais distintos — a PNAB (Aldir Blanc) é o
caso típico: fomento a projetos, manutenção de espaços, agentes individuais,
culturas populares. O relatório precisa mostrar **cada edital individualmente**,
e não agrupar tudo sob o nome do programa.

O reconhecimento é por termo literal presente no texto capturado. O que não
casa fica como "programa não identificado", com a lacuna declarada — nunca
deduzido. Sem IA e sem tokens.
"""
from __future__ import annotations

import json
import re
import unicodedata

from .nucleo import ROOT, load_json, now_iso

# Datas de início e fim escritas na fonte.
_D = r"(\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2})"
INICIO = re.compile(
    r"(?:in[íi]cio|a partir de|abertura|inscri[çc][õo]es\s+(?:a partir de|de)|de)\s*[:\-]?\s*" + _D, re.I)
FIM = re.compile(
    r"(?:at[ée]|encerra(?:mento|m|)|fim|limite|prazo final|t[ée]rmino)\s*[:\-]?\s*" + _D, re.I)
PERIODO = re.compile(_D + r"\s*(?:a|at[ée]|-|–)\s*" + _D)

def _n(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode().lower()

def _cfg() -> dict:
    return load_json(ROOT / "config/programas.json")

def _texto(item: dict) -> str:
    return _n(" ".join(str(item.get(c) or "") for c in
                       ("titulo", "evidencia", "texto_primario", "resumo_fonte", "consulta_origem")))

def identificar_programa(item: dict, cfg: dict | None = None) -> dict:
    cfg = cfg or _cfg()
    texto = _texto(item)
    for programa in cfg["programas"]:
        for termo in programa["termos"]:
            if _n(termo) in texto:
                return {
                    "programa_id": programa["id"], "programa": programa["nome"],
                    "lei": programa["lei"], "esfera": programa["esfera"],
                    "fluxo": programa.get("fluxo", "edital"),
                    "aciona_farol": programa.get("aciona_farol", True),
                    "alerta": programa.get("alerta"),
                    "nota": programa.get("nota"),
                    "reconhecido_por": termo,
                }
    return {
        "programa_id": None, "programa": "Programa não identificado",
        "lei": None, "esfera": None, "fluxo": "edital", "aciona_farol": True,
        "reconhecido_por": None,
        "lacuna": "nenhum termo de programa conhecido no texto capturado — conferir o edital",
    }

def identificar_modalidade(item: dict, programa: dict, cfg: dict | None = None) -> dict:
    """Modalidade = objeto ou atividade a ser executada, tal como escrito na fonte."""
    cfg = cfg or _cfg()
    texto = _texto(item)
    if programa.get("programa_id"):
        definicao = next((p for p in cfg["programas"] if p["id"] == programa["programa_id"]), {})
        for modalidade in definicao.get("modalidades_conhecidas", []):
            nucleo = _n(modalidade).split(" — ")[0].split(" - ")[0]
            if nucleo and nucleo in texto:
                return {"modalidade": modalidade, "origem": "catalogo_do_programa"}
    # objeto declarado literalmente no texto
    achado = re.search(r"objeto[:\s]+([^.;\n]{15,180})", item.get("evidencia") or "", re.I)
    if achado:
        return {"modalidade": achado.group(1).strip()[:180], "origem": "objeto_literal_da_fonte"}
    return {"modalidade": None, "origem": None,
            "lacuna": "objeto/modalidade não localizado no texto capturado — conferir o edital"}

def _data(bruto: str | None) -> str | None:
    if not bruto:
        return None
    bruto = bruto.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", bruto):
        return bruto
    partes = bruto.split("/")
    if len(partes) == 3:
        d, m, a = partes
        try:
            return f"{int(a):04d}-{int(m):02d}-{int(d):02d}"
        except ValueError:
            return None
    return None

def extrair_periodo(item: dict) -> dict:
    """Início e fim das inscrições, apenas quando escritos na fonte."""
    bruto = " ".join(str(item.get(c) or "") for c in ("titulo", "evidencia", "texto_primario"))
    inicio = fim = None
    faixa = PERIODO.search(bruto)
    if faixa:
        inicio, fim = _data(faixa.group(1)), _data(faixa.group(2))
    if not inicio:
        achado = INICIO.search(bruto)
        inicio = _data(achado.group(1)) if achado else None
    if not fim:
        achado = FIM.search(bruto)
        fim = _data(achado.group(1)) if achado else None
    if not fim:
        fim = _data(item.get("prazo_texto"))
    if not inicio:
        inicio = item.get("data_publicacao")
    return {
        "inicio": inicio, "fim": fim,
        "inicio_declarado": bool(inicio and inicio != item.get("data_publicacao")),
        "fim_declarado": bool(fim),
        "observacao": "datas conforme escritas na fonte; conferir no edital antes de qualquer decisão",
    }

def caracterizar(item: dict, cfg: dict | None = None) -> dict:
    cfg = cfg or _cfg()
    programa = identificar_programa(item, cfg)
    modalidade = identificar_modalidade(item, programa, cfg)
    periodo = extrair_periodo(item)
    return {**programa, **modalidade, "periodo": periodo, "caracterizado_em": now_iso()}

def run() -> dict:
    from .nucleo import carregar_oportunidades, gravar_oportunidades
    cfg = _cfg()
    registros = carregar_oportunidades()
    resumo = {"executado_em": now_iso(), "avaliados": 0, "identificados": 0, "por_programa": {}}
    for item in registros.values():
        dados = caracterizar(item, cfg)
        item["caracterizacao"] = dados
        item["aciona_farol_programa"] = dados.get("aciona_farol", True)
        resumo["avaliados"] += 1
        if dados.get("programa_id"):
            resumo["identificados"] += 1
            resumo["por_programa"][dados["programa"]] = resumo["por_programa"].get(dados["programa"], 0) + 1
    gravar_oportunidades(registros)
    return resumo

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
