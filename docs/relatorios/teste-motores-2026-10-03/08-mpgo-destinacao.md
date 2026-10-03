# Motor 08 — MP-GO: Programa Destina (`mpgo-destinacao`)

**Veredito:** workflow FUNCIONANDO por regra (verificação manual mensal) · coleta FUNCIONANDO por regra: o site
**proíbe robôs**, e o motor nunca o acessa, como deve ser · resultado FUNCIONANDO (o cadastro Destina está
registrado) · histórico de 3 anos PARCIAL (2 registros do MP-GO no inventário).

## Workflow

- **Agenda:** às 07:53, a cada 30 dias, com **`coleta: manual`**. O agendador não dispara motor manual, o que é
  correto. O módulo é `src/ministerios_publicos.py` (`ler_parte("mpgo-destinacao")`), e o teste
  `tests/test_motor_12_ministerios_publicos.py` passa.
- **Leituras:** **nunca rodou** com este id; a separação do MP em três motores entrou às 19:27 de 02/10. A luz está
  cinza, e cinza é o esperado para um motor manual.
- **Antecessor `plat-mp-destinacoes-reparacao`:** 20 leituras e 42 achados. A última rodada, às 19:10 de 02/10,
  **quebrou o passo dos sensores** (ver consolidado).

## Onde coleta

| Fonte | Endereço | Situação |
|---|---|---|
| f00 — Edital Destina nº 02/2024 (COMPOR) | `mpgo.mp.br/portal/conteudo/destina-destinacao-articulada-de-acordos-edital-n-02-2024` | **Nunca acessado**: o `robots.txt` do MP-GO tem `Disallow: /` e a nuvem nem conecta. Regra fixa e conferência manual mensal |
| f01 — `robots.txt` | `mpgo.mp.br/robots.txt` | Regra |

## Resultado

- **Registro fixo (OPORTUNIDADE de fluxo contínuo):** *DESTINA — cadastro de entidades para receber bens e valores de
  acordos*, Edital nº 02/2024, vigente até o próximo ato convocatório (Atos PGJ 77/2022, 25/2024 e 58/2025).
- **Pendência do presidente:** pedir o cadastro da A.M.C. no Destina, pelo COMPOR, telefone (62) 3243-8116.
- Não há outro edital do MP-GO a ler: as destinações são caso a caso, sem calendário.

## Histórico de 3 anos

- O inventário do estudo de 02/10 (`biblioteca_alexandria/base/ministerios_publicos/estudo/historico_3_anos_motor_12.csv`)
  traz **2 registros do MP-GO**: o Destina (OPORTUNIDADE) e 1 para acompanhar. Os dois estão sem data de publicação.
- **Lacuna:** as destinações do MP-GO de 2023 a 2025 não são publicadas em lista. Sem acesso por robô, o histórico só
  pode vir de pedido ao COMPOR, pela Lei de Acesso à Informação.

## Correções, por prioridade

1. **Ação do titular:** cadastrar a A.M.C. no Destina. Sem cadastro, a entidade não recebe destinação.
2. Pedido pela Lei de Acesso à Informação ao COMPOR com as destinações de 2023 a 2025 (valor, entidade, área), para
   formar o histórico.
3. Manter o lembrete mensal da verificação manual no painel, com a data da última conferência.

## Conselho de 7 lentes

| Lente | Opinião |
|---|---|
| Extremamente pessimista | O motor nunca vai "achar" nada: o site proíbe robôs. Se o titular não conferir todo mês, o motor é decorativo. |
| Pessimista | O histórico tem 2 linhas sem data. Não serve para previsão. |
| Levemente pessimista | O antecessor quebrou o passo dos sensores na última rodada. |
| **Neutro** | **Motor correto ao respeitar o robots.txt e tratar o Destina como cadastro contínuo. O ganho real depende de um ato do titular (o cadastro) e de um pedido pela Lei de Acesso. Qualidade: conferência manual mensal registrada com data.** |
| Levemente otimista | O registro fixo já está no painel como oportunidade de fluxo contínuo. |
| Otimista | Uma vez cadastrada, a A.M.C. recebe destinação sem concorrer a edital. |
| Extremamente otimista | Com o histórico obtido pela Lei de Acesso, o sistema sabe que áreas e valores o MP-GO costuma destinar. |
