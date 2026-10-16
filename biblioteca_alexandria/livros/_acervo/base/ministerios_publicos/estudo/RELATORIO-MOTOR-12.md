# Motor 12 — Ministérios Públicos: destinação de recursos de reparação e de bens lesados

**Estudo ao vivo de 02/10/2026.** Período: 02/10/2023 a 02/10/2026.
**Para quem:** A.M.C. Jardim América, OSC de Goiânia, no sistema Eldorado.

**Como foi feito:**

- Navegador do titular, com IP brasileiro, para MP-GO e MPT-GO.
- Leitura na nuvem para MPF, MPDFT, MPM, MPU, CNMP, FDD e Planalto.

**Arquivos deste estudo:**

- `fontes_motor_12.csv`: 48 fontes.
- `historico_3_anos_motor_12.csv`: 92 registros.
- `itens_ancora.md`
- `PROMPT-IMPLANTACAO-MOTOR-12.md`

---

## 0. Resumo em uma página

| Órgão | Registros em 3 anos | Oportunidade hoje | Achado principal |
|---|---|---|---|
| **MPT-GO (PRT 18ª)** | 59. São 43 editais de indicação, mais cadastro, normas e páginas | **2** | Publica **editais de 5 dias** para indicar quem recebe valores de TAC e ações. Saíram 43 de 17/12/2025 a 01/10/2026: 28 da PTM Anápolis e 15 de Goiânia. **O motor antigo nunca os viu**, porque a tabela é montada por script |
| **MP-GO (Destina)** | 2 (edital de cadastro e atos PGJ) | **1** (cadastro contínuo) | O Edital de Chamamento **02/2024** do COMPOR continua vigente. O robots.txt **proíbe todo robô** |
| **MPF (PR-GO e modelos)** | 8 | 0 com prazo; cadastro bienal aberto | A PR-GO abriu o cadastro em 09/10/2025, com regra bienal até cerca de out/2027. Inscrição pelo protocolo eletrônico com login gov.br. Houve doação de bens em out/nov/2025 |
| **MPDFT** | 7 | 0 | O Edital PGJ 1/2026 foi encerrado, com 51 habilitadas em 18/09/2026. É do DF, fora do território da A.M.C. |
| **MPT nacional** | 12 | 0 | A Nota Técnica 9/2025 trata da ADPF 944. Editais das outras regionais são ruído |
| **MPM** | 2 | 0 | Destina caso a caso e não tem cadastro |
| **FDD / CFDD (MJ)** | 2 | 0 | **Nenhum edital para OSC desde 2017.** Em 07/08/2026, "Seleção em andamento" = "Não há" |
| **CNMP, DOU, MPU** | normas e fontes | — | A Res. CNMP 179/2017, art. 5º §1º, permite destinar recursos de TAC **diretamente a entidades** |

**O que está aberto em 02/10/2026:**

1. **MPT-GO, PTM Anápolis, Edital 009220.2026**, de 01/10/2026, procedimento 000037.2019.18.003-6. O valor vai **até R$ 94.428,74**.
   - O prazo é de **5 dias** contados da publicação, e o edital não diz se são úteis ou corridos. Termina entre **06/10/2026** (corridos) e **08/10/2026** (úteis). **Use 05/10/2026 como data segura.**
   - Exige cadastro prévio no Sistema de Destinações. **A A.M.C. não está na lista de habilitadas.**
2. **MPT-GO, cadastro no Sistema de Destinações (Edital PRT18 nº 24/2025):** permanente. **É a porta de entrada para todos os editais de 5 dias.**
3. **MP-GO Destina, Edital de Chamamento 02/2024:** cadastro contínuo, válido até o próximo ato convocatório.
4. **MPF PR-GO, cadastro de bens e valores (09/10/2025):** recebimento contínuo até a próxima edição bienal. O link do edital dá 404. Está classificado como ACOMPANHAR, e não como OPORTUNIDADE, porque o edital não foi lido.

---

## 1. Mapa das fontes

O detalhe de cada fonte está em `fontes_motor_12.csv`. Cada linha tem órgão, unidade, tipo, url, se abre sem login, robots, tipo de página, como ver os antigos, frequência, rota e observação.

### 1.1 MP-GO — prioridade 1

| Tipo | Fonte | O que tem | Rota |
|---|---|---|---|
| Primária | `mpgo.mp.br/portal/conteudo/destina-destinacao-articulada-de-acordos-edital-n-02-2024` | Página do Destina, com Edital 02/2024, Ato PGJ 58/2025 e Anexos I, II e III | **computador_do_titular**, com leitura manual (ver 1.4) |
| Regra | `mpgo.mp.br/robots.txt` | `User-agent: *` / `Disallow: /`. Só Googlebot, Slurp, msnbot e Twitterbot têm regras próprias | — |
| Secundária | Notícias do MP-GO e diário do MP-GO | Pelo mesmo robots, robôs não podem ler | manual |

**Rota do motor:** o robô do Eldorado **não pode ler** o MP-GO. Da nuvem, a conexão também expira.

- O motor registra o Destina como **regra permanente**, com o cadastro vigente.
- Mostra no painel "verificação manual mensal pelo titular".
- Nunca marca a fonte como "lida".

### 1.2 MPT-GO (PRT 18ª Região) — prioridade 2

| Tipo | Fonte | O que tem | Rota |
|---|---|---|---|
| **Primária** | `prt18.mpt.mp.br/servicos/editais-de-destinacao-de-recursos-bens` | Tabela com unidade, data, número do edital, procedimento e PDF. **É montada por JavaScript** | **computador_do_titular** (navegador) |
| Primária (PDF) | mesma página, `?task=baixa&format=raw&arq=<token>` | O PDF tem texto: valor, procedimento, prazo de 5 dias, documentos e critérios | computador_do_titular |
| Secundária | `/servicos/entidades-assistenciais` | 57 entidades habilitadas; **a A.M.C. não consta** | computador_do_titular |
| Secundária | `/servicos/prestacao-de-contas-de-destinacoes` | 1.090 registros de prestação de contas | computador_do_titular |
| Regra | `/informe-se/doacoes-convenios` e o tutorial do Sistema de Destinações | Como se cadastrar | nuvem |
| Regra | `destinacoes.mpt.mp.br` | Sistema nacional de cadastro (JavaScript, com conta) | **só manual**. O cadastro é ato da entidade |

### 1.3 MPU e demais — prioridades 3 e 4

**MPF:**

- **PR-GO.** O caminho atual é `/o-mpf/unidades/pr-go/`; o antigo `mpf.mp.br/go` dá 404.
  - Notícias.
  - Transparência, "bens para doação".
  - Notícia do cadastro de 09/10/2025.
  - Portaria PGR/MPF 1.097/2024.
  - Rota nuvem.
- **Modelos de outras procuradorias:** PR-BA e PR-PB.

**MPDFT:**

- Tag "medidas alternativas".
- Notícias.
- Cema.
- TACs.
- O robots bloqueia `/portal/images/`, onde ficam os PDFs. Por isso o PDF do edital não foi lido.

**MPT nacional:**

- RSS de notícias.
- Nota Técnica 9/2025.
- O Diário Eletrônico (`diario.mpt.mp.br`) **não resolveu**.

**MPM:** notificações e SPDV. São ruído.

**MPU:** o sitemap não tem nada sobre destinação.

**FDD / CFDD (gov.br/mj):**

- Seleção em andamento.
- Seleções anteriores.
- Atas.
- Legislação.
- Transferegov.
- Rota nuvem.

**CNMP:** o PDF da Res. 179/2017 abre na nuvem. A busca de normas exige JavaScript (computador_do_titular).

**DOU (in.gov.br):** a busca exige JavaScript (computador_do_titular).

### 1.4 Ressalva de conduta

Antes de ler o robots.txt do MP-GO, o navegador do titular abriu **uma vez** a página inicial do portal e a página do Destina. Depois que o robots foi lido, não houve mais navegação no MP-GO.

O motor, por ser robô, **não deve** acessar o site.

---

## 2. Histórico de 3 anos

Os 92 registros estão em `historico_3_anos_motor_12.csv`, com todos os campos pedidos. **O que não estava escrito na fonte ficou vazio. Nada foi completado por dedução.**

**MPT-GO, 43 editais de indicação de destinação:**

- Publicados de 17/12/2025 a 01/10/2026.
- Valores de R$ 7 mil a R$ 2,14 milhões. O maior é o 008314.2026, de Anápolis, de 24/08/2026.
- Todos com o mesmo modelo:
  - 5 dias;
  - projeto social obrigatório;
  - cadastro prévio;
  - certidões tributária, previdenciária e de FGTS;
  - declaração de inexistência de parentes de membros.
- A escolha cabe ao membro, por **independência funcional**.
- Critérios: exequibilidade, pertinência temática e histórico da entidade.
- **Não há registro antes de dez/2025.** A tabela começa nessa data, provavelmente por causa do novo marco: Res. CSMPT 232/2025 e Edital 24/2025 (nov/2025).

**MP-GO:** 1 edital de cadastro (02/2024) e os atos PGJ 77/2022, 25/2024 e 58/2025.

**MPF:**

- Cadastro PR-GO (09/10/2025).
- Portaria 1.097/2024.
- Edital de doação 01/2025 (27/10 a 06/11/2025) e seu resultado (26/11/2025).
- Modelos PR-PB e PR-BA.
- 2 itens de ruído: sentença do aterro, que destina a fundo; e o edital de 2023, fora da janela.

**MPDFT:** Edital PGJ 1/2026, com etapas em abril, julho e setembro de 2026; balanço de 2024; uma destinação das Semas; e 2 de ruído.

**MPT nacional:** 3 a acompanhar (NT 9/2025 e as convocações de 30/10/2025 e 27/08/2026) e 9 editais de outras regionais (ruído).

**MPM:** 1 ANPP de 2024 e 1 edital de notificação (ruído).

**FDD:** NAS 2023 e Pronasci 2/2023. São só para entes públicos, então são ruído.

## 3. Classificação

| Classe | Total | Critério |
|---|---|---|
| **OPORTUNIDADE** | 3 | Aberto em 02/10/2026, para entidade privada sem fins lucrativos, no território da A.M.C. (Goiás) |
| **ACOMPANHAR** | 68 | Encerrado, mas mostra o padrão; ou norma; ou cadastro de outra UF que serve de modelo; ou etapa de edital |
| **RUÍDO** | 21 | Outra UF sem efeito para a A.M.C.; destino exclusivo a fundos ou entes públicos; notificação processual; fora da janela |

Cada linha do CSV traz o **motivo** da classificação.

## 4. Calendário

| Fonte | Ritmo observado | O que o motor faz |
|---|---|---|
| **MPT-GO editais de 5 dias** | Cerca de **4 a 5 por mês**, sem calendário. Em 2026 saíram em quase todas as semanas | Ler **todo dia útil**. Alerta imediato, porque 5 dias não toleram leitura semanal |
| MPT-GO cadastro | Permanente; a convocação para atualizar saiu em 30/10/2025 | Ler mensalmente |
| MP-GO Destina | Edital vigente até o próximo ato; destinações caso a caso | Verificação manual mensal |
| MPF PR-GO cadastro | Bienal: 09/10/2025, e a próxima edição deve sair por volta de out/2027 | Mensal; alerta a partir de set/2027 |
| MPF PR-GO doação de bens | Jan/2023 e out/2025, com 10 dias de prazo | Semanal entre setembro e dezembro |
| MPDFT | Edital PGJ em março ou abril; balanços bienais em março | Mensal (fora do território) |
| Outras regionais do MPT | Concentradas entre junho e outubro | Só para estatística |
| FDD / CFDD | Sem edital desde 2023. O CFDD se reúne na última quinta do mês: 29/10, 26/11 e 17/12/2026 | Mensal, depois de cada reunião |

## 5. Programa Destina (MP-GO) — como funciona e como a A.M.C. participa

**O que é.** É o Projeto DAAMP, Destinação Articulada de Acordos do MP-GO, conduzido pelo **COMPOR** (Centro de Autocomposição de Conflitos e Segurança Jurídica). Suas regras estão nos Atos PGJ 77/2022, 25/2024 e 58/2025.

- Os valores e bens de acordos (TAC, ANPP, transações) deixam de ser destinados caso a caso, sem publicidade.
- Passam a ir para entidades **previamente cadastradas** pelo Edital de Chamamento 02/2024.
- A base é a Res. CNMP 179/2017 (art. 5º §1º) e a Res. Conjunta CNJ/CNMP 10/2024.

**Como funciona:**

1. **Cadastro contínuo.** O edital 02/2024 "permanecerá vigente até a publicação do ato convocatório seguinte". A entidade pede o cadastro com os anexos I a III do edital.
2. **Análise do COMPOR.** O COMPOR defere, indefere ou pede complementação. **O cadastro não garante recebimento.**
3. **Destinação.** O promotor do caso escolhe entre as cadastradas, conforme a pertinência com o dano, e a entidade recebe bens ou valores.
4. **Prestação de contas em 30 dias** para `prestacaodecontas@mpgo.mp.br`, com comprovante fiscal, nota de entrega e fotos.

**Contato:** telefone (62) 3243-8116; WhatsApp (62) 99432-3082.

**O que a A.M.C. precisa fazer.** Tudo isto é ato do presidente; o sistema não preenche nem envia nada.

1. Baixar, na página do Destina, o Edital 02/2024, o Ato PGJ 58/2025 e os Anexos I, II e III. Conferir a lista de documentos, que não foi transcrita aqui porque o PDF não foi aberto.
2. Montar o kit permanente:
   - estatuto e ata de eleição vigentes;
   - CNPJ;
   - certidões federais, estaduais, municipais, de FGTS e trabalhista;
   - conta bancária exclusiva;
   - relatório de atividades;
   - fotos;
   - declaração de inexistência de parentesco com membros do MP.
3. Enviar o pedido de cadastro pelo canal indicado no edital e **guardar o protocolo**.
4. Ter **2 ou 3 projetos-modelo prontos**, com objeto, público, cronograma e custos por etapa, alinhados às áreas de dano mais comuns em acordos: consumidor, meio ambiente urbano, infância e idosos.
5. Depois de receber, prestar contas em 30 dias.

**Mesma lógica no MPT-GO, e é mais urgente.** A A.M.C. precisa se cadastrar no **Sistema de Destinações** (`destinacoes.mpt.mp.br`), conforme o Edital PRT18 24/2025 e a Portaria PRT18 124/2025. Depois disso pode responder aos editais de 5 dias com um projeto.

- O tema é trabalhista, com pertinência ao procedimento de cada edital. Por exemplo: qualificação profissional, combate ao trabalho infantil e saúde e segurança no trabalho.
- Projetos de assistência social genérica tendem a perder em pertinência.

## 6. Léxico

**Termos que indicam o alvo:**

- destinação de recursos ou bens; indicação de destinação; reversão de bens e recursos.
- edital de chamamento para cadastramento; cadastro de órgãos e entidades; entidades assistenciais; habilita instituições.
- Sistema de Destinações; Destina; DAAMP; COMPOR.
- prestação pecuniária; medidas alternativas; multas e indenizações; dano moral coletivo; TAC; ANPP.
- bens e valores; Res. Conjunta CNJ/CNMP 10/2024; Res. CNMP 179/2017; Res. CSMPT 232/2025; Portaria PGR/MPF 1.097/2024.
- Fundo de Defesa de Direitos Difusos; CFDD; carta-consulta; seleção em andamento.

**Falsos positivos que o motor deve vetar:**

- "destinação de vagas" (concurso ou PCD).
- "chamamento público" para comprar ou alugar imóvel do próprio MP.
- Editais de notificação do MPM.
- Lista de TACs sem chamamento.
- "Lista Suja" e cadastro gov.br.
- Destinação a **fundos e órgãos públicos**: Fundo de Modernização da PCDF, Bombeiros, municípios, FDD.
- Notícias "custeado por destinações", quando o projeto já foi escolhido.
- "Bloqueio de bens e valores" em operações.
- Editais da SAJU/MJ.
- Edital CFDD 1/2022, que escolhe quem compõe o Conselho.
- Editais FDD restritos a entes públicos.
- Pregão ou licitação com a palavra "edital".
- Estágio ou processo seletivo.
- Datas de modificação de arquivo que não são data de publicação: por exemplo, o edital MPF 1/2023 modificado em 2026.

## 7. O que não foi confirmado, e por quê

| Ponto | Motivo |
|---|---|
| Documentos exatos e PDF do Edital Destina 02/2024 | O robots do MP-GO proíbe robôs. A extensão do navegador ficou instável e os endereços dos anexos não foram extraídos |
| Se os 5 dias do MPT-GO são úteis ou corridos | O edital não diz |
| Texto do Edital PRT18 24/2025 e da Portaria 124/2025 | PDFs em `/images/`, proibido pelo robots da PRT18 |
| Número e PDF do edital de cadastro da PR-GO (2025) | O link oficial dá 404. Pedir à PR-GO: prgo-chefiagabinete@mpf.mp.br |
| Cláusulas do Edital MPDFT 1/2026 | PDF em `/portal/images/`, bloqueado pelo robots |
| Editais do MPT-GO antes de dez/2025 | A tabela começa em 17/12/2025. Não se sabe se houve antes com outro formato |
| Diário Eletrônico do MPT | `diario.mpt.mp.br` não resolveu |
| Versão compilada da Res. CNMP 179/2017 | A busca do CNMP exige JavaScript |
| DOU | A busca exige JavaScript; não foi consultado |
| Ata 298ª e atas 299ª a 301ª do CFDD | Não listadas na página |

**Anti-injeção:** nenhuma página lida trouxe instrução dirigida ao agente. **Nada foi ignorado por esse motivo.**

**Privacidade:** não foi coletado nenhum CPF nem nome de investigado, réu ou beneficiário pessoa física. Só aparecem nomes de órgãos e números de procedimento, que são públicos.

---

## 8. Conselho de 7 lentes

Conselheiros: chief engineers, staff engineers e CTOs de big tech, e professores de computação.

**1. Extremamente pessimista** — Dra. Iolanda Bastos, ex-CTO de plataforma de pagamentos.

- A janela de 5 dias com leitura que depende do computador do titular é uma armadilha. Se o computador ficar desligado num feriado prolongado, perde-se o edital.
- O MP-GO proíbe robôs, então metade do motor é cega por definição.
- E a A.M.C. nem está cadastrada no MPT-GO: o motor vai gerar alertas que ela não pode responder.

**2. Pessimista** — Prof. Renato Quintela, sistemas distribuídos.

- A tabela do MPT-GO é JavaScript, e o PDF vem com token. Os tokens podem expirar ou mudar de formato, e se o motor gravar o link com token, o link quebra.
- O motor deve gravar a **chave natural** (unidade + número do edital + procedimento) e o link da listagem, nunca o token como identidade.

**3. Levemente pessimista** — Eng. Márcia Tavares, staff engineer de dados.

- O risco é de **duplicação**: o mesmo edital pode aparecer na listagem, na notícia e no DOU.
- Também há risco de **datas erradas**, porque a data de modificação de arquivo foi confundida com publicação no edital MPF 1/2023.
- O histórico precisa entrar nos livros **uma vez**, com marcador de estado.

**4. Neutro** — Dr. Augusto Prado, CTO e professor convidado. **Síntese e decisão:**

- **Decisão:** implantar o Motor 12 em três trilhas.
  - **(a) MPT-GO, prioridade máxima.** Leitura diária da listagem pelo computador do titular (coleta local) e extração do PDF. Gera alerta "5 dias" com data-limite segura, calculada pela contagem corrida a partir do dia seguinte à publicação, menos um dia.
  - **(b) Regras permanentes,** sem leitura robótica: MP-GO Destina, MPT-GO cadastro, MPF PR-GO cadastro bienal e FDD. O motor registra o estado e pede verificação manual mensal.
  - **(c) Nuvem para MPF, MPDFT, MPT nacional e FDD,** com filtro territorial Goiás e o veto de fundos e entes públicos.
- **Parâmetros de qualidade:**
  1. Os 3 itens-âncora do MPT-GO são reencontrados nos testes sem rede.
  2. Zero registro duplicado pela chave natural.
  3. `data_publicacao` e `data_consulta` em todo registro.
  4. Nenhuma fonte com robots proibitivo marcada como "lida".
  5. Nenhum dado de pessoa física.
- **Riscos e mitigação:**

| Risco | Mitigação |
|---|---|
| Perder um edital de 5 dias | Leitura diária, e alerta por e-mail ou push no mesmo dia |
| Token do PDF expira | Chave natural, com o token só como "último link visto" |
| A A.M.C. não está cadastrada | Pendência ao presidente: "cadastrar no Sistema de Destinações" |
| Pertinência temática baixa | Kit de projetos-modelo trabalhistas |
| Robots do MP-GO | Rota manual; nunca robô |
| Duplicação | Chave natural e mescla por fonte |

**5. Levemente otimista** — Eng. Luana Ribeiro, chief engineer de busca.

- O achado é forte: 43 editais em menos de 10 meses, num canal que o sistema não via.
- O modelo do PDF é idêntico entre os editais. Um extrator de regex simples tira valor, procedimento e prazo com alta precisão, em biblioteca-padrão.

**6. Otimista** — Prof. Caio Menezes, recuperação de informação.

- Com 1.090 prestações de contas públicas e 57 habilitadas, o motor pode **aprender o perfil vencedor**: temas, faixas de valor, unidade e quais entidades recebem com frequência.
- Assim gera o "ranking de pertinência" de cada edital para a A.M.C. antes mesmo de ela abrir o PDF.

**7. Extremamente otimista** — Dra. Helena Saraiva, CTO de govtech.

- O MPT-GO destinou milhões em 2026; só o 008314.2026 vale R$ 2,14 milhões.
- Com o cadastro feito, projetos prontos e o alerta diário, a A.M.C. passa a concorrer a uma **fonte recorrente e quase invisível às outras OSCs**, com prazo curto que favorece quem está preparado.
- Some-se o Destina e o MPF, e é um canal novo de captação inteiro.

---

**Fontes principais:**

- [MPT-GO editais](https://www.prt18.mpt.mp.br/servicos/editais-de-destinacao-de-recursos-bens)
- [MPT-GO entidades](https://www.prt18.mpt.mp.br/servicos/entidades-assistenciais)
- [MP-GO Destina](https://www.mpgo.mp.br/portal/conteudo/destina-destinacao-articulada-de-acordos-edital-n-02-2024)
- [MPF PR-GO cadastro](https://www.mpf.mp.br/o-mpf/unidades/pr-go/noticias/mpf-em-goias-cadastra-entidades-e-orgaos-publicos-para-recebimento-bens-e-valores-decorrentes-da-atuacao-da-instituicao)
- [FDD seleção em andamento](https://www.gov.br/mj/pt-br/assuntos/seus-direitos/consumidor/direitos-difusos/selecao-em-andamento)
- [Res. CNMP 179](https://www.cnmp.mp.br/portal/images/Resolucoes/Resolu%C3%A7%C3%A3o-179.pdf)
