"""EXPURGO DO QUE NÃO É OPORTUNIDADE (titular, 15/10/2026).

"Não quero dado inútil; oportunidade que não se utiliza é dado inútil. Uma vez eliminada e descartada, deve ter removido
o seu registro por completo." Começa pelo PNCP, de onde vem a maior parte do ruído.

1. CLASSIFICA cada compra do PNCP citada em QUALQUER arquivo de dados: é INVÁLIDA só com motivo explícito do portão de
   captação (território, licitação/compra, contrato de serviço, contratação de vagas, PNAE, pessoa física, ILPI e
   acolhimento fora de Goiás e das capitais). Dúvida (título curto, sem sinal claro) NÃO é apagada.
2. REMOVE um registro (elemento de lista, entrada de dicionário, linha de JSONL, linha do banco) só quando TODAS as
   compras do PNCP que ele cita são inválidas — um livro com edições válidas e inválidas não se perde.
3. Alcança: dados/, estado/, docs/dados/, biblioteca_alexandria/ (JSON e JSONL), o banco dados/eldorado.db, o catálogo
   de livros e as PASTAS dos livros eliminados, e o registro de releitura (estado/achados_vistos.json).
4. Simulação primeiro (--simular); a execução grava estado/expurgo/AAAA-MM-DD.json com o que saiu de cada lugar.
"""
from __future__ import annotations

import json
import re
import shutil
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from .nucleo import ROOT

VERSAO = 4          # 16/10/2026: v4 = histórico só ligado a livro de oportunidade; achado só trecho e links; v3 = o acervo de histórico também passa pelos portões; v2: regra territorial em todo o sistema — mudou a regra, o expurgo roda de novo no mesmo dia
PNCP = re.compile(r"pncp\.gov\.br/(?:app/editais|pncp-api/v1/orgaos|api/(?:pncp|consulta)/v1/orgaos)/(\d{14})/(?:compras/)?(\d{4})/(\d+)", re.I)
AREAS = ["dados", "estado", "docs/dados", "biblioteca_alexandria"]
# 16/10/2026 (titular): o Eldorado e o Farol são as duas metades do sistema; a regra dos livros e os expurgos valem SÓ
# para o Eldorado — os dados da associação e do Farol nunca são tocados
FAROL = re.compile(r"(^|/)(dados/farol|dados/associacoes|biblioteca_alexandria/associacoes)(/|$)|preparacao_farol\.json$")
NUNCA = re.compile(r"(^|/)(config|tests|src|scripts)/|estado/expurgo/|estado/pncp/estudo_mes\.json|/arquivo_frio/")
TITULO = ("titulo", "nome", "programa", "nome_classificado", "objeto")


URL = re.compile(r"https?://[^\s\"'<>\\]+")
VEREDITO: dict = {}          # chave → True (inválida) / False (válida); só chaves JULGADAS contam


def _url_chave(u: str) -> str:
    from .vistos import chave
    return chave({"url": u.rstrip(".,;)")})


def _chaves(txt: str) -> set:
    ks = {f"{a}/{b}/{int(c)}" for a, b, c in PNCP.findall(txt)}
    if VEREDITO:
        for u in URL.findall(txt):
            if "pncp.gov.br" not in u:
                k = _url_chave(u)
                if k in VEREDITO:
                    ks.add(k)
    return ks


def _arquivos():
    for a in AREAS:
        for p in (ROOT / a).rglob("*"):
            rel = str(p.relative_to(ROOT))
            if p.is_file() and p.suffix in (".json", ".jsonl", ".txt") and not NUNCA.search(rel) and not FAROL.search(rel) \
                    and p.stat().st_size < 120_000_000:
                yield p


def _carregar(p: Path):
    txt = p.read_text(encoding="utf-8", errors="replace")
    if p.suffix == ".jsonl":
        linhas = []
        for l in txt.splitlines():
            try:
                linhas.append(json.loads(l))
            except ValueError:
                linhas.append(l)
        return "jsonl", linhas
    try:
        return "json", json.loads(txt)
    except ValueError:
        return None, None


# ── 1. CLASSIFICAR ─────────────────────────────────────────────────────────────────────────────────────────────────
def _julgar_territorio(obj, juizo: dict):
    """16/10/2026 (titular): em outros estados só ESTADUAIS e CAPITAIS — julga cada registro com endereço."""
    if isinstance(obj, dict):
        u = next((obj.get(f) for f in ("url", "pagina", "link_oficial", "site_oficial") if isinstance(obj.get(f), str) and obj[f].startswith("http")), None)
        t = next((obj.get(f) for f in TITULO if isinstance(obj.get(f), str)), None)
        if u and t and "pncp.gov.br" not in u:
            from .repositorio_unico import municipal_fora_de_goias
            try:
                ruim = bool(municipal_fora_de_goias({"titulo": t, "orgao": obj.get("orgao"), "url": u, "uf": obj.get("uf"),
                                                      "nivel": obj.get("nivel"), "link_oficial": obj.get("link_oficial")}))
            except Exception:  # noqa: BLE001
                ruim = False
            k = _url_chave(u); juizo.setdefault(k, set()).add(ruim)
        for v in obj.values():
            if isinstance(v, (dict, list)):
                _julgar_territorio(v, juizo)
    elif isinstance(obj, list):
        for v in obj:
            _julgar_territorio(v, juizo)


def _coletar_registros(obj, out: dict):
    """Para cada chave do PNCP, o melhor título/órgão/UF que algum registro traz."""
    if isinstance(obj, dict):
        ks = _chaves(json.dumps(obj, ensure_ascii=False)) if any(isinstance(v, str) and "pncp.gov.br" in v for v in obj.values()) else set()
        if len(ks) == 1:
            k = next(iter(ks)); r = out.setdefault(k, {})
            for f in TITULO:
                if isinstance(obj.get(f), str) and len(obj[f]) > len(r.get("titulo") or ""):
                    r["titulo"] = obj[f]
            for f in ("orgao", "uf", "municipio", "esfera", "modalidade"):
                if obj.get(f) and not r.get(f):
                    r[f] = obj[f]
        for v in obj.values():
            if isinstance(v, (dict, list)):
                _coletar_registros(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _coletar_registros(v, out)


def classificar(info: dict) -> tuple[bool, str | None]:
    """(inválida?, motivo). Inválida SÓ com motivo explícito do portão de captação."""
    from .pncp_osc import _N, portao_associacao
    from .repositorio_unico import uf_por_municipio
    t = str(info.get("titulo") or "")
    orgao = str(info.get("orgao") or t.partition(" — ")[0])
    uf = str(info.get("uf") or "")[:2].upper() if len(str(info.get("uf") or "")) >= 2 and str(info.get("uf")).upper() not in ("BR", "NONE") else None
    uf = uf or uf_por_municipio(orgao)
    mo = re.search(r"(?:MUNICIPIO|PREFEITURA MUNICIPAL|CAMARA MUNICIPAL|FUNDO MUNICIPAL DE [A-Z ]{3,40}?) DE ([A-Z ]{3,40})", _N(orgao))
    esfera = str(info.get("esfera") or "")[:1].upper() or None
    if esfera not in ("M", "E", "F", "D"):
        esfera = "M" if re.search(r"MUNICIP|PREFEIT|CAMARA MUNICIPAL|CONSORCIO", _N(orgao)) else None
    m = {"titulo": t, "orgao": orgao, "uf": uf, "municipio": info.get("municipio") or (mo.group(1).title() if mo else None),
         "esfera": esfera, "modalidade": info.get("modalidade")}
    motivo = portao_associacao(m, _N(f"{t} {info.get('objeto') or ''}"))
    return (bool(motivo), motivo)


# ── 2. REMOVER ─────────────────────────────────────────────────────────────────────────────────────────────────────
def _invalido(obj, inval: set) -> bool:
    ks = _chaves(json.dumps(obj, ensure_ascii=False) if not isinstance(obj, str) else obj)
    julgadas = {k for k in ks if k in inval or VEREDITO.get(k) is False or "/" in k and not k.startswith(("url:", "txt:"))}
    return bool(julgadas) and julgadas <= inval


def _colunar(obj: dict, inval: set, cont: Counter) -> dict:
    """Formato colunar (schema + linhas, com ou sem dicionários de valores): remove a LINHA inteira, decodificada;
    os dicionários de valores ficam intactos (as posições que as outras linhas usam não mudam)."""
    sc = obj.get("schema") or obj.get("campos") or []
    dic = obj.get("dicionarios") or obj.get("dicionario") or obj.get("dic") or {}
    def texto(l):
        partes = []
        for i, x in enumerate(l if isinstance(l, list) else []):
            c = sc[i] if i < len(sc) else None
            if c in dic and isinstance(x, int) and isinstance(dic[c], list) and x < len(dic[c]):
                x = dic[c][x]
            partes.append(json.dumps(x, ensure_ascii=False) if not isinstance(x, str) else x)
        return " ".join(partes)
    novas = []
    for l in obj.get("linhas") or []:
        ks = _chaves(texto(l))
        if ks and ks <= inval:
            cont["removidos"] += 1; continue
        novas.append(l)
    return {**obj, "linhas": novas}


def _filtrar(obj, inval: set, cont: Counter):
    if isinstance(obj, dict) and isinstance(obj.get("linhas"), list) and isinstance(obj.get("schema") or obj.get("campos"), list):
        return _colunar(obj, inval, cont)
    if isinstance(obj, list):
        registros = bool(obj) and all(isinstance(v, dict) for v in obj)      # só lista de REGISTROS (nunca uma linha colunar)
        novo = []
        for v in obj:
            if registros and _invalido(v, inval):
                cont["removidos"] += 1; continue
            novo.append(_filtrar(v, inval, cont) if isinstance(v, (dict, list)) and not isinstance(v, list) or registros else v)
        return novo
    if isinstance(obj, dict):
        novo = {}
        for k, v in obj.items():
            if isinstance(v, dict) and _invalido(v, inval):
                cont["removidos"] += 1; continue
            novo[k] = _filtrar(v, inval, cont)
        return novo
    return obj


def executar(simular: bool = True) -> dict:
    VEREDITO.clear()
    regs: dict = {}
    arqs = list(_arquivos())
    cache = {}
    for p in arqs:
        tipo, obj = _carregar(p)
        if tipo:
            cache[p] = (tipo, obj); _coletar_registros(obj, regs)
    # chaves citadas só em texto (sem registro com título): ficam como dúvida (não apagadas)
    inval, motivos = set(), Counter()
    try:                                                   # o que o repositório DESCARTOU também sai por completo
        from . import repositorio_unico as R
        R.construir(gravar=False)
        for d in R.DESCARTADAS:
            for k in _chaves(f"{d.get('url')} {d.get('link_oficial')}"):
                inval.add(k); motivos["descartada no repositório"] += 1
    except Exception:  # noqa: BLE001
        pass
    exemplos = defaultdict(list)
    juizo: dict = {}
    for p_, (tipo_, obj_) in cache.items():
        _julgar_territorio(obj_, juizo)
    VEREDITO.clear()
    for k, vs in juizo.items():
        VEREDITO[k] = (vs == {True})                  # inválida só se TODO registro que cita o endereço é inválido
        if VEREDITO[k]:
            inval.add(k); motivos["município de outro estado (não capital)"] += 1
    for k, info in regs.items():
        if k in inval:
            continue
        ruim, mot = classificar(info)
        if ruim:
            inval.add(k); g = mot.split(" (")[0].split(" —")[0][:60]; motivos[g] += 1
            if len(exemplos[g]) < 5:
                exemplos[g].append(str(info.get("titulo"))[:120])
    por_arquivo, livros_removidos = {}, []
    for p, (tipo, obj) in cache.items():
        cont = Counter()
        if tipo == "jsonl":
            novo = [l for l in obj if not (isinstance(l, dict) and _invalido(l, inval) and (cont.update(removidos=1) or True))]
        else:
            novo = _filtrar(obj, inval, cont)
        if cont["removidos"]:
            rel = str(p.relative_to(ROOT)); por_arquivo[rel] = cont["removidos"]
            if rel.endswith("fontes/motores.json"):
                antes = {l.get("id") for l in (obj.get("motores") or [])}
                depois = {l.get("id") for l in (novo.get("motores") or [])}
                livros_removidos = sorted(antes - depois)
            if not simular:
                if tipo == "jsonl":
                    p.write_text("\n".join(json.dumps(l, ensure_ascii=False) if not isinstance(l, str) else l for l in novo) + "\n", encoding="utf-8")
                else:
                    ini = p.read_text(encoding="utf-8", errors="replace")[:300]
                    compacto = "\n" not in ini.strip()[:200]
                    p.write_text(json.dumps(novo, ensure_ascii=False, separators=(",", ":")) if compacto else
                                 json.dumps(novo, ensure_ascii=False, indent=2 if ini.startswith(("{\n  ", "[\n  ")) else 1), encoding="utf-8")
    # pastas dos livros eliminados (biblioteca_alexandria/livros/anexos/<pasta>) que só citam compras inválidas
    pastas = []
    base = ROOT / "biblioteca_alexandria/livros/anexos"
    for d in (base.iterdir() if base.exists() else []):
        if d.is_dir():
            txt = " ".join(f.read_text(encoding="utf-8", errors="replace") for f in d.rglob("*") if f.is_file() and f.stat().st_size < 5_000_000)
            ks = _chaves(txt)
            if ks and ks <= inval:
                pastas.append(str(d.relative_to(ROOT)))
                if not simular:
                    shutil.rmtree(d)
    # banco
    banco = {}
    db = ROOT / "dados/eldorado.db"
    if db.exists() and inval:
        con = sqlite3.connect(db)
        for (tab,) in con.execute("select name from sqlite_master where type='table'"):
            cols = [r[1] for r in con.execute(f"pragma table_info('{tab}')")]
            n = 0
            for (rowid, *vals) in con.execute(f"select rowid, * from '{tab}'"):
                txt = " ".join(str(v) for v in vals if isinstance(v, str))
                ks = _chaves(txt)
                if ks and ks <= inval:
                    n += 1
                    if not simular:
                        con.execute(f"delete from '{tab}' where rowid=?", (rowid,))
            if n:
                banco[tab] = n
        if not simular:
            con.commit(); con.execute("vacuum")
        con.close()
    # registro de releitura
    vist = ROOT / "estado/achados_vistos.json"
    nv = 0
    if vist.exists():
        V = json.loads(vist.read_text(encoding="utf-8"))
        for m_ in V.values():
            for k in [k for k in m_ if (k.startswith("pncp:") and k[5:] in inval) or k in inval]:
                nv += 1
                if not simular:
                    del m_[k]
        if not simular:
            vist.write_text(json.dumps(V, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    res = {"em": date.today().isoformat(), "versao": VERSAO, "simulacao": simular, "compras_pncp_citadas": len(regs), "invalidas": len(inval),
           "motivos": dict(motivos.most_common()), "exemplos": dict(exemplos), "registros_removidos_por_arquivo": dict(sorted(por_arquivo.items(), key=lambda x: -x[1])),
           "total_registros_removidos": sum(por_arquivo.values()), "livros_removidos": livros_removidos, "pastas_de_livros_removidas": pastas,
           "linhas_do_banco_removidas": banco, "registro_de_releitura": nv}
    if not simular:
        d = ROOT / "estado/expurgo"; d.mkdir(parents=True, exist_ok=True)
        (d / f"{res['em']}.json").write_text(json.dumps({**res, "chaves_invalidas": sorted(inval)}, ensure_ascii=False, indent=1), encoding="utf-8")
    return res


if __name__ == "__main__":
    r = executar(simular="--executar" not in sys.argv)
    print(json.dumps({k: (v if k not in ("exemplos",) else v) for k, v in r.items() if k not in ("registros_removidos_por_arquivo",)}, ensure_ascii=False, indent=1)[:5000])
    print("arquivos:", json.dumps(dict(list(r["registros_removidos_por_arquivo"].items())[:40]), ensure_ascii=False, indent=0))
