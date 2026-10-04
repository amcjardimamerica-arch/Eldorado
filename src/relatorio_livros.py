"""RELATÓRIO POR LIVRO PARA ESTUDO PREDITIVO + 12 ITENS DAS EDIÇÕES ANTERIORES (titular, 03/10/2026).

Para cada livro (oportunidade recorrente) gera um relatório com:
  1. as edições dos últimos 3 anos (`historico`), cada uma com os 12 itens do edital em quatro estados honestos:
       confirmado       — lido na página oficial da edição (trecho literal em `itens12`) ou campo comprovado da edição
       catalogo         — dado do livro (órgão, território, esfera), não lido na edição
       dispensa_edital  — o próprio edital diz que o item não existe
       dispensa_tipo    — o regime do recurso (config/dispensas_por_regime.json) costuma não ter o item (PROVÁVEL)
       nao_localizado   — ainda não lido
  2. o estudo preditivo: mês típico, duração típica, próxima janela, antecedência do aviso, regras que se repetem;
  3. o conselho de 7 lentes (extremamente pessimista → extremamente otimista) com o neutro decidindo;
  4. a situação de validação do livro: validado | dispensa individual documentada | pendente de coleta.
Sem IA, biblioteca-padrão, nada inventado: o que não foi lido aparece como `nao_localizado`.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import date
from pathlib import Path

from .dispensas_itens import ITENS, matriz, regime, regime_do_motor
from .selo_livros import CAT, ROOT, _d, hoje_brt

SAIDA = ROOT / "dados/coleta_3_anos/relatorios"
RESUMO = ROOT / "docs/dados/relatorios_livros.json"
MESES = "jan fev mar abr mai jun jul ago set out nov dez".split()

# livros sem série comparável: dispensa INDIVIDUAL documentada (motivo escrito no próprio livro pela coleta)
_FORA_ESCOPO = re.compile(r"aquisi[cç][ãa]o de (g[êe]neros|medicamentos|equipamentos)|g[êe]neros aliment[íi]cios|servi[cç]os m[ée]dicos|plant[õo]es|farmac[êe]utic|laborat[óo]rios de an[áa]lises|im[óo]vel apto|loca[cç][ãa]o|registro de pre[cç]os|catadores|material rodante|especialidades m[ée]dicas|aparelhos auditivos|transporte de pacientes|remo[cç][ãa]o de pacientes", re.I)

_DISPENSA_LIVRO = [
    (r"n[ãa]o [ée] oportunidade de capta", "arquivar", "Não é captação (serviço público/ruído do motor): arquivar o livro, sem estudo preditivo."),
    (r"estrutural", "estrutural", "Oportunidade estrutural (catálogo de financiador): a recorrência depende do ciclo do financiador, não de edital próprio."),
    (r"emenda parlamentar|^emenda", "emenda", "Emenda parlamentar: não há edital; a janela vem da LOA e da indicação do parlamentar (itens de edital dispensados pelo regime)."),
    (r"presta[cç][ãa]o pecuni[áa]ria", "judicial", "Destinação judicial: sem edição própria comparável; valor e escolha são atos do juízo."),
    (r"Minist[ée]rio P[úu]blico", "mp", "Ministério Público: a tabela oficial só lista editais vigentes; sem série anterior publicada."),
    (r"FIA/CEDCA|FMDCA|fundos", "fundo", "Fundo de conselho: o edital segue o calendário do conselho; histórico depende de resoluções do conselho."),
]


# Dispensa individual por NATUREZA do livro (decidida livro a livro pela leitura do título e do regime, 03/10/2026)
_DISPENSA_NOME = [
    (r"^Edital n[ºo°]\.? ?\d+/2023 .*lei paulo gustavo", "ciclo_unico",
     "Ciclo único da Lei Paulo Gustavo (2023): o edital é a própria edição de 2023; a recorrência estadual passou à PNAB (livro próprio). Sem série anterior a comparar."),
    (r"^(Resultado|Divulgado resultado|Termos? de Fomento|Termo de Fomento|Secult Goiás divulga plano de ação|Goiás Social — Governo de Goiás confere|Pdf edital de credenciamento)", "ato_derivado",
     "Ato derivado de um edital (resultado, termo ou plano de ação): não tem prazo próprio; o estudo preditivo vale para o livro do edital-mãe."),
    (r"^(Convênios e parcerias|Organizações sociais|Consulta de Emendas|Editais de Chamamento Público|Editais - Minist|Plataforma_pid|Chamamento público — Goiás|Termos de Fomento)", "indice",
     "Página-índice/portal (lista de editais ou serviço), não um edital: o estudo preditivo está nos livros dos editais listados."),
]
_DISPENSA_REGIME = {
    "incentivo_fiscal": ("Incentivo fiscal: a captação é contínua por projeto aprovado (sem edital com prazo); a janela vem do calendário da lei/portaria, itens de prazo dispensados pelo regime."),
    "destinacao_judicial": ("Destinação judicial: sem edição própria comparável; valor e escolha são atos do juízo."),
    "emenda_parlamentar": ("Emenda parlamentar: não há edital; a janela vem da LOA e da indicação do parlamentar."),
    "doacao_de_bens": ("Doação de bens: sem edital com prazos fixos; a oferta segue o fluxo do órgão doador."),
    "fluxo_continuo": ("Programa de fluxo contínuo: sem janela de inscrição; itens de prazo, resultado e recurso dispensados pelo regime."),
}
_MANUAL = ROOT / "dados/coleta_3_anos/classificacao_livros.json"


def _manual() -> dict:
    try:
        return json.loads(_MANUAL.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _item_status(nome: str, ed: dict, x: dict, reg: str) -> dict:
    it = (ed.get("itens12") or {}).get(nome)
    if isinstance(it, dict) and it.get("valor"):
        return {"estado": it.get("estado", "confirmado"), "valor": it["valor"], "trecho": it.get("trecho")}
    if isinstance(it, dict) and it.get("estado") == "nao_localizado":
        return {"estado": "nao_localizado", "valor": None, "porque": it.get("porque")}
    if isinstance(it, str) and it:
        return {"estado": "confirmado", "valor": it}
    if nome == "Objeto" and ed.get("titulo"):
        return {"estado": "confirmado", "valor": ed["titulo"][:200], "fonte": "título da edição"}
    if nome == "Prazo de inscrição" and (ed.get("abertura") or ed.get("encerramento")):
        return {"estado": "confirmado", "valor": f"{ed.get('abertura') or '?'} a {ed.get('encerramento') or '?'}", "fonte": "datas da edição"}
    if nome == "Valor" and ed.get("valor"):
        return {"estado": "confirmado", "valor": str(ed["valor"])}
    if nome == "Órgão / financiador" and x.get("orgao"):
        return {"estado": "catalogo", "valor": x["orgao"]}
    if nome == "Território":
        return {"estado": "catalogo", "valor": x.get("municipio") or x.get("geo") or x.get("uf") or "?"}
    if nome == "Esfera" and x.get("esfera"):
        return {"estado": "catalogo", "valor": x["esfera"]}
    disp = (matriz().get("regimes", {}).get(reg, {}).get("itens") or {}).get(nome)
    if disp:
        return {"estado": "dispensa_tipo", "valor": None, "porque": disp.get("porque"), "confianca": disp.get("confianca")}
    d = _derivado(nome, x)
    if d:
        return d
    return {"estado": "nao_localizado", "valor": None, "porque": _PORQUE.get(nome, "Não consta na página lida da edição; leitura do edital/anexos pendente.")}


_PORQUE = {
    "Resultado": "A data do resultado é ato posterior ao edital (publicação separada); não constava na página/PDF lido da edição. Pendência: conferir a ata/resultado no site do órgão.",
    "Prazo de recurso": "O prazo de recurso está no corpo do edital (PDF) ou na publicação do resultado; não foi lido na página da edição. Pendência explícita.",
    "Valor": "O valor global/por projeto não aparece na página lida da edição (está no edital ou na notícia de lançamento); pendência explícita.",
    "Requisitos": "Os requisitos de habilitação estão no corpo do edital (PDF), não lido nesta rodada; pendência explícita, não suposta.",
    "Anexos": "A lista de anexos está no corpo do edital (PDF), não lido nesta rodada; pendência explícita, não suposta.",
}


def _derivado(nome: str, x: dict) -> dict | None:
    """Itens que o catálogo do livro já sabe (esfera, área, destinação/público, órgão), marcados como derivados do catálogo."""
    org = str(x.get("orgao") or "")
    if nome == "Esfera":
        e = x.get("esfera") or x.get("abrangencia")
        if not e:
            if re.search(r"prefeitura|munic[íi]pi|c[âa]mara municipal|fundo municipal", org, re.I):
                e = "Municipal"
            elif re.search(r"estado|governo de|secult|goi[áa]s|seds|secretaria de estado", org, re.I) and not re.search(r"minist", org, re.I):
                e = "Estadual"
            elif re.search(r"minist[ée]rio|gov\.br|federal|funarte|bndes|iphan|ibama|mma|minc|embratur|anvisa|caixa", org, re.I):
                e = "Federal"
            elif re.search(r"funda[cç][ãa]o|instituto|banco|seguros|ita[úu]|petrobras|vale|ong|associa", org, re.I):
                e = "Privada/terceiro setor"
        if e:
            return {"estado": "catalogo", "valor": str(e), "fonte": "catálogo do livro (esfera/abrangência/órgão)"}
    if nome == "Área de atuação":
        a = x.get("objeto_area") or x.get("area_atuacao") or x.get("segmento")
        if a:
            return {"estado": "catalogo", "valor": str(a), "fonte": "catálogo do livro (área do objeto)"}
    if nome == "Destinação":
        t = x.get("tipo_objeto"); pub = x.get("publico")
        if t or pub:
            pub = ", ".join(pub) if isinstance(pub, list) else (pub or "")
            return {"estado": "catalogo", "valor": "; ".join(v for v in [f"tipo: {t}" if t else "", f"público: {pub}" if pub else ""] if v),
                    "fonte": "catálogo do livro (tipo de objeto e público); destino exato do recurso é lido no edital"}
    if nome == "Órgão / financiador":
        v = x.get("orgao") or x.get("municipio")
        if v:
            return {"estado": "catalogo", "valor": str(v)}
    return None


def _itens_por_pagina() -> dict:
    """dados/coleta_3_anos/itens12/*.json = {"<pagina_oficial>": {"<item>": {"estado","valor","trecho"}}} lidos da própria página/PDF/API."""
    out: dict = {}
    for arq in sorted((ROOT / "dados/coleta_3_anos/itens12").glob("*.json")):
        try:
            for u, v in json.loads(arq.read_text(encoding="utf-8")).items():
                out.setdefault(u, {}).update(v)
        except ValueError:
            continue
    return out


_PAG: dict | None = None


def _edicoes_livro(x: dict) -> list[dict]:
    """Edições do histórico com ano anterior ao corrente e página oficial (a mesma base do selo), uma por ano/mês."""
    hoje = hoje_brt()
    por: dict[str, dict] = {}
    for h in x.get("historico") or []:
        d = _d(h.get("publicado_em")) or _d(h.get("inicio"))
        if not d or d.year >= hoje.year or d < hoje.replace(year=hoje.year - 3):
            continue
        e = por.setdefault(d.strftime("%Y-%m"), {"mes": d.strftime("%Y-%m"), "ano": d.year, "titulo": h.get("titulo"), "abertura": None,
                                                 "encerramento": None, "pagina_oficial": None, "valor": None, "itens12": {}})
        ini = _d(h.get("inicio")) or (None if h.get("so_encerramento") else d)   # só o encerramento lido: abertura fica nula (nada inventado)
        if ini:
            e["abertura"] = min(filter(None, [_d(e["abertura"]), ini])).isoformat()
        f = _d(h.get("fim"))
        if f and f >= d and (f - d).days <= 400:
            e["encerramento"] = max(filter(None, [_d(e["encerramento"]), f])).isoformat()
        e["pagina_oficial"] = e["pagina_oficial"] or h.get("pagina_oficial")
        e["valor"] = e["valor"] or h.get("valor")
        for k, v in (h.get("itens12") or {}).items():
            e["itens12"].setdefault(k, v)
    global _PAG
    _PAG = _PAG if _PAG is not None else _itens_por_pagina()
    for e in por.values():
        for k, v in (_PAG.get(e["pagina_oficial"] or "") or {}).items():
            e["itens12"].setdefault(k, v)
    return [por[k] for k in sorted(por)]


def _situacao(x: dict, eds: list[dict], reg: str | None = None) -> tuple[str, str]:
    selo = (x.get("selo_livro") or {}).get("selo")
    m0 = _manual().get(x.get("id"))
    if m0 and m0.get("situacao") == "dispensa_individual:ciclo_unico":     # ciclo único declarado: a própria edição não vira série
        return m0["situacao"], m0["motivo"]
    for rx, cod, motivo in _DISPENSA_NOME:
        if cod == "ciclo_unico" and re.search(rx, str(x.get("programa") or x.get("nome_classificado") or ""), re.I):
            return "dispensa_individual:" + cod, motivo
    if selo == "ouro":
        return "validado", "recorrência comprovada em 2 ou mais anos com página oficial"
    if eds:
        return "validado_parcial", "há edição anterior comprovada, mas só um ano ou sem datas completas: previsão com confiança média"
    obs = (x.get("livro_coleta") or {}).get("observacao") or ""
    if obs.startswith("SERIE CONFIRMADA"):
        return "serie_confirmada_sem_datas", obs
    if obs.startswith("VERIFICADO"):
        return "verificado_sem_serie", obs
    m = _manual().get(x.get("id"))
    if m:
        return m["situacao"], m["motivo"]
    for rx, cod, motivo in _DISPENSA_NOME:
        if re.search(rx, str(x.get("programa") or x.get("nome_classificado") or ""), re.I):
            return "dispensa_individual:" + cod, motivo
    txt = obs or ("Emenda parlamentar" if x.get("tipo_objeto") == "Emenda" else "")
    for rx, cod, motivo in _DISPENSA_LIVRO:
        if re.search(rx, txt, re.I):
            return "dispensa_individual:" + cod, motivo
    if reg in _DISPENSA_REGIME:
        return "dispensa_individual:regime_" + reg, _DISPENSA_REGIME[reg]
    return "pendente_de_coleta", obs or "sem edição anterior achada nas fontes lidas"


def _conselho(x: dict, eds: list[dict], prev: dict, sit: str) -> dict:
    n = len(eds)
    anos = sorted({e["ano"] for e in eds})
    mt = prev.get("mes_tipico")
    lacunas = Counter()
    for e in eds:
        for k in ITENS:
            if e["itens12"].get(k) is None and e["_status"][k]["estado"] == "nao_localizado":
                lacunas[k] += 1
    pior = ", ".join(k for k, _ in lacunas.most_common(3)) or "nenhum"
    mes = MESES[mt - 1] if mt else "sem mês típico"
    return {
        "extremamente_pessimista": f"Com {n} edição(ões) comprovada(s), qualquer previsão de janela pode estar errada; órgão pode extinguir ou suspender o programa.",
        "pessimista": f"Itens ainda não lidos nas edições: {pior}. Sem eles, requisitos e anexos da próxima podem diferir.",
        "levemente_pessimista": "Abertura registrada pode ser a data de publicação, não a de abertura real; a janela pode deslocar semanas.",
        "neutro": (f"Situação: {sit}. Tratar {mes} como mês provável apenas se houver 2 anos; conferir a página do órgão 30 dias antes "
                   "(Lei 13.019, art. 26) e auditar a série por amostra."),
        "levemente_otimista": f"Série em {len(anos)} ano(s) ({', '.join(map(str, anos)) or '—'}) já dá referência de calendário e de valor.",
        "otimista": "Reuso de documentos e do plano de trabalho das edições anteriores encurta a preparação da inscrição.",
        "extremamente_otimista": f"Com mês típico em {mes}, o painel avisa a janela antes do edital sair e a AMC chega com a proposta pronta.",
    }


def relatorio(x: dict) -> dict:
    hoje = hoje_brt()
    reg, _ = regime(x, x.get("programa") or "", privada=(x.get("esfera") == "privada"))
    eds = _edicoes_livro(x)
    for e in eds:
        e["_status"] = {k: _item_status(k, e, x, reg) for k in ITENS}
        e["itens12_resumo"] = dict(Counter(v["estado"] for v in e["_status"].values()))
    sit, motivo = _situacao(x, eds, reg)
    sel = x.get("selo_livro") or {}
    prev = dict(sel.get("preditivo") or {})
    ab = [_d(e["abertura"]) for e in eds if e["abertura"]]
    ant = []
    for e in eds:
        a, f = _d(e["abertura"]), _d(e["encerramento"])
        if a and f:
            ant.append((f - a).days)
    fora = bool(_FORA_ESCOPO.search(str(x.get("programa") or "")))
    out = {
        "adequacao": ("fora do escopo do terceiro setor/AMC (compra, saúde, imóvel ou serviço): candidato a arquivar" if fora else "no escopo (a confirmar pelo titular)"),
        "id": x.get("id"), "livro": x.get("nome_classificado") or x.get("programa"), "orgao": x.get("orgao"), "bloco": sel.get("bloco"),
        "tipo": x.get("tipo_objeto"), "regime": reg, "selo_livro": sel.get("selo"), "selo_oportunidade": (x.get("esteira") or {}).get("selo"),
        "validacao": {"situacao": sit, "motivo": motivo}, "gerado_em": hoje.isoformat(),
        "preditivo": {**prev, "meses_das_edicoes": [e["mes"] for e in eds], "duracao_dias_por_edicao": ant,
                      "intervalo_entre_edicoes_dias": [(b - a).days for a, b in zip(ab, ab[1:])]},
        "edicoes": [{k: v for k, v in e.items() if k != "itens12"} | {"itens": e.pop("_status")} for e in eds],
    }
    if sel.get("bloco") == "GO" and sel.get("selo") != "ouro":
        from .perfil_go import itens_do_livro, site_oficial
        out["site_oficial"] = site_oficial(x)
        out["itens12_livro"] = itens_do_livro(x, out["edicoes"], _derivado, sit, motivo)
    out["conselho_7_lentes"] = _conselho(x, [{**e, "_status": e["itens"], "itens12": {}} for e in out["edicoes"]], out["preditivo"], sit)
    return out


def md(r: dict) -> str:
    L = [f"# {r['livro']}", "", f"Órgão: {r['orgao'] or '—'} · bloco {r['bloco']} · regime {r['regime']} · selo do livro **{r['selo_livro']}** · selo da oportunidade {r['selo_oportunidade']}",
         "", f"Validação: **{r['validacao']['situacao']}** — {r['validacao']['motivo']}", "", "## Estudo preditivo", ""]
    p = r["preditivo"]
    L.append(f"Mês típico: {MESES[p['mes_tipico'] - 1] if p.get('mes_tipico') else 'sem dados'} · duração típica: {p.get('duracao_tipica_dias') or '—'} dias · próxima janela: {p.get('proxima_janela') or '—'} · confiança: {p.get('confianca')}")
    if r.get("site_oficial"):
        so = r["site_oficial"]
        L += ["", "## Site oficial", "", f"{so['url'] or 'não localizado'} — {so['orgao_site'] or ''} ({so['tipo']}; verificado: {so['verificado']})"]
        L += ["", "## Os 12 itens consolidados do histórico", ""] + [f"- {k}: {v['estado']}" + (f" — {v['valor']}" if v.get("valor") else "") + f" ({v['origem']})" for k, v in r["itens12_livro"].items()]
    L += ["", "## Edições anteriores e os 12 itens", ""]
    if not r["edicoes"]:
        L.append("Nenhuma edição anterior comprovada (ver validação).")
    for e in r["edicoes"]:
        L += [f"### {e['mes']} — {e['titulo']}", f"Página oficial: {e['pagina_oficial']}", ""]
        for k, v in e["itens"].items():
            L.append(f"- {k}: {v['estado']}" + (f" — {v['valor']}" if v.get("valor") else "") + (f" ({v['porque']})" if v.get("porque") else ""))
        L.append("")
    L += ["## Conselho de 7 lentes", ""] + [f"- {k.replace('_', ' ')}: {v}" for k, v in r["conselho_7_lentes"].items()]
    return "\n".join(L) + "\n"


def gerar() -> dict:
    C = json.loads(CAT.read_text(encoding="utf-8"))
    SAIDA.mkdir(parents=True, exist_ok=True)
    cont, itens = Counter(), Counter()
    resumo = []
    for x in C.get("motores") or []:
        r = relatorio(x)
        (SAIDA / f"{r['id']}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        (SAIDA / f"{r['id']}.md").write_text(md(r), encoding="utf-8")
        cont[r["validacao"]["situacao"].split(":")[0] + (":" + r["validacao"]["situacao"].split(":")[1] if ":" in r["validacao"]["situacao"] else "")] += 1
        for e in r["edicoes"]:
            itens.update(v["estado"] for v in e["itens"].values())
        resumo.append({"id": r["id"], "livro": r["livro"], "bloco": r["bloco"], "selo": r["selo_livro"], "situacao": r["validacao"]["situacao"],
                       "edicoes": len(r["edicoes"]), "mes_tipico": r["preditivo"].get("mes_tipico"), "proxima_janela": r["preditivo"].get("proxima_janela")})
    RESUMO.write_text(json.dumps({"gerado_em": hoje_brt().isoformat(), "por_situacao": dict(cont), "itens_das_edicoes": dict(itens), "livros": resumo},
                                 ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {"por_situacao": dict(cont), "itens_das_edicoes": dict(itens), "livros": len(resumo)}


if __name__ == "__main__":
    print(json.dumps(gerar(), ensure_ascii=False, indent=1))
