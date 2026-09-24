#!/usr/bin/env python3
"""A BASE SÓLIDA DA BIBLIOTECA — leve, textual, por pastas, de leitura imediata.

O que o sistema tinha: 3.946 arquivos JSON espalhados, uma ficha por pasta, os vereditos do titular
guardados FORA da Biblioteca (em dados/editais/extraidos) e uma "previsão" construída sobre edições de
diário (Betim/MG a cada mês não é edital que volta: é o diário que sai). Nada disso era base para
direcionar motor, Piloto ou Farol.

O que esta base produz, em biblioteca_alexandria/base/ (JSONL: uma linha por registro, abre em qualquer
ferramenta, grep e pandas leem em milissegundos):

    editais/<ano>.jsonl        HISTÓRICO — todo edital conhecido, um esquema só, com o veredito do titular
    aprovados.jsonl            os editais que o titular selecionou: a base de pontuação
    recorrencia.jsonl          PREDITIVO — quem publica de novo, em que mês, com que força; próxima janela
    pontuacao/criterios.json   o que separa aprovado de reprovado, medido: pesos por tema, esfera, UF,
                               órgão recorrente, faixa de valor, exigências
    leis/indice_por_esfera.json + lacunas.json   o que a Biblioteca de leis cobre e o que falta para
                               Goiás, Goiânia e a Região Metropolitana

Regra: edição de diário nunca entra (é matéria-prima, vive no índice de diários). Só entra o que tem
título e fonte; o veredito só vem do titular.

    python3 scripts/construir_base.py
"""
from __future__ import annotations

import collections
import csv
import json
import re
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from src.nucleo import chave_curta  # noqa: E402

B = RAIZ / "biblioteca_alexandria"
BASE = B / "base"
UFS_ABRANGENCIA = {"GO"}
NACIONAL = {"nacional", "federal", "BR", ""}


def ler(p: Path, padrao=None):
    try:
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else padrao
    except Exception:
        return padrao


def jsonl(p: Path, linhas: list[dict]):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in linhas), encoding="utf-8")


def _data(*vals) -> str | None:
    for v in vals:
        s = str(v or "")[:10]
        if re.match(r"\d{4}-\d{2}-\d{2}$", s):
            return s
        m = re.search(r"(\d{2})/(\d{2})/(\d{4})", str(v or ""))
        if m:
            return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    return None


def _e_edicao_de_diario(d: dict) -> bool:
    return str(d.get("fonte_id") or "") == "querido-diario" and bool(re.search(r"di[aá]rio oficial", str(d.get("titulo") or ""), re.I))


def historico() -> tuple[list[dict], list[dict]]:
    ext = {}
    for f in (RAIZ / "dados/editais/extraidos").glob("*.json"):
        d = ler(f)
        if isinstance(d, dict):
            ext[chave_curta(f.stem)] = d
    familias = {}
    g = RAIZ / "dados/verificacao/parecer_2026-09-23/EXCLUIR-2026-09-23.csv"
    if g.exists():
        for r in csv.DictReader(open(g, encoding="utf-8-sig"), delimiter=";"):
            familias[chave_curta(r.get("id", ""))] = r.get("familia")
    linhas = []
    vistos = set()
    for f in (B / "oportunidades").glob("*/*/ficha.json"):
        d = ler(f)
        if not isinstance(d, dict) or _e_edicao_de_diario(d):
            continue
        k = chave_curta(d.get("id") or f.parent.parent.name)
        if k in vistos:
            continue
        vistos.add(k)
        e = ext.get(k) or {}
        vi = e.get("validacao_individual") if isinstance(e.get("validacao_individual"), dict) else {}
        ve = e.get("verificacao_externa") if isinstance(e.get("verificacao_externa"), dict) else {}
        pub = _data(d.get("data_publicacao"), d.get("inicio"), e.get("inicio"), ve.get("inicio"))
        uf = (d.get("uf") or e.get("uf") or "").upper()
        linhas.append({
            "id": k, "chave": d.get("chave") or f.parent.parent.name, "titulo": (d.get("titulo") or "")[:200],
            "orgao": d.get("orgao") or e.get("orgao"), "esfera": d.get("nivel") or e.get("nivel"),
            "uf": uf, "territorio": d.get("territorio"), "tema": d.get("area") or e.get("area"),
            "programa": d.get("programa"), "ano": str(d.get("ano") or (pub or "")[:4] or ""),
            "publicado_em": pub, "inicio": _data(d.get("inicio"), e.get("inicio")),
            "fim": _data(d.get("fim"), e.get("fim"), ve.get("prazo")), "valor": d.get("valor") or e.get("valor"),
            "fonte_id": d.get("fonte_id"), "url": d.get("url"), "pagina_oficial": ve.get("pagina_oficial") or e.get("pagina_oficial"),
            "exigencias": (d.get("exigencias_detectadas") or [])[:12],
            "veredito": vi.get("veredito") or vi.get("resultado"), "motivo": (vi.get("motivo") or vi.get("observacao") or "")[:160] or None,
            "familia_descarte": familias.get(k), "pertinencia_pncp": e.get("pertinencia_pncp"),
            "verificado_em": ve.get("em") or e.get("verificado_em"),
            "abrangencia": "nacional" if (d.get("territorio") in NACIONAL or d.get("nivel") == "federal") else ("goias" if uf == "GO" else "fora"),
        })
    aprovados = [x for x in linhas if x["veredito"] == "aprovado"]
    return linhas, aprovados


def recorrencia(linhas: list[dict]) -> list[dict]:
    """Quem publica de novo. Só edital de verdade, só dentro da abrangência, agrupado por órgão e tema."""
    hoje = date.today()
    grupos = collections.defaultdict(list)
    for x in linhas:
        if not x.get("publicado_em") or x["abrangencia"] == "fora" or not x.get("orgao"):
            continue
        grupos[(x["orgao"], x.get("tema") or "outros")].append(x)
    saida = []
    for (orgao, tema), xs in grupos.items():
        anos = sorted({x["publicado_em"][:4] for x in xs})
        meses = collections.Counter(int(x["publicado_em"][5:7]) for x in xs)
        mes, _ = meses.most_common(1)[0]
        duracoes = [(date.fromisoformat(x["fim"]) - date.fromisoformat(x["publicado_em"])).days
                    for x in xs if x.get("fim") and x["fim"] > x["publicado_em"]]
        prox_ano = hoje.year if mes >= hoje.month else hoje.year + 1
        saida.append({"orgao": orgao, "tema": tema, "anos": anos, "forca": len(anos), "mes_tipico": mes,
                      "duracao_tipica_dias": round(sum(duracoes) / len(duracoes)) if duracoes else None,
                      "proxima_janela": f"{prox_ano}-{mes:02d}", "aprovados": sum(1 for x in xs if x["veredito"] == "aprovado"),
                      "exemplos": [x["id"] for x in xs[:3]]})
    saida.sort(key=lambda r: (-r["forca"], -r["aprovados"], r["proxima_janela"]))
    return saida


def criterios(linhas: list[dict]) -> dict:
    """O que separa aprovado de reprovado, medido no que o titular já julgou."""
    ap = [x for x in linhas if x["veredito"] == "aprovado"]
    re_ = [x for x in linhas if x["veredito"] in ("reprovado", "ruido")]
    def taxa(chave, f=lambda v: v):
        a = collections.Counter(f(x.get(chave)) for x in ap); r = collections.Counter(f(x.get(chave)) for x in re_)
        out = {}
        for k in set(a) | set(r):
            if k in (None, "", "None"):
                continue
            n = a[k] + r[k]
            if n >= 3:
                out[str(k)] = {"aprovados": a[k], "reprovados": r[k], "taxa": round(a[k] / n, 2)}
        return dict(sorted(out.items(), key=lambda kv: -kv[1]["taxa"]))
    def faixa(v):
        try:
            v = float(str(v).replace(".", "").replace(",", "."))
        except Exception:
            return None
        return "ate_50k" if v <= 50_000 else "50k_200k" if v <= 200_000 else "200k_1M" if v <= 1_000_000 else "acima_1M"
    exig_a = collections.Counter(e for x in ap for e in x.get("exigencias") or [])
    exig_r = collections.Counter(e for x in re_ for e in x.get("exigencias") or [])
    exig = {e: {"aprovados": exig_a[e], "reprovados": exig_r[e]} for e in exig_a if exig_a[e] >= 3}
    return {"em": date.today().isoformat(), "base": {"aprovados": len(ap), "reprovados": len(re_)},
            "regra": "peso = taxa de aprovação observada; critério sem 3 casos não pontua; o veredito só vem do titular",
            "por_tema": taxa("tema"), "por_esfera": taxa("esfera"), "por_uf": taxa("uf"), "por_abrangencia": taxa("abrangencia"),
            "por_fonte": taxa("fonte_id"), "por_faixa_de_valor": taxa("valor", faixa),
            "orgaos_com_aprovados": collections.Counter(x["orgao"] for x in ap if x.get("orgao")).most_common(20),
            "exigencias_frequentes": dict(sorted(exig.items(), key=lambda kv: -kv[1]["aprovados"])[:25])}


LACUNAS_LEIS = [
    {"esfera": "municipal-goiania", "norma": "Lei Orgânica do Município de Goiânia", "por_que": "base de competências e subvenções municipais"},
    {"esfera": "municipal-goiania", "norma": "Lei municipal de incentivo à cultura de Goiânia (Lei nº 9.154/2012 ou vigente)", "por_que": "incentivo fiscal municipal (ISS/IPTU) a projetos culturais"},
    {"esfera": "municipal-goiania", "norma": "Decreto municipal que regulamenta o MROSC em Goiânia", "por_que": "rito local de chamamento, termo de fomento e prestação de contas"},
    {"esfera": "municipal-goiania", "norma": "Lei do FMDCA e do FMAS de Goiânia; resoluções do CMDCA e do CMAS", "por_que": "registro no conselho e editais dos fundos"},
    {"esfera": "municipal-goiania", "norma": "LDO e LOA de Goiânia (anexo de subvenções e emendas impositivas)", "por_que": "onde as emendas e subvenções são autorizadas"},
    {"esfera": "estadual-goias", "norma": "Decreto estadual que regulamenta a Lei 13.019 em Goiás", "por_que": "rito estadual de parceria"},
    {"esfera": "estadual-goias", "norma": "Lei do Pró-Esporte/incentivo ao esporte de Goiás e regulamento", "por_que": "incentivo fiscal estadual ao esporte"},
    {"esfera": "estadual-goias", "norma": "Lei do Fundo Estadual de Cultura / Goyazes (regulamentos e portarias da Secult)", "por_que": "já há a lei; faltam os regulamentos e o rito de prestação de contas"},
    {"esfera": "estadual-goias", "norma": "Resoluções do CEDCA-GO e do CEAS-GO", "por_que": "fundos estaduais e certificação"},
    {"esfera": "estadual-goias", "norma": "Instruções normativas do TCE-GO e do TCM-GO sobre parcerias com OSC", "por_que": "como os tribunais de contas fiscalizam o repasse"},
    {"esfera": "rmg", "norma": "Lei Complementar da Região Metropolitana de Goiânia (LC 27/1999 e atualizações) e o Codemetro", "por_que": "instrumentos e fundos metropolitanos"},
    {"esfera": "federal", "norma": "Lei 14.133/2021 (contratações) — os artigos de credenciamento e concurso", "por_que": "é por onde o PNCP publica o que serve à OSC"},
    {"esfera": "federal", "norma": "Lei 12.101/2009 e Lei Complementar 187/2021 (CEBAS)", "por_que": "certificação de entidade beneficente"},
    {"esfera": "federal", "norma": "Lei 14.399/2022 (PNAB) e LC 195/2022 (Paulo Gustavo) com decretos", "por_que": "fomento cultural descentralizado a municípios de Goiás"},
    {"esfera": "federal", "norma": "Decreto 8.726/2016 (regulamento do MROSC) e Portaria conjunta de prestação de contas", "por_que": "rito federal de parceria"},
    {"esfera": "judiciario", "norma": "Resolução CNJ 154/2012 e provimentos da CGJ-GO sobre prestação pecuniária", "por_que": "cadastro de entidades nas varas de execução penal"},
]


def leis() -> tuple[dict, list[dict]]:
    idx = ler(B / "leis/indice.json", {}) or {}
    itens = [x for xs in (idx.get("por_tema") or {}).values() for x in (xs if isinstance(xs, list) else [])]
    def esfera(x):
        t = json.dumps(x, ensure_ascii=False).lower()
        if re.search(r"goi[âa]nia|municipal", t): return "municipal-goiania"
        if re.search(r"goi[áa]s|estadual|goyazes|tjgo|alego", t): return "estadual-goias"
        if re.search(r"cnj|tjgo|tribunal|provimento", t): return "judiciario"
        return "federal"
    por = collections.defaultdict(list)
    for x in itens:
        por[esfera(x)].append({"id": x.get("id"), "titulo": x.get("titulo") or x.get("nome"), "tema": x.get("tema")})
    presentes = {x["id"] for x in itens if x.get("id")}
    return ({"em": date.today().isoformat(), "total": len(itens), "por_esfera": {k: len(v) for k, v in por.items()},
             "itens": dict(por),
             "aplicacao": "Goiás e Região Metropolitana de Goiânia: toda norma federal se aplica; a estadual vale no estado; "
                          "a municipal só em Goiânia — os outros 19 municípios da RMG têm leis próprias, não cobertas"},
            [dict(l, presente=False) for l in LACUNAS_LEIS if not any(p and p in l["norma"].lower() for p in presentes)])


def main() -> dict:
    linhas, aprovados = historico()
    por_ano = collections.defaultdict(list)
    for x in linhas:
        por_ano[x["ano"] or "sem-ano"].append(x)
    for ano, xs in por_ano.items():
        jsonl(BASE / "editais" / f"{ano}.jsonl", xs)
    jsonl(BASE / "aprovados.jsonl", aprovados)
    rec = recorrencia(linhas)
    jsonl(BASE / "recorrencia.jsonl", rec)
    crit = criterios(linhas)
    (BASE / "pontuacao").mkdir(parents=True, exist_ok=True)
    (BASE / "pontuacao/criterios.json").write_text(json.dumps(crit, ensure_ascii=False, indent=1), encoding="utf-8")
    inv, lac = leis()
    (BASE / "leis").mkdir(parents=True, exist_ok=True)
    (BASE / "leis/indice_por_esfera.json").write_text(json.dumps(inv, ensure_ascii=False, indent=1), encoding="utf-8")
    (BASE / "leis/lacunas.json").write_text(json.dumps({"em": date.today().isoformat(), "lacunas": lac}, ensure_ascii=False, indent=1), encoding="utf-8")
    resumo = {"em": date.today().isoformat(), "editais": len(linhas), "por_ano": {k: len(v) for k, v in sorted(por_ano.items())},
              "com_veredito": sum(1 for x in linhas if x["veredito"]), "aprovados": len(aprovados),
              "com_data_de_publicacao": sum(1 for x in linhas if x["publicado_em"]), "com_prazo": sum(1 for x in linhas if x["fim"]),
              "com_orgao": sum(1 for x in linhas if x["orgao"]), "recorrencias": len(rec),
              "recorrencias_fortes": sum(1 for r in rec if r["forca"] >= 2), "leis": inv["por_esfera"], "lacunas_de_leis": len(lac)}
    (BASE / "resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=1), encoding="utf-8")
    (BASE / "README.md").write_text(__doc__.split("Regra:")[0].strip() + "\n", encoding="utf-8")
    return resumo


if __name__ == "__main__":
    print(json.dumps(main(), ensure_ascii=False, indent=1))
