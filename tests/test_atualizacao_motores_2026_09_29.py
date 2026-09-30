"""Atualização dos motores de 29/09/2026: Querido Diário novo, nova tentativa, Comunica PJe como pista, PNCP com
espera crescente, SAPL como certificado inválido (sem desligar verificação), wa.me fora da coleta."""
import json, sys, unittest
from pathlib import Path
from unittest import mock
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class _Resp:
    def __init__(self, corpo): self.corpo = corpo.encode()
    def read(self, n=-1): return self.corpo
    def __enter__(self): return self
    def __exit__(self, *a): return False


class TesteAtualizacao(unittest.TestCase):
    def test_querido_diario_endereco_novo_primeiro(self):
        C = json.loads((ROOT / "config/coletores_api.json").read_text(encoding="utf-8"))
        self.assertEqual(C["querido_diario"]["bases"][0], "https://api.queridodiario.org.br")
        self.assertEqual(C["pncp"]["esperas_s"], [5, 15, 45])

    def test_nova_tentativa_quando_nao_vem_json(self):
        from src import coletores_api as c
        respostas = [_Resp("no available server"), _Resp('{"gazettes": []}')]
        with mock.patch.object(c, "urlopen", side_effect=lambda *a, **k: respostas.pop(0)), \
             mock.patch.object(c, "validate_public_https", lambda u: None), mock.patch("time.sleep", lambda s: None):
            self.assertEqual(c._get_json_resiliente("https://api.queridodiario.org.br/gazettes", 3, [3, 5]), {"gazettes": []})

    def test_comunica_pje_entra_como_pista(self):
        from src import coletores_api as c
        corpo = json.dumps({"items": [{"id": 1, "nomeOrgao": "1ª Vara Criminal de Goiânia", "data_disponibilizacao": "2026-09-25", "texto": "prestação pecuniária"}]})
        with mock.patch.object(c, "_get_json_resiliente", lambda *a, **k: json.loads(corpo)):
            from datetime import date
            ach, fal = c.coletar_comunica_pje(date(2026, 9, 21), date(2026, 9, 28), {"base": "https://comunicaapi.pje.jus.br/api/v1/comunicacao",
                                               "tribunais": ["TJGO"], "termos": ["prestação pecuniária"], "max_paginas": 1, "itens_por_pagina": 100})
        self.assertEqual(ach[0]["status"], "pista"); self.assertTrue(ach[0]["confirmar_url_oficial"])
        src = (ROOT / "src/fluxo_oportunidades.py").read_text(encoding="utf-8")
        self.assertIn('m.get("status") == "pista" and m.get("confirmar_url_oficial")', src)

    def test_sapl_nao_e_bloqueio_de_ip_e_verificacao_continua(self):
        A = json.loads((ROOT / "config/alternativas_acesso.json").read_text(encoding="utf-8"))
        self.assertEqual(A["situacao_dos_dominios"]["sapl.goiania.go.leg.br"]["situacao"], "certificado_invalido_no_portal")
        for arq in ("src/coletores_api.py", "src/sensores.py", "src/nucleo.py"):
            t = (ROOT / arq).read_text(encoding="utf-8")
            self.assertNotIn("CERT_NONE", t); self.assertNotIn("_create_unverified_context", t)

    def test_whatsapp_fora_da_coleta(self):
        from src.alternativas import url_coletavel
        self.assertFalse(url_coletavel("https://wa.me/5562999999999")); self.assertTrue(url_coletavel("https://www.tjgo.jus.br/"))


if __name__ == "__main__":
    unittest.main()
