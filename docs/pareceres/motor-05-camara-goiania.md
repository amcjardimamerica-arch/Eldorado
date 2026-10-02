# Parecer do conselho — Motor 05 · Câmara Municipal de Goiânia

**Data:** 01/10/2026 · **Motor:** `camara-goiania-pl` (Bússola, posição 05) · **Matéria:** técnica (engenharia de coleta), com reflexo jurídico (utilidade pública municipal como requisito de habilitação; leis de fomento e parceria — Lei 13.019/2014 e Lei Municipal 8.411/2006; emendas impositivas)

## 1. Síntese

Em setembro de 2026 o motor 05 rodou **40 vezes, achou 0 e registrou 3 a 5 falhas por dia**. As causas:

- lia a **home do portal** (Plone), que traz o menu e nenhuma proposição;
- lia `/feed/` e `/diario-oficial`, que dão **404**, e `/transparencia/licitacoes-e-contratos`, que só tem contratos da própria Câmara;
- tentava o **SAPL** (`sapl.goiania.go.leg.br`), que responde com **certificado inválido** e não é o sistema em uso;
- procurava "edital" no rótulo de links, mas a Câmara quase nunca publica edital para OSC.

Onde estão os dados: no **SUAP da Câmara** (`suap.camaragyn.go.gov.br/camara/consulta_publica/`), o "Processos Eletrônicos" do Portal da Transparência. Cada projeto de lei tem número, assunto, autor, setor atual, data e, na página do processo, a lista de documentos com data (parecer jurídico, despachos, votação).

**O achado mais importante:** o **Projeto de Lei nº 288/2026**, do vereador **Heyler Leão**, declara de **utilidade pública municipal a própria A.M.C. Jardim América**. Foi protocolado em 17/06/2026 e está em trâmite na Procuradoria (setor PROC). Recebeu **parecer jurídico em 17/09/2026** e o **Despacho 766/2026 – PROC/PRES/MESA/CMG em 29/09/2026**. O motor antigo nunca o viu.

**Decisão do neutro:** aprovar a versão 2. O motor passa a ler o SUAP por assunto, segue a tramitação dos processos da associação e lê as notícias do portal. Classifica cada item com o motivo escrito e monta a lista de utilidades públicas (habilitação).

## 2. Resultado de setembro/2026 (motor antigo)

| Item | Número | Evidência |
|---|---|---|
| Leituras | 40, todas com 0 achados (`vazias_seguidas` = 40) | `estado/esquadra.json` › `camara-goiania-pl` |
| Falhas por dia | 3 a 5, de 04/09 a 30/09 (26 dias com registro) | `estado/esquadra_diario.json` |
| Páginas que responderam | só a home: 15,9 KB e 0 links | `diagnostico` de 30/09 |
| Bloqueios registrados | `sapl.goiania.go.leg.br` 76 (URLError), `www.goiania.go.leg.br` 55 (HTTPError e timeout), `transparencia.camaragyn.go.gov.br` 23 | `estado/bloqueios.json` |
| Agenda × execução | agenda semanal (quinta, coleta local), mas a escala rodou todo dia na nuvem | `config/agenda_motores.json`; `motivo` = "motor regular e geral — todo dia" |

## 3. Defeitos encontrados

1. **D1 — Rota errada.** Home, RSS inexistente, SAPL com certificado inválido e páginas 404. As proposições estão no SUAP, aberto pelo Portal da Transparência (Núcleo GOV) → Projetos de Lei.
2. **D2 — Objeto errado.** O motor procurava edital. O que a Câmara produz para a associação é **habilitação** (utilidade pública municipal), **leis** que criam programas, fundos, isenções, doações e parcerias com entidades, **emendas impositivas** e, raramente, um chamamento.
3. **D3 — A própria associação fora do radar.** O PL 288/2026, que declara de utilidade pública a A.M.C. Jardim América, estava em tramitação desde junho, sem nenhum aviso.
4. **D4 — Falha diária sem causa útil.** Os 404 e o certificado inválido apareciam como "falha" genérica, e o dia ficava azul com falhas.
5. **D5 — Agenda contraditória.** O painel dizia "semanal, coleta local", mas a escala rodava todo dia na nuvem.

## 4. Rotas (Etapa 3)

Testes com IP brasileiro pelo navegador do titular em 01/10/2026. O `robots.txt` do portal permite tudo.

| Rota | Resposta | O que entrega | Decisão |
|---|---|---|---|
| `suap.camaragyn.go.gov.br/camara/consulta_publica/?classificacao=PL&assunto=…&ano=…&page=…` | 200 · HTML do servidor, 20 por página, do mais novo para o mais antigo | número do processo, assunto (ementa), autor, setor atual, situação e data de criação. Exige um assunto; o filtro de ano é o do protocolo | **usar** (Fonte A) |
| `…/processo_eletronico/visualizar_processo/{id}/?page=…` | 200 | lista de documentos com data (instrução, parecer, despacho), "Total de N itens" | **usar** para os processos da associação (Fonte B) |
| `www.goiania.go.leg.br/search_rss?SearchableText=…&sort_on=created&sort_order=reverse` | 200 · RSS 1.0, 25 por busca | notícias, vídeos e arquivos (atas) do portal | **usar** (Fonte C), só notícias e vídeos |
| `www.goiania.go.leg.br/RSS` | 200 | últimas publicações do portal | não precisa (a busca cobre) |
| `…/processo-legislativo/pautas-de-sessoes` | 200 | pauta diária em PDF (projetos e requerimentos) | não usar agora: exige leitor de PDF |
| `camaragoiania.nucleogov.com.br/cidadao/informacao/licitacoes_cnt` | 200 · dados por `POST /api` (JavaScript) | pregões da própria Câmara (alimentação, firewall…) | **descartar**: nada para OSC |
| `sapl.goiania.go.leg.br` | certificado inválido | — | descartar |
| `/feed/`, `/diario-oficial`, `/transparencia/licitacoes`, `/atividade-legislativa/proposicoes` | 404 | — | descartar |

Em 2026, até 30/09, a busca por assunto devolve: "programa" 88 processos, "cultura" 24, "utilidade pública" 20, "emenda" 14, "associação" 11 e "entidade" 10.

## 5. Parametrização antes × depois

| Item | Antes | Agora |
|---|---|---|
| Rotas | home, `/feed/`, SAPL, licitações (5 URLs, 6 páginas) | SUAP por assunto (18 assuntos, janela de 35 dias, até 4 páginas cada) + processos da associação (com documentos) + 9 buscas de notícias |
| Unidade de leitura | rótulo de link | processo legislativo (número, ementa, autor, setor, data) e notícia |
| Objeto | "edital" | utilidade pública (habilitação), fomento/parceria/isenção/doação para entidades, fundo municipal, emenda impositiva, regra para entidades parceiras, chamamento da Câmara, bairro Jardim América |
| Saída | achados | **OPORTUNIDADE**: chamamento ou edital com entidades como público e prazo aberto. **ACOMPANHAR**: a utilidade pública da associação, leis de fomento, parceria, fundo ou regra para entidade, e emendas impositivas. **Lista de habilitação**: as utilidades públicas de outras entidades, com projeto, vereador e situação. **RUÍDO**: denominação, homenagem, data comemorativa, concurso |
| Associação | — | processos pelo nome (A.M.C. Jardim América, Moradores e Comerciantes do Jardim América). Lidos **antes** das outras fontes, sem corte de janela. Aviso de **novidade** quando aparece documento novo |
| Nuvem × local | sempre na nuvem, com falha | tenta na nuvem. Se o SUAP recusar o IP, registra "aguardando coleta local" sem falha, e `scripts/coleta_brasil.py` faz a leitura completa |
| Estado | — | `estado/camara_goiania.json`: abertas, a acompanhar (a da associação primeiro), utilidade pública (até 600), processos da associação e histórico. Leitura com falha **não apaga** o que já estava lá |
| Agenda | semanal (quinta), rodando todo dia | todos os dias às 20:23, alinhada ao que a escala já fazia |

## 6. Calibração (Etapa 6)

O código desta versão rodou sem alteração no navegador do titular, com IP brasileiro e Python no próprio navegador, sobre o SUAP e o portal reais.

**(a) Leitura de 01/10/2026:** 22 consultas ao SUAP, em 7 s, e nenhuma falha. Foram 103 processos lidos, 22 deles criados nos últimos 35 dias. Mais o processo da associação, com 19 documentos, e 18 notícias distintas de 9 buscas.

| Veredito | Quantos | Quais |
|---|---|---|
| OPORTUNIDADE | 0 | nenhum chamamento ou edital da Câmara para entidades em setembro |
| ACOMPANHAR | 2 | **PL 288/2026: utilidade pública da A.M.C. Jardim América** (parecer jurídico em 17/09, despacho 766/2026 em 29/09); PLC 31/2026 (Sistema Municipal de Cultura: parceria com Pontos de Cultura) |
| Lista de habilitação | 3 | PL 434/2026 (PRORED, Oséias Varão); PL 419/2026 (Associação Esportiva do Centro de Formação…, Henrique Alves); PL 417/2026 (Instituto de Apoio a Crianças e Adolescentes Casa do P…, Lucas Vergílio) |
| RUÍDO | 18 processos e 18 notícias | programas sem entidade, datas comemorativas, patrimônio imaterial, fundos imobiliários, concurso da Câmara, homenagens |

**(b) 2026 inteiro (janeiro a setembro), 169 processos:**

- 20 utilidades públicas: 1 é da associação, 19 vão para a lista de habilitação, e as 20 tiveram o nome da entidade lido;
- 11 para acompanhar;
- 139 ruídos.

Entre os 11 para acompanhar, três interessam diretamente à associação:

- **PL 219/2026:** moderniza a seleção, a governança e a fiscalização das **parcerias com entidades** (Lei 8.411/2006, o MROSC municipal);
- **PL 334/2026:** **adoção de áreas verdes ociosas por associações de moradores**;
- **PL 394/2026:** uso gratuito de praças e parques para **ações sociais sem fins lucrativos**.

Os outros oito:

- PLC 31/2026 (Pontos de Cultura);
- PL 79/2026: exigências de proteção à criança para **entidades parceiras do município**;
- Fundo de Afroempreendedorismo;
- ofício sobre o FMAS;
- emendas impositivas da LOA 2026 (justificativas de impedimento);
- Fundo do Consumidor;
- entidades de tiro esportivo;
- a própria utilidade pública da A.M.C.

**Conferência manual:**

- os 11 itens para acompanhar e as 20 utilidades públicas foram lidos um a um;
- dos 139 ruídos, filtrei os 114 com palavras sociais ou "institui" e li um a um os 12 que citam associação, entidade, moradores, coletivo ou instituição. Saiu um só erro: o PL 79/2026 (regra para entidades parceiras), que virou a categoria "regra para entidades" e ganhou teste;
- as 18 notícias de setembro são de tramitação, concurso e homenagem, e não há chamamento.

**Revisão independente:** um revisor separado leu o código e achou 16 pontos. Todos foram corrigidos, e os 11 relevantes têm teste:

- leitura com falha apagava a lista de acompanhamento;
- a associação só era lida depois das 18 buscas e podia perder o prazo da execução (agora é lida primeiro);
- "denominação" no texto derrubava a utilidade pública da associação;
- CPF no assunto ou no autor chegava ao estado;
- notícia de concurso ou do Parlamento Jovem virava oportunidade;
- falha na página do processo gerava "novidade" falsa no dia seguinte;
- recusa no meio da Fonte A descartava o que já tinha sido lido;
- o parser era rígido (classe com atributo extra, ícone em `<i>`);
- erro de certificado era tratado como recusa de IP;
- o nome da entidade era cortado no primeiro ponto ("A.M.C.", "Sto.");
- "entidades da Administração Pública" e "Instituto de Previdência" contavam como OSC;
- título de documento sem checagem de injeção;
- link para outro host;
- número de "Emenda à Lei Orgânica";
- contagem de habilitações novas;
- aviso de cobertura cortada.

## 7. Conselho de 7 lentes

Os conselheiros são arquétipos sorteados para esta análise, não pessoas reais.

**1. Extremamente pessimista — chief engineer de integração com sistemas legados de governo.**
O SUAP não tem API pública: o motor lê HTML. Uma atualização do SUAP, que é software livre e é atualizado pelo fornecedor, pode mudar as classes. A defesa é o alerta "o SUAP disse ter processos, mas o leitor não reconheceu nenhum bloco", e não o silêncio. Outro risco: o domínio `camaragyn.go.gov.br` recusou o robô no passado, com 23 URLError. Se o SUAP também recusar o GitHub, o motor depende de o titular rodar a coleta local.

**2. Pessimista — staff engineer de relevância.**
A busca do SUAP casa só o **assunto** (a ementa), não o texto do projeto. Um projeto cuja ementa diz "institui o programa X" sem citar entidades passa como ruído, mesmo que o artigo 5º preveja parceria com OSC. O "Sua Nota, Nossa Cidade" é um exemplo: programas de nota fiscal costumam permitir doar créditos a entidades, e a ementa não diz isso.

**3. Levemente pessimista — professor de engenharia de computação, especialista em recuperação de informação.**
Edital da própria Câmara para OSC é raro: 0 em setembro. A Fonte C (notícias) é a de menor rendimento e existe para não perder o caso raro. As 25 respostas por busca do Plone vêm ordenadas por data, mas cortam semanas movimentadas.

**4. Neutro — CTO de plataforma de dados legislativos, mediador.** O voto está na seção 8.

**5. Levemente otimista — professor de ciência da computação, especialista em sistemas explicáveis.**
Cada item traz o motivo, o número do projeto, o vereador e o setor. A lista de utilidades públicas mostra **quais vereadores apresentam utilidade pública e para quem**, e esse é um mapa de padrinhos políticos útil para a associação.

**6. Otimista — staff engineer de produto, foco em captação.**
A versão 2 transforma o motor em **acompanhamento da habilitação da própria associação**. A utilidade pública municipal é requisito de editais municipais e de subvenção, e o motor avisa quando o PL 288/2026 anda: parecer, comissão, plenário, sanção. Os PLs 219, 334 e 394 mudam o terreno onde a associação atua: parceria, área verde e uso de praça.

**7. Extremamente otimista — CTO de big tech, pós-doutor em Python.**
Com o número do processo como chave, o sistema cruza a lei aprovada aqui com o **Diário Oficial de Goiânia** (motor 01). A lei sancionada sai lá, e o chamamento que ela autoriza também. A Câmara passa a ser o **aviso antecipado**: o recurso que vai existir em seis meses aparece hoje como projeto.

## 8. Voto do neutro (vinculante)

**Decisão:** aprovar o motor 05 versão 2 e publicar depois dos PRs dos motores 03, 04 e 22. A base do ramo é a do motor 22, porque o leitor de prazo das notícias vem do motor 22.

**Metas (medidas a cada 30 dias em `estado/camara_goiania.json` › `historico`):**

| Indicador | Meta |
|---|---|
| Leituras com resposta do SUAP (nuvem ou local) | ≥ 90% dos dias úteis |
| Processo da associação lido | 100% das leituras com resposta |
| Mudança na tramitação da associação avisada | no dia da leitura seguinte ao novo documento |
| Utilidades públicas com nome da entidade lido | ≥ 95% (calibração: 20/20) |
| Precisão de ACOMPANHAR (conferida pelo titular) | ≥ 80% |
| Falha de formato do SUAP | 0 dias sem alerta (`alerta_formato`) |

**Mitigação de riscos:**

1. **Recusa de IP na nuvem:** o motor tenta. Se o SUAP recusar, registra "aguardando coleta local" sem colorir o dia de vermelho, e `scripts/coleta_brasil.py` já inclui o motor, porque os dois domínios estão em `exige_brasil`.
2. **Mudança de HTML:** parser tolerante a atributos e ícones, e alerta quando há "Total" sem blocos.
3. **Ementa curta:** lista generosa de assuntos e categorias para fundo, programa com entidades e regra para entidades. A leitura do texto do projeto é o próximo passo.
4. **Leitura parcial:** não apaga o estado e não gera aviso falso. A associação é lida primeiro.
5. **PII:** CPF mascarado em assunto, autor e título de documento. Os documentos do processo (estatuto, documentos pessoais) nunca são baixados: só o título e a data.

## 9. Melhorias aplicadas

| Arquivo | O que mudou |
|---|---|
| `src/camara_goiania.py` (novo) | leitor do motor 05: Fontes A (SUAP por assunto), B (processos da associação, com documentos) e C (notícias), recusa de IP, classificação, lista de habilitação, aviso de tramitação, preservação do estado, alarmes |
| `config/camara_goiania.json` (novo) | assuntos, janelas, nomes da associação, buscas de notícias, ritmo e limites |
| `src/sensores.py` | o `camara-goiania-pl` passa ao novo leitor |
| `config/sensores.json` | URLs reais (SUAP e busca do portal), nota de 01/10 e `suap.camaragyn.go.gov.br` em `exige_brasil` |
| `config/rotas_motores.json`, `config/agenda_motores.json` | rotas verificadas, perfil (habilitação e acompanhamento) e agenda diária |
| `src/auditoria_motores.py`, `scripts/descricao_motores.py` | textos do conselho e da evolução gratuita |
| `tests/test_motor05_camara_goiania.py` (novo) | 29 testes: blocos do SUAP, documentos, RSS, utilidade pública da associação, habilitação, fomento, emenda, regra para entidades, ruídos, notícias, recusa na nuvem e no local, novidade, quarentena e os casos da revisão |

**Testes:** a suíte completa tem as mesmas 40 falhas e 3 erros que já existiam no ramo do motor 03, e nenhuma falha nova. Os 29 testes novos estão verdes, e os dos motores 01 a 04 e 22 também. `scripts/verificar_privacidade.py` não encontrou nenhuma credencial publicada.

## 10. Para o titular (01/10/2026)

| O quê | Situação | Por que importa |
|---|---|---|
| **PL 288/2026: utilidade pública da A.M.C. Jardim América** (Heyler Leão) | em trâmite; parecer jurídico em 17/09; Despacho 766/2026 (PROC/PRES/MESA) em 29/09; setor PROC | requisito de habilitação em editais municipais e em subvenção |
| PL 219/2026: parcerias com entidades (altera a Lei 8.411/2006) | em trâmite | muda as regras de seleção e de prestação de contas das parcerias com a Prefeitura |
| PL 334/2026: adoção de áreas verdes ociosas por associações de moradores | em trâmite | a associação pode adotar área verde do bairro |
| PL 394/2026: uso gratuito de praças e parques para ações sociais sem fins lucrativos | em trâmite | eventos e ações da associação em praça pública sem taxa |
| PL 79/2026: proteção à criança nas entidades parceiras do município | em trâmite | exigência nova, se a associação fizer parceria com crianças e adolescentes |

## 11. Pendências

1. **Ordem de implantação:** os PRs dos motores 03, 04 e 22 antes deste.
2. **Primeira execução na nuvem:** ver se o SUAP responde ao GitHub. Se responder, tirar `suap.camaragyn.go.gov.br` de `exige_brasil`. Se recusar, a coleta local passa a ser a leitura deste motor.
3. **Texto do projeto:** ler o documento "Projeto de Lei" de cada item para acompanhar (o conteúdo é carregado à parte no SUAP) e confirmar quem recebe o recurso. Os programas de nota fiscal, como o "Sua Nota, Nossa Cidade", são o caso típico.
4. **Pautas de sessões em PDF:** mostrariam em que dia o PL 288/2026 vai a plenário. Exige leitor de PDF, e por isso é decisão sobre dependência.
5. **Painel:** os itens para acompanhar dos motores 01 a 05 e 22 ficam em `estado/*.json` (`atos_para_painel`), mas o painel ainda não os mostra. Ligá-los ao painel é uma decisão de prioridade do titular.
