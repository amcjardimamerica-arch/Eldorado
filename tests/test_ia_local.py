"""IA local (20/09): contrato das tarefas, validação por trecho literal e aplicação como proposta."""
import json, pathlib, unittest
from src.ia_local import IALocal, t_classificar_objeto, t_extrair_objeto_prazo, t_propor_lexico, t_diagnosticar_rota, t_catalogar_achado, ciclo, aplicar, CFG
ROOT = pathlib.Path(__file__).resolve().parents[1]


def falso(resposta: dict):
    """transporte simulado: devolve o que um modelo responderia."""
    return lambda payload: {"model": "simulado", "choices": [{"message": {"content": json.dumps(resposta, ensure_ascii=False)}}]}


TEXTO = ("EDITAL DE CHAMAMENTO PÚBLICO Nº 05/2026. DO OBJETO: seleção de organização da sociedade civil para termo de fomento "
         "na área de cultura. DAS INSCRIÇÕES: as propostas serão recebidas de 01/10/2026 até 30 de outubro de 2026.")


class TesteValidacaoPorTrecho(unittest.TestCase):
    def test_classificacao_so_vale_com_trecho_no_texto(self):
        """21/09: duas perguntas binárias (é fomento? há veto?) em vez de três classes."""
        ok = IALocal(transporte=falso({"e_fomento_a_osc": True, "trecho_fomento": "seleção de organização da sociedade civil para termo de fomento", "sinal_de_veto": None, "confianca": 0.9}))
        p = t_classificar_objeto(ok, {"id": "a", "titulo": "Edital 05/2026"}, TEXTO)
        self.assertTrue(p["valido"]); self.assertEqual(p["familia"], "fomento_osc"); self.assertTrue(p["perguntas"]["e_fomento_a_osc"])
        veto = IALocal(transporte=falso({"e_fomento_a_osc": False, "sinal_de_veto": "servico_ao_orgao", "trecho_veto": "DAS INSCRIÇÕES: as propostas serão recebidas", "confianca": 0.8}))
        p1 = t_classificar_objeto(veto, {"id": "a", "titulo": ""}, TEXTO)
        self.assertEqual(p1["familia"], "servico_ao_orgao"); self.assertTrue(p1["valido"])          # veto com trecho real
        ruim = IALocal(transporte=falso({"e_fomento_a_osc": True, "trecho_fomento": "frase que não existe no documento nenhum", "sinal_de_veto": None, "confianca": 0.95}))
        p2 = t_classificar_objeto(ruim, {"id": "a", "titulo": "Edital 05/2026"}, TEXTO)
        self.assertFalse(p2["valido"]); self.assertIn("trecho", p2["invalido_por"])
        inc = IALocal(transporte=falso({"e_fomento_a_osc": False, "sinal_de_veto": None, "confianca": 0.7}))
        self.assertEqual(t_classificar_objeto(inc, {"id": "a", "titulo": ""}, TEXTO)["familia"], "atencao")   # sem sinal claro → atenção
        self.assertIsNone(t_classificar_objeto(IALocal(transporte=falso({"familia": "x"})), {"id": "a", "titulo": ""}, TEXTO))  # fora do esquema

    def test_prazo_inventado_e_descartado(self):
        inv = IALocal(transporte=falso({"objeto": "seleção de organização da sociedade civil", "objeto_trecho": "seleção de organização da sociedade civil",
                                        "fim": "2026-12-31", "prazo_trecho": "até 31 de dezembro de 2026", "pagina_oficial": None}))
        p = t_extrair_objeto_prazo(inv, {"id": "b"}, TEXTO)
        self.assertIsNone(p["fim"])                      # data sem trecho no texto: fora
        self.assertTrue(p["objeto"])                     # objeto com trecho: fica
        ok = IALocal(transporte=falso({"objeto": "seleção de organização da sociedade civil", "objeto_trecho": "seleção de organização da sociedade civil",
                                       "inicio": "2026-10-01", "fim": "2026-10-30", "prazo_trecho": "até 30 de outubro de 2026"}))
        p2 = t_extrair_objeto_prazo(ok, {"id": "b"}, TEXTO); self.assertEqual(p2["fim"], "2026-10-30")

    def test_lexico_so_com_exemplo_real_e_sem_cruzar(self):
        ia = IALocal(transporte=falso({"positivos": [{"termo": "termo de fomento", "exemplo": "x"}, {"termo": "unicórnio", "exemplo": "x"}],
                                       "vetos": [{"termo": "pregão", "exemplo": "y"}, {"termo": "edital", "exemplo": "y"}]}))
        p = t_propor_lexico(ia, ["Edital de termo de fomento cultura"], ["Pregão eletrônico edital 9"])
        self.assertEqual([x["termo"] for x in p["positivos"]], ["termo de fomento"])     # 'unicórnio' não está em aprovado
        self.assertEqual([x["termo"] for x in p["vetos"]], ["pregão"])                  # 'edital' aparece nos dois lados: fora
        self.assertEqual(p["descartados"], 2)

    def test_rota_sugerida_valida_url(self):
        ia = IALocal(transporte=falso({"causa_provavel": "home institucional", "confianca": 0.7,
                                       "tentar": [{"tipo": "url", "valor": "https://gife.org.br/agenda/", "porque": "lista oportunidades"}, {"tipo": "url", "valor": "não é url", "porque": ""}, {"tipo": "termo", "valor": "chamada de projetos", "porque": ""}]}))
        p = t_diagnosticar_rota(ia, {"id": "plat-gife", "nome": "GIFE", "perfil": "x", "rotas": [], "diagnostico": {}, "lexico": []})
        self.assertTrue(p["valido"]); self.assertEqual([x["valido"] for x in p["tentar"]], [True, False, True])

    def test_catalogo_do_dia(self):
        ia = IALocal(transporte=falso({"resumo": "Dois chamamentos municipais e um edital privado.", "destaques": [{"titulo": "x", "porque": "y"}]}))
        p = t_catalogar_achado(ia, "2026-09-20", {"pncp-api": [{"titulo": "Chamamento"}]}); self.assertTrue(p["valido"])


class TesteCicloEAplicacao(unittest.TestCase):
    def test_ciclo_sem_servidor_nao_inventa(self):
        class Off(IALocal):
            def disponivel(self): return False
        r = ciclo(Off()); self.assertFalse(r["disponivel"]); self.assertIn("iniciar", r["nota"])

    def test_aplicar_grava_como_proposta_nunca_sobrescreve(self):
        import datetime
        dia = datetime.date.today().isoformat()
        pasta = ROOT / "estado/ia_local"; pasta.mkdir(parents=True, exist_ok=True)
        (pasta / f"propostas-{dia}.json").write_text(json.dumps({"propostas": [
            {"tarefa": "extrair_objeto_prazo", "id": "lab-ia-1", "objeto": "seleção de OSC", "inicio": None, "fim": "2026-10-30", "trechos": {}, "valido": True},
            {"tarefa": "propor_lexico", "positivos": [{"termo": "termo de fomento", "exemplo": "x"}], "vetos": [], "valido": True},
            {"tarefa": "diagnosticar_rota", "motor": "plat-gife", "causa_provavel": "x", "tentar": [{"tipo": "url", "valor": "https://gife.org.br/agenda/", "valido": True}], "confianca": .7, "valido": True},
            {"tarefa": "classificar_objeto", "id": "lab-ia-2", "familia": "fomento_osc", "confianca": .9, "valido": False, "invalido_por": "trecho"}]}), encoding="utf-8")
        r = aplicar(dia)
        self.assertEqual(r["extracao"], 1); self.assertEqual(r["rotas"], 1); self.assertEqual(r["classificacao"], 0)   # a inválida não entra
        ex = json.loads((ROOT / "dados/editais/extraidos/lab-ia-1.json").read_text(encoding="utf-8"))
        self.assertEqual(ex["proposta_ia"]["fim"], "2026-10-30"); self.assertNotIn("Prazo de inscrição", ex.get("itens", {}))   # proposta, não dado confirmado
        self.assertEqual(ex["propostas_ia_local"][0]["origem"], "ia_local")
        rot = json.loads((ROOT / "estado/rotas_sugeridas_ia.json").read_text(encoding="utf-8"))
        self.assertEqual(rot["sugestoes"][-1]["status"], "a_confirmar_pelo_titular")
        (ROOT / "dados/editais/extraidos/lab-ia-1.json").unlink(); (pasta / f"propostas-{dia}.json").unlink()

    def test_configuracao_e_instalador(self):
        self.assertEqual(CFG["modelos"]["principal"]["nome"], "Qwen2.5-3B-Instruct"); self.assertLessEqual(CFG["modelos"]["principal"]["tamanho_gb"], 2.5)
        self.assertEqual(CFG["motor"]["nome"], "llama.cpp"); self.assertLessEqual(CFG["motor"]["tamanho_mb"], 25)
        self.assertIn("prazo", CFG["validacao"]["trecho_literal_obrigatorio_para"])
        self.assertTrue((ROOT / "scripts/ia_local_instalar.py").exists())
        self.assertTrue((ROOT / "biblioteca_alexandria/IA-LOCAL-ESTUDO-DO-CONSELHO-2026-09-20.md").exists())
        self.assertIn("ia_local/", (ROOT / ".gitignore").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
