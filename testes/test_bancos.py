import sqlite3

import pytest

from eldorado.banco._sqlite import EsquemaIncompativel, integridade
from eldorado.banco.biblioteca import esquema as bib

EXIGIDAS = {
    "biblioteca": {"achado", "livro", "uniao", "passaporte", "passagem", "tentativa", "item", "documento", "pagina", "busca", "certidao",
                   "veredito", "relatorio_etapa", "analise_rede", "previsao", "transferencia", "lei", "calendario", "historia_do_livro"},
    "especial": {"empresa", "incentivo", "ranking", "oportunidade_empresa", "vinculo_livro", "aprofundamento"},
    "cerebro": {"modulo", "dominio", "workflow", "plano", "acionamento", "execucao", "execucao_passo", "recibo", "execucao_motor", "agenda",
                "cobertura_dia", "decisao_pertinencia", "medicao", "modelo", "rotulo", "regra", "aprendizado_temporario",
                "aprendizado_permanente", "alarme", "maquina"},
}


def test_os_tres_bancos_tem_as_tabelas_do_contrato(bancos):
    for nome, exigidas in EXIGIDAS.items():
        existentes = {r[0] for r in bancos[nome].execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')")}
        assert exigidas <= existentes, (nome, exigidas - existentes)
        assert integridade(bancos[nome])


def test_recibo_registra_processador_e_memoria(bancos):
    cols = {r[1] for r in bancos["cerebro"].execute("PRAGMA table_info(recibo)")}
    assert {"duracao_ms", "cpu_ms", "memoria_pico_kb"} <= cols


def test_reabrir_mantem_os_dados_e_a_versao(tmp_path):
    c = bib.abrir(tmp_path / "b.db")
    c.execute("INSERT INTO lei(id, atualizada_em) VALUES ('l1', 'x')")
    c.close()
    c = bib.abrir(tmp_path / "b.db")
    assert c.execute("SELECT COUNT(*) FROM lei").fetchone()[0] == 1
    assert c.execute("PRAGMA user_version").fetchone()[0] == bib.VERSAO


def test_banco_com_versao_diferente_e_recusado(tmp_path):
    c = bib.abrir(tmp_path / "b.db")
    c.execute("PRAGMA user_version=99")
    c.close()
    with pytest.raises(EsquemaIncompativel):
        bib.abrir(tmp_path / "b.db")


def test_regras_valem_mesmo_fora_do_gravador(bancos):
    b = bancos["biblioteca"]
    b.execute("INSERT INTO livro(id, missao, chave, situacao, criado_em, atualizado_em) VALUES ('L','o','k','em trabalho','x','x')")
    for sql in ("DELETE FROM livro", "UPDATE livro SET chave='outra'", "UPDATE livro SET situacao='excluido'"):
        with pytest.raises(sqlite3.Error):
            b.execute(sql)
