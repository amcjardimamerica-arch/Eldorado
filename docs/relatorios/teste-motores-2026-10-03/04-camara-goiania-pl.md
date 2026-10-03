# Motor 04 — Câmara Municipal de Goiânia (`camara-goiania-pl`)

**Veredito:** workflow FALHA (o motor não é disparado) · coleta FALHA desde 30/09 · resultado FALHA (0 achados em 40
leituras) · histórico de 3 anos FALHA.

## Workflow

- **Agenda:** todos os dias, às 20:23, com **`coleta: local`**.
  - `scripts/agenda_motores.py` **pula** os motores de coleta local, por regra.
  - Por isso, o `agenda-motores` → `monitoramento-diario` **nunca dispara este motor na nuvem**. Ele depende só do
    computador do titular (`scripts/coleta_brasil.py`).
- **Módulo:** `src/camara_goiania.py` (v2, 01/10), que lê o SUAP, os processos da própria associação e o RSS do
  portal. O teste `tests/test_motor05_camara_goiania.py` passa.
- **Última leitura:** 30/09, às 09:34, ainda com o leitor **antigo** (genérico): leu a home e teve 3 falhas. A v2
  nunca rodou. A luz está **cinza** em 01 e 02/10.
- **Alerta ausente:** foram 40 leituras vazias seguidas e o painel não deu alerta. A regra só alerta quando não há
  falha, e aqui houve falhas.

## Onde coleta

| Rota | Endereço | Situação |
|---|---|---|
| A — SUAP, consulta pública de processos | `suap.camaragyn.go.gov.br/camara/consulta_publica/` | Recusa IP estrangeiro; só local |
| B — processos da própria A.M.C. | SUAP | Só local |
| C — notícias do portal (RSS) | `goiania.go.leg.br/search_rss` | Recusa IP estrangeiro; só local |

Teste ao vivo: na nuvem, só a home de `goiania.go.leg.br` respondeu (HTTP 200, 15 KB). A conferência no navegador do
titular ficou pendente, porque o Chrome não respondeu.

## Resultado

- 0 oportunidades e 0 registros na base.
- **O que se perde:**
  - o acompanhamento do **Projeto de Lei nº 288/2026**, que declara de utilidade pública a própria A.M.C. Jardim
    América e é citado no módulo;
  - as leis municipais de fomento e isenção para entidades;
  - as emendas impositivas dos vereadores.

## Histórico de 3 anos

- **Próprio e correlato:** nenhum registro.
- **Recuperação possível:** o SUAP lista os processos do mais novo ao mais antigo, por assunto. A carga de 3 anos
  (utilidade pública, subvenção, fundo, emenda) é viável **no computador do titular**.

## Correções, por prioridade

1. **Pôr o motor para rodar no Brasil:** no computador do titular (agendador da coleta local) ou na VM Oracle. Sem
   isso, ele está parado.
2. **Alerta de motor parado:** alertar quando a última leitura passar de 48 horas, com ou sem falha. Hoje, 40 leituras
   vazias passaram sem aviso.
3. **Carga de 3 anos** no SUAP, pelos assuntos da Fonte A, com o PL 288/2026 em acompanhamento fixo.

## Conselho de 7 lentes

| Lente | Opinião |
|---|---|
| Extremamente pessimista | O motor está parado e o painel não avisou. A tramitação da utilidade pública da própria associação pode passar sem ninguém ver. |
| Pessimista | Depende 100% de uma máquina no Brasil, que não está rodando. |
| Levemente pessimista | Mesmo rodando, a Câmara quase não publica edital: o ganho é habilitação e acompanhamento, não captação direta. |
| **Neutro** | **O código v2 está pronto e testado. O defeito é de execução. Prioridade: ligar a coleta local ou a VM e criar o alerta de motor parado há mais de 48 horas. Qualidade: o PL 288/2026 aparece no painel com a última movimentação.** |
| Levemente otimista | O SUAP traz número, assunto, autor e documentos com data: dado estruturado e confiável. |
| Otimista | Emendas impositivas municipais para entidades são recurso direto e recorrente. |
| Extremamente otimista | Com 3 anos de utilidade pública aprovada, o sistema mapeia todas as entidades do bairro e os vereadores que apoiam. |
