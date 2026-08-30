"""Converte uma pista secundária (imprensa/diário/rede social) em oportunidade
primária, exigindo a URL oficial do edital. A pista nunca entra sozinha.

Uso:
  python scripts/confirmar_pista.py PISTA_ID https://dominio-oficial/pagina-do-edital --por "Nome"
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from urllib.parse import urlsplit
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.nucleo import (ROOT, append_jsonl, carregar_oportunidades, gravar_oportunidades,
                        load_json, merge_registro, novo_id, now_iso, sha256, validate_public_https)

def hosts_catalogados() -> set:
    hosts = set()
    cfg = load_json(ROOT / "config/fontes.json")
    for f in cfg["fontes"]:
        hosts.update(f.get("hosts_links") or [])
        if f.get("url"): hosts.add(urlsplit(f["url"]).hostname)
    for uf, url in load_json(ROOT / "config/portais_federativos.json")["estados"]:
        hosts.add(urlsplit(url).hostname)
    return {h for h in hosts if h}

def confirmar(pista_id: str, url_primaria: str, por: str) -> dict:
    validate_public_https(url_primaria)
    host = urlsplit(url_primaria).hostname or ""
    catalogo = hosts_catalogados()
    if not any(host == h or host.endswith("." + h) for h in catalogo):
        raise SystemExit(f"host {host} não está entre os domínios catalogados; adicione a fonte antes")
    pistas_path = ROOT / "dados/oportunidades/pistas_imprensa.jsonl"
    pista = None
    if pistas_path.exists():
        for linha in pistas_path.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                registro = json.loads(linha)
                if registro["id"] == pista_id: pista = registro; break
    if pista is None:
        raise SystemExit(f"pista {pista_id} não encontrada em pistas_imprensa.jsonl")
    registros = carregar_oportunidades()
    novo = {
        "id": novo_id(url_primaria), "status": "capturada",
        "titulo": pista.get("titulo", "")[:300], "url": url_primaria,
        "fonte_id": pista.get("fonte_id", "pista_confirmada"), "fonte_nome": pista.get("fonte_nome", "pista confirmada"),
        "territorio": pista.get("territorio", "BR"), "tipo_fonte": "pista_confirmada_manual",
        "confianca": "primaria", "coletado_em": now_iso(), "nivel": pista.get("nivel"),
        "uf": pista.get("uf"), "municipio": pista.get("municipio"), "areas_fonte": pista.get("areas_fonte") or [],
        "prazo_texto": pista.get("prazo_texto"), "ano_referencia": pista.get("ano_referencia"),
        "evidencia": pista.get("evidencia", "")[:500], "hash_evidencia": sha256(pista.get("evidencia", "").encode()),
        "pista_origem": pista_id, "verificado_por": por, "verificado_em": now_iso(),
    }
    registros[novo["id"]] = merge_registro(registros.get(novo["id"]), novo)
    gravar_oportunidades(registros)
    append_jsonl(ROOT / "estado/auditoria.jsonl", {"evento": "pista_confirmada", "pista": pista_id, "oportunidade": novo["id"], "por": por, "em": now_iso()})
    return novo

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("pista_id"); p.add_argument("url_primaria"); p.add_argument("--por", default="revisao_humana")
    a = p.parse_args()
    print(json.dumps(confirmar(a.pista_id, a.url_primaria, a.por), ensure_ascii=False, indent=2))
