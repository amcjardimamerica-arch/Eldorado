# Fechamento de 23/09/2026 — dados atualizados e fila fechada

**O que o titular pediu:** "Quero que atualize todos dados e deixe tudo fechado e pronto / use acesso local para buscar e ter as informações necessárias."

**O que ficou:** nenhum edital com prazo aberto está sem objeto, sem prazo ou sem página oficial. O que resta na fila é só o que ninguém conseguiu confirmar prazo — e cada linha diz por quê.

---

## 1. O que foi lido, e por onde

A nuvem não alcança o PNCP: as chamadas saem pelo proxy e voltam bloqueadas. A rota que funcionou foi o **navegador local do titular**, e foi por ela que 21 leituras foram feitas em 23/09/2026 — 14 registros na API oficial de consulta e 7 listas de arquivos do próprio órgão.

**Os 5 editais de Goiás que nenhuma rodada anterior tinha verificado estão todos encerrados:**

| Órgão | Encerramento | Situação |
|---|---|---|
| Formosa/GO | 22/07/2026 16h45 | julgado — anexos trazem HOMOLOGAÇÃO e TERMO DE COLABORAÇÃO 05/2026 |
| Cavalcante/GO | 25/11/2024 17h00 | encerrado |
| Alvorada do Norte/GO nº 423 | 19/12/2023 17h00 | encerrado |
| Alvorada do Norte/GO nº 424 | 19/12/2023 17h00 | julgado — homologação nos anexos |
| Planaltina/GO (Esporte 2026) | 13/05/2026 08h00 | julgado — homologação e adjudicação |

Além destes, a busca oficial revelou **2 registros novos** de Planaltina/GO (Esporte 2026 e Cultura 2025), ambos também encerrados.

**Os 7 registros que a nuvem não conseguira reconfirmar agora têm hora exata:**
Indaiatuba/SP 25/09/2026 09h00 · Itatinga/SP 02/10/2026 23h59 · Osório/RS 07/10/2026 · Montes Claros/MG 09/11/2026 18h00 · UNICENTRO/PR 10/12/2026 08h00 · Canoas/RS 31/12/2027 · Peruíbe/SP 05/11/2029 14h01.

**Uma chave estava errada na base.** Osório/RS apontava para `88866396000155/2026/122`, que devolve HTTP 400 — registro inexistente. O verdadeiro é `88814181000130/2026/450`, encontrado pela busca oficial do PNCP.

---

## 2. Três defeitos encontrados no caminho

### O mesmo edital existia duas vezes, e ninguém via

A base de oportunidades sempre truncou o identificador em oito caracteres. As bases de verificação, não — guardam a chave inteira de vinte. As duas grafias nunca se encontravam.

O efeito era pior do que duplicata: **27 registros já verificados e fechados em 15/09 continuavam aparecendo como "em aberto sem informação"**, porque a verificação nunca chegava neles. Mais 7 editais existiam em duas linhas cada.

A correção é `chave_curta`, em `src/nucleo.py`: toda leitura de base passa por ela, e as duas grafias voltam a ser o mesmo registro. Chave escrita à mão (`planaltina-esporte-2026`) fica inteira, porque oito caracteres dela não identificam nada. Truncar só é seguro enquanto nenhum prefixo de oito servir a dois identificadores diferentes — em 23/09 não havia um único caso em mais de dezessete mil registros, e **agora há teste cobrando que continue assim**.

### Prazo vencido estava sendo contado como reprovação por objeto

O painel dizia que 492 registros foram derrubados pelo objeto. Não eram. **24 deles têm natureza de fomento legítima e foram reprovados só por estarem fora do tempo** — prazo encerrado, edital já julgado, homologação publicada. Somados aos que de fato não são edital de fomento, davam a leitura errada de que o motor derruba por objeto muito mais do que derruba.

Agora são dois contadores separados: `reprovado_por_objeto` (463) e `reprovado_por_prazo_vencido` (24).

### Porta de entrada não tem prazo, e estava sendo cobrada como se tivesse

Emenda parlamentar, Lei Rouanet, doação de mercadorias da Receita Federal, prestações pecuniárias do TJGO, patrocínio BNDES, cadastro do Instituto Impactarte: nenhum destes tem edital com data. O que têm é **porta de entrada em fluxo contínuo**. Cobrar prazo deles é cobrar o que não existe.

Passaram a ter bloco próprio, com o endereço da porta no lugar da data. Foram 12 capturas que correspondem a **9 portas distintas** — o BNDES chegara duas vezes em cada uma das suas duas portas, e o Impactarte por dois domínios.

---

## 3. Dúvida encerrada: os dois domínios do Impactarte

A coleta trazia `impactarte.com.br` e `impactarte.org.br` como endereços divergentes da mesma oportunidade. Lidos no navegador local em 23/09: **servem o mesmo site**, mesmo título e mesmo menu. O `.com.br` é a home; o `.org.br/cadastro-proponente` guarda o formulário — cadastro aberto de organizações, com causas de atuação, abrangência territorial, certificações, missão e metodologia, e **sem data de encerramento em lugar nenhum**.

Não são duas fontes, é uma. O registro na curadoria foi completado (`curadoria-008`), não duplicado — e essa contenção foi checada: uma tentativa de gravar como fonte nova foi revertida ao ver que a fonte já existia.

---

## 4. Estado final dos dados

**Fila de pesquisa** — `docs/dados/abertos_sem_informacao.json`

| | antes | depois |
|---|---|---|
| registros na fila | 167 | **107** |
| com prazo aberto ainda sem informação | 5 | **0** |
| urgentes (prioridade 1) | 2 | **0** |
| identificadores repetidos | 7 | **0** |

Os 107 restantes são todos `sem_prazo_confirmado`: prioridade 3 (26), 4 (80) e 5 (1). Nenhum deles tem prazo aberto — são registros para os quais nenhuma fonte oficial confirmou data, e 90 exigem o navegador do titular para avançar.

**Descartados, com motivo:** 17.140 edições de diário sem ato · 463 reprovados pelo objeto · 77 encerrados · 24 reprovados por prazo vencido · 17 completos · 12 capturas de mecanismo permanente.

**Vigilância de prazos** — `estado/prazos.json`: 86 prazos confirmados (eram 82), 9 críticos, 71 encerrados.

**Os 7 registros ainda em aberto têm página oficial de verdade.** Não a página de divulgação do PNCP — o arquivo que o **próprio órgão** anexou ao registro, lido na lista oficial de arquivos em 23/09. A origem fica declarada em cada um, conforme a regra que o titular afinou em 08/09, e a página de divulgação fica guardada à parte, sem valer como fonte.

---

## 5. Nenhuma data foi inventada

A regra vale inteira. Campo sem confirmação saiu nulo, com o motivo escrito na observação. Os 107 registros que continuam sem prazo continuam sem prazo — não receberam estimativa, não receberam data plausível. Um `null` honesto vale mais que uma data plausível.

---

## 6. Testes

**394 testes, todos passando.** Foram acrescentados 27 novos, em `tests/test_fechamento_2026_09_23.py`, cobrindo: a base de fechamento (forma, vocabulário, nenhuma data inventada, os cinco de Goiás encerrados, a chave de Osório corrigida), a página oficial dos abertos (arquivo do órgão, origem declarada, divulgação não vale), `chave_curta` (inclusive a ausência de colisão de prefixo nas dezessete mil chaves reais), a separação da reprovação temporal, o reconhecimento de mecanismo permanente e o colapso das portas duplicadas.

**Quatro testes que já vinham quebrados foram consertados** — três deles quebrados *antes* desta rodada, o que foi verificado guardando o trabalho e rodando a suíte no estado anterior:

- Dois testes do fluxo de 5 passos usavam um edital de laboratório com prazo fixo em `30/09/2026`. Em 23/09 sobravam sete dias, o conselho decidia "regularizar antes" — **a decisão correta** para seis documentos pendentes e uma semana de prazo — e a suíte acusava falha num fluxo intacto. O prazo do laboratório passou a ser relativo a hoje: o que se mede é a decisão do conselho, não o calendário.
- O teste dos motores lia um arquivo gerado em 15/09 e cobrava que hoje não aparecesse como "futuro". O arquivo estava velho; foi regenerado.
- Um teste meu de 15/09 fixava o nome da base mais recente em vez da regra. A regra é "a mais recente vence", não "a de 15/09 vence"; agora cobra a ordem por recência.

`scripts/verificar_privacidade.py`: **privacidade pública verificada**.
