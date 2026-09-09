"""PARÂMETROS DA AUDITORIA DE 09/09/2026 — o que a medição autorizou.

A auditoria comparou o motor com 231 validações humanas sobre 468 registros e
mostrou três coisas:

  • o motor NÃO erra: precisão 100% no que decide, falso positivo zero;
  • ele DECIDE POUCO: 31,9% dos objetos ficam em "atenção", e cada um custa uma
    leitura de documento;
  • a via do PNCP é a da contratação: dos 317 registros consultados lá, 311
    citam a Lei 14.133/2021 e NENHUM cita a Lei 13.019/2014.

Este módulo implanta os parâmetros que já têm medida de origem, com o número de
casos que cada expressão acertou. Nada aqui reprova por ausência de vocabulário
— só por sinal positivo de inconformidade (P24, a regra que protege contra o
erro caro).
"""
from __future__ import annotations

import json
import re
from datetime import date, datetime
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json

# ── P04/P05: o amparo legal decide antes do texto ─────────────────────────────
LEI_PARCERIA = re.compile(r"13\.?019[/\s]*(?:de\s*)?2014|lei\s+13\.?019|marco\s+regulat[óo]rio\s+das\s+organiza", re.I)
LEI_CONTRATO = re.compile(r"14\.?133[/\s]*(?:de\s*)?2021|lei\s+14\.?133|8\.?666[/\s]*(?:de\s*)?1993|lei\s+8\.?666", re.I)

# ── P06 a P09: expressões com acerto contado na base de 468 ───────────────────
# (regex, casos medidos, reprovados, motivo, exceção que resgata)
REGRAS_MEDIDAS = [
    (re.compile(r"com\s+ou\s+sem\s+fins\s+lucrativos", re.I), 38, 34,
     "o edital admite empresa ('com ou sem fins lucrativos'): não é fomento exclusivo a OSC", None),
    (re.compile(r"credenciamento\s+de\s+pessoas?\s+jur[íi]dicas?", re.I), 88, 88,
     "credenciamento de pessoa jurídica: contratação de quem presta ou fornece",
     re.compile(r"de\s+direito\s+privado[,\s]+sem\s+fins\s+lucrativos", re.I)),
    (re.compile(r"pessoas?\s+jur[íi]dicas?[^.]{0,80}?(?:para\s+)?(?:a\s+)?(?:realiza[çc][ãa]o|presta[çc][ãa]o|execu[çc][ãa]o)\s+d[eo]s?\s+servi[çc]", re.I), 71, 71,
     "credencia pessoa jurídica para realizar, prestar ou executar serviço ao órgão", None),
    (re.compile(r"\bprestador(?:a|as|es)?\s+de\s+servi[çc]o", re.I), 29, 29,
     "'prestador de serviço' descreve quem vende serviço ao órgão, não quem recebe fomento", None),
]

# sinais POSITIVOS de fomento — só eles resgatam (P24: nunca reprovar por ausência)
FOMENTO_NOMEADO = re.compile(r"termo\s+de\s+(?:fomento|colabora[çc][ãa]o)|acordo\s+de\s+coopera[çc][ãa]o|"
                             r"parceria\s+com\s+(?:a\s+)?(?:organiza[çc][ãa]o|osc)|fomento\s+a\s+projetos?", re.I)
DESTINATARIO_OSC = re.compile(r"(?:exclusivamente\s+)?(?:a|para|de|às|as)\s+(?:organiza[çc][õo]es?\s+da\s+sociedade\s+civil|"
                              r"entidades?\s+sem\s+fins\s+lucrativos|osc\b)|sem\s+fins\s+lucrativos", re.I)


def enquadramento_legal(texto: str, amparo: str = "") -> dict:
    """P04/P05 — a lei citada decide o enquadramento antes de qualquer palavra do objeto."""
    alvo = f"{amparo} {texto}"
    if LEI_PARCERIA.search(alvo):
        return {"lei": "13.019/2014", "presuncao": "parceria", "decide": True,
                "fundamento": "Lei 13.019/2014 rege as parcerias com OSC (termo de fomento, de colaboração e acordo de cooperação)"}
    if LEI_CONTRATO.search(alvo):
        resgate = bool(FOMENTO_NOMEADO.search(texto) and DESTINATARIO_OSC.search(texto))
        return {"lei": "14.133/2021" if re.search(r"14\.?133", alvo) else "8.666/1993",
                "presuncao": "contratação", "decide": not resgate,
                "resgatado": resgate,
                "fundamento": ("Lei 14.133/2021, art. 6º, XLIII: credenciamento é chamamento para 'prestar serviços ou fornecer bens' — "
                               "presume contratação" + (", mas há instrumento de fomento nomeado com destinatário exclusivo sem fins lucrativos" if resgate else ""))}
    return {"lei": None, "presuncao": None, "decide": False,
            "fundamento": "sem amparo legal declarado: não decide, mantém em atenção"}


def avaliar_medido(texto: str, amparo: str = "") -> dict:
    """Aplica as regras com acerto medido. Devolve reprovado/atencao/None (não opina)."""
    if not texto or len(texto.split()) <= 5:                       # P29: objeto curto não permite veredito
        return {"veredito": "atencao", "motivo": "objeto com 5 palavras ou menos não permite veredito — exige leitura do documento",
                "parametro": "P29", "prioridade_de_leitura": True}
    leg = enquadramento_legal(texto, amparo)
    if leg["lei"] == "13.019/2014":
        return {"veredito": None, "motivo": leg["fundamento"], "parametro": "P04", "enquadramento_legal": leg}
    for rx, casos, acertos, motivo, excecao in REGRAS_MEDIDAS:
        if rx.search(texto):
            if excecao and excecao.search(texto):
                continue                                            # a exceção resgata (P09)
            if FOMENTO_NOMEADO.search(texto) and DESTINATARIO_OSC.search(texto):
                continue                                            # P24: sinal positivo de fomento prevalece
            return {"veredito": "reprovado", "motivo": motivo, "parametro": "P06-P09",
                    "medida": f"{acertos} de {casos} casos medidos na base de 468", "enquadramento_legal": leg}
    if leg["decide"] and leg["presuncao"] == "contratação":
        return {"veredito": "reprovado", "motivo": leg["fundamento"], "parametro": "P05", "enquadramento_legal": leg}
    return {"veredito": None, "motivo": "sem sinal positivo de inconformidade", "parametro": "P24", "enquadramento_legal": leg}


# ── P11, P12, P30: o que NÃO é prazo de inscrição ─────────────────────────────
VIGENCIA_RX = re.compile(r"vig[êe]ncia|validade\s+do\s+credenciamento|execu[çc][ãa]o\s+do\s+objeto|prazo\s+de\s+execu", re.I)


def prazo_confiavel(inicio: str | None, fim: str | None, contexto: str = "") -> dict:
    """P11 (início = fim é data de publicação), P12 (janela > 1095 dias é vigência),
    P30 (vigência nunca vira prazo de inscrição)."""
    if not fim:
        return {"confiavel": False, "motivo": "sem data de encerramento", "parametro": "P30"}
    if inicio and inicio == fim:
        return {"confiavel": False, "motivo": "início igual ao fim: é assinatura de data de publicação, não janela de inscrição",
                "parametro": "P11", "acao": "prazo_a_confirmar"}
    if VIGENCIA_RX.search(contexto or ""):
        return {"confiavel": False, "motivo": "a data encontrada é de vigência/execução, não de inscrição",
                "parametro": "P30", "acao": "prazo_a_confirmar"}
    if inicio:
        try:
            dias = (date.fromisoformat(fim) - date.fromisoformat(inicio)).days
            if dias > 1095:
                return {"confiavel": False, "dias": dias, "parametro": "P12",
                        "motivo": f"janela de {dias} dias: é vigência de credenciamento contínuo, não prazo de inscrição",
                        "acao": "nao_listar_como_aberto"}
        except ValueError:
            pass
    try:
        if int(fim[:4]) > date.today().year + 3:
            return {"confiavel": False, "parametro": "P12",
                    "motivo": f"encerramento em {fim[:4]}: credenciamento contínuo, não janela de inscrição",
                    "acao": "nao_listar_como_aberto"}
    except (ValueError, TypeError):
        pass
    return {"confiavel": True, "motivo": "janela de inscrição plausível"}


# ── P14: revogação e errata ───────────────────────────────────────────────────
REVOGACAO_RX = re.compile(r"revoga[çc][ãa]o|revogado|anula[çc][ãa]o|cancelamento\s+do\s+edital", re.I)
ERRATA_RX = re.compile(r"errata|retifica[çc][ãa]o|adendo|prorroga[çc][ãa]o", re.I)


def sinalizadores_de_anexos(anexos: list) -> dict:
    """P14 — anexo de revogação encerra o registro; errata obriga a reler o prazo."""
    nomes = " ".join(str((a or {}).get("nome") or a) for a in (anexos or []))
    return {"revogado": bool(REVOGACAO_RX.search(nomes)),
            "tem_errata": bool(ERRATA_RX.search(nomes)),
            "acao": ("encerrar o registro: há anexo de revogação" if REVOGACAO_RX.search(nomes)
                     else "reler o prazo: há errata/retificação anexada" if ERRATA_RX.search(nomes) else None)}


# ── P21: cadência de 7 dias derivada do art. 26 da Lei 13.019/2014 ────────────
CADENCIA_DIAS = 7


def fontes_atrasadas(limite_dias: int = CADENCIA_DIAS) -> dict:
    """P21 — o edital de parceria tem de sair com 30 dias de antecedência (art. 26);
    visita a cada 7 dias garante quatro chances de vê-lo antes de fechar."""
    est = load_json(ROOT / "estado/esquadra.json") if (ROOT / "estado/esquadra.json").exists() else {}
    hoje = date.today()
    atrasadas, em_dia = [], 0
    for sid, s in (est.get("sensores") or {}).items():
        ult = (s.get("ultima") or "")[:10]
        if not ult:
            atrasadas.append({"id": sid, "nome": s.get("nome"), "dias": None, "motivo": "nunca visitada"})
            continue
        try:
            dias = (hoje - date.fromisoformat(ult)).days
        except ValueError:
            continue
        if dias > limite_dias:
            atrasadas.append({"id": sid, "nome": s.get("nome"), "dias": dias, "ultima": ult})
        else:
            em_dia += 1
    atrasadas.sort(key=lambda x: -(x.get("dias") or 9999))
    return {"em": now_iso(), "limite_dias": limite_dias, "em_dia": em_dia, "atrasadas": len(atrasadas),
            "fundamento": "Lei 13.019/2014, art. 26: divulgação com antecedência mínima de 30 dias — visita semanal dá 4 chances de ver cada edital",
            "itens": atrasadas[:60]}


# ── P25: a zona de atenção é orçamento, com meta ──────────────────────────────
META_ZONA_ATENCAO = 0.15


def zona_de_atencao() -> dict:
    """P25 — mede quanto do trabalho o motor deixa para leitura humana."""
    an = load_json(ROOT / "dados/editais/analises.json") if (ROOT / "dados/editais/analises.json").exists() else {}
    if not an:
        return {"medido": False}
    total = len(an)
    atencao = sum(1 for v in an.values() if v.get("selo") == "analise_incompleta")
    prop = atencao / total if total else 0
    return {"em": now_iso(), "total": total, "em_atencao": atencao, "proporcao": round(prop, 3),
            "meta": META_ZONA_ATENCAO, "dentro_da_meta": prop <= META_ZONA_ATENCAO,
            "custo": f"{atencao} leitura(s) de documento pendente(s)",
            "regra": "cada registro em atenção custa uma leitura; a meta é 15% com falso positivo em zero"}


# ── P31: auditoria cega de recall — a medida que faltava ──────────────────────
def auditoria_cega(amostra_municipios: int = 20, amostra_patrocinadores: int = 5) -> dict:
    """P31 — mede o que o sistema NUNCA VIU. Sorteia fontes, lista o que a base tem
    delas e produz o roteiro para a conferência manual. A taxa de perda é publicada."""
    import random
    cat = load_json(ROOT / "config/fontes_captacao_260.json").get("fontes", [])
    dados = load_json(ROOT / "docs/dashboard-dados.json") if (ROOT / "docs/dashboard-dados.json").exists() else {}
    por_fonte: dict = {}
    for e in (dados.get("editais") or []):
        por_fonte.setdefault(e.get("fonte_id") or e.get("fonte_nome"), []).append(e)
    rnd = random.Random(int(date.today().strftime("%Y%m%d")))
    municipais = [f for f in cat if f.get("nivel") == "municipal"]
    privados = [f for f in cat if f.get("nivel") in ("privada", "internacional")]
    sorteio = rnd.sample(municipais, min(amostra_municipios, len(municipais))) + \
              rnd.sample(privados, min(amostra_patrocinadores, len(privados)))
    itens = []
    for f in sorteio:
        achados = por_fonte.get(f["id"]) or por_fonte.get(f.get("orgao")) or []
        itens.append({"fonte": f["id"], "programa": f.get("programa"), "orgao": f.get("orgao"),
                      "sites": (f.get("sites") or [])[:2], "na_base": len(achados),
                      "conferir": "abrir o site, listar os editais publicados nos últimos 60 dias e comparar com 'na_base'"})
    res = {"em": now_iso(), "parametro": "P31", "sorteados": len(itens),
           "regra": "todas as métricas medem o que entrou; esta mede o que NUNCA entrou. Sem ela, não se sabe o tamanho da perda.",
           "sem_nada_na_base": sum(1 for x in itens if x["na_base"] == 0),
           "itens": itens, "taxa_de_perda": None,
           "como_fechar": "após a conferência manual, preencher 'encontrados_no_site' em cada item e a taxa de perda é calculada"}
    write_json(ROOT / "estado/auditoria_cega.json", res)
    return {k: v for k, v in res.items() if k != "itens"}


def run() -> dict:
    """Executa as medições da Onda 1 e grava o painel de parâmetros."""
    med = {"em": now_iso(), "origem": "auditoria de 09/09/2026 (468 registros, 231 validações)",
           "zona_de_atencao": zona_de_atencao(),
           "cadencia_das_fontes": fontes_atrasadas(),
           "auditoria_cega": auditoria_cega()}
    write_json(ROOT / "estado/parametros_motores.json", med)
    return {"zona_de_atencao": med["zona_de_atencao"].get("proporcao"),
            "fontes_atrasadas": med["cadencia_das_fontes"]["atrasadas"],
            "auditoria_cega_sorteados": med["auditoria_cega"]["sorteados"]}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
