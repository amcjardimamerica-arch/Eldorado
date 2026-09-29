# Parecer do conselho — motores parados na Bússola (22, 29, 30) e os dias 27 e 28 · 28/09/2026

## O que estava acontecendo — três causas

| causa | efeito | correção |
|---|---|---|
| **O gerador dos motores quebrava** (`KeyError: 'segmento'`, depois `'camadas'`) desde que os opressores viraram repositórios de oportunidade (`op-…`, criados hoje de manhã) — registros sem campos que ele exigia; a falha era engolida pelo monitoramento | o arquivo dos calendários dos motores parou em 27/09 14h42 (monitoramento) e 28/09 09h59: **todos** os motores apareciam "não executado" em 27 e 28 | o gerador completa com valores neutros os registros que não criou; roda de novo em 3 s |
| **O GitHub entrega só 8 a 12 das 48 execuções horárias por dia** do agendador, e o motor só saía se a execução caísse **exatamente** no seu horário | motor perdia o dia inteiro quando o GitHub pulava o horário — foi o que houve com os motores 29 e 30 no domingo (execuções às 2h51 e 3h42; agenda 3h23) | **recuperação do horário perdido**: cada execução dispara todo motor cujo horário já passou e que não rodou desde então; a última leitura vem do painel (o registro que o agendador consultava nem existia) |
| **Motores 29 e 30 (empresas)** só rodavam pelo agendamento de domingo 6h UTC — que tinha sumido da lista — e, chamados pelo nome, o monitoramento entrava em modo manual, que não executa a leitura de empresas | nunca executavam | o domingo volta à agenda; chamados pelo nome, rodam a leitura de empresas |
| **Motor 22 (Mapa das OSC)** tinha sido desativado ("base cadastral, não publica editais"), mas seguia no painel como ativo, sem agenda | "sem leitura ainda" para sempre | reativado lendo a página de **editais** do Mapa das OSC, seg/qua/sex 11h23; se não houver editais, aparece "lendo, sem achados" |
| **Domingo** fora da agenda de vários motores (seg–sex) aparecia como "não executado" | parecia falha | o calendário mostra **"fora da agenda"** nos dias sem horário |

## O conselho

**Extremamente pessimista.** Uma mudança de dados (os repositórios) derrubou o gerador de todos os motores, e a tela
seguiu mostrando o calendário velho sem avisar — o erro engolido foi o verdadeiro defeito.

**Pessimista.** Agendamento horário no GitHub é melhor-esforço: contar com o horário exato era apostar na exceção.

**Neutro (ponderador).** As três correções atacam a causa: gerador tolerante a registros de outros criadores,
agendador que recupera o que perdeu, e motores de empresas com gatilho real. Parâmetros: saúde acusa o arquivo dos
motores com mais de 30 h; teste de guarda para o gerador e o agendador; "fora da agenda" separado de "não executado".

**Otimista.** Na próxima execução do agendador, os motores atrasados (entre eles 29 e 30) já saem.
