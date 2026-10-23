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
def painel(config: Path = CONFIG, saida: Path = Path("docs")):
    """Gera o painel (a página e os dados das visões) na pasta publicada pelo GitHub Pages."""
    from ..painel.visoes import publicar
    _, dados, _ = _cfg(config)
    r = publicar(dados, saida, config.parent)
    typer.echo(f"painel gerado em {saida}: {r['livros']} livros, {r['abertas']} abertas, dados com {r['bytes'] / 1e6:.1f} MB")


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
def lote(config: Path = CONFIG, saida: Path = Path("verificacao/lotes")):
    """ETAPA 5: gera o lote da análise externa (os livros na etapa 5, para o Claude no Chrome)."""
    import json
    import sqlite3
    from datetime import date

    from ..cartorio.analise_externa import gerar_lote
    _, dados, _ = _cfg(config)
    con = sqlite3.connect(f"file:{dados / 'biblioteca.db'}?mode=ro", uri=True)
    lt = gerar_lote(con, date.today())
    con.close()
    saida.mkdir(parents=True, exist_ok=True)
    (saida / f"{lt['lote']}.json").write_text(json.dumps(lt, ensure_ascii=False, indent=1), encoding="utf-8")
    typer.echo(f"{saida / (lt['lote'] + '.json')}: {len(lt['livros'])} livro(s)")


@app.command()
def vereditos(arquivo: Path, config: Path = CONFIG):
    """ETAPA 5: importa o veredito do Claude no Chrome (o Cartório valida e armazena; o livro segue na linha)."""
    import sqlite3

    from ..cartorio.analise_externa import importar
    from .eventos import Diario
    c, dados, eventos = _cfg(config)
    diario = Diario(eventos, "analise-externa")
    con = sqlite3.connect(f"file:{dados / 'biblioteca.db'}?mode=ro", uri=True)
    r = importar(arquivo.read_bytes(), con, diario)
    con.close()
    for x in r:
        typer.echo(f"  {x}")
    typer.echo("aplique com: eldorado aplicar")


@app.command()
def inventario(raiz: Path = Path(".")):
    """Gera o inventário do sistema: o catálogo da medição (config/arquivos.json) e o mapa legível (MAPA-DO-SISTEMA.md)."""
    import collections
    import json

    from ..cerebro.inventario import gerar, mapa
    cat = gerar(raiz)
    (raiz / "config/arquivos.json").write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding="utf-8")
    (raiz / "MAPA-DO-SISTEMA.md").write_text(mapa(cat), encoding="utf-8")
    typer.echo(f"{len(cat['arquivos'])} arquivos: {dict(collections.Counter(a['situacao'][:22] for a in cat['arquivos']))}")
    typer.echo(f"{len(cat['motores'])} motores: {dict(collections.Counter((m['tipo'], m['situacao']) for m in cat['motores']))}")


@app.command()
def missao(config: Path = CONFIG, quantas: int = 1, anotar: bool = typer.Option(False, "--anotar")):
    """PILOTOS: uma missão real do Espião (busca, descarte, leitura e filtro), sem gravar na Biblioteca."""
    import sqlite3
    import tempfile

    from ...motores.acesso.api import DegrauAPI
    from ...motores.acesso.escada import Escada
    from ...motores.acesso.leve import DegrauLeve
    from ..cerebro.pilotos import missoes
    _, dados, _ = _cfg(config)
    con = sqlite3.connect(f"file:{dados / 'biblioteca.db'}?mode=ro", uri=True) if (dados / "biblioteca.db").exists() else sqlite3.connect(":memory:")
    escada = Escada([DegrauAPI(), DegrauLeve()], intervalo_padrao=1.0, tentativas=1, tempo_limite=25)
    with tempfile.TemporaryDirectory() as tmp:
        achados, rel = missoes(Path(tmp), con, escada, ociosidade=True, orcamento_s=600)
    for m in rel.get("missoes", [])[:quantas]:
        linha = f"família {m['familia']} · consulta «{m['consulta']}» · {m['resultados']} resultados · {m['achados']} achado(s) · descartes {m['motivos']}"
        typer.echo(linha)
        if anotar:
            typer.echo(f"::notice title=Missão do Espião::{linha[:900]}")
    for a in achados:
        typer.echo(f"  achado: {a.titulo[:90]} <{a.link_divulgacao}>")
        if anotar:
            typer.echo(f"::notice title=Achado do Espião::{a.titulo[:200]} <{a.link_divulgacao}>")


motor_app = typer.Typer(help="Criar motores pela orientação de design (eldorado/motores/skills/criar-motor/SKILL.md).")
app.add_typer(motor_app, name="motor")


@motor_app.command("ficha")
def motor_ficha(id: str):
    """O que o estudo definiu para o motor e o aprendizado do Eldorado0 (só para aprender)."""
    from ...motores.canal.fabrica import ficha
    typer.echo(ficha(id))


@motor_app.command("criar")
def motor_criar(id: str):
    """O esqueleto da configuração, com a identidade, os alvos, o aprendizado e a métrica preenchidos."""
    from ...motores.canal.fabrica import criar
    typer.echo(f"criado: {criar(id)} — decida as rotas pela sondagem e valide com: eldorado motor validar {id}")


@motor_app.command("validar")
def motor_validar(id: str):
    """O que a orientação exige: aceito pelo registro, conforme o estudo, duas rotas, os alvos do estudo e métrica."""
    from ...motores.canal.fabrica import validar
    r = validar(id)
    for nome, ok, det in r:
        typer.echo(f"  {'✓' if ok else '✗'} {nome}: {det}")
    raise typer.Exit(0 if all(ok for _, ok, _ in r) else 1)


@motor_app.command("sondar")
def motor_sondar(id: str, anotar: bool = typer.Option(False, "--anotar")):
    """Sonda todas as rotas do motor (fontes, alvos e documentos do programa); precisa de internet."""
    from ...motores.canal.fabrica import enderecos
    sondar(enderecos(id), anotar)


@app.command()
def permanente(workflow: Path = Path("workflows/passagem.toml"), config: Path = CONFIG,
               limite_min: float = typer.Option(320, help="duração desta execução; perto do limite, grava e passa a vez à continuação"),
               gravar_min: float = typer.Option(30, help="grava o trabalho no repositório a cada tantos minutos"),
               espera_max_min: float = typer.Option(15, help="sem fila, olha de novo no máximo a cada tantos minutos"),
               gravar: bool = typer.Option(True, help="gravar no repositório (desligue fora do GitHub)")):
    """FUNCIONAMENTO PERMANENTE (titular, 22/10/2026): sem horário de trabalho e descanso. Uma passagem depois da outra
    enquanto houver fila; sem fila, espera só até a próxima ação prevista pelo Cérebro e volta."""
    import os
    import subprocess
    import time
    from datetime import datetime, timezone

    from ..cerebro.fila import fila_do_sistema
    _, dados, _ = _cfg(config)
    inicio = ultimo = time.monotonic()
    ciclo = 0

    def gravar_agora() -> None:
        if gravar:
            r = subprocess.run(["bash", "scripts/gravar.sh", "false"], capture_output=True, text=True)
            typer.echo(f"  gravação: {(r.stdout or r.stderr).strip()[-200:] or 'ok'}")

    while True:
        ciclo += 1
        try:
            _rodar(workflow, config, None, None, "leve")
        except typer.Exit as e:
            if e.exit_code not in (0, None):
                typer.echo(f"ciclo {ciclo}: a passagem terminou com o código {e.exit_code}; o sistema segue")
        except Exception as e:  # noqa: BLE001 — o funcionamento é permanente: a falha de um ciclo vira registro e pausa curta
            typer.echo(f"ciclo {ciclo}: falha {type(e).__name__}: {str(e)[:300]}")
            time.sleep(60)
        os.environ.pop("ELDORADO_FORCAR", None)                     # acionar todos vale só para o primeiro ciclo
        f = fila_do_sistema(dados, config.parent)
        decorrido = time.monotonic() - inicio
        typer.echo(f"ciclo {ciclo} · {datetime.now(timezone.utc):%H:%M} UTC · motores devidos {len(f['motores_devidos'])} · "
                   f"livros em trabalho {f['livros_em_trabalho']} · próxima ação prevista {f['proxima_acao'][11:16]}")
        if decorrido > limite_min * 60:
            break
        if time.monotonic() - ultimo > gravar_min * 60:
            gravar_agora()
            ultimo = time.monotonic()
        if not f["total"]:
            espera = min(f["proxima_s"], espera_max_min * 60, max(0.0, limite_min * 60 - decorrido))
            typer.echo(f"  sem fila: espera {espera / 60:.0f} min (até a próxima ação prevista)")
            time.sleep(espera)
    typer.echo(f"fim desta execução depois de {ciclo} ciclo(s); a continuação segue o trabalho")


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
