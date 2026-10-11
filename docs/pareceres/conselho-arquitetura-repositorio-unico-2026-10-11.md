# Conselho da arquitetura — repositório único de oportunidades (11/10/2026)

**Problema:** a tela inicial contava o fluxo (562), a caixa contava outro conjunto (388), o Cartório um terceiro (517) e os lotes do Chrome saíram da caixa — por isso 283 dos 400 verificados nem estavam no que a tela contava, e as 311 "em verificação" nunca foram verificadas. Informação segregada por origem obrigava pesquisas diárias que nunca esgotavam.

**Decisão:** um REPOSITÓRIO ÚNICO (`src/repositorio_unico.py` → `dados/oportunidades/repositorio_unico.json`): um registro por oportunidade, com todas as origens, a prova de cada item na fonte, o estado, a estante (sem livro · bronze · prata · ouro, como classificador) e o próximo passo decidido pela rede neural e pela skill da origem. Todos os painéis e filas derivam dele.

## Os sete prompts e o que cada um implantou

| Conselheiro | Prompt | Implantado |
|---|---|---|
| Dra. Irene Lacerda (extremamente pessimista) | "Prove que a tela, o Cartório e o Chrome contam o mesmo universo; qualquer divergência é defeito." | `auditar()`: compara o repositório com a tela, a fila do Cartório e o lote do Chrome; divergência vira alerta no resumo. |
| Prof. Caio Menezes (pessimista) | "Nenhuma oportunidade pode ficar parada sem dono e sem próximo passo." | Todo registro tem próximo passo; `no_passo_desde` e `estagnado` (mais de 3 dias no mesmo passo sobe para o topo da fila). |
| Eng. Luana Freire (levemente pessimista) | "Uma oportunidade, um registro, um livro — sem cópia por motor." | Id canônico na entrada (revisão humana + regra M1), com todos os `ids_origem` e `fontes`; um livro por oportunidade (`src/unificar_livros.py`). |
| Dr. Otávio Lemos (neutro) | "Nada vale sem prova na fonte; nenhum dado é criado." | Itens em quatro estados: comprovado (trecho + documento + página), dispensado (justificado), não comprovado (lido pelo motor, sem prova), falta. "Confirmada" do motor só vale com objeto e prazo comprovados. |
| Eng. Diego Arakaki (levemente otimista) | "Uma fila só, para todas as ferramentas." | O Cartório lê a fila do repositório (`_repositorio()`), no mesmo universo da tela. |
| Profa. Clara Nogueira (otimista) | "Cada origem com a sua rota de extração." | `config/skills_extracao_origem.json`: rota e ordem das 10 abordagens por origem (PNCP, Querido Diário, agregador, Interceptador, Espião, diário oficial, site oficial, revisão); o Cartório segue a ordem da skill. |
| Dr. Fábio Rangel (extremamente otimista) | "O Chrome é exceção, nunca rotina." | `scripts/gerar_lote_chrome.py`: só registros do repositório com as 10 abordagens esgotadas; recusa se o total não bater com a fila. |

## A rede neural em cada passo
1. **Entrada:** todas as origens no repositório, duplicatas fundidas.
2. **Aplica-se a OSC?** A rede dá a nota; abaixo de 0,12, sem prova e sem prazo, o próximo passo é "dispensar — confirmar na fonte".
3. **Prioridade:** prazo vigente primeiro, depois a nota da rede; estagnados sobem.
4. **Próximo passo:** achar o site oficial → abordagens do Cartório na ordem da skill → (exceção) Chrome.
5. **Prova:** cada item comprovado entra no mesmo registro.
6. **Estante:** sem livro · bronze · prata · ouro pela prova dos 12 itens.
