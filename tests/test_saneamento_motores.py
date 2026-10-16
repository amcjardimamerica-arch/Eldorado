"""Saneamento dos motores (10/10/2026) — regras medidas contra o gabarito da revisão da Parte 1 (Goiás).

O gabarito (tests/fixtures/gabarito_abertas_p1_go_2026_10_10.json) tem os 338 registros de Goiás lidos no documento
oficial, com o veredito humano. A regra inviolável: NENHUMA regra automática descarta, encerra ou marca como duplicata
um registro que a revisão achou vigente (ouro, prata, bronze) ou pendente.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from src import saneamento_motores as S

ROOT = Path(__file__).resolve().parents[1]
GAB = ROOT / "tests/fixtures/gabarito_abertas_p1_go_2026_10_10.json"
HOJE = date(2026, 10, 10)
UTEIS = ("ouro", "prata", "bronze", "pendente")


def _registros():
    g = json.loads(GAB.read_text(encoding="utf-8"))["itens"]
    regs, ver = [], {}
    for x in g:
        if not x.get("registro"):
            continue
        r = {k: v for k, v in x["registro"].items() if v is not None}
        r["id"] = x["id"]
        regs.append(r)
        ver[x["id"]] = x
    return regs, ver


class SemRevisaoHumana(unittest.TestCase):
    """As regras AUTOMÁTICAS sozinhas (sem o arquivo de vereditos)."""

    def setUp(self):
        self._v = S.VEREDITOS
        S.VEREDITOS = Path(tempfile.gettempdir()) / "nao_existe_vereditos.json"
        S.limpar_cache()
        self.regs, self.ver = _registros()
        self.dups = S.agrupar_duplicatas(self.regs)
        self.res = {r["id"]: S.sanear_registro(r, HOJE, self.dups) for r in self.regs}

    def tearDown(self):
        S.VEREDITOS = self._v
        S.limpar_cache()

    def test_nenhum_util_atingido(self):
        atingidos = []
        for rid, s in self.res.items():
            if self.ver[rid]["veredito"] in UTEIS:
                if s["descartar"] or s["ajustes"].get("tipo_registro") == "duplicata" or s["ajustes"].get("situacao") == "encerrada":
                    atingidos.append((rid[:8], self.ver[rid]["veredito"], s))
        self.assertEqual(atingidos, [], "regra automática atingiu oportunidade vigente/pendente")

    def test_ruido_da_lista_a_sai_da_caixa(self):
        ruido = [rid for rid in self.res if self.ver[rid]["lista"] == "A" and self.ver[rid]["veredito"] == "ruido"]
        tratados = [rid for rid in ruido if self.res[rid]["descartar"] or self.res[rid]["ajustes"].get("tipo_registro") in ("duplicata", "edicao_diario")]
        self.assertGreaterEqual(len(tratados) / len(ruido), 0.9, f"{len(tratados)} de {len(ruido)}")

    def test_edicoes_de_diario_reconhecidas(self):
        b = [rid for rid in self.res if self.ver[rid]["lista"] == "B"]
        ed = [rid for rid in b if self.res[rid]["ajustes"].get("tipo_registro") in ("edicao_diario", "duplicata") or str(self.res[rid]["descartar"] or "").startswith("M14")]
        self.assertGreaterEqual(len(ed) / len(b), 0.98)
        # 10/10 (titular, M14): edição sem ato no trecho é ELIMINADA no motor (antes ia ao histórico como encerrada)
        antigas = [rid for rid in b if self.res[rid]["ajustes"].get("situacao") == "encerrada" or str(self.res[rid]["descartar"] or "").startswith("M14")]
        self.assertGreaterEqual(len(antigas), 240)                     # 228 edições eram de 2021–2025 (e mais as de >120 dias)

    def test_ato_dentro_do_diario_nao_vira_edicao(self):
        # 53e16dff (Natal no Parque) tem a URL da edição, mas o título é do ATO — é ouro
        self.assertNotEqual(self.res["53e16dff2aeb300819dd"]["ajustes"].get("tipo_registro"), "edicao_diario")
        k = next(k for k in self.res if k.startswith("653ed858"))
        self.assertEqual(self.res[k]["ajustes"].get("tipo_registro"), "edicao_diario")

    def test_duplicatas_conhecidas(self):
        d = {k[:8]: v["canonico"][:8] for k, v in self.dups.items()}
        self.assertTrue({"ec450d5c", "8180983c"} & set(d), "aviso DOU × DOE de Goiatuba")
        self.assertEqual(d.get("16617718"), "121e6786", "duas notícias do mesmo edital de Senador Canedo")
        self.assertTrue({"b3e0dbe3", "a6b497ca"} & set(d), "edital e aviso 01/2026 da Secult")

    def test_pecas_de_edital(self):
        for t in ("ANEXO IX – MINUTA DO TERMO DE COLABORAÇÃO", "3ª Alteração do Cronograma, “Tabela 2”", "Retificação do Edital 3/2026"):
            self.assertTrue(S.eh_peca_de_edital(t), t)
        self.assertFalse(S.eh_peca_de_edital("Edital de Chamamento Público Nº 01/2026"))

    def test_territorio(self):
        self.assertEqual(self.res["b7aa39bfeae73ea37efd"]["ajustes"].get("nivel"), "federal")      # Anater
        for rid in ("8117447425a2e5d8dcde", "db79db77"):                                               # Bondinho (RJ), ArcelorMittal (SC)
            k = next(x for x in self.res if x.startswith(rid[:8]))
            self.assertIsNone(self.res[k]["ajustes"].get("uf", "GO"), rid)

    def test_pncp_prazo_suspeito(self):
        self.assertTrue(self.res["b5199edf43e7cbb8db7d"]["ajustes"].get("prazo_pncp_suspeito"))      # Pirenópolis: 2027 era do registro
        self.assertFalse(self.res["64b098a6f46de27ba9d0"]["ajustes"].get("prazo_pncp_suspeito"))     # Senador Canedo: 383 dias, legítimo

    def test_numeros_diferentes_nunca_fundem(self):
        regs = [{"id": "a1", "titulo": "Prefeitura de Cachoeira Alta — Edital nº 001/2026", "url": "https://diariooficial.abc.go.gov.br/x/1"},
                {"id": "a2", "titulo": "Prefeitura de Cachoeira Alta — Edital nº 002/2026", "url": "https://diariooficial.abc.go.gov.br/x/2"},
                {"id": "a3", "titulo": "AVISO DE CHAMADA PÚBLICA Nº 3/2026 - SCFV Prefeitura de Cafelândia", "url": "https://capitaai.com.br/a"},
                {"id": "a4", "titulo": "Aviso de Chamamento Público Nº 3/2026 - SVS/AP Superintendência", "url": "https://capitaai.com.br/b"},
                {"id": "a5", "titulo": "EXTRATO DE ACORDO DE COOPERAÇÃO TÉCNICA Nº 1.2026/AGEDOCE SEMAD", "url": "https://x.org/1"},
                {"id": "a6", "titulo": "EXTRATO DE ACORDO DE COOPERAÇÃO TÉCNICA Nº 7 /2026 AGEDOCE SEMAD", "url": "https://x.org/2"}]
        self.assertEqual(S.agrupar_duplicatas(regs), {})

    def test_url_canonica(self):
        self.assertEqual(S.url_canonica("https://www.institutoassai.org.br/?utm_source=assai&utm_medium=menu"),
                         S.url_canonica("https://institutoassai.org.br/"))

    def test_extrair_fim_so_encerra(self):
        self.assertEqual(S.extrair_fim("Inscrições abertas até 05/02/2026, pelo e-mail"), "2026-02-05")
        r = {"id": "z", "titulo": "Edital 9/2026", "evidencia": "propostas de 01/12/2026 a 20/12/2026", "url": "https://a.go.gov.br/e"}
        self.assertNotIn("situacao", S.sanear_registro(r, HOJE)["ajustes"])                         # futuro: não abre nada


class ComRevisaoHumana(unittest.TestCase):
    """Com biblioteca_alexandria/livros/_acervo/editais/vereditos_revisao.json, o veredito humano vence."""

    def setUp(self):
        S.limpar_cache()

    def test_vereditos_aplicados(self):
        if not S.VEREDITOS.exists():
            self.skipTest("vereditos ainda não importados")
        regs, ver = _registros()
        for r in regs:
            s = S.sanear_registro(r, HOJE)
            v = ver[r["id"]]["veredito"]
            if v in ("ruido", "fora_perfil"):
                self.assertTrue(s["descartar"], r["id"])
            elif v in UTEIS:
                self.assertFalse(s["descartar"], r["id"])
                self.assertNotEqual(s["ajustes"].get("situacao"), "encerrada", r["id"])


class Painel(unittest.TestCase):
    def test_painel_por_motor(self):
        S.limpar_cache()
        regs, _ = _registros()
        mantidos, rel = S.sanear_abertas(regs, HOJE)
        p = S.painel_qualidade(regs, mantidos, rel["descartes"], HOJE)
        nomes = {m["motor"] for m in p["motores"]}
        self.assertIn("Querido Diário — diários oficiais municipais", nomes)
        self.assertTrue(all("aproveitamento" in m for m in p["motores"]))


if __name__ == "__main__":
    unittest.main()


class TesteM14EdicaoSemAto(unittest.TestCase):
    """10/10/2026 (titular): edição de diário só passa se o trecho mostra ato de abertura para o terceiro setor."""
    def test_criterio(self):
        from src.saneamento_motores import ato_no_trecho, limpar_cache
        limpar_cache()
        self.assertTrue(ato_no_trecho("Chamamento Público nº 04/2026 Órgão Requisitante: Secretaria Municipal de Cultura, seleção de projetos culturais de agentes culturais")[0])
        self.assertTrue(ato_no_trecho("O CMDCA, com esteio na Lei nº 13.019, torna público o Edital de Chamamento Público para organizações da sociedade civil")[0])
        for t in ("ATO DE DECLARAÇÃO DE INEXIGIBILIDADE DE CHAMAMENTO PÚBLICO com a OSC",
                  "RESULTADO FINAL do Edital de Chamamento Público para organizações da sociedade civil",
                  "estrutura funcional da Administração Municipal, cria órgãos, cargos e funções",
                  "Edital de concurso público para provimento de cargos efetivos",
                  "Termo de Execução Cultural nº 01/2026, apoio financeiro a agentes culturais"):
            self.assertFalse(ato_no_trecho(t)[0], t)
