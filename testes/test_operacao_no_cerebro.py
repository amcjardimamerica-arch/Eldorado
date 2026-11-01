"""01/11/2026 (titular): a telemetria vai ao Cérebro, completa, com 30 dias de retenção; fora do histórico permanente
(o alerta da Sala). E a localização de cada livro pelas próprias provas (a UF, o município e a esfera)."""

import sqlite3
from datetime import datetime, timedelta, timezone

from eldorado.base.cartorio.localizacao import provas
from eldorado.base.cerebro.retencao import reter
from eldorado.base.nucleo.eventos import CATALOGO, TIPOS_OPERACAO, Diario, ler, pasta_operacao


def test_a_telemetria_fica_fora_do_historico_mas_chega_ao_cerebro_e_ao_diario(tmp_path):
    pasta = tmp_path / "eventos"
    d = Diario(pasta, "exec-1")
    d.emitir("medicao.registrada", "teste", {"marcador": "x", "nivel": "n", "em": "2026-11-01T00:00:00+00:00", "ponto": "p", "valor": 1})
    d.emitir("execucao.passo", "teste", {"execucao": "exec-1", "passo": 1, "no": "a", "estado": "concluido", "entrada": [], "saida": []})
    historico = [a for a in pasta.rglob("*.jsonl")]
    assert not any(b"medicao.registrada" in a.read_bytes() or b"execucao.passo" in a.read_bytes() for a in historico)
    assert list(pasta_operacao(pasta).rglob("exec-1.jsonl"))
    assert {e.tipo for e in ler(pasta)} >= {"medicao.registrada", "execucao.passo"}  # vão ao banco
    assert {e.tipo for e in d.eventos()} >= {"execucao.passo"}  # a retomada os vê
    assert {"comandante.decidiu", "sala.medida", "arquivos.medidos", "chamada.recibo", "memoria.registrada"} <= TIPOS_OPERACAO


def test_a_retencao_apaga_so_o_que_passou_de_30_dias(tmp_path):
    db = tmp_path / "cerebro.db"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE medicao(marcador, em)")
    velho = (datetime.now(timezone.utc) - timedelta(days=31)).isoformat()
    novo = (datetime.now(timezone.utc) - timedelta(days=29)).isoformat()
    con.executemany("INSERT INTO medicao VALUES (?,?)", [("v", velho), ("n", novo)])
    con.commit()
    con.close()
    r = reter(db, tmp_path / "eventos")
    assert r["medicao"] == 1
    assert [x[0] for x in sqlite3.connect(db).execute("SELECT marcador FROM medicao")] == ["n"]


def test_a_localizacao_pelas_provas_do_livro():
    p = provas({"territorio": "Colinas do Sul/GO", "oficial": "https://colinasdosul.go.gov.br/x", "orgao": "Prefeitura Municipal de Colinas do Sul"})
    assert p["uf"] == "GO" and p["municipio"] == "Colinas do Sul" and p["esfera"] == "municipal"
    assert provas({"oficial": "https://goias.gov.br/secult"})["uf"] == "GO"
    assert "esfera" not in provas({"oficial": "https://secult.go.gov.br/x"})  # o domínio prova a UF, não a esfera municipal
    assert "livro.localizado" in CATALOGO


def test_a_telemetria_e_guardada_no_repositorio_e_compactada(tmp_path):
    """01/11/2026: a pasta operacao/ fica ao lado do histórico e vai ao repositório (o Cérebro é remontado com ela a cada
    execução: as decisões do Comandante sobrevivem); os dias passados viram .jsonl.gz, lidos de volta; e saem com 30 dias."""
    import gzip
    import os
    import time
    from pathlib import Path

    pasta = tmp_path / "eventos"
    assert pasta_operacao(pasta) == tmp_path / "operacao"
    assert "dados/operacao" not in Path(".gitignore").read_text(encoding="utf-8")
    assert "for pasta in eventos operacao " in Path("scripts/gravar.sh").read_text(encoding="utf-8")
    d = Diario(pasta, "exec-2")
    ev = d.emitir("comandante.decidiu", "teste", {"id": 1, "em": "2026-10-20T00:00:00+00:00", "etapa": "x", "acao": "y"})
    arq = next(pasta_operacao(pasta).rglob("exec-2.jsonl"))
    velho = pasta_operacao(pasta) / "2026" / "10" / "20"
    velho.mkdir(parents=True)
    (velho / "exec-2.jsonl").write_bytes(arq.read_bytes())
    os.utime(velho / "exec-2.jsonl", (time.time() - 5 * 3600, time.time() - 5 * 3600))
    antigo = pasta_operacao(pasta) / "2026" / "09" / "01"
    antigo.mkdir(parents=True)
    (antigo / "exec-0.jsonl").write_bytes(arq.read_bytes())
    db = tmp_path / "cerebro.db"
    sqlite3.connect(db).close()
    r = reter(db, pasta)
    assert r["arquivos_compactados"] >= 1 and r["arquivos_apagados"] == 1
    assert (velho / "exec-2.jsonl.gz").exists() and gzip.decompress((velho / "exec-2.jsonl.gz").read_bytes())
    assert sum(1 for e in ler(pasta) if e.id == ev.id) >= 1  # o compactado é lido de volta


def test_a_avaliacao_de_decisao_que_saiu_nao_vira_alerta():
    from eldorado.base.nucleo.gravador import DISPENSAVEIS

    assert {"comandante.avaliada", "livro.localizado"} <= DISPENSAVEIS
