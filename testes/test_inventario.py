"""O inventário: todo arquivo do código no catálogo, na ordem do funcionamento, e os 47 motores do projeto."""
from pathlib import Path

from eldorado.base.cerebro.inventario import gerar, mapa


def test_inventario_do_sistema():
    cat = gerar(".")
    nomes = [a["arquivo"] for a in cat["arquivos"]]
    assert len(nomes) == len(set(nomes)) and [a["ordem"] for a in cat["arquivos"]] == list(range(1, len(nomes) + 1))
    codigo = {str(p) for p in Path("eldorado").rglob("*.py") if "__pycache__" not in p.parts}
    assert codigo <= set(nomes)                                                           # nenhum arquivo fora do catálogo
    assert all({"arquivo", "parte", "componente", "ligacoes", "critico", "metrica"} <= set(a) for a in cat["arquivos"])   # o que a medição lê
    m = cat["motores"]
    assert len(m) == 47 and sum(x["tipo"] == "regular" for x in m) == 45 and {x["id"] for x in m if x["tipo"] == "piloto"} == {"piloto-aberto", "piloto-interceptador"}
    ordem = {a["arquivo"]: a["ordem"] for a in cat["arquivos"]}
    assert ordem["eldorado/base/nucleo/contratos.py"] < ordem["eldorado/base/cartorio/cartorio.py"] < ordem["eldorado/base/cartorio/analise_externa.py"]
    assert "## Os 47 motores" in mapa(cat)
