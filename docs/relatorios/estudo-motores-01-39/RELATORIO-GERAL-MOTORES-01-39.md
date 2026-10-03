# Relatório geral — rotas dos motores 01 a 39 e extração de 3 anos dos motores 24 a 39

**Data:** 02/10/2026
**Associação:** A.M.C. Jardim América (Goiânia/GO)
**Sistema:** Eldorado, painel com 49 motores, ordem `config/ordem_motores.json` v2026-10-02.2. A ordem foi conferida no painel aberto no navegador do titular.

**Método:**

- Um motor por vez. O próximo só começou depois que o anterior entregou o relatório e os livros.
- Leitura pelo WebFetch, fora do Brasil, respeitando o robots.txt. Sem login, sem formulário.
- O conteúdo das páginas foi tratado como dado.

**Prompt executado:** `PROMPT-AUDITORIA-01-39-E-EXTRACAO-24-39.md`.

**Prompt injection:** nenhuma instrução dirigida a IA foi encontrada nas páginas lidas.

---

## 1. Em uma página

1. **Rotas 01 a 23:** detalhes em `RELATORIO-ROTAS-01-23.md`.

   | Situação | Quantos | Motores |
   |---|---|---|
   | Funcionam | 3 | 02, 15, 18 |
   | Funcionam em parte | 7 | 01, 06, 16, 20, 21, 22 e 13 |
   | Bloqueados na nuvem | 3 | 03, 04, 11 |
   | Rota errada | 4 | 05, 12, 17, 19 |
   | Nunca rodaram | 4 | 07, 08, 09, 10 |
   | Sem rota | 2 | 14 e 23 (o 23 é interno) |

   - **Gravíssimo:** os motores 08, 09 e 10 (Ministérios Públicos) têm as **mesmas 22 rotas copiadas**, e o 08 não tem nenhuma rota do próprio MP-GO.
2. **Rotas 24 a 39:** os 16 motores aparecem como **"satisfatória"** no painel, mas **12 deles têm defeito**. O principal se repete em vários leitores: **o ano do prazo é inventado**. Quando a página traz só "dia de mês", o leitor joga para o próximo ano futuro. Por isso, editais encerrados aparecem como **abertos com prazo em 2027**. Confirmado em:
   - 26 Observatório: 28 de 42 indícios;
   - 28 ABCR: 10 de 10;
   - 29 Funarte: 8;
   - 31 Rede Comuá: 3 de 5;
   - 32 Baobá: 4 de 4.
3. **Outros defeitos que se repetem:**
   - **Link "oficial" errado:** aponta para rodapé ou patrocinador, outro agregador, encurtador ou página de segurança.
   - **Financiador vazio:** o campo não vem preenchido.
   - **Valor lixo:** "R$ 97", que é o preço da assinatura do CapitaAI; "US$ 20 mil" copiado entre itens.
   - **Chave errada no Transferegov:** o código do órgão é usado no lugar do código do programa.
   - **Rota `None`:** em 29, 32, 33, 36 e 38 o motor lê só a home.
   - **API que devolve só 2 itens:** no 34 Fundo Brasil, a API ignora os filtros.
4. **Extração de 3 anos (24 a 39):** **1.130 oportunidades** extraídas, que resultam em **1.089 registros** depois de juntar duplicatas entre motores. Cada registro tem o site oficial, ou fica marcado para aguardar a fonte. Ficam assim:
   - **654 livros** com site oficial de publicação:
     - 23 abertos;
     - 28 sem data ou de fluxo contínuo;
     - **603 encerrados, que vão para os livros como ARQUIVADOS**, servindo de histórico e de previsão da próxima edição.
   - **435 aguardando fonte:** o agregador não trouxe o site do financiador, então não viram livro até a confirmação (regra DI-05).
5. **Histórico curto em agregadores novos:**
   - O Farol Cultural tem cerca de 8 meses de acervo.
   - O CapitaAI existe desde 18/08/2026.
   - O "3 anos" só existe completo nos financiadores, que são os motores 29, 31, 32, 34, 36, 37 e 38, e nos feeds paginados do Observatório e da ABCR.
6. **CESE (39):** o robots.txt da CESE proíbe o **ClaudeBot** (`Disallow: /`) e libera os demais robôs. O estudo não leu o site. O motor do sistema, que se identifica como robô próprio, pode fazer a carga do histórico pelo sitemap.

---

## 2. Motores 24 a 39, um a um

| nº | Motor | Rota hoje | Histórico 3 anos (abertas / encerradas / sem data) | Aplicáveis à A.M.C. (sim / depende) | Diagnóstico | Rota melhor (verificada) |
|---|---|---|---|---|---|---|
| 24 | Farol Cultural | API ok | 504 (30 / 456 / 18). Acervo começa em fev/2026 | 2 / 29 | Funciona. Estado vem do campo status, que contradiz o prazo; léxico vazio deixa entrar ruído | `api/v1/editais?per_page=50&page=N` até `meta.total_pages` |
| 25 | CapitaAI | sitemap corta em 400 URLs | 20 confirmadas (10 / 7 / 3). Site existe desde ago/2026 | 1 / 5 | Parcial. 182 sem link oficial; valor "R$ 97" | `capitaai.com.br/captacao`, com os 553 guias, incluindo 195 encerrados |
| 26 | Observatório 3º Setor | feed ok, só ~6 semanas | 153 (13 / 111 / 29) | 18 / 94 | **Prazo com ano inventado**; financiador vazio | `…/editais/feed/?paged=1..24` |
| 27 | Mapas Culturais | `None` | 97 (6 / 88 / 3) | 14 / 47 | Parcial. Mapa Goiano quase parado: PNAB-GO foi para o Sistema Baru | `/api/opportunity/find?...&registrationTo=GTE(data)` (Mapa Goiano e nacional). Não usar `owner.name` (LGPD) |
| 28 | ABCR | feed ok | 159 (6 / 145 / 8) | 34 / 64 | **Prazo com ano inventado** (10/10); links errados | `captadores.org.br/category/editais/feed/?paged=1..31` |
| 29 | Funarte | `None` | 25 (0 / 15 / 10) | 0 / 21 | **Prazo com ano inventado**; programas-mãe sem subpáginas | `gov.br/funarte/.../editais-abertos` mais as pastas `/editais/2023..2026` |
| 30 | Transferegov | ZIP mais API | 17 (5 / 12 / 0) | 0 / 10 | **Chave errada** (órgão no lugar do programa); OSC falso em repasses fundo a fundo | API Parcerias `?ano_programa=AAAA&pagina=N` mais páginas de chamamento dos ministérios |
| 31 | Rede Comuá | API vê só 10 | 86 (1 / 85 / 0) | 2 / 57 | **Início lido como prazo e ano inventado** | `wp-json/wp/v2/_editais?per_page=100&after=` |
| 32 | Fundo Baobá | `None` | 9 (0 / 8 / 1) | 0 / 2 | **4 de 4 achados falsos** (prazo em 2027) | `/editais/` (estado) mais RSS `category/edital/feed/` |
| 33 | Editais Culturais | `None` | 34 (1 / 31 / 2) | 0 / 2 | **Portal comercial**, com concursos próprios pagos para pessoa física | sitemap mais 7 categorias; cadência mensal; rebaixar para "só descoberta" |
| 34 | Fundo Brasil | API devolve 2 de 24 | 24 (0 / 23 / 1) | **3** / 18 | API ignora filtros | `edital-sitemap.xml` (85 URLs) mais a página de cada edital |
| 35 | IDIS | feed defasado | 10 (2 / 8 / 0) | 3 / 4 | 90% do feed é notícia ou vaga | `wp-json/wp/v2/posts?search=&after=` mais `post-sitemap.xml` |
| 36 | UNDEF | `None` (home) | 3 (0 / 2 / 1) | 0 / 3 | Uma chamada por ano, em inglês ou francês, com mínimo de US$ 100 mil | 3 páginas fixas (apply-for-funding, when-apply, node/310) |
| 37 | Fundo Casa | API ok, devolve 10 | 32 (0 / 31 / 1) | 0 / 14 | Painel subestima: 1 achado contra 32 chamadas | `wp/v2/search?subtype=chamadas&per_page=100` mais `?include=id` |
| 38 | BrazilFoundation | `None` | 3 (0 / 3 / 0) | 2 (seleções) | Sem edital público desde 2023; usa carta-convite em 2026 | `wp-json/wp/v2/posts?search=edital/selecionadas/chamada` |
| 39 | CESE | API (nuvem do sistema ok) | não extraído: o robots.txt proíbe o ClaudeBot | — | Campos prazo, valor e UF chegam nulos | Manter a API; extrair prazo do `content`; paginar |

Cada motor tem o relatório completo, com o conselho de 7 lentes e a síntese do neutro, em `motores/NN-id/RELATORIO.md`.

---

## 3. Oportunidades ABERTAS hoje com aplicabilidade "sim" ou "depende" (motores 24 a 39)

| Prazo | Oportunidade | Aplicável | Situação do livro |
|---|---|---|---|
| 04/10/2026 | 15º Edital Fundação Aperam Acesita — Social 2026 | depende (território da empresa) | livro (site oficial) |
| 13/10/2026 | Serpro — Aviso de Chamamento 857/2026 | depende | livro |
| 19/10/2026 | **Zurich — Leis de Incentivo 2026** (motores 28 e 35) | depende (exige projeto aprovado em lei de incentivo) | livro |
| 19/10/2026 | Fundo Baobá — Programa Marielle Franco, 2º Apoio Coletivo (R$ 300 mil) | depende (exige 85% de mulheres negras na direção) | livro |
| 30/10/2026 | **Fundação Maria Emília — FME Transforma** (motores 26 e 28) | **sim** | livro |
| 30/10/2026 | MinC/SCDC — Cultura Viva, 2ª edição Pontões | depende | aguardando fonte |
| 01/11/2026 | Karibu Foundation — programa padrão | depende | livro |
| 09/11/2026 | Equatorial — chamada de eficiência energética | depende (CEBAS) | aguardando fonte |
| 04/12/2026 | **BNDES Periferias em Rede**, 6º ciclo | depende | livro |
| 16/09/2027 | Pirenópolis/GO — termo de colaboração com OSC (R$ 300 mil) | depende (território) | livro |

**Fluxo contínuo ("sim"):**

- Instituto Impactarte, aguardando fonte.
- Cadastro Nacional de Pontos e Pontões de Cultura.
- Biblioteca Comunitária é Cultura Viva (MinC).

**Previsão pelo histórico (não confirmada):**

- O Edital Geral do Fundo Brasil abre todo começo de dezembro; foi "sim" em 2024, 2025 e 2026.
- Pronon e Pronas devem abrir entre outubro e novembro.
- O Fundo Ecos Cerrado abre em setembro.
- O Fundo Casa tem temporadas em fev–abr e set–nov.

---

## 4. Conselho de 7 lentes: síntese transversal dos motores 24 a 39

Conselheiros: chief engineer, staff engineer, CTO e professores de computação.

- **Extremamente pessimista** (Dra. Valquíria Antunes, CTO): o painel mente. "Satisfatória" com prazo inventado é pior que "falha", porque o titular confia e perde o tempo dele com editais mortos.
- **Pessimista** (Prof. Heitor Lameira): 5 motores leem `None`. Na prática, são motores de enfeite.
- **Levemente pessimista** (Eng. Clarice Moura, staff engineer): sem link oficial, 435 itens ficam parados. O agregador sem extração do link no corpo do texto gera fila infinita.
- **Neutro** (Dr. Otávio Rezende, chief engineer). **Decisão:** manter os 16 motores, com três correções transversais antes de qualquer ajuste fino.
  1. **Data:** um único leitor de datas para todos os motores.
     - O ano vem do texto. Se o texto não traz, o ano vem da data de publicação, com checagem de faixa.
     - Nunca usar "próximo ano futuro".
     - Em "de X a Y", o prazo é Y.
     - Reprocessar todos os indícios que têm prazo em 2027.
  2. **Link oficial:** extrair do corpo do texto e validar o domínio.
     - Descartar agregadores, encurtadores (expandir antes de avaliar), formulários, rodapé e patrocinador.
     - Sem domínio do financiador, a ação é "aguardar_fonte".
  3. **Estado honesto no painel:**
     - "satisfatória" só quando houver item com prazo e link oficial válidos;
     - rota `None` vira "sem rota";
     - API que devolve menos que o sitemap vira "parcial".

  **Parâmetros de qualidade:**
  - 0 prazos com ano inferido;
  - pelo menos 90% dos livros com domínio do financiador;
  - duplicatas entre motores juntadas por financiador, programa e edição;
  - cada motor com carga de histórico feita uma única vez (`historico_carregado: true`).

  | Risco | Mitigação |
  |---|---|
  | Excesso de "aguardar fonte" | O Interceptador (23) confirma os casos semanalmente |
  | Bloqueio de site | Ponte Brasil (computador do titular) |
  | robots.txt que proíbe | Não ler; registrar a pendência |
  | Ruído de pessoa física | Filtro de público ("só PF" vira "não") |
- **Levemente otimista** (Eng. Laís Penteado): com o feed paginado, o Observatório e a ABCR dão 3 anos de histórico de graça, com mais de 300 programas.
- **Otimista** (Prof. Bruno Taveira): com 603 encerrados arquivados, a previsão da próxima edição fica viável. Um exemplo é o calendário do Fundo Brasil, do Fundo Casa e do Pronon/Pronas.
- **Extremamente otimista** (Dra. Marina Quental, CTO): corrigidos data e link, os 16 motores viram um radar nacional de financiadores privados, com previsão de janela e alerta antecipado. Nenhuma OSC de Goiânia tem isso.

---

## 5. O que não foi confirmado

- **CESE (39):** o robots.txt proíbe o ClaudeBot.
- **Páginas não lidas por limite de chamadas:**
  - Observatório: cerca de 200 posts.
  - ABCR: cerca de 150 posts.
  - Funarte: 19 itens de 2023.
  - IDIS: o sitemap completo.
- **ZIP do Siconv:** formato binário, não lido.
- **Sites que não responderam daqui:** DGARTES, Iberescena e mapas.cultura.gov.br. O site do Einstein deu 403.
- **Classificação heurística:** nos itens de agregador não abertos um a um, o estado foi classificado pelo prazo publicado pelo agregador. Esses itens estão marcados como tal no relatório de cada motor.
