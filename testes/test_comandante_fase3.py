"""A fase 3 (titular, 25/10/2026; a engenharia do n8n): o nó de agente do Comandante escolhe as etapas da passagem e o
"Escolher" do executor pula as escolhidas (as seguintes continuam). Em sombra até o parâmetro comandante.aciona = sim."""

import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from eldorado.base.comandante import escolher as E
from eldorado.base.fluxo.definicao import de_dicionario
from eldorado.base.fluxo.executor import Executor
from eldorado.base.nucleo.eventos import Diario


def test_o_executor_pula_o_que_o_agente_escolheu(tmp_path):
    d = de_dicionario(
        {
            "workflow": {"id": "t"},
            "no": [{"id": i, "tipo": f"nos_teste:{f}"} for i, f in (("agente", "agente_pula_a"), ("a", "contar"), ("b", "contar"))],
            "conexao": [{"de": "agente", "para": "a", "saida": "ordem"}, {"de": "a", "para": "b", "saida": "ordem"}],
        }
    )
    r = Executor(d, tmp_path / "ev").executar()
    passos = {e.dados["no"]: e.dados["estado"] for e in Diario(tmp_path / "ev", r.execucao).eventos() if e.tipo == "execucao.passo"}
    assert (
        r.estado == "concluida" and passos["a"] == "pulado" and passos["b"] == "concluido"
    )  # a pulada; b, depois dela, rodou                                   # a foi pulada; b, depois dela, rodou


def _passos(c, no, saidas, base):
    for i, _s in enumerate(saidas):
        c.execute(
            "INSERT OR IGNORE INTO execucao(id, workflow, versao, inicio, estado) VALUES (?, 'passagem', 1, ?, 'concluida')",
            (f"x{i}", base.isoformat()),
        )
    for i, s in enumerate(saidas):
        c.execute(
            "INSERT INTO execucao_passo VALUES (?, ?, ?, ?, '[]', ?, ?)",
            (
                f"x{i}",
                hash(no) % 1000 + 10 * len(saidas),
                no,
                "concluido" if s != "pulado" else "pulado",
                json.dumps(s if s != "pulado" else []),
                (base - timedelta(hours=i)).isoformat(),
            ),
        )


def test_a_escolha_pela_necessidade_e_a_sombra(bancos, tmp_path):
    c, agora = bancos["cerebro"], datetime.now(timezone.utc)
    _passos(c, "farol", [[{"transferidos": 0}]] * 6, agora)  # 6 passagens sem render: candidata
    _passos(c, "validar", [[{"validados": 0}]] * 5 + [[{"validados": 2}]], agora)  # rendeu em uma: roda
    _passos(c, "aplicar_final", [[]] * 8, agora)  # essencial: nunca é pulada
    c.commit()
    assert [x["no"] for x in E.escolher(c)] == ["farol"]
    ctx = SimpleNamespace(diario=Diario(tmp_path / "ev", "c"), execucao="X")
    r = E.no_comandante_escolher([], {"dados": str(tmp_path)}, ctx)[0]
    assert r["pular"] == ["farol"] and not r["aciona"] and "__pular__" not in r  # em sombra: registra, não pula
    c.execute("INSERT INTO parametro VALUES ('comandante', 'aciona', 1, 'sim', NULL, 'titular', ?)", (agora.isoformat(),))
    c.commit()
    assert E.no_comandante_escolher([], {"dados": str(tmp_path)}, ctx)[0]["__pular__"] == ["farol"]  # ligado: pula
    _passos(c, "farol", ["pulado"] * 3, agora + timedelta(hours=10))
    c.commit()
    assert "farol" not in [x["no"] for x in E.escolher(c)]  # nunca mais de 3 seguidas
