#!/usr/bin/env python3
"""DESCRIÇÃO INTERNA DE CADA MOTOR — o que ele busca, como busca, onde para e como afiar.

Aparece só ao passar o mouse sobre o quadro do motor na Bússola. Escrita para permitir
melhoria: quem lê precisa saber, em segundos, o objetivo do motor, o caminho que ele faz, o
ponto exato em que ele perde o que busca, e a próxima coisa a fazer nele.

Sai dos arquivos do sistema — rotas, finalidade, relatório individual e correções aplicadas —
e é refeita a cada geração: a descrição acompanha o motor, não fica velha.

    python3 scripts/descricao_motores.py
"""
from __future__ import annotations

import datetime
import json
from pathlib import Path
from urllib.parse import urlsplit

RAIZ = Path(__file__).resolve().parents[1]

# Evolução GRATUITA: só caminhos sem custo, escolhidos pela família da fonte.
EVOLUCAO = {
    "pncp-api": "filtrar NA CONSULTA da API oficial do PNCP (uf=GO e modalidade), em vez de baixar tudo e "
                "descartar depois: o credenciamento é barrado antes de chegar",
    "dou": "Ro-DOU (robô de código aberto do governo federal que busca termos no DOU) ou INLABS da Imprensa "
           "Nacional (XML integral da edição, gratuito com cadastro)",
    "do-goias": "ler o PDF da edição completa, não só o índice — o ato está dentro; e ser o único leitor do "
                "Diário para os motores estaduais",
    "do-goiania": "verificar a cobertura de Goiânia no Querido Diário (API aberta da Open Knowledge Brasil); "
                  "se houver, dispensa a coleta local",
    "dje-tjgo": "testar a API do Diário de Justiça Eletrônico Nacional (DJEN/CNJ), que publica os atos dos "
                "tribunais fora do WAF do TJGO",
    "dj-trf1-go": "testar a API do DJEN/CNJ, que concentra os diários da Justiça Federal",
    "camara-goiania-pl": "verificar se a Câmara usa o SAPL (Interlegis), que expõe API aberta de proposições",
    "alego-pl": "dados abertos da ALEGO para proposições e leis de utilidade pública, em vez de raspar páginas",
    "plat-salic": "API pública do SALIC: projetos aprovados e INCENTIVADORES com valores — serve também à lista "
                  "de empresas",
    "motor-gife": "API do SALIC (incentivadores por empresa, com valores e anos) + dados abertos de CNPJ da "
                  "Receita: histórico real de destinação",
    "empresas-incentivadas": "cruzar a lista do ICMS de Goiás com os incentivadores do SALIC: quem já destinou "
                             "por lei sobe na fila",
    "motor-patrocinio": "alertas gratuitos em RSS (Google Alertas) para 'patrocínio' + Goiânia/Goiás: a imprensa "
                        "avisa quando uma empresa patrocina",
    "sindico-aberto": "feeds RSS das entidades e da imprensa do terceiro setor, em vez de busca genérica bloqueada",
}
FINALIDADE = {"descoberta": "Descobrir oportunidades novas", "insumo": "Alimentar o sistema com referência",
              "recorrencia": "Revisitar oportunidades já conhecidas"}


def ler(p, padrao=None):
    f = RAIZ / p
    try:
        return json.loads(f.read_text(encoding="utf-8")) if f.exists() else padrao
    except Exception:
        return padrao


def evolucao(mid: str) -> str:
    if mid in EVOLUCAO:
        return EVOLUCAO[mid]
    if mid.startswith("plat-"):
        return "ler o feed RSS da plataforma (sites WordPress publicam /feed/ de graça): mais leve que raspar e não bloqueia"
    return "trocar raspagem por feed RSS ou API aberta da própria fonte, quando existir"


def gerar() -> dict:
    R = ler("config/rotas_motores.json", {})
    M = R.get("motores") or {}
    fm = ler("config/finalidade_motores.json", {}).get("motores") or {}
    FM = dict(fm) if isinstance(fm, list) else fm
    REL = {x["id"]: x for x in (ler("docs/dados/relatorio_motores.json", {}).get("motores") or [])}
    COR = (ler("estado/correcoes_motores_2026-09-24.json", {}) or {}).get("por_motor") or {}
    saida = {}
    for mid, m in M.items():
        r = REL.get(mid, {})
        f = FM.get(mid) or {}
        rotas = m.get("rotas") or []
        doms = sorted({(urlsplit(str(x.get("url") or "")).hostname or "").replace("www.", "")
                       for x in rotas if str(x.get("url") or "").startswith("http")} - {""})
        fin = f.get("finalidade") or "descoberta"
        if fin == "insumo" and f.get("do_que"):
            obj = f"Alimentar o sistema com {f['do_que']}, a partir de {m.get('perfil') or mid}."
        else:
            obj = f"{FINALIDADE.get(fin, fin)} em {m.get('perfil') or mid}."
        como = (f"Roda a cada {f.get('cadencia_dias') or '—'} dia(s), coleta "
                f"{'pelo computador do titular' if m.get('coleta') == 'local' else 'na nuvem'}; lê "
                f"{len(rotas)} rota(s) em {len(doms)} domínio(s) ({', '.join(doms[:3])}{'…' if len(doms) > 3 else ''}); "
                f"abre só links que casam com {len(m.get('lexico_camada1') or [])} termos e escapam dos "
                f"{len(R.get('camada_1_veto') or [])} vetos, e confirma no texto com "
                f"{len(m.get('lexico_camada2') or [])} termos.")
        op, dec = r.get("onde_para") or {}, r.get("veredito") or {}
        afiar = ([f"{dec['decisao'].lower()}: {dec.get('porque', '')}"] if dec.get("decisao") else []) + COR.get(mid, [])[:2]
        saida[mid] = {"nome": r.get("nome") or mid, "objetivo": obj, "como_funciona": como,
                      "onde_para": f"{op.get('estagio', '—')} — {op.get('porque', '')}".strip(" —"),
                      "para_afiar": afiar[:3], "evolucao_gratuita": evolucao(mid)}
    return {"em": datetime.date.today().isoformat(),
            "regra": "descrição interna: aparece só ao passar o mouse sobre o quadro do motor na Bússola",
            "motores": saida}


if __name__ == "__main__":
    d = gerar()
    for arq in ("config/descricao_motores.json", "docs/dados/descricao_motores.json"):
        (RAIZ / arq).write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(d['motores'])} descrições → config/ e docs/dados/")
