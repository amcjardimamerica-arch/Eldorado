"""PNCP PARA O TERCEIRO SETOR — entender a finalidade de cada publicação antes de aceitá-la.

O PNCP é o portal das contratações da Lei 14.133/2021: compra, obra, serviço, locação, leilão.
Parceria com organização da sociedade civil é regida por outra lei (a 13.019/2014, o MROSC) e
não é contratação — só aparece no PNCP quando o ente a publica "de carona" numa modalidade da
14.133, quase sempre credenciamento (12) ou concurso (3). Por isso a maior parte do que o portal
publica NÃO serve a uma associação, e o que serve vem misturado com o que não serve, na mesma
modalidade e às vezes com as mesmas palavras.

A decisão tem três passos, nesta ordem:

    1. POSITIVO    há sinal de terceiro setor? (OSC, fomento, prêmio, subvenção, fundo municipal)
                   Sem sinal: não é para o terceiro setor, e nem se olha mais.
    2. CONTROLE    entre os positivos, há sinal de que o destino é EMPRESA? (empresa especializada,
                   menor preço, fornecimento, ME/EPP, prestação de serviço ao órgão…)
                   O controle só age DEPOIS do positivo: é ele que separa o "credenciamento de
                   agentes culturais para premiação" do "credenciamento de empresas de exames".
    3. EXCEÇÃO     sinal forte de parceria MROSC (termo de fomento, termo de colaboração, Lei
                   13.019) vence o controle: o edital de parceria cita "empresa" ao vetar.

O resultado não é só sim ou não: é a FINALIDADE da proposta e a PERTINÊNCIA dela para uma OSC.
"""
from __future__ import annotations

import re
import unicodedata


def _n(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", str(s or "").lower())
                   if unicodedata.category(c) != "Mn")


# 1 · LÉXICO POSITIVO — sinais de que a proposta se dirige ao terceiro setor
POSITIVO = {
    "parceria_mrosc": ["organizacao da sociedade civil", "organizacoes da sociedade civil", " osc ", " oscs ",
                       "termo de fomento", "termo de colaboracao", "acordo de cooperacao", "lei 13.019",
                       "lei n 13.019", "13.019/2014", "mrosc", "chamamento publico de osc"],
    # calibrado contra o gabarito de 23/09: "com ou sem fins lucrativos", cooperativas e agremiações
    # eram pertinentes e passavam despercebidos
    "entidade_sem_fins": ["sem fins lucrativos", "entidade filantropica", "entidades filantropicas",
                          "entidade beneficente", "cooperativa", "agremiac", "organizacoes comunitarias",
                          "organizacoes de pequeno porte", "coletivos", "instituicoes de longa permanencia",
                          "subprojeto", "selecao de propostas", "apoio a iniciativas"],
    "fomento_cultural": ["lei paulo gustavo", "pnab", "aldir blanc", "politica nacional aldir blanc",
                         "agentes culturais", "agente cultural", "projetos culturais", "premiacao",
                         "premio", "fomento a cultura", "fomento cultural", "mestres da cultura"],
    "fundo_social": ["fmas", "fmdca", "fundo municipal dos direitos", "fundo municipal de assistencia",
                     "fundo da infancia", "fia ", "cmdca", "cmas", "conselho municipal", "subvencao social",
                     "subvencoes sociais", "fundo do idoso"],
    # "chamamento público" e "fomento" SOZINHOS não entram: no PNCP o chamamento é usado para
    # tudo (hotéis, combustível, imóvel) — medido no corpus de 768 publicações
    "fomento_geral": ["projetos sociais", "projeto social", "projetos esportivos", "apoio a projetos",
                      "selecao de projetos", "fomento a projetos", "fomento ao esporte"],
}

# 2 · LÉXICO DE CONTROLE — sinais de que o destino é EMPRESA. Só age depois do positivo.
CONTROLE = {
    "empresa_como_destino": ["empresa especializada", "empresas especializadas", "contratacao de empresa",
                             "pessoa juridica de direito privado com fins", "com fins lucrativos",
                             "microempresa", "empresa de pequeno porte", "me/epp", "me e epp",
                             "exclusiva para me", "cota reservada"],
    "julgamento_de_preco": ["menor preco", "maior desconto", "maior lance", "melhor lance",
                            "registro de precos", "ata de registro"],
    "compra_ou_fornecimento": ["fornecimento de", "aquisicao de", "aquisicoes de", "generos alimenticios",
                               "material de consumo", "equipamentos"],
    "servico_ao_orgao": ["prestacao de servicos", "prestacao de servico", "servicos de engenharia",
                         "credenciamento de empresas", "credenciamento de clinicas", "credenciamento de laboratorios",
                         "credenciamento de prestadores", "credenciamento de pessoas juridicas",
                         "credenciamento de leiloeiros", "exames", "consultas medicas", "plantoes",
                         "combustive", "hoteis", "pousadas", "passagens aereas", "agencias de viagens",
                         "estabelecimentos de saude", "profissionais formados", "aquisicao imobiliaria"],
    "financeiro": ["instituicao financeira", "instituicoes financeiras", "folha de pagamento", "consignado"],
    "obra_ou_imovel": ["execucao de obra", "reforma de", "construcao de", "locacao de imovel",
                       "permissao de uso", "concessao de uso", "alienacao"],
    "pessoa_fisica_servico": ["pareceristas", "parecerista", "jurados", "cache", "apresentacoes artisticas",
                              "contratacao artistica", "instrutores", "oficineiros",
                              "confeccao, entrega", "montagem e desmontagem", "execucao dos servicos"],
}

# 3 · EXCEÇÃO — parceria MROSC explícita vence o controle
EXCECAO = ["termo de fomento", "termo de colaboracao", "lei 13.019", "13.019/2014", "mrosc",
           "organizacao da sociedade civil", "organizacoes da sociedade civil"]

PERTINENCIA = {
    "parceria_mrosc": "alta", "fomento_cultural": "alta", "fundo_social": "alta",
    "entidade_sem_fins": "media", "fomento_geral": "media",
}
FINALIDADE_DO_CONTROLE = {
    "empresa_como_destino": "contratação de empresa", "julgamento_de_preco": "licitação por preço",
    "compra_ou_fornecimento": "compra pública", "servico_ao_orgao": "serviço prestado ao órgão",
    "financeiro": "serviço financeiro", "obra_ou_imovel": "obra, imóvel ou uso de espaço",
    "pessoa_fisica_servico": "contratação de pessoa para serviço ao órgão",
}


def _acha(texto: str, grupos: dict) -> dict:
    t = f" {_n(texto)} "
    return {g: [p for p in ps if p in t] for g, ps in grupos.items() if any(p in t for p in ps)}


def classificar(objeto: str, titulo: str = "") -> dict:
    """A finalidade da proposta e a pertinência para o terceiro setor, com o porquê."""
    texto = f"{titulo} {objeto}"
    pos = _acha(texto, POSITIVO)
    if not pos:
        return {"passo": "positivo", "terceiro_setor": False, "pertinencia": "nula",
                "finalidade": "contratação pública comum", "porque": "nenhum sinal de terceiro setor"}
    ctrl = _acha(texto, CONTROLE)
    exc = [p for p in EXCECAO if p in f" {_n(texto)} "]
    # CREDENCIAMENTO SEM FOMENTO É HABILITAÇÃO DE PRESTADOR — a regra que o sistema já adota na
    # missão especial: credenciamento só serve à OSC quando nomeia o instrumento de repasse ou o
    # fomento cultural/social. Sem isso, é cadastro para vender serviço ao órgão.
    forte = exc or pos.get("fomento_cultural") or pos.get("fundo_social") or pos.get("entidade_sem_fins")
    if "credenciament" in _n(texto) and not forte and "servico_ao_orgao" not in ctrl:
        ctrl["servico_ao_orgao"] = ["credenciamento sem instrumento de fomento"]
    melhor = min(pos, key=lambda g: ["parceria_mrosc", "fomento_cultural", "fundo_social",
                                     "entidade_sem_fins", "fomento_geral"].index(g))
    if ctrl and not exc:
        g = next(iter(ctrl))
        return {"passo": "controle", "terceiro_setor": False, "pertinencia": "nula",
                "finalidade": FINALIDADE_DO_CONTROLE[g],
                "porque": f"tinha sinal de terceiro setor ({', '.join(pos[melhor][:2])}), mas o destino é "
                          f"{FINALIDADE_DO_CONTROLE[g]} ({', '.join(ctrl[g][:2])})",
                "sinais": {"positivo": pos, "controle": ctrl}}
    return {"passo": "exceção" if ctrl else "positivo", "terceiro_setor": True,
            "pertinencia": PERTINENCIA[melhor],
            "finalidade": {"parceria_mrosc": "parceria com OSC (MROSC)", "fomento_cultural": "fomento ou prêmio cultural",
                           "fundo_social": "fundo ou conselho de direitos", "entidade_sem_fins": "seleção de entidade sem fins lucrativos",
                           "fomento_geral": "fomento a projeto"}[melhor],
            "porque": (f"sinal de terceiro setor ({', '.join(pos[melhor][:2])})"
                       + (f"; o controle apontou {', '.join(ctrl[next(iter(ctrl))][:1])}, mas a parceria MROSC é explícita "
                          f"({exc[0]})" if ctrl else "")),
            "sinais": {"positivo": pos, "controle": ctrl}}
