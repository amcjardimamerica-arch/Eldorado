"""Contrato futuro do Google Drive. Não acessa a rede enquanto a integração estiver inativa."""
from __future__ import annotations
import json, os
from .nucleo import ROOT, load_json, now_iso

def readiness() -> dict:
    cfg=load_json(ROOT/"config/integracoes.json")["google_drive"]
    associations={}
    seen=set()
    for aid,item in cfg["associacoes"].items():
        env=item["folder_id_env"]; folder=os.getenv(env)
        if folder and folder in seen: raise ValueError("uma pasta do Drive não pode pertencer a duas associações")
        if folder: seen.add(folder)
        associations[aid]={"ativa":bool(cfg["ativa"] and item.get("ativa")),"folder_configurado":bool(folder),"folder_id_env":env}
    return {"verificado_em":now_iso(),"integracao_ativa":cfg["ativa"],"credencial_configurada":bool(os.getenv(cfg["credencial_env"])),"associacoes":associations,"status":"pronta_para_configuracao_futura" if not cfg["ativa"] else "exige_conector_autorizado"}

if __name__=="__main__": print(json.dumps(readiness(),ensure_ascii=False,indent=2))
