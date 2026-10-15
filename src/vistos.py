"""RELEITURA PADRÃO PARA TODOS OS MOTORES (titular, 15/10/2026).

A mesma oportunidade relida num dia seguinte NÃO é oportunidade nova. O motor do PNCP marcava ~210 "oportunidades" por
dia — as mesmas compras abertas relidas todo dia — e o painel somava 2.873 em 13 dias e 10.254 no total, quando havia
242 compras distintas. Regra para TODOS os motores: cada oportunidade tem uma CHAVE; a primeira leitura é NOVA, as
seguintes são RELIDAS (só atualizam "visto em"). Os indicadores contam NOVAS (distintas) e mostram as relidas à parte.

Chave (a primeira que existir): compra do PNCP (CNPJ/ano/sequencial) · endereço normalizado (sem protocolo, www,
parâmetros de rastreio, âncora e barra final) · título + órgão normalizados.
Estado: estado/achados_vistos.json {motor: {chave: [primeira_vez, ultima_vez, vezes]}}.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from datetime import date
from pathlib import Path

from .nucleo import ROOT

ARQ = ROOT / "estado/achados_vistos.json"
PNCP = re.compile(r"pncp\.gov\.br/(?:app/editais|pncp-api/v1/orgaos|api/(?:pncp|consulta)/v1/orgaos)/(\d{14})/(?:compras/)?(\d{4})/(\d+)", re.I)
RASTREIO = re.compile(r"[?&](?:utm_[a-z]+|fbclid|gclid|ref|source)=[^&#]*", re.I)


def _sem(s) -> str:
    return re.sub(r"\s+", " ", "".join(c for c in unicodedata.normalize("NFD", str(s or "").lower()) if unicodedata.category(c) != "Mn")).strip()


def chave(a: dict) -> str:
    for u in (a.get("url"), a.get("link_oficial"), a.get("url_documento")):
        m = PNCP.search(str(u or ""))
        if m:
            return f"pncp:{m.group(1)}/{m.group(2)}/{int(m.group(3))}"
    u = str(a.get("url") or "")
    if u.startswith("http"):
        u = RASTREIO.sub("", u).split("#")[0]
        u = re.sub(r"^https?://(?:www\.)?", "", u.lower()).rstrip("/")
        return "url:" + u
    return "txt:" + hashlib.sha1(f"{_sem(a.get('titulo'))}|{_sem(a.get('orgao'))}".encode()).hexdigest()[:20]


def _carregar() -> dict:
    try:
        return json.loads(ARQ.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}


def registrar(motor: str, achados: list[dict], hoje: date | None = None, gravar: bool = True) -> dict:
    """Separa NOVAS de RELIDAS para um motor e devolve as contagens (e a lista das novas)."""
    d = _carregar(); m = d.setdefault(motor, {}); h = (hoje or date.today()).isoformat()
    novas, relidas, vistas = [], 0, set()
    for a in achados or []:
        k = chave(a)
        if k in vistas:
            continue                                   # repetida na MESMA leitura
        vistas.add(k)
        if k in m:
            m[k][1] = h; m[k][2] = int(m[k][2]) + 1; relidas += 1
        else:
            m[k] = [h, h, 1]; novas.append(a)
    if gravar:
        ARQ.parent.mkdir(parents=True, exist_ok=True)
        ARQ.write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {"novas": len(novas), "relidas": relidas, "lidas": len(vistas), "lista_novas": novas}


def distintas(motor: str, desde: str | None = None) -> int:
    m = _carregar().get(motor) or {}
    return sum(1 for v in m.values() if not desde or v[0] >= desde)


def semear(gravar: bool = True) -> dict:
    """1ª execução: o histórico de cada motor (bases de eventos, já distintas) vira o registro de vistos."""
    d = _carregar()
    for f in sorted((ROOT / "dados/financiadores").glob("*/eventos.compacto.json")):
        motor = f.parent.name
        try:
            ev = json.loads(f.read_text(encoding="utf-8")); sc = ev.get("schema") or []
            linhas = [dict(zip(sc, x)) for x in ev.get("linhas") or []]
        except Exception:  # noqa: BLE001
            continue
        m = d.setdefault(motor, {})
        for x in linhas:
            k = chave(x); dia = str(x.get("coletado_em") or "")[:10] or date.today().isoformat()
            if k not in m:
                m[k] = [dia, dia, 1]
    if gravar:
        ARQ.parent.mkdir(parents=True, exist_ok=True)
        ARQ.write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {k: len(v) for k, v in d.items()}


def corrigir_totais(sensores: dict) -> dict:
    """Totais acumulados por releitura viram distintos; a diferença vai para 'relidas_total' (uma vez só)."""
    feitos = {}
    for mid, reg in (sensores or {}).items():
        if not isinstance(reg, dict) or reg.get("totais_por_distintas"):
            continue
        n = distintas(mid)
        antigo = int(reg.get("achados_total") or 0)
        if n and antigo > n:
            reg["relidas_total"] = int(reg.get("relidas_total") or 0) + (antigo - n)
            reg["achados_total"] = n
            feitos[mid] = (antigo, n)
        reg["totais_por_distintas"] = True
    return feitos
