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
                    "('C','analise externa','2026-11-03T10:00:00'),('D','farol','2026-11-01');")
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
    assert ae.conferir_completo(r, _banco()) == []     # C entrou depois do lote; D já saiu das etapas pendentes (no Farol)
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


def test_a_versao_recebida_pelo_chrome_e_a_que_conta(tmp_path, monkeypatch):
    """04/11/2026: o lote do dia é regravado; a conferência usa a versão com a hora que o veredito declara."""
    monkeypatch.chdir(tmp_path)
    p = tmp_path / "verificacao/lotes"
    p.mkdir(parents=True)
    (p / "lote-x.json").write_text(json.dumps({"lote": "lote-x", "gerado_em": "2026-11-03T20:00:00+00:00",
                                               "livros": [{"livro_id": i} for i in "ABCD"]}))      # a versão de agora: 4
    ae.guardar_versao(p, "lote-x", {"lote": "lote-x", "gerado_em": "2026-11-03T15:22:07+00:00", "livros": [{"livro_id": "A"}]})
    r = ae.Retorno(lote="lote-x", lote_gerado_em="2026-11-03T15:22:07+00:00", vereditos=[ae.Veredito(livro_id="A", decisao="valido")])
    assert ae.conferir_completo(r, _banco()) == []                      # a versão das 15:22 tinha só o A


def test_a_decisao_encerrada_arquiva_e_nao_exclui():
    from pathlib import Path
    t = Path("eldorado/base/cartorio/analise_externa.py").read_text(encoding="utf-8")
    i = t.index('if v.decisao in ("encerrada", "arquivar"):')
    bloco = t[i:t.index("continue", i)]                      # só o bloco da decisão, até o «continue»
    assert '"arquivo"' in bloco and "livro.excluido_logicamente" not in bloco


def test_a_gravacao_nao_apaga_as_versoes_nem_os_lotes_das_partes():
    """04/11/2026: o gravar.sh tirava do repositório tudo de verificacao/lotes ausente na pasta do ciclo (as versões e os
    lotes das partes do Chrome sumiam a cada gravação); o ciclo passa a trazê-los para a conferência da R41."""
    from pathlib import Path
    s = Path("scripts/gravar.sh").read_text(encoding="utf-8")
    assert 'grep -v "/versoes/" | grep -v -- "-externa-"' in s
    t = Path("eldorado/base/cartorio/analise_externa.py").read_text(encoding="utf-8")
    assert 'for sub in ("lotes/versoes/", "lotes/"):' in t and '"arquivar"' in t


def test_o_lote_completo_leva_todas_as_etapas_pendentes():
    """04/11/2026 (titular): o lote único do Chrome com todos os livros sem decisão; depois do veredito, nenhuma pendência."""
    from pathlib import Path
    t = Path("eldorado/base/cartorio/analise_externa.py").read_text(encoding="utf-8")
    assert "def gravar_lote_completo" in t and "gerar_lote(con, hoje, None, PENDENTES)" in t
    assert 'destino = "farol" if aberta else "arquivo"' in t
    s = Path("eldorado/base/painel/sala.py").read_text(encoding="utf-8")
    assert '"externa": ["ve_para_o_chrome", "de_decisoes", "es_expurgo"' in s and '"es_parcial"],' in s


def test_o_importador_normaliza_o_formato_do_chrome():
    """05/11/2026: itens em dicionário, página em texto, número no endereço — normalizados, sem perder a informação."""
    import msgspec
    bruto = json.dumps({"lote": "x", "vereditos": [{"livro_id": "A", "decisao": "valido",
        "itens": {"Objeto": {"valor": "fomento", "trecho": "t", "pagina": "p. 3", "endereco": "https://e"},
                  "Valor": {"valor": 1000, "trecho": "u", "pagina": "DOU Seção 3", "url": 7}},
        "dispensas": {"Prazo de recurso": "não há recurso previsto no regulamento do prêmio"}}]})
    r = msgspec.json.decode(ae.normalizar_retorno(bruto), type=ae.Retorno)
    i = {x.item: x for x in r.vereditos[0].itens}
    assert i["Objeto"].pagina == 3 and i["Objeto"].url == "https://e"
    assert i["Valor"].valor == "1000" and i["Valor"].pagina == 7 and i["Valor"].url is None and "[DOU Seção 3]" in i["Valor"].trecho
    assert r.vereditos[0].dispensas[0].item == "Prazo de recurso"


def test_o_livro_segue_o_caminho_autorizado():
    """05/11/2026 (grupo 1): da recepção só se vai à certificação; da preparação ao Farol, pela validação."""
    passos = []

    class Pas:
        def __init__(self, f):
            self.f = f

        def fase(self, livro):
            return self.f

        def mover(self, livro, para, motivo, extra):
            passos.append(para)
            self.f = para
            return True, ""

    class Cart:
        passaporte = Pas("recepcao")
    assert ae.levar(Cart(), "L", "arquivo", "m", "g") and passos == ["certificacao", "arquivo"]
    passos.clear()
    Cart.passaporte = Pas("preparacao")
    assert ae.levar(Cart(), "L", "farol", "m", "g") and passos == ["validacao", "farol"]
