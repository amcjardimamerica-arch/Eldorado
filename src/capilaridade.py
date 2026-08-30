"""Camada capilar e descentralizada de PISTAS SECUNDÁRIAS.

Busca menções a editais/chamamentos na imprensa e em anúncios de emissores
(via RSS de notícias), por termo, por emissor catalogado e por UF ativa.
Nada daqui entra na base primária: pistas ficam em arquivo separado e só se
tornam oportunidade quando a URL OFICIAL é confirmada
(`scripts/confirmar_pista.py` ou verificação assistida).

Redes sociais fechadas (Instagram/Facebook/X) não servem conteúdo a coletores
simples; a via preparada para elas é por credencial de API oficial
(config/capilaridade.json → redes_sociais, inativa até haver credencial).
"""
from __future__ import annotations

import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

from .nucleo import (ROOT, append_jsonl, canonical_url, load_json, now_iso,
                     sha256, slug, validate_public_https, write_json)

def _rss(url: str, timeout: int = 30):
    validate_public_https(url)
    req = Request(url, headers={"User-Agent": "Eldorado-OSC/3.0 contato-via-repositorio"})
    with urlopen(req, timeout=timeout) as resp:
        data = resp.read(2_000_001)
    if len(data) > 2_000_000: raise ValueError("resposta excede limite")
    return ET.fromstring(data)

def _consultas(cfg: dict, escopo: dict) -> list[tuple[str, str, str | None]]:
    """(id_consulta, texto, uf) — descentralizado: termos gerais × UFs ativas
    + termos específicos por emissor catalogado."""
    saida = []
    ufs = escopo.get("ufs_ativas") or []
    for termo in cfg.get("termos_gerais", []):
        for uf in ufs:
            saida.append((f"g-{slug(termo)}-{uf.lower()}", f'{termo} {uf}', uf))
    for emissor in cfg.get("emissores", []):
        if not emissor.get("ativa", True): continue
        for termo in emissor.get("termos") or cfg.get("termos_emissor_padrao", []):
            saida.append((f'e-{emissor["id"]}-{slug(termo)}', f'{emissor["nome"]} {termo}', emissor.get("uf")))
    limite = int(cfg.get("max_consultas_por_execucao", 40))
    if len(saida) <= limite:
        return saida
    # rotação persistente: cada execução cobre uma fatia; nenhum termo/UF fica para trás
    cursor_path = ROOT / "estado/cursor_capilaridade.json"
    inicio = int(load_json(cursor_path).get("proxima", 0)) % len(saida) if cursor_path.exists() else 0
    fatia = [saida[(inicio + i) % len(saida)] for i in range(limite)]
    write_json(cursor_path, {"proxima": (inicio + limite) % len(saida), "total": len(saida)})
    return fatia

def run() -> dict:
    cfg = load_json(ROOT / "config/capilaridade.json")
    if not cfg.get("ativa", True):
        return {"executado_em": now_iso(), "status": "desativada"}
    escopo = load_json(ROOT / "config/escopo.json")
    saida_path = ROOT / "dados/oportunidades/pistas_imprensa.jsonl"
    conhecidas = {}
    if saida_path.exists():
        for linha in saida_path.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                item = json.loads(linha); conhecidas[item["id"]] = item
    relatorio = {"executado_em": now_iso(), "consultas": 0, "consultas_com_falha": 0, "pistas_novas": 0}
    for cid, texto, uf in _consultas(cfg, escopo):
        relatorio["consultas"] += 1
        try:
            raiz = _rss(cfg["motor_rss"].format(consulta=quote(texto)))
            for node in raiz.findall(".//item")[: int(cfg.get("max_itens_por_consulta", 10))]:
                titulo = (node.findtext("title") or "").strip()
                link = canonical_url((node.findtext("link") or "").strip())
                if not titulo or not link.startswith("https://"): continue
                pid = sha256(("imprensa|" + link).encode())[:20]
                if pid in conhecidas: continue
                conhecidas[pid] = {
                    "id": pid, "status": "pista_imprensa", "confianca": "secundaria",
                    "titulo": titulo[:300], "url": link, "fonte_id": "imprensa-" + cid,
                    "fonte_nome": "Camada capilar de imprensa/anúncios", "uf": uf, "territorio": uf or "BR",
                    "consulta_origem": texto, "coletado_em": now_iso(),
                    "evidencia": titulo[:500], "hash_evidencia": sha256(titulo.encode()),
                    "regra": "não entra na base primária sem confirmação da URL oficial",
                }
                relatorio["pistas_novas"] += 1
            time.sleep(float(cfg.get("intervalo_segundos", 1)))
        except (HTTPError, URLError, OSError, ValueError, ET.ParseError):
            relatorio["consultas_com_falha"] += 1
    saida_path.parent.mkdir(parents=True, exist_ok=True)
    saida_path.write_text("".join(json.dumps(x, ensure_ascii=False, separators=(",", ":")) + "\n" for x in sorted(conhecidas.values(), key=lambda x: x["id"])), encoding="utf-8")
    write_json(ROOT / "estado/ultima_capilaridade.json", relatorio)
    append_jsonl(ROOT / "estado/auditoria.jsonl", {"evento": "capilaridade", **relatorio})
    return relatorio

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
