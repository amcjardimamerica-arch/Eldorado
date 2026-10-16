# Conselho dos motores — 2ª rodada (validação das correções) — 2026-10-16

## Dra. Irene Lacerda (extremamente pessimista)

- Dos motores cegos e de página vazia da 1ª rodada, quantos já tiveram a rota testada pelo afinador?
- A rota nova traz sinal de edital ou só responde?
- Algum continua cego mesmo depois da troca de rota?

```json
{
 "cegos_da_1a_rodada": 28,
 "testados": 21,
 "com_rota_nova": 7,
 "via_ponte": 0,
 "continuam_cegos": [
  "camara-goiania-pl",
  "f260-captacao-218",
  "f260-captacao-223",
  "f260-captacao-229",
  "f260-captacao-230",
  "f260-captacao-233",
  "f260-captacao-234",
  "f260-captacao-235",
  "f260-captacao-222",
  "f260-curadoria-008",
  "f260-espalhado-acessoainformacao-cavalcante-go-gov-br",
  "f260-captacao-252",
  "f260-captacao-242",
  "f260-espalhado-rouanet-cultura-gov-br"
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
   "achados_total_1a": 28,
   "achados_total_agora": 28,
   "no_fluxo": 5,
   "confirmadas": 0
  },
  {
   "motor": "f260-captacao-118",
   "achados_total_1a": 29,
   "achados_total_agora": 29,
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
   "achados_total_1a": 131,
   "achados_total_agora": 131,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "plat-empresas-editais-incentivados",
   "achados_total_1a": 39,
   "achados_total_agora": 39,
   "no_fluxo": 8,
   "confirmadas": 0
  },
  {
   "motor": "f260-captacao-069",
   "achados_total_1a": 27,
   "achados_total_agora": 27,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "f260-captacao-025",
   "achados_total_1a": 35,
   "achados_total_agora": 35,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "f260-curadoria-009",
   "achados_total_1a": 61,
   "achados_total_agora": 61,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "outras-oportunidades-1",
   "achados_total_1a": 80,
   "achados_total_agora": 80,
   "no_fluxo": 19,
   "confirmadas": 0
  },
  {
   "motor": "outras-oportunidades-2",
   "achados_total_1a": 48,
   "achados_total_agora": 48,
   "no_fluxo": 16,
   "confirmadas": 0
  },
  {
   "motor": "outras-oportunidades-4",
   "achados_total_1a": 28,
   "achados_total_agora": 28,
   "no_fluxo": 23,
   "confirmadas": 0
  },
  {
   "motor": "outras-oportunidades-6",
   "achados_total_1a": 36,
   "achados_total_agora": 36,
   "no_fluxo": 9,
   "confirmadas": 0
  },
  {
   "motor": "outras-oportunidades-7",
   "achados_total_1a": 77,
   "achados_total_agora": 77,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "plataforma-mapas-culturais",
   "achados_total_1a": 66,
   "achados_total_agora": 66,
   "no_fluxo": 12,
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
 "exemplos_da_rede_de_rotas": 10106
}
```

## Dr. Otávio Lemos (neutro)

- A fatia de oportunidades achadas fora dos motores diminuiu?
- Quais domínios só os agregadores encontram e ainda não têm motor?

```json
{
 "fora_dos_motores_pct_1a": 70.5,
 "fora_dos_motores_pct_agora": 70.5,
 "origem": {
  "Piloto": 147,
  "agregador/outra": 253,
  "motor": 167
 },
 "dominios_so_de_agregador": [
  {
   "dominio": "data.queridodiario.ok.org.br",
   "oportunidades": 6
  },
  {
   "dominio": "fapesp.br",
   "oportunidades": 5
  },
  {
   "dominio": "culteditais.cultura.gov.br",
   "oportunidades": 4
  },
  {
   "dominio": "conselho.saude.gov.br",
   "oportunidades": 3
  },
  {
   "dominio": "fapemig.br",
   "oportunidades": 2
  },
  {
   "dominio": "dgartes.gov.pt",
   "oportunidades": 2
  },
  {
   "dominio": "salinas.mg.gov.br",
   "oportunidades": 2
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
   "dominio": "transparencia.adustina.ba.gov.br",
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
 "dia_de_referencia": "2026-10-15",
 "ativos": 159,
 "lidos_ontem": 51,
 "lidos_hoje": 134,
 "nao_lidos_ontem_nem_hoje": [
  "plat-captamos",
  "plat-rede-filantropia",
  "pncp-api"
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
 "fontes_recebidas": 409,
 "por_origem": {
  "conselho (fontes irmãs)": 167,
  "Cartório (site oficial certificado)": 200,
  "Espião (privado/internacional)": 42
 },
 "lidas_nas_ultimas_24h": 315,
 "dimensionamento": {
  "fontes": 409,
  "sites_por_execucao": 17,
  "execucoes_por_dia": 3,
  "sites_por_clone_por_dia": 51,
  "clones": 8,
  "cobertura_diaria": 408,
  "segundos_por_execucao": {
   "tipico": 88,
   "pior_caso": 238
  },
  "le_todas_no_dia": false
 },
 "clones_que_ja_leram": {
  "outras-oportunidades-1": {
   "ultima": "2026-10-16T00:13:45+00:00",
   "duracao_s": 90,
   "achados": 39
  },
  "outras-oportunidades-2": {
   "ultima": "2026-10-15T23:08:48+00:00",
   "duracao_s": 97,
   "achados": 1
  },
  "outras-oportunidades-3": {
   "ultima": "2026-10-16T00:15:56+00:00",
   "duracao_s": 131,
   "achados": 6
  },
  "outras-oportunidades-4": {
   "ultima": "2026-10-15T15:24:09+00:00",
   "duracao_s": 84,
   "achados": 12
  },
  "outras-oportunidades-5": {
   "ultima": "2026-10-16T00:17:51+00:00",
   "duracao_s": 115,
   "achados": 3
  },
  "outras-oportunidades-6": {
   "ultima": "2026-10-16T00:25:18+00:00",
   "duracao_s": 118,
   "achados": 24
  },
  "outras-oportunidades-7": {
   "ultima": "2026-10-16T00:21:14+00:00",
   "duracao_s": 69,
   "achados": 10
  },
  "outras-oportunidades-8": {
   "ultima": "2026-10-15T23:11:00+00:00",
   "duracao_s": 131,
   "achados": 5
  }
 },
 "com_achado": 64
}
```

## Dr. Fábio Rangel (extremamente otimista)

- Os adaptadores por plataforma responderam? Quantas APIs abriram e quantos achados vieram?
- Quais plataformas valem o próximo adaptador?

```json
{
 "adaptadores": {
  "plataforma-wordpress": {
   "ultima": "2026-10-15T23:05:37+00:00",
   "achados": 9,
   "diagnostico": {
    "sites": 20,
    "instancias": null,
    "respostas_json": 43,
    "posts": 60,
    "oportunidades": null,
    "motivo_zero": null
   }
  },
  "plataforma-mapas-culturais": {
   "ultima": "2026-10-16T00:20:05+00:00",
   "achados": 17,
   "diagnostico": {
    "sites": null,
    "instancias": 12,
    "respostas_json": 5,
    "posts": null,
    "oportunidades": 49,
    "motivo_zero": null
   }
  }
 },
 "proximos_candidatos": {
  "WordPress": {
   "orgaos": 113,
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
   "orgaos": 12,
   "exemplos": [
    "culteditais.cultura.gov.br",
    "editaisdobrasil.com",
    "mapa.cultura.es.gov.br",
    "mapa.cultura.gov.br",
    "mapacultural.cim-amfri.sc.gov.br",
    "mapacultural.pa.gov.br"
   ]
  },
  "Diário municipal em lote (AGM/DOM)": {
   "orgaos": 17,
   "exemplos": [
    "campobelo.mg.gov.br",
    "diariooficial.abc.go.gov.br",
    "diariooficial.goiania.go.gov.br",
    "diariooficial.palmas.to.gov.br",
    "diariooficial.vitoria.es.gov.br",
    "divinopolisdotocantins.to.gov.br"
   ]
  },
  "Portal de transparência de fornecedor": {
   "orgaos": 21,
   "exemplos": [
    "bndes.gov.br",
    "comunidade.transparenciainternacional.org.br",
    "gov.br",
    "itacoatiara.am.gov.br",
    "itumbiara.go.gov.br",
    "mpf.mp.br"
   ]
  },
  "Sistemas de editais (Prosas/Editais)": {
   "orgaos": 49,
   "exemplos": [
    "adustina.ba.gov.br",
    "alteditais.com.br",
    "arapongas.pr.gov.br",
    "banrisulcultural.com.br",
    "bonde.org",
    "cajuru.sp.gov.br"
   ]
  }
 }
}
```
