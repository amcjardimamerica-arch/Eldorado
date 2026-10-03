"""MAESTRO — A REDE NEURAL CONDUZ O DIA (titular, 02/10/2026).

Os motores são ferramentas de uma etapa. O maestro, a cada passagem do fluxo de status (4 vezes por dia):
  1. PLANEJA  quais motores rodam hoje (agenda) e em que ordem: rendimento real do canal (oportunidades validadas como
              reais por leitura — linha de produção), diagnóstico (planos de correção) e livros com abertura próxima
              no índice do motor (léxico temporário da chave de acionamento);
  2. MEDE     a cobertura do dia de cada motor: completa (leu sem falha de página) · parcial (falha em parte das páginas)
              · pendente (ainda não leu) · pendente_local (exige IP brasileiro — coleta no computador do titular);
  3. CONTROLA dispara de novo os pendentes e os parciais, até 3 vezes por dia, para a busca do dia NÃO ficar parcial;
  4. FECHA    o dia quando todos os motores planejados estão completos (ou esgotaram as tentativas — fica registrado).
Saída: docs/dados/maestro.json · estado: estado/maestro/AAAA-MM-DD.json
"""
from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAIDA = ROOT / "docs/dados/maestro.json"
DIAS = ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return padrao


def hoje_brt():
    return datetime.now(timezone(timedelta(hours=-3))).date()


def roda_hoje(ag: dict, dia) -> bool:
    d = str((ag or {}).get("dias") or "todos").lower()
    if d.startswith("inativ"):
        return False
    return d == "todos" or DIAS[dia.weekday()] in d or (d == "uteis" and dia.weekday() < 5)


CORTE = ("cobertura_cortada", "cortados", "paginas_nao_lidas", "alerta_formato", "adiados_por_tempo", "truncado")


def cobertura(sid: str, reg: dict | None, diag: dict | None, diag_motor: dict | None = None) -> str:
    """02/10: além da falha de página, a leitura CORTADA que o motor registra no próprio diagnóstico conta como parcial."""
    if reg and any((diag_motor or {}).get(k) for k in CORTE) and reg.get("cor") not in ("vermelho",):
        return "parcial"
    if reg and (diag_motor or {}).get("aguardando_brasil") and reg.get("cor") not in ("vermelho",):
        return "pendente_local"       # 03/10 (teste do motor 13): leu o que a nuvem alcança; o resto espera o Brasil — nunca "completa"
    if not reg:
        return "pendente_local" if "exige" in json.dumps(diag or {}, ensure_ascii=False).lower() else "pendente"
    if reg.get("cor") in ("vermelho",) or int(reg.get("falhas") or 0) > 0:
        return "parcial"
    if reg.get("cor") in ("cinza", "futuro", "fora"):
        return "pendente"
    _dm = diag_motor or {}
    _pulou_local = _dm.get("alerta_local") or any("computador do titular" in str((f or {}).get("pulado") or "") or "IP estrangeiro" in str((f or {}).get("pulado") or "")
                                                 for f in (_dm.get("fontes") or {}).values() if isinstance(f, dict))
    if _dm.get("rotas_pendentes_local") or _pulou_local:
        return "pendente_local"                       # 03/10: leu só a parte da nuvem; o resto é da coleta local (Brasil)
    return "completa"


def planejar(dia=None) -> list[dict]:
    dia = dia or hoje_brt()
    try:
        from .sensores import registro
        ativos = [s["id"] for s in registro()]
    except Exception:  # noqa: BLE001
        ativos = []
    A = (_j(ROOT / "config/agenda_motores.json", {}) or {}).get("motores", {})
    canais = {c["canal"]: c for c in (_j(ROOT / "docs/dados/linha_producao.json", {}) or {}).get("canais", [])}
    planos = {m["motor"]: m for m in (_j(ROOT / "docs/dados/planos_correcao.json", {}) or {}).get("motores", [])}
    E = (_j(ROOT / "estado/esquadra.json", {}) or {}).get("sensores", {})
    lex = (_j(ROOT / "estado/lexico_temporario_livros.json", {}) or {}).get("itens", [])
    from .linha_producao import canal_canonico
    plano = []
    for sid in ativos:
        ag = A.get(sid) or A.get(sid.replace("plat-", "")) or {}
        if not roda_hoje(ag, dia):
            continue
        c = canais.get(canal_canonico(sid)) or {}
        leituras = int((E.get(sid) or {}).get("leituras") or 0)
        rend = (int(c.get("validadas_como_reais") or 0) + 0.5) / (leituras + 5)        # oportunidades reais por leitura
        diag = (planos.get(sid) or {}).get("diagnostico", "saudavel")
        livros_proximos = sum(1 for it in lex if sid in (it.get("motores") or []))
        prioridade = round(rend * (0.5 if diag in ("sem_rendimento", "falha_parcial") else 1.0) + 0.02 * livros_proximos, 4)
        plano.append({"motor": sid, "prioridade": prioridade, "diagnostico": diag, "livros_com_abertura_proxima": livros_proximos,
                      "horarios": ag.get("horarios_brt"), "coleta": ag.get("coleta") or "nuvem"})
    return sorted(plano, key=lambda p: -p["prioridade"])


def controlar(disparar: bool = False, dia=None) -> dict:
    dia = dia or hoje_brt(); d0 = dia.isoformat()
    cfg = (_j(ROOT / "config/esteira.json", {}) or {}).get("maestro", {}); limite = int(cfg.get("tentativas_por_dia", 3))
    est_p = ROOT / f"estado/maestro/{d0}.json"; est = _j(est_p, {"tentativas": {}})
    D = (_j(ROOT / "estado/esquadra_diario.json", {}) or {}).get("sensores", {})
    ESQ = (_j(ROOT / "estado/esquadra.json", {}) or {}).get("sensores", {})
    A_ag = (_j(ROOT / "config/agenda_motores.json", {}) or {}).get("motores", {})
    S = {m.get("id"): m for m in (_j(ROOT / "docs/dados/status_motores.json", {}) or {}).get("motores", [])}
    plano = planejar(dia)
    try:   # o que a agenda JÁ esperava ter lido (respeita horário e cadência de cada motor)
        sp = importlib.util.spec_from_file_location("ag", ROOT / "scripts/agenda_motores.py"); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        atrasados = set(m.recuperar())
    except Exception:  # noqa: BLE001
        atrasados = set()
    for p in plano:
        c = cobertura(p["motor"], (D.get(p["motor"]) or {}).get(d0), S.get(p["motor"]) or S.get(p["motor"].replace("plat-", "")),
                      ((ESQ.get(p["motor"]) or {}).get("diagnostico")) or {})
        # D-1: o dia anterior só está observado se o motor completou a leitura hoje ou ontem depois da última janela
        _ont = (D.get(p["motor"]) or {}).get((dia - timedelta(days=1)).isoformat()) or {}
        _ag = (A_ag.get(p["motor"]) or {})
        _diario = str(_ag.get("dias") or "todos") == "todos" and int(_ag.get("cadencia_dias") or 1) <= 1
        p["dia_anterior"] = ("nao_se_aplica" if not _diario else
                             "observado" if c == "completa" or _ont.get("cor") in ("verde", "azul", "amarelo") else "nao_observado")
        _sem_agenda = p["motor"] not in A_ag
        _ont0 = (D.get(p["motor"]) or {}).get((dia - timedelta(days=1)).isoformat()) or {}
        if c == "pendente" and _sem_agenda and not _ont0:
            c = "pendente_sem_agenda"                # 02/10: fonte sem horário próprio (ex.: as 260) — o maestro a lê em lotes
        elif c == "pendente" and p["motor"] not in atrasados:
            c = "aguardando_horario"                 # ainda não chegou a hora (ou a cadência) — não se dispara
        p["cobertura"] = c
        p["tentativas_hoje"] = int(est["tentativas"].get(p["motor"]) or 0)
    a_disparar = [p["motor"] for p in plano if p["cobertura"] in ("pendente", "parcial") and p["tentativas_hoje"] < limite and p["coleta"] != "local"]
    _lote = int(cfg.get("lote_sem_agenda", 40))                # fontes sem horário próprio: em lotes, por prioridade
    a_disparar += [p["motor"] for p in plano if p["cobertura"] == "pendente_sem_agenda"][:_lote]
    a_disparar += [x for x in atrasados if x not in a_disparar and int(est["tentativas"].get(x) or 0) < limite]
    if disparar:
        # 02/10: só conta tentativa de quem DE FATO leu (parcial). O GitHub mantém um único disparo na fila e cancela o
        # anterior: contar por disparo esgotava as 3 tentativas de motores que nunca chegaram a rodar.
        parciais = {p["motor"] for p in plano if p["cobertura"] == "parcial"}
        for x in a_disparar:
            if x in parciais:
                est["tentativas"][x] = int(est["tentativas"].get(x) or 0) + 1
    from collections import Counter
    cont = Counter(p["cobertura"] for p in plano)
    completos = cont.get("completa", 0)
    esgotados = [p["motor"] for p in plano if p["cobertura"] in ("pendente", "parcial") and p["tentativas_hoje"] >= limite]
    fechado = all(p["cobertura"] == "completa" or p["motor"] in esgotados or p["cobertura"] == "pendente_local" for p in plano)   # sem agenda: só fecha lido
    completos_ou_esperando = completos + cont.get("aguardando_horario", 0)
    out = {"dia": d0, "em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "regra": __doc__.split("Saída")[0].strip(),
           "planejados": len(plano), "cobertura": dict(cont), "cobertura_percentual": round(100 * completos / max(1, len(plano) - cont.get("aguardando_horario", 0)), 1),
           "a_disparar": a_disparar, "esgotaram_tentativas": esgotados, "dia_fechado": fechado,
           "dia_anterior_nao_observado": [p["motor"] for p in plano if p.get("dia_anterior") == "nao_observado"], "plano": plano}
    est_p.parent.mkdir(parents=True, exist_ok=True)
    est.update({"ultima": out["em"], "cobertura": dict(cont), "dia_fechado": fechado}); est_p.write_text(json.dumps(est, ensure_ascii=False, indent=1), encoding="utf-8")
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def relatorio_etapas(dia=None, controle: dict | None = None) -> dict:
    """02/10 (titular): a rede neural como MAESTRO — relatório do que aconteceu em cada etapa do dia, com alertas e veredito."""
    from collections import Counter
    dia = dia or hoje_brt(); d0 = dia.isoformat(); ontem = (dia - timedelta(days=1)).isoformat()
    ctl = controle or _j(SAIDA, {})
    E = []; alertas = []
    E.append({"etapa": "0 · planejamento e cobertura", "planejados": ctl.get("planejados"), "cobertura": ctl.get("cobertura"),
              "cobertura_percentual": ctl.get("cobertura_percentual"), "redisparados": len(ctl.get("a_disparar") or []),
              "dia_anterior_nao_observado": ctl.get("dia_anterior_nao_observado") or []})
    if ctl.get("dia_anterior_nao_observado"):
        alertas.append(f"{len(ctl['dia_anterior_nao_observado'])} motor(es) ainda sem o dia anterior observado")
    D = (_j(ROOT / "estado/esquadra_diario.json", {}) or {}).get("sensores", {})
    hoje_m = {k: v.get(d0) for k, v in D.items() if v.get(d0)}
    E.append({"etapa": "1 · captação", "motores_que_leram": len(hoje_m), "achados": sum(int((v or {}).get("achados") or 0) for v in hoje_m.values()),
              "com_falha": sorted(k for k, v in hoje_m.items() if int((v or {}).get("falhas") or 0) > 0)})
    esq = (_j(ROOT / "estado/esquadra.json", {}) or {}).get("ultima_execucao") or {}
    if str(esq.get("em") or "")[:10] < ontem:
        alertas.append(f"o registro da esquadra está parado desde {str(esq.get('em'))[:16]}")
    from .integridade import verificar, situacao
    novos, sit, sinais, d1, sem_pub, atrasos = 0, Counter(), Counter(), 0, 0, []
    base = ROOT / "dados/oportunidades/oportunidades.jsonl"
    if base.exists():
        with base.open(encoding="utf-8") as fh:
            for l in fh:
                if d0 not in l and ontem not in l:
                    continue
                try:
                    r = json.loads(l)
                except ValueError:
                    continue
                if str(r.get("coletado_em") or "")[:10] != d0:
                    continue
                novos += 1; fl = verificar(r); sit[situacao(fl)] += 1; sinais.update(x["codigo"] for x in fl)
                pub = str(r.get("data_publicacao") or "")[:10]
                if pub == ontem:
                    d1 += 1
                if not pub:
                    sem_pub += 1
    E.append({"etapa": "2 · base (registros novos de hoje)", "novos": novos, "publicados_no_dia_anterior": d1, "sem_data_de_publicacao": sem_pub})
    E.append({"etapa": "3 · integridade (condicionais)", "situacao": dict(sit), "sinais": dict(sinais.most_common(10))})
    if sit.get("inconclusiva"):
        alertas.append(f"{sit['inconclusiva']} leitura(s) inconclusiva(s) hoje — foram ao reprocessamento")
    R = _j(ROOT / "estado/rede_neural/modelo.json.gz", None) if False else None
    try:
        import gzip
        meta = json.loads(gzip.decompress((ROOT / "estado/rede_neural/modelo.json.gz").read_bytes())).get("meta") or {}
    except Exception:  # noqa: BLE001
        meta = {}
    mt = meta.get("metricas") or {}
    E.append({"etapa": "4 · rede neural", "auc_fora_da_amostra": mt.get("auc"), "precisao": mt.get("precisao"), "revocacao": mt.get("revocacao"),
              "treinada_em": str(meta.get("treinada_em") or "")[:10], "rotulos": meta.get("rotulados"),
              "regra": "a rede só dá nota a leitura íntegra; inconclusiva não recebe nota"})
    if mt.get("revocacao") is not None and float(mt["revocacao"]) < 0.75:
        alertas.append(f"a rede deixa passar {100 - round(100 * float(mt['revocacao']))}% das oportunidades reais no corte de 0,5 (revocação {mt['revocacao']})")
    C = [x for x in (_j(ROOT / "biblioteca_alexandria/fontes/motores.json", {}) or {}).get("motores", []) if x.get("papel") != "fonte_de_busca"]
    E.append({"etapa": "5 · livros", "total": len(C), "criados_hoje": sum(1 for x in C if str(x.get("criado_em") or "")[:10] == d0),
              "atualizados_hoje": sum(1 for x in C if any(str((h or {}).get("visto_em") or "")[:10] == d0 for h in (x.get("historico") or []) if isinstance(h, dict)))})
    E.append({"etapa": "6 · qualificação", "vereditos": dict(Counter((x.get("qualificacao") or {}).get("veredito") or "aplicável" for x in C))})
    E.append({"etapa": "7 · esteira de selos", "selos": dict(Counter((x.get("esteira") or {}).get("selo") or "fora" for x in C)),
              "estantes": dict(Counter((x.get("esteira") or {}).get("estante") or "fora" for x in C))})
    dsc = (_j(ROOT / "docs/dados/descartes.json", {}) or {})
    E.append({"etapa": "8 · descartes e melhorias nos motores", "descartados_hoje": dsc.get("hoje", 0), "restricoes_ativas": dsc.get("restricoes_ativas", 0)})
    out = {"dia": d0, "em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "etapas": E, "alertas": alertas,
           "veredito": "dia em ordem" if not alertas else f"{len(alertas)} ponto(s) de atenção"}
    (ROOT / "docs/dados/relatorio_etapas.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    pasta = ROOT / "docs/relatorios/maestro"; pasta.mkdir(parents=True, exist_ok=True)
    md = [f"# Relatório do maestro — {d0}", "", f"**Veredito:** {out['veredito']}", ""] + [f"- ⚠ {a}" for a in alertas] + [""]
    for e in E:
        md.append(f"## {e['etapa']}"); md += [f"- {k}: {json.dumps(v, ensure_ascii=False)}" for k, v in e.items() if k != "etapa"]; md.append("")
    (pasta / f"{d0}.md").write_text("\n".join(md), encoding="utf-8")
    for velho in sorted(pasta.glob("*.md"))[:-30]:            # guarda só 30 dias (armazenamento leve)
        velho.unlink()
    return out


if __name__ == "__main__":
    o = controlar(disparar="--disparar" in sys.argv)
    try:
        relatorio_etapas(controle=o)
    except Exception as ex:  # noqa: BLE001 — o relatório nunca impede o disparo
        print(f"relatório do maestro falhou: {type(ex).__name__}", file=sys.stderr)
    if "--ids" in sys.argv or "--disparar" in sys.argv:
        print(",".join(o["a_disparar"]))
    else:
        print(json.dumps({k: o[k] for k in ("dia", "planejados", "cobertura", "cobertura_percentual", "a_disparar", "dia_fechado")}, ensure_ascii=False, indent=1))
