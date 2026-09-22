"""O PILOTO — cria prompts de busca, VOA até a internet e lê o que encontrou.

O erro que este módulo corrige: o modelo local não tem internet. Perguntar a ele "que
institutos publicam edital?" só devolve o que estava nos pesos — por isso as missões
vinham "secas". A ordem certa é outra:

    1. o Piloto CRIA a consulta de busca (é nisso que o modelo é bom: formular)
    2. o sistema EXECUTA a busca na internet (o runner do GitHub tem rede)
    3. o Piloto LÊ os resultados reais e diz o que serve, com o site oficial
    4. o que passa vira alvo; o que não passa vira lição

Busca sem API paga: DuckDuckGo HTML (html.duckduckgo.com) e Bing HTML como reserva.
"""
from __future__ import annotations

import gzip
import json
import re
import time
import urllib.parse
import urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json

CFG = ROOT / "config/motor_sindico.json"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
VETOR = re.compile(r"observatorio3setor|captadores\.org|prosas\.com|gife\.org\.br/noticias|g1\.globo|uol\.com|facebook|instagram|linkedin|youtube|twitter|x\.com|wikipedia", re.I)
LIXO = re.compile(r"duckduckgo|bing\.com|google\.|/search\?|javascript:|mailto:", re.I)


class _Res(HTMLParser):
    """Extrai (titulo, url, trecho) da página de resultados."""
    def __init__(self):
        super().__init__(); self.itens = []; self._a = None; self._t = []; self._sn = False; self._snt = []
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "a" and "result__a" in (d.get("class") or ""):
            self._a = d.get("href"); self._t = []
        elif tag == "a" and self._a is None and (d.get("href") or "").startswith("http") and "result" in (d.get("class") or ""):
            self._a = d.get("href"); self._t = []
        elif tag == "a" and "result__snippet" in (d.get("class") or ""):
            self._sn = True; self._snt = []
    def handle_data(self, s):
        if self._a is not None and not self._sn:
            self._t.append(s)
        elif self._sn:
            self._snt.append(s)
    def handle_endtag(self, tag):
        if tag == "a" and self._a is not None and not self._sn:
            tit = re.sub(r"\s+", " ", "".join(self._t)).strip()
            url = self._a
            if url.startswith("//duckduckgo.com/l/?uddg="):
                url = urllib.parse.unquote(url.split("uddg=")[1].split("&")[0])
            if tit and url.startswith("http") and not LIXO.search(url):
                self.itens.append({"titulo": tit[:160], "url": url, "trecho": ""})
            self._a = None
        elif tag == "a" and self._sn:
            if self.itens:
                self.itens[-1]["trecho"] = re.sub(r"\s+", " ", "".join(self._snt)).strip()[:300]
            self._sn = False


def buscar(consulta: str, maximo: int = 10, tempo: float = 20) -> list[dict]:
    """Busca real na internet, sem API paga. Devolve [{titulo, url, trecho}]."""
    for base in ("https://html.duckduckgo.com/html/?q=", "https://lite.duckduckgo.com/lite/?q="):
        try:
            req = urllib.request.Request(base + urllib.parse.quote(consulta), headers={"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9"})
            with urllib.request.urlopen(req, timeout=tempo) as r:
                html = r.read().decode("utf-8", "ignore")
            p = _Res(); p.feed(html)
            if p.itens:
                return p.itens[:maximo]
        except Exception:
            time.sleep(1.5)
    return []


def ler_pagina(url: str, limite: int = 6000, tempo: float = 20) -> str:
    """Texto da página, para o Piloto confirmar que é oportunidade de verdade."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=tempo) as r:
            bruto = r.read(400_000)
            if (r.headers.get("Content-Encoding") or "") == "gzip":
                bruto = gzip.decompress(bruto)
            html = bruto.decode("utf-8", "ignore")
        html = re.sub(r"(?is)<(script|style|nav|footer|header)[^>]*>.*?</\1>", " ", html)
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()[:limite]
    except Exception:
        return ""


def _oficial(url: str) -> bool:
    return bool(url) and url.startswith("http") and not VETOR.search(url)


def caçar(ia, angulo: dict, conhecidos: set[str], max_consultas: int = 3, max_paginas: int = 4) -> tuple[list[dict], str, list[str]]:
    """O voo completo: o Piloto cria as consultas, busca, lê e decide.
    Devolve (achados, lição, consultas usadas)."""
    from .cargo_sindico import licoes_para_o_prompt
    cfg = load_json(CFG)
    lic = licoes_para_o_prompt()
    # 1) o Piloto CRIA as consultas de busca
    r = ia.perguntar((lic + "\n\n" if lic else "") +
                     f"OBJETIVO DA MISSÃO: {angulo['pergunta']}\n"
                     "Escreva consultas de busca na web (português do Brasil) que encontrem PÁGINAS OFICIAIS dessas oportunidades. "
                     "Use termos que apareceriam no site do financiador, não em notícia. Exemplos de bons termos: \"edital\", \"chamada pública\", "
                     "\"seleção de projetos\", \"inscrições\", \"instituto\", \"fundação\", \"organizações da sociedade civil\", mais o recorte do objetivo.",
                     '{"consultas": ["consulta 1", "consulta 2", "consulta 3"]}')
    consultas = [c for c in ((r or {}).get("consultas") or []) if isinstance(c, str) and len(c) > 8][:max_consultas]
    if not consultas:                                   # rede de segurança: consulta montada do próprio ângulo
        consultas = [re.sub(r"\s+", " ", angulo["pergunta"])[:110] + " edital site oficial"]
    # 2) BUSCA DE VERDADE
    brutos, vistos = [], set()
    for c in consultas:
        for it in buscar(c, 8):
            if it["url"] in vistos:
                continue
            vistos.add(it["url"]); brutos.append({**it, "consulta": c})
    if not brutos:
        return [], f"ângulo '{angulo['id']}': a busca não devolveu resultado (rede ou bloqueio)", consultas
    # 3) o Piloto LÊ os resultados reais e escolhe
    lista = "\n".join(f"{i+1}. {b['titulo']} — {b['url']}\n   {b['trecho'][:160]}" for i, b in enumerate(brutos[:14]))
    q = ia.perguntar(f"OBJETIVO: {angulo['pergunta']}\n\nRESULTADOS REAIS DA BUSCA:\n{lista}\n\n"
                     "Quais destes são MESMO oportunidade de recurso para organização sem fins lucrativos (edital, chamada, seleção de projetos, patrocínio, doação, incentivo fiscal)? "
                     "Descarte notícia, vaga de emprego, licitação, curso e página institucional sem oportunidade.",
                     '{"escolhidos": [{"n": número da lista, "porque": "uma frase", "tipo": "edital|programa|financiador"}]}')
    escolhidos = [(x.get("n"), x) for x in ((q or {}).get("escolhidos") or []) if isinstance(x.get("n"), int) and 1 <= x["n"] <= len(brutos[:14])]
    achados = []
    for n, x in escolhidos[:max_paginas]:
        b = brutos[n - 1]
        texto = ler_pagina(b["url"])                     # 4) confirma na própria página
        conf = None
        if len(texto) < 300:                              # página não abriu: o trecho do resultado ainda serve de pista
            texto = f"{b['titulo']} {b.get('trecho','')}"
        if len(texto) > 60:
            conf = ia.perguntar(f"PÁGINA: {b['url']}\nTEXTO: {texto[:3500]}\n\nIsto é uma oportunidade de recurso para organização sem fins lucrativos?",
                                '{"e_oportunidade": true|false, "nome": "nome da oportunidade ou do financiador", "trecho": "frase literal da página que comprova", "quem_pode": "...", "onde_inscrever": "url ou null"}')
        def _n(s): return re.sub(r"[^a-z0-9 ]", " ", re.sub(r"\s+", " ", (s or "").lower())).strip()
        ok = bool(conf and conf.get("e_oportunidade") and conf.get("trecho") and _n(str(conf["trecho"]))[:45] in _n(texto))
        nome = (conf or {}).get("nome") or b["titulo"]
        chave = re.sub(r"[^a-z0-9 ]", "", str(nome).lower())[:60]
        achados.append({"titulo": str(nome)[:110], "onde": b["url"][:140], "url": b["url"],
                        "trecho": (conf or {}).get("trecho", "")[:180], "porque": x.get("porque", "")[:120],
                        "consulta": b["consulta"][:90], "confirmado_na_pagina": ok,
                        "novo": ok and _oficial(b["url"]) and chave not in conhecidos})
    novos = sum(1 for a in achados if a["novo"])
    licao = (f"ângulo '{angulo['id']}': {len(consultas)} consulta(s) → {len(brutos)} resultado(s) → {len(achados)} lido(s) → {novos} confirmado(s) na página"
             if achados else f"ângulo '{angulo['id']}': busca voltou {len(brutos)} resultados, nenhum passou no crivo")
    return achados, licao, consultas


if __name__ == "__main__":
    import sys
    print(json.dumps(buscar(" ".join(sys.argv[1:]) or "edital organizações da sociedade civil 2026", 6), ensure_ascii=False, indent=1))
