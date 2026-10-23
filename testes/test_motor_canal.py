"""Critério de pronto da Fase 5.3: um motor escrito só como arquivo de configuração roda da agenda ao livro certificado."""
import json
from pathlib import Path

import pymupdf
import pytest
from servidor_local import criar_servidor
from test_cartorio import EDITAL

from eldorado.base.fluxo.definicao import carregar
from eldorado.base.fluxo.executor import Executor
from eldorado.base.fluxo.nos import abrir_bancos
from eldorado.motores.canal.estado import EstadoMotor
from eldorado.motores.canal.motor import Configuracao


def pdf(texto):
    d = pymupdf.open()
    pg = d.new_page()
    pg.insert_textbox(pymupdf.Rect(40, 40, 555, 800), texto, fontsize=9)
    return d.tobytes()


LISTA = """<html><body><h1>Editais da Secretaria de Cultura</h1>
<a href="/docs/edital-3-2026.pdf">Edital de Chamamento Público nº 3/2026 — Fomento a projetos culturais de organizações da sociedade civil</a>
<a href="/docs/alimentos.pdf">CREDENCIAMENTO PÚBLICO, com o objetivo de realizar a Aquisição de Gêneros Alimentícios</a>
<a href="/sobre.html">Sobre a secretaria</a></body></html>""".encode()


@pytest.fixture(scope="module")
def fonte():
    srv, estado = criar_servidor({"/fonte/editais.html": (200, LISTA, "text/html; charset=utf-8"),
                                  "/docs/edital-3-2026.pdf": (200, pdf(EDITAL), "application/pdf"),
                                  "/docs/alimentos.pdf": (200, pdf("Credenciamento para aquisição de gêneros alimentícios. Valor R$ 10.000,00."), "application/pdf")})
    yield f"http://127.0.0.1:{estado.porta}", estado
    srv.shutdown()


def montar(tmp_path, base, horario="06:10"):
    (tmp_path / "motor.toml").write_text(f'''
[motor]
id = "secult-go-teste"
nome = "Secretaria de Cultura de Goiás (teste)"
categoria = "Executivo"
finalidade = "editais de fomento cultural para organizações da sociedade civil"
canal = "paginas"
uf = "GO"
orgao = "Secult"

[[fonte]]
nome = "Editais da Secult"
url = "{base}/fonte/editais.html"
tipo = "pagina"

[acesso]
degraus = ["api", "leve"]
intervalo_s = 0

[leitura]
tabelas = "uteis"

[lexico]
termos = ["edital", "chamamento", "credenciamento"]
vetos = ["resultado final"]
''')
    dados = tmp_path / "dados"
    (tmp_path / "modulos.toml").write_text(f'[[modulo]]\nclasse = "eldorado.motores.canal.motor:MotorCanal"\n'
                                           f'parametros = {{ configuracao = {json.dumps(str(tmp_path / "motor.toml"))}, dados = {json.dumps(str(dados / "motores"))} }}\n')
    (tmp_path / "agenda.toml").write_text('[[modulo]]\nid = "secult-go-teste"\nhorarios = ["06:00", "12:00"]\n')
    wf = Path("workflows/passagem.toml").read_text(encoding="utf-8")
    wf = (wf.replace('"config/agenda.toml"', json.dumps(str(tmp_path / "agenda.toml"))).replace('"config/modulos.toml"', json.dumps(str(tmp_path / "modulos.toml")))
            .replace('dados = "dados"', f"dados = {json.dumps(str(dados))}").replace('eventos = "eventos"', f"eventos = {json.dumps(str(tmp_path / 'eventos'))}"))
    wf = wf.replace('parametros = { agenda', f'parametros = {{ agora = "2026-10-22T{horario}:00-03:00", carga_fixa = 0.1, agenda', 1)
    wf = wf.replace('tipo = "eldorado.base.cerebro.regencia:no_acionar"\nparametros = { ', 'tipo = "eldorado.base.cerebro.regencia:no_acionar"\nparametros = { carga_fixa = 0.1, ', 1)
    wf = wf.replace("orcamento_s = 300", "orcamento_s = 0")             # este teste mede o motor; a linha do Cartório tem teste próprio
    (tmp_path / f"passagem-{horario[:2]}.toml").write_text(wf)
    return carregar(tmp_path / f"passagem-{horario[:2]}.toml"), dados


def test_motor_so_de_configuracao_da_agenda_ao_livro_certificado(fonte, tmp_path, monkeypatch):
    base, estado_srv = fonte
    wf, dados = montar(tmp_path, base)
    r = Executor(wf, tmp_path / "eventos").executar()
    assert r.estado == "concluida", r.erro
    assert len(r.saidas["acionar"]) == 2                                                   # o edital e o credenciamento (o "Sobre" o léxico ignorou)
    assert len(r.saidas["decidir"]) == 1 and len(r.saidas["cartorio"]) == 1               # o portão barrou a compra de alimentos
    livro = r.saidas["cartorio"][0]
    assert livro["estrela"] in ("bronze", "prata", "ouro")
    b = abrir_bancos(dados)
    try:
        bib = b["biblioteca"]
        assert bib.execute("SELECT COUNT(*) FROM documento").fetchone()[0] == 2 and bib.execute("SELECT COUNT(*) FROM pagina").fetchone()[0] == 2
        assert bib.execute("SELECT COUNT(*) FROM certidao WHERE livro_id=? AND pagina=1", (livro["livro"],)).fetchone()[0] >= 6
        assert bib.execute("SELECT link_oficial FROM livro WHERE id=?", (livro["livro"],)).fetchone()[0].endswith("/docs/edital-3-2026.pdf")
        assert b["cerebro"].execute("SELECT achados, erro FROM execucao_motor WHERE motor='secult-go-teste'").fetchone()[:] == (2, None)
    finally:
        for c in b.values():
            c.close()
    painel = EstadoMotor(dados / "motores/secult-go-teste.db").painel()
    fonte_ = painel["fontes"][0]
    assert (fonte_["achados"], fonte_["aceitos"], fonte_["barrados"]) == (2, 1, 1)               # o motor aprendeu com o retorno
    acessos_pdf = estado_srv.acessos[("/docs/edital-3-2026.pdf", "outro")] + estado_srv.acessos[("/docs/edital-3-2026.pdf", "navegador")]

    wf2, _ = montar(tmp_path, base, horario="12:10")                                       # segunda passagem, página sem mudança
    monkeypatch.setenv("ELDORADO_FORCAR", "1")          # sem grade fixa: o Cérebro não relê sem necessidade; acionada à mão
    r2 = Executor(wf2, tmp_path / "eventos").executar()
    assert r2.estado == "concluida" and r2.saidas["acionar"] == []
    assert estado_srv.acessos[("/docs/edital-3-2026.pdf", "outro")] + estado_srv.acessos[("/docs/edital-3-2026.pdf", "navegador")] == acessos_pdf
    assert EstadoMotor(dados / "motores/secult-go-teste.db").painel()["fontes"][0]["sem_mudanca"] == 1


def test_configuracao_invalida_e_recusada(tmp_path):
    with pytest.raises(ValueError):
        Configuracao(**{"motor": {"id": "x", "nome": "x", "categoria": "x", "finalidade": "x"}, "fonte": [{"nome": "a", "url": "u", "tipo": "inventado"}]})
    with pytest.raises(ValueError):
        Configuracao(**{"motor": {"id": "x", "nome": "x", "categoria": "x", "finalidade": "x"}, "fonte": [], "chave_inventada": 1})
