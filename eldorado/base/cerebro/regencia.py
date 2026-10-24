"""A Regência: planeja a passagem, aciona os motores e autoriza cada passagem de livro.

- Planejar: o que está devido na agenda (uma passagem por janela), na ordem das notas da rede, dentro da folga
  da máquina (governador).
- Acionar: cada motor é chamado e medido (recibo); os achados viram eventos; um motor que falha não derruba os outros.
- Autorizar: só as passagens de fase permitidas, e no máximo 3 tentativas por fase.
"""
from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import msgspec

from ..fluxo.agenda import Agenda, Devido
from ..fluxo.agenda import carregar as carregar_agenda
from ..nucleo.contratos import Achado, Plano
from ..nucleo.eventos import Diario, agora, novo_id
from ..nucleo.recibo import emitir_recibo, medir
from ..nucleo.registro import Registro
from ..nucleo.registro import carregar as carregar_registro
from .governador import Governador, Leitura, medidor_psutil

TRANSICOES = {   # a linha de produção do Cartório (titular, 22/10/2026): uma etapa nunca acontece antes da outra
    "recepcao": {"certificacao"},                                               # 1 → 2
    "certificacao": {"preparacao", "farol", "arquivo"},                         # 2 → 3; ouro com prazo aberto → Farol; encerrada → arquivo
    "preparacao": {"validacao", "analise externa", "arquivo"},                  # 3 → 4 (chegou informação); → 5 (rede esgotada)
    "validacao": {"preparacao", "analise externa", "farol", "arquivo"},         # 4 → 3, → 5, → Farol, → arquivo
    "analise externa": {"validacao", "farol", "arquivo"},                       # 5 → 4 (o Chrome trouxe informação), → Farol, → arquivo
    "farol": {"arquivo"},                                                       # a oportunidade encerrou: a estrela vira o selo do livro
    "arquivo": {"recepcao"},                                                    # nova oportunidade: volta à linha pela recepção
}
COLUNAS_ACHADO = {"id", "motor", "encontrado_em", "publicado_em", "link_divulgacao", "link_oficial", "titulo", "dados",
                  "veio_de_copia_arquivada", "pista"}


def autorizar(fase_atual: str | None, para: str, tentativas_na_fase: int = 0, maximo: int = 3) -> tuple[bool, str]:
    if fase_atual is None:
        return para == "recepcao", "entrada de um livro novo (fase 1, recepção)"
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
    def __init__(self, agenda: Agenda, governador: Governador, registro: Registro, diario: Diario, notas: dict[str, float] | None = None,
                 especial=None):
        self.agenda, self.governador, self.registro, self.diario = agenda, governador, registro, diario
        self.notas = notas or {}
        self.especial = especial                                    # a base Especial (leitura), para o registro das empresas

    def planejar(self, agora_: datetime, acionadas: set[tuple[str, str]] = frozenset(),
                 ultima: dict[str, datetime] | None = None, forcar: bool = False, decisoes: list | None = None) -> dict[str, Any]:
        """Os módulos devidos pela agenda. forcar: todos os registrados, agora (acionamento à mão pela titular ou pela
        análise externa); a janela é a deste minuto, então a trava "uma passagem por janela" continua valendo."""
        if decisoes is not None:                                         # a decisão do Cérebro (sem grade fixa)
            ini = agora_.replace(second=0, microsecond=0)
            devidos = [Devido(d.motor, ini.isoformat(), (ini + timedelta(minutes=60)).isoformat(), d.motivo) for d in decisoes
                       if d.motor in self.registro.ids()]
        elif forcar:
            ini = agora_.replace(second=0, microsecond=0)
            devidos = [Devido(m, ini.isoformat(), (ini + timedelta(minutes=30)).isoformat(), "acionado à mão") for m in sorted(self.registro.ids())]
        else:
            devidos = [d for d in self.agenda.devidos(agora_, acionadas, ultima) if d.modulo in self.registro.ids()]
        devidos.sort(key=lambda d: -self.notas.get(d.modulo, 0.5))
        plano = {"passagem": novo_id(), "criado_em": agora(), "paralelismo": self.governador.paralelismo(),
                 "motores": [{"modulo": d.modulo, "janela_inicio": d.janela_inicio, "janela_fim": d.janela_fim, "motivo": d.motivo,
                              "nota": self.notas.get(d.modulo, 0.5)} for d in devidos]}
        self.diario.emitir("plano.criado", "regencia", {"passagem": plano["passagem"], "criado_em": plano["criado_em"],
                                                        "motores": plano["motores"], "livros_por_etapa": None, "tempo_por_etapa": None})
        return plano

    def acionar(self, plano: dict[str, Any], execucao: str | None = None) -> tuple[list[dict[str, Any]], list[str]]:
        """Os motores do plano, EM PARALELO (titular, 24/10/2026: operar perto de 85% da capacidade): o governador decide,
        a cada motor, quantos trabalhadores cabem na carga atual (o custo aprendido de cada motor, o alvo de 85%); os
        resultados são processados um a um, na ordem em que terminam. Sem folga e sem nenhum rodando, o motor é adiado."""
        import time as _t
        from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
        achados: list[dict[str, Any]] = []
        adiados: list[str] = []
        pendentes: dict[Any, tuple[str, str]] = {}
        fila = list(plano["motores"])
        with ThreadPoolExecutor(max_workers=max(1, self.governador.paralelismo_maximo)) as pool:
            while fila or pendentes:
                while fila:
                    m = fila[0]
                    modulo = m["modulo"]
                    cabe = max(1, self.governador.paralelismo(modulo)) if pendentes else 1
                    if len(pendentes) >= cabe:
                        break                                       # a carga está no alvo: espera um terminar
                    if not pendentes and not self.governador.pode_iniciar(modulo):
                        adiados.append(modulo)                      # sem folga nem com a máquina parada: adiado
                        fila.pop(0)
                        continue
                    fila.pop(0)
                    motor = self.registro.obter(modulo)
                    self.diario.emitir("agenda.definida", "regencia", {"modulo": modulo, "janela_inicio": m["janela_inicio"],
                                                                       "janela_fim": m["janela_fim"], "motivo": m["motivo"]})
                    self.diario.emitir("acionamento.feito", "regencia", {"passagem": plano["passagem"], "etapa": "coleta", "modulo": modulo,
                                                                         "motivo": m["motivo"], "em": agora()})
                    p = Plano(passagem=plano["passagem"], janela_inicio=m["janela_inicio"], janela_fim=m["janela_fim"])
                    if hasattr(motor, "estado"):                   # o motor entrega o que aprende ao Cérebro, pelo diário da execução
                        motor.estado.diario = self.diario
                    f = pool.submit(medir, lambda motor=motor, p=p: list(motor.buscar(p)), medir_memoria=False)
                    pendentes[f] = (modulo, agora())
                if not pendentes:
                    break
                prontos, _ = wait(list(pendentes), timeout=5, return_when=FIRST_COMPLETED)
                if not prontos:
                    _t.sleep(0.05)
                    continue
                for f in prontos:
                    modulo, inicio = pendentes.pop(f)
                    med = f.result()
                    emitir_recibo(self.diario, execucao, modulo, "regencia", med)
                    self.governador.aprender_custo(modulo, med.cpu_ms, med.duracao_ms, med.memoria_pico_kb)
                    lista = med.resultado or []
                    self.diario.emitir("motor.execucao", "regencia", {"motor": modulo, "inicio": inicio, "fim": agora(), "achados": len(lista),
                                                                      "erro": med.erro or None})
                    for a in lista:
                        if (a.dados or {}).get("especial"):              # empresa e incentivo: à base Especial, não à Pertinência
                            from ..especial.registro import Registro as RegistroEspecial
                            RegistroEspecial(self.especial, self.diario).registrar(a.dados["especial"], modulo, a.dados.get("fonte") or modulo)
                            continue
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
    forcar = bool(parametros.get("forcar")) or os.environ.get("ELDORADO_FORCAR") == "1"
    decisoes = None if forcar else _decidir(quando, registro.ids(), parametros)
    if decisoes is not None:                                          # a sala de controle como parâmetro do funcionamento
        from ..painel.sala import ler_sala
        sala = ler_sala(Path(parametros.get("dados", "dados"))) or {}
        ja = {d.motor for d in decisoes}
        atrasados = [m for m in (sala.get("detalhes") or {}).get("fora_da_cadencia", []) if m in registro.ids() and m not in ja]
        if atrasados:
            from .decisao import Decisao
            decisoes = [Decisao(m, "a sala de controle: fora da cadência (acionado primeiro)", 1.0) for m in atrasados] + list(decisoes)
    return [{"plano": r.planejar(quando, acion, ultima, forcar=forcar, decisoes=decisoes)}]


def _decidir(quando: datetime, motores: list[str], parametros: dict[str, Any]) -> list:
    """O que o Cérebro aprendeu: as execuções de cada motor e a situação da última leitura de cada fonte."""
    from .decisao import Execucao, decidir
    dados = Path(parametros.get("dados", "dados"))
    historico: list[Execucao] = []
    if (dados / "cerebro.db").exists():
        con = sqlite3.connect(f"file:{dados / 'cerebro.db'}?mode=ro", uri=True)
        try:
            from ...motores.canal.motor import apelidos
            ap = apelidos()
            for m, ini, ach, erro in con.execute("SELECT motor, inicio, achados, erro FROM execucao_motor ORDER BY inicio"):
                historico.append(Execucao(ap.get(m, m), datetime.fromisoformat(ini), ach or 0, bool(erro)))
        finally:
            con.close()
    cer = dados / "cerebro.db"
    if cer.exists():                                                   # a fonte falhou depois da última execução? (motor_fonte, no Cérebro)
        e = sqlite3.connect(f"file:{cer}?mode=ro", uri=True)
        try:
            tem = e.execute("SELECT 1 FROM sqlite_master WHERE name='motor_fonte'").fetchone()
            for m in motores:
                ultimas = [x for x in historico if x.motor == m]
                if tem and ultimas:
                    ini = ultimas[-1].inicio.isoformat()
                    ultimas[-1].falhou |= e.execute("SELECT COUNT(*) FROM motor_fonte WHERE motor=? AND situacao='erro' AND ultima >= ?",
                                                    (m, ini[:19])).fetchone()[0] > 0
        finally:
            e.close()
    ponto = {}
    agenda = Path(parametros.get("agenda", "config/agenda.toml"))
    if agenda.exists():
        import tomllib
        for mod in tomllib.loads(agenda.read_text(encoding="utf-8")).get("modulo", []):
            ponto[mod["id"]] = {int(h.split(":")[0]) for h in mod.get("horarios", [])}
    nota = None
    if (dados / "biblioteca.db").exists() and (dados / "cerebro.db").exists():
        from .rede import RedeNeural
        b = sqlite3.connect(f"file:{dados / 'biblioteca.db'}?mode=ro", uri=True)
        c = sqlite3.connect(f"file:{dados / 'cerebro.db'}?mode=ro", uri=True)
        try:
            nota = RedeNeural.treinar(b, c).nota_motor                  # a rede neural reaprende e dá a nota de cada motor
        finally:
            b.close()
            c.close()
    return decidir(quando, list(motores), historico, ponto, nota=nota)


def no_acionar(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    registro = carregar_registro(parametros.get("modulos", "config/modulos.toml"))
    esp_p = Path(parametros.get("dados", "dados")) / "biblioteca.db"   # as empresas, na Biblioteca
    especial = sqlite3.connect(f"file:{esp_p}?mode=ro", uri=True) if esp_p.exists() else None
    r = Regencia(Agenda([]), _governador(parametros, contexto.diario), registro, contexto.diario, especial=especial)
    achados: list[dict[str, Any]] = []
    for item in itens:
        a, adiados = r.acionar(item["plano"], contexto.execucao)
        achados.extend(a)
        for m in adiados:
            contexto.diario.emitir("alarme.aberto", "regencia", {"gravidade": "baixa", "modulo": m, "aberto_em": agora(),
                                                                 "mensagem": f"motor adiado pelo governador: {r.governador.motivo()}"})
    if especial is not None:
        especial.close()
    return achados
