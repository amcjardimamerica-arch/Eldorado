"""CARTÓRIO · LEITURA E EXTRAÇÃO (titular, 09/10/2026).

Régua única de site oficial, leitura do documento (PDF, ZIP do PNCP, página HTML) e extração dos 12 itens POR SEÇÃO,
cada um com valor + trecho literal + página + documento. Também reconhece quando o edital NÃO TEM o requisito e devolve
a dispensa com a justificativa de não aplicabilidade e o trecho que a comprova (regra de 04/10: "não informado" é falta,
nunca dispensa). Funções puras testadas sem rede; conteúdo lido é DADO, nunca instrução.
"""
from __future__ import annotations

import bisect
import io
import re
from urllib.parse import urlsplit

DOZE = ["Objeto", "Prazo de inscrição", "Resultado", "Prazo de recurso", "Valor", "Órgão / financiador",
        "Território", "Esfera", "Requisitos", "Anexos", "Destinação", "Área de atuação"]

# ── RÉGUA ÚNICA DE SITE OFICIAL (regra do titular de 07/09: vetor não é fonte) ──────────────────────────────────────
VETOR_ESTRITO = re.compile(r"pncp\.gov\.br/(?:app|pncp-api/v1/(?:orgaos/[^/]+/compras/[^/]+/[^/]+)?$)|queridodiario|capitaai|prosas\.com|"
                           r"observatorio3setor|captadores\.org|editaisculturais|bussolasocial|filantropia\.ong|nossacausa|farolcultural|"
                           r"bit\.ly|google\.|facebook\.|instagram\.|linkedin\.|youtube\.|portaldoterceirosetor|gife\.org\.br/(?!.*edital)|"
                           # 11/10: agregadores, blogs e portais vistos nas provas do Interceptador — só pista, nunca fonte
                           r"buscarlicitacao|querolicitacao|notasocial|corrivus|agenciadobem|acheconcursos|scbrnews|inclusaosocial\.com|"
                           r"blog\.bondinho|artequemoraaqui|mosaicco", re.I)
IMPRENSA = re.compile(r"g1\.globo|uol\.com|folha\.|estadao\.|metropoles|jornal|noticia", re.I)
VETOR = re.compile(VETOR_ESTRITO.pattern + "|" + IMPRENSA.pattern, re.I)
DOC_ORGAO = re.compile(r"pncp\.gov\.br/pncp-api/v1/orgaos/\d+/compras/\d+/\d+/arquivos/\d+", re.I)
PUBLICO = re.compile(r"\.(gov|leg|jus|mp|def|tc)\.br$|(^|\.)in\.gov\.br$|\.edu\.br$|\.org\.br$|\.(com|org)\.br$|\.org$|\.com$|\.int$", re.I)
GOV = re.compile(r"\.(gov|leg|jus|mp|def|tc)\.br$", re.I)


def regua(url: str | None) -> tuple[bool, str]:
    """(é oficial?, por quê). Oficial: arquivo anexado pelo órgão no PNCP, domínio público (.gov/.leg/.jus/.mp/.tc),
    DOU, ou domínio próprio do financiador privado. Nunca: página de anúncio do PNCP, Querido Diário, agregador, imprensa."""
    u = str(url or "")
    if not u.startswith("http"):
        return False, "sem endereço"
    try:
        urlsplit(u).hostname
    except ValueError:
        return False, "endereço malformado"
    if DOC_ORGAO.search(u):
        return True, "arquivo do edital anexado pelo órgão no PNCP"
    if VETOR_ESTRITO.search(u):
        return False, "vetor (anúncio, republicador ou agregador) — não é fonte"
    _h = (urlsplit(u).hostname or "").lower()
    if GOV.search(_h) or _h.endswith("in.gov.br"):
        return True, "domínio público oficial"          # 09/10 v2: notícia em domínio de governo é oficial (o órgão publica)
    if IMPRENSA.search(u):
        return False, "imprensa — não é fonte"
    try:
        from .sites_oficiais import e_republicador
        if e_republicador(u):
            return False, "republicador catalogado"
    except Exception:  # noqa: BLE001
        pass
    h = (urlsplit(u).hostname or "").lower()
    if GOV.search(h) or h.endswith("in.gov.br"):
        return True, "domínio público oficial"
    if PUBLICO.search(h):
        return True, "domínio próprio do financiador"
    return False, "domínio não reconhecido"


def esfera_do_dominio(url: str) -> str | None:
    try:
        h = (urlsplit(str(url or "")).hostname or "").lower()
    except ValueError:
        return None
    if not h:
        return None
    # 15/10 (avaliação com gabarito): portal nacional e diário oficial NÃO dizem a esfera do órgão — o PNCP publica
    # compras de prefeituras e estados; o DOU publica atos municipais. Nesses, a esfera vem do órgão, nunca do domínio.
    if re.search(r"(^|\.)(pncp\.gov\.br|in\.gov\.br|queridodiario\.ok\.org\.br)$", h):
        return None
    if re.search(r"(^|\.)gov\.br$", h) and not re.search(r"\.[a-z]{2}\.gov\.br$", h):
        return "federal"
    if re.search(r"prefeitura|camara|municipal|\.[a-z]+\.[a-z]{2}\.gov\.br$", h):
        return "municipal"
    if h.endswith(".gov.br"):
        return "estadual"
    return None


# ── LEITURA ────────────────────────────────────────────────────────────────────────────────────────────────────────
def de_zip(b: bytes) -> tuple[bytes | None, str | None]:
    import zipfile
    try:
        z = zipfile.ZipFile(io.BytesIO(b))
    except Exception:  # noqa: BLE001
        return None, None
    pdfs = [i for i in z.infolist() if i.filename.lower().endswith(".pdf") and i.file_size <= 30_000_000]
    if not pdfs:
        return None, None
    i = next((x for x in pdfs if "edital" in x.filename.lower()), max(pdfs, key=lambda x: x.file_size))
    return z.read(i), i.filename


def paginas(b: bytes, tipo: str = "", max_paginas: int = 60, min_letras: int = 40) -> dict:
    """bytes → {ok, motivo, paginas: [texto por página], tabelas}. PDF (texto + tabelas quando houver pdfplumber),
    ZIP do PNCP ou HTML. Motivo explícito em toda falha."""
    b = b or b""
    nome_zip = None
    if b[:2] == b"PK":
        b, nome_zip = de_zip(b)
        if b is None:
            return {"ok": False, "motivo": "zip_sem_pdf", "paginas": []}
    if b[:1024].lstrip().startswith(b"%PDF"):
        try:
            from pypdf import PdfReader
        except Exception:  # noqa: BLE001
            return {"ok": False, "motivo": "sem_leitor_pdf", "paginas": []}
        try:
            rd = PdfReader(io.BytesIO(b))
            if rd.is_encrypted:
                rd.decrypt("")
            txt = []
            for p in rd.pages[:max_paginas]:
                try:
                    txt.append(p.extract_text() or "")
                except Exception:  # noqa: BLE001
                    txt.append("")
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "motivo": "pdf_corrompido", "paginas": [], "detalhe": type(e).__name__}
        # CAMADA 2: tabelas (cronogramas) — só se pdfplumber estiver no ambiente
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(b)) as pdf:
                for i, pg in enumerate(pdf.pages[:max_paginas]):
                    for t in pg.extract_tables() or []:
                        linhas = [" | ".join(str(c or "").strip() for c in row) for row in t if row]
                        if linhas and i < len(txt):
                            txt[i] += "\n[TABELA] " + " \n[TABELA] ".join(linhas)
        except Exception:  # noqa: BLE001
            pass
        letras = sum(len(re.findall(r"[A-Za-zÀ-ú]", t)) for t in txt)
        if letras < min_letras * max(1, len(txt)):
            return {"ok": False, "motivo": "pdf_escaneado", "paginas": txt, "detalhe": "páginas de imagem, sem camada de texto"}
        return {"ok": True, "motivo": None, "paginas": txt, "tipo": "pdf", "dentro_do_zip": nome_zip}
    h = b.decode("utf-8", "ignore")
    if "<" not in h[:2000]:
        return {"ok": False, "motivo": "formato_desconhecido", "paginas": []}
    corpo = re.sub(r"(?is)<(script|style|nav|footer|header)[^>]*>.*?</\1>", " ", h)
    corpo = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</h\d>|</tr>", "\n", corpo)
    t = re.sub(r"[ \t]+", " ", re.sub(r"<[^>]+>", " ", corpo))
    t = re.sub(r"&nbsp;", " ", t)
    if re.search(r"(?i)<title>[^<]*(404|n[ãa]o encontrad|not found|erro|acesso negado)", h[:3000]):
        return {"ok": False, "motivo": "pagina_de_erro", "paginas": []}
    return {"ok": len(re.findall(r"[A-Za-zÀ-ú]", t)) > 200, "motivo": None if len(t) > 200 else "pagina_vazia",
            "paginas": [t], "tipo": "html", "html": h}


DOC_LINK = re.compile(r"""href=["']([^"']+?)["'][^>]*>(.{0,200}?)</a>""", re.I | re.S)
EMBUTIDO = re.compile(r"""<(?:iframe|embed|object)[^>]+(?:src|data)=["']([^"']+)["']|data-pdf=["']([^"']+)["']|["'](https?://[^"'\s]+\.pdf(?:\?[^"'\s]*)?)["']""", re.I)


def links_de_documento(html: str, base: str) -> list[tuple[str, str]]:
    """Links de documento numa página oficial, do mais provável (edital) ao menos: PDF, /Download/, wp-content."""
    from urllib.parse import urljoin
    out = []
    for href, rot in DOC_LINK.findall(html or ""):
        try:
            u = urljoin(base, href.strip()); urlsplit(u).hostname
        except ValueError:
            continue
        r = re.sub(r"<[^>]+>|\s+", " ", rot).strip()
        if not u.startswith("http"):
            continue
        doc = re.search(r"\.pdf($|\?)|/download/|/wp-content/uploads/|/arquivos?/|anexo", u, re.I)
        if doc or re.search(r"(?i)\bedital\b|regulamento|chamamento|termo de refer", r):
            peso = (3 if re.search(r"(?i)edital|regulamento|chamamento", r + u) else 0) + (2 if doc else 0) - \
                   (2 if re.search(r"(?i)resultado|homologa|errata|retifica|ata\b|recurso", r + u) else 0)
            out.append((peso, u, r[:120]))
    for m in EMBUTIDO.finditer(html or ""):                 # PDF embutido no visualizador (iframe/embed/object/data-pdf)
        src = next((g for g in m.groups() if g), None)
        try:
            u = urljoin(base, src.strip()) if src else None
        except ValueError:
            u = None
        if u and u.startswith("http"):
            out.append((6, u, "documento embutido na página"))
    vistos, res = set(), []
    for _p, u, r in sorted(out, key=lambda x: -x[0]):
        if u not in vistos:
            vistos.add(u); res.append((u, r))
    return res[:8]


def links_de_saida(html: str, base: str) -> list[str]:
    """Pista (agregador/notícia): links para FORA dela que apontam para edital, regulamento ou inscrição."""
    from urllib.parse import urljoin
    hb = (urlsplit(base).hostname or "").lower()
    out = []
    for href, rot in DOC_LINK.findall(html or ""):
        try:
            u = urljoin(base, href.strip()); h = (urlsplit(u).hostname or "").lower()
        except ValueError:
            continue
        if not u.startswith("http") or not h or h == hb or VETOR.search(u):
            continue
        alvo = re.search(r"(?i)edital|regulamento|inscri|chamamento|chamada|sele[çc][ãa]o|pr[êe]mio|programa|\.pdf", rot + " " + u) or \
            re.search(r"(?i)clique aqui|acesse|saiba mais|site oficial|p[áa]gina oficial|confira|link", rot) or GOV.search(h)
        if alvo:
            out.append((0 if re.search(r"(?i)edital|regulamento|\.pdf", rot + u) else 1, u))
    return list(dict.fromkeys(u for _p, u in sorted(out)))[:6]


# ── EXTRAÇÃO POR SEÇÕES ────────────────────────────────────────────────────────────────────────────────────────────
MES = {"janeiro": 1, "fevereiro": 2, "março": 3, "marco": 3, "abril": 4, "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
       "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12}
DATA = r"(?:\d{1,2}[/.]\d{1,2}[/.](?:20)?\d{2}|\d{1,2}º? de (?:janeiro|fevereiro|mar[çc]o|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro) de \d{4})"
SECAO = re.compile(r"(?:^|\n|\s)(?:\d{1,2}(?:\.\d{1,2})*\.?\s*[-–]?\s*|CAP[ÍI]TULO\s+[IVXL]+\s*[-–]?\s*)?"
                   r"(D[OA]S?\s+(OBJETO|OBJETIVOS?|PRAZOS?|INSCRI[ÇC][ÕO]ES|CRONOGRAMA|RECURSOS?(?: FINANCEIROS| OR[ÇC]AMENT[ÁA]RIOS)?|VALOR(?:ES)?|"
                   r"PR[ÊE]MIOS?|PREMIA[ÇC][ÃA]O|CONDI[ÇC][ÕO]ES DE PARTICIPA[ÇC][ÃA]O|PARTICIPA[ÇC][ÃA]O|REQUISITOS|HABILITA[ÇC][ÃA]O|"
                   r"RESULTADOS?|ANEXOS|DESTINA[ÇC][ÃA]O|FINALIDADE|IMPEDIMENTOS|VED[AÇ][ÇÕ][ÃO]ES))\b")
AREAS = {"Cultura": r"cultur|artes?\b|patrim[oô]nio|audiovisual|m[uú]sica|teatro", "Assistência social": r"assist[eê]ncia social|vulnerabilidade|socioassist",
         "Educação": r"educa[çc][ãa]o|escola|ensino", "Saúde": r"\bsa[úu]de\b", "Esporte": r"esport|lazer", "Meio ambiente": r"ambient|clim|sustentab",
         "Criança e adolescente": r"crian[çc]a|adolescente|juventude", "Idosos": r"idos[oa]s|pessoa idosa", "Direitos humanos": r"direitos humanos|igualdade racial|mulheres",
         "Ciência e tecnologia": r"ci[êe]ncia|tecnolog|inova[çc][ãa]o|pesquisa"}


class Texto:
    """Texto do documento inteiro com o mapa posição → página, e as seções localizadas."""
    def __init__(self, paginas_: list[str]):
        self.inicio, partes, pos = [], [], 0
        for p in paginas_:
            self.inicio.append(pos); t = (p or "") + "\n"; partes.append(t); pos += len(t)
        self.t = "".join(partes)
        self.plano = re.sub(r"\s+", " ", self.t)
        self.secoes = [(m.start(1), m.group(2).upper()) for m in SECAO.finditer(self.t)]

    def pagina(self, pos: int) -> int:
        return max(1, bisect.bisect_right(self.inicio, pos))

    def secao(self, nome_rx: str, tamanho: int = 1500) -> tuple[int, str] | None:
        for i, (pos, nome) in enumerate(self.secoes):
            if re.search(nome_rx, nome):
                fim = self.secoes[i + 1][0] if i + 1 < len(self.secoes) else pos + tamanho
                return pos, self.t[pos:min(fim, pos + tamanho)]
        return None

    def trecho(self, ini: int, fim: int, folga: int = 70) -> str:
        return re.sub(r"\s+", " ", self.t[max(0, ini - folga):fim + folga]).strip()[:400]


def _data_iso(s: str) -> str | None:
    s = s.strip().lower()
    m = re.match(r"(\d{1,2})[/.](\d{1,2})[/.]((?:20)?\d{2})", s)
    if m:
        a = int(m.group(3)); a = a + 2000 if a < 100 else a
        d, mo = int(m.group(1)), int(m.group(2))
    else:
        m = re.match(r"(\d{1,2})º? de ([a-zç]+) de (\d{4})", s)
        if not m or m.group(2) not in MES:
            return None
        d, mo, a = int(m.group(1)), MES[m.group(2)], int(m.group(3))
    if not (1 <= d <= 31 and 1 <= mo <= 12 and 2015 <= a <= 2035):
        return None
    return f"{a:04d}-{mo:02d}-{d:02d}"


def _achar(T: Texto, rx: str, secao_rx: str | None = None, grupo: int = 1, flags=re.I | re.S):
    """Procura primeiro dentro da seção certa; depois no documento inteiro. Devolve (valor, ini, fim)."""
    alvos = []
    if secao_rx:
        s = T.secao(secao_rx)
        if s:
            alvos.append((s[0], s[1]))
    alvos.append((0, T.t))
    for base, txt in alvos:
        m = re.search(rx, txt, flags)
        if m:
            g = m.group(grupo) if (grupo is not None and m.lastindex and grupo <= m.lastindex) else m.group(0)
            return re.sub(r"\s+", " ", g).strip(), base + m.start(), base + m.end()
    return None


def normalizar(p: str) -> str:
    """Desfaz quebras do leitor de PDF nas datas: "23 /09 /2026" → "23/09/2026"; "/202 6" → "/2026"; "1º de" mantido."""
    p = re.sub(r"(?<=\d) ?/ ?(?=\d)", "/", p or "")
    return re.sub(r"(/20\d) (\d)\b", r"\1\2", p)


def extrair(paginas_: list[str], documento: str, titulo: str = "", orgao_hint: str = "") -> dict:
    """{'pontos': {item: {valor, trecho, pagina, documento, metodo}}, 'dispensas': {item: {motivo, trecho, pagina}},
    'fim': ISO do prazo de inscrição (quando houver)}."""
    paginas_ = [normalizar(p) for p in paginas_]
    T = Texto(paginas_)
    P, D, fim = {}, {}, None

    def pôr(item, valor, ini, fim_, metodo="seção"):
        if valor and len(str(valor).strip()) >= 3 and item not in P:
            P[item] = {"valor": str(valor).strip()[:300], "trecho": T.trecho(ini, fim_), "pagina": T.pagina(ini),
                       "documento": documento, "metodo": metodo}

    # PRAZO DE INSCRIÇÃO — janela depois da palavra-chave, dentro de INSCRIÇÕES/CRONOGRAMA/PRAZO
    # 15/10 (avaliação com gabarito): o ponto de abreviatura/numeração ("OSCs. 23/09", "2.3.Data") não encerra mais a
    # janela; "à" liga as duas datas; rótulos de cronograma e de credenciamento; data antes do rótulo (tabela).
    kw = (r"(?:per[ií]odo de inscri[çc][õo]es|inscri[çc][õo]es|recebimento d[ae]s? (?:propostas|projetos|inscri|documenta|envelopes)|"
          r"(?:envio|entrega|protocolo|apresenta[çc][ãa]o|submiss[ãa]o) d[ae]s? (?:propostas|projetos|envelopes|documenta[çc][ãa]o|planos? de trabalho)|"
          r"data (?:e hora )?(?:final|limite|de encerramento) (?:d[ae]s?|para) (?:propostas|inscri|envio|entrega|recebimento)|"
          r"prazo (?:final |limite )?(?:para|de) (?:inscri|envio|entrega|apresenta|submiss)|"
          r"(?:permanecer[áa]|ficar[áa]|estar[áa]) (?:em )?abert[oa]|poder[ãa]o ser recebid[ao]s|credenciamento a partir)")
    jan = r"(?:[^.]|\.(?=\S)|\.\s(?=\d)){0,160}?"
    lig = r"(?:[^.\d]{0,40}?(?:a|à|á|at[ée]|e|ao)\s*(" + DATA + r"))?"
    padroes = [kw + jan + rf"({DATA})" + lig, rf"({DATA})\s*(?:a|à|á|at[ée])\s*({DATA})[^.\n]{{0,60}}?" + kw]
    for sec in (r"INSCRI|CRONOGRAMA|PRAZO", None):
        r = None
        for rx in padroes:
            r = _achar(T, rx, sec, None)
            if r and [x for x in (_data_iso(d) for d in re.findall(DATA, r[0], re.I)) if x]:
                break
            r = None
        if r:
            ds = re.findall(DATA, r[0], re.I)
            isos = [x for x in (_data_iso(d) for d in ds) if x]
            if isos:
                fim = max(isos)
                val = f"{ds[0]} a {ds[-1]}" if len(ds) > 1 else f"até {ds[0]}"
                pôr("Prazo de inscrição", val, r[1], r[2], "cronograma" if sec else "texto")
                break
    # RESULTADO
    # 15/10 (avaliação com gabarito): a DATA do resultado no cronograma vem antes do "N dias" solto; "em até N dias …
    # divulgar o resultado"; a janela atravessa pontos de numeração.
    jr = r"(?:[^.]|\.(?=\S)|\.\s(?=\d)){0,120}?"
    rot = r"(?:divulga[çc][ãa]o|publica[çc][ãa]o|homologa[çc][ãa]o)?\s*(?:d[oa]s? )?resultados?(?: (?:final|definitivo|preliminar|provis[óo]rio|parcial))?"
    r = None
    for rx, sec in ((rot + jr + rf"({DATA})", r"CRONOGRAMA|RESULTADO"),
                    (r"em at[ée] (\d{1,3}\s*\(?[a-zç ]{0,12}\)?\s*dias(?:\s*[úu]teis| corridos)?)[^.]{0,80}?(?:divulgar|publicar|proclamar)[^.]{0,20}?resultado", r"RESULTADO|CRONOGRAMA"),
                    (rf"(?:divulga[çc][ãa]o d[oa]s? )?resultado(?: final| definitivo| preliminar)?[^.]{{0,120}}?({DATA}|\d+\s*[(\[]?[a-z ]*[)\]]?\s*dias)", r"CRONOGRAMA|RESULTADO")):
        r = _achar(T, rx, sec)
        if r:
            break
    if r:
        pôr("Resultado", r[0], r[1], r[2])
    # PRAZO DE RECURSO
    # 15/10 (avaliação com gabarito): "recurso" no sentido de CONTESTAÇÃO — nunca recursos financeiros/orçamentários;
    # o número de dias ou o intervalo de datas da fase recursal, antes ou depois do rótulo.
    dias_rx = r"(\d{1,2}\s*[(\[]?[a-zçã ]{0,12}[)\]]?\s*dias(?:\s*[úu]teis| corridos)?)"
    ctx = (r"(?:prazo recursal|prazo (?:para|de) (?:a )?(?:interposi[çc][ãa]o de |apresenta[çc][ãa]o de )?recursos?|interpo(?:r|si[çc][ãa]o d[eo]s?)\s+recursos?|recursos? (?:administrativos?|contra|ao resultado|do resultado|"
           r"quanto|em face)|apresenta[çc][ãa]o de recursos?|fase recursal|caber[áa]\s*,?[^.]{0,60}?recurso|poder[ãa]o? (?:recorrer|interpor))")
    jan2 = r"(?:[^.]|\.(?=\S)|\.\s(?=\d)){0,140}?"
    r = None
    for rx in (ctx + jan2 + rf"({DATA})\s*(?:a|à|á|at[ée])\s*({DATA})", ctx + jan2 + dias_rx,
               r"(?:no )?prazo (?:de|m[áa]ximo de) " + dias_rx + r"[^.]{0,120}?" + ctx,
               # última tentativa: qualquer "recurso" que NÃO seja dinheiro
               r"\brecursos?\b(?!\s+(?:financeiros?|or[çc]ament[áa]rios?|p[úu]blicos?|pr[óo]prios?|humanos?|materiais|dispon[íi]veis|"
               r"federais|estaduais|municipais|repassad|transferid|destinad|necess[áa]rios?|da |do |de |para |oriundos?|captad))" + jan2 + dias_rx):
        r = _achar(T, rx, r"RECURSO|CRONOGRAMA|RESULTADO", None)
        if r:
            break
    if r:
        dd = re.findall(DATA, r[0], re.I)
        m = re.search(dias_rx, r[0], re.I)
        val = f"{dd[0]} a {dd[-1]}" if len(dd) > 1 else (re.sub(r"\s+", " ", m.group(1)) if m else r[0])
        pôr("Prazo de recurso", val, r[1], r[2])
    # VALOR — prefere o R$ ao lado de "valor global/total/teto/montante"
    r = _achar(T, r"(?:valor (?:global|total|m[áa]ximo|estimado|de at[ée]|do pr[êe]mio|de cada)|montante|teto|dota[çc][ãa]o|recursos? (?:financeiros|dispon[ií]veis|totais)|limite de)[^.]{0,80}?(R\$\s?\d[\d.]*(?:,\d{2})?(?:\s*\([^)]{3,80}\))?)",
               r"RECURSO|VALOR|PR[ÊE]MI|PREMIA")
    r = r or _achar(T, r"(R\$\s?\d{1,3}(?:\.\d{3})+(?:,\d{2})?(?:\s*\([^)]{3,80}\))?)")
    if r:
        pôr("Valor", r[0], r[1], r[2])
    # OBJETO
    s = T.secao(r"OBJETO|OBJETIVO|FINALIDADE")
    if s:
        corpo = re.sub(r"^\S+(?:\s+\S+){0,2}\s*", "", s[1][:700])
        m = re.search(r"([A-ZÀ-Úa-zà-ú0-9][^.;]{40,320}[.;])", corpo)
        if m:
            pôr("Objeto", m.group(1), s[0], s[0] + len(m.group(0)) + 20)
    if "Objeto" not in P:
        r = _achar(T, r"(?:tem (?:por|como) (?:objeto|objetivo|finalidade)|objeto d[oe]st[ea] (?:edital|chamamento|chamada)\s*(?:é|:)|o presente (?:edital|chamamento p[úu]blico|regulamento)[^.]{0,50}?(?:visa|objetiva|destina-se))\s*[:,\-–]?\s*([^.;]{30,320}[.;])")
        if r:
            pôr("Objeto", r[0], r[1], r[2], "texto")
    # ÓRGÃO / FINANCIADOR — cabeçalho da primeira página primeiro
    cab = "\n".join(paginas_[:1])[:2500]
    m = re.search(r"((?:PREFEITURA MUNICIPAL DE|MUNIC[ÍI]PIO DE|GOVERNO DO ESTADO D[EOA]|SECRETARIA (?:MUNICIPAL|ESTADUAL|DE ESTADO)?\s*D[EOA]S?|MINIST[ÉE]RIO D[EOA]S?|"
                  r"FUNDA[ÇC][ÃA]O|INSTITUTO|FUNDO (?:MUNICIPAL|ESTADUAL|NACIONAL)|AG[ÊE]NCIA|C[ÂA]MARA MUNICIPAL DE|TRIBUNAL|MINIST[ÉE]RIO P[ÚU]BLICO)[^\n,;.]{3,90})", cab, re.I)
    if m:
        pôr("Órgão / financiador", re.sub(r"\s+", " ", m.group(1)), m.start(1), m.end(1), "cabeçalho")
    elif orgao_hint:
        r = _achar(T, re.escape(orgao_hint[:40]))
        if r:
            pôr("Órgão / financiador", orgao_hint, r[1], r[2], "texto")
    # TERRITÓRIO
    # 15/10 (avaliação com gabarito): o município (sede exigida, "Município de X", cabeçalho da prefeitura) vem antes do
    # estado, que aparece cedo no texto e era pego primeiro; nome próprio sem atravessar linha.
    nome = r"[A-ZÀ-Ú][a-zà-úA-ZÀ-Ú'’-]+(?:\s(?:d[aeo]s?\s)?[A-ZÀ-Ú][a-zà-úA-ZÀ-Ú'’-]+){0,3}"
    r = None
    for rx, fl in ((r"(todo o territ[óo]rio nacional|abrang[êe]ncia nacional|em qualquer (?:unidade da federa[çc][ãa]o|estado|munic[íi]pio) do (?:pa[íi]s|Brasil))", re.I),
                   (r"((?:sediad[ao]s?|sede|domiciliad[ao]s?|atua[çc][ãa]o comprovada)\s+(?:[^.]{0,30}?\s)?(?:no|em|na cidade de|no munic[íi]pio de)\s+" + nome + ")", 0),
                   (r"((?:no|do|ao) [Mm]unic[íi]pio de " + nome + ")", 0),
                   (r"(PREFEITURA (?:MUNICIPAL )?DE [A-ZÀ-Ú][A-ZÀ-Ú' -]{2,40})", 0),
                   (r"(abrang[êe]ncia (?:estadual|municipal)|(?:no|do) Estado d[eoa] " + nome + ")", 0)):
        r = _achar(T, rx, None, 1, fl)
        if r:
            break
    if r:
        pôr("Território", r[0], r[1], r[2], "texto")
    # ESFERA — pelo domínio oficial do documento ou pelo órgão
    esf = esfera_do_dominio(documento)
    org = (P.get("Órgão / financiador") or {}).get("valor", "") + " " + orgao_hint
    if not esf and not org.strip():
        org = cab[:600]
    if not esf:
        esf = "municipal" if re.search(r"(?i)prefeitura|munic[íi]pio|municipal|c[âa]mara de vereadores", org) else "estadual" if re.search(r"(?i)governo do estado|de estado|estadual|tribunal de justi[çc]a|assembleia legislativa|minist[ée]rio p[úu]blico do estado|\buniversidade estadual", org) \
            else "federal" if re.search(r"(?i)minist[ée]rio|uni[ãa]o|federal", org) else "privada" if re.search(r"(?i)instituto|funda[çc][ãa]o|empresa|s\.?a\.?\b|ltda", org) else None
    if esf:
        P["Esfera"] = {"valor": esf, "trecho": f"domínio/órgão: {(urlsplit(documento).hostname or '')} · {org.strip()[:80]}", "pagina": 1,
                       "documento": documento, "metodo": "domínio e órgão"}
    # REQUISITOS
    if True:  # 15/10 (avaliação com gabarito): a frase explícita de quem pode participar vem antes da 1ª frase da seção
        r = _achar(T, r"((?:poder[ãa]o participar|poder[ãa]o se inscrever|est[ãa]o aptas? a participar|s[ãa]o requisitos|requisitos? (?:para|de) (?:participa|inscri|habilita)|"
                      r"(?:as|os) (?:proponentes|interessad[oa]s|organiza[çc][õo]es) dever[ãa]o (?:comprovar|apresentar|possuir)|habilita[çc][ãa]o jur[íi]dica|"
                      r"documentos? (?:necess[áa]rios|exigidos) (?:para|à|a) (?:inscri|habilita))[^.;]{20,320}[.;])")
        if r:
            pôr("Requisitos", r[0], r[1], r[2], "texto")
    s = T.secao(r"CONDI|PARTICIPA|REQUISITO|HABILITA")
    if s and "Requisitos" not in P:
        m = re.search(r"([A-ZÀ-Úa-zà-ú0-9][^.;]{40,350}[.;])", re.sub(r"^\S+(?:\s+\S+){0,4}\s*", "", s[1][:900]))
        if m:
            pôr("Requisitos", m.group(1), s[0], s[0] + 300)
    # ANEXOS
    an = list(dict.fromkeys(re.sub(r"\s+", " ", a).strip() for a in re.findall(r"ANEXO\s+[IVXL]{1,5}\s*[-–—:]?\s*[^\n]{0,70}", T.t)))
    if an:
        i = T.t.find("ANEXO")
        P["Anexos"] = {"valor": "; ".join(an)[:300], "trecho": T.trecho(i, i + 120), "pagina": T.pagina(i), "documento": documento, "metodo": "lista de anexos"}
    # DESTINAÇÃO
    r = _achar(T, r"((?:os |o )?(?:recursos?|valores?|pr[êe]mios?|apoio) (?:ser[ãa]o|dever[ãa]o ser|poder[ãa]o ser) (?:destinados?|aplicados?|utilizados?|empregados?)[^.;]{15,250}[.;]|"
                  r"destina-se a[^.;]{15,250}[.;]|(?:s[ãa]o |ser[ãa]o )?(?:consideradas )?despesas (?:eleg[ií]veis|financi[áa]veis|permitidas)[^.;]{10,250}[.;]|"
                  r"(?:poder[ãa]o|dever[ãa]o) ser (?:financiad[oa]s|custead[oa]s)[^.;]{10,250}[.;]|itens financi[áa]veis[^.;]{10,250}[.;]|"
                  # 15/10 (avaliação com gabarito): "projetos destinados à…", "para aplicação de recursos do…"
                  r"(?:projetos|propostas|recursos|parcerias?|a[çc][õo]es) destinad[oa]s? (?:à|a|ao|às|aos)\s[^.;]{15,250}[.;]|"
                  r"para (?:a )?(?:aplica[çc][ãa]o|execu[çc][ãa]o) (?:d[eo]s? )?recursos[^.;]{10,220}[.;])",
               r"DESTINA|FINALIDADE|RECURSO|OBJETO")
    if r:
        pôr("Destinação", r[0], r[1], r[2])
    # ÁREA DE ATUAÇÃO
    base = (P.get("Objeto") or {}).get("valor", "") + " " + titulo + " " + T.plano[:6000]
    ach = [a for a, rx in AREAS.items() if re.search(rx, base, re.I)]
    if ach:
        P["Área de atuação"] = {"valor": ", ".join(ach[:3]), "trecho": f"termos do objeto e do título: {', '.join(ach[:3])}", "pagina": 1,
                                "documento": documento, "metodo": "palavras-chave do objeto"}

    # ── DISPENSAS: o edital NÃO TEM o requisito — sempre com o trecho que comprova ──────────────────────────────────
    def dispensar(item, rx, motivo):
        if item in P or item in D:
            return
        m = re.search(rx, T.t, re.I | re.S)
        if m:
            D[item] = {"motivo": f"dispensado pelo Cartório — não se aplica: {motivo}", "trecho": T.trecho(m.start(), m.end()),
                       "pagina": T.pagina(m.start()), "documento": documento}

    continuo = r"fluxo cont[íi]nuo|a qualquer tempo|inscri[çc][õo]es permanentes|em car[áa]ter permanente|cadastro permanente|chamamento permanente"
    dispensar("Prazo de inscrição", continuo, "inscrição em fluxo contínuo (cadastro permanente, sem data-limite)")
    credenciamento = re.search(r"(?i)credenciamento", titulo + " " + (P.get("Objeto") or {}).get("valor", "") + " " + T.plano[:3000]) and \
        not re.search(r"(?i)classifica[çc][ãa]o|pontua[çc][ãa]o|crit[ée]rios? de (?:sele|julga|avalia)", T.plano)
    if credenciamento:
        dispensar("Resultado", r"credenciamento", "credenciamento sem seleção competitiva — todos os habilitados são credenciados")
    dispensar("Resultado", continuo, "fluxo contínuo — cada proposta é analisada ao chegar, não há resultado único")
    dispensar("Prazo de recurso", r"n[ãa]o caber[áa] recurso|sem fase recursal|decis[ãa]o (?:final )?irrecorr[ií]vel|n[ãa]o h[áa] (?:previs[ãa]o de )?recurso", "o edital declara que não cabe recurso")
    dispensar("Valor", r"sem (?:repasse|transfer[êe]ncia) de recursos|n[ãa]o (?:haver[áa]|envolve|implica|prev[êe]) (?:o )?(?:repasse|transfer[êe]ncia) de recursos|"
                       r"sem [ôo]nus (?:para|ao|à)|a t[íi]tulo gratuito|acordo de coopera[çc][ãa]o|cess[ãa]o (?:gratuita|de uso)", "sem repasse financeiro (cooperação, cessão ou habilitação sem recurso)")
    if re.search(r"(?i)\bpr[êe]mio|premia[çc][ãa]o", titulo + " " + T.plano[:4000]):
        dispensar("Destinação", r"reconhecimento (?:de|a|à|da|das|dos)|trajet[óo]ria|n[ãa]o (?:ser[áa]|haver[áa]) (?:exigid[ao] )?presta[çc][ãa]o de contas",
                  "prêmio de reconhecimento — uso livre pelo premiado, sem destinação vinculada")
    dispensar("Anexos", r"n[ãa]o (?:h[áa]|possui|acompanham?) anexos|sem anexos", "o edital declara que não possui anexos")
    return {"pontos": P, "dispensas": D, "fim": fim}


DIARIO_URL = re.compile(r"queridodiario|in\.gov\.br|diariooficial|/diario|diariomunicipal|/Download/legislacao/diariooficial|/edicao|/edicoes", re.I)


def _sem_acento(s: str) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", str(s or "").lower()) if unicodedata.category(c) != "Mn")


def localizar_ato(paginas_: list[str], titulo: str, orgao: str = "") -> list[str] | None:
    """Edição inteira de diário: só as páginas do ato (e a seguinte). Procura, nesta ordem: número com ano (003/2026);
    "nº 4" perto de edital/chamamento; os termos entre aspas do título (busca do Querido Diário); o órgão + chamamento.
    Sem nada que identifique o ato: None (nada é extraído, para não atribuir dado de ato vizinho)."""
    pg = [_sem_acento(t) for t in paginas_]
    tit = _sem_acento(titulo)
    idx: list[int] = []
    m = re.search(r"\b(\d{1,4})\s*/\s*(20\d{2})\b", tit)
    if m:
        rx = re.compile(rf"\b0*{int(m.group(1))}\s*/\s*{m.group(2)}\b")
        idx = [i for i, t in enumerate(pg) if rx.search(t)]
    if not idx:
        m = re.search(r"\bn[ºo°.]*\s*0*(\d{1,4})\b", tit)
        if m:
            rx = re.compile(rf"(edital|chamamento|chamada|aviso)[^\n]{{0,60}}\bn[ºo°.]*\s*0*{int(m.group(1))}\b")
            idx = [i for i, t in enumerate(pg) if rx.search(t)]
    if not idx:
        frases = [f for f in re.findall(r'"([^"]{6,80})"', tit)]
        if frases:
            idx = [i for i, t in enumerate(pg) if all(f in t for f in frases)]
    if not idx and orgao:
        o = _sem_acento(orgao)[:40]
        idx = [i for i, t in enumerate(pg) if o and o in t and re.search(r"chamamento publico|edital de selecao|chamada publica", t)]
    if not idx or len(idx) > 6:                              # ausente, ou espalhado demais para ser um ato só
        return None
    manter = {j for i in idx for j in (i, i + 1) if j < len(paginas_)}
    return [t if j in manter else "" for j, t in enumerate(paginas_)]


# ── GABARITO POR ÓRGÃO (v4, 09/10/2026) ────────────────────────────────────────────────────────────────────────────
# Cada órgão tende a usar o mesmo modelo de edital. Ao ler um documento OFICIAL, o Cartório guarda o RÓTULO que vem
# antes de cada valor ("Período de inscrições:", "Valor global do repasse:"); no próximo edital do mesmo órgão, procura
# esses rótulos e aceita o valor só se tiver a FORMA do item (data no prazo, R$ no valor). Nada é inventado: o valor e o
# trecho continuam literais do documento.
FORMA = {"Prazo de inscrição": DATA, "Resultado": DATA + r"|\d+\s*[(\[]?[a-z ]*[)\]]?\s*dias", "Prazo de recurso": DATA + r"|\d+\s*[(\[]?[a-zç ]*[)\]]?\s*dias",
         "Valor": r"R\$\s?\d"}


def chave_orgao(url: str, orgao: str = "") -> str | None:
    """CNPJ do órgão (PNCP), senão o domínio oficial, senão o nome normalizado."""
    m = re.search(r"/orgaos/(\d{14})/", str(url or "")) or re.search(r"/editais/(\d{14})/", str(url or ""))
    if m:
        return "cnpj:" + m.group(1)
    try:
        h = (urlsplit(str(url or "")).hostname or "").lower()
    except ValueError:
        h = ""
    h = re.sub(r"^www\.", "", h)
    if h and GOV.search(h) and h not in ("in.gov.br", "gov.br", "pncp.gov.br", "dados.gov.br", "transferegov.sistema.gov.br"):
        return "dominio:" + h                            # domínio compartilhado por muitos órgãos não é chave de órgão
    o = _sem_acento(orgao)
    return ("orgao:" + re.sub(r"[^a-z0-9]+", " ", o).strip()[:60]) if o.strip() else None


COM_ROTULO = ("Objeto", "Prazo de inscrição", "Resultado", "Prazo de recurso", "Valor", "Requisitos", "Anexos", "Destinação")


def chaves_orgao(url: str, orgao: str = "") -> list[str]:
    """Todas as chaves do órgão (CNPJ/domínio pelo endereço e o nome): o que se aprende por uma vale pela outra."""
    ks = [chave_orgao(url, ""), chave_orgao("", orgao)]
    return [k for k in dict.fromkeys(ks) if k]


def ancora(trecho: str, valor: str) -> str | None:
    """O rótulo que antecede o valor no trecho literal (até 45 caracteres), sem números — o 'endereço' do item."""
    t, v = _sem_acento(trecho), _sem_acento(valor)[:25]
    i = t.find(v) if v else -1
    if i <= 0:
        return None
    a = re.sub(r"\d+", " ", t[max(0, i - 45):i])
    a = re.sub(r"\s+", " ", re.sub(r"[^a-z ]+", " ", a)).strip()
    a = " ".join(a.split()[-5:])
    return a if len(a) >= 8 and len(a.split()) >= 2 else None


def aplicar_gabarito(paginas_: list[str], ancoras: dict, documento: str, ja: set) -> dict:
    """Itens que a extração padrão não achou, procurados pelos rótulos aprendidos deste órgão."""
    T = Texto(paginas_)
    alvo = _sem_acento(T.t)
    out = {}
    for item, lista in (ancoras or {}).items():
        if item in ja:
            continue
        for a in lista:
            rx = r"\s+".join(map(re.escape, a.split()))
            m = re.search(rx + r"[\s:.\-–]*([^\n]{3,260})", alvo)
            if not m:
                continue
            ini, fim = m.start(1), m.end(1)
            fonte = T.t if len(alvo) == len(T.t) else alvo                 # posições batem quando o comprimento se mantém
            bruto = re.sub(r"\s+", " ", fonte[ini:fim]).strip()
            frase = re.split(r"(?<=[.;])\s", bruto)[0]
            f = FORMA.get(item)
            if f:
                mm = re.search(f, frase, re.I)
                if not mm:
                    continue
                valor = frase[:mm.end() + 40].strip(" .;:")
            else:
                if len(frase) < 15 or len(a.split()) < 3:          # sem forma própria: só com rótulo de 3+ palavras
                    continue
                valor = frase
            out[item] = {"valor": valor[:300], "trecho": T.trecho(m.start(), fim), "pagina": T.pagina(m.start()),
                         "documento": documento, "metodo": f"gabarito do órgão (rótulo “{a}”)"}
            break
    return out
