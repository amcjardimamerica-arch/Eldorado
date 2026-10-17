"""OS LIVROS SÃO O BANCO DE DADOS (titular, 15/10/2026).

"Os motores não guardam informação nem têm banco próprio. Cada informação obtida vira um LIVRO, autônomo do motor, que
é visto por todo o sistema como o banco de dados. Cada oportunidade cria o seu livro ou se vincula ao livro que já tem o
seu histórico." O livro (catálogo da Biblioteca de Alexandria) guarda, numa seção única `oportunidade`:

  identidade      chave (compra do PNCP · endereço normalizado · título+órgão), título, órgão, UF
  links           link de acesso (onde foi encontrada), link oficial, classe e resultado da curadoria
  trecho          o texto exato da oportunidade e de onde ele veio
  checklist12     os 12 itens com estado, valor, trecho, página, documento e fonte; dispensas justificadas
  achados         cada motor que a encontrou, com o endereço e quando
  analises        Cartório, dossiê do PNCP, curadoria, rede neural, Interceptador, Piloto e Claude externo
  estado          estado, motivo, prazo e prontidão para o Farol

ETAPA 1 (esta): toda oportunidade do repositório cria/vincula o seu livro, e o livro passa a reunir tudo.
ETAPA 2: repositório, fichas e painel leem dos livros. ETAPA 3: saem os bancos paralelos dos motores.
Catálogo: biblioteca_alexandria/fontes/motores.json. Índice: biblioteca_alexandria/fontes/indice_chaves.json.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .nucleo import ROOT
from .vistos import chave

CAT = ROOT / "biblioteca_alexandria/fontes/motores.json"
INDICE = ROOT / "biblioteca_alexandria/fontes/indice_chaves.json"


def _j(p, padrao):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao


def _agora() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _chaves_do_livro(lv: dict) -> set:
    ks = set()
    if isinstance(lv.get("oportunidade"), dict) and lv["oportunidade"].get("chave"):
        ks.add(lv["oportunidade"]["chave"])
    pags = lv.get("paginas") if isinstance(lv.get("paginas"), list) else []
    for u in [lv.get("pagina"), lv.get("site_oficial"), *pags]:
        if isinstance(u, str) and u.startswith("http"):
            ks.add(chave({"url": u}))
    return ks


def _analises(r, cert, cur, dos, inter, piloto, val) -> list:
    a = []
    if cert:
        a.append({"origem": "Cartório", "em": cert.get("em"), "leitura": cert.get("leitura"), "ainda_faltam": cert.get("ainda_faltam"),
                  "link_oficial": cert.get("link_oficial")})
    if dos:
        a.append({"origem": "dossiê do PNCP", "em": dos.get("em"), "status": dos.get("status"), "motivo": dos.get("motivo"),
                  "pertinencia": dos.get("pertinencia"), "fontes": [f.get("fonte") for f in dos.get("fontes") or []]})
    if cur:
        a.append({"origem": "curadoria do link oficial", "resultado": cur.get("curadoria"), "classe": cur.get("classe_do_link_oficial"),
                  "criterios_que_falham": cur.get("falham")})
    if isinstance(r.get("nota_rede"), (int, float)):
        a.append({"origem": "rede neural", "nota": r["nota_rede"]})
    if inter:
        a.append({"origem": "Piloto - Interceptador", "em": inter.get("em"), "qualidade": inter.get("qualidade"),
                  "comprovados": inter.get("comprovados"), "de": inter.get("de")})
    if piloto:
        a.append({"origem": "Piloto", "em": piloto.get("em"), "desfecho": piloto.get("desfecho"), "motivo": piloto.get("motivo")})
    if val:
        a.append({"origem": "Claude (validação externa)", "decisao": val.get("decisao") or val.get("veredito"), "motivo": val.get("motivo")})
    return a


def _novo_livro(r: dict, k: str) -> dict:
    return {"id": "op-" + hashlib.sha1(k.encode()).hexdigest()[:12], "programa": r.get("titulo"), "orgao": r.get("orgao"), "uf": r.get("uf"),
            "tipo": "repositorio_de_oportunidade", "motor": "banco de livros", "pagina": r.get("link_oficial") or r.get("url"),
            "criado_em": _agora()[:10], "motivo_status": "criado a partir da oportunidade (os livros são o banco)", "historico": []}


def consolidar(gravar: bool = True) -> dict:
    cat_doc = _j(CAT, {"motores": []}); L = cat_doc.setdefault("motores", [])
    por_id = {lv.get("id"): lv for lv in L}
    idx = {}
    for lv in L:
        for k in _chaves_do_livro(lv):
            idx.setdefault(k, lv.get("id"))
    regs = (_j(ROOT / "biblioteca_alexandria/livros/_vistas/repositorio_unico.json", {}) or {}).get("registros") or []
    certs = {str(k).split(":", 1)[-1]: c for k, c in ((__import__("src.livro_arquivo", fromlist=["x"]).ler_arquivo(ROOT / "estado/cartorio/certidoes.json", {}) or {}).get("certidoes") or {}).items()}
    cur = {x.get("id"): x for x in (_j(ROOT / "biblioteca_alexandria/livros/_vistas/curadoria_links.json", {}) or {}).get("itens") or []}
    dos = (_j(ROOT / "estado/pncp/dossies.json", {}) or {}).get("dossies") or {}
    inter = (_j(ROOT / "estado/interceptador/estado.json", {}) or {}).get("feitos") or {}
    piloto = (_j(ROOT / "estado/piloto/aprendizados/tratados.json", {}) or {}).get("itens") or {}
    val = {}
    for f in sorted((ROOT / "biblioteca_alexandria/livros/_vistas/validacao_mapa").glob("validacao_*.json")):
        for it in (_j(f, {}) or {}).get("itens") or []:
            if isinstance(it, dict) and it.get("id"):
                val[it["id"]] = it
    criados = vinculados = 0
    try:                                               # 16/10 (titular): ÍNDICE — a nova edição encontra o livro do programa
        from .indice_livros import Indice, entrada
        _IDX = Indice([entrada(lv) for lv in L if lv.get("id")])
    except Exception:  # noqa: BLE001
        _IDX = None
    pelo_indice = 0
    for r in regs:
        k = chave(r)
        lid = r.get("livro") if r.get("livro") in por_id else (idx.get(k) or (idx.get(chave({"url": r["link_oficial"]})) if r.get("link_oficial") else None))
        if lid not in por_id and _IDX:
            _lid, _s, _mot = _IDX.encontrar(r)
            if _lid in por_id:
                lid = _lid; pelo_indice += 1
        if lid in por_id:
            lv = por_id[lid]; vinculados += 1
        else:
            lv = _novo_livro(r, k); L.append(lv); por_id[lv["id"]] = lv; criados += 1
        idx[k] = lv["id"]
        c, cu = certs.get(r["id"]), cur.get(r["id"])
        it12 = {}
        for nome, v in (r.get("itens") or {}).items():
            if isinstance(v, dict):
                it12[nome] = {kk: v.get(kk) for kk in ("estado", "valor", "trecho", "pagina", "documento", "fonte") if v.get(kk) is not None}
        for nome, v in ((c or {}).get("itens") or {}).items():
            if isinstance(v, dict):
                it12[nome] = {"estado": "comprovado", **{kk: v.get(kk) for kk in ("valor", "trecho", "pagina", "documento", "fonte", "metodo") if v.get(kk) is not None}}
        antes = lv.get("oportunidade") if isinstance(lv.get("oportunidade"), dict) else {}
        achados = {(a.get("motor"), a.get("url")): a for a in antes.get("achados") or [] if isinstance(a, dict)}
        for o in [r.get("origem"), *(r.get("fontes") or [])]:
            if o:
                m = str(o if isinstance(o, str) else (o.get("motor") or o.get("origem") or ""))[:80]
                achados.setdefault((m, r.get("url")), {"motor": m, "url": r.get("url"), "visto_em": r.get("publicado_em") or _agora()[:10]})
        lv["oportunidade"] = {
            "chave": k, "id_repositorio": r["id"], "titulo": r.get("titulo"), "orgao": r.get("orgao"), "uf": r.get("uf"),
            "links": {"acesso": r.get("url"), "oficial": (cu or {}).get("link_oficial") or r.get("link_oficial"),
                      "classe_do_oficial": (cu or {}).get("classe_do_link_oficial"), "curadoria": (cu or {}).get("curadoria")},
            "trecho": (cu or {}).get("trecho"), "checklist12": it12, "dispensas": (c or {}).get("dispensas") or {},
            "achados": list(achados.values())[-30:],
            "analises": _analises(r, c, cu, dos.get(r["id"]), inter.get(r["id"]), piloto.get(r.get("url") or ""), val.get(r["id"])),
            "estado": {"estado": r.get("estado"), "motivo": r.get("motivo_estado"), "fim": r.get("fim"), "pronta_para_farol": r.get("pronta_para_farol")},
            "atualizado_em": _agora()}
    # eliminada/descartada = livro eliminado: o livro criado só para ela sai; o livro antigo perde a seção da oportunidade
    ativos = {r["id"] for r in regs}
    removidos = 0
    for lv in list(L):
        op = lv.get("oportunidade") if isinstance(lv.get("oportunidade"), dict) else None
        if op and op.get("id_repositorio") not in ativos:
            if lv.get("motor") == "banco de livros":
                L.remove(lv); removidos += 1
            else:
                lv.pop("oportunidade", None)
    idx = {k: v for k, v in idx.items() if v in {lv.get("id") for lv in L}}
    for lv in L:                                       # 16/10: achados já guardados ficam só com o necessário
        for i, x in list((lv.get("coleta") or {}).items()):
            if isinstance(x, dict):
                lv["coleta"][i] = so_o_necessario(x)
    # etapa 3: JUNÇÃO — os achados da mesma oportunidade (ids_origem) vão para o livro dela; o livro de entrada que
    # ficar vazio sai (sem multiplicar livros)
    onde = {}
    for lv in L:
        for i in (lv.get("coleta") or {}):
            onde.setdefault(str(i), lv.get("id"))
    juntados = 0
    for r in regs:
        alvo = por_id.get(idx.get(chave(r)))
        if not alvo:
            continue
        for i in [r["id"], *(r.get("ids_origem") or [])]:
            src_id = onde.get(str(i))
            if src_id and src_id != alvo.get("id") and src_id in por_id:
                src = por_id[src_id]; x = (src.get("coleta") or {}).pop(str(i), None)
                if x is not None:
                    alvo.setdefault("coleta", {})[str(i)] = x; onde[str(i)] = alvo["id"]; juntados += 1
    ids_repo = {str(i) for r in regs for i in [r["id"], *(r.get("ids_origem") or [])]}
    entrada_removidos = 0
    for lv in list(L):
        if lv.get("motor") != "banco de livros" or lv.get("oportunidade") or lv.get("brutos") or lv.get("historico"):
            continue
        if not lv.get("coleta") or (regs and not (set(lv["coleta"]) & ids_repo)):
            L.remove(lv); por_id.pop(lv.get("id"), None); entrada_removidos += 1   # 16/10: não virou oportunidade → não fica
    # etapa 2 (fichas): o ACHADO BRUTO de cada motor (coleta) e o registro do agregador ficam no livro da oportunidade
    try:
        ids = {}
        for r in regs:
            lid = idx.get(chave(r))
            if lid:
                for i in [r["id"], *(r.get("ids_origem") or [])]:
                    ids[str(i)] = lid
        col = ROOT / "dados/oportunidades/oportunidades.jsonl"
        if col.exists() and ids:
            with col.open(encoding="utf-8") as fh:
                for linha in fh:
                    if '"id"' not in linha:
                        continue
                    try:
                        x = json.loads(linha)
                    except ValueError:
                        continue
                    lid = ids.get(str(x.get("id")))
                    if lid in por_id:
                        por_id[lid].setdefault("coleta", {})[str(x["id"])] = x
        for x in (__import__("src.livro_arquivo", fromlist=["x"]).ler_arquivo(ROOT / "estado/agregadores/itens.json", {}) or {}).get("itens") or []:
            lid = ids.get(str(x.get("id")))
            if lid in por_id:
                por_id[lid].setdefault("agregador", {})[str(x["id"])] = x
    except Exception:  # noqa: BLE001
        pass
    cat_doc["total"] = len(L); cat_doc["gerado_em"] = _agora()
    if gravar:
        CAT.write_text(json.dumps(cat_doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        INDICE.write_text(json.dumps({"em": _agora(), "chaves": idx}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    try:
        from .indice_livros import construir as _ci
        _ci(gravar)                                    # o índice é refeito a cada passagem
    except Exception:  # noqa: BLE001
        pass
    return {"oportunidades": len(regs), "livros_criados": criados, "livros_vinculados": vinculados, "ligados_pelo_indice": pelo_indice,
            "livros_removidos": removidos,
            "livros_de_entrada_removidos": entrada_removidos, "achados_juntados": juntados, "livros": len(L)}


def livro_da_oportunidade(a: dict) -> dict | None:
    """Leitura padrão para todo o sistema: o livro de uma oportunidade, pela chave."""
    lid = ((_j(INDICE, {}) or {}).get("chaves") or {}).get(chave(a))
    return next((lv for lv in (_j(CAT, {}) or {}).get("motores") or [] if lv.get("id") == lid), None) if lid else None




# ── ETAPA 2 · o repositório lê dos livros ───────────────────────────────────────────────────────────────────────────
# Enquanto os motores ainda entregam pelos arquivos antigos (a etapa 3 os tira), tudo o que eles trazem ENTRA PRIMEIRO
# nos livros: cada registro bruto cria o seu livro ou se vincula ao que já tem o histórico, e fica guardado nele
# (livro["brutos"][id]). O repositório deixa de ler os arquivos dos motores e lê os livros (brutos_dos_livros).
# Sincronia: o que a origem deixou de trazer (expurgado, encerrado na fonte) sai do livro também.
def ingerir(brutos: list[dict], gravar: bool = True) -> dict:
    cat_doc = _j(CAT, {"motores": []}); L = cat_doc.setdefault("motores", [])
    por_id = {lv.get("id"): lv for lv in L}
    idx = {}
    for lv in L:
        for k in _chaves_do_livro(lv):
            idx.setdefault(k, lv.get("id"))
        for b in (lv.get("brutos") or {}).values():
            if isinstance(b, dict):
                idx.setdefault(chave(b), lv.get("id"))
    # chave interna = origem + id: a MESMA oportunidade vem do fluxo e da caixa com o mesmo id e campos diferentes
    _k = lambda b: f"{b.get('_fonte') or 'caixa'}:{b.get('id')}"
    for n, b in enumerate(brutos):
        b["_ordem"] = n                               # a ordem de chegada é preservada (o repositório depende dela)
    atuais = {_k(b) for b in brutos if b.get("id") is not None}
    criados = vinculados = 0
    for b in brutos:
        if b.get("id") is None:
            continue
        k = chave(b)
        lid = idx.get(k)
        if lid not in por_id:
            lv = _novo_livro(b, k); L.append(lv); por_id[lv["id"]] = lv; criados += 1; idx[k] = lv["id"]
        else:
            lv = por_id[lid]; vinculados += 1
        lv.setdefault("brutos", {})[_k(b)] = b
    retirados = 0
    for lv in list(L):
        br = lv.get("brutos") or {}
        for i in [i for i in br if i not in atuais]:
            del br[i]; retirados += 1
        if lv.get("motor") == "banco de livros" and not br and not lv.get("oportunidade") and not lv.get("coleta"):
            L.remove(lv)                                # livro criado só para um registro que a origem não traz mais (16/10: nunca com achados)
    cat_doc["total"] = len(L); cat_doc["gerado_em"] = _agora()
    if gravar:
        CAT.write_text(json.dumps(cat_doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {"brutos": len(atuais), "livros_criados": criados, "vinculados": vinculados, "retirados": retirados, "livros": len(L)}


def brutos_dos_livros() -> list[dict]:
    """A entrada do repositório, lida dos LIVROS (a ordem estável é a do catálogo)."""
    out, vistos = [], set()
    for lv in (_j(CAT, {}) or {}).get("motores") or []:
        for i, b in (lv.get("brutos") or {}).items():
            if i not in vistos and isinstance(b, dict):
                vistos.add(i); out.append(b)
    out.sort(key=lambda b: b.get("_ordem", 10**9))
    return [{k: v for k, v in b.items() if k != "_ordem"} for b in out]


def secoes_dos_livros(secao: str) -> dict:
    """Etapa 2: {id: registro} de uma seção guardada nos livros ('coleta', 'agregador' ou 'brutos:fluxo')."""
    out = {}
    fonte = secao.split(":", 1)[1] if ":" in secao else None
    for lv in (_j(CAT, {}) or {}).get("motores") or []:
        if secao.startswith("brutos"):
            for b in (lv.get("brutos") or {}).values():
                if isinstance(b, dict) and b.get("_fonte") == fonte:
                    out[b.get("id")] = b
        else:
            out.update(lv.get(secao) or {})
    return out


def fluxo_por_uf() -> dict:
    """Etapa 2: {"itens_por_uf": {uf: [registros]}} — o fluxo como os módulos antigos o liam, reconstruído dos LIVROS."""
    grupos: dict = {}
    regs = [b for b in brutos_dos_livros() if b.get("_fonte") == "fluxo"]
    for b in regs:
        x = {k: v for k, v in b.items() if k not in ("_fonte", "_uf")}
        grupos.setdefault(b.get("_uf") or "BR", []).append(x)
    return {"itens_por_uf": grupos} if regs else {}


# 16/10/2026 (titular): do motor fica SÓ o trecho exato da oportunidade, o link da publicação, o link oficial e a
# identificação mínima que o fluxo, as fichas e o painel usam. Nada mais do documento; análises derivadas (qualidade,
# destinação, pertinência, caracterização, léxico) não ficam no achado.
CAMPOS_DO_ACHADO = ("id", "titulo", "evidencia", "url", "link_oficial", "pagina_oficial", "fonte_nome", "fonte_id", "sensor", "motor",
                    "tipo_fonte", "tipo_registro", "coletado_em", "data_publicacao", "data_consulta", "descoberto_em", "visto_em", "inicio",
                    "fim", "prazo_texto", "prazo_situacao", "nivel", "uf", "territorio", "orgao", "objeto", "valor", "area", "status",
                    "estado_export", "confianca", "_seq", "relido_por")
# 16/10/2026 (titular): SEM limite — o trecho guardado é o suficiente para a oportunidade INTEIRA


def so_o_necessario(a: dict) -> dict:
    x = {k: a[k] for k in CAMPOS_DO_ACHADO if k in a and a[k] not in (None, "", [], {})}
    return x


# ── ETAPA 3 · os motores gravam no LIVRO ─────────────────────────────────────────────────────────────────────────────
def registrar_achados(achados: list[dict], motor: str | None = None, gravar: bool = True) -> dict:
    """Cada achado (já aprovado pelo portão de oportunidade) cria o seu livro ou se vincula ao que já tem o histórico,
    e fica guardado nele (livro["coleta"][id]). Uma única gravação do catálogo por chamada."""
    if not achados:
        return {"achados": 0, "livros_criados": 0, "vinculados": 0}
    cat_doc = _j(CAT, {"motores": []}); L = cat_doc.setdefault("motores", [])
    por_id = {lv.get("id"): lv for lv in L}
    idx = {}
    for lv in L:
        for k in _chaves_do_livro(lv):
            idx.setdefault(k, lv.get("id"))
        for sec in ("brutos", "coleta"):
            for b in (lv.get(sec) or {}).values():
                if isinstance(b, dict):
                    idx.setdefault(chave(b), lv.get("id"))
    criados = vinculados = pelo_indice = 0
    _ind = None
    seq = int(cat_doc.get("seq_achados") or 0)
    for a in achados:
        if a.get("id") is None:
            continue
        seq += 1
        a = {**a, "_seq": a.get("_seq") or seq}           # ordem de chegada (o fluxo e o painel dependem dela)
        k = chave(a); lid = idx.get(k)
        if lid not in por_id:                             # 17/10 (titular): o MOTOR consulta o índice antes de criar livro
            if _ind is None:
                from .indice_livros import Indice, entrada
                _ind = Indice([entrada(x) for x in L if x.get("id")])
            _lid, _s, _mot = _ind.encontrar(a)
            if _lid in por_id:
                lid = _lid; idx[k] = lid; a = {**a, "_indice": _mot}
                pelo_indice += 1
        if lid not in por_id:
            lv = _novo_livro(a, k); L.append(lv); por_id[lv["id"]] = lv; idx[k] = lv["id"]; criados += 1
        else:
            lv = por_id[lid]; vinculados += 1
        col = lv.setdefault("coleta", {})
        if str(a["id"]) in col:                          # releitura padrão: o PRIMEIRO achado fica; os seguintes são anotados
            x = col[str(a["id"])]
            quem = a.get("sensor") or a.get("motor") or motor
            if quem and quem not in (x.get("relido_por") or []):
                x["relido_por"] = (x.get("relido_por") or []) + [quem]
            continue
        col[str(a["id"])] = so_o_necessario({**a, **({"motor": motor} if motor and not a.get("motor") else {})})
    cat_doc["seq_achados"] = seq
    if gravar:
        cat_doc["total"] = len(L); cat_doc["gerado_em"] = _agora()
        CAT.write_text(json.dumps(cat_doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {"achados": len(achados), "livros_criados": criados, "vinculados": vinculados, "ligados_pelo_indice": pelo_indice}


def achados() -> list[dict]:
    """Leitura padrão dos achados dos motores — a partir dos LIVROS (substitui a base bruta oportunidades.jsonl), na
    ordem de chegada e sem campos internos."""
    out = []
    for lv in (_j(CAT, {}) or {}).get("motores") or []:
        out.extend(x for x in (lv.get("coleta") or {}).values() if isinstance(x, dict))
    out.sort(key=lambda x: x.get("_seq") or 0)
    return [{k: v for k, v in x.items() if k not in ("_seq", "relido_por")} for x in out]


def migrar_base_para_livros(base: Path | None = None) -> dict:
    """Uma vez: as linhas da base bruta (já limpa pelo portão) entram nos livros, na ordem em que estão."""
    base = base or ROOT / "dados/oportunidades/oportunidades.jsonl"
    linhas = []
    if base.exists():
        for n, l in enumerate(base.open(encoding="utf-8"), 1):
            try:
                a = json.loads(l)
            except ValueError:
                continue
            if isinstance(a, dict) and a.get("id") is not None:
                a["_seq"] = n; linhas.append(a)
    return registrar_achados(linhas, None)


def limpar_base_bruta(base: Path | None = None, gravar: bool = True) -> dict:
    """Etapa 3 (16/10/2026): a base bruta dos motores fica só com o que é OPORTUNIDADE (portão no motor) e com trecho
    antigo que é histórico de um livro existente; o resto sai. Não cria um livro por achado: quem reconhece que dois
    achados são a mesma oportunidade é a unificação do repositório, que vincula cada oportunidade ao seu livro."""
    from .porta_oportunidade import motivo_para_nao_guardar
    from collections import Counter
    base = base or ROOT / "dados/oportunidades/oportunidades.jsonl"
    if not base.exists():
        return {"mantidas": 0, "removidas": 0}
    import re as _re
    urls_livros = set(_re.findall(r'https?://[^"\\\s]+', CAT.read_text(encoding="utf-8"))) if CAT.exists() else set()
    manter, fora = [], Counter()
    with base.open(encoding="utf-8") as fh:
        for linha in fh:
            try:
                a = json.loads(linha)
            except ValueError:
                fora["linha inválida"] += 1; continue
            if not isinstance(a, dict) or a.get("id") is None:
                fora["sem id"] += 1; continue
            m = motivo_para_nao_guardar(a)
            if m and m.startswith("edital de ano anterior") and a.get("url") in urls_livros:
                m = None                                   # trecho antigo ligado a um livro: é histórico dele
            if m:
                fora[m.split(" —")[0].split(" (")[0].split(" em 20")[0][:50]] += 1
            else:
                manter.append(linha if linha.endswith("\n") else linha + "\n")
    if gravar:
        base.write_text("".join(manter), encoding="utf-8")
    return {"mantidas": len(manter), "removidas": sum(fora.values()), "motivos": dict(fora.most_common())}


MARCO_MIGRACAO = ROOT / "estado/livros_migracao.json"


def migrar_se_preciso() -> dict:
    """Uma única vez, depois do expurgo e da limpeza da base: os achados da base vão para os livros. Depois disso,
    o fluxo e o painel dos motores leem dos livros e cada motor grava direto neles."""
    if MARCO_MIGRACAO.exists():
        return {"migracao": "já feita", **(_j(MARCO_MIGRACAO, {}) or {})}
    limpeza = limpar_base_bruta()
    r = migrar_base_para_livros()
    MARCO_MIGRACAO.parent.mkdir(parents=True, exist_ok=True)
    MARCO_MIGRACAO.write_text(json.dumps({"em": _agora(), "limpeza": {k: v for k, v in limpeza.items() if k != "motivos"}, **r},
                                         ensure_ascii=False, indent=1), encoding="utf-8")
    return {"migracao": "feita agora", **r}


def sincronizar_achados(registros: dict) -> dict:
    """Etapa 3: quem antes regravava a base inteira (gravar_oportunidades) agora sincroniza os livros — achado
    alterado é atualizado no livro dele, achado removido sai, achado novo entra (cria ou vincula o livro)."""
    cat_doc = _j(CAT, {"motores": []}); L = cat_doc.setdefault("motores", [])
    onde = {}
    for lv in L:
        for i in (lv.get("coleta") or {}):
            onde[str(i)] = lv
    alt = rem = 0
    for i, lv in list(onde.items()):
        if i not in registros:
            lv["coleta"].pop(i, None); rem += 1
        else:
            atual = lv["coleta"][i]
            internos = {k: atual[k] for k in ("_seq", "relido_por") if k in atual}
            novo = so_o_necessario(registros[i])
            if {k: v for k, v in atual.items() if k not in internos} != {k: v for k, v in novo.items() if k not in internos}:
                lv["coleta"][i] = {**novo, **internos}; alt += 1
    novos = [x for i, x in registros.items() if str(i) not in onde]
    CAT.write_text(json.dumps(cat_doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    r = registrar_achados(novos) if novos else {}
    return {"alterados": alt, "removidos": rem, "novos": len(novos), **r}


MARCO_MODALIDADE = ROOT / "estado/modalidade_migracao.json"


def renomear_modalidade_nos_dados(simular: bool = False) -> dict:
    """16/10/2026 (titular): o item 'Destinação' passa a se chamar 'Modalidade' — a forma como o recurso chega à
    associação (convênio, termo de fomento/colaboração, contrato, doação, prêmio, incentivo fiscal…), que diz ao Farol
    qual legislação se aplica, quais documentos, como é a inscrição e a prestação de contas. Uma vez, em todos os dados:
    CHAVES 'Destinação' e o NOME do item em listas; texto livre ('Destinação judicial', 'de prestações…') não muda."""
    if MARCO_MODALIDADE.exists() and not simular:
        return {"migracao": "já feita"}
    from collections import Counter

    def trocar(o, c):
        if isinstance(o, dict):
            return {("Modalidade" if k == "Destinação" and not c.update(chaves=1) else k): trocar(v, c) for k, v in o.items()}
        if isinstance(o, list):
            return [("Modalidade" if v == "Destinação" and not c.update(nomes=1) else trocar(v, c)) for v in o]
        return o
    tot, arquivos = Counter(), 0
    for area in ("dados", "estado", "docs/dados", "biblioteca_alexandria"):
        for p in (ROOT / area).rglob("*"):
            if not p.is_file() or p.suffix not in (".json", ".jsonl") or p.stat().st_size > 120_000_000:
                continue
            txt = p.read_text(encoding="utf-8", errors="replace")
            if "Destinação" not in txt and "Destina\\u00e7\\u00e3o" not in txt:   # também o acento escapado
                continue
            c = Counter()
            if p.suffix == ".jsonl":
                novas = []
                for l in txt.splitlines():
                    try:
                        novas.append(json.dumps(trocar(json.loads(l), c), ensure_ascii=False, separators=(",", ":")))
                    except ValueError:
                        novas.append(l)
                novo = "\n".join(novas) + ("\n" if txt.endswith("\n") else "")
            else:
                try:
                    obj = json.loads(txt)
                except ValueError:
                    continue
                o2 = trocar(obj, c)
                compacto = "\n" not in txt.strip()[:200]
                novo = json.dumps(o2, ensure_ascii=False, separators=(",", ":")) if compacto else \
                    json.dumps(o2, ensure_ascii=False, indent=2 if txt.startswith(("{\n  ", "[\n  ")) else 1)
            if sum(c.values()):
                tot.update(c); arquivos += 1
                if not simular:
                    p.write_text(novo, encoding="utf-8")
    r = {"arquivos": arquivos, **dict(tot)}
    if not simular:
        MARCO_MODALIDADE.parent.mkdir(parents=True, exist_ok=True)
        MARCO_MODALIDADE.write_text(json.dumps({"em": _agora(), **r}, ensure_ascii=False, indent=1), encoding="utf-8")
    return r


def _modalidade_do_texto(*textos) -> tuple[str, str, str] | None:
    """(modalidade oficial, base legal, texto onde está escrita) — só se ESTIVER escrita; nunca inferida."""
    import re
    from .cartorio_leitura import FORMALIZA, MODALIDADES
    NEGA = re.compile(r"(?i)(?:vedad[oa]s?|duplicidade|exceto|salvo|n[ãa]o (?:poder[áa]|ser[áa]|se aplica|é)|proibid[oa])[^.;]{0,40}$")
    melhor = None
    for n, t in enumerate(textos):
        if not isinstance(t, str) or not t.strip():
            continue
        for nome, rx, base, peso in MODALIDADES:
            for m in re.finditer(rx, t, re.I):
                antes = t[max(0, m.start() - 60):m.start()]
                if NEGA.search(antes):
                    continue                                 # menção negada ('vedada duplicidade com a Lei Rouanet')
                if n > 0 and not re.search(FORMALIZA + r"[^.;]{0,40}$", antes, re.I):
                    continue                                 # no TRECHO: só como forma de formalização
                if melhor is None or peso > melhor[3]:
                    melhor = (nome, base, t[max(0, m.start() - 120):m.end() + 120], peso)
                break
    return melhor[:3] if melhor else None


def revisar_modalidade_nos_livros(gravar: bool = True) -> dict:
    """16/10/2026 (titular): a Modalidade é a FORMA COMO O RECURSO CHEGA à associação — não a finalidade nem a
    elegibilidade. Em cada checklist dos livros: valor que já é modalidade é padronizado na lista oficial (com a base
    legal); elegibilidade ou finalidade no lugar → procura a modalidade escrita no próprio valor ou no trecho; se não
    estiver escrita, o item fica EM ABERTO para o Cartório extrair do documento. O log de mudanças não é alterado."""
    from collections import Counter
    cat_doc = _j(CAT, {"motores": []}); L = cat_doc.get("motores") or []
    res = Counter()
    LOG = ("mudou", "historico_parametros")

    def rever(item: dict) -> None:
        if not isinstance(item, dict):
            return
        v = item.get("valor", item.get("v"))
        if v in (None, "", "None"):
            res["vazio"] += 1; return
        achada = _modalidade_do_texto(str(v), item.get("trecho") or item.get("t"))
        chave_v = "valor" if "valor" in item else "v"
        if achada:
            nome, base, onde = achada
            if item.get(chave_v) != nome:
                res["padronizada" if str(v).strip().lower().startswith(nome.lower()[:6]) else "corrigida (estava escrita)"] += 1
            else:
                res["ja_correta"] += 1
            item[chave_v] = nome; item["base_legal"] = base
            item.setdefault("trecho", onde)
        else:
            res["em_aberto (era finalidade/elegibilidade)"] += 1
            item[chave_v] = None; item["estado"] = "falta"
            item["revisao_modalidade"] = f"valor anterior não era modalidade de recebimento: {str(v)[:120]}"
            for k in ("s",):
                if k in item:
                    item[k] = "falta"

    def andar(o, dentro_log=False):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "Modalidade" and not dentro_log:
                    rever(v)
                else:
                    andar(v, dentro_log or k in LOG)
        elif isinstance(o, list):
            for x in o:
                andar(x, dentro_log)
    for lv in L:
        andar(lv)
    # as certidões do Cartório são copiadas para os livros a cada passagem — revistas também, senão desfariam a revisão
    certs = {}
    for nome in ("certidoes.json", "certidoes_manuais.json"):
        p = ROOT / "estado/cartorio" / nome
        d_ = __import__("src.livro_arquivo", fromlist=["x"]).ler_arquivo(p, None)
        if d_:
            certs[p] = d_; andar(certs[p])
    if gravar:
        CAT.write_text(json.dumps(cat_doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        if certs:
            __import__("src.livro_arquivo", fromlist=["x"]).guardar_lote(list(certs.items()))
    return dict(res)


def revisar_modalidade_uma_vez() -> dict:
    """A revisão do CONTEÚDO da Modalidade roda uma vez, com registro próprio (independe da troca do nome)."""
    marco = ROOT / "estado/modalidade_revisao.json"
    if marco.exists():
        return {"revisao": "já feita"}
    r = revisar_modalidade_nos_livros()
    marco.parent.mkdir(parents=True, exist_ok=True)
    marco.write_text(json.dumps({"em": _agora(), **r}, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"revisao": "feita agora", **r}


def unir_duplicados(gravar: bool = True) -> dict:
    """16/10/2026 (titular): o índice revela o MESMO programa em dois livros; o conteúdo é juntado num só.
    Fica o livro com oportunidade aberta; senão, o de histórico maior; senão, o mais antigo. Junta achados, registros
    brutos, agregador, histórico (sem repetir edição), páginas e o arquivo do livro; o controle dos arquivos absorvidos
    passa a apontar para o livro que fica; 'juntados' guarda o rastro. Dois livros com oportunidades abertas DIFERENTES
    não são unidos."""
    from .indice_livros import Indice, entrada
    from . import livro_arquivo as LA
    cat_doc = _j(CAT, {"motores": []}); L = cat_doc.get("motores") or []
    por = {lv["id"]: lv for lv in L if lv.get("id")}
    I = Indice([entrada(lv) for lv in L if lv.get("id")])
    pares = []
    for lv in L:
        o, _s, _m = I.encontrar({"titulo": lv.get("programa"), "orgao": lv.get("orgao"), "uf": lv.get("uf"),
                                 "municipio": lv.get("municipio"), "url": lv.get("pagina")}, excluir=lv.get("id"))
        if o and o in por:
            par = tuple(sorted([lv["id"], o]))
            if par not in pares:
                pares.append(par)

    def peso(lv):
        return (1 if isinstance(lv.get("oportunidade"), dict) else 0, len(lv.get("historico") or []), -int(str(lv.get("criado_em") or "9999")[:4] or 9999))
    juntados, mantidos_separados, mapa = [], 0, {}
    for a, b in pares:
        a, b = mapa.get(a, a), mapa.get(b, b)
        if a == b or a not in por or b not in por:
            continue
        A, B = por[a], por[b]
        import re as _re
        _num = lambda t: set(_re.findall(r"(?i)(?:n[ºo°.]*\s*|edital\s+|chamamento\s+p[uú]blico\s+n?[ºo°]?\s*)0*(\d{1,4})\s*/\s*(\d{4})", str(t or "")))
        _inc = lambda t: set(_re.findall(r"(?i)\binciso\s+([ivxl]+)\b", str(t or "")))
        na, nb, ia, ib = _num(A.get("programa")), _num(B.get("programa")), _inc(A.get("programa")), _inc(B.get("programa"))
        if (na and nb and not (na & nb)) or (ia and ib and ia != ib):
            mantidos_separados += 1; continue           # editais DIFERENTES do mesmo órgão (número ou inciso): não une
        oa, ob = A.get("oportunidade"), B.get("oportunidade")
        if isinstance(oa, dict) and isinstance(ob, dict) and oa.get("id_repositorio") != ob.get("id_repositorio"):
            mantidos_separados += 1; continue
        fica, sai = (A, B) if peso(A) >= peso(B) else (B, A)
        for sec in ("coleta", "brutos", "agregador"):
            if sai.get(sec):
                fica.setdefault(sec, {}); fica[sec] = {**sai[sec], **fica[sec]}
        ids_h = {e.get("id") for e in fica.get("historico") or [] if isinstance(e, dict)}
        for e in sai.get("historico") or []:
            if isinstance(e, dict) and e.get("id") not in ids_h:
                fica.setdefault("historico", []).append(e); ids_h.add(e.get("id"))
        pags = [x for x in [*(fica.get("paginas") or []), sai.get("pagina"), *(sai.get("paginas") or [])] if isinstance(x, str)]
        fica["paginas"] = list(dict.fromkeys(pags))
        if not isinstance(fica.get("oportunidade"), dict) and isinstance(sai.get("oportunidade"), dict):
            fica["oportunidade"] = sai["oportunidade"]
        fica.setdefault("juntados", []).append({"id": sai["id"], "programa": sai.get("programa"), "em": _agora()[:10]})
        juntados.append((fica["id"], sai["id"], fica.get("programa"), sai.get("programa")))
        mapa[sai["id"]] = fica["id"]
        if gravar:
            d_f, d_s = LA.ler(fica["id"]), LA.ler(sai["id"])
            for rel, ent in (d_s.get("acervo") or {}).items():
                d_f.setdefault("acervo", {}).setdefault(rel, {}).update(ent)
            if d_s.get("acervo"):
                LA.gravar(fica["id"], d_f)
            (LA.PASTA / f"{sai['id']}.json").unlink(missing_ok=True)
        L.remove(sai); por.pop(sai["id"], None)
    if gravar and juntados:
        orig = _j(LA.ORIGENS, {}) or {}
        for reg in orig.values():
            for c in (reg.get("conteineres") or {}).values():
                for e in c.get("entradas") or []:
                    if e and e[0] in mapa:
                        e[0] = mapa[e[0]]
            if reg.get("inteiro") and reg["inteiro"][0] in mapa:
                reg["inteiro"][0] = mapa[reg["inteiro"][0]]
        LA.ORIGENS.parent.mkdir(parents=True, exist_ok=True)
        LA.ORIGENS.write_text(json.dumps(orig, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        cat_doc["total"] = len(L)
        CAT.write_text(json.dumps(cat_doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {"pares": len(pares), "juntados": len(juntados), "mantidos_separados": mantidos_separados,
            "lista": [{"fica": f, "sai": s_, "programa_fica": pf, "programa_sai": ps} for f, s_, pf, ps in juntados]}


def historico_e_epoca(gravar: bool = True) -> dict:
    """16/10/2026 (titular): (1) o histórico do livro é UM SÓ — o campo paralelo 'historico_edicoes' entra no
    'historico' (sem repetir edição) e deixa de existir; (2) a ÉPOCA DE ABERTURA é calculada das edições do próprio
    livro, cada data com a edição e o link de onde veio. Livro sem edição datada com fonte fica sem época (nada estimado)."""
    import re as _re
    from collections import Counter
    cat_doc = _j(CAT, {"motores": []}); L = cat_doc.get("motores") or []
    migrados = com_epoca = 0
    for lv in L:
        if lv.get("historico_edicoes"):
            h = lv.setdefault("historico", []); ids = {x.get("id") for x in h if isinstance(x, dict)}
            for e in lv.pop("historico_edicoes"):
                if isinstance(e, dict) and e.get("id") not in ids:
                    h.append({"id": e.get("id"), "titulo": e.get("titulo"), "ano": e.get("ano"), "pagina_oficial": e.get("link_oficial"),
                              "link_publicacao": e.get("link_publicacao"), "buscar_link_oficial": not e.get("link_oficial"),
                              "publicado_em": e.get("data_publicacao"), "inicio": e.get("inicio"), "fim": e.get("fim"),
                              "origem": "acervo de histórico"}); ids.add(e.get("id"))
            migrados += 1
        base = []
        for e in lv.get("historico") or []:
            if not isinstance(e, dict):
                continue
            data = str(e.get("inicio") or e.get("publicado_em") or "")[:10]
            fonte = e.get("pagina_oficial") or e.get("link_publicacao")
            if _re.fullmatch(r"\d{4}-\d{2}-\d{2}", data) and isinstance(fonte, str) and fonte.startswith("http"):
                base.append({"id": e.get("id"), "ano": data[:4], "data": data, "tipo": "abertura" if e.get("inicio") else "publicação", "fonte": fonte})
        if base:
            meses = Counter(b["data"][5:7] for b in base)
            lv["epoca_abertura"] = {"meses": [m for m, _ in meses.most_common()], "mes_mais_comum": meses.most_common(1)[0][0],
                                    "edicoes": sorted(base, key=lambda b: b["data"]), "calculada_em": _agora()[:10],
                                    "regra": "calculada das edições do próprio livro; cada data com a edição e o link de onde veio"}
            com_epoca += 1
        else:
            lv.pop("epoca_abertura", None)
    if gravar:
        CAT.write_text(json.dumps(cat_doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {"livros": len(L), "historico_paralelo_migrado": migrados, "com_epoca_de_abertura": com_epoca}

if __name__ == "__main__":
    print(json.dumps(consolidar(), ensure_ascii=False))
