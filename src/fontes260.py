"""As 260 fontes de captação — cada uma com seu site oficial e seu padrão.

Determinação do titular: análise aprofundada de Goiás e Goiânia, sem deixar
nenhuma fonte de fora. O relatório de 260 fontes traz programa, nível, área,
forma de divulgação e obrigatoriedade de publicação — mas **nenhuma URL**.
Este módulo resolve, para cada fonte, ONDE ela publica (site oficial do
órgão, diário oficial, portal do conselho, plataforma) e qual é o seu padrão
(edital, fundo, emenda, incentivo fiscal, destinação judicial, doação, grant),
e entrega tudo ao motor de busca ativa.

Grau de confiança de cada site, sempre declarado:
  confirmada  — vem do catálogo de fontes já validado (config/fontes.json)
  curada      — atribuída pela tabela institucional deste módulo; a busca
                ativa confere a página ao abrir
  generica    — apenas a forma de divulgação (diário oficial, PNCP, DOU)
Nunca se inventa endereço: sem correspondência, a fonte fica com a rota
genérica e marcada como pendente de localização.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from urllib.parse import urlsplit

from .nucleo import ROOT, load_json, now_iso, slug, write_json

ROTAS = ROOT / "estado/rotas_monitoramento.json"
SAIDA_CFG = ROOT / "config/fontes_captacao_260.json"
SAIDA_BIB = ROOT / "biblioteca_alexandria/fontes/catalogo_260.json"

# ------------------------------------------------ tabela institucional (curada)
# (padrão no nome do programa, nível) -> sites oficiais
_TABELA = [
    # Goiânia — cultura
    (r"pnab goi[âa]nia|secult goi[âa]nia|cultura.*goi[âa]nia|ocupa[çc][ãa]o cultural municipal|lei municipal n[ºo] 7\.957",
     "municipal", ["https://www.goiania.go.gov.br/cultura/", "https://diariooficial.goiania.go.gov.br/"],
     "Secretaria Municipal de Cultura de Goiânia"),
    # Goiás — cultura
    (r"pnab goi[áa]s|fundo de arte e cultura|secult goi[áa]s|goi[áa]s pelo mundo",
     "estadual", ["https://goias.gov.br/cultura/", "https://diariooficial.abc.go.gov.br/"],
     "Secretaria de Estado da Cultura de Goiás (Secult-GO)"),
    (r"goyazes", "estadual", ["https://goias.gov.br/cultura/"], "Programa Goyazes — Secult-GO"),
    (r"\bfica\b", "estadual", ["https://goias.gov.br/cultura/"], "FICA — Festival Internacional de Cinema e Vídeo Ambiental (Secult-GO)"),
    # esporte
    (r"esporte.*goi[âa]nia|secretaria municipal dos esportes|contraturno escolar",
     "municipal", ["https://www.goiania.go.gov.br/", "https://diariooficial.goiania.go.gov.br/"],
     "Secretaria Municipal de Esporte e Lazer de Goiânia"),
    (r"pr[óo]-goi[áa]s atleta|eventos esportivos|esporte.*goi[áa]s|esporte e lazer para idosos",
     "estadual", ["https://goias.gov.br/esporte/", "https://diariooficial.abc.go.gov.br/"],
     "Secretaria de Estado de Esporte e Lazer (SEEL-GO)"),
    # assistência social
    (r"semasdh|fmas goi[âa]nia|termo de fomento municipal para entidade social|acolhimento",
     "municipal", ["https://www.goiania.go.gov.br/", "https://diariooficial.goiania.go.gov.br/"],
     "SEMASDH Goiânia / Fundo Municipal de Assistência Social (CMAS)"),
    (r"seds goi[áa]s|feas-go|protege goi[áa]s|termo de fomento estadual para entidade social|inclus[ãa]o produtiva|mulheres em vulnerabilidade|seguran[çc]a alimentar|fam[íi]lias de baixa renda",
     "estadual", ["https://goias.gov.br/social/", "https://diariooficial.abc.go.gov.br/"],
     "Secretaria de Estado de Desenvolvimento Social (SEDS-GO) / FEAS"),
    # criança, adolescente e idoso
    (r"fmdca|cmdca|crian[çc]as? e adolescentes|adolescentes|protagonismo juvenil|trabalho infantil|evas[ãa]o escolar|parentalidade|empreendedorismo juvenil|biblioteca comunit[áa]ria|media[çc][ãa]o de leitura|convivência de crian",
     "municipal", ["https://www.goiania.go.gov.br/"], "CMDCA Goiânia / FMDCA"),
    (r"fundo estadual da crian[çc]a|cedca", "estadual", ["https://goias.gov.br/social/"], "CEDCA-GO / FEIA"),
    (r"fundo municipal do idoso|intergeracional", "municipal", ["https://www.goiania.go.gov.br/"], "Conselho Municipal do Idoso de Goiânia"),
    (r"fundo estadual dos direitos da pessoa idosa", "estadual", ["https://goias.gov.br/social/"], "Conselho Estadual do Idoso de Goiás"),
    # educação
    (r"sme goi[âa]nia|educa[çc][ãa]o integral|educativo em goi[âa]nia", "municipal",
     ["https://www.goiania.go.gov.br/educacao/", "https://diariooficial.goiania.go.gov.br/"], "Secretaria Municipal de Educação de Goiânia"),
    (r"educativo em goi[áa]s|educa[çc][ãa]o para o trabalho", "estadual", ["https://goias.gov.br/educacao/"], "Seduc-GO"),
    # saúde
    (r"sms goi[âa]nia|sa[úu]de preventiva", "municipal", ["https://saude.goiania.go.gov.br/", "https://diariooficial.goiania.go.gov.br/"], "Secretaria Municipal de Saúde de Goiânia"),
    (r"ses-go|sa[úu]de comunit[áa]ria", "estadual", ["https://goias.gov.br/saude/", "https://diariooficial.abc.go.gov.br/"], "Secretaria de Estado da Saúde (SES-GO)"),
    # meio ambiente
    (r"semad", "estadual", ["https://goias.gov.br/meioambiente/"], "Semad-GO"),
    # justiça e controle
    (r"tjgo|vara de execu[çc][ãa]o penal", "municipal", ["https://www.tjgo.jus.br/"], "Tribunal de Justiça de Goiás — destinação de prestações pecuniárias"),
    (r"justi[çc]a federal em goi[áa]s", "estadual", ["https://www.trf1.jus.br/sjgo/"], "Justiça Federal — Seção Judiciária de Goiás"),
    (r"mpgo", "estadual", ["https://www.mpgo.mp.br/"], "Ministério Público de Goiás"),
    (r"tcm-go", "municipal", ["https://www.tcm.go.gov.br/"], "Tribunal de Contas dos Municípios de Goiás"),
    # emendas
    (r"emenda (?:parlamentar )?(?:estadual|de bancada)|alego", "estadual", ["https://portal.al.go.leg.br/"], "ALEGO — gabinetes"),
    (r"emenda (?:parlamentar )?municipal|sri goi[âa]nia|c[âa]mara municipal", "municipal", ["https://www.goiania.go.leg.br/"], "Câmara Municipal de Goiânia — gabinetes"),
    (r"emenda parlamentar federal", "federal", ["https://www.camara.leg.br/", "https://www12.senado.leg.br/"], "Câmara dos Deputados e Senado — gabinetes"),
    # privados e outros GO
    (r"sebrae goi[áa]s", "estadual", ["https://sebraego.com.br/"], "Sebrae Goiás"),
    (r"empresas locais de goi[âa]nia", "municipal", [], "Patrocínio direto — sem página única"),
    (r"conv[êe]nio com [óo]rg[ãa]o p[úu]blico estadual", "estadual", ["https://pncp.gov.br/", "https://diariooficial.abc.go.gov.br/"], "PNCP / Diário Oficial de Goiás"),
    # federais
    (r"rouanet|pronac|salic|minist[ée]rio da cultura|pnab federal|aldir blanc", "federal", ["https://www.gov.br/cultura/pt-br/assuntos/editais"], "Ministério da Cultura / SALIC"),
    (r"lei de incentivo ao esporte|minist[ée]rio do esporte", "federal", ["https://www.gov.br/esporte/pt-br"], "Ministério do Esporte"),
    (r"\bmds\b|\bfnas\b|\bcnas\b|suas", "federal", ["https://www.gov.br/mds/pt-br"], "MDS / FNAS / CNAS"),
    (r"conanda|fnca|fundo nacional para a crian", "federal", ["https://www.gov.br/participamaisbrasil/conanda"], "Conanda / FNCA"),
    (r"pronon|pronas|minist[ée]rio da sa[úu]de", "federal", ["https://www.gov.br/saude/pt-br"], "Ministério da Saúde"),
    (r"\bfnde\b|\bmec\b", "federal", ["https://www.gov.br/fnde/pt-br"], "FNDE / MEC"),
    (r"bndes|fundo amaz[ôo]nia", "federal", ["https://www.bndes.gov.br/"], "BNDES"),
    (r"petrobras", "federal", ["https://petrobras.com.br/"], "Petrobras — programas socioambientais"),
    (r"\bcnj\b|destina[çc][ãa]o de penas", "federal", ["https://www.cnj.jus.br/"], "CNJ — destinações"),
    (r"\bmpf\b|minist[ée]rio p[úu]blico federal", "federal", ["https://www.mpf.mp.br/"], "Ministério Público Federal"),
    (r"emenda de bancada|congresso", "federal", ["https://www.camara.leg.br/", "https://www12.senado.leg.br/"], "Congresso Nacional"),
    (r"projetos aptos.*\blie\b", "federal", ["https://www.gov.br/esporte/pt-br/acoes-e-programas/lei-de-incentivo-ao-esporte"], "Lei de Incentivo ao Esporte — projetos aptos"),
    (r"receita federal|bens m[óo]veis apreendidos|mercadorias apreendidas", "federal", ["https://www.gov.br/receitafederal/pt-br"], "Receita Federal — destinação de mercadorias"),
    (r"coleta seletiva|compostagem|economia circular|horta comunit|nascente", "federal", ["https://www.gov.br/mma/pt-br", "https://www.bndes.gov.br/"], "MMA / Fundo Nacional do Meio Ambiente / BNDES"),
    (r"paradesporto|natac[ãa]o|[áa]rbitros e monitores", "federal", ["https://www.gov.br/esporte/pt-br"], "Ministério do Esporte / Comitê Paralímpico"),
    # privados nacionais — páginas institucionais de editais
    (r"bússola social|bussola social", "privada", ["https://bussolasocial.com.br/"], "Bússola Social — Bússola Editais"),
    (r"mapa das osc", "privada", ["https://mapaosc.ipea.gov.br/"], "Mapa das OSC (IPEA)"),
    (r"funda[çc][ãa]o arcelormittal", "privada", ["https://fundacaoarcelormittal.org.br/"], "Fundação ArcelorMittal"),
    (r"funda[çc][ãa]o banco do brasil", "privada", ["https://www.fbb.org.br/"], "Fundação Banco do Brasil"),
    (r"funda[çc][ãa]o bradesco", "privada", ["https://fundacao.bradesco/"], "Fundação Bradesco"),
    (r"funda[çc][ãa]o ita[úu]", "privada", ["https://www.fundacaoitau.org.br/"], "Fundação Itaú"),
    (r"funda[çc][ãa]o telef[ôo]nica", "privada", ["https://fundacaotelefonicavivo.org.br/"], "Fundação Telefônica Vivo"),
    (r"funda[çc][ãa]o vale", "privada", ["https://www.fundacaovale.org/"], "Fundação Vale"),
    (r"instituto claro", "privada", ["https://www.institutoclaro.org.br/"], "Instituto Claro"),
    (r"instituto coca-cola", "privada", ["https://www.institutococacolabrasil.com.br/"], "Instituto Coca-Cola Brasil"),
    (r"grupo botic[áa]rio", "privada", ["https://www.fundacaogrupoboticario.org.br/"], "Fundação Grupo Boticário"),
    (r"instituto localiza", "privada", ["https://institutolocaliza.com.br/"], "Instituto Localiza"),
    (r"lojas renner", "privada", ["https://www.institutolojasrenner.org.br/"], "Instituto Lojas Renner"),
    (r"instituto natura", "privada", ["https://www.institutonatura.org/"], "Instituto Natura"),
    (r"neoenergia", "privada", ["https://www.institutoneoenergia.org.br/"], "Instituto Neoenergia"),
    (r"instituto sabin", "privada", ["https://www.institutosabin.org.br/"], "Instituto Sabin"),
    (r"instituto sicoob", "privada", ["https://www.institutosicoob.org.br/"], "Instituto Sicoob"),
    (r"instituto unibanco", "privada", ["https://www.institutounibanco.org.br/"], "Instituto Unibanco"),
    (r"instituto votorantim", "privada", ["https://www.institutovotorantim.org.br/"], "Instituto Votorantim"),
    (r"destina[çc][ãa]o de ir pessoa jur[íi]dica", "privada", ["https://www.gov.br/participamaisbrasil/conanda"], "Destinação de IR ao Fundo da Criança (via conselhos)"),
    (r"compensa[çc][ãa]o ambiental", "privada", ["https://goias.gov.br/meioambiente/"], "Compensação ambiental — Semad/IBAMA"),
    # internacionais
    (r"\bbid\b", "internacional", ["https://www.iadb.org/pt-br"], "BID"),
    (r"banco mundial", "internacional", ["https://www.worldbank.org/pt/country/brazil"], "Banco Mundial"),
    (r"climate justice", "internacional", ["https://www.cjrfund.org/"], "Climate Justice Resilience Fund"),
    (r"echoing green", "internacional", ["https://echoinggreen.org/"], "Echoing Green"),
    (r"ford foundation", "internacional", ["https://www.fordfoundation.org/"], "Ford Foundation"),
    (r"gef small grants", "internacional", ["https://sgp.undp.org/"], "GEF Small Grants Programme"),
    (r"gates foundation", "internacional", ["https://www.gatesfoundation.org/"], "Gates Foundation"),
    (r"global fund for women", "internacional", ["https://www.globalfundforwomen.org/"], "Global Fund for Women"),
    (r"google\.org", "internacional", ["https://www.google.org/"], "Google.org"),
    (r"meta community", "internacional", ["https://www.facebook.com/community/"], "Meta Community Grants"),
    (r"microsoft philanthropies", "internacional", ["https://www.microsoft.com/pt-br/corporate-responsibility/philanthropies"], "Microsoft Philanthropies"),
    (r"oak foundation", "internacional", ["https://oakfnd.org/"], "Oak Foundation"),
    (r"open society", "internacional", ["https://www.opensocietyfoundations.org/"], "Open Society Foundations"),
    (r"pnud", "internacional", ["https://www.undp.org/pt/brazil"], "PNUD Brasil"),
    (r"rockefeller", "internacional", ["https://www.rockefellerfoundation.org/"], "Rockefeller Foundation"),
    (r"skoll", "internacional", ["https://skoll.org/"], "Skoll Foundation"),
    (r"unesco", "internacional", ["https://www.unesco.org/creativity/pt/ifcd"], "UNESCO — Fundo Internacional para a Diversidade Cultural"),
    (r"unicef", "internacional", ["https://www.unicef.org/brazil/"], "UNICEF Brasil"),
    (r"usaid", "internacional", ["https://www.usaid.gov/"], "USAID"),
    (r"erasmus", "internacional", ["https://erasmus-plus.ec.europa.eu/"], "União Europeia — Erasmus+"),
    (r"europeaid", "internacional", ["https://international-partnerships.ec.europa.eu/"], "União Europeia — International Partnerships"),
]
_GENERICO = {
    "diario_oficial_municipio": ["https://diariooficial.goiania.go.gov.br/"],
    "diario_oficial_estado": ["https://diariooficial.abc.go.gov.br/"],
    "diario_oficial_uniao": ["https://www.in.gov.br/"],
    "portal_compras_pncp": ["https://pncp.gov.br/"],
    "plataforma_agregadora": ["https://prosas.com.br/editais"],
    "resolucao_conselho": [],
    "emenda_parlamentar": [],
    "edital_destinacao_judicial": ["https://www.cnj.jus.br/"],
    "edital_ministerio_publico": ["https://www.mpgo.mp.br/", "https://www.mpf.mp.br/"],
    "lista_projetos_aptos": [],
    "pagina_institucional_privada": [],
    "submissao_internacional": [],
}
_PADRAO = {
    "editais_chamamentos": "edital", "fundos": "fundo", "emendas": "emenda",
    "incentivos_fiscais": "incentivo_fiscal", "justica_destinacoes": "destinacao_judicial",
    "doacoes_patrocinios": "doacao_patrocinio", "grants_internacionais": "grant",
    "outros": "outro",
}


def _fontes_json() -> dict:
    cfg = ROOT / "config/fontes.json"
    return {f["id"]: f for f in load_json(cfg).get("fontes", [])} if cfg.exists() else {}


def resolver(rota: dict, fontes: dict) -> dict:
    nome, nivel = rota["fonte_programa"], rota["nivel"]
    sites, orgao, confianca = [], None, "generica"
    # 1) catálogo validado
    for fc in rota.get("fontes_correspondentes") or []:
        f = fontes.get(fc.get("id"))
        if f and f.get("url"):
            sites.append(f["url"]); orgao = orgao or f.get("nome"); confianca = "confirmada"
    # 2) tabela institucional curada
    for padrao, niv, urls, org in _TABELA:
        if re.search(padrao, nome, re.I) and (niv == nivel or nivel in ("a_validar", "privada", "internacional")):
            for u in urls:
                if u not in sites:
                    sites.append(u)
            orgao = orgao or org
            if confianca != "confirmada":
                confianca = "curada"
            break
    # 3) forma de divulgação
    for u in _GENERICO.get(rota.get("forma_divulgacao") or "", []):
        if u not in sites:
            sites.append(u)
    uf = "GO" if re.search(r"goi[áa]s|goi[âa]nia|alego|tjgo|mpgo|tcm-go|seds|semasdh|cmdca|fmdca|fmas|feas|goyazes|fica\b|seel|ses-go|sms goi|sme goi|semad", nome, re.I) \
        or nivel in ("municipal", "estadual") else None
    return {
        "id": rota["id_acervo"], "programa": nome, "nivel": nivel,
        "area": slug(rota.get("area") or "outros").replace("-", "_")[:40],
        "tipo": _PADRAO.get(rota.get("tipo_catalogo"), "outro"),
        "forma_divulgacao": rota.get("forma_divulgacao"),
        "publicacao_obrigatoria": bool(rota.get("obrigatoriedade_publicacao")),
        "uf": uf, "goias": bool(uf),
        "orgao": orgao or "órgão a localizar",
        "sites": sites, "dominios": sorted({urlsplit(u).hostname for u in sites if u}),
        "confianca_site": confianca if sites else "pendente",
        "padrao": {
            "natureza": ("recurso" if rota.get("tipo_catalogo") in
                         ("editais_chamamentos", "fundos", "emendas", "grants_internacionais",
                          "justica_destinacoes", "incentivos_fiscais", "doacoes_patrocinios")
                         else "outro"),
            "canal": rota.get("camada_principal"),
            "confianca_rota": rota.get("confianca"),
        },
    }


def run() -> dict:
    rotas = load_json(ROTAS).get("rotas", [])
    fontes = _fontes_json()
    itens = [resolver(r, fontes) for r in rotas]
    # prioridade Goiás/Goiânia primeiro, depois federal e demais
    itens.sort(key=lambda i: (not i["goias"], i["nivel"] != "municipal",
                              i["nivel"] != "estadual", i["programa"]))
    dominios = Counter(d for i in itens for d in i["dominios"])
    conf = Counter(i["confianca_site"] for i in itens)
    resumo = {
        "gerado_em": now_iso(), "total": len(itens),
        "goias_goiania": sum(1 for i in itens if i["goias"]),
        "com_site": sum(1 for i in itens if i["sites"]),
        "confianca": dict(conf),
        "dominios_distintos": len(dominios),
        "top_dominios": dominios.most_common(15),
        "pendentes_de_localizacao": [{"id": i["id"], "programa": i["programa"], "nivel": i["nivel"]}
                                     for i in itens if not i["sites"]],
        "regra": ("site confirmado > curado > genérico; sem correspondência fica pendente — "
                  "nenhum endereço é inventado. A busca ativa confere cada site ao abrir."),
    }
    write_json(SAIDA_CFG, {"versao": 1, "resumo": {k: v for k, v in resumo.items()
                                                    if k not in ("pendentes_de_localizacao",)},
                           "fontes": itens})
    SAIDA_BIB.parent.mkdir(parents=True, exist_ok=True)
    write_json(SAIDA_BIB, {**resumo, "fontes": itens})
    return resumo


if __name__ == "__main__":
    r = run()
    print(json.dumps({k: v for k, v in r.items() if k != "pendentes_de_localizacao"},
                     ensure_ascii=False, indent=2))
    print("pendentes:", len(r["pendentes_de_localizacao"]))
