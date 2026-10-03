# Motor 17 — CNPq / MCTI / Setec-MEC: chamadas com extensão e parceria com OSC (`cnpq-extensao`)

**Veredito:** workflow FALHA em 02/10 (adiado por tempo) · coleta PARCIAL (lê a home do MCTI, e 2 páginas falham) ·
resultado FALHA (0 achados em 19 leituras) · histórico de 3 anos FALHA.

## Workflow

- **Agenda (`plat-cnpq-extensao`):** todos os dias, às 09:23 e 15:23, na nuvem.
- **Módulo:** não tem módulo próprio; usa o leitor genérico. Também não tem teste próprio.
- **Última leitura:** 01/10, às 12:04. Em 02/10, o motor entrou na rodada manual das 14:49, mas foi **adiado por
  tempo**.
  - Os diários (motores 01 a 03), o PNCP e o Congresso consumiram os 1.452 segundos do passo.
  - Junto com ele ficaram para depois **49 motores**.
- A luz está **vermelha**, com "2 páginas com falha".

## Onde coleta

| Endereço | Nuvem |
|---|---|
| `gov.br/cnpq/.../programas/chamadas-publicas` (página do painel) | não aparece entre as que responderam: deve ser uma das 2 com falha |
| `gov.br/mcti/pt-br` (home) | HTTP 200, 207 KB |
| `gov.br/mcti/.../chamamento-oceano` | HTTP 200: chamamento de pesquisa oceânica, que não é para OSC |

- O motor segue links da home do MCTI ("Chamamento Vacinas", "Mudança do clima", "Licitações") e veta ou ignora tudo.
- **A fonte certa não está configurada:** a lista de chamadas abertas do CNPq (`chamadas.cnpq.br` e a página de chamadas
  públicas) e as chamadas de extensão da Setec-MEC.

## Resultado

- 0 oportunidades em 19 leituras.

## Histórico de 3 anos

- **Nenhum registro.**
- **Recuperação possível:** o CNPq mantém a lista de chamadas encerradas por ano. Filtrar as que têm "extensão" e
  "organizações da sociedade civil" de 2023 a 2026 diria se o motor tem razão de existir.

## Correções, por prioridade

1. **Corrigir o tempo do passo dos sensores** (ver consolidado). Os diários consomem a rodada, e o resto é adiado. Em
   02/10, foram 12 execuções de sensor para mais de 100 motores agendados.
2. **Trocar a fonte:** sair da home do MCTI e ir para a lista de chamadas abertas do CNPq, com filtro de extensão e
   parceria com OSC.
3. **Sondagem de 3 anos** nas chamadas encerradas. Sem nenhuma que admita OSC, rebaixar o motor para cadência
   semanal.

## Conselho de 7 lentes

| Lente | Opinião |
|---|---|
| Extremamente pessimista | Motor que não roda, lê a página errada e nunca achou nada: puro custo. |
| Pessimista | Chamadas do CNPq raramente admitem OSC como proponente; em geral é a universidade que propõe. |
| Levemente pessimista | Sem teste próprio, nenhuma mudança é protegida. |
| **Neutro** | **Defeito duplo: execução (adiado por tempo) e fonte errada. Prioridade: o tempo do passo e a fonte certa do CNPq. Decidir pela sondagem dos 3 anos. Qualidade: motivo de zero explícito em cada leitura.** |
| Levemente otimista | As páginas do gov.br respondem da nuvem. |
| Otimista | Chamadas de extensão com parceria de OSC trazem recurso e universidade como parceira técnica. |
| Extremamente otimista | Uma parceria com instituto federal em Goiás abre uma linha recorrente de projetos de extensão no bairro. |
