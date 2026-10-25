"""O ciclo de vida dos alarmes (titular, 25/10/2026): o que se resolveu é fechado; o que não se resolveu fica aceso."""
from eldorado.base.cerebro.revisao_alarmes import revisar
from eldorado.base.nucleo.eventos import criar


def test_os_alarmes_resolvidos_sao_fechados(bancos, gravador):
    ev = lambda m, msg, em: criar("alarme.aberto", "t", {"gravidade": "alta", "modulo": m, "mensagem": msg, "aberto_em": em})  # noqa: E731
    assert gravador.aplicar([
        ev("workflow:passagem", "o nó encaminhar falhou depois de 1 tentativa(s): AttributeError", "2026-10-24T01:00:00+00:00"),
        ev("workflow:passagem", "o nó farol falhou depois de 1 tentativa(s): ValueError", "2026-10-24T01:00:00+00:00"),
        ev("gravador", "evento recusado (livro.unido, x): biblioteca.uniao: IntegrityError: UNIQUE constraint failed", "2026-10-25T00:00:00+00:00"),
        ev("gravador", "evento recusado (livro.criado, y): CHECK constraint failed", "2026-10-25T00:00:00+00:00")]).ok
    c = bancos["cerebro"]
    c.execute("INSERT INTO execucao(id, workflow, versao, inicio, estado) VALUES ('e', 'passagem', 1, '2026-10-25T00:00:00+00:00', 'concluida')")
    c.execute("INSERT INTO execucao_passo VALUES ('e', 1, 'encaminhar', 'concluido', NULL, NULL, '2026-10-25T01:00:00+00:00')")
    c.commit()
    fechados = {msg for (i, msg) in [(i, c.execute("SELECT mensagem FROM alarme WHERE id = ?", (i,)).fetchone()[0]) for i, _ in revisar(c)]}
    assert any("encaminhar" in m for m in fechados) and any("UNIQUE" in m for m in fechados)          # resolvidos
    assert not any("farol" in m for m in fechados) and not any("CHECK" in m for m in fechados)       # não resolvidos: abertos
