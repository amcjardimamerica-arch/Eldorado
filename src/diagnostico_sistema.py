"""DIAGNÓSTICO ÚNICO DO SISTEMA (titular, 14/10/2026) — backend; nada de página, quadro ou apresentação.

Quando a titular pede "Analise o sistema", o Claude roda:
    python -m src.diagnostico_sistema              # só diagnostica
    python -m src.diagnostico_sistema --corrigir   # diagnostica, corrige em sequência e diagnostica de novo
e lê estado/diagnostico_sistema.md (resumo) e estado/diagnostico_sistema.json (completo).

O que reúne num só lugar:
  1. SISTEMAS   motores (status, cadência, auditoria), maestro, rede neural, Cartório, Pilotos (Interceptador e
                Espião), saúde (arquivos, frescor, coerência, fluxos do GitHub), auditoria cega, sala de controle
  2. OPORTUNIDADES, uma a uma (repositório único, abertas): tem livro? o livro existe no catálogo? está validada?
                tem site oficial e prazo? aparece na tela (fluxo) e na ficha? decisão da titular aplicada?
  3. INTEGRAÇÃO repositório × tela × fichas × catálogo de livros × decisões × indicadores: mesmos ids, mesmas
                contagens, todos em dia
  4. PROBLEMAS  cada um com gravidade e a CORREÇÃO que se aplica

Correções (--corrigir), uma etapa depois da outra (nada em paralelo), com as rotinas que o sistema já tem:
  decisões da titular → livros (criar/vincular) → repositório único → tela das oportunidades → fichas →
  sala de controle → saúde
Problemas que não têm correção automática (motor em falha, fluxo do GitHub falhando, item sem site oficial) ficam
listados com a ação recomendada, para a análise do Claude e do conselho.
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAIDA = ROOT / "estado/diagnostico_sistema.json"
RESUMO = ROOT / "estado/diagnostico_sistema.md"
D = ROOT / "docs/dados"
FRESCOR_H = {"repositorio": 3, "fluxo": 3, "fichas": 3, "sala_controle": 3, "status_motores": 8, "maestro": 3, "rede_neural": 26, "saude": 26}


def _j(p: Path, padrao=None):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao if padrao is not None else {}


def _idade_h(ts) -> float | None:
    try:
        t = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        t = t if t.tzinfo else t.replace(tzinfo=timezone.utc)
        return round((datetime.now(timezone.utc) - t).total_seconds() / 3600, 1)
    except Exception:  # noqa: BLE001
        return None


def _problema(lista, codigo, gravidade, texto, correcao=None, quantidade=None, exemplos=None):
    lista.append({"codigo": codigo, "gravidade": gravidade, "texto": texto, "correcao": correcao,
                  "quantidade": quantidade, "exemplos": (exemplos or [])[:8]})


def sistemas(P: list) -> dict:
    st, ma, rn = _j(D / "status_motores.json"), _j(D / "maestro.json"), _j(D / "rede_neural.json")
    ca, it, es = _j(D / "cartorio.json"), _j(D / "interceptador.json"), _j(D / "espiao_avaliacao.json")
    sa, sc = _j(D / "saude.json"), _j(D / "sala_controle.json")
    am, ac = _j(ROOT / "estado/auditoria_motores.json"), _j(ROOT / "estado/auditoria_cega.json")
    mot = st.get("motores") or []
    vermelhos = [{"id": m.get("id"), "nome": m.get("nome"), "resultado": m.get("resultado")} for m in mot if m.get("luz") == "vermelho"]
    atencao = [{"id": m.get("id"), "nome": m.get("nome"), "resultado": m.get("resultado")} for m in mot if m.get("luz") == "verde" and "atenção" in str(m.get("resultado"))]
    for m in vermelhos:
        _problema(P, "motor_em_falha", "alta", f"motor em falha: {m['nome']} — {m['resultado']}", "investigar o motor (sem correção automática)")
    vc = rn.get("validacao_cruzada") or {}
    if vc.get("auc") is not None and vc["auc"] < 0.8:
        _problema(P, "rede_neural_fraca", "media", f"rede neural com discernimento abaixo do normal (AUC {vc['auc']})", "retreinar com mais decisões rotuladas")
    for a in sa.get("alertas") or []:
        _problema(P, f"saude_{a.get('area')}", "media", f"saúde · {a.get('area')}: {a.get('texto')}",
                  "refazer tela e indicadores" if a.get("area") in ("coerência", "frescor") else "ver o fluxo/arquivo indicado")
    fluxos = sc.get("fluxos") or []
    return {
        "motores": {"total": len(mot), "funcionando": sum(1 for m in mot if m.get("luz") == "verde"), "em_falha": len(vermelhos),
                    "inativos": sum(1 for m in mot if m.get("luz") == "cinza"), "em_falha_lista": vermelhos, "leitura_parcial": atencao,
                    "status_em": st.get("gerado_em"), "auditoria": {k: am.get(k) for k in ("em", "total", "por_estado")}},
        "maestro": {k: ma.get(k) for k in ("em", "planejados", "cobertura_percentual", "cobertura", "dia_fechado")}
                   | {"esgotaram_tentativas": len(ma.get("esgotaram_tentativas") or []) if isinstance(ma.get("esgotaram_tentativas"), list) else ma.get("esgotaram_tentativas"),
                      "a_disparar": len(ma.get("a_disparar") or []) if isinstance(ma.get("a_disparar"), list) else ma.get("a_disparar")},
        "rede_neural": {"em": rn.get("em"), "modelo_treinado_em": rn.get("modelo_treinado_em"), "rotulados": rn.get("rotulados"),
                        "validacao_cruzada": vc, "pendentes_provaveis_reais": rn.get("pendentes_provaveis_reais")},
        "cartorio": {"em": ca.get("em"), "resumo": ca.get("resumo")},
        "pilotos": {"interceptador": {"estado": it.get("estado"), "ultimo_voo": it.get("ultimo_voo") or it.get("em"), "contagem": it.get("contagem")},
                    "espiao": {"em": es.get("em"), "voos": es.get("voos"), "empresas_novas": es.get("empresas_novas")}},
        "saude": {"em": sa.get("em"), "alertas": sa.get("alertas") or []},
        "auditoria_cega": {k: ac.get(k) for k in ("em", "taxa_de_perda", "sem_nada_na_base")},
        "fluxos_github": {"total": len(fluxos), "com_falha": [f.get("nome") for f in fluxos if f.get("conclusao") == "failure"]},
        "sala_controle": {"em": sc.get("em"), "indice_saude": sc.get("indice_saude"), "contagem": sc.get("contagem")},
    }


def oportunidades(P: list, hoje: str) -> dict:
    R = (_j(ROOT / "dados/oportunidades/repositorio_unico.json", {}).get("registros") or [])
    abertas = [r for r in R if r.get("estado") != "fechada" and not r.get("arquivada")]
    cat = {m.get("id"): m for m in (_j(ROOT / "biblioteca_alexandria/fontes/motores.json", {}).get("motores") or [])}
    fl = {x.get("id") for v in (_j(D / "fluxo_oportunidades.json", {}).get("itens_por_uf") or {}).values() for x in v}
    fichas = _j(D / "fichas_oportunidades.json", {}); fid = set((fichas.get("fichas") or {}).keys()) | set((fichas.get("alias") or {}).keys())
    idx = (_j(ROOT / "estado/opressores_indice.json", {}).get("indice") or {})
    sem_livro_regra = Counter()
    sem_livro, livro_inexistente, sem_site, sem_prazo, vencida, fora_tela, sem_ficha = [], [], [], [], [], [], []
    estados = Counter(); faltam = Counter()
    for r in abertas:
        estados[r.get("estado")] += 1
        nome = f"{(r.get('titulo') or '')[:70]} [{r['id']}]"
        if not r.get("livro"):
            regra = next(((idx.get(i) or {}).get("dispensa") for i in [r["id"], *(r.get("ids_origem") or [])] if (idx.get(i) or {}).get("dispensa")), None) or r.get("motivo_sem_livro")
            if regra:
                sem_livro_regra[str(regra)[:90]] += 1          # sem livro por regra registrada: não é problema
            else:
                sem_livro.append(nome)
        elif r["livro"] not in cat:
            livro_inexistente.append(nome)
        if not r.get("link_oficial"):
            sem_site.append(nome)
        if not r.get("fim") and r.get("regime") != "fluxo_continuo":
            sem_prazo.append(nome)
        elif r.get("fim") and str(r["fim"]) < hoje:
            vencida.append(nome)
        ids = {r["id"], *(r.get("ids_origem") or [])}
        if not ids & fl:
            fora_tela.append(nome)
        if not ids & fid:
            sem_ficha.append(nome)
        for k in r.get("faltam") or []:
            faltam[k] += 1
    n = len(abertas)
    if sem_livro:
        _problema(P, "oportunidade_sem_livro", "alta", f"{len(sem_livro)} de {n} oportunidades abertas sem livro e sem regra que justifique", "criar/vincular livros", len(sem_livro), sem_livro)
    if livro_inexistente:
        _problema(P, "livro_inexistente", "alta", f"{len(livro_inexistente)} oportunidades apontam para livro que não existe no catálogo",
                  "criar/vincular livros e refazer o repositório", len(livro_inexistente), livro_inexistente)
    if vencida:
        _problema(P, "prazo_vencido_aberta", "alta", f"{len(vencida)} oportunidades com prazo vencido ainda contadas como abertas", "refazer o repositório", len(vencida), vencida)
    if fora_tela:
        _problema(P, "fora_da_tela", "alta", f"{len(fora_tela)} abertas no repositório que não aparecem na tela de oportunidades", "refazer a tela", len(fora_tela), fora_tela)
    if sem_ficha:
        _problema(P, "sem_ficha", "media", f"{len(sem_ficha)} abertas sem ficha (janela de detalhe)", "refazer as fichas", len(sem_ficha), sem_ficha)
    if sem_site:
        _problema(P, "sem_site_oficial", "media", f"{len(sem_site)} abertas ainda sem site oficial", "Cartório/Interceptador (sem correção automática imediata)", len(sem_site), sem_site)
    if sem_prazo:
        _problema(P, "sem_prazo", "baixa", f"{len(sem_prazo)} abertas sem prazo de inscrição conhecido", "Cartório/Interceptador (sem correção automática imediata)", len(sem_prazo), sem_prazo)
    return {"abertas": n, "por_estado": dict(estados), "validadas": estados.get("validada", 0),
            "percentual_validadas": round(100 * estados.get("validada", 0) / n, 1) if n else None,
            "com_livro": n - len(sem_livro) - sum(sem_livro_regra.values()), "sem_livro": len(sem_livro),
            "sem_livro_por_regra": sum(sem_livro_regra.values()), "sem_livro_por_regra_motivos": dict(sem_livro_regra.most_common(6)),
            "livro_inexistente": len(livro_inexistente),
            "sem_site_oficial": len(sem_site), "sem_prazo": len(sem_prazo), "prazo_vencido": len(vencida),
            "fora_da_tela": len(fora_tela), "sem_ficha": len(sem_ficha), "itens_que_mais_faltam": dict(faltam.most_common(12))}


def integracao(P: list, op: dict) -> dict:
    rr = _j(D / "repositorio_resumo.json"); fl = _j(D / "fluxo_oportunidades.json"); fi = _j(D / "fichas_oportunidades.json")
    sc = _j(D / "sala_controle.json"); ma = _j(D / "maestro.json"); rn = _j(D / "rede_neural.json"); st = _j(D / "status_motores.json"); sa = _j(D / "saude.json")
    n_tela = sum(len(v) for v in (fl.get("itens_por_uf") or {}).values())
    sc_ab = next((i.get("valor") for i in (sc.get("instrumentos") or []) if i.get("id") == "es_abertas"), None)
    contagens = {"repositorio_abertas": rr.get("abertas"), "diagnostico_abertas": op["abertas"], "tela_cartoes": n_tela,
                 "fichas": fi.get("total"), "sala_controle_abertas": sc_ab}
    if rr.get("abertas") is not None and n_tela and abs(int(rr["abertas"]) - n_tela) > 0:
        _problema(P, "tela_diverge_do_repositorio", "alta", f"tela mostra {n_tela} oportunidades e o repositório conta {rr['abertas']}", "refazer a tela")
    if sc_ab is not None and rr.get("abertas") is not None and sc_ab != rr["abertas"]:
        _problema(P, "indicadores_desatualizados", "media", f"sala de controle conta {sc_ab} abertas e o repositório {rr['abertas']}", "refazer a sala de controle")
    frescor = {"repositorio": rr.get("em"), "fluxo": fl.get("gerado_em") or fl.get("em"), "fichas": fi.get("em"), "sala_controle": sc.get("em"),
               "status_motores": st.get("gerado_em"), "maestro": ma.get("em"), "rede_neural": rn.get("em"), "saude": sa.get("em")}
    idade = {k: _idade_h(v) for k, v in frescor.items()}
    for k, h in idade.items():
        if h is None or h > FRESCOR_H[k]:
            _problema(P, f"atrasado_{k}", "media", f"{k} sem atualização há {h if h is not None else '?'} h (limite {FRESCOR_H[k]} h)",
                      {"repositorio": "refazer o repositório", "fluxo": "refazer a tela", "fichas": "refazer as fichas", "sala_controle": "refazer a sala de controle",
                       "saude": "refazer a saúde"}.get(k, "ver o fluxo que gera este dado"))
    dec = _j(ROOT / "estado/decisoes_editais.json", {}); dec = dec.get("decisoes") if isinstance(dec.get("decisoes"), dict) else {}
    R = {r["id"]: r for r in (_j(ROOT / "dados/oportunidades/repositorio_unico.json", {}).get("registros") or [])}
    nao_aplicadas = [k for k, v in dec.items() if v.get("estado") in ("descartado", "inscrito") and k in R and not R[k].get("arquivada") and R[k].get("estado") != "fechada"]
    if nao_aplicadas:
        _problema(P, "decisao_nao_aplicada", "alta", f"{len(nao_aplicadas)} decisões da titular ainda não aplicadas no repositório", "aplicar as decisões", len(nao_aplicadas), nao_aplicadas)
    return {"contagens": contagens, "idade_horas": idade, "decisoes_da_titular": len(dec), "decisoes_nao_aplicadas": len(nao_aplicadas)}


def diagnosticar() -> dict:
    hoje = date.today().isoformat(); P: list = []
    s = sistemas(P); o = oportunidades(P, hoje); i = integracao(P, o)
    ordem = {"alta": 0, "media": 1, "baixa": 2}
    P.sort(key=lambda p: (ordem.get(p["gravidade"], 3), p["codigo"]))
    return {"em": datetime.now(timezone.utc).replace(microsecond=0).isoformat(), "sistemas": s, "oportunidades": o, "integracao": i,
            "problemas": P, "contagem_problemas": dict(Counter(p["gravidade"] for p in P)),
            "corrigiveis": sorted({p["correcao"] for p in P if p["correcao"] and not any(t in p["correcao"] for t in ("sem correção", "investigar", "ver o", "retreinar"))})}


# ── correções, em sequência (uma etapa depois da outra) ─────────────────────────────────────────────────────────────
def _etapa(nome: str, fn, log: list) -> None:
    t = time.time()
    try:
        r = fn(); log.append({"etapa": nome, "ok": True, "segundos": round(time.time() - t, 1), "resultado": str(r)[:300]})
    except Exception as e:  # noqa: BLE001
        log.append({"etapa": nome, "ok": False, "segundos": round(time.time() - t, 1), "erro": f"{type(e).__name__}: {str(e)[:300]}"})


def corrigir(diag: dict) -> list:
    precisa = set(diag.get("corrigiveis") or [])
    if not precisa:
        return []
    log: list = []
    if "aplicar as decisões" in precisa:
        from . import decisoes_titular; _etapa("decisões da titular → livros e repositório", decisoes_titular.run, log)
    if precisa & {"criar/vincular livros", "criar/vincular livros e refazer o repositório"}:
        from . import opressores_repositorio; _etapa("livros: criar ou vincular para cada oportunidade", opressores_repositorio.sincronizar, log)
    from . import repositorio_unico
    _etapa("repositório único", lambda: repositorio_unico.construir(gravar=True), log)
    if precisa & {"refazer a tela", "refazer tela e indicadores", "refazer o repositório", "criar/vincular livros", "criar/vincular livros e refazer o repositório", "aplicar as decisões"}:
        from . import fluxo_oportunidades; _etapa("tela das oportunidades (fluxo completo)", fluxo_oportunidades.atualizar_mapa, log)
    from . import fichas_oportunidades, sala_controle, saude
    _etapa("fichas das oportunidades", fichas_oportunidades.run, log)
    _etapa("sala de controle", sala_controle.run, log)
    _etapa("saúde do sistema", saude.checar, log)
    return log


def resumo_md(antes: dict, depois: dict | None, log: list) -> str:
    d = depois or antes; o, s, i = d["oportunidades"], d["sistemas"], d["integracao"]
    L = [f"# Diagnóstico do sistema · {d['em'][:16].replace('T', ' ')} UTC", ""]
    if depois:
        L += [f"Correções aplicadas: {sum(1 for x in log if x['ok'])} de {len(log)} etapas · problemas antes {len(antes['problemas'])} → depois {len(depois['problemas'])}", ""]
        L += [f"- {'ok ' if x['ok'] else 'ERRO'} {x['etapa']} ({x['segundos']} s)" + ("" if x["ok"] else f" — {x['erro']}") for x in log] + [""]
    L += ["## Oportunidades", f"- abertas: {o['abertas']} · validadas: {o['validadas']} ({o['percentual_validadas']}%) · por estado: {o['por_estado']}",
          f"- com livro: {o['com_livro']} · sem livro (problema): {o['sem_livro']} · sem livro por regra: {o['sem_livro_por_regra']} {o['sem_livro_por_regra_motivos']} · livro inexistente: {o['livro_inexistente']}",
          f"- sem site oficial: {o['sem_site_oficial']} · sem prazo: {o['sem_prazo']} · prazo vencido ainda aberta: {o['prazo_vencido']}",
          f"- fora da tela: {o['fora_da_tela']} · sem ficha: {o['sem_ficha']}", f"- itens que mais faltam: {o['itens_que_mais_faltam']}", "",
          "## Sistemas", f"- motores: {s['motores']['funcionando']} funcionando · {s['motores']['em_falha']} em falha · {s['motores']['inativos']} inativos · {len(s['motores']['leitura_parcial'])} com leitura parcial",
          *[f"  - em falha: {m['nome']} — {m['resultado']}" for m in s["motores"]["em_falha_lista"]],
          f"- maestro: cobertura {s['maestro'].get('cobertura_percentual')}% · esgotados {s['maestro'].get('esgotaram_tentativas')}",
          f"- rede neural: AUC {s['rede_neural']['validacao_cruzada'].get('auc')} · rotulados {s['rede_neural'].get('rotulados')} · treinada em {s['rede_neural'].get('modelo_treinado_em')}",
          f"- Cartório: {(s['cartorio'].get('resumo') or {}).get('pct_certificado_12')} certificado · fluxos do GitHub com falha: {s['fluxos_github']['com_falha']}",
          f"- saúde: {len(s['saude']['alertas'])} alerta(s) · índice da sala de controle: {s['sala_controle'].get('indice_saude')}", "",
          "## Integração", f"- contagens: {i['contagens']}", f"- idade (h): {i['idade_horas']}",
          f"- decisões da titular: {i['decisoes_da_titular']} · não aplicadas: {i['decisoes_nao_aplicadas']}", "",
          f"## Problemas ({len(d['problemas'])})"]
    L += [f"- [{p['gravidade']}] {p['texto']}" + (f" → {p['correcao']}" if p["correcao"] else "") for p in d["problemas"]]
    return "\n".join(L) + "\n"


def run(corrigir_: bool = False) -> dict:
    antes = diagnosticar(); log = []; depois = None
    if corrigir_:
        log = corrigir(antes)
        depois = diagnosticar() if log else None
    final = depois or antes
    res = {**final, "corrigido": bool(log), "correcoes": log, "antes": {"problemas": len(antes["problemas"]), "contagem": antes["contagem_problemas"]} if depois else None}
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    RESUMO.write_text(resumo_md(antes, depois, log), encoding="utf-8")
    return {"problemas": len(final["problemas"]), "por_gravidade": final["contagem_problemas"], "corrigido": bool(log),
            "abertas": final["oportunidades"]["abertas"], "sem_livro": final["oportunidades"]["sem_livro"]}


if __name__ == "__main__":
    print(json.dumps(run("--corrigir" in sys.argv), ensure_ascii=False))
