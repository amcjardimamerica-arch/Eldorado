"""ADAPTADORES POR PLATAFORMA (conselho dos motores, Dr. Fábio Rangel — 10/10/2026).

Em vez de um leitor por órgão, um leitor por PLATAFORMA cobre todos os órgãos que a usam:
  plataforma-wordpress        API pública do WordPress (/wp-json/wp/v2/posts?search=…): busca "edital", "chamamento" e
                              "seleção" nos posts dos últimos 45 dias de cada site oficial WordPress conhecido
  plataforma-mapas-culturais  API padrão do Mapas Culturais (/api/opportunity/find): oportunidades com inscrição aberta,
                              com a data oficial de encerramento
Os sites vêm do que o sistema já conhece (oportunidades, certidões do Cartório, biblioteca de sites), redescobertos pelo
conselho a cada execução (estado/conselho/plataformas.json). Rodízio com cursor: N sites por leitura, todos ao longo do dia.
Os achados saem no formato dos demais motores e passam pelos mesmos filtros (destinação e pertinência).
"""
from __future__ import annotations

import json
import re
import time
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
PLATAFORMAS = ROOT / "estado/conselho/plataformas.json"
CURSOR = ROOT / "estado/conselho/cursor_plataformas.json"


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao


def _baixar(url: str):
    from .executor_skills import baixar
    return baixar(url)


def _limpa(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", str(s or ""))).replace("&#8211;", "–").replace("&#8220;", "“").replace("&#8221;", "”").strip()


def _rodizio(lista: list[str], chave: str, n: int) -> list[str]:
    if not lista:
        return []
    cur = _j(CURSOR, {}) or {}
    i = int(cur.get(chave) or 0) % len(lista)
    fatia = (lista[i:] + lista[:i])[:n]
    cur[chave] = (i + n) % len(lista)
    CURSOR.parent.mkdir(parents=True, exist_ok=True)
    CURSOR.write_text(json.dumps(cur), encoding="utf-8")
    return fatia


def _achado(sensor: dict, titulo: str, url: str, evidencia: str, prazo: str | None, orgao: str) -> dict | None:
    from .nucleo import novo_id, now_iso
    from hashlib import sha256
    try:
        from .destinacao import avaliar_destinacao
    except Exception:  # noqa: BLE001
        avaliar_destinacao = None
    try:
        from .pertinencia import pertinente
    except Exception:  # noqa: BLE001
        pertinente = None
    if avaliar_destinacao:
        dest = avaliar_destinacao({"titulo": titulo, "evidencia": evidencia, "fonte_id": sensor["id"]})
        if not dest.get("elegivel"):
            return None
    else:
        dest = {"elegivel": True}
    if pertinente and not pertinente({"titulo": titulo, "evidencia": evidencia}).get("ok"):
        return None
    return {"id": novo_id(url), "titulo": titulo[:300], "url": url, "fonte_id": sensor["id"], "fonte_nome": f"{sensor['nome']} — {orgao}"[:160],
            "territorio": "BR", "uf": None, "nivel": None, "tipo_fonte": f"sensor_{sensor.get('tipo', 'api')}", "confianca": "primaria",
            "coletado_em": now_iso(), "prazo_texto": prazo, "valor_texto": None, "evidencia": evidencia[:500],
            "hash_evidencia": sha256(evidencia.encode()).hexdigest(), "lexico": [], "forca_lexica": None, "destinacao": dest, "sensor": sensor["id"]}


def ler_wordpress(sensor: dict, hoje: date | None = None, limites: dict | None = None, baixar=None) -> dict:
    from .nucleo import now_iso
    baixar = baixar or _baixar; hoje = hoje or date.today()
    doms = _rodizio((_j(PLATAFORMAS, {}).get("WordPress") or []), "wordpress", int(sensor.get("max_paginas") or 20))
    desde = (hoje - timedelta(days=45)).isoformat() + "T00:00:00"
    achados, falhas, diag = {}, [], {"sites": len(doms), "respostas_json": 0, "posts": 0, "paginas_lidas": 0, "links_total": 0,
                                       "links_candidatos": 0, "motivo_zero": None}
    for d in doms:
        for termo in ("edital", "chamamento", "seleção"):
            u = f"https://{d}/wp-json/wp/v2/posts?search={quote(termo)}&after={desde}&per_page=10&_fields=link,title,date,excerpt"
            try:
                b, _t = baixar(u); diag["paginas_lidas"] += 1
                posts = json.loads(b)
                if not isinstance(posts, list):
                    raise ValueError("resposta não é lista")
                diag["respostas_json"] += 1
            except Exception as e:  # noqa: BLE001
                falhas.append({"url": u, "erro": type(e).__name__}); break        # site sem API aberta: não insiste nos outros termos
            for p in posts:
                diag["posts"] += 1; diag["links_total"] += 1
                tit = _limpa((p.get("title") or {}).get("rendered")); ev = _limpa((p.get("excerpt") or {}).get("rendered"))
                if not re.search(r"(?i)edital|chamamento|chamada|sele[çc][ãa]o|pr[êe]mio|inscri", tit + " " + ev):
                    continue
                diag["links_candidatos"] += 1
                a = _achado(sensor, tit, p.get("link") or "", f"{tit}. {ev}", None, d)
                if a and a["url"]:
                    achados[a["id"]] = a
            time.sleep(0.3)
    if not achados:
        diag["motivo_zero"] = "nenhum post de edital nos últimos 45 dias nos sites lidos" if diag["respostas_json"] else "nenhum site respondeu à API do WordPress"
    return {"sensor": sensor["id"], "achados": list(achados.values()), "falhas": falhas[:20], "saude": [], "diagnostico": diag, "lido_em": now_iso()}


def ler_mapas(sensor: dict, hoje: date | None = None, limites: dict | None = None, baixar=None) -> dict:
    from .nucleo import now_iso
    baixar = baixar or _baixar; hoje = hoje or date.today()
    hosts = _rodizio((_j(PLATAFORMAS, {}).get("Mapas Culturais") or []), "mapas", int(sensor.get("max_paginas") or 12))
    achados, falhas, diag = {}, [], {"instancias": len(hosts), "respostas_json": 0, "oportunidades": 0, "paginas_lidas": 0,
                                       "links_total": 0, "links_candidatos": 0, "motivo_zero": None}
    for h in hosts:
        u = (f"https://{h}/api/opportunity/find?@select=id,name,shortDescription,registrationFrom,registrationTo,singleUrl"
             f"&registrationTo=GTE({hoje.isoformat()})&@order=registrationTo%20ASC&@limit=30")
        try:
            b, _t = baixar(u); diag["paginas_lidas"] += 1
            ops = json.loads(b)
            if not isinstance(ops, list):
                raise ValueError("resposta não é lista")
            diag["respostas_json"] += 1
        except Exception as e:  # noqa: BLE001
            falhas.append({"url": u, "erro": type(e).__name__}); continue
        for o in ops:
            diag["oportunidades"] += 1; diag["links_total"] += 1
            tit = _limpa(o.get("name")); ev = _limpa(o.get("shortDescription"))
            fim = str(o.get("registrationTo") or "")[:10] if isinstance(o.get("registrationTo"), str) else \
                str((o.get("registrationTo") or {}).get("date") or "")[:10]
            url = o.get("singleUrl") or f"https://{h}/oportunidade/{o.get('id')}/"
            diag["links_candidatos"] += 1
            a = _achado(sensor, tit, url, f"{tit}. {ev}"[:600], fim or None, h)
            if a:
                achados[a["id"]] = a
        time.sleep(0.3)
    if not achados:
        diag["motivo_zero"] = "nenhuma oportunidade com inscrição aberta nas instâncias lidas" if diag["respostas_json"] else "nenhuma instância respondeu à API"
    return {"sensor": sensor["id"], "achados": list(achados.values()), "falhas": falhas[:20], "saude": [], "diagnostico": diag, "lido_em": now_iso()}
