"""Parecer de PRAZO de cada fonte de recurso.

Pergunta do titular: existe análise de prazo por recurso? É permanente? É
periódico? Quais são as datas de cada edital?

Este módulo responde uma fonte por vez, classificando o REGIME DE PRAZO em
categorias fechadas, cada uma com o fundamento que a sustenta:

  `permanente_com_janela_anual` .. abre e fecha em datas fixas todo ano
                                   (emendas 01/10–30/11; doação RFB 01/01–31/12
                                   nos anos ímpares; Rouanet/PNAB/Goyazes
                                   02/01–31/10 por janela histórica declarada)
  `permanente_fluxo_continuo` .... aceita proposta a qualquer tempo, sem janela
  `periodico_confirmado` ......... publicou no mesmo mês em ANOS DISTINTOS —
                                   sazonalidade comprovada
  `periodico_suspeito` ........... publicou várias vezes, mas tudo no mesmo ano:
                                   pode ser sazonal, ainda não dá para afirmar
  `eventual_observado` ........... já publicou, sem padrão de mês
  `sem_observacao` ............... nenhuma publicação no acervo

E, para cada fonte, as DATAS conhecidas: janelas fixas do regramento, prazos
publicados nos editais históricos e a próxima janela provável, cada uma com a
origem (`regramento`, `edital_publicado`, `projecao`) e o grau de certeza.

Nada é estimado sem dizer que é estimativa.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import date

from .nucleo import ROOT, load_json, now_iso, slug, write_json

SAIDA = ROOT / "biblioteca_alexandria/fontes"
RELATORIO = SAIDA / "parecer_prazos.json"
_MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

# Fontes cujo prazo vem do REGRAMENTO, não de observação
_REGRAMENTO = {
    "emenda": {"regime": "permanente_com_janela_anual", "inicio": "10-01", "fim": "11-30",
               "fundamento": "regra anual de captação de emendas: 01/10 a 30/11 de todo ano",
               "certeza": "alta"},
    "doacao-receita-federal": {"regime": "permanente_com_janela_anual",
                               "inicio": "01-01", "fim": "12-31", "anos": "impares",
                               "fundamento": ("Portaria RFB 200/2022, art. 80, I, 'a': vedada a "
                                              "doação a OSC no ano de eleição — logo, ano inteiro "
                                              "nos anos ímpares"),
                               "certeza": "alta"},
    "rouanet": {"regime": "permanente_com_janela_anual", "inicio": "02-01", "fim": "10-31",
                "fundamento": "janela histórica declarada pelo titular (Lei 8.313/1991 — SALIC)",
                "certeza": "media_a_confirmar"},
    "aldir-blanc": {"regime": "permanente_com_janela_anual", "inicio": "02-01", "fim": "10-31",
                    "fundamento": "premissa do titular: mesma sazonalidade da Rouanet (PNAB)",
                    "certeza": "media_a_confirmar"},
    "goyazes": {"regime": "permanente_com_janela_anual", "inicio": "02-01", "fim": "10-31",
                "fundamento": "premissa do titular: mesma sazonalidade da Rouanet (Lei GO 13.613/2000)",
                "certeza": "media_a_confirmar"},
}
# tipos do catálogo que, por natureza, não têm edital com janela
_FLUXO_CONTINUO = {
    "doacao_patrocinio": ("captação por proposta direta ao doador/patrocinador, "
                          "a qualquer tempo"),
    "destinacao_judicial": ("habilitação da entidade junto à vara/conselho; as "
                            "destinações ocorrem conforme os processos, sem edital periódico"),
    "emenda": "indicação ao gabinete dentro da janela orçamentária anual",
}


def _regra_do_regramento(f: dict) -> dict | None:
    alvo = f'{f.get("id","")} {f.get("programa","")} {f.get("orgao","")}'.lower()
    for chave, regra in _REGRAMENTO.items():
        if chave in alvo or chave.replace("-", " ") in alvo:
            return regra
    if f.get("tipo") == "emenda":
        return _REGRAMENTO["emenda"]
    return None


def _datas_dos_editais(casos: list[dict]) -> list[dict]:
    """Prazos efetivamente publicados nos editais desta fonte."""
    saida = []
    for c in casos:
        if c.get("fim") or c.get("inicio"):
            saida.append({"ano": c.get("ano"), "inicio": c.get("inicio"), "fim": c.get("fim"),
                          "origem": "edital_publicado", "certeza": "alta",
                          "titulo": (c.get("titulo") or "")[:90]})
    return sorted(saida, key=lambda x: str(x.get("fim") or x.get("inicio") or ""))[:20]


def parecer_da_fonte(f: dict, dossie: dict, hoje: date) -> dict:
    """Regime de prazo e datas conhecidas — uma fonte por vez."""
    casos = dossie.get("casos") or []
    meses_por_ano: dict[int, set] = defaultdict(set)
    for c in casos:
        d = c.get("inicio") or c.get("fim")
        if d:
            meses_por_ano[int(d[5:7])].add(d[:4])
    n_editais = dossie.get("editais_no_historico", 0) or len(casos)
    anos = sorted({a for s in meses_por_ano.values() for a in s})
    recorrentes = {m: sorted(a) for m, a in meses_por_ano.items() if len(a) >= 2}

    reg = _regra_do_regramento(f)
    datas: list[dict] = []
    if reg:
        regime = reg["regime"]
        fundamento = reg["fundamento"]
        certeza = reg["certeza"]
        for ano in (hoje.year, hoje.year + 1):
            if reg.get("anos") == "impares" and ano % 2 == 0:
                datas.append({"ano": ano, "inicio": None, "fim": None,
                              "origem": "regramento", "certeza": "alta",
                              "observacao": "ano de eleição: captação vedada"})
                continue
            datas.append({"ano": ano, "inicio": f'{ano}-{reg["inicio"]}',
                          "fim": f'{ano}-{reg["fim"]}', "origem": "regramento",
                          "certeza": certeza})
    elif f.get("tipo") in _FLUXO_CONTINUO and n_editais == 0:
        regime = "permanente_fluxo_continuo"
        fundamento = _FLUXO_CONTINUO[f["tipo"]]
        certeza = "media"
    elif recorrentes:
        regime = "periodico_confirmado"
        m = sorted(recorrentes, key=lambda x: -len(recorrentes[x]))[0]
        fundamento = (f"publicou em {_MESES[m-1]} nos anos {', '.join(recorrentes[m])} — "
                      "sazonalidade comprovada em anos distintos")
        certeza = "alta"
        prox_ano = hoje.year if m > hoje.month else hoje.year + 1
        datas.append({"ano": prox_ano, "inicio": f"{prox_ano}-{m:02d}-01", "fim": None,
                      "origem": "projecao", "certeza": "media",
                      "observacao": "mês provável pela recorrência; dia a confirmar no edital"})
    elif n_editais >= 2 and len(anos) == 1:
        regime = "periodico_suspeito"
        top = Counter({m: len(a) for m, a in meses_por_ano.items()})
        mm = [f"{_MESES[m-1]}" for m, _ in top.most_common(3)]
        fundamento = (f"{n_editais} publicação(ões), todas em {anos[0] if anos else '—'} "
                      f"(meses: {', '.join(mm) or '—'}): pode ser sazonal, mas um único ano "
                      "de observação não permite afirmar")
        certeza = "baixa"
    elif n_editais >= 1:
        regime = "eventual_observado"
        fundamento = f"{n_editais} publicação(ões) sem padrão de mês identificável"
        certeza = "baixa"
    else:
        regime = "sem_observacao"
        fundamento = "nenhuma publicação desta fonte no acervo — prazo desconhecido"
        certeza = "nenhuma"

    datas += _datas_dos_editais(casos)
    com_data = sum(1 for c in casos if c.get("fim"))
    return {
        "id": f["id"], "programa": f["programa"], "orgao": f.get("orgao"),
        "nivel": f.get("nivel"), "uf": f.get("uf"), "goias": f.get("goias"),
        "tipo": f.get("tipo"), "area": f.get("area"),
        "regime_de_prazo": regime, "permanente": regime.startswith("permanente"),
        "periodico": regime.startswith("periodico"),
        "fundamento": fundamento, "certeza": certeza,
        "editais_observados": n_editais, "anos_observados": anos,
        "editais_com_prazo_publicado": com_data,
        "meses_recorrentes": [_MESES[m-1] for m in sorted(recorrentes)],
        "datas": datas[:24],
        "lacuna": (None if com_data or reg else
                   ("os editais desta fonte estão no acervo sem data de inscrição: "
                    "a data está dentro da edição do diário, ainda por extrair"
                    if n_editais else "sem observação para analisar prazo")),
        "gerado_em": now_iso(),
    }


def run(hoje: date | None = None) -> dict:
    hoje = hoje or date.today()
    f260 = load_json(ROOT / "config/fontes_captacao_260.json").get("fontes", [])
    idx = SAIDA / "indice.json"
    dossies = {}
    if idx.exists():
        for it in load_json(idx).get("itens", []):
            pasta = ROOT / (it.get("pasta") or "")
            if (pasta / "dossie.json").exists():
                dossies[it["id"]] = load_json(pasta / "dossie.json")
    # liga 260 ↔ dossiê pelo órgão (mesma regra das fichas)
    def dossie_de(f: dict) -> dict:
        """Casamento ESTRITO. O casamento frouxo por órgão fazia 20 fontes
        distintas herdarem o mesmo dossiê de 41 editais — e cada uma sair como
        'eventual observado' com histórico que não é dela. Aqui, ou o dossiê é
        da própria fonte, ou ela é tratada como sem observação."""
        if f["id"] in dossies:
            return dossies[f["id"]]
        toks = {t for t in re.findall(r"[a-zà-ú]{6,}", (f.get("orgao") or "").lower())
                if t not in ("municipal", "estadual", "federal", "secretaria", "conselho",
                             "governo", "prefeitura", "goiania", "estado")}
        if len(toks) < 2:
            return {}
        for d in dossies.values():
            alvo = (d.get("fonte", {}).get("nome") or "").lower()
            if all(t in alvo for t in toks) and d.get("editais_no_historico"):
                return d
        return {}

    pareceres = []
    for f in f260:                                  # ← uma fonte por vez
        p = parecer_da_fonte(f, dossie_de(f), hoje)
        pareceres.append(p)
        write_json(SAIDA / slug(f["id"]) / "parecer_prazo.json", p)
    pareceres.sort(key=lambda p: (not p["goias"], p["regime_de_prazo"], p["programa"]))

    regimes = Counter(p["regime_de_prazo"] for p in pareceres)
    por_area: dict[str, Counter] = defaultdict(Counter)
    for p in pareceres:
        a = ("cultura" if "cultur" in f'{p["programa"]}{p["orgao"]}'.lower() else
             "esporte" if "esport" in f'{p["programa"]}{p["orgao"]}'.lower() else
             "fundo" if "fundo" in f'{p["programa"]}{p["orgao"]}'.lower() else "demais")
        por_area[a][p["regime_de_prazo"]] += 1
    resumo = {
        "gerado_em": now_iso(), "fontes": len(pareceres),
        "permanentes": sum(1 for p in pareceres if p["permanente"]),
        "periodicos": sum(1 for p in pareceres if p["periodico"]),
        "com_datas_conhecidas": sum(1 for p in pareceres if p["datas"]),
        "regimes": dict(regimes.most_common()),
        "por_area": {a: dict(c) for a, c in por_area.items()},
        "goias": {"fontes": sum(1 for p in pareceres if p["goias"]),
                  "permanentes": sum(1 for p in pareceres if p["goias"] and p["permanente"]),
                  "com_datas": sum(1 for p in pareceres if p["goias"] and p["datas"])},
        "lista": [{k: p[k] for k in ("id", "programa", "orgao", "nivel", "uf", "goias",
                                     "regime_de_prazo", "permanente", "periodico",
                                     "certeza", "editais_observados",
                                     "editais_com_prazo_publicado")}
                  | {"proxima_data": (p["datas"][0] if p["datas"] else None)}
                  for p in pareceres],
        "nota": ("regime classificado uma fonte por vez; janela de regramento tem certeza "
                 "alta, janela histórica declarada fica 'a confirmar', e um único ano de "
                 "observação nunca é tratado como sazonalidade"),
    }
    write_json(RELATORIO, resumo)
    return resumo


if __name__ == "__main__":
    r = run()
    print(json.dumps({k: v for k, v in r.items() if k != "lista"}, ensure_ascii=False, indent=2))
