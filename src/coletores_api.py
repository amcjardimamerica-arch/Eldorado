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

def _get_json_resiliente(url: str, tentativas: int = 1, esperas: list | None = None, timeout: int = 45) -> dict:
    """29/09/2026: nova tentativa com espera — o Querido Diário às vezes responde 'no available server' em TEXTO puro
    (só vira JSON depois de validado) e o PNCP oscila (Timeout/HTTPError). esperas: lista de segundos por tentativa;
    [a, b] com 2 números = intervalo aleatório entre a e b."""
    import random
    import time as _t
    ultimo = None
    for n in range(max(1, tentativas)):
        try:
            validate_public_https(url)
            req = Request(url, headers={"User-Agent": "Eldorado-OSC/3.0 contato-via-repositorio", "Accept": "application/json"})
            with urlopen(req, timeout=timeout) as resp:
                bruto = resp.read(8_000_001)
            if len(bruto) > 8_000_000:
                raise ValueError("resposta excede limite")
            texto = bruto.decode("utf-8", "replace").strip()
            if not texto.startswith(("{", "[")):
                raise ValueError(f"resposta não é JSON: {texto[:60]!r}")      # ex.: 'no available server'
            return json.loads(texto)
        except Exception as exc:
            ultimo = exc
            if n + 1 >= tentativas:
                break
            if esperas and len(esperas) == 2 and tentativas <= 3 and esperas[0] < esperas[1] <= 10:
                espera = random.uniform(esperas[0], esperas[1])
            else:
                espera = (esperas or [5])[min(n, len(esperas or [5]) - 1)]
            _t.sleep(espera)
    raise ultimo


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
                    corpo = _get_json_resiliente(f"{base}/v1/contratacoes/publicacao?{q}", int(cfg.get("tentativas", 1)),
                                                 cfg.get("esperas_s"), int(cfg.get("timeout_s", 45)))
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
                        # FINALIDADE DA PROPOSTA (24/09): léxico positivo primeiro, léxico de
                        # CONTROLE depois (destino a empresa), exceção para parceria MROSC explícita.
                        # No corpus de 768 publicações, só 24,6% serviam ao terceiro setor.
                        from .pncp_terceiro_setor import classificar as _finalidade
                        _f = _finalidade(objeto)
                        if not _f["terceiro_setor"]:
                            descartados.append({"objeto": objeto[:120],
                                                "motivo": f"{_f['passo']}: {_f['finalidade']}"})
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
                            "finalidade_pncp": _f["finalidade"], "pertinencia_pncp": _f["pertinencia"],
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
                    corpo = _get_json_resiliente(f"{base}/gazettes?{q}", int(cfg.get("tentativas", 1)),
                                                 cfg.get("espera_s"), int(cfg.get("timeout_s", 45)))
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

def coletar_comunica_pje(inicio: date, fim: date, cfg: dict | None = None) -> tuple[list[dict], list[dict]]:
    """COMUNICA PJe (CNJ) — rota do TJGO e do TRF1 (29/09/2026). Consulta por termos do léxico do terceiro setor; cada
    comunicação vira PISTA (regra 19 do AGENTS.md): só vira oportunidade com a URL oficial confirmada."""
    cfg = cfg or _cfg()["comunica_pje"]
    achados, falhas, vistos = [], [], set()
    for trib in cfg.get("tribunais", []):
        for termo in cfg.get("termos", []):
            for pagina in range(1, int(cfg.get("max_paginas", 3)) + 1):
                q = urlencode({"siglaTribunal": trib, "dataDisponibilizacaoInicio": inicio.isoformat(), "dataDisponibilizacaoFim": fim.isoformat(),
                               "itensPorPagina": int(cfg.get("itens_por_pagina", 100)), "pagina": pagina, "texto": termo})
                try:
                    corpo = _get_json_resiliente(f"{cfg['base']}?{q}", int(cfg.get("tentativas", 1)), cfg.get("esperas_s"), int(cfg.get("timeout_s", 60)))
                except (HTTPError, URLError, OSError, ValueError, json.JSONDecodeError) as exc:
                    falhas.append({"api": "comunica_pje", "tribunal": trib, "termo": termo, "erro": type(exc).__name__}); break
                itens = corpo.get("items") or corpo.get("itens") or corpo.get("content") or corpo.get("data") or [] if isinstance(corpo, dict) else corpo
                for it in itens or []:
                    ident = str(it.get("id") or it.get("hash") or it.get("numero_processo") or it.get("numeroProcesso") or "")
                    chave = f"{trib}|{ident}|{termo}"
                    if not ident or chave in vistos:
                        continue
                    vistos.add(chave)
                    orgao = it.get("nomeOrgao") or it.get("orgao") or trib
                    dia = str(it.get("data_disponibilizacao") or it.get("dataDisponibilizacao") or "")[:10]
                    texto = " ".join(str(it.get("texto") or "").split())[:600]
                    link = str(it.get("link") or "")
                    achados.append({"id": sha256(("pje|" + chave).encode())[:20], "status": "pista", "titulo": f"{trib} · {orgao} {dia} — {termo}"[:300],
                                    "url": link if link.startswith("https://") else f"https://comunica.pje.jus.br/consulta?siglaTribunal={trib}&texto={quote(termo)}",
                                    "fonte_id": f"comunica-pje-{trib.lower()}", "fonte_nome": f"Comunica PJe (CNJ) — {trib}", "territorio": "GO" if trib == "TJGO" else "BR",
                                    "tipo_fonte": "comunicacao_processual", "confianca": "pista", "confirmar_url_oficial": True,
                                    "data_publicacao": dia or None, "trecho": texto, "processo": it.get("numero_processo") or it.get("numeroProcesso")})
                if len(itens or []) < int(cfg.get("itens_por_pagina", 100)):
                    break
    return achados, falhas


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
    if (cfg.get("comunica_pje") or {}).get("ativa"):
        ini = hoje - timedelta(days=dias or int(cfg["comunica_pje"].get("dias_incrementais", 3)))
        a, f = coletar_comunica_pje(ini, hoje); novos += a; relatorio["falhas"] += f
    relatorio["itens"] = len(novos)
    _salvar(novos, relatorio)
    write_json(ROOT / "estado/ultima_coleta_api.json", relatorio)
    append_jsonl(ROOT / "estado/auditoria.jsonl", {"evento": "coleta_api", **{k: relatorio[k] for k in ("executado_em", "novas", "itens")}, "falhas": len(relatorio["falhas"])})
    return relatorio

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
