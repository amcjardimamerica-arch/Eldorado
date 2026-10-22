"""Um motor de teste que entrega um edital real de Goiás (com o documento) e uma licitação (que o portão deve barrar)."""
from eldorado.base.nucleo.contratos import Achado, Descricao, Motor, Saude


class MotorEdital(Motor):
    def descrever(self):
        return Descricao(id="do-goias", tipo="motor", parte="MOTORES", finalidade="editais de teste", metrica="achados")

    def saude(self):
        return Saude(ok=True)

    def planejar(self, plano):
        return []

    def buscar(self, plano):
        yield Achado(id="A-edital", motor="do-goias", encontrado_em="2026-10-20", publicado_em="2026-10-01", link_divulgacao="https://goias.gov.br/cultura/edital-3-2026",
                     link_oficial="https://goias.gov.br/cultura/edital-3-2026.pdf", titulo="Edital de Chamamento Público nº 3/2026 — Fomento a projetos culturais de organizações da sociedade civil",
                     dados={"uf": "GO", "orgao": "Secult"}, documento_sha256="sha-edital")
        yield Achado(id="A-licitacao", motor="do-goias", encontrado_em="2026-10-20", link_divulgacao="https://goias.gov.br/x",
                     titulo="CREDENCIAMENTO PÚBLICO, com o objetivo de realizar a Aquisição de Gêneros Alimentícios", dados={"uf": "GO"})

    def aprender(self, retornos):
        pass

    def painel(self):
        return {}
