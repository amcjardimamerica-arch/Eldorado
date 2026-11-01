"""01/11/2026 (titular): "somente o Claude apaga livros e faz expurgos, o sistema não faz"; "faça a avaliação antes de
expurgar"; os migrados do Eldorado0 são histórico, sem nova releitura nem avaliação (salvo os abertos)."""

import json
import sqlite3
from pathlib import Path

from eldorado.base.cartorio import expurgo_claude
from eldorado.base.cartorio.migrados import e_migrado, sql_migrado


def test_os_migrados_sao_identificados_e_ficam_fora_da_fila_do_interceptador():
    assert e_migrado("op-690f9928042c") and e_migrado("captacao-056") and not e_migrado("L-c96fd99ed858939d")
    fonte = Path("eldorado/motores/pilotos/interceptador.py").read_text(encoding="utf-8")
    assert "f\"AND NOT ({sql_migrado()} AND COALESCE(d.inscricao_fim, '') < ?)\", (hoje,)" in fonte  # o aberto fica
    assert "l.id LIKE 'op-%'" in sql_migrado()


def test_a_ferramenta_so_indica_e_registra(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    con = sqlite3.connect(":memory:")
    con.executescript("""CREATE TABLE documento(id, obtido_em); CREATE TABLE certidao(documento_id);
      CREATE TABLE achado(id, livro_id, decisao, encontrado_em, motor, documento_id);
      INSERT INTO documento VALUES (1,'2026-10-01'),(2,'2026-10-01'); INSERT INTO certidao VALUES (1);
      INSERT INTO achado VALUES ('a',NULL,'descartar','2026-10-01','motor-x',NULL),('b',NULL,'descartar','2026-10-01','alego-pl',NULL);""")
    Path("verificacao/migrados").mkdir(parents=True)
    Path("verificacao/migrados/parte-1.json").write_text(
        json.dumps({"itens": [{"id": "op-1", "veredito": None}, {"id": "op-2", "veredito": "manter"}]})
    )
    c = expurgo_claude.candidatos(con)
    assert c == {"documentos_sem_uso": 1, "achados_sem_livro": 1, "migrados_no_chrome": 1, "total": 3}
    assert con.execute("SELECT COUNT(*) FROM documento").fetchone()[0] == 2  # nada saiu
    assert expurgo_claude.ultimo() is None
    expurgo_claude.registrar({"documentos": 1}, "teste", quando="2026-11-02T10:00:00+00:00")
    assert expurgo_claude.ultimo()["motivo"] == "teste"


def test_a_sala_mostra_o_ultimo_expurgo_e_os_indicados():
    fonte = Path("eldorado/base/painel/sala.py").read_text(encoding="utf-8")
    assert '"es_expurgo"' in fonte and "o sistema não apaga; o Claude avalia e expurga" in fonte
    assert Path("expurgos/2026-10-30T115556.json").exists()
    assert sum(len(json.loads(Path(f"verificacao/migrados/parte-{i}.json").read_text(encoding="utf-8"))["itens"]) for i in (1, 2, 3)) == 716
