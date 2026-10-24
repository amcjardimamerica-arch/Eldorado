"""Critério de pronto da Fase 3: uma passagem é planejada, acionada e medida, e cada arquivo ganha ponto, círculo e linhas."""
import json
from datetime import datetime
from zoneinfo import ZoneInfo

from eldorado.base.fluxo.definicao import carregar
from eldorado.base.fluxo.executor import Executor
from eldorado.base.fluxo.nos import abrir_bancos

# a hora da passagem no dia de HOJE: o histórico das execuções é gravado com o relógio real (um dia fixo quebra na virada)
HOJE_0610 = datetime.now(ZoneInfo("America/Sao_Paulo")).replace(second=0, microsecond=0).isoformat()   # a hora real: um horário fixo ficava no futuro de madrugada

def preparar(tmp_path):
    (tmp_path / "modulos.toml").write_text('[[modulo]]\nclasse = "modulos_teste:MotorTeste"\nparametros = { id = "bom" }\n'
                                           '[[modulo]]\nclasse = "modulos_teste:MotorTeste"\nparametros = { id = "quebrado", falhar = true }\n')
    (tmp_path / "agenda.toml").write_text('[[modulo]]\nid = "bom"\nhorarios = ["06:00"]\n[[modulo]]\nid = "quebrado"\nhorarios = ["06:00"]\n')
    comum = {"modulos": str(tmp_path / "modulos.toml"), "dados": str(tmp_path / "dados"), "carga_fixa": 0.1}
    nos = [("planejar", "eldorado.base.cerebro.regencia:no_planejar", {**comum, "agenda": str(tmp_path / "agenda.toml"), "agora": HOJE_0610}),
           ("acionar", "eldorado.base.cerebro.regencia:no_acionar", comum),
           ("decidir", "eldorado.base.cerebro.pertinencia:no_decidir", {"missao": "modulos_teste:MissaoTeste"}),
           ("aplicar", "eldorado.base.fluxo.nos:aplicar_eventos", {"dados": str(tmp_path / "dados"), "eventos": str(tmp_path / "ev")}),
           ("aprender", "eldorado.base.cerebro.aprendizado:no_aprendizado", {"dados": str(tmp_path / "dados")}),
           ("completude", "eldorado.base.cerebro.completude:no_completude", {}),
           ("medir", "eldorado.base.cerebro.medicao:no_medir", {"catalogo": "config/arquivos.json"}),
           ("aplicar_final", "eldorado.base.fluxo.nos:aplicar_eventos", {"dados": str(tmp_path / "dados"), "eventos": str(tmp_path / "ev")})]
    linhas = ['[workflow]\nid = "passagem-teste"\n']
    for i, t, p in nos:
        linhas.append(f'[[no]]\nid = "{i}"\ntipo = "{t}"\nparametros = {json.dumps(p)}\n'.replace('": ', '" = ').replace('{"', '{ "').replace(', "', ', "'))
    for a, b in zip([n[0] for n in nos], [n[0] for n in nos][1:], strict=False):
        linhas.append(f'[[conexao]]\nde = "{a}"\npara = "{b}"\n')
    wf = tmp_path / "passagem.toml"
    wf.write_text("\n".join(linhas))
    return wf


def test_passagem_planejada_acionada_e_medida(tmp_path):
    wf = preparar(tmp_path)
    r = Executor(carregar(wf), tmp_path / "ev").executar()
    assert r.estado == "concluida", r.erro
    assert len(r.saidas["acionar"]) == 2 and len(r.saidas["decidir"]) == 1        # o motor quebrado não derrubou o bom; só Goiás passou
    assert r.saidas["completude"][0]["reacionar"] == ["quebrado"]
    b = abrir_bancos(tmp_path / "dados")
    try:
        c = b["cerebro"]
        catalogo = json.load(open("config/arquivos.json"))["arquivos"]
        medidos = {m: (p, ci, li) for m, p, ci, li in c.execute("SELECT marcador, ponto, circulo, linhas FROM medicao WHERE nivel='arquivo'")}
        assert set(medidos) == {a["arquivo"] for a in catalogo}                                         # cada arquivo ganhou a sua medição
        assert all(p and ci and li for p, ci, li in medidos.values())                                    # com ponto, círculo e linhas
        for arq in ("eldorado/base/cerebro/regencia.py", "eldorado/base/cerebro/pertinencia.py", "eldorado/base/fluxo/nos.py"):
            assert medidos[arq][0] == "v", (arq, medidos[arq])
        assert medidos["eldorado/base/cartorio/cartorio.py"] == ("c", "c", "c")                          # ainda não construído: cinza
        assert c.execute("SELECT ponto FROM medicao WHERE nivel='motor' AND marcador='quebrado'").fetchone()[0] == "r"
        assert c.execute("SELECT COUNT(*) FROM medicao WHERE nivel='sistema'").fetchone()[0] == 1
        assert tuple(c.execute("SELECT motores_devidos, motores_lidos, completo FROM cobertura_dia").fetchone()) == (2, 1, 0)
        assert [tuple(r) for r in b["biblioteca"].execute("SELECT decisao, COUNT(*) FROM achado GROUP BY 1")] == [("aceito", 1), ("barrado", 1)]
    finally:
        for con in b.values():
            con.close()
    r2 = Executor(carregar(wf), tmp_path / "ev").executar()                                              # mesma janela, segunda passagem
    assert r2.estado == "concluida" and r2.saidas["acionar"] == []                                       # uma passagem por janela
