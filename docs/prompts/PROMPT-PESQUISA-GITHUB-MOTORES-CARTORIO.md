# Pesquisa em repositórios públicos do GitHub — melhorias para os motores de busca e o Cartório (14/10/2026)

## Finalidade
Encontrar, em repositórios públicos, soluções já testadas para os erros CONHECIDOS do Eldorado (análise do sistema e
treino dos motores) e aplicá-las com ganho MEDIDO — não por regra, mas pelo treino com casos conhecidos.

## Erros conhecidos que orientam a busca
1. Fonte oficial: replicadores (Querido Diário, PNCP, CapitaAI…) sem link para a fonte; Querido Diário 17/41 no treino
   (a API do projeto devolve só a cópia; o site da prefeitura é adivinhado pelo padrão município.uf.gov.br).
2. PDF do edital: só 23% dos casos chegam à fonte E ao PDF.
3. Cartório: 69% dos itens certificados; os que mais faltam são prazo de recurso, resultado, prazo de inscrição, valor,
   anexos e requisitos (extração de datas, valores e seções em texto de edital).
4. Validação: 10% das abertas validadas; 441 sem prazo conhecido.
5. Leitura de páginas: conteúdo principal misturado com menus e rodapés; PDFs escaneados.

## Onde procurar (em ordem)
1. Querido Diário (okfn-brasil): os raspadores de cada município trazem o ENDEREÇO OFICIAL do diário de cada cidade.
2. Clientes e documentação da API do PNCP (arquivos da contratação, link de origem).
3. Extração de datas, valores e prazos em português (bibliotecas e expressões testadas em documentos públicos).
4. Extração do conteúdo principal de páginas e de texto/tabelas de PDF (inclusive escaneados).
5. Projetos de raspagem de licitações, editais e diários oficiais brasileiros.

## Critérios
Repositório ativo, licença aberta, testado em dados públicos brasileiros; preferir DADOS (endereços, padrões) e
técnicas pequenas a dependências pesadas; cada adoção precisa de ganho medido no treino (fluxo 38) ou nos testes.

## Entrega
Relatório com os repositórios avaliados, o que foi adotado e por quê, e o ganho medido antes × depois.
