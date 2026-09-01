"""Emendas · fases 3 e 5 — aprovação automática e produção dos documentos.

Fase 3: emenda parlamentar não tem edital nem requisito eliminatório de
certame, então TODAS as associações cadastradas são aprovadas automaticamente.
Não há conselho a deliberar sobre elegibilidade — a decisão de a qual gabinete
pedir é do titular.

Fase 5: para cada associação, produz um ofício por parlamentar e um projeto
com plano de trabalho completo, ajustados ao perfil e à área de atuação da
entidade. O ofício segue o padrão dos ofícios da associação no Drive:
cabeçalho com número e data, destinatário, assunto, corpo, e o fecho com
presidente e CNPJ.

Nada é inventado: valor, metas quantitativas e dados sensíveis que não estejam
no cadastro público entram como campo a preencher, listado na nota técnica.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from .biblioteca import ASSOCIACOES, pasta_edital_da_associacao
from .nucleo import ROOT, load_json, now_iso, slug, write_json

BIBLIOTECA = ROOT / "biblioteca_alexandria/emendas"

_TRATAMENTO = {
    "Vereador(a)": ("Ao Excelentíssimo Senhor", "Vereador", "Senhor Vereador"),
    "Deputado(a) Estadual": ("Ao Excelentíssimo Senhor", "Deputado Estadual",
                             "Senhor Deputado"),
    "Deputado(a) Federal": ("Ao Excelentíssimo Senhor", "Deputado Federal",
                            "Senhor Deputado"),
    "Senador(a)": ("Ao Excelentíssimo Senhor", "Senador", "Senhor Senador"),
}


def _perfil(slug_assoc: str) -> dict:
    arq = ASSOCIACOES / slug_assoc / "perfil_publico.json"
    return load_json(arq) if arq.exists() else {}


def oficio(assoc: dict, parlamentar: dict, tipo: dict, ano: int,
           numero: int, hoje: date) -> str:
    """Ofício no padrão da associação (modelo dos ofícios do Drive)."""
    trat, cargo, voc = _TRATAMENTO.get(parlamentar.get("cargo") or "",
                                       ("Ao Excelentíssimo Senhor",
                                        parlamentar.get("cargo") or "Parlamentar",
                                        "Senhor Parlamentar"))
    areas = ", ".join(assoc.get("areas") or []) or "atuação comunitária"
    municipio = (assoc.get("territorios") or ["Goiânia"])[0]
    data_br = hoje.strftime("%d de %B de %Y")
    meses = {"January": "janeiro", "February": "fevereiro", "March": "março",
             "April": "abril", "May": "maio", "June": "junho", "July": "julho",
             "August": "agosto", "September": "setembro", "October": "outubro",
             "November": "novembro", "December": "dezembro"}
    for en, pt in meses.items():
        data_br = data_br.replace(en, pt)
    return f"""Ofício nº {numero:03d}/{ano} – AMC-JA{" " * 6}Goiânia, {data_br}.

{trat}

{parlamentar.get("nome_parlamentar") or "[nome do parlamentar]"}

{cargo} — {parlamentar.get("partido") or "[partido]"}/{parlamentar.get("uf") or "[UF]"}

{parlamentar.get("gabinete") or "[gabinete]"}

{parlamentar.get("endereco") or "[endereço da casa legislativa]"}

Assunto: Solicita destinação de emenda parlamentar {ano} para projeto social.

{voc},

Aliado a satisfação de cumprimentá-lo, sirvo-me do presente para solicitar a
Vossa Excelência a destinação de emenda parlamentar do exercício {ano} em favor
da {assoc.get("nome") or "[associação]"}, entidade sem fins lucrativos sediada
em {municipio}, com atuação em {areas}.

A entidade apresenta, em anexo, projeto técnico com plano de trabalho completo,
contendo diagnóstico, objeto, metas, indicadores, cronograma físico-financeiro,
memória de cálculo e matriz de prestação de contas, elaborado conforme a
Lei 13.019/2014 e o {tipo.get("lei") or "regramento aplicável"}.

O recurso será integralmente aplicado no objeto proposto, com prestação de
contas na forma da legislação, cabendo à entidade a execução e o
acompanhamento das metas pactuadas.

Para respostas, indica-se o e-mail <amc.jardimamerica@gmail.com>.

Na expectativa de contar com especial atenção de Vossa Excelência, antecipo
agradecimentos, ao ensejo, renovo os protestos de elevada estima e distinta
consideração.

Cordialmente,

Eduardo Kleber Xavier Lemos

Presidente da {assoc.get("nome") or "[associação]"}

CNPJ [preencher — dado não consta do cadastro público]
"""


def plano_de_trabalho(assoc: dict, tipo: dict, ano: int) -> str:
    """Plano de trabalho completo, ajustado ao perfil da associação."""
    areas = assoc.get("areas") or []
    area_principal = (areas[0] if areas else "atuação comunitária").replace("_", " ")
    municipio = (assoc.get("territorios") or ["Goiânia"])[0]
    nome = assoc.get("nome") or "[associação]"
    return f"""# Plano de trabalho — emenda parlamentar {ano}

**Proponente:** {nome}
**Território:** {municipio}
**Áreas de atuação:** {", ".join(a.replace("_", " ") for a in areas) or "a declarar"}
**Fonte:** {tipo["nome"]}
**Fundamento:** {tipo["lei"]}; Lei 13.019/2014 (MROSC)

## 1. Identificação do proponente
- Razão social: {nome}
- Natureza jurídica: {assoc.get("natureza_juridica") or "associação privada sem fins lucrativos"}
- Tempo de existência: {assoc.get("anos_existencia") if assoc.get("anos_existencia") is not None else "[preencher]"} ano(s)
- CNPJ, endereço, telefone e responsável legal: **[preencher — dados não constam do cadastro público]**

## 2. Diagnóstico
Descrever o problema a ser enfrentado em {municipio}, com fonte de dados
(IBGE, SUAS, secretaria municipal), população afetada e recorte territorial.
**[preencher com o diagnóstico da entidade]**

## 3. Objeto
Execução de projeto na área de {area_principal}, compatível com o estatuto da
entidade e com a política pública correspondente.

## 4. Justificativa
Relacionar o objeto ao diagnóstico, à experiência da entidade e ao interesse
público, demonstrando por que a emenda é o instrumento adequado.

## 5. Metas e indicadores
| Meta | Indicador | Linha de base | Meio de verificação | Responsável |
|---|---|---|---|---|
| [preencher] | [preencher] | [preencher] | lista de presença, relatório, foto | [preencher] |

Metas devem ser SMART: específicas, mensuráveis, alcançáveis, relevantes e
com prazo.

## 6. Cronograma físico-financeiro
| Etapa | Início | Fim | Valor |
|---|---|---|---|
| [preencher] | | | |

## 7. Orçamento e memória de cálculo
Discriminar cada item com quantidade, valor unitário e pesquisa de preços
(três cotações ou tabela oficial de referência). **[preencher]**

## 8. Contrapartida e sustentabilidade
Indicar contrapartida (quando exigida) e como a ação segue após o recurso.

## 9. Governança, riscos e proteção de dados
Responsáveis, matriz de riscos, acessibilidade, comunicação e tratamento de
dados pessoais conforme a LGPD.

## 10. Prestação de contas
Cada meta define desde já qual documento provará sua entrega: relatório de
execução do objeto, relatório financeiro, notas fiscais, listas, registros
fotográficos e conciliação bancária.

---
Documento gerado automaticamente pelo Farol de Alexandria a partir do perfil
público da associação. Os campos marcados **[preencher]** dependem de dados
sensíveis que não ficam no repositório público — completá-los antes do
protocolo. Nenhuma informação foi inventada.
"""


def preparar(ano: int | None = None, hoje: date | None = None,
             limite_oficios: int = 40) -> dict:
    """Fases 3 e 5: aprova todas as associações e produz os documentos."""
    from .emendas import _cfg, ESTADO
    hoje = hoje or date.today()
    ano = ano or hoje.year
    cfg = _cfg()
    idx = ASSOCIACOES / "indice.json"
    assocs = load_json(idx).get("associacoes", []) if idx.exists() else []
    saida = []
    for tipo in cfg["tipos"]:
        arq = ESTADO / f'{tipo["id"]}-{ano}.json'
        if not arq.exists():
            continue
        op = load_json(arq)
        parlamentares = op.get("parlamentares") or []
        for a in assocs:
            perfil = _perfil(a["slug"])
            destino = pasta_edital_da_associacao(a["slug"], f'{tipo["nome"]} {ano}')
            (destino / "oficios").mkdir(parents=True, exist_ok=True)
            gerados = []
            for i, p in enumerate(parlamentares[:limite_oficios], start=1):
                nome_arq = f'{i:03d}-{slug(p.get("nome_parlamentar") or "parlamentar")}.md'
                (destino / "oficios" / nome_arq).write_text(
                    oficio(perfil, p, tipo, ano, i, hoje), encoding="utf-8")
                gerados.append(nome_arq)
            (destino / "PLANO-DE-TRABALHO.md").write_text(
                plano_de_trabalho(perfil, tipo, ano), encoding="utf-8")
            dossie = {
                "fonte": {"tipo": tipo["id"], "nome": tipo["nome"], "ano": ano,
                          "sem_edital": True,
                          "janela": {"inicio": op["inicio"], "fim": op["fim"]}},
                "associacao": {"slug": a["slug"], "nome": a["nome"]},
                "fase_3": {"decisao": "aprovado automaticamente",
                           "fundamento": ("emenda parlamentar não tem edital nem "
                                          "requisito eliminatório de certame; a "
                                          "oportunidade existe em todos os gabinetes")},
                "fase_5": {"oficios_gerados": len(gerados),
                           "parlamentares_disponiveis": len(parlamentares),
                           "plano_de_trabalho": "PLANO-DE-TRABALHO.md",
                           "limite_por_execucao": limite_oficios},
                "pendencias": (op.get("detalhes") or {}).get("pendencias", []),
                "campos_a_preencher": ["CNPJ", "endereço", "telefone",
                                       "diagnóstico", "metas", "orçamento"],
                "gerado_em": now_iso(),
                "padrao_documental": "ofícios da associação (Google Drive)",
            }
            write_json(destino / "dossie.json", dossie)
            nota = [f'# Nota técnica — {tipo["nome"]} {ano}', "",
                    f'**Associação:** {a["nome"]}  ',
                    f'**Janela de captação:** {op["inicio"]} a {op["fim"]}  ',
                    f'**Parlamentares com mandato levantados:** {len(parlamentares)}  ',
                    f'**Ofícios gerados nesta execução:** {len(gerados)}', "",
                    "## Documentos prontos", "",
                    f'- `PLANO-DE-TRABALHO.md` — plano completo conforme a Lei 13.019/2014',
                    f'- `oficios/` — um ofício por gabinete, no padrão da entidade', "",
                    "## Falta providenciar", "",
                    "Campos marcados **[preencher]** nos documentos dependem de dados "
                    "que não ficam no repositório público:", "",
                    "- CNPJ, endereço e telefone da entidade",
                    "- diagnóstico local com fonte de dados",
                    "- metas, indicadores e linha de base",
                    "- orçamento com memória de cálculo e pesquisa de preços", ""]
            if (op.get("detalhes") or {}).get("pendencias"):
                nota += ["## Pendências do levantamento", ""]
                nota += [f'- {p}' for p in op["detalhes"]["pendencias"]]
            nota += ["", "---", "",
                     "Gerado pelo Farol de Alexandria. Nenhuma informação foi "
                     "inventada; conferir antes do protocolo."]
            (destino / "NOTA-TECNICA.md").write_text("\n".join(nota) + "\n",
                                                     encoding="utf-8")
            saida.append({"tipo": tipo["id"], "associacao": a["slug"],
                          "oficios": len(gerados),
                          "pasta": str(destino.relative_to(ROOT))
                          if str(destino).startswith(str(ROOT)) else str(destino)})
    resumo = {"executado_em": now_iso(), "ano": ano, "preparados": saida,
              "associacoes": len(assocs),
              "nota": ("fase 3 aprova todas as associações (não há requisito "
                       "eliminatório); fase 5 produz ofícios e plano de trabalho")}
    write_json(BIBLIOTECA / f"preparacao-{ano}.json", resumo)
    return resumo


if __name__ == "__main__":
    print(json.dumps(preparar(), ensure_ascii=False, indent=2)[:1500])
