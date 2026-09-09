"""Como chegar em cada fonte — a rota, não só o endereço.

A lição das rodadas de 08 e 09/09/2026: o coletor conclui "não há edital" quando
o que houve foi rota errada. O mesmo endereço responde por um caminho e falha
por outro — `bndes.gov.br/wps/portal` devolve só metadados para requisição de
servidor e o conteúdo inteiro para o navegador; `portaldecompraspublicas.com.br`
devolve HTTP 403 para requisição e monta a página em JavaScript;
`fundacaomariaemilia.org.br` não abre por nenhum caminho, porque o certificado
está inválido.

Este módulo lê `config/rotas_de_coleta.json` e responde três perguntas que o
coletor precisa fazer antes de gastar uma requisição:

  1. `rota_de(url)` — por qual caminho esta URL se abre?
  2. `pode_da_nuvem(url)` — vale tentar da nuvem, ou só do navegador do titular?
  3. `serve_como_fonte(url)` — o que estiver aqui pode virar prazo e objeto na
     base, ou serve apenas para descobrir o nome do órgão?

A terceira é a que protege a regra do titular: portal de notícia e plataforma
privada de licitação nunca viram fonte de prazo, por mais convincente que a
página pareça.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache

from .nucleo import ROOT

CONFIG = ROOT / "config/rotas_de_coleta.json"

# Rotas em que a página NÃO pode alimentar prazo, objeto nem página oficial.
_NAO_SERVEM = frozenset({"nao_serve_como_fonte", "so_para_descobrir_nome", "bloqueado"})


@lru_cache(maxsize=1)
def rotas() -> tuple[dict, ...]:
    dados = json.loads(CONFIG.read_text(encoding="utf-8"))
    return tuple(dados["rotas"])


def _host(url: str) -> str:
    return re.sub(r"^\w+://", "", str(url or "")).split("/", 1)[0].lower()


def rota_de(url: str) -> dict | None:
    """A rota mais específica que casa com a URL, ou None se o domínio é novo.

    Casa por sufixo de domínio e também por prefixo de caminho, porque
    `bndes.gov.br` inteiro responde a requisição simples mas
    `bndes.gov.br/wps/portal` exige navegador — e é o caminho que decide.
    """
    alvo = str(url or "").lower()
    # "www." atrapalha o casamento por caminho: o padrão é escrito
    # "bndes.gov.br/wps/portal" e a URL real vem "www.bndes.gov.br/wps/portal".
    alvo_sem_esquema = re.sub(r"^(?:\w+://)?(?:www\.)?", "", alvo)
    host = re.sub(r"^www\.", "", _host(alvo))
    melhor = None
    melhor_peso = -1
    for rota in rotas():
        for padrao in rota.get("padrao_dominio", []):
            p = padrao.lower()
            casa = alvo_sem_esquema.startswith(p) if "/" in p else (
                host == p or host.endswith("." + p))
            if not casa:
                continue
            peso = len(p) + (1000 if "/" in p else 0)
            if peso > melhor_peso:
                melhor, melhor_peso = rota, peso
    return melhor


def pode_da_nuvem(url: str) -> bool:
    """Vale tentar da nuvem? Domínio desconhecido responde True: tentar é barato,
    e o resultado ensina a rota."""
    rota = rota_de(url)
    if rota is None:
        return True
    return bool(rota.get("alcancavel_da_nuvem", True))


def exige_navegador(url: str) -> bool:
    rota = rota_de(url)
    if rota is None:
        return False
    return rota.get("rota") in {"navegador_obrigatorio", "api_oficial"} and not rota.get(
        "alcancavel_da_nuvem", True)


def serve_como_fonte(url: str) -> tuple[bool, str]:
    """(pode virar prazo/objeto na base, motivo)."""
    rota = rota_de(url)
    if rota is None:
        return True, "domínio ainda não catalogado: tratar como fonte, e registrar a rota depois de tentar"
    if rota.get("rota") in _NAO_SERVEM:
        proibido = rota.get("proibido_como_fonte_de") or ["prazo", "objeto", "pagina_oficial"]
        return False, "%s: não serve como fonte de %s. %s" % (
            rota["familia"], ", ".join(proibido), rota.get("saida") or rota.get("nota") or "")
    return True, "%s: rota %s" % (rota["familia"], rota["rota"])


def ritmo_de(url: str) -> str | None:
    rota = rota_de(url)
    return (rota or {}).get("ritmo")


def diagnostico(url: str) -> dict:
    """Tudo o que se sabe sobre como abrir esta URL, para o relatório e o log."""
    rota = rota_de(url)
    serve, motivo = serve_como_fonte(url)
    return {
        "url": url,
        "familia": (rota or {}).get("familia"),
        "rota": (rota or {}).get("rota", "desconhecida"),
        "pode_da_nuvem": pode_da_nuvem(url),
        "exige_navegador": exige_navegador(url),
        "serve_como_fonte": serve,
        "motivo": motivo,
        "ritmo": ritmo_de(url),
        "erro_conhecido": (rota or {}).get("erro_conhecido"),
    }
