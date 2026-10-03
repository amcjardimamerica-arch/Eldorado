"""SELO DO LIVRO — OURO · PRATA · BRONZE pelo histórico dos últimos 3 anos (titular, 03/10/2026).

A OPORTUNIDADE já tem o seu selo (estrela: site oficial → prata; + prazo e os 12 dados → ouro; senão bronze). O LIVRO
passa a ter o seu próprio selo (ícone de livro, ao lado da estrela), que mede o quanto o histórico permite PREVER a
próxima edição:

  OURO    edições em 2 ou mais anos distintos nos últimos 3 anos, ao menos uma de ano anterior ao atual com página
          oficial (não agregador/notícia) e data de inscrição — recorrência comprovada: mês típico e próxima janela
          com confiança
  PRATA   há histórico anterior ao ano atual (1 edição datada, ou 2+ anos sem data/página oficial completas) — a
          recorrência é provável, mas falta prova para prever com segurança
  BRONZE  nenhuma edição anterior ao ano atual na janela de 3 anos (só a edição corrente, ou nada) — o livro precisa
          da coleta dos 3 anos

Edição = registro do histórico do livro (`historico`) ou janela de inscrição (`livro.inscricao.janelas`) com data
dentro da janela; registros do mesmo ano/mês são a MESMA edição (vários motores vendo o mesmo edital). O ano da
edição é o da PUBLICAÇÃO/abertura (nunca o da vigência — credenciamento até 2031 não é edição de 2031).

Também ordena a COLETA dos 3 anos: Goiás → Brasil (nacional) → internacional → demais estados, separados por tipo
de oportunidade. Saídas: `selo_livro` em cada livro de biblioteca_alexandria/fontes/motores.json e
docs/dados/selos_livros.json (resumo, blocos e filas de coleta GO/BR/INT). Sem IA, biblioteca-padrão, nada inventado.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "biblioteca_alexandria/fontes/motores.json"
SAIDA = ROOT / "docs/dados/selos_livros.json"
FILAS = ROOT / "dados/coleta_3_anos"
ANOS = 3
UFS = set("AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split())
BLOCOS = ("GO", "BR", "INT", "UF")                       # ordem de resolução pedida pelo titular
NOME_BLOCO = {"GO": "Goiás", "BR": "Brasil (nacional)", "INT": "Internacional", "UF": "Demais estados"}


def hoje_brt() -> date:
    return datetime.now(timezone(timedelta(hours=-3))).date()


def _d(s) -> date | None:
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", str(s or ""))
    try:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None
    except ValueError:
        return None


def _oficial(u: str | None) -> bool:
    if not u or not str(u).startswith("http"):
        return False
    try:
        from .sites_oficiais import e_republicador
        return not e_republicador(u)
    except Exception:  # noqa: BLE001
        return not re.search(r"capitaai|observatorio3setor|prosas|captadores|editaisculturais|jusbrasil|queridodiario|google\.", u, re.I)


def edicoes(x: dict, hoje: date | None = None) -> list[dict]:
    """Edições do livro na janela de 3 anos, uma por ano/mês, com o melhor dado de cada uma."""
    hoje = hoje or hoje_brt()
    ini = hoje.replace(year=hoje.year - ANOS) if not (hoje.month == 2 and hoje.day == 29) else hoje - timedelta(days=365 * ANOS)
    brutos = []
    for h in x.get("historico") or []:
        d = _d(h.get("publicado_em")) or _d(h.get("inicio"))
        if not d:
            continue
        brutos.append({"data": d, "fim": _d(h.get("fim")), "inicio": _d(h.get("inicio")), "url": h.get("pagina_oficial") or h.get("url"),
                       "titulo": str(h.get("titulo") or "")[:160], "decisao": h.get("decisao")})
    for j in ((x.get("livro") or {}).get("inscricao") or {}).get("janelas") or []:
        d = _d(j.get("inicio"))
        if d:
            brutos.append({"data": d, "fim": _d(j.get("fim")), "inicio": d, "url": None, "titulo": "janela de inscrição registrada", "decisao": None})
    por_mes: dict[str, dict] = {}
    for b in brutos:
        if not (ini <= b["data"] <= hoje):
            continue
        k = b["data"].strftime("%Y-%m")
        a = por_mes.setdefault(k, {"mes": k, "ano": b["data"].year, "abertura": None, "encerramento": None, "pagina_oficial": None,
                                   "fontes": 0, "titulo": b["titulo"]})
        a["fontes"] += 1
        a["abertura"] = min(filter(None, [a["abertura"], b["inicio"] or b["data"]]), default=None)
        if b["fim"] and b["fim"] >= b["data"] and (b["fim"] - b["data"]).days <= 400:     # vigência longa não é prazo de inscrição
            a["encerramento"] = max(filter(None, [a["encerramento"], b["fim"]]), default=None)
        if not a["pagina_oficial"] and _oficial(b["url"]):
            a["pagina_oficial"] = b["url"]
    out = sorted(por_mes.values(), key=lambda e: e["mes"])
    for e in out:
        e["abertura"] = e["abertura"].isoformat() if e["abertura"] else None
        e["encerramento"] = e["encerramento"].isoformat() if e["encerramento"] else None
    return out


def bloco(x: dict) -> str:
    geo = str(x.get("geo") or x.get("uf") or "")
    if x.get("internacional") or geo == "INT":
        return "INT"
    if geo == "GO":
        return "GO"
    if geo in UFS:
        return "UF"
    return "BR"


def avaliar(x: dict, hoje: date | None = None) -> dict:
    hoje = hoje or hoje_brt()
    E = edicoes(x, hoje)
    anos = sorted({e["ano"] for e in E})
    anteriores = [e for e in E if e["ano"] < hoje.year]
    prova = [e for e in anteriores if e["pagina_oficial"] and (e["encerramento"] or e["abertura"])]
    if len(anos) >= 2 and prova:
        selo, porque = "ouro", f"edições em {len(anos)} anos ({', '.join(map(str, anos))}), com edição anterior comprovada em página oficial"
    elif anteriores:
        selo, porque = "prata", (f"histórico anterior a {hoje.year} ({', '.join(str(e['ano']) for e in anteriores)}), "
                                 + ("sem página oficial ou data de inscrição para prever com segurança" if not prova else "recorrência em um só ano"))
    else:
        selo, porque = "bronze", ("só a edição de " + str(hoje.year) if E else "nenhuma edição registrada") + " nos últimos 3 anos — coletar o histórico"
    meses = [int(e["abertura"][5:7]) for e in E if e["abertura"]]
    duracoes = [(date.fromisoformat(e["encerramento"]) - date.fromisoformat(e["abertura"])).days for e in E if e["abertura"] and e["encerramento"]]
    mes_tipico = Counter(meses).most_common(1)[0][0] if meses else None
    falta = []
    if selo != "ouro":
        if len(anos) < 2:
            falta.append("edições de 2023–2025 (mesmo órgão e mesmo programa)")
        if not prova:
            falta.append("página oficial e datas de inscrição de uma edição anterior")
    return {"selo": selo, "porque": porque, "janela": f"{hoje.replace(year=hoje.year - ANOS).isoformat()} a {hoje.isoformat()}",
            "teve_edital_3_anos": bool(anteriores), "anos_com_edicao": anos, "edicoes_3_anos": len(E), "edicoes": E[-8:],
            "preditivo": {"mes_tipico": mes_tipico, "duracao_tipica_dias": sorted(duracoes)[len(duracoes) // 2] if duracoes else None,
                          "proxima_janela": (f"{hoje.year + (1 if mes_tipico and mes_tipico < hoje.month else 0)}-{mes_tipico:02d}" if mes_tipico else None),
                          "confianca": {"ouro": "alta", "prata": "media", "bronze": "baixa"}[selo]},
            "falta_para_ouro": falta, "bloco": bloco(x), "tipo": x.get("tipo_objeto") or "Edital", "em": hoje.isoformat()}


ENTRADA = FILAS / "entrada"


def incorporar(livros: list[dict]) -> int:
    """Coletas dos 3 anos (prompts GO/BR/INT) → edições no histórico do livro. Arquivo:
    dados/coleta_3_anos/entrada/<bloco>_AAAA-MM-DD.json = {"<id do livro>": {"edicoes": [{"ano", "titulo", "abertura",
    "encerramento", "pagina_oficial", "valor", "trecho"}], "observacao": "..."}}. Só entra edição com página oficial e
    ano; nada sem prova. Idempotente (mesma página + mesmo ano não entra duas vezes)."""
    if not ENTRADA.exists():
        return 0
    por_id = {x.get("id"): x for x in livros}; n = 0
    for arq in sorted(ENTRADA.glob("*.json")):
        try:
            d = json.loads(arq.read_text(encoding="utf-8"))
        except ValueError:
            continue
        for lid, v in (d.items() if isinstance(d, dict) else []):
            x = por_id.get(lid)
            if not x or not isinstance(v, dict):
                continue
            hist = x.setdefault("historico", [])
            vistos = {(str(h.get("pagina_oficial") or ""), str(h.get("ano") or "")) for h in hist}
            for e in v.get("edicoes") or []:
                ano = str(e.get("ano") or str(e.get("abertura") or "")[:4])
                if not (e.get("pagina_oficial") and re.fullmatch(r"20\d{2}", ano)) or (str(e["pagina_oficial"]), ano) in vistos:
                    continue
                hist.append({"id": "c3a-" + re.sub(r"[^a-z0-9]", "", (lid + ano + str(e.get("abertura") or "")).lower())[:24],
                             "titulo": str(e.get("titulo") or x.get("programa") or "")[:200], "ano": ano,
                             "publicado_em": e.get("abertura") or f"{ano}-01-01", "inicio": e.get("abertura"), "fim": e.get("encerramento"),
                             "pagina_oficial": e["pagina_oficial"], "valor": e.get("valor"), "trecho": str(e.get("trecho") or "")[:300],
                             "origem": f"coleta 3 anos ({arq.name})"})
                vistos.add((str(e["pagina_oficial"]), ano)); n += 1
    return n


def aplicar(hoje: date | None = None, gravar: bool = True) -> dict:
    hoje = hoje or hoje_brt()
    C = json.loads(CAT.read_text(encoding="utf-8"))
    livros = C.get("motores") or []
    novas = incorporar(livros)
    blocos: dict[str, dict] = {b: defaultdict(list) for b in BLOCOS}
    cont = Counter()
    for x in livros:
        s = avaliar(x, hoje)
        x["selo_livro"] = s
        cont[s["selo"]] += 1
        blocos[s["bloco"]][s["tipo"]].append({"id": x.get("id"), "nome": x.get("nome_classificado") or x.get("programa"), "selo_livro": s["selo"],
                                              "selo_oportunidade": (x.get("esteira") or {}).get("selo"), "anos": s["anos_com_edicao"],
                                              "orgao": x.get("orgao"), "municipio": x.get("municipio"), "uf": x.get("geo"),
                                              "pagina": x.get("pagina"), "falta": s["falta_para_ouro"]})
    ordem = {"bronze": 0, "prata": 1, "ouro": 2}
    res = {"gerado_em": hoje.isoformat(), "regra": __doc__.split("Também")[0].strip(), "livros": len(livros), "por_selo": dict(cont),
           "ordem_de_resolucao": [NOME_BLOCO[b] for b in BLOCOS], "blocos": {}}
    for b in BLOCOS:
        tipos = {t: sorted(v, key=lambda r: (ordem[r["selo_livro"]], str(r["nome"]))) for t, v in sorted(blocos[b].items(), key=lambda kv: -len(kv[1]))}
        res["blocos"][b] = {"nome": NOME_BLOCO[b], "total": sum(len(v) for v in tipos.values()),
                            "por_selo": dict(Counter(r["selo_livro"] for v in tipos.values() for r in v)),
                            "por_tipo": {t: len(v) for t, v in tipos.items()}, "tipos": tipos}
    if gravar:
        CAT.write_text(json.dumps(C, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        SAIDA.parent.mkdir(parents=True, exist_ok=True)
        SAIDA.write_text(json.dumps(res, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        FILAS.mkdir(parents=True, exist_ok=True)
        for b in ("GO", "BR", "INT"):                       # filas das 3 coletas (só quem ainda não é ouro)
            fila = [{**r, "tipo": t} for t, v in res["blocos"][b]["tipos"].items() for r in v if r["selo_livro"] != "ouro"]
            (FILAS / f"fila_{b.lower()}.json").write_text(json.dumps({"bloco": NOME_BLOCO[b], "gerado_em": hoje.isoformat(), "total": len(fila),
                                                                     "itens": fila}, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"livros": len(livros), "por_selo": dict(cont), "por_bloco": {b: res["blocos"][b]["total"] for b in BLOCOS}, "edicoes_coletadas_novas": novas}


def selo_por_livro() -> dict[str, str]:
    try:
        C = json.loads(CAT.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return {x["id"]: (x.get("selo_livro") or {}).get("selo") for x in C.get("motores") or [] if x.get("selo_livro")}


if __name__ == "__main__":
    print(json.dumps(aplicar(), ensure_ascii=False, indent=1))
