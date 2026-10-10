# ETAPA 2: melhorias dos motores que encontraram as oportunidades da Parte 3

Base: as 300 oportunidades da Parte 3 (Brasil, privadas e sem nível, abertas) depois das 3 passadas, mais as 23 derivadas. Cada oportunidade foi atribuída ao motor que a trouxe (campo `fonte_nome`). "Útil" quer dizer oportunidade vigente com estrela certificada no documento oficial (ouro, prata ou bronze). "Precisão" é a fração de úteis sobre tudo o que o motor trouxe.

## 1. Resultado em uma linha
Os motores trouxeram 300 registros. Só 20 viraram oportunidade vigente certificada (6,7%), e 182 eram ruído, duplicata ou fora do perfil (61%). Outros 57 já estavam encerrados, 43 deles já fechados no dia em que foram coletados. As páginas-catálogo descartadas como ruído escondiam 23 oportunidades que nenhum motor registrou, e 6 delas estão vigentes e certificadas, 3 em ouro.

## 2. Indicadores por motor

| Motor (fonte) | Trouxe | Úteis (ouro/prata/bronze) | Precisão | Pendentes | Encerradas | Ruído | Duplicatas | Fora do perfil | Nível/UF a corrigir |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| Piloto - Espião — busca aberta no terceiro setor | 103 | 11 (1/5/5) | 11% | 27 | 29 | 26 | 8 | 2 | 60 |
| Motor do Piloto — busca aberta no terceiro setor | 81 | 0 (0/0/0) | 0% | 1 | 13 | 25 | 42 | 0 | 34 |
| ABCR — Associação Brasileira de Captadores | 29 | 4 (2/2/0) | 14% | 0 | 2 | 16 | 6 | 1 | 3 |
| Busca de empresas para FIA, Idoso, Lei de Incentivo ao Esporte, Pronas, Pronon e Goyazes | 26 | 2 (0/2/0) | 8% | 4 | 3 | 10 | 5 | 2 | 6 |
| Observatório do Terceiro Setor — editais | 24 | 2 (1/1/0) | 8% | 5 | 4 | 7 | 4 | 2 | 2 |
| Secult Goiás — Goyazes e Aldir Blanc | 13 | 1 (0/0/1) | 8% | 0 | 1 | 9 | 1 | 1 | 13 |
| Bússola Social - Bússola Editais | 4 | 0 (0/0/0) | 0% | 0 | 0 | 4 | 0 | 0 | 0 |
| Agência do Bem / Rede do Bem — Edital de Microprojetos | 4 | 0 (0/0/0) | 0% | 0 | 3 | 1 | 0 | 0 | 0 |
| SALIC — Lei Rouanet (Ministério da Cultura) | 3 | 0 (0/0/0) | 0% | 0 | 0 | 3 | 0 | 0 | 3 |
| TJGO - penas pecuniárias 1ª Vara de Execução Penal de Goiânia | 2 | 0 (0/0/0) | 0% | 1 | 0 | 1 | 0 | 0 | 1 |
| Mapa das OSC - área de editais | 2 | 0 (0/0/0) | 0% | 0 | 0 | 2 | 0 | 0 | 2 |
| Instituto Sabin | 2 | 0 (0/0/0) | 0% | 0 | 0 | 2 | 0 | 0 | 0 |
| Outros 7 motores com 1 registro cada | 7 | 0 | 0% | 0 | 2 | 4 | 1 | 0 | 3 |

## 3. Pontos de acerto (manter)

| Motor | O que acertou | Evidência |
|---|---|---|
| ABCR | Melhor razão de ouro: 2 dos 4 ouros do sistema. Os prazos que o motor trouxe batiam com o documento oficial (2 de 2). | CONANDA/FNCA, R$ 6 milhões, fecha 11/10; Zurich, até 19/10; Maria Emília, até R$ 1 milhão; BNDES Periferias, até 04/12. |
| Piloto, Espião | Único motor que chega aos chamamentos municipais e de conselhos de fora de Goiás. Com 11 úteis, é o que mais produziu em número absoluto. | CRA-RS (ouro); Iguatu/CE, OS de saúde, R$ 45,1 milhões; Senador Pompeu/CE; Itagibá/BA; Ielmo Marinho/RN; Nova Independência/SP; Baobá Marielle Franco; Fundo Brasil Emergencial; ContraFluxo. |
| Observatório do Terceiro Setor | Acha os grandes editais corporativos. | Grupo Equatorial, R$ 61 milhões (ouro); Karibu Foundation. |
| Busca de empresas (FIA, Idoso, Esporte e outras) | Acha editais de institutos regionais e religiosos. | Instituto Genésio (SC); CNBB/FNS, até R$ 50 mil. |
| Todos | Os títulos das notícias costumam ter objeto e valor corretos, e servem como boa pista para chegar ao documento. | Os 20 úteis têm título coerente com o edital oficial. |

## 4. Pontos de erro (corrigir)

### 4.1 Erros comuns a todos os motores
| Código | Erro | Tamanho na Parte 3 | Consequência |
|---|---|---|---|
| E1 | Campos centrais vazios na coleta | `uf` vazio em 295 de 300; `fim` vazio em 294; `valor_texto` vazio em 272; `nivel` vazio em 31 | O sistema não sabe se a oportunidade está aberta, de onde é nem quanto vale. Tudo vira "possível" (294) e vai para revisão manual. |
| E2 | Nível e UF errados | 18 registros de **Goiás** (Secult GO e outros) caíram na Parte 3 em vez da Parte 1. Mais de 120 registros públicos (prefeituras, ministérios, conselhos, Ibama, BNDES) foram rotulados como "privada" ou ficaram sem nível. | Oportunidades de Goiás aparecem na fila errada, e as partes 1 e 2 deixam de vê-las. |
| E3 | URL não normalizada | 61 links envelopados pelo DuckDuckGo (`duckduckgo.com/l?uddg=`) no Motor do Piloto. 38 duplicatas têm exatamente a mesma URL real. | 67 duplicatas (22% da Parte 3): 49 dentro do mesmo motor e 18 entre motores. |
| E4 | Página-catálogo ou home registrada como oportunidade | 110 ruídos: catálogos do CapitaAI (`/editais-abertos/...`), homes de agregadores, rótulos de blog (`/search/label`), seções de categoria, vagas de emprego, notícias de resultado, leis e artigos do tipo "como conseguir". | Ruído no painel. As oportunidades reais dentro dos catálogos se perdem (23 derivadas). |
| E5 | Sem filtro de prazo na coleta | 57 encerradas; 43 já estavam vencidas quando foram coletadas; mediana de 112 dias entre o fim do prazo e a coleta; a pior chegou a 747 dias. | Trabalho de leitura gasto em oportunidade morta. |
| E6 | Agregador tratado como verdade | 58 registros com divergência entre agregador e documento oficial. Exemplos: CapitaAI dá R$ 12 mil para Lagoa do Ouro, e o oficial é R$ 1.248.104,44; R$ 150 mil para Planaltina, e o oficial no PNCP é R$ 30 mil; vários "fluxo contínuo" que têm prazo; a ABCR mantinha o prazo antigo do CONANDA (17/09), já retificado para 11/10. | Valor e prazo errados chegam à titular. |
| E7 | Perfil OSC não verificado | 8 registros fora do perfil: pessoa física (FAPESB, Festival Ubuntu, Favela Lab, Conta que soma, palestrantes FIFE), empresas produtoras (FSA) e escolas ou estudantes (Liga STEAM). | Sugestões em que a OSC não pode se inscrever. |
| E8 | Fontes oficiais ilegíveis pela automação | 41 pendentes após 3 passadas: robots.txt 11, site com erro 10, DOU 8, JavaScript 5, PNCP em PDF binário 2, URL longa 1, sem documento 4. | Oportunidade possivelmente aberta, mas sem certidão. |

### 4.2 Erros e correções por motor
**Motor do Piloto (busca aberta), 81 registros, 0 úteis.**
- Erro: guarda o link do buscador em vez do destino (61 links do DuckDuckGo).
- Erro: guarda homes e catálogos (CapitaAI, AltEditais, Prosas, Mapa das OSC, Vagas Terceiro Setor, Substack).
- Erro: repete a mesma página em várias buscas (42 duplicatas).
- Correção: decodificar `uddg` e normalizar a URL; descartar homes e catálogos ou expandi-los em derivadas (M2); deduplicar antes de gravar (M1).
- Se a precisão continuar em 0%, rebaixar o motor a "fonte de pistas": ele alimenta o expansor de catálogos e não grava oportunidades.

**Piloto, Espião (busca aberta), 103 registros, 11 úteis, 27 pendentes.**
- Acerto: as páginas individuais do CapitaAI levam aos chamamentos municipais.
- Erro: grava sem UF e sem nível (60 a corrigir, quase todos municipais).
- Erro: grava catálogos temáticos do CapitaAI (`/editais-abertos/<tema>-para-ong`) e rótulos de blog.
- Erro: não extrai o prazo, e 29 registros já estavam encerrados.
- Correção: extrair do CapitaAI o número de controle do PNCP (`CNPJ-1-SEQ/ANO`) ou o link do PNCP e consultar a API oficial (M6), que certifica objeto, prazo, valor, órgão e território sem ler PDF. Inferir UF e nível pelo nome do órgão (M5). Aplicar o filtro de prazo (M4).

**ABCR (captadores.org.br), 29 registros, 4 úteis (2 ouro).**
- Acerto: as notícias de edital levam ao financiador.
- Erro: grava vagas de emprego, eventos, webinars e páginas de categoria (16 ruídos), e repete a mesma notícia (6 duplicatas).
- Correção: ler só `/editais/<slug>`; excluir `/category/`, `/vagas/`, `/eventos/` e `/abcr/` (notícias institucionais). Seguir o link de saída da notícia até o edital (as notícias podem citar prazo anterior a uma retificação).

**Observatório do Terceiro Setor, 24 registros, 2 úteis.**
- Erro: grava seções temáticas (`/secoes_tematicas/editais/...`) e notícias de capacitação ou consultoria gratuita (FEA Social, Instituto Equatorial), que não são fomento.
- Correção: aplicar o detector de catálogo (M2) e o filtro de não-oportunidade (M3).

**Busca de empresas (FIA, Idoso, Esporte, Pronas, Pronon, Goyazes), 26 registros, 2 úteis.**
- Erro: grava páginas institucionais de "leis de incentivo" (Sicredi), prêmios para escolas (Liga STEAM) e notícias de lei, como a prorrogação do Pronon.
- Correção: gravar só a página que tenha edital com prazo; páginas institucionais viram fonte monitorada (checagem periódica), não oportunidade.

**Secult Goiás (Goyazes e Aldir Blanc), 13 registros, 1 útil.**
- Erro grave de roteamento: os 13 registros têm `uf` vazio e, por isso, caíram na Parte 3 (Brasil) em vez da Parte 1 (Goiás).
- Erro: 9 são notícias ou catálogos (PNAB 2026 já encerrado em 17/04).
- Correção: UF fixa "GO" e nível "estadual" para todo registro desse motor; catálogo PNAB expandido em editais individuais (M2).

**Bússola Social, SALIC, Mapa das OSC, Instituto Sabin, Agência do Bem e outros pequenos: 0 úteis.**
- Erro: páginas de produto ou portal (Bússola), páginas genéricas (SALIC, Mapa das OSC) e programas de 2025 encerrados (Agência do Bem).
- Correção: converter em fontes monitoradas (avisar quando a página mudar) e parar de criar oportunidades diretamente.

## 5. Melhorias a implementar (em ordem de prioridade)
O detalhamento técnico (padrões, campos, critérios de aceite) está em `melhorias_motores.json`, no mesmo pacote.

| # | Melhoria | Onde | Efeito esperado (medido na Parte 3) | Critério de aceite |
|---|---|---|---|---|
| M1 | Normalizar a URL (decodificar `uddg`, remover `utm_*`, `#` e barra final) e deduplicar por URL canônica e por (financiador, número do edital, ano) | Na gravação, comum a todos os motores | Elimina 38 duplicatas de URL idêntica e a maior parte das 18 entre motores | Duplicatas abaixo de 5% por motor |
| M2 | Detector de página-catálogo: não grava o catálogo, expande os links de saída para domínios oficiais em oportunidades derivadas | Comum, antes da gravação | Tira cerca de 60 ruídos e recupera oportunidades como as 23 derivadas (6 certificadas) | Nenhuma URL de catálogo gravada como oportunidade |
| M3 | Filtro de não-oportunidade: vaga, resultado, lei, evento ou webinar, capacitação gratuita, artigo "como conseguir", institucional | Comum, classificador de título e URL | Tira cerca de 40 ruídos | Ruído abaixo de 10% por motor |
| M4 | Prazo obrigatório na coleta: extrair `fim` (padrões de data); se `fim` < data da coleta, arquivar como encerrada; sem prazo, marcar `sem_prazo` | Comum | Evita 43 coletas de oportunidade já vencida | Nenhuma oportunidade gravada como aberta com prazo vencido |
| M5 | UF e nível pelo órgão: "Prefeitura Municipal de X" → municipal e UF (tabela IBGE); "Secretaria de Estado", "Secult Goiás" ou goias.gov.br → estadual GO; gov.br, Ibama, BNDES, conselhos profissionais (CRA, CAU, CREFITO), CAIXA → federal; fundação, instituto ou empresa → privada | Comum; Secult GO com UF fixa | Corrige 18 registros de Goiás desviados e mais de 120 públicos rotulados como privados | `uf` preenchida em 95% ou mais; 0 registros de Goiás fora da Parte 1 |
| M6 | Rota PNCP oficial: extrair o número de controle ou link do PNCP da pista e consultar `pncp.gov.br/api/consulta/v1/orgaos/<cnpj>/compras/<ano>/<seq>` (objeto, datas, valor, órgão, município) | Espião, Motor do Piloto, motores de prefeituras | Certificou 5 casos que o CapitaAI informava errado ou sem fonte | Todo chamamento municipal com número de controle sai com 6 itens certificados |
| M7 | Agregador nunca preenche valor ou prazo; só registra a pista e a URL de saída. Divergência entre agregador e oficial vai para `alertas` | Comum | Evita os 58 casos de divergência | 0 itens certificados com documento de agregador |
| M8 | Classificador de perfil OSC: "pessoa física", "proponente pesquisador", "empresas produtoras", "artistas individuais", "estudantes", "escolas" → `fora_perfil` com o trecho | Comum, depois da leitura | Antecipa os 8 fora do perfil | Nenhum fora do perfil apresentado como oportunidade |
| M9 | Ponte com o Chrome da titular para DOU, Prosas, Bússola Social, arquivos do PNCP e sites em JavaScript; leitor de .docx para os anexos | Cartório, degrau 4 | Resolve a maior parte dos 41 pendentes | Pendentes abaixo de 10% por parte |
| M10 | Painel de qualidade por motor (precisão, duplicatas, ruído, encerradas na coleta, UF vazia), recalculado a cada ciclo, com rebaixamento automático para "fonte de pistas" se a precisão ficar abaixo de 5% por 2 ciclos | Painel e esteira | Mantém os motores medidos | Indicadores publicados a cada ciclo |

## 6. Ordem de implantação sugerida
1. M1, M3, M4 e M5: regras simples na gravação; cortam cerca de 70% do volume inútil e corrigem o roteamento de Goiás.
2. M2 e M6: transformam catálogo e agregador em oportunidade oficial certificada.
3. M7 e M8: protegem a qualidade do que chega à titular.
4. M9 e M10: resolvem os pendentes e mantêm a medição.

## 7. Conselho de 7 lentes
- **Extremamente pessimista:** 6,7% de aproveitamento quer dizer que, a cada 15 registros, a titular paga a leitura de 14 que não servem. O Motor do Piloto não produziu nada em 81 registros e ainda gerou 42 duplicatas. Sem M1 a M5, a próxima rodada repete o problema.
- **Pessimista:** o roteamento de UF falhou em 295 de 300 registros. A prova mais grave são as 18 oportunidades de Goiás, o público prioritário, que caíram fora da Parte 1. O agregador continua sendo lido como verdade em valores e prazos (58 divergências), e isso pode levar a decisões erradas de inscrição.
- **Levemente pessimista:** as regras de URL e de título (M2 e M3) podem descartar oportunidade legítima, por exemplo uma notícia que é o único lugar onde o edital aparece. Mitigação: o descarte vira "pista" com link de saída, nunca exclusão.
- **Neutro (decide):** implantar M1, M3, M4 e M5 já, porque são regras determinísticas, baratas e testáveis com este conjunto de 300 como gabarito. Depois M2 e M6, que dependem de ler a pista, e por fim M7 a M10. Parâmetros de qualidade por motor: precisão de 25% ou mais, duplicatas abaixo de 5%, ruído abaixo de 10%, `uf` e `fim` preenchidos em 95% ou mais e nenhuma oportunidade vencida na coleta. Mitigações: todo descarte automático fica registrado com o motivo e pode ser revertido; o conjunto de 300 com vereditos (pacote da Etapa 1) passa a ser o teste de regressão dos motores. Correções feitas antes de entregar: Ibama e Lagoa do Ouro rebaixados para pendente, FAPESB marcada como fora do perfil e duplicatas entre lotes e entre derivadas unificadas.
- **Levemente otimista:** a ABCR e o Observatório já entregam os editais de maior valor (CONANDA, Zurich, Equatorial, Maria Emília). Com M7 eles ficam confiáveis sem trocar de fonte.
- **Otimista:** a rota PNCP (M6) transforma o Espião numa fonte nacional de chamamentos municipais certificados, sem precisar ler PDF. Só aqui saíram Iguatu (R$ 45,1 milhões), Senador Pompeu, Itagibá e Ielmo Marinho.
- **Extremamente otimista:** com catálogos expandidos (M2) e um painel por motor (M10), o sistema passa de "lista de links" para uma carteira certificada e autolimpante. As 23 derivadas desta rodada mostram que existe mais oportunidade real do que os motores registram hoje.
