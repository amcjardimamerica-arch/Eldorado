"""16/11/2026 (titular): a importação dos livros de ouro validados no edital pelos 20 agentes do Claude no Chrome."""
import json
import sqlite3

from eldorado.base.cartorio.importar_ouro import _proximo_serial, converter, importar_arquivo, prefixo


def test_o_formato_dos_agentes_e_normalizado():
    v = {"livro_id": "L1", "decisao": "mecanismo", "parecer": "Lei Rouanet", "dispensas": [{"item": "Prazo de recurso", "justificativa": "fluxo contínuo"}, {}],
         "itens": [{"item": "Objeto", "valor": 12, "trecho": "apoio a projetos", "pagina": "3"}, {"item": "Valor", "trecho": ""}],
         "edicoes_anteriores": ["2025-03-10", {"edicao": "Edital 01/2025", "abertura": ""}, {"abertura": "2024-03-18"}]}
    c = converter(v)
    assert c["decisao"] == "valido" and c["motivo"].startswith("mecanismo permanente")
    assert c["itens"] == [{"item": "Objeto", "valor": "12", "trecho": "apoio a projetos", "pagina": 3, "url": None}]
    assert c["edicoes_anteriores"] == ["2025-03-10", "2024-03-18"] and len(c["dispensas"]) == 1
    assert converter({"livro_id": "L2", "decisao": "unir"}) is None


def test_o_codigo_de_ouro_e_conferido():
    assert prefixo({"abrangencia": "GYN.GO", "objeto": "C01", "acao": "AP"}) == "GYN.GO-C01-AP"
    assert prefixo({"abrangencia": "BR", "objeto": "D99", "acao": ""}) == "BR-D99"
    assert prefixo({"abrangencia": "Goiânia", "objeto": "C01"}) is None and prefixo({"abrangencia": "GO", "objeto": "Teatro"}) is None


def test_o_numero_de_serie_e_compartilhado_entre_as_partes():
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE livro_dados(codigo_ouro TEXT)")
    con.execute("INSERT INTO livro_dados VALUES ('GYN.GO-C01-AP-0004')")
    usados = {}
    assert [_proximo_serial(con, "GYN.GO-C01-AP", usados) for _ in range(2)] == [5, 6]
    assert _proximo_serial(con, "GYN.GO-C01-AP", usados) == 7           # a parte seguinte, na mesma passagem
    assert _proximo_serial(con, "BR-D01", usados) == 1


def test_a_parte_incompleta_e_recusada(tmp_path):
    arq = tmp_path / "ouro-x.json"
    arq.write_text(json.dumps({"lote": "x", "total_lote": 3, "vereditos": [{"livro_id": "A", "decisao": "valido"}], "retorno": [{"livro_id": "B"}]}))
    r = importar_arquivo(arq, sqlite3.connect(":memory:"), None)
    assert "recusado" in r and "o lote tem 3" in r["recusado"]


def test_importar_duas_vezes_gera_zero_evento_novo(tmp_path):
    """C-13 (16/11/2026): a parte já importada (com o relatório em importados/) não é importada de novo, mesmo que volte."""
    from eldorado.base.cartorio.importar_ouro import importar_pasta

    class D:
        def __init__(self):
            self.ev = []

        def emitir(self, t, m, d, **k):
            self.ev.append(t)
    (tmp_path / "importados").mkdir()
    (tmp_path / "ouro-x.json").write_text(json.dumps({"lote": "x", "total_lote": 1, "vereditos": [{"livro_id": "A", "decisao": "valido"}]}))
    (tmp_path / "importados" / "ouro-x-relatorio.json").write_text("{}")
    d = D()
    assert importar_pasta(sqlite3.connect(":memory:"), d, tmp_path) == [] and d.ev == []
