"""A Pertinência: decide se cada achado é oportunidade (pelo portão da missão) e mede a saída de cada etapa.

O motor não decide pertinência: ele entrega; a decisão é da base, com o motivo de toda recusa, e volta ao motor
como retorno (para ele aprender).
"""
from __future__ import annotations

from typing import Any

import msgspec

from ..nucleo.contratos import Achado, Missao, Retorno
from ..nucleo.eventos import Diario, agora
from ..nucleo.registro import instanciar


class Pertinencia:
    def __init__(self, missao: Missao, diario: Diario):
        self.missao = missao
        self.diario = diario

    def decidir(self, achado: Achado) -> Retorno:
        injecao = (achado.documento or {}).get("injecao")
        try:
            if injecao:                                              # reprovação automática, antes do portão
                aceito, motivo = False, f"reprovação automática: padrão de injeção de instruções no documento: “{str(injecao)[:200]}”"
            else:
                aceito, motivo = self.missao.portao(achado)
        except Exception as e:  # noqa: BLE001 — o portão com erro não aceita nem descarta: barra com o motivo e alarma
            aceito, motivo = False, f"erro no portão: {type(e).__name__}: {e}"
            self.diario.emitir("alarme.aberto", "pertinencia", {"gravidade": "alta", "modulo": "pertinencia", "mensagem": motivo, "aberto_em": agora()})
        decisao = "aceito" if aceito else "barrado"
        self.diario.emitir("pertinencia.decidida", "pertinencia", {"etapa": "coleta", "referencia": achado.id, "decisao": decisao,
                                                                   "motivo": motivo, "regra": None, "em": agora()})
        return Retorno(achado=achado.id, decisao=decisao, motivo=motivo)

    def medir_etapa(self, etapa: str, entrada: int, saida: int, devolvidos: int = 0) -> dict[str, Any]:
        """A saída de uma etapa: quanto do que entrou seguiu adiante (e quanto foi devolvido)."""
        valor = (saida / entrada) if entrada else None
        dados = {"marcador": f"etapa:{etapa}", "nivel": "componente", "em": agora(), "valor": valor,
                 "ponto": "v" if entrada else "c", "circulo": "c" if valor is None else ("v" if valor > 0 else "a"),
                 "linhas": "c", "motivo": f"entraram {entrada}, seguiram {saida}, devolvidos {devolvidos}"}
        self.diario.emitir("medicao.registrada", "pertinencia", dados)
        return dados


def no_decidir(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó do workflow: decide cada achado recebido; segue adiante só o que foi aceito."""
    p = Pertinencia(instanciar(parametros["missao"], parametros.get("missao_parametros")), contexto.diario)
    aceitos = []
    retornos: dict[str, list[Retorno]] = {}
    for item in itens:
        achado = msgspec.convert({k: v for k, v in item.items() if not k.startswith("_")}, Achado)
        r = p.decidir(achado)
        retornos.setdefault(achado.motor, []).append(r)
        if r.decisao == "aceito":
            aceitos.append(item)
    p.medir_etapa("coleta", len(itens), len(aceitos))
    if parametros.get("modulos"):                               # o retorno volta a cada motor, para ele aprender
        from ..nucleo.registro import carregar as carregar_registro
        registro = carregar_registro(parametros["modulos"])
        for motor, lista in retornos.items():
            if motor in registro.ids():
                registro.obter(motor).aprender(lista)
    return aceitos
