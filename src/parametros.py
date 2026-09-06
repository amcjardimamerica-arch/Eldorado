"""PARAMETRIZAÇÃO DAS FONTES DE RECURSO — a base que permite vencer o edital antes do lançamento.

Cada uma das 260 fontes recebe uma ficha `parametros.json` com:

  1. os 14 ITENS do checklist, cada um com valor, origem e situação
     (obtido | previsto pelo regramento | não exigido neste tipo de recurso);
  2. os DOCUMENTOS exigidos, ancorados na Lei 13.019/2014 (arts. 33, 34 e 26 do
     Decreto 8.726/2016) e nas exigências próprias do tipo de recurso, cada um
     marcado como obrigatório | condicional | não exigido, com a base legal;
  3. VALORES mínimo e máximo praticados (do acervo quando há histórico; do
     regramento quando a norma fixa teto; nunca inventados);
  4. os CRITÉRIOS DE PONTUAÇÃO típicos do tipo de recurso, com pesos, ou a
     marcação de que o recurso não é competitivo (emenda, incentivo fiscal,
     credenciamento) — a terceira coluna da análise;
  5. a ANÁLISE PREDITIVA: janela provável, recorrência observada, antecedência
     necessária, o que preparar antes do lançamento e as armadilhas conhecidas.

Os 14 itens = os 12 do edital + REQUISITOS DE HABILITAÇÃO e CRITÉRIOS DE
PONTUAÇÃO, que o titular pediu como verificações próprias.
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json

DESTINO = ROOT / "biblioteca_alexandria/fontes"
CATALOGO = ROOT / "config/fontes_captacao_260.json"

ITENS_14 = ["Objeto", "Prazo de inscrição", "Resultado", "Prazo de recurso", "Valor", "Órgão / financiador",
            "Território", "Esfera", "Requisitos", "Anexos", "Destinação", "Área de atuação",
            "Requisitos de habilitação", "Critérios de pontuação"]

# ── Documentos: Lei 13.019/2014 e Decreto 8.726/2016 (base legal de cada exigência) ──
DOCS_MROSC = [
    ("estatuto", "Estatuto social registrado e alterações", "Lei 13.019/2014, art. 34, III", "obrigatorio"),
    ("ata_eleicao", "Ata de eleição do quadro dirigente atual", "Lei 13.019/2014, art. 34, V", "obrigatorio"),
    ("cnpj", "Comprovante de inscrição no CNPJ (3 anos para federal; 2 estadual; 1 municipal)", "Lei 13.019/2014, art. 33, V, 'a' e art. 34, II", "obrigatorio"),
    ("comprovante_endereco", "Comprovante de endereço da sede ou declaração do dirigente", "Lei 13.019/2014, art. 34, VII", "obrigatorio"),
    ("rg_cpf_dirigente", "Cópia do RG e CPF do dirigente", "Lei 13.019/2014, art. 34, VI", "obrigatorio"),
    ("certidao_federal", "Certidão negativa conjunta de débitos federais (RFB/PGFN)", "Decreto 8.726/2016, art. 26; Lei 13.019/2014, art. 34, II", "obrigatorio"),
    ("certidao_estadual", "Certidão negativa estadual", "Decreto 8.726/2016, art. 26 (regulamento do ente)", "obrigatorio"),
    ("certidao_municipal", "Certidão negativa municipal", "Decreto 8.726/2016, art. 26 (regulamento do ente)", "obrigatorio"),
    ("cndt", "CNDT — Certidão negativa de débitos trabalhistas", "CLT, art. 642-A; exigida nos chamamentos", "obrigatorio"),
    ("crf_fgts", "CRF — Certificado de regularidade do FGTS", "Lei 8.036/1990, art. 27; exigida nos chamamentos", "obrigatorio"),
    ("relatorio_atividades", "Relatório de atividades e comprovação de experiência prévia", "Lei 13.019/2014, art. 33, V, 'b' e art. 34, VIII", "obrigatorio"),
    ("plano_de_trabalho", "Plano de trabalho (metas, cronograma físico-financeiro, indicadores)", "Lei 13.019/2014, arts. 22 e 35, §1º", "obrigatorio"),
    ("declaracao_nao_vedacao", "Declaração de não incidência das vedações do art. 39", "Lei 13.019/2014, art. 34, II c/c art. 39", "obrigatorio"),
    ("declaracao_instalacoes", "Declaração de instalações e condições materiais ou previsão de contratação", "Lei 13.019/2014, art. 33, V, 'c' e art. 34, IX", "obrigatorio"),
    ("conta_bancaria", "Conta bancária específica para a parceria", "Lei 13.019/2014, art. 51", "condicional"),
    ("inscricao_conselho", "Inscrição no conselho de política pública (CMAS, CMDCA, CMI)", "Lei 8.742/1993, art. 9º; Res. CNAS 14/2014 (assistência social)", "condicional"),
    ("cebas", "CEBAS — Certificação de entidade beneficente", "LC 187/2021", "condicional"),
    ("balanco_patrimonial", "Balanço patrimonial e demonstrações contábeis do último exercício", "exigência usual de capacidade financeira (editais e fundos)", "condicional"),
    ("utilidade_publica", "Título/lei de utilidade pública", "leis específicas do ente", "condicional"),
    ("certidao_cadin", "Consulta ao CADIN e ao SIAFI/Transferegov (adimplência)", "Lei 10.522/2002; IN de transferências", "condicional"),
]

# ── Parâmetros por TIPO de recurso: o que a norma já determina antes de o edital sair ──
PERFIL_TIPO = {
    "edital": {
        "competitivo": True, "rito": "chamamento público (Lei 13.019/2014, arts. 23 a 32)",
        "itens_nao_exigidos": [],
        "pontuacao": [("Adequação da proposta ao objeto e à política pública", 25), ("Experiência prévia e capacidade técnica da OSC", 25),
                      ("Metas, indicadores e viabilidade do cronograma", 20), ("Adequação e economicidade do orçamento", 20), ("Território e público beneficiado", 10)],
        "base_pontuacao": "Lei 13.019/2014, art. 27 (julgamento por critérios objetivos publicados no edital)",
        "docs_condicionais_ativos": ["conta_bancaria", "balanco_patrimonial"],
        "prazo_minimo": "30 dias entre publicação e fim das inscrições (Lei 13.019/2014, art. 26 do Decreto 8.726/2016)",
        "recurso": "5 dias úteis do resultado preliminar (Lei 13.019/2014, art. 27, §§4º e 5º)",
    },
    "fundo": {
        "competitivo": True, "rito": "edital do fundo, aprovado pelo conselho gestor",
        "itens_nao_exigidos": [],
        "pontuacao": [("Alinhamento ao plano/política do fundo", 30), ("Experiência da entidade na política", 25), ("Metas e indicadores", 20), ("Orçamento", 15), ("Território prioritário", 10)],
        "base_pontuacao": "resolução do conselho gestor do fundo",
        "docs_condicionais_ativos": ["inscricao_conselho", "conta_bancaria", "balanco_patrimonial"],
        "prazo_minimo": "conforme resolução do conselho (usual 30 dias)",
        "recurso": "conforme resolução do conselho (usual 5 dias úteis)",
    },
    "emenda": {
        "competitivo": False, "rito": "indicação parlamentar — captação pessoal, sem seleção",
        "itens_nao_exigidos": ["Resultado", "Prazo de recurso", "Critérios de pontuação"],
        "motivo_nao_exigidos": "não há seleção competitiva: a indicação é ato político do parlamentar, sem julgamento, resultado publicado ou fase recursal",
        "pontuacao": [], "base_pontuacao": "não se aplica — recurso não competitivo",
        "docs_condicionais_ativos": ["conta_bancaria", "certidao_cadin", "inscricao_conselho"],
        "prazo_minimo": "janela de indicações: outubro a novembro, para o orçamento do ano seguinte",
        "recurso": "não se aplica",
    },
    "incentivo_fiscal": {
        "competitivo": False, "rito": "aprovação técnica do projeto + captação junto a incentivadores",
        "itens_nao_exigidos": ["Critérios de pontuação"],
        "motivo_nao_exigidos": "não há disputa por nota: o projeto é aprovado tecnicamente e o recurso depende de captação junto a contribuintes",
        "pontuacao": [], "base_pontuacao": "análise técnica de admissibilidade (não competitiva)",
        "docs_condicionais_ativos": ["balanco_patrimonial"],
        "prazo_minimo": "janela anual de propostas definida pelo órgão",
        "recurso": "recurso administrativo do indeferimento, no prazo da norma do programa",
    },
    "doacao_patrocinio": {
        "competitivo": False, "rito": "destinação/doação por decisão do doador ou do conselho",
        "itens_nao_exigidos": ["Critérios de pontuação", "Prazo de recurso"],
        "motivo_nao_exigidos": "destinação por decisão do doador/conselho, sem julgamento competitivo nem fase recursal",
        "pontuacao": [], "base_pontuacao": "não se aplica",
        "docs_condicionais_ativos": ["inscricao_conselho", "utilidade_publica", "conta_bancaria"],
        "prazo_minimo": "fluxo contínuo ou janela do conselho/empresa",
        "recurso": "não se aplica",
    },
    "grant": {
        "competitivo": True, "rito": "chamada de propostas de organização privada/internacional",
        "itens_nao_exigidos": [],
        "pontuacao": [("Alinhamento à teoria de mudança do financiador", 30), ("Impacto e evidências", 25), ("Capacidade institucional e governança", 20), ("Orçamento e contrapartida", 15), ("Sustentabilidade", 10)],
        "base_pontuacao": "critérios próprios do financiador (não regidos pela Lei 13.019)",
        "docs_condicionais_ativos": ["balanco_patrimonial", "utilidade_publica"],
        "prazo_minimo": "conforme a chamada (usual 30 a 60 dias)",
        "recurso": "em regra não há; decisão do financiador é final",
    },
    "destinacao_judicial": {
        "competitivo": True, "rito": "credenciamento/habilitação de entidades perante a vara ou o conselho (Res. CNJ 154/2012)",
        "itens_nao_exigidos": ["Valor"],
        "motivo_nao_exigidos": "o valor não é fixado em edital: depende das prestações pecuniárias arrecadadas no período",
        "pontuacao": [("Aderência do projeto ao público da execução penal/direitos difusos", 30), ("Capacidade de execução e prestação de contas", 30), ("Território de atuação", 20), ("Contrapartida social", 20)],
        "base_pontuacao": "edital de chamamento da vara/conselho (Res. CNJ 154/2012, art. 2º)",
        "docs_condicionais_ativos": ["utilidade_publica", "conta_bancaria", "balanco_patrimonial"],
        "prazo_minimo": "chamamento anual ou semestral da vara",
        "recurso": "conforme o edital da vara",
    },
    "outro": {
        "competitivo": None, "rito": "a confirmar no regulamento do programa",
        "itens_nao_exigidos": [],
        "pontuacao": [], "base_pontuacao": "a confirmar no edital/regulamento",
        "docs_condicionais_ativos": ["conta_bancaria"],
        "prazo_minimo": "a confirmar", "recurso": "a confirmar",
    },
}

# ── Faixas de valor por tipo/nível, quando a norma ou a prática as fixa ──
FAIXAS = {
    ("emenda", "federal"): (0.01, 2_500_000.0, "indicação individual de emenda federal (limite por indicação no orçamento)"),
    ("emenda", "estadual"): (0.01, 2_500_000.0, "indicação de emenda estadual (ALEGO)"),
    ("emenda", "municipal"): (0.01, 2_500_000.0, "indicação de emenda municipal (Câmara de Goiânia)"),
    ("incentivo_fiscal", "federal"): (0.01, 1_500_000.0, "Rouanet: teto por proponente/ano conforme IN do MinC; LIE e demais têm tetos próprios"),
    ("incentivo_fiscal", "estadual"): (0.01, None, "Goyazes e similares: teto definido no edital anual do programa"),
    ("doacao_patrocinio", "municipal"): (0.01, None, "destinação de IR/ICMS a fundos: valor conforme destinações captadas no exercício"),
}


def _faixa(fonte: dict, historico: dict) -> dict:
    chave = (fonte["tipo"], fonte["nivel"])
    minimo = maximo = None; base = None
    if chave in FAIXAS:
        minimo, maximo, base = FAIXAS[chave]
    vals = [v for v in (historico.get("valores") or []) if isinstance(v, (int, float))]
    return {"minimo": minimo if minimo is not None else (min(vals) if vals else None),
            "maximo": maximo if maximo is not None else (max(vals) if vals else None),
            "base": base or ("observado no acervo (%d edições)" % len(vals) if vals else "não fixado em norma; depende do edital de cada edição"),
            "observados_no_acervo": vals[:8] or None,
            "nota": "valores mínimo e máximo são referências: o edital de cada edição prevalece"}


def documentos(fonte: dict) -> list[dict]:
    perfil = PERFIL_TIPO.get(fonte["tipo"], PERFIL_TIPO["outro"])
    ativos = set(perfil["docs_condicionais_ativos"])
    if fonte["area"] in ("assistencia_social_seguranca_alimentar", "crianca_adolescente", "pessoa_idosa"):
        ativos.add("inscricao_conselho")
    if fonte["area"] in ("saude_pessoa_com_deficiencia_prevencao",):
        ativos.update({"inscricao_conselho", "cebas"})
    saida = []
    for chave, rotulo, base, natureza in DOCS_MROSC:
        if fonte["nivel"] in ("privada", "internacional") and natureza == "obrigatorio" and chave in ("certidao_estadual", "certidao_municipal", "rg_cpf_dirigente", "declaracao_nao_vedacao", "declaracao_instalacoes"):
            situacao, obs = "nao_exigido", "financiador privado/internacional não se rege pela Lei 13.019/2014; documento não exigido salvo previsão da chamada"
        elif natureza == "obrigatorio":
            situacao, obs = "obrigatorio", base
        elif chave in ativos:
            situacao, obs = "obrigatorio", base + " — exigível neste tipo de recurso/área"
        else:
            situacao, obs = "nao_exigido", base + " — não exigível neste tipo de recurso, salvo previsão expressa do edital"
        saida.append({"documento": chave, "rotulo": rotulo, "situacao": situacao, "base_legal": base, "observacao": obs})
    return saida


def itens_14(fonte: dict, historico: dict, valores: dict) -> list[dict]:
    perfil = PERFIL_TIPO.get(fonte["tipo"], PERFIL_TIPO["outro"])
    nao = set(perfil["itens_nao_exigidos"]); motivo = perfil.get("motivo_nao_exigidos", "não se aplica a este tipo de recurso")
    prev = {
        "Objeto": (f"{fonte['programa']} — {fonte['orgao']}", "catálogo das 260 fontes"),
        "Prazo de inscrição": (perfil["prazo_minimo"], "regramento do tipo de recurso"),
        "Resultado": ("publicação do resultado preliminar e final pelo órgão, no mesmo veículo do edital", "Lei 13.019/2014, art. 27"),
        "Prazo de recurso": (perfil["recurso"], "regramento do tipo de recurso"),
        "Valor": (_texto_faixa(valores), "faixa parametrizada"),
        "Órgão / financiador": (fonte["orgao"], "catálogo"),
        "Território": (fonte.get("uf") or ("Brasil" if fonte["nivel"] == "federal" else "internacional" if fonte["nivel"] == "internacional" else "a confirmar"), "catálogo"),
        "Esfera": (fonte["nivel"], "catálogo"),
        "Requisitos": ("OSC constituída, regularidade fiscal e trabalhista, experiência na área e tempo mínimo de existência conforme a esfera", "Lei 13.019/2014, art. 33"),
        "Anexos": ("edital, plano de trabalho, declarações e planilha orçamentária (modelos publicados com o edital)", "prática do rito"),
        "Destinação": (f"projetos de {fonte['area'].replace('_', ' ')}", "catálogo"),
        "Área de atuação": (fonte["area"], "catálogo"),
        "Requisitos de habilitação": (perfil["rito"], "regramento"),
        "Critérios de pontuação": ("; ".join(f"{c} ({p})" for c, p in perfil["pontuacao"]) or perfil["base_pontuacao"], perfil["base_pontuacao"]),
    }
    saida = []
    for item in ITENS_14:
        if item in nao:
            saida.append({"item": item, "situacao": "nao_exigido", "valor": None, "motivo": motivo})
            continue
        v, origem = prev[item]
        obtido = (historico.get("itens") or {}).get(item)
        saida.append({"item": item, "situacao": "obtido" if obtido else "previsto",
                      "valor": obtido or v, "origem": ("último edital no acervo" if obtido else origem)})
    return saida


def _texto_faixa(v: dict) -> str:
    def fmt(x):
        return ("R$ %s" % f"{x:,.2f}").replace(",", "@").replace(".", ",").replace("@", ".")
    if v["minimo"] is None and v["maximo"] is None:
        return "não fixado previamente; definido no edital de cada edição"
    if v["maximo"] is None:
        return f"a partir de {fmt(v['minimo'])}; teto definido no edital da edição"
    return f"de {fmt(v['minimo'])} a {fmt(v['maximo'])} — {v['base']}"


def historico_da_fonte(fonte: dict, con=None) -> dict:
    """Edições anteriores no acervo: datas, meses, valores e itens já comprovados."""
    import sqlite3
    toks = [t for t in re.findall(r"[a-zà-ú]{5,}", (fonte["programa"] + " " + fonte["orgao"]).lower())
            if t not in ("edital", "editais", "programa", "municipal", "estadual", "federal", "publico", "público", "projetos", "entidade", "entidades")][:4]
    if not toks:
        return {"ocorrencias": 0}
    try:
        con = con or __import__("importlib").import_module("src.banco").conectar()
        rows = con.execute("SELECT data_publicacao, titulo, financiador, url, exigencias, criterios, inicio, fim FROM historico "
                           "WHERE data_publicacao >= date('now','-5 years') LIMIT 40000").fetchall()
    except Exception:
        return {"ocorrencias": 0, "erro": "banco indisponível"}
    orgao_toks = [x for x in re.findall(r"[a-zà-ú]{4,}", (fonte["orgao"] or "").lower())
                  if x not in ("secretaria", "estado", "estadual", "municipal", "federal", "ministerio", "ministério", "fundo", "nacional", "conselho", "para", "goias", "goiás")][:3]
    hits = []
    for r in rows:
        alvo = ((r[1] or "") + " " + (r[2] or "")).lower()
        casa_prog = sum(1 for t in toks if t in alvo) >= min(2, len(toks))
        casa_orgao = bool(orgao_toks) and sum(1 for t in orgao_toks if t in alvo) >= min(2, len(orgao_toks))
        if casa_prog or casa_orgao:
            hits.append(r)
    meses = {}; anos = {}; valores = []
    for r in hits:
        d = (r[0] or "")
        if len(d) >= 7:
            meses[d[5:7]] = meses.get(d[5:7], 0) + 1; anos[d[:4]] = anos.get(d[:4], 0) + 1
        for m in re.finditer(r"R\$\s?([\d\.]{4,},\d{2})", " ".join(str(r[i] or "") for i in (1, 4, 5))):
            try: valores.append(float(m.group(1).replace(".", "").replace(",", ".")))
            except ValueError: pass
    # exigências e critérios já observados em edições anteriores desta fonte
    exig, crit = [], []
    for r in hits[:60]:
        for campo, destino in ((r[4], exig), (r[5], crit)):
            if not campo: continue
            try:
                v = json.loads(campo) if str(campo).strip().startswith(("[", "{")) else [str(campo)]
                destino.extend([str(x)[:160] for x in (v if isinstance(v, list) else [v])])
            except Exception:
                destino.append(str(campo)[:160])
    vistos = set(); exig = [x for x in exig if not (x in vistos or vistos.add(x))][:12]
    vistos = set(); crit = [x for x in crit if not (x in vistos or vistos.add(x))][:12]
    return {"ocorrencias": len(hits), "por_ano": dict(sorted(anos.items())), "por_mes": dict(sorted(meses.items())),
            "valores": valores, "termos": toks + orgao_toks, "exigencias_observadas": exig, "criterios_observados": crit, "ultimas": [{"data": r[0], "titulo": (r[1] or "")[:110], "url": r[3]} for r in hits[:5]]}


MES_NOME = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]


def preditiva(fonte: dict, historico: dict) -> dict:
    perfil = PERFIL_TIPO.get(fonte["tipo"], PERFIL_TIPO["outro"])
    meses = historico.get("por_mes") or {}
    anos = historico.get("por_ano") or {}
    janela = None; confianca = "baixa"
    if meses:
        top = sorted(meses.items(), key=lambda kv: -kv[1])[:2]
        janela = " ou ".join(MES_NOME[int(m) - 1] for m, _ in top)
        confianca = "alta" if len(anos) >= 3 else "média" if len(anos) == 2 else "baixa (uma única ocorrência)"
    else:
        JANELA_TIPO = {"emenda": "outubro a novembro", "incentivo_fiscal": "janela anual do programa (fevereiro a outubro na Rouanet)",
                       "fundo": "primeiro semestre, após aprovação do plano de aplicação pelo conselho",
                       "edital": "não observado no acervo — acompanhar o veículo oficial", "grant": "não observado no acervo",
                       "doacao_patrocinio": "fluxo contínuo", "destinacao_judicial": "chamamento anual da vara", "outro": "não observado"}
        janela = JANELA_TIPO.get(fonte["tipo"], "não observado")
    antecedencia = {"edital": 45, "fundo": 45, "grant": 60, "incentivo_fiscal": 90, "emenda": 90, "doacao_patrocinio": 30, "destinacao_judicial": 45, "outro": 45}[fonte["tipo"]]
    preparar = ["documentação institucional válida (estatuto, ata, CNPJ, endereço)",
                "as cinco certidões dentro do prazo (a federal e a CNDT valem 180 dias; estadual e municipal 90; FGTS 30)",
                "relatório de atividades com evidências dos últimos exercícios",
                "plano de trabalho com metas, indicadores e cronograma físico-financeiro pré-escrito para o objeto típico da fonte"]
    if "inscricao_conselho" in [d["documento"] for d in documentos(fonte) if d["situacao"] == "obrigatorio"]:
        preparar.insert(0, "inscrição vigente no conselho de política pública (leva de 30 a 90 dias — obter fora da janela)")
    if fonte["tipo"] == "incentivo_fiscal":
        preparar.append("cadastro no sistema do programa (Salic/Goyazes) e lista de empresas incentivadoras prováveis")
    if fonte["tipo"] == "emenda":
        preparar.append("habilitação na plataforma de transferências e projeto de bolso para apresentar ao gabinete")
    armadilhas = {"edital": ["prazo curto entre publicação e inscrição (30 dias): sem documentação pronta, não dá tempo",
                             "orçamento sem memória de cálculo e sem 3 cotações costuma zerar a nota de economicidade"],
                  "fundo": ["exigência de inscrição no conselho é eliminatória e demora a sair",
                            "plano de aplicação do fundo define as áreas — projeto fora da linha é desclassificado"],
                  "emenda": ["indicação sem habilitação prévia na plataforma não vira convênio",
                             "ano eleitoral restringe repasses (vedações da Lei 9.504/1997)"],
                  "incentivo_fiscal": ["aprovação não é dinheiro: sem incentivador, o projeto morre aprovado",
                                       "prestação de contas rigorosa; captação parcial exige readequação"],
                  "doacao_patrocinio": ["depende de relacionamento e do calendário fiscal do doador (dezembro)",
                                        "fundos municipais exigem inscrição no conselho e plano aprovado"],
                  "grant": ["exigência de relatórios em inglês e de governança (política de salvaguardas)",
                            "contrapartida e sustentabilidade pesam mais que o projeto em si"],
                  "destinacao_judicial": ["credenciamento é anual e a entidade precisa estar habilitada antes do repasse",
                                          "prestação de contas à vara é mais rígida que em convênios"],
                  "outro": ["regulamento não confirmado: tratar como hipótese até ler o edital"]}[fonte["tipo"]]
    return {"janela_provavel": janela, "confianca": confianca, "recorrencia": {"anos_observados": sorted(anos), "ocorrencias": historico.get("ocorrencias", 0)},
            "antecedencia_recomendada_dias": antecedencia, "preparar_antes": preparar, "armadilhas": armadilhas,
            "vencer_antes_do_lancamento": ("Com a documentação pronta e o plano de trabalho pré-escrito para o objeto típico desta fonte, "
                                           f"a inscrição vira uma tarefa de {'2 a 3 dias' if perfil['competitivo'] else '1 dia'} quando o edital sair. "
                                           f"Comece {antecedencia} dias antes da janela prevista ({janela}).")}


MAPA_DIVULGACAO = {"resolucao_conselho": "fundo", "emenda_parlamentar": "emenda", "pagina_institucional_privada": "grant",
                   "diario_oficial_uniao": "edital", "diario_oficial_estado": "edital", "diario_oficial_municipio": "edital",
                   "lista_projetos_aptos": "incentivo_fiscal", "edital_ministerio_publico": "destinacao_judicial",
                   "edital_destinacao_judicial": "destinacao_judicial", "portal_compras_pncp": "edital", "plataforma_agregadora": "edital"}


def _tipo_efetivo(fonte: dict) -> tuple[str, str | None]:
    """As 79 fontes catalogadas como 'outro' recebem o rito pelo modo de divulgação
    (resolução de conselho → fundo; emenda → emenda; página privada → grant...)."""
    if fonte["tipo"] != "outro":
        return fonte["tipo"], None
    novo = MAPA_DIVULGACAO.get(fonte.get("forma_divulgacao") or "", "outro")
    return novo, (f"tipo inferido do modo de divulgação ({fonte.get('forma_divulgacao')}) — confirmar no primeiro edital lido" if novo != "outro" else None)


def parametrizar(fonte: dict, con=None) -> dict:
    tipo_ef, nota_tipo = _tipo_efetivo(fonte)
    fonte = {**fonte, "tipo": tipo_ef}
    hist = historico_da_fonte(fonte, con)
    val = _faixa(fonte, hist)
    perfil = PERFIL_TIPO.get(fonte["tipo"], PERFIL_TIPO["outro"])
    docs = documentos(fonte)
    ficha = {
        "id": fonte["id"], "programa": fonte["programa"], "orgao": fonte["orgao"], "nivel": fonte["nivel"], "area": fonte["area"],
        "tipo_recurso": fonte["tipo"], "tipo_catalogo": ("outro" if nota_tipo else fonte["tipo"]), "nota_tipo": nota_tipo, "uf": fonte.get("uf"), "goias": bool(fonte.get("goias")), "sites": fonte.get("sites") or [],
        "rito": perfil["rito"], "competitivo": perfil["competitivo"],
        "itens_14": itens_14(fonte, hist, val),
        "documentos": docs,
        "documentos_resumo": {"obrigatorios": [d["documento"] for d in docs if d["situacao"] == "obrigatorio"],
                              "nao_exigidos": [d["documento"] for d in docs if d["situacao"] == "nao_exigido"]},
        "valores": val,
        "pontuacao": {"competitivo": perfil["competitivo"], "base": perfil["base_pontuacao"],
                      "criterios": [{"criterio": c, "peso": p} for c, p in perfil["pontuacao"]] or None,
                      "observados_em_edicoes_anteriores": hist.get("criterios_observados") or None,
                      "nota": "critérios previstos pelo rito; os observados em edições anteriores (quando houver) prevalecem sobre a previsão"},
        "exigencias_observadas": hist.get("exigencias_observadas") or None,
        "historico_5_anos": {k: hist.get(k) for k in ("ocorrencias", "por_ano", "por_mes", "ultimas") if k in hist},
        "preditiva": preditiva(fonte, hist),
        "parametrizado_em": now_iso(), "versao": 1,
        "aviso": "parametrização derivada da norma e do acervo; o edital de cada edição prevalece. Itens 'previsto' são hipóteses fundamentadas, não fatos.",
    }
    return ficha


def run(inicio: int = 0, quantidade: int = 260) -> dict:
    """Sequencial: uma fonte por vez, gravando antes de passar à seguinte."""
    from .banco import conectar
    fontes = load_json(CATALOGO)["fontes"]
    try:
        con = conectar()
    except Exception:
        con = None
    feitas, erros = [], []
    for f in fontes[inicio:inicio + quantidade]:
        try:
            ficha = parametrizar(f, con)
            pasta = DESTINO / f["id"]; pasta.mkdir(parents=True, exist_ok=True)
            write_json(pasta / "parametros.json", ficha)
            feitas.append(f["id"])
        except Exception as exc:
            erros.append({"id": f["id"], "erro": f"{type(exc).__name__}: {exc}"})
    indice = {"gerado_em": now_iso(), "total_catalogo": len(fontes),
              "parametrizadas": sorted(p.parent.name for p in DESTINO.glob("*/parametros.json"))}
    write_json(DESTINO / "indice_parametros.json", indice)
    return {"parametrizadas_agora": len(feitas), "erros": erros[:5], "total_parametrizadas": len(indice["parametrizadas"]), "total_catalogo": len(fontes)}


if __name__ == "__main__":
    import sys
    ini = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    qtd = int(sys.argv[2]) if len(sys.argv) > 2 else 260
    print(json.dumps(run(ini, qtd), ensure_ascii=False, indent=2))
