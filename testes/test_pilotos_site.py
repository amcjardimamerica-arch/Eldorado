"""Os pilotos no site ligados aos dados (titular, 25/10/2026: sem leitura na página inicial e na sala)."""
import shutil
import sqlite3

from eldorado.base.painel.dados import _molde
from eldorado.base.painel.pilotos import montar


def test_os_pilotos_tem_leitura(tmp_path):
    for n in ("biblioteca", "cerebro"):
        shutil.copy(f"dados/{n}.db", tmp_path / f"{n}.db")
    from eldorado.base.fluxo.nos import abrir_bancos
    for c in {id(x): x for x in abrir_bancos(tmp_path).values()}.values():
        c.close()
    arq, status = montar(sqlite3.connect(tmp_path / "biblioteca.db"), sqlite3.connect(tmp_path / "cerebro.db"), _molde)
    assert set(arq) == {"espiao.json", "espiao_ao_vivo.json", "interceptador.json", "interceptador_ao_vivo.json", "esquadrilha.json", "achados_pilotos.json"}
    assert all(arq[f].get("em") or arq[f].get("atualizado_em") for f in arq)                 # nenhum arquivo vazio
    assert set(status) == {"piloto-aberto", "piloto-interceptador"} and all(s["resultado"] for s in status.values())
    assert "ainda sem execução" not in " ".join(s["resultado"] for s in status.values())
