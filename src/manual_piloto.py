"""MANUAL DO PILOTO — livro especial de cada piloto (titular, 16/10/2026).

Livro especial: livro PERMANENTE de uma ferramenta, que não é oportunidade, e registra o aprendizado e a evolução dela.
Cada piloto tem o seu, em biblioteca_alexandria/livros/especiais/manual-do-piloto-<piloto>.json:

    missoes_pendentes  cada missão avaliada desde o último ciclo (forma compacta)
    ciclos             a cada 100 MISSÕES, um ciclo de aprendizado: efetividade, por tipo de missão, motivos de
                       insucesso, consultas que renderam e as regras que dele saíram
    regras_em_vigor    o que o piloto aprendeu e APLICA — vai no briefing de cada missão
    licoes, melhorias, tratados   (o que antes ficava em estado/piloto/aprendizados)

Substitui os ~18.700 arquivos de estado/piloto/aprendizados (uma avaliação por missão): o aprendizado deixa de ser
arquivo solto e passa a morar no livro do piloto, e o piloto o lê antes de cada voo.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from .nucleo import ROOT

ESPECIAIS = ROOT / "biblioteca_alexandria/livros/especiais"
CICLO = 100                                              # aprendizado a cada 100 missões
MOTIVOS = {"busca_vazia": "a busca não devolveu resultado", "sem_texto": "os achados vieram sem texto para ler",
           "nada_no_crivo": "nenhum achado passou no crivo", "pagina_nao_confirma": "a página oficial não confirmou",
           "modelo_mudo": "o modelo não respondeu", "fora_do_objeto": "os achados estavam fora do objeto"}


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


PILOTOS = ("espiao", "interceptador")                     # 16/10 (titular): DOIS livros especiais de piloto


def slug(piloto: str) -> str:
    """Toda missão é de um dos dois pilotos: Interceptador, ou Espião (missão aberta e missão especial são voos dele)."""
    return "interceptador" if "intercept" in str(piloto or "").lower() else "espiao"


def caminho(piloto: str) -> Path:
    return ESPECIAIS / f"manual-do-piloto-{slug(piloto)}.json"


def ler(piloto: str) -> dict:
    p = caminho(piloto)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"id": f"manual-do-piloto-{slug(piloto)}", "tipo": "livro_especial", "ferramenta": "piloto",
                "piloto": piloto, "finalidade": "registrar o aprendizado e a evolução do piloto; as regras em vigor "
                "vão no briefing de cada missão", "criado_em": _agora(), "temporario": "a cada 100 voos o piloto aprende, aplica (regras em vigor) e as missões "
                "são apagadas; ficam as regras e o resumo dos últimos ciclos", "missoes_total": 0, "missoes_pendentes": [],
                "ciclos": [], "regras_em_vigor": [], "consultas_que_renderam": [], "licoes": {}, "melhorias": [],
                "tratados": {}, "descartes_por_motivo": {}}


def gravar(m: dict) -> None:
    ESPECIAIS.mkdir(parents=True, exist_ok=True)
    m["atualizado_em"] = _agora()
    caminho(m.get("piloto")).write_text(json.dumps(m, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def _compacta(av: dict) -> dict:
    return {k: av.get(k) for k in ("em", "missao", "alvo", "consulta", "achados", "uteis", "descartados", "efetividade",
                                   "motivo_do_insucesso") if av.get(k) not in (None, "", [])}


def aprender(m: dict) -> dict:
    """Um ciclo de aprendizado sobre as missões pendentes (chamado a cada 100)."""
    lote = m.get("missoes_pendentes") or []
    if not lote:
        return {}
    n = len(lote)
    ef = round(sum(float(x.get("efetividade") or 0) for x in lote) / n, 3)
    por_tipo: dict = {}
    for x in lote:
        t = x.get("missao") or "sem tipo"
        d = por_tipo.setdefault(t, {"missoes": 0, "com_util": 0})
        d["missoes"] += 1; d["com_util"] += 1 if (x.get("uteis") or 0) > 0 else 0
    motivos = Counter(x.get("motivo_do_insucesso") for x in lote if x.get("motivo_do_insucesso"))
    renderam = [x.get("consulta") for x in lote if (x.get("uteis") or 0) > 0 and x.get("consulta")]
    regras = []
    for t, d in sorted(por_tipo.items(), key=lambda kv: -kv[1]["missoes"]):
        if d["missoes"] >= 10 and d["com_util"] == 0:
            regras.append(f"missões do tipo '{t}' — {d['missoes']} no ciclo sem nenhum achado útil: reformular a "
                          "abordagem antes de repetir (outra fonte, outra consulta)")
        elif d["missoes"] >= 10 and d["com_util"] / d["missoes"] >= 0.3:
            regras.append(f"missões do tipo '{t}' rendem ({d['com_util']} de {d['missoes']} com achado útil): manter")
    if motivos:
        mot, q = motivos.most_common(1)[0]
        if q >= n * 0.5:
            regras.append(f"metade ou mais das missões falhou porque {MOTIVOS.get(mot, mot)} ({q} de {n}): "
                          + {"busca_vazia": "trocar de buscador ou de fonte direta",
                             "sem_texto": "abrir a página/PDF antes de julgar",
                             "fora_do_objeto": "fechar a consulta no objeto (OSC, chamamento, fomento)",
                             "nada_no_crivo": "fechar a consulta no objeto (OSC, chamamento, fomento)",
                             "pagina_nao_confirma": "procurar a página oficial do órgão antes do agregador",
                             "modelo_mudo": "reduzir o tamanho do pedido ao modelo"}.get(mot, "corrigir a causa"))
    ciclo = {"numero": len(m.get("ciclos") or []) + 1, "em": _agora(), "missoes": n,
             "periodo": [lote[0].get("em"), lote[-1].get("em")], "efetividade_media": ef,
             "missoes_com_util": sum(1 for x in lote if (x.get("uteis") or 0) > 0), "por_tipo": por_tipo,
             "motivos_de_insucesso": dict(motivos.most_common()), "regras": regras}
    m.setdefault("ciclos", []).append(ciclo)
    m["ciclos"] = m["ciclos"][-5:]                            # temporário: só os últimos 5 resumos
    m["ciclos_realizados"] = int(m.get("ciclos_realizados") or 0) + 1
    ciclo["numero"] = m["ciclos_realizados"]
    m["regras_em_vigor"] = regras or m.get("regras_em_vigor") or []
    vistos = list(dict.fromkeys([*renderam, *(m.get("consultas_que_renderam") or [])]))
    m["consultas_que_renderam"] = vistos[:30]
    m["missoes_pendentes"] = []
    return ciclo


def registrar(piloto: str, av: dict, gravar_: bool = True) -> dict:
    """Registra uma missão avaliada; a cada 100, aprende e aplica (regras em vigor)."""
    m = ler(piloto)
    m.setdefault("missoes_pendentes", []).append(_compacta(av))
    m["missoes_total"] = int(m.get("missoes_total") or 0) + 1
    ciclo = aprender(m) if len(m["missoes_pendentes"]) >= CICLO else None
    if gravar_:
        gravar(m)
    return {"missoes_total": m["missoes_total"], "pendentes": len(m["missoes_pendentes"]), "ciclo": ciclo}


def texto_para_briefing(piloto: str) -> str:
    """O que o piloto aprendeu e aplica nesta missão (vai no briefing)."""
    m = ler(piloto)
    regras = m.get("regras_em_vigor") or []
    cons = m.get("consultas_que_renderam") or []
    if not regras and not cons:
        return ""
    ult = (m.get("ciclos") or [{}])[-1]
    return ("MANUAL DO PILOTO (o que você aprendeu nos últimos ciclos de 100 missões — aplique):\n"
            + "".join(f"- {r}\n" for r in regras)
            + (f"- consultas que renderam achado útil: {cons[:10]}\n" if cons else "")
            + (f"(ciclo {ult.get('numero')}: efetividade média {ult.get('efetividade_media')})\n\n" if ult else "\n"))


def migrar(pasta: Path | None = None, apagar: bool = True) -> dict:
    """Uma vez: as avaliações de estado/piloto/aprendizados viram ciclos no manual de cada piloto, em ordem
    cronológica; lições, melhorias, tratados, síntese e descartes entram no manual; a pasta é apagada."""
    import lzma
    import shutil
    pasta = pasta or ROOT / "estado/piloto/aprendizados"
    if not pasta.exists():
        return {"migrado": False, "motivo": "pasta já não existe"}
    avs: list = []
    for a in sorted((pasta / "avaliacoes").glob("*.json")):
        try:
            avs.append(json.loads(a.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            continue
    for xz in sorted((pasta / "avaliacoes").glob("*.jsonl.xz")) + sorted(pasta.glob("*.jsonl.xz")):
        try:
            for linha in lzma.open(xz, "rt", encoding="utf-8"):
                try:
                    avs.append(json.loads(linha))
                except ValueError:
                    pass
        except (OSError, lzma.LZMAError):
            continue
    avs = [a for a in avs if isinstance(a, dict) and a.get("motor") and not a.get("ensaio")]
    avs.sort(key=lambda a: str(a.get("em") or ""))
    manuais: dict = {}
    for a in avs:
        m = manuais.setdefault(slug(a["motor"]), ler(a["motor"]))
        m["piloto"] = "Piloto - Interceptador" if slug(a["motor"]) == "interceptador" else "Piloto - Espião"
        m["missoes_pendentes"].append(_compacta(a)); m["missoes_total"] = int(m.get("missoes_total") or 0) + 1
        if len(m["missoes_pendentes"]) >= CICLO:
            aprender(m)
    def _j(nome, padrao):
        try:
            return json.loads((pasta / nome).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return padrao
    lic = (_j("licoes.json", {}) or {}).get("itens") or {}
    mel = (_j("melhorias.json", {}) or {}).get("itens") or []
    trat = (_j("tratados.json", {}) or {}).get("itens") or {}
    for p_ in PILOTOS:                                    # os dois livros especiais existem sempre
        manuais.setdefault(p_, ler(p_)); manuais[p_]["piloto"] = "Piloto - Interceptador" if p_ == "interceptador" else "Piloto - Espião"
    principal = manuais["espiao"]
    for k, it in lic.items():
        (manuais.get(slug(it.get("motor"))) or principal).setdefault("licoes", {})[k] = it
    for it in mel:
        (manuais.get(slug(it.get("motor"))) or principal).setdefault("melhorias", []).append(it)
    principal.setdefault("tratados", {}).update(trat)             # editais já abordados (sem piloto atribuído)
    for extra in ("sintese_ate_2026-09-30.json", "licoes_parecer_23_09.json", "poda_2026-09-23.json", "acervo_fora_do_objeto.json"):
        v = _j(extra, None)
        if v is not None:
            principal.setdefault("historico_de_aprendizado", {})[extra.replace(".json", "")] = v
    desc = Counter()
    for q in (pasta / "quarentena").glob("*.jsonl"):
        for linha in q.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                desc[json.loads(linha).get("motivo") or "?"] += 1
            except ValueError:
                pass
    principal["descartes_por_motivo"] = dict(Counter(principal.get("descartes_por_motivo") or {}) + desc)
    for m in manuais.values():
        gravar(m)
    res = {"migrado": True, "avaliacoes": len(avs), "manuais": {s: {"missoes": m.get("missoes_total"),
           "ciclos": m.get("ciclos_realizados"), "pendentes": len(m.get("missoes_pendentes") or []),
           "regras_em_vigor": len(m.get("regras_em_vigor") or [])} for s, m in manuais.items()},
           "licoes": len(lic), "melhorias": len(mel), "tratados": len(trat), "descartes": sum(desc.values())}
    if apagar:
        shutil.rmtree(pasta, ignore_errors=True)
    return res
