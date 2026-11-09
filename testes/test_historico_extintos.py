"""09/11/2026 (R50): o histórico dos 14 motores extintos conta no motor que os reúne — na pontuação, no mostrador e na Bússola."""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from eldorado.base.cerebro.pontuacao_motores import calcular
from eldorado.base.painel.dados import APELIDO
from eldorado.motores.canal.motor import apelidos


def test_os_extintos_tem_um_motor_que_os_reune():
    ap = apelidos()
    for velho, novo in {"site-rede-comua": "fundacoes-nacionais", "site-fundo-casa": "fundacoes-nacionais", "salic": "governo-federal",
                        "motor-gife": "novo-fundacoes-institutos", "site-mapas-culturais": "plataforma-mapas-culturais",
                        "site-undef": "novo-internacional", "outros-agregadores": "editais-do-brasil"}.items():
        assert ap.get(velho) == novo and APELIDO(velho) == novo
    assert APELIDO("dou") == "dou"


def test_o_achado_do_extinto_pontua_no_motor_que_o_reune(tmp_path):
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "pontuacao_motores.toml").write_text(Path("config/pontuacao_motores.toml").read_text(encoding="utf-8"), encoding="utf-8")
    b = sqlite3.connect(":memory:")
    b.executescript("CREATE TABLE achado(livro_id TEXT, motor TEXT, encontrado_em TEXT, decisao TEXT);"
                    "CREATE TABLE livro(id TEXT, situacao TEXT, criado_em TEXT, justificativa_exclusao TEXT, estrela TEXT);"
                    "CREATE TABLE passaporte(livro_id TEXT, fase TEXT);"
                    "INSERT INTO achado VALUES ('L1', 'site-fundo-casa', '2026-11-05', 'aceito');"
                    "INSERT INTO livro VALUES ('L1', 'aguardando', '2026-11-05', '', 'ouro');"
                    "INSERT INTO passaporte VALUES ('L1', 'farol');")
    r = calcular(b, None, tmp_path, agora=datetime(2026, 11, 9, 12, tzinfo=timezone.utc))
    assert r["fundacoes-nacionais"]["acertos"] == 1 and r["fundacoes-nacionais"]["m3d"]["livros"] == 1
