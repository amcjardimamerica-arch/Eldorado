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
    pg.goto("http://127.0.0.1:8765/dashboard.html", wait_until="networkidle")
    pg.evaluate("()=>{ if(window.modulo) modulo('eldorado'); mostra('neural'); }")
    pg.wait_for_timeout(6000)
    for i, y in enumerate((0, 1400, 2800)):
        pg.evaluate(f"window.scrollTo(0,{y})")
        pg.wait_for_timeout(1200)
        pg.screenshot(path=str(SAIDA / f"sala-{i + 1}.png"))
    r["medida"] = pg.evaluate("""()=>new Promise(ok=>{ const q=[]; let ant=performance.now(), y=0;
      function passo(t){ q.push(t-ant); ant=t; y+=40; window.scrollTo(0,y); if(q.length<120) requestAnimationFrame(passo);
        else { q.sort((a,b)=>a-b); ok({quadros:q.length, mediana_ms:+q[60].toFixed(1), p95_ms:+q[114].toFixed(1)}); } }
      requestAnimationFrame(passo); })""")
    r["rede"] = pg.evaluate("""()=>{ const s=document.getElementById('nv-rede'); const c=document.getElementById('nv-ceu');
      return {linhas: s? s.querySelectorAll('path').length:0, constelacoes: s? s.querySelectorAll('g.cons').length:0,
              estrelas_vermelhas: s? s.querySelectorAll('.vermelha').length:0, sinais: s? s.querySelectorAll('animateMotion').length:0,
              fundo: c? getComputedStyle(c).position:null, faixas: document.querySelectorAll('#v-neural .faixa').length}; }""")
    # as linhas no lugar: a ponta de cada sinapse tem de estar na borda da faixa (até 6 px)
    r["alinhamento"] = pg.evaluate("""()=>{ const P=document.getElementById('nv-palco'), pt=P.getBoundingClientRect().top;
      const F=[...document.querySelectorAll('#v-neural .faixa')].map(f=>{const q=f.getBoundingClientRect(); return [q.top-pt,q.bottom-pt];});
      const L=[...document.querySelectorAll('#nv-rede > path')].map(p=>p.getAttribute('d').match(/-?[\\d.]+/g).map(Number));
      return L.map((n,i)=>F[i]&&F[i+1]? Math.max(Math.abs(n[1]-(F[i][1]+2)), Math.abs(n[7]-(F[i+1][0]-2))):null); }""")
    r["erros_da_pagina"] = erros
    b.close()
(SAIDA / "sala.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(r, ensure_ascii=False))
