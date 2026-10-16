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
    regs = (_j(ROOT / "dados/oportunidades/repositorio_unico.json", {}) or {}).get("registros") or []
    certs = {str(k).split(":", 1)[-1]: c for k, c in ((_j(ROOT / "estado/cartorio/certidoes.json", {}) or {}).get("certidoes") or {}).items()}
    cur = {x.get("id"): x for x in (_j(ROOT / "estado/curadoria_links.json", {}) or {}).get("itens") or []}
    dos = (_j(ROOT / "estado/pncp/dossies.json", {}) or {}).get("dossies") or {}
    inter = (_j(ROOT / "estado/interceptador/estado.json", {}) or {}).get("feitos") or {}
    piloto = (_j(ROOT / "estado/piloto/aprendizados/tratados.json", {}) or {}).get("itens") or {}
    val = {}
    for f in sorted((ROOT / "dados/oportunidades/validacao_mapa").glob("validacao_*.json")):
        for it in (_j(f, {}) or {}).get("itens") or []:
            if isinstance(it, dict) and it.get("id"):
                val[it["id"]] = it
    criados = vinculados = 0
    for r in regs:
        k = chave(r)
        lid = r.get("livro") if r.get("livro") in por_id else (idx.get(k) or (idx.get(chave({"url": r["link_oficial"]})) if r.get("link_oficial") else None))
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
        for x in (_j(ROOT / "estado/agregadores/itens.json", {}) or {}).get("itens") or []:
            lid = ids.get(str(x.get("id")))
            if lid in por_id:
                por_id[lid].setdefault("agregador", {})[str(x["id"])] = x
    except Exception:  # noqa: BLE001
        pass
    cat_doc["total"] = len(L); cat_doc["gerado_em"] = _agora()
    if gravar:
        CAT.write_text(json.dumps(cat_doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        INDICE.write_text(json.dumps({"em": _agora(), "chaves": idx}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {"oportunidades": len(regs), "livros_criados": criados, "livros_vinculados": vinculados, "livros_removidos": removidos, "livros": len(L)}


def livro_da_oportunidade(a: dict) -> dict | None:
    """Leitura padrão para todo o sistema: o livro de uma oportunidade, pela chave."""
    lid = ((_j(INDICE, {}) or {}).get("chaves") or {}).get(chave(a))
    return next((lv for lv in (_j(CAT, {}) or {}).get("motores") or [] if lv.get("id") == lid), None) if lid else None


if __name__ == "__main__":
    print(json.dumps(consolidar(), ensure_ascii=False))


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
        if lv.get("motor") == "banco de livros" and not br and not lv.get("oportunidade"):
            L.remove(lv)                                # livro criado só para um registro que a origem não traz mais
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
