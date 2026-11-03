"""R41 (titular, 03/11/2026): nada parcial — o veredito do Chrome cobre TODOS os livros do lote, ou é recusado por inteiro
(nada importado) e vira alarme na Sala; o lote traz a instrução no topo do que o Chrome lê."""
import json

from eldorado.base.cartorio import analise_externa as ae
from eldorado.base.cartorio.manutencao_expurgo import INSTRUCOES as INSTR_DOC


class _Diario:
    def __init__(self):
        self.ev = []

    def emitir(self, tipo, modulo, dados):
        self.ev.append((tipo, dados))


def _banco():
    import sqlite3
    b = sqlite3.connect(":memory:")
    b.executescript("CREATE TABLE passaporte(livro_id TEXT, fase TEXT, entrou_em TEXT);"
                    "INSERT INTO passaporte VALUES ('A','analise externa','2026-11-01'),('B','analise externa','2026-11-01'),"
                    "('C','analise externa','2026-11-03T10:00:00'),('D','preparacao','2026-11-01');")
    return b


def test_o_veredito_parcial_e_recusado_por_inteiro(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "verificacao/lotes").mkdir(parents=True)
    (tmp_path / "verificacao/lotes/lote-x.json").write_text(json.dumps(
        {"lote": "lote-x", "gerado_em": "2026-11-02T00:00:00", "livros": [{"livro_id": i} for i in "ABCD"]}))
    d = _Diario()
    r = ae.importar(json.dumps({"lote": "lote-x", "vereditos": [{"livro_id": "A", "decisao": "valido"}]}), _banco(), d)
    assert "R41" in r[0]["recusado"] and "B" in r[0]["recusado"] and len(r) == 1
    assert [t for t, _ in d.ev] == ["alarme.aberto"]                       # só o alarme: nenhum veredito entrou


def test_o_completo_considera_so_os_devidos(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "verificacao/lotes").mkdir(parents=True)
    (tmp_path / "verificacao/lotes/lote-x.json").write_text(json.dumps(
        {"lote": "lote-x", "gerado_em": "2026-11-02T00:00:00", "livros": [{"livro_id": i} for i in "ABCD"]}))
    r = ae.Retorno(lote="lote-x", vereditos=[ae.Veredito(livro_id="A", decisao="valido"), ae.Veredito(livro_id="B", decisao="descartar")])
    assert ae.conferir_completo(r, _banco()) == []     # C entrou depois do lote; D já saiu da análise externa
    r2 = ae.Retorno(lote="lote-x", vereditos=[ae.Veredito(livro_id="A", decisao="valido"), ae.Veredito(livro_id="B", decisao="pendente")])
    assert ae.conferir_completo(r2, _banco()) == ["B"]
    assert isinstance(ae.conferir_completo(ae.Retorno(vereditos=[]), _banco()), str)   # sem o lote: recusado


def test_a_instrucao_vai_no_topo_do_lote():
    assert ae.ENTREGA_COMPLETA.startswith("ENTREGA COMPLETA E TOTAL (R41)") and "não entregue nada" in ae.ENTREGA_COMPLETA
    assert INSTR_DOC.startswith("ENTREGA COMPLETA E TOTAL (R41)")


def test_o_expurgo_vai_junto_da_verificacao_externa():
    """R42 (titular, 03/11/2026): o lote leva os lotes de documentos do expurgo e a instrução do livro sem dados."""
    from pathlib import Path
    assert "EXPURGO JUNTO (R42)" in ae.INSTRUCOES and "SEM DADOS" in ae.INSTRUCOES
    t = Path("eldorado/base/cartorio/analise_externa.py").read_text(encoding="utf-8")
    assert '"expurgo_junto": junto' in t and "timedelta(days=7)" in t
    c = Path("eldorado/base/comandante/cartorio.py").read_text(encoding="utf-8")
    assert 'for lid in c["sem_dados"]:' in c and "validar o expurgo (R42)" in c
