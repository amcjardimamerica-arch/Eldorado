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
 "do-goiania": {"pess": "43 leituras e 0 achado: lia o rótulo de uma página de serviço; a edição é um PDF de 240 páginas e o ato está dentro.",
                "otim": "o Querido Diário já indexa Goiânia: 232 edições na base, com o edital SEGENP 001/2026 (25/09, R$ 5 milhões, prazo 26/10) e o PNAB 006/2026.",
                "decide": "refeito em 01/10: lê o texto da edição pela nuvem, recorta em atos e classifica; a coleta local passa a ser reforço do dia, não condição."},
 "do-goias": {"pess": "em setembro não leu o Diário nenhum dia: 06–20/09 foi pulado e pintado de azul; desde 21/09 repetia 11 itens velhos das secretarias.",
              "otim": "o portal tem busca de texto completo, sumário por órgão e texto de cada matéria — e as prefeituras do interior publicam ali.",
              "decide": "refeito em 01/10: busca + edição do dia + API das secretarias, com o classificador comum; prova na primeira execução na nuvem."},
 "dou": {"pess": "em setembro leu no máximo 17% das matérias: a Seção 3 passava de 2,5 MB e vinha cortada (5 dias com 0 lidas), a Seção 1 nunca era lida, e os 14 'achados' eram extratos e editais de universidade.",
         "otim": "o DOU de setembro tinha 23 seleções reais para OSC — prefeituras de Goiás (PNAB, MROSC), IBAMA, ANATER, Caixa, Correios — e 833 extratos de parceria que mostram quem financia quem.",
         "decide": "refeito em 01/10: DO1 + DO3 + extras inteiras, íntegra das matérias de interesse e classificador comum com vetos federais; prova na primeira execução na nuvem."},
 "pncp-api": {"pess": "52 leituras e 0 achado: o sensor lia 3 das 11 URLs, vetava 'com ou sem fins lucrativos' e tomava 429; o coletor paralelo gravou 215 registros sem prazo, 206 fora de Goiás.",
              "otim": "os municípios de Goiás publicam ali, como credenciamento, chamamentos MROSC com data oficial de encerramento (Pirenópolis, Senador Canedo, Silvânia).",
              "decide": "refeito em 01/10: propostas abertas + busca do portal, vetos e finalidade; o PNCP segue vetor, o PDF do órgão é o documento oficial."},
 "camara-goiania-pl": {"pess": "40 leituras e 0 achado em setembro: lia a home do Plone, um SAPL com certificado inválido e páginas que dão 404; 3 a 5 falhas por dia.",
                       "otim": "o SUAP da Câmara tem todo projeto de lei com autor, setor e documentos datados — inclusive o PL 288/2026, que declara de utilidade pública a própria A.M.C. Jardim América.",
                       "decide": "refeito em 01/10: SUAP por assunto, tramitação da associação e notícias; utilidade pública vira lista de habilitação; edital da Câmara é raro e só entra com prazo."},
 "alego-pl": {"pess": "14 achados, todos de projetos de lei — não de editais.",
              "otim": "as emendas impositivas estaduais (janela out-nov) nascem aqui.",
              "decide": "manter; reclassificar os achados como 'insumo de emenda', não como oportunidade."},
 "congresso-nacional": {"pess": "motor novo (02/10): o Congresso quase não publica edital para OSC; as convocações do Senado desde 2017 não tiveram nenhuma para entidades; a área de emendas usava janela fixa, sem o prazo oficial da CMO.",
                        "otim": "o PLOA 2027 (PLN 24/2026) reserva R$ 28,5 bi em emendas individuais (≈ R$ 43 mi por deputado, R$ 79 mi por senador) e R$ 16,3 bi de bancada; as APIs da Câmara e do Senado mostram cada regra nova para entidades (MROSC, IBS/CBS, REFIS social).",
                        "decide": "criado em 02/10: CMO (etapa de emendas + comunicados), APIs das Casas, notícias e convocações; a janela oficial alimenta a área de emendas; proposição é insumo, nunca edital."},
 "judiciario-cnj-tjgo": {"pess": "motor novo (02/10): reúne dje-tjgo e cnj-destinacoes, que somaram 80 leituras e 0 achado — liam páginas 404 do TJGO, o Jusbrasil e a página de compras do CNJ; o TJGO recusa IP estrangeiro, então o essencial depende do computador do titular.",
                         "otim": "cada comarca abre o seu edital de prestações pecuniárias e o TJGO anuncia com o PDF (Goiânia 01/2026, Rio Verde 01/2026, Piracanjuba, Cocalzinho, Itaberaí); o RSS do TJGO pagina e traz tudo, e a regra exige só o cadastro no Banco de Projetos Sociais.",
                         "decide": "criado em 02/10: RSS do TJGO + notícia + PDF (local), busca do CNJ (nuvem), PNCP cruzado e habilitação prévia; Goiânia primeiro; edital de outro estado é ruído; DJEN desligado (só intimações com nomes de réus)."},
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
 "plat-gife": {"pess": "em setembro, 0 edital: a seleção mensal era lida, mas os links 'Inscreva-se/Acesse' têm rótulo curto e eram descartados; o único achado foi a ficha do associado Fundação FEAC; 1 erro por dia em /transparencia.",
               "otim": "a seleção do GIFE e a Capta trazem 3 a 6 editais de investidores sociais por mês, com prazo, valor e link oficial (Fundo Baobá, FAS, Impactarte, Viva Pequena África).",
               "decide": "refeito em 01/10: API do GIFE (Editais + busca) e da Capta, um item por bloco, prazo, público OSC e abrangência nacional ou Goiás; a ficha de associado nunca vira edital."},
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
