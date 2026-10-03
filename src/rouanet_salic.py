"""MOTOR 16 — LEI ROUANET (Mecanismo de Incentivo a Projetos Culturais) pelo SALIC (corrigido em 03/10/2026).

O que estava errado (teste dos motores de 03/10): o motor lia páginas institucionais do Ministério da Cultura
("Secretaria de Fomento", FAQ da PNAB) com o leitor genérico e contava a mesma página a cada leitura ("105 achados" que
eram 3 páginas). Não lia o SALIC nem a regra da janela de propostas.

O que a Lei Rouanet oferece a uma associação (verificado em 03/10/2026):
  · A JANELA DE PROPOSTAS: Instrução Normativa MinC nº 29, de 29/01/2026, art. 5º — "O período para apresentação de
    propostas culturais é de 1º de fevereiro a 31 de outubro de cada ano" (gov.br/cultura › legislação e normativas).
    Não é edital com seleção: é o prazo anual para cadastrar a proposta no SALIC; aprovada, a entidade capta com
    empresas e pessoas físicas (renúncia de imposto de renda).
  · O MAPA DE GOIÁS: os projetos de Goiás no SALIC (API pública api.salic.cultura.gov.br/api/v1/projetos, filtro UF e
    ano do projeto) — quem propõe, em que segmento, quanto foi aprovado e quanto foi captado. Serve de referência e de
    série histórica (3 anos), não é oportunidade.

Privacidade: só entram proponentes pessoa JURÍDICA (CNPJ de 14 dígitos); proponente pessoa física (CPF) e a ficha
técnica (nomes de pessoas) nunca são gravados. Conteúdo coletado é dado, nunca instrução.
"""
from __future__ import annotations

import json
import re
import time
import urllib.request
from datetime import date

from .nucleo import ROOT, load_json, now_iso, sha256, validate_public_https, write_json

MOTOR_ID = "plat-salic"
ESTADO = ROOT / "estado/salic_go.json"
ARQ = ROOT / "biblioteca_alexandria/base/historico_3_anos/salic"
API = "https://api.salic.cultura.gov.br/api/v1/projetos/?UF={uf}&ano_projeto={ano}&limit={lim}&offset={off}&format=json"
NORMA = {"ato": "Instrução Normativa MinC nº 29, de 29 de janeiro de 2026", "artigo": "art. 5º",
         "texto": "O período para apresentação de propostas culturais é de 1º de fevereiro a 31 de outubro de cada ano.",
         "url": "https://www.gov.br/cultura/pt-br/acesso-a-informacao/legislacao-e-normativas/instrucao-normativa-minc-no-29-de-29-de-janeiro-de-2026",
         "conferido_em": "2026-10-03"}
UA = "Mozilla/5.0 (X11; Linux x86_64) Eldorado-OSC/1.0"
CAMPOS = ("PRONAC", "nome", "situacao", "UF", "municipio", "segmento", "mecanisnmo", "enquadradmento", "ano_projeto",
          "data_inicio", "data_termino", "valor_solicitado", "valor_aprovado", "valor_captado", "proponente", "cgccpf")


def janela(hoje: date) -> dict:
    """A janela de propostas do ano: aberta (até 31/10) ou a próxima (1º/02)."""
    ini, fim = date(hoje.year, 2, 1), date(hoje.year, 10, 31)
    if hoje < ini:
        return {"aberta": False, "inicio": ini.isoformat(), "fim": fim.isoformat(), "dias_restantes": None}
    if hoje <= fim:
        return {"aberta": True, "inicio": ini.isoformat(), "fim": fim.isoformat(), "dias_restantes": (fim - hoje).days}
    return {"aberta": False, "inicio": date(hoje.year + 1, 2, 1).isoformat(), "fim": date(hoje.year + 1, 10, 31).isoformat(),
            "dias_restantes": None}


def registro_janela(hoje: date) -> dict:
    j = janela(hoje)
    ano = j["fim"][:4]
    return {"id": sha256(f"rouanet-janela-{ano}".encode())[:20], "status": "capturada",
            "titulo": f"Lei Rouanet — apresentação de propostas culturais no SALIC ({ano}): de 01/02 a 31/10",
            "url": NORMA["url"], "url_oficial": "https://salic.cultura.gov.br/", "fonte_id": MOTOR_ID,
            "fonte_nome": "SALIC — Lei Rouanet (Ministério da Cultura)", "orgao": "Ministério da Cultura — SEFIC",
            "territorio": "BR", "uf": None, "nivel": "federal", "tipo_fonte": "regra_oficial", "confianca": "primaria",
            "coletado_em": now_iso(), "data_publicacao": "2026-01-30", "inicio": j["inicio"], "fim": j["fim"],
            "prazo_texto": j["fim"], "regime": "incentivo_fiscal", "fluxo_continuo": False,
            "evidencia": f"{NORMA['ato']}, {NORMA['artigo']}: {NORMA['texto']}",
            "objeto": "Cadastro de proposta cultural no SALIC para captar recursos por renúncia fiscal (Lei 8.313/1991). "
                      "Associações sem fins lucrativos podem propor; aprovada a proposta, a captação é com empresas e pessoas físicas.",
            "hash_evidencia": sha256(NORMA["texto"].encode())}


def _get_json(url: str, timeout: int = 40) -> dict:
    validate_public_https(url)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read(20_000_000).decode("utf-8", "ignore"))


def _limpo(p: dict) -> dict | None:
    doc = re.sub(r"\D", "", str(p.get("cgccpf") or ""))
    if len(doc) != 14:                                   # pessoa física: fora (privacidade)
        return None
    r = {k: p.get(k) for k in CAMPOS}
    r["cgccpf"] = doc
    r["id"] = f"salic-{p.get('PRONAC')}"
    return r


def projetos(uf: str, ano: int, limite: int = 2000, pausa: float = 0.4) -> list[dict]:
    """Projetos do SALIC por UF e ano do projeto (2 dígitos na API), só proponente pessoa jurídica."""
    out, off, lim = [], 0, 100
    while off < limite:
        d = _get_json(API.format(uf=uf, ano=str(ano)[-2:], lim=lim, off=off))
        lote = ((d.get("_embedded") or {}).get("projetos")) or []
        out += [x for x in (_limpo(p) for p in lote) if x]
        if len(lote) < lim:
            break
        off += lim
        time.sleep(pausa)
    return out


def arquivar(regs: list[dict], ano: int) -> int:
    ARQ.mkdir(parents=True, exist_ok=True)
    p = ARQ / f"{ano}.jsonl"
    ja = set()
    if p.exists():
        ja = {json.loads(l)["id"] for l in p.read_text(encoding="utf-8").splitlines() if l.strip()}
    novos = 0
    with p.open("a", encoding="utf-8") as fh:
        for r in regs:
            if r["id"] not in ja:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n"); ja.add(r["id"]); novos += 1
    return novos


def ler_motor(sensor: dict | None = None, hoje: date | None = None, limites: dict | None = None) -> dict:
    """Mesma saída de `sensores.ler`: o achado é a JANELA de propostas (oportunidade anual); o mapa de Goiás vai ao estado."""
    hoje = hoje or date.today()
    est = load_json(ESTADO) if ESTADO.exists() else {}
    diag = {"paginas_lidas": 0, "links_total": 0, "links_candidatos": 0, "descobertas": [], "pdf_links": 0, "motivo_zero": None,
            "versao": "motor 16 Rouanet/SALIC v2 (03/10/2026)", "norma": NORMA, "janela": janela(hoje), "fontes": {}}
    falhas, saude = [], []
    # série de 3 anos + ano corrente, um ano por passagem depois de completa (o corrente sempre)
    feitos = set(str(a) for a in (est.get("anos_completos") or []))
    anos = [hoje.year] + [a for a in range(hoje.year - 1, hoje.year - 4, -1) if str(a) not in feitos][:1]
    for ano in anos:
        try:
            regs = projetos("GO", ano)
            novos = arquivar(regs, ano)
            diag["fontes"][str(ano)] = {"projetos_go": len(regs), "novos_no_arquivo": novos,
                                         "captado": round(sum(float(r.get("valor_captado") or 0) for r in regs), 2),
                                         "aprovado": round(sum(float(r.get("valor_aprovado") or 0) for r in regs), 2)}
            diag["paginas_lidas"] += 1 + len(regs) // 100
            saude.append({"url": API.format(uf="GO", ano=str(ano)[-2:], lim=100, off=0), "http": 200, "bytes": 0, "itens": len(regs)})
            if ano != hoje.year:
                feitos.add(str(ano))
        except Exception as e:  # noqa: BLE001
            falhas.append({"url": API.format(uf="GO", ano=str(ano)[-2:], lim=100, off=0), "erro": "salic_api", "code": getattr(e, "code", None),
                           "waf": None, "causa": f"{type(e).__name__}: {str(e)[:100]}"})
    est.update({"ultima": {"em": now_iso(), "data": hoje.isoformat(), "achados": 1 if diag["janela"]["aberta"] else 0,
                           "falhas": [f["causa"] for f in falhas], "janela": diag["janela"], "por_ano": diag["fontes"]},
                "anos_completos": sorted(feitos), "norma": NORMA})
    write_json(ESTADO, est)
    achados = [registro_janela(hoje)] if diag["janela"]["aberta"] else []
    if not achados:
        diag["motivo_zero"] = f"janela de propostas fechada; a próxima abre em {diag['janela']['inicio']} ({NORMA['ato']}, {NORMA['artigo']})"
    return {"sensor": MOTOR_ID, "achados": achados, "falhas": falhas, "saude": saude, "diagnostico": diag, "lido_em": now_iso()}
