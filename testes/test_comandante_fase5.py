"""A fase 5 (titular, 25/10/2026): as skills do Hermes no Eldorado, contadas pela evidência, com o curador (ativa, parada,
arquivada; nunca apaga), o grafo, e a conferência de 20 minutos que restaura a mudança sobrescrita."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from eldorado.base.aprendizado.curador import curar
from eldorado.base.comandante import parametros as P
from eldorado.base.nucleo.eventos import Diario, ler


def _ap(gravador, pasta):
    rel = gravador.aplicar(list(ler(pasta)))
    assert rel.ok, rel.recusados
    for f in pasta.rglob("*.jsonl"):
        f.unlink()


def test_o_curador_conta_pela_evidencia_e_nunca_apaga(bancos, gravador, tmp_path):
    c, ev, agora = bancos["cerebro"], tmp_path / "ev", datetime.now(timezone.utc)
    curar(tmp_path, Diario(ev, "a"), Path("skills"), agora=agora)
    _ap(gravador, ev)
    n = c.execute("SELECT COUNT(*) FROM skill").fetchone()[0]
    assert n == len(list(Path("skills").glob("*/SKILL.md"))) >= 11 and c.execute("SELECT COUNT(*) FROM grafo_aresta").fetchone()[0] >= 2 * n
    c.execute("INSERT INTO espiao_missao(em, familia, consulta, resultados, candidatos, achados) VALUES (?, 'x', 'q', 3, 1, 1)", (agora.isoformat(),))
    c.commit()
    curar(tmp_path, Diario(ev, "a"), Path("skills"), agora=agora)
    _ap(gravador, ev)
    assert tuple(c.execute("SELECT usos, sucessos FROM skill WHERE nome = 'espiao-missao'").fetchone()) == (1, 1)  # pela evidência
    curar(tmp_path, Diario(ev, "a"), Path("skills"), agora=agora + timedelta(days=20))  # 20 dias sem uso
    _ap(gravador, ev)
    assert c.execute("SELECT estado FROM skill WHERE nome = 'espiao-missao'").fetchone()[0] == "parada"
    curar(tmp_path, Diario(ev, "a"), Path("skills"), agora=agora + timedelta(days=50))  # 30 dias parada
    _ap(gravador, ev)
    assert c.execute("SELECT estado FROM skill WHERE nome = 'espiao-missao'").fetchone()[0] == "arquivada"
    assert c.execute("SELECT COUNT(*) FROM skill").fetchone()[0] == n  # nada se apaga
    c.execute(
        "INSERT INTO espiao_missao(em, familia, consulta, resultados, candidatos, achados) VALUES (?, 'x', 'q2', 1, 0, 0)",
        ((agora + timedelta(days=50)).isoformat(),),
    )
    c.commit()
    curar(tmp_path, Diario(ev, "a"), Path("skills"), agora=agora + timedelta(days=50))  # usada de novo: ativa
    _ap(gravador, ev)
    assert c.execute("SELECT estado FROM skill WHERE nome = 'espiao-missao'").fetchone()[0] == "ativa"


def test_a_conferencia_de_20_minutos_restaura_o_sobrescrito(bancos, gravador, tmp_path):
    c, ev, agora = bancos["cerebro"], tmp_path / "ev", datetime.now(timezone.utc)
    P.definir(c, Diario(ev, "c"), "pilotos", "intervalo_s", "3", "regra da titular", agora - timedelta(minutes=25))
    _ap(gravador, ev)
    c.execute("INSERT INTO parametro VALUES ('pilotos', 'intervalo_s', 2, '60', NULL, 'escrita de fora', ?)", (agora.isoformat(),))
    c.commit()
    assert P.conferir(c, Diario(ev, "c")) == {"intactas": 0, "restauradas": 1}
    _ap(gravador, ev)
    assert P.valor(c, "pilotos", "intervalo_s") == "3"  # restaurado
    assert c.execute("SELECT COUNT(*) FROM alarme WHERE modulo = 'comandante:conferencia'").fetchone()[0] == 1
    assert c.execute("SELECT estado FROM conferencia").fetchone()[0] == "restaurada"
    P.definir(c, Diario(ev, "c"), "pilotos", "carga_maxima", "85", "regra da titular", agora - timedelta(minutes=21))
    _ap(gravador, ev)
    assert P.conferir(c, Diario(ev, "c"))["intactas"] == 1  # a intocada: intacta
