#!/usr/bin/env python3
"""PILOTOS NO BRASIL — Espião e Interceptador com IP brasileiro, sem custo (parecer dos pilotos, 02/10/2026).

Roda no computador do titular (enquanto ligado) ou numa VM gratuita no Brasil (24 h). Usa o MESMO código e o MESMO
modelo local da nuvem (Qwen3-8B pelo llama.cpp — nada de API paga), mas com IP brasileiro:
  • o DuckDuckGo deixa de cortar na 2ª busca (até 30 por voo, 6 s entre elas);
  • prefeituras, TJGO e portais que recusam IP estrangeiro abrem;
  • o que a nuvem não conseguiu (fonte ilegível, busca sem resposta) é retentado aqui primeiro.

Enquanto este programa roda, ele grava um BATIMENTO (estado/sede_pilotos.json) e a nuvem fica em terra; se ele parar,
a nuvem reassume sozinha. Trabalha num CLONE PRÓPRIO do repositório (padrão: ~/Eldorado-pilotos), para nunca mexer na
pasta da coleta do titular. Grava cada voo no GitHub mesclando com o que a nuvem gravou — nunca por cima.

    python scripts/pilotos_brasil.py                       # 55 min, os dois pilotos alternados
    python scripts/pilotos_brasil.py --maquina vm --minutos 55
    python scripts/pilotos_brasil.py --pilotos interceptador

Requisitos na máquina: git (com o login do GitHub já gravado), Python 3 e a IA local (python scripts/ia_local_instalar.py).
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

REPO = "https://github.com/amcjardimamerica-arch/Eldorado.git"
AQUI = Path(__file__).resolve().parents[1]
MODELO = "Qwen3-8B-Q4_K_M.gguf"
CAMINHOS_INTERCEPTADOR = ["docs/dados/interceptador.json", "estado/piloto/fila_resgate.json", "dados/editais/extraidos",
                          "biblioteca_alexandria/oportunidades", "estado/pilotos", "estado/aprendizado", "docs/dados/achados_pilotos.json"]
CAMINHOS_ESPIAO = ["estado/piloto", "estado/pilotos", "estado/aprendizado", "docs/dados/piloto.json", "docs/dados/achados_pilotos.json",
                   "estado/rotas_sugeridas_ia.json", "config/lexico_aprendido.json", "dados/editais/extraidos"]
REGERAR = [["-m", "src.reset_pilotos"], ["-m", "src.skills.aprendizado"], ["-m", "src.achados_pilotos"],
           ["-m", "src.fluxo_oportunidades", "--completo"], ["-m", "src.achados_motores"]]
ADICIONAR = ["estado/sede_pilotos.json", "estado/interceptador", "docs/dados/interceptador.json", "estado/piloto", "estado/pilotos",
             "estado/aprendizado", "dados/editais/extraidos", "biblioteca_alexandria/oportunidades", "docs/dados/piloto.json",
             "docs/dados/achados_pilotos.json", "docs/dados/fluxo_oportunidades.json", "docs/dados/achados_motores.json",
             "biblioteca_alexandria/fontes/motores.json", "config/parametros_pilotos.json", "config/lexico_aprendido.json"]


def sh(cmd: list[str], timeout: int = 600, cwd: Path | None = None, ok=False) -> int:
    print("▶", " ".join(cmd)[:160], flush=True)
    try:
        return subprocess.call(cmd, timeout=timeout, cwd=cwd)
    except subprocess.TimeoutExpired:
        print("  tempo esgotado", flush=True)
        return 124


def _git(*a, timeout=300) -> int:
    return sh(["git", *a], timeout)


def _clone(pasta: Path) -> None:
    if not (pasta / ".git").exists():
        sh(["git", "clone", "-q", REPO, str(pasta)], 1800)
    sh(["git", "-C", str(pasta), "config", "user.name", "pilotos-brasil"])
    sh(["git", "-C", str(pasta), "config", "user.email", "pilotos-brasil@eldorado"])


def _sincronizar() -> None:
    _git("fetch", "-q", "origin", "main")
    _git("reset", "-q", "--hard", "origin/main")      # o clone é só dos pilotos: nada do titular se perde aqui


def _gravar(mensagem: str, copia: Path | None, extras: Path | None) -> bool:
    """Leva o voo ao GitHub: volta ao main mais novo, MESCLA o estado do Interceptador, devolve os arquivos do voo,
    regenera os derivados e envia. Até 5 tentativas."""
    for i in range(5):
        _sincronizar()
        if copia and copia.exists():
            sh([sys.executable, "-m", "src.pilotos_sede", "mesclar-interceptador", str(copia)], 120)
        if extras and extras.exists():
            for arq in extras.rglob("*"):
                if arq.is_file():
                    alvo = Path(arq.relative_to(extras))
                    alvo.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(arq, alvo)
        for r in REGERAR:
            sh([sys.executable, *r], 300)
        for p in ADICIONAR:
            if Path(p).exists():
                _git("add", "-A", "--", p)
        if subprocess.call(["git", "diff", "--cached", "--quiet"]) == 0:
            print("nada a gravar", flush=True)
            return True
        _git("commit", "-q", "-m", mensagem)
        if _git("push", "-q", "origin", "HEAD:main") == 0:
            print(f"gravado ({i + 1})", flush=True)
            return True
        time.sleep(5 * (i + 1))
    return False


def _guardar_copia(caminhos: list[str], tmp: Path) -> Path:
    """Copia o que o voo mudou (antes de voltar ao main)."""
    destino = tmp / "extras"
    mudados = subprocess.run(["git", "status", "--porcelain", "--", *caminhos], capture_output=True, text=True).stdout.splitlines()
    for linha in mudados:
        arq = linha[3:].strip().strip('"')
        if " -> " in arq:
            arq = arq.split(" -> ")[1]
        p = Path(arq)
        if p.is_dir():
            for f in p.rglob("*"):
                if f.is_file():
                    (destino / f).parent.mkdir(parents=True, exist_ok=True); shutil.copy2(f, destino / f)
        elif p.is_file():
            (destino / p).parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p, destino / p)
    return destino


def _batimento(maquina: str, pilotos: list[str], estado: str = "voando") -> None:
    _sincronizar()
    acao = "batimento" if estado == "voando" else "encerrar"
    sh([sys.executable, "-m", "src.pilotos_sede", acao, "--maquina", maquina, "--pilotos", ",".join(pilotos)], 60)
    _git("add", "estado/sede_pilotos.json")
    _git("commit", "-q", "-m", f"pilotos no Brasil ({maquina}): {estado}")
    _git("push", "-q", "origin", "HEAD:main")


def _servidor(porta: int) -> subprocess.Popen | None:
    """Sobe o llama.cpp com o Qwen3-8B (o mesmo da nuvem). Sem a IA local instalada, para com instrução clara."""
    try:
        if urllib.request.urlopen(f"http://127.0.0.1:{porta}/health", timeout=2).status == 200:
            return None                                   # já está no ar
    except Exception:  # noqa: BLE001
        pass
    ia = Path(os.environ.get("ELDORADO_IA_LOCAL") or (AQUI / "ia_local"))
    exe = next((p for p in (ia / "motor/llama-server.exe", ia / "motor/llama-server", Path(os.environ.get("LLAMA_SERVER") or "/nao"))
                if p.exists()), None)
    modelo = next((p for p in (ia / "modelos" / MODELO, Path(os.environ.get("ELDORADO_MODELO") or "/nao")) if p.exists()), None)
    if not exe or not modelo:
        raise SystemExit("IA local não encontrada: rode uma vez  python scripts/ia_local_instalar.py  (llama.cpp + Qwen3-8B, "
                         f"cerca de 5 GB). Procurado em {ia}.")
    env = dict(os.environ, LD_LIBRARY_PATH=str(exe.parent))
    srv = subprocess.Popen([str(exe), "-m", str(modelo), "-c", "16384", "--port", str(porta), "--host", "127.0.0.1", "--jinja",
                            "-t", str(max(2, (os.cpu_count() or 4) - 1))], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(240):
        try:
            if urllib.request.urlopen(f"http://127.0.0.1:{porta}/health", timeout=2).status == 200:
                return srv
        except Exception:  # noqa: BLE001
            time.sleep(1)
    srv.kill()
    raise SystemExit("a IA local não subiu em 4 minutos (memória livre? o Qwen3-8B usa cerca de 6 GB)")


VOO_INTERCEPTADOR = """
import json
from src.ia_local import IALocal, CFG
from src.interceptador import voo
CFG["limites"]["tokens_resposta"] = 1400
CFG["limites"]["tempo_maximo_s"] = 1500
r = voo(IALocal(porta={porta}, timeout=1500))
print(json.dumps({{k: v for k, v in r.items() if k not in ("passos", "itens")}}, ensure_ascii=False)[:1200])
"""
VOO_ESPIAO = """
import json
from src.piloto import ciclo
r = ciclo(porta={porta})
print(json.dumps(r, ensure_ascii=False)[:1200])
"""


def dentro(a) -> int:
    os.environ.update({"ELDORADO_LOCAL_BR": "1", "ELDORADO_VOO_REAL": "1", "PYTHONIOENCODING": "utf-8"})
    pilotos = [p for p in a.pilotos.split(",") if p in ("interceptador", "espiao")]
    fim = time.time() + a.minutos * 60
    srv = _servidor(a.porta)
    voos = 0
    try:
        _batimento(a.maquina, pilotos)
        while time.time() < fim - 300:
            piloto = pilotos[voos % len(pilotos)]
            _sincronizar()
            if Path("estado/interceptador/pausado").exists() and piloto == "interceptador":
                print("Interceptador em terra por ordem do titular", flush=True); voos += 1; continue
            codigo = VOO_INTERCEPTADOR if piloto == "interceptador" else VOO_ESPIAO
            sh([sys.executable, "-c", codigo.format(porta=a.porta)], 1800)
            with tempfile.TemporaryDirectory() as t:
                tmp = Path(t)
                copia = None
                if piloto == "interceptador" and Path("estado/interceptador").exists():
                    copia = tmp / "interceptador"; shutil.copytree("estado/interceptador", copia)
                extras = _guardar_copia(CAMINHOS_INTERCEPTADOR if piloto == "interceptador" else CAMINHOS_ESPIAO, tmp)
                sh([sys.executable, "-m", "src.pilotos_sede", "batimento", "--maquina", a.maquina, "--pilotos", ",".join(pilotos)], 60)
                (extras / "estado").mkdir(parents=True, exist_ok=True)
                shutil.copy2("estado/sede_pilotos.json", extras / "estado/sede_pilotos.json")
                _gravar(f"pilotos no Brasil ({a.maquina}): {piloto} {time.strftime('%Y-%m-%d %H:%M')}", copia, extras)
            voos += 1
    finally:
        try:
            _batimento(a.maquina, pilotos, "encerrado")
        finally:
            if srv:
                srv.kill()
    print(f"concluído: {voos} voo(s) no Brasil ({a.maquina})", flush=True)
    return 0


def _garantir_navegador() -> None:
    """03/10 (titular): o navegador dos Pilotos (src/navegador_local.py). Uma vez só: instala o Playwright; no Windows
    usa o Edge que já existe; sem ele, baixa o Chromium. Se falhar, os Pilotos voam como antes (sem navegador)."""
    try:
        import playwright  # noqa: F401
        return
    except Exception:  # noqa: BLE001
        pass
    sh([sys.executable, "-m", "pip", "install", "--quiet", "playwright"], timeout=900, ok=True)
    edge = any(Path(p).exists() for p in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                                           r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"))
    if not edge:
        sh([sys.executable, "-m", "playwright", "install", "chromium"], timeout=1800, ok=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutos", type=float, default=55)
    ap.add_argument("--pilotos", default="interceptador,espiao")
    ap.add_argument("--maquina", default="computador", choices=["computador", "vm"])
    ap.add_argument("--pasta", default=str(Path.home() / "Eldorado-pilotos"))
    ap.add_argument("--porta", type=int, default=8082)
    ap.add_argument("--dentro", action="store_true", help=argparse.SUPPRESS)
    a = ap.parse_args()
    if a.dentro:
        return dentro(a)
    _garantir_navegador()
    pasta = Path(a.pasta)
    _clone(pasta)
    sh(["git", "-C", str(pasta), "fetch", "-q", "origin", "main"])
    sh(["git", "-C", str(pasta), "reset", "-q", "--hard", "origin/main"])
    env = dict(os.environ, ELDORADO_IA_LOCAL=os.environ.get("ELDORADO_IA_LOCAL") or str(AQUI / "ia_local"))
    return subprocess.call([sys.executable, "scripts/pilotos_brasil.py", "--dentro", "--minutos", str(a.minutos), "--pilotos", a.pilotos,
                            "--maquina", a.maquina, "--porta", str(a.porta)], cwd=pasta, env=env)


if __name__ == "__main__":
    sys.exit(main())
