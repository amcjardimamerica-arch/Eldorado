"""PONTE HOSTGATOR PARA OS MOTORES 04, 07 E 13 (titular, 03/10/2026).

Os portais da Câmara de Goiânia (SUAP e portal), do TJGO (notícias, PDFs dos editais, Banco de Projetos) e das
prefeituras de Goiás (*.go.gov.br) recusam o IP estrangeiro do GitHub. A hospedagem do titular na Hostgator tem IP
brasileiro: `ponte/ponte.php` recebe o pedido ASSINADO do GitHub, lê a página pública e devolve. O motor continua igual.

Quando passa pela ponte: só no GitHub (sem ELDORADO_LOCAL_BR), só com os segredos ELDORADO_PONTE_URL e
ELDORADO_PONTE_CHAVE gravados, e só para os domínios que recusam a nuvem (config/sensores.json › exige_brasil e os
sites *.go.gov.br, *.tjgo.jus.br, *.goiania.go.leg.br). No computador do titular a leitura é direta.

    abrir(url) -> (status, url_final, corpo_bytes, cabecalhos)        levanta ErroPonte se a ponte falhar
"""
from __future__ import annotations

import gzip
import json
import os
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUFIXOS = (".go.gov.br", ".tjgo.jus.br", "tjgo.jus.br", ".goiania.go.leg.br", "goiania.go.leg.br", "camaragyn.go.gov.br")
USO = {"pedidos": 0, "ok": 0, "falhas": 0}


def _exige() -> set[str]:
    try:
        d = json.loads((ROOT / "config/sensores.json").read_text(encoding="utf-8"))
        return set((d.get("exige_brasil") or {}).get("dominios") or [])
    except Exception:  # noqa: BLE001
        return set()


def na_nuvem() -> bool:
    return bool(os.environ.get("GITHUB_ACTIONS")) and not os.environ.get("ELDORADO_LOCAL_BR")


def configurada() -> bool:
    from .indexadores import ponte
    return ponte._http_configurada() if hasattr(ponte, "_http_configurada") else ponte.configurada()


def precisa(url: str) -> bool:
    h = (urllib.parse.urlsplit(url).hostname or "").lower()
    return h in _exige() or h.endswith(SUFIXOS)


def usar(url: str) -> bool:
    """Passa pela ponte? Só no GitHub, com a ponte configurada, num domínio que recusa a nuvem."""
    return na_nuvem() and configurada() and precisa(url)


def disponivel() -> bool:
    """O motor pode ler os portais do Brasil nesta execução (direto no Brasil ou pela ponte)."""
    return not na_nuvem() or configurada()


def abrir(url: str, aceitar: str = "text/html,application/xhtml+xml,application/json,*/*;q=0.5", timeout: int = 40,
          max_bytes: int = 6_000_000) -> tuple[int, str, bytes, dict]:
    from .indexadores import ponte
    USO["pedidos"] += 1
    try:
        st, final, corpo, hdr = ponte.buscar(url, {"Accept": aceitar, "Accept-Language": "pt-BR,pt;q=0.9"}, timeout, max_bytes)
    except Exception:
        USO["falhas"] += 1
        raise
    if (hdr.get("content-encoding") or "") == "gzip" or corpo[:2] == b"\x1f\x8b":
        try:
            corpo = gzip.decompress(corpo)
        except OSError:
            pass
    USO["ok"] += 1
    return st, final, corpo, hdr


def texto(url: str, timeout: int = 40, max_bytes: int = 6_000_000) -> str:
    st, _f, corpo, hdr = abrir(url, timeout=timeout, max_bytes=max_bytes)
    if st >= 400:
        raise RuntimeError(f"HTTP {st} pela ponte")
    cs = "utf-8"
    ct = hdr.get("content-type") or ""
    if "charset=" in ct:
        cs = ct.split("charset=")[-1].split(";")[0].strip() or "utf-8"
    return corpo.decode(cs, "replace")
