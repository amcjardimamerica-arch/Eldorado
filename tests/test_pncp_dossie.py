"""15/10/2026 (titular): dossiê do PNCP — 12/12 confirmados ou descarte justificado; dispensa só com fontes esgotadas."""
import json
import unittest

from src import pncp_dossie as P

API = "https://pncp.gov.br/api/consulta/v1/orgaos/11598317000198/compras/2026/36"
BASE = "https://pncp.gov.br/pncp-api/v1/orgaos/11598317000198/compras/2026/36"
URL = "https://pncp.gov.br/app/editais/11598317000198/2026/36"
META = {"situacaoCompraNome": "Divulgada no PNCP", "amparoLegal": {"nome": "Lei 13.019/2014, Art. 30, VI"},
        "orgaoEntidade": {"esferaId": "M", "razaoSocial": "MUNICIPIO DE INHUMAS"}, "unidadeOrgao": {"municipioNome": "Inhumas", "ufSigla": "GO"},
        "objetoCompra": "Credenciamento de OSC para termo de colaboração na assistência social", "dataAberturaProposta": "2026-10-01T08:00:00",
        "dataEncerramentoProposta": "2026-12-30T17:00:00", "valorTotalEstimado": 120000, "modalidadeNome": "Credenciamento"}
EDITAL = ("<html><body><p>EDITAL. 1. DO OBJETO 1.1 Credenciamento de OSC para celebração de Termo de Colaboração. 4.1. Poderão participar "
          "organizações da sociedade civil sediadas no município de Inhumas. O resultado será publicado no Diário Oficial do Município. "
          "6.2. O prazo recursal é de 3 (três) dias úteis. Área: assistência social.</p></body></html>")


class Rede:
    def __init__(self, mapa):
        self.m = mapa

    def get(self, u):
        v = self.m.get(u)
        if v is None:
            return None, "", "erro_rede: 404"
        return v.encode(), ("application/json" if v[:1] in "[{" else "text/html"), None


class Dossie(unittest.TestCase):
    def test_doze_de_doze_confirmados(self):
        r = Rede({API: json.dumps(META), BASE + "/arquivos": json.dumps([{"url": BASE + "/arquivos/1", "tipoDocumentoNome": "Edital"}]), BASE + "/arquivos/1": EDITAL})
        d = P.dossie({"id": "x", "titulo": "Credenciamento OSC Inhumas", "url": URL}, r, "2026-10-15")
        self.assertEqual((d["status"], d["faltam"]), ("completo", []))
        self.assertEqual(d["itens"]["Esfera"]["fonte"], "metadados oficiais do PNCP")
        self.assertTrue(all(v.get("trecho") and v.get("documento") for v in d["itens"].values()))

    def test_portoes(self):
        m = dict(META, amparoLegal={"nome": "Lei 14.133/2021, Art. 79"}, objetoCompra="Credenciamento de clínicas para exames laboratoriais")
        self.assertIn("não se aplica a associação", P.dossie({"id": "y", "titulo": "c", "url": URL}, Rede({API: json.dumps(m)}), "2026-10-15")["motivo"])
        m = dict(META, unidadeOrgao={"municipioNome": "Itapevi", "ufSigla": "SP"})
        self.assertIn("outro estado", P.dossie({"id": "z", "titulo": "t", "url": URL}, Rede({API: json.dumps(m)}), "2026-10-15")["motivo"])
        m = dict(META, situacaoCompraNome="Revogada")
        self.assertEqual(P.dossie({"id": "w", "titulo": "t", "url": URL}, Rede({API: json.dumps(m)}), "2026-10-15")["status"], "fechada")
        m = dict(META, unidadeOrgao={"municipioNome": "Recife", "ufSigla": "PE"})                 # capital: segue
        self.assertNotEqual(P.dossie({"id": "v", "titulo": "t", "url": URL}, Rede({API: json.dumps(m)}), "2026-10-15")["status"], "descartada")

    def test_sem_fontes_esgotadas_nada_e_dispensado_por_hipotese(self):
        d = P.dossie({"id": "u", "titulo": "Credenciamento OSC", "url": URL}, Rede({API: json.dumps(META)}), "2026-10-15")
        self.assertEqual(d["status"], "em trabalho")
        self.assertTrue(d["proximo"].startswith("Interceptador"))
        for v in d["dispensas"].values():
            self.assertTrue(v["fontes_consultadas"])                                              # dispensa sempre com as fontes


if __name__ == "__main__":
    unittest.main()


class PortaoDoMotorNoDossie(unittest.TestCase):
    def test_pregao_e_servico_saem_no_dossie(self):
        m = dict(META, modalidadeNome="Pregão - Eletrônico", objetoCompra="aquisição de equipamentos", amparoLegal={"nome": "Lei 14.133/2021"})
        self.assertIn("licitação", P.dossie({"id": "p", "titulo": "Pregão", "url": URL}, Rede({API: json.dumps(m)}), "2026-10-15")["motivo"])
        m = dict(META, objetoCompra="Credenciamento de ILPI para acolhimento de idosos", amparoLegal={"nome": "Lei 14.133/2021, Art. 79"},
                 unidadeOrgao={"municipioNome": "Nova Santa Rita", "ufSigla": "RS"}, orgaoEntidade={"esferaId": "E", "razaoSocial": "ESTADO DO RS"})
        self.assertIn("fora de Goiás", P.dossie({"id": "q", "titulo": "Credenciamento ILPI", "url": URL}, Rede({API: json.dumps(m)}), "2026-10-15")["motivo"])
