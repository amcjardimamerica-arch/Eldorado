"""Degraus 3 a 5: os navegadores, para páginas que só existem depois do JavaScript.

- 3 · Lightpanda (medido: 58 ms e 24 MB por página, contra 156 ms e 484 MB do Chromium). A ESPERA É OBRIGATÓRIA: sem
  ela, o teste entregou 0 de 50 editais; com a espera (seletor ou rede ociosa), 50 de 50.
- 4 · Navegador não detectável (Patchright; extra 'navegador').
- 5 · Navegador anti-detecção (Camoufox; extra 'navegador').
Todos são pesados: só começam com a permissão do governador. Sem o binário ou o extra, o degrau é pulado com aviso.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from .escada import Indisponivel, Passageiro, Resposta


class DegrauLightpanda:
    nome = "3 · navegador leve (Lightpanda)"
    pesado = True

    def __init__(self, binario: str | None = None, espera_seletor: str | None = None, espera: str = "networkidle"):
        self.binario = binario or os.environ.get("ELDORADO_LIGHTPANDA") or shutil.which("lightpanda")
        if espera not in ("load", "domcontentloaded", "networkalmostidle", "networkidle", "done"):
            raise ValueError("espera inválida")
        self.espera_seletor, self.espera = espera_seletor, espera

    def buscar(self, url: str, tempo_limite: float) -> Resposta:
        if not self.binario or not Path(self.binario).exists():
            raise Indisponivel("binário do Lightpanda não encontrado (variável ELDORADO_LIGHTPANDA)")
        cmd = [self.binario, "fetch", "--dump", "html"]
        cmd += ["--wait-selector", self.espera_seletor] if self.espera_seletor else ["--wait-until", self.espera]
        try:
            p = subprocess.run(cmd + [url], capture_output=True, timeout=tempo_limite)
        except subprocess.TimeoutExpired as e:
            raise Passageiro("Lightpanda: tempo esgotado") from e
        if p.returncode != 0 and not p.stdout:
            raise Passageiro(f"Lightpanda saiu com {p.returncode}: {p.stderr[-200:].decode(errors='ignore')}")
        return Resposta(url, 200, p.stdout, "text/html")


class DegrauNavegador:
    """Degraus 4 e 5: Patchright (não detectável) ou Camoufox (anti-detecção), pelo mesmo contrato do Playwright."""
    pesado = True

    def __init__(self, motor: str = "patchright", espera_seletor: str | None = None):
        if motor not in ("patchright", "camoufox"):
            raise ValueError("motor: patchright ou camoufox")
        self.motor, self.espera_seletor = motor, espera_seletor
        self.nome = "4 · navegador não detectável (Patchright)" if motor == "patchright" else "5 · navegador anti-detecção (Camoufox)"

    def buscar(self, url: str, tempo_limite: float) -> Resposta:
        try:
            if self.motor == "patchright":
                from patchright.sync_api import sync_playwright
                gerente = sync_playwright()
            else:
                from camoufox.sync_api import Camoufox
                gerente = Camoufox(headless=True)
        except ImportError as e:
            raise Indisponivel(f"{self.motor} não instalado (extra 'navegador')") from e
        try:
            with gerente as g:
                navegador = g.chromium.launch(headless=True) if self.motor == "patchright" else g
                pagina = navegador.new_page()
                tempo = max(tempo_limite, 60.0) * 1000              # o navegador é mais lento que um pedido simples
                resp = pagina.goto(url, timeout=tempo, wait_until="domcontentloaded")
                try:                                                # a rede acalma? (rastreadores e anúncios nunca acalmam)
                    pagina.wait_for_load_state("networkidle", timeout=15000)
                except Exception:  # noqa: BLE001 — segue com o que os scripts já montaram
                    pagina.wait_for_timeout(3000)
                if self.espera_seletor:
                    pagina.wait_for_selector(self.espera_seletor, timeout=tempo)
                tipo = (resp.headers.get("content-type", "") if resp else "") or "text/html"
                if resp is not None and "html" not in tipo.lower():
                    html = resp.body()                              # JSON, XML, PDF: o conteúdo original, não a página que o navegador monta em volta
                else:
                    html = pagina.content().encode("utf-8")
                navegador.close()
        except Exception as e:  # noqa: BLE001 — falha do navegador (não do site) é passageira; o motor registra
            if "Executable doesn't exist" in str(e) or "playwright install" in str(e):
                raise Indisponivel(f"{self.motor}: navegador não instalado") from e
            raise Passageiro(f"{self.motor}: {type(e).__name__}: {e}") from e
        return Resposta(url, resp.status if resp else 200, html, tipo if resp is not None else "text/html")
