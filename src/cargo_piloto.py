"""O CARGO DE PILOTO — o ocupante é trocável; o contrato é do sistema.

Três coisas vivem aqui:

  ocupante() ........... quem exerce o cargo hoje (config/cargo_piloto.json → ocupante_atual)
  memoria_de_erros ..... o que o ocupante errou, virando instrução para a rodada seguinte.
                         É assim que ele evolui sem trocar de modelo: cada falso positivo,
                         falso negativo e resposta fora do esquema vira um exemplo curto que
                         entra no prompt como "erros a não repetir".
  avaliar_candidato() .. mede um reserva contra o gabarito e, se bater o ocupante nas métricas
                         do critério, faz a troca sozinho — sem tocar em mais nada do sistema.

ESCOPO (decisão do titular, 22/09/2026): o Piloto é SNIPER DE OPORTUNIDADES. Encontra, valida,
cataloga, descobre onde e quando se publica, e afia os motores. NÃO interpreta edital para
elaborar projeto nem redige documentos de inscrição — isso saiu do cargo.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json

CARGO = ROOT / "config/cargo_piloto.json"
MEM = ROOT / "estado/piloto/memoria_erros.json"
MAX_NO_PROMPT = 12


def pode_assumir(candidato: dict) -> tuple[bool, str]:
    """O CARGO NÃO ACEITA REPROVADO.

    CORREÇÃO DO REGISTRO (23/09): escrevi antes que o Llama-3.2-3B fora nomeado sem passar no
    benchmark. Errado, e a verdade importa. Ele VENCEU o benchmark 1, em 21/09: acerto 0,597,
    zero prazos inventados, 16 tokens/s — acima dos 50% exigidos e o mais rápido. A nomeação
    foi legítima.

    O que aconteceu foi outra coisa, e pior: no benchmark 2, em 22/09, ele caiu para 0,342 —
    abaixo do critério do próprio cargo — e NINGUÉM O TIROU. Ficou mais um dia e meio no
    posto, respondendo a 12% dos pedidos em voo. O buraco não era nomear reprovado: era não
    ter regra para demitir quem deixa de cumprir o critério depois de nomeado.
    """
    return _pode(candidato)


def _pode(candidato: dict) -> tuple[bool, str]:
    """Critério de entrada.

    Daqui em diante, ocupante não elegível não entra: o cargo fica VAGO e o Piloto voa com a
    rede determinística, que sorteia o rumo do catálogo sem repetir. Voar sem modelo é pior
    que voar com um bom modelo, mas melhor que voar com um que não responde — porque assim o
    vazio fica visível, em vez de disfarçado de inteligência.
    """
    if not candidato:
        return False, "sem candidato"
    if candidato.get("eliminado_por"):
        return False, f"eliminado em prova decisiva: {', '.join(candidato['eliminado_por'])}"
    if candidato.get("nao_provou"):
        return False, f"não provou nas eliminatórias: {', '.join(candidato['nao_provou'])}"
    if not candidato.get("elegivel"):
        return False, "reprovado na trilha do cargo"
    if (candidato.get("taxa_de_resposta") or 0) < 0.5:
        return False, f"responde a {candidato['taxa_de_resposta']:.0%} dos pedidos, abaixo dos 50%"
    return True, f"elegível: nota {candidato.get('nota')}, responde a {candidato['taxa_de_resposta']:.0%}"


def deve_sair(medida: dict | None = None) -> tuple[bool, str]:
    """A REGRA QUE FALTAVA: quem deixa de cumprir o critério, sai.

    Entrar no cargo tinha critério; permanecer, não. Foi por isso que um ocupante medido em
    0,342 (abaixo dos 50%) seguiu voando por um dia e meio depois da medição que o reprovou.
    Agora a permanência é verificada a cada avaliação e a cada 10 briefings em voo.
    """
    c = load_json(CARGO) if CARGO.exists() else {}
    o = c.get("ocupante_atual") or {}
    if not o.get("nome"):
        return False, "cargo já está vago"
    d = o.get("desempenho_em_voo") or {}
    if d.get("pedidos", 0) >= 10 and d.get("taxa_de_resposta", 1) < 0.5:
        return True, (f"responde a {d['taxa_de_resposta']:.0%} dos pedidos em voo, "
                      f"abaixo dos 50% que o cargo exige ({d['pedidos']} pedidos medidos)")
    m = medida or o.get("desempenho") or {}
    if m.get("prazos_inventados", 0) > 0:
        return True, f"inventou {m['prazos_inventados']} prazo(s): falta eliminatória"
    if m and (m.get("acerto") is not None) and m["acerto"] < 0.5:
        return True, f"acerto caiu para {m['acerto']:.1%}, abaixo dos 50% exigidos"
    return False, "cumpre o critério"


def cargo_vago(motivo: str) -> dict:
    """Declara o posto vago e registra por quê, para que ninguém o preencha por inércia."""
    c = load_json(CARGO) if CARGO.exists() else {}
    anterior = (c.get("ocupante_atual") or {}).get("nome")
    c["ocupante_atual"] = {"nome": None, "vago": True, "desde": now_iso()[:16], "motivo": motivo,
                           "anterior": anterior,
                           "como_o_piloto_voa": "rede determinística: rumo sorteado do catálogo de "
                                                "ângulos, sem repetir os últimos. O voo perde a "
                                                "leitura da página, não a direção."}
    write_json(CARGO, c)
    return c["ocupante_atual"]


def cargo() -> dict:
    return load_json(CARGO)


def ocupante() -> dict:
    return cargo()["ocupante_atual"]


def criterio() -> dict:
    return cargo()["criterio_de_contratacao"]


# ───────────────────────────────────────────────── memória de erros (a evolução)
def registrar_erro(tipo: str, titulo: str, esperado: str, veio: str, licao: str = "") -> None:
    """tipo: falso_positivo | falso_negativo | fora_do_esquema | trecho_inexistente"""
    m = load_json(MEM) if MEM.exists() else {"erros": {}, "atualizado_em": None, "total": 0}
    chave = f"{tipo}|{(titulo or '')[:60].lower()}"
    e = m["erros"].setdefault(chave, {"tipo": tipo, "exemplo": (titulo or "")[:110], "esperado": esperado, "veio": veio, "n": 0, "licao": licao})
    e["n"] += 1
    if licao:
        e["licao"] = licao
    m["total"] = sum(x["n"] for x in m["erros"].values())
    m["atualizado_em"] = now_iso()
    MEM.parent.mkdir(parents=True, exist_ok=True)
    write_json(MEM, m)


def licoes_para_o_prompt(n: int = MAX_NO_PROMPT) -> str:
    """As lições mais frequentes viram texto curto no prompt da próxima rodada."""
    if not MEM.exists():
        return ""
    m = load_json(MEM)
    top = sorted(m.get("erros", {}).values(), key=lambda e: -e["n"])[:n]
    if not top:
        return ""
    linhas = []
    for e in top:
        if e["tipo"] == "falso_positivo":
            linhas.append(f'- "{e["exemplo"]}" NÃO é fomento a OSC (você já errou {e["n"]}x): {e.get("licao") or "leia o objeto, não o título"}')
        elif e["tipo"] == "falso_negativo":
            linhas.append(f'- "{e["exemplo"]}" É fomento a OSC (você já errou {e["n"]}x): {e.get("licao") or "chamamento com termo de fomento/colaboração conta"}')
        elif e["tipo"] == "fora_do_esquema":
            linhas.append(f'- responda SÓ o JSON pedido; você saiu do esquema {e["n"]}x')
        else:
            linhas.append(f'- cite trecho que EXISTE no texto; você citou frase inexistente {e["n"]}x')
    return "ERROS A NÃO REPETIR (medidos nas rodadas anteriores):\n" + "\n".join(linhas)


def estatistica() -> dict:
    if not MEM.exists():
        return {"total": 0, "por_tipo": {}}
    m = load_json(MEM)
    por = {}
    for e in m.get("erros", {}).values():
        por[e["tipo"]] = por.get(e["tipo"], 0) + e["n"]
    return {"total": m.get("total", 0), "por_tipo": por, "distintos": len(m.get("erros", {})), "atualizado_em": m.get("atualizado_em")}


# ───────────────────────────────────────────────── contratação e demissão
def aprovado_no_criterio(r: dict) -> tuple[bool, str]:
    c = criterio()
    if (r.get("prazos_inventados") or 0) > 0:
        return False, f"inventou {r['prazos_inventados']} prazo(s) — eliminatório"
    if (r.get("acerto") or 0) < c["assertividade_minima"]:
        return False, f"acerto {r.get('acerto')} abaixo do mínimo {c['assertividade_minima']}"
    if r.get("falso_positivo") is not None and r["falso_positivo"] > c["falso_positivo_maximo"]:
        return False, f"falso positivo {r['falso_positivo']} acima de {c['falso_positivo_maximo']}"
    if (r.get("gb") or 0) > c["tamanho_maximo_gb"]:
        return False, f"{r.get('gb')} GB acima do limite {c['tamanho_maximo_gb']}"
    if (r.get("tokens_por_s") or 0) < c["velocidade_minima_tokens_s"]:
        return False, f"{r.get('tokens_por_s')} tok/s abaixo de {c['velocidade_minima_tokens_s']}"
    return True, "cumpre o critério"


def trocar_ocupante(novo: dict, resultado: dict, motivo: str) -> dict:
    """A troca é UMA escrita em config/cargo_piloto.json. Nada mais do sistema muda."""
    c = cargo()
    antigo = c["ocupante_atual"]
    c.setdefault("ex_ocupantes", []).insert(0, {**antigo, "demitido_em": date.today().isoformat(), "motivo_da_demissao": motivo})
    c["ocupante_atual"] = {"id": novo["id"], "nome": novo["nome"], "arquivo": novo.get("arquivo") or novo["url"].split("/")[-1],
                           "url": novo["url"], "gb": novo.get("gb"), "licenca": novo.get("licenca"),
                           "contratado_em": date.today().isoformat(), "medido_em": f"avaliação de {date.today().isoformat()}",
                           "desempenho": {k: resultado.get(k) for k in ("acerto", "prazos_inventados", "falso_positivo", "tokens_por_s", "minutos")},
                           "por_que": motivo}
    c["atualizado_em"] = date.today().isoformat()
    write_json(CARGO, c)
    # o config operacional aponta para o novo arquivo — é o que o workflow baixa
    op = ROOT / "config/piloto.json"
    s = load_json(op) if op.exists() else {}
    s.update({"modelo_vencedor": novo["id"], "arquivo": c["ocupante_atual"]["arquivo"], "url": novo["url"],
              "eleito_em": now_iso(), "benchmark": motivo})
    write_json(op, s)
    return {"demitido": antigo["id"], "contratado": novo["id"], "motivo": motivo}


def avaliar_candidato(cand_id: str, limite: int = 120, porta: int = 8082) -> dict:
    """Mede um reserva contra o gabarito; troca se for melhor que o ocupante."""
    from .piloto import gabarito, avaliar_modelo
    c = cargo()
    cand = next((x for x in c["banco_de_reserva"] if x["id"] == cand_id), None)
    if not cand:
        return {"erro": f"{cand_id} não está no banco de reserva"}
    cand = {**cand, "arquivo": cand.get("arquivo") or cand["url"].split("/")[-1]}
    r = avaliar_modelo(cand, gabarito(limite), porta)
    ok, porque = aprovado_no_criterio(r)
    atual = ocupante().get("desempenho") or {}
    melhor = ok and (r.get("acerto") or 0) > (atual.get("acerto") or 0)
    saida = {"em": now_iso(), "candidato": cand_id, "resultado": {k: r.get(k) for k in ("acerto", "prazos_inventados", "falso_positivo", "falso_negativo", "tokens_por_s", "minutos", "itens", "erro")},
             "cumpre_criterio": ok, "porque": porque, "melhor_que_o_ocupante": melhor,
             "ocupante_hoje": {"id": ocupante()["id"], "acerto": atual.get("acerto")}}
    if melhor:
        saida["troca"] = trocar_ocupante(cand, r, f"{cand['nome']}: acerto {r.get('acerto')} contra {atual.get('acerto')} do ocupante, {r.get('tokens_por_s')} tok/s, {cand.get('gb')} GB")
    write_json(ROOT / "estado/piloto" / f"avaliacao-{cand_id}-{date.today().isoformat()}.json", saida)
    return saida


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == "avaliar":
        print(json.dumps(avaliar_candidato(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 120), ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"ocupante": ocupante(), "criterio": criterio(), "reservas": [r["id"] for r in cargo()["banco_de_reserva"]],
                          "memoria_de_erros": estatistica(), "escopo_nao_faz": cargo()["escopo"]["nao_faz"]}, ensure_ascii=False, indent=2))
