"""R56 (titular, 14/11/2026): a fonte que só pode ser lida no computador local não é alerta da Sala de controle."""
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from eldorado.base.cerebro.sinais_motores import sinais
from eldorado.base.painel import sala
from eldorado.motores.acesso.escada import Pendente
from eldorado.motores.acesso.local import DegrauLocal


def _cer(linhas):
    c = sqlite3.connect(":memory:")
    c.executescript("CREATE TABLE motor_fonte(motor TEXT, nome TEXT, leituras INT, sem_mudanca INT, falhas INT, ultimo_erro TEXT, ultima TEXT, situacao TEXT);"
                    "CREATE TABLE motor_entregue(motor TEXT, em TEXT); CREATE TABLE execucao_motor(motor TEXT, inicio TEXT);")
    c.executemany("INSERT INTO motor_fonte VALUES ('m', ?, 1, 0, 1, ?, ?, ?)", linhas)
    c.execute("INSERT INTO motor_entregue VALUES ('m', ?)", (datetime.now(timezone.utc).isoformat(),))
    return c


def test_a_sala_nao_tem_o_mostrador_das_fontes_do_computador_local():
    assert "mo_pendentes_local" not in sala.ETAPAS["coleta"] and "mo_pendentes_local" not in sala.RELOGIOS["coleta"]
    assert 'I("mo_pendentes_local"' not in Path("eldorado/base/painel/sala.py").read_text(encoding="utf-8")
    assert "mo_pendentes_local" not in Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")


def test_a_fonte_do_computador_local_nao_acende_o_motor():
    agora = datetime.now(timezone.utc).isoformat()
    c = _cer([("a", "pendente no computador local", agora, "erro"), ("b", "", agora, "lida")])
    s = sinais(c, "m", ["a", "b"], especial=True, rara=True)
    assert s["luz"] == "verde" and s["coleta_local"] == ["a"] and not any("computador local" in x for x in s["sinais"])
    so_local = sinais(_cer([("a", "pendente no computador local", agora, "erro")]), "m", ["a"], especial=True, rara=True)
    assert so_local["luz"] == "cinza"                                   # todas de coleta local: sem cor de alerta
    nova = sinais(_cer([("b", "", agora, "lida")]), "m", ["b", "nova"], especial=True, rara=True)
    assert nova["aguardando_primeira_leitura"] == ["nova"] and nova["abandonadas"] == []   # S7


def test_o_resultado_do_motor_diz_que_exige_coleta_local():
    d = Path("eldorado/base/painel/dados.py").read_text(encoding="utf-8")
    assert "fonte(s) exigem coleta local:" in d and '" · ⚠ {len(sg[\'coleta_local\'])}' not in d


def test_nenhum_pedido_novo_ao_computador_local(tmp_path):
    try:
        DegrauLocal(tmp_path).buscar("https://www.tjgo.jus.br/x", 10)
    except Pendente as e:
        assert "coleta local" in str(e)
    assert not list((tmp_path / "pedidos").glob("*.json"))


def test_o_ponte_php_e_a_lista_do_sistema_tem_os_mesmos_dominios():
    import importlib.util
    spec = importlib.util.spec_from_file_location("gerar_ponte", "scripts/gerar_ponte.py")
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    php = Path("ponte/ponte.php").read_text(encoding="utf-8")
    bloco = php[php.index("const DOMINIOS = ["):php.index("];", php.index("const DOMINIOS = ["))]
    assert sorted(set(re.findall(r"'([^']+)'", bloco))) == g.dominios() and "github" not in php.lower()
    cfg = {x.strip() for x in Path("config/ponte_dominios.txt").read_text(encoding="utf-8").splitlines() if x.strip() and not x.startswith("#")}
    assert cfg <= set(g.dominios())
    _ = timedelta


def test_a_limpeza_nao_apaga_o_ciente_nem_as_marcas_dos_ciclos(tmp_path):
    from eldorado.base.cerebro.retencao import reter
    c = sqlite3.connect(tmp_path / "c.db")
    c.execute("CREATE TABLE medicao(marcador TEXT, em TEXT, valor REAL)")
    velho = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
    c.executemany("INSERT INTO medicao VALUES (?, ?, 0)", [("ciente:farol:fa_fecham_7d", velho), ("ciclo:reset", velho), ("rede:x", velho)])
    c.commit()
    c.close()
    reter(tmp_path / "c.db", tmp_path / "ev")
    ficou = {r[0] for r in sqlite3.connect(tmp_path / "c.db").execute("SELECT marcador FROM medicao")}
    assert ficou == {"ciente:farol:fa_fecham_7d", "ciclo:reset"}


def test_o_acerto_nos_50_na_janela_de_7_dias():
    from eldorado.base.cerebro.rede import metricas_por_contagem
    agora = datetime.now(timezone.utc)
    velhos = [((agora - timedelta(days=20)).isoformat(), True, 0.99) for _ in range(300)]
    novos = [((agora - timedelta(days=1)).isoformat(), False, 0.9) for _ in range(30)]
    m = metricas_por_contagem(velhos + novos, 0.5, n=500, minimo=300)
    assert m["acerto_50"] == 0.0 and m["rotulos_7d"] == 30            # só a semana: os 300 antigos não contam


def test_o_ultimo_expurgo_conta_a_importacao_do_chrome(tmp_path):
    import json

    from eldorado.base.painel.sala import _ultima_importacao_com_descarte
    (tmp_path / "veredito-lote-2026-11-14-externa-grupo-1.json").write_text(json.dumps({"vereditos": [{"decisao": "descartar"}, {"decisao": "valido"}]}))
    u = _ultima_importacao_com_descarte(tmp_path)
    assert u["em"].startswith("2026-11-14") and "1 descarte" in u["motivo"]
