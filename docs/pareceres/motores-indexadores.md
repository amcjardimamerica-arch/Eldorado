# Parecer do conselho — Motores indexadores (02/10/2026)

## Decisão

Foram criados 7 motores, um por metodologia de leitura. O catálogo `config/indexadores.json` tem 32 entradas:

- 29 sites lidos pelos indexadores (uma das entradas agrupa 7 embaixadas);
- 3 delegados a motores que já existem;
- 22 instâncias da rede Mapas Culturais, dentro da entrada da rede.

Cada site tem o seu motor, com os parâmetros do próprio site.

**Motores antigos reunidos:**

| Motor antigo | Para onde foi | O que muda |
|---|---|---|
| `plat-observatorio-3setor` | `idx-feeds` | lê o RSS da seção de editais, não os rótulos da página |
| `plat-abcr` | `idx-feeds` | lê o RSS da categoria, com o link oficial de cada artigo |
| `motor-agregadores` (CapitaAI, Farol, IDIS) | `idx-sitemaps`, `idx-apis` e `idx-feeds` | ver tabela abaixo |
| `plat-mapa-osc` e `plat-prosas-oscs` | `idx-assistido` | ver "Bloqueios" |

**O antigo `motor-agregadores` passa a ler assim:**

| Site | Antes | Agora |
|---|---|---|
| CapitaAI | 40 editais por rodada | sitemap com 553 páginas públicas e 84 listagens com o prazo no cartão |
| Farol Cultural | 20 editais da listagem | API pública com os 497 editais abertos |
| IDIS | RSS | RSS filtrado por edital |

**Motores que continuam com leitor próprio:** GIFE e Capta (motor 22), MinC/SALIC e FAPEG/Secult-GO. Eles aparecem
na família `idx-feeds` como "delegados" e não são lidos duas vezes.

Tudo o que os indexadores acham é **indício**. O registro vai ao fluxo das oportunidades em
`estado/agregadores/itens.json`, com o mesmo contrato e os mesmos ids de antes. Leva o link da fonte oficial, quando o
indexador o traz. O prazo do indexador é pista até o Interceptador confirmar na fonte oficial.

## Os 7 motores

| Motor | Metodologia | Sites | Rodadas por dia |
|---|---|---|---|
| idx-feeds | feed RSS/Atom ou API REST do WordPress | Observatório, ABCR, IDIS, fundsforNGOs (tag Brasil), Rede Comuá, Fundo Brasil, Fundo Casa, CESE; GIFE/Capta delegados ao motor 22 | 6 |
| idx-apis | API JSON paginada | Farol Cultural (497 abertos), rede Mapas Culturais (MinC, Mapa Goiano, CE, PE, PA, ES, SE, PB, AP, João Pessoa, Rede das Artes e 11 candidatas sondadas toda semana), Transferegov (módulo Parcerias) | 6 |
| idx-sitemaps | sitemap.xml com data de alteração + JSON-LD e links da página | CapitaAI (inclui a página dele sobre o Prosas) | 6 |
| idx-listagens | página de editais + página de cada edital novo | Baobá, BrazilFoundation, IAF, Funarte, UNDEF, Editais Culturais, Radar do Portal do Impacto | 2 |
| idx-dados-abertos | arquivo oficial do dia | Siconv — programas com recebimento de propostas aberto a OSC | 1 |
| idx-ponte-brasil | os mesmos leitores por IP brasileiro | Portal Filantropia e todo site que a escada de rotas mandar | 6 (com ponte) e a cada coleta no Brasil |
| idx-assistido | navegador do titular + pilotos | Prosas, Mapa das OSC, FINEP, Itaú Social, Embaixada dos EUA, Petrobras, FBB, embaixadas | contínuo |

### Cotas de cada rodada

- 700 requisições e 25 minutos por rodada.
- Até 80 itens novos por site. No CapitaAI: 70 páginas e 14 listagens por rodada; as 84 listagens dão a volta em um dia.
- O que não couber fica com o cursor guardado e é a primeira coisa da rodada seguinte. A fila inicial do CapitaAI (cerca de 550 páginas) termina em um dia e meio; depois só entram as páginas novas ou alteradas.

## Calibração no navegador (02/10/2026)

Os leitores foram rodados no Chrome do titular, sobre as páginas reais, antes de entrar no repositório.

| Site | O que se mediu |
|---|---|
| Farol Cultural (API) | 497 editais abertos; 100% com link oficial, 436 com prazo (88%), 384 com UF (77%) |
| Rede Mapas Culturais | 83 oportunidades abertas na leitura de teste; 69 com UF |
| Feeds WordPress | Fundo Casa 10, Fundo Brasil 7, CESE 11, Rede Comuá 18 itens recentes |
| CapitaAI | 553 páginas /captacao/ no sitemap e 84 listagens /editais-abertos/ liberadas no robots.txt |

**O que a calibração do CapitaAI mudou no motor:**

1. **O prazo vem do cartão da listagem, não do texto do guia.** O guia de cada página é texto de apoio com datas
   ilustrativas. Em 2 das 3 páginas conferidas apareciam datas soltas como "14 de março de 2024" e "até 15 de julho de
   2026". Lidas como prazo, elas descartariam editais abertos como vencidos. O cartão da listagem traz o campo
   "Prazo: dd/mm/aaaa", junto com o órgão e o público aceito.
2. **O link oficial vem rotulado como "página oficial".** Pode apontar para o Diário Oficial da União, para um
   formulário do Google ou para o site do órgão. O rótulo agora conta pontos, e o formulário do órgão é aceito quando o
   agregador o chama de página oficial.
3. **Cartão sem página lida vira indício na hora.** Ele entra com prazo e órgão, e a leitura da página depois só
   completa o link oficial, pelo mesmo id.

## Escada de rotas: como nenhum bloqueio faz perder oportunidade

| Rota | Quem lê | Quando o site vai para ela |
|---|---|---|
| nuvem | GitHub, respeitando robots.txt, intervalo por site e cache condicional | padrão |
| ponte | IP brasileiro: ponte HTTP na hospedagem, VM no Brasil ou computador do titular | o domínio está em `exige_brasil`, ou deu 2 falhas seguidas de rede ou bloqueio pela nuvem |
| assistida | titular ou Claude no Chrome, com o botão "Capturar indícios" | o robots.txt proíbe robôs, a página só abre com JavaScript, a rota ainda precisa ser levantada, ou 3 bloqueios também pelo IP brasileiro |

**Regras da escada:**

- Toda semana o site tenta de novo a rota mais barata; quando ela volta a funcionar, ele desce. Quem foi para a assistida por robots.txt é reavaliado a cada 30 dias.
- Site que espera a ponte há 3 dias entra também na fila da coleta assistida, para não ficar parado.

**Os sites fechados a robôs (Prosas, FINEP) continuam cobertos por três caminhos:**

1. a **rota indireta**: outro indexador que pode ser lido e publica os mesmos editais, como a página do CapitaAI sobre o Prosas;
2. o **Piloto - Espião**, que recebe um ângulo de busca pelo financiador fora do site fechado (`estado/indexadores/angulos_piloto.json`);
3. a **coleta assistida**: o titular abre o site e o botão grava o que a página mostra.

O robô nunca toca o site fechado.

## Conselho de 7 lentes

| Lente | Quem fala | Ponto central | O que foi exigido e está no código |
|---|---|---|---|
| Extremamente pessimista | Engenheiro-chefe de confiabilidade | Mais fontes, mais quebras silenciosas. Site mudo sem aviso foi o defeito dos motores 01, 02 e 22. | Cada família grava o seu diário (calendário e luz no painel). Site que falha sobe na escada, e falha nunca vira "funcionou". |
| Pessimista | Staff engineer de dados | O mesmo edital aparece no Farol, no CapitaAI e na rede Mapas Culturais com títulos diferentes. | Chave dupla de duplicata: link oficial canônico, ou título + prazo + UF. Um indício só, com várias fontes. |
| Levemente pessimista | Professor de sistemas distribuídos | Três escritores no mesmo arquivo: nuvem, computador do titular e envio da coleta assistida. | A rodada gera um delta e o reaplica sobre o main mais recente antes do push, para não apagar o que outro gravou. |
| Neutro | CTO | Decide (abaixo). | — |
| Levemente otimista | Professor de recuperação de informação | Farol, Mapas Culturais, WordPress e CapitaAI entregam dados estruturados (API, JSON-LD, sitemap com data). | Leitores estruturados primeiro; a raspagem de HTML fica só onde não há alternativa. |
| Otimista | Staff engineer de produto | Bloqueio não precisa ser perda: há rota indireta, Piloto e navegador. | Fila assistida no painel, botão de captura, ângulos do Piloto, roteiro para o Claude no Chrome. |
| Extremamente otimista | Chief engineer de plataforma | Site novo deve ser uma linha de configuração. | O catálogo JSON tem a metodologia e os parâmetros de cada site; o leitor é escolhido pelo campo `leitor`. |

### Voto do neutro

1. **Aprovado.** São 7 famílias, um motor por site e indícios no fluxo com o mesmo contrato do motor antigo.
2. **Licença.** Nenhum site com robots.txt fechado é lido por robô. A leitura segue a RFC 9309: os grupos de `*` se
   somam e vale a regra mais longa. Isso corrige o leitor-padrão do Python, que lê só o primeiro grupo e liberaria o
   Prosas.
3. **O que se guarda.** Só o fato: título, financiador, prazo, valor, UF, link oficial e um resumo de até 300
   caracteres. O texto curado do agregador não é copiado (Lei 9.610/1998, art. 7º, XIII; os atos oficiais estão fora
   da proteção pelo art. 8º, IV).
4. **Fora do fluxo, mas guardado no acervo.** Fica de fora o que tem prazo vencido, público claramente fora do perfil
   de OSC (bolsa de doutorado, só empresa, só prefeitura), quarentena, chamada estrangeira que não se aplica ao Brasil
   e indício sem prazo publicado há mais de 60 dias. O limite é de 1.000 indícios no fluxo, com Goiás primeiro, depois
   Brasil e prazo mais próximo.

| Parâmetro | Meta | Onde se mede |
|---|---|---|
| Link oficial | 85% ou mais dos indícios no fluxo | `por_fonte.com_link_oficial` em `estado/agregadores/itens.json` |
| Duplicata | um indício por edital | `fontes` de cada indício; o painel mostra quantas fontes o viram |
| Silêncio | nenhuma família vermelha por 2 dias | diário de cada família no painel |
| Bloqueio | todo site bloqueado com rota (ponte ou assistida) em até 1 dia | `docs/dados/indexadores.json` → `sites[].rota` |
| Volume do fluxo | o mapa continua gerado em menos de 300 s | passo "mapa" do fluxo 16 |

## Riscos e mitigação

| Risco | Mitigação |
|---|---|
| O volume cresce (de 62 para até 1.000 indícios) e pesa no mapa e no Interceptador | Limite configurável (`limites.indicios_no_fluxo_max`), ordem Goiás → Brasil → prazo. O mapa foi medido em 12 s com os dados atuais. |
| A ponte HTTP em datacenter também é bloqueada | O site sobe para a coleta assistida; o computador do titular continua sendo o IP residencial. |
| Ponte usada como proxy aberto | Pedido assinado com HMAC e válido por 5 minutos; lista de domínios; só destino público; 120 pedidos por minuto. |
| Mudança de layout num site | Os leitores estruturados (API, JSON-LD, sitemap) quebram menos. A falha aparece no painel e sobe na escada. |
| Validações já feitas se perdem | O id do indício é o mesmo do motor antigo (sha1 da página do agregador). Os itens antigos foram migrados com a data em que apareceram. |

## Pendências

1. **Rotas a levantar no navegador:**
   - Petrobras e Fundação Banco do Brasil;
   - Embaixadas: Japão, Canadá, Alemanha, Austrália, Reino Unido, Países Baixos e Noruega.
2. **Colunas do Siconv.** Confirmar na primeira leitura real os nomes das colunas de `siconv_programa.zip`. O leitor
   reconhece as colunas pelo nome e, se não reconhecer, grava a lista de cabeçalhos no diagnóstico.
3. **Ponte Brasil.** Escolher um dos três jeitos (`ponte/LEIA-ME.md`).
4. **Prosas.** Pedido de licença escrita: se vier, o leitor de API (JSON:API do widget) entra na rota nuvem com
   intervalo de 30 s.
