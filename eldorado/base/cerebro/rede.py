"""A rede neural única, de aprendizado contínuo (River): aprende a cada veredito e dá as notas.

Avaliação honesta (prequencial): para cada caso, primeiro prevê, depois aprende; as métricas medem o acerto
antes de a rede ver a resposta. O modelo fica fora do Git (dados/modelo); o Cérebro guarda as métricas de cada versão.
"""
from __future__ import annotations

import pickle
import re
from pathlib import Path
from typing import Any

from river import linear_model, metrics, optim

from ..nucleo.eventos import Diario, agora

PALAVRA = re.compile(r"[a-zà-ú]{4,}")


def caracteristicas(item: dict[str, Any]) -> dict[str, float]:
    f: dict[str, float] = {"vies": 1.0}
    for campo in ("motor", "uf", "tema", "orgao"):
        v = item.get(campo) or (item.get("dados") or {}).get(campo)
        if v:
            f[f"{campo}={str(v).lower()[:40]}"] = 1.0
    f["tem_link_oficial"] = 1.0 if item.get("link_oficial") else 0.0
    f["pista"] = 1.0 if item.get("pista") else 0.0
    for p in sorted(set(PALAVRA.findall(str(item.get("titulo") or "").lower())))[:25]:
        f[f"p={p}"] = 1.0
    return f


class Rede:
    def __init__(self):
        self.modelo = linear_model.LogisticRegression(optimizer=optim.SGD(0.1))
        self.discernimento = metrics.ROCAUC()
        self.precisao = metrics.Precision()
        self.revocacao = metrics.Recall()
        self.amostras = 0
        self.brier_soma = 0.0                                       # a calibração: a média de (probabilidade − o que aconteceu)²

    def nota(self, item: dict[str, Any]) -> float:
        return float(self.modelo.predict_proba_one(caracteristicas(item)).get(True, 0.5))

    def aprender(self, item: dict[str, Any], valido: bool) -> float:
        x = caracteristicas(item)
        p = self.modelo.predict_proba_one(x)
        self.discernimento.update(valido, p)
        self.precisao.update(valido, p.get(True, 0.0) >= 0.5)
        self.revocacao.update(valido, p.get(True, 0.0) >= 0.5)
        self.brier_soma += (p.get(True, 0.5) - (1.0 if valido else 0.0)) ** 2
        self.modelo.learn_one(x, valido)
        self.amostras += 1
        return p.get(True, 0.5)

    def metricas(self) -> dict[str, float | None]:
        if not self.amostras:
            return {"discernimento": None, "precisao": None, "revocacao": None, "brier": None}
        return {"discernimento": round(float(self.discernimento.get()), 4), "precisao": round(float(self.precisao.get()), 4),
                "revocacao": round(float(self.revocacao.get()), 4), "brier": round(self.brier_soma / self.amostras, 4)}

    def salvar(self, pasta: str | Path, diario: Diario | None = None) -> Path:
        p = Path(pasta)
        p.mkdir(parents=True, exist_ok=True)
        versao = f"{self.amostras:07d}-{agora().replace(':', '').replace('-', '')[:15]}"
        arq = p / f"rede-{versao}.pkl"
        arq.write_bytes(pickle.dumps(self))
        (p / "rede-atual.txt").write_text(arq.name)
        if diario:
            diario.emitir("modelo.treinado", "rede", {"versao": versao, "treinado_em": agora(), "arquivo": arq.name, **self.metricas()})
        return arq

    @classmethod
    def carregar(cls, pasta: str | Path) -> "Rede":
        p = Path(pasta)
        atual = p / "rede-atual.txt"
        if not atual.exists():
            return cls()
        return pickle.loads((p / atual.read_text().strip()).read_bytes())


# ---------------------------------------------------------------------- a rede neural do Cérebro: três perguntas
def _host(u: str | None) -> str:
    m = re.match(r"https?://([^/]+)", u or "")
    return m.group(1).lower().removeprefix("www.") if m else "sem link"


def car_acao(acao: str, livro: dict[str, Any]) -> dict[str, float]:
    """Esta ação vai trazer informação nova para este livro?"""
    f = {"vies": 1.0, f"acao={acao}": 1.0, f"dominio={_host(livro.get('link_oficial'))}": 1.0, f"estrela={livro.get('estrela') or 'sem'}": 1.0,
         f"acao_estrela={acao}|{livro.get('estrela') or 'sem'}": 1.0}
    for item in livro.get("faltam") or []:
        f[f"falta={item}"] = 1.0
        f[f"acao_falta={acao}|{item}"] = 1.0
    return f


def car_motor(motor: str, hora: int, dia: int) -> dict[str, float]:
    """Este motor vai encontrar algo agora?"""
    return {"vies": 1.0, f"motor={motor}": 1.0, f"hora={hora}": 1.0, f"dia={dia}": 1.0, f"motor_hora={motor}|{hora}": 1.0,
            f"motor_dia={motor}|{dia}": 1.0}


class _Pergunta(Rede):
    def __init__(self, car):
        super().__init__()
        self._car = car

    lote = None                                                    # o modelo em lote, quando discerne melhor (cerebro/lote.py)

    def nota_de(self, x: dict[str, float]) -> float:
        if self.lote is not None:
            return self.lote.nota(x)
        return float(self.modelo.predict_proba_one(x).get(True, 0.5))

    def aprender_de(self, x: dict[str, float], valido: bool) -> None:
        p = self.modelo.predict_proba_one(x)                       # primeiro prevê (avaliação honesta), depois aprende
        self.discernimento.update(valido, p)
        self.precisao.update(valido, p.get(True, 0.0) >= 0.5)
        self.revocacao.update(valido, p.get(True, 0.0) >= 0.5)
        self.brier_soma += (p.get(True, 0.5) - (1.0 if valido else 0.0)) ** 2
        self.modelo.learn_one(x, valido)
        self.amostras += 1


class RedeNeural:
    """A rede do Cérebro: reaprende a cada ciclo com o histórico inteiro dos bancos, em ordem cronológica (nada se
    perde entre as execuções), e responde às três perguntas que as decisões fazem."""
    PERGUNTAS = ("oportunidade", "acao", "motor")

    def __init__(self):
        self.p = {k: _Pergunta(None) for k in self.PERGUNTAS}

    def nota_oportunidade(self, livro: dict[str, Any]) -> float:
        return self.p["oportunidade"].nota_de(caracteristicas(livro))

    def nota_acao(self, acao: str, livro: dict[str, Any]) -> float:
        return self.p["acao"].nota_de(car_acao(acao, livro))

    def nota_motor(self, motor: str, hora: int, dia: int) -> float:
        return self.p["motor"].nota_de(car_motor(motor, hora, dia))

    lote: dict[str, Any] = {}

    def metricas(self) -> dict[str, dict]:
        return {k: {"amostras": r.amostras, **r.metricas(), **({"lote": self.lote[k]} if k in self.lote else {})} for k, r in self.p.items()}

    @classmethod
    def treinar(cls, biblioteca, cerebro) -> "RedeNeural":
        import json
        import sqlite3
        from datetime import datetime
        from zoneinfo import ZoneInfo
        rede, casos = cls(), []
        biblioteca.row_factory = sqlite3.Row
        # oportunidade: os vereditos, os livros que chegaram ao Farol (válidos) e os excluídos (inválidos)
        livros = {r["id"]: dict(r) for r in biblioteca.execute("SELECT id, titulo, orgao, uf, link_oficial, situacao FROM livro")}
        for r in biblioteca.execute("SELECT livro_id, origem, decisao, em FROM veredito"):
            if r["livro_id"] in livros:
                casos.append((r["em"], "oportunidade", caracteristicas(livros[r["livro_id"]]), r["decisao"] not in ("descartar", "invalido", "excluir")))
        for r in biblioteca.execute("SELECT livro_id, para, em FROM passagem WHERE para = 'farol'"):
            if r["livro_id"] in livros:
                casos.append((r["em"], "oportunidade", caracteristicas(livros[r["livro_id"]]), True))
        for lv in livros.values():
            if lv["situacao"] == "excluido":
                casos.append(("9999", "oportunidade", caracteristicas(lv), False))
        for r in biblioteca.execute("SELECT motor, titulo, link_oficial, dados, encontrado_em FROM achado WHERE decisao = 'barrado'"):
            try:                                                    # os barrados pela Pertinência: os exemplos negativos
                d = json.loads(r["dados"] or "{}")
            except ValueError:
                d = {}
            x = caracteristicas({"motor": r["motor"], "titulo": r["titulo"], "link_oficial": r["link_oficial"], "uf": d.get("uf"), "orgao": d.get("orgao")})
            casos.append((r["encontrado_em"] or "", "oportunidade", x, False))
        # ação: cada tentativa na etapa 3, e se o Cartório certificou algo novo para o livro depois dela
        certs: dict[str, list[str]] = {}
        for r in biblioteca.execute("SELECT livro_id, em FROM certidao WHERE situacao IN ('comprovado','dispensado') ORDER BY em"):
            certs.setdefault(r["livro_id"], []).append(r["em"])
        estrela = {r["id"]: r["estrela"] for r in biblioteca.execute("SELECT id, estrela FROM livro")}
        for r in biblioteca.execute("SELECT livro_id, ferramenta, em, resultado FROM tentativa WHERE fase = 'preparacao' ORDER BY em"):
            lv = livros.get(r["livro_id"])
            if not lv:
                continue
            try:
                res = json.loads(r["resultado"] or "{}")
            except ValueError:
                res = {}
            trouxe = any(em > r["em"] for em in certs.get(r["livro_id"], [])) and (res.get("trouxe", True) or res.get("documentos", 1))
            acao = r["ferramenta"].split(" ")[0] if r["ferramenta"].startswith("motor") else r["ferramenta"]
            casos.append((r["em"], "acao", car_acao(acao, {**lv, "estrela": estrela.get(r["livro_id"]), "faltam": res.get("faltam") or []}), bool(trouxe)))
        # motor: cada execução (achou ou não)
        fuso = ZoneInfo("America/Sao_Paulo")
        from ...motores.canal.motor import apelidos
        ap = apelidos()
        for m, ini, ach in cerebro.execute("SELECT motor, inicio, achados FROM execucao_motor"):
            t = datetime.fromisoformat(ini).astimezone(fuso)
            casos.append((ini, "motor", car_motor(ap.get(m, m), t.hour, t.weekday()), (ach or 0) > 0))
        casos = sorted(casos, key=lambda c: str(c[0]))
        for _, pergunta, x, valido in casos:
            rede.p[pergunta].aprender_de(x, valido)
        from .lote import comparar_e_ligar  # o lote (scikit-learn): usado onde discerne melhor
        rede.lote = comparar_e_ligar(rede, casos)
        return rede


_GUARDADA: dict[str, tuple[float, "RedeNeural"]] = {}


def rede_atual(dados: Path, max_idade_s: float = 900, forcar: bool = False) -> "RedeNeural | None":
    """A rede treinada guardada no processo por até 15 min (o parecer do conselho, 24/10/2026: ela era treinada três vezes
    por passagem — no planejamento, no encaminhamento e no nó da rede). O nó da rede treina (forcar) e atualiza a guardada."""
    import sqlite3
    import time as _t
    dados = Path(dados)
    k = str(dados.resolve())
    if not forcar and k in _GUARDADA and _t.monotonic() - _GUARDADA[k][0] < max_idade_s:
        return _GUARDADA[k][1]
    if not (dados / "biblioteca.db").exists() or not (dados / "cerebro.db").exists():
        return None
    b = sqlite3.connect(f"file:{dados / 'biblioteca.db'}?mode=ro", uri=True)
    c = sqlite3.connect(f"file:{dados / 'cerebro.db'}?mode=ro", uri=True)
    try:
        rede = RedeNeural.treinar(b, c)
    finally:
        b.close()
        c.close()
    _GUARDADA[k] = (_t.monotonic(), rede)
    return rede


def no_rede(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem: a rede reaprende com o histórico inteiro e registra as métricas de cada pergunta no Cérebro."""
    dados = Path(parametros.get("dados", "dados"))
    if not (dados / "biblioteca.db").exists() or not (dados / "cerebro.db").exists():
        return []
    rede = rede_atual(dados, forcar=True)                       # o nó da rede treina e atualiza a guardada
    m = rede.metricas()
    for pergunta, x in m.items():
        if x["amostras"]:
            contexto.diario.emitir("modelo.treinado", "rede", {"versao": f"{pergunta}-{x['amostras']:07d}-{agora()[:16]}", "treinado_em": agora(),
                                                               "arquivo": f"rede:{pergunta}", "discernimento": x["discernimento"],
                                                               "precisao": x["precisao"], "revocacao": x["revocacao"], "brier": x.get("brier")})
    # 29/10/2026: a avaliação dos pendentes fica DESLIGADA até a rede ser retreinada para livros: ela dá ~0,003 a tudo,
    # inclusive aos 33 livros do Farol (o discernimento de 0,996 é medido sobre achados barrados, que têm características
    # que um livro não tem). Ligar com o parâmetro avaliar_pendentes = true no nó, depois do retreino.
    avaliados = 0
    if parametros.get("avaliar_pendentes"):
        avaliados = avaliar_pendentes(rede, dados, contexto.diario, f"oportunidade-{m.get('oportunidade', {}).get('amostras', 0):07d}-{agora()[:16]}")
    return [{"rede": m, "pendentes_avaliados": avaliados}]


def avaliar_pendentes(rede: "RedeNeural", dados: Path, diario, versao: str, maximo: int = 1000, mudanca: float = 0.1) -> int:
    """29/10/2026 (titular, com o conselho): a rede dá a nota de "oportunidade real" a cada livro pendente (recepção,
    preparação e análise externa) e a registra na análise da rede (antes ela treinava e não entregava nada: a tabela
    vazia). Só registra a nota nova ou a que mudou mais de 0,1; no máximo 1.000 por passagem. A nota NÃO arquiva nem
    decide sozinha: informa a Sala e o Comandante (o Cartório e a validação continuam decidindo)."""
    import sqlite3

    b = sqlite3.connect(f"file:{Path(dados) / 'biblioteca.db'}?mode=ro", uri=True)
    b.row_factory = sqlite3.Row
    try:
        antes = {r[0]: r[1] for r in b.execute(
            "SELECT livro_id, nota FROM analise_rede WHERE id IN (SELECT MAX(id) FROM analise_rede GROUP BY livro_id)")}
        livros = [dict(r) for r in b.execute(
            "SELECT l.id, l.titulo, l.orgao, l.uf, l.link_oficial, l.situacao FROM livro l JOIN passaporte p ON p.livro_id = l.id "
            "WHERE p.fase IN ('recepcao', 'preparacao', 'analise externa') AND l.situacao NOT IN ('excluido', 'unido') "
            "AND COALESCE(l.estrela, 'sem') <> 'ouro'")]
    except sqlite3.Error:
        return 0
    finally:
        b.close()
    n = 0
    for lv in livros:
        if n >= maximo:
            break
        nota = round(rede.nota_oportunidade(lv), 4)
        anterior = antes.get(lv["id"])
        if anterior is not None and abs(nota - anterior) <= mudanca:
            continue
        diario.emitir("analise.rede", "rede", {
            "livro_id": lv["id"], "em": agora(), "nota": nota, "pertinencia": 1.0 if nota >= 0.5 else 0.0,
            "explicacao": "provável oportunidade real" if nota >= 0.5 else "provavelmente não é uma oportunidade (o Cartório confere)",
            "modelo_versao": versao})
        n += 1
    return n

