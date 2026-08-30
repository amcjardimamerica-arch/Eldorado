"""Mede a abrangência dos 260 pontos de captação do acervo.

Desde a malha de rotas (src/rota_monitoramento.py), a pergunta deixou de ser
"este tipo tem camada?" e passou a ser "este ponto tem caminho de captura?".
A resposta vem de estado/rotas_monitoramento.json, que atribui a cada ponto a
forma de divulgação que ele usa e a camada que a captura.

Este script mantém a leitura por tipo como conferência cruzada.

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
    # "outros" no acervo são, em geral, TIPOS DE PROJETO (ex.: "núcleo de futebol de
    # base"), não fontes distintas. Cada um é roteado pela origem do dinheiro em
    # src/rota_monitoramento.py, que atribui forma de divulgação e camada.
    "outros": "roteado por origem do recurso (rota_monitoramento): conselho, diário oficial, emenda, incentivo ou instituição privada",
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
    rotas_arquivo = ROOT / "estado/rotas_monitoramento.json"
    rotas = load_json(rotas_arquivo) if rotas_arquivo.exists() else {}
    resultado = {
        "gerado_em": now_iso(), "total_catalogo": catalogo["total"],
        "com_rota_de_monitoramento": rotas.get("com_rota_de_monitoramento"),
        "sem_rota_de_monitoramento": rotas.get("sem_rota"),
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
