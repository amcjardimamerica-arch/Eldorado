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
5. **O portal entrega pista; a fonte oficial entrega a prova.** Motor de portal que reúne editais de terceiros segue até
   o documento oficial (`seguir_oficial`), e o link oficial é o do órgão, não o do portal.
6. **O motor extrai o necessário e a prova**: os dados da oportunidade, o link de divulgação, o link oficial e o texto
   literal do documento. Nada de informação de livro no motor: livro é do Cartório.
7. **O aprendizado mora dentro do motor.** Lições, bloqueios conhecidos, alternativas e rotas que falharam ficam em
   `[aprendizado]`; o estado vivo (assinaturas, leituras, previsão dos alvos, retornos) fica em `dados/motores/<id>.db`,
   escrito só pelo motor. Um motor nunca lê o aprendizado de outro; o que é comum fica na missão ou no canivete.
8. **A rede neural só aciona, prioriza e mede.** O motor não decide quando roda.
9. **Regras da titular que todo motor respeita:** o `robots.txt` é informação, e a espera que ele pede vira o intervalo
   do domínio; os dados públicos são captados íntegros, como publicados; nada é simulado (sem rota, o motor diz que não
   leu); o léxico comum da missão é herdado, não copiado.

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
| `metabusca` | a busca restrita a um domínio ou tema, quando não há listagem |
| `wayback` | o histórico do endereço |

No endereço: `{hoje:%Y%m%d}`, `{hoje-1:%Y-%m-%d}`, `{hoje+500:...}`, `{pagina}` e as chaves de `valores`.

### Leitura (`motores/leitura/`)
Página, PDF (com tabelas), OCR, planilha, documento, compactado, normalização de datas e valores, expurgo de menus e
rodapés, e a reserva universal. O motor entrega o **texto literal**; o sistema nunca recebe binário. Documentos com
padrão de injeção de instruções são marcados e reprovados.

### Alvos (`[[alvo]]`)
`id` (o do estudo), `nome`, `enderecos` (o primeiro é a rota; os outros, alternativas), `orgao`, `previsao_meses`. O
alvo é lido na janela prevista; quando muda, o motor registra o mês (a previsão se aprende) e entrega os links que
passam no léxico, ou a própria página.

### Programas e normas (`[programa]`)
Para os mecanismos permanentes (leis de incentivo, fundos): o livro do programa, as normas mais recentes da página de
legislação e a extração própria do texto normativo.

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

## Bloqueios

1. Registre o bloqueio em `[aprendizado]` (domínio, erro, data).
2. Tente, nesta ordem: a API do mesmo órgão; a página com o degrau `leve`; o degrau de navegador; a cópia arquivada; o
   computador da titular (`local`); outra rota do mesmo edital (o diário oficial, o Querido Diário, o portal federal).
3. Se o `robots.txt` proíbe, a informação fica registrada e a fonte vai para a coleta assistida; o motor não insiste.

## Pronto quando

- `eldorado motor validar <id>` passa;
- o teste nas páginas gravadas passa (o que entrega e o que veta);
- o motor está em `config/modulos.toml`;
- nos 14 dias seguintes, a métrica da finalidade diz que ele atinge.
