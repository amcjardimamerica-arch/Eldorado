"""Módulos usados só pelos testes: motores e uma missão que cumprem os contratos."""
from eldorado.base.nucleo.contratos import Achado, Descricao, Missao, Motor, Saude


class MotorTeste(Motor):
    def __init__(self, id="motor-teste", ufs=("GO", "SP"), falhar=False):
        self.id, self.ufs, self.falhar = id, tuple(ufs), falhar
        self.retornos = []

    def descrever(self):
        return Descricao(id=self.id, tipo="motor", parte="MOTORES", finalidade="achar editais de teste", metrica="achados por janela", componente="Motores de teste")

    def saude(self):
        return Saude(ok=not self.falhar)

    def planejar(self, plano):
        return list(plano.alvos)

    def buscar(self, plano):
        if self.falhar:
            raise ConnectionError("fonte fora do ar (provocado)")
        for i, uf in enumerate(self.ufs):
            yield Achado(id=f"{self.id}-{plano.passagem[-6:]}-{i}", motor=self.id, encontrado_em="2026-10-22", link_divulgacao=f"https://fonte/{uf}/{i}",
                         titulo=f"Edital de fomento cultural {uf}", dados={"uf": uf})

    def aprender(self, retornos):
        self.retornos.extend(retornos)

    def painel(self):
        return {"retornos": len(self.retornos)}


class MissaoTeste(Missao):
    def descrever(self):
        return Descricao(id="missao-teste", tipo="missao", parte="BASE", finalidade="aceitar só Goiás", metrica="decisões corretas")

    def saude(self):
        return Saude(ok=True)

    def itens(self):
        return [{"codigo": "uf", "nome": "UF"}]

    def chave(self, achado):
        return achado.link_divulgacao

    def portao(self, achado):
        uf = achado.dados.get("uf")
        if uf == "QUEBRA":
            raise RuntimeError("portão quebrado (provocado)")
        return (uf == "GO", "Goiás" if uf == "GO" else f"fora do território: {uf}")
