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
VETOR = re.compile(r"pncp\.gov\.br/(?:app|pncp-api/v1/(?:orgaos/[^/]+/compras/[^/]+/[^/]+)?$)|queridodiario|capitaai|prosas\.com|"
                   r"observatorio3setor|captadores\.org|editaisculturais|bussolasocial|filantropia\.ong|nossacausa|farolcultural|"
                   r"bit\.ly|google\.|facebook\.|instagram\.|linkedin\.|youtube\.|g1\.globo|uol\.com|folha\.|estadao\.|metropoles|"
                   r"jornal|noticia|portaldoterceirosetor|gife\.org\.br/(?!.*edital)", re.I)
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
    if VETOR.search(u):
        return False, "vetor (anúncio, republicador, agregador ou imprensa) — não é fonte"
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
    if re.search(r"(^|\.)(gov\.br|in\.gov\.br)$", h) and not re.search(r"\.[a-z]{2}\.gov\.br$", h):
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
        if re.search(r"(?i)edital|regulamento|inscri|chamamento|chamada|sele[çc][ãa]o|pr[êe]mio|programa", rot + " " + u):
            out.append(u)
    return list(dict.fromkeys(out))[:5]


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
            g = m.group(grupo) if grupo is not None else m.group(0)
            return re.sub(r"\s+", " ", g).strip(), base + m.start(), base + m.end()
    return None


def extrair(paginas_: list[str], documento: str, titulo: str = "", orgao_hint: str = "") -> dict:
    """{'pontos': {item: {valor, trecho, pagina, documento, metodo}}, 'dispensas': {item: {motivo, trecho, pagina}},
    'fim': ISO do prazo de inscrição (quando houver)}."""
    T = Texto(paginas_)
    P, D, fim = {}, {}, None

    def pôr(item, valor, ini, fim_, metodo="seção"):
        if valor and len(str(valor).strip()) >= 3 and item not in P:
            P[item] = {"valor": str(valor).strip()[:300], "trecho": T.trecho(ini, fim_), "pagina": T.pagina(ini),
                       "documento": documento, "metodo": metodo}

    # PRAZO DE INSCRIÇÃO — janela depois da palavra-chave, dentro de INSCRIÇÕES/CRONOGRAMA/PRAZO
    kw = r"(?:per[ií]odo de inscri[çc][õo]es|inscri[çc][õo]es|recebimento d[ae]s? (?:propostas|projetos|inscri)|envio d[ae]s? propostas|submiss[ãa]o d[ae]s? propostas)"
    for sec in (r"INSCRI|CRONOGRAMA|PRAZO", None):
        r = _achar(T, kw + rf"[^.]{{0,160}}?({DATA})(?:[^.\d]{{0,40}}?(?:a|at[ée]|e|ao)\s*({DATA}))?", sec, None)
        if r:
            ds = re.findall(DATA, r[0], re.I)
            isos = [x for x in (_data_iso(d) for d in ds) if x]
            if isos:
                fim = max(isos)
                val = f"{ds[0]} a {ds[-1]}" if len(ds) > 1 else f"até {ds[0]}"
                pôr("Prazo de inscrição", val, r[1], r[2], "cronograma" if sec else "texto")
                break
    # RESULTADO
    r = _achar(T, rf"(?:divulga[çc][ãa]o d[oa]s? )?resultado(?: final| definitivo| preliminar)?[^.]{{0,120}}?({DATA}|\d+\s*[(\[]?[a-z ]*[)\]]?\s*dias)", r"CRONOGRAMA|RESULTADO")
    if r:
        pôr("Resultado", r[0], r[1], r[2])
    # PRAZO DE RECURSO
    r = _achar(T, rf"recurso[s]?[^.]{{0,140}}?(\d+\s*[(\[]?[a-zç ]*[)\]]?\s*dias(?:\s*[úu]teis| corridos)?|{DATA})", r"RECURSO|CRONOGRAMA|RESULTADO")
    if r:
        pôr("Prazo de recurso", r[0], r[1], r[2])
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
                  r"FUNDA[ÇC][ÃA]O|INSTITUTO|FUNDO (?:MUNICIPAL|ESTADUAL|NACIONAL)|AG[ÊE]NCIA|C[ÂA]MARA MUNICIPAL DE|TRIBUNAL|MINIST[ÉE]RIO P[ÚU]BLICO)[^\n,;]{3,90})", cab, re.I)
    if m:
        pôr("Órgão / financiador", re.sub(r"\s+", " ", m.group(1)), m.start(1), m.end(1), "cabeçalho")
    elif orgao_hint:
        r = _achar(T, re.escape(orgao_hint[:40]))
        if r:
            pôr("Órgão / financiador", orgao_hint, r[1], r[2], "texto")
    # TERRITÓRIO
    r = _achar(T, r"(todo o territ[óo]rio nacional|abrang[êe]ncia (?:nacional|estadual|municipal)|(?:no|do) Munic[íi]pio de [A-ZÀ-Ú][\wÀ-ú' ]{2,40}|(?:no|do) Estado d[eoa] [A-ZÀ-Ú][\wÀ-ú ]{2,30})", None, 1, re.S)
    if r:
        pôr("Território", r[0], r[1], r[2], "texto")
    # ESFERA — pelo domínio oficial do documento ou pelo órgão
    esf = esfera_do_dominio(documento)
    org = (P.get("Órgão / financiador") or {}).get("valor", "") + " " + orgao_hint
    if not esf:
        esf = "municipal" if re.search(r"(?i)prefeitura|munic[íi]pio|municipal", org) else "estadual" if re.search(r"(?i)governo do estado|de estado|estadual", org) \
            else "federal" if re.search(r"(?i)minist[ée]rio|uni[ãa]o|federal", org) else "privada" if re.search(r"(?i)instituto|funda[çc][ãa]o|empresa|s\.?a\.?\b|ltda", org) else None
    if esf:
        P["Esfera"] = {"valor": esf, "trecho": f"domínio/órgão: {(urlsplit(documento).hostname or '')} · {org.strip()[:80]}", "pagina": 1,
                       "documento": documento, "metodo": "domínio e órgão"}
    # REQUISITOS
    s = T.secao(r"CONDI|PARTICIPA|REQUISITO|HABILITA")
    if s:
        m = re.search(r"([A-ZÀ-Úa-zà-ú0-9][^.;]{40,350}[.;])", re.sub(r"^\S+(?:\s+\S+){0,4}\s*", "", s[1][:900]))
        if m:
            pôr("Requisitos", m.group(1), s[0], s[0] + 300)
    if "Requisitos" not in P:
        r = _achar(T, r"((?:poder[ãa]o participar|est[ãa]o aptas? a participar|s[ãa]o requisitos|requisitos? (?:para|de) (?:participa|inscri|habilita))[^.;]{20,320}[.;])")
        if r:
            pôr("Requisitos", r[0], r[1], r[2], "texto")
    # ANEXOS
    an = list(dict.fromkeys(re.sub(r"\s+", " ", a).strip() for a in re.findall(r"ANEXO\s+[IVXL]{1,5}\s*[-–—:]?\s*[^\n]{0,70}", T.t)))
    if an:
        i = T.t.find("ANEXO")
        P["Anexos"] = {"valor": "; ".join(an)[:300], "trecho": T.trecho(i, i + 120), "pagina": T.pagina(i), "documento": documento, "metodo": "lista de anexos"}
    # DESTINAÇÃO
    r = _achar(T, r"((?:os |o )?(?:recursos?|valores?|pr[êe]mios?) (?:ser[ãa]o|dever[ãa]o ser|poder[ãa]o ser) (?:destinados?|aplicados?|utilizados?)[^.;]{15,250}[.;]|destina-se a[^.;]{15,250}[.;])",
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


def localizar_ato(paginas_: list[str], titulo: str) -> list[str] | None:
    """Edição inteira de diário: só as páginas em que o número do ato aparece (e a seguinte). Sem número: None."""
    m = re.search(r"\b(\d{1,4})\s*/\s*(20\d{2})\b", titulo or "")
    if not m:
        return None
    rx = re.compile(rf"\b0*{int(m.group(1))}\s*/\s*{m.group(2)}\b")
    idx = [i for i, t in enumerate(paginas_) if rx.search(t or "")]
    if not idx:
        return None
    manter = {j for i in idx for j in (i, i + 1) if j < len(paginas_)}
    return [t if j in manter else "" for j, t in enumerate(paginas_)]
