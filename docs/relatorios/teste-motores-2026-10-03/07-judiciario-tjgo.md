# Motor 07 — TJ-GO: editais das comarcas e Banco de Projetos Sociais (`judiciario-tjgo`)

**Veredito:** workflow PARCIAL (motor criado em 02/10 às 19:27; ainda não rodou) · coleta PARCIAL (o TJGO só abre no
Brasil) · resultado FUNCIONANDO no antecessor (1 edital real) · histórico de 3 anos FALHA.

## Workflow

- **Agenda:** todos os dias, às 07:53 e 16:23, na nuvem e no computador do titular. O disparo é `agenda-motores` →
  `monitoramento-diario` → `src.sensores` → `src/judiciario_go.py` (`ler_parte("judiciario-tjgo")`).
- **Testes:** `tests/test_motor_judiciario_go.py` passa.
- **Leituras:** **nunca rodou** com este id; a separação TJ-GO/CNJ entrou às 19:27 de 02/10. A primeira passada prevista
  é às 07:53 de 03/10.
- **Antecessores:**
  - `judiciario-cnj-tjgo`: 2 leituras manuais em 02/10, 2 achados. Hoje está inativo.
  - `dje-tjgo`: 40 leituras, **0 achados**, lendo o Jusbrasil, que é a fonte errada. Também inativo, o que está
    correto.

## Onde coleta

| Fonte | Endereço | Rota |
|---|---|---|
| A — Agência de Notícias do TJGO (RSS) | `tjgo.jus.br/index.php/agencia-de-noticias/noticias-ccs?format=feed&type=rss` | só local (o TJGO recusa IP estrangeiro) |
| B — PDF do edital da comarca | `tjgo.jus.br/images/docs/CCS/…` | só local |
| C — Banco de Projetos Sociais da CGJ | `corregedoria.tjgo.jus.br/basesocial` | só local |
| D — PNCP cruzado (TJGO e CNJ) | via motor 15 | nuvem |

Na nuvem, as fontes A e B foram puladas ("na nuvem o TJGO recusa IP estrangeiro"). A conferência no navegador do
titular ficou pendente, porque o Chrome não respondeu.

## Resultado (antecessor `judiciario-cnj-tjgo`)

- **Acerto:** *Itaberaí — Edital seleciona projetos de Itaberaí (GO) para receberem recursos de prestação pecuniária*
  (30/09, PDF do TJGO).
  - É o tipo exato de oportunidade do motor.
  - **Atenção:** vale só para entidades da comarca de Itaberaí.
  - O prazo gravado, 18/08/2027, precisa ser conferido no PDF; pode ser a vigência, e não a inscrição.
- **Cruzado do PNCP:** TJGO — credenciamento de entidades sem fins lucrativos para coleta de recicláveis, até 2031
  (vigência longa).
- **Acompanhar:** 4 itens. Os registros do CNJ na base (prêmios PopRuaJud, gestão de pessoas) são ruído de outra fonte.

## Histórico de 3 anos

- **Próprio:** 1 registro, de 2026.
- **Configuração:** a carga inicial está em **150 dias**, e não em 3 anos.
- **Recuperação possível:** a Agência de Notícias do TJGO tem arquivo paginado de anos. A carga de 3 anos dos editais
  de prestação pecuniária de todas as comarcas (Goiânia primeiro) é viável **no computador do titular**.

## Correções, por prioridade

1. **Rodar a rota local** (computador do titular ou VM Oracle). Sem ela, o motor só vê o que o PNCP repete.
2. **Ampliar a carga inicial** de 150 dias para 3 anos (cerca de 1.100 dias), fracionada por execução, gravando os
   editais passados de cada comarca. Isso dá o mês típico de abertura de cada uma.
3. **Prazo:** distinguir inscrição de vigência no PDF do edital (caso Itaberaí).

## Conselho de 7 lentes

| Lente | Opinião |
|---|---|
| Extremamente pessimista | O motor nunca rodou com o nome novo. Na nuvem, ele é cego para o TJGO. |
| Pessimista | Itaberaí não serve para uma entidade de Goiânia. O motor precisa priorizar a comarca de Goiânia. |
| Levemente pessimista | Um prazo de 2027 num edital de comarca é suspeito: pode ser vigência. |
| **Neutro** | **O desenho está certo (notícia → PDF → Banco de Projetos) e já acertou um edital real. A execução depende do Brasil. Prioridade: rota local e carga de 3 anos. Meta: todo edital de comarca de Goiás no painel em até 24 horas da notícia.** |
| Levemente otimista | O cruzamento com o PNCP pega o que o TJGO publica como contratação. |
| Otimista | Prestação pecuniária é recurso recorrente, sem disputa nacional: excelente para a associação. |
| Extremamente otimista | Com 3 anos de editais, o sistema sabe quando a comarca de Goiânia costuma abrir e prepara o cadastro no Banco de Projetos antes. |
