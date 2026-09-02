"""Extração do ato dentro da edição do diário.

A auditoria revelou o achado que muda o jogo: 7.084 editais do acervo apontam
para `data.queridodiario.ok.org.br/.../<hash>.pdf` — e isso **não é um
agregador**, é o **PDF da edição inteira do diário oficial**. O ato do edital
está lá dentro, com objeto, prazo, valor e requisitos. O sistema tinha o
documento na mão e só lia o título.

Este módulo abre a edição, localiza o TRECHO do ato (a matéria que casa o
léxico do terceiro setor) e extrai dele os 11 itens. Uma edição pode conter
vários atos; cada um vira um registro próprio com seu recorte.

Economia: o PDF é baixado uma vez por edição (cache por hash), o texto é
recortado por janela ao redor do casamento, e nada de IA — regex e léxico.
"""
from __future__ import annotations

import io
import json
import re
from datetime import date

from .lexico import casar
from .nucleo import ROOT, load_json, now_iso, sha256, validate_public_https, write_json

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover
    PdfReader = None

CACHE = ROOT / "estado/edicoes"
_MATERIA = re.compile(
    r"(?:EDITAL|CHAMAMENTO\s+P[ÚU]BLICO|CHAMADA\s+P[ÚU]BLICA|TERMO\s+DE\s+FOMENTO|"
    r"TERMO\s+DE\s+COLABORA[ÇC][ÃA]O|RESOLU[ÇC][ÃA]O|AVISO\s+DE\s+CHAMAMENTO|"
    r"EXTRATO\s+DE\s+TERMO)", re.I)
_OBJETO = re.compile(r"objeto[:\s][^.]{20,400}\.", re.I)
_FIM = re.compile(r"(?:at[ée]\s+(?:o\s+dia\s+)?|prazo\s+final[^.\d]{0,20}|encerra\w*[^.\d]{0,20}|"
                  r"inscri[çc][õo]es[^.\d]{0,40}?at[ée]\s+)(\d{1,2}/\d{1,2}/\d{4}|\d{1,2}\s+de\s+\w+\s+de\s+\d{4})", re.I)
_INI = re.compile(r"(?:a\s+partir\s+d[eo]\s+|abertura[^.\d]{0,20}|in[íi]cio[^.\d]{0,25})"
                  r"(\d{1,2}/\d{1,2}/\d{4})", re.I)
_VALOR = re.compile(r"R\$\s?\d[\d.]{2,12}(?:,\d{2})?")
_RESULT = re.compile(r"(?:resultado(?:\s+(?:preliminar|final))?|homologa\w*|classifica\w*\s+final)"
                     r"[^.\d]{0,40}(\d{1,2}/\d{1,2}/\d{4})", re.I)
_RECURSO = re.compile(r"recurs\w+[^.\d]{0,60}?(\d{1,2}/\d{1,2}/\d{4})", re.I)
_ANEXO = re.compile(r"\bANEXO\s+[IVX0-9]+", re.I)
_EXIG = re.compile(
    r"(estatuto\s+social|ata\s+de\s+(?:posse|elei[çc][ãa]o)|cart[ãa]o\s+cnpj|comprovante\s+de\s+inscri[çc][ãa]o|"
    r"certid[ãa]o\s+negativa[^.,;]{0,40}|crf/?fgts|certificado\s+de\s+regularidade\s+do\s+fgts|cndt|"
    r"balan[çc]o\s+patrimonial|plano\s+de\s+trabalho|planilha\s+or[çc]ament[áa]ria|"
    r"declara[çc][ãa]o[^.,;]{0,40}|inscri[çc][ãa]o\s+no\s+conselho|\bcebas\b|\bcneas\b|"
    r"dois\s+anos|tr[êe]s\s+anos|regularidade\s+fiscal)", re.I)


def baixar_edicao(url: str, timeout: int = 30, max_bytes: int = 25_000_000) -> bytes | None:
    """Baixa a edição uma vez; guarda em cache pelo hash da URL."""
    CACHE.mkdir(parents=True, exist_ok=True)
    alvo = CACHE / (sha256(url.encode())[:24] + ".pdf")
    if alvo.exists():
        return alvo.read_bytes()
    from urllib.request import Request, urlopen
    if not url.startswith("file://"):
        from urllib.parse import urlsplit
        validate_public_https(url, urlsplit(url).hostname)
    try:
        req = Request(url, headers={"User-Agent": "Eldorado-OSC/1.0 edicao"})
        with urlopen(req, timeout=timeout) as r:
            dados = r.read(max_bytes)
    except Exception:
        return None
    alvo.write_bytes(dados)
    return dados


def texto_da_edicao(dados: bytes) -> str | None:
    if PdfReader is None or not dados:
        return None
    try:
        leitor = PdfReader(io.BytesIO(dados))
        return re.sub(r"[ \t]+", " ",
                      "\n".join((p.extract_text() or "") for p in leitor.pages))
    except Exception:
        return None


def recortar_atos(texto: str, janela: int = 4000, maximo: int = 8) -> list[str]:
    """Trechos da edição que contêm matéria de interesse do terceiro setor."""
    if not texto:
        return []
    cortes, vistos = [], set()
    for m in _MATERIA.finditer(texto):
        ini = max(0, m.start() - 300)
        trecho = texto[ini: ini + janela]
        if not casar(trecho[:1200])["candidato"]:
            continue
        chave = sha256(trecho[:400].lower().encode())[:12]
        if chave in vistos:
            continue
        vistos.add(chave)
        cortes.append(trecho)
        if len(cortes) >= maximo:
            break
    return cortes


def extrair_itens(trecho: str) -> dict:
    """Os 11 itens a partir do texto do ato — só o que está escrito."""
    def um(rx):
        m = rx.search(trecho)
        return m.group(1).strip() if m else None
    exig = sorted({m.group(0).lower().strip() for m in _EXIG.finditer(trecho)})[:20]
    anexos = sorted({m.group(0).upper() for m in _ANEXO.finditer(trecho)})[:12]
    obj = _OBJETO.search(trecho)
    return {
        "objeto": re.sub(r"\s+", " ", obj.group(0))[:400] if obj else None,
        "inicio": um(_INI), "fim": um(_FIM),
        "resultado": um(_RESULT), "recurso": um(_RECURSO),
        "valores": sorted({m.group(0) for m in _VALOR.finditer(trecho)})[:5],
        "exigencias": exig, "anexos": anexos,
        "trecho_hash": sha256(trecho.encode()),
        "extraido_em": now_iso(),
    }


def processar(ficha: dict) -> dict:
    """Abre a edição do edital e devolve os itens obtidos, ou o motivo da falha."""
    url = ficha.get("url") or ""
    if not url.lower().endswith(".pdf"):
        return {"ok": False, "motivo": "url não é edição em PDF"}
    dados = baixar_edicao(url)
    if not dados:
        return {"ok": False, "motivo": "edição não pôde ser baixada (rede ou tamanho)"}
    texto = texto_da_edicao(dados)
    if not texto:
        return {"ok": False, "motivo": ("extrator PDF ausente" if PdfReader is None
                                        else "edição sem camada de texto (escaneada)")}
    atos = recortar_atos(texto)
    if not atos:
        return {"ok": False, "motivo": "edição sem matéria do terceiro setor no recorte",
                "paginas_texto": len(texto)}
    itens = [extrair_itens(a) for a in atos]
    melhor = max(itens, key=lambda i: sum(1 for v in i.values() if v))
    obtidos = sum(1 for k in ("objeto", "fim", "resultado", "recurso") if melhor.get(k)) \
        + bool(melhor["valores"]) + bool(melhor["exigencias"]) + bool(melhor["anexos"])
    return {"ok": True, "atos_no_documento": len(atos), "itens": melhor,
            "todos_os_atos": itens[:4], "itens_obtidos": obtidos,
            "bytes_edicao": len(dados)}





# ------------------------------------------------------- processamento em lote
def run(limite: int = 60, uf_primeiro: str = "GO", hoje=None) -> dict:
    """Abre as edições ainda não extraídas — uma por vez, Goiás primeiro.

    Cada edição processada enriquece a ficha no banco com os itens obtidos e
    registra o motivo quando não dá. Roda incremental: o cache evita rebaixar
    a mesma edição, e o marcador impede reprocessar o que já rendeu.
    """
    from .banco import conectar
    con = conectar()
    with con:
        con.execute("CREATE TABLE IF NOT EXISTS edicoes ("
                    "chave TEXT, ano TEXT, id TEXT, ok INTEGER, motivo TEXT, "
                    "itens_obtidos INTEGER, extraido_em TEXT, PRIMARY KEY (chave, ano, id))")
    linhas = con.execute(
        "SELECT h.chave, h.ano, h.id, h.ficha FROM historico h "
        "LEFT JOIN edicoes e ON e.chave=h.chave AND e.ano=h.ano AND e.id=h.id "
        "WHERE e.id IS NULL AND h.url LIKE '%.pdf' "
        "ORDER BY (h.uf=?) DESC, h.data_publicacao DESC LIMIT ?",
        (uf_primeiro, limite)).fetchall()
    ok = falha = 0
    ganho_total = 0
    motivos: dict[str, int] = {}
    with con:
        for chave, ano, cid, fj in linhas:          # ← sequencial, um por vez
            ficha = json.loads(fj)
            antes = sum(1 for k in ("objeto", "fim") if ficha.get(k))
            r = processar(ficha)
            if r["ok"]:
                it = r["itens"]
                ficha["extracao_edicao"] = {
                    "atos_no_documento": r["atos_no_documento"],
                    "itens_obtidos": r["itens_obtidos"], **it}
                # promove o que veio do ato, sem sobrescrever dado já confirmado
                for destino, valor in (("objeto", it["objeto"]), ("fim_texto", it["fim"]),
                                       ("inicio_texto", it["inicio"])):
                    if valor and not ficha.get(destino):
                        ficha[destino] = valor
                if it["exigencias"]:
                    ficha["exigencias_detectadas"] = sorted(
                        set(ficha.get("exigencias_detectadas") or []) | set(it["exigencias"]))[:30]
                if it["valores"] and not ficha.get("valores_citados"):
                    ficha["valores_citados"] = it["valores"]
                if it["anexos"]:
                    ficha["anexos_no_ato"] = it["anexos"]
                if it["resultado"] or it["recurso"]:
                    ficha["marcos"] = [m for m in (ficha.get("marcos") or [])] + [
                        x for x in ({"tipo": "resultado_preliminar", "data_texto": it["resultado"],
                                     "projetado": False} if it["resultado"] else None,
                                    {"tipo": "recurso", "data_texto": it["recurso"],
                                     "projetado": False} if it["recurso"] else None) if x]
                ganho_total += r["itens_obtidos"]
                ok += 1
            else:
                falha += 1
                motivos[r["motivo"]] = motivos.get(r["motivo"], 0) + 1
            con.execute("INSERT OR REPLACE INTO edicoes VALUES (?,?,?,?,?,?,?)",
                        (chave, ano, cid, int(r["ok"]), r.get("motivo"),
                         r.get("itens_obtidos", 0), now_iso()))
            con.execute("UPDATE historico SET ficha=? WHERE chave=? AND ano=? AND id=?",
                        (json.dumps(ficha, ensure_ascii=False), chave, ano, cid))
    pend = con.execute("SELECT COUNT(*) FROM historico h LEFT JOIN edicoes e "
                       "ON e.chave=h.chave AND e.ano=h.ano AND e.id=h.id "
                       "WHERE e.id IS NULL AND h.url LIKE '%.pdf'").fetchone()[0]
    con.close()
    return {"executado_em": now_iso(), "processadas": len(linhas), "com_ato": ok,
            "sem_ato": falha, "itens_ganhos": ganho_total,
            "motivos": motivos, "ainda_por_extrair": pend,
            "nota": ("edições do diário abertas uma por vez, Goiás primeiro; "
                     "cache por edição e marcador impedem retrabalho")}


if __name__ == "__main__":
    print(json.dumps(run(limite=200), ensure_ascii=False, indent=2))
