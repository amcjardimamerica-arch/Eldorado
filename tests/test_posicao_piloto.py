"""O anunciador da posição do Piloto (24/09)."""
import os, time, unittest
import src.posicao_piloto as P


class TestePosicaoAoVivo(unittest.TestCase):
    def setUp(self):
        P._estado.update({"t": 0.0, "lugar": None, "sha": None, "log": []})
        self._env = {k: os.environ.pop(k, None) for k in ("GH_TOKEN", "GITHUB_TOKEN", "GITHUB_REPOSITORY")}

    def tearDown(self):
        for k, v in self._env.items():
            if v is not None:
                os.environ[k] = v

    def test_fora_do_actions_falha_em_silencio(self):
        """Anunciar posição é conveniência; voar é a finalidade. Nunca derruba o voo."""
        r = P.anunciar({"tipo": "afiar_motor", "motor": "motor-gife"})
        self.assertFalse(r["anunciado"])
        self.assertEqual(r["log"][0]["http"], 0)

    def test_mesmo_lugar_nao_reanuncia_antes_de_4_min(self):
        P._estado.update({"lugar": "afiar_motor|motor-gife|None", "t": time.time()})
        r = P.anunciar({"tipo": "afiar_motor", "motor": "motor-gife"})
        self.assertFalse(r["anunciado"]); self.assertIn("mesmo lugar", r["porque"])

    def test_intervalo_minimo_entre_anuncios(self):
        P._estado.update({"lugar": "outro", "t": time.time()})
        r = P.anunciar({"tipo": "afiar_motor", "motor": "motor-gife"})
        self.assertFalse(r["anunciado"]); self.assertIn(f"{P.INTERVALO_MIN_S}s", r["porque"])

    def test_reanuncia_o_mesmo_lugar_passados_4_min(self):
        """Sem isto, uma missão longa venceria no painel (8 min) e o avião sumiria com ele
        trabalhando."""
        P._estado.update({"lugar": "afiar_motor|motor-gife|None", "t": time.time() - P.REANUNCIO_S - 1})
        r = P.anunciar({"tipo": "afiar_motor", "motor": "motor-gife"})
        self.assertNotIn("porque", r)                          # tentou gravar (sem token, falha)
        self.assertLess(P.REANUNCIO_S, P.VALIDADE_S)

    def test_o_ramo_e_o_arquivo_sao_os_que_o_painel_le(self):
        self.assertEqual(P.RAMO, "piloto-ao-vivo")
        self.assertEqual(P.ARQUIVO, "docs/dados/piloto_posicao.json")

    def test_o_ciclo_anuncia_no_inicio_de_cada_missao_e_pousa_no_fim(self):
        import pathlib
        src = (pathlib.Path(__file__).resolve().parents[1] / "src/piloto.py").read_text(encoding="utf-8")
        self.assertIn("_anunciar(m, voo=rel.get(\"voo_do_dia\"), de=len(plano))", src)
        self.assertIn("_pousar_pos(", src)
        self.assertIn('rel["posicao_ao_vivo"] = _reg_pos()', src)

    def test_o_workflow_entrega_o_token_ao_ciclo(self):
        import pathlib
        w = (pathlib.Path(__file__).resolve().parents[1] / ".github/workflows/piloto.yml").read_text(encoding="utf-8")
        self.assertIn("GH_TOKEN: ${{ github.token }}   # posição ao vivo no ramo piloto-ao-vivo", w)
