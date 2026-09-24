"""POSIÇÃO DO PILOTO EM TEMPO REAL — onde ele está trabalhando agora.

O painel só é republicado a cada 6 horas (deploy do GitHub Pages agendado). Tudo o que o voo
escreve em `docs/dados` chega ao site com até 6 horas de atraso — e foi por isso que o painel
chegou a dizer "em terra" com 16 voos no dia. Para o avião aparecer EXATAMENTE onde o Piloto
está trabalhando, a posição precisa chegar ao navegador em minutos, não em horas.

Como chega:

    ramo próprio   `piloto-ao-vivo`, com um arquivo só: docs/dados/piloto_posicao.json.
                   Fica fora do histórico da main, então nunca entra em conflito com os
                   commits dos voos e não enche o histórico de "piloto: posição".
    API de conteúdo  cada anúncio é uma gravação direta no ramo, sem tocar na árvore de
                   trabalho do voo — nada de pull, rebase ou stash no meio de uma missão.
    o painel lê    direto do repositório, com ETag: resposta 304 não gasta cota.

O que se anuncia é o mínimo para o painel achar o lugar: tipo da missão, motor, alvo. Quem
sabe onde fica cada coisa na tela é o painel — a regra de posição mora lá, não aqui.

Nunca derruba o voo: sem token, sem rede ou com a API recusando, o anúncio falha em silêncio
e fica anotado. Anunciar posição é conveniência; voar é a finalidade.
"""
from __future__ import annotations

import base64
import json
import os
import time
import urllib.request
from datetime import datetime, timezone

RAMO = "piloto-ao-vivo"
ARQUIVO = "docs/dados/piloto_posicao.json"
INTERVALO_MIN_S = 40      # dois anúncios nunca a menos disto — a API tem limite secundário
VALIDADE_S = 480          # o painel esconde o avião se o último anúncio passar disto
REANUNCIO_S = 240         # mesma missão por mais que isto: reanuncia, para não vencer no painel

_estado = {"t": 0.0, "lugar": None, "sha": None, "log": []}


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _api(metodo: str, caminho: str, corpo: dict | None = None) -> tuple[int, dict]:
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not tok or not repo:
        return 0, {"erro": "sem token ou repositório no ambiente (fora do Actions)"}
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/{caminho}", method=metodo,
        data=json.dumps(corpo).encode() if corpo is not None else None,
        headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "eldorado-piloto"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"{}")
        except Exception:
            return e.code, {}
    except Exception as e:
        return -1, {"erro": type(e).__name__}


def _gravar(conteudo: dict, mensagem: str) -> bool:
    corpo = {"message": mensagem, "branch": RAMO,
             "content": base64.b64encode(json.dumps(conteudo, ensure_ascii=False, indent=1)
                                         .encode("utf-8")).decode()}
    if _estado["sha"]:
        corpo["sha"] = _estado["sha"]
    cod, r = _api("PUT", f"contents/{ARQUIVO}", corpo)
    if cod in (409, 422):
        # o sha guardado envelheceu (outro voo gravou no meio): relê e tenta uma vez
        c2, atual = _api("GET", f"contents/{ARQUIVO}?ref={RAMO}")
        if c2 == 200 and atual.get("sha"):
            corpo["sha"] = atual["sha"]
            cod, r = _api("PUT", f"contents/{ARQUIVO}", corpo)
    ok = cod in (200, 201)
    if ok:
        _estado["sha"] = ((r.get("content") or {}).get("sha")) or _estado["sha"]
    _estado["log"] = (_estado["log"] + [{"em": _agora(), "http": cod, "ok": ok,
                                         "msg": mensagem[:60]}])[-20:]
    return ok


def anunciar(missao: dict, voo: int | None = None, de: int | None = None,
             forcar: bool = False) -> dict:
    """Anuncia onde o Piloto começa a trabalhar. Chamado no início de cada missão."""
    tipo = missao.get("tipo")
    motor = missao.get("motor")
    alvo_id = missao.get("alvo_id")
    lugar = f"{tipo}|{motor}|{alvo_id}"
    agora = time.time()
    if not forcar:
        if lugar == _estado["lugar"] and agora - _estado["t"] < REANUNCIO_S:
            return {"anunciado": False, "porque": "mesmo lugar do anúncio anterior"}
        if agora - _estado["t"] < INTERVALO_MIN_S:
            return {"anunciado": False, "porque": f"menos de {INTERVALO_MIN_S}s desde o anterior"}
    alvo = missao.get("_alvo") or {}
    conteudo = {
        "estado": "em_voo",
        "atualizado_em": _agora(),
        "validade_s": VALIDADE_S,
        "voo": voo,
        "missao": {"tipo": tipo, "motor": motor, "alvo_id": alvo_id,
                   "alvo_titulo": (alvo.get("titulo") or "")[:120] or None,
                   "ordem": missao.get("ordem"), "de": de},
        "regra": "o painel mostra o avião SÓ sobre o lugar exato desta missão; "
                 "passada a validade sem novo anúncio, ele some",
    }
    ok = _gravar(conteudo, f"posição: {tipo} · {motor or '—'}")
    if ok:
        _estado.update({"t": agora, "lugar": lugar})
    return {"anunciado": ok, "lugar": lugar, "log": _estado["log"][-1:]}


def pousar(detalhe: str = "") -> dict:
    """No pouso, o avião sai da tela: sem missão, não há lugar exato onde aparecer."""
    ok = _gravar({"estado": "pousado", "atualizado_em": _agora(), "validade_s": VALIDADE_S,
                  "missao": None, "detalhe": detalhe[:120],
                  "regra": "pousado: o avião não aparece em lugar nenhum"},
                 "posição: pousou")
    _estado.update({"t": time.time(), "lugar": None})
    return {"anunciado": ok, "log": _estado["log"][-1:]}


def registro() -> list[dict]:
    """O que foi anunciado neste voo — entra no relatório, para se saber se chegou."""
    return list(_estado["log"])
