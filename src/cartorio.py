"""CARTÓRIO DE FONTES OFICIAIS (titular, 09/10/2026).

Os motores DESCOBREM; o Cartório CERTIFICA. Toda estrela (oportunidade aberta) e todo livro (histórico) que tenha
QUALQUER um dos 12 itens indisponível entra na fila do Cartório. Para cada um, ele sobe uma escada de degraus — do mais
barato e confiável ao mais caro — até achar o documento OFICIAL, lê o documento por seções e emite uma CERTIDÃO:
link oficial (régua única: vetor nunca é fonte), degrau em que foi achado, impressão digital do documento, e cada item
com valor + trecho literal + página — ou a DISPENSA com a justificativa de que o requisito não existe naquele edital.

Balcões (como chegar ao documento em cada tipo de fonte):
  pncp      página do PNCP → API de arquivos do órgão (PDF ou ZIP), o edital primeiro
  diario    DOU, Diário de Goiás/Goiânia, Querido Diário → o ato dentro da edição (só as páginas do ato)
  orgao     domínio público → documentos da página + biblioteca de mídia do WordPress pelo número do edital
  privado   site do financiador → documentos da página (regulamento, edital)
  pista     agregador/notícia → links de SAÍDA para o financiador; o resto vai ao Interceptador
  proprio   Ministério Público e Judiciário: já leem o PDF; o Cartório só converte em certidão

Escada: 0 documento na mão · 1 link de saída da pista · 2 busca do número do edital dentro do domínio oficial ·
        3 Interceptador (IA) · 4 Chrome. O Cartório resolve 0–2 sem IA; 3 e 4 recebem só o que sobrou.
Integração: a fila é ordenada pela urgência (prazo), pela nota da REDE NEURAL e pela distância até o ouro (menos
itens faltando primeiro: cada certidão vira selo). Estrelas: o fluxo de oportunidades lê a certidão no checklist.
Livros: linhas no formato do importador (scripts/importar_verificacao_livros.py), que confere e entrega à esteira.
Execução: `python -m src.cartorio [--limite N] [--segundos S]`.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote, urlsplit

from . import cartorio_leitura as L

ROOT = Path(__file__).resolve().parents[1]
PASTA = ROOT / "estado/cartorio"
CERTIDOES = PASTA / "certidoes.json"
LIVROS_OUT = PASTA / "resultados_livros.jsonl"
INTERCEPTADOR = PASTA / "para_o_interceptador.json"
RELATORIO = ROOT / "docs/dados/cartorio.json"
CFG = ROOT / "config/cartorio.json"
FLUXO = ROOT / "docs/dados/fluxo_oportunidades.json"
CATALOGO = ROOT / "biblioteca_alexandria/fontes/motores.json"
VERSAO = "cartório v2 (09/10/2026)"
FALTA = ("falta", "pend", "ref", None)


def cfg() -> dict:
    padrao = {"oportunidades_por_execucao": 40, "segundos_por_execucao": 1500, "documentos_por_oportunidade": 4,
              "revisitar_dias": 7, "livros_por_execucao": 25, "pausa_segundos": 1.0}
    try:
        return {**padrao, **json.loads(CFG.read_text(encoding="utf-8"))}
    except Exception:  # noqa: BLE001
        return padrao


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao


def _agora() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


# ── REDE (injetável nos testes) ────────────────────────────────────────────────────────────────────────────────────
def _baixar(url: str) -> tuple[bytes, str]:
    """Direto; se o site oficial recusar a nuvem (DOU: RemoteDisconnected; 403), tenta pela ponte do computador do titular."""
    from .executor_skills import baixar
    try:
        return baixar(url)
    except Exception as e1:  # noqa: BLE001
        try:
            from . import ponte_brasil as PB
            if PB.na_nuvem() and PB.configurada() and not PB.precisa(url):     # precisa(): o executor já tentou a ponte
                st, _f, corpo, hdr = PB.abrir(url, timeout=60)
                if st == 200 and corpo:
                    return corpo, (hdr or {}).get("content-type", "")
        except Exception:  # noqa: BLE001
            pass
        raise e1


def _permitido(url: str) -> bool:
    try:
        from .executor_skills import permitido
        return permitido(url)
    except Exception:  # noqa: BLE001
        return True


class Rede:
    def __init__(self, baixar=None, permitido=None, pausa: float = 1.0):
        self.baixar = baixar or _baixar; self.permitido = permitido or _permitido; self.pausa = pausa; self.n = 0

    def get(self, url: str) -> tuple[bytes | None, str, str | None]:
        """(bytes, tipo, motivo_da_falha)."""
        try:
            if not self.permitido(url):
                return None, "", "robots_proibe"
        except Exception:  # noqa: BLE001
            pass
        try:
            self.n += 1
            b, t = self.baixar(url)
            if self.pausa:
                time.sleep(self.pausa)
            return b, t or "", None
        except Exception as e:  # noqa: BLE001
            return None, "", f"erro_rede: {type(e).__name__}"


# ── BALCÕES ────────────────────────────────────────────────────────────────────────────────────────────────────────
PNCP_APP = re.compile(r"pncp\.gov\.br/app/editais/(\d{14})/(\d{4})/(\d+)", re.I)
DIARIO = re.compile(r"queridodiario|in\.gov\.br|diariooficial|/diario|doe\.|dom\.|diariomunicipal|/Download/legislacao/diariooficial", re.I)
PROPRIOS = ("mpgo-destinacao", "mptgo-destinacao", "mpu-destinacao", "plat-mp-destinacoes-reparacao", "judiciario-tjgo", "judiciario-cnj", "judiciario-cnj-tjgo")


def balcao(op: dict) -> str:
    try:
        return _balcao(op)
    except ValueError:                                   # endereço malformado na pista
        return "pista"


def _balcao(op: dict) -> str:
    us = " ".join(str(op.get(k) or "") for k in ("url", "link_oficial", "url_documento"))
    if str(op.get("origem") or "").split("motor ")[-1].split(" ")[0] in PROPRIOS:
        return "proprio"
    if "pncp.gov.br" in us:
        return "pncp"
    if DIARIO.search(us) or str(op.get("tipo") or "").startswith("menção em diário"):
        return "diario"
    link = op.get("link_oficial") or op.get("url")
    ok, _ = L.regua(link)
    if ok:
        return "orgao" if L.GOV.search(urlsplit(str(link)).hostname or "") else "privado"
    return "pista"


def documentos(op: dict, rede: Rede, maximo: int = 4) -> list[dict]:
    """Escada de degraus: devolve documentos candidatos [{url, degrau, como, bytes, tipo}] — o oficial primeiro."""
    b = balcao(op); out, vistos = [], set()

    def add(url, degrau, como):
        if url and url not in vistos and len(out) < maximo:
            vistos.add(url); out.append({"url": url, "degrau": degrau, "como": como})

    for k in ("url_documento", "url_edital"):
        if op.get(k):
            add(op[k], 0, "documento entregue pelo motor")
    if b == "pncp":
        m = PNCP_APP.search(" ".join(str(op.get(k) or "") for k in ("url", "link_oficial")))
        if m:
            api = f"https://pncp.gov.br/pncp-api/v1/orgaos/{m.group(1)}/compras/{m.group(2)}/{m.group(3)}/arquivos"
            raw, _t, _e = rede.get(api)
            try:
                arqs = json.loads(raw or b"[]")
            except ValueError:
                arqs = []
            arqs = [a for a in arqs if isinstance(a, dict) and a.get("statusAtivo", True) and (a.get("url") or a.get("uri"))]
            arqs.sort(key=lambda a: 0 if re.search(r"(?i)edital", f"{a.get('titulo')} {a.get('tipoDocumentoNome')}") else 1)
            for a in arqs[:maximo]:
                u = re.sub(r"^https://pncp\.gov\.br:\d+/", "https://pncp.gov.br/", a.get("url") or a.get("uri"))
                add(u, 0, f"PNCP: arquivo anexado pelo órgão ({a.get('tipoDocumentoNome') or a.get('titulo') or 'documento'})")
    for k in ("link_oficial", "url", "pagina_oficial", "site_oficial"):
        u = op.get(k)
        if u and (L.regua(u)[0] or b == "diario"):
            add(u, 0, "página/documento oficial já conhecido")
    if b == "pista" and not out:                         # a pista (vetor) é aberta só para achar o link de SAÍDA ao financiador
        for k in ("url", "link_oficial"):
            if op.get(k):
                add(op[k], 0, "pista (vetor): lida só para achar o link do financiador"); break
    return out


def _wordpress(base: str, numero: str, rede: Rede) -> list[str]:
    """Degrau 2: biblioteca de mídia do WordPress do órgão, pelo número do edital — devolve o PDF direto."""
    raw, _t, err = rede.get(f"{base}/wp-json/wp/v2/media?search={quote(numero)}&per_page=10")
    if err or not raw:
        return []
    try:
        itens = json.loads(raw)
    except ValueError:
        return []
    return [i.get("source_url") for i in itens if isinstance(i, dict) and str(i.get("mime_type") or "").endswith("pdf") and i.get("source_url")][:3]


# ── CERTIDÃO ───────────────────────────────────────────────────────────────────────────────────────────────────────
def certificar(op: dict, faltam: list[str], rede: Rede, maximo_docs: int = 4) -> dict:
    """Uma oportunidade: escada de degraus → leitura → extração → certidão (só os itens que FALTAVAM contam)."""
    cert = {"id": op.get("id"), "tipo": op.get("_tipo", "estrela"), "titulo": str(op.get("titulo") or "")[:200], "balcao": balcao(op),
            "faltavam": list(faltam), "em": _agora(), "versao": VERSAO, "link_oficial": None, "degrau": None, "como": None,
            "documentos": [], "itens": {}, "dispensas": {}, "fim": None, "encaminhado": None}
    if cert["balcao"] == "proprio":
        cert.update({"encaminhado": "motor próprio já lê o documento (Ministério Público / Judiciário)",
                     "resolvidos": [], "ainda_faltam": list(faltam), "eficiencia": 0.0})
        return cert
    fila = documentos(op, rede, maximo_docs)
    titulo = str(op.get("titulo") or "")
    lidos = 0
    i = 0
    while i < len(fila) and lidos < maximo_docs:
        d = fila[i]; i += 1
        raw, tipo, err = rede.get(d["url"])
        reg = {"url": d["url"], "degrau": d["degrau"], "como": d["como"]}
        if err:
            reg["falha"] = err; cert["documentos"].append(reg); continue
        lido = L.paginas(raw, tipo)
        reg.update({"motivo": lido.get("motivo"), "tipo": lido.get("tipo"), "paginas": len(lido.get("paginas") or []),
                    "sha1": hashlib.sha1(raw).hexdigest()[:16]})
        # degrau 1 e 2: a página não é o documento — segue os links do próprio site oficial / da pista
        if lido.get("tipo") == "html":
            html = lido.get("html") or ""
            if L.regua(d["url"])[0]:
                for u, rot in L.links_de_documento(html, d["url"]):
                    if len(fila) < maximo_docs + 4 and u not in {x["url"] for x in fila}:
                        fila.append({"url": u, "degrau": max(1, d["degrau"]), "como": f"documento citado na página oficial: {rot or u}"})
                num = re.search(r"\b(\d{1,4}\s*/\s*20\d{2})\b", titulo)
                if num and L.GOV.search(urlsplit(d["url"]).hostname or "") and re.search(r"(?i)wp-content|wordpress|wp-json", html):
                    base = "{0.scheme}://{0.netloc}".format(urlsplit(d["url"]))
                    for u in _wordpress(base, num.group(1).replace(" ", ""), rede):
                        if u not in {x["url"] for x in fila}:
                            fila.append({"url": u, "degrau": 2, "como": f"biblioteca de mídia do site oficial (edital {num.group(1)})"})
            else:
                for u in L.links_de_saida(html, d["url"]):
                    if L.regua(u)[0] and u not in {x["url"] for x in fila}:
                        fila.append({"url": u, "degrau": 1, "como": "link de saída da pista para o site do financiador"})
        pgs = lido.get("paginas") or []
        if lido.get("ok") and pgs:
            if len(pgs) > 30:                                    # edição inteira de diário: só o ato
                sel = L.localizar_ato(pgs, titulo, str(op.get("orgao") or ""))
                if sel is None:
                    reg["motivo"] = "ato_nao_localizado"; cert["documentos"].append(reg); continue
                pgs = sel; reg["edicao_inteira"] = True
            from .nucleo import has_prompt_injection
            if has_prompt_injection(" ".join(pgs)[:250_000]):
                reg["motivo"] = "quarentena"; cert["documentos"].append(reg); continue
            lidos += 1
            ex = L.extrair(pgs, d["url"], titulo, str(op.get("orgao") or ""))
            oficial, porque = L.regua(d["url"])
            reg["oficial"] = porque
            for k, v in ex["pontos"].items():
                if k in faltam and k not in cert["itens"]:
                    cert["itens"][k] = v
            for k, v in ex["dispensas"].items():
                if k in faltam and k not in cert["itens"] and k not in cert["dispensas"]:
                    cert["dispensas"][k] = v
            cert["fim"] = cert["fim"] or ex.get("fim")
            if oficial and not cert["link_oficial"]:
                cert.update({"link_oficial": d["url"], "degrau": d["degrau"], "como": d["como"], "regua": porque})
        cert["documentos"].append(reg)
        if all(k in cert["itens"] or k in cert["dispensas"] for k in faltam) and cert["link_oficial"]:
            break
    resolvidos = [k for k in faltam if k in cert["itens"] or k in cert["dispensas"]]
    cert["resolvidos"] = resolvidos
    cert["ainda_faltam"] = [k for k in faltam if k not in resolvidos]
    cert["eficiencia"] = round(len(resolvidos) / len(faltam), 3) if faltam else 1.0
    if not cert["link_oficial"] or cert["ainda_faltam"]:
        motivos = sorted({str(x.get("falha") or x.get("motivo")) for x in cert["documentos"] if x.get("falha") or x.get("motivo")})
        cert["encaminhado"] = ("Interceptador: site oficial não localizado nos degraus 0–2" if not cert["link_oficial"] else
                               f"Interceptador: {len(cert['ainda_faltam'])} item(ns) não estão no documento oficial lido") + \
                              (f" ({', '.join(motivos)[:160]})" if motivos else "")
        if any("robots_proibe" in m for m in motivos):
            cert["encaminhado"] = "Chrome (último recurso): o robots.txt do site oficial proíbe a leitura automática"
    return cert


# ── FILAS: quem tem informação indisponível ────────────────────────────────────────────────────────────────────────
def _nota_rede(op: dict) -> float:
    try:
        from .rede_neural import nota
        n = nota(op)
        return float(n) if n is not None else 0.5
    except Exception:  # noqa: BLE001
        return float(op.get("nota_rede") or 0.5)


def fila_estrelas(fluxo: dict | None = None) -> list[dict]:
    d = fluxo if fluxo is not None else _j(FLUXO, {})
    out = []
    for lista in (d.get("itens_por_uf") or {}).values():
        for x in lista:
            ck = x.get("checklist") or {}
            faltam = [k for k in L.DOZE if (ck.get(k) or {}).get("s") in FALTA]
            if faltam and x.get("id") and x.get("tipo") != "emenda":
                out.append({**x, "_tipo": "estrela", "_faltam": faltam})
    return out


def fila_livros(catalogo: dict | None = None) -> list[dict]:
    C = catalogo if catalogo is not None else _j(CATALOGO, {})
    out = []
    for x in C.get("motores") or []:
        e = x.get("esteira") or {}
        if e.get("selo") == "ouro":
            continue
        faltam = [k for k in (e.get("doze_faltando") or []) if k in L.DOZE]
        sem_site = not e.get("site_confirmado_por")
        if not faltam and not sem_site:
            continue
        p = x.get("parametros") or {}
        out.append({"id": x.get("id"), "_tipo": "livro", "_faltam": faltam, "_sem_site": sem_site, "titulo": x.get("programa") or x.get("nome_classificado"),
                    "orgao": x.get("orgao"), "uf": x.get("uf"), "nota_rede": x.get("nota_rede"), "selo": e.get("selo"),
                    "url_edital": (p.get("edital") or {}).get("url") or e.get("url_edital"),
                    "link_oficial": p.get("fonte_oficial") or e.get("site_oficial"), "url": x.get("pagina")})
    return out


def prioridade(op: dict, hoje: str) -> tuple:
    """Urgência do prazo (abertas que fecham antes primeiro) · nota da rede neural · menos itens até o ouro."""
    fim = str(op.get("fim") or "")[:10]
    aberta = 0 if (fim and fim >= hoje) else 1
    return (aberta, fim or "9999", -_nota_rede(op), len(op.get("_faltam") or []))


def _assinatura(op: dict) -> str:
    return hashlib.sha1(json.dumps([op.get(k) for k in ("url", "link_oficial", "url_edital", "url_documento", "_faltam")], default=str).encode()).hexdigest()[:12]


def devidos(fila: list[dict], certidoes: dict, revisitar_dias: int) -> list[dict]:
    """Ativação: entra quem tem item indisponível E (nunca foi certificado, OU a informação mudou, OU já passou o prazo de revisita)."""
    limite = (datetime.now(timezone.utc) - timedelta(days=revisitar_dias)).isoformat()
    out = []
    for op in fila:
        c = certidoes.get(f"{op['_tipo']}:{op['id']}")
        leitor_novo = c and c.get("versao") != VERSAO and (c.get("ainda_faltam") or not c.get("link_oficial"))
        if not c or c.get("assinatura") != _assinatura(op) or str(c.get("em") or "") < limite or leitor_novo:
            out.append(op)
    return out


# ── LIVROS: formato do importador (confere e entrega à esteira) ────────────────────────────────────────────────────
def linhas_livro(op: dict, c: dict) -> list[dict]:
    out = []
    if op.get("_sem_site") and c.get("link_oficial"):
        out.append({"livro": op["id"], "etapa": "bronze", "site_oficial": c["link_oficial"], "url_edital": c["link_oficial"],
                    "confirmado_localmente": True, "modelo": VERSAO, "fontes": [c["link_oficial"]],
                    "motivo": f"Cartório: {c.get('como')} ({c.get('regua')})"})
    if c.get("itens") or c.get("dispensas"):
        doze = {k: f'{v["valor"]} — “{v["trecho"][:180]}” ({v["documento"]}, p. {v["pagina"]})' for k, v in c["itens"].items()}
        disp = {k: f'{v["motivo"]} — “{v["trecho"][:160]}” (p. {v["pagina"]})' for k, v in c["dispensas"].items()}
        r = {"livro": op["id"], "etapa": "prata", "doze": doze, "dispensas": disp, "modelo": VERSAO,
             "url_edital": c.get("link_oficial") if str(c.get("link_oficial") or "").startswith("https://") else None,
             "edital_validado": bool(c.get("link_oficial")), "fontes": [d["url"] for d in c["documentos"] if d.get("oficial")][:5],
             "motivo": f"Cartório: {len(c['resolvidos'])} de {len(c['faltavam'])} itens que faltavam (degrau {c.get('degrau')})"}
        if c.get("fim"):
            r["prazo_inscricao_fim"] = c["fim"]
        out.append({k: v for k, v in r.items() if v not in (None, {}, [])})
    return out


# ── CHECKLIST DAS ESTRELAS (lido pelo fluxo de oportunidades) ──────────────────────────────────────────────────────
_CACHE: dict = {}


def certidao(eid: str) -> dict | None:
    if "c" not in _CACHE:
        _CACHE["c"] = (_j(CERTIDOES, {}) or {}).get("certidoes") or {}
    return _CACHE["c"].get(f"estrela:{eid}")


def item_checklist(eid: str, item: str) -> dict | None:
    """Para o fluxo: o item certificado (ok, com trecho e página) ou a dispensa justificada (disp)."""
    c = certidao(eid)
    if not c:
        return None
    v = (c.get("itens") or {}).get(item)
    if v:
        return {"s": "ok", "v": str(v["valor"])[:90], "t": f'{v["trecho"][:130]} (Cartório · p. {v["pagina"]})', "de": "Cartório", "doc": v.get("documento")}
    d = (c.get("dispensas") or {}).get(item)
    if d:
        return {"s": "disp", "v": d["motivo"][:160], "t": f'{d["trecho"][:120]} (Cartório · p. {d["pagina"]})', "de": "Cartório"}
    return None


def link_oficial(eid: str) -> str | None:
    c = certidao(eid)
    return (c or {}).get("link_oficial")


# ── EXECUÇÃO ───────────────────────────────────────────────────────────────────────────────────────────────────────
def run(limite: int | None = None, segundos: int | None = None, rede: Rede | None = None,
        fluxo: dict | None = None, catalogo: dict | None = None, gravar: bool = True) -> dict:
    c = cfg(); hoje = date.today().isoformat(); t0 = time.time()
    limite = limite or int(c["oportunidades_por_execucao"]); segundos = segundos or int(c["segundos_por_execucao"])
    rede = rede or Rede(pausa=float(c["pausa_segundos"]))
    base = _j(CERTIDOES, {}) or {}
    certs = base.get("certidoes") or {}
    estrelas = devidos(fila_estrelas(fluxo), certs, int(c["revisitar_dias"]))
    livros = devidos(fila_livros(catalogo), certs, int(c["revisitar_dias"]))
    estrelas.sort(key=lambda o: prioridade(o, hoje)); livros.sort(key=lambda o: prioridade(o, hoje))
    lote = estrelas[:max(1, limite - min(len(livros), int(c["livros_por_execucao"])))] + livros[:int(c["livros_por_execucao"])]
    lote = lote[:limite]
    feitas, novas_linhas, erros = [], [], []
    for op in lote:
        if time.time() - t0 > segundos:
            break
        faltam = op["_faltam"] or (["Objeto"] if op.get("_sem_site") else [])
        try:
            cert = certificar(op, faltam, rede, int(c["documentos_por_oportunidade"]))
        except Exception as ex:  # noqa: BLE001 — uma oportunidade com erro nunca derruba a fila inteira
            import traceback
            cert = {"id": op.get("id"), "tipo": op.get("_tipo"), "titulo": str(op.get("titulo") or "")[:200], "balcao": "?",
                    "faltavam": faltam, "resolvidos": [], "ainda_faltam": faltam, "eficiencia": 0.0, "documentos": [], "itens": {},
                    "dispensas": {}, "em": _agora(), "versao": VERSAO, "link_oficial": None,
                    "encaminhado": f"Interceptador: erro no Cartório ({type(ex).__name__})", "erro": traceback.format_exc()[-800:]}
            erros.append({"id": op.get("id"), "erro": f"{type(ex).__name__}: {str(ex)[:200]}"})
        cert["assinatura"] = _assinatura(op)
        cert["selo_antes"] = op.get("selo")
        cert["prazo"] = op.get("fim"); cert["uf"] = op.get("uf"); cert["orgao"] = op.get("orgao")
        cert["origem"] = op.get("origem")
        if op["_tipo"] == "estrela":
            from .criterio_selos import nivel
            ck = {k: v for k, v in (op.get("checklist") or {}).items()}
            for k in cert.get("resolvidos") or []:
                ck[k] = item_checklist_de(cert, k)
            cert["selo_depois"] = nivel(ck)
            cert["selo_antes"] = nivel(op.get("checklist") or {})
        else:
            novas_linhas += linhas_livro(op, cert)
        certs[f"{op['_tipo']}:{op['id']}"] = cert
        feitas.append(cert)
    para_int = [{"id": x["id"], "tipo": x["tipo"], "titulo": x["titulo"], "motivo": x["encaminhado"], "faltam": x.get("ainda_faltam")}
                for x in certs.values() if x.get("encaminhado", "") and str(x.get("encaminhado")).startswith("Interceptador")]
    rel = relatorio(certs, feitas, len(estrelas), len(livros))
    if gravar:
        PASTA.mkdir(parents=True, exist_ok=True)
        CERTIDOES.write_text(json.dumps({"em": _agora(), "versao": VERSAO, "certidoes": certs}, ensure_ascii=False, indent=1), encoding="utf-8")
        INTERCEPTADOR.write_text(json.dumps({"em": _agora(), "regra": "só o que o Cartório não resolveu nos degraus 0–2", "itens": para_int[:300]},
                                            ensure_ascii=False, indent=1), encoding="utf-8")
        if novas_linhas:
            (PASTA / "novos_livros.jsonl").write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in novas_linhas) + "\n", encoding="utf-8")
            with LIVROS_OUT.open("a", encoding="utf-8") as fh:
                for x in novas_linhas:
                    fh.write(json.dumps(x, ensure_ascii=False) + "\n")
        RELATORIO.parent.mkdir(parents=True, exist_ok=True)
        RELATORIO.write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")
        _CACHE.clear()
    return {"certificadas": len(feitas), "fila_estrelas": len(estrelas), "fila_livros": len(livros), "linhas_livros": len(novas_linhas),
            "acessos": rede.n, "segundos": round(time.time() - t0), "eficiencia": rel["resumo"]["eficiencia_itens"], "erros": erros[:20]}


def item_checklist_de(cert: dict, item: str) -> dict:
    v = (cert.get("itens") or {}).get(item)
    if v:
        return {"s": "ok", "v": str(v["valor"])[:90]}
    d = (cert.get("dispensas") or {}).get(item) or {}
    return {"s": "disp", "v": d.get("motivo", "")[:160]}


def relatorio(certs: dict, feitas: list[dict], fila_e: int, fila_l: int) -> dict:
    """Taxas de eficiência (por item, por balcão, por degrau) e a lista clicável de certidões."""
    from collections import Counter
    todas = list(certs.values())
    pedido, obtido, dispensado = Counter(), Counter(), Counter()
    por_balcao, por_degrau, selos = {}, Counter(), Counter()
    for c in todas:
        for k in c.get("faltavam") or []:
            pedido[k] += 1
        for k in c.get("itens") or {}:
            obtido[k] += 1
        for k in c.get("dispensas") or {}:
            dispensado[k] += 1
        b = por_balcao.setdefault(c.get("balcao") or "?", {"certidoes": 0, "com_link_oficial": 0, "faltavam": 0, "resolvidos": 0})
        b["certidoes"] += 1; b["com_link_oficial"] += bool(c.get("link_oficial"))
        b["faltavam"] += len(c.get("faltavam") or []); b["resolvidos"] += len(c.get("resolvidos") or [])
        if c.get("degrau") is not None:
            por_degrau[f"degrau {c['degrau']}"] += 1
        if c.get("tipo") == "estrela" and (c.get("selo_depois") != c.get("selo_antes")):
            selos[f"{c.get('selo_antes') or 'sem selo'} → {c.get('selo_depois') or 'sem selo'}"] += 1
    for b in por_balcao.values():
        b["eficiencia"] = round(b["resolvidos"] / b["faltavam"], 3) if b["faltavam"] else None
        b["taxa_link_oficial"] = round(b["com_link_oficial"] / b["certidoes"], 3) if b["certidoes"] else None
    tf, tr = sum(pedido.values()), sum(obtido.values()) + sum(dispensado.values())
    itens = {k: {"faltavam": pedido[k], "obtidos": obtido[k], "dispensados": dispensado[k],
                 "eficiencia": round((obtido[k] + dispensado[k]) / pedido[k], 3) if pedido[k] else None} for k in L.DOZE}
    lista = sorted(todas, key=lambda c: (-(c.get("eficiencia") or 0), c.get("titulo") or ""))
    enxuta = [{k: c.get(k) for k in ("id", "tipo", "titulo", "balcao", "link_oficial", "degrau", "como", "faltavam", "resolvidos", "ainda_faltam",
                                      "eficiencia", "encaminhado", "selo_antes", "selo_depois", "em", "prazo", "uf", "orgao", "fim")} |
              {"itens": {k: {kk: v.get(kk) for kk in ("valor", "trecho", "pagina", "documento", "metodo")} for k, v in (c.get("itens") or {}).items()},
               "dispensas": {k: {kk: v.get(kk) for kk in ("motivo", "trecho", "pagina", "documento")} for k, v in (c.get("dispensas") or {}).items()},
               "documentos": [{kk: d.get(kk) for kk in ("url", "degrau", "como", "motivo", "falha", "oficial", "paginas", "edicao_inteira")} for d in c.get("documentos") or []]}
              for c in lista[:400]]
    return {"em": _agora(), "versao": VERSAO, "regra": __doc__.split("Execução:")[0].strip(),
            "identidade_visual": "provisória (config/identidade_visual.json aguarda o design de referência)",
            "resumo": {"certidoes": len(todas), "nesta_execucao": len(feitas), "fila_estrelas": fila_e, "fila_livros": fila_l,
                       "itens_que_faltavam": tf, "itens_obtidos": sum(obtido.values()), "itens_dispensados": sum(dispensado.values()),
                       "eficiencia_itens": round(tr / tf, 3) if tf else None,
                       "com_link_oficial": sum(1 for c in todas if c.get("link_oficial")),
                       "taxa_link_oficial": round(sum(1 for c in todas if c.get("link_oficial")) / len(todas), 3) if todas else None,
                       "certidoes_completas": sum(1 for c in todas if not c.get("ainda_faltam") and c.get("link_oficial")),
                       "para_o_interceptador": sum(1 for c in todas if str(c.get("encaminhado") or "").startswith("Interceptador")),
                       "para_o_chrome": sum(1 for c in todas if str(c.get("encaminhado") or "").startswith("Chrome")),
                       "selos_que_mudaram": dict(selos), "por_degrau": dict(por_degrau)},
            "por_item": itens, "por_balcao": por_balcao, "certidoes": enxuta}


if __name__ == "__main__":
    a = sys.argv[1:]
    lim = int(a[a.index("--limite") + 1]) if "--limite" in a else None
    seg = int(a[a.index("--segundos") + 1]) if "--segundos" in a else None
    print(json.dumps(run(lim, seg), ensure_ascii=False, indent=1))
