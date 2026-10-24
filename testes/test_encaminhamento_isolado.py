"""O parecer do conselho (24/10/2026): os sub-trabalhos do encaminhamento isolados; a falha de um não apaga os outros."""
from types import SimpleNamespace

from eldorado.base.cerebro import encaminhamento as E
from eldorado.base.nucleo.eventos import ler


def test_o_espiao_falhando_nao_apaga_os_outros(bancos, gravador, diario, tmp_path, monkeypatch):
    chamados = []
    monkeypatch.setattr(E.Encaminhamento, "andar", lambda self, orc, hoje=None: (chamados.append("interceptador") or ([], {})))
    import eldorado.base.cerebro.pilotos as P
    import eldorado.base.cerebro.originais as O
    monkeypatch.setattr(P, "missoes", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("o Espião quebrou")))
    monkeypatch.setattr(O, "vigiar", lambda *a, **k: (chamados.append("originais") or ([], {})))
    modulos = tmp_path / "modulos.toml"
    modulos.write_text("")
    r = E.no_encaminhar([], {"dados": str(tmp_path), "modulos": str(modulos), "config": "config"}, SimpleNamespace(diario=diario))
    assert r == [] and chamados == ["interceptador", "originais"]                  # os outros dois rodaram
    alarmes = [e for e in ler(tmp_path / "eventos") if e.tipo == "alarme.aberto"]
    assert any("espiao" in e.dados["modulo"] and "o Espião quebrou" in e.dados["mensagem"] for e in alarmes)
    assert gravador.aplicar(alarmes).ok                                             # o alarme é gravado (sem recusa)
