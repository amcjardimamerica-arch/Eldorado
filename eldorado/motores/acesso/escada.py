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
    if r.status in (404, 410):                  # a página não existe: nenhum degrau muda isso (lição do Diário de Goiás, 23/10)
        raise Indisponivel(f"status {r.status}: a página não existe")
    if r.status >= 400:
        raise Bloqueado(f"status {r.status}")
    amostra = r.conteudo[:20000]
    if SINAIS_BLOQUEIO.search(amostra) and len(r.conteudo) < 200_000:
        raise Bloqueado("página de desafio ou captcha")
    # o código executável não conta como conteúdo; os blocos de DADOS (JSON, JSON-LD) contam (lição do DOU, 22/10)
    sem_codigo = re.sub(rb"(?is)<script\b(?![^>]*type=[\"']application/(?:ld\+)?json)[^>]*>.*?</script>|<(style|noscript)\b.*?</\1>", b"", amostra)
    eh_html = "html" in r.tipo or amostra.lstrip()[:15].lower().startswith((b"<!doctype", b"<html"))
    if eh_html and len(re.sub(rb"<[^>]+>|\s+", b"", sem_codigo)) < 40:
        raise Bloqueado("página HTML quase vazia (provável bloqueio ou conteúdo só com JavaScript)")


# 29/10/2026: a identidade canônica dos degraus (o código no início do nome): 1 API, 2 leve, P ponte BR (10), 3 Lightpanda,
# 4 Patchright, 5 Camoufox, 6 Wayback, 7 Tor, 8 leitor público, 9 computador da titular; a ordem é a da escada completa
NOMES_CANONICOS = {1: "API", 2: "requisição leve", 10: "ponte BR", 3: "Lightpanda", 4: "Patchright", 5: "Camoufox", 6: "Wayback",
                   7: "Tor", 8: "leitor público", 9: "computador da titular"}
ORDEM_CANONICA = [1, 2, 10, 3, 4, 5, 6, 7, 8, 9]


def servico_local(url: str) -> bool:
    """O serviço da própria máquina (o SearXNG do fluxo: ELDORADO_SEARXNG, ou o padrão 127.0.0.1:8888): só os degraus
    diretos. Pelo ENDEREÇO com a porta (um servidor local qualquer, como o dos testes, sobe a escada normalmente)."""
    import os

    alvo = {urlsplit(os.environ.get("ELDORADO_SEARXNG") or "").netloc, "127.0.0.1:8888", "localhost:8888"} - {""}
    return urlsplit(url).netloc.lower() in alvo


def codigo(degrau) -> int | None:
    prefixo = str(getattr(degrau, "nome", "")).split("·")[0].strip()
    return 10 if prefixo == "P" else (int(prefixo) if prefixo.isdigit() else None)


def ler_aprendido(dados) -> dict[str, int]:
    """O que a escada já aprendeu (o Cérebro: a tabela dominio), domínio → código canônico do degrau."""
    import sqlite3
    from pathlib import Path

    arq = Path(dados) / "cerebro.db"
    if not arq.exists():
        return {}
    try:
        c = sqlite3.connect(f"file:{arq}?mode=ro", uri=True)
        try:
            return {d: int(g) for d, g in c.execute("SELECT dominio, degrau_que_funciona FROM dominio WHERE degrau_que_funciona IS NOT NULL")}
        finally:
            c.close()
    except sqlite3.Error:
        return {}


# 11/11/2026 (reanálise da Sala): o domínio que terminou a escada inteira «pendente no computador local» era subido de novo,
# degrau por degrau, a cada fonte e a cada acionamento. No site que só abre no Brasil cada degrau esgota o tempo (2 tentativas
# de 30 s): ~7 min por fonte. O motor das prefeituras gastava os 20 min do acionamento em 3 fontes de Luziânia, parava sem ler
# nenhuma, e a Regência o acionava de novo na passagem seguinte («continua o trabalho do dia»): 26 de 30 acionamentos em
# 10/11 (9,2 h do dia), e a passagem em mais de 20 min. Agora a escada lembra a hora em que o domínio terminou pendente:
# por RESUBIR_PENDENTE_H horas, o pedido vai direto ao degrau do computador da titular (a resposta chegou? é lida; não chegou?
# pendente, em milissegundos). Passado o prazo, a escada inteira é tentada de novo (o site pode ter voltado a abrir) — o
# computador da titular continua sem ser o ponto de partida permanente (29/10/2026). O acionamento à mão sobe sempre.
RESUBIR_PENDENTE_H = 6.0


def ler_pendentes(dados) -> dict[str, float]:
    """Os domínios que terminaram a escada pendentes no computador da titular (o Cérebro: a tabela dominio), domínio → a
    hora da última subida inteira (segundos desde a época)."""
    import sqlite3
    from datetime import datetime
    from pathlib import Path

    arq = Path(dados) / "cerebro.db"
    if not arq.exists():
        return {}
    saida: dict[str, float] = {}
    try:
        c = sqlite3.connect(f"file:{arq}?mode=ro", uri=True)
        try:
            for d, quando in c.execute("SELECT dominio, ultimo_bloqueio FROM dominio WHERE exige_local = 1 AND degrau_que_funciona IS NULL "
                                       "AND ultimo_bloqueio IS NOT NULL"):
                try:
                    saida[d] = datetime.fromisoformat(str(quando)).timestamp()
                except ValueError:
                    continue
        finally:
            c.close()
    except sqlite3.Error:
        return {}
    return saida


class Escada:
    def __init__(self, degraus: list[Degrau], diario: Diario | None = None, governador=None, intervalo_padrao: float = 1.0,
                 tentativas: int = 2, aprendido: dict[str, int] | None = None, tempo_limite: float = 30.0, dormir=time.sleep):
        self.degraus, self.diario, self.governador = degraus, diario, governador
        self.intervalo_padrao, self.tentativas, self.tempo_limite, self.dormir = intervalo_padrao, tentativas, tempo_limite, dormir
        self.aprendido: dict[str, int] = dict(aprendido or {})       # domínio → índice do degrau que funcionou
        self.ultimo_degrau: str | None = None
        self.intervalos: dict[str, float] = {}
        self._ultimo: dict[str, float] = {}
        self._trava = threading.Lock()
        self.bloqueios: dict[str, int] = {}
        self.pendente_desde: dict[str, float] = {}                  # 11/11/2026: domínio → a hora da última subida que terminou pendente
        self.relogio = time.time

    def definir_intervalo(self, dom: str, segundos: float) -> None:
        self.intervalos[dom] = max(self.intervalos.get(dom, 0.0), segundos)

    def _esperar(self, dom: str) -> None:
        with self._trava:
            falta = self._ultimo.get(dom, 0.0) + self.intervalos.get(dom, self.intervalo_padrao) - time.monotonic()
            if falta > 0:
                self.dormir(falta)
            self._ultimo[dom] = time.monotonic()

    def buscar(self, url: str, corpo: dict[str, str] | None = None) -> Resposta:
        """corpo: os campos de um formulário (POST); os degraus que não fazem POST são pulados."""
        dom = dominio(url)
        inicio = self.aprendido.get(dom, 0)
        motivos: list[str] = []
        # 29/10/2026: o serviço da própria máquina (o SearXNG em 127.0.0.1) não sobe a escada: só os degraus diretos (a
        # escada levava o SearXNG ao computador da titular, que responde "pendente", e o Espião voltava vazio)
        limite = len(self.degraus)
        if servico_local(url):
            inicio, limite = 0, sum(1 for d in self.degraus if codigo(d) in (1, 2)) or 1
        ordem = list(range(inicio, limite))
        # 05/11/2026 (titular: a ponte BR no canivete de todo motor): o domínio que aprendeu um degrau depois da ponte (os
        # navegadores, a cópia arquivada) começava por ele e nunca tentava a ponte — ela é tentada antes
        ponte = next((j for j, d in enumerate(self.degraus[:limite]) if str(getattr(d, "nome", "")).startswith("P ·")), None)
        if ponte is not None and ponte < inicio:
            ordem.insert(0, ponte)
        # 11/11/2026: o domínio que terminou pendente há pouco vai direto ao degrau do computador da titular (ver RESUBIR_PENDENTE_H)
        import os
        local = next((j for j, d in enumerate(self.degraus[:limite]) if codigo(d) == 9), None)
        desde = self.pendente_desde.get(dom)
        atalho = (local is not None and desde is not None and corpo is None and 0 <= self.relogio() - desde < RESUBIR_PENDENTE_H * 3600
                  and os.environ.get("ELDORADO_FORCAR") != "1" and not servico_local(url))
        if atalho:
            ordem = [local]
        for i in ordem:
            d = self.degraus[i]
            if d.pesado and self.governador is not None and not self.governador.pode_iniciar(f"degrau:{d.nome}", "pesado"):
                motivos.append(f"{d.nome}: adiado pelo governador")
                continue
            try:
                for tentativa in Retrying(stop=stop_after_attempt(self.tentativas), retry=retry_if_exception_type(Passageiro),
                                          wait=wait_exponential(multiplier=0.5, max=8), sleep=self.dormir, reraise=True):
                    with tentativa:
                        self._esperar(dom)
                        r = d.buscar(url, self.tempo_limite, corpo=corpo) if corpo is not None else d.buscar(url, self.tempo_limite)
                        avaliar(r)
            except Bloqueado as e:
                self.bloqueios[dom] = self.bloqueios.get(dom, 0) + 1
                motivos.append(f"{d.nome}: bloqueado ({e})")
                continue
            except Indisponivel as e:
                if "não existe" in str(e):              # sem subir degraus e sem aprender nada sobre o domínio
                    raise Indisponivel(f"{dom}: {e}") from e
                motivos.append(f"{d.nome}: indisponivel ({e})")
                continue
            except Passageiro as e:
                motivos.append(f"{d.nome}: passageiro ({e})")
                continue
            except TypeError as e:                                  # o degrau não faz POST
                if corpo is None:
                    raise
                motivos.append(f"{d.nome}: não faz POST ({str(e)[:60]})")
                continue
            except Pendente as e:
                # 29/10/2026: "pendente" não é sucesso: registra que o domínio exigiu o computador da titular, mas NÃO como o
                # degrau por onde começar (antes, uma única falha mandava o domínio para sempre ao "pendente")
                if atalho:                                          # 11/11/2026: sem subir a escada de novo (e sem renovar a hora)
                    from datetime import datetime, timezone
                    quando = datetime.fromtimestamp(desde, timezone.utc).strftime("%d/%m %H:%M UTC")
                    raise Pendente(f"{e} — pedido já entregue: a escada inteira terminou pendente em {quando} e volta a ser "
                                   f"tentada {RESUBIR_PENDENTE_H:.0f} h depois") from e
                self.pendente_desde[dom] = self.relogio()
                self._registrar_exige_local(dom)
                # 05/11/2026 (R45): a pendência leva o motivo de cada degrau que falhou antes (antes só «pendente»)
                raise Pendente(f"{e} — antes: {'; '.join(motivos)}" if motivos else str(e)) from e   # 14/11: sem o corte (os últimos degraus somiam)
            r.degrau = d.nome
            self.ultimo_degrau = d.nome                         # o degrau que serviu a última leitura (vai para o livro)
            self.pendente_desde.pop(dom, None)                  # 11/11/2026: o domínio respondeu: deixa de ser pendente
            r.alertas = motivos + r.alertas
            if self.aprendido.get(dom) != i:
                self._aprender(dom, i)
            return r
        raise Bloqueado(f"{dom}: nenhum degrau conseguiu ({'; '.join(motivos)})")

    def semear(self, memoria: dict[str, int]) -> int:
        """29/10/2026: a memória do que já foi aprendido (domínio → código canônico do degrau), convertida para a posição
        nesta escada; o próximo pedido ao domínio começa pelo degrau que funcionou (antes recomeçava do primeiro)."""
        pos = {codigo(d): j for j, d in enumerate(self.degraus)}
        n = 0
        for dom, cod in memoria.items():
            if cod == 9:                             # 29/10/2026: o computador da titular nunca é o ponto de partida
                continue
            if cod in pos and dom not in self.aprendido:
                self.aprendido[dom] = pos[cod]
                n += 1
        return n

    def semear_pendentes(self, memoria: dict[str, float]) -> int:
        """11/11/2026: a memória dos domínios que terminaram pendentes no computador da titular (domínio → a hora da última
        subida inteira); vale a mais recente."""
        n = 0
        for dom, quando in memoria.items():
            if quando > self.pendente_desde.get(dom, 0.0):
                self.pendente_desde[dom] = float(quando)
                n += 1
        return n

    def degrau_maximo(self) -> int | None:
        """O código canônico do degrau mais alto que esta escada precisou usar (para a Sala: o Camoufox está em uso?)."""
        usados = [codigo(self.degraus[i]) for i in set(self.aprendido.values()) if 0 <= i < len(self.degraus)]
        usados = [u for u in usados if u is not None]
        return max(usados, key=ORDEM_CANONICA.index) if usados else None

    def _registrar_exige_local(self, dom: str) -> None:
        if self.diario:
            self.diario.emitir("dominio.aprendido", "escada", {"dominio": dom, "degrau_que_funciona": None, "bloqueios": self.bloqueios.get(dom, 0),
                                                                 "exige_local": 1, "ultimo_bloqueio": agora()})

    def _aprender(self, dom: str, i: int, exige_local: bool = False) -> None:
        self.aprendido[dom] = i
        if self.diario:
            # 29/10/2026: grava o CÓDIGO canônico do degrau (cada escada tem a sua lista; a posição não serve a outra)
            dados = {"dominio": dom, "degrau_que_funciona": codigo(self.degraus[i]) if 0 <= i < len(self.degraus) else i,
                     "bloqueios": self.bloqueios.get(dom, 0), "exige_local": int(exige_local),
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
