"""Orquestração da varredura profunda (segunda e quarta).

Cada etapa é isolada: falha em uma NUNCA derruba as demais — o erro fica
registrado e o resumo/alerta dá visibilidade. Ordem do fluxo:

coleta HTML → APIs oficiais → capilaridade (pistas) → social → verificação
assistida → dossiês → aprendizado/previsões → triagem → casos → Farol IA → painel
"""
from __future__ import annotations
import json

from . import (aprendizado, capilaridade, casos, coletores_api, dossies, eldorado,
               farol_ia, painel, triagem, verificacao_assistida, verificacao_social)
from .nucleo import ROOT, append_jsonl, now_iso, write_json

def _rodar(nome, funcao, relatorio):
    try:
        relatorio["etapas"][nome] = funcao() or {"ok": True}
    except Exception as exc:  # noqa: BLE001 — isolamento deliberado entre etapas
        relatorio["etapas"][nome] = {"erro": f"{type(exc).__name__}: {exc}"[:300]}

def main():
    relatorio = {"executado_em": now_iso(), "etapas": {}}
    _rodar("coleta", eldorado.run, relatorio)
    _rodar("apis_oficiais", coletores_api.run, relatorio)
    _rodar("capilaridade", capilaridade.run, relatorio)
    _rodar("verificacao_social", verificacao_social.run, relatorio)
    _rodar("verificacao_assistida", verificacao_assistida.run, relatorio)
    _rodar("dossies", dossies.run, relatorio)
    _rodar("aprendizado", aprendizado.run, relatorio)

    def _triagem_e_casos():
        gatilhos = triagem.run()
        criados = casos.run(gatilhos) if gatilhos else 0
        append_jsonl(ROOT / "estado/diario_novidades.jsonl",
                     {"em": now_iso(), "casos_abertos": [g["oportunidade_id"] for g in gatilhos], "total": criados})
        return {"gatilhos": len(gatilhos), "casos_criados": criados}
    _rodar("triagem_e_casos", _triagem_e_casos, relatorio)
    _rodar("farol_ia", farol_ia.run, relatorio)
    _rodar("painel", painel.run, relatorio)

    write_json(ROOT / "estado/ultima_execucao_diaria.json", relatorio)
    print(json.dumps(relatorio, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
