# Motor 12 — Justiça Federal, Seção Judiciária de Goiás (`dj-trf1-go`)

**Veredito:** workflow FALHA (não é disparado) · coleta PARCIAL (lê a página institucional) · resultado FALHA
(0 achados em 40 leituras) · histórico de 3 anos FALHA.

## Workflow

- **Agenda:** de segunda a sexta, às 07:53, com **`coleta: local`**. O agendador pula motor local, então **o GitHub
  não dispara este motor**.
- **O rótulo está errado:** na última leitura (30/09), o site `trf1.jus.br/sjgo/` **respondeu da nuvem** (HTTP 200, 88
  KB). O motor não precisa do Brasil.
- **Módulo:** não tem módulo próprio; usa o leitor genérico de `src/sensores.py`. Também não tem teste próprio.
- **Leituras:** 40, com **0 achados**. O alerta "trocar URL" está ativo. A luz é cinza desde 30/09.

## Onde coleta

| Endereço | Nuvem |
|---|---|
| `trf1.jus.br/sjgo/` (home da seção) | HTTP 200 |
| Descobertas automáticas: "Editais e Portarias" (`/sjgo/processual/editais-e-portarias`), "Publicações de Interesse Público", "Diários da Justiça" | seguidas, mas nenhum rótulo casou com o léxico |

## Resultado

- 0 oportunidades e 0 registros.
- O objetivo da agenda já reconhece: destinações de pena federais em Goiás são **raras**.
- A rota certa seria a página de "Editais e Portarias" da SJGO e as notícias das varas criminais e dos juizados
  (prestação pecuniária). A home institucional não serve.

## Histórico de 3 anos

- **Nenhum registro.**
- **Recuperação possível:** a página de editais e portarias da SJGO e o Diário da Justiça do TRF1 têm arquivo por data.
  Uma busca dirigida por "prestação pecuniária" e "entidades" de 2023 a 2026 diria se essa fonte vale o esforço.

## Correções, por prioridade

1. **Trocar `coleta: local` por `nuvem`** em `config/agenda_motores.json`, porque o site responde da nuvem. Assim o motor
   volta a ser disparado.
2. **Apontar para a listagem certa:** "Editais e Portarias" da SJGO, com léxico de prestação pecuniária, entidades e
   destinação.
3. **Sondagem de 3 anos** por "prestação pecuniária" na SJGO. Sem nenhum caso, rebaixar o motor para cadência mensal.

## Conselho de 7 lentes

| Lente | Opinião |
|---|---|
| Extremamente pessimista | 40 dias de zero, parado desde 30/09 por um rótulo errado, e ninguém percebeu. |
| Pessimista | Mesmo corrigido, o TRF1 quase não destina a entidades em Goiás. |
| Levemente pessimista | Leitor genérico em página institucional: alto custo, nenhum retorno. |
| **Neutro** | **Corrigir o rótulo (é nuvem, não local) e a listagem. Decidir pela sondagem dos 3 anos: sem casos, cadência mensal. Qualidade: o motor deixa de ser cinza e passa a ter motivo de zero explícito.** |
| Levemente otimista | O site responde bem da nuvem: corrigir é barato. |
| Otimista | A Justiça Federal destina em outros estados (TRF, R$ 1,6 milhão). Goiás pode ter casos pontuais. |
| Extremamente otimista | Um único edital federal de prestação pecuniária pode financiar um projeto inteiro da associação. |
