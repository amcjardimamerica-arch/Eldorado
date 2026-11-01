"""Os extratores determinísticos do Interceptador (titular, 01/11/2026: a melhoria 1 do diagnóstico).

70% do material que o Interceptador encontrava nunca era lido pela IA (o modelo local roda no processador: ~117 s por
leitura, uma de cada vez). Muitos itens do checklist têm forma fixa e não precisam de IA: as datas da inscrição, o valor em
reais, os anexos citados, o órgão do livro, a cidade, a esfera. Estes extratores leem o texto antes da IA e devolvem, para
cada item que acham, o valor e o TRECHO copiado literalmente do documento (o mesmo formato da IA: o Cartório certifica pelo
trecho). A IA fica só com o que exige leitura de verdade.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any

DATA = r"\d{1,2}\s*(?:/|\.|-|de\s+[a-zç]+\s+de)\s*(?:\d{1,2}\s*(?:/|\.|-)\s*)?\d{2,4}"
INTERVALO = re.compile(rf"({DATA})\s*(?:a|até|ate|à|ao|e|-|–)\s*({DATA})", re.I)
DATA_SOLTA = re.compile(rf"(?:até|ate)\s+(?:o\s+dia\s+)?({DATA})", re.I)
REAIS = re.compile(r"R\$\s*\d{1,3}(?:\.\d{3})*(?:,\d{2})?(?:\s*(?:mil|milh[õo]es|milh[ãa]o))?", re.I)
ANEXO = re.compile(r"\bANEXO\s+(?:[IVXL]{1,6}|\d{1,2})\b(?:\s*[-–—:]\s*[^\n]{3,80})?", re.I)
OBJETO = re.compile(r"(?:do\s+objeto|objeto)\s*[:.\-–]?\s*(?:\d+(?:\.\d+)*\s*)?(?:o\s+presente\s+edital\s+tem\s+(?:como\s+objeto|por\s+objetivo)\s+)?"
                    r"([A-ZÀ-Úa-zà-ú][^\n]{40,320}?[.;])", re.I)
FINALIDADE = re.compile(r"(?:tem\s+(?:por|como)\s+(?:finalidade|objetivo|objeto))\s+([^\n]{40,320}?[.;])", re.I)
REQUISITOS = re.compile(r"((?:poder[ãa]o|podem|est[ãa]o\s+aptas?\s+a)\s+(?:participar|se\s+inscrever|concorrer)[^\n]{20,320}?[.;])", re.I)
ESFERAS = (("municipal", re.compile(r"prefeitura\s+municipal|munic[íi]pio\s+de\s+[A-ZÀ-Ú]|secretaria\s+municipal|c[âa]mara\s+municipal", re.I)),
           ("estadual", re.compile(r"governo\s+do\s+estado|secretaria\s+de\s+estado|secretaria\s+estadual|assembleia\s+legislativa", re.I)),
           ("federal", re.compile(r"minist[ée]rio\s+d[aeo]s?\s|governo\s+federal|uni[ãa]o\s+federal", re.I)))
MODALIDADES = (("prêmio", r"pr[êe]mio"), ("chamamento público", r"chamamento\s+p[úu]blico"), ("credenciamento", r"credenciamento"),
               ("fomento", r"termo\s+de\s+fomento|\bfomento\b"), ("colaboração", r"termo\s+de\s+colabora[çc][ãa]o"),
               ("patrocínio", r"patroc[íi]nio"), ("bolsa", r"\bbolsas?\b"), ("seleção de projetos", r"sele[çc][ãa]o\s+de\s+projetos"))
AREAS = (("cultura", r"\bcultur"), ("esporte", r"\besport"), ("assistência social", r"assist[êe]ncia\s+social"), ("saúde", r"\bsa[úu]de\b"),
         ("educação", r"\beduca[çc]"), ("meio ambiente", r"meio\s+ambiente|ambiental"), ("direitos humanos", r"direitos\s+humanos"),
         ("criança e adolescente", r"crian[çc]a|adolescente"), ("pessoa idosa", r"\bidos[oa]"))
UFS = {"AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas", "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal",
       "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul", "MG": "Minas Gerais",
       "PA": "Pará", "PB": "Paraíba", "PR": "Paraná", "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro",
       "RN": "Rio Grande do Norte", "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina",
       "SP": "São Paulo", "SE": "Sergipe", "TO": "Tocantins"}


def _sem_acento(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c)).lower()


def _frase(texto: str, ini: int, fim: int, margem: int = 140) -> str:
    """O trecho literal em volta do achado (cortado nas bordas da frase, sem sair do texto)."""
    a = max(0, ini - margem)
    b = min(len(texto), fim + margem)
    corte_a = max(texto.rfind(".", a, ini), texto.rfind("\n", a, ini))
    corte_b = [p for p in (texto.find(".", fim, b), texto.find("\n", fim, b)) if p != -1]
    a = corte_a + 1 if corte_a != -1 else a
    b = (min(corte_b) + 1) if corte_b else b
    return texto[a:b].strip()[:500]


def _primeiro(paginas: list[str], rx: re.Pattern, perto: re.Pattern | None = None, janela: int = 160):
    for n, texto in enumerate(paginas, 1):
        for m in rx.finditer(texto):
            if perto is None or perto.search(texto[max(0, m.start() - janela): m.end() + janela]):
                return n, texto, m
    return None


def extrair(paginas: list[str], faltam: list[str], orgao: str | None = None, municipio: str | None = None,
            uf: str | None = None) -> dict[str, dict[str, Any]]:
    """Para os itens que faltam, o que o texto traz em forma fixa: {item: {valor, trecho, pagina, origem}}."""
    saida: dict[str, dict[str, Any]] = {}
    paginas = [p for p in paginas if p]
    if not paginas:
        return saida

    def poe(item: str, valor: str, n: int, trecho: str) -> None:
        trecho = trecho.strip()
        if item in faltam and item not in saida and trecho and trecho in paginas[n - 1]:
            saida[item] = {"valor": valor.strip()[:300], "trecho": trecho[:500], "pagina": n, "origem": "extrator"}

    if "Prazo de inscrição" in faltam:
        inscr = re.compile(r"inscri[çc]", re.I)
        r = _primeiro(paginas, INTERVALO, inscr) or _primeiro(paginas, DATA_SOLTA, inscr)
        if r:
            n, t, m = r
            valor = f"{m.group(1)} a {m.group(2)}" if m.re is INTERVALO else f"até {m.group(1)}"
            poe("Prazo de inscrição", valor, n, _frase(t, m.start(), m.end()))
    if "Valor" in faltam:
        r = _primeiro(paginas, REAIS, re.compile(r"valor|total|recurso|pr[êe]mio|apoio|montante|or[çc]amento|financ", re.I), 120)
        if r:
            n, t, m = r
            poe("Valor", m.group(0), n, _frase(t, m.start(), m.end()))
    if "Anexos" in faltam:
        for n, t in enumerate(paginas, 1):
            achados = list(ANEXO.finditer(t))
            nomes = list(dict.fromkeys(re.sub(r"\s+", " ", a.group(0)).strip() for a in achados))
            if len(nomes) >= 1:
                poe("Anexos", "; ".join(nomes[:8]), n, _frase(t, achados[0].start(), achados[0].end(), 60))
                break
    if "Objeto" in faltam:
        r = _primeiro(paginas, OBJETO) or _primeiro(paginas, FINALIDADE)
        if r:
            n, t, m = r
            poe("Objeto", m.group(1), n, m.group(0))
    if "Requisitos" in faltam:
        r = _primeiro(paginas, REQUISITOS)
        if r:
            n, t, m = r
            poe("Requisitos", m.group(1), n, m.group(1))
    if "Órgão / financiador" in faltam and orgao and len(orgao) >= 6:
        rx = re.compile(re.escape(orgao.strip()), re.I)
        r = _primeiro(paginas, rx)
        if r:
            n, t, m = r
            poe("Órgão / financiador", m.group(0), n, _frase(t, m.start(), m.end(), 60))
    if "Território" in faltam:
        nomes = [x for x in (municipio, UFS.get((uf or "").upper())) if x and len(x) >= 4]
        for nome in nomes:
            r = _primeiro(paginas, re.compile(r"\b" + re.escape(nome) + r"\b", re.I))
            if r:
                n, t, m = r
                poe("Território", m.group(0) + ("" if nome == municipio else ""), n, _frase(t, m.start(), m.end(), 60))
                break
    if "Esfera" in faltam:
        for nome, rx in ESFERAS:
            r = _primeiro(paginas, rx)
            if r:
                n, t, m = r
                poe("Esfera", nome, n, _frase(t, m.start(), m.end(), 50))
                break
    if "Modalidade" in faltam:
        for nome, padrao in MODALIDADES:
            r = _primeiro(paginas, re.compile(padrao, re.I))
            if r:
                n, t, m = r
                poe("Modalidade", nome, n, _frase(t, m.start(), m.end(), 60))
                break
    if "Área de atuação" in faltam:
        for nome, padrao in AREAS:
            r = _primeiro(paginas, re.compile(padrao, re.I))
            if r:
                n, t, m = r
                poe("Área de atuação", nome, n, _frase(t, m.start(), m.end(), 60))
                break
    return saida
