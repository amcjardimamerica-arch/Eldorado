"""O motor de indicadores: ponto, círculo e linhas de cada arquivo, e a agregação por componente, parte e sistema.

- Ponto (funciona): sem recibo, cinza; a última chamada falhou, vermelho; alguma falhou e a última deu certo,
  amarelo; todas certas, verde.
- Círculo (atinge a finalidade): a métrica do arquivo. Até a fase do arquivo ter a sua métrica própria, vale a taxa
  de sucesso das chamadas (≥ 95% verde, ≥ 80% amarelo, abaixo disso vermelho).
- Linhas (ligações): das ligações declaradas no catálogo, quantas foram de fato exercidas na passagem.
- Agregação: componente vermelho se um arquivo crítico está vermelho; amarelo se 20% ou mais estão sem medição;
  parte vermelha se um componente está vermelho, amarela se menos de 80% dos componentes estão verdes; o sistema
  é a pior parte, e vermelho com alarme crítico aberto.
Arquivo ainda não construído fica cinza: é a verdade, e não um defeito escondido.
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from ..nucleo.eventos import Diario, agora

ORDEM = {"r": 3, "a": 2, "v": 1, "c": 0}


def arquivo_de(modulo: str) -> str | None:
    """'eldorado.base.cerebro.regencia:no_planejar' → 'eldorado/base/cerebro/regencia.py'."""
    if ":" not in modulo:
        return None
    return modulo.split(":", 1)[0].replace(".", "/") + ".py"


def _ponto(recibos: list[dict[str, Any]]) -> str:
    if not recibos:
        return "c"
    if not recibos[-1]["ok"]:
        return "r"
    return "a" if any(not r["ok"] for r in recibos) else "v"


def _circulo(recibos: list[dict[str, Any]]) -> tuple[str, float | None]:
    if not recibos:
        return "c", None
    taxa = sum(1 for r in recibos if r["ok"]) / len(recibos)
    return ("v" if taxa >= 0.95 else "a" if taxa >= 0.8 else "r"), round(taxa, 4)


class Medicao:
    def __init__(self, catalogo: list[dict[str, Any]]):
        self.catalogo = {a["arquivo"]: a for a in catalogo}

    @classmethod
    def do_arquivo(cls, caminho: str | Path = "config/arquivos.json") -> "Medicao":
        return cls(json.loads(Path(caminho).read_text(encoding="utf-8"))["arquivos"])

    def calcular(self, recibos: list[dict[str, Any]], alarmes_criticos: int = 0,
                 evidencias: dict[str, tuple[bool | None, str]] | None = None) -> dict[str, Any]:
        por_arquivo: dict[str, list[dict[str, Any]]] = defaultdict(list)
        por_motor: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for r in recibos:
            arq = arquivo_de(r["modulo"])
            (por_arquivo[arq] if arq in self.catalogo else por_motor[r["modulo"]]).append(r)
        exercidos = set(por_arquivo)
        arquivos: dict[str, dict[str, Any]] = {}
        for arq, info in self.catalogo.items():
            rs = por_arquivo.get(arq, [])
            circulo, valor = _circulo(rs)
            if not rs:
                linhas = "c"
            elif not info["ligacoes"]:
                linhas = "v"
            else:
                feitas = sum(1 for lig in info["ligacoes"] if lig in exercidos)
                linhas = "v" if feitas == len(info["ligacoes"]) else ("a" if feitas else "c")
            arquivos[arq] = {"ponto": _ponto(rs), "circulo": circulo, "linhas": linhas, "valor": valor,
                             "motivo": f"{len(rs)} chamada(s); métrica: {info['metrica']}" if rs else "sem chamada nesta passagem"}
            ev = (evidencias or {}).get(arq)
            if not rs and ev:   # 29/10/2026: o que o GitHub executa (fluxos, gravar.sh) e as configurações: medidos pela evidência
                ok, mot = ev
                cor = "v" if ok else ("r" if ok is False else "c")
                arquivos[arq] = {"ponto": cor, "circulo": cor, "linhas": "v" if ok else "c", "valor": 1.0 if ok else (0.0 if ok is False else None),
                                 "motivo": mot}
        motores = {m: {"ponto": _ponto(rs), "circulo": _circulo(rs)[0], "linhas": "v", "valor": _circulo(rs)[1], "motivo": f"{len(rs)} acionamento(s)"}
                   for m, rs in por_motor.items()}
        componentes: dict[str, dict[str, Any]] = {}
        grupos: dict[str, list[str]] = defaultdict(list)
        for arq, info in self.catalogo.items():
            grupos[info["componente"]].append(arq)
        for comp, arqs in grupos.items():
            criticos_vermelhos = [a for a in arqs if self.catalogo[a]["critico"] and "r" in (arquivos[a]["ponto"], arquivos[a]["circulo"])]
            sem = sum(1 for a in arqs if arquivos[a]["ponto"] == "c") / len(arqs)
            cor = "r" if criticos_vermelhos else ("a" if sem >= 0.2 else "v")
            motivo = f"{len(arqs)} arquivo(s), {sem:.0%} sem medição"
            if criticos_vermelhos:
                motivo += f"; críticos vermelhos: {', '.join(criticos_vermelhos)}"
            componentes[comp] = {"ponto": cor, "circulo": cor, "linhas": "c", "valor": round(1 - sem, 4), "motivo": motivo,
                                 "parte": self.catalogo[arqs[0]]["parte"]}
        partes: dict[str, dict[str, Any]] = {}
        for parte in sorted({c["parte"] for c in componentes.values()}):
            cs = [c for c in componentes.values() if c["parte"] == parte]
            verdes = sum(1 for c in cs if c["ponto"] == "v") / len(cs)
            cor = "r" if any(c["ponto"] == "r" for c in cs) else ("a" if verdes < 0.8 else "v")
            partes[parte] = {"ponto": cor, "circulo": cor, "linhas": "c", "valor": round(verdes, 4), "motivo": f"{len(cs)} componente(s), {verdes:.0%} verdes"}
        pior = max((p["ponto"] for p in partes.values()), key=lambda c: ORDEM[c], default="c")
        if alarmes_criticos:
            pior = "r"
        sistema = {"ponto": pior, "circulo": pior, "linhas": "c", "valor": None,
                   "motivo": f"pior parte; {alarmes_criticos} alarme(s) crítico(s) aberto(s)"}
        return {"arquivos": arquivos, "motores": motores, "componentes": componentes, "partes": partes, "sistema": sistema}

    @staticmethod
    def registrar(diario: Diario, resultado: dict[str, Any]) -> int:
        em = agora()
        n = 0
        for nivel, chave in (("arquivo", "arquivos"), ("motor", "motores"), ("componente", "componentes"), ("parte", "partes")):
            for marcador, m in resultado[chave].items():
                diario.emitir("medicao.registrada", "medicao", {"marcador": marcador, "nivel": nivel, "em": em, "ponto": m["ponto"],
                                                                "circulo": m["circulo"], "linhas": m["linhas"], "valor": m["valor"], "motivo": m["motivo"]})
                n += 1
        s = resultado["sistema"]
        diario.emitir("medicao.registrada", "medicao", {"marcador": "eldorado", "nivel": "sistema", "em": em, "ponto": s["ponto"],
                                                        "circulo": s["circulo"], "linhas": s["linhas"], "valor": s["valor"], "motivo": s["motivo"]})
        return n + 1


def no_medir(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Mede tudo o que foi chamado nesta passagem, lendo os recibos do diário da própria execução."""
    eventos = contexto.diario.eventos()
    recibos = [e.dados for e in eventos if e.tipo == "chamada.recibo"]
    criticos = sum(1 for e in eventos if e.tipo == "alarme.aberto" and e.dados.get("gravidade") == "critica")
    m = Medicao.do_arquivo(parametros.get("catalogo", "config/arquivos.json"))
    r = m.calcular(recibos, criticos, evidencias())
    n = Medicao.registrar(contexto.diario, r)
    return [{"medicoes": n, "sistema": r["sistema"]["ponto"], "arquivos_medidos": sum(1 for a in r["arquivos"].values() if a["ponto"] != "c")}]


def evidencias(agora_: datetime | None = None) -> dict[str, tuple[bool | None, str]]:
    """29/10/2026 (titular): a finalidade do que não é chamado pelo código da passagem, pela evidência real. Antes esses
    arquivos ficavam sempre "sem chamada nesta passagem" (sem finalidade), mesmo funcionando ou falhando de verdade."""
    from datetime import timezone as _tz

    agora_ = agora_ or datetime.now(_tz.utc)
    ev: dict[str, tuple[bool | None, str]] = {}
    try:
        g = json.loads(Path("dados/ultima_gravacao.json").read_text(encoding="utf-8"))
        idade = (agora_ - datetime.fromisoformat(g["em"])).total_seconds() / 60
        ok = bool(g.get("ok")) and idade <= 45
        mot = f"última gravação há {idade:.0f} min: {'gravou' if g.get('ok') else 'FALHOU'} ({str(g.get('resumo', ''))[-120:]})"
        ev["scripts/gravar.sh"] = (ok, mot)
        ev[".github/workflows/eldorado.yml"] = (ok, "o ciclo em funcionamento; " + mot)
    except (OSError, ValueError, KeyError):
        ev["scripts/gravar.sh"] = (None, "ainda sem gravação registrada neste ciclo")
    try:
        from ..painel.sala import _github
        q = next((f for f in _github(agora_) if f["nome"] == "Qualidade"), None)
        if q:
            c = q.get("conclusao") if q.get("situacao") == "completed" else q.get("ultima_conclusao")
            ev[".github/workflows/qualidade.yml"] = ({"success": True, "failure": False}.get(c), f"última Qualidade terminada: {c or 'nenhuma'}")
    except Exception:  # noqa: BLE001 — sem a API do GitHub, a Qualidade fica sem evidência (cinza)
        pass
    # as configurações lidas fora da passagem: a comparação (R01, na Sala) e a matriz de dispensas (no Interceptador)
    try:
        import tomllib

        cfg = tomllib.loads(Path("config/comparacao.toml").read_text(encoding="utf-8"))
        ev["config/comparacao.toml"] = (bool(cfg.get("motores")), f"a comparação R01 de {len(cfg.get('motores') or {})} motores, medida na Sala")
    except (OSError, ValueError):
        ev["config/comparacao.toml"] = (False, "o arquivo da comparação não abriu")
    try:
        reg = json.loads(Path("config/missao/dispensas_por_regime.json").read_text(encoding="utf-8")).get("regimes", {})
        ev["config/missao/dispensas_por_regime.json"] = (bool(reg), f"{len(reg)} regimes aplicados ao que o Interceptador busca")
    except (OSError, ValueError):
        ev["config/missao/dispensas_por_regime.json"] = (False, "a matriz de dispensas não abriu")
    return ev
