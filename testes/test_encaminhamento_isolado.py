"""O parecer do conselho (24/10/2026): os pilotos em nós próprios; a falha de um não apaga os outros."""
import tomllib
from pathlib import Path
from types import SimpleNamespace

from eldorado.base.cerebro import encaminhamento as E


def test_o_espiao_falhando_nao_apaga_os_outros(bancos, gravador, diario, tmp_path, monkeypatch):
    d = tomllib.loads(Path("workflows/passagem.toml").read_text(encoding="utf-8"))
    tipos = {n["id"]: n["tipo"] for n in d["no"]}
    assert tipos["espiao"].endswith(":no_espiao") and tipos["originais"].endswith(":no_originais")
    entradas = {c["de"] for c in d["conexao"] if c["para"] == "decidir_rede" and c.get("saida", "principal") == "principal"}
    assert {"encaminhar", "espiao", "originais"} <= entradas                    # a decisão recebe de cada um, separadamente
    import eldorado.base.cerebro.pilotos as P
    monkeypatch.setattr(P, "missoes", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("o Espião quebrou")))
    vigiados = []
    import eldorado.base.cerebro.originais as O
    monkeypatch.setattr(O, "vigiar", lambda *a, **k: (vigiados.append(1) or ([], {})))
    modulos = tmp_path / "modulos.toml"
    modulos.write_text("")
    ctx = SimpleNamespace(diario=diario)
    par = {"dados": str(tmp_path), "modulos": str(modulos), "config": "config"}
    try:
        E.no_espiao([], par, ctx)
        quebrou = False
    except RuntimeError:
        quebrou = True
    assert quebrou                                                               # o nó do Espião falha sozinho (o executor registra)
    assert E.no_originais([], par, ctx) == [] and vigiados == [1]                # e os sites originais rodam normalmente


def test_a_escada_dos_pilotos_e_a_completa():
    from eldorado.motores.acesso.completa import ORDEM
    assert ORDEM == ("api", "leve", "ponte", "lightpanda", "patchright", "camoufox", "arquivo", "local")   # a ponte BR (25/10/2026)
    import inspect
    assert "escada_completa" in inspect.getsource(E._contexto_pilotos)
