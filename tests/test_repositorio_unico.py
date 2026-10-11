"""11/10/2026 (titular): repositório único — um registro por oportunidade, todas as origens, prova na fonte, estante
como classificador, próximo passo pela rede neural e pela skill; todos os painéis no mesmo universo."""
import json, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import repositorio_unico as R


class TesteRepositorio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(); T = Path(cls.tmp.name)
        cls.o = (R.SAIDA, R.RESUMO); R.SAIDA = T / "r.json"; R.RESUMO = T / "s.json"
        cls.res = R.construir(gravar=True); cls.regs = json.loads(R.SAIDA.read_text())["registros"]

    @classmethod
    def tearDownClass(cls):
        R.SAIDA, R.RESUMO = cls.o; cls.tmp.cleanup()

    def test_um_registro_por_oportunidade_e_soma(self):
        ids = [x["id"] for x in self.regs]; self.assertEqual(len(ids), len(set(ids)))
        orig = [i for x in self.regs for i in x["ids_origem"]]; self.assertEqual(len(orig), len(set(orig)), "nenhum id de origem em dois registros")
        r = self.res; self.assertEqual(r["abertas"], r["validadas"] + r["em_verificacao"] + r["validacao_manual"])

    def test_todo_registro_tem_proximo_passo_estante_e_prova(self):
        for x in self.regs:
            self.assertTrue(x["proximo_passo"]); self.assertIn(x["estante"], ("sem_livro", "bronze", "prata", "ouro"))
            self.assertEqual(set(x["itens"]), set(R.DOZE))
            for it in x["itens"].values():
                self.assertIn(it["estado"], ("comprovado", "dispensado", "nao_comprovado", "falta"))
                if it["estado"] == "comprovado":
                    self.assertTrue(it.get("trecho") or it.get("valor"))

    def test_validada_so_com_prova(self):
        for x in self.regs:
            if x["estado"] == "validada" and x["motivo_estado"].startswith("objeto e prazo"):
                self.assertEqual(x["itens"]["Objeto"]["estado"], "comprovado"); self.assertEqual(x["itens"]["Prazo de inscrição"]["estado"], "comprovado")

    def test_chrome_e_excecao_e_skills(self):
        for x in self.regs:
            if x["proximo_passo"].startswith("Busca externa"):
                self.assertTrue(x["cartorio"]["tentativas"] >= 5 or x["cartorio"]["esgotada"], "busca externa só depois das abordagens automáticas")
        self.assertEqual(R._skill("motor agregadores · farolcultura"), "agregador"); self.assertEqual(R._skill("motor pncp-api"), "pncp")
        sk = json.loads((ROOT / "config/skills_extracao_origem.json").read_text(encoding="utf-8"))["skills"]
        for k, v in sk.items():
            self.assertEqual(sorted(v["ordem"]), list(range(1, 11)), k)

    def test_auditoria_e_integracoes(self):
        self.assertIn("auditoria", self.res); self.assertIn("motivo_sem_livro", self.res)
        self.assertIn("from .repositorio_unico import construir as _repo", (ROOT / "src/fluxo_oportunidades.py").read_text(encoding="utf-8"))
        c = (ROOT / "src/cartorio.py").read_text(encoding="utf-8"); self.assertIn("_repositorio()", c); self.assertIn("_ordem_da_skill(op)", c)
        self.assertIn("RECUSADO", (ROOT / "scripts/gerar_lote_chrome.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()


class TesteMelhoriasMotores(unittest.TestCase):
    """11/10: duplicata fundida antes do registro; livro para toda oportunidade do repositório; ouro sem prova → vermelho."""
    def test_deduplicar_antes_do_registro(self):
        from src.fluxo_oportunidades import deduplicar
        itens = [{"id": "a", "titulo": "Edital nº 3/2026 de Cultura", "url": "https://x.go.gov.br/edital-3-2026", "checklist": {"Valor": {"s": "falta"}}},
                 {"id": "b", "titulo": "Edital nº 3/2026 de Cultura", "url": "https://x.go.gov.br/edital-3-2026", "link_oficial": "https://x.go.gov.br/e.pdf",
                  "checklist": {"Valor": {"s": "ok", "v": "R$ 10.000,00"}}}]
        fica, st = deduplicar(itens)
        self.assertEqual(len(fica), 1); self.assertEqual(st["duplicatas_fundidas_antes_do_registro"], 1)
        self.assertEqual(fica[0]["link_oficial"], "https://x.go.gov.br/e.pdf"); self.assertEqual(fica[0]["checklist"]["Valor"]["s"], "ok")

    def test_criador_le_o_repositorio_e_ajuste_generico(self):
        self.assertIn("dados/oportunidades/repositorio_unico.json", (ROOT / "src/opressores_repositorio.py").read_text(encoding="utf-8"))
        self.assertTrue((ROOT / "scripts/ajustar_ouro_sem_prova.py").exists())


class TesteRegraExterna(unittest.TestCase):
    """11/10: toda busca externa termina em arquivar, eliminar ou completar; o livro direciona a busca e é arquivado."""
    def test_cobrar_resolucao(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        import importar_revisao_abertas as I
        regs = {"a": {"veredito": "prata"}, "b": {"veredito": "encerrada", "prazo": {"fim": "2026-09-01"}},
                "c": {"veredito": "encerrada", "prazo": {"fim": "2026-09-01", "trecho": "inscrições até 01/09/2026"}},
                "d": {"veredito": "ruido", "parecer": "é resultado de seleção"}, "e": {"veredito": "fora_perfil"}, "f": {"veredito": "ouro"}}
        av = I.cobrar_resolucao(regs)
        self.assertEqual({k: v["veredito"] for k, v in regs.items()}, {"a": "validacao_manual", "b": "validacao_manual", "c": "encerrada",
                                                                       "d": "ruido", "e": "validacao_manual", "f": "ouro"})
        self.assertEqual(len(av), 3)

    def test_livro_direciona_e_arquiva(self):
        self.assertIn("REGRA_EXTERNA", (ROOT / "src/repositorio_unico.py").read_text(encoding="utf-8"))
        o = (ROOT / "src/opressores_repositorio.py").read_text(encoding="utf-8"); self.assertIn('x["arquivado"] =', o); self.assertIn("livros_reabertos", o)
        self.assertIn("regra_de_resolucao", (ROOT / "scripts/gerar_lote_chrome.py").read_text(encoding="utf-8"))
        self.assertTrue((ROOT / "docs/prompts/PROMPT-BUSCA-EXTERNA-PADRAO.md").exists())


class TesteInterceptadorNaCadeia(unittest.TestCase):
    """11/10: o repositório direciona o Interceptador (fila e contexto) e recebe de volta só o que tem fonte oficial."""
    def test_regua_no_retorno_e_passos(self):
        self.assertFalse(R._oficial("https://buscarlicitacao.com.br/licitacoes/x"), "agregador não é fonte")
        self.assertTrue(R._oficial("https://www.goiania.go.gov.br/edital.pdf"))
        s = (ROOT / "src/repositorio_unico.py").read_text(encoding="utf-8")
        self.assertIn("Interceptador: achar o site oficial (sem pista no livro", s); self.assertIn("Interceptador leu em agregador", s)

    def test_interceptador_le_o_repositorio(self):
        from src import interceptador as IC
        self.assertTrue(callable(IC.alvo_do_repositorio))
        s = (ROOT / "src/interceptador.py").read_text(encoding="utf-8")
        self.assertIn("r1 = alvo_do_repositorio(feitos)", s); self.assertIn('"contexto_do_repositorio"', s); self.assertIn('["site"] = x["link_oficial"]', s)


class TesteEsteiraFarol(unittest.TestCase):
    """11/10: toda aberta aplicável tem livro; etapa e ferramenta em cada registro; pronta vai ao Farol; aprendizado no livro."""
    def test_etapas(self):
        self.assertTrue(R._etapa("validada", "acompanhar o prazo", True, True)[0].startswith("9"))
        self.assertTrue(R._etapa("em_verificacao", "dispensar: x", True, False)[0].startswith("4"))
        self.assertTrue(R._etapa("em_verificacao", "Interceptador: achar o site oficial", False, False)[0].startswith("6"))
        self.assertEqual(R._etapa("em_verificacao", "Interceptador: completar 3 item(ns)", True, False)[1], "Interceptador")
        self.assertTrue(R._etapa("em_verificacao", "Busca externa (Claude/Chrome): …", True, False)[0].startswith("8"))
        self.assertTrue(R._etapa("validada", "acompanhar o prazo", False, False)[0].startswith("5"))

    def test_livro_farol_e_aprendizado(self):
        o = (ROOT / "src/opressores_repositorio.py").read_text(encoding="utf-8")
        self.assertIn('if m and not re.match(r"(?i)fora da abrang|sem crit[ée]rio de sele", m):', o)
        self.assertIn("não se aplica a OSC: o destino é a dispensa", o); self.assertIn('x["pagina_aprendida"]', o)
        self.assertIn('"modelo": "oportunidade completa", "pronta": True', (ROOT / "src/preparacao_livros.py").read_text(encoding="utf-8"))
        self.assertIn("repositorio_depois_dos_livros", (ROOT / "src/fluxo_oportunidades.py").read_text(encoding="utf-8"))
        sys.path.insert(0, str(ROOT / "scripts")); import importar_revisao_abertas as I
        self.assertTrue(callable(I.gravar_aprendizado))
        self.assertIn('"aprendizado"', (ROOT / "docs/prompts/PROMPT-BUSCA-EXTERNA-PADRAO.md").read_text(encoding="utf-8"))

    def test_gravar_aprendizado(self):
        sys.path.insert(0, str(ROOT / "scripts")); import importar_revisao_abertas as I
        import tempfile as _t
        with _t.TemporaryDirectory() as d:
            orig = I.ROOT; I.ROOT = Path(d)
            try:
                av = I.gravar_aprendizado({"a": {"veredito": "ouro", "aprendizado": {"onde_estava": "https://x.go.gov.br/e.pdf", "sugestao_para_o_motor": "ler a aba Chamamentos"}},
                                           "b": {"veredito": "encerrada"}}, "EXTERNA-T")
                ap = json.loads((Path(d) / "estado/biblioteca/aprendizados_externos.json").read_text())["aprendizados"]
                me = json.loads((Path(d) / "docs/dados/melhorias_motores_externas.json").read_text())["melhorias"]
            finally:
                I.ROOT = orig
        self.assertIn("a", ap); self.assertEqual(me[0]["sugestao"], "ler a aba Chamamentos"); self.assertEqual(av, ["b: sem relatório de aprendizado"])


class TesteMunicipaisForaDeGoias(unittest.TestCase):
    """11/10/2026 (titular): municipal de fora de Goiás é arquivada (livro fica); internacionais, nacionais e
    estaduais ficam; sem UF determinada, fica."""
    def test_regra(self):
        f = R.municipal_fora_de_goias
        self.assertTrue(f({"titulo": "MUNICIPIO DE OLINDINA — Chamamento", "uf": "BA"}))
        self.assertTrue(f({"titulo": "Prefeitura de Itajaí — concurso", "url": "https://corrivus.com.br/santa-catarina/itajai/x"}))
        self.assertTrue(f({"titulo": "Chamamento", "orgao": "Prefeitura Municipal de Iguatu", "link_oficial": "https://iguatu.ce.gov.br/x"}))
        self.assertIsNone(f({"titulo": "Edital Cultura Goiatuba 2026", "orgao": "Prefeitura de Goiatuba", "link_oficial": "https://goiatuba.go.gov.br/x"}))
        self.assertIsNone(f({"titulo": "MUNICIPIO DE TRINDADE — credenciamento", "url": "https://pncp.gov.br/app/editais/1/2026/1"}), "sem UF: fica")
        self.assertIsNone(f({"titulo": "Edital estadual", "orgao": "Secretaria de Estado da Cultura de São Paulo", "nivel": "estadual", "uf": "SP"}))
        self.assertIsNone(f({"titulo": "Programa federal de fomento", "nivel": "federal", "uf": "DF"}))
        self.assertIn("_arq_mun", (ROOT / "src/opressores_repositorio.py").read_text(encoding="utf-8"), "o livro fica")
