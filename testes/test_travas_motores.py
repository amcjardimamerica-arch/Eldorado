"""Travas das regras da titular sobre os motores (config/regras_titular.json)."""
import tomllib
import typing
from pathlib import Path

from eldorado.motores.canal import motor as M

ESCADA = {"api", "leve", "lightpanda", "patchright", "camoufox", "arquivo", "local"}


def test_a_escada_completa_e_o_padrao_e_esta_em_todo_motor():
    assert set(M.CfgAcesso().degraus) == ESCADA == set(typing.get_args(typing.get_args(M.CfgAcesso.model_fields["degraus"].annotation)[0]))
    faltam = {p.stem: sorted(ESCADA - set(tomllib.loads(p.read_text(encoding="utf-8")).get("acesso", {}).get("degraus", list(ESCADA))))
              for p in Path("eldorado/motores/canal/config").glob("*.toml")}
    assert not {k: v for k, v in faltam.items() if v}, faltam


def test_a_escada_vai_para_o_livro(tmp_path):
    import json
    import sqlite3

    from eldorado.base.cartorio.auditoria import escada_do_livro
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE achado (livro_id TEXT, motor TEXT, dados TEXT, encontrado_em TEXT)")
    con.execute("INSERT INTO achado VALUES ('L', 'dou', ?, '2026-10-24')", (json.dumps({"escada": {"motor": "dou", "degrau": "1 · API oficial"}}),))
    assert escada_do_livro(con, "L") == "dou · degrau 1 · API oficial"
    assert escada_do_livro(con, "sem-achado").startswith("livro migrado do Eldorado0")
