"""02/10 (titular): esteira metódica de selos (bronze → prata → ouro), Interceptador local, maestro e guarda de dados."""
import json, sys, tempfile, unittest
from datetime import date
from pathlib import Path
from unittest import mock
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import esteira as E

CFG = json.loads((ROOT / "config/esteira.json").read_text(encoding="utf-8"))
DOZE = CFG["doze_dados"]


def livro(pagina, completos=True, prazo=True, lid="op-teste"):
    ck = {i: {"v": "valor"} for i in (DOZE if completos else DOZE[:3])}
    h = [{"pagina_oficial": pagina, "fim": "2026-11-30"}] if prazo else [{"pagina_oficial": pagina}]
    return {"id": lid, "programa": "Edital Goyazes de cultura", "pagina": pagina, "historico": h, "livro": {"checklist": ck}}


class TesteSelos(unittest.TestCase):
    def test_bronze_prata_ouro(self):
        self.assertEqual(E.avaliar(livro("https://cultura.go.gov.br/edital"), CFG)["nivel"], "ouro")
        self.assertEqual(E.avaliar(livro("https://cultura.go.gov.br/edital", completos=False), CFG)["nivel"], "prata")
        self.assertEqual(E.avaliar(livro("https://instituto-qualquer.org/edital"), CFG)["nivel"], "bronze")
        self.assertEqual(E.avaliar(livro("https://observatorio3setor.org.br/noticia/x"), CFG)["nivel"], "bronze")

    def test_estantes_tentativas_e_reabertura(self):
        x = livro("https://instituto-qualquer.org/edital")
        E.atualizar_livro(x, CFG, "2026-10-02"); self.assertEqual(x["esteira"]["estante"], "fila_bronze")
        x["esteira"]["tentativas_bronze"] = 2
        E.atualizar_livro(x, CFG, "2026-10-02"); self.assertEqual(x["esteira"]["estante"], "investigacao_bronze")
        x["historico"].append({"pagina_oficial": "https://instituto-qualquer.org/novo", "fim": "2026-12-01"})   # informação nova
        E.atualizar_livro(x, CFG, "2026-10-03"); self.assertEqual(x["esteira"]["estante"], "fila_bronze")
        self.assertEqual(x["esteira"]["tentativas_bronze"], 0)

    def test_resultados_do_computador_do_titular(self):
        with tempfile.TemporaryDirectory() as tmp:
            R, A = Path(tmp) / "r.jsonl", Path(tmp) / "a.json"
            x = livro("https://instituto-qualquer.org/edital", completos=False, lid="op-a")
            C = {"motores": [x]}
            R.write_text("\n".join(json.dumps(l) for l in [
                {"livro": "op-a", "etapa": "bronze", "site_oficial": "https://instituto.org.br/edital", "confirmado_localmente": True,
                 "modelo": "claude-sonnet-5-5", "aprendizado": "o edital fica em /editais"},
                {"livro": "op-a", "etapa": "prata", "modelo": "claude-opus-5-5", "edital_validado": True, "prazo_inscricao_fim": "2026-11-30",
                 "doze": {i: "ok" for i in DOZE[3:9]}, "dispensas": {i: "não se aplica" for i in DOZE[9:]}, "aprendizado": "exige CNPJ de 2 anos"}]), encoding="utf-8")
            with mock.patch.object(E, "RESULTADOS", R), mock.patch.object(E, "APLICADOS", A):
                r = E.aplicar_resultados(C, CFG, "2026-10-02")
            E.atualizar_livro(x, CFG, "2026-10-02")
        self.assertEqual(r["bronze_confirmados"], 1); self.assertEqual(r["prata_validados"], 1)
        self.assertEqual(x["esteira"]["selo"], "ouro"); self.assertEqual(x["esteira"]["estante"], "farol")
        self.assertEqual(len(x["esteira"]["aprendizado"]), 2)
        self.assertIn("claude-sonnet-5-5", x["esteira"]["site_confirmado_por"])


class TesteInterceptadorLocal(unittest.TestCase):
    def _imp(self):
        import importlib.util
        sp = importlib.util.spec_from_file_location("il", ROOT / "scripts/interceptador_local.py"); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        return m

    def test_bronze_confere_no_ip_do_titular(self):
        L = self._imp()
        it = {"livro": "op-a", "programa": "Edital Goyazes de cultura", "candidatos": ["https://noticia.com.br/x"], "termos": ["goyazes"]}
        resp = '{"site_oficial": "https://cultura.go.gov.br", "url_edital": "https://cultura.go.gov.br/goyazes", "aprendizado": "ok"}'
        for pagina, esperado in (({"status": 200, "texto": "Programa Goyazes inscrições"}, True), ({"status": 404, "texto": ""}, False),
                                 ({"status": 200, "texto": "página sem relação"}, False)):
            with mock.patch.object(L, "ler", return_value=pagina), mock.patch("src.ia.chamar", return_value=resp), mock.patch("src.ia.credencial", return_value="x"):
                self.assertEqual(L.bronze(it)["confirmado_localmente"], esperado, pagina)

    def test_prata_o_codigo_valida(self):
        L = self._imp()
        it = {"livro": "op-a", "programa": "X", "url_edital": "https://cultura.go.gov.br/e", "doze_faltando": ["Valor", "Resultado"]}
        with mock.patch.object(L, "ler", return_value={"status": 200, "texto": "edital ...", "pdfs": []}):
            with mock.patch("src.ia.chamar", return_value='{"prazo_inscricao_fim": "2026-11-30", "doze": {"Valor": "R$ 10 mil"}, "dispensas": {"Resultado": "contínuo"}}'):
                self.assertTrue(L.prata(it, CFG)["edital_validado"])
            with mock.patch("src.ia.chamar", return_value='{"prazo_inscricao_fim": null, "doze": {"Valor": "R$ 10 mil"}}'):
                self.assertFalse(L.prata(it, CFG)["edital_validado"])   # sem prazo e item faltando: o modelo não valida sozinho

    def test_esforco_baixo_e_modelos(self):
        from src import ia
        self.assertEqual((ia.modelo_para("esteira_bronze"), ia.esforco_para("esteira_bronze")), ("claude-sonnet-5-5", "low"))
        self.assertEqual((ia.modelo_para("esteira_prata"), ia.esforco_para("esteira_prata")), ("claude-opus-5-5", "low"))


class TesteMaestroEGuarda(unittest.TestCase):
    def test_cobertura(self):
        from src.maestro import cobertura
        self.assertEqual(cobertura("x", {"cor": "verde", "falhas": 0}, {}), "completa")
        self.assertEqual(cobertura("x", {"cor": "azul", "falhas": 2}, {}), "parcial")
        self.assertEqual(cobertura("x", None, {"motivo": "exige IP Brasil"}), "pendente_local")

    def test_tentativa_so_conta_quando_o_motor_leu(self):
        src = (ROOT / "src/maestro.py").read_text(encoding="utf-8")
        self.assertIn('parciais = {p["motor"] for p in plano if p["cobertura"] == "parcial"}', src)

    def test_guarda_contra_dados_de_teste(self):
        from src.guarda_dados_teste import e_teste, limpar_catalogo
        self.assertTrue(e_teste("https://x.gov.br/edital")); self.assertFalse(e_teste("https://goias.gov.br/x"))
        C = {"motores": [{"id": "a", "pagina": "https://x.gov.br/edital", "historico": [{"pagina_oficial": "https://x.gov.br/edital"}]},
                         {"id": "b", "pagina": "https://goias.gov.br/b", "historico": [{"pagina_oficial": "https://x.gov.br/edital"}, {"pagina_oficial": "https://goias.gov.br/b"}]}]}
        r = limpar_catalogo(C)
        self.assertEqual([x["id"] for x in C["motores"]], ["b"]); self.assertEqual(len(C["motores"][0]["historico"]), 1); self.assertEqual(r["livros_falsos"], 1)

    def test_producao_roda_testes_isolada(self):
        y = (ROOT / ".github/workflows/monitoramento-diario.yml").read_text(encoding="utf-8")
        self.assertIn("git worktree add --detach /tmp/eldorado_testes", y)


if __name__ == "__main__":
    unittest.main()
