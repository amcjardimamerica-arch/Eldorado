"""SAÚDE DO SISTEMA (titular, 27/09) — o que a tela não mostra, checado sozinho.

Roda ao pouso de cada voo do Interceptador e no monitoramento diário; publica docs/dados/saude.json. O cabeçalho
do painel mostra quantos alertas há e, ao passar o cursor, quais. Checagens:
  arquivos    JSON íntegro em todos os dados publicados e estados
  frescor     cada arquivo do painel dentro do prazo do seu gerador (gerador parado aparece aqui)
  coerência   número do mapa = lista por estado; soma dos estados = total
  gerador     o gerador principal falhou depois da última geração?
  claude      a análise a cada 3 dias está atrasada?
  opressores  duplicados no catálogo
  workflows   algum workflow com as últimas execuções todas em falha ou cancelamento (API do GitHub, no servidor)
"""
from __future__ import annotations

import glob
import json
import os
import subprocess
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAIDA = ROOT / "docs/dados/saude.json"
PRAZOS_H = {"docs/dashboard-dados.js": 3, "docs/dados/fluxo_oportunidades.json": 4, "docs/dados/interceptador.json": 3,
            "docs/dados/esquadrilha.json": 3, "docs/dados/achados_motores.json": 30, "docs/dados/motores.json": 30,
            "docs/dados/ranking_apoiadores.json": 24 * 8, "docs/dados/para_claude.json": 30}


def _idade_h(f: str) -> float | None:
    t = subprocess.run(["git", "log", "-1", "--format=%cI", "--", f], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if not t:
        return None
    return (datetime.now(timezone.utc) - datetime.fromisoformat(t)).total_seconds() / 3600


def _workflows() -> list[str]:
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"); rep = os.environ.get("GITHUB_REPOSITORY", "amcjardimamerica-arch/Eldorado")
    if not tok:
        return []
    def api(u):
        req = urllib.request.Request(f"https://api.github.com/repos/{rep}/{u}", headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read())
    ruins = []
    try:
        for w in api("actions/workflows?per_page=50").get("workflows", []):
            if w.get("state") != "active":
                continue
            rs = api(f"actions/workflows/{w['id']}/runs?per_page=5").get("workflow_runs", [])
            fim = [r for r in rs if r.get("status") == "completed"]
            if len(fim) >= 3 and all(r.get("conclusion") in ("failure", "cancelled", "timed_out") for r in fim):
                ruins.append(f"{w['name']}: últimas {len(fim)} execuções sem sucesso")
    except Exception as e:
        ruins.append(f"não foi possível consultar os workflows ({type(e).__name__})")
    return ruins


def checar() -> dict:
    alertas, ok = [], []
    ruins = []
    for pat in ("docs/dados/*.json", "estado/**/*.json", "config/*.json", "biblioteca_alexandria/fontes/*.json"):
        for f in glob.glob(str(ROOT / pat), recursive=True):
            try:
                json.loads(Path(f).read_text(encoding="utf-8"))
            except Exception:
                ruins.append(os.path.relpath(f, ROOT))
    (alertas.append({"area": "arquivos", "texto": f"{len(ruins)} arquivo(s) de dados corrompido(s): {', '.join(ruins[:4])}"}) if ruins else ok.append("todos os arquivos de dados íntegros"))
    for f, lim in PRAZOS_H.items():
        h = _idade_h(f)
        if h is not None and h > lim:
            alertas.append({"area": "frescor", "texto": f"{os.path.basename(f)} sem atualização há {h:.0f} h (prazo do gerador: {lim} h)"})
    if not any(a["area"] == "frescor" for a in alertas):
        ok.append("todos os arquivos do painel dentro do prazo dos geradores")
    try:
        F = json.loads((ROOT / "docs/dados/fluxo_oportunidades.json").read_text(encoding="utf-8"))
        pu, iu = F["mapa"]["por_uf"], F.get("itens_por_uf") or {}
        div = [k for k in pu if pu[k]["possiveis"] != len(iu.get(k, []))]
        if not (F.get("validacao") or {}).get("aplicada"):
            alertas.append({"area": "mapa", "texto": "o mapa publicado foi gerado SEM a validação individual — o painel mantém o último válido"})
        elif (F.get("validacao") or {}).get("sem_decisao"):
            alertas.append({"area": "mapa", "texto": f"{F['validacao']['sem_decisao']} oportunidade(s) no mapa sem decisão (curadoria)"})
        (alertas.append({"area": "coerência", "texto": f"mapa e lista divergem em {', '.join(div[:5])}"}) if div else ok.append("número do mapa = lista de cada estado"))
    except Exception as e:
        alertas.append({"area": "coerência", "texto": f"fluxo ilegível ({type(e).__name__})"})
    falha = ROOT / "estado/piloto/gerador_painel_falhou.txt"
    if falha.exists():
        h_falha, h_ger = _idade_h("estado/piloto/gerador_painel_falhou.txt"), _idade_h("docs/dashboard-dados.js")
        if h_falha is not None and h_ger is not None and h_falha < h_ger:
            alertas.append({"area": "gerador", "texto": "o gerador principal do painel falhou depois da última geração"})
    try:
        pc = json.loads((ROOT / "docs/dados/para_claude.json").read_text(encoding="utf-8"))
        prox = pc.get("proxima_analise_do_claude")
        if pc.get("a_analisar") and prox and prox < date.today().isoformat():
            alertas.append({"area": "claude", "texto": f"análise do Claude atrasada desde {prox}: {pc['a_analisar']} item(ns) esperando validação ou descarte"})
        elif pc.get("a_analisar"):
            alertas.append({"area": "claude", "texto": f"{pc['a_analisar']} item(ns) esperando a análise do Claude (próxima: {prox})"})
    except Exception:
        pass
    try:
        import re
        C = json.loads((ROOT / "biblioteca_alexandria/fontes/motores.json").read_text(encoding="utf-8")).get("motores", [])
        from collections import Counter
        d = sum(v - 1 for v in Counter(re.sub(r"[^a-z0-9]", "", f"{x.get('programa')}{x.get('orgao')}".lower())[:80] for x in C).values() if v > 1)
        if d:
            alertas.append({"area": "opressores", "texto": f"{d} opressor(es) duplicado(s) no catálogo"})
    except Exception:
        pass
    for w in _workflows():
        alertas.append({"area": "workflows", "texto": w})
    res = {"em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "alertas": alertas, "ok": ok}
    SAIDA.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    return res


if __name__ == "__main__":
    r = checar(); print(json.dumps(r, ensure_ascii=False, indent=1))
