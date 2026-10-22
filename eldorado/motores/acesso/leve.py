"""Degrau 2: requisição leve com assinatura de navegador real (TLS e cabeçalhos de um Chrome).

Duas assinaturas diferentes: curl_cffi e, se ele for barrado, primp (medido: 40% mais rápido; outra assinatura de TLS).
Quando um site barra uma, a outra costuma passar. Também carrega certificados que alguns órgãos não enviam.
"""
from __future__ import annotations

from .escada import Bloqueado, Passageiro, Resposta


class DegrauLeve:
    nome = "2 · requisição com assinatura de navegador (curl_cffi, primp)"
    pesado = False

    def __init__(self, proxy: str | None = None):
        from curl_cffi import requests as cr
        self._cr = cr
        self.sessao = cr.Session(impersonate="chrome", proxies={"http": proxy, "https": proxy} if proxy else None)
        self._primp = None
        self.proxy = proxy

    def _por_primp(self, url: str, tempo_limite: float) -> Resposta:
        import primp
        if self._primp is None:
            try:
                self._primp = primp.Client(impersonate="chrome_131", follow_redirects=True, timeout=tempo_limite, proxy=self.proxy)
            except Exception:  # noqa: BLE001 — nome de perfil muda entre versões: o aleatório também é um navegador real
                self._primp = primp.Client(impersonate="random", follow_redirects=True, timeout=tempo_limite, proxy=self.proxy)
        r = self._primp.get(url)
        return Resposta(str(r.url), r.status_code, r.content, (r.headers or {}).get("content-type", ""))

    def buscar(self, url: str, tempo_limite: float) -> Resposta:
        try:
            r = self.sessao.get(url, timeout=tempo_limite, allow_redirects=True)
            resp = Resposta(str(r.url), r.status_code, r.content, r.headers.get("content-type", ""))
        except self._cr.exceptions.RequestException as e:
            raise Passageiro(f"curl_cffi: {e}") from e
        from .escada import avaliar
        try:
            avaliar(resp)
            return resp
        except Bloqueado:
            try:
                outra = self._por_primp(url, tempo_limite)
            except Exception as e:  # noqa: BLE001 — a segunda assinatura falhou por rede: é passageiro
                raise Passageiro(f"primp: {e}") from e
            outra.alertas.append("curl_cffi barrado; passou com a assinatura do primp")
            return outra
