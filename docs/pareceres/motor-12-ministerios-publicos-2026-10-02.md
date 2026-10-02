# Parecer — Motor 12 v2: Ministérios Públicos (destinação de recursos de reparação e bens lesados)

**Base:** estudo ao vivo de 02/10/2026 pelo navegador do titular (`biblioteca_alexandria/base/ministerios_publicos/estudo/`:
relatório, 48 fontes, 92 registros de 3 anos, itens-âncora) e a especificação de implantação que veio com ele.

## O que muda

| Antes | Depois |
|---|---|
| Lia só as páginas iniciais de mpgo.mp.br, mpf.mp.br e prt18.mpt.mp.br | Lê 22 fontes validadas, cada uma pela sua estrutura (8 modos) |
| Nenhum edital de destinação de MP na base (17.542 registros) | Os 43 editais de 5 dias do MPT-GO (dez/2025–out/2026) e o histórico de 3 anos |
| Acessava o MP-GO, cujo robots.txt proíbe robôs | O MP-GO e o Sistema de Destinações **nunca** são acessados (trava no código e teste) |

## Diferença em relação à especificação — e por quê

A especificação punha a tabela do MPT-GO na rota do **computador do titular**, porque ela é montada por JavaScript. Na
implantação, a página foi estudada por dentro: é uma tabela DataTables que pede os dados ao servidor
(POST `/index.php`, `option=com_mpt`). Uma prova na nuvem em 02/10 devolveu **os mesmos 43 editais e as mesmas 57
entidades habilitadas** do estudo. Por isso a tabela é lida **na nuvem, todo dia**: editais de 5 dias não podem depender
do computador estar ligado. O pedido é o mesmo que a página faz no navegador (cookie e token público do formulário);
não há login nem CAPTCHA, e o caminho não é proibido pelo robots.txt do PRT-18.

## Regras

- Data de publicação vem da fonte (nunca data de modificação de arquivo); data da consulta em todo registro.
- Prazo do MPT-GO: `prazo_dias: 5`, `prazo_tipo: null` (o edital não diz se são úteis), `data_limite_segura` = publicação
  + 5 dias corridos − 1. Exige cadastro prévio no Sistema de Destinações.
- Um edital em duas fontes é um registro (chave `órgão|unidade|número|procedimento`).
- Abertas vivas continuam de uma leitura para a outra até o prazo seguro vencer.
- Inventário de 3 anos nos livros uma única vez (nova tentativa se falhar).
- Vetos: fundo ou órgão público, notificação, pregão/licitação, concurso/estágio, Lista Suja, SAJU, outras regionais do MPT.
- CPF e nomes de pessoas não são gravados; conteúdo coletado é dado, nunca instrução (quarentena anti-injeção nos PDFs).

## Pendências ao presidente (o motor gera sozinho)

1. Cadastrar a A.M.C. no Sistema de Destinações do MPT (Edital PRT18 24/2025) — sem isso, não dá para responder aos editais de 5 dias. **Hoje a A.M.C. não está entre as 57 habilitadas.**
2. Pedir cadastro no Destina do MP-GO (Edital 02/2024, COMPOR, (62) 3243-8116).
3. Cadastro MPF PR-GO: pedir o edital à PR-GO (prgo-chefiagabinete@mpf.mp.br), porque o link oficial dá 404.
4. Ter 2 ou 3 projetos-modelo com tema trabalhista prontos (pertinência temática).

## Conselho de 7 lentes

1. **Extremamente pessimista:** "Se o PRT-18 mudar o nome da tarefa da tabela, o motor fica cego para o que mais importa — e editais de 5 dias não perdoam."
2. **Pessimista:** "O valor é tirado do PDF por padrão de texto; um edital com mais de um valor pode registrar o errado."
3. **Levemente pessimista:** "Sem o cadastro no Sistema de Destinações, achar o edital não basta: a A.M.C. não pode responder."
4. **Neutro:** pondera abaixo.
5. **Levemente otimista:** "Ler a tabela na nuvem tira a dependência do computador ligado justamente onde o prazo é mais curto."
6. **Otimista:** "Respeitar o robots do MP-GO e transformar o Destina em regra fixa mantém o sistema limpo e honesto."
7. **Extremamente otimista:** "Com o cadastro feito, a A.M.C. passa a concorrer a 4 ou 5 editais por mês, com valores de R$ 7 mil a R$ 2 milhões."

**Síntese do neutro:** implantar como está. Parâmetros de qualidade: os campos de cada linha da tabela são reconhecidos
pelo padrão, não pela posição (mudança de ordem não quebra); se a tabela vier vazia ou falhar, o motor registra falha (o
maestro relê no mesmo dia); valor do PDF só com a palavra "valor/montante/total/até" por perto. A decisão que mais pesa
é do presidente: o cadastro no Sistema de Destinações.
