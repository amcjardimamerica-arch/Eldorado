# 03 — A Biblioteca, o Especial e o banco do Cérebro (o esquema do banco de dados)

**Versão final, revisada antes da criação (22/10/2026).** Esquema da **parte modular do banco de dados** do novo Eldorado, no mesmo formato dos esquemas da base e dos motores, e cumprindo exatamente os contratos definidos neles. Os esquemas SQL deste documento foram **executados e testados num SQLite real** em 22/10/2026. Nada foi criado no repositório novo.

## Revisão final (antes da criação, 22/10/2026)

**Entra desde a Fase 5:**
1. **primp** no degrau 2 da escada de acesso (medido: 40% mais rápido que o curl_cffi, com outra assinatura de navegador).
2. **Protego** na escada de acesso: o robots como informação; a espera pedida pelo site alimenta o limite por domínio, sem bloquear.
3. **webtech** na leitura de páginas: detecta o sistema do site (WordPress e outros) para usar a API dele.
4. **Lightpanda 1.0.0** no degrau 3 (medido: 58 ms e 24 MB por página, contra 156 ms e 484 MB do Chromium), **com a espera configurada obrigatória** em cada motor.
5. **O recibo de cada chamada registra o processador e a memória de pico**, além do tempo: a Sala mostra quanto cada arquivo consome, e o governador adia os mais pesados.
6. **Números por extenso** por regra própria na normalização.
7. **O motor de indicadores** (`cerebro/medicao.py`) e o componente **Análise** (história do livro, previsão e calendário) na base.
8. **A análise da rede neural sobre cada livro**, guardada na Biblioteca (`analise_rede`).

**Sai desde a Fase 5:**
1. **Litestream** (as fotografias e os eventos cobrem a recuperação).
2. **A lógica que estava no banco** (história, previsão, calendário), que passou para a Análise.
3. **Os 103 projetos descartados** no estudo do GitHub, cada um com o motivo (arquivo C).

**Preservado:** as telas do Farol (Enquadramento, Documentos, fichas). **No Eldorado0:** o Interceptador foi corrigido e voltou a gerar aprendizado até a parada total, em 30 dias.

**Ordem de criação:** começa pela Fase 1 (Fundação): contratos, configuração, eventos, alarmes, os esquemas dos três bancos, o gravador e os testes.

## 1. Os princípios do banco

1. **Relacional, em SQLite**, um arquivo por banco: `biblioteca.db` (os livros), `especial.db` (as empresas) e `cerebro.db` (a operação e o aprendizado do sistema, **sem nenhuma oportunidade**).
2. **O banco só guarda, impõe as regras e oferece as visões.** Toda lógica (selos, previsão, história, calendário) fica na base; o banco não depende de nenhuma outra parte.
3. **Só o gravador escreve**, aplicando eventos. Cada evento aplicado fica registrado (`evento_aplicado`), e o mesmo evento não é aplicado duas vezes.
4. **Nada se apaga nem se sobrescreve.** A exclusão é lógica, com justificativa; uma prova nova é gravada ao lado da anterior, que fica contestada; uma regra nova substitui a anterior, que fica registrada.
5. **Nenhum PDF ou imagem dentro do sistema.** O original vai ao Drive; o banco guarda o endereço, a assinatura e o **texto literal completo de cada página, comprimido**, com busca de texto.
6. **Toda tela de oportunidade lê a Biblioteca**, pelas visões. Toda tela de operação lê o Cérebro.

## 2. Os três bancos

| Banco | Para quê | Tabelas | Visões | Regras (gatilhos) | Índices |
| --- | --- | --- | --- | --- | --- |
| `biblioteca.db` | os livros e tudo o que se sabe de cada oportunidade | 23 | 4 | 12 | 19 |
| `especial.db` | as empresas, os incentivos e as oportunidades nas empresas conhecidas | 7 | 1 | 3 | 5 |
| `cerebro.db` | a operação do sistema: plano, execuções, medições, regras, modelo, aprendizado, alarmes, máquina | 21 | 2 | 3 | 16 |

## 3. O livro: a história contada por inteiro

Cada livro reúne, na Biblioteca:

| Parte do livro | Onde fica |
| --- | --- |
| Identidade: missão, chave, título, tema, órgão, UF, município | `livro` |
| **Os dois links:** onde foi divulgada e o link oficial | `livro`, `achado` |
| **Os selos:** a estrela (completude dos 12 itens) e o selo do livro (previsibilidade) | `livro` |
| **Os motores que a encontraram e as datas** | `achado` (motor, data, link, se veio de cópia arquivada, se é pista) |
| **As informações obtidas:** cada item com o valor, o trecho, a página e o documento | `certidao` (comprovado, dispensado com justificativa, pendente, contestado) |
| **O texto literal** de cada página do documento oficial | `pagina` (comprimido) e `busca` |
| **O workflow pelo sistema:** a fase atual, as passagens (autorizadas pela Regência) e as tentativas (até 3 por ferramenta) | `passaporte`, `passagem`, `tentativa` |
| **Os relatórios de cada etapa**, com o que gerou, aprendeu e faltou, e se a análise foi interna ou externa | `relatorio_etapa` |
| **A análise da rede neural sobre o livro** (nota, pertinência, explicação, versão do modelo) | `analise_rede` |
| **As decisões:** da titular, do Chrome, do Interceptador, das regras | `veredito` |
| **A previsão:** motores e datas em que foi encontrada, a próxima abertura prevista, o alerta antes de abrir | `previsao` |
| As uniões de duplicados e a transferência ao Farol | `uniao`, `transferencia` |

**A visão `historia_do_livro`** junta tudo isso numa linha do tempo, em ordem: achados, passagens, tentativas, certidões, relatórios internos e externos, análises da rede, vereditos e a transferência. É a fonte da **página do livro** no painel, com este layout:

1. **Cabeçalho:** título, órgão, UF, situação, a estrela e o selo do livro, os dois links.
2. **Os 12 itens:** cada um com o valor, o trecho e a página, ou a dispensa com justificativa.
3. **A linha do tempo** (a visão `historia_do_livro`).
4. **As análises:** os relatórios de cada etapa, separando a análise interna (do sistema) da externa (do Chrome e da titular), e a análise da rede.
5. **A previsão:** a próxima abertura e o alerta.
6. **O texto literal:** busca dentro do documento, com a página.

## 4. As visões que alimentam as telas

| Visão | Banco | Tela |
| --- | --- | --- |
| `calendario` | Biblioteca | Calendário: oportunidades abertas e previstas |
| `historia_do_livro` | Biblioteca | Página do livro |
| `selos` | Biblioteca | Cartório e início |
| `achados_por_motor` | Biblioteca | Bússola e painel de cada motor |
| `empresas_com_oportunidade_aberta` | Especial | Oportunidades de empresas |
| `regra_vigente` | Cérebro | Sala (regras) |
| `alarmes_abertos` | Cérebro | Sala (alarmes) e início |

As demais telas (Sala, mostrador da máquina, Bússola) leem as tabelas `medicao`, `maquina`, `execucao_motor` e `cobertura_dia` do Cérebro, pelas visões geradas a cada passagem.

## 5. O Especial: empresas e pilotos

O banco Especial guarda as **empresas** (com a origem de cada descoberta), os **incentivos** comprovados por lei (FIA, Idoso, Esporte, Rouanet, Pronas, Pronon, Goyazes, ICMS, PAT), os **rankings**, as **oportunidades nas empresas conhecidas** e o **vínculo com os livros**. O **Espião descobre** empresas e oportunidades novas (`descoberta_por = 'espiao'`); o **Interceptador aprofunda** o conhecimento de cada uma (`aprofundamento`). A finalidade é ter o relatório das oportunidades já abertas, das que podem abrir e das que podem ser buscadas nas empresas conhecidas.

## 6. O banco do Cérebro

Sem nenhuma oportunidade. Guarda: os módulos e os domínios (com o degrau de acesso que funciona em cada um); o plano, os acionamentos, as execuções e cada passo delas (para retomar depois de uma queda); os recibos de cada chamada (a base do ponto de cada arquivo); as execuções dos motores; a agenda e a cobertura do dia; as decisões de pertinência; as medições em todos os níveis; o modelo e os rótulos; as regras, com precedência e substituição; o aprendizado **temporário (até 30 dias, imposto pelo banco)** e o permanente; os alarmes; e a máquina (uso e tamanho de cada parte).

## 7. O texto, os originais e as fotografias

- **Texto:** cada página é gravada comprimida com zstd (nível 3, com dicionário treinado), e indexada numa busca FTS5 **sem cópia do texto**. Teste com um edital real de 26 páginas: 59.848 bytes viraram 28.856; a busca achou as páginas certas; o texto restaurado ficou idêntico.
- **Originais:** o PDF, a imagem e a planilha vão ao Drive; o banco guarda `drive_id` e `sha256`.
- **Fotografias:** os três bancos são copiados comprimidos fora do Git e podem ser reconstruídos dos eventos.

## 8. A migração do Eldorado0 (30 dias)

Importados por eventos e conferidos pelas contagens: 3.668 livros, 2.706 certidões, 1.531 vereditos, a base de empresas (565 arquivos do livro especial) e todo o aprendizado (`APRENDIZADO-ELDORADO.json`). O CPF é removido onde não for necessário. Depois, o Eldorado0 é desligado por partes, até o expurgo total.

## 9. Os testes feitos em 22/10/2026

| Teste | Resultado |
| --- | --- |
| Apagar livro, achado, prova, empresa | barrado |
| Mudar a identidade do livro | barrado |
| Sobrescrever prova, alterar relatório, texto de página, veredito, análise da rede, regra | barrado |
| Excluir sem justificativa; dispensar sem justificativa | barrado |
| Passagem sem a Regência; 4ª tentativa; livro duplicado | barrado |
| Aplicar o mesmo evento duas vezes | barrado |
| Aprendizado temporário com mais de 30 dias | barrado |
| Exclusão lógica com justificativa | permitida |
| Texto comprimido restaurado | idêntico |
| Busca de texto sem cópia | acha a página certa |
| Calendário, história do livro, selos, achados por motor | funcionam |
| Tabelas exigidas pelos esquemas da base e dos motores | todas presentes |

## 10. Os arquivos do banco

#### `eldorado/banco/biblioteca/esquema.py`

| Campo | Esboço |
| --- | --- |
| Funções principais | criar o banco com o esquema e as regras; versionar o esquema (PRAGMA user_version) e migrar; ligar WAL, chaves estrangeiras e mmap; verificar a integridade |
| Tabelas que lê | — |
| Configuração | caminho do banco |
| Alarmes | integridade falhou, versão do esquema diferente da esperada |
| Indicador · ponto | funciona quando chamado |
| Indicador · círculo | limiares: íntegro / aviso de versão / falha de integridade |
| Teste de aceite | as 13 operações proibidas são barradas e a exclusão lógica é aceita (testado em 22/10) |
| Atende à finalidade da titular | banco relacional SQLite; nada se apaga nem se sobrescreve |

#### `eldorado/banco/biblioteca/livro.py`

| Campo | Esboço |
| --- | --- |
| Funções principais | ler o livro inteiro; listar por situação, tema, selo; ler a história (visão); oferecer as visões às telas |
| Tabelas que lê | todas as tabelas da Biblioteca |
| Configuração | — |
| Alarmes | consulta lenta |
| Indicador · ponto | funciona quando chamado |
| Indicador · círculo | limiares: consulta < 50 ms / 50 a 500 ms / mais |
| Teste de aceite | a história de um livro volta em ordem, com todas as passagens |
| Atende à finalidade da titular | cada livro analisado de forma individual |

#### `eldorado/banco/biblioteca/texto.py`

| Campo | Esboço |
| --- | --- |
| Funções principais | comprimir o texto de cada página com zstd (com dicionário treinado); indexar na busca FTS5 sem cópia do texto; restaurar o texto exato |
| Tabelas que lê | pagina, busca |
| Configuração | nível de compressão 3, dicionário |
| Alarmes | texto restaurado diferente do original |
| Indicador · ponto | funciona quando chamado |
| Indicador · círculo | limiares: restauração idêntica / — / diferente |
| Teste de aceite | o texto de um edital real é restaurado idêntico; a busca acha a página certa |
| Atende à finalidade da titular | texto literal completo, sem PDF, no menor tamanho |

#### `eldorado/banco/biblioteca/leis.py`

| Campo | Esboço |
| --- | --- |
| Funções principais | guardar as leis e o regramento de cada fonte |
| Tabelas que lê | lei |
| Configuração | — |
| Alarmes | — |
| Indicador · ponto | funciona quando chamado |
| Indicador · círculo | limiares: atualizadas / — / paradas |
| Teste de aceite | uma lei nova aparece ligada aos livros que ela afeta |
| Atende à finalidade da titular | acompanhar leis que criam recursos |

#### `eldorado/banco/especial/esquema.py`

| Campo | Esboço |
| --- | --- |
| Funções principais | criar o banco Especial (empresas); regras: empresa não se apaga, incentivo não se sobrescreve |
| Tabelas que lê | — |
| Configuração | caminho do banco |
| Alarmes | integridade falhou |
| Indicador · ponto | funciona quando chamado |
| Indicador · círculo | limiares: íntegro / — / falha |
| Teste de aceite | apagar uma empresa é barrado (testado em 22/10) |
| Atende à finalidade da titular | parte Especial com dados de empresas |

#### `eldorado/banco/especial/empresas.py`

| Campo | Esboço |
| --- | --- |
| Funções principais | ficha da empresa; incentivos comprovados; oportunidades nas empresas conhecidas; descobertas do Espião e aprofundamentos do Interceptador; vínculo com os livros |
| Tabelas que lê | empresa, incentivo, oportunidade_empresa, aprofundamento, vinculo_livro |
| Configuração | — |
| Alarmes | — |
| Indicador · ponto | funciona quando chamado |
| Indicador · círculo | limiares: atualizadas / — / paradas |
| Teste de aceite | uma empresa descoberta pelo Espião recebe o aprofundamento do Interceptador |
| Atende à finalidade da titular | Espião busca, Interceptador aprofunda; oportunidades nas empresas conhecidas |

#### `eldorado/banco/cerebro_db/esquema.py`

| Campo | Esboço |
| --- | --- |
| Funções principais | criar o banco do Cérebro; temporário até 30 dias; regra imutável (substituição registrada); visões: regra vigente, alarmes abertos |
| Tabelas que lê | — |
| Configuração | caminho do banco |
| Alarmes | temporário com mais de 30 dias |
| Indicador · ponto | funciona quando chamado |
| Indicador · círculo | limiares: retenção cumprida / — / violada |
| Teste de aceite | um temporário de 61 dias é barrado; alterar uma regra é barrado (testado em 22/10) |
| Atende à finalidade da titular | Cérebro com banco próprio, sem oportunidades |

#### `eldorado/banco/originais/drive.py`

| Campo | Esboço |
| --- | --- |
| Funções principais | enviar o original ao Drive; guardar o endereço e a assinatura; conferir que o original existe |
| Tabelas que lê | documento |
| Configuração | pasta do Drive, credencial |
| Alarmes | original citado e ausente no Drive |
| Indicador · ponto | funciona quando chamado |
| Indicador · círculo | limiares: todos no Drive / atraso / ausente |
| Teste de aceite | um PDF enviado volta pelo endereço e a assinatura confere |
| Atende à finalidade da titular | PDF e imagem só no Drive, nunca no sistema |

#### `eldorado/banco/fotografia.py`

| Campo | Esboço |
| --- | --- |
| Funções principais | fotografia comprimida dos três bancos, fora do Git; reconstruir a partir dos eventos |
| Tabelas que lê | três bancos |
| Configuração | destino das fotografias |
| Alarmes | fotografia atrasada, reconstrução diferente |
| Indicador · ponto | funciona quando chamado |
| Indicador · círculo | limiares: do dia / 1 dia de atraso / mais |
| Teste de aceite | o banco reconstruído dos eventos é igual ao original |
| Atende à finalidade da titular | robusto, recuperável; lição dos 2,1 GB de histórico do Git |

## 11. Os esquemas SQL completos (executados e testados)

### `biblioteca.db`

```sql
PRAGMA foreign_keys=ON;
CREATE TABLE evento_aplicado (id TEXT PRIMARY KEY, tipo TEXT NOT NULL, aplicado_em TEXT NOT NULL);
CREATE TRIGGER evento_aplicado_imutavel BEFORE UPDATE ON evento_aplicado BEGIN SELECT RAISE(ABORT,'evento aplicado não se altera'); END;

CREATE TABLE livro (id TEXT PRIMARY KEY, missao TEXT NOT NULL, chave TEXT NOT NULL, titulo TEXT, tema TEXT,
  orgao TEXT, uf TEXT, municipio_ibge TEXT, link_divulgacao TEXT, link_oficial TEXT,
  estrela TEXT CHECK (estrela IN ('sem','bronze','prata','ouro')), selo_livro TEXT CHECK (selo_livro IN ('sem','bronze','prata','ouro')),
  informacoes_validadas INTEGER NOT NULL DEFAULT 0,
  situacao TEXT NOT NULL CHECK (situacao IN ('em trabalho','aguardando','verificacao externa','finalizado','transferido ao farol','excluido')),
  justificativa_exclusao TEXT, criado_em TEXT NOT NULL, atualizado_em TEXT NOT NULL,
  UNIQUE (missao, chave), CHECK (situacao <> 'excluido' OR justificativa_exclusao IS NOT NULL));
CREATE TABLE achado (id TEXT PRIMARY KEY, motor TEXT NOT NULL, encontrado_em TEXT NOT NULL, publicado_em TEXT,
  link_divulgacao TEXT NOT NULL, link_oficial TEXT, titulo TEXT, dados TEXT NOT NULL,
  documento_id INTEGER REFERENCES documento(id), veio_de_copia_arquivada INTEGER NOT NULL DEFAULT 0, pista INTEGER NOT NULL DEFAULT 0,
  decisao TEXT CHECK (decisao IN ('pendente','aceito','barrado')) DEFAULT 'pendente', motivo TEXT, livro_id TEXT REFERENCES livro(id));
CREATE TABLE uniao (livro_que_fica TEXT REFERENCES livro(id), livro_unido TEXT REFERENCES livro(id), em TEXT NOT NULL, motivo TEXT NOT NULL,
  PRIMARY KEY (livro_que_fica, livro_unido));
CREATE TABLE passaporte (livro_id TEXT PRIMARY KEY REFERENCES livro(id),
  fase TEXT NOT NULL CHECK (fase IN ('coleta','certificacao','investigacao','verificacao externa','farol')), entrou_em TEXT NOT NULL);
CREATE TABLE passagem (id INTEGER PRIMARY KEY, livro_id TEXT NOT NULL REFERENCES livro(id), de TEXT, para TEXT NOT NULL, em TEXT NOT NULL,
  autorizado_por TEXT NOT NULL CHECK (autorizado_por = 'regencia'), motivo TEXT);
CREATE TABLE tentativa (livro_id TEXT REFERENCES livro(id), fase TEXT, ferramenta TEXT, numero INTEGER CHECK (numero BETWEEN 1 AND 3),
  em TEXT NOT NULL, resultado TEXT, proxima_em TEXT, PRIMARY KEY (livro_id, fase, ferramenta, numero));
CREATE TABLE item (missao TEXT, codigo TEXT, nome TEXT NOT NULL, como_prova TEXT, PRIMARY KEY (missao, codigo));
CREATE TABLE documento (id INTEGER PRIMARY KEY, url TEXT NOT NULL, sha256 TEXT NOT NULL UNIQUE, tipo TEXT, paginas INTEGER,
  obtido_em TEXT NOT NULL, oficial INTEGER NOT NULL DEFAULT 0, drive_id TEXT, leitor TEXT, versao_leitor TEXT);
CREATE TABLE pagina (documento_id INTEGER REFERENCES documento(id), numero INTEGER, texto_zstd BLOB NOT NULL, caracteres INTEGER NOT NULL,
  expurgado INTEGER NOT NULL DEFAULT 0, PRIMARY KEY (documento_id, numero));
CREATE VIRTUAL TABLE busca USING fts5(texto, content='', contentless_delete=1, tokenize='unicode61 remove_diacritics 2');
CREATE TABLE busca_mapa (rowid INTEGER PRIMARY KEY, documento_id INTEGER NOT NULL, numero INTEGER NOT NULL);
CREATE TABLE certidao (id INTEGER PRIMARY KEY, livro_id TEXT NOT NULL REFERENCES livro(id), item TEXT NOT NULL, valor TEXT,
  documento_id INTEGER REFERENCES documento(id), pagina INTEGER, trecho TEXT, fase TEXT NOT NULL,
  situacao TEXT NOT NULL CHECK (situacao IN ('comprovado','dispensado','pendente','contestado')), justificativa TEXT, em TEXT NOT NULL,
  CHECK (situacao <> 'dispensado' OR justificativa IS NOT NULL));
CREATE TABLE veredito (id INTEGER PRIMARY KEY, livro_id TEXT NOT NULL REFERENCES livro(id),
  origem TEXT NOT NULL CHECK (origem IN ('titular','chrome','interceptador','regra')), decisao TEXT NOT NULL, motivo TEXT, como_encontrou TEXT, em TEXT NOT NULL);
CREATE TABLE relatorio_etapa (id INTEGER PRIMARY KEY, livro_id TEXT NOT NULL REFERENCES livro(id), fase TEXT NOT NULL,
  gerou TEXT NOT NULL, aprendeu TEXT, faltou TEXT, analise TEXT CHECK (analise IN ('interna','externa')) DEFAULT 'interna', em TEXT NOT NULL);
CREATE TABLE previsao (livro_id TEXT PRIMARY KEY REFERENCES livro(id), motores_que_encontraram TEXT, datas_encontrado TEXT,
  proxima_abertura_prevista TEXT, alerta_em TEXT, confianca REAL, calculada_em TEXT NOT NULL);
CREATE TABLE transferencia (livro_id TEXT REFERENCES livro(id), em TEXT NOT NULL, versao_formato TEXT NOT NULL, PRIMARY KEY (livro_id, em));
CREATE TABLE analise_rede (id INTEGER PRIMARY KEY, livro_id TEXT NOT NULL REFERENCES livro(id), em TEXT NOT NULL, nota REAL,
  pertinencia REAL, explicacao TEXT, modelo_versao TEXT NOT NULL);
CREATE TABLE lei (id TEXT PRIMARY KEY, esfera TEXT, numero TEXT, ementa TEXT, situacao TEXT, link_oficial TEXT, atualizada_em TEXT NOT NULL);
CREATE INDEX achado_livro ON achado(livro_id); CREATE INDEX achado_motor ON achado(motor, encontrado_em);
CREATE INDEX certidao_livro ON certidao(livro_id); CREATE INDEX passagem_livro ON passagem(livro_id, em);
CREATE INDEX livro_situacao ON livro(situacao); CREATE INDEX previsao_abertura ON previsao(proxima_abertura_prevista);
-- regras do banco: nada se apaga nem se sobrescreve
CREATE TRIGGER livro_nao_se_apaga BEFORE DELETE ON livro BEGIN SELECT RAISE(ABORT,'livro não se apaga: use a exclusão lógica'); END;
CREATE TRIGGER livro_identidade_fixa BEFORE UPDATE OF id, missao, chave, criado_em ON livro BEGIN SELECT RAISE(ABORT,'a identidade do livro não se altera'); END;
CREATE TRIGGER achado_nao_se_apaga BEFORE DELETE ON achado BEGIN SELECT RAISE(ABORT,'achado não se apaga'); END;
CREATE TRIGGER certidao_nao_se_sobrescreve BEFORE UPDATE OF valor, documento_id, pagina, trecho ON certidao BEGIN SELECT RAISE(ABORT,'prova não se sobrescreve: grave nova e conteste a anterior'); END;
CREATE TRIGGER certidao_nao_se_apaga BEFORE DELETE ON certidao BEGIN SELECT RAISE(ABORT,'prova não se apaga'); END;
CREATE TRIGGER relatorio_imutavel BEFORE UPDATE ON relatorio_etapa BEGIN SELECT RAISE(ABORT,'relatório de etapa não se altera'); END;
CREATE TRIGGER relatorio_nao_se_apaga BEFORE DELETE ON relatorio_etapa BEGIN SELECT RAISE(ABORT,'relatório de etapa não se apaga'); END;
CREATE TRIGGER passagem_imutavel BEFORE UPDATE ON passagem BEGIN SELECT RAISE(ABORT,'passagem não se altera'); END;
CREATE TRIGGER veredito_imutavel BEFORE UPDATE ON veredito BEGIN SELECT RAISE(ABORT,'veredito não se altera'); END;
CREATE TRIGGER analise_rede_imutavel BEFORE UPDATE ON analise_rede BEGIN SELECT RAISE(ABORT,'a análise da rede não se altera: grave uma nova'); END;
CREATE TRIGGER pagina_imutavel BEFORE UPDATE ON pagina BEGIN SELECT RAISE(ABORT,'o texto de uma página não se altera'); END;
-- visões que alimentam as telas (toda tela de oportunidade lê daqui)
CREATE VIEW calendario AS
  SELECT l.id, l.titulo, l.tema, l.uf, 'aberta' AS tipo, NULL AS data_prevista, l.estrela, l.selo_livro FROM livro l
   WHERE l.situacao IN ('em trabalho','aguardando','verificacao externa','finalizado')
  UNION ALL SELECT l.id, l.titulo, l.tema, l.uf, 'prevista', p.proxima_abertura_prevista, l.estrela, l.selo_livro
   FROM previsao p JOIN livro l ON l.id = p.livro_id WHERE p.proxima_abertura_prevista IS NOT NULL AND l.situacao <> 'excluido';
CREATE VIEW historia_do_livro AS
  SELECT livro_id, encontrado_em AS em, 'achado' AS tipo, motor || ': ' || COALESCE(titulo,'') AS texto FROM achado WHERE livro_id IS NOT NULL
  UNION ALL SELECT livro_id, em, 'passagem', COALESCE(de,'início') || ' → ' || para || COALESCE(' (' || motivo || ')','') FROM passagem
  UNION ALL SELECT livro_id, em, 'tentativa', fase || ' · ' || ferramenta || ' · tentativa ' || numero || ' · ' || COALESCE(resultado,'') FROM tentativa
  UNION ALL SELECT livro_id, em, 'certidão', item || ' · ' || situacao FROM certidao
  UNION ALL SELECT livro_id, em, 'relatório ' || analise, fase || ': ' || gerou FROM relatorio_etapa
  UNION ALL SELECT livro_id, em, 'veredito', origem || ': ' || decisao FROM veredito
  UNION ALL SELECT livro_id, em, 'análise da rede', 'nota ' || COALESCE(nota,'') || ' · ' || COALESCE(explicacao,'') FROM analise_rede
  UNION ALL SELECT livro_id, em, 'transferência', 'ao Farol (formato ' || versao_formato || ')' FROM transferencia;
CREATE VIEW selos AS SELECT estrela, selo_livro, COUNT(*) AS livros FROM livro WHERE situacao <> 'excluido' GROUP BY estrela, selo_livro;
CREATE VIEW achados_por_motor AS SELECT motor, COUNT(*) AS achados, SUM(decisao='aceito') AS aceitos, SUM(decisao='barrado') AS barrados, MAX(encontrado_em) AS ultimo FROM achado GROUP BY motor;
```

### `especial.db`

```sql
PRAGMA foreign_keys=ON;
CREATE TABLE evento_aplicado (id TEXT PRIMARY KEY, tipo TEXT NOT NULL, aplicado_em TEXT NOT NULL);
CREATE TRIGGER evento_aplicado_imutavel BEFORE UPDATE ON evento_aplicado BEGIN SELECT RAISE(ABORT,'evento aplicado não se altera'); END;

CREATE TABLE empresa (cnpj TEXT PRIMARY KEY, razao_social TEXT NOT NULL, nome_fantasia TEXT, uf TEXT, municipio_ibge TEXT, porte TEXT,
  atividade_principal TEXT, regime_tributario TEXT, site TEXT, descoberta_por TEXT CHECK (descoberta_por IN ('espiao','motor','importacao','titular')),
  descoberta_em TEXT NOT NULL, atualizada_em TEXT NOT NULL);
CREATE TABLE incentivo (id INTEGER PRIMARY KEY, cnpj TEXT NOT NULL REFERENCES empresa(cnpj),
  lei TEXT NOT NULL CHECK (lei IN ('FIA','Idoso','Esporte','Rouanet','Pronas','Pronon','Goyazes','ICMS','PAT','outra')),
  ano INTEGER, valor REAL, comprovado INTEGER NOT NULL DEFAULT 0, fonte TEXT NOT NULL, em TEXT NOT NULL);
CREATE TABLE ranking (cnpj TEXT REFERENCES empresa(cnpj), criterio TEXT, posicao INTEGER, pontos REAL, calculado_em TEXT NOT NULL, PRIMARY KEY (cnpj, criterio, calculado_em));
CREATE TABLE oportunidade_empresa (id TEXT PRIMARY KEY, cnpj TEXT NOT NULL REFERENCES empresa(cnpj), titulo TEXT NOT NULL, tipo TEXT,
  link_oficial TEXT, abertura TEXT, encerramento TEXT, encontrada_por TEXT, encontrada_em TEXT NOT NULL);
CREATE TABLE vinculo_livro (cnpj TEXT REFERENCES empresa(cnpj), livro_id TEXT NOT NULL, papel TEXT, em TEXT NOT NULL, PRIMARY KEY (cnpj, livro_id, papel));
CREATE TABLE aprofundamento (id INTEGER PRIMARY KEY, cnpj TEXT NOT NULL REFERENCES empresa(cnpj), piloto TEXT NOT NULL DEFAULT 'interceptador',
  o_que TEXT NOT NULL, achou TEXT, fonte TEXT, em TEXT NOT NULL);
CREATE TRIGGER empresa_nao_se_apaga BEFORE DELETE ON empresa BEGIN SELECT RAISE(ABORT,'empresa não se apaga'); END;
CREATE TRIGGER incentivo_nao_se_sobrescreve BEFORE UPDATE OF valor, ano, lei ON incentivo BEGIN SELECT RAISE(ABORT,'incentivo não se sobrescreve'); END;
CREATE VIEW empresas_com_oportunidade_aberta AS
  SELECT e.cnpj, e.razao_social, o.titulo, o.encerramento FROM empresa e JOIN oportunidade_empresa o ON o.cnpj = e.cnpj WHERE o.encerramento IS NULL OR o.encerramento >= date('now');
```

### `cerebro.db`

```sql
PRAGMA foreign_keys=ON;
CREATE TABLE evento_aplicado (id TEXT PRIMARY KEY, tipo TEXT NOT NULL, aplicado_em TEXT NOT NULL);
CREATE TRIGGER evento_aplicado_imutavel BEFORE UPDATE ON evento_aplicado BEGIN SELECT RAISE(ABORT,'evento aplicado não se altera'); END;

CREATE TABLE modulo (id TEXT PRIMARY KEY, tipo TEXT NOT NULL CHECK (tipo IN ('motor','piloto','ferramenta','arquivo','skill')), parte TEXT NOT NULL,
  componente TEXT, finalidade TEXT NOT NULL, metrica TEXT, ligado INTEGER NOT NULL DEFAULT 1, arquivado INTEGER NOT NULL DEFAULT 0, versao TEXT);
CREATE TABLE dominio (dominio TEXT PRIMARY KEY, degrau_que_funciona INTEGER, bloqueios INTEGER NOT NULL DEFAULT 0, robots_proibe INTEGER NOT NULL DEFAULT 0,
  exige_local INTEGER NOT NULL DEFAULT 0, ultimo_bloqueio TEXT);
CREATE TABLE workflow (id TEXT, versao INTEGER, definicao TEXT NOT NULL, criado_em TEXT NOT NULL, PRIMARY KEY (id, versao));
CREATE TABLE plano (passagem TEXT PRIMARY KEY, criado_em TEXT NOT NULL, motores TEXT, livros_por_etapa TEXT, tempo_por_etapa TEXT);
CREATE TABLE acionamento (id INTEGER PRIMARY KEY, passagem TEXT REFERENCES plano(passagem), etapa TEXT, modulo TEXT, motivo TEXT, em TEXT NOT NULL);
CREATE TABLE execucao (id TEXT PRIMARY KEY, workflow TEXT, versao INTEGER, inicio TEXT NOT NULL, fim TEXT, estado TEXT CHECK (estado IN ('rodando','concluida','falhou','retomada')));
CREATE TABLE execucao_passo (execucao TEXT REFERENCES execucao(id), passo INTEGER, no TEXT, estado TEXT, entrada TEXT, saida TEXT, em TEXT NOT NULL, PRIMARY KEY (execucao, passo));
CREATE TABLE recibo (id INTEGER PRIMARY KEY, execucao TEXT, modulo TEXT NOT NULL, chamado_por TEXT, ok INTEGER NOT NULL, duracao_ms INTEGER,
  cpu_ms INTEGER, memoria_pico_kb INTEGER, erro TEXT, em TEXT NOT NULL);
CREATE TABLE execucao_motor (id INTEGER PRIMARY KEY, motor TEXT NOT NULL, inicio TEXT NOT NULL, fim TEXT, fontes_lidas INTEGER, mudancas INTEGER,
  achados INTEGER, aceitos INTEGER, barrados INTEGER, bloqueios INTEGER, degrau_maximo INTEGER, erro TEXT);
CREATE TABLE agenda (modulo TEXT, janela_inicio TEXT, janela_fim TEXT, motivo TEXT, PRIMARY KEY (modulo, janela_inicio));
CREATE TABLE cobertura_dia (dia TEXT PRIMARY KEY, motores_devidos INTEGER, motores_lidos INTEGER, alvos_na_janela INTEGER, alvos_lidos INTEGER, completo INTEGER);
CREATE TABLE decisao_pertinencia (id INTEGER PRIMARY KEY, etapa TEXT NOT NULL, referencia TEXT NOT NULL, decisao TEXT NOT NULL, motivo TEXT, regra TEXT, em TEXT NOT NULL);
CREATE TABLE medicao (marcador TEXT, nivel TEXT CHECK (nivel IN ('arquivo','componente','parte','sistema','motor')), em TEXT,
  ponto TEXT CHECK (ponto IN ('v','a','r','c')), circulo TEXT CHECK (circulo IN ('v','a','r','c')), linhas TEXT CHECK (linhas IN ('v','a','r','c')),
  valor REAL, motivo TEXT, PRIMARY KEY (marcador, nivel, em));
CREATE TABLE modelo (versao TEXT PRIMARY KEY, treinado_em TEXT NOT NULL, discernimento REAL, precisao REAL, revocacao REAL, arquivo TEXT);
CREATE TABLE rotulo (referencia TEXT, origem TEXT, decisao TEXT, em TEXT, PRIMARY KEY (referencia, origem, em));
CREATE TABLE regra (id INTEGER PRIMARY KEY, missao TEXT, tema TEXT NOT NULL, regra TEXT NOT NULL, decisao_da_titular INTEGER NOT NULL DEFAULT 0,
  data TEXT, precedencia INTEGER NOT NULL DEFAULT 0, vigente INTEGER NOT NULL DEFAULT 1, substituida_por INTEGER REFERENCES regra(id));
CREATE TABLE aprendizado_temporario (id INTEGER PRIMARY KEY, modulo TEXT, o_que TEXT NOT NULL, evidencia TEXT, usos INTEGER NOT NULL DEFAULT 0,
  resultado REAL, criado_em TEXT NOT NULL, expira_em TEXT NOT NULL);
CREATE TABLE aprendizado_permanente (id INTEGER PRIMARY KEY, modulo TEXT, o_que TEXT NOT NULL, promovido_em TEXT NOT NULL, origem_temporario INTEGER,
  medicao_que_provou TEXT, arquivado INTEGER NOT NULL DEFAULT 0);
CREATE TABLE alarme (id INTEGER PRIMARY KEY, gravidade TEXT CHECK (gravidade IN ('baixa','media','alta','critica')), modulo TEXT, mensagem TEXT NOT NULL,
  rastro TEXT, aberto_em TEXT NOT NULL, fechado_em TEXT, repeticoes INTEGER NOT NULL DEFAULT 1);
CREATE TABLE maquina (em TEXT PRIMARY KEY, processador REAL, memoria REAL, disco REAL, rede_entrada REAL, rede_saida REAL, paralelismo INTEGER,
  tamanho_biblioteca INTEGER, tamanho_especial INTEGER, tamanho_cerebro INTEGER, tamanho_eventos INTEGER, tamanho_motores INTEGER);
CREATE TRIGGER temporario_ate_30_dias BEFORE INSERT ON aprendizado_temporario
  WHEN julianday(NEW.expira_em) - julianday(NEW.criado_em) > 30 BEGIN SELECT RAISE(ABORT,'aprendizado temporário dura no máximo 30 dias'); END;
CREATE TRIGGER regra_imutavel BEFORE UPDATE OF regra, data, decisao_da_titular ON regra BEGIN SELECT RAISE(ABORT,'regra não se altera: registre nova e marque a anterior como substituída'); END;
CREATE INDEX recibo_modulo ON recibo(modulo, em); CREATE INDEX medicao_em ON medicao(em); CREATE INDEX alarme_aberto ON alarme(fechado_em);
CREATE VIEW regra_vigente AS SELECT tema, regra, data FROM regra WHERE vigente = 1 AND substituida_por IS NULL;
CREATE VIEW alarmes_abertos AS SELECT gravidade, modulo, mensagem, aberto_em, repeticoes FROM alarme WHERE fechado_em IS NULL;
```

## 12. Parecer do conselho

**1. Extremamente pessimista — Dra. Ingrid Valdés.** “Três bancos com um gravador só: se o gravador aplicar um evento num banco e falhar no outro, eles divergem. A aplicação por evento precisa ser atômica em cada banco e conferida entre eles.”

**2. Pessimista — Prof. Kenji Morimoto.** “A busca sem cópia do texto não permite reconstruir o trecho a partir do índice; a página comprimida tem de existir sempre. A regra de imutabilidade da página protege isso.”

**3. Levemente pessimista — Eng. Rafaela Duarte.** “A migração de 3.668 livros com histórias incompletas vai gerar livros com lacunas. Elas devem aparecer como lacunas, e não como dados.”

**5. Levemente otimista — Eng. Mei Tanaka.** “As regras estão dentro do banco: mesmo um defeito no código não consegue apagar um livro.”

**6. Otimista — Prof. Diego Albuquerque.** “A visão da história do livro transforma o banco num relato legível, que a titular pode conferir livro a livro.”

**7. Extremamente otimista — Dra. Lucía Ferraz.** “O mesmo esquema serve a outra missão: o livro de contas públicas usa as mesmas tabelas, com outros itens.”

**Síntese do neutro — Dr. Antônio Brandt.** O esquema do banco está aprovado para a criação, com quatro parâmetros: (1) **cada evento aplicado de forma atômica** e registrado em `evento_aplicado` no banco em que atua; (2) **lacunas da migração marcadas como lacunas**; (3) **teste de reconstrução** dos bancos a partir dos eventos, toda semana; (4) **versão do esquema** controlada e migrações testadas antes de rodar.
