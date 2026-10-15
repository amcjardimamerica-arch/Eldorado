"""15/10/2026: com a ponte Brasil configurada, os portais 'exige_brasil' (SPL da ALEGO, MPGO) são lidos pela ponte."""
import os
import unittest
from unittest import mock

from src import ponte_brasil as PB
from src import sensores as S


class SensoresPelaPonte(unittest.TestCase):
    URL = "https://alegodigital.al.go.leg.br/spl/consulta-cronologico.aspx"

    def _ambiente(self, ponte: bool):
        return mock.patch.dict(os.environ, {"GITHUB_ACTIONS": "true", **({"ELDORADO_PONTE_URL": "https://p", "ELDORADO_PONTE_CHAVE": "k"} if ponte else {})}, clear=False)

    def test_com_ponte_nao_pula_e_le_pela_ponte(self):
        os.environ.pop("ELDORADO_LOCAL_BR", None)
        with self._ambiente(True), mock.patch.object(PB, "configurada", lambda: True), \
             mock.patch.object(S, "validate_public_https", lambda *a, **k: None), \
             mock.patch.object(PB, "abrir", lambda url, **k: (200, url, "<html>SPL ok</html>".encode(), {})):
            self.assertFalse(S._na_nuvem_sem_brasil())
            self.assertTrue(S._pela_ponte(self.URL))
            self.assertFalse(S._pela_ponte("https://portal.al.go.leg.br/noticias"))      # fora da lista: direto
            self.assertIn("SPL ok", S._abrir(self.URL)[0])

    def test_sem_ponte_continua_pulando(self):
        os.environ.pop("ELDORADO_LOCAL_BR", None)
        with self._ambiente(False), mock.patch.object(PB, "configurada", lambda: False):
            self.assertTrue(S._na_nuvem_sem_brasil())
            self.assertFalse(S._pela_ponte(self.URL))


if __name__ == "__main__":
    unittest.main()


class RobotsPelaPonte(unittest.TestCase):
    """15/10/2026: o SPL da ALEGO proíbe as consultas no robots.txt (lido pela ponte) — o motor obedece."""
    def test_robots_lido_pela_ponte_e_obedecido(self):
        from src.indexadores import ponte
        S._ROBOTS_PONTE.clear()
        robots = b"User-agent: *\nDisallow: /spl/consulta\n"
        with mock.patch.object(ponte, "buscar", lambda *a, **k: (200, "u", robots, {})):
            self.assertFalse(S._robots_pela_ponte("https://alegodigital.al.go.leg.br/spl/consulta-tipo.aspx"))
            self.assertTrue(S._robots_pela_ponte("https://alegodigital.al.go.leg.br/spl/sessoes.aspx"))

    def test_falha_da_ponte_nao_le(self):
        from src.indexadores import ponte
        S._ROBOTS_PONTE.clear()

        def falha(*a, **k):
            raise OSError("ponte fora")
        with mock.patch.object(ponte, "buscar", falha):
            self.assertFalse(S._robots_pela_ponte("https://alegodigital.al.go.leg.br/spl/x"))


class RegistrarDiaComForcaVazia(unittest.TestCase):
    """15/10/2026 (auditoria da esteira): achado com forca_lexica None derrubava a passagem inteira dos motores."""
    def test_forca_lexica_none_nao_derruba(self):
        import tempfile
        from datetime import date
        from pathlib import Path
        d = Path(tempfile.mkdtemp())
        with mock.patch.object(S, "ROOT", d, create=True):
            try:
                S.registrar_dia("teste", date(2026, 10, 15), {"achados": [{"forca_lexica": None}, {"forca_lexica": None, "titulo": "x"}], "falhas": []})
            except TypeError as e:
                self.fail(f"TypeError: {e}")
            except Exception:
                pass                                     # gravação em disco não é o alvo deste teste
