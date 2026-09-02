"""Previsão de editais — o Eldorado olhando para os meses seguintes.

Premissa do titular: onisciência sobre editais passados, presentes e futuros
prováveis, a partir do estudo histórico da Biblioteca de Alexandria.

Como funciona:
  · O acervo histórico (SQLite) é agrupado por ÓRGÃO real × ÁREA. Para cada
    grupo, conta-se em quais meses do ano houve publicação e em quantos anos
    distintos. Padrão = mesmo mês em 2+ anos.
  · Para cada padrão, projeta-se uma previsão no próximo ano em que o mês
    ainda não passou. A previsão carrega força (anos observados), a janela
    típica (duração média das inscrições no histórico) e a lista dos casos
    que a sustentam.
  · Regras especiais (Rouanet, Aldir Blanc/PNAB, Goyazes) vêm de
    `config/previsoes_especiais.json` como HIPÓTESE DECLARADA a confirmar no
    edital — nunca como fato.

No painel, a previsão aparece em CINZA CLARO somente nos meses futuros; ao
virar o mês, as previsões daquele mês desaparecem e ficam só as dos meses
adiante. Previsão nunca vira edital: quando o edital real é publicado, ele
entra pela varredura normal e a previsão correspondente sai.
"""
from __future__ import annotations

import json
import re
import sqlite3
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, slug, write_json

CFG_ESPECIAIS = ROOT / "config/previsoes_especiais.json"
SAIDA = ROOT / "biblioteca_alexandria/previsoes"

_DIARIO = re.compile(r"Di[áa]rio Oficial d[eoa]s? ([^(—-]+?)\s*\(([A-Z]{2})\)")


def orgao_real(financiador: str | None, titulo: str | None) -> str:
    """O órgão de fato, não o agregador (Querido Diário / PNCP)."""
    m = _DIARIO.search(titulo or "")
    if m:
        return f"Prefeitura de {m.group(1).strip()} ({m.group(2)})"
    m = re.search(r"PNCP\s+—\s+(.+)", financiador or "")
    if m:
        return m.group(1).strip()[:70]
    return (financiador or "órgão não identificado")[:70]


def padroes(con: sqlite3.Connection, minimo_anos: int = 2) -> list[dict]:
    """Padrões de recorrência: órgão × área × mês, em 2+ anos distintos."""
    rows = con.execute(
        "SELECT financiador, area, uf, nivel, data_publicacao, inicio, fim, titulo, chave "
        "FROM historico").fetchall()
    grupos: dict[tuple, dict] = defaultdict(
        lambda: {"anos": set(), "duracoes": [], "casos": [], "titulos": set()})
    for fin, area, uf, nivel, pub, ini, fim, tit, chave in rows:
        d = ini or pub
        if not d:
            continue
        org = orgao_real(fin, tit)
        g = grupos[(org, area or "outros", uf, nivel, d[5:7])]
        g["anos"].add(d[:4])
        if ini and fim and fim > ini:
            g["duracoes"].append((date.fromisoformat(fim) - date.fromisoformat(ini)).days)
        if len(g["casos"]) < 6:
            g["casos"].append({"ano": d[:4], "chave": chave, "titulo": (tit or "")[:100]})
        g["titulos"].add(re.sub(r"\s+\d{4}-\d{2}-\d{2}.*$", "", tit or "")[:80])
    saida = []
    for (org, area, uf, nivel, mes), g in grupos.items():
        if len(g["anos"]) < minimo_anos:
            continue
        dur = (round(sum(g["duracoes"]) / len(g["duracoes"])) if g["duracoes"] else 30)
        saida.append({"orgao": org, "area": area, "uf": uf, "nivel": nivel, "mes": mes,
                      "anos_observados": sorted(g["anos"]),
                      "forca": len(g["anos"]), "duracao_tipica_dias": max(7, min(dur, 120)),
                      "casos": g["casos"], "exemplo_titulo": next(iter(g["titulos"]))})
    saida.sort(key=lambda p: (-p["forca"], p["orgao"], p["mes"]))
    return saida


def _especiais(hoje: date) -> list[dict]:
    """Rouanet, Aldir Blanc/PNAB, Goyazes — janelas por hipótese declarada."""
    if not CFG_ESPECIAIS.exists():
        return []
    cfg = load_json(CFG_ESPECIAIS)
    saida = []
    encerradas = set()
    jc = ROOT / "config/janelas_confirmadas.json"
    if jc.exists():
        encerradas = {(x["id"], x["ano"]) for x in load_json(jc).get("encerramentos", [])}
    for r in cfg.get("regras", []):
        if not r.get("inicio_mes_dia") or not r.get("fim_mes_dia"):
            continue                                   # sem regra própria, sem janela
        for ano in (hoje.year, hoje.year + 1):
            if (r["id"], ano) in encerradas:
                continue                               # encerrada: não se projeta
            ini = f'{ano}-{r["inicio_mes_dia"]}'
            fim = f'{ano}-{r["fim_mes_dia"]}'
            if fim < hoje.isoformat():
                continue
            saida.append({
                "id": f'prev-{r["id"]}-{ano}', "previsto": True, "especial": True,
                "titulo": f'{r["nome"]} — janela histórica de inscrição {ano}',
                "orgao": r["orgao"], "area": r["area"], "uf": r.get("uf"),
                "nivel": r["nivel"], "lei": r["lei"],
                "inicio": ini, "fim": fim, "forca": r.get("forca", 2),
                "base": r["base"], "status_verificacao": r["status_verificacao"],
                "fonte_confirmacao": r["fonte_confirmacao"],
                "modalidades": r.get("modalidades", []),
                "nota": ("HIPÓTESE declarada pelo titular, a confirmar no edital do "
                         "ano — nunca tratada como data publicada"),
            })
    return saida


def prever(hoje: date | None = None, meses_adiante: int = 12,
           con: sqlite3.Connection | None = None) -> dict:
    """Gera as previsões dos próximos meses (a partir do MÊS SEGUINTE)."""
    hoje = hoje or date.today()
    fechar = con is None
    if con is None:
        from .banco import conectar
        con = conectar()
    pats = padroes(con)
    if fechar:
        con.close()
    previsoes = []
    for p in pats:
        for delta in range(1, meses_adiante + 1):
            ano = hoje.year + (hoje.month - 1 + delta) // 12
            mes = (hoje.month - 1 + delta) % 12 + 1
            if f"{mes:02d}" != p["mes"]:
                continue
            ini = date(ano, mes, 1)
            fim = ini + timedelta(days=p["duracao_tipica_dias"])
            previsoes.append({
                "id": f'prev-{slug(p["orgao"])[:40]}-{p["area"]}-{ano}-{p["mes"]}',
                "previsto": True, "especial": False,
                "titulo": f'{p["orgao"]} — edital provável de {p["area"].replace("_", " ")}',
                "orgao": p["orgao"], "area": p["area"], "uf": p["uf"], "nivel": p["nivel"],
                "inicio": ini.isoformat(), "fim": fim.isoformat(),
                "forca": p["forca"], "anos_observados": p["anos_observados"],
                "duracao_tipica_dias": p["duracao_tipica_dias"],
                "casos": p["casos"], "exemplo_titulo": p["exemplo_titulo"],
                "base": (f'publicação no mês {p["mes"]} em {p["forca"]} ano(s) '
                         f'distinto(s): {", ".join(p["anos_observados"])}'),
                "nota": "previsão por recorrência histórica; some quando o mês passa "
                        "ou quando o edital real é publicado",
            })
            break
    previsoes += _especiais(hoje)
    previsoes += _janelas_das_260(hoje, {p["id"] for p in previsoes})
    previsoes.sort(key=lambda x: (x["inicio"], -x["forca"]))
    resumo = {"gerado_em": now_iso(), "referencia": hoje.isoformat(),
              "padroes_encontrados": len(pats),
              "previsoes": len(previsoes),
              "por_mes": _por_mes(previsoes),
              "itens": previsoes,
              "regra": ("cinza claro só nos meses futuros; ao virar o mês, as "
                        "previsões daquele mês desaparecem")}
    SAIDA.mkdir(parents=True, exist_ok=True)
    write_json(SAIDA / "previsoes.json", resumo)
    write_json(SAIDA / "padroes.json", {"gerado_em": now_iso(), "total": len(pats),
                                        "padroes": pats[:2000]})
    return resumo


def _janelas_das_260(hoje: date, ja_tem: set[str]) -> list[dict]:
    """Janela provável de cada uma das 260 fontes de captação.

    As fichas de três tempos já calculam a próxima janela de cada fonte a
    partir do dossiê histórico. Elas precisam aparecer NO CALENDÁRIO — é o que
    o titular chama de "ver as 260 no calendário", especialmente esporte,
    cultura e os fundos. A duração usa a média observada da fonte (ou 30 dias).
    """
    ft = ROOT / "biblioteca_alexandria/fontes/fichas_tres_tempos.json"
    if not ft.exists():
        return []
    from datetime import timedelta as _td
    saida = []
    for f in load_json(ft).get("fontes_lista", []):
        j = f.get("proxima_janela")
        # só entra janela sustentada por ANOS DISTINTOS — o mês repetido dentro
        # do mesmo ano é viés da amostra (a coleta começou em ago/2026)
        if not j or not j.get("mes") or len(j.get("anos_observados") or []) < 2:
            continue
        try:
            ano, mes = (int(x) for x in j["mes"].split("-"))
        except Exception:
            continue
        ini = date(ano, mes, 1)
        if ini < hoje.replace(day=1):
            continue
        fim = ini + _td(days=30)
        pid = f'prev260-{f["id"]}-{j["mes"]}'
        if pid in ja_tem:
            continue
        saida.append({
            "id": pid, "previsto": True, "especial": False, "das_260": True,
            "titulo": f'{f["programa"]} — janela provável',
            "orgao": f.get("orgao"), "area": _area_da_260(f),
            "uf": f.get("uf"), "nivel": f.get("nivel"),
            "inicio": ini.isoformat(), "fim": fim.isoformat(),
            "forca": 3 if (j.get("confianca") == "alta") else 2,
            "base": (f'fonte do catálogo de 260 · {j.get("base", "recorrência do dossiê")}'
                     + (f' · {f["editais"]} edital(is) no histórico' if f.get("editais") else "")),
            "goias": f.get("goias"),
            "nota": "janela provável da fonte catalogada; confirmar no órgão",
        })
    return saida


_AREA_260 = {"cultura": "cultura", "esporte": "esporte", "educa": "educacao",
             "saude": "saude", "assistencia": "assistencia_social",
             "crianca": "crianca_adolescente", "idosa": "pessoa_idosa",
             "ambiente": "meio_ambiente", "emenda": "emendas_parlamentares"}


def _area_da_260(f: dict) -> str:
    alvo = f'{f.get("programa","")} {f.get("orgao","")}'.lower()
    for chave, area in _AREA_260.items():
        if chave in alvo:
            return area
    return "outros"


def _por_mes(previsoes: list[dict]) -> dict:
    c: dict[str, int] = defaultdict(int)
    for p in previsoes:
        c[p["inicio"][:7]] += 1
    return dict(sorted(c.items()))


if __name__ == "__main__":
    r = prever()
    print(json.dumps({k: v for k, v in r.items() if k != "itens"},
                     ensure_ascii=False, indent=2))
