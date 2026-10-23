"""A decisão do Cérebro: a cada batimento, quais motores acionar, conforme a necessidade (titular, 22/10/2026).

O Eldorado não tem horário fixo. O acionamento de hora em hora é só o batimento que acorda o sistema; quem decide é o
Cérebro, com o que aprendeu do histórico:
  - todo motor lê todo dia: o que ainda não leu hoje é acionado ("primeira leitura do dia"), pelo rendimento aprendido;
  - a fonte que falhou na leitura anterior tenta de novo, até 3 vezes no dia;
  - o motor volta quando chega uma hora em que a fonte dele costuma publicar (horas APRENDIDAS: as horas em que trouxe
    achados novos); com histórico curto, os horários herdados do Eldorado0 são só o ponto de partida;
  - o que não tem necessidade não roda.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

FUSO = ZoneInfo("America/Sao_Paulo")
MINIMO_HISTORICO = 5          # execuções com achados antes de confiar só no aprendido
JANELA_APRENDIZADO_DIAS = 30


@dataclass
class Execucao:
    motor: str
    inicio: datetime
    achados: int
    falhou: bool = False


@dataclass
class Decisao:
    motor: str
    motivo: str
    prioridade: float


def horas_produtivas(motor: str, historico: list[Execucao], ponto_de_partida: set[int], agora: datetime) -> set[int]:
    recentes = [e for e in historico if e.motor == motor and e.inicio >= agora - timedelta(days=JANELA_APRENDIZADO_DIAS)]
    com_achados = [e for e in recentes if e.achados > 0]
    aprendidas = {e.inicio.astimezone(FUSO).hour for e in com_achados}
    return aprendidas if len(com_achados) >= MINIMO_HISTORICO else aprendidas | ponto_de_partida


def rendimento(motor: str, historico: list[Execucao]) -> float:
    m = [e for e in historico if e.motor == motor]
    return sum(e.achados for e in m) / len(m) if m else 1.0          # sem histórico: prioridade média


def decidir(agora: datetime, motores: list[str], historico: list[Execucao], ponto_de_partida: dict[str, set[int]],
            maximo_tentativas: int = 3) -> list[Decisao]:
    local = agora.astimezone(FUSO)
    hoje = local.date()
    saida: list[Decisao] = []
    for m in motores:
        do_dia = sorted((e for e in historico if e.motor == m and e.inicio.astimezone(FUSO).date() == hoje), key=lambda e: e.inicio)
        r = rendimento(m, historico)
        if not do_dia:
            saida.append(Decisao(m, "primeira leitura do dia", 1000 + r))
            continue
        ultima = do_dia[-1]
        if ultima.falhou and len(do_dia) < maximo_tentativas:
            saida.append(Decisao(m, f"nova tentativa ({len(do_dia) + 1}ª do dia): a fonte falhou na leitura anterior", 500 + r))
            continue
        h_ultima = ultima.inicio.astimezone(FUSO).hour
        pendentes = sorted(h for h in horas_produtivas(m, historico, ponto_de_partida.get(m, set()), agora) if h_ultima < h <= local.hour)
        if pendentes:
            saida.append(Decisao(m, f"a fonte costuma publicar às {pendentes[-1]}h (aprendido do histórico); última leitura às {h_ultima}h", 100 + r))
    return sorted(saida, key=lambda d: -d.prioridade)


def proxima(agora: datetime, motores: list[str], historico: list[Execucao], ponto_de_partida: dict[str, set[int]]) -> datetime:
    """Quando será a próxima ação prevista: a próxima hora aprendida de alguma fonte, ou a primeira leitura de amanhã."""
    local = agora.astimezone(FUSO)
    amanha = (local + timedelta(days=1)).replace(hour=0, minute=1, second=0, microsecond=0)
    candidatas = [amanha]
    for m in motores:
        for h in horas_produtivas(m, historico, ponto_de_partida.get(m, set()), agora):
            if h > local.hour:
                candidatas.append(local.replace(hour=h, minute=0, second=0, microsecond=0))
    return min(candidatas).astimezone(agora.tzinfo)
