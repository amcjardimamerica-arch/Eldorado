"""O esquema do banco do Cérebro (cerebro.db): a operação e o aprendizado do sistema, sem nenhuma oportunidade.

Esquema executado e testado em 22/10/2026. O banco só guarda, impõe as regras e oferece as visões; só o gravador escreve.
"""
from __future__ import annotations

from pathlib import Path

from .._sqlite import abrir as _abrir

VERSAO = 6

DDL = r"""
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
CREATE TABLE execucao (id TEXT PRIMARY KEY, workflow TEXT, versao INTEGER, inicio TEXT NOT NULL, fim TEXT, estado TEXT CHECK (estado IN ('rodando','concluida','falhou','retomada','aguardando')));
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
"""


# 2: o aprendizado dos motores e do Espião DENTRO do Cérebro (titular, 24/10/2026: só o Cérebro tem um banco paralelo, o de
# aprendizado; antes, cada motor tinha o seu arquivo em dados/motores/<id>.db, e o Espião, espiao.db)
DDL_V2 = r"""
CREATE TABLE IF NOT EXISTS motor_assinatura (motor TEXT NOT NULL, fonte TEXT NOT NULL, valor TEXT NOT NULL, em TEXT NOT NULL, PRIMARY KEY (motor, fonte));
CREATE TABLE IF NOT EXISTS motor_mapa_url (motor TEXT NOT NULL, dominio TEXT NOT NULL, url TEXT NOT NULL, primeira_vez TEXT NOT NULL,
  PRIMARY KEY (motor, dominio, url));
CREATE TABLE IF NOT EXISTS motor_mapa_dominio (motor TEXT NOT NULL, dominio TEXT NOT NULL, verificado_em TEXT NOT NULL, urls INTEGER,
  PRIMARY KEY (motor, dominio));
CREATE TABLE IF NOT EXISTS motor_alvo_mudanca (motor TEXT NOT NULL, alvo TEXT NOT NULL, em TEXT NOT NULL, mes INTEGER NOT NULL, PRIMARY KEY (motor, alvo, em));
CREATE TABLE IF NOT EXISTS motor_entregue (motor TEXT NOT NULL, chave TEXT NOT NULL, em TEXT NOT NULL, achado TEXT, fonte TEXT, PRIMARY KEY (motor, chave));
CREATE INDEX IF NOT EXISTS motor_entregue_achado ON motor_entregue(motor, achado);
CREATE TABLE IF NOT EXISTS motor_fonte (motor TEXT NOT NULL, nome TEXT NOT NULL, leituras INTEGER NOT NULL DEFAULT 0, sem_mudanca INTEGER NOT NULL DEFAULT 0,
  achados INTEGER NOT NULL DEFAULT 0, aceitos INTEGER NOT NULL DEFAULT 0, barrados INTEGER NOT NULL DEFAULT 0, falhas INTEGER NOT NULL DEFAULT 0,
  ultimo_erro TEXT, ultima TEXT, situacao TEXT, PRIMARY KEY (motor, nome));
CREATE TABLE IF NOT EXISTS motor_retorno (motor TEXT NOT NULL, achado TEXT NOT NULL, fonte TEXT, decisao TEXT, motivo TEXT, em TEXT NOT NULL,
  PRIMARY KEY (motor, achado));
CREATE TABLE IF NOT EXISTS espiao_familia (nome TEXT PRIMARY KEY, a REAL NOT NULL DEFAULT 1, b REAL NOT NULL DEFAULT 1, usos INTEGER NOT NULL DEFAULT 0,
  achados INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS espiao_consulta (texto TEXT PRIMARY KEY, familia TEXT, usos INTEGER NOT NULL DEFAULT 0,
    achados INTEGER NOT NULL DEFAULT 0, ultima TEXT);
CREATE TABLE IF NOT EXISTS espiao_missao (id INTEGER PRIMARY KEY, em TEXT NOT NULL, familia TEXT, consulta TEXT, resultados INTEGER, candidatos INTEGER,
  achados INTEGER, motivos TEXT, rotas TEXT, bloqueada INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS espiao_rota (nome TEXT PRIMARY KEY, descansa_ate TEXT);
"""
# 3: o Cérebro jamais guarda livros (titular, 24/10/2026): as entradas e saídas dos passos passam a ser só o resumo (quantos
# itens), e o conteúdo dos achados que já estava gravado é apagado
DDL_V3 = r"""
UPDATE execucao_passo SET entrada = CASE WHEN json_valid(entrada) AND json_type(entrada) = 'array' THEN json_object('itens', json_array_length(entrada)) END,
  saida = CASE WHEN json_valid(saida) AND json_type(saida) = 'array' THEN json_object('itens', json_array_length(saida)) END
"""

# 4: o mapa do site visto por domínio numa linha (a lista das URLs), entregue pelo motor por evento
DDL_V4 = r"""
ALTER TABLE motor_mapa_dominio ADD COLUMN vistas TEXT
"""

# 5: o monitoramento de cada arquivo (titular, 24/10/2026): a medição atual e a do dia (o ponto, o círculo e as ligações)
DDL_V5 = r"""
CREATE TABLE IF NOT EXISTS medicao_arquivos (chave TEXT PRIMARY KEY, em TEXT NOT NULL, dados TEXT NOT NULL)
"""

# 6: a releitura dos documentos herdados sem texto: as tentativas (aprendizado; o texto vai para o livro, na Biblioteca)
DDL_V6 = r"""
CREATE TABLE IF NOT EXISTS releitura (documento_id INTEGER PRIMARY KEY, tentativas INTEGER NOT NULL, ultima TEXT NOT NULL, resultado TEXT)
"""


def abrir(caminho: str | Path):
    """Na criação, o esquema inteiro (com a versão 2); um Cérebro na versão 1 é migrado (as tabelas motor_* e espiao_*)."""
    return _abrir(caminho, DDL + ";\n" + DDL_V2 + ";\n" + DDL_V4 + ";\n" + DDL_V5 + ";\n" + DDL_V6, VERSAO,
                  {2: DDL_V2, 3: DDL_V3, 4: DDL_V4, 5: DDL_V5, 6: DDL_V6})
