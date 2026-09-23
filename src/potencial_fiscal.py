"""POTENCIAL FISCAL — quanto uma empresa poderia direcionar, em ordem de grandeza.

Isto é uma ESTIMATIVA, e o desenho do cálculo importa mais do que o número: quem vai pedir
precisa saber se está diante de uma empresa de cinco mil ou de cinco milhões, e por quê.

O caminho do cálculo, todo declarado:

    porte + capital social  →  faixa de faturamento anual
    faturamento × margem    →  lucro tributável estimado
    lucro → IRPJ devido     →  15% + adicional de 10% sobre o que passa de R$ 240 mil/ano
    IRPJ devido × limites   →  quanto cabe em cada lei de incentivo

Limites federais usados (Lucro Real, dedução do IRPJ devido):

    Fundo da Criança e do Adolescente ....... 1%
    Fundo do Idoso ......................... 1%
    PRONON (oncologia) ..................... 1%
    PRONAS (pessoa com deficiência) ........ 1%
    Lei Rouanet (cultura) .................. 4%
    Lei de Incentivo ao Esporte ............ 1%

Três advertências que acompanham todo número daqui:

1. Empresa no Simples Nacional **não** deduz — o incentivo exige Lucro Real. Quem está no
   Simples aparece com potencial zero e o motivo escrito.
2. O faturamento é inferido do porte e do capital social, não declarado. Erra para mais e
   para menos. Serve para ordenar candidatos, nunca para escrever num ofício.
3. O ICMS depende de programa estadual, e cada estado tem o seu. Enquanto a regra de Goiás
   não for confirmada na fonte oficial, o campo fica marcado como a confirmar em vez de
   receber um número inventado.
"""
from __future__ import annotations

import re

# Limites de dedução do IRPJ devido, por lei
LEIS_IRPJ = {
    "fia": {"nome": "Fundo da Criança e do Adolescente", "limite": 0.01,
            "serve_para": "projeto com criança e adolescente", "conselho": "CMDCA"},
    "idoso": {"nome": "Fundo do Idoso", "limite": 0.01,
              "serve_para": "projeto com pessoa idosa", "conselho": "CMI"},
    "pronon": {"nome": "PRONON", "limite": 0.01, "serve_para": "oncologia", "conselho": "Ministério da Saúde"},
    "pronas": {"nome": "PRONAS/PCD", "limite": 0.01,
               "serve_para": "pessoa com deficiência", "conselho": "Ministério da Saúde"},
    "rouanet": {"nome": "Lei Rouanet", "limite": 0.04, "serve_para": "cultura", "conselho": "Minc/SALIC"},
    "esporte": {"nome": "Lei de Incentivo ao Esporte", "limite": 0.01,
                "serve_para": "esporte e paradesporto", "conselho": "Ministério do Esporte"},
}
ADICIONAL_A_PARTIR_DE = 240_000.0      # por ano
ALIQUOTA_IRPJ = 0.15
ALIQUOTA_ADICIONAL = 0.10
MARGEM_PADRAO = 0.08                   # lucro tributável presumido sobre o faturamento

# Faixa de faturamento anual por porte, em reais
PORTES = {
    "ME": (81_000, 360_000), "MICRO EMPRESA": (81_000, 360_000), "MICROEMPRESA": (81_000, 360_000),
    "EPP": (360_000, 4_800_000), "EMPRESA DE PEQUENO PORTE": (360_000, 4_800_000),
    "DEMAIS": (4_800_000, 300_000_000), "MEDIO PORTE": (4_800_000, 90_000_000),
    "GRANDE PORTE": (90_000_000, 1_000_000_000),
}


def _num(v) -> float:
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    s = re.sub(r"[^\d,.-]", "", str(v)).replace(".", "").replace(",", ".")
    try:
        return float(s)
    except Exception:
        return 0.0


def _faixa_faturamento(cad: dict) -> tuple[float, float, str]:
    porte = str(cad.get("porte") or "").upper().strip()
    cap = _num(cad.get("capital_social"))
    for k, (a, b) in PORTES.items():
        if k in porte:
            base = (a, b, f"porte declarado: {porte.title()}")
            break
    else:
        base = (0.0, 0.0, "porte não declarado")
    if cap > 0:
        # capital social costuma acompanhar a escala da empresa; usamos como âncora
        por_cap = (cap * 1.5, cap * 12.0)
        if base[1] == 0:
            return por_cap[0], por_cap[1], f"capital social de R$ {cap:,.0f}".replace(",", ".")
        return (max(base[0], por_cap[0] * 0.5), max(base[1], por_cap[1] * 0.5),
                f"{base[2]} e capital social de R$ {cap:,.0f}".replace(",", "."))
    return base


def _irpj(lucro: float) -> float:
    if lucro <= 0:
        return 0.0
    return lucro * ALIQUOTA_IRPJ + max(0.0, lucro - ADICIONAL_A_PARTIR_DE) * ALIQUOTA_ADICIONAL


def estimar(cadastro: dict, margem: float = MARGEM_PADRAO) -> dict:
    """A estimativa completa, com a conta à mostra."""
    cad = cadastro or {}
    simples = str(cad.get("opcao_simples") or "").lower() in ("sim", "true", "1", "optante")
    situacao = str(cad.get("situacao") or "").upper()
    if simples:
        return {"apurou": False, "motivo": "optante pelo Simples Nacional — não deduz incentivo fiscal do IRPJ",
                "irpj": None, "icms": None, "confianca": "certa"}
    if "BAIXADA" in situacao or "INAPTA" in situacao or "SUSPENSA" in situacao:
        return {"apurou": False, "motivo": f"situação cadastral: {situacao.title()}",
                "irpj": None, "icms": None, "confianca": "certa"}

    fmin, fmax, base = _faixa_faturamento(cad)
    if fmax <= 0:
        return {"apurou": False, "motivo": "sem porte nem capital social no cadastro — não dá para estimar",
                "irpj": None, "icms": None, "confianca": "nenhuma"}

    lmin, lmax = fmin * margem, fmax * margem
    imin, imax = _irpj(lmin), _irpj(lmax)
    leis = {k: {"nome": v["nome"], "serve_para": v["serve_para"], "conselho": v["conselho"],
                "limite_pct": v["limite"] * 100,
                "min": round(imin * v["limite"]), "max": round(imax * v["limite"])}
            for k, v in LEIS_IRPJ.items()}
    teto_total = sum(v["limite"] for v in LEIS_IRPJ.values())      # 9% somando todas as leis
    confianca = "media" if _num(cad.get("capital_social")) > 0 and cad.get("porte") else "baixa"
    return {
        "apurou": True, "confianca": confianca,
        "base_do_calculo": base,
        "faturamento": {"min": round(fmin), "max": round(fmax)},
        "margem_usada_pct": round(margem * 100, 1),
        "lucro_estimado": {"min": round(lmin), "max": round(lmax)},
        "irpj": {"devido_min": round(imin), "devido_max": round(imax),
                 "direcionavel_min": round(imin * teto_total), "direcionavel_max": round(imax * teto_total),
                 "teto_pct": round(teto_total * 100, 1), "por_lei": leis,
                 "regra": "dedução sobre o IRPJ devido, só para empresa no Lucro Real"},
        "icms": {"direcionavel_min": None, "direcionavel_max": None,
                 "estado": cad.get("uf"),
                 "situacao": "a confirmar",
                 "porque": "o direcionamento de ICMS depende de programa estadual; a regra vigente em "
                           "Goiás precisa ser confirmada na fonte oficial antes de virar número aqui"},
        "aviso": "ordem de grandeza a partir do porte e do capital social; serve para ordenar candidatos, "
                 "não para escrever em ofício. Confirmar com a contabilidade da empresa.",
    }


def resumir(e: dict) -> dict:
    """O pouco que a linha do ranking precisa mostrar."""
    p = e.get("potencial") or {}
    if not p.get("apurou"):
        return {"tem": False, "motivo": p.get("motivo") or "não estimado"}
    i = p["irpj"]
    return {"tem": True, "min": i["direcionavel_min"], "max": i["direcionavel_max"],
            "confianca": p.get("confianca"), "icms": p["icms"]["situacao"]}


def faixa_texto(minimo: float | None, maximo: float | None) -> str:
    """R$ 12 mil a R$ 90 mil — arredondado, porque precisão falsa engana."""
    def um(v):
        v = float(v or 0)
        if v >= 1_000_000_000:
            return f"R$ {v/1_000_000_000:.1f} bi".replace(".", ",")
        if v >= 1_000_000:
            return f"R$ {v/1_000_000:.1f} mi".replace(".", ",")
        if v >= 1_000:
            return f"R$ {v/1_000:.0f} mil"
        return f"R$ {v:.0f}"
    if not maximo:
        return "—"
    return f"{um(minimo)} a {um(maximo)}"
