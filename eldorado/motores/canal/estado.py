"""O estado de cada motor: o seu aprendizado de uso próprio, DENTRO DO CÉREBRO (cerebro.db, tabelas motor_*, com a
coluna motor). A regra da titular (24/10/2026): só o Cérebro tem um banco paralelo, o de aprendizado; os livros vivem só
na Biblioteca. Guarda as assinaturas das páginas (vigilância), o que já foi entregue (a chave e o id do achado, nunca o
achado), o rendimento de cada fonte, os retornos da Pertinência, o mapa dos sites originais e as mudanças dos alvos.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DDL = """
CREATE TABLE IF NOT EXISTS motor_assinatura (motor TEXT NOT NULL, fonte TEXT NOT NULL, valor TEXT NOT NULL, em TEXT NOT NULL, PRIMARY KEY (motor, fonte));
CREATE TABLE IF NOT EXISTS motor_mapa_url (motor TEXT NOT NULL, dominio TEXT NOT NULL, url TEXT NOT NULL, primeira_vez TEXT NOT NULL,
  PRIMARY KEY (motor, dominio, url));
CREATE TABLE IF NOT EXISTS motor_mapa_dominio (motor TEXT NOT NULL, dominio TEXT NOT NULL, verificado_em TEXT NOT NULL, urls INTEGER,
  PRIMARY KEY (motor, dominio));
CREATE TABLE IF NOT EXISTS motor_alvo_mudanca (motor TEXT NOT NULL, alvo TEXT NOT NULL, em TEXT NOT NULL, mes INTEGER NOT NULL, PRIMARY KEY (motor, alvo, em));
CREATE TABLE IF NOT EXISTS motor_entregue (motor TEXT NOT NULL, chave TEXT NOT NULL, em TEXT NOT NULL, achado TEXT, fonte TEXT, PRIMARY KEY (motor, chave));
CREATE INDEX IF NOT EXISTS motor_entregue_achado ON motor_entregue(motor, achado);
CREATE TABLE IF NOT EXISTS motor_fonte (motor TEXT NOT NULL, nome TEXT NOT NULL, leituras INTEGER NOT NULL DEFAULT 0, sem_mudanca INTEGER NOT NULL DEFAULT 0,
  achados INTEGER NOT NULL DEFAULT 0, aceitos INTEGER NOT NULL DEFAULT 0, barrados INTEGER NOT NULL DEFAULT 0, falhas INTEGER NOT NULL DEFAULT 0,
  ultimo_erro TEXT, ultima TEXT, situacao TEXT, PRIMARY KEY (motor, nome));
CREATE TABLE IF NOT EXISTS motor_retorno (motor TEXT NOT NULL, achado TEXT NOT NULL, fonte TEXT, decisao TEXT, motivo TEXT, em TEXT NOT NULL,
  PRIMARY KEY (motor, achado));
"""


def caminho_do_cerebro(dados: str | Path) -> Path:
    """dados/motores (o parâmetro antigo) → dados/cerebro.db; outra pasta → <pasta>/cerebro.db."""
    p = Path(dados)
    if p.suffix == ".db":
        return p
    return (p.parent if p.name == "motores" else p) / "cerebro.db"


class EstadoMotor:
    def __init__(self, cerebro: str | Path, motor: str = "motor"):
        p = caminho_do_cerebro(cerebro)
        p.parent.mkdir(parents=True, exist_ok=True)
        self.motor = motor
        from ...banco.cerebro_db.esquema import abrir  # o Cérebro pelo esquema (as tabelas motor_* são da versão 2)
        self.con = abrir(p)
        self.con.row_factory = None
        self.con.execute("PRAGMA busy_timeout=60000")

    def _q(self, sql: str, args: tuple = ()) -> sqlite3.Cursor:
        return self.con.execute(sql, (self.motor, *args))

    def assinatura(self, fonte: str) -> str | None:
        r = self._q("SELECT valor FROM motor_assinatura WHERE motor=? AND fonte=?", (fonte,)).fetchone()
        return r[0] if r else None

    def gravar_assinatura(self, fonte: str, valor: str, em: str) -> None:
        self._q("INSERT INTO motor_assinatura VALUES (?,?,?,?) ON CONFLICT(motor, fonte) DO UPDATE SET valor=excluded.valor, em=excluded.em",
                (fonte, valor, em))

    def mapa_visto(self, dominio: str) -> set[str]:
        """As URLs do mapa do site original já vistas neste domínio (conhecimento do motor: domínios e URLs, nunca livros)."""
        return {r[0] for r in self._q("SELECT url FROM motor_mapa_url WHERE motor=? AND dominio=?", (dominio,))}

    def mapa_verificado_em(self, dominio: str) -> str | None:
        r = self._q("SELECT verificado_em FROM motor_mapa_dominio WHERE motor=? AND dominio=?", (dominio,)).fetchone()
        return r[0] if r else None

    def marcar_mapa(self, dominio: str, urls: list[str], em: str) -> None:
        self.con.executemany("INSERT OR IGNORE INTO motor_mapa_url VALUES (?, ?, ?, ?)", [(self.motor, dominio, u, em) for u in urls])
        self._q("INSERT OR REPLACE INTO motor_mapa_dominio VALUES (?, ?, ?, ?)", (dominio, em, len(urls)))

    def mudanca_do_alvo(self, alvo: str, em: str) -> None:
        """O alvo mudou: o mês fica registrado (é assim que o motor aprende a previsão de edição)."""
        self._q("INSERT OR IGNORE INTO motor_alvo_mudanca VALUES (?, ?, ?, ?)", (alvo, em, int(em[5:7])))

    def meses_do_alvo(self, alvo: str) -> list[int]:
        return [r[0] for r in self._q("SELECT DISTINCT mes FROM motor_alvo_mudanca WHERE motor=? AND alvo=? ORDER BY mes", (alvo,))]

    def ja_entregue(self, chave: str) -> bool:
        return self._q("SELECT 1 FROM motor_entregue WHERE motor=? AND chave=?", (chave,)).fetchone() is not None

    def marcar_entregue(self, chave: str, em: str, achado: str | None = None, fonte: str | None = None) -> None:
        self._q("INSERT OR IGNORE INTO motor_entregue VALUES (?,?,?,?,?)", (chave, em, achado, fonte))

    def leitura(self, fonte: str, em: str, achados: int = 0, sem_mudanca: bool = False, erro: str | None = None) -> None:
        self._q("INSERT OR IGNORE INTO motor_fonte(motor, nome) VALUES (?, ?)", (fonte,))
        situacao = "erro" if erro else ("sem mudança" if sem_mudanca else "lida")
        self.con.execute("UPDATE motor_fonte SET leituras=leituras+1, sem_mudanca=sem_mudanca+?, achados=achados+?, falhas=falhas+?, "
                         "ultimo_erro=COALESCE(?, ultimo_erro), ultima=?, situacao=? WHERE motor=? AND nome=?",
                         (int(sem_mudanca), achados, int(bool(erro)), erro, em, situacao, self.motor, fonte))

    def retorno(self, achado: str, fonte: str | None, decisao: str, motivo: str | None, em: str) -> None:
        if fonte is None:                                      # a fonte de onde o achado veio, guardada na entrega
            r = self._q("SELECT fonte FROM motor_entregue WHERE motor=? AND achado=?", (achado,)).fetchone()
            fonte = r[0] if r else None
        novo = self._q("INSERT OR IGNORE INTO motor_retorno VALUES (?,?,?,?,?,?)", (achado, fonte, decisao, motivo, em)).rowcount
        if novo and fonte:
            col = "aceitos" if decisao == "aceito" else "barrados"
            self.con.execute(f"UPDATE motor_fonte SET {col}={col}+1 WHERE motor=? AND nome=?", (self.motor, fonte))

    def painel(self) -> dict:
        self.con.row_factory = sqlite3.Row
        fontes = [{k: r[k] for k in r.keys() if k != "motor"} for r in self._q("SELECT * FROM motor_fonte WHERE motor=? ORDER BY nome")]
        self.con.row_factory = None
        return {"fontes": fontes, "entregues": self._q("SELECT COUNT(*) FROM motor_entregue WHERE motor=?").fetchone()[0]}
