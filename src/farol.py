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
    if blockers: return {"elegivel":False,"pontuacao":0,"faixa":"sem_enquadramento","bloqueios":blockers,"faltantes":missing,"explicacao":"Requisito eliminatório não atendido ou não comprovado.","acoes_para_maximizar":["obter ou comprovar os requisitos faltantes sem alterar fatos"]}
    weights=criteria["pesos"]
    score=0; reasons=[]
    if not req.get("areas") or _contains(profile.get("areas"),req.get("areas")): score+=weights["tema"]; reasons.append("aderência temática")
    if not req.get("territorios") or _contains(profile.get("territorios"),req.get("territorios")): score+=weights["territorio"]; reasons.append("aderência territorial")
    if profile.get("experiencias"): score+=weights["experiencia"]; reasons.append("experiência cadastrada")
    if profile.get("documentos_validos"): score+=weights["documentacao"]; reasons.append("documentação cadastrada")
    if profile.get("capacidade_execucao"): score+=weights["capacidade_execucao"]; reasons.append("capacidade de execução declarada")
    if opportunity.get("fonte_id") in (profile.get("historico_financiadores") or []): score+=weights["historico_financiador"]; reasons.append("histórico com financiador")
    band="alta" if score>=80 else "moderada" if score>=60 else "baixa"
    actions=[]
    if not profile.get("documentos_validos"): actions.append("validar documentação institucional exigida")
    if not profile.get("capacidade_execucao"): actions.append("comprovar equipe, orçamento, governança e capacidade de execução")
    if not profile.get("experiencias"): actions.append("anexar evidências de experiência compatível")
    return {"elegivel":True,"pontuacao":score,"faixa":band,"bloqueios":[],"faltantes":missing,"explicacao":", ".join(reasons) or "Sem evidência suficiente para pontuar.","acoes_para_maximizar":actions}

def run() -> dict:
    criteria=load_json(ROOT/"config/criterios.json"); opp=[]
    db=ROOT/"dados/oportunidades/oportunidades.jsonl"
    if db.exists():
        opp=[json.loads(x) for x in db.read_text(encoding="utf-8").splitlines() if x.strip()]
        opp=[x for x in opp if x.get("status") in {"verificada_primaria","verificada_dupla"}]
    executed=now_iso(); processed=0
    paths=list((ROOT/"dados/associacoes").glob("*/perfil_publico.json"))
    forbidden={"cpf","rg","dados_bancarios","telefone_pessoal","email_pessoal","endereco_residencial","documentos_pessoais"}
    for path in sorted(paths):
        profile=load_json(path); aid=profile["id"]
        if path.parent.name!=aid: raise ValueError(f"perfil {aid} fora do diretório exclusivo")
        exposed=forbidden & set(profile)
        if exposed:
            raise ValueError(f"perfil público {aid} contém campos proibidos: {sorted(exposed)}")
        ranked=[]
        for item in opp:
            decision=evaluate(profile,item,criteria); ranked.append({"oportunidade_id":item["id"],"titulo":item["titulo"],"url":item["url"],**decision})
        ranked.sort(key=lambda x:(x["elegivel"],x["pontuacao"]),reverse=True)
        write_json(path.parent/"farol/rankings/ultimo.json",{"associacao_id":aid,"gerado_em":executed,"oportunidades":ranked}); processed+=1
    return {"executado_em":executed,"associacoes_processadas":processed}

if __name__ == "__main__": print(json.dumps(run(),ensure_ascii=False,indent=2))
