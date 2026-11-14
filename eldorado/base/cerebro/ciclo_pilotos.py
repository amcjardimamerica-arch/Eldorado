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


def avaliar_interceptador(bib: sqlite3.Connection, desde: str = "") -> dict[str, Any]:
    ab: dict[str, dict] = defaultdict(lambda: {"tentativas": 0, "erros": 0, "aceitos": 0})
    erros = 0
    try:                                              # desde o reset (R55); o banco sem a data conta todas
        linhas = bib.execute("SELECT ferramenta, resultado FROM tentativa WHERE COALESCE(em, '') >= ?", (desde,)).fetchall()
    except sqlite3.OperationalError:
        linhas = bib.execute("SELECT ferramenta, resultado FROM tentativa").fetchall()
    for ferr, res in linhas:
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


RESET = "R55"   # 14/11/2026 (titular): o reset das missões dos pilotos depois das correções das rotas


def marca_reset(cer: sqlite3.Connection) -> str:
    """O instante do reset (R55) — as contagens dos ciclos começam dele; "" se ainda não houve."""
    try:
        r = cer.execute("SELECT MAX(em) FROM medicao WHERE marcador = 'ciclo:reset'").fetchone()
        return (r[0] or "") if r else ""
    except sqlite3.Error:
        return ""


def resetar(cer: sqlite3.Connection, diario) -> bool:
    """14/11/2026 (titular: «faça o reset nas missões dos pilotos»): uma vez, na primeira passagem com as correções das
    rotas (R55) — as crenças das famílias voltam ao começo (a=1, b=1), as consultas aposentadas com a ferramenta quebrada
    voltam ao rodízio, o fator real volta a 1, a preferência do Interceptador é zerada e os ciclos contam a partir daqui.
    Nada é apagado: é a marca «ciclo:reset» e os eventos de cada estado novo."""
    if marca_reset(cer):
        return False
    em = agora()
    try:
        for (nome,) in cer.execute("SELECT nome FROM espiao_familia").fetchall():
            diario.emitir("espiao.familia", "ciclo-pilotos", {"nome": nome, "a": 1.0, "b": 1.0, "usos": 0, "achados": 0})
        for q, fam in cer.execute("SELECT texto, familia FROM espiao_consulta WHERE usos >= 3 AND achados = 0").fetchall():
            diario.emitir("espiao.consulta", "ciclo-pilotos", {"texto": q, "familia": fam, "usos": 0, "achados": 0, "ultima": em})
    except sqlite3.Error:
        pass                                                          # o Cérebro ainda sem as tabelas do Espião: só a marca
    for pil in ("espiao", "interceptador"):
        diario.emitir("medicao.registrada", "ciclo-pilotos", {"marcador": f"ciclo:{pil}", "nivel": "componente", "em": em, "valor": 0,
                                                              "motivo": json.dumps({"reset": RESET, "fatores": {}, "preferencia": None})})
    diario.emitir("medicao.registrada", "ciclo-pilotos", {"marcador": "ciclo:reset", "nivel": "componente", "em": em, "valor": 0,
                                                          "motivo": json.dumps({"regra": RESET, "o_que": "reset das missões dos pilotos"})})
    return True


def aprendizado_novo(cer: sqlite3.Connection, bib: sqlite3.Connection, desde: str) -> dict[str, Any]:
    """O que o ciclo traz além da R47 (titular, 14/11/2026: «veja a cada 100 missões se é possível trazer algum aprendizado
    além dos que foram colocados no relatório»): o placar das rotas, as missões sem pista, os motivos de descarte, as
    listagens abertas, a varredura do cadastro — e quais critérios de aceite do parecer de rotas ainda não foram atingidos."""
    from .relatorio_turno import medir
    vazio = {"sem_pista_pct": None, "rotas_respondendo": 0, "rota_maior_parte_pct": None, "placar": {}, "motivos": {},
             "listagens_abertas": 0, "varreduras": 0, "achados_da_varredura": 0, "aceitos": None, "falta_no_aceite": []}
    try:
        r = medir(cer, bib, desde)
        linhas = cer.execute("SELECT familia, motivos, achados FROM espiao_missao WHERE em >= ?", (desde,)).fetchall()
    except sqlite3.Error:                             # o Cérebro sem as colunas das missões: só as medidas da R47
        return vazio
    motivos: dict[str, int] = defaultdict(int)
    varreduras = [0, 0]
    for fam, mot, ach in linhas:
        for k, v in json.loads(mot or "{}").items():
            motivos[k] += int(v or 0)
        if fam == "camada1_cadastro":
            varreduras[0] += 1
            varreduras[1] += ach or 0
    falta = []
    if r["sem_pista_pct"] is not None and r["sem_pista_pct"] >= 5:
        falta.append(f"missões sem pista {r['sem_pista_pct']}% (alvo < 5%)")
    if r["rota_maior_parte_pct"] is not None and r["rota_maior_parte_pct"] > 50:
        falta.append(f"uma rota com {r['rota_maior_parte_pct']}% das pistas (alvo ≤ 50%)")
    if r["rotas_respondendo"] < 5:
        falta.append(f"{r['rotas_respondendo']} rota(s) respondendo (alvo ≥ 5)")
    if r["pncp_nas_missoes"]:
        falta.append(f"a rota do PNCP em {r['pncp_nas_missoes']} missão(ões) (alvo 0)")
    return {"sem_pista_pct": r["sem_pista_pct"], "rotas_respondendo": r["rotas_respondendo"], "rota_maior_parte_pct": r["rota_maior_parte_pct"],
            "placar": r["placar"], "motivos": dict(sorted(motivos.items(), key=lambda kv: -kv[1])[:8]),
            "listagens_abertas": motivos.get("listagem aberta", 0), "varreduras": varreduras[0], "achados_da_varredura": varreduras[1],
            "aceitos": r["aceitos"], "falta_no_aceite": falta}


def ciclo(bib: sqlite3.Connection, cer: sqlite3.Connection, diario, raiz: Path = RAIZ, a_cada: int = A_CADA) -> dict[str, Any]:
    """Roda o ciclo do piloto que passou de mais 100 (missões do Espião; erros do Interceptador) desde o último — contados a
    partir do reset (R55)."""
    from .aprendizado import Aprendizado
    feito: dict[str, Any] = {}
    if resetar(cer, diario):
        return {"reset": RESET}
    desde = marca_reset(cer)
    try:                                              # desde o reset (R55); o banco sem a data conta todas
        missoes = cer.execute("SELECT COUNT(*) FROM espiao_missao WHERE em >= ?", (desde,)).fetchone()[0] or 0
    except sqlite3.OperationalError:
        missoes = cer.execute("SELECT COUNT(*) FROM espiao_missao").fetchone()[0] or 0
    ult_m, ult_o = ultimo(cer, "espiao")
    ult_em = ult_o.get("em") or desde
    if missoes - ult_m >= a_cada:
        av = avaliar_espiao(bib, cer, raiz)
        for q in av["aposentar"]:                      # a consulta que só trouxe erro real sai do rodízio (usos ≥ 3, achados 0)
            diario.emitir("espiao.consulta", "ciclo-pilotos", {"texto": q, "usos": 99, "achados": 0, "ultima": agora()})
        novo = aprendizado_novo(cer, bib, ult_em)
        orient = {"fatores": {f: x["fator_real"] for f, x in av["familias"].items()}, "preferir": av["preferir"], "evitar": av["evitar"],
                  "aposentadas": len(av["aposentar"]), "media_real": av["media_real"], "em": agora(), "novo": novo}
        diario.emitir("medicao.registrada", "ciclo-pilotos", {"marcador": "ciclo:espiao", "nivel": "componente", "em": agora(),
                                                              "valor": missoes, "motivo": json.dumps(orient, ensure_ascii=False)})
        falta = "; ".join(novo["falta_no_aceite"]) or "nada — o aceite atingido"
        licao = (f"Espião (ciclo de {a_cada} missões, {missoes} desde o reset): preferir {', '.join(av['preferir']) or '—'}; "
                 f"evitar {', '.join(av['evitar']) or '—'}; {len(av['aposentar'])} consulta(s) aposentada(s) por só trazer erro real; "
                 f"{novo['sem_pista_pct']}% sem pista, {novo['rotas_respondendo']} rota(s) respondendo, {novo['listagens_abertas']} "
                 f"listagem(ns) aberta(s), {novo['varreduras']} varredura(s) do cadastro ({novo['achados_da_varredura']} achado(s)); "
                 f"ainda falta: {falta}")
        Aprendizado(diario).registrar("comandante", licao, json.dumps({"familias": av["familias"], "novo": novo}, ensure_ascii=False)[:4000])
        feito["espiao"] = orient
    ai = avaliar_interceptador(bib, desde)
    ult_e, _ = ultimo(cer, "interceptador")
    if ai["erros"] - ult_e >= a_cada:
        orient = {"preferencia": ai["preferencia"], "ordem": ai["ordem"],
                  "rendimento": {k: x["rendimento"] for k, x in ai["abordagens"].items()}}
        diario.emitir("medicao.registrada", "ciclo-pilotos", {"marcador": "ciclo:interceptador", "nivel": "componente", "em": agora(),
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
