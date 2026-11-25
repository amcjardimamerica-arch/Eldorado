"""N-02 (manutenção de 25/11/2026; a titular autorizou a regravação única em 25/11/2026): a certidão apontava para o
documento pelo número do banco. Numa remontagem com outra ordem de documentos, 1.968 certidões de 24 e 25/11 se perdiam
(1.214 recusadas) ou passavam a apontar para outro documento (754). R35, R08, R46."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from conftest import AGORA, ev, livro

import eldorado.banco.biblioteca.esquema as bib
import eldorado.banco.cerebro_db.esquema as cer
from eldorado.base.cartorio import cartorio as C
from eldorado.base.cartorio.certificacao import Certificacao
from eldorado.base.nucleo import correcoes
from eldorado.base.nucleo.eventos import criar
from eldorado.base.nucleo.gravador import Gravador

TEXTO = "EDITAL DE CHAMAMENTO PÚBLICO Nº 3/2026. As inscrições estarão abertas de 01/10/2026 a 30/11/2026. Valor total R$ 500.000,00."


def _bancos(pasta: Path):
    pasta.mkdir(parents=True, exist_ok=True)
    livros = bib.abrir(pasta / "biblioteca.db")
    return {"biblioteca": livros, "especial": livros, "cerebro": cer.abrir(pasta / "cerebro.db")}


def _docs(ordem):
    return [criar("documento.registrado", "teste", {"url": f"https://exemplo.gov.br/{s}.pdf", "sha256": s, "obtido_em": AGORA, "oficial": 1})
            for s in ordem]


def _sha_da_certidao(b) -> list[str]:
    return [r[0] for r in b["biblioteca"].execute(
        "SELECT d.sha256 FROM certidao c JOIN documento d ON d.id = c.documento_id ORDER BY c.item")]


def test_certidao_gravada_leva_o_sha256_do_documento(bancos, diario, gravador):
    gravador.aplicar(_docs(["sha-a", "sha-b"]) + [ev("pagina.gravada", documento_sha256="sha-b", numero=1, texto=TEXTO), livro()])
    leitor = C.Cartorio.__new__(C.Cartorio)
    leitor.con = bancos["biblioteca"]
    paginas = leitor._paginas("sha-b")
    assert paginas and all(p.documento_id == "sha-b" for p in paginas)       # a página leva a assinatura, não o número 2
    Certificacao(diario).certificar("L1", paginas)
    gravadas = [e.dados for e in diario.eventos() if e.tipo == "certidao.gravada"]
    assert gravadas and all(d.get("documento_sha256") == "sha-b" and "documento_id" not in d for d in gravadas)


def test_remontar_dos_eventos_da_o_mesmo_documento_a_cada_certidao(tmp_path):
    """Duas remontagens com a ordem dos documentos diferente dão o mesmo documento por certidão (a nova, pela assinatura;
    a antiga, com o número, pela tradução gerada na produção)."""
    cert_nova = criar("certidao.gravada", "teste", {"livro_id": "L1", "item": "Objeto", "valor": "projetos culturais", "fase": "certificacao",
                                                    "situacao": "comprovado", "em": AGORA, "documento_sha256": "sha-c", "pagina": 1, "trecho": "t"})
    # a certidão antiga: o número 3 é o documento «sha-c» NA PRODUÇÃO (ordem a, b, c)
    cert_antiga = criar("certidao.gravada", "teste", {"livro_id": "L1", "item": "Valor", "valor": "R$ 500.000,00", "fase": "certificacao",
                                                      "situacao": "comprovado", "em": AGORA, "documento_id": 3, "pagina": 1, "trecho": "t"})
    producao = _bancos(tmp_path / "producao")
    Gravador(producao).aplicar(_docs(["sha-a", "sha-b", "sha-c"]) + [livro(), cert_nova, cert_antiga])
    # a pasta de eventos da produção, para o comando de tradução
    evs = tmp_path / "eventos" / "2026" / "11" / "24"
    evs.mkdir(parents=True)
    (evs / "x.jsonl").write_text(json.dumps({"id": cert_antiga.id, "tipo": cert_antiga.tipo, "modulo": "teste", "em": "2026-11-24T10:00:00+00:00",
                                             "dados": cert_antiga.dados}) + "\n", encoding="utf-8")
    tabela = tmp_path / "correcoes" / "certidoes_sha256.json"
    r = correcoes.gerar(tmp_path / "producao" / "biblioteca.db", tmp_path / "eventos", "2026-11-23", caminho=tabela,
                        agora=datetime(2026, 11, 24, 12, tzinfo=timezone.utc))
    assert r["novos"] == 1 and r["concluida_em"] is None
    shas = []
    for nome, ordem in (("r1", ["sha-c", "sha-a", "sha-b"]), ("r2", ["sha-b", "sha-c", "sha-a"])):
        b = _bancos(tmp_path / nome)
        correcoes.ARQUIVO, antes = tabela, correcoes.ARQUIVO
        try:
            rel = Gravador(b).aplicar(_docs(ordem) + [livro(), cert_nova, cert_antiga])
        finally:
            correcoes.ARQUIVO = antes
        assert not rel.recusados, rel.recusados
        shas.append(_sha_da_certidao(b))
    assert shas[0] == shas[1] == _sha_da_certidao(producao) == ["sha-c", "sha-c"]


def test_sem_a_traducao_a_certidao_antiga_continua_aceita_como_hoje(bancos, gravador):
    """Compatibilidade: o evento antigo com o número é aplicado pelo número quando não há tradução para ele."""
    gravador.aplicar(_docs(["sha-a"]) + [livro()])
    rel = gravador.aplicar([ev("certidao.gravada", livro_id="L1", item="Objeto", valor="x", fase="certificacao", situacao="comprovado", em=AGORA,
                               documento_id=1, pagina=1, trecho="t")])
    assert not rel.recusados and _sha_da_certidao(bancos) == ["sha-a"]


def test_a_traducao_conclui_sozinha_24h_depois_da_ultima_certidao_com_numero(tmp_path):
    b = _bancos(tmp_path / "p")
    Gravador(b).aplicar(_docs(["sha-a"]))
    evs = tmp_path / "eventos" / "2026" / "11" / "24"
    evs.mkdir(parents=True)
    (evs / "x.jsonl").write_text(json.dumps({"id": "e1", "tipo": "certidao.gravada", "em": "2026-11-24T10:00:00+00:00",
                                             "dados": {"documento_id": 1}}) + "\n", encoding="utf-8")
    tabela = tmp_path / "c.json"
    depois = datetime(2026, 11, 26, tzinfo=timezone.utc)
    r = correcoes.gerar(tmp_path / "p" / "biblioteca.db", tmp_path / "eventos", caminho=tabela, agora=depois)
    assert r["concluida_em"] and json.loads(tabela.read_text(encoding="utf-8"))["eventos"] == {"e1": "sha-a"}
    assert correcoes.gerar(tmp_path / "p" / "biblioteca.db", tmp_path / "eventos", caminho=tabela, agora=depois + timedelta(days=1))["novos"] == 0


def test_expurgo_e_descarte_pela_assinatura_nao_tocam_outro_documento(bancos, gravador):
    """O número do documento num banco é outro documento noutro banco: o expurgo e o descarte vão pela assinatura."""
    gravador.aplicar(_docs(["sha-a", "sha-b"]) + [ev("pagina.gravada", documento_sha256="sha-a", numero=1, texto="A"),
                                                  ev("pagina.gravada", documento_sha256="sha-b", numero=1, texto="B")])
    # o evento veio de outro banco, onde o número 2 era o «sha-a»
    gravador.aplicar([ev("leitura.expurgada", documento_id=2, documento_sha256="sha-a", motivo="R35"),
                      ev("documento.descartado", documento_id=2, documento_sha256="sha-zzz")])   # assinatura que não está aqui
    con = bancos["biblioteca"]
    assert [r[0] for r in con.execute("SELECT d.sha256 FROM pagina p JOIN documento d ON d.id = p.documento_id")] == ["sha-b"]
    assert {r[0] for r in con.execute("SELECT sha256 FROM documento")} == {"sha-a", "sha-b"}
