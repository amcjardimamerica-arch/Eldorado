# Motor 02 — Diário Oficial do Estado de Goiás (`do-goias`)

**Veredito:** workflow FUNCIONANDO · coleta FUNCIONANDO (a rota B é intermitente) · resultado PARCIAL (precisão) ·
histórico de 3 anos FALHA.

## Workflow

- **Agenda:** de segunda a sexta, às 06:23, 12:53 e 20:23. O disparo é `agenda-motores` → `monitoramento-diario`
  (fontes=do-goias) → `src.sensores` → `src/diario_goias.py` (motor-02 v2, 01/10).
- **Testes:** 7 arquivos, entre eles `tests/test_motor02_diario_goias.py`.
- **Leituras:** 45; a última foi em 02/10, às 14:33. Luz **verde**, com 5 achados.
- **Calendário:** 01 e 02/10 aparecem como "parcial".

## Onde coleta

| Rota | Endereço | 01/10 | 02/10 |
|---|---|---|---|
| A — busca de texto completo | `diariooficial.abc.go.gov.br/busca/busca/buscar/query/0/` | leu | leu: 26 consultas, 88 páginas, 153 matérias |
| B — edição do dia (sumário) | `…/apifront/portal/edicoes/edicoes_from_data/` | leu | **sem leitura**: 0 edições |
| C — site da Secult (WordPress) | `goias.gov.br/cultura/wp-json/wp/v2/posts` | leu | leu: 20 consultas, 12 matérias |

- Foram processadas 7 edições (nº 7384 a 7390), e não houve dia útil sem diário.
- A página inicial do diário respondeu HTTP 200 da nuvem.
- O teste no navegador do titular ficou pendente, porque o Chrome não respondeu.

## Resultado

- **Matérias de 02/10:** 165, classificadas em 5 OPORTUNIDADE, 32 ACOMPANHAR e 128 RUÍDO. Há 17 oportunidades únicas
  em 26 registros, e 16 estão na base, todas de Goiás.
- **Acertos prováveis:**
  - Secult — edital para levar a produção goiana ao Rio de Janeiro (29/09);
  - SECTI-GO — Edital nº 002/2026;
  - Prefeitura de Cachoeira Alta — Edital nº 001/2026;
  - Prefeitura de Goiatuba — Edital nº 004/2026;
  - Prefeitura de Nova Iguaçu de Goiás — Edital nº 001/2026, com prazo até 02/10, já vencido.
- **Falsos positivos ou registros velhos** (10 dos 16 na base não têm data de publicação; vêm de versões anteriores à
  v2):
  - "ANEXO IX – Minuta do Termo de Colaboração";
  - "Extrato do Termo de Colaboração 01/2026": um extrato é parceria já celebrada, não oportunidade aberta;
  - "Chamamentos Públicos" e "Chamamentos Públicos 2026": títulos de página;
  - "Aviso de Chamamento Público Nº 02/2006";
  - avisos com prazo de 05/02/2026, já encerrados;
  - a aquisição de gêneros alimentícios da agricultura familiar (02/10): é compra pública (PNAE), não fomento a OSC.

## Histórico de 3 anos

- **Próprio:** 6 registros datados, todos de 2026. **Não há carga de 2023 a 2025.**
- **Correlato:** nenhum outro motor gravou registro deste diário.
- **Recuperação possível:** a rota A é busca de texto completo em todo o acervo do diário, e a rota B lista edições por
  data. A carga de 3 anos é viável, com termos como "chamamento público", "termo de fomento" e "Lei 13.019",
  ano a ano.

## Correções, por prioridade

1. **Carga histórica de 3 anos** pela rota A, ano a ano, com o mesmo classificador. Gravar as oportunidades como
   encerradas, com órgão, objeto e mês.
2. **Limpar os 10 registros sem data** das versões antigas e **vetar** "extrato", "minuta/anexo", título de página e
   compra da agricultura familiar (PNAE) como OPORTUNIDADE.
3. **Rota B:** investigar o "sem leitura" de 02/10. A rota leu em 01/10; registrar se a edição do dia ainda não tinha
   saído na hora da leitura.

## Conselho de 7 lentes

| Lente | Opinião |
|---|---|
| Extremamente pessimista | Mais da metade do que está na base deste motor é ruído ou passado. O titular perde tempo e confia menos no painel. |
| Pessimista | A rota B falhou justamente no dia mais recente. |
| Levemente pessimista | O classificador ainda aceita anexo e extrato como oportunidade. |
| **Neutro** | **Coleta sólida, com três rotas e sem dia útil perdido. A qualidade do que vira oportunidade precisa de vetos. Prioridade: limpeza + vetos + carga dos 3 anos pela busca de texto completo. Meta: 80% de acerto no que é marcado OPORTUNIDADE.** |
| Levemente otimista | 128 ruídos descartados por dia mostram o filtro funcionando. |
| Otimista | A busca de texto completo do diário permite reconstruir os 3 anos sem depender de terceiros. |
| Extremamente otimista | Com o histórico, a Secult e a SEDS ganham calendário previsto de editais. |
