"""A escada de acesso: do degrau mais leve ao mais forte, aprendendo por domínio qual degrau funciona.

- Bloqueio reconhecido: 401, 403, 407, 429, 451, 503 com desafio, página de captcha ou de desafio do provedor, e
  página HTML quase vazia. Bloqueio sobe de degrau; erro passageiro (rede, 5xx) repete no mesmo degrau, com espera.
- Sem travas para robôs (titular, 22/10): o robots é só informação; a espera que ele pede vira o intervalo do domínio.
- O intervalo mínimo entre pedidos ao mesmo domínio é respeitado.
- Os degraus pesados (navegadores) só começam com a permissão do governador de carga.
- Cada domínio aprende o degrau que funciona; o próximo pedido começa por ele (evento dominio.aprendido).
"""
from __future__ import annotations

import re
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Protocol
from urllib.parse import urlsplit

from tenacity import Retrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from ...base.nucleo.eventos import Diario, agora

STATUS_BLOQUEIO = {401, 403, 407, 429, 451}
SINAIS_BLOQUEIO = re.compile(rb"(?i)captcha|cf-chl|challenge-platform|just a moment\.\.\.|access denied|acesso negado|attention required|"
                             rb"are you a robot|verify you are human|ddos-guard|incapsula|perimeterx|datadome")


@dataclass
class Resposta:
    url: str
    status: int
    conteudo: bytes
    tipo: str = ""
    degrau: str = ""
    copia_arquivada: bool = False
    alertas: list[str] = field(default_factory=list)


class Bloqueado(Exception):
    """O site recusou este degrau (subir de degrau)."""


class Passageiro(Exception):
    """Erro passageiro (rede, 5xx, tempo esgotado): repetir no mesmo degrau, com espera."""


class Indisponivel(Exception):
    """O degrau não está instalado ou ligado nesta máquina (pular)."""


class Pendente(Exception):
    """O pedido foi entregue a outro executor (o computador da titular) e a resposta virá depois."""


class Degrau(Protocol):
    nome: str
    pesado: bool

    def buscar(self, url: str, tempo_limite: float) -> Resposta: ...


def dominio(url: str) -> str:
    return (urlsplit(url).hostname or "").lower().removeprefix("www.")


def avaliar(r: Resposta) -> None:
    """Levanta Bloqueado ou Passageiro conforme a resposta; nada, se a resposta serve."""
    if r.status in STATUS_BLOQUEIO:
        raise Bloqueado(f"status {r.status}")
    if r.status == 503 and SINAIS_BLOQUEIO.search(r.conteudo[:20000]):
        raise Bloqueado("503 com desafio")
    if r.status >= 500:
        raise Passageiro(f"status {r.status}")
    if r.status >= 400:
        raise Bloqueado(f"status {r.status}")
    amostra = r.conteudo[:20000]
    if SINAIS_BLOQUEIO.search(amostra) and len(r.conteudo) < 200_000:
        raise Bloqueado("página de desafio ou captcha")
    sem_codigo = re.sub(rb"(?is)<(script|style|noscript)\b.*?</\1>", b"", amostra)
    eh_html = "html" in r.tipo or amostra.lstrip()[:15].lower().startswith((b"<!doctype", b"<html"))
    if eh_html and len(re.sub(rb"<[^>]+>|\s+", b"", sem_codigo)) < 40:
        raise Bloqueado("página HTML quase vazia (provável bloqueio ou conteúdo só com JavaScript)")


class Escada:
    def __init__(self, degraus: list[Degrau], diario: Diario | None = None, governador=None, intervalo_padrao: float = 1.0,
                 tentativas: int = 2, aprendido: dict[str, int] | None = None, tempo_limite: float = 30.0, dormir=time.sleep):
        self.degraus, self.diario, self.governador = degraus, diario, governador
        self.intervalo_padrao, self.tentativas, self.tempo_limite, self.dormir = intervalo_padrao, tentativas, tempo_limite, dormir
        self.aprendido: dict[str, int] = dict(aprendido or {})       # domínio → índice do degrau que funcionou
        self.intervalos: dict[str, float] = {}
        self._ultimo: dict[str, float] = {}
        self._trava = threading.Lock()
        self.bloqueios: dict[str, int] = {}

    def definir_intervalo(self, dom: str, segundos: float) -> None:
        self.intervalos[dom] = max(self.intervalos.get(dom, 0.0), segundos)

    def _esperar(self, dom: str) -> None:
        with self._trava:
            falta = self._ultimo.get(dom, 0.0) + self.intervalos.get(dom, self.intervalo_padrao) - time.monotonic()
            if falta > 0:
                self.dormir(falta)
            self._ultimo[dom] = time.monotonic()

    def buscar(self, url: str) -> Resposta:
        dom = dominio(url)
        inicio = self.aprendido.get(dom, 0)
        motivos: list[str] = []
        for i in range(inicio, len(self.degraus)):
            d = self.degraus[i]
            if d.pesado and self.governador is not None and not self.governador.pode_iniciar(f"degrau:{d.nome}", "pesado"):
                motivos.append(f"{d.nome}: adiado pelo governador")
                continue
            try:
                for tentativa in Retrying(stop=stop_after_attempt(self.tentativas), retry=retry_if_exception_type(Passageiro),
                                          wait=wait_exponential(multiplier=0.5, max=8), sleep=self.dormir, reraise=True):
                    with tentativa:
                        self._esperar(dom)
                        r = d.buscar(url, self.tempo_limite)
                        avaliar(r)
            except Bloqueado as e:
                self.bloqueios[dom] = self.bloqueios.get(dom, 0) + 1
                motivos.append(f"{d.nome}: bloqueado ({e})")
                continue
            except (Indisponivel, Passageiro) as e:
                motivos.append(f"{d.nome}: {type(e).__name__.lower()} ({e})")
                continue
            except Pendente:
                self._aprender(dom, i, exige_local=True)
                raise
            r.degrau = d.nome
            r.alertas = motivos + r.alertas
            if self.aprendido.get(dom) != i:
                self._aprender(dom, i)
            return r
        raise Bloqueado(f"{dom}: nenhum degrau conseguiu ({'; '.join(motivos)})")

    def _aprender(self, dom: str, i: int, exige_local: bool = False) -> None:
        self.aprendido[dom] = i
        if self.diario:
            dados = {"dominio": dom, "degrau_que_funciona": i, "bloqueios": self.bloqueios.get(dom, 0), "exige_local": int(exige_local),
                     "ultimo_bloqueio": agora() if self.bloqueios.get(dom) else None}
            self.diario.emitir("dominio.aprendido", "escada", dados)


def ler_robots(escada: Escada, url: str, buscar_texto) -> dict[str, Any]:
    """Lê o robots.txt como informação: a espera pedida vira o intervalo do domínio; nada é bloqueado."""
    from protego import Protego
    base = f"{urlsplit(url).scheme}://{urlsplit(url).netloc}"
    try:
        texto = buscar_texto(f"{base}/robots.txt")
    except Exception:  # noqa: BLE001 — sem robots, segue com o intervalo padrão (é só informação)
        return {"lido": False}
    rp = Protego.parse(texto)
    espera = rp.crawl_delay("Eldorado") or rp.crawl_delay("*")
    if espera:
        escada.definir_intervalo(dominio(url), float(espera))
    return {"lido": True, "espera": espera, "robots_proibiria": not rp.can_fetch(url, "Eldorado")}
