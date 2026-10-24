"""A cópia dos bancos e dos eventos no Drive (plano C: a API do Google; o rclone de alternativa).

Pronta para quando a titular indicar a pasta: as credenciais de uma conta de serviço (ELDORADO_DRIVE_CREDENCIAIS, o JSON)
e a pasta (ELDORADO_DRIVE_PASTA, o id). Sem elas, o comando diz que aguarda. O rclone entra quando houver o remoto
configurado (ELDORADO_RCLONE_REMOTO, por exemplo "drive:Eldorado").
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def pacote(dados: Path = Path("dados"), eventos: Path = Path("eventos")) -> Path:
    """Os bancos e os eventos num pacote compactado, com a data."""
    nome = Path(tempfile.gettempdir()) / f"eldorado-{datetime.now(timezone.utc):%Y-%m-%d}.tar.gz"
    with tarfile.open(nome, "w:gz") as t:
        for p in sorted(dados.glob("*.db")):
            t.add(p, arcname=f"dados/{p.name}")
        if eventos.exists():
            t.add(eventos, arcname="eventos")
    return nome


def copiar(dados: Path = Path("dados"), eventos: Path = Path("eventos")) -> str:
    cred, pasta, remoto = os.environ.get("ELDORADO_DRIVE_CREDENCIAIS"), os.environ.get("ELDORADO_DRIVE_PASTA"), os.environ.get("ELDORADO_RCLONE_REMOTO")
    if not ((cred and pasta) or (remoto and shutil.which("rclone"))):
        return "aguarda a pasta do Drive (os segredos ELDORADO_DRIVE_CREDENCIAIS e ELDORADO_DRIVE_PASTA, ou ELDORADO_RCLONE_REMOTO)"
    arq = pacote(dados, eventos)
    if cred and pasta:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        credenciais = service_account.Credentials.from_service_account_info(json.loads(cred), scopes=["https://www.googleapis.com/auth/drive.file"])
        servico = build("drive", "v3", credentials=credenciais, cache_discovery=False)
        f = servico.files().create(body={"name": arq.name, "parents": [pasta]}, media_body=MediaFileUpload(str(arq), resumable=True), fields="id").execute()
        return f"copiado no Drive: {arq.name} ({f.get('id')})"
    subprocess.run(["rclone", "copy", str(arq), remoto], check=True, timeout=1800)
    return f"copiado pelo rclone: {arq.name} → {remoto}"
