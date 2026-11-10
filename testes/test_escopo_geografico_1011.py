"""10/11/2026 (titular): barrar o que não é de Goiás, nacional, capitais, estadual de outro estado ou internacional — o
município do interior de outro estado sai, também quando o título é o endereço (mapas de site); a revisão a cada passagem."""
import sqlite3

from eldorado.base.cartorio.auditoria import fora_do_escopo
from eldorado.base.missao.regras_portao import municipal_fora_de_goias as fora


def test_a_regra_nos_titulos_de_endereco():
    sai = ["ribeirao pires pnab 006 2026 fomento a projetos culturais 52541fd2", "tupaciguara mg edital 01 2026 fomento para osc cultural",
           "jequie ba premiacao mestres e mestras das culturas populares 2026"]
    fica = ["rio de janeiro edital no 5 desenvolvimento de jogos", "minas gerais chamamento publico organizacao de eventos",
            "rio grande do sul edital de cultura 2026", "anapolis edital pnab 2026", "sao paulo e campinas edital conjunto", "pnab ciclo 2",
            "Edital PNAB 2026 — Prefeitura de Goiânia"]
    assert all(fora({"titulo": t}) for t in sai)
    assert not any(fora({"titulo": t}) for t in fica)
    assert fora({"titulo": "edital 2026", "url": "https://farolcultural.com.br/editais/novo-hamburgo-rs-edital-03-2026"})
    assert not fora({"titulo": "tupaciguara mg edital 01 2026", "abrangencia": "estadual"})          # a abrangência estadual fica


def test_a_revisao_do_escopo_a_cada_passagem():
    c = sqlite3.connect(":memory:")
    c.executescript("CREATE TABLE livro(id TEXT, titulo TEXT, orgao TEXT, uf TEXT, link_oficial TEXT, link_divulgacao TEXT, situacao TEXT);"
                    "CREATE TABLE passaporte(livro_id TEXT, fase TEXT); CREATE TABLE livro_dados(livro_id TEXT, abrangencia TEXT);")
    for lid, t, fase in (("A", "tupaciguara mg edital 01 2026", "analise externa"), ("B", "anapolis edital pnab 2026", "analise externa"),
                         ("C", "jequie ba premiacao 2026", "farol"), ("captacao-9", "ribeirao pires pnab 2026", "arquivo")):
        c.execute("INSERT INTO livro VALUES (?, ?, '', 'BR', '', '', 'em trabalho')", (lid, t))
        c.execute("INSERT INTO passaporte VALUES (?, ?)", (lid, fase))
    assert set(fora_do_escopo(c)) == {"A"}      # B é de Goiás; C está no Farol (a titular decide); o catálogo nunca sai (R44)


def test_a_uf_do_replicador_nao_vale_contra_o_municipio_nomeado():
    """10/11/2026: o replicador marca «GO»; o texto nomeia um município de outro estado — vale o município."""
    assert fora({"titulo": "municipio de sao caetano edital de chamamento publico no 003 2026", "uf": "GO"})
    assert not fora({"titulo": "municipio de senador canedo edital de chamamento 12 2026", "uf": "GO"})
    assert not fora({"titulo": "municipio de goias edital de chamamento publico 2026", "uf": "GO"})


def test_o_site_de_divulgacao_exige_prazo_vigente():
    import tomllib
    from pathlib import Path

    from eldorado.motores.canal.motor import _prazo_vigente_no_texto as prazo
    assert prazo("Inscrições até 30/11/2099") is None and prazo("o termo vigora até 14/02/2028") is None
    for p in Path("eldorado/motores/canal/config").glob("*.toml"):
        d = tomllib.loads(p.read_text(encoding="utf-8"))
        if d["motor"].get("grupo", "").startswith("Sites de divulgação"):
            assert d["lexico"].get("exige_prazo") and d["lexico"].get("territorio") == "goias" and d["leitura"].get("paginas_dos_achados"), p.stem
