"""07/11/2026: a tentativa é numerada pelas anteriores do mesmo livro e ferramenta, e a repetida não abre alarme."""
import ast
from pathlib import Path

from eldorado.base.nucleo.eventos import CATALOGO


def test_nenhum_emissor_numera_a_tentativa_como_1_fixo():
    fixos = []
    for f in Path("eldorado").rglob("*.py"):
        t = ast.parse(f.read_text(encoding="utf-8"))
        for n in ast.walk(t):
            if (isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "emitir" and n.args and isinstance(n.args[0], ast.Constant)
                    and n.args[0].value == "tentativa.registrada" and len(n.args) > 2 and isinstance(n.args[2], ast.Dict)):
                for k, v in zip(n.args[2].keys, n.args[2].values):
                    if isinstance(k, ast.Constant) and k.value == "numero" and isinstance(v, ast.Constant):
                        fixos.append(f"{f}:{n.lineno}")
    assert not fixos, fixos


def test_a_tentativa_repetida_nao_e_recusada():
    assert CATALOGO["tentativa.registrada"][0].operacao == "inserir_se_novo"
