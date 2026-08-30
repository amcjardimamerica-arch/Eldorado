"""Falha o build se derivados públicos contiverem padrões proibidos."""
from __future__ import annotations
import gzip, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]/"dados/associacoes"
PATTERNS={
    "cpf_formatado":re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"),
    "rg_contextual":re.compile(r"(?i)\bRG\b\s*[:|,\"]*\s*\d{5,12}\b"),
    "chave_privada":re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "token_github":re.compile(r"\b(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}\b"),
}

def content(path: Path) -> str:
    raw=path.read_bytes()
    if path.suffix==".gz": raw=gzip.decompress(raw)
    return raw.decode("utf-8","ignore")

def main() -> None:
    hits=[]
    for path in ROOT.rglob("*"):
        if not path.is_file(): continue
        text=content(path)
        for name,pattern in PATTERNS.items():
            if pattern.search(text): hits.append(f"{path.relative_to(ROOT)}:{name}")
    if hits: raise SystemExit("dados proibidos detectados: "+", ".join(hits))
    print("privacidade pública verificada")

if __name__=="__main__": main()
