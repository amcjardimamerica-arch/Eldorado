# Relatório de desempenho dos motores de busca — 23/09/2026

O que os motores capturaram, o que disso serviu, e o que deve deixar de ser capturado. Todos os números
saem da base do próprio sistema, medidos hoje sobre **695 registros** acumulados nas rodadas de 08, 09 e
15 de setembro.

---

## 1. O número que governa todos os outros

| Alcance geográfico do registro | Registros | % |
|---|---:|---:|
| **Outra UF** (municipal, fora de Goiás) | **596** | **85,8%** |
| Goiás | 37 | 5,3% |
| Nacional | 30 | 4,3% |
| Sem UF a classificar | 32 | 4,6% |

A abrangência aprovada pelo titular é **nacional + Goiás + Goiânia**. Logo, **85,8% de tudo que os motores
capturaram está fora do alcance da associação** — não por mérito, por porta: chamamento municipal de outro
estado exige sede, atuação local ou inscrição em conselho municipal daquele município.

Cruzando alcance com veredito, o desperdício fica exato:

| Alcance | Aproveitáveis (aprovado + atenção) | Reprovados | Sem veredito |
|---|---:|---:|---:|
| Outra UF | 76 | 358 | 162 |
| Nacional | **27** | 3 | 0 |
| Goiás | **6** | 25 | 6 |
| Sem UF | 3 | 23 | 6 |

**Dos 112 registros aproveitáveis de toda a base, apenas 33 estão dentro da abrangência.** Os outros 79
foram verificados, tiveram prazo conferido, documento lido, ficha escrita — e não servem.

**O filtro existe e não é usado na hora certa.** `src/enquadramento.py` já calcula
*"atuação geográfica do edital ⊆ atuação da associação"*, e o arquivo de enquadramento da AMC diz, em
09/09: de **140 editais abertos, 8 compatíveis geograficamente**. Esse filtro roda na fase 2, depois da
coleta, da triagem e da verificação. **Rodando antes, ele economizaria a maior parte do esforço da
operação.**

---

## 2. Rendimento por origem: onde a busca rende e onde não rende

| Origem | Registros | Aprovados | Dentro da abrangência | Aproveitamento real |
|---|---:|---:|---:|---:|
| **Outras fontes** (patrocinador privado, programa federal) | 56 | 22 | **28** | **50,0%** |
| PNCP relocalizado pela busca oficial | 12 | 6 | 1 | 8,3% |
| PNCP consultado | 310 | 37 | 15 | **4,8%** |
| PNCP sem chave | 73 | 4 | 2 | 2,7% |
| PNCP barrado no título | 5 | 0 | 2 | — |

**A fonte do patrocinador rende dez vezes mais que o PNCP** por registro trabalhado (50,0% contra 4,8%),
e a diferença aumentou em relação à medição de 09/09 justamente porque o filtro de abrangência foi
aplicado: as fontes privadas e federais são majoritariamente nacionais, e por isso quase tudo que elas
trazem está dentro do alcance.

Confirmação pelo domínio das páginas oficiais dos 112 aproveitáveis: 70 em `pncp.gov.br`, mas os que
efetivamente servem estão em `bndes.gov.br` (6), `institutolojasrenner.org.br` (5), `gov.br` (3),
`climaesociedade.org` (3), `goias.gov.br` (2), `mariaemilia.org.br`, `rouanet.cultura.gov.br`,
`portal.al.go.leg.br`, `goiania.go.leg.br`, `impactarte.org.br`.

---

## 3. O que deve ser DESCARTADO nas próximas buscas

Regras de descarte, cada uma com o volume que ela elimina, medido nesta base.

### 3.1 Descarte por objeto — 409 registros (58,8% da base)

Nenhum destes é edital de fomento a OSC, e **a reprovação não depende de prazo**:

| Família | Registros | O padrão textual |
|---|---:|---|
| Serviço ao órgão | 174 | credenciamento de prestador remunerado por procedimento, vaga ou paciente |
| Compra pública | 45 | aquisição de bens pelo órgão |
| Compra ou fornecimento | 24 | fornecimento ao órgão |
| Instituição financeira | 13 | credenciamento de banco, cooperativa de crédito |
| Parecerista ou júri | 12 | subcomissão técnica, avaliador, jurado — pessoa física técnica |
| Imóvel ou mercado | 12 | locação e prospecção de imóvel |
| Uso de espaço público | 11 | permissão de uso para exploração comercial |
| Cachê artístico | 10 | contratação de artista para evento |
| Busca de patrocinador | 7 | o órgão busca quem o patrocine — a entidade pagaria |
| Resultado de habilitação | 7 | ato decorrente de edital já julgado |
| Resultado de edital | 6 | homologação, adjudicação |

### 3.2 Descarte por alcance — 596 registros de outra UF

**Não é exclusão, é rebaixamento.** Ficam no acervo histórico (servem de modelo e de série temporal para
previsão de reabertura) e saem da fila de verificação enquanto a abrangência for nacional + GO + Goiânia.
Se o titular ampliar a abrangência, voltam sozinhos.

### 3.3 Descarte por assinatura de data

- **Janela maior que três anos** — fachada de credenciamento contínuo, não prazo de inscrição. A base tem
  encerramentos em 2034 (dez registros do mesmo consórcio de saúde) e um em **2099**.
- **Encerramento anterior à própria publicação** — sete registros. Crateús/CE foi divulgado seis horas
  depois de fechar; Araquari/SC entrou três meses e meio depois; Vila Rica/MT, sete meses. Quando a fonte
  se contradiz, não há prazo a apresentar.
- **Janela de um dia** (abertura igual ao encerramento) — 82 registros. É assinatura de data de
  publicação, não de janela. Exceção comprovada: Indaiatuba/SP, onde a data era real — por isso a regra é
  "a confirmar no documento", não descarte automático.

### 3.4 Descarte de vetor e de duplicata

- **Edições inteiras de diário oficial sem ato identificado** — 17.140 registros na base de oportunidades.
  Não são editais: são publicações onde um termo apareceu. Servem para descobrir órgão e processo, nunca
  como edital.
- **Duplicatas** — 22 grupos, 62 registros. Nesta rodada apareceram mais três pares: Impactarte
  (`ea14b1b3` e `0eac700d`), BNDES Patrocínio (`0e732756` e `2bef5397`) e Gravataí/RS, além do envelope de
  Porto Feliz, que é o inverso: **um registro contendo cinco editais**.

---

## 4. O que deve ser APROVEITADO nas próximas buscas

### 4.1 Os sinais textuais que funcionaram, com acerto medido

Medidos na zona de atenção, onde o motor não decide sozinho:

| Expressão | Decide por | Acertos / erros |
|---|---|---|
| `pessoas jurídicas … para realização/prestação de serviço` | reprovar | 71 / 0 |
| `prestadora(s) de serviço` | reprovar | 29 / 0 |
| `credenciamento de pessoas jurídicas` | reprovar, salvo *"de direito privado, sem fins lucrativos"* | 88 / 1 |
| `com ou sem fins lucrativos` | reprovar, salvo premiação ou fomento direto | 34 / 1 |
| `organizações da sociedade civil` | aprovar | 18 / 1 |
| `apoio financeiro`, `termo de colaboração`, `termo de fomento` | aprovar | 8 / 0 |

**A mais contra-intuitiva continua sendo a mais útil:** `com ou sem fins lucrativos` contém a marca de OSC
e significa o contrário — o edital admite empresa, logo é contratação.

### 4.2 Os campos que servem e os que enganam

| Campo | Serve? | Medida |
|---|---|---|
| `objetoCompra` da API do PNCP | **sim** — é o único que separa fomento de contratação | decidiu 68% dos casos sozinho |
| Lista de anexos (`/arquivos`) | **sim** — títulos com REVOGAÇÃO, ERRATA, PRORROGAÇÃO valem mais que qualquer campo | achou a revogação de Porangatu/GO, a de Quixeramobim/CE e a prorrogação de Ipojuca/PE |
| `amparoLegal` | **não** | quase todos vêm como Lei 14.133/2021 mesmo quando o objeto declara MROSC expressamente |
| `situacaoCompraNome` | **não** | "Divulgada no PNCP" aparece em editais encerrados há três anos |
| `linkSistemaOrigem` | **quase nunca** | preenchido em 51 de 317; 22 deles com apenas um espaço em branco; o resto aponta para plataforma privada |
| `dataEncerramentoProposta` | **com ressalva** | é a janela de proposta, não o cronograma de inscrição; o cronograma real está no PDF |

### 4.3 As fontes que devem crescer

Por rendimento medido, o catálogo deve crescer nesta ordem:

1. **Patrocinadores privados e programas federais com página própria** — 50% de aproveitamento. É um alvo
   de dezenas de instituições, não de milhares de municípios, e cada uma tem uma página só, que muda pouco.
2. **Fontes de Goiás e de Goiânia** — 37 registros na base para 5,3% do total, quando a abrangência
   aprovada põe Goiás no centro. O catálogo tem 101 fontes goianas e elas produziram pouco: vale investigar
   se estão apontando para páginas de editais ou para índices de secretaria.
3. **Mecanismos permanentes** — penas pecuniárias do TJGO, destinação da Receita Federal, emendas
   parlamentares, Rouanet. Não têm prazo, não aparecem no alarme, e por isso somem do radar. São os de
   melhor relação esforço/retorno para uma entidade com documentação a regularizar.

---

## 5. As correções de motor que esta rodada exige

Em ordem de retorno, com o teste que comprova cada uma.

**M1 — Filtro de abrangência ANTES da verificação, não depois.**
Hoje o sistema verifica 695 registros e descobre na fase 2 que 8 são compatíveis. Invertendo: filtrar por
abrangência logo após a triagem de objeto, e verificar só o que passa.
*Ganho medido:* 85,8% menos verificação, sem perder nenhuma oportunidade acessível.
*Teste de aceite:* nenhum registro de outra UF entra na fila de verificação enquanto a abrangência for
nacional + GO + Goiânia; e a contagem de compatíveis geográficos é publicada em cada rodada.

**M2 — Patrocinador nacional com edital territorial.**
O Funbio é fonte nacional e suas chamadas 07 e 08/2026 são fechadas ao litoral do Paraná. O filtro de
abrangência aprovou por causa da fonte e errou por causa do objeto.
*Correção:* extrair do objeto os municípios ou a região nomeada e cruzar com a abrangência, mesmo em fonte
nacional.
*Teste:* as chamadas do Funbio para o litoral do Paraná não aparecem como compatíveis para uma entidade de
Goiânia.

**M3 — Requisito de habilitação como campo de primeira classe.**
O FME Transforma exige **diploma de doutorado do coordenador**; o CONANDA exige **registro no CMDCA** e
**execução em cinco regiões**; Guaíra exige **inscrição no Conselho Municipal de Educação**. Nenhuma
dessas exigências é capturada hoje, e todas são eliminatórias antes do mérito.
*Correção:* extrair do edital os requisitos de habilitação e cruzar com o perfil da associação, marcando
`inelegivel_por_requisito` com o requisito nomeado.
*Teste:* o FME aparece como inelegível para a AMC com o motivo "coordenador precisa ter doutorado", em vez
de aparecer como a maior oportunidade aberta — que foi o que o sistema disse em 09 e em 15/09, e estava
errado.

**M4 — Porte do proponente.**
O BNDES Periferias exige projeto de **R$ 20 milhões** e a AMC cabe no subprojeto de R$ 500 mil a R$ 3
milhões, na posição de organização de base.
*Correção:* registrar valor mínimo do projeto e distinguir o papel — proponente ou executor —, porque a
ação recomendada muda completamente.
*Teste:* o BNDES Periferias aparece com o rótulo "entrar como organização de base", não "inscrever-se".

**M5 — Um registro, vários editais.**
Porto Feliz/SP: um registro do PNCP com cinco editais PNAB, cinco inscrições separadas na plataforma
CultBR.
*Correção:* quando a lista de anexos trouxer mais de um documento do tipo Edital com números distintos,
desdobrar o registro.
*Teste:* o registro de Porto Feliz vira cinco, cada um com seu número.

**M6 — Mecanismo permanente não é edital sem prazo.**
Receita Federal, penas pecuniárias, Impactarte, emendas: prazo nulo por natureza, não por falta de
verificação. Hoje entram na fila de pesquisa e nunca saem.
*Correção:* classe própria `mecanismo_permanente`, com campo `como_se_habilita` no lugar de prazo, e
lista própria no painel.
*Teste:* nenhum mecanismo permanente aparece na fila de "falta prazo".

**M7 — Hora, não só dia.**
Ipu/CE encerra às **17h00**; Guaíra às **17h00**; o FME às **23h59**. A base guarda só a data.
*Correção:* guardar hora de encerramento quando o edital a declarar.
*Teste:* o painel mostra "hoje, até 17h" e não apenas "hoje".

**M8 — Ano eleitoral como restrição de mecanismo.**
A Receita Federal veda entrega de mercadorias a OSC em ano eleitoral. Já havia a armadilha eleitoral do
portal de Goiás, que suspende notícias. É o mesmo fenômeno em duas formas.
*Correção:* marcar mecanismos com restrição eleitoral e sinalizar no painel durante o período.
*Teste:* a destinação da Receita Federal aparece como "habilitar agora, entrega suspensa até o fim do
período eleitoral".

---

## 6. Limites honestos desta medição

**A API de consulta do PNCP esteve instável hoje.** Sete registros não puderam ser reverificados — o
endpoint devolveu *read timeout* em dezenas de tentativas ao longo de mais de uma hora, com cache-busters
distintos, enquanto o endpoint de arquivos respondia normalmente. São eles: Indaiatuba/SP, Itatinga/SP,
Osório/RS, Montes Claros/MG, UNICENTRO/PR, Canoas/RS e Peruíbe/SP. Os prazos desses sete **permanecem como
estavam, não confirmados hoje**, e isso está escrito registro por registro.

**Três sites continuam inacessíveis por rota automatizada:** Osório/RS (certificado com hostname inválido
e 403 na raiz), Xanxerê/SC (403 em todo o domínio) e Nova Ubiratã/MT (portal só em JavaScript). Não é
ausência de edital: é bloqueio de acesso, e a diferença entre as duas coisas é justamente o que o
parâmetro "coberto até" existe para registrar.

**E o limite que nenhuma dessas medições cobre:** tudo aqui mede o que entrou na base. **Nada mede o que
os motores nunca viram.** Enquanto não houver a auditoria cega de recall — sortear municípios e
patrocinadores, procurar à mão e comparar —, a taxa de perda permanece desconhecida.
