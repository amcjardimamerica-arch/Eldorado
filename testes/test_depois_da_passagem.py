"""01/11/2026 (titular: o alerta "8.704 documentos sem texto lido"): a manutenção depois de cada passagem (o expurgo e o
descarte da R35, a retenção de 30 dias, a memória devolvida) ficava no caminho do retorno normal de _rodar, que nunca
retorna (termina sempre com typer.Exit): nunca rodou na produção. E o indicador da Sala media a R35 funcionando."""

import re
import sqlite3
from pathlib import Path

from eldorado.base.nucleo import comandos


def test_a_manutencao_roda_em_todo_termino_real_da_passagem():
    fonte = Path(comandos.__file__).read_text(encoding="utf-8")
    corpo = fonte[fonte.index("def permanente(") :]
    assert "def _depois_da_passagem() -> None:" in corpo
    ramo_exit = corpo[corpo.index("except typer.Exit as e:") : corpo.index("except Exception as e:  # noqa: BLE001 — o funcionamento é permanente")]
    assert "if e.exit_code != ADIADO:" in ramo_exit and "_depois_da_passagem()" in ramo_exit
    rotina = corpo[corpo.index("def _depois_da_passagem") : corpo.index("    while True:")]
    for parte in ("_expurgar_leituras(", "_reter(", "liberar_memoria()"):
        assert parte in rotina
    # o caminho do retorno normal não guarda mais nada sozinho (o que existir ali também está na rotina)
    assert re.search(r"_rodar\(workflow, config, None, None, \"leve\"\)\n.*\n\s+_depois_da_passagem\(\)", corpo)


def test_sem_texto_lido_e_a_leitura_que_nao_extraiu_texto(tmp_path):
    """O documento lido e certificado, com a leitura fora do banco pela R35, não conta; conta a leitura sem texto."""
    from eldorado.base.painel import sala

    fonte = Path(sala.__file__).read_text(encoding="utf-8")
    assert "COALESCE(d.paginas, 0) = 0" in fonte and 'NOT EXISTS (SELECT 1 FROM pagina p WHERE p.documento_id = d.id)"\n    herd' not in fonte
    con = sqlite3.connect(tmp_path / "b.db")
    con.execute("CREATE TABLE documento(id, leitor, paginas)")
    con.executemany(
        "INSERT INTO documento VALUES (?,?,?)",
        [(1, "pdf (PyMuPDF)", 3), (2, "página (selectolax + resiliparse)", 0), (3, "Eldorado0 (sem o texto)", 0)],
    )
    lidos, herd, zero = "d.leitor IS NOT NULL AND d.leitor <> ''", "d.leitor LIKE 'Eldorado0%'", "COALESCE(d.paginas, 0) = 0"
    assert con.execute(f"SELECT COUNT(*) FROM documento d WHERE {lidos} AND NOT ({herd}) AND {zero}").fetchone()[0] == 1
