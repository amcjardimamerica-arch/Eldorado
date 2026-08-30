from __future__ import annotations
import json
from .nucleo import ROOT, load_json, now_iso, write_json

VERIFIED={"verificada_primaria","verificada_dupla"}

def assess(profile: dict, opportunity: dict) -> dict:
    reasons=[]; risks=[]; score=0
    if opportunity.get("status") not in VERIFIED:
        return {"acionar_farol":False,"pontuacao_preliminar":0,"faixa":"insuficiente","razoes":[],"riscos":["oportunidade ainda não verificada na fonte primária"]}
    score+=30; reasons.append("fonte primária verificada")
    opp_areas=set((opportunity.get("requisitos") or {}).get("areas") or opportunity.get("areas_fonte") or [])
    profile_areas=set(profile.get("areas") or [])
    if opp_areas and opp_areas & profile_areas: score+=35; reasons.append("aderência temática explícita")
    elif not opp_areas: score+=10; risks.append("área do edital ainda não estruturada")
    else: risks.append("sem aderência temática comprovada")
    uf=opportunity.get("uf"); territories=set(profile.get("territorios") or [])
    if not uf or uf in territories or any(x.startswith(uf+"/") for x in territories): score+=25; reasons.append("aderência territorial")
    else: risks.append("território incompatível")
    if profile.get("experiencias"): score+=10; reasons.append("experiência institucional cadastrada")
    level="alta" if score>=80 else "moderada" if score>=60 else "baixa"
    return {"acionar_farol":score>=60,"pontuacao_preliminar":score,"faixa":level,"razoes":reasons,"riscos":risks}

def run() -> list[dict]:
    db=ROOT/"dados/oportunidades/oportunidades.jsonl"; opportunities=[]
    if db.exists(): opportunities=[json.loads(x) for x in db.read_text(encoding="utf-8").splitlines() if x.strip()]
    triggers=[]
    for profile_path in sorted((ROOT/"dados/associacoes").glob("*/perfil_publico.json")):
        profile=load_json(profile_path); aid=profile["id"]
        if profile_path.parent.name!=aid: raise ValueError(f"perfil {aid} fora de seu universo")
        for opportunity in opportunities:
            decision=assess(profile,opportunity)
            if decision["acionar_farol"]:
                payload={"associacao_id":aid,"oportunidade_id":opportunity["id"],"titulo":opportunity["titulo"],"url":opportunity["url"],"avaliado_em":now_iso(),**decision}
                write_json(profile_path.parent/"farol/triagens"/(opportunity["id"]+".json"),payload); triggers.append(payload)
    return triggers

if __name__=="__main__": print(json.dumps(run(),ensure_ascii=False,indent=2))
