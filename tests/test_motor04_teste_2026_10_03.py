"""03/10/2026 — teste do motor 04 (Câmara Municipal de Goiânia): robots.txt do SUAP respeitado, pautas do Plenário
(fonte D) lidas no portal, publicado × lido para o maestro, e os casos-limite reais do classificador. Sem rede."""
import json, os, sys, tempfile, unittest
from datetime import date
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import camara_goiania as cg
from src import maestro

HOJE = date(2026, 10, 3)
BASE = "https://www.goiania.go.leg.br"
LISTAGEM = f"""<html><body>
<a href="{BASE}/processo-legislativo/pautas-de-sessoes/pauta-de-projetos-01-10-2026.pdf/view">Pauta de Projetos 01-10-2026.pdf</a>
<a href="{BASE}/processo-legislativo/pautas-de-sessoes/pauta-de-requerimentos-01-10-2026-5.pdf">requerimentos</a>
<a href="{BASE}/processo-legislativo/pautas-de-sessoes/pauta-de-projetos-29-09-2026.pdf">Pauta de Projetos 29-09-2026.pdf</a>
<a href="{BASE}/processo-legislativo/pautas-de-sessoes/pauta-de-projetos-02-07-2026.pdf">antiga</a>
<a href="https://outro.exemplo.br/pauta-de-projetos-30-09-2026.pdf">outro host</a>
</body></html>"""
# o formato real do PDF (texto extraído), com nomes de pessoa trocados por um marcador
PAUTA_0110 = ("PAUTA DE PROJETOS - 78ª SESSÃO ORDINÁRIA - 01/10/2026 ____ Projeto de Decreto Legislativo 084/2023 Criação: 04/12/2023 "
              "Autoria: VEREADOR A Fase: Única Quórum: 2/3 Votação: Simbólica Resumo: CONCEDE TÍTULO DE CIDADÃ GOIANIENSE À Sra. PESSOA X. "
              "Comissão: Constituição, Justiça e Redação Relatoria: VEREADOR B Conclusão: Pela Aprovação. ______ "
              "Projeto de Lei 298/2021 Criação: 10/05/2021 Autoria: VEREADOR C Fase: Segunda Quórum: Simples Votação: Simbólica "
              "Resumo: INSTITUI A CAMPANHA FARMÁCIA SOLIDÁRIA PARA DOAÇÃO, REAPROVEITAMENTO, CONSCIENTIZAÇÃO E DISTRIBUIÇÃO DE MEDICAMENTOS. "
              "Comissão: Saúde e Assistência Social Relatoria: VEREADOR D Conclusão: Pela Aprovação ______ "
              "Projeto de Lei 288/2026 Criação: 14/08/2026 Autoria: VEREADOR E Fase: Primeira Quórum: Simples Votação: Simbólica "
              "Resumo: DECLARA DE UTILIDADE PÚBLICA MUNICIPAL A ASSOCIAÇÃO DOS MORADORES E COMERCIANTES DO JARDIM AMÉRICA. "
              "Comissão: Constituição, Justiça e Redação Conclusão: Pela Aprovação ______")
PAUTA_2909 = ("PAUTA DE PROJETOS - 76ª SESSÃO ORDINÁRIA - 29/09/2026 ____ Projeto de Lei 097/2025 Criação: 20/02/2025 Autoria: VEREADOR F "
              "Fase: Segunda Quórum: Simples Votação: Simbólica Resumo: DISPÕE SOBRE A DECLARAÇÃO DE UTILIDADE PÚBLICA A ASSOCIAÇÃO DE "
              "CULTURA E DANÇA QUADRILHA JUNINA UAI. Comissão: Cultura Conclusão: Pela Aprovação ______ "
              "Projeto de Lei 298/2021 Criação: 10/05/2021 Autoria: VEREADOR C Fase: Primeira Quórum: Simples Votação: Simbólica "
              "Resumo: INSTITUI A CAMPANHA FARMÁCIA SOLIDÁRIA PARA DOAÇÃO DE MEDICAMENTOS. Comissão: Saúde ______")
CFG = json.loads((ROOT / "config/camara_goiania.json").read_text(encoding="utf-8"))


class RobotsDoSuap(unittest.TestCase):
    def test_suap_nunca_e_lido(self):
        diag = {"fontes": {k: {"falhas": [], "consultas": 0, "itens": 0} for k in "ABCD"}}
        with mock.patch.object(cg, "_get_texto", side_effect=AssertionError("o SUAP não pode ser acessado")):
            self.assertEqual(cg.fonte_a(HOJE, CFG, diag), [])
            self.assertEqual(cg.fonte_b(HOJE, CFG, diag), [])
        self.assertTrue(diag["fontes"]["A"]["proibido_robots"] and diag["fontes"]["B"]["proibido_robots"])
        self.assertEqual(diag["fontes"]["A"]["consultas"], 0)

    def test_robots_do_portal_lido_e_respeitado(self):
        cg._ROBOTS.clear()
        robots = "User-agent: *\nDisallow: /privado/\n"
        with mock.patch.object(cg, "_get_texto", return_value=robots):
            self.assertTrue(cg.robots_permite(f"{BASE}/processo-legislativo/pautas-de-sessoes", CFG))
            self.assertFalse(cg.robots_permite(f"{BASE}/privado/x", CFG))
        cg._ROBOTS.clear()


class PautasDoPlenario(unittest.TestCase):
    def test_listagem_so_pautas_de_projetos_do_proprio_host(self):
        p = cg.pautas_da_listagem(LISTAGEM, BASE)
        self.assertEqual([x["data"] for x in p], ["2026-10-01", "2026-09-29", "2026-07-02"])
        self.assertTrue(all(x["url"].endswith(".pdf") and "/view" not in x["url"] for x in p))

    def test_projetos_da_pauta_sem_nome_de_pessoa(self):
        itens = cg.projetos_da_pauta(PAUTA_0110, f"{BASE}/p.pdf", "2026-10-01")
        self.assertEqual([i["numero"] for i in itens], ["084/2023", "298/2021", "288/2026"])
        self.assertEqual(itens[1]["tipo_documento"], "Projeto de Lei")
        self.assertIn("segunda votação", itens[1]["situacao"])
        self.assertEqual(itens[0]["criado"], "2023-12-04")

    def _rodar(self, falha_pdf=False):
        cg._ROBOTS.clear()
        d = Path(tempfile.mkdtemp())
        cfg = dict(CFG, robots={"proibe_hosts": ["suap.camaragyn.go.gov.br"]}, portal=dict(CFG["portal"], buscas=[]))
        (d / "cfg.json").write_text(json.dumps(cfg), encoding="utf-8")
        textos = {"01-10": PAUTA_0110, "29-09": PAUTA_2909}

        def texto(url, timeout=25, max_bytes=0):
            if url.endswith("robots.txt"):
                return "User-agent: *\nDisallow:\n"
            if "pautas-de-sessoes" in url:
                return LISTAGEM
            raise AssertionError(url)

        def pdf(url, cfg_, F, max_bytes=0):
            F["consultas"] += 1
            if falha_pdf and "29-09" in url:
                raise RuntimeError("tempo esgotado")
            return next(v for k, v in textos.items() if k in url).encode()
        with mock.patch.object(cg, "CFG", d / "cfg.json"), mock.patch.object(cg, "ESTADO", d / "est.json"), \
             mock.patch.object(cg, "_get_texto", side_effect=texto), mock.patch.object(cg, "_get_bytes", side_effect=pdf), \
             mock.patch.object(cg, "_texto_pdf", side_effect=lambda b: b.decode()), mock.patch.object(cg.time, "sleep"), \
             mock.patch.object(cg, "_hoje_real", return_value=HOJE):
            r = cg.ler_motor()
            est = json.loads((d / "est.json").read_text(encoding="utf-8"))
        cg._ROBOTS.clear()
        return r, est

    def test_leitura_completa_pelas_pautas(self):
        r, est = self._rodar()
        dg = r["diagnostico"]
        self.assertEqual(dg["leitura_do_dia"]["pautas_publicadas"], 2)        # a de julho está fora da janela
        self.assertEqual(dg["leitura_do_dia"]["pautas_lidas"], 2)
        self.assertNotIn("paginas_nao_lidas", dg)
        self.assertIn("A", dg["proibido_robots"]["fontes"])
        propria = [a for a in est["acompanhar"] if a.get("propria")]
        self.assertEqual(len(propria), 1)                                       # o PL 288/2026 da associação, pela pauta
        self.assertIn("288/2026", json.dumps(propria, ensure_ascii=False))
        self.assertEqual([h["entidade"] for h in est["utilidade_publica"]], ["ASSOCIAÇÃO DE CULTURA E DANÇA QUADRILHA JUNINA UAI"])
        self.assertEqual(dg["vereditos"]["RUIDO"], 3)       # título de cidadã, a campanha (uma vez só) e a utilidade pública de OUTRA entidade (vai à habilitação)

    def test_pauta_nao_lida_vira_parcial_no_maestro(self):
        r, _ = self._rodar(falha_pdf=True)
        dg = r["diagnostico"]
        self.assertEqual(dg["paginas_nao_lidas"], ["pauta de 2026-09-29 (pauta-de-projetos-29-09-2026.pdf)"])
        self.assertEqual(maestro.cobertura(cg.MOTOR_ID, {"cor": "azul", "falhas": 0}, {}, dg), "parcial")


class CasosLimite(unittest.TestCase):
    def c(self, assunto=None, fonte="D", titulo=None, descricao=None, numero=None):
        return cg.classificar_item({"fonte": fonte, "assunto": assunto, "titulo": titulo, "descricao": descricao, "numero": numero},
                                   HOJE, CFG)

    def test_titulo_de_cidada_e_cidadania_sao_ruido(self):
        for t in ("CONCEDE TÍTULO DE CIDADÃ GOIANIENSE À Sra. X", "CONCEDE TÍTULO HONORÍFICO DE CIDADANIA GOIANIENSE AO Sr. Y"):
            c = self.c(t)
            self.assertEqual((c["veredito"], c["motivos"][0]), ("RUIDO", "título honorífico ou homenagem"))

    def test_noticia_da_loa_e_janela_de_emendas(self):
        c = self.c(fonte="C", titulo="Projeto da Lei Orçamentária Anual de 2027 começa a tramitar na Câmara",
                   descricao="Proposta da LOA 2027 estima receita de R$ 11,7 bilhões")
        self.assertEqual((c["veredito"], c["categoria"]), ("ACOMPANHAR", "orcamento_emendas"))

    def test_noticia_de_lei_do_terceiro_setor(self):
        c = self.c(fonte="C", titulo="Plenário aprova atualização da legislação municipal para o terceiro setor",
                   descricao="visa aperfeiçoamento institucional e fortalecimento dos instrumentos de transparência")
        self.assertEqual((c["veredito"], c["categoria"]), ("ACOMPANHAR", "regra_para_entidades"))

    def test_projeto_da_associacao_pelo_numero(self):
        c = self.c("DECLARA DE UTILIDADE PÚBLICA MUNICIPAL A ENTIDADE", numero="288/2026")
        self.assertTrue(c["propria"]); self.assertEqual(c["veredito"], "ACOMPANHAR")

    def test_programa_sem_entidade_e_calendario_sao_ruido(self):
        self.assertEqual(self.c("INSTITUI O PROGRAMA MUNICIPAL NOSSA ESCOLA, NOSSO FUTURO")["veredito"], "RUIDO")
        self.assertEqual(self.c("INSTITUI NO CALENDÁRIO OFICIAL DO MUNICÍPIO A SEMANA MUNICIPAL DE LIMPEZA")["veredito"], "RUIDO")


class Agenda(unittest.TestCase):
    def test_motor_04_volta_para_a_nuvem(self):
        a = json.loads((ROOT / "config/agenda_motores.json").read_text(encoding="utf-8"))["motores"]["camara-goiania-pl"]
        self.assertEqual(a["coleta"], "nuvem")
        s = json.loads((ROOT / "config/sensores.json").read_text(encoding="utf-8"))
        urls = next(x for x in s["sensores_especiais"] if x["id"] == "camara-goiania-pl")["urls"]
        self.assertFalse([u for u in urls if "suap." in u])


if __name__ == "__main__":
    unittest.main()
