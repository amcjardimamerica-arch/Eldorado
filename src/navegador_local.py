"""NAVEGADOR DO TITULAR PARA OS PILOTOS (titular, 03/10/2026).

Diagnóstico (estado/piloto, 29/09–03/10): do GitHub, das 6 vias de busca só o DuckDuckGo responde; o Espião faz 182–344
missões por dia e só 3,6% acham oportunidade ABERTA; o Interceptador fica "insuficiente" em 72% dos voos e 24 caíram em
"nenhuma fonte legível" (página que não abre ou só monta com JavaScript). O gargalo é o ACESSO, não o volume.

Solução: quando os Pilotos voam no computador do titular (ELDORADO_LOCAL_BR=1, scripts/pilotos_brasil.py), as buscas e
a leitura de páginas passam por um NAVEGADOR DE VERDADE, com o IP e o navegador do titular — o Microsoft Edge que já vem
no Windows, controlado pelo Playwright (ferramenta aberta da Microsoft para automatizar navegadores), com um perfil
próprio do Eldorado (cookies guardados, menos verificações). Sem Edge, usa o Chromium do Playwright.

Regras: ritmo de pessoa (pausa entre buscas), teto diário, nada de login nem de resolver verificação (CAPTCHA): se o
buscador pedir, a via descansa. Conteúdo lido é dado, nunca instrução. Sem o Playwright instalado, nada muda.
Instalação no computador: pip install playwright  (o Edge já existe; reserva: python -m playwright install chromium).
"""
from __future__ import annotations

import atexit
import json
import os
import random
import re
import time
import urllib.parse
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTADOR = ROOT / "estado/piloto/navegador_local.json"
TETO_DIA = int(os.environ.get("ELDORADO_NAVEGADOR_TETO", "400"))
PAUSA = (3.0, 7.0)                                         # segundos entre buscas: ritmo de pessoa
_ESTADO: dict = {}
VERIFICACAO = re.compile(r"captcha|n[aã]o sou um rob[oô]|unusual traffic|tr[aá]fego incomum|verify you are human|are you a robot", re.I)


def disponivel() -> bool:
    """Só no computador do titular (ou na VM do Brasil), com o Playwright instalado e sem descanso por verificação."""
    if os.environ.get("ELDORADO_LOCAL_BR") != "1" or os.environ.get("ELDORADO_SEM_NAVEGADOR") == "1":
        return False
    try:
        import playwright.sync_api  # noqa: F401
    except Exception:  # noqa: BLE001
        return False
    c = _contador()
    return c.get("dia") != date.today().isoformat() or (c.get("usos", 0) < TETO_DIA and not c.get("descanso"))


def _contador() -> dict:
    try:
        return json.loads(CONTADOR.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}


def _contar(descanso: str | None = None) -> None:
    c = _contador(); hoje = date.today().isoformat()
    if c.get("dia") != hoje:
        c = {"dia": hoje, "usos": 0}
    c["usos"] = int(c.get("usos") or 0) + 1
    if descanso:
        c["descanso"] = descanso
    CONTADOR.parent.mkdir(parents=True, exist_ok=True)
    CONTADOR.write_text(json.dumps(c, ensure_ascii=False), encoding="utf-8")


def _pagina():
    """Um navegador por processo (reaproveitado), com o perfil do Eldorado."""
    if _ESTADO.get("pagina"):
        return _ESTADO["pagina"]
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    perfil = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "Eldorado" / "navegador"
    perfil.mkdir(parents=True, exist_ok=True)
    opcoes = dict(user_data_dir=str(perfil), headless=os.environ.get("ELDORADO_NAVEGADOR_VISIVEL") != "1", locale="pt-BR",
                  viewport={"width": 1280, "height": 900})
    try:
        ctx = pw.chromium.launch_persistent_context(channel="msedge", **opcoes)     # o Edge que já vem no Windows
    except Exception:  # noqa: BLE001
        ctx = pw.chromium.launch_persistent_context(**opcoes)                       # reserva: Chromium do Playwright
    pg = ctx.pages[0] if ctx.pages else ctx.new_page()
    _ESTADO.update(pw=pw, ctx=ctx, pagina=pg)
    atexit.register(fechar)
    return pg


def fechar() -> None:
    try:
        if _ESTADO.get("ctx"):
            _ESTADO["ctx"].close()
        if _ESTADO.get("pw"):
            _ESTADO["pw"].stop()
    except Exception:  # noqa: BLE001
        pass
    _ESTADO.clear()


def resultados_bing(html: str) -> list[dict]:
    out = []
    for m in re.finditer(r'<li class="b_algo".*?<h2[^>]*>\s*<a[^>]+href="(https?://[^"]+)"[^>]*>(.*?)</a>', html, re.S):
        out.append({"url": m.group(1), "titulo": re.sub(r"<[^>]+>", "", m.group(2)).strip()})
    return out


def resultados_ddg(html: str) -> list[dict]:
    out = []
    for m in re.finditer(r'<a[^>]+class="[^"]*result__a[^"]*"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, re.S):
        u = m.group(1)
        if "uddg=" in u:
            u = urllib.parse.unquote(urllib.parse.parse_qs(urllib.parse.urlsplit(u).query).get("uddg", [u])[0])
        if u.startswith("http"):
            out.append({"url": u, "titulo": re.sub(r"<[^>]+>", "", m.group(2)).strip()})
    return out


def buscar(consulta: str, maximo: int = 10) -> list[dict]:
    """Busca no navegador do titular: Bing e, se vier pouco, DuckDuckGo. Pede verificação → a via descansa no dia."""
    pg = _pagina(); saida, vistos = [], set()
    for nome, url, ler in (("bing", "https://www.bing.com/search?setlang=pt-BR&cc=BR&q=" + urllib.parse.quote(consulta), resultados_bing),
                           ("duckduckgo", "https://html.duckduckgo.com/html/?kl=br-pt&q=" + urllib.parse.quote(consulta), resultados_ddg)):
        if len(saida) >= maximo:
            break
        time.sleep(random.uniform(*PAUSA))
        pg.goto(url, wait_until="domcontentloaded", timeout=30000)
        html = pg.content(); _contar()
        if VERIFICACAO.search(html[:20000]):
            _contar(descanso=f"{nome} pediu verificação"); continue
        for r in ler(html):
            if r["url"] not in vistos:
                vistos.add(r["url"]); saida.append({**r, "via": f"navegador do titular ({nome})"})
    return saida[:maximo]


def ler(url: str, limite: int = 60000, espera_ms: int = 12000) -> str:
    """Texto da página DEPOIS do JavaScript (o que a leitura simples não vê)."""
    pg = _pagina()
    time.sleep(random.uniform(1.0, 2.5))
    pg.goto(url, wait_until="domcontentloaded", timeout=40000)
    try:
        pg.wait_for_load_state("networkidle", timeout=espera_ms)
    except Exception:  # noqa: BLE001
        pass
    _contar()
    t = pg.inner_text("body") or ""
    return re.sub(r"[ \t]+", " ", re.sub(r"\n{3,}", "\n\n", t)).strip()[:limite]
