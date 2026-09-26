"""Incentivos fiscais verificados das empresas da Biblioteca de Alexandria.

A PERGUNTA DO TITULAR (26/09/2026)

"Analise todos os dados de empresas na biblioteca de alexandria e faça a
atualização deles se destinaram valores pela Rouanet, FIA, Esporte, Idoso,
PRONON, PRONAS, Goyazes, PAT."

O QUE HAVIA ANTES DESTA ROTINA

Nada verificado. O campo `destinacoes_5_anos` estava vazio em todas as empresas,
e os 26 arquivos de consulta ao SALIC gravados em `dados/empresas/destinacoes/`
diziam a mesma coisa: "falha: HTTPError". A API do Ministério da Cultura tinha
mudado de endereço — de `/v1/incentivadores` para `/api/v1/incentivadores` — e
o motor continuava batendo na porta antiga. Ao mesmo tempo, o ranking exibia no
painel, como etiqueta, os mecanismos que cada empresa "usa": Rouanet, FIA, LIE.
Eram hipóteses de conhecimento público, e o próprio ranking as chamava assim.
O painel não. Quem olhava a etiqueta lia fato.

O QUE ESTA ROTINA FAZ

Lê três extratos oficiais gravados em `dados/empresas/destinacoes/fontes/`,
todos obtidos pelo navegador local do titular em 26/09/2026:

  • Rouanet — SALIC (MinC): total histórico por CNPJ na API nova e cada doação,
    com projeto, valor e data, no SalicComparar do próprio ministério;
  • Goyazes — Secult-GO: créditos de ICMS concedidos por empresa, 2024 a 2026;
  • PAT — MTE: relação das empresas beneficiárias até 31/03/2026.

E registra, mecanismo por mecanismo, o que as fontes permitem afirmar — e o que
não permitem. LIE está sob defeso eleitoral: a página oficial responde "Conteúdo
restrito" até o fim do período. FIA, Fundo do Idoso, PRONON e PRONAS não têm
lista pública de doadores por CNPJ: a doação aparece na declaração da empresa e
na prestação de contas do conselho ou da instituição, e nenhuma das duas é
aberta. Esses campos saem nulos, com o motivo e o caminho para obter o dado.

TRÊS REGRAS QUE ESTA ROTINA NÃO NEGOCIA

1. Nada inventado. Valor, ano e CNPJ só com fonte oficial; sem fonte, nulo.
2. Nome não é CNPJ. A empresa sem CNPJ na base só ganha um quando o órgão
   oficial devolve a razão social correspondente — e a resolução fica registrada.
3. Inscrição no PAT não prova Lucro Real. Doação à Rouanet prova: só a pessoa
   jurídica tributada pelo lucro real pode deduzi-la (Lei 8.313/1991, art. 26).
"""
from __future__ import annotations

import json
import re
import unicodedata
from collections import defaultdict
from datetime import date
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json

FONTES = ROOT / "dados/empresas/destinacoes/fontes"
ROUANET = FONTES / "rouanet_salic_2026-09-26.json"
GOYAZES = FONTES / "goyazes_creditos_2024-2026.json"
PAT = FONTES / "pat_recorte_2026-03-31.json"
SAIDA = ROOT / "biblioteca_alexandria/empresas/incentivos_verificados.json"
SAIDA_PAINEL = ROOT / "docs/dados/incentivos_verificados.json"

REFERENCIA = "2026-09-26"
ANOS_HISTORICO = 5  # regra do titular (config/empresas.json → historico_anos)

# ── O que cada mecanismo permite afirmar hoje, e por onde se chega ao dado ──
MECANISMOS = {
    "Rouanet": {
        "status": "lido",
        "fonte": "SALIC — Ministério da Cultura",
        "url": "https://aplicacoes.cultura.gov.br/comparar/control_IncentivadoresSeusProponente/",
        "prova_lucro_real": True,
        "nota": "total histórico pela API nova do SALIC e cada doação pelo SalicComparar, ambos do MinC",
    },
    "Goyazes": {
        "status": "lido",
        "fonte": "Secretaria de Estado da Cultura de Goiás",
        "url": "https://goias.gov.br/cultura/programa-goyazes/",
        "prova_lucro_real": False,
        "nota": ("créditos de ICMS concedidos por empresa, 2024, 2025 e 2026; a planilha traz o nome da "
                 "empresa, não o CNPJ, e o valor é o do projeto aprovado"),
    },
    "PAT": {
        "status": "lido",
        "fonte": "Ministério do Trabalho e Emprego — dados.gov.br",
        "url": "https://dados.gov.br/dados/conjuntos-dados/programa-de-alimentacao-do-trabalhador-pat",
        "prova_lucro_real": False,
        "nota": ("inscrição no PAT até 31/03/2026; é indício de regime tributário, não prova — a dedução "
                 "no IRPJ só existe no Lucro Real, mas a inscrição não exige Lucro Real"),
    },
    "LIE": {
        "status": "bloqueado_defeso_eleitoral",
        "fonte": "Ministério do Esporte",
        "url": "https://www.gov.br/esporte/pt-br/acoes-e-programas/lei-de-incentivo-ao-esporte",
        "retomar_em": "2026-10-26",
        "prova_lucro_real": True,
        "nota": ("a página da Lei de Incentivo ao Esporte respondeu HTTP 401 'Conteúdo restrito' em 26/09/2026; "
                 "o ministério declara defeso de 02/07/2026 até o pleito (04/10) e, havendo segundo turno, até "
                 "25/10/2026. Consultar de novo a partir de 26/10/2026"),
    },
    "FIA": {
        "status": "sem_fonte_publica_por_cnpj",
        "fonte": None,
        "prova_lucro_real": True,
        "caminho": ("pedido de acesso à informação (Lei 12.527/2011) ao CMDCA de Goiânia e ao CEDCA-GO pedindo a "
                    "relação de doadores pessoa jurídica ao fundo por exercício; o conselho a tem porque emite o recibo"),
        "nota": "a doação ao Fundo da Infância e Adolescência não tem lista nacional aberta por doador",
    },
    "Fundo do Idoso": {
        "status": "sem_fonte_publica_por_cnpj",
        "fonte": None,
        "prova_lucro_real": True,
        "caminho": "pedido de acesso à informação ao Conselho Municipal e ao Conselho Estadual da Pessoa Idosa",
        "nota": "mesma situação do FIA: o recibo é emitido pelo conselho e não há lista pública por doador",
    },
    "PRONON": {
        "status": "sem_fonte_publica_por_cnpj",
        "fonte": None,
        "prova_lucro_real": True,
        "caminho": ("a instituição credenciada que recebeu a doação é quem tem o doador; pedir na prestação de "
                    "contas dela ou ao Ministério da Saúde por acesso à informação"),
        "nota": "o Ministério da Saúde publica projetos aprovados, não doadores",
    },
    "PRONAS/PCD": {
        "status": "sem_fonte_publica_por_cnpj",
        "fonte": None,
        "prova_lucro_real": True,
        "caminho": "idem PRONON",
        "nota": "o Ministério da Saúde publica projetos aprovados, não doadores",
    },
}

# ── CNPJ que a base trazia errado, com a prova de cada correção ──
CORRECOES_CNPJ = {
    "Vale": {"errado": "53400818000168", "correto": "33592510000154",
             "prova": "o CNPJ da base é da FERTIGRAN FERTILIZANTES VALE DO RIO GRANDE (SALIC e PAT); o SALIC devolve VALE S.A. para 33592510000154"},
    "Stone": {"errado": "57497539000115", "correto": "16501555000157",
              "prova": "o CNPJ da base é da BRIDGESTONE (SALIC e PAT); o SALIC devolve STONE PAGAMENTOS S.A. para 16501555000157"},
    "Fleury": {"errado": "37639630000110", "correto": "60840055000131",
               "prova": "o CNPJ da base não aparece no SALIC nem no PAT; o SALIC devolve Fleury S/A para 60840055000131 e o PAT, FLEURY SA"},
    "Nestlé": {"errado": "08334818000152", "correto": "60409075000152",
               "prova": "o CNPJ da base é da Nestlé Nordeste Alimentos e Bebidas, subsidiária; a matriz é NESTLE BRASIL LTDA., 60409075000152 no SALIC"},
}

# ── Nome sem CNPJ na base → CNPJ, só quando a fonte oficial devolveu a razão social ──
RESOLUCAO_POR_NOME = {
    "Alcoa": ("23637697000101", "SALIC: ALCOA Alumínio S.A."),
    "Arcelor Mittal": ("17469701000177", "SALIC: ARCELORMITTAL BRASIL S.A."),
    "Banco do Brasil": ("00000000000191", "SALIC: BANCO DO BRASIL SA"),
    "Bradesco": ("60746948000112", "SALIC: BANCO BRADESCO S.A."),
    "Braskem": ("42150391000170", "SALIC: Braskem S.A"),
    "Caixa Econômica Federal": ("00360305000104", "SALIC: CAIXA ECONOMICA FEDERAL"),
    "Caixa": ("00360305000104", "SALIC: CAIXA ECONOMICA FEDERAL"),
    "Correios": ("34028316000103", "SALIC: EMPRESA BRASILEIRA DE CORREIOS E TELEGRAFOS"),
    "Dasa": ("61486650000183", "SALIC: DIAGNOSTICOS DA AMERICA S.A."),
    "Eletrobras": ("00001180000126", "SALIC: CENTRAIS ELETRICAS BRASILEIRAS SA ELETROBRAS (matriz)"),
    "Hapvida": ("63554067000198", "SALIC: Hapvida Assistência Médica Ltda."),
    "Itaú Unibanco": ("60701190000104", "SALIC: ITAU UNIBANCO S.A."),
    "Itaú": ("60701190000104", "SALIC: ITAU UNIBANCO S.A."),
    "Localiza": ("16670085000155", "SALIC: LOCALIZA RENT A CAR SA"),
    "Marisa": ("61189288000189", "SALIC: Marisa Lojas Varejista Ltda"),
    "Sabin": ("00718528000109", "SALIC: Laboratório Sabin Análises Clínicas Ltda."),
    "Santander": ("90400888000142", "SALIC: BANCO SANTANDER (BRASIL) S.A."),
    "Saneago": ("01616929000102", "SALIC: Saneamento de Goiás S/A SANEAGO"),
    "Frigorífico Minerva": ("67620377000114", "SALIC: MINERVA S.A."),
    "Unimed Goiânia": ("02476067000122", "SALIC: Unimed Goiânia - Cooperativa de Trabalho Médico"),
    "TV Anhanguera": ("01534510000101", "SALIC: TELEVISAO ANHANGUERA S/A"),
    "Hospital Israelita Albert Einstein": ("60765823000130", "SALIC: SOCIEDADE BENEF ISRAELITA BRAS HOSPITAL ALBERT EINSTEIN"),
    "Drogasil / RD Saúde": ("61585865000151", "SALIC e PAT: RAIA DROGASIL S/A"),
    "Grupo Petrópolis": ("73410326000160", "PAT: CERVEJARIA PETROPOLIS S/A"),
    "Assaí": ("06057223000171", "SALIC e PAT: SENDAS DISTRIBUIDORA S/A"),
    "Assaí Atacadista": ("06057223000171", "SALIC e PAT: SENDAS DISTRIBUIDORA S/A"),
    "Supermercados Carrefour": ("45543915000181", "SALIC e PAT: CARREFOUR COMERCIO E INDUSTRIA LTDA"),
    "Grupo Big / Atacadão": ("75315333000109", "SALIC: ATACADAO S.A."),
    "Telefônica Vivo": ("02558157000162", "SALIC: TELEFONICA BRASIL S.A."),
    "Vivo": ("02558157000162", "SALIC: TELEFONICA BRASIL S.A."),
    "Equatorial Energia": ("01543032000104", "Goyazes: EQUATORIAL ENERGIA GOIÁS / EQUATORIAL GOIÁS DISTRIBUIDORA DE ENERGIA S.A."),
    "Cooperativa Comigo": ("02077618000185", "PAT: COMIGO-COOP.AGROIND.DOS PROD.RURAIS DO SUDOESTE GOIANO"),
    "Cervejaria Ambev Goiás": ("07526557000100", "mesma pessoa jurídica: AMBEV S.A. (SALIC e PAT)"),
}

# ── Marca de grupo, ou marca que só casa com a pessoa jurídica por conhecimento externo ──
SEM_CNPJ_UNICO = {
    "BTG Pactual": "grupo: o SALIC traz 17 pessoas jurídicas BTG, nenhuma é a matriz única do grupo",
    "Sicoob": "sistema de cooperativas: cada singular tem CNPJ próprio",
    "Sicredi": "sistema de cooperativas: cada singular tem CNPJ próprio",
    "Unimed": "sistema de cooperativas: cada singular tem CNPJ próprio (a de Goiânia está resolvida à parte)",
    "Coca-Cola Brasil": "a marca não é a pessoa jurídica que produz; o SALIC não devolveu a matriz",
    "Coca-Cola": "idem Coca-Cola Brasil",
    "Coca-Cola Femsa": "no Brasil opera como SPAL Indústria Brasileira de Bebidas — a confirmar antes de atribuir o CNPJ",
    "Heineken": "no Brasil opera como HNK BR Indústria de Bebidas (50221019000136, já na base) — a confirmar antes de fundir",
    "Grupo Boticário": "o SALIC devolve O Boticário Franchising S.A.; outras empresas do grupo têm CNPJ próprio — a confirmar",
    "Grupo Mateus": "o SALIC não devolveu registro para o nome",
    "Nubank": "o SALIC não devolveu registro para o nome",
    "Rede D'Or": "o SALIC não devolveu registro para o nome",
    "CCR": "o SALIC não devolveu registro para o nome",
    "Grupo Bretas / Cencosud": "o SALIC não devolveu registro para o nome",
    "Grupo Jaime Câmara": "grupo de comunicação; a TV Anhanguera, do grupo, está resolvida à parte",
    "Faculdade Estácio Goiás": "grupo educacional: o SALIC traz 33 pessoas jurídicas Estácio",
}

# ── Entidades que não apuram IRPJ pelo Lucro Real: incentivo fiscal não se aplica ──
ISENTAS = {
    "Sebrae Goiás": "serviço social autônomo",
    "Sesc Goiás": "serviço social autônomo",
    "Fieg / Sesi / Senai Goiás": "federação sindical e serviços sociais autônomos",
    "Fecomércio Goiás": "federação sindical",
    "PUC Goiás": "instituição de ensino sem fins lucrativos",
}

# ── Registros que não são empresa: erro de leitura de fonte ──
DESCARTES = {
    "de janeiro de 2026": ("fragmento de data lido como nome na posição 28 da lista de maiores contribuintes do ICMS "
                           "de 2026; a empresa real dessa posição não foi identificada"),
    "WhatsApp Agenda Grupo": "trecho de notícia do Jornal Opção lido como nome de patrocinador pelo motor de patrocínio",
    "Diário de Goiás Comunicação LTDA": ("o veículo que publicou a notícia foi gravado como patrocinador do evento; "
                                         "portal de notícia é fonte de descoberta, nunca o patrocinador"),
}

# ── Grafias da planilha do Goyazes que são a mesma empresa da base ──
ALIAS_GOYAZES = {
    "02089969000106": ["LATICINIOS BELA VISTA", "LATICINIO BELA VISTA", "LATICIONIO BELA VISTA"],
    "01543032000104": ["EQUATORIAL ENERGIA GOIAS", "EQUATORIAL GOIAS DISTRIBUIDORA ENERGIA"],
    "00080671000100": ["CARAMURU ALIMENTOS"],
    "02421421000111": ["TIM"],
    "03380763000101": ["REFRESCOS BANDEIRANTES"],
}

_SUFIXOS = re.compile(r"\b(LTDA|SA|S A|EIRELI|EIRELLI|ME|EPP|CIA|COMPANHIA|DE|DO|DA|DOS|DAS|E|INDUSTRIA|COMERCIO|IND|COM|"
                      r"IMPORTACAO|EXPORTACAO|IMPORTACOES|FILIAL)\b")


def normalizar_nome(nome: str) -> str:
    """Nome de empresa comparável: sem acento, sem pontuação, sem forma societária."""
    s = unicodedata.normalize("NFKD", nome or "").encode("ascii", "ignore").decode().upper()
    s = s.replace("S/A", " SA ").replace("S.A.", " SA ").replace("S.A", " SA ")
    s = re.sub(r"[^A-Z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", _SUFIXOS.sub(" ", s)).strip()


def so_digitos(valor) -> str:
    return re.sub(r"\D", "", str(valor or ""))


def _carregar(caminho: Path) -> dict:
    return load_json(caminho) if caminho.exists() else {}


def _corte() -> int:
    return date.fromisoformat(REFERENCIA).year - ANOS_HISTORICO


# ───────────────────────── leitura de cada mecanismo ─────────────────────────
def rouanet_de(cnpj: str, base: dict | None = None) -> dict:
    """O que o SALIC diz de um CNPJ: destinou, não consta, ou não foi lido."""
    base = base if base is not None else _carregar(ROUANET)
    reg = (base.get("empresas") or {}).get(so_digitos(cnpj))
    if reg is None:
        return {"status": "nao_lido", "motivo": "CNPJ fora do lote lido em 26/09/2026"}
    if reg.get("api_status") == 404 and not reg.get("doacoes"):
        return {"status": "nao_consta", "fonte": "SALIC/MinC",
                "motivo": "o SALIC não tem este CNPJ como incentivador da Lei Rouanet"}
    doacoes = reg.get("doacoes") or []
    por_ano: dict = defaultdict(lambda: {"doacoes": 0, "valor": 0.0})
    for data_iso, _pronac, valor, _prop, _proj in doacoes:
        ano = (data_iso or "")[:4] or "sem data"
        por_ano[ano]["doacoes"] += 1
        por_ano[ano]["valor"] = round(por_ano[ano]["valor"] + valor, 2)
    anos = sorted(a for a in por_ano if a.isdigit())
    recentes = [d for d in doacoes if (d[0] or "0")[:4].isdigit() and int(d[0][:4]) >= _corte()]
    total_grid = round(sum(d[2] for d in doacoes), 2)
    total_api = ((reg.get("api") or {}).get("total_doado"))
    saida = {
        "status": "destinou" if doacoes or total_api else "nao_consta",
        "fonte": "SALIC/MinC",
        "razao_social_salic": ((reg.get("api") or {}).get("nome") or "").strip() or None,
        "total_historico_api": round(total_api, 2) if total_api else None,
        "total_historico_doacoes": total_grid if doacoes else None,
        "doacoes_registradas": len(doacoes),
        "primeiro_ano": anos[0] if anos else None,
        "ultimo_ano": anos[-1] if anos else None,
        "por_ano": {a: dict(v) for a, v in sorted(por_ano.items())},
        "ultimos_5_anos": {
            "desde": _corte(),
            "doacoes": len(recentes),
            "valor": round(sum(d[2] for d in recentes), 2),
            "anos": sorted({d[0][:4] for d in recentes}),
        },
        "doacoes_5_anos": [{"data": d[0], "pronac": d[1], "valor": d[2], "proponente": d[3] or None, "projeto": d[4]} for d in recentes],
        "lido_em": reg.get("lido_em"),
    }
    if total_api and doacoes and abs(total_grid - total_api) / total_api > 0.02:
        saida["divergencia"] = (f"as duas bases do MinC divergem: API R$ {total_api:,.2f} e relatório por doação "
                                f"R$ {total_grid:,.2f}. As duas ficam registradas; nenhuma é descartada").replace(",", "X").replace(".", ",").replace("X", ".")
    return saida


def _indice_goyazes(base: dict | None = None) -> dict:
    base = base if base is not None else _carregar(GOYAZES)
    indice: dict = defaultdict(list)
    for linha in base.get("linhas") or []:
        partes = [p for p in re.split(r"\s+/\s+|\s*;\s*|\n", linha.get("empresa") or "") if p.strip()]
        for p in partes:
            indice[normalizar_nome(p)].append({**linha, "empresa_na_planilha": p.strip(),
                                               "empresas_no_projeto": max(len(partes), linha.get("empresas_no_grupo") or 1)})
    return indice


def goyazes_de(cnpj: str, nomes: list[str], indice: dict | None = None) -> dict:
    """Linhas do Goyazes atribuídas a esta empresa — por grafia conhecida ou nome exato."""
    indice = indice if indice is not None else _indice_goyazes()
    chaves = set(ALIAS_GOYAZES.get(so_digitos(cnpj), []))
    chaves |= {normalizar_nome(n) for n in nomes if n and len(normalizar_nome(n)) >= 4}
    linhas = [l for k in chaves for l in indice.get(k, [])]
    if not linhas:
        return {"status": "nao_consta_2024_2026", "fonte": "Secult-GO",
                "motivo": "o nome da empresa não aparece nas planilhas de créditos concedidos de 2024, 2025 e 2026"}
    por_ano: dict = defaultdict(lambda: {"projetos": 0, "valor_projetos": 0.0})
    for l in linhas:
        por_ano[str(l["ano"])]["projetos"] += 1
        por_ano[str(l["ano"])]["valor_projetos"] = round(por_ano[str(l["ano"])]["valor_projetos"] + (l.get("valor") or 0), 2)
    return {
        "status": "destinou", "fonte": "Secult-GO",
        "grafias_na_planilha": sorted({l["empresa_na_planilha"] for l in linhas}),
        "por_ano": dict(sorted(por_ano.items())),
        "projetos": [{"ano": l["ano"], "projeto": l["projeto"], "proponente": l["proponente"], "cidades": l["cidades"],
                      "valor_projeto": l.get("valor"), "empresas_no_projeto": l["empresas_no_projeto"], "fonte": l["fonte"],
                      **({"valor_projeto_compartilhado": l["valor_projeto_compartilhado"]} if l.get("linha_de_continuacao") else {})}
                     for l in sorted(linhas, key=lambda x: (x["ano"], x["projeto"]))],
        "nota": "valor do projeto aprovado; com mais de uma empresa no projeto, não é a cota individual",
    }


def pat_de(cnpj: str, base: dict | None = None) -> dict:
    base = base if base is not None else _carregar(PAT)
    reg = (base.get("empresas") or {}).get(so_digitos(cnpj))
    if reg is None:
        return {"status": "nao_lido", "motivo": "CNPJ fora do lote lido em 26/09/2026"}
    exato = reg.get("cnpj_exato")
    if exato and exato.get("situacao") == "Ativo":
        status = "inscrita"
    elif reg.get("estabelecimentos_ativos"):
        status = "inscrita_por_estabelecimento"
    elif reg.get("estabelecimentos_inativos"):
        status = "inscricao_inativa"
    else:
        status = "nao_consta"
    return {"status": status, "fonte": "MTE — relação de beneficiárias do PAT até 31/03/2026",
            "estabelecimentos_ativos": reg.get("estabelecimentos_ativos"), "estabelecimentos_inativos": reg.get("estabelecimentos_inativos"),
            "trabalhadores_atendidos": reg.get("trabalhadores_ativos"), "cnpj_exato": exato,
            "leitura": "indício de regime tributário, não prova de Lucro Real"}


def lucro_real_pela_rouanet(rouanet: dict) -> dict | None:
    """Doação à Rouanet desde o corte = Lucro Real confirmado naquele exercício."""
    anos = (rouanet.get("ultimos_5_anos") or {}).get("anos") or []
    if rouanet.get("status") == "destinou" and anos:
        return {"classe": "confirmado",
                "motivo": (f"destinou pela Lei Rouanet em {', '.join(anos)} — só a pessoa jurídica tributada pelo lucro "
                           "real pode deduzir (Lei 8.313/1991, art. 26)"),
                "fonte": "SALIC/MinC", "exercicios": anos}
    return None


# ───────────────────────── a ficha de uma empresa ─────────────────────────
def ficha(nome: str, cnpj: str | None, bases: dict | None = None) -> dict:
    """Todos os mecanismos para uma empresa, com status explícito em cada um."""
    b = bases or carregar_bases()
    cnpj_original = so_digitos(cnpj)
    correcao = CORRECOES_CNPJ.get(nome)
    resolucao = None
    if correcao and cnpj_original in ("", correcao["errado"]):
        cnpj_final = correcao["correto"]
    elif not cnpj_original and nome in RESOLUCAO_POR_NOME:
        cnpj_final, prova = RESOLUCAO_POR_NOME[nome]
        resolucao = {"cnpj": cnpj_final, "prova": prova}
    else:
        cnpj_final = cnpj_original
    # o ranking regerado já traz o CNPJ resolvido; a prova da resolução continua na ficha
    if not resolucao and nome in RESOLUCAO_POR_NOME and RESOLUCAO_POR_NOME[nome][0] == cnpj_final:
        resolucao = {"cnpj": cnpj_final, "prova": RESOLUCAO_POR_NOME[nome][1]}

    saida = {"nome": nome, "cnpj": cnpj_final or None, "verificado_em": REFERENCIA}
    if correcao and cnpj_final == correcao["correto"]:
        saida["cnpj_corrigido"] = correcao
    if resolucao:
        saida["cnpj_resolvido_por_nome"] = resolucao
    if nome in DESCARTES:
        return {**saida, "descartar": True, "motivo": DESCARTES[nome]}
    if nome in ISENTAS:
        saida["incentivo_fiscal"] = {"aplica": False, "motivo": f"{ISENTAS[nome]}: não apura IRPJ pelo Lucro Real; "
                                                                "patrocínio só com verba própria"}

    mec = {}
    if cnpj_final:
        mec["Rouanet"] = rouanet_de(cnpj_final, b["rouanet"])
        mec["PAT"] = pat_de(cnpj_final, b["pat"])
        nomes = [nome, mec["Rouanet"].get("razao_social_salic") or ""]
        exato = (mec["PAT"].get("cnpj_exato") or {})
        nomes.append(exato.get("razao_social") or "")
        mec["Goyazes"] = goyazes_de(cnpj_final, nomes, b["goyazes"])
    else:
        motivo = SEM_CNPJ_UNICO.get(nome, "sem CNPJ identificado em fonte oficial")
        mec["Rouanet"] = {"status": "sem_cnpj", "motivo": motivo}
        mec["PAT"] = {"status": "sem_cnpj", "motivo": motivo}
        mec["Goyazes"] = goyazes_de("", [nome], b["goyazes"])
    for m in ("LIE", "FIA", "Fundo do Idoso", "PRONON", "PRONAS/PCD"):
        info = MECANISMOS[m]
        mec[m] = {"status": info["status"], "valor": None, "motivo": info["nota"],
                  **({"retomar_em": info["retomar_em"]} if info.get("retomar_em") else {}),
                  **({"caminho": info["caminho"]} if info.get("caminho") else {})}
    saida["mecanismos"] = mec
    # "confirmados": destinou em algum momento, segundo a fonte oficial.
    # "confirmados_5_anos": destinou dentro da janela do titular — é o que o painel mostra
    # como etiqueta, para que doação de 2009 não pareça relação viva com a empresa.
    saida["confirmados"] = sorted(m for m, v in mec.items() if v.get("status") == "destinou")
    recentes = []
    if (mec["Rouanet"].get("ultimos_5_anos") or {}).get("anos"):
        recentes.append("Rouanet")
    if any(int(a) >= _corte() for a in (mec["Goyazes"].get("por_ano") or {})):
        recentes.append("Goyazes")
    saida["confirmados_5_anos"] = sorted(recentes)
    lucro = lucro_real_pela_rouanet(mec["Rouanet"])
    if lucro:
        saida["lucro_real"] = lucro
    if nome in SEM_CNPJ_UNICO:
        saida["observacao"] = SEM_CNPJ_UNICO[nome]
    return saida


def carregar_bases() -> dict:
    return {"rouanet": _carregar(ROUANET), "pat": _carregar(PAT), "goyazes": _indice_goyazes()}


# ───────────────────────── aplicação na biblioteca ─────────────────────────
def destinacoes_para_historico(f: dict) -> list[dict]:
    """Formato de `destinacoes_5_anos` que o motor de empresas já lê."""
    hist = []
    rou = (f.get("mecanismos") or {}).get("Rouanet") or {}
    for d in rou.get("doacoes_5_anos") or []:
        hist.append({"programa": "Lei Rouanet", "ano": d["data"][:4] if d.get("data") else None, "data": d.get("data"),
                     "projeto": d["projeto"], "pronac": d["pronac"], "valor": d["valor"], "proponente": d.get("proponente"),
                     "fonte": "SALIC/MinC", "url": MECANISMOS["Rouanet"]["url"]})
    goy = (f.get("mecanismos") or {}).get("Goyazes") or {}
    for p in goy.get("projetos") or []:
        if p["ano"] >= _corte():
            hist.append({"programa": "Goyazes", "ano": str(p["ano"]), "projeto": p["projeto"], "valor": p.get("valor_projeto"),
                         "valor_e_do_projeto": True, "empresas_no_projeto": p["empresas_no_projeto"],
                         "proponente": p["proponente"], "fonte": "Secult-GO", "url": p["fonte"]})
    return sorted(hist, key=lambda h: (h.get("ano") or "", h.get("programa")))


def aplicar_em_painel(painel: dict, bases: dict | None = None) -> dict:
    """go.json: preenche destinacoes_5_anos, lucro_real e a ficha verificada de cada empresa."""
    b = bases or carregar_bases()
    mantidas = []
    for e in painel.get("empresas") or []:
        f = ficha(e.get("nome") or "", e.get("cnpj"), b)
        if f.get("descartar"):
            continue
        e["incentivos_verificados"] = resumo_da_ficha(f)
        hist = destinacoes_para_historico(f)
        if hist:
            e["destinacoes_5_anos"] = hist
        if f.get("lucro_real") and (e.get("lucro_real") or {}).get("classe") != "confirmado":
            e["lucro_real"] = f["lucro_real"]
        pot = e.get("potencial_destinacao") or {}
        if "Rouanet" in f["confirmados"] and (f["mecanismos"]["Rouanet"]["ultimos_5_anos"]["anos"]):
            pot["cultura"] = "ja_destina"
        if "Goyazes" in f["confirmados"]:
            pot["cultura_icms_goias"] = "ja_destina"
        e["potencial_destinacao"] = pot
        mantidas.append(e)
    painel["descartadas_na_verificacao"] = len(painel.get("empresas") or []) - len(mantidas)
    painel["empresas"] = mantidas
    painel["total"] = len(mantidas)
    painel["incentivos_verificados_em"] = REFERENCIA
    return painel


_LINHA_HIPOTESE = re.compile(r"^(\d+): usa \d+ mecanismo")
# linhas que esta rotina acrescenta — retiradas antes de recalcular, para que rodar
# duas vezes não some os mesmos pontos duas vezes
_LINHA_VERIFICADA = re.compile(r"^(\d+): (destinou pela Lei Rouanet|destinou ICMS pelo Programa Goyazes|inscrita no PAT)")


def aplicar_em_ranking(itens: list[dict], categoria: str, bases: dict | None = None) -> list[dict]:
    """Ranking: CNPJ corrigido, mecanismos verificados no lugar das hipóteses, registros falsos fora."""
    b = bases or carregar_bases()
    saida = []
    for item in itens:
        f = ficha(item.get("nome") or "", item.get("cnpj"), b)
        if f.get("descartar"):
            continue
        novo = dict(item)
        if f.get("cnpj") and f.get("cnpj") != so_digitos(item.get("cnpj")):
            novo["cnpj"] = cnpj_fmt(f["cnpj"])
        pontos = int(novo.get("pontos") or 0)
        por = []
        for linha in novo.get("por") or []:
            m = _LINHA_HIPOTESE.match(linha) or _LINHA_VERIFICADA.match(linha)
            if m:
                pontos -= int(m.group(1))
                continue
            por.append(linha)
        mec = f.get("mecanismos") or {}
        rou = mec.get("Rouanet") or {}
        anos_rou = (rou.get("ultimos_5_anos") or {}).get("anos") or []
        if categoria == "destinacao_tributaria":
            if anos_rou:
                v = min(20, 8 + 3 * len(anos_rou))
                pontos += v
                por.append(f"{v}: destinou pela Lei Rouanet em {len(anos_rou)} ano(s) desde {_corte()} — {', '.join(anos_rou)} (SALIC/MinC)")
            if (mec.get("Goyazes") or {}).get("status") == "destinou":
                pontos += 25
                anos_g = ", ".join(sorted((mec["Goyazes"].get("por_ano") or {}).keys()))
                por.append(f"25: destinou ICMS pelo Programa Goyazes em Goiás ({anos_g}) — o incentivo ao alcance de uma OSC de Goiânia (Secult-GO)")
            if (mec.get("PAT") or {}).get("status") in ("inscrita", "inscrita_por_estabelecimento"):
                pontos += 2
                por.append("2: inscrita no PAT (MTE) — indício de regime tributário, não prova")
        novo["pontos"] = max(0, min(100, pontos))
        novo["por"] = por
        novo["incentivos_hipotese"] = item.get("incentivos_hipotese", item.get("incentivos"))
        novo["incentivos"] = f.get("confirmados_5_anos") or None
        novo["incentivos_historico"] = f.get("confirmados") or None
        novo["incentivos_verificados"] = resumo_da_ficha(f)
        if f.get("lucro_real"):
            novo["condicao"] = "Lucro Real confirmado pela Rouanet recente; confirmar imposto devido no exercício antes de propor"
        saida.append(novo)
    saida.sort(key=lambda x: (-x["pontos"], x["nome"]))
    # a mesma pessoa jurídica aparecia duas vezes — por marca ("Telefônica Vivo") e pela
    # razão social da lista do ICMS ("TELEFONICA BRASIL S.A."). Com o CNPJ resolvido, as
    # duas viram uma: fica a de maior pontuação, e o outro nome é guardado.
    unicas, por_cnpj = [], {}
    for x in saida:
        c = so_digitos(x.get("cnpj"))
        if c and c in por_cnpj:
            por_cnpj[c].setdefault("tambem_listada_como", []).append(x["nome"])
            # quem absorve uma empresa da lista de conhecidas herda o lugar garantido dela
            if x.get("origem_lista") == "conhecida":
                por_cnpj[c]["origem_lista"] = "conhecida"
            continue
        if c:
            por_cnpj[c] = x
        unicas.append(x)
    for i, x in enumerate(unicas, 1):
        x["posicao"] = i
    return unicas


def resumo_da_ficha(f: dict) -> dict:
    """O que o ranking e o painel precisam — o detalhe doação a doação fica na
    base verificada (biblioteca_alexandria/empresas/incentivos_verificados.json),
    para que o arquivo do painel não carregue milhares de linhas por empresa."""
    mec = f.get("mecanismos") or {}
    resumo = {}
    for m, v in mec.items():
        item = {"status": v.get("status")}
        if m == "Rouanet" and v.get("status") == "destinou":
            item.update({"total_historico_api": v.get("total_historico_api"), "ultimo_ano": v.get("ultimo_ano"),
                         "ultimos_5_anos": v.get("ultimos_5_anos"), "fonte": v.get("fonte")})
        elif m == "Goyazes" and v.get("status") == "destinou":
            item.update({"por_ano": v.get("por_ano"), "fonte": v.get("fonte"), "nota": v.get("nota")})
        elif m == "PAT" and v.get("status") not in ("sem_cnpj", "nao_lido"):
            item.update({"estabelecimentos_ativos": v.get("estabelecimentos_ativos"), "leitura": v.get("leitura")})
        elif v.get("motivo"):
            item["motivo"] = v["motivo"]
            for k in ("retomar_em", "caminho"):
                if v.get(k):
                    item[k] = v[k]
        resumo[m] = item
    saida = {k: f[k] for k in ("cnpj", "verificado_em", "confirmados", "confirmados_5_anos", "lucro_real",
                               "cnpj_corrigido", "cnpj_resolvido_por_nome", "incentivo_fiscal", "observacao") if f.get(k)}
    saida["mecanismos"] = resumo
    saida["detalhe"] = "biblioteca_alexandria/empresas/incentivos_verificados.json"
    return saida


def cnpj_fmt(c: str) -> str:
    d = so_digitos(c)
    return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}" if len(d) == 14 else c


def descobertas_goyazes(conhecidos: set[str], bases: dict | None = None) -> list[dict]:
    """Empresas que destinaram ICMS pelo Goyazes e ainda não estão na biblioteca."""
    b = bases or carregar_bases()
    ja = set(conhecidos)
    for grafias in ALIAS_GOYAZES.values():
        ja |= set(grafias)
    # a mesma empresa vem grafada de jeitos diferentes de um ano para outro (COMPLEM em
    # cinco versões, "CENTROESTE"/"CENTROOESTE", "CLINIA"/"CLINICA"). Sem CNPJ na
    # planilha, agrupa-se por semelhança forte de nome — e o grupo fica marcado para
    # confirmação pelo CNPJ, nunca tratado como certeza.
    from difflib import SequenceMatcher
    grupos: list[list[str]] = []
    for chave in sorted(k for k in b["goyazes"] if k and k not in ja):
        for g in grupos:
            ref = g[0]
            curto, longo = sorted((ref, chave), key=len)
            if (SequenceMatcher(None, ref, chave).ratio() >= 0.88
                    or (len(curto.split()) >= 2 and longo.startswith(curto))):
                g.append(chave)
                break
        else:
            grupos.append([chave])
    saida = []
    for grupo in grupos:
        chave = grupo[0]
        linhas = [l for k in grupo for l in b["goyazes"][k]]
        por_ano: dict = defaultdict(lambda: {"projetos": 0, "valor_projetos": 0.0})
        for l in linhas:
            por_ano[str(l["ano"])]["projetos"] += 1
            por_ano[str(l["ano"])]["valor_projetos"] = round(por_ano[str(l["ano"])]["valor_projetos"] + (l.get("valor") or 0), 2)
        saida.append({"nome": sorted({l["empresa_na_planilha"] for l in linhas})[0], "chave": chave, "cnpj": None,
                      **({"agrupado_por_semelhanca_de_nome": grupo} if len(grupo) > 1 else {}),
                      "grafias": sorted({l["empresa_na_planilha"] for l in linhas}), "por_ano": dict(sorted(por_ano.items())),
                      "projetos": len(linhas), "valor_projetos": round(sum(l.get("valor") or 0 for l in linhas), 2),
                      "cidades": sorted({c.strip() for l in linhas for c in re.split(r"[,;]", l.get("cidades") or "") if c.strip()})[:12],
                      "fonte": "Secult-GO — créditos concedidos por empresa",
                      "proximo_passo": "obter o CNPJ no cadastro da Receita e incluir no motor de empresas de Goiás"})
    return sorted(saida, key=lambda x: (-x["valor_projetos"], x["nome"]))


# ───────────────────────── execução ─────────────────────────
def _todas_as_empresas() -> list[tuple[str, str | None]]:
    vistos, lista = set(), []
    painel = _carregar(ROOT / "biblioteca_alexandria/empresas/go/go.json")
    for e in painel.get("empresas") or []:
        chave = (e.get("nome"), so_digitos(e.get("cnpj")))
        if chave not in vistos:
            vistos.add(chave); lista.append((e.get("nome"), e.get("cnpj")))
    for cat in ("destinacao_tributaria", "patrocinio_privado"):
        for e in (_carregar(ROOT / f"biblioteca_alexandria/empresas/ranking_{cat}.json").get("empresas") or []):
            chave = (e.get("nome"), so_digitos(e.get("cnpj")))
            if chave not in vistos:
                vistos.add(chave); lista.append((e.get("nome"), e.get("cnpj")))
    return lista


def run() -> dict:
    b = carregar_bases()
    fichas = [ficha(n, c, b) for n, c in _todas_as_empresas()]
    validas = [f for f in fichas if not f.get("descartar")]
    por_cnpj = {}
    for f in validas:
        if f.get("cnpj"):
            por_cnpj.setdefault(f["cnpj"], f)
    conhecidos = {normalizar_nome(f["nome"]) for f in validas}
    for f in por_cnpj.values():
        rs = (f["mecanismos"].get("Rouanet") or {}).get("razao_social_salic")
        if rs:
            conhecidos.add(normalizar_nome(rs))
    novas = descobertas_goyazes(conhecidos, b)

    def conta(m, st):
        return sum(1 for f in por_cnpj.values() if (f["mecanismos"].get(m) or {}).get("status") == st)

    resumo = {
        "referencia": REFERENCIA,
        "registros_na_biblioteca": len(fichas),
        "descartados": [{"nome": f["nome"], "motivo": f["motivo"]} for f in fichas if f.get("descartar")],
        "empresas_com_cnpj": len(por_cnpj),
        "sem_cnpj_unico": sorted({f["nome"] for f in validas if not f.get("cnpj")}),
        "cnpj_corrigidos": [{"nome": n, **c} for n, c in CORRECOES_CNPJ.items()],
        "cnpj_resolvidos_por_nome": len({f["nome"] for f in validas if f.get("cnpj_resolvido_por_nome")}),
        "rouanet": {"destinou": conta("Rouanet", "destinou"), "nao_consta": conta("Rouanet", "nao_consta"),
                    "destinou_desde_corte": sum(1 for f in por_cnpj.values() if (f["mecanismos"]["Rouanet"].get("ultimos_5_anos") or {}).get("anos"))},
        "goyazes": {"destinou": conta("Goyazes", "destinou"), "empresas_novas_descobertas": len(novas)},
        "pat": {"inscrita": conta("PAT", "inscrita"), "inscrita_por_estabelecimento": conta("PAT", "inscrita_por_estabelecimento"),
                "inscricao_inativa": conta("PAT", "inscricao_inativa"), "nao_consta": conta("PAT", "nao_consta")},
        "lucro_real_confirmado_pela_rouanet": sum(1 for f in por_cnpj.values() if f.get("lucro_real")),
        "mecanismos_sem_fonte": {m: MECANISMOS[m]["status"] for m in ("LIE", "FIA", "Fundo do Idoso", "PRONON", "PRONAS/PCD")},
    }
    saida = {"gerado_em": now_iso(), "referencia": REFERENCIA,
             "regra": ("valor, ano e CNPJ só com fonte oficial; mecanismo sem fonte pública sai nulo com o motivo e o "
                       "caminho para obter o dado; inscrição no PAT não prova Lucro Real"),
             "mecanismos": MECANISMOS, "resumo": resumo,
             "empresas": sorted(por_cnpj.values(), key=lambda f: f["nome"]),
             "sem_cnpj": sorted([f for f in validas if not f.get("cnpj")], key=lambda f: f["nome"]),
             "descobertas_goyazes": novas}
    write_json(SAIDA, saida)
    write_json(SAIDA_PAINEL, {k: v for k, v in saida.items() if k != "empresas"} |
               {"empresas": [{"nome": f["nome"], "cnpj": f["cnpj"], "confirmados": f["confirmados"],
                              "rouanet_5_anos": (f["mecanismos"]["Rouanet"].get("ultimos_5_anos") or {}),
                              "goyazes": (f["mecanismos"]["Goyazes"].get("por_ano") or None),
                              "pat": f["mecanismos"]["PAT"].get("status"),
                              "lucro_real": (f.get("lucro_real") or {}).get("classe")} for f in saida["empresas"]]})

    # aplica na biblioteca, para que o painel e os rankings já saiam verificados
    go = ROOT / "biblioteca_alexandria/empresas/go/go.json"
    if go.exists():
        write_json(go, aplicar_em_painel(load_json(go), b))
    for cat in ("destinacao_tributaria", "patrocinio_privado"):
        for destino in (ROOT / f"biblioteca_alexandria/empresas/ranking_{cat}.json", ROOT / f"docs/dados/ranking_{cat}.json"):
            if destino.exists():
                d = load_json(destino)
                d["empresas"] = aplicar_em_ranking(d.get("empresas") or [], cat, b)
                d["total"] = len(d["empresas"])
                d["incentivos_verificados_em"] = REFERENCIA
                d["metodo"] = (d.get("metodo", "") .split(" Desde 26/09/2026")[0] +
                               " Desde 26/09/2026 os mecanismos exibidos são os VERIFICADOS em fonte oficial (SALIC, Secult-GO, MTE); "
                               "as hipóteses antigas ficam em incentivos_hipotese.")
                write_json(destino, d)
    return resumo


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
