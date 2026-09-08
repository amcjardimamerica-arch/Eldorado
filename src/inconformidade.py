"""Inconformidade de objeto — o veto aprendido na verificação de 08/09/2026.

Contexto. Na verificação manual dos 210 registros de `docs/dados/nao_verificados.json`,
82 deles (39%) NÃO eram edital de fomento a OSC. Nenhum foi barrado por
`pertinencia.pertinente()`, e a razão é sempre a mesma: o texto cita "projetos
culturais", "sem fins lucrativos" ou "termo de fomento", o que liga o
`_TERCEIRO_SETOR_FORTE` e neutraliza o veto de empresa. O filtro antigo pergunta
"o texto fala de terceiro setor?"; faltava perguntar "isto é uma CHAMADA ABERTA
que repassa recurso a uma entidade?".

Este módulo responde a segunda pergunta. São seis famílias, todas medidas em
casos reais da verificação — o número entre parênteses é quantos registros dos
210 cairiam em cada uma:

1. resultado_de_edital (21) — "Contratação do proponente FULANO, selecionado no
   Edital do Chamamento Público 01/2025". É o CONTRATO que decorre de um edital
   já julgado, publicado no PNCP como registro próprio. Não há inscrição.
2. empresa_ou_mercado (15) — "seleção/habilitação de empresa da construção
   civil", "prospecção de mercado imobiliário", "contratação de serviços
   técnicos". O filtro antigo pegava "contratação de empresa", não "seleção de
   empresa" nem "habilitação de empresa".
3. busca_patrocinador (6) — "chamamento público para a oferta de cotas de
   patrocínio para a realização do campeonato". O dinheiro ENTRA no órgão. O
   filtro antigo só vetava "cotas de patrocínio DE EMPRESAS".
4. qualificacao_previa (5) — "chamamento público para qualificação de pessoas
   jurídicas como Organização Social". Habilita para um futuro contrato de
   gestão; não repassa nada e não tem projeto. Atenção: é diferente de
   "seleção de entidade JÁ QUALIFICADA como OSCIP para celebrar termo de
   parceria", que é chamada real e precisa passar.
5. parceria_ja_celebrada (10) — "dispensa de chamamento público", "termo de
   fomento que entre si celebram", "repasse financeiro à Associação X". O
   parceiro está nomeado no próprio instrumento.
6. compra_publica (1+) — chamada pública da agricultura familiar (PNAE) e
   credenciamento de recebedor de resíduos: a entidade entra como fornecedora e
   recebe por venda.

O veto é sempre por SINAL POSITIVO de inconformidade, nunca por ausência de
palavra do terceiro setor — assim uma entidade não é descartada só porque o
edital foi escrito com vocabulário pobre.
"""
from __future__ import annotations

import re

# 1. Resultado de edital: o proponente já está nomeado.
_RESULTADO = re.compile(
    r"contrata[çc][ãa]o\s+d[oa]\s+proponente|"
    r"contrata[çc][ãa]o\s+art[íi]stica,?\s+segundo\s+edital|"
    r"selecionad[oa]\s+e\s+classificad[oa]\s+no\s+edital|"
    r"para\s+apresenta[çc][ãa]o\s+d[aoe].{0,60}?selecionad", re.I)

# 2. Empresa / mercado: o filtro antigo não cobria "seleção" e "habilitação".
_EMPRESA_EXTRA = re.compile(
    r"(?:sele[çc][ãa]o|habilita[çc][ãa]o|credenciar|selecionar\s+e\s+credenciar)\s+(?:p[úu]blica\s+)?de\s+empresas?\b|"
    r"empresas?\s+d[oae]\s+ramo\s+d[ae]\s+constru[çc][ãa]o|"
    r"empresas?\s+d[ae]\s+constru[çc][ãa]o\s+civil|"
    r"empresas?\s+construtoras?|"
    r"prospec[çc][ãa]o\s+de\s+mercado\s+imobili[áa]rio|"
    r"sele[çc][ãa]o\s+de\s+im[óo]vel\s+urbano|"
    r"contrata[çc][ãa]o\s+de\s+servi[çc]os\s+t[ée]cnicos\s+profissionais|"
    r"incentivo\s+econ[ôo]mico[^.]{0,40}?empresas?|"
    r"empresas?\s+para\s+concess[ãa]o\s+de\s+incentivo|"
    r"empresas?\s+interessadas\s+em\s+receber,?\s+em\s+doa[çc][ãa]o|"
    r"entidade\s+fechada\s+de\s+previd[êe]ncia\s+complementar|\bEFPC\b|"
    r"utiliza[çc][ãa]o\s+de\s+espa[çc]o\s+p[úu]blico|"
    r"emprego\s+de\s+m[ãa]o\s+de\s+obra|"
    r"exporem\s+e\s+comercializarem|"
    r"credenciar\s+institui[çc][õo]es[^.]{0,60}?doa[çc][ãa]o\s+de\s+bens\s+m[óo]veis|"
    r"bens\s+m[óo]veis\s+considerados\s+inserv[íi]veis", re.I)

# 3. O órgão buscando patrocinador: o recurso entra, não sai.
_PATROCINADOR = re.compile(
    r"oferta\s+de\s+cotas?\s+de\s+patroc[íi]nio|"
    r"capta[çc][ãa]o\s+de\s+(?:cotas?\s+de\s+)?(?:recursos?\s+financeiros?|patroc[íi]nio)[^.]{0,50}?(?:por\s+meio\s+de\s+patroc[íi]nio|para\s+custeio|para\s+a\s+realiza[çc][ãa]o)|"
    r"interessad[ao]s?\s+em\s+adquirir\s+cotas?\s+de\s+patroc[íi]nio|"
    r"propostas?\s+de\s+patroc[íi]nio[^.]{0,80}?(?:expositor|artes[ãa]os|food\s*truck)|"
    r"firmar\s+acordos?\s+de\s+patroc[íi]nio", re.I)

# 4. Qualificação prévia como OS/OSS — sem repasse e sem projeto.
_QUALIFICACAO = re.compile(
    r"qualifica[çc][ãa]o\s+de\s+(?:pessoas?\s+jur[íi]dicas?|entidades?)[^.]{0,90}?organiza[çc][ãa]o\s+social|"
    r"qualifica[çc][ãa]o\s+de\s+entidades?[^.]{0,60}?como\s+organiza[çc][ãa]o\s+social|"
    r"interessadas?\s+em\s+se\s+qualificar(?:em)?\s+como\s+organiza[çc][ãa]o\s+social|"
    r"processo\s+de\s+qualifica[çc][ãa]o\s+de\s+entidades?\s+privadas?[^.]{0,60}?organiza[çc][ãa]o\s+social|"
    r"entidades?\s+privadas?\s+sem\s+fins\s+lucrativos,?\s+qualificad[ao]s?\s+como\s+organiza[çc][õo]es?\s+sociais|"
    r"habilita[çc][ãa]o\s+(?:para|de)\s+eventual\s+e\s+futuro\s+(?:termo|contrato)", re.I)
# ...mas "entidade JÁ qualificada como OSCIP/OS para celebrar termo" é chamada real.
_QUALIFICACAO_SALVA = re.compile(
    r"qualificada\s+como\s+organiza[çc][ãa]o\s+(?:da\s+sociedade\s+civil\s+de\s+interesse\s+p[úu]blico|social)[^.]{0,80}?"
    r"para\s+(?:celebrar|celebra[çc][ãa]o)", re.I)

# 5. Parceria já celebrada / parceiro nominal.
_JA_CELEBRADA = re.compile(
    r"dispensa\s+de\s+chamamento\s+p[úu]blico|"
    r"termo\s+de\s+(?:fomento|colabora[çc][ãa]o)\s+que\s+(?:entre\s+si\s+)?celebram|"
    r"repasse\s+financeiro\s+(?:a|para)\s+(?:a\s+)?associa[çc][ãa]o\s+\w|"
    r"termo\s+de\s+fomento\s+(?:entre|com)\s+a\s+(?:secretaria|associa[çc][ãa]o|apae|funda[çc][ãa]o|institui[çc][ãa]o)|"
    r"^\s*referente\s+ao\s+termo\s+de\s+fomento|"
    r"o\s+presente\s+termo\s+de\s+fomento\s+tem\s+por\s+objeto|"
    r"convoca[çc][ãa]o\s+d[ae]s?\s+(?:entidades|coletivos)[^.]{0,80}?listad|"
    r"celebra[çc][ãa]o\s+de\s+termo\s+de\s+fomento\s+entre\s+o\s+munic[íi]pio\s+\w+[^.]{0,40}?\be\s+a\s+\w|"
    r"inexigibilidade\s+de\s+licita[çc][ãa]o[^.]{0,60}?contratada:", re.I)

# 6. Compra pública / fornecimento: a entidade vende, não recebe fomento.
_COMPRA = re.compile(
    r"projeto\s+de\s+venda|"
    r"interessados\s+em\s+fornecer\s+g[êe]neros\s+aliment[íi]cios|"
    r"chamada\s+p[úu]blica[^.]{0,60}?agricultura\s+familiar|"
    r"credenciamento[^.]{0,60}?recebimento\s+de\s+res[íi]duos\s+recicl[áa]veis|"
    r"credenciamento\s+para\s+(?:a\s+)?contrata[çc][ãa]o\s+de[^.]{0,60}?servi[çc]os\s+ambulatoriais|"
    r"contratar\s+as?\s+entidades?\s+privadas?[^.]{0,60}?para\s+presta[çc][ãa]o", re.I)


# 7. Contrato de gestão com Organização Social — gestão de serviço público, não fomento.
_CONTRATO_GESTAO = re.compile(
    r"contrato\s+de\s+gest[ãa]o|"
    r"organiza[çc][ãa]o\s+social\s+de\s+sa[úu]de|\bOSS\b|"
    r"gerenciamento,?\s+(?:a\s+)?operacionaliza[çc][ãa]o\s+e\s+(?:a\s+)?execu[çc][ãa]o\s+d[eao]s?\s+(?:a[çc][õo]es|servi[çc]os)", re.I)

# 8. Conteúdo editorial capturado por engano pelo coletor.
_EDITORIAL = re.compile(
    r"hist[óo]rias?\s+de\s+sucesso|\bpodcast\b|\be-?book\b|"
    r"\bcase\s+de\s+sucesso\b|blog\s+d[eo]\s+|leia\s+mais", re.I)

# 9. Prêmio interno da administração — não admite OSC como proponente.
_PREMIO_INTERNO = re.compile(
    r"destina-?se\s+a\s+tribunais|"
    r"[óo]rg[ãa]os\s+do\s+sistema\s+de\s+justi[çc]a|"
    r"destinad[oa]\s+a\s+(?:[óo]rg[ãa]os|entes)\s+p[úu]blicos", re.I)

# 10. Página de termos já celebrados (a armadilha de goias.gov.br/cultura/termos-de-fomento):
# título isolado, sem número de edital nem objeto.
_PAGINA_TERMOS = re.compile(r"^\s*termos?\s+de\s+fomento\s*$", re.I)

_FAMILIAS = (
    ("resultado_de_edital", _RESULTADO,
     "é o contrato decorrente de um edital já julgado, com proponente nomeado — não há inscrição"),
    ("parceria_ja_celebrada", _JA_CELEBRADA,
     "parceria com entidade nominal (dispensa de chamamento ou termo já celebrado) — não há fase de inscrição"),
    ("busca_patrocinador", _PATROCINADOR,
     "o órgão busca patrocinador: o recurso entra no órgão, não é repassado à entidade"),
    ("empresa_ou_mercado", _EMPRESA_EXTRA,
     "seleção de empresa, de serviço técnico ou de imóvel — fora do terceiro setor"),
    ("compra_publica", _COMPRA,
     "compra ou credenciamento de fornecedor: a entidade recebe por venda, não por fomento"),
    ("conteudo_editorial", _EDITORIAL,
     "conteúdo editorial (matéria, case, podcast) capturado por engano — não é edital"),
    ("premio_interno", _PREMIO_INTERNO,
     "prêmio restrito a órgãos públicos: OSC não pode se inscrever"),
    ("pagina_de_termos_celebrados", _PAGINA_TERMOS,
     "página de termos já celebrados, sem número de edital e sem fase de inscrição"),
)


# Sinais que não reprovam, mas exigem conferência humana antes de virar caso.
_ATENCAO = (
    (re.compile(r"inexigibilidade", re.I),
     "instrumento por inexigibilidade: pode não ter havido disputa aberta — conferir antes de tratar como oportunidade"),
    (re.compile(r"acordo\s+de\s+coopera[çc][ãa]o|sem\s+transfer[êe]ncia\s+de\s+recursos", re.I),
     "acordo de cooperação: costuma não envolver repasse financeiro"),
    (re.compile(r"\bOSCIP\b|organiza[çc][ãa]o\s+da\s+sociedade\s+civil\s+de\s+interesse\s+p[úu]blico", re.I),
     "exige qualificação prévia como OSCIP: confirmar se a entidade já a possui"),
)


def avaliar(texto: str) -> dict:
    """Veredito de conformidade de objeto.

    Três níveis, porque a verificação mostrou que nem tudo é sim ou não:
      - {'ok': True,  'atencao': None}  — chamada aberta de fomento;
      - {'ok': True,  'atencao': str}   — passa, mas com ressalva de enquadramento;
      - {'ok': False, 'familia': str}   — não é edital de fomento a OSC.
    """
    t = re.sub(r"\s+", " ", texto or "").strip()
    for nome, rx, motivo in _FAMILIAS:
        if rx.search(t):
            return {"ok": False, "familia": nome, "motivo": motivo, "atencao": None}
    if _QUALIFICACAO.search(t) and not _QUALIFICACAO_SALVA.search(t):
        return {"ok": False, "familia": "qualificacao_previa",
                "motivo": "qualificação prévia como Organização Social: habilita para futuro contrato, sem repasse nem projeto",
                "atencao": None}
    if _CONTRATO_GESTAO.search(t):
        return {"ok": False, "familia": "contrato_de_gestao",
                "motivo": "contrato de gestão com Organização Social: gestão de serviço público, com qualificação prévia — não é fomento a projeto",
                "atencao": None}
    for rx, aviso in _ATENCAO:
        if rx.search(t):
            return {"ok": True, "familia": None, "motivo": "objeto compatível com fomento a OSC", "atencao": aviso}
    return {"ok": True, "familia": None, "motivo": "objeto compatível com fomento a OSC", "atencao": None}


def avaliar_item(item: dict) -> dict:
    """Mesmo veredito, a partir de um registro de oportunidade.

    O título é avaliado à parte porque algumas armadilhas só se reconhecem pelo
    título isolado — "Termos de Fomento", sozinho, é a página de termos já
    celebrados do Estado de Goiás, e não um edital.
    """
    titulo = re.sub(r"\s+", " ", str(item.get("titulo") or "")).strip()
    if _PAGINA_TERMOS.match(titulo):
        return {"ok": False, "familia": "pagina_de_termos_celebrados",
                "motivo": "página de termos já celebrados, sem número de edital e sem fase de inscrição",
                "atencao": None}
    texto = " ".join(str(item.get(c) or "") for c in ("titulo", "objeto", "evidencia"))
    return avaliar(texto[:4000])
