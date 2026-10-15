"""15/10/2026: robots.txt pela RFC 9309 — 4xx permite, 5xx bloqueia, 200 obedece, sem Python-urllib."""
import io
import unittest
from unittest import mock
from urllib.error import HTTPError

from src import executor_skills as X


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _abrir(resposta):
    class Op:
        def open(self, req, timeout=None):
            assert "EldoradoBot" in req.get_header("User-agent")
            if isinstance(resposta, Exception):
                raise resposta
            return _Resp(resposta.encode())
    return lambda *a, **k: Op()


class RobotsRFC(unittest.TestCase):
    def setUp(self):
        X._robots.clear(); X.robots_motivos.clear()

    def _com(self, resposta):
        return mock.patch.object(X, "build_opener", _abrir(resposta))

    def test_403_no_robots_permite(self):
        with self._com(HTTPError("u", 403, "Forbidden", {}, None)):
            self.assertTrue(X.permitido("https://data.exemplo.org/a/b.pdf"))
        self.assertIn("403", X.robots_motivos["https://data.exemplo.org"])

    def test_404_permite(self):
        with self._com(HTTPError("u", 404, "Not found", {}, None)):
            self.assertTrue(X.permitido("https://x.gov.br/edital.pdf"))

    def test_500_bloqueia(self):
        with self._com(HTTPError("u", 503, "Unavailable", {}, None)):
            self.assertFalse(X.permitido("https://y.gov.br/edital.pdf"))

    def test_200_obedece(self):
        with self._com("User-agent: *\nDisallow: /privado/\n"):
            self.assertFalse(X.permitido("https://z.gov.br/privado/a.pdf"))
            self.assertTrue(X.permitido("https://z.gov.br/editais/a.pdf"))

    def test_pagina_html_no_lugar_do_robots_permite(self):
        with self._com("<html><body>Acesso</body></html>"):
            self.assertTrue(X.permitido("https://w.gov.br/a.pdf"))


if __name__ == "__main__":
    unittest.main()
