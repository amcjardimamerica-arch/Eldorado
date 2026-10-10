"""MOTORES LIGADOS E DESLIGADOS À MÃO, PELO FOGO (titular, 10/10/2026).

Apertar o FOGO ao lado esquerdo de um motor no painel o DESLIGA (vira a fogueira apagada); apertar de novo o LIGA.
  · desligado: nenhum acionamento automático o executa — agenda, maestro, rede neural, fluxos dos Pilotos e das
    empresas. Fica parado até o titular apertar o fogo de novo. (A busca imediata pelo fósforo continua possível:
    é uma ordem sua, não um acionamento automático.)
  · ligado (com fogo): volta a integrar o workflow e a rede neural pode acioná-lo normalmente.
O painel grava a decisão pelo fluxo "motor-manual" (GitHub Actions); a fonte de verdade é config/motores_manuais.json
e o painel lê a cópia em docs/dados/motores_manuais.json.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/motores_manuais.json"
PUBLICO = ROOT / "docs/dados/motores_manuais.json"


def _agora() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def carregar() -> dict:
    try:
        d = json.loads(CONFIG.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        d = {}
    d.setdefault("regra", (__doc__ or "").split("\n\n")[0].strip())
    d.setdefault("motores", {})
    return d


def _chaves(mid: str) -> list[str]:
    m = str(mid or "")
    return [m, m[5:] if m.startswith("plat-") else "plat-" + m]


def desligados() -> set[str]:
    out = set()
    for k, v in (carregar().get("motores") or {}).items():
        if (v or {}).get("estado") == "desligado":
            out |= set(_chaves(k))
    return out


def desligado(mid: str) -> bool:
    return any(k in desligados() for k in _chaves(mid))


def info(mid: str) -> dict | None:
    m = carregar().get("motores") or {}
    for k in _chaves(mid):
        if (m.get(k) or {}).get("estado") == "desligado":
            return m[k]
    return None


def definir(mid: str, estado: str, motivo: str = "", por: str = "titular (fogo no painel)") -> dict:
    if estado not in ("ligado", "desligado"):
        raise ValueError("estado deve ser 'ligado' ou 'desligado'")
    d = carregar()
    hist = d.setdefault("historico", [])
    hist.append({"motor": mid, "estado": estado, "em": _agora(), "por": por, "motivo": motivo})
    d["historico"] = hist[-300:]
    if estado == "desligado":
        d["motores"][mid] = {"estado": "desligado", "desde": _agora(), "por": por, "motivo": motivo}
    else:
        for k in _chaves(mid):
            d["motores"].pop(k, None)
    d["em"] = _agora()
    _pausa_dos_pilotos(mid, estado)
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    publicar(d)
    return d


PAUSA_PILOTOS = {"piloto-aberto": ROOT / "estado/piloto_pausado", "piloto-espiao": ROOT / "estado/piloto_pausado",
                 "piloto-interceptador": ROOT / "estado/interceptador/pausado"}


def _pausa_dos_pilotos(mid: str, estado: str) -> None:
    """Os Pilotos já têm 'em terra por ordem do titular' (arquivo de pausa respeitado pelos fluxos e pela cadeia de voos)."""
    p = PAUSA_PILOTOS.get(mid)
    if not p:
        return
    if estado == "desligado":
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"desligado no fogo do painel em {_agora()}\n", encoding="utf-8")
    elif p.exists():
        p.unlink()


def publicar(d: dict | None = None) -> None:
    d = d or carregar()
    PUBLICO.parent.mkdir(parents=True, exist_ok=True)
    PUBLICO.write_text(json.dumps({"em": d.get("em"), "regra": d.get("regra"), "desligados": d.get("motores") or {},
                                   "historico": (d.get("historico") or [])[-30:]}, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["definir"] and len(a) >= 3:
        r = definir(a[1], a[2], " ".join(a[3:]))
        print(json.dumps({"motor": a[1], "estado": a[2], "desligados": sorted(r["motores"])}, ensure_ascii=False))
    elif a[:1] == ["ativo"] and len(a) >= 2:        # código de saída 0 = ligado; 1 = desligado (para os fluxos)
        sys.exit(1 if desligado(a[1]) else 0)
    else:
        print("uso: python -m src.motores_manuais definir <motor> ligado|desligado [motivo] | ativo <motor>")
