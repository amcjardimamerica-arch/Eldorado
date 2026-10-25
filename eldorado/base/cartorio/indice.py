"""O índice: cria o livro ou vincula ao existente pela chave da missão; reconhece o mesmo edital em canais diferentes.

A semelhança do título (MinHash, datasketch) só vincula quando a UF é a mesma: programas diferentes de estados
diferentes nunca são unidos por engano. Unir dois livros existentes registra a união; nenhum é apagado.
"""
from __future__ import annotations

import sqlite3
from typing import Any

from datasketch import MinHash, MinHashLSH

from ..missao.chave import normalizar
from ..nucleo.contratos import Achado, Missao
from ..nucleo.eventos import Diario, agora

LIMIAR = 0.8


def _minhash(texto: str) -> MinHash:
    """Semelhança pelas palavras do título normalizado (sem número do ato, ano e palavras vazias)."""
    m = MinHash(num_perm=128)
    for p in set(normalizar(texto).split()) or {""}:
        m.update(p.encode())
    return m


class Indice:
    def __init__(self, biblioteca: sqlite3.Connection | None, missao: Missao, diario: Diario, missao_id: str = "oportunidades"):
        self.missao, self.diario, self.missao_id = missao, diario, missao_id
        self._por_chave: dict[str, str] = {}
        self._por_titulo_link: dict[tuple[str, str], tuple[str, str | None]] = {}   # o mesmo título e o mesmo link: (livro, UF)
        self._uf: dict[str, str | None] = {}
        self._lsh = MinHashLSH(threshold=LIMIAR, num_perm=128)
        if biblioteca is not None:
            from .identidade import _link, titulo_normal
            for lid, t, lo, ld, uf in biblioteca.execute("SELECT id, titulo, link_oficial, link_divulgacao, uf FROM livro WHERE missao=? "
                                                         "AND situacao NOT IN ('excluido', 'unido')", (missao_id,)):
                for u in (lo, ld):
                    if u:
                        self._por_titulo_link.setdefault((titulo_normal(t), _link(u)), (lid, uf))
            for r in biblioteca.execute("SELECT id, chave, titulo, uf FROM livro WHERE missao=? AND situacao NOT IN ('excluido', 'unido')", (missao_id,)):
                self._lembrar(r[0], r[1], r[2] or "", r[3])

    def _lembrar(self, livro: str, chave: str, titulo: str, uf: str | None) -> None:
        self._por_chave[chave] = livro
        self._uf[livro] = uf
        if titulo and livro not in self._lsh:
            self._lsh.insert(livro, _minhash(titulo))

    def resolver(self, achado: Achado) -> tuple[str, bool, str]:
        """Devolve (livro, novo?, como). Grava a criação e o vínculo como eventos."""
        d = achado.dados or {}
        chave = self.missao.chave(achado)
        livro, como = self._por_chave.get(chave), "mesma chave"
        if livro is None and achado.titulo:                           # a oportunidade que já tem livro agrega a ele (24/10/2026)
            from .identidade import _link, titulo_normal
            t = titulo_normal(achado.titulo)
            for u in (achado.link_oficial, achado.link_divulgacao):
                achou = self._por_titulo_link.get((t, _link(u))) if u else None
                if achou and not (achou[1] and d.get("uf") and achou[1] != d.get("uf")):     # UFs diferentes nunca se unem
                    livro, como = achou[0], "a mesma oportunidade (o mesmo título e o mesmo link)"
                    break
        if livro is None and achado.titulo:
            for candidato in self._lsh.query(_minhash(achado.titulo)):
                if self._uf.get(candidato) and self._uf.get(candidato) == d.get("uf"):
                    livro, como = candidato, "mesmo edital em outro canal (título semelhante, mesma UF)"
                    break
        novo = livro is None
        if novo:
            livro, como = f"L-{chave[:16]}", "livro novo"
            self.diario.emitir("livro.criado", "indice", {
                "id": livro, "missao": self.missao_id, "chave": chave, "titulo": achado.titulo, "tema": d.get("tema") or d.get("area"),
                "orgao": d.get("orgao"), "uf": d.get("uf"), "link_divulgacao": achado.link_divulgacao, "link_oficial": achado.link_oficial,
                "estrela": "sem", "selo_livro": "sem", "informacoes_validadas": 0, "situacao": "em trabalho", "criado_em": agora(), "atualizado_em": agora()})
            self._lembrar(livro, chave, achado.titulo or "", d.get("uf"))
            from .identidade import _link, titulo_normal
            for u in (achado.link_oficial, achado.link_divulgacao):
                if u:
                    self._por_titulo_link.setdefault((titulo_normal(achado.titulo), _link(u)), (livro, d.get("uf")))
        self.diario.emitir("livro.vinculado", "indice", {"achado_id": achado.id, "livro_id": livro})
        return livro, novo, como

    def unir(self, fica: str, unido: str, motivo: str) -> None:
        self.diario.emitir("livro.unido", "indice", {"livro_que_fica": fica, "livro_unido": unido, "em": agora(), "motivo": motivo})


def linha(con: sqlite3.Connection, sql: str, *args: Any) -> list[dict[str, Any]]:
    con.row_factory = sqlite3.Row
    return [dict(r) for r in con.execute(sql, args)]
