"""Os modelos em lote do Cérebro: medidos em ordem cronológica e usados só onde discernem melhor que o contínuo."""

import random

import pytest

from eldorado.base.cerebro import lote


def casos(n, sinal=True):
    r = random.Random(3)
    saida = []
    for i in range(n):
        v = r.random() < 0.5
        x = {"motor=a": 1.0 if (v if sinal else r.random() < 0.5) else 0.0, "ruido": r.random()}
        saida.append((f"2026-{i:05d}", "acao", x, v))
    return saida


def test_lote_aprende_o_sinal_e_recusa_poucos_casos():
    pytest.importorskip("sklearn")
    c = casos(200)
    m = lote.treinar([x for *_, x, _ in c], [v for *_, v in c])
    assert m is not None and m.discernimento > 0.9 and m.nota({"motor=a": 1.0, "ruido": 0.5}) > 0.5
    assert lote.treinar([x for *_, x, _ in c[:10]], [v for *_, v in c[:10]]) is None  # poucos casos: fica o contínuo


def test_compara_e_liga_so_onde_discerne_melhor():
    pytest.importorskip("sklearn")
    from eldorado.base.cerebro.rede import RedeNeural

    rede = RedeNeural()
    c = casos(200)
    for _, p, x, v in c:
        rede.p[p].aprender_de(x, v)
    relato = lote.comparar_e_ligar(rede, c)
    assert relato["acao"]["usa"] in ("lote", "contínuo") and relato["oportunidade"]["lote"] == "poucos casos"
    assert (rede.p["acao"].lote is not None) == (relato["acao"]["usa"] == "lote")


# ---- 29/10/2026 (titular): a etapa 5 do Cartório leva TODA a fila ao Chrome (o lote de 40 por dia deixava 146 parados)
def _fila(gravador, n, prefixo="A"):
    from test_linha_cartorio import livro

    eventos = []
    for i in range(n):
        eventos += livro(f"{prefixo}{i:03d}", "analise externa")
    assert gravador.aplicar(eventos).ok


def test_a_gerar_lote_sem_limite_leva_todos(gravador, bancos):
    from datetime import date

    from eldorado.base.cartorio.analise_externa import gerar_lote

    _fila(gravador, 60)
    assert len(gerar_lote(bancos["biblioteca"], date(2026, 10, 29))["livros"]) == 60


def test_b_o_limite_vem_da_configuracao(gravador, bancos, tmp_path):
    from datetime import date

    from eldorado.base.cartorio.analise_externa import atualizar_lote_do_dia, config_analise_externa, gerar_lote

    _fila(gravador, 60)
    (tmp_path / "cartorio.toml").write_text("[analise_externa]\nmaximo_lote = 40\ntamanho_parte = 50\n", encoding="utf-8")
    cfg = config_analise_externa(tmp_path / "cartorio.toml")
    assert cfg["maximo_lote"] == 40 and len(gerar_lote(bancos["biblioteca"], date(2026, 10, 29), cfg["maximo_lote"])["livros"]) == 40
    assert atualizar_lote_do_dia(bancos["biblioteca"], tmp_path / "lotes", date(2026, 10, 29), cfg=cfg)["livros"] == 40
    (tmp_path / "zero.toml").write_text("[analise_externa]\nmaximo_lote = 0\n", encoding="utf-8")
    assert config_analise_externa(tmp_path / "zero.toml")["maximo_lote"] is None  # 0 = todos
    assert config_analise_externa(tmp_path / "nao-existe.toml")["maximo_lote"] is None  # ausente = todos


def test_c_o_lote_e_regerado_quando_a_fila_muda(gravador, bancos, diario, tmp_path):
    import json
    from datetime import date

    from test_linha_cartorio import aplicar

    from eldorado.base.cartorio.analise_externa import atualizar_lote_do_dia, importar

    _fila(gravador, 5)
    b, pasta, dia, cfg = bancos["biblioteca"], tmp_path / "lotes", date(2026, 10, 29), {"maximo_lote": None, "tamanho_parte": 50}
    r = atualizar_lote_do_dia(b, pasta, dia, cfg=cfg)
    assert r["mudou"] and r["livros"] == 5
    assert not atualizar_lote_do_dia(b, pasta, dia, cfg=cfg)["mudou"]  # nada mudou: não regrava
    r = atualizar_lote_do_dia(b, pasta, dia, saiu={"A001"}, cfg=cfg)  # um livro saiu da etapa
    ids = [x["livro_id"] for x in json.loads((pasta / "lote-2026-10-29.json").read_text())["livros"]]
    assert r["mudou"] and "A001" not in ids and len(ids) == 4
    # o livro com veredito que continua na etapa (faltam itens) vai ao fim, marcado como retorno
    from test_linha_cartorio import VALORES, livro

    assert gravador.aplicar(livro("R000", "analise externa", itens=[k for k in VALORES if k not in ("Anexos", "Prazo de recurso")])).ok
    importar(json.dumps({"lote": "lote-2026-10-29", "vereditos": [{"livro_id": "R000", "decisao": "valido"}]}), b, diario)
    aplicar(gravador, tmp_path)
    atualizar_lote_do_dia(b, pasta, dia, cfg=cfg)
    livros = json.loads((pasta / "lote-2026-10-29.json").read_text())["livros"]
    assert livros[-1]["livro_id"] == "R000" and livros[-1]["retorno"] is True and set(livros[-1]["faltam"]) == {"Anexos", "Prazo de recurso"}
    assert not any(x.get("retorno") for x in livros[:-1])
    todos = {x["livro_id"] for x in json.loads((pasta / "lote-2026-10-29.json").read_text())["livros"]}
    r = atualizar_lote_do_dia(b, pasta, dia, saiu=todos, cfg=cfg)  # a etapa vazia
    assert r["lote"] is None and not (pasta / "lote-2026-10-29.json").exists()


def test_d_as_partes_somam_o_total_sem_repetir(gravador, bancos, tmp_path):
    import json
    from datetime import date

    from eldorado.base.cartorio.analise_externa import atualizar_lote_do_dia

    _fila(gravador, 120)
    pasta = tmp_path / "lotes"
    r = atualizar_lote_do_dia(bancos["biblioteca"], pasta, date(2026, 10, 29), cfg={"maximo_lote": None, "tamanho_parte": 50})
    assert r["partes"] == ["lote-2026-10-29-parte-1", "lote-2026-10-29-parte-2", "lote-2026-10-29-parte-3"]
    completo = [x["livro_id"] for x in json.loads((pasta / "lote-2026-10-29.json").read_text())["livros"]]
    partes = [[x["livro_id"] for x in json.loads((pasta / f"{n}.json").read_text())["livros"]] for n in r["partes"]]
    assert [len(p) for p in partes] == [50, 50, 20] and sum(partes, []) == completo and len(set(completo)) == 120
    # a fila encolhe para 40: as partes somem (o arquivo completo fica)
    r = atualizar_lote_do_dia(
        bancos["biblioteca"], pasta, date(2026, 10, 29), saiu=set(completo[40:]), cfg={"maximo_lote": None, "tamanho_parte": 50}
    )
    assert r["partes"] == [] and not list(pasta.glob("*-parte-*.json")) and (pasta / "lote-2026-10-29.json").exists()


def test_e_importar_aceita_o_veredito_de_uma_parte(gravador, bancos, diario):
    import json

    from eldorado.base.cartorio.analise_externa import importar

    _fila(gravador, 2)
    r = importar(
        json.dumps({"lote": "lote-2026-10-29-parte-2", "vereditos": [{"livro_id": "A001", "decisao": "descartar", "motivo": "não é edital"}]}),
        bancos["biblioteca"],
        diario,
    )
    assert r == [{"livro": "A001", "descartado": True}]
