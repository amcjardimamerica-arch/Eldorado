"""05/11/2026 (titular: o sistema enxuto): o acúmulo que a análise dos arquivos sem uso revelou não volta."""
import gzip
import json
from datetime import datetime, timezone
from pathlib import Path

from eldorado.base.comandante import apresentar as A


def test_a_telemetria_compactada_nao_e_lida_duas_vezes_nem_fica_no_repositorio(tmp_path):
    from eldorado.base.nucleo.eventos import ler
    ev = tmp_path / "eventos"
    op = tmp_path / "operacao" / "2026" / "11" / "01"
    ev.mkdir()
    op.mkdir(parents=True)
    linha = json.dumps({"id": "1", "tipo": "sala.medida", "modulo": "m", "em": "2026-11-01T00:00:00+00:00", "dados": {}}) + "\n"
    (op / "x.jsonl").write_text(linha)
    (op / "x.jsonl.gz").write_bytes(gzip.compress(linha.encode()))
    assert len([e for e in ler(ev) if e.id == "1"]) == 1
    assert '[ ! -e "$RAIZ/$f.gz" ] || git update-index --force-remove "$f"' in Path("scripts/gravar.sh").read_text(encoding="utf-8")


def test_o_relatorio_do_ciclo_nao_e_regravado_a_cada_chamada(tmp_path, monkeypatch):
    agora = datetime(2026, 11, 5, 12, tzinfo=timezone.utc)
    (tmp_path / "2026-11-05-1100.json").write_text(json.dumps({"em": "2026-11-05T11:00:00+00:00"}))
    (tmp_path / "relatorio-melhoria-motores-grupo-3.json").write_text("{}")        # sem «em»: não é relatório do ciclo
    (tmp_path / "2026-10-30-0900.json").write_text(json.dumps({"em": "2026-10-30T09:00:00+00:00"}))
    monkeypatch.setattr(A, "reunir", lambda d, a: (_ for _ in ()).throw(AssertionError("não devia gravar")))
    assert A.apresentar(tmp_path, tmp_path, agora) is None
    assert not (tmp_path / "2026-10-30-0900.json").exists() and (tmp_path / "relatorio-melhoria-motores-grupo-3.json").exists()
