from __future__ import annotations

import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler

from .nucleo import ROOT, append_jsonl, canonical_url, has_prompt_injection, load_json, now_iso, sha256, slug, validate_public_https, write_json

TERMS = re.compile(r"\b(edital|chamada pública|seleção pública|chamamento público|doação|patrocínio|apoio financeiro|fundo|emenda|incentivo)\b", re.I)
DEADLINE = re.compile(r"\b(?:at[eé]|prazo|inscri(?:ção|ções))\D{0,25}(\d{1,2}/\d{1,2}/20\d{2})", re.I)

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
    req=Request(url, headers={"User-Agent":policy["user_agent"],"Accept":"text/html,application/rss+xml,application/atom+xml,text/plain;q=0.8,*/*;q=0.2"})
    with build_opener(SafeRedirect(host)).open(req, timeout=policy["timeout_segundos"]) as response:
        final=response.geturl(); validate_public_https(final, host)
        ctype=response.headers.get_content_type()
        data=response.read(policy["max_bytes"]+1)
        if len(data)>policy["max_bytes"]: raise ValueError("resposta excede limite")
        if ctype not in {"text/html","text/plain","application/rss+xml","application/atom+xml","application/xml","text/xml"}:
            raise ValueError(f"tipo não permitido: {ctype}")
        return data, final, ctype

def candidates(source: dict, data: bytes, final_url: str) -> list[dict]:
    text=data.decode("utf-8", "replace")
    if has_prompt_injection(text):
        return [{"status":"quarentena_prompt_injection","titulo":source["nome"],"url":final_url,"evidencia":"Conteúdo externo contém padrão de controle de modelo."}]
    parser=Links(); parser.feed(text)
    out=[]
    for href,label in parser.links:
        label=html.unescape(re.sub(r"\s+"," ",label)).strip()
        if len(label)<5 or not TERMS.search(label): continue
        url=canonical_url(urljoin(final_url,href))
        if urlsplit(url).scheme!="https": continue
        deadline=DEADLINE.search(label)
        out.append({
            "id":sha256((source["id"]+"|"+url).encode())[:20], "status":"capturada", "titulo":label[:300],
            "url":url, "fonte_id":source["id"], "fonte_nome":source["nome"], "territorio":source["territorio"],
            "tipo_fonte":source["tipo"], "confianca":source["confianca"], "coletado_em":now_iso(),
            "prazo_texto":deadline.group(1) if deadline else None, "evidencia":label[:500], "hash_evidencia":sha256(label.encode())
        })
    unique={item["id"]:item for item in out}
    return list(unique.values())

def run() -> dict:
    cfg=load_json(ROOT/"config/fontes.json"); db=ROOT/"dados/oportunidades/oportunidades.jsonl"
    existing={}
    if db.exists():
        for line in db.read_text(encoding="utf-8").splitlines():
            if line.strip():
                item=json.loads(line); existing[item["id"]]=item
    report={"executado_em":now_iso(),"fontes_total":0,"fontes_ok":0,"fontes_falha":0,"novas":0,"quarentena":0,"falhas":[]}
    for source in cfg["fontes"]:
        if not source.get("ativa"): continue
        report["fontes_total"]+=1
        try:
            data,final,ctype=fetch(source,cfg["politica"]); report["fontes_ok"]+=1
            for item in candidates(source,data,final):
                if item["status"].startswith("quarentena"):
                    report["quarentena"]+=1; append_jsonl(ROOT/"estado/quarentena.jsonl",item); continue
                if item["id"] not in existing: report["novas"]+=1
                existing[item["id"]]=item
        except (HTTPError,URLError,OSError,ValueError) as exc:
            report["fontes_falha"]+=1; report["falhas"].append({"fonte":source["id"],"erro":type(exc).__name__})
    db.parent.mkdir(parents=True,exist_ok=True)
    db.write_text("".join(json.dumps(x,ensure_ascii=False,separators=(",",":"))+"\n" for x in sorted(existing.values(),key=lambda v:v["id"])),encoding="utf-8")
    write_json(ROOT/"estado/ultima_execucao.json",report)
    append_jsonl(ROOT/"estado/auditoria.jsonl",{"evento":"coleta_diaria",**report})
    return report

if __name__ == "__main__": print(json.dumps(run(),ensure_ascii=False,indent=2))
