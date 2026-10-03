"""03/10/2026: estudo dos motores 01–39 — leitor de datas, semente dos livros 24–39 e fila do Interceptador. Sem rede."""
import json, sys, tempfile, unittest
from datetime import date
from pathlib import Path
from unittest import mock
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TesteLeitorDeDatas(unittest.TestCase):
    def test_sem_ano_vale_o_ano_da_publicacao(self):
        from src.indexadores.extracao import prazo
        H = date(2026, 10, 3)
        self.assertEqual(prazo("Inscrições até 19 de outubro", H, "2026-09-20"), "2026-10-19")   # nunca 2027
        self.assertEqual(prazo("Inscrições até 2 de setembro", H, "2026-08-01"), "2026-09-02")    # encerrado, não 2027
        self.assertEqual(prazo("Inscrições até 15 de janeiro", H, "2025-12-10"), "2026-01-15")   # virada do ano
        self.assertEqual(prazo("Inscrições até 02/09", H), "2026-09-02")
        self.assertEqual(prazo("Inscrições de 5 a 19 de outubro", H, "2026-09-30"), "2026-10-19")  # de X a Y → Y
        self.assertEqual(prazo("Inscrições até 19 de outubro de 2025", H, "2026-09-20"), "2025-10-19")

    def test_corrige_so_os_motores_do_texto(self):
        from src.indexadores import motor as IM
        A = {"itens": {"a": {"fonte": "abcr", "prazo": "2027-09-02", "publicado": "2026-08-01"},
                       "b": {"fonte": "farolcultural", "prazo": "2027-09-02", "publicado": "2026-08-01"},
                       "c": {"fonte": "abcr", "prazo": "2027-03-10", "publicado": "2026-11-20"}}}
        cat = {"sites": [{"id": "abcr", "motor": "site-abcr"}, {"id": "farolcultural", "motor": "site-farol-cultural"}]}
        with mock.patch.object(IM, "_j", lambda p, d: A if str(p).endswith("indicios.json") else d), mock.patch.object(IM, "catalogo", lambda: cat):
            self.assertEqual(IM.corrigir_prazos_do_ano_seguinte(gravar=False), 1)
        self.assertEqual(A["itens"]["a"]["prazo"], "2026-09-02")          # ABCR: o texto dizia "2 de setembro"
        self.assertEqual(A["itens"]["b"]["prazo"], "2027-09-02")          # Farol: data da fonte, não muda
        self.assertEqual(A["itens"]["c"]["prazo"], "2027-03-10")          # 10/03/2026 cairia antes da publicação


class TesteSemente(unittest.TestCase):
    def test_uma_vez_encerrados_na_estante_e_aguardar_fonte_na_fila(self):
        import src.livros_regra as LR
        sem = {"versao": "teste-1", "itens": [
            {"acao": "criar_livro", "estado": "encerrado_arquivar", "aplicavel": "sim", "titulo": "Edital Cultura Viva de Teste 2024",
             "orgao": "Secretaria de Teste", "url": "https://cultura.teste.gov.br/edital-2024", "prazo": "2024-05-30", "publicado_em": "2024-04-01", "uf": "GO", "motor": "site-farol-cultural"},
            {"acao": "aguardar_fonte", "estado": "aberto", "titulo": "Chamada aberta sem site", "pagina_agregador": "https://agregador.org/chamada-x"}]}
        with tempfile.TemporaryDirectory() as t:
            t = Path(t); (t / "s.json").write_text(json.dumps(sem), encoding="utf-8")
            with mock.patch.object(LR, "SEMENTE_2439", t / "s.json"), mock.patch.object(LR, "FILA_2439", t / "f.json"):
                C = {"motores": []}
                r = LR._aplicar_semente_24_39(C)
                self.assertEqual(r["fila_interceptador"], 1)
                n = len(C["motores"]); C["semente_24_39"] = r
                self.assertIs(LR._aplicar_semente_24_39(C), r); self.assertEqual(len(C["motores"]), n)        # uma vez só
                fila = json.loads((t / "f.json").read_text(encoding="utf-8"))["itens"]
        self.assertFalse([x for x in C["motores"] if "Chamada aberta sem site" in str(x)])                    # aguardar_fonte não vira livro
        self.assertEqual(fila[0]["pagina_agregador"], "https://agregador.org/chamada-x")
        x = next(x for x in C["motores"] if x.get("estado_semente") == "encerrado_arquivar")
        fins = [h.get("fim") for h in x.get("historico") or [] if isinstance(h, dict) and h.get("fim")]
        self.assertTrue(fins and max(fins) < date.today().isoformat())                                         # prazo vencido → "Na Estante"

    def test_interceptador_tem_o_nivel_da_semente(self):
        self.assertIn("6 · semente 24–39", (ROOT / "src/interceptador.py").read_text(encoding="utf-8"))
        self.assertIn('C["semente_24_39"] = _aplicar_semente_24_39(C)', (ROOT / "src/livros_regra.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
