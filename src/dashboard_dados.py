"""Dados consolidados do dashboard interativo — substitui os relatórios datados.

O dashboard (`docs/dashboard.html`) é um arquivo estático único, escrito uma
vez. A cada varredura, o robô atualiza somente este arquivo de dados; o painel
lê e monta tudo no navegador — filtros, abas, calendário e contagens de prazo
calculadas ao vivo, sempre atuais mesmo entre varreduras.

Duas saídas equivalentes:
- `docs/dashboard-dados.json` — para leitura via rede (GitHub Pages).
- `docs/dashboard-dados.js`   — o mesmo conteúdo em `window.DADOS = {...}`,
  para funcionar também abrindo o arquivo local direto do repositório clonado,
  onde `fetch()` de arquivo é bloqueado pelo navegador.

Emendas parlamentares: os dados vão junto, mas a decisão de exibir é do
navegador (outubro/novembro) e **nada aqui aciona o Farol**. Sem IA e sem tokens.
"""
from __future__ import annotations

import json
from datetime import date

from . import parlamentares as mod_parlamentares
from .programas import caracterizar
from .relatorio_busca import _calendario, _situacao
from .nucleo import ROOT, carregar_oportunidades, load_json, now_iso, write_json

def _ler(caminho: str) -> dict:
    arquivo = ROOT / caminho
    return load_json(arquivo) if arquivo.exists() else {}

def coletar(hoje: date | None = None) -> dict:
    hoje = hoje or date.today()
    cfg_prog = load_json(ROOT / "config/programas.json")
    cfg_parl = load_json(ROOT / "config/parlamentares.json")

    editais = []
    for item in carregar_oportunidades().values():
        if item.get("status") in {"quarentena_prompt_injection", "descartada"}:
            continue
        carac = item.get("caracterizacao") or caracterizar(item, cfg_prog)
        periodo = carac.get("periodo") or {}
        situacao = _situacao(periodo.get("inicio"), periodo.get("fim"), hoje)
        editais.append({
            "id": item["id"], "titulo": item.get("titulo"), "url": item.get("url"),
            "fonte_nome": item.get("fonte_nome"), "territorio": item.get("territorio"),
            "uf": item.get("uf"), "nivel": item.get("nivel"), "status": item.get("status"),
            "confianca": item.get("confianca"),
            "programa": carac.get("programa"), "programa_id": carac.get("programa_id"),
            "lei": carac.get("lei"), "modalidade": carac.get("modalidade"),
            "fluxo": carac.get("fluxo", "edital"), "alerta_programa": carac.get("alerta"),
            "aciona_farol": carac.get("aciona_farol", True),
            "inicio": periodo.get("inicio"), "fim": periodo.get("fim"),
            "inicio_declarado": bool(periodo.get("inicio_declarado")),
            "estado_no_export": situacao["estado"],
            "nota_conformidade": (item.get("qualidade") or {}).get("nota"),
            "classe_conformidade": (item.get("qualidade") or {}).get("classe"),
            "pendencias_conformidade": [x["rotulo"] for x in
                                        ((item.get("qualidade") or {}).get("conteudo_pendente") or [])][:8],
            "ficha": f"editais/{item['id']}.html",
            "coletado_em": item.get("coletado_em"),
        })

    janelas = cfg_prog["janelas_recorrentes"]
    continuos = [{"programa": p["nome"], "lei": p["lei"]}
                 for p in cfg_prog["programas"]
                 if p["id"] in janelas["fluxo_continuo_mensal"]["programas"]]

    parl = mod_parlamentares.carregar_do_disco(hoje.year)

    return {
        "gerado_em": now_iso(),
        "referencia_da_ultima_varredura": hoje.isoformat(),
        "editais": editais,
        "calendario": _calendario(editais, cfg_prog, hoje.year),
        "fluxo_continuo": continuos,
        "janela_emendas": {"meses": janelas["emendas_parlamentares"]["meses"],
                           "rotulo": janelas["emendas_parlamentares"]["rotulo"],
                           "aciona_farol": False,
                           "motivo": cfg_parl["motivo_nao_acionar"]},
        "parlamentares": {"ano": parl.get("ano"), "total": parl.get("total", 0),
                          "lista": parl.get("parlamentares", []),
                          "pendencias": parl.get("pendencias", []),
                          "resultado_eleicao": parl.get("resultado_eleicao",
                                                        {"status": "nao_carregado"}),
                          "status": parl.get("status")},
        "execucao": _ler("estado/ultima_execucao.json"),
        "prazos": {k: v for k, v in _ler("estado/prazos.json").items() if k != "itens"},
        "qualidade": _ler("estado/qualidade.json"),
        "rotas_260": {k: v for k, v in _ler("estado/rotas_monitoramento.json").items() if k != "rotas"},
        "carga_historica": _ler("estado/ultima_carga_historica.json") or {"status": "nunca_executada"},
        "avisos": [
            "Dados automatizados exigem conferência na fonte primária antes de qualquer decisão.",
            "Datas de início e fim são as escritas na fonte; ausência é lacuna declarada, não estimada.",
            "Emendas parlamentares não acionam o Farol: a área informa e direciona apenas.",
        ],
    }

def run(hoje: date | None = None) -> dict:
    dados = coletar(hoje)
    write_json(ROOT / "docs/dashboard-dados.json", dados)
    conteudo = json.dumps(dados, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    (ROOT / "docs/dashboard-dados.js").write_text(
        "window.DADOS=" + conteudo + ";\n", encoding="utf-8")
    return {"gerado_em": dados["gerado_em"], "editais": len(dados["editais"]),
            "parlamentares_carregados": dados["parlamentares"]["total"]}

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
