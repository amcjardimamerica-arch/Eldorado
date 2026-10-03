# Selo do livro — Ouro, Prata e Bronze pelo histórico de 3 anos (03/10/2026)

## O que muda
A **oportunidade** continua com a sua estrela (site oficial → prata; + prazo e os 12 dados → ouro; senão bronze). O
**livro** ganha um selo próprio — um **ícone de livro ao lado da estrela** no cartão da oportunidade e no cartão da
Biblioteca — que mede o quanto o histórico dos últimos 3 anos permite prever a próxima edição:

| Selo do livro | Regra |
|---|---|
| **Ouro** | edições em 2 ou mais anos distintos entre 03/10/2023 e 03/10/2026, com ao menos uma edição anterior a 2026 provada em página oficial e com data de inscrição |
| **Prata** | há edição anterior a 2026, mas sem página oficial ou data suficientes (ou recorrência em um só ano) |
| **Bronze** | nenhuma edição anterior a 2026 na janela (só a edição atual, ou nada) — precisa da coleta dos 3 anos |

Regras de contagem: várias capturas do mesmo edital no mesmo mês são **uma** edição; o ano é o da publicação/abertura
(credenciamento com vigência até 2031 não é edição de 2031); agregador e notícia não provam edição.

Cada livro passa a guardar `selo_livro`: selo, motivo, se teve edital nos 3 anos, anos com edição, as edições, e o
**preditivo** (mês típico, duração típica, próxima janela, confiança alta/média/baixa) e o que falta para ouro.

## Levantamento de hoje (2.183 livros após a curadoria do ciclo)
| Bloco (ordem de resolução) | Livros | Ouro | Prata | Bronze | Tipos mais comuns |
|---|---|---|---|---|---|
| 1 · Goiás | 388 | 14 | 51 | 323 | Edital 211 · Chamamento 83 · Fundo 43 · Credenciamento 15 · Destinação judicial 13 |
| 2 · Brasil (nacional) | 1.003 | 7 | 97 | 899 | Edital 482 · Credenciamento 215 · Fundo 120 · Chamamento 62 · Prêmio 40 |
| 3 · Internacional | 64 | 0 | 6 | 58 | Grant internacional 64 |
| 4 · Demais estados | 728 | 8 | 137 | 583 | Credenciamento 249 · Chamamento 239 · Edital 207 |
| **Total** | **2.183** | **29** | **291** | **1.863** | |

- **85% dos livros são bronze**: não há edição anterior a 2026 registrada — é o tamanho da coleta dos 3 anos.
- Ouro em Goiás: FAPEG (4 chamadas), Goiás Social (CEDCA, Conselho da Juventude, R$ 10 milhões, PPCAAM, chamamento de instituições), Goiás Turismo, Itaberaí (CMDCA 2025 e chamamento 002/2025), Pirenópolis (termo de fomento) e um chamamento 02/2024.
- Nas 660 oportunidades do painel: livro ouro 4 · prata 11 · bronze 438 · sem livro 207.

## Filas de coleta (prompts)
`dados/coleta_3_anos/fila_go.json` (374) · `fila_br.json` (996) · `fila_int.json` (64), por tipo e com bronze primeiro.
Os prompts `PROMPT-COLETA-3-ANOS-LIVROS-GO/BR/INT.md` gravam em `dados/coleta_3_anos/entrada/`; `python -m src.selo_livros`
incorpora as edições provadas e recalcula os selos (idempotente). Os demais estados ficam para depois de Goiás, Brasil e internacional.

## Conselho de 7 lentes
- **Extremamente pessimista:** 1.863 livros sem histórico — o preditivo hoje é quase todo de confiança baixa.
- **Pessimista:** a coleta de 3 anos é longa; feita sem prova oficial, encheria a base de falsos ouros.
- **Levemente pessimista:** dois selos lado a lado podem confundir; as legendas (ao passar o mouse) explicam cada um.
- **Neutro (decide):** implantar o selo e coletar na ordem Goiás → Brasil → internacional → demais estados, só com prova oficial. Parâmetros: ouro exige 2 anos + página oficial + data; meta de 100% dos livros de Goiás com selo definido por coleta (não por ausência) em 30 dias. Mitigação: idempotência na incorporação e trecho literal obrigatório.
- **Levemente otimista:** 29 livros já são previsíveis com confiança alta.
- **Otimista:** o ícone mostra, no próprio cartão, se vale preparar a entidade antes do edital.
- **Extremamente otimista:** com Goiás todo em ouro, a A.M.C. passa a montar documentos meses antes de cada abertura.
