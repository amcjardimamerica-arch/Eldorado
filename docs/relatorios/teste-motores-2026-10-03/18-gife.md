# Motor 18 — GIFE e Capta: editais selecionados (`gife`)

**Veredito:** workflow FUNCIONANDO · coleta FUNCIONANDO (API do WordPress do GIFE e da Capta) · resultado
FUNCIONANDO (3 editais reais) · histórico de 3 anos FALHA (o arquivo existe e não foi carregado).

## Workflow

- **Agenda (`plat-gife`):** todos os dias, às 11:23 e 17:53, na nuvem. O módulo é `src/gife_editais.py` (motor-22 v2,
  01/10), e o teste `tests/test_motor22_gife.py` passa.
- **Leituras:** 28; a última foi em 02/10, às 20:09. Luz **verde**, com 3 achados.

## Onde coleta

| Fonte | Endereço | Nuvem |
|---|---|---|
| A — seleção mensal de editais do GIFE | `gife.org.br/wp-json/wp/v2/posts` | HTTP 200: 6 consultas, 17 posts, 15 itens |
| B — Capta, para onde a seleção aponta | `capta.org.br/wp-json/wp/v2/posts` | HTTP 200: 2 consultas, 8 posts, 8 itens |

## Resultado

- **Classificação:** 21 itens, que deram 3 OPORTUNIDADE, 14 ACOMPANHAR e 4 RUÍDO. São 4 únicas em 8 registros.
- **Acertos:**
  - Fundo Baobá — Programa Marielle Franco (lideranças femininas negras), até **19/10/2026**;
  - Rede Memória Viva — Iniciativa Viva Pequena África, até **03/10/2026**, ou seja, hoje;
  - Edital Impactarte, de fluxo contínuo.
- **Ruído:** "Fundação FEAC", sem data e sem edital, só o nome da fundação.
- Nenhum é exclusivo de Goiás. São editais nacionais abertos a OSC de qualquer estado.

## Histórico de 3 anos

- **Próprio:** 3 registros, de 2026.
- **Recuperação possível:** a seleção de editais do GIFE é publicada todo mês desde antes de 2023, e a API do WordPress
  pagina por data (`after`/`before`). A carga de 36 seleções mensais (de out/2023 a set/2026) é viável e leve. Ela dá
  o calendário dos financiadores privados: quem abre, em que mês e com que valor.

## Correções, por prioridade

1. **Carga de 3 anos** das seleções mensais do GIFE pela API, gravando os editais encerrados com financiador, área e
   mês.
2. **Vetar registro sem edital** (nome de fundação sem chamada, como o caso FEAC).
3. **Alerta de prazo curto:** a Rede Memória Viva vence hoje. Edital com menos de 5 dias deve subir no painel.

## Conselho de 7 lentes

| Lente | Opinião |
|---|---|
| Extremamente pessimista | Edital que vence hoje aparece com o mesmo destaque de um que vence em meses. |
| Pessimista | O GIFE seleciona para o Brasil todo: pouca coisa é específica de Goiás. |
| Levemente pessimista | O nome de fundação sem edital entrou como registro. |
| **Neutro** | **Motor limpo, com fonte estruturada e acertos reais. Prioridade: carga de 3 anos (36 seleções) e destaque de prazo curto. Qualidade: 100% dos registros com prazo ou "fluxo contínuo" explícito.** |
| Levemente otimista | API estável, sem bloqueio, leve. |
| Otimista | A seleção do GIFE é curadoria profissional dos melhores editais privados. |
| Extremamente otimista | Com 3 anos de seleções, a associação monta a agenda anual dos financiadores privados. |
