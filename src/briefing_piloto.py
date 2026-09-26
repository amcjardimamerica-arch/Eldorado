"""BRIEFING DE VOO — o relatório que o Piloto escreve ANTES de decolar.

Nenhum voo começa no escuro. A cada decolagem o Piloto:

  1. lê o estado do banco (quantos editais, de onde vêm, o que está aberto, o que arquivou);
  2. lê os briefings dos voos anteriores (o que já tentou, o que rendeu, o que veio seco);
  3. escreve um DIAGNÓSTICO: onde há buraco no mapa — setor, região ou tipo de fonte que a
     casa ainda não olhou;
  4. faz uma APOSTA PREDITIVA: onde provavelmente existe recurso que ninguém aqui viu ainda,
     e por quê;
  5. dessa aposta nasce o PROMPT da pesquisa daquele voo.

O briefing fica guardado em estado/piloto/briefings/ e alimenta o voo seguinte — é assim que
a linha de pesquisa evolui em vez de girar em círculo.
"""
from __future__ import annotations

import json
import re
from datetime import date, datetime, timezone
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json

PASTA = ROOT / "estado/piloto/briefings"
PUB = ROOT / "docs/dados/briefings_piloto.json"
LIMITE_HISTORICO = 8


def _estado_do_banco() -> dict:
    """Uma fotografia curta do que a Biblioteca tem hoje."""
    f = {}
    base = sorted((ROOT / "dados/editais").glob("*-eldorado-*-completo.json"), reverse=True)
    if base:
        d = load_json(base[0])
        itens = d.get("itens") or {}
        eds = list(itens.values()) if isinstance(itens, dict) else list(itens)
        res = d.get("resumo") or {}
        f["editais_no_banco"] = len(eds)
        f["oportunidades_abertas"] = (res.get("prazo") or {}).get("aberto")
        f["arquivadas"] = (res.get("prazo") or {}).get("encerrado")
        f["sem_prazo_confirmado"] = (res.get("prazo") or {}).get("sem_prazo_confirmado")
        ufs, orgs = {}, {}
        for e in eds:
            ufs[e.get("uf") or "?"] = ufs.get(e.get("uf") or "?", 0) + 1
            o = (e.get("orgao") or "?")[:40]
            orgs[o] = orgs.get(o, 0) + 1
        f["por_uf"] = dict(sorted(ufs.items(), key=lambda kv: -kv[1])[:8])
        f["orgaos_mais_frequentes"] = dict(sorted(orgs.items(), key=lambda kv: -kv[1])[:8])
        f["nota"] = "quase tudo aqui é fonte PÚBLICA — o Piloto existe para trazer o que falta: dinheiro privado"
    ab = ROOT / "docs/dados/abertas.json"
    if ab.exists():
        f["linhas_na_vitrine"] = load_json(ab).get("total")      # tudo que o painel exibe, público incluso
    rad = ROOT / "dados/empresas/radar_piloto.json"
    if rad.exists():
        emp = (load_json(rad).get("empresas") or {})
        f["empresas_no_radar"] = len(emp)
        f["radar_a_pesquisar"] = sum(1 for e in emp.values() if e.get("marcador") == "a_pesquisar")
        f["setores_ja_vistos"] = sorted({a for e in emp.values() for a in (e.get("angulos") or [])})[:14]
    fr = ROOT / "estado/piloto/fila_resgate.json"
    if fr.exists():
        its = (load_json(fr).get("itens") or {}).values()
        f["editais_incompletos_na_fila"] = sum(1 for v in its if v.get("estado") == "aguardando")
        f["editais_ja_resgatados"] = sum(1 for v in its if v.get("estado") == "resgatado")
    rk = ROOT / "docs/dados/ranking_apoiadores.json"
    if rk.exists():
        d = load_json(rk)
        f["apoiadores_mapeados"] = d.get("total")
        f["sem_dado_cadastral"] = (d.get("total") or 0) - (d.get("com_cnpj") or 0)
    return f


def anteriores(n: int = LIMITE_HISTORICO) -> list[dict]:
    if not PASTA.exists():
        return []
    arqs = sorted(PASTA.glob("*.json"), reverse=True)[:n]
    return [load_json(a) for a in arqs]


def _resumo_dos_anteriores(hist: list[dict]) -> list[str]:
    L = []
    for b in hist:
        L.append(f"[{b.get('em', '')[:10]}] apostou em {b.get('aposta', {}).get('onde', '?')} "
                 f"→ {b.get('resultado', {}).get('achados', '?')} achado(s); {b.get('aposta', {}).get('porque', '')[:80]}")
    return L


def _cobertura() -> str:
    """O Piloto não repete o trabalho dos motores: precisa saber onde eles já olham."""
    try:
        from .cobertura import instrucao_para_o_piloto, mapa
        mapa()
        return instrucao_para_o_piloto()
    except Exception:
        return ""


def _registrar_mudez(mudo: bool) -> None:
    """O cargo exige do ocupante ≥50% de acerto. Um modelo que não responde entrega zero —
    então a mudez é medida e fica no arquivo do cargo, para a avaliação poder decidir."""
    # O CONTADOR MORA EM estado/, NÃO EM config/. O voo só commita estado, dados, docs e a
    # biblioteca: gravado no arquivo do cargo, o contador sumia a cada pouso — depois de dois
    # voos do Qwen3 ele ainda marcava 0 pedidos, e a regra dos 50% nunca poderia valer.
    # SÓ O VOO REAL CONTA. Em 24/09 os testes, com modelos falsos "mudos", gravaram 33 pedidos
    # e 12% de resposta no contador do Qwen3 — um desempenho que não era dele e que teria
    # disparado o alerta de substituição. O workflow põe ELDORADO_VOO_REAL=1 no passo do ciclo;
    # fora dele, nada é contado.
    import os as _os
    if _os.environ.get("ELDORADO_VOO_REAL") != "1":
        return
    from .cargo_piloto import ocupante as _oc
    arq = ROOT / "estado/piloto/desempenho_em_voo.json"
    tudo = load_json(arq) if arq.exists() else {}
    oid = (_oc() or {}).get("id") or "vago"
    d = tudo.setdefault(oid, {"pedidos": 0, "mudos": 0})
    d["pedidos"] += 1
    d["mudos"] += 1 if mudo else 0
    d["taxa_de_resposta"] = round(1 - d["mudos"] / d["pedidos"], 3)
    d["avaliado_ate"] = now_iso()[:16]
    if d["pedidos"] >= 10 and d["taxa_de_resposta"] < 0.5:
        d["alerta"] = (f"responde em {d['taxa_de_resposta']*100:.0f}% dos pedidos, abaixo dos 50% "
                       "que o cargo exige — candidato a substituição pelo banco de reserva")
    else:
        d.pop("alerta", None)
    tudo[oid] = d
    write_json(arq, tudo)


def escrever(ia, motor_cfg: dict | None = None) -> dict:
    """Escreve o briefing deste voo e devolve o prompt de pesquisa que ele gerou."""
    banco = _estado_do_banco()
    hist = anteriores()
    já_apostou = [b.get("aposta", {}).get("onde") for b in hist if b.get("aposta")]
    secos = [b.get("aposta", {}).get("onde") for b in hist
             if (b.get("resultado") or {}).get("achados") == 0 and b.get("aposta")]

    r = ia.perguntar(
        "VOCÊ É O PILOTO do Eldorado, e está no pátio prestes a decolar. Antes de sair, faça a leitura da casa "
        "e decida ONDE vale procurar dinheiro que ainda não mapeamos.\n\n"
        f"O QUE A BIBLIOTECA TEM HOJE:\n{json.dumps(banco, ensure_ascii=False, indent=1)}\n\n"
        + ("VOOS ANTERIORES:\n- " + "\n- ".join(_resumo_dos_anteriores(hist)) + "\n\n" if hist else "")
        + (f"JÁ APOSTEI NESTES LUGARES (não repita): {[x for x in já_apostou if x]}\n" if já_apostou else "")
        + (f"ESTES VIERAM SECOS: {[x for x in secos if x]}\n\n" if secos else "\n")
        + ("ATENÇÃO: há editais incompletos esperando resgate. Eles são atendidos ANTES desta exploração — "
           "o que você planeja aqui é o que sobra de tempo depois deles.\n\n"
           if banco.get("editais_incompletos_na_fila") else "")
        + (_cobertura() + "\n\n")
        + "REGRA PRINCIPAL DO ESPIÃO (titular, 26/09): encontre o que os outros motores NÃO encontram. Seja criativo. Procure "
          "oportunidades em geral — empresas, fundações, institutos, editais abertos, prêmios, fundos, programas — onde os 30 motores "
          "não chegam (a cobertura mostra onde eles já estão). Sua finalidade primordial é CRIAR oportunidades novas que virem fontes "
          "permanentes de busca. "
        + "Pense como quem caça a FONTE do dinheiro, não o edital: que empresa deduz imposto, que empresa patrocina "
          "evento, quem tem instituto ou fundação, quem publica relatório ESG, quem aparece como apoiadora no site de "
          "outra entidade, que setor da economia está com caixa e ainda não foi procurado por ninguém daqui.\n"
          "Faça uma APOSTA: onde provavelmente existe recurso que nós ainda não vimos? Diga por que acredita nisso "
          "(o raciocínio importa) e escreva a pergunta de pesquisa que este voo deve responder.",
        '{"diagnostico": "o buraco que vejo no mapa, uma frase", '
        '"aposta": {"onde": "setor/região/tipo de fonte", "porque": "o raciocínio", "confianca": "alta|media|baixa"}, '
        '"pergunta_de_pesquisa": "a pergunta que orienta o voo", '
        '"o_que_procurar": ["site oficial", "..."], "nivel": "regional|estadual|nacional|internacional"}')

    b = {"em": now_iso(), "voo": len(list(PASTA.glob("*.json"))) + 1 if PASTA.exists() else 1,
         "banco": banco,
         "diagnostico": (r or {}).get("diagnostico"),
         "aposta": (r or {}).get("aposta") or {},
         "pergunta_de_pesquisa": (r or {}).get("pergunta_de_pesquisa"),
         "o_que_procurar": (r or {}).get("o_que_procurar") or [],
         "nivel": (r or {}).get("nivel") or "nacional",
         "resultado": {"achados": None}}
    if not b["pergunta_de_pesquisa"]:
        # REDE DE SEGURANÇA COM RUMO DE VERDADE (23/09). Antes ela devolvia sempre a mesma
        # pergunta genérica: em 12 voos houve 2 apostas distintas, porque o modelo ficou mudo
        # em 9 deles. Agora o rumo sai do catálogo de ângulos, rodando por sorteio sem
        # repetição — o voo perde a inteligência do modelo, mas não perde a direção.
        import random
        from .nucleo import load_json as _lj
        cfg = _lj(ROOT / "config/motor_piloto.json") if (ROOT / "config/motor_piloto.json").exists() else {}
        angs = cfg.get("angulos_de_ataque") or []
        usados = [x.get("aposta", {}).get("onde") for x in hist if x.get("aposta")]
        livres = [a for a in angs if a.get("id") not in usados] or angs
        if livres:
            a = random.Random(f"{now_iso()[:13]}-{len(hist)}").choice(livres)
            b["pergunta_de_pesquisa"] = a["pergunta"]
            b["nivel"] = a.get("nivel") or "nacional"
            b["aposta"] = {"onde": a["id"], "confianca": "baixa",
                           "porque": "o modelo não respondeu; rumo sorteado do catálogo, sem repetir os últimos"}
            b["o_que_procurar"] = [a.get("alvo") or "empresa"]
        else:
            b["pergunta_de_pesquisa"] = ("Que empresas com caixa e programa social ainda não estão na nossa "
                                         "lista, e onde publicam seus editais ou patrocínios?")
            b["aposta"] = {"onde": "livre", "porque": "o modelo não respondeu e o catálogo está vazio",
                           "confianca": "baixa"}
        b["modelo_mudo"] = True
        _registrar_mudez(True)
    else:
        _registrar_mudez(False)
    PASTA.mkdir(parents=True, exist_ok=True)
    # o carimbo vai ao milissegundo: dois briefings no mesmo segundo colidiam no mesmo
    # arquivo, e o histórico deixava de crescer — a rede de segurança repetia o rumo
    write_json(PASTA / f"{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}.json", b)
    return b


def fechar(briefing: dict, achados: list[dict], abertas: int = 0, arquivadas: int = 0) -> dict:
    """Ao pousar, o briefing recebe o que o voo trouxe — é o que o próximo voo vai ler."""
    briefing["resultado"] = {"achados": len(achados), "oportunidades_abertas": abertas,
                             "arquivadas": arquivadas,
                             "alvos": [{"nome": a.get("titulo", "")[:90], "url": a.get("url"),
                                        "prazo": a.get("prazo"), "situacao": a.get("situacao")} for a in achados[:12]],
                             "fechado_em": now_iso()}
    arqs = sorted(PASTA.glob("*.json"), reverse=True) if PASTA.exists() else []
    if arqs:
        write_json(arqs[0], briefing)
    publicar()
    return briefing


def publicar() -> dict:
    hist = anteriores(12)
    saida = {"em": now_iso(), "total": len(list(PASTA.glob("*.json"))) if PASTA.exists() else 0,
             "voos": [{"em": b.get("em", "")[:16], "diagnostico": b.get("diagnostico"),
                       "aposta": b.get("aposta"), "pergunta": b.get("pergunta_de_pesquisa"),
                       "nivel": b.get("nivel"), "resultado": b.get("resultado")} for b in hist]}
    write_json(PUB, saida)
    return {"total": saida["total"]}


if __name__ == "__main__":
    print(json.dumps({"banco": _estado_do_banco(), **publicar()}, ensure_ascii=False, indent=1))
