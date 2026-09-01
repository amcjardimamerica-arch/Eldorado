"""Etapa 3 · Conselho de 7 lentes sobre o edital — corrobora a etapa 4.

Premissa do titular: toda análise passa por um conselho de sete posições —
extremamente pessimista, pessimista, levemente pessimista, neutro, levemente
otimista, otimista e extremamente otimista. Os pessimistas procuram falhas e
defeitos; os otimistas, as vantagens e virtudes alcançáveis; o **neutro**
pondera de forma imparcial, fecha a decisão e fixa parâmetros de qualidade e
mitigação de riscos.

Como a matéria é jurídica (habilitação, requisitos, prestação de contas), os
conselheiros têm o peso de ministros de tribunais superiores, doutrinadores e
advogados pós-doutores no tema — sorteados a cada análise. Usamos ARQUÉTIPOS,
não nomes de pessoas reais: o repositório é público e nomes reais criariam
risco de direitos da personalidade (o conselho de personalidades históricas
segue existindo em `src/conselho.py`, para os casos internos).

**O voto do neutro é vinculante para a etapa 4.** A decisão automática de
concorrer só ocorre se o conselho corroborar; do contrário o edital vai para
«regularizar antes» ou «descartar», com o fundamento registrado.

Economia de tokens: as seis lentes usam o modelo intermediário, uma chamada
curta cada, sobre o pacote mínimo; só a síntese do neutro usa o modelo forte.
Sem credencial, o conselho roda determinístico — cada lente tem verificações
próprias — e declara a pendência. Nunca simula IA.
"""
from __future__ import annotations

import json
import random
import re
from datetime import date

from .nucleo import ROOT, load_json, now_iso

PONTOS_DE_VISTA = ("extremamente_pessimista", "pessimista", "levemente_pessimista",
                   "neutro", "levemente_otimista", "otimista", "extremamente_otimista")
ROTULOS = {
    "extremamente_pessimista": "Extremamente pessimista",
    "pessimista": "Pessimista",
    "levemente_pessimista": "Levemente pessimista",
    "neutro": "Neutro (ponderador)",
    "levemente_otimista": "Levemente otimista",
    "otimista": "Otimista",
    "extremamente_otimista": "Extremamente otimista",
}
PESOS = {"extremamente_pessimista": -3, "pessimista": -2, "levemente_pessimista": -1,
         "neutro": 0, "levemente_otimista": 1, "otimista": 2,
         "extremamente_otimista": 3}

ARQUETIPOS = (
    "Ministro(a) de tribunal superior, relator(a) em controle de contas públicas",
    "Doutrinador(a) de direito administrativo, autor(a) de tratado sobre parcerias",
    "Advogado(a) pós-doutor(a) em terceiro setor e MROSC",
    "Procurador(a) de contas com atuação em fomento e convênios",
    "Professor(a) titular de licitações e contratos administrativos",
    "Conselheiro(a) de tribunal de contas estadual, relator(a) de prestações",
    "Advogado(a) pós-doutor(a) em direito financeiro e compliance de OSCs",
    "Desembargador(a) com atuação em direito público e improbidade",
    "Doutrinador(a) de direito constitucional aplicado ao terceiro setor",
    "Parecerista pós-doutor(a) em governança de entidades sem fins lucrativos",
)


def sorteia_conselheiros(semente: str) -> dict[str, str]:
    """Personalidades distintas e aleatórias a cada análise (reprodutível)."""
    r = random.Random(semente)
    escolhidos = r.sample(ARQUETIPOS, len(PONTOS_DE_VISTA))
    return dict(zip(PONTOS_DE_VISTA, escolhidos))


# ------------------------------------------------------ lentes determinísticas
def _achados(lente: str, ctx: dict) -> list[str]:
    a: list[str] = []
    faltam, alertas = ctx["faltam"], ctx["alertas"]
    docs_falta, dias = ctx["docs_faltantes"], ctx["dias_para_fim"]

    if lente == "extremamente_pessimista":
        if faltam:
            a.append(f"requisito eliminatório em falta ({', '.join(faltam)}): "
                     "inabilitação certa se protocolar assim")
        if dias is not None and dias <= 7:
            a.append(f"restam {dias} dia(s): risco concreto de certidão vencer "
                     "antes do protocolo ou de fila em cartório")
        if len(docs_falta) >= 5:
            a.append(f"{len(docs_falta)} documentos ausentes — volume incompatível "
                     "com o prazo remanescente")
        if not ctx["historico_ocorrencias"]:
            a.append("sem histórico deste financiador na Biblioteca: critérios de "
                     "julgamento desconhecidos, disputa às cegas")
        if not a:
            a.append("nenhuma falha estrutural aparente — o que não equivale a "
                     "habilitação assegurada; a análise do órgão é soberana")
    elif lente == "pessimista":
        if docs_falta:
            a.append("pendências documentais: "
                     + ", ".join(d["documento"].replace("_", " ") for d in docs_falta[:4]))
        if not ctx["perfil_completo"]:
            a.append("cadastro público incompleto: campos sem dado impedem o "
                     "preenchimento automático dos modelos")
        if alertas:
            a.append(f"{len(alertas)} exigência(s) do edital ainda não comprovadas")
        if not a:
            a.append("documentação reunida, mas resta o risco de divergência "
                     "formal na conferência do órgão")
    elif lente == "levemente_pessimista":
        if alertas:
            a.append("dependem de confirmação: " + "; ".join(alertas[:3]))
        if dias is not None and 7 < dias <= 20:
            a.append(f"janela de {dias} dias é apertada para obter certidões e "
                     "revisar o plano de trabalho")
        if not a:
            a.append("cenário controlável, desde que a revisão final confira cada "
                     "documento contra a lista literal do edital")
    elif lente == "levemente_otimista":
        if ctx["atende"]:
            a.append("requisitos objetivos já atendidos: " + ", ".join(ctx["atende"]))
        if ctx["modelos"]:
            a.append(f"{ctx['modelos']} modelo(s) do edital preservados e prontos "
                     "para preenchimento")
        if not a:
            a.append("nada impede a participação; o caminho é reunir o que falta")
    elif lente == "otimista":
        if ctx["area_aderente"]:
            a.append("objeto do edital aderente à área de atuação da entidade")
        if dias is not None and dias > 20:
            a.append(f"{dias} dias de prazo: tempo suficiente para reunir a "
                     "documentação e qualificar a proposta")
        if ctx["historico_ocorrencias"]:
            a.append(f"{ctx['historico_ocorrencias']} ocorrência(s) deste "
                     "financiador no histórico: exigências previsíveis")
        if not a:
            a.append("oportunidade compatível com o porte e a atuação da entidade")
    elif lente == "extremamente_otimista":
        if not faltam:
            a.append("sem requisito eliminatório pendente: habilitação plenamente "
                     "alcançável nesta janela")
        if ctx["valor_texto"]:
            a.append(f"recurso em disputa: {ctx['valor_texto']}")
        a.append("aprovação gera experiência comprovada, útil como pontuação nos "
                 "próximos editais do mesmo financiador")
    return a


def _ponderacao_neutra(ctx: dict, vistas: dict) -> dict:
    faltam, docs_falta = ctx["faltam"], ctx["docs_faltantes"]
    dias = ctx["dias_para_fim"]
    if faltam:
        decisao = "descartar"
        fundamento = ("requisito eliminatório não atendido — protocolar geraria "
                      "inabilitação e consumiria trabalho sem chance de êxito")
    elif docs_falta and dias is not None and dias <= 7 and len(docs_falta) >= 4:
        decisao = "regularizar antes"
        fundamento = (f"{len(docs_falta)} documentos pendentes para {dias} dia(s) "
                      "de prazo: risco alto de protocolo incompleto")
    elif docs_falta:
        decisao = "concorrer"
        fundamento = (f"nenhum impedimento eliminatório; {len(docs_falta)} "
                      "documento(s) a providenciar dentro do prazo")
    else:
        decisao = "concorrer"
        fundamento = "requisitos atendidos e documentação reunida"
    parametros = [
        "conferir cada documento contra a lista literal do edital antes do protocolo",
        "certidões válidas na data do protocolo, não apenas na de emissão",
        "plano de trabalho e planilha preenchidos no modelo do próprio edital",
        "campo sem informação vai para a nota técnica — nada é preenchido por suposição",
    ]
    if dias is not None and dias <= 15:
        parametros.append(f"prazo curto ({dias} dias): providenciar primeiro o que "
                          "depende de terceiros (certidões e cartório)")
    mitigacao = [{"risco": d["documento"].replace("_", " "), "acao": d["como_obter"]}
                 for d in docs_falta[:8]]
    mitigacao += [{"risco": al, "acao": "confirmar no texto do edital e arquivar a "
                                        "comprovação na pasta do caso"}
                  for al in ctx["alertas"][:4]]
    return {"decisao": decisao, "fundamento": fundamento,
            "parametros_de_qualidade": parametros,
            "mitigacao_de_riscos": mitigacao,
            "pontos_considerados": {k: len(v) for k, v in vistas.items()}}


def _contexto(edital: dict, avaliacao: dict, contexto: dict, hoje: date) -> dict:
    fim = edital.get("fim")
    return {
        "faltam": avaliacao.get("faltam", []),
        "atende": avaliacao.get("atende", []),
        "alertas": avaliacao.get("alertas", []),
        "docs_faltantes": contexto.get("documentos_faltantes", []),
        "dias_para_fim": (date.fromisoformat(fim) - hoje).days if fim else None,
        "historico_ocorrencias": contexto.get("historico_ocorrencias", 0),
        "modelos": contexto.get("modelos", 0),
        "area_aderente": contexto.get("area_aderente", False),
        "perfil_completo": contexto.get("perfil_completo", False),
        "valor_texto": edital.get("valor_texto"),
    }


def deliberar(edital: dict, avaliacao: dict, contexto: dict,
              hoje: date | None = None) -> dict:
    """Conselho determinístico: sempre roda, com ou sem credencial."""
    hoje = hoje or date.today()
    ctx = _contexto(edital, avaliacao, contexto, hoje)
    conselheiros = sorteia_conselheiros(
        f'{edital.get("chave")}|{avaliacao.get("slug")}|{edital.get("ano")}')
    lentes, vistas = {}, {}
    for pv in PONTOS_DE_VISTA:
        if pv == "neutro":
            continue
        achados = _achados(pv, ctx)
        vistas[pv] = achados
        lentes[pv] = {"rotulo": ROTULOS[pv], "peso": PESOS[pv],
                      "conselheiro": conselheiros[pv], "achados": achados}
    neutro = _ponderacao_neutra(ctx, vistas)
    lentes["neutro"] = {"rotulo": ROTULOS["neutro"], "peso": 0,
                        "conselheiro": conselheiros["neutro"], **neutro}
    return {"executado_em": now_iso(), "modo": "deterministico",
            "conselheiros": conselheiros, "lentes": lentes,
            "decisao": neutro["decisao"], "fundamento": neutro["fundamento"],
            "parametros_de_qualidade": neutro["parametros_de_qualidade"],
            "mitigacao_de_riscos": neutro["mitigacao_de_riscos"],
            "vinculante_para_etapa_4": True,
            "nota": ("conselho determinístico; a redação das lentes por IA roda "
                     "quando FAROL_AI_API_KEY estiver configurada")}


def deliberar_com_ia(edital: dict, avaliacao: dict, contexto: dict,
                     trechos: list[str] | None = None,
                     historico: dict | None = None,
                     hoje: date | None = None) -> dict:
    """Mesmo conselho, com as lentes redigidas pela IA quando há credencial."""
    base = deliberar(edital, avaliacao, contexto, hoje)
    from .farol_parecer import _cfg, _chamar, _chave
    if not _chave():
        return base
    cfg = _cfg()["modelos"]
    sistema = ("Você integra um conselho jurídico que analisa editais para "
               "organizações da sociedade civil no Brasil. Responda SOMENTE com "
               "base no material fornecido. Nunca invente exigência, valor, prazo "
               "ou critério: o que não constar deve ser apontado como dado "
               "faltante. Seja técnico e objetivo, em português do Brasil.")
    pacote = json.dumps({
        "edital": {k: edital.get(k) for k in ("titulo", "fonte_nome", "inicio",
                                              "fim", "valor_texto")},
        "portao_objetivo": avaliacao, "contexto": contexto,
        "historico": historico or {}, "trechos": (trechos or [])[:40],
    }, ensure_ascii=False)[:14000]
    for pv in PONTOS_DE_VISTA:
        if pv == "neutro":
            continue
        foco = ("aponte falhas, riscos e motivos de inabilitação" if PESOS[pv] < 0
                else "aponte vantagens, virtudes e o melhor resultado alcançável")
        try:
            texto = _chamar(cfg["analise"], sistema,
                            f'Você é {base["conselheiros"][pv]}. Sua posição no '
                            f"conselho é {ROTULOS[pv].upper()}. {foco.capitalize()}. "
                            "Liste de 2 a 4 pontos objetivos, um por linha, "
                            f"começando por '- '.\n\nMATERIAL:\n{pacote}",
                            max_tokens=600)
            base["lentes"][pv]["achados_ia"] = [
                l.lstrip("- ").strip() for l in texto.splitlines()
                if l.strip().startswith("-")]
        except Exception as exc:
            base["lentes"][pv]["erro_ia"] = type(exc).__name__
    try:
        resumo = json.dumps({k: v.get("achados_ia") or v.get("achados")
                             for k, v in base["lentes"].items() if k != "neutro"},
                            ensure_ascii=False)[:9000]
        sintese = _chamar(cfg["parecer"], sistema,
                          f'Você é {base["conselheiros"]["neutro"]}, o NEUTRO: '
                          "pondere as seis posições de forma imparcial e feche a "
                          "decisão. Responda em JSON com decisao (CONCORRER, "
                          "REGULARIZAR ANTES ou DESCARTAR), fundamento, "
                          "parametros_de_qualidade (lista) e mitigacao_de_riscos "
                          "(lista de {risco, acao}). Só JSON.\n\nPOSIÇÕES:\n"
                          + resumo + "\n\nPORTÃO OBJETIVO:\n"
                          + json.dumps(avaliacao, ensure_ascii=False), max_tokens=1500)
        dados = json.loads(re.sub(r"^```(?:json)?|```$", "", sintese.strip(),
                                  flags=re.M).strip())
        base["lentes"]["neutro"]["sintese_ia"] = dados
        # o portão objetivo prevalece: a IA não pode liberar requisito em falta
        if not avaliacao.get("bloqueio_objetivo"):
            d = str(dados.get("decisao", "")).lower()
            if "descartar" in d:
                base["decisao"] = "descartar"
            elif "regularizar" in d:
                base["decisao"] = "regularizar antes"
            elif "concorrer" in d:
                base["decisao"] = "concorrer"
            for campo in ("fundamento", "parametros_de_qualidade", "mitigacao_de_riscos"):
                if dados.get(campo):
                    base[campo] = dados[campo]
        base["modo"] = "conselho_com_ia"
    except Exception as exc:
        base["erro_sintese"] = type(exc).__name__
    return base


if __name__ == "__main__":
    print(json.dumps(deliberar(
        {"chave": "x", "ano": "2026", "titulo": "Edital 1/2026",
         "fim": "2026-09-30", "valor_texto": "R$ 200.000,00"},
        {"slug": "a", "associacao": "Assoc", "faltam": [], "atende": ["cebas"],
         "alertas": ["plano de trabalho: exigido no edital — confirmar"],
         "bloqueio_objetivo": False},
        {"documentos_faltantes": [{"documento": "certidao_fgts",
                                   "como_obter": "CRF na Caixa"}],
         "historico_ocorrencias": 2, "modelos": 1, "area_aderente": True,
         "perfil_completo": True},
        date(2026, 9, 1)), ensure_ascii=False, indent=2))
