## Parecer do conselho — 24/09/2026

*Conselho técnico de sete posições sobre os números acima. O parecer é datado: regenerar o
relatório atualiza os capítulos, mas as decisões abaixo são de 24/09.*

**1. Extremamente pessimista — chief engineer.** Dos 30 motores, só 10 produzem algo que sobrevive à triagem, e o maior deles, o PNCP, descarta 74% do que traz: 433 de 587 registros. O sistema gasta a maior parte do esforço de leitura numa única fonte ruidosa, e quatro das fontes mais valiosas de Goiânia — Diário do Município, TJGO, TRF1 e Câmara — não rendem nada pela nuvem.

**2. Pessimista — staff engineer.** O Diário Oficial de Goiás é lido cinco vezes por cinco motores. Isso não é redundância de segurança: é desperdício de cota num site que já registra recusas, e cinco motores quebram juntos no dia em que o diário mudar de formato.

**3. Levemente pessimista — professor de engenharia de software.** Três motores — `motor-gife`, `motor-patrocinio`, `piloto-aberto` — entraram no sistema depois da auditoria e nunca foram medidos como os outros. Um motor sem medição fica fora de qualquer decisão, e é exatamente por isso que tende a ficar para sempre.

**4. Neutro — CTO (ponderador).** O relatório não autoriza eliminar nenhum motor hoje, e isso é um resultado, não uma omissão: quem parecia morto era motor de coleta local sendo julgado pela nuvem, motor de insumo sendo julgado por achado, ou motor com três dias de vida. O que ele autoriza é **redistribuir trabalho**:

- **PNCP (`pncp-api`) — afinar o filtro na captura.** As correções M1 a M3 do parecer de 23/09 (abrangência antes de verificar, território no objeto, requisito de habilitação) passam a rodar na entrada do motor, não depois. Meta: cair de 74% para menos de 40% de eliminação.
- **Diário Oficial de Goiás — um motor lê, os outros recebem.** `do-goias` passa a ser o único leitor de `diariooficial.abc.go.gov.br`; `plat-ovg`, `plat-fapeg`, `plat-fundos-estaduais-go` e `plat-secult-go` ficam só com os seus domínios próprios e recebem do diário o que casar com o léxico de cada um.
- **Coleta local — os quatro que recusam a nuvem.** `do-goiania`, `dje-tjgo`, `dj-trf1-go` e `camara-goiania-pl` passam para o computador do titular. São as fontes mais próximas de Goiânia; não há substituto para elas.
- **Reativar — os que produzem mas não rodam todo dia.** `plat-abcr` e `plat-observatorio-3setor` trazem 14 e 20 registros com eliminação de 0% e 5% — os melhores números fora do PNCP — e rodaram 6 de 20 dias. Descobrir por que param é a tarefa de maior retorno da lista.
- **Medir os três motores de empresas** na próxima auditoria.
- **Observar os cinco motores novos** até 08/10 antes de julgar o léxico.

**5. Levemente otimista — professor de ciência da computação.** O quadro mostra onde cada motor para, e em quase todos o ponto de parada é operacional — agenda, rota, local de coleta — e não de concepção. Isso é conserto de configuração, não reconstrução.

**6. Otimista — staff engineer.** Fora do PNCP, os motores que funcionam eliminam quase nada: ABCR 0%, Observatório 5%, Secult 22%, DO-GO 0%. As fontes do terceiro setor e do governo estadual trazem pouco, mas trazem certo. O problema é de volume, não de qualidade.

**7. Extremamente otimista — CTO.** Com a fusão do Diário de Goiás, o filtro na entrada do PNCP e a coleta local das quatro fontes de Goiânia, o sistema passa a ler menos e achar mais. É a primeira vez que se pode dizer, motor por motor, o que cada um custa e o que cada um devolve.

### Tarefas direcionadas, em ordem de retorno

| # | tarefa | motores | onde para hoje |
|---|---|---|---|
| 1 | descobrir por que param e fazê-los rodar todo dia | `plat-abcr`, `plat-observatorio-3setor` | agenda |
| 2 | levar para o computador do titular | `do-goiania`, `dje-tjgo`, `dj-trf1-go`, `camara-goiania-pl` | leitura |
| 3 | filtro de abrangência e objeto na captura | `pncp-api` | triagem (74% eliminado) |
| 4 | um leitor só para o Diário Oficial de Goiás | `do-goias` + 4 `plat-*` estaduais | sobreposição |
| 5 | incluir na auditoria e na validação | `motor-gife`, `motor-patrocinio`, `piloto-aberto` | sem medição |
| 6 | reavaliar em 08/10 | 5 motores novos em observação | léxico (amostra curta) |
