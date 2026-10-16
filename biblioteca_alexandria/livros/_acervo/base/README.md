A BASE SÓLIDA DA BIBLIOTECA — leve, textual, por pastas, de leitura imediata.

O que o sistema tinha: 3.946 arquivos JSON espalhados, uma ficha por pasta, os vereditos do titular
guardados FORA da Biblioteca (em dados/editais/extraidos) e uma "previsão" construída sobre edições de
diário (Betim/MG a cada mês não é edital que volta: é o diário que sai). Nada disso era base para
direcionar motor, Piloto ou Farol.

O que esta base produz, em biblioteca_alexandria/base/ (JSONL: uma linha por registro, abre em qualquer
ferramenta, grep e pandas leem em milissegundos):

    editais/<ano>.jsonl        HISTÓRICO — todo edital conhecido, um esquema só, com o veredito do titular
    aprovados.jsonl            os editais que o titular selecionou: a base de pontuação
    recorrencia.jsonl          PREDITIVO — quem publica de novo, em que mês, com que força; próxima janela
    pontuacao/criterios.json   o que separa aprovado de reprovado, medido: pesos por tema, esfera, UF,
                               órgão recorrente, faixa de valor, exigências
    leis/indice_por_esfera.json + lacunas.json   o que a Biblioteca de leis cobre e o que falta para
                               Goiás, Goiânia e a Região Metropolitana
