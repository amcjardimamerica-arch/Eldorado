"""COLETA ASSISTIDA — o que o robô não pode ler, o titular (ou o Claude no Chrome) lê no navegador.

Para os sites cujo robots.txt proíbe robôs (Prosas, FINEP), que só abrem com JavaScript (Itaú Social), que recusam
até o IP brasileiro, ou cuja rota ainda precisa ser levantada. Não se burla nada: é uma PESSOA abrindo a página no
próprio navegador, no ritmo de uma pessoa, e guardando o que a página mostra.

  1. A fila fica em estado/indexadores/fila_assistida.json (e no painel): o que abrir, por quê e como.
  2. Na página aberta, o botão "Capturar indícios" (arraste-o de docs/coleta-assistida.html para a barra de
     favoritos) lê o que a página já carregou — o widget do Prosas, dados estruturados, links de edital com data —
     e baixa o arquivo indicios-<site>-<data>.json. Páginas do mesmo site se acumulam até o titular baixar.
  3. O arquivo vai para entrada_manual/indexadores/ (arrastar na página de envio do GitHub). O motor importa na
     próxima rodada: cada item vira indício, com a rota "assistida", e segue o fluxo como os demais.
  4. Enquanto isso, a ROTA INDIRETA (outro indexador que pode ser lido e que também publica esses editais, como a
     página do CapitaAI sobre o Prosas) e o ÂNGULO DE BUSCA do Piloto - Espião cobrem o site.

Formato do arquivo (o botão já gera assim):
  {"eldorado": "indicios-v1", "capturado_em": "...", "paginas": [{"url", "titulo", "host", "itens": [
      {"titulo", "url", "prazo"?, "financiador"?, "valor"?, "uf"?, "oficial"?, "texto"?, "continuo"?}]}]}
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

from . import extracao as X
from .leitores import item
from .motor import ESTADO, ROOT, _j, aplicar, catalogo

ENTRADA = ROOT / "entrada_manual/indexadores"
PLATAFORMAS_OFICIAIS = ("prosas.com.br", "mapa.cultura.gov.br", "editais.itausocial.org.br", "editais.baoba.org.br")
_DATA = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _site_do_host(host: str, cat: dict) -> dict | None:
    h = (host or "").lower().replace("www.", "")
    for s in cat.get("sites") or []:
        hosts = {(urlsplit(u).hostname or "").lower().replace("www.", "") for u in [s.get("url"), s.get("pagina")] + list(s.get("listas") or []) if u}
        if h in hosts:
            return s
    return None


def validar(dado: dict) -> list[str]:
    erros = []
    if not isinstance(dado, dict) or dado.get("eldorado") != "indicios-v1":
        return ["não é um arquivo de captura do Eldorado (campo 'eldorado' diferente de 'indicios-v1')"]
    if not isinstance(dado.get("paginas"), list):
        erros.append("sem a lista 'paginas'")
    return erros


def importar(hoje: date | None = None, gravar: bool = True) -> dict:
    """Importa os arquivos novos de entrada_manual/indexadores/ (cada arquivo uma vez, pelo hash).
    gravar=False devolve as partes do delta (itens, importados, capturas) para a rodada aplicar junto."""
    hoje = hoje or date.today()
    cat = catalogo()
    est = _j(ESTADO, {"sites": {}})
    feitos = dict(est.get("importados") or {})
    rel = {"arquivos": 0, "itens": 0, "recusados": [], "delta": {"itens": [], "importados": {}, "capturas": {}}}
    d = rel["delta"]
    for arq in sorted(ENTRADA.glob("*.json")) if ENTRADA.exists() else []:
        bruto = arq.read_bytes()
        h = hashlib.sha256(bruto).hexdigest()[:16]
        if h in feitos:
            continue
        try:
            dado = json.loads(bruto.decode("utf-8"))
        except Exception:
            rel["recusados"].append({"arquivo": arq.name, "motivo": "JSON ilegível"}); d["importados"][h] = {"arquivo": arq.name, "recusado": True}; continue
        erros = validar(dado)
        if erros:
            rel["recusados"].append({"arquivo": arq.name, "motivo": "; ".join(erros)}); d["importados"][h] = {"arquivo": arq.name, "recusado": True}; continue
        rel["arquivos"] += 1
        n_arq = 0
        for pg in dado["paginas"][:200]:
            host = (pg.get("host") or urlsplit(pg.get("url") or "").hostname or "").lower()
            s = _site_do_host(host, cat) or {"id": "captura-" + re.sub(r"[^a-z0-9]+", "-", host).strip("-")[:40], "nome": f"Coleta assistida — {host}",
                                              "motor": "idx-assistido"}
            if s.get("mesmo_que"):
                s = next((x for x in cat.get("sites") or [] if x["id"] == s["mesmo_que"]), s)
            ctx = {"hoje": hoje, "rota": "assistida", "limites": {}}
            for it in (pg.get("itens") or [])[:500]:
                tit, url = X.limpar(it.get("titulo"), 300), str(it.get("url") or "")
                if len(tit.split()) < 2 or not url.startswith(("http://", "https://")):
                    continue
                pz = it.get("prazo") if isinstance(it.get("prazo"), str) and _DATA.match(it.get("prazo") or "") else X.prazo(it.get("texto") or "", hoje)
                hu = (urlsplit(url).hostname or "").lower().replace("www.", "")
                oficial = it.get("oficial") if str(it.get("oficial") or "").startswith("http") else (url if any(hu.endswith(p) for p in PLATAFORMAS_OFICIAIS) else None)
                d["itens"].append(item(s, ctx, titulo=tit, pagina=url, link_oficial=oficial, prazo=pz,
                                       financiador=it.get("financiador"), valor=it.get("valor") or X.valor(it.get("texto") or ""),
                                       uf=it.get("uf") if it.get("uf") in X.UFS else X.uf(tit), resumo=it.get("texto"),
                                       texto_perfil=f"{tit} {it.get('texto') or ''}",
                                       extra={"continuo": True} if it.get("continuo") else None))
                n_arq += 1
            d["capturas"][s["id"]] = {"em": dado.get("capturado_em") or hoje.isoformat(), "itens": len(pg.get("itens") or []), "arquivo": arq.name}
        rel["itens"] += n_arq
        d["importados"][h] = {"arquivo": arq.name, "em": hoje.isoformat(), "itens": n_arq}
    if gravar and (d["importados"]):
        from .motor import agora_utc, BRT
        rel["aplicado"] = aplicar({"hoje": hoje.isoformat(), "em": agora_utc().isoformat(timespec="seconds"), **d})
    return rel
