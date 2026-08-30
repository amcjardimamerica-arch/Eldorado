"""Verificação diária leve: detecta raízes alteradas e prioriza a varredura profunda."""
from __future__ import annotations
import json
from urllib.error import HTTPError, URLError
from .eldorado import fetch, source_in_scope
from .nucleo import ROOT, canonical_url, load_json, now_iso, sha256, write_json

def run() -> dict:
    cfg=load_json(ROOT/"config/fontes.json"); scope=load_json(ROOT/"config/escopo.json")
    queue_path=ROOT/"estado/fila_fontes.json"; prior=load_json(queue_path).get("fontes",[]) if queue_path.exists() else []
    changed=set(prior); failures=[]; checked=0
    for source in cfg["fontes"]:
        if not source.get("ativa") or not source_in_scope(source,scope) or source.get("modo","html_publico")!="html_publico": continue
        checked+=1
        try:
            data,_,_=fetch(source,cfg["politica"]); digest=sha256(data)
            state_path=ROOT/"estado/fontes"/(source["id"]+".json")
            state=load_json(state_path) if state_path.exists() else {}
            root_hash=state.get("paginas",{}).get(canonical_url(source["url"]))
            if digest!=root_hash: changed.add(source["id"])
        except (HTTPError,URLError,OSError,ValueError) as exc:
            failures.append({"fonte":source["id"],"erro":type(exc).__name__})
    report={"executado_em":now_iso(),"fontes_verificadas":checked,"fontes_na_fila":len(changed),"falhas":failures}
    write_json(queue_path,{"fontes":sorted(changed),"atualizado_em":report["executado_em"]})
    write_json(ROOT/"estado/ultima_sentinela.json",report)
    return report

if __name__=="__main__": print(json.dumps(run(),ensure_ascii=False,indent=2))
