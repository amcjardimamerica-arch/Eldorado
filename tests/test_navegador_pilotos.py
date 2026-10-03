"""03/10/2026: navegador do titular para os Pilotos (busca e leitura com JavaScript), 2 buscas por voo na nuvem."""
import os, sys, unittest
from pathlib import Path
from unittest import mock
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TesteNavegador(unittest.TestCase):
    def test_so_no_computador_do_titular(self):
        from src import navegador_local as N
        with mock.patch.dict(os.environ, {"ELDORADO_LOCAL_BR": ""}):
            self.assertFalse(N.disponivel())                       # na nuvem, nunca

    def test_resultados(self):
        from src import navegador_local as N
        self.assertEqual(N.resultados_bing('<li class="b_algo"><h2><a href="https://a.gov.br/e">Edital</a></h2></li>')[0]["url"], "https://a.gov.br/e")
        self.assertEqual(N.resultados_ddg('<a class="result__a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fb.org.br%2Fx">X</a>')[0]["url"], "https://b.org.br/x")
        self.assertTrue(N.VERIFICACAO.search("Our systems have detected unusual traffic"))

    def test_busca_usa_o_navegador_primeiro_e_cai_nas_vias_de_sempre(self):
        from src import piloto_busca as PB, navegador_local as N
        with mock.patch.object(N, "disponivel", return_value=True), mock.patch.object(N, "buscar", return_value=[{"url": "https://x.gov.br", "titulo": "t"}]):
            self.assertEqual(PB._buscar_sem_cache("edital osc")[0]["url"], "https://x.gov.br")
        with mock.patch.object(N, "disponivel", return_value=True), mock.patch.object(N, "buscar", side_effect=RuntimeError("falhou")), \
             mock.patch.object(PB, "_vias_de_reserva", return_value=[]):
            PB._buscar_sem_cache("edital osc")                      # não quebra: segue pelas vias de sempre

    def test_leitura_curta_vai_ao_navegador(self):
        from src import piloto_busca as PB, navegador_local as N
        with mock.patch("urllib.request.urlopen", side_effect=OSError("recusou")), mock.patch.object(N, "disponivel", return_value=True), \
             mock.patch.object(N, "ler", return_value="Edital completo " * 50):
            self.assertIn("Edital completo", PB.ler_pagina("https://x.gov.br/e"))

    def test_duas_buscas_por_voo_na_nuvem(self):
        s = (ROOT / "src/piloto_busca.py").read_text(encoding="utf-8")
        self.assertIn('max_consultas = min(max_consultas, int(os.environ.get("ELDORADO_BUSCAS_NA_NUVEM", "2")))', s)
        self.assertIn("_garantir_navegador()", (ROOT / "scripts/pilotos_brasil.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
