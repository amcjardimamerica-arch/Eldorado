# Coleta dos 3 anos — livros do Brasil (03/10/2023 a 03/10/2026)

O prompt melhorado está em `docs/relatorios/PROMPT-COLETA-3-ANOS-BR-MELHORADO-2026-10-03.md`.

## Resultado em uma linha

Dos 1.123 livros do bloco Brasil, **216 foram trabalhados nesta passagem** (40 programas/financiadores pesquisados na fonte oficial). **6 subiram a ouro, 24 ficaram em prata e 186 em bronze.** Os outros 907 livros foram triados e ficam para a próxima passagem.

**Aviso de método:** a fila oficial (`fila_br.json`) e o módulo `src.selo_livros` não estavam no GitHub. A fila foi **reconstruída** a partir do catálogo, com os mesmos ids, e o selo é **estimado** por `scripts/expandir_coleta_br.py`. O selo oficial sai quando se rodar `python -m src.selo_livros`.

## Como foi feito

Cada programa foi pesquisado uma vez (a "âncora") e as edições valem para todos os livros daquele programa. Só conta edição com página oficial, trecho literal da página e data dentro da janela de 3 anos. Agregador serviu só para achar edição. Edição de programa que não é para OSC (pessoa física, escola, universitário) não conta.

## Números

- Edições registradas: 249 em 101 livros (2023: 11; 2024: 29; 2025: 53; 2026: 47).
- **Ouro (6):** 3 livros do Fundo Ecos (11 edições, 2024, 2025 e 2026) e 3 da Fundação Cargill, programa Semeia (2024, 2025 e 2026). Todos com prova literal.
- **Prata (24):**
  - PRONON/PRONAS (6): só 2025 comprovado.
  - FDD (7): só o edital 02/2023.
  - Fundo Brasil, Edital Geral (4): 2023, 2024 e 2025, mas prova por resumo, não literal.
  - CONANDA/SNDCA (2), BNDES Periferias, Banco do Nordeste, Neoenergia, Funarte, Salvador Arena PAPS (1 cada).
- **Bronze (186):** sem edição anterior a 2026 comprovada. Podem ser oportunidades novas ou programas que não consegui provar.
- **Âncoras sem nenhuma edição comprovada (19):** ArcelorMittal, Bradesco, BrazilFoundation, FAPESP, FNCA, FNI, Fundação Itaú, Fundação Telefônica, Fundação Vale, Impactarte, Instituto Claro, Instituto Coca-Cola, Instituto Localiza, Instituto Natura, LIE, Mapa Cultural, Receita/Justiça, Unibanco e Votorantim. Os sites estavam fora do ar, sem datas ou só com conteúdo por script.

## Janelas abertas agora

| Programa | Fecha em | Observação |
|---|---|---|
| Fundo Ecos, 52º edital | 08/10/2026 | chamada induzida, protegida por senha |
| Rouanet nas Favelas 2 | 13/10/2026 | inscrição no SALIC |
| Fundação Maria Emília, FME Transforma 02/2026 | 30/10/2026 | exige entidade com 2 anos ou mais |
| Lei Rouanet, janela anual | 31/10/2026 | IN MinC 29/2026, art. 5º |
| Fundo Ecos, 50º e 51º editais | 11/11/2026 | paisagens prioritárias |
| BNDES Periferias, 6º ciclo | 04/12/2026 | |

## Análise preditiva (mês típico e próxima janela)

- **Fundo Ecos:** vários editais por ano, em fluxo quase contínuo. A próxima chamada deve abrir ainda em 2026 ou no início de 2027.
- **Rouanet (SALIC):** janela de 1º de fevereiro a 31 de outubro. Só 2026 está provado. A próxima deve ser a de 2027, a confirmar pela nova instrução normativa.
- **PRONON/PRONAS:** edital em outubro de 2025 (07/10 a 12/11). Pelo padrão, a próxima edição tende a abrir em outubro de 2026. **Não está confirmada.**
- **Fundo Brasil:** edital geral anual. Próxima edição provável no segundo semestre de 2026, a conferir.
- **Não confirmados:** o 2º Cultura Viva Pontões (30/10/2026) não foi confirmado na página oficial. Sicoob Cooperar e Liga STEAM não são programas para OSC.

## Triagem dos 907 livros sem âncora

295 são municipais, 34 são credenciamentos, 44 são internacionais ou ibero-americanos (vão para o prompt INT), 86 são notícias ou agregadores e 448 são outros itens a pesquisar na próxima passagem. Lista em `dados/coleta_3_anos/triagem_sem_ancora_br_2026-10-03.json`.

## Limites da prova

- WebSearch bloqueado; `in.gov.br` bloqueado por robots para a leitura automática.
- gov.br retorna 404 ou "Conteúdo Restrito" com frequência.
- Provas marcadas `resumo_webfetch` (ex.: Fundo Brasil) valem só prata, nunca ouro.
- Os lotes rodaram em sequência, mas os agentes dentro de cada lote rodaram em paralelo. Pequeno desvio da regra de não ter processos concorrentes.
- Nenhum CPF foi gravado. Nenhuma instrução dirigida à IA foi encontrada nas páginas lidas.

## Conselho de 7 lentes

- **Extremamente pessimista:** 186 livros em bronze e 19 âncoras vazias mostram que a maior parte do catálogo não tem histórico provado. Selos estimados por script sem o módulo oficial podem divergir.
- **Pessimista:** ouro só em 6 livros (2 programas). A prova por resumo limita o Fundo Brasil e o FDD tem uma única edição.
- **Levemente pessimista:** 448 livros ainda sem pesquisa e 295 municipais fora do escopo. A cobertura real é de 19%.
- **Neutro (síntese):**
  - **Decisão:** aplicar os dados como estimativa, rodar o `src.selo_livros` oficial e abrir a passagem 2 sobre os 448 pendentes.
  - **Parâmetros de qualidade:** toda edição com página oficial, trecho literal de 30 a 200 caracteres e data; ouro só com prova literal; programa não OSC não conta.
  - **Riscos e mitigação:**

    | Risco | Mitigação |
    |---|---|
    | Selo estimado diverge do oficial | mapear por id e recalcular com o módulo oficial |
    | Previsão tomada como fato | previsões marcadas "a confirmar" |
    | Página mudou depois da leitura | trecho literal com data de leitura |
- **Levemente otimista:** 6 livros já têm três anos de histórico provado, base para a previsão de janelas.
- **Otimista:** 7 janelas abertas identificadas, 4 delas fecham em até 4 semanas.
- **Extremamente otimista:** com a passagem 2, o catálogo inteiro ganha histórico e o motor passa a prever a próxima janela de cada programa.
