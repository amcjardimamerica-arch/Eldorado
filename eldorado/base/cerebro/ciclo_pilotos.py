"""O ciclo de aprendizado dos pilotos a cada 100 (titular, 29/09/2026, no Eldorado0: «a cada 100 erros, parâmetros de
busca melhores»; «estratégia nova a cada 100 pesquisas»). Refeito em 06/11/2026: o sistema novo não o tinha.

O defeito que o ciclo corrige: o Espião (a amostragem de Thompson das famílias) e a política do Comandante aprendiam com
os ACHADOS da missão — os candidatos que passavam pelo crivo do próprio Espião —, não com o resultado REAL. A família
«internacional_espanhol» acumulou 2.499 «achados» em 3.219 usos e passou a dominar, enquanto a precisão real do Espião
era de 15% (os vereditos do Claude no Chrome).

A cada 100 missões do Espião, o ciclo:
  - mede o resultado real de cada família e de cada consulta (o livro que nasceu do achado: ACERTO se o Chrome o
    confirmou — válido, encerrada, arquivar — ou se chegou ao Farol; ERRO se foi descartado ou expurgado);
  - dá a cada família o FATOR REAL (a taxa de acerto real dela contra a média), que o Comandante e o Espião passam a
    multiplicar na escolha da família;
  - aposenta as consultas que só trouxeram erro (3 ou mais erros reais e nenhum acerto).
A cada 100 erros do Interceptador (a tentativa sem nenhum item aceito), o ciclo:
  - mede a taxa de cada abordagem (itens aceitos por tentativa) e a ordem que mais rende;
  - grava essa ordem como a preferência do plano de voo, quando a rede não der a dela.
Cada ciclo fica no Cérebro (medicao, marcador «ciclo:espiao» / «ciclo:interceptador», o valor = a contagem no ciclo, o
motivo = as orientações em JSON) e vira uma lição do Aprendizado para o Comandante.
"""
from __future__ import annotations

import json
import sqlite3
from collections import defaultdict
from pathlib import Path
from typing import Any

from ..nucleo.eventos import agora

A_CADA = 100
RAIZ = Path(__file__).resolve().parents[3]


def resultado_real(bib: sqlite3.Connection, raiz: Path = RAIZ) -> dict[str, str]:
    """livro → «acerto» ou «erro» (a mesma régua da pontuação dos motores); os livros em curso ficam de fora."""
    from .pontuacao_motores import REAIS, _vereditos
    ver = _vereditos(raiz)
    out = {}
    for lid, sit, fase in bib.execute("SELECT l.id, l.situacao, p.fase FROM livro l LEFT JOIN passaporte p ON p.livro_id = l.id"):
        dec = (ver.get(lid) or (None,))[0]
        if dec in REAIS or (dec is None and fase == "farol" and sit not in ("excluido", "unido")):
            out[lid] = "acerto"
        elif dec == "descartar" or (dec is None and sit == "excluido"):
            out[lid] = "erro"
    return out


def avaliar_espiao(bib: sqlite3.Connection, cer: sqlite3.Connection, raiz: Path = RAIZ) -> dict[str, Any]:
    real = resultado_real(bib, raiz)
    fam: dict[str, dict] = defaultdict(lambda: {"livros": 0, "acertos": 0, "erros": 0})
    cons: dict[str, dict] = defaultdict(lambda: {"familia": "", "acertos": 0, "erros": 0})
    for dados, lid in bib.execute("SELECT dados, livro_id FROM achado WHERE motor = 'espiao' AND livro_id IS NOT NULL"):
        try:
            d = json.loads(dados or "{}")
        except ValueError:
            continue
        f, q, r = d.get("familia") or "outros", d.get("consulta") or "", real.get(lid)
        fam[f]["livros"] += 1
        if r:
            fam[f][r + "s"] += 1
            if q:
                cons[q]["familia"] = f
                cons[q][r + "s"] += 1
    usos = {n: (u or 0, a or 0) for n, u, a in cer.execute("SELECT nome, usos, achados FROM espiao_familia")}
    tot_a = sum(x["acertos"] for x in fam.values())
    tot_d = sum(x["acertos"] + x["erros"] for x in fam.values())
    media = (tot_a + 1) / (tot_d + 2)
    familias = {}
    for f in set(fam) | set(usos):
        x = fam[f]
        taxa = (x["acertos"] + 1) / (x["acertos"] + x["erros"] + 2)            # a taxa real (com o anteparo de Laplace)
        familias[f] = {**x, "missoes": usos.get(f, (0, 0))[0], "candidatos": usos.get(f, (0, 0))[1],
                       "taxa_real": round(taxa, 3), "fator_real": round(min(3.0, max(0.1, taxa / media)), 3)}
    aposentar = sorted(q for q, x in cons.items() if x["erros"] >= 3 and not x["acertos"])
    ordem = sorted(familias, key=lambda f: -familias[f]["fator_real"])
    return {"familias": familias, "media_real": round(media, 3), "aposentar": aposentar,
            "preferir": [f for f in ordem if familias[f]["fator_real"] >= 1.2][:5],
            "evitar": [f for f in ordem if familias[f]["fator_real"] <= 0.6 and familias[f]["acertos"] + familias[f]["erros"] >= 5]}


def avaliar_interceptador(bib: sqlite3.Connection) -> dict[str, Any]:
    ab: dict[str, dict] = defaultdict(lambda: {"tentativas": 0, "erros": 0, "aceitos": 0})
    erros = 0
    for ferr, res in bib.execute("SELECT ferramenta, resultado FROM tentativa"):
        try:
            d = json.loads(res or "{}")
        except ValueError:
            d = {}
        n = (d.get("ia") or {}).get("aceitas")
        if not isinstance(n, (int, float)):            # a tentativa de um motor registra «trouxe» (e não «aceitas»)
            n = int(bool(d.get("trouxe") or d.get("obtidos")))
        k = str(ferr or "?")
        ab[k]["tentativas"] += 1
        ab[k]["aceitos"] += n
        if not n:
            ab[k]["erros"] += 1
            erros += 1
    for x in ab.values():
        x["rendimento"] = round(x["aceitos"] / x["tentativas"], 3) if x["tentativas"] else 0.0
    ordem = [k for k, _ in sorted(ab.items(), key=lambda kv: -kv[1]["rendimento"])]
    numeros = []
    for k in ordem:
        try:
            numeros.append(int(str(k).split()[-1]))
        except ValueError:
            continue
    return {"abordagens": dict(ab), "erros": erros, "ordem": ordem, "preferencia": numeros}


def ultimo(cer: sqlite3.Connection, piloto: str) -> tuple[float, dict]:
    try:
        r = cer.execute("SELECT valor, motivo FROM medicao WHERE marcador = ? ORDER BY em DESC LIMIT 1", (f"ciclo:{piloto}",)).fetchone()
    except sqlite3.Error:
        return 0.0, {}
    if not r:
        return 0.0, {}
    try:
        return float(r[0] or 0), json.loads(r[1] or "{}")
    except (TypeError, ValueError):
        return float(r[0] or 0), {}


def ciclo(bib: sqlite3.Connection, cer: sqlite3.Connection, diario, raiz: Path = RAIZ, a_cada: int = A_CADA) -> dict[str, Any]:
    """Roda o ciclo do piloto que passou de mais 100 (missões do Espião; erros do Interceptador) desde o último."""
    from .aprendizado import Aprendizado
    feito: dict[str, Any] = {}
    missoes = cer.execute("SELECT COUNT(*) FROM espiao_missao").fetchone()[0] or 0
    ult_m, _ = ultimo(cer, "espiao")
    if missoes - ult_m >= a_cada:
        av = avaliar_espiao(bib, cer, raiz)
        for q in av["aposentar"]:                      # a consulta que só trouxe erro real sai do rodízio (usos ≥ 3, achados 0)
            diario.emitir("espiao.consulta", "ciclo-pilotos", {"texto": q, "usos": 99, "achados": 0, "ultima": agora()})
        orient = {"fatores": {f: x["fator_real"] for f, x in av["familias"].items()}, "preferir": av["preferir"], "evitar": av["evitar"],
                  "aposentadas": len(av["aposentar"]), "media_real": av["media_real"]}
        diario.emitir("medicao.registrada", "ciclo-pilotos", {"marcador": "ciclo:espiao", "nivel": "aprendizado", "em": agora(),
                                                              "valor": missoes, "motivo": json.dumps(orient, ensure_ascii=False)})
        Aprendizado(diario).registrar("comandante", f"Espião (ciclo de {a_cada} missões, {missoes} no total): preferir {', '.join(av['preferir']) or '—'}; "
                                      f"evitar {', '.join(av['evitar']) or '—'}; {len(av['aposentar'])} consulta(s) aposentada(s) por só trazer erro real",
                                      json.dumps(av["familias"], ensure_ascii=False)[:4000])
        feito["espiao"] = orient
    ai = avaliar_interceptador(bib)
    ult_e, _ = ultimo(cer, "interceptador")
    if ai["erros"] - ult_e >= a_cada:
        orient = {"preferencia": ai["preferencia"], "ordem": ai["ordem"],
                  "rendimento": {k: x["rendimento"] for k, x in ai["abordagens"].items()}}
        diario.emitir("medicao.registrada", "ciclo-pilotos", {"marcador": "ciclo:interceptador", "nivel": "aprendizado", "em": agora(),
                                                              "valor": ai["erros"], "motivo": json.dumps(orient, ensure_ascii=False)})
        Aprendizado(diario).registrar("comandante", f"Interceptador (ciclo de {a_cada} erros, {ai['erros']} no total): a ordem das abordagens "
                                      f"pelo rendimento real — {', '.join(ai['ordem'][:6])}", json.dumps(ai["abordagens"], ensure_ascii=False)[:4000])
        feito["interceptador"] = orient
    return feito


def fator_familia(cer: sqlite3.Connection, familia: str) -> float:
    """O fator real da família pelo último ciclo (1 sem ciclo)."""
    return float((ultimo(cer, "espiao")[1].get("fatores") or {}).get(familia, 1.0))


def preferencia_interceptador(cer: sqlite3.Connection) -> list[int] | None:
    return (ultimo(cer, "interceptador")[1].get("preferencia")) or None
