# Parecer do conselho — Motor 01 · Diário Oficial do Município de Goiânia

**Data:** 01/10/2026 · **Motor:** `do-goiania` (Bússola, posição 01) · **Matéria:** técnica (engenharia de coleta), com reflexo jurídico (MROSC, fundos, PNAB)

## 1. Síntese

O motor 01 rodou 43 vezes e não achou nada. A causa não foi falta de edital. O motor estava construído para ler a fonte de um jeito que nunca poderia dar certo:

1. Ele lia o **texto dos links** de uma página. O Diário de Goiânia publica **um PDF por dia**, com cerca de 240 páginas, e o link diz apenas "Edição nº 8871 de 25 de setembro de 2026". O chamamento fica **dentro** do PDF.
2. O endereço configurado (`/diario-oficial/`) leva à **Carta de Serviços**, não ao Diário. A lista real das edições está em outro endereço (`lista_diarios.asp?ano=AAAA`).
3. Na nuvem, o motor nem tentava ler: o portal recusa IP estrangeiro, e a coleta local nunca foi executada (`ultima_coleta_local_br = null`).
4. O **Querido Diário já cobre Goiânia**, e a base tinha **232 edições** de Goiânia vindas dele. Todas eram descartadas pelo painel com a regra "edição de diário não é oportunidade", sem que ninguém abrisse o ato.

Dentro dessas edições descartadas estava um edital aberto: **SEGENP — Chamamento Público nº 001/2026, "Natal no Parque – A Magia de Brincar"**. É um termo de colaboração com OSC, valor máximo de **R$ 5.000.000,00** e protocolo único **até 26/10/2026, às 23h59**. O conselho conferiu o texto direto no PDF oficial da edição nº 8871 (25/09/2026).

**Decisão do neutro:** o motor foi refeito. Agora ele lê o **texto integral** das edições, divide cada edição em **atos** e classifica cada ato de forma determinística, sem IA e sem custo. A coleta local deixa de ser condição para o motor funcionar e passa a ser reforço do dia.

## 2. O que foi examinado

| Fonte | O que mostrou |
|---|---|
| `config/sensores.json`, `config/rotas_motores.json`, `config/agenda_motores.json` | URLs, léxicos (14 termos na camada 1, 12 na camada 2, 12 vetos), agenda 08:23 seg–sex, coleta "local" |
| `src/sensores.py` (função `ler`) | o motor lê só rótulos de `<a>`; na nuvem, devolve "aguardando coleta local" sem ler nada |
| `estado/esquadra.json` | 43 leituras, 43 vazias seguidas, 0 páginas lidas |
| `dados/oportunidades/oportunidades.jsonl` | 268 registros do Querido Diário com "goiânia" no título: 232 de Goiânia e **36 de Aparecida de Goiânia**, misturados |
| `src/achados_motores.py` | a regra especial do motor 01 contava esses 268 registros e depois descartava todos: 268 → 0 |
| `estado/ultima_rmg.json` | o coletor metropolitano falhou **147 de 147 consultas**, todas registradas como "sem resposta das bases", sem dizer o erro |
| Portal da Prefeitura, inspecionado pelo navegador do titular (IP brasileiro) em 01/10 | lista de 2026 com 187 edições, incluindo as Edições Extras; endereço fixo de cada PDF; o PDF da edição 8871 tem 9,3 MB, 238 páginas e camada de texto; duas rotas de secretaria davam **404** |

## 3. Parametrização encontrada × parametrização nova

| Item | Antes | Agora |
|---|---|---|
| Leitura | rótulo do link | texto integral da edição → atos |
| Fonte na nuvem | nenhuma (pulava) | Querido Diário, território IBGE 5208707 |
| Fonte local | Carta de Serviços (endereço errado) | lista oficial do ano + PDF do dia (`do_AAAAMMDD_NNNNNNNNN.pdf`) |
| Consultas | 2 nacionais, sem território | 10 dirigidas a Goiânia: MROSC, CMDCA/FMDCA, CMAS/FMAS, idoso, PNAB/Aldir Blanc, subvenção e emenda, inexigibilidade, entidades sem fins lucrativos |
| Sintaxe | `OR` (não é operador no Querido Diário) | `|` = OU, `+` = E |
| Janela | 5 dias | 15 dias (o atraso medido do Querido Diário foi de 2 a 16 dias, mediana de 5,5) |
| Trecho | 1 trecho de 400 caracteres | 3 trechos de 1.500 + texto integral (até 8 edições por execução) |
| Território | "goiânia" no título (pegava Aparecida) | `territory_id == 5208707` |
| Agenda | 08:23 seg–sex, só local | 07:41 todos os dias na nuvem + coleta local quando houver |
| Rotas | 4 rotas, 2 com erro 404 | 4 rotas verificadas em 01/10 |

## 4. Como cada ato é classificado

| Dimensão | Valores | Exemplo real |
|---|---|---|
| **Tipo** (decidido pelo cabeçalho, não pelo timbre) | abertura · retificação · andamento/resultado · celebração · normativo · referência · composição de conselho | "EDITAL DE DIVULGAÇÃO DO RESULTADO FINAL… PNAB 006/2026" → andamento |
| **Regime** | MROSC · fundo/conselho · PNAB/cultura · credenciamento · Organização Social da saúde | "Lei nº 8.411/2006… qualificado como Organização Social" → OS da saúde |
| **Público** | OSC · OSC e pessoa física · pessoa física · empresa | credenciamento SMS "PESSOA FÍSICA" → pessoa física |
| **Órgão** | CMDCA/FMDCA, CMAS/FMAS, CMI/FMI, SECULT, SEDHS, SEGENP, SME, SMS, Esportes, Relações Institucionais, Câmara | timbre "Secretaria Municipal de Gestão de Negócios e Parcerias" → SEGENP |
| **Prazo** | período "de X a Y" → Y; "até dd/mm/aaaa"; datas por extenso | "25 de setembro de 2026 a 26 de outubro de 2026" → 2026-10-26 |

**Vereditos:**

- **OPORTUNIDADE**: abertura ou retificação de seleção para OSC, em regime de interesse, com prazo não vencido. Entra na base como `capturada` e segue o fluxo normal (completude → confirmação → Farol).
- **ACOMPANHAR**: resultado, recurso, homologação, extrato de termo, inexigibilidade, vaga da sociedade civil em conselho, ou edital sem prazo publicado há mais de 60 dias. Vale como inteligência: mostra quem venceu, quanto recebeu, qual órgão faz parceria direta e quando o fundo costuma abrir.
- **RUÍDO**: credenciamento de prestadores (Lei 8.666, art. 25 / Lei 14.133, art. 79), Organização Social da saúde, decretos e portarias sem seleção.

**Calibração nas 232 edições já existentes:** 1 OPORTUNIDADE (o edital da SEGENP), 80 ACOMPANHAR e 151 RUÍDO. Antes, o resultado era zero de 232.

## 5. Conselho de 7 lentes

Os conselheiros são arquétipos sorteados para esta análise, não pessoas reais.

**1. Extremamente pessimista — chief engineer de infraestrutura de dados, 25 anos em pipelines de missão crítica, cético por ofício.**
O motor ficou cego por quatro semanas e o painel o mostrava como "lendo sem achar". Isso é pior do que mostrar "quebrado": o sistema mentiu por omissão. E o mesmo padrão pode se repetir. O coletor metropolitano falhou 147 de 147 consultas e ninguém percebeu, porque o erro era gravado como frase genérica. O Querido Diário é de terceiros: se mudar a API ou atrasar 16 dias, o motor volta a ficar cego. Exijo três coisas: erro descrito, alarme por ausência e uma segunda fonte que não dependa do Querido Diário.

**2. Pessimista — staff engineer de busca e relevância, obcecado por falso positivo.**
A classificação por expressão regular é frágil. O timbre do órgão vem antes do cabeçalho, o PDF quebra linhas no meio da frase e o mesmo edital repete o título duas vezes. A calibração em 232 trechos é amostra pequena, e os trechos do Querido Diário são fragmentos, não o ato inteiro. Riscos concretos:

- o anexo "minuta do termo de colaboração" vira um segundo ato;
- um edital de 69 mil caracteres é truncado em 7 mil;
- edital com prazo escrito de forma incomum ("no prazo de 30 dias da publicação") fica sem data e cai em ACOMPANHAR depois de 60 dias.

**3. Levemente pessimista — professor de engenharia de computação, especialista em extração de documentos.**
O PDF oficial tem 395 imagens para 238 páginas. Parte do Diário pode ser digitalizada, sem texto, e o pypdf não lê imagem. O Querido Diário faz o próprio OCR, o que é um ponto a favor dele. Mas o texto dele pode chegar com caracteres trocados (já aparecem "jus�fica�va" e "Ins�tucionais" na base). O classificador precisa tolerar isso. Ele tolera em parte, porque compara sem acento, mas não corrige caractere perdido.

**4. Neutro — CTO de plataforma pública de dados, mediador.** O voto está na seção 6.

**5. Levemente otimista — professor de ciência da computação, especialista em sistemas determinísticos explicáveis.**
A escolha certa foi não usar IA nesta etapa. Cada veredito traz o motivo escrito ("credenciamento de prestadores — Lei 8.666 art. 25"), e isso pode ser auditado pelo titular, que é advogado. O recorte pelo cabeçalho em caixa alta é a regularidade mais forte do Diário de Goiânia: no PDF de 25/09, 184 linhas começavam com cabeçalho de ato.

**6. Otimista — staff engineer de produto, foco em valor entregue.**
A melhoria não é marginal. O motor sai de zero para a fonte mais próxima da associação. A categoria ACOMPANHAR vale tanto quanto OPORTUNIDADE para captação: os extratos de termo de fomento e as justificativas de inexigibilidade mostram quais secretarias fazem parceria direta com OSC, com valores e entidades. A Secretaria dos Esportes e a de Relações Institucionais aparecem repetidamente, o que é sinal de emendas e parcerias diretas que um edital nunca mostraria.

**7. Extremamente otimista — CTO de big tech com pós-doutorado em Python, visionário.**
O mesmo leitor serve aos 21 municípios da Região Metropolitana sem custo: basta trocar o código IBGE. Com os atos classificados por cinco anos, o sistema passa a **prever** a abertura dos fundos. O CMDCA abriu edital em abril de 2023 e julgou recurso em julho, e a PNAB fecha ciclo entre agosto e dezembro. A Bússola pode avisar a associação 30 dias antes, que é a antecedência mínima do art. 26 da Lei 13.019/2014, e não só depois que o edital sai.

## 6. Voto do neutro (vinculante)

**Decisão:** aprovar o motor 01 versão 2 e publicar, com os parâmetros e as mitigações abaixo.

**Parâmetros de qualidade (medidos a cada 30 dias, em `estado/diario_goiania.json`):**

| Indicador | Meta |
|---|---|
| Edições de dias úteis lidas (Querido Diário ou portal) | ≥ 90% |
| Atraso entre publicação e leitura | ≤ 7 dias na nuvem; ≤ 1 dia com coleta local |
| Precisão de OPORTUNIDADE (conferida pelo titular) | ≥ 80%; abaixo disso, a regra que errou é corrigida e ganha teste |
| Falha de consulta com causa descrita | 100% (nenhuma "sem resposta" genérica) |
| CPF em trecho gravado | 0 |

**Mitigação de riscos:**

1. **Dependência do Querido Diário:** a coleta local lê o PDF oficial do dia pelo endereço fixo. Se o Querido Diário falhar, o diagnóstico mostra o erro exato e o painel acusa falha, em vez de "lendo sem achar".
2. **Título repetido do edital:** quando o cabeçalho curto é seguido de outro cabeçalho do mesmo tipo, os dois são unidos (teste com o layout real da edição 8871).
3. **Timbre antes do cabeçalho:** o tipo do ato é decidido pela primeira palavra de ato em caixa alta, não pela primeira linha.
4. **Edital antigo sem prazo:** fica em ACOMPANHAR com o aviso "conferir se ainda está aberto". Nada é tratado como aberto sem prova.
5. **Fragmento do Querido Diário:** sempre que possível, lê o texto integral (`txt_url`); o fragmento é só o recurso de reserva.
6. **Dado pessoal:** CPF, inteiro ou parcialmente mascarado, vira `[CPF]` antes de gravar. O texto integral fica em `estado/edicoes/` (fora do Git).
7. **Injeção de instrução:** ato suspeito vai para `estado/quarentena.jsonl` e não entra na base.

## 7. Melhorias aplicadas

| # | Melhoria | Arquivo |
|---|---|---|
| M1 | Novo leitor do motor 01: Querido Diário + PDF oficial → atos → classificação | `src/diario_goiania.py` |
| M2 | `sensores.ler` passa o motor 01 para o novo leitor, antes do bloqueio "exige Brasil" | `src/sensores.py` |
| M3 | Parâmetros do motor em arquivo próprio: consultas, janela, limites, padrão da edição | `config/diario_goiania.json` |
| M4 | URLs reais (lista oficial e Querido Diário), no lugar da Carta de Serviços | `config/sensores.json` |
| M5 | Rotas sem 404 (Cultura e Conselhos verificados em 01/10), léxico e vetos ampliados | `config/rotas_motores.json` |
| M6 | Agenda na nuvem todo dia às 07:41; coleta "nuvem + local" | `config/agenda_motores.json` |
| M7 | O painel conta os atos do motor, não as edições, e Aparecida de Goiânia deixa de entrar | `src/achados_motores.py` |
| M8 | Coletor metropolitano: tempo limite de 60 s e erro descrito; sintaxe `|` em vez de `OR` | `src/rmg_diarios.py`, `config/municipios_rmg.json` |
| M9 | Auditorias deixam de marcar o motor 01 como "bloqueado/coleta local" | `src/auditoria_29.py`, `src/auditoria_motores.py`, `scripts/descricao_motores.py` |
| M10 | 15 testes, incluindo o layout real da edição 8871 e o veto ao credenciamento | `tests/test_motor01_diario_goiania.py` |

## 8. Oportunidade encontrada, para decisão do titular

**SEGENP — Edital de Chamamento Público nº 001/2026, "Natal no Parque – A Magia de Brincar"** (Diário Oficial nº 8871, 25/09/2026)

- **Regime:** Lei 13.019/2014, IN 05/2020 do TCM-GO, Decreto Federal 8.726/2016 (subsidiário).
- **Objeto:** termo de colaboração com OSC para planejamento, coordenação, produção executiva, cenografia de grande porte, infraestrutura temporária e animação itinerante no Parque Mutirama.
- **Valor máximo:** R$ 5.000.000,00, com recurso municipal.
- **Protocolo único:** de 25/09/2026 a 26/10/2026, às 23h59, somente por e-mail. Os arquivos serão abertos em 27/10/2026, às 09h00.
- **Atenção do conselho:** o objeto é produção de evento de grande porte. A associação só deve concorrer se o estatuto e a experiência comprovada cobrirem cultura e eventos. Essa é uma decisão de negócio do titular.

## 9. Pendências declaradas

1. **Confirmar na primeira execução da nuvem** que as 10 consultas com `|` e `+` voltam resultados. O ambiente desta análise não alcança a API do Querido Diário, e a sintaxe foi aplicada conforme a documentação pública dele.
2. **Mostrar os atos ACOMPANHAR no cartão do motor.** Os dados já ficam em `estado/diario_goiania.json`; falta o bloco visual, que depende da identidade visual definitiva (`config/identidade_visual.json`).
3. **Previsão de abertura dos fundos** (CMDCA, CMAS, PNAB) a partir do histórico de atos classificados.
4. **Estender o leitor aos 21 municípios da Região Metropolitana**, trocando apenas o código IBGE.
