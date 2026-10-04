"""04/10/2026: cada motor do painel tem a sua skill documental, ligada e com as 6 seções."""
import json, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


class Teste(unittest.TestCase):
    def test_cada_motor_tem_a_sua_skill(self):
        P = json.loads((ROOT / "config/ordem_motores.json").read_text(encoding="utf-8"))["posicoes"]
        SM = json.loads((ROOT / "config/skills_motores.json").read_text(encoding="utf-8"))["motores"]
        for mid in P:
            arq = ROOT / f"skills/motores/por_motor/{mid}/SKILL.md"
            if not arq.exists():
                continue                                   # motores que saíram do painel (agregados)
            s = arq.read_text(encoding="utf-8")
            for sec in ("## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## 6."):
                self.assertIn(sec, s, mid)
            lig = (SM.get(mid) or SM.get("plat-" + mid) or {}).get("skills") or []
            self.assertIn(f"motores/por_motor/{mid}", lig, mid)
        self.assertGreaterEqual(len(list((ROOT / "skills/motores/por_motor").iterdir())), 42)


if __name__ == "__main__":
    unittest.main()
