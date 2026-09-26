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
        if "pdf" in tipo.lower() or u.lower().endswith(".pdf"):
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
    s = unicodedata.normalize("NFD", str(s or "").lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def comprovado(trecho: str, texto_norm: str, curto_ok: bool = False) -> bool:
    t = _norm(trecho)
    if len(t) < 12:
        return bool(curto_ok and len(t) >= 4 and re.search(r"(^| )" + re.escape(t) + r"( |$)", texto_norm))
    if t in texto_norm:
        return True
    # tolerância a quebra de linha e pontuação: metade inicial e final do trecho, ambas presentes
    meio = len(t) // 2
    return t[:meio].strip() in texto_norm and t[meio:].strip() in texto_norm and len(t) >= 30


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
    b = g("area"); v = str(b.get("valor") or "").lower(); c = ok(b, True) and v in ("cultura", "educacao", "saude", "assistencia_social", "esporte", "meio_ambiente", "direitos")
    campos["Área de atuação"] = {"valor": v or None, "trecho": b.get("trecho"), "comprovado": c}
    if c: e["area"] = v
    n = sum(1 for v in campos.values() if v["comprovado"])
    e["investigacao_ia"] = {"em": time.strftime("%Y-%m-%dT%H:%M:%S"), "modelo": modelo, "fontes": fontes, "campos": campos,
                            "comprovados": n, "total": len(DOZE),
                            "regra": "só entra na ficha o que tem trecho literal encontrado na fonte"}
    e["confirmacao"] = f"investigado pela IA ({modelo}) em {time.strftime('%d/%m/%Y')}: {n}/{len(DOZE)} itens comprovados"
    return e["investigacao_ia"]


MESTRE = ROOT / "dados/oportunidades/oportunidades.jsonl"


def registro(eid: str) -> dict | None:
    """O registro MESTRE (título, URL) vem de oportunidades.jsonl; a verificação (site oficial confirmado,
    anexos) vem do extraído, que é criado se não existir. Os dois juntos são o edital."""
    m = None
    if MESTRE.exists():
        for l in MESTRE.open(encoding="utf-8"):
            if eid in l:
                try:
                    d = json.loads(l)
                    if d.get("id") == eid:
                        m = d; break
                except ValueError:
                    pass
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
