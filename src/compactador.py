"""COMPACTADOR SEM PERDA (titular, 28/09) — documentos grandes e de uso esporádico viram um pacote menor, verificável.

  empacotar(caminhos, nome)   junta os arquivos num .tar.xz (compressão máxima), grava o SHA-256 e o tamanho de
                              CADA original no manifesto e, antes de devolver, reabre o pacote e confere byte a byte
                              que cada arquivo volta idêntico. Só então o pacote é considerado bom.
  transcrever(arquivo)        para HTML e PDF: extrai o texto (uma TRANSCRIÇÃO leve e pesquisável) que fica no
                              repositório; o original vai inteiro, sem perda, no pacote.
  restaurar(pacote, destino)  devolve os arquivos originais e confere cada assinatura.

O manifesto (biblioteca_alexandria/arquivo_frio/manifesto.json) diz, para cada pacote: o que tem dentro, as
assinaturas, o tamanho antes e depois, e ONDE está guardado (Release do GitHub e/ou Google Drive). Nada é apagado
do repositório sem pacote verificado e guardado fora dele.

Nota de engenharia: arquivo que muda a cada voo NÃO deve ser comprimido dentro do repositório — o git já comprime
cada versão e guarda só a diferença entre versões; um .xz muda inteiro a cada gravação e incharia o histórico. O
compactador é para o que é grande e parado (arquivo frio).
"""
from __future__ import annotations

import hashlib
import io
import json
import lzma
import os
import re
import tarfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFESTO = ROOT / "biblioteca_alexandria/arquivo_frio/manifesto.json"
TRANSCRICOES = ROOT / "biblioteca_alexandria/arquivo_frio/transcricoes"


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def empacotar(caminhos: list[str], nome: str, destino: Path) -> dict:
    destino.mkdir(parents=True, exist_ok=True)
    arq = destino / f"{nome}.tar.xz"
    conteudo, total = [], 0
    with tarfile.open(arq, "w:xz", preset=9 | lzma.PRESET_EXTREME) as t:
        for c in caminhos:
            p = ROOT / c
            if not p.is_file():
                continue
            b = p.read_bytes(); total += len(b)
            conteudo.append({"arquivo": c, "bytes": len(b), "sha256": _sha(b)})
            t.add(p, arcname=c)
    # VERIFICAÇÃO: reabre e confere cada arquivo, byte a byte, pela assinatura
    esperado = {x["arquivo"]: x["sha256"] for x in conteudo}
    with tarfile.open(arq, "r:xz") as t:
        vistos = 0
        for m in t.getmembers():
            if m.isfile():
                b = t.extractfile(m).read()
                if esperado.get(m.name) != _sha(b):
                    raise ValueError(f"verificação falhou em {m.name}: o pacote não devolve o original idêntico")
                vistos += 1
    if vistos != len(conteudo):
        raise ValueError("verificação falhou: número de arquivos no pacote diferente do original")
    return {"pacote": arq.name, "sha256_pacote": _sha(arq.read_bytes()), "arquivos": len(conteudo), "bytes_originais": total,
            "bytes_pacote": arq.stat().st_size, "reducao": round(1 - arq.stat().st_size / max(1, total), 3), "verificado": True,
            "conteudo": conteudo, "criado_em": date.today().isoformat()}


def transcrever(caminho: str) -> str | None:
    """Texto pesquisável de HTML ou PDF (a transcrição leve fica no repositório; o original, no pacote)."""
    p = ROOT / caminho
    if not p.is_file():
        return None
    texto = ""
    if p.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader
            texto = "\n".join((pg.extract_text() or "") for pg in PdfReader(str(p)).pages)
        except Exception:
            return None
    elif p.suffix.lower() in (".html", ".htm"):
        h = p.read_text(encoding="utf-8", errors="ignore")
        h = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", h)
        texto = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h)).strip()
    else:
        return None
    TRANSCRICOES.mkdir(parents=True, exist_ok=True)
    out = TRANSCRICOES / (re.sub(r"[^a-zA-Z0-9]+", "_", caminho)[:120] + ".txt.xz")
    out.write_bytes(lzma.compress(texto.encode("utf-8"), preset=9))
    return str(out.relative_to(ROOT))


def restaurar(pacote: Path, destino: Path) -> int:
    reg = next((x for x in manifesto().get("pacotes", []) if x["pacote"] == pacote.name), None)
    esperado = {x["arquivo"]: x["sha256"] for x in (reg or {}).get("conteudo", [])}
    n = 0
    with tarfile.open(pacote, "r:xz") as t:
        for m in t.getmembers():
            if not m.isfile():
                continue
            b = t.extractfile(m).read()
            if esperado and esperado.get(m.name) != _sha(b):
                raise ValueError(f"{m.name}: assinatura não confere")
            alvo = destino / m.name; alvo.parent.mkdir(parents=True, exist_ok=True); alvo.write_bytes(b); n += 1
    return n


def manifesto() -> dict:
    try:
        return json.loads(MANIFESTO.read_text(encoding="utf-8"))
    except Exception:
        return {"regra": __doc__.split("Nota de engenharia")[0].strip(), "pacotes": []}


def registrar(reg: dict, onde: dict) -> None:
    m = manifesto()
    reg = {**{k: v for k, v in reg.items() if k != "conteudo"}, "guardado_em": onde,
           "conteudo": reg["conteudo"] if reg["arquivos"] <= 200 else {"resumo": f"{reg['arquivos']} arquivos", "lista": f"{reg['pacote']}.lista.jsonl"}}
    m["pacotes"] = [x for x in m["pacotes"] if x["pacote"] != reg["pacote"]] + [reg]
    MANIFESTO.parent.mkdir(parents=True, exist_ok=True)
    MANIFESTO.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
