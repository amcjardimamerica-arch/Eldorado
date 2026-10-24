"""Testes de fumaça sobre os DADOS REAIS (24/10/2026): os dois defeitos que derrubaram todas as passagens desde a
meia-noite só apareciam com o banco real (os testes usavam bancos pequenos). Estes rodam no portão."""
import re
import shutil
import sqlite3
from pathlib import Path


def test_o_cerebro_treina_com_o_banco_real(tmp_path):
    from eldorado.base.cerebro.rede import RedeNeural
    for n in ("biblioteca", "cerebro"):
        shutil.copy(f"dados/{n}.db", tmp_path / f"{n}.db")
    rede = RedeNeural.treinar(sqlite3.connect(tmp_path / "biblioteca.db"), sqlite3.connect(tmp_path / "cerebro.db"))
    assert rede.metricas()["oportunidade"]["amostras"] > 100                    # treinou, sem erro (o lote incluído)


def test_nenhum_codigo_pede_o_id_na_configuracao():
    """A configuração do motor guarda o id em cfg.motor.id; cfg.id derrubou o encaminhamento (156 passagens)."""
    erros = [f"{p}:{i}" for p in Path("eldorado").rglob("*.py") for i, linha in enumerate(p.read_text(encoding="utf-8").splitlines(), 1)
             if re.search(r"\bcfg\.id\b", linha)]
    assert not erros, erros
