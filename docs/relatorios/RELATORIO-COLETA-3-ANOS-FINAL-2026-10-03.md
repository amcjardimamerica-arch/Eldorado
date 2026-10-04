# Relatório final — Coleta de 3 anos dos 2180 livros (Goiás → Brasil → Internacional → outros estados)

Data: 03/10/2026 · Janela de leitura: 03/10/2023 a 03/10/2026 · Sistema Eldorado / Farol de Alexandria

## 1. Resultado em uma frase

Os 2180 livros foram percorridos e **nenhum ficou pendente**: cada um tem situação individual registrada, com os 12 itens do edital (Objeto, Prazo de inscrição, Resultado, Prazo de recurso, Valor, Órgão/financiador, Território, Esfera, Requisitos, Anexos, Destinação, Área de atuação) preenchidos por edição ou com dispensa individual justificada, e com um relatório preditivo próprio em `dados/coleta_3_anos/relatorios/<id>.md` e `.json`.

## 2. Selos e situações

Selos de livro hoje: ouro 242, prata 355, bronze 1583. O selo ouro exige edições em 2 ou mais anos distintos, com ao menos uma anterior ao ano corrente em página oficial e com data; prata é alguma edição anterior; bronze é nenhuma.

| Bloco | Livros | Validado | Validado parcial | Série indicada / sem datas | Verificado sem série | Dispensa individual | Pendente |
|---|---|---|---|---|---|---|---|
| Goiás | 387 | 77 | 73 | 19 | 11 | 207 | 0 |
| Brasil | 1003 | 97 | 108 | 27 | 270 | 501 | 0 |
| Internacional | 64 | 2 | 7 | 1 | 2 | 52 | 0 |
| Outros estados | 726 | 66 | 146 | 17 | 338 | 159 | 0 |

Como ler cada situação. **Validado** é recorrência comprovada em 2 ou mais anos com página oficial. **Validado parcial** é edição anterior comprovada, mas em um só ano ou com datas incompletas, e vale para previsão com confiança média. **Série indicada** é quando o título ou a fonte oficial se numera como edição posterior à primeira (por exemplo, 14º edital da Rede do Bem, 39º do ISPN/Ecos, Ciclo 2 da Política Nacional Aldir Blanc): a repetição está provada pela fonte oficial, mas as datas das edições anteriores ainda não foram lidas. **Série confirmada sem datas** é a edição de anos anteriores achada na página oficial sem a data de inscrição. **Verificado sem série** é livro consultado em fonte oficial ou busca e sem edição anterior do mesmo objeto localizada, com o que foi lido registrado no texto. **Dispensa individual** é a dispensa justificada de cada livro, pelos motivos abaixo.

| Motivo da dispensa | Livros |
|---|---|
| fora_escopo_perfil | 215 |
| estrutural | 158 |
| espelho_agregador | 105 |
| fora_escopo_contratacao | 90 |
| ruido_diario | 57 |
| ruido_portal | 38 |
| ciclo_unico | 37 |
| fora_escopo_compra | 34 |
| ato_derivado | 25 |
| emenda | 21 |
| fundo | 21 |
| regime_incentivo_fiscal | 20 |
| arquivar | 20 |
| mp | 18 |
| regime_credenciamento_permanente | 18 |
| indice | 17 |
| judicial | 11 |
| regime_destinacao_judicial | 7 |
| regime_fluxo_continuo | 5 |
| regime_doacao_de_bens | 2 |

## 3. Os 12 itens das edições anteriores

Nas 730 edições comprovadas, os 12 itens somam 8.760 leituras: 1.874 confirmados na página da edição, 3.467 vindos do catálogo do livro (esfera, área, destinação/público, órgão, território), 211 dispensados pelo tipo do edital e 3.208 ainda não localizados. Cada não localizado traz o motivo escrito (Resultado, Prazo de recurso, Requisitos, Anexos e Valor ficam no corpo do edital em PDF ou em publicação posterior, não lidos nesta rodada) e é pendência explícita, nunca suposição. Esses 3.208 só se fecham lendo cada PDF; não foram fechados nesta rodada.

## 4. Relatório preditivo por oportunidade

Cada livro tem mês típico de abertura, duração típica, próxima janela provável e confiança (alta no ouro, média na prata, baixa no bronze), além de intervalo entre edições. Nada é inventado: edição que só tem a data de encerramento lida fica com abertura nula e não entra no cálculo do mês típico. Esta correção foi feita nesta etapa em `src/selo_livros.py` e `src/relatorio_livros.py`, porque cinco livros de Goiás (Natal do Bem, FAPEG e inscrição de edital em Goiânia) apareciam com abertura em 01/01, data fabricada pelo ano.

## 5. Conselho de 7 lentes (decisão do neutro)

Cada relatório traz as sete lentes, do extremamente pessimista ao extremamente otimista. O consolidado do neutro para esta coleta é o seguinte. Os pessimistas apontam que 621 livros estão apenas verificados sem série, que 3.208 itens de edições ficaram não localizados e que parte das aberturas pode ser a data da notícia, e não a da inscrição. Os otimistas apontam que 242 livros estão validados, que a janela de 3 anos já dá calendário para os de ouro e que o preditivo antecipa o aviso e o reuso do plano de trabalho. O neutro decide: usar a previsão de mês apenas nos ouro e na prata com data; tratar o restante como radar; conferir a página do órgão 30 dias antes da janela (Lei 13.019/2014, art. 26); ler as datas das edições "série indicada" antes de apostar em calendário; e auditar a série por amostra de 10% a cada trimestre.

## 6. Auditoria feita nesta etapa

Auditoria programática de todas as 576 séries validadas e parciais: nenhuma edição fora da janela, nenhuma com encerramento anterior à abertura, nenhuma com vigência acima de 400 dias tratada como prazo, nenhum mês duplicado na mesma série. Foram achadas 26 edições sem página oficial (todas em livros "validado parcial", portanto com confiança média) e 5 aberturas em 01/01 fabricadas, já corrigidas.

## 7. Limites que o titular precisa conhecer

Séries do tipo ordinal por programa (PNAB, ProAC) têm a repetição provada, mas as datas dos editais municipais anteriores não foram lidas uma a uma. Algumas edições usam a data da divulgação na imprensa como abertura. O portal goias.gov.br suspendeu notícias no período eleitoral, o que impediu a leitura de algumas páginas de Goiás, e por isso alguns livros goianos ficaram em "verificado sem série" com busca web como fonte. A classificação de "fora de escopo" dos livros de compra, contratação, pessoas físicas, conselhos e prêmios é do sistema e deve ser confirmada pelo titular antes de arquivar.

## 8. Urgente para a AMC

O edital MPT-GO 009220.2026 (PTM Anápolis) tem data segura de inscrição até 05/10/2026.

## 9. Como aplicar

O pacote traz `LEIA-ME-APLICAR.md`, a pasta `arquivos/` (src, tests, docs/dados, `dados/coleta_3_anos/**` com relatorios/, itens12/, specs/ e as ferramentas tools_*.py) e um git bundle da branch `claude/coleta-3-anos-go-2026-10-03`. O envio direto ao GitHub deu 403 neste ambiente, por isso o pacote segue para ser enviado por outro chat.

## 10. Testes e privacidade

A verificação de privacidade passou ("nenhuma credencial publicada"). A suíte de testes tem falhas que já existiam antes desta coleta (50 falhas e 3 erros na base 9840bf7e, quase todas de testes de painel/dashboard); nesta branch são 48 falhas e 3 erros, **nenhuma nova**, e 5 testes a mais passando. Corrigir essas falhas antigas é tarefa à parte.
