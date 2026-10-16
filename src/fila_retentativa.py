"""FILA DE RETENTATIVA (titular, 15/10/2026) — timeout ou erro de acesso numa página não para a pesquisa.

Regra:
  · a página que dá erro (tempo esgotado, 403/429/5xx, conexão derrubada, DNS…) SAI da passagem e a fila de pesquisa
    segue com as próximas;
  · ela volta 30 minutos depois (ESPERA_MIN) — antes disso, as passagens a pulam com o motivo "aguardando retentativa";
  · após 5 tentativas (LIMITE) com o MESMO erro seguidas, sai da fila de vez e aparece no mostrador da sala de controle
    como falha ("fora da fila"); erro diferente recomeça a contagem; sucesso a tira da fila.
Serve às páginas dos motores (chave = URL; escopo = motor) e aos documentos das oportunidades (escopo = "cartorio").
Estado: estado/fila_retentativa.json
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARQ = ROOT / "estado/fila_retentativa.json"
ESPERA_MIN = 30
LIMITE = 5
_CACHE: dict | None = None


def _agora() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _carregar() -> dict:
    global _CACHE
    if _CACHE is None:
        try:
            _CACHE = json.loads(ARQ.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            _CACHE = {}
        _CACHE.setdefault("fila", {}); _CACHE.setdefault("fora_da_fila", {})
    return _CACHE


def gravar() -> None:
    d = _carregar()
    d["em"] = _agora().isoformat()
    d["resumo"] = resumo()
    ARQ.parent.mkdir(parents=True, exist_ok=True)
    ARQ.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def tipo_erro(exc: BaseException | None = None, code=None, texto: str | None = None) -> str:
    """Rótulo estável do erro: o mesmo erro, o mesmo rótulo (é o que conta para as 5 tentativas)."""
    if code:
        return f"HTTP {code}"
    nome = type(exc).__name__ if exc is not None else str(texto or "erro")
    if "imeout" in nome or "timed out" in str(exc or texto or ""):
        return "tempo esgotado"
    return nome[:60]


def fora_da_fila(url: str) -> bool:
    return url in _carregar()["fora_da_fila"]


def aguardando(url: str, agora: datetime | None = None) -> bool:
    """Errou há menos de 30 minutos: a passagem pula e segue a fila."""
    r = _carregar()["fila"].get(url)
    return bool(r) and (agora or _agora()) < datetime.fromisoformat(r["proxima_em"])


def devidas(escopo: str, agora: datetime | None = None) -> list[str]:
    """Páginas do escopo cujo prazo de 30 minutos já venceu — entram no começo da fila desta passagem."""
    a = agora or _agora()
    return [u for u, r in _carregar()["fila"].items() if r.get("escopo") == escopo and a >= datetime.fromisoformat(r["proxima_em"])]


def falhou(url: str, escopo: str, erro: str, causa: str | None = None, agora: datetime | None = None) -> dict:
    d = _carregar(); a = agora or _agora()
    r = d["fila"].get(url) or {"escopo": escopo, "primeiro_erro": a.isoformat(), "tentativas": 0, "erro": None, "historico": []}
    r["tentativas"] = r["tentativas"] + 1 if r.get("erro") == erro else 1          # erro diferente recomeça a contagem
    r.update({"escopo": escopo, "erro": erro, "causa": causa, "ultimo_erro": a.isoformat(),
              "proxima_em": (a + timedelta(minutes=ESPERA_MIN)).isoformat()})
    r["historico"] = (r["historico"] + [{"em": a.isoformat(), "erro": erro}])[-10:]
    if r["tentativas"] >= LIMITE:
        d["fila"].pop(url, None)
        d["fora_da_fila"][url] = {**r, "saiu_em": a.isoformat(), "motivo": f"{LIMITE} tentativas com o mesmo erro ({erro})"}
        return {"estado": "fora_da_fila", **d["fora_da_fila"][url]}
    d["fila"][url] = r
    return {"estado": "aguardando", **r}


def sucesso(url: str) -> None:
    _carregar()["fila"].pop(url, None)


def reabrir(url: str) -> bool:
    """Devolve à fila uma página que saiu (uso manual, depois de corrigida a causa)."""
    return _carregar()["fora_da_fila"].pop(url, None) is not None


def resumo() -> dict:
    d = _carregar()
    por_escopo: dict = {}
    for u, r in d["fora_da_fila"].items():
        por_escopo[r.get("escopo") or "—"] = por_escopo.get(r.get("escopo") or "—", 0) + 1
    return {"aguardando_retentativa": len(d["fila"]), "fora_da_fila": len(d["fora_da_fila"]), "fora_da_fila_por_escopo": por_escopo,
            "regra": f"volta em {ESPERA_MIN} min; sai após {LIMITE} tentativas com o mesmo erro"}


def reabrir_corrigidos(exige_brasil: set | None = None) -> list[str]:
    """16/10/2026 (sala de controle): devolve à fila as páginas cuja CAUSA foi corrigida — endereço http:// (agora vira
    https://) e site que passou a ser lido pela ponte Brasil."""
    from urllib.parse import urlsplit
    d = _carregar(); voltam = []
    for u, r in list(d["fora_da_fila"].items()):
        host = urlsplit(u).hostname or ""
        if (u.startswith("http://") and "ValueError" in str(r.get("erro"))) or (exige_brasil and host in exige_brasil):
            d["fora_da_fila"].pop(u); voltam.append(u)
    return voltam
