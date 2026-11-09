"""A pontuação de cada motor (titular, 05/11/2026): os acertos parametrizados com os erros, para a melhoria do motor.

Os parâmetros estão em config/pontuacao_motores.toml. Para cada livro, o motor que o encontrou primeiro (o achado mais
antigo) recebe o resultado: ACERTO se é oportunidade real (o veredito do Claude no Chrome «valido», «encerrada» ou
«arquivar», ou o livro no Farol); ERRO se não era (o veredito «descartar», ou o expurgo pelo sistema); os demais estão em
andamento. A nota soma a precisão, o rendimento, o local da pesca e a saúde (os sinais da Bússola), pelos pesos. Cada tipo
de erro (pelo motivo) que passa da parcela mínima vira uma indicação de busca e de configuração; os sinais da Bússola e o
parecer do motor completam as indicações.
"""
from __future__ import annotations

import json
import math
import re
import sqlite3
import tomllib
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parents[3]
CONFIG = RAIZ / "config/pontuacao_motores.toml"
REAIS = ("valido", "encerrada", "arquivar")


def parametros(caminho: Path = CONFIG) -> dict[str, Any]:
    return tomllib.loads(caminho.read_text(encoding="utf-8"))


def _vereditos(raiz: Path) -> dict[str, tuple[str, str]]:
    """livro → (decisão, motivo), dos vereditos do Chrome (os importados e os ainda na entrada)."""
    saida: dict[str, tuple[str, str]] = {}
    pasta = raiz / "verificacao" / "vereditos"
    for f in sorted([*pasta.glob("importados/*.json"), *pasta.glob("*.json")]):
        try:
            for v in json.loads(f.read_text(encoding="utf-8")).get("vereditos") or []:
                if v.get("livro_id") and v.get("decisao"):
                    saida[v["livro_id"]] = (str(v["decisao"]), str(v.get("motivo") or ""))
        except (OSError, ValueError, AttributeError):
            continue
    return saida


def _semana(iso: str | None) -> str | None:
    try:
        d = date.fromisoformat(str(iso)[:10])
    except ValueError:
        return None
    return (d - timedelta(days=d.weekday())).isoformat()


MESES = ("jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez")


def rotulo_dias(agora: datetime) -> str:
    """O período das 8 colunas do mostrador («2–9 nov»), o mesmo para todos os motores."""
    a1 = agora.date()
    a0 = a1 - timedelta(days=7)
    return f"{a0.day}–{a1.day} {MESES[a1.month - 1]}" if a0.month == a1.month else f"{a0.day} {MESES[a0.month - 1]}–{a1.day} {MESES[a1.month - 1]}"


def atividade(bib: sqlite3.Connection, cer: sqlite3.Connection | None, agora: datetime) -> dict[str, dict[str, Any]]:
    """09/11/2026 (o mostrador 3D Radar + Funil): a atividade real de cada motor — em 30 dias (execuções, falhas, achados,
    aceitos, livros trazidos e com estrela), hoje (leituras e achados) e os últimos 8 dias, classificados como no calendário
    do motor: verde (livro com os 12 itens), amarelo (achado aceito, parcial), azul (leu e não havia oportunidade),
    vermelho (todas as leituras falharam), cinza (não executou)."""
    hoje = agora.date()
    d30, dias8 = (hoje - timedelta(days=29)).isoformat(), [(hoje - timedelta(days=k)).isoformat() for k in range(7, -1, -1)]
    A: dict[str, dict[str, Any]] = defaultdict(lambda: {"exec": 0, "falhas": 0, "ach": 0, "acc": 0, "livros": 0, "estrelas": 0, "hl": 0, "ha": 0,
                                                         "rodou": set(), "por_dia": defaultdict(lambda: [0, 0, 0, 0])})
    def _q(con, sql, args):   # a coluna ausente (um banco antigo ou de teste) zera só aquela parte da atividade
        try:
            return con.execute(sql, args).fetchall() if con is not None else []
        except sqlite3.Error:
            return []
    # 09/11/2026: a medida real é a LEITURA de fonte — cada execução registra as fontes lidas e as bloqueadas; a execução que
    # não leu nada por não ter fonte devida (R49: cada local uma vez por dia) não é falha. Execuções = as leituras tentadas;
    # falhas = as leituras bloqueadas e as execuções com erro. Os pilotos: o Espião pelas missões (a busca sem resposta é a
    # falha) e o Interceptador pelas tentativas (a tentativa sem item obtido é a falha)
    _execs = _q(cer, "SELECT motor, substr(inicio, 1, 10), SUM(COALESCE(fontes_lidas, 0) + COALESCE(bloqueios, 0)), "
                     "SUM(COALESCE(bloqueios, 0) + ((erro IS NOT NULL AND erro <> '') * 1)) FROM execucao_motor WHERE inicio >= ? GROUP BY 1, 2", (d30,))
    _execs += [("espiao", d, n, f) for d, n, f in _q(cer, "SELECT substr(em, 1, 10), COUNT(*), SUM(COALESCE(resultados, 0) = 0) FROM espiao_missao "
                                                          "WHERE em >= ? GROUP BY 1", (d30,))]
    _execs += [("interceptador", d, n, f) for d, n, f in _q(bib, "SELECT substr(em, 1, 10), COUNT(*), SUM(resultado LIKE '%\"aceitas\": 0%' "
                                                                 "OR resultado LIKE '%\"trouxe\": false%') FROM tentativa WHERE em >= ? GROUP BY 1", (d30,))]
    for m, dia, n, f in _execs:
        x = A[m]
        x["rodou"].add(dia)
        n, f = n or 0, f or 0
        x["exec"] += n
        x["falhas"] += f or 0
        x["por_dia"][dia][0] += n
        x["por_dia"][dia][1] += f or 0
        if dia == dias8[-1]:
            x["hl"] = n
    for m, dia, n, a in _q(bib, "SELECT motor, substr(encontrado_em, 1, 10), COUNT(*), SUM(decisao = 'aceito') FROM achado "
                                "WHERE encontrado_em >= ? GROUP BY 1, 2", (d30,)):
        x = A[m]
        x["ach"] += n
        x["acc"] += a or 0
        x["por_dia"][dia][2] += a or 0
        if dia == dias8[-1]:
            x["ha"] = n
    for m, dia, est in _q(
            bib, "SELECT a.motor, substr(l.criado_em, 1, 10), COALESCE(l.estrela, 'sem') FROM livro l JOIN (SELECT livro_id, motor, MIN(encontrado_em) "
            "FROM achado WHERE livro_id IS NOT NULL GROUP BY livro_id) a ON a.livro_id = l.id WHERE l.criado_em >= ?", (d30,)):
        x = A[m]
        x["livros"] += 1
        x["estrelas"] += int(est != "sem")
        if est == "ouro":
            x["por_dia"][dia][3] += 1
    for x in A.values():
        cols = []
        for dia in dias8:
            e, f, acc, ouro = x["por_dia"].get(dia, [0, 0, 0, 0])
            cols.append(["cinza", 0] if dia not in x["rodou"] else ["vermelho", 0] if e and f >= e else ["verde", ouro] if ouro
                        else ["amarelo", acc] if acc else ["azul", 0])
        x["dias"] = cols
        x["diasRot"] = rotulo_dias(agora)
        del x["por_dia"], x["rodou"]
    return A


def calcular(bib: sqlite3.Connection, cer: sqlite3.Connection | None = None, raiz: Path = RAIZ,
             agora: datetime | None = None, prm: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    prm = prm or parametros(raiz / "config/pontuacao_motores.toml")
    agora = agora or datetime.now(timezone.utc)
    pesos, faixas, minimos = prm["pesos"], prm["faixas"], prm["minimos"]
    regras = [(r["tipo"], re.compile(r["padrao"], re.I), r["indicacao"]) for r in prm["melhoria"]["regra"]]
    ver = _vereditos(raiz)
    origem = {lid: m for lid, m, _ in bib.execute(
        "SELECT livro_id, motor, MIN(encontrado_em) FROM achado WHERE livro_id IS NOT NULL GROUP BY livro_id")}
    estado = {r[0]: r[1:] for r in bib.execute(
        "SELECT l.id, l.situacao, p.fase, l.criado_em, COALESCE(l.justificativa_exclusao, '') FROM livro l "
        "LEFT JOIN passaporte p ON p.livro_id = l.id")}
    hoje_sem = _semana(agora.date().isoformat())
    semanas = [(date.fromisoformat(hoje_sem) - timedelta(weeks=k)).isoformat() for k in range(int(minimos["semanas"]) - 1, -1, -1)]
    C: dict[str, Counter] = defaultdict(Counter)
    tipos: dict[str, Counter] = defaultdict(Counter)
    serie: dict[str, dict[str, Counter]] = defaultdict(lambda: defaultdict(Counter))
    for lid, motor in origem.items():
        e = estado.get(lid)
        if not e:
            continue
        sit, fase, criado, just = e
        dec, motivo = ver.get(lid, (None, ""))
        if dec in REAIS or (dec is None and fase == "farol" and sit not in ("excluido", "unido")):
            res = "acertos"
        elif dec == "descartar" or (dec is None and sit == "excluido"):
            res = "erros"
            texto = motivo or just
            tipo = next((t for t, rx, _ in regras if rx.search(texto)), "outros")
            tipos[motor][tipo] += 1
        elif sit == "unido":
            continue
        else:
            res = "andamento"
        C[motor][res] += 1
        s = _semana(criado)
        if s in semanas and res != "andamento":
            serie[motor][s][res] += 1
    maior = max((c["acertos"] for c in C.values()), default=0)
    sinais_de = {}
    if cer is not None:
        from .sinais_motores import sinais
        for m in set(C) | set(prm.get("local", {})):
            try:
                sinais_de[m] = sinais(cer, m)
            except sqlite3.Error:
                pass
    atv = atividade(bib, cer, agora)
    saida: dict[str, dict[str, Any]] = {}
    medidos = set(prm.get("local", {})) | {"interceptador", "espiao"}   # os motores configurados e os dois pilotos
    for m in sorted(medidos):
        c = C[m]
        a, e_, n = c["acertos"], c["erros"], c["andamento"]
        dec = a + e_
        precisao = a / dec if dec else 0.0
        rend = (math.log10(1 + a) / math.log10(1 + maior)) if maior else 0.0
        local = float(prm.get("local", {}).get(m, 0.6))
        sg = sinais_de.get(m) or {}
        luz = sg.get("luz") or "cinza"
        saude = {"verde": 1.0, "amarelo": 0.5}.get(luz, 0.0)
        nota = round(pesos["precisao"] * precisao + pesos["rendimento"] * rend + pesos["local"] * local + pesos["saude"] * saude, 1)
        faixa = ("formacao" if dec < int(minimos["decididos"]) else "excelente" if nota >= faixas["excelente"]
                 else "bom" if nota >= faixas["bom"] else "atencao" if nota >= faixas["atencao"] else "critico")
        melhorias = []
        for t, qtd in tipos[m].most_common():
            if e_ and qtd / e_ >= float(prm["melhoria"]["parcela_minima"]):
                txt = next((i for tt, _, i in regras if tt == t), None)
                if txt:
                    melhorias.append({"tipo": t, "erros": qtd, "parcela": round(qtd / e_, 2), "indicacao": txt})
        if sg.get("pendentes_local"):
            melhorias.append({"tipo": "computador_local", "erros": len(sg["pendentes_local"]), "parcela": None,
                              "indicacao": f"{len(sg['pendentes_local'])} fonte(s) pendente(s) no computador local: ler pela ponte BR "
                                           f"({', '.join(sg['pendentes_local'])[:140]})."})
        if sg.get("nunca_entregou"):
            melhorias.append({"tipo": "nunca_entregou", "erros": 0, "parcela": None,
                              "indicacao": "O motor lê e nunca entregou nada: corrigir a extração da página."})
        if prm.get("parecer", {}).get(m):
            melhorias.append({"tipo": "parecer", "erros": None, "parcela": None, "indicacao": prm["parecer"][m]})
        at = atv.get(m) or {}
        vazio = [["cinza", 0]] * 8
        m3d = {"a": a, "e": e_, "curso": n, "local": local, "saude": saude, "melh": len(melhorias), "luz": luz,
               "exec": at.get("exec", 0), "falhas": at.get("falhas", 0), "ach": at.get("ach", 0), "acc": at.get("acc", 0),
               "livros": at.get("livros", 0), "estrelas": at.get("estrelas", 0), "hl": at.get("hl", 0), "ha": at.get("ha", 0),
               "hf": 0, "hs": 0, "dias": at.get("dias", vazio), "diasRot": rotulo_dias(agora)}
        saida[m] = {"m3d": m3d, "nota": nota, "faixa": faixa, "acertos": a, "erros": e_, "andamento": n, "decididos": dec,
                    "precisao": round(precisao, 3), "em_formacao": dec < int(minimos["decididos"]),
                    "rendimento": round(rend, 3), "local": local, "saude": saude, "luz": luz,
                    "componentes": {"precisao": round(pesos["precisao"] * precisao, 1), "rendimento": round(pesos["rendimento"] * rend, 1),
                                    "local": round(pesos["local"] * local, 1), "saude": round(pesos["saude"] * saude, 1)},
                    "serie": [{"semana": s, "acertos": serie[m][s]["acertos"], "erros": serie[m][s]["erros"]} for s in semanas],
                    "erros_por_tipo": dict(tipos[m].most_common()), "melhorias": melhorias}
    return saida
