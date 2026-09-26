"""PILOTO - INTERCEPTADOR (titular, 26/09) — a segunda IA do sistema, com o mesmo modelo (Qwen3-8B).

O Espião descobre; o Interceptador COMPROVA. Ele não explora, não cria, não aposta. Pega os indícios de
oportunidade que já existem no sistema — a fila de resgate (o que o Espião achou nos sites do terceiro setor,
e os editais do acervo sem prazo, objeto ou página oficial) e os editais abertos do painel com itens em falta —
e, um por um:

    1. entende os dados já indicados;
    2. MAPEIA O SITE OFICIAL da oportunidade (conhecido, escolhido entre os links da divulgação, ou buscado);
    3. lê o documento/edital na fonte oficial e comprova as DOZE condições da oportunidade, cada uma com
       trecho literal encontrado no texto;
    4. para o que faltar, registra a dispensa só se o próprio edital a disser, com trecho.

Nada entra sem prova. O que ele confirma volta para a fila de resgate (o item vira 'resgatado' e vai à
Biblioteca), para o registro do edital (a ficha do painel) e para o bordo (prazo aberto confirmado = OURO).
"""
from __future__ import annotations

import json
import time
from datetime import date
from pathlib import Path

from .investigador import DOZE, investigar_um, registro
from .nucleo import load_json, now_iso, write_json

ROOT = Path(__file__).resolve().parents[1]
FILA = ROOT / "estado/piloto/fila_resgate.json"
ESTADO = ROOT / "estado/piloto/interceptador.json"
PUB = ROOT / "docs/dados/interceptador.json"
MOTOR = "piloto-aberto"        # o motor de busca aberta da família Piloto: as estrelas de ouro aparecem nele
REVISITA_DIAS = 7


def _mestre_por_url() -> dict:
    """Ids do arquivo mestre por URL — a fila de resgate guarda a URL; o registro do edital, o id."""
    from .investigador import _mestre
    return {v.get("url"): k for k, v in _mestre().items() if v.get("url")}


def alvos(maximo: int = 40) -> list[dict]:
    """Quem precisa de comprovação, em ordem: fila de resgate (mais urgente primeiro), depois os editais
    abertos do painel com itens em falta. Um alvo já interceptado só volta depois de REVISITA_DIAS."""
    est = load_json(ESTADO) if ESTADO.exists() else {}
    feitos = est.get("feitos") or {}
    limite = (date.today().toordinal() - REVISITA_DIAS)
    def recente(k):
        f = feitos.get(k) or {}
        try:
            return date.fromisoformat(str(f.get("em", ""))[:10]).toordinal() > limite
        except ValueError:
            return False
    out, vistos = [], set()
    fila = (load_json(FILA) or {}).get("itens") or {} if FILA.exists() else {}
    por_url = _mestre_por_url()
    for it in sorted(fila.values(), key=lambda x: -(x.get("urgencia") or 0)):
        if it.get("estado") == "resgatado":
            continue
        eid = it.get("id") if registro(str(it.get("id") or "")) else por_url.get(it.get("url"))
        if not eid and it.get("url") and it.get("id"):
            # indício vindo do catálogo do Espião: ainda não tem registro — o Interceptador cria um, a partir da fila
            eid = str(it["id"])
            arq = ROOT / "dados/editais/extraidos" / f"{eid}.json"
            if not arq.exists():
                write_json(arq, {"edital_id": eid, "titulo": it.get("titulo"), "url": it.get("url"), "orgao": it.get("orgao"),
                                 "fonte_nome": it.get("orgao"), "origem": "fila de resgate (catálogo do Espião)",
                                 "enquadramento": it.get("enquadramento"), "descoberto_em": it.get("descoberto_em")})
        if not eid or eid in vistos or recente(eid):
            continue
        vistos.add(eid); out.append({"id": eid, "de": "fila de resgate", "fila_id": it.get("id"), "titulo": it.get("titulo")})
        if len(out) >= maximo:
            return out
    # editais ABERTOS com itens em falta: o prazo aberto vive no registro (verificação do titular ou
    # investigação anterior), não no arquivo mestre — é por ele que o painel monta os cartões
    hoje = date.today().isoformat()
    for arq in sorted((ROOT / "dados/editais/extraidos").glob("*.json")):
        if len(out) >= maximo:
            break
        eid = arq.stem
        if eid in vistos or recente(eid):
            continue
        try:
            ex = json.loads(arq.read_text(encoding="utf-8"))
        except ValueError:
            continue
        ve = ex.get("verificacao_externa") if isinstance(ex.get("verificacao_externa"), dict) else {}
        prazo = str(ve.get("prazo") or ex.get("fim") or (ex.get("itens") or {}).get("prazo") or "")[:10]
        if not prazo or prazo < hoje:
            continue
        inv = ex.get("investigacao_ia") or {}
        if inv.get("comprovados", 0) >= len(DOZE):
            continue
        e = registro(eid) or {}
        if str(e.get("titulo") or "").startswith("Diário Oficial de") or not (e.get("url") or e.get("pagina_oficial")):
            continue
        vistos.add(eid); out.append({"id": eid, "de": "edital aberto com itens em falta", "titulo": e.get("titulo"), "prazo": prazo})
    return out


def _devolver_a_fila(alvo: dict, e_inv: dict) -> None:
    """O que foi comprovado volta à fila de resgate: prazo confirmado = item resgatado (e vai à Biblioteca)."""
    if not alvo.get("fila_id"):
        return
    try:
        from .missao_especial import registrar_resgate
        campos = e_inv.get("campos") or {}
        reg = registro(alvo["id"]) or {}
        dados = {"prazo": reg.get("fim"), "inicio": reg.get("inicio"), "pagina_oficial": reg.get("pagina_oficial"),
                 "objeto": reg.get("objeto"), "orgao": reg.get("orgao"), "valor": reg.get("valor_texto"),
                 "trecho": (campos.get("Prazo de inscrição") or {}).get("trecho")}
        registrar_resgate(alvo["fila_id"], {k: v for k, v in dados.items() if v})
    except Exception:
        pass


def _abate(alvo: dict, e_inv: dict) -> None:
    """Prazo aberto confirmado com trecho = estrela de OURO no motor do Piloto."""
    try:
        from .esquadrilha import abrir_missao, fechar_missao
        reg = registro(alvo["id"]) or {}
        fim = reg.get("fim")
        abrir_missao({"tipo": "interceptar", "motor": MOTOR, "ordem": 1, "alvo_id": alvo["id"], "_alvo": {"titulo": alvo.get("titulo")}}, "Piloto - Interceptador")
        achados = []
        if fim and fim >= date.today().isoformat() and (e_inv.get("campos") or {}).get("Prazo de inscrição", {}).get("comprovado"):
            achados.append({"titulo": reg.get("titulo"), "url": reg.get("pagina_oficial") or reg.get("url"), "prazo": fim,
                            "situacao": "aberta", "resgate": True, "novo": False})
        fechar_missao(f"{e_inv.get('comprovados', 0)}/{len(DOZE)} comprovados", achados,
                      f"interceptador · {(reg.get('titulo') or '')[:60]}: {e_inv.get('comprovados', 0)}/{len(DOZE)} itens comprovados ou dispensados")
    except Exception:
        pass


def rodada(ia, minutos: float = 280, maximo: int = 40) -> dict:
    fim = time.time() + minutos * 60
    est = load_json(ESTADO) if ESTADO.exists() else {"feitos": {}, "rodadas": []}
    est.setdefault("feitos", {}); est.setdefault("rodadas", [])
    lista = alvos(maximo)
    r = {"em": now_iso(), "papel": "Piloto - Interceptador", "modelo": "qwen3-8b", "alvos": len(lista), "editais": []}
    for a in lista:
        if time.time() > fim:
            r["parou"] = "tempo da rodada esgotado"; break
        x = investigar_um(a["id"], ia, "qwen3-8b")
        x["de"] = a["de"]
        r["editais"].append(x)
        e_inv = (registro(a["id"]) or {}).get("investigacao_ia") or {}
        _devolver_a_fila(a, e_inv)
        _abate(a, e_inv)
        est["feitos"][a["id"]] = {"em": now_iso(), "comprovados": x.get("comprovados"), "de": a["de"]}
        write_json(ESTADO, est)
        print(f"{a['id']} · {x.get('comprovados', '-')}/{len(DOZE)} · {x.get('s', '-')} s · {a['de']} · {str(a.get('titulo'))[:60]} · {x.get('erro') or ''}", flush=True)
    r["resumo"] = {"interceptados": len(r["editais"]),
                   "media_itens": round(sum(x.get("comprovados", 0) for x in r["editais"]) / max(1, len(r["editais"])), 1),
                   "completos": sum(1 for x in r["editais"] if x.get("comprovados") == len(DOZE)),
                   "com_prazo_confirmado": sum(1 for x in r["editais"] if "Prazo de inscrição" not in (x.get("nao_resolvidos") or []) and "comprovados" in x)}
    est["rodadas"] = (est["rodadas"] + [{k: v for k, v in r.items() if k != "editais"}])[-30:]
    write_json(ESTADO, est)
    PUB.parent.mkdir(parents=True, exist_ok=True)
    write_json(PUB, {**r, "editais": [{k: v for k, v in x.items() if k != "passos"} for x in r["editais"]],
                     "acumulado": {"interceptados": len(est["feitos"]), "rodadas": len(est["rodadas"])}})
    return r
