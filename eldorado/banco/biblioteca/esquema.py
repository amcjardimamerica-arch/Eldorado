"""O esquema da Biblioteca (biblioteca.db): os livros e tudo o que se sabe de cada oportunidade.

Esquema executado e testado em 22/10/2026. O banco só guarda, impõe as regras e oferece as visões; só o gravador escreve.
"""
from __future__ import annotations

from pathlib import Path

from .._sqlite import abrir as _abrir

VERSAO = 8

DDL_V2 = r"""
CREATE TABLE livro_dados (livro_id TEXT PRIMARY KEY REFERENCES livro(id),
  abrangencia TEXT CHECK (abrangencia IN ('municipal_go','estadual_go','capital_outro_estado','municipal_fora_go','estadual_outro_estado','nacional','internacional','indeterminado')),
  municipio TEXT, uf TEXT, esfera TEXT CHECK (esfera IN ('municipal','estadual','federal','privada','internacional') OR esfera IS NULL),
  inscricao_inicio TEXT, inscricao_fim TEXT, resultado_em TEXT, recurso_dias INTEGER, valor_min REAL, valor_max REAL, modalidade TEXT, area TEXT,
  situacao_prazo TEXT CHECK (situacao_prazo IN ('aberta','encerrada','sem prazo')),
  link_oficial_tipo TEXT CHECK (link_oficial_tipo IN ('fonte','republicador','ausente')),
  validacao TEXT NOT NULL CHECK (validacao IN ('aprovado','revisar','expurgado')), motivos TEXT, validado_em TEXT NOT NULL);
CREATE INDEX livro_dados_abrangencia ON livro_dados(abrangencia);
CREATE INDEX livro_dados_prazo ON livro_dados(situacao_prazo, inscricao_fim)
"""

DDL = r"""
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
"""


DDL_V3 = r"""
CREATE TABLE expurgo_externo (id INTEGER PRIMARY KEY, em TEXT NOT NULL, por TEXT NOT NULL, motivo TEXT NOT NULL, livros INTEGER NOT NULL,
  linhas INTEGER NOT NULL, ids TEXT NOT NULL);
CREATE TRIGGER expurgo_externo_sem_alteracao BEFORE UPDATE ON expurgo_externo BEGIN SELECT RAISE(ABORT, 'o registro do expurgo não se altera'); END;
CREATE TRIGGER expurgo_externo_sem_apagar BEFORE DELETE ON expurgo_externo BEGIN SELECT RAISE(ABORT, 'o registro do expurgo não se apaga'); END
"""

DDL_V4 = r"""
CREATE TABLE livro_lei (livro_id TEXT NOT NULL REFERENCES livro(id), lei_id TEXT NOT NULL REFERENCES lei(id), papel TEXT NOT NULL,
  em TEXT NOT NULL, PRIMARY KEY (livro_id, lei_id));
CREATE INDEX livro_lei_lei ON livro_lei(lei_id)
"""

DDL_V5 = r"""
CREATE TABLE passaporte_v5 (livro_id TEXT PRIMARY KEY REFERENCES livro(id),
  fase TEXT NOT NULL CHECK (fase IN ('recepcao','certificacao','preparacao','validacao','analise externa','farol')), entrou_em TEXT NOT NULL);
INSERT INTO passaporte_v5 SELECT livro_id, CASE fase WHEN 'coleta' THEN 'recepcao' WHEN 'investigacao' THEN 'preparacao'
  WHEN 'verificacao externa' THEN 'analise externa' ELSE fase END, entrou_em FROM passaporte;
DROP TABLE passaporte;
ALTER TABLE passaporte_v5 RENAME TO passaporte
"""

DDL_V6 = r"""
CREATE TABLE passaporte_v6 (livro_id TEXT PRIMARY KEY REFERENCES livro(id),
  fase TEXT NOT NULL CHECK (fase IN ('recepcao','certificacao','preparacao','validacao','analise externa','farol','arquivo')),
  entrou_em TEXT NOT NULL);
INSERT INTO passaporte_v6 SELECT livro_id, fase, entrou_em FROM passaporte;
DROP TABLE passaporte;
ALTER TABLE passaporte_v6 RENAME TO passaporte
"""

DDL_V7 = r"""
ALTER TABLE livro_dados ADD COLUMN origem TEXT;
ALTER TABLE livro_dados ADD COLUMN origem_motivo TEXT
"""

DDL_V8 = r"""
ALTER TABLE livro_dados ADD COLUMN escada TEXT
"""

MIGRACOES = {2: DDL_V2, 3: DDL_V3, 4: DDL_V4, 5: DDL_V5, 6: DDL_V6, 7: DDL_V7, 8: DDL_V8}   # 2: a decupagem (livro_dados); 3: o registro do expurgo; 4: a legislação (livro_lei);
# 5: as 5 fases do Cartório no passaporte (titular, 22/10/2026); 6: o arquivo (o livro aguardando nova oportunidade);
# 7: a origem decidida por livro (confirmado, candidato, ausente) e o motivo (titular, 23/10/2026);
# 8: a escada no livro (o motor e o degrau de acesso que obtiveram a oportunidade; titular, 24/10/2026)


def abrir(caminho: str | Path):
    return _abrir(caminho, DDL + ";\n" + DDL_V2 + ";\n" + DDL_V3 + ";\n" + DDL_V4 + ";\n" + DDL_V5 + ";\n" + DDL_V6 + ";\n" + DDL_V7 + ";\n" + DDL_V8, VERSAO, MIGRACOES)
