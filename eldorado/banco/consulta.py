"""A consulta da Biblioteca (plano C: Datasette), só leitura, com consultas prontas.

eldorado consultar --porta 8001
"""

from __future__ import annotations

import json
from pathlib import Path

METADADOS = {
    "title": "Eldorado — consulta da Biblioteca (só leitura)",
    "databases": {
        "biblioteca": {
            "queries": {
                "abertas": {
                    "title": "Oportunidades abertas",
                    "sql": "SELECT l.id, l.titulo, l.orgao, l.uf, d.inscricao_fim, l.link_oficial FROM livro l "
                    "JOIN livro_dados d ON d.livro_id = l.id WHERE d.situacao_prazo = 'aberta' "
                    "AND l.situacao NOT IN ('excluido', 'unido') ORDER BY d.inscricao_fim",
                },
                "farol": {
                    "title": "Livros no Farol",
                    "sql": "SELECT l.id, l.titulo, l.orgao, l.estrela FROM livro l JOIN passaporte p ON p.livro_id = l.id WHERE p.fase = 'farol'",
                },
                "certidoes_do_livro": {
                    "title": "As certidões de um livro",
                    "sql": "SELECT item, valor, situacao, fase, trecho, em FROM certidao WHERE livro_id = :livro ORDER BY em",
                },
                "origem": {
                    "title": "A origem dos livros",
                    "sql": "SELECT origem, origem_motivo, COUNT(*) AS livros FROM livro_dados GROUP BY 1, 2 ORDER BY 3 DESC",
                },
            }
        }
    },
}


def servir(porta: int = 8001, dados: Path = Path("dados")) -> None:
    import subprocess
    import sys
    import tempfile

    meta = Path(tempfile.gettempdir()) / "eldorado_datasette.json"
    meta.write_text(json.dumps(METADADOS, ensure_ascii=False), encoding="utf-8")
    bancos = [str(p) for p in (dados / "biblioteca.db", dados / "cerebro.db") if p.exists()]
    subprocess.run(
        [
            sys.executable,
            "-m",
            "datasette",
            "serve",
            *[f"--immutable={b}" for b in bancos],
            "--metadata",
            str(meta),
            "--port",
            str(porta),
            "--setting",
            "sql_time_limit_ms",
            "5000",
        ],
        check=False,
    )
