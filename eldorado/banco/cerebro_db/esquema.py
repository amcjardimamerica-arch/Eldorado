"""O esquema do banco do Cérebro (cerebro.db): a operação e o aprendizado do sistema, sem nenhuma oportunidade.

Esquema executado e testado em 22/10/2026. O banco só guarda, impõe as regras e oferece as visões; só o gravador escreve.
"""
from __future__ import annotations

from pathlib import Path

from .._sqlite import abrir as _abrir

VERSAO = 1

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


def abrir(caminho: str | Path):
    return _abrir(caminho, DDL, VERSAO)
