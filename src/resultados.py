"""Busca ativa de resultados, prorrogações e recursos de cada edital.

Revisita a página primária dos editais conhecidos procurando, no texto, os
marcos da fase final: resultado preliminar, resultado final, homologação,
prorrogação, retificação e fase de recurso. Cada achado vira um EVENTO datado
em `estado/resultados_editais.jsonl`, consumido pelo calendário do dashboard —
que marca a data e sinaliza quando um prazo foi prorrogado.

Determinístico, sem IA e sem tokens. O que a página não disser não é inventado.
"""
from __future__ import annotations

import json
import re
from urllib.error import HTTPError, URLError

from .eldorado import fetch
from .nucleo import (ROOT, append_jsonl, carregar_oportunidades, gravar_oportunidades,
                     html_para_texto, load_json, now_iso, sha256, write_json)

_D = r"(\d{1,2}/\d{1,2}/20\d{2})"
MARCOS = [
    ("resultado_final",      re.compile(r"resultado\s+(final|definitivo)|homologa[çc][ãa]o(?:\s+do\s+resultado)?", re.I)),
    ("resultado_preliminar", re.compile(r"resultado\s+(preliminar|provis[óo]rio)|classifica[çc][ãa]o\s+preliminar", re.I)),
    ("prorrogacao",          re.compile(r"prorroga[çc][ãa]o|prorrogad[oa]|novo\s+prazo|prazo\s+prorrogado", re.I)),
    ("retificacao",          re.compile(r"retifica[çc][ãa]o|errata|retificad[oa]", re.I)),
    ("recurso",              re.compile(r"fase\s+de\s+recursos?|prazo\s+(?:para|de)\s+recursos?|interposi[çc][ãa]o\s+de\s+recursos?", re.I)),
]
DATA_PROXIMA = re.compile(_D)
STATUS_ALVO = {"verificada_primaria", "verificada_dupla", "verificada_humana",
               "elegivel", "em_preparacao", "submetida"}

def _fontes() -> dict:
    return {f["id"]: f for f in load_json(ROOT / "config/fontes.json")["fontes"]}

def analisar_texto(texto: str) -> list[dict]:
    """Extrai marcos e a data mais próxima de cada menção (janela de 160 chars)."""
    eventos = []
    for tipo, padrao in MARCOS:
        achado = padrao.search(texto)
        if not achado:
            continue
        janela = texto[max(0, achado.start() - 40): achado.end() + 160]
        # a data do marco vem DEPOIS da menção ("resultado ... em 20/10"), nunca antes
        pos_frente = texto[achado.start(): achado.end() + 160]
        data = DATA_PROXIMA.search(pos_frente)
        eventos.append({
            "tipo": tipo,
            "trecho": re.sub(r"\s+", " ", janela).strip()[:240],
            "data_mencionada": data.group(1) if data else None,
        })
    return eventos

def run(max_por_execucao: int = 25) -> dict:
    fontes = _fontes()
    politica = load_json(ROOT / "config/fontes.json")["politica"]
    registros = carregar_oportunidades()
    saida = ROOT / "estado/resultados_editais.jsonl"
    vistos = set()
    if saida.exists():
        for linha in saida.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                e = json.loads(linha)
                vistos.add((e["edital_id"], e["tipo"], e.get("hash_trecho")))
    relatorio = {"executado_em": now_iso(), "consultados": 0, "eventos_novos": 0,
                 "prorrogacoes": 0, "falhas": []}
    for item in registros.values():
        if relatorio["consultados"] >= max_por_execucao:
            break
        if item.get("status") not in STATUS_ALVO or not str(item.get("url", "")).startswith("https://"):
            continue
        fonte = fontes.get(item.get("fonte_id"))
        if not fonte:
            continue
        relatorio["consultados"] += 1
        try:
            dados, final, _ = fetch({**fonte, "url": item["url"]}, politica)
        except (HTTPError, URLError, OSError, ValueError) as exc:
            relatorio["falhas"].append({"edital": item["id"], "erro": type(exc).__name__})
            continue
        texto = html_para_texto(dados.decode("utf-8", "replace"))
        for evento in analisar_texto(texto):
            chave = (item["id"], evento["tipo"], sha256(evento["trecho"].encode())[:16])
            if chave in vistos:
                continue
            vistos.add(chave)
            registro = {"edital_id": item["id"], "titulo": item.get("titulo"),
                        "url": item["url"], "detectado_em": now_iso(),
                        "hash_trecho": chave[2], **evento,
                        "observacao": "detecção textual automática — conferir na página primária"}
            append_jsonl(saida, registro)
            relatorio["eventos_novos"] += 1
            if evento["tipo"] == "prorrogacao":
                relatorio["prorrogacoes"] += 1
                if evento["data_mencionada"]:
                    # prorrogação atualiza o prazo exibido, preservando o original
                    item.setdefault("prazo_original", item.get("prazo_texto"))
                    item["prazo_texto"] = evento["data_mencionada"]
                    item["prazo_prorrogado"] = True
            marcos = item.setdefault("marcos_resultado", [])
            marcos.append({"tipo": evento["tipo"], "data": evento["data_mencionada"],
                           "detectado_em": now_iso()})
    gravar_oportunidades(registros)
    write_json(ROOT / "estado/ultima_busca_resultados.json", relatorio)
    return relatorio

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
