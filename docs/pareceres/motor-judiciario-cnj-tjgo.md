# Parecer do conselho — Motor do Judiciário (CNJ e TJGO)

**Data:** 02/10/2026 · **Associação de referência:** A.M.C. Jardim América (OSC, Goiânia/GO) · **Reúne os motores
`dje-tjgo` e `cnj-destinacoes` em um só: `judiciario-cnj-tjgo`.**

## 1. Síntese

O Judiciário destina a entidades o dinheiro das prestações pecuniárias, das penas de multa e das transações penais. A
diretriz nacional é a Resolução CNJ 558/2024; em Goiás valem também o Código de Normas da Corregedoria (art. 257, § 3º) e
as portarias de cada Diretoria do Foro.

Cada comarca abre o **seu** edital de seleção de projetos e o TJGO anuncia o edital na Agência de Notícias, com o PDF
anexado. A entidade precisa estar cadastrada antes no **Banco de Projetos Sociais** da Corregedoria-Geral da Justiça
(CGJ/GO).

Os dois motores antigos somaram **80 leituras e nenhum achado**:

- liam páginas que não existem mais (404);
- liam um republicador (Jusbrasil);
- liam a página de compras do CNJ.

E, mesmo que achassem algo, a coleta no computador do titular não grava os achados na base.

**Decisão:** criar um motor único, com leitor próprio (`src/judiciario_go.py`), sem IA e sem tokens. As fontes são cinco:

- o RSS da Agência de Notícias do TJGO, paginado;
- a página de cada notícia e o PDF do edital;
- a busca do Portal do CNJ;
- o cruzamento do que o PNCP já trouxe do TJGO e do CNJ;
- a exigência do Banco de Projetos.

Goiânia vem primeiro. Edital de outro estado é ruído, porque só aceita entidades daquela comarca.

## 2. Diagnóstico — o que o sistema tinha

| O que existia | Defeito |
|---|---|
| `dje-tjgo`: 6 URLs, coleta local | As 5 páginas do TJGO dão **404** desde a reforma do portal: `/execucao-penal`, `/coordenadoria-de-execucao-penal`, `/editais-de-chamamento`, `/…/20140-prestacao-pecuniaria` e `/dje` (verificado em 02/10/2026). Na nuvem, só o Jusbrasil respondia, e trazia a navegação dos diários do país inteiro (12CJM, AAM, AEMERJ…). O MPGO é outro órgão. **40 leituras, 0 achados.** |
| `cnj-destinacoes`: 3 URLs, nuvem | Lia a home do CNJ, a página de **licitações de compras** e `/sistema-carcerario/penas-e-medidas-alternativas/`, que dá **404**. **40 leituras, 0 achados.** |
| `scripts/coleta_brasil.py` | Roda os sensores no computador do titular, mas **não grava os achados na base**: registra só a contagem. Um edital achado em casa nunca chegaria ao painel. |
| Investigação (ponto `captacao-190` das 260) | Gravou o "Prêmio de Boas Práticas PopRuaJud" do CNJ como se fosse do TJGO. É prêmio para tribunais, não para entidades. |
| Motor 04 (PNCP) | Já trazia o credenciamento do TJGO para entidades sem fins lucrativos (coleta seletiva, até 22/07/2031). Fica com o motor 04; aqui é só cruzado. |

## 3. Varredura das rotas (02/10/2026, navegador do titular, IP brasileiro)

| Rota | Resultado | Uso no motor |
|---|---|---|
| RSS `…/agencia-de-noticias/noticias-ccs?format=feed&type=rss` | RSS 2.0 do Joomla, 8 notícias por página. Pagina com `&limitstart=8, 16…`: o item 800 já é de junho de 2026, cerca de 7 notícias por dia. O `&limit=` é ignorado. | **Fonte A**: lê até a primeira página toda já vista; carga inicial de 150 dias, 25 páginas por vez |
| Notícia da 1ª VEP de Rio Verde (03/07/2026) | Edital 01/2026. Inscrições até 30/09/2026. Exige o Banco de Projetos Sociais, as áreas de segurança pública, educação e saúde e atuação no município de Rio Verde. O PDF está anexado ao corpo (`/images/docs/ccs/…pdf`). | **Fonte B**: corpo em `com-content-article item-page`, data em `<time datetime>` |
| Notícia da 1ª VEP de Goiânia (12/01/2026) | Edital 01/2026. "Requerimento de Habilitação até o dia **30 deste mês**". Fundamento: Código de Normas, art. 257, § 3º, e Portaria 819/2024 da Diretoria do Foro. PDF em `/files/2026/01 - Janeiro/…pdf`. | Prazo relativo resolvido pela data da publicação: 30/01/2026 |
| Outras comarcas na mesma agência | Piracanjuba, Cocalzinho de Goiás e a Vepema de Goiânia, além de Itaberaí (republicada pelo CNJ) | Extração de comarca pelo título e pelo texto |
| Busca do site do TJGO (`com_search`, `finder`) | 500 / não ligado | Não usada |
| `robots.txt` do TJGO | Joomla padrão (bloqueia `/administrator/`, `/components/`…); `/index.php/…`, `/files/` e `/images/` liberados | Respeitado |
| `corregedoria.tjgo.jus.br/basesocial` | Banco de Projetos Sociais: cadastro da entidade e "busca pública de projetos". A busca lista **nome e telefone dos responsáveis** de cada projeto. | **Fonte E**: só a exigência. A lista **não é coletada** (LGPD). |
| DJEN, `comunicaapi.pje.jus.br/api/v1/comunicacao` | Recusa IP estrangeiro; do Brasil, filtra por `siglaTribunal` e `texto`. "prestação pecuniária" no TJGO em setembro: 22 itens, **todos intimações** (sentenças e decisões com nomes de réus). `tipoComunicacao=Edital` é ignorado. | **Desligado**: não traz edital, só dado pessoal |
| Busca do Portal do CNJ (`?s=`) | Responde do Brasil. Republica editais dos tribunais ("Edital seleciona projetos de Itaberaí (GO)…") e de outros estados. A API REST do WordPress devolve `[]` e `/feed/` cai na home. | **Fonte C**: nuvem; se o CNJ recusar a nuvem, o computador lê na vez seguinte |
| Auditoria coordenada do CNJ (2025) | Cita a Resolução nº 558/2024 como diretriz de gestão, registro e destinação | Regra nacional (insumo) |
| PNCP | Credenciamento do TJGO (CNPJ 02.292.266/0001-80) para entidades sem fins lucrativos | **Fonte D**: cruzada da base (motor 04) |

## 4. O que é oportunidade para a associação — leitura jurídica

| Tipo | Natureza | Classificação |
|---|---|---|
| Edital de seleção de projetos com recursos de prestação pecuniária, com prazo vigente | Recurso, por decisão judicial, sem disputa de preço | **OPORTUNIDADE** |
| O mesmo edital, publicado há até 20 dias, sem prazo na notícia | Recurso, com prazo a conferir no PDF | **OPORTUNIDADE** (`prazo_a_confirmar`) |
| Credenciamento de entidades sem fins lucrativos pelo Judiciário (ex.: coleta seletiva solidária) | Parceria | **OPORTUNIDADE** |
| Edital encerrado | Mostra o ciclo da comarca: Goiânia abre em janeiro | ACOMPANHAR |
| Resultado, entrega de equipamentos, repasse | Mostra quem recebe | ACOMPANHAR |
| Provimento, resolução, Código de Normas | Regra | ACOMPANHAR |
| Banco de Projetos Sociais da CGJ/GO | **Habilitação prévia**: sem ele, a entidade não participa | ACOMPANHAR, sempre no topo |
| Edital de comarca de outro estado (republicado pelo CNJ) | Só aceita entidades daquela comarca | RUÍDO |
| Concurso, licitação, leilão, edital processual (citação, praça) | — | RUÍDO |

**Requisitos que o motor extrai de cada edital:**

- comarca e vara;
- número do edital;
- prazo de inscrição ou habilitação;
- **áreas admitidas** (Goiânia e Rio Verde, 2026: segurança pública, educação e saúde);
- **restrição territorial** (a entidade deve atuar no município da comarca);
- exigência do Banco de Projetos;
- forma de inscrição (e-mail ou presencial).

Se o objeto da associação cabe nas áreas admitidas é enquadramento, e quem decide é o Farol.

## 5. Parametrização (`config/judiciario_go.json`)

| Fonte | Rota | O que lê | Limites |
|---|---|---|---|
| A — notícias do TJGO | computador do titular | RSS paginado | 6 páginas por coleta (para na página toda vista); carga inicial de 150 dias, 25 páginas por vez; 20 notícias abertas por coleta (o resto fica pendente) |
| B — PDF do edital | computador do titular | o PDF anexado ao corpo da notícia (texto pelo pypdf, quando instalado) | 6 PDFs por coleta, até 15 MB; PDF lido não é relido |
| C — busca do CNJ | nuvem (computador, se a nuvem for recusada) | 4 consultas | uma vez por dia; 8 notícias por leitura |
| D — PNCP cruzado | base | órgão TJGO ou CNJ nos registros do motor 04 | sem rede |
| E — Banco de Projetos | fixa | a exigência | — |
| F — DJEN | desligada | — | motivo registrado |

**A rota da coleta.** O computador do titular grava `estado/judiciario_go_local.json`, e só ele escreve nesse arquivo. A
leitura diária da nuvem (07h53) incorpora esses registros e entrega as oportunidades à base. Assim o que o computador
acha chega ao painel sem que ele grave na base nem dispute arquivo com a nuvem.

**Duplicata.** Um edital visto na notícia do TJGO, no PDF e na republicação do CNJ é **um** registro. A chave é comarca
+ número do edital, comarca + prazo, o PDF ou a URL. A fonte primária (TJGO) vence, e as outras ficam em
`vista_tambem_em`.

## 6. Conselho de 7 lentes

| Lente | Quem fala | Ponto central | O que foi exigido e está no código |
|---|---|---|---|
| Extremamente pessimista | Engenheiro-chefe de confiabilidade | Os dois motores leram 80 vezes páginas mortas e o painel mostrou "ativo, sem achados". 404 não pode virar "sem edital hoje". | O 404 é falha nomeada no diagnóstico. A nuvem alerta quando o computador do titular passa 3 dias sem coletar. O formato desconhecido do RSS também é sinalizado. |
| Pessimista | Staff engineer de dados | A mesma notícia aparece no TJGO, no PDF e no CNJ. E notícias de outro estado inflariam o painel. | Chave múltipla de duplicata; edital de outro estado vira RUÍDO; o PNCP é só cruzado, nunca duplicado. |
| Levemente pessimista | Professor de sistemas distribuídos | Computador e nuvem gravando o mesmo estado geram conflito no git, e o coleta_brasil não grava a base. | Arquivo local separado, escrito só pelo computador; a nuvem lê esse arquivo e entrega à base. |
| Neutro | CTO | Decide (abaixo). | — |
| Levemente otimista | Professor de recuperação de informação | O RSS do Joomla pagina e traz tudo; a notícia traz comarca, número, prazo e PDF. | RSS paginado até a página vista; extração de comarca, vara, número, prazo (inclusive "até o dia N deste mês"), áreas e restrição. |
| Otimista | Staff engineer de produto | O pré-requisito (Banco de Projetos) é o que mais decide. Quem se cadastra antes concorre em todas as comarcas onde atua. | Habilitação prévia sempre no topo do "acompanhar"; Goiânia primeiro nas abertas. |
| Extremamente otimista | Chief engineer de plataforma | O mesmo leitor serve à Justiça Federal (TRF1/SJGO) e à do Trabalho (TRT18). | Leitor por fontes configuráveis; a extensão fica registrada como próximo passo, por decisão do titular. |

### Voto do neutro

1. **Aprovado.** Os dois motores viram um, e os antigos ficam inativos com o motivo registrado e `agregado_a`.
2. **Licença e privacidade.**
   - O `robots.txt` é respeitado.
   - Nada passa por login ou CAPTCHA.
   - O DJEN fica desligado, porque traz dado pessoal de réus sem trazer oportunidade.
   - A lista pública do Banco de Projetos (nome e telefone) não é coletada.
   - O CPF sai dos trechos guardados.
3. **O que se guarda:**
   - título;
   - comarca e vara;
   - número do edital;
   - prazo;
   - áreas admitidas e restrição territorial;
   - link oficial (o PDF);
   - evidência curta mascarada.
4. **Fora do escopo agora:** TRF1/SJGO (é o motor 13, com posição fixada pelo titular) e TRT18. Juntar os dois é
   decisão do titular.

| Parâmetro | Meta | Onde se mede |
|---|---|---|
| Cobertura | todo edital de prestação pecuniária anunciado pelo TJGO em até 1 dia útil da notícia, com o computador ligado | `estado/judiciario_go_local.json` → `rss` e `historico` |
| Link oficial | 100% das oportunidades com o PDF ou a notícia oficial | `url` / `url_documento` |
| Prazo | 90% das oportunidades com prazo lido; o resto com `prazo_a_confirmar` | `fim` |
| Duplicata | um registro por edital | `vista_tambem_em` |
| Silêncio | alerta se o computador passar 3 dias sem coletar | `diagnostico.alerta_local` |
| Privacidade | nenhum nome de réu, CPF ou telefone de responsável no git | `verificar_privacidade.py` e testes |

## 7. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| O computador do titular fica desligado | Alerta na nuvem depois de 3 dias. A busca do CNJ continua pela nuvem e pega parte das republicações. |
| O TJGO muda o portal de novo | RSS e `<time datetime>` são padrões do Joomla. A falha de formato aparece no diagnóstico, e os testes usam a estrutura real verificada. |
| O PDF sem camada de texto (escaneado) | Valem os dados da notícia. `sem_texto` conta no diagnóstico. |
| O edital do ano vira OPORTUNIDADE com prazo vencido | A data relativa é resolvida pela publicação. Sem prazo, só vale nos 20 dias seguintes à publicação e com sinal de abertura. |
| A busca do CNJ recusa a nuvem | `recusado_na_nuvem_em` faz o computador ler o CNJ na coleta seguinte. |

## 8. Pendências

1. **Primeira coleta real no computador do titular.** Confirmar a carga inicial de 150 dias (cerca de 130 páginas de
   RSS, em parcelas de 25) e o texto dos PDFs com o pypdf instalado.
2. **Primeira leitura da nuvem.** Confirmar que a busca do CNJ responde ao GitHub. Se recusar, o computador assume
   sozinho.
3. **Previsão por comarca.** Ver o histórico do "acompanhar": Goiânia abre em janeiro. É o próximo passo gratuito.
4. **Decisão do titular:** incluir a Justiça Federal (TRF1/SJGO, hoje o motor 13) e a do Trabalho (TRT18) no mesmo
   leitor.
