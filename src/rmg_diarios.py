"""Malha metropolitana de Goiânia — diários oficiais município a município.

Modelo primário: seguir o dinheiro público na origem. Em município pequeno não
existe página de editais; o que existe é o **diário oficial**, onde o conselho
publica a resolução e a prefeitura publica o chamamento. Este módulo cobre os
21 municípios da Região Metropolitana pelo Querido Diário, com consultas
específicas para fundos e conselhos (CMDCA, CMAS, CMI).

O código IBGE de cada município **não é escrito de memória**: é resolvido em
execução no endpoint público de cidades do Querido Diário e cacheado em
`estado/territorios_rmg.json`. Município não resolvido vira pendência declarada
e continua coberto pelo PNCP e pela varredura do site, quando houver.

Sem IA e sem tokens.
"""
from __future__ import annotations

import json
import unicodedata
from datetime import date, timedelta
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .nucleo import (ROOT, append_jsonl, canonical_url, has_prompt_injection, load_json,
                     novo_id, now_iso, sha256, validate_public_https, write_json)

CACHE = ROOT / "estado/territorios_rmg.json"
SAIDA = ROOT / "dados/oportunidades/oportunidades.jsonl"

def _normalizar(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower().strip()

def _buscar(url: str, timeout: int = 25) -> dict:
    validate_public_https(url)
    req = Request(url, headers={"User-Agent": "Eldorado-OSC/3.0 contato-via-repositorio",
                                "Accept": "application/json"})
    with urlopen(req, timeout=timeout) as resposta:
        bruto = resposta.read(4_000_001)
    if len(bruto) > 4_000_000:
        raise ValueError("resposta excede limite")
    return json.loads(bruto.decode("utf-8", "replace"))

def resolver_territorios(cfg: dict, bases: list[str]) -> dict:
    """Resolve o código IBGE de cada município pelo nome, sem inventar valor."""
    cache = load_json(CACHE) if CACHE.exists() else {"municipios": {}, "atualizado_em": None}
    conhecidos = cache.get("municipios", {})
    pendentes = []
    for municipio in cfg["municipios"]:
        chave = f"{municipio['nome']}/{municipio['uf']}"
        if municipio.get("territory_id"):
            conhecidos[chave] = municipio["territory_id"]
        if conhecidos.get(chave):
            continue
        achou = None
        for base in bases:
            url = f"{base.rstrip('/')}/cities?" + urlencode({"city_name": municipio["nome"]})
            try:
                dados = _buscar(url)
            except (HTTPError, URLError, OSError, ValueError, json.JSONDecodeError):
                continue
            for cidade in dados.get("cities", []) or []:
                if (cidade.get("state_code") == municipio["uf"]
                        and _normalizar(cidade.get("territory_name", "")) == _normalizar(municipio["nome"])):
                    achou = cidade.get("territory_id")
                    break
            if achou:
                break
        if achou:
            conhecidos[chave] = achou
        else:
            pendentes.append(chave)
    cache = {"municipios": conhecidos, "pendentes": pendentes, "atualizado_em": now_iso(),
             "regra": "códigos resolvidos pelo endpoint público de cidades; nenhum código é escrito de memória"}
    write_json(CACHE, cache)
    return cache

def run(dias: int | None = None) -> dict:
    cfg = load_json(ROOT / "config/municipios_rmg.json")
    apis = load_json(ROOT / "config/coletores_api.json")["querido_diario"]
    if not apis.get("ativa"):
        return {"status": "querido_diario_inativo", "executado_em": now_iso()}
    bases = apis["bases"]
    cache = resolver_territorios(cfg, bases)
    resolvidos = cache["municipios"]

    fim = date.today()
    inicio = fim - timedelta(days=int(dias or apis.get("dias_incrementais", 5)))
    relatorio = {"executado_em": now_iso(), "municipios_configurados": len(cfg["municipios"]),
                 "municipios_resolvidos": len(resolvidos), "municipios_pendentes": cache.get("pendentes", []),
                 "consultas": 0, "novas": 0, "falhas": []}

    from .nucleo import carregar_oportunidades, gravar_oportunidades, merge_registro
    registros = carregar_oportunidades()
    novos = 0

    for municipio in cfg["municipios"]:
        chave = f"{municipio['nome']}/{municipio['uf']}"
        territorio_id = resolvidos.get(chave)
        if not territorio_id:
            continue
        for consulta in cfg["consultas_diario"]:
            relatorio["consultas"] += 1
            parametros = {"querystring": consulta, "territory_ids": territorio_id,
                          "published_since": inicio.isoformat(), "published_until": fim.isoformat(),
                          "size": min(int(apis.get("size", 50)), 50)}
            sucesso = False
            for base in bases:
                url = f"{base.rstrip('/')}/gazettes?" + urlencode(parametros)
                try:
                    dados = _buscar(url)
                except (HTTPError, URLError, OSError, ValueError, json.JSONDecodeError) as exc:
                    continue
                sucesso = True
                for gazeta in dados.get("gazettes", []) or []:
                    link = canonical_url(gazeta.get("txt_url") or gazeta.get("url") or "")
                    if not link.startswith("https://"):
                        continue
                    trecho = " ".join(gazeta.get("excerpts") or [])[:800]
                    if has_prompt_injection(trecho):
                        append_jsonl(ROOT / "estado/quarentena.jsonl",
                                     {"origem": "rmg_diarios", "municipio": chave, "url": link, "em": now_iso()})
                        continue
                    publicado = gazeta.get("date")
                    oid = novo_id(f"rmg|{link}|{publicado}|{consulta}")
                    registro = {
                        "id": oid, "status": "capturada",
                        "titulo": (f"Diário oficial de {municipio['nome']} — {publicado}: "
                                   f"{trecho[:180] or consulta}")[:300],
                        "url": link, "fonte_id": f"do-{_normalizar(municipio['nome']).replace(' ', '-')}",
                        "fonte_nome": f"Diário Oficial de {municipio['nome']} (GO)",
                        "territorio": f"GO/{municipio['nome']}", "uf": "GO",
                        "nivel": "municipal", "tipo_fonte": "diario_oficial_municipal",
                        "forma_divulgacao": "diario_oficial_municipio",
                        "confianca": "primaria", "coletado_em": now_iso(),
                        "data_publicacao": publicado,
                        "ano_referencia": int(str(publicado)[:4]) if publicado else None,
                        "prazo_texto": None, "consulta_origem": consulta,
                        "evidencia": trecho or consulta, "hash_evidencia": sha256((trecho or consulta).encode()),
                        "regiao_metropolitana": "Goiânia",
                    }
                    anterior = registros.get(oid)
                    registros[oid] = merge_registro(anterior, registro)
                    if anterior is None:
                        novos += 1
                break
            if not sucesso:
                relatorio["falhas"].append({"municipio": chave, "consulta": consulta[:40], "erro": "sem resposta das bases"})

    gravar_oportunidades(registros)
    relatorio["novas"] = novos
    write_json(ROOT / "estado/ultima_rmg.json", relatorio)
    append_jsonl(ROOT / "estado/auditoria.jsonl", {"evento": "rmg_diarios", **{k: v for k, v in relatorio.items() if k != "falhas"}})
    return relatorio

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
