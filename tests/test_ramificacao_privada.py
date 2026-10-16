"""11/10/2026 (titular): ramificação privada — só chamamento/edital de empresa vira oportunidade e livro; empresa
cadastrada, doação ou patrocínio já realizado não é oportunidade; o banco de empresas cresce com os chamamentos e o
Espião; as saídas do Espião não se perdem."""
import json, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import repositorio_unico as R


class TesteChamamento(unittest.TestCase):
    def test_realizada_sem_chamamento_e_dispensa(self):
        t = "ArcelorMittal transforma uniformes usados em 360 cobertores para instituições"
        self.assertTrue(R.REALIZADA.search(t)); self.assertFalse(R.CHAMAMENTO.search(t))
        for t in ("Concurso Talentos contemporâneos 16ª edição", "Art Explora Residency programme 2027", "MECENAS DO CEARÁ 2026",
                  "Instituto X abre edital de patrocínio", "Credenciamento de artistas locais", "Fundação Y: inscrições abertas"):
            self.assertTrue(R.CHAMAMENTO.search(t), t)
        self.assertTrue(R._privada({"origem": "motor agregadores · capitaai"})); self.assertTrue(R._privada({"origem": "Piloto - Espião"}))
        self.assertFalse(R._privada({"origem": "motor pncp-api"}))


class TesteSaidasDoEspiao(unittest.TestCase):
    def test_catalogo_preserva_e_voo_guarda(self):
        c = (ROOT / "src/catalogo_terceiro_setor.py").read_text(encoding="utf-8")
        self.assertIn('c.get("origem") != "catálogo do Piloto - Espião"', c)
        w = (ROOT / ".github/workflows/piloto.yml").read_text(encoding="utf-8")
        linha = next(l for l in w.splitlines() if l.strip().startswith("for P in config/parametros_pilotos_fixos.json") and "espiao_empresas" in l)
        self.assertIn("biblioteca_alexandria/livros/especiais/empresas/dados/go/espiao_empresas.json", linha, "o arquivo de empresas entra na cópia de segurança do voo")

    def test_banco_de_empresas_e_livro(self):
        p = (ROOT / "src/patrocinios.py").read_text(encoding="utf-8")
        self.assertIn('"tipo_fonte": "chamamento privado aberto"', p)
        o = (ROOT / "src/opressores_repositorio.py").read_text(encoding="utf-8")
        self.assertIn('str(x.get("proximo_passo") or "").startswith("dispensar")', o)


if __name__ == "__main__":
    unittest.main()
