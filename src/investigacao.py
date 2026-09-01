"""Investigação — varredura profunda em sites segmentados do terceiro setor.

A varredura padrão lê a página inicial de cada fonte. A investigação vai
além: nos portais que concentram editais para OSCs (Prosas, Captamos, Mapa
das OSC, Observatório do Terceiro Setor, Rede Filantropia, ABCR, GIFE),
segue os links de edital encontrados até um nível de profundidade, para
capturar título, objeto, prazo e valor que só aparecem na página do edital.

Cada achado passa pelo filtro de destinação (fase 2) antes de entrar. O que
não é destinado ao terceiro setor é descartado com o motivo registrado.
Executa no GitHub Actions (aqui a rede não alcança esses domínios).
"""
from __future__ import annotations

import json
import re
import time
from datetime import date
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

from .destinacao import avaliar_destinacao
from .nucleo import (ROOT, append_jsonl, canonical_url, load_json, now_iso,
                     sha256, validate_public_https, write_json)

CFG = ROOT / "config/investigacao.json"
ESTADO = ROOT / "estado/investigacao"

_EDITAL = re.compile(r"edital|chamada|chamamento|sele[çc][ãa]o|pr[êe]mio|inscri[çc]|fomento|"
                     r"apoio\s+a\s+projetos|oportunidade", re.I)
_FIM = re.compile(r"(?:at[ée]|prazo|encerra\w*|inscri[çc][õo]es[^.]{0,30}?at[ée])\D{0,25}"
                  r"(\d{1,2}/\d{1,2}/20\d{2})", re.I)
_VALOR = re.compile(r"R\$\s?[\d.]{1,12},\d{2}|R\$\s?[\d.]{3,12}", re.I)


class _Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []; self.texto = []; self._h = None; self._t = []
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._h = dict(attrs).get("href"); self._t = []
    def handle_data(self, data):
        self.texto.append(data)
        if self._h is not None:
            self._t.append(data)
    def handle_endtag(self, tag):
        if tag == "a" and self._h is not None:
            self.links.append((self._h, " ".join(self._t).strip())); self._h = None


def _abrir(url: str, timeout: int = 25, max_bytes: int = 3_000_000) -> tuple[str, str]:
    from urllib.request import Request, urlopen
    if not url.startswith("file://"):
        validate_public_https(url, urlsplit(url).hostname)
    req = Request(url, headers={"User-Agent": "Eldorado-OSC/1.0 investigacao"})
    with urlopen(req, timeout=timeout) as r:
        return r.read(max_bytes).decode("utf-8", "replace"), r.geturl()


def investigar_fonte(fonte: dict, profundidade: int = 1, limite_links: int = 40,
                     pausa: float = 1.0) -> tuple[list[dict], list[dict]]:
    achados, falhas = [], []
    try:
        html, final = _abrir(fonte["url"])
    except Exception as exc:
        return [], [{"fonte": fonte["id"], "erro": type(exc).__name__}]
    p = _Links(); p.feed(html)
    candidatos = [(urljoin(final, h), t) for h, t in p.links
                  if t and len(t) >= 8 and _EDITAL.search(t)][:limite_links]
    for url, rotulo in candidatos:
        url = canonical_url(url)
        if urlsplit(url).scheme not in ("https", "file"):
            continue
        texto_pag, objeto = "", None
        if profundidade >= 1:
            try:
                time.sleep(pausa)
                pag, _ = _abrir(url)
                q = _Links(); q.feed(pag)
                texto_pag = re.sub(r"\s+", " ", " ".join(q.texto))[:6000]
                m = re.search(r"objeto[^.]{0,220}\.", texto_pag, re.I)
                objeto = m.group(0)[:240] if m else None
            except Exception as exc:
                falhas.append({"url": url, "erro": type(exc).__name__})
        evid = (rotulo + " " + texto_pag[:800]).strip()
        dest = avaliar_destinacao({"titulo": rotulo, "evidencia": evid,
                                   "fonte_id": fonte["id"]})
        if not dest["elegivel"]:
            continue
        fim = _FIM.search(texto_pag or rotulo)
        val = _VALOR.search(texto_pag or "")
        achados.append({
            "id": sha256(("inv|" + url).encode())[:20], "status": "capturada",
            "titulo": rotulo[:300], "url": url,
            "fonte_id": fonte["id"], "fonte_nome": fonte["nome"],
            "territorio": fonte.get("territorio", "BR"),
            "tipo_fonte": "investigacao_terceiro_setor", "confianca": "secundaria",
            "coletado_em": now_iso(), "prazo_texto": fim.group(1) if fim else None,
            "valor_texto": val.group(0) if val else None, "objeto": objeto,
            "evidencia": evid[:500], "hash_evidencia": sha256(evid.encode()),
            "destinacao": dest, "profundidade": profundidade,
        })
    return achados, falhas


def run(limite_fontes: int | None = None) -> dict:
    cfg = load_json(CFG) if CFG.exists() else {"fontes": []}
    ESTADO.mkdir(parents=True, exist_ok=True)
    total, falhas_t, novos = [], [], 0
    from .nucleo import carregar_oportunidades, DB_OPORTUNIDADES
    existentes = carregar_oportunidades()
    for fonte in (cfg.get("fontes") or [])[:limite_fontes]:
        if not fonte.get("ativa", True):
            continue
        ach, fal = investigar_fonte(fonte, cfg.get("profundidade", 1),
                                    cfg.get("limite_links_por_fonte", 40))
        falhas_t += fal
        for a in ach:
            if a["id"] not in existentes:
                append_jsonl(DB_OPORTUNIDADES, a); novos += 1
            total.append({"fonte": fonte["id"], "titulo": a["titulo"][:80],
                          "prazo": a["prazo_texto"], "valor": a["valor_texto"]})
    resumo = {"executado_em": now_iso(), "fontes": len(cfg.get("fontes") or []),
              "achados": len(total), "novos_na_base": novos,
              "falhas": falhas_t[:20], "amostra": total[:20],
              "nota": ("investigação profunda em sites segmentados do terceiro setor; "
                       "cada achado passou pelo filtro de destinação")}
    write_json(ESTADO / "resumo.json", resumo)
    return resumo


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2)[:1500])
