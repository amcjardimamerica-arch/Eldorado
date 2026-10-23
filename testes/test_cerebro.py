from datetime import datetime, timedelta, timezone

import pytest
from conftest import AGORA, ev, livro
from modulos_teste import MissaoTeste, MotorTeste

from eldorado.base.cerebro.aprendizado import Aprendizado
from eldorado.base.cerebro.completude import calcular
from eldorado.base.cerebro.governador import Governador, Leitura
from eldorado.base.cerebro.medicao import Medicao, arquivo_de
from eldorado.base.cerebro.pertinencia import Pertinencia
from eldorado.base.cerebro.rede import Rede
from eldorado.base.cerebro.regencia import Regencia, autorizar
from eldorado.base.cerebro.regras import Regra, Regras
from eldorado.base.cerebro.regras import carregar as carregar_regras
from eldorado.base.fluxo.agenda import Agenda
from eldorado.base.fluxo.agenda import Regra as RegraAgenda
from eldorado.base.nucleo.contratos import Achado, ContratoVioladoErro, Descricao
from eldorado.base.nucleo.eventos import Alvo, ler
from eldorado.base.nucleo.registro import Registro, RegistroErro
from eldorado.base.nucleo.registro import carregar as carregar_registro

SP = timezone(timedelta(hours=-3))


# ------------------------------------------------------------------ regras
def test_regra_vigente_e_a_decisao_mais_recente_da_titular():
    r = carregar_regras("config/regras.toml")
    assert "Sem travas para robôs" in r.vigente("acesso a sites").regra
    assert r.contradicoes() == []


def test_substituicao_e_contradicao_vao_para_o_cerebro(diario, gravador, bancos, tmp_path):
    rs = Regras([Regra("t", "antiga", "2026-01-01", True), Regra("t", "nova", "2026-02-01", True),
                 Regra("x", "um texto", "2026-03-01", True), Regra("x", "outro texto", "2026-03-01", True)])
    assert [t for t, _ in rs.contradicoes()] == ["x"]
    rs.registrar(diario)
    assert gravador.aplicar(ler(tmp_path / "eventos")).ok
    c = bancos["cerebro"]
    assert [tuple(r) for r in c.execute("SELECT regra FROM regra_vigente WHERE tema='t'")] == [("nova",)]
    assert c.execute("SELECT COUNT(*) FROM alarme WHERE modulo='regras'").fetchone()[0] == 1


# ------------------------------------------------------------------ registro
def test_registro_confere_o_contrato_e_arquiva_em_vez_de_apagar(diario):
    reg = Registro(diario)
    reg.registrar(MotorTeste())
    with pytest.raises(RegistroErro):
        reg.registrar(MotorTeste())

    class SemFinalidade(MotorTeste):
        def descrever(self):
            return Descricao(id="x", tipo="motor", parte="MOTORES", finalidade="", metrica="m")
    with pytest.raises(ContratoVioladoErro):
        reg.registrar(SemFinalidade())
    reg.arquivar("motor-teste")
    assert reg.ids() == []
    reg.restaurar("motor-teste")
    assert reg.ids("motor") == ["motor-teste"]


def test_registro_pela_configuracao(tmp_path):
    p = tmp_path / "m.toml"
    p.write_text('[[modulo]]\nclasse = "modulos_teste:MotorTeste"\nparametros = { id = "a" }\n'
                 '[[modulo]]\nclasse = "modulos_teste:MotorTeste"\nligado = false\nparametros = { id = "b" }\n')
    assert carregar_registro(p).ids() == ["a"]
    p.write_text('[[modulo]]\nclasse = "nao_existe:X"\n')
    with pytest.raises(RegistroErro):
        carregar_registro(p)


# ------------------------------------------------------------------ pertinência
def test_pertinencia_decide_com_motivo_e_portao_com_erro_barra_e_alarma(diario, gravador, bancos, tmp_path):
    p = Pertinencia(MissaoTeste(), diario)
    achados = [Achado(id=f"A{i}", motor="m", encontrado_em="2026-10-22", link_divulgacao=f"https://x/{i}", dados={"uf": uf})
               for i, uf in enumerate(["GO", "SP", "QUEBRA"])]
    for a in achados:
        diario.emitir("achado.entregue", "m", {"id": a.id, "motor": "m", "encontrado_em": a.encontrado_em, "link_divulgacao": a.link_divulgacao, "dados": a.dados})
    decisoes = [p.decidir(a).decisao for a in achados]
    assert decisoes == ["aceito", "barrado", "barrado"]
    assert gravador.aplicar(ler(tmp_path / "eventos")).ok
    b = bancos["biblioteca"]
    assert b.execute("SELECT motivo FROM achado WHERE id='A1'").fetchone()[0] == "fora do território: SP"
    assert bancos["cerebro"].execute("SELECT COUNT(*) FROM alarme WHERE modulo='pertinencia'").fetchone()[0] == 1


# ------------------------------------------------------------------ regência
def test_transicoes_de_fase():
    assert autorizar(None, "recepcao")[0] and not autorizar(None, "certificacao")[0]         # todo livro entra pela fase 1
    assert autorizar("recepcao", "certificacao")[0] and not autorizar("recepcao", "farol")[0]
    assert autorizar("certificacao", "farol")[0] and autorizar("certificacao", "preparacao")[0]   # completo → Farol; senão → 3
    assert autorizar("preparacao", "validacao")[0] and autorizar("preparacao", "analise externa")[0]
    assert not autorizar("preparacao", "farol")[0]                                            # a fase 3 não certifica
    assert autorizar("validacao", "farol")[0] and autorizar("analise externa", "farol")[0]
    assert not autorizar("certificacao", "preparacao", tentativas_na_fase=4)[0]
    assert not autorizar("farol", "recepcao")[0]


def _regencia(diario, carga=0.1, motores=None):
    reg = Registro()
    for m in motores or [MotorTeste("bom"), MotorTeste("quebrado", falhar=True)]:
        reg.registrar(m)
    ag = Agenda([RegraAgenda(modulo=i, horarios=("06:00",)) for i in reg.ids()] + [RegraAgenda(modulo="nao-registrado", horarios=("06:00",))])
    return Regencia(ag, Governador(lambda: Leitura(carga, carga, 0.3)), reg, diario, notas={"quebrado": 0.9, "bom": 0.2})


def test_plano_so_com_registrados_e_na_ordem_das_notas(diario):
    plano = _regencia(diario).planejar(datetime(2026, 10, 22, 6, 10, tzinfo=SP))
    assert [m["modulo"] for m in plano["motores"]] == ["quebrado", "bom"]


def test_motor_que_falha_nao_derruba_os_outros(diario, gravador, bancos, tmp_path):
    r = _regencia(diario)
    achados, adiados = r.acionar(r.planejar(datetime(2026, 10, 22, 6, 10, tzinfo=SP)), "exec-1")
    assert len(achados) == 2 and adiados == []
    assert gravador.aplicar(ler(tmp_path / "eventos")).ok
    c = bancos["cerebro"]
    assert dict(c.execute("SELECT chamado_por, COUNT(*) FROM recibo GROUP BY 1").fetchall()) == {"regencia": 2}
    assert c.execute("SELECT erro FROM execucao_motor WHERE motor='quebrado'").fetchone()[0].startswith("ConnectionError")
    assert bancos["biblioteca"].execute("SELECT COUNT(*) FROM achado").fetchone()[0] == 2


def test_sem_folga_o_motor_e_adiado(diario):
    r = _regencia(diario, carga=0.84)
    achados, adiados = r.acionar(r.planejar(datetime(2026, 10, 22, 6, 10, tzinfo=SP)))
    assert achados == [] and sorted(adiados) == ["bom", "quebrado"]


# ------------------------------------------------------------------ aprendizado
def test_ciclo_do_aprendizado(diario, gravador, bancos, tmp_path):
    a = Aprendizado(diario)
    t0 = datetime(2026, 10, 1, tzinfo=timezone.utc)
    for o in ("rota boa", "rota ruim", "rota sem uso"):
        a.registrar("do-goias", o, quando=t0)
    assert gravador.aplicar(ler(tmp_path / "eventos")).ok
    c = bancos["cerebro"]
    ids = dict(c.execute("SELECT o_que, id FROM aprendizado_temporario").fetchall())
    a.usar(ids["rota boa"], 5, 0.9)
    a.usar(ids["rota ruim"], 4, 0.1)
    assert gravador.aplicar(ler(tmp_path / "eventos")).ok
    temporarios = [dict(r) for r in c.execute("SELECT * FROM aprendizado_temporario")]
    r = a.avaliar(temporarios, quando=t0 + timedelta(days=31))
    assert len(r["promovidos"]) == 1 and len(r["arquivados"]) == 1 and len(r["vencidos"]) == 1
    assert gravador.aplicar(ler(tmp_path / "eventos")).ok
    assert c.execute("SELECT COUNT(*) FROM aprendizado_temporario").fetchone()[0] == 0
    assert [tuple(r) for r in c.execute("SELECT o_que, arquivado FROM aprendizado_permanente ORDER BY o_que")] == [("rota boa", 0), ("rota ruim", 1)]


def test_so_o_temporario_pode_ser_apagado(gravador, bancos):
    gravador.aplicar([livro()])
    con = bancos["biblioteca"]
    con.execute("BEGIN")
    with pytest.raises(ValueError, match="nada se apaga"):
        gravador._executar(con, Alvo("biblioteca", "livro", "apagar", ("id",)), {"id": "L1"})
    con.execute("ROLLBACK")
    assert con.execute("SELECT COUNT(*) FROM livro").fetchone()[0] == 1
    with pytest.raises(ValueError):
        Aprendizado(None, retencao_dias=31)


def test_temporario_expirado_sai_e_nada_da_biblioteca_some(gravador, bancos, diario, tmp_path):
    gravador.aplicar([livro(), ev("aprendizado.registrado", o_que="x", criado_em=AGORA, expira_em="2026-11-01T00:00:00+00:00")])
    tid = bancos["cerebro"].execute("SELECT id FROM aprendizado_temporario").fetchone()[0]
    assert gravador.aplicar([ev("aprendizado.expirado", id=tid)]).ok
    assert bancos["biblioteca"].execute("SELECT COUNT(*) FROM livro").fetchone()[0] == 1


# ------------------------------------------------------------------ rede
def test_rede_aprende_e_mede_com_honestidade(tmp_path, diario, gravador, bancos):
    import random
    rnd = random.Random(7)
    rede = Rede()
    for _ in range(600):
        uf = rnd.choice(["GO", "SP", "MG"])
        oficial = rnd.random() < 0.5
        rede.aprender({"uf": uf, "link_oficial": "https://o" if oficial else None, "titulo": "edital de fomento"}, uf == "GO" and oficial)
    m = rede.metricas()
    assert m["discernimento"] > 0.85
    assert rede.nota({"uf": "GO", "link_oficial": "https://o"}) > rede.nota({"uf": "SP"})
    rede.salvar(tmp_path / "modelo", diario)
    assert Rede.carregar(tmp_path / "modelo").amostras == 600
    assert gravador.aplicar(ler(tmp_path / "eventos")).ok
    assert bancos["cerebro"].execute("SELECT discernimento FROM modelo").fetchone()[0] > 0.85


# ------------------------------------------------------------------ completude
def test_completude_aponta_o_que_reacionar(diario):
    r = calcular(diario, "2026-10-22", ["a", "b", "c"], ["a", "c"])
    assert r["motores_devidos"] == 3 and r["motores_lidos"] == 2 and r["completo"] == 0 and r["reacionar"] == ["b"]


# ------------------------------------------------------------------ medição
CAT = [{"arquivo": "eldorado/x/a.py", "parte": "BASE", "componente": "C1", "ligacoes": ["eldorado/x/b.py"], "critico": True, "metrica": "m"},
       {"arquivo": "eldorado/x/b.py", "parte": "BASE", "componente": "C1", "ligacoes": [], "critico": False, "metrica": "m"},
       {"arquivo": "eldorado/x/c.py", "parte": "BASE", "componente": "C2", "ligacoes": ["eldorado/x/a.py"], "critico": False, "metrica": "m"}]


def rec(mod, ok=1):
    return {"modulo": f"eldorado.x.{mod}:f", "ok": ok}


def test_regras_do_ponto_circulo_e_linhas():
    r = Medicao(CAT).calcular([rec("a"), rec("a", 0), rec("a"), rec("b")])
    a, b, c = (r["arquivos"][f"eldorado/x/{n}.py"] for n in "abc")
    assert (a["ponto"], a["circulo"], a["linhas"]) == ("a", "r", "v")      # uma falha, 67% de sucesso, ligação exercida
    assert (b["ponto"], b["circulo"], b["linhas"]) == ("v", "v", "v")
    assert (c["ponto"], c["circulo"], c["linhas"]) == ("c", "c", "c")      # não chamado: cinza, sem esconder
    assert r["componentes"]["C1"]["ponto"] == "r"                          # crítico com círculo vermelho
    assert r["sistema"]["ponto"] == "r"


def test_alarme_critico_deixa_o_sistema_vermelho_e_motor_e_medido_a_parte():
    r = Medicao(CAT).calcular([rec("a"), rec("b"), {"modulo": "do-goias", "ok": 1}], alarmes_criticos=1)
    assert r["motores"]["do-goias"]["ponto"] == "v" and r["sistema"]["ponto"] == "r"
    assert arquivo_de("eldorado.base.cerebro.regencia:no_planejar") == "eldorado/base/cerebro/regencia.py" and arquivo_de("do-goias") is None
