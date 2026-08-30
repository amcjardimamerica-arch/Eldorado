from __future__ import annotations

import hashlib
import ipaddress
import json
import re
import socket
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]

INJECTION_PATTERNS = [
    re.compile(p, re.I) for p in (
        r"ignore .{0,40}(instruction|prompt|message)",
        r"disregard (all|any|the|previous|prior)",
        r"system prompt",
        r"prompt injection",
        r"reveal (the )?(prompt|secret|token)",
        r"you are (chatgpt|claude|an ai)",
    )
]

def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def slug(text: str) -> str:
    clean = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", clean).strip("-")[:90] or "sem-nome"

def canonical_url(url: str) -> str:
    p = urlsplit(url.strip())
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/") or "/", p.query, ""))

def validate_public_https(url: str, allowed_host: str | None = None) -> None:
    p = urlsplit(url)
    if p.scheme != "https" or not p.hostname or p.username or p.password:
        raise ValueError("URL deve ser HTTPS e não pode conter credenciais")
    if allowed_host and not (p.hostname == allowed_host or p.hostname.endswith("." + allowed_host)):
        raise ValueError("redirecionamento para domínio não autorizado")
    for info in socket.getaddrinfo(p.hostname, 443, type=socket.SOCK_STREAM):
        ip = ipaddress.ip_address(info[4][0])
        if not ip.is_global:
            raise ValueError("endereço local, reservado ou privado bloqueado")

def has_prompt_injection(text: str) -> bool:
    sample = text[:250_000]
    return any(p.search(sample) for p in INJECTION_PATTERNS)

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_jsonl(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")
