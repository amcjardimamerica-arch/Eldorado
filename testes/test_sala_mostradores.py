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


def test_o_servidor_mostra_a_rede(tmp_path):
    """25/10/2026 (a titular): o servidor do sistema com o uso da rede (a taxa pela diferença entre as duas últimas leituras)."""
    from eldorado.banco.biblioteca.esquema import abrir as ab
    from eldorado.banco.cerebro_db.esquema import abrir as ac
    b, c = ab(tmp_path / "b.db"), ac(tmp_path / "c.db")
    for em, ent, sai in (("2026-10-25T10:00:00+00:00", 1_000_000_000, 500_000_000), ("2026-10-25T10:05:00+00:00", 1_300_000_000, 530_000_000)):
        c.execute("INSERT INTO maquina(em, processador, memoria, disco, rede_entrada, rede_saida, nucleos) VALUES (?, .5, .4, .3, ?, ?, 4)", (em, ent, sai))
    c.commit()
    r = montar(b, c, Path("."), [])
    rede = next(i for i in r["maquina"]["instrumentos"] if i["id"] == "sv_rede")
    assert r["maquina"]["rede"] == {"entrada_mb_s": 1.0, "saida_mb_s": 0.1} and rede["valor"] == 0.9 and rede["estado"] == "verde"
    pagina = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    assert pagina.index('id="nv-tubo"') < pagina.index('class="vidro alarmes"') < pagina.index('id="nv-maquina"')   # trocaram de lugar
