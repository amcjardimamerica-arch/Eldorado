"""R37 e R38 (titular, 02/11/2026): o Comandante comanda o Cartório e ordena o trabalho das escadas."""
import sqlite3
from pathlib import Path

from eldorado.base.comandante import cartorio as C
from eldorado.base.missao import itens as I


def test_o_comandante_esta_na_passagem():
    t = Path("workflows/passagem.toml").read_text(encoding="utf-8")
    assert 'tipo = "eldorado.base.comandante.cartorio:no_comandar_cartorio"' in t and "esteira" not in t.split("comandante_cartorio")[0][-200:]


def test_o_comandante_decide_o_destino(monkeypatch):
    b = sqlite3.connect(":memory:")
    b.executescript("""
    CREATE TABLE livro(id TEXT, situacao TEXT, link_oficial TEXT); CREATE TABLE livro_dados(livro_id TEXT, inscricao_fim TEXT, validacao TEXT);
    CREATE TABLE passaporte(livro_id TEXT, fase TEXT); CREATE TABLE uniao(livro_que_fica TEXT, livro_unido TEXT);
    CREATE TABLE certidao(livro_id TEXT, item TEXT, situacao TEXT);
    INSERT INTO livro VALUES ('L-completo','em trabalho','https://o'),('L-falta','em trabalho','https://o'),('L-velho','em trabalho','https://o'),
                             ('L-semlink','em trabalho',NULL),('L-nada','em trabalho',NULL),('L-parado','em trabalho','https://o');
    INSERT INTO livro_dados VALUES ('L-completo','2099-01-01','aprovado'),('L-falta','2099-01-01','aprovado'),('L-velho','2000-01-01','aprovado'),
                                   ('L-semlink','2099-01-01','aprovado'),('L-nada',NULL,'aprovado'),('L-parado','2099-01-01','aprovado');
    INSERT INTO passaporte SELECT id,'preparacao' FROM livro;
    """)
    b.executemany("INSERT INTO certidao VALUES ('L-completo',?, 'comprovado')", [(k,) for k in I.DOZE])

    class F:
        id = "L-falta"
    monkeypatch.setattr("eldorado.motores.pilotos.interceptador.fila", lambda con, hoje: [F()])
    assert C.candidatos(b, "2026-11-02") == {"encerrados": ["L-velho"], "completos": ["L-completo"], "sem_o_que_buscar": ["L-parado"],
                                             "ao_chrome_sem_link": ["L-semlink"], "aguardam_motores": ["L-nada"]}


def test_a_ordem_de_territorio():
    ordem = sorted([("nacional", "BR"), ("capital_outro_estado", "SP"), ("internacional", None), ("estadual_go", "GO")],
                   key=lambda x: C.chave_de_busca(x[0], x[1], "2026-12-01", "2026-11-02"))
    assert [x[0] for x in ordem] == ["estadual_go", "nacional", "internacional", "capital_outro_estado"]
    assert C.peso_espiao("associacoes_goias_eventos") > C.peso_espiao("setor_apoio_regiao") > C.peso_espiao("internacional_financiador")


def test_a_escada_nao_busca_sem_link_nem_completo():
    assert C.pode_buscar(None, False)[0] is False and C.pode_buscar("https://o", True)[0] is False and C.pode_buscar("https://o", False)[0] is True
    t = Path("eldorado/motores/pilotos/interceptador.py").read_text(encoding="utf-8")
    assert "if lv.faltam and lv.link_oficial:" in t and "chave_de_busca" in t


def test_a_lei_e_o_chamamento():
    assert C.documento_oficial("incentivo_fiscal") == "a lei e o chamamento"
    from eldorado.motores.pilotos.interceptador import CHAVE, regime_de
    assert regime_de("Projeto pela Lei Goyazes", None) == "incentivo_fiscal" and CHAVE.search("Lei nº 8.313") and CHAVE.search("Portaria 01")
    assert "a lei e o chamamento são o documento oficial" in Path("eldorado/base/cartorio/analise_externa.py").read_text(encoding="utf-8")


def test_o_interceptador_grava_o_degrau_da_escada():
    t = Path("eldorado/motores/pilotos/interceptador.py").read_text(encoding="utf-8")
    assert '"escada": {"motor": "interceptador", "fonte": ABORDAGENS[n],' in t


def test_a_rede_aprende_com_livros_e_julga_os_pendentes():
    """02/11/2026 (titular): a pergunta «oportunidade» só com livros (cada um uma vez; sem o «pendente»; sem os achados
    barrados no portão, que davam 0,48 sobre livros), e a avaliação dos pendentes religada."""
    r = Path("eldorado/base/cerebro/rede.py").read_text(encoding="utf-8")
    assert "def caracteristicas_livro" in r and "decisao <> 'pendente'" in r and "WHERE decisao = 'barrado'\")" not in r
    assert "avaliar_pendentes = true" in Path("workflows/passagem.toml").read_text(encoding="utf-8")
