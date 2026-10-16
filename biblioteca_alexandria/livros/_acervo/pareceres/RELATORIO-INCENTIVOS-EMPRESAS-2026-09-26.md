# Incentivos fiscais das empresas da Biblioteca de Alexandria — verificação de 26/09/2026

**Pedido do titular:** analisar todas as empresas da Biblioteca de Alexandria e atualizar se destinaram recursos pela Rouanet, FIA, Esporte, Idoso, PRONON, PRONAS, Goyazes e PAT, usando o acesso local da máquina.

**Resultado em uma frase:** o que as fontes oficiais permitem afirmar está gravado, empresa por empresa, com valor, ano e fonte; o que não existe publicamente saiu nulo, com o motivo e o caminho para obter.

Nenhuma senha foi necessária. As consultas foram feitas pelo navegador do seu computador, em páginas e dados abertos dos órgãos.

---

## 1. O que havia antes

- O campo "destinações dos últimos 5 anos" estava **vazio em todas as empresas**.
- Os 40 arquivos de consulta ao SALIC gravavam só "falha". O Ministério da Cultura mudou o endereço da API (de `/v1/` para `/api/v1/`) e o sistema continuava batendo na porta antiga.
- O painel mostrava etiquetas como "Rouanet", "FIA", "LIE" em cada empresa. **Eram hipóteses de conhecimento público**, e o próprio ranking as chamava de "a confirmar". O painel não avisava — quem lia a etiqueta lia fato.
- **Quatro CNPJs do ranking eram de outra empresa**: a "Vale" era uma fábrica de fertilizantes (Fertigran); a "Stone" era a Bridgestone; o "Fleury" não existia em nenhum cadastro; a "Nestlé" era uma subsidiária do Nordeste.
- **Três registros nem eram empresa**: "de janeiro de 2026" (pedaço de cabeçalho de PDF lido como nome, na posição 28 do ICMS), "WhatsApp Agenda Grupo" (trecho de notícia) e "Diário de Goiás" (o jornal que publicou a notícia, gravado como patrocinador).

## 2. Mecanismo por mecanismo

Foram verificadas **99 empresas com CNPJ** — todas as que estão hoje na biblioteca, incluindo as que ganharam CNPJ nesta rodada. Outras 33 são marcas de grupo, entidades isentas ou nomes sem CNPJ em fonte oficial (shoppings, veículos de comunicação, construtoras locais), e ficaram registradas com o motivo.

| Mecanismo | Situação | Fonte |
|---|---|---|
| **Rouanet** | **Lido.** 86 empresas destinaram; 64 dentro da janela de 5 anos (desde 2021); 13 nunca constaram como incentivadoras | SALIC — Ministério da Cultura (API e SalicComparar) |
| **Goyazes** | **Lido.** 5 empresas da base destinaram ICMS em 2024–2026 — e **87 empresas novas** que destinam pelo Goyazes e não estavam na biblioteca | Secult-GO — planilhas de créditos concedidos por empresa |
| **PAT** | **Lido.** 90 empresas inscritas (87 pelo CNPJ exato, 3 por estabelecimento), 7 só com inscrição inativa, 2 sem inscrição | MTE — relação de beneficiárias até 31/03/2026 |
| **Esporte (LIE)** | **Bloqueado.** A página do Ministério do Esporte responde "Conteúdo restrito" por causa do defeso eleitoral | Retomar a partir de **26/10/2026** |
| **FIA** | **Sem fonte pública por empresa.** | Caminho: pedido pela Lei de Acesso à Informação ao CMDCA de Goiânia e ao CEDCA-GO |
| **Fundo do Idoso** | **Sem fonte pública por empresa.** | Caminho: pedido aos conselhos municipal e estadual da pessoa idosa |
| **PRONON / PRONAS** | **Sem fonte pública por empresa.** O Ministério da Saúde publica projetos, não doadores | Caminho: prestação de contas da instituição que recebeu, ou pedido ao ministério |

**Leitura importante:** doação à Rouanet **prova** que a empresa estava no Lucro Real naquele ano (só essa empresa pode deduzir — Lei 8.313/1991, art. 26). Com isso, **64 empresas passaram a ter Lucro Real confirmado**. A inscrição no PAT **não prova** — a empresa do Lucro Presumido também pode se inscrever; é indício, e foi registrado assim.

## 3. O que interessa à A.M.C. primeiro

O Goyazes é o incentivo ao alcance de uma entidade de Goiânia: ICMS de Goiás, empresa de Goiás, projeto em Goiás. Quem já destina por ele:

**Da base atual:**
- **Equatorial Goiás** — 69 projetos em 2024–2026, cerca de R$ 22 milhões em projetos aprovados;
- **Laticínios Bela Vista** — 35 projetos, cerca de R$ 15,8 milhões;
- **Refrescos Bandeirantes** — 3 projetos, e também a maior doadora goiana da Rouanet recente (R$ 3,76 milhões desde 2023);
- **TIM** e **Caramuru** — 1 projeto cada em 2024.

**Novas, que não estavam na biblioteca** (as de maior volume): Leve Alimentos (R$ 9,4 mi), Catral Refrigeração (R$ 4,6 mi), CHESP — Companhia Hidroelétrica São Patrício (R$ 4,5 mi), Harmonia Musical (R$ 3,8 mi), Papelaria Tributária (R$ 3,5 mi), Via Nut (R$ 2,5 mi), Milhão Ingredientes (R$ 2,0 mi), Arte Trigo (R$ 2,0 mi), Complem (R$ 1,8 mi), Lactosul (R$ 1,8 mi). A lista completa das 87 está na base, sem CNPJ — a planilha da Secult traz só o nome. O próximo passo de cada uma é obter o CNPJ.

**Empresas goianas da biblioteca que doaram à Rouanet desde 2021:** Refrescos Bandeirantes (R$ 3,76 mi), Saneago (R$ 3,54 mi), Nutriza (R$ 400 mil), Real Distribuição (R$ 215 mil) e Caramuru (R$ 100 mil).

## 4. Correções feitas na base

- **CNPJs corrigidos** (Vale, Stone, Fleury, Nestlé), cada um com a prova registrada.
- **33 nomes sem CNPJ ganharam CNPJ**, só quando o SALIC, o PAT ou a Secult devolveram a razão social correspondente — vários eram a mesma empresa já listada pela razão social e foram fundidos. Marcas de grupo (Sicoob, Sicredi, BTG, Coca-Cola, Unimed nacional) continuam sem CNPJ — não há um CNPJ único para o grupo.
- **Entidades isentas** (Sebrae, Sesc, Fieg/Sesi/Senai, Fecomércio, PUC Goiás) marcadas: não apuram IRPJ pelo Lucro Real, então não destinam por incentivo fiscal — patrocinam com verba própria.
- **A mesma empresa listada duas vezes** (por marca e por razão social — "Telefônica Vivo" e "TELEFONICA BRASIL S.A.") virou uma só; a vaga que sobra é reposta pela próxima empresa da lista oficial do ICMS, sem mudar o critério de quem entra no ranking.
- **Os três registros falsos saíram**, e o ranking agora recusa fragmento de data como nome.
- **As etiquetas do painel mostram só o verificado** e dentro da janela de 5 anos, com ✓. A hipótese antiga ficou guardada à parte. Uma doação de 2009 não aparece mais como relação viva com a empresa.

## 5. Nada inventado

- Valor, ano e CNPJ só com fonte oficial.
- Onde as duas bases do Ministério da Cultura divergem (7 empresas), **as duas ficam registradas**.
- No Goyazes, o valor é o do **projeto aprovado** — quando há mais de uma empresa no projeto, não é a cota de cada uma, e isso está escrito em cada registro.
- Conferência: cinco valores da base foram lidos de novo no SALIC ao vivo e bateram centavo por centavo; a soma do Goyazes 2024 e 2025 bate com o total publicado pela Secult.

## 6. Parecer do conselho (engenharia)

- **Extremamente pessimista:** a resolução de CNPJ por nome é o ponto frágil. Mitigado: só 33 resoluções, cada uma com a razão social devolvida pelo órgão; as de marca ambígua ficaram de fora.
- **Pessimista:** o Goyazes não traz CNPJ; casar nome é arriscado. Mitigado: grafias da base casadas por tabela explícita e revisada; descobertas agrupadas por semelhança ficam marcadas "confirmar pelo CNPJ".
- **Levemente pessimista:** o relatório por doação do SalicComparar é uma tela, não uma API — pode mudar. Mitigado: o extrato está gravado no repositório e o motor lê primeiro a base verificada.
- **Neutro:** o sistema passou a distinguir quatro coisas que antes eram uma — destinou, não consta, não lido, sem fonte pública. Parâmetro de qualidade: nenhum campo sai sem status.
- **Levemente otimista:** 64 empresas com Lucro Real confirmado por lei, não por estimativa de porte.
- **Otimista:** o motor de empresas volta a enxergar a Rouanet — estava cego desde a mudança da API.
- **Extremamente otimista:** 87 empresas goianas que já destinam ICMS a projetos culturais entram no radar — o grupo mais próximo da realidade de uma entidade de Goiânia.

## 7. O que fica pendente — e quando

1. **LIE:** consultar a partir de 26/10/2026, quando termina o defeso.
2. **FIA e Fundo do Idoso:** só por pedido de acesso à informação aos conselhos. É decisão sua fazer o pedido — posso redigir.
3. **CNPJ das 87 empresas novas do Goyazes:** consulta ao cadastro da Receita, uma a uma.

## 8. Testes

41 testes novos (`tests/test_incentivos_empresas.py`) cobrando: fontes gravadas e somas conferidas, Rouanet com janela de 5 anos e prova de Lucro Real, grafias do Goyazes, PAT sem confirmar regime, mecanismos sem fonte sempre nulos, CNPJs corrigidos sem atingir a empresa verdadeira dona do número, registros falsos fora, etiqueta só com o verificado e aplicação idempotente.
