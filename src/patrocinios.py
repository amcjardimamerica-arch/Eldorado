"""2º motor — PATROCÍNIO PRIVADO (marketing, sem benefício fiscal).

Procura em imprensa, rádio, TV e portais de eventos da região quais EMPRESAS
patrocinam, com recursos próprios, eventos culturais, esportivos e educacionais.
Refinamento igual ao motor GIFE (matriz na região, cadastro RFB, capital, score,
elegibilidade), com finalidade específica: patrocínio privado — Lucro Real aqui
é informativo, não requisito (marketing independe de regime).

Regras de honestidade: cada patrocínio registrado traz a URL, o trecho e o
evento; menções com 'Rouanet/incentivo fiscal/edital' são EXCLUÍDAS (não é
patrocínio privado); nada é inventado — sem CNPJ no texto, a empresa fica
'a identificar' até casar com a base ou com o cadastro.

Saída: dados/empresas/<uf>/patrocinios.json (achados) e a agregação na base
(campo `patrocinios`), com score e classe próprios.
"""
from __future__ import annotations

import json
import re
import time
from datetime import date

from .nucleo import ROOT, load_json, now_iso, write_json
from .empresas import (_cfg, _get, _chave, _toks_nome, PASTA, BIB, carregar_base, salvar_base, agregar,
                       cadastro_cnpj, area_potencial, EMPRESA_RX, so_digitos)

def _cfgp() -> dict:
    return _cfg()["patrocinio_privado"]


def classificar_area(texto: str) -> str:
    tl = texto.lower()
    if re.search(r"corrida|maratona|campeonato|copa|torneio|jogos|atleta|esport|futebol|v[ôo]lei|basquete|jud[ôo]|ciclismo", tl): return "esporte"
    if re.search(r"escola|educa|olimp[íi]ada de|feira de ci[êe]ncias|bolsa|universidade|palestra|congresso|semin[áa]rio|curso", tl): return "educacao"
    return "cultura"


def extrair_patrocinios(texto: str, fonte: dict, url: str) -> list[dict]:
    """Trechos onde uma EMPRESA aparece ligada a 'patrocínio/apoio/oferecimento'
    de um EVENTO; exclui benefício fiscal."""
    cfg = _cfgp(); est = cfg["estados"]["GO"]
    ev_rx = re.compile("|".join(map(re.escape, est["eventos_alvo"])), re.I)
    pat_rx = re.compile("|".join(map(re.escape, est["sem_beneficio_fiscal"])), re.I)
    exc_rx = re.compile("|".join(map(re.escape, est["excluir"])), re.I)
    saida, vistos = [], set()
    for m in pat_rx.finditer(texto):
        # a FRASE do patrocínio (entre pontos), não a vizinhança inteira — para que
        # um 'Rouanet' na frase seguinte não apague um patrocínio privado legítimo
        ini = texto.rfind(". ", 0, m.start()); ini = 0 if ini < 0 else ini + 2
        fim = texto.find(". ", m.end()); fim = len(texto) if fim < 0 else fim + 1
        janela = texto[max(ini, m.start() - 320): min(fim, m.end() + 320)]
        if exc_rx.search(janela) or not ev_rx.search(janela):
            continue
        for e in EMPRESA_RX.finditer(janela):
            emp = e.group(1).strip()
            ev = ev_rx.search(janela).group(0)
            k = (emp.upper(), ev.lower(), url)
            if k in vistos or len(emp) < 5:
                continue
            vistos.add(k)
            saida.append({"empresa": emp, "evento": ev, "area": classificar_area(janela), "termo": m.group(0),
                          "trecho": re.sub(r"\s+", " ", janela).strip()[:260], "fonte": fonte["nome"], "tipo_fonte": fonte["tipo"],
                          "url": url, "em": now_iso(), "beneficio_fiscal": False})
    return saida


def coletar(uf: str = "GO", limite_paginas: int = 40) -> dict:
    cfg = _cfgp(); est = cfg["estados"][uf]
    destino = PASTA / uf.lower() / "patrocinios.json"
    atual = load_json(destino) if destino.exists() else {"uf": uf, "achados": [], "leituras": [], "cursor": 0}
    fontes = est["fontes"]; lidas, novos = 0, 0
    inicio = atual.get("cursor", 0)
    for i in range(len(fontes)):
        f = fontes[(inicio + i) % len(fontes)]
        for pg in est["paginas_por_fonte"]:
            if lidas >= limite_paginas:
                break
            url = f["url"].rstrip("/") + pg
            try:
                html = _get(url, timeout=15); lidas += 1
                txt = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S)
                txt = re.sub(r"<[^>]+>", " ", txt); txt = re.sub(r"\s+", " ", txt)
                for a in extrair_patrocinios(txt, f, url):
                    if not any(x["url"] == a["url"] and x["empresa"].upper() == a["empresa"].upper() and x["evento"] == a["evento"] for x in atual["achados"]):
                        atual["achados"].append(a); novos += 1
            except Exception:
                pass
            time.sleep(0.4)
    atual["cursor"] = (inicio + 1) % len(fontes)
    atual["achados"] = atual["achados"][-3000:]
    atual["leituras"] = (atual.get("leituras") or [])[-30:] + [{"em": now_iso(), "paginas_lidas": lidas, "novos": novos}]
    write_json(destino, atual)
    return {"paginas_lidas": lidas, "novos": novos, "total": len(atual["achados"])}


def score_patrocinio(pats: list[dict], cad: dict | None) -> dict:
    p = _cfgp()["score_patrocinio"]; pts, mem = 0, []
    if pats:
        n = len(pats); v = min(p["eventos_patrocinados_5_anos"], 10 + 5 * n); pts += v; mem.append(f"{n} evento(s) patrocinado(s) +{v}")
        anos = {a["em"][:4] for a in pats}
        if len(anos) >= 2: pts += p["recorrencia_anual"]; mem.append(f"recorrência em {len(anos)} anos +{p['recorrencia_anual']}")
        areas = {a["area"] for a in pats}
        if len(areas) >= 2: pts += p["diversidade_de_areas"]; mem.append(f"{len(areas)} áreas +{p['diversidade_de_areas']}")
        if any(re.search(r"cotas|naming|patrocinador oficial|parceiro oficial", a["trecho"], re.I) for a in pats): pts += p["cotas_ou_naming"]; mem.append("cotas/naming +10")
    if cad:
        if cad.get("matriz") and (cad.get("uf") == "GO"): pts += p["matriz_na_regiao"]; mem.append("matriz na região +15")
        cap = cad.get("capital_social") or 0
        if cap > 10_000_000: v = 5 if cap <= 50_000_000 else p["capital_social"]; pts += v; mem.append(f"capital +{v}")
    pts = min(100, pts)
    classe = next(v for k, v in sorted(p["classes"].items(), key=lambda kv: -int(kv[0])) if pts >= int(k))
    return {"score": pts, "classe": classe, "memoria": mem}


def run(uf: str = "GO") -> dict:
    """Coleta nas fontes de comunicação, cruza com a base do motor GIFE (agrega o
    campo `patrocinios`), cria registros para empresas novas identificadas e
    grava a saída para o painel."""
    col = coletar(uf)
    achados = load_json(PASTA / uf.lower() / "patrocinios.json").get("achados", [])
    base = carregar_base()
    por_emp: dict[str, list] = {}
    for a in achados:
        por_emp.setdefault(a["empresa"].upper(), []).append(a)
    agregadas = novas = 0
    for nome, pats in por_emp.items():
        alvo = None
        for k, e in base.items():
            if len(_toks_nome(nome) & _toks_nome(e["nome"])) >= 2:
                alvo = k; break
        if alvo is None:
            alvo = _chave(None, nome)
            agregar(base, alvo, pats[0]["empresa"], None, None, origem="patrocínio privado (imprensa/eventos)")
            novas += 1
        e = base[alvo]
        e["patrocinios"] = pats[-40:]
        sp = score_patrocinio(pats, e.get("cadastro"))
        e["patrocinio_score"] = sp["score"]; e["patrocinio_classe"] = sp["classe"]; e["patrocinio_memoria"] = sp["memoria"]
        e["patrocinio_areas"] = sorted({a["area"] for a in pats})
        agregadas += 1
    salvar_base(base)
    saida = [{"id": k, "nome": e["nome"], "cnpj": e.get("cnpj"), "municipio": (e.get("cadastro") or {}).get("municipio"),
              "eventos": len(e.get("patrocinios", [])), "areas": e.get("patrocinio_areas", []), "score": e.get("patrocinio_score", 0),
              "classe": e.get("patrocinio_classe"), "memoria": e.get("patrocinio_memoria", []), "elegivel": e.get("elegivel"),
              "organizacao_mapeada": True, "lucro_real_informativo": (e.get("lucro_real") or {}).get("classe"),
              "area_potencial": e.get("area_potencial") or area_potencial(e.get("cadastro") or {}),
              "patrocinios": [{"evento": a["evento"], "area": a["area"], "fonte": a["fonte"], "tipo_fonte": a["tipo_fonte"], "url": a["url"], "trecho": a["trecho"][:200], "em": a["em"][:10]} for a in e.get("patrocinios", [])[-10:]]}
             for k, e in base.items() if e.get("patrocinios")]
    saida.sort(key=lambda x: -x["score"])
    BIB.mkdir(parents=True, exist_ok=True)
    write_json(BIB / uf.lower() / "patrocinios.json", {"uf": uf, "gerado_em": now_iso(), "fontes": [f["nome"] for f in _cfgp()["estados"][uf]["fontes"]],
                                                     "coleta": col, "total": len(saida), "empresas": saida})
    return {"uf": uf, **col, "empresas_com_patrocinio": agregadas, "novas_na_base": novas, "executado_em": now_iso()}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
