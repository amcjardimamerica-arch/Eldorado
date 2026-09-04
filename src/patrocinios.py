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


def _fontes_descobertas(uf: str) -> dict:
    arq = ROOT / _cfgp()["estados"][uf]["descoberta_semanal"]["arquivo"]
    return load_json(arq) if arq.exists() else {"uf": uf, "verificadas": [], "candidatas": {}, "leituras": []}


def descobrir_fontes(uf: str, html_por_url: dict, fontes_atuais: list[dict]) -> dict:
    """SEMANAL: recolhe, nas páginas lidas, links para novos sites de Goiás que
    divulgam eventos/festivais/shows ou são meios de comunicação; verifica cada
    candidato (responde e fala de eventos/patrocínio) e só então o inclui."""
    from html.parser import HTMLParser
    from urllib.parse import urlsplit, urljoin
    cfg = _cfgp()["estados"][uf]["descoberta_semanal"]
    est = _fontes_descobertas(uf)
    dominios = {urlsplit(f["url"]).hostname.replace("www.", "") for f in fontes_atuais} | {urlsplit(v["url"]).hostname.replace("www.", "") for v in est["verificadas"]}
    class L(HTMLParser):
        def __init__(self): super().__init__(); self.l = []; self._h = None; self._t = []
        def handle_starttag(self, tag, attrs):
            if tag == "a": self._h = dict(attrs).get("href"); self._t = []
        def handle_data(self, d):
            if self._h is not None: self._t.append(d)
        def handle_endtag(self, tag):
            if tag == "a" and self._h is not None: self.l.append((self._h, " ".join(self._t).strip())); self._h = None
    sinais = re.compile("|".join(map(re.escape, cfg["sinais_goias"])), re.I)
    midia = re.compile(r"festival|show|evento|agenda|r[áa]dio|\btv\b|jornal|portal|not[íi]cias|cultura|esporte|arena|est[áa]dio|teatro|feira", re.I)
    for url, html in html_por_url.items():
        p = L()
        try: p.feed(html)
        except Exception: continue
        for h, rot in p.l:
            if not h or not h.startswith("http"): continue
            dom = (urlsplit(h).hostname or "").lower().replace("www.", "")
            if not dom or dom in dominios or any(x in dom for x in ("facebook", "instagram", "twitter", "youtube", "whatsapp", "google", "globo.com", "uol.com", "linkedin", "tiktok", "apple", "spotify")):
                continue
            if sinais.search(dom + " " + (rot or "")) and midia.search(dom + " " + (rot or "")):
                c = est["candidatas"].setdefault(dom, {"dominio": dom, "vista_em": [], "rotulos": [], "de": []})
                c["vista_em"].append(now_iso()[:10]); c["vista_em"] = sorted(set(c["vista_em"]))[-10:]
                if rot and rot[:60] not in c["rotulos"]: c["rotulos"] = (c["rotulos"] + [rot[:60]])[-5:]
                if url not in c["de"]: c["de"] = (c["de"] + [url])[-5:]
    # verificação: candidato responde e fala de eventos/patrocínio → entra no rol
    novas = 0
    for dom, c in sorted(est["candidatas"].items(), key=lambda kv: -len(kv[1]["vista_em"])):
        if novas >= cfg["maximo_novas_por_semana"] or c.get("verificada") is not None:
            continue
        try:
            html = _get(f"https://{dom}", timeout=15)
            txt = re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S))
            ok = bool(re.search(r"patroc[íi]nio|festival|evento|show|agenda cultural|esporte", txt, re.I)) and bool(sinais.search(txt[:20000]))
            c["verificada"] = ok; c["verificada_em"] = now_iso()
            if ok:
                est["verificadas"].append({"nome": dom, "url": f"https://{dom}", "tipo": "descoberta", "incluida_em": now_iso()[:10], "rotulos": c["rotulos"]}); novas += 1
        except Exception as exc:
            c["verificada"] = False; c["erro"] = type(exc).__name__
        time.sleep(0.4)
    est["leituras"] = (est.get("leituras") or [])[-30:] + [{"em": now_iso(), "candidatas": len(est["candidatas"]), "novas_verificadas": novas, "total_verificadas": len(est["verificadas"])}]
    write_json(ROOT / cfg["arquivo"], est)
    return {"candidatas": len(est["candidatas"]), "novas": novas, "verificadas": len(est["verificadas"])}


def coletar(uf: str = "GO", limite_paginas: int = 40) -> dict:
    cfg = _cfgp(); est = cfg["estados"][uf]
    destino = PASTA / uf.lower() / "patrocinios.json"
    atual = load_json(destino) if destino.exists() else {"uf": uf, "achados": [], "leituras": [], "cursor": 0}
    fontes = est["fontes"] + _fontes_descobertas(uf).get("verificadas", [])     # rol configurado + descobertas verificadas
    lidas, novos = 0, 0; html_lidos = {}
    inicio = atual.get("cursor", 0)
    for i in range(len(fontes)):
        f = fontes[(inicio + i) % len(fontes)]
        for pg in est["paginas_por_fonte"]:
            if lidas >= limite_paginas:
                break
            url = f["url"].rstrip("/") + pg
            try:
                html = _get(url, timeout=15); lidas += 1; html_lidos[url] = html
                txt = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S)
                txt = re.sub(r"<[^>]+>", " ", txt); txt = re.sub(r"\s+", " ", txt)
                for a in extrair_patrocinios(txt, f, url):
                    if not any(x["url"] == a["url"] and x["empresa"].upper() == a["empresa"].upper() and x["evento"] == a["evento"] for x in atual["achados"]):
                        atual["achados"].append(a); novos += 1
            except Exception:
                pass
            time.sleep(0.4)
    atual["cursor"] = (inicio + 1) % len(fontes)
    desc = descobrir_fontes(uf, html_lidos, fontes)
    atual["descoberta"] = desc
    atual["achados"] = atual["achados"][-3000:]
    atual["leituras"] = (atual.get("leituras") or [])[-30:] + [{"em": now_iso(), "paginas_lidas": lidas, "novos": novos}]
    write_json(destino, atual)
    return {"paginas_lidas": lidas, "novos": novos, "total": len(atual["achados"]), "fontes": len(fontes), "descoberta": desc}


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
    rel = {"uf": uf, **col, "empresas_com_patrocinio": agregadas, "novas_na_base": novas, "executado_em": now_iso()}
    # registro no diário semanal (alimenta o calendário do motor no painel)
    sem_p = ROOT / "estado/empresas_semanal.jsonl"
    if sem_p.exists():
        linhas = [l for l in sem_p.read_text(encoding="utf-8").splitlines() if l.strip()]
        if linhas:
            ult = json.loads(linhas[-1]); ult["patrocinios_novos"] = col.get("novos", 0); ult["patrocinios_total"] = col.get("total", 0)
            linhas[-1] = json.dumps(ult, ensure_ascii=False); sem_p.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return rel


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
