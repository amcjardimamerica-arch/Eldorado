#!/usr/bin/env python3
"""SONDAGEM DAS FONTES DE DESTINAÇÃO TRIBUTÁRIA (titular, 26/09) — roda no servidor do GitHub.

1. RECEITA FEDERAL. A LC 187/2021 acrescentou ao CTN (art. 198, §3º, IV) a permissão de divulgar benefícios
   tributários de pessoa jurídica; a Lei 14.973/2024 criou a DIRBI (declaração mensal de benefícios). Procura,
   nas páginas de dados abertos e de transparência da Receita, conjuntos com beneficiário por CNPJ — e se
   incluem deduções do IRPJ por doação (Rouanet, FIA, Idoso, Esporte, PRONON, PRONAS).
2. LEI DE INCENTIVO AO ESPORTE. A página está em defeso eleitoral ('Conteúdo restrito'). Procura as cópias
   anteriores no Internet Archive (web.archive.org): planilhas e relatórios de projetos captados e patrocinadores.

Grava tudo o que achou — e o que não achou — em biblioteca_alexandria/base/incentivos/sondagem_fontes.json;
arquivos de dados baixados vão para biblioteca_alexandria/base/incentivos/historico/.
"""
from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "biblioteca_alexandria/base/incentivos"
HIST = SAIDA / "historico"
UA = {"User-Agent": "Mozilla/5.0 (Eldorado; associacao sem fins lucrativos; dados publicos)"}
CHAVE = re.compile(r"benef[ií]c|incentiv|ren[uú]ncia|gasto[s]? tribut|dirbi|transpar[eê]ncia fiscal|doa[cç][õo]|imunidade|dgt|lei 14\.973|lc 187", re.I)
DADO = re.compile(r"\.(csv|xlsx?|zip|json|ods)(\?|$)", re.I)


class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.l = []; self._h = None; self._t = []
    def handle_starttag(self, tag, a):
        if tag == "a":
            self._h = dict(a).get("href"); self._t = []
    def handle_data(self, d):
        if self._h is not None:
            self._t.append(d)
    def handle_endtag(self, tag):
        if tag == "a" and self._h:
            self.l.append((self._h, " ".join("".join(self._t).split())[:160])); self._h = None


def get(url: str, tempo: int = 40, bruto: bool = False):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=tempo) as r:
            b = r.read(40_000_000)
            return r.status, (b if bruto else b.decode("utf-8", "ignore")), r.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        return e.code, None, ""
    except Exception as e:
        return -1, str(e)[:120], ""


def receita() -> dict:
    semente = [
        "https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/dados-abertos",
        "https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/dados-abertos/receitadata",
        "https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/publicacoes/relatorios/renuncia-fiscal",
        "https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/institucional/transparencia",
        "https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/declaracoes-e-demonstrativos/dirbi",
        "https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/dados-abertos/beneficios-fiscais",
        "https://dadosabertos.rfb.gov.br/",
    ]
    visitadas, achados, paginas = set(), [], []
    fila = [(u, 0) for u in semente]
    while fila and len(visitadas) < 45:
        u, prof = fila.pop(0)
        if u in visitadas:
            continue
        visitadas.add(u)
        cod, html, _ = get(u)
        paginas.append({"url": u, "http": cod})
        if cod != 200 or not isinstance(html, str):
            continue
        p = Links(); p.feed(html)
        for h, rot in p.l:
            full = urljoin(u, h or "")
            if not full.startswith("http"):
                continue
            alvo = f"{rot} {full}"
            if DADO.search(full) and CHAVE.search(alvo):
                achados.append({"arquivo": full, "rotulo": rot, "pagina": u})
            elif CHAVE.search(alvo) and prof < 2 and "receitafederal" in full and full not in visitadas:
                fila.append((full, prof + 1))
        time.sleep(0.3)
    # a página achou algo sobre dedução por doação?
    return {"paginas_visitadas": paginas, "arquivos_de_dados": achados[:80],
            "tem_por_cnpj": any(re.search(r"cnpj|benefici[aá]ri|pessoa jur", a["rotulo"] + a["arquivo"], re.I) for a in achados)}


def lie_wayback() -> dict:
    """Cópias da Lei de Incentivo ao Esporte no Internet Archive: arquivos de dados e páginas de projetos."""
    cdx = ("https://web.archive.org/cdx/search/cdx?url=" + urllib.parse.quote("gov.br/esporte/pt-br/acoes-e-programas/lei-de-incentivo-ao-esporte") +
           "*&output=json&filter=statuscode:200&collapse=urlkey&limit=3000")
    cod, txt, _ = get(cdx, 90)
    out = {"cdx_http": cod, "capturas": 0, "arquivos": [], "baixados": []}
    if cod != 200 or not isinstance(txt, str):
        return out
    try:
        linhas = json.loads(txt)[1:]
    except ValueError:
        return out
    out["capturas"] = len(linhas)
    # colunas: urlkey, timestamp, original, mimetype, statuscode, digest, length
    arqs = [l for l in linhas if DADO.search(l[2]) or "pdf" in l[3] or re.search(r"projet|captad|aprovad|patrocin|incentivador|relat|resultado", l[2], re.I)]
    out["arquivos"] = [{"url": l[2], "quando": l[1], "tipo": l[3]} for l in arqs][:200]
    HIST.mkdir(parents=True, exist_ok=True)
    for l in [l for l in arqs if DADO.search(l[2]) or "spreadsheet" in l[3] or "excel" in l[3] or "csv" in l[3]][:25]:
        url = f"https://web.archive.org/web/{l[1]}id_/{l[2]}"
        c2, b, tp = get(url, 90, bruto=True)
        if c2 == 200 and isinstance(b, (bytes, bytearray)) and len(b) > 500:
            nome = re.sub(r"[^A-Za-z0-9._-]+", "_", l[2].split("/")[-1])[:80] or "arquivo"
            dest = HIST / f"lie_{l[1][:8]}_{nome}"
            dest.write_bytes(b)
            out["baixados"].append({"arquivo": str(dest.relative_to(RAIZ)), "de": l[2], "captura": l[1], "bytes": len(b)})
        time.sleep(1)
    return out


def lie_agora() -> dict:
    cod, html, _ = get("https://www.gov.br/esporte/pt-br/acoes-e-programas/lei-de-incentivo-ao-esporte")
    return {"http": cod, "restrito": isinstance(html, str) and "restrito" in html.lower()}


def receita_fundo() -> dict:
    """Todas as ligações das páginas de benefícios da Receita — e os diretórios de arquivos que elas citam."""
    alvos = ["https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/dados-abertos/beneficios-e-renuncias-fiscais",
             "https://www.gov.br/receitafederal/pt-br/assuntos/beneficios-fiscais",
             "https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/paineis/dashboards-das-atividades-de-beneficios-fiscais"]
    out = {}
    for u in alvos:
        cod, html, _ = get(u)
        if cod != 200 or not isinstance(html, str):
            out[u] = {"http": cod}; continue
        p = Links(); p.feed(html)
        ls = [(urljoin(u, h or ""), r) for h, r in p.l if h and not h.startswith("#")]
        uteis = [{"url": a, "rotulo": r} for a, r in ls if not re.search(r"/pt-br/(assuntos|acesso-a-informacao|servicos|canais|noticias|centrais)/?$|facebook|twitter|instagram|youtube|linkedin|flickr|soundcloud|whatsapp|#", a)]
        texto = re.sub(r"<[^>]+>", " ", html); texto = re.sub(r"\s+", " ", texto)
        i = texto.lower().find("benef")
        out[u] = {"http": cod, "links": uteis[:120], "trecho": texto[max(0, i - 200): i + 1500]}
        for a in [x["url"] for x in uteis if re.search(r"arquivos\.receitafederal|dados\.gov\.br|/dados/|\.zip|\.csv|\.xlsx|powerbi|app\.powerbi", x["url"])][:10]:
            c2, h2, tp = get(a)
            item = {"http": c2, "tipo": tp}
            if c2 == 200 and isinstance(h2, str) and "html" in tp:
                p2 = Links(); p2.feed(h2); item["links"] = [urljoin(a, h or "") for h, _ in p2.l][:80]
            out.setdefault("seguidos", {})[a] = item
    return out


def main() -> dict:
    SAIDA.mkdir(parents=True, exist_ok=True)
    import sys
    if "--receita" in sys.argv:
        r = json.loads((SAIDA / "sondagem_fontes.json").read_text(encoding="utf-8")) if (SAIDA / "sondagem_fontes.json").exists() else {}
        r["receita_fundo"] = receita_fundo(); r["em_receita_fundo"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        (SAIDA / "sondagem_fontes.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        print(json.dumps({k: (v.get("http"), len(v.get("links") or [])) for k, v in r["receita_fundo"].items() if k != "seguidos"}, ensure_ascii=False)); return r
    r = {"em": time.strftime("%Y-%m-%dT%H:%M:%S"), "receita": receita(), "lie_hoje": lie_agora(), "lie_internet_archive": lie_wayback()}
    (SAIDA / "sondagem_fontes.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"receita_arquivos": len(r["receita"]["arquivos_de_dados"]), "receita_por_cnpj": r["receita"]["tem_por_cnpj"],
                      "lie_hoje": r["lie_hoje"], "lie_capturas": r["lie_internet_archive"]["capturas"],
                      "lie_baixados": len(r["lie_internet_archive"]["baixados"])}, ensure_ascii=False))
    return r


if __name__ == "__main__":
    main()
