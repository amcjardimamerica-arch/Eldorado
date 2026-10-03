# Parecer — Pilotos Espião e Interceptador: falhas de acesso e a solução pelo computador do titular (03/10/2026)

**Conselho técnico** (chief engineer, staff engineer, CTO e professores de computação, Python) · **Associação:** A.M.C. Jardim América

## 1. Números medidos (estado/piloto e estado/interceptador, 29/09 a 03/10)

| | Piloto Espião | Piloto Interceptador |
|---|---|---|
| Missões por dia | 182 a 344 (média 233) | 48 a 99 (média 54) |
| Com algum resultado | 65% (5,2 achados por missão) | 69% (ao menos 1 item comprovado) |
| **Com resultado que serve** | **3,6%** acham oportunidade ABERTA | **1%** chegam a "validada"; 72% ficam "insuficiente" |
| Duração | — | 13 min nos voos com resultado; 11 min no geral |
| Falha principal | das 6 vias de busca, só o DuckDuckGo responde ao GitHub (Google, Bing, Mojeek e outras: zero) | "nenhuma fonte legível" (24 voos: página que não abre ou só monta com JavaScript); "o modelo não devolveu JSON" (9) |

## 2. Parecer de cada Piloto

**Piloto Espião.** O volume é alto e o rendimento é baixo porque ele busca quase sempre pela mesma porta (DuckDuckGo) e
acha, na maior parte, páginas de agregadores (CapitaAI, blogs) em vez do edital. Mais missões não resolvem: a falha é de
ACESSO às buscas. Missões repetidas com a mesma consulta (uma foi tentada 310 vezes, com 3 resultados) gastam o dia.

**Piloto Interceptador.** Ele acha a página, mas não consegue LER: o servidor do GitHub é recusado por portais e a
leitura simples não executa o JavaScript que monta muitas páginas oficiais. Daí os 72% "insuficientes" e os 24 voos
"nenhuma fonte legível". O erro de JSON (9) é do modelo pequeno e já tem nova tentativa.

## 3. A solução (implantada)

1. **Navegador do titular** (`src/navegador_local.py`): no computador do titular, as buscas e a leitura de páginas
   passam por um navegador de verdade — o Microsoft Edge que já vem no Windows, controlado pelo Playwright (ferramenta
   aberta da Microsoft), com perfil próprio do Eldorado e o IP do titular. Lê a página DEPOIS do JavaScript. Ritmo de
   pessoa (3 a 7 segundos entre buscas), teto de 400 usos por dia, nada de login nem de verificação: se o buscador
   pedir, a via descansa. Prova feita: uma página montada por JavaScript deu só "Edital" na leitura simples e o texto
   completo (prazo, valor e documentos) no navegador.
2. **Onde entra:** primeira via de busca dos Pilotos no computador; leitura de página vazia ou curta; leitura do edital
   pelo Interceptador quando a página não abre.
3. **Na nuvem, 2 buscas por voo** (só o DuckDuckGo responde ao GitHub; o resto era tempo perdido).
4. **A ponte da Hostgator para os Pilotos:** não serve para BUSCAR (é IP de datacenter, que Google e Bing tratam como
   robô); serve para LER páginas oficiais (.gov.br, .jus.br, .leg.br, .mp.br) — o Interceptador na nuvem a usa quando a
   página não abre. O TJ-GO (Cloudflare) recusa também a ponte.
5. **Instalação:** a rotina dos Pilotos no computador (`scripts/pilotos_brasil.py`) instala o Playwright sozinha, uma
   vez; usa o Edge; sem ele, baixa o Chromium. Se falhar, os Pilotos voam como antes.

## 4. Conselho de 7 lentes

1. **Extremamente pessimista:** "Buscador que perceber automação vai pedir verificação; se o computador ficar desligado, tudo volta ao GitHub."
2. **Pessimista:** "Um navegador aberto consome memória; em computador fraco, as missões ficam mais lentas."
3. **Levemente pessimista:** "O teto de 400 por dia é menor que as 233 missões do Espião com várias buscas cada: será preciso escolher melhor as consultas."
4. **Neutro:** pondera abaixo.
5. **Levemente otimista:** "Ler a página depois do JavaScript resolve de uma vez o 'nenhuma fonte legível'."
6. **Otimista:** "Com IP residencial e Edge real, Bing e DuckDuckGo respondem como a uma pessoa — o Espião sai da porta única."
7. **Extremamente otimista:** "Menos missões, mas certeiras: o rendimento de abertas pode sair de 3,6% para dezenas de %."

**Síntese do neutro:** implantar. Parâmetros: o navegador só no computador do titular; ritmo de pessoa e teto diário;
verificação pedida = via descansa (nunca resolver); sem o Playwright, nada muda. Próximo ajuste recomendado: reduzir as
missões repetidas do Espião (a consulta tentada 310 vezes) — qualidade em vez de volume.
