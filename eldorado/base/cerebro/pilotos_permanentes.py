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


PASTA_ENTREGAS = Path("dados/pilotos")   # 27/10/2026: os achados dos pilotos num arquivo; a passagem cortada não os perde
_TRAVA_ENTREGAS = threading.Lock()


def entregar(piloto: str, achado: Any) -> None:
    """O achado do voo: na fila e no arquivo do piloto (sobrevive à passagem cortada e ao reinício do processo)."""
    import json as _json
    ENTREGAS[piloto].put(achado)
    try:
        import msgspec
        linha = _json.dumps(msgspec.to_builtins(achado), ensure_ascii=False)
    except Exception:  # noqa: BLE001
        return
    with _TRAVA_ENTREGAS:
        PASTA_ENTREGAS.mkdir(parents=True, exist_ok=True)
        with open(PASTA_ENTREGAS / f"{piloto}.jsonl", "a", encoding="utf-8") as f:
            f.write(linha + "\n")


def entregas(piloto: str) -> list[dict[str, Any]]:
    """O que os voos trouxeram desde a última passagem (o nó do piloto devolve isto): a fila e, se a fila se perdeu (a
    passagem cortada, o processo reiniciado), o arquivo. O arquivo é esvaziado na entrega."""
    import json as _json
    saida = []
    while True:
        try:
            saida.append(ENTREGAS[piloto].get_nowait())
        except queue.Empty:
            break
    arq = PASTA_ENTREGAS / f"{piloto}.jsonl"
    with _TRAVA_ENTREGAS:
        if arq.exists():
            linhas = [ln for ln in arq.read_text(encoding="utf-8").splitlines() if ln.strip()]
            arq.unlink()
            if len(linhas) > len(saida):                   # a fila se perdeu: o arquivo tem tudo
                try:
                    import msgspec

                    from ..nucleo.contratos import Achado
                    saida = [msgspec.convert(_json.loads(ln), Achado) for ln in linhas]
                except Exception:  # noqa: BLE001 — o arquivo ilegível não derruba a passagem
                    pass
    return saida


def sinal(diario, piloto: str, motivo: str) -> None:
    """O sinal de vida do piloto (25/10/2026): os quadros do site leem o "ligado/agora" por ele, não pelo último resultado."""
    diario.emitir("medicao.registrada", f"piloto:{piloto}", {"marcador": f"piloto:{piloto}", "nivel": "componente",
                                                              "em": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()), "ponto": "v",
                                                              "valor": 1, "motivo": motivo[:300]})


def _contexto(dados: Path, diario):
    from .encaminhamento import _contexto_pilotos
    return _contexto_pilotos({"dados": str(dados), "modulos": "config/modulos.toml", "intervalo_s": 1.0}, SimpleNamespace(diario=diario))


PARALELOS_INTERCEPTADOR = 5   # o máximo; o uso normal é 1, e a ociosidade da máquina libera até 5 (titular, 27/10/2026)


class _Vaga:
    """Um dos 5 voos do Interceptador, com o SEU contexto reaproveitado de livro em livro (26/10/2026: criar o contexto
    inteiro a cada livro fazia a memória subir ~12% por hora até 96%, e a regra dos 85% parou o sistema por 3 horas);
    renovado a cada 20 livros."""
    RENOVAR = 20

    def __init__(self, dados: Path, eventos: Path, k: int):
        self.dados, self.eventos, self.k, self.feitos, self.ctx = dados, eventos, k, 0, None

    def contexto(self):
        if self.ctx is None or self.feitos >= self.RENOVAR:
            self.fechar()
            from ...motores.descoberta.metabusca import Metabusca
            from ...motores.pilotos.interceptador import Interceptador
            from ..nucleo.eventos import Diario
            from ..nucleo.ia import IA
            from .encaminhamento import Encaminhamento
            from .rede import rede_atual
            diario = Diario(self.eventos, f"interceptador-{self.k}")
            dados_, con, escada, registro = _contexto(self.dados, diario)
            ia = IA(cargo_nome="interceptador", vaga=self.k, tempo_limite=150.0)   # 29/10/2026: 150 s (eram 240: um voo passava de 20 min)
            mb = Metabusca(buscar=escada.buscar)

            def buscar_links(q: str, mb=mb) -> list[str]:
                try:
                    return [p.link for p in mb.consultar(q, limite=10)[0]]
                except Exception:  # noqa: BLE001
                    return []
            enc = Encaminhamento(con, diario, registro, Interceptador(con, diario, escada, metabusca=buscar_links,
                                                                     ia=ia if ia.disponivel() else None), rede_atual(dados_))
            self.ctx, self.feitos = {"diario": diario, "dados": dados_, "con": con, "enc": enc}, 0
        return self.ctx

    def fechar(self) -> None:
        import gc
        if self.ctx:
            try:
                self.ctx["con"].close()
            except Exception:  # noqa: BLE001
                pass
        self.ctx = None
        gc.collect()


def _voo_interceptador(vaga: _Vaga, parar: threading.Event, lv_id: str, base: dict | None, tempo_livro_s: float) -> None:
    """Um voo do Interceptador, no contexto da sua vaga."""
    from ...motores.pilotos.interceptador import carregar
    from ..comandante.biblioteca import registrar_tentativa
    from ..comandante.pilotos import autorizar, pousou
    c = vaga.contexto()
    livros = carregar(c["con"], [lv_id])
    if not livros or autorizar("interceptador", c["dados"], c["diario"], parar, alvo=lv_id, titulo=livros[0].titulo or "") is None:
        return
    SITUACAO[f"interceptador-{vaga.k}"] = {"livro": lv_id, "titulo": livros[0].titulo, "desde": time.time()}
    sinal(c["diario"], "interceptador", f"em voo ({vaga.k + 1} de {PARALELOS_INTERCEPTADOR}): {livros[0].titulo}")
    try:
        if base:                                          # o pré-voo da base: o site oficial e a esfera, sem a IA (26/10/2026)
            from ..comandante.biblioteca import prevoo

            completado = prevoo(c["diario"], c["enc"].interceptador, livros[0], base)
            if completado and set(completado) >= set(base["buscar"]):
                return                                    # completou sem o plano de voo (a tentativa fica registrada)
        _quem, achados = c["enc"].encaminhar(livros[0], time.monotonic() + tempo_livro_s)
        for a in (achados if isinstance(achados, list) else [achados] if achados else []):
            entregar("interceptador", a)
    finally:
        vaga.feitos += 1
        if base:
            registrar_tentativa(c["diario"], base)       # a tentativa de completar a base (no máximo 2, com 30 minutos entre elas)
        pousou("interceptador")


def paralelos_agora() -> int:
    """Quantos voos o Comandante libera agora: 5; com a memória acima de 85% há mais de 10 minutos, 2 (26/10/2026)."""
    from ..comandante.pilotos import pressao, vagas_por_ociosidade
    return 1 if pressao() >= 600 else min(PARALELOS_INTERCEPTADOR, vagas_por_ociosidade())

def voar_interceptador(dados: Path, diario, parar: threading.Event, tempo_livro_s: float = 180) -> None:
    """O Interceptador: 5 livros em paralelo, pelo plano de voo, sem parar. A fila: primeiro a de completar a base (as
    abertas incompletas, as recuperáveis, as sem base; 2 tentativas, 30 minutos entre elas); depois a fila de sempre.
    26/10/2026: cada vaga tem o SEU fio, fixo (a conexão da vaga com a Biblioteca só pode ser usada no fio que a criou;
    num conjunto de fios a vaga mudava de fio e o voo quebrava em silêncio: só a vaga 1 voava); o erro de um voo vira alarme."""
    import queue

    from ...motores.pilotos.interceptador import fila
    from ..comandante.biblioteca import avaliar
    from ..comandante.biblioteca import fila as fila_base
    eventos = Path(getattr(diario, "pasta", "eventos"))
    pedidos: queue.Queue = queue.Queue()
    avisados: set[str] = set()

    def trabalhador(k: int) -> None:
        vaga = _Vaga(dados, eventos, k)
        while not parar.is_set():
            if k >= paralelos_agora():                       # sob pressão de memória, só as primeiras vagas voam
                parar.wait(30)
                continue
            try:
                lv_id, b = pedidos.get(timeout=5)
            except queue.Empty:
                continue
            try:
                _voo_interceptador(vaga, parar, lv_id, b, tempo_livro_s)
            except Exception as e:  # noqa: BLE001 — o voo que falha vira alarme (uma vez por tipo); a vaga se renova
                tipo = f"{type(e).__name__}: {str(e)[:120]}"
                if tipo not in avisados:
                    avisados.add(tipo)
                    diario.emitir("alarme.aberto", "piloto:interceptador", {"gravidade": "media", "modulo": "piloto:interceptador",
                                                                            "mensagem": f"o voo da vaga {k + 1} falhou: {tipo}",
                                                                            "aberto_em": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())})
                vaga.fechar()
            finally:
                pedidos.task_done()
        vaga.fechar()

    fios = [threading.Thread(target=trabalhador, args=(k,), name=f"interceptador-{k + 1}", daemon=True) for k in range(PARALELOS_INTERCEPTADOR)]
    for f in fios:
        f.start()
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
            for v in voos:
                pedidos.put(v)
            while pedidos.unfinished_tasks and not parar.is_set():   # a volta termina quando as 5 vagas esvaziam a fila
                parar.wait(5)
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
                    entregar("espiao", enc._entregar(a, "espiao"))
                sinal(diario, "espiao", f"pousou: {len(achados)} achado(s)")
                from ..comandante.pilotos import registrar_missao
                registrar_missao(aut["alvo"], len(achados))
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
    from ..comandante.pilotos import carga
    while not parar.wait(60):
        carga()                                                   # a pressão de memória medida a cada minuto (26/10/2026)
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
