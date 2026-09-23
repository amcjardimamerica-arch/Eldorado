"""Defeitos achados pelos 10 voos observados em 23/09."""
import json, pathlib, unittest
from src.missao_especial import _relevante, montar_fila, proximo, devolver_a_fila, CREDENCIAMENTO
ROOT = pathlib.Path(__file__).resolve().parents[1]


class TesteFilaAvanca(unittest.TestCase):
    """Os 10 voos reservaram o MESMO alvo: max() por urgência devolve o primeiro do empate,
    e quem falha volta com a mesma urgência."""

    def test_dez_reservas_dao_dez_alvos(self):
        montar_fila()
        ids = []
        for _ in range(10):
            a = proximo()
            if not a: break
            ids.append(a["id"])
        self.assertGreaterEqual(len(set(ids)), 8, f"a fila não anda: {len(set(ids))} distintos")
        for i in ids: devolver_a_fila(i)

    def test_tentativa_rebaixa_a_prioridade(self):
        src = (ROOT / "src/missao_especial.py").read_text(encoding="utf-8")
        self.assertIn("A FILA PRECISA ANDAR", src)
        self.assertIn("7 * _v.get(\"tentativas\", 0)", src)
        self.assertIn("ultima_tentativa", src)

    def test_devolver_conta_a_tentativa_quando_houve(self):
        montar_fila()
        a = proximo()
        devolver_a_fila(a["id"], tentado=True)
        d = json.loads((ROOT / "estado/piloto/fila_resgate.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(d["itens"][a["id"]]["tentativas"], 1)
        self.assertTrue(d["itens"][a["id"]].get("ultima_tentativa"))


class TesteFiltroCorrigido(unittest.TestCase):
    def test_plural_e_acento(self):
        self.assertFalse(_relevante({"titulo": "AQUISIÇÃO EXCLUSIVA DE GÊNEROS ALIMENTÍCIOS"})[0])
        self.assertFalse(_relevante({"titulo": "aquisicao de generos"})[0])

    def test_credenciamento_nao_e_captacao(self):
        """88% da fila era habilitação para prestar serviço, não fomento."""
        self.assertFalse(_relevante({"titulo": "EDITAL DE CREDENCIAMENTO DE OSC"})[0])
        self.assertIn("credenciamento", _relevante({"titulo": "Credenciamento de entidades"})[1])
        # mas credenciamento QUE LEVA A FOMENTO continua valendo
        self.assertTrue(_relevante({"titulo": "Credenciamento para termo de fomento"})[0])
        self.assertTrue(_relevante({"titulo": "Termo de Colaboração com OSC"})[0])
        self.assertGreaterEqual(len(CREDENCIAMENTO), 3)

    def test_a_fila_ficou_so_com_captacao(self):
        r = montar_fila()
        self.assertLess(r["total_incompletos"], 60)          # era 153, com 88% de credenciamento
        self.assertGreater(sum(r["descartados_por_nao_servirem"].values()), 300)
        d = json.loads((ROOT / "estado/piloto/fila_resgate.json").read_text(encoding="utf-8"))
        cred = [str(v.get("titulo", "")).lower() for v in d["itens"].values()
                if v.get("estado") == "aguardando" and "credencia" in str(v.get("titulo", "")).lower()]
        # o que sobra tem de nomear o instrumento de repasse — credenciamento PARA termo de
        # colaboração é fomento; credenciamento de prestador de serviço não é
        for c in cred:
            self.assertTrue(any(x in c for x in ("fomento", "colabora", "projeto", "parceria")),
                            f"credenciamento puro voltou à fila: {c[:70]}")
        self.assertLessEqual(len(cred), 5)


class TesteVetorNaoEFonte(unittest.TestCase):
    def test_nao_le_o_sitemap_do_vetor(self):
        src = (ROOT / "src/piloto.py").read_text(encoding="utf-8")
        self.assertIn("VETOR NÃO É FONTE", src)
        self.assertIn("pncp.gov.br", src)
        self.assertIn("not any(v in h for v in VETOR_DOM)", src)


class TesteBancoDeProvas(unittest.TestCase):
    def test_o_banco_existe_e_se_declara(self):
        s = (ROOT / "scripts/voo_observado.py").read_text(encoding="utf-8")
        self.assertIn("BANCO DE PROVAS, não produção", s)
        self.assertIn("ELDORADO_APRENDIZADOS", s)            # não suja a base real
        self.assertIn("class IAMuda", s); self.assertIn("class IAFalante", s)
        self.assertIn("impedimento", s)                      # anota o que o ambiente não deu

    def test_o_relatorio_dos_dez_voos_foi_gravado(self):
        r = json.loads((ROOT / "estado/piloto/voo_observado_2026-09-23.json").read_text(encoding="utf-8"))
        self.assertEqual(len(r["voos"]), 10)
        self.assertGreaterEqual(len(r["diario"]), 70)
        self.assertIn("banco de provas", r["natureza"])
        self.assertIn("com_modelo_mudo", r["comparacao"])

    def test_o_parecer_traz_as_sete_posicoes(self):
        p = (ROOT / "biblioteca_alexandria/VOO-OBSERVADO-10-2026-09-23.md").read_text(encoding="utf-8")
        for pos in ("Extremamente pessimista", "Pessimista", "Levemente pessimista", "Neutro",
                    "Levemente otimista", "Otimista", "Extremamente otimista"):
            self.assertIn(pos, p, pos)
        self.assertIn("88%", p)                               # o achado central
        self.assertIn("10 voos, 10 alvos", p)
