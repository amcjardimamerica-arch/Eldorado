# Itens-âncora do Motor 12 (critério de aceite)

Cada item abaixo é real. Todos foram vistos em 02/10/2026 na fonte oficial.

Para ser aceito, o motor implantado precisa:

- **reencontrar os itens nos testes sem rede** (fixtures com o HTML ou o texto destes itens);
- **reencontrá-los na primeira coleta real**;
- tirar deles os campos indicados;
- dar a eles a classificação esperada.

| # | Órgão | Item | Campos esperados | Classificação esperada |
|---|---|---|---|---|
| 1 | MPT-GO | **Edital 009220.2026**, PTM Anápolis, publicado em **01/10/2026** | procedimento `000037.2019.18.003-6`; valor **R$ 94.428,74** (ExTAC 0010025-57.2019.5.18.0171); prazo de 5 dias; exige cadastro prévio (Edital PRT18 24/2025) | OPORTUNIDADE, com data-limite segura de 05/10/2026 |
| 2 | MPT-GO | **Edital 008314.2026**, PTM Anápolis, publicado em **24/08/2026** | valor **R$ 2.141.800,00**; procedimento `000545.2021.18.000-2` | ACOMPANHAR (encerrado) |
| 3 | MPT-GO | **Edital 067008.2026**, Goiânia (sede), publicado em **06/08/2026** | procedimento `002360.2025.18.000-7`; valor **R$ 40.746,65** | ACOMPANHAR (encerrado) |
| 4 | MP-GO | **Destina: Edital de Chamamento nº 02/2024** (COMPOR / DAAMP) | fluxo contínuo; Atos PGJ 77/2022, 25/2024 e 58/2025; prestação de contas em 30 dias | OPORTUNIDADE (regra permanente, verificação manual) |
| 5 | MPF | **PR-GO: cadastro de entidades e órgãos para bens e valores**, notícia de **09/10/2025** | bienal (Portaria PGR/MPF 1.097/2024); inscrição pelo protocolo eletrônico | ACOMPANHAR (link do edital 404) |

## Links

**1 a 3 (listagem):** https://www.prt18.mpt.mp.br/servicos/editais-de-destinacao-de-recursos-bens

Os PDFs são baixados pelo botão da linha. O endereço tem a forma `?task=baixa&format=raw&arq=<token>`.

Tokens vistos em 02/10/2026:

- **1:** `zpEKILyO3R97KvSesbLpuWw4KHWh2SJL0ruqCot_iOuRgdlg-LT6Fr8seXnxFt4gMqcBnqKv_M84ydbrHtBrj4I5WKdz8TTLAPymQAH4yrNBlvfMj5kJqfQK-XKShmle`
- **3:** `zpEKILyO3R97KvSesbLpuWw4KHWh2SJL0ruqCot_iOta2vxxuIZeQ9wS1CPuPpj0VRIloqNP_8PyEkkAgMQCdoI5WKdz8TTLAPymQAH4yrNBlvfMj5kJqfQK-XKShmle`

O token pode mudar. **Não o use como identidade do registro.**

**4:** https://www.mpgo.mp.br/portal/conteudo/destina-destinacao-articulada-de-acordos-edital-n-02-2024

O robots.txt proíbe robôs. Por isso este item entra como **regra fixa** no catálogo, e não como coleta.

**5:** https://www.mpf.mp.br/o-mpf/unidades/pr-go/noticias/mpf-em-goias-cadastra-entidades-e-orgaos-publicos-para-recebimento-bens-e-valores-decorrentes-da-atuacao-da-instituicao

## Chave natural para deduplicar

`orgao | unidade | numero_edital | procedimento`

Exemplo: `MPT-GO|PTM Anápolis|009220.2026|000037.2019.18.003-6`.

## Teste negativo, que tem de dar RUÍDO

| Item | Por que é ruído |
|---|---|
| "MPDFT obtém destinação de mais de R$ 12 milhões para o Fundo de Modernização da PCDF" (25/09/2026) | O destino é um fundo público |
| "Edital de Notificação nº 1", MPM Manaus (14/09/2026) | É notificação processual |
| Edital FDD NAS 2023 | É restrito a entes públicos |
