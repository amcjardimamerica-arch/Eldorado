"""PACOTE DO CONSELHO — a cada 3 dias, o Claude valida o que o Piloto não obteve.

Gera estado/pacote_conselho.md com: o que o Piloto fez nos últimos 3 dias (por nível), o que
ficou sem solução, o RELATÓRIO DE APRENDIZADO E BLOQUEIOS (uma linha por evento), as propostas
que aguardam validação (enquadramentos, rotas sugeridas, extrações), e as perguntas que o
conselho precisa responder. O Claude abre o arquivo, valida, corrige e anota o modelo com que
trabalhou.
"""
from __future__ import annotations
import json
from datetime import date, timedelta
from pathlib import Path
from .nucleo import ROOT, load_json, now_iso, write_json

P = ROOT / "estado/sindico"


def montar(dias: int = 3) -> dict:
    hoje = date.today(); desde = (hoje - timedelta(days=dias)).isoformat()
    rels = sorted(P.glob("relatorio-*.json"))
    rels = [load_json(r) for r in rels if r.stem.split("-", 1)[1] >= desde]
    apr = [json.loads(l) for l in (P / "aprendizado.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()] if (P / "aprendizado.jsonl").exists() else []
    apr = [a for a in apr if a.get("d", "") >= desde]
    mem = [json.loads(l) for l in (P / "memoria_mineracao.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()] if (P / "memoria_mineracao.jsonl").exists() else []
    mem = [m for m in mem if m.get("d", "") >= desde]
    rot = load_json(ROOT / "estado/rotas_sugeridas_ia.json") if (ROOT / "estado/rotas_sugeridas_ia.json").exists() else {"sugestoes": []}
    pend = [s for s in rot.get("sugestoes", []) if s.get("status", "").startswith("a_confirmar")]
    from .fonte_edital import EXTRAIDOS
    enq = []
    for f in EXTRAIDOS.glob("*.json"):
        d = load_json(f)
        for a, v in (d.get("enquadramento_sindico") or {}).items():
            if str(v.get("status", "")).startswith("proposta"):
                enq.append({"edital": d.get("edital_id") or f.stem, "assoc": a, "ganharia": v.get("ganharia"), "faltam": v.get("documentos_faltantes")})
    cfg = load_json(ROOT / "config/sindico.json") if (ROOT / "config/sindico.json").exists() else {}
    L = [f"# Pacote do conselho — validação do Claude ({hoje.isoformat()}, últimos {dias} dias)", "",
         f"Piloto: modelo **{cfg.get('modelo_vencedor') or 'não eleito'}**. Ao responder, o Claude anota o modelo com que trabalhou.", "",
         "## O que o Piloto fez", ""]
    for r in rels:
        L.append(f"- {r.get('em','')[:16]} — {r.get('anuncio','')}")
    if not rels: L.append("- nenhum ciclo concluído no período")
    L += ["", f"## Relatório de aprendizado e bloqueios ({len(apr)})", ""]
    for a in apr[:60]:
        L.append(f"- {a['d']} · nível {a.get('n') or '—'} · **{a['t']}** — tentou: {a['tentou']} · impediu: {a['impediu']} · aprendeu: {a['aprendeu']}")
    if not apr: L.append("- nenhum bloqueio registrado")
    L += ["", f"## Pesquisas autônomas do nível 3 ({len(mem)})", ""]
    for m in mem[:40]:
        L.append(f"- {m['d']} · {m['p']} · {'NEGATIVO' if m.get('neg') else str(m.get('n')) + ' pista(s)'}")
    L += ["", f"## Aguardando validação do conselho", "",
          f"### Rotas e pistas sugeridas ({len(pend)})", ""]
    for s in pend[:40]:
        L.append(f"- {s.get('motor') or s.get('empresa') or s.get('fundo') or s.get('mecanismo') or '—'} → {json.dumps(s.get('tentar') or s.get('onde_procurar') or '', ensure_ascii=False)[:160]}")
    L += ["", f"### Enquadramentos propostos ({len(enq)})", ""]
    for x in enq[:40]:
        L.append(f"- `{x['edital']}` × {x['assoc']} — ganharia: **{x['ganharia']}** · faltam: {x['faltam']}")
    L += ["", "## Perguntas para o conselho", "",
          "1. Quais rotas sugeridas confirmar (entram no catálogo) e quais descartar (entram na memória negativa)?",
          "2. Quais enquadramentos avançam para preparação de documentos e projeto (nível 2)?",
          "3. Que bloqueios exigem ação do titular (coleta local, documento ao órgão, decisão)?",
          "4. O modelo eleito deve continuar? (reexecutar o benchmark se a taxa de propostas inválidas subir)",
          "", "_Ao final, registrar em `estado/sindico/validacoes_claude.jsonl`: data, modelo do Claude, decisões._"]
    (ROOT / "estado/pacote_conselho.md").write_text("\n".join(L), encoding="utf-8")
    (ROOT / "docs/dados/pacote_conselho.md").write_text("\n".join(L), encoding="utf-8")
    res = {"em": now_iso(), "dias": dias, "ciclos": len(rels), "bloqueios": len(apr), "pesquisas": len(mem), "rotas_pendentes": len(pend), "enquadramentos_pendentes": len(enq)}
    write_json(ROOT / "estado/pacote_conselho.json", res)
    return res


if __name__ == "__main__":
    print(json.dumps(montar(), ensure_ascii=False, indent=2))
