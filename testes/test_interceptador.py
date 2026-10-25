"""As 5 fases: o Cartório organiza; a rede encaminha; o Interceptador traz a informação; o Cartório valida (fase 4)."""
import msgspec
import pymupdf
import pytest
from conftest import AGORA, ev
from servidor_local import criar_servidor

from eldorado.base.cartorio.cartorio import Cartorio
from eldorado.base.cerebro.encaminhamento import Encaminhamento
from eldorado.base.missao.oportunidades import MissaoOportunidades
from eldorado.base.nucleo.eventos import ler
from eldorado.base.nucleo.registro import Registro
from eldorado.motores.acesso.api import DegrauAPI
from eldorado.motores.acesso.escada import Escada
from eldorado.motores.pilotos.interceptador import Interceptador, fila

EDITAL = ("EDITAL DE CHAMAMENTO PÚBLICO Nº 3/2026. O presente edital tem por objeto a seleção de projetos culturais de organizações da sociedade civil. "
          "As inscrições estarão abertas de 01/10/2026 a 30/11/2026. Serão destinados R$ 500.000,00 no Estado de Goiás.")


def pdf(texto):
    d = pymupdf.open()
    d.new_page().insert_textbox(pymupdf.Rect(40, 40, 555, 800), texto, fontsize=10)
    return d.tobytes()


PAGINA = ("<html><body><main><h1>Edital nº 3/2026</h1><p>" + "Secretaria de Cultura publica o edital de fomento. " * 5
          + '</p><a href="/arquivos/edital-3-2026.pdf">Edital nº 3/2026 (regulamento)</a></main></body></html>').encode()


@pytest.fixture(scope="module")
def orgao():
    srv, est = criar_servidor({"/editais/edital-3-2026": (200, PAGINA, "text/html; charset=utf-8"),
                               "/arquivos/edital-3-2026.pdf": (200, pdf(EDITAL), "application/pdf")})
    yield f"http://127.0.0.1:{est.porta}"
    srv.shutdown()


def livro_na_fase_3(i, link):
    return [ev("livro.criado", id=i, missao="oportunidades", chave=f"k{i}", titulo="Edital de Chamamento Público nº 3/2026 — fomento cultural", orgao="Secult",
               uf="GO", link_oficial=link, estrela="sem", selo_livro="sem", informacoes_validadas=0, situacao="em trabalho", criado_em=AGORA, atualizado_em=AGORA),
            ev("livro.decupado", livro_id=i, abrangencia="estadual_go", situacao_prazo="aberta", inscricao_fim="2026-11-30", validacao="aprovado", validado_em=AGORA),
            ev("livro.passagem", livro_id=i, de="certificacao", para="preparacao", em=AGORA, autorizado_por="regencia")]


def escada():
    return Escada([DegrauAPI()], intervalo_padrao=0, tentativas=1, tempo_limite=5)


def test_interceptador_entrega_informacao_ao_livro_sem_certificar(orgao, gravador, bancos, diario, tmp_path):
    assert gravador.aplicar(livro_na_fase_3("L", f"{orgao}/editais/edital-3-2026")).ok
    b = bancos["biblioteca"]
    lv = fila(b, "2026-10-22")[0]
    r = Interceptador(b, diario, escada()).investigar(lv)
    assert r["abordagem"] == 1 and r["achado"].dados["livro_id"] == "L" and any("30/11/2026" in p for p in r["achado"].documento["paginas"])
    assert not [e for e in ler(tmp_path / "eventos") if e.tipo == "certidao.gravada"]                       # quem certifica é o Cartório
    assert [e.dados["fase"] for e in ler(tmp_path / "eventos") if e.tipo == "tentativa.registrada"] == ["preparacao"]


def test_rede_interceptador_e_cartorio_fase_4(orgao, gravador, bancos, diario, tmp_path):
    assert gravador.aplicar(livro_na_fase_3("L", f"{orgao}/editais/edital-3-2026")).ok
    b = bancos["biblioteca"]
    rede = Encaminhamento(b, diario, Registro(), Interceptador(b, diario, escada()))
    quem, achados = rede.encaminhar(fila(b, "2026-10-22")[0])
    assert quem.startswith("interceptador · plano de voo") and achados                                         # um livro, o plano de voo
    assert all("paginas" not in a["documento"] for a in achados)                                               # o texto vai pelo banco
    assert gravador.aplicar(list(ler(tmp_path / "eventos"))).ok
    Cartorio(b, MissaoOportunidades(), diario).processar(achados)                                              # fase 4: validar
    assert gravador.aplicar(list(ler(tmp_path / "eventos"))).ok
    fases = [r[0] for r in b.execute("SELECT para FROM passagem WHERE livro_id='L' ORDER BY id")]
    assert fases[-2:] == ["validacao", "preparacao"]                                                         # faltam itens: volta à fase 3
    itens = {r[0] for r in b.execute("SELECT item FROM certidao WHERE livro_id='L' AND situacao='comprovado'")}
    assert {"Objeto", "Prazo de inscrição", "Território"} <= itens and b.execute("SELECT estrela FROM livro WHERE id='L'").fetchone()[0] != "sem"


def test_rede_esgotada_vai_a_analise_externa(gravador, bancos, diario, tmp_path):
    assert gravador.aplicar(livro_na_fase_3("S", None)).ok                                                    # sem link: nenhuma abordagem tem material
    b = bancos["biblioteca"]
    quem, achado = Encaminhamento(b, diario, Registro(), Interceptador(b, diario, escada())).encaminhar(fila(b, "2026-10-22")[0])
    assert quem == "analise externa" and achado is None
    assert gravador.aplicar(list(ler(tmp_path / "eventos"))).ok
    assert b.execute("SELECT fase FROM passaporte WHERE livro_id='S'").fetchone()[0] == "analise externa"


def test_livro_novo_percorre_fases_1_2_3(gravador, bancos, diario, tmp_path):
    from eldorado.base.cerebro.regencia import achado_para_evento
    from eldorado.base.nucleo.contratos import Achado
    a = Achado(id="n1", motor="m", encontrado_em="2026-10-22", link_divulgacao="https://x.go.gov.br/e", titulo="Chamada pública para organizações da sociedade civil",
               dados={"uf": "GO"})
    assert gravador.aplicar([ev("achado.entregue", **achado_para_evento(a), decisao="aceito", motivo="oportunidade")]).ok
    livro = Cartorio(bancos["biblioteca"], MissaoOportunidades(), diario).processar([msgspec.to_builtins(a)])[0]["livro"]
    assert gravador.aplicar(list(ler(tmp_path / "eventos"))).ok
    assert [r[0] for r in bancos["biblioteca"].execute("SELECT para FROM passagem WHERE livro_id=? ORDER BY id", (livro,))] == \
        ["recepcao", "certificacao", "preparacao"]


def test_abordagem_secretaria_do_municipio(bancos, diario):
    """Titular, 23/10/2026: o diário divulga; a oportunidade original costuma estar no site da secretaria do município."""
    from eldorado.motores.pilotos.interceptador import Livro

    class Escada:
        pedidos = []

        def buscar(self, url):
            self.pedidos.append(url)
            if url.startswith("https://www.buritidegoias.go.gov.br/wp-json/wp/v2/posts?search=6"):
                return type("R", (), {"conteudo": b'[{"link": "https://www.buritidegoias.go.gov.br/edital-de-credenciamento-006-2026/", "title": {}}]'})()
            raise __import__("eldorado.motores.acesso.escada", fromlist=["Indisponivel"]).Indisponivel("não existe")
    lv = Livro("L", "EDITAL DE CREDENCIAMENTO Nº 006/2026", "Fundo Municipal de Saúde", None, "https://diariomunicipal.com.br/agm/x.pdf#ato-9",
               "sem", None, {}, set(), "Buriti de Goiás", "GO")
    e = Escada()
    assert Interceptador(bancos["biblioteca"], diario, e)._a11(lv) == ["https://www.buritidegoias.go.gov.br/edital-de-credenciamento-006-2026/"]
    assert Interceptador(bancos["biblioteca"], diario, e)._a11(Livro("M", "Edital", None, None, None, "sem", None, {}, set())) == []   # sem município
