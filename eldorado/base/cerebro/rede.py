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


def caracteristicas_livro(lv: dict[str, Any]) -> dict[str, float]:
    """02/11/2026 (titular): o que um LIVRO tem (não um achado): o território, a esfera, a modalidade, a área, o tipo do
    link oficial, o órgão, o motor que o trouxe e as palavras do título. Ensaio prequencial com cada livro uma vez:
    AUC 0,93 (0,95 nos mais recentes), contra 0,48 da rede treinada com os achados barrados."""
    f: dict[str, float] = {"vies": 1.0}
    for k in ("uf", "abrangencia", "esfera", "area", "link_oficial_tipo"):
        if lv.get(k):
            f[f"{k}={str(lv[k]).lower()[:30]}"] = 1.0
    if lv.get("modalidade"):
        f["mod=" + re.sub(r"\s+", " ", str(lv["modalidade"]).lower())[:25]] = 1.0
    if lv.get("orgao"):
        f["orgao=" + str(lv["orgao"]).lower()[:30]] = 1.0
    if lv.get("motor"):
        f["motor=" + str(lv["motor"])] = 1.0
    f["tem_link_oficial"] = 1.0 if lv.get("link_oficial") else 0.0
    for p in sorted(set(PALAVRA.findall(str(lv.get("titulo") or "").lower())))[:25]:
        f[f"p={p}"] = 1.0
    return f


SQL_LIVROS = ("SELECT l.id, l.titulo, l.orgao, l.uf, l.link_oficial, l.situacao, d.abrangencia, d.esfera, d.modalidade, d.area, "
              "d.link_oficial_tipo FROM livro l LEFT JOIN livro_dados d ON d.livro_id = l.id")


def livros_para_a_rede(biblioteca, onde: str = "", args: tuple = ()) -> dict[str, dict[str, Any]]:
    """Os livros com as características da rede (e o motor que trouxe cada um: o do primeiro achado)."""
    import sqlite3
    antes = biblioteca.row_factory
    biblioteca.row_factory = sqlite3.Row
    try:
        lv = {r["id"]: dict(r) for r in biblioteca.execute(SQL_LIVROS + (" " + onde if onde else ""), args)}
        for i, m in biblioteca.execute("SELECT livro_id, motor FROM achado WHERE livro_id IS NOT NULL ORDER BY encontrado_em DESC"):
            if i in lv:
                lv[i]["motor"] = m                                  # em ordem decrescente: fica o do primeiro achado
    finally:
        biblioteca.row_factory = antes
    return lv


class Rede:
    def __init__(self, lr: float = 0.1, limiar: float = 0.5):
        self.modelo = linear_model.LogisticRegression(optimizer=optim.SGD(lr))
        self.limiar = limiar                                        # 02/11/2026: o limiar de decisão de cada pergunta (benchmark)
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
        self.precisao.update(valido, p.get(True, 0.0) >= getattr(self, "limiar", 0.5))
        self.revocacao.update(valido, p.get(True, 0.0) >= getattr(self, "limiar", 0.5))
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
    """Esta ação vai trazer informação nova para este livro?

    02/11/2026 (benchmark): mais o contexto da tentativa — quantas o livro já teve, o regime da oportunidade, o território,
    o prazo e quantos itens faltam (AUC prequencial 0,797 → 0,844; Brier 0,166 → 0,143)."""
    f = {"vies": 1.0, f"acao={acao}": 1.0, f"dominio={_host(livro.get('link_oficial'))}": 1.0, f"estrela={livro.get('estrela') or 'sem'}": 1.0,
         f"acao_estrela={acao}|{livro.get('estrela') or 'sem'}": 1.0}
    faltam = livro.get("faltam") or []
    for item in faltam:
        f[f"falta={item}"] = 1.0
        f[f"acao_falta={acao}|{item}"] = 1.0
    if livro.get("tentativas_n") is not None:
        k = min(int(livro["tentativas_n"]), 6)
        f[f"tentativa_n={k}"] = 1.0
        f[f"acao_n={acao}|{k}"] = 1.0
    if livro.get("titulo") is not None or livro.get("modalidade") is not None:
        from ...motores.pilotos.interceptador import regime_de
        rg = regime_de(livro.get("titulo") or "", livro.get("modalidade"))
        f[f"regime={rg}"] = 1.0
        f[f"acao_regime={acao}|{rg}"] = 1.0
    if livro.get("abrangencia"):
        f[f"abr={livro['abrangencia']}"] = 1.0
    if "fim" in livro:
        ref = str(livro.get("em") or agora())[:10]
        f["prazo=" + ("aberto" if livro["fim"] and livro["fim"] >= ref else "encerrado" if livro["fim"] else "sem")] = 1.0
    f[f"nfaltam={min(len(faltam), 8)}"] = 1.0
    return f


def car_motor(motor: str, hora: int, dia: int, recentes: list[bool] | None = None) -> dict[str, float]:
    """Este motor vai encontrar algo agora?

    02/11/2026 (benchmark): mais o resultado das últimas execuções do próprio motor (AUC 0,829 → 0,852; Brier 0,126 → 0,110)."""
    f = {"vies": 1.0, f"motor={motor}": 1.0, f"hora={hora}": 1.0, f"dia={dia}": 1.0, f"motor_hora={motor}|{hora}": 1.0,
         f"motor_dia={motor}|{dia}": 1.0}
    if recentes is not None:
        if recentes:
            u = int(recentes[-1])
            f[f"ultimo={u}"] = 1.0
            f[f"motor_ultimo={motor}|{u}"] = 1.0
            f[f"taxa5={round(sum(recentes) / len(recentes), 1)}"] = 1.0
        else:
            f["sem_historico"] = 1.0
    return f


class _Pergunta(Rede):
    def __init__(self, car, lr: float = 0.1, limiar: float = 0.5):
        super().__init__(lr, limiar)
        self._car = car

    lote = None                                                    # o modelo em lote, quando discerne melhor (cerebro/lote.py)

    def nota_de(self, x: dict[str, float]) -> float:
        if self.lote is not None:
            return self.lote.nota(x)
        return float(self.modelo.predict_proba_one(x).get(True, 0.5))

    def aprender_de(self, x: dict[str, float], valido: bool) -> None:
        p = self.modelo.predict_proba_one(x)                       # primeiro prevê (avaliação honesta), depois aprende
        self.discernimento.update(valido, p)
        self.precisao.update(valido, p.get(True, 0.0) >= getattr(self, "limiar", 0.5))
        self.revocacao.update(valido, p.get(True, 0.0) >= getattr(self, "limiar", 0.5))
        self.brier_soma += (p.get(True, 0.5) - (1.0 if valido else 0.0)) ** 2
        self.modelo.learn_one(x, valido)
        self.amostras += 1


class RedeNeural:
    """A rede do Cérebro: reaprende a cada ciclo com o histórico inteiro dos bancos, em ordem cronológica (nada se
    perde entre as execuções), e responde às três perguntas que as decisões fazem."""
    PERGUNTAS = ("oportunidade", "acao", "motor")

    # 02/11/2026 (benchmark prequencial, estudos/bench_rede_2026_11_02.py): a taxa e o limiar de cada pergunta
    CONFIG = {"oportunidade": (0.2, 0.5), "acao": (0.1, 0.45), "motor": (0.1, 0.35)}

    def __init__(self):
        self.p = {k: _Pergunta(None, *self.CONFIG[k]) for k in self.PERGUNTAS}
        self.motor_recentes: dict[str, list[bool]] = {}

    def nota_oportunidade(self, livro: dict[str, Any]) -> float:
        return self.p["oportunidade"].nota_de(caracteristicas_livro(livro))

    def nota_acao(self, acao: str, livro: dict[str, Any]) -> float:
        return self.p["acao"].nota_de(car_acao(acao, livro))

    def nota_motor(self, motor: str, hora: int, dia: int) -> float:
        return self.p["motor"].nota_de(car_motor(motor, hora, dia, (getattr(self, "motor_recentes", {}) or {}).get(motor, [])))

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
        # oportunidade (02/11/2026, titular): só LIVROS, cada um uma vez — o veredito final do Chrome ou da titular (o
        # «pendente» não é resposta), ou a chegada ao Farol; os achados barrados no portão são outra população e
        # ensinavam a rede a reconhecer barrados, não livros (o ensaio de 29/10 dava 0,48 sobre livros)
        livros = livros_para_a_rede(biblioteca)
        biblioteca.row_factory = sqlite3.Row
        rotulo: dict[str, bool] = {}
        primeiro: dict[str, str] = {}
        for r in biblioteca.execute("SELECT livro_id, decisao, em FROM veredito WHERE decisao <> 'pendente' ORDER BY em"):
            if r["livro_id"] in livros:
                rotulo[r["livro_id"]] = r["decisao"] not in ("descartar", "invalido", "excluir")
                primeiro.setdefault(r["livro_id"], r["em"])
        for r in biblioteca.execute("SELECT livro_id, MIN(em) AS em FROM passagem WHERE para = 'farol' GROUP BY livro_id"):
            if r["livro_id"] in livros and r["livro_id"] not in rotulo:
                rotulo[r["livro_id"]], primeiro[r["livro_id"]] = True, r["em"]
        for lid, y in rotulo.items():
            casos.append((primeiro[lid] or "", "oportunidade", caracteristicas_livro(livros[lid]), y))
        # ação: cada tentativa na etapa 3, e se o Cartório certificou algo novo para o livro depois dela
        certs: dict[str, list[str]] = {}
        for r in biblioteca.execute("SELECT livro_id, em FROM certidao WHERE situacao IN ('comprovado','dispensado') ORDER BY em"):
            certs.setdefault(r["livro_id"], []).append(r["em"])
        estrela = {r["id"]: r["estrela"] for r in biblioteca.execute("SELECT id, estrela FROM livro")}
        fim = {r["livro_id"]: r["inscricao_fim"] for r in biblioteca.execute("SELECT livro_id, inscricao_fim FROM livro_dados")}
        n_tent: dict[str, int] = {}
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
            casos.append((r["em"], "acao", car_acao(acao, {**lv, "estrela": estrela.get(r["livro_id"]), "faltam": res.get("faltam") or [],
                                                           "tentativas_n": n_tent.get(r["livro_id"], 0), "fim": fim.get(r["livro_id"]),
                                                           "em": r["em"]}), bool(trouxe)))
            n_tent[r["livro_id"]] = n_tent.get(r["livro_id"], 0) + 1
        # motor: cada execução (achou ou não)
        fuso = ZoneInfo("America/Sao_Paulo")
        from ...motores.canal.motor import apelidos
        ap = apelidos()
        recentes: dict[str, list[bool]] = {}
        for m, ini, ach in sorted(cerebro.execute("SELECT motor, inicio, achados FROM execucao_motor").fetchall(), key=lambda r: str(r[1])):
            t = datetime.fromisoformat(ini).astimezone(fuso)
            mm = ap.get(m, m)
            casos.append((ini, "motor", car_motor(mm, t.hour, t.weekday(), list(recentes.get(mm, []))), (ach or 0) > 0))
            recentes[mm] = (recentes.get(mm, []) + [(ach or 0) > 0])[-5:]
        rede.motor_recentes = recentes
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
    # 02/11/2026 (titular): a rede retreinada só com livros (AUC prequencial 0,93); a avaliação dos pendentes religada
    # (parâmetro avaliar_pendentes = true no nó). A nota informa a Sala e o Comandante; não arquiva nem decide sozinha.
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
        livros = list(livros_para_a_rede(
            b, "JOIN passaporte p ON p.livro_id = l.id WHERE p.fase IN ('recepcao', 'preparacao', 'analise externa') "
               "AND l.situacao NOT IN ('excluido', 'unido') AND COALESCE(l.estrela, 'sem') <> 'ouro'").values())
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

