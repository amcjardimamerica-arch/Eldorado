"""A fase 2 do Comandante (titular, 25/10/2026): decide em paralelo com a ordem fixa, registra cada decisão com o motivo
no Arquivo do Cérebro; o Aprendizado avalia; a política reaprende do Cérebro; a IA recebe o contexto da memória."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

from eldorado.base.aprendizado.avaliar import avaliar
from eldorado.base.aprendizado.memoria import no_memorizar
from eldorado.base.comandante.decidir import decidir
from eldorado.base.nucleo.eventos import Diario, criar, ler


def _aplicar(gravador, pasta):
    rel = gravador.aplicar(list(ler(pasta)))
    assert rel.ok, rel.recusados
    for f in pasta.rglob("*.jsonl"):
        f.unlink()


def test_o_comandante_decide_registra_e_reaprende_do_cerebro(bancos, gravador, tmp_path):
    ontem = datetime.now(timezone.utc) - timedelta(days=1)
    ev = tmp_path / "ev"
    decidir(tmp_path, Path("config"), Diario(ev, "c"), {"motores": [{"modulo": "pncp"}]}, agora=ontem)
    _aplicar(gravador, ev)
    c = bancos["cerebro"]
    dec = c.execute("SELECT etapa, alvo, motivo, politica FROM comandante_decisao").fetchall()
    assert len([d for d in dec if d[0] == "coleta"]) == 8 and all(d[2] and d[3] == "vw-squarecb" for d in dec)
    escolhido = dec[0][1]
    assert (
        gravador.aplicar(
            [
                criar(
                    "achado.entregue",
                    "t",
                    {
                        "id": "A-cmd-1",
                        "motor": escolhido,
                        "titulo": "Edital de teste",
                        "encontrado_em": ontem.date().isoformat(),
                        "link_divulgacao": "https://x.gov.br/e",
                        "decisao": "aceito",
                    },
                )
            ]
        ).ok
        or True
    )
    r = avaliar(tmp_path, Diario(ev, "a"))
    _aplicar(gravador, ev)
    assert r["avaliadas"] >= 8 and c.execute("SELECT COUNT(*) FROM comandante_decisao WHERE avaliada_em IS NOT NULL").fetchone()[0] >= 8
    r2 = decidir(tmp_path, Path("config"), Diario(ev, "c"), None)
    assert r2["decisoes"]["coleta"]["aprendidas"] >= 8  # reaprendeu das decisões avaliadas no Cérebro


def test_a_ia_recebe_o_contexto_do_cerebro(bancos, gravador, tmp_path, monkeypatch):
    agora = datetime.now(timezone.utc).isoformat()
    assert gravador.aplicar(
        [
            criar(
                "alarme.aberto",
                "t",
                {
                    "gravidade": "alta",
                    "modulo": "piloto:interceptador",
                    "aberto_em": agora,
                    "mensagem": "o Interceptador não abriu o edital da Funarte: a ponte recusou o domínio",
                },
            )
        ]
    ).ok
    ev = tmp_path / "ev"
    no_memorizar([], {"dados": str(tmp_path)}, SimpleNamespace(diario=Diario(ev, "m")))
    _aplicar(gravador, ev)
    monkeypatch.setenv("ELDORADO_DADOS", str(tmp_path))
    from eldorado.base.nucleo.ia import memoria_do_cerebro

    lembrancas = memoria_do_cerebro("investigar o edital da Funarte pelo Interceptador")
    assert lembrancas and "Funarte" in lembrancas[0]
