"""O site do painel é a imagem do sistema novo (titular, 23/10/2026): nenhum dado do Eldorado0, e cada número vem do banco."""
import json
import re
from pathlib import Path

MOLDE = Path("eldorado/base/painel/molde")


def test_o_molde_nao_tem_nenhum_dado():
    texto = "".join(p.read_text(encoding="utf-8") for p in MOLDE.glob("*.json") if p.name != "itens.json")
    assert not re.findall(r':\s*("[^"]+"|[1-9]\d*|true)', texto)                                     # nenhum valor
    assert not [k for k in re.findall(r'"([^"]+)":', texto) if re.search(r"\d{3,}|^\d{4}-\d{2}|^https?:", k)]  # nenhuma chave que seja dado
    itens = json.loads((MOLDE / "itens.json").read_text(encoding="utf-8"))
    assert not re.findall(r':\s*("[^"]+"|[1-9]\d*|true)', json.dumps({k: v for k, v in itens.items() if not k.startswith("campos_")}))


def test_a_pagina_le_so_o_proprio_site():
    s = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    assert "raw.githubusercontent.com" not in s and "Eldorado0" not in s
    assert 'const REPO_RAW="";' in s and 'window.tokenLeitura=()=>"";' in s
    assert "eldorado_fluxo_valido_sistema_novo" in s                                          # o navegador descarta o mapa antigo


def test_o_site_gerado_bate_com_o_banco(tmp_path):
    import sqlite3

    from eldorado.base.painel.dados import gerar
    r = gerar(tmp_path / "site")
    b = sqlite3.connect("dados/biblioteca.db")
    abertas = b.execute("SELECT COUNT(*) FROM livro l JOIN livro_dados d ON d.livro_id = l.id WHERE d.situacao_prazo = 'aberta' AND l.situacao <> 'excluido'").fetchone()[0]
    assert r["oportunidades_abertas"] == abertas and r["motores"] == len(json.loads(Path("config/motores_previstos.json").read_text())["motores"])
    st = json.loads((tmp_path / "site/dados/status_motores.json").read_text(encoding="utf-8"))
    assert len(st["motores"]) == r["motores"] and st["contagem"]["verde"] + st["contagem"]["vermelho"] + st["contagem"]["cinza"] == r["motores"]
    assert "window.DADOS=" in (tmp_path / "site/dashboard-dados.js").read_text(encoding="utf-8")[:20]
    fl = json.loads((tmp_path / "site/dados/fluxo_oportunidades.json").read_text(encoding="utf-8"))
    assert fl["validacao"]["aplicada"] and fl["mapa"]["total"]["confirmadas"] + fl["mapa"]["total"]["possiveis"] == abertas
