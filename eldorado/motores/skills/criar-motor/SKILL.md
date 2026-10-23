---
name: criar-motor
description: Como criar um motor do Eldorado novo, do estudo de reorganização ao motor registrado e medido, usando o motor genérico, os alvos e o canivete suíço. Use sempre que for criar, refazer ou ampliar um motor.
metadata:
  versao: 1
  criada_em: 2026-10-22
  origem: plano inicial do Eldorado novo (A — workflow; B — arquivos e vínculos; C — ferramentas estudadas no GitHub) e o estudo de reorganização dos motores (19/10/2026); o Eldorado0 só como fonte de aprendizado
  uso: 0
  resultado: null
  estado: ativa
---

# Criar um motor do Eldorado

Um motor do Eldorado é **configuração e aprendizado**, nunca código. Todos os motores rodam sobre o **motor genérico**
(`eldorado/motores/canal/motor.py`), que já sabe acessar, ler, descobrir, pré-filtrar, entregar e aprender. Criar um motor
é declarar, num arquivo `eldorado/motores/canal/config/<id>.toml`, **onde** ele procura, **o que** ele reconhece e **o que
ele já aprendeu**. A estrutura do sistema não muda quando um motor entra.

## Os princípios

1. **Um canal, um motor.** O motor é especializado no tipo de fonte (diário oficial, portal estadual, API federal,
   tribunal, casa legislativa, portal do terceiro setor). Os motores antigos que liam o mesmo canal são **reunidos** nele
   (`nomes_anteriores`), e o histórico deles passa a ser dele.
2. **Pontos de captação são alvos**, não motores. Cada programa vigiado vira um `[[alvo]]` do motor do seu canal, com a
   sua previsão de edição.
3. **API primeiro.** Onde houver API pública (WordPress, PNCP, DOU, Salic, Transferegov, Mapas Culturais, Querido
   Diário), ela é a rota principal; a página é a alternativa.
4. **Ao menos duas rotas.** O mesmo edital sai em mais de um lugar (o diário oficial e o site da secretaria; o site da
   fundação e o portal do terceiro setor). Um motor com uma rota só fica cego quando ela muda.
5. **Nenhum motor é, por regra, a fonte original** (titular, 23/10/2026). Diários, portais e sites de divulgação
   divulgam; um portal (como o Prosas) tanto replica oportunidades de outros quanto tem as suas. O motor entrega o link
   onde encontrou (`link_divulgacao`) e, quando a tentativa cega acha um documento (`seguir_oficial`), o link
   candidato à origem (`link_oficial`). Original ou divulgação é decidido POR LIVRO, com evidência
   (`base/cartorio/origem.py`: o domínio do órgão ou do financiador do livro, o município, o Chrome, o Interceptador);
   a rede neural vincula e aprofunda. Dado incompleto é esperado: o Interceptador e o Chrome completam. Nos diários, a
   oportunidade original costuma estar no site da secretaria do município (a abordagem 11 do Interceptador).
6. **O motor extrai o necessário e a prova**: os dados da oportunidade, o link de divulgação, o link candidato à origem
   (quando houver) e o texto literal do que leu. Nada de informação de livro no motor: livro é do Cartório.
7. **O aprendizado mora dentro do motor.** Lições, bloqueios conhecidos, alternativas e rotas que falharam ficam em
   `[aprendizado]`; o estado vivo (assinaturas, leituras, previsão dos alvos, retornos) fica em `dados/motores/<id>.db`,
   escrito só pelo motor. Um motor nunca lê o aprendizado de outro; o que é comum fica na missão ou no canivete.
8. **A rede neural só aciona, prioriza e mede.** O motor não decide quando roda.
9. **Regras da titular que todo motor respeita:** o `robots.txt` é informação, e a espera que ele pede vira o intervalo
   do domínio; os dados públicos são captados íntegros, como publicados; nada é simulado (sem rota, o motor diz que não
   leu); o léxico comum da missão é herdado, não copiado.

## O motor modelo
Todo motor novo parte do **motor modelo** (`eldorado/base/motor_modelo/modelo.toml`), que fica no sistema base, não
roda e não aparece nos relatórios: uma configuração com **todas as ferramentas do sistema**, cada uma explicada.
`eldorado motor criar <id>` copia o modelo e preenche a identidade, os alvos e o aprendizado do estudo. **Ferramenta
nova implantada entra também no modelo** (o teste `testes/test_motor_modelo.py` falha enquanto faltar).

## O passo a passo

1. **A ficha.** `eldorado motor ficha <id>` mostra o que o estudo definiu: categoria, finalidade, motores reunidos,
   alvos (com os endereços reais) e o aprendizado do Eldorado0 (leituras, acertos, domínios, bloqueios, lições,
   melhorias recomendadas). É o ponto de partida; nada é copiado de lá, só aprendido.
2. **O esqueleto.** `eldorado motor criar <id>` escreve a configuração com a identidade, a finalidade, os nomes
   anteriores, os alvos, o aprendizado e a métrica preenchidos, e **as rotas candidatas comentadas** para você decidir.
3. **A sondagem.** Antes de escrever uma rota, confirme que ela responde: `eldorado sondar <endereços>` onde houver
   internet (o fluxo **Diagnóstico** do GitHub publica o resultado como anotação). Só entra rota que respondeu; a que
   recusa entra em `[aprendizado]`, com o erro.
4. **As rotas.** Escolha no canivete (abaixo) o tipo de cada `[[fonte]]`, a principal e a alternativa.
5. **O léxico em duas camadas.** `termos` e `vetos` decidem o que abrir (camada de direcionamento, nos títulos e links;
   `termos_em = "titulo"` em sites de notícias). A camada de contexto, no texto do documento, é da Pertinência e do
   Cartório. O léxico do motor é **próprio da fonte**.
6. **A leitura.** `documentos` (ler os PDFs), `paginas_dos_achados`, `seguir_oficial` (da divulgação ao documento
   oficial), `tabelas` (cronogramas). Programas permanentes (incentivos) usam `[programa]`, `[programa.normas]` e
   `[programa.extracao]`; a extração das normas vale só para o programa.
7. **A validação.** `eldorado motor validar <id>`: a configuração é aceita pelo registro, conforme o estudo (id e
   categoria), com ao menos duas rotas e métrica.
8. **O teste nas páginas gravadas.** Um teste com as respostas reais gravadas da sondagem, servidas localmente, prova o
   que o motor entrega (e o que ele veta). É o critério de pronto do plano.
9. **O registro.** Acrescente o motor em `config/modulos.toml` e o ponto de partida em `config/agenda.toml` (o Cérebro
   aprende a hora certa depois).
10. **A medição.** Nos 14 dias seguintes, a métrica da finalidade diz se o motor atinge: leu dentro da cadência e
    entregou ao menos um achado aceito; não atinge se ficou sem leitura além do dobro da cadência ou se todos os achados
    foram barrados.

## O canivete suíço (as ferramentas que todo motor usa sem escrever código)

### Acesso — a escada (`motores/acesso/`)
| Degrau | Para quê |
|---|---|
| `api` | APIs públicas e arquivos; cliente HTTP direto |
| `leve` | páginas que recusam robô: requisição com assinatura de navegador |
| `lightpanda`, `patchright`, `camoufox` | páginas que só existem com JavaScript ou que exigem navegador |
| `arquivo` | a cópia arquivada (Wayback) quando o site mudou ou saiu do ar |
| `local` | o computador da titular (IP do Brasil), para os domínios que recusam a nuvem |

**Navegador que não denuncia robôs (degraus 4 e 5).** Quando a lista da página só existe depois dos scripts (Prosas,
Mapa das OSC), ou quando o site barra robôs, o motor lê pela própria escada com um navegador real: o **Patchright**
(degrau 4, Chromium sem as marcas de automação) e o **Camoufox** (degrau 5, Firefox anti-detecção, de reserva). Ponha-os
primeiro na escada (`degraus = ["patchright", "camoufox", "leve", "api"]`), porque a escada só sobe quando o degrau de
baixo falha, e uma página que responde sem a lista não é falha. O navegador espera a rede ficar ociosa (os scripts
terminarem); `espera_seletor` espera um elemento específico. Os fluxos instalam os dois (`patchright install chromium` e
`python -m camoufox fetch`). Leia devagar (`intervalo_s` maior): o robots é informação, e a espera vira intervalo.

Use `exige_brasil = true` na fonte que só responde do Brasil; o degrau `local` resolve. A escada respeita o intervalo
de cada domínio e descansa o que bloqueia.

### Descoberta — as cinco formas (`motores/descoberta/`)
| Tipo de fonte | Quando |
|---|---|
| `api` (com `caminhos` em jmespath e `paginacao`) | API JSON própria do órgão (PNCP, Transferegov, diários com API) |
| `wordpress` | sites em WordPress: `/wp-json/wp/v2/...`, com `termos` na busca |
| `ckan` | portais de dados abertos |
| `feed` | RSS e Atom |
| `mapa` | o mapa do site (sitemap) |
| `pagina` | a página de editais, com os links extraídos; `seletor` para limitar a região |
| `cadeia` | a listagem em etapas: a lista → cada item → o detalhe (`[[fonte.cadeia]]` com elos `json`, `html` ou `atos`; `[fonte.pista]` monta a pista com os campos do último elo). Diários oficiais, tribunais, portais com sumário |
| `metabusca` | a busca restrita a um domínio ou tema, quando não há listagem |
| `wayback` | o histórico do endereço |

No endereço: `{hoje:%Y%m%d}`, `{hoje-1:%Y-%m-%d}`, `{hoje+500:...}`, `{pagina}` e as chaves de `valores`.

### Gravação das páginas reais
`eldorado gravar <endereços> --pasta testes/paginas/<motor>` (ou o fluxo **Gravar páginas**, no GitHub) grava as respostas
inteiras: é como se conhece a estrutura real da fonte antes de configurar, e é a base do teste nas páginas gravadas.

### Leitura (`motores/leitura/`)
Página, PDF (com tabelas), OCR, planilha, documento, compactado, normalização de datas e valores, expurgo de menus e
rodapés, e a reserva universal. **O recorte dos atos** (`leitura/atos.py`, o elo `atos` da cadeia) divide a edição inteira
de um diário em atos: o cabeçalho, o órgão acima dele, o começo e o texto integral; o texto do ato vai na pista (`texto`) e
é o documento, sem baixar de novo a edição. Quando o título engana (um "EDITAL Nº" de licença ambiental), use
`termos_em = "tudo"` e ponha o começo do ato no resumo, para os vetos o verem. O motor entrega o **texto literal**; o sistema nunca recebe binário. Documentos com
padrão de injeção de instruções são marcados e reprovados.

### Alvos (`[[alvo]]`)
`id` (o do estudo), `nome`, `enderecos` (o primeiro é a rota; os outros, alternativas), `orgao`, `previsao_meses`. O
alvo é lido na janela prevista; quando muda, o motor registra o mês (a previsão se aprende) e entrega os links que
passam no léxico, ou a própria página.

### Programas e normas (`[programa]`)
Para os mecanismos permanentes (leis de incentivo, fundos): o livro do programa, as normas mais recentes da página de
legislação e a extração própria do texto normativo.

### O canivete de cada achado (o motor padrão, `[canivete]`)
Todo motor nasce com a caixa de ferramentas ligada: depois de ler o documento ou a página de cada achado, o canivete
(`leitura/enriquecer.py`) extrai o **idioma** (lingua), a **data de publicação** (htmldate), as **datas citadas com o
trecho**, marcando as de prazo (datefinder, dateparser), os **valores em reais** com o trecho (price-parser), os
**metadados estruturados** (extruct: JSON-LD, microdata, Open Graph) e o **texto principal** sem menus e rodapés
(trafilatura, que substitui o texto da página no documento). Vai para `dados.canivete`. Um motor desliga o que não fizer
sentido: `[canivete] valores = false`. A leitura padrão já traz o OCR (imagens e PDFs escaneados) e o leitor universal.

### O mapa do site original (todo motor, sem configuração)
Com o histórico do livro, ele tem um site de divulgação e um site original (a origem confirmada). A rede neural pede ao
motor do livro `vigiar_original(livro)`: o motor lê os mapas do domínio original (o robots.txt, o sitemap.xml, o índice e
o mapa do WordPress, por `descoberta/mapa_original.py`), compara com o que já viu daquele domínio (no estado do motor:
domínios e URLs, nunca livros) e entrega as URLs novas que têm a ver com o livro (o número do edital, as palavras próprias
do título, os arquivos). Na primeira visita, só o relevante e recente; cada domínio, no máximo uma vez por semana. No livro
arquivado, a novidade é a próxima oportunidade, que volta pela recepção.

### Pilotos e IA
O motor não chama IA. O que o motor não alcança é do **Espião**; o que falta num livro é do **Interceptador**, acionado
pela rede neural. A IA propõe; o sistema valida.

## A anatomia da configuração

```toml
[motor]           # id (o do estudo), nome, categoria, categoria_estudo, finalidade, tipo_finalidade, uf, orgao,
                  # nomes_anteriores (os motores reunidos)
[[fonte]]         # nome, url, tipo, papel (principal | alternativa), exige_brasil, termos, caminhos, paginacao...
[[alvo]]          # id, nome, enderecos, orgao, previsao_meses
[acesso]          # degraus, intervalo_s
[leitura]         # documentos, paginas_dos_achados, seguir_oficial, tabelas, max_documentos
[lexico]          # termos, vetos, termos_em
[programa]        # (só para mecanismos permanentes) e [programa.normas], [programa.extracao]
[legislacao]      # as leis que regem a oportunidade
[aprendizado]     # licoes, bloqueios_conhecidos, alternativas_para_bloqueio, rotas_que_falharam
[metrica]         # cadencia_h, periodo_dias
```

## Motores de destino especial (a base de empresas)

Um motor que alimenta a base Especial (empresas e incentivos), e não a Biblioteca, declara `destino = "especial"` e o mapa
`[especial]` (ou `[fonte.especial]`, por fonte): `cnpj`, `razao_social`, `uf`, `atividade_principal`, `tipo_pessoa` e
`incentivo = { lei, ano, valor }`, com os campos do item entre chaves. A Regência desvia esses registros para
`base/especial/registro.py`, que valida o CNPJ (os dígitos verificadores; a raiz de 8 dígitos casa com a empresa
conhecida), grava a empresa sem perder o que já se sabia e não duplica o incentivo da mesma fonte. As regras do banco
valem: a lei é uma de FIA, Idoso, Esporte, Rouanet, Pronas, Pronon, Goyazes, ICMS, PAT ou outra; pessoa física fica fora.
Para tabelas em PDF, o elo `linhas` reconhece cada registro por um padrão com grupos nomeados.

## Lições da criação dos primeiros motores (23/10/2026)

- **do-goias**: a fonte certa era uma cadeia de três elos (edições do dia → sumário em árvore → texto da matéria); o motor
  antigo inventava caminhos e ficou um mês sem ler, com a auditoria dizendo "funcionando". Grave antes de configurar.
- **do-goiania**: a maior parte dos "EDITAL Nº" do diário são avisos de licença ambiental; o Querido Diário deve ser
  consultado pelo código do município (o nome mistura cidades vizinhas); a lista oficial responde da nuvem.
- **prefeituras-50-go**: a sondagem mudou o aprendizado (23 das 25 cidades respondem da nuvem; o registro antigo dizia
  17 só pelo Brasil). Aprendizado se confere, não se herda.
- **novo-diarios-municipais-go**: a busca da AGM não devolve nada sem sessão, mas a página inicial aponta o PDF da edição
  do dia; o Querido Diário tem texto completo de só 2 municípios de Goiás. O recorte dos atos leva o município adiante
  (`campos = {{ localidade = '<regex>' }}` no elo `atos`). Num TOML, a string literal ('…') não interpreta a barra
  invertida: escreva o regex com UMA barra.
- **empresas-editais-incentivados**: nos portais do gov.br, os menus trazem centenas de links; use `seletor = "#content"`
  (o seletor limita a vigilância e os links à região do conteúdo). O canal deste motor são os mecanismos de incentivo,
  não os sites institucionais das empresas (nenhum edital neles, no Eldorado0).
- **Teste com links absolutos**: se a página real usa links com o domínio da fonte, o servidor do teste troca o domínio
  dentro da página também (a extração só aceita links do mesmo domínio).
- **motor-gife**: confira os padrões funcionando sobre os dados reais (499 das 500 linhas do PDF), não só a validação;
  as regras do banco (a lei do incentivo, quem descobriu a empresa) aparecem no teste, não antes.
- **cnpq-extensao, site-funarte, novo-bancos-publicos**: rode o motor nas páginas gravadas e OLHE o que ele entrega antes de
  escrever as conferências; "nenhuma entrega" pode ser o certo (as 4 chamadas abertas do CNPq eram para pesquisadores).
  O servidor comum das páginas gravadas está em `testes/paginas_servidor.py`. Várias gravações seguidas: a fila do GitHub
  cancela a que estava esperando; acione uma de cada vez, ou confira o índice depois.
- **mptgo-destinacao**: a tabela que carrega por script costuma vir de um POST na sessão da página (Joomla, tabelas
  dinâmicas): procure no código da página o endereço e os campos; a cadeia abre a sessão (elo `html` com o código) e
  pede a tabela (elo com `corpo`). Confirme com `eldorado motor experimentar <id>` (o fluxo Experimentar motor), que roda
  o motor inteiro com a internet de verdade.
- **mpu-destinacao, mpgo-destinacao**: o cadastro antigo trazia endereços de alvo trocados (o alvo do MP-GO apontava o MPF
  e o MPT; o do FDD, o CONANDA): confira cada endereço de alvo antes de vigiar. Alvo em portal grande leva `seletor` (os
  menus entram como links e casam com palavras soltas do léxico, como "projetos"). Nos portais Plone, cada documento tem
  o link do ícone e o do título para o mesmo endereço: a extração guarda o do título.
- **Judiciário (diagnóstico)**: o zero do Eldorado0 no TJ-GO era bloqueio da nuvem, não fonte errada; diagnostique antes
  de reconstruir. Prefira o endereço de busca confirmado na sondagem (o CNJ responde diferente em /search/ e em /?s=).
  Vetos de palavra curta casam dentro de outras ("curso" em "recursos"): use a palavra inteira, `(^| )curso( |$)`.
  Numa string comum do TOML ("…"), a barra invertida é escape: use classes como `[a-z]*` no lugar de `\w*`.
- **outros-agregadores**: páginas avulsas de editais (achadas uma a uma) não são canal: viram livros, e o site original
  é vigiado pelo mapa do site. Agregador costuma misturar licitações com oportunidades: procure a área própria de
  oportunidades. No teste local, páginas de domínios diferentes com o mesmo caminho (todas as "/") se sobrepõem no
  servidor de teste: leia o arquivo gravado direto, ou use o experimento real.
- **Teste com página real**: página montada à mão costuma ser "HTML quase vazio", que a escada trata como bloqueio; use a
  página real gravada, alterando o mínimo.

## Bloqueios

1. Registre o bloqueio em `[aprendizado]` (domínio, erro, data).
2. Tente, nesta ordem: a API do mesmo órgão; a página com o degrau `leve`; o degrau de navegador; a cópia arquivada; o
   computador da titular (`local`); outra rota do mesmo edital (o diário oficial, o Querido Diário, o portal federal).
3. O `robots.txt` é informação (regra da titular): a proibição fica registrada no aprendizado e a espera que ele pede
   vira o intervalo do domínio; o motor lê devagar, sem insistir em quem recusa (403, 429), e não trata o robots como
   bloqueio.

## Pronto quando

- `eldorado motor validar <id>` passa;
- o teste nas páginas gravadas passa (o que entrega e o que veta);
- o motor está em `config/modulos.toml`;
- nos 14 dias seguintes, a métrica da finalidade diz que ele atinge.
