from __future__ import annotations
import json
from datetime import datetime, timezone
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET
from .nucleo import ROOT, canonical_url, load_json, now_iso, sha256, slug, validate_public_https

def host_allowed(url: str, domain: str) -> bool:
    host=urlsplit(url).hostname or ""
    return host == domain or host.endswith("." + domain)

def run(limit_per_query: int = 10) -> dict:
    cfg=load_json(ROOT/"config/retrospectivo.json"); db=ROOT/"dados/oportunidades/oportunidades.jsonl"; existing={}
    if db.exists():
        for line in db.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row=json.loads(line); existing[row["id"]]=row
    current=datetime.now(timezone.utc).year; years=range(current-cfg["janela_anos"]+1,current+1)
    queries=[]
    for funder in cfg["financiadores"]:
        if not funder.get("ativa") or not funder.get("dominio_oficial"): continue
        name=funder["nome"]; domain=funder["dominio_oficial"]
        for year in years:
            for template in cfg["consultas_base"]:
                query=template.format(nome=name,ano=year,dominio=domain)
                queries.append((name,domain,year,query))
    if not queries:
        return {"novas_pistas":0,"consultas":0,"consultas_com_falha":0,"proximo_cursor":0,"executado_em":now_iso()}
    cursor_path=ROOT/"estado/cursor_retrospectivo.json"
    cursor=load_json(cursor_path).get("proxima",0) if cursor_path.exists() else 0
    selected=[queries[(cursor+i)%len(queries)] for i in range(min(cfg["max_consultas_por_execucao"],len(queries)))]
    found=errors=0
    for name,domain,year,query in selected:
                url=cfg["motor"].format(consulta=quote(query)); validate_public_https(url,"www.bing.com")
                try:
                    req=Request(url,headers={"User-Agent":"Eldorado-OSC/1.0"})
                    with urlopen(req,timeout=20) as response: data=response.read(2_000_001)
                    if len(data)>2_000_000: raise ValueError("resposta excede limite")
                    root=ET.fromstring(data)
                    for node in root.findall(".//item")[:limit_per_query]:
                        title=(node.findtext("title") or "").strip(); link=canonical_url(node.findtext("link") or "")
                        if not title or urlsplit(link).scheme!="https" or not host_allowed(link,domain): continue
                        oid=sha256(("retro|"+link).encode())[:20]
                        if oid in existing: continue
                        existing[oid]={"id":oid,"status":"descoberta_nao_verificada","titulo":title[:300],"url":link,"fonte_id":slug(name),"fonte_nome":name,"territorio":"BR","tipo_fonte":"busca_retroativa_dominio_catalogado","confianca":"pista","coletado_em":now_iso(),"ano_pesquisado":year,"dominio_autorizado":domain,"consulta_origem":query,"prazo_texto":None,"evidencia":title[:500],"hash_evidencia":sha256(title.encode())}; found+=1
                except Exception:
                    errors+=1
    db.write_text("".join(json.dumps(x,ensure_ascii=False,separators=(",",":"))+"\n" for x in sorted(existing.values(),key=lambda v:v["id"])),encoding="utf-8")
    next_cursor=(cursor+len(selected))%len(queries)
    cursor_path.parent.mkdir(parents=True,exist_ok=True); cursor_path.write_text(json.dumps({"proxima":next_cursor,"total":len(queries)},indent=2)+"\n",encoding="utf-8")
    return {"novas_pistas":found,"consultas":len(selected),"consultas_com_falha":errors,"proximo_cursor":next_cursor,"executado_em":now_iso()}

if __name__=="__main__": print(json.dumps(run(),ensure_ascii=False,indent=2))
