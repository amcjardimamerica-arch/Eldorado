"""MOTOR 03 — Diário Oficial da União (versão 2, 01/10/2026).

Parecer do conselho: docs/pareceres/motor-03-diario-uniao.md. O que o motor antigo fazia e por que rendia pouco:

1. Lia a "Leitura do Jornal" só da Seção 3 com o limite geral de 2,5 MB por página. A Seção 3 tem 2,1–2,7 MB:
   nos dias maiores (02, 04, 11 e 25/09; 01/10) o HTML vinha cortado antes de fechar o JSON das matérias, a
   expressão de reserva achava o `{"jsonArray":[]}` VAZIO do portlet de busca e o painel mostrava "matérias do
   DOU lidas: 0" com a página respondendo 200.
2. Nos outros dias lia só as 600 primeiras das ~2.200 matérias da Seção 3 (≈27%) e NUNCA lia a Seção 1
   (resoluções dos conselhos nacionais, portarias do MinC, MDS, MDHC) nem as edições extras.
3. Decidia pelo TÍTULO da matéria ("EXTRATO DE TERMO DE FOMENTO", "EDITAL DE Nº 126/IFAL"), que no DOU é
   genérico: em setembro trouxe 14 registros — 9 extratos de parceria já celebrada, 4 editais de universidade e
   1 edital de intimação. Nenhuma seleção aberta a OSC. O "prazo" gravado era a data de publicação.
4. A busca /consulta com `exactDate=dia` deu HTTPError em 297 de 328 tentativas (bloqueios.json) e a descoberta
   seguia links institucionais ("Destaques do DOU", "Leitura do Jornal" sem data).

Como funciona agora (sem IA, sem tokens, biblioteca-padrão):
  Fonte A — leitura do jornal: DO1 + DO3 + as edições extras que o próprio dia anuncia (`typeNormDay`), lidas
            INTEIRAS (limite próprio de 12 MB) e recortadas pelo `<script id="params">` exato. Cada matéria já
            traz tipo (artType), órgão (hierarquia), página e um trecho; o filtro de interesse escolhe as que
            valem abrir e a íntegra vem de /web/dou/-/<urlTitle>.
  Fonte B — busca do DOU (reserva): consultas dirigidas na janela da semana; só entra o que a Fonte A não viu.
  → cada matéria é classificada por `src/atos_diario.py` (OPORTUNIDADE · ACOMPANHAR · RUÍDO, com o motivo),
    com os vetos e regimes próprios da esfera federal deste módulo;
  → prefeituras e governos de OUTROS estados que publicam no DOU ficam fora (território); as de Goiás entram.

Conteúdo coletado é DADO: injeção → quarentena; CPF → [CPF]; o que o texto não diz fica `null`.
"""
from __future__ import annotations

import html as _html
import json
import os
import re
import time
from datetime import date, timedelta
from urllib.parse import quote

from . import atos_diario as atos
from .nucleo import (ROOT, append_jsonl, has_prompt_injection, load_json, now_iso, sha256,
                     validate_public_https, write_json)

MOTOR_ID = "dou"
CFG = ROOT / "config/diario_uniao.json"
ESTADO = ROOT / "estado/diario_uniao.json"
QUARENTENA = ROOT / "estado/quarentena.jsonl"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 Eldorado-OSC/1.0"
BASE = "https://www.in.gov.br"
UF = "GO"
NOME_UF = "GOIAS"

# feriados nacionais fixos: dia útil sem edição não é falha nesses dias
FERIADOS_FIXOS = {"01-01", "04-21", "05-01", "09-07", "10-12", "11-02", "11-15", "11-20", "12-25"}

# ─────────────────────────── filtro de interesse (o que vale abrir) ───────────────────────────
INTERESSE = re.compile(
    r"CHAMAMENTO|CHAMADA PUBLICA|TERMO DE FOMENTO|TERMO DE COLABORA|13\.019|SOCIEDADE CIVIL|\bOSCS?\b|SEM FINS LUCRATIVOS|"
    r"FILANTROP|CONANDA|\bFNCA\b|FUNDO NACIONAL (?:DOS DIREITOS )?DA CRIANCA|FUNDO NACIONAL D[OA] (?:PESSOA )?IDOS|\bPNAB\b|"
    r"ALDIR BLANC|PAULO GUSTAVO|ROUANET|PRONON|PRONAS|INCENTIVO AO ESPORTE|EMENDAS? PARLAMENTAR|PREMIO|PREMIACAO|"
    r"SELECAO DE PROJETOS|EDITAL DE SELECAO|PONTOS? DE CULTURA|CULTURA VIVA|EXTRATO DE PARCERIA|DOACAO|PATROCINIO|"
    r"DIREITOS DIFUSOS|FUNDO NACIONAL DO MEIO AMBIENTE")
# tipos de matéria que nunca são recurso para OSC (salvo quando o próprio tipo fala de chamamento/fomento)
TIPO_VETO = re.compile(
    r"LICITACAO|PREGAO|ADJUDICA|REGISTRO DE PRECOS|^EXTRATO DE CONTRATO|TERMO ADITIVO|APOSTILAMENTO|RESCISAO|PENALIDADE|"
    r"INTIMACAO|NOTIFICACAO|CITACAO|REGISTRO DE DIPLOMA|SUSPENSAO|DISTRATO|COMODATO|PERMISSAO DE USO|ATO DECLARATORIO|"
    r"ACORDAO|PAUTA")
TIPO_SALVA = re.compile(r"CHAMAMENTO|FOMENTO|COLABORA")
# órgãos da Seção 1 que publicam fomento a OSC (resoluções de conselho, portarias de edital, cofinanciamento)
HIER_SOCIAL = re.compile(
    r"CULTURA|ASSISTENCIA SOCIAL|DESENVOLVIMENTO SOCIAL|DIREITOS HUMANOS|ESPORTE|MEIO AMBIENTE|MULHERES|IGUALDADE RACIAL|"
    r"POVOS INDIGENAS|SAUDE|EDUCACAO|CIDADES|JUSTICA|TRABALHO|AGRARIO|PESCA|CIENCIA")
HIER_FORA = re.compile(r"^ENTIDADES DE FISCALIZACAO DO EXERCICIO DAS PROFISSOES")   # conselhos profissionais (CREA, CRM…)

# ─────────────────────────── vetos e regimes da esfera federal (vão ao classificador comum) ───────────────────────────
VETOS_BR = [
    # (regime, padrão, motivo, cede_a_mrosc) — calibrados com as 55.567 matérias de setembro/2026
    ("selecao_academica",
     re.compile(r"CONCESSAO DE BOLSA|BOLSAS? DE (?:PESQUISA|ESTUDO|INICIACAO|EXTENSAO|MONITORIA)|BOLSISTA|POS-GRADUACAO|MESTRADO|"
                r"DOUTORADO|RESIDENCIA (?:MEDICA|MULTIPROFISSIONAL|EM AREA)|VESTIBULAR|ESTAGIARI|ESTAGIO (?:OBRIGATORIO|NAO OBRIGATORIO|"
                r"CURRICULAR|REMUNERADO)|PROFESSOR(?:ES)? (?:SUBSTITUTO|VISITANTE|EFETIVO)|SELECAO DE DOCENTE|CONCURSO PUBLICO|\bSISU\b|"
                r"TRANSFERENCIA EXTERNA|PORTADOR DE DIPLOMA|SERVICO MILITAR|OFICIAIS? TEMPORARI|BANCO DE AVALIADORES|PREMIO CAPES|"
                r"DE TESE\b|TESES E DISSERTACOES"),
     "seleção acadêmica, militar ou de pessoal (bolsas, alunos, professores, concurso) — não é recurso para OSC", False),
    ("empreendedorismo",
     re.compile(r"INCUBADORA|STARTUPS?\b|EMPREENDIMENTOS? INOVADORES|ATIVIDADES EMPREENDEDORAS|ACELERACAO DE EMPRESAS"),
     "incubação ou aceleração de empresas e startups — não é recurso para associação", True),
    ("selecao_pessoas",
     re.compile(r"PROCESSO SELETIVO|SELECAO (?:DE|PARA) (?:ALUNOS|DISCENTES|CANDIDATOS|ESTUDANTES)|PESSOAS CANDIDATAS"),
     "processo seletivo de pessoas — não é recurso para OSC", True),
    ("apoio_ao_orgao",
     re.compile(r"ATRAIR APOIO|CAPTACAO DE APOIO|RECEBER APOIO|APOIO DE PESSOAS JURIDICAS|OFERTA DE PATROCINIO (?:AO|A|PARA)|"
                r"DOACAO (?:AO|A|PARA O) (?:CAMPUS|INSTITUTO|ORGAO|HOSPITAL|UNIVERSIDADE)|IMOVE(?:L|IS)[^.]{0,60}MEDIANTE DOACAO|"
                r"EM FAVOR D[AO] (?:UNIVERSIDADE|INSTITUTO FEDERAL|CAMPUS|HOSPITAL|FUNDACAO OSWALDO)|"
                r"DONATARI[OA]:?\s*(?:A |O )?(?:UNIVERSIDADE|INSTITUTO FEDERAL|CAMPUS|HOSPITAL)"),
     "chamada para o órgão público RECEBER apoio, patrocínio ou doação — quem paga é a entidade; não é recurso para OSC", False),
    ("imovel",
     re.compile(r"LOCACAO DE IMOVE|PROSPECCAO (?:DE MERCADO )?(?:DE |PARA )?IMOVE|IMOVE(?:L|IS) (?:PARA|A SER) (?:LOCAD|LOCACAO|ABRIGAR|"
                r"INSTALACAO|SEDIAR)|AQUISICAO DE IMOVE|ALIENACAO DE (?:BENS )?IMOVE|SELECAO DE IMOVE|PROCURA DE IMOVE|NECESSITA LOCAR|"
                r"ESCOLHA DE AREA|AREA MINIMA DE|CESSAO DE (?:USO DE )?(?:ESPACO|AREA)|EXPLORACAO COMERCIAL|LANCHONETE|CANTINA|"
                r"CONCESSIONARIOS|PERMISSIONARIOS"),
     "chamamento para imóvel, cessão de espaço ou exploração comercial — não é fomento a OSC", False),
    ("ato_processual",
     re.compile(r"EDITAL DE (?:INTIMACAO|NOTIFICACAO|CITACAO)|AUTO DE INFRACAO|NOTIFICACAO DE LANCAMENTO|PROCESSO ADMINISTRATIVO "
                r"SANCIONADOR|CANCELAMENTO DE REGISTRO"),
     "intimação, notificação ou ato sancionador — não é edital para associação", False),
    ("empresas_servicos",
     re.compile(r"CONTRATACAO (?:PELO MENOR PRECO[^.]{0,40})?DE (?:EMPRESA|SERVICOS?)|EMPRESA ESPECIALIZADA|DISPUTA ABERTA|MENOR PRECO|"
                r"ENCOMENDA TECNOLOGICA|FORNECIMENTO DE (?:MATERIA|EQUIPAMENTO|CAIXAS?|MEDICAMENTO|SOLUC|PRODUTO)|LOCACAO E INSTALACAO"),
     "contratação de empresa ou serviço (menor preço, disputa, fornecimento) — não é fomento a OSC", False),
    ("credenciamento_prestadores",
     re.compile(r"CREDENCIAMENTO DE PESSOAS? (?:JURIDICAS?|FISICAS?)(?: E (?:JURIDICAS?|FISICAS?))? PARA (?:A )?PRESTACAO|"
                r"PRESTACAO DE SERVICOS (?:FUNERARIOS|MEDICOS|ODONTOLOGICOS|DE SAUDE|LABORATORIAIS|DE TRANSPORTE|HOSPITALARES)|"
                r"INEXIGIBILIDADE DE LICITACAO N"),
     "credenciamento de prestadores de serviço (Lei 14.133, art. 79) — não é fomento a OSC, mesmo quando pago por fundo", False),
    ("empresas_credenciamento",
     re.compile(r"(?:CHAMAMENTO|CREDENCIAMENTO)[^.]{0,220}(?:EMPRESAS|INSTITUICOES FINANCEIRAS|LEILOEIROS|CORRETORES|AGENCIAS? DE "
                r"VIAGEM|LEILAO|CONSIGNA|PLANOS? DE SAUDE|OPERADORAS?|HOTEIS|LABORATORIOS|CLINICAS)"),
     "chamamento ou credenciamento de empresas e prestadores — não é fomento a OSC", True),
    ("pesquisa_contratada",
     re.compile(r"INSTITUICOES DE ENSINO SUPERIOR[^.]{0,120}FUNDACOES DE APOIO|FUNDACOES DE APOIO A PESQUISA|PESQUISAS? EMPIRICAS|"
                r"AGENCIA NACIONAL DE PESQUISA"),
     "contratação de pesquisa com universidades ou fundações de apoio — não é edital para associação", False),
    ("selecao_familias",
     re.compile(r"SELECAO (?:E INDICACAO )?DE FAMILIAS|FAMILIAS (?:DOMICILIADAS|BENEFICIARIAS|POTENCIALMENTE)|PRE-SELECAO DE FAMILIAS|"
                r"UNIDADES HABITACIONAIS"),
     "seleção de famílias beneficiárias (habitação, programas sociais) — não é recurso para OSC", False),
    ("participacao_publica",
     re.compile(r"COLHER SUBSIDIOS|TOMADA DE SUBSIDIOS|RECEBER CONTRIBUICOES|CONTRIBUICOES (?:SOBRE|PARA) A (?:MINUTA|PROPOSTA|REGULAMENTACAO)"),
     "tomada de subsídios ou coleta de contribuições — participação, não recurso", False),
    ("consulta_publica",
     re.compile(r"CONSULTA PUBLICA|AUDIENCIA PUBLICA"),
     "consulta ou audiência pública — participação, não recurso (o edital definitivo sai depois)", True),
    ("pesquisa_clinica",
     re.compile(r"CHAMAMENTO[^.]{0,160}(?:PARTICIPANTES DE PESQUISA|VOLUNTARIOS PARA PESQUISA|ENSAIO CLINICO)"),
     "chamamento de voluntários de pesquisa — não é recurso para OSC", False),
]
REGIMES_BR = [
    ("doacao_bens", re.compile(r"(?:CHAMAMENTO|EDITAL|AVISO)[^.]{0,260}DOAC|RECEBEREM? (?:POR |EM )?DOACAO|DOACAO (?:DE|DOS) (?:BENS|MATERIAIS|"
                               r"EQUIPAMENTOS|VEICULOS|ALIMENTOS)|INSERVIVEIS|OCIOSOS|ANTIECONOMICOS|DESFAZIMENTO|MERCADORIAS APREENDIDAS|"
                               r"UNIDADES RECEBEDORAS|RECEBIMENTO GRATUITO")),
    ("coleta_seletiva_solidaria", re.compile(r"CATADORES DE MATERIA(?:L|IS)|COLETA SELETIVA SOLIDARIA|5\.940")),
    ("aprendizagem_esfl", re.compile(r"PROGRAMA DE APRENDIZAGEM|CADASTRO NACIONAL D[AE] APRENDIZAGEM|10\.097|JOVE(?:M|NS) APRENDIZ")),
    ("esporte_clubes", re.compile(r"CLUBES? (?:FORMADORES|PARALIMPICOS|ESPORTIVOS)|ENTIDADES? DE PRATICA DESPORTIVA|COMITE BRASILEIRO DE CLUBES|"
                                  r"ENTIDADES? (?:ESPORTIVAS|DESPORTIVAS)")),
    ("patrocinio_estatal", re.compile(r"SELECAO PUBLICA DE (?:PROJETOS|PATROCINIO)|CHAMADA PUBLICA (?:DE|PARA) PATROCINIO|"
                                      r"PATROCINIO (?:CULTURAL|ESPORTIVO|SOCIAL|A PROJETOS)|EDITAL DE PATROCINIO|PROGRAMA DE PATROCINIO")),
    ("cultura_federal", re.compile(r"CULTURA VIVA|13\.018|LEI ROUANET|8\.313|\bPRONAC\b|FUNDO NACIONAL DE CULTURA|PREMIO[^.]{0,60}CULTUR|"
                                   r"FUNARTE|PALMARES|AUDIOVISUAL[^.]{0,40}(?:FOMENTO|SELECAO)")),
    ("esporte_incentivo", re.compile(r"INCENTIVO AO ESPORTE|11\.438|PROJETOS? (?:DESPORTIVOS|PARADESPORTIVOS)")),
    ("saude_incentivo", re.compile(r"\bPRONON\b|\bPRONAS\b")),
]
# tipo de matéria do DOU → o que o classificador comum precisa ver no cabeçalho
ART_RETIFICA = re.compile(r"^(?:AVISO DE )?(?:ALTERACAO|RETIFICACAO|PRORROGACAO|ADIAMENTO|REABERTURA|REPUBLICACAO)")
ART_RESULTADO = re.compile(r"^(?:RESULTADO|AVISO DE (?:HOMOLOGACAO|JULGAMENTO|HABILITACAO|RESULTADO)|ATA\b)")
ART_NORMATIVO = re.compile(r"^(?:PORTARIA|RESOLUCAO|RECOMENDACAO|DELIBERACAO|DECISAO|DESPACHO|ATO\b|DECRETO|INSTRUCAO NORMATIVA|LEI\b|"
                           r"MEDIDA PROVISORIA)")
ART_FECHA = re.compile(r"REVOGACAO|CANCELAMENTO|ANULACAO|SUSPENSAO")
TEXTO_ANDAMENTO = re.compile(r"CONTEMPLAD|ALTERACAO DE REPRESENTANTE|NAO HOUVE INTERPOSICAO DE RECURSO|RESULTADO (?:PRELIMINAR|FINAL)|"
                             r"RESULTADO D[AOE]S? (?:AVALIACAO|ANALISE|SELECAO|JULGAMENTO|HABILITACAO)|MERITO CULTURAL|HOMOLOGA")
TEXTO_FECHA = re.compile(r"\b(?:REVOGA|CANCELA|ANULA|SUSPENDE)\w*\b[^.]{0,60}(?:CHAMAMENTO|CHAMADA|EDITAL)")
_PERIODO_MES = re.compile(r"\b(?:DE|DO DIA|ENTRE OS DIAS|ENTRE)\s+(\d{1,2})\s+(?:A|ATE|E)\s+(?:O DIA\s+)?(\d{1,2})\s+DE\s+([A-Z]+)\s+DE\s+(\d{4})")
_D_BR = r"(\d{1,2}/\d{1,2}/\d{4}|\d{1,2} DE [A-Z]+ DE \d{4})"
_SESSAO = re.compile(r"(?:DATA DE ABERTURA|SESSAO PUBLICA|ABERTURA DOS ENVELOPES|ENTREGA DOS ENVELOPES|ENTREGA DAS PROPOSTAS)[^.]{0,80}?" + _D_BR)
_LEIA_SE = re.compile(r"LEIA-?SE\s*:?(.{0,600})", re.S)
_PERIODO_DM = re.compile(r"(?:A PARTIR DO DIA|DO DIA|DE)\s+\d{1,2}/\d{1,2}\s+(?:AO DIA|A|ATE)\s+(?:O DIA\s+)?(\d{1,2})/(\d{1,2})\s*(?:DE|/)\s*(\d{4})")
_DATA_FINAL = re.compile(r"(?:DATA (?:FINAL|LIMITE)|PRAZO FINAL|ULTIMO DIA|ENCERRAMENTO DAS INSCRICOES)[^0-9]{0,50}(\d{1,2}/\d{1,2}/\d{4})")
_UFS = {"ACRE": "AC", "ALAGOAS": "AL", "AMAPA": "AP", "AMAZONAS": "AM", "BAHIA": "BA", "CEARA": "CE", "ESPIRITO SANTO": "ES",
        "MARANHAO": "MA", "MATO GROSSO DO SUL": "MS", "MATO GROSSO": "MT", "MINAS GERAIS": "MG", "PARAIBA": "PB", "PARANA": "PR",
        "PARA": "PA", "PERNAMBUCO": "PE", "PIAUI": "PI", "RIO DE JANEIRO": "RJ", "RIO GRANDE DO NORTE": "RN", "RIO GRANDE DO SUL": "RS",
        "RONDONIA": "RO", "RORAIMA": "RR", "SANTA CATARINA": "SC", "SAO PAULO": "SP", "SERGIPE": "SE", "TOCANTINS": "TO",
        "GOIAS": "GO", "DISTRITO FEDERAL": "DF", "BRASILIA": "DF"}
_UNIDADE_REGIONAL = re.compile(r"SUPERINTENDENCIA (?:ESTADUAL|REGIONAL)|(?:COORDENACAO|GERENCIA|DIRETORIA|DIVISAO|UNIDADE|ESCRITORIO|"
                               r"SUPERINTENDENCIA|DELEGACIA) REGIONAL|\d+ª? SUPERINTENDENCIA|CAMPUS|GERENCIA EXECUTIVA|"
                               r"SECAO JUDICIARIA|DISTRITO SANITARIO|ESCRITORIO DE REPRESENTACAO|SUREG|FILIAL|DELEGACIA")
_SIGLA_UNIDADE = re.compile(r"\b(?:SE|SR|SUREG|SUPERINTENDENCIA ESTADUAL N\d)\s*[/-]?\s*([A-Z]{2,3})\b")
FUNDOS_BR = re.compile(
    r"CONANDA|\bFNCA\b|FUNDO NACIONAL (?:PARA A |DOS DIREITOS DA |DA )?CRIANCA|FUNDO NACIONAL D[OA] (?:PESSOA )?IDOS|\bFNI\b|\bCNDPI\b|"
    r"FUNDO DE DEFESA DE DIREITOS DIFUSOS|\bFDD\b|\bCFDD\b|FUNDO NACIONAL DO MEIO AMBIENTE|\bFNMA\b|FUNDO NACIONAL DE ASSISTENCIA "
    r"SOCIAL|\bFNAS\b|\bCNAS\b|FUNDO NACIONAL ANTIDROGAS|\bFUNAD\b|FUNDO AMAZONIA")
ORGAOS_BR = [
    ("CONANDA/FNCA", r"CONANDA|\bFNCA\b|DIREITOS DA CRIANCA E DO ADOLESCENTE"),
    ("CNDPI/FNI (pessoa idosa)", r"DIREITOS DA PESSOA IDOSA|\bFNI\b|\bCNDPI\b"),
    ("CNAS/FNAS", r"\bCNAS\b|\bFNAS\b|CONSELHO NACIONAL DE ASSISTENCIA SOCIAL"),
    ("CFDD/FDD (direitos difusos)", r"DIREITOS DIFUSOS|\bCFDD\b"),
    ("MinC (cultura)", r"MINISTERIO DA CULTURA|FUNARTE|FUNDACAO CULTURAL PALMARES|PATRIMONIO HISTORICO|ANCINE|BIBLIOTECA NACIONAL|"
                       r"CASA DE RUI BARBOSA|INSTITUTO BRASILEIRO DE MUSEUS"),
    ("MDS (desenvolvimento e assistência social)", r"DESENVOLVIMENTO E ASSISTENCIA SOCIAL"),
    ("MDHC (direitos humanos)", r"DIREITOS HUMANOS E DA CIDADANIA"),
    ("Ministério do Esporte", r"MINISTERIO DO ESPORTE"),
    ("MMA (meio ambiente)", r"MEIO AMBIENTE E MUDANCA DO CLIMA|CHICO MENDES|\bIBAMA\b|RECURSOS NATURAIS RENOVAVEIS"),
    ("Ministério das Mulheres", r"MINISTERIO DAS MULHERES"),
    ("Ministério da Igualdade Racial", r"IGUALDADE RACIAL"),
    ("Povos Indígenas / FUNAI", r"POVOS INDIGENAS"),
    ("MDA (desenvolvimento agrário)", r"DESENVOLVIMENTO AGRARIO"),
    ("Ministério da Saúde", r"MINISTERIO DA SAUDE"),
    ("MEC (educação)", r"MINISTERIO DA EDUCACAO"),
    ("Ministério da Justiça", r"JUSTICA E SEGURANCA PUBLICA"),
    ("MCTI (ciência e tecnologia)", r"CIENCIA, TECNOLOGIA E INOVACAO"),
    ("Banco ou estatal federal", r"BANCO DA AMAZONIA|BANCO DO NORDESTE|CAIXA ECONOMICA|BANCO DO BRASIL|DESENVOLVIMENTO ECONOMICO E SOCIAL|"
                                 r"PETROBRAS|CORREIOS|ELETROBRAS|ITAIPU|FINANCIADORA DE ESTUDOS"),
    ("Sistema S", r"SERVICO SOCIAL D[AOE]|SERVICO NACIONAL DE APRENDIZAGEM|APOIO AS MICRO E PEQUENAS EMPRESAS"),
    ("Receita Federal", r"RECEITA FEDERAL"),
]
ORGAOS_SOCIAIS = {r for r, _ in ORGAOS_BR} - {"Banco ou estatal federal", "Sistema S", "Receita Federal", "MEC (educação)",
                                                "Ministério da Saúde", "Ministério da Justiça", "MCTI (ciência e tecnologia)"}
_MINUSC = {"De", "Do", "Da", "Dos", "Das", "E"}


def _cfg() -> dict:
    return load_json(CFG) if CFG.exists() else {}


def _em_nuvem() -> bool:
    return bool(os.environ.get("GITHUB_ACTIONS")) and not os.environ.get("ELDORADO_LOCAL_BR")


def _get(url: str, timeout: int = 45, max_bytes: int = 12_000_000) -> str:
    """Lê a página INTEIRA (a Seção 3 passa de 2,5 MB). Corte silencioso é proibido: acima do limite, erro descrito."""
    from urllib.request import Request, urlopen
    validate_public_https(url)
    req = Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/json;q=0.9,*/*;q=0.5",
                                "Accept-Language": "pt-BR,pt;q=0.9"})
    with urlopen(req, timeout=timeout) as r:
        dados = r.read(max_bytes + 1)
    if len(dados) > max_bytes:
        raise ValueError(f"página maior que o limite de {max_bytes // 1_000_000} MB — não lida pela metade")
    return dados.decode("utf-8", "replace")


def _erro(exc: Exception) -> str:
    code = getattr(exc, "code", None)
    nome = type(exc).__name__
    causa = ("bloqueio (HTTP 403) — o portal recusou este endereço" if code == 403 else
             "tempo esgotado" if "Timeout" in nome or "timed out" in str(exc) else
             "conexão derrubada pelo servidor" if nome in ("RemoteDisconnected", "ConnectionResetError") else
             "endereço não resolve (DNS)" if nome == "gaierror" else
             f"HTTP {code}" if code else nome)
    return f"{causa}: {str(exc)[:90]}"


def _get_tentando(url: str, tentativas: int = 3, **kw) -> str:
    ultimo = None
    for i in range(tentativas):
        try:
            return _get(url, **kw)
        except Exception as exc:  # noqa: BLE001 — vira diagnóstico, nunca silêncio
            ultimo = exc
            if getattr(exc, "code", None) in (403, 404) or isinstance(exc, ValueError):
                break
            time.sleep(min(12, 2 * (2 ** i)))
    raise RuntimeError(_erro(ultimo))


# ─────────────────────────── leitura do jornal (Fonte A) ───────────────────────────
_PARAMS = re.compile(r'<script[^>]*\bid="params"[^>]*>(.*?)</script>', re.S)
_PARAMS_BUSCA = re.compile(r'<script[^>]*\bid="_br_com_seatecnologia_in_buscadou_BuscaDouPortlet_params"[^>]*>(.*?)</script>', re.S)


def materias_do_jornal(h: str) -> tuple[list[dict], dict]:
    """HTML da "Leitura do Jornal" → (matérias, edições do dia). Só o `<script id="params">` EXATO conta:
    o portlet de busca da mesma página tem um `{"jsonArray":[]}` vazio que enganava a versão antiga."""
    m = _PARAMS.search(h or "")
    if not m:
        raise ValueError("a página não trouxe o bloco de matérias (params) — layout mudou ou resposta incompleta")
    j = json.loads(m.group(1))
    return list(j.get("jsonArray") or []), dict(j.get("typeNormDay") or {})


def materias_da_busca(h: str) -> list[dict]:
    m = _PARAMS_BUSCA.search(h or "")
    if not m:
        raise ValueError("a página da busca não trouxe o bloco de resultados")
    return list(json.loads(m.group(1)).get("jsonArray") or [])


def url_jornal(d: date, secao: str) -> str:
    return f"{BASE}/leiturajornal?data={d.strftime('%d-%m-%Y')}&secao={secao}"


def url_materia(url_title: str) -> str:
    return f"{BASE}/web/dou/-/{url_title}"


def url_busca(consulta: str, secao: str = "todos", janela: str = "semana", delta: int = 50) -> str:
    return f"{BASE}/consulta/-/buscar/dou?q={quote(consulta)}&s={secao}&exactDate={janela}&sortType=0&delta={delta}"


def _limpo(t: str | None) -> str:
    """A busca do DOU devolve o título com marcação de destaque (<span class='highlight'>CHAMAMENTO</span>)."""
    return re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", "", t or ""))).strip()


def _N(t: str | None) -> str:
    return atos.sem_acento(_limpo(t)).upper()


def territorio_do_item(item: dict) -> tuple[str, str, str | None]:
    """(nível, território, prefeitura) — o DOU publica atos de prefeituras e governos de todo o país."""
    hl = [x for x in (item.get("hierarchyList") or []) if x]
    topo = _N(hl[0]) if hl else ""
    if topo.startswith("PREFEITURAS"):
        uf_ok = len(hl) > 1 and _N(hl[1]).endswith(NOME_UF)
        nome = None
        if len(hl) > 2:
            nome = re.sub(r"(?i)^prefeitura (municipal )?d[eoa]s?\s+", "", hl[2]).strip()
            nome = " ".join(w.lower() if w in _MINUSC else w for w in nome.title().split())
        return ("municipal", f"{UF}/{nome}" if uf_ok and nome else (UF if uf_ok else "fora"), nome)
    if topo.startswith("GOVERNO DO ESTADO"):
        return ("estadual", UF if len(hl) > 1 and _N(hl[1]).endswith(NOME_UF) else "fora", None)
    return ("federal", "BR", None)


def interessa(item: dict) -> tuple[bool, str]:
    """(abrir?, motivo do corte). Só decide o que LER; quem decide se é oportunidade é o classificador."""
    art, tit = _N(item.get("artType")), _N(item.get("title"))
    conteudo, hier = _N(item.get("content")), _N(item.get("hierarchyStr"))
    if TIPO_VETO.search(art) and not TIPO_SALVA.search(art):
        return False, "tipo"
    if HIER_FORA.search(hier):
        return False, "conselho_profissional"
    if territorio_do_item(item)[1] == "fora":
        return False, "fora_territorio"
    secao = str(item.get("pubName") or "")
    if INTERESSE.search(tit + " " + art):
        ok = True
    else:
        ok = bool(INTERESSE.search(conteudo)) and (secao.startswith("DO3") or bool(HIER_SOCIAL.search(hier)))
    if ok and secao.startswith("DO1") and not HIER_SOCIAL.search(hier) and not re.search(r"CHAMAMENTO|FOMENTO|COLABORA|EMENDA",
                                                                                           tit + " " + conteudo):
        ok = False
    return ok, ("" if ok else "sem_termo")


def texto_da_materia(h: str) -> str:
    """Íntegra da matéria: o bloco `texto-dou`, sem o rodapé "Este conteúdo não substitui…"."""
    m = re.search(r'<div class="texto-dou">(.*?)(?:<p class="dou-paragraph">\s*Este conte|</article>|<div class="(?:informacao-conteudo|rodape)|\Z)', h or "", re.S)
    bloco = m.group(1) if m else ""
    bloco = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", bloco)
    bloco = re.sub(r"(?i)<br\s*/?>|</(p|div|tr|li|h\d)>", "\n", bloco)
    t = _html.unescape(re.sub(r"<[^>]+>", " ", bloco))
    t = re.sub(r"[ \t ]+", " ", t)
    return re.sub(r"\n\s*\n+", "\n", t).strip()


def _pascoa(ano: int) -> date:
    a, b, c = ano % 19, ano // 100, ano % 100
    d, e = b // 4, b % 4
    g = (8 * b + 13) // 25
    h = (19 * a + b - d - g + 15) % 30
    j, k = c // 4, c % 4
    m = (a + 11 * h) // 319
    r = (2 * e + 2 * j - k - h + m + 32) % 7
    mes = (h - m + r + 90) // 25
    return date(ano, mes, (h - m + r + mes + 19) % 32)


def _dia_util(d: date) -> bool:
    """Dia com edição normal do DOU: seg–sex, fora dos feriados nacionais fixos e da Sexta-feira Santa."""
    return d.weekday() < 5 and d.strftime("%m-%d") not in FERIADOS_FIXOS and d != _pascoa(d.year) - timedelta(days=2)


def _hoje_brt():
    from datetime import datetime, timezone
    return datetime.now(timezone(timedelta(hours=-3)))


def dias_uteis_sem_dou(hist: dict, hoje: date) -> int:
    """Dias úteis seguidos, até hoje, em que a edição não foi lida (fim de semana e feriado não contam nem zeram)."""
    n, d = 0, hoje
    for _ in range(30):
        if _dia_util(d):
            h = hist.get(d.isoformat())
            if not h or not h.get("sem_edicao"):
                break
            n += 1
        d -= timedelta(days=1)
    return n


def fonte_a(hoje: date, cfg: dict, diag: dict, proc: dict, vistas_url: dict | None = None) -> list[dict]:
    """Edições dos últimos N dias (DO1, DO3 e extras anunciadas) → matérias de interesse com a íntegra."""
    a = cfg.get("fonte_a", {})
    vistas_url = {} if vistas_url is None else vistas_url
    dias = int(a.get("janela_dias", 3)); lim = int(a.get("max_textos_por_dia", 160))
    pausa = float(a.get("pausa_segundos", 0.3)); mb = int(a.get("max_bytes", 12_000_000))
    secoes = list(a.get("secoes") or ["do1", "do3"]); extras = dict(a.get("extras") or {"DO1E": "do1e", "DO3E": "do3e"})
    out, F = [], diag["fontes"]["A"]
    # 03/10 (teste do motor 03): dia útil fora da janela que NUNCA foi lido (ex.: 29/09, perdido na troca para a v2) entra
    # na leitura — até `retroativo_por_execucao` dias por passagem, dentro dos últimos `retroativo_dias`
    ret_dias, ret_max = int(a.get("retroativo_dias", 10)), int(a.get("retroativo_por_execucao", 3))
    janela = [hoje - timedelta(days=k) for k in range(dias)]
    tinha_estado = bool(proc)                                # estado novo (1ª execução, testes): sem retroativo
    atrasados = [] if not tinha_estado else [hoje - timedelta(days=k) for k in range(dias, ret_dias + 1)
                 if _dia_util(hoje - timedelta(days=k)) and f"{(hoje - timedelta(days=k)).isoformat()}|do3" not in proc][:ret_max]
    F["retroativos"] = [d.isoformat() for d in atrasados]
    vistas_antes = set(vistas_url)
    F.setdefault("cortados", 0)
    for d in janela + atrasados:
        fila, vistas, flags, abertos_dia = list(secoes), set(), {}, 0
        while fila:
            sec = fila.pop(0)
            if sec in vistas:
                continue
            vistas.add(sec)
            try:
                itens, fl = materias_do_jornal(_get_tentando(url_jornal(d, sec), max_bytes=mb))
            except Exception as exc:  # noqa: BLE001
                F["falhas"].append(f"{d.isoformat()} {sec}: {exc}"); continue
            flags.update(fl)
            for nome, ok in fl.items():                      # extras anunciadas pelo próprio dia
                if ok and extras.get(nome) and extras[nome] not in vistas:
                    fila.append(extras[nome])
            chave = f"{d.isoformat()}|{sec}"
            F["secoes_lidas"] += 1; F["materias_no_jornal"] += len(itens); F["lidas_ok"].append(chave)
            if itens:
                F["com_materias"].append(chave)
            if proc.get(chave, {}).get("materias") == len(itens):
                continue                                     # edição já processada e sem matéria nova
            sel, cortes = [], {}
            for it in itens:
                ok, porque = interessa(it)
                if ok:
                    sel.append(it)
                else:
                    cortes[porque] = cortes.get(porque, 0) + 1
            for porque, n in cortes.items():
                F["cortes"][porque] = F["cortes"].get(porque, 0) + n
            abertos, falhou, cortados = 0, 0, 0
            for it in sel:
                if d in atrasados and it.get("urlTitle") in vistas_antes:
                    continue                                 # dia retroativo: matéria já vista em outra passagem não se repete
                art = str(it.get("artType") or "")
                tx = None
                if not art.startswith("Extrato") and abertos_dia >= lim and it.get("urlTitle"):
                    cortados += 1                            # 03/10: íntegra além do limite do dia — leitura parcial, não "completa"
                if not art.startswith("Extrato") and abertos_dia < lim and it.get("urlTitle"):
                    try:
                        tx = texto_da_materia(_get_tentando(url_materia(it["urlTitle"]), tentativas=2, max_bytes=3_000_000))
                        abertos += 1; abertos_dia += 1
                        time.sleep(pausa)
                    except Exception as exc:  # noqa: BLE001
                        falhou += 1
                        F["falhas"].append(f"matéria {it.get('urlTitle')}: {exc}")
                if it.get("urlTitle"):
                    vistas_url[it["urlTitle"]] = d.isoformat()
                out.append(_materia(it, tx, "A"))
            F["textos_abertos"] += abertos
            F["cortados"] += cortados
            if falhou or cortados:                           # íntegra que falhou ou ficou além do limite: relida na próxima passagem
                proc.pop(chave, None)
                continue
            proc[chave] = {"data": d.isoformat(), "materias": len(itens), "de_interesse": len(sel), "abertas": abertos,
                           "em": now_iso()}
        F["edicoes_do_dia"][d.isoformat()] = sorted(k for k, v in flags.items() if v)
    F["materias_lidas"] = len(out)
    # o que ainda falta no período: dia útil dos últimos `retroativo_dias` sem a Seção 3 lida (o maestro vê "parcial")
    F["dias_nao_lidos"] = [] if not tinha_estado else [(hoje - timedelta(days=k)).isoformat() for k in range(1, ret_dias + 1)
                           if _dia_util(hoje - timedelta(days=k)) and f"{(hoje - timedelta(days=k)).isoformat()}|do3" not in proc]
    return out


def _materia(it: dict, texto: str | None, fonte: str) -> dict:
    hl = [x for x in (it.get("hierarchyList") or []) if x]
    pub = str(it.get("pubDate") or "")
    m = re.match(r"(\d{2})/(\d{2})/(\d{4})", pub)
    nivel, terr, pref = territorio_do_item(it)
    return {"titulo": _limpo(it.get("title")), "tipo_dou": it.get("artType"), "hierarquia": hl,
            "caminho": " › ".join(hl + ([it["artType"]] if it.get("artType") else [])),
            "texto": texto if texto else _limpo(it.get("content")), "integra": bool(texto),
            "data": f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None, "secao": it.get("pubName"),
            "edicao": it.get("editionNumber"), "pagina": it.get("numberPage"), "url_title": it.get("urlTitle"),
            "url": url_materia(it["urlTitle"]) if it.get("urlTitle") else None, "nivel": nivel, "territorio": terr,
            "prefeitura": pref, "fonte": fonte}


def fonte_b(hoje: date, cfg: dict, diag: dict, ja_vistas: set) -> list[dict]:
    """Busca do DOU (reserva): só o que a Fonte A não trouxe — cobre dia perdido e matéria republicada."""
    b = cfg.get("fonte_b", {})
    if not b.get("usar", True):
        return []
    out, F = [], diag["fontes"]["B"]
    for q in b.get("consultas") or []:
        try:
            itens = materias_da_busca(_get_tentando(url_busca(q, b.get("secao", "todos"), b.get("janela", "semana")),
                                                    tentativas=2, max_bytes=3_000_000))
        except Exception as exc:  # noqa: BLE001
            F["falhas"].append(f"{q[:40]}: {exc}"); continue
        F["consultas"] += 1
        for it in itens:
            if not it.get("urlTitle") or it["urlTitle"] in ja_vistas:
                continue
            ok, _ = interessa(it)
            if not ok:
                continue
            ja_vistas.add(it["urlTitle"])
            tx = None
            if not str(it.get("artType") or "").startswith("Extrato"):
                try:
                    tx = texto_da_materia(_get_tentando(url_materia(it["urlTitle"]), tentativas=2, max_bytes=3_000_000))
                except Exception as exc:  # noqa: BLE001
                    F["falhas"].append(f"matéria {it['urlTitle']}: {exc}")
            out.append(_materia(it, tx, "B"))
        time.sleep(float(b.get("pausa_segundos", 0.5)))
    F["materias_lidas"] = len(out)
    # o que ainda falta no período: dia útil dos últimos `retroativo_dias` sem a Seção 3 lida (o maestro vê "parcial")
    F["dias_nao_lidos"] = [] if not tinha_estado else [(hoje - timedelta(days=k)).isoformat() for k in range(1, ret_dias + 1)
                           if _dia_util(hoje - timedelta(days=k)) and f"{(hoje - timedelta(days=k)).isoformat()}|do3" not in proc]
    return out


# ─────────────────────────── classificação ───────────────────────────
def orgao_do_item(m: dict) -> str | None:
    if m.get("prefeitura"):
        return f"Prefeitura de {m['prefeitura']}"
    H = _N(" / ".join(m.get("hierarquia") or []))
    achado = next(((r, p) for r, p in ORGAOS_BR if re.search(p, H)), None)
    if achado and achado[0] in ("Banco ou estatal federal", "Sistema S"):
        return next((x for x in (m.get("hierarquia") or []) if re.search(achado[1], _N(x))), achado[0])
    if achado:
        return achado[0]
    hl = [x for x in (m.get("hierarquia") or []) if len(x) > 4]     # "…/PE", "…/MA" são siglas de unidade, não órgão
    return hl[-1] if hl else None


def uf_da_unidade(m: dict) -> str | None:
    """Unidade REGIONAL de órgão federal (superintendência, campus, filial…) → a UF dela, pela hierarquia.
    "Correios / … / Superintendência Estadual N4 PB" → PB; "Polícia Federal / Superintendência Regional em São Paulo" → SP."""
    H = _N(" / ".join(m.get("hierarquia") or []))
    if not _UNIDADE_REGIONAL.search(H):
        return None
    for nome in sorted(_UFS, key=len, reverse=True):
        if re.search(r"(?:\bD[OAE]S?|\bN[OA]|\bEM|ESTADO D[OAE]|[-/(])\s*" + nome + r"\b", H):
            return _UFS[nome]
    ms = _SIGLA_UNIDADE.search(H)
    if ms:
        sig = ms.group(1)
        return "DF" if sig == "BSB" else sig if sig in set(_UFS.values()) else None
    return None


_SIGLAS_UF = "AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|TO"   # SE fica de fora: é "Superintendência Estadual" nos Correios
_CIDADE_UF = re.compile(r"(?<=[A-Z]{3})\s*[/-]\s*(" + _SIGLAS_UF + r")\b(?!\s*/)")
REGIMES_LOCAIS = {"doacao_bens", "coleta_seletiva_solidaria"}      # entrega física: só vale perto da associação


def ufs_no_texto(texto: str) -> set[str]:
    """UFs citadas como local ("Passo Fundo/RS", "Brasília-DF", "Estado de Minas Gerais")."""
    T = _N(texto)[:2500]
    ufs = set(_CIDADE_UF.findall(T))
    for nome, sig in _UFS.items():
        if re.search(r"(?:ESTADO D[EOA]|EM|NO|NA)\s+" + nome + r"\b", T):
            ufs.add(sig)
    return ufs


def _prazo_extra(texto: str) -> str | None:
    """Prazos que o classificador comum não lê: "de 14 a 18 de setembro de 2026", "DATA FINAL PARA O ENVIO: 05/10/2026"."""
    T = _N(texto)
    m = _PERIODO_MES.search(T)
    if m and re.search(r"INSCRI|PERIODO|PROPOSTA|RECEB|ENVIO|ENTREGA", T[max(0, m.start() - 160): m.end() + 40]):
        return atos._data_br(f"{m.group(2)} de {m.group(3).lower()} de {m.group(4)}")
    m = _PERIODO_DM.search(T)
    if m and re.search(r"INSCRI|PERIODO|PROPOSTA|RECEB|ENVIO|ENTREGA|PRESENCIAL|REALIZARA", T[max(0, m.start() - 200): m.end() + 60]) \
            and not re.search(r"VIGENCIA", T[max(0, m.start() - 80): m.start()]):
        return atos._data_br(f"{m.group(1)}/{m.group(2)}/{m.group(3)}")
    m = _DATA_FINAL.search(T) or _SESSAO.search(T)
    return atos._data_br(m.group(1).lower()) if m else None


_FECHO = re.compile(r"\n[^\n]{0,60},\s*\d{1,2}(?:º)? DE [A-Z]+ DE \d{4}|\n\s*(?:ONDE SE L|LEIA-?SE)")
_CTX_PRAZO = re.compile(r"INSCRI|PRAZO|PROPOSTA|ENVIO|RECEB|ENTREGA|ENCERRA|ATE\b|PERIODO")


def _prazo_retificado(texto: str) -> str | None:
    """Retificação "Onde se lê: … 29 de outubro … Leia-se: … 22 de outubro" → vale o prazo do LEIA-SE.
    Só o trecho do leia-se (até a linha de local e data ou o próximo "onde se lê"), só com contexto de prazo,
    e do período vale a data FINAL ("de 25/09 a 30/10" → 30/10)."""
    T = _N(texto)
    m = _LEIA_SE.search(T)
    if not m:
        return None
    trecho = m.group(1)
    f = _FECHO.search(trecho)
    trecho = trecho[: f.start()] if f else trecho
    if not _CTX_PRAZO.search(trecho):
        return None
    datas = re.findall(_D_BR, trecho)
    return atos._data_br(datas[-1].lower()) if datas else None


def classificar_materia(m: dict, hoje: date) -> dict:
    """Uma matéria do DOU → veredito do classificador comum, com vetos/regimes/fundos federais e órgão pela hierarquia.
    O tipo da matéria no DOU (artType) entra como cabeçalho: "Aviso de Alteração" é retificação; "Resultado de
    Julgamento" é andamento; Portaria/Resolução que só menciona o edital é ato normativo, não o edital."""
    art = _N(m.get("tipo_dou"))
    prefixo = "RETIFICACAO — " if ART_RETIFICA.search(art) else "RESULTADO FINAL — " if ART_RESULTADO.search(art) else ""
    ato = atos.classificar(m.get("texto") or "", hoje, m.get("data"), titulo=prefixo + (m.get("titulo") or ""),
                           caminho=m.get("caminho"), orgaos=ORGAOS_BR,
                           ambito={"federal": "federal", "estadual": "estadual"}.get(m.get("nivel"), "municipal"),
                           vetos=VETOS_BR, regimes_extra=REGIMES_BR, fundos=FUNDOS_BR)
    ato["orgao"] = orgao_do_item(m) or ato.get("orgao")
    ato["cabecalho"] = re.sub(r"^(?:RETIFICACAO|RESULTADO FINAL) — ", "", ato["cabecalho"])
    if ato["tipo"] == "retificacao":
        fim = _prazo_retificado(m.get("texto") or "")
        if fim:
            ato["fim"], ato["prazo_texto"] = fim, fim
    if not ato["fim"]:
        fim = _prazo_extra(m.get("texto") or "")
        if fim:
            ato["fim"], ato["prazo_texto"] = fim, fim
    if ato["veredito"] == "ACOMPANHAR" and ato["regime"] in ("credenciamento", "credenciamento_cultura") and ato["tipo"] != "abertura":
        ato["veredito"], ato["motivos"] = "RUIDO", ["andamento de credenciamento de prestadores — não é fomento a OSC"]
    elif ato["veredito"] == "RUIDO" and ato["tipo"] == "retificacao" and ato["regime"] == "indefinido" \
            and re.search(r"CHAMAMENTO PUBLICO", _N(m.get("texto"))[:600]) and orgao_do_item(m) in ORGAOS_SOCIAIS:
        ato["veredito"], ato["motivos"] = "ACOMPANHAR", ["retificação de chamamento público de ministério da área social — conferir o edital"]
    _Tx = _N(m.get("texto"))[:1500]
    if ato["veredito"] == "RUIDO" and ato["regime"] in REGIMES_LOCAIS and ato["tipo"] in ("referencia", "abertura") \
            and re.search(r"TORNA PUBLIC\w*[^.]{0,160}DOAC|EDITAL DE DOAC|(?:CHAMAMENTO|AVISO)[^.]{0,120}DOAC", _Tx) \
            and re.search(r"ENTIDADES|SEM FINS LUCRATIVOS|\bOSCS?\b|INSTITUICOES|ORGANIZACOES DA SOCIEDADE CIVIL|ASSOCIACOES", _Tx) \
            and not re.search(r"RESULTADO|HOMOLOGA|CONTEMPLAD|TERMO DE DOACAO CELEBRADO", _Tx[:300]):
        # 03/10 (teste do motor 03): edital de doação de bens a entidades é recurso aberto — segue para a regra de local
        ato["veredito"], ato["tipo"], ato["motivos"] = "OPORTUNIDADE", "abertura", ["edital de doação de bens a entidades sem fins lucrativos"]
    if ato["veredito"] == "ACOMPANHAR" and ato["regime"] in REGIMES_LOCAIS and m.get("nivel") == "federal":
        locais = ufs_no_texto(m.get("texto") or "") | ({uf_da_unidade(m)} - {None})
        if locais and not locais & {UF, "DF"}:
            ato["veredito"], ato["motivos"] = "RUIDO", [f"doação ou coleta com entrega física em {', '.join(sorted(locais))} — fora de Goiás e do DF"]
    if ato["veredito"] != "OPORTUNIDADE":
        return ato
    T = _N(m.get("texto"))[:900]
    uf = uf_da_unidade(m) if m.get("nivel") == "federal" else None
    rebaixa = None
    if ato["fim"] and ato["fim"] < hoje.isoformat():
        rebaixa = ("ACOMPANHAR", f"edital de interesse, mas o prazo escrito ({ato['fim']}) já passou")
    elif ART_FECHA.search(art) or TEXTO_FECHA.search(T):
        rebaixa = ("ACOMPANHAR", "edital revogado, cancelado ou suspenso — não está aberto")
    elif ART_NORMATIVO.search(art):
        rebaixa = ("ACOMPANHAR", f"ato normativo ({m.get('tipo_dou')}) que trata de seleção de interesse — o edital sai à parte; acompanhar")
    elif TEXTO_ANDAMENTO.search(T) and not re.search(r"INSCRICOES (?:SERAO|ESTARAO|ABERTAS)|TORNA PUBLIC\w* A (?:ABERTURA|REABERTURA)", T):
        rebaixa = ("ACOMPANHAR", "andamento de seleção de interesse (contemplados, recurso, resultado) — inscrições encerradas")
    elif uf and uf not in (UF, "DF"):
        rebaixa = ("RUIDO", f"unidade regional de órgão federal em {uf} — a seleção é local, fora de Goiás")
    elif ato["regime"] in REGIMES_LOCAIS and m.get("nivel") == "federal":
        locais = ufs_no_texto(m.get("texto") or "") | ({uf} if uf else set())
        perto = bool(locais & {UF, "DF"}) or bool(re.search(r"GOIAS|GOIANIA|BRASILIA|DISTRITO FEDERAL", _N(" / ".join(m.get("hierarquia") or []))))
        if locais and not perto:
            rebaixa = ("RUIDO", f"doação ou coleta com entrega física em {', '.join(sorted(locais))} — fora de Goiás e do DF")
        elif not perto:
            rebaixa = ("ACOMPANHAR", "doação ou coleta com entrega física sem local identificado no aviso — conferir se é em Goiás ou no DF")
    elif not m.get("integra"):
        rebaixa = ("ACOMPANHAR", "seleção de interesse vista só no trecho do jornal — abrir a íntegra para confirmar prazo e público")
    if rebaixa:
        ato["veredito"], ato["motivos"] = rebaixa[0], [rebaixa[1]]
    return ato


def _chave_orgao(m: dict, ato: dict) -> str:
    """Para deduplicar, o órgão é a HIERARQUIA inteira do DOU: "Comando do Exército" tem dezenas de unidades com
    "Chamamento nº 1/2026" diferentes; a mesma unidade, no aviso e na retificação, tem a mesma hierarquia."""
    base = " / ".join(m.get("hierarquia") or []) or (ato.get("orgao") or "")
    return "h" + sha256(_N(base).encode())[:16]             # chave_ato corta o órgão em 30 letras: o hash não colide


def _chave(ato: dict, m: dict) -> str:
    """Edital: órgão + número (aviso, retificação e resultado se encontram). Extrato sem número: cada matéria é um ato
    próprio — dez extratos de termo de fomento do mesmo órgão no mesmo dia são dez parcerias, não uma."""
    if not ato["numero"] and m.get("url_title"):
        return atos.chave_ato(_chave_orgao(m, ato), None, m["url_title"] + f"#{m.get('ato_n') or 1}", None)
    return atos.chave_ato(_chave_orgao(m, ato), ato["numero"], m.get("titulo") or ato["cabecalho"], m.get("data"))


def _registro(ato: dict, m: dict) -> dict:
    ev = atos.mascarar_pii(re.sub(r"\s+", " ", ((m.get("titulo") or "") + " " + (m.get("texto") or ""))))[:700]
    titulo = " — ".join(x for x in [ato["orgao"] or "Governo Federal", (m.get("titulo") or ato["cabecalho"][:90])[:140],
                                     (ato["objeto"] or "")[:120]] if x)
    nivel, terr = m.get("nivel") or "federal", m.get("territorio") or "BR"
    return {
        "id": sha256(f"dou|{_chave(ato, m)}".encode())[:20],
        "status": "capturada", "titulo": titulo[:300], "url": m.get("url"), "fonte_id": MOTOR_ID,
        "fonte_nome": "Diário Oficial da União", "territorio": terr, "uf": UF if terr != "BR" else None, "nivel": nivel,
        "tipo_fonte": "sensor_diario_oficial", "confianca": "primaria", "forma_divulgacao": "diario_oficial_uniao",
        "coletado_em": now_iso(), "data_publicacao": m.get("data"), "secao_dou": m.get("secao"), "edicao_dou": m.get("edicao"),
        "pagina": m.get("pagina"), "tipo_dou": m.get("tipo_dou"), "numero_edital": ato["numero"],
        "prazo_texto": ato["prazo_texto"], "fim": ato["fim"], "valor_texto": (ato["valores"] or [None])[0],
        "objeto": ato["objeto"], "orgao": ato["orgao"], "regime": ato["regime"], "caminho_sumario": m.get("caminho"),
        "evidencia": ev, "hash_evidencia": sha256(ev.encode()), "fontes_observadas": [m["fonte"]],
        "classificacao_ato": {k: ato[k] for k in ("veredito", "tipo", "regime", "publico", "motivos", "sinais")},
        "sensor": MOTOR_ID, "forca_lexica": 3,
    }


_CAB_LINHA = re.compile(r"^(?:AVISO D[EO]|AVISO$|EDITAL\b|EXTRATO D|RESULTADO D[EOA] (?:JULGAMENTO|HABILITACAO|CHAMAMENTO)|"
                        r"HOMOLOGACAO D|RETIFICACAO\b|ERRATA\b|PORTARIA\b|RESOLUCAO\b|DECRETO\b|TERMO DE\b|ATA DE\b|DESPACHO\b|"
                        r"CHAMAMENTO PUBLICO\b|CHAMADA PUBLICA\b|ADJUDICACAO\b|RATIFICACAO\b)")
_DATA_NA_LINHA = re.compile(r"\d{1,2}/\d{1,2}/\d{2,4}|\d{1,2} DE [A-Z]+ DE \d{4}")


def expandir(materias: list[dict]) -> list[dict]:
    """Uma matéria do DOU pode trazer VÁRIOS atos (Mozarlândia, 18/09: o aviso PNAB e, colado, um aviso de licitação).
    Cada linha de cabeçalho em CAIXA ALTA depois da primeira abre um ato novo — senão o veto de um contamina o outro."""
    out = []
    for m in materias:
        linhas = (m.get("texto") or "").split("\n")
        cortes = [i for i, l in enumerate(linhas) if i > 0 and 8 <= len(l.strip()) <= 140 and l.strip() == l.strip().upper()
                  and _CAB_LINHA.search(_N(l.strip())) and not _DATA_NA_LINHA.search(_N(l))
                  and not re.match(r"\s*(?:ONDE SE L|LEIA-?SE)", _N(l))]
        if not m.get("integra") or not cortes:
            out.append(m); continue
        limites = [0] + cortes + [len(linhas)]
        pedacos = ["\n".join(linhas[limites[k]:limites[k + 1]]).strip() for k in range(len(limites) - 1)]
        while len(pedacos) > 1 and len(pedacos[0]) < 160:     # só o cabeçalho do 1º ato (ex.: "PORTARIA Nº 12…"): junta
            pedacos[:2] = [pedacos[0] + "\n" + pedacos[1]]
        n = 0
        for k, pedaco in enumerate(pedacos):
            if len(pedaco) < 60:
                continue
            n += 1
            out.append(dict(m, texto=pedaco, titulo=m.get("titulo") if k == 0 else pedaco.split("\n", 1)[0].strip(),
                            tipo_dou=m.get("tipo_dou") if k == 0 else None, ato_n=n))
    return out


def classificar_lote(materias: list[dict], hoje: date) -> tuple[dict, dict, dict]:
    """→ ({id: OPORTUNIDADE}, {id: ACOMPANHAR}, contagens), deduplicados; resultado ou prazo vencido em outra
    matéria do mesmo edital fecha a oportunidade."""
    oport, acomp = {}, {}
    cont = {"OPORTUNIDADE": 0, "ACOMPANHAR": 0, "RUIDO": 0, "quarentena": 0}
    andamento, retificados = set(), {}
    for m in expandir(materias):
        bruto = (m.get("titulo") or "") + "\n" + (m.get("texto") or "")
        if has_prompt_injection(bruto):
            append_jsonl(QUARENTENA, {"origem": MOTOR_ID, "url": m.get("url"), "em": now_iso(), "hash": sha256(bruto.encode())[:16]})
            cont["quarentena"] += 1; continue
        ato = classificar_materia(m, hoje)
        cont[ato["veredito"]] += 1
        if ato["tipo"] == "retificacao" and ato["numero"] and ato["fim"]:
            ch = sha256(f"dou|{atos.chave_ato(_chave_orgao(m, ato), ato['numero'], None, None)}".encode())[:20]
            retificados[ch] = max(retificados.get(ch, ""), ato["fim"])
        if ato["veredito"] == "RUIDO":
            continue
        reg = _registro(ato, m)
        alvo = oport if ato["veredito"] == "OPORTUNIDADE" else acomp
        if ato["tipo"] == "andamento":
            andamento.add(reg["id"])                             # mesmo quando se funde a um registro já visto
        if reg["id"] in alvo:
            ant = alvo[reg["id"]]
            ant["fontes_observadas"] = sorted(set(ant["fontes_observadas"]) | {m["fonte"]})
            ant["fim"] = ant.get("fim") or reg["fim"]
            continue
        alvo[reg["id"]] = reg
    for i, r in oport.items():                                   # "onde se lê … leia-se": o prazo retificado vale
        novo = retificados.get(i)
        if novo and novo != r.get("fim"):
            r["fim"] = r["prazo_texto"] = novo
            r["classificacao_ato"]["motivos"] = r["classificacao_ato"]["motivos"] + [f"prazo retificado no DOU para {novo}"]
    for i in list(oport):
        if oport[i].get("fim") and oport[i]["fim"] < hoje.isoformat():
            r = oport.pop(i)
            r["classificacao_ato"]["veredito"] = "ACOMPANHAR"
            r["classificacao_ato"]["motivos"] = [f"prazo retificado ({r['fim']}) já passou"]
            acomp[i] = r; cont["OPORTUNIDADE"] -= 1; cont["ACOMPANHAR"] += 1
            continue
        a = acomp.get(i)
        if not a:
            continue
        vencido = bool(a.get("fim")) and a["fim"] < hoje.isoformat()
        if vencido or i in andamento:
            r = oport.pop(i)
            r["classificacao_ato"]["veredito"] = "ACOMPANHAR"
            r["classificacao_ato"]["motivos"] = [("prazo escrito em outra publicação já passou (" + a["fim"] + ")") if vencido
                                                 else "a seleção já tem resultado publicado — inscrições encerradas"]
            acomp[i] = r
            cont["OPORTUNIDADE"] -= 1; cont["ACOMPANHAR"] += 1
    return oport, acomp, cont


# ─────────────────────────── o motor ───────────────────────────
def ler_motor(sensor: dict | None = None, hoje: date | None = None, limites: dict | None = None) -> dict:
    """Leitura do motor 03 com a mesma saída de `sensores.ler` (inclusive `dou_json_materias` para o painel)."""
    hoje = hoje or (sensor or {}).get("_data") or _hoje_brt().date()   # 03/10: o dia é o de Brasília (o executor roda em UTC)
    cfg = _cfg()
    est = load_json(ESTADO) if ESTADO.exists() else {}
    proc = est.setdefault("edicoes_processadas", {})
    diag = {"paginas_lidas": 0, "links_total": 0, "links_candidatos": 0, "descobertas": [], "pdf_links": 0, "motivo_zero": None,
            "versao": "motor-03 v2 (01/10/2026)", "nuvem": _em_nuvem(),
            "fontes": {"A": {"falhas": [], "materias_lidas": 0, "secoes_lidas": 0, "materias_no_jornal": 0, "textos_abertos": 0,
                             "cortes": {}, "edicoes_do_dia": {}, "lidas_ok": [], "com_materias": []},
                       "B": {"falhas": [], "materias_lidas": 0, "consultas": 0}}}
    corte = (hoje - timedelta(days=120)).isoformat()
    vistas_url = {k: v for k, v in (est.get("materias_vistas") or {}).items() if v >= (hoje - timedelta(days=10)).isoformat()}
    materias = []
    try:
        materias += fonte_a(hoje, cfg, diag, proc, vistas_url)
    except Exception as exc:  # noqa: BLE001 — uma fonte nunca derruba a outra
        diag["fontes"]["A"]["falhas"].append(f"etapa: {_erro(exc)}")
    try:
        ja = set(vistas_url) | {m["url_title"] for m in materias if m.get("url_title")}
        materias += fonte_b(hoje, cfg, diag, ja)
    except Exception as exc:  # noqa: BLE001
        diag["fontes"]["B"]["falhas"].append(f"etapa: {_erro(exc)}")
    oport, acomp, cont = classificar_lote(materias, hoje)
    A = diag["fontes"]["A"]
    diag["vereditos"] = cont
    diag["dou_json_materias"] = A["materias_no_jornal"]
    diag["paginas_lidas"] = A["secoes_lidas"] + A["textos_abertos"]
    diag["links_total"] = A["materias_no_jornal"]
    diag["links_candidatos"] = len(materias)
    # 03/10: chaves que o maestro lê como leitura PARCIAL (src/maestro.py · CORTE) → acionamento complementar no mesmo dia
    if A.get("dias_nao_lidos"):
        diag["paginas_nao_lidas"] = [url_jornal(date.fromisoformat(x), "do3") for x in A["dias_nao_lidos"]]
    if A.get("cortados"):
        diag["cortados"] = A["cortados"]
    # edição do dia não lida em dia útil = FALHA (não é "azul, funcionou sem oportunidade")
    d0 = hoje.isoformat()
    do3_hoje = f"{d0}|do3" in A["com_materias"]
    cedo = hoje == _hoje_brt().date() and _hoje_brt().hour < 8          # a edição do dia sai no começo da manhã
    sem_edicao_hoje = _dia_util(hoje) and not cedo and not do3_hoje
    hist = est.setdefault("historico", {})
    ant = hist.get(d0) or {}
    novo = {"secoes": A["secoes_lidas"], "materias": A["materias_no_jornal"], "abertas": A["textos_abertos"], **cont}
    # 3 passagens por dia: a 2ª e a 3ª pulam a edição já processada — o histórico guarda o MAIOR de cada contador
    hist[d0] = {k: max(int(ant.get(k) or 0), int(v)) for k, v in novo.items()} | {
        "sem_edicao": bool(sem_edicao_hoje and ant.get("sem_edicao", True))}
    seq = dias_uteis_sem_dou(hist, hoje)                                  # por DIA, não por execução (3 passagens/dia)
    est["dias_uteis_sem_dou"] = seq
    if seq >= 2:
        diag["alerta"] = f"{seq} dias úteis seguidos sem ler a edição do DOU — conferir a rede e o layout da Leitura do Jornal"
    # as passagens seguintes do mesmo dia repetem as oportunidades já achadas hoje (o dia não "desbota" para azul)
    do_dia = est.get("oportunidades_do_dia") or {}
    if do_dia.get("data") != hoje.isoformat():
        do_dia = {"data": hoje.isoformat(), "registros": []}
    do_dia["registros"] = [r for r in do_dia["registros"] if r["id"] not in acomp]   # fechada nesta passagem: sai
    ja = {r["id"] for r in do_dia["registros"]}
    do_dia["registros"] += [r for r in oport.values() if r["id"] not in ja]
    for r in do_dia["registros"]:
        oport.setdefault(r["id"], r)
    est["oportunidades_do_dia"] = do_dia
    est["materias_vistas"] = vistas_url | {m["url_title"]: (m.get("data") or d0) for m in materias if m.get("url_title")}
    novos = [{k: a[k] for k in ("id", "titulo", "url", "data_publicacao", "fim", "orgao", "regime", "objeto", "valor_texto",
                                "fontes_observadas", "territorio")} | {"motivo": a["classificacao_ato"]["motivos"][0],
                                                                      "tipo": a["classificacao_ato"]["tipo"]}
             for a in acomp.values()]
    ids = {a["id"] for a in novos}
    est["acompanhar"] = (novos + [a for a in est.get("acompanhar", []) if a["id"] not in ids
                                  and (a.get("data_publicacao") or "") >= corte])[:500]
    est["edicoes_processadas"] = {k: v for k, v in proc.items() if (v.get("data") or "") >= corte}
    est["ultima"] = {"em": now_iso(), "data": hoje.isoformat(), "vereditos": cont, "cortes": A["cortes"],
                     "edicoes_do_dia": A["edicoes_do_dia"], "falhas": (A["falhas"] + diag["fontes"]["B"]["falhas"])[:10]}
    est["historico"] = {k: v for k, v in hist.items() if k >= corte}
    write_json(ESTADO, est)
    falhas = [{"url": BASE + "/leiturajornal", "erro": "secao_nao_lida", "code": None, "waf": None, "causa": f}
              for f in A["falhas"] if not f.startswith("matéria ")][:6]
    if sem_edicao_hoje:
        causa = next((f for f in A["falhas"] if f.startswith(d0)), "a Leitura do Jornal respondeu sem matérias em dia útil")
        falhas.insert(0, {"url": url_jornal(hoje, "do3"), "erro": "edicao_nao_lida", "code": None, "waf": None, "causa": causa})
    # saúde só com o que foi lido de fato; DO3 de dia útil não lida → sem saúde (o dia fica vermelho, não azul)
    saude = [] if sem_edicao_hoje else [{"url": url_jornal(date.fromisoformat(k.split("|")[0]), k.split("|")[1]), "http": 200,
                                         "bytes": 0} for k in A["lidas_ok"]][:6]
    if not oport:
        diag["motivo_zero"] = (f"{A['materias_no_jornal']} matérias no jornal, {len(materias)} de interesse "
                               f"({A['textos_abertos']} íntegras): nenhuma seleção aberta para OSC hoje · "
                               f"{cont['ACOMPANHAR']} a acompanhar · {cont['RUIDO']} ruído"
                               if A["secoes_lidas"] else "a edição não foi lida: " + (falhas[0]["causa"] if falhas else "sem leitura"))
    return {"sensor": MOTOR_ID, "achados": list(oport.values()), "falhas": falhas, "saude": saude,
            "diagnostico": diag, "lido_em": now_iso()}


def atos_para_painel(limite: int = 12) -> list[dict]:
    est = load_json(ESTADO) if ESTADO.exists() else {}
    return sorted(est.get("acompanhar", []), key=lambda a: str(a.get("data_publicacao") or ""), reverse=True)[:limite]


if __name__ == "__main__":
    print(json.dumps(ler_motor()["diagnostico"], ensure_ascii=False, indent=2))
