"""A sala de controle (titular, 24/10/2026): cada mostrador ligado ao dado medido; nenhum zerado por falta de ligação."""
import re
import shutil
import sqlite3
from pathlib import Path

from eldorado.base.painel.sala import ETAPAS, montar


def test_todo_instrumento_da_sala_e_medido(tmp_path):
    pagina = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    bloco = pagina[pagina.index("const ETAPAS=[   /* 18/10/2026"):]
    bloco = bloco[: bloco.index("];")]
    esperados = {i for lst in re.findall(r"ids:\[([^\]]*)\]", bloco) for i in re.findall(r'"([a-z_0-9]+)"', lst)}
    assert esperados == {i for lst in ETAPAS.values() for i in lst}                      # o que a página desenha é o que o sistema mede
    for n in ("biblioteca", "cerebro"):
        shutil.copy(f"dados/{n}.db", tmp_path / f"{n}.db")
    from eldorado.base.fluxo.nos import abrir_bancos
    for c in {id(x): x for x in abrir_bancos(tmp_path).values()}.values():
        c.close()
    r = montar(sqlite3.connect(tmp_path / "biblioteca.db"), sqlite3.connect(tmp_path / "cerebro.db"), Path("."), [{"id": "dou", "nome": "DOU", "luz": "verde"}])
    ids = {i["id"]: i for i in r["instrumentos"]}
    assert set(ids) == esperados
    for i in ids.values():                                  # valor vazio só com o estado cinza e o motivo dito
        assert i["valor"] is not None or (i["estado"] == "cinza" and i["motivo"]), i["id"]
    assert len(r["mimico"]) == 8 and r["indice_saude"] > 0 and len(r["compartimentos"]) == 9
