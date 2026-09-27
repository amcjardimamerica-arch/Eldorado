"""PONTUAÇÃO DAS EMPRESAS PELA DOAÇÃO (titular, 26/09).

Cada recurso que a empresa destina conta ponto; os 100 pontos são redistribuídos pelo que se comprova em fonte
oficial; doar em ANOS SEGUIDOS dá BÔNUS acima de 100 — sinal de que a empresa tem a parte social resolvida
por dentro (orçamento, rito, gente que cuida). E a nota define a HIERARQUIA.

    base (até 100)
      Recursos destinados ........ 30 pelo primeiro mecanismo com destinação verificada nos últimos 5 anos
                                   (Rouanet, Goyazes, Esporte, FIA, Idoso, PRONON, PRONAS) e +15 por mecanismo
                                   adicional — até 60 (só o total histórico da Rouanet, sem anos: 10)
      Volume ..................... pela ordem de grandeza do que destinou em 5 anos — até 20
      Frequência ................. número de doações/projetos em 5 anos — até 15
      Goiás ...................... sede em Goiás 4 + destinou a projeto em Goiás 6 — até 10
      Lucro Real confirmado ...... doou por incentivo = Lucro Real no ano (Lei 8.313/91, art. 26) — 5
      Canal ...................... GIFE, patrocínio observado pelos motores, programa social próprio — até 5
    bônus (acima de 100)
      Anos seguidos .............. +4 por ano consecutivo a partir do 2º na maior sequência — até +20
      Vários recursos no mesmo ano +5
    hierarquia
      Parceira social ≥ 100 · Destinadora ativa 70–99 · Destinadora eventual 45–69 · Potencial 25–44 · A prospectar < 25
"""
from __future__ import annotations

import math
from datetime import date

JANELA_DESDE = date.today().year - 5
NIVEIS = [(100, "Parceira social", "doa todo ano, por mais de um caminho: a parte social já é rotina da empresa"),
          (70, "Destinadora ativa", "destina com frequência e volume comprovados"),
          (45, "Destinadora eventual", "já destinou, sem regularidade"),
          (25, "Potencial", "tem perfil e algum sinal, falta a destinação recente comprovada"),
          (0, "A prospectar", "sem destinação comprovada: prospecção desde o começo")]
MECANISMOS_DOACAO = ("Rouanet", "Goyazes", "LIE", "Esporte", "FIA", "Fundo do Idoso", "Idoso", "PRONON", "PRONAS/PCD", "PRONAS")


def _volume(valor: float) -> int:
    if valor <= 0:
        return 0
    return max(0, min(20, int(4 * (math.log10(valor) - 3))))     # 10 mil → 4 · 100 mil → 8 · 1 mi → 12 · 10 mi → 16 · 100 mi → 20


def _freq(n: int) -> int:
    for lim, p in ((20, 15), (10, 12), (6, 9), (3, 6), (1, 3)):
        if n >= lim:
            return p
    return 0


def _maior_sequencia(anos: set[int]) -> int:
    melhor = atual = 0; ant = None
    for a in sorted(anos):
        atual = atual + 1 if ant is not None and a == ant + 1 else 1
        melhor = max(melhor, atual); ant = a
    return melhor


def nivel(pontos: float) -> dict:
    for lim, nome, porque in NIVEIS:
        if pontos >= lim:
            return {"nivel": nome, "porque": porque, "ordem": NIVEIS.index((lim, nome, porque)) + 1}
    return {"nivel": "A prospectar", "porque": NIVEIS[-1][2], "ordem": 5}


def pontuar(e: dict) -> dict:
    iv = e.get("incentivos_verificados") or {}
    mec = iv.get("mecanismos") or {}
    sal = e.get("salic") or {}
    comp, prova = {}, []
    anos_por_mec: dict[str, set[int]] = {}
    valor5 = 0.0; n5 = 0
    # Rouanet
    r = mec.get("Rouanet") or {}
    u5 = r.get("ultimos_5_anos") or {}
    if r.get("status") == "destinou" and u5.get("doacoes"):
        anos_por_mec["Rouanet"] = {int(a) for a in (u5.get("anos") or []) if str(a).isdigit()}
        valor5 += float(u5.get("valor") or 0); n5 += int(u5.get("doacoes") or 0)
        prova.append(f"Rouanet: {u5.get('doacoes')} doação(ões) em {', '.join(u5.get('anos') or [])}")
    elif sal.get("anos"):
        anos_por_mec["Rouanet"] = {int(a) for a in sal["anos"] if str(a).isdigit() and int(a) >= JANELA_DESDE}
    # Goyazes
    g = mec.get("Goyazes") or {}
    if g.get("status") == "destinou":
        pa = g.get("por_ano") or {}
        anos_por_mec["Goyazes"] = {int(a) for a in pa if str(a).isdigit()}
        valor5 += sum(float(v.get("valor_projetos") or 0) for v in pa.values()); n5 += sum(int(v.get("projetos") or 0) for v in pa.values())
        prova.append(f"Goyazes: {sum(int(v.get('projetos') or 0) for v in pa.values())} projeto(s) em {', '.join(sorted(pa))}")
    # os demais mecanismos, quando houver destinação verificada
    for m in MECANISMOS_DOACAO:
        if m in ("Rouanet", "Goyazes"):
            continue
        x = mec.get(m) or {}
        if x.get("status") == "destinou":
            anos = {int(a) for a in (x.get("anos") or (x.get("ultimos_5_anos") or {}).get("anos") or []) if str(a).isdigit()}
            anos_por_mec[m] = anos or {date.today().year}
            valor5 += float(x.get("valor") or (x.get("ultimos_5_anos") or {}).get("valor") or 0); n5 += int(x.get("doacoes") or 1)
            prova.append(f"{m}: destinou")
    janela = {m: {a for a in s if a >= JANELA_DESDE} for m, s in anos_por_mec.items()}
    com_janela = [m for m, s in janela.items() if s]
    # 1) recursos destinados
    if com_janela:
        comp["recursos"] = min(60, 30 + 15 * (len(com_janela) - 1))
    elif sal.get("total") or (r.get("status") == "destinou"):
        comp["recursos"] = 10; prova.append("Rouanet: destinou (total histórico, sem os anos)")
    else:
        comp["recursos"] = 0
    # 2) volume e 3) frequência
    if valor5 <= 0 and sal.get("total"):
        comp["volume"] = _volume(float(sal["total"])) // 2
    else:
        comp["volume"] = _volume(valor5)
    comp["frequencia"] = _freq(n5)
    # 4) Goiás
    uf = str((e.get("cadastro") or {}).get("uf") or e.get("uf") or "").upper()
    go = 4 if uf == "GO" or e.get("icms_goias") else 0
    if janela.get("Goyazes") or (sal.get("destino") or {}).get("GO"):
        go += 6
    comp["goias"] = go
    # 5) Lucro Real confirmado
    lr = (iv.get("lucro_real") or {}).get("classe") == "confirmado" or bool(com_janela and "Rouanet" in com_janela) or bool(sal.get("total"))
    comp["lucro_real"] = 5 if lr else 0
    # 6) canal
    comp["canal"] = min(5, (2 if e.get("gife") else 0) + (2 if e.get("observado_pelo_motor") else 0) + (1 if e.get("programa") else 0))
    base = min(100, sum(comp.values()))
    # bônus
    todos = set().union(*janela.values()) if janela else set()
    seq = _maior_sequencia(todos)
    b_seq = min(20, 4 * max(0, seq - 1))
    ano_multi = any(sum(1 for s in janela.values() if a in s) >= 2 for a in todos)
    b_multi = 5 if ano_multi else 0
    bonus = b_seq + b_multi
    total = base + bonus
    return {"pontos": total, "base": base, "bonus": bonus, "componentes": comp,
            "bonus_detalhe": {"anos_seguidos": seq, "pontos_anos_seguidos": b_seq, "varios_recursos_no_mesmo_ano": ano_multi, "pontos_varios_recursos": b_multi},
            "recursos_na_janela": com_janela, "anos_com_doacao": sorted(todos), "prova": prova, **nivel(total)}
