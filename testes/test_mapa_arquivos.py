"""O mapa REAL dos arquivos (titular, 24/10/2026): todo arquivo do sistema no mapa, ligado pelo que comunica, e nenhum
arquivo fora do funcionamento sem decisão registrada."""
import tomllib
from pathlib import Path

from eldorado.base.cerebro.mapa_arquivos import montar

# os arquivos fora do funcionamento hoje, cada um com o motivo (a titular decide: ligar ou retirar)
PARADOS = {
    "eldorado/base/cerebro/regras.py": "a tabela de regras foi desligada (ninguém a usa)",
    "config/regras.toml": "a tabela de regras foi desligada (ninguém a usa)",
    "config/comparacao.toml": "a comparação de 14 dias com o Eldorado0 não foi construída",
    "workflows/manutencao.toml": "um workflow interno que nenhum fluxo executa",
    "eldorado/motores/acesso/rotas_alternativas.py": "o Tor, desligado por desenho no plano",
    "eldorado/base/motor_modelo/__init__.py": "o motor modelo não roda (é só modelo)",
}
MAPA = montar()
NOS = {n["id"]: n for n in MAPA["nos"]}


def test_todo_arquivo_do_sistema_esta_no_mapa():
    faltam = [p.as_posix() for p in Path("eldorado").rglob("*.py") if "__pycache__" not in p.parts and p.as_posix() not in NOS]
    faltam += [p.as_posix() for p in Path("eldorado/motores/canal/config").glob("*.toml") if p.as_posix() not in NOS]
    faltam += [b for b in ("dados/biblioteca.db", "dados/cerebro.db") if b not in NOS]
    assert not faltam, faltam
    assert sum(1 for n in NOS.values() if n["componente"].startswith("motor ")) == len(list(Path("eldorado/motores/canal/config").glob("*.toml")))


def test_o_fluxo_real_esta_ligado():
    fluxo = {(a["de"], a["rotulo"]) for a in MAPA["arestas"] if a["tipo"] == "fluxo"}
    for n in tomllib.loads(Path("workflows/passagem.toml").read_text(encoding="utf-8"))["no"]:
        assert ("workflows/passagem.toml", n["id"]) in fluxo, n["id"]
    assert any(a["tipo"] == "aciona" and a["de"] == ".github/workflows/eldorado.yml" for a in MAPA["arestas"])
    assert any(a["tipo"] == "grava" and a["para"] == "dados/biblioteca.db" for a in MAPA["arestas"])


def test_nenhum_arquivo_fora_do_funcionamento_sem_decisao():
    fora = {p for p, n in NOS.items() if not n["alcancado"] and p != "eldorado/base/cerebro/mapa_arquivos.py"}
    assert fora <= set(PARADOS), f"arquivo fora do funcionamento sem decisão da titular: {sorted(fora - set(PARADOS))}"


def test_nenhum_no_da_passagem_sem_ligacao():
    """24/10/2026: seis nós acrescentados ficaram sem ligação e rodavam no começo, fora da ordem do fluxo."""
    d = tomllib.loads(Path("workflows/passagem.toml").read_text(encoding="utf-8"))
    ligados = {x for c in d["conexao"] for x in (c["de"], c["para"])}
    assert not [n["id"] for n in d["no"] if n["id"] not in ligados]
