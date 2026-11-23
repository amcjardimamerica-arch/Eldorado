"""23/11/2026 (C-01): a guarda dos bancos entre uma execução e a seguinte (o cache do GitHub Actions).

Sem a guarda, cada execução começava da fotografia de 25/10 e reaplicava os 3,1 milhões de eventos: de 82 a 448 minutos sem
passagem a cada troca (42% do tempo parado desde 19/11). Com ela, a execução restaura os dois bancos e a marca dos eventos
aplicados (dados/aplicados.json) e aplica só os novos. Sem guarda, ou com ela corrompida, tudo segue como antes: a fotografia
e a reaplicação dos eventos — nada passa a depender da guarda para estar certo (R08: são os mesmos dois bancos).

  conferir  PRAGMA quick_check nos bancos restaurados; corrompidos, voltam à fotografia do repositório (e a marca sai)
  preparar  wal_checkpoint(TRUNCATE) antes de salvar (nunca salvar a guarda com o banco aberto pela metade)
  limpar    apaga as guardas anteriores do Actions, mantendo a que acabou de ser salva
"""
from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
import urllib.request
from pathlib import Path

BANCOS = ("dados/biblioteca.db", "dados/cerebro.db")
MARCA = Path("dados/aplicados.json")
PREFIXO = "eldorado-bancos-"


def conferir() -> int:
    ruins = []
    for b in BANCOS:
        if not Path(b).exists():
            continue
        try:
            c = sqlite3.connect(b)
            ok = c.execute("PRAGMA quick_check").fetchone()[0] == "ok"
            c.close()
        except sqlite3.Error:
            ok = False
        if not ok:
            ruins.append(b)
    if ruins:
        print(f"::warning::a guarda dos bancos falhou na conferência ({', '.join(ruins)}): volta à fotografia e remonta dos eventos")
        for b in BANCOS:
            for s in ("-wal", "-shm"):
                Path(b + s).unlink(missing_ok=True)
        subprocess.run(["git", "checkout", "--", *BANCOS], check=False)
        MARCA.unlink(missing_ok=True)
        return 0                                     # a execução segue: remonta dos eventos, como antes da guarda
    print("a guarda dos bancos conferida: " + ", ".join(f"{b} {Path(b).stat().st_size // 1048576} MB" for b in BANCOS if Path(b).exists()))
    return 0


def preparar() -> int:
    for b in BANCOS:
        if Path(b).exists():
            c = sqlite3.connect(b, timeout=120)
            c.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            c.close()
    return 0


def limpar(manter: str) -> int:
    repo, token = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not (repo and token):
        print("sem o repositório ou o token: a limpeza fica para a próxima")
        return 0
    cab = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    url = f"https://api.github.com/repos/{repo}/actions/caches?key={PREFIXO}&per_page=100"
    caches = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=cab), timeout=30).read()).get("actions_caches") or []
    if not any(c["key"] == manter for c in caches):            # a nova não está lá: não apaga nenhuma
        print(f"a guarda {manter} não aparece no Actions: nada é apagado")
        return 0
    apagadas = 0
    for c in caches:
        if c["key"].startswith(PREFIXO) and c["key"] != manter:
            req = urllib.request.Request(f"https://api.github.com/repos/{repo}/actions/caches/{c['id']}", headers=cab, method="DELETE")
            urllib.request.urlopen(req, timeout=30)
            apagadas += 1
    print(f"guardas anteriores apagadas: {apagadas} (fica {manter})")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "conferir":
        sys.exit(conferir())
    if cmd == "preparar":
        sys.exit(preparar())
    if cmd == "limpar":
        sys.exit(limpar(sys.argv[2]))
    print(__doc__)
    sys.exit(2)
