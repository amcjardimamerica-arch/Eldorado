"""A rede neural na fase 3 do Cartório (titular, 22/10/2026): quem age é a rede, não o Cartório.

Para cada livro na preparação (fase 3), na ordem do Cartório (as abertas que fecham antes primeiro), a rede decide:
  1. o MOTOR DA OPORTUNIDADE (o que trouxe o livro), uma pesquisa focada, uma vez por livro;
  2. o INTERCEPTADOR, uma abordagem por batimento (até as 10);
  3. esgotados os dois, a ANÁLISE EXTERNA (fase 5, o Claude no Chrome).
A informação nova volta ao livro como achado e passa pela Pertinência e pelo Cartório (fase 4, validação). O trabalho
anda pelo orçamento de tempo do batimento e continua no seguinte, até esgotar.
"""
from __future__ import annotations

import json
import sqlite3
import time
from datetime import date
from pathlib import Path
from typing import Any

import msgspec

from ..cartorio.passaporte import Passaporte
from ..nucleo.eventos import agora
from ..nucleo.registro import carregar as carregar_registro
from .regencia import _sem_paginas, achado_para_evento


def motores_do_livro(con: sqlite3.Connection, livro: str) -> list[str]:
    return [r[0] for r in con.execute("SELECT DISTINCT motor FROM achado WHERE livro_id=? AND motor <> 'interceptador' ORDER BY motor", (livro,))]


def ja_pesquisado(con: sqlite3.Connection, livro: str, motor: str) -> bool:
    return con.execute("SELECT 1 FROM tentativa WHERE livro_id=? AND fase='preparacao' AND ferramenta=?", (livro, f"motor {motor}")).fetchone() is not None


class Encaminhamento:
    def __init__(self, biblioteca: sqlite3.Connection, diario, registro, interceptador, rede=None):
        self.con, self.diario, self.registro, self.interceptador, self.rede = biblioteca, diario, registro, interceptador, rede
        self.passaporte = Passaporte(biblioteca, diario, maximo=10)

    def _entregar(self, a, quem: str) -> dict[str, Any]:
        doc = a.documento or {}
        self.diario.emitir("documento.registrado", quem, {"url": doc["url"], "sha256": doc["sha256"], "tipo": doc.get("tipo"),
             "paginas": len(doc.get("paginas") or []), "obtido_em": agora(), "oficial": int(bool(doc.get("oficial"))), "leitor": doc.get("leitor")})
        for i, texto in enumerate(doc.get("paginas") or [], 1):
            self.diario.emitir("pagina.gravada", quem, {"documento_sha256": doc["sha256"], "numero": i, "texto": texto})
        self.diario.emitir("achado.entregue", quem, achado_para_evento(a))
        return _sem_paginas(msgspec.to_builtins(a)) | {"documento": _sem_paginas(doc)}

    def encaminhar(self, lv) -> tuple[str, dict[str, Any] | None]:
        """Uma decisão da rede para um livro: quem age agora, e a informação nova (se veio)."""
        from ...motores.pilotos.interceptador import ORDEM
        vivo = {"link_oficial": lv.link_oficial, "estrela": lv.estrela, "faltam": lv.faltam}
        motores = [m for m in motores_do_livro(self.con, lv.id) if m in self.registro.ids() and not ja_pesquisado(self.con, lv.id, m)]
        abordagens = [n for n in ORDEM[lv.balcao] if n not in lv.tentadas]
        if self.rede is not None:                                   # a rede escolhe a ação de maior nota; a ordem do balcão desempata
            pos = {n: i for i, n in enumerate(ORDEM[lv.balcao])}
            abordagens.sort(key=lambda n: (-round(self.rede.nota_acao(f"abordagem {n}", vivo), 2), pos[n]))
            if motores and abordagens and self.rede.nota_acao("motor", vivo) < self.rede.nota_acao(f"abordagem {abordagens[0]}", vivo) - 0.1:
                motores = []                                        # a rede prefere o Interceptador agora (o motor fica para depois)
        for motor in motores:
            if True:
                m = self.registro.obter(motor)
                a = m.pesquisar({"id": lv.id, "titulo": lv.titulo, "link_oficial": lv.link_oficial, "link_divulgacao": lv.link_divulgacao}) \
                    if hasattr(m, "pesquisar") else None
                self.diario.emitir("tentativa.registrada", "rede", {"livro_id": lv.id, "fase": "preparacao", "ferramenta": f"motor {motor}", "numero": 1,
                                                                    "em": agora(), "resultado": json.dumps({"trouxe": bool(a), "faltam": lv.faltam}),
                                                                    "proxima_em": None})
                return f"motor {motor}", (self._entregar(a, motor) if a else None)
        r = self.interceptador.investigar(lv, abordagens if self.rede is not None else None)
        if r["esgotado"]:
            self.passaporte._tentativas[(lv.id, "preparacao", "rede")] = 0
            self.passaporte.mover(lv.id, "analise externa", "fase 5: a rede esgotou o motor da oportunidade e as abordagens do Interceptador")
            return "analise externa", None
        return f"interceptador · abordagem {r['abordagem']}", (self._entregar(r["achado"], "interceptador") if r["achado"] else None)

    def andar(self, orcamento_s: float, hoje: str | None = None) -> tuple[list[dict[str, Any]], dict[str, int]]:
        from ...motores.pilotos.interceptador import fila
        inicio, achados, contagem = time.monotonic(), [], {}
        livros = fila(self.con, hoje or date.today().isoformat())
        if self.rede is not None:                                   # dentro da mesma urgência, os mais promissores primeiro
            hj = hoje or date.today().isoformat()
            livros.sort(key=lambda x: (0 if (x.fim and x.fim >= hj) else 1, x.fim or "9999",
                                       -round(self.rede.nota_oportunidade({"titulo": x.titulo, "orgao": x.orgao, "link_oficial": x.link_oficial}), 2)))
        for lv in livros:
            if time.monotonic() - inicio > orcamento_s:
                break
            quem, a = self.encaminhar(lv)
            contagem[quem.split(" ·")[0].split(" ")[0]] = contagem.get(quem.split(" ·")[0].split(" ")[0], 0) + 1
            if a:
                achados.append(a)
        return achados, contagem


def no_encaminhar(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem: a rede neural encaminha os livros da fase 3 e devolve a informação nova (para a Pertinência)."""
    from ...motores.acesso.api import DegrauAPI
    from ...motores.acesso.escada import Escada
    from ...motores.acesso.leve import DegrauLeve
    from ...motores.pilotos.interceptador import Interceptador
    p = Path(parametros.get("dados", "dados")) / "biblioteca.db"
    if not p.exists():
        return []
    con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    try:
        escada = Escada([DegrauAPI(), DegrauLeve()], intervalo_padrao=float(parametros.get("intervalo_s", 1.0)), tentativas=1, tempo_limite=25)
        registro = carregar_registro(parametros.get("modulos", "config/modulos.toml"), contexto.diario)
        from .rede import RedeNeural
        cer = Path(parametros.get("dados", "dados")) / "cerebro.db"
        c = sqlite3.connect(f"file:{cer}?mode=ro", uri=True) if cer.exists() else None
        rede = RedeNeural.treinar(con, c) if c is not None else None
        if c is not None:
            c.close()
        from ..nucleo.ia import IA
        ia = IA()
        achados, contagem = Encaminhamento(con, contexto.diario, registro, Interceptador(con, contexto.diario, escada, ia=ia if ia.disponivel() else None),
                                           rede).andar(
            float(parametros.get("orcamento_s", 300)))
    finally:
        con.close()
    return achados
