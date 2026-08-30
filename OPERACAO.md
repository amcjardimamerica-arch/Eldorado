# Operação

## Comandos

```bash
python -m src.executar_diario
python -m src.sentinela
python -m src.executar_farol
python -m unittest discover -s tests -v
python scripts/importar_acervo.py entrada_acervo
python scripts/importar_catalogo_captacao.py planilha.xlsx
python scripts/criar_associacao.py SLUG "Nome da associação"
python scripts/ingestao_associacao.py SLUG documento.docx
```

## Estados de uma oportunidade

`pista_do_acervo_pendente_url_primaria` → `capturada` → `verificada_primaria` ou `verificada_dupla` → `elegivel` ou `inelegivel` → `em_preparacao` → `submetida` → `selecionada` ou `nao_selecionada` → `em_execucao` → `prestacao_de_contas` → `encerrada`.

`src.executar_diario` não encaminha oportunidades apenas capturadas. Depois da revisão humana das evidências, a triagem pode abrir um caso isolado; `src.executar_farol` continua disponível para reavaliação manual.

Na operação automática, `src.executar_diario` chama uma triagem determinística. Somente oportunidades verificadas e com aderência mínima de 60/100 recebem caso no Farol; os demais itens permanecem no histórico para preparação futura da associação.

## Dossiê do financiador

O diretório individual reúne eventos comprovados dos últimos cinco anos, valor quando publicado, objeto, forma de acesso, público, território, requisitos recorrentes e links. “Padrão” só é promovido após duas ocorrências independentes; antes disso aparece como hipótese.

## Plano de trabalho e prestação de contas

O Farol gera checklist a partir do edital e do procedimento aplicável. A redação final deve preservar a estrutura exigida pela fonte, conter indicadores mensuráveis, cronograma, memória de cálculo, matriz de riscos e plano de evidências. A prestação de contas nasce junto com o plano: cada meta define desde o início qual documento provará sua entrega.
