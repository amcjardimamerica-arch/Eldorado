"""15/10/2026 (titular): os livros são o banco — cada oportunidade cria ou vincula o seu livro; eliminada some."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src import banco_livros as B


class BancoLivros(unittest.TestCase):
    def setUp(self):
        self.r = Path(tempfile.mkdtemp())
        for d in ("biblioteca_alexandria/fontes", "dados/oportunidades/validacao_mapa", "estado/cartorio"):
            (self.r / d).mkdir(parents=True)
        (self.r / "biblioteca_alexandria/fontes/motores.json").write_text(json.dumps({"motores": [
            {"id": "op-antigo", "programa": "FIA Goiânia", "pagina": "https://www.goiania.go.gov.br/fia/edital-2026", "historico": [{"ano": 2025}]}]}))
        regs = [{"id": "a1", "titulo": "FIA Goiânia 2026", "url": "https://goiania.go.gov.br/fia/edital-2026", "itens": {"Objeto": {"estado": "comprovado", "valor": "x"}}},
                {"id": "b2", "titulo": "Chamamento novo", "url": "https://anapolis.go.gov.br/chamamento-7", "nota_rede": 0.8}]
        (self.r / "dados/oportunidades/repositorio_unico.json").write_text(json.dumps({"registros": regs}))
        (self.r / "estado/cartorio/certidoes.json").write_text(json.dumps({"certidoes": {"estrela:b2": {"em": "2026-10-15", "leitura": "total",
            "itens": {"Valor": {"valor": "R$ 10.000,00", "trecho": "valor global de R$ 10.000,00", "pagina": 3, "documento": "https://anapolis.go.gov.br/e.pdf"}}}}}))
        self.p = [mock.patch.object(B, "ROOT", self.r), mock.patch.object(B, "CAT", self.r / "biblioteca_alexandria/fontes/motores.json"),
                  mock.patch.object(B, "INDICE", self.r / "biblioteca_alexandria/fontes/indice_chaves.json")]
        for x in self.p:
            x.start()

    def tearDown(self):
        for x in self.p:
            x.stop()

    def test_vincula_cria_e_reune(self):
        r = B.consolidar()
        self.assertEqual((r["livros_vinculados"], r["livros_criados"]), (1, 1))
        L = {lv["id"]: lv for lv in json.loads((self.r / "biblioteca_alexandria/fontes/motores.json").read_text())["motores"]}
        self.assertEqual(L["op-antigo"]["oportunidade"]["id_repositorio"], "a1")
        self.assertEqual(L["op-antigo"]["historico"], [{"ano": 2025}])                     # o histórico do livro fica
        novo = next(lv for lv in L.values() if lv["id"] != "op-antigo")["oportunidade"]
        self.assertEqual(novo["checklist12"]["Valor"]["pagina"], 3)
        self.assertEqual({a["origem"] for a in novo["analises"]}, {"Cartório", "rede neural"})
        self.assertEqual(B.livro_da_oportunidade({"url": "https://anapolis.go.gov.br/chamamento-7"})["oportunidade"]["id_repositorio"], "b2")

    def test_eliminada_some(self):
        B.consolidar()
        (self.r / "dados/oportunidades/repositorio_unico.json").write_text(json.dumps({"registros": []}))
        r = B.consolidar()
        L = json.loads((self.r / "biblioteca_alexandria/fontes/motores.json").read_text())["motores"]
        self.assertEqual(r["livros_removidos"], 1)
        self.assertEqual([lv["id"] for lv in L], ["op-antigo"])
        self.assertNotIn("oportunidade", L[0])


if __name__ == "__main__":
    unittest.main()


class Etapa2Repositorio(unittest.TestCase):
    """16/10/2026: o repositório lê dos livros — ingestão com a origem separada, a ordem preservada e a sincronia."""
    def setUp(self):
        self.r = Path(tempfile.mkdtemp()); (self.r / "biblioteca_alexandria/fontes").mkdir(parents=True)
        (self.r / "biblioteca_alexandria/fontes/motores.json").write_text(json.dumps({"motores": [
            {"id": "op-antigo", "programa": "FIA", "pagina": "https://goiania.go.gov.br/fia"}]}))
        self.p = [mock.patch.object(B, "CAT", self.r / "biblioteca_alexandria/fontes/motores.json")]
        for x in self.p:
            x.start()

    def tearDown(self):
        for x in self.p:
            x.stop()

    def test_ingerir_e_ler(self):
        brutos = [{"id": "1", "_fonte": "fluxo", "url": "https://goiania.go.gov.br/fia", "link_oficial": "https://goiania.go.gov.br/fia/edital.pdf"},
                  {"id": "2", "_fonte": "fluxo", "url": "https://x.gov.br/a"},
                  {"id": "1", "_fonte": "caixa dos motores", "url": "https://goiania.go.gov.br/fia"}]       # mesma oportunidade, outra origem
        r = B.ingerir(brutos)
        self.assertEqual((r["vinculados"], r["livros_criados"]), (2, 1))
        lidos = B.brutos_dos_livros()
        self.assertEqual([(b["id"], b["_fonte"]) for b in lidos], [("1", "fluxo"), ("2", "fluxo"), ("1", "caixa dos motores")])
        self.assertEqual(lidos[0]["link_oficial"], "https://goiania.go.gov.br/fia/edital.pdf")    # a 2ª origem não apaga a 1ª
        B.ingerir([brutos[0]])                                                                    # a origem deixou de trazer o '2'
        L = json.loads((self.r / "biblioteca_alexandria/fontes/motores.json").read_text())["motores"]
        self.assertEqual([lv["id"] for lv in L], ["op-antigo"])                                   # livro só daquele registro sai
        self.assertEqual([b["id"] for b in B.brutos_dos_livros()], ["1"])


class Etapa2Cartorio(unittest.TestCase):
    """16/10/2026: a fila do Cartório vem dos livros, com os mesmos registros e as mesmas assinaturas."""
    def test_fila_dos_livros(self):
        from src import cartorio as C
        r = Path(tempfile.mkdtemp()); (r / "biblioteca_alexandria/fontes").mkdir(parents=True)
        cat = r / "biblioteca_alexandria/fontes/motores.json"; cat.write_text(json.dumps({"motores": []}))
        x = {"id": "e1", "_fonte": "fluxo", "titulo": "Chamamento", "url": "https://x.go.gov.br/c", "checklist": {"Objeto": {"s": "falta"}}}
        with mock.patch.object(B, "CAT", cat), mock.patch.object(C, "_repositorio", lambda: None), mock.patch.object(C, "_situacao_caixa", lambda: {}):
            B.ingerir([x])
            nova = C.fila_estrelas()
            velha = C.fila_estrelas({"itens_por_uf": {"GO": [x]}})
        self.assertEqual([o["id"] for o in nova], ["e1"])
        self.assertEqual(C._assinatura(nova[0]), C._assinatura(velha[0]))


class Etapa2Fichas(unittest.TestCase):
    """16/10/2026: o achado bruto de cada motor e o registro do agregador ficam no livro; as fichas leem de lá."""
    def test_coleta_e_agregador_no_livro(self):
        r = Path(tempfile.mkdtemp())
        for d in ("biblioteca_alexandria/fontes", "dados/oportunidades", "estado/agregadores"):
            (r / d).mkdir(parents=True)
        (r / "biblioteca_alexandria/fontes/motores.json").write_text(json.dumps({"motores": []}))
        (r / "dados/oportunidades/repositorio_unico.json").write_text(json.dumps({"registros": [
            {"id": "c1", "titulo": "Chamamento", "url": "https://x.go.gov.br/c", "ids_origem": ["c1", "c2"]}]}))
        (r / "dados/oportunidades/oportunidades.jsonl").write_text(json.dumps({"id": "c2", "sensor": "motor-x", "fonte_nome": "Fonte X"}) + "\n")
        (r / "estado/agregadores/itens.json").write_text(json.dumps({"itens": [{"id": "c1", "agregador": "Prosas"}]}))
        with mock.patch.object(B, "ROOT", r), mock.patch.object(B, "CAT", r / "biblioteca_alexandria/fontes/motores.json"), \
                mock.patch.object(B, "INDICE", r / "biblioteca_alexandria/fontes/indice_chaves.json"):
            B.consolidar()
            self.assertEqual(B.secoes_dos_livros("coleta")["c2"]["sensor"], "motor-x")
            self.assertEqual(B.secoes_dos_livros("agregador")["c1"]["agregador"], "Prosas")


class Etapa2Interceptador(unittest.TestCase):
    """16/10/2026: o Interceptador lê o fluxo (agrupado por UF) reconstruído dos livros."""
    def test_fluxo_por_uf(self):
        r = Path(tempfile.mkdtemp()); (r / "biblioteca_alexandria/fontes").mkdir(parents=True)
        cat = r / "biblioteca_alexandria/fontes/motores.json"; cat.write_text(json.dumps({"motores": []}))
        with mock.patch.object(B, "CAT", cat):
            B.ingerir([{"id": "1", "_fonte": "fluxo", "_uf": "GO", "url": "https://a.go.gov.br/x"},
                       {"id": "2", "_fonte": "fluxo", "_uf": "BR", "url": "https://b.gov.br/y"},
                       {"id": "3", "_fonte": "caixa dos motores", "url": "https://c.gov.br/z"}])
            d = B.fluxo_por_uf()["itens_por_uf"]
        self.assertEqual({uf: [x["id"] for x in L] for uf, L in d.items()}, {"GO": ["1"], "BR": ["2"]})
        self.assertNotIn("_uf", d["GO"][0]); self.assertNotIn("_fonte", d["GO"][0])


class Etapa3Portao(unittest.TestCase):
    """16/10/2026: o motor só guarda o que é oportunidade; a base bruta fica só com oportunidade e histórico de livro."""
    def test_portao(self):
        from src.porta_oportunidade import motivo_para_nao_guardar as M
        self.assertIsNone(M({"titulo": "Chamamento público de OSC — termo de colaboração", "fim": "2026-12-01"}, "2026-10-16"))
        self.assertIn("vaga", M({"titulo": "Instituto X abre vaga de estágio"}, "2026-10-16"))
        self.assertIn("prazo encerrado", M({"titulo": "Edital de fomento cultural 2026", "fim": "2026-10-01"}, "2026-10-16"))
        self.assertIn("PNCP", M({"titulo": "MUNICIPIO DE ANAPOLIS — Pregão eletrônico para aquisição de equipamentos",
                                 "url": "https://pncp.gov.br/app/editais/01005727000124/2026/136", "uf": "GO"}, "2026-10-16"))
        self.assertIn("outro estado", M({"titulo": "MUNICIPIO DE NAZARENO — Pregão eletrônico para aquisição de equipamentos",
                                         "url": "https://pncp.gov.br/app/editais/18557561000151/2026/136", "uf": "MG"}, "2026-10-16"))
        self.assertEqual(M({"titulo": "x"}), "sem título")

    def test_limpar_base(self):
        r = Path(tempfile.mkdtemp()); (r / "biblioteca_alexandria/fontes").mkdir(parents=True)
        cat = r / "biblioteca_alexandria/fontes/motores.json"
        cat.write_text(json.dumps({"motores": [{"id": "l1", "historico": [{"pagina": "https://x.go.gov.br/edital-2024"}]}]}))
        base = r / "o.jsonl"
        base.write_text("\n".join(json.dumps(x) for x in [
            {"id": "a", "titulo": "Chamamento público de OSC 2026", "fim": "2026-12-01"},
            {"id": "b", "titulo": "Diário Oficial de X 2023 — edital", "url": "https://qd.org/x"},
            {"id": "c", "titulo": "Edital de fomento 2024", "url": "https://x.go.gov.br/edital-2024"},
            {"id": "d", "titulo": "Instituto abre vaga de estágio"}]) + "\n")
        with mock.patch.object(B, "CAT", cat):
            res = B.limpar_base_bruta(base)
        self.assertEqual([json.loads(l)["id"] for l in base.read_text().splitlines()], ["a", "c"])   # 'c' é histórico de livro
        self.assertEqual(res["removidas"], 2)


class Etapa3Leitores(unittest.TestCase):
    """16/10/2026: achados nos livros — primeiro fica, ordem de chegada, entrada sem oportunidade sai."""
    def test_achados_nos_livros(self):
        r = Path(tempfile.mkdtemp())
        for d in ("biblioteca_alexandria/fontes", "dados/oportunidades"):
            (r / d).mkdir(parents=True)
        cat = r / "biblioteca_alexandria/fontes/motores.json"; cat.write_text(json.dumps({"motores": []}))
        rep = r / "dados/oportunidades/repositorio_unico.json"
        with mock.patch.object(B, "ROOT", r), mock.patch.object(B, "CAT", cat), mock.patch.object(B, "INDICE", r / "i.json"):
            B.registrar_achados([{"id": "a", "titulo": "Chamamento OSC", "url": "https://x.go.gov.br/a", "sensor": "m1"},
                                 {"id": "z", "titulo": "Ruído", "url": "https://y.com/z", "sensor": "m1"}])
            B.registrar_achados([{"id": "a", "titulo": "Chamamento OSC (relido)", "url": "https://x.go.gov.br/a", "sensor": "m2"}])
            self.assertEqual([x["id"] for x in B.achados()], ["a", "z"])
            self.assertEqual(B.achados()[0]["titulo"], "Chamamento OSC")                    # o primeiro fica
            rep.write_text(json.dumps({"registros": [{"id": "a", "titulo": "Chamamento OSC", "url": "https://x.go.gov.br/a"}]}))
            res = B.consolidar()
            self.assertEqual(res["livros_de_entrada_removidos"], 1)                          # 'z' não virou oportunidade
            self.assertEqual([x["id"] for x in B.achados()], ["a"])


class MigracaoUnica(unittest.TestCase):
    def test_uma_vez(self):
        r = Path(tempfile.mkdtemp())
        for d in ("biblioteca_alexandria/fontes", "dados/oportunidades", "estado"):
            (r / d).mkdir(parents=True)
        cat = r / "biblioteca_alexandria/fontes/motores.json"; cat.write_text(json.dumps({"motores": []}))
        base = r / "dados/oportunidades/oportunidades.jsonl"
        base.write_text(json.dumps({"id": "a", "titulo": "Chamamento público de OSC", "url": "https://x.go.gov.br/a", "fim": "2099-01-01"}) + "\n")
        with mock.patch.object(B, "ROOT", r), mock.patch.object(B, "CAT", cat), mock.patch.object(B, "MARCO_MIGRACAO", r / "estado/livros_migracao.json"):
            self.assertEqual(B.migrar_se_preciso()["migracao"], "feita agora")
            self.assertEqual([x["id"] for x in B.achados()], ["a"])
            self.assertEqual(B.migrar_se_preciso()["migracao"], "já feita")


class LeituraUnicaNucleo(unittest.TestCase):
    """16/10/2026: carregar/gravar_oportunidades usam os livros depois da migração."""
    def test_nucleo(self):
        from src import nucleo as N
        r = Path(tempfile.mkdtemp())
        for d in ("biblioteca_alexandria/fontes", "dados/oportunidades", "estado"):
            (r / d).mkdir(parents=True)
        cat = r / "biblioteca_alexandria/fontes/motores.json"; cat.write_text(json.dumps({"motores": []}))
        base = r / "dados/oportunidades/oportunidades.jsonl"; base.write_text(json.dumps({"id": "velho", "titulo": "Base antiga"}) + "\n")
        with mock.patch.object(N, "ROOT", r), mock.patch.object(N, "DB_OPORTUNIDADES", base), mock.patch.object(B, "CAT", cat):
            self.assertEqual(list(N.carregar_oportunidades()), ["velho"])                   # antes da migração: a base
            (r / "estado/livros_migracao.json").write_text("{}")
            B.registrar_achados([{"id": "a", "titulo": "Chamamento OSC", "url": "https://x.go.gov.br/a"},
                                 {"id": "b", "titulo": "Fomento cultural", "url": "https://y.go.gov.br/b"}])
            regs = N.carregar_oportunidades()
            self.assertEqual(sorted(regs), ["a", "b"])                                         # depois: os livros
            regs["a"]["status"] = "verificada"; del regs["b"]; regs["c"] = {"id": "c", "titulo": "Novo", "url": "https://z.go.gov.br/c"}
            N.gravar_oportunidades(regs)
            depois = N.carregar_oportunidades()
            self.assertEqual(sorted(depois), ["a", "c"]); self.assertEqual(depois["a"]["status"], "verificada")
            self.assertEqual(base.read_text().count("\n"), 1)                                  # a base não foi regravada
