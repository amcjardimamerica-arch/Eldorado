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


class _ResGoogle(HTMLParser):
    """Resultados do Google HTML: links em /url?q=<destino>&sa=..."""
    def __init__(self):
        super().__init__(); self.itens = []; self._a = None; self._t = []
    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        h = dict(attrs).get("href") or ""
        if h.startswith("/url?q="):
            u = urllib.parse.unquote(h[7:].split("&")[0])
            if u.startswith("http") and not LIXO.search(u):
                self._a = u; self._t = []
    def handle_data(self, s):
        if self._a is not None:
            self._t.append(s)
    def handle_endtag(self, tag):
        if tag == "a" and self._a is not None:
            tit = re.sub(r"\s+", " ", "".join(self._t)).strip()
            if len(tit) > 8:
                self.itens.append({"titulo": tit[:160], "url": self._a, "trecho": ""})
            self._a = None


BUSCADORES = [
    ("duckduckgo", "https://html.duckduckgo.com/html/?q={q}", _Res),
    ("google", "https://www.google.com/search?q={q}&hl=pt-BR&num=20", _ResGoogle),
    ("duckduckgo-lite", "https://lite.duckduckgo.com/lite/?q={q}", _Res),
    ("bing", "https://www.bing.com/search?q={q}&setlang=pt-BR&count=20", _Res),
]


def buscar(consulta: str, maximo: int = 10, tempo: float = 20, motores: list[str] | None = None) -> list[dict]:
    """Busca real na internet em VÁRIOS buscadores (DuckDuckGo + Google + Bing), sem API paga.
    Os resultados são misturados e deduplicados por URL; cada item traz de onde veio."""
    saida, vistos = [], set()
    alvos = [b for b in BUSCADORES if not motores or b[0] in motores]
    for nome, molde, parser in alvos:
        try:
            url = molde.format(q=urllib.parse.quote(consulta))
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9",
                                                       "Accept": "text/html,application/xhtml+xml"})
            with urllib.request.urlopen(req, timeout=tempo) as r:
                bruto = r.read()
                if (r.headers.get("Content-Encoding") or "") == "gzip":
                    bruto = gzip.decompress(bruto)
                html = bruto.decode("utf-8", "ignore")
            p = parser(); p.feed(html)
            for it in p.itens:
                chave = re.sub(r"[#?].*$", "", it["url"]).rstrip("/")
                if chave in vistos:
                    continue
                vistos.add(chave); saida.append({**it, "buscador": nome})
            if len(saida) >= maximo * 2:
                break
        except Exception:
            time.sleep(1.2)
    return saida[:maximo]


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


def _similar(a: str, b: str) -> float:
    """Jaccard entre conjuntos de palavras — barato e suficiente para barrar consulta repetida."""
    A = {w for w in re.findall(r"[a-zà-ú0-9]{4,}", (a or "").lower())}
    B = {w for w in re.findall(r"[a-zà-ú0-9]{4,}", (b or "").lower())}
    return len(A & B) / len(A | B) if A and B else 0.0


def consultas_ja_usadas(n: int = 60) -> list[str]:
    cfg = load_json(CFG) if CFG.exists() else {}
    fora = []
    for r in (cfg.get("consultas_usadas") or [])[:n]:
        fora += [c for c in (r.get("consultas") or [])]
    return fora[:n]


def inedita(c: str, usadas: list[str], teto: float | None = None) -> bool:
    teto = teto if teto is not None else ((load_json(CFG).get("prompt_unico") or {}).get("similaridade_maxima") or 0.72)
    return all(_similar(c, u) < teto for u in usadas)


def caçar(ia, angulo: dict, conhecidos: set[str], max_consultas: int = 3, max_paginas: int = 4) -> tuple[list[dict], str, list[str]]:
    """O voo completo: o Piloto cria as consultas, busca, lê e decide.
    Devolve (achados, lição, consultas usadas)."""
    from .cargo_sindico import licoes_para_o_prompt
    cfg = load_json(CFG)
    lic = licoes_para_o_prompt()
    # 1) o Piloto CRIA um QUESTIONAMENTO NOVO — nunca repete consulta nem variação próxima
    usadas = consultas_ja_usadas()
    amostra = usadas[:18]
    r = ia.perguntar((lic + "\n\n" if lic else "") +
                     f"OBJETIVO DA MISSÃO ({angulo.get('nivel','')}): {angulo['pergunta']}\n\n"
                     + ("JÁ PERGUNTEI ISTO ANTES (não repita, nem com palavras parecidas):\n- " + "\n- ".join(amostra) + "\n\n" if amostra else "")
                     + "Escreva consultas de busca NOVAS, em português do Brasil, que encontrem PÁGINAS OFICIAIS. "
                       "Foque em EMPRESA PRIVADA: instituto próprio, fundação, programa social, relatório ESG, patrocínio declarado, edital de anos anteriores. "
                       "Varie o ângulo a cada consulta (setor, região, tipo de documento, ano) — consultas parecidas entre si não servem.",
                     '{"consultas": ["consulta 1", "consulta 2", "consulta 3"], "porque_sao_novas": "uma frase"}')
    brutas = [c for c in ((r or {}).get("consultas") or []) if isinstance(c, str) and len(c) > 8]
    consultas, descartadas = [], 0
    for c in brutas:
        if inedita(c, usadas + consultas):
            consultas.append(c)
        else:
            descartadas += 1
        if len(consultas) >= max_consultas:
            break
    if not consultas:                                   # rede de segurança com variação do ângulo e do ano
        import random as _rr
        tempero = _rr.Random(f"{date.today()}-{angulo['id']}").choice(["site oficial", "edital 2026", "programa social", "relatório ESG", "seleção de projetos", "instituto"])
        consultas = [re.sub(r"\s+", " ", angulo["pergunta"])[:100] + " " + tempero]
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
            conf = ia.perguntar(
                f"PÁGINA: {b['url']}\nTEXTO: {texto[:3500]}\n\n"
                "Isto é uma oportunidade de recurso para organização sem fins lucrativos? "
                "Leia com atenção o PRAZO e os DOCUMENTOS exigidos. "
                "Se o prazo já passou ou o edital é de ano anterior, marque situacao='arquivada' — ela ainda serve, "
                "porque indica que o financiador costuma abrir de novo. Só escreva prazo se a data estiver ESCRITA na página.",
                '{"e_oportunidade": true|false, "nome": "nome da oportunidade ou do financiador", '
                '"trecho": "frase literal da página que comprova", "quem_pode": "...", "onde_inscrever": "url ou null", '
                '"situacao": "aberta|arquivada|sem_prazo_na_pagina", "prazo": "AAAA-MM-DD ou null", '
                '"documentos": ["documento exigido", "..."], "valor": "o que a página diz sobre valores ou null", '
                '"recorrente": true|false}')
        def _n(s): return re.sub(r"[^a-z0-9 ]", " ", re.sub(r"\s+", " ", (s or "").lower())).strip()
        ok = bool(conf and conf.get("e_oportunidade") and conf.get("trecho") and _n(str(conf["trecho"]))[:45] in _n(texto))
        nome = (conf or {}).get("nome") or b["titulo"]
        chave = re.sub(r"[^a-z0-9 ]", "", str(nome).lower())[:60]
        c = conf or {}
        prazo = c.get("prazo") if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(c.get("prazo") or "")) else None
        sit = c.get("situacao") if c.get("situacao") in ("aberta", "arquivada", "sem_prazo_na_pagina") else "sem_prazo_na_pagina"
        if prazo:                                         # a data manda: o modelo às vezes erra o rótulo
            sit = "aberta" if prazo >= date.today().isoformat() else "arquivada"
        achados.append({"titulo": str(nome)[:110], "onde": b["url"][:140], "url": b["url"],
                        "trecho": c.get("trecho", "")[:180], "porque": x.get("porque", "")[:120],
                        "situacao": sit, "prazo": prazo,
                        "documentos": [str(d)[:70] for d in (c.get("documentos") or [])][:8],
                        "quem_pode": str(c.get("quem_pode") or "")[:120], "valor": str(c.get("valor") or "")[:90],
                        "recorrente": bool(c.get("recorrente")), "onde_inscrever": c.get("onde_inscrever"),
                        "consulta": b["consulta"][:90], "confirmado_na_pagina": ok,
                        "novo": ok and _oficial(b["url"]) and chave not in conhecidos})
    novos = sum(1 for a in achados if a["novo"])
    abertas = sum(1 for a in achados if a.get("situacao") == "aberta")
    arquiv = sum(1 for a in achados if a.get("situacao") == "arquivada")
    fontes = ", ".join(sorted({b.get("buscador", "?") for b in brutos}))
    licao = (f"ângulo '{angulo['id']}': {len(consultas)} consulta(s) nova(s)" + (f" ({descartadas} repetida(s) descartada(s))" if descartadas else "") +
             f" → {len(brutos)} resultado(s) [{fontes}] → {len(achados)} lido(s) → {novos} confirmado(s) na página"
             f" ({abertas} aberta(s), {arquiv} arquivada(s))"
             if achados else f"ângulo '{angulo['id']}': busca voltou {len(brutos)} resultados, nenhum passou no crivo")
    return achados, licao, consultas


if __name__ == "__main__":
    import sys
    print(json.dumps(buscar(" ".join(sys.argv[1:]) or "edital organizações da sociedade civil 2026", 6), ensure_ascii=False, indent=1))
