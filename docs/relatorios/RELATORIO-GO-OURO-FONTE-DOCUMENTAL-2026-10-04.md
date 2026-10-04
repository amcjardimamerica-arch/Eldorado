# Livros de Goiás: ouro pela fonte documental (04/10/2026)

## Resultado
Dos 387 livros de Goiás, 226 foram declarados inaplicáveis (cada um com a prova e o livro-mãe, quando há) e 161 seguem válidos. Dos 161 válidos, 148 têm selo ouro (126 por série de edições lidas nos editais em 2 anos distintos, 22 por regime permanente documentado com base legal) e 13 não chegaram ao ouro:
- 10 com edição única comprovada, depois de buscar outros anos nos sites oficiais: Socioeducativo SEDS 001/2026, SECTI Cidadão Tech 60+, Alvorada do Norte 006/2026, Cine Goiás Itinerante, Blocos de carnaval, Cultura negra/quilombola/periferia, Bandas/corais/fanfarras, PNAB Goiânia subsídio de manutenção (Edital 12/2024), SEMASC Senador Canedo e o GO.IA da FAPEG. Programa novo não tem histórico para provar: o livro tem parecer completo e fica prata/bronze até o ano que vem.
- 3 com série real, mas só um ano dentro da janela de 3 anos do selo (a edição mais antiga é de 2022/2023): Fundo de Arte e Cultura, Auxílio Nutricional SEDS, Goiás Turismo R$ 2,5 mi e Fundo Municipal de Cultura de Anápolis (regulamentos 2021-2024). A série está lida e documentada nos pareceres; o selo só vira ouro se a titular aceitar janela maior para esses programas.

## O que mudou no sistema (os agentes nos motores)
- Skill `comum/leitor_documental` e contrato `config/leitor_documental.json`, carregados por todos os 152 motores (`config/skills_motores.json`): notícia é indício; os 12 itens saem do edital, regulamento, cronograma ou ata, com trecho literal, documento e página.
- `src/leitor_documental.py`: fila de Goiás, validação (item sem trecho ou sem documento vira indício; ouro exige 2 anos com documento; inaplicável exige prova; edição única exige o relato da busca) e aplicação. Testes em `tests/test_leitor_documental.py`.
- `src/sites_oficiais.py`: PDF/anexo em /wp-content/uploads/AAAA/MM/ deixou de ser tratado como notícia (era o que impedia o ouro dos editais da Secult).
- `src/selo_livros.py`: ouro por regime permanente documentado (campo `via`). `src/relatorio_livros.py`: parecer do livro, itens dispensados/pendentes por documento e `universo_go`.
- Método que funcionou nos agentes de navegador: PDF lido com pdf.js dentro de aba do próprio site; REST do WordPress (wp-json) para achar arquivos de editais quando as notícias do goias.gov.br estão suspensas pelo período eleitoral.

## Conselho de 7 lentes
Extremamente pessimista: 226 inaplicáveis é muito; parte (59 fora de perfil, 46 sementes) foi decidida por triagem, com prova fraca em alguns (ex.: conselho CEDHIRCOP sem PDF). Pessimista: alguns trechos vieram de resumo do WebFetch e de OCR, e PDFs de 2026 sem texto foram transcritos de imagem; o ouro de Goiás Turismo depende de aceitar 2021/2023/2025 como o mesmo programa. Levemente pessimista: 22 ouros por regime têm evidência frágil em casos como Fundo do Idoso e FIA (base federal, lei estadual não lida). Neutro: manter os 148 ouros, marcar `via` e confiança, auditar por amostra de 10% os trechos e reler no IP do titular os PDFs ilegíveis; tratar as 10 edições únicas como programas novos a monitorar. Levemente otimista: 1.364 itens agora têm trecho e documento. Otimista: o leitor documental passa a valer para todos os motores. Extremamente otimista: com a fila e a validação prontas, BR e INT repetem o método.

## Limites declarados
O repositório do GitHub não pôde ser lido nesta sessão: o trabalho foi feito sobre a cópia local de 03/10 e as atualizações de dados que a titular fez depois não entraram. O PNCP respondeu 503 em parte da leitura. Nada foi enviado ao GitHub.
