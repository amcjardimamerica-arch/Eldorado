# Skills dos Pilotos (29/09/2026)

Pacotes pequenos por tarefa, carregados só na missão que precisa (src/skills/__init__.py). Instrução ≤500 tokens; o que é mecânico é código.

- **comum/leitura_pdf** — Abrir e ler PDF (texto e tabelas) e buscar expressões com o contexto em volta — a identificação mais importante.
- **comum/aprendizado_resultado** — A cada 100 erros de um Piloto, mede onde falhou e grava parâmetros de busca melhores.
- **espiao/descobrir_entidades_novas** — Descobrir empresas, institutos, fundações e entidades ligadas ao terceiro setor que NÃO estão no cadastro.
- **espiao/triagem_indicio** — Triagem antes de entregar uma candidata: é oportunidade para associação do terceiro setor?
- **interceptador/cronograma** — Mapear inscrição, resultado e recurso a partir do cronograma do edital (quase sempre tabela em PDF).
- **interceptador/site_oficial** — Achar o site oficial do financiador (nunca o republicador), na ordem das rotas que funcionam.
- **interceptador/dossie_empresa** — Dossiê investigativo de empresa do cadastro: composição, contatos, projetos e atuação no terceiro setor.

## Skills dos motores (02/10/2026)

Uma por família de fonte + duas comuns; o vínculo motor → skill fica em config/skills_motores.json.

- **motores/diario_oficial** — Ler diário oficial (municipal, estadual, da União, da Justiça) e achar o ato que abre recurso para OSC.
- **motores/portal_chamamentos** — Ler portais de chamamentos e contratações públicas (PNCP, SALIC, Mapa das OSC, portais de prefeituras).
- **motores/orgao_publico** — Ler sites de órgãos públicos (secretarias, autarquias, fundações, conselhos, fundos, Congresso).
- **motores/justica_mp** — Ler Justiça e Ministério Público (destinação de penas pecuniárias, TAC, reparação).
- **motores/terceiro_setor** — Ler sites especializados no terceiro setor (ABCR, Observatório, agregadores, GIFE, recorrência).
- **motores/entidades** — Ler sites de institutos, fundações e outras entidades financiadoras.
- **motores/empresas** — Ler sites empresariais e buscar linhas de captação de empresas, mesmo sem publicação.
- **motores/pilotos** — Pilotos (Espião e Interceptador): buscar oportunidades FORA dos canais e confirmar na fonte oficial.
- **comum/linha_producao** — Contrato comum da linha de produção: o que todo canal entrega e o que nunca pode acontecer.
- **comum/leitor_documental** — Abrir o site oficial e os arquivos do edital e extrair os 12 itens do documento; notícia é só indício (03/10/2026).
- **comum/plano_correcao** — Roteiro dos planos de correção: diagnosticar o canal e aplicar o plano previsto no fluxograma.

## Esteira de selos (02/10/2026)

Bronze → Prata → Ouro, conduzida pelo maestro (src/maestro.py); o Interceptador local executa bronze (Sonnet 5.5) e prata (Opus 5.5), esforço baixo. Ver docs/arquitetura/esteira-de-selos.md.
