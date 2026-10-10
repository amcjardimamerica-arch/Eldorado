"""10/10 (titular): no calendário de cada motor, o dia com oportunidade mostra a QUANTIDADE de editais encontrados
no lugar do nome do edital (o nome continua no balão)."""
import unittest
from pathlib import Path
H = (Path(__file__).resolve().parents[1] / "docs/dashboard.html").read_text(encoding="utf-8")


class TesteCalendarioMotor(unittest.TestCase):
    def test_quantidade_no_lugar_do_nome(self):
        self.assertIn('${q} ${q===1?"edital":"editais"}', H)
        self.assertNotIn('${esc(x.t.slice(0,26))}…', H, "o nome do edital não aparece mais no dia")


if __name__ == "__main__":
    unittest.main()
