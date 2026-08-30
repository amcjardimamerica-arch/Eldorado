from __future__ import annotations

import json
from pathlib import Path
from .nucleo import ROOT, load_json, now_iso, write_json

def _contains(values, wanted):
    return not wanted or bool(set(values or []) & set(wanted or []))

def evaluate(profile: dict, opportunity: dict, criteria: dict) -> dict:
    req=opportunity.get("requisitos") or {}
    blockers=[]
    if req.get("naturezas_juridicas") and profile.get("natureza_juridica") not in req["naturezas_juridicas"]: blockers.append("natureza_juridica")
    if req.get("territorios") and not _contains(profile.get("territorios"),req["territorios"]): blockers.append("territorio")
    if req.get("areas") and not _contains(profile.get("areas"),req["areas"]): blockers.append("area_atuacao")
    if (profile.get("anos_existencia") or 0) < (req.get("anos_existencia_min") or 0): blockers.append("tempo_existencia")
    missing=sorted(set(req.get("certificacoes") or [])-set(profile.get("certificacoes") or []))
    if missing: blockers.append("certificacoes_obrigatorias")
    if blockers: return {"elegivel":False,"pontuacao":0,"bloqueios":blockers,"faltantes":missing,"explicacao":"Requisito eliminatório não atendido ou não comprovado."}
    weights=criteria["pesos"]
    score=0; reasons=[]
    if not req.get("areas") or _contains(profile.get("areas"),req.get("areas")): score+=weights["tema"]; reasons.append("aderência temática")
    if not req.get("territorios") or _contains(profile.get("territorios"),req.get("territorios")): score+=weights["territorio"]; reasons.append("aderência territorial")
    if profile.get("experiencias"): score+=weights["experiencia"]; reasons.append("experiência cadastrada")
    if profile.get("documentos_validos"): score+=weights["documentacao"]; reasons.append("documentação cadastrada")
    if profile.get("capacidade_execucao"): score+=weights["capacidade_execucao"]; reasons.append("capacidade de execução declarada")
    if opportunity.get("fonte_id") in (profile.get("historico_financiadores") or []): score+=weights["historico_financiador"]; reasons.append("histórico com financiador")
    return {"elegivel":True,"pontuacao":score,"bloqueios":[],"faltantes":missing,"explicacao":", ".join(reasons) or "Sem evidência suficiente para pontuar."}

def run() -> dict:
    criteria=load_json(ROOT/"config/criterios.json"); opp=[]
    db=ROOT/"dados/oportunidades/oportunidades.jsonl"
    if db.exists(): opp=[json.loads(x) for x in db.read_text(encoding="utf-8").splitlines() if x.strip()]
    results={"executado_em":now_iso(),"associacoes":{}}
    for path in sorted((ROOT/"dados/associacoes").glob("*/perfil.json")):
        profile=load_json(path); aid=profile["id"]
        ranked=[]
        for item in opp:
            decision=evaluate(profile,item,criteria); ranked.append({"oportunidade_id":item["id"],"titulo":item["titulo"],"url":item["url"],**decision})
        ranked.sort(key=lambda x:(x["elegivel"],x["pontuacao"]),reverse=True)
        results["associacoes"][aid]=ranked
        write_json(ROOT/"resultados"/aid/"ranking.json",{"associacao_id":aid,"gerado_em":results["executado_em"],"oportunidades":ranked})
    write_json(ROOT/"resultados/resumo.json",results)
    return results

if __name__ == "__main__": print(json.dumps(run(),ensure_ascii=False,indent=2))

