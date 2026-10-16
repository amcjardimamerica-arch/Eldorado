"""DECISÕES DA TITULAR NO PAINEL → LIVRO (12/10/2026) — docs/prompts/PROMPT-FICHA-DA-OPORTUNIDADE-2026-10-12.md

Entrada: estado/decisoes_editais.json, exportado pelo painel (janela da oportunidade: «Inscrição realizada» e
«Descartar»). Nada é apagado:
  descartado → o livro da oportunidade recebe `revisao_exclusao` (pedido em, por, oportunidade, título, motivo,
               situação "aguardando análise do Claude") e entra na fila docs/dados/fila_revisao_exclusao.json; o
               Claude decide se exclui ou não
  inscrito   → o livro recebe `inscricao_realizada` (em, oportunidade)
Se a titular recuperar a oportunidade (a decisão sai do arquivo), a sinalização feita pelo painel é retirada.
O repositório único lê as mesmas decisões: a oportunidade decidida sai das abertas (marca "arquivada").
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECISOES = ROOT / "estado/decisoes_editais.json"
REP = ROOT / "biblioteca_alexandria/livros/_vistas/repositorio_unico.json"
CATALOGO = ROOT / "biblioteca_alexandria/fontes/motores.json"
FILA = ROOT / "docs/dados/fila_revisao_exclusao.json"
POR = "titular (painel)"


def _j(p: Path, padrao=None):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao if padrao is not None else {}


def decisoes() -> dict:
    d = _j(DECISOES, {}) or {}
    return d.get("decisoes") if isinstance(d.get("decisoes"), dict) else {k: v for k, v in d.items() if isinstance(v, dict) and v.get("estado")}


def marca_no_repositorio(ids: list[str], dec: dict | None = None) -> str | None:
    """Usado pelo repositório único: a oportunidade decidida no painel sai das abertas."""
    dec = decisoes() if dec is None else dec
    for i in ids:
        v = dec.get(i) or {}
        if v.get("estado") == "descartado":
            return f"descartada pela titular em {str(v.get('em') or '')[:10]} — aguardando análise do Claude (o livro fica)"
        if v.get("estado") == "inscrito":
            return f"inscrição realizada em {str(v.get('em') or '')[:10]}"
    return None


def run() -> dict:
    dec = decisoes()
    R = (_j(REP, {}).get("registros") or [])
    por_id = {}
    for r in R:
        for i in [r["id"], *(r.get("ids_origem") or [])]:
            por_id[i] = r
    C = _j(CATALOGO, {}) or {}
    livros = {m.get("id"): m for m in (C.get("motores") or [])}
    sinalizados, inscritos, retirados, mudou = [], 0, 0, False
    ativos = set()
    for oid, v in dec.items():
        r = por_id.get(oid); L = livros.get((r or {}).get("livro"))
        if not L:
            continue
        if v.get("estado") == "descartado":
            ativos.add(L["id"])
            if not L.get("revisao_exclusao") or (L["revisao_exclusao"].get("por") == POR and L["revisao_exclusao"].get("oportunidade") != oid):
                L["revisao_exclusao"] = {"pedido_em": v.get("em") or datetime.now(timezone.utc).isoformat(), "por": POR, "oportunidade": oid,
                                         "titulo": v.get("titulo") or (r or {}).get("titulo"), "motivo": v.get("motivo") or "descartada no painel",
                                         "situacao": "aguardando análise do Claude"}
                mudou = True
            sinalizados.append({"livro": L["id"], **L["revisao_exclusao"]})
        elif v.get("estado") == "inscrito" and not L.get("inscricao_realizada"):
            L["inscricao_realizada"] = {"em": v.get("em"), "oportunidade": oid}; inscritos += 1; mudou = True
    for L in livros.values():                      # recuperada no painel: retira a sinalização feita pelo painel
        rx = L.get("revisao_exclusao")
        if rx and rx.get("por") == POR and rx.get("situacao") == "aguardando análise do Claude" and L["id"] not in ativos:
            L.pop("revisao_exclusao"); retirados += 1; mudou = True
    if mudou:
        CATALOGO.write_text(json.dumps(C, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")   # formato único (compacto)
    FILA.write_text(json.dumps({"em": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                                "regra": "descartar no painel não apaga o livro: sinaliza para o Claude analisar a exclusão",
                                "pendentes": sinalizados}, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"decisoes": len(dec), "livros_sinalizados": len(sinalizados), "inscricoes_registradas": inscritos, "sinalizacoes_retiradas": retirados}


def definir(oid: str, estado: str, titulo: str = "") -> dict:
    """12/10: a decisão chega do painel pelo fluxo 33 (sem exportar arquivo). estado: inscrito · descartado · em_andamento
    (em_andamento = recuperar: a decisão sai do arquivo)."""
    d = _j(DECISOES, {}) or {}
    dec = decisoes()
    if estado == "em_andamento":
        dec.pop(oid, None)
    else:
        dec[oid] = {"estado": estado, "em": datetime.now(timezone.utc).replace(microsecond=0).isoformat(), "titulo": titulo[:200],
                    "acao": {"inscrito": "inscrição realizada", "descartado": "descartado"}.get(estado, estado), "por": POR}
    DECISOES.parent.mkdir(parents=True, exist_ok=True)
    DECISOES.write_text(json.dumps({**({k: v for k, v in d.items() if k != "decisoes"} if "decisoes" in d else {}),
                                    "atualizado_em": datetime.now(timezone.utc).replace(microsecond=0).isoformat(), "decisoes": dec},
                                   ensure_ascii=False, indent=1), encoding="utf-8")
    return {"oportunidade": oid, "estado": estado, "decisoes": len(dec)}


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 4 and sys.argv[1] == "definir":
        print(json.dumps(definir(sys.argv[2], sys.argv[3], " ".join(sys.argv[4:])), ensure_ascii=False))
    print(json.dumps(run(), ensure_ascii=False))
