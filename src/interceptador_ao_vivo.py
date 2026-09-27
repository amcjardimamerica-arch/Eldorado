"""O INTERCEPTADOR AO VIVO (titular, 27/09) — o mesmo canal do Espião, arquivo próprio.

A cada etapa do voo (alvo escolhido, página oficial, leitura da fonte, pergunta ao modelo, dispensas, parecer,
pouso), grava docs/dados/interceptador_ao_vivo.json no ramo piloto-ao-vivo pela API do GitHub. O painel lê de
lá direto, sem esperar a republicação do site: é o que o titular vê "em tempo real".
Limite: um anúncio a cada 15 s no mínimo (a API tem limite secundário); o pouso sempre grava.
"""
from __future__ import annotations

import base64
import json
import time

from .posicao_piloto import RAMO, _agora, _api

ARQUIVO = "docs/dados/interceptador_ao_vivo.json"
_e = {"sha": None, "t": 0.0, "voo": {}}


def _gravar(conteudo: dict, forcar: bool = False) -> bool:
    if not forcar and time.time() - _e["t"] < 15:
        return False
    corpo = {"message": "interceptador ao vivo: " + str(conteudo.get("etapa") or conteudo.get("estado"))[:60], "branch": RAMO,
             "content": base64.b64encode(json.dumps(conteudo, ensure_ascii=False, indent=1).encode("utf-8")).decode()}
    if not _e["sha"]:
        c0, atual = _api("GET", f"contents/{ARQUIVO}?ref={RAMO}")
        if c0 == 200:
            _e["sha"] = atual.get("sha")
    if _e["sha"]:
        corpo["sha"] = _e["sha"]
    cod, r = _api("PUT", f"contents/{ARQUIVO}", corpo)
    if cod in (409, 422):
        c2, atual = _api("GET", f"contents/{ARQUIVO}?ref={RAMO}")
        if c2 == 200:
            corpo["sha"] = atual.get("sha"); cod, r = _api("PUT", f"contents/{ARQUIVO}", corpo)
    if cod in (200, 201):
        _e["sha"] = ((r.get("content") or {}).get("sha")) or _e["sha"]; _e["t"] = time.time()
        return True
    return False


def decolar(alvo: dict) -> None:
    _e["voo"] = {"estado": "em_voo", "papel": "Piloto - Interceptador", "inicio": _agora(), "atualizado_em": _agora(),
                 "alvo": {"titulo": (alvo or {}).get("titulo"), "de": (alvo or {}).get("de"), "modo": (alvo or {}).get("modo"),
                          "tipo": (alvo or {}).get("tipo"), "url": (alvo or {}).get("url")},
                 "etapa": "alvo escolhido", "passos": [{"em": _agora(), "etapa": "alvo escolhido", "detalhe": str((alvo or {}).get("titulo") or "")[:160]}]}
    _gravar(_e["voo"], forcar=True)


def etapa(nome: str, detalhe: str = "") -> None:
    if not _e["voo"]:
        return
    _e["voo"]["etapa"] = nome; _e["voo"]["atualizado_em"] = _agora()
    _e["voo"]["passos"] = (_e["voo"]["passos"] + [{"em": _agora(), "etapa": nome, "detalhe": str(detalhe)[:200]}])[-14:]
    _gravar(_e["voo"])


def pousar(resultado: dict) -> None:
    v = _e["voo"] or {"papel": "Piloto - Interceptador", "passos": []}
    v.update({"estado": "pousou", "fim": _agora(), "atualizado_em": _agora(), "etapa": "pousou",
              "resultado": {k: resultado.get(k) for k in ("qualidade", "comprovados", "dispensados", "total", "pagina_oficial", "erro", "resultado", "segundos")},
              "parecer": (resultado.get("parecer_fonte") or {}).get("serve_como_fonte")})
    v["passos"] = (v.get("passos", []) + [{"em": _agora(), "etapa": "pousou", "detalhe": f"{resultado.get('qualidade') or resultado.get('resultado') or ''} · {resultado.get('comprovados', '-')}/{resultado.get('total', 12)}"}])[-14:]
    _gravar(v, forcar=True)


def aguardar(porque: str) -> None:
    _gravar({"estado": "aguardando", "papel": "Piloto - Interceptador", "atualizado_em": _agora(), "etapa": "aguardando alvo", "detalhe": porque[:200], "passos": []}, forcar=True)
