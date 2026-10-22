"""A Regência: planeja a passagem, aciona os motores e autoriza cada passagem de livro.

- Planejar: o que está devido na agenda (uma passagem por janela), na ordem das notas da rede, dentro da folga
  da máquina (governador).
- Acionar: cada motor é chamado e medido (recibo); os achados viram eventos; um motor que falha não derruba os outros.
- Autorizar: só as passagens de fase permitidas, e no máximo 3 tentativas por fase.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import msgspec

from ..fluxo.agenda import Agenda
from ..fluxo.agenda import carregar as carregar_agenda
from ..nucleo.contratos import Achado, Plano
from ..nucleo.eventos import Diario, agora, novo_id
from ..nucleo.recibo import emitir_recibo, medir
from ..nucleo.registro import Registro
from ..nucleo.registro import carregar as carregar_registro
from .governador import Governador, Leitura, medidor_psutil

TRANSICOES = {
    "coleta": {"certificacao"},
    "certificacao": {"investigacao", "verificacao externa", "farol"},
    "investigacao": {"certificacao"},
    "verificacao externa": {"certificacao", "farol"},
    "farol": set(),
}
COLUNAS_ACHADO = {"id", "motor", "encontrado_em", "publicado_em", "link_divulgacao", "link_oficial", "titulo", "dados",
                  "veio_de_copia_arquivada", "pista"}


def autorizar(fase_atual: str | None, para: str, tentativas_na_fase: int = 0, maximo: int = 3) -> tuple[bool, str]:
    if fase_atual is None:
        return (para == "coleta" or para == "certificacao"), "entrada de um livro novo"
    if para not in TRANSICOES.get(fase_atual, set()):
        return False, f"passagem não permitida: {fase_atual} → {para}"
    if tentativas_na_fase > maximo:
        return False, f"mais de {maximo} tentativas em {fase_atual}"
    return True, f"{fase_atual} → {para}"


def achado_para_evento(a: Achado) -> dict[str, Any]:
    """O achado no formato da tabela; a assinatura do documento e o endereço no Drive vão dentro dos dados."""
    d = msgspec.to_builtins(a)
    ev = {k: (int(v) if isinstance(v, bool) else v) for k, v in d.items() if k in COLUNAS_ACHADO}
    extras = {k: d[k] for k in ("documento_sha256", "drive_id") if d.get(k)}
    if a.documento and a.documento.get("sha256"):
        extras["documento_sha256"] = a.documento["sha256"]
    if extras:
        ev["dados"] = {**(ev.get("dados") or {}), **extras}
    return ev


class Regencia:
    def __init__(self, agenda: Agenda, governador: Governador, registro: Registro, diario: Diario, notas: dict[str, float] | None = None):
        self.agenda, self.governador, self.registro, self.diario = agenda, governador, registro, diario
        self.notas = notas or {}

    def planejar(self, agora_: datetime, acionadas: set[tuple[str, str]] = frozenset(),
                 ultima: dict[str, datetime] | None = None) -> dict[str, Any]:
        devidos = [d for d in self.agenda.devidos(agora_, acionadas, ultima) if d.modulo in self.registro.ids()]
        devidos.sort(key=lambda d: -self.notas.get(d.modulo, 0.5))
        plano = {"passagem": novo_id(), "criado_em": agora(), "paralelismo": self.governador.paralelismo(),
                 "motores": [{"modulo": d.modulo, "janela_inicio": d.janela_inicio, "janela_fim": d.janela_fim, "motivo": d.motivo,
                              "nota": self.notas.get(d.modulo, 0.5)} for d in devidos]}
        self.diario.emitir("plano.criado", "regencia", {"passagem": plano["passagem"], "criado_em": plano["criado_em"],
                                                        "motores": plano["motores"], "livros_por_etapa": None, "tempo_por_etapa": None})
        return plano

    def acionar(self, plano: dict[str, Any], execucao: str | None = None) -> tuple[list[dict[str, Any]], list[str]]:
        achados: list[dict[str, Any]] = []
        adiados: list[str] = []
        for m in plano["motores"]:
            modulo = m["modulo"]
            if not self.governador.pode_iniciar(modulo):
                adiados.append(modulo)
                continue
            motor = self.registro.obter(modulo)
            self.diario.emitir("agenda.definida", "regencia", {"modulo": modulo, "janela_inicio": m["janela_inicio"],
                                                               "janela_fim": m["janela_fim"], "motivo": m["motivo"]})
            self.diario.emitir("acionamento.feito", "regencia", {"passagem": plano["passagem"], "etapa": "coleta", "modulo": modulo,
                                                                 "motivo": m["motivo"], "em": agora()})
            p = Plano(passagem=plano["passagem"], janela_inicio=m["janela_inicio"], janela_fim=m["janela_fim"])
            inicio = agora()
            med = medir(lambda motor=motor, p=p: list(motor.buscar(p)))
            emitir_recibo(self.diario, execucao, modulo, "regencia", med)
            lista = med.resultado or []
            self.diario.emitir("motor.execucao", "regencia", {"motor": modulo, "inicio": inicio, "fim": agora(), "achados": len(lista),
                                                              "erro": med.erro or None})
            for a in lista:
                if a.documento:
                    self._documento(modulo, a.documento)
                ev = achado_para_evento(a)
                self.diario.emitir("achado.entregue", modulo, ev)
                achados.append(_sem_paginas(msgspec.to_builtins(a)) | {"documento": _sem_paginas(a.documento) if a.documento else None})
        return achados, adiados

    def _documento(self, modulo: str, doc: dict[str, Any]) -> None:
        """O documento oficial que o motor leu: o registro (pela assinatura) e o texto literal de cada página."""
        self.diario.emitir("documento.registrado", modulo, {"url": doc["url"], "sha256": doc["sha256"], "tipo": doc.get("tipo"),
                                                            "paginas": len(doc.get("paginas") or []), "obtido_em": agora(),
                                                            "oficial": int(bool(doc.get("oficial"))), "drive_id": doc.get("drive_id"),
                                                            "leitor": doc.get("leitor"), "versao_leitor": doc.get("versao_leitor")})
        for i, texto in enumerate(doc.get("paginas") or [], 1):
            self.diario.emitir("pagina.gravada", modulo, {"documento_sha256": doc["sha256"], "numero": i, "texto": texto})


def _sem_paginas(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if k != "paginas"}


def _governador(parametros: dict[str, Any], diario: Diario) -> Governador:
    if "carga_fixa" in parametros:
        c = float(parametros["carga_fixa"])
        return Governador(lambda: Leitura(c, c, 0.3), diario=diario)
    return Governador(medidor_psutil(), diario=diario)


def _acionadas(dados: str | Path) -> tuple[set[tuple[str, str]], dict[str, datetime]]:
    p = Path(dados) / "cerebro.db"
    if not p.exists():
        return set(), {}
    con = sqlite3.connect(p)
    try:
        acion = {(r[0], r[1]) for r in con.execute("SELECT modulo, janela_inicio FROM agenda")}
        sql = "SELECT motor, MAX(fim) FROM execucao_motor WHERE erro IS NULL GROUP BY motor"
        ultima = {r[0]: datetime.fromisoformat(r[1]) for r in con.execute(sql) if r[1]}
    finally:
        con.close()
    return acion, ultima


def no_planejar(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    quando = datetime.fromisoformat(parametros["agora"]) if parametros.get("agora") else datetime.now(timezone.utc)
    registro = carregar_registro(parametros.get("modulos", "config/modulos.toml"), contexto.diario)
    acion, ultima = _acionadas(parametros.get("dados", "dados"))
    r = Regencia(carregar_agenda(parametros.get("agenda", "config/agenda.toml")), _governador(parametros, contexto.diario), registro, contexto.diario)
    return [{"plano": r.planejar(quando, acion, ultima)}]


def no_acionar(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    registro = carregar_registro(parametros.get("modulos", "config/modulos.toml"))
    r = Regencia(Agenda([]), _governador(parametros, contexto.diario), registro, contexto.diario)
    achados: list[dict[str, Any]] = []
    for item in itens:
        a, adiados = r.acionar(item["plano"], contexto.execucao)
        achados.extend(a)
        for m in adiados:
            contexto.diario.emitir("alarme.aberto", "regencia", {"gravidade": "baixa", "modulo": m, "aberto_em": agora(),
                                                                 "mensagem": f"motor adiado pelo governador: {r.governador.motivo()}"})
    return achados
