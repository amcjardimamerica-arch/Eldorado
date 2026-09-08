#!/usr/bin/env python3
"""Espelha os PDFs dos editais de Goiás no acervo do Google Drive.

POR QUE ESTE SCRIPT EXISTE

A regra do titular é que todo edital que se aplique a Goiás fique arquivado no
Drive de forma integral. O dossiê e o texto são gravados no momento da
verificação; o binário do PDF, não — porque a sessão de verificação roda em
ambiente sem rede direta e transportar megabytes de PDF por ali seria caro e
frágil. Este script fecha essa lacuna: roda no GitHub Actions, onde há rede,
baixa cada PDF do endereço registrado em `pdf_origem` e o envia para a pasta
do acervo, ao lado do dossiê correspondente.

COMO RODA

  python scripts/espelhar_editais_drive.py            # espelha o que falta
  python scripts/espelhar_editais_drive.py --conferir  # só relata, não envia

Credencial: variável de ambiente indicada em `config/integracoes.json`
(`google_drive.credencial_env`). Sem credencial, o script NÃO simula envio —
apenas relata o que faria, conforme a regra do repositório de nunca simular
execução de integração.

O QUE ELE NÃO FAZ

Não reescreve o dossiê nem inventa metadado. Se `pdf_origem` estiver vazio ou
responder erro, o item fica na lista de falhas com o motivo, e o acervo segue
com o texto que já tem. Falha de espelhamento nunca apaga o que está gravado.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.acervo_drive import PASTA_GO_DRIVE, banco  # noqa: E402

LIMITE_BYTES = 25 * 1024 * 1024  # PDF de edital acima disso é anexo em lote, não o edital
UA = "Eldorado/1.0 (acervo de editais historicos; contato pelo repositorio)"


def _baixar(url: str) -> tuple[bytes | None, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            dados = r.read(LIMITE_BYTES + 1)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        return None, f"falha ao baixar: {type(e).__name__}"
    if len(dados) > LIMITE_BYTES:
        return None, f"arquivo acima do limite de {LIMITE_BYTES // (1024*1024)} MB"
    if not dados[:4] == b"%PDF":
        assinatura = dados[:4].decode("latin1", "replace")
        return dados, f"não é PDF (assinatura {assinatura!r}) — enviado como está"
    return dados, "ok"


def nome_do_arquivo(item: dict) -> str:
    partes = ["GO", str(item.get("ano") or "s-ano"),
              (item.get("municipio") or item.get("esfera") or "GO").replace("/", "-"),
              (item.get("edital") or item.get("id") or "").replace("/", "-")]
    return " — ".join(p for p in partes if p)[:180] + ".pdf"


def espelhar(conferir_apenas: bool = False) -> dict:
    cfg = json.loads((ROOT / "config/integracoes.json").read_text(encoding="utf-8"))
    env = cfg["google_drive"]["credencial_env"]
    credencial = os.getenv(env)
    itens = banco().get("itens", [])
    fila = [x for x in itens if x.get("pdf_origem") and not x.get("pdf_espelhado_em")]
    rel = {"total_no_acervo": len(itens), "na_fila": len(fila),
           "credencial_configurada": bool(credencial), "pasta_destino": PASTA_GO_DRIVE,
           "enviados": [], "falhas": []}
    if conferir_apenas or not credencial:
        rel["situacao"] = ("apenas conferência" if conferir_apenas else
                           f"sem credencial em {env}: nada foi enviado e nada foi simulado")
        rel["faria"] = [{"id": x["id"], "arquivo": nome_do_arquivo(x), "de": x["pdf_origem"]}
                        for x in fila]
        return rel
    from src.integracoes_drive import enviar_arquivo  # só existe com integração ativa
    for item in fila:
        dados, motivo = _baixar(item["pdf_origem"])
        if dados is None:
            rel["falhas"].append({"id": item["id"], "motivo": motivo})
            continue
        try:
            enviar_arquivo(PASTA_GO_DRIVE, nome_do_arquivo(item), dados, "application/pdf")
            rel["enviados"].append({"id": item["id"], "arquivo": nome_do_arquivo(item),
                                    "bytes": len(dados), "observacao": motivo})
        except Exception as e:  # falha de rede/API não pode derrubar o acervo
            rel["falhas"].append({"id": item["id"], "motivo": f"erro no envio: {type(e).__name__}"})
    rel["situacao"] = "espelhamento executado"
    return rel


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--conferir", action="store_true", help="só relata, não envia")
    a = ap.parse_args()
    print(json.dumps(espelhar(a.conferir), ensure_ascii=False, indent=2))
