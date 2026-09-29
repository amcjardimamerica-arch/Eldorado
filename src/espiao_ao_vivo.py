"""O ESPIÃO AO VIVO (titular, 29/09) — o mesmo canal e o mesmo formato do Interceptador, arquivo próprio.

A cada passo do voo (decolagem com o plano, início de cada missão, resultado de cada missão com o que encontrou, pouso)
grava docs/dados/espiao_ao_vivo.json no ramo piloto-ao-vivo pela API do GitHub. O painel lê de lá direto, a cada 15 s,
sem esperar a republicação do site. Leva também as missões do voo anterior, para a caixa mostrar "as últimas missões"
mesmo no começo de um voo novo. Limite: um anúncio a cada 15 s (o resultado de missão e o pouso sempre gravam).
"""
from __future__ import annotations

import base64
import json
import time

from .posicao_piloto import RAMO, _agora, _api

ARQUIVO = "docs/dados/espiao_ao_vivo.json"
_e = {"sha": None, "t": 0.0, "voo": {}}
NOMES = {"descobrir": "descobrir entidades novas", "aposta": "aposta do briefing", "catalogar": "catalogar site do terceiro setor",
         "prospectar": "prospectar empresas", "resgate": "resgate", "cacar_oportunidade": "caçar oportunidade", "afiar_motor": "afiar motor",
         "reconhecimento": "reconhecimento", "preparando": "preparando o modelo"}


def _gravar(conteudo: dict, forcar: bool = False) -> bool:
    if not forcar and time.time() - _e["t"] < 15:
        return False
    corpo = {"message": "espião ao vivo: " + str(conteudo.get("etapa") or conteudo.get("estado"))[:60], "branch": RAMO,
             "content": base64.b64encode(json.dumps(conteudo, ensure_ascii=False, indent=1).encode("utf-8")).decode()}
    try:
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
    except Exception:
        pass
    return False


def _nome(m: dict) -> str:
    t = m.get("tipo") or ""
    return NOMES.get(t, t) if m.get("motor") in (None, "", "piloto-aberto") else f"{NOMES.get(t, t)} · {m.get('motor')}"


def decolar(plano: list[dict], voo: int | None = None, anteriores: list[dict] | None = None) -> None:
    _e["voo"] = {"estado": "em_voo", "papel": "Piloto - Espião", "voo_do_dia": voo, "inicio": _agora(), "atualizado_em": _agora(),
                 "plano": [{"ordem": i + 1, "missao": _nome(m), "alvo": str((m.get("_alvo") or {}).get("titulo") or m.get("alvo_id") or "")[:120]} for i, m in enumerate(plano)],
                 "etapa": f"decolou — {len(plano)} missão(ões) no plano", "missao_atual": None, "concluidas": [],
                 "anteriores": (anteriores or [])[:10],
                 "passos": [{"em": _agora(), "etapa": "decolou", "detalhe": f"voo {voo or '—'} · {len(plano)} missão(ões): " + ", ".join(sorted({_nome(m) for m in plano}))[:180]}]}
    _gravar(_e["voo"], forcar=True)


def missao(m: dict, n: int, total: int) -> None:
    v = _e["voo"]
    if not v:
        return
    alvo = str((m.get("_alvo") or {}).get("titulo") or (m.get("_site") or {}).get("nome") or (m.get("_brief") or {}).get("pergunta") or m.get("alvo_id") or "")[:160]
    v["missao_atual"] = {"n": n, "total": total, "missao": _nome(m), "alvo": alvo, "desde": _agora()}
    v["etapa"] = f"missão {n}/{total}: {_nome(m)}"; v["atualizado_em"] = _agora()
    v["passos"] = (v["passos"] + [{"em": _agora(), "etapa": f"missão {n}/{total} — {_nome(m)}", "detalhe": alvo}])[-16:]
    _gravar(v)


def resultado(m: dict, alvo, achados: list, licao: str, abates: int = 0) -> None:
    v = _e["voo"]
    if not v:
        return
    ini = (v.get("missao_atual") or {}).get("desde")
    achs = [{"titulo": str(a.get("titulo") or a.get("empresa") or a.get("nome") or "")[:120], "url": a.get("url"), "novo": bool(a.get("novo"))}
            for a in (achados or []) if isinstance(a, dict)][:6]
    v["concluidas"] = (v["concluidas"] + [{"missao": _nome(m), "tipo": m.get("tipo"), "alvo": str(alvo or "")[:160], "inicio": ini, "fim": _agora(),
                                           "achados": len(achados or []), "abates": abates, "licao": str(licao or "")[:220], "encontrou": achs}])[-12:]
    v["missao_atual"] = None; v["atualizado_em"] = _agora()
    v["etapa"] = f"missão concluída: {len(achados or [])} achado(s)"
    v["passos"] = (v["passos"] + [{"em": _agora(), "etapa": f"concluiu — {len(achados or [])} achado(s)", "detalhe": str(licao or "")[:180]}])[-16:]
    _gravar(v, forcar=True)


def pousar(rel: dict, em_corrente: bool = False) -> None:
    v = _e["voo"] or {"papel": "Piloto - Espião", "passos": [], "concluidas": []}
    v.update({"estado": "patio" if em_corrente else "pousou", "fim": _agora(), "atualizado_em": _agora(), "missao_atual": None,
              "etapa": "no pátio — decolando o próximo voo" if em_corrente else "pousou",
              "resultado": {"missoes": len(rel.get("missoes") or []), "abates": rel.get("abates"), "propostas": rel.get("propostas"),
                            "encerrou_por": rel.get("encerrou_por")}})
    v["passos"] = (v.get("passos", []) + [{"em": _agora(), "etapa": v["etapa"], "detalhe": f"{len(rel.get('missoes') or [])} missão(ões) · {rel.get('abates') or 0} abate(s) · {rel.get('propostas') or 0} proposta(s)"}])[-16:]
    _gravar(v, forcar=True)


def preparando() -> None:
    """Início do workflow: o modelo ainda está sendo preparado (3 a 5 min) — a caixa já mostra que o voo começou."""
    _e["voo"] = {"estado": "em_voo", "papel": "Piloto - Espião", "inicio": _agora(), "atualizado_em": _agora(), "etapa": "decolando — preparando o modelo",
                 "missao_atual": None, "concluidas": [], "passos": [{"em": _agora(), "etapa": "decolando", "detalhe": "preparando o modelo local (3 a 5 min)"}]}
    try:
        c0, atual = _api("GET", f"contents/{ARQUIVO}?ref={RAMO}")
        if c0 == 200:
            ant = json.loads(base64.b64decode(atual.get("content") or b"").decode("utf-8") or "{}")
            _e["voo"]["anteriores"] = (ant.get("concluidas") or ant.get("anteriores") or [])[-10:]
    except Exception:
        pass
    _gravar(_e["voo"], forcar=True)
