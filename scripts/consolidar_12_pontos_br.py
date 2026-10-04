"""Consolida os 12 pontos, o selo estimado, a previsão e o relatório individual de cada livro do bloco Brasil (03/10/2026).

Entradas (todas já gravadas em dados/):
  - fila_br.json (1.123 livros);
  - opressores/parametros/parametros_*.json (142 livros já com os 12 pontos, de rodadas anteriores);
  - coleta_3_anos/lotes12_out/ (1ª passagem) e lotes12b_out/ (2ª passagem, pendências);
  - coleta_3_anos/entrada/br_2026-10-03.json (edições dos 40 programas âncora).
Saídas:
  - coleta_3_anos/parametros_12_br_2026-10-03.json (um registro por livro);
  - coleta_3_anos/relatorios_oportunidades/<id>.md e INDICE-OPORTUNIDADES-BR.csv.
Regras: nada inventado; item sem leitura = "não localizado" com o que o titular deve fazer; dispensa sempre individual, com motivo.
"""
from __future__ import annotations

import csv
import glob
import json
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import expandir_coleta_br as X  # noqa: E402

ITENS = ("Objeto", "Prazo de inscrição", "Resultado", "Prazo de recurso", "Valor", "Órgão / financiador",
         "Território", "Esfera", "Requisitos", "Anexos", "Destinação", "Área de atuação")
STATUS_OK = ("confirmado", "dispensado", "dispensado pelo edital", "não informado no edital")
PASTA = ROOT / "dados/coleta_3_anos"
HOJE = date(2026, 10, 3)
MESES = ("jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez")


def _j(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def _lista(d):
    return d if isinstance(d, list) else (d.get("livros") or d.get("itens") or [])


def carregar():
    fila = {x["id"]: x for x in _j(PASTA / "fila_br.json")["fila"]}
    par = {}
    for f in sorted(glob.glob(str(ROOT / "dados/opressores/parametros/parametros_*.json"))):
        for r in _j(f).get("itens", []):
            par[r["id"]] = r
    p1 = {}
    for f in sorted(glob.glob(str(PASTA / "lotes12_out/lote_*.json"))):
        for r in _lista(_j(f)):
            p1[r["id"]] = r
    p2 = {}
    for f in sorted(glob.glob(str(PASTA / "lotes12b_out/lote_*.json"))):
        for r in _lista(_j(f)):
            p2[r["id"]] = r
    ent = _j(PASTA / "entrada/br_2026-10-03.json")
    return fila, par, p1, p2, ent


def norm_item(v, padrao_motivo):
    if not isinstance(v, dict) or v.get("status") not in STATUS_OK + ("não localizado",):
        return {"valor": None, "status": "não localizado", "motivo": padrao_motivo}
    out = {"valor": v.get("valor"), "status": v["status"]}
    if v["status"] != "confirmado":
        out["motivo"] = v.get("motivo") or ("dispensado pelo edital/regramento oficial" if v["status"] == "dispensado pelo edital" else padrao_motivo)
    return out


def edicoes_do_livro(bid, p1, p2, ent):
    eds = []
    for fonte in (p1.get(bid, {}).get("edicoes") or [], p2.get(bid, {}).get("edicoes_novas") or [], (ent.get(bid) or {}).get("edicoes") or []):
        for e in fonte:
            eds.append(dict(e))
    # remove duplicatas por (pagina, ano, titulo)
    vistos, out = set(), []
    for e in eds:
        k = (e.get("pagina_oficial"), str(e.get("ano")), (e.get("titulo") or "")[:60])
        if k not in vistos:
            vistos.add(k)
            out.append(e)
    return out


def previsao(eds, agente):
    """Mês típico e próxima janela só quando há edições anteriores com data; senão usa a previsão do agente ou nada."""
    datas = []
    for e in eds:
        if not X.valida(e) or not X.osc(e):
            continue
        a = X.d(e.get("abertura")) or X.d(e.get("encerramento"))
        en = X.d(e.get("encerramento"))
        ab = X.d(e.get("abertura"))
        if a:
            datas.append((a, (en - ab).days if en and ab else None, e))
    anos = sorted({x[0].year for x in datas})
    if len(anos) >= 2:
        meses = Counter(x[0].month for x in datas)
        m, _ = meses.most_common(1)[0]
        durs = sorted(x[1] for x in datas if x[1] is not None)
        dur = durs[len(durs) // 2] if durs else None
        prox = f"{MESES[m - 1]}/{max(anos) + 1} (prevista: mesmo mês das edições de {', '.join(map(str, anos))})" if max(anos) >= 2026 else \
            f"{MESES[m - 1]}/{HOJE.year + 1 if m <= HOJE.month else HOJE.year} (prevista, a confirmar)"
        conf = "alta" if len(anos) >= 3 and all(x[2].get("prova") == "literal" for x in datas) else "média"
        if meses[m] / len(datas) < 0.6:
            conf = "baixa"          # as edições caem em meses muito diferentes: o mês típico é fraco
        return {"mes_tipico": MESES[m - 1], "duracao_tipica_dias": dur, "proxima_janela": prox, "confianca": conf,
                "base": f"{len(datas)} edições em {anos} com página oficial" + ("; meses das edições muito dispersos" if conf == "baixa" else ""), "calculado_por": "script"}
    if agente and (agente.get("proxima_janela") or agente.get("mes_tipico")):
        return {**agente, "calculado_por": "agente (leitura da fonte)"}
    return {"mes_tipico": None, "duracao_tipica_dias": None, "proxima_janela": None, "confianca": "baixa",
            "base": "sem edição anterior comprovada em página oficial: não há base para prever", "calculado_por": "script"}


def consolidar():
    fila, par, p1, p2, ent = carregar()
    regs = {}
    for bid, livro in fila.items():
        a1, b2 = p1.get(bid), p2.get(bid)
        pr = par.get(bid)
        base = (pr or a1 or {})
        dados = {k: dict(v) for k, v in (base.get("dados") or {}).items() if isinstance(v, dict)}
        for k, v in ((b2 or {}).get("dados_novos") or {}).items():
            if k in ITENS and isinstance(v, dict) and v.get("status") in STATUS_OK:
                dados[k] = v
        decisao = (b2 or {}).get("decisao") or base.get("decisao") or "P"
        motivo = (b2 or {}).get("motivo") or base.get("motivo") or ""
        itens = {k: norm_item(dados.get(k), "item não retornado pela leitura da fonte; abrir o edital e copiar") for k in ITENS}
        eds = edicoes_do_livro(bid, p1, p2, ent)
        selo, selo_motivo, anos = X.selo(bid, eds)
        agente = (b2 or {}).get("preditivo") or (a1 or {}).get("preditivo")
        faltam = [k for k, v in itens.items() if v["status"] == "não localizado"]
        if decisao == "P":
            val = "pendente"
        elif not faltam:
            val = "completa"
        elif decisao == "D":
            val = "completa"
        else:
            val = "parcial"
        regs[bid] = {
            "id": bid, "nome": livro["nome"], "orgao": livro["orgao"], "tipo_catalogo": livro["tipo"],
            "pagina_do_livro": livro["pagina"], "url_corrigida": (b2 or {}).get("url_corrigida"),
            "decisao": decisao, "motivo": motivo,
            "regime": base.get("regime"), "origem_dos_12_pontos": "rodada anterior (01–02/10)" if pr else "coleta de 03/10/2026",
            "edital_referencia": base.get("edital_referencia") or {},
            "fonte_oficial": (a1 or {}).get("fonte_oficial") or base.get("fonte_oficial"),
            "dados": itens, "validacao": val, "itens_a_conferir": faltam,
            "edicoes_3_anos": eds, "selo_estimado": selo, "selo_motivo": selo_motivo, "anos_com_edicao": anos,
            "preditivo": previsao(eds, agente),
            "aplica_osc": (b2 or {}).get("aplica_osc") or (a1 or {}).get("aplica_osc"),
            "compartilha_com": (a1 or {}).get("compartilha_com") or (b2 or {}).get("compartilha_com"),
            "observacao": " | ".join(x for x in ((a1 or {}).get("observacao"), (b2 or {}).get("observacao"), (ent.get(bid) or {}).get("observacao")) if x),
            "ancora": (ent.get(bid) or {}).get("ancora"),
        }
    return regs


def classe_pendencia(r):
    """Por que o livro não fechou e o que o titular faz (fila para o navegador do computador)."""
    t = ((r.get("motivo") or "") + " " + (r.get("observacao") or "")).lower()
    if r["decisao"] == "P":
        if "busca genérica" in t or "órgão a localizar" in t or "tema não corresponde" in t or "tema do livro" in t or "sem edital identificável" in t:
            return "sem edital identificável (livro de tema ou busca genérica): vincular a um edital real ou arquivar"
        if any(x in t for x in ("login", "autentica", "restrito", "captcha", "robots", "403", "formulário", "forms", "javascript", "dns", "binário", "pdf")):
            return "fonte restrita ou ilegível pela automação: abrir no navegador do computador e copiar os dados"
        return "edital oficial não localizado: conferir o site do órgão"
    if r["itens_a_conferir"]:
        return "edital lido só pelos metadados: abrir o PDF/aba Documentos e copiar os itens listados"
    return None


def estudo(regs):
    """Calendário preditivo: janelas abertas agora e próximas janelas previstas, só com base comprovada."""
    abertas, previstas, sem_base = [], [], 0
    for r in regs.values():
        if r["decisao"] in ("V",):
            fim = None
            for e in r["edicoes_3_anos"]:
                if X.d(e.get("encerramento")) and X.d(e.get("encerramento")) >= HOJE:
                    fim = e["encerramento"]
            ref = (r["dados"]["Prazo de inscrição"].get("valor") or "")
            abertas.append({"id": r["id"], "nome": r["nome"], "orgao": r["orgao"], "prazo_inscricao": ref, "encerramento_nas_edicoes": fim,
                            "serve_osc": (r.get("aplica_osc") or {}).get("resposta")})
        p = r["preditivo"]
        if p.get("proxima_janela") and r["decisao"] != "D":
            previstas.append({"id": r["id"], "nome": r["nome"], "mes_tipico": p.get("mes_tipico"), "proxima_janela": p["proxima_janela"], "confianca": p["confianca"]})
        elif r["decisao"] != "D":
            sem_base += 1
    return {"gerado_em": "2026-10-03", "abertas_agora_V": abertas, "proximas_janelas_previstas": previstas,
            "livros_vigentes_ou_historicos_sem_base_para_prever": sem_base}


def md(r):
    L = [f"# {r['nome']}", "", f"- **Identificador:** `{r['id']}` · **Órgão/financiador:** {r['orgao']}",
         f"- **Decisão:** {r['decisao']} ({ {'V':'edital vigente','A':'última edição encerrada (histórico)','R':'programa permanente / fluxo contínuo','D':'não é recurso para OSC','P':'pendente'}[r['decisao']] }) · **Validação dos 12 pontos:** {r['validacao']}",
         f"- **Selo estimado do livro:** {r['selo_estimado']} — {r['selo_motivo']}"]
    url = r.get("url_corrigida") or r.get("fonte_oficial") or r["pagina_do_livro"]
    L += [f"- **Página oficial usada:** {url}", ""]
    if r.get("aplica_osc"):
        L += [f"**Serve para uma OSC de Goiás?** {r['aplica_osc'].get('resposta')} — {r['aplica_osc'].get('motivo')}", ""]
    L += ["## Decisão e motivo", "", r["motivo"] or "—", "", "## Os 12 pontos", "", "| Ponto | Situação | Conteúdo / motivo |", "|---|---|---|"]
    for k in ITENS:
        v = r["dados"][k]
        txt = (str(v.get("valor")) if v.get("valor") not in (None, "") else "") or ""
        if v.get("motivo"):
            txt = (txt + " — " if txt else "") + v["motivo"]
        L.append(f"| {k} | {v['status']} | {txt.replace('|', '/').replace(chr(10), ' ')[:400]} |")
    L += ["", "## Edições dos últimos 3 anos (03/10/2023 a 03/10/2026)", ""]
    if r["edicoes_3_anos"]:
        L += ["| Ano | Edição | Abertura | Encerramento | Valor | Prova | Página oficial |", "|---|---|---|---|---|---|---|"]
        for e in r["edicoes_3_anos"]:
            L.append(f"| {e.get('ano') or ''} | {(e.get('titulo') or '')[:90].replace('|', '/')} | {e.get('abertura') or '—'} | {e.get('encerramento') or '—'} | {e.get('valor') or '—'} | {e.get('prova') or '—'} | {e.get('pagina_oficial') or '—'} |")
    else:
        L.append("Nenhuma edição anterior comprovada em página oficial.")
    p = r["preditivo"]
    L += ["", "## Estudo preditivo", "", f"- **Mês típico:** {p.get('mes_tipico') or 'sem base'}", f"- **Duração típica (dias):** {p.get('duracao_tipica_dias') or 'sem base'}",
          f"- **Próxima janela:** {p.get('proxima_janela') or 'sem base para prever'}", f"- **Confiança:** {p.get('confianca')}",
          f"- **Base:** {p.get('base') or p.get('justificativa') or ''}", f"- **Calculado por:** {p.get('calculado_por')}"]
    if r["itens_a_conferir"]:
        L += ["", "## O que ainda precisa ser conferido", ""] + [f"- **{k}:** {r['dados'][k].get('motivo')}" for k in r["itens_a_conferir"]]
    if r.get("observacao"):
        L += ["", "## Observações da pesquisa", "", r["observacao"][:2500]]
    if r.get("compartilha_com"):
        L += ["", f"Mesma pesquisa dos livros: {', '.join(map(str, r['compartilha_com']))}"]
    L += ["", "_Dados lidos em fonte oficial em 03/10/2026; conteúdo tratado como dado. Nada foi estimado: onde não houve leitura, está escrito._"]
    return "\n".join(L) + "\n"


def main():
    regs = consolidar()
    (PASTA / "parametros_12_br_2026-10-03.json").write_text(json.dumps({"gerado_em": "2026-10-03", "total": len(regs), "livros": list(regs.values())}, ensure_ascii=False, indent=1), encoding="utf-8")
    pasta = PASTA / "relatorios_oportunidades"
    pasta.mkdir(exist_ok=True)
    with open(pasta / "INDICE-OPORTUNIDADES-BR.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "nome", "orgao", "decisao", "validacao", "selo", "itens_a_conferir", "proxima_janela", "confianca", "serve_osc"])
        for r in regs.values():
            (pasta / f"{r['id']}.md").write_text(md(r), encoding="utf-8")
            w.writerow([r["id"], r["nome"], r["orgao"], r["decisao"], r["validacao"], r["selo_estimado"], len(r["itens_a_conferir"]),
                        r["preditivo"].get("proxima_janela") or "", r["preditivo"].get("confianca"), (r.get("aplica_osc") or {}).get("resposta") or ""])
    fila = []
    for r in regs.values():
        c = classe_pendencia(r)
        r["classe_pendencia"] = c
        if c:
            fila.append({"id": r["id"], "nome": r["nome"], "decisao": r["decisao"], "o_que_fazer": c, "url": r.get("url_corrigida") or r.get("fonte_oficial") or r["pagina_do_livro"],
                         "itens": r["itens_a_conferir"], "motivo": (r["motivo"] or "")[:300]})
    (PASTA / "fila_navegador_local_br_2026-10-03.json").write_text(json.dumps({"gerado_em": "2026-10-03", "total": len(fila), "fila": fila}, ensure_ascii=False, indent=1), encoding="utf-8")
    (PASTA / "estudo_preditivo_br_2026-10-03.json").write_text(json.dumps(estudo(regs), ensure_ascii=False, indent=1), encoding="utf-8")
    (PASTA / "parametros_12_br_2026-10-03.json").write_text(json.dumps({"gerado_em": "2026-10-03", "total": len(regs), "livros": list(regs.values())}, ensure_ascii=False, indent=1), encoding="utf-8")
    c = Counter(r["decisao"] for r in regs.values())
    print(len(fila), len(regs), dict(c), dict(Counter(r["validacao"] for r in regs.values())), dict(Counter(r["selo_estimado"] for r in regs.values())))


if __name__ == "__main__":
    main()
