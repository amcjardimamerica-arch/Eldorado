# Operação

## Comandos

```bash
python -m src.executar_diario            # varredura completa (o que roda seg/qua)
python -m src.sentinela                  # checagem diária leve
python -m src.executar_farol             # reprocessar triagem/casos/ranking + Farol IA
python -m src.retrospectivo              # carga histórica (janelas mensais pendentes)
python -m src.resumo_execucao            # resumo humano + decisão de alerta
python -m unittest discover -s tests -v
python scripts/promover.py listar capturada
python scripts/promover.py ID verificada_primaria --por "Nome" --nota "conferido na fonte"
python scripts/confirmar_pista.py PISTA_ID https://dominio-oficial/edital --por "Nome"
python scripts/cobertura_catalogo.py     # abrangência das camadas sobre os 260 pontos
python scripts/importar_acervo.py entrada_acervo
python scripts/importar_catalogo_captacao.py planilha.xlsx
python scripts/criar_associacao.py SLUG "Nome da associação"
python scripts/ingestao_associacao.py SLUG documento.docx
```

## Estados de uma oportunidade

`pista_do_acervo_pendente_url_primaria` / `pista_imprensa` → `capturada` → `verificada_primaria` ou `verificada_dupla` → `elegivel` ou `inelegivel` → `em_preparacao` → `submetida` → `selecionada` ou `nao_selecionada` → `em_execucao` → `prestacao_de_contas` → `encerrada`.

**Quem verifica:** a verificação assistida (sem IA) promove `capturada → verificada_primaria` quando abre a URL primária em fonte catalogada, encontra termos de edital e não há padrão de injeção — com evidência hasheada e auditoria. O humano continua soberano via `scripts/promover.py` (promove, rebaixa ou descarta; status definidos por humano nunca são rebaixados pela máquina).

## O caso no Farol (por associação, universo isolado)

```text
farol/casos/<oportunidade>/
  01_enquadramento.json                triagem inicial
  01b_enquadramento_com_requisitos.json portão com requisitos reais do edital
  02_plano_trabalho.md                 rascunho editável (nunca sobrescrito)
  03_manual_presidente.md              manual geral (nunca sobrescrito)
  04_documentos_necessarios.md         checklist
  05_prestacao_contas.md               matriz
  conselho/01..07_*/entrada.json       pacotes isolados das 7 lentes
  conselho/01..07_*/resposta.json      respostas (IA ou fila externa)
  06_parecer_conselho.md               ponto de vista + personalidade + vantagens/desvantagens
  07_pacote_presidente.md              decisão, prazos, pendências e orientações OBJETIVAS
  submissao/                           documentos finais limpos (sem IA, sem placeholders)
  rascunhos/                           o que ainda tem pendência, com os motivos
```

Sem credencial de IA (`FAROL_AI_API_KEY` em Actions Secrets), o sistema prepara os pacotes e para aí, dizendo isso com clareza — nunca finge parecer. Com credencial, o fluxo segue automático dentro dos limites de `config/ia.json` (casos por execução, tamanhos, modelos por tarefa).

## Dossiê e aprendizado do financiador

O diretório individual reúne eventos comprovados, valor quando publicado, objeto, forma de acesso, requisitos recorrentes e links. “Padrão” só é promovido após **duas ocorrências validadas**; antes disso aparece como hipótese. `aprendizado.json` traz também a **previsão de janela** (mesmo mês em 2+ anos) para preparar a entidade ANTES da abertura; o consolidado fica em `estado/previsoes.json`.

## Plano de trabalho e prestação de contas

O Farol gera checklist a partir do edital e do procedimento aplicável. A redação final preserva a estrutura exigida pela fonte, com indicadores mensuráveis, cronograma, memória de cálculo, riscos e plano de evidências. A prestação de contas nasce junto com o plano: cada meta define desde o início qual documento provará sua entrega. Documentos em `submissao/` saem em nome da entidade, prontos para conferência e assinatura da diretoria; tudo que é orientação vai ao pacote do presidente.

## Conformidade, prazos e HTML por edital

Toda análise de oportunidade viva produz HTML. A cada varredura profunda:

1. `src/qualidade.py` mede cada registro contra `config/padroes_edital.json` — conteúdo mínimo
   do chamamento público (base: Lei 13.019/2014, art. 24, §1º) e sinais de oficialidade do ato.
   Nota de 0 a 100 e classe (`completo`, `suficiente`, `insuficiente`, `apenas_indicio`, `reprovado`).
   O que a fonte não disse vira **pendência declarada**, nunca preenchimento automático.
2. `src/prazos.py` converte o prazo textual em dias corridos restantes, classifica a urgência
   (30/15/7/3/1 dias) e grava `estado/alerta_prazos.json`; o workflow abre issue com rótulo `prazo`.
3. `src/fichas.py` grava `docs/editais/<id>.html` — uma ficha por edital com dados, fonte, URL primária,
   evidência com hash, prazo, conformidade item a item e o aprendizado acumulado do financiador.
4. `src/relatorio_amplitude.py` gera `docs/relatorio-amplitude.html` a partir da configuração viva:
   canais de busca, uso de tokens por etapa, testes e padrões exigidos. Nenhum número é escrito à mão.

Comandos:

```bash
python -m src.qualidade
python -m src.prazos
python -m src.fichas
python -m src.relatorio_amplitude
```

## Carga histórica de cinco anos — campanha única

Levantamento **único**, para formar o padrão do repositório (requisitos, parâmetros, janelas de
publicação e condições de cumprimento). Percorre 5 anos fracionados **mês a mês**, em ordem
cronológica, um mês após o outro, do mais antigo ao mais recente, sobre PNCP e Querido Diário,
mais uma camada anual por `site:domínio_oficial` dos financiadores catalogados.

- O cursor `estado/cursor_carga_historica.json` registra cada janela concluída; janela que falha é
  repetida na execução seguinte, então nenhum mês fica sem varredura.
- O workflow roda de 6 em 6 horas **apenas enquanto houver janela pendente**. Ao concluir todas,
  grava `estado/bootstrap_cinco_anos.json` e passa a encerrar imediatamente — nunca mais consome tempo.
- Esta etapa **não gera HTML**: é levantamento de padrão, não análise de oportunidade viva.
  Ela alimenta `src/aprendizado.py`, que é quem transforma histórico em previsão de janelas.

## Formas de divulgação e rota dos 260 pontos

`config/canais_divulgacao.json` lista as 18 formas pelas quais um ponto de captação
torna público que há dinheiro disponível, e qual camada do sistema captura cada uma.

O princípio é o modelo primário de rastreio de dinheiro público: **onde há recurso
público, há ato administrativo; onde há ato administrativo, há publicação obrigatória.**
A publicação é o ponto de captura — não o anúncio, não a notícia, não o post.

`src/rota_monitoramento.py` aplica isso ponto a ponto: lê o campo de origem do acervo,
identifica a forma de divulgação (resolução de conselho, edital do MP, destinação
judicial, emenda, incentivo fiscal, diário oficial…) e atribui a camada correspondente
mais as rotas de reforço. Quando o texto não permite identificar a forma, entra a
**rota-piso do nível federativo**: DOU para federal, diário estadual para estadual,
diário municipal para municipal. Resultado em `estado/rotas_monitoramento.json`.

```bash
python -m src.rota_monitoramento
python scripts/cobertura_catalogo.py
```

## Região Metropolitana de Goiânia

`src/rmg_diarios.py` cobre os 21 municípios pelo diário oficial, com consultas
específicas para conselhos e fundos. Em município pequeno raramente existe página de
editais; o que existe é o diário. O código IBGE de cada município é **resolvido em
execução** pelo endpoint público de cidades e cacheado em `estado/territorios_rmg.json` —
nenhum código é escrito de memória. Município não resolvido vira pendência declarada e
continua coberto por PNCP e varredura de site.

## Redes sociais sem acesso direto

`src/redes_indireta.py` usa quatro rotas, em ordem de confiabilidade:

1. **Espelho oficial no site do órgão** — a mais confiável, já coberta pela varredura HTML.
2. **Indexação por buscador** — ativa; devolve título e trecho textual do post, não a imagem.
3. **oEmbed público** — desligada; enriquece pista cuja URL já se conhece, não descobre post novo.
4. **API oficial com credencial** — desligada até haver segredo; única rota com a imagem disponível.

Sobre ler o texto impresso na imagem do post: o OCR exige primeiro obter o arquivo da
imagem, e obter o arquivo exige o acesso direto que estas rotas não têm. O gancho está
declarado em `config/redes_indireta.json` → `ocr_quando_houver_credencial` e só se torna
executável pela rota 4. Mesmo com OCR, o resultado continua **pista**: card de divulgação
não é edital.

## Relatório da varredura — segundas e quartas

`src/relatorio_busca.py` grava `docs/relatorios/<data>.html` ao fim de cada varredura,
com histórico navegável em `docs/relatorios/index.html`. Três partes:

**1. Editais abertos no período.** Uma caixa por edital. Quando o mesmo programa publica
vários editais — a PNAB/Aldir Blanc é o caso típico — cada um aparece individualizado, com
nome da lei de regência, modalidade (objeto ou atividade a executar) e a contagem de prazo
de início e fim. `src/programas.py` faz o reconhecimento por termo literal; o que não casa
fica como "programa não identificado", com a lacuna declarada.

**2. Calendário do ano.** Doze meses com abertura e encerramento de cada edital, mais os
programas de fluxo contínuo (Rouanet, LIE, Goyazes — habilitação por lote, sem data única
de encerramento) e a janela de emendas parlamentares destacada em outubro e novembro.

**3. Emendas parlamentares.** Área que **só abre em outubro e novembro**. Fora da janela,
exibe apenas a data de reabertura. Lista parlamentares com mandato no ano, gabinete,
resultado eleitoral e bandeiras medidas por atuação registrada (proposições e comissões),
não por opinião atribuída. Tema com uma só ocorrência é ruído e não vira bandeira.

```bash
python -m src.relatorio_busca
python -m src.relatorio_busca --forcar   # consulta fora da janela, marcada como tal
python -m src.parlamentares              # carga oficial; roda no workflow só em out/nov
```

### Emendas não acionam o Farol

Trava em `src/triagem.py`: oportunidade cujo programa é emenda parlamentar, ou cuja forma de
divulgação é `emenda_parlamentar`, nunca abre caso nem gera plano de trabalho automaticamente.
A triagem devolve `somente_informativo`. Emenda depende de articulação e viabilidade política —
o sistema informa e direciona; o plano só é produzido mediante solicitação expressa.

### Dados de parlamentares

Nenhum nome, partido, gabinete, votação ou bandeira é escrito de memória. Federal vem da API
de dados abertos da Câmara. ALEGO, Câmara de Goiânia e resultado eleitoral do TSE estão
declarados como **pendência**, com o link oficial para consulta humana — sem carga, a área
mostra a pendência em vez de dado que pareça verdadeiro.

## Dashboard — Eldorado e Farol de Alexandria

`docs/dashboard.html` — painel único, alimentado às **segundas e sextas** pela varredura,
e **mensalmente** pela revisão de leis (dia 1º) e pelo compilado de dados históricos
(`dados/compilados/AAAA-MM.json`).

Estrutura: dois botões no centro superior — **Eldorado** e **Farol de Alexandria**.
- Eldorado → **Calendário** (mês navegável; ícone por dia, cor = área do edital, símbolo =
  tipo de evento: abertura ▲, encerramento ■, resultado preliminar ◐, final ●, prorrogação ⟳,
  retificação ✎, recurso §; prorrogações atualizam a data e mostram a original),
  **Editais Abertos** (caixas com resumo; clique abre protocolo, qualificação, pontuação,
  requisitos e documentos — lacunas declaradas) e **Bússola** (quadros lineares dos dias do
  mês: houve busca? validou? clique traz o detalhe da auditoria; fontes com edital aberto em
  caixas próprias com links e anexos; legenda de cor por tipo de fonte).
- Farol → **Documentos** (posteriormente), **Editais Abertos** e **Biblioteca** (26 normas).
- Tudo tem resumo ao passar o mouse e detalhe ao clicar.
- Resultados/prorrogações/recursos são buscados ativamente (`src/resultados.py`).

### Acesso restrito

- Dados publicados **cifrados** (AES-256-GCM; chave por PBKDF2-SHA256, 200k iterações).
  Sem a senha, o arquivo no ar é ilegível — esta é a proteção real.
- **Senha do mês** AMC-XXXX-XXXX, derivada de `ACESSO_MASTER` (Secret) + mês corrente:
  troca sozinha todo dia 1º e a anterior deixa de abrir qualquer coisa (expiração automática
  no último dia do mês). Sessão local vale até o fim do mês.
- Envio automático por **WhatsApp** no dia 1º (workflow `acesso-mensal`); **reenvio /
  recuperação**: Actions → acesso-mensal → *Run workflow* (registra motivo em auditoria).
  Trocar o número = atualizar o Secret `WHATSAPP_PHONE`.
- Bloqueio de **celular** e verificação de **localização Goiânia** por IP no navegador —
  barreiras dissuasórias (contornáveis por técnico); a criptografia é o cadeado.
- Secrets necessários: `ACESSO_MASTER` (frase longa aleatória), `WHATSAPP_PHONE`
  (com DDI, ex.: 5562...), `CALLMEBOT_APIKEY` (obtida no primeiro contato com o robô do
  CallMeBot). Sem eles, o painel publica sem cifragem e declara a pendência.

