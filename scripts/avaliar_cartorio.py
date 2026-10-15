"""AVALIAÇÃO DO CARTÓRIO COM GABARITO (titular, 15/10/2026).

Mede a extração atual dos 12 itens contra os casos JÁ COMPROVADOS por leitura humana do documento oficial
(conferências no Chrome de 10–11/10: dados/revisoes/fila_chrome_2026_10_11). O gabarito aprendido por órgão
(estado/cartorio/gabaritos.json) NUNCA é usado como verdade: foi produzido pela própria extração.

Duas etapas:
  --baixar   (precisa de rede; roda no GitHub Actions) baixa o documento de cada caso com a MESMA rede e a MESMA
             leitura do Cartório (src.cartorio.Rede + cartorio_leitura.paginas) e guarda o texto por página em
             estado/cartorio/avaliacao/textos.json.gz — sem guardar o PDF.
  --medir    (sem rede) roda cartorio_leitura.extrair no texto guardado, compara item a item com o gabarito e grava
             estado/cartorio/avaliacao/resultado.json + docs/relatorios/avaliacao-cartorio-AAAA-MM-DD.md.

Classificação de cada item de cada caso:
  acerto       a extração achou o item e o valor confere com o gabarito
  erro         achou, mas o valor não confere (diz onde pegou e onde estava o certo)
  falta        o gabarito tem o item, o documento contém o trecho, e a extração não achou → defeito de REGRA
  fora         o trecho do gabarito não está no documento lido (veio de outra fonte: API do PNCP, outro anexo,
               página HTML) → não conta contra a regra; vira pendência de DOCUMENTO
  sem_texto    o documento não pôde ser lido (rede, escaneado, formato) → pendência de LEITURA
Dispensas: gabarito dispensa e a extração dispensa (ou não acha) = acerto; extração inventa valor = erro.
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import re
import sys
import time
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import cartorio_leitura as L  # noqa: E402

FILA = ROOT / "dados/revisoes/fila_chrome_2026_10_11"
PASTA = ROOT / "estado/cartorio/avaliacao"
TEXTOS = PASTA / "textos.json.gz"
RESULTADO = PASTA / "resultado.json"
HISTORICO = PASTA / "historico.json"
RELATORIOS = ROOT / "docs/relatorios"

TEXTUAIS = ("Objeto", "Requisitos", "Destinação")
STOP = set("para pela pelo pelas pelos como mais seus suas esta este essa esse entre sobre todos todas cada desde "
           "serao sera deverao devera poderao podera com sem que dos das nos nas uma umas uns por qual quais "
           "edital chamamento publico publica presente".split())


# ── CASOS COMPROVADOS ──────────────────────────────────────────────────────────────────────────────────────────────
def casos() -> dict:
    """id → {url, titulo, orgao, itens, dispensas, prazo}. O REFAZER (refeito à mão) prevalece sobre os lotes."""
    meta = {}
    for f in sorted(FILA.glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        for r in (d.get("registros") or []) if isinstance(d, dict) else []:
            if isinstance(r, dict) and r.get("id"):
                meta.setdefault(r["id"], r)
    out = {}
    arqs = sorted(glob.glob(str(FILA / "resultados/resultado_*.json"))) + sorted(glob.glob(str(FILA / "refazer/resultado_*.json")))
    for f in arqs:                                   # refazer por último: sobrescreve
        for k, v in json.loads(Path(f).read_text(encoding="utf-8")).items():
            if not (isinstance(v, dict) and v.get("link_documento") and (v.get("itens") or v.get("dispensas"))):
                continue
            m = meta.get(k, {})
            out[k] = {"id": k, "url": v["link_documento"], "titulo": str(m.get("titulo") or ""), "orgao": str(m.get("orgao") or ""),
                      "itens": {i: x for i, x in (v.get("itens") or {}).items() if isinstance(x, dict)},
                      "dispensas": {i: x for i, x in (v.get("dispensas") or {}).items()}, "prazo": v.get("prazo") or {}}
    return out


# ── ETAPA A: BAIXAR (rede) ─────────────────────────────────────────────────────────────────────────────────────────
def url_do_documento(url: str) -> str:
    """Página do PNCP (/app/editais/CNPJ/ANO/SEQ) não é documento: o Cartório usa a API de arquivos (o edital é o 1)."""
    m = re.search(r"pncp\.gov\.br/app/editais/(\d{14})/(\d{4})/(\d+)", url)
    return f"https://pncp.gov.br/pncp-api/v1/orgaos/{m.group(1)}/compras/{m.group(2)}/{m.group(3)}/arquivos/1" if m else url


def baixar(limite: int | None = None, segundos: int = 2400) -> dict:
    from src.cartorio import Rede
    rede = Rede(pausa=0.5)
    cs = casos()
    antigos = _ler_textos()
    t0 = time.time()
    out = {}
    for n, (k, c) in enumerate(cs.items()):
        if limite and n >= limite:
            break
        u = url_do_documento(c["url"])
        velho = antigos.get(k)
        if velho and velho.get("url") == u and velho.get("ok"):
            out[k] = velho; continue
        if time.time() - t0 > segundos:
            if velho:
                out[k] = velho
            continue
        raw, tipo, err = rede.get(u)
        reg = {"url": u, "baixado_em": _agora()}
        if err or not raw:
            reg.update({"ok": False, "motivo": err or "vazio", "paginas": []})
            if err == "robots_proibe":
                from src import executor_skills as X
                from urllib.parse import urlsplit
                b = "{0.scheme}://{0.netloc}".format(urlsplit(u))
                reg["robots"] = X.robots_motivos.get(b)
        else:
            lido = L.paginas(raw, tipo, 60)
            reg.update({"ok": bool(lido.get("ok")), "motivo": lido.get("motivo"), "tipo": lido.get("tipo"),
                        "bytes": len(raw), "paginas": lido.get("paginas") or []})
            if lido.get("tipo") == "html":     # guarda os links de documento da página (diagnóstico do degrau 1)
                reg["links_doc"] = L.links_de_documento(lido.get("html") or "", u)[:15]
        out[k] = reg
        print(f"{n + 1:3d} {k} {'ok ' if reg['ok'] else 'NÃO'} {reg.get('motivo') or ''} {u[:90]}", flush=True)
    PASTA.mkdir(parents=True, exist_ok=True)
    with gzip.open(TEXTOS, "wt", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False)
    print(f"textos: {sum(1 for r in out.values() if r.get('ok'))}/{len(out)} lidos")
    return out


def _ler_textos() -> dict:
    try:
        with gzip.open(TEXTOS, "rt", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:  # noqa: BLE001
        return {}


# ── COMPARAÇÃO ─────────────────────────────────────────────────────────────────────────────────────────────────────
def sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", str(s or "").lower()) if unicodedata.category(c) != "Mn")


def palavras(s: str) -> set:
    return {w for w in re.findall(r"[a-z0-9]{4,}", sem_acento(s)) if w not in STOP}


def sobrepoe(a: str, b: str) -> float:
    A, B = palavras(a), palavras(b)
    return len(A & B) / min(len(A), len(B)) if A and B else 0.0


def datas(s: str) -> set:
    s = str(s or "")
    out = {x for x in (L._data_iso(d) for d in re.findall(L.DATA, s, re.I)) if x}
    out |= set(re.findall(r"20\d{2}-\d{2}-\d{2}", s))
    return out


def dias(s: str) -> set:
    return {int(n) for n in re.findall(r"(\d{1,3})\s*(?:\([^)]{1,20}\)\s*)?dias", sem_acento(s))}


def dinheiro(s: str) -> set:
    out = set()
    for m in re.findall(r"R\$\s?(\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?)", str(s or "")):
        try:
            out.add(round(float(m.replace(".", "").replace(",", ".")), 2))
        except ValueError:
            pass
    return out


ESFERAS = (("municipal", r"munic|prefeit|\bm\b"), ("estadual", r"estad|\be\b|governo do"), ("federal", r"feder|uniao|minist|\bf\b"),
           ("privada", r"privad|empresa|institut|funda|associa|\bp\b"))


def esfera(s: str) -> str | None:
    s = sem_acento(s)
    for nome, rx in ESFERAS:
        if re.search(rx, s):
            return nome
    return None


def areas(s: str) -> set:
    return {a for a, rx in L.AREAS.items() if re.search(rx, str(s or ""), re.I)}


def confere(item: str, ext: dict, gab: dict, prazo: dict) -> bool:
    ev, et = str(ext.get("valor") or ""), str(ext.get("trecho") or "")
    gv, gt = str(gab.get("valor") or ""), str(gab.get("trecho") or "")
    e, g = ev + " " + et, gv + " " + gt
    if item == "Prazo de inscrição":
        fim = str((prazo or {}).get("fim") or "")[:10]
        de = datas(ev)
        if fim and de:
            return max(de) == fim
        return bool(de & datas(g))
    if item in ("Resultado", "Prazo de recurso"):
        if (datas(ev) & datas(g)) or (dias(ev) & dias(g)):
            return True
        return sobrepoe(et, gt) >= 0.5
    if item == "Valor":
        return bool(dinheiro(ev) & dinheiro(g))
    if item == "Esfera":
        return esfera(ev) is not None and esfera(ev) == esfera(gv)
    if item == "Área de atuação":
        return bool(areas(ev) & (areas(gv) or areas(gt)))
    if item == "Órgão / financiador":
        return sobrepoe(ev, gv) >= 0.5
    if item == "Território":
        if re.search(r"nacional|todo o territ", sem_acento(g)):
            return bool(re.search(r"nacional|todo o territ", sem_acento(e)))
        return bool(palavras(ev) & palavras(gv)) or sobrepoe(ev, gv) >= 0.5
    if item == "Anexos":
        re_an = r"anexo\s+([ivxl]{1,5})\b"
        ae, ag = set(re.findall(re_an, sem_acento(e))), set(re.findall(re_an, sem_acento(g)))
        return bool(ae) and (not ag or len(ae & ag) / len(ag) >= 0.5)
    # textuais: Objeto, Requisitos, Destinação
    s = max(sobrepoe(e, g), sobrepoe(et, gt))
    return s >= 0.35 or (s >= 0.2 and ext.get("pagina") and ext.get("pagina") == gab.get("pagina"))


def compacto(s: str) -> tuple[str, list[int]]:
    """Só letras e números, sem acento, com o mapa para a posição original (o PDF cola e separa palavras)."""
    out, mapa = [], []
    for i, ch in enumerate(sem_acento(s)):
        if ch.isalnum():
            out.append(ch); mapa.append(i)
    return "".join(out), mapa


def no_documento(trecho: str, doc: tuple[str, list[int]]) -> tuple[bool, int | None]:
    """O trecho do gabarito está no texto lido? Procura pedaços de 28 caracteres (só letras e números)."""
    t = re.sub(r"\(p\. ?\d+\)|\.\.\.|…", " ", str(trecho or ""))
    alvo = compacto(t)[0]
    comp, mapa = doc
    if len(alvo) < 16 or not comp:
        return False, None
    n = 28 if len(alvo) >= 28 else len(alvo)
    for i in range(0, max(1, len(alvo) - n + 1), 9):
        j = comp.find(alvo[i:i + n])
        if j >= 0:
            return True, mapa[j]
    return False, None


def medir(com_gabarito_orgao: bool = False, gravar: bool = True, rotulo: str = "") -> dict:
    cs, tx = casos(), _ler_textos()
    gab_org = None
    if com_gabarito_orgao:
        from src import cartorio as C
        gab_org = C._j(C.GABARITOS, {}) or {}
    por_item = {i: Counter() for i in L.DOZE}
    falhas = []
    por_caso = {}
    for k, c in cs.items():
        r = tx.get(k)
        pgs = (r or {}).get("paginas") or []
        if r and r.get("ok") and pgs and len(pgs) > 30 and L.DIARIO_URL.search(r.get("url") or ""):
            sel = L.localizar_ato(pgs, c["titulo"], c["orgao"])
            pgs = sel if sel else []
        ok = bool(r and r.get("ok") and pgs)
        ex = L.extrair(pgs, (r or {}).get("url") or c["url"], c["titulo"], c["orgao"]) if ok else {"pontos": {}, "dispensas": {}}
        if ok and gab_org is not None:
            from src import cartorio as C
            chaves = L.chaves_orgao((r or {}).get("url") or c["url"], c["orgao"])
            for kk, v in L.aplicar_gabarito(pgs, C.ancoras_do_orgao(gab_org, chaves), r["url"], set(ex["pontos"])).items():
                ex["pontos"][kk] = v
        T = L.Texto(pgs) if ok else None
        doc = compacto(T.t) if T else ("", [])
        res = {}
        for item in L.DOZE:
            g, gd = c["itens"].get(item), c["dispensas"].get(item)
            e, ed = ex["pontos"].get(item), ex["dispensas"].get(item)
            if not g and not gd:
                continue
            if not ok:
                cl = "sem_texto"
            elif gd and not g:
                cl = "erro" if e else "acerto"
            elif e:
                cl = "acerto" if confere(item, e, g, c["prazo"]) else "erro"
            else:
                cl = "falta"
            if cl in ("erro", "falta") and g:
                achou, pos = no_documento(g.get("trecho") or g.get("valor") or "", doc)
                if not achou and item not in ("Esfera", "Área de atuação", "Território"):
                    cl = "fora"
                f = {"caso": k, "item": item, "classe": cl, "url": (r or {}).get("url"), "gabarito": (g.get("valor") or "")[:200],
                     "trecho_gabarito": (g.get("trecho") or "")[:240], "pagina_gabarito": g.get("pagina"),
                     "pagina_no_texto": T.pagina(pos) if (T and pos is not None) else None}
                if e:
                    f.update({"extraido": str(e.get("valor") or "")[:200], "pagina_extraido": e.get("pagina"), "metodo": e.get("metodo")})
                if ed:
                    f["dispensa_extraida"] = ed.get("motivo")
                if cl != "fora":
                    f["causa"] = causa(item, f, T)
                falhas.append(f)
            por_item[item][cl] += 1
            res[item] = cl
        por_caso[k] = {"url": (r or {}).get("url"), "lido": ok, "motivo": (r or {}).get("motivo"), "itens": res}
    resumo = {}
    for item, ct in por_item.items():
        base = ct["acerto"] + ct["erro"] + ct["falta"]
        resumo[item] = {**dict(ct), "medidos": base, "acerto_pct": round(100 * ct["acerto"] / base, 1) if base else None,
                        "precisao_pct": round(100 * ct["acerto"] / (ct["acerto"] + ct["erro"]), 1) if (ct["acerto"] + ct["erro"]) else None}
    tot = Counter()
    for ct in por_item.values():
        tot.update(ct)
    base = tot["acerto"] + tot["erro"] + tot["falta"]
    out = {"em": _agora(), "rotulo": rotulo, "versao_extracao": getattr(L, "VERSAO", None), "casos": len(cs),
           "documentos_lidos": sum(1 for v in por_caso.values() if v["lido"]),
           "geral": {**dict(tot), "medidos": base, "acerto_pct": round(100 * tot["acerto"] / base, 1) if base else None,
                     "precisao_pct": round(100 * tot["acerto"] / (tot["acerto"] + tot["erro"]), 1) if (tot["acerto"] + tot["erro"]) else None},
           "por_item": resumo, "nao_lidos": dict(Counter(v["motivo"] or "?" for v in por_caso.values() if not v["lido"])),
           "falhas": falhas, "por_caso": por_caso}
    if gravar:
        PASTA.mkdir(parents=True, exist_ok=True)
        RESULTADO.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        h = json.loads(HISTORICO.read_text(encoding="utf-8")) if HISTORICO.exists() else []
        h.append({"em": out["em"], "rotulo": rotulo, "geral": out["geral"], "por_item": {i: v["acerto_pct"] for i, v in resumo.items()}})
        HISTORICO.write_text(json.dumps(h, ensure_ascii=False, indent=1), encoding="utf-8")
        relatorio(out)
    return out


def _pos_original(t: str, pos_plano: int | None) -> int:
    """Converte posição no texto sem acento (mesmo tamanho, pois NFD remove só marcas) — aproximação suficiente."""
    return min(len(t) - 1, max(0, pos_plano or 0))


def causa(item: str, f: dict, T) -> str:
    if f["classe"] == "falta":
        if item == "Prazo de inscrição":
            return "datas do período não estão junto da palavra de inscrição/recebimento (cronograma em tabela ou rótulo diferente)"
        if item in ("Resultado", "Prazo de recurso"):
            return "o cronograma usa outro rótulo ou o prazo vem por extenso/sem a palavra-chave perto do número"
        if item == "Valor":
            return "o valor não vem com 'valor global/total/teto' perto do R$ e não tem milhar com ponto"
        if item in TEXTUAIS:
            return "a seção do item não tem título reconhecido (numeração ou nome fora do padrão)"
        if item == "Órgão / financiador":
            return "o órgão não está na 1ª página com prefixo conhecido (Prefeitura, Secretaria, Ministério…)"
        return "regra não reconheceu o trecho que está no documento"
    pe, pg = f.get("pagina_extraido"), f.get("pagina_no_texto") or f.get("pagina_gabarito")
    if pe and pg and pe != pg:
        return f"pegou outro trecho (página {pe}); o certo está na página {pg}"
    return "pegou o trecho certo da região, mas o valor não confere (formato, intervalo ou item vizinho)"


def relatorio(out: dict) -> Path:
    RELATORIOS.mkdir(parents=True, exist_ok=True)
    p = RELATORIOS / f"avaliacao-cartorio-{out['em'][:10]}.md"
    g = out["geral"]
    ln = [f"# Avaliação do Cartório com gabarito — {out['em'][:16].replace('T', ' ')} UTC", "",
          f"Casos comprovados: **{out['casos']}** · documentos lidos: **{out['documentos_lidos']}** · "
          f"acerto geral: **{g['acerto_pct']}%** (precisão {g['precisao_pct']}%) sobre {g['medidos']} itens medidos.", "",
          "Acerto = achou e confere ÷ (acerto + erro + falta). Precisão = acerto ÷ (acerto + erro). "
          "'Fora' = o trecho do gabarito não está no documento lido (não conta contra a regra). "
          "'Sem texto' = documento não lido.", "",
          "| Item | Acerto | Precisão | Acertos | Erros | Faltas | Fora | Sem texto |", "|---|---|---|---|---|---|---|---|"]
    for i, v in out["por_item"].items():
        ln.append(f"| {i} | {v['acerto_pct']}% | {v['precisao_pct']}% | {v.get('acerto', 0)} | {v.get('erro', 0)} | {v.get('falta', 0)} | "
                  f"{v.get('fora', 0)} | {v.get('sem_texto', 0)} |")
    ln += ["", "## Documentos não lidos", ""] + [f"- {m}: {n}" for m, n in sorted(out["nao_lidos"].items(), key=lambda x: -x[1])]
    ln += ["", "## Causas das falhas por item", ""]
    por = defaultdict(Counter)
    for f in out["falhas"]:
        if f["classe"] in ("erro", "falta"):
            por[f["item"]][f"{f['classe']}: {f.get('causa')}"] += 1
    for i in L.DOZE:
        if por[i]:
            ln.append(f"**{i}**")
            ln += [f"- {n}× {c}" for c, n in por[i].most_common(6)]
            ln.append("")
    ln += ["## Exemplos (até 3 por item)", ""]
    vistos = Counter()
    for f in out["falhas"]:
        if f["classe"] in ("erro", "falta") and vistos[f["item"]] < 3:
            vistos[f["item"]] += 1
            ln.append(f"- **{f['item']}** ({f['classe']}) · caso `{f['caso']}` · {f.get('url')}  \n"
                      f"  gabarito: {f['gabarito'][:140]} (p. {f.get('pagina_no_texto') or f.get('pagina_gabarito')})  \n"
                      f"  extraído: {f.get('extraido') or '—'} (p. {f.get('pagina_extraido') or '—'})  \n  causa: {f.get('causa')}")
    p.write_text("\n".join(ln) + "\n", encoding="utf-8")
    return p


def _agora() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--baixar", action="store_true")
    ap.add_argument("--medir", action="store_true")
    ap.add_argument("--limite", type=int)
    ap.add_argument("--segundos", type=int, default=2400)
    ap.add_argument("--rotulo", default="")
    a = ap.parse_args()
    if a.baixar:
        baixar(a.limite, a.segundos)
    if a.medir or not a.baixar:
        o = medir(rotulo=a.rotulo)
        print(json.dumps({"geral": o["geral"], "por_item": {i: v["acerto_pct"] for i, v in o["por_item"].items()}}, ensure_ascii=False, indent=1))
