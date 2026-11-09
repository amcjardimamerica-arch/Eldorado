"""O inventário: todo arquivo do código no catálogo, na ordem do funcionamento, e os 43 motores do projeto (a organização da titular de 09/11/2026, R50)."""
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
    assert len(m) == 61 and sum(x["tipo"] == "regular" for x in m) == 59   # R51 (09/11/2026): os 18 sites de divulgação and {x["id"] for x in m if x["tipo"] == "piloto"} == {"piloto-aberto", "piloto-interceptador"}
    assert {x["categoria"] for x in m} == {"EXE", "JUD", "LEG", "POR", "IA"} and sum(len(x["alvos"]) for x in m) == 86   # 09/11/2026 (titular): os 27 alvos «propostos para sair» saíram
    ordem = {a["arquivo"]: a["ordem"] for a in cat["arquivos"]}
    assert ordem["eldorado/base/nucleo/contratos.py"] < ordem["eldorado/base/cartorio/cartorio.py"] < ordem["eldorado/base/cartorio/analise_externa.py"]
    assert "## Os 61 motores" in mapa(cat)


def test_motores_conformes_ao_estudo_da_titular():
    import json
    import tomllib
    estudo = {m["id"]: m for m in json.loads(Path("config/motores_previstos.json").read_text(encoding="utf-8"))["motores"]}
    vistos: dict[str, str] = {}
    for p in Path("eldorado/motores/canal/config").glob("*.toml"):
        m = tomllib.loads(p.read_text(encoding="utf-8"))["motor"]
        assert m["id"] == p.stem and m["id"] in estudo, f"{m['id']} não é um motor do estudo"                 # um canal, um motor
        assert m.get("categoria_estudo") == estudo[m["id"]]["categoria"], m["id"]
        for antigo in m.get("nomes_anteriores", []):
            assert antigo not in vistos, f"{antigo} aponta para {vistos[antigo]} e {m['id']}"
            vistos[antigo] = m["id"]
