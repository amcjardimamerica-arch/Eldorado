"""A Pertinência: decide se cada achado é oportunidade (pelo portão da missão) e mede a saída de cada etapa.

O motor não decide pertinência: ele entrega; a decisão é da base, com o motivo de toda recusa, e volta ao motor
como retorno (para ele aprender).
"""
from __future__ import annotations

from pathlib import Path
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
    if parametros.get("recuperar_pendentes"):                  # 29/10/2026: os achados órfãos voltam à decisão
        ja = {i.get("id") for i in itens}
        itens = list(itens) + [x for x in pendentes_sem_decisao(Path(parametros.get("dados", "dados")), int(parametros.get("recuperar_pendentes")))
                               if x["id"] not in ja]
    for item in itens:
        achado = msgspec.convert({k: v for k, v in item.items() if not k.startswith("_")}, Achado)
        r = p.decidir(achado)
        r.fonte = (achado.dados or {}).get("fonte")
        retornos.setdefault(achado.motor, []).append(r)
        if r.decisao == "aceito":
            aceitos.append(item)
    p.medir_etapa("coleta", len(itens), len(aceitos))
    if parametros.get("modulos"):                               # o retorno volta a cada motor, para ele aprender
        from ..nucleo.registro import carregar as carregar_registro
        registro = carregar_registro(parametros["modulos"])
        for motor, lista in retornos.items():
            if motor in registro.ids():
                m = registro.obter(motor)
                if hasattr(m, "estado"):                      # o aprendizado vai ao Cérebro pelo diário da execução
                    m.estado.diario = contexto.diario
                m.aprender(lista)
    return aceitos


def pendentes_sem_decisao(dados: Path, limite: int = 150) -> list[dict[str, Any]]:
    """29/10/2026 (titular: "todos os dados de livros devem ser gravados nos livros"): os achados gravados que ficaram sem
    decisão. O piloto grava o achado no próprio diário e o entrega à passagem; se a passagem é interrompida antes de
    terminar (uma implantação, o apagão da gravação), a regra R09 descarta a passagem inteira — a decisão junto — e o
    achado, já fora da fila de entregas, ficava órfão para sempre ("pendente": 334, desde 24/10), com a informação fora do
    livro. A cada passagem, até `limite` deles voltam à Pertinência (os mais antigos primeiro)."""
    import json
    import sqlite3

    arq = Path(dados) / "biblioteca.db"
    if not arq.exists():
        return []
    con = sqlite3.connect(f"file:{arq}?mode=ro", uri=True)
    try:
        linhas = con.execute(
            "SELECT id, motor, encontrado_em, link_divulgacao, link_oficial, titulo, publicado_em, dados, veio_de_copia_arquivada, pista "
            "FROM achado WHERE decisao = 'pendente' ORDER BY encontrado_em, rowid LIMIT ?", (limite,)).fetchall()
    except sqlite3.Error:
        return []
    finally:
        con.close()
    out = []
    for i, m, enc, div, ofi, tit, pub, dad, copia, pista in linhas:
        try:
            d = json.loads(dad or "{}")
        except ValueError:
            d = {}
        out.append({"id": i, "motor": m, "encontrado_em": enc or "", "link_divulgacao": div or ofi or "", "link_oficial": ofi, "titulo": tit,
                    "publicado_em": pub, "dados": d if isinstance(d, dict) else {}, "veio_de_copia_arquivada": bool(copia), "pista": bool(pista)})
    return out

