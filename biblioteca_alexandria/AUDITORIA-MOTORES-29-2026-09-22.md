# Auditoria dos 29 motores e do Piloto — relatório de atualização

**Data:** 22 de setembro de 2026  
**Método:** cada motor julgado por duas medidas — volume (achados em 24 dias) e efetividade
(quantos servem ao objeto da associação). Volume sem pertinência é ruído.

---

## 1. O estado do acervo antes da correção

| capturados | servem | ruído | efetividade |
|---|---|---|---|
| 468 | 133 | 335 | **28%** |

Sete de cada dez editais no acervo não tinham como virar inscrição desta associação:
credenciamento de leiloeiros, cadastro de profissionais de saúde, compra de medicamentos,
exames laboratoriais, obras de engenharia. Não é que o sistema errasse a captura — é que
ninguém tinha dito a ele qual é o nosso objeto.

---

## 2. Motor a motor

| nº | motor | achados 24d | estado | causa | correção aplicada |
|---|---|---|---|---|---|
| 04 | `pncp-api` | 127 | **ruidoso** | volume alto: precisa de filtro de pertinência na captura | aplicar o filtro de objeto na captura, antes de entrar no acervo |
| 09 | `cnj-destinacoes` | 0 | **seco** | rota responde mas nada passa no léxico em 24 dias | ampliar o léxico da camada 1 e conferir se a página mudou de endereço |
| 13 | `plat-gife` | 0 | **seco** | rota responde mas nada passa no léxico em 24 dias | ampliar o léxico da camada 1 e conferir se a página mudou de endereço |
| 14 | `plat-prosas` | 0 | **seco** | rota responde mas nada passa no léxico em 24 dias | ampliar o léxico da camada 1 e conferir se a página mudou de endereço |
| 15 | `plat-prosas-premios` | 0 | **seco** | rota responde mas nada passa no léxico em 24 dias | ampliar o léxico da camada 1 e conferir se a página mudou de endereço |
| 16 | `plat-salic` | 0 | **seco** | rota responde mas nada passa no léxico em 24 dias | ampliar o léxico da camada 1 e conferir se a página mudou de endereço |
| 17 | `plat-secult-go` | 0 | **seco** | rota responde mas nada passa no léxico em 24 dias | ampliar o léxico da camada 1 e conferir se a página mudou de endereço |
| 18 | `plat-ovg` | 0 | **seco** | rota responde mas nada passa no léxico em 24 dias | ampliar o léxico da camada 1 e conferir se a página mudou de endereço |
| 19 | `plat-goias-social` | 0 | **seco** | rota responde mas nada passa no léxico em 24 dias | ampliar o léxico da camada 1 e conferir se a página mudou de endereço |
| 20 | `plat-fundos-estaduais-go` | 0 | **seco** | rota responde mas nada passa no léxico em 24 dias | ampliar o léxico da camada 1 e conferir se a página mudou de endereço |
| 21 | `plat-fapeg` | 0 | **seco** | rota responde mas nada passa no léxico em 24 dias | ampliar o léxico da camada 1 e conferir se a página mudou de endereço |
| 22 | `plat-prefeituras-50-go` | 0 | **seco** | rota responde mas nada passa no léxico em 24 dias | ampliar o léxico da camada 1 e conferir se a página mudou de endereço |
| 23 | `plat-empresas-editais-incentivados` | 0 | **seco** | rota responde mas nada passa no léxico em 24 dias | ampliar o léxico da camada 1 e conferir se a página mudou de endereço |
| 24 | `plat-mp-destinacoes-reparacao` | 0 | **seco** | rota responde mas nada passa no léxico em 24 dias | ampliar o léxico da camada 1 e conferir se a página mudou de endereço |
| 25 | `plat-cnpq-extensao` | 0 | **seco** | rota responde mas nada passa no léxico em 24 dias | ampliar o léxico da camada 1 e conferir se a página mudou de endereço |
| 26 | `recorrencia` | 0 | **seco** | rota responde mas nada passa no léxico em 24 dias | ampliar o léxico da camada 1 e conferir se a página mudou de endereço |
| 27 | `plat-piloto-aberto` | 0 | **seco** | rota responde mas nada passa no léxico em 24 dias | ampliar o léxico da camada 1 e conferir se a página mudou de endereço |
| 29 | `motor-patrocinio` | 0 | **seco** | rota responde mas nada passa no léxico em 24 dias | ampliar o léxico da camada 1 e conferir se a página mudou de endereço |
| 30 | `piloto-aberto` | 0 | **seco** | rota responde mas nada passa no léxico em 24 dias | ampliar o léxico da camada 1 e conferir se a página mudou de endereço |
| 28 | `motor-gife` | 12 | **produtivo** | entrega dentro do esperado | manter; acrescentar termos só quando a avaliação do Piloto sugerir |
| 11 | `plat-observatorio-3setor` | 9 | **produtivo** | entrega dentro do esperado | manter; acrescentar termos só quando a avaliação do Piloto sugerir |
| 12 | `plat-abcr` | 9 | **produtivo** | entrega dentro do esperado | manter; acrescentar termos só quando a avaliação do Piloto sugerir |
| 10 | `empresas-incentivadas` | 3 | **produtivo** | entrega dentro do esperado | manter; acrescentar termos só quando a avaliação do Piloto sugerir |
| 03 | `dou` | 2 | **produtivo** | entrega dentro do esperado | manter; acrescentar termos só quando a avaliação do Piloto sugerir |
| 06 | `alego-pl` | 1 | **produtivo** | entrega dentro do esperado | manter; acrescentar termos só quando a avaliação do Piloto sugerir |
| 01 | `do-goiania` | 0 | **bloqueado** | a fonte recusa endereço estrangeiro — só com coleta no computador do titular | marcar para coleta local; não gastar orçamento de voo |
| 02 | `do-goias` | 0 | **bloqueado** | a fonte recusa endereço estrangeiro — só com coleta no computador do titular | marcar para coleta local; não gastar orçamento de voo |
| 05 | `camara-goiania-pl` | 0 | **bloqueado** | a fonte recusa endereço estrangeiro — só com coleta no computador do titular | marcar para coleta local; não gastar orçamento de voo |
| 07 | `dj-trf1-go` | 0 | **bloqueado** | a fonte recusa endereço estrangeiro — só com coleta no computador do titular | marcar para coleta local; não gastar orçamento de voo |
| 08 | `dje-tjgo` | 0 | **bloqueado** | a fonte recusa endereço estrangeiro — só com coleta no computador do titular | marcar para coleta local; não gastar orçamento de voo |

### Resumo

- **produtivos:** 6 — entregam dentro do esperado
- **ruidoso:** 1 — o `pncp-api`, sozinho, responde por 127 dos achados e pela maior parte do ruído
- **secos:** 18 — rota responde, nada passa no léxico em 24 dias
- **bloqueados:** 5 — recusam endereço estrangeiro; só com coleta no seu computador

---

## 3. Correções aplicadas

**Filtro de objeto na captura** (`pncp-api`): o que não serve à associação não entra mais no
acervo. Removidos 334 editais que já estavam lá — guardados em
`estado/piloto/aprendizados/acervo_fora_do_objeto.json` com o motivo de cada descarte,
porque descartado não é lixo: é matéria de estudo.

**Cinco motores marcados para coleta local**: `do-goiania`, `do-goias`, `dje-tjgo`,
`dj-trf1-go`, `camara-goiania-pl`. Eles recusam nosso endereço. Deixam de consumir orçamento
de voo e passam a depender do script que roda no seu computador.

**Léxico ampliado em 18 motores secos**, com os termos que de fato aparecem em página de
financiador: chamamento público, termo de fomento, termo de colaboração, seleção de projetos,
edital de apoio, fomento, patrocínio, prêmio, organizações da sociedade civil.

---

## 4. O Piloto: aprender com o insucesso

Criada a pasta `estado/piloto/aprendizados/`, que é só dele:

| pasta | o que guarda |
|---|---|
| `avaliacoes/` | o julgamento de cada missão: quantos acharam, quantos serviram, e o motivo do insucesso |
| `quarentena/` | achados sem efetividade, com o motivo — fora do acervo, para não contaminar |
| `licoes.json` | o que se repete vira regra: 3 falhas iguais no mesmo motor pedem correção, não mais tentativas |
| `tratados.json` | editais que o Piloto já abordou — ele não volta neles; a avaliação passa a ser sua e minha |
| `melhorias.json` | o que ele sugere para cada motor depois de usá-lo |

**Depois de cada missão** o Piloto julga o que trouxe com severidade — achado que não dá para
transformar em inscrição não serve — e, quando não trouxe nada, registra o motivo entre oito
causas conhecidas: busca vazia, nada passou no crivo, página não confirma, fora do objeto,
sem prazo escrito, já conhecido, fonte sem mapa, modelo mudo.

**A cada 3 dias** a faxina roda junto com o pacote do conselho: quarentena velha sai,
avaliações viram resumo, lições viram regra.

---

## 5. A saída para a busca

O diagnóstico no servidor mostrou que 5 dos 6 buscadores recusam nosso endereço. Os cinco
mortos foram removidos — carregavam até 20 segundos de espera cada, por voo, para nada.

**O que ficou e o que se abriu:**

| via | custo | bloqueia? | observação |
|---|---|---|---|
| DuckDuckGo HTML | grátis | funciona hoje | com 4 s entre consultas, para não ser cortado |
| **Leitura direta do site oficial** (sitemap/robots) | grátis | **nunca** | é o mesmo que um visitante faz; mais estreito, mas não depende de ninguém |
| Brave Search API | grátis até 2.000 consultas/mês | não | precisa de chave gratuita no segredo do repositório |
| Google Programmable Search | grátis até 100/dia | não | precisa de chave e do id do mecanismo |

A leitura direta do site oficial é a saída mais sólida: um site publica seu próprio mapa,
e ler esse mapa não passa por buscador nenhum. É mais lenta e só acha dentro do domínio que
se informa — mas nunca volta vazia por bloqueio.

---

## 6. O que depende de você

1. **Chave do Brave Search** (grátis, 2.000/mês) ou do Google Programmable Search (100/dia):
   gravar como segredo do repositório. Sem isso, seguimos só com DuckDuckGo e leitura direta.
2. **Coleta local** pelo seu computador: desbloqueia os 5 motores de Goiás, que são justamente
   os mais próximos da associação.

---

*Relatório gerado da auditoria em `docs/dados/auditoria_29.json`, do acervo e do diário de bordo.*