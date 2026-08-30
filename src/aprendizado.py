"""Aprendizado automático com editais anteriores — sem IA, só evidência:

1. Padrões recorrentes por financiador: um requisito vira "padrão" apenas com
   DUAS ocorrências independentes em editais distintos; antes disso é hipótese.
2. Previsão de janelas: se a mesma fonte publicou edital em meses próximos em
   pelo menos dois anos diferentes, projeta-se a janela provável do próximo —
   sempre rotulada hipótese, nunca fato.

Resultados: dados/financiadores|doadores/<fonte>/aprendizado.json e
estado/previsoes.json (consumido pelo painel e pela sentinela humana)."""
from __future__ import annotations

import json
from collections import Counter, defaultdict

from .nucleo import ROOT, carregar_oportunidades, load_json, now_iso, slug, write_json

MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

def _mes(item: dict) -> int | None:
    data = item.get("data_publicacao") or ""
    if len(data) >= 7 and data[5:7].isdigit():
        return int(data[5:7])
    prazo = item.get("prazo_texto") or ""
    partes = prazo.split("/")
    if len(partes) == 3 and partes[1].isdigit():
        return int(partes[1])
    return None

def _ano(item: dict) -> int | None:
    return item.get("ano_referencia") or item.get("ano_pesquisado")

def run() -> dict:
    registros = list(carregar_oportunidades().values())
    fontes_cfg = {f["id"]: f for f in load_json(ROOT / "config/fontes.json")["fontes"]}
    por_fonte = defaultdict(list)
    for item in registros:
        por_fonte[item.get("fonte_id") or "desconhecida"].append(item)
    previsoes = []
    resumo = {"executado_em": now_iso(), "fontes_analisadas": 0, "previsoes": 0, "padroes": 0}
    for fid, itens in sorted(por_fonte.items()):
        resumo["fontes_analisadas"] += 1
        fonte = fontes_cfg.get(fid, {})
        base = "doadores" if fonte.get("tipo") in {"empresa", "empresa_publica", "fundacao_empresarial"} else "financiadores"
        # 1) requisitos recorrentes (somente requisitos validados por humano contam para padrão)
        contagem = Counter()
        for item in itens:
            requisitos = item.get("requisitos") or {}
            if not isinstance(requisitos, dict): continue
            validado = bool(item.get("requisitos_validados"))
            for chave, valor in requisitos.items():
                for unidade in (valor if isinstance(valor, list) else [valor]):
                    if unidade in (None, "", []): continue
                    contagem[(chave, str(unidade), validado)] += 1
        padroes, hipoteses = [], []
        vistos = set()
        for (chave, valor, validado), vezes in contagem.most_common():
            if (chave, valor) in vistos: continue
            vistos.add((chave, valor))
            total = contagem[(chave, valor, True)] + contagem[(chave, valor, False)]
            destino = padroes if contagem[(chave, valor, True)] >= 2 else hipoteses
            destino.append({"requisito": chave, "valor": valor, "ocorrencias": total,
                            "ocorrencias_validadas": contagem[(chave, valor, True)]})
        # 2) previsão de janela por recorrência mensal em anos distintos
        anos_por_mes = defaultdict(set)
        for item in itens:
            mes, ano = _mes(item), _ano(item)
            if mes and ano: anos_por_mes[mes].add(ano)
        janela = sorted(m for m, anos in anos_por_mes.items() if len(anos) >= 2)
        previsao = None
        if janela:
            previsao = {"fonte_id": fid, "fonte_nome": fonte.get("nome", fid),
                        "janela_provavel": [MESES[m - 1] for m in janela],
                        "anos_de_base": sorted({a for m in janela for a in anos_por_mes[m]}),
                        "status": "hipotese_por_recorrencia", "gerado_em": now_iso()}
            previsoes.append(previsao)
        if padroes or hipoteses or previsao:
            pasta = ROOT / "dados" / base / slug(fid)
            pasta.mkdir(parents=True, exist_ok=True)
            write_json(pasta / "aprendizado.json", {
                "gerado_em": now_iso(), "eventos_considerados": len(itens),
                "padroes_confirmados": padroes[:30], "hipoteses": hipoteses[:30],
                "previsao_janela": previsao,
                "regra": "padrão exige 2+ ocorrências validadas; previsão exige o mesmo mês em 2+ anos; tudo é hipótese até conferência humana",
            })
            resumo["padroes"] += len(padroes)
    resumo["previsoes"] = len(previsoes)
    write_json(ROOT / "estado/previsoes.json", {"gerado_em": now_iso(), "previsoes": previsoes})
    return resumo

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
