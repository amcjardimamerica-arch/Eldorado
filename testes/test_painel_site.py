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


def test_o_item_do_radar_e_o_livro_campo_a_campo(tmp_path):
    """Titular, 24/10/2026: o site mostra exatamente os livros da Biblioteca (o checklist, os valores, a estrela, a etapa e a escada)."""
    import collections
    import json
    import shutil
    import sqlite3

    from eldorado.base.fluxo.nos import abrir_bancos
    from eldorado.base.missao import itens as I
    from eldorado.base.painel.dados import gerar
    raiz = tmp_path / "raiz"                                       # como a produção: o banco migrado antes de gerar o site
    (raiz / "dados").mkdir(parents=True)
    for n in ("biblioteca", "cerebro"):
        shutil.copy(f"dados/{n}.db", raiz / "dados" / f"{n}.db")
    for d in ("config", "eldorado"):
        (raiz / d).symlink_to(Path(d).resolve())
    for c in {id(x): x for x in abrir_bancos(raiz / "dados").values()}.values():
        c.close()
    gerar(tmp_path / "site", raiz)
    f = json.loads((tmp_path / "site" / "dados" / "fluxo_oportunidades.json").read_text(encoding="utf-8"))
    itens = [x for v in f["itens_por_uf"].values() for x in v]
    bib = sqlite3.connect(f"file:{raiz / 'dados' / 'biblioteca.db'}?mode=ro", uri=True)
    bib.row_factory = sqlite3.Row
    certs = collections.defaultdict(list)
    for r in bib.execute("SELECT * FROM certidao"):
        certs[r["livro_id"]].append(dict(r))
    estrela = dict(bib.execute("SELECT id, estrela FROM livro").fetchall())
    fase = dict(bib.execute("SELECT livro_id, fase FROM passaporte").fetchall())
    emp = json.loads((tmp_path / "site" / "dados" / "empresas.json").read_text(encoding="utf-8"))["estados"]
    cnpjs = [x["cnpj"] for v in emp.values() if isinstance(v, dict) for x in v.get("empresas", [])]
    assert sorted(cnpjs) == sorted(r[0] for r in bib.execute("SELECT cnpj FROM empresa"))       # as empresas: as mesmas, sem repetir
    for x in itens:
        m = I.melhor(certs.get(x["id"], []))
        assert {k for k, v in x["checklist"].items() if v.get("s")} == {k for k in I.DOZE if I.resolvido(m.get(k))}, x["id"]
        assert x["selo"] == (estrela[x["id"]] or "") and x["etapa"] == fase[x["id"]], x["id"]
