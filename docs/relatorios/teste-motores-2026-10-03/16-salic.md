# Motor 16 — SALIC / Lei Rouanet, Ministério da Cultura (`salic`)

**Veredito:** workflow FUNCIONANDO · coleta PARCIAL (lê páginas do Ministério, não o SALIC) · resultado FALHA (os 3
registros únicos são páginas institucionais) · histórico de 3 anos FALHA.

## Workflow

- **Agenda (`plat-salic`):** todos os dias, às 08:53, 13:53 e 19:53, na nuvem.
- **Módulo:** **não tem módulo próprio**; usa o leitor genérico de `src/sensores.py`. Também não tem teste próprio.
- **Leituras:** 21; a última foi em 02/10, às 17:55. Luz **verde**.
- **Contagem inflada:** "105 achados" são **14 registros que dão só 3 únicos**. A mesma página é contada a cada
  leitura.

## Onde coleta

| Endereço | Nuvem |
|---|---|
| `gov.br/cultura/pt-br/assuntos/editais` | HTTP 200, 125 KB |
| `gov.br/cultura/.../lei-rouanet` | HTTP 200, 54 KB |
| Descobertas: Licitações e Contratos, Contratos, Licitações, Atas de Registro de Preços | seguidas; é ruído para OSC |

O SALIC em si (sistema de propostas e projetos da Rouanet, com dados abertos) **não é lido**.

## Resultado

- **Os 3 registros na base são páginas institucionais, sem data:**
  - "Secretaria de Fomento e Incentivo à Cultura";
  - "Política Nacional Aldir Blanc" (FAQ);
  - "Política Nacional Aldir Blanc" (página do programa).
- Nenhum é edital nem janela de proposta.
- **Prazo de atenção:** o objetivo registra a janela anual de propostas da Rouanet no SALIC como 1º/02 a 31/10
  ("confirmar IN vigente"). Se valer em 2026, **ela fecha em 28 dias**, e o motor não avisa.

## Histórico de 3 anos

- **Nenhum registro datado.**
- **Recuperação possível:** os dados abertos do SALIC (projetos aprovados por ano, proponente, UF, valor captado) dariam
  os projetos de Goiás de 2023 a 2026 e as empresas que mais incentivam. Também alimentariam o motor 20.

## Correções, por prioridade

1. **Confirmar hoje a janela de propostas da Rouanet 2026** na Instrução Normativa vigente e pôr o prazo no painel.
2. **Leitor próprio do SALIC** (dados abertos de projetos e propostas). Trocar as páginas institucionais pela fonte de
   dados. Vetar "licitações", "contratos" e páginas de FAQ.
3. **Contar achados únicos**, não leituras repetidas da mesma página.

## Conselho de 7 lentes

| Lente | Opinião |
|---|---|
| Extremamente pessimista | A janela da Rouanet pode fechar em 31/10 sem que o painel avise. O motor só guarda páginas de menu. |
| Pessimista | "105 achados" é um número enganoso: são 3 páginas repetidas. |
| Levemente pessimista | Leitor genérico, sem teste próprio. |
| **Neutro** | **O motor roda, mas não lê a fonte que importa. Prioridade: confirmar o prazo da janela de 2026 e criar o leitor de dados abertos do SALIC. Meta: o painel mostra a janela da Rouanet com data oficial e os projetos de Goiás por ano.** |
| Levemente otimista | O site do Ministério responde bem da nuvem. |
| Otimista | Os dados do SALIC mostram as empresas que incentivam cultura em Goiás, e isso é ouro para a captação. |
| Extremamente otimista | Com 3 anos de SALIC, a associação monta proposta e carteira de patrocinadores antes da janela de 2027. |
