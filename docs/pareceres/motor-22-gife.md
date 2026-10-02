# Parecer do conselho — Motor 22 · GIFE (Grupo de Institutos, Fundações e Empresas)

**Data:** 01/10/2026 · **Motor:** `plat-gife` (Bússola, posição 22) · **Matéria:** técnica (engenharia de coleta), com reflexo na captação junto ao investimento social privado (fundos, institutos e fundações empresariais)

## 1. Síntese

Em setembro de 2026 o motor 22 **não trouxe nenhum edital**. As causas:

- lia a **home institucional** (`https://gife.org.br/`) e a **/agenda/** (eventos), que não listam editais;
- chegava à seleção mensal "Confira editais com inscrições abertas…", mas ali cada edital é um bloco — **título em negrito sem link**, um parágrafo com financiador, prazo e valor, e um link "Inscreva-se", "Acesse" ou "Saiba mais". O leitor genérico só considera links com rótulo de 10 letras ou mais: **os links eram descartados e o título nunca era lido**;
- "instituto" e "fundação" no léxico transformavam a ficha de qualquer associado em candidato. A única "oportunidade" do motor (29/09 a 01/10) foi **"Fundação FEAC"** — a página de perfil do associado, não um edital;
- a descoberta seguia "Transparência" (`/transparencia`), que responde erro: **1 falha por dia, 26 ao todo**.

O que o GIFE tem e o motor não usava:

- a **API pública** do site (WordPress), com a categoria **Editais** e a busca por "edital", "inscrições abertas", "chamada";
- a plataforma **Capta** (`capta.org.br/oportunidades/…`), para onde os links "Inscreva-se" da seleção apontam. Cada oportunidade ali tem campos fixos: **Região**, **Inscrições até: dd/mm/aaaa** e **Edital: link oficial do financiador**.

Em 01/10/2026 estavam **abertos 3 editais nacionais para OSC** na curadoria do GIFE e da Capta:

- **Fundo Baobá — Programa Marielle Franco** (lideranças femininas negras, R$ 300 mil por iniciativa), até **19/10/2026**;
- **Iniciativa Viva Pequena África — Rede Memória Viva** (memória e patrimônio afro-brasileiro), até **03/10/2026**;
- **Edital Impactarte**, em fluxo contínuo.

**Decisão do neutro:** aprovar a versão 2. O motor passa a ler a API do GIFE e da Capta, separa cada bloco da seleção num item, cruza GIFE e Capta e classifica cada edital por prazo, público e abrangência, sempre com o motivo escrito.

## 2. Resultado de setembro/2026 (motor antigo)

| Item | Número | Evidência |
|---|---|---|
| Leituras | 26 no total; 13 dias com registro em setembro/outubro (04–06/09 e 21/09–01/10) | `estado/esquadra.json`, `estado/esquadra_diario.json` › `plat-gife` |
| Editais reais encontrados | **0** | idem |
| Falso positivo | "Fundação FEAC" (`/associados/fundacao-feac`), 29/09, 30/09 e 01/10 — virou ficha na Biblioteca | `biblioteca_alexandria/oportunidades/plat-gife-fundacao-feac/` |
| Falha diária | `/transparencia` com erro HTTP, 26 vezes | `estado/bloqueios.json` › `gife.org.br` |
| Páginas lidas por execução | 6 (home, agenda e 4 "descobertas", entre elas a seleção de setembro/outubro) | `diagnostico.descobertas` |
| Links vistos × vetados | 647 links, 345 candidatos, 89 vetados na camada 1 | `diagnostico` de 01/10 |
| Agenda | "rodou 6 de 20 dias esperados" (07 a 20/09 sem leitura) | `config/descricao_motores.json` |

## 3. Defeitos encontrados

1. **D1 — Rota errada.** A home e a agenda não listam editais. A seleção de editais estava a um clique, e a API pública nunca foi usada.
2. **D2 — Rótulo curto descartado.** Os links de cada edital ("Inscreva-se", "Acesse", "Saiba mais") têm menos de 10 letras e eram ignorados; o nome do edital fica num parágrafo em negrito, sem link.
3. **D3 — Ficha de associado como oportunidade.** "Instituto" e "fundação" no léxico da camada 1 casam o nome de qualquer associado. Resultado: "Fundação FEAC" registrada três dias seguidos.
4. **D4 — Falha diária sem relação com editais.** A descoberta segue "Transparência", que dá erro, e o dia ficava com falha.
5. **D5 — Capta ignorada.** A fonte com prazo, região e link oficial em campos fixos nunca foi lida.
6. **D6 — Seleção fora da categoria.** A seleção de 31/08 ("Confira editais com inscrições abertas em setembro") está só em "Notícias": seguir uma única listagem perde seleções.
7. **D7 — Sem prazo e sem link oficial.** O prazo vem no texto sem ano ("até o dia 19 de outubro") e o link oficial está na Capta; o motor não guardava nenhum dos dois.

## 4. Rotas (Etapa 3)

Testes com IP brasileiro pelo navegador do titular em 01/10/2026. O GitHub já recebia 200 do `gife.org.br` (`estado/esquadra.json` › `saude`). O `robots.txt` dos dois sites permite a leitura (`Disallow:` vazio).

| Rota | Resposta | O que entrega | Decisão |
|---|---|---|---|
| `gife.org.br/wp-json/wp/v2/posts?categories=25` | 200 | categoria **Editais** (450 posts; 57 desde 2024): seleções mensais e notícias de edital único | **usar** (Fonte A) |
| `gife.org.br/wp-json/wp/v2/posts?search=…&after=…` | 200 | busca: pega a seleção de 31/08 que ficou só em Notícias e notícias como "Fundação Maria Emília lança chamada" | **usar** (Fonte A) |
| `capta.org.br/wp-json/wp/v2/posts?categories=4` | 200 | categoria **Oportunidades** (36 posts; 8 de julho a setembro/2026) com Região, Inscrições até e Edital | **usar** (Fonte B) |
| `gife.org.br/feed/` | 200 | só os 10 posts mais recentes, todas as categorias | descartar (a API já cobre) |
| `gife.org.br/editais` | 200 | página da categoria (HTML) | link de referência do motor |
| `gife.org.br/agenda/`, `/associados/`, `/transparencia` | 200 / 200 / erro | eventos, fichas institucionais, erro | **descartar** |

Ritmo dos dois sites: a leitura completa leva 8 chamadas e cerca de 3,5 s no navegador; o leitor faz pausa de 1 s entre chamadas.

## 5. Parametrização antes × depois

| Item | Antes | Agora |
|---|---|---|
| Rotas | home + agenda + 4 "descobertas" | API do GIFE (categoria Editais + 4 buscas, janela de 90 dias) + API da Capta (categoria Oportunidades, janela de 365 dias) |
| Unidade de leitura | rótulo de link | **bloco** da seleção (título em negrito ou subtítulo + texto + links); também "**Título** – texto" no mesmo parágrafo |
| Prazo | nenhum | campo "Inscrições até" da Capta; no texto, "até (as 18h do dia) 19 de outubro", "até 05/11", "de 01/09 a 20/09", com o ano inferido pela data do post; "fluxo contínuo" / "inscrições contínuas". Data de resultado, execução ou evento não vira prazo |
| Público | léxico ("instituto", "fundação") | OSC (organizações, associações, coletivos, movimentos, sem fins lucrativos/econômicos, projetos incentivados) × pesquisadores, pós-graduação, estudantes, jornalistas, municípios, empresas/startups, pessoas físicas. Valem primeiro as frases de elegibilidade ("podem participar", "destinado a", "aceita propostas de"); a frase em que o financiador se descreve ("o Instituto X é uma OSC") não conta |
| Abrangência | nenhuma | nacional (campo Região ou "de qualquer estado brasileiro", "todo o país") ou regional que alcance Goiás (Centro-Oeste, Cerrado, Goiás, Goiânia); entorno das operações de empresa → ACOMPANHAR |
| GIFE × Capta | — | o link "Inscreva-se" leva à Capta: um registro só, com o prazo e o link oficial da Capta e o texto do GIFE; sem link, cruza pelo link oficial ou por título parecido (≥ 3 palavras e 60%) |
| URL do registro | a página lida | o **link oficial do financiador**; a página do GIFE/Capta vai em `url_fonte` |
| Id | hash da URL lida | hash da oportunidade (slug da Capta, link oficial ou título) + mapa de apelidos no estado: o id não muda se um dia a Capta não responder |
| Retroativo | — | o motor não relê dia passado (o que importa é o que está aberto hoje) |

## 6. Calibração (Etapa 6)

O código desta versão rodou sem alteração no navegador do titular, com IP brasileiro e Python no próprio navegador.

**(a) Leitura de ponta a ponta em 01/10/2026:** 8 chamadas, nenhuma falha. GIFE: 17 posts → 15 itens; Capta: 8 posts → 8 itens; 21 editais únicos depois do cruzamento.

| Veredito | Quantos | Quais |
|---|---|---|
| OPORTUNIDADE | **3** | Marielle Franco (GIFE + Capta), Rede Memória Viva (GIFE + Capta), Impactarte |
| ACOMPANHAR | 14 | 9 encerrados em agosto/setembro (ArcelorMittal Investe, Fundo Ecos, AXIA, BNDES Periferias Fortes – Norte, Ernest Solvay, FAS Soluções que Vêm do Território, Fundo Amazônia Indígenas, IA para Saúde Mental, Edital Social Porto); 2 regionais fora de Goiás (APERAM – MG, até 04/10; Floresta+ Amazônia, até 31/12); 2 sem prazo ou sem abrangência no texto (MAPFRE Investimento Social, Fundação Maria Emília FME Transforma) e 1 evento (Encontro do Terceiro Setor FDC) |
| RUÍDO | 4 | PDPG/CAPES (pós-graduação), Chamada Cidades LUPPA (municípios), Campus Mobile (estudantes), Programa Danielle Ardaillon (pesquisadores) |

**(b) Setembro dia a dia** (os mesmos posts, só os publicados até cada dia): 2 OPORTUNIDADES de 01 a 23/09 (Rede Memória Viva e Impactarte) e 3 de 24 a 30/09 (entra Marielle Franco); 14 a 19 itens a ACOMPANHAR por dia. O motor antigo: 0 editais e 1 falso positivo.

**(c) Histórico da categoria Editais desde 2024:** 57 posts → 144 itens; 74% com prazo lido. Capta: 36 posts; as oportunidades de 2026 têm todas o campo "Inscrições até".

**Conferência manual:** as 3 OPORTUNIDADES, os 4 RUÍDOS e os 14 ACOMPANHAR foram lidos um a um no texto original: todos corretos. Os erros achados no caminho viraram regra e teste:

- o Instituto Claro se descreve como "organização da sociedade civil", e o Campus Mobile (para estudantes) saía como edital de OSC;
- "em parceria com a Associação do Laboratório…" contava como público OSC (agora só o plural ou "organização da sociedade civil");
- "Inscreva-se" casava com a sigla de Sergipe ("-SE");
- "até as 18h do dia 4 de fevereiro" e "inscrições contínuas" não eram lidos;
- a seleção de janeiro/2026 e a de abril/2025 usam "**Título** – texto" no mesmo parágrafo;
- espaço de largura zero no início de títulos;
- "municípios onde a empresa mantém operações" (AXIA) e "raio de 100 km das unidades" (Solvay) → entorno da empresa.

**Revisão independente:** um revisor separado leu o código e achou 17 pontos. 16 foram corrigidos, 13 deles com teste; o 17º (a sigla da cidade-sede do financiador, "de Campinas (SP)", lida como restrição) fica registrado — fora de Goiás muda só o motivo do ACOMPANHAR; uma sede em Goiás poderia levar a OPORTUNIDADE um edital sem abrangência declarada, caso raro que a confirmação no edital segura:

- fusão por título juntava editais diferentes do mesmo financiador (Fundo Casa Amazônia × Cerrado) — agora só cruza com a Capta, com 3 palavras em comum e sem slugs diferentes;
- link oficial sem a consulta (`?id=10` × `?id=11`) e a home do financiador viravam a mesma chave;
- título com o link na mesma linha e "Inscrições até 19 de outubro" em negrito eram tratados como título;
- falso "nacional" em "todo o estado do Pará", "todos os estados da Amazônia Legal", "qualquer região do estado de São Paulo";
- data de execução ("executados até 30/06/2027") tomada como prazo; faixa "01/09 a 20/09" não lida;
- "instituições sem fins econômicos" não contava como OSC; "bolsas para pesquisadores que estudam OSC" contava;
- seleção com título fora do padrão; campos da Capta separados por quebra de linha; "Região: Nacional." com ponto;
- id mudava em dia sem Capta; "Mato Grosso do Sul" somava Mato Grosso; slug da Capta aceitava qualquer caminho;
- post malformado ou com data inválida derrubava a fonte; dia com resposta parcial marcado como falho; redirecionamento sem nova checagem de endereço público.

## 7. Conselho de 7 lentes

Os conselheiros são arquétipos sorteados para esta análise, não pessoas reais.

**1. Extremamente pessimista — chief engineer de ingestão de conteúdo editorial.**
A seleção do GIFE é feita à mão por uma equipe de comunicação. Basta mudar o modelo do texto (tabela, lista, cartões) para o separador de blocos errar. A defesa é a Capta, com campos fixos, e o teste de regressão com os dois formatos reais. A métrica a vigiar é `historico.<dia>.itens`: se cair a 0 com posts lidos, o formato mudou.

**2. Pessimista — staff engineer de relevância.**
O volume é pequeno — 3 a 6 editais por mês — e 26% dos itens não trazem prazo no texto do GIFE. "Abrangência não informada" vai para ACOMPANHAR: um edital nacional mal redigido fica fora das OPORTUNIDADES (Fundação Maria Emília diz "sociedade brasileira", não "todo o país"). É a troca consciente por precisão.

**3. Levemente pessimista — professor de engenharia de computação, especialista em sistemas de recomendação.**
GIFE e Capta são curadoria, fonte secundária. O prazo da Capta é transcrito à mão; o do edital pode ter sido prorrogado ou antecipado. A regra do sistema continua: o link oficial vai no registro e a confirmação (etapa 2) é no edital do financiador.

**4. Neutro — CTO de plataforma de dados do terceiro setor, mediador.** O voto está na seção 8.

**5. Levemente otimista — professor de ciência da computação, especialista em sistemas explicáveis.**
Cada veredito tem uma frase que o titular audita: "destinado a estudantes — não a organizações da sociedade civil", "restrito a Minas Gerais — não alcança GO", "restrito ao entorno das operações do financiador — conferir se Goiânia está na lista". O ACOMPANHAR guarda o financiador recorrente: os editais encerrados de agosto/setembro voltam no ano seguinte.

**6. Otimista — staff engineer de produto, foco em captação.**
É a única fonte da Bússola dedicada ao **investimento social privado**: fundos independentes (Baobá, Casa, Brasil de Direitos Humanos), institutos empresariais e editais incentivados (MAPFRE, Porto, ArcelorMittal). Valores relevantes — R$ 300 mil por iniciativa no Marielle Franco — e público OSC por definição.

**7. Extremamente otimista — CTO de big tech, pós-doutor em Python.**
O ACOMPANHAR com encerrados forma o **calendário do investimento social privado**: quem abre, em que mês, com que valor. Somado aos associados do GIFE (motor 30, incentivos fiscais), o sistema passa a prever o edital antes de ele sair.

## 8. Voto do neutro (vinculante)

**Decisão:** aprovar o motor 22 versão 2 e publicar depois dos PRs dos motores 03 e 04 (a base do ramo é a do motor 04).

**Metas (medidas a cada 30 dias em `estado/gife_editais.json` › `historico`):**

| Indicador | Meta |
|---|---|
| Passagens com resposta de pelo menos uma das APIs | ≥ 95% |
| Seleções mensais do GIFE separadas em itens | 100% (0 item com post lido = alerta de formato) |
| OPORTUNIDADES com link oficial do financiador | ≥ 90% (calibração: 3/3) |
| Precisão de OPORTUNIDADE (conferida pelo titular) | ≥ 90% (calibração: 3/3) |
| Ficha de associado ou página institucional como oportunidade | 0 |

**Mitigação de riscos:**

1. **Mudança de formato:** dois formatos de seleção cobertos por teste; a Capta segura prazo e link; o histórico mostra queda de itens.
2. **Prazo transcrito:** o registro leva o link oficial; o Farol confirma no edital antes de qualquer candidatura.
3. **Falso negativo por abrangência:** "não informada" vai para ACOMPANHAR com o motivo escrito, nunca some.
4. **Curadoria como fonte:** `confianca = secundaria`; `url` = link oficial; `url_fonte` = GIFE/Capta.
5. **Conteúdo coletado é dado:** injeção → quarentena (teste); evidência com CPF mascarado.

## 9. Melhorias aplicadas

| Arquivo | O que mudou |
|---|---|
| `src/gife_editais.py` (novo) | leitor do motor 22: API do GIFE e da Capta, blocos da seleção, campos da Capta, prazo, público, abrangência, cruzamento GIFE × Capta, ids estáveis, alarme |
| `config/gife_editais.json` (novo) | endereços, categorias (slug + id de reserva), buscas, janelas, território, ritmo e limites |
| `src/sensores.py` | o `plat-gife` passa ao novo leitor |
| `config/investigacao.json` | URL de referência `https://gife.org.br/editais` e nota do leitor |
| `config/rotas_motores.json`, `config/agenda_motores.json` | rotas reais (APIs), verificação nova e nota de 01/10 |
| `src/auditoria_motores.py`, `scripts/descricao_motores.py` | textos do conselho e da evolução gratuita |
| `tests/test_motor22_gife.py` (novo) | 42 testes: os dois formatos reais de seleção, notícia, ficha de associado, Capta, prazo, território, público, cruzamento, ids, quarentena, rede simulada, falha, retroativo, delegação e os casos da revisão |

**Testes:** a suíte completa tem as mesmas 40 falhas e 3 erros que já existiam no ramo do motor 03, e nenhuma falha nova. Os 42 testes novos estão verdes, e os dos motores 01 a 04 também. `scripts/verificar_privacidade.py` não encontrou nenhuma credencial publicada.

## 10. Editais abertos na curadoria do GIFE em 01/10/2026, para o titular decidir

| Financiador | Edital | Público | Abrangência | Inscrições até | Link oficial |
|---|---|---|---|---|---|
| Iniciativa Viva Pequena África | Rede Memória Viva (adesão) | coletivos e organizações de memória afro-brasileira | nacional | **03/10/2026** | via Prosas (campo "Edital" da Capta) |
| Fundo Baobá | Programa Marielle Franco — aceleração de lideranças femininas negras (R$ 300 mil por iniciativa, 10 selecionadas) | organizações, grupos e coletivos de mulheres negras, com ou sem CNPJ | nacional | **19/10/2026** | `editais.baoba.org.br` |
| Impactarte | Edital Impactarte | organizações | nacional | fluxo contínuo | `impactarte.org.br` |

A ACOMPANHAR, com prazo aberto: **Fundação APERAM Acesita – Social 15ª** (até 04/10, restrito ao Vale do Aço/MG) e **Floresta+ Amazônia** (até 31/12, Amazônia Legal). Sem prazo no texto: **MAPFRE — investimento social** (projetos aprovados em leis de incentivo: Rouanet, Esporte, FIA, Idoso) e **Fundação Maria Emília — FME Transforma** (saúde e educação; aceita OSC).

## 11. Pendências

1. **Ordem de implantação:** os PRs dos motores 03 e 04 antes deste.
2. **Primeira execução na nuvem:** confirmar `historico.<dia>.falhou = false` e se a Capta responde ao GitHub (só foi testada do Brasil; se recusar, a Fonte A segue sozinha e o diagnóstico mostra a causa).
3. **Registro antigo:** a ficha "Fundação FEAC" (`plat-gife-fundacao-feac`) continua na base como oportunidade. É página institucional de associado, não edital: a revisão humana decide marcá-la como `descartada` (`merge_registro` preserva o status).
4. **Confirmação no edital:** abrir o link oficial de cada OPORTUNIDADE para conferir o prazo no próprio edital (próximo passo gratuito).
5. **Associados do GIFE:** a página de editais de cada associado (institutos e fundações empresariais) fica para o motor 30, que já lista os associados.
