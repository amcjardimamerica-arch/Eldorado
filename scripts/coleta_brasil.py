"""COLETA LOCAL (BRASIL) — roda na máquina do titular, só quando ela está ligada.

Lê, com o IP brasileiro do titular, os portais que recusam o robô do GitHub
(TJGO, Câmara e Prefeitura de Goiânia, goias.gov.br, MPGO, Diário de Goiás),
extrai texto dos editais, atualiza o monitor e envia o resultado ao repositório.
Sem custo, sem servidor 24h, sem VPN paga: a "VPN" é a sua própria conexão.

Uso (Windows: clique duas vezes em coleta_brasil.bat; Linux/macOS: python3 scripts/coleta_brasil.py)
"""
from __future__ import annotations
import os, subprocess, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
os.environ["ELDORADO_LOCAL_BR"] = "1"
os.environ.pop("GITHUB_ACTIONS", None)


def run(cmd: list[str], timeout: int = 1800) -> int:
    print("▶", " ".join(cmd)); return subprocess.call(cmd, timeout=timeout)


def main():
    run(["git", "pull", "--rebase", "origin", "main"])
    cfg = json.loads((ROOT / "config/sensores.json").read_text(encoding="utf-8"))
    exige = set((cfg.get("exige_brasil") or {}).get("dominios") or [])
    # só os sensores que exigem Brasil (regulares + 260 pontos) — o resto o GitHub já faz
    from urllib.parse import urlsplit
    sys.path.insert(0, str(ROOT))
    from src.sensores import registro, ler, registrar_dia, ESTADO
    from src.nucleo import load_json, write_json, now_iso
    from datetime import date
    est = load_json(ESTADO) if ESTADO.exists() else {"sensores": {}}
    hoje = date.today().isoformat(); n = 0; achados = 0
    for s in registro():
        hosts = {urlsplit(u).hostname for u in s.get("urls", [])}
        if not hosts or not (hosts & exige):
            continue
        r = ler(s, pausa=1.0); n += 1; achados += len(r.get("achados", []))
        reg = est["sensores"].setdefault(s["id"], {"nome": s["nome"], "leituras": 0, "achados_total": 0})
        reg.update({"ultima": now_iso(), "leituras": reg.get("leituras", 0) + 1, "achados_ultima": len(r["achados"]), "achados_total": reg.get("achados_total", 0) + len(r["achados"]),
                    "saude": (r.get("saude") or []) + (r.get("falhas") or []), "diagnostico": {**(r.get("diagnostico") or {}), "origem": "coleta local (Brasil)"}})
        registrar_dia(s["id"], hoje, r)
        print(f"  {s['nome'][:50]:50s} achados {len(r['achados'])} · {(r.get('diagnostico') or {}).get('motivo_zero') or 'OK'}")
    est["ultima_coleta_local_br"] = {"em": now_iso(), "sensores": n, "achados": achados}
    write_json(ESTADO, est)
    run([sys.executable, "-m", "src.motores"], 900)
    run([sys.executable, "-m", "src.dashboard_dados"], 1800)
    run(["git", "add", "-A", "estado", "dados", "docs", "biblioteca_alexandria"])
    run(["git", "commit", "-m", f"coleta local (Brasil) {hoje}: {n} portais lidos, {achados} achados"])
    run(["git", "pull", "--rebase", "origin", "main"]); run(["git", "push", "origin", "main"])
    print(f"\nConcluído: {n} portais lidos do Brasil, {achados} achados. O painel é publicado pelo GitHub em até 6 horas.")


if __name__ == "__main__":
    main()
