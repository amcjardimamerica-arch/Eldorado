"""Ferramenta HUMANA de verificação: promove ou rebaixa o status de uma
oportunidade com trilha de auditoria. É o elo que autoriza o Farol.

Uso:
  python scripts/promover.py listar [capturada|pista...]        # pendentes
  python scripts/promover.py ID verificada_primaria --por "Nome" [--nota "..."]
  python scripts/promover.py ID descartada --por "Nome" --nota "motivo"
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.nucleo import ROOT, append_jsonl, carregar_oportunidades, gravar_oportunidades, now_iso

STATUS_HUMANOS = [
    "verificada_primaria", "verificada_dupla", "elegivel", "inelegivel",
    "em_preparacao", "submetida", "selecionada", "nao_selecionada",
    "em_execucao", "prestacao_de_contas", "encerrada", "descartada", "capturada",
]

def promover(oid: str, status: str, por: str, nota: str | None = None, registros: dict | None = None) -> dict:
    if status not in STATUS_HUMANOS:
        raise SystemExit(f"status inválido; use um de: {', '.join(STATUS_HUMANOS)}")
    proprio = registros is None
    registros = carregar_oportunidades() if proprio else registros
    if oid not in registros:
        raise SystemExit(f"oportunidade {oid} não encontrada na base")
    item = registros[oid]
    anterior = item.get("status")
    item.update({"status": status, "verificado_em": now_iso(), "verificado_por": por})
    if nota:
        item.setdefault("notas", []).append({"em": now_iso(), "por": por, "texto": nota})
    if proprio:
        gravar_oportunidades(registros)
        append_jsonl(ROOT / "estado/auditoria.jsonl", {
            "evento": "promocao_status", "oportunidade": oid,
            "de": anterior, "para": status, "por": por, "em": now_iso(),
        })
    return item

def listar(filtro: str | None) -> None:
    registros = carregar_oportunidades()
    linhas = [x for x in registros.values() if not filtro or (x.get("status") or "").startswith(filtro)]
    linhas.sort(key=lambda x: (x.get("status", ""), x.get("coletado_em", "")))
    for x in linhas:
        print(f'{x["id"]}  {x.get("status", "?"):28} {x.get("uf") or "BR":5} {x.get("titulo", "")[:80]}')
        print(f'{"":2}{x.get("url", "")}')
    print(f"total: {len(linhas)}")

if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "listar":
        listar(sys.argv[2] if len(sys.argv) > 2 else None); raise SystemExit(0)
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("id"); p.add_argument("status")
    p.add_argument("--por", default="revisao_humana")
    p.add_argument("--nota", default=None)
    a = p.parse_args()
    item = promover(a.id, a.status, a.por, a.nota)
    print(json.dumps({"id": item["id"], "status": item["status"], "titulo": item.get("titulo")}, ensure_ascii=False, indent=2))
