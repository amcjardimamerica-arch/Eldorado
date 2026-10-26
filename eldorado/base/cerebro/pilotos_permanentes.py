"""Os pilotos de forma permanente (titular, 25/10/2026: "execute eles de forma permanente, da forma que foram desenvolvidos
para funcionar").

Como foram desenvolvidos (o Eldorado0 e o plano): voos contínuos e independentes — o Interceptador consumindo a fila
livro após livro, sem parar; o Espião fazendo missões em sequência, com o descanso das rotas. Como rodavam: nós dentro da
passagem, depois da coleta e do Cartório, com 5 e 3 minutos de orçamento (poucos minutos por passagem, e nada quando a
passagem era interrompida antes deles).

Agora os dois voam em segundo plano durante todo o ciclo (o funcionamento permanente os liga). O que trazem fica na fila
de entrega; os nós deles, na passagem seguinte, entregam o que os voos trouxeram à Pertinência e ao Cartório. A carga
do servidor é respeitada (acima de 90% de memória, esperam). Falha de um voo vira registro; o voo seguinte segue (R18).
"""
from __future__ import annotations

import queue
import threading
import time
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from typing import Any

ATIVO = threading.Event()                      # os voos permanentes estão ligados (os nós só entregam)
ENTREGAS: dict[str, queue.Queue] = {"interceptador": queue.Queue(), "espiao": queue.Queue()}
SITUACAO: dict[str, dict[str, Any]] = {"interceptador": {}, "espiao": {}}


def entregas(piloto: str) -> list[dict[str, Any]]:
    """O que os voos trouxeram desde a última passagem (o nó do piloto devolve isto)."""
    saida = []
    while True:
        try:
            saida.append(ENTREGAS[piloto].get_nowait())
        except queue.Empty:
            return saida


def sinal(diario, piloto: str, motivo: str) -> None:
    """O sinal de vida do piloto (25/10/2026): os quadros do site leem o "ligado/agora" por ele, não pelo último resultado."""
    diario.emitir("medicao.registrada", f"piloto:{piloto}", {"marcador": f"piloto:{piloto}", "nivel": "componente",
                                                              "em": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()), "ponto": "v",
                                                              "valor": 1, "motivo": motivo[:300]})


def _contexto(dados: Path, diario):
    from .encaminhamento import _contexto_pilotos
    return _contexto_pilotos({"dados": str(dados), "modulos": "config/modulos.toml", "intervalo_s": 1.0}, SimpleNamespace(diario=diario))


PARALELOS_INTERCEPTADOR = 5   # 5 livros em paralelo (titular, 25/10/2026), cada um autorizado pelo Comandante (a carga até 85%)


def _voo_interceptador(dados: Path, eventos: Path, parar: threading.Event, k: int, lv_id: str, base: dict | None, tempo_livro_s: float) -> None:
    """Um voo do Interceptador: o seu diário, a sua conexão com a Biblioteca e a sua vaga da IA."""
    from ...motores.descoberta.metabusca import Metabusca
    from ...motores.pilotos.interceptador import Interceptador, carregar
    from ..comandante.biblioteca import registrar_tentativa
    from ..comandante.pilotos import autorizar, pousou
    from ..nucleo.eventos import Diario
    from ..nucleo.ia import IA
    from .encaminhamento import Encaminhamento
    from .rede import rede_atual
    diario = Diario(eventos, f"interceptador-{k}")
    dados_, con, escada, registro = _contexto(dados, diario)
    try:
        livros = carregar(con, [lv_id])
        if not livros or autorizar("interceptador", dados_, diario, parar, alvo=lv_id, titulo=livros[0].titulo or "") is None:
            return
        ia, rede = IA(cargo_nome="interceptador", vaga=k), rede_atual(dados_)
        mb = Metabusca(buscar=escada.buscar)

        def buscar_links(q: str, mb=mb) -> list[str]:
            try:
                return [p.link for p in mb.consultar(q, limite=10)[0]]
            except Exception:  # noqa: BLE001
                return []
        enc = Encaminhamento(con, diario, registro, Interceptador(con, diario, escada, metabusca=buscar_links, ia=ia if ia.disponivel() else None), rede)
        SITUACAO[f"interceptador-{k}"] = {"livro": lv_id, "titulo": livros[0].titulo, "desde": time.time()}
        sinal(diario, "interceptador", f"em voo ({k + 1} de {PARALELOS_INTERCEPTADOR}): {livros[0].titulo}")
        try:
            _quem, achados = enc.encaminhar(livros[0], time.monotonic() + tempo_livro_s)
            for a in (achados if isinstance(achados, list) else [achados] if achados else []):
                ENTREGAS["interceptador"].put(a)
        finally:
            if base:
                registrar_tentativa(diario, base)       # a tentativa de completar a base (no máximo 2, com 30 minutos entre elas)
            pousou("interceptador")
    finally:
        con.close()


def voar_interceptador(dados: Path, diario, parar: threading.Event, tempo_livro_s: float = 180) -> None:
    """O Interceptador: 5 livros em paralelo, pelo plano de voo, sem parar. A fila: primeiro a de completar a base (as
    abertas incompletas, as recuperáveis, as sem base; 2 tentativas, 30 minutos entre elas); depois a fila de sempre."""
    from concurrent.futures import ThreadPoolExecutor, wait

    from ...motores.pilotos.interceptador import fila
    from ..comandante.biblioteca import avaliar
    from ..comandante.biblioteca import fila as fila_base
    eventos = Path(getattr(diario, "pasta", "eventos"))
    while not parar.is_set():
        try:
            dados_, con, _escada, _registro = _contexto(dados, diario)
            try:
                tem_base = "base_classe" in {r[1] for r in con.execute("PRAGMA table_info(livro_dados)")}
                base = fila_base(avaliar(con)) if tem_base else []
                ids_base = {x["id"] for x in base}
                comuns = [lv.id for lv in fila(con, date.today().isoformat()) if lv.id not in ids_base][:30]
            finally:
                con.close()
            voos = [(x["id"], x) for x in base] + [(i, None) for i in comuns]
            if not voos:
                sinal(diario, "interceptador", "aguardando: a fila de livros está vazia")
                parar.wait(300)
                continue
            livres = list(range(PARALELOS_INTERCEPTADOR))
            with ThreadPoolExecutor(max_workers=PARALELOS_INTERCEPTADOR) as pool:
                em_voo: dict = {}
                for lv_id, b in voos:
                    if parar.is_set():
                        break
                    while not livres:
                        feitos, _ = wait(list(em_voo), return_when="FIRST_COMPLETED")
                        for f in feitos:
                            livres.append(em_voo.pop(f))
                    k = livres.pop(0)
                    em_voo[pool.submit(_voo_interceptador, dados, eventos, parar, k, lv_id, b, tempo_livro_s)] = k
                wait(list(em_voo))
        except Exception as e:  # noqa: BLE001 — uma volta que falha vira registro; a seguinte segue
            diario.emitir("alarme.aberto", "piloto:interceptador", {"gravidade": "media", "modulo": "piloto:interceptador",
                                                                    "mensagem": f"a volta do Interceptador falhou: {type(e).__name__}: {str(e)[:200]}",
                                                                    "aberto_em": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())})
            parar.wait(60)


def voar_espiao(dados: Path, diario, parar: threading.Event, orcamento_s: float = 150) -> None:
    """O Espião: missão após missão (as rotas descansam sozinhas quando falham), com uma pausa entre os voos."""
    from ..comandante.pilotos import autorizar, pousou
    from .encaminhamento import Encaminhamento
    from .pilotos import missoes
    while not parar.is_set():
        try:
            aut = autorizar("espiao", dados, diario, parar)                 # as quatro regras do Comandante (25/10/2026)
            if aut is None:
                if not parar.is_set():
                    sinal(diario, "espiao", "aguardando: sem janela de busca (as rotas descansando)")
                    parar.wait(60)
                continue
            dados_, con, escada, registro = _contexto(dados, diario)
            try:
                SITUACAO["espiao"] = {"desde": time.time()}
                sinal(diario, "espiao", f"em voo: a família {aut['alvo']} (autorizada pelo Comandante)")
                achados, _ = missoes(dados_, con, escada, True, orcamento_s, diario=diario, familia=aut["alvo"])
                enc = Encaminhamento(con, diario, registro, None)
                for a in achados:
                    ENTREGAS["espiao"].put(enc._entregar(a, "espiao"))
                sinal(diario, "espiao", f"pousou: {len(achados)} achado(s)")
            finally:
                con.close()
                pousou("espiao")
        except Exception as e:  # noqa: BLE001
            diario.emitir("alarme.aberto", "piloto:espiao", {"gravidade": "media", "modulo": "piloto:espiao",
                                                             "mensagem": f"o voo permanente do Espião falhou: {type(e).__name__}: {str(e)[:300]}",
                                                             "aberto_em": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())})
            parar.wait(60)                                                # um voo que falhou: um minuto antes do próximo


def conferir_sempre(dados: Path, diario, parar: threading.Event) -> None:
    """O Comandante confere, a cada minuto, as mudanças feitas em funcionamento há 20 minutos (a regra da titular)."""
    import sqlite3

    from ..comandante.parametros import conferir
    while not parar.wait(60):
        try:
            cer = sqlite3.connect(f"file:{dados / 'cerebro.db'}?mode=ro", uri=True)
            try:
                if cer.execute("SELECT 1 FROM sqlite_master WHERE name = 'conferencia'").fetchone():
                    conferir(cer, diario)
            finally:
                cer.close()
        except Exception:  # noqa: BLE001 — a conferência seguinte tenta de novo
            pass


def ligar(dados: Path, eventos: Path, parar: threading.Event) -> list[threading.Thread]:
    """Liga os dois voos permanentes (o funcionamento permanente chama no início do ciclo)."""
    from ..nucleo.eventos import Diario
    ATIVO.set()
    fios = [threading.Thread(target=voar_interceptador, args=(dados, Diario(eventos, "interceptador"), parar), daemon=True, name="interceptador"),
            threading.Thread(target=voar_espiao, args=(dados, Diario(eventos, "espiao"), parar), daemon=True, name="espiao"),
            threading.Thread(target=conferir_sempre, args=(dados, Diario(eventos, "comandante"), parar), daemon=True, name="comandante")]
    for f in fios:
        f.start()
    return fios
