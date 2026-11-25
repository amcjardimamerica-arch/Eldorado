"""C-05 da manutenção de 23/11 (pendente em 25/11, P-02): com o diário, o uso do objetivo só chega ao Cérebro quando a
passagem aplica os eventos; durante o voo o «menos usado» era sempre o mesmo — a mesma consulta 40 vezes em 2 h 30
(23/11) e «Fundação Walmart» 19 vezes (25/11); 56% de consultas diferentes. R55, R57 («a busca é diferente a cada
tentativa»; «o local de busca não se repete»), R35 (a gravação continua só por evento)."""
from __future__ import annotations

import json
import random

from eldorado.base.nucleo.eventos import Diario
from eldorado.motores.pilotos.espiao import Espiao


def test_o_espiao_com_diario_nao_repete_objetivo_nem_consulta_no_mesmo_voo(tmp_path):
    consultas_feitas: list[str] = []

    def consultar(q):
        consultas_feitas.append(q)
        return [], ["searxng: 0 pista(s), 0 nova(s)"]

    db = tmp_path / "cerebro.db"
    prep = Espiao(db, consultar, lambda u: None, rnd=random.Random(1))
    prep.con.executemany("INSERT INTO espiao_objetivo(id, tipo, alvo, prioridade, consultas) VALUES (?, ?, ?, ?, ?)",
                         [(f"OBJ-{i:03d}", "financiador conhecido", f"Fundação {i}", 1,
                           json.dumps([f'"Fundação {i}" edital {{ano}}', f'"Fundação {i}" inscrições {{ano}}'])) for i in range(60)])
    prep.con.commit()
    prep.con.close()
    diario = Diario(tmp_path / "eventos", "voo")
    objetivos = []
    for _ in range(50):                                   # 50 missões seguidas, com o diário e SEM aplicar os eventos
        e = Espiao(db, consultar, lambda u: None, rnd=random.Random(1), diario=diario)   # recriado a cada missão, como no voo
        e.missao()
        objetivos.append(json.loads(json.dumps([x.dados for x in diario.eventos() if x.tipo == "espiao.missao"][-1])).get("objetivo"))
        e.con.close()
    assert len(consultas_feitas) == 50 and len(set(consultas_feitas)) == 50
    assert len(set(objetivos)) == 50
