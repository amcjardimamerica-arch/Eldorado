from __future__ import annotations

import html
import json
import re
import time
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
from xml.etree import ElementTree as ET

from .nucleo import (
    ROOT, append_jsonl, canonical_url, carregar_oportunidades, gravar_oportunidades,
    has_prompt_injection, load_json, merge_registro, novo_id, now_iso,
    robots_permite, sha256, validate_public_https, write_json,
)

TERMS = re.compile(r"\b(edital|chamada pública|seleção pública|chamamento público|credenciamento|doação|patrocínio|apoio financeiro|fomento|fundo|emenda|incentivo|prêmio)\b", re.I)
DISCOVERY = re.compile(r"(edital|chamad|chamament|credenciament|sele[cç][aã]o|oportunidade|convenio|parceria|fomento|doa[cç][aã]o|patrocin|fundo|emenda|incentivo|premio|pr[êe]mio|transparencia|licitac)", re.I)
DEADLINE = re.compile(r"\b(?:at[eé]|prazo|inscri(?:ção|ções))\D{0,25}(\d{1,2}/\d{1,2}/20\d{2})", re.I)
YEAR = re.compile(r"\b(20(?:2[0-9]|1[0-9]))\b")
XML_TYPES = {"application/rss+xml", "application/atom+xml", "application/xml", "text/xml"}

class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self._href=None; self._text=[]
    def handle_starttag(self, tag, attrs):
        if tag == "a": self._href=dict(attrs).get("href"); self._text=[]
    def handle_data(self, data):
        if self._href is not None: self._text.append(data)
    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            self.links.append((self._href, " ".join(self._text).strip())); self._href=None

class SafeRedirect(HTTPRedirectHandler):
    def __init__(self, host): self.host=host
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_public_https(newurl, self.host)
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def fetch(source: dict, policy: dict) -> tuple[bytes, str, str]:
    url=source["url"]; host=urlsplit(url).hostname
    validate_public_https(url, host)
    req=Request(url, headers={"User-Agent":policy["user_agent"],"Accept":"text/html,application/rss+xml,application/atom+xml,application/json,text/plain;q=0.8,*/*;q=0.2"})
    with build_opener(SafeRedirect(host)).open(req, timeout=policy["timeout_segundos"]) as response:
        final=response.geturl(); validate_public_https(final, host)
        ctype=response.headers.get_content_type()
        data=response.read(policy["max_bytes"]+1)
        if len(data)>policy["max_bytes"]: raise ValueError("resposta excede limite")
        if ctype not in {"text/html","text/plain","application/json"} | XML_TYPES:
            raise ValueError(f"tipo não permitido: {ctype}")
        return data, final, ctype

def montar_item(source: dict, url: str, label: str, extra: dict | None = None) -> dict:
    deadline=DEADLINE.search(label); year=YEAR.search(label)
    item={
        "id":novo_id(url), "status":"capturada", "titulo":label[:300],
        "url":url, "fonte_id":source["id"], "fonte_nome":source["nome"], "territorio":source.get("territorio","BR"),
        "tipo_fonte":source.get("tipo"), "confianca":source.get("confianca"), "coletado_em":now_iso(),
        "nivel":source.get("nivel"), "uf":source.get("uf"), "municipio":source.get("municipio"),
        "areas_fonte":source.get("areas") or [],
        "prazo_texto":deadline.group(1) if deadline else None, "ano_referencia":int(year.group(1)) if year else None,
        "evidencia":label[:500], "hash_evidencia":sha256(label.encode()),
    }
    if extra: item.update(extra)
    return item

def _host_permitido(source: dict, url: str, final_url: str) -> bool:
    host=urlsplit(url).hostname or ""
    allowed=source.get("hosts_links") or [urlsplit(source.get("url") or final_url).hostname]
    return urlsplit(url).scheme=="https" and any(host == a or host.endswith("." + a) for a in allowed)

def candidates(source: dict, data: bytes, final_url: str, ctype: str = "text/html") -> list[dict]:
    text=data.decode("utf-8", "replace")
    if has_prompt_injection(text):
        return [{"status":"quarentena_prompt_injection","titulo":source["nome"],"url":final_url,
                 "pagina":canonical_url(final_url),"evidencia":"Conteúdo externo contém padrão de controle de modelo.","registrado_em":now_iso()}]
    out=[]
    if ctype in XML_TYPES or text.lstrip()[:100].startswith("<?xml"):
        try: root=ET.fromstring(data)
        except ET.ParseError: root=None
        if root is not None:
            ns={"atom":"http://www.w3.org/2005/Atom"}
            entries=root.findall(".//item")+root.findall(".//atom:entry",ns)
            for node in entries:
                title=(node.findtext("title") or node.findtext("atom:title",namespaces=ns) or "").strip()
                link=node.findtext("link") or ""
                if not link:
                    el=node.find("atom:link",ns); link=el.get("href") if el is not None else ""
                link=canonical_url(urljoin(final_url,link.strip()))
                if len(title)>=5 and TERMS.search(title) and _host_permitido(source,link,final_url):
                    out.append(montar_item(source,link,title))
    else:
        parser=Links(); parser.feed(text)
        for href,label in parser.links:
            label=html.unescape(re.sub(r"\s+"," ",label)).strip()
            if len(label)<5 or not TERMS.search(label): continue
            url=canonical_url(urljoin(final_url,href))
            if not _host_permitido(source,url,final_url): continue
            out.append(montar_item(source,url,label))
    unique={item["id"]:item for item in out}
    return list(unique.values())

def source_in_scope(source: dict, scope: dict) -> bool:
    if source.get("nivel") not in scope.get("niveis_ativos", []): return False
    if source.get("uf") and source["uf"] not in scope.get("ufs_ativas", []): return False
    if source.get("municipio") and source["municipio"] not in scope.get("municipios_ativos", []): return False
    selected=set(scope.get("areas_ativas", [])); areas=set(source.get("areas") or [])
    return not areas or not selected or bool(areas & selected)

def allowed_url(source: dict, url: str) -> bool:
    host=urlsplit(url).hostname or ""
    return urlsplit(url).scheme == "https" and any(host == item or host.endswith("." + item) for item in source.get("hosts_links", []))

def discover_pages(source: dict, data: bytes, final_url: str) -> list[str]:
    parser=Links(); parser.feed(data.decode("utf-8","replace")); found=[]
    for href,label in parser.links:
        url=canonical_url(urljoin(final_url,href)); signal=f"{label} {urlsplit(url).path}"
        if allowed_url(source,url) and DISCOVERY.search(signal): found.append(url)
    return list(dict.fromkeys(found))

def record_edital_history(item: dict, previous: dict | None) -> None:
    tracked=("titulo","url","status","prazo_texto","ano_referencia","evidencia","hash_evidencia","requisitos")
    changes={key:{"anterior":previous.get(key) if previous else None,"atual":item.get(key)} for key in tracked if not previous or previous.get(key)!=item.get(key)}
    if not changes: return
    folder=ROOT/"dados/editais"/item["id"]; folder.mkdir(parents=True,exist_ok=True)
    append_jsonl(folder/"historico.jsonl",{"registrado_em":now_iso(),"fonte_id":item.get("fonte_id"),"alteracoes":changes})
    write_json(folder/"atual.json",item)

def crawl_source(source: dict, policy: dict) -> tuple[list[dict],dict]:
    state_path=ROOT/"estado/fontes"/(source["id"]+".json")
    state=load_json(state_path) if state_path.exists() else {"paginas":{},"conhecidas":[]}
    priority=[source["url"],*state.get("conhecidas",[])]
    queue=list(dict.fromkeys(priority)); visited=set(); found=[]; changed_pages=0; robots_skips=0
    limit=int(source.get("max_paginas") or policy.get("max_paginas_por_fonte",40))
    interval=float(policy.get("intervalo_segundos",1))
    for url in iter(lambda: queue.pop(0) if queue else None, None):
        if len(visited)>=limit: break
        if url in visited or not allowed_url(source,url): continue
        visited.add(url)
        if policy.get("respeitar_robots",True) and not robots_permite(url,policy["user_agent"]):
            robots_skips+=1; continue
        data,final,ctype=fetch({**source,"url":url},policy); digest=sha256(data)
        if interval: time.sleep(interval)
        old=state.get("paginas",{}).get(canonical_url(final))
        if old==digest: continue
        changed_pages+=1; state.setdefault("paginas",{})[canonical_url(final)]=digest
        found.extend(candidates(source,data,final,ctype))
        if ctype=="text/html":
            for discovered in discover_pages(source,data,final):
                if discovered not in visited and discovered not in queue: queue.append(discovered)
    known=list(dict.fromkeys([*state.get("conhecidas",[]),*visited]))[:limit]
    state.update({"conhecidas":known,"ultima_verificacao_completa":now_iso(),"paginas_alteradas":changed_pages,"bloqueadas_por_robots":robots_skips})
    write_json(state_path,state)
    return found,state

MODOS_CRAWL={"html_publico","rss_publico"}

def run() -> dict:
    cfg=load_json(ROOT/"config/fontes.json"); scope=load_json(ROOT/"config/escopo.json")
    existing=carregar_oportunidades()
    report={"executado_em":now_iso(),"fontes_catalogadas":len(cfg["fontes"]),"fontes_total":0,"fontes_ok":0,"fontes_falha":0,"fontes_fora_escopo":0,"fontes_manuais":0,"fontes_api":0,"novas":0,"atualizadas":0,"quarentena":0,"falhas":[],"escopo":{k:scope.get(k) for k in ("ufs_ativas","niveis_ativos")}}
    queued=set()
    queue_path=ROOT/"estado/fila_fontes.json"
    if queue_path.exists(): queued=set(load_json(queue_path).get("fontes",[]))
    sources=sorted(cfg["fontes"],key=lambda x:(x["id"] not in queued,x["id"]))
    report["paginas_alteradas"]=0
    for source in sources:
        if not source.get("ativa"): continue
        if not source_in_scope(source,scope): report["fontes_fora_escopo"]+=1; continue
        modo=source.get("modo","html_publico")
        if modo.startswith("api_"): report["fontes_api"]+=1; continue  # tratadas em src.coletores_api
        if modo not in MODOS_CRAWL or modo not in cfg["politica"].get("modos_coleta_permitidos",[]):
            report["fontes_manuais"]+=1; continue
        report["fontes_total"]+=1
        try:
            rows,state=crawl_source(source,cfg["politica"]); report["fontes_ok"]+=1; report["paginas_alteradas"]+=state["paginas_alteradas"]
            for item in rows:
                if item["status"].startswith("quarentena"):
                    report["quarentena"]+=1; append_jsonl(ROOT/"estado/quarentena.jsonl",item); continue
                previous=existing.get(item["id"])
                merged=merge_registro(previous,item)
                if previous is None: report["novas"]+=1
                elif merged!=previous: report["atualizadas"]+=1
                record_edital_history(merged,previous)
                existing[item["id"]]=merged
        except (HTTPError,URLError,OSError,ValueError) as exc:
            report["fontes_falha"]+=1; report["falhas"].append({"fonte":source["id"],"erro":type(exc).__name__})
    gravar_oportunidades(existing)
    write_json(ROOT/"estado/ultima_execucao.json",report)
    write_json(queue_path,{"fontes":[],"consumido_em":now_iso()})
    append_jsonl(ROOT/"estado/auditoria.jsonl",{"evento":"coleta_diaria",**report})
    return report

if __name__ == "__main__": print(json.dumps(run(),ensure_ascii=False,indent=2))
