"""O estado de cada motor: o seu aprendizado de uso próprio, num banco só dele (dados/motores/<id>.db, fora do Git).

Guarda as assinaturas das páginas (vigilância), o que já foi entregue (para não entregar de novo), o rendimento de cada
fonte e os retornos da Pertinência. Nenhuma oportunidade: elas vivem só na Biblioteca. Só o próprio motor escreve aqui.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DDL = """
CREATE TABLE IF NOT EXISTS assinatura (fonte TEXT PRIMARY KEY, valor TEXT NOT NULL, em TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS alvo_mudanca (alvo TEXT NOT NULL, em TEXT NOT NULL, mes INTEGER NOT NULL, PRIMARY KEY (alvo, em));
CREATE TABLE IF NOT EXISTS entregue (chave TEXT PRIMARY KEY, em TEXT NOT NULL, achado TEXT, fonte TEXT);
CREATE TABLE IF NOT EXISTS fonte (nome TEXT PRIMARY KEY, leituras INTEGER NOT NULL DEFAULT 0, sem_mudanca INTEGER NOT NULL DEFAULT 0,
  achados INTEGER NOT NULL DEFAULT 0, aceitos INTEGER NOT NULL DEFAULT 0, barrados INTEGER NOT NULL DEFAULT 0, falhas INTEGER NOT NULL DEFAULT 0,
  ultimo_erro TEXT, ultima TEXT);
CREATE TABLE IF NOT EXISTS retorno (achado TEXT PRIMARY KEY, fonte TEXT, decisao TEXT, motivo TEXT, em TEXT NOT NULL);
"""


class EstadoMotor:
    def __init__(self, caminho: str | Path):
        p = Path(caminho)
        p.parent.mkdir(parents=True, exist_ok=True)
        self.con = sqlite3.connect(p, isolation_level=None, check_same_thread=False)
        self.con.execute("PRAGMA journal_mode=WAL")
        self.con.executescript(DDL)
        if "situacao" not in {r[1] for r in self.con.execute("PRAGMA table_info(fonte)")}:   # a situação da última leitura
            self.con.execute("ALTER TABLE fonte ADD COLUMN situacao TEXT")

    def assinatura(self, fonte: str) -> str | None:
        r = self.con.execute("SELECT valor FROM assinatura WHERE fonte=?", (fonte,)).fetchone()
        return r[0] if r else None

    def gravar_assinatura(self, fonte: str, valor: str, em: str) -> None:
        self.con.execute("INSERT INTO assinatura VALUES (?,?,?) ON CONFLICT(fonte) DO UPDATE SET valor=excluded.valor, em=excluded.em", (fonte, valor, em))

    def mudanca_do_alvo(self, alvo: str, em: str) -> None:
        """O alvo mudou: o mês fica registrado (é assim que o motor aprende a previsão de edição)."""
        self.con.execute("INSERT OR IGNORE INTO alvo_mudanca VALUES (?, ?, ?)", (alvo, em, int(em[5:7])))
        self.con.commit()

    def meses_do_alvo(self, alvo: str) -> list[int]:
        return [r[0] for r in self.con.execute("SELECT DISTINCT mes FROM alvo_mudanca WHERE alvo = ? ORDER BY mes", (alvo,))]

    def ja_entregue(self, chave: str) -> bool:
        return self.con.execute("SELECT 1 FROM entregue WHERE chave=?", (chave,)).fetchone() is not None

    def marcar_entregue(self, chave: str, em: str, achado: str | None = None, fonte: str | None = None) -> None:
        self.con.execute("INSERT OR IGNORE INTO entregue VALUES (?,?,?,?)", (chave, em, achado, fonte))

    def leitura(self, fonte: str, em: str, achados: int = 0, sem_mudanca: bool = False, erro: str | None = None) -> None:
        self.con.execute("INSERT OR IGNORE INTO fonte(nome) VALUES (?)", (fonte,))
        situacao = "erro" if erro else ("sem mudança" if sem_mudanca else "lida")
        self.con.execute("UPDATE fonte SET leituras=leituras+1, sem_mudanca=sem_mudanca+?, achados=achados+?, falhas=falhas+?, "
                         "ultimo_erro=COALESCE(?, ultimo_erro), ultima=?, situacao=? WHERE nome=?",
                         (int(sem_mudanca), achados, int(bool(erro)), erro, em, situacao, fonte))

    def retorno(self, achado: str, fonte: str | None, decisao: str, motivo: str | None, em: str) -> None:
        if fonte is None:                                      # a fonte de onde o achado veio, guardada na entrega
            r = self.con.execute("SELECT fonte FROM entregue WHERE achado=?", (achado,)).fetchone()
            fonte = r[0] if r else None
        novo = self.con.execute("INSERT OR IGNORE INTO retorno VALUES (?,?,?,?,?)", (achado, fonte, decisao, motivo, em)).rowcount
        if novo and fonte:
            col = "aceitos" if decisao == "aceito" else "barrados"
            self.con.execute(f"UPDATE fonte SET {col}={col}+1 WHERE nome=?", (fonte,))

    def painel(self) -> dict:
        self.con.row_factory = sqlite3.Row
        fontes = [dict(r) for r in self.con.execute("SELECT * FROM fonte ORDER BY nome")]
        self.con.row_factory = None
        return {"fontes": fontes, "entregues": self.con.execute("SELECT COUNT(*) FROM entregue").fetchone()[0]}
