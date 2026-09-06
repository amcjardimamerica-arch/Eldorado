# Motores bloqueados — causa exata por domínio (estado em 06/09/2026, 28 saídas do robô)

| Domínio | Falhas | Erro registrado | Causa exata | Solução |
|---|---|---|---|---|
| www.in.gov.br (DOU) | 28 | 24× HTTP 4xx, 4× conexão derrubada | recusa de agente automatizado (WAF); a home responde, a busca por querystring cai | resolvido em parte com identificação de navegador; a leitura do JSON da Seção 3 funciona (368 matérias/dia) — os 4xx são das páginas de busca, dispensáveis |
| www.tjgo.jus.br | 23 | HTTP 403 em TODAS as rotas (home, DJE, licitações, chamamentos) | 403 sem WAF identificado: **bloqueio de IP de datacenter/estrangeiro** — padrão típico dos tribunais | só resolve com saída pelo Brasil (túnel WireGuard ou runner próprio) ou espelho (DJEN/Jusbrasil) |
| www.goiania.go.leg.br (Câmara) | 10 | 5× 403, 5× timeout | filtro de rede que derruba/atrasa IP estrangeiro; a home entrega 0 links (conteúdo por script) | saída pelo Brasil + navegador sem tela (Playwright) para o script |
| diariooficial.goiania.go.gov.br | 9 | gaierror (DNS) | **endereço não existe** — subdomínio errado na configuração | corrigido: a listagem real fica em www.goiania.go.gov.br/diario-oficial (edições em PDF por script) |
| www.goiania.go.gov.br | 7 | 5× 403, 2× timeout | filtro de IP estrangeiro nas páginas internas; a home responde | saída pelo Brasil |
| www.cnj.jus.br | 6 | HTTP 403 (páginas internas) | WAF do CNJ em rotas profundas; a home responde (3.473 links) | ler só a home + destinações via DJEN |
| www.goias.gov.br | 6 | HTTP 403 | filtro de IP estrangeiro nas páginas de secretaria (goias.gov.br/cultura responde) | saída pelo Brasil; usar os subdomínios que respondem |
| gife.org.br | 6 | HTTP 403 nas páginas de editais | WAF (site em WordPress com proteção) | identificação de navegador já aplicada; se persistir, RSS do site |
| sapl.goiania.go.leg.br | 6 | URLError | subdomínio do SAPL não responde/não existe para Goiânia | remover; usar o portal de proposições que a Câmara publicar |
| pncp.gov.br (API) | 5 | 2× URLError, 2× timeout, 1× HTTP | API oscila e limita taxa; funciona na maioria das horas (20 chamamentos/dia lidos) | manter; tentativa com 30 s e retentativa na hora seguinte |
| diariooficial.abc.go.gov.br (DO-GO) | 4 | HTTP 4xx nas listagens | as páginas de listagem só existem para navegador; a home responde | edições em PDF por script → extração de edições (fase 2) |
| www.filantropia.ong | 4 | HTTP 403 | WAF total | motor removido |
| www.mpgo.mp.br | 4 | URLError | conexão recusada ao IP estrangeiro | saída pelo Brasil |

Regra geral: 403 **com** cabeçalho de WAF = bloqueio a robô (identificação de navegador ajuda); 403 **sem** WAF ou conexão recusada = filtro de IP estrangeiro
(só a saída pelo Brasil resolve); gaierror = endereço errado (corrigir); 200 com 0 links = conteúdo por script (navegador sem tela).
A partir desta saída o robô grava, para cada falha, o código HTTP, o WAF identificado e a causa — visível no diagnóstico de cada motor.

## Saída pelo Brasil — como ligar

Opção A (túnel): num servidor seu no Brasil (VPS em São Paulo, ~R$ 30/mês, ou um computador ligado), instale WireGuard como servidor;
crie um cliente e cole o arquivo .conf do cliente no segredo do repositório **WG_CONFIG_BR**. O robô ativa o túnel no início de cada
saída e passa a sair pelo seu IP brasileiro (estado/saida_brasil.txt registra o IP de saída).
Opção B (runner próprio): Settings → Actions → Runners → New self-hosted runner, no seu computador/VPS; o robô roda inteiro no Brasil.
