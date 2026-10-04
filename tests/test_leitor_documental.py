import unittest

from src import leitor_documental as ld

DOC = "https://exemplo.go.gov.br/wp-content/uploads/2025/edital-01-2025.pdf"
DOC2 = "https://exemplo.go.gov.br/wp-content/uploads/2024/edital-02-2024.pdf"


def ed(ano, url, itens):
    return {"ano": ano, "mes": f"{ano}-03", "inicio": f"{ano}-03-01", "fim": f"{ano}-03-30", "titulo": "Edital",
            "documentos": [{"url": url, "tipo": "edital"}], "itens": itens}


class TesteLeitorDocumental(unittest.TestCase):
    def test_item_sem_trecho_ou_documento_vira_indicio(self):
        v = {"veredito": "ouro", "parecer": "ok", "edicoes": [
            ed(2025, DOC, {"Valor": {"valor": "R$ 1 mi", "trecho": "O valor total é de R$ 1.000.000,00", "documento": DOC},
                           "Objeto": {"valor": "x", "trecho": "", "documento": DOC}}), ed(2024, DOC2, {})]}
        limpo, rej = ld.validar_livro(v)
        e25 = [e for e in limpo["edicoes"] if e["ano"] == "2025"][0]
        self.assertIn("Valor", e25["itens12"]); self.assertNotIn("Objeto", e25["itens12"])
        self.assertTrue(any("indício" in r for r in rej)); self.assertEqual(limpo["veredito"], "ouro")

    def test_noticia_nao_vale_como_edicao(self):
        v = {"veredito": "ouro", "parecer": "ok", "edicoes": [{"ano": 2025, "documentos": [{"url": "https://x/noticia", "tipo": "noticia"}], "itens": {}}, ed(2024, DOC2, {})]}
        limpo, rej = ld.validar_livro(v)
        self.assertEqual(limpo["veredito"], "pendente"); self.assertEqual(len(limpo["edicoes"]), 1)

    def test_ouro_exige_dois_anos_e_inaplicavel_exige_prova(self):
        self.assertEqual(ld.validar_livro({"veredito": "ouro", "parecer": "p", "edicoes": [ed(2025, DOC, {})]})[0]["veredito"], "pendente")
        self.assertEqual(ld.validar_livro({"veredito": "inaplicavel", "parecer": "p", "motivo_inaplicavel": "curto"})[0]["veredito"], "pendente")
        self.assertEqual(ld.validar_livro({"veredito": "inaplicavel", "parecer": "p", "motivo_inaplicavel": "Notícia do Diário Oficial sem relação com entidades do terceiro setor."})[0]["veredito"], "inaplicavel")
        self.assertEqual(ld.validar_livro({"veredito": "ouro_regime", "parecer": "p"})[0]["veredito"], "pendente")


if __name__ == "__main__":
    unittest.main()
