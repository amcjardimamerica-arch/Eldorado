"""O Espião e o Cérebro dos pilotos: busca só fora dos motores, aprende as famílias, respeita bloqueio e ociosidade."""
import random

import msgspec
from conftest import ev

from eldorado.base.cartorio.cartorio import Cartorio
from eldorado.base.cerebro.pilotos import dose, missoes
from eldorado.base.cerebro.regencia import achado_para_evento
from eldorado.base.missao.oportunidades import MissaoOportunidades
from eldorado.base.nucleo.eventos import ler
from eldorado.motores.descoberta.pistas import Pista
from eldorado.motores.pilotos.espiao import Espiao

PAGINAS = {"https://institutoexemplo.org.br/edital-2026": ("Edital Instituto Exemplo 2026", "Edital de seleção de projetos sociais: inscrições abertas para "
                                                           "organizações da sociedade civil sem fins lucrativos de Goiás."),
           "https://lojaqualquer.com.br/ofertas": ("Ofertas", "Compre agora com desconto."),
           "https://fundacaobeta.org/grants": ("Grants", "Call for proposals: grants for NGOs in Brazil, nonprofit organizations eligible.")}
PISTAS = [Pista(titulo="Edital Instituto Exemplo", link="https://institutoexemplo.org.br/edital-2026", origem="busca"),
          Pista(titulo="Secretaria", link="https://www.goias.gov.br/edital", origem="busca"),
          Pista(titulo="Facebook", link="https://facebook.com/x", origem="busca"),
          Pista(titulo="Loja", link="https://lojaqualquer.com.br/ofertas", origem="busca"),
          Pista(titulo="Já vigiado", link="https://gife.org.br/edital", origem="busca"),
          Pista(titulo="Já na Biblioteca", link="https://conhecido.org/edital", origem="busca"),
          Pista(titulo="Fundação Beta", link="https://fundacaobeta.org/grants", origem="busca")]


def espiao(tmp_path, consultar=None, seed=1):
    return Espiao(tmp_path / "motores" / "espiao.db", consultar or (lambda q: (PISTAS, ["searxng: desligado", "ddgs: 7 pista(s)"])),
                  lambda u: PAGINAS.get(u), vigiados={"gife.org.br"}, conhecidos={"https://conhecido.org/edital"}, rnd=random.Random(seed))


def test_missao_so_fora_dos_motores_e_com_sinal_de_osc(tmp_path):
    e = espiao(tmp_path)
    m = e.missao()
    assert {a.link_divulgacao for a in m["achados"]} == {"https://institutoexemplo.org.br/edital-2026", "https://fundacaobeta.org/grants"}
    assert m["motivos"] == {"domínio de governo (território dos motores)": 1, "buscador, agregador ou rede social": 1,
                            "sem sinal de oportunidade para OSC": 1, "já vigiado por um motor": 1, "já está na Biblioteca": 1}
    a, usos = e.con.execute("SELECT a, usos FROM familia WHERE nome = ?", (m["familia"],)).fetchone()
    assert a == 2.0 and usos == 1                                                                   # a família que rendeu é reforçada
    assert e.missao()["achados"] == []                                                             # o que já achou não volta


def test_thompson_e_consulta_aposentada(tmp_path):
    e = espiao(tmp_path)
    e.con.execute("UPDATE familia SET a = 1, b = 60")
    e.con.execute("UPDATE familia SET a = 60, b = 1 WHERE nome = 'internacional_ingles'")
    assert sum(e.escolher()[0] == "internacional_ingles" for _ in range(30)) >= 27
    for q in ("call for proposals Brazil civil society 2026", "grants for NGOs in Brazil 2026", "small grants Brazil community organizations 2026",
              "funding opportunity nonprofits Latin America 2026 Brazil eligible", "request for proposals Brazil social projects 2026"):
        e.con.execute("INSERT INTO consulta VALUES (?, 'internacional_ingles', 3, 0, NULL)", (q.replace("2026", str(__import__("datetime").date.today().year)),))
    assert e.escolher()[0] != "internacional_ingles"                                                # todas aposentadas: outra família


def test_bloqueio_e_ociosidade(tmp_path, bancos):
    falha = lambda q: ([], ["searxng: falhou (Erro); descansa 60 min", "ddgs: falhou (Limite); descansa 60 min", "marginalia: falhou (Erro); descansa 60 min"])  # noqa: E731
    e = espiao(tmp_path, falha)
    assert e.missao()["bloqueada"] and e.bloqueado()
    achados, rel = missoes(tmp_path, bancos["biblioteca"], None, ociosidade=True, consultar=falha, ler=lambda u: None)
    assert achados == [] and rel["decisao"].startswith("bloqueio")
    achados, rel = missoes(tmp_path / "outro", bancos["biblioteca"], None, ociosidade=False, consultar=falha, ler=lambda u: None)
    assert achados == [] and rel["decisao"].startswith("sem ociosidade")
    assert dose({"missoes": 0}) == 2 and dose({"missoes": 5, "com_resultado": 1}) == 4 and dose({"missoes": 25, "com_resultado": 0}) == 1


def test_achado_do_espiao_entra_pela_recepcao(tmp_path, gravador, bancos, diario):
    achados, rel = missoes(tmp_path, bancos["biblioteca"], None, ociosidade=True, consultar=lambda q: (PISTAS, ["ddgs: 7 pista(s)"]),
                           ler=lambda u: PAGINAS.get(u))
    assert rel["decisao"].startswith("ociosidade: 2 missão") and len(achados) == 2
    a = achados[0]
    assert gravador.aplicar([ev("achado.entregue", **achado_para_evento(a), decisao="aceito", motivo="oportunidade")]).ok
    livro = Cartorio(bancos["biblioteca"], MissaoOportunidades(), diario).processar([msgspec.to_builtins(a)])[0]["livro"]
    assert gravador.aplicar(list(ler(tmp_path / "eventos"))).ok
    assert [r[0] for r in bancos["biblioteca"].execute("SELECT para FROM passagem WHERE livro_id=? ORDER BY id", (livro,))][:2] == ["recepcao", "certificacao"]


def test_blog_divulga_mas_nao_e_a_fonte(tmp_path):
    e = espiao(tmp_path)
    assert e.fora_dos_motores("https://institutosocialcrescervida.blogspot.com/2026/08/editais.html") == (False, "buscador, agregador ou rede social")
