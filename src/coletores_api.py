"""Coletores de APIs públicas oficiais (somente leitura, sem chave, sem IA):

- PNCP  (pncp.gov.br): editais de credenciamento/concurso publicados por todos
  os entes federativos — capilaridade nacional com uma única API.
- Querido Diário (Open Knowledge Brasil): busca textual nos diários oficiais
  municipais — captura chamamentos que nunca chegam a portais estruturados.

Ambos alimentam a MESMA base deduplicada, via merge que preserva revisão humana.
"""
from __future__ import annotations

import json
import time
from datetime import date, timedelta
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import Request, urlopen

from .nucleo import (ROOT, append_jsonl, carregar_oportunidades, gravar_oportunidades,
                     load_json, merge_registro, novo_id, now_iso, sha256,
                     validate_public_https, write_json)

import re

def _cfg():
    return load_json(ROOT / "config/coletores_api.json")

def _get_json(url: str, timeout: int = 45, max_bytes: int = 8_000_000):
    validate_public_https(url)
    req = Request(url, headers={"User-Agent": "Eldorado-OSC/3.0 contato-via-repositorio", "Accept": "application/json"})
    with urlopen(req, timeout=timeout) as resp:
        data = resp.read(max_bytes + 1)
        if len(data) > max_bytes: raise ValueError("resposta excede limite")
        return json.loads(data.decode("utf-8", "replace"))

def _salvar(novos: list[dict], relatorio: dict) -> None:
    if not novos: return
    registros = carregar_oportunidades()
    for item in novos:
        anterior = registros.get(item["id"])
        fundido = merge_registro(anterior, item)
        if anterior is None: relatorio["novas"] += 1
        registros[item["id"]] = fundido
    gravar_oportunidades(registros)

# ─── PNCP ────────────────────────────────────────────────────────────────────

def _pncp_url_publica(item: dict) -> str | None:
    link = (item.get("linkSistemaOrigem") or "").strip()
    if link.startswith("https://"):
        return link
    controle = item.get("numeroControlePNCP")  # ex.: 00000000000000-1-000001/2026
    if controle and "/" in controle:
        ident, ano = controle.split("/", 1)
        partes = ident.split("-")
        if len(partes) == 3:
            cnpj, _, sequencial = partes
            return f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{int(sequencial)}"
    return None

def coletar_pncp(inicio: date, fim: date, escopo: dict, cfg: dict | None = None) -> tuple[list[dict], list[dict]]:
    cfg = cfg or _cfg()["pncp"]
    filtro = re.compile(cfg["filtro_regex"], re.I)
    ufs = set(escopo.get("ufs_ativas") or [])
    achados, falhas, descartados = [], [], []
    for base in cfg["bases"]:
        try:
            for modalidade in cfg["modalidades"]:
                pagina = 1
                while pagina <= int(cfg.get("max_paginas", 5)):
                    q = urlencode({"dataInicial": inicio.strftime("%Y%m%d"), "dataFinal": fim.strftime("%Y%m%d"),
                                   "codigoModalidadeContratacao": modalidade, "pagina": pagina,
                                   "tamanhoPagina": int(cfg.get("tamanho_pagina", 50))})
                    corpo = _get_json(f"{base}/v1/contratacoes/publicacao?{q}")
                    dados = corpo.get("data") or corpo.get("resultado") or []
                    for item in dados:
                        objeto = (item.get("objetoCompra") or item.get("objeto") or "").strip()
                        uf = ((item.get("unidadeOrgao") or {}).get("ufSigla") or "").upper() or None
                        if not objeto or not filtro.search(objeto): continue
                        if uf and ufs and uf not in ufs: continue
                        # filtro da ETAPA 2 já na coleta: o PNCP publica muito
                        # certame comercial; o que uma OSC não pode concorrer
                        # não entra na base (economia e higiene do acervo)
                        from .destinacao import avaliar_destinacao
                        dest = avaliar_destinacao({"titulo": objeto, "evidencia": objeto,
                                                   "fonte_id": "pncp"})
                        if not dest["elegivel"]:
                            descartados.append({"objeto": objeto[:120],
                                                "motivo": dest["motivo"]})
                            continue
                        url = _pncp_url_publica(item)
                        if not url: continue
                        orgao = ((item.get("orgaoEntidade") or {}).get("razaoSocial") or "órgão público").strip()
                        municipio = ((item.get("unidadeOrgao") or {}).get("municipioNome") or None)
                        publicado = (item.get("dataPublicacaoPncp") or "")[:10] or None
                        achados.append({
                            "id": novo_id(url), "status": "capturada", "titulo": objeto[:300], "url": url,
                            "fonte_id": "pncp", "fonte_nome": f"PNCP — {orgao}"[:120], "territorio": uf or "BR",
                            "tipo_fonte": "api_oficial_pncp", "confianca": "primaria", "coletado_em": now_iso(),
                            "nivel": "municipal" if municipio else "federal", "uf": uf,
                            "municipio": f"{uf}/{municipio}" if uf and municipio else None,
                            "areas_fonte": [], "prazo_texto": None,
                            "ano_referencia": int(publicado[:4]) if publicado else None,
                            "data_publicacao": publicado,
                            "evidencia": objeto[:500], "hash_evidencia": sha256(objeto.encode()),
                            "modalidade_pncp": modalidade,
                            "destinacao": dest,
                        })
                    total_paginas = int(corpo.get("totalPaginas") or 1)
                    if pagina >= total_paginas: break
                    pagina += 1
                    time.sleep(0.5)
            if descartados:
                falhas.append({"api": "pncp", "descartados_fase2": len(descartados),
                               "amostra": descartados[:5],
                               "nota": "fora do escopo do terceiro setor"})
            return achados, falhas
        except (HTTPError, URLError, OSError, ValueError, json.JSONDecodeError) as exc:
            falhas.append({"api": "pncp", "base": base, "erro": type(exc).__name__})
    return achados, falhas

# ─── Querido Diário ─────────────────────────────────────────────────────────

def coletar_querido_diario(inicio: date, fim: date, escopo: dict, cfg: dict | None = None) -> tuple[list[dict], list[dict]]:
    cfg = cfg or _cfg()["querido_diario"]
    ufs = set(escopo.get("ufs_ativas") or [])
    achados, falhas = [], []
    for base in cfg["bases"]:
        try:
            for consulta in cfg["consultas"]:
                offset = 0
                for _ in range(int(cfg.get("max_paginas", 4))):
                    q = urlencode({"querystring": consulta, "published_since": inicio.isoformat(),
                                   "published_until": fim.isoformat(), "size": int(cfg.get("size", 50)),
                                   "offset": offset, "excerpt_size": 400, "number_of_excerpts": 1})
                    corpo = _get_json(f"{base}/gazettes?{q}")
                    diarios = corpo.get("gazettes") or []
                    for g in diarios:
                        uf = (g.get("state_code") or "").upper() or None
                        if uf and ufs and uf not in ufs: continue
                        url = (g.get("url") or g.get("txt_url") or "").strip()
                        if not url.startswith("https://"): continue
                        nome = g.get("territory_name") or "município"
                        dia = (g.get("date") or "")[:10]
                        trecho = " ".join((g.get("excerpts") or [""])[0].split())
                        titulo = f"Diário Oficial de {nome} ({uf}) {dia} — {consulta}"
                        achados.append({
                            "id": sha256(("qd|" + url + "|" + dia).encode())[:20], "status": "capturada", "titulo": titulo[:300], "url": url,
                            "fonte_id": "querido-diario", "fonte_nome": "Querido Diário — diários oficiais municipais",
                            "territorio": uf or "BR", "tipo_fonte": "diario_oficial_municipal", "confianca": "primaria",
                            "coletado_em": now_iso(), "nivel": "municipal", "uf": uf,
                            "municipio": f"{uf}/{nome}" if uf else None, "areas_fonte": [],
                            "prazo_texto": None, "ano_referencia": int(dia[:4]) if dia else None,
                            "data_publicacao": dia or None,
                            "evidencia": (trecho or titulo)[:500], "hash_evidencia": sha256((trecho or titulo).encode()),
                        })
                    total = int(corpo.get("total_gazettes") or 0)
                    offset += int(cfg.get("size", 50))
                    if offset >= total: break
                    time.sleep(0.5)
            return achados, falhas
        except (HTTPError, URLError, OSError, ValueError, json.JSONDecodeError) as exc:
            falhas.append({"api": "querido_diario", "base": base, "erro": type(exc).__name__})
    return achados, falhas

# ─── Execução incremental (diária/segunda-quarta) ───────────────────────────

def run(dias: int | None = None) -> dict:
    cfg = _cfg(); escopo = load_json(ROOT / "config/escopo.json")
    hoje = date.today()
    relatorio = {"executado_em": now_iso(), "novas": 0, "itens": 0, "falhas": []}
    novos: list[dict] = []
    if cfg["pncp"].get("ativa"):
        ini = hoje - timedelta(days=dias or int(cfg["pncp"].get("dias_incrementais", 5)))
        a, f = coletar_pncp(ini, hoje, escopo); novos += a; relatorio["falhas"] += f
    if cfg["querido_diario"].get("ativa"):
        ini = hoje - timedelta(days=dias or int(cfg["querido_diario"].get("dias_incrementais", 5)))
        a, f = coletar_querido_diario(ini, hoje, escopo); novos += a; relatorio["falhas"] += f
    relatorio["itens"] = len(novos)
    _salvar(novos, relatorio)
    write_json(ROOT / "estado/ultima_coleta_api.json", relatorio)
    append_jsonl(ROOT / "estado/auditoria.jsonl", {"evento": "coleta_api", **{k: relatorio[k] for k in ("executado_em", "novas", "itens")}, "falhas": len(relatorio["falhas"])})
    return relatorio

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
