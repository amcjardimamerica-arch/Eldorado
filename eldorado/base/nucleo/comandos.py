"""Os comandos da plataforma: os mesmos no GitHub, no computador da titular e (depois) no painel.

Códigos de saída: 0 deu certo · 1 falhou · 75 adiado (sistema pausado ou sem folga na máquina).
"""
from __future__ import annotations

import json
import sqlite3
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
APRENDIZADO = typer.Option(None, help="APRENDIZADO-ELDORADO.json (o aprendizado dos motores)")


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
def migrar(origem: Path, config: Path = CONFIG, lote: int = 500, aprendizado: Optional[Path] = APRENDIZADO):
    """Importa o Eldorado0 (cópia local do repositório) e confere as contagens. Sai com erro se algo divergir."""
    from itertools import chain

    from ..migracao.importar_eldorado0 import Importador, amostra, conferir, lotes
    from ..migracao.importar_eldorado0 import aprendizado as aprendizado_motores
    _, dados, _ = _cfg(config)
    bancos = abrir_bancos(dados)
    try:
        imp = Importador(origem)
        g = Gravador(bancos)
        aplicados = recusados = 0
        fluxo = chain(imp.eventos(), aprendizado_motores(imp, aprendizado) if aprendizado else [])
        for grupo in lotes(fluxo, lote):
            r = g.aplicar(grupo)
            aplicados, recusados = aplicados + r.aplicados, recusados + len(r.recusados)
        typer.echo(f"eventos aplicados: {aplicados} · recusados: {recusados}")
        tabela = conferir(imp, bancos)
        for q, a, c, ok in tabela:
            typer.echo(f"  {'ok ' if ok else 'DIVERGE'} {q}: origem {a} · banco {c}")
        am = amostra(origem, bancos)
        typer.echo(f"  amostra campo a campo: {sum(ok for _, _, ok in am)} de {len(am)} livros iguais")
        for tipo, n in imp.r.lacunas.items():
            typer.echo(f"  lacuna: {tipo}: {n} (ex.: {', '.join(imp.r.exemplos_lacuna.get(tipo, [])[:3])})")
    finally:
        for c in bancos.values():
            c.close()
    raise typer.Exit(0 if recusados == 0 and all(ok for *_, ok in tabela) and all(ok for *_, ok in am) else 1)


@app.command()
def expurgar(motivo: str, config: Path = CONFIG, validacao: bool = typer.Option(False, "--validacao", help="os livros que a validação marcou como expurgados"),
             livro: Optional[list[str]] = None):
    """ANÁLISE EXTERNA: apaga fisicamente livros e tudo o que depende deles, com o registro do expurgo (a automação não apaga)."""
    from .expurgo_externo import expurgar as _expurgar
    _, dados, _ = _cfg(config)
    b = abrir_bancos(dados)
    try:
        ids = list(livro or [])
        if validacao:
            ids += [r[0] for r in b["biblioteca"].execute("SELECT livro_id FROM livro_dados WHERE validacao='expurgado'")]
        r = _expurgar(b["biblioteca"], b["cerebro"], sorted(set(ids)), motivo)
        typer.echo(f"expurgados {r['livros']} livro(s) · {r['linhas']} linha(s): {json.dumps(r['por_tabela'], ensure_ascii=False)}")
        for c in b.values():
            c.execute("VACUUM")
    finally:
        for c in b.values():
            c.close()


@app.command()
def fechar(config: Path = CONFIG):
    """Consolida os bancos (o arquivo auxiliar de escrita volta para o banco) antes de gravar no Git."""
    _, dados, _ = _cfg(config)
    for p in sorted(Path(dados).rglob("*.db")):
        con = sqlite3.connect(p)
        try:
            con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            con.execute("PRAGMA optimize")
            ok = con.execute("PRAGMA integrity_check").fetchone()[0]
        finally:
            con.close()
        if ok != "ok":
            typer.echo(f"{p}: integridade {ok}", err=True)
            raise typer.Exit(1)
        typer.echo(f"{p}: consolidado ({p.stat().st_size / 1e6:.1f} MB)")


@app.command()
def sondar(urls: list[str], anotar: bool = typer.Option(False, "--anotar", help="publica cada resultado como anotação do GitHub")):
    """ANÁLISE EXTERNA: acessa endereços pela escada (API e assinatura de navegador) e mostra o status e o começo da resposta."""
    from ...motores.acesso.api import DegrauAPI
    from ...motores.acesso.escada import Bloqueado, Escada
    from ...motores.acesso.leve import DegrauLeve
    escada = Escada([DegrauAPI(), DegrauLeve()], intervalo_padrao=0.5, tentativas=1, tempo_limite=25)
    for url in urls:
        try:
            r = escada.buscar(url)
            texto = r.conteudo[:400].decode("utf-8", errors="replace").replace("\n", " ")
            linha = f"{r.status} · {len(r.conteudo)} bytes · {r.tipo} · degrau {r.degrau[:1]} · {texto}"
        except Bloqueado as e:
            linha = f"FALHOU · {str(e)[:400]}"
        except Exception as e:  # noqa: BLE001 — a sondagem relata qualquer falha, sem parar as outras
            linha = f"ERRO · {type(e).__name__}: {str(e)[:300]}"
        typer.echo(f"{url}\n   {linha}")
        if anotar:
            typer.echo(f"::notice title={url[:120]}::{linha.replace(chr(37), ' por cento')[:900]}")


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
