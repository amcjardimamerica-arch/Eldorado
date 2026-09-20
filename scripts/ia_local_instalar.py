"""INSTALADOR DA IA LOCAL — llama.cpp + modelo GGUF, para a pasta ia_local/ ou para um pen drive.

Uso (no computador do titular, com internet):
    python scripts/ia_local_instalar.py                      # motor + modelo principal (~2 GB) em ./ia_local
    python scripts/ia_local_instalar.py --leve               # modelo leve (~1 GB), para pen drive / PC modesto
    python scripts/ia_local_instalar.py --destino E:\\eldorado-ia   # instala no pen drive

Depois: ia_local/iniciar.bat (Windows) ou ia_local/iniciar.sh (Linux/macOS) sobe o servidor local.
Nada é instalado no sistema: são arquivos numa pasta; apagar a pasta remove tudo.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "config/ia_local.json").read_text(encoding="utf-8"))


def _plataforma() -> str:
    s = platform.system().lower(); m = platform.machine().lower()
    if s.startswith("win"):
        return "windows-x64"
    if s == "darwin":
        return "macos-arm64" if "arm" in m else "macos-arm64"
    return "linux-x64"


def _baixar(url: str, destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.exists() and destino.stat().st_size > 1_000_000:
        print(f"  já existe: {destino.name} ({destino.stat().st_size/1e6:.0f} MB)"); return
    print(f"  baixando {url.split('/')[-1]} …")
    def _prog(b, bs, total):
        if total > 0 and b % 200 == 0:
            print(f"\r    {b*bs/1e6:7.0f} / {total/1e6:.0f} MB", end="")
    urllib.request.urlretrieve(url, destino, _prog)
    print(f"\r    ok: {destino.stat().st_size/1e6:.0f} MB")


def instalar(destino: Path, leve: bool) -> dict:
    destino.mkdir(parents=True, exist_ok=True)
    plat = _plataforma()
    print(f"IA local do Eldorado — instalando em {destino} ({plat})")
    # 1) motor
    url_m = CFG["motor"]["downloads"][plat]
    pacote = destino / url_m.split("/")[-1]
    _baixar(url_m, pacote)
    motor_dir = destino / "motor"
    if not motor_dir.exists():
        motor_dir.mkdir()
        if pacote.suffix == ".zip":
            with zipfile.ZipFile(pacote) as z: z.extractall(motor_dir)
        else:
            with tarfile.open(pacote) as t: t.extractall(motor_dir)
        # achatar subpasta única
        subs = [p for p in motor_dir.iterdir() if p.is_dir()]
        if len(subs) == 1 and not (motor_dir / "llama-server").exists() and not (motor_dir / "llama-server.exe").exists():
            for p in subs[0].iterdir(): shutil.move(str(p), motor_dir / p.name)
            subs[0].rmdir()
    # 2) lançadores (antes do modelo: se o download do modelo falhar, o titular baixa à mão e a pasta já está pronta)
    mod = CFG["modelos"]["leve" if leve else "principal"]
    modelo = destino / "modelos" / mod["arquivo"]
    srv = "llama-server.exe" if plat.startswith("win") else "llama-server"
    porta = CFG["servidor"]["porta"]; ctx = CFG["servidor"]["contexto"]
    (destino / "iniciar.bat").write_text(
        f'@echo off\r\ncd /d "%~dp0"\r\necho IA local do Eldorado — {mod["nome"]} — http://127.0.0.1:{porta}\r\n'
        f'motor\\{srv} -m "modelos\\{mod["arquivo"]}" --port {porta} --host 127.0.0.1 -c {ctx} --jinja\r\npause\r\n', encoding="utf-8")
    (destino / "iniciar.sh").write_text(
        f'#!/bin/sh\ncd "$(dirname "$0")"\nexport LD_LIBRARY_PATH="$PWD/motor:$LD_LIBRARY_PATH"\n'
        f'echo "IA local do Eldorado — {mod["nome"]} — http://127.0.0.1:{porta}"\n'
        f'./motor/{srv} -m "modelos/{mod["arquivo"]}" --port {porta} --host 127.0.0.1 -c {ctx} --jinja\n', encoding="utf-8")
    try: os.chmod(destino / "iniciar.sh", 0o755)
    except Exception: pass
    # 3) modelo
    try:
        _baixar(mod["url"], modelo)
    except Exception as e:
        print(f"\n  ATENÇÃO: o modelo não baixou ({type(e).__name__}). Baixe manualmente:\n    {mod['url']}\n  e salve em: {modelo}\n  O motor e os lançadores já estão prontos.")
    info = {"instalado_em": str(destino), "plataforma": plat, "motor": CFG["motor"]["release"], "modelo": mod["nome"], "arquivo_modelo": str(modelo),
            "tamanho_total_mb": round(sum(p.stat().st_size for p in destino.rglob("*") if p.is_file()) / 1e6)}
    (destino / "instalacao.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nPronto. Total em disco: {info['tamanho_total_mb']} MB.\nPara ligar: {destino / ('iniciar.bat' if plat.startswith('win') else 'iniciar.sh')}")
    return info


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--destino", default=str(ROOT / CFG["pasta"]))
    ap.add_argument("--leve", action="store_true", help="modelo de ~1 GB (pen drive / PC modesto)")
    a = ap.parse_args()
    instalar(Path(a.destino), a.leve)
