"""R36 (titular, 02/11/2026): a leitura sem livro investigada sem êxito é liberada pelo sistema; o sinal vai ao Chrome."""
import sqlite3
from pathlib import Path

from eldorado.base.cartorio import manutencao_expurgo as m


def test_o_sinal_vai_ao_chrome_e_o_invalidado_sai():
    assert m.destino("https://captadores.org.br/editais/zurich-abre-edital-nacional", None, set(), set()) == "chrome"
    assert m.destino("https://x.org/pagina-qualquer-2026", None, set(), set()) == "chrome"
    assert m.destino("https://y.org/doc", "interceptador · documento na mão", set(), set()) == "chrome"
    assert m.destino("https://senadorcanedo.go.gov.br/sistema-de-escrita-fiscal", None, set(), set()) == "descartar"
    assert m.destino("https://www.fundobrasil.org.br/edital/edital-anual-2017", None, set(), set()) == "descartar"
    assert m.destino("https://gazeta.com.br/tag/edital", None, set(), set()) == "descartar"
    assert m.destino("https://mapa.cultura.gov.br/oportunidade/11685/#info", None, set(), {"L-1"}) == "vincular"
    assert m.destino("https://a.org/edital-x", None, set(), {"L-1", "L-2"}) == "chrome"   # ambíguo: não vincula


def test_a_manutencao_esta_na_passagem():
    t = Path("workflows/passagem.toml").read_text(encoding="utf-8")
    assert 'tipo = "eldorado.base.cartorio.manutencao_expurgo:no_manutencao_expurgo"' in t


class _Diario:
    def __init__(self):
        self.ev = []

    def emitir(self, tipo, modulo, dados):
        self.ev.append((tipo, dados))


def test_nenhum_livro_e_tocado(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    b = sqlite3.connect(":memory:")
    b.executescript("""
    CREATE TABLE livro(id TEXT, link_oficial TEXT, link_divulgacao TEXT, situacao TEXT);
    CREATE TABLE achado(id TEXT, motor TEXT, encontrado_em TEXT, decisao TEXT, motivo TEXT, link_oficial TEXT,
                        link_divulgacao TEXT, livro_id TEXT, documento_id INTEGER);
    CREATE TABLE certidao(documento_id INTEGER);
    CREATE TABLE documento(id INTEGER, url TEXT, leitor TEXT, sha256 TEXT, obtido_em TEXT);
    INSERT INTO livro VALUES ('L-1','https://o.gov.br/edital-um-dois.pdf',NULL,'em trabalho');
    INSERT INTO achado VALUES ('a1','dou','2026-01-01','barrado','extrato',NULL,'https://dou/x',NULL,NULL);
    INSERT INTO achado VALUES ('a2','dou','2026-01-01','barrado','x',NULL,'https://dou/y','L-1',NULL);
    INSERT INTO achado VALUES ('a3','dou','2026-01-01','aceito','x',NULL,'https://dou/z',NULL,NULL);
    INSERT INTO documento VALUES (1,'https://o.gov.br/edital-um-dois.pdf','pdf','s1','2026-01-01');
    INSERT INTO documento VALUES (2,'https://p.go.gov.br/sistema-fiscal-atualizado','html','s2','2026-01-01');
    INSERT INTO documento VALUES (3,'https://q.org/chamada-publica-cultura','html','s3','2026-01-01');
    """)
    d = _Diario()
    r = m.executar(b, None, d, tmp_path / "expurgo")
    saiu_achado = [x["id"] for t, x in d.ev if t == "achado.descartado"]
    saiu_doc = [x["documento_id"] for t, x in d.ev if t == "documento.descartado"]
    assert saiu_achado == ["a1"] and saiu_doc == [2] and r["documentos_ao_chrome"] == 1
    assert not any(t.startswith("livro.") for t, _ in d.ev)
