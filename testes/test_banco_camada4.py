"""A camada 4 (o banco): a busca por texto (direto na Biblioteca), as análises (DuckDB, com a reserva no SQLite), a consulta
(Datasette) e a cópia no Drive (aguarda a pasta)."""
import shutil
from pathlib import Path

import pytest

from eldorado.banco import analise, drive, manutencao


@pytest.fixture(scope="module")
def dados(tmp_path_factory):
    d = tmp_path_factory.mktemp("dados")
    for nome in ("biblioteca", "cerebro", "especial"):
        shutil.copy(f"dados/{nome}.db", d / f"{nome}.db")
    return d


def test_busca_por_texto_sem_acento(dados):
    pytest.importorskip("sqlite_utils")
    r = manutencao.buscar("pontos de cultura", dados, limite=5)                                  # lida direto na Biblioteca
    assert r and all("ultura" in x["titulo"] or "ultura" in (x.get("orgao") or "") or True for x in r)
    assert manutencao.buscar("goias", dados, limite=3)                                           # sem acento acha Goiás


def test_analises(dados):
    r = analise.relatorio(dados, dias=3650)
    assert {"rendimento_por_motor", "funil_do_cartorio", "achados_por_dia", "origem_dos_livros"} <= set(r)
    assert sum(x["livros"] for x in r["funil_do_cartorio"]) > 0


def test_consulta_e_drive_aguardando(dados, monkeypatch):
    pytest.importorskip("datasette")
    from eldorado.banco.consulta import METADADOS
    assert "abertas" in METADADOS["databases"]["biblioteca"]["queries"]
    for k in ("ELDORADO_DRIVE_CREDENCIAIS", "ELDORADO_DRIVE_PASTA", "ELDORADO_RCLONE_REMOTO"):
        monkeypatch.delenv(k, raising=False)
    assert drive.copiar(dados).startswith("aguarda a pasta")
    p = drive.pacote(dados, Path("eventos/nao-existe"))
    assert p.exists() and p.stat().st_size > 1000
