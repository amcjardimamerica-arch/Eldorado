"""O LIVRO EM ARQUIVO PRÓPRIO E A ABSORÇÃO DOS BANCOS PARALELOS (titular, 16/10/2026).

REGRA MÁXIMA: o único banco de dados do Eldorado são os LIVROS. Todo dado de oportunidade vive no livro dela.
Oportunidade aberta com livro acrescenta as informações do edital atual às anteriores (o edital atual sempre vale);
oportunidade sem livro ganha um livro com todas as informações levantadas. É proibido criar dados fora dos livros.

  biblioteca_alexandria/livros/<livro>.json   o CONTEÚDO do livro: o que cada etapa e ferramenta levantou sobre a
                                              oportunidade, por origem ("acervo"), com a data em que entrou
  biblioteca_alexandria/fontes/motores.json   a CAPA dos livros (identidade e ficha) — índice do catálogo
  biblioteca_alexandria/livros/_origens.json  controle: de que arquivo antigo veio cada entrada e em que formato,
                                              para os leitores remontarem a mesma estrutura a partir dos livros

ABSORÇÃO (absorver): cada ENTRADA de um arquivo paralelo (chave de dicionário, item de lista ou linha de JSONL) é ligada
a um livro pela chave, pelo id, pelo link ou pelo título+órgão; ligada → vai ao arquivo do livro; não ligada → se for
oportunidade com prazo vigente que passa nos portões, ganha livro; senão é descartada. Depois o arquivo antigo é APAGADO.
LEITURA (carregar): o leitor pede o caminho antigo e recebe a mesma estrutura, montada a partir dos livros.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

from .nucleo import ROOT
from .vistos import chave

PASTA = ROOT / "biblioteca_alexandria/livros"
ORIGENS = PASTA / "_origens.json"
CAT = ROOT / "biblioteca_alexandria/fontes/motores.json"
URL = re.compile(r"https?://[^\s\"'<>]+")


def _j(p: Path, padrao):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao


def _agora() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _rel(p) -> str:
    p = Path(p)
    try:
        return str(p.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(p)


# 16/10/2026 (titular): a regra dos livros vale SÓ para o Eldorado; os dados da associação e do Farol ficam fora
FAROL = re.compile(r"(^|/)(dados/farol|dados/associacoes|biblioteca_alexandria/associacoes)(/|$)|preparacao_farol\.json$")


# ── livro em arquivo ──────────────────────────────────────────────────────────────────────────────────────────────
def ler(lid: str) -> dict:
    return _j(PASTA / f"{lid}.json", {"id": lid, "acervo": {}})


def gravar(lid: str, d: dict) -> None:
    PASTA.mkdir(parents=True, exist_ok=True)
    (PASTA / f"{lid}.json").write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


# ── ligação ───────────────────────────────────────────────────────────────────────────────────────────────────────
_IDX_MEMO: dict = {}


def indice() -> dict:
    """chave/id/link/título → livro. 16/10: em MEMÓRIA enquanto o catálogo não muda (gravar centenas de edições não
    reconstrói o índice a cada uma)."""
    marca = CAT.stat().st_mtime_ns if CAT.exists() else 0
    if _IDX_MEMO.get("marca") == marca and _IDX_MEMO.get("idx") is not None:
        return dict(_IDX_MEMO["idx"])
    idx = _indice()
    _IDX_MEMO.update({"marca": marca, "idx": idx})
    return dict(idx)


def _indice() -> dict:
    from .banco_livros import _chaves_do_livro
    L = (_j(CAT, {}) or {}).get("motores") or []
    idx = {}
    for lv in L:
        lid = lv.get("id"); idx[lid] = lid
        for k in _chaves_do_livro(lv):
            idx.setdefault(k, lid)
        op = lv.get("oportunidade") if isinstance(lv.get("oportunidade"), dict) else {}
        if op.get("id_repositorio"):
            idx[op["id_repositorio"]] = lid
        for sec in ("coleta", "brutos"):
            for i, b in (lv.get(sec) or {}).items():
                idx.setdefault(str(i).split(":")[-1], lid)
                if isinstance(b, dict) and b.get("url"):
                    idx.setdefault(chave(b), lid)
        for e in lv.get("historico") or []:
            if isinstance(e, dict):
                if e.get("id"):
                    idx.setdefault(e["id"], lid)
                if isinstance(e.get("pagina_oficial"), str):
                    idx.setdefault(chave({"url": e["pagina_oficial"]}), lid)
        t = f"{lv.get('programa') or ''}|{lv.get('orgao') or ''}".lower().strip("|")
        if len(t) > 12:
            idx.setdefault("t:" + t, lid)
    return idx


def ligar(k, v, idx: dict) -> str | None:
    cands = []
    if isinstance(k, str):
        cands.append(k)
        if re.match(r"^(?:estrela|livro|pncp|op|url|txt):", k):     # 16/10: chave com prefixo ('estrela:<id>', 'livro:<id>')
            cands.append(k.split(":", 1)[1])
        if k.startswith("http"):
            cands.append(chave({"url": k}))
    if isinstance(v, dict):
        for f in ("livro", "livro_id", "opressor", "oportunidade_id", "id_repositorio", "id"):
            if isinstance(v.get(f), str):
                cands.append(v[f])
        for f in ("url", "link_oficial", "pagina", "pagina_oficial", "site_oficial", "fonte"):
            if isinstance(v.get(f), str) and v[f].startswith("http"):
                cands.append(chave({"url": v[f]}))
        t = f"{v.get('programa') or v.get('titulo') or ''}|{v.get('orgao') or ''}".lower().strip("|")
        if len(t) > 12:
            cands.append("t:" + t)
    for c in cands:
        if c in idx:
            return idx[c]
    if isinstance(v, (dict, list)):                       # último recurso: um link que já pertence a um livro
        for u in URL.findall(json.dumps(v, ensure_ascii=False)[:20000]):
            c = chave({"url": u.rstrip(".,;)")})
            if c in idx:
                return idx[c]
    return None


def _candidata(v) -> bool:
    """16/10/2026 (titular): entrada de DESCOBERTA (agregadores, Piloto) ganha livro se passar no portão de oportunidade,
    com ou sem prazo — a candidata sem prazo é justamente a 'possível' que o sistema existe para verificar. Com prazo
    já encerrado, não ganha livro."""
    if not isinstance(v, dict) or not (v.get("titulo") and (v.get("url") or v.get("link_oficial"))):
        return False
    from .porta_oportunidade import motivo_para_nao_guardar
    return motivo_para_nao_guardar(v) is None


def _oportunidade_vigente(v) -> bool:
    if not isinstance(v, dict) or not (v.get("titulo") and (v.get("url") or v.get("link_oficial"))):
        return False
    fim = str(v.get("fim") or "")[:10]
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fim) or fim < date.today().isoformat():
        return False
    from .porta_oportunidade import motivo_para_nao_guardar
    return motivo_para_nao_guardar(v) is None


# ── absorção ──────────────────────────────────────────────────────────────────────────────────────────────────────
REG = ("id", "url", "titulo", "livro", "pagina", "link_oficial", "pagina_oficial", "programa", "opressor", "oportunidade_id")


def _eh_registro(v) -> bool:
    return isinstance(v, dict) and any(k in v for k in REG)


_IDX_ATUAL: dict = {}
DESCARTES: list = []                                     # (arquivo, caminho, chave, registro) descartados na última absorção


def _eh_conteiner(v) -> bool:
    """Lista de registros, ou dicionário cujas chaves são links/ids e os valores são dicionários."""
    if isinstance(v, list) and v:
        return sum(1 for x in v if _eh_registro(x)) >= max(1, len(v) // 2)
    if isinstance(v, dict) and len(v) >= 1:
        ks = list(v)
        chaves_id = sum(1 for k in ks if isinstance(k, str) and (k.startswith("http") or re.fullmatch(r"[\w.:-]{6,80}", k) and not k.islower()
                                                              or re.fullmatch(r"(?:op|cat|agr|lv|estrela|livro)[-:][\w-]+|[0-9a-f]{12,40}", str(k))))
        dicts = sum(1 for x in v.values() if isinstance(x, (dict, list)))
        # 16/10: a chave É um livro (ou oportunidade/link conhecido)? — 'captacao-118' não tem formato de id, mas é livro
        conhecidas = sum(1 for k in ks if isinstance(k, str) and (k in _IDX_ATUAL or (k.startswith("http") and chave({"url": k}) in _IDX_ATUAL)))
        return dicts >= max(1, len(v) // 2) and max(chaves_id, conhecidas) >= max(1, len(v) // 2)
    return False


def _expandir(o, caminho=""):
    """(esqueleto, contêineres) — cada contêiner: (caminho, forma, [(chave, registro)])."""
    if _eh_conteiner(o):
        forma = "list" if isinstance(o, list) else "dict"
        itens = [(str(i), x) for i, x in enumerate(o)] if forma == "list" else list(o.items())
        return {"__conteiner__": caminho}, [(caminho, forma, itens)]
    if isinstance(o, dict):
        esq, conts = {}, []
        for k, v in o.items():
            e, c = _expandir(v, f"{caminho}/{k}")
            esq[k] = e; conts += c
        return esq, conts
    return o, []


def absorver(caminhos: list, gravar_: bool = True, apagar: bool = True, controle_sem_livro: bool = False,
             descoberta: bool = False) -> dict:
    """controle_sem_livro=True: a parte que não é oportunidade (ex.: diagnóstico e aposta do voo do piloto) fica no
    CONTROLE (_origens), não nos livros nem descartada — é memória operacional, não dado de oportunidade."""
    from .banco_livros import _novo_livro
    idx = indice()
    _IDX_ATUAL.clear(); _IDX_ATUAL.update(idx)
    cat = _j(CAT, {"motores": []}); L = cat.setdefault("motores", [])
    origens = _j(ORIGENS, {})
    livros: dict = {}
    st = Counter(); criados = 0; arquivos = []

    def guardar(rel, cam, k, v):
        nonlocal criados
        lid = ligar(k, v, idx)
        if not lid and (_candidata(v) if descoberta else _oportunidade_vigente(v)):   # oportunidade sem livro: ganha livro
            lv = _novo_livro(v, chave(v)); L.append(lv); idx[chave(v)] = lv["id"]; lid = lv["id"]; criados += 1
        if not lid:
            st["descartadas (não ligam e não são oportunidade vigente)"] += 1
            DESCARTES.append((rel, cam, k, v)); return None
        d = livros.setdefault(lid, ler(lid))
        d.setdefault("acervo", {}).setdefault(rel, {})[f"{cam}|{k}"] = {"dado": v, "absorvido_em": _agora()}
        st["absorvidas"] += 1
        return lid
    for p in caminhos:
        p = Path(p)
        if not p.is_file() or p.suffix not in (".json", ".jsonl") or FAROL.search(_rel(p)):
            continue                                       # o Farol (e a associação) nunca é absorvido
        try:
            t = p.read_text(encoding="utf-8", errors="replace")
            obj = [json.loads(l) for l in t.splitlines() if l.strip()] if p.suffix == ".jsonl" else json.loads(t)
        except Exception:  # noqa: BLE001
            st["arquivo ilegível"] += 1; continue
        rel = _rel(p)
        # 16/10: arquivo que SE IDENTIFICA (edital_id ou o nome do arquivo) e liga a um livro vai INTEIRO para ele — sem
        # descer nas listas internas (ex.: as tentativas de extração de uma edição não são registros de oportunidade)
        _id_arq = (obj.get("edital_id") or obj.get("id")) if isinstance(obj, dict) else None
        _chv = str(_id_arq or p.stem)                     # só o IDENTIFICADOR (sem procurar links dentro do arquivo)
        _lid_arq = (idx.get(_chv) or idx.get(_chv.split(":", 1)[-1])) if isinstance(obj, dict) else None
        if _lid_arq:
            d = livros.setdefault(_lid_arq, ler(_lid_arq))
            d.setdefault("acervo", {}).setdefault(rel, {})["|_arquivo"] = {"dado": obj, "absorvido_em": _agora()}
            st["absorvidas"] += 1
            origens[rel] = {"jsonl": p.suffix == ".jsonl", "esqueleto": None, "conteineres": {}, "inteiro": [_lid_arq, "|_arquivo"],
                            "gravado_em": _agora()}
            arquivos.append(p); continue
        esq, conts = _expandir(obj)
        reg = {"jsonl": p.suffix == ".jsonl", "esqueleto": esq, "conteineres": {}}
        if not conts:                                     # o arquivo inteiro é o registro de uma oportunidade
            if isinstance(obj, dict) and not obj.get("id") and (obj.get("edital_id") or p.stem):
                obj_l = {**obj, "id": obj.get("edital_id") or p.stem}    # 16/10: o id está no NOME do arquivo / edital_id
                lid = ligar(obj_l["id"], obj_l, idx) or None
                if lid:
                    d = livros.setdefault(lid, ler(lid))
                    d.setdefault("acervo", {}).setdefault(rel, {})["|_arquivo"] = {"dado": obj, "absorvido_em": _agora()}
                    st["absorvidas"] += 1
                else:
                    lid = guardar(rel, "", "_arquivo", obj)
            else:
                lid = guardar(rel, "", "_arquivo", obj)
            reg["inteiro"] = [lid, "|_arquivo"] if lid else None
            if not lid and controle_sem_livro:
                reg["controle"] = obj; st["descartadas (não ligam e não são oportunidade vigente)"] -= 1
        for cam, forma, itens in conts:
            ent = []
            for k, v in itens:
                lid = guardar(rel, cam, k, v)
                if lid:
                    ent.append([lid, f"{cam}|{k}", k])
            reg["conteineres"][cam] = {"forma": forma, "entradas": ent}
        reg["gravado_em"] = _agora()
        origens[rel] = reg
        arquivos.append(p)
    if gravar_:
        for lid, d in livros.items():
            gravar(lid, d)
        PASTA.mkdir(parents=True, exist_ok=True)
        ORIGENS.write_text(json.dumps(origens, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        if criados:
            CAT.write_text(json.dumps(cat, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        if apagar:
            for p in arquivos:
                p.unlink()                                 # o banco paralelo é APAGADO (à força)
    return {"arquivos": len(arquivos), "livros_tocados": len(livros), "livros_criados": criados, **dict(st)}


# ── leitura pelos módulos antigos ─────────────────────────────────────────────────────────────────────────────────
_MEMO: dict = {}


def carregar(caminho, padrao=None):
    """O leitor pede o CAMINHO antigo e recebe a mesma estrutura, montada a partir dos livros. 16/10: a montagem fica em
    MEMÓRIA enquanto os livros não mudam (a fase de recálculo estourava o tempo relendo milhares de livros); cada
    chamada recebe uma CÓPIA, para um módulo não alterar o que o outro lê."""
    import copy
    rel = _rel(caminho)
    marca = ORIGENS.stat().st_mtime_ns if ORIGENS.exists() else 0
    if (rel, marca) in _MEMO:
        v = _MEMO[(rel, marca)]
        return copy.deepcopy(v) if v is not None else padrao
    v = _carregar(caminho, None)
    _MEMO.clear() if len(_MEMO) > 64 else None
    _MEMO[(rel, marca)] = v
    return copy.deepcopy(v) if v is not None else padrao


def _carregar(caminho, padrao=None):
    rel = _rel(caminho)
    o = (_j(ORIGENS, {}) or {}).get(rel)
    if not o:
        return padrao
    cache: dict = {}

    def valor(lid, chave_int):
        d = cache.setdefault(lid, ler(lid))
        x = ((d.get("acervo") or {}).get(rel) or {}).get(chave_int)
        return None if x is None else x["dado"]
    if o.get("inteiro"):
        return valor(*o["inteiro"])
    if "controle" in o and not o["conteineres"]:
        return o["controle"]
    if "inteiro" in o and not o["conteineres"]:
        return padrao

    def montar(e):
        if isinstance(e, dict) and set(e) == {"__conteiner__"}:
            c = o["conteineres"].get(e["__conteiner__"]) or {"forma": "list", "entradas": []}
            pares = [(k, valor(lid, ci)) for lid, ci, k in c["entradas"]]
            pares = [(k, v) for k, v in pares if v is not None]
            return {k: v for k, v in pares} if c["forma"] == "dict" else [v for _k, v in pares]
        if isinstance(e, dict):
            return {k: montar(v) for k, v in e.items()}
        return e
    return montar(o["esqueleto"])


def arquivos_de(pasta) -> list[str]:
    """Os 'arquivos' antigos de uma pasta (agora dentro dos livros), para quem fazia glob."""
    pre = _rel(pasta).rstrip("/") + "/"
    return sorted(k for k in (_j(ORIGENS, {}) or {}) if k.startswith(pre))


def guardar(caminho, obj, controle_sem_livro: bool = False) -> dict:
    """Quem gravava num arquivo passa a gravar NO LIVRO: a estrutura é absorvida na hora e o arquivo não fica.
    A versão anterior do mesmo 'arquivo' é tirada dos livros antes (sem restos)."""
    caminho = Path(caminho); rel = _rel(caminho)
    o = (_j(ORIGENS, {}) or {}).get(rel)
    if o:
        lids = {e[0] for c in (o.get("conteineres") or {}).values() for e in c.get("entradas") or []}
        if o.get("inteiro"):
            lids.add(o["inteiro"][0])
        for lid in lids:
            d = ler(lid)
            if (d.get("acervo") or {}).pop(rel, None) is not None:
                gravar(lid, d)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
    return absorver([caminho], controle_sem_livro=controle_sem_livro)


# ── TRAVA: pastas cujo conteúdo só pode existir DENTRO dos livros ───────────────────────────────────────────────────
PROIBIDOS = ["estado/piloto/briefings",          # cresce a cada lote absorvido (16/10/2026)
             "dados/oportunidades/pareceres_livros", "dados/coleta_3_anos",   # lote 2
             "estado/cartorio/certidoes.json", "estado/cartorio/certidoes_manuais.json",   # lote 3
             "estado/agregadores/itens.json", "estado/piloto/candidatas_do_catalogo.json",  # entradas do fluxo
             "dados/editais/extraidos",                     # edições extraídas
             # 16/10: viraram LIVROS ESPECIAIS (biblioteca_alexandria/livros/especiais/...): as pastas antigas não voltam
             "biblioteca_alexandria/empresas", "dados/empresas", "estado/empresas_semanal.jsonl", "estado/emendas",
             "estado/sentinela", "estado/legislativo.json", "estado/legislativo_entrada.json", "estado/camara_goiania.json",
             "estado/ultima_carga_parlamentares.json", "estado/ultima_sentinela.json", "estado/piloto/aprendizados",
             "estado/prazos.json", "estado/rotas_recorrencia.json"]          # passo 2(a): análises de oportunidade


def absorver_proibidos() -> dict:
    """A cada passagem do comando: o que existir nas pastas proibidas é absorvido nos livros e apagado."""
    DESCOBERTA = ("estado/agregadores/itens.json", "estado/piloto/candidatas_do_catalogo.json")
    fs = [p for g in PROIBIDOS if g not in DESCOBERTA for p in ((ROOT / g).rglob("*") if (ROOT / g).is_dir() else [ROOT / g]) if p.is_file()]
    fd = [ROOT / g for g in DESCOBERTA if (ROOT / g).is_file()]       # entradas de descoberta: livro pelo portão, com ou sem prazo
    for g in PROIBIDOS:                                   # 16/10: .md nas pastas proibidas são cópias em texto do que está no livro
        if (ROOT / g).is_dir():
            for m_ in (ROOT / g).rglob("*.md"):
                m_.unlink()
    r = absorver(fs) if fs else {"arquivos": 0}
    if fd:
        r = {"geral": r, "descoberta": absorver(fd, descoberta=True)}
    for g in PROIBIDOS:
        d = ROOT / g
        if d.is_dir() and not any(d.rglob("*")):
            d.rmdir()
    return {"pastas_proibidas": PROIBIDOS, **r}


def proibido(rel: str) -> bool:
    if FAROL.search(rel):
        return False                                       # o Farol nunca é proibido (fora da regra)
    return any(rel == g or rel.startswith(g.rstrip("/") + "/") for g in PROIBIDOS)


# ── transição: módulos antigos leem e gravam pelos livros (16/10/2026) ──────────────────────────────────────────────
def ler_arquivo(caminho, padrao=None):
    """Lê o 'arquivo' antigo: em disco enquanto não foi absorvido; depois, montado a partir dos livros."""
    p = Path(caminho)
    if p.is_file():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return padrao
    return carregar(p, padrao)


def arquivos(pasta, padrao: str = "*.json") -> list[Path]:
    """Os 'arquivos' de uma pasta: os ainda em disco + os que já estão nos livros (para quem fazia glob)."""
    import fnmatch
    pasta = Path(pasta)
    fis = {_rel(p) for p in pasta.glob(padrao)} if pasta.is_dir() else set()
    nos_livros = {r for r in arquivos_de(pasta) if fnmatch.fnmatch(Path(r).name, padrao) and "/" not in r[len(_rel(pasta)) + 1:]}
    return [ROOT / r for r in sorted(fis | nos_livros)]


def guardar_lote(itens: list, descoberta: bool = False) -> dict:
    """Grava vários 'arquivos' de uma vez NOS LIVROS (o índice de ligação é montado uma só vez)."""
    caminhos = []
    for caminho, obj in itens:
        caminho = Path(caminho); caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8"); caminhos.append(caminho)
    return absorver(caminhos, descoberta=descoberta) if caminhos else {"arquivos": 0}


def idade_h(caminho) -> float:
    """Horas desde a última gravação do 'arquivo' antigo — em disco (mtime) ou nos livros (controle)."""
    import time
    p = Path(caminho)
    if p.exists():
        return (time.time() - p.stat().st_mtime) / 3600
    g = ((_j(ORIGENS, {}) or {}).get(_rel(p)) or {}).get("gravado_em")
    if not g:
        return 10 ** 6
    return (datetime.now(timezone.utc) - datetime.fromisoformat(g)).total_seconds() / 3600


def existe(caminho) -> bool:
    """O 'arquivo' antigo existe — em disco ou já absorvido nos livros (substitui Path.exists() nos leitores)."""
    p = Path(caminho)
    if p.exists():
        return True
    o = (_j(ORIGENS, {}) or {}).get(_rel(p))            # 16/10: só existe se houver conteúdo para montar
    return bool(o and (o.get("inteiro") or "controle" in o or any(c.get("entradas") for c in (o.get("conteineres") or {}).values())))
