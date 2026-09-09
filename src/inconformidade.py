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
    r"firmar\s+acordos?\s+de\s+patroc[íi]nio|"
    # Rodada de 09/09/2026: Parintins/AM, Coari/AM, Três Coroas/RS e Irecê/BA
    # publicam "credenciamento para a captação de cotas de patrocínio" e
    # "interessadas em patrocinar os eventos". O recurso entra no órgão.
    r"capta[çc][ãa]o\s+(?:e\s+sele[çc][ãa]o\s+)?de\s+cotas?\s+de\s+patroc[íi]nio|"
    r"interessad[ao]s?\s+em\s+patrocinar|"
    r"sele[çc][ãa]o\s+de\s+patrocinador|"
    r"verbas?/cotas?\s+de\s+patroc[íi]nio", re.I)

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
    r"inexigibilidade\s+de\s+licita[çc][ãa]o[^.]{0,60}?contratada:|"
    # Rodada de 09/09/2026: Araquari/SC publicou "Celebração de parceria com a
    # COOPERATIVA DE ARAQUARI AGRICULTURA FAMILIAR, inscrita no CNPJ sob o nº...".
    # O parceiro está nomeado com CNPJ no próprio objeto: o negócio está fechado.
    r"(?:celebra[çc][ãa]o|formaliza[çc][ãa]o)\s+de\s+(?:parceria|termo)[^.]{0,80}?inscrit[ao]\s+no\s+CNPJ|"
    r"credenciamento\s+d[ao]\s+[A-Z\u00c0-\u00da][^,]{3,60},\s*(?:pessoa\s+f[íi]sica|inscrit)|"
    r"inscrit[ao]\s+no\s+CNPJ\s+sob\s+o\s+n", re.I)

# 6. Compra pública / fornecimento: a entidade vende, não recebe fomento.
_COMPRA = re.compile(
    r"projeto\s+de\s+venda|"
    r"interessados\s+em\s+fornecer\s+g[êe]neros\s+aliment[íi]cios|"
    r"chamada\s+p[úu]blica[^.]{0,60}?agricultura\s+familiar|"
    r"credenciamento[^.]{0,60}?recebimento\s+de\s+res[íi]duos\s+recicl[áa]veis|"
    # casos medidos na fila em 08/09: credenciamento de PESSOAS ou de EMPRESAS para prestar/fornecer,
    # e credenciamento para CAPTAR patrocínio para o próprio órgão
    r"credenciamento\s+de\s+(?:avaliadores|pareceristas|profissionais|peritos|leiloeiros|instrutores|oficineiros|artistas|empresas?|pessoas?\s+jur[íi]dicas?\s+para\s+presta)|"
    r"credenciamento[^.]{0,50}?(?:para\s+)?(?:a\s+)?capta[çc][ãa]o\s+(?:e\s+sele[çc][ãa]o\s+)?de\s+cotas\s+de\s+patroc[íi]nio|"
    r"credenciamento\s+de\s+empresa\s+para\s+aquisi[çc][ãa]o|"
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

# ---------------------------------------------------------------------------
# Segunda rodada — aprendido na verificação de 09/09/2026 (467 registros:
# 408 do PNCP e 59 de outras fontes). O número entre parênteses é quantos
# registros dessa rodada cairiam em cada família.
#
# A descoberta desta rodada é de uma família só, e ela é enorme:
# CREDENCIAMENTO PARA PRESTAR SERVIÇO AO ÓRGÃO. De 317 objetos lidos na API
# oficial do PNCP, 116 eram credenciamento de pessoa jurídica para prestar
# consulta médica, exame, serviço funerário, manutenção de veículo, lavagem
# de frota, hospedagem, transporte. Quase todos dizem "com ou sem fins
# lucrativos" ou "preferencialmente entidades filantrópicas" — e é exatamente
# essa frase que fazia o registro passar pelo filtro antigo. A entidade
# recebe por procedimento executado, em tabela SUS/SIGTAP: é receita de
# venda de serviço, não repasse de fomento.
#
# Nenhuma dessas famílias reprova quando o objeto nomeia um instrumento de
# fomento de verdade (termo de fomento, de colaboração, de execução cultural,
# acordo de cooperação, PNAB, Lei Paulo Gustavo, Lei 13.019). Nesse caso o
# veredito cai para ATENÇÃO, não para reprovação: é a diferença entre
# "credenciamento de clínica para fazer exame" e "credenciamento de OSC para
# celebrar termo de fomento na área da saúde". Falso positivo é o erro caro —
# perde oportunidade e não deixa rastro.
# ---------------------------------------------------------------------------

# 11. Prestação de serviço ao órgão, remunerada por unidade (116).
_SERVICO_AO_ORGAO = re.compile(
    r"presta[çc][ãa]o\s+d[eo]s?\s+servi[çc]|"
    r"interessad[oa]s?\s+em\s+prestar|"
    r"servi[çc]os?\s+(?:m[ée]dic|banc[áa]ri|funer[áa]ri|odontol[óo]gic|de\s+sa[úu]de|laboratori|socioassistenci)|"
    r"de\s+forma\s+complementar\s+a[o\s]{0,3}(?:sistema\s+[úu]nico|sus\b)|"
    r"complementar\s+a[o\s]{0,3}sus\b|"
    r"manuten[çc][ãa]o\s+(?:preventiva|corretiva)|"
    r"tabela\s+(?:sus|sigtap|abc)|"
    r"exames?\s+(?:laboratoriai|cl[íi]nic|de\s+imagem|eletivo)|"
    r"consultas?\s+(?:m[ée]dic|de\s+especialidade|e\s+exames)|"
    r"m[ée]dia\s+(?:e\s+alta\s+)?complexidade|"
    r"plant[õo]es\s+m[ée]dic|"
    r"pr[óo]teses?\s+(?:dent[áa]ri|odontol)|"
    r"lava(?:gem|[çc][ãa]o)\s+e\s+higieniza|"
    r"transporte\s+(?:sanit[áa]rio|universit[áa]rio|de\s+passageiros)|"
    r"servi[çc]os\s+de\s+hospedagem|"
    r"leiloeir|"
    r"cart[õo]es?\s+de\s+vale|"
    r"aux[íi]lio\s+(?:funeral|alimenta)|"
    r"demanda\s+de\s+vagas|vagas\s+d[ae]\s+educa[çc][ãa]o\s+infantil|"
    r"credenciamento\s+de\s+(?:m[ée]dicos|profissionais\s+de\s+sa[úu]de|laborat[óo]rios|cl[íi]nicas|farm[áa]cias|funer[áa]rias|hot[ée]is)|"
    r"exames?\s+especializados?|especialidades\s+m[ée]dicas?", re.I)

# 12. Compra ou fornecimento de bens ao órgão (34).
_FORNECIMENTO = re.compile(
    r"fornecimento\s+de\s+(?:g[êe]neros|alimentos|refei[çc][õo]es|combust[íi]ve|medicamentos|pe[çc]as|produtos)|"
    r"fornecer\s+produtos|interessad[oa]s?\s+em\s+fornecer|"
    r"aquisi[çc][ãa]o\s+de\s+(?:g[êe]neros|alimentos|hortifr[úu]t|vagas|certificados)|"
    r"g[êe]neros\s+aliment[íi]cios|alimenta[çc][ãa]o\s+escolar|\bPNAE\b|merenda\s+escolar|"
    r"produtos\s+l[áa]cteos|comercializa[çc][ãa]o\s+de\s+seus\s+produtos", re.I)

# 13. Imóvel e mercado imobiliário (12).
_IMOVEL = re.compile(
    r"prospec[çc][ãa]o\s+d[eo]\s+mercado\s+imobili|"
    r"prospec[çc][ãa]o\s+de\s+(?:mercado\s+de\s+)?im[óo]vei|"
    r"loca[çc][ãa]o\s+de\s+(?:um\s+|01\s*\(um\)\s*)?im[óo]ve|"
    r"credenciamento\s+de\s+im[óo]vei|"
    r"avalia[çc][õo]es\s+imobili[áa]ri|"
    r"cess[õo]es\s+de\s+im[óo]vei|\bcomodato\b|"
    r"contrato\s+de\s+arrendamento\s+de\s+superf[íi]cie", re.I)

# 14. Parecerista, avaliador, júri, subcomissão — destinatário é pessoa física
#     técnica, e o pagamento é por parecer emitido (12).
_PESSOA_FISICA_TECNICA = re.compile(
    r"parecerist|"
    r"avaliador(?:es)?(?:/parecerist)?|"
    r"j[úu]ri\s+art[íi]stic|"
    r"banco\s+de\s+(?:avaliador|parecerist)|"
    r"subcomiss[ãa]o\s+t[ée]cnica|"
    r"emiss[ãa]o\s+de\s+parecer|"
    r"compor\s+(?:a\s+)?comiss[ãa]o\s+de\s+(?:sele[çc][ãa]o|julgamento)", re.I)

# 15. Cachê artístico: contratação de artista, músico ou instrutor para evento (10).
_CACHE_ARTISTICO = re.compile(
    r"contrata[çc][ãa]o\s+de\s+artistas|"
    r"credenciamento\s+de\s+(?:artistas|m[úu]sicos|bandas|atra[çc][õo]es\s+art[íi]stic|instrutores)|"
    r"apresenta[çc][õo]es\s+(?:art[íi]stic|culturai)|"
    r"shows\s+musicai|"
    r"servi[çc]os\s+de\s+natureza\s+art[íi]stic|"
    r"desfile\s+c[íi]vico|arraial\s+cultural|embelezamento", re.I)

# 16. Instituição financeira, cooperativa de crédito, microcrédito (8).
#     Cuidado: "banco de fomento" tem a palavra fomento e enganava o filtro.
_FINANCEIRA = re.compile(
    r"institui[çc][õo]es?\s+financeiras?|"
    r"cooperativas?\s+de\s+cr[ée]dito|"
    r"bancos?\s+de\s+fomento|"
    r"bancos?\s+comerciais|"
    r"microcr[ée]dito|"
    r"servi[çc]os\s+banc[áa]ri|"
    r"arrecada[çc][ãa]o\s+de\s+tributos|recolhimento\s+de\s+tributos|"
    r"empr[ée]stimo\s+pessoal", re.I)

# 17. Permissão ou autorização de uso de espaço público para exploração
#     comercial: a entidade paga (ou vende), não recebe (6).
_USO_DE_ESPACO = re.compile(
    r"permiss[ãa]o\s+de\s+uso|"
    r"autoriza[çc][ãa]o\s+de\s+uso|"
    r"explora[çc][ãa]o\s+comercial|"
    r"\bstands?\b|"
    r"comercializa[çc][ãa]o\s+de\s+aliment|"
    r"venda\s+de\s+espa[çc]o|fornecimento\s+de\s+espa[çc]o|"
    r"venda\s+de\s+bebidas", re.I)

# 18. Destinado a entes públicos: adesão de municípios, prefeituras (1 —
#     Chamada Pública 01/2026 da SECULT/GO, "adesão de até 120 municípios").
_ENTES_PUBLICOS = re.compile(
    r"ades[ãa]o\s+(?:institucional\s+)?(?:volunt[áa]ria\s+)?de\s+(?:at[ée]\s+)?\d*\s*\(?[\w\s]{0,20}\)?\s*munic[íi]pios|"
    r"poder[ãa]o\s+aderir[^.]{0,60}?munic[íi]pios|"
    r"munic[íi]pios\s+e\s+distritos[^.]{0,60}?por\s+interm[ée]dio\s+de\s+suas\s+prefeituras|"
    r"credenciamento\s+de\s+[óo]rg[ãa]os\s+e\s+entidades\s+da\s+administra[çc][ãa]o", re.I)

# 19. Destinado a pessoa física fora do terceiro setor: prêmio para
#     jornalistas, estudantes, profissionais (2 — Prêmio MOL de Jornalismo).
_PESSOA_FISICA = re.compile(
    r"profissionais\s+e\s+estudantes\s+de\s+comunica[çc][ãa]o|"
    r"jornalistas\s+profissionais|"
    r"categorias?\s+jovem\s+jornalista|"
    r"destinad[oa]\s+a\s+estudantes", re.I)

# 20. Resultado de habilitação — parente do resultado_de_edital, mas a
#     redação é outra (2 — PNAB 2026 da SECULT/GO).
_RESULTADO_HABILITACAO = re.compile(
    r"resultado\s+(?:final|preliminar|parcial)\s+d[eo]s?\s+(?:habilitad|selecionad|classificad|inscri)|"
    r"divulgad[oa]\s+(?:o\s+)?resultado|"
    r"lista\s+de\s+(?:habilitad|pr[ée]-?qualificad|inscrit)|"
    r"prorroga[çc][ãa]o\s+do\s+prazo\s+para\s+divulga[çc][ãa]o\s+do\s+resultado|"
    r"pr[ée]-?qualificados\s+por\s+segmento|"
    r"contrata[çc][ãa]o\s+d[ao]s?\s+(?:empresa\s+|servi[çc]os?\s+em\s+sa[úu]de\s+d[ea]\s+)?credenciad|"
    r"oriund[oa]\s+do\s+edital", re.I)

# 21. Conteúdo institucional de portal de terceiros ou do próprio patrocinador:
#     página índice, notícia, pesquisa, livro, campanha, curso, desconto (24
#     dos 59 registros de outras fontes).
_INSTITUCIONAL = re.compile(
    r"lan[çc]a\s+(?:o\s+)?livro|"
    r"pesquisa\s+d[eo]\s+instituto|retrata\s+a\s+cultura|"
    r"\bplen[áa]rias?\b|receber[ãa]o\s+especialistas|"
    r"\bdesconto\b[^.]{0,40}?certifica[çc]|"
    r"guia\s+d[oe]s?\s+guias|"
    r"conhe[çc]a\s+os\s+profissionais|profissionais\s+certificados|"
    r"semana\s+de\s+doa[çc][ãa]o\s+de\s+sangue|"
    r"doa[çc][ãa]o\s+de\s+\d+\s+toneladas|"
    r"ag[êe]ncia\s+de\s+not[íi]cias|"
    r"o\s+perfil\s+das\s+organiza[çc][õo]es\s+da\s+sociedade\s+civil", re.I)

# Instrumento de fomento de verdade. Se aparecer, as famílias 11 a 17 e a 12
# não reprovam: rebaixam para atenção. É o resgate que impede o falso positivo.
_FOMENTO_FORTE = re.compile(
    r"termo\s+de\s+(?:fomento|colabora[çc][ãa]o|coopera[çc][ãa]o|execu[çc][ãa]o\s+cultural|conv[êe]nio|compromisso)|"
    r"acordo\s+de\s+coopera[çc][ãa]o|"
    r"lei\s+n?[º°]?\s*13\.?019|13\.019\/2014|"
    r"\bPNAB\b|aldir\s+blanc|paulo\s+gustavo|"
    r"recursos?\s+n[ãa]o\s+reembols[áa]ve|"
    r"m[úu]tua\s+(?:coopera[çc][ãa]o|colabora[çc][ãa]o)|"
    r"premia[çc][ãa]o\s+de\s+(?:projetos|agente)|"
    r"apoio\s+financeiro\s+[àa]s?\s+(?:organiza[çc][õo]es|quadrilhas|iniciativas)|"
    r"regime\s+de\s+colabora[çc][ãa]o|"
    # "fomento" solto conta: as famílias que usam a palavra por outro motivo
    # ("bancos de fomento") não são resgatáveis e reprovam de todo jeito.
    r"\bfomento\b", re.I)

# Fomento cultural nomeado: PNAB, Lei Paulo Gustavo, termo de execução cultural,
# repasse não reembolsável. Resgata o cachê artístico mesmo sem a palavra "OSC"
# no objeto, porque o fomento cultural admite grupo e coletivo — e um edital de
# PNAB para "artistas e grupos culturais locais" é oportunidade real de captação,
# não contratação de show. Foi o caso de Itacaré/BA nesta rodada.
_FOMENTO_CULTURAL = re.compile(
    r"\bPNAB\b|aldir\s+blanc|paulo\s+gustavo|"
    r"termo\s+de\s+execu[çc][ãa]o\s+cultural|"
    r"recursos?\s+n[ãa]o\s+reembols[áa]ve|"
    r"fomento\s+direto|"
    r"fomentar\s+a\s+cultura|fomento\s+aos?\s+artistas|"
    r"premia[çc][ãa]o\s+de\s+(?:projetos|agente)", re.I)

# Entidade sem fins lucrativos mencionada no objeto.
_TERCEIRO_SETOR = re.compile(
    r"organiza[çc][õo]es?\s+d[ae]\s+sociedade\s+civil|\bOSCs?\b|"
    r"sem\s+fins\s+lucrativos|filantr[óo]pic|"
    r"entidades?\s+de\s+utilidade\s+p[úu]blica|"
    r"\bcoletivos?\b|associa[çc][õo]es|cooperativas", re.I)

# Serviço socioassistencial de alta complexidade: acolhimento, ILPI,
# comunidade terapêutica. Pode ser parceria (fomento) ou contratação — o
# objeto não diz. Nunca reprova sozinho; vai a conferência humana.
_SOCIOASSISTENCIAL = re.compile(
    r"socioassistenci|"
    r"prote[çc][ãa]o\s+social\s+especial|"
    r"acolhimento\s+institucional|"
    r"longa\s+perman[êe]ncia|\bILPI\b|"
    r"comunidades?\s+terap[êe]utic|"
    r"reabilita[çc][ãa]o\s+(?:intelectual|psicossocial)", re.I)

_FAMILIAS_V2 = (
    ("resultado_de_habilitacao", _RESULTADO_HABILITACAO,
     "é o resultado, a contratação decorrente ou a prorrogação de um edital já julgado — a inscrição fechou"),
    ("conteudo_institucional", _INSTITUCIONAL,
     "conteúdo institucional ou notícia do portal (livro, pesquisa, campanha, curso, desconto) — não é edital"),
    ("destinado_a_entes_publicos", _ENTES_PUBLICOS,
     "destinatário são municípios, prefeituras ou órgãos públicos: OSC não pode se inscrever"),
    ("destinado_a_pessoa_fisica", _PESSOA_FISICA,
     "destinatário são pessoas físicas fora do terceiro setor (jornalistas, estudantes, profissionais)"),
    ("parecerista_ou_juri", _PESSOA_FISICA_TECNICA,
     "credenciamento de parecerista, avaliador ou júri: pagamento por parecer emitido, não fomento a projeto"),
    ("instituicao_financeira", _FINANCEIRA,
     "credenciamento de instituição financeira, cooperativa de crédito ou operador de microcrédito"),
    ("imovel_ou_mercado", _IMOVEL,
     "prospecção imobiliária, locação, comodato ou arrendamento — fora do terceiro setor"),
    ("uso_de_espaco_publico", _USO_DE_ESPACO,
     "permissão ou autorização de uso de espaço público para exploração comercial: a entidade vende, não recebe"),
    ("cache_artistico", _CACHE_ARTISTICO,
     "contratação de artista, músico ou instrutor para evento do órgão: é cachê por apresentação, não fomento"),
    ("compra_ou_fornecimento", _FORNECIMENTO,
     "compra ou fornecimento de bens ao órgão: a entidade entra como fornecedora e recebe por venda"),
    ("servico_ao_orgao", _SERVICO_AO_ORGAO,
     "credenciamento para prestar serviço ao órgão, remunerado por procedimento executado: é contratação, não fomento"),
)

# Famílias que decidem ANTES das genéricas da primeira rodada, porque são
# recortes mais precisos do mesmo descarte. Nenhuma delas é resgatável: um
# banco, um parecerista, um município e um resultado de habilitação não viram
# oportunidade de captação por citarem a palavra fomento.
_FAMILIAS_ESPECIFICAS = (
    ("resultado_de_habilitacao", _RESULTADO_HABILITACAO,
     "é o resultado, a contratação decorrente ou a prorrogação de um edital já julgado — a inscrição fechou"),
    ("parecerista_ou_juri", _PESSOA_FISICA_TECNICA,
     "credenciamento de parecerista, avaliador ou júri: pagamento por parecer emitido, não fomento a projeto"),
    ("instituicao_financeira", _FINANCEIRA,
     "credenciamento de instituição financeira, cooperativa de crédito ou operador de microcrédito"),
    ("destinado_a_entes_publicos", _ENTES_PUBLICOS,
     "destinatário são municípios, prefeituras ou órgãos públicos: OSC não pode se inscrever"),
    ("destinado_a_pessoa_fisica", _PESSOA_FISICA,
     "destinatário são pessoas físicas fora do terceiro setor (jornalistas, estudantes, profissionais)"),
    ("conteudo_institucional", _INSTITUCIONAL,
     "conteúdo institucional ou notícia do portal (livro, pesquisa, campanha, curso, desconto) — não é edital"),
)

# As famílias que o resgate de fomento rebaixa para atenção em vez de reprovar.
_RESGATAVEIS = frozenset({
    "servico_ao_orgao", "compra_ou_fornecimento", "cache_artistico",
    "uso_de_espaco_publico", "imovel_ou_mercado",
})

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
    # Rodada de 09/09/2026: uma errata muda o cronograma. O prazo que vale é o
    # da errata, não o do edital original — e quem lê a base precisa saber.
    (re.compile(r"\berrata\b|retifica[çc][ãa]o\s+d[eo]\s+cronograma|republica[çc][ãa]o\s+d[eo]\s+edital", re.I),
     "há errata ou retificação de cronograma: o prazo vigente é o da errata — conferir a versão em vigor antes de usar a data"),
    (_SOCIOASSISTENCIAL,
     "serviço socioassistencial de alta complexidade: pode ser parceria de fomento ou contratação de vaga — conferir o instrumento no edital"),
)


def avaliar(texto: str) -> dict:

    """Veredito de conformidade de objeto.

    Três níveis, porque a verificação mostrou que nem tudo é sim ou não:
      - {'ok': True,  'atencao': None}  — chamada aberta de fomento;
      - {'ok': True,  'atencao': str}   — passa, mas com ressalva de enquadramento;
      - {'ok': False, 'familia': str}   — não é edital de fomento a OSC.

    A ordem importa. Primeiro as famílias da primeira rodada, que são
    reprovações duras e precisas. Depois as da segunda rodada, que descrevem
    contratação e compra — e essas admitem resgate: se o objeto nomeia um
    instrumento de fomento de verdade e menciona entidade sem fins lucrativos,
    o veredito cai para atenção em vez de reprovar. É o que separa
    "credenciamento de clínica para fazer exame" de "credenciamento de OSC
    para celebrar termo de fomento na área da saúde".
    """
    t = re.sub(r"\s+", " ", texto or "").strip()

    # Resgate que vem antes de tudo. O filtro de compra pública passou a pegar
    # "credenciamento de artistas", e com isso engolia o edital de PNAB de
    # Itacaré/BA, que é fomento direto com repasse não reembolsável a artistas e
    # grupos culturais. Parecerista continua barrado: sob PNAB ou não, quem
    # emite parecer presta serviço técnico.
    if (_FOMENTO_CULTURAL.search(t) and _CACHE_ARTISTICO.search(t)
            and not _PESSOA_FISICA_TECNICA.search(t)):
        return {"ok": True, "familia": None, "motivo": "objeto compatível com fomento a OSC",
                "atencao": ("fomento cultural direto a artistas e grupos: confirmar no edital se admite "
                            "pessoa jurídica sem fins lucrativos como proponente")}

    # Famílias específicas que precisam decidir antes das genéricas, para que o
    # motivo registrado seja o certo. Um credenciamento de parecerista rotulado
    # como "compra pública" reprova pelo motivo errado, e o motivo é o que o
    # titular lê quando reabre o caso.
    for nome, rx, motivo in _FAMILIAS_ESPECIFICAS:
        if rx.search(t):
            return {"ok": False, "familia": nome, "motivo": motivo, "atencao": None}

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
    tem_fomento = bool(_FOMENTO_FORTE.search(t))
    tem_osc = bool(_TERCEIRO_SETOR.search(t))
    for nome, rx, motivo in _FAMILIAS_V2:
        if not rx.search(t):
            continue
        if nome == "cache_artistico" and _FOMENTO_CULTURAL.search(t):
            return {"ok": True, "familia": None,
                    "motivo": "objeto compatível com fomento a OSC",
                    "atencao": ("fomento cultural direto a artistas e grupos: confirmar no edital se admite "
                                "pessoa jurídica sem fins lucrativos como proponente")}
        if nome in _RESGATAVEIS and _SOCIOASSISTENCIAL.search(t) and tem_osc:
            return {"ok": True, "familia": None,
                    "motivo": "objeto compatível com fomento a OSC",
                    "atencao": ("serviço socioassistencial de alta complexidade com entidade sem fins "
                                "lucrativos: pode ser parceria de fomento ou contratação de vaga — conferir "
                                "o instrumento no edital")}
        if nome in _RESGATAVEIS and tem_fomento and tem_osc:
            return {"ok": True, "familia": None,
                    "motivo": "objeto compatível com fomento a OSC",
                    "atencao": ("o objeto nomeia instrumento de fomento mas descreve prestação de serviço "
                                "(%s): conferir no edital se o repasse é por plano de trabalho ou por "
                                "procedimento executado" % nome)}
        return {"ok": False, "familia": nome, "motivo": motivo, "atencao": None}
    if _SOCIOASSISTENCIAL.search(t) and tem_osc:
        return {"ok": True, "familia": None, "motivo": "objeto compatível com fomento a OSC",
                "atencao": ("serviço socioassistencial de alta complexidade: pode ser parceria de fomento ou "
                            "contratação de vaga — conferir o instrumento no edital")}
    for rx, aviso in _ATENCAO:
        if rx.search(t):
            return {"ok": True, "familia": None, "motivo": "objeto compatível com fomento a OSC", "atencao": aviso}
    if not tem_fomento and not tem_osc:
        # Não reprova. O princípio deste módulo é vetar por sinal POSITIVO de
        # inconformidade, nunca por ausência de palavra do terceiro setor: há
        # edital de fomento escrito com vocabulário pobre ("CHAMAMENTO PÚBLICO
        # RESÍDUOS SÓLIDOS", de Curitiba, é objeto de uma linha e pode ser
        # parceria com cooperativa de catadores). Vai a conferência humana.
        return {"ok": True, "familia": None, "motivo": "objeto compatível com fomento a OSC",
                "atencao": ("objeto sem marca de fomento e sem menção a entidade sem fins lucrativos: "
                            "insuficiente para enquadrar — abrir o edital antes de descartar")}
    if not tem_fomento:
        return {"ok": True, "familia": None, "motivo": "objeto compatível com fomento a OSC",
                "atencao": ("menciona entidade sem fins lucrativos mas não nomeia instrumento de fomento: "
                            "conferir no edital qual é o instrumento e se há repasse")}
    if not tem_osc:
        return {"ok": True, "familia": None, "motivo": "objeto compatível com fomento a OSC",
                "atencao": ("nomeia instrumento de fomento mas não diz se admite OSC: conferir no edital "
                            "quem pode se inscrever")}
    # P04-P09 (auditoria de 09/09): as regras com acerto medido decidem o que as famílias
    # acima deixaram passar. Entram DEPOIS para preservar os rótulos já validados, e só
    # reprovam por sinal POSITIVO de inconformidade (P24 — falso positivo é o erro caro).
    try:
        from .parametros_motores import avaliar_medido
        _m = avaliar_medido(texto)
        if _m.get("veredito") == "reprovado":
            return {"ok": False, "familia": "medida_auditoria",
                    "motivo": _m["motivo"] + (f" [{_m['parametro']}, {_m['medida']}]" if _m.get("medida") else f" [{_m['parametro']}]"),
                    "atencao": None}
        if _m.get("veredito") == "atencao":
            return {"ok": True, "familia": None, "motivo": "objeto compatível com fomento a OSC",
                    "atencao": _m["motivo"]}
    except Exception:
        pass
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
