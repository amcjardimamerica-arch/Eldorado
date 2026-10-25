"""Os pilotos no site ligados aos dados (titular, 25/10/2026: sem leitura na página inicial e na sala)."""
import shutil
import sqlite3

from eldorado.base.painel.dados import _molde
from eldorado.base.painel.pilotos import montar


def test_os_pilotos_tem_leitura(tmp_path):
    for n in ("biblioteca", "cerebro"):
        shutil.copy(f"dados/{n}.db", tmp_path / f"{n}.db")
    from eldorado.base.fluxo.nos import abrir_bancos
    for c in {id(x): x for x in abrir_bancos(tmp_path).values()}.values():
        c.close()
    arq, status = montar(sqlite3.connect(tmp_path / "biblioteca.db"), sqlite3.connect(tmp_path / "cerebro.db"), _molde)
    assert set(arq) == {"espiao.json", "espiao_ao_vivo.json", "interceptador.json", "interceptador_ao_vivo.json", "esquadrilha.json", "achados_pilotos.json"}
    assert all(arq[f].get("em") or arq[f].get("atualizado_em") for f in arq)                 # nenhum arquivo vazio
    assert set(status) == {"piloto-aberto", "piloto-interceptador"} and all(s["resultado"] for s in status.values())
    assert "ainda sem execução" not in " ".join(s["resultado"] for s in status.values())


def test_os_quadros_dos_pilotos_recebem_o_que_leem(tmp_path, gravador, bancos):
    """25/10/2026 (a titular: "este problema deve ser corrigido definitivamente"): os campos exatos que os quadros do Espião e do
    Interceptador leem, e o sinal de vida dos pilotos (o ligado/agora pelo sinal, não pelo último resultado)."""
    from datetime import datetime, timezone

    from eldorado.base.nucleo.eventos import criar
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    assert gravador.aplicar([criar("medicao.registrada", "piloto:interceptador", {"marcador": "piloto:interceptador", "nivel": "componente", "em": agora,
                                                                                   "ponto": "v", "valor": 1, "motivo": "em voo: um edital"}),
                             criar("medicao.registrada", "piloto:espiao", {"marcador": "piloto:espiao", "nivel": "componente", "em": agora,
                                                                           "ponto": "v", "valor": 1, "motivo": "em voo: missão de busca"})]).ok
    arq, status = montar(bancos["biblioteca"], bancos["cerebro"], _molde)
    iv, ev, e, i = arq["interceptador_ao_vivo.json"], arq["espiao_ao_vivo.json"], arq["espiao.json"], arq["interceptador.json"]
    assert iv["estado"] == "em_voo" and ev["estado"] == "em_voo"                          # o sinal recente: em voo
    assert iv["detalhe"] == "em voo: um edital" and ev["etapa"] == "em voo: missão de busca"
    assert i["estado"] == "em voo" and isinstance(e.get("missoes"), list) and isinstance(i.get("missoes"), list)
    assert all(isinstance(p, dict) and "ordem" in p for p in ev["plano"]) and all(isinstance(c, dict) and "fim" in c for c in ev["concluidas"])
    from eldorado.base.painel.legado import montar as legado
    pv = legado(bancos["biblioteca"], bancos["cerebro"], [], status, _molde)["piloto_ao_vivo.json"]
    assert pv["motor"] in ("ligado", "parado", "desligado") and pv["motor"] == "ligado"   # o quadro do Espião: MOTOR LIGADO
