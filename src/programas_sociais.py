"""PROGRAMAS SOCIAIS E LEIS DE INCENTIVO — o que cada empresa já apoiou.

Saber que uma empresa "tem incentivo fiscal" não ajuda ninguém a pedir. O que ajuda é saber
**por qual lei** ela já destinou, porque cada lei tem porta, órgão e documento próprios:
quem destina pelo FIA fala com o conselho da criança do município; quem destina pela Rouanet
passa pelo Ministério da Cultura e precisa de projeto aprovado antes.

Uma empresa que já destinou por uma lei é candidata muito melhor do que uma que apenas
poderia: ela já tem o caminho interno montado — o setor fiscal sabe fazer, a diretoria já
aprovou antes, existe precedente. É por isso que o histórico pesa mais que a capacidade.

A pontuação social/ESG ordena a lista por EVIDÊNCIA DE DOAÇÃO, não por tamanho da empresa.
Uma empresa média com instituto próprio e três leis no histórico vem antes de uma gigante
que nunca destinou nada.
"""
from __future__ import annotations

import re

# As leis pelas quais uma empresa pode destinar, com o que cada uma exige
LEIS = {
    "rouanet": {
        "nome": "Lei Rouanet", "lei": "Lei 8.313/1991", "area": "cultura",
        "orgao": "Ministério da Cultura (SALIC)", "teto": "4% do IRPJ devido",
        "porta": "projeto precisa estar aprovado no SALIC antes de a empresa destinar",
        "apelidos": ["rouanet", "lei rouanet", "incentivo à cultura", "salic", "cultura"]},
    "esporte": {
        "nome": "Lei de Incentivo ao Esporte", "lei": "Lei 11.438/2006", "area": "esporte",
        "orgao": "Ministério do Esporte", "teto": "1% do IRPJ devido",
        "porta": "projeto aprovado no Ministério do Esporte; inclui paradesporto",
        "apelidos": ["esporte", "lie", "lei do esporte", "incentivo ao esporte"]},
    "fia": {
        "nome": "Fundo da Criança e do Adolescente", "lei": "Lei 8.069/1990 (ECA)", "area": "criança e adolescente",
        "orgao": "CMDCA do município", "teto": "1% do IRPJ devido",
        "porta": "a entidade precisa estar inscrita no CMDCA; a destinação é ao fundo, não à entidade",
        "apelidos": ["fia", "fumcad", "criança", "crianca", "adolescente", "cmdca", "eca"]},
    "idoso": {
        "nome": "Fundo do Idoso", "lei": "Lei 12.213/2010", "area": "pessoa idosa",
        "orgao": "Conselho Municipal do Idoso", "teto": "1% do IRPJ devido",
        "porta": "inscrição no conselho do idoso; destinação ao fundo municipal",
        "apelidos": ["idoso", "fundo do idoso", "cmi"]},
    "pronon": {
        "nome": "PRONON", "lei": "Lei 12.715/2012", "area": "oncologia",
        "orgao": "Ministério da Saúde", "teto": "1% do IRPJ devido",
        "porta": "projeto de atenção oncológica credenciado no Ministério da Saúde",
        "apelidos": ["pronon", "oncologia", "câncer", "cancer"]},
    "pronas": {
        "nome": "PRONAS/PCD", "lei": "Lei 12.715/2012", "area": "pessoa com deficiência",
        "orgao": "Ministério da Saúde", "teto": "1% do IRPJ devido",
        "porta": "projeto de reabilitação ou inclusão da pessoa com deficiência credenciado",
        "apelidos": ["pronas", "pcd", "deficiência", "deficiencia"]},
    "pat": {
        "nome": "Programa de Alimentação do Trabalhador", "lei": "Lei 6.321/1976", "area": "alimentação",
        "orgao": "Ministério do Trabalho", "teto": "dedução sobre despesa",
        "porta": "benefício do próprio quadro de empregados; não financia projeto externo",
        "apelidos": ["pat", "alimentação do trabalhador"]},
    "goyazes": {
        "nome": "Fundo de Cultura de Goiás (Goyazes)", "lei": "Lei estadual 15.633/2006", "area": "cultura",
        "orgao": "Secult-GO", "teto": "conforme edital estadual",
        "porta": "seleção por edital estadual; alcance restrito a Goiás",
        "apelidos": ["goyazes", "fundo de cultura", "secult"]},
}

# O que vale ponto, e por quê. Histórico pesa mais que capacidade.
PESOS = {
    "lei_com_historico": 14,      # já destinou por esta lei: o caminho interno existe
    "instituto_proprio": 18,      # instituto ou fundação: verba e governança dedicadas
    "gife": 12,                   # mapeada em fonte de investimento social
    "area_declarada": 6,          # diz publicamente o que apoia
    "patrocinio_privado": 8,      # patrocina com verba própria
    "esg_relatorio": 10,          # publica relatório
    "contato_conhecido": 3,       # dá para chegar nela
}


def _norm(s: str) -> str:
    return re.sub(r"[^a-zà-ú ]", "", str(s or "").lower()).strip()


def identificar(termo: str) -> str | None:
    """De 'FIA', 'Lei do Esporte' ou 'incentivo à cultura' para a chave da lei."""
    t = _norm(termo)
    if not t:
        return None
    for chave, d in LEIS.items():
        if t == chave or any(a in t or t in a for a in d["apelidos"]):
            return chave
    return None


def programas_de(e: dict) -> list[dict]:
    """A lista de programas que a empresa já apoiou, com a porta de entrada de cada um."""
    achados, vistos = [], set()

    def _add(chave, prova, historico):
        if not chave or chave in vistos:
            return
        vistos.add(chave)
        d = LEIS[chave]
        achados.append({"chave": chave, "nome": d["nome"], "lei": d["lei"], "area": d["area"],
                        "orgao": d["orgao"], "teto": d["teto"], "porta": d["porta"],
                        "historico": historico, "prova": (prova or "")[:160]})

    for inc in (e.get("incentivos") or []):
        _add(identificar(inc), f"declarado como incentivo utilizado: {inc}", True)
    for d in (e.get("destinacoes") or []):
        if isinstance(d, dict):
            _add(identificar(d.get("programa")),
                 f"{d.get('programa')} {d.get('ano') or ''} — {d.get('projeto') or ''}".strip(), True)
    # o texto do 'por que pontua' às vezes nomeia a lei sem estar no campo próprio
    texto = " ".join(str(x) for x in (e.get("por") or [])) + " " + str(e.get("apoia") or "")
    for chave in LEIS:
        if chave in vistos:
            continue
        if any(a in _norm(texto) for a in LEIS[chave]["apelidos"] if len(a) > 4):
            _add(chave, "mencionado no levantamento", False)
    return achados


def pontos_sociais(e: dict, programas: list[dict] | None = None) -> dict:
    """A nota que ordena a lista: evidência de doação, não tamanho da empresa."""
    progs = programas if programas is not None else programas_de(e)
    por, total = [], 0
    com_hist = [p for p in progs if p["historico"]]
    if com_hist:
        n = len(com_hist) * PESOS["lei_com_historico"]
        total += n
        por.append(f"{n}: já destinou por {len(com_hist)} lei(s) — {', '.join(p['nome'] for p in com_hist)}")
    mencionados = [p for p in progs if not p["historico"]]
    if mencionados:
        total += 4 * len(mencionados)
        por.append(f"{4 * len(mencionados)}: {len(mencionados)} lei(s) citada(s) no levantamento, a confirmar")
    if e.get("programa"):
        total += PESOS["instituto_proprio"]
        por.append(f"{PESOS['instituto_proprio']}: tem {e['programa']} — verba e governança próprias")
    texto = " ".join(str(x) for x in (e.get("por") or []))
    if "gife" in texto.lower():
        total += PESOS["gife"]
        por.append(f"{PESOS['gife']}: mapeada em fonte de investimento social (GIFE)")
    if "esg" in texto.lower() or "sustentabilidade" in texto.lower():
        total += PESOS["esg_relatorio"]
        por.append(f"{PESOS['esg_relatorio']}: publica relatório ESG ou de sustentabilidade")
    if e.get("apoia"):
        total += PESOS["area_declarada"]
        por.append(f"{PESOS['area_declarada']}: declara publicamente apoiar {e['apoia']}")
    if str(e.get("origem") or "").startswith("patroc"):
        total += PESOS["patrocinio_privado"]
        por.append(f"{PESOS['patrocinio_privado']}: patrocina eventos com verba própria")
    c = e.get("cadastro") or {}
    if c.get("telefone") or c.get("email") or e.get("site"):
        total += PESOS["contato_conhecido"]
        por.append(f"{PESOS['contato_conhecido']}: há caminho de contato")
    return {"pontos": total, "por": por,
            "nivel": "forte" if total >= 50 else "bom" if total >= 25 else "inicial" if total else "sem evidência",
            "leis_com_historico": len(com_hist), "programas": len(progs)}
