from __future__ import annotations
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from .nucleo import ROOT, load_json, now_iso, sha256, validate_public_https, write_json

def run() -> dict:
    catalog=load_json(ROOT/"biblioteca/leis/catalogo.json"); changed=[]; ok=[]; missing=[]; failures=[]
    for item in catalog["itens"]:
        url=item.get("url_oficial")
        if not url: missing.append(item["id"]); continue
        try:
            validate_public_https(url)
            req=Request(url,headers={"User-Agent":"Eldorado-OSC/3.0 revisao-normativa"})
            with urlopen(req,timeout=45) as response: data=response.read(10_000_001)
            if len(data)>10_000_000: raise ValueError("norma excede limite")
            digest=sha256(data); path=ROOT/"estado/leis"/(item["id"]+".json"); prior=load_json(path) if path.exists() else {}
            if prior.get("sha256") and prior["sha256"]!=digest: changed.append(item["id"])
            write_json(path,{"id":item["id"],"url":url,"sha256":digest,"consultado_em":now_iso(),"mudou_desde_consulta_anterior":item["id"] in changed})
            ok.append(item["id"])
        except (HTTPError,URLError,OSError,ValueError) as exc: failures.append({"id":item["id"],"erro":type(exc).__name__})
    report={"executado_em":now_iso(),"verificadas":ok,"hash_alterado":changed,"sem_url_oficial":missing,"falhas":failures,"revisao_humana_obrigatoria":bool(changed or missing or failures)}
    write_json(ROOT/"estado/revisao_normativa.json",report); return report

if __name__=="__main__": print(json.dumps(run(),ensure_ascii=False,indent=2))
