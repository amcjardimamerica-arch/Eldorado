# Livros do Brasil: 12 pontos, histórico de 3 anos e estudo preditivo (03/10/2026)

Esta rodada completa a coleta dos 3 anos (relatório `COLETA-3-ANOS-LIVROS-BR-2026-10-03.md`). Agora **cada um dos 1.123 livros do bloco Brasil** foi verificado, e cada oportunidade tem seu relatório individual.

## Resultado em uma linha

Os 1.123 livros têm decisão e os 12 pontos preenchidos, ou com dispensa individual e motivo, ou com "não localizado" e o que fazer. Após a 3ª passagem (leitura dos editais em PDF), **924 livros têm os 12 pontos fechados, 129 ficam parciais e 70 seguem pendentes (P)**. Em 146 livros o edital em PDF foi de fato aberto e lido.

**O que não foi possível fechar, e por quê:** a API de arquivos do PNCP (que lista os PDFs dos editais) respondeu 503 durante toda a 3ª passagem e foi testada de novo em 04/10 com o mesmo resultado; por isso os editais de credenciamento e chamamento hospedados no PNCP continuam só com os metadados. Há também páginas com login ou CAPTCHA, bloqueio por robots.txt e PDFs ilegíveis pela automação. Nada disso foi contornado. Quando a API voltar, basta repetir os lotes 1 a 3 (e parte dos lotes 4, 6, 7, 9, 10, 18, 20, 21 e 24) de `lotes12c/`.

## Como foi feito

1. A fila de 1.123 livros foi separada em 142 livros que já tinham os 12 pontos (rodadas de 29/09 a 02/10) e 981 novos.
2. **1ª passagem:** 45 lotes, na página oficial: decisão, 12 pontos, edições dos 3 anos e previsão.
3. **2ª passagem:** 14 lotes sobre os 274 livros com pendência (outra URL oficial, Chrome, PDFs, API do PNCP).
4. **3ª passagem:** 26 lotes para abrir o edital em PDF de cada V, R e A e completar Resultado, Prazo de recurso, Requisitos e Anexos. Mudou várias decisões (por exemplo, Rouanet nas Favelas 2 passou a R, por ser restrito a 8 locais fora de Goiás).
5. `scripts/consolidar_12_pontos_br.py` junta as 3 passagens, calcula selo e previsão e gera os relatórios.
6. **Dispensa individual:** o item só é "dispensado" com motivo escrito. Item que existe e não foi lido é "não localizado".

## Números

| Decisão | Livros | Significado |
|---|---:|---|
| V | 143 | edital vigente (inscrição aberta ou credenciamento em vigor) |
| A | 259 | última edição encerrada (histórico) |
| R | 110 | programa permanente ou fluxo contínuo |
| D | 541 | não é recurso para OSC: compra de serviço, artista, pessoa física, vaga, concurso, notícia |
| P | 70 | pendente, com motivo e ação |

- **Validação dos 12 pontos:** 924 completa, 129 parcial, 70 pendente.
- **Pontos nos 582 livros que não são D:** 5.020 confirmados (antes 4.185), 515 "não informado no edital", 298 dispensados e 1.151 "não localizados" (antes 2.166).
- **Selo estimado dos 582 livros que não são D:** 21 ouro, 128 prata e 433 bronze.
- **Previsão:** 120 livros têm próxima janela: 1 alta, 39 média e 80 baixa.
- **Aplicabilidade ao titular (V):** 25 "sim", 72 "depende", 21 "não"; 18 sem resposta registrada.

### Os 70 pendentes

- **28** são livros de tema ou busca genérica do DOU, sem edital identificável. Recomendação: vincular a um edital real ou arquivar.
- **27** têm fonte restrita ou ilegível: login, robots, formulário ou PDF binário.
- **15** têm edital oficial não localizado: conferir o site do órgão.

### Principais achados da leitura dos PDFs

- **Pontões Cultura Viva 11/2026 (MinC):** 02 a 30/10/2026, R$ 7,85 mi, recurso em 3 dias úteis.
- **Natal no Parque (Goiânia):** até 26/10/2026, R$ 5 mi, 12 anexos.
- **Goiatuba, PNAB Ciclo 2:** R$ 156 mil, inscrição até 13/10, resultado final 06/11, recursos em 21 a 23/10 e 31/10 a 04/11.
- **Criança Esperança/UNESCO:** 05/10 a 08/11/2026, R$ 150/200/250 mil por projeto, exige 3 anos de CNPJ; Goiás entra na cota do Centro-Oeste.
- **Fundo Baobá, Marielle Franco 2:** inscrições de 14/09 a 19/10, resultado 11/01/2027.
- **Zurich:** projeto já aprovado em lei de incentivo; sem recurso contra o resultado final.
- **Lei Rouanet:** recurso em 10 dias (IN MinC 29/2026). **Esporte:** a Lei de Incentivo foi substituída pela LC 222/2025.
- **Fundo Ecos 50º e 51º:** só PI, MA, BA e MS. **Fundação Aperam:** só Vale do Aço e Jequitinhonha. **Camargo Fellowship:** só pessoa física.
- **BNDES Fundo Socioambiental:** chamada permanente aberta apenas para Periferias 5º ciclo e Corais; o Roteiro está no Portal do Cliente (login).
- **Divergências entre PDF e página** (registradas na observação): Renner, Oncoguia, Vozes Periféricas, Escolas Livres, Evoluir 2024, iCS, Ibama/Fundo Rio Doce (22/10 na nota contra 29/10 no PDF) e Mestra Francisca Rodrigues (28/09 no edital contra 05/10 no Mapa Cultural).

## Janelas abertas e próximas que interessam à A.M.C.

| Prazo | Oportunidade | Serve à A.M.C.? |
|---|---|---|
| 03/10 (hoje) | Embratur, patrocínio 2026 | depende |
| 04/10 | Fundação Aperam Acesita, 15º edital | não (só Vale do Aço e Jequitinhonha, MG) |
| 05/10 | Rede Memória Viva (Prosas) | sim (apoio técnico, sem financiamento direto) |
| 07 e 09/10 | Chamamentos PNAB/Aldir Blanc municipais (8/2026 e 003/2026) | depende do município |
| 14/10 | 1º chamamento público do programa de Fortaleza (fuso Fortaleza) | depende |
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

A previsão só nasce de edições com página oficial e data. O script exige 2 ou mais anos com edição para apontar o mês típico e a próxima janela. Se os meses das edições forem muito diferentes, a confiança cai para baixa. O arquivo `estudo_preditivo_br_2026-10-03.json` reúne as 143 janelas abertas e as 120 próximas janelas. Entre as previsões de confiança média ou alta:

- Fundação Cargill, Nutrindo Soluções Locais: junho de 2027 (edições de 2024, 2025 e 2026). Confiança alta.
- Banco do Nordeste, Editais Sociais: agosto de 2027. Confiança média.
- Instituto Neoenergia: março de 2027. Confiança média.
- Raízes e Labora, Educação para o Bem Viver: março de 2027. Confiança média.
- BNDES Periferias: junho de 2027 em uma série e agosto a dezembro no 6º ciclo. As datas variam entre ciclos; confiança baixa.

## Limites da prova

- O texto dos editais em PDF foi lido só onde o ambiente extraiu. A prova das edições é **literal** apenas onde houve trecho entre aspas de página oficial. No restante é "resumo".
- Os livros do PNCP têm só os metadados do registro (API de arquivos em 503, testada de novo em 04/10). Em vários o objeto sugere compra de serviço (credenciamento de ILPI, catadores, exames SUS). Foram classificados D quando contratam serviço remunerado e V quando firmam parceria com OSC. **Os casos limítrofes estão marcados na observação de cada livro**, para o titular decidir.
- Alguns livros apontam para a página errada. Isso está registrado em `url_corrigida` e deve ser aplicado ao catálogo.
- Algumas decisões D foram tomadas pelo título porque a página não abriu. A decisão tem esse aviso na observação. Vale uma conferência por amostra.
- O PNCP limitou as consultas (429) por longos períodos e a API de arquivos ficou fora do ar em parte da rodada.
- O selo é estimado pelo script. O selo oficial vem de `python -m src.selo_livros`, que não estava no GitHub.
- Nenhuma instrução dirigida à IA foi encontrada nas páginas lidas. Nenhum CPF foi gravado.

## Conselho de 7 lentes

- **Extremamente pessimista:** 1.151 itens "não localizados" e 70 livros pendentes; o PNCP ficou sem PDFs. Um painel que mostra "12 pontos" sem dizer que o PDF não foi lido vira falsa segurança. Alguns D foram decididos só pelo título e podem esconder uma oportunidade.
- **Pessimista:** a API do PNCP entrega só metadados. Em dezenas de credenciamentos municipais e de órgãos (dezenas de V citam credenciamento) o titular precisará abrir o edital antes de decidir. A linha entre compra de serviço (D) e parceria com OSC (V) é de julgamento.
- **Levemente pessimista:** a previsão com base em uma ou duas edições é fraca, e a maioria dos livros não tem nem isso. Das 120 previsões, 80 são de confiança baixa.
- **Neutro (síntese):**
  - **Decisão:** aplicar. Tratar V e R como candidatos e conferir o edital antes de qualquer inscrição. Rodar a fila de conferências do arquivo `fila_navegador_local_br_2026-10-03.json` no navegador do computador e recalcular com `python -m src.selo_livros`.
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
- **Levemente otimista:** 924 livros têm os 12 pontos fechados e cada um tem seu relatório. As 541 exclusões (D) liberam a atenção para o que importa.
- **Otimista:** 143 vigentes, 25 "sim" e 72 "depende" formam uma carteira concreta; a tabela de janelas acima lista as que fecham até 31/10.
- **Extremamente otimista:** com a fila local fechada e a série de 3 anos, o painel avisará a janela seguinte de cada programa antes de o edital sair.

## Arquivos

- `dados/coleta_3_anos/parametros_12_br_2026-10-03.json`: um registro por livro (12 pontos, edições, selo, previsão).
- `dados/coleta_3_anos/relatorios_oportunidades/<id>.md` (1.123 relatórios) e `INDICE-OPORTUNIDADES-BR.csv`.
- `dados/coleta_3_anos/estudo_preditivo_br_2026-10-03.json` e `fila_navegador_local_br_2026-10-03.json`.
- `scripts/consolidar_12_pontos_br.py` e `tests/test_consolidacao_12_pontos_br_2026_10_03.py` (11 testes).
- Materiais de pesquisa: `lotes12/`, `lotes12_out/`, `lotes12b/`, `lotes12b_out/`, `lotes12c/`, `lotes12c_out/`.
