# Parecer — Desmonte dos motores indexadores (02/10/2026)

**Conselho técnico** (chief engineer, staff engineer, CTO e professores de computação, Python) · **Associação:** A.M.C. Jardim América

Pedido do titular: parecer **individual** de cada indexador (motores 11 e 18 a 23 do painel); eliminar o ineficaz e o que já é coberto por outro motor ou lê o mesmo local; separar cada site em um motor próprio, com o nome do local, uma finalidade e uma fonte. Números: leitura de 02/10/2026 (`docs/dados/indexadores.json`).

Critérios: **vira motor** — fonte própria de oportunidades, com indício real ou financiador relevante; **eliminado** — já coberto por outro motor, lê o mesmo local, proíbe robôs sem caminho alternativo ou não rendeu nada sendo agregador; **unido** — dois leitores do mesmo local.

## Motor 11 — Indexadores — dados abertos de governo

**Como funciona:** arquivo oficial atualizado todo dia (Transferegov: programas com recebimento de propostas aberto)

| site | leituras | indícios no acervo | no fluxo | falhas | decisão |
|---|---|---|---|---|---|
| Transferegov — programas abertos a propostas (dados abertos Siconv) | 1 | 11 | 11 | 0 | **vira motor** `site-transferegov` — Transferegov: programas e parcerias com OSC abertos na plataforma federal (dados abertos) |

**Veredito:** o indexador deixa de existir como motor; 1 site(s) viram motor próprio.

## Motor 18 — Indexadores — APIs públicas de editais

**Como funciona:** API JSON paginada: Farol Cultural (/api/v1/editais), rede Mapas Culturais (uma instância por estado ou cidade) e Transferegov (programas)

| site | leituras | indícios no acervo | no fluxo | falhas | decisão |
|---|---|---|---|---|---|
| Farol Cultural — editais culturais abertos (API) | 6 | 493 | 384 | 0 | **vira motor** `site-farol-cultural` — Farol Cultural: editais de cultura de todo o Brasil, pela API pública do portal |
| Rede Mapas Culturais — oportunidades com inscrição aberta | 6 | 32 | 32 | 3 | **vira motor** `site-mapas-culturais` — Mapas Culturais: editais das redes estaduais e municipais de cultura que usam a plataforma |
| Transferegov — programas do módulo Gestão de Parcerias (API) | 1 | 5 | 5 | 0 | **unido** ao motor `site-transferegov` (mesma plataforma) |
| SALIC e editais do MinC (motor próprio) | 0 | 0 | 0 | 0 | **eliminado** — coberto pelo motor 16 (SALIC — Ministério da Cultura): o mesmo local não é lido duas vezes |

**Veredito:** o indexador deixa de existir como motor; 2 site(s) viram motor próprio, 1 eliminado(s).

## Motor 19 — Indexadores — coleta assistida e pilotos (sites que proíbem robôs)

**Como funciona:** fila de coleta no navegador do titular (botão 'Capturar indícios' ou Claude no Chrome), rota indireta por outro indexador que pode ser lido e ângulos de busca para o Piloto - Espião; o Interceptador comprova na fonte oficial

| site | leituras | indícios no acervo | no fluxo | falhas | decisão |
|---|---|---|---|---|---|
| Prosas — editais e prêmios para OSCs | None | 0 | 0 | 0 | **eliminado** — o robots.txt do Prosas proíbe robôs; a lista pública dos editais do Prosas já chega pela CapitaAI (60 na 1ª leitura) |
| Mapa das OSC (Ipea) — editais | None | 0 | 0 | 0 | **vira motor** `site-mapa-osc` — Mapa das OSC (Ipea): coleta assistida (o site proíbe robôs). *Corrigido na implantação: o motor antigo do Mapa das OSC está desligado e era coberto por este indexador — eliminar os dois deixaria o portal sem cobertura.* |
| FINEP — chamadas públicas | None | 0 | 0 | 0 | **vira motor** `site-finep` — Finep: chamadas públicas (coleta assistida: o site proíbe robôs) |
| Itaú Social — editais | None | 0 | 0 | 0 | **vira motor** `site-itau-social` — Itaú Social: editais (coleta assistida: o site proíbe robôs) |
| Embaixada dos EUA — apoios a projetos | None | 0 | 0 | 0 | **vira motor** `site-embaixada-eua` — Embaixada dos EUA: pequenas doações a projetos (coleta assistida) |
| Petrobras — seleções socioambientais e culturais | None | 0 | 0 | 0 | **vira motor** `site-petrobras` — Petrobras: seleções socioambientais (coleta assistida: o site proíbe robôs) |
| Fundação Banco do Brasil — editais | None | 0 | 0 | 0 | **vira motor** `site-fundacao-banco-do-brasil` — Fundação Banco do Brasil: editais (coleta assistida: o site proíbe robôs) |
| Embaixadas com pequenos projetos (Japão, Canadá, Alemanha, Austrália, Reino Unido, Países Baixos, Noruega) | None | 0 | 0 | 0 | **vira motor** `site-embaixada-japao` — Embaixada do Japão: apoio a projetos comunitários (coleta assistida) |

**Veredito:** o indexador deixa de existir como motor; 6 site(s) viram motor próprio, 2 eliminado(s).

## Motor 20 — Indexadores — feeds RSS e WordPress

**Como funciona:** feed RSS/Atom da seção de editais ou API REST do WordPress (posts e tipos próprios de edital), com leitura do artigo só quando o item é novo

| site | leituras | indícios no acervo | no fluxo | falhas | decisão |
|---|---|---|---|---|---|
| Observatório do Terceiro Setor — editais | 1 | 42 | 42 | 0 | **vira motor** `site-observatorio-terceiro-setor` — Observatório do Terceiro Setor: editais publicados na seção temática do portal |
| ABCR — editais divulgados pelos captadores | 1 | 20 | 18 | 0 | **vira motor** `site-abcr` — ABCR — Associação Brasileira de Captadores de Recursos: editais divulgados pela associação dos captadores |
| IDIS — notícias de editais (RSS) | 1 | 2 | 2 | 0 | **vira motor** `site-idis` — IDIS — Instituto para o Desenvolvimento do Investimento Social: chamadas e editais de investimento social |
| fundsforNGOs — chamadas internacionais abertas ao Brasil | 0 | 0 | 0 | 1 | **eliminado** — ineficaz: recusa o robô (bloqueio do WAF) e é agregador estrangeiro de conteúdo já coberto |
| Rede Comuá — editais dos fundos independentes | 1 | 6 | 5 | 0 | **vira motor** `site-rede-comua` — Rede Comuá: editais dos fundos independentes de filantropia |
| Fundo Brasil de Direitos Humanos — editais | 1 | 5 | 2 | 0 | **vira motor** `site-fundo-brasil` — Fundo Brasil de Direitos Humanos: editais de direitos humanos |
| Fundo Casa Socioambiental — chamadas | 1 | 2 | 1 | 0 | **vira motor** `site-fundo-casa` — Fundo Casa Socioambiental: chamadas socioambientais |
| CESE — editais | 1 | 11 | 0 | 0 | **vira motor** `site-cese` — CESE — Coordenadoria Ecumênica de Serviço: editais de apoio a projetos populares |
| GIFE e Capta (motor 22) | 0 | 0 | 0 | 0 | **eliminado** — coberto pelo motor 18 (GIFE), que já lê GIFE e Capta pela API |

**Veredito:** o indexador deixa de existir como motor; 7 site(s) viram motor próprio, 2 eliminado(s).

## Motor 21 — Indexadores — listagens de editais dos financiadores

**Como funciona:** página de editais do site + página de cada edital novo, com as regras de cada site no catálogo

| site | leituras | indícios no acervo | no fluxo | falhas | decisão |
|---|---|---|---|---|---|
| Fundo Baobá — editais | 14 | 11 | 4 | 0 | **vira motor** `site-fundo-baoba` — Fundo Baobá: editais para equidade racial |
| BrazilFoundation — edital | 1 | 1 | 0 | 0 | **vira motor** `site-brazilfoundation` — BrazilFoundation: editais de apoio a organizações brasileiras |
| Inter-American Foundation — chamadas | 0 | 0 | 0 | 1 | **vira motor** `site-iaf` — IAF — Fundação Interamericana: chamadas de apoio a organizações de base (recusa IP estrangeiro) |
| Editais Culturais (editaisculturais.com.br) | 10 | 4 | 2 | 0 | **vira motor** `site-editais-culturais` — Editais Culturais: editais de cultura reunidos no portal |
| Funarte — editais | 25 | 20 | 18 | 3 | **vira motor** `site-funarte` — Funarte: editais da Fundação Nacional de Artes |
| Fundo das Nações Unidas para a Democracia (UNDEF) | 3 | 2 | 2 | 0 | **vira motor** `site-undef` — UNDEF — Fundo das Nações Unidas para a Democracia: chamadas anuais para a sociedade civil |
| Radar de Editais — Portal do Impacto | 1 | 0 | 0 | 0 | **eliminado** — ineficaz: nenhum indício na leitura; agregador cujo conteúdo já chega pela CapitaAI e pelo Observatório |
| FAPEG e Secult-GO (motor estadual) | 0 | 0 | 0 | 0 | **eliminado** — coberto pelo motor 14 (Oportunidades Estaduais Governamentais de Goiás), que lê a FAPEG e a Secult |

**Veredito:** o indexador deixa de existir como motor; 6 site(s) viram motor próprio, 2 eliminado(s).

## Motor 22 — Indexadores — ponte Brasil (sites que recusam IP estrangeiro)

**Como funciona:** os mesmos leitores, com saída pelo IP brasileiro do computador do titular (scripts/coleta_brasil.py, de 3 em 3 horas, das 6h10 às 21h10, com o computador ligado); máquina virtual no Brasil e ponte HTTP em hospedagem ficam como alternativas futuras

| site | leituras | indícios no acervo | no fluxo | falhas | decisão |
|---|---|---|---|---|---|
| Portal Filantropia — editais | None | 0 | 0 | 0 | **vira motor** `site-rede-filantropia` — Rede Filantropia: editais divulgados pela rede (lida pelo computador do titular: recusa IP estrangeiro) |

**Veredito:** o indexador deixa de existir como motor; 1 site(s) viram motor próprio.

## Motor 23 — Indexadores — sitemaps e páginas estruturadas

**Como funciona:** sitemap.xml com data de alteração (lastmod) + dados estruturados (JSON-LD) e links oficiais de cada página nova ou alterada

| site | leituras | indícios no acervo | no fluxo | falhas | decisão |
|---|---|---|---|---|---|
| CapitaAI — páginas públicas de captação (sitemap) | 86 | 329 | 319 | 0 | **vira motor** `site-capitaai` — CapitaAI: editais e oportunidades de captação, incluindo a lista pública dos editais do Prosas |

**Veredito:** o indexador deixa de existir como motor; 1 site(s) viram motor próprio.

## Regras dos motores gerados

- **Leitura a partir da última leitura:** cada leitura registra a cobertura de datas (publicação mais antiga e mais recente). Se a leitura não chegou até a data da anterior e esgotou as páginas permitidas, há **lacuna**: a próxima leitura volta mais páginas (até 10 a mais), até fechar o buraco.
- **Registro compacto de cada leitura** (`estado/indexadores/estado.json`, por site): hash do que foi lido, quantidade, cobertura de datas, lacuna — só as 30 últimas leituras. O texto útil (título, datas, link oficial, prazo) fica no acervo dos indícios; nada mais é guardado.
- **Motor criado quando falta:** indício cujo site oficial não tem motor, visto 2 ou mais vezes, gera um motor novo com leitor de listagem genérico (`criado_automaticamente`), em observação.
- **Ordem:** os motores gerados entram a partir do 24, depois do Piloto - Interceptador, na ordem do rendimento.

## Conselho de 7 lentes

1. **Extremamente pessimista:** "Vinte e quatro motores no lugar de sete multiplicam o painel; os de coleta assistida vão ficar cinza para sempre."
2. **Pessimista:** "A regra de lacuna depende de o site expor datas; listagem sem data nunca fecha o buraco com certeza."
3. **Levemente pessimista:** "Motor criado sozinho pode nascer quebrado; precisa de observação antes de contar como fonte."
4. **Neutro:** pondera abaixo.
5. **Levemente otimista:** "Cada fonte com o próprio nome deixa claro o que rende e o que não rende."
6. **Otimista:** "Eliminar o que lê o mesmo local corta requisições e falsos 'motores ativos'."
7. **Extremamente otimista:** "Com a cobertura de datas, nenhum dia fica sem leitura sem que o sistema saiba."

**Síntese do neutro:** desmontar como proposto. Parâmetros: motor de coleta assistida aparece como "assistida" (nunca "falhou"); motor criado automaticamente começa "em observação" e só é promovido com indício real; a lacuna é medida onde o site dá data e, onde não dá, a leitura percorre as páginas retroativas fixas.
