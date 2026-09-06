"""FONTE ORIGINAL DO EDITAL — do aviso ao documento completo.

O PNCP publica só a divulgação; o edital completo está nos arquivos da própria
contratação (API oficial do PNCP) e/ou no site institucional do órgão
(`linkSistemaOrigem`). Este módulo:
  1. localiza a fonte original (arquivos do PNCP; site institucional; página do
     edital em outras fontes) e baixa até 3 PDFs (≤ 8 MB cada);
  2. extrai o texto (pypdf) e o guarda COMPACTO (gzip, ≤ 120 mil caracteres) em
     dados/editais/textos/<id>.txt.gz — nunca o PDF inteiro no repositório;
  3. extrai deterministicamente o que dá (prazo, valor, objeto, resultado,
     recurso, requisitos, anexos, pontuação) antes de qualquer IA;
  4. entrega o texto compacto para a IA mais barata completar os 12 itens e
     entender regras, requisitos e pontuação — com escalada só se faltar.
"""
from __future__ import annotations

import gzip
import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen

from .nucleo import ROOT, load_json, now_iso, write_json

TEXTOS = ROOT / "dados/editais/textos"
EXTRAIDOS = ROOT / "dados/editais/extraidos"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 Eldorado-OSC/1.0", "From": "contato-via-repositorio",
      "Accept": "application/json,text/html,application/pdf;q=0.9,*/*;q=0.5"}
MAX_PDF = 8_000_000
MAX_TXT = 120_000
DATA = r"(\d{1,2})\s*(?:/|de\s+)\s*(\d{1,2}|janeiro|fevereiro|mar[çc]o|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\s*(?:/|de\s+)\s*(20\d{2})"
MESES = {m: i for i, m in enumerate(["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"], 1)}


def _get(url: str, timeout: int = 25, binario: bool = False, limite: int = MAX_PDF):
    h = dict(UA)
    if "pncp.gov.br/api" in url or "pncp-api" in url:
        h["Accept"] = "application/json"; h["User-Agent"] = "Mozilla/5.0 Eldorado-OSC/1.0"
    req = Request(url, headers=h)
    with urlopen(req, timeout=timeout) as r:
        dados = r.read(limite + 1)
        if len(dados) > limite:
            raise ValueError("arquivo maior que o limite")
        return dados if binario else dados.decode("utf-8", "replace")


def _iso(m) -> str | None:
    try:
        d, mm, a = m.group(1), m.group(2), m.group(3)
        mes = int(mm) if mm.isdigit() else MESES.get(mm.lower().replace("marco", "março"))
        return f"{a}-{int(mes):02d}-{int(d):02d}" if mes else None
    except Exception:
        return None


# ───────────── 1. localizar a fonte original ─────────────
def fontes_originais(e: dict) -> dict:
    """PNCP: arquivos oficiais da contratação + linkSistemaOrigem (site
    institucional). Outras fontes: a própria página, procurando PDFs de edital."""
    url = e.get("url") or ""
    saida = {"site_institucional": None, "pdfs": [], "paginas": [], "origem": None, "erros": []}
    m = re.search(r"pncp\.gov\.br/app/editais/(\d{14})/(\d{4})/(\d+)", url)
    if m:
        cnpj, ano, seq = m.groups(); saida["origem"] = "pncp"
        js = None
        for base in (f"https://pncp.gov.br/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{seq}", f"https://pncp.gov.br/api/consulta/v1/orgaos/{cnpj}/compras/{ano}/{seq}",
                     f"https://pncp.gov.br/pncp-api/v1/orgaos/{cnpj}/compras/{ano}/{seq}"):
            try:
                js = json.loads(_get(base, limite=2_000_000)); saida["endpoint_pncp"] = base; break
            except Exception as exc:
                saida["erros"].append(f"pncp compra ({base.split('/')[3]}): {type(exc).__name__} {getattr(exc, 'code', '')}".strip())
        try:
            if js is None: raise ValueError("sem resposta do PNCP")
            saida["site_institucional"] = js.get("linkSistemaOrigem") or None
            saida["orgao"] = (js.get("orgaoEntidade") or {}).get("razaoSocial"); saida["uf"] = (js.get("unidadeOrgao") or {}).get("ufSigla"); saida["municipio"] = (js.get("unidadeOrgao") or {}).get("municipioNome")
            saida["objeto_pncp"] = js.get("objetoCompra"); saida["encerramento_pncp"] = js.get("dataEncerramentoProposta"); saida["abertura_pncp"] = js.get("dataAberturaProposta")
        except Exception as exc:
            saida["erros"].append(f"pncp compra: {type(exc).__name__}")
        # PNCP é portal de DIVULGAÇÃO: nenhum arquivo é baixado dele. A fonte é o órgão
        # publicador: sistema de origem informado, ou o site institucional deduzido do CNPJ.
        saida["nota_pncp"] = "PNCP tratado como fonte indireta; documentos buscados no site institucional do órgão"
        if not saida["site_institucional"]:
            saida["site_institucional"] = site_institucional_do_orgao(cnpj, saida.get("orgao") or "", saida.get("uf"), saida.get("municipio"))
        if saida["site_institucional"]:
            saida["paginas"].append(saida["site_institucional"])
    elif url.startswith("https://"):
        saida["origem"] = "pagina"; saida["paginas"].append(url)
    # site institucional: a partir da home do órgão, descobrir a página de editais/licitações/chamamentos
    novas = []
    for pg in list(saida["paginas"])[:1]:
        try:
            html = _get(pg, limite=3_000_000)
            for h, rot in re.findall(r'href="([^"]+)"[^>]*>([^<]{0,80})', html):
                if re.search(r"edita|licita|chamament|credenciament|transpar", (rot or "") + h, re.I) and not re.search(r"\.(pdf|jpg|png)$|mailto:|#", h):
                    u = urljoin(pg, h)
                    if u not in saida["paginas"] and u not in novas and len(novas) < 3: novas.append(u)
        except Exception as exc:
            saida["erros"].append(f"home institucional: {type(exc).__name__} ({pg[:60]})")
    saida["paginas"] += novas; saida["paginas_descobertas"] = novas
    # páginas: PDFs de edital linkados
    for pg in list(saida["paginas"])[:4]:
        try:
            html = _get(pg, limite=3_000_000)
            for h, rot in re.findall(r'href="([^"]+)"[^>]*>([^<]{0,120})', html):
                if re.search(r"\.pdf(\?|$)", h, re.I) or re.search(r"edital|anexo|regulamento|termo de refer", rot, re.I):
                    u = urljoin(pg, h)
                    if u.lower().endswith(".pdf") or re.search(r"\.pdf(\?|$)", u, re.I):
                        saida["pdfs"].append({"titulo": rot.strip()[:100] or Path(urlsplit(u).path).name, "tipo": "site institucional", "url": u,
                                              "prioridade": 0 if re.search(r"edital", rot + u, re.I) else 1})
        except Exception as exc:
            saida["erros"].append(f"página {pg[:40]}: {type(exc).__name__}")
    vistos = set(); uniq = []
    for p in sorted(saida["pdfs"], key=lambda x: x["prioridade"]):
        if p.get("url") and p["url"] not in vistos:
            vistos.add(p["url"]); uniq.append(p)
    saida["pdfs"] = uniq
    return saida


def site_institucional_do_orgao(cnpj: str, nome: str, uf: str | None, municipio: str | None) -> str | None:
    """Site oficial do órgão publicador: (a) e-mail corporativo do cadastro público do
    CNPJ; (b) padrão dos portais municipais (www.<cidade>.<uf>.gov.br); (c) None."""
    try:
        js = json.loads(_get(f"https://minhareceita.org/{cnpj}", timeout=15, limite=1_000_000))
        email = (js.get("email") or "").lower()
        dom = email.split("@")[-1] if "@" in email else ""
        if dom and dom.endswith((".gov.br", ".leg.br", ".jus.br", ".mp.br", ".edu.br", ".org.br")) and not dom.startswith(("gmail", "hotmail")):
            return f"https://www.{dom}" if not dom.startswith("www.") else f"https://{dom}"
    except Exception:
        pass
    import unicodedata
    cid = municipio or (re.search(r"(?:MUNIC[ÍI]PIO|PREFEITURA(?: MUNICIPAL)?) D[EA] (.+)", nome or "", re.I) or [None, None])[1]
    if cid and uf:
        slug = re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", cid).encode("ascii", "ignore").decode().lower())
        for cand in (f"https://www.{slug}.{uf.lower()}.gov.br", f"https://{slug}.{uf.lower()}.gov.br"):
            try:
                _get(cand, timeout=12, limite=200_000); return cand
            except Exception:
                continue
    return None


# ───────────── 2. PDF → texto compacto ─────────────
def texto_do_pdf(dados: bytes) -> str:
    import io
    try:
        from pypdf import PdfReader
        rd = PdfReader(io.BytesIO(dados))
        partes = []
        for p in rd.pages[:120]:
            partes.append(p.extract_text() or "")
            if sum(len(x) for x in partes) > MAX_TXT:
                break
        return re.sub(r"[ \t]+", " ", "\n".join(partes))[:MAX_TXT]
    except Exception:
        return ""


def obter_texto(e: dict, maximo_pdfs: int = 3) -> dict:
    """Baixa os PDFs da fonte original, extrai e guarda o texto compactado."""
    TEXTOS.mkdir(parents=True, exist_ok=True)
    f = fontes_originais(e)
    textos, usados = [], []
    for p in f["pdfs"][:maximo_pdfs]:
        try:
            dados = _get(p["url"], binario=True, timeout=40)
            t = texto_do_pdf(dados)
            if len(t) > 200:
                textos.append(f"### {p['titulo']} ({p['tipo']})\n{t}"); usados.append({"titulo": p["titulo"], "url": p["url"], "caracteres": len(t)})
        except Exception as exc:
            f["erros"].append(f"pdf {p['url'][:40]}: {type(exc).__name__}")
    if not textos and f.get("paginas"):
        try:
            html = _get(f["paginas"][0], limite=3_000_000)
            t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S)))
            if len(t) > 300:
                textos.append("### página institucional\n" + t[:MAX_TXT]); usados.append({"titulo": "página institucional", "url": f["paginas"][0], "caracteres": len(t)})
        except Exception as exc:
            f["erros"].append(f"html: {type(exc).__name__}")
    texto = "\n\n".join(textos)[:MAX_TXT]
    arq = TEXTOS / f"{e['id']}.txt.gz"
    if texto:
        with gzip.open(arq, "wt", encoding="utf-8", compresslevel=9) as gz:
            gz.write(texto)
    return {"texto": texto, "arquivo": str(arq.relative_to(ROOT)) if texto else None, "kb_compacto": round(arq.stat().st_size / 1024, 1) if texto else 0,
            "fontes": usados, "site_institucional": f.get("site_institucional"), "pagina_divulgacao": f.get("pagina_divulgacao") or (f["paginas"][0] if f.get("paginas") and f["origem"] == "pagina" and not re.search(r"pncp|in\.gov|queridodiario", f["paginas"][0]) else None), "origem": f.get("origem"), "pncp": {k: f.get(k) for k in ("orgao", "uf", "municipio", "objeto_pncp", "encerramento_pncp", "abertura_pncp") if f.get(k)},
            "erros": f["erros"], "anexos": [{"nome": p["titulo"], "url": p["url"]} for p in f["pdfs"][:12]]}


def texto_guardado(e: dict) -> str:
    arq = TEXTOS / f"{e['id']}.txt.gz"
    if not arq.exists():
        return ""
    with gzip.open(arq, "rt", encoding="utf-8") as gz:
        return gz.read()


# ───────────── 3. extração determinística ─────────────
def extrair_deterministico(texto: str, pncp: dict | None = None) -> dict:
    t = texto; itens = {}; fontes = {}
    def pega(item, rx, grupo=1, conv=None, flags=re.I | re.S):
        m = re.search(rx, t, flags)
        if m:
            v = conv(m) if conv else m.group(grupo).strip()
            if v: itens[item] = v[:300] if isinstance(v, str) else v; fontes[item] = "texto do edital"
    pega("Objeto", r"\b(?:do\s+)?objeto\b[^\n:]{0,40}[:\-–]\s*(.{40,600}?)(?:\n\s*\n|\n\s*\d+\.|\Z)")
    m = re.search(r"(?:inscri[çc][õo]es?|propostas?|habilita[çc][ãa]o)[^.]{0,160}?(?:at[ée]|encerra\w*|prazo\s+final|t[ée]rmino)[^.]{0,40}?" + DATA, t, re.I | re.S)
    if m: itens["Prazo de inscrição"] = _iso(m) or m.group(0)[-10:]; fontes["Prazo de inscrição"] = "texto do edital"
    m = re.search(r"(?:in[íi]cio|abertura)\s+d[ao]s?\s+(?:inscri[çc][õo]es|propostas)[^.]{0,80}?" + DATA, t, re.I | re.S)
    if m: itens["Início das inscrições"] = _iso(m)
    m = re.search(r"(?:divulga[çc][ãa]o|publica[çc][ãa]o)\s+d[oa]\s+resultado[^.]{0,120}?" + DATA, t, re.I | re.S)
    if m: itens["Resultado"] = _iso(m) or m.group(0)[-10:]; fontes["Resultado"] = "texto do edital"
    m = re.search(r"recursos?[^.]{0,80}?prazo\s+de\s+(\d{1,2})\s*\(?[^)]{0,20}\)?\s*dias?(\s+[úu]teis)?", t, re.I)
    if m: itens["Prazo de recurso"] = f"{m.group(1)} dias{m.group(2) or ''}"; fontes["Prazo de recurso"] = "texto do edital"
    m = re.search(r"R\$\s?([\d\.]{4,}(?:,\d{2})?)", t)
    if m: itens["Valor"] = "R$ " + m.group(1); fontes["Valor"] = "texto do edital (primeiro valor citado — conferir)"
    m = re.search(r"\b(?:crit[ée]rios?\s+de\s+(?:avalia[çc][ãa]o|pontua[çc][ãa]o|julgamento)|pontua[çc][ãa]o\s+m[áa]xima)\b(.{0,1200}?)(?:\n\s*\n|\Z)", t, re.I | re.S)
    if m: itens["Pontuação (regras)"] = re.sub(r"\s+", " ", m.group(1)).strip()[:900]
    m = re.search(r"\b(?:requisitos|habilita[çc][ãa]o|documenta[çc][ãa]o\s+(?:exigida|necess[áa]ria)|condi[çc][õo]es\s+de\s+participa[çc][ãa]o)\b(.{0,1400}?)(?:\n\s*\n|\Z)", t, re.I | re.S)
    if m: itens["Requisitos"] = re.sub(r"\s+", " ", m.group(1)).strip()[:900]; fontes["Requisitos"] = "texto do edital"
    anexos = sorted(set(re.findall(r"\bANEXO\s+([IVXLC]+|\d+)\b", t)))
    if anexos: itens["Anexos"] = ", ".join("Anexo " + a for a in anexos[:15]); fontes["Anexos"] = "texto do edital"
    m = re.search(r"(?:destina[çc][ãa]o|finalidade|p[úu]blico[- ]alvo|benefici[áa]rios?)[^.\n]{0,20}[:\-–]\s*(.{30,400}?)(?:\.|\n)", t, re.I | re.S)
    if m: itens["Destinação"] = re.sub(r"\s+", " ", m.group(1)).strip()[:300]; fontes["Destinação"] = "texto do edital"
    docs = sorted({d.lower() for d in re.findall(r"(estatuto social|ata de (?:elei[çc][ãa]o|posse)|certid[ãa]o negativa[^,;.]{0,40}|CNDT|CRF|FGTS|comprovante de endere[çc]o|cart[ãa]o (?:do )?CNPJ|balan[çc]o patrimonial|relat[óo]rio de atividades|inscri[çc][ãa]o no (?:CMAS|CMDCA|CMI|conselho)[^,;.]{0,30})", t, re.I)})
    if pncp:
        if pncp.get("objeto_pncp") and "Objeto" not in itens: itens["Objeto"] = pncp["objeto_pncp"][:300]; fontes["Objeto"] = "PNCP (divulgação)"
        if pncp.get("encerramento_pncp") and "Prazo de inscrição" not in itens: itens["Prazo de inscrição"] = pncp["encerramento_pncp"][:10]; fontes["Prazo de inscrição"] = "PNCP (divulgação)"
        if pncp.get("orgao"): itens["Órgão / financiador"] = pncp["orgao"]; fontes["Órgão / financiador"] = "PNCP"
        if pncp.get("uf"): itens["Território"] = (pncp.get("municipio") + "/" if pncp.get("municipio") else "") + pncp["uf"]; fontes["Território"] = "PNCP"
    return {"itens": itens, "fontes": fontes, "documentos_exigidos_texto": docs[:20], "metodo": "determinístico"}


def conhecimento_regramento(e: dict) -> dict:
    """Itens conhecidos e estáveis de regras permanentes (ex.: Rouanet) registrados
    em config/regramentos.json — fonte 'conhecimento do regramento'."""
    cfg = ROOT / "config/regramentos.json"
    if not cfg.exists():
        return {}
    alvo = f"{e.get('titulo','')} {e.get('fonte_nome','')} {e.get('programa','')}".lower()
    for g in load_json(cfg).get("regramentos", []):
        toks = [x[:6] for x in re.findall(r"[a-zà-ú]{5,}", g["fonte"].lower()) if x not in ("programa", "nacional", "cultura", "edital")]
        esfera = {"federais": ("federal", "câmara", "senado", "união"), "estaduais": ("estadual", "goiás", "alego"), "municipais": ("municipal", "goiânia", "câmara municipal")}
        chave_esf = next((k for k in esfera if k in g["fonte"].lower()), None)
        if toks and any(tk in alvo for tk in toks[:2]) and g.get("itens_conhecidos") and (not chave_esf or any(x in alvo for x in esfera[chave_esf])):
            return {"itens": g["itens_conhecidos"], "fonte": f"conhecimento do regramento ({g['fonte']}) — {g.get('nota_itens_conhecidos','')}", "pagina": g.get("pagina_oficial")}
    return {}


def relatorio(reg: dict, e: dict, credencial: bool) -> dict:
    """Relatório da pesquisa fina: o que foi feito, o que rendeu, o que falhou —
    e o que só cabe a mão humana quando a IA falhou de fato."""
    etapas = []
    fontes = reg.get("fontes") or []; erros = reg.get("erros") or []
    if reg.get("origem") == "pncp":
        etapas.append({"etapa": "PNCP (fonte indireta — só divulgação, nada é baixado dali)", "ok": bool(reg.get("pncp") or reg.get("endpoint_pncp")), "detalhe": "divulgação lida; fonte oficial = órgão publicador" if reg.get("pncp") else "a API do PNCP não respondeu para esta contratação"})
    if reg.get("site_institucional"):
        etapas.append({"etapa": "site institucional do órgão", "ok": True, "detalhe": reg["site_institucional"], "link": reg["site_institucional"]})
    elif reg.get("origem") == "pncp":
        etapas.append({"etapa": "site institucional do órgão", "ok": False, "detalhe": "não localizado: o PNCP não informou o sistema de origem e o cadastro do CNPJ não trouxe domínio oficial — indicar o site manualmente"})
    etapas.append({"etapa": "documentos do edital (PDF/anexos)", "ok": bool(fontes), "detalhe": f"{len(fontes)} arquivo(s) lido(s), texto compacto de {reg.get('kb_compacto') or 0} KB" if fontes else "nenhum PDF/anexo acessível: " + ("; ".join(erros[:3]) or "sem link de documento na fonte")})
    itens = reg.get("itens") or {}; fi = reg.get("fontes_itens") or {}
    det = [k for k, v in fi.items() if "texto do edital" in v or "PNCP" in v]; ia = [k for k, v in fi.items() if v.startswith("IA")]; con = [k for k, v in fi.items() if "regramento" in v]; man = [k for k, v in fi.items() if "complemento" in v]
    etapas.append({"etapa": "extração determinística", "ok": bool(det), "detalhe": f"{len(det)} item(ns): {', '.join(det[:6])}" if det else "nada extraível do texto"})
    tent = reg.get("tentativas") or []
    if not credencial:
        etapas.append({"etapa": "IA (haiku → sonnet)", "ok": False, "detalhe": "NÃO EXECUTADA: a credencial FAROL_AI_API_KEY não está registrada nos segredos do repositório (Settings → Secrets and variables → Actions)", "acao": "registrar_credencial"})
    elif tent:
        ult = tent[-1]; etapas.append({"etapa": "IA (haiku → sonnet)", "ok": ult.get("status") == "respondeu", "detalhe": f"{len(tent)} chamada(s); última {ult.get('modelo')}: {ult.get('status')}; itens pela IA: {', '.join(ia) or 'nenhum'}"})
    else:
        etapas.append({"etapa": "IA (haiku → sonnet)", "ok": False, "detalhe": "sem texto do edital para a IA ler — a fonte não entregou documentos"})
    if con: etapas.append({"etapa": "conhecimento do regramento", "ok": True, "detalhe": f"{len(con)} item(ns) de regra permanente: {', '.join(con[:6])}"})
    if man: etapas.append({"etapa": "complemento manual", "ok": True, "detalhe": ", ".join(man)})
    faltam = reg.get("faltam") or []
    ia_falhou = (not credencial) or (tent and tent[-1].get("status") != "respondeu") or (not fontes and faltam)
    manual = None
    if faltam and ia_falhou:
        links = [x for x in ([reg.get("site_institucional")] + [p.get("url") for p in (reg.get("anexos") or [])[:3]] + [e.get("url")]) if x]
        manual = {"motivo": "a IA não conseguiu acessar/extrair os documentos" if fontes or credencial else "sem documentos acessíveis e sem IA", "itens": faltam, "links": links[:4],
                  "instrucao": "abra a fonte, localize o edital e use 'subir informação faltante' com os itens listados"}
    return {"etapas": etapas, "completo": not faltam, "faltam": faltam, "manual": manual, "situacao": "pesquisa completa" if not faltam else ("pesquisa incompleta — ação manual indicada" if manual else "pesquisa incompleta — nova tentativa na próxima saída")}


def mini_parecer_deterministico(reg: dict, e: dict) -> str:
    it = reg.get("itens") or {}
    partes = []
    if it.get("Objeto"): partes.append(f"Objeto: {str(it['Objeto'])[:160]}.")
    if it.get("Valor"): partes.append(f"Valor: {str(it['Valor'])[:140]}.")
    if it.get("Prazo de inscrição"): partes.append(f"Inscrições até {it['Prazo de inscrição']}.")
    if it.get("Requisitos"): partes.append(f"Requisitos: {str(it['Requisitos'])[:160]}.")
    if reg.get("pontuacao"): partes.append("Pontuação: " + "; ".join(f"{c.get('criterio')} ({c.get('peso')})" for c in reg["pontuacao"][:4]) + ".")
    if reg.get("faltam"): partes.append(f"Ainda não compreendido: {', '.join(reg['faltam'])}.")
    return " ".join(partes) or "Sem elementos suficientes para parecer — a fonte não entregou o edital."


def prompt_extracao(e: dict, texto: str, faltam: list[str]) -> str:
    return (f"Você extrai dados de editais para o terceiro setor. Edital: {e.get('titulo')} ({e.get('fonte_nome')}).\n"
            f"Texto do edital (compacto, pode estar truncado):\n\"\"\"\n{texto[:60000]}\n\"\"\"\n"
            f"Preencha SOMENTE os itens que faltam: {', '.join(faltam)}. Além disso: regras do edital em 3 a 6 frases, requisitos de habilitação "
            "(lista objetiva), critérios de pontuação com pesos, documentos exigidos (lista de nomes padronizados: estatuto, ata_eleicao, cnpj, "
            "certidao_federal, certidao_estadual, certidao_municipal, cndt, crf_fgts, comprovante_endereco, plano_de_trabalho, relatorio_atividades, "
            "inscricao_conselho, cebas, conta_bancaria), e anexos/modelos citados. Responda SOMENTE JSON: {\"itens\": {<item>: <valor ou null>}, "
            "\"regras\": <texto>, \"requisitos\": [<lista>], \"pontuacao\": [{\"criterio\": <texto>, \"peso\": <número ou null>}], "
            "\"documentos_exigidos\": [<lista>], \"anexos\": [<lista>], \"mini_parecer\": <3 a 5 frases sobre as especificidades deste edital para uma OSC: quem pode, o que financia, como pontua, armadilhas>, "
            "\"confianca\": <0-1>}. Nunca invente: sem base no texto, null.")


def investigar(e: dict, chamar, modelos: list[str], forcar: bool = False, rede: bool = True) -> dict:
    """Pipeline completo e imediato: fonte original → texto compacto → extração
    determinística → IA barata → IA reforço só se ainda faltar. Guarda em
    dados/editais/extraidos/<id>.json."""
    EXTRAIDOS.mkdir(parents=True, exist_ok=True)
    arq = EXTRAIDOS / f"{e['id']}.json"
    reg = load_json(arq) if arq.exists() else {"edital_id": e["id"], "titulo": e.get("titulo"), "tentativas": []}
    if reg.get("completo") and not forcar:
        return reg
    # sem repetição: se as duas últimas tentativas não avançaram e nada mudou (sem texto novo nem complemento), aguarda
    ult = (reg.get("tentativas") or [])[-2:]
    if not forcar and len(ult) == 2 and all(t.get("itens_obtidos", 0) == 0 for t in ult) and reg.get("caracteres_texto") == len(texto_guardado(e)) and not complementos_mudaram(e, reg):
        reg["aguardando"] = "sem avanço nas duas últimas tentativas — aguardando texto novo ou complemento manual"
        return reg
    texto = texto_guardado(e)
    if rede and (not texto or forcar):
        ob = obter_texto(e); texto = ob["texto"]
        reg.update({k: ob[k] for k in ("arquivo", "kb_compacto", "fontes", "site_institucional", "pagina_divulgacao", "origem", "pncp", "erros", "anexos")})
    det = extrair_deterministico(texto, reg.get("pncp")) if texto else {"itens": {}, "fontes": {}, "documentos_exigidos_texto": [], "metodo": "sem texto"}
    itens = dict(reg.get("itens") or {}); fontes = dict(reg.get("fontes_itens") or {})
    # o que o motor já sabe do edital entra como piso (fonte: cadastro do motor)
    semente = {"Objeto": e.get("objeto") or e.get("resumo"), "Prazo de inscrição": e.get("fim"), "Órgão / financiador": e.get("fonte_nome"),
               "Território": e.get("uf") or ("Brasil" if e.get("abrangencia") == "nacional" else None), "Esfera": e.get("nivel"),
               "Área de atuação": e.get("area") if e.get("area") not in (None, "outros") else None, "Valor": e.get("valor_texto")}
    for k, v in semente.items():
        if v and not itens.get(k): itens[k] = str(v)[:300]; fontes[k] = "cadastro do edital (motor de busca)"
    for k, v in det["itens"].items():
        if k not in itens: itens[k] = v; fontes[k] = det["fontes"].get(k, "texto do edital")
    conh = conhecimento_regramento(e)
    for k, v in (conh.get("itens") or {}).items():
        if not itens.get(k): itens[k] = v; fontes[k] = conh["fonte"]
    if conh.get("pagina") and not reg.get("site_institucional"): reg["site_institucional"] = conh["pagina"]
    alvo = ["Objeto", "Prazo de inscrição", "Resultado", "Prazo de recurso", "Valor", "Órgão / financiador", "Território", "Esfera", "Requisitos", "Anexos", "Destinação", "Área de atuação"]
    faltam = [i for i in alvo if not itens.get(i)]
    # IA em escalada: só sobre o que falta, com o texto compacto
    for i, modelo in enumerate(modelos):
        if not faltam or not texto:
            break
        if i == 2 and len(faltam) < 3:
            break                                     # Opus só se ainda faltarem 3 ou mais itens
        r = chamar(modelo, prompt_extracao(e, texto, faltam), 1600, web=(len(texto) < 800), tarefa=f"edital:{e['id']}")
        novos = 0
        if r.get("status") == "respondeu":
            for k, v in (r.get("itens") or {}).items():
                if v and not itens.get(k): itens[k] = v; fontes[k] = f"IA ({modelo}) sobre o texto do edital"; novos += 1
        reg["tentativas"].append({"em": now_iso(), "modelo": modelo, "status": r.get("status"), "faltavam": list(faltam), "uso": r.get("uso"), "itens_obtidos": novos,
                                  "sinal": "verde" if novos else ("amarelo" if r.get("status") == "respondeu" else "vermelho")})
        if r.get("status") != "respondeu":
            break
        for k in ("regras", "requisitos", "pontuacao", "documentos_exigidos", "anexos_ia", "confianca", "mini_parecer"):
            src_k = "anexos" if k == "anexos_ia" else k
            if r.get(src_k) not in (None, "", []): reg[k] = r[src_k]
        faltam = [i for i in alvo if not itens.get(i)]
    import os as _os
    reg["relatorio"] = relatorio({**reg, "itens": itens, "fontes_itens": fontes, "faltam": faltam}, e, bool(_os.environ.get("FAROL_AI_API_KEY")))
    reg["mini_parecer"] = reg.get("mini_parecer") or mini_parecer_deterministico({**reg, "itens": itens, "faltam": faltam}, e)
    reg.update({"itens": itens, "fontes_itens": fontes, "faltam": faltam, "completo": not faltam, "metodo": det["metodo"],
                "documentos_exigidos": reg.get("documentos_exigidos") or _padroniza_docs(det["documentos_exigidos_texto"]),
                "pontuacao_texto": det["itens"].get("Pontuação (regras)"), "atualizado_em": now_iso(), "caracteres_texto": len(texto)})
    write_json(arq, reg)
    return reg


def complementos_mudaram(e: dict, reg: dict) -> bool:
    from .enquadramento import complementos
    return bool(set(complementos(e)) - set(reg.get("itens") or {}))


def _padroniza_docs(lista: list[str]) -> list[str]:
    mapa = [("estatuto", "estatuto"), ("ata de", "ata_eleicao"), ("cndt", "cndt"), ("crf", "crf_fgts"), ("fgts", "crf_fgts"), ("endere", "comprovante_endereco"),
            ("cnpj", "cnpj"), ("balan", "balanco_patrimonial"), ("relat", "relatorio_atividades"), ("inscri", "inscricao_conselho"),
            ("federal", "certidao_federal"), ("estadual", "certidao_estadual"), ("municipal", "certidao_municipal"), ("certid", "certidao_federal")]
    saida = []
    for d in lista:
        for k, v in mapa:
            if k in d and v not in saida:
                saida.append(v); break
    return saida
