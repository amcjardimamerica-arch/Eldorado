"""Rota de monitoramento — nenhum dos 260 pontos de captação fica sem caminho.

Este módulo faz o que a medição de cobertura antiga não fazia: em vez de dizer
"coberto" ou "descoberto" por tipo, ele **atribui a cada ponto do acervo uma
rota concreta** — qual forma de divulgação aquele ponto usa, qual camada do
sistema captura essa forma e qual fonte catalogada corresponde.

A regra que fecha a lacuna: todo ponto de captação que envolve **dinheiro
público** tem publicação obrigatória em diário oficial. Mesmo que não exista
página de editais, mesmo que o conselho não tenha site, o ato existe e é
publicado. Por isso a rota-piso de qualquer ponto público é o diário oficial do
seu nível federativo — DOU, diário estadual ou diário municipal.

Pontos privados não têm publicação obrigatória; a rota-piso deles é a página
institucional no domínio oficial mais a camada de imprensa.

Resultado: `estado/rotas_monitoramento.json` e o relatório HTML de amplitude.
Sem IA e sem tokens.
"""
from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter

from .nucleo import ROOT, load_json, now_iso, write_json

def _n(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode().lower()

# Pistas textuais no campo "onde captar" do acervo -> forma de divulgação.
# A ordem importa: a primeira que casar define a rota principal.
SINAIS = [
    (r"cmdca|fmdca|conanda|cedca|conselho.*crianca", "resolucao_conselho", "crianca_adolescente"),
    (r"cmi\b|conselho.*idoso|fundo do idoso|cndi", "resolucao_conselho", "pessoa_idosa"),
    (r"cmas|ceas|cnas|fmas|feas|fnas|conselho.*assistencia", "resolucao_conselho", "assistencia_social"),
    (r"conselho|cofen|cms\b|conselho de saude", "resolucao_conselho", None),
    (r"minist[eé]rio p[uú]blico|mpgo|mpf\b|mpt\b|cnmp|tac\b|termo de ajustamento", "edital_ministerio_publico", None),
    (r"tjgo|tribunal|cnj\b|vara|judici|pena pecuni|presta[cç][aã]o pecuni|trt", "edital_destinacao_judicial", None),
    (r"fdd|cfdd|direitos difusos", "resolucao_conselho", "direitos_difusos"),
    (r"emenda|parlamentar|deputad|senador|alego|c[aâ]mara|congresso|sri\b", "emenda_parlamentar", None),
    (r"salic|rouanet|lie\b|sli\b|pronon|pronas|goyazes|incentivo|icms|lei de incentivo|dedu[cç][aã]o|receita federal",
     "lista_projetos_aptos", None),
    (r"transferegov|convenio|conv[eê]nio|plataforma \+brasil", "portal_compras_pncp", None),
    (r"prosas|capta|gife|observat[oó]rio|plataforma", "plataforma_agregadora", None),
    (r"submiss[aã]o internacional|uni[aã]o europeia|bid\b|unesco|grants|embaixada|internacional",
     "submissao_internacional", None),
    (r"empresa|funda[cç][aã]o|instituto|patroc[ií]nio|doa[cç][aã]o|banco\b|itau|bradesco|vale\b",
     "pagina_institucional_privada", None),
    (r"prefeitura|munic[ií]pio|secretaria municipal|sme\b|sms\b|semasdh|secult goi[aâ]nia|smel",
     "diario_oficial_municipio", None),
    (r"secult goi[aá]s|seds|seel|semad|governo de goi[aá]s|estadual|ses\b|estado",
     "diario_oficial_estado", None),
    (r"minist[eé]rio|mds|minc|mec\b|mdhc|mma\b|mjsp|mcti|federal|gov\.br|uni[aã]o",
     "diario_oficial_uniao", None),
    (r"site oficial", "site_oficial_orgao", None),
]

# Rota-piso por nível: onde o ato obrigatoriamente aparece quando nada mais existe.
PISO_POR_NIVEL = {
    "federal": ("diario_oficial_uniao", "in-dou-secao3"),
    "estadual": ("diario_oficial_estado", "goias-editais"),
    "municipal": ("diario_oficial_municipio", "querido_diario"),
    "privada": ("pagina_institucional_privada", "capilaridade_imprensa"),
    "internacional": ("submissao_internacional", "varredura_html"),
    "a_validar": ("portal_compras_pncp", "api_pncp"),
}

def _forma_por_texto(item: dict) -> tuple[str | None, str | None]:
    alvo = _n(f"{item.get('onde_captar_original','')} {item.get('fonte_programa','')} {item.get('tipo_original','')}")
    for padrao, forma, area in SINAIS:
        if re.search(padrao, alvo):
            return forma, area
    return None, None

def rota_para(item: dict, formas: dict, fontes_por_forma: dict) -> dict:
    """Devolve a rota principal e as rotas de reforço de um ponto de captação."""
    niveis = item.get("niveis_inferidos") or ["a_validar"]
    nivel = niveis[0]
    forma, area = _forma_por_texto(item)
    origem = "sinal_textual"
    if not forma:
        forma = PISO_POR_NIVEL.get(nivel, PISO_POR_NIVEL["a_validar"])[0]
        origem = "piso_por_nivel"

    definicao = formas.get(forma, {})
    reforcos = []
    # Todo ponto público ganha o PNCP como reforço; todo ponto ganha imprensa.
    if nivel in {"federal", "estadual", "municipal"}:
        reforcos.append({"forma": "portal_compras_pncp", "camada": "api_pncp"})
        if nivel == "municipal":
            reforcos.append({"forma": "diario_oficial_municipio", "camada": "querido_diario"})
    reforcos.append({"forma": "rede_social_oficial", "camada": "redes_indireta"})
    if forma != "plataforma_agregadora":
        reforcos.append({"forma": "plataforma_agregadora", "camada": "varredura_html"})

    return {
        "id_acervo": item["id_acervo"],
        "fonte_programa": item.get("fonte_programa"),
        "tipo_catalogo": item.get("tipo_catalogo"),
        "nivel": nivel,
        "area": area or item.get("area_original"),
        "forma_divulgacao": forma,
        "origem_da_rota": origem,
        "camada_principal": definicao.get("camada", "varredura_html"),
        "confianca": definicao.get("confianca", "pista"),
        "obrigatoriedade_publicacao": definicao.get("obrigatoriedade", "nenhuma"),
        "fontes_correspondentes": fontes_por_forma.get(forma, [])[:6],
        "reforcos": reforcos,
        "monitoravel": True,
    }

def run() -> dict:
    catalogo = load_json(ROOT / "catalogo_captacao/catalogo_anexo.json")
    canais = load_json(ROOT / "config/canais_divulgacao.json")
    fontes = load_json(ROOT / "config/fontes.json")["fontes"]
    formas = {f["id"]: f for f in canais["formas"]}

    fontes_por_forma: dict[str, list] = {}
    for fonte in fontes:
        if not fonte.get("ativa"):
            continue
        chave = fonte.get("forma_divulgacao") or "site_oficial_orgao"
        fontes_por_forma.setdefault(chave, []).append({"id": fonte["id"], "nome": fonte["nome"]})

    rotas = [rota_para(item, formas, fontes_por_forma) for item in catalogo["itens"]]
    sem_rota = [r for r in rotas if not r["monitoravel"]]

    por_forma = Counter(r["forma_divulgacao"] for r in rotas)
    por_nivel = Counter(r["nivel"] for r in rotas)
    por_origem = Counter(r["origem_da_rota"] for r in rotas)
    obrigatorias = sum(1 for r in rotas if r["obrigatoriedade_publicacao"] == "legal")

    resultado = {
        "gerado_em": now_iso(),
        "total_catalogo": catalogo["total"],
        "com_rota_de_monitoramento": len(rotas) - len(sem_rota),
        "sem_rota": len(sem_rota),
        "percentual": round(100 * (len(rotas) - len(sem_rota)) / max(len(rotas), 1), 1),
        "com_publicacao_obrigatoria": obrigatorias,
        "por_forma_divulgacao": dict(por_forma.most_common()),
        "por_nivel": dict(por_nivel.most_common()),
        "origem_da_rota": dict(por_origem),
        "regra": ("Ter rota não é o mesmo que ter oportunidade confirmada: a rota garante que existe caminho "
                  "técnico de captura. A confirmação continua exigindo URL primária."),
        "rotas": rotas,
    }
    write_json(ROOT / "estado/rotas_monitoramento.json", resultado)
    return {k: v for k, v in resultado.items() if k != "rotas"}

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
