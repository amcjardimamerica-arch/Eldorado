#!/usr/bin/env python3
"""Roda a bateria de testes numa CÓPIA TEMPORÁRIA do repositório.

Por quê: cada módulo do sistema acha a raiz pela própria pasta (Path(__file__).parents[1]). Rodando a bateria
dentro do repositório, os testes gravavam nos livros, em estado/ e em docs/dados (36 arquivos por rodada,
medido em 17/10/2026). Copiando os arquivos para uma pasta temporária e rodando lá, todos os módulos passam a
enxergar a cópia como raiz — e o repositório real fica intocado.

Uso:
    python3 scripts/testar.py                      # bateria inteira, isolada
    python3 scripts/testar.py -- tests/test_cartorio.py -k portao   # repassa argumentos ao pytest
    python3 scripts/testar.py -j 4                 # 4 processos, CADA UM com a sua cópia
    python3 scripts/testar.py --falhas /tmp/f.txt  # grava a lista de testes que falharam
    python3 scripts/testar.py --manter             # não apaga a cópia (para investigar)
    python3 scripts/testar.py --comando "python scripts/rodar_testes.py"   # qualquer comando, dentro da cópia

Garantia: o `git status` do repositório real é lido antes e depois; se mudou, o script termina com erro.
"""
from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
MARCA = ".copia_de_teste"          # arquivo que identifica a cópia isolada


def estado_git(raiz: Path) -> str:
    """Retrato do repositório real: arquivos alterados + conteúdo deles (hash), para pegar até regravação idêntica."""
    r = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all", "--ignored"], cwd=raiz,
                       capture_output=True, text=True, check=True)
    return r.stdout


def _git(raiz: Path, *args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=raiz, capture_output=True, check=True).stdout


def _lista(saida: bytes) -> list[str]:
    return [p for p in saida.decode("utf-8").split("\0") if p]


def montar_copia(raiz: Path, destino: Path) -> int:
    """Cópia FIEL e isolada: clone local compartilhado (só LÊ os objetos do original) no mesmo commit, mais as
    edições locais por cima (alterados, novos não ignorados e apagados). A cópia é um repositório git de verdade,
    porque há código que consulta o git (ex.: src/uso_arquivos.py usa `git ls-files`). Sem remoto: nada sai dela."""
    head = _git(raiz, "rev-parse", "HEAD").decode().strip()
    subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout", str(raiz), str(destino)], check=True)
    _git(destino, "checkout", "-q", "--detach", head)
    _git(destino, "remote", "remove", "origin")
    n = 0
    for rel in _lista(_git(raiz, "ls-files", "-z", "--modified", "--others", "--exclude-standard")):
        if (raiz / rel).is_file():
            (destino / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(raiz / rel, destino / rel)
            n += 1
    for rel in _lista(_git(raiz, "ls-files", "-z", "--deleted")):
        (destino / rel).unlink(missing_ok=True)
    (destino / MARCA).write_text(str(raiz), encoding="utf-8")
    return n


IGNORAR_PADRAO = ["tests/test_system.py",            # suíte de sistema: roda à parte
                  "tests/test_validacao_mapa.py"]    # passa de 100 s: tratado no item 2 do plano de testes


def arquivos_de_teste(extras: list[str]) -> list[str]:
    alvos = [x for x in extras if not x.startswith("-") and x.startswith("tests")]
    if alvos:
        return alvos
    return sorted(str(p.relative_to(RAIZ)) for p in (RAIZ / "tests").glob("test_*.py")
                  if str(p.relative_to(RAIZ)) not in IGNORAR_PADRAO)


def repartir(arquivos: list[str], n: int) -> list[list[str]]:
    """Reparte por peso (tempo medido em tests/duracoes.json quando existir; senão, tamanho do arquivo)."""
    try:
        import json
        dur = json.loads((RAIZ / "tests/duracoes.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        dur = {}
    peso = {a: float(dur.get(a, (RAIZ / a).stat().st_size / 2000 if (RAIZ / a).exists() else 1)) for a in arquivos}
    grupos, cargas = [[] for _ in range(n)], [0.0] * n
    for a in sorted(arquivos, key=lambda x: -peso[x]):
        k = cargas.index(min(cargas))
        grupos[k].append(a); cargas[k] += peso[a]
    return [g for g in grupos if g]


def falhas_do_junit(xml: Path) -> list[str]:
    """Ids no formato 'tests/test_x.py::Classe::metodo' de cada teste com falha ou erro."""
    if not xml.exists():
        return []
    out = []
    for caso in ET.parse(xml).getroot().iter("testcase"):
        if caso.find("failure") is not None or caso.find("error") is not None:
            mod = (caso.get("classname") or "").split(".")
            arq = "/".join(mod[:2]) + ".py" if len(mod) >= 2 else caso.get("file", "?")
            out.append("::".join([arq, *mod[2:], caso.get("name", "?")]))
    return sorted(set(out))


def contagem_junit(xml: Path) -> dict:
    c = {"testes": 0, "falhas": 0, "erros": 0, "pulados": 0, "tempo": 0.0}
    if xml.exists():
        for su in ET.parse(xml).getroot().iter("testsuite"):
            c["testes"] += int(su.get("tests", 0)); c["falhas"] += int(su.get("failures", 0))
            c["erros"] += int(su.get("errors", 0)); c["pulados"] += int(su.get("skipped", 0))
            c["tempo"] += float(su.get("time", 0))
    return c


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manter", action="store_true", help="não apaga as cópias temporárias ao terminar")
    ap.add_argument("--comando", help="roda este comando (texto) dentro de UMA cópia, em vez da bateria")
    ap.add_argument("-j", "--paralelo", type=int, default=1, help="processos; cada um com a SUA cópia")
    ap.add_argument("--falhas", help="grava aqui a lista de testes que falharam (um id por linha)")
    ap.add_argument("--junit", help="copia aqui o relatório JUnit unificado do último grupo (ou do único)")
    ap.add_argument("extras", nargs=argparse.REMAINDER, help="argumentos repassados ao pytest (depois de --)")
    a = ap.parse_args(argv)
    extras = [x for x in a.extras if x != "--"]

    antes = estado_git(RAIZ)
    base = Path(tempfile.mkdtemp(prefix="eldorado_testes_"))
    env = dict(os.environ, ELDORADO_COPIA_DE_TESTE="1", PYTHONDONTWRITEBYTECODE="1")
    rc_final = 0
    try:
        if a.comando:
            import shlex
            copia = base / "Eldorado"
            montar_copia(RAIZ, copia)
            rc_final = subprocess.run(shlex.split(a.comando), cwd=copia, env=env).returncode
        else:
            arquivos = arquivos_de_teste(extras)
            opcoes = [x for x in extras if not x.startswith("tests")]
            grupos = repartir(arquivos, max(1, a.paralelo))
            t0 = time.time()
            procs = []
            modelo = base / "modelo" / "Eldorado"
            montar_copia(RAIZ, modelo)                 # um checkout; as demais cópias saem desta (5x mais rápido)
            for i, grupo in enumerate(grupos):
                copia = base / f"g{i}" / "Eldorado"
                copia.parent.mkdir(parents=True)
                subprocess.run(["cp", "-a", str(modelo), str(copia)], check=True)
                xml = base / f"g{i}.xml"
                log = open(base / f"g{i}.log", "w", encoding="utf-8")
                cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rfE",
                       f"--junitxml={xml}", *opcoes, *grupo]
                procs.append((i, subprocess.Popen(cmd, cwd=copia, env=env, stdout=log, stderr=subprocess.STDOUT), log, xml))
            print(f"[isolamento] {len(grupos)} cópia(s) prontas em {time.time() - t0:.1f} s; "
                  f"{len(arquivos)} arquivos de teste", flush=True)
            total = {"testes": 0, "falhas": 0, "erros": 0, "pulados": 0}
            falhas: list[str] = []
            for i, p, log, xml in procs:
                rc = p.wait(); log.close()
                if rc not in (0, 1):
                    rc_final = rc_final or rc
                    print(f"[isolamento] grupo {i} terminou com código {rc}; registro:", flush=True)
                    print((base / f"g{i}.log").read_text(encoding="utf-8")[-4000:])
                c = contagem_junit(xml)
                for k in total:
                    total[k] += c[k]
                falhas += falhas_do_junit(xml)
                if a.paralelo == 1:
                    print((base / f"g{i}.log").read_text(encoding="utf-8")[-20000:])
            falhas = sorted(set(falhas))
            print(f"[bateria] {total['testes']} testes · {total['falhas']} falhas · {total['erros']} erros · "
                  f"{total['pulados']} pulados · {time.time() - t0:.0f} s", flush=True)
            for f in falhas:
                print("   FALHOU", f)
            if a.falhas:
                Path(a.falhas).write_text("".join(f + "\n" for f in falhas), encoding="utf-8")
            if falhas:
                rc_final = rc_final or 1
    finally:
        depois = estado_git(RAIZ)
        if a.manter:
            print(f"[isolamento] cópias mantidas em {base}")
        else:
            shutil.rmtree(base, ignore_errors=True)
    if antes != depois:
        print("[isolamento] ERRO: o repositório real mudou durante a bateria:", file=sys.stderr)
        for linha in sorted(set(antes.splitlines()) ^ set(depois.splitlines())):
            print("   ", linha, file=sys.stderr)
        return 3
    print("[isolamento] repositório real intocado (git status idêntico antes e depois)")
    return rc_final


if __name__ == "__main__":
    sys.exit(main())
