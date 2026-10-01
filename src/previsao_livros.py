"""PREVISÃO DOS LIVROS E ATIVAÇÃO 30 DIAS ANTES (titular, 02/10/2026).

Cada livro da Biblioteca guarda as janelas de inscrição que já conheceu — edições do histórico, janelas registradas,
pesquisa dos 12 parâmetros e as datas do histórico dos parâmetros. Com elas, prevê a PRÓXIMA ABERTURA e o livro é
ATIVADO 30 DIAS ANTES (ligado por 30 dias: lido todo dia, com a IA buscando o que falta) — para o edital ser visto
quando abrir, não depois.

Confiança: ALTA (janelas em 3 anos ou mais) · MÉDIA (2 anos) · BAIXA (1 janela). A ativação automática exige a
confiança mínima de config/parametros_biblioteca.json › previsao (padrão: média; com uma janela só, apenas programa de
regime anual). Captação contínua não precisa de previsão. Saída: docs/dados/previsao_livros.json
"""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "biblioteca_alexandria/fontes/motores.json"
LIG = ROOT / "estado/opressores.json"
PAR = ROOT / "config/parametros_biblioteca.json"
SAIDA = ROOT / "docs/dados/previsao_livros.json"
PADRAO = {"ativar_dias_antes": 30, "duracao_padrao_dias": 30, "confianca_minima": "media", "anual_com_uma_janela": True, "horizonte_painel_dias": 120}
ORDEM = {"baixa": 1, "media": 2, "alta": 3}
DATA = re.compile(r"\b(\d{1,2})/(\d{1,2})/(20\d\d)\b|\b(20\d\d)-(\d{2})-(\d{2})\b")


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return padrao


def _d(s) -> date | None:
    try:
        return date.fromisoformat(str(s)[:10])
    except Exception:
        return None


def _datas(txt) -> list[date]:
    out = []
    for m in DATA.finditer(str(txt or "")):
        try:
            out.append(date(int(m.group(3)), int(m.group(2)), int(m.group(1))) if m.group(1) else date(int(m.group(4)), int(m.group(5)), int(m.group(6))))
        except ValueError:
            pass
    return out


def janelas(x: dict) -> list[tuple[date | None, date | None]]:
    """Todas as janelas de inscrição que o livro conhece: (abertura, encerramento)."""
    js = []
    for h in x.get("historico") or []:
        js.append((_d(h.get("inicio")), _d(h.get("fim"))))
        ds = _datas((h.get("parametros") or {}).get("Prazo de inscrição"))
        if len(ds) >= 2:
            js.append((min(ds), max(ds)))
    for j in ((x.get("livro") or {}).get("inscricao") or {}).get("janelas") or x.get("janelas") or []:
        if isinstance(j, dict):
            js.append((_d(j.get("inicio")), _d(j.get("fim"))))
    p = x.get("parametros") or {}
    if p.get("inicio") or p.get("fim"):
        js.append((_d(p.get("inicio")), _d(p.get("fim"))))
    for mud in ((x.get("livro") or {}).get("historico_parametros") or []):
        for v in (mud.get("mudou") or {}).get("Prazo de inscrição", {}).values():
            ds = _datas(v)
            if len(ds) >= 2:
                js.append((min(ds), max(ds)))
    ck = ((x.get("livro") or {}).get("checklist") or {}).get("Prazo de inscrição", {}).get("v")
    ds = _datas(ck)
    if len(ds) >= 2:
        js.append((min(ds), max(ds)))
    # uma janela por ano (a mais completa); janela de 1 ano inteiro é captação contínua, não época
    por_ano = {}
    for a, f in js:
        if not (a or f) or (a and f and (f - a).days > 300):
            continue
        ano = (a or f).year
        atual = por_ano.get(ano)
        if not atual or (a and f and not (atual[0] and atual[1])):
            por_ano[ano] = (a, f)
    return [por_ano[k] for k in sorted(por_ano)]


def prever(x: dict, hoje: date, cfg: dict) -> dict | None:
    if x.get("regime_inscricao") == "contínuo" or str(x.get("regime_prazo") or "").startswith("permanente"):
        return None
    js = janelas(x)
    if not js:
        return None
    duracoes = [(f - a).days for a, f in js if a and f and 0 < (f - a).days <= 300]
    dur = sorted(duracoes)[len(duracoes) // 2] if duracoes else cfg["duracao_padrao_dias"]
    ult_a, ult_f = js[-1]
    abre_ref = ult_a or (ult_f - timedelta(days=dur))
    if ult_f and abre_ref <= hoje <= ult_f:
        return {"situacao": "aberta agora", "abertura": abre_ref.isoformat(), "encerramento": ult_f.isoformat(), "confianca": "comprovada",
                "base": "janela atual registrada"}
    # mês e dia típicos de abertura (o mais frequente entre as janelas)
    md = Counter(((a or (f - timedelta(days=dur))).month, (a or (f - timedelta(days=dur))).day) for a, f in js).most_common(1)[0][0]
    ano = hoje.year
    try:
        prox = date(ano, md[0], min(md[1], 28))
    except ValueError:
        prox = date(ano, md[0], 1)
    if prox + timedelta(days=dur) < hoje:
        prox = prox.replace(year=ano + 1)
    anos = len({(a or f).year for a, f in js})
    conf = "alta" if anos >= 3 else "media" if anos == 2 else "baixa"
    return {"situacao": "prevista", "abertura": prox.isoformat(), "encerramento": (prox + timedelta(days=dur)).isoformat(),
            "ativar_em": (prox - timedelta(days=cfg["ativar_dias_antes"])).isoformat(), "confianca": conf,
            "base": f"{len(js)} janela(s) em {anos} ano(s); duração típica {dur} dias",
            "proxima_janela": prox.isoformat()[:7]}


def run(hoje: date | None = None) -> dict:
    hoje = hoje or datetime.now(timezone(timedelta(hours=-3))).date()
    cfg = {**PADRAO, **((_j(PAR, {}) or {}).get("previsao") or {})}
    C = _j(CAT, {}); L = _j(LIG, {"ligados": {}}); L.setdefault("ligados", {})
    try:
        from .parametros_opressores import dispensados
        disp = dispensados()
    except Exception:
        disp = set()
    try:
        man = set((_j(ROOT / "config/motores_ativos.json", {}) or {}).get("inativos") or [])
    except Exception:
        man = set()
    prev, ativados, futuro = 0, [], []
    for x in C.get("motores") or []:
        if x.get("papel") == "fonte_de_busca":
            continue
        pv = prever(x, hoje, cfg)
        if not pv:
            continue
        prev += 1
        x["previsao"] = {**(x.get("previsao") or {}), **pv}
        if pv["situacao"] != "prevista":
            continue
        ok_conf = ORDEM[pv["confianca"]] >= ORDEM.get(cfg["confianca_minima"], 2) or \
            (pv["confianca"] == "baixa" and cfg.get("anual_com_uma_janela") and x.get("regime_inscricao") == "anual")
        ativ, abre, fecha = _d(pv["ativar_em"]), _d(pv["abertura"]), _d(pv["encerramento"])
        linha = {"id": x["id"], "nome": x.get("nome_classificado") or x.get("programa"), "geo": x.get("geo"), "abertura_prevista": pv["abertura"],
                 "ativar_em": pv["ativar_em"], "confianca": pv["confianca"], "base": pv["base"], "ativa_automaticamente": ok_conf}
        if ativ <= hoje <= fecha:
            if ok_conf and x["id"] not in L["ligados"] and x["id"] not in disp and x["id"] not in man:
                L["ligados"][x["id"]] = {"desde": hoje.isoformat(), "ate": (hoje + timedelta(days=30)).isoformat(),
                                         "origem": f"automática: abertura prevista em {abre.strftime('%d/%m/%Y')} (confiança {pv['confianca']}) — ativado 30 dias antes",
                                         "dias": 0, "ia": [], "itens": {}}
                ativados.append(linha)
        if hoje <= ativ <= hoje + timedelta(days=cfg["horizonte_painel_dias"]) or ativ <= hoje <= fecha:
            futuro.append(linha)
    CAT.write_text(json.dumps(C, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    LIG.write_text(json.dumps(L, ensure_ascii=False, indent=1), encoding="utf-8")
    futuro.sort(key=lambda z: z["ativar_em"])
    rel = {"em": hoje.isoformat(), "regra": __doc__.split("Confiança")[0].strip(), "parametros": cfg, "livros_com_previsao": prev,
           "ativados_hoje": ativados, "proximas_ativacoes": futuro}
    SAIDA.write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"livros_com_previsao": prev, "ativados_hoje": len(ativados), "proximas_ativacoes": len(futuro)}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=1))
