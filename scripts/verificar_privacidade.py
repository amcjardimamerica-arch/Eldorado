"""Falha o build só se uma CREDENCIAL for publicada (token do GitHub, chave privada).

24/09, por decisão do titular: os dados do sistema são públicos e pesquisáveis, e as travas
de privacidade (CPF, RG) saíram. Fica só a checagem de credenciais — elas não são dado: são a
chave do repositório. Um token publicado deixa qualquer pessoa apagar ou alterar o sistema.
"""
from __future__ import annotations
import gzip, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]/"dados/associacoes"
PATTERNS={
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
    if hits: raise SystemExit("credencial detectada: "+", ".join(hits))
    print("nenhuma credencial publicada")

if __name__=="__main__": main()
