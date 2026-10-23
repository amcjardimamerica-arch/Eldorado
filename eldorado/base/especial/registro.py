"""O registro da base Especial (as empresas e os incentivos): o "cartório" do banco especial.db.

Os motores de destino "especial" (como o motor-gife) não entregam oportunidades: entregam empresas (quem pode
destinar incentivo) e incentivos (o que cada uma já destinou, por qual lei). O registro valida e armazena, por eventos:
  - o CNPJ: 14 dígitos com os dígitos verificadores; ou a raiz de 8 dígitos (como publicam os maiores contribuintes
    do ICMS), que é casada com a empresa já conhecida pela mesma raiz;
  - a empresa: inserida ou atualizada pelo CNPJ (o que já se sabia não se perde: só campos vazios são preenchidos);
  - o incentivo: um por empresa, lei e fonte (a mesma fonte não duplica).
Dados públicos íntegros, como publicados (titular, 22/10/2026); pessoa física fica fora da base de empresas.
"""
from __future__ import annotations

import re
import sqlite3
from typing import Any

from ..nucleo.eventos import Diario, agora


def cnpj_valido(cnpj: str) -> bool:
    d = re.sub(r"\D", "", cnpj or "")
    if len(d) != 14 or d == d[0] * 14:
        return False
    for n in (12, 13):
        pesos = list(range(n - 7, 1, -1)) + list(range(9, 1, -1))
        soma = sum(int(a) * b for a, b in zip(d[:n], pesos[-n:], strict=True))
        if int(d[n]) != (0 if soma % 11 < 2 else 11 - soma % 11):
            return False
    return True


def resolver_cnpj(con: sqlite3.Connection | None, cnpj: str) -> tuple[str | None, str]:
    """O CNPJ completo e válido, ou a empresa conhecida pela mesma raiz, ou a raiz (sem empresa conhecida)."""
    d = re.sub(r"\D", "", cnpj or "")
    if len(d) == 14:
        return (d, "cnpj") if cnpj_valido(d) else (None, "cnpj inválido")
    if len(d) == 8:
        if con is not None:
            r = con.execute("SELECT cnpj FROM empresa WHERE substr(cnpj, 1, 8) = ? ORDER BY length(cnpj) DESC LIMIT 1", (d,)).fetchone()
            if r:
                return r[0], "raiz casada com a empresa conhecida"
        return d, "raiz (sem empresa conhecida)"
    return None, "sem CNPJ"


class Registro:
    def __init__(self, especial: sqlite3.Connection | None, diario: Diario):
        self.con, self.diario = especial, diario

    def registrar(self, dados: dict[str, Any], motor: str, fonte: str) -> dict[str, Any]:
        if (dados.get("tipo_pessoa") or "juridica").lower().startswith("fis"):
            return {"registrado": False, "motivo": "pessoa física fica fora da base de empresas"}
        cnpj, como = resolver_cnpj(self.con, str(dados.get("cnpj") or ""))
        if cnpj is None:
            return {"registrado": False, "motivo": como}
        atual = {}
        if self.con is not None:
            self.con.row_factory = sqlite3.Row
            r = self.con.execute("SELECT * FROM empresa WHERE cnpj = ?", (cnpj,)).fetchone()
            atual = dict(r) if r else {}
        novo = {"cnpj": cnpj, "razao_social": dados.get("razao_social") or atual.get("razao_social") or cnpj}
        for campo in ("nome_fantasia", "uf", "municipio_ibge", "porte", "atividade_principal", "regime_tributario", "site"):
            novo[campo] = atual.get(campo) or dados.get(campo)              # o que já se sabia não se perde
        # a regra do banco (espiao, motor, importacao, titular); o motor e a fonte ficam no evento e no incentivo
        novo["descoberta_por"] = atual.get("descoberta_por") or ("espiao" if motor == "espiao" else "motor")
        novo["descoberta_em"] = atual.get("descoberta_em") or agora()
        novo["atualizada_em"] = agora()
        self.diario.emitir("empresa.registrada", motor, novo)
        inc = dados.get("incentivo") or {}
        if inc.get("lei"):
            # pela raiz: a mesma empresa chega pela raiz (ICMS) e pelo CNPJ completo (Salic) e não pode duplicar o incentivo
            ja = self.con is not None and self.con.execute("SELECT 1 FROM incentivo WHERE substr(cnpj, 1, 8) = ? AND lei = ? AND fonte = ?",
                                                           (cnpj[:8], inc["lei"], f"{motor}: {fonte}")).fetchone()
            if not ja:
                valor = inc.get("valor")
                self.diario.emitir("incentivo.registrado", motor, {"cnpj": cnpj, "lei": inc["lei"], "ano": inc.get("ano"),
                                                                   "valor": float(valor) if valor not in (None, "") else None,
                                                                   "comprovado": 1, "fonte": f"{motor}: {fonte}", "em": agora()})
        return {"registrado": True, "cnpj": cnpj, "como": como}
