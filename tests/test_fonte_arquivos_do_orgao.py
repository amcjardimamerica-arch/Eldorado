"""O arquivo do edital anexado pelo próprio órgão ao PNCP é fonte.

Correção de 09/09/2026. O módulo recusava qualquer download do PNCP, por
entender que o portal é só divulgação. A regra do titular foi afinada em 08/09:
o arquivo do edital do próprio órgão hospedado lá é documento oficial e vale,
com a origem declarada. E é exatamente ali que está o cronograma — a consulta
devolve a janela de proposta, que em credenciamento costuma ser um período de
fachada de dez anos, enquanto o edital traz "abertura do prazo de inscrições".
209 registros ficaram sem prazo por causa dessa recusa.
"""
import unittest
from unittest import mock

from src import fonte_edital


LISTA = [
    {"titulo": "ATO DA DISPENSA DE LICITACAO.", "uri": "https://pncp.gov.br/pncp-api/v1/x/arquivos/1"},
    {"titulo": "EDITAL__001.2026_CHAMAMENTO_QUALIFICACAO", "uri": "https://pncp.gov.br/pncp-api/v1/x/arquivos/3"},
    {"titulo": "ERRATA DO CRONOGRAMA", "uri": "https://pncp.gov.br/pncp-api/v1/x/arquivos/4"},
    {"titulo": "TERMO DE REVOGACAO", "uri": "https://pncp.gov.br/pncp-api/v1/x/arquivos/5"},
    {"titulo": "sem uri"},
]


class TesteArquivosDoOrgao(unittest.TestCase):
    def _lista(self):
        with mock.patch.object(fonte_edital, "_get", return_value=__import__("json").dumps(LISTA)):
            return fonte_edital._arquivos_do_orgao_no_pncp("00000000000191", "2026", "1", [])

    def test_edital_vem_com_prioridade_zero(self):
        arqs = self._lista()
        edital = [a for a in arqs if "EDITAL" in a["titulo"]][0]
        self.assertEqual(edital["prioridade"], 0)
        self.assertIn("origem declarada", edital["tipo"])

    def test_documento_sem_uri_e_descartado(self):
        self.assertEqual(len(self._lista()), 4)

    def test_revogacao_e_marcada(self):
        # Um edital revogado não é oportunidade, e isso não aparece em nenhum
        # outro campo do PNCP. Foi o caso de Porangatu/GO nesta rodada.
        arqs = self._lista()
        self.assertTrue([a for a in arqs if a["revogacao"]])
        self.assertTrue([a for a in arqs if a["errata"]])

    def test_erro_de_rede_nao_derruba_a_coleta(self):
        erros = []
        with mock.patch.object(fonte_edital, "_get", side_effect=OSError("timeout")):
            self.assertEqual(fonte_edital._arquivos_do_orgao_no_pncp("1", "2026", "1", erros), [])
        self.assertTrue(erros and "arquivos do órgão no PNCP" in erros[0])


class TesteRotaDecideAPagina(unittest.TestCase):
    def test_portal_de_noticia_e_recusado_pela_tabela_de_rotas(self):
        # Antes havia uma lista de domínios escrita na mão dentro do módulo.
        with mock.patch.object(fonte_edital, "_get", side_effect=OSError("bloqueado")):
            r = fonte_edital.obter_texto({"id": "teste-rota-noticia",
                                          "url": "https://captadores.org.br/editais/abc"})
        self.assertTrue(any("não serve como fonte" in e for e in r["erros"]))


if __name__ == "__main__":
    unittest.main()
