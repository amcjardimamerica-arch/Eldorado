"""AS OPORTUNIDADES DE CADA MOTOR, SEM REPETIÇÃO (titular, 27/09).

Cada motor da Bússola mostra quantas oportunidades DIFERENTES encontrou e as 5 mais recentes, com a DATA DE
PUBLICAÇÃO ORIGINAL. A mesma oportunidade chega em registros diferentes (a divulgação e a página oficial, o
"continue lendo" da ABCR, o título com e sem acento, o endereço com e sem parâmetros): aqui ela conta uma vez.
Edição de diário oficial não é oportunidade e não entra.
Saída: docs/dados/achados_motores.json
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
MESTRE = ROOT / "dados/oportunidades/oportunidades.jsonl"
SAIDA = ROOT / "docs/dados/achados_motores.json"
ALIAS = {   # motor da Bússola → identificadores de fonte gravados nos registros
    "pncp-api": set(),   # 01/10 (motor 04 v2): os 215 registros "pncp" do coletor antigo (país inteiro, sem prazo) saem do cartão
    "plat-observatorio-3setor": {"observatorio-3setor", "observatorio-terceiro-setor"},
    "plat-secult-go": {"secult-go", "goyazes-programa"}, "piloto-aberto": {"plat-piloto-aberto", "piloto-aberto"},
    "plat-piloto-aberto": {"plat-piloto-aberto", "piloto-aberto"}, "plat-abcr": {"abcr"},
}


def _norm_tit(t: str) -> str:
    t = re.sub(r"(?i)^continue lendo\s+", "", str(t or ""))
    t = unicodedata.normalize("NFKD", t.lower()); t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "", t)[:70]


def _norm_url(u: str) -> str:
    p = urlsplit(str(u or "")); return ((p.hostname or "").replace("www.", "") + p.path.rstrip("/")).lower()


def _data(*v) -> str | None:
    for x in v:
        s = str(x or "")[:10]
        if re.match(r"\d{4}-\d{2}-\d{2}$", s):
            return s
    return None


def montar() -> dict:
    D = json.loads((ROOT / "docs/dados/descricao_motores.json").read_text(encoding="utf-8"))
    motores = list((D.get("motores") or D).keys())
    regs = [json.loads(l) for l in MESTRE.open(encoding="utf-8") if l.strip()] if MESTRE.exists() else []
    # a data de publicação de muitas fontes (ABCR, Diário de Goiás) está na ficha da Biblioteca, não no registro
    pub_ficha = {}
    for f in (ROOT / "biblioteca_alexandria/oportunidades").glob("*/*/ficha.json"):
        try:
            fi = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if fi.get("id") and _data(fi.get("data_publicacao"), fi.get("publicado_em")):
            pub_ficha[fi["id"]] = _data(fi.get("data_publicacao"), fi.get("publicado_em"))
    ext = ROOT / "dados/editais/extraidos"
    # OPRESSOR E SITE OFICIAL DE CADA OPORTUNIDADE (28/09): onde a informação fica guardada e onde ela nasce
    from .sites_oficiais import e_republicador
    cat = json.loads((ROOT / "biblioteca_alexandria/fontes/motores.json").read_text(encoding="utf-8")).get("motores", []) if (ROOT / "biblioteca_alexandria/fontes/motores.json").exists() else []
    lig = (json.loads((ROOT / "estado/opressores.json").read_text(encoding="utf-8")) or {}).get("ligados", {}) if (ROOT / "estado/opressores.json").exists() else {}
    opr_u = {_norm_url(x.get("pagina")): x for x in cat if x.get("pagina")}
    opr_t = {_norm_tit(x.get("programa")): x for x in cat}
    try:
        from .validacao_mapa import carregar as _valc
        VAL = _valc()
    except Exception:
        VAL = {}
    try:
        FX = {x["id"]: x for v in (json.loads((ROOT / "docs/dados/fluxo_oportunidades.json").read_text(encoding="utf-8")).get("itens_por_uf") or {}).values() for x in v}
    except Exception:
        FX = {}
    # O QUE O PRÓPRIO MOTOR VIU (28/09): o registro de uma oportunidade fica em nome de quem a catalogou primeiro; o motor
    # do Goiás Social viu o edital do Auxílio Nutricional 3 dias seguidos, mas o registro é do FEAS-GO. A lista do motor
    # junta o que é dele no registro E o que ele leu nos seus dias (d, t, u) — cada oportunidade uma vez.
    viu = {}
    try:
        MJ = json.loads((ROOT / "docs/dados/motores.json").read_text(encoding="utf-8"))
        por_url = {_norm_url(r.get("url")): r for r in regs if r.get("url")}
        por_tit = {_norm_tit(r.get("titulo")): r for r in regs if r.get("titulo")}
        for p in (MJ.get("plataformas") or []) + (MJ.get("oficiais") or []):
            for dd in p.get("dias") or []:
                if not dd.get("t"):
                    continue
                r0 = por_url.get(_norm_url(dd.get("u"))) or por_tit.get(_norm_tit(dd.get("t"))) or {}
                viu.setdefault(str(p.get("id")), []).append({**r0, "id": r0.get("id") or ("visto-" + _norm_url(dd.get("u"))[:40]),
                                                             "titulo": r0.get("titulo") or dd["t"], "url": r0.get("url") or dd.get("u"),
                                                             "descoberto_em": r0.get("descoberto_em") or dd.get("d")})
    except Exception:
        pass
    out = {}
    for mid in motores:
        ids = {mid, mid.replace("plat-", "")} | ALIAS.get(mid, set())
        xs = [r for r in regs if r.get("fonte_id") in ids]
        for k in ids:
            xs += viu.get(k, [])
        if mid == "piloto-interceptador":
            # O QUE O INTERCEPTADOR VALIDOU (28/09): ele não gera registro com a própria fonte nem leitura diária — o
            # resultado dele são os estudos. Entram as oportunidades que ele validou (completas ou parciais).
            try:
                est = json.loads((ROOT / "estado/interceptador/estado.json").read_text(encoding="utf-8")).get("feitos") or {}
            except Exception:
                est = {}
            por_id = {r.get("id"): r for r in regs}
            xs = []
            for eid, f in est.items():
                if f.get("qualidade") not in ("validada", "parcial"):
                    continue
                r0 = por_id.get(eid) or {}
                try:
                    e0 = json.loads((ext / f"{eid}.json").read_text(encoding="utf-8"))
                except Exception:
                    e0 = {}
                tit = r0.get("titulo") or e0.get("titulo")
                from .opressores_repositorio import NAO_E_SELECAO
                if tit and not NAO_E_SELECAO.search(tit):        # dispensa de chamamento, pessoa física e compra não são oportunidade
                    xs.append({**r0, "id": eid, "titulo": tit, "url": r0.get("url") or e0.get("url"),
                               "descoberto_em": str(f.get("em") or "")[:10], "fim": r0.get("fim") or e0.get("fim")})
        if mid.startswith(("idx-", "site-")):
            # 02/10: um motor por site — os indícios ligam-se ao motor PELO SITE de origem (o campo motor dos indícios
            # antigos guarda a família desmontada; o site não mudou)
            try:
                _sm = {x["id"]: x.get("motor") for x in json.loads((ROOT / "config/indexadores.json").read_text(encoding="utf-8")).get("sites") or []}
                xs = [{"id": g["id"], "titulo": g.get("titulo"), "url": g.get("link_oficial") or g.get("pagina_agregador"), "fim": g.get("prazo"),
                       "uf": g.get("uf"), "descoberto_em": g.get("primeiro_visto")}
                      for g in json.loads((ROOT / "estado/agregadores/itens.json").read_text(encoding="utf-8")).get("itens", [])
                      if any(_sm.get(f) == mid for f in (g.get("fontes") or [g.get("fonte")]))]
            except Exception:
                xs = []
        # 03/10 (titular): motor que recebeu sites agregados (motor 20 ← 40/41/43/44/45/47; motor 17 ← 42) soma os indícios deles
        try:
            _cxa = json.loads((ROOT / "config/indexadores.json").read_text(encoding="utf-8"))
            _agm = (_cxa.get("agregados") or {}).get("motores") or {}
            _sit = {a.get("site") for k, v in _agm.items() if k in ids or k.removeprefix("plat-") in ids for a in v}
            if _sit:
                xs = list(xs) + [{"id": g["id"], "titulo": g.get("titulo"), "url": g.get("link_oficial") or g.get("pagina_agregador"),
                                  "fim": g.get("prazo"), "uf": g.get("uf"), "descoberto_em": g.get("primeiro_visto")}
                                 for g in json.loads((ROOT / "estado/agregadores/itens.json").read_text(encoding="utf-8")).get("itens", [])
                                 if _sit & set(g.get("fontes") or [g.get("fonte")])]
        except Exception:
            pass
        if mid == "motor-agregadores":
            try:
                xs = [{"id": g["id"], "titulo": g.get("titulo"), "url": g.get("link_oficial") or g.get("pagina_agregador"), "fim": g.get("prazo"),
                       "uf": g.get("uf"), "descoberto_em": g.get("primeiro_visto")}
                      for g in json.loads((ROOT / "estado/agregadores/itens.json").read_text(encoding="utf-8")).get("itens", [])]
            except Exception:
                xs = []
        if mid == "do-goiania":
            # 01/10 (parecer do motor 01): antes entravam as EDIÇÕES do Querido Diário com "goiânia" no título —
            # inclusive Aparecida de Goiânia — e todas caíam no filtro "edição não é oportunidade" (268 → 0).
            # Agora entram os ATOS que o leitor recortou e classificou como oportunidade (fonte_id do-goiania).
            xs = [r for r in regs if r.get("fonte_id") == "do-goiania"]
        vistos_t, vistos_u, unicas = set(), set(), []
        for r in xs:
            r["_pub"] = _data(r.get("data_publicacao")) or pub_ficha.get(r.get("id"))
        for r in sorted(xs, key=lambda r: str(r["_pub"] or _data(r.get("descoberto_em"), r.get("coletado_em")) or ""), reverse=True):
            tit = str(r.get("titulo") or "")
            if not tit or re.match(r"(?i)di[aá]rio oficial d[eo] ", tit) or r.get("estado_export") in ("arquivado", "excluido"):
                continue
            kt, ku = _norm_tit(tit), _norm_url(r.get("url"))
            if (kt and kt in vistos_t) or (ku and ku in vistos_u):
                continue
            vistos_t.add(kt); vistos_u.add(ku)
            e = {}
            try:
                e = json.loads((ext / f"{r.get('id')}.json").read_text(encoding="utf-8"))
            except Exception:
                pass
            ve = e.get("verificacao_externa") if isinstance(e.get("verificacao_externa"), dict) else {}
            v = VAL.get(r.get("id")) or {}; fx = FX.get(r.get("id")) or {}
            of = next((u for u in (v.get("fonte_oficial"), fx.get("link_oficial"), ve.get("pagina_oficial"), e.get("pagina_oficial"))
                       if isinstance(u, str) and u.startswith("http") and not e_republicador(u)), None)
            o = opr_u.get(_norm_url(of)) or opr_u.get(ku) or opr_t.get(kt)
            dec = v.get("decisao")
            if o:
                opr = {"id": o["id"], "ligado": o["id"] in lig, "estado": "informação guardada no opressor"}
            elif dec in ("descartada", "arquivada_encerrada"):
                opr = {"id": None, "estado": ("encerrada — vai para a Biblioteca" if dec == "arquivada_encerrada" else "descartada") + f": {str(v.get('motivo') or '')[:90]}"}
            elif fx:
                opr = {"id": None, "estado": "opressor será criado no próximo ciclo do fluxo"}
            else:
                opr = {"id": None, "estado": "fora da janela das possíveis (mais de 60 dias sem prazo)"}
            unicas.append({"id": r.get("id"), "titulo": re.sub(r"(?i)^continue lendo\s+", "", tit)[:160],
                           "site_oficial": of, "opressor": opr, "decisao": dec,
                           "url": ve.get("pagina_oficial") or e.get("pagina_oficial") or r.get("url"),
                           "publicado_em": r["_pub"], "visto_em": None if r["_pub"] else _data(r.get("descoberto_em"), r.get("coletado_em")),
                           "prazo": _data(r.get("fim"), ve.get("prazo"), e.get("fim")), "uf": r.get("uf")})
        out[mid] = {"total_registros": len(xs), "total_unicas": len(unicas), "ultimas": unicas[:5]}
    res = {"em": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(timespec="seconds"), "regra": "oportunidades diferentes por motor, sem repetição; as 5 mais recentes pela data de publicação original", "motores": out}
    SAIDA.write_text(json.dumps(res, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {m: (v["total_registros"], v["total_unicas"]) for m, v in out.items() if v["total_registros"]}


if __name__ == "__main__":
    print(montar())
