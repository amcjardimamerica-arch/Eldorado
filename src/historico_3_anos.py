"""HISTÓRICO DE 3 ANOS DOS MOTORES 03, 11 E 18 (titular, 03/10/2026).

Pedido do titular: buscar as oportunidades que foram ABERTAS nos últimos 3 anos e gerar o LIVRO de cada uma para
validação no sistema; as encerradas ficam como ARQUIVO para a análise preditiva (mês típico, órgão, valor, recorrência).

  Motor 03 — Diário Oficial da União: dia a dia (dias úteis), Seção 3 e Seção 1 da Leitura do Jornal; a lista do dia
             passa pelo mesmo filtro e pelo mesmo classificador do motor; a íntegra só é aberta para o que o resumo
             já indica como seleção aberta (no máximo 12 por dia).
  Motor 11 — CNJ: as páginas da busca do Portal do CNJ (os mesmos termos do motor), notícia por notícia, com a data.
  Motor 18 — GIFE: mês a mês, os posts da categoria Editais (a seleção mensal do GIFE) pela API do WordPress.

A carga é FRACIONADA: cada execução processa o que cabe no orçamento de tempo e grava o cursor; a seguinte continua de
onde parou, do mais recente para o mais antigo. Nada é inventado: o que o texto não diz fica null.

Saídas
  biblioteca_alexandria/base/historico_3_anos/<motor>/<ano>.jsonl   arquivo (encerradas e abertas, uma linha por oportunidade)
  livros (Biblioteca de Alexandria)                                 livro novo ou edição nova (src.livros_regra.registrar_achados)
  estado/historico_3_anos/<motor>.json                              cursor e contagens
  docs/dados/historico_3_anos.json                                  resumo para o painel

    python -m src.historico_3_anos dou --minutos 25
    python -m src.historico_3_anos judiciario-cnj plat-gife
    python -m src.historico_3_anos --status
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import date, timedelta
from pathlib import Path

from .nucleo import ROOT, now_iso, write_json

ARQ = ROOT / "biblioteca_alexandria/base/historico_3_anos"
EST = ROOT / "estado/historico_3_anos"
RESUMO = ROOT / "docs/dados/historico_3_anos.json"
ANOS = 3
NOMES = {"dou": "Motor 03 — Diário Oficial da União", "judiciario-cnj": "Motor 11 — CNJ (prestações pecuniárias)",
         "plat-gife": "Motor 18 — GIFE (seleção mensal de editais)"}
CAMPOS = ("id", "titulo", "orgao", "url", "url_fonte", "data_publicacao", "fim", "regime", "objeto", "valor_texto", "uf",
          "territorio", "comarca", "financiador", "abrangencia", "publico", "secao_dou", "tipo_dou", "numero_edital")


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao


def inicio(hoje: date | None = None) -> date:
    h = hoje or date.today()
    return date(h.year - ANOS, h.month, min(h.day, 28))


# ─────────────────────────── arquivo e livros ───────────────────────────
def situacao(r: dict, hoje: date) -> str:
    fim = str(r.get("fim") or "")[:10]
    if fim:
        return "encerrada" if fim < hoje.isoformat() else "aberta"
    pub = str(r.get("data_publicacao") or "")[:10]
    return "encerrada" if pub and pub < (hoje - timedelta(days=90)).isoformat() else "sem_prazo"


def arquivar(motor: str, regs: list[dict], hoje: date) -> int:
    """Grava no arquivo do ano, sem repetir o id. Devolve quantos entraram."""
    novos = 0
    por_ano: dict[str, list[dict]] = {}
    for r in regs:
        ano = str(r.get("data_publicacao") or "")[:4] or "sem-ano"
        por_ano.setdefault(ano, []).append(r)
    for ano, lista in por_ano.items():
        p = ARQ / motor.replace("plat-", "") / f"{ano}.jsonl"
        p.parent.mkdir(parents=True, exist_ok=True)
        ja = set()
        if p.exists():
            for linha in p.read_text(encoding="utf-8").splitlines():
                try:
                    ja.add(json.loads(linha)["id"])
                except Exception:  # noqa: BLE001
                    pass
        with p.open("a", encoding="utf-8") as fh:
            for r in lista:
                if r["id"] in ja:
                    continue
                ja.add(r["id"])
                fh.write(json.dumps({**{k: r.get(k) for k in CAMPOS}, "motor": motor, "situacao": situacao(r, hoje),
                                     "arquivado_em": hoje.isoformat()}, ensure_ascii=False) + "\n")
                novos += 1
    return novos


def livros(motor: str, regs: list[dict]) -> dict:
    """Cada oportunidade vira livro (ou edição de um livro existente) — validação no sistema e previsão."""
    if not regs:
        return {}
    try:
        from .livros_regra import registrar_achados
        achados = [{**r, "fonte_id": motor, "pagina_oficial": r.get("url"),
                    "origem": f"{NOMES.get(motor, motor)} — histórico de 3 anos"} for r in regs]
        res = registrar_achados(achados, f"{NOMES.get(motor, motor)} — histórico de 3 anos")
        return {k: v for k, v in (res or {}).items() if isinstance(v, (int, str))}
    except Exception as e:  # noqa: BLE001
        return {"erro": f"{type(e).__name__}: {str(e)[:120]}"}


# ─────────────────────────── motor 03 — DOU ───────────────────────────
def _dias_uteis(de: date, ate: date) -> list[date]:
    from .diario_uniao import _dia_util
    out, d = [], ate
    while d >= de:
        if _dia_util(d):
            out.append(d)
        d -= timedelta(days=1)
    return out


def periodo_dou(d: date, ctx: dict) -> list[dict]:
    from . import diario_uniao as U
    cfg = U._cfg()
    a = cfg.get("fonte_a", {})
    mb = int(a.get("max_bytes", 12_000_000))
    materias = []
    for sec in ("do3", "do1"):
        itens, _fl = U.materias_do_jornal(U._get_tentando(U.url_jornal(d, sec), max_bytes=mb))
        ctx["materias"] = ctx.get("materias", 0) + len(itens)
        materias += [U._materia(it, None, "H") for it in itens if U.interessa(it)[0]]
    oport, _acomp, _cont = U.classificar_lote(materias, d)
    # íntegra só do que o resumo já indica como seleção aberta: prazo, órgão e objeto completos
    abrir = [m for m in materias if m.get("url_title") and any(o.get("url") == m.get("url") for o in oport.values())][:12]
    for m in abrir:
        try:
            m["texto"] = U.texto_da_materia(U._get_tentando(U.url_materia(m["url_title"]), tentativas=2, max_bytes=3_000_000))
            m["integra"] = True
            time.sleep(0.3)
        except Exception:  # noqa: BLE001
            pass
    if abrir:
        oport, _acomp, _cont = U.classificar_lote(materias, d)
    return [{**r, "data_publicacao": r.get("data_publicacao") or d.isoformat()} for r in oport.values()]


# ─────────────────────────── motor 11 — CNJ ───────────────────────────
def periodo_cnj(pagina: int, ctx: dict) -> list[dict]:
    from urllib.parse import quote_plus
    from . import judiciario_go as J
    cfg = J._cfg()
    f = (cfg.get("fontes") or {}).get("C_cnj_busca") or {}
    termos = f.get("termos") or ["prestação pecuniária edital"]
    F = {"falhas": [], "consultas": 0, "itens": 0}
    vistos = ctx.setdefault("vistos", [])
    itens = []
    for termo in termos:
        # 03/10: por DATA (a ordem por relevância misturava anos e o corte dos "mais antigos que 3 anos" não funcionava)
        url = (f.get("busca_pagina") or "https://www.cnj.jus.br/page/{pagina}/?s={termo}&orderby=date&order=DESC").format(
            termo=quote_plus(termo), pagina=pagina) if pagina > 1 else f["busca"].format(termo=quote_plus(termo), pagina=1)
        try:
            res = J.resultados_cnj(J._get(url, cfg, F))
        except Exception:  # noqa: BLE001
            continue
        for x in res:
            if x["url"] in vistos or not J.candidata(x["titulo"]):
                continue
            vistos.append(x["url"])
            try:
                art = J.artigo(J._get(x["url"], cfg, F), x["url"], x["titulo"], ("www.cnj.jus.br", "cnj.jus.br"))
            except Exception:  # noqa: BLE001
                continue
            itens.append({**x, "fonte": "C", "texto": art["texto"], "publicado": art["publicado"], "pdfs": art["pdfs"]})
    ctx["vistos"] = vistos[-3000:]
    lim = inicio().isoformat()
    regs = []
    for it in itens:
        pub = str(it.get("publicado") or "")[:10]
        if pub and pub < lim:
            ctx["antigos"] = ctx.get("antigos", 0) + 1
            continue
        try:
            dia = date.fromisoformat(pub) if pub else date.today()
        except ValueError:
            dia = date.today()
        oport, acomp, _c = J.classificar_lote([it], dia, cfg)
        for r in list(oport.values()) + [a for a in acomp.values() if re.search(r"EDITA|SELECAO|SELECIONA|PROJETOS", J._N(a.get("titulo")))]:
            regs.append({**r, "data_publicacao": r.get("data_publicacao") or pub or None})
    return regs


# ─────────────────────────── motor 18 — GIFE ───────────────────────────
def _meses(de: date, ate: date) -> list[str]:
    out, a, m = [], ate.year, ate.month
    while (a, m) >= (de.year, de.month):
        out.append(f"{a:04d}-{m:02d}")
        m -= 1
        if m == 0:
            a, m = a - 1, 12
    return out


def periodo_gife(mes: str, ctx: dict) -> list[dict]:
    from . import gife_editais as G
    cfg = G._cfg()
    g = cfg.get("gife") or {}
    base, cat = g.get("base", "https://gife.org.br"), int(g.get("categoria_id", 25))
    a, m = (int(x) for x in mes.split("-"))
    fim = date(a + (m == 12), 1 if m == 12 else m + 1, 1)
    consulta = f"categories={cat}&after={a:04d}-{m:02d}-01T00:00:00&before={fim.isoformat()}T00:00:00&orderby=date&order=asc"
    F = {"falhas": [], "consultas": 0, "posts": 0, "itens": 0}
    posts = G._posts(base, consulta, cfg, F, max_paginas=6)
    ctx["posts"] = ctx.get("posts", 0) + len(posts)
    itens = [i for p in posts for i in G.itens_gife(p, cfg)]
    ufs = (cfg.get("territorio") or {}).get("ufs") or ["GO"]
    regs = []
    for p in posts:
        dia = date.fromisoformat(str(p.get("date"))[:10])
        doposts = [i for i in itens if i.get("post_id") == p.get("id")]
        oport, _acomp, _c = G.classificar_lote(doposts, dia, ufs, cfg, {})
        regs += [{**r, "data_publicacao": r.get("data_publicacao") or dia.isoformat()} for r in oport.values()]
    return regs


# ─────────────────────────── condução ───────────────────────────
MOTORES = {
    "dou": {"periodos": lambda hoje: [d.isoformat() for d in _dias_uteis(inicio(hoje), hoje - timedelta(days=1))],
            "ler": lambda p, ctx: periodo_dou(date.fromisoformat(p), ctx)},
    "judiciario-cnj": {"periodos": lambda hoje: [str(n) for n in range(1, 41)], "ler": lambda p, ctx: periodo_cnj(int(p), ctx)},
    "plat-gife": {"periodos": lambda hoje: _meses(inicio(hoje), hoje), "ler": periodo_gife},
}


def rodar(motor: str, minutos: float = 20, hoje: date | None = None) -> dict:
    hoje = hoje or date.today()
    m = MOTORES[motor]
    p_est = EST / f"{motor.replace('plat-', '')}.json"
    est = _j(p_est, {}) or {}
    feitos = set(est.get("feitos") or [])
    pendentes = [p for p in m["periodos"](hoje) if p not in feitos]
    ctx = est.setdefault("ctx", {})
    fim = time.monotonic() + minutos * 60
    regs_rodada, falhas, lidos = [], [], 0
    for p in pendentes:
        if time.monotonic() > fim:
            break
        try:
            regs = m["ler"](p, ctx)
            regs_rodada += regs
            feitos.add(p); lidos += 1
            # CNJ: a busca não tem data; quando as páginas só trazem notícia mais velha que 3 anos, a carga termina
            if motor == "judiciario-cnj" and not regs and ctx.get("antigos", 0) >= 20:
                feitos.update(m["periodos"](hoje))
                break
        except Exception as e:  # noqa: BLE001 — período que falhou fica para a próxima execução
            falhas.append(f"{p}: {type(e).__name__}: {str(e)[:100]}")
            if len(falhas) >= 8:
                break
    novos = arquivar(motor, regs_rodada, hoje)
    liv = livros(motor, regs_rodada)
    total = len(m["periodos"](hoje))
    cont = est.setdefault("por_ano", {})
    for r in regs_rodada:
        a = str(r.get("data_publicacao") or "")[:4] or "sem-ano"
        cont[a] = int(cont.get(a) or 0) + 1
    est.update({"motor": motor, "nome": NOMES.get(motor), "desde": inicio(hoje).isoformat(), "feitos": sorted(feitos),
                "periodos_total": total, "periodos_feitos": len(feitos & set(m["periodos"](hoje))),
                "concluido": len(feitos & set(m["periodos"](hoje))) >= total or (motor == "judiciario-cnj" and lidos == 0 and not pendentes),
                "ultima": {"em": now_iso(), "periodos_lidos": lidos, "oportunidades": len(regs_rodada), "arquivadas_novas": novos,
                           "livros": liv, "falhas": falhas[:8]}})
    EST.mkdir(parents=True, exist_ok=True)
    write_json(p_est, est)
    resumo()
    return est["ultima"] | {"concluido": est["concluido"], "periodos_feitos": est["periodos_feitos"], "periodos_total": total}


def resumo() -> dict:
    out = {"em": now_iso(), "regra": __doc__.split("Saídas")[0].strip(), "motores": {}}
    for motor in MOTORES:
        e = _j(EST / f"{motor.replace('plat-', '')}.json", {}) or {}
        pasta = ARQ / motor.replace("plat-", "")
        sit, n = {}, 0
        for p in sorted(pasta.glob("*.jsonl")) if pasta.exists() else []:
            for linha in p.read_text(encoding="utf-8").splitlines():
                try:
                    s = json.loads(linha).get("situacao")
                except ValueError:
                    continue
                n += 1
                sit[s] = sit.get(s, 0) + 1
        out["motores"][motor] = {"nome": NOMES.get(motor), "desde": e.get("desde"), "concluido": bool(e.get("concluido")),
                                 "periodos": f"{e.get('periodos_feitos', 0)}/{e.get('periodos_total', 0)}",
                                 "arquivadas": n, "por_situacao": sit, "por_ano": e.get("por_ano") or {},
                                 "ultima": (e.get("ultima") or {}).get("em")}
    RESUMO.parent.mkdir(parents=True, exist_ok=True)
    write_json(RESUMO, out)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m src.historico_3_anos")
    ap.add_argument("motores", nargs="*", default=list(MOTORES))
    ap.add_argument("--minutos", type=float, default=20)
    ap.add_argument("--status", action="store_true")
    a = ap.parse_args(argv)
    if a.status:
        print(json.dumps(resumo(), ensure_ascii=False, indent=1))
        return 0
    for motor in a.motores:
        if motor in MOTORES:
            print(motor, json.dumps(rodar(motor, a.minutos), ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
