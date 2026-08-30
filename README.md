# Eldorado + Farol de Alexandria

Sistema nacional, auditável e econômico para localizar recursos destinados a organizações da sociedade civil e transformar oportunidades verificadas em decisões, planos de trabalho e trilhas de prestação de contas.

## As duas partes

| Módulo | Função | Resultado |
|---|---|---|
| **Eldorado** | Monitora fontes públicas, privadas e plataformas de editais; deduplica; registra evidências; acompanha cinco anos de histórico por financiador | oportunidades verificadas e dossiês individualizados |
| **Farol de Alexandria** | Aplica requisitos eliminatórios, pontua aderência de cada associação, consulta leis/procedimentos e prepara pacotes de trabalho | ranking explicável, checklist, plano de trabalho e prestação de contas |

As partes usam um identificador imutável de oportunidade, mas não misturam associações. Cada perfil fica em diretório próprio. Somente o perfil institucional saneado pode ser versionado; originais, documentos pessoais e dados privados são ignorados pelo Git porque este repositório é público.

## Operação automática

- Diariamente, às **5h30 de Brasília**, uma sentinela leve compara o conjunto de candidatos de cada fonte e prioriza a fila, sem executar o Farol.
- Às **segundas e quartas, às 6h**, a varredura profunda percorre as **62 fontes catalogadas** (com `robots.txt` e intervalo entre requisições), consulta as **APIs oficiais** (PNCP e Querido Diário), roda a **camada capilar de imprensa** (pistas secundárias), a **verificação assistida**, dossiês, aprendizado, triagem e — havendo caso aberto e credencial — o **Farol IA**, do edital ao pacote do presidente.
- A **carga histórica de cinco anos é fracionada mês a mês** (domingos, 6h35) com cursor e repetição só das janelas que falharem; concluída, grava `estado/bootstrap_cinco_anos.json` e não volta a executar.
- Mensalmente, hashes das fontes jurídicas oficiais são comparados e uma revisão humana é aberta para vigência, revogação e impacto procedimental.
- Nenhum token de IA é usado em coleta, deduplicação, filtros, pontuação, aprendizado ou painel. A IA entra somente no Farol (por caso, com limites) e na exportação controlada do painel — sempre com o modelo dimensionado por tarefa em `config/ia.json`.
- O sistema **não falha em silêncio**: mais da metade das fontes falhando, três execuções sem novidade ou etapa quebrada abrem issue automática com o resumo.

## Segurança e prova

- URLs são restritas a HTTPS e a uma lista de domínios autorizados; endereços locais e privados são bloqueados.
- Cada evidência recebe SHA-256, URL, horário UTC, origem e nível de confiança.
- Conteúdo externo é sempre dado não confiável. Tentativas de prompt injection são colocadas em quarentena e nunca viram instruções.
- Requisitos sem fonte e oportunidades sem URL primária não são tratados como confirmados.
- O sistema não cria valores, prazos, beneficiários ou exigências ausentes na fonte.

## Começar

1. Abra **Actions → 00 · Verificar prontidão → Run workflow**.
2. Em **Settings → Actions → General**, permita leitura e gravação ao workflow.
3. Em **Settings → Pages**, publique a pasta `docs` da branch `main` se desejar o painel público.
4. Crie cada associação com `python scripts/criar_associacao.py SLUG "Nome"`. Cada entidade recebe diretórios exclusivos de conhecimento, documentos, editais, planos, prestações e casos do Farol.
5. `config/escopo.json` está em **amplitude máxima (27 UFs)** na fase Eldorado; a seleção fina é papel do Farol. Reduza UFs apenas para poupar tempo de varredura.
6. Para ligar a IA do Farol: **Settings → Secrets and variables → Actions → New repository secret** → `FAROL_AI_API_KEY` (chave da API Anthropic). Sem a chave, o sistema prepara os pacotes e avisa; nada é simulado.
7. Execute localmente com `python -m src.executar_diario`. O Farol é acionado só após verificação (assistida com evidência, ou humana via `scripts/promover.py`) e triagem com possibilidade moderada ou alta; reprocessamento manual em `python -m src.executar_farol`.

Para importar DOCX, imagens ou planilhas localmente, instale os componentes opcionais com `pip install -r requirements-importacao.txt`. O monitoramento normal continua usando apenas a biblioteca-padrão do Python.

## Estrutura

```text
config/                       fontes (62), escopo, APIs, capilaridade, IA e pontuação
catalogo_captacao/            260 pistas do anexo por nível e tipo (+ cobertura em estado/)
src/                          coleta, APIs, capilaridade, verificação, matching, IA, aprendizado e painel
dados/oportunidades/          banco JSONL deduplicado por URL canônica (+ pistas_imprensa.jsonl)
dados/financiadores/          dossiê + aprendizado/previsão por financiador
dados/associacoes/            isolamento estrito por associação (casos, submissão, presidente)
dados/doadores/               empresas e fundações doadoras separadas
biblioteca/leis/              catálogo jurídico com vigência (26 normas: MROSC, Rouanet, Pelé, LC 222/2025, PNAB, LPG, Goyazes…)
biblioteca/procedimentos/     procedimentos e checklists reutilizáveis
biblioteca/modelos/           modelos versionados
acervo_importado/             índice verificável do anexo fornecido
docs/                         painel estático e dados filtráveis
estado/                       hashes, cursores, previsões, alertas e auditoria
```

## Trilha de busca cirúrgica

1. O acervo fornece pistas de programas e formas de captação, sem convertê-las automaticamente em fatos atuais.
2. `config/fontes.json` funciona como lista de permissão: o coletor não segue links para domínios não catalogados. A busca histórica usa `site:dominio_oficial` e também descarta o resultado se o host não coincidir.
3. `config/escopo.json` elimina UFs, municípios e áreas antes de qualquer requisição, economizando banda e tokens.
4. Portais públicos são coletados automaticamente; Goodstack e UN Partner Portal ficam como portais autenticados e não são raspados.
5. Duas camadas oficiais de capilaridade nacional complementam a varredura: **PNCP** (credenciamentos e concursos de todos os entes) e **Querido Diário** (busca textual nos diários oficiais municipais). A camada de imprensa (`config/capilaridade.json`) gera pistas secundárias descentralizadas por termo × UF × emissor — que só viram oportunidade com a URL oficial confirmada.
6. Uma oportunidade só segue ao Farol quando `verificada_primaria` ou `verificada_dupla` — pela verificação assistida (evidência hasheada e auditada) ou por `scripts/promover.py`.

O dashboard permite filtrar por UF, nível e área, baixar um novo `escopo.json` e exportar um pacote JSON mínimo para ChatGPT ou Claude.

## Conselho independente do Farol

Cada caso elegível recebe sete pacotes separados, dos pontos de vista extremamente pessimista ao extremamente otimista. As personalidades brasileiras (pool de 14, áreas correlatas) são sorteadas entre lentes relevantes e não repetem a mesma posição na rodada seguinte. São simulações metodológicas, não opiniões reais.

O parecer final permanece bloqueado até existirem sete respostas JSON válidas e usa o **modelo mais avançado configurado** (`config/ia.json`, env sobrepõe). O resultado indica, lente a lente, **ponto de vista, personalidade, vantagens e desvantagens**, e o filtro final ou explica por que a associação não teria chances, ou entrega em `submissao/` os **documentos prontos** — em nome da entidade, sem referência a IA e sem pendências; orientações, prazos e assinaturas ficam no `07_pacote_presidente.md`, objetivos e resumidos. Bloqueio eliminatório evidente dispensa o conselho (economia). Sem credencial autorizada, o sistema prepara os pacotes e diz isso com clareza — nunca simula que uma IA foi executada.

## Associação inicial

`dados/associacoes/amc-jardim-america/` contém o perfil público sanitizado da A.M.C., capacidades, indicadores, projetos/eventos e o índice compacto do DOCX anexado. O arquivo original tem dados pessoais e 17 imagens; por segurança, foram publicados apenas texto e tabelas compactados com PII removida e manifestos de hash das imagens.

Consulte também [ARQUITETURA.md](ARQUITETURA.md), [SEGURANCA.md](SEGURANCA.md) e [OPERACAO.md](OPERACAO.md).
