# IA local da Biblioteca de Alexandria — estudo do conselho e decisão (20/09/2026)

## O pedido
Uma IA simples, de código aberto, que rode dentro do sistema — no computador do titular ou num
pen drive — de forma sozinha e independente, para **organizar e aprimorar os dados locais**:
catalogar o resultado das buscas, entender melhor cada edital a cada dia, melhorar links e o
direcionamento dos disparos. Finalidade principal: **organização e aprimoramento de buscas**.

## Uma correção necessária antes de tudo
Não existe "um Claude mais simples de código aberto". A Anthropic não publica os pesos de
nenhum modelo Claude. O que existe de aberto e pequeno vem de outras casas: **Qwen** (Alibaba,
licença Apache 2.0), **Gemma** (Google, licença própria permissiva), **Llama** (Meta, licença
comunitária com restrições), **Phi** (Microsoft, MIT), **SmolLM** (Hugging Face, Apache 2.0).
O Claude continua sendo a inteligência forte do sistema — na rotina de domingo e no pacote do
Desktop (Opus 5) — e a IA local faz o trabalho de organização que não exige um modelo grande.

## Como uma IA local funciona (para o titular)
Dois arquivos bastam:
1. **o motor** — `llama.cpp`, programa de código aberto (MIT) que executa modelos no processador
   comum, sem placa de vídeo. Pesa **17 MB** (Linux) ou **18,5 MB** (Windows). Já baixado e
   testado nesta sessão.
2. **o modelo** — um arquivo `.gguf` com os "pesos" comprimidos (quantização Q4: cada parâmetro
   em 4 bits). Um modelo de 1,5 bilhão de parâmetros ocupa ~1 GB; de 3 bilhões, ~2 GB.

Roda em qualquer PC com 4 GB de RAM livres; cabe num pen drive de 8 GB com sobra. Não precisa de
instalação: descompacta e executa. Um servidor local (`llama-server`) fica ouvindo em
`http://127.0.0.1:8080` e o sistema conversa com ele por HTTP, no mesmo formato da API da OpenAI.

## Modelos avaliados (só os que cabem no critério de disco e sabem português)

| modelo | tamanho Q4 | português | licença | veredito do conselho |
|---|---|---|---|---|
| **Qwen2.5-3B-Instruct** | ~2,0 GB | muito bom | Apache 2.0 | **principal** — melhor razão qualidade/tamanho, JSON estável, segue instrução |
| **Qwen2.5-1.5B-Instruct** | ~1,0 GB | bom | Apache 2.0 | **modo leve / pen drive** — mesma família, metade do disco |
| Gemma-2-2B-it | ~1,6 GB | bom | Gemma (permissiva) | alternativa; um pouco mais lento no CPU |
| Llama-3.2-3B-Instruct | ~2,0 GB | bom | Llama Community | licença mais restrita; sem ganho sobre o Qwen 3B em PT |
| Phi-3.5-mini (3,8B) | ~2,3 GB | médio | MIT | forte em inglês; PT irregular |
| SmolLM2-1.7B-Instruct | ~1,0 GB | fraco | Apache 2.0 | descartado para português |
| TinyLlama-1.1B | ~0,7 GB | fraco | Apache 2.0 | descartado — erra demais em JSON |
| Qwen2.5-7B-Instruct | ~4,7 GB | excelente | Apache 2.0 | acima do critério de disco; opcional para PC com 16 GB |

## Parecer do conselho

**Extremamente pessimista.** Um modelo de 3 bilhões erra. Vai inventar prazo, vai confundir
credenciamento com fomento, vai "completar" campo vazio. Se a saída dele entrar direto no banco,
o sistema volta ao problema dos 310 em Goiás — com mais confiança e menos rastro.

**Pessimista.** Roda no CPU: 5 a 15 tokens por segundo. Analisar 200 editais por dia leva uma
hora. E o computador do titular precisa estar ligado.

**Levemente pessimista.** Dois modelos (Claude e o local) opinando sobre o mesmo edital criam
ambiguidade: qual vale?

**Neutro — a decisão.** A IA local **nunca decide sozinha**: ela **propõe**, e tudo o que ela
propõe (a) sai em JSON com esquema fixo, (b) passa por validação determinística antes de ser
gravado, (c) fica marcado com `origem: ia_local` e o nome do modelo, (d) pode ser revertido
em bloco. Ela trabalha na **camada de organização**, onde o custo do erro é baixo e a
verificação é barata: classificar registros pelo objeto, propor termos de léxico, sugerir
por que uma rota não rendeu e o que tentar, extrair objeto/prazo de texto já coletado
(com o trecho que justifica), e catalogar o achado do dia. Prazo, valor e página oficial só
entram no registro se houver **trecho literal** no texto que os sustente — a mesma regra que
vale para o robô e para o titular. O Claude continua com a análise que exige juízo (aderência,
parecer, decisão de inscrição).

**Levemente otimista.** O que a IA local faz bem — classificar, sugerir, resumir texto já
obtido — é exatamente o gargalo de hoje: 122 análises incompletas e 18 motores "lendo sem achar"
que ninguém tem tempo de investigar.

**Otimista.** Roda de graça, todo dia, o dia inteiro, no computador ligado do titular. Cada
rodada devolve propostas; o que passa na validação melhora o léxico e as rotas do dia seguinte.
É o "aumenta o entendimento a cada dia" pedido, com rastro.

**Extremamente otimista.** Em um mês de operação, o léxico aprendido e as rotas sugeridas pela
IA local podem cobrir a maior parte dos "lendo sem achar" — e o Claude passa a receber pacotes
já organizados, gastando tempo só no que exige juízo.

## O que foi implantado (20/09)
- `config/ia_local.json` — motor, modelo principal e leve, endereço do servidor, tarefas
  permitidas, limites e a regra de validação.
- `scripts/ia_local_instalar.py` — baixa o llama.cpp (release do GitHub, 17 MB) e o modelo GGUF
  (Hugging Face), para a pasta `ia_local/` do repositório ou para um pen drive; cria o
  `iniciar.bat` / `iniciar.sh`.
- `src/ia_local.py` — cliente HTTP do `llama-server`; cinco tarefas com esquema JSON e
  validação: `classificar_objeto`, `extrair_objeto_prazo` (só com trecho literal),
  `propor_lexico`, `diagnosticar_rota`, `catalogar_achado`. Grava propostas em
  `estado/ia_local/propostas-<data>.json`; `aplicar()` só aceita o que passa na validação.
- Pacote do Desktop passa a incluir a etapa "IA local: rodar `python -m src.ia_local ciclo`".
- Testes com servidor simulado (sem modelo): o contrato, a validação e a recusa de dado sem trecho.

## Como o titular liga
```
python scripts/ia_local_instalar.py            # uma vez; ~2 GB; pode apontar --destino E:\eldorado-ia
ia_local\iniciar.bat                           # sobe o servidor local (janela fica aberta)
python -m src.ia_local ciclo                   # roda as tarefas do dia e grava as propostas
python -m src.ia_local aplicar                 # aplica só o que passou na validação
```
No Claude Desktop, o pacote diário já contém esses passos; a tarefa agendada de 07h executa tudo.
