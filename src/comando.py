"""REDE NEURAL DE COMANDO — maestro e rede neural são UMA coisa só (titular, 15/10/2026).

A rede neural determina o caminho de todo o fluxo; o maestro é a mão dela: aciona os motores de busca e devolve o que
foi coletado. A rede avalia o que voltou e direciona para a fase seguinte. Um ciclo, do começo ao fim:

  1. DECIDIR    quais motores ler e em que ordem — necessidade (pendente, parcial, horário vencido, adiado) somada ao
                valor esperado de cada motor (nota média que a rede deu aos achados dele);
  2. ACIONAR    o maestro roda os motores escolhidos e devolve um recibo (lidos, achados, falhas, adiados, erro);
  3. AVALIAR    a rede mede a completude de cada motor (completa · parcial · pendente · só do Brasil) e o que entrou;
  4. REACIONAR  parciais e pendentes voltam na mesma passagem enquanto houver tempo; o que só o Brasil/Chrome lê vai
                para a fila de conferência humana (estado/comando/para_chrome.json);
  5. DIRECIONAR as fases seguintes, em ordem, cada uma com RECIBO e PORTÃO: a rede decide rodar, pular (com motivo) ou
                adiar — por exemplo, sem coleta nova e com mapa recente, o recálculo do mapa não roda;
  6. VEREDITO   etapa com erro torna o ciclo VERMELHO (o fluxo do GitHub falha à vista; acabou a falha silenciosa).

Entradas por linha de comando (o fluxo 22 chama na ordem): `coleta` (1–4) · `sequencia` (5) · `veredito` (6).
Estado: estado/comando/ciclo_atual.json · estado/comando/AAAA-MM-DD.json · painel: docs/dados/comando.json
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "estado/comando"
CICLO = DIR / "ciclo_atual.json"
PAINEL = ROOT / "docs/dados/comando.json"
PARA_CHROME = DIR / "para_chrome.json"
ERRO = re.compile(r"Traceback \(most recent call last\)|^\w*Error: |falhou ou estourou", re.M)
PRAZO_COLETA_S = int(os.environ.get("COMANDO_PRAZO_COLETA_S", "2100"))


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao


def _w(p: Path, d) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def _agora() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _idade_h(p: Path) -> float:
    try:
        return (time.time() - p.stat().st_mtime) / 3600
    except OSError:
        return 1e9


# ── EXECUÇÃO COM RECIBO ────────────────────────────────────────────────────────────────────────────────────────────
def executar(etapa: str, cmd: list[str], timeout: int, env: dict | None = None) -> dict:
    """Roda um passo e devolve o recibo: código, tempo, erro (Traceback ou exceção), fim da saída."""
    t0 = time.time()
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout,
                           env={**os.environ, "PYTHONUNBUFFERED": "1", **(env or {})})
        saida, rc = (r.stdout or "") + (r.stderr or ""), r.returncode
    except subprocess.TimeoutExpired as e:
        saida, rc = str(e.stdout or "")[-4000:] + "\nestourou o tempo", 124
    erro = None
    if rc != 0 or ERRO.search(saida):
        linhas = [l for l in saida.splitlines() if ERRO.search(l) or re.match(r"\s*\w+(Error|Exception)\b", l)]
        erro = (linhas[-1] if linhas else f"código {rc}")[:300]
    return {"etapa": etapa, "rc": rc, "segundos": round(time.time() - t0, 1), "erro": erro, "saida": saida[-3000:]}


# ── 1. DECIDIR ─────────────────────────────────────────────────────────────────────────────────────────────────────
def valor_por_motor() -> dict:
    """Valor esperado de cada motor: nota média que a rede neural deu aos registros dele no repositório (0–1).
    O repositório guarda a origem em texto ("motor pncp-api", "motor Querido Diário — …"): casa por código ou nome."""
    regs = (_j(ROOT / "dados/oportunidades/repositorio_unico.json", {}) or {}).get("registros") or []
    try:
        from .sensores import registro
        chaves = [(str(x["id"]).lower(), str(x.get("nome") or "").lower()) for x in registro()]
    except Exception:  # noqa: BLE001
        chaves = []
    soma: dict = {}
    for r in regs:
        n = r.get("nota_rede")
        o = re.sub(r"^motor\s+", "", str(r.get("origem") or "").lower()).strip()
        if not isinstance(n, (int, float)) or not o:
            continue
        m = next((i for i, nome in chaves if o.startswith(i) or (nome and (o.startswith(nome[:30]) or nome.startswith(o[:30])))), None)
        if m:
            t = soma.setdefault(m, [0.0, 0]); t[0] += n; t[1] += 1
    return {m: round(t[0] / t[1], 3) for m, t in soma.items() if t[1]}


def decidir_coleta() -> dict:
    sys.path.insert(0, str(ROOT / "scripts")); sys.path.insert(0, str(ROOT))
    import motores_da_vez as MV                                   # necessidade: maestro (pendente/parcial) + agenda + adiados
    ids = MV.lista(disparar=True)
    adiados = set(((_j(ROOT / "estado/esquadra.json", {}) or {}).get("ultima_execucao") or {}).get("adiados_por_tempo") or [])
    val = valor_por_motor()
    pos = {m: i for i, m in enumerate(ids)}
    ordem = sorted(ids, key=lambda m: (m not in adiados, -(val.get(m, 0.3)), pos[m]))   # adiado primeiro; depois o mais valioso
    return {"motores": ordem, "adiados": sorted(adiados & set(ids)), "valor": {m: val.get(m) for m in ordem}}


# ── 2. ACIONAR (o maestro) ─────────────────────────────────────────────────────────────────────────────────────────
def acionar(motores: list[str], prazo_s: int) -> dict:
    if not motores:
        return {"etapa": "acionar", "rc": 0, "segundos": 0, "erro": None, "saida": "nenhum motor da vez", "motores": []}
    r = executar("acionar", [sys.executable, "-m", "src.sensores"], prazo_s + 180,
                 {"MOTORES_FONTES": ",".join(motores), "SENSORES_PRAZO_S": str(prazo_s)})
    u = (_j(ROOT / "estado/esquadra.json", {}) or {}).get("ultima_execucao") or {}
    r.update({"motores": motores, "executados": u.get("sensores_executados"), "achados": u.get("achados"),
              "novos_na_base": u.get("novos_na_base"), "adiados_por_tempo": u.get("adiados_por_tempo") or []})
    try:
        with open(ROOT / "estado/log_sensores.txt", "a", encoding="utf-8") as fh:
            fh.write(f"\n[comando {_agora()}] motores: {','.join(motores)}\n{r['saida']}\n")
    except OSError:
        pass
    return r


# ── 3–4. AVALIAR e REACIONAR ───────────────────────────────────────────────────────────────────────────────────────
def avaliar_coleta(motores: list[str]) -> dict:
    """Completude de cada motor acionado, medida pelo maestro (que agora é a mão da rede)."""
    from .maestro import controlar, relatorio_etapas
    c = controlar(disparar=False)
    try:
        relatorio_etapas(controle=c)                 # o relatório do dia que o painel do maestro mostra
    except Exception:  # noqa: BLE001
        pass
    plano = {p["motor"]: p for p in c.get("plano") or []}
    estado = {m: (plano.get(m) or {}).get("cobertura", "fora_do_plano") for m in motores}
    reacionar = [m for m, e in estado.items() if e in ("parcial", "pendente") and int((plano.get(m) or {}).get("tentativas_hoje") or 0) < 3]
    humano = [m for m, e in estado.items() if e == "pendente_local"]
    return {"cobertura_do_dia_pct": c.get("cobertura_percentual"), "estado": estado, "reacionar": reacionar, "para_humano": humano,
            "completos": sum(1 for e in estado.values() if e == "completa")}


def ciclo_coleta() -> dict:
    t0 = time.time()
    ciclo = {"inicio": _agora(), "recibos": [], "decisoes": []}
    d = decidir_coleta()
    ciclo["decisoes"].append({"fase": "decidir", "motores": len(d["motores"]), "adiados_primeiro": d["adiados"]})
    r = acionar(d["motores"], PRAZO_COLETA_S); ciclo["recibos"].append(_sem_saida(r))
    av = avaliar_coleta(d["motores"])
    ciclo["avaliacao"] = av
    resto = PRAZO_COLETA_S - (time.time() - t0)
    if av["reacionar"] and resto > 300:                               # reaciona na mesma passagem, com o tempo que sobra
        r2 = acionar(av["reacionar"], int(resto - 120)); r2["etapa"] = "reacionar"; ciclo["recibos"].append(_sem_saida(r2))
        av2 = avaliar_coleta(d["motores"]); ciclo["avaliacao"] = av2
        ciclo["decisoes"].append({"fase": "reacionar", "motores": av["reacionar"], "completos_depois": av2["completos"]})
    elif av["reacionar"]:
        ciclo["decisoes"].append({"fase": "reacionar", "adiado_para_a_proxima_passagem": av["reacionar"], "motivo": "sem tempo nesta passagem"})
    if ciclo["avaliacao"]["para_humano"]:
        fila = _j(PARA_CHROME, {"itens": {}})
        for m in ciclo["avaliacao"]["para_humano"]:
            fila["itens"][m] = {"desde": fila["itens"].get(m, {}).get("desde") or _agora(), "motivo": "parte da fonte só abre do Brasil ou proíbe robôs"}
        _w(PARA_CHROME, fila)
    ciclo["novos_na_base"] = sum(int(x.get("novos_na_base") or 0) for x in ciclo["recibos"])
    _w(CICLO, ciclo)
    return ciclo


def _sem_saida(r: dict) -> dict:
    return {k: v for k, v in r.items() if k != "saida"}


# ── 5. DIRECIONAR as fases seguintes ───────────────────────────────────────────────────────────────────────────────
def _hoje_brt() -> str:
    from .maestro import hoje_brt
    return hoje_brt().isoformat()


def fases(ctx: dict) -> list[dict]:
    """(etapa, finalidade, comando, tempo, decisão da rede). A decisão devolve None (roda) ou o motivo de pular."""
    py = sys.executable
    novos = int(ctx.get("novos_na_base") or 0)
    mapa = ROOT / "dados/fluxo_oportunidades.json"
    diaria = (ROOT / "estado/biblioteca_diaria.txt")
    feita_hoje = diaria.exists() and diaria.read_text(encoding="utf-8").strip() == _hoje_brt()
    from .rede_neural import precisa_treinar
    return [
        {"etapa": "painel_motores", "finalidade": "achados, status e cobertura de cada motor",
         "cmds": [[py, "-m", "src.achados_motores"], [py, "-c", "import src.motores as M; M.run()"], [py, "-m", "src.status_motores"]], "t": 300,
         "pular": None},
        {"etapa": "treinar_rede", "finalidade": "a rede reaprende com as validações novas",
         "cmds": [[py, "-m", "src.rede_neural"]], "t": 600, "pular": None if precisa_treinar() else "modelo recente e sem rótulos novos suficientes"},
        {"etapa": "biblioteca_diaria", "finalidade": "leitor documental, selos e decisões da titular nos livros (1 vez por dia)",
         "cmds": [[py, "-c", "from src.leitor_documental import aplicar; print(aplicar())"], [py, "-m", "src.selo_livros"], [py, "-m", "src.decisoes_titular"]],
         "t": 700, "pular": "já feita hoje" if feita_hoje else None, "depois": lambda: diaria.write_text(_hoje_brt(), encoding="utf-8")},
        {"etapa": "documento_oficial", "finalidade": "do replicador à fonte oficial e ao PDF do edital",
         "cmds": [[py, "scripts/treino_fontes.py", "--aplicar"]], "t": 420, "pular": None},
        {"etapa": "mapa", "finalidade": "repositório único, mapa e estados das oportunidades",
         "cmds": [[py, "-m", "src.fluxo_oportunidades", "--completo"]], "t": 300,
         "pular": "nada novo na coleta e mapa com menos de 2 h" if (novos == 0 and _idade_h(mapa) < 2) else None},
        {"etapa": "fichas", "finalidade": "ficha e janela de cada oportunidade aberta", "cmds": [[py, "-m", "src.fichas_oportunidades"]], "t": 200, "pular": None},
        {"etapa": "legislativo", "finalidade": "projetos de lei, utilidades públicas e orçamento — acompanhamento sem livro",
         "cmds": [[py, "-m", "src.legislativo"]], "t": 120, "pular": None},
        {"etapa": "sala_de_controle", "finalidade": "instrumentos de cada etapa", "cmds": [[py, "-m", "src.sala_controle"]], "t": 150, "pular": None},
        {"etapa": "diagnostico", "finalidade": "diagnóstico único do sistema", "cmds": [[py, "-m", "src.diagnostico_sistema"]], "t": 300, "pular": None},
    ]


def ciclo_sequencia() -> dict:
    ctx = _j(CICLO, {"recibos": [], "decisoes": []})
    for f in fases(ctx):
        if f["pular"]:
            ctx["decisoes"].append({"fase": f["etapa"], "pulou": f["pular"]}); continue
        rs = [executar(f"{f['etapa']}:{i + 1}", c, f["t"]) for i, c in enumerate(f["cmds"])]
        rec = {"etapa": f["etapa"], "finalidade": f["finalidade"], "segundos": round(sum(r["segundos"] for r in rs), 1),
               "erro": next((f"{r['etapa']}: {r['erro']}" for r in rs if r["erro"]), None)}
        ctx["recibos"].append(rec)
        if not rec["erro"] and f.get("depois"):
            try:
                f["depois"]()
            except OSError:
                pass
    ctx["fim"] = _agora()
    ctx["erros"] = [r for r in ctx["recibos"] if r.get("erro")]
    ctx["estado"] = "vermelho" if ctx["erros"] else "verde"
    _w(CICLO, ctx)
    dia = DIR / f"{_hoje_brt()}.json"
    h = _j(dia, {"ciclos": []}); h["ciclos"] = (h["ciclos"] + [ctx])[-48:]; _w(dia, h)
    _w(PAINEL, {"atualizado_em": ctx["fim"], "regra": __doc__.split("Entradas por")[0].strip(), "ultimo_ciclo": ctx,
                "ciclos_hoje": len(h["ciclos"]), "vermelhos_hoje": sum(1 for c in h["ciclos"] if c.get("estado") == "vermelho")})
    return ctx


# ── 6. VEREDITO ────────────────────────────────────────────────────────────────────────────────────────────────────
def veredito() -> int:
    ctx = _j(CICLO, {})
    erros = ctx.get("erros") or [r for r in ctx.get("recibos") or [] if r.get("erro")]
    for e in erros:
        print(f"::error title=Etapa com erro: {e.get('etapa')}::{e.get('erro')}")
    print(json.dumps({"estado": "vermelho" if erros else "verde", "etapas_com_erro": len(erros),
                      "cobertura_do_dia_pct": (ctx.get("avaliacao") or {}).get("cobertura_do_dia_pct")}, ensure_ascii=False))
    return 1 if erros else 0


if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else "tudo"
    if modo in ("coleta", "tudo"):
        c = ciclo_coleta(); print(json.dumps({k: c[k] for k in ("decisoes", "novos_na_base")}, ensure_ascii=False))
    if modo in ("sequencia", "tudo"):
        c = ciclo_sequencia(); print(json.dumps({"estado": c["estado"], "erros": len(c["erros"])}, ensure_ascii=False))
    if modo in ("veredito", "tudo"):
        sys.exit(veredito())
