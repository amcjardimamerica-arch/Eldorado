"""Acervo de Editais Históricos no Google Drive — a regra de Goiás.

REGRA (definida pelo titular em 08/09/2026)

Todo edital que se aplique a Goiás tem de ter o edital extraído e arquivado na
pasta `Eldorado — Farol de Alexandria / Editais Históricos / GO — Goiás` do
Google Drive, com o texto do documento, o dossiê de metadados e o endereço do
PDF de origem. "Aplicar-se a Goiás" é qualquer um destes três casos:

  1. edital de município goiano;
  2. edital estadual de Goiás;
  3. edital de âmbito nacional que admita proponente sediado em Goiás.

O arquivamento é condição de conclusão da verificação, não etapa opcional: um
edital de Goiás verificado e não arquivado conta como pendência.

POR QUE A REGRA EXISTE

Dos 9 registros de Goiás que a base tinha, 3 apontavam para
`goias.gov.br/cultura/termos-de-fomento` (lista de termos já celebrados, sem
inscrição), 2 tinham o edital principal AUSENTE do próprio registro público do
PNCP — só errata, comunicado e anexos — e 1 estava cadastrado com o objeto de
outro processo. Sem cópia própria, a busca histórica de Goiás depende de o
município ter mantido o link no ar, e ele não mantém.

ONDE FICA O QUE

  Drive: pasta 1CF1VdDgGxsVhxlmYum1_erCtd8A3T2o8 (Editais Históricos)
         subpasta 17oInKWlCCcDIyhV7QjcZfOmUHYVwG-4p (GO — Goiás)
         banco: BANCO-EDITAIS-HISTORICOS.json
  Repo:  espelho local em `dados/acervo/banco_editais_historicos.json`, para
         que o painel e os testes funcionem sem rede e sem credencial.

O upload dos PDFs é feito por `scripts/espelhar_editais_drive.py`, que roda no
GitHub Actions (onde há rede) com a credencial de serviço; este módulo só lê,
valida e aponta pendências.
"""
from __future__ import annotations

import json
import re

from .inconformidade import avaliar_item as _avaliar_inconformidade
from .nucleo import ROOT, load_json, now_iso, write_json

BANCO = ROOT / "dados/acervo/banco_editais_historicos.json"

PASTA_ACERVO_DRIVE = "1CF1VdDgGxsVhxlmYum1_erCtd8A3T2o8"
PASTA_GO_DRIVE = "17oInKWlCCcDIyhV7QjcZfOmUHYVwG-4p"

# Fontes estaduais de Goiás conferidas com navegador em 08/09/2026.
FONTES_GOIAS = (
    "https://www.goias.gov.br/cultura/pnab/edital-2026-pnab/",
    "https://pnab.cultura.go.gov.br",
    "https://web.ufg.br/plateia-editais/",
    "https://fica.go.gov.br",
)

# Página que nunca terá edital aberto: termos já celebrados por inexigibilidade.
ARMADILHA_TERMOS_GO = "goias.gov.br/cultura/termos-de-fomento"

_MUNICIPIO_GO = re.compile(r"\.go\.gov\.br|/GO/|\bGoi[áa]s\b|\bGoi[âa]nia\b", re.I)


def aplica_se_a_goias(item: dict) -> tuple[bool, str]:
    """Diz se o edital entra na regra de arquivamento e por qual dos três casos."""
    uf = (item.get("uf") or "").upper()
    if uf == "GO":
        return True, "edital de órgão de Goiás (municipal ou estadual)"
    texto = " ".join(str(item.get(c) or "") for c in ("orgao", "titulo", "link_capturado",
                                                      "pagina_oficial", "url"))
    if _MUNICIPIO_GO.search(texto):
        return True, "órgão ou endereço em Goiás identificado no registro"
    nivel = (item.get("nivel") or item.get("esfera") or "").lower()
    if nivel == "federal" or (not uf and re.search(r"[âa]mbito nacional|nacional", texto, re.I)):
        return True, "edital de âmbito nacional: admite proponente sediado em Goiás"
    return False, "não se aplica a Goiás"


def banco() -> dict:
    """Espelho local do banco do Drive. Sem arquivo, devolve banco vazio."""
    if not BANCO.exists():
        return {"banco": "Editais Históricos", "versao": 1, "itens": []}
    return load_json(BANCO)


def arquivados() -> set[str]:
    return {str(x.get("id")) for x in banco().get("itens", []) if x.get("id")}


def pendencias(itens: list[dict]) -> list[dict]:
    """Editais de Goiás que precisam ser arquivados e ainda não estão no acervo.

    Registro reprovado por inconformidade de objeto não entra na conta: não é
    edital de fomento, então não há o que arquivar. Sem esse filtro o relatório
    acusaria pendência para qualificação de OS, incentivo a empresas e prêmio
    interno de tribunal — que é exatamente o ruído que o acervo deve evitar.
    """
    ja = {x[:8] for x in arquivados()}
    fora = []
    for it in itens:
        oid = str(it.get("id") or "")
        aplica, motivo = aplica_se_a_goias(it)
        if not aplica or oid[:8] in ja:
            continue
        inc = _avaliar_inconformidade(it)
        if not inc["ok"]:
            continue
        fora.append({"id": oid, "titulo": (it.get("titulo") or "")[:120],
                     "uf": it.get("uf"), "motivo_da_regra": motivo,
                     "pdf_origem": it.get("pagina_oficial") or it.get("url")})
    return fora


def conferir(itens: list[dict] | None = None) -> dict:
    """Relatório de conformidade da regra de Goiás, gravado em estado/."""
    if itens is None:
        lista = ROOT / "docs/dados/nao_verificados.json"
        itens = load_json(lista).get("itens", []) if lista.exists() else []
    pend = pendencias(itens)
    b = banco()
    rel = {
        "em": now_iso(),
        "regra": ("todo edital que se aplique a Goiás — municipal goiano, estadual de Goiás "
                  "ou nacional que admita proponente de Goiás — tem de estar arquivado no "
                  "acervo de Editais Históricos do Drive"),
        "pasta_drive": PASTA_GO_DRIVE,
        "arquivados": len(b.get("itens", [])),
        "pendentes": len(pend),
        "nota": ("registros reprovados por inconformidade de objeto não geram pendência: "
                 "não são edital de fomento e não há o que arquivar"),
        "lista_pendentes": pend[:60],
        "fontes_goias_validas": list(FONTES_GOIAS),
        "armadilha": ARMADILHA_TERMOS_GO,
    }
    write_json(ROOT / "estado/acervo_goias.json", rel)
    return rel


if __name__ == "__main__":
    print(json.dumps(conferir(), ensure_ascii=False, indent=2)[:2500])
