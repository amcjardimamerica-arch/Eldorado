"""Verificação assistida (determinística, sem IA e sem tokens): abre a URL
primária de oportunidades apenas `capturada`, confere que a página é de fonte
catalogada, contém termos de edital e está livre de padrões de injeção, e
então promove para `verificada_primaria` com evidência hasheada e auditoria.

O humano continua soberano: `scripts/promover.py` rebaixa ou descarta qualquer
promoção (status protegidos nunca são rebaixados pela máquina)."""
from __future__ import annotations

import json
import re
from urllib.error import HTTPError, URLError

from .eldorado import TERMS, fetch
from .nucleo import (ROOT, append_jsonl, carregar_oportunidades, gravar_oportunidades,
                     has_prompt_injection, html_para_texto, load_json, now_iso, sha256, write_json)

TIPOS_INELEGIVEIS = {"busca_retroativa_dominio_catalogado", "rede_social_oficial", "diario_oficial_municipal"}

def _fontes() -> dict:
    return {f["id"]: f for f in load_json(ROOT / "config/fontes.json")["fontes"]}

def run() -> dict:
    cfg = load_json(ROOT / "config/ia.json").get("verificacao_assistida", {})
    relatorio = {"executado_em": now_iso(), "avaliadas": 0, "promovidas": 0, "recusadas": 0, "falhas": []}
    if not cfg.get("ativa"):
        relatorio["status"] = "desativada"; return relatorio
    politica = load_json(ROOT / "config/fontes.json")["politica"]
    fontes = _fontes()
    registros = carregar_oportunidades()
    limite = int(cfg.get("max_por_execucao", 10))
    candidatas = [x for x in registros.values()
                  if x.get("status") == "capturada" and x.get("confianca") == "primaria"
                  and x.get("tipo_fonte") not in TIPOS_INELEGIVEIS]
    candidatas.sort(key=lambda x: x.get("coletado_em") or "", reverse=True)
    for item in candidatas[:limite]:
        relatorio["avaliadas"] += 1
        fonte = fontes.get(item.get("fonte_id"))
        if not fonte:
            relatorio["recusadas"] += 1; continue
        pseudo = {**fonte, "url": item["url"]}
        try:
            data, final, ctype = fetch(pseudo, politica)
            texto = html_para_texto(data.decode("utf-8", "replace")) if ctype == "text/html" else data.decode("utf-8", "replace")[:120_000]
            if has_prompt_injection(texto):
                relatorio["recusadas"] += 1
                append_jsonl(ROOT / "estado/quarentena.jsonl", {"id": item["id"], "url": final, "motivo": "injecao_na_pagina_primaria", "em": now_iso()})
                continue
            achado = TERMS.search(texto)
            if not achado:
                relatorio["recusadas"] += 1; continue
            inicio = max(achado.start() - 120, 0)
            trecho = re.sub(r"\s+", " ", texto[inicio:achado.end() + 280]).strip()
            item.update({
                "status": "verificada_primaria",
                "verificado_em": now_iso(), "verificado_por": "verificacao_assistida",
                "evidencia_verificacao": {"url_final": final, "sha256_pagina": sha256(data), "trecho": trecho[:500]},
            })
            relatorio["promovidas"] += 1
            append_jsonl(ROOT / "estado/auditoria.jsonl", {"evento": "verificacao_assistida", "oportunidade": item["id"], "url": final, "em": now_iso()})
        except (HTTPError, URLError, OSError, ValueError) as exc:
            relatorio["falhas"].append({"oportunidade": item["id"], "erro": type(exc).__name__})
    gravar_oportunidades(registros)
    write_json(ROOT / "estado/ultima_verificacao_assistida.json", relatorio)
    return relatorio

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
