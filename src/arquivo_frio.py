"""ARQUIVO FRIO (titular, 28/09) — roda no servidor do GitHub (workflow 14).

Para cada conjunto de config/arquivo_frio.json ainda presente no repositório:
  1. empacota sem perda e verifica byte a byte (src/compactador.py);
  2. guarda o pacote na Release do GitHub (fora do histórico do repositório) e, se o Drive estiver ligado (rclone,
     segredo RCLONE_CONF), na pasta "Eldorado — Arquivo frio" do Google Drive;
  3. confere que o que foi guardado tem o mesmo tamanho e assinatura;
  4. só então remove os originais do repositório e registra tudo no manifesto (com a lista de cada arquivo e sua
     assinatura, para restaurar um a um).
"""
from __future__ import annotations

import glob
import json
import lzma
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

from .compactador import ROOT, empacotar, registrar

CFG = ROOT / "config/arquivo_frio.json"
TMP = Path("/tmp/arquivo_frio")
LISTAS = ROOT / "biblioteca_alexandria/arquivo_frio/listas"


def _api(metodo, url, dados=None, cab=None):
    tok = os.environ["GITHUB_TOKEN"]
    h = {"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json", **(cab or {})}
    req = urllib.request.Request(url, data=dados, method=metodo, headers=h)
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read() or b"{}")


def _release(tag: str) -> dict:
    rep = os.environ.get("GITHUB_REPOSITORY", "amcjardimamerica-arch/Eldorado")
    try:
        return _api("GET", f"https://api.github.com/repos/{rep}/releases/tags/{tag}")
    except Exception:
        return _api("POST", f"https://api.github.com/repos/{rep}/releases",
                    json.dumps({"tag_name": tag, "name": f"Arquivo frio — {tag[-10:]}", "body": "Pacotes sem perda do arquivo frio. Ver manifesto."}).encode())


def _enviar_release(rel: dict, arq: Path) -> dict:
    # anexo com o mesmo nome é SUBSTITUÍDO: a assinatura do manifesto tem de corresponder ao que está guardado
    ja = next((a for a in rel.get("assets", []) if a["name"] == arq.name), None)
    if ja:
        _api("DELETE", ja["url"])
    up = rel["upload_url"].split("{")[0] + f"?name={arq.name}"
    return _api("POST", up, arq.read_bytes(), {"Content-Type": "application/octet-stream"})


def _enviar_drive(arq: Path, pasta: str) -> str | None:
    if not os.environ.get("RCLONE_CONF"):
        return None
    conf = Path("/tmp/rclone.conf"); conf.write_text(os.environ["RCLONE_CONF"])
    r = subprocess.run(["rclone", "--config", str(conf), "copy", str(arq), "gdrive:", "--drive-root-folder-id", pasta], capture_output=True, text=True)
    if r.returncode != 0:
        print("Drive falhou:", r.stderr[-300:]); return None
    chk = subprocess.run(["rclone", "--config", str(conf), "size", f"gdrive:{arq.name}", "--drive-root-folder-id", pasta, "--json"], capture_output=True, text=True)
    try:
        return "drive:" + arq.name if json.loads(chk.stdout).get("bytes") == arq.stat().st_size else None
    except Exception:
        return None


def run() -> list[dict]:
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    rel = _release(cfg["release_tag"]) if os.environ.get("GITHUB_TOKEN") else None
    feitos = []
    for cj in cfg["conjuntos"]:
        arquivos = list(cj.get("arquivos") or [])
        if cj.get("padrao"):
            arquivos += subprocess.run(["git", "ls-files", cj["padrao"]], cwd=ROOT, capture_output=True, text=True).stdout.split()
        arquivos = [a for a in arquivos if (ROOT / a).is_file()]
        if not arquivos:
            continue
        reg = empacotar(arquivos, cj["nome"], TMP)                       # verificação byte a byte lá dentro
        arq = TMP / reg["pacote"]
        onde = {}
        if rel:
            a = _enviar_release(rel, arq)
            if a.get("size") == arq.stat().st_size:
                onde["release"] = a.get("browser_download_url")
        d = _enviar_drive(arq, cfg["drive_pasta_id"])
        if d:
            onde["drive"] = cfg["drive_pasta_url"]
        if not onde:
            print(f"{cj['nome']}: pacote NÃO guardado fora do repositório — nada removido"); continue
        LISTAS.mkdir(parents=True, exist_ok=True)
        (LISTAS / f"{cj['nome']}.jsonl.xz").write_bytes(lzma.compress("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in reg["conteudo"]).encode("utf-8"), preset=9))
        registrar({**reg, "por_que": cj.get("por_que")}, onde)
        lista = TMP / f"{cj['nome']}.remover.txt"; lista.write_text("\n".join(arquivos) + "\n", encoding="utf-8")
        # 62.305 caminhos numa linha de comando estouram o limite do sistema: a lista vai por arquivo
        subprocess.run(["git", "rm", "-q", "-r", "--cached", "--ignore-unmatch", f"--pathspec-from-file={lista}"], cwd=ROOT, check=True)
        for a in arquivos:
            try:
                (ROOT / a).unlink()
            except FileNotFoundError:
                pass
        feitos.append({"conjunto": cj["nome"], "arquivos": reg["arquivos"], "mb_antes": reg["bytes_originais"] // 1048576,
                       "mb_pacote": round(reg["bytes_pacote"] / 1048576, 1), "guardado_em": onde})
        print(json.dumps(feitos[-1], ensure_ascii=False))
    return feitos


if __name__ == "__main__":
    run()
