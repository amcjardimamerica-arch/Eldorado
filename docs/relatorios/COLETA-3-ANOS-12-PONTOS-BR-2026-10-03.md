# Livros do Brasil: 12 pontos, histórico de 3 anos e estudo preditivo (03/10/2026)

Esta rodada completa a coleta dos 3 anos (relatório `COLETA-3-ANOS-LIVROS-BR-2026-10-03.md`). Agora **cada um dos 1.123 livros do bloco Brasil** foi verificado, e cada oportunidade tem seu relatório individual.

## Resultado em uma linha

Os 1.123 livros têm decisão e os 12 pontos preenchidos, ou com dispensa individual e motivo, ou com "não localizado" e o que fazer. **110 livros seguem pendentes (P)** e **245 têm itens que só o edital em PDF traz**. Eles ficam numa fila de 411 conferências para o navegador do computador do titular.

**O que não foi possível fechar por dentro do sistema, e por quê:** páginas que exigem login ou CAPTCHA (Conanda/MDHC, gov.br, Transferegov), páginas bloqueadas por robots.txt, PDFs que o ambiente não extrai e o limite de requisições do PNCP. Nada disso foi contornado.

## Como foi feito

1. A fila de 1.123 livros foi separada em 142 livros que já tinham os 12 pontos (rodadas de 29/09 a 02/10) e 981 novos.
2. **1ª passagem:** 45 lotes, um livro por vez, na página oficial. Cada livro recebeu decisão (V, A, R, D ou P), os 12 pontos da edição de referência, as edições dos 3 anos com página oficial e trecho, e a previsão.
3. **2ª passagem:** 14 lotes sobre os 274 livros com pendência (185 P, 78 V e 11 R com itens não lidos). Os agentes tentaram outra URL oficial, o Chrome, PDFs e a API do PNCP.
4. O script `scripts/consolidar_12_pontos_br.py` junta tudo, calcula selo e previsão e gera os relatórios.
5. **Dispensa individual:** o item só é "dispensado" quando há motivo escrito (por exemplo, "fluxo contínuo sem data final" ou "não é recurso para OSC"). Item que existe e não foi lido é "não localizado".

## Números

| Decisão | Livros | Significado |
|---|---:|---|
| V | 142 | edital vigente (inscrição aberta ou credenciamento em vigor) |
| A | 247 | última edição encerrada (histórico) |
| R | 88 | programa permanente ou fluxo contínuo |
| D | 536 | não é recurso para OSC: compra de serviço, artista, pessoa física, vaga, concurso, notícia |
| P | 110 | pendente, com motivo e ação |

- **Validação dos 12 pontos:** 768 completa (todos os 536 D e 232 vigentes, históricos ou permanentes), 245 parcial, 110 pendente.
- **Pontos nos 587 livros que não são D:** 4.185 confirmados, 409 "não informado no edital", 284 dispensados (45 pelo próprio edital) e 2.166 "não localizados".
- **Selo estimado dos 587 livros que não são D:** 21 ouro, 119 prata e 447 bronze.
- **Previsão:** 118 livros têm próxima janela. Só 1 tem confiança alta e 39 média; os outros 78 têm confiança baixa.
- **Por que tantos "não localizados":** o edital em PDF só foi lido onde o ambiente conseguiu. No PNCP, só os metadados (objeto, datas, valor) estão confirmados, e os itens Resultado, Prazo de recurso, Requisitos e Anexos exigem abrir a aba Documentos.
- **Aplicabilidade ao titular (V):** 13 "sim", 80 "depende" (território ou perfil), 24 "não". Os demais estão sem resposta registrada.

### Os 110 pendentes

- **24** são livros de tema ou busca genérica do DOU, sem edital identificável. Recomendação: vincular a um edital real ou arquivar.
- **53** têm fonte restrita ou ilegível: login, robots, formulário, PDF binário ou site fora do ar.
- **33** têm edital oficial não localizado.

## Janelas abertas e próximas que interessam à A.M.C.

| Prazo | Oportunidade | Serve à A.M.C.? |
|---|---|---|
| 03/10 (hoje) | Embratur, patrocínio 2026 | depende |
| 04/10 | Fundação Aperam Acesita, 15º edital | não (só Vale do Aço e Jequitinhonha, MG) |
| 05/10 | Rede Memória Viva (Prosas) | sim |
| 08/10 | Fundo Ecos, 52º edital (chamada induzida, protegida por senha) | a conferir |
| 09/10 | Silvânia/GO, PNAB Ciclo 2 | depende |
| 11/10 | CONANDA/SNDCA 01/2026 (prorrogado) | depende |
| 13/10 | Goiatuba/GO, PNAB Ciclo 2 | depende |
| 13/10 | Rouanet nas Favelas 2 | não (favelas de 8 capitais e DF) |
| 16/10 | SEDS-GO, Edital 001/2026 socioeducativo | a conferir |
| 19/10 | Zurich, leis de incentivo (exige projeto já aprovado) | sim |
| 19/10 | Fundo Baobá, Marielle Franco (85% de mulheres negras na direção) | depende |
| 22/10 | Ibama/MMA, Chamamento 03/2026 (Fundo Rio Doce). A nota oficial diz 22/10 e o PDF diz 29/10: conferir | território MG/ES |
| 26/10 | Goiânia, Natal no Parque (R$ 5 mi, MROSC) | sim |
| 26/10 | SECTI-GO, Edital 002/2026 Cidadão Tech 60+ (R$ 1 mi) | a conferir |
| 30/10 | Fundação Maria Emília, FME Transforma 02/2026 | depende |
| 30/10 | MinC, 2º Cultura Viva Pontões (inscrições de 02/10 a 30/10) | depende |
| 31/10 | Lei Rouanet, janela anual no SALIC | sim |
| 08/10 a 01/12 | Secult-GO, Arranjos Regionais FSA | a conferir |
| 09/11 | Grupo Equatorial, chamada de eficiência energética | depende (CEBAS) |
| 11/11 | Fundo Ecos, 50º e 51º editais | não (PI, MA, BA e MS) |
| 04/12 | BNDES Periferias em Rede, 6º ciclo | depende |
| 15/12 | MAPFRE, janela PRONAS/PRONON | depende |
| 11/05/2027 | Senador Canedo/GO, termo de colaboração (R$ 300 mil, OSC inscrita no CMAS) | sim |
| 16/09/2027 | Pirenópolis/GO, termo de colaboração (R$ 300 mil) | sim |

**Atenção ao PRONON e ao PRONAS/PCD:** a página oficial do serviço no gov.br (atualizada em 06/02/2026) diz que não há previsão de submissão de novos projetos. A previsão de outubro, feita no relatório anterior, **não se sustenta**.

## Estudo preditivo

A previsão só nasce de edições com página oficial e data. O script exige 2 ou mais anos com edição para apontar o mês típico e a próxima janela. Se os meses das edições forem muito diferentes, a confiança cai para baixa. O arquivo `estudo_preditivo_br_2026-10-03.json` reúne as 142 janelas abertas e as 118 próximas janelas. Entre as previsões de confiança média ou alta:

- Fundação Cargill, Nutrindo Soluções Locais: junho de 2027 (edições de 2024, 2025 e 2026). Confiança alta.
- Banco do Nordeste, Editais Sociais: agosto de 2027. Confiança média.
- Instituto Neoenergia: março de 2027. Confiança média.
- Raízes e Labora, Educação para o Bem Viver: março de 2027. Confiança média.
- BNDES Periferias: junho de 2027 em uma série e agosto a dezembro no 6º ciclo. As datas variam entre ciclos; confiança baixa.

## Limites da prova

- O texto dos editais em PDF foi lido só onde o ambiente extraiu. A prova das edições é **literal** apenas onde houve trecho entre aspas de página oficial. No restante é "resumo".
- Todos os livros do PNCP têm só os metadados do registro. Em vários o objeto sugere compra de serviço (credenciamento de ILPI, catadores, exames SUS). Foram classificados D quando contratam serviço remunerado e V quando firmam parceria com OSC. **Os casos limítrofes estão marcados na observação de cada livro**, para o titular decidir.
- Alguns livros apontam para a página errada. Isso está registrado em `url_corrigida` e deve ser aplicado ao catálogo.
- Algumas decisões D foram tomadas pelo título porque a página não abriu. A decisão tem esse aviso na observação. Vale uma conferência por amostra.
- O PNCP limitou as consultas (429) por longos períodos e a API de arquivos ficou fora do ar em parte da rodada.
- O selo é estimado pelo script. O selo oficial vem de `python -m src.selo_livros`, que não estava no GitHub.
- Nenhuma instrução dirigida à IA foi encontrada nas páginas lidas. Nenhum CPF foi gravado.

## Conselho de 7 lentes

- **Extremamente pessimista:** 2.166 itens "não localizados" e 110 livros pendentes. Um painel que mostra "12 pontos" sem dizer que o PDF não foi lido vira falsa segurança. Alguns D foram decididos só pelo título e podem esconder uma oportunidade.
- **Pessimista:** a API do PNCP entrega só metadados. Em dezenas de credenciamentos municipais e de órgãos (41 V citam credenciamento) o titular precisará abrir o edital antes de decidir. A linha entre compra de serviço (D) e parceria com OSC (V) é de julgamento.
- **Levemente pessimista:** a previsão com base em uma ou duas edições é fraca, e a maioria dos livros não tem nem isso. Das 118 previsões, 78 são de confiança baixa.
- **Neutro (síntese):**
  - **Decisão:** aplicar. Tratar V e R como candidatos e conferir o edital antes de qualquer inscrição. Rodar a fila de 411 conferências no navegador do computador e recalcular com `python -m src.selo_livros`.
  - **Parâmetros de qualidade:**
    - nenhum item sem status e sem motivo;
    - dispensa só com motivo individual;
    - previsão só com edição oficial datada;
    - decisão por título marcada na observação.
  - **Riscos e mitigação:**

    | Risco | Mitigação |
    |---|---|
    | Credenciamento tratado como fomento | observação em cada caso; conferir o edital |
    | Item dado como "dispensado" que existe | motivo escrito e conferência por amostra de 10% |
    | Página do livro errada | `url_corrigida` aplicada ao catálogo |
    | Prazo vencido no dia | datas conferidas em 03/10; recalcular nas rodadas diárias |
- **Levemente otimista:** 768 livros têm os 12 pontos fechados e cada um tem seu relatório. As 536 exclusões (D) liberam a atenção para o que importa.
- **Otimista:** 142 vigentes, 13 "sim" e 80 "depende" formam uma carteira concreta; a tabela de janelas acima lista as que fecham até 31/10.
- **Extremamente otimista:** com a fila local fechada e a série de 3 anos, o painel avisará a janela seguinte de cada programa antes de o edital sair.

## Arquivos

- `dados/coleta_3_anos/parametros_12_br_2026-10-03.json`: um registro por livro (12 pontos, edições, selo, previsão).
- `dados/coleta_3_anos/relatorios_oportunidades/<id>.md` (1.123 relatórios) e `INDICE-OPORTUNIDADES-BR.csv`.
- `dados/coleta_3_anos/estudo_preditivo_br_2026-10-03.json` e `fila_navegador_local_br_2026-10-03.json`.
- `scripts/consolidar_12_pontos_br.py` e `tests/test_consolidacao_12_pontos_br_2026_10_03.py` (11 testes).
- Materiais de pesquisa: `lotes12/`, `lotes12_out/`, `lotes12b/`, `lotes12b_out/`.
