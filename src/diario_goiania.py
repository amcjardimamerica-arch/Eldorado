"""MOTOR 01 — Diário Oficial do Município de Goiânia (versão 2, 01/10/2026).

Parecer do conselho de 01/10/2026 (docs/pareceres/motor-01-diario-goiania.md). O que mudou e por quê:

1. O motor antigo lia o RÓTULO dos links de uma página de serviço. A edição do Diário de Goiânia é
   um PDF inteiro (≈240 páginas); o rótulo é "Edição nº 8871 de 25 de setembro de 2026" e nunca casa
   com léxico nenhum. O chamamento está DENTRO do PDF. Resultado: 43 leituras, 0 achados.
2. A URL configurada (`/diario-oficial/`) é a Carta de Serviços, não o Diário. A lista real das
   edições é `shtml//portal/casacivil/lista_diarios.asp?ano=AAAA` e cada edição tem endereço
   determinístico: `Download/legislacao/diariooficial/AAAA/do_AAAAMMDD_NNNNNNNNN.pdf`.
3. O Querido Diário (Open Knowledge Brasil) JÁ indexa Goiânia (IBGE 5208707), com 2 a 16 dias de
   atraso (mediana 5,5 dias em set/2026), e é acessível da nuvem. A base tinha 232 edições de Goiânia vindas dele — todas
   descartadas pelo painel como "edição de diário não é oportunidade", sem abrir o ato.

Como funciona agora (sem IA, sem tokens, biblioteca-padrão; pypdf só quando houver PDF):

    Querido Diário (nuvem, todo dia, janela de 15 dias, consultas dirigidas ao território)
      + edição direta do portal (coleta local no Brasil, quando o titular roda a coleta)
          → texto integral da edição → recorte em ATOS pelo cabeçalho
          → classificação determinística de cada ato:
                tipo (abertura · retificação · andamento/resultado · celebração · referência)
                regime (MROSC · fundos/conselhos · PNAB/cultura · credenciamento · OS saúde)
                público (OSC · pessoa física · empresa/clínica)
          → OPORTUNIDADE (abertura para OSC, prazo não vencido) entra na base como `capturada`;
            ACOMPANHAR (resultado, extrato de termo, inexigibilidade, retificação de edital de interesse)
            vai para o painel como inteligência; RUÍDO é só contado.

Conteúdo coletado é DADO: trecho com injeção vai para a quarentena; CPF é mascarado antes de gravar;
nada é inventado — o que o texto não diz fica `null`.
"""
from __future__ import annotations

import io
import json
import os
import re
import time
import unicodedata
from datetime import date, datetime, timedelta
from html.parser import HTMLParser
from urllib.parse import urlencode, urljoin, urlsplit

from .nucleo import (ROOT, append_jsonl, has_prompt_injection, load_json, now_iso, sha256,
                     validate_public_https, write_json)

MOTOR_ID = "do-goiania"
IBGE = "5208707"
PORTAL = "https://www.goiania.go.gov.br"
LISTA = PORTAL + "/shtml//portal/casacivil/lista_diarios.asp?ano={ano}"
EDICAO_PDF = re.compile(r"/Download/legislacao/diariooficial/(\d{4})/do_(\d{8})_(\d{9})\.pdf", re.I)
CFG = ROOT / "config/diario_goiania.json"
ESTADO = ROOT / "estado/diario_goiania.json"
CACHE = ROOT / "estado/edicoes/goiania"          # fora do Git (.gitignore: estado/edicoes/)
QUARENTENA = ROOT / "estado/quarentena.jsonl"

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 Eldorado-OSC/1.0"


# ───────────────────────────── utilidades ─────────────────────────────
def _sem_acento(t: str) -> str:
    t = unicodedata.normalize("NFKD", t or "")
    return "".join(c for c in t if not unicodedata.combining(c))


def _cfg() -> dict:
    return load_json(CFG) if CFG.exists() else {}


def _em_nuvem() -> bool:
    return bool(os.environ.get("GITHUB_ACTIONS")) and not os.environ.get("ELDORADO_LOCAL_BR")


def _get(url: str, timeout: int = 60, max_bytes: int = 8_000_000, aceitar: str = "*/*") -> bytes:
    from urllib.request import Request, urlopen
    if not url.startswith("file://"):
        validate_public_https(url)
    req = Request(url, headers={"User-Agent": UA, "Accept": aceitar, "Accept-Language": "pt-BR,pt;q=0.9"})
    with urlopen(req, timeout=timeout) as r:
        dados = r.read(max_bytes + 1)
    if len(dados) > max_bytes:
        raise ValueError("resposta excede limite")
    return dados


def _get_json(url: str, timeout: int = 60, tentativas: int = 2) -> dict:
    """GET com nova tentativa e erro DESCRITO (o coletor metropolitano falhava 147 de 147
    consultas registrando só 'sem resposta das bases')."""
    ultimo = None
    for i in range(tentativas):
        try:
            return json.loads(_get(url, timeout=timeout, aceitar="application/json").decode("utf-8", "replace"))
        except Exception as exc:  # noqa: BLE001 — o erro vira diagnóstico, não silêncio
            ultimo = exc
            time.sleep(min(20, 2.5 * (2 ** i)))         # espera crescente: 2,5 · 5 · 10 · 20 s
    code = getattr(ultimo, "code", None)
    raise RuntimeError(f"{type(ultimo).__name__}{f' HTTP {code}' if code else ''}: {str(ultimo)[:120]}")


_CPF = re.compile(r"(?<![\d*])[\d*]{3}\.[\d*]{3}\.[\d*]{3}-[\d*]{2}(?![\d*])")


def mascarar_pii(t: str) -> str:
    """CPF (inteiro ou parcialmente mascarado) sai do trecho antes de ir para o Git público."""
    return _CPF.sub("[CPF]", t or "")


# ───────────────────────────── 1. lista de edições do portal ─────────────────────────────
class _Ancoras(HTMLParser):
    def __init__(self):
        super().__init__(); self.itens = []; self._h = None; self._t = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._h = dict(attrs).get("href"); self._t = []

    def handle_data(self, data):
        if self._h is not None:
            self._t.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._h is not None:
            self.itens.append((self._h, " ".join(self._t).strip())); self._h = None


def edicoes_da_lista(html: str, base: str = PORTAL + "/") -> list[dict]:
    """Lê a lista anual do portal e devolve [{data, numero, extra, url, rotulo}] (mais recente primeiro)."""
    p = _Ancoras(); p.feed(html or "")
    out, vistos = [], set()
    for href, rot in p.itens:
        u = urljoin(base, href or "")
        m = EDICAO_PDF.search(u)
        if not m or u in vistos:
            continue
        vistos.add(u)
        d = m.group(2)
        out.append({"data": f"{d[:4]}-{d[4:6]}-{d[6:]}", "numero": int(m.group(3)), "url": u,
                    "extra": bool(re.search(r"extra|suplement", rot or "", re.I)), "rotulo": (rot or "")[:90]})
    return sorted(out, key=lambda e: (e["data"], e["numero"]), reverse=True)


def url_oficial(data_iso: str, numero) -> str | None:
    """Endereço da edição no portal, pelo padrão observado em 01/10/2026 na lista oficial."""
    try:
        n = int(str(numero).strip())
        d = date.fromisoformat(str(data_iso)[:10])
    except (TypeError, ValueError):
        return None
    return f"{PORTAL}/Download/legislacao/diariooficial/{d.year}/do_{d.strftime('%Y%m%d')}_{n:09d}.pdf"


def texto_do_pdf(dados: bytes) -> str | None:
    try:
        from pypdf import PdfReader
    except Exception:  # pragma: no cover — coleta local sem pypdf
        return None
    try:
        leitor = PdfReader(io.BytesIO(dados))
        return "\n".join((pg.extract_text() or "") for pg in leitor.pages)
    except Exception:
        return None


# ───────────────────────────── 2. recorte em atos ─────────────────────────────
# Cabeçalho de ato: linha em CAIXA ALTA que abre a matéria. A menção em caixa baixa
# ("no Edital de Chamamento Público nº 1/2026") NÃO abre ato — é referência dentro de outro.
_CABECALHO = re.compile(
    r"(?m)^[ \t]*(?:"
    r"EDITAL(?: DE [A-ZÇÃÕÁÉÍÓÚÊÔ ]{3,60})?|AVISO(?: DE [A-ZÇÃÕÁÉÍÓÚÊÔ ]{3,60})?|CHAMADA P[ÚU]BLICA|"
    r"EXTRATO(?: D[OAE]S? [A-ZÇÃÕÁÉÍÓÚÊÔ ]{3,60})?|TERMO DE (?:FOMENTO|COLABORA[ÇC][ÃA]O|ADITAMENTO|HOMOLOGA[ÇC][ÃA]O)|"
    r"RESULTADO(?: [A-ZÇÃÕÁÉÍÓÚÊÔ ]{3,40})?|HOMOLOGA[ÇC][ÃA]O|RETIFICA[ÇC][ÃA]O|ERRATA|"
    r"RESOLU[ÇC][ÃA]O|PORTARIA|DECRETO|DESPACHO|LEI(?: COMPLEMENTAR)?|INSTRU[ÇC][ÃA]O NORMATIVA|ATA(?: DE [A-ZÇÃÕÁÉÍÓÚÊÔ ]{3,60})?|"
    r"JUSTIFICATIVA DE (?:INEXIGIBILIDADE|DISPENSA)|INEXIGIBILIDADE|DISPENSA DE CHAMAMENTO"
    r")\b[^\n]{0,180}")

_INTERESSE = re.compile(
    r"chamamento|chamada p[uú]blica|termo de fomento|termo de colabora|13\.019|sociedade civil|\bosc\b|"
    r"cmdca|fmdca|\bcmas\b|\bfmas\b|fundo municipal|conselho municipal|aldir blanc|\bpnab\b|paulo gustavo|"
    r"subven[cç][aã]o social|emenda impositiva|emenda parlamentar|entidades? sem fins lucrativos|inexigibilidade|"
    r"dispensa de chamamento|edital de sele[cç][aã]o|plano de trabalho", re.I)


def recortar_atos(texto: str, janela: int = 7000, maximo: int = 60) -> list[str]:
    """Divide a edição em matérias pelo cabeçalho; devolve só as que tocam o terceiro setor."""
    if not texto:
        return []
    marcas = [m.start() for m in _CABECALHO.finditer(texto)]
    if not marcas:
        marcas = [0]
    if marcas[0] > 0:
        marcas.insert(0, 0)
    atos, vistos = [], set()
    pendente = None                      # cabeçalho curto ("EDITAL… Nº 001/2026" + título) junta-se ao seguinte
    for i, ini in enumerate(marcas):
        fim = marcas[i + 1] if i + 1 < len(marcas) else len(texto)
        if pendente is None:
            pendente = ini
            # timbre logo acima do cabeçalho (órgão, diretoria) entra no ato — até a linha do CEP/assinatura anterior
            antes = texto[max(0, ini - 500):ini].split("\n")
            timbre = []
            for linha in reversed(antes[-7:]):
                if (re.search(r"CEP|CRC|autenticidade|assinad[oa] eletronicamente|https?://", linha, re.I)
                        or _CABECALHO.match(linha) or linha.rstrip().endswith((".", ";", ":")) or len(linha) > 110):
                    break                # timbre é linha curta de órgão/diretoria — não frase nem outro ato
                timbre.insert(0, linha)
            cab_timbre = "\n".join(timbre).strip()
        if fim - pendente < 400 and i + 1 < len(marcas):
            w1 = texto[pendente:pendente + 12].strip().split(" ")[0].upper()
            w2 = texto[fim:fim + 12].strip().split(" ")[0].upper()
            if w1 == w2 and w1 in ("EDITAL", "AVISO", "CHAMADA"):
                continue                 # o título repetido do mesmo edital ("EDITAL… Nº 001/2026" / "EDITAL…")
        trecho = ((cab_timbre + "\n") if cab_timbre else "") + texto[pendente:min(fim, pendente + janela)].strip()
        pendente = None
        if len(trecho) < 60 or not _INTERESSE.search(trecho):
            continue
        k = sha256(re.sub(r"\s+", " ", trecho[:500]).lower().encode())[:16]
        if k in vistos:
            continue
        vistos.add(k); atos.append(trecho)
        if len(atos) >= maximo:
            break
    return atos


# ───────────────────────────── 3. classificação determinística ─────────────────────────────
_ORGAOS = [  # (rótulo, padrão) — a ordem importa: o conselho/fundo vence a secretaria-mãe
    ("CMDCA/FMDCA", r"CMDCA|FMDCA|DIREITOS DA CRIANCA|FUNDO DA INFANCIA|\bFIA\b"),
    ("CMAS/FMAS", r"\bCMAS\b|\bFMAS\b|CONSELHO MUNICIPAL DE ASSISTENCIA SOCIAL|FUNDO MUNICIPAL DE ASSISTENCIA SOCIAL"),
    ("CMI/FMI (idoso)", r"\bCMI\b|\bFMI\b|CONSELHO MUNICIPAL DO IDOSO|FUNDO MUNICIPAL DO IDOSO|DIREITOS DA PESSOA IDOSA"),
    ("SECULT (cultura)", r"SECRETARIA MUNICIPAL DE CULTURA|\bSECULT\b|ALDIR BLANC|\bPNAB\b|PAULO GUSTAVO|PONTOS? DE CULTURA"),
    ("SEDHS (desenvolvimento humano e social)", r"DESENVOLVIMENTO HUMANO E SOCIAL|\bSEDHS\b|\bSEMAS\b|\bSEMASDH\b"),
    ("SEGENP (gestão de negócios e parcerias)", r"GESTAO DE NEGOCIOS E PARCERIAS|\bSEGENP\b|\bSEGNEP\b"),
    ("SME (educação)", r"SECRETARIA MUNICIPAL DE EDUCACAO|\bSME\b"),
    ("SMS (saúde)", r"SECRETARIA MUNICIPAL DE SAUDE|\bSMS\b|FUNDO MUNICIPAL DE SAUDE"),
    ("Esportes (SEMEL)", r"ESPORTE E LAZER|SECRETARIA MUNICIPAL DOS? ESPORTES?|\bSEMEL\b|\bSECEL\b"),
    ("Relações Institucionais (emendas)", r"RELACOES INSTITUCIONAIS|\bSRI\b"),
    ("AGETUL (turismo)", r"\bAGETUL\b|TURISMO, EVENTOS E LAZER"),
    ("Câmara Municipal (emendas)", r"EMENDA IMPOSITIVA|EMENDA PARLAMENTAR"),
]
_RX = {
    "resultado": re.compile(r"RESULTADO (?:PRELIMINAR|FINAL|DEFINITIVO|PROVISORIO)|HOMOLOGA|CLASSIFICACAO (?:FINAL|PRELIMINAR)|"
                            r"ATA DE (?:ANALISE|JULGAMENTO|SELECAO)|RECURSOS? (?:INTERPOSTOS?|ADMINISTRATIVO)|"
                            r"RELACAO DOS PROPONENTES|HABILITAD[AO]S|INABILITAD[AO]S|DEFERID[AO]S|INDEFERID[AO]S|"
                            r"RESULTADO D[AOE]S? (?:ANALISE|AVALIACAO|SELECAO|JULGAMENTO|PROCESSOS?)|EM GRAU DE RECURSO|MERITO CULTURAL"),
    "celebracao": re.compile(r"EXTRATO D[OAE]S? (?:TERMO|CONVENIO|ACORDO|PARCERIA)|TERMO ADITIVO|INEXIGIBILIDADE|DISPENSA DE CHAMAMENTO|"
                             r"CELEBRACAO DE (?:TERMO|PARCERIA)"),
    "retificacao": re.compile(r"RETIFICA|ERRATA|PRORROGA|REABERTURA|ADIAMENTO"),
    "abertura": re.compile(r"(?:EDITAL|AVISO) DE CHAMAMENTO|CHAMADA PUBLICA|EDITAL DE SELECAO|"
                           r"TORNA PUBLIC[OA][^.]{0,160}(?:ABERTURA|INSCRIC|SELECAO DE (?:PROJETOS|PROPOSTAS|ORGANIZACOES|ENTIDADES))|"
                           r"(?:ABERTURA|PERIODO) DE INSCRIC|AS INSCRICOES (?:SERAO|ESTARAO|PODERAO)"),
    # no CORPO (sem cabeçalho) só vale abertura com verbo de abertura — "sobre o edital…" é referência
    "abertura_corpo": re.compile(r"TORNA PUBLIC[OA][^.]{0,160}(?:ABERTURA|INSCRIC|SELECAO DE (?:PROJETOS|PROPOSTAS|ORGANIZACOES|ENTIDADES))|"
                                 r"(?:ABERTURA|PERIODO) DE INSCRIC|AS INSCRICOES (?:SERAO|ESTARAO|PODERAO|FICAM ABERTAS)"),
    # regime / público
    "mrosc": re.compile(r"13\.019|SOCIEDADE CIVIL|\bOSCS?\b|MROSC|TERMO DE (?:FOMENTO|COLABORACAO)|ENTIDADES? SEM FINS LUCRATIVOS|"
                        r"ENTIDADES? (?:SOCIOASSISTENCIA|PRIVADAS SEM)"),
    "fundo": re.compile(r"CMDCA|FMDCA|\bCMAS\b|\bFMAS\b|FUNDO MUNICIPAL D[OEA]S? (?:DIREITOS|ASSISTENCIA|IDOSO|CULTURA|CRIANCA)|\bFIA\b"),
    "cultura": re.compile(r"ALDIR BLANC|\bPNAB\b|PAULO GUSTAVO|14\.399|PONTOS? DE CULTURA|FOMENTO A CULTURA"),
    "credenciamento": re.compile(r"CREDENCIAMENTO|ART(?:IGO)?\.? ?25[^.]{0,40}8\.666|14\.133[^.]{0,40}ART(?:IGO)?\.? ?79|"
                                 r"PRESTAD(?:OR|ORES) DE SERVICOS? (?:MEDIC|DE SAUDE)|CONTRATO AUTONOMO|INEXIGIBILIDADE DE LICITACAO"),
    "os_saude": re.compile(r"8\.411|QUALIFICAD[AO] COMO ORGANIZACAO SOCIAL|ORGANIZACAO SOCIAL (?:NA AREA|DE SAUDE|NO AMBITO)|CONTRATO DE GESTAO"),
    "pessoa_fisica": re.compile(r"PESSOA FISICA|PESSOAS FISICAS|PROFISSIONAIS? (?:MEDIC|DE SAUDE)|GUIAS? DE TURISMO|INFLUENCIADORES"),
    "empresa": re.compile(r"\bLTDA\b|\bEIRELI\b|\bS/?A\b|CLINICAS?|LABORATORIOS?|EMPRESAS? (?:DO RAMO|ESPECIALIZADA)"),
    "conselho_composicao": re.compile(r"PROCESSO ELEITORAL|COMPOSICAO DO CONSELHO|ELEICAO D[AO]S? (?:CONSELHEIR|SOCIEDADE CIVIL)|"
                                      r"INTEGRAR O CONSELHO|REPRESENTANTES DA SOCIEDADE CIVIL|POSSE D[OA]S? CONSELHEIR"),
}
_CAB_CORPO = re.compile(r"\b(?:EDITAL|AVISO|CHAMADA P[ÚU]BLICA|EXTRATO|RESULTADO|HOMOLOGA[ÇC][ÃA]O|RETIFICA[ÇC][ÃA]O|ERRATA|"
                        r"RESOLU[ÇC][ÃA]O|PORTARIA|DECRETO|DESPACHO|ATA DE|TERMO DE|TERMO ADITIVO|JUSTIFICATIVA|"
                        r"INEXIGIBILIDADE|LEI N|INSTRU[ÇC][ÃA]O NORMATIVA)\b")
_NUM_CHAM = re.compile(r"CHAMAMENTO PUBLICO\s*(?:N\W{0,3})?\s*(\d{1,4}\s*/\s*20\d{2})")
_NUM = re.compile(r"N[º°o.]?\s*(?:º\s*)?(\d{1,4}\s*/\s*20\d{2})", re.I)
_OBJETO = re.compile(r"(?:DO\s+)?OBJETO\s*[:\-–.]?\s*(.{25,420}?)(?:\.\s|\n\s*\n|$)", re.I | re.S)
_FIM = re.compile(r"(?:at[ée]\s+(?:o\s+dia\s+|as\s+\d{1,2}h\d{0,2}\s+(?:min\s+)?do\s+dia\s+)?|prazo\s+final[^.\d]{0,30}|encerra\w*[^.\d]{0,30}|"
                  r"inscri[çc][õo]es[^.\d]{0,60}?(?:at[ée]|a)\s+)(\d{1,2}/\d{1,2}/\d{4}|\d{1,2}\s+de\s+[a-zç]+\s+de\s+\d{4})", re.I)
_PERIODO = re.compile(r"(?:per[ií]odo|protocolo|inscri[çc][õo]es|recebimento|envio|propostas)[^.\n]{0,60}?"
                      r"(\d{1,2}(?:/\d{1,2}/\d{4}|\s+de\s+[a-zç]+\s+de\s+\d{4}))\s+(?:a|at[ée])\s+"
                      r"(\d{1,2}(?:/\d{1,2}/\d{4}|\s+de\s+[a-zç]+\s+de\s+\d{4}))", re.I)
_VALOR = re.compile(r"R\$\s?\d{1,3}(?:\.\d{3})*(?:,\d{2})?")
_MESES = {m: i for i, m in enumerate(["janeiro", "fevereiro", "marco", "abril", "maio", "junho", "julho", "agosto",
                                      "setembro", "outubro", "novembro", "dezembro"], 1)}


def _data_br(txt: str | None) -> str | None:
    if not txt:
        return None
    t = _sem_acento(txt.lower()).strip()
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})$", t)
    try:
        if m:
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1))).isoformat()
        m = re.match(r"(\d{1,2})\s+de\s+([a-z]+)\s+de\s+(\d{4})$", t)
        if m and m.group(2) in _MESES:
            return date(int(m.group(3)), _MESES[m.group(2)], int(m.group(1))).isoformat()
    except ValueError:
        return None
    return None


def classificar_ato(trecho: str, hoje: date | None = None, publicado: str | None = None) -> dict:
    """Classifica UMA matéria do diário. Determinístico, explicável: cada decisão traz o motivo."""
    hoje = hoje or date.today()
    bruto = re.sub(r"[ \t]+", " ", trecho or "")
    T = _sem_acento(bruto).upper()
    # o cabeçalho é a PRIMEIRA palavra de ato em CAIXA ALTA no início do trecho — o timbre
    # ("SECRETARIA MUNICIPAL DE…", endereço, telefone) vem antes e não pode decidir o tipo
    mc = _CAB_CORPO.search(bruto[:700])
    tem_cab = bool(mc)
    ini = len(_sem_acento(bruto[:mc.start()])) if mc else 0
    cab = T[ini:ini + 220] if tem_cab else ""
    s = {k: bool(rx.search(T)) for k, rx in _RX.items()}
    c = {k: bool(rx.search(cab)) for k, rx in _RX.items() if k in ("resultado", "celebracao", "retificacao", "abertura")}
    cab = cab or T.lstrip()[:220]
    # TIPO — o cabeçalho manda; o corpo só decide quando o cabeçalho é neutro (portaria, despacho…)
    if c["resultado"] or (re.match(r"\s*(DESPACHO|PORTARIA|ATA)\b", cab) and s["resultado"]):
        tipo = "andamento"
    elif c["celebracao"] or (re.match(r"\s*(EXTRATO|JUSTIFICATIVA)\b", cab)):
        tipo = "celebracao"
    elif c["retificacao"]:
        tipo = "retificacao"
    elif c["abertura"] or (re.match(r"\s*(EDITAL|AVISO|CHAMADA)\b", cab) and s["abertura"]):
        tipo = "abertura"
    elif re.match(r"\s*(DECRETO|PORTARIA|DESPACHO|LEI|RESOLUCAO|INSTRUCAO)\b", cab):
        tipo = "normativo" if not s["resultado"] else "andamento"
    else:
        tipo = "abertura" if s["abertura_corpo"] else "andamento" if s["resultado"] else "referencia"
    if s["conselho_composicao"] and tipo in ("abertura", "retificacao"):
        tipo = "composicao_conselho"           # eleição de conselheiros: importa à OSC, mas não é recurso
    # REGIME
    if s["os_saude"]:
        regime = "organizacao_social_saude"
    elif s["credenciamento"] and not (s["mrosc"] or s["fundo"]):
        regime = "credenciamento"
    elif s["cultura"]:
        regime = "pnab_cultura"
    elif s["fundo"]:
        regime = "fundo_conselho"
    elif s["mrosc"]:
        regime = "mrosc"
    else:
        regime = "indefinido"
    publico = ("osc" if (s["mrosc"] or s["fundo"]) else
               "pessoa_fisica" if s["pessoa_fisica"] and not s["empresa"] else
               "empresa" if s["empresa"] else
               "osc_e_pessoa_fisica" if regime == "pnab_cultura" else "indefinido")
    if regime == "pnab_cultura" and s["pessoa_fisica"] and not (s["mrosc"] or s["fundo"]):
        publico = "osc_e_pessoa_fisica"        # PNAB admite pessoa física, coletivo E pessoa jurídica sem fins lucrativos
    orgao = next((r for r, p in _ORGAOS if re.search(p, T)), None)
    num = _NUM_CHAM.search(T) or _NUM.search(cab) or _NUM.search(T[:900])
    obj = _OBJETO.search(bruto)
    fim_txt = None
    mp = _PERIODO.search(bruto)
    m = _FIM.search(bruto)
    if mp:
        fim_txt = mp.group(2)            # "de 25 de setembro de 2026 a 26 de outubro de 2026" → o fim é a 2ª data
    elif m:
        fim_txt = m.group(1)
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
        else:
            veredito = "OPORTUNIDADE"; motivos.append(f"{tipo} de seleção para OSC no regime {regime}")
    elif tipo in ("andamento", "celebracao", "retificacao", "composicao_conselho") and (de_interesse or publico == "osc"):
        veredito = "ACOMPANHAR"
        motivos.append({"andamento": "resultado/andamento de seleção de interesse — prazo de recurso e quem venceu",
                        "celebracao": "parceria celebrada ou inexigibilidade — inteligência: órgão, valor e entidade parceira",
                        "retificacao": "retificação de edital de interesse — conferir prazo",
                        "composicao_conselho": "vaga da sociedade civil em conselho municipal — porta de entrada dos fundos"}[tipo])
    elif tipo == "referencia" and de_interesse and (num or _VALOR.search(bruto) or re.search(r"CELEBRA|REPASSE|TERMO DE FOMENTO", T)):
        veredito = "ACOMPANHAR"
        motivos.append("menção a parceria ou edital de interesse dentro de outro ato — conferir o ato completo na edição")
    else:
        veredito = "RUIDO"
        motivos.append({"credenciamento": "credenciamento de prestadores (Lei 8.666 art. 25 / 14.133 art. 79) — não é fomento a OSC",
                        "organizacao_social_saude": "qualificação/contrato de Organização Social na saúde (Lei Municipal 8.411/2006)",
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


# ───────────────────────────── 4. fontes ─────────────────────────────
def consultas_querido_diario(hoje: date, cfg: dict) -> list[str]:
    bases = cfg.get("querido_diario", {}).get("bases") or ["https://api.queridodiario.ok.org.br"]
    janela = int(cfg.get("querido_diario", {}).get("janela_dias", 15))
    out = []
    for q in cfg.get("querido_diario", {}).get("consultas") or []:
        params = {"territory_ids": IBGE, "querystring": q,
                  "published_since": (hoje - timedelta(days=janela)).isoformat(), "published_until": hoje.isoformat(),
                  "size": int(cfg.get("querido_diario", {}).get("size", 30)), "sort_by": "descending_date",
                  "excerpt_size": int(cfg.get("querido_diario", {}).get("excerpt_size", 1500)),
                  "number_of_excerpts": int(cfg.get("querido_diario", {}).get("number_of_excerpts", 3))}
        out.append(f"{bases[0].rstrip('/')}/gazettes?" + urlencode(params))
    return out


def ler_querido_diario(hoje: date, cfg: dict, diag: dict) -> dict[str, dict]:
    """{chave_edicao: {data, numero, url, txt_url, url_oficial, excertos[], consultas[]}}"""
    qd = cfg.get("querido_diario", {})
    bases = qd.get("bases") or ["https://api.queridodiario.ok.org.br"]
    edicoes: dict[str, dict] = {}
    for q, url0 in zip(qd.get("consultas") or [], consultas_querido_diario(hoje, cfg)):
        corpo, erro = None, None
        for b in bases:
            url = url0.replace(bases[0].rstrip("/"), b.rstrip("/"), 1)
            try:
                corpo = _get_json(url, tentativas=int(qd.get("tentativas", 2))); break   # 01/10: 503 da API é passageiro
            except RuntimeError as exc:
                erro = str(exc)
        diag["qd_consultas"] += 1
        if corpo is None:
            diag["qd_falhas"].append(erro or "sem resposta"); continue
        for g in corpo.get("gazettes") or []:
            if str(g.get("territory_id") or IBGE) != IBGE:
                continue                                   # Aparecida de Goiânia ≠ Goiânia
            k = (g.get("url") or g.get("txt_url") or "") + "|" + str(g.get("date"))
            e = edicoes.setdefault(k, {"data": (g.get("date") or "")[:10], "numero": g.get("edition"),
                                       "extra": bool(g.get("is_extra_edition")), "url": g.get("url"),
                                       "txt_url": g.get("txt_url"), "excertos": [], "consultas": []})
            e["url_oficial"] = url_oficial(e["data"], e["numero"])
            for x in g.get("excerpts") or []:
                x = re.sub(r"<[^>]+>", "", x or "")
                if x and x not in e["excertos"]:
                    e["excertos"].append(x)
            e["consultas"].append(q[:60])
        time.sleep(0.4)
    diag["qd_edicoes"] = len(edicoes)
    return edicoes


def texto_integral_qd(ed: dict, diag: dict) -> str | None:
    """Texto da edição já extraído pelo Querido Diário (txt_url) — sem PDF, sem pypdf."""
    u = ed.get("txt_url")
    if not u or not str(u).startswith("https://"):
        return None
    CACHE.mkdir(parents=True, exist_ok=True)
    alvo = CACHE / (sha256(u.encode())[:24] + ".txt")
    if alvo.exists():
        return alvo.read_text(encoding="utf-8", errors="replace")
    try:
        t = _get(u, timeout=60, max_bytes=12_000_000, aceitar="text/plain").decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001
        diag["txt_falhas"].append(f"{type(exc).__name__}: {u[-50:]}")
        return None
    alvo.write_text(t, encoding="utf-8")
    diag["txt_lidos"] += 1
    return t


def ler_portal(hoje: date, cfg: dict, diag: dict, processadas: set) -> dict[str, dict]:
    """Coleta LOCAL (IP brasileiro): lista do ano → PDFs das últimas edições ainda não lidas."""
    port = cfg.get("portal", {})
    if _em_nuvem():
        diag["portal"] = "nuvem: o portal recusa IP estrangeiro — fica para a coleta local (scripts/coleta_brasil.py)"
        return {}
    eds = []
    for ano in sorted({hoje.year, (hoje - timedelta(days=int(port.get("janela_dias", 7)))).year}, reverse=True):
        try:
            html = _get(LISTA.format(ano=ano), timeout=30, max_bytes=3_000_000, aceitar="text/html").decode("latin-1", "replace")
            eds += edicoes_da_lista(html)
            diag["portal_listas"] += 1
        except Exception as exc:  # noqa: BLE001
            diag["portal_falhas"].append(f"lista {ano}: {type(exc).__name__}")
    corte = (hoje - timedelta(days=int(port.get("janela_dias", 7)))).isoformat()
    novas = [e for e in eds if e["data"] >= corte and e["url"] not in processadas][: int(port.get("max_pdfs_por_execucao", 4))]
    out = {}
    for e in novas:
        CACHE.mkdir(parents=True, exist_ok=True)
        alvo = CACHE / (sha256(e["url"].encode())[:24] + ".txt")
        texto = alvo.read_text(encoding="utf-8", errors="replace") if alvo.exists() else None
        if texto is None:
            try:
                dados = _get(e["url"], timeout=120, max_bytes=40_000_000, aceitar="application/pdf")
            except Exception as exc:  # noqa: BLE001
                diag["portal_falhas"].append(f"pdf {e['data']}: {type(exc).__name__}"); continue
            texto = texto_do_pdf(dados)
            if not texto:
                diag["portal_falhas"].append(f"pdf {e['data']}: sem camada de texto ou pypdf ausente"); continue
            alvo.write_text(texto, encoding="utf-8")
        diag["portal_pdfs"] += 1
        out[e["url"] + "|" + e["data"]] = {**e, "url_oficial": e["url"], "texto": texto, "excertos": []}
    return out


# ───────────────────────────── 5. o motor ─────────────────────────────
def _achado(ato: dict, ed: dict, trecho: str) -> dict:
    url = ed.get("url_oficial") if ed.get("origem") == "portal" else (ed.get("url") or ed.get("url_oficial"))
    chave = ato["numero"] or sha256(re.sub(r"\s+", " ", trecho[:400]).lower().encode())[:12]
    titulo = " — ".join(x for x in [
        ato["orgao"] or "Prefeitura de Goiânia",
        f"Edital nº {ato['numero']}" if ato["numero"] else ato["cabecalho"][:90],
        (ato["objeto"] or "")[:140]] if x)
    ev = mascarar_pii(re.sub(r"\s+", " ", trecho))[:700]
    return {
        "id": sha256(f"dogyn|{ato['orgao']}|{chave}".encode())[:20], "status": "capturada",
        "titulo": titulo[:300], "url": url, "url_oficial_provavel": ed.get("url_oficial"),
        "url_querido_diario": ed.get("url"), "fonte_id": MOTOR_ID,
        "fonte_nome": "Diário Oficial do Município de Goiânia", "territorio": "GO/Goiânia", "municipio": "GO/Goiânia",
        "uf": "GO", "nivel": "municipal", "tipo_fonte": "sensor_diario_oficial", "confianca": "primaria",
        "forma_divulgacao": "diario_oficial_municipio", "coletado_em": now_iso(),
        "data_publicacao": ed.get("data"), "edicao_numero": ed.get("numero"),
        "prazo_texto": ato["prazo_texto"], "fim": ato["fim"], "valor_texto": (ato["valores"] or [None])[0],
        "objeto": ato["objeto"], "orgao": ato["orgao"], "regime": ato["regime"],
        "evidencia": ev, "hash_evidencia": sha256(ev.encode()),
        "classificacao_ato": {k: ato[k] for k in ("veredito", "tipo", "regime", "publico", "motivos", "sinais")},
        "sensor": MOTOR_ID, "forca_lexica": 3,
    }


def ler_motor(sensor: dict | None = None, hoje: date | None = None, limites: dict | None = None) -> dict:
    """Leitura do motor 01 com a mesma saída de `sensores.ler` (achados, falhas, saude, diagnostico)."""
    hoje = hoje or (sensor or {}).get("_data") or date.today()
    cfg = _cfg()
    est = load_json(ESTADO) if ESTADO.exists() else {"processadas": {}, "atos": []}
    proc = est.setdefault("processadas", {})
    diag = {"paginas_lidas": 0, "links_total": 0, "links_candidatos": 0, "descobertas": [], "pdf_links": 0, "motivo_zero": None,
            "versao": "motor-01 v2 (01/10/2026)", "qd_consultas": 0, "qd_edicoes": 0, "qd_falhas": [], "txt_lidos": 0, "txt_falhas": [],
            "portal_listas": 0, "portal_pdfs": 0, "portal_falhas": [], "atos_lidos": 0,
            "vereditos": {"OPORTUNIDADE": 0, "ACOMPANHAR": 0, "RUIDO": 0}}
    edicoes = {}
    try:
        for k, e in ler_querido_diario(hoje, cfg, diag).items():
            edicoes[k] = {**e, "origem": "querido_diario"}
    except Exception as exc:  # noqa: BLE001
        diag["qd_falhas"].append(f"{type(exc).__name__}: {exc}"[:160])
    oficiais_lidas = {e.get("url_oficial") for e in edicoes.values()}
    for k, e in ler_portal(hoje, cfg, diag, set(proc)).items():
        if e["url_oficial"] in oficiais_lidas and not e.get("texto"):
            continue
        edicoes[k] = {**e, "origem": "portal"}
    max_txt = int(cfg.get("querido_diario", {}).get("max_textos_integrais", 8))
    achados, saude, falhas, atos_painel = [], [], [], []
    for k, ed in sorted(edicoes.items(), key=lambda kv: kv[1].get("data") or "", reverse=True):
        marca = ed.get("url_oficial") or ed.get("url") or k
        texto = ed.get("texto")
        if texto is None and ed.get("origem") == "querido_diario" and max_txt > 0 and marca not in proc:
            texto = texto_integral_qd(ed, diag); max_txt -= 1
        partes = recortar_atos(texto) if texto else [x for x in ed.get("excertos") or [] if _INTERESSE.search(x)]
        if texto:
            proc[marca] = {"data": ed.get("data"), "em": now_iso(), "atos": len(partes), "origem": ed.get("origem")}
        saude.append({"url": marca, "http": 200, "bytes": len(texto or "".join(ed.get("excertos") or []))})
        diag["paginas_lidas"] += 1; diag["pdf_links"] += 1
        for trecho in partes:
            if has_prompt_injection(trecho):
                append_jsonl(QUARENTENA, {"origem": MOTOR_ID, "url": marca, "em": now_iso(), "hash": sha256(trecho.encode())[:16]})
                continue
            ato = classificar_ato(trecho, hoje, ed.get("data"))
            diag["atos_lidos"] += 1; diag["vereditos"][ato["veredito"]] += 1
            if ato["veredito"] == "RUIDO":
                continue
            reg = _achado(ato, ed, trecho)
            atos_painel.append({k2: reg[k2] for k2 in ("id", "titulo", "url", "data_publicacao", "fim", "orgao", "regime", "objeto")}
                               | {"veredito": ato["veredito"], "tipo": ato["tipo"], "motivo": ato["motivos"][0]})
            if ato["veredito"] == "OPORTUNIDADE":
                achados.append(reg)
    if not edicoes and diag["qd_falhas"]:
        falhas.append({"url": "querido_diario", "erro": "consulta", "code": None, "waf": None, "causa": diag["qd_falhas"][0]})
    # memória curta: atos dos últimos 120 dias (sem texto integral), para o painel e para não reprocessar
    vistos = {a["id"] for a in atos_painel}
    corte = (hoje - timedelta(days=120)).isoformat()
    est["atos"] = (atos_painel + [a for a in est.get("atos", []) if a["id"] not in vistos and (a.get("data_publicacao") or "") >= corte])[:300]
    est["processadas"] = {u: v for u, v in proc.items() if (v.get("data") or "") >= corte}
    est["ultima"] = {"em": now_iso(), "data": hoje.isoformat(), **{k: diag[k] for k in
                     ("qd_consultas", "qd_edicoes", "txt_lidos", "portal_pdfs", "atos_lidos", "vereditos")},
                     "falhas": (diag["qd_falhas"] + diag["txt_falhas"] + diag["portal_falhas"])[:8]}
    write_json(ESTADO, est)
    unicos = {a["id"]: a for a in achados}
    if not unicos:
        if not edicoes:
            diag["motivo_zero"] = ("Querido Diário sem resposta: " + diag["qd_falhas"][0]) if diag["qd_falhas"] else \
                "nenhuma edição de Goiânia com matéria do terceiro setor na janela consultada"
        else:
            v = diag["vereditos"]
            diag["motivo_zero"] = (f"{diag['qd_edicoes'] + diag['portal_pdfs']} edição(ões) lida(s), {diag['atos_lidos']} ato(s) do terceiro setor: "
                                   f"nenhum chamamento aberto para OSC hoje · {v['ACOMPANHAR']} a acompanhar · {v['RUIDO']} ruído "
                                   f"(credenciamento, OS da saúde, decretos)")
    return {"sensor": MOTOR_ID, "achados": list(unicos.values()), "falhas": falhas, "saude": saude,
            "diagnostico": diag, "lido_em": now_iso()}


def atos_para_painel(limite: int = 12) -> list[dict]:
    est = load_json(ESTADO) if ESTADO.exists() else {}
    ordem = {"OPORTUNIDADE": 0, "ACOMPANHAR": 1}
    return sorted(est.get("atos", []), key=lambda a: (ordem.get(a.get("veredito"), 9), str(a.get("data_publicacao") or "")),
                  reverse=False)[:limite]


def reclassificar_base(hoje: date | None = None) -> dict:
    """Reaproveita o que JÁ está na base: as edições de Goiânia vindas do Querido Diário
    (232 em 01/10/2026) tinham o trecho do ato guardado e eram descartadas sem leitura."""
    from .nucleo import DB_OPORTUNIDADES
    hoje = hoje or date.today()
    out = {"lidos": 0, "OPORTUNIDADE": 0, "ACOMPANHAR": 0, "RUIDO": 0, "exemplos": []}
    if not DB_OPORTUNIDADES.exists():
        return out
    for linha in DB_OPORTUNIDADES.open(encoding="utf-8"):
        try:
            r = json.loads(linha)
        except ValueError:
            continue
        if r.get("fonte_id") != "querido-diario" or not str(r.get("titulo", "")).startswith("Diário Oficial de Goiânia (GO)"):
            continue
        out["lidos"] += 1
        a = classificar_ato(r.get("evidencia") or "", hoje, r.get("data_publicacao"))
        out[a["veredito"]] += 1
        if a["veredito"] != "RUIDO" and len(out["exemplos"]) < 15:
            out["exemplos"].append({"data": r.get("data_publicacao"), "veredito": a["veredito"], "tipo": a["tipo"],
                                    "regime": a["regime"], "orgao": a["orgao"], "numero": a["numero"],
                                    "trecho": mascarar_pii(re.sub(r"\s+", " ", r.get("evidencia") or ""))[:180]})
    return out


if __name__ == "__main__":
    print(json.dumps(ler_motor()["diagnostico"], ensure_ascii=False, indent=2))
