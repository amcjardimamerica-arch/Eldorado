"""AUDITORIA DOS MOTORES DE BUSCA — 20/09/2026 — com parecer do conselho por motor.

Produz estado/auditoria_motores.json e docs/dados/auditoria_motores.json a partir do
que cada motor REALMENTE fez (esquadra.json, bloqueios, achados), classifica cada um
em quatro estados honestos e dá o parecer do conselho (pessimista → otimista → neutro
que decide) para cada.

Estados possíveis de um motor:
  FUNCIONANDO ........ leu nos últimos 7 dias e já entregou edital alguma vez
  LENDO SEM ACHAR .... leu nos últimos 7 dias, nunca entregou edital (léxico? formato? fonte errada?)
  PARADO ............. não lê há mais de 7 dias (cadência P21 violada)
  NUNCA RODOU ........ não tem leitura registrada
  BLOQUEADO .......... a última leitura falhou em todas as páginas

A regra de ouro segue a auditoria de 09/09: o problema do sistema não é bloqueio, é
DEGRADAÇÃO SILENCIOSA — fontes mudam e ninguém percebe. Cada motor aqui tem a causa
e a correção escritas.
"""
from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json

CADENCIA = 7   # dias (P21: art. 26 da Lei 13.019/2014 → 30 dias de antecedência → 4 chances)

# parecer do conselho por motor (id → dict). O neutro decide.
CONSELHO = {
 "do-goiania": {"pess": "recusa IP estrangeiro há semanas; só lê pela coleta local, que nunca foi rodada.",
                "otim": "é o diário da cidade da associação: todo chamamento da SEMASDH, CMDCA e CMAS passa aqui.",
                "decide": "manter; a coleta local (.bat) é o único desbloqueio real — prioridade 1 do titular."},
 "do-goias": {"pess": "lê 200 mas zero achado em 20 dias: ou o léxico não casa com o formato do ABC, ou o ato fica no PDF.",
              "otim": "é onde saem os editais da SECULT, SEDS, SES e os decretos de emenda impositiva.",
              "decide": "manter e abrir o PDF da edição: o ato está dentro, não no índice."},
 "dou": {"pess": "regrediu de 368 matérias/dia para zero por mudança de seletor; corrigido, mas só 2 achados desde então.",
         "otim": "é a fonte federal: MDHC, CONANDA, Rouanet, MinC, emendas.",
         "decide": "manter; validar por 7 dias se o JSON volta a trazer matérias — se não, ler a seção 3 pela busca avançada."},
 "pncp-api": {"pess": "311 de 317 registros citam a Lei 14.133 e nenhum a 13.019: a via do PNCP é a da contratação.",
              "otim": "é o único lugar onde 5.570 municípios publicam de forma padronizada; o arquivo do edital hospedado lá é documento oficial.",
              "decide": "manter como DESCOBERTA (número do processo + órgão), nunca como fonte; o filtro de objeto já barra o ruído."},
 "camara-goiania-pl": {"pess": "lê e não acha: projetos de utilidade pública raramente vêm com edital.",
                       "otim": "é onde nascem as declarações de utilidade pública municipal, requisito de vários editais.",
                       "decide": "manter em cadência semanal, não diária: é insumo de habilitação, não de captação."},
 "alego-pl": {"pess": "14 achados, todos de projetos de lei — não de editais.",
              "otim": "as emendas impositivas estaduais (janela out-nov) nascem aqui.",
              "decide": "manter; reclassificar os achados como 'insumo de emenda', não como oportunidade."},
 "dj-trf1-go": {"pess": "zero achados sempre; destinações de pena federais são raras em Goiás.",
                "otim": "quando vem, vem sem edital e sem disputa.",
                "decide": "reduzir para cadência semanal."},
 "dje-tjgo": {"pess": "50 recusas do WAF Cloudflare; não lê há semanas.",
              "otim": "as varas de execução penal de Goiânia destinam prestações pecuniárias a entidades — dinheiro certo, sem edital.",
              "decide": "manter; só a coleta local desbloqueia — junto com o DO-Goiânia é a prioridade 1."},
 "cnj-destinacoes": {"pess": "lê 200 e nunca achou: a página do CNJ é institucional, não lista destinações.",
                     "otim": "as destinações de pena são a família mais subexplorada do sistema.",
                     "decide": "TROCAR a rota: a fonte real são os tribunais estaduais (TJGO já coberto) — CNJ vira referência, não motor."},
 "empresas-incentivadas": {"pess": "1 achado em 20 dias procurando o SITE da empresa.",
                           "otim": "o radar mostrou o Porto Itapoá publicando EDITAL próprio de renúncia fiscal — modelo replicável.",
                           "decide": "manter e SOMAR o motor novo 'empresas-editais-incentivados', que procura o edital e não o site."},
 "plat-observatorio-3setor": {"pess": "portal de notícia: anuncia, não publica; guardou mídia kit como se fosse edital.",
                              "otim": "foi o motor mais produtivo em achados (21) — é onde o privado nacional aparece primeiro.",
                              "decide": "manter como DESCOBERTA; a fonte oficial é sempre localizada depois."},
 "plat-abcr": {"pess": "idem: vetor de divulgação, 2 recusas em setembro.",
               "otim": "23 achados, o segundo mais produtivo.",
               "decide": "manter como descoberta; nunca como fonte."},
 "plat-gife": {"pess": "lê a home institucional, nunca achou edital.",
               "otim": "os associados do GIFE são os maiores investidores sociais do país.",
               "decide": "TROCAR a URL para a agenda/oportunidades dos associados; a home não serve."},
 "plat-prosas": {"pess": "nunca rodou: descartada por deduplicação de URL contra os 260 pontos.",
                 "otim": "é a maior plataforma de editais do terceiro setor no Brasil.",
                 "decide": "CORRIGIDO hoje: passa a ter sensor próprio e roda todo dia."},
 "plat-prosas-premios": {"pess": "lê e não reconhece: prêmios a pessoa física não são fomento a OSC.",
                         "otim": "alguns prêmios aceitam OSC e pagam bem.",
                         "decide": "manter com o filtro de objeto ativo."},
 "plat-salic": {"pess": "nunca rodou (mesma deduplicação); a página do MinC não declara a data-limite.",
                "otim": "Rouanet é a oportunidade nacional mais relevante para a A.M.C.",
                "decide": "CORRIGIDO hoje; ler a IN vigente para a janela."},
 "plat-secult-go": {"pess": "nunca rodou; e a página de termos de fomento é armadilha (já celebrados).",
                    "otim": "os 18 editais do PNAB Goiás Ciclo 2 saíram daqui e o sistema não viu.",
                    "decide": "CORRIGIDO hoje; as 5 rotas (Chamamentos, Goyazes, Fundo, PNAB, LPG) já estão na curadoria."},
 "plat-ovg": {"pess": "novo: sem histórico, sem léxico calibrado.",
              "otim": "maior operador de repasses a entidades de Goiás com UMA fonte no catálogo — a lacuna mais cara.",
              "decide": "INCLUÍDO hoje; primeira leitura na próxima saída."},
 "plat-goias-social": {"pess": "novo; risco de página institucional sem edital.",
                       "otim": "abriga o Auxílio Nutricional que já validamos.",
                       "decide": "INCLUÍDO hoje."},
 "plat-fundos-estaduais-go": {"pess": "novo; fundos publicam via conselho, em resolução, não em edital.",
                              "otim": "FIA-GO, Idoso, FUNJUVE e FEMA são recursos com destinatário obrigatório: entidades.",
                              "decide": "INCLUÍDO hoje; ler também as resoluções dos conselhos."},
 "plat-fapeg": {"pess": "novo; FAP financia pesquisa, OSC só entra como parceira.",
                "otim": "FAPERGS e FAPESC apareceram no radar financiando terceiro setor.",
                "decide": "INCLUÍDO hoje em cadência semanal."},
 "plat-prefeituras-50-go": {"pess": "novo; 50 portais heterogêneos, muitos bloqueiam IP estrangeiro.",
                            "otim": "7 dos 25 editais do radar vieram de prefeituras médias — é a lacuna de cobertura nº 1 (zero fontes diretas).",
                            "decide": "INCLUÍDO hoje; começa por Goiânia, Aparecida, Anápolis, Rio Verde, Luziânia; coleta local para os bloqueados."},
 "plat-empresas-editais-incentivados": {"pess": "novo; poucas empresas publicam edital próprio.",
                                        "otim": "quem publica (Porto Itapoá, Renner, Maria Emília) distribui milhões sem disputa política.",
                                        "decide": "INCLUÍDO hoje; cruzar com o ranking de 100 empresas de Goiás."},
 "plat-mp-destinacoes-reparacao": {"pess": "novo; cada MP tem portal próprio.",
                                   "otim": "MPMG, MPF e MPSE distribuíram reparação a OSC no radar; MPGO tem edital próprio.",
                                   "decide": "INCLUÍDO hoje; MPGO primeiro."},
 "plat-cnpq-extensao": {"pess": "novo; chamadas exigem ICT proponente.",
                        "otim": "extensão e popularização da ciência aceitam OSC parceira; Setec/MEC idem.",
                        "decide": "INCLUÍDO hoje em cadência semanal."},
}


def _estado(s: dict, hoje: date) -> tuple[str, str]:
    ult = (s.get("ultima") or "")[:10]
    if not ult:
        return "NUNCA RODOU", "sem leitura registrada"
    dias = (hoje - date.fromisoformat(ult)).days
    saude = s.get("saude") or []
    if saude and all(x.get("erro") for x in saude):
        return "BLOQUEADO", f"todas as páginas falharam em {ult}"
    if dias > CADENCIA:
        return "PARADO", f"{dias} dias sem leitura (cadência de {CADENCIA})"
    if (s.get("achados_total") or 0) > 0:
        return "FUNCIONANDO", f"leu em {ult}; {s.get('achados_total')} achado(s) acumulado(s)"
    return "LENDO SEM ACHAR", f"leu em {ult}; nunca reconheceu edital"


def run() -> dict:
    from .sensores import registro
    hoje = date.today()
    esq = load_json(ROOT / "estado/esquadra.json").get("sensores", {}) if (ROOT / "estado/esquadra.json").exists() else {}
    regulares = [s for s in registro() if not s.get("fontes_260")]
    itens = []
    for s in regulares:
        e = esq.get(s["id"]) or {}
        est, base = _estado(e, hoje)
        c = CONSELHO.get(s["id"], {})
        itens.append({"id": s["id"], "nome": s["nome"], "tipo": s["tipo"], "estado": est, "base": base,
                      "ultima": (e.get("ultima") or "")[:16], "achados_total": e.get("achados_total") or 0,
                      "conselho": {"pessimista": c.get("pess"), "otimista": c.get("otim"), "neutro_decide": c.get("decide")}
                      if c else {"neutro_decide": "sem parecer registrado — avaliar na próxima auditoria"}})
    ordem = {"BLOQUEADO": 0, "PARADO": 1, "NUNCA RODOU": 2, "LENDO SEM ACHAR": 3, "FUNCIONANDO": 4}
    itens.sort(key=lambda x: (ordem[x["estado"]], x["id"]))
    resumo = {k: sum(1 for x in itens if x["estado"] == k) for k in ordem}
    res = {"em": now_iso(), "cadencia_dias": CADENCIA, "total": len(itens), "por_estado": resumo,
           "correcoes_de_hoje": [
               "regulares nunca mais são cortados pelo limite de 40 por execução (as 4 plataformas ficaram 14 dias sem rodar por isso)",
               "toda plataforma configurada vira sensor próprio (Prosas, SALIC e Secult-GO nunca tinham rodado por deduplicação de URL)",
               "8 motores novos a partir do radar de 16/09 e da lacuna medida: OVG, Goiás Social, fundos estaduais GO, FAPEG, prefeituras das 50 maiores, editais de empresas incentivadoras, MPs de reparação, CNPq/Setec de extensão",
               "Mapa das OSC mantido desativado com motivo (base cadastral, não publica edital)",
           ],
           "itens": itens}
    write_json(ROOT / "estado/auditoria_motores.json", res)
    write_json(ROOT / "docs/dados/auditoria_motores.json", res)
    return {k: v for k, v in res.items() if k != "itens"}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
