"""UMA OPORTUNIDADE = UM LIVRO (titular, 11/10/2026) — reconciliação do catálogo da Biblioteca.

1. GRUPOS DE DUPLICATAS (a revisão humana confirmou que é o MESMO edital): os livros do grupo são FUNDIDOS num só —
   o que já contém a oportunidade canônica (senão o de histórico mais longo, depois o mais antigo). Os demais saem do
   catálogo, com o histórico, o checklist e o vínculo de leitura absorvidos (mesma fusão da curadoria).
2. LIVRO LIGADO SÓ À DUPLICATA: passa a conter também a canônica (o livro é da oportunidade, não da cópia).
3. OPORTUNIDADE EM MAIS DE UM LIVRO SEM SER DUPLICATA: se os livros são o MESMO programa pelo teste da curadoria
   (nome e financiador parecidos, sem ser edital distinto), são livros duplicados e se FUNDEM; se são programas
   diferentes (editais distintos de um mesmo programa, títulos genéricos de órgãos diferentes), NÃO se fundem — a
   oportunidade fica só no livro mais compatível (o que a tem como atual; senão o de nome mais parecido).
4. ids_juntados sem repetição em todos os livros.
Relatório: estado/biblioteca/unificacao_livros.json. Roda no fim da curadoria dos livros (src/fluxo_oportunidades.py); manual: python -m src.unificar_livros [--verificar]
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "biblioteca_alexandria/fontes/motores.json"
LIG = ROOT / "estado/livros_monitoramento.json"
REL = ROOT / "estado/biblioteca/unificacao_livros.json"


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao


GENERICO = r"^(aviso de |edital de |extrato de )?(chamamento|chamada|edital|credenciamento|sele[çc][ãa]o|aviso)( p[úu]blic[oa])?( n[ºo°.]?\s*[\d/.-]+)?$"


def mesmo_programa(a: dict, b: dict, par: dict) -> bool:
    """O mesmo programa em dois livros? Nome contido no outro ou quase igual palavra por palavra, órgão compatível;
    título genérico ('Aviso de Chamamento Público nº 1/2026') nunca basta para fundir."""
    import re
    import unicodedata
    from rapidfuzz import fuzz
    from .curadoria_biblioteca import mesma_oportunidade
    n = lambda t: re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", "".join(c for c in unicodedata.normalize("NFD", str(t or "").lower()) if unicodedata.category(c) != "Mn"))).strip()
    pa, pb = n(a.get("programa")), n(b.get("programa"))
    if not pa or not pb or re.match(GENERICO, pa) or re.match(GENERICO, pb) or min(len(pa), len(pb)) < 12:
        return False                                        # título genérico nunca basta, nem com o mesmo domínio
    try:
        if mesma_oportunidade(a, b, par):
            return True
    except Exception:  # noqa: BLE001
        pass
    nome = (pa in pb or pb in pa) or fuzz.token_set_ratio(pa, pb) >= 92
    oa, ob = n(a.get("orgao")), n(b.get("orgao"))
    orgao = not oa or not ob or fuzz.token_set_ratio(oa, ob) >= 80
    try:                                                    # mesmo domínio da página oficial também prova o financiador
        from .curadoria_biblioteca import _host
        orgao = orgao or (bool(_host(a.get("pagina"))) and _host(a.get("pagina")) == _host(b.get("pagina")))
    except Exception:  # noqa: BLE001
        pass
    try:                                                    # livro vindo de AGREGADOR: o "órgão" é o agregador, não o financiador
        from .cartorio_leitura import regua
        orgao = orgao or not regua(str(a.get("pagina") or ""))[0] or not regua(str(b.get("pagina") or ""))[0]
    except Exception:  # noqa: BLE001
        pass
    return bool(nome and orgao)


def unificar(gravar: bool = True) -> dict:
    from .livros_repositorio import canonica_por_revisao
    from .curadoria_biblioteca import _juntar, mesma_oportunidade, editais_distintos
    PAR = _j(ROOT / "config/parametros_biblioteca.json", {}).get("duplicidade") or {}
    C = _j(CAT, {"motores": []}); ms = C.get("motores") or []
    L = _j(LIG, {"ligados": {}}); lig = L.setdefault("ligados", {})
    canon = canonica_por_revisao()
    rel = {"em": datetime.now(timezone.utc).replace(microsecond=0).isoformat(), "fundidos": [], "religados": [], "retirados": [], "ids_juntados_limpos": 0}
    por_id = {m["id"]: m for m in ms}

    def livros_de() -> dict:
        d = defaultdict(list)
        for m in ms:
            for h in m.get("historico") or []:
                if isinstance(h, dict) and h.get("id"):
                    if m["id"] not in d[str(h["id"])]:
                        d[str(h["id"])].append(m["id"])
        return d

    # 1 · grupos de duplicatas → um livro
    grupos = defaultdict(set)
    for dup, can in canon.items():
        grupos[can] |= {dup, can}
    sai = set()
    li = livros_de()
    for can, g in grupos.items():
        ids = [l for i in g for l in li.get(i, []) if l not in sai]
        ids = list(dict.fromkeys(ids))
        if len(ids) > 1:
            def nota(lid):
                m = por_id[lid]; tem = any(str(h.get("id")) == can for h in m.get("historico") or [] if isinstance(h, dict))
                return (not tem, -len(m.get("historico") or []), str(m.get("criado_em") or "9999"))
            ids.sort(key=nota); fica = por_id[ids[0]]
            for lid in ids[1:]:
                _juntar(fica, por_id[lid]); sai.add(lid)
                if lid in lig:
                    lig.setdefault(fica["id"], lig[lid]); lig.pop(lid, None)
            rel["fundidos"].append({"canonica": can, "fica": fica["id"], "juntou": ids[1:], "programa": str(fica.get("programa"))[:100]})
    ms = [m for m in ms if m["id"] not in sai]; por_id = {m["id"]: m for m in ms}

    # 2 · livro ligado só à duplicata → contém também a canônica
    li = livros_de()
    for can, g in grupos.items():
        ids = list(dict.fromkeys(l for i in g for l in li.get(i, [])))
        if len(ids) == 1 and can not in li:
            m = por_id[ids[0]]
            m.setdefault("historico", []).append({"id": can, "titulo": str(m.get("programa") or "")[:160], "origem": "revisão humana: canônica do grupo de duplicatas"})
            m["edicoes"] = len(m["historico"])
            rel["religados"].append({"canonica": can, "livro": m["id"]})
    # marca as cópias no histórico
    for m in ms:
        for h in m.get("historico") or []:
            if isinstance(h, dict) and str(h.get("id")) in canon:
                h["duplicata_de"] = canon[str(h["id"])]

    # 3 · oportunidade em mais de um livro (sem ser duplicata) → fica só no mais compatível
    li = livros_de()
    for oid, ids in li.items():
        if len(ids) < 2 or oid in canon:
            continue
        def compat(lid):
            m = por_id[lid]; h = next((h for h in m.get("historico") or [] if isinstance(h, dict) and str(h.get("id")) == oid), {})
            try:
                from .cartorio_leitura import regua
                oficial = regua(str(m.get("pagina") or ""))[0]
            except Exception:  # noqa: BLE001
                oficial = True
            return (not oficial, m.get("atual") != oid, -SequenceMatcher(None, str(h.get("titulo") or "").lower(), str(m.get("programa") or "").lower()).ratio())
        ids = [i for i in sorted(ids, key=compat) if i not in sai]
        if len(ids) < 2:
            continue
        mesmos = [lid for lid in ids[1:] if mesmo_programa(por_id[ids[0]], por_id[lid], PAR) and not editais_distintos(por_id[ids[0]], por_id[lid])]
        for lid in mesmos:                                     # o mesmo programa em dois livros: funde
            _juntar(por_id[ids[0]], por_id[lid]); sai.add(lid)
            if lid in lig:
                lig.setdefault(ids[0], lig[lid]); lig.pop(lid, None)
        if mesmos:
            rel["fundidos"].append({"oportunidade": oid, "fica": ids[0], "juntou": mesmos, "programa": str(por_id[ids[0]].get("programa"))[:100], "por": "mesmo programa (curadoria)"})
        for lid in [l for l in ids[1:] if l not in mesmos]:
            m = por_id[lid]
            m["historico"] = [h for h in m.get("historico") or [] if not (isinstance(h, dict) and str(h.get("id")) == oid)]
            m["edicoes"] = len(m["historico"])
            if m.get("atual") == oid:
                m.pop("atual", None)
        if [l for l in ids[1:] if l not in mesmos]:
            rel["retirados"].append({"oportunidade": oid, "fica_em": ids[0], "saiu_de": [l for l in ids[1:] if l not in mesmos]})
    ms = [m for m in ms if m["id"] not in sai]; por_id = {m["id"]: m for m in ms}

    # 4 · ids_juntados sem repetição
    for m in ms:
        j = m.get("ids_juntados") or []
        if len(j) != len(set(j)):
            m["ids_juntados"] = list(dict.fromkeys(j)); rel["ids_juntados_limpos"] += 1

    li = livros_de()
    rel["resumo"] = {"livros_antes": len(C.get("motores") or []), "livros_depois": len(ms), "fundidos": len(rel["fundidos"]),
                     "livros_absorvidos": len(sai), "religados": len(rel["religados"]), "oportunidades_desambiguadas": len(rel["retirados"]),
                     "ids_juntados_limpos": rel["ids_juntados_limpos"],
                     "oportunidades_com_mais_de_um_livro_depois": sum(1 for v in li.values() if len(v) > 1)}
    if gravar:
        C["motores"] = ms
        CAT.write_text(json.dumps(C, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")   # 11/10: formato único (compacto)
        LIG.parent.mkdir(parents=True, exist_ok=True); LIG.write_text(json.dumps(L, ensure_ascii=False, indent=1), encoding="utf-8")
        REL.parent.mkdir(parents=True, exist_ok=True); REL.write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")
    return rel


if __name__ == "__main__":
    r = unificar(gravar="--verificar" not in sys.argv)
    print(json.dumps(r["resumo"], ensure_ascii=False, indent=1))
