#!/usr/bin/env python3
"""VOO OBSERVADO — dez voos com um avaliador a bordo.

Isto é um BANCO DE PROVAS, não produção. A diferença importa e está declarada em cada linha
do relatório: aqui o contêiner não alcança buscador nenhum e não há modelo local rodando.
O que o banco faz é exercitar o CÓDIGO REAL de decisão — briefing, escolha de rumo, missão
de resgate, prospecção, avaliação, aprendizado — com os DADOS REAIS do sistema, substituindo
apenas o que o ambiente não pode fornecer, e anotando cada substituição.

A pergunta que o banco responde: **onde cada voo para, e por quê?**

Duas condições de cabine, cinco voos cada:

    voos 1 a 5    modelo MUDO — a realidade de hoje (12% de resposta)
    voos 6 a 10   modelo RESPONDENDO — para isolar o que o modelo contribui

Comparar as duas metades diz quanto do fracasso é do modelo e quanto é de arquitetura.
"""
from __future__ import annotations

import json
import random
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.nucleo import load_json  # noqa: E402

DIARIO: list[dict] = []
T0 = time.time()


def anota(voo: int, etapa: str, decisao: str, detalhe: str = "", ok: bool | None = None,
          impedimento: str = "") -> None:
    """O avaliador anota. Cada linha é uma decisão observada, não um resumo."""
    DIARIO.append({"voo": voo, "t": round(time.time() - T0, 2), "etapa": etapa,
                   "decisao": decisao, "detalhe": detalhe[:220], "ok": ok,
                   "impedimento": impedimento})
    marca = "  " if ok is None else ("✓ " if ok else "✗ ")
    imp = f"   [banco: {impedimento}]" if impedimento else ""
    print(f"  {marca}{etapa:<22} {decisao}{(' — ' + detalhe[:90]) if detalhe else ''}{imp}")


class IAMuda:
    """O ocupante de hoje: responde a 12% dos pedidos."""
    nome = "mudo (Llama-3.2-3B como está)"

    def __init__(self, semente: int):
        self.r = random.Random(semente)
        self.pedidos = self.respostas = 0

    def perguntar(self, p, esquema=None):
        self.pedidos += 1
        if self.r.random() < 0.12:
            self.respostas += 1
            return _resposta_plausivel(p, esquema)
        return None


class IAFalante:
    """O ocupante que o cargo exige: responde sempre, com JSON válido."""
    nome = "respondendo (hipótese de um reserva que cumpre o critério)"

    def __init__(self, semente: int):
        self.r = random.Random(semente)
        self.pedidos = self.respostas = 0

    def perguntar(self, p, esquema=None):
        self.pedidos += 1
        self.respostas += 1
        return _resposta_plausivel(p, esquema, self.r)


def _resposta_plausivel(p: str, esquema=None, r: random.Random | None = None):
    """Resposta no formato que o código espera. Conteúdo verossímil, nunca dado real."""
    r = r or random.Random(0)
    t = (p or "").lower()
    if "prestes a decolar" in t or "biblioteca hoje" in t.replace("_", " "):
        m = load_json(RAIZ / "config/motor_piloto.json")
        a = r.choice(m.get("angulos_de_ataque") or [{"id": "x", "pergunta": "onde há recurso?", "nivel": "nacional"}])
        return {"diagnostico": "o acervo é quase todo fonte pública",
                "aposta": {"onde": a["id"], "porque": "setor com caixa e pouco procurado", "confianca": "media"},
                "pergunta_de_pesquisa": a["pergunta"], "o_que_procurar": ["site oficial"],
                "nivel": a.get("nivel", "nacional")}
    if "missão especial" in t or "resgate de edital" in t:
        return {"consultas": [f"edital página oficial {r.randint(1, 99)}"],
                "onde_provavelmente_esta": "portal do órgão", "o_que_ler_na_pagina": ["prazo"]}
    if "procuro este edital" in t:
        return {"e_este_edital": False}
    if "páginas que listam apoiadores" in t or "missão de expansão" in t:
        return {"consultas": ["\"nossos parceiros\" associação Goiás"]}
    if "serve" in t and "achados" in t:
        return {"itens": [], "o_que_melhorar_no_motor": "filtrar por 'chamamento' antes de abrir"}
    if "consultas" in str(esquema or ""):
        return {"consultas": ["consulta de banco de provas"]}
    return None


def voo(n: int, ia) -> dict:
    """Um voo completo, anotado etapa a etapa."""
    from src.briefing_piloto import escrever as brief, fechar as fecha_brief
    from src.missao_especial import montar_fila, proximo, devolver_a_fila
    from src.cobertura import ja_coberto, mapa

    print(f"\n── VOO {n:02d} · cabine: {ia.nome}")
    res = {"voo": n, "cabine": ia.nome, "etapas": 0, "achados": 0, "parou_em": None}

    # 1 · BRIEFING
    b = brief(ia)
    mudo = bool(b.get("modelo_mudo"))
    anota(n, "briefing", "rumo definido" if not mudo else "modelo mudo → rumo sorteado",
          f"{(b.get('aposta') or {}).get('onde')} · {b.get('nivel')}", ok=not mudo)
    res["rumo"] = (b.get("aposta") or {}).get("onde")
    res["modelo_mudo_no_briefing"] = mudo
    res["etapas"] += 1

    # 2 · MAPA DE COBERTURA
    m = mapa()
    anota(n, "cobertura", f"{m['dominios_cobertos']} domínios a evitar", "não repetir o que os motores já leem", ok=True)
    res["etapas"] += 1

    # 3 · FILA DE RESGATE
    montar_fila()
    alvo = proximo()
    if alvo:
        anota(n, "fila de resgate", f"reservou «{str(alvo.get('titulo'))[:46]}»",
              f"urgência {alvo.get('urgencia')} · falta {len(alvo.get('falta') or [])} dado(s)", ok=True)
        res["etapas"] += 1
        # 4 · RESGATE: primeiro o site do órgão
        VETOR_DOM = ("pncp.gov.br", "in.gov.br", "queridodiario.ok.org.br", "diariooficial")
        dominio = None
        for campo in ("pagina_oficial", "site", "url"):
            u = alvo.get(campo)
            if u and str(u).startswith("http"):
                from urllib.parse import urlsplit
                h = (urlsplit(str(u)).hostname or "").replace("www.", "")
                if h and not any(v in h for v in VETOR_DOM):
                    dominio = h
                    break
        if dominio:
            anota(n, "resgate·site do órgão", f"tentaria ler {dominio}", "sitemap do próprio portal",
                  ok=False, impedimento="sem rede no contêiner")
            res["parou_em"] = "rede: leitura do site do órgão"
        else:
            anota(n, "resgate·site do órgão", "sem domínio conhecido no alvo",
                  "o edital não trouxe página oficial — é justamente o que falta", ok=False)
            res["parou_em"] = "alvo sem domínio: nada para ler"
        anota(n, "resgate·buscador", "segunda via não acionada",
              "o buscador só entra se o site do órgão falhar por conteúdo, não por rede",
              ok=False, impedimento="sem rede no contêiner")
        devolver_a_fila(alvo["id"], tentado=True)
        res["etapas"] += 1
    else:
        anota(n, "fila de resgate", "fila vazia", "nada a resgatar", ok=False)
        res["parou_em"] = "fila vazia"

    # 5 · PROSPECÇÃO
    from src.piloto_busca import buscar
    consulta = f"\"nossos parceiros\" associação {n}"
    r = buscar(consulta, maximo=3, tempo=5)
    anota(n, "prospecção·busca", f"{len(r)} resultado(s)", consulta, ok=bool(r),
          impedimento="" if r else "sem rede no contêiner")
    if not res["parou_em"]:
        res["parou_em"] = "rede: busca de apoiadores"
    res["etapas"] += 1

    # 6 · CRIVO DE COBERTURA (funciona sem rede)
    amostra = ["https://www.in.gov.br/dou/edital", "https://institutodesconhecido.org.br/apoio"]
    descartados = [u for u in amostra if ja_coberto(u)[0]]
    anota(n, "crivo de cobertura", f"{len(descartados)} de {len(amostra)} descartado(s)",
          "domínio já lido por motor não é trabalho do Piloto", ok=True)
    res["etapas"] += 1

    # 7 · AVALIAÇÃO E APRENDIZADO
    from src.aprendizados_piloto import avaliar
    a = avaliar(ia, {"motor": "sindico-aberto", "tipo": "cacar_oportunidade",
                     "licao": "a busca não devolveu resultado (rede ou bloqueio)"}, [])
    av = a["avaliacao"]
    anota(n, "aprendizado", f"motivo registrado: {av.get('motivo_do_insucesso')}",
          av.get("explicacao") or "", ok=True)
    res["motivo"] = av.get("motivo_do_insucesso")
    res["etapas"] += 1

    fecha_brief(b, [])
    res["pedidos_ao_modelo"] = ia.pedidos
    res["respostas_do_modelo"] = ia.respostas
    return res


def main() -> int:
    import os
    import tempfile
    tmp = tempfile.mkdtemp(prefix="voo-observado-")
    os.environ["ELDORADO_APRENDIZADOS"] = tmp        # o banco não suja a base de produção
    import importlib
    import src.aprendizados_piloto as A
    importlib.reload(A)

    print("=" * 78)
    print("BANCO DE PROVAS · 10 VOOS OBSERVADOS")
    print("Código e dados reais. Sem rede e sem modelo local — cada substituição é anotada.")
    print("=" * 78)

    voos = []
    for i in range(1, 11):
        ia = IAMuda(i) if i <= 5 else IAFalante(i)
        voos.append(voo(i, ia))

    mudos = [v for v in voos if v["voo"] <= 5]
    falantes = [v for v in voos if v["voo"] > 5]
    rel = {
        "em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "natureza": "banco de provas: código e dados reais, sem rede e sem modelo local",
        "voos": voos, "diario": DIARIO,
        "comparacao": {
            "com_modelo_mudo": {"voos": len(mudos),
                                "rumos_distintos": len({v["rumo"] for v in mudos}),
                                "etapas_medias": round(sum(v["etapas"] for v in mudos) / len(mudos), 1)},
            "com_modelo_respondendo": {"voos": len(falantes),
                                       "rumos_distintos": len({v["rumo"] for v in falantes}),
                                       "etapas_medias": round(sum(v["etapas"] for v in falantes) / len(falantes), 1)},
        },
        "onde_pararam": {},
    }
    for v in voos:
        rel["onde_pararam"][v["parou_em"] or "concluiu"] = rel["onde_pararam"].get(v["parou_em"] or "concluiu", 0) + 1

    saida = RAIZ / "estado/piloto/voo_observado_2026-09-23.json"
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")

    print("\n" + "=" * 78)
    print("RESUMO")
    print(f"  rumos distintos — modelo mudo: {rel['comparacao']['com_modelo_mudo']['rumos_distintos']}/5"
          f" · modelo respondendo: {rel['comparacao']['com_modelo_respondendo']['rumos_distintos']}/5")
    print(f"  onde os voos pararam: {rel['onde_pararam']}")
    print(f"  diário: {len(DIARIO)} decisões anotadas → {saida.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
