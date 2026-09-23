"""O fechamento de 23/09/2026 — e a identidade de registro que ele consertou.

O TITULAR PEDIU "tudo fechado e pronto". Fechar exigiu tres coisas.

1. LER O QUE A NUVEM NAO ALCANCAVA. O PNCP so respondeu pelo navegador local do
   titular. Catorze registros foram lidos por la, um a um, na API oficial de
   consulta e na lista de arquivos do proprio orgao. Entre eles os cinco editais
   de Goias que nenhuma rodada anterior tinha verificado — todos encerrados, dois
   com homologacao ja publicada nos anexos — e a chave de Osorio/RS, que na base
   apontava para um registro inexistente (HTTP 400).

2. PARAR DE CONTAR O MESMO EDITAL DUAS VEZES. A base de oportunidades sempre
   truncou o id em oito caracteres; as bases de verificacao guardam a chave
   inteira de vinte. As duas grafias nunca se encontravam, e por isso sete
   editais existiam em duplicata na fila — o Instituto Impactarte, o Osorio/RS e
   mais cinco. Pior: vinte e sete registros ja verificados e fechados em 15/09
   continuavam aparecendo como "sem informacao", porque a verificacao nunca
   chegava neles. `chave_curta` e a correcao, e este arquivo cobra que nenhum
   prefixo de oito caracteres sirva a dois ids diferentes.

3. NAO CHAMAR DE REPROVACAO POR OBJETO O QUE E PRAZO VENCIDO. Vinte e quatro dos
   registros fechados em 15/09 tem natureza de fomento legitima e foram
   reprovados so por estarem fora do tempo. Somados aos que nao sao edital de
   fomento, davam ao titular a leitura errada do motor.

NADA AQUI INVENTA DATA. A regra do titular vale inteira: campo sem confirmacao
sai nulo, com o motivo escrito na observacao.
"""
import json
import re
import unittest
from datetime import date
from pathlib import Path

from src import abertos_sem_informacao as A
from src.nucleo import ID_LONGO, carregar_oportunidades, chave_curta

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/dados/verificacao_fechamento_2026-09-23.json"
HOJE = date(2026, 9, 23)


def _base() -> dict:
    return json.loads(BASE.read_text(encoding="utf-8"))


class TesteBaseDeFechamento(unittest.TestCase):
    """A base existe, tem forma conhecida e declara de onde cada dado veio."""

    def test_a_base_existe_e_tem_catorze_registros(self):
        d = _base()
        self.assertEqual(d["total"], 14)
        self.assertEqual(len(d["itens"]), 14)

    def test_todo_registro_declara_a_rota_e_a_data_da_leitura(self):
        for chave, item in _base()["itens"].items():
            self.assertIn("navegador", (item.get("rota_usada") or "").lower(), chave)
            self.assertEqual(item.get("verificado_em"), "2026-09-23", chave)

    def test_nenhuma_data_inventada(self):
        """Data presente e data ISO completa; data ausente e nula, nunca estimada."""
        iso = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        for chave, item in _base()["itens"].items():
            for campo in ("inicio", "fim"):
                valor = item.get(campo)
                self.assertTrue(valor is None or iso.match(str(valor)),
                                f"{chave}.{campo} = {valor!r}")

    def test_veredito_e_prazo_usam_vocabulario_fechado(self):
        for chave, item in _base()["itens"].items():
            self.assertIn(item.get("veredito"), {"aprovado", "atencao", "reprovado"}, chave)
            self.assertIn(item.get("prazo_situacao"), {"aberto", "encerrado"}, chave)

    def test_os_cinco_editais_de_goias_estao_todos_encerrados(self):
        """Nenhum deles rendia inscricao — era o que faltava saber."""
        goias = [i for i in _base()["itens"].values() if i.get("uf") == "GO"]
        self.assertGreaterEqual(len(goias), 5)
        for item in goias:
            self.assertEqual(item.get("prazo_situacao"), "encerrado", item.get("orgao"))

    def test_a_chave_de_osorio_foi_corrigida(self):
        """A base apontava 88866396000155/2026/122, que devolve HTTP 400."""
        osorio = next(i for i in _base()["itens"].values() if i.get("orgao", "").endswith("OSORIO"))
        self.assertEqual(osorio["chave_pncp"]["cnpj"], "88814181000130")
        self.assertEqual(osorio["chave_pncp"]["seq"], 450)


class TestePaginaOficialDosAbertos(unittest.TestCase):
    """Registro em aberto tem que ter pagina oficial de verdade — a do orgao."""

    def test_todo_registro_aberto_aponta_para_arquivo_do_proprio_orgao(self):
        abertos = [i for i in _base()["itens"].values() if i.get("prazo_situacao") == "aberto"]
        self.assertEqual(len(abertos), 7)
        for item in abertos:
            oficial, _ = A.e_pagina_oficial(item["pagina_oficial"])
            self.assertTrue(oficial, item.get("orgao"))
            self.assertIn("/arquivos/", item["pagina_oficial"], item.get("orgao"))

    def test_a_origem_do_arquivo_fica_declarada(self):
        """A regra do titular de 08/09: o arquivo do orgao vale, com a origem dita."""
        for item in _base()["itens"].values():
            if item.get("prazo_situacao") != "aberto":
                continue
            self.assertIn("ORIGEM DECLARADA", item.get("observacao") or "", item.get("orgao"))
            arquivo = item.get("arquivo_do_orgao") or {}
            self.assertTrue(arquivo.get("uri"), item.get("orgao"))
            self.assertTrue(arquivo.get("titulo"), item.get("orgao"))

    def test_a_pagina_de_divulgacao_fica_guardada_mas_nao_vale_como_fonte(self):
        for item in _base()["itens"].values():
            divulgacao = item.get("pagina_divulgacao")
            if not divulgacao:
                continue
            self.assertIn("/app/editais/", divulgacao)
            oficial, _ = A.e_pagina_oficial(divulgacao)
            self.assertFalse(oficial, divulgacao)


class TesteChaveCurta(unittest.TestCase):
    """As duas grafias do mesmo id voltam a ser o mesmo registro."""

    def test_id_longo_e_id_curto_apontam_para_o_mesmo_registro(self):
        self.assertEqual(chave_curta("ea14b1b3f360d2dc8637"), chave_curta("ea14b1b3"))
        self.assertEqual(chave_curta("81a444690ae9d6a7fc56"), "81a44469")

    def test_chave_escrita_a_mao_fica_inteira(self):
        """Oito caracteres de 'planaltina-esporte-2026' nao identificam nada."""
        for chave in ("planaltina-esporte-2026", "emenda-estadual-go-2026", "janela-rouanet-2026"):
            self.assertEqual(chave_curta(chave), chave)

    def test_valor_ausente_nao_quebra(self):
        self.assertEqual(chave_curta(None), "")
        self.assertEqual(chave_curta(""), "")

    def test_nenhum_prefixo_de_oito_serve_a_dois_ids_diferentes(self):
        """Truncar so e seguro enquanto isso for verdade. Se deixar de ser, quebra aqui."""
        por_prefixo: dict = {}
        ids = {str(i) for i in carregar_oportunidades()}
        for caminho in A.BASES_VERIFICADAS:
            if not caminho.exists():
                continue
            itens = json.loads(caminho.read_text(encoding="utf-8")).get("itens") or {}
            ids.update(itens if isinstance(itens, dict)
                       else (str(x.get("id", "")) for x in itens))
        for identificador in ids:
            if ID_LONGO.match(identificador):
                por_prefixo.setdefault(identificador[:8], set()).add(identificador)
        colisoes = {p: v for p, v in por_prefixo.items() if len(v) > 1}
        self.assertEqual(colisoes, {}, f"prefixo de oito caracteres em disputa: {colisoes}")

    def test_a_verificacao_alcanca_o_registro_gravado_com_a_chave_inteira(self):
        """O teste que teria pego a duplicata: a base de fechamento usa vinte."""
        indice = A._verificadas()
        for chave in indice:
            self.assertFalse(ID_LONGO.match(chave) and len(chave) > 8,
                             f"chave nao normalizada no indice: {chave}")
        self.assertIn("81a44469", indice)
        self.assertIn("77be3a1f", indice)


class TesteMotivoDaReprovacao(unittest.TestCase):
    """Prazo vencido nao e reprovacao por objeto."""

    def test_prazo_encerrado_e_reprovacao_temporal(self):
        for familia in ("prazo encerrado em 02/10/2025",
                        "edital ja julgado — homologacao publicada nos anexos",
                        "edital já julgado, homologado e adjudicado",
                        "prazo encerrado em 07/01/2025, ha mais de vinte meses"):
            self.assertEqual(A.motivo_da_reprovacao(familia), "reprovado_por_prazo_vencido", familia)

    def test_objeto_alheio_ao_fomento_continua_reprovacao_por_objeto(self):
        for familia in ("servico_ao_orgao", "compra_publica", "credenciamento de prestador",
                        "busca_patrocinador", "destinado_a_pessoa_fisica"):
            self.assertEqual(A.motivo_da_reprovacao(familia), "reprovado_por_objeto", familia)

    def test_familia_vazia_nao_quebra(self):
        self.assertEqual(A.motivo_da_reprovacao(None), "reprovado_por_objeto")
        self.assertEqual(A.motivo_da_reprovacao(""), "reprovado_por_objeto")


class TesteMecanismoPermanente(unittest.TestCase):
    """Quem tem porta de entrada, e nao prazo, nao pode aparecer como 'falta prazo'."""

    def test_reconhece_os_mecanismos_sem_prazo(self):
        for objeto in ("Emenda Parlamentar Estadual — Goias — captacao 2026",
                       "destinacao de prestacoes pecuniarias pela Vara de Execucao Penal",
                       "inscricao em fluxo continuo, a qualquer tempo",
                       "Doacao de mercadorias apreendidas — Receita Federal",
                       "cadastro de proponente para a janela orcamentaria"):
            self.assertTrue(A.e_mecanismo_permanente({"objeto": objeto}), objeto)

    def test_nao_confunde_edital_com_prazo(self):
        for objeto in ("CHAMAMENTO PUBLICO para selecao de OSC, inscricoes ate 25/09/2026",
                       "Termo de Colaboracao com organizacao da sociedade civil"):
            self.assertFalse(A.e_mecanismo_permanente({"objeto": objeto}), objeto)


class TesteColapsoDosPermanentes(unittest.TestCase):
    """Uma porta de entrada aparece uma vez, com todos os endereços que tem."""

    def test_capturas_repetidas_viram_uma_porta_so(self):
        capturas = [
            {"id": "a1", "titulo": "Patrocinio a projetos culturais", "orgao": None,
             "pagina_oficial": "https://www.bndes.gov.br/patrocinios"},
            {"id": "b2", "titulo": "Patrocinio a projetos culturais", "orgao": None,
             "pagina_oficial": "https://www.bndes.gov.br/patrocinios"},
        ]
        saida = A.colapsar_permanentes(capturas)
        self.assertEqual(len(saida), 1)
        self.assertEqual(sorted(saida[0]["capturado_como"]), ["a1", "b2"])
        self.assertEqual(saida[0]["portas"], ["https://www.bndes.gov.br/patrocinios"])
        self.assertNotIn("conferir_porta", saida[0])

    def test_endereco_divergente_nao_e_descartado_e_fica_marcado(self):
        """O Instituto Impactarte chegou por .com.br e por .org.br."""
        capturas = [
            {"id": "a1", "titulo": "Instituto Impactarte", "orgao": "Instituto Impactarte",
             "pagina_oficial": "https://impactarte.com.br"},
            {"id": "b2", "titulo": "Instituto Impactarte", "orgao": "Instituto Impactarte",
             "pagina_oficial": "https://www.impactarte.org.br/cadastro-proponente"},
        ]
        saida = A.colapsar_permanentes(capturas)
        self.assertEqual(len(saida), 1)
        self.assertEqual(len(saida[0]["portas"]), 2, "nenhum endereco pode sumir")
        self.assertIn("confirmar", saida[0]["conferir_porta"])

    def test_portas_diferentes_do_mesmo_orgao_nao_se_misturam(self):
        """O BNDES tem duas portas distintas; colapsar as duas seria perder uma."""
        capturas = [
            {"id": "a1", "titulo": "Patrocinio a projetos culturais", "orgao": None,
             "pagina_oficial": "https://www.bndes.gov.br/patrocinios"},
            {"id": "b2", "titulo": "Selecao Publica de Projetos para Patrocinio Cultural 01/2025",
             "orgao": None, "pagina_oficial": "https://www.bndes.gov.br/selecao-01-2025"},
        ]
        self.assertEqual(len(A.colapsar_permanentes(capturas)), 2)

    def test_a_saida_real_conta_capturas_e_portas_separadamente(self):
        saida = json.loads((ROOT / "docs/dados/abertos_sem_informacao.json").read_text(encoding="utf-8"))
        bloco = saida["resumo"]["mecanismos_permanentes"]
        self.assertEqual(bloco["total"], len(bloco["itens"]))
        self.assertGreaterEqual(bloco["capturas"], bloco["total"])
        for item in bloco["itens"]:
            self.assertTrue(item["capturado_como"], item.get("titulo"))

    def test_nenhum_mecanismo_permanente_sobrou_na_fila(self):
        saida = json.loads((ROOT / "docs/dados/abertos_sem_informacao.json").read_text(encoding="utf-8"))
        for item in saida["itens"]:
            self.assertFalse(A.e_mecanismo_permanente(item),
                             f"porta de entrada cobrada como prazo: {item.get('id_curto')}")


class TesteFilaFechada(unittest.TestCase):
    """O estado que o titular pediu: nada em aberto sem informacao."""

    def test_nenhum_registro_em_aberto_ficou_sem_informacao(self):
        saida = json.loads((ROOT / "docs/dados/abertos_sem_informacao.json").read_text(encoding="utf-8"))
        abertos = [x for x in saida["itens"] if x.get("situacao") == "aberto"]
        self.assertEqual(abertos, [], "edital com prazo aberto ainda sem objeto, prazo ou pagina")

    def test_o_que_resta_na_fila_e_so_o_que_ninguem_confirmou_prazo(self):
        saida = json.loads((ROOT / "docs/dados/abertos_sem_informacao.json").read_text(encoding="utf-8"))
        for item in saida["itens"]:
            self.assertEqual(item.get("situacao"), "sem_prazo_confirmado", item.get("id_curto"))

    def test_a_base_de_fechamento_e_a_primeira_das_bases_verificadas(self):
        """A mais recente vence — e ela que corrige a chave de Osorio."""
        self.assertEqual(A.BASES_VERIFICADAS[0].name, "verificacao_fechamento_2026-09-23.json")


if __name__ == "__main__":
    unittest.main()


class TesteLimpezaDosDiarios(unittest.TestCase):
    """Edição de diário não é oportunidade: é matéria-prima. Eram 18.456 das 19.172 fichas —
    96% da Biblioteca — e faziam cada varredura passar por elas de novo."""

    def test_a_biblioteca_nao_guarda_mais_edicao_de_diario(self):
        import json as _j
        op = ROOT / "biblioteca_alexandria/oportunidades"
        diarios = 0
        for f in op.glob("*/*/ficha.json"):
            try:
                if _j.loads(f.read_text(encoding="utf-8")).get("fonte_id") == "querido-diario":
                    diarios += 1
            except Exception:
                pass
        self.assertEqual(diarios, 0)
        self.assertLess(len(list(op.glob("*/*/ficha.json"))), 1200)   # era 19.172

    def test_o_indice_guarda_o_endereco_para_voltar(self):
        import json as _j
        i = _j.loads((ROOT / "dados/editais/indice_diarios.json").read_text(encoding="utf-8"))
        self.assertGreater(i["total"], 15000)
        self.assertIn("matéria-prima", i["porque_sairam_da_biblioteca"])
        self.assertIn("Diário nunca é fonte de prazo", i["como_voltar"])
        com_url = [v for v in i["itens"].values() if v.get("url")]
        self.assertGreater(len(com_url), 15000)                       # dá para voltar a cada uma

    def test_o_que_serve_continua_na_biblioteca(self):
        import json as _j
        fontes = set()
        for f in (ROOT / "biblioteca_alexandria/oportunidades").glob("*/*/ficha.json"):
            try:
                fontes.add(_j.loads(f.read_text(encoding="utf-8")).get("fonte_id"))
            except Exception:
                pass
        for f in ("pncp", "observatorio-3setor", "abcr"):
            self.assertIn(f, fontes, f)


class TesteLeiturasLocaisAplicadas(unittest.TestCase):
    """O pacote trouxe o arquivo com as 14 leituras do navegador local. Copiá-lo para
    docs/dados não faz nada: o motor lê os REGISTROS. Enquanto a leitura não descer até
    eles, a próxima varredura reverifica o que o titular já verificou à mão."""

    @classmethod
    def setUpClass(cls):
        import json as _j
        cls.an = _j.loads((ROOT / "dados/editais/analises.json").read_text(encoding="utf-8"))
        cls.reg = _j.loads((ROOT / "estado/leituras_locais_23_09_aplicadas.json").read_text(encoding="utf-8"))

    def test_as_catorze_desceram_aos_registros(self):
        self.assertEqual(self.reg["aplicadas"], 14)
        self.assertEqual(self.reg["com_hora"], 14)
        com_hora = [v for v in self.an.values() if isinstance(v, dict) and v.get("hora_encerramento")]
        self.assertGreaterEqual(len(com_hora), 14)

    def test_a_hora_decide_se_ainda_esta_aberto(self):
        """Formosa encerrou 22/07 às 16h45, não 'em 22/07'."""
        f = next(v for v in self.an.values() if isinstance(v, dict)
                 and "FORMOSA" in str(v.get("orgao", "")).upper())
        self.assertEqual(f["hora_encerramento"], "16:45")
        self.assertEqual(f["fim"], "2026-07-22")

    def test_a_pagina_oficial_e_a_do_orgao_nao_a_divulgacao(self):
        for v in self.an.values():
            if isinstance(v, dict) and v.get("verificado_por", "").startswith("navegador local"):
                self.assertIn("divulgação do PNCP", v["divulgacao_nao_vale"])
                self.assertIn("nunca para confirmar prazo", v["divulgacao_nao_vale"])

    def test_a_chave_de_osorio_foi_trocada_em_todo_lugar(self):
        """A chave antiga devolvia HTTP 400. Trocar só numa base deixaria as outras
        apontando para o vazio, e a varredura seguinte voltaria a usar a errada."""
        import json as _j
        o = self.an["81a444690ae9d6a7fc56"]
        self.assertIn("88814181000130", str(o["chave_pncp"]))
        self.assertIn("88866396000155", o["chave_pncp_anterior"])
        self.assertIn("HTTP 400", o["porque_mudou"])
        self.assertEqual(self.reg["corrigiu_chave"], ["81a44469"])

        # e em nenhum arquivo a chave velha sobra como ponteiro ativo
        def ativos(o, cam=""):
            s = []
            if isinstance(o, dict):
                for k, v in o.items():
                    s += ativos(v, f"{cam}.{k}")
            elif isinstance(o, list):
                for i, v in enumerate(o):
                    s += ativos(v, f"{cam}[{i}]")
            elif "88866396000155" in str(o):
                s.append(cam)
            return s
        for arq in ("dados/editais/analises.json", "dados/editais/marcacoes_ia.json"):
            campos = ativos(_j.loads((ROOT / arq).read_text(encoding="utf-8")))
            vivos = [c for c in campos
                     if not any(x in c for x in ("anterior", "porque_mudou", "observacao"))]
            self.assertEqual(vivos, [], f"{arq}: {vivos[:2]}")

    def test_os_dois_registros_novos_de_planaltina_entraram(self):
        for k in ("planaltina-esporte-2026", "planaltina-cultura-2025"):
            self.assertIn(k, self.an, k)
            self.assertIn("registro novo", self.an[k]["origem"])
        self.assertEqual(sorted(self.reg["novos"]),
                         ["planaltina-cultura-2025", "planaltina-esporte-2026"])

    def test_chave_escrita_a_mao_nao_e_truncada(self):
        """Sem isto, 'planaltina-esporte-2026' viraria 'planalti' e colidiria com qualquer
        outro registro de Planaltina."""
        from src.nucleo import chave_curta
        self.assertEqual(chave_curta("planaltina-esporte-2026"), "planaltina-esporte-2026")
        self.assertEqual(chave_curta("81a444690ae9d6a7fc56"), "81a44469")
