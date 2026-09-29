"""SKILL · LEITURA DE PDF E EXPRESSÕES EM CONTEXTO (titular, 29/09) — a identificação mais importante.

Abre o PDF (texto de cada página + TABELAS, que o texto corrido perde: é nelas que ficam cronograma, valores e
prazos), busca EXPRESSÕES (regex) e devolve cada ocorrência com o CONTEXTO em volta e a página. Os trechos-chave
vão na frente do texto que o modelo lê — ele decide sobre o que importa, em vez de garimpar 60 páginas.
Usa pdfplumber (tabelas); sem ele, pypdf (só texto).
"""
from __future__ import annotations

import io
import re

# expressões por condição do checklist — a skill de aprendizado acrescenta termos às condições que mais falham
EXPRESSOES = {
    "Prazo de inscrição": [r"inscri[cç][õo]es?\s+(?:ser[aã]o\s+)?(?:realizadas|abertas|recebidas)?[^.]{0,60}?(?:at[eé]|de\s+\d)", r"per[ií]odo\s+de\s+inscri", r"prazo\s+(?:final\s+)?(?:para|de)\s+(?:inscri|envio|submiss)", r"data\s+limite", r"encerramento\s+das\s+inscri"],
    "Resultado": [r"resultado\s+(?:preliminar|final|provis[oó]rio|definitivo)", r"divulga[cç][aã]o\s+do\s+resultado", r"homologa[cç][aã]o\s+do\s+resultado", r"publica[cç][aã]o\s+do\s+resultado"],
    "Prazo de recurso": [r"recurso[s]?\b[^.]{0,80}?(?:\d+\s*\(?\w*\)?\s*dias|at[eé]|prazo)", r"interposi[cç][aã]o\s+de\s+recurso", r"prazo\s+recursal"],
    "Cronograma": [r"cronograma", r"\betapa[s]?\b[^.]{0,40}?\bdata", r"calend[aá]rio"],
    "Valor": [r"R\$\s?\d[\d.]*(?:,\d{2})?", r"valor\s+(?:total|global|m[aá]ximo|de\s+at[eé]|por\s+projeto)", r"dota[cç][aã]o\s+or[cç]ament[aá]ria", r"recursos\s+financeiros"],
    "Requisitos": [r"requisitos?\s+(?:para|de)\s+(?:participa|habilita)", r"poder[aã]o\s+participar", r"habilita[cç][aã]o", r"documenta[cç][aã]o\s+(?:necess[aá]ria|exigida)", r"vedad[ao]s?\s+(?:a\s+)?participa"],
    "Objeto": [r"\bdo\s+objeto\b", r"o\s+presente\s+edital\s+(?:tem\s+(?:por|como)\s+(?:objeto|finalidade)|visa)", r"objeto\s+(?:deste|do\s+presente)"],
    "Destinação": [r"destinad[ao]s?\s+a", r"p[uú]blico[- ]alvo", r"benefici[aá]rios"],
    "Anexos": [r"\banexo\s+[IVX\d]+", r"formul[aá]rio\s+de\s+inscri", r"modelo\s+de\s+(?:plano|proposta)"],
}
DATA = re.compile(r"\b(\d{1,2})[/.](\d{1,2})[/.](\d{2,4})\b|\b(\d{1,2})\s+de\s+(janeiro|fevereiro|mar[cç]o|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)(?:\s+de\s+(\d{4}))?", re.I)


def ler_pdf(dados: bytes, max_paginas: int = 80) -> dict:
    """{'paginas': [texto por página], 'tabelas': [(pagina, [[células]])], 'motor': 'pdfplumber'|'pypdf'}"""
    try:
        import pdfplumber
        pags, tabs = [], []
        with pdfplumber.open(io.BytesIO(dados)) as pdf:
            for i, p in enumerate(pdf.pages[:max_paginas], 1):
                pags.append(p.extract_text() or "")
                try:
                    for t in p.extract_tables() or []:
                        linhas = [[(c or "").replace("\n", " ").strip() for c in ln] for ln in t if ln and any(ln)]
                        if len(linhas) >= 2:
                            tabs.append((i, linhas))
                except Exception:
                    pass
        return {"paginas": pags, "tabelas": tabs, "motor": "pdfplumber"}
    except Exception:
        pass
    try:
        from pypdf import PdfReader
        rd = PdfReader(io.BytesIO(dados))
        return {"paginas": [(p.extract_text() or "") for p in rd.pages[:max_paginas]], "tabelas": [], "motor": "pypdf"}
    except Exception:
        return {"paginas": [], "tabelas": [], "motor": "nenhum"}


def texto_com_tabelas(doc: dict) -> str:
    """Texto corrido + as tabelas escritas linha a linha ('Etapa | Data'), para que o cronograma não se perca."""
    partes = list(doc.get("paginas") or [])
    for pag, linhas in doc.get("tabelas") or []:
        partes.append(f"\n[TABELA da página {pag}]\n" + "\n".join(" | ".join(c for c in ln if c) for ln in linhas))
    return "\n".join(partes)


def buscar(texto: str, expressoes: dict | list | None = None, janela: int = 220, maximo_por_expr: int = 3) -> list[dict]:
    """Cada ocorrência: {'condicao', 'expressao', 'trecho' (com contexto), 'posicao', 'datas' encontradas no trecho}."""
    if isinstance(expressoes, list):
        expressoes = {"busca": expressoes}
    expressoes = expressoes or EXPRESSOES
    t = re.sub(r"[ \t]+", " ", texto or "")
    out, vistos = [], set()
    for cond, lista in expressoes.items():
        for rx in lista:
            n = 0
            for m in re.finditer(rx, t, re.I):
                a, b = max(0, m.start() - janela // 3), min(len(t), m.end() + janela)
                chave = (cond, a // 150)
                if chave in vistos:
                    continue
                vistos.add(chave)
                trecho = re.sub(r"\s+", " ", t[a:b]).strip()
                out.append({"condicao": cond, "expressao": rx, "trecho": trecho, "posicao": m.start(),
                            "datas": [d.group(0) for d in DATA.finditer(trecho)][:6]})
                n += 1
                if n >= maximo_por_expr:
                    break
    return out


def trechos_chave(texto: str, condicoes: list[str] | None = None, limite: int = 3200) -> str:
    """Bloco de TRECHOS-CHAVE para pôr na frente do texto do edital (condições com datas primeiro)."""
    exp = {k: v for k, v in EXPRESSOES.items() if not condicoes or k in condicoes or k == "Cronograma"}
    try:
        from .aprendizado import parametros
        extra = (parametros().get("interceptador") or {}).get("expressoes_extras") or {}
        for k, v in extra.items():
            exp.setdefault(k, []); exp[k] = exp[k] + [x for x in v if x not in exp[k]]
    except Exception:
        pass
    achados = buscar(texto, exp)
    achados.sort(key=lambda x: (not x["datas"], x["condicao"] not in ("Prazo de inscrição", "Cronograma", "Resultado", "Prazo de recurso"), x["posicao"]))
    bloco, total = [], 0
    for a in achados:
        linha = f"• [{a['condicao']}] …{a['trecho']}…"
        if total + len(linha) > limite:
            break
        bloco.append(linha); total += len(linha)
    return ("TRECHOS-CHAVE (skill leitura de PDF — expressões e contexto):\n" + "\n".join(bloco) + "\n\n") if bloco else ""
