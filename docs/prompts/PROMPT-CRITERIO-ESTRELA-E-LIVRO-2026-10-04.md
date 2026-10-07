# Prompt — Critério único da estrela e do livro (04/10/2026)

**Finalidade:** estrela ouro e livro ouro só com os 12 itens validados (ou dispensados com justificativa de que não se aplicam).

1. **Item resolvido:** validado = valor real (não vale vazio, "não informado", "não localizado"); dispensado = só com a
   justificativa de que NÃO SE APLICA ("dispensado pelo edital…", "não se aplica…"). Item não informado é FALTA.
2. **Critério (estrela e livro):** bronze = Objeto + Prazo de inscrição + Território · prata = bronze + Valor + Requisitos ·
   ouro = os 12 itens resolvidos.
3. **Estrela:** só edital ABERTO, pelos itens do edital atual; fechado = sem estrela.
4. **Livro:** o HISTÓRICO conhecido (itens do livro + campos e edições do histórico), para a análise preditiva; a série de
   edições fica em `selo_livro.selo_serie`.
5. **Execução:** `src/criterio_selos.py` (critério único) usado em `fluxo_oportunidades._selos_dos_itens` (estrela) e em
   `selo_livros.aplicar` (livro); relatório `docs/relatorios/ELDORADO-OPORTUNIDADES-ABERTAS-ESTRELA-E-LIVRO-2026-10-04.xlsx`.
