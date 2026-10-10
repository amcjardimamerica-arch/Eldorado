# Relatório · Revisão das oportunidades abertas · Parte 1 (Goiás) · 10/10/2026

Escopo: lista A, com 71 oportunidades GO, e lista B, com 267 edições de diário oficial. Todos os 338 ids receberam veredito, com prova registrada nos arquivos `resultado_ABERTAS_P1-GO_A01..A04.json` e `B01..B09.json`. O arquivo `RETOMADA-PARTE-1-GO.json` está com `"concluido": true`. Nada foi enviado ao GitHub (regra permanente).

## 1. Totais por veredito

| Veredito | Lista A | Lista B | Total |
|---|---|---|---|
| ouro | 9 | 0 | 9 |
| prata | 2 | 0 | 2 |
| bronze | 1 | 0 | 1 |
| pendente | 1 | 2 | 3 |
| encerrada | 11 | 30 | 41 |
| fora_perfil | 6 | 22 | 28 |
| duplicata | 7 | 1 | 8 |
| ruido | 34 | 212 | 246 |
| **Total** | **71** | **267** | **338** |

Na lista B, 56 edições ficaram como `ato_identificado` e 211 como `sem_oportunidade`.

## 2. Oportunidades ouro abertas (12 itens com trecho, site oficial e prazo vigente)

| id | Oportunidade | Valor | Prazo final |
|---|---|---|---|
| 7a5b6e2e | SEDS-GO Chamamento 001/2026, socioeducativo (Rio Verde/Itumbiara) | Lote I R$ 8.641.792,18; Lote II R$ 4.258.987,15 | **16/10/2026** |
| 4fd88f08 | Cachoeira Alta, PNAB 001/2026 | R$ 101.385,68 | **19/10/2026 17h** |
| 4a13aa8e | Rubiataba, PNAB 01/2026 | R$ 200.000,00 | 13/10 a **26/10/2026 17h** |
| 448c8e19 | SECTI-GO 002/2026, Cidadão Tech 60+ | R$ 1 mi | **26/10/2026 18h** |
| 53e16dff | SEGENP Goiânia 001/2026, Natal no Parque | R$ 5 mi | **26/10/2026 23h59** (e-mail) |
| c546d1fd | Secult-GO Edital 20/2026, Ocupa Goiás Brasilidades Futuros 2027 | R$ 1 mi | **29/10/2026 23h59** |
| d1083dc9 | Colinas do Sul, Premiação PNAB 01/2026 | R$ 43.866,00 | **01/11/2026 23h59** |
| b7aa39bf | Anater/MDA Chamada 006/2026, ATER Agroecologia (lote GO Vale do Paranã) | R$ 43 mi (nacional) | **06/11/2026** |
| 90de619c | Itaberaí, CMDCA 001/2026 | R$ 80 mil (8 × R$ 10 mil) | 03/11 a **10/11/2026 17h** |

Alertas registrados:

- **53e16dff**: o edital tem divergência interna de prazo (46 × 39 dias).
- **448c8e19**: o e-mail indicado para recurso diverge entre trechos do edital.
- **b7aa39bf**: é nacional, por isso a reclassificação para federal/BR.

## 3. Prata e bronze (motivo de não serem ouro)

- **64b098a6**, FMAS Senador Canedo, credenciamento de OSC do CMAS (prata). R$ 300 mil, de 11/05/2026 a 11/05/2027. Faltam Resultado, Prazo de recurso, Anexos e Destinação, porque o servidor de arquivos do PNCP não entregou o PDF.
- **b5199edf**, Pirenópolis, oficinas de música por Termo de Colaboração (prata). R$ 300 mil, até 16/09/2027. Faltam os mesmos quatro itens, pelo mesmo motivo.
- **97773a72**, Corumbá de Goiás, Aviso 3/2026 PNAB (bronze). Prazo de 01 a 15/10, com prova no DOU, p. 205. O edital não está online. A notícia indica R$ 40 mil e 36 prêmios, mas isso é só pista e não foi aceito como prova.

## 4. Pendentes um a um

1. **cdce7341**, Piracanjuba, Aviso 001/2026 PNAB. A página oficial existe, mas os links do edital estão vazios. Faltam 7 itens (prazo, resultado, recurso, valor, requisitos, anexos e destinação). Pista: Premiação PNCV 002/2026.
2. **e412e794** (lista B), CMDCA Aparecida de Goiânia, Credenciamento 001/2025. O ato foi identificado, mas o prazo de inscrição não aparece no texto do diário.
3. **31bc5b45** (lista B), CMDPI Aparecida de Goiânia, Credenciamento 02/2023. Mesma situação. Provavelmente está encerrada; falta prova.

Pistas novas, ainda não registradas como `novo-` por falta de documento oficial:

- Piracanjuba, Premiação PNCV 002/2026;
- Hidrolina, "Chamamento 07" (DOE 7376);
- Portaria SMS 708/2026 (futuro edital de saúde).

## 5. Reclassificações sugeridas

- **b7aa39bf**: situação aberta, uf BR, nível federal, tipo edital.
- **81174474** (Bondinho Pão de Açúcar): encerrada em 09/10, uf RJ, nível privada.
- **db79db77** (ArcelorMittal): encerrada em 30/09, uf SC, nível privada.
- **3dcafbd7** e **b6093acc** (Aperam): uf MG, nível privada.
- **4ca98d4c** e **5e39a0f1**: uf BR, nível privada.
- Marcadas como situação encerrada: 529e7f3f, 5b991f65, db310a0f, 93aa2d9d, e6801d29, 3a3514f6, 121e6786, 65aa2703, 35720136, entre outras (ver JSON). Observação sobre **e6801d29**: o link aponta para outro processo.
- 8 registros da lista A que são na verdade edições de diário: tipo_registro `edicao_diario`.

## 6. Eficiência dos 12 itens

Base: as 13 oportunidades vivas (ouro, prata, bronze e pendente da lista A).

| Item | Encontrado com trecho | Pendente |
|---|---|---|
| Objeto | 13 | 0 |
| Órgão / financiador | 13 | 0 |
| Território | 13 | 0 |
| Esfera | 13 | 0 |
| Área de atuação | 13 | 0 |
| Prazo de inscrição | 12 | 1 |
| Valor | 11 | 2 |
| Requisitos | 11 | 2 |
| Resultado | 9 | 4 |
| Prazo de recurso | 9 | 4 |
| Anexos | 9 | 4 |
| Destinação | 9 | 4 |

Os gargalos são sempre os mesmos quatro itens (Resultado, Recurso, Anexos e Destinação). Eles só aparecem no edital completo, nunca no aviso ou no registro do PNCP.

## 7. Selos antes e depois

- Depois: 9 ouro, 2 prata e 1 bronze. Os outros 59 registros da lista A saem da vitrine de abertas (encerrada, fora_perfil, duplicata ou ruído).
- O selo anterior de cada id não foi guardado neste lote. A comparação fina deve ser feita na implantação, cruzando com `dados/abertas.json`.
- Na prática, 83% da lista A (59/71) não era oportunidade aberta e utilizável.

## 8. Limitações declaradas

- **Lista B:** a varredura das 211 edições `sem_oportunidade` foi heurística, buscando no texto integral por títulos de abertura (edital, chamamento, credenciamento, premiação etc.). Um ato com título atípico pode ter escapado.
- **Leitura por imagem:** editais escaneados ou com fonte quebrada foram lidos por imagem (Goiatuba e Secult 20/2026). O risco de erro de transcrição é baixo, mas existe.
- **PNCP:** o servidor de arquivos ficou instável, o que impediu o ouro de 64b098a6 e b5199edf.
- **Possível download indevido:** a navegação até um .txt do Querido Diário pode ter gerado um download no seu computador. Verifique a pasta Downloads.
- **Local de gravação:** não houve acesso à Área de Trabalho nesta sessão. Os arquivos foram entregues pelo chat; ao baixar, salve na Área de Trabalho.

## 9. Conselho de 7 lentes

- **Extremamente pessimista:** 211 edições foram descartadas por heurística, e uma única oportunidade perdida invalida a promessa do sistema. Além disso, prazos de 16 e 19/10 vencem antes da implantação, se ela atrasar.
- **Pessimista:** três dos nove ouros têm divergências internas (prazo, e-mail de recurso, abrangência nacional). Se forem exibidos como ouro sem alerta, a entidade pode perder o prazo ou recorrer ao endereço errado.
- **Levemente pessimista:** as pratas dependem de um servidor instável, e o bronze de Corumbá depende de inscrição presencial, o que limita o alcance.
- **Neutro (decisão):** aprovar a implantação. Critérios de qualidade e mitigações:
  1. exibir os alertas junto do selo ouro;
  2. ordenar a vitrine pelo prazo mais próximo (SEDS 16/10 e Cachoeira Alta 19/10 em destaque imediato);
  3. tentar de novo os PDFs do PNCP de 64b098a6 e b5199edf na Parte 2 ou em rotina semanal;
  4. reamostrar 10% das 211 edições `sem_oportunidade` com leitura humana;
  5. criar registros `novo-` para Piracanjuba PNCV 002 e Hidrolina 07 assim que houver documento oficial.
- **Levemente otimista:** a limpeza tira 59 falsas abertas da vitrine e aumenta a confiança no selo.
- **Otimista:** cerca de R$ 64 milhões em oportunidades ouro vigentes com trecho literal. Destes, R$ 21 mi são editais goianos e R$ 43 mi correspondem à chamada nacional da Anater.
- **Extremamente otimista:** o padrão de gargalo (os quatro itens que só aparecem no edital completo) vira regra do motor: buscar o PDF integral antes de tentar o selo. Isso eleva o rendimento de ouro nas Partes 2 e 3.
