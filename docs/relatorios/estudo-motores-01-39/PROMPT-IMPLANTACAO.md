# Prompt de implantação — livros dos motores 24 a 39 e correções dos motores 01 a 39

> Cole este texto numa sessão do Claude com acesso de escrita ao repositório `amcjardimamerica-arch/Eldorado` e anexe o .zip.

Siga o `CLAUDE.md`. O titular não programa: não faça perguntas técnicas, execute tudo e explique em português simples. Termine com commit em uma branch `claude/livros-motores-24-39`, Pull Request e o link.

## 1. Livros (semente)

1. Copie `livros_motores_24_39.json` para `dados/oportunidades/livros_motores_24_39.json`.
2. Em `src/livros_regra.py`, acrescente uma segunda semente, igual a `_aplicar_semente`, controlada pela `versao` do arquivo e aplicada uma vez só.
   - Passe para `registrar_achados` somente os itens com `acao == "criar_livro"`.
   - Leve juntos os campos `prazo`, `publicado_em`, `url` (site oficial), `orgao`, `uf` e `valor`.
   - Grave em cada livro `estado_semente` e `aplicavel_amc`.
3. **Itens com `estado == "encerrado_arquivar"`:** o livro nasce **arquivado**. Use o mesmo mecanismo que já arquiva livros com prazo vencido. A edição fica no histórico e alimenta a previsão.
   - Não apague nada.
   - Território não é veto: a aplicabilidade é só enquadramento.
4. **Itens com `acao == "aguardar_fonte"`:** não viram livro. Entram na fila do Interceptador com `pagina_agregador`, para que ele confirme o site oficial.
5. Os resultados esperados no primeiro ciclo estão no cabeçalho do arquivo (`totais`): 654 livros, sendo 23 abertos, 28 sem data e 603 arquivados, e 435 na fila.

## 2. Correções transversais (prioridade 1)

1. **Leitor de datas único** (`src/indexadores/extracao.py` e os leitores de feed, listagem e WordPress):
   - o ano vem do texto; se o texto não traz o ano, vem da data de publicação, com checagem de faixa;
   - nunca usar "próximo ano futuro";
   - em "de X a Y", o prazo é Y.
   - Reprocesse os indícios de `estado/indexadores/indicios.json` com prazo em 2027. Os motores afetados são 26, 28, 29, 31 e 32.
2. **Link oficial:**
   - extrair do corpo do texto, preferindo o link mais próximo de "edital", "inscrições" ou "acesse";
   - expandir bit.ly antes de avaliar;
   - descartar agregadores, formulários, rodapé, patrocinador e as páginas genéricas do gov.br;
   - validar que o domínio responde.
3. **Valor:** descartar "R$ 97" (CapitaAI) e valores copiados de outro item.
4. **Estado no painel:**
   - rota `None` → "sem rota";
   - API que devolve menos que o sitemap → "parcial";
   - "satisfatória" só quando houver item com prazo e link oficial válidos.

## 3. Rotas por motor

Use as URLs verificadas; os detalhes estão em `motores/NN-id/RELATORIO.md`, seção 1, e na seção 7, "Melhorias".

| Motor | Ação |
|---|---|
| 24 | `?per_page=50&page=N` até `total_pages`; estado pelo prazo, não pelo campo `status` |
| 25 | Rota `/captacao`, incluindo os encerrados, mais `/editais-abertos/para-ong`; o sitemap fica só como sentinela |
| 26 | Rotina com `feed/?paged=1..2`; carga única de histórico com `?paged=1..24` |
| 27 | API `opportunity/find` com `registrationTo=GTE`, no Mapa Goiano e no nacional; sem `owner.name`; acrescentar o Sistema Baru (PNAB GO) |
| 28 | `feed/?paged=N` até o último visto; carga de histórico com `1..31` |
| 29 | `editais-abertos` mais as pastas `/editais/AAAA`; descer às subpáginas; deduplicar pelo slug |
| 30 | Chave = código do programa; excluir repasses fundo a fundo; API Parcerias por ano; vigiar Pronon e Pronas em set–nov |
| 31 | `_editais?per_page=100&after=`, abrindo só os itens novos ou alterados |
| 32 | `/editais/` (estado) mais o RSS da categoria edital; resolver links bit.ly até editais.baoba.org.br |
| 33 | Sitemap mais 7 categorias; filtrar os domínios próprios; cadência mensal; rebaixar para "só descoberta" |
| 34 | `edital-sitemap.xml` mais a página de cada edital; janela diária de 25/11 a 20/12 |
| 35 | `wp-json/wp/v2/posts?search=&after=` mais `post-sitemap.xml`; filtrar vagas e notícias |
| 36 | 3 páginas fixas; leitura diária de outubro a março; chave = ano da janela |
| 37 | `wp/v2/search?subtype=chamadas` mais `?include=`; regex do prazo e do valor; filtro de abrangência |
| 38 | `wp-json/wp/v2/posts` com as buscas edital, selecionadas e chamada; estado "sem edital público desde 2023" |
| 39 | Manter a API; extrair o prazo do `content`; paginar pelo `X-WP-Total`; carga de histórico pelo sitemap. **Não usar identificação de IA** (o robots.txt proíbe o ClaudeBot) |

**Motores 01 a 23:** as correções estão em `RELATORIO-ROTAS-01-23.md`. Prioridades:

1. **08, 09 e 10:** separar as rotas copiadas. Use o estudo do motor 12.
2. **14:** criar as rotas WordPress das secretarias (`goias.gov.br/social` e `goias.gov.br/cultura`).
3. **17:** trocar pela rota `gov.br/cnpq/pt-br/chamadas/abertas-para-submissao`.
4. **06:** aplicar filtro de data nas APIs da Câmara e do Senado.
5. **05, 01, 16, 19 e 21:** corrigir os endereços.

## 4. Testes sem rede

1. Leitor de datas: os casos reais "19 de outubro" num post de 2026 devem dar 2026, nunca 2027.
2. Semente:
   - aplicada uma vez só;
   - os encerrados ficam arquivados;
   - `aguardar_fonte` não cria livro.
3. Link oficial: bit.ly, agregadores e gov.br genérico são rejeitados.

Depois rode:

- `python -m unittest discover -s tests` — só falha nova bloqueia;
- `python scripts/verificar_privacidade.py`.

Não commite os resíduos que os testes deixam em `estado/`, `docs/dados/` e `config/`.

## 5. Mensagem ao titular (modelo)

> "Apliquei o estudo dos motores 24 a 39. Entraram 654 livros com o site oficial: 23 abertos, 28 de fluxo contínuo e 603 encerrados, que ficaram arquivados como histórico. Outros 435 aguardam a confirmação da fonte pelo Interceptador. Corrigi o defeito que inventava o ano do prazo, que fazia editais vencidos aparecerem como abertos. Testes ok. Pull Request: <link>."
