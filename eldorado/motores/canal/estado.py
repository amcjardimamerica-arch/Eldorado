"""O aprendizado de cada motor, entregue ao Cérebro (titular, 24/10/2026): NENHUM motor tem banco de dados. O motor só
LÊ o que o Cérebro já aprendeu (cerebro.db, tabelas motor_*, só leitura) e ENTREGA o que aprende como eventos
(motor.entregue, motor.fonte, motor.assinatura, motor.mapa, motor.alvo, motor.retorno), que o gravador registra no banco de
aprendizado do Cérebro, como os achados. Dentro da mesma execução, o que já foi entregue fica em memória (os eventos só são
aplicados no passo seguinte). Nada de livro: as entregas guardam a chave e o id do achado, nunca o achado.

Na cadeia, a Regência dá ao motor o diário da execução. Fora dela (experimentos, testes), a entrega passa pelo mesmo
gravador, na hora, sobre o Cérebro da pasta indicada.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


def caminho_do_cerebro(dados: str | Path) -> Path:
    """dados/motores (o parâmetro antigo) → dados/cerebro.db; outra pasta → <pasta>/cerebro.db."""
    p = Path(dados)
    if p.suffix == ".db":
        return p
    return (p.parent if p.name == "motores" else p) / "cerebro.db"


SQL_FONTES = """SELECT f.nome, f.leituras, f.sem_mudanca, f.achados,
  (SELECT COUNT(*) FROM motor_retorno r WHERE r.motor = f.motor AND r.fonte = f.nome AND r.decisao = 'aceito') AS aceitos,
  (SELECT COUNT(*) FROM motor_retorno r WHERE r.motor = f.motor AND r.fonte = f.nome AND r.decisao <> 'aceito') AS barrados,
  f.falhas, f.ultimo_erro, f.ultima, f.situacao FROM motor_fonte f WHERE f.motor = ? ORDER BY f.nome"""


class EstadoMotor:
    def __init__(self, cerebro: str | Path, motor: str = "motor", diario=None, especial: bool = False):
        self.caminho, self.motor, self.diario = caminho_do_cerebro(cerebro), motor, diario
        # "já entregue" só vale se o achado EXISTE na Biblioteca (24/10/2026: 199 entregas "fantasmas" de experimentos e
        # ciclos antigos travavam 9 motores; o Mapa da Cultura nunca mais entregava). O destino especial (empresas) não vira achado.
        bib = self.caminho.parent / "biblioteca.db"
        self._bib = sqlite3.connect(f"file:{bib}?mode=ro", uri=True, check_same_thread=False) if (bib.exists() and not especial) else None
        from ...banco.cerebro_db.esquema import abrir  # o esquema existe (as tabelas motor_*); o motor não escreve nele
        abrir(self.caminho).close()
        self.con = sqlite3.connect(f"file:{self.caminho}?mode=ro", uri=True, check_same_thread=False, timeout=60)
        self._entregues: set[str] = set()
        self._assinaturas: dict[str, str] = {}
        self._fontes: dict[str, dict[str, Any]] = {}
        self._mapa: dict[str, set[str]] = {}
        self._retornos: set[str] = set()
        self._entregue_fonte: dict[str, str] = {}

    # ---- a entrega ao Cérebro ----
    def _entregar(self, tipo: str, dados: dict[str, Any]) -> None:
        dados = {"motor": self.motor, **dados}
        if self.diario is not None:
            self.diario.emitir(tipo, self.motor, dados)
            return
        from ...banco.cerebro_db.esquema import abrir
        from ...base.nucleo.eventos import criar  # fora da cadeia: o mesmo gravador, na hora
        from ...base.nucleo.gravador import Gravador
        con = abrir(self.caminho)
        try:
            vazio = sqlite3.connect(":memory:")
            Gravador({"cerebro": con, "biblioteca": vazio, "especial": vazio}).aplicar([criar(tipo, self.motor, dados)])
        finally:
            con.close()

    def _um(self, sql: str, args: tuple = ()) -> Any:
        r = self.con.execute(sql, (self.motor, *args)).fetchone()
        return r

    # ---- assinaturas (vigilância) ----
    def assinatura(self, fonte: str) -> str | None:
        if fonte in self._assinaturas:
            return self._assinaturas[fonte]
        r = self._um("SELECT valor FROM motor_assinatura WHERE motor=? AND fonte=?", (fonte,))
        return r[0] if r else None

    def gravar_assinatura(self, fonte: str, valor: str, em: str) -> None:
        self._assinaturas[fonte] = valor
        self._entregar("motor.assinatura", {"fonte": fonte, "valor": valor, "em": em})

    # ---- o mapa do site original (domínios e URLs, nunca livros) ----
    def mapa_visto(self, dominio: str) -> set[str]:
        vistas = {r[0] for r in self.con.execute("SELECT url FROM motor_mapa_url WHERE motor=? AND dominio=?", (self.motor, dominio))}
        r = self._um("SELECT vistas FROM motor_mapa_dominio WHERE motor=? AND dominio=?", (dominio,))
        if r and r[0]:
            vistas |= set(json.loads(r[0]))
        return vistas | self._mapa.get(dominio, set())

    def mapa_verificado_em(self, dominio: str) -> str | None:
        r = self._um("SELECT verificado_em FROM motor_mapa_dominio WHERE motor=? AND dominio=?", (dominio,))
        return r[0] if r else None

    def marcar_mapa(self, dominio: str, urls: list[str], em: str) -> None:
        todas = self.mapa_visto(dominio) | set(urls)
        self._mapa[dominio] = todas
        self._entregar("motor.mapa", {"dominio": dominio, "verificado_em": em, "urls": len(urls), "vistas": json.dumps(sorted(todas))})

    # ---- os alvos (a previsão de edição se aprende pelos meses em que mudaram) ----
    def mudanca_do_alvo(self, alvo: str, em: str) -> None:
        self._entregar("motor.alvo", {"alvo": alvo, "em": em, "mes": int(em[5:7])})

    def meses_do_alvo(self, alvo: str) -> list[int]:
        return [r[0] for r in self.con.execute("SELECT DISTINCT mes FROM motor_alvo_mudanca WHERE motor=? AND alvo=? ORDER BY mes", (self.motor, alvo))]

    # ---- o que já foi entregue (a chave e o id do achado) ----
    def ja_entregue(self, chave: str) -> bool:
        if chave in self._entregues:
            return True
        r = self._um("SELECT achado FROM motor_entregue WHERE motor=? AND chave=?", (chave,))
        if r is None:
            return False
        if self._bib is not None and r[0]:
            try:
                if self._bib.execute("SELECT 1 FROM achado WHERE id = ?", (r[0],)).fetchone() is None:
                    return False                                   # a entrega fantasma: o achado não está na Biblioteca
            except sqlite3.Error:
                pass
        return True

    def marcar_entregue(self, chave: str, em: str, achado: str | None = None, fonte: str | None = None) -> None:
        if chave in self._entregues:
            return
        self._entregues.add(chave)
        if achado and fonte:
            self._entregue_fonte[achado] = fonte
        self._entregar("motor.entregue", {"chave": chave, "em": em, "achado": achado, "fonte": fonte})

    # ---- o rendimento de cada fonte ----
    def _fonte(self, nome: str) -> dict[str, Any]:
        if nome not in self._fontes:
            self.con.row_factory = sqlite3.Row
            r = self.con.execute("SELECT * FROM motor_fonte WHERE motor=? AND nome=?", (self.motor, nome)).fetchone()
            self.con.row_factory = None
            self._fontes[nome] = ({k: r[k] for k in r.keys()} if r else
                                  {"motor": self.motor, "nome": nome, "leituras": 0, "sem_mudanca": 0, "achados": 0, "aceitos": 0, "barrados": 0,
                                   "falhas": 0, "ultimo_erro": None, "ultima": None, "situacao": None})
        return self._fontes[nome]

    def leitura(self, fonte: str, em: str, achados: int = 0, sem_mudanca: bool = False, erro: str | None = None) -> None:
        f = self._fonte(fonte)
        f.update(leituras=f["leituras"] + 1, sem_mudanca=f["sem_mudanca"] + int(sem_mudanca), achados=f["achados"] + achados,
                 falhas=f["falhas"] + int(bool(erro)), ultimo_erro=erro or f["ultimo_erro"], ultima=em,
                 situacao="erro" if erro else ("sem mudança" if sem_mudanca else "lida"))
        self._entregar("motor.fonte", {k: v for k, v in f.items() if k != "motor"})

    def retorno(self, achado: str, fonte: str | None, decisao: str, motivo: str | None, em: str) -> None:
        if achado in self._retornos or self._um("SELECT 1 FROM motor_retorno WHERE motor=? AND achado=?", (achado,)):
            return
        self._retornos.add(achado)
        if fonte is None:
            fonte = self._entregue_fonte.get(achado)
            if fonte is None:
                r = self._um("SELECT fonte FROM motor_entregue WHERE motor=? AND achado=?", (achado,))
                fonte = r[0] if r else None
        # aceitos e barrados de cada fonte se contam pelos próprios retornos (sem contador duplicado na linha da fonte)
        self._entregar("motor.retorno", {"achado": achado, "fonte": fonte, "decisao": decisao, "motivo": motivo, "em": em})

    def painel(self) -> dict:
        self.con.row_factory = sqlite3.Row
        fontes = [{k: r[k] for k in r.keys() if k != "motor"} for r in self.con.execute(SQL_FONTES, (self.motor,))]
        self.con.row_factory = None
        n = self._um("SELECT COUNT(*) FROM motor_entregue WHERE motor=?")[0]
        return {"fontes": fontes, "entregues": n}
