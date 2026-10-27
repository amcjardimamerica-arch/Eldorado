"""Os 12 itens do livro e o critério único da estrela (titular, 04/10/2026), aproveitado do Eldorado0.

bronze = Objeto + Prazo de inscrição + Território · prata = bronze + Valor + Requisitos · ouro = os 12 itens, cada um
VALIDADO (com valor) ou DISPENSADO com justificativa de que não se aplica. "Não informado", "não localizado" ou vazio
NÃO é dispensa: é falta.
"""
from __future__ import annotations

import re

DOZE = ("Objeto", "Prazo de inscrição", "Resultado", "Prazo de recurso", "Valor", "Órgão / financiador",
        "Território", "Esfera", "Requisitos", "Anexos", "Modalidade", "Área de atuação")
BRONZE = ("Objeto", "Prazo de inscrição", "Território")
PRATA = BRONZE + ("Valor", "Requisitos")
NUCLEO = BRONZE                       # 11/10: o núcleo nunca é dispensado
FALTA = re.compile(r"^\s*(n[ãa]o (informad|localizad|encontrad|consta)|sem informa|pendente|—|-|\?)", re.I)
JUSTIFICA = re.compile(r"n[ãa]o consta nos documentos oficiais lidos|dispensad[oa] pel[oa]|n[ãa]o se aplica|n[ãa]o aplic[aá]vel|inaplic[aá]vel|n[ãa]o h[aá] (prazo de )?recurso|sem sele[çc][ãa]o competitiva|fluxo cont[ií]nuo|cadastro permanente|regime", re.I)


def dispensa_valida(item: str, justificativa: str | None) -> bool:
    """Dispensa só com a justificativa de que o item não se aplica, e nunca para o núcleo."""
    j = str(justificativa or "").strip()
    return item not in NUCLEO and bool(JUSTIFICA.search(j)) and len(j) >= 20


FASES_CHROME = ("verificacao externa", "analise externa")   # a análise externa: o Claude no Chrome


def resolvido(certidao: dict | None) -> bool:
    """Item comprovado (valor real com prova) ou dispensado com justificativa válida."""
    if not certidao:
        return False
    if certidao.get("situacao") == "dispensado":               # a dispensa só vale pelo Claude no Chrome (titular, 24/10/2026)
        return certidao.get("fase") in FASES_CHROME and dispensa_valida(certidao.get("item", ""), certidao.get("justificativa"))
    v = str(certidao.get("valor") or "").strip()
    return certidao.get("situacao") == "comprovado" and len(v) >= 3 and not FALTA.search(v)




def nivel(certidoes: dict[str, dict], origem_confirmada: bool = False) -> str:
    """A estrela pela régua da titular (23/10/2026): bronze = o prazo de inscrição certificado; prata = o prazo e o link
    original da oportunidade (a origem confirmada do livro); ouro = prata e os 12 itens, cada um comprovado ou dispensado
    pelo Claude no Chrome (as dispensas automáticas não valem para o ouro); sem o prazo, sem estrela."""
    prazo = certidoes.get("Prazo de inscrição")
    if not (prazo and prazo.get("situacao") == "comprovado" and resolvido(prazo)):
        return "sem"
    if not origem_confirmada:
        return "bronze"

    return "ouro" if all(resolvido(certidoes.get(k)) for k in DOZE) else "prata"   # o checklist completo, ou dispensado pelo Chrome

def faltando(certidoes: dict[str, dict]) -> list[str]:
    return [k for k in DOZE if not resolvido(certidoes.get(k))]


def itens() -> list[dict[str, str]]:
    return [{"codigo": k, "nome": k, "nucleo": "sim" if k in NUCLEO else "não"} for k in DOZE]


FASES_VALIDADAS = ("eldorado0", "verificacao externa", "titular")   # validadas por pessoa ou por verificação externa


TIPOS_EDITAL = ("pdf", "docx", "doc", "odt", "ato")   # o edital: o documento ou o ato publicado no diário (não a página)


def do_edital(certidoes: list[dict], tipos: dict) -> None:
    """Marca em cada certidão se ela veio do edital (o tipo do documento de onde foi lida)."""
    for c in certidoes:
        c["_edital"] = tipos.get(c.get("documento_id")) in TIPOS_EDITAL


def melhor(certidoes: list[dict]) -> dict[str, dict]:
    """A certidão que vale para cada item: a validada antes da automática; entre as do mesmo tipo, a que tem prova
    literal (o trecho e a página da fonte); depois, a mais recente. Uma automática nunca supera uma validada (22/10/2026)."""
    out: dict[str, dict] = {}
    # 27/10/2026 (titular): cada oportunidade é certificada NO EDITAL; o anúncio ou o site só valem sem edital
    for c in sorted(certidoes, key=lambda c: (bool(c.get("_edital")), c.get("fase") in FASES_VALIDADAS,
                                               bool(c.get("trecho")) and c.get("pagina") is not None, c.get("id") or 0)):
        out[c["item"]] = c
    return out


CRITICOS = ("Prazo de inscrição", "Valor", "Esfera", "Território")   # contradição nesses itens manda o livro para revisão
