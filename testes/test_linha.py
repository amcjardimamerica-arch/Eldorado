"""A linha de produção do Cartório: a fila, uma tentativa por livro, as abordagens na ordem do balcão e a Investigação."""
import pymupdf
import pytest
from conftest import AGORA, ev
from servidor_local import criar_servidor

from eldorado.base.cartorio.linha import Linha, fila
from eldorado.base.nucleo.eventos import ler
from eldorado.motores.acesso.api import DegrauAPI
from eldorado.motores.acesso.escada import Escada

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


def livro(i, link):
    return [ev("livro.criado", id=i, missao="oportunidades", chave=f"k{i}", titulo="Edital de Chamamento Público nº 3/2026 — fomento cultural", orgao="Secult",
               uf="GO", link_oficial=link, estrela="sem", selo_livro="sem", informacoes_validadas=0, situacao="em trabalho", criado_em=AGORA, atualizado_em=AGORA),
            ev("livro.decupado", livro_id=i, abrangencia="estadual_go", situacao_prazo="aberta", inscricao_fim="2026-11-30", validacao="aprovado", validado_em=AGORA),
            ev("livro.passagem", livro_id=i, de=None, para="certificacao", em=AGORA, autorizado_por="regencia")]


def test_linha_certifica_pula_sem_material_e_encaminha(orgao, gravador, bancos, diario, tmp_path):
    assert gravador.aplicar(livro("L", f"{orgao}/editais/edital-3-2026")).ok
    b = bancos["biblioteca"]
    assert [x.id for x in fila(b, "2026-10-22")] == ["L"]
    linha = Linha(b, diario, Escada([DegrauAPI()], intervalo_padrao=0, tentativas=1, tempo_limite=5))
    r = linha.tentar(fila(b, "2026-10-22")[0])
    assert r["abordagem"] == 1 and {"Objeto", "Prazo de inscrição", "Território"} <= set(r["itens_novos"])          # documento na mão
    assert gravador.aplicar(list(ler(tmp_path / "eventos"))).ok
    assert b.execute("SELECT estrela FROM livro WHERE id='L'").fetchone()[0] in ("bronze", "prata")
    assert b.execute("SELECT COUNT(*) FROM certidao c JOIN documento d ON d.id = c.documento_id WHERE c.livro_id='L'").fetchone()[0] >= 3  # ligadas ao documento
    lv = fila(b, "2026-10-22")[0]
    assert 1 in lv.tentadas and lv.balcao in ("bronze", "prata")
    passos = [linha.tentar(lv) for _ in range(12)]
    assert passos[-1].get("encaminhado")                                                                         # esgotou o que tinha material
    usados = [p["abordagem"] for p in passos if p["abordagem"]]
    assert len(usados) == len(set(usados)) and 6 not in usados                                                   # sem repetir; sem mapa do site: pulada
    assert gravador.aplicar(list(ler(tmp_path / "eventos"))).ok
    assert b.execute("SELECT fase FROM passaporte WHERE livro_id='L'").fetchone()[0] == "investigacao"
    assert b.execute("SELECT COUNT(*) FROM tentativa WHERE livro_id='L' AND ferramenta LIKE 'abordagem %'").fetchone()[0] == 1 + len(usados)


def test_orcamento_de_tempo_por_batimento(gravador, bancos, diario):
    assert gravador.aplicar(livro("A", None) + livro("B", None)).ok
    linha = Linha(bancos["biblioteca"], diario, Escada([DegrauAPI()], intervalo_padrao=0, tentativas=1, tempo_limite=2))
    assert linha.andar(0, "2026-10-22") == []                                                                    # sem tempo, ninguém
