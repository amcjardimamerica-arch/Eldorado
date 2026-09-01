"""Farol de Alexandria · Documentos-modelo dos editais.

REGRA DO TITULAR: os documentos-modelo são extraídos em PDF e PREENCHIDOS
DIRETAMENTE NO MODELO — nunca se cria documento novo no lugar do formulário
oficial. O preenchimento clona o PDF original e grava os valores nos campos
de formulário (AcroForm) existentes; layout, carimbos e numeração do órgão
permanecem intactos.

Modelos sem campos de formulário (PDF "chapado") não são preenchíveis por
máquina: o Farol declara a pendência e entrega o modelo original + os dados
prontos para transcrição humana — nunca um documento recriado.
"""
from __future__ import annotations

import json
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, sha256, write_json

try:
    from pypdf import PdfReader, PdfWriter
except Exception:  # pragma: no cover
    PdfReader = PdfWriter = None

FAROL = ROOT / "dados/farol/editais"


def inventario() -> list[dict]:
    """Todos os modelos preservados, por edital/ano, com preenchibilidade."""
    saida = []
    if not FAROL.exists():
        return saida
    for dj in sorted(FAROL.glob("*/*/dados.json")):
        d = load_json(dj)
        pasta = dj.parent
        for anexo in d.get("anexos_modelo", []):
            arq = pasta / "anexos" / anexo["arquivo"]
            campos = None
            if PdfReader is not None and arq.exists():
                try:
                    campos = sorted((PdfReader(arq).get_fields() or {}).keys())
                except Exception:
                    campos = None
            saida.append({"edital": d["chave"], "ano": d["ano"],
                          "modelo": anexo["arquivo"], "origem": anexo.get("url"),
                          "caminho": str(arq.relative_to(ROOT)),
                          "preenchivel": bool(campos),
                          "campos": campos or [],
                          "pendencia": None if campos else
                          "modelo sem campos de formulário — preenchimento "
                          "manual sobre o PDF original"})
    return saida


def preencher_modelo(pdf_modelo: Path, valores: dict, destino: Path) -> dict:
    """Preenche os campos do PRÓPRIO modelo (clone fiel do PDF original).

    Devolve o relatório: campos preenchidos, campos do modelo ignorados por
    falta de dado (lacuna declarada) e valores fornecidos sem campo no modelo.
    Levanta erro se o ambiente não tem pypdf — nunca finge preenchimento.
    """
    if PdfReader is None:
        raise RuntimeError("pypdf ausente — preenchimento não disponível neste ambiente")
    leitor = PdfReader(pdf_modelo)
    campos = leitor.get_fields() or {}
    if not campos:
        raise ValueError("modelo sem campos de formulário: preencher manualmente "
                         "sobre o PDF original, sem recriar o documento")
    escritor = PdfWriter()
    escritor.append(leitor)
    usaveis = {k: str(v) for k, v in valores.items() if k in campos and v not in (None, "")}
    for pagina in escritor.pages:
        escritor.update_page_form_field_values(pagina, usaveis)
    try:  # visualizadores exigem NeedAppearances para exibir o valor
        escritor.set_need_appearances_writer(True)
    except Exception:
        pass
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("wb") as h:
        escritor.write(h)
    rel = {"modelo": str(pdf_modelo), "destino": str(destino),
           "preenchidos": sorted(usaveis),
           "campos_sem_dado": sorted(set(campos) - set(usaveis)),
           "dados_sem_campo": sorted(set(valores) - set(campos)),
           "sha256_original": sha256(pdf_modelo.read_bytes()),
           "preenchido_em": now_iso()}
    write_json(destino.with_suffix(".preenchimento.json"), rel)
    return rel


if __name__ == "__main__":
    print(json.dumps(inventario(), ensure_ascii=False, indent=2))
