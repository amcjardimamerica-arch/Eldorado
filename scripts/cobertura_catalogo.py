"""Mede a abrangência: quantos dos 260 pontos de captação do acervo têm ao
menos uma camada de coleta ativa cobrindo seu nível/tipo — e lista os
descobertos, que são a fila de validação de novas fontes.

Uso: python scripts/cobertura_catalogo.py"""
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.nucleo import ROOT, load_json, now_iso, write_json

CAMADAS_GERAIS = {
    # tipo_catalogo -> justificativa da camada que o cobre
    "editais_chamamentos": "varredura de portais (62 fontes) + PNCP + Querido Diário",
    "fundos": "fontes de fundos catalogadas + diários oficiais (conselhos deliberam por resolução publicada)",
    "emendas": "portais federativos + diários oficiais",
    "incentivos_fiscais": "páginas de programas (Rouanet/SALIC, PRONON/PRONAS, Goyazes, LC 222/2025)",
    "justica_destinacoes": "TJGO banco de projetos + diários oficiais",
    "doacoes_patrocinios": "páginas institucionais catalogadas + camada capilar de imprensa",
    "grants_internacionais": "fontes internacionais (UE, BID, UNESCO, Grants.gov) + portais autenticados manuais",
    "plataformas_radar": "fontes agregadoras (Prosas, Capta, GIFE, Observatório)",
    "outros": None,
}

def run() -> dict:
    catalogo = load_json(ROOT / "catalogo_captacao/catalogo_anexo.json")
    fontes = load_json(ROOT / "config/fontes.json")["fontes"]
    ativos_nivel = {f.get("nivel") for f in fontes if f.get("ativa")}
    cobertos, descobertos = [], []
    for item in catalogo["itens"]:
        tipo = item.get("tipo_catalogo") or "outros"
        niveis = item.get("niveis_inferidos") or ["a_validar"]
        camada = CAMADAS_GERAIS.get(tipo)
        nivel_ok = any(n in ativos_nivel or n == "a_validar" for n in niveis)
        if camada and nivel_ok:
            cobertos.append(item["id_acervo"])
        else:
            descobertos.append({"id": item["id_acervo"], "fonte_programa": item.get("fonte_programa"),
                                "tipo": tipo, "niveis": niveis})
    resultado = {
        "gerado_em": now_iso(), "total_catalogo": catalogo["total"],
        "cobertos_por_camada_ativa": len(cobertos), "descobertos": len(descobertos),
        "percentual_cobertura": round(100 * len(cobertos) / max(catalogo["total"], 1), 1),
        "fila_validacao": descobertos[:60],
        "regra": "cobertura por camada não substitui a validação página a página: itens cobertos continuam pistas até terem URL primária confirmada",
    }
    write_json(ROOT / "estado/cobertura_catalogo.json", resultado)
    print(json.dumps({k: resultado[k] for k in ("total_catalogo", "cobertos_por_camada_ativa", "descobertos", "percentual_cobertura")}, ensure_ascii=False, indent=2))
    return resultado

if __name__ == "__main__":
    run()
