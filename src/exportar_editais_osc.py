"""ALIMENTAÇÃO DIÁRIA DO SITE editaisOSC (titular, 13/10/2026).

Gera, a partir das oportunidades abertas, um arquivo com SÓ estes campos por oportunidade: nome, link direto da página
do edital (o oficial; nunca agregador nem nada do sistema), objeto, abrangência (federal = todo o Brasil; estadual = UF)
e prazo de inscrição (ou fluxo contínuo). Nada de livros, motores, fontes internas ou identificadores.

Certificação: os itens vão como um texto JSON canônico (`itens_json`) com o seu SHA-256; a requisição inteira é assinada
com HMAC-SHA256 (segredo OSC_SEGREDO). O site recusa o que não conferir. Envio: POST para OSC_URL (segredos do GitHub).
O conteúdo não menciona a origem.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLUXO = ROOT / "docs/dados/fluxo_oportunidades.json"
OBJETOS = {"cultura": "Cultura", "esporte": "Esporte e lazer", "saude": "Saúde", "crianca": "Criança e adolescente",
           "idoso": "Pessoa idosa", "assistencia": "Assistência social", "meio_ambiente": "Meio ambiente e clima",
           "educacao": "Educação", "direitos_humanos": "Direitos humanos"}
AGREGADORES = ("captadores.org.br", "farolcultural", "prosas.com.br", "funcafe", "editaldeculturaeesporte", "editais.net")


def _objeto(area: str | None) -> str:
    a = str(area or "").lower()
    return next((v for k, v in OBJETOS.items() if k in a), "Outros")


def _internacional(x: dict) -> bool:
    ck = x.get("checklist") or {}
    txt = json.dumps({k: v for k, v in (ck.items() if isinstance(ck, dict) else []) if k in ("Território", "Esfera")}, ensure_ascii=False).lower()
    return "internacional" in txt


def itens(hoje: date | None = None) -> list[dict]:
    hoje = hoje or date.today()
    F = json.loads(FLUXO.read_text(encoding="utf-8"))
    out, vistos = [], set()
    for uf, lista in (F.get("itens_por_uf") or {}).items():
        for x in lista:
            link = x.get("link_oficial") or (x.get("inspecao") or {}).get("pagina_oficial")
            if not link or not str(link).startswith("http") or any(a in str(link) for a in AGREGADORES):
                continue
            if uf == "__nac__" and _internacional(x):
                continue
            fim = x.get("fim") if isinstance(x.get("fim"), str) and len(x.get("fim")) == 10 else None
            if fim and fim < hoje.isoformat():
                continue
            chave = (str(x.get("titulo") or "").strip().lower(), link)
            if chave in vistos:
                continue
            vistos.add(chave)
            out.append({"nome": str(x.get("titulo") or "").strip()[:300], "link": link, "objeto": _objeto(x.get("area")),
                        "abrangencia": "federal" if uf == "__nac__" else "estadual", "uf": "" if uf == "__nac__" else uf,
                        "prazo": fim, "continuo": x.get("regime") == "fluxo_continuo"})
    return sorted(out, key=lambda i: (i["prazo"] or "9999", i["nome"]))


def pacote(lista: list[dict]) -> tuple[bytes, str]:
    itens_json = json.dumps(lista, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    h = hashlib.sha256(itens_json.encode("utf-8")).hexdigest()
    corpo = json.dumps({"gerado_em": datetime.now(timezone.utc).replace(microsecond=0).isoformat(), "total": len(lista),
                        "sha256": h, "itens_json": itens_json}, ensure_ascii=False).encode("utf-8")
    return corpo, h


def enviar() -> dict:
    url, segredo = os.environ.get("OSC_URL", ""), os.environ.get("OSC_SEGREDO", "")
    lista = itens(); corpo, h = pacote(lista)
    if not url or not segredo:
        return {"enviado": False, "motivo": "segredos OSC_URL/OSC_SEGREDO não configurados", "itens": len(lista), "sha256": h}
    assinatura = hmac.new(segredo.encode("utf-8"), corpo, hashlib.sha256).hexdigest()
    # 15/10/2026 (análise do sistema): o fluxo 35 falhava 100% sem dizer por quê — agora até 3 tentativas com espera
    # crescente e o motivo (HTTP, resposta do site, rede) sempre registrado
    import time
    ultimo = None
    for tentativa in range(1, 4):
        # 15/10 (ciclo 5): o Mod_Security da hospedagem devolvia HTTP 406 — pedido sem cabeçalhos de navegador
        req = urllib.request.Request(url, data=corpo, method="POST", headers={
            "Content-Type": "application/json; charset=utf-8", "X-Assinatura": assinatura,
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*", "Accept-Language": "pt-BR,pt;q=0.9", "Accept-Encoding": "identity",
            "Origin": "{0.scheme}://{0.netloc}".format(urllib.parse.urlsplit(url)), "Referer": "{0.scheme}://{0.netloc}/".format(urllib.parse.urlsplit(url))})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                bruto = r.read().decode("utf-8", "replace")
            try:
                resp = json.loads(bruto or "{}")
            except ValueError:
                ultimo = {"motivo": "o site respondeu sem JSON", "resposta": bruto[:300]}; break
            if resp.get("sha256") != h:
                ultimo = {"motivo": "o site não confirmou o mesmo hash", "resposta": json.dumps(resp, ensure_ascii=False)[:300]}; break
            return {"enviado": True, "itens": len(lista), "sha256": h, "confirmado_pelo_site": resp.get("itens"), "tentativas": tentativa}
        except urllib.error.HTTPError as e:
            ultimo = {"motivo": f"HTTP {e.code} do site", "http": e.code, "resposta": (e.read() or b"").decode("utf-8", "replace")[:300]}
            if e.code < 500 and e.code != 429:
                break                                   # 4xx (menos 429) não melhora repetindo
        except Exception as e:  # noqa: BLE001
            ultimo = {"motivo": f"rede: {type(e).__name__}: {str(e)[:160]}"}
        time.sleep(10 * tentativa)
    return {"enviado": False, "itens": len(lista), "sha256": h, **(ultimo or {})}

if __name__ == "__main__":
    if "--enviar" in sys.argv:
        r = enviar()
        print(json.dumps(r, ensure_ascii=False))
        if not r.get("enviado") and "não configurados" not in str(r.get("motivo")):
            print(f"::error title=envio ao site EditaisOSC::{r.get('motivo')} · {str(r.get('resposta') or '')[:200]}", file=sys.stderr)
            sys.exit(1)
    else:
        L = itens(); _, h = pacote(L)
        print(json.dumps({"itens": len(L), "federais": sum(1 for i in L if i["abrangencia"] == "federal"), "sha256": h,
                          "objetos": sorted({i["objeto"] for i in L}), "exemplo": L[:2]}, ensure_ascii=False, indent=1))
