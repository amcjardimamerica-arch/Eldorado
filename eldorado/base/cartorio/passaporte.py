"""O passaporte: move o livro entre as fases só com a autorização da Regência, e registra as tentativas (até 3)."""
from __future__ import annotations

import sqlite3

from ..cerebro.regencia import autorizar
from ..nucleo.eventos import Diario, agora

SITUACAO = {"analise externa": "verificacao externa", "farol": "transferido ao farol"}


class Passaporte:
    def __init__(self, biblioteca: sqlite3.Connection | None, diario: Diario, maximo: int = 3):
        self.con, self.diario, self.maximo = biblioteca, diario, maximo
        self._fase: dict[str, str | None] = {}
        self._tentativas: dict[tuple[str, str, str], int] = {}

    def fase(self, livro: str) -> str | None:
        if livro in self._fase:
            return self._fase[livro]
        if self.con is not None:
            r = self.con.execute("SELECT fase FROM passaporte WHERE livro_id=?", (livro,)).fetchone()
            if r:
                return r[0]
        return None

    def tentativas(self, livro: str, fase: str, ferramenta: str) -> int:
        k = (livro, fase, ferramenta)
        if k not in self._tentativas:
            n = 0
            if self.con is not None:
                n = self.con.execute("SELECT COUNT(*) FROM tentativa WHERE livro_id=? AND fase=? AND ferramenta=?", k).fetchone()[0]
            self._tentativas[k] = n
        return self._tentativas[k]

    def mover(self, livro: str, para: str, motivo: str = "") -> tuple[bool, str]:
        de = self.fase(livro)
        n = max((t for (lv, f, _), t in self._tentativas.items() if lv == livro and f == de), default=0)
        ok, porque = autorizar(de, para, n, self.maximo)
        if not ok:
            return False, porque
        self.diario.emitir("livro.passagem", "passaporte", {"livro_id": livro, "de": de, "para": para, "em": agora(),
                                                             "autorizado_por": "regencia", "motivo": motivo or porque})
        if para in SITUACAO:
            self.diario.emitir("livro.situacao", "passaporte", {"id": livro, "situacao": SITUACAO[para], "atualizado_em": agora()})
        self._fase[livro] = para
        return True, porque

    def tentar(self, livro: str, ferramenta: str, resultado: str, proxima_em: str | None = None) -> bool:
        """Registra uma tentativa na fase atual. Falso quando as 3 já se esgotaram (o livro deve seguir adiante)."""
        fase = self.fase(livro) or "coleta"
        n = self.tentativas(livro, fase, ferramenta)
        if n >= self.maximo:
            return False
        self._tentativas[(livro, fase, ferramenta)] = n + 1
        self.diario.emitir("tentativa.registrada", "passaporte", {"livro_id": livro, "fase": fase, "ferramenta": ferramenta, "numero": n + 1,
                                                                  "em": agora(), "resultado": resultado, "proxima_em": proxima_em})
        return True
