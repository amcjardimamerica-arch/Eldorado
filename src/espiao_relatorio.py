"""RELATÓRIO DO PILOTO - ESPIÃO no MESMO FORMATO do Interceptador (titular, 30/09) — docs/dados/espiao.json.

O quadro dos dois Pilotos é o mesmo: acumulado, fila, última missão e a lista de missões com o que cada uma
encontrou. Fontes: estado/piloto/bordo.json (diário de bordo), avaliações de cada missão (inclusive o arquivo mensal
compactado), a esquadrilha (estrelas) e o relatório do Interceptador (indícios entregues a ele).
Gerado ao fim de cada voo do Espião.
"""
from __future__ import annotations

import glob
import json
import lzma
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAIDA = ROOT / "docs/dados/espiao.json"
NOMES = {"descobrir": "descobrir entidades novas", "aposta": "aposta do briefing", "catalogar": "catalogar site do terceiro setor",
         "prospectar": "prospectar empresas", "resgate": "resgate", "cacar_oportunidade": "caçar oportunidade", "afiar_motor": "afiar motor"}


def _j(p, padrao):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:
        return padrao


def _dur(a, b):
    try:
        return (datetime.fromisoformat(str(b).replace("Z", "+00:00")) - datetime.fromisoformat(str(a).replace("Z", "+00:00"))).total_seconds()
    except Exception:
        return None


def montar() -> dict:
    B = _j(ROOT / "estado/piloto/bordo.json", {}); P = _j(ROOT / "docs/dados/piloto.json", {}); E = _j(ROOT / "docs/dados/esquadrilha.json", {})
    I = _j(ROOT / "docs/dados/interceptador.json", {})
    av = [a for a in (_j(f, None) for f in glob.glob(str(ROOT / "estado/piloto/aprendizados/avaliacoes/*.json"))) if a]
    for f in glob.glob(str(ROOT / "estado/piloto/aprendizados/avaliacoes/arquivo-*.jsonl.xz")):
        try:
            av += [json.loads(l).get("avaliacao") or {} for l in lzma.decompress(Path(f).read_bytes()).decode().splitlines() if l.strip()]
        except Exception:
            pass
    motivos = Counter("com_resultado" if int(a.get("uteis") or 0) > 0 else (a.get("motivo_do_insucesso") or "sem_registro") for a in av)
    ms = list(B.get("missoes") or [])
    durs = [d for d in (_dur(m.get("inicio"), m.get("fim")) for m in ms) if d is not None and d >= 0]
    ab = (E.get("abates") or {}).get("piloto-aberto") or (B.get("abates") or {}).get("piloto-aberto") or {}
    novas = sum(int(m.get("achados") or 0) for m in ms if m.get("tipo") == "descobrir")
    comp = {"com_resultado": motivos.get("com_resultado", 0), "nada_no_crivo": motivos.get("nada_no_crivo", 0),
            "fora_do_objeto": motivos.get("fora_do_objeto", 0),
            "busca_sem_resposta": sum(v for k, v in motivos.items() if k not in ("com_resultado", "nada_no_crivo", "fora_do_objeto"))}
    acumulado = {"missoes": sum(comp.values()), "composicao": comp, "com_resultado": comp["com_resultado"], "nada_no_crivo": comp["nada_no_crivo"],
                 "fora_do_objeto": comp["fora_do_objeto"], "busca_sem_resposta": comp["busca_sem_resposta"], "achados": sum(int(a.get("uteis") or 0) for a in av),
                 "entidades_novas_recentes": novas, "estrelas_de_ouro": ab.get("ouro") or 0, "abates": ab.get("n") or 0,
                 "indicios_entregues_ao_interceptador": (I.get("fila") or {}).get("indícios do Espião", 0),
                 "tempo_medio_min": round(sum(durs) / len(durs) / 60, 1) if durs else None}
    try:
        from .piloto import CONSULTAS_DESCOBERTA
        n_consultas = len(CONSULTAS_DESCOBERTA)
    except Exception:
        n_consultas = 0
    fila = {"consultas de descoberta (rodízio)": n_consultas, "apostas do briefing por voo": 2,
            "indícios entregues ao Interceptador": acumulado["indicios_entregues_ao_interceptador"]}
    missoes = []
    for m in sorted(ms, key=lambda x: str(x.get("fim") or x.get("inicio") or ""), reverse=True)[:25]:   # o diário não é gravado em ordem de tempo
        seg = _dur(m.get("inicio"), m.get("fim"))
        ach = int(m.get("achados") or 0)
        res = str(m.get("resultado") or m.get("licao") or "")
        encontrou = [{"titulo": str(x.get("titulo") or x.get("empresa") or x.get("nome") or "")[:120], "url": x.get("url")}
                     for x in (m.get("alvos") or []) if isinstance(x, dict)][:6]
        missoes.append({"em": m.get("fim") or m.get("inicio"), "segundos": seg, "tipo": m.get("tipo"), "modo": NOMES.get(m.get("tipo"), m.get("tipo")),
                        "de": m.get("motor"), "alvo": ((m.get("_alvo") or {}).get("titulo") if isinstance(m.get("_alvo"), dict) else None) or res[:120],
                        "qualidade": "com resultado" if ach else ("fora do objeto" if "fora do objeto" in res.lower() else "nada no crivo"),
                        "achados": ach, "abates": m.get("abates") or 0, "justificativa": res[:400], "encontrou": encontrou,
                        "avaliacao": f"{ach} achado(s)" if ach else "nada passou no crivo"})
    ult = ms[-1] if ms else {}
    recente = _dur(ult.get("fim") or ult.get("inicio"), datetime.now(timezone.utc).isoformat())
    pe = (_j(ROOT / "config/parametros_pilotos.json", {}) or {}).get("espiao") or {}
    aprend = {"buscas_que_funcionam": (pe.get("consultas_boas") or [])[:5], "buscas_que_falham": (pe.get("consultas_ruins") or [])[:5],
              "rendimento_por_tipo": pe.get("rendimento_das_buscas") or {}, "em": pe.get("consultas_aprendidas_em")}
    out = {"em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "papel": "Piloto - Espião", "aprendizado": aprend, "modelo": P.get("modelo"),
           "estado": "em atividade" if B.get("missao_atual") or (recente is not None and recente < 1800) else "aguardando o próximo voo",
           "ultimo_voo": {"voo_do_dia": P.get("voo_do_dia"), "em": P.get("em"), "missoes": len(P.get("missoes") or []), "abates": P.get("abates"),
                          "propostas": P.get("propostas")},
           "fila": fila, "acumulado": acumulado, "missoes": missoes}
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"missoes_no_quadro": len(missoes), "acumulado": acumulado}


if __name__ == "__main__":
    print(json.dumps(montar(), ensure_ascii=False, indent=1))
