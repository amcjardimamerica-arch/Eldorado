# Relatório de melhoria dos motores de busca — Verificação 2026-11-05, Grupo 2 (partes 9–16)

Resultado: 400 livros — 14 valido, 50 encerrada, 23 arquivar, 313 descartar (78% de ruído).

## Regras sugeridas (por impacto)
1. **gov.br institucional (~170 livros):** bloquear na entrada URLs com /composicao/, /acesso-a-informacao/, /assuntos/, /servicos/, /temas/, /navegue-por-temas, /canais_atendimento/, /orgaos-do-governo, /por-dentro-do-govbr/, /noticias, /transparencia, /Defeso/, ?origem=. Exigir no CORPO (não no menu) "edital", "chamamento" ou "inscrições" + link para PDF.
2. **Replicador CapitaAI (~125 livros):** não gerar livro a partir do guia; usar o guia só para extrair o link oficial. Descartar na entrada guias com "encerrado" no título.
3. **Público errado:** filtrar FAPs/CNPq/FAPESP (pesquisador/ICT), compras PNAE/PAA, credenciamentos de saúde, locação de imóvel, empresas/startups, bolsas a pessoa física.
4. **Abrangência:** município de outro estado que não é capital → descartar automático por UF+IBGE antes da verificação.
5. **Notícias antigas (Fundo Brasil, GIFE, Fundo Casa 2001–2024):** filtrar por data de publicação < 12 meses.
6. **Anexos isolados (formulários, FAQ, pareceres de recurso):** vincular ao edital-mãe ou descartar.
7. **Duplicatas:** deduplicar por URL normalizada e por (financiador, nº da chamada).

## Fontes que funcionaram
- curl + pdftotext em PDFs oficiais; FUNBIO: regulamento em base64 no __NEXT_DATA__.
- Leis: camara.leg.br quando planalto.gov.br não responde.
- Prosas (página oficial da chamada) para editais privados.

## Fontes problemáticas (conferir manualmente)
- casa.org.br (Fundo Casa) bloqueia robôs → trechos via WebFetch: conferir no navegador.
- pesquisa.in.gov.br (DOU) sem resolução DNS no ambiente.
- Portal de Belém fora do ar (L-f6a39eaeaff63574 pode virar encerrada).
