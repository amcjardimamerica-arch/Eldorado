"""SKILLS DOS PILOTOS (titular, 29/09) — pacotes pequenos por tarefa, carregados só na missão que precisa.

Cada skill = skills/<piloto>/<nome>/SKILL.md (instrução curta, ≤500 tokens) + código em src/skills/ quando a tarefa é
mecânica (ler PDF, buscar expressões, consultar cadastro) + exemplos/regras aprendidas. No máximo 1–2 por pedido.
"""
from __future__ import annotations

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2] / "skills"
POR_MISSAO = {
    ("interceptador", "edital"): ["comum/leitura_pdf", "interceptador/cronograma"],
    ("interceptador", "site_oficial"): ["interceptador/site_oficial"],
    ("interceptador", "empresa"): ["interceptador/dossie_empresa"],
    ("espiao", "descobrir"): ["espiao/descobrir_entidades_novas", "espiao/triagem_indicio"],
    ("espiao", "aposta"): ["espiao/triagem_indicio"],
}


def instrucao(nome: str, limite: int = 2000) -> str:
    """A seção '## Instrução' do SKILL.md (curta; vai para o modelo)."""
    try:
        t = (RAIZ / nome / "SKILL.md").read_text(encoding="utf-8")
    except Exception:
        return ""
    m = re.search(r"## Instrução\s*\n([\s\S]*?)(?:\n## |\Z)", t)
    return (m.group(1).strip() if m else "")[:limite]


def para(piloto: str, missao: str) -> str:
    return "\n\n".join(f"[skill {n}]\n{instrucao(n)}" for n in POR_MISSAO.get((piloto, missao), []) if instrucao(n))


def catalogo() -> list[dict]:
    out = []
    for f in sorted(RAIZ.glob("*/*/SKILL.md")):
        t = f.read_text(encoding="utf-8")
        d = re.search(r"^description:\s*(.+)$", t, re.M)
        out.append({"skill": f"{f.parent.parent.name}/{f.parent.name}", "descricao": d.group(1).strip() if d else ""})
    return out
