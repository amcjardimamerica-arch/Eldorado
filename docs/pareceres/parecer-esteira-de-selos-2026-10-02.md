# Parecer — Esteira metódica de selos conduzida pela rede neural (02/10/2026)

**Conselho técnico** (chief engineer, staff engineer, CTO e professores de computação, Python) · **Associação de referência:** A.M.C. Jardim América

## 1. O pedido, organizado

0. **Maestro (rede neural)** planeja o dia, controla os motores e só fecha o dia com a busca 100% feita. 1. **Resultado**: a oportunidade completa/atualiza um livro ou cria um novo. 2. **Bronze**: confirmar o site oficial — Interceptador no computador do titular, Sonnet 5.5 (esforço baixo), até 2 reprocessamentos; sem sucesso → Estante de Investigação Bronze. 3. **Prata**: Opus 5.5 (esforço baixo) valida edital, prazos e 12 dados (ou dispensas); sem validação → Estante de Investigação Prata. 4. **Ouro**: pronto para o Farol. Aprendizado de cada etapa gravado no livro.

## 2. O que foi construído

| Peça | Arquivo | O que faz |
|---|---|---|
| Maestro | `src/maestro.py` (no fluxo de status, 4×/dia) | plano do dia por prioridade (rendimento real do canal, diagnóstico, livros com abertura próxima); cobertura de cada motor (completa · parcial · pendente · aguardando horário · pendente local); dispara de novo parciais e atrasados até 3×/dia; registra o fechamento do dia |
| Esteira | `src/esteira.py` + `config/esteira.json` (no ciclo, depois da rede neural) | selo e estante de cada livro; filas ordenadas pela nota da rede e pelo prazo; aplica os resultados do computador do titular; grava aprendizado; informação nova reabre a estante |
| Interceptador local | `scripts/interceptador_local.py` (dentro de `coleta_brasil`) | bronze: Sonnet 5.5 + busca/leitura na web, conferência no IP do titular; prata: Opus 5.5 lê página e PDF do edital; **o código valida** (prazo + 12 dados/dispensas) |
| Adaptador de IA | `src/ia.py` | esforço (`output_config.effort`) e ferramentas `web_search_20260318`/`web_fetch_20260318` — conferidos no SDK oficial `anthropic` 1.11.0; retoma pausas da busca; registra uso em `estado/ia_uso.jsonl` |
| Painel | `docs/dashboard.html` | selo no cartão, filtro de selos e estantes, seção "Esteira de selos" no livro |

## 3. Problema grave encontrado e corrigido no caminho

O fluxo de produção **rodava a suíte de testes sobre os dados reais** e depois gravava tudo; um teste do resgate do Piloto criava **fichas falsas** (página `x.gov.br`, prazo 2099, valor "R$ 100 mil") — 11 fichas, 7 entradas de histórico, 3 livros, 2 extrações e 1 item de validação contaminados desde 29/09. Correção: testes da produção numa cópia isolada (`git worktree`); o arquivo de teste não grava mais fora da pasta temporária; limpeza feita; **guarda permanente** (`src/guarda_dados_teste.py`) a cada ciclo.

## 4. Primeira avaliação com os dados reais

Bronze **209** · Prata **769** · Ouro **11** (livros fora da esteira: fontes de busca e qualificados "não aplica"). A prata é grande porque "Resultado" e "Prazo de recurso" faltam em quase todos: a dispensa só conta quando validada pela leitura do edital (Opus) — a matriz de dispensas prováveis **não** promove sozinha, de propósito.

## 5. Conselho de 7 lentes

1. **Extremamente pessimista:** "Com 15 pratas por dia, a fila de 769 leva mais de 50 dias; e a fila depende de o computador do titular estar ligado."
2. **Pessimista:** "O modelo pode apontar site plausível e errado; a conferência por termos do programa no texto é fraca para nomes genéricos."
3. **Levemente pessimista:** "Sem a credencial no computador, a esteira para no bronze — o sistema avisa, mas não avança."
4. **Neutro:** pondera abaixo.
5. **Levemente otimista:** "O IP do titular resolve o bloqueio que derrubava o Interceptador; a busca do modelo acha o oficial onde o robô não chega."
6. **Otimista:** "O código valida a prata — o modelo extrai, não decide. O aprendizado gravado no livro torna cada nova tentativa mais curta."
7. **Extremamente otimista:** "Com o maestro, nenhum dia fecha parcial; com a esteira, o Farol só recebe ouro."

**Síntese do neutro — parâmetros e mitigação:** limites diários configuráveis (`config/esteira.json`: 40 bronze, 15 prata) e uso auditado; a nota da rede ordena as filas (o que mais provavelmente é real e vence antes vai primeiro); confirmação do site sempre no IP do titular; validação da prata pelo código; reabertura automática com informação nova; sem credencial nada é simulado. **Ajuste recomendado:** subir o limite da prata quando o custo observado em `estado/ia_uso.jsonl` for conhecido.

## 6. Para funcionar

1. No computador do titular, definir a variável de ambiente **`FAROL_AI_API_KEY`** (chave da API) e rodar a coleta local como hoje (`coleta_brasil.bat`). Ter o **`pdftotext`** (Poppler) instalado para ler PDFs.
2. O resto roda sozinho: o maestro a cada 6 horas; a esteira a cada ciclo; os resultados voltam no envio da coleta local.
