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


def test_o_portao_roda_na_producao():
    """24/10/2026: o portão falhou em todo ciclo por 5 horas porque a produção não instalava o pytest (o grupo 'testes')."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("instalar", "scripts/instalar_bibliotecas.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    assert "testes" in m.NUCLEO


def test_os_pilotos_concluem_com_os_dados_reais(tmp_path, monkeypatch):
    """24/10/2026 (o parecer exclusivo do encaminhamento): os três nós dos pilotos rodam sobre a cópia dos bancos reais e
    concluem; o Espião entrega o aprendizado pelos eventos (nada direto no arquivo)."""
    from types import SimpleNamespace

    from eldorado.base.cerebro import encaminhamento as E
    from eldorado.base.fluxo.nos import abrir_bancos
    from eldorado.base.nucleo.eventos import Diario, ler
    from eldorado.motores.acesso import completa
    from eldorado.motores.acesso.escada import Escada
    monkeypatch.setattr(completa, "escada_completa", lambda *a, **k: Escada([], intervalo_padrao=0))   # sem rede: rápido e determinístico
    for n in ("biblioteca", "cerebro"):
        shutil.copy(f"dados/{n}.db", tmp_path / f"{n}.db")
    for c in {id(x): x for x in abrir_bancos(tmp_path).values()}.values():
        c.close()
    antes = sqlite3.connect(tmp_path / "cerebro.db").execute("SELECT COUNT(*) FROM espiao_missao").fetchone()[0]
    ctx = SimpleNamespace(diario=Diario(tmp_path / "eventos"))
    par = {"dados": str(tmp_path), "modulos": "config/modulos.toml", "config": "config", "orcamento_s": 3, "orcamento_pilotos_s": 3,
           "orcamento_originais_s": 0, "intervalo_s": 0.1}
    for no in (E.no_encaminhar, E.no_espiao, E.no_originais):
        assert isinstance(no([], par, ctx), list)                                      # conclui (não levanta exceção)
    assert sqlite3.connect(tmp_path / "cerebro.db").execute("SELECT COUNT(*) FROM espiao_missao").fetchone()[0] == antes
    assert all(e.tipo in __import__("eldorado.base.nucleo.eventos", fromlist=["CATALOGO"]).CATALOGO for e in ler(tmp_path / "eventos"))
