"""N-05 (manutenção de 25/11/2026): a cópia de segurança dos livros (a cada 3 dias) parou em 21/11.

Era o único passo do fim sem `if: always()`: quando um passo anterior falhava, o GitHub o pulava."""
from pathlib import Path

import yaml


def test_os_passos_de_guarda_do_fim_rodam_sempre():
    passos = yaml.safe_load(Path(".github/workflows/eldorado.yml").read_text(encoding="utf-8"))["jobs"]["passagem"]["steps"]
    por_nome = {p.get("name", ""): p for p in passos}
    exigidos = ["A manutenção dos bancos", "A cópia de segurança dos livros", "A cópia no Drive", "Consolidar os bancos",
                "Guarda do fim — salvar", "Gravar no repositório"]
    for prefixo in exigidos:
        achados = [p for n, p in por_nome.items() if n.startswith(prefixo)]
        assert achados, prefixo
        for p in achados:
            assert str(p.get("if", "")).strip() == "always()", f"{p['name']} sem if: always()"
