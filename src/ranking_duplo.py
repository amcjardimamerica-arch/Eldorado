"""DUAS LISTAS, DOIS CRITÉRIOS — e a mesma empresa pode estar nas duas.

São universos distintos, com finalidades distintas, e misturá-los produz um ranking que não
serve para nenhum dos dois pedidos:

    DESTINAÇÃO TRIBUTÁRIA   dinheiro que a empresa já deve ao fisco e escolhe para onde vai.
                            Não sai do caixa dela. O pedido vai ao setor fiscal ou à
                            contabilidade, depende de a empresa estar no Lucro Real, e tem
                            teto legal por lei. Quem decide é o CFO, e a conversa é técnica.

    DOAÇÃO E PATROCÍNIO     dinheiro do próprio bolso: patrocínio de evento, projeto social,
                            verba de marketing aplicada no terceiro setor. Sai do caixa. O
                            pedido vai ao marketing, ao instituto ou à diretoria, e a conversa
                            é de contrapartida e imagem.

Uma empresa pode aparecer só numa, só noutra, ou nas duas — com posição própria em cada,
porque o que a qualifica numa coisa não a qualifica na outra. Uma gigante do Lucro Real que
nunca patrocinou nada é excelente na primeira lista e irrelevante na segunda.

CADA CRITÉRIO DECLARA SE FOI APURADO. Um critério sem dado não vira zero silencioso: vira
"não levantado", e a confiança da nota cai. Assim dá para distinguir uma empresa que não doa
de uma sobre a qual ainda não se sabe nada — diferença que decide a quem escrever primeiro.
"""
from __future__ import annotations

import re

from .programas_sociais import programas_de

# ── critérios da DESTINAÇÃO TRIBUTÁRIA ──────────────────────────────────────────────
# Peso alto para o que prova que o caminho interno existe; capacidade vale menos que hábito.
CRITERIOS_FISCAL = [
    ("leis_com_historico", 30, "leis pelas quais já destinou",
     "cada lei usada prova que o setor fiscal já fez o caminho e a diretoria já aprovou"),
    ("diversidade", 10, "variedade de mecanismos",
     "usar mais de uma lei indica estrutura montada, não destinação isolada"),
    ("instituto", 15, "instituto ou fundação própria",
     "há quem cuide disso dentro da empresa, com verba e governança"),
    ("capacidade", 20, "porte tributário (Lucro Real)",
     "sem Lucro Real não há dedução: é condição, não mérito"),
    ("recorrencia", 15, "anos seguidos destinando",
     "destinar todo ano é rotina orçamentária; destinar uma vez foi evento"),
    ("valor", 10, "valores já destinados",
     "o quanto indica a faixa de pedido razoável"),
]

# ── critérios da DOAÇÃO E PATROCÍNIO ────────────────────────────────────────────────
# Aqui o que importa é o hábito de gastar do próprio bolso com causa social.
CRITERIOS_DOADORA = [
    ("patrocinio", 25, "patrocínio declarado a evento ou projeto",
     "já pagou do próprio caixa por visibilidade em causa social"),
    ("recorrencia", 15, "patrocina com regularidade",
     "verba recorrente tem dono e calendário; verba eventual depende de sobra"),
    ("instituto", 15, "instituto ou fundação própria",
     "canal permanente de doação, com critério publicado"),
    ("area_afim", 10, "apoia área próxima da nossa",
     "assistência, cultura, esporte ou comunidade — quem já apoia o parecido ouve melhor"),
    ("investimento_social", 12, "mapeada como investidora social",
     "aparece em fonte de investimento social privado (GIFE e afins)"),
    ("marketing_social", 13, "verba de marketing em causa social",
     "patrocínio de evento social é orçamento de marketing, e marketing tem verba anual"),
    ("valor_percentual", 10, "valores ou percentual do faturamento",
     "sem isso não dá para calibrar o pedido"),
]

AREAS_AFINS = ("assistência", "assistencia", "social", "comunidade", "cultura", "esporte",
               "criança", "crianca", "idoso", "educação", "educacao", "juventude",
               "inclusão", "inclusao", "alimentar", "vulnerab")


def _texto(e: dict) -> str:
    return " ".join(str(x) for x in (e.get("por") or [])
                    + [e.get("apoia"), e.get("programa"), e.get("via_de_entrada"), e.get("condicao")]
                    if x).lower()


def _crit(chave: str, peso: int, ponto: float, apurado: bool, valor: str, catalogo) -> dict:
    d = next((c for c in catalogo if c[0] == chave), (chave, peso, chave, ""))
    return {"chave": chave, "rotulo": d[2], "porque": d[3], "peso": peso,
            "pontos": round(min(ponto, peso), 1), "apurado": apurado,
            "valor": valor if apurado else "não levantado"}


def avaliar_fiscal(e: dict) -> dict:
    """A empresa como candidata a DIRECIONAR IMPOSTO."""
    progs = programas_de(e)
    com_hist = [p for p in progs if p["historico"]]
    t = _texto(e)
    cs = []

    cs.append(_crit("leis_com_historico", 30, 10 * len(com_hist), bool(progs),
                    ", ".join(p["nome"] for p in com_hist) or "nenhuma comprovada", CRITERIOS_FISCAL))
    cs.append(_crit("diversidade", 10, 5 * max(0, len(com_hist) - 1), bool(progs),
                    f"{len(com_hist)} mecanismo(s)", CRITERIOS_FISCAL))
    cs.append(_crit("instituto", 15, 15 if e.get("programa") else 0, True,
                    e.get("programa") or "não tem instituto próprio conhecido", CRITERIOS_FISCAL))
    icms = e.get("icms_goias")
    lucro = "lucro real" in t or bool(com_hist)
    cap = (20 if icms and int(icms) <= 20 else 15 if icms else 10 if lucro else 0)
    cs.append(_crit("capacidade", 20, cap, bool(icms) or lucro,
                    (f"{icms}º maior contribuinte do ICMS de Goiás" if icms else
                     "Lucro Real presumido pelo histórico de dedução"), CRITERIOS_FISCAL))
    anos = sorted({m for p in progs for m in re.findall(r"20\d\d", p.get("prova") or "")})
    cs.append(_crit("recorrencia", 15, 5 * len(anos), bool(anos),
                    f"destinou em {', '.join(anos)}" if anos else "", CRITERIOS_FISCAL))
    valores = re.findall(r"R\$ ?[\d\.]+", t)
    cs.append(_crit("valor", 10, 10 if valores else 0, bool(valores),
                    ", ".join(valores[:3]), CRITERIOS_FISCAL))
    return _fechar(cs, CRITERIOS_FISCAL, apto=bool(progs) or bool(icms) or lucro,
                   porta="setor fiscal ou contabilidade — é imposto devido, não doação")


def avaliar_doadora(e: dict) -> dict:
    """A empresa como candidata a DOAR OU PATROCINAR com verba própria."""
    t = _texto(e)
    cs = []
    patroc = bool(re.search(r"patroc|apoio a evento|naming|ativa[çc][ãa]o", t))
    cs.append(_crit("patrocinio", 25, 25 if patroc else 0, True,
                    "histórico público de patrocínio" if patroc else "nenhum patrocínio localizado",
                    CRITERIOS_DOADORA))
    rec = bool(re.search(r"recorrente|anual|todo ano|edi[çc][õo]es|h[áa] \d+ anos", t))
    cs.append(_crit("recorrencia", 15, 15 if rec else 0, rec, "patrocínio recorrente", CRITERIOS_DOADORA))
    cs.append(_crit("instituto", 15, 15 if e.get("programa") else 0, True,
                    e.get("programa") or "não tem instituto próprio conhecido", CRITERIOS_DOADORA))
    apoia = str(e.get("apoia") or "")
    afim = [a for a in AREAS_AFINS if a in (apoia + " " + t).lower()]
    cs.append(_crit("area_afim", 10, 10 if afim else 0, bool(apoia),
                    apoia or "área não declarada", CRITERIOS_DOADORA))
    gife = bool(e.get("gife")) or "gife" in t
    cs.append(_crit("investimento_social", 12, 12 if gife else 0, True,
                    "mapeada em fonte de investimento social" if gife else "não mapeada", CRITERIOS_DOADORA))
    mkt = bool(re.search(r"evento|festival|feira|show|jogo|campeonato|marketing", t))
    cs.append(_crit("marketing_social", 13, 13 if mkt else 0, mkt,
                    "verba de marketing aplicada em evento social", CRITERIOS_DOADORA))
    valores = re.findall(r"R\$ ?[\d\.]+|\d+% do faturamento", t)
    cs.append(_crit("valor_percentual", 10, 10 if valores else 0, bool(valores),
                    ", ".join(valores[:3]), CRITERIOS_DOADORA))
    return _fechar(cs, CRITERIOS_DOADORA,
                   apto=patroc or bool(e.get("programa")) or gife or bool(afim),
                   porta="marketing, instituto ou diretoria — sai do caixa, pede contrapartida")


def _fechar(cs: list[dict], catalogo, apto: bool, porta: str) -> dict:
    total = sum(c["pontos"] for c in cs)
    teto = sum(c[1] for c in catalogo)
    apurados = [c for c in cs if c["apurado"]]
    peso_apurado = sum(c["peso"] for c in apurados)
    conf = round(peso_apurado / teto, 2) if teto else 0.0
    falta = [{"rotulo": c["rotulo"], "porque": c["porque"], "peso": c["peso"]}
             for c in cs if not c["apurado"]]
    return {"apto": apto, "pontos": round(total, 1), "teto": teto,
            "percentual": round(100 * total / teto) if teto else 0,
            "criterios": cs, "falta_levantar": falta,
            "apurados": len(apurados), "total_criterios": len(cs),
            "confianca": conf,
            "nivel": ("forte" if total >= 0.55 * teto else "bom" if total >= 0.33 * teto
                      else "inicial" if total > 0 else "sem evidência"),
            "porta_de_entrada": porta}
