# Motor 20 — Incentivos Fiscais: empresas da base ICMS, RFB e SALIC de Goiás (`motor-gife`)

**Veredito:** workflow FUNCIONANDO (semanal, aos domingos) · coleta FUNCIONANDO (lista oficial do ICMS) · resultado
FUNCIONANDO para o que se propõe: 60 empresas mapeadas, que são alvos de captação e não editais · histórico de 3 anos
PARCIAL (2024 e 2025 completos, 2023 ausente, 2026 com erro de leitura).

## Workflow

- **Agenda:** aos domingos, às 03:23, a cada 7 dias, na nuvem.
- **Disparo:** quando o agendador manda `motor-gife`, o passo "Motor de empresas" do `monitoramento-diario` roda:
  - `src.empresas semanal GO`;
  - `src.patrocinios`;
  - `src.biblioteca_empresas` e `src.incentivos_empresas`;
  - os sites das maiores contribuintes do ICMS.
- **Testes:** `tests/test_prospeccao.py` e mais 9 arquivos.
- **Última leitura:** 29/09, às 00:17. A luz é cinza "fora da agenda", o que é correto. A próxima é no domingo, 04/10.

## Onde coleta

| Fonte | Endereço | Situação |
|---|---|---|
| Maiores contribuintes do ICMS (Secretaria da Economia de Goiás) | `goias.gov.br/economia/os-maiores-contribuintes-do-icms/` | HTTP 200; 25 anexos na página, mas **só 2 lidos por execução** |
| Cadastro da Receita Federal e SALIC | base `dados/empresas/` | cruzamento |

## Resultado

- **60 empresas mapeadas**, com pontuação de potencial de destinação incentivada (Rouanet, LIE, FIA/Idoso,
  PRONON/PRONAS). As primeiras são Renner (60), Brasal Refrigerantes, Votoran, BRF, Telefônica, Refrescos Bandeirantes,
  Assaí e Hyundai (55).
- São **alvos de captação**, não editais. O painel mostra corretamente "empresas mapeadas".
- As rotas dessas empresas alimentam o motor 19, que hoje não as lê bem (ver o relatório 19).

## Histórico de 3 anos

| Ano | Lista do ICMS |
|---|---|
| 2024 | 300 empresas (completa) |
| 2025 | 300 empresas (completa) |
| 2026 | **erro**: 1 "empresa" chamada "de janeiro de 2026". O leitor pegou a data da página como nome |
| 2023 | **ausente**, embora a página tenha 25 anexos |

## Correções, por prioridade

1. **Corrigir a leitura de 2026:** descartar entrada sem CNPJ e com nome de data. Se a lista oficial de 2026 ainda não
   existe, registrar "não publicada".
2. **Ler os 25 anexos** e completar 2023 (e anos anteriores, se houver). Hoje são lidos só 2 por execução.
3. **Série de 3 anos por empresa** (posição no ranking do ICMS e projetos incentivados no SALIC): quem sobe no ranking
   e quem já destina vira prioridade de contato.

## Conselho de 7 lentes

| Lente | Opinião |
|---|---|
| Extremamente pessimista | Uma "empresa" chamada "de janeiro de 2026" no ranking mostra que nada confere o que o leitor grava. |
| Pessimista | Empresa mapeada não é dinheiro: sem rota de edital (motor 19), a lista fica parada. |
| Levemente pessimista | A cadência semanal faz sentido, mas 2 anexos por vez atrasa o histórico. |
| **Neutro** | **O motor cumpre o papel (60 alvos com pontuação, lista oficial de 2024 e 2025). Prioridade: limpar 2026, ler 2023 e ligar as empresas ao motor 19. Qualidade: zero entrada sem CNPJ no ranking.** |
| Levemente otimista | A fonte é oficial e estável: o ranking do ICMS do próprio Estado. |
| Otimista | As grandes contribuintes do ICMS são as que mais podem destinar por renúncia fiscal. |
| Extremamente otimista | Com 3 anos de ranking cruzados com o SALIC, a associação tem uma carteira de patrocinadores priorizada e justificada. |
