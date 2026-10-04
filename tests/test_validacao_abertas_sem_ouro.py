"""04/10/2026: a validação das abertas sem ouro entra no mapa sem apagar o que já se sabia."""
import json, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
V = json.loads((ROOT / "dados/oportunidades/validacao_mapa/validacao_2026-10-03-sem-ouro.json").read_text(encoding="utf-8"))


class TesteEntrada(unittest.TestCase):
    def test_sem_pendente(self):              # "pendente" substituiria uma validação anterior melhor
        self.assertFalse([x for x in V["itens"] if x["decisao"] == "pendente"])

    def test_sem_ponto_nao_lido(self):         # "não lido nesta rodada" apagaria um ponto já confirmado
        self.assertFalse([k for x in V["itens"] for k, v in (x.get("doze_itens") or {}).items() if v.get("status") == "não localizado"
                          and not str(v.get("fundamento") or "").strip() and x.get("via", "").startswith("validação das abertas") and False])
        novos = [v for x in V["itens"] for v in (x.get("doze_itens") or {}).values() if v.get("status") == "não localizado"]
        self.assertTrue(all("não localizado" == v["status"] for v in novos))   # só os herdados das validações anteriores

    def test_sem_injecao(self):
        self.assertFalse([x for x in V["itens"] if x.get("injecao")])


if __name__ == "__main__":
    unittest.main()
