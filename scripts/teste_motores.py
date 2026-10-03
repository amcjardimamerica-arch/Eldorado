#!/usr/bin/env python3
"""TESTE DE COLETA E DESEMPENHO DOS MOTORES 01–21 (titular, 03/10/2026).

Para cada motor, um por vez, monta o DOSSIÊ do que o sistema registrou (sem rede):
  1. identidade — número do painel (config/ordem_motores.json), id e os ids antigos do mesmo motor;
  2. workflow — agenda (config/agenda_motores.json), o fluxo que dispara (agenda-motores → monitoramento-diario
     com fontes=<id>), o módulo de código e os testes;
  3. onde coleta — os endereços configurados e os que a última leitura de fato abriu (estado/esquadra.json › saude);
  4. resultado — última leitura, leituras, achados, falhas, luz do status (docs/dados/status_motores.json),
     oportunidades únicas (docs/dados/achados_motores.json) e registros na base (dados/oportunidades);
  5. histórico de 3 anos — registros da base por ano de publicação, desde 3 anos antes de hoje.

O teste AO VIVO de cada fonte é feito à parte, no navegador do titular (o ambiente de execução não alcança os portais).

    python scripts/teste_motores.py 1            # dossiê do motor 01 (JSON)
    python scripts/teste_motores.py --todos      # os 21, em sequência
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
HOJE = date.today()
INICIO_3_ANOS = date(HOJE.year - 3, HOJE.month, min(HOJE.day, 28))

# ids antigos/alternativos com que o mesmo motor gravou estado e registros (o painel renumerou em 02/10)
ALIASES = {
    "camara-goiania-pl": ["camara-goiania-emendas"],
    "judiciario-tjgo": ["dje-tjgo", "judiciario-cnj-tjgo"],
    "mpgo-destinacao": ["plat-mp-destinacoes-reparacao"],
    "mptgo-destinacao": ["plat-mp-destinacoes-reparacao"],
    "mpu-destinacao": ["plat-mp-destinacoes-reparacao"],
    "judiciario-cnj": ["cnj-destinacoes", "judiciario-cnj-tjgo"],
    "prefeituras-50-go": ["plat-prefeituras-50-go"],
    "estaduais-go-gov": ["plat-estaduais-go-gov"],
    "pncp-api": ["pncp"],
    "salic": ["plat-salic"],
    "cnpq-extensao": ["plat-cnpq-extensao"],
    "gife": ["plat-gife"],
    "empresas-editais-incentivados": ["plat-empresas-editais-incentivados", "empresas-incentivadas"],
}
MODULOS = {
    "do-goiania": "src/diario_goiania.py", "do-goias": "src/diario_goias.py", "dou": "src/diario_uniao.py",
    "camara-goiania-pl": "src/camara_goiania.py", "alego-pl": "src/sensores.py", "congresso-nacional": "src/congresso_nacional.py",
    "judiciario-tjgo": "src/judiciario_go.py", "judiciario-cnj": "src/judiciario_go.py", "mpgo-destinacao": "src/ministerios_publicos.py",
    "mptgo-destinacao": "src/ministerios_publicos.py", "mpu-destinacao": "src/ministerios_publicos.py", "dj-trf1-go": "src/sensores.py",
    "prefeituras-50-go": "src/prefeituras_25_go.py", "estaduais-go-gov": "src/estaduais_go.py", "pncp-api": "src/pncp_osc.py",
    "salic": "src/sensores.py", "cnpq-extensao": "src/sensores.py", "gife": "src/gife_editais.py",
    "empresas-editais-incentivados": "src/empresas_rotas.py", "motor-gife": "src/prospeccao.py", "motor-patrocinio": "src/prospeccao.py",
}


def _j(p: str, padrao=None):
    try:
        return json.loads((RAIZ / p).read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao


def _ano(r: dict) -> int | None:
    for k in ("data_publicacao", "data_publicacao_origem", "ano_referencia"):
        v = r.get(k)
        if v:
            m = re.match(r"(\d{4})", str(v))
            if m:
                return int(m.group(1))
    return None


def _base() -> list[dict]:
    saida = []
    with open(RAIZ / "dados/oportunidades/oportunidades.jsonl", encoding="utf-8") as fh:
        for linha in fh:
            try:
                saida.append(json.loads(linha))
            except ValueError:
                pass
    return saida


_BASE: list[dict] | None = None


def dossie(numero: int) -> dict:
    global _BASE
    pos = (_j("config/ordem_motores.json", {}) or {}).get("posicoes") or {}
    mid = next((k for k, v in pos.items() if int(v) == numero), None)
    if not mid:
        return {"numero": numero, "erro": "número fora da ordem do painel"}
    ids = [mid, f"plat-{mid}", *ALIASES.get(mid, [])]
    painel = next((o for o in ((_j("docs/dados/motores.json", {}) or {}).get("oficiais", []) +
                               (_j("docs/dados/motores.json", {}) or {}).get("plataformas", [])) if o.get("id") == mid), {})
    agenda_todos = (_j("config/agenda_motores.json", {}) or {}).get("motores") or {}
    agenda = {i: agenda_todos[i] for i in ids if i in agenda_todos}
    sensores = (_j("config/sensores.json", {}) or {}).get("sensores_especiais") or []
    sensor_cfg = [s for s in sensores if s.get("id") in ids]
    esq = ((_j("estado/esquadra.json", {}) or {}).get("sensores") or {})
    estado = {i: esq[i] for i in ids if i in esq}
    status = next((s for s in (_j("docs/dados/status_motores.json", {}) or {}).get("motores", []) if s.get("id") == mid), {})
    achados = ((_j("docs/dados/achados_motores.json", {}) or {}).get("motores") or {})
    unicas = {i: {k: achados[i].get(k) for k in ("total_registros", "total_unicas")} for i in ids if i in achados}
    if _BASE is None:
        _BASE = _base()
    regs = [r for r in _BASE if r.get("fonte_id") in ids or any(f in ids for f in (r.get("fontes_observadas") or []))]
    por_ano = Counter(_ano(r) for r in regs)
    tres = [r for r in regs if (_ano(r) or 0) >= INICIO_3_ANOS.year and str(r.get("data_publicacao") or "9999") >= INICIO_3_ANOS.isoformat()]
    anteriores = [r for r in tres if str(r.get("data_publicacao") or "") < HOJE.replace(month=1, day=1).isoformat()]
    # histórico CORRELATO: o que a base tem do mesmo site oficial (qualquer motor) e, para os diários municipais, do
    # Querido Diário do mesmo município — mostra se a fonte tem passado registrado, mesmo que o motor seja novo
    from urllib.parse import urlsplit
    urls_motor = [painel.get("url") or ""] + [u for s in sensor_cfg for u in re.findall(r"https?://[^\"'\s,]+", json.dumps(s, ensure_ascii=False))]
    dominios = {re.sub(r"^www\.", "", (urlsplit(u).hostname or "")) for u in urls_motor if u.startswith("http")}
    dominios -= {"", "api.queridodiario.ok.org.br", "html.duckduckgo.com", "bing.com", "news.google.com", "goias.gov.br", "gov.br"}
    correlatos = [r for r in _BASE if r not in regs and any(re.sub(r"^www\.", "", urlsplit(str(r.get("url") or "")).hostname or "").endswith(d) for d in dominios)]
    if mid == "do-goiania":
        correlatos += [r for r in _BASE if r.get("fonte_id") == "querido-diario" and "Goiânia" in str(r.get("municipio"))]
    corr_ano = Counter(_ano(r) for r in correlatos)
    modulo = MODULOS.get(mid)
    testes = subprocess.run(["git", "grep", "-l", "-e", mid, "--", "tests"], cwd=RAIZ, capture_output=True, text=True).stdout.split()
    if modulo:
        nome_mod = Path(modulo).stem
        testes += [t for t in subprocess.run(["git", "grep", "-l", "-e", f"src.{nome_mod}\\b", "-e", f"import {nome_mod}\\b", "--", "tests"],
                                             cwd=RAIZ, capture_output=True, text=True).stdout.split() if t not in testes]
    return {
        "numero": numero, "id": mid, "ids_relacionados": ids[1:], "nome": painel.get("nome"), "tipo": painel.get("tipo"),
        "workflow": {
            "agenda": {i: {k: a.get(k) for k in ("horarios_brt", "dias", "cadencia_dias", "coleta", "objetivo")} for i, a in agenda.items()},
            "disparo": "agenda-motores.yml (:23/:53) → monitoramento-diario.yml (fontes=<id>) → python -m src.sensores" if agenda else "sem entrada na agenda",
            "modulo": modulo, "modulo_existe": bool(modulo and (RAIZ / modulo).exists()), "testes": sorted(set(testes)),
            "sensor_configurado": [s.get("id") for s in sensor_cfg],
        },
        "onde_coleta": {
            "pagina_do_painel": painel.get("url"),
            "configurado": sorted({u for s in sensor_cfg for u in re.findall(r"https?://[^\"'\s,]+", json.dumps(s, ensure_ascii=False))})[:25],
            "aberto_na_ultima_leitura": [{"id": i, "url": x.get("url"), "http": x.get("http"), "bytes": x.get("bytes")}
                                         for i, e in estado.items() for x in (e.get("saude") or [])][:25],
        },
        "resultado": {
            "status_painel": {k: status.get(k) for k in ("luz", "resultado", "ultima_leitura")},
            "estado": {i: {k: e.get(k) for k in ("ultima", "leituras", "achados_total", "achados_ultima", "falhas_ultima",
                                                  "vazias_seguidas", "alerta", "motivo")} for i, e in estado.items()},
            "diagnostico": {i: {k: v for k, v in (e.get("diagnostico") or {}).items() if k in ("paginas_lidas", "motivo_zero", "versao", "nuvem")}
                            for i, e in estado.items()},
            "dias_outubro": [(d.get("d"), d.get("cor")) for d in (painel.get("dias") or []) if str(d.get("d", "")).startswith(f"{HOJE:%Y-%m}") and d.get("cor") != "futuro"],
            "oportunidades_unicas": unicas,
            "registros_na_base": len(regs),
            "por_status": dict(Counter(r.get("status") for r in regs).most_common()),
            "goias": sum(1 for r in regs if r.get("uf") == "GO"),
        },
        "historico_3_anos": {
            "desde": INICIO_3_ANOS.isoformat(),
            "por_ano": {str(a): por_ano[a] for a in sorted(a for a in por_ano if a)},
            "sem_data": por_ano.get(None, 0),
            "na_janela": len(tres),
            "anteriores_a_este_ano": len(anteriores),
            "anos_cobertos": sorted({_ano(r) for r in tres if _ano(r)}),
            "exemplos_anteriores": [{"data": r.get("data_publicacao"), "titulo": str(r.get("titulo"))[:110], "url": r.get("url")}
                                    for r in sorted(anteriores, key=lambda r: str(r.get("data_publicacao")))[:5]],
            "correlato": {"dominios": sorted(dominios), "registros": len(correlatos),
                          "por_ano": {str(a): corr_ano[a] for a in sorted(a for a in corr_ano if a)},
                          "fontes": dict(Counter(r.get("fonte_id") for r in correlatos).most_common(6))},
        },
    }


def main(argv: list[str]) -> int:
    alvo = range(1, 22) if "--todos" in argv else [int(a) for a in argv if a.isdigit()] or [1]
    for n in alvo:
        print(json.dumps(dossie(n), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
