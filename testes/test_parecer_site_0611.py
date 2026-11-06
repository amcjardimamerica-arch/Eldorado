"""06/11/2026 (parecer de teste do site): as travas dos mostradores — nada de «undefined», de verde sem régua, de soma
que não fecha ou de contador negativo."""
import json
import sqlite3
from pathlib import Path

from eldorado.base.painel import dados, pilotos, sala


def test_o_relatorio_da_titular_e_o_do_comandante(tmp_path):
    rel = tmp_path / "verificacao" / "relatorios"
    rel.mkdir(parents=True)
    bom = {"em": "2026-11-06T09:16:00+00:00", "redigido_por": "o Comandante", "redacao": {"resumo": "x", "prioridades": []},
           "abertas": 1, "ouro_abertas": 0, "novidades": {}, "falta": {}}
    (rel / "2026-11-06-0916.json").write_text(json.dumps(bom))
    (rel / "relatorio-melhoria-motores-grupo-3.json").write_text(json.dumps({"grupo": 3, "lote": "x", "livros": []}))
    s = Path("eldorado/base/painel/dados.py").read_text(encoding="utf-8")
    assert 'glob("20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9].json")' in s and "all(k in _d for k in _OBRIG)" in s
    h = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    assert '"em","redigido_por","redacao","abertas","ouro_abertas","novidades","falta"].every' in h


def test_o_espiao_fecha_as_contas():
    b = sqlite3.connect("file:dados/biblioteca.db?mode=ro", uri=True)
    c = sqlite3.connect("file:dados/cerebro.db?mode=ro", uri=True)
    e = pilotos.montar(b, c, dados._molde)[0]["espiao.json"]
    a = e["acumulado"]
    assert a["com_resultado"] + a["nada_no_crivo"] + a["fora_do_objeto"] + a["busca_sem_resposta"] == a["missoes"]
    assert sum(x["achados"] for x in e["aprendizado"]["rendimento_por_tipo"].values()) == a["achados_das_missoes"]
    assert all(isinstance(x, dict) for x in e["aprendizado"]["buscas_que_funcionam"] + e["aprendizado"]["buscas_que_falham"])


def test_nenhum_instrumento_verde_sem_regua_e_a_regua_unica():
    b = sqlite3.connect("file:dados/biblioteca.db?mode=ro", uri=True)
    c = sqlite3.connect("file:dados/cerebro.db?mode=ro", uri=True)
    d = sala.montar(b, c, Path("."), [])
    assert not [x["id"] for x in d["instrumentos"] if x["estado"] == "verde" and not x.get("faixa")]
    assert all(x.get("cadencia_h") is not None and x.get("faz") for x in d["instrumentos"])
    from eldorado.base.cartorio.regua import regua
    r = regua(b)
    v = {x["id"]: x["valor"] for x in d["instrumentos"]}
    assert v["es_abertas"] == r["abertas"] and r["validadas"] + r["em_verificacao"] == r["abertas"]


def test_nenhum_contador_negativo_no_fluxo():
    f = dados._fluxo(dados.Sistema(Path(".")), "2026-11-06T12:00:00+00:00")
    assert f["validacao"]["sem_decisao"] >= 0
