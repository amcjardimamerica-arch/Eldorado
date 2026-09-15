# Relatório do agente semanal — Eldorado / Farol de Alexandria

**Data:** 13/09/2026 (domingo, 03h — rotina automática)
**Escopo:** editais abertos com possibilidade de atuação em Goiás ou no Brasil, para as associações cadastradas.

---

## 1. Editais no pacote

O gerador de pacote (`src.enquadramento pacote 25`) varreu o universo de **409 editais** do banco e devolveu
**7 pendentes**. Os outros já estavam analisados (40 com selo próprio) ou são **256 edições de diário sem ato
extraído**, que não são editais e seguem em bloco próprio.

A regra do titular — não repetir análise de edital já completo — foi respeitada: nenhum dos 7 tinha análise
fechada. Todos os 7 foram analisados nesta execução.

| # | ID | O que é | Selo | Itens |
|---|---|---|---|---|
| 1 | `71f1af059c45f010339a` | Novo Gama/GO — credenciamento de empresa de construção civil | Inconformidade | 6/12 |
| 2 | `5b991f651a1905c579de` | Alvorada do Norte/GO — Chamamento 003/2023, agentes culturais de audiovisual | Inconformidade | 6/12 |
| 3 | `db310a0fc81e8c860adc` | Alvorada do Norte/GO — Chamamento 004/2023, demais áreas culturais | Inconformidade | 6/12 |
| 4 | `9d21d4e6a4ccab244aed` | Secult-GO — errata e retificação de cronograma dos Editais PNAB nº 4 e nº 6 | Inconformidade | 12/12 |
| 5 | `6a6c37dcb037c09baa6c` | Secult-GO — lista de aprovados e suplentes do Edital de Infância e Juventude | Inconformidade | 6/12 |
| 6 | `db0bf83f4df2fe2c618a` | Secult-GO — retificação de cronograma dos Editais PNAB nº 12, 13 e 14/2026 | Análise incompleta | 6/12 |
| 7 | `ea14b1b3f360d2dc8637` | Instituto Impactarte — edital contínuo, até R$ 150 mil, nacional | Análise incompleta | 11/12 |

---

## 2. Completos 12/12

**Um:** o `9d21d4e6a4ccab244aed`, e por caminho legítimo — os seis itens que faltavam foram marcados como
**dispensáveis com motivo**, porque o registro é um ato de errata de cronograma e não uma chamada de
inscrição: não há prazo, valor ou requisito a preencher. O selo, ainda assim, é de Inconformidade, pelo
motivo da seção 4.

Nenhum outro fechou os 12 itens. Nenhum prazo, valor ou requisito foi estimado para completar quadro:
onde não havia base no texto do edital ou no regramento, ficou **null** e está dito abaixo o que falta.

---

## 3. Incompletos e o que falta

### `ea14b1b3f360d2dc8637` — Instituto Impactarte *(a melhor oportunidade do pacote)*

Chamada **nacional**, privada, em **fluxo contínuo**, com aporte direto de **até R$ 150 mil** por iniciativa,
sem incentivo fiscal. Aderência **82** para a A.M.C. Jardim América; chances **45**.

Onze dos doze itens preenchidos. **Falta: Anexos** — e, fora dos doze, falta a **lista de documentos exigidos**
no cadastro, que é o que impede o selo de Conformidade.

Atenção à origem dos dados: o robô **não obteve o regulamento na fonte oficial**. A página do próprio
Instituto (`impactarte.org.br/cadastro-proponente`) não devolveu o texto à leitura automatizada. Requisitos,
critérios e valor vieram da matéria do Observatório do Terceiro Setor, que é **veículo de divulgação, não
fonte**, e estão marcados como tal no parecer. **Fonte a consultar:** https://www.impactarte.org.br/cadastro-proponente

Os cinco requisitos divulgados são todos cumpridos pela associação, inclusive o mais restritivo — três anos de
existência, contra os **43 anos** que ela tem.

### `db0bf83f4df2fe2c618a` — PNAB 2026, Editais nº 12, 13 e 14 (Secult-GO)

Faltam **seis itens**: prazo de inscrição, resultado, prazo de recurso, valor, requisitos e anexos. O robô não
obteve o edital na fonte: `goias.gov.br` retornou erro nesta rota e o texto capturado antes era o comunicado de
suspensão de notícias por legislação eleitoral, não o ato.

**Por que continua vivo, e os outros PNAB não:** aqui não há prova de encerramento. Os Editais nº 12, 13 e 14
não aparecem entre os certames com resultado publicado na página oficial capturada, e retificação de cronograma
frequentemente desloca a janela de inscrição para a frente. Aderência provisória **55**, apoiada só no que está
confirmado — edital estadual de Goiás, área de cultura, dirigido a agentes culturais e OSCs goianas.

**Fonte a consultar:** `goias.gov.br/cultura`, página *Editais 2026 – PNAB*.

### Os cinco restantes

Ficaram em 6/12 por opção deliberada: são registros descartados, e completar campos de um edital que não
serve seria trabalho perdido e risco de dado inventado.

---

## 4. Dispensados e o motivo

Cinco registros foram marcados **"dispensado"** em `dados/associacoes/amc-jardim-america/decisoes_editais.json`
(o arquivo passou de 12 para 17 entradas) e receberam selo de **Inconformidade**, o que os move
automaticamente para a aba **Arquivados — Encerrados / Descartados** do painel:

1. **Novo Gama/GO** — o objeto declarado pelo Município é credenciamento de **empresa do ramo da construção
   civil** para construir unidades habitacionais em área municipal. É contratação de obra por pessoa jurídica
   empresária, não repasse a entidade sem fins lucrativos. Não há previsão de parceria da Lei 13.019/2014.

2. **Alvorada do Norte/GO, Chamamento 003/2023** — seleção de agentes culturais de audiovisual **do próprio
   município**, em ciclo de 2023. A associação atua em Goiânia, a cerca de 350 km, e não é elegível.

3. **Alvorada do Norte/GO, Chamamento 004/2023** — edital irmão do anterior, demais áreas culturais. Mesmo
   motivo.

4. **Errata dos Editais PNAB nº 4 e nº 6** — a página oficial de Editais 2026 – PNAB, capturada na íntegra,
   mostra que os dois certames já passaram da inscrição: constam **Classificados e Desclassificados** das
   Categorias A e B do nº 04 e das Categorias A a E do nº 06, além da 6ª Retificação de Cronograma de
   01/09/2026. O que resta é andamento de resultado, não janela de captação.

5. **Lista de aprovados e suplentes do Edital de Infância e Juventude** — resultado de certame já julgado,
   confirmado pela mesma página oficial. Não há inscrição a fazer.

Nenhum registro foi marcado como "inscrição realizada" — isso é decisão do titular.

---

## 5. Dois defeitos de dado corrigidos

A suíte acusou duas falhas na primeira passagem. Ambas eram **defeito de dado**, e o dado foi corrigido — o
teste, não.

**a) Material de veículo guardado como texto de edital.** Quatro arquivos em `dados/editais/textos/` guardavam
o *Midia Kit* do Observatório do Terceiro Setor em vez do edital — exatamente o que a regra `serve_como_fonte`
de `src/fonte_edital.py` proíbe. São arquivos antigos, anteriores à regra. Removidos:
`f359e425734cf4682571`, `c5c7e37e2e275d2e69fe`, `ea14b1b3f360d2dc8637`, `295af6bb3f2da0a2be71`.

**b) O dia de hoje aparecia como "futuro" no monitor do DOU.** `docs/dados/motores.json` estava congelado em
12/09. Regenerado com `python -m src.motores`; 13/09 saiu de "futuro" para "cinza".

**Depois da correção: 220 testes verdes** (`OK (skipped=1)`, 307s) e `verificar_privacidade.py` limpo.

---

## 6. O que ficou para o titular decidir

1. **Abrir `impactarte.org.br/cadastro-proponente` no navegador** e capturar regulamento, documentos exigidos e
   etapas de seleção. É o único item que falta para a análise ficar completa, e a melhor oportunidade do
   pacote. O fluxo contínuo elimina a pressão de prazo — dá para preparar bem antes de submeter.

2. **Abrir `goias.gov.br/cultura`, página Editais 2026 – PNAB**, e capturar objeto e cronograma retificado dos
   Editais nº 12, 13 e 14/2026. Se as inscrições estiverem abertas, é oportunidade estadual em Goiás na área de
   cultura, onde a associação é elegível por território e por estatuto.

3. **Decidir sobre a inscrição no Impactarte.** A recomendação do parecer é inscrever, depois de conferir o
   regulamento na fonte. O que precisa ser montado antes: dossiê de impacto com números de três anos,
   demonstrações financeiras recentes e a narrativa dos 43 anos de atuação contínua no Jardim América, Nova
   Suíça e Conjunto Oásis.

4. **A entrega desta semana é patch, não commit.** O `git push` foi negado de novo pelo proxy da sessão
   (*"not in this session's authorized repository set"*), como em 12/09. As alterações estão commitadas
   localmente e exportadas em `PATCH-agente-semanal-2026-09-13.patch`. Para o push sair, a rotina precisa ser
   recriada em `claude.ai/code/routines` **com o repositório Eldorado selecionado**, ou uma sessão aberta por
   `claude.ai/code?repositories=amcjardimamerica-arch/Eldorado` precisa aplicar o patch.

---

## 7. Números do acervo depois desta execução

| | |
|---|---:|
| Editais com selo de análise | **771** |
| Conformidade | 146 |
| Inconformidade (arquivados) | 506 |
| Análise incompleta | 119 |
| Editais abertos no enquadramento | 139 |
| Universo varrido no pacote | 409 |
| Edições de diário sem ato (bloco próprio) | 256 |
