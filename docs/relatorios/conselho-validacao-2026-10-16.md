# Conselho dos motores — 2ª rodada (validação das correções) — 2026-10-16

## Dra. Irene Lacerda (extremamente pessimista)

- Dos motores cegos e de página vazia da 1ª rodada, quantos já tiveram a rota testada pelo afinador?
- A rota nova traz sinal de edital ou só responde?
- Algum continua cego mesmo depois da troca de rota?

```json
{
 "cegos_da_1a_rodada": 31,
 "testados": 24,
 "com_rota_nova": 7,
 "via_ponte": 1,
 "continuam_cegos": [
  "camara-goiania-pl",
  "f260-captacao-218",
  "f260-captacao-223",
  "f260-captacao-227",
  "f260-captacao-229",
  "f260-captacao-230",
  "f260-captacao-233",
  "f260-captacao-234",
  "f260-captacao-235",
  "f260-captacao-222",
  "f260-curadoria-008",
  "f260-espalhado-acessoainformacao-cavalcante-go-gov-br",
  "f260-captacao-228",
  "f260-captacao-252",
  "f260-captacao-240",
  "f260-espalhado-rouanet-cultura-gov-br",
  "f260-espalhado-sistema-mirassoldoeste-mt-gov-br"
 ],
 "aguardando_afinador": 7
}
```

## Prof. Caio Menezes (pessimista)

- Os motores de ruído da 1ª rodada continuam registrando achados que não viram oportunidade?
- A troca de rota aumentou a produção sem perder precisão?

```json
{
 "motores_de_ruido_1a": 14,
 "ruido_agora": [
  {
   "motor": "empresas-incentivadas",
   "achados_total_1a": 29,
   "achados_total_agora": 29,
   "no_fluxo": 4,
   "confirmadas": 0
  },
  {
   "motor": "f260-captacao-118",
   "achados_total_1a": 31,
   "achados_total_agora": 31,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "f260-captacao-044",
   "achados_total_1a": 31,
   "achados_total_agora": 31,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "plat-cnpq-extensao",
   "achados_total_1a": 133,
   "achados_total_agora": 133,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "plat-empresas-editais-incentivados",
   "achados_total_1a": 47,
   "achados_total_agora": 47,
   "no_fluxo": 9,
   "confirmadas": 0
  },
  {
   "motor": "f260-captacao-069",
   "achados_total_1a": 54,
   "achados_total_agora": 54,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "f260-captacao-025",
   "achados_total_1a": 37,
   "achados_total_agora": 37,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "f260-curadoria-009",
   "achados_total_1a": 68,
   "achados_total_agora": 68,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "outras-oportunidades-1",
   "achados_total_1a": 97,
   "achados_total_agora": 97,
   "no_fluxo": 5,
   "confirmadas": 0
  },
  {
   "motor": "outras-oportunidades-2",
   "achados_total_1a": 55,
   "achados_total_agora": 55,
   "no_fluxo": 3,
   "confirmadas": 0
  },
  {
   "motor": "outras-oportunidades-6",
   "achados_total_1a": 42,
   "achados_total_agora": 42,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "outras-oportunidades-7",
   "achados_total_1a": 82,
   "achados_total_agora": 82,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "plataforma-mapas-culturais",
   "achados_total_1a": 68,
   "achados_total_agora": 68,
   "no_fluxo": 10,
   "confirmadas": 0
  },
  {
   "motor": "outras-oportunidades-8",
   "achados_total_1a": 26,
   "achados_total_agora": 26,
   "no_fluxo": 2,
   "confirmadas": 0
  }
 ],
 "ruido_que_passou_a_confirmar": []
}
```

## Eng. Luana Freire (levemente pessimista)

- A redundância é saudável ou há pontos lidos por vários motores sem que nenhum renda (redundância vazia)?
- Quanto custa o afinador e quantos domínios passaram a depender da ponte?

```json
{
 "pontos_com_redundancia": 17,
 "redundancia_vazia": [],
 "dominios_via_ponte": 3,
 "exemplos_da_rede_de_rotas": 10498
}
```

## Dr. Otávio Lemos (neutro)

- A fatia de oportunidades achadas fora dos motores diminuiu?
- Quais domínios só os agregadores encontram e ainda não têm motor?

```json
{
 "fora_dos_motores_pct_1a": 73.6,
 "fora_dos_motores_pct_agora": 73.6,
 "origem": {
  "motor": 111,
  "Piloto": 131,
  "agregador/outra": 178
 },
 "dominios_so_de_agregador": [
  {
   "dominio": "fapesp.br",
   "oportunidades": 5
  },
  {
   "dominio": "performeurope.eu",
   "oportunidades": 1
  },
  {
   "dominio": "hto.ifsp.edu.br",
   "oportunidades": 1
  },
  {
   "dominio": "www2.fab.mil.br",
   "oportunidades": 1
  },
  {
   "dominio": "finep.gov.br",
   "oportunidades": 1
  },
  {
   "dominio": "licitacoes.caixa.gov.br",
   "oportunidades": 1
  },
  {
   "dominio": "sejaumvoluntario.sisicmbio.icmbio.gov.br",
   "oportunidades": 1
  },
  {
   "dominio": "florestamaisamazonia.mma.gov.br",
   "oportunidades": 1
  },
  {
   "dominio": "wordpress.sea.sc.gov.br",
   "oportunidades": 1
  },
  {
   "dominio": "sape.sc.gov.br",
   "oportunidades": 1
  },
  {
   "dominio": "fapemig.br",
   "oportunidades": 1
  },
  {
   "dominio": "api.site.fapemig.br",
   "oportunidades": 1
  },
  {
   "dominio": "mapacultural.pe.gov.br",
   "oportunidades": 1
  },
  {
   "dominio": "prefeitura.poa.br",
   "oportunidades": 1
  }
 ],
 "nota": "a fatia só cai depois que os motores novos (Outras Oportunidades, plataformas) completarem as primeiras leituras"
}
```

## Eng. Diego Arakaki (levemente otimista)

- A leitura diária está sendo cumprida por todos os motores ativos?
- Quem não foi lido ontem nem hoje?

```json
{
 "dia_de_referencia": "2026-10-16",
 "ativos": 157,
 "lidos_ontem": 129,
 "lidos_hoje": 130,
 "nao_lidos_ontem_nem_hoje": [
  "plat-captamos",
  "plat-rede-filantropia"
 ],
 "ainda_sem_primeira_leitura": [
  "motor-gife",
  "motor-patrocinio",
  "piloto-aberto",
  "site-abcr",
  "site-brazilfoundation",
  "site-capitaai",
  "site-cese",
  "site-editais-culturais",
  "site-farol-cultural",
  "site-funarte",
  "site-fundo-baoba",
  "site-fundo-brasil",
  "site-fundo-casa",
  "site-idis",
  "site-mapa-osc",
  "site-mapas-culturais",
  "site-observatorio-terceiro-setor",
  "site-prosas",
  "site-rede-comua",
  "site-rede-filantropia",
  "site-transferegov",
  "site-undef"
 ]
}
```

## Profa. Clara Nogueira (otimista)

- Outras Oportunidades está recebendo as fontes novas e lendo todas no mesmo dia?
- Os clones dão conta do volume?

```json
{
 "fontes_recebidas": 395,
 "por_origem": {
  "conselho (fontes irmãs)": 166,
  "Cartório (site oficial certificado)": 181,
  "Espião (privado/internacional)": 48
 },
 "lidas_nas_ultimas_24h": 338,
 "dimensionamento": {
  "fontes": 395,
  "sites_por_execucao": 17,
  "execucoes_por_dia": 3,
  "sites_por_clone_por_dia": 51,
  "clones": 8,
  "cobertura_diaria": 395,
  "segundos_por_execucao": {
   "tipico": 88,
   "pior_caso": 238
  },
  "le_todas_no_dia": true
 },
 "clones_que_ja_leram": {
  "outras-oportunidades-1": {
   "ultima": "2026-10-16T12:20:42+00:00",
   "duracao_s": 43,
   "achados": 39
  },
  "outras-oportunidades-2": {
   "ultima": "2026-10-16T12:24:57+00:00",
   "duracao_s": 98,
   "achados": 1
  },
  "outras-oportunidades-3": {
   "ultima": "2026-10-16T11:23:04+00:00",
   "duracao_s": 64,
   "achados": 4
  },
  "outras-oportunidades-4": {
   "ultima": "2026-10-16T13:52:07+00:00",
   "duracao_s": 74,
   "achados": 3
  },
  "outras-oportunidades-5": {
   "ultima": "2026-10-16T11:22:00+00:00",
   "duracao_s": 115,
   "achados": 3
  },
  "outras-oportunidades-6": {
   "ultima": "2026-10-16T12:21:55+00:00",
   "duracao_s": 72,
   "achados": 20
  },
  "outras-oportunidades-7": {
   "ultima": "2026-10-16T11:13:18+00:00",
   "duracao_s": 137,
   "achados": 13
  },
  "outras-oportunidades-8": {
   "ultima": "2026-10-16T12:26:29+00:00",
   "duracao_s": 92,
   "achados": 1
  }
 },
 "com_achado": 56
}
```

## Dr. Fábio Rangel (extremamente otimista)

- Os adaptadores por plataforma responderam? Quantas APIs abriram e quantos achados vieram?
- Quais plataformas valem o próximo adaptador?

```json
{
 "adaptadores": {
  "plataforma-wordpress": {
   "ultima": "2026-10-16T12:23:19+00:00",
   "achados": 3,
   "diagnostico": {
    "sites": 20,
    "instancias": null,
    "respostas_json": 42,
    "posts": 40,
    "oportunidades": null,
    "motivo_zero": null
   }
  },
  "plataforma-mapas-culturais": {
   "ultima": "2026-10-16T11:03:51+00:00",
   "achados": 15,
   "diagnostico": {
    "sites": null,
    "instancias": 11,
    "respostas_json": 4,
    "posts": null,
    "oportunidades": 40,
    "motivo_zero": null
   }
  }
 },
 "proximos_candidatos": {
  "WordPress": {
   "orgaos": 114,
   "exemplos": [
    "abong.org.br",
    "acaoeducativa.org.br",
    "alvoradadonorte.go.gov.br",
    "anater.org",
    "banrisulcultural.com.br",
    "baoba.org.br"
   ]
  },
  "Mapas Culturais": {
   "orgaos": 11,
   "exemplos": [
    "culteditais.cultura.gov.br",
    "editaisdobrasil.com",
    "mapa.cultura.es.gov.br",
    "mapa.cultura.gov.br",
    "mapacultural.pa.gov.br",
    "mapacultural.pe.gov.br"
   ]
  },
  "Diário municipal em lote (AGM/DOM)": {
   "orgaos": 14,
   "exemplos": [
    "diariooficial.abc.go.gov.br",
    "diariooficial.goiania.go.gov.br",
    "diariooficial.palmas.to.gov.br",
    "diariooficial.vitoria.es.gov.br",
    "divinopolisdotocantins.to.gov.br",
    "dom.morrodochapeu.ba.gov.br"
   ]
  },
  "Portal de transparência de fornecedor": {
   "orgaos": 15,
   "exemplos": [
    "bndes.gov.br",
    "comunidade.transparenciainternacional.org.br",
    "gov.br",
    "itumbiara.go.gov.br",
    "mpf.mp.br",
    "rio.rj.gov.br"
   ]
  },
  "Sistemas de editais (Prosas/Editais)": {
   "orgaos": 43,
   "exemplos": [
    "alteditais.com.br",
    "banrisulcultural.com.br",
    "bonde.org",
    "cajuru.sp.gov.br",
    "chamamentos.serpro.gov.br",
    "climaesociedade.org"
   ]
  }
 }
}
```
