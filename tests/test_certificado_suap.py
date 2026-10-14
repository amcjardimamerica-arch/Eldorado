"""03/10/2026: o SUAP é lido DIRETO da nuvem com a cadeia que ele não envia; a ponte fica de reserva."""
import ssl, sys, unittest
from pathlib import Path
from unittest import mock
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TesteCertificadoSuap(unittest.TestCase):
    def test_cadeia_carregada_com_verificacao_ligada(self):
        from src.certificados import contexto
        c = contexto()
        self.assertEqual(c.verify_mode, ssl.CERT_REQUIRED); self.assertTrue(c.check_hostname)
        nomes = " ".join(str(x.get("subject")) for x in c.get_ca_certs())
        self.assertIn("YR2", nomes); self.assertIn("Root YR", nomes)

    def test_direto_primeiro_e_ponte_de_reserva(self):
        import src.camara_goiania as CG
        from src import ponte_brasil
        # 14/10: a conferência do endereço resolve o nome na internet — simulada, para o teste não depender da rede
        _v = mock.patch.object(CG, "validate_public_https", return_value=None); _v.start(); self.addCleanup(_v.stop)
        with mock.patch.object(CG, "_direto", return_value="ok direto"), mock.patch.object(ponte_brasil, "texto") as pt, \
             mock.patch.object(ponte_brasil, "usar", return_value=True):
            self.assertEqual(CG._get_texto("https://suap.camaragyn.go.gov.br/"), "ok direto"); pt.assert_not_called()
        with mock.patch.object(CG, "_direto", side_effect=RuntimeError("recusado")), mock.patch.object(ponte_brasil, "texto", return_value="pela ponte"), \
             mock.patch.object(ponte_brasil, "usar", return_value=True):
            self.assertEqual(CG._get_texto("https://suap.camaragyn.go.gov.br/"), "pela ponte")


if __name__ == "__main__":
    unittest.main()
