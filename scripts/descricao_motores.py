#!/usr/bin/env python3
"""DESCRIÇÃO E CONFIGURAÇÃO DE CADA MOTOR — para o mouse (resumo) e para o clique (completa).

Ao passar o mouse sobre o quadro do motor na Bússola aparece o resumo: objetivo, quando roda,
como funciona, onde para, o que fazer, evolução gratuita. Ao clicar, abre a janela com a
configuração inteira: rotas e endereços, léxico das duas camadas, veto geral, verificação em
duas etapas, agenda, números do mês e do acervo.

Sai dos arquivos do sistema — rotas, finalidade, agenda, relatório individual e correções
aplicadas — e é refeita a cada geração: a descrição acompanha o motor, não fica velha.

    python3 scripts/descricao_motores.py
"""
from __future__ import annotations

import datetime
import json
from pathlib import Path
from urllib.parse import urlsplit

RAIZ = Path(__file__).resolve().parents[1]

EVOLUCAO = {
    "pncp-api": "filtrar NA CONSULTA da API oficial do PNCP (uf=GO e modalidade), em vez de baixar tudo e "
                "descartar depois: o credenciamento é barrado antes de chegar",
    "dou": "Ro-DOU (robô de código aberto do governo federal que busca termos no DOU) ou INLABS da Imprensa "
           "Nacional (XML integral da edição, gratuito com cadastro)",
    "do-goias": "ler o PDF da edição completa, não só o índice — o ato está dentro; e ser o único leitor do "
                "Diário para os motores estaduais",
    "do-goiania": "verificar a cobertura de Goiânia no Querido Diário (API aberta da Open Knowledge Brasil); "
                  "se houver, dispensa a coleta local",
    "dje-tjgo": "testar a API do Diário de Justiça Eletrônico Nacional (DJEN/CNJ), fora do WAF do TJGO",
    "dj-trf1-go": "testar a API do DJEN/CNJ, que concentra os diários da Justiça Federal",
    "camara-goiania-pl": "verificar se a Câmara usa o SAPL (Interlegis), que expõe API aberta de proposições",
    "alego-pl": "dados abertos da ALEGO para proposições e leis de utilidade pública, em vez de raspar páginas",
    "plat-salic": "API pública do SALIC: projetos aprovados e INCENTIVADORES com valores — serve também à lista "
                  "de empresas",
    "motor-gife": "API do SALIC (incentivadores por empresa, com valores e anos) + dados abertos de CNPJ da "
                  "Receita: histórico real de destinação",
    "empresas-incentivadas": "cruzar a lista do ICMS de Goiás com os incentivadores do SALIC: quem já destinou "
                             "por lei sobe na fila",
    "motor-patrocinio": "alertas gratuitos em RSS (Google Alertas) para 'patrocínio' + Goiânia/Goiás",
    "piloto-aberto": "feeds RSS das entidades e da imprensa do terceiro setor, em vez de busca genérica bloqueada",
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
    AG = (ler("config/agenda_motores.json", {}) or {}).get("motores") or {}
    saida = {}
    for mid, m in M.items():
        r, f, ag = REL.get(mid, {}), FM.get(mid) or {}, AG.get(mid) or {}
        rotas = [{"nome": x.get("nome"), "url": x.get("url"), "tipo": x.get("tipo")}
                 for x in (m.get("rotas") or []) if str(x.get("url") or "")]
        doms = sorted({(urlsplit(str(x["url"])).hostname or "").replace("www.", "")
                       for x in rotas if str(x["url"]).startswith("http")} - {""})
        fin = f.get("finalidade") or "descoberta"
        if ag.get("objetivo"):
            obj = ag["objetivo"][0].upper() + ag["objetivo"][1:] + "."
        elif fin == "insumo" and f.get("do_que"):
            obj = f"Alimentar o sistema com {f['do_que']}, a partir de {m.get('perfil') or mid}."
        else:
            obj = f"{FINALIDADE.get(fin, fin)} em {m.get('perfil') or mid}."
        como = (f"Roda a cada {ag.get('cadencia_dias') or f.get('cadencia_dias') or '—'} dia(s), coleta "
                f"{'pelo computador do titular' if m.get('coleta') == 'local' else 'na nuvem'}; lê {len(rotas)} rota(s) em "
                f"{len(doms)} domínio(s) ({', '.join(doms[:3])}{'…' if len(doms) > 3 else ''}); abre só links que casam com "
                f"{len(m.get('lexico_camada1') or [])} termos e escapam dos {len(R.get('camada_1_veto') or [])} vetos, e confirma "
                f"no texto com {len(m.get('lexico_camada2') or [])} termos.")
        op, dec = r.get("onde_para") or {}, r.get("veredito") or {}
        afiar = ([f"{dec['decisao'].lower()}: {dec.get('porque', '')}"] if dec.get("decisao") else []) + COR.get(mid, [])[:2]
        saida[mid] = {
            "nome": r.get("nome") or mid, "perfil": m.get("perfil"), "tipo": r.get("tipo"), "finalidade": fin,
            "coleta": m.get("coleta") or "nuvem", "nota_coleta": m.get("nota_coleta"),
            "objetivo": obj, "como_funciona": como,
            "agenda": f"{ag.get('horarios_brt', '—')} · {ag.get('dias', '—')} — {ag.get('por_que_esta_hora', '')}".strip(" —"),
            "agenda_detalhe": {k: ag.get(k) for k in ("horarios_brt", "dias", "cadencia_dias", "por_que_esta_hora")},
            "verificacao": ag.get("verificacao") or {},
            "onde_para": f"{op.get('estagio', '—')} — {op.get('porque', '')}".strip(" —"),
            "para_afiar": afiar[:3], "evolucao_gratuita": evolucao(mid),
            "rotas": rotas, "dominios": doms,
            "lexico_1": m.get("lexico_camada1") or [], "lexico_2": m.get("lexico_camada2") or [],
            "veto_motor": m.get("veto_camada1") or [],
            "numeros": {"mes": r.get("mes"), "acervo": r.get("resultado"), "estado": r.get("estado"),
                        "achados_total": r.get("achados_total"), "bloqueios": r.get("bloqueios")},
        }
    return {"em": datetime.date.today().isoformat(),
            "regra": "resumo ao passar o mouse; configuração completa ao clicar no quadro do motor",
            "veto_geral": R.get("camada_1_veto") or [], "lexico_geral": R.get("camada_1_geral") or [],
            "motores": saida}


if __name__ == "__main__":
    d = gerar()
    for arq in ("config/descricao_motores.json", "docs/dados/descricao_motores.json"):
        (RAIZ / arq).parent.mkdir(parents=True, exist_ok=True)
        (RAIZ / arq).write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(d['motores'])} motores → config/ e docs/dados/descricao_motores.json")
