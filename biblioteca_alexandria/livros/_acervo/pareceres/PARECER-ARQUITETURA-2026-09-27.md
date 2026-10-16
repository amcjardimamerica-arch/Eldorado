# Parecer do conselho — arquitetura de descoberta e organização, etapa por etapa · 27/09/2026, 23h40

*Auditoria feita nos dados e nos workflows, não na tela: 17 workflows, os arquivos de cada etapa, a coerência entre
as contas e o histórico de gravações do repositório.*

## 1. O fluxo, como está hoje

```
motores (30) ─┐                     ┌─> mestre (18.863 registros) ──┐
Espião ───────┼─> descoberta ───────┤                               ├─> fluxo ─> mapa · calendário · painel lateral
motores OPR ──┘   (indícios)        └─> candidatas / radar ─────────┘      │
                                                                             ├─> opressor novo (30 dias)
Interceptador (Goiás → sorteio) ─> site oficial ─> 12 condições ─> registro ─┤
                                                                             ├─> cadastro preditivo
                                                                             └─> fila do Claude (a cada 3 dias)
gerador principal ─> dashboard-dados.js + fragmentos ─> camada ao vivo (API → cópia pública → site, 4 min)
```

## 2. O que a auditoria encontrou — e já foi corrigido

| # | invisível na tela | gravidade | correção |
|---|---|---|---|
| 1 | **Um voo do Espião desfez a leitura pela API às 21h49**: o gerador principal reescrevia o próprio `dashboard.html` a cada voo (só para trocar o número de versão) e gravava a cópia antiga por cima | crítica | reescrita removida; leitura pela API reaplicada; teste de guarda |
| 2 | **Histórico do repositório inchando**: 394 gravações em 24 h, 1,5 GB; o arquivo de oportunidades (8 MB) regravado 123× em 300 gravações — ~1 GB — com o mesmo conteúdo (só a ordem das chaves mudava) | alta | fragmentos grandes só regravados se o conteúdo mudou (provado: duas rodadas, nenhuma regravação) |
| 3 | **Prontidão rodava a cada gravação** — centenas de execuções por dia, 15 de 15 falhando, escondendo falha real | alta | só com mudança de código, testes, configuração ou workflows, e 1×/dia |
| 4 | **Busca ativa antiga cancelada por tempo** em 8 execuções seguidas | média | sem agendamento (o Interceptador faz esse trabalho) |
| 5 | **Ranking com 22 MB**, relido inteiro a cada 4 min | média | 16 MB; a camada ao vivo não baixa de novo o que não mudou (ETag) |
| 6 | **4 opressores duplicados** no catálogo | baixa | removidos; o fluxo compara programa + órgão antes de criar |
| 7 | **Nada avisava quando algo quebrava em silêncio** (59 erros silenciados só no monitoramento) | alta | verificador de saúde: arquivos, frescor de cada gerador, coerência, falha do gerador, análise do Claude, duplicados, workflows — no cabeçalho do painel |

Íntegros: nenhum JSON corrompido; mestre sem ids duplicados; número do mapa = lista em todos os estados; soma dos
estados = total; nenhum token gravado no repositório.

## 3. O que continua pendente (em ordem)

1. **A análise do Claude a cada 3 dias não tem gatilho.** 199 itens esperam validação ou descarte, e nenhuma análise foi
   feita. Ela depende de o titular chamar o Claude; o verificador de saúde agora mostra o atraso no cabeçalho. *Proposta:*
   o titular abre uma conversa a cada 3 dias com "faça a análise da fila" — ou uma rotina com chave de API própria.
2. **Quatro testes antigos do sistema falham**, então a prontidão diária seguirá vermelha até serem acertados: painel acima
   de 20 MB (o ranking), contagem da validação dos 467 (414 > 400), um campo `pontos` ausente num teste de empresas, e
   uma verificação de texto do calendário por motor.
3. **O desenho "cada voo grava a cópia inteira por cima"** continua frágil. As proteções cobrem o que foi apagado e o que o
   voo não mexeu, mas não um arquivo que o voo regenerou a partir de dados velhos. *Proposta:* cada papel grava só na sua
   pasta, e os derivados grandes (ranking, oportunidades) passam a ser gerados na publicação, não commitados a cada voo.
4. **O histórico de 1,5 GB** não encolhe sozinho: o corte do inchaço vale daqui para frente. Uma limpeza do histórico
   (reescrita) pode ser feita depois, com o titular ciente de que muda os identificadores das gravações antigas.
5. **Cadastro preditivo**: 209 oportunidades, mas só 4 com estudo do Interceptador anexado — os identificadores das
   oportunidades estudadas nem sempre coincidem com os do cadastro.
6. **Segurança**: o token do GitHub usado nesta conversa continua ativo e deve ser **revogado** e substituído por um novo,
   com as permissões mínimas (Actions e Contents).

## 4. O conselho

**Extremamente pessimista.** Uma correção publicada foi desfeita em minutos por um processo automático, e ninguém veria
isso na tela. É o tipo de falha que faz o titular desconfiar de tudo o que o painel mostra.

**Pessimista.** 394 gravações por dia num repositório de 1,5 GB é um relógio correndo: o GitHub limita repositórios e
sites publicados, e cada voo regravando megabytes aproxima o limite.

**Levemente pessimista.** O verificador de saúde enxerga, mas não conserta; sem alguém olhando os alertas, eles viram
ruído — como a prontidão virou.

**Neutro (ponderador).** A arquitetura de descoberta está correta e coerente nos dados: mapa, lista e fluxo batem. As
falhas estavam na operação — processos que regravam o que não é deles, erros engolidos, verificação que ninguém lia.
As três correções estruturais de hoje (o painel não é mais reescrito pelos voos, arquivos só regravados quando mudam,
saúde visível no cabeçalho) atacam exatamente isso. Parâmetros de qualidade daqui em diante: cabeçalho com "saúde: ok";
prontidão diária verde; análise do Claude em dia; crescimento do histórico medido semanalmente.

**Levemente otimista.** Nenhum dado corrompido, nenhuma divergência entre as contas: a base é sólida.

**Otimista.** Com a saúde no cabeçalho, o titular passa a ver, sem abrir o GitHub, se algum gerador parou, se o mapa
diverge ou se a análise atrasou.

**Extremamente otimista.** Cada falha encontrada hoje virou teste: o sistema passa a se defender das próprias regressões.
