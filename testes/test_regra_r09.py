"""A regra R09 (titular, 25/10/2026): o painel inteiro a cada mudança e a cada 15 min (a sala no menor tempo possível);
toda mudança no sistema o para, implanta e religa, atualizando tudo naquele momento."""
import re
from pathlib import Path

import yaml


def _wf(nome):
    return yaml.safe_load(Path(f".github/workflows/{nome}").read_text(encoding="utf-8"))


def test_o_painel_a_cada_mudanca_e_a_cada_15_minutos():
    p = _wf("painel.yml")
    gatilhos = p.get("on") or p.get(True)
    assert "push" in gatilhos and "workflow_dispatch" in gatilhos and "workflow_run" in gatilhos
    assert any(c["cron"].startswith("*/15") for c in gatilhos["schedule"])
    assert p["concurrency"]["cancel-in-progress"] is False                         # uma republicação não cancela a outra
    texto = Path(".github/workflows/painel.yml").read_text(encoding="utf-8")
    assert re.search(r"eldorado aplicar \|\|", texto)                                 # um evento recusado não deixa o site velho
    assert "--gravar-min 5" in Path(".github/workflows/eldorado.yml").read_text(encoding="utf-8")     # a sala: a cada 5 min
    assert "painel.yml/dispatches" in Path("scripts/gravar.sh").read_text(encoding="utf-8")         # cada gravação aciona o painel


def test_toda_mudanca_para_implanta_e_religa():
    i = _wf("implantar.yml")
    gatilhos = i.get("on") or i.get(True)
    assert "eldorado/**" in gatilhos["push"]["paths"] and "config/**" in gatilhos["push"]["paths"]
    texto = Path(".github/workflows/implantar.yml").read_text(encoding="utf-8")
    assert "gh run cancel" in texto and "gh workflow run eldorado.yml" in texto and "implantar/pedido.txt" in texto
    assert i["concurrency"]["cancel-in-progress"] is False                              # uma implantação nunca cancela a outra
    assert "gh workflow run painel.yml" in texto                                         # o painel republicado depois de cada implantação
    passos = [s_.get("name", "") for s_ in i["jobs"]["implantar"]["steps"]]
    assert passos.index("1. Parar o ciclo na hora") < passos.index("3. Religar com o código novo")   # para NA HORA (sem esperar a passagem)
    e = yaml.safe_load(Path(".github/workflows/eldorado.yml").read_text(encoding="utf-8"))
    cont = next(s_ for s_ in e["jobs"][next(iter(e["jobs"]))]["steps"] if s_.get("name", "").startswith("Continuar"))
    assert "cancelled" in cont["if"]                                                     # interrompido, quem religa é o Implantar
    comandos = Path("eldorado/base/nucleo/comandos.py").read_text(encoding="utf-8")
    assert "implantar/pedido.txt" in comandos and "implantar.is_set()" in comandos     # termina a passagem e para (sem cortar)


def test_o_radar_nao_repete_livro_nem_mostra_unido():
    fonte = Path("eldorado/base/painel/dados.py").read_text(encoding="utf-8")
    assert "situacao NOT IN ('excluido', 'unido')" in fonte


def test_a_gravacao_nao_muda_o_ciclo_em_andamento():
    """25/10/2026: o 'git pull' da gravação trazia o código e as configurações novas para o ciclo em andamento (o nó do
    Espião falhou com a configuração nova lida pelo código antigo). A gravação usa uma árvore de trabalho separada."""
    g = Path("scripts/gravar.sh").read_text(encoding="utf-8")
    assert "git worktree add" in g and "git pull -q" not in g and "push -q origin HEAD:main" in g and ".inicio_ciclo" in g
