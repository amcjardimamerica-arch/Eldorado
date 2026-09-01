"""Eldorado · Campanha de completude — "a busca só termina quando encontra".

REGRA DO TITULAR (01/09/2026): identificar uma publicação em Diário Oficial é
apenas o COMEÇO. A partir dela, o Eldorado busca por até 30 dias consecutivos
o edital integral e seus documentos-modelo nos sites oficiais (secretaria,
prefeitura, governo, ministério, empresa). O edital só é considerado ACHADO
("Eldorado encontrado") quando a verificação é DUPLA:

  1ª verificação — FONTE: a informação foi identificada e a origem registrada
     (diário oficial, PNCP, portal), com URL e evidência hasheada;
  2ª verificação — CONTEÚDO: o edital integral foi obtido de página oficial,
     o texto foi extraído, as datas de inscrição constam e os documentos-
     modelo (anexos preenchíveis) foram preservados em PDF.

Somente editais COMPLETOS alimentam o Dashboard e o Farol de Alexandria.
Os demais permanecem como MONITORAMENTOS na Bússola, com a campanha diária
registrada, até completar ou expirar a janela de 30 dias.

Organização no Farol — uma pasta por edital, subpasta por ano:
  dados/farol/editais/<chave>/<ANO>/
    edital.txt        texto integral convertido (o PDF do edital NÃO é
                      guardado quando existem anexos-modelo; preserva-se
                      apenas o que serve para preencher)
    edital.pdf        somente quando o próprio edital é formulário (AcroForm)
                      ou quando não há anexos-modelo
    dados.json        metadados completos, fontes, hashes, campanha
    anexos/*.pdf      exclusivamente documentos-modelo (anexo, formulário,
                      requerimento, declaração, plano de trabalho, ficha)

Dependência opcional: pypdf (extração de texto e detecção de formulário).
Sem pypdf o motor registra a pendência e nunca finge extração.
"""
from __future__ import annotations

import json
import re
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

from .nucleo import (ROOT, canonical_url, carregar_oportunidades, load_json,
                     now_iso, sha256, slug, write_json)

try:  # opcional: sem pypdf o motor declara a lacuna
    from pypdf import PdfReader
except Exception:  # pragma: no cover
    PdfReader = None

CFG = ROOT / "config/completude.json"
ESTADO = ROOT / "estado/completude.json"
FAROL = ROOT / "dados/farol/editais"

_MODELO = re.compile(
    r"anexo|modelo|formul[aá]rio|requerimento|declara[çc][ãa]o|"
    r"plano\s+de\s+trabalho|ficha\s+de|minuta", re.I)
_EH_PDF = re.compile(r"\.pdf(\?|$)", re.I)
_NUM_EDITAL = re.compile(r"\b(?:edital|chamamento|chamada|sele[çc][ãa]o)\D{0,20}?"
                         r"(\d{1,4})\s*/\s*(20\d{2})", re.I)
_DATA_BR = re.compile(r"\b(\d{1,2})/(\d{1,2})/(20\d{2})\b")
_FIM_PISTA = re.compile(r"(?:at[eé]|encerra\w*|prazo\s+final|inscri[çc][õo]es[^.]{0,40}?at[eé])"
                        r"\D{0,30}(\d{1,2}/\d{1,2}/20\d{2})", re.I)
_INI_PISTA = re.compile(r"(?:a\s+partir\s+de|in[ií]cio\s+d?as?\s+inscri[çc][õo]es|abertura)"
                        r"\D{0,30}(\d{1,2}/\d{1,2}/20\d{2})", re.I)
_MENCIONA_ANEXO = re.compile(r"\banexos?\b|\bmodelos?\b|\bformul[aá]rios?\b", re.I)


# ---------------------------------------------------------------- utilidades
def _cfg() -> dict:
    if CFG.exists():
        return load_json(CFG)
    return {"janela_dias": 30, "max_campanhas_por_execucao": 40,
            "max_pdf_mb": 10, "max_total_mb_por_edital": 25,
            "timeout_segundos": 25}


def _estado() -> dict:
    if ESTADO.exists():
        return load_json(ESTADO)
    return {"versao": 1, "campanhas": {}}


def _iso(d: str) -> str | None:
    m = _DATA_BR.fullmatch(d.strip()) if d else None
    if not m:
        return None
    dd, mm, aa = m.groups()
    try:
        return date(int(aa), int(mm), int(dd)).isoformat()
    except ValueError:
        return None


class _Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href = None
        self._txt: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._txt = []

    def handle_data(self, data):
        if self._href is not None:
            self._txt.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            self.links.append((self._href, " ".join(self._txt).strip()))
            self._href = None


def _abrir(url: str, timeout: int, max_bytes: int) -> tuple[bytes, str, str]:
    """Ponto único de rede (injetável nos testes). Devolve (dados, url_final,
    content-type). HTTPS público é exigido para http(s); file:// é aceito
    apenas em testes."""
    from urllib.request import Request, urlopen
    if url.startswith("file://"):
        with urlopen(url) as r:  # nosec — usado só em teste local
            return r.read(max_bytes + 1), url, r.headers.get_content_type()
    from .nucleo import validate_public_https
    validate_public_https(url, urlsplit(url).hostname)
    req = Request(url, headers={"User-Agent": "Eldorado-OSC/1.0 completude"})
    with urlopen(req, timeout=timeout) as r:
        dados = r.read(max_bytes + 1)
        return dados, r.geturl(), r.headers.get_content_type()


def _texto_pdf(dados: bytes) -> tuple[str | None, bool]:
    """(texto, tem_formulario). Nunca inventa: sem pypdf devolve (None, False)."""
    if PdfReader is None:
        return None, False
    import io
    try:
        leitor = PdfReader(io.BytesIO(dados))
        texto = "\n".join((p.extract_text() or "") for p in leitor.pages)
        form = bool(leitor.get_fields())
        return (texto.strip() or None), form
    except Exception:
        return None, False


# ------------------------------------------------------------------ campanha
def chave_do_edital(item: dict) -> tuple[str, str]:
    """(chave, ano) — a chave agrupa o MESMO edital entre anos; repetições do
    edital viram subpastas por ano, como determinado pelo titular."""
    titulo = item.get("titulo") or ""
    m = _NUM_EDITAL.search(titulo)
    ano = (m.group(2) if m else None) or str(item.get("ano_referencia")
            or str(item.get("coletado_em") or "")[:4] or date.today().year)
    base = f'{item.get("fonte_id","fonte")}-edital-{m.group(1)}' if m \
        else f'{item.get("fonte_id","fonte")}-{slug(titulo)[:40]}'
    return slug(base), ano


def _fontes_oficiais(item: dict) -> list[str]:
    """Sites oficiais onde o edital integral pode estar publicado, conforme o
    nível federativo (secretaria/prefeitura/governo/ministério/empresa)."""
    cfg = load_json(ROOT / "config/fontes.json")
    terr = str(item.get("territorio") or "")
    uf = terr.split("/")[0]
    urls = []
    for f in cfg.get("fontes", []):
        if not f.get("ativa"):
            continue
        ft = str(f.get("territorio") or "")
        if ft in (terr, uf, "BR"):
            urls.append(f["url"])
    origem = item.get("url")
    if origem:
        urls.insert(0, origem)  # 1ª verificação: a própria fonte identificada
    vistos, unicos = set(), []
    for u in urls:
        if u not in vistos:
            vistos.add(u)
            unicos.append(u)
    return unicos[:6]


def _casa_titulo(item: dict, rotulo: str) -> bool:
    m = _NUM_EDITAL.search(item.get("titulo") or "")
    if m and re.search(rf"{m.group(1)}\s*/\s*{m.group(2)}", rotulo):
        return True
    tokens = [t for t in re.findall(r"[a-zà-ú]{5,}", (item.get("titulo") or "").lower())
              if t not in ("edital", "chamamento", "publica", "publico")][:4]
    r = rotulo.lower()
    return bool(tokens) and sum(t in r for t in tokens) >= max(2, len(tokens) - 1)


def _tentar(item: dict, camp: dict, cfg: dict) -> dict:
    """Uma tentativa diária: varre as fontes oficiais atrás do edital integral
    e dos documentos-modelo. Registra tudo; só promove com completude."""
    hoje = date.today().isoformat()
    tentativa = {"data": hoje, "urls": [], "achados": [], "falhas": []}
    max_pdf = cfg["max_pdf_mb"] * 1_048_576
    achou_texto = camp.get("texto_ok", False)
    pdfs_modelo: list[tuple[str, bytes, str]] = []
    edital_pdf: tuple[str, bytes, bool] | None = None
    texto_edital = camp.get("_texto")

    for base in _fontes_oficiais(item):
        tentativa["urls"].append(base)
        try:
            dados, final, ctype = _abrir(base, cfg["timeout_segundos"], max_pdf)
        except Exception as exc:  # rede/bloqueio: registra e segue
            tentativa["falhas"].append({"url": base, "erro": type(exc).__name__})
            continue
        if "pdf" in (ctype or ""):
            texto, form = _texto_pdf(dados)
            if texto and _casa_titulo(item, texto[:2000]):
                texto_edital, achou_texto = texto, True
                edital_pdf = (final, dados, form)
                tentativa["achados"].append({"tipo": "edital_pdf", "url": final})
            continue
        html = dados.decode("utf-8", "replace")
        parser = _Links()
        parser.feed(html)
        for href, rotulo in parser.links:
            url = canonical_url(urljoin(final, href))
            if not _EH_PDF.search(url):
                continue
            eh_modelo = bool(_MODELO.search(rotulo) or _MODELO.search(url))
            eh_edital = _casa_titulo(item, rotulo) or "edital" in rotulo.lower()
            if not (eh_modelo or eh_edital):
                continue
            try:
                pdf, pdf_final, _ = _abrir(url, cfg["timeout_segundos"], max_pdf)
            except Exception as exc:
                tentativa["falhas"].append({"url": url, "erro": type(exc).__name__})
                continue
            if len(pdf) > max_pdf:
                tentativa["falhas"].append({"url": url, "erro": "acima_do_limite"})
                continue
            texto, form = _texto_pdf(pdf)
            if eh_modelo:
                pdfs_modelo.append((rotulo or Path(urlsplit(pdf_final).path).name,
                                    pdf, pdf_final))
                tentativa["achados"].append({"tipo": "modelo", "url": pdf_final})
            elif eh_edital and texto:
                texto_edital, achou_texto = texto, True
                edital_pdf = (pdf_final, pdf, form)
                tentativa["achados"].append({"tipo": "edital_pdf", "url": pdf_final})

    # ---- avaliação de completude (padrão de qualidade "Eldorado encontrado")
    texto_ref = " ".join(x for x in (texto_edital, item.get("evidencia"),
                                     item.get("titulo")) if x)
    fim = camp.get("fim") or item.get("prazo_texto")
    ini = camp.get("inicio")
    if texto_edital:
        m = _FIM_PISTA.search(texto_edital)
        if m:
            fim = fim or m.group(1)
        m = _INI_PISTA.search(texto_edital)
        if m:
            ini = ini or m.group(1)
    fim_iso, ini_iso = _iso(fim or ""), _iso(ini or "")
    menciona_anexo = bool(_MENCIONA_ANEXO.search(texto_edital or ""))
    anexos_ok = bool(pdfs_modelo) or camp.get("anexos_ok") \
        or (achou_texto and not menciona_anexo)   # sem menção = sem anexos declarados
    objeto_ok = bool(item.get("caracterizacao", {}).get("objeto")
                     or re.search(r"objeto", texto_ref, re.I))

    completo = bool(achou_texto and fim_iso and anexos_ok and objeto_ok)
    pend = []
    if not achou_texto:
        pend.append("texto integral do edital não obtido"
                    + ("" if PdfReader else " (extrator PDF ausente no ambiente)"))
    if not fim_iso:
        pend.append("prazo final de inscrição não declarado")
    if not anexos_ok:
        pend.append("edital menciona anexos/modelos ainda não localizados")
    if not objeto_ok:
        pend.append("objeto não identificado")

    camp.update({"texto_ok": achou_texto, "anexos_ok": anexos_ok,
                 "fim": fim, "inicio": ini, "fim_iso": fim_iso, "inicio_iso": ini_iso,
                 "pendencias": pend, "_texto": texto_edital})
    camp.setdefault("tentativas", []).append(
        {k: v for k, v in tentativa.items() if v})

    if completo:
        _materializar(item, camp, texto_edital, edital_pdf, pdfs_modelo)
        camp["status"] = "completo"
        camp["completo_em"] = now_iso()
    return camp


def _materializar(item: dict, camp: dict, texto: str,
                  edital_pdf: tuple | None,
                  modelos: list[tuple[str, bytes, str]]) -> None:
    """Grava a pasta do edital no Farol: subpasta por ANO; texto convertido;
    APENAS PDFs que sejam anexos-modelo; o PDF do edital só permanece quando
    ele próprio é formulário ou quando não há modelos."""
    chave, ano = chave_do_edital(item)
    pasta = FAROL / chave / ano
    (pasta / "anexos").mkdir(parents=True, exist_ok=True)
    (pasta / "edital.txt").write_text(texto or "", encoding="utf-8")
    anexos_meta = []
    for rotulo, pdf, url in modelos:
        nome = slug(rotulo)[:60] or "modelo"
        destino = pasta / "anexos" / f"{nome}.pdf"
        destino.write_bytes(pdf)
        anexos_meta.append({"nome": rotulo, "arquivo": destino.name,
                            "url": url, "sha256": sha256(pdf)})
    manter_pdf = edital_pdf and (edital_pdf[2] or not modelos)
    if manter_pdf:
        (pasta / "edital.pdf").write_bytes(edital_pdf[1])
    elif (pasta / "edital.pdf").exists() and modelos:
        (pasta / "edital.pdf").unlink()          # regra: com modelos, só o txt
    write_json(pasta / "dados.json", {
        "id": item["id"], "chave": chave, "ano": ano,
        "titulo": item.get("titulo"), "fonte_id": item.get("fonte_id"),
        "fonte_nome": item.get("fonte_nome"), "territorio": item.get("territorio"),
        "url_identificacao": item.get("url"),
        "url_edital": edital_pdf[0] if edital_pdf else None,
        "inicio": camp.get("inicio_iso"), "fim": camp.get("fim_iso"),
        "verificacao": {"fonte": True, "conteudo": True,
                        "criterio": "texto integral + prazo final + anexos-modelo"},
        "anexos_modelo": anexos_meta,
        "edital_pdf_mantido": bool(manter_pdf),
        "hash_texto": sha256((texto or "").encode()),
        "campanha": {"criada_em": camp.get("criado_em"),
                     "tentativas": len(camp.get("tentativas", [])),
                     "completo_em": now_iso()},
    })


def run(limite: int | None = None, hoje: date | None = None) -> dict:
    """Execução diária: abre campanhas para novas identificações de diário e
    dá continuidade às pendentes, até completar ou expirar (30 dias)."""
    cfg = _cfg()
    hoje = hoje or date.today()
    est = _estado()
    campanhas = est["campanhas"]
    itens = {i["id"]: i for i in carregar_oportunidades().values()}

    # abre campanha para toda identificação ainda não completa
    for oid, item in itens.items():
        if oid in campanhas:
            continue
        campanhas[oid] = {"criado_em": hoje.isoformat(), "status": "monitorando",
                          "fonte_id": item.get("fonte_id"), "tentativas": []}

    fila = [oid for oid, c in campanhas.items()
            if c["status"] == "monitorando" and oid in itens]
    # prioriza: com prazo declarado primeiro; depois mais antigos
    fila.sort(key=lambda oid: (0 if itens[oid].get("prazo_texto") else 1,
                               campanhas[oid]["criado_em"]))
    limite = limite or cfg["max_campanhas_por_execucao"]
    resumo = {"executado_em": now_iso(), "tentadas": 0, "completas": 0,
              "expiradas": 0, "monitorando": 0}
    for oid in fila[:limite]:
        camp, item = campanhas[oid], itens[oid]
        idade = (hoje - date.fromisoformat(camp["criado_em"])).days
        if idade > cfg["janela_dias"]:
            camp["status"] = "expirado"
            camp["expirado_em"] = now_iso()
            camp["pendencias"] = (camp.get("pendencias") or []) + [
                f"janela de {cfg['janela_dias']} dias esgotada sem completude — "
                "requer verificação humana"]
            resumo["expiradas"] += 1
            continue
        _tentar(item, camp, cfg)
        resumo["tentadas"] += 1
        if camp["status"] == "completo":
            resumo["completas"] += 1
    for c in campanhas.values():
        c.pop("_texto", None)
    resumo["monitorando"] = sum(1 for c in campanhas.values()
                                if c["status"] == "monitorando")
    write_json(ESTADO, est)
    return resumo


def completos() -> dict:
    """{id_da_oportunidade: dados.json} de todos os editais materializados."""
    saida = {}
    if not FAROL.exists():
        return saida
    for dj in FAROL.glob("*/*/dados.json"):
        try:
            d = load_json(dj)
            saida[d["id"]] = d
        except Exception:
            continue
    return saida


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
