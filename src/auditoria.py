"""Auditoria da Biblioteca — edital por edital, um após o outro.

Determinação do titular: nada de ação paralela. Cada edital dos últimos 5 anos
é examinado individualmente e só então passa-se ao seguinte. Para cada um:

  1. quais dos 11 itens foram obtidos e quais faltam;
  2. **por que** faltam — o diagnóstico da causa, que é o que orienta a
     próxima melhoria;
  3. qual motor (sensor) deveria tê-lo capturado por completo e se ele existe.

As causas são fechadas num vocabulário curto, para virar estatística:

  `ementa_sem_corpo` .......... a fonte publicou só a ementa (diário)
  `sem_url_primaria` .......... o registro não tem link para o ato
  `url_de_agregador` .......... o link aponta para o agregador, não o órgão
  `ato_nao_baixado` ........... há URL do órgão, mas o texto nunca foi buscado
  `resultado_nao_publicado` ... o certame não teve resultado divulgado ali
  `sem_sensor_para_a_fonte` ... nenhum motor cobre o domínio de origem
  `fonte_fora_do_escopo` ...... não é edital para OSC

Saída: `biblioteca_alexandria/historico/auditoria_individual.json` (resumo e
estatística) e uma linha por edital em `auditoria_editais.jsonl` — formato
enxuto, para não pesar o repositório.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import date
from urllib.parse import urlsplit

from .completude_biblioteca import ITENS, onze_itens
from .nucleo import ROOT, load_json, now_iso, write_json

SAIDA = ROOT / "biblioteca_alexandria/historico"
# ACHADO DA AUDITORIA: a URL do Querido Diário é o PDF da EDIÇÃO INTEIRA do
# diário oficial — o ato do edital está dentro dela. Não é agregador: é a
# fonte primária, e o sistema só precisava abrir o documento.
_EDICAO_PDF = re.compile(r"queridodiario\.ok\.org\.br/.+\.pdf$", re.I)
_AGREG = re.compile(r"pncp\.gov|compras|licitanet|bll|bnc|portaldecompras", re.I)


def _dominio(url: str | None) -> str | None:
    try:
        return (urlsplit(url or "").hostname or "").lower() or None
    except Exception:
        return None


def _sensores_por_dominio() -> dict[str, str]:
    try:
        from .sensores import registro
    except Exception:
        return {}
    mapa = {}
    for s in registro():
        for u in s["urls"]:
            d = _dominio(u)
            if d:
                mapa.setdefault(d, s["id"])
    return mapa


def diagnosticar(ficha: dict, itens: dict, sensores: dict) -> dict:
    """Por que os itens faltam neste edital — uma causa por item ausente."""
    url = ficha.get("url")
    dom = _dominio(url)
    edicao = bool(url) and bool(_EDICAO_PDF.search(url))
    tem_ato = bool(url) and (edicao or not _AGREG.search(url))
    causas: dict[str, str] = {}
    for it in itens["itens"]:
        if it["comprovado"]:
            continue
        nome = it["item"]
        if not url:
            causas[nome] = "sem_url_primaria"
        elif nome in ("Resultado", "Prazo de recurso"):
            causas[nome] = ("resultado_nao_publicado"
                            if ficha.get("tem_resultado_publicado") is False
                            else "ato_nao_baixado")
        elif edicao:
            causas[nome] = "edicao_nao_extraida"
        elif not tem_ato:
            causas[nome] = "url_de_agregador"
        elif dom and dom not in sensores:
            causas[nome] = "sem_sensor_para_a_fonte"
        else:
            causas[nome] = "ato_nao_baixado"
    if (ficha.get("destinacao") or {}).get("elegivel") is False:
        causas = {k: "fonte_fora_do_escopo" for k in causas}
    principal = Counter(causas.values()).most_common(1)
    return {"causas_por_item": causas,
            "causa_principal": principal[0][0] if principal else None,
            "dominio": dom, "tem_ato_de_origem": tem_ato, "edicao_pdf": edicao,
            "sensor_responsavel": sensores.get(dom or "", None),
            "acao_recomendada": _acao(principal[0][0] if principal else None, dom)}


def _acao(causa: str | None, dom: str | None) -> str | None:
    return {
        "ementa_sem_corpo": "campanha de completude: baixar o ato integral na fonte",
        "edicao_nao_extraida": ("a URL é o PDF da edição do diário: abrir e recortar o ato "
                                "(src/edicao.py) — a informação já está no acervo"),
        "sem_url_primaria": "recoletar o registro com URL (o coletor precisa gravar o link)",
        "url_de_agregador": f"criar sensor para o órgão de origem (hoje só há {dom})",
        "ato_nao_baixado": "busca ativa: abrir a URL e extrair texto, datas e anexos",
        "resultado_nao_publicado": "monitorar a fonte na janela de resultado (calendário do Farol)",
        "sem_sensor_para_a_fonte": f"acrescentar {dom} à esquadra de sensores",
        "fonte_fora_do_escopo": "manter descartado; não é edital para OSC",
    }.get(causa or "", None)


def run(anos: int = 5, hoje: date | None = None, limite: int | None = None,
        uf: str | None = None) -> dict:
    """Percorre o acervo SEQUENCIALMENTE, um edital por vez."""
    from .banco import conectar
    hoje = hoje or date.today()
    corte = str(hoje.year - anos)
    sensores = _sensores_por_dominio()
    con = conectar()
    linhas = con.execute(
        "SELECT chave, ano, id, ficha FROM historico "
        + ("WHERE uf=? " if uf else "") +
        "ORDER BY (uf='GO') DESC, data_publicacao DESC",
        ((uf,) if uf else ())).fetchall()
    con.close()
    if limite:
        linhas = linhas[:limite]

    SAIDA.mkdir(parents=True, exist_ok=True)
    jl = SAIDA / "auditoria_editais.jsonl"
    completos = parciais = vazios = 0
    causas_geral: Counter = Counter()
    por_item_falta: Counter = Counter()
    por_dominio: dict[str, Counter] = defaultdict(Counter)
    por_uf: dict[str, Counter] = defaultdict(Counter)
    por_ano: dict[str, Counter] = defaultdict(Counter)
    sem_sensor: Counter = Counter()
    n = 0
    with jl.open("w", encoding="utf-8") as saida:
        for chave, ano, cid, fj in linhas:          # ← um por vez, em ordem
            ficha = json.loads(fj)
            if (ficha.get("data_publicacao") or "9999")[:4] < corte:
                continue
            itens = onze_itens(ficha)
            diag = diagnosticar(ficha, itens, sensores)
            n += 1
            comp = itens["comprovados"]
            if comp == itens["total"]:
                completos += 1
            elif comp >= 6:
                parciais += 1
            else:
                vazios += 1
            for it in itens["itens"]:
                if not it["comprovado"]:
                    por_item_falta[it["item"]] += 1
            if diag["causa_principal"]:
                causas_geral[diag["causa_principal"]] += 1
            d = diag["dominio"] or "sem_url"
            por_dominio[d]["editais"] += 1
            por_dominio[d]["itens_obtidos"] += comp
            if not diag["sensor_responsavel"] and diag["dominio"]:
                sem_sensor[diag["dominio"]] += 1
            u = ficha.get("uf") or "—"
            por_uf[u]["editais"] += 1; por_uf[u]["itens_obtidos"] += comp
            a = (ficha.get("data_publicacao") or "")[:4] or "—"
            por_ano[a]["editais"] += 1; por_ano[a]["itens_obtidos"] += comp
            saida.write(json.dumps({
                "chave": chave, "ano": ano, "id": cid,
                "titulo": (ficha.get("titulo") or "")[:110],
                "uf": ficha.get("uf"), "nivel": ficha.get("nivel"),
                "financiador": (ficha.get("financiador") or "")[:60],
                "obtidos": comp, "total": itens["total"],
                "faltam": [i["item"] for i in itens["itens"] if not i["comprovado"]],
                "causa": diag["causa_principal"], "dominio": diag["dominio"],
                "sensor": diag["sensor_responsavel"],
                "acao": diag["acao_recomendada"],
            }, ensure_ascii=False) + "\n")

    def _media(c: Counter) -> float:
        return round(c["itens_obtidos"] / c["editais"], 2) if c["editais"] else 0

    relatorio = {
        "gerado_em": now_iso(), "janela": f"{corte}–{hoje.year}", "uf": uf,
        "editais_auditados": n,
        "completos_11_itens": completos, "parciais_6_a_10": parciais, "abaixo_de_6": vazios,
        "itens_que_mais_faltam": [{"item": k, "faltam_em": v} for k, v in por_item_falta.most_common()],
        "causas": [{"causa": k, "editais": v,
                    "acao": _acao(k, None)} for k, v in causas_geral.most_common()],
        "por_ano": {a: {"editais": c["editais"], "media_itens": _media(c)}
                    for a, c in sorted(por_ano.items())},
        "por_uf_top": {u: {"editais": c["editais"], "media_itens": _media(c)}
                       for u, c in sorted(por_uf.items(), key=lambda x: -x[1]["editais"])[:10]},
        "por_dominio_top": [{"dominio": d, "editais": c["editais"], "media_itens": _media(c),
                             "tem_sensor": d in sensores}
                            for d, c in sorted(por_dominio.items(), key=lambda x: -x[1]["editais"])[:12]],
        "dominios_sem_sensor": [{"dominio": d, "editais": v} for d, v in sem_sensor.most_common(15)],
        "detalhe_por_edital": str(jl.relative_to(ROOT)),
        "nota": ("auditoria sequencial, um edital por vez; cada item ausente recebe "
                 "a causa e a ação recomendada — nada é estimado"),
    }
    write_json(SAIDA / "auditoria_individual.json", relatorio)
    return relatorio


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2)[:2600])
