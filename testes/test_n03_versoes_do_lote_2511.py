"""N-03 (manutenção de 25/11/2026; a titular autorizou em 25/11/2026 apagar do repositório as versões de lote com mais de
7 dias sem veredito pendente): verificacao/lotes/versoes/ tinha 1.496 arquivos (2,4 GB) — a mesma geração do lote
gravada de novo a cada 5 minutos, e a retenção de 7 dias só apagava na máquina. R41 (a versão que o Chrome recebeu
precisa existir), R35."""
from __future__ import annotations

import json
import subprocess
from datetime import date
from pathlib import Path

from eldorado.base.cartorio import analise_externa as ae

LIVROS = [{"livro_id": i} for i in "ABC"]


def _lote(gerado_em: str, livros=LIVROS) -> dict:
    return {"lote": "lote-2026-11-25-externa-completo", "gerado_em": gerado_em, "total_livros": len(livros), "livros": livros}


def test_lote_identico_nao_gera_versao_nova(tmp_path):
    p = tmp_path / "lotes"
    nome = "lote-2026-11-25-externa-completo"
    ae.guardar_versao(p, nome, _lote("2026-11-25T17:50:00+00:00"))
    ae.guardar_versao(p, nome, _lote("2026-11-25T17:55:00+00:00"))                 # a mesma geração, 5 min depois
    assert len(list((p / "versoes").glob("lote-*.json"))) == 1
    ae.guardar_versao(p, nome, _lote("2026-11-25T18:00:00+00:00", LIVROS + [{"livro_id": "D"}]))   # mudança real
    assert len(list((p / "versoes").glob("lote-*.json"))) == 2


def test_o_veredito_acha_a_versao_pelo_conteudo(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    p = tmp_path / "verificacao/lotes"
    nome = "lote-x"
    ae.guardar_versao(p, nome, {"lote": nome, "gerado_em": "2026-11-25T15:00:00+00:00", "livros": [{"livro_id": "A"}]})
    ae.guardar_versao(p, nome, {"lote": nome, "gerado_em": "2026-11-25T15:05:00+00:00", "livros": [{"livro_id": "A"}]})   # apelido
    (p / "lote-x.json").write_text(json.dumps({"lote": nome, "gerado_em": "2026-11-25T20:00:00+00:00",
                                                "livros": [{"livro_id": i} for i in "ABCD"]}), encoding="utf-8")
    v = ae.arquivo_da_versao(p, nome, "2026-11-25T15:05:00+00:00")
    assert v is not None and [x["livro_id"] for x in json.loads(v.read_text(encoding="utf-8"))["livros"]] == ["A"]
    import sqlite3
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE passaporte (livro_id TEXT, fase TEXT, entrou_em TEXT)")
    con.executemany("INSERT INTO passaporte VALUES (?, 'analise externa', '2026-11-01')", [(i,) for i in "ABCD"])
    r = ae.Retorno(lote=nome, lote_gerado_em="2026-11-25T15:05:00+00:00", vereditos=[ae.Veredito(livro_id="A", decisao="valido")])
    assert ae.conferir_completo(r, con, p) == []        # a versão das 15:05 (idêntica à das 15:00) tinha só o A


def test_um_veredito_de_lote_antigo_ainda_e_importado(tmp_path):
    """O veredito pendente segura a versão de 7 dias ou mais (critério de aceite 3)."""
    p = tmp_path / "lotes"
    ver = tmp_path / "vereditos"
    ver.mkdir()
    ae.guardar_versao(p, "lote-2026-11-10", {"lote": "lote-2026-11-10", "gerado_em": "2026-11-10T10:00:00+00:00", "livros": LIVROS})
    ae.guardar_versao(p, "lote-2026-11-11", {"lote": "lote-2026-11-11", "gerado_em": "2026-11-11T10:00:00+00:00", "livros": LIVROS})
    (ver / "v.json").write_text(json.dumps({"lote": "lote-2026-11-10", "lote_gerado_em": "2026-11-10T10:00:00+00:00", "vereditos": []}),
                                encoding="utf-8")
    r = ae.limpar_versoes(p, date(2026, 11, 25), ver)
    assert r["vencidas"] == 1
    assert ae.arquivo_da_versao(p, "lote-2026-11-10", "2026-11-10T10:00:00+00:00") is not None   # o pendente ficou
    assert ae.arquivo_da_versao(p, "lote-2026-11-11", "2026-11-11T10:00:00+00:00") is None       # o vencido saiu


def test_as_versoes_repetidas_ja_gravadas_viram_apelido_uma_vez(tmp_path):
    pv = tmp_path / "lotes" / "versoes"
    pv.mkdir(parents=True)
    for h in ("100000Z", "100500Z", "101000Z"):
        (pv / f"lote-2026-11-24@2026-11-24T{h}.json").write_text(json.dumps({"lote": "lote-2026-11-24", "gerado_em": h, "livros": LIVROS}))
    r = ae.limpar_versoes(tmp_path / "lotes", date(2026, 11, 25), None)
    assert r["duplicadas"] == 2 and len(list(pv.glob("lote-*.json"))) == 1
    assert ae.arquivo_da_versao(tmp_path / "lotes", "lote-2026-11-24", "2026-11-24T101000Z") is not None


def test_a_gravacao_tira_do_repositorio_a_versao_vencida(tmp_path):
    """A gravação tira do repositório só o que a máquina tirou: vencida (7 dias) ou repetida; nunca a que ainda não veio."""
    p = tmp_path / "lotes"
    pv = p / "versoes"
    pv.mkdir(parents=True)
    (pv / "indice.json").write_text(json.dumps({"apelidos": {"lote-2026-11-24@2026-11-24T100500Z": "lote-2026-11-24@2026-11-24T100000Z.json"},
                                                "ultimo": {}}), encoding="utf-8")
    (pv / "lote-2026-11-24@2026-11-24T100000Z.json").write_text("{}")
    repo = ["verificacao/lotes/versoes/lote-2026-11-01@2026-11-01T100000Z.json",     # vencida, fora da máquina: sai
            "verificacao/lotes/versoes/lote-2026-11-24@2026-11-24T100500Z.json",     # repetida (apelido): sai
            "verificacao/lotes/versoes/lote-2026-11-24@2026-11-24T100000Z.json",     # na máquina: fica
            "verificacao/lotes/versoes/lote-2026-11-25@2026-11-25T120000Z.json"]     # nova, ainda não veio: fica
    assert ae.versoes_a_tirar_do_repositorio(repo, p, date(2026, 11, 25)) == repo[:2]
    s = Path("scripts/gravar.sh").read_text(encoding="utf-8")
    assert 'git ls-files "verificacao/lotes/versoes/*.json" 2>/dev/null | eldorado versoes-a-tirar' in s
    assert subprocess.run(["bash", "-n", "scripts/gravar.sh"]).returncode == 0
