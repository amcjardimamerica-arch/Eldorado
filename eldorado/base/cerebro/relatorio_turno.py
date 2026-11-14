"""14/11/2026 (R55, C8 e C9): o relatório de turno do Espião — gerado na reserva final de cada execução (até 6 h), em
relatorios/espiao/, fora da retenção da operação. Mede o RESULTADO (os achados e os aceitos), não as missões, e traz o placar
de cada rota de busca: quantas vezes respondeu, falhou ou descansou e quantas pistas trouxe."""
from __future__ import annotations

import json
import re
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def medir(cer: sqlite3.Connection, bib: sqlite3.Connection | None, desde: str, ate: str | None = None) -> dict[str, Any]:
    ate = ate or datetime.now(timezone.utc).isoformat()
    linhas = cer.execute("SELECT familia, consulta, resultados, candidatos, achados, rotas FROM espiao_missao WHERE em >= ? AND em < ?",
                         (desde, ate)).fetchall()
    n = len(linhas)
    sem_pista = sum(1 for x in linhas if not x[2])
    placar: dict[str, Counter] = defaultdict(Counter)
    for *_r, rotas in linhas:
        for linha in json.loads(rotas or "[]"):
            nome = linha.split(":")[0]
            m = re.search(r"(\d+) pista\(s\)", linha)
            if m:
                placar[nome]["respondeu"] += 1
                placar[nome]["pistas"] += int(m.group(1))
            elif "falhou" in linha:
                placar[nome]["falhou"] += 1
            elif "descans" in linha:
                placar[nome]["descansando"] += 1
            else:
                placar[nome]["outro"] += 1
    total_pistas = sum(c["pistas"] for c in placar.values()) or 0
    familias = Counter()
    achados_fam = Counter()
    for fam, _q, _res, _cand, ach, _r in linhas:
        familias[fam] += 1
        achados_fam[fam] += ach or 0
    aceitos = None
    if bib is not None:
        try:
            aceitos = bib.execute("SELECT COUNT(*) FROM achado WHERE motor = 'espiao' AND decisao = 'aceito' AND encontrado_em >= ?",
                                  (desde[:10],)).fetchone()[0]
        except sqlite3.Error:
            aceitos = None
    return {
        "desde": desde, "ate": ate, "missoes": n, "sem_pista": sem_pista, "sem_pista_pct": round(100 * sem_pista / n, 1) if n else None,
        "achados": sum(x[4] or 0 for x in linhas), "aceitos": aceitos,
        "rotas_respondendo": sum(1 for c in placar.values() if c["respondeu"]),
        "rota_maior_parte_pct": round(100 * max((c["pistas"] for c in placar.values()), default=0) / total_pistas, 1) if total_pistas else None,
        "placar": {k: dict(v) for k, v in sorted(placar.items(), key=lambda kv: -kv[1]["pistas"])},
        "familias": [{"familia": f, "missoes": u, "achados": achados_fam[f]} for f, u in familias.most_common()],
        "pncp_nas_missoes": sum(1 for *_r, rotas in linhas if '"pncp' in (rotas or "")),
    }


def gerar(cer: sqlite3.Connection, bib: sqlite3.Connection | None, raiz: Path, desde: str) -> Path:
    """Grava o relatório do turno (Markdown e JSON) e devolve o caminho do Markdown."""
    r = medir(cer, bib, desde)
    pasta = Path(raiz) / "relatorios" / "espiao"
    pasta.mkdir(parents=True, exist_ok=True)
    marca = datetime.fromisoformat(r["ate"]).strftime("%Y%m%d-%H%M")
    (pasta / f"turno-{marca}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    linhas = [f"# Relatório de turno do Espião — {r['desde'][:16]} a {r['ate'][:16]} (UTC)", "",
              "| Medida | Valor |", "|---|---|",
              f"| Missões | {r['missoes']} |", f"| Missões sem nenhuma pista | {r['sem_pista']} ({r['sem_pista_pct']}%) |",
              f"| Achados entregues | {r['achados']} |", f"| Achados aceitos na Biblioteca | {r['aceitos'] if r['aceitos'] is not None else '—'} |",
              f"| Rotas de busca respondendo | {r['rotas_respondendo']} |",
              f"| Rota com a maior parte das pistas | {r['rota_maior_parte_pct']}% |",
              f"| Missões com a rota do PNCP | {r['pncp_nas_missoes']} |", "",
              "## Placar das rotas", "", "| Rota | Respondeu | Pistas | Falhou | Descansando |", "|---|---|---|---|---|"]
    linhas += [f"| {k} | {v.get('respondeu', 0)} | {v.get('pistas', 0)} | {v.get('falhou', 0)} | {v.get('descansando', 0)} |" for k, v in r["placar"].items()]
    linhas += ["", "## Famílias", "", "| Família | Missões | Achados |", "|---|---|---|"]
    linhas += [f"| {f['familia']} | {f['missoes']} | {f['achados']} |" for f in r["familias"]]
    md = pasta / f"turno-{marca}.md"
    md.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return md
