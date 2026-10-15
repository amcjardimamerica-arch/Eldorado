#!/usr/bin/env python3
"""INTERRUPÇÃO PARA ANALISE O SISTEMA (titular, 15/10/2026).

Quando a titular pede "Analise o sistema", o fluxo 36:
  1. INTERROMPER  desativa todos os fluxos ativos (menos o próprio 36), para nada regravar nem sobrescrever dados por
                  cima das correções ou da análise enquanto ela roda; grava a lista em estado/analise_pausa.json;
  2. AGUARDAR     espera terminarem as execuções que já estavam em andamento (as em fila ficam na fila);
  3. TESTES       roda só os testes da própria análise (procedimento assistido: cada teste com resultado gravado em
                  estado/analise_testes.json);
  4. (diagnóstico, amostra e registro — passos do fluxo 36)
  5. RETOMAR      reativa exatamente os fluxos que interrompeu (passo com `if: always()`: retoma mesmo se a análise
                  falhar). Se uma análise anterior caiu sem retomar, o INTERROMPER seguinte retoma primeiro.

    python scripts/pausa_analise.py interromper | aguardar [minutos] | testes | retomar
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
PAUSA = ROOT / "estado/analise_pausa.json"
TESTES = ROOT / "estado/analise_testes.json"
REPO = os.environ.get("GITHUB_REPOSITORY", "amcjardimamerica-arch/Eldorado")
PROPRIO = "analise-sistema.yml"
TESTES_DA_ANALISE = ["tests.test_analise_ciclos", "tests.test_diagnostico_sistema"]


def _agora() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def gh(metodo: str, caminho: str):
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    dados = json.dumps({"ref": "main"}).encode() if (metodo == "POST" and caminho.endswith("/dispatches")) else None
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/{caminho}", method=metodo, data=dados,
                                 headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            corpo = r.read()
            return r.status, (json.loads(corpo) if corpo else None)
    except urllib.error.HTTPError as e:
        return e.code, None


def _ler() -> dict:
    try:
        return json.loads(PAUSA.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}


def _gravar(d: dict) -> None:
    PAUSA.parent.mkdir(parents=True, exist_ok=True)
    PAUSA.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def retomar() -> dict:
    d = _ler()
    ok, falha = [], []
    for w in d.get("interrompidos") or []:
        st, _ = gh("PUT", f"actions/workflows/{w['id']}/enable")
        (ok if st in (200, 204) else falha).append(w["arquivo"])
    st, _ = gh("POST", "actions/workflows/motores-da-vez.yml/dispatches") if ok else (None, None)   # 15/10: recupera a passagem perdida
    d.update({"retomado_em": _agora(), "retomados": ok, "falha_ao_retomar": falha, "em_pausa": bool(falha),
              "comando_disparado_na_retomada": st in (200, 204)})
    _gravar(d)
    print(f"retomados {len(ok)}; falha {falha}")
    return d


def interromper() -> dict:
    ant = _ler()
    if ant.get("em_pausa"):                             # análise anterior caiu sem retomar: retoma primeiro
        retomar()
    _, r = gh("GET", "actions/workflows?per_page=100")
    ws = [w for w in (r or {}).get("workflows") or [] if w.get("state") == "active" and not str(w.get("path", "")).endswith(PROPRIO)]
    feitos = []
    for w in ws:
        st, _ = gh("PUT", f"actions/workflows/{w['id']}/disable")
        if st in (200, 204):
            feitos.append({"id": w["id"], "nome": w.get("name"), "arquivo": str(w.get("path", "")).rsplit("/", 1)[-1]})
    d = {"interrompido_em": _agora(), "execucao_da_analise": os.environ.get("GITHUB_RUN_ID"), "interrompidos": feitos, "em_pausa": True}
    _gravar(d)
    print(f"interrompidos {len(feitos)} fluxos")
    return d


def aguardar(minutos: int = 45) -> dict:
    eu = os.environ.get("GITHUB_RUN_ID")
    fim = time.time() + 60 * minutos
    while True:
        _, r = gh("GET", "actions/runs?status=in_progress&per_page=100")
        rodando = [x for x in (r or {}).get("workflow_runs") or [] if str(x.get("id")) != str(eu)]
        if not rodando or time.time() > fim:
            break
        print(f"aguardando {len(rodando)} execução(ões): " + ", ".join(x.get("name", "")[:40] for x in rodando[:5]), flush=True)
        time.sleep(30)
    d = _ler(); d["aguardou_ate"] = _agora(); d["ainda_rodando_ao_fim_da_espera"] = [x.get("name") for x in rodando]
    _gravar(d)
    return d


def testes() -> dict:
    r = subprocess.run([sys.executable, "-m", "unittest", "-v", *TESTES_DA_ANALISE], cwd=ROOT, capture_output=True, text=True, timeout=600)
    linhas = [l for l in r.stderr.splitlines() if " ... " in l]
    res = {"em": _agora(), "modulos": TESTES_DA_ANALISE, "ok": r.returncode == 0,
           "testes": [{"teste": l.split(" ... ")[0].strip(), "resultado": l.split(" ... ")[-1].strip()} for l in linhas],
           "resumo": (r.stderr.strip().splitlines() or [""])[-1]}
    TESTES.parent.mkdir(parents=True, exist_ok=True)
    TESTES.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"testes da análise: {res['resumo']} · {len(res['testes'])} conferidos")
    return res


if __name__ == "__main__":
    acao = sys.argv[1] if len(sys.argv) > 1 else ""
    if acao == "interromper":
        interromper()
    elif acao == "aguardar":
        aguardar(int(sys.argv[2]) if len(sys.argv) > 2 else 45)
    elif acao == "testes":
        sys.exit(0 if testes()["ok"] else 1)
    elif acao == "retomar":
        retomar()
    else:
        print(__doc__)
