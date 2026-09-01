"""Parecer do conselho sobre o acervo histórico.

Depois da catalogação (fases 1 e 2), o conselho de 7 lentes emite um parecer
por edital: o que foi exigido, quem venceu, qual foi o fator decisivo e o que
esse caso ensina para as disputas atuais.

Honestidade acima de tudo: a maioria das publicações de diário traz apenas a
ementa. Onde o texto não nomeia vencedor nem critério, o parecer **declara a
lacuna** e o caso entra na fila de busca do ato integral — jamais se inventa
um vencedor ou um "fator decisivo".

O parecer roda em modo determinístico (sem custo). Com FAROL_AI_API_KEY, os
casos que efetivamente têm resultado publicado recebem também a leitura das
lentes por IA, priorizando os de maior valor — economia de tokens.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import date

from .biblioteca import OPORTUNIDADES
from .conselho_edital import PESOS, PONTOS_DE_VISTA, ROTULOS, sorteia_conselheiros
from .nucleo import ROOT, load_json, now_iso, write_json

SAIDA = ROOT / "biblioteca_alexandria/historico"


def _lentes(ficha: dict) -> dict:
    """As 7 posições sobre um edital já encerrado — o que ele ensina."""
    venc = ficha.get("vencedores_identificados") or []
    crit = ficha.get("criterios_de_julgamento") or []
    exig = ficha.get("exigencias_detectadas") or []
    tem_res = ficha.get("tem_resultado_publicado")
    valores = ficha.get("valores_citados") or []
    conselheiros = sorteia_conselheiros(f'{ficha["chave"]}|{ficha["ano"]}|historico')
    lentes = {}

    def add(pv, achados):
        lentes[pv] = {"rotulo": ROTULOS[pv], "peso": PESOS[pv],
                      "conselheiro": conselheiros[pv], "achados": achados}

    a = []
    if not tem_res:
        a.append("nenhum ato de homologação na evidência: não se sabe se houve "
                 "vencedor, deserção ou anulação")
    if not crit:
        a.append("critério de julgamento não publicado na ementa — replicar este "
                 "caso sem o edital integral é inseguro")
    if not exig:
        a.append("requisitos não detalhados: a ementa do diário não substitui o "
                 "edital para fins de habilitação")
    add("extremamente_pessimista", a or [
        "mesmo com resultado publicado, a ementa não revela a pontuação de cada "
        "concorrente — a comparação continua parcial"])

    a = []
    if tem_res and not venc:
        a.append("há resultado, mas o nome do vencedor não foi capturado: exige "
                 "busca do ato integral")
    if not valores:
        a.append("valor do certame não publicado na evidência")
    add("pessimista", a or ["dados suficientes para histórico, insuficientes para "
                            "reproduzir a proposta vencedora"])

    a = []
    if exig and len(exig) < 4:
        a.append(f"apenas {len(exig)} exigência(s) identificada(s): amostra pequena "
                 "para inferir padrão")
    add("levemente_pessimista", a or ["caso utilizável como referência, desde que "
                                      "confirmado no edital de origem"])

    a = []
    if exig:
        a.append("exigências recuperadas para o histórico: " + ", ".join(exig[:6]))
    if ficha.get("fim"):
        a.append(f'prazo de encerramento datado ({ficha["fim"]}): serve para prever '
                 "a janela do mesmo financiador")
    add("levemente_otimista", a or ["caso incorporado ao acervo, mesmo sem detalhe"])

    a = []
    if venc:
        a.append("vencedor(es) identificado(s): " + "; ".join(venc[:3]))
    if crit:
        a.append("critério de julgamento capturado: " + crit[0][:120])
    if valores:
        a.append(f'valor citado: R$ {valores[0]}')
    add("otimista", a or ["financiador e território registrados: base para mapear "
                          "recorrência"])

    a = []
    if venc and crit:
        a.append("caso completo — vencedor e critério conhecidos: modelo direto do "
                 "que este financiador premia")
    elif venc:
        a.append("perfil do vencedor conhecido: referência de porte e natureza da "
                 "entidade que este financiador aprova")
    a.append("cada caso catalogado aumenta a previsibilidade das próximas janelas")
    add("extremamente_otimista", a)

    # neutro: o que este caso ensina, com a lacuna declarada
    if venc and crit:
        leitura = ("caso com vencedor e critério publicados — replicável como "
                   "referência direta")
        forca = "alta"
    elif venc:
        leitura = ("vencedor conhecido, critério não publicado — usar para perfil "
                   "de entidade aprovada, não para estratégia de pontuação")
        forca = "media"
    elif tem_res:
        leitura = ("resultado publicado sem nomeação na evidência — buscar o ato "
                   "integral antes de usar como referência")
        forca = "baixa"
    else:
        leitura = ("sem resultado publicado — vale como registro de exigências e "
                   "janela, não como padrão de aprovação")
        forca = "baixa"
    lentes["neutro"] = {
        "rotulo": ROTULOS["neutro"], "peso": 0,
        "conselheiro": conselheiros["neutro"],
        "leitura": leitura, "forca_probatoria": forca,
        "fator_decisivo": (crit[0][:200] if crit else None),
        "vencedores": venc,
        "lacunas": ficha.get("lacunas", []),
        "uso_recomendado": (
            "referência de estratégia" if forca == "alta" else
            "referência de perfil de entidade" if forca == "media" else
            "registro de exigências e janela"),
    }
    return lentes


def parecer_do_edital(ficha: dict) -> dict:
    lentes = _lentes(ficha)
    n = lentes["neutro"]
    return {
        "edital": {"chave": ficha["chave"], "ano": ficha["ano"],
                   "titulo": ficha.get("titulo"), "financiador": ficha.get("financiador"),
                   "territorio": ficha.get("territorio"), "area": ficha.get("area"),
                   "data_publicacao": ficha.get("data_publicacao"),
                   "estado_prazo": ficha.get("estado_prazo")},
        "requisitos_identificados": ficha.get("exigencias_detectadas", []),
        "vencedores": n["vencedores"],
        "fator_decisivo": n["fator_decisivo"],
        "forca_probatoria": n["forca_probatoria"],
        "leitura_do_conselho": n["leitura"],
        "uso_recomendado": n["uso_recomendado"],
        "lacunas": n["lacunas"],
        "conselheiros": {pv: lentes[pv]["conselheiro"] for pv in PONTOS_DE_VISTA},
        "lentes": lentes,
        "modo": "deterministico",
        "gerado_em": now_iso(),
    }


def run(limite: int | None = None) -> dict:
    """Emite o parecer de cada edital catalogado e consolida o histórico de
    vencedores e critérios, para orientar as disputas atuais."""
    if not OPORTUNIDADES.exists():
        return {"executado_em": now_iso(), "pareceres": 0,
                "nota": "nenhum edital catalogado"}
    fichas = sorted(OPORTUNIDADES.glob("*/*/ficha.json"))
    if limite:
        fichas = fichas[:limite]
    total = com_vencedor = com_criterio = 0
    vencedores: Counter = Counter()
    criterios: Counter = Counter()
    exigencias: Counter = Counter()
    por_financiador: dict[str, dict] = defaultdict(
        lambda: {"casos": 0, "vencedores": [], "criterios": [], "meses": Counter()})
    fila_busca = []

    for fp in fichas:
        ficha = load_json(fp)
        if ficha.get("origem") != "catalogacao_historica_5_anos":
            continue
        p = parecer_do_edital(ficha)
        write_json(fp.parent / "parecer_historico.json", p)
        total += 1
        fin = ficha.get("financiador") or "—"
        por_financiador[fin]["casos"] += 1
        if ficha.get("fim"):
            por_financiador[fin]["meses"][ficha["fim"][5:7]] += 1
        for v in p["vencedores"]:
            vencedores[v] += 1
            por_financiador[fin]["vencedores"].append(v)
        if p["vencedores"]:
            com_vencedor += 1
        if p["fator_decisivo"]:
            com_criterio += 1
            criterios[p["fator_decisivo"][:120]] += 1
            por_financiador[fin]["criterios"].append(p["fator_decisivo"][:120])
        exigencias.update(ficha.get("exigencias_detectadas") or [])
        if ficha.get("tem_resultado_publicado") and not p["vencedores"]:
            fila_busca.append({"chave": ficha["chave"], "ano": ficha["ano"],
                               "url": ficha.get("url"),
                               "motivo": "resultado publicado sem nomeação do "
                                         "vencedor na evidência"})

    recorrencias = []
    for fin, d in por_financiador.items():
        for mes, n in d["meses"].items():
            if n >= 2:
                recorrencias.append({"financiador": fin, "mes": mes, "ocorrencias": n,
                                     "leitura": "janela recorrente — hipótese a confirmar"})

    consolidado = {
        "executado_em": now_iso(),
        "editais_com_parecer": total,
        "com_vencedor_identificado": com_vencedor,
        "com_fator_decisivo": com_criterio,
        "cobertura_vencedores": round(com_vencedor / total * 100, 2) if total else 0,
        "vencedores_recorrentes": [{"entidade": e, "vitorias": n}
                                   for e, n in vencedores.most_common(40)],
        "criterios_mais_citados": [{"criterio": c, "ocorrencias": n}
                                   for c, n in criterios.most_common(20)],
        "exigencias_mais_cobradas": [{"exigencia": e, "ocorrencias": n}
                                     for e, n in exigencias.most_common(30)],
        "recorrencias_por_financiador": sorted(recorrencias,
                                               key=lambda r: -r["ocorrencias"])[:40],
        "fila_busca_ato_integral": fila_busca[:200],
        "nota": ("vencedores e critérios saem exclusivamente do texto publicado; "
                 "onde a evidência não nomeia, a lacuna fica declarada e o caso "
                 "entra na fila de busca do ato integral"),
    }
    SAIDA.mkdir(parents=True, exist_ok=True)
    write_json(SAIDA / "consolidado.json", consolidado)
    return consolidado


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2)[:2500])
