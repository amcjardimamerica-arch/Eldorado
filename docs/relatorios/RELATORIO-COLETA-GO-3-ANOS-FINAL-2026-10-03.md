# Relatório — Coleta de 3 anos dos livros de Goiás (03/10/2026)

Janela: 03/10/2023 a 03/10/2026. Fila de Goiás: 374 livros (selo ainda não ouro). Método: leitura das APIs oficiais pelo navegador do titular (IP do Brasil), sem inventar nada; toda edição gravada tem página oficial, data e trecho literal.

## Resultado

| Item | Antes | Depois |
|---|---|---|
| Livros de Goiás com edição anterior comprovada | 0 | 131 (177 edições: 2023 = 40, 2024 = 89, 2025 = 58) |
| Selos de Goiás (bloco GO, 387 livros) | ouro 15 · prata 51 · bronze 321 | ouro 72 · prata 73 · bronze 242 |
| Selos do sistema (2.180 livros) | ouro 30 · prata 291 · bronze 1.859 | ouro 87 · prata 313 · bronze 1.780 |

## Fontes que renderam prova (e como foram lidas)

1. Sites do Governo de Goiás (goias.gov.br/cultura, /social, /fapeg, /esporte): API WordPress, 1.600 publicações de 2023–2026, leitura de data e trecho.
2. Prefeitura de Goiânia (/wp-json): Lei Paulo Gustavo 2023, PNAB 2024, Lei Municipal de Incentivo à Cultura 2024.
3. Prefeitura de Senador Canedo e de Anápolis (/wp-json): PNAB 2024–2025 e Fundo Municipal de Cultura 2023/2024.
4. PNCP (/api/search com CNPJ do órgão): campos data_inicio_vigencia e data_fim_vigencia dão abertura e encerramento exatos. Foi a fonte mais limpa; vale replicar para os blocos BR e UF.

## Séries confirmadas (livros que viraram ouro)

Pontos e Pontões de Cultura (2024, 2025), Programa Goyazes (2024, 2025), Fica (2024, 2025), Circuito das Cavalhadas (2024, 2025), Natal do Bem (2023, 2024, 2025), chamamento de OSC da Política Nacional Aldir Blanc (2023, 2025), PNAB de Senador Canedo (2024, 2025), chamamentos anuais da Secult pela Lei 13.019 (2024, 2025), Programa de Mobilidade Internacional da FAPEG (2024, 2025), Bolsas de Formação da FAPEG (2024, 2025), Tecnova (2024, 2025), listagem geral de chamadas da FAPEG (2023, 2024, 2025), Rede Municipal de Pontos de Cultura de Goiânia (2024, 2025), agentes culturais de audiovisual de um município (2023, 2024), credenciamento de prestadores de um município (2024, 2025).

Correção ao que informei antes: o livro "Goiás pelo Mundo" (FAPEG 08/2026) tem edições anteriores como Programa de Mobilidade Internacional (CP 11/2024 e CP 21/2025). Eu havia registrado "sem edição" no teste inicial; a coleta corrigiu.

## O que ficou pendente (243 livros) e por quê

| Grupo | Livros | Situação |
|---|---|---|
| Sem série oficial achada nas fontes lidas | 124 | Próximo passo: Diário Oficial do município/estado e site do órgão |
| Oportunidade estrutural (catálogo) | 28 | Histórico depende do financiador |
| Fundos FIA/CEDCA/FMDCA/FMI | 21 | Conferir editais dos conselhos |
| Emenda parlamentar (ALEGO) | 20 | Não é edital; janela vem da LOA; portal sem API |
| Ministérios Públicos (MPT, MPF, MPGO) | 17 | Tabela atual só lista editais vigentes |
| CNJ / TJGO (prestação pecuniária) | 11 | Sem edição própria comparável |
| Ruído (vacina, CRLV, Encceja, vagas de emprego, cursos, convocação de aprovados) | 22 | Não é captação: sugiro arquivar o livro |

Cada um dos 243 carrega a observação com o motivo no próprio livro (arquivo `go_2026-10-03_z_pendentes.json`).

## Conselho de 7 lentes (neutro decide)

- Extremamente pessimista: boa parte das "edições" é página de notícia ou índice; abertura pela data de publicação pode adiantar ou atrasar a janela real em semanas.
- Pessimista: séries por tema (PNAB por linguagem) copiam a mesma prova para várias categorias; o edital específico pode não ter existido em 2024.
- Levemente pessimista: PDFs dos editais da FAPEG não foram lidos; faltam encerramentos.
- Neutro: aceitar o selo ouro só onde há duas edições em anos distintos com página oficial; marcar na observação quando a abertura é a data de publicação; auditar por amostra 10% das séries antes de usar a previsão de janela.
- Levemente otimista: Goiás passou de 15 para 72 livros ouro em uma rodada.
- Otimista: o PNCP entrega abertura e encerramento exatos; replicar nos 996 livros do Brasil e nos 726 das UFs é rápido.
- Extremamente otimista: com os meses típicos de cada série (fev–abr Cavalhadas e Fica, ago–set PNAB, out Natal do Bem), o painel já pode avisar a janela seguinte antes do edital sair.

Parâmetros de qualidade e mitigação: (1) nenhuma edição sem página oficial e data; (2) auditar 10% das séries por amostragem; (3) livros "ruído" saem da fila; (4) rodar o mesmo método do PNCP nos blocos BR e UF; (5) ler os PDFs da FAPEG para completar encerramentos.

## Como aplicar

1. Fazer `git fetch` do bundle `coleta-go.bundle` e fundir na branch de trabalho, ou copiar os arquivos do RAR por cima do repositório.
2. Rodar `python -m src.selo_livros` (recalcula selos e a fila) e `python -m unittest tests.test_selo_livros tests.test_selos_nas_abertas`.
3. Abrir o PR com o título "Coleta 3 anos — livros de Goiás".
