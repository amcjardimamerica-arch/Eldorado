"""A arquitetura dos bancos (titular, desde o planejamento; reforçada em 24/10/2026):
- só dois bancos: a Biblioteca (os livros e as empresas) e o Cérebro (o aprendizado, nunca livros);
- nenhum motor tem banco: o motor só lê o aprendizado do Cérebro e entrega o que aprende por eventos;
- o Cérebro guarda só o resumo dos passos (nunca o conteúdo dos achados)."""
import re
import sqlite3
from pathlib import Path

PERMITIDOS = {"biblioteca.db", "cerebro.db"}


def test_o_codigo_so_abre_a_biblioteca_e_o_cerebro():
    proibidos = []
    for p in Path("eldorado").rglob("*.py"):
        if p.as_posix() == "eldorado/banco/consolidar.py":                       # importa e apaga os bancos antigos
            continue
        for linha in p.read_text(encoding="utf-8").splitlines():
            if linha.lstrip().startswith("#"):
                continue
            for nome in re.findall(r"[\"'/ ]([a-z_]+\.db)[\"']", linha):
                if nome not in PERMITIDOS:
                    proibidos.append(f"{p}: {nome}")
    assert not proibidos, proibidos


def test_o_motor_nao_escreve_banco(tmp_path):
    from eldorado.motores.canal.estado import EstadoMotor
    e = EstadoMotor(tmp_path / "motores", "teste")
    assert e.caminho == tmp_path / "cerebro.db"
    try:
        e.con.execute("INSERT INTO motor_entregue VALUES ('teste', 'k', '2026', NULL, NULL)")
        escreveu = True
    except sqlite3.OperationalError:
        escreveu = False
    assert not escreveu                                                            # a conexão do motor é só leitura
    assert not list((tmp_path / "motores").glob("*.db")) if (tmp_path / "motores").exists() else True


def test_o_cerebro_guarda_so_o_resumo_dos_passos():
    from eldorado.base.nucleo.eventos import CATALOGO
    mapa = CATALOGO["execucao.passo"][0].mapa
    r = mapa({"execucao": "x", "passo": 1, "no": "acionar", "estado": "concluido", "em": "2026",
              "entrada": [], "saida": [{"id": "a1", "titulo": "Edital de fomento", "link_divulgacao": "https://x"}]})
    assert r["saida"] == {"itens": 1, "ids": ["a1"]} and "titulo" not in str(r)
