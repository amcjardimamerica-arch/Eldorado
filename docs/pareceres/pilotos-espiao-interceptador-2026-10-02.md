# Parecer do conselho — Piloto - Espião e Piloto - Interceptador

**Data:** 02/10/2026. **Período analisado:** 01/10 e 02/10, desde a implantação da esteira de selos (02/10, 13h20 UTC),
com o acumulado dos pilotos.

## 1. Síntese

Os dois pilotos voam o dia inteiro (cerca de 90 voos do Espião e 40 a 85 do Interceptador por dia), mas rendem pouco:

- **Espião:** com o crivo, ficam de 6 a 9 achados por dia, e quase todas as avaliações terminam em "nada no crivo".
- **Interceptador:** em 131 voos, só 1 edital saiu "validado" e 38 saíram "parciais".

A trava que o titular viu é real e tem nome. No servidor do GitHub (IP de datacenter nos EUA), o DuckDuckGo entrega
**2 buscas por máquina** e bloqueia. O resto do voo ia para o Google Notícias, que traz notícia e não o site oficial. Isso
gerou três efeitos em cadeia:

1. o Interceptador escolhia página oficial de outro estado;
2. o Interceptador não conseguia abrir os sites das prefeituras, que recusam o IP;
3. o Espião repetia as mesmas consultas.

**Decisão:** os pilotos podem, sim, voar com IP brasileiro, sem custo. Os caminhos são o computador do titular, quando
ligado, e uma VM gratuita no Brasil, 24 horas. Funciona assim:

- os pilotos usam o mesmo código e o mesmo modelo local (Qwen3-8B), sem API paga;
- a nuvem passa a conferir quem está voando e fica em terra enquanto o Brasil voa;
- se o Brasil parar, a nuvem reassume sozinha.

Junto vieram as correções da busca, do território e da continuidade.

## 2. Resultados desde a última implantação

### Piloto - Interceptador (01–02/10, 131 voos)

| Medida | Valor |
|---|---|
| Qualidade | 92 insuficientes, 38 parciais, 1 validada |
| "Nenhuma fonte legível" (o site não abriu) | 18 |
| "O modelo não devolveu JSON" | 8 |
| Sem página oficial | 61 |
| Página oficial **de outro estado ou município** | 13 de 70 (19%) |
| Tempo médio por voo | ~650 s |
| Acumulado (728 alvos) | 348 insuficientes, 221 parciais, 34 validadas, 6 fontes confirmadas, 80 dossiês de empresa |
| Mapa no último pouso | 23 confirmadas, 652 possíveis |

**Casos reais de página errada:**

| Alvo | Página escolhida |
|---|---|
| Cachoeira Alta (GO) | `cachoeirapaulista.sp.gov.br` |
| Anápolis | `transparencia.ipiau.ba.gov.br` |
| Nova Iguaçu de Goiás | o edital do FUNDEB da SME de **Goiânia** |
| Serra Dourada | Secretaria de Esportes de **São Paulo** (três vezes) |

E a página errada ficava presa: a rodada seguinte a reaproveitava como "de rodada anterior".

### Piloto - Espião (29/09–02/10)

| Medida | Valor |
|---|---|
| Voos por dia | 85 a 101 |
| Missões por relatório | 7 (aposta, descobrir) |
| Achados / abates por dia | 6 a 9 |
| Avaliações | quase todas "nada no crivo" |
| Vias de busca | só o DuckDuckGo: 46 usos, 3 bloqueios registrados, mais o corte silencioso depois de 2 por voo |
| Consulta mais repetida | "financiamento de projetos voluntariado osc 2026 inscrições abertas": **241 vezes**, 3 com resultado |
| Consultas ruins repetidas | 93, 86 e 83 vezes |

## 3. Diagnóstico — por que trava

| # | Defeito | Efeito |
|---|---|---|
| 1 | O DuckDuckGo corta o IP do GitHub na 2ª busca (medido em 01/10: 8, 8, 0, 0, 0 resultados) | O voo segue pelo Google Notícias: notícia, não site oficial |
| 2 | Com a cota do DuckDuckGo esgotada, o código ia **direto** ao Google Notícias, sem tentar as vias por API (Brave, Google) | Mesmo com a chave gravada, ela nunca seria usada |
| 3 | O Interceptador nem recebia as chaves de busca (só o Espião tinha os segredos no fluxo) | Idem |
| 4 | Prefeituras de Goiás e o TJGO recusam IP estrangeiro | "Nenhuma fonte legível" (18 em 2 dias) |
| 5 | Validação da página oficial sem território | 13 páginas de outro estado ou município |
| 6 | Página de "rodada anterior" reusada sem conferência | O erro fica para sempre |
| 7 | Falha de rede contada como resultado ("insuficiente") | O alvo não volta para nova tentativa |
| 8 | O Espião repete a mesma consulta voo após voo | As 2 buscas boas são gastas no que já sabia |

## 4. Os pilotos podem usar o acesso local do titular?

**Podem, e é o melhor caminho para a busca.** O IP residencial não é tratado como robô de datacenter e abre os sites
de Goiás.

O sistema já tinha a coleta no computador (`scripts/coleta_brasil.py`) e um Interceptador local, que usa API paga.
Agora há `scripts/pilotos_brasil.py`, que roda os **dois** pilotos com o **modelo local gratuito**:

- até 30 buscas por voo no DuckDuckGo, com 6 s entre elas;
- os sites que recusavam a nuvem abrem;
- os alvos que a nuvem não conseguiu são retentados aqui primeiro.

**Por que não o Chrome do titular como base.** O Claude no Chrome serve para casos difíceis: páginas com JavaScript ou
CAPTCHA, que não se contorna, e a coleta assistida. Mas depende de alguém com o navegador aberto e não roda sozinho 24
horas. Ficou como reforço, não como base.

## 5. Possibilidades 24 h, sem custo ou de baixo custo

| Opção | Custo | Horas | O que resolve | Limites |
|---|---|---|---|---|
| **A. VM gratuita no Brasil** (Oracle Cloud Always Free, São Paulo ou Vinhedo; 4 núcleos ARM e 24 GB) | R$ 0 | 24 h | Os dois pilotos com o Qwen3-8B e IP brasileiro; sites de Goiás abrem; busca melhor que a do GitHub | A conta pede cartão só para verificação. Às vezes falta capacidade ARM na região (tentar de novo). O IP ainda é de datacenter, então o DuckDuckGo pode limitar, e as reservas cobrem. |
| **B. Computador do titular** | R$ 0 | enquanto ligado | Melhor IP para busca (residencial) | Para quando o computador desliga; a nuvem reassume |
| **C. Chaves gratuitas de busca** (Google Programmable Search; Brave Search API) | R$ 0 no plano gratuito | 24 h, na própria nuvem | Busca de verdade sem bloqueio, dentro da cota diária ou mensal | Limite de consultas; conferir o plano gratuito vigente ao criar a chave. O código já usa a chave primeiro, assim que existir. |
| **D. Ponte na Hostgator** (`ponte/ponte.php`) | o que já paga | 24 h | IP brasileiro para **ler** sites que recusam o exterior e uma pequena cota extra de buscas | IP compartilhado e de datacenter; não roda modelo |
| E. Navegador do titular (Claude no Chrome / coleta assistida) | R$ 0 | sob demanda | Páginas com JavaScript, casos pontuais | Não é automático |
| F. Outras VMs grátis (GCP e2-micro, AWS 12 meses) | R$ 0 | 24 h | — | Sem região Brasil grátis no GCP; a AWS grátis tem 1 GB de memória, que não roda o modelo |

**Recomendação do conselho:** A + B + C juntas.

- **A** é a base 24 h.
- **B** é o reforço residencial enquanto o computador está ligado.
- **C** dá busca confiável inclusive quando a nuvem precisa reassumir.
- **D** só se o titular quiser leitura 24 h por IP brasileiro sem a VM.

O código já troca entre elas sozinho.

## 6. O que foi feito (código)

1. **Busca que não trava** (`src/piloto_busca.py`):
   - cache de 24 h por consulta (6 h se vazia), só no voo real;
   - esgotado o DuckDuckGo, a ordem é: **API com chave → ponte Brasil → Google Notícias**;
   - no Brasil (`ELDORADO_LOCAL_BR=1`), cota de 30 buscas por voo, com 6 s de intervalo.
2. **Território** (`src/sites_oficiais.py`):
   - a UF e o município esperados saem do registro ou do título;
   - página `.xx.gov.br` de outro estado é recusada;
   - página municipal que não é do município esperado nem o cita é recusada;
   - nova **rota municipal**: procura o edital dentro do site da prefeitura (catálogo das 25 maiores ou
     `<município>.go.gov.br`), pelo mapa do site, sem buscador;
   - a página de rodada anterior também passa pelo território.
3. **Continuidade** (`src/interceptador.py`):
   - "fonte ilegível" e "busca sem resultado" viram **retentativa**, até 3;
   - no Brasil, a retentativa vem antes de tudo;
   - na nuvem, só a de busca, depois de 3 dias.
4. **Sede dos pilotos** (`src/pilotos_sede.py`, `config/pilotos_sede.json`):
   - o batimento do Brasil vai em `estado/sede_pilotos.json`;
   - a nuvem confere no início de cada voo (job `sede`) e fica em terra enquanto o batimento estiver fresco (45 min);
   - parou o batimento, ela reassume. O Interceptador confere de hora em hora; o Espião, a cada 2 h (a corrente
     encadeada religa antes);
   - o estado do Interceptador passa a ser **mesclado**, por alvo vence o mais recente, em vez de apagado e copiado.
5. **Execução no Brasil:**
   - `scripts/pilotos_brasil.py`: clone próprio, sobe o llama.cpp e alterna os pilotos, gravando cada voo mesclado;
   - `scripts/agendar_pilotos_brasil.ps1/.bat`: de hora em hora no Windows;
   - `scripts/instalar_vm_pilotos.sh`: compila o llama.cpp, baixa o Qwen3-8B e cria o cron de hora em hora na VM.
6. **Chaves de busca no Interceptador:** os segredos `BRAVE_SEARCH_KEY`, `GOOGLE_CSE_KEY` e `GOOGLE_CSE_CX` passaram a
   chegar também ao Interceptador, mais a ponte.

## 7. Conselho de 7 lentes

| Lente | Quem fala | Ponto central | O que ficou no código |
|---|---|---|---|
| Extremamente pessimista | Engenheiro-chefe de confiabilidade | Dois pilotos gravando o mesmo estado: um apaga o outro. E se o Brasil cair, ninguém voa. | Mescla por alvo; batimento de 45 min; a nuvem reassume sozinha. |
| Pessimista | Staff engineer de dados | 19% das páginas oficiais eram de outro território, e o erro ficava preso. | Validação territorial, inclusive da página guardada; rota municipal sem buscador. |
| Levemente pessimista | Professor de redes | IP de datacenter brasileiro (Oracle) também pode ser limitado pelo buscador. | Ordem de reservas (API, ponte, notícias); computador residencial como reforço. |
| Neutro | CTO | Decide (abaixo). | — |
| Levemente otimista | Professor de recuperação de informação | Metade das buscas é repetida; cache e consulta dentro do site oficial poupam a cota. | Cache de 24 h; busca no mapa do site. |
| Otimista | Staff engineer de produto | Falha de rede não é resultado: o alvo deve voltar. | Retentativa com causa, até 3, com o Brasil primeiro. |
| Extremamente otimista | Chief engineer de plataforma | Uma VM grátis de 24 GB roda o mesmo modelo 24 h; o GitHub vira reserva. | Instalador da VM e sede automática. |

### Voto do neutro

1. **Aprovado.** Sede automática: o Brasil é a sede preferida e a nuvem é a reserva.
2. **Nada pago.** O modelo é o mesmo Qwen3-8B local. O Interceptador local com API paga continua opcional, como já era.
3. **Licença e respeito às fontes:**
   - não se contorna CAPTCHA nem login;
   - o intervalo entre buscas é mantido;
   - o cache reduz a carga sobre os buscadores.

| Parâmetro | Meta | Onde se mede |
|---|---|---|
| Buscas úteis por voo | ≥ 10 no Brasil; ≥ 2 + reservas na nuvem | `estado/piloto/vias.json`, `cache_buscas.json` |
| Página de outro território | 0 | `busca_do_oficial.tentativas` / `paginas_recusadas` |
| "Fonte ilegível" sem retentativa | 0 | `feitos[*].retentar` |
| Voo sem sede | nenhum período de 2 h sem voar | `estado/sede_pilotos.json` e as rodadas |
| Validadas + parciais | dobrar em 7 dias com a VM | relatórios diários do Interceptador |

## 8. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| A VM gratuita sem capacidade ARM na hora de criar | Tentar outra região do Brasil (São Paulo/Vinhedo). O computador do titular e as chaves cobrem enquanto isso. |
| O computador lento para o Qwen3-8B (precisa de cerca de 6 GB livres) | O voo demora mais, mas não quebra. O titular pode deixar só o Espião (`--pilotos espiao`). |
| Conflito de git entre Brasil e nuvem | Clone próprio, volta ao main a cada voo, mescla do Interceptador e 5 tentativas de envio. |
| Cota das chaves gratuitas | As chaves entram só quando o DuckDuckGo esgota, e o cache poupa consultas. |

## 9. Pendências e decisões do titular

1. **Escolher as opções** A, B e C (recomendado) e criar:
   - a conta da VM;
   - as chaves gratuitas.

   São cadastros pessoais: senha e cartão passam só pelo titular, nunca pelo chat.
2. **Instalar no computador:** agendamento `scripts/agendar_pilotos_brasil.bat` e a IA local. Pode ser feito pela
   conversa do Claude no aplicativo de desktop.
3. **Primeira semana:** comparar validadas e parciais por dia antes e depois da sede no Brasil.
