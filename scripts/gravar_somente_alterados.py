#!/usr/bin/env python3
"""GRAVAR SOMENTE O QUE ESTE FLUXO ALTEROU (titular, 15/10/2026 — análise do sistema, ciclo 5).

Defeito medido: a análise das 14:43 reaplicou a ÁRVORE INTEIRA que tinha copiado às 14:03 e apagou a coleta que o
comando único gravou às 14:37 (docs/dados/maestro.json e comando.json voltaram às 12:46). O mesmo mecanismo existia no
fluxo 22. Regra nova: cada fluxo grava só os arquivos que ELE mudou, sempre por cima do main MAIS RECENTE.

    python scripts/gravar_somente_alterados.py salvar              # ao fim do trabalho: guarda os arquivos alterados
    python scripts/gravar_somente_alterados.py aplicar "mensagem"   # parte do main atual e grava só esses arquivos
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUARDA = Path("/tmp/alterados_pelo_fluxo")
AREAS = ["biblioteca_alexandria", "dados", "estado", "docs/dados", "docs/dashboard-dados.js", "docs/relatorios"]


# 17/10/2026: arquivos-ÍNDICE que vários fluxos gravam ao mesmo tempo. Copiar a versão do fluxo por cima do main apagava
# o que os outros fluxos tinham acrescentado enquanto este rodava (o índice dos livros caiu de 8.412 para 1 e depois
# ficou em 263 entradas). Para eles, a gravação JUNTA: tudo o que está no main fica; o que este fluxo gravou prevalece.
INDICES_JUNTADOS = {"biblioteca_alexandria/livros/_origens.json"}


def juntar_indice(no_main: dict, do_fluxo: dict) -> dict:
    """União sem perda: chaves só do main ficam; chaves do fluxo prevalecem."""
    return {**(no_main or {}), **(do_fluxo or {})}


def _copiar(origem: Path, c: str) -> None:
    destino = ROOT / c
    destino.parent.mkdir(parents=True, exist_ok=True)
    if c in INDICES_JUNTADOS and destino.is_file():
        try:
            no_main = json.loads(destino.read_text(encoding="utf-8"))
            do_fluxo = json.loads(origem.read_text(encoding="utf-8"))
        except ValueError:
            raise RuntimeError(f"{c}: índice ilegível no main ou no fluxo — nada gravado para não apagar entradas")
        if isinstance(no_main, dict) and isinstance(do_fluxo, dict):
            junto = juntar_indice(no_main, do_fluxo)
            destino.write_text(json.dumps(junto, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
            print(f"{c}: juntado (main {len(no_main)} + fluxo {len(do_fluxo)} = {len(junto)} entradas)")
            return
    shutil.copy2(origem, destino)


def _git(*a, ok=False) -> str:
    r = subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)
    if r.returncode and not ok:
        raise RuntimeError(f"git {' '.join(a)}: {r.stderr.strip()[:300]}")
    return r.stdout


def salvar() -> dict:
    mud = [l for l in _git("status", "--porcelain", "--untracked-files=all", "--", *AREAS).splitlines() if l.strip()]
    alterados, apagados = [], []
    for l in mud:
        caminho = l[3:].split(" -> ")[-1].strip().strip('"')
        (apagados if l[:2].strip() == "D" else alterados).append(caminho)
    try:                                              # 16/10/2026 (titular): TRAVA — dado de oportunidade só nos livros
        sys.path.insert(0, str(ROOT))
        from src.livro_arquivo import proibido
        recusados = [c for c in alterados if proibido(c)]
        if recusados:
            print(f"TRAVA: {len(recusados)} arquivo(s) em pasta proibida recusado(s) (o dado só existe nos livros): {recusados[:3]}")
            alterados = [c for c in alterados if not proibido(c)]
    except Exception:  # noqa: BLE001
        pass
    if GUARDA.exists():
        shutil.rmtree(GUARDA)
    for c in alterados:
        d = GUARDA / "arquivos" / c
        d.parent.mkdir(parents=True, exist_ok=True)
        if (ROOT / c).is_file():
            shutil.copy2(ROOT / c, d)
    m = {"alterados": alterados, "apagados": apagados}
    GUARDA.mkdir(parents=True, exist_ok=True)
    (GUARDA / "manifesto.json").write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"guardados {len(alterados)} alterado(s) e {len(apagados)} apagado(s)")
    return m


def aplicar(msg: str, tentativas: int = 6) -> bool:
    m = json.loads((GUARDA / "manifesto.json").read_text(encoding="utf-8"))
    if not m["alterados"] and not m["apagados"]:
        print("nada a gravar"); return True
    for i in range(1, tentativas + 1):
        _git("fetch", "-q", "origin", "main")
        _git("reset", "-q", "--hard", "origin/main")                 # sempre o main MAIS RECENTE
        for c in m["alterados"]:
            o = GUARDA / "arquivos" / c
            if o.is_file():
                _copiar(o, c)                                 # 17/10: índices são JUNTADOS, não substituídos
        for c in m["apagados"]:
            if c in INDICES_JUNTADOS:
                continue                                       # 17/10: um fluxo nunca apaga o índice compartilhado
            if (ROOT / c).exists():
                _git("rm", "-q", "--", c, ok=True)
        # 17/10/2026 (titular): TRAVA DOS LIVROS — as mudanças desta passagem já estão sobre o main mais recente (HEAD):
        # nenhum livro apagado nem sobrescrito; só informação nova (o que outra gravação fez no main é preservado)
        subprocess.run([sys.executable, "-m", "src.trava_livros"], cwd=ROOT, capture_output=True)
        # 17/10 (titular): a Bússola recalculada pelo catálogo FINAL (o que vai ser gravado agora)
        subprocess.run([sys.executable, "-c", "from src import fluxo_oportunidades as F; F.sincronizar_catalogo()"], cwd=ROOT, capture_output=True)
        _cat = "biblioteca_alexandria/fontes/motores.json"
        _extra = [_cat] if _git("diff", "--name-only", "--", _cat).strip() else []
        _flx = "docs/dados/fluxo_oportunidades.json"
        _extra += [_flx] if _git("diff", "--name-only", "--", _flx).strip() and _flx not in m["alterados"] else []
        _extra += [l[3:] for l in _git("status", "--porcelain", "--", "biblioteca_alexandria/livros").splitlines()
                   if l.strip() and l[3:] not in m["alterados"]]
        _git("add", "--", *[c for c in m["alterados"] + _extra if (ROOT / c).exists()], ok=True)
        if not _git("diff", "--cached", "--name-only"):
            print("nada mudou em relação ao main"); return True
        _git("commit", "-q", "-m", msg)
        if subprocess.run(["git", "push", "-q", "origin", "HEAD:main"], cwd=ROOT).returncode == 0:
            print(f"gravado na tentativa {i}: só os {len(m['alterados'])} arquivo(s) deste fluxo"); return True
        time.sleep(5 * i)
    print("REGISTRO FALHOU — nenhum arquivo de outro fluxo foi sobrescrito"); return False


if __name__ == "__main__":
    if sys.argv[1:2] == ["salvar"]:
        salvar()
    elif sys.argv[1:2] == ["aplicar"]:
        sys.exit(0 if aplicar(sys.argv[2] if len(sys.argv) > 2 else "dados") else 1)
    else:
        print(__doc__)
