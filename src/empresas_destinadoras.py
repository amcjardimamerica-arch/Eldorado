"""MOTOR 19 — BANCO DE EMPRESAS QUE DESTINAM IMPOSTO A ASSOCIAÇÕES E O BRAÇO SOCIAL DE CADA UMA (titular, 03/10/2026).

O que o motor 19 observa: os sites institucionais das empresas do banco de dados que JÁ fazem destinação tributária
(renúncia fiscal) e, principalmente, o instituto ou a fundação que distribui esses recursos. Quando o instituto abre
edital, é concorrência aberta para a associação.

De onde vem cada dado (nada inventado):
  · EMPRESA e MECANISMO: docs/dados/incentivos_verificados.json (CNPJ conferido; Rouanet pelo SALIC, Goyazes pela
    Secult-GO, referência 26/09/2026).
  · INSTITUTO/FUNDAÇÃO: rede de associados do GIFE (gife.org.br/associados, categoria "Fundação / Instituto
    Empresarial"), perfil aberto e conferido no navegador do titular em 03/10/2026; o site é o que o próprio perfil
    do GIFE indica e o número do Mapa das OSC (IPEA) confirma que é entidade do terceiro setor.
  · Empresa sem instituto no GIFE: "instituto": null — "não verificado", nunca "não tem".
  · "vinculo": "a_confirmar" quando a ligação empresa→instituto vem só do nome ou do grupo econômico.

Saída: config/empresas_destinadoras.json — fonte das rotas do motor 19 (sensores.py › rotas_para_sensor).
"""
from __future__ import annotations

import json

from .nucleo import ROOT, load_json, now_iso, write_json

VERIF = ROOT / "docs/dados/incentivos_verificados.json"
SAIDA = ROOT / "config/empresas_destinadoras.json"
CONFERIDO = "2026-10-03"
GIFE = "https://gife.org.br/associados/{}/"
MAPA = "https://mapaosc.ipea.gov.br/visualizar-osc.html#/{}"

# CNPJ (ou nome, quando a base não tem CNPJ único) → braço social conferido no GIFE em 03/10/2026
BRACOS = [
    ("17469701000177", None, "Fundação ArcelorMittal", "fundacao-arcelormittal", "https://www.famb.org.br/", "507816", "confirmado"),
    ("00000000000191", None, "Fundação Banco do Brasil", "fundacao-banco-do-brasil", "https://www.fbb.org.br/", "784138", "confirmado"),
    ("60746948000112", None, "Fundação Bradesco", "fundacao-bradesco", "https://www.fb.org.br/", "608439", "confirmado"),
    ("60498706000157", None, "Fundação Cargill", "fundacao-cargill", "https://alimentacaoemfoco.org.br/", "595170", "confirmado"),
    ("50290329000102", None, "Fundação Cargill", "fundacao-cargill", "https://alimentacaoemfoco.org.br/", "595170", "confirmado"),
    ("33041260000164", None, "Fundação Casas Bahia", "fundacao-casas-bahia", "http://www.viavarejo.com.br/fundacaoviavarejo", "788357", "confirmado"),
    ("60701190000104", None, "Fundação Itaú", "fundacao-itau", "https://www.fundacaoitau.org.br/", None, "confirmado"),
    ("60701190000104", None, "Instituto Unibanco", "instituto-unibanco", "https://www.institutounibanco.org.br/", "599810", "confirmado"),
    ("08070508000178", None, "Fundação Raízen", "fundacao-raizen", "https://www.fundacaoraizen.org.br/", "789304", "confirmado"),
    ("02558157000162", None, "Fundação Telefônica Vivo", "fundacao-telefonica", "https://fundacaotelefonica.org.br/", "591462", "confirmado"),
    ("59104760000191", None, "Fundação Toyota do Brasil", "fundacao-toyota-do-brasil", "https://www.fundacaotoyotadobrasil.org.br/", None, "confirmado"),
    ("33592510000154", None, "Fundação Vale", "fundacao-vale", "https://www.fundacaovale.org/", "561379", "confirmado"),
    ("59104422000150", None, "Fundação Grupo Volkswagen", "fundacao-volkswagen", "https://www.fundacaogrupovw.org.br/", "634720", "confirmado"),
    ("23637697000101", None, "Instituto Alcoa", "instituto-alcoa", "http://www.alcoa.com/brasil/pt/institute/about.asp", "660319", "confirmado"),
    ("06057223000171", None, "Instituto Assaí", "instituto-assai", "https://institutoassai.org.br/", None, "confirmado"),
    ("33009911000139", None, "Instituto BAT Brasil", "instituto-bat-brasil", "https://www.institutobatbrasil.org/", "563664", "confirmado"),
    ("01838723000127", None, "Instituto BRF", "instituto-brf", "https://www.institutobrf.com/", None, "confirmado"),
    ("40432544000147", None, "Instituto Claro", "instituto-claro", "https://www.institutoclaro.org.br/", "563789", "confirmado"),
    ("59275792000150", None, "Instituto General Motors", "instituto-general-motors", "https://www.chevrolet.com.br/marca/instituto-gm", None, "confirmado"),
    ("16670085000155", None, "Instituto Localiza", "instituto-localiza", "https://www.institutolocaliza.org/", None, "confirmado"),
    ("92754738000162", None, "Instituto Lojas Renner", "instituto-lojas-renner", "https://www.institutolojasrenner.org.br/", "732138", "confirmado"),
    ("61156501000156", None, "Instituto Mosaic", "instituto-mosaic", None, None, "confirmado"),
    ("71673990000177", None, "Instituto Natura", "instituto-natura", "https://www.institutonatura.org.br/", "593600", "confirmado"),
    ("00718528000109", None, "Instituto Sabin", "instituto-sabin", "https://institutosabin.org.br/", "783068", "confirmado"),
    ("01637895000132", None, "Instituto Votorantim", "instituto-votorantim", "https://www.institutovotorantim.org.br/", "669954", "confirmado"),
    ("02916265000160", None, "Fundo JBS pela Amazônia", "fundo-jbs-pela-amazonia", "https://www.fundojbsamazonia.org/", None, "confirmado"),
    ("07358761000169", None, "Instituto Helda Gerdau", "instituto-helda-gerdau", None, None, "a_confirmar"),
    ("33337122000127", None, "Instituto Ultra", "instituto-ultra", "https://www.institutoultra.org.br/", None, "a_confirmar"),
    (None, "Grupo Boticário", "Fundação Grupo Boticário", "fundacao-grupo-boticario", "https://www.fundacaogrupoboticario.org.br/", "1186007", "confirmado"),
    (None, "Grupo Boticário", "Instituto Grupo Boticário", "instituto-grupo-boticario", None, "814879", "confirmado"),
    (None, "Sicoob", "Instituto Sicoob", "instituto-sicoob", "http://www.institutosicoob.org.br/", None, "confirmado"),
    (None, "Sicredi", "Fundação Sicredi", "fundacao-sicredi", "https://fundacaosicredi.org.br/", None, "confirmado"),
    (None, "Nubank", "Instituto Nu", "instituto-nu", None, None, "confirmado"),
]
NOTAS_VINCULO = {"Instituto Helda Gerdau": "ligação com a Gerdau pelo nome da família fundadora; conferir no site do instituto",
                 "Instituto Ultra": "Ipiranga pertence ao grupo Ultra (Ultrapar); conferir se o instituto atende a Ipiranga"}


def _braco(t: tuple) -> dict:
    cnpj, nome, inst, slug, site, osc, vinc = t
    b = {"nome": inst, "tipo": "fundação" if inst.startswith("Funda") else ("fundo" if inst.startswith("Fundo") else "instituto"),
         "site": site, "gife": GIFE.format(slug), "mapa_osc": MAPA.format(osc) if osc else None,
         "vinculo": vinc, "conferido_em": CONFERIDO,
         "pagina_de_edital": None,   # descoberta na leitura: o motor segue, a partir da home, os links que casam com o léxico
         "fonte": "perfil do associado na rede GIFE (categoria Fundação / Instituto Empresarial), lido em 03/10/2026"}
    if inst in NOTAS_VINCULO:
        b["nota"] = NOTAS_VINCULO[inst]
    if not site:
        b["pendencia"] = "o perfil do GIFE não traz o site; localizar o site oficial antes de observar"
    return b


def montar() -> dict:
    v = load_json(VERIF) if VERIF.exists() else {"empresas": [], "resumo": {}}
    empresas = []
    for e in v.get("empresas", []):
        bracos = [_braco(t) for t in BRACOS if t[0] == e.get("cnpj")]
        r = e.get("rouanet_5_anos") or {}
        empresas.append({"empresa": e.get("nome"), "cnpj": e.get("cnpj"), "mecanismos_confirmados": e.get("confirmados") or [],
                         "rouanet_5_anos": r or None, "lucro_real": e.get("lucro_real"),
                         "destina": bool(e.get("confirmados")),
                         "bracos_sociais": bracos,
                         "instituto": None if bracos else "não verificado — sem associado no GIFE em 03/10/2026; outro instituto não conferido",
                         "observar": "instituto" if any(b["site"] for b in bracos) else "pendente"})
    for nome in sorted({t[1] for t in BRACOS if t[1]}):
        empresas.append({"empresa": nome, "cnpj": None, "mecanismos_confirmados": [], "rouanet_5_anos": None, "lucro_real": None,
                         "destina": None, "nota": "consta em incentivos_verificados como 'sem CNPJ único' (grupo econômico)",
                         "bracos_sociais": [_braco(t) for t in BRACOS if t[1] == nome], "instituto": None,
                         "observar": "instituto"})
    com = [x for x in empresas if x["bracos_sociais"]]
    res = {"versao": 2, "gerado_em": now_iso(), "conferido_em": CONFERIDO,
           "regra": ("motor 19: observa o site do instituto ou da fundação que distribui o recurso de renúncia fiscal das empresas "
                     "que já destinam (banco verificado); edital aberto ali é concorrência para a associação. Empresa sem braço "
                     "social conferido fica 'não verificado', nunca 'não tem'."),
           "fontes": {"empresas": "docs/dados/incentivos_verificados.json", "bracos": "https://gife.org.br/associados/",
                      "entidade_terceiro_setor": "https://mapaosc.ipea.gov.br/"},
           "total_empresas": len(empresas), "com_braco_social": len(com),
           "bracos_com_site": len({b["site"] for x in com for b in x["bracos_sociais"] if b["site"]}),
           "sem_braco_verificado": [x["empresa"] for x in empresas if not x["bracos_sociais"] and x["destina"]],
           "empresas": empresas}
    write_json(SAIDA, res)
    return {k: res[k] for k in ("total_empresas", "com_braco_social", "bracos_com_site")}


def rotas(limite: int = 40) -> list[str]:
    """Página de edital (quando já conhecida) e home de cada braço social, sem repetir."""
    if not SAIDA.exists():
        return []
    d = load_json(SAIDA)
    vistos, urls = set(), []
    for e in d.get("empresas", []):
        for b in e.get("bracos_sociais", []):
            for u in (b.get("pagina_de_edital"), b.get("site")):
                if u and u not in vistos:
                    vistos.add(u); urls.append(u)
    return urls[:limite]


if __name__ == "__main__":
    print(json.dumps(montar(), ensure_ascii=False, indent=2))
