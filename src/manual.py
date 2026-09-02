"""Alimentação manual — o que o titular envia entra no sistema como fonte máxima.

Pasta de entrada: `entrada_manual/<id-da-fonte>/` — o titular arrasta ali o
edital e os documentos que buscou (PDF, DOCX, TXT, HTML). Também aceita
`entrada_manual/links.json` (links dos documentos por fonte, para o sistema
buscar atualizações e aprender onde procurar) e `config/motores_ativos.json`
(motores desativados pelo titular no painel).

Para cada arquivo:
  1. extrai o texto (PDF via pypdf; DOCX via zip/XML; TXT/HTML direto);
  2. cria/atualiza a pasta do edital na Biblioteca de Alexandria
     (`oportunidades/<chave>/<ano>/`): edital.txt, anexos preservados em PDF,
     ficha com origem 'alimentacao_manual';
  3. FASE 2 — extrai as 11 camadas do texto (mesmo extrator das edições do
     diário) e registra a confirmação documental;
  4. FASE 3 — emite o parecer determinístico e o conselho para a Biblioteca,
     abrindo caminho para Enquadrar.
Links aprendidos entram no regramento e nos sites da fonte. Nada é presumido:
o que o arquivo não traz fica declarado como lacuna.
"""
from __future__ import annotations

import io
import json
import re
import shutil
from datetime import date
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, sha256, slug, write_json

ENTRADA = ROOT / "entrada_manual"
OPORT = ROOT / "biblioteca_alexandria/oportunidades"
PROCESSADOS = ROOT / "estado/alimentacao_manual.json"


def _texto_de(arq: Path) -> str | None:
    ext = arq.suffix.lower()
    try:
        if ext == ".pdf":
            from pypdf import PdfReader
            return "\n".join((p.extract_text() or "") for p in PdfReader(str(arq)).pages)
        if ext == ".docx":
            import zipfile
            with zipfile.ZipFile(arq) as z:
                xml = z.read("word/document.xml").decode("utf-8", "replace")
            return re.sub(r"<[^>]+>", " ", xml)
        if ext in (".txt", ".md", ".csv", ".json"):
            return arq.read_text(encoding="utf-8", errors="ignore")
        if ext in (".html", ".htm"):
            h = arq.read_text(encoding="utf-8", errors="ignore")
            return re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", h, flags=re.S | re.I))
    except Exception:
        return None
    return None


def _fonte(fid: str) -> dict:
    cfg = ROOT / "config/fontes_captacao_260.json"
    if cfg.exists():
        for f in load_json(cfg).get("fontes", []):
            if f["id"] == fid:
                return f
    return {"id": fid, "programa": fid, "orgao": None, "nivel": None, "uf": None}


def _eh_modelo(nome: str) -> bool:
    return bool(re.search(r"anexo|modelo|formul|requerimento|declara|plano\s*de\s*trabalho|ficha|minuta", nome, re.I))


def processar_fonte(pasta: Path, hoje: date | None = None) -> dict:
    hoje = hoje or date.today()
    fid = pasta.name
    fonte = _fonte(fid)
    arquivos = sorted(p for p in pasta.iterdir() if p.is_file() and not p.name.startswith("."))
    if not arquivos:
        return {"fonte": fid, "arquivos": 0}
    from .edicao import extrair_itens
    from .confirmacao import conferir
    textos, modelos, principal = [], [], None
    for a in arquivos:
        t = _texto_de(a)
        if a.suffix.lower() == ".pdf" and _eh_modelo(a.name):
            modelos.append(a)
        if t and len(t) > 200 and (principal is None or len(t) > len(textos[-1][1] if textos else "")):
            principal = a
        if t:
            textos.append((a, t))
    texto = " ".join(t for _, t in textos) if textos else ""
    m = re.search(r"\b(?:edital|chamamento|chamada|sele[çc][ãa]o)\D{0,20}?(\d{1,4})\s*/\s*(20\d{2})", texto, re.I)
    ano = m.group(2) if m else str(hoje.year)
    chave = slug(f'{fid}-edital-{m.group(1)}' if m else f'{fid}-manual-{hoje.isoformat()}')[:80]
    destino = OPORT / chave / ano
    (destino / "anexos").mkdir(parents=True, exist_ok=True)
    if texto:
        (destino / "edital.txt").write_text(texto, encoding="utf-8")
    for mod in modelos:
        shutil.copyfile(mod, destino / "anexos" / mod.name)
    itens = extrair_itens(texto) if texto else {}
    ficha = {
        "id": f"manual-{sha256((fid + chave + ano).encode())[:12]}", "chave": chave, "ano": ano,
        "titulo": (re.search(r"(EDITAL[^\n]{5,140}|CHAMAMENTO[^\n]{5,140})", texto, re.I) or [None])[0]
                  or f'{fonte.get("programa")} — documento enviado em {hoje.isoformat()}',
        "url": None, "fonte_id": fid, "fonte_nome": fonte.get("orgao") or fonte.get("programa"),
        "financiador": fonte.get("orgao"), "territorio": fonte.get("uf") or "BR", "uf": fonte.get("uf"),
        "nivel": fonte.get("nivel"), "origem": "alimentacao_manual",
        "arquivos": [a.name for a in arquivos], "modelos": [m0.name for m0 in modelos],
        "objeto": itens.get("objeto"), "inicio": None, "fim": None,
        "prazo_texto": itens.get("fim"), "inicio_texto": itens.get("inicio"),
        "valores_citados": itens.get("valores") or [], "exigencias_detectadas": itens.get("exigencias") or [],
        "anexos_no_ato": itens.get("anexos") or [], "marcos": [
            x for x in ({"tipo": "resultado_preliminar", "data_texto": itens.get("resultado"), "projetado": False}
                        if itens.get("resultado") else None,
                        {"tipo": "recurso", "data_texto": itens.get("recurso"), "projetado": False}
                        if itens.get("recurso") else None) if x],
        "evidencia": texto[:1500], "hash_evidencia": sha256(texto.encode()) if texto else None,
        "destinacao": {"elegivel": True, "motivo": "enviado pelo titular como fonte de recurso para OSC"},
        "enviado_em": now_iso(),
        "verificacao": {"fonte": "titular", "conteudo": bool(texto),
                        "criterio": "documento integral enviado pelo titular (fonte máxima)"},
    }
    def _iso(br):
        m0 = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", (br or "").strip())
        if not m0:
            return None
        try:
            return date(int(m0.group(3)), int(m0.group(2)), int(m0.group(1))).isoformat()
        except ValueError:
            return None
    ficha["fim"] = _iso(itens.get("fim")); ficha["inicio"] = _iso(itens.get("inicio"))
    ficha["confirmacao"] = conferir(ficha)                 # FASE 2
    write_json(destino / "ficha.json", ficha)
    write_json(destino / "requisitos_condicoes_valores.json", {"itens": itens, "fase": 2})
    # FASE 3 — parecer e conselho
    fase3 = None
    try:
        from .farol_parecer import gerar
        fase3 = gerar(chave, ano)
    except Exception as exc:
        fase3 = {"erro": type(exc).__name__}
    # aprendizado: a fonte passa a ter documento conhecido
    return {"fonte": fid, "arquivos": len(arquivos), "modelos": len(modelos),
            "pasta": (str(destino.relative_to(ROOT)) if str(destino).startswith(str(ROOT)) else str(destino)),
            "chave": chave, "ano": ano,
            "fase2": ficha["confirmacao"]["nivel_confirmacao"],
            "camadas_ok": ficha["confirmacao"]["itens_ok"],
            "fase3": (fase3 or {}).get("recomendacao") or (fase3 or {}).get("erro")}


def aprender_links(hoje: date | None = None) -> dict:
    arq = ENTRADA / "links.json"
    if not arq.exists():
        return {"links": 0}
    dados = load_json(arq).get("links", {})
    cfg = ROOT / "config/fontes_captacao_260.json"
    n = 0
    if cfg.exists():
        c = load_json(cfg)
        for f in c.get("fontes", []):
            for u in dados.get(f["id"], []):
                if u not in f["sites"]:
                    f["sites"].insert(0, u); n += 1
                    f["confianca_site"] = "indicada_pelo_titular"
        write_json(cfg, c)
    return {"links": n}


def run(hoje: date | None = None) -> dict:
    hoje = hoje or date.today()
    est = load_json(PROCESSADOS) if PROCESSADOS.exists() else {"processados": {}}
    saida = []
    if ENTRADA.exists():
        for pasta in sorted(p for p in ENTRADA.iterdir() if p.is_dir()):
            marca = sha256("|".join(sorted(f"{p.name}:{p.stat().st_size}" for p in pasta.iterdir() if p.is_file())).encode())[:16]
            if est["processados"].get(pasta.name) == marca:
                continue
            r = processar_fonte(pasta, hoje)
            est["processados"][pasta.name] = marca
            saida.append(r)
    links = aprender_links(hoje)
    est["atualizado_em"] = now_iso()
    write_json(PROCESSADOS, est)
    return {"executado_em": now_iso(), "fontes_processadas": saida, "links_aprendidos": links["links"]}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
