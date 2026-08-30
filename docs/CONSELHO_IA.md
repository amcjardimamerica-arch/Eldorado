# Conselho independente de IA

Cada caso do Farol contém sete diretórios. O arquivo `entrada.json` de um conselheiro deve ser enviado em uma chamada nova, sem histórico e sem anexar as outras seis entradas ou respostas.

## Regras

- A personalidade é uma lente metodológica inspirada em legado público, não imitação nem opinião real.
- A posição crítica é sorteada e muda na nova rodada.
- Cada saída deve obedecer ao esquema de `formato_saida` e ser salva como `resposta.json` no mesmo diretório.
- `python -m src.parecer_final` só deve ser integrado a um executor depois da validação das sete respostas.
- O modelo final é definido por `FAROL_FINAL_MODEL`; use o melhor modelo disponível e autorizado no ambiente, sem gravar chaves no GitHub.
- Não envie PII, dados bancários, documentos pessoais ou fotografias sem autorização.

O repositório prepara os pacotes e valida a independência. Chamadas comerciais externas permanecem desligadas em `config/ia.json` até que o proprietário configure provedor, modelo, limite de gastos, segredo e política de dados.
