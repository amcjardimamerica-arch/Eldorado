# Skills dos Pilotos (29/09/2026)

Pacotes pequenos por tarefa, carregados só na missão que precisa (src/skills/__init__.py). Instrução ≤500 tokens; o que é mecânico é código.

- **comum/leitura_pdf** — Abrir e ler PDF (texto e tabelas) e buscar expressões com o contexto em volta — a identificação mais importante.
- **comum/aprendizado_resultado** — A cada 100 erros de um Piloto, mede onde falhou e grava parâmetros de busca melhores.
- **espiao/descobrir_entidades_novas** — Descobrir empresas, institutos, fundações e entidades ligadas ao terceiro setor que NÃO estão no cadastro.
- **espiao/triagem_indicio** — Triagem antes de entregar uma candidata: é oportunidade para associação do terceiro setor?
- **interceptador/cronograma** — Mapear inscrição, resultado e recurso a partir do cronograma do edital (quase sempre tabela em PDF).
- **interceptador/site_oficial** — Achar o site oficial do financiador (nunca o republicador), na ordem das rotas que funcionam.
- **interceptador/dossie_empresa** — Dossiê investigativo de empresa do cadastro: composição, contatos, projetos e atuação no terceiro setor.
