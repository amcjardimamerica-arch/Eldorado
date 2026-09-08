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



def enviar_arquivo(pasta_id: str, nome: str, dados: bytes, mime: str) -> dict:
    """Envia um arquivo ao acervo do Drive. Contrato do espelhamento de editais.

    Usado por `scripts/espelhar_editais_drive.py` para gravar o PDF do edital
    na pasta de Editais Históricos. Enquanto a integração não estiver ativa e
    credenciada, esta função FALHA de forma explícita — não simula envio, não
    grava marcador de sucesso e não devolve resposta falsa, conforme a regra do
    repositório de nunca simular execução de integração.
    """
    cfg = load_json(ROOT / "config/integracoes.json")["google_drive"]
    if not cfg.get("ativa"):
        raise RuntimeError(
            "integração do Google Drive inativa em config/integracoes.json: "
            "o PDF não foi enviado e nada foi simulado")
    if not os.getenv(cfg["credencial_env"]):
        raise RuntimeError(
            f"credencial ausente em {cfg['credencial_env']}: o PDF não foi enviado")
    raise NotImplementedError(
        "cliente do Drive ainda não implementado neste repositório. O acervo é "
        "populado hoje pela sessão verificadora (dossiê e texto) e este contrato "
        "existe para o espelhamento automático do binário quando a credencial de "
        "serviço for configurada no GitHub Actions.")


if __name__ == "__main__":
    print(json.dumps(readiness(), ensure_ascii=False, indent=2))
