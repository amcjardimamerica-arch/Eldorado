"""OPORTUNIDADES ENCONTRADAS PELOS PILOTOS, POR DIA (titular, 01/10).

Cada Piloto mostra, como os demais motores, as oportunidades que encontrou em cada dia — só as oportunidades, sem as
buscas. O histórico é PERMANENTE (estado/pilotos/achados_por_dia.json): sobrevive ao reset das missões.
  Espião        livros que ele criou, candidatas do catálogo e alvos das missões com resultado
  Interceptador oportunidades que ele estudou e comprovou (validada, parcial, fonte confirmada)
Painel: docs/dados/achados_pilotos.json (últimos 60 dias).
"""
from __future__ import annotations

import glob
import json
import re
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARQ = ROOT / "estado/pilotos/achados_por_dia.json"
PAINEL = ROOT / "docs/dados/achados_pilotos.json"
CAT = ROOT / "biblioteca_alexandria/fontes/motores.json"
UTIL = ("validada", "parcial", "fonte_confirmada", "fonte_possivel")


def _j(p, padrao):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:
        return padrao


def _item(titulo, url, uf=None, prazo=None, situacao=None, livro=None) -> dict | None:
    t = re.sub(r"\s+", " ", str(titulo or "")).strip()
    t = re.sub(r"(?i)^(continue lendo|leia mais|saiba mais|clique aqui|veja também|ver mais)[\s:—-]*", "", t)   # sobras da página
    if len(t) < 8:
        return None
    return {k: v for k, v in {"titulo": t[:180], "url": url if str(url or "").startswith("http") else None, "uf": uf, "prazo": prazo,
                              "situacao": situacao, "livro": livro}.items() if v}


def coletar() -> dict:
    """Junta, por dia, o que cada Piloto encontrou (fontes atuais + histórico permanente)."""
    H = _j(ARQ, {"espiao": {}, "interceptador": {}})
    def por(piloto, dia, it):
        if not it or not dia:
            return
        lista = H.setdefault(piloto, {}).setdefault(dia[:10], [])
        chave = (it.get("url") or it["titulo"]).lower()
        if not any((x.get("url") or x["titulo"]).lower() == chave for x in lista):
            lista.append(it)
    # ESPIÃO
    for c in (_j(ROOT / "estado/piloto/candidatas_do_catalogo.json", {}).get("itens") or _j(ROOT / "estado/piloto/candidatas_do_catalogo.json", [])):
        if isinstance(c, dict):
            por("espiao", str(c.get("descoberto_em") or ""), _item(c.get("titulo"), c.get("url"), situacao=c.get("enquadramento")))
    for m in (_j(ROOT / "estado/piloto/bordo.json", {}).get("missoes") or []):
        for a in (m.get("alvos") or []):
            if isinstance(a, dict):
                por("espiao", str(m.get("fim") or m.get("inicio") or ""), _item(a.get("titulo") or a.get("nome"), a.get("url") or a.get("onde"), a.get("uf"), a.get("prazo")))
    for x in (_j(CAT, {}).get("motores") or []):
        if "Piloto - Espião" in str(x.get("motivo_status") or ""):
            por("espiao", str(x.get("criado_em") or ""), _item(x.get("nome_classificado") or x.get("programa"), x.get("pagina"), x.get("geo"), livro=x.get("id")))
    # INTERCEPTADOR
    for f in sorted(glob.glob(str(ROOT / "estado/interceptador/relatorios/*.json"))):
        for v in (_j(f, {}).get("voos") or []):
            if v.get("tipo") == "edital" and v.get("qualidade") in UTIL:
                por("interceptador", str(v.get("em") or v.get("inicio") or ""),
                    _item(v.get("alvo"), v.get("pagina_oficial"), situacao=f"{v.get('qualidade')} · {v.get('comprovados') or 0} de 12 itens comprovados"))
    return H


def gravar(H: dict) -> dict:
    ARQ.parent.mkdir(parents=True, exist_ok=True)
    ARQ.write_text(json.dumps(H, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    desde = (date.today() - timedelta(days=60)).isoformat()
    pub = {p: {d: v for d, v in sorted((H.get(p) or {}).items()) if d >= desde} for p in ("espiao", "interceptador")}
    PAINEL.write_text(json.dumps({"em": date.today().isoformat(), **pub}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {p: {"dias": len(pub[p]), "oportunidades": sum(len(v) for v in pub[p].values())} for p in pub}


def guardar_nos_livros() -> dict:
    """Antes do reset: o que os Pilotos encontraram vai para os livros — o Espião cria o que falta; o estudo do
    Interceptador leva os itens comprovados ao livro estudado."""
    from .livros_regra import registrar_achados_do_espiao, anotar_checklist
    H = coletar()
    esp = [dict(it, prazo=it.get("prazo")) for dia in (H.get("espiao") or {}).values() for it in dia if it.get("url")]
    r_esp = registrar_achados_do_espiao(esp)
    C = _j(CAT, {}); por_id = {x.get("id"): x for x in (C.get("motores") or [])}; n = 0
    for f in glob.glob(str(ROOT / "dados/editais/extraidos/op-*.json")):
        e = _j(f, {}); I = e.get("investigacao_ia") or {}
        lid = Path(f).stem[3:]
        if lid in por_id and I.get("campos"):
            ck = {k: (v.get("valor") or v.get("trecho")) for k, v in I["campos"].items() if isinstance(v, dict) and v.get("comprovado")}
            if ck and anotar_checklist(por_id[lid], ck, "Piloto - Interceptador (estudo)"):
                n += 1
    if n:
        CAT.write_text(json.dumps(C, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {"espiao": r_esp, "interceptador_livros_atualizados": n, "historico": gravar(H)}


def run() -> dict:
    return gravar(coletar())


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=1))
