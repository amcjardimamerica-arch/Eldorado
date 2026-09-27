"""ENTIDADES EMPRESARIAIS — meta prioritária dos dois Pilotos (titular, 27/09).

Associações comerciais, federações, confederações, sindicatos patronais, câmaras, CDLs, grupos de institutos:
quem agremia empresas é o atalho para muitas empresas de uma vez. Prioridade para as NACIONAIS e as de GOIÁS.
Entidade de outro estado sem vínculo nacional nem com Goiás é DESCARTADA.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config/entidades_prioritarias.json"


def cfg() -> dict:
    try:
        return json.loads(CFG.read_text(encoding="utf-8"))
    except Exception:
        return {}


def e_entidade(texto: str) -> bool:
    t = str(texto or "").lower()
    return any(k in t for k in cfg().get("termos_de_entidade", [])) or bool(re.search(r"\b(acieg|fecom[eé]rcio|fieg|faeg|facieg|gife|cni|cnc|cna|cacb|cndl|ocb|adial|sinduscon|sebrae|amcham|febraban)\b", t))


def abrangencia(nome: str, url: str = "", texto: str = "") -> str:
    """nacional | goias | outro_estado | indefinida — pelo nome, pelo endereço e pelo começo do texto do site."""
    c = cfg(); t = f" {nome} {url} {str(texto)[:2500]} ".lower()
    semente = {x["url"].split("//")[-1].split("/")[0].replace("www.", ""): k for k in ("nacionais", "goias") for x in c.get(k, [])}
    host = str(url).split("//")[-1].split("/")[0].replace("www.", "").lower()
    if host in semente:
        return "nacional" if semente[host] == "nacionais" else "goias"
    if any(s in t for s in c.get("sinais_goias", [])):
        return "goias"
    if any(s in t for s in c.get("sinais_nacionais", [])):
        return "nacional"
    if any(s in t for s in c.get("outros_estados", [])):
        return "outro_estado"
    return "indefinida"


def descartar(nome: str, url: str = "", texto: str = "") -> str | None:
    """Motivo do descarte, ou None. Só descarta ENTIDADE de outro estado sem vínculo nacional nem com Goiás."""
    if not e_entidade(f"{nome} {texto[:600] if texto else ''}"):
        return None
    ab = abrangencia(nome, url, texto)
    return "entidade de outro estado, sem vínculo nacional nem com Goiás" if ab == "outro_estado" else None


def prioridade(nome: str, url: str = "", texto: str = "") -> int:
    """0 = entidade de Goiás · 1 = entidade nacional · 2 = demais · 9 = descartar."""
    if descartar(nome, url, texto):
        return 9
    if e_entidade(f"{nome} {url}"):
        ab = abrangencia(nome, url, texto)
        return 0 if ab == "goias" else 1 if ab == "nacional" else 2
    return 2


def sementes() -> list[dict]:
    c = cfg()
    return [{"url": x["url"], "nome": x["nome"], "tipo": "entidade-" + ("goias" if k == "goias" else "nacional"), "prioridade": 0 if k == "goias" else 1}
            for k in ("goias", "nacionais") for x in c.get(k, [])]
