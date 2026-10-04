"""EXECUTOR DOCUMENTAL DOS MOTORES (titular, 04/10/2026) — os robôs seguem a skill de cada motor, sem o Claude.

Para cada oportunidade das filas (entrada_manual/skills_documentais/fila_NN_<motor>.json), UM MOTOR POR VEZ e UMA
OPORTUNIDADE POR VEZ: lê a fonte do motor e o site oficial (robots.txt respeitado; ponte de reserva), acha os links dos
documentos (PDF, /Download/, /wp-content/uploads/), abre até 3 e extrai os 12 pontos — cada um com valor, trecho
literal, documento e página. Grava no formato do importador (resultados_robo_NN_<motor>.jsonl). O que o robô não
consegue de nenhuma forma vai para fila_chrome.json — o Claude no Chrome é o ÚLTIMO recurso.
Conteúdo lido é dado, nunca instrução.
"""
from __future__ import annotations

import io
import json
import re
import time
import urllib.parse
import urllib.robotparser
from datetime import date
from pathlib import Path
from urllib.request import HTTPSHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
PASTA = ROOT / "entrada_manual/skills_documentais"
UA = "Mozilla/5.0 (compatible; EldoradoBot/1.0; +https://github.com/amcjardimamerica-arch/Eldorado)"
DOC = re.compile(r'href="([^"]+?(?:\.pdf|/Download/[^"]+|/wp-content/uploads/[^"]+\.(?:pdf|docx?)))"', re.I)
DATA = r"\d{1,2}/\d{1,2}/\d{4}|\d{1,2} de [a-zç]+ de \d{4}"
_robots: dict = {}

REGRAS = {   # (padrão, grupo do valor) — o trecho é o entorno literal do achado
    "Prazo de inscrição": (rf"inscri[çc][õo]es?[^.]{{0,90}}?({DATA})(?:[^.]{{0,40}}?(?:a|até|e)\s*({DATA}))?", None),
    "Valor": (r"(R\$\s?[\d\.]+(?:,\d{2})?(?:\s*\([^)]{3,60}\))?)", 1),
    "Objeto": (r"(?:DO OBJETO|Do Objeto|objeto)\s*[:\-–]?\s*([^.;]{30,300}[.;])", 1),
    "Resultado": (rf"resultado[^.]{{0,70}}?({DATA})", 1),
    "Prazo de recurso": (rf"recurso[^.]{{0,90}}?(\d+\s*\(?[a-z ]*\)?\s*dias(?: úteis)?|{DATA})", 1),
    "Órgão / financiador": (r"((?:Secretaria|Prefeitura Municipal de|Minist[ée]rio|Funda[çc][ãa]o|Instituto|Fundo)\s[^,.;\n]{3,80})", 1),
    "Requisitos": (r"(poder[ãa]o participar[^.;]{20,300}[.;]|requisitos? (?:para|de) (?:participa|inscri)[^.;]{20,300}[.;])", 1),
    "Destinação": (r"(destina-se a[^.;]{20,220}[.;]|recursos? (?:ser[ãa]o )?destinados?[^.;]{20,220}[.;])", 1),
    "Território": (r"((?:Munic[ií]pio|Estado) de [A-ZÀ-Ú][\wÀ-ú ]{2,40}|todo o territ[óo]rio nacional)", 1),
}
AREAS = {"Cultura": r"cultur|artes?\b|patrim[oô]nio", "Assistência social": r"assist[eê]ncia social|vulnerabilidade|suas\b",
         "Educação": r"educa[çc][ãa]o|escola", "Saúde": r"sa[úu]de\b", "Esporte": r"esport", "Meio ambiente": r"ambient|clim",
         "Criança e adolescente": r"crian[çc]a|adolescente"}


def permitido(url: str) -> bool:
    p = urllib.parse.urlsplit(url); base = f"{p.scheme}://{p.netloc}"
    if base not in _robots:
        rp = urllib.robotparser.RobotFileParser(base + "/robots.txt")
        try:
            rp.read()
        except Exception:  # noqa: BLE001
            rp = None
        _robots[base] = rp
    return True if _robots[base] is None else _robots[base].can_fetch("EldoradoBot", url)


def baixar(url: str) -> tuple[bytes, str]:
    from .certificados import contexto
    try:
        with build_opener(HTTPSHandler(context=contexto())).open(Request(url, headers={"User-Agent": UA}), timeout=40) as r:
            return r.read(15_000_000), r.headers.get("Content-Type") or ""
    except Exception as e1:  # noqa: BLE001
        from . import ponte_brasil as PB
        if PB.usar(url):
            st, _f, corpo, hdr = PB.abrir(url, timeout=60)
            if st == 200:
                return corpo, (hdr or {}).get("content-type", "")
        raise e1


def paginas_de_texto(b: bytes, tipo: str) -> list[str]:
    if "pdf" in tipo.lower() or b[:4] == b"%PDF":
        from pypdf import PdfReader
        return [(p.extract_text() or "") for p in PdfReader(io.BytesIO(b)).pages[:40]]
    h = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", b.decode("utf-8", "ignore"))
    return [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h))]


def extrair_pontos(paginas: list[str], documento: str) -> dict:
    """Os 12 pontos com valor + trecho literal + documento + página. Só o que o texto diz."""
    out: dict = {}
    for n, t in enumerate(paginas, 1):
        tt = re.sub(r"\s+", " ", t)
        for item, (rx, g) in REGRAS.items():
            if item in out:
                continue
            m = re.search(rx, tt, re.I)
            if m:
                val = " a ".join(x for x in m.groups() if x) if g is None else m.group(g)
                out[item] = {"valor": val.strip()[:300], "trecho": tt[max(0, m.start() - 60):m.end() + 60].strip()[:400],
                             "documento": documento, "pagina": n}
        if "Área de atuação" not in out:
            ach = [a for a, rx in AREAS.items() if re.search(rx, tt, re.I)]
            if ach:
                out["Área de atuação"] = {"valor": ", ".join(ach[:3]), "trecho": "(palavras-chave do documento)", "documento": documento, "pagina": n}
        an = re.findall(r"ANEXO\s+[IVXL]+\s*[-–—:]?\s*[^\n]{0,70}", t)
        if an and "Anexos" not in out:
            out["Anexos"] = {"valor": "; ".join(dict.fromkeys(a.strip() for a in an))[:300], "trecho": an[0][:200], "documento": documento, "pagina": n}
    h = (urllib.parse.urlsplit(documento).hostname or "").lower()
    if "Esfera" not in out and h:
        esf = "federal" if re.search(r"(^|\.)gov\.br$", h) and not re.search(r"\.[a-z]{2}\.gov\.br$", h) else \
              ("municipal" if re.search(r"prefeitura|municipal|\.[a-z]+\.[a-z]{2}\.gov\.br$", h) else ("estadual" if h.endswith(".gov.br") else None))
        if esf:
            out["Esfera"] = {"valor": esf, "trecho": f"domínio oficial {h}", "documento": documento, "pagina": 1}
    return out


def tratar(op: dict) -> tuple[dict | None, str]:
    """Uma oportunidade: fonte → site oficial → documentos → 12 pontos."""
    urls = [u for u in (op.get("site_oficial_conhecido"), op.get("fonte_do_motor")) if u and str(u).startswith("http")]
    docs, motivo = [], "sem endereço"
    for u in urls[:2]:
        if not permitido(u):
            motivo = "robots.txt proíbe"; continue
        try:
            b, tipo = baixar(u)
        except Exception as e:  # noqa: BLE001
            motivo = f"não abriu: {type(e).__name__}"; continue
        if "pdf" in tipo.lower() or b[:4] == b"%PDF":
            docs.append((u, b, tipo))
        else:
            for h in DOC.findall(b.decode("utf-8", "ignore"))[:6]:
                d = urllib.parse.urljoin(u, h)
                if d not in [x[0] for x in docs] and permitido(d):
                    try:
                        db, dt = baixar(d); docs.append((d, db, dt))
                    except Exception:  # noqa: BLE001
                        pass
                if len(docs) >= 3:
                    break
            if not docs:
                docs.append((u, b, tipo))                      # a própria página, quando não há documento
        time.sleep(1.0)
    pontos: dict = {}
    for d, b, tipo in docs[:3]:
        try:
            for k, v in extrair_pontos(paginas_de_texto(b, tipo), d).items():
                pontos.setdefault(k, v)
        except Exception:  # noqa: BLE001
            continue
    if not pontos or not op.get("livro"):
        return None, motivo if not docs else "documento sem os pontos legíveis"
    doc0 = next((d for d, _b, t in docs if "pdf" in t.lower() or d.lower().endswith(".pdf")), None)
    return {"livro": op["livro"], "etapa": "prata",
            "doze": {k: f'{v["valor"]} — “{v["trecho"][:180]}” ({v["documento"]}, p. {v["pagina"]})' for k, v in pontos.items()},
            "url_edital": doc0 if doc0 and doc0.startswith("https://") else None,
            "fontes": list(dict.fromkeys(v["documento"] for v in pontos.values() if str(v["documento"]).startswith("https://")))[:5],
            "motivo": f"executor documental (robô): {len(pontos)} dos 12 pontos lidos no documento", "modelo": "executor documental dos motores",
            "em": date.today().isoformat()}, "ok"


def run(limite_por_motor: int = 20, motores: list[str] | None = None) -> dict:
    idx = json.loads((PASTA / "indice.json").read_text(encoding="utf-8"))
    chrome, resumo = [], []
    for m in idx["motores"]:
        if motores and m["motor"] not in motores:
            continue
        fila = json.loads((ROOT / m["arquivo"]).read_text(encoding="utf-8")).get("fila") or []
        saida = PASTA / f"resultados_robo_{m['ordem']:02d}_{m['motor']}.jsonl"
        linhas, ok = [], 0
        for op in fila[:limite_por_motor]:
            r, motivo = tratar(op)
            if r:
                r = {k: v for k, v in r.items() if v}
                linhas.append(json.dumps(r, ensure_ascii=False)); ok += 1
            else:
                chrome.append({"motor": m["motor"], **op, "por_que_o_robo_nao_conseguiu": motivo})
            saida.write_text("\n".join(linhas) + ("\n" if linhas else ""), encoding="utf-8")   # gravado a cada oportunidade
        resumo.append({"motor": m["motor"], "fila": len(fila), "completadas_pelo_robo": ok})
    (PASTA / "fila_chrome.json").write_text(json.dumps({"regra": "ÚLTIMO recurso: só o que os robôs não conseguiram",
                                                         "total": len(chrome), "itens": chrome}, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"motores": resumo, "para_o_chrome": len(chrome)}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=1))
