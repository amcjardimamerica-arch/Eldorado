"""TESTE DE ACIONAMENTO DE CADA MOTOR (titular, 02/10/2026).

Percorre os motores NA ORDEM DO PAINEL (config/ordem_motores.json) e aciona UM POR VEZ: o próximo só começa quando o
atual termina e o relatório dele é gravado. Cada tipo é acionado pelo seu caminho:
  sensor (diários, legislativo, Judiciário, MP, portais…) → src.sensores.ler(sensor)
  motor por site (site-…)                                  → rodada dos indexadores só daquele site (forçada)
  Motor Incentivos Fiscais / Patrocínio Privado             → as rotinas de empresas (com limite de tempo)
  Piloto - Espião / Piloto - Interceptador                  → dispara o voo (fluxo do GitHub) e espera terminar
O teste NÃO grava dados de produção: o fluxo só envia o relatório (docs/relatorios/teste-acionamento/).
Uso: python3 scripts/testar_acionamento.py [--motores id1,id2] [--limite-s 900]
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PASTA = ROOT / "docs/relatorios/teste-acionamento"
PILOTOS = {"piloto-aberto": "piloto.yml", "piloto-interceptador": "interceptador.yml"}
EMPRESAS = {"motor-gife": ["python", "-m", "src.incentivos_empresas"], "motor-patrocinio": ["python", "-m", "src.patrocinios"]}

LER_SENSOR = r'''
import json, sys
from src.sensores import registro, ler
mid = sys.argv[1]
s = next((x for x in registro() if x["id"] in (mid, "plat-" + mid)), None)
if s is None:
    print(json.dumps({"situacao": "não encontrado no registro de sensores"})); sys.exit(0)
r = ler(s)
d = r.get("diagnostico") or {}
print(json.dumps({"sensor": s["id"], "achados": len(r.get("achados") or []), "falhas": len(r.get("falhas") or []),
                  "falhas_exemplo": [str(f.get("causa") or f.get("erro"))[:120] for f in (r.get("falhas") or [])[:3]],
                  "paginas": d.get("paginas_lidas"), "motivo_zero": str(d.get("motivo_zero") or "")[:200],
                  "exige_brasil": bool(r.get("pulado_exige_brasil")), "vereditos": d.get("vereditos")}, ensure_ascii=False))
'''
LER_SITE = r'''
import json, sys
from src.indexadores import motor as M
mid = sys.argv[1]
cat = M.catalogo()
sites = [s["id"] for s in cat["sites"] if s.get("motor") == mid]
r = M.rodada(sites=sites, forcar=True, gravar=False)
est = {k: v for k, v in (r.get("sites") or {}).items()}
print(json.dumps({"sites": sites, "lidos": r.get("lidos"), "detalhe": est, "requisicoes": r.get("requisicoes")}, ensure_ascii=False, default=str))
'''


def _rodar(cmd: list[str], limite: int) -> tuple[int | None, str, str]:
    try:
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=limite)
        return p.returncode, p.stdout[-6000:], p.stderr[-1500:]
    except subprocess.TimeoutExpired as e:
        return None, (e.stdout or "")[-2000:] if isinstance(e.stdout, str) else "", "estourou o limite de tempo"


def _gh(metodo: str, caminho: str, corpo: dict | None = None) -> dict:
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY", "amcjardimamerica-arch/Eldorado")
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}{caminho}", method=metodo,
                                 data=json.dumps(corpo).encode() if corpo is not None else None,
                                 headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        b = r.read()
    return json.loads(b) if b else {}


def _piloto(fluxo: str, limite: int) -> dict:
    """Dispara o voo e ESPERA terminar (o próximo motor só começa depois)."""
    antes = datetime.now(timezone.utc).isoformat(timespec="seconds")
    _gh("POST", f"/actions/workflows/{fluxo}/dispatches", {"ref": "main"})
    fim = time.monotonic() + limite; run = None
    while time.monotonic() < fim:
        time.sleep(30)
        rs = (_gh("GET", f"/actions/workflows/{fluxo}/runs?per_page=5&event=workflow_dispatch").get("workflow_runs") or [])
        run = next((r for r in rs if r["created_at"] >= antes[:19]), run)
        if run and run.get("status") == "completed":
            return {"voo": run["id"], "conclusao": run.get("conclusion"), "inicio": run["created_at"], "fim": run["updated_at"]}
    return {"voo": (run or {}).get("id"), "conclusao": "não terminou no limite do teste", "situacao_do_voo": (run or {}).get("status")}


def ordem() -> list[str]:
    pos = json.loads((ROOT / "config/ordem_motores.json").read_text(encoding="utf-8"))["posicoes"]
    return [k for k, _ in sorted(pos.items(), key=lambda kv: kv[1])]


def veredito(tipo: str, rc, saida: dict) -> str:
    if rc is None:
        return "FALHOU — estourou o tempo"
    if tipo == "piloto":
        return "OK — voou" if saida.get("conclusao") == "success" else f"ATENÇÃO — voo: {saida.get('conclusao')}"
    if rc != 0:
        return "FALHOU — erro ao acionar"
    if tipo == "site":
        d = list((saida.get("detalhe") or {}).values())
        if not d:
            return "OK — fora da rota da nuvem (assistida ou ponte)"
        return "OK — leu" if any((x.get("lidas") or 0) > 0 for x in d) else "ATENÇÃO — acionou mas não leu: " + "; ".join(sum((x.get("falhas") or [] for x in d), []))[:160]
    if tipo == "sensor":
        if saida.get("situacao"):
            return "ATENÇÃO — " + saida["situacao"]
        if saida.get("exige_brasil"):
            return "OK — exige IP brasileiro (lido pela coleta no computador)"
        return "OK — leu" if not saida.get("falhas") or saida.get("paginas") else f"ATENÇÃO — {saida.get('falhas')} falha(s)"
    return "OK"


def run(motores: list[str] | None = None, limite: int = 900) -> list[dict]:
    PASTA.mkdir(parents=True, exist_ok=True)
    dia = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    arq_j, arq_m = PASTA / f"{dia}.json", PASTA / f"{dia}.md"
    rel = []
    lista = motores or ordem()
    for n, mid in enumerate(lista, 1):
        t0 = time.monotonic(); ini = datetime.now(timezone.utc).isoformat(timespec="seconds")
        if mid in PILOTOS:
            tipo = "piloto"
            try:
                saida, rc = _piloto(PILOTOS[mid], 3600), 0
            except Exception as e:  # noqa: BLE001
                saida, rc = {"erro": f"{type(e).__name__}: {e}"[:200]}, 1
        elif mid in EMPRESAS:
            tipo = "empresas"
            rc, out, err = _rodar(EMPRESAS[mid], limite); saida = {"saida": out[-800:], "erro": err[-400:]}
        elif mid.startswith("site-"):
            tipo = "site"
            rc, out, err = _rodar([sys.executable, "-c", LER_SITE, mid], limite)
            try:
                saida = json.loads(out.strip().splitlines()[-1])
            except Exception:  # noqa: BLE001
                saida = {"saida": out[-600:], "erro": err[-600:]}
        else:
            tipo = "sensor"
            rc, out, err = _rodar([sys.executable, "-c", LER_SENSOR, mid], limite)
            try:
                saida = json.loads(out.strip().splitlines()[-1])
            except Exception:  # noqa: BLE001
                saida = {"saida": out[-600:], "erro": err[-600:]}
        r = {"ordem": n, "motor": mid, "tipo": tipo, "inicio": ini, "segundos": round(time.monotonic() - t0), "veredito": veredito(tipo, rc, saida), "resultado": saida}
        rel.append(r)
        # relatório gravado ANTES do próximo motor começar
        arq_j.write_text(json.dumps({"em": ini, "regra": __doc__.split("Uso:")[0].strip(), "motores": rel}, ensure_ascii=False, indent=1), encoding="utf-8")
        linhas = [f"# Teste de acionamento — {dia}", "", f"{len(rel)} de {len(lista)} motores testados, um por vez, na ordem do painel.", "",
                  "| nº | motor | tipo | tempo | resultado |", "|---|---|---|---|---|"]
        linhas += [f"| {x['ordem']} | {x['motor']} | {x['tipo']} | {x['segundos']} s | {x['veredito']} |" for x in rel]
        arq_m.write_text("\n".join(linhas) + "\n", encoding="utf-8")
        print(f"[{n}/{len(lista)}] {mid}: {r['veredito']} ({r['segundos']} s)", flush=True)
    return rel


if __name__ == "__main__":
    a = sys.argv
    mot = a[a.index("--motores") + 1].split(",") if "--motores" in a else None
    lim = int(a[a.index("--limite-s") + 1]) if "--limite-s" in a else 900
    run(mot, lim)
