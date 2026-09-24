# Auditoria de afiação dos motores — 24/09/2026

## 1. O que realmente travou a busca nos últimos 20 dias

**Os motores não estavam falhando: estavam sendo impedidos de começar.** O workflow dos motores roda a suíte
de testes antes da coleta e, com qualquer falha, nenhum motor roda. Nos 20 dias até hoje, o horário das 09h UTC
teve 17 execuções e 16 falharam; o das 08h, 13 de 13 — todas no passo "Testes antes da coleta". Os blocos da
madrugada (diários, justiça, plataformas) rodaram em 4 dos 20 dias.

Seis testes seguravam o portão — dois quebrados por mim (um import de `yaml` e a regra do `piloto.json` que
reescrevi ao empossar o Qwen3), os outros por data fixa apodrecida, arquivo gerado fora do git, motor novo sem
finalidade declarada e um teste do DOU que dependia de rede sem saber. **Todos corrigidos**, e o portão foi
redesenhado: **só teste crítico bloqueia a coleta** — privacidade, segredo, injeção de prompt, data inventada. O
resto vira aviso registrado em `estado/ultimo_teste_ci.txt`, e os motores rodam.

Consequência para a leitura dos números: a "linha de busca de 20 dias" é, na prática, **uma linha de 4 a 13 dias
efetivos por bloco**. Motores julgados lentos ou secos estavam, em boa parte, simplesmente sem rodar.

## 2. Correções implantadas hoje

- **Veto geral de 12 para 37 termos**, tirados das famílias que responderam por 344 dos 409 descartes: serviço ao
  órgão (174), compra pública (69), imóvel e uso de espaço (23), instituição financeira (13), parecerista (12),
  cachê (10) e resultado ou extrato de parceria já julgada (19). O veto age no **rótulo do link**, antes de abrir
  a página: descarta sem gastar leitura — e não toca o corpo de um edital aberto que cite "resultado final" no
  cronograma.
- **Um leitor só para o Diário Oficial de Goiás.** `plat-ovg`, `plat-fapeg`, `plat-fundos-estaduais-go` e
  `plat-secult-go` deixaram de ler `diariooficial.abc.go.gov.br`; o `do-goias` lê e recebeu os termos próprios de
  cada um. As páginas próprias deles em `goias.gov.br` continuam — aquilo não era duplicata.
- **Finalidade declarada** para os quatro motores que não tinham; **cadência coerente** do `cnj-destinacoes` (30 dias).
- **Descrição interna de cada motor** no painel — objetivo, como funciona, onde para hoje, o que fazer e uma
  evolução gratuita —, visível só com o mouse parado sobre o quadro, na Bússola.

## 3. Motor a motor: o que fazer e como evoluir de graça

| motor | decisão | onde para hoje | o que fazer | evolução gratuita |
|---|---|---|---|---|
| `pncp-api` | **AFINAR FILTRO** | triagem — 433 de 587 registros eliminados (74%) | traz volume, mas quase tudo é ruído | filtrar NA CONSULTA da API oficial do PNCP (uf=GO e modalidade), em vez de baixar tudo e descartar depois: o credenciamento é barrado antes de chegar |
| `camara-goiania-pl` | **COLETA LOCAL** | leitura — a nuvem é recusada; a coleta desta fonte é local | a fonte recusa endereço de fora do país; o que a nuvem lê é a página de recusa — só rende pelo computador do titular | verificar se a Câmara usa o SAPL (Interlegis), que expõe API aberta de proposições |
| `dj-trf1-go` | **COLETA LOCAL** | leitura — a nuvem é recusada; a coleta desta fonte é local | a fonte recusa endereço de fora do país; o que a nuvem lê é a página de recusa — só rende pelo computador do titular | testar a API do DJEN/CNJ, que concentra os diários da Justiça Federal |
| `dje-tjgo` | **COLETA LOCAL** | leitura — a nuvem é recusada; a coleta desta fonte é local | a fonte recusa endereço de fora do país; o que a nuvem lê é a página de recusa — só rende pelo computador do titular | testar a API do Diário de Justiça Eletrônico Nacional (DJEN/CNJ), que publica os atos dos tribunais fora do WAF do TJGO |
| `do-goiania` | **COLETA LOCAL** | leitura — a nuvem é recusada; a coleta desta fonte é local | a fonte recusa endereço de fora do país; o que a nuvem lê é a página de recusa — só rende pelo computador do titular | verificar a cobertura de Goiânia no Querido Diário (API aberta da Open Knowledge Brasil); se houver, dispensa a coleta local |
| `alego-pl` | **INSUMO** | chega à biblioteca — 1 de 1 ativos | não busca oportunidade: alimenta o sistema com emenda parlamentar; não se mede por achado | dados abertos da ALEGO para proposições e leis de utilidade pública, em vez de raspar páginas |
| `cnj-destinacoes` | **INSUMO** | léxico — lê as páginas e nada casa com os termos — nenhum achado no mês | cadência alinhada a 30 dias: referência normativa não muda por semana | trocar raspagem por feed RSS ou API aberta da própria fonte, quando existir |
| `do-goias` | **MANTER** | chega à biblioteca — 9 de 9 ativos | recebe 6 termo(s) de plat-ovg: credenciamento de entidades, entidades parceiras, Mais Social, edital de apoio…; recebe 5 termo(s) de plat-fapeg: chamada pública, extensão, inovação social, popularização da ciência… | ler o PDF da edição completa, não só o índice — o ato está dentro; e ser o único leitor do Diário para os motores estaduais |
| `dou` | **MANTER** | chega à biblioteca — 3 de 3 ativos | produz e o que produz sobrevive à triagem | Ro-DOU (robô de código aberto do governo federal que busca termos no DOU) ou INLABS da Imprensa Nacional (XML integral da edição, gratuito com cadastro) |
| `plat-fundos-estaduais-go` | **MANTER** | captura sem ficha — 6 achado(s) sem ficha na Biblioteca | deixa de ler o Diário Oficial de Goiás (1 rota): quem lê é o do-goias | ler o feed RSS da plataforma (sites WordPress publicam /feed/ de graça): mais leve que raspar e não bloqueia |
| `plat-goias-social` | **MANTER** | chega à biblioteca — 6 de 6 ativos | produz e o que produz sobrevive à triagem | ler o feed RSS da plataforma (sites WordPress publicam /feed/ de graça): mais leve que raspar e não bloqueia |
| `plat-mp-destinacoes-reparacao` | **MANTER** | chega à biblioteca — 2 de 2 ativos | produz e o que produz sobrevive à triagem | ler o feed RSS da plataforma (sites WordPress publicam /feed/ de graça): mais leve que raspar e não bloqueia |
| `plat-ovg` | **MANTER** | captura sem ficha — 6 achado(s) sem ficha na Biblioteca | deixa de ler o Diário Oficial de Goiás (1 rota): quem lê é o do-goias | ler o feed RSS da plataforma (sites WordPress publicam /feed/ de graça): mais leve que raspar e não bloqueia |
| `plat-salic` | **MANTER** | chega à biblioteca — 5 de 5 ativos | produz e o que produz sobrevive à triagem | API pública do SALIC: projetos aprovados e INCENTIVADORES com valores — serve também à lista de empresas |
| `plat-secult-go` | **MANTER** | chega à biblioteca — 7 de 9 ativos | deixa de ler o Diário Oficial de Goiás (1 rota): quem lê é o do-goias | ler o feed RSS da plataforma (sites WordPress publicam /feed/ de graça): mais leve que raspar e não bloqueia |
| `plat-sindico-aberto` | **MANTER** | chega à biblioteca — 12 de 12 ativos | produz e o que produz sobrevive à triagem | ler o feed RSS da plataforma (sites WordPress publicam /feed/ de graça): mais leve que raspar e não bloqueia |
| `recorrencia` | **MANTER** | chega à biblioteca — 2 de 2 ativos | produz e o que produz sobrevive à triagem | trocar raspagem por feed RSS ou API aberta da própria fonte, quando existir |
| `motor-gife` | **MEDIR** | sem medição — o motor não tem auditoria nem validação: nunca foi medido como os outros | entrou no sistema depois da auditoria; sem número não há como julgar | API do SALIC (incentivadores por empresa, com valores e anos) + dados abertos de CNPJ da Receita: histórico real de destinação |
| `motor-patrocinio` | **MEDIR** | sem medição — o motor não tem auditoria nem validação: nunca foi medido como os outros | entrou no sistema depois da auditoria; sem número não há como julgar | alertas gratuitos em RSS (Google Alertas) para 'patrocínio' + Goiânia/Goiás: a imprensa avisa quando uma empresa patrocina |
| `sindico-aberto` | **MEDIR** | sem medição — o motor não tem auditoria nem validação: nunca foi medido como os outros | entrou no sistema depois da auditoria; sem número não há como julgar | feeds RSS das entidades e da imprensa do terceiro setor, em vez de busca genérica bloqueada |
| `plat-cnpq-extensao` | **OBSERVAR** | léxico — lê as páginas e nada casa com os termos — nenhum achado no mês | só 3 execução(ões) desde que nasceu — amostra curta demais para julgar o léxico | ler o feed RSS da plataforma (sites WordPress publicam /feed/ de graça): mais leve que raspar e não bloqueia |
| `plat-empresas-editais-incentivados` | **OBSERVAR** | léxico — lê as páginas e nada casa com os termos — nenhum achado no mês | só 3 execução(ões) desde que nasceu — amostra curta demais para julgar o léxico | ler o feed RSS da plataforma (sites WordPress publicam /feed/ de graça): mais leve que raspar e não bloqueia |
| `plat-fapeg` | **OBSERVAR** | léxico — lê as páginas e nada casa com os termos — nenhum achado no mês | deixa de ler o Diário Oficial de Goiás (1 rota): quem lê é o do-goias | ler o feed RSS da plataforma (sites WordPress publicam /feed/ de graça): mais leve que raspar e não bloqueia |
| `plat-prefeituras-50-go` | **OBSERVAR** | léxico — lê as páginas e nada casa com os termos — nenhum achado no mês | só 3 execução(ões) desde que nasceu — amostra curta demais para julgar o léxico | ler o feed RSS da plataforma (sites WordPress publicam /feed/ de graça): mais leve que raspar e não bloqueia |
| `plat-prosas` | **OBSERVAR** | léxico — lê as páginas e nada casa com os termos — nenhum achado no mês | só 3 execução(ões) desde que nasceu — amostra curta demais para julgar o léxico | ler o feed RSS da plataforma (sites WordPress publicam /feed/ de graça): mais leve que raspar e não bloqueia |
| `empresas-incentivadas` | **REATIVAR** | agenda — rodou 4 de 20 dias esperados | não está rodando nos dias previstos | cruzar a lista do ICMS de Goiás com os incentivadores do SALIC: quem já destinou por lei sobe na fila |
| `plat-abcr` | **REATIVAR** | agenda — rodou 6 de 20 dias esperados | não está rodando nos dias previstos | ler o feed RSS da plataforma (sites WordPress publicam /feed/ de graça): mais leve que raspar e não bloqueia |
| `plat-gife` | **REATIVAR** | agenda — rodou 6 de 20 dias esperados | não está rodando nos dias previstos | ler o feed RSS da plataforma (sites WordPress publicam /feed/ de graça): mais leve que raspar e não bloqueia |
| `plat-observatorio-3setor` | **REATIVAR** | agenda — rodou 6 de 20 dias esperados | não está rodando nos dias previstos | ler o feed RSS da plataforma (sites WordPress publicam /feed/ de graça): mais leve que raspar e não bloqueia |
| `plat-prosas-premios` | **REATIVAR** | agenda — rodou 6 de 20 dias esperados | não está rodando nos dias previstos | ler o feed RSS da plataforma (sites WordPress publicam /feed/ de graça): mais leve que raspar e não bloqueia |

## 4. Uma única evolução para o sistema inteiro

**Um servidor próprio no Brasil, ligado ao GitHub como executor dos voos e dos motores (runner auto-hospedado).**

É a única mudança que atinge os três pontos de busca ao mesmo tempo:

- **Motores:** o endereço brasileiro libera as fontes que recusam servidor estrangeiro — Diário de Goiânia, TJGO,
  TRF1, Câmara — sem depender do seu computador ligado. (O WAF do TJGO pode continuar recusando endereço de
  datacenter; isso só se confirma na prática.)
- **Piloto:** com máquina própria, o modelo fica carregado entre voos — hoje cada voo baixa 1,1 GB e sobe o servidor
  antes de começar, parte grande de um voo de 2 minutos —, e cabe um modelo maior. Acaba a fila do GitHub que
  cancelou o benchmark duas vezes.
- **Busca:** o servidor pode hospedar um SearXNG (metabuscador de código aberto) como rota própria, somado à chave
  gratuita da Brave.

**Como pagar pouco ou nada — programas com ação social para ONGs.** *Não tenho acesso à internet nesta conversa:
os termos abaixo são os que eu conhecia até meados de 2026 e precisam ser conferidos antes de qualquer cadastro.*

- **Goodstack** (antiga Percent): valida organizações sem fins lucrativos e dá acesso a descontos de empresas
  parceiras. A AMC, com CNPJ de associação, valida-se uma vez e usa a validação em vários programas.
- **TechSoup Brasil**: doações e descontos de software e nuvem para ONGs brasileiras; historicamente, a porta para os
  créditos anuais da **AWS** para organizações sem fins lucrativos (a AWS tem região em São Paulo).
- **Microsoft para ONGs**: historicamente oferecia crédito anual de Azure a organizações elegíveis; o Azure tem região
  em São Paulo (Brazil South), onde caberia o servidor.
- **Oracle Cloud Always Free**: sem ação social, mas **gratuito** — máquina ARM de 4 núcleos e 24 GB de memória, com
  região em São Paulo. Exige cartão no cadastro e costuma ter fila de capacidade.

**Recomendação:** tentar primeiro a via social — validar a AMC na Goodstack e na TechSoup Brasil e pedir crédito de
nuvem com região em São Paulo; em paralelo, a Oracle gratuita como alternativa imediata. Se nenhuma sair, um servidor
pago pequeno em São Paulo custa na faixa de dezenas de reais por mês.

## 5. O conselho

**Extremamente pessimista — chief engineer.** Passamos dias afinando léxico de motores que nem rodavam. Nenhum número
de desempenho vale sem antes conferir se o motor executou.

**Pessimista — staff engineer.** O veto novo sai de 409 descartes de uma só rodada de análise. É boa amostra, mas
regra de exclusão precisa de retorno: se em duas semanas algum edital legítimo aparecer descartado por ela, o termo sai.

**Levemente pessimista — professor de engenharia de software.** Portão que bloqueia produção por teste de texto de
painel é defeito de desenho. Corrigido, o risco vira o oposto: aviso que ninguém lê. `estado/ultimo_teste_ci.txt`
precisa ser olhado.

**Neutro — CTO (ponderador).** Ordem de execução: (1) confirmar nos próximos dias que os blocos da madrugada voltaram
a rodar — sem isso nada mais importa; (2) medir o efeito do veto no PNCP, com meta de cair de 74% para menos de 40% de
descarte; (3) aplicar as evoluções gratuitas começando pelas de maior alcance — filtro na consulta do PNCP e API do
SALIC para empresas; (4) buscar o servidor no Brasil pela via social.

**Levemente otimista — professor de ciência da computação.** Metade das evoluções gratuitas troca raspagem por API
oficial ou feed: menos bloqueio, menos quebra por mudança de layout, dado mais limpo.

**Otimista — staff engineer.** A API do SALIC responde de uma vez uma pergunta que o sistema tenta responder por três
motores: quem já destinou por lei de incentivo, quanto e em que ano.

**Extremamente otimista — CTO.** Com os motores rodando todo dia pela primeira vez em semanas, o próximo relatório vai
medir o sistema de verdade — e é provável que muitos motores "secos" deixem de ser.
