"""Restauração dos livros retirados em massa do catálogo às 02:28 de 17/10/2026 (titular, 17/10).

Fonte: o catálogo de 17/10 02:09 (commit 29c5d199c, 2.010 livros), guardado em
biblioteca_alexandria/livros/_acervo/restauracao/catalogo_2026-10-17_0209.json (só os livros que faltam).
--montar   extrai do histórico do GitHub os livros que faltam (uma vez; precisa do git com esse commit)
--aplicar  devolve ao catálogo os que ainda faltam (idempotente; roda no fechamento de cada passagem)
Ficam de fora: o que o Claude no Chrome eliminou (ruído, fora do perfil), o que o portão barra hoje e o que já tem outro
livro com o mesmo programa e órgão (não cria duplicata).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
CAT = ROOT / "biblioteca_alexandria/fontes/motores.json"
REF = ROOT / "biblioteca_alexandria/livros/_acervo/restauracao/catalogo_2026-10-17_0209.json"
COMMIT = "29c5d199c"


def _chave(x: dict) -> str:
    return re.sub(r"[^a-z0-9]", "", f"{x.get('programa')}{x.get('orgao')}".lower())[:80]


def _eliminados() -> set:
    try:
        V = json.loads((ROOT / "biblioteca_alexandria/livros/_acervo/editais/vereditos_revisao.json").read_text(encoding="utf-8"))["vereditos"]
    except Exception:  # noqa: BLE001
        return set()
    return {i for i, v in V.items() if (v or {}).get("veredito") in ("ruido", "fora_perfil")}


def montar() -> dict:
    ant = json.loads(subprocess.run(["git", "show", f"{COMMIT}:biblioteca_alexandria/fontes/motores.json"], cwd=ROOT,
                                    capture_output=True, text=True, check=True).stdout)["motores"]
    hoje = {x.get("id") for x in json.loads(CAT.read_text(encoding="utf-8"))["motores"]}
    falt = [x for x in ant if x.get("id") not in hoje]
    REF.parent.mkdir(parents=True, exist_ok=True)
    REF.write_text(json.dumps({"origem": f"catálogo de 17/10 02:09 ({COMMIT})", "livros": falt}, ensure_ascii=False,
                              separators=(",", ":")), encoding="utf-8")
    return {"no_catalogo_de_0209": len(ant), "faltam_hoje": len(falt)}


def aplicar(gravar: bool = True) -> dict:
    if not REF.exists():
        return {"restauracao": "sem referência"}
    from src.porta_oportunidade import motivo_para_nao_guardar
    ref = json.loads(REF.read_text(encoding="utf-8"))["livros"]
    C = json.loads(CAT.read_text(encoding="utf-8")); L = C.setdefault("motores", [])
    ids = {x.get("id") for x in L}; chaves = {_chave(x) for x in L}; elim = _eliminados()
    st = {"devolvidos": 0, "ja_estavam": 0, "eliminados_pelo_chrome": 0, "barrados_pelo_portao": 0, "ja_tem_livro_igual": 0}
    for x in ref:
        if x.get("id") in ids:
            st["ja_estavam"] += 1; continue
        ops = set(map(str, (x.get("coleta") or {}).keys())) | {str(h.get("id")) for h in x.get("historico") or [] if isinstance(h, dict)}
        if ops and ops <= elim:
            st["eliminados_pelo_chrome"] += 1; continue
        if motivo_para_nao_guardar({"titulo": x.get("programa"), "orgao": x.get("orgao"), "uf": x.get("uf"),
                                    "url": x.get("pagina")}) and not x.get("historico"):
            st["barrados_pelo_portao"] += 1; continue
        if _chave(x) in chaves:                        # junta histórico e coleta ao livro igual (não cria duplicata)
            alvo = next(y for y in L if _chave(y) == _chave(x))
            hid = {str(h.get("id")) for h in alvo.get("historico") or [] if isinstance(h, dict)}
            novos_h = [h for h in x.get("historico") or [] if isinstance(h, dict) and str(h.get("id")) not in hid]
            novos_c = {k: v for k, v in (x.get("coleta") or {}).items() if k not in (alvo.get("coleta") or {})}
            if novos_h or novos_c:
                alvo.setdefault("historico", []).extend(novos_h); alvo.setdefault("coleta", {}).update(novos_c)
                st["juntados_ao_livro_igual"] = st.get("juntados_ao_livro_igual", 0) + 1
            else:
                st["ja_tem_livro_igual"] += 1
            continue
        L.append({**x, "restaurado_em": "2026-10-17", "restaurado_de": COMMIT}); ids.add(x.get("id")); chaves.add(_chave(x))
        st["devolvidos"] += 1
    if gravar and (st["devolvidos"] or st.get("juntados_ao_livro_igual")):
        CAT.write_text(json.dumps(C, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return st


if __name__ == "__main__":
    print(json.dumps(montar() if "--montar" in sys.argv else aplicar(gravar="--simular" not in sys.argv), ensure_ascii=False))
