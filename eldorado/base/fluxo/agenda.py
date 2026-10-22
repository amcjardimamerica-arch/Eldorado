"""A agenda: quais módulos estão devidos agora.

Cada módulo tem horários, dias, cadência e, opcionalmente, janelas previstas pela análise preditiva.
Regra central: uma passagem por janela. Uma janela já acionada não é acionada de novo
(lição do Eldorado0: 425 execuções do mesmo fluxo em 7 horas).
"""
from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

DIAS = ("seg", "ter", "qua", "qui", "sex", "sab", "dom")


class AgendaInvalida(Exception):
    pass


@dataclass(frozen=True)
class Regra:
    modulo: str
    horarios: tuple[str, ...] = ()
    dias: tuple[str, ...] = DIAS
    cadencia_dias: int = 1
    janela_min: int = 30
    motivo: str = ""
    janelas_previstas: tuple[tuple[str, str], ...] = ()

    def __post_init__(self):
        for h in self.horarios:
            try:
                datetime.strptime(h, "%H:%M")
            except ValueError as e:
                raise AgendaInvalida(f"{self.modulo}: horário inválido {h!r}") from e
        if set(self.dias) - set(DIAS):
            raise AgendaInvalida(f"{self.modulo}: dias inválidos {sorted(set(self.dias) - set(DIAS))}")
        if self.cadencia_dias < 1 or self.janela_min < 1:
            raise AgendaInvalida(f"{self.modulo}: cadência e janela devem ser positivas")


@dataclass(frozen=True)
class Devido:
    modulo: str
    janela_inicio: str
    janela_fim: str
    motivo: str


@dataclass
class Agenda:
    regras: list[Regra]
    fuso: str = "America/Sao_Paulo"
    _tz: ZoneInfo = field(init=False)

    def __post_init__(self):
        self._tz = ZoneInfo(self.fuso)
        nomes = [r.modulo for r in self.regras]
        if len(nomes) != len(set(nomes)):
            raise AgendaInvalida("módulo repetido na agenda")

    def devidos(self, agora: datetime, acionadas: set[tuple[str, str]] = frozenset(),
                ultima_execucao: dict[str, datetime] | None = None) -> list[Devido]:
        """O que está devido agora. `acionadas` são as janelas já acionadas (módulo, início da janela)."""
        if agora.tzinfo is None:
            raise ValueError("a hora deve ter fuso")
        local = agora.astimezone(self._tz)
        ultima_execucao = ultima_execucao or {}
        saida: list[Devido] = []
        for r in self.regras:
            candidatas: list[tuple[datetime, datetime, str]] = []
            if DIAS[local.weekday()] in r.dias:
                for h in r.horarios:
                    hh, mm = map(int, h.split(":"))
                    ini = local.replace(hour=hh, minute=mm, second=0, microsecond=0)
                    fim = ini + timedelta(minutes=r.janela_min)
                    if ini <= local < fim:
                        candidatas.append((ini, fim, r.motivo or f"horário {h}"))
            for ini_s, fim_s in r.janelas_previstas:
                ini, fim = datetime.fromisoformat(ini_s).astimezone(self._tz), datetime.fromisoformat(fim_s).astimezone(self._tz)
                if ini <= local < fim:
                    candidatas.append((ini, fim, "janela prevista pela análise"))
            for ini, fim, motivo in candidatas:
                chave = (r.modulo, ini.isoformat())
                if chave in acionadas:
                    continue
                ultima = ultima_execucao.get(r.modulo)
                if r.cadencia_dias > 1 and ultima and (local - ultima.astimezone(self._tz)) < timedelta(days=r.cadencia_dias) - timedelta(minutes=r.janela_min):
                    continue
                saida.append(Devido(r.modulo, ini.isoformat(), fim.isoformat(), motivo))
                break                                    # uma passagem por janela e por módulo
        return saida


def carregar(arquivo: str | Path, fuso: str = "America/Sao_Paulo") -> Agenda:
    p = Path(arquivo)
    if not p.exists():
        return Agenda([], fuso)
    d = tomllib.loads(p.read_text(encoding="utf-8"))
    regras = []
    for m in d.get("modulo", []):
        regras.append(Regra(modulo=m["id"], horarios=tuple(m.get("horarios", [])), dias=tuple(m.get("dias", DIAS)),
                            cadencia_dias=int(m.get("cadencia_dias", 1)), janela_min=int(m.get("janela_min", 30)), motivo=m.get("motivo", ""),
                            janelas_previstas=tuple(tuple(j) for j in m.get("janelas_previstas", []))))
    return Agenda(regras, d.get("fuso", fuso))
