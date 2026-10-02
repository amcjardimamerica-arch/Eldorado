"""02/10 (titular): chave de acionamento dos livros, índice dos motores e léxico temporário de 30 dias; Prosas reunido."""
import json, sys, tempfile, unittest
from datetime import date
from pathlib import Path
from unittest import mock
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import chaves_livros as K


class TesteChaves(unittest.TestCase):
    def test_termos_pelos_nomes_proprios(self):
        self.assertEqual(K.termos_da_chave({"nome_classificado": "Mapfre abre seleção de projetos incentivados com foco — Brasil"}), ["mapfre"])
        self.assertIn("dia de doar", K.termos_da_chave({"nome_classificado": "Dia de Doar abre inscrições para edital — Brasil"}))
        self.assertIn("pnab", K.termos_da_chave({"nome_classificado": "PNAB Goiás - Audiovisual — Goiás"}))
        self.assertNotIn("observatorio", " ".join(K.termos_da_chave({"nome_classificado": "Zurich abre edital", "orgao": "Observatório do Terceiro Setor — editais"})))

    def test_lexico_temporario_na_janela_e_limite(self):
        with tempfile.TemporaryDirectory() as tmp:
            L = Path(tmp) / "l.json"
            L.write_text(json.dumps({"itens": [{"livro": "a", "termos": ["goyazes"], "motores": ["do-goias"], "desde": "2026-10-01", "ate": "2026-11-30"},
                                               {"livro": "b", "termos": ["mapfre"], "motores": [], "desde": "2026-12-01", "ate": "2027-01-10"}]}), encoding="utf-8")
            with mock.patch.object(K, "LEXICO", L):
                self.assertEqual(K.termos_temporarios("do-goias", date(2026, 10, 2)), ["goyazes"])
                self.assertEqual(K.termos_temporarios("dou", date(2026, 10, 2)), [], "fora do índice e sem livro geral vigente")
                self.assertEqual(K.termos_temporarios("dou", date(2026, 12, 5)), ["mapfre"], "livro sem índice vale para todos na janela")
        self.assertIn("termos_temporarios(sensor.get(\"id\"))", (ROOT / "src/sensores.py").read_text(encoding="utf-8"))

    def test_prosas_reunido_e_pausado(self):
        I = {f["id"]: f for f in json.loads((ROOT / "config/investigacao.json").read_text(encoding="utf-8"))["fontes"]}
        for k in ("prosas", "prosas-premios"):
            self.assertFalse(I[k]["ativa"]); self.assertEqual(I[k]["agregado_a"], "prosas-oscs")
        self.assertFalse(I["prosas-oscs"]["ativa"]); self.assertIn("robots.txt", I["prosas-oscs"]["motivo_inativa"])
        from src.sensores import registro
        self.assertFalse([s for s in registro() if "prosas" in s["id"]])


if __name__ == "__main__":
    unittest.main()
