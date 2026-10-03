# Motor 09 — MPT-GO: editais de 5 dias para destinação (`mptgo-destinacao`)

**Veredito:** workflow PARCIAL (motor criado em 02/10 às 19:27; ainda não rodou) · coleta FUNCIONANDO (a tabela do
PRT-18 é lida na nuvem) · resultado FUNCIONANDO (1 edital aberto, real) · histórico de 3 anos PARCIAL (2026 forte,
2024 e 2025 fracos).

## Workflow

- **Agenda:** todos os dias, às 07:53 e 16:23, na nuvem. O módulo é `src/ministerios_publicos.py`
  (`ler_parte("mptgo-destinacao")`), e o teste do motor 12 passa.
- **Leituras:** nunca rodou com o id novo. A primeira passada prevista é às 07:53 de 03/10.
- **Antecessor `plat-mp-destinacoes-reparacao`:** 20 leituras e 42 achados. A última rodada, às 19:10 de 02/10, leu a
  tabela e **depois quebrou o passo dos sensores** (`KeyError: 'lido_em'`, ver consolidado).

## Onde coleta

| Fonte | Endereço | Nuvem |
|---|---|---|
| Tabela de editais de destinação (PRT 18ª, Goiânia e PTM Anápolis) | `prt18.mpt.mp.br/servicos/editais-de-destinacao-de-recursos-bens` | HTTP 200, **43 itens** |
| Entidades habilitadas | `prt18.mpt.mp.br/servicos/entidades-assistenciais` | HTTP 200, 57 entidades. **A A.M.C. não consta** |

O motor faz o que o navegador faz: abre a página, pega o token público e pede a tabela (que vem por JavaScript). O PDF
do edital é baixado na mesma sessão.

## Resultado

- **Aberto agora:** *Edital 009220.2026 — indicação de destinação de recursos ou bens — PTM Anápolis*, publicado em
  01/10, com prazo de 5 dias e **data segura 05/10/2026**. Exige cadastro prévio no Sistema de Destinações do MPT.
- **Fluxo contínuo:** cadastramento no Sistema de Destinações (Edital PRT18 24/2025), porta de entrada para todos os
  editais de 5 dias.
- **Acompanhar:** 63 itens (editais encerrados e informes).
- **Ruído antigo na base:** os títulos de página "Editais de Destinação de Recursos ou Bens" e "Entidades
  Assistenciais", gravados como registros pela versão anterior.

## Histórico de 3 anos

- O inventário do estudo traz, para o MPT-GO, **45 registros de 2026, 9 de 2025 e 2 de 2024**, mais 2 sem data.
- O ritmo de 2026 é de 4 a 5 editais por mês: 43 em 9,5 meses.
- **Lacuna:** 2024 e 2025 estão sub-representados. A tabela do PRT-18 mostra principalmente o ano corrente. O passado
  vem pelos PDFs e pela prestação de contas das destinações (`servicos/prestacao-de-contas-de-destinacoes`), que dá
  valor e entidade beneficiada.

## Correções, por prioridade

1. **Ação do titular:** cadastrar a A.M.C. no Sistema de Destinações do MPT (Edital PRT18 24/2025). Sem isso, o edital
   de Anápolis (até 05/10) e os próximos não podem ser respondidos.
2. **Corrigir a quebra dos sensores** e confirmar as duas leituras diárias com o id novo. Edital de 5 dias não admite
   dia sem leitura.
3. **Completar 2024 e 2025** pela página de prestação de contas das destinações. Limpar os 2 títulos de página da base.

## Conselho de 7 lentes

| Lente | Opinião |
|---|---|
| Extremamente pessimista | Edital de 5 dias com o motor parado por uma quebra: em 48 horas a oportunidade some. |
| Pessimista | A A.M.C. não está habilitada. O motor acha, mas a associação não pode responder. |
| Levemente pessimista | O histórico de 2024 e 2025 é fraco para prever. |
| **Neutro** | **O melhor motor de destinação do conjunto: lê a fonte primária na nuvem, com data segura do prazo. Prioridade: o cadastro da A.M.C. (ação do titular) e a correção da quebra. Meta: todo edital do PRT-18 no painel no mesmo dia, com alerta.** |
| Levemente otimista | 4 a 5 editais por mês em Goiás é fluxo constante. |
| Otimista | O PTM Anápolis e a PRT Goiânia cobrem a região da associação. |
| Extremamente otimista | Com o cadastro e 2 ou 3 projetos-modelo de tema trabalhista prontos, a A.M.C. responde a todo edital em 5 dias. |
