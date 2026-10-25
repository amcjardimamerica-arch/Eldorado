"""Abre a sala de controle num navegador, fotografa em três alturas de rolagem e mede os quadros ao rolar
(o fluxo 'Visualizar a sala de controle'). Saída: testes/capturas/sala-*.png e testes/capturas/sala.json."""
import http.server
import json
import threading
from functools import partial
from pathlib import Path

from patchright.sync_api import sync_playwright

SITE, SAIDA = Path("_site"), Path("testes/capturas")
SAIDA.mkdir(parents=True, exist_ok=True)
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8765), partial(http.server.SimpleHTTPRequestHandler, directory=str(SITE)))
threading.Thread(target=srv.serve_forever, daemon=True).start()
r = {}
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    pg = b.new_page(viewport={"width": 1600, "height": 950})
    erros = []
    pg.on("pageerror", lambda e: erros.append(str(e)[:300]))
    pg.goto("http://127.0.0.1:8765/dashboard.html", wait_until="load", timeout=60000)
    try:
        pg.evaluate("()=>document.querySelector(\"button[data-v='neural']\").click()")   # o botão da navegação (escondido até abrir o menu)
    except Exception as e:  # noqa: BLE001
        r["erro_ao_abrir"] = str(e)[:300]
    pg.wait_for_timeout(6000)
    for i, y in enumerate((0, 1400, 2800)):
        pg.evaluate(f"window.scrollTo(0,{y})")
        pg.wait_for_timeout(1200)
        pg.screenshot(path=str(SAIDA / f"sala-{i + 1}.png"))
    try:
        r["medida"] = pg.evaluate("""()=>new Promise(ok=>{ const q=[]; let ant=performance.now(), y=0;
          function passo(t){ q.push(t-ant); ant=t; y+=40; window.scrollTo(0,y); if(q.length<120) requestAnimationFrame(passo);
            else { q.sort((a,b)=>a-b); ok({quadros:q.length, mediana_ms:+q[60].toFixed(1), p95_ms:+q[114].toFixed(1)}); } }
          requestAnimationFrame(passo); })""")
    except Exception as e:  # noqa: BLE001
        r["medida"] = {"erro": str(e)[:300]}
    try:
        r["rede"] = pg.evaluate("""()=>{ const s=document.getElementById('nv-rede'); const c=document.getElementById('nv-ceu');
          return {linhas: s? s.querySelectorAll('path').length:0, constelacoes: s? s.querySelectorAll('g.cons').length:0,
                  estrelas_vermelhas: s? s.querySelectorAll('.vermelha').length:0, sinais: s? s.querySelectorAll('animateMotion').length:0,
                  fundo: c? getComputedStyle(c).position:null, faixas: document.querySelectorAll('#v-neural .faixa').length}; }""")
    except Exception as e:  # noqa: BLE001
        r["rede"] = {"erro": str(e)[:300]}
    # as linhas no lugar: a ponta de cada sinapse tem de estar na borda da faixa (até 6 px)
    try:
        r["alinhamento"] = pg.evaluate("""()=>{ const P=document.getElementById('nv-palco'), pt=P.getBoundingClientRect().top;
          const F=[...document.querySelectorAll('#v-neural .faixa')].map(f=>{const q=f.getBoundingClientRect(); return [q.top-pt,q.bottom-pt];});
          const L=[...document.querySelectorAll('#nv-rede > path')].map(p=>p.getAttribute('d').match(/-?[\\d.]+/g).map(Number));
          return L.map((n,i)=>F[i]&&F[i+1]? Math.max(Math.abs(n[1]-(F[i][1]+2)), Math.abs(n[7]-(F[i+1][0]-2))):null); }""")
    except Exception as e:  # noqa: BLE001
        r["alinhamento"] = {"erro": str(e)[:300]}
    try:                                                       # o mapa dos arquivos, com as linhas de um arquivo acesas
        pg.evaluate("document.getElementById('nv-mapa').scrollIntoView()")
        pg.wait_for_timeout(2500)
        pg.screenshot(path=str(SAIDA / "mapa-1.png"))
        pg.evaluate("()=>{const b=[...document.querySelectorAll('#nv-mapa .st')].find(x=>x.dataset.c.endsWith('cerebro/regencia.py'));"
                    " if(b){b.scrollIntoView({block:'center'}); b.click();}}")
        pg.wait_for_timeout(1200)
        pg.screenshot(path=str(SAIDA / "mapa-2.png"))
        r["mapa"] = pg.evaluate("()=>({arquivos:document.querySelectorAll('#nv-mapa .st').length,"
                                " linhas_acesas:document.querySelectorAll('#nv-mapa-linhas path').length,"
                                " ficha:!!document.querySelector('#nv-mapa-ficha.aberta')})")
    except Exception as e:  # noqa: BLE001
        r["mapa"] = {"erro": str(e)[:300]}
    r["erros_da_pagina"] = erros
    b.close()
# o SITE PUBLICADO (o endereço público): a sala, o mapa e os mostradores lá, e não numa cópia
try:
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        pg = b.new_page(viewport={"width": 1600, "height": 950})
        pg.goto("https://amcjardimamerica-arch.github.io/Eldorado/dashboard.html?v=" + str(__import__("time").time()), wait_until="load", timeout=60000)
        pg.wait_for_timeout(5000)                               # a página inicial: as oportunidades repetidas na tela
        pg.screenshot(path=str(SAIDA / "publicado-inicio.png"))
        r["repetidos_inicio"] = pg.evaluate("""()=>{ const t=[...document.querySelectorAll('a,div,li,span')].filter(e=>e.children.length===0)
            .map(e=>e.innerText.trim()).filter(x=>x.length>25); const c={}; t.forEach(x=>c[x]=(c[x]||0)+1);
            return Object.entries(c).filter(([k,v])=>v>1).sort((a,b)=>b[1]-a[1]).slice(0,15); }""")
        pg.evaluate("()=>document.querySelector(\"button[data-v='neural']\").click()")
        pg.wait_for_timeout(7000)
        pg.screenshot(path=str(SAIDA / "publicado-sala.png"))
        r["publicado"] = pg.evaluate("""()=>({mapa: !!document.getElementById('nv-mapa'), rede: !!document.getElementById('nv-rede'),
            faixas: document.querySelectorAll('#v-neural .faixa').length,
            sem_leitura: [...document.querySelectorAll('#v-neural .faixa')].filter(f=>/sem leitura/.test(f.innerText)).length,
            indice: (document.getElementById('nv-contagens')||{}).innerText||''})""")
        pg.evaluate("document.getElementById('nv-mapa') && document.getElementById('nv-mapa').scrollIntoView()")
        pg.wait_for_timeout(3000)
        pg.screenshot(path=str(SAIDA / "publicado-mapa.png"))
        try:                                                   # o Cartório (25/10/2026): os mostradores e a ficha de um livro
            pg.evaluate("()=>document.querySelector(\"button[data-v='cartorio']\").click()")
            pg.wait_for_timeout(8000)
            pg.screenshot(path=str(SAIDA / "publicado-cartorio.png"))
            pg.evaluate("()=>{const d=document.querySelector('#car-lista details.c'); if(d){d.open=true; d.scrollIntoView();}}")
            pg.wait_for_timeout(4000)
            pg.screenshot(path=str(SAIDA / "publicado-cartorio-ficha.png"))
            r["cartorio"] = pg.evaluate("()=>({etapas:(document.getElementById('car-m-etapas')||{}).innerText||'',"
                                        " livros:document.querySelectorAll('#car-lista details.c').length, ficha:!!document.querySelector('#car-lista .ficha')})")
        except Exception as e:  # noqa: BLE001
            r["cartorio"] = {"erro": str(e)[:300]}
        b.close()
except Exception as e:  # noqa: BLE001
    r["publicado"] = {"erro": str(e)[:300]}
(SAIDA / "sala.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(r, ensure_ascii=False))
