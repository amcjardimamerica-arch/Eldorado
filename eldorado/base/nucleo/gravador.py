"""O gravador único: o único que escreve nos bancos.

Aplica cada evento aos bancos e tabelas indicados no catálogo:
- de forma atômica em cada banco (uma transação por evento e por banco);
- idempotente: cada aplicação fica registrada em `evento_aplicado`; reaplicar não duplica nada, e um evento
  aplicado só em parte (queda entre dois bancos) é completado na reaplicação;
- sem esconder recusas: se as regras do banco recusarem um evento, ele é registrado como recusado e um alarme
  é aberto; o gravador segue com os demais eventos;
- sem descartar dados em silêncio: coluna desconhecida é recusa, não é ignorada.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from typing import Any, Iterable

import msgspec
import zstandard

from ...banco._sqlite import colunas
from .contratos import Linhagem
from .eventos import CATALOGO, Alvo, Diario, Evento, agora


@dataclass
class Relatorio:
    aplicados: int = 0
    repetidos: int = 0
    recusados: list[tuple[str, str, str]] = field(default_factory=list)   # (evento, tipo, motivo)

    @property
    def ok(self) -> bool:
        return not self.recusados


class Gravador:
    def __init__(self, bancos: dict[str, sqlite3.Connection], diario: Diario | None = None):
        faltando = {"biblioteca", "especial", "cerebro"} - set(bancos)
        if faltando:
            raise ValueError(f"bancos ausentes: {', '.join(sorted(faltando))}")
        self.bancos = bancos
        self.diario = diario
        self._colunas: dict[tuple[str, str], set[str]] = {}
        self._zstd = zstandard.ZstdCompressor(level=3)

    # ------------------------------------------------------------ aplicação

    def aplicar(self, eventos: Iterable[Evento]) -> Relatorio:
        r = Relatorio()
        for ev in eventos:
            self._aplicar_evento(ev, r)
        return r

    def _aplicar_evento(self, ev: Evento, r: Relatorio) -> None:
        alvos = CATALOGO.get(ev.tipo)
        if alvos is None:
            self._recusar(ev, r, "tipo fora do catálogo")
            return
        for i, alvo in enumerate(alvos):
            if alvo.operacao == "expandir":
                self._expandir(ev, r)
                continue
            con = self.bancos[alvo.banco]
            chave = f"{ev.id}#{i}"
            try:
                con.execute("BEGIN IMMEDIATE")
                if con.execute("SELECT 1 FROM evento_aplicado WHERE id=?", (chave,)).fetchone():
                    con.execute("ROLLBACK")
                    r.repetidos += 1
                    continue
                dados = alvo.mapa(ev.dados) if alvo.mapa else dict(ev.dados)
                self._executar(con, alvo, dados)
                con.execute("INSERT INTO evento_aplicado(id, tipo, aplicado_em) VALUES (?,?,?)", (chave, ev.tipo, agora()))
                con.execute("COMMIT")
                r.aplicados += 1
            except (sqlite3.Error, KeyError, ValueError, TypeError) as e:
                if con.in_transaction:
                    con.execute("ROLLBACK")
                self._recusar(ev, r, f"{alvo.banco}.{alvo.tabela}: {type(e).__name__}: {e}")

    def _executar(self, con: sqlite3.Connection, alvo: Alvo, dados: dict[str, Any]) -> None:
        if alvo.operacao == "pagina":
            self._pagina(con, dados)
            return
        cols = self._cols(alvo.banco, alvo.tabela)
        desconhecidas = set(dados) - cols
        if desconhecidas:
            raise ValueError(f"colunas desconhecidas: {', '.join(sorted(desconhecidas))}")
        dados = {k: (msgspec.json.encode(v).decode() if isinstance(v, (dict, list)) else v) for k, v in dados.items()}
        nomes = list(dados)
        if alvo.operacao == "inserir":
            con.execute(f"INSERT INTO {alvo.tabela} ({', '.join(nomes)}) VALUES ({', '.join('?' * len(nomes))})", list(dados.values()))
        elif alvo.operacao == "atualizar":
            falta = [c for c in alvo.chave if c not in dados]
            if falta:
                raise ValueError(f"chave ausente: {', '.join(falta)}")
            muda = [c for c in nomes if c not in alvo.chave]
            if not muda:
                raise ValueError("nada a atualizar")
            cur = con.execute(f"UPDATE {alvo.tabela} SET {', '.join(f'{c}=?' for c in muda)} WHERE {' AND '.join(f'{c}=?' for c in alvo.chave)}",
                              [dados[c] for c in muda] + [dados[c] for c in alvo.chave])
            if cur.rowcount == 0:
                raise ValueError(f"linha não encontrada em {alvo.tabela} para {dict((c, dados[c]) for c in alvo.chave)}")
        elif alvo.operacao == "inserir_ou_atualizar":
            muda = [c for c in nomes if c not in alvo.chave]
            conflito = f"ON CONFLICT ({', '.join(alvo.chave)}) DO " + (f"UPDATE SET {', '.join(f'{c}=excluded.{c}' for c in muda)}" if muda else "NOTHING")
            con.execute(f"INSERT INTO {alvo.tabela} ({', '.join(nomes)}) VALUES ({', '.join('?' * len(nomes))}) {conflito}", list(dados.values()))
        else:
            raise ValueError(f"operação desconhecida: {alvo.operacao}")

    def _pagina(self, con: sqlite3.Connection, d: dict[str, Any]) -> None:
        """O texto literal da página: comprimido com zstd e indexado na busca, sem uma segunda cópia do texto."""
        texto = d["texto"]
        con.execute("INSERT INTO pagina(documento_id, numero, texto_zstd, caracteres, expurgado) VALUES (?,?,?,?,?)",
                    (d["documento_id"], d["numero"], self._zstd.compress(texto.encode("utf-8")), len(texto), int(d.get("expurgado", 0))))
        rowid = con.execute("INSERT INTO busca_mapa(documento_id, numero) VALUES (?,?)", (d["documento_id"], d["numero"])).lastrowid
        con.execute("INSERT INTO busca(rowid, texto) VALUES (?,?)", (rowid, texto))

    def _expandir(self, ev: Evento, r: Relatorio) -> None:
        """Um lote (migração): cada evento interno recebe um identificador derivado e estável, para a reaplicação."""
        for n, item in enumerate(ev.dados.get("eventos", [])):
            interno = Evento(id=f"{ev.id}/{n:06d}", tipo=item["tipo"], modulo=item.get("modulo", ev.modulo), em=ev.em,
                             dados=item["dados"], linhagem=Linhagem(**item.get("linhagem", {})))
            self._aplicar_evento(interno, r)

    # ------------------------------------------------------------ recusas e alarmes

    def _recusar(self, ev: Evento, r: Relatorio, motivo: str) -> None:
        r.recusados.append((ev.id, ev.tipo, motivo))
        if ev.tipo == "alarme.aberto":
            return                                  # nunca entra em laço de alarmes
        dados = {"gravidade": "alta", "modulo": "gravador", "mensagem": f"evento recusado ({ev.tipo}, {ev.id}): {motivo}"[:2000],
                 "aberto_em": agora()}
        alarme = (self.diario.emitir("alarme.aberto", "gravador", dados) if self.diario
                  else Evento(id=f"{ev.id}!alarme", tipo="alarme.aberto", modulo="gravador", em=agora(), dados=dados))
        self._aplicar_evento(alarme, Relatorio())

    def _cols(self, banco: str, tabela: str) -> set[str]:
        k = (banco, tabela)
        if k not in self._colunas:
            self._colunas[k] = colunas(self.bancos[banco], tabela)
            if not self._colunas[k]:
                raise ValueError(f"tabela inexistente: {banco}.{tabela}")
        return self._colunas[k]
