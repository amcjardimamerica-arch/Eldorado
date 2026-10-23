"""A API do sistema (FastAPI): a leitura do sistema real, sem mexer em nada."""
import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from eldorado.base.painel.api import criar_app  # noqa: E402


@pytest.fixture(scope="module")
def cliente():
    return TestClient(criar_app())


def test_saude_e_motores(cliente):
    s = cliente.get("/saude").json()
    assert s["esquema"] >= 7 and s["livros"] > 0 and "preparacao" in s["por_etapa"]
    m = cliente.get("/motores").json()
    assert len(m) == 47 and {"id", "luz", "resultado"} <= set(m[0])
    d = cliente.get("/motores/do-goias").json()
    assert d["configuracao"]["motor"]["id"] == "do-goias" and d["descricao"]["rotas"]
    assert cliente.get("/motores/nao-existe").status_code == 404


def test_livros_e_o_livro_com_certidoes_e_historia(cliente):
    lista = cliente.get("/livros", params={"limite": 5}).json()
    assert 0 < len(lista) <= 5
    lv = cliente.get(f"/livros/{lista[0]['id']}").json()
    assert lv["livro"]["id"] == lista[0]["id"] and isinstance(lv["certidoes"], list) and lv["historia"]
    assert cliente.get("/livros/nao-existe").status_code == 404
    assert all(a["id"] for a in cliente.get("/abertas").json()[:5])
