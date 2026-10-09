"""LEITURA DE PDF NOS MOTORES PRINCIPAIS (titular, 09/10/2026).

Diagnóstico que motivou: na leitura de 09/10, só 1 dos 142 motores tinha aberto PDFs (o motor 12, dos Ministérios
Públicos) e os 5 vieram "sem texto". A conferência no navegador do titular (09/10) mostrou que os editais do MPT-GO são
PDFs com camada de texto (Arial com ToUnicode, 2 páginas, application/pdf) — nem escaneados, nem página de erro. Os 5
"sem texto" eram da leitura de 02/10, feita antes de o pypdf ser instalado no passo dos motores (correção de 03/10); a
leitura seguinte do MPT-GO (08/10) já leu 6 editais com valor e prazo. Os demais motores achavam o link do documento
(`pdf_links`, `url_documento` do PNCP) e não abriam o arquivo.

O que este módulo faz: depois que um motor principal (diários oficiais, PNCP e prefeituras) devolve as oportunidades,
abre o DOCUMENTO de cada uma — o PDF anexado (PNCP: às vezes um ZIP com o PDF dentro), o PDF da prefeitura ou a
edição do diário — e extrai os 12 pontos com o MESMO extrator do executor documental (`src/executor_skills.py`):
valor + trecho literal + documento + página. Em edição inteira de diário, só as páginas do ato (localizado pelo número
do edital ou pelas palavras do título) são lidas — o valor de outro ato da mesma edição nunca é atribuído ao edital.

Regras: robots.txt respeitado; conteúdo lido é DADO, nunca instrução (injeção → quarentena, nada é extraído); nada é
inventado (o que o texto não diz fica de fora); o motor continua dono dos seus campos (só preenche o que veio vazio);
orçamento por leitura (documentos e segundos) e memória por endereço em estado/leitura_pdf_motores.json, para não
baixar o mesmo arquivo a cada passagem. Documento sem texto recebe o motivo: `resposta_nao_e_pdf` (página de erro ou
visualizador no lugar do arquivo), `pdf_sem_camada_de_texto` (escaneado), `pdf_cortado_no_limite`, `sem_leitor_pdf`,
`pdf_ilegivel`, `zip_sem_pdf`.
"""
from __future__ import annotations

import io
import re
import time
import unicodedata
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .nucleo import has_prompt_injection, load_json, now_iso, sha256, write_json

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config/leitura_pdf_motores.json"
CACHE = ROOT / "estado/leitura_pdf_motores.json"
PADRAO = {"ativa": True, "motores": ["do-goiania", "do-goias", "dou", "pncp-api", "plat-prefeituras-50-go"],
          "documentos_por_leitura": 6, "segundos_por_leitura": 150, "max_bytes": 30_000_000, "paginas_documento": 40,
          "paginas_edicao": 250, "paginas_do_ato": 3, "memoria_dias": 30, "memoria_max": 800}
DOC_URL = re.compile(r"https://[^\s\"'<>)\]]+?(?:\.pdf\b|\.zip\b|/Download/[^\s\"'<>)\]]+|/wp-content/uploads/[^\s\"'<>)\]]+?\.(?:pdf|docx?)\b|"
                     r"/pncp-api/v1/orgaos/[^\s\"'<>)\]]+?/arquivos/\d+)", re.I)
EDICAO = re.compile(r"(?i)/diariooficial/|queridodiario|/diario[-_]?oficial|/doe[-_/]|/edicao|/edicoes/")
VISUALIZADOR = re.compile(r"(?i)/visualizacoes/pdf/")
NUM_EDITAL = re.compile(r"(?i)n[º°o.]*\s*(\d{1,5})\s*/\s*(\d{4})")


def cfg() -> dict:
    return {**PADRAO, **(load_json(CFG) if CFG.exists() else {})}


def _N(t) -> str:
    t = unicodedata.normalize("NFKD", str(t or "")).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", t).upper()


def documentos_do_achado(a: dict) -> list[str]:
    """Os documentos de uma oportunidade, do mais oficial para o menos: o arquivo anexado (url_documento/url_edital), o
    próprio endereço quando é arquivo, o site oficial quando é arquivo e os links de documento citados no texto."""
    out: list[str] = []
    for k in ("url_documento", "url_edital", "url", "site_oficial", "pagina_oficial"):
        u = str(a.get(k) or "")
        if u.startswith("https://") and (k in ("url_documento", "url_edital") or DOC_URL.fullmatch(u.split("#")[0]) or DOC_URL.match(u)):
            out.append(u.split("#")[0])
    for k in ("documentos", "fontes"):
        for u in a.get(k) or []:
            u = str((u or {}).get("url") if isinstance(u, dict) else u or "")
            if u.startswith("https://") and DOC_URL.match(u):
                out.append(u.split("#")[0])
    for m in DOC_URL.finditer(" ".join(str(a.get(k) or "") for k in ("evidencia", "texto", "descricao"))):
        out.append(m.group(0).rstrip(".,;"))
    return [u for u in dict.fromkeys(out) if not VISUALIZADOR.search(u)]


def _formato(b: bytes, ctype: str) -> str:
    cab = (b or b"")[:1024].lstrip()
    if cab.startswith(b"%PDF"):
        return "pdf"
    if cab.startswith(b"PK"):
        return "zip"
    if re.match(rb"(?i)<(!doctype|html|head|body|\?xml)", cab) or "html" in (ctype or "").lower():
        return "html"
    return "outro"


def _pdfs_do_zip(b: bytes) -> list[tuple[str, bytes]]:
    """PNCP: o órgão às vezes anexa um ZIP. Os PDFs de dentro, o que se chama 'edital' primeiro (até 3, 30 MB)."""
    try:
        z = zipfile.ZipFile(io.BytesIO(b))
    except Exception:  # noqa: BLE001
        return []
    nomes = [i for i in z.infolist() if i.filename.lower().endswith(".pdf") and i.file_size <= 30_000_000 and not i.filename.startswith("__MACOSX")]
    nomes.sort(key=lambda i: (0 if "EDITAL" in _N(i.filename) else 1, i.filename))
    out = []
    for i in nomes[:3]:
        try:
            out.append((i.filename, z.read(i)))
        except Exception:  # noqa: BLE001
            continue
    return out


def ancoras(titulo: str) -> list[re.Pattern]:
    """Como achar o ato dentro da edição: o número do edital (com ou sem zeros à esquerda) e, na falta, as palavras do
    título."""
    pads = []
    for n, ano in NUM_EDITAL.findall(titulo or ""):
        pads.append(re.compile(rf"\b0*{int(n)}\s*/\s*{ano}\b"))
    desc = (titulo or "").split(" — ")[-1]
    ws = [w for w in re.findall(r"[A-Za-zÀ-ú]{4,}", _N(desc))][:6]
    if len(ws) >= 4:
        pads.append(re.compile(r"\W+".join(map(re.escape, ws))))
    return pads


def localizar_ato(paginas: list[str], titulo: str) -> int | None:
    norm = [_N(p) for p in paginas]
    for pad in ancoras(titulo):
        for i, t in enumerate(norm):
            if pad.search(t):
                return i
    return None


def _extrair(paginas: list[str], documento: str) -> dict:
    from .executor_skills import extrair_pontos
    return extrair_pontos(paginas, documento)


def ler_documento(url: str, titulo: str = "", c: dict | None = None, edicao: bool | None = None) -> dict:
    """Um documento: baixa, reconhece o formato (PDF, ZIP com PDF, HTML no lugar do PDF), lê o texto e extrai os 12
    pontos com o extrator do executor documental. Edição inteira de diário: só as páginas do ato."""
    from .executor_skills import baixar, paginas_de_texto, permitido
    c = c or cfg()
    edicao = bool(EDICAO.search(url)) if edicao is None else edicao
    r = {"documento": url, "lido_em": now_iso(), "situacao": "nao_abriu", "motivo": None, "paginas": 0, "pontos": {}}
    try:
        if not permitido(url):
            r.update(situacao="robots", motivo="robots.txt proíbe a leitura automática"); return r
    except Exception:  # noqa: BLE001
        pass
    try:
        b, ctype = baixar(url, max_bytes=int(c["max_bytes"]))
    except Exception as e:  # noqa: BLE001
        r["motivo"] = f"não abriu: {type(e).__name__}"; return r
    r["bytes"] = len(b)
    fmt = _formato(b, ctype)
    alvos: list[tuple[str, bytes]] = []
    if fmt == "zip":
        alvos = _pdfs_do_zip(b); r["formato"] = "zip"
        if not alvos:
            r.update(situacao="sem_texto", motivo="zip_sem_pdf"); return r
    elif fmt == "pdf":
        alvos = [("", b)]; r["formato"] = "pdf"
    else:
        r.update(situacao="sem_texto", formato=fmt, motivo="resposta_nao_e_pdf",
                 nota="o endereço devolveu página (erro, login ou visualizador) no lugar do arquivo"); return r
    if len(b) >= int(c["max_bytes"]):
        r.update(situacao="sem_texto", motivo="pdf_cortado_no_limite", nota=f"arquivo maior que {int(c['max_bytes']) // 1_000_000} MB"); return r
    texto_total = 0
    for nome, pdf in alvos:
        doc = url + (f"#{nome}" if nome else "")
        try:
            pags = paginas_de_texto(pdf, "application/pdf", int(c["paginas_edicao"] if edicao else c["paginas_documento"]))
        except ImportError:
            r.update(situacao="sem_texto", motivo="sem_leitor_pdf", nota="pypdf ausente no ambiente desta leitura"); return r
        except Exception as e:  # noqa: BLE001
            r.update(situacao="sem_texto", motivo="pdf_ilegivel", nota=type(e).__name__); continue
        n_txt = sum(len(p.strip()) for p in pags)
        texto_total += n_txt
        r["paginas"] += len(pags)
        if n_txt < 80:
            continue
        if has_prompt_injection(" ".join(pags)[:200_000]):
            r.update(situacao="quarentena", motivo="conteúdo com instrução dirigida a robô — nada foi extraído", pontos={}); return r
        desloc = 0
        if edicao and len(pags) > 6:
            i = localizar_ato(pags, titulo)
            if i is None:
                r.update(situacao="com_texto", motivo="ato_nao_localizado_na_edicao",
                         nota="a edição tem texto, mas o número/título do ato não foi achado: nada extraído para não misturar atos")
                continue
            desloc = i; pags = pags[i:i + int(c["paginas_do_ato"])]; r["paginas_do_ato"] = [i + 1, i + len(pags)]
        for k, v in _extrair(pags, doc).items():
            if k not in r["pontos"]:
                r["pontos"][k] = {**v, "pagina": int(v.get("pagina") or 1) + desloc}
        if r["pontos"]:
            break
    if r["pontos"]:
        r.update(situacao="com_texto", motivo=None)
    elif texto_total < 80 and r.get("motivo") not in ("pdf_ilegivel",):
        r.update(situacao="sem_texto", motivo="pdf_sem_camada_de_texto", nota="PDF escaneado (imagem): precisa de OCR ou leitura humana")
    elif r["situacao"] != "com_texto" and r.get("motivo") is None:
        r.update(situacao="com_texto", motivo="texto lido, nenhum dos 12 pontos reconhecido")
    return r


def _aplicar(a: dict, r: dict) -> None:
    pts = r.get("pontos") or {}
    a["leitura_documental"] = {k: r.get(k) for k in ("documento", "situacao", "motivo", "nota", "paginas", "paginas_do_ato", "lido_em", "formato") if r.get(k) is not None}
    if pts:
        a["leitura_documental"]["pontos"] = {k: {"valor": v.get("valor"), "trecho": v.get("trecho"), "pagina": v.get("pagina"),
                                                  "documento": v.get("documento")} for k, v in pts.items()}
        a["leitura_documental"]["pontos_lidos"] = len(pts)
        if not a.get("valor_texto") and pts.get("Valor"):
            a["valor_texto"] = pts["Valor"]["valor"]
        if not a.get("prazo_texto") and pts.get("Prazo de inscrição"):
            a["prazo_texto"] = pts["Prazo de inscrição"]["valor"]


def enriquecer(resultado: dict, sensor: dict, c: dict | None = None, agora: float | None = None) -> dict:
    """Pós-leitura de um motor principal: abre os documentos das oportunidades (orçamento por leitura, memória por
    endereço) e registra no diagnóstico quantos PDFs foram abertos, quantos tinham texto e por que os outros não."""
    c = c or cfg()
    if not isinstance(resultado, dict) or not c.get("ativa") or (sensor or {}).get("id") not in set(c.get("motores") or []):
        return resultado
    achados = resultado.get("achados") or []
    diag = resultado.setdefault("diagnostico", {}) if isinstance(resultado.get("diagnostico", {}), dict) else {}
    L = {"documentos": 0, "abertos": 0, "da_memoria": 0, "com_texto": 0, "com_pontos": 0, "sem_texto": 0, "nao_abriu": 0,
         "motivos": {}, "fora_do_orcamento": 0, "versao": "leitura de PDF dos motores (09/10/2026)"}
    mem = load_json(CACHE) if CACHE.exists() else {}
    itens = mem.setdefault("itens", {})
    fim = (agora or time.monotonic()) + float(c["segundos_por_leitura"])
    corte = (datetime.now(timezone.utc) - timedelta(days=int(c["memoria_dias"]))).isoformat()
    novos = 0
    for a in achados:
        if not isinstance(a, dict):
            continue
        docs = documentos_do_achado(a)
        if not docs:
            continue
        L["documentos"] += 1
        u = docs[0]
        k = sha256((u + "|" + str(a.get("titulo") or "")[:120]).encode())[:24]
        r = itens.get(k)
        if r and str(r.get("lido_em") or "") >= corte and r.get("situacao") != "nao_abriu":
            L["da_memoria"] += 1
        elif novos < int(c["documentos_por_leitura"]) and time.monotonic() < fim:
            r = ler_documento(u, str(a.get("titulo") or ""), c)
            novos += 1; L["abertos"] += 1
            itens[k] = {**r, "motor": sensor.get("id"), "titulo": str(a.get("titulo") or "")[:160]}
        else:
            L["fora_do_orcamento"] += 1; continue
        st = r.get("situacao")
        if st == "com_texto":
            L["com_texto"] += 1
            if r.get("pontos"):
                L["com_pontos"] += 1
        elif st == "nao_abriu":
            L["nao_abriu"] += 1
        else:
            L["sem_texto"] += 1
        if r.get("motivo"):
            L["motivos"][r["motivo"][:60]] = L["motivos"].get(r["motivo"][:60], 0) + 1
        _aplicar(a, r)
    if len(itens) > int(c["memoria_max"]):
        mem["itens"] = dict(sorted(itens.items(), key=lambda kv: str(kv[1].get("lido_em") or ""))[-int(c["memoria_max"]):])
    if novos:
        mem["em"] = now_iso()
        write_json(CACHE, mem)
    diag["leitura_pdf"] = L
    # mesma régua do motor 12: o painel soma 'pdfs_lidos' e 'sem_texto' de todos os motores
    diag["pdfs_lidos"] = int(diag.get("pdfs_lidos") or 0) + L["com_texto"] + L["sem_texto"]
    diag["sem_texto"] = int(diag.get("sem_texto") or 0) + L["sem_texto"]
    return resultado
