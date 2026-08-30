# Catálogo de formas de captação

Esta árvore separa as pistas do acervo por **nível** e **tipo de captação**. Cada pasta contém um `catalogo.json` gerado da planilha anexada. Um mesmo item pode aparecer em mais de um nível quando a própria descrição combina Município, Estado, União ou fonte privada.

## Regra de prova

- `pista_do_acervo_pendente_url_primaria`: serve para orientar o mapeamento, mas não é oportunidade aberta.
- `capturada`: o robô localizou menção em uma fonte catalogada.
- `verificada_primaria`: existe página ou documento oficial do edital, com evidência e data de consulta.
- `verificada_dupla`: além da fonte primária, há pista independente no canal social oficial ou em plataforma de terceiro setor.

Valores do anexo ficam em `valor_texto_nao_verificado`. Eles não são usados no dashboard como valores atuais até confirmação.

## Níveis

- `municipal`: chamamentos, fundos, emendas e incentivos municipais.
- `estadual`: programas, fundos, emendas e incentivos estaduais.
- `federal`: Transferegov, ministérios, fundos e incentivos federais.
- `privada`: empresas, fundações, plataformas, doações e patrocínios.
- `internacional`: portais multilaterais, fundações e grants.
- `a_validar`: classificação que exige revisão humana.

O arquivo consolidado é `catalogo_anexo.json`; a reprodução é feita por `scripts/importar_catalogo_captacao.py`.
