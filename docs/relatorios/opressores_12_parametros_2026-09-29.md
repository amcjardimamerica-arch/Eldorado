# Motores opressores — os 12 parâmetros de cada edital (29/09/2026)

## O que foi feito

Os **329 opressores ligados** foram divididos em **10 blocos temáticos**. Cada um foi pesquisado na fonte oficial para obter os 12 parâmetros do edital vigente ou, quando não havia edital aberto, os da última edição, que vão para o histórico e servem para prever a próxima.

Os 12 parâmetros são: objeto, prazo de inscrição, resultado, prazo de recurso, valor, órgão/financiador, território, esfera, requisitos, anexos, destinação e área de atuação.

Quando o próprio recurso não tem algum desses parâmetros, a **dispensa** ficou registrada com o motivo. Exemplos: fluxo contínuo, destinação de IR, cadastro do MP, emenda parlamentar, prêmio sem recurso.

A pesquisa foi feita de três formas:

- **Nuvem:** 10 pesquisadores em paralelo, um por bloco.
- **Navegador do seu computador:** usado para os sites que bloqueiam a nuvem (MPGO, Prêmio LED, Impactarte, Unibanco, Ambev) e para os PDFs do próprio órgão anexados ao PNCP (Vera Cruz/RS e Adustina/BA).
- **Reaproveitamento:** 92 opressores já tinham sido verificados item a item em 27 e 29/09.

**Regras seguidas:**

- A fonte é sempre o site oficial do órgão ou do patrocinador, ou o arquivo do próprio órgão anexado ao PNCP, com a origem declarada.
- Nenhuma data ou valor estimado. Sem fonte oficial, o campo ficou `null` com o status "não localizado".
- Todos os PDFs foram checados contra prompt injection. **Nenhuma injeção foi encontrada.**

## Resultado geral

| Decisão | Qtd. | O que acontece no sistema |
|---|---:|---|
| **V** — edital vigente aberto | 53 | Os 12 parâmetros entram no opressor; a IA não pergunta de novo o que já está fechado |
| **A** — última edição encerrada | 66 | Os 12 parâmetros da edição ficam no histórico e alimentam a previsão |
| **R** — programa permanente, sem edital periódico | 37 | Regramento oficial com as dispensas registradas (IR a fundos, Rouanet, LIE, MPGO/MPT, emendas ALEGO, doação da Receita) |
| **D** — não é recurso para OSC | 94 | O opressor é desligado e **não volta a ser ligado automaticamente** |
| **P** — pendente | 79 | O motivo fica registrado; a busca continua nos itens "não localizado" |

Parâmetros levantados: **1.483 confirmados**, **106 dispensados pelo edital**, **72 "não informado no edital"** e **211 "não localizado"**.

**No sistema, depois da aplicação:**

| Situação | Antes | Depois |
|---|---:|---:|
| Opressores ligados | 329 | 235 (94 desligados como não-recurso) |
| Opressores com os 12 fechados | 10 | 98 |
| Opressores com nenhum parâmetro | 299 | 80 (os pendentes) |

## Os 10 blocos

| # | Bloco | Opressores | V | A | R | D | P | 12/12 fechados | Página do motor corrigida |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Goiás — governo estadual | 27 | 4 | 11 | 2 | 9 | 1 | 15 | 15 |
| 2 | Goiânia e ALEGO (emendas estaduais) | 28 | 0 | 5 | 18 | 4 | 1 | 22 | 25 |
| 3 | Programas federais | 29 | 8 | 6 | 9 | 6 | 0 | 16 | 16 |
| 4 | Destinação judicial, MP, emendas e agregadores | 18 | 2 | 0 | 5 | 11 | 0 | 4 | 6 |
| 5 | Fundações, institutos, empresas e internacionais | 45 | 7 | 17 | 3 | 13 | 5 | 15 | 22 |
| 6 | Diários oficiais — Sudeste e Sul | 49 | 2 | 9 | 0 | 5 | 33 | 5 | 41 |
| 7 | Diários oficiais — Nordeste, Norte e Centro-Oeste | 35 | 2 | 8 | 0 | 2 | 23 | 5 | 33 |
| 8 | Repositório — cultura e PNAB municipais | 21 | 10 | 1 | 0 | 5 | 5 | 5 | 11 |
| 9 | Repositório — chamamentos de OSC | 20 | 10 | 4 | 0 | 3 | 3 | 7 | 15 |
| 10 | Repositório — demais oportunidades | 57 | 8 | 5 | 0 | 36 | 8 | 4 | 14 |

A coluna "página do motor corrigida" conta os casos em que a pesquisa indicou uma página oficial diferente da que o motor monitorava. Exemplos:

- programa estadual apontando para o Conanda federal;
- o próprio Programa Goyazes apontando para o Conanda;
- item de diário apontando para PDF de outro município.

A página correta ficou em `pagina_oficial_verificada`. O endereço original do motor não foi apagado.

## Prazos abertos — Goiás, Goiânia e nacionais

| Prazo | Oportunidade | Bloco |
|---|---|---|
| **29/09 (hoje)** | Prêmio Nacional Enap/MDHC — crianças e adolescentes em situação de rua | 3 |
| **29/09 (hoje)** | Alvorada do Norte/GO — PNAB 006/2026 (Virada Cultural, R$ 50 mil) | 8 |
| 11/10 | Conanda/SNDCA — Edital 01/2026 (SGDCA/Sinase), prorrogado, pelo Transferegov | 4 |
| 13/10 | Goiatuba/GO — PNAB 004/2026 (inscrições a partir de 01/10) | 8 |
| 13/10 | MinC — Rouanet nas Favelas 2 (Edital 6/2026) — **Goiânia não está entre as 8 capitais atendidas** | 10 |
| 16/10 | SEDS-GO — Socioeducativo (termo de colaboração) | 1 |
| 19/10 | Zurich — Leis de Incentivo 2026 | 5 |
| 29/10 | Secult-GO — Ocupa Goiás: Brasilidades & Futuros 2027 (R$ 1 milhão) | 1 |
| 30/10 | Fundação Maria Emília — FME Transforma | 5 |
| 09/11 | Equatorial — CPP 001/2026 (edital de Goiás na versão 2) | 5 |
| 04/12 | BNDES Periferias em Rede — 6º ciclo | 3 |
| Contínuo | SEDS-GO — Credenciamento 001/2026 (Auxílio Nutricional e Água/Energia) | 1 |
| Contínuo | MPT-GO (PRT-18) — editais de destinação | 4 |
| Contínuo | MPGO — cadastro DAAMP (Edital 02/2024 do COMPOR, vigente até novo ato) | 4 |
| Contínuo | Planaltina/GO — Chamamento 06/2026 (Esporte e Lazer) | 10 |
| Contínuo | iCS, Instituto ACP e Impactarte — propostas e cadastros em fluxo contínuo | 5/9 |

Os demais editais abertos são de municípios fora da abrangência aprovada (CE, BA, RS, SP, PR, PE, MA, RN e ES) e de programas privados regionais (FUNBIO Paraná, Bondinho Pão de Açúcar, Fundação Aperam). Estão todos no arquivo de dados com os 12 parâmetros.

## O que a pesquisa revelou sobre os motores

1. **Um terço dos opressores ligados não era recurso (94 de 329).** Os casos foram:
   - agregadores tratados como programa: Prosas, Bússola, Capta, GIFE Mosaico, Mapa das OSC, CapitaAí e vagas.terceirosetor;
   - "histórias de sucesso" de blog;
   - bolsas de pesquisa para pessoa física: FAPEG e universidades estrangeiras;
   - rótulos genéricos sem programa por trás, como "Projeto de biblioteca comunitária" ligado ao Conanda;
   - fundações que declaram oficialmente não abrir editais a OSC externas: Vale, Bradesco, Votorantim, Sicoob, Claro e Ford.

   Agora esses opressores são desligados e não voltam.
   > **Decisão sua:** se quiser continuar acompanhando alguma dessas fundações por relacionamento, é só pedir para religar.
2. **Os opressores de diário oficial são os mais difíceis (56 dos 79 pendentes).** O diário mostra o extrato, mas a prefeitura não publica o edital no site, ou o site bloqueia leitura automática (portais atende.net, sites com robots.txt, certificado inválido).
   - O PNCP do próprio órgão resolveu alguns casos (Vera Cruz/RS e Adustina/BA). A maioria das prefeituras pequenas não anexa o chamamento de OSC no PNCP.
   - Todos esses pendentes são de fora da abrangência. **Não há pendente de diário em Goiás**, com uma exceção: o "Natal no Parque" de Goiânia, que só aparece no Diário Oficial e não tem página própria no portal da Prefeitura.
3. **Os programas permanentes estavam sem regramento (37).** Destinação de IR a fundos, Lei Rouanet, LIE, doação da Receita, MPGO/MPT e emendas da ALEGO agora têm os 12 parâmetros com as dispensas explicadas. Assim a IA dos disjuntores não gasta mais tentativas procurando "prazo de inscrição" onde ele não existe.
4. **Páginas erradas:** 198 opressores monitoravam uma página que não era a do recurso. A página verificada ficou registrada.

## Pendentes que valem sua atenção

| Opressor | Por que ficou pendente |
|---|---|
| Goiânia — "Natal no Parque" (Edital 001/2026, R$ 5 mi segundo o Diário) | Não publicado no portal da Prefeitura nem no PNCP; vale confirmar direto com a Secretaria de Gestão de Negócios e Parcerias |
| Fundo Municipal do Idoso de Goiânia | O motor estava ligado a dados de outro município (Vilhena/RO); falta a página oficial do Conselho Municipal do Idoso |
| Ambev Brasilidades 2026 (prazo 30/09 segundo agregadores) | O site da Ambev, aberto pelo seu navegador, não publica o edital; não confirmado |
| Secult-GO — Arranjos Regionais do Audiovisual 2026 (R$ 30 mi, FSA) | Só o Plano de Ação foi publicado; os editais ainda não saíram |
| Instituto Unibanco | A página oficial de editais não lista edição vigente |
| Instituto Coca-Cola, Sabin, Instituto Porto, Fundo BIS | Sites fora do ar, com certificado inválido ou sem chamada identificável |

## Conselho das 7 lentes

- **Extremamente pessimista:** 79 opressores seguem sem os 12 parâmetros, e 56 deles dependem de prefeituras que não publicam o edital. O motor de diários continua trazendo trabalho que ninguém consegue confirmar.
- **Pessimista:** desligar 94 opressores de uma vez pode apagar uma fundação que abra edital no ano que vem. Vale, Votorantim e Bradesco mudam de política.
- **Levemente pessimista:** os parâmetros vieram do edital lido hoje. Uma retificação amanhã deixa o dado velho, e o sistema precisa reler as páginas dos V.
- **Neutro (decisor):** o ganho é real. Os opressores com os 12 fechados passaram de 10 para 98, e o custo de IA caiu, porque 94 opressores inúteis saíram e 37 permanentes já não perguntam o que não existe. As proteções são quatro:
  - dispensa não é eterna: basta o titular religar;
  - todo V tem a fonte oficial gravada para reverificação;
  - "não localizado" continua sendo buscado;
  - pendente de diário fora da abrangência não bloqueia nada.

  O **critério de qualidade** é este: todo parâmetro confirmado tem valor e fonte oficial, e nenhuma data sem fonte. Isso está verificado por teste automático.
- **Levemente otimista:** as 198 páginas corrigidas fazem os motores acharem a próxima edição direto na fonte, sem depender de agregador.
- **Otimista:** as 66 edições encerradas, com parâmetros completos, dão ao preditivo datas reais de abertura e de resultado para projetar 2027.
- **Extremamente otimista:** para Goiás e Goiânia, o sistema passa a ter o regramento completo de todos os canais permanentes: MPGO, MPT, emendas ALEGO, FECAD, Goyazes e FAC. É a base para um calendário anual de captação da associação.

## Como entra no sistema

- **Dados da pesquisa:** `dados/opressores/parametros/parametros_2026-09-29.json`, com um registro por opressor e os 12 parâmetros com status, fonte, edição de referência, página verificada e recomendação ao motor.
- **Aplicação:** `src/parametros_opressores.py`. É idempotente e roda sozinha em três momentos:
  - no fluxo completo das oportunidades;
  - na rotina diária dos disjuntores;
  - na geração do catálogo, com o campo `parametros` em cada motor e o resumo "V · 12/12 · prazo" no painel.
- Os opressores com decisão D não são religados, nem pela ativação automática nem pelo repositório.
- **Testes:** 9 testes novos, que passam. A suíte completa tem as mesmas 41 falhas que já existem no `main`, sem nenhuma nova. A checagem de privacidade passou.
