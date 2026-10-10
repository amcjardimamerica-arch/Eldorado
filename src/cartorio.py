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
GABARITOS = PASTA / "gabaritos.json"
APRENDE = ("seção", "texto", "cronograma")                  # métodos cujo rótulo vale aprender (não: cabeçalho, domínio, palavras-chave)


def aprender(gab: dict, chave: str | None, pontos: dict) -> int:
    """Guarda o rótulo de cada item achado num documento OFICIAL deste órgão (os mais frequentes primeiro)."""
    if not chave:
        return 0
    n = 0
    g = gab.setdefault(chave, {"itens": {}, "documentos": 0, "atualizado": None})
    g["documentos"] += 1; g["atualizado"] = _agora()
    for item, v in pontos.items():
        if v.get("metodo") not in APRENDE or item not in L.COM_ROTULO:
            continue
        a = L.ancora(v.get("trecho") or "", v.get("valor") or "")
        if a:
            cont = g["itens"].setdefault(item, {})
            cont[a] = cont.get(a, 0) + 1; n += 1
            if len(cont) > 12:                                   # guarda só os rótulos mais frequentes
                for k in sorted(cont, key=lambda k: cont[k])[:len(cont) - 12]:
                    cont.pop(k)
    return n


def aprender_das_validacoes(gab: dict, fluxo: dict) -> int:
    """Os itens JÁ VALIDADOS com trecho (Interceptador, validação individual, titular) ensinam os rótulos de cada órgão —
    inclusive rótulos que a extração padrão não conhece. É o que faz o gabarito render além do que o Cartório já acha."""
    n = 0
    for lista in (fluxo.get("itens_por_uf") or {}).values():
        for x in lista:
            pts = {k: {"valor": v.get("v"), "trecho": v.get("t"), "metodo": "texto"} for k, v in (x.get("checklist") or {}).items()
                   if isinstance(v, dict) and v.get("s") in ("ok", "val") and v.get("v") and v.get("t") and v.get("de") != "Cartório"}
            if pts:
                for chave in L.chaves_orgao(str(x.get("link_oficial") or x.get("url") or ""), str(x.get("orgao") or "")):
                    sig = hashlib.sha1(json.dumps([x.get("id"), sorted(pts)], ensure_ascii=False).encode()).hexdigest()[:10]
                    if sig in ((gab.get(chave) or {}).get("validacoes_vistas") or []):
                        continue                                  # não conta a mesma validação duas vezes
                    n += aprender(gab, chave, pts)
                    gab[chave]["validacoes_vistas"] = ((gab[chave].get("validacoes_vistas") or []) + [sig])[-200:]
    return n


def ancoras_do_orgao(gab: dict, chave, minimo: int = 1, por_item: int = 5) -> dict:
    """Rótulos aprendidos do órgão — aceita uma chave ou a lista de chaves (CNPJ/domínio + nome), somando as contagens."""
    soma: dict = {}
    for k in ([chave] if isinstance(chave, str) or chave is None else chave):
        for item, c in (((gab or {}).get(k or "") or {}).get("itens") or {}).items():
            for a, n in c.items():
                soma.setdefault(item, {}); soma[item][a] = soma[item].get(a, 0) + n
    return {item: [a for a, n in sorted(c.items(), key=lambda x: -x[1]) if n >= minimo][:por_item] for item, c in soma.items()}
FLUXO = ROOT / "docs/dados/fluxo_oportunidades.json"
CATALOGO = ROOT / "biblioteca_alexandria/fontes/motores.json"
VERSAO = "cartório v5 · linha de produção (09/10/2026)"
FALTA = ("falta", "pend", "ref", "prov", None)
BUSCAS_MAX = 10                                            # 09/10 (titular): até 10 tentativas, cada uma com abordagem diferente


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


PNCP_ANEXOS = 10                                       # v3: o aviso do PNCP é curto; o edital completo vem nos anexos


def _prioridade_anexo(nome: str) -> int:
    """Edital primeiro; depois termo de referência e anexos do edital; atas, resultados e erratas por último."""
    n = str(nome or "")
    if re.search(r"(?i)ata\b|resultado|homologa|errata|retifica|impugna|recurso|esclarecimento", n):
        return 4
    if re.search(r"(?i)edital|regulamento", n):
        return 0
    if re.search(r"(?i)termo de refer|plano de trabalho|projeto b[áa]sico|anexo", n):
        return 1
    if re.search(r"(?i)chamamento|chamada|aviso", n):
        return 2                                         # o aviso costuma ser o resumo do edital
    return 3


def documentos(op: dict, rede: Rede, maximo: int = 4, pncp_teto: int | None = None) -> list[dict]:
    """Escada de degraus: devolve documentos candidatos [{url, degrau, como, bytes, tipo}] — o oficial primeiro."""
    b = balcao(op); out, vistos = [], set()

    _pt = PNCP_ANEXOS if pncp_teto is None else pncp_teto
    teto = max(maximo, _pt) if b == "pncp" else maximo

    def add(url, degrau, como):
        if url and url not in vistos and len(out) < teto:
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
            arqs.sort(key=lambda a: _prioridade_anexo(f"{a.get('titulo')} {a.get('tipoDocumentoNome')}"))
            for a in arqs[:max(maximo, _pt)]:
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
def certificar(op: dict, faltam: list[str], rede: Rede, maximo_docs: int = 4, gab: dict | None = None,
               docs: list[dict] | None = None, ajustes: dict | None = None) -> dict:
    """Uma oportunidade: escada de degraus → leitura → extração → certidão (só os itens que FALTAVAM contam)."""
    cert = {"id": op.get("id"), "tipo": op.get("_tipo", "estrela"), "titulo": str(op.get("titulo") or "")[:200], "balcao": balcao(op),
            "faltavam": list(faltam), "em": _agora(), "versao": VERSAO, "link_oficial": None, "degrau": None, "como": None,
            "documentos": [], "itens": {}, "dispensas": {}, "fim": None, "encaminhado": None}
    if cert["balcao"] == "proprio":
        cert.update({"encaminhado": "motor próprio já lê o documento (Ministério Público / Judiciário)",
                     "resolvidos": [], "ainda_faltam": list(faltam), "eficiencia": 0.0})
        return cert
    aj = ajustes or {"seguir_links": True, "paginas": 60}
    fila = list(docs) if docs is not None else documentos(op, rede, maximo_docs)
    titulo = str(op.get("titulo") or "")
    lidos = 0
    i = 0
    teto_lidos = max(maximo_docs, PNCP_ANEXOS, len(fila)) if (cert["balcao"] == "pncp" or docs is not None) else maximo_docs
    while i < len(fila) and lidos < teto_lidos:
        d = fila[i]; i += 1
        raw, tipo, err = rede.get(d["url"])
        reg = {"url": d["url"], "degrau": d["degrau"], "como": d["como"]}
        if err:
            reg["falha"] = err; cert["documentos"].append(reg); continue
        lido = L.paginas(raw, tipo, int(aj.get("paginas") or 60))
        reg.update({"motivo": lido.get("motivo"), "tipo": lido.get("tipo"), "paginas": len(lido.get("paginas") or []),
                    "sha1": hashlib.sha1(raw).hexdigest()[:16]})
        # degrau 1 e 2: a página não é o documento — segue os links do próprio site oficial / da pista
        if lido.get("tipo") == "html" and aj.get("seguir_links", True):
            html = lido.get("html") or ""
            if L.regua(d["url"])[0]:
                for u, rot in L.links_de_documento(html, d["url"]):
                    if len(fila) < maximo_docs + int(aj.get("extra") or 4) and u not in {x["url"] for x in fila}:
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
            if len(pgs) > 30 and (cert["balcao"] == "diario" or L.DIARIO_URL.search(d["url"])):   # só EDIÇÃO de diário: só o ato
                                                         # (v3b: edital longo de órgão é lido inteiro — antes era descartado)
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
            # GABARITO DO ÓRGÃO: o que a extração padrão não achou, pelos rótulos aprendidos deste órgão; e aprende com este
            if gab is not None and oficial:
                chaves = list(dict.fromkeys(L.chaves_orgao(d["url"], str(op.get("orgao") or "")) + L.chaves_orgao(str(op.get("url") or ""), "")))
                chave = chaves[0] if chaves else None
                extra = L.aplicar_gabarito(pgs, ancoras_do_orgao(gab, chaves), d["url"], set(ex["pontos"]))
                for k, v in extra.items():
                    ex["pontos"][k] = v; ex["dispensas"].pop(k, None)
                cert["gabarito"] = {"orgao": chave, "itens_pelo_gabarito": sorted(extra)} if extra else cert.get("gabarito")
                for _k in chaves:
                    aprender(gab, _k, {k: v for k, v in ex["pontos"].items() if k not in extra})
            reg["oficial"] = porque
            for k, v in ex["pontos"].items():
                if k in faltam and k not in cert["itens"]:
                    cert["itens"][k] = v
                    cert["dispensas"].pop(k, None)
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
                    "link_oficial": p.get("fonte_oficial") or e.get("site_oficial"), "url": x.get("pagina"),
                    "historico_urls": [h.get("pagina_oficial") for h in (x.get("historico") or []) if isinstance(h, dict) and h.get("pagina_oficial")][-5:]})
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
        info_nova = c and c.get("assinatura") != _assinatura(op)
        # 09/10 (titular): até 3 buscas por oportunidade; depois disso só volta se chegar informação NOVA dos motores
        if c and int(c.get("tentativa") or 1) >= BUSCAS_MAX and not info_nova:
            continue
        if not c or info_nova or str(c.get("em") or "") < limite or leitor_novo:
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
def _baixar_ponte(url: str) -> tuple[bytes, str]:
    """Abordagem 8: só pela ponte do computador do titular (IP do Brasil)."""
    from . import ponte_brasil as PB
    if not PB.configurada():
        raise RuntimeError("ponte do titular não configurada")
    st, _f, corpo, hdr = PB.abrir(url, timeout=60)
    if st != 200 or not corpo:
        raise RuntimeError(f"ponte: HTTP {st}")
    return corpo, (hdr or {}).get("content-type", "")


INTERVALO_HORAS = 12                                       # entre duas tentativas da mesma oportunidade


def _ultima(c: dict) -> str:
    h = c.get("abordagens") or []
    return str((h[-1] if h else c).get("em") or "")


def _vez(op: dict, certs: dict, agora: datetime) -> tuple[bool, dict | None, list[int]]:
    """(é a vez dela?, certidão anterior, abordagens já usadas). Limite de 10; informação nova entra na hora."""
    from . import cartorio_linha as LN
    ant = certs.get(f"{op['_tipo']}:{op['id']}")
    usadas = [h["n"] for h in (ant or {}).get("abordagens") or []] or ([1] if ant else [])
    if len(usadas) >= LN.MAX_TENTATIVAS:
        return False, ant, usadas
    if not ant or ant.get("assinatura") != _assinatura(op):
        return True, ant, usadas
    return _ultima(ant) < (agora - timedelta(hours=INTERVALO_HORAS)).isoformat(), ant, usadas


def run(limite: int | None = None, segundos: int | None = None, rede: Rede | None = None,
        fluxo: dict | None = None, catalogo: dict | None = None, gravar: bool = True, rede_ponte: Rede | None = None) -> dict:
    """LINHA DE PRODUÇÃO (09/10): balcões por selo (sem estrela → bronze → prata → ouro), uma abordagem diferente por
    tentativa (até 10), itens acumulados, e a oportunidade que sobe de selo segue na hora para o balcão seguinte."""
    from collections import deque
    from . import cartorio_linha as LN
    c = cfg(); hoje = date.today().isoformat(); t0 = time.time(); agora = datetime.now(timezone.utc)
    limite = limite or int(c["oportunidades_por_execucao"]); segundos = segundos or int(c["segundos_por_execucao"])
    rede = rede or Rede(pausa=float(c["pausa_segundos"]))
    rede_ponte = rede_ponte or Rede(baixar=_baixar_ponte, pausa=float(c["pausa_segundos"]))
    base = _j(CERTIDOES, {}) or {}
    certs = base.get("certidoes") or {}
    gab = _j(GABARITOS, {}) or {}
    fluxo = fluxo if fluxo is not None else _j(FLUXO, {})
    catalogo = catalogo if catalogo is not None else _j(CATALOGO, {})
    try:
        aprender_das_validacoes(gab, fluxo)
    except Exception:  # noqa: BLE001
        pass
    bib = LN.construir_biblioteca(catalogo, certs)
    todas = fila_estrelas(fluxo) + fila_livros(catalogo)
    na_linha = {"sem_estrela": 0, "bronze": 0, "prata": 0}
    devidas, esgotadas = [], 0
    for op in todas:
        op["_estagio"] = LN.estagio(op)
        if not op["_estagio"]:
            continue
        na_linha[op["_estagio"]] += 1
        vez, ant, usadas = _vez(op, certs, agora)
        if len(usadas) >= LN.MAX_TENTATIVAS:
            esgotadas += 1
        if vez:
            op["_usadas"] = usadas
            devidas.append(op)

    def prio(op):
        fim = str(op.get("fim") or "")[:10]
        foco_falta = sum(1 for k in LN.FOCO[op["_estagio"]] if k in (op.get("_faltam") or []))
        return (0 if (fim and fim >= hoje) else 1, fim or "9999", len(op["_usadas"]), -_nota_rede(op), foco_falta)
    devidas.sort(key=prio)
    livros_max = int(c["livros_por_execucao"])
    est_q = [o for o in devidas if o["_tipo"] == "estrela"]; liv_q = [o for o in devidas if o["_tipo"] == "livro"]
    fila = deque((est_q[:max(1, limite - min(len(liv_q), livros_max))] + liv_q[:livros_max])[:limite])
    feitas, novas_linhas, erros, promovidas, sem_material, repassadas = [], [], [], 0, 0, set()
    while fila and time.time() - t0 <= segundos:
        op = fila.popleft()
        chave = f"{op['_tipo']}:{op['id']}"
        ant = certs.get(chave)
        usadas = [h["n"] for h in (ant or {}).get("abordagens") or []] or ([1] if ant else [])
        faltam = op.get("_faltam") or (["Objeto"] if op.get("_sem_site") else [])
        est0 = op["_estagio"]
        escolhida, docs, aj = None, [], {}
        for n in LN.proxima_abordagem(est0, usadas):
            try:
                docs, aj = LN.documentos(n, op, rede, ant, bib, int(c["documentos_por_oportunidade"]))
            except Exception:  # noqa: BLE001
                docs = []
            if docs:
                escolhida = n
                break
        if not escolhida:
            sem_material += 1                              # nada novo a tentar agora: volta quando chegar material
            continue
        try:
            nova = certificar(op, faltam, rede_ponte if aj.get("ponte") else rede, int(c["documentos_por_oportunidade"]), gab, docs, aj)
        except Exception as ex:  # noqa: BLE001 — uma oportunidade com erro nunca derruba a fila inteira
            import traceback
            nova = {"id": op.get("id"), "tipo": op.get("_tipo"), "titulo": str(op.get("titulo") or "")[:200], "balcao": "?",
                    "documentos": [], "itens": {}, "dispensas": {}, "em": _agora(), "versao": VERSAO, "link_oficial": None,
                    "encaminhado": f"Interceptador: erro no Cartório ({type(ex).__name__})", "erro": traceback.format_exc()[-800:]}
            erros.append({"id": op.get("id"), "erro": f"{type(ex).__name__}: {str(ex)[:200]}"})
        nova.pop("_aprendeu", None)
        cert = LN.acumular(ant, nova, escolhida, faltam)
        cert.update({"assinatura": _assinatura(op), "primeira_em": (ant or {}).get("primeira_em") or (ant or {}).get("em") or cert.get("em"),
                     "prazo": op.get("fim"), "uf": op.get("uf"), "orgao": op.get("orgao"), "origem": op.get("origem"),
                     "estagio_inicio": (ant or {}).get("estagio_inicio") or est0, "versao": VERSAO})
        if op["_tipo"] == "estrela":
            from .criterio_selos import nivel
            ck = dict(op.get("checklist") or {})
            for k in list(cert["itens"]) + list(cert["dispensas"]):
                ck[k] = item_checklist_de(cert, k)
            cert["selo_antes"] = (ant or {}).get("selo_antes", nivel(op.get("checklist") or {}))
            cert["selo_depois"] = nivel(ck)
            op2 = {**op, "checklist": ck}
            est1 = LN.estagio(op2)
            cert["estagio"] = est1 or "ouro"
            # LINHA DE PRODUÇÃO: subiu de selo nesta tentativa → segue já para o balcão seguinte (uma vez por execução)
            if est1 != est0:
                promovidas += 1
                if est1 and chave not in repassadas and cert["tentativa"] < LN.MAX_TENTATIVAS:
                    repassadas.add(chave)
                    op2["_estagio"] = est1; op2["_faltam"] = [k for k in L.DOZE if (ck.get(k) or {}).get("s") in FALTA]
                    fila.appendleft(op2)
        else:
            cert["estagio"] = est0
            novas_linhas += linhas_livro(op, cert)
        certs[chave] = cert
        feitas.append(cert)
    para_int = [{"id": x["id"], "tipo": x["tipo"], "titulo": x["titulo"], "motivo": x["encaminhado"], "faltam": x.get("ainda_faltam")}
                for x in certs.values() if str(x.get("encaminhado") or "").startswith("Interceptador")]
    rel = relatorio(certs, feitas, sum(1 for o in todas if o.get("_tipo") == "estrela" and o.get("_estagio")),
                    sum(1 for o in todas if o.get("_tipo") == "livro" and o.get("_estagio")), gab)
    rel["linha_de_producao"] = {"na_linha": na_linha, "devidas_nesta_hora": len(devidas), "promovidas_nesta_execucao": promovidas,
                                "sem_material_agora": sem_material, "esgotadas_10_abordagens": esgotadas,
                                "biblioteca_de_sites": {"chaves": len(bib), "sites": sum(len(v["urls"]) for v in bib.values())},
                                "intervalo_horas": INTERVALO_HORAS, "limite": LN.MAX_TENTATIVAS,
                                "balcoes": {k: {"nome": LN.NOME_BALCAO[k], "foco": LN.FOCO[k],
                                                "ordem": [f"{n} · {LN.ABORDAGENS[n]}" for n in LN.ORDEM[k]]} for k in LN.ORDEM}}
    if gravar:
        PASTA.mkdir(parents=True, exist_ok=True)
        CERTIDOES.write_text(json.dumps({"em": _agora(), "versao": VERSAO, "certidoes": certs}, ensure_ascii=False, indent=1), encoding="utf-8")
        GABARITOS.write_text(json.dumps(gab, ensure_ascii=False, indent=1), encoding="utf-8")
        LN.BIBLIOTECA.parent.mkdir(parents=True, exist_ok=True)
        LN.BIBLIOTECA.write_text(json.dumps({"em": _agora(), "chaves": len(bib), "sites": bib}, ensure_ascii=False, indent=1), encoding="utf-8")
        INTERCEPTADOR.write_text(json.dumps({"em": _agora(), "regra": "só o que o Cartório não resolveu (até 10 abordagens)", "itens": para_int[:300]},
                                            ensure_ascii=False, indent=1), encoding="utf-8")
        if novas_linhas:
            (PASTA / "novos_livros.jsonl").write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in novas_linhas) + "\n", encoding="utf-8")
            with LIVROS_OUT.open("a", encoding="utf-8") as fh:
                for x in novas_linhas:
                    fh.write(json.dumps(x, ensure_ascii=False) + "\n")
        RELATORIO.parent.mkdir(parents=True, exist_ok=True)
        RELATORIO.write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")
        _CACHE.clear()
    return {"certificadas": len(feitas), "na_linha": na_linha, "devidas": len(devidas), "promovidas": promovidas,
            "sem_material": sem_material, "esgotadas": esgotadas, "linhas_livros": len(novas_linhas),
            "acessos": rede.n, "segundos": round(time.time() - t0), "eficiencia": rel["resumo"]["eficiencia_itens"], "erros": erros[:20]}


def item_checklist_de(cert: dict, item: str) -> dict:
    v = (cert.get("itens") or {}).get(item)
    if v:
        return {"s": "ok", "v": str(v["valor"])[:90]}
    d = (cert.get("dispensas") or {}).get(item) or {}
    return {"s": "disp", "v": d.get("motivo", "")[:160]}


def cobertura_12(c: dict) -> dict:
    """Os 12 pontos da certidão em 4 estados — a mesma conta da página (docs/cartorio.html, função cob)."""
    it, ds, fa = c.get("itens") or {}, c.get("dispensas") or {}, c.get("faltavam") or []
    est = {k: "certificado" if k in it else "dispensado" if k in ds else "falta" if k in fa else "ja_constava" for k in L.DOZE}
    n = lambda e: sum(1 for v in est.values() if v == e)
    return {"estados": est, "certificados": n("certificado"), "dispensados": n("dispensado"), "ja_constavam": n("ja_constava"),
            "faltam": n("falta"), "pct_certificado_12": round((n("certificado") + n("dispensado")) / 12, 4),
            "pct_cobertura_12": round((n("certificado") + n("dispensado") + n("ja_constava")) / 12, 4)}


def relatorio(certs: dict, feitas: list[dict], fila_e: int, fila_l: int, gab: dict | None = None) -> dict:
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
    # v3: EFICIÊNCIA POR SAFRA — 1ª tentativa (fila nova) separada das refeitas (os casos difíceis) e por versão do leitor
    def _safra(grupo):
        f = sum(len(c.get("faltavam") or []) for c in grupo); r = sum(len(c.get("resolvidos") or []) for c in grupo)
        return {"certidoes": len(grupo), "faltavam": f, "resolvidos": r, "eficiencia": round(r / f, 3) if f else None,
                "com_link_oficial": sum(1 for c in grupo if c.get("link_oficial")),
                "taxa_link_oficial": round(sum(1 for c in grupo if c.get("link_oficial")) / len(grupo), 3) if grupo else None}
    pelo_gabarito = Counter(k for c in todas for k in ((c.get("gabarito") or {}).get("itens_pelo_gabarito") or []))
    # 09/10 (linha de produção): o que cada uma das 10 abordagens rendeu, e cada balcão de selo
    from .cartorio_linha import ABORDAGENS, NOME_BALCAO
    por_abordagem = {n: {"nome": nome, "vezes": 0, "renderam": 0, "itens": 0, "links_oficiais": 0} for n, nome in ABORDAGENS.items()}
    for c in todas:
        for h in c.get("abordagens") or []:
            a = por_abordagem.get(h.get("n"))
            if a and not h.get("legado"):
                a["vezes"] += 1; a["itens"] += len(h.get("ganhou") or []); a["renderam"] += bool(h.get("ganhou"))
                a["links_oficiais"] += bool(h.get("link_oficial_novo"))
    for a in por_abordagem.values():
        a["taxa_de_acerto"] = round(a["renderam"] / a["vezes"], 3) if a["vezes"] else None
    por_balcao_selo = {}
    for k, nome in {**NOME_BALCAO, "ouro": "Ouro (saiu da linha)"}.items():
        g = [c for c in todas if (c.get("estagio") or c.get("estagio_inicio")) == k]
        f = sum(len(c.get("faltavam") or []) for c in g); r = sum(len(c.get("resolvidos") or []) for c in g)
        por_balcao_selo[k] = {"nome": nome, "certidoes": len(g), "faltavam": f, "resolvidos": r, "eficiencia": round(r / f, 3) if f else None,
                              "entraram_aqui": sum(1 for c in todas if c.get("estagio_inicio") == k),
                              "esgotadas": sum(1 for c in g if c.get("esgotada"))}
    safras = {"primeira tentativa": _safra([c for c in todas if int(c.get("tentativa") or 1) == 1]),
              "refeitas": _safra([c for c in todas if int(c.get("tentativa") or 1) > 1])}
    versoes = {}
    for c in todas:
        versoes.setdefault(str(c.get("versao") or "?").split(" (")[0], []).append(c)
    por_versao = {v: _safra(g) for v, g in sorted(versoes.items())}
    itens = {k: {"faltavam": pedido[k], "obtidos": obtido[k], "dispensados": dispensado[k],
                 "eficiencia": round((obtido[k] + dispensado[k]) / pedido[k], 3) if pedido[k] else None} for k in L.DOZE}
    lista = sorted(todas, key=lambda c: (-(c.get("eficiencia") or 0), c.get("titulo") or ""))
    enxuta = [{k: c.get(k) for k in ("id", "tipo", "titulo", "balcao", "link_oficial", "degrau", "como", "faltavam", "resolvidos", "ainda_faltam", "tentativa", "versao", "gabarito",
                                      "estagio", "estagio_inicio", "esgotada",
                                      "eficiencia", "encaminhado", "selo_antes", "selo_depois", "em", "prazo", "uf", "orgao", "fim")} |
              {"itens": {k: {kk: v.get(kk) for kk in ("valor", "trecho", "pagina", "documento", "metodo")} for k, v in (c.get("itens") or {}).items()},
               "dispensas": {k: {kk: v.get(kk) for kk in ("motivo", "trecho", "pagina", "documento")} for k, v in (c.get("dispensas") or {}).items()},
               "abordagens": [{kk: h.get(kk) for kk in ("n", "nome", "em", "ganhou", "legado")} for h in (c.get("abordagens") or [])],
               "documentos": [{kk: d.get(kk) for kk in ("url", "degrau", "como", "motivo", "falha", "oficial", "paginas", "edicao_inteira")} for d in c.get("documentos") or []]}
              for c in lista[:400]]
    # 10/10 (titular): COBERTURA DOS 12 PONTOS — o % da certidão era resolvidos ÷ itens que faltavam na ENTRADA da fila
    # (1 de 1 = 100% com um só ponto verde). Agora cada certidão leva os 12 em 4 estados e o resumo, o % sobre os 12.
    for c in enxuta:
        c["cobertura_12"] = cobertura_12(c)
    _cb = [c["cobertura_12"] for c in enxuta]; _n12 = len(_cb) * 12
    _som = {k: sum(x[k] for x in _cb) for k in ("certificados", "dispensados", "ja_constavam", "faltam")}
    cob12 = {"pontos_12_total": _n12, **{f"pontos_{k}": v for k, v in _som.items()},
             "pct_certificado_12": round((_som["certificados"] + _som["dispensados"]) / _n12, 4) if _n12 else None,
             "certidoes_12_de_12": sum(1 for x in _cb if x["certificados"] + x["dispensados"] == 12),
             "certidoes_sem_item_faltando": sum(1 for c in enxuta if c["cobertura_12"]["faltam"] == 0 and c.get("link_oficial")),
             "nota_denominador": "eficiencia_itens = resolvidos ÷ itens que faltavam na ENTRADA da fila (não é % dos 12); use pct_certificado_12"}
    return {"em": _agora(), "versao": VERSAO, "regra": __doc__.split("Execução:")[0].strip(),
            "identidade_visual": "provisória (config/identidade_visual.json aguarda o design de referência)",
            "resumo": {**cob12, "certidoes": len(todas), "nesta_execucao": len(feitas), "fila_estrelas": fila_e, "fila_livros": fila_l,
                       "itens_que_faltavam": tf, "itens_obtidos": sum(obtido.values()), "itens_dispensados": sum(dispensado.values()),
                       "eficiencia_itens": round(tr / tf, 3) if tf else None,
                       "com_link_oficial": sum(1 for c in todas if c.get("link_oficial")),
                       "taxa_link_oficial": round(sum(1 for c in todas if c.get("link_oficial")) / len(todas), 3) if todas else None,
                       "certidoes_completas": sum(1 for c in todas if not c.get("ainda_faltam") and c.get("link_oficial")),
                       "para_o_interceptador": sum(1 for c in todas if str(c.get("encaminhado") or "").startswith("Interceptador")),
                       "para_o_chrome": sum(1 for c in todas if str(c.get("encaminhado") or "").startswith("Chrome")),
                       "selos_que_mudaram": dict(selos), "por_degrau": dict(por_degrau)},
            "por_item": itens, "por_balcao": por_balcao, "por_safra": safras, "por_versao": por_versao,
            "por_abordagem": por_abordagem, "por_balcao_selo": por_balcao_selo,
            "gabarito": {"orgaos_com_gabarito": sum(1 for g in (gab if gab is not None else (_j(GABARITOS, {}) or {})).values() if g.get("itens")), "itens_achados_pelo_gabarito": dict(pelo_gabarito),
                         "certidoes_ajudadas": sum(1 for c in todas if (c.get("gabarito") or {}).get("itens_pelo_gabarito"))},
            "certidoes": enxuta}


if __name__ == "__main__":
    a = sys.argv[1:]
    lim = int(a[a.index("--limite") + 1]) if "--limite" in a else None
    seg = int(a[a.index("--segundos") + 1]) if "--segundos" in a else None
    print(json.dumps(run(lim, seg), ensure_ascii=False, indent=1))
