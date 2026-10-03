# Motor 33 — site-editais-culturais (Editais Culturais / "Acheaqui Arte e Cultura")

Estudo feito em 02/10/2026. Foram usadas cerca de 44 chamadas de WebFetch (limite indicado: cerca de 40). O WebSearch está bloqueado para a organização. O curl também é bloqueado pelo proxy para estes domínios.

**Conclusão principal:** o site **não é um agregador de editais de financiadores.** Ele é o portal comercial "Acheaqui Arte e Cultura" (com as marcas Facultura e Revista Editais Culturais). O portal:

- vende modelos de projeto cultural e serviços de divulgação, músicos e turismo;
- organiza **concursos próprios pagos**, todos para pessoa física;
- só nas páginas de categoria, cita alguns concursos de terceiros, a maioria estrangeiros ou para pessoa física.

Para uma OSC de Goiânia, o rendimento é quase nulo.

---

## 1. Rota (teste e conclusão)

| URL testada | Resultado |
|---|---|
| Rota configurada: `None` (html_listagem) | Não há rota. O leitor cai na página pública. |
| https://editaisculturais.com.br/ | 200. Traz 4 destaques de blog: 2 concursos próprios, 1 artigo de turismo e 1 venda de modelo. Não traz prazo, valor nem link oficial. |
| https://www.editaisculturais.com.br/robots.txt | 200. `Disallow: /servers/frontend/`, **Crawl-delay: 10**, aponta para o sitemap. |
| **https://www.editaisculturais.com.br/sitemap.xml** | 200. 261 URLs, sem `lastmod`: 87 em PT, cerca de 88 em `/en-us/` e 85 em `/l/` (blog). **É a melhor rota de descoberta.** |
| /editais-culturais-abertos-2025/, /l/editais-culturais-abertos-2025/, /l/editais-culturais-2025/, /l/projetos-culturais-abertos/ | 200, mas **nenhum edital de terceiro**. São páginas de venda de "modelos de projetos culturais prontos" (publicadas em 06/03/2025). |
| /fotografia/, /literatura/, /artes-cenicas/, /danca/, /musica/, /audiovisual/, /artes-visuais/ | 200. **São as únicas páginas com concursos de terceiros que têm link externo**: 21 itens no total, alguns com prazo, valor e link. |
| /submit-contest-enviar-concurso/ | Formulário para produtores enviarem concursos. Exige a logo e o link do portal no site do produtor. |
| Feed RSS / API / paginação | Não existem. Não foram encontrados. |
| Web Archive (histórico) | Bloqueado: SITE_BLOCKED. |

**Conclusão:** a rota atual é a página inicial. Ela é a pior escolha, porque ali só aparecem concursos próprios e posts. A melhor rota verificada tem duas partes:

- **Descoberta:** `https://www.editaisculturais.com.br/sitemap.xml`.
- **Leitura:** as **7 páginas de categoria** (`/fotografia/`, `/literatura/`, `/artes-cenicas/`, `/danca/`, `/musica/`, `/audiovisual/`, `/artes-visuais/`), extraindo **só os links externos**.

Respeitar o Crawl-delay de 10 s. Mesmo com a rota melhor, o rendimento útil para OSC é baixo (ver seção 6).

## 2. Histórico de 3 anos (02/10/2023 a 02/10/2026)

O site não tem arquivo nem datas confiáveis. Os metadados de quase todas as páginas próprias foram regravados em 22/09/2026. O histórico foi montado assim:

- 7 páginas de categoria;
- páginas de concurso tiradas do sitemap;
- 10 links oficiais abertos por amostra.

**A. Terceiros (financiadores ou organizadores externos)**

| Data pub. | Título | Financiador | Site oficial | Prazo | Estado | Aplicável |
|---|---|---|---|---|---|---|
| 2024-12-28 | Funarte Aberta 2025 – Ocupação dos espaços da Funarte no RJ (pauta gratuita) | Funarte | gov.br/funarte/pt-br/editais/2024/programa-funarte-aberta-2025-...-rio-de-janeiro **(verificado)** | 2025-12-01 | encerrado_arquivar | depende |
| 2026-04-27 | Concurso de Fotografias Olhos de Ver 2026 | IRPH / Prefeitura do Rio | irph.prefeitura.rio/concurso-de-fotografias-olhos-de-ver-2026/ **(verificado)** | 2026-06-19 | encerrado_arquivar | não |
| "" | Prêmio Barueri de Artes Visuais 2024 | Sec. Cultura e Turismo de Barueri | portal.barueri.sp.gov.br/.../REGULAMENTO_PREMIO_ARTES_VISUAIS_2024.pdf **(verificado)** | 2024-10-05 | encerrado_arquivar | não |
| "" | IX Concurso Internacional de Poetrix 2024 | Academia Internacional Poetrix | academiapoetrix.org/2024/06/... **(verificado)** | 2024-07-31 | encerrado_arquivar | não |
| "" | Ibermúsicas – Apoio à Circulação de Profissionais da Música | Programa Ibermúsicas | ibermusicas.org/index.php/convocatorias-pt/ **(abre; sem ciclo vigente)** | "" | sem_data | depende |
| "" | 26º FND – International Dance Competition | Festival Norte Dança (Portugal) | festivalnortedanca.org **(abre)** | 2025-11-22 | encerrado_arquivar | não |
| "" | FND Online – 3ª edição | Festival Norte Dança (Portugal) | festivalnortedanca.org **(abre)** | 2025-05-31 | encerrado_arquivar | não |
| "" | 21º Concurso Literário Mansueto Bernardi 2024 | Prefeitura de Veranópolis/RS | veranopolis.rs.gov.br/... (403) | 2024-08-16 | encerrado_arquivar | não |
| "" | 2º Concurso Intern. de Poesias – Prêmio Mario Quintana | Editora Mandacaru | editoramandacaru.com.br/... (erro SSL) | 2024-08-10 | encerrado_arquivar | não |
| "" | Sony World Photography Awards 2025 | World Photography Organisation | worldphoto.org/pt (não aberto) | 2025-01-10 | encerrado_arquivar | não |
| "" | IPPA Awards 2025 | IPPAWARDS | ippawards.com (não aberto) | 2025-03-31 | encerrado_arquivar | não |
| "" | Concurso Fotográfico SENAR-SP 2025 | SENAR-SP / FAESP | faespsenar.com.br (aberto; o concurso não aparece) | 2025-04-25 | encerrado_arquivar | não |
| "" | Prêmio Portfólio FotoDoc 2025 | FotoDoc | fotodoc.com.br/premio/ (não aberto) | 2025-06-30 | encerrado_arquivar | não |
| "" | Global Journey Photography Contest | SITTP | sittp.com/registration (não aberto) | 2025-05-30 | encerrado_arquivar | não |
| "" | ND Awards 2026 | ND Awards | ndawards.net (não aberto) | "" | sem_data | não |
| "" | Terrain.org 16th Annual Contest | Terrain.org | terrain.org (não aberto) | 2025-09-01 | encerrado_arquivar | não |
| "" | Flash 405 | Exposition Review | expositionreview.com (não aberto) | 2025-09-05 | encerrado_arquivar | não |
| "" | SFWP Literary Awards | Santa Fe Writers Project | sfwp.com (não aberto) | 2025-09-15 | encerrado_arquivar | não |
| "" | 6º Festival Sertanejo Raiz | Prefeitura de Bueno Brandão/MG | "" (o link aponta para festivaisdobrasil.net) | 2024-09-10 | encerrado_arquivar | não |
| "" | 3º Canto Por Ti Festival | S. C. Corinthians Paulista | corinthians.com.br/cantoporti (não aberto) | 2024-08-28 | encerrado_arquivar | não |
| "" | Festival Timbre 2024 | Groover | groover.co (página inicial) | 2024-08-12 | encerrado_arquivar | não |
| 2025-08-14 | I Prêmio Concurso Artes Visuais 2025 | "Cultural Notices" | culturalnotices.net (DNS não resolve) | 2025-08-30 | encerrado_arquivar | não |

**B. Concursos próprios do portal (o "financiador" é o próprio agregador; sem CNPJ; todos com taxa paga e só para pessoa física)**

| Data pub. | Título | Organizador | Site oficial | Prazo | Estado | Aplicável |
|---|---|---|---|---|---|---|
| 2026-09-28 | IV Grande Prêmio Fotografia "Meu Coração Brasileiro" 2026 (indício) | Acheaqui | "" (só o portal) | 2026-10-15 (prorrogado) | **aberto** | não |
| 2026-09-24 | O mesmo concurso, página "Cópia de iii-..." (indício duplicado) | Acheaqui | "" | 2026-09-27 | encerrado_arquivar | não |
| "" | II Grande Prêmio Artes Cênicas 2025 (indício "Concurso de Teatro 2026") | Acheaqui | "" | 2025-05-25 | encerrado_arquivar | não |
| "" | Facultura International Photography Award 2026 | Acheaqui + Facultura | "" | 2026-06-22 | encerrado_arquivar | não |
| 2026-06-14 | Prêmio Mata Atlântica 2026 | Acheaqui + Facultura | "" | 2026-07-30 | encerrado_arquivar | não |
| 2026-06-25 | I Prêmio Fotografia Revista Editais Culturais – Dia Mundial da Fotografia 2026 | Acheaqui | "" | 2026-08-22 | encerrado_arquivar | não |
| 2026-02-02 | I Prêmio Literatura e Poesias – E-book e Podcast 2026 | Ordem Jnana + Acheaqui | "" | 2026-07-15 | encerrado_arquivar | não |
| "" | I Concurso de Dança Online Internacional 2025 (= t1st International...) | Acheaqui | "" | 2025-04-30 | encerrado_arquivar | não |
| "" | I Grande Prêmio Audiovisual 2025 | Acheaqui | "" | 2025-04-30 | encerrado_arquivar | não |
| "" | II Grande Prêmio Literatura – Poesia, Conto, Post 2025 | Acheaqui | "" | 2025-04-30 | encerrado_arquivar | não |
| "" | Concurso de Poesias e Contos Místicos 2025 | Centro Ciência e Magia na Yoga + Acheaqui | "" | 2025-03-06 | encerrado_arquivar | não |
| "" | I Concurso de Músicos Portal Acheaqui (cadastro) | Acheaqui | "" | 2025-08-31 | encerrado_arquivar | não |

**Falso positivo:** o indício "Divulgação do Seu Evento..." (R$ 95,00) é um **serviço pago de divulgação** vendido pelo portal. Não é oportunidade. Está em `livros.json` com a observação "descartar".

**Verificação dos indícios (4):** nenhum dos 4 tem `link_oficial` nem `financiador`. Os 4 foram abertos:

- 2 são o mesmo concurso próprio (página duplicada);
- 1 tem título desatualizado: o indício diz "Teatro 2026", mas o conteúdo é de 2025 e sem prazo;
- 1 é serviço pago.

Como os indícios não trazem link oficial, a amostra de 10 links foi tirada dos links externos das páginas de categoria:

| Resultado | Quantos | Quais |
|---|---|---|
| Abriram e são do financiador | 5 | Funarte, IRPH, Barueri, Poetrix, FND |
| Abriu, mas sem ciclo vigente | 1 | Ibermúsicas |
| Abriu, mas é página genérica sem o concurso | 1 | SENAR-SP |
| Falharam | 3 | Veranópolis (403), Mandacaru (SSL), culturalnotices.net (DNS) |

O link da Funarte no agregador usa o caminho antigo `/editais-1/2024/...`. O caminho válido é `/editais/2024/...`.

## 3. Onde publica

- **O próprio portal:** os concursos próprios ficam em páginas do domínio editaisculturais.com.br. A inscrição é por **formulário próprio**, **e-mail** ou **WhatsApp**, com pagamento da taxa por **PIX**. Em um caso, o PIX vai para um endereço de e-mail pessoal (gmail). Não há regulamento com CNPJ nem plataforma de terceiros.
- **Terceiros citados:**
  - órgãos públicos com site oficial: Funarte em gov.br, com inscrição pelo **Prosas** (prosas.com.br/editais/15338); Prefeitura do Rio (IRPH); Barueri e Veranópolis (regulamento em PDF no portal municipal);
  - entidades privadas nacionais: editoras, academias literárias, SENAR, clubes;
  - concursos estrangeiros com taxa em dólar, com formulário próprio de cada site.
- Não usa Mapas Culturais nem Transferegov. Não trouxe nenhuma chamada de fundação ou instituto voltada a OSC.

## 4. Tipos de oportunidade

- **Prêmios e concursos artísticos individuais:** quase a totalidade. Áreas: fotografia, literatura/poesia, dança, artes cênicas, audiovisual, artes visuais, música.
- **Chamadas internacionais:** fotografia e literatura nos EUA e Reino Unido; dança em Portugal.
- **Cessão de pauta (ocupação de espaços):** Funarte Aberta. É a única com PJ cultural sem fins lucrativos elegível.
- **Cadastro:** o cadastro de músicos do próprio portal.
- **Não há:** edital de projeto com repasse a OSC, fundo rotativo, bolsa institucional nem chamada de fundação.
- **Faixas de valor:**
  - terceiros: de R$ 0 (só divulgação) a R$ 5.000 por categoria; prêmios estrangeiros de US$ 1.000 a US$ 10.000;
  - concursos próprios: anunciam de R$ 500 a "R$ 50.000 para cada um dos 5 primeiros", com taxa de R$ 15 a R$ 70. Esses números são incompatíveis com a arrecadação plausível e não há entidade responsável identificável. Tratar como **sinal de risco**.
- **Quem pode participar:** pessoa física (artistas amadores e profissionais), salvo Funarte Aberta (PF, PJ cultural e MEI) e Ibermúsicas (profissionais e grupos de música).

## 5. Calendário

- **Concursos próprios:** dois ciclos por ano.
  - 1º semestre: abre em fevereiro ou março, fecha em março, abril ou maio (2025) ou em julho (2026).
  - 2º semestre: abre em junho ou agosto, fecha em julho, agosto, setembro ou outubro. As prorrogações são frequentes.
- **Terceiros citados:**
  - fotografia internacional: prazos de novembro a junho;
  - literatura nos EUA: agosto e setembro;
  - festivais de música: julho a setembro;
  - Funarte Aberta: abre no fim de dezembro e fica em fluxo até dezembro do ano seguinte.
- Não há regularidade de publicação de terceiros. As páginas de categoria são atualizadas à mão e mantêm itens vencidos (de 2024 e 2025) junto com os de 2026.

## 6. Conselho de 7 lentes sobre o motor

1. **Extremamente pessimista — Dra. Helga Ruppenthal, professora de computação (pós-doutorado em Python, ETH), implacável.** "O motor aponta para um site que não é fonte de editais. É uma loja de modelos de projeto e de concursos pagos sem CNPJ. O painel diz 'satisfatório' porque contou duas páginas próprias como achados. É um falso verde. Pior: um dos 'achados' anuncia R$ 50 mil para cada um dos cinco primeiros, com taxa de R$ 35. Se isso entrar no funil de uma OSC, o sistema endossa um risco reputacional. Rota `None` é rota inexistente."
2. **Pessimista — Marcos Teodoro, chief engineer, metódico e seco.** "Nenhum dos 4 indícios tem financiador nem link oficial. O título 'Concurso de Teatro 2026' sai do HTML, mas o conteúdo é de 2025. Há duplicata ('Cópia de iii') e um serviço de R$ 95 classificado como oportunidade. O resumo guarda o menu do site em vez do conteúdo. O léxico casa 'prêmio', 'concurso' e 'R$' sem distinguir 'taxa de inscrição' de 'premiação'."
3. **Levemente pessimista — Priya Nandakumar, staff engineer, pragmática.** "As categorias têm, sim, links externos. Mas dos 21 de terceiros, só 2 são aplicáveis 'depende' para OSC. Os metadados de data foram regravados em lote em 22/09/2026, então `publicado` não serve para o corte temporal. E o Crawl-delay de 10 s precisa ser respeitado."
4. **Neutro — Prof. Dr. Augusto Leal Bastos, pós-doutorado em Python (USP), árbitro sereno.** Síntese abaixo.
5. **Levemente otimista — Renata Okafor, staff engineer, construtiva.** "O sitemap é limpo: 261 URLs, sem paginação nem JavaScript. Dá para fazer a varredura completa com 8 requisições e diferenciar páginas novas por diff de URL. A extração de links externos por categoria é trivial e já devolveu Funarte e prefeituras."
6. **Otimista — Diego Arantes, CTO de big tech, visionário.** "O valor do motor está em servir de **descobridor de financiadores**. Funarte, IRPH, Barueri e Ibermúsicas viram sementes para motores dedicados. E o motor ensina o sistema a reconhecer concursos pagos de risco, o que protege a associação."
7. **Extremamente otimista — Profa. Dra. Lívia Sakamoto, pós-doutorado em Python (Unicamp), entusiasta.** "Com filtro de risco, deduplicação e roteamento ao site oficial, o motor vira um sensor barato que custa 8 requisições por semana. No melhor cenário, pega uma ou duas pautas ou prêmios públicos por ano e alimenta o motor da Funarte. Ganho marginal, custo quase zero."

**Síntese do neutro (Prof. Augusto Leal Bastos)**

- **Decisão:** **rebaixar** o motor de "satisfatório" para **"baixo rendimento / só descoberta"**. Manter com cadência **mensal**, apenas para descobrir links externos. **Nunca criar livro** a partir de concursos próprios do portal. Esses ficam em `aguardar_fonte` com `aplicavel = nao` e a marca de risco "concurso pago sem entidade identificada".
- **Melhorias:** ver seção 7.
- **Parâmetros de qualidade:**
  1. ≥ 90% dos itens publicados com `link_oficial` fora de editaisculturais.com.br (hoje: 0% dos indícios);
  2. 0 itens de domínio próprio com `acao = criar_livro`;
  3. 0 duplicatas (mesmo título normalizado e mesmo prazo);
  4. taxa de falso positivo (serviços ou modelos à venda) < 5%;
  5. `prazo` preenchido em ≥ 70% dos itens de terceiros;
  6. ≤ 10 requisições por ciclo, com 10 s de intervalo.
- **Riscos e mitigação:**
  1. *Endossar concurso pago de risco:* lista de domínios "comerciais/próprios" e regra "taxa de inscrição + PF + sem CNPJ → não aplicável, sem livro".
  2. *Datas de publicação regravadas:* ignorar `article:published_time`; usar a data em que a URL aparece pela primeira vez no sitemap (`primeiro_visto`).
  3. *Links quebrados ou antigos (403, SSL, DNS, caminho antigo da Funarte):* validar o link oficial antes de criar livro; se falhar, `aguardar_fonte`; normalizar `/editais-1/` para `/editais/` no gov.br/funarte.
  4. *Itens vencidos mantidos nas categorias:* corte por prazo e janela de 3 anos; se não houver prazo, `sem_data` com revisão em 90 dias.
  5. *Mudança de layout ou bloqueio:* o sitemap é a âncora; se ele falhar, o motor alerta em vez de cair silenciosamente na página inicial.

## 7. Melhorias do motor

1. **Rota:** trocar `None` (página inicial) por `sitemap.xml` (descoberta) mais as 7 categorias `/fotografia/`, `/literatura/`, `/artes-cenicas/`, `/danca/`, `/musica/`, `/audiovisual/`, `/artes-visuais/` (leitura). Respeitar o Crawl-delay de 10 s.
2. **Link oficial:** extrair só os `<a href>` externos ao domínio. Item sem link externo passa a ser `aguardar_fonte`. Validar o link (HTTP 200 e domínio do órgão) antes de criar livro.
3. **Filtro de origem:** os domínios editaisculturais.com.br, culturalnotices.net e festivaisdobrasil.net são "comerciais/próprios". Concursos deles nunca viram livro.
4. **Léxico:** separar "taxa de inscrição / valor da inscrição / PIX" de "premiação". Descartar páginas com "modelo de projeto", "divulgar 1 evento", "loja", "contratar músico". Exigir os termos OSC/organização/pessoa jurídica para `aplicavel = sim/depende`.
5. **Filtro de aplicabilidade:** "pessoa física / fotógrafos / poetas / bailarinos" sem menção a PJ leva a `aplicavel = nao`. Concurso estrangeiro com taxa em dólar leva a `nao`.
6. **Deduplicação:** usar o título normalizado sem prefixo "Cópia de", mais o prazo, mais o link oficial. Tratar como duplicatas, por exemplo, `t1st-international...` e `concurso-de-danca-internacional-2025`, e `copia-de-iii...` e `iv-grande-premio...`.
7. **Histórico e data:** não confiar nos metadados de publicação (regravados em lote). Guardar `primeiro_visto` por URL do sitemap e prazo extraído do texto. O Web Archive não está acessível neste ambiente.
8. **Cadência:** de diária ou semanal para **mensal**. O rendimento útil para OSC não justifica mais.
9. **Encaminhamento:** cada financiador público descoberto (Funarte, IRPH, prefeituras) deve gerar uma sugestão de motor dedicado em vez de depender do agregador. A Funarte já tem o motor 29.
10. **Resumo:** extrair o corpo do texto, e não o menu. Hoje o `resumo` dos indícios é o cabeçalho de navegação.

## 8. O que não foi confirmado e por quê

- **Links oficiais não abertos** (limite de cerca de 40 chamadas): Sony World Photography, IPPA, FotoDoc, SITTP, ND Awards, Terrain.org, Exposition Review, SFWP, Corinthians e Groover. Ficam em `aguardar_fonte`, com o prazo vindo do agregador.
- **Links que falharam:** Veranópolis (403), Editora Mandacaru (certificado SSL inválido), culturalnotices.net (DNS não resolve).
- **SENAR-SP:** o agregador aponta só para a página inicial, que não mostra o concurso.
- **Ibermúsicas:** a página oficial diz que as convocatórias de 2027 saem em meados de 2027. O período "16/06 a 01/10" citado pelo agregador não traz ano.
- **Funarte Aberta MG/SP:** citada genericamente na categoria /danca/, mas não verificada aqui (consta no motor 29).
- **Datas de publicação:** os metadados das páginas próprias foram regravados (22/09/2026). Só foram mantidas as datas que aparecem no texto ou que divergem desse lote.
- **Web Archive:** bloqueado (SITE_BLOCKED). Não foi possível ver como o site era em 2023. Nenhum item de 02/10/2023 a meados de 2024 foi encontrado nas páginas atuais.
- **Premiações dos concursos próprios:** não há como confirmar se são pagas. Não há CNPJ, entidade jurídica identificada nem regulamento registrado.
- **Instruções dirigidas à IA:** nenhuma encontrada nas páginas lidas.
- **Dados pessoais:** nomes de pessoas físicas (contatos e equipe) não foram registrados.
