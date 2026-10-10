# Conselho dos motores — 2ª rodada (validação das correções) — 2026-10-10

## Dra. Irene Lacerda (extremamente pessimista)

- Dos motores cegos e de página vazia da 1ª rodada, quantos já tiveram a rota testada pelo afinador?
- A rota nova traz sinal de edital ou só responde?
- Algum continua cego mesmo depois da troca de rota?

```json
{
 "cegos_da_1a_rodada": 34,
 "testados": 6,
 "com_rota_nova": 4,
 "via_ponte": 0,
 "continuam_cegos": [
  "camara-goiania-pl",
  "f260-captacao-218"
 ],
 "aguardando_afinador": 28
}
```

## Prof. Caio Menezes (pessimista)

- Os motores de ruído da 1ª rodada continuam registrando achados que não viram oportunidade?
- A troca de rota aumentou a produção sem perder precisão?

```json
{
 "motores_de_ruido_1a": 18,
 "ruido_agora": [
  {
   "motor": "empresas-incentivadas",
   "achados_total_1a": 24,
   "achados_total_agora": 24,
   "no_fluxo": 0,
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
   "no_fluxo": 1,
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
   "achados_total_1a": 433,
   "achados_total_agora": 433,
   "no_fluxo": 4,
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
   "achados_total_1a": 42,
   "achados_total_agora": 42,
   "no_fluxo": 9,
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
   "no_fluxo": 1,
   "confirmadas": 0
  },
  {
   "motor": "mptgo-destinacao",
   "achados_total_1a": 36,
   "achados_total_agora": 36,
   "no_fluxo": 0,
   "confirmadas": 0
  },
  {
   "motor": "f260-curadoria-009",
   "achados_total_1a": 40,
   "achados_total_agora": 40,
   "no_fluxo": 0,
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
 "pontos_com_redundancia": 9,
 "redundancia_vazia": [],
 "dominios_via_ponte": 0,
 "exemplos_da_rede_de_rotas": 112
}
```

## Dr. Otávio Lemos (neutro)

- A fatia de oportunidades achadas fora dos motores diminuiu?
- Quais domínios só os agregadores encontram e ainda não têm motor?

```json
{
 "fora_dos_motores_pct_1a": 66.1,
 "fora_dos_motores_pct_agora": 66.1,
 "origem": {
  "agregador/outra": 308,
  "motor": 202,
  "Piloto": 85
 },
 "dominios_so_de_agregador": [
  {
   "dominio": "data.queridodiario.ok.org.br",
   "oportunidades": 11
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
   "dominio": "arapongas.pr.gov.br",
   "oportunidades": 2
  },
  {
   "dominio": "fappr.pr.gov.br",
   "oportunidades": 2
  },
  {
   "dominio": "penapolis.sp.gov.br",
   "oportunidades": 1
  },
  {
   "dominio": "chamamentos.itapevi.sp.gov.br",
   "oportunidades": 1
  },
  {
   "dominio": "indaiatuba.sp.gov.br",
   "oportunidades": 1
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
 "lidos_hoje": 34,
 "nao_lidos_ontem_nem_hoje": [
  "plat-captamos",
  "plat-rede-filantropia"
 ],
 "ainda_sem_primeira_leitura": [
  "motor-gife",
  "motor-patrocinio",
  "outras-oportunidades-1",
  "outras-oportunidades-2",
  "outras-oportunidades-3",
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
 "fontes_recebidas": 125,
 "por_origem": {
  "conselho (fontes irmãs)": 120,
  "Cartório (site oficial certificado)": 5
 },
 "lidas_nas_ultimas_24h": 0,
 "dimensionamento": {
  "fontes": 125,
  "sites_por_execucao": 17,
  "execucoes_por_dia": 3,
  "sites_por_clone_por_dia": 51,
  "clones": 3,
  "cobertura_diaria": 125,
  "segundos_por_execucao": {
   "tipico": 88,
   "pior_caso": 238
  },
  "le_todas_no_dia": true
 },
 "clones_que_ja_leram": {},
 "com_achado": 0
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
   "orgaos": 40,
   "exemplos": [
    "alvoradadonorte.go.gov.br",
    "baoba.org.br",
    "brasil.aperam.com",
    "casafluminense.org.br",
    "cavalcante.go.gov.br",
    "childfundbrasil.org.br"
   ]
  },
  "Mapas Culturais": {
   "orgaos": 9,
   "exemplos": [
    "culteditais.cultura.gov.br",
    "mapa.cultura.es.gov.br",
    "mapa.cultura.gov.br",
    "mapacultural.pa.gov.br",
    "mapacultural.pe.gov.br",
    "mapacultural.se.gov.br"
   ]
  },
  "Diário municipal em lote (AGM/DOM)": {
   "orgaos": 5,
   "exemplos": [
    "diariooficial.abc.go.gov.br",
    "diariooficial.goiania.go.gov.br",
    "diariooficial.vitoria.es.gov.br",
    "dom.mossoro.rn.gov.br",
    "goiania.go.gov.br"
   ]
  },
  "Portal de transparência de fornecedor": {
   "orgaos": 14,
   "exemplos": [
    "acessoinformacao.com.br",
    "bndes.gov.br",
    "codau.com.br",
    "comunidade.transparenciainternacional.org.br",
    "mpf.mp.br",
    "saude.mg.gov.br"
   ]
  },
  "Sistemas de editais (Prosas/Editais)": {
   "orgaos": 33,
   "exemplos": [
    "adustina.ba.gov.br",
    "arapongas.pr.gov.br",
    "banrisulcultural.com.br",
    "bonde.org",
    "chamamentos.serpro.gov.br",
    "climaesociedade.org"
   ]
  }
 }
}
```
