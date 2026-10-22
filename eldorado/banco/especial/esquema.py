"""O esquema do Especial (especial.db): as empresas, os incentivos e as oportunidades nas empresas conhecidas.

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
"""


def abrir(caminho: str | Path):
    return _abrir(caminho, DDL, VERSAO)
