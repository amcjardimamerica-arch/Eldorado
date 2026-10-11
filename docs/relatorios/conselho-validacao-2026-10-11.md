# Conselho dos motores — 2ª rodada (validação das correções) — 2026-10-11

## Dra. Irene Lacerda (extremamente pessimista)

- Dos motores cegos e de página vazia da 1ª rodada, quantos já tiveram a rota testada pelo afinador?
- A rota nova traz sinal de edital ou só responde?
- Algum continua cego mesmo depois da troca de rota?

```json
{
 "cegos_da_1a_rodada": 34,
 "testados": 28,
 "com_rota_nova": 12,
 "via_ponte": 0,
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
  "f260-captacao-242",
  "f260-espalhado-rouanet-cultura-gov-br"
 ],
 "aguardando_afinador": 6
}
```

## Prof. Caio Menezes (pessimista)

- Os motores de ruído da 1ª rodada continuam registrando achados que não viram oportunidade?
- A troca de rota aumentou a produção sem perder precisão?

```json
{
 "motores_de_ruido_1a": 19,
 "ruido_agora": [
  {
   "motor": "empresas-incentivadas",
   "achados_total_1a": 42,
   "achados_total_agora": 42,
   "no_fluxo": 1,
   "confirmadas": 0
  },
  {
   "motor": "f260-captacao-051",
   "achados_total_1a": 108,
   "achados_total_agora": 108,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "f260-captacao-098",
   "achados_total_1a": 58,
   "achados_total_agora": 58,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "f260-captacao-118",
   "achados_total_1a": 24,
   "achados_total_agora": 24,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "f260-captacao-151",
   "achados_total_1a": 56,
   "achados_total_agora": 56,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "f260-captacao-035",
   "achados_total_1a": 89,
   "achados_total_agora": 89,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "f260-captacao-217",
   "achados_total_1a": 91,
   "achados_total_agora": 91,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "f260-captacao-237",
   "achados_total_1a": 49,
   "achados_total_agora": 49,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "f260-captacao-038",
   "achados_total_1a": 99,
   "achados_total_agora": 99,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "f260-curadoria-006",
   "achados_total_1a": 84,
   "achados_total_agora": 84,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "plat-empresas-editais-incentivados",
   "achados_total_1a": 613,
   "achados_total_agora": 613,
   "no_fluxo": 2,
   "confirmadas": 0
  },
  {
   "motor": "plat-mp-destinacoes-reparacao",
   "achados_total_1a": 42,
   "achados_total_agora": 42,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "plat-prefeituras-50-go",
   "achados_total_1a": 51,
   "achados_total_agora": 51,
   "no_fluxo": 1,
   "confirmadas": 0
  },
  {
   "motor": "f260-captacao-025",
   "achados_total_1a": 28,
   "achados_total_agora": 28,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "f260-curadoria-001",
   "achados_total_1a": 20,
   "achados_total_agora": 20,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "f260-curadoria-004",
   "achados_total_1a": 20,
   "achados_total_agora": 20,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "mptgo-destinacao",
   "achados_total_1a": 47,
   "achados_total_agora": 47,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "f260-curadoria-009",
   "achados_total_1a": 40,
   "achados_total_agora": 40,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "outras-oportunidades-1",
   "achados_total_1a": 31,
   "achados_total_agora": 31,
   "no_fluxo": 6,
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
 "pontos_com_redundancia": 10,
 "redundancia_vazia": [],
 "dominios_via_ponte": 1,
 "exemplos_da_rede_de_rotas": 1691
}
```

## Dr. Otávio Lemos (neutro)

- A fatia de oportunidades achadas fora dos motores diminuiu?
- Quais domínios só os agregadores encontram e ainda não têm motor?

```json
{
 "fora_dos_motores_pct_1a": 81.2,
 "fora_dos_motores_pct_agora": 81.2,
 "origem": {
  "agregador/outra": 295,
  "motor": 90,
  "Piloto": 94
 },
 "dominios_so_de_agregador": [
  {
   "dominio": "data.queridodiario.ok.org.br",
   "oportunidades": 8
  },
  {
   "dominio": "fapesp.br",
   "oportunidades": 6
  },
  {
   "dominio": "fapesc.sc.gov.br",
   "oportunidades": 4
  },
  {
   "dominio": "conselho.saude.gov.br",
   "oportunidades": 3
  },
  {
   "dominio": "mapa.cultura.gov.br",
   "oportunidades": 2
  },
  {
   "dominio": "fappr.pr.gov.br",
   "oportunidades": 2
  },
  {
   "dominio": "monteazulpaulista.sp.gov.br",
   "oportunidades": 1
  },
  {
   "dominio": "fccr.sp.gov.br",
   "oportunidades": 1
  },
  {
   "dominio": "prefeitura.poa.br",
   "oportunidades": 1
  },
  {
   "dominio": "performeurope.eu",
   "oportunidades": 1
  },
  {
   "dominio": "transartists.org",
   "oportunidades": 1
  },
  {
   "dominio": "veranstaltungen.emma-pf.de",
   "oportunidades": 1
  },
  {
   "dominio": "itacoatiara.am.gov.br",
   "oportunidades": 1
  },
  {
   "dominio": "gulbenkian.pt",
   "oportunidades": 1
  },
  {
   "dominio": "hto.ifsp.edu.br",
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
 "dia_de_referencia": "2026-10-10",
 "ativos": 159,
 "lidos_ontem": 100,
 "lidos_hoje": 48,
 "nao_lidos_ontem_nem_hoje": [
  "plat-captamos",
  "plat-rede-filantropia"
 ],
 "ainda_sem_primeira_leitura": [
  "motor-gife",
  "motor-patrocinio",
  "outras-oportunidades-4",
  "outras-oportunidades-5",
  "outras-oportunidades-6",
  "outras-oportunidades-7",
  "outras-oportunidades-8",
  "piloto-aberto",
  "plataforma-mapas-culturais",
  "plataforma-wordpress",
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
 "fontes_recebidas": 202,
 "por_origem": {
  "conselho (fontes irmãs)": 129,
  "Cartório (site oficial certificado)": 73
 },
 "lidas_nas_ultimas_24h": 120,
 "dimensionamento": {
  "fontes": 202,
  "sites_por_execucao": 17,
  "execucoes_por_dia": 3,
  "sites_por_clone_por_dia": 51,
  "clones": 4,
  "cobertura_diaria": 202,
  "segundos_por_execucao": {
   "tipico": 88,
   "pior_caso": 238
  },
  "le_todas_no_dia": true
 },
 "clones_que_ja_leram": {
  "outras-oportunidades-1": {
   "ultima": "2026-10-10T21:59:34+00:00",
   "duracao_s": 30,
   "achados": 22
  },
  "outras-oportunidades-2": {
   "ultima": "2026-10-10T22:00:11+00:00",
   "duracao_s": 37,
   "achados": 2
  },
  "outras-oportunidades-3": {
   "ultima": "2026-10-10T22:01:03+00:00",
   "duracao_s": 51,
   "achados": 0
  }
 },
 "com_achado": 12
}
```

## Dr. Fábio Rangel (extremamente otimista)

- Os adaptadores por plataforma responderam? Quantas APIs abriram e quantos achados vieram?
- Quais plataformas valem o próximo adaptador?

```json
{
 "adaptadores": "aguardando a primeira leitura pela agenda (09h53 e 11h23 de Brasília)",
 "proximos_candidatos": {
  "WordPress": {
   "orgaos": 53,
   "exemplos": [
    "alvoradadonorte.go.gov.br",
    "anater.org",
    "banrisulcultural.com.br",
    "baoba.org.br",
    "brasil.aperam.com",
    "cachoeiraalta.go.gov.br"
   ]
  },
  "Mapas Culturais": {
   "orgaos": 10,
   "exemplos": [
    "culteditais.cultura.gov.br",
    "mapa.cultura.es.gov.br",
    "mapa.cultura.gov.br",
    "mapacultural.pa.gov.br",
    "mapacultural.pe.gov.br",
    "mapacultural.saobernardo.sp.gov.br"
   ]
  },
  "Diário municipal em lote (AGM/DOM)": {
   "orgaos": 13,
   "exemplos": [
    "campobelo.mg.gov.br",
    "diariooficial.abc.go.gov.br",
    "diariooficial.goiania.go.gov.br",
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
    "mpf.mp.br",
    "muribeca.se.gov.br",
    "saude.mg.gov.br",
    "transparencia.adustina.ba.gov.br"
   ]
  },
  "Sistemas de editais (Prosas/Editais)": {
   "orgaos": 39,
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
