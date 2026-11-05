# Verificação externa · GRUPO 3 de 3 · lote-2026-11-05-externa-completo (partes 17 a 24)

## Como implantar
1. Copie `verificacao/vereditos/*.json` para a mesma pasta no repositório. São 8 arquivos, um por parte, cada um com `lote`, `lote_gerado_em` e `total_livros` iguais aos do lote.
2. Os relatórios de melhoria ficam em `relatorios/`. Há um por parte e um consolidado (`relatorio-melhoria-motores-grupo-3.json`). Eles alimentam o aprendizado dos motores.
3. `LISTA-LIVROS-...xlsx` é a planilha de controle. Tem a decisão e o motivo de cada livro, e as abas "Controle das partes" e "Relatório por livro".

## Entrega (R41): 8 de 8 partes completas, 369 de 369 livros
| Parte | Livros | valido | encerrada | arquivar | descartar |
|---|---|---|---|---|---|
| 17 | 50 | 1 | 0 | 1 | 48 |
| 18 | 50 | 2 | 1 | 0 | 47 |
| 19 | 50 | 8 | 4 | 11 | 27 |
| 20 | 50 | 24 | 6 | 3 | 17 |
| 21 | 50 | 1 | 7 | 1 | 41 |
| 22 | 50 | 6 | 1 | 2 | 41 |
| 23 | 50 | 0 | 7 | 6 | 37 |
| 24 | 19 | 1 | 5 | 6 | 7 |
| **Total** | **369** | **43** | **31** | **30** | **265** |

O validador conferiu todos os vereditos:
- todas as decisões usam os 4 termos aceitos;
- todo veredito tem motivo;
- em todo livro não descartado, os 12 itens estão resolvidos, por item com trecho e url ou por dispensa;
- nenhuma dispensa cai no núcleo;
- toda dispensa tem pelo menos 20 caracteres e uma das expressões aceitas.

Os lotes de documentos listados em `expurgo_junto` não fazem parte desta entrega, porque o prompt do grupo diz "neste grupo, só os livros".

## Aprendizados para os motores (os que mais se repetiram)
1. **Páginas do gov.br viraram livros: 77 dos 265 descartes.** Excluir os caminhos `/navegue-por-temas/`, `/assuntos/`, `/acoes-e-programas/`, `/composicao/`, `/acesso-a-informacao/`, `/noticias*`, `/orgaos/` e `/comunicacao/`. A exceção é a página que tem link para PDF de edital com prazo. O mesmo vale para os menus do BNDES e do PNCP (pncp.gov.br/pncp/pt-br/*, /app/*).
2. **Edições inteiras do Querido Diário (31).** Não transformar a edição em livro. Extrair só o ato de chamamento com período de inscrição e filtrar os municípios de fora de GO que não sejam capital.
3. **Replicadores.** CapitaAI, Observatório, DevelopmentAid, opportunitiesfeed, fundsforngos, ejornais, agrolink, AltEditais, Conjunta e Instagram não são fonte. Seguir sempre até o financiador e conferir lá o status, porque o Capta dizia "contínuo" para Ford, IAF e Claro, que não têm chamada aberta.
4. **Certidões erradas.** Em 34 livros as certidões foram corrigidas:
   - certidão copiada de outro edital (Bálsamo, Gráfica do Exército);
   - Esfera tirada de rodapé ou de "Receita Federal";
   - "Modalidade: bolsa" tirada de "Bolsa Família";
   - prazo e valor vindos do replicador.

   Regra: a certidão só vale se o trecho citar o mesmo número de edital e o mesmo órgão do livro.
5. **PNCP.** Ler o edital pela API `/arquivos`. O prazo vem do edital, não de `dataEncerramentoProposta`. Deduplicar os livros op-* com o mesmo `numeroControlePNCP`: só na parte 20 havia 8 pares.
6. **Proponente.** As chamadas das FAPs, CNPq e CAPES são para pesquisador, ICT ou doutor e devem ser excluídas. Excluir também credenciamentos "com ou sem fins lucrativos" de prestação de serviço. Os credenciamentos de catadores (Decreto 5.940) são oportunidade para OSC.
7. **Portais montados por JavaScript.** O Criança Esperança e o Prosas precisam de navegador. Não descartar por página vazia no curl. No Prosas, ler o JSON embutido na página.
8. **Editais atrás de login (SIGRP-PI).** Buscar o aviso no DOU ou no DOE e o edital em sejus.pi.gov.br/documentos/editais.
9. **Território.** Filtrar as chamadas restritas a outro país, como UNDP Quênia, Uzbequistão e Etiópia, Kellogg, MAR Fund, Expo Inclusión e "la Caixa".
10. **Catálogo.** Trocar as páginas iniciais institucionais pelas páginas de chamadas. Marcar como "só por convite" Gates, Ford, OSF, Skoll, Oak e Global Fund for Women.

## Válidos com prazo aberto (data de hoje, 05/11/2026)
- FAPESPA 018/2026: fecha hoje, 05/11. FAPESPA 019/2026: até 06/11. FAPESPA 020/2026: até 09/11.
- Rondônia, OSC: até 08/11. O livro dizia 12 a 19/11; o certo, pelo edital, é 09/10 a 08/11.
- Criança Esperança 2027: até 08/11, às 23h59.
- DNIT, catadores: documentos até 07/11.
- Gráfica do Exército, catadores: sessão em 09/11.
- SEJUS-PI APEC: até 10/11.
- Fundo Ecos Edital 50º (captacao-242): até 11/11.
- Sonhar o Mundo (SISEM-SP): até 13/11.
- Comunidades terapêuticas do Rio de Janeiro: até 25/11.
- SMADS São Paulo: até 26/11.
- Funarte Memória das Artes: até 18/12.
- PIE-SC/Celesc: até 31/12.
- Roche, associações de pacientes: até 31/01/2027.
- JBRJ 2/2026: até 21/07/2027.

Há ainda os de fluxo contínuo e cadastro permanente:
- Havan (3 livros), FAU-LAC, TechSoup/Microsoft (2), Setpar, Sesc Mesa Brasil RJ;
- APC do Japão, GFCF, Instituto ACP;
- credenciamentos de catadores: CPTM, TST, TJTO, TJAL, TRT4, TRT16, TRE-RN, MPPR, DPE-PR, IFSULDEMINAS.

## Pontos para a titular conferir
- **PCJ saneamento:** arquivado com as certidões antigas, porque o site bloqueia todas as leituras.
- **Credenciamentos de catadores de outros estados:** foram marcados valido. Pela regra "restrito a outra região", seriam arquivar.
- **Edições anteriores do catálogo:** só uma data foi confirmada (UNESCO IFCD, 2026-03-23). As demais ficaram vazias, porque não houve data oficial achada.
- **Participação sem recurso:** chamadas de participação sem recurso financeiro (COP31, Conabio, UPR Info) foram descartadas ou encerradas como não oportunidade de recurso.
- **Dispensas genéricas:** várias dispensas em encerradas e arquivadas usam "não consta nos documentos oficiais lidos".
