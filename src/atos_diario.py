"""ATOS DE DIÁRIO OFICIAL — classificador comum aos motores de diário (parecer do motor 02, 01/10/2026).

Generaliza o classificador do motor 01 (`src/diario_goiania.py`) para qualquer diário — municipal ou estadual:
o mesmo esquema (tipo · regime · público · órgão · prazo) e os mesmos vereditos (OPORTUNIDADE · ACOMPANHAR ·
RUÍDO, sempre com o motivo escrito). O motor 01 continua com a sua cópia até o PR nº 11 ser mesclado; depois
passa a importar daqui (pendência registrada no parecer do motor 02) — assim os dois PRs não colidem.

O que este módulo acrescenta ao do motor 01:
  · órgão passado de fora (tabela de órgãos estaduais; ou o caminho do sumário do Diário do Estado, que já diz
    "SECRETARIAS DE ESTADO › Secretaria de Estado da Cultura › Atos › Editais");
  · o TÍTULO da matéria entra como cabeçalho — o Diário de Goiás entrega título e texto separados;
  · vetos do ruído típico do Estado: processo seletivo simplificado (PSS), licitação/pregão/registro de preço,
    compra da agricultura familiar (PNAE), Organização Social (Lei Estadual 15.503/2005) e atos de pessoal;
  · recorte da página do Diário de Goiás pelo carimbo "Protocolo NNNNNN", que fecha cada matéria;
  · chave de deduplicação entre fontes (o mesmo edital no Diário e no site da secretaria vira um registro só).

Sem IA, sem rede, só biblioteca-padrão. Conteúdo é DADO: este módulo não executa nada do que lê.
"""
from __future__ import annotations

import re
import unicodedata
from datetime import date, timedelta

from . import diario_goiania as _dg

# Reaproveita os padrões validados no motor 01 (um só lugar para corrigir)
_RX = _dg._RX
_CAB_CORPO = _dg._CAB_CORPO
_NUM_CHAM = _dg._NUM_CHAM
_NUM = _dg._NUM
_OBJETO = _dg._OBJETO
_FIM = _dg._FIM
_PERIODO = _dg._PERIODO
_VALOR = _dg._VALOR
_data_br = _dg._data_br
mascarar_pii = _dg.mascarar_pii


def sem_acento(t: str) -> str:
    t = unicodedata.normalize("NFKD", t or "")
    return "".join(c for c in t if not unicodedata.combining(c))


# ─────────────────────────── órgãos do Estado de Goiás (ordem importa) ───────────────────────────
ORGAOS_GO = [
    ("CEDCA/FIA-GO", r"\bCEDCA\b|DIREITOS DA CRIANCA E DO ADOLESCENTE|\bFIA\b|FUNDO ESTADUAL DA INFANCIA"),
    ("CEAS/FEAS-GO", r"\bCEAS\b|\bFEAS\b|CONSELHO ESTADUAL DE ASSISTENCIA SOCIAL|FUNDO ESTADUAL DE ASSISTENCIA SOCIAL"),
    ("Conselho Estadual da Pessoa Idosa", r"PESSOA IDOSA|CONSELHO ESTADUAL DO IDOSO|FUNDO ESTADUAL DO IDOSO"),
    ("SECULT-GO (cultura)", r"SECRETARIA DE ESTADO DA CULTURA|\bSECULT\b|GOYAZES|FUNDO DE ARTE E CULTURA|ALDIR BLANC|\bPNAB\b"),
    ("SEDS-GO / Goiás Social", r"DESENVOLVIMENTO SOCIAL|\bSEDS\b|GOIAS SOCIAL|COFINANCIAMENTO"),
    ("OVG", r"VOLUNTARIAS DE GOIAS|\bOVG\b"),
    ("SEEL-GO (esporte)", r"ESPORTE E LAZER|\bSEEL\b"),
    ("Retomada (trabalho e qualificação)", r"SECRETARIA DE ESTADO DA RETOMADA|\bRETOMADA\b"),
    ("SEDUC-GO (educação)", r"SECRETARIA DE ESTADO DA EDUCACAO|\bSEDUC\b"),
    ("SES-GO (saúde)", r"SECRETARIA (DE ESTADO )?DA SAUDE|\bSES\b"),
    ("SECTI-GO (ciência e tecnologia)", r"CIENCIA, TECNOLOGIA|\bSECTI\b"),
    ("FAPEG", r"\bFAPEG\b|FUNDACAO DE AMPARO A PESQUISA"),
    ("Direitos Humanos / Mulher", r"DIREITOS HUMANOS|SECRETARIA DE ESTADO DA MULHER|IGUALDADE RACIAL"),
    ("SEAPA-GO (agricultura)", r"AGRICULTURA, PECUARIA|\bSEAPA\b"),
    ("ALEGO (emendas)", r"EMENDA (PARLAMENTAR|IMPOSITIVA)|DECRETO DE PROGRAMACAO"),
]

_RESULTADO_EXTRA = re.compile(r"LISTA DE APROVADOS|APROVADOS E SUPLENTES|RELACAO DOS (?:SELECIONADOS|CLASSIFICADOS|HABILITADOS)|"
                              r"SELECIONADOS|CLASSIFICADOS|CONVALIDACAO|HOMOLOGACAO DO RESULTADO")
_LICITACAO_CAB = re.compile(r"PREGAO|LICITACAO|LEILAO|CONCORRENCIA|TOMADA DE PRECOS|ADJUDICA|REGISTRO DE PRECOS?|DISPENSA DE LICITA")
_CAB_T = re.compile(r"\b(?:EDITAL|AVISO|CHAMADA PUBLICA|EXTRATO|RESULTADO|HOMOLOGACAO|RETIFICACAO|ERRATA|RESOLUCAO|PORTARIA|"
                    r"DECRETO|DESPACHO|ATA DE|TERMO DE|TERMO ADITIVO|JUSTIFICATIVA|INEXIGIBILIDADE|LEI N|INSTRUCAO NORMATIVA)\b")
_MUNICIPIO = re.compile(r"(?:O\s+)?MUNIC[IÍ]PIO\s+DE\s+([A-ZÀ-Ú][A-ZÀ-Ú' ]{2,40}?)\s*(?:[-–,/(]|\b(?:GO|ESTADO|CNPJ|POR|ATRAVES|TORNA|INSCRITO|PESSOA)\b)")


_EXTRA = {
    "pss": re.compile(r"PROCESSO SELETIVO SIMPLIFICADO|\bPSS\b|CONTRATACAO TEMPORARIA|PROCESSO SELETIVO PARA CONTRATA"),
    "licitacao": re.compile(r"PREGAO|CONCORRENCIA|TOMADA DE PRECOS|REGISTRO DE PRECOS?|DISPENSA DE LICITACAO|"
                            r"INEXIGIBILIDADE DE LICITACAO|AVISO DE LICITACAO|ADJUDICACAO|LEILAO"),
    "pnae": re.compile(r"AGRICULTURA FAMILIAR|\bPNAE\b|GENEROS ALIMENTICIOS|ALIMENTACAO ESCOLAR"),
    "os_estadual": re.compile(r"15\.503|CONTRATO DE GESTAO|QUALIFICACAO COMO ORGANIZACAO SOCIAL|ORGANIZACOES SOCIAIS"),
    "pessoal": re.compile(r"NOMEA|EXONERA|APOSENTADORIA|PENSAO|FERIAS|LICENCA|PROGRESSAO|DESIGNA(R)? .{0,40}SERVIDOR|"
                          r"CESSAO DE SERVIDOR|ABONO"),
    "fomento_forte": re.compile(r"TERMO DE FOMENTO|TERMO DE COLABORACAO|13\.019|ORGANIZACOES? DA SOCIEDADE CIVIL|\bOSCS?\b|"
                                r"SEM FINS LUCRATIVOS|SELECAO DE PROJETOS|FOMENTO A CULTURA|PREMIO|PREMIACAO"),
}
_D = r"(\d{1,2}/\d{1,2}/\d{4}|\d{1,2}\s+de\s+[a-zç]+\s+de\s+\d{4})"
_PERIODO2 = re.compile(r"(?:do dia|de|entre os dias|entre)\s+" + _D + r"\s+(?:a|at[ée]|e)\s+(?:o dia\s+)?" + _D, re.I)
_CONTEXTO_PRAZO = re.compile(r"ABERT|INSCRI|PROPOSTA|RECEB|CHAMAMENTO|PROTOCOL|ENVIO", re.I)


def _periodo_aberto(bruto: str):
    """"Torna público que do dia 28/09/2026 a 02/10/2026 estará aberto chamamento" → a 2ª data, se o entorno falar
    de abertura/inscrição (vigência de contrato "de 01/01 a 31/12" não conta)."""
    for m in _PERIODO2.finditer(bruto):
        entorno = bruto[max(0, m.start() - 150): m.end() + 150]
        if _CONTEXTO_PRAZO.search(entorno) and not re.search(r"vig[eê]ncia", entorno, re.I):
            return m.group(2)
    return None


_PROTOCOLO = re.compile(r"Protocolo\s+\d{5,7}\b")


def orgao_do_caminho(caminho: str | None, orgaos=ORGAOS_GO) -> str | None:
    """O sumário do Diário de Goiás já diz quem publicou: "… › Secretaria de Estado da Cultura › Atos › Editais"."""
    if not caminho:
        return None
    C = sem_acento(caminho).upper()
    if C.startswith("MUNICIPIOS"):
        partes = [p.strip() for p in caminho.split("›")]
        return f"Prefeitura de {partes[2]}" if len(partes) > 2 and partes[1].upper().startswith("PREFEITURA") else partes[-1]
    return next((r for r, p in orgaos if re.search(p, C)), None)


_PREFEITURA = re.compile(r"PREFEITURA (?:MUNICIPAL )?DE ([A-ZÀ-Ú][A-ZÀ-Ú' ]{2,40}?)\s*(?:[-–,(/]|\b(?:CNPJ|AVISO|EDITAL|EXTRATO|TORNA|O MUNIC[IÍ]PIO|ESTADO DE GOI[AÁ]S)\b)")
_MINUSC = {"De", "Do", "Da", "Dos", "Das", "E"}


def prefeitura_no_texto(bruto: str) -> str | None:
    """Publicação de prefeitura achada pela busca (sem caminho do sumário): "PREFEITURA MUNICIPAL DE NOVA IGUAÇU…"."""
    m = _PREFEITURA.search((bruto or "")[:600].upper()) or _MUNICIPIO.search((bruto or "")[:700].upper())
    if not m:
        return None
    return " ".join(w.lower() if w in _MINUSC else w for w in m.group(1).strip().title().split())


def territorio_do_caminho(caminho: str | None) -> tuple[str, str]:
    """(nível, território) — publicação de prefeitura no Diário do Estado é municipal."""
    if caminho and sem_acento(caminho).upper().startswith("MUNICIPIOS"):
        partes = [p.strip() for p in caminho.split("›")]
        if len(partes) > 2:
            return "municipal", f"GO/{partes[2]}"
    return "estadual", "GO"


def segmentar_pagina(texto: str, maximo: int = 40) -> list[str]:
    """Página do Diário de Goiás → matérias: cada uma termina no carimbo "Protocolo NNNNNN"."""
    if not texto:
        return []
    partes, ini = [], 0
    for m in _PROTOCOLO.finditer(texto):
        partes.append(texto[ini:m.end()].strip()); ini = m.end()
    if ini < len(texto):
        partes.append(texto[ini:].strip())
    return [p for p in partes if len(p) > 60][:maximo]


def classificar(trecho: str, hoje: date | None = None, publicado: str | None = None, *,
                titulo: str | None = None, caminho: str | None = None, orgaos=ORGAOS_GO, ambito: str = "estadual") -> dict:
    """Classifica UMA matéria. Mesma regra do motor 01, com título/caminho do sumário e vetos estaduais."""
    hoje = hoje or date.today()
    corpo = re.sub(r"[ \t]+", " ", trecho or "")
    bruto = ((titulo.strip() + "\n") if titulo else "") + corpo
    T = sem_acento(bruto).upper()
    mc = _CAB_CORPO.search(bruto[:700])
    tem_cab = bool(mc)
    ini = len(sem_acento(bruto[:mc.start()])) if mc else 0
    mt = _CAB_T.search(T[:200])                  # "Palmelo Extrato Termo de Convalidação…": cabeçalho em caixa mista
    if mt and (not mc or mt.start() < ini):
        tem_cab, ini = True, mt.start()
    cab = T[ini:ini + 220] if tem_cab else ""
    s = {k: bool(rx.search(T)) for k, rx in _RX.items()}
    s.update({k: bool(rx.search(T)) for k, rx in _EXTRA.items()})
    c = {k: bool(rx.search(cab)) for k, rx in _RX.items() if k in ("resultado", "celebracao", "retificacao", "abertura")}
    folha = sem_acento((caminho or "").split("›")[-1]).upper().strip()
    cab = cab or T.lstrip()[:220]
    # TIPO — o cabeçalho (título) manda; a seção do sumário desempata
    c["resultado"] = c["resultado"] or bool(_RESULTADO_EXTRA.search(cab))
    if c["resultado"] or folha.startswith(("RESULTADO", "ADJUDICAC")) or (re.match(r"\s*(DESPACHO|PORTARIA|ATA)\b", cab) and s["resultado"]):
        tipo = "andamento"
    elif re.match(r"\s*EXTRATO DE PUBLICACAO", cab) and re.search(r"TORNA PUBLIC\w* A REALIZACAO|LANCAMENTO D[OE]|SELECAO PUBLICA", T):
        tipo = "abertura"                        # SECULT-GO publica o lançamento do edital como "Extrato de Publicação"
    elif c["celebracao"] or re.match(r"\s*(EXTRATO|JUSTIFICATIVA)\b", cab) or folha.startswith(("EXTRATO", "TERMOS DE CONVENIO", "TERMOS ADITIVOS", "ACORDOS")):
        tipo = "celebracao"
    elif c["retificacao"] or folha.startswith(("ERRATA", "RETIFICAC", "ADIAMENTO")):
        tipo = "retificacao"
    elif c["abertura"] or (re.match(r"\s*(EDITAL|AVISO|CHAMADA)\b", cab) and (s["abertura"] or s["abertura_corpo"])) \
            or (folha in ("EDITAIS", "CHAMADAS PUBLICAS", "AVISOS") and s["abertura_corpo"]):
        tipo = "abertura"
    elif re.match(r"\s*(DECRETO|PORTARIA|DESPACHO|LEI|RESOLUCAO|INSTRUCAO)\b", cab):
        tipo = "normativo" if not s["resultado"] else "andamento"
    else:
        tipo = "abertura" if s["abertura_corpo"] else "andamento" if s["resultado"] else "referencia"
    if s["conselho_composicao"] and tipo in ("abertura", "retificacao"):
        tipo = "composicao_conselho"
    if tipo == "retificacao" and not re.search(r"EDITAL|CHAMAMENTO|CHAMADA", T):
        tipo = "referencia"                      # prorrogação de comissão, portaria etc. — não é edital
    # REGIME — os vetos estaduais vêm antes do fomento, salvo quando o texto é claramente de fomento a OSC
    fomento = s["mrosc"] or s["fundo"] or s["cultura"] or s["fomento_forte"]
    if _LICITACAO_CAB.search(cab[:160]) and not re.search(r"CHAMAMENTO|CHAMADA PUBLICA|FOMENTO|COLABORA", cab[:160]):
        regime = "licitacao"                     # "AVISO DE LICITAÇÃO — PREGÃO… FUNDO MUNICIPAL DE ASSISTÊNCIA SOCIAL"
    elif s["os_saude"] or (s["os_estadual"] and not s["mrosc"]):
        regime = "organizacao_social"
    elif s["pss"] and not fomento:
        regime = "processo_seletivo_pessoal"
    elif s["pnae"] and not (s["mrosc"] or s["fundo"]):
        regime = "pnae_agricultura_familiar"
    elif s["credenciamento"] and s["cultura"] and not (s["mrosc"] or s["fundo"]):
        regime = "credenciamento_cultura"        # PNAB: pareceristas (pessoa física) ou agentes/espaços — conferir
    elif s["credenciamento"] and not (s["mrosc"] or s["fundo"]):
        regime = "credenciamento"
    elif s["licitacao"] and not fomento:
        regime = "licitacao"
    elif s["cultura"]:
        regime = "pnab_cultura"
    elif s["fundo"]:
        regime = "fundo_conselho"
    elif s["mrosc"] or s["fomento_forte"]:
        regime = "mrosc"
    elif s["pessoal"]:
        regime = "pessoal"
    else:
        regime = "indefinido"
    publico = ("osc" if (s["mrosc"] or s["fundo"] or s["fomento_forte"] and not s["pessoa_fisica"]) else
               "pessoa_fisica" if s["pessoa_fisica"] and not s["empresa"] else
               "empresa" if s["empresa"] else
               "osc_e_pessoa_fisica" if regime == "pnab_cultura" else "indefinido")
    if regime == "pnab_cultura" and s["pessoa_fisica"] and not (s["mrosc"] or s["fundo"]):
        publico = "osc_e_pessoa_fisica"
    pref = None if caminho else prefeitura_no_texto(bruto)
    municipal_txt = bool(re.search(r"SECRETARIA MUNICIPAL|FUNDO MUNICIPAL|PREFEITURA MUNICIPAL|O MUNICIPIO DE", T[:900]))
    orgao = orgao_do_caminho(caminho, orgaos) or (f"Prefeitura de {pref}" if pref else None) \
        or ("Prefeitura (município a confirmar)" if municipal_txt and not caminho else None) \
        or next((r for r, p in orgaos if re.search(p, T)), None)
    if pref or (orgao or "").startswith("Prefeitura de "):
        ambito = "municipal"
    num = _NUM_CHAM.search(T) or _NUM.search(cab) or _NUM.search(T[:900])
    obj = _OBJETO.search(corpo) or _OBJETO.search(bruto)
    mp, m = _PERIODO.search(bruto), _FIM.search(bruto)
    fim_txt = mp.group(2) if mp else (_periodo_aberto(bruto) or (m.group(1) if m else None))
    fim = _data_br(fim_txt)
    motivos = []
    de_interesse = regime in ("mrosc", "fundo_conselho", "pnab_cultura")
    if tipo in ("abertura", "retificacao") and de_interesse and publico in ("osc", "osc_e_pessoa_fisica"):
        velho = bool(publicado) and str(publicado)[:10] < (hoje - timedelta(days=60)).isoformat()
        if fim and fim < hoje.isoformat():
            veredito = "ACOMPANHAR"; motivos.append(f"edital de interesse, mas o prazo escrito ({fim}) já passou")
        elif not fim and velho:
            veredito = "ACOMPANHAR"; motivos.append(f"edital de interesse publicado em {str(publicado)[:10]}, sem prazo no trecho — "
                                                     "mais de 60 dias: conferir se ainda está aberto antes de tratar como oportunidade")
        elif tipo == "retificacao" and not fim:
            veredito = "ACOMPANHAR"; motivos.append("retificação de edital de interesse sem novo prazo no texto — conferir o cronograma no edital")
        else:
            veredito = "OPORTUNIDADE"; motivos.append(f"{tipo} de seleção para OSC no regime {regime}")
    elif tipo in ("andamento", "celebracao", "retificacao", "composicao_conselho") and (de_interesse or publico == "osc"):
        veredito = "ACOMPANHAR"
        motivos.append({"andamento": "resultado/andamento de seleção de interesse — prazo de recurso e quem venceu",
                        "celebracao": "parceria celebrada, convênio ou inexigibilidade — inteligência: órgão, valor e entidade",
                        "retificacao": "retificação de edital de interesse — conferir prazo",
                        "composicao_conselho": f"vaga da sociedade civil em conselho {'estadual' if ambito == 'estadual' else 'municipal'} — porta de entrada dos fundos"}[tipo])
    elif regime == "credenciamento_cultura" and tipo in ("abertura", "retificacao"):
        veredito = "ACOMPANHAR"
        motivos.append("credenciamento no âmbito da PNAB — conferir se é de pareceristas (pessoa física) ou de agentes e espaços culturais")
    elif tipo == "referencia" and de_interesse and (num or _VALOR.search(bruto) or re.search(r"CELEBRA|REPASSE|TERMO DE FOMENTO", T)):
        veredito = "ACOMPANHAR"
        motivos.append("menção a parceria ou edital de interesse dentro de outro ato — conferir o ato completo na edição")
    else:
        veredito = "RUIDO"
        motivos.append({"credenciamento": "credenciamento de prestadores (Lei 14.133 art. 79) — não é fomento a OSC",
                        "organizacao_social": "Organização Social / contrato de gestão (Lei Estadual 15.503/2005) — não é edital para associação",
                        "processo_seletivo_pessoal": "processo seletivo simplificado de pessoal — não é recurso para OSC",
                        "pnae_agricultura_familiar": "compra da agricultura familiar (PNAE) — não é fomento a OSC",
                        "licitacao": "licitação/contratação de empresa — não é fomento a OSC",
                        "pessoal": "ato de pessoal (nomeação, aposentadoria, férias)",
                        }.get(regime, f"tipo {tipo}, regime {regime}, público {publico} — sem seleção aberta para OSC"))
    return {
        "veredito": veredito, "tipo": tipo, "regime": regime, "publico": publico, "orgao": orgao,
        "numero": re.sub(r"\s+", "", num.group(1)) if num else None,
        "cabecalho": re.sub(r"\s+", " ", bruto.strip()[:160]),
        "objeto": re.sub(r"\s+", " ", obj.group(1)).strip()[:400] if obj else None,
        "prazo_texto": fim_txt, "fim": fim,
        "valores": sorted(set(_VALOR.findall(bruto)))[:5],
        "sinais": sorted(k for k, v in s.items() if v), "motivos": motivos, "cabecalho_detectado": tem_cab,
    }


def chave_ato(orgao: str | None, numero: str | None, titulo: str | None, data: str | None = None) -> str:
    """Mesmo edital em fontes diferentes → mesma chave: órgão + número; sem número, órgão + dia da publicação
    (o Diário e a busca dão títulos diferentes ao mesmo aviso); sem os dois, o título normalizado."""
    o = re.sub(r"[^a-z0-9]+", "", sem_acento(orgao or "").lower())[:30]
    if numero:
        n = re.sub(r"[^0-9/]", "", numero)
        a, _, b = n.partition("/")
        return f"{o}|{int(a) if a.isdigit() else a}/{b}"          # "03/2026" e "3/2026" são o mesmo edital
    if data and o:
        return f"{o}|{str(data)[:10]}|sn"
    return f"{o}|{re.sub(r'[^a-z0-9]+', '', sem_acento(titulo or '').lower())[:60]}"
