"""Os comandos da plataforma: os mesmos no GitHub, no computador da titular e (depois) no painel.

Códigos de saída: 0 deu certo · 1 falhou · 75 adiado (sistema pausado ou sem folga na máquina).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import typer

from ..cerebro.governador import Governador, medidor_psutil, tamanho
from ..fluxo import agenda as agenda_mod
from ..fluxo import definicao
from ..fluxo.executor import Executor
from ..fluxo.fila import Fila
from ..fluxo.nos import abrir_bancos
from .config import carregar as carregar_config
from .eventos import ler
from .gravador import Gravador

app = typer.Typer(help="Eldorado: comandos da plataforma.", no_args_is_help=True, add_completion=False)
ADIADO = 75


def _cfg(config: Path):
    c = carregar_config(config)
    raiz = config.parent.parent if config.parent.name == "config" else Path(".")
    return c, (raiz / c.caminhos.dados), (raiz / c.caminhos.eventos)


CONFIG = typer.Option(Path("config/eldorado.toml"), "--config", help="Arquivo de configuração")
AGENDA = typer.Option(Path("config/agenda.toml"), help="Agenda dos módulos")
AGORA = typer.Option(None, help="Data e hora ISO com fuso (padrão: agora)")


@app.command()
def iniciar(config: Path = CONFIG):
    """Cria (ou confere) os três bancos."""
    _, dados, eventos = _cfg(config)
    eventos.mkdir(parents=True, exist_ok=True)
    bancos = abrir_bancos(dados)
    for nome, con in bancos.items():
        v = con.execute("PRAGMA user_version").fetchone()[0]
        ok = con.execute("PRAGMA integrity_check").fetchone()[0]
        typer.echo(f"{nome}: versão {v}, integridade {ok}")
        con.close()


@app.command()
def aplicar(config: Path = CONFIG):
    """Aplica aos bancos os eventos pendentes (idempotente)."""
    _, dados, eventos = _cfg(config)
    bancos = abrir_bancos(dados)
    try:
        r = Gravador(bancos).aplicar(ler(eventos))
    finally:
        for c in bancos.values():
            c.close()
    typer.echo(f"aplicados {r.aplicados} · repetidos {r.repetidos} · recusados {len(r.recusados)}")
    for ev, tipo, motivo in r.recusados[:20]:
        typer.echo(f"  recusado {tipo} ({ev}): {motivo}")
    raise typer.Exit(1 if r.recusados else 0)


def _rodar(workflow: Path, config: Path, entrada: Optional[str], execucao: Optional[str], peso: str):
    _, dados, eventos = _cfg(config)
    if (dados / "PAUSADO").exists():
        typer.echo("sistema pausado: nada foi executado")
        raise typer.Exit(ADIADO)
    g = Governador(medidor_psutil(str(dados if dados.exists() else ".")))
    if not g.pode_iniciar(peso=peso):
        typer.echo(f"adiado: {g.motivo()}")
        raise typer.Exit(ADIADO)
    d = definicao.carregar(workflow)
    r = Executor(d, eventos).executar(json.loads(entrada) if entrada else None, execucao)
    typer.echo(json.dumps({"execucao": r.execucao, "estado": r.estado, "erro": r.erro, "reagendar_em_s": r.reagendar_em_s}, ensure_ascii=False))
    if r.estado == "reagendada":
        typer.echo(f"retomar depois de {int(r.reagendar_em_s or 0)} s: eldorado retomar {workflow} {r.execucao}")
    raise typer.Exit(1 if r.estado == "falhou" else 0)


@app.command()
def executar(workflow: Path, entrada: Optional[str] = typer.Option(None, help="Itens de entrada, em JSON"), config: Path = CONFIG,
             peso: str = typer.Option("leve", help="leve ou pesado")):
    """Executa um workflow."""
    _rodar(workflow, config, entrada, None, peso)


@app.command()
def retomar(workflow: Path, execucao: str, config: Path = CONFIG):
    """Retoma uma execução interrompida ou reagendada, do passo em que parou."""
    _rodar(workflow, config, None, execucao, "leve")


@app.command()
def maquina(config: Path = CONFIG):
    """Mostra o uso da máquina, a folga até 85% e o tamanho de cada parte."""
    c, dados, eventos = _cfg(config)
    g = Governador(medidor_psutil(str(dados if dados.exists() else ".")), limite=c.limites.carga_maxima)
    leitura = g.ler()
    typer.echo(f"processador {leitura.processador:.0%} · memória {leitura.memoria:.0%} · disco {leitura.disco:.0%} · carga {leitura.carga:.0%} "
               f"(limite {g.limite:.0%}) · paralelismo permitido {g.paralelismo()}")
    for parte, p in (("biblioteca", dados / "biblioteca.db"), ("especial", dados / "especial.db"), ("cerebro", dados / "cerebro.db"), ("eventos", eventos)):
        typer.echo(f"  {parte}: {tamanho(p) / 1e6:.2f} MB")


@app.command()
def devidos(agora: Optional[str] = AGORA, arquivo: Path = AGENDA):
    """Lista os módulos devidos agora."""
    quando = datetime.fromisoformat(agora) if agora else datetime.now(timezone.utc)
    for d in agenda_mod.carregar(arquivo).devidos(quando):
        typer.echo(f"{d.modulo}: janela {d.janela_inicio} a {d.janela_fim} ({d.motivo})")


@app.command()
def pausar(config: Path = CONFIG):
    """Pausa o sistema: nada novo começa até despausar."""
    _, dados, _ = _cfg(config)
    dados.mkdir(parents=True, exist_ok=True)
    (dados / "PAUSADO").write_text(datetime.now(timezone.utc).isoformat())
    typer.echo("sistema pausado")


@app.command()
def despausar(config: Path = CONFIG):
    """Retira a pausa."""
    _, dados, _ = _cfg(config)
    (dados / "PAUSADO").unlink(missing_ok=True)
    typer.echo("sistema despausado")


@app.command()
def trabalhar(config: Path = CONFIG, trabalhadores: int = typer.Option(0, help="0 = o governador decide")):
    """Roda o consumidor da fila, sob o governador e a pausa."""
    c, dados, eventos = _cfg(config)
    g = Governador(medidor_psutil(str(dados if dados.exists() else ".")), limite=c.limites.carga_maxima)
    fila = Fila(dados / "fila.db", eventos, g, dados / "PAUSADO")
    n = trabalhadores or max(1, g.paralelismo())
    typer.echo(f"consumidor da fila com {n} trabalhador(es)")
    fila.huey.create_consumer(workers=n, periodic=True).run()


if __name__ == "__main__":
    app()
