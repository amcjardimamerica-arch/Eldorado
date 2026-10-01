# Parecer individual dos Pilotos — Espião e Interceptador · 01/10/2026

Base: missões depois das correções e skills de 29–30/09 (Espião: 1.338; Interceptador: 267 voos — 187 estudos de
edital e 80 dossiês), mais um diagnóstico da busca feito no próprio servidor do GitHub.

---

## Piloto - Espião (descobrir oportunidades e entidades novas)

### Onde acerta
- **Lê bem quando consegue ler**: no diagnóstico, as páginas abriram em 0,2 s com 6.000 caracteres; o buscador trouxe
  8 resultados com trecho nas consultas que passaram.
- **Aprende com o que funciona**: as consultas boas dos últimos 7 dias usam termos concretos — CONANDA, empresarial,
  saúde, doação, voluntariado, parceiros.
- **Agora registra o que buscou** (desde 30/09): o aprendizado deixou de ser cego.

### Onde erra
- **1.338 missões, 5 com resultado (0,4%)** — por uma causa só: **o buscador corta depois de 2 consultas seguidas**
  (diagnóstico: 8, 8, 0, 0, 0 resultados). O zero era gravado como "nada no crivo", a via entrava em descanso e todas
  as buscas seguintes do voo saíam vazias. O crivo recebia **texto vazio** ("o trecho fornecido está vazio").
- **Repetição cega**: a mesma consulta chegou a 98 tentativas no dia, porque o aprendizado escolhia "boas" do
  histórico e o bloqueio parecia falha delas.
- **Descoberta de entidades novas** segue fraca (1 resultado em 950): a consulta genérica traz notícias, não entidades.

### O que foi corrigido (parâmetros em `config/parametros_pilotos.json › espiao`)
| parâmetro | valor | por quê |
|---|---|---|
| intervalo_busca_s | 10 | o DuckDuckGo corta quem consulta em sequência |
| espera_se_busca_vazia_s / tentativas_se_vazia | 25 s / 2 | zero resultados é bloqueio: espera e tenta de novo |
| max_usos_da_mesma_consulta_por_dia | 3 | fim das 98 repetições |
| janela_aprendizado_dias | 7 | aprender com o presente, não com o histórico antigo |
| motivos_que_nao_punem_a_consulta | busca vazia, bloqueio, sem texto | a consulta só é reprovada quando foi lida e não serviu |
| reprovas_desde | 01/10 | as reprovações do período do bloqueio foram anuladas |

---

## Piloto - Interceptador (comprovar na fonte oficial e aprofundar o que existe)

### Onde acerta
- **Acha a página oficial em 71% dos estudos** (132 de 187).
- **Dossiês de empresas**: 80 empresas de Goiás com composição (sócios), contatos e projetos verificados — 5 dos 6
  itens em todos.
- **Lê PDFs**: 93 PDFs entre os 260 documentos dos 120 estudos mais recentes.

### Onde erra
- **4% validados, 58% insuficientes** nos 187 estudos recentes. Faltam sempre as condições do cronograma — prazo de
  recurso (161), resultado (154), valor (122) —, porque boa parte dos alvos é notícia ou menção, sem edital.
- **10 estudos perdidos** por resposta do modelo fora do formato; **12** sem fonte legível.
- **Repetição**: um mesmo alvo foi estudado 10 vezes.
- **Dossiês sem site**: os 80 ficaram sem o site da empresa (procurava só no cadastro e no e-mail da Receita) — o
  resumo investigativo não vem da leitura do site.

### O que foi corrigido (parâmetros em `config/parametros_pilotos.json › interceptador`)
| parâmetro | valor | por quê |
|---|---|---|
| tentativas_se_resposta_fora_do_formato | 2 | nova tentativa com instrução mais estrita |
| dias_sem_reestudar_o_mesmo_alvo | 7 | fim dos 10 estudos do mesmo alvo |
| dossie_busca_site | sim | procura o site pelo nome; só vale o domínio que contém o nome da empresa |

As lições estão nas skills `descobrir_entidades_novas`, `triagem_indicio`, `cronograma` e `dossie_empresa`.

---

## O conselho

**Extremamente pessimista — chief engineer.** O Espião trabalhou dois dias praticamente às cegas e o sistema chamou
isso de "nada no crivo". Um bloqueio externo virou aprendizado errado — e o aprendizado errado reforçou o erro.

**Pessimista — staff engineer.** Depender de um único buscador gratuito é o ponto frágil. Intervalo e nova tentativa
reduzem o problema, não o eliminam: a solução estrutural é uma segunda via (a chave da Brave Search, pendente).

**Levemente pessimista — professor.** O Interceptador gasta 10 minutos para concluir que uma notícia não tem
cronograma. Falta uma triagem rápida antes do estudo completo.

**Neutro — CTO (ponderador).** Os dois erros principais eram de infraestrutura e de medição, não de inteligência: o
buscador cortando e o motivo do insucesso mal classificado. Corrigido isso, os parâmetros passam a medir o que importa.
Pontos de controle: taxa de buscas com resultado acima de 80%; Espião com resultado acima de 5% das missões em 7 dias;
Interceptador com validadas acima de 15% e insuficientes abaixo de 40%; nenhum alvo reestudado em menos de 7 dias;
dossiês com site em pelo menos metade.

**Levemente otimista — professor.** O aprendizado agora separa o que é falha da consulta do que é falha do caminho — é
isso que permite evoluir sem se enganar.

**Otimista — staff engineer.** As apostas concretas já mostraram rendimento alto quando a busca funciona (91% antes do
bloqueio). Com a busca estável, o Espião volta a entregar.

**Extremamente otimista — CTO.** Com os dossiês ganhando o site e o Interceptador sem retrabalho, os dois Pilotos
passam a somar: um abre território, o outro aprofunda — com números que dizem a verdade.

### Pontos fortes para ampliar
Leitura de página e de PDF; página oficial em 71%; dossiês com composição e projetos; consultas concretas por tema.

### Pontos de falha para corrigir em seguida
Segunda via de busca (Brave Search — cadastro e segredo `BRAVE_SEARCH_KEY`); triagem rápida do Interceptador antes do
estudo completo; descoberta de entidades novas por listas oficiais (associações empresariais, fundações) em vez de
consulta genérica.
