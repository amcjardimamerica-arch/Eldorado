"""CRITÉRIO ÚNICO DA ESTRELA E DO LIVRO (titular, 04/10/2026).

bronze = Objeto + Prazo de inscrição + Território identificados · prata = bronze + Valor + Requisitos ·
ouro = os 12 itens, cada um VALIDADO (com valor) ou DISPENSADO com justificativa de que não se aplica.
"Não informado no edital", "não localizado" ou vazio NÃO é dispensa: é falta.
A ESTRELA usa o edital ATUAL (só oportunidade aberta); o LIVRO usa o HISTÓRICO conhecido (análise preditiva).
"""
from __future__ import annotations

import re

DOZE = ["Objeto", "Prazo de inscrição", "Resultado", "Prazo de recurso", "Valor", "Órgão / financiador",
        "Território", "Esfera", "Requisitos", "Anexos", "Destinação", "Área de atuação"]
BRONZE = ("Objeto", "Prazo de inscrição", "Território")
PRATA = BRONZE + ("Valor", "Requisitos")
FALTA = re.compile(r"^\s*(n[ãa]o (informad|localizad|encontrad|consta)|sem informa|pendente|—|-|\?)", re.I)
JUSTIFICA = re.compile(r"dispensad[oa] pel[oa]|n[ãa]o se aplica|n[ãa]o aplic[aá]vel|inaplic[aá]vel|n[ãa]o h[aá] (prazo de )?recurso|sem sele[çc][ãa]o competitiva|fluxo cont[ií]nuo|cadastro permanente|regime", re.I)


def resolvido(item: dict | None) -> bool:
    """Item validado (valor real) ou dispensado COM justificativa de não aplicabilidade."""
    if not isinstance(item, dict):
        return False
    v = str(item.get("v") or item.get("valor") or "").strip()
    st = item.get("s") or item.get("status")
    just = " ".join(str(item.get(k) or "") for k in ("v", "valor", "j", "motivo", "porque", "fundamento"))
    if st in ("disp", "dispensado") or v.lower().startswith("dispensad"):
        return bool(JUSTIFICA.search(just)) and len(just.strip()) >= 20
    return len(v) >= 3 and not FALTA.search(v)


def nivel(itens: dict) -> str | None:
    """bronze · prata · ouro pelo conjunto de itens (dicionário item → {s, v, ...})."""
    ok = {k for k in DOZE if resolvido((itens or {}).get(k))}
    if all(k in ok for k in DOZE):
        return "ouro"
    if all(k in ok for k in PRATA):
        return "prata"
    if all(k in ok for k in BRONZE):
        return "bronze"
    return None


def faltando(itens: dict) -> list[str]:
    return [k for k in DOZE if not resolvido((itens or {}).get(k))]


ORDEM = {None: 0, "bronze": 1, "prata": 2, "ouro": 3}


def auditar_estrelas(itens: list[dict]) -> list[dict]:
    """REGRA PERMANENTE (04/10): nenhuma estrela acima do que os 12 itens permitem. Recalcula e REBAIXA; devolve os casos."""
    casos = []
    for it in itens:
        devido = nivel(it.get("checklist") or {}) if it.get("selo") else None
        if ORDEM.get(it.get("selo"), 0) > ORDEM.get(devido, 0):
            casos.append({"id": it.get("id"), "tinha": it.get("selo"), "ficou": devido, "faltando": faltando(it.get("checklist") or {})})
            it["selo"] = devido; it["selo_rebaixado_pela_auditoria"] = True
    return casos


def dispensa_valida(motivo: str) -> bool:
    """Dispensa só com a justificativa de que o item NÃO SE APLICA ("não informado" é falta)."""
    return bool(JUSTIFICA.search(str(motivo or ""))) and len(str(motivo or "").strip()) >= 20
