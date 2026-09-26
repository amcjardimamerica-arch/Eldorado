"""O INVESTIGADOR — responde às DOZE perguntas de cada edital aberto, com prova literal (titular, 26/09).

Uma missão só: quando o botão «Investigar com IA» é acionado, um modelo maior (Qwen3-8B) lê a página
oficial e os anexos de cada edital aberto e responde às doze perguntas da ficha — objeto, prazo de
inscrição, resultado, prazo de recurso, valor, órgão/financiador, território, esfera, requisitos, anexos,
destinação, área de atuação.

VALIDAÇÃO CONFIÁVEL: cada resposta vem com um TRECHO LITERAL; o trecho é procurado no texto lido e só o que
está lá é aceito. Resposta sem trecho ou com trecho que não existe na fonte é registrada como "não comprovado"
e NÃO entra na ficha. Nenhum prazo é gravado sem trecho: a regra do cargo (prazo inventado elimina) vale
para o Investigador tanto quanto para o Piloto.

O que se grava, no registro do edital (dados/editais/extraidos/<id>.json):
    campos padrão que a ficha já lê (objeto, inicio/fim, marcos, valor_texto, orgao, uf, nivel,
    detalhes.documentos_exigidos, anexos, destinacao, area) — só os comprovados;
    investigacao_ia: modelo, fontes lidas, cada campo com valor, trecho e se foi comprovado.
"""
from __future__ import annotations

import json
import re
import time
import unicodedata
import urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
EXTRAIDOS = ROOT / "dados/editais/extraidos"
SAIDA = ROOT / "docs/dados/investigacoes_ia.json"
UA = {"User-Agent": "Mozilla/5.0 (Eldorado Investigador; associacao sem fins lucrativos)"}

DOZE = ["Objeto", "Prazo de inscrição", "Resultado", "Prazo de recurso", "Valor", "Órgão / financiador",
        "Território", "Esfera", "Requisitos", "Anexos", "Destinação", "Área de atuação"]

ESQUEMA = {
    "objeto": {"valor": "o que o edital financia, em uma frase", "trecho": "trecho literal"},
    "prazo_inscricao": {"inicio": "AAAA-MM-DD ou null", "fim": "AAAA-MM-DD ou null", "trecho": "trecho literal com a data"},
    "resultado": {"data": "AAAA-MM-DD ou null", "trecho": "trecho literal"},
    "prazo_recurso": {"inicio": "AAAA-MM-DD ou null", "fim": "AAAA-MM-DD ou null", "trecho": "trecho literal"},
    "valor": {"valor": "valor por projeto ou total, como está escrito", "trecho": "trecho literal"},
    "orgao": {"valor": "quem publica e financia", "trecho": "trecho literal"},
    "territorio": {"uf": "sigla ou null", "abrangencia": "nacional|estadual|municipal|regional", "trecho": "trecho literal"},
    "esfera": {"valor": "federal|estadual|municipal|privada", "trecho": "trecho literal"},
    "requisitos": {"lista": ["documento ou exigência"], "trecho": "trecho literal"},
    "anexos": {"lista": [{"nome": "nome do anexo", "url": "endereço ou null"}], "trecho": "trecho literal"},
    "destinacao": {"elegivel": "true se organização da sociedade civil pode concorrer", "natureza": "fomento|premio|patrocinio|convenio|outro", "trecho": "trecho literal"},
    "area": {"valor": "cultura|educacao|saude|assistencia_social|esporte|meio_ambiente|direitos|outros", "trecho": "trecho literal"},
}


# ── leitura da fonte ─────────────────────────────────────────────────────────────────────────
class _Texto(HTMLParser):
    def __init__(self):
        super().__init__(); self.partes = []; self.links = []; self._skip = 0; self._h = None
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"): self._skip += 1
        if tag == "a": self._h = dict(attrs).get("href")
        if tag in ("p", "div", "li", "br", "tr", "h1", "h2", "h3", "h4", "td"): self.partes.append("\n")
    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript"): self._skip = max(0, self._skip - 1)
        if tag == "a": self._h = None
    def handle_data(self, d):
        if not self._skip: self.partes.append(d)
        if self._h: self.links.append((self._h, d.strip()))


def _baixar(url: str, tempo: int = 40) -> tuple[bytes, str]:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=tempo) as r:
        return r.read(15_000_000), (r.headers.get("Content-Type") or "")


def _pdf_texto(dados: bytes) -> str:
    try:
        from pypdf import PdfReader
        import io
        rd = PdfReader(io.BytesIO(dados))
        return "\n".join((p.extract_text() or "") for p in rd.pages[:60])
    except Exception:
        return ""


def texto_do_edital(e: dict) -> tuple[str, list[dict]]:
    """A página oficial primeiro, depois o que o registro já tem, depois os anexos em PDF."""
    fontes, textos, vistos = [], [], set()
    urls = [e.get("pagina_oficial"), ((e.get("validacao") or {}).get("site")), e.get("url")]
    # anexos já registrados entram só se o nome parecer o edital (não manuais, planos ou relatórios)
    urls += [a.get("url") for a in (e.get("anexos") or []) if isinstance(a, dict) and a.get("url")
             and re.search(r"edital|anexo|regulamento|chamamento|termo|formul|inscri", f"{a.get('nome', '')} {a.get('url', '')}", re.I)]
    for u in [u for u in urls if u and str(u).startswith("http")]:
        if u in vistos or re.search(r"duckduckgo|bing\.com|google\.", u): continue
        vistos.add(u)
        try:
            dados, tipo = _baixar(u)
        except Exception as ex:
            fontes.append({"url": u, "ok": False, "erro": type(ex).__name__}); continue
        # PDF pelo CONTEÚDO: o PNCP entrega o edital sem se anunciar como PDF, e os 303 mil caracteres de
        # binário lidos como página deram 0/12 nos dois modelos
        if dados[:5] == b"%PDF-" or "pdf" in tipo.lower() or u.lower().endswith(".pdf"):
            t = _pdf_texto(dados); fontes.append({"url": u, "ok": bool(t), "tipo": "pdf", "chars": len(t)})
        else:
            p = _Texto(); p.feed(dados.decode("utf-8", "ignore")); t = re.sub(r"[ \t]+", " ", "".join(p.partes)); t = re.sub(r"\n{3,}", "\n\n", t)
            fontes.append({"url": u, "ok": bool(t.strip()), "tipo": "html", "chars": len(t)})
            # anexos em PDF linkados na página oficial entram também (até 4)
            for h, rot in p.links:
                full = urljoin(u, h or "")
                parece_edital = re.search(r"edital|anexo|regulamento|chamamento|termo|formul|inscri|sele[cç]", f"{rot} {full}", re.I)
                if full.lower().endswith(".pdf") and parece_edital and full not in vistos and len([f for f in fontes if f.get("tipo") == "pdf"]) < 3:
                    vistos.add(full)
                    try:
                        d2, _ = _baixar(full); t2 = _pdf_texto(d2)
                        fontes.append({"url": full, "ok": bool(t2), "tipo": "pdf", "nome": rot[:80], "chars": len(t2)})
                        if t2: textos.append(f"\n\n=== ANEXO: {rot[:80]} ({full}) ===\n{t2}")
                    except Exception as ex:
                        fontes.append({"url": full, "ok": False, "tipo": "pdf", "erro": type(ex).__name__})
        if t.strip():
            textos.append(f"\n\n=== FONTE: {u} ===\n{t}")
    return "".join(textos), fontes


# ── validação: o trecho tem de existir na fonte ──────────────────────────────────────────────
def _norm(s: str) -> str:
    # NFKD desfaz ligaduras de PDF (ﬁ → fi); a hifenização de fim de linha é juntada antes de normalizar
    s = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", str(s or ""))
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def comprovado(trecho: str, texto_norm: str, curto_ok: bool = False) -> bool:
    t = _norm(trecho)
    if len(t) < 12:
        return bool(curto_ok and len(t) >= 4 and re.search(r"(^| )" + re.escape(t) + r"( |$)", texto_norm))
    if t in texto_norm:
        return True
    # TEXTO DE PDF NÃO BATE LETRA POR LETRA (26/09): o 8B copiou 'Fundação Maria Emília Pedreira Freire De
    # Carvalho, CNPJ…' — que está no edital — e o validador rejeitou. Agora vale a janela: 85% das palavras
    # do trecho aparecem juntas, num trecho do texto de até 1,5× o tamanho. Continua exigindo a prova no texto.
    pal = [w for w in t.split() if len(w) > 2]
    if len(pal) < 4:
        return False
    tw = texto_norm.split()
    alvo = set(pal); n = len(pal); larg = int(n * 1.5) + 2
    rara = min(pal, key=lambda w: texto_norm.count(" " + w + " ") or 10**9)
    for i, w in enumerate(tw):
        if w != rara:
            continue
        janela = set(tw[max(0, i - larg): i + larg])
        if len(alvo & janela) >= 0.85 * len(alvo):
            return True
    return False


def _data(v) -> str | None:
    s = str(v or "")
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", s) or None
    if m: return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}" if m else None


# ── as doze perguntas ────────────────────────────────────────────────────────────────────────
PROMPT = """Você é o Investigador da Biblioteca de Alexandria. Leia o TEXTO DA FONTE abaixo — a página oficial e os anexos de
um edital — e responda às DOZE perguntas da ficha. REGRAS:
1. Responda SOMENTE com o que está escrito no texto. Cada campo traz um "trecho": copie LITERALMENTE de 30 a 200
   caracteres do texto que provam a resposta. Se não houver trecho, deixe o valor null e o trecho vazio.
2. Nunca invente data, valor ou órgão. Datas no formato AAAA-MM-DD.
3. "destinacao.elegivel" é true só se o texto disser que organizações da sociedade civil, associações, ONGs,
   entidades sem fins lucrativos ou coletivos podem concorrer.
4. Devolva APENAS o JSON, exatamente com as chaves do esquema.

EDITAL: {titulo}
ESQUEMA: {esquema}

TEXTO DA FONTE (pode estar truncado):
{texto}
"""


def _recortar(texto: str, limite: int = 42_000) -> str:
    """Cabe no contexto: o começo inteiro e, se faltar, janelas em volta das palavras que importam."""
    if len(texto) <= limite:
        return texto
    cab = texto[: int(limite * 0.55)]
    resto = texto[int(limite * 0.55):]
    janelas, usados = [], 0
    for m in re.finditer(r"(?i)inscri|prazo|resultado|recurso|valor|r\$|objeto|anexo|habilita|requisito|elegív|poder[aã]o participar", resto):
        a, b = max(0, m.start() - 350), min(len(resto), m.end() + 500)
        if janelas and a < janelas[-1][1]:
            janelas[-1] = (janelas[-1][0], b)
        else:
            janelas.append((a, b))
        usados += b - a
        if usados > limite - len(cab):
            break
    return cab + "".join(f"\n[...]\n{resto[a:b]}" for a, b in janelas)


def responder(ia, e: dict, texto: str) -> dict | None:
    return ia.perguntar(PROMPT.format(titulo=(e.get("titulo") or "")[:160], esquema=json.dumps(ESQUEMA, ensure_ascii=False),
                                      texto=_recortar(texto)), json.dumps(ESQUEMA, ensure_ascii=False))


def aplicar(e: dict, r: dict, texto: str, fontes: list[dict], modelo: str) -> dict:
    """Só o comprovado entra na ficha; tudo fica registrado em investigacao_ia."""
    tn = _norm(texto)
    campos = {}
    def ok(bloco, curto=False):
        return isinstance(bloco, dict) and comprovado(bloco.get("trecho") or "", tn, curto)
    g = lambda k: r.get(k) if isinstance(r.get(k), dict) else {}
    # Objeto
    b = g("objeto"); c = ok(b) and bool(b.get("valor")); campos["Objeto"] = {"valor": b.get("valor"), "trecho": b.get("trecho"), "comprovado": c}
    if c: e["objeto"] = str(b["valor"])[:400]
    # Prazo de inscrição
    b = g("prazo_inscricao"); fim = _data(b.get("fim")); ini = _data(b.get("inicio")); c = ok(b) and bool(fim)
    if c and fim < (date.today() - __import__("datetime").timedelta(days=365)).isoformat():
        c = False; b = {**b, "trecho": (b.get("trecho") or "") + " [rejeitado: data implausível para edital aberto]"}
    campos["Prazo de inscrição"] = {"valor": f"{ini or '?'} a {fim}" if fim else None, "trecho": b.get("trecho"), "comprovado": c}
    if c:
        e["fim"] = fim; e["inicio"] = ini or e.get("inicio"); e["prazo_texto"] = str(b.get("trecho"))[:160]; e["situacao"] = "aberta" if fim >= date.today().isoformat() else "encerrada"
    # Resultado e recurso → marcos
    marcos = [m for m in (e.get("marcos") or []) if m.get("tipo") not in ("resultado_final", "recurso")]
    b = g("resultado"); d = _data(b.get("data")); c = ok(b) and bool(d)
    campos["Resultado"] = {"valor": d, "trecho": b.get("trecho"), "comprovado": c}
    if c: marcos.append({"tipo": "resultado_final", "data": d, "trecho": str(b.get("trecho"))[:160]})
    b = g("prazo_recurso"); d1, d2 = _data(b.get("inicio")), _data(b.get("fim")); c = ok(b) and bool(d2 or d1)
    campos["Prazo de recurso"] = {"valor": f"{d1 or '?'} a {d2 or '?'}" if (d1 or d2) else None, "trecho": b.get("trecho"), "comprovado": c}
    if c: marcos.append({"tipo": "recurso", "data": d2 or d1, "inicio": d1, "fim": d2, "trecho": str(b.get("trecho"))[:160]})
    if marcos: e["marcos"] = marcos
    # Valor
    b = g("valor"); c = ok(b) and bool(b.get("valor")); campos["Valor"] = {"valor": b.get("valor"), "trecho": b.get("trecho"), "comprovado": c}
    if c: e["valor_texto"] = str(b["valor"])[:160]
    # Órgão
    b = g("orgao"); c = ok(b) and bool(b.get("valor")); campos["Órgão / financiador"] = {"valor": b.get("valor"), "trecho": b.get("trecho"), "comprovado": c}
    if c: e["orgao"] = str(b["valor"])[:160]
    # Território
    b = g("territorio"); c = ok(b, True) and bool(b.get("uf") or b.get("abrangencia")); campos["Território"] = {"valor": b.get("uf") or b.get("abrangencia"), "trecho": b.get("trecho"), "comprovado": c}
    if c:
        if b.get("uf") and re.fullmatch(r"[A-Z]{2}", str(b["uf"]).upper()): e["uf"] = str(b["uf"]).upper()
        if b.get("abrangencia") == "nacional": e["abrangencia"] = "nacional"
    # Esfera
    b = g("esfera"); v = str(b.get("valor") or "").lower(); c = ok(b, True) and v in ("federal", "estadual", "municipal", "privada")
    campos["Esfera"] = {"valor": v or None, "trecho": b.get("trecho"), "comprovado": c}
    if c and v in ("federal", "estadual", "municipal"): e["nivel"] = v
    # Requisitos
    b = g("requisitos"); lista = [str(x)[:120] for x in (b.get("lista") or []) if x][:20]; c = ok(b) and bool(lista)
    campos["Requisitos"] = {"valor": ", ".join(lista)[:300] or None, "trecho": b.get("trecho"), "comprovado": c}
    if c: e.setdefault("detalhes", {})["documentos_exigidos"] = lista
    # Anexos — os PDFs realmente lidos contam como comprovação
    lidos = [{"nome": f.get("nome") or urlsplit(f["url"]).path.split("/")[-1], "url": f["url"]} for f in fontes if f.get("tipo") == "pdf" and f.get("ok")]
    b = g("anexos"); decl = [{"nome": str(x.get("nome") or "")[:80], "url": x.get("url")} for x in (b.get("lista") or []) if isinstance(x, dict) and x.get("nome")]
    c = bool(lidos) or (ok(b) and bool(decl))
    campos["Anexos"] = {"valor": f"{len(lidos or decl)} anexo(s)" if (lidos or decl) else None, "trecho": b.get("trecho"), "comprovado": c}
    if c: e["anexos"] = lidos or decl
    # Destinação
    b = g("destinacao"); el = str(b.get("elegivel")).lower() in ("true", "1", "sim"); c = ok(b)
    campos["Destinação"] = {"valor": ("elegível" if el else "fora do escopo") + (f" · {b.get('natureza')}" if b.get("natureza") else ""), "trecho": b.get("trecho"), "comprovado": c}
    if c: e["destinacao"] = {"elegivel": el, "natureza": b.get("natureza"), "motivo": str(b.get("trecho"))[:160]}
    # Área
    b = g("area"); _areas = ("cultura", "educacao", "saude", "assistencia_social", "esporte", "meio_ambiente", "direitos")
    v = next((a for a in re.split(r"[|,;/ ]+|\be\b", _norm(b.get("valor") or "").replace("assistencia social", "assistencia_social").replace("meio ambiente", "meio_ambiente")) if a in _areas), "")
    c = ok(b, True) and bool(v)
    campos["Área de atuação"] = {"valor": v or None, "trecho": b.get("trecho"), "comprovado": c}
    if c: e["area"] = v
    # DE ONDE VEIO A PROVA: cada trecho comprovado é localizado na fonte que o contém (oficial ou divulgação)
    blocos = re.split(r"\n\n=== (?:FONTE|ANEXO): ", texto)
    dom_of = (urlsplit(e.get("pagina_oficial") or "").hostname or "").replace("www.", "")
    for k, v in campos.items():
        if not v.get("comprovado") or not v.get("trecho"):
            continue
        for bl in blocos[1:]:
            cab, _, corpo = bl.partition(" ===\n")
            if comprovado(v["trecho"], _norm(corpo), True):
                url = re.search(r"https?://\S+?(?=\)|$|\s)", cab)
                u = url.group(0) if url else cab[:120]
                v["fonte"] = u
                v["fonte_oficial"] = bool(dom_of) and dom_of in (urlsplit(u).hostname or "")
                break
    n = sum(1 for v in campos.values() if v["comprovado"])
    e["investigacao_ia"] = {"em": time.strftime("%Y-%m-%dT%H:%M:%S"), "modelo": modelo, "fontes": fontes, "campos": campos,
                            "comprovados": n, "total": len(DOZE),
                            "regra": "só entra na ficha o que tem trecho literal encontrado na fonte"}
    e["confirmacao"] = f"investigado pela IA ({modelo}) em {time.strftime('%d/%m/%Y')}: {n}/{len(DOZE)} itens comprovados"
    return e["investigacao_ia"]


MESTRE = ROOT / "dados/oportunidades/oportunidades.jsonl"


_MESTRE_IDX: dict | None = None


def _mestre() -> dict:
    """Índice do arquivo mestre por id, montado uma vez (17 mil linhas; varrer por id era lento demais)."""
    global _MESTRE_IDX
    if _MESTRE_IDX is None:
        _MESTRE_IDX = {}
        if MESTRE.exists():
            for l in MESTRE.open(encoding="utf-8"):
                try:
                    d = json.loads(l)
                except ValueError:
                    continue
                if d.get("id"):
                    _MESTRE_IDX[d["id"]] = d
    return _MESTRE_IDX


def registro(eid: str) -> dict | None:
    """O registro MESTRE (título, URL) vem de oportunidades.jsonl; a verificação (site oficial confirmado,
    anexos) vem do extraído, que é criado se não existir. Os dois juntos são o edital."""
    m = _mestre().get(eid)
    arq = EXTRAIDOS / f"{eid}.json"
    ex = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {}
    if not m and not ex:
        return None
    e = {**(m or {}), **ex, "id": eid}
    ve = ex.get("verificacao_externa") if isinstance(ex.get("verificacao_externa"), dict) else {}
    e["pagina_oficial"] = e.get("pagina_oficial") or ve.get("pagina_oficial") or (ex.get("validacao") or {}).get("site")
    e["titulo"] = e.get("titulo") or (m or {}).get("titulo")
    return e


def investigar(ids: list[str], ia, modelo: str, prazo_s: float = 280 * 60) -> dict:
    fim = time.time() + prazo_s
    saida = {"em": time.strftime("%Y-%m-%dT%H:%M:%S"), "modelo": modelo, "editais": []}
    for eid in ids:
        if time.time() > fim:
            saida["parou"] = "tempo esgotado"; break
        arq = EXTRAIDOS / f"{eid}.json"
        e = registro(eid)
        if e is None:
            saida["editais"].append({"id": eid, "erro": "registro não encontrado"}); continue
        t0 = time.time()
        texto, fontes = texto_do_edital(e)
        if not texto.strip():
            e["investigacao_ia"] = {"em": time.strftime("%Y-%m-%dT%H:%M:%S"), "modelo": modelo, "fontes": fontes, "campos": {}, "comprovados": 0, "total": len(DOZE), "erro": "nenhuma fonte legível"}
            arq.write_text(json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
            saida["editais"].append({"id": eid, "titulo": e.get("titulo"), "comprovados": 0, "erro": "nenhuma fonte legível", "fontes": fontes}); continue
        r = responder(ia, e, texto)
        if not isinstance(r, dict):
            saida["editais"].append({"id": eid, "titulo": e.get("titulo"), "comprovados": 0, "erro": "o modelo não devolveu JSON", "s": round(time.time() - t0)}); continue
        inv = aplicar(e, r, texto, fontes, modelo)
        e.setdefault("edital_id", eid)
        arq.write_text(json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
        saida["editais"].append({"id": eid, "titulo": e.get("titulo"), "comprovados": inv["comprovados"], "total": inv["total"],
                                 "nao_comprovados": [k for k, v in inv["campos"].items() if not v["comprovado"]],
                                 "s": round(time.time() - t0), "chars": len(texto), "fontes": len([f for f in fontes if f.get("ok")])})
        print(f"{eid} · {inv['comprovados']}/{inv['total']} · {round(time.time() - t0)} s · {e.get('titulo', '')[:60]}", flush=True)
    saida["resumo"] = {"investigados": len([x for x in saida["editais"] if "comprovados" in x]),
                       "media_comprovados": round(sum(x.get("comprovados", 0) for x in saida["editais"]) / max(1, len(saida["editais"])), 1),
                       "completos_12_de_12": sum(1 for x in saida["editais"] if x.get("comprovados") == len(DOZE))}
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    return saida


# ── INVESTIGAÇÃO ESPECIALIZADA POR EDITAL (titular, 26/09) ───────────────────────────────────
# Um botão por edital. Passos, sempre nesta ordem:
#   1. entender os DADOS INDICADOS (título, fonte, órgão, prazo, o que já foi verificado);
#   2. achar a PÁGINA OFICIAL: se conhecida, usa; senão lê a página de divulgação e escolhe, entre os links
#      que saem dela, o que leva ao site do órgão — e, se não houver, busca pelo site do órgão;
#   3. ler a FONTE OFICIAL (página e anexos que parecem o edital) e responder às doze perguntas;
#   4. para cada item NÃO encontrado, perguntar se o edital DISPENSA aquele item — com trecho literal — e, se
#      dispensar, registrar a justificativa: dispensa justificada conta como informação válida (verde).

PROMPT_PAGINA = """Você é o Investigador da Biblioteca de Alexandria. Este é um EDITAL conhecido pelo sistema:
título: {titulo}
fonte que o divulgou: {fonte}
órgão/financiador indicado: {orgao}
prazo indicado: {prazo}
página de divulgação lida: {url}

Abaixo estão os LINKS que saem dessa página de divulgação. Escolha o que leva à PÁGINA OFICIAL do edital — o site do
órgão ou financiador que o publica (não redes sociais, não a própria página de divulgação, não a página inicial genérica).
Se nenhum servir, devolva url null. Responda APENAS o JSON: {{"url": "...", "porque": "..."}}

LINKS:
{links}
"""

PROMPT_DISPENSA = """Você é o Investigador da Biblioteca de Alexandria. Sobre o edital "{titulo}", os itens abaixo NÃO foram
encontrados no texto da fonte oficial. Para cada um, diga se o edital DISPENSA o item — isto é, se o texto mostra que o
item não se aplica a este edital (exemplos: não há fase de recurso; apoio é em espécie, sem valor em dinheiro; inscrição
por formulário, sem anexos; resultado comunicado diretamente, sem data; edital aberto a todo o território nacional).
Só diga que dispensa se houver TRECHO LITERAL do texto que sustente; copie de 30 a 200 caracteres. Se não houver, "dispensa": false.
O fato de o texto NÃO MENCIONAR o item não é dispensa: dispensa é o edital dizer que o item não se aplica.
Responda APENAS o JSON, uma chave por item, exatamente com estes nomes: {itens}
Formato de cada item: {{"dispensa": true|false, "justificativa": "uma frase", "trecho": "trecho literal ou vazio"}}

TEXTO DA FONTE (pode estar truncado):
{texto}
"""

CHAVE_ITEM = {"Objeto": "objeto", "Prazo de inscrição": "prazo_inscricao", "Resultado": "resultado", "Prazo de recurso": "prazo_recurso",
              "Valor": "valor", "Órgão / financiador": "orgao", "Território": "territorio", "Esfera": "esfera", "Requisitos": "requisitos",
              "Anexos": "anexos", "Destinação": "destinacao", "Área de atuação": "area"}


def _links_da_pagina(url: str) -> list[tuple[str, str]]:
    try:
        dados, tipo = _baixar(url)
    except Exception:
        return []
    if "pdf" in tipo.lower():
        return []
    p = _Texto(); p.feed(dados.decode("utf-8", "ignore"))
    dom = (urlsplit(url).hostname or "").replace("www.", "")
    out, vistos = [], set()
    for h, rot in p.links:
        full = urljoin(url, h or "")
        hd = (urlsplit(full).hostname or "").replace("www.", "")
        if not full.startswith("http") or full in vistos or not hd or hd == dom:
            continue
        if re.search(r"facebook|instagram|twitter|x\.com|linkedin|youtube|whatsapp|t\.me|wa\.me|pinterest|tiktok|google\.|apple\.|mailto", full):
            continue
        vistos.add(full); out.append((full, (rot or "")[:90]))
    return out[:40]


def pagina_oficial(ia, e: dict) -> tuple[str | None, str]:
    """Conhecida → usa. Senão: links que saem da divulgação, escolhidos pelo modelo; senão, busca pelo órgão."""
    ve = e.get("verificacao_externa") if isinstance(e.get("verificacao_externa"), dict) else {}
    confirmada = ve.get("pagina_oficial") or (e.get("validacao") or {}).get("site")
    if confirmada:
        return confirmada, "página oficial confirmada pelo titular ou pela validação"
    if e.get("pagina_oficial"):
        # escolhida numa rodada anterior da IA: precisa conversar com o órgão ou o título — a rodada de 26/09
        # gravou um link de rodapé da ABCR e a seguinte o aceitou como 'já verificada'
        dom = _norm(urlsplit(e["pagina_oficial"]).hostname or "").replace(" ", "")
        chaves = [w for w in _norm(f"{e.get('orgao') or ''} {re.sub(r'(?i)^continue lendo ', '', e.get('titulo') or '')}").split() if len(w) >= 5]
        if any(w in dom for w in chaves):
            return e["pagina_oficial"], "página oficial de rodada anterior, conferida pelo domínio"
        e["pagina_oficial"] = None
    url = e.get("url") or ""
    links = _links_da_pagina(url) if url.startswith("http") else []
    if links:
        r = ia.perguntar(PROMPT_PAGINA.format(titulo=(e.get("titulo") or "")[:160], fonte=e.get("fonte_nome") or e.get("fonte_id") or "—",
                                              orgao=e.get("orgao") or "—", prazo=e.get("prazo_texto") or e.get("fim") or "—", url=url,
                                              links="\n".join(f"- {u}  ({r})" for u, r in links)), '{"url": "...", "porque": "..."}')
        u = (r or {}).get("url") if isinstance(r, dict) else None
        if u and str(u).startswith("http") and any(u == l for l, _ in links):
            # o domínio tem de conversar com o órgão ou o título — o 8B escolheu um link de rodapé da ABCR
            dom = _norm(urlsplit(u).hostname or "").replace(" ", "")
            chaves = [w for w in _norm(f"{e.get('orgao') or ''} {e.get('titulo') or ''}").split() if len(w) >= 5]
            if any(w in dom for w in chaves):
                return u, f"escolhida entre {len(links)} links da divulgação: {(r or {}).get('porque', '')[:120]}"
            passos_rejeitado = f"o modelo escolheu {u}, rejeitado: o domínio não tem relação com o órgão nem com o título"
    try:
        from .piloto_busca import buscar
        q = f"{(e.get('orgao') or '').strip()} {re.sub(r'(?i)^continue lendo ', '', (e.get('titulo') or ''))[:80]} edital".strip()
        for r in (buscar(q, maximo=6) or []):
            u = r.get("url") or ""
            if u.startswith("http") and not re.search(r"captadores|observatorio3setor|prosas|filantropia\.ong|gife|duckduckgo|bing\.", u):
                return u, f"achada pelo buscador com '{q[:60]}'"
    except Exception:
        pass
    return None, "não encontrada: sem link para o site do órgão na divulgação e o buscador não devolveu o site"


def dispensas(ia, e: dict, texto: str, faltantes: list[str]) -> dict:
    if not faltantes:
        return {}
    r = ia.perguntar(PROMPT_DISPENSA.format(titulo=(e.get("titulo") or "")[:160], itens=json.dumps([CHAVE_ITEM[i] for i in faltantes], ensure_ascii=False),
                                            texto=_recortar(texto, 30_000)), "{item: {dispensa, justificativa, trecho}}")
    tn = _norm(texto); out = {}
    for item in faltantes:
        b = (r or {}).get(CHAVE_ITEM[item]) if isinstance(r, dict) else None
        just = _norm(b.get("justificativa") if isinstance(b, dict) else "")
        # AUSÊNCIA NÃO É DISPENSA: "o edital não menciona recurso" é falta de informação, não regra do edital
        if re.search(r"nao (menciona|informa|consta|cita|especifica|apresenta|traz|indica)|nao ha (informacao|mencao|dados)|sem informacao", just):
            continue
        if isinstance(b, dict) and str(b.get("dispensa")).lower() in ("true", "1", "sim") and comprovado(b.get("trecho") or "", tn):
            out[item] = {"justificativa": str(b.get("justificativa") or "")[:200], "trecho": str(b.get("trecho") or "")[:200]}
    return out


def investigar_um(eid: str, ia, modelo: str) -> dict:
    t0 = time.time()
    e = registro(eid)
    if e is None:
        return {"id": eid, "erro": "registro não encontrado"}
    passos = [f"dados indicados: título «{(e.get('titulo') or '')[:80]}», fonte {e.get('fonte_nome') or e.get('fonte_id') or '—'}, "
              f"órgão {e.get('orgao') or '—'}, prazo {e.get('prazo_texto') or e.get('fim') or '—'}"]
    oficial, como = pagina_oficial(ia, e)
    passos.append(f"página oficial: {oficial or 'não encontrada'} — {como}")
    if oficial:
        e["pagina_oficial"] = oficial
    texto, fontes = texto_do_edital(e)
    if not texto.strip():
        e["investigacao_ia"] = {"em": time.strftime("%Y-%m-%dT%H:%M:%S"), "modelo": modelo, "passos": passos, "fontes": fontes,
                                "campos": {}, "comprovados": 0, "dispensados": 0, "total": len(DOZE), "erro": "nenhuma fonte legível"}
        (EXTRAIDOS / f"{eid}.json").write_text(json.dumps({**e, "edital_id": eid}, ensure_ascii=False, indent=1), encoding="utf-8")
        return {"id": eid, "titulo": e.get("titulo"), "comprovados": 0, "erro": "nenhuma fonte legível", "passos": passos, "s": round(time.time() - t0)}
    r = responder(ia, e, texto)
    if not isinstance(r, dict):
        return {"id": eid, "titulo": e.get("titulo"), "comprovados": 0, "erro": "o modelo não devolveu JSON", "passos": passos, "s": round(time.time() - t0)}
    inv = aplicar(e, r, texto, fontes, modelo)
    faltantes = [k for k, v in inv["campos"].items() if not v["comprovado"]]
    disp = dispensas(ia, e, texto, faltantes)
    for item, d in disp.items():
        inv["campos"][item].update({"dispensado": True, "justificativa": d["justificativa"], "trecho_dispensa": d["trecho"],
                                    "valor": f"dispensado — {d['justificativa']}"})
    inv["dispensados"] = len(disp)
    inv["comprovados"] = sum(1 for v in inv["campos"].values() if v["comprovado"] or v.get("dispensado"))
    inv["passos"] = passos + [f"doze perguntas respondidas: {sum(1 for v in inv['campos'].values() if v['comprovado'])} comprovadas na fonte",
                              f"dispensas justificadas: {len(disp)} ({', '.join(disp) or 'nenhuma'})",
                              f"sem informação nem dispensa: {', '.join(k for k, v in inv['campos'].items() if not (v['comprovado'] or v.get('dispensado'))) or 'nenhum'}"]
    inv["s"] = round(time.time() - t0)
    e["confirmacao"] = f"investigado pela IA ({modelo}) em {time.strftime('%d/%m/%Y')}: {inv['comprovados']}/{len(DOZE)} itens (comprovados ou dispensados)"
    (EXTRAIDOS / f"{eid}.json").write_text(json.dumps({**e, "edital_id": eid}, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"id": eid, "titulo": e.get("titulo"), "comprovados": inv["comprovados"], "dispensados": len(disp), "total": len(DOZE),
            "nao_resolvidos": [k for k, v in inv["campos"].items() if not (v["comprovado"] or v.get("dispensado"))],
            "s": inv["s"], "chars": len(texto), "fontes": len([f for f in fontes if f.get("ok")]), "pagina_oficial": oficial, "passos": passos}


def investigar_especializado(ids: list[str], ia, modelo: str, prazo_s: float = 300 * 60) -> dict:
    fim = time.time() + prazo_s
    saida = {"em": time.strftime("%Y-%m-%dT%H:%M:%S"), "modelo": modelo, "modo": "especializado (um edital por vez)", "editais": []}
    for eid in ids:
        if time.time() > fim:
            saida["parou"] = "tempo esgotado"; break
        x = investigar_um(eid, ia, modelo); saida["editais"].append(x)
        print(f"{eid} · {x.get('comprovados', '-')}/12 ({x.get('dispensados', 0)} dispensa) · {x.get('s', '-')} s · {str(x.get('titulo', ''))[:60]} · {x.get('erro') or ''}", flush=True)
    saida["resumo"] = {"investigados": len([x for x in saida["editais"] if "comprovados" in x]),
                       "media_itens_resolvidos": round(sum(x.get("comprovados", 0) for x in saida["editais"]) / max(1, len(saida["editais"])), 1),
                       "completos_12_de_12": sum(1 for x in saida["editais"] if x.get("comprovados") == len(DOZE))}
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    (SAIDA.parent / f"investigacoes_ia_{modelo}.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    SAIDA.write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    return saida
