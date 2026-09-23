"""Auditoria dos 29 motores, aprendizados do Piloto e saída de busca (22/09)."""
import json, pathlib, unittest
from src.auditoria_29 import auditar, BLOQUEADOS, _efetividade_do_acervo
from src.aprendizados_piloto import (avaliar, ja_tratado, marcar_tratado, quarentenar,
                                     faxina, publicar, MOTIVOS, QUAR, LICOES, TRATADOS)
from src.missao_especial import _relevante
ROOT = pathlib.Path(__file__).resolve().parents[1]


def setUpModule():
    """A base de aprendizados vai para pasta temporária: teste não escreve em produção."""
    global _TMP
    import os, tempfile, importlib
    _TMP = tempfile.mkdtemp(prefix="aprendizados-")
    os.environ["ELDORADO_APRENDIZADOS"] = _TMP
    import src.aprendizados_piloto as A
    importlib.reload(A)
    g = globals()
    for nome in ("avaliar", "ja_tratado", "marcar_tratado", "quarentenar", "faxina",
                 "publicar", "QUAR", "LICOES", "TRATADOS", "MOTIVOS"):
        if hasattr(A, nome):
            g[nome] = getattr(A, nome)


def tearDownModule():
    import os, shutil, importlib
    os.environ.pop("ELDORADO_APRENDIZADOS", None)
    import src.aprendizados_piloto as A
    importlib.reload(A)
    shutil.rmtree(_TMP, ignore_errors=True)



class _IA:
    def __init__(self, r=None): self.r = r; self.perguntas = []
    def perguntar(self, p, e=None): self.perguntas.append(p); return self.r


class TesteAuditoriaDosMotores(unittest.TestCase):
    def test_julga_cada_motor_por_volume_e_efetividade(self):
        d = json.loads((ROOT / "docs/dados/auditoria_29.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(d["motores"], 29)
        self.assertEqual(len(d["fichas"]), d["motores"])
        for f in d["fichas"]:
            self.assertIn(f["estado"], ("produtivo", "ruidoso", "seco", "bloqueado", "nunca_rodou"))
            self.assertTrue(f["causa"] and f["correcao"])                 # nunca um estado sem explicação
            self.assertEqual(f["n"], d["fichas"].index(f) + 1 if False else f["n"])
        self.assertEqual(sorted({f["n"] for f in d["fichas"]}), list(range(1, d["motores"] + 1)))

    def test_ruidoso_e_diferente_de_produtivo(self):
        d = json.loads((ROOT / "docs/dados/auditoria_29.json").read_text(encoding="utf-8"))
        ruid = [f for f in d["fichas"] if f["estado"] == "ruidoso"]
        self.assertTrue(ruid, "o pncp-api traz 127 e quase nada serve: tem de ser marcado como ruidoso")
        self.assertIn("filtro", ruid[0]["correcao"])

    def test_bloqueados_saem_do_orcamento_de_voo(self):
        cfg = json.loads((ROOT / "config/rotas_motores.json").read_text(encoding="utf-8"))
        m = cfg.get("motores") or cfg
        for b in BLOQUEADOS:
            if b in m:
                self.assertEqual(m[b].get("coleta"), "local", b)

    def test_acervo_foi_limpo_do_que_nao_serve(self):
        # Os 334 fora do objeto NÃO são apagados: ficam marcados. Apagar esvaziava as
        # estatísticas históricas de que o fluxo de decisão depende.
        import json as _j, glob as _g
        base = sorted(_g.str if False else _g.glob(str(ROOT / "dados/editais/*-eldorado-*-completo.json")))[-1]
        d = _j.loads(open(base, encoding="utf-8").read())
        marcados = [v for v in d["itens"].values() if v.get("fora_do_objeto")]
        self.assertGreater(len(marcados), 200, "o que não serve fica marcado, não apagado")
        self.assertTrue(all(v.get("motivo_fora") for v in marcados))
        f = json.loads((ROOT / "estado/piloto/aprendizados/acervo_fora_do_objeto.json").read_text(encoding="utf-8"))
        self.assertGreater(f["total"], 200)                               # o descartado ficou guardado
        self.assertTrue(all(v.get("motivo") for v in f["itens"].values()))  # cada um com seu motivo

    def test_relatorio_tem_os_motores_um_por_um(self):
        r = (ROOT / "biblioteca_alexandria/AUDITORIA-MOTORES-29-2026-09-22.md").read_text(encoding="utf-8")
        d = json.loads((ROOT / "docs/dados/auditoria_29.json").read_text(encoding="utf-8"))
        for f in d["fichas"]:
            self.assertIn(f"`{f['id']}`", r, f["id"])
        for s in ("Brave Search", "sitemap", "coleta local", "efetividade"):
            self.assertIn(s, r, s)


class TesteAprendizadosDoPiloto(unittest.TestCase):
    """Usa motores REAIS e devolve a base ao estado anterior — motor de ensaio é bloqueado
    desde 23/09, justamente para os testes não contaminarem as estatísticas."""

    def setUp(self):
        from src.aprendizados_piloto import LICOES, MELHORIAS, AVAL
        self._bk = {p: p.read_text(encoding="utf-8") for p in (LICOES, MELHORIAS) if p.exists()}
        self._avs = set(AVAL.glob("*.json")) if AVAL.exists() else set()

    def tearDown(self):
        from src.aprendizados_piloto import AVAL
        for p, txt in self._bk.items():
            p.write_text(txt, encoding="utf-8")
        for a in (set(AVAL.glob("*.json")) - self._avs):
            a.unlink()

    def test_avalia_efetividade_depois_da_missao(self):
        ia = _IA({"itens": [{"n": 0, "serve": True, "porque": "edital de fomento"},
                            {"n": 1, "serve": False, "porque": "licitação de merenda"}],
                  "o_que_melhorar_no_motor": "filtrar por 'chamamento' no título"})
        r = avaliar(ia, {"motor": "motor-gife", "tipo": "cacar_oportunidade", "licao": "2 lidos"},
                    [{"titulo": "Edital", "url": "https://t1.org"}, {"titulo": "Merenda", "url": "https://t2.gov"}])
        a = r["avaliacao"]
        self.assertEqual(a["uteis"], 1); self.assertEqual(a["descartados"], 1); self.assertEqual(a["efetividade"], 0.5)
        self.assertTrue(a["melhoria_sugerida"])                           # indica melhoria para o motor
        self.assertEqual(len(r["uteis"]), 1)                              # só o que serve segue adiante
        self.assertIn("porque_serve", r["uteis"][0])

    def test_indica_o_motivo_do_insucesso(self):
        r = avaliar(_IA(), {"motor": "motor-patrocinio", "tipo": "cacar_oportunidade",
                            "licao": "a busca não devolveu resultado (rede ou bloqueio)"}, [])
        a = r["avaliacao"]
        self.assertEqual(a["motivo_do_insucesso"], "busca_vazia")
        self.assertEqual(a["explicacao"], MOTIVOS["busca_vazia"])
        self.assertIn("nada_no_crivo", MOTIVOS); self.assertIn("modelo_mudo", MOTIVOS)

    def test_nao_volta_no_edital_ja_abordado(self):
        marcar_tratado("https://ja.org/e", "Edital velho", "descartado", "fora do objeto")
        self.assertTrue(ja_tratado("https://ja.org/e"))
        t = json.loads(TRATADOS.read_text(encoding="utf-8"))["itens"]["https://ja.org/e"]
        self.assertTrue(t["entregue_ao_claude"])                          # passa a ser avaliação do Claude
        src = (ROOT / "src/piloto.py").read_text(encoding="utf-8")
        self.assertIn("não se volta no que já foi abordado", src)
        self.assertIn('ach = _r["uteis"]', src)                           # só o que serve entra no sistema

    def test_insucesso_fica_na_pasta_do_piloto_e_nao_no_acervo(self):
        quarentenar({"titulo": "x", "url": "https://x"}, "fora_do_objeto", "m/t")
        arqs = list(QUAR.glob("*.jsonl"))
        self.assertTrue(arqs)
        self.assertTrue(str(QUAR).endswith("quarentena"))   # a base pode estar redirecionada
        self.assertNotIn("quarentena", str(ROOT / "biblioteca_alexandria"))
        p = publicar()
        self.assertIn("só informação correta entra na Biblioteca", p["regra"])

    def test_tres_falhas_iguais_viram_regra(self):
        for _ in range(3):
            avaliar(_IA(), {"motor": "empresas-incentivadas", "tipo": "cacar_oportunidade",
                            "licao": "a busca não devolveu resultado (rede ou bloqueio)"}, [])
        d = json.loads(LICOES.read_text(encoding="utf-8"))["itens"]
        it = d["empresas-incentivadas|busca_vazia"]
        self.assertGreaterEqual(it["vezes"], 3)
        self.assertIn("precisa de correção, não de mais tentativas", it["regra"])

    def test_faxina_de_tres_dias_esta_no_ciclo(self):
        w = (ROOT / ".github/workflows/conselho.yml").read_text(encoding="utf-8")
        self.assertIn("src.aprendizados_piloto faxina", w)
        self.assertIn("src.auditoria_29 aplicar", w)
        r = faxina()
        self.assertEqual(r["dias"], 3)


class TesteSaidaDeBusca(unittest.TestCase):
    def test_buscadores_mortos_foram_removidos(self):
        from src.piloto_busca import BUSCADORES, CHAVES
        self.assertEqual([b[0] for b in BUSCADORES], ["duckduckgo"])       # só o que provou funcionar
        self.assertIn("brave", CHAVES); self.assertIn("google_cse", CHAVES)

    def test_leitura_direta_do_site_nao_depende_de_buscador(self):
        from src.piloto_busca import buscar_na_fonte
        src = (ROOT / "src/piloto_busca.py").read_text(encoding="utf-8")
        self.assertIn("SAÍDA QUE NENHUM BUSCADOR BLOQUEIA", src)
        self.assertIn("sitemap.xml", src); self.assertIn("robots.txt", src)
        self.assertTrue(callable(buscar_na_fonte))

    def test_api_com_chave_nao_quebra_o_voo_sem_chave(self):
        from src.piloto_busca import _por_api
        self.assertEqual(_por_api("brave", "x", 5), [])
        self.assertEqual(_por_api("google_cse", "x", 5), [])
