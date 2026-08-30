"""Leitura indireta de redes sociais — sem acesso autenticado e sem raspagem.

Pergunta que este módulo responde: dá para saber que um órgão anunciou edital
num post sem entrar na rede social? Resposta honesta: **parcialmente, e sempre
como pista**. Existem quatro rotas legítimas, em ordem de confiabilidade:

1. **Espelho oficial no site do órgão** — muitos executivos publicam no portal
   de notícias o mesmo conteúdo do post. É a rota mais confiável e já está
   coberta pela varredura HTML; aqui ela é registrada como rota preferencial.
2. **Indexação por buscador** — posts públicos de perfis institucionais são
   indexados e aparecem em RSS de busca. Devolve título e trecho do post, não
   a imagem. É a rota ativa deste módulo.
3. **oEmbed público** — endpoint oficial de incorporação que devolve metadados
   de um post específico *cuja URL já se conhece*. Serve para enriquecer uma
   pista existente, não para descobrir posts novos. Preparado, desligado.
4. **API oficial com credencial** — Instagram Graph e YouTube Data. Única rota
   que lê a conta inteira de forma estável e legítima. Exige credencial e, no
   caso do Instagram, que a conta seja business/creator vinculada. Desligada
   até haver segredo configurado.

**Sobre "analisar a imagem postada":** o texto sobre a imagem (o card de edital)
só seria legível por OCR, e para rodar OCR é preciso primeiro obter o arquivo da
imagem — o que exige exatamente o acesso direto que não temos. Por isso o módulo
lê **texto de legenda e de indexação**, nunca pixels. Quando a rota 4 for
ativada, a imagem passa a estar disponível e o OCR se torna viável; o gancho
está declarado em `config/redes_indireta.json` → `ocr_quando_houver_credencial`.

Nada aqui confirma edital. Toda saída é pista e exige URL oficial por
`scripts/confirmar_pista.py`. Sem IA e sem tokens.
"""
from __future__ import annotations

import json
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

from .nucleo import (ROOT, append_jsonl, canonical_url, has_prompt_injection, load_json,
                     novo_id, now_iso, sha256, validate_public_https, write_json)

SAIDA = ROOT / "dados/oportunidades/pistas_sociais.jsonl"
TERMOS_EDITAL = re.compile(
    r"(edital|chamamento|chamada p[úu]blica|inscri[çc][õo]es|sele[çc][ãa]o p[úu]blica|"
    r"resolu[çc][ãa]o|termo de fomento|termo de colabora[çc][ãa]o|fundo municipal|"
    r"credenciament|premia[çc][ãa]o|fomento)", re.I)

def _carregar_pistas() -> dict:
    conhecidas = {}
    if SAIDA.exists():
        for linha in SAIDA.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                item = json.loads(linha)
                conhecidas[item["id"]] = item
    return conhecidas

def _consultar_rss(url: str, limite: int) -> list[tuple[str, str, str]]:
    validate_public_https(url, urlsplit(url).hostname)
    req = Request(url, headers={"User-Agent": "Eldorado-OSC/3.0 contato-via-repositorio"})
    with urlopen(req, timeout=25) as resposta:
        bruto = resposta.read(2_000_001)
    if len(bruto) > 2_000_000:
        raise ValueError("resposta excede limite")
    raiz = ET.fromstring(bruto)
    saida = []
    for node in raiz.findall(".//item")[:limite]:
        titulo = (node.findtext("title") or "").strip()
        link = canonical_url(node.findtext("link") or "")
        descricao = re.sub(r"<[^>]+>", " ", node.findtext("description") or "").strip()
        if titulo and link.startswith("https://"):
            saida.append((titulo, link, descricao))
    return saida

def run() -> dict:
    cfg = load_json(ROOT / "config/redes_indireta.json")
    relatorio = {"executado_em": now_iso(), "rota": "indexacao_de_buscador",
                 "consultas": 0, "pistas_novas": 0, "falhas": [],
                 "rotas_desligadas": [], "ocr": "indisponivel_sem_credencial"}
    if not cfg.get("ativa"):
        relatorio["status"] = "desativada"
        write_json(ROOT / "estado/ultima_redes_indireta.json", relatorio)
        return relatorio

    for nome, rota in cfg.get("rotas", {}).items():
        if not rota.get("ativa"):
            relatorio["rotas_desligadas"].append({"rota": nome, "motivo": rota.get("motivo")})

    conhecidas = _carregar_pistas()
    intervalo = float(cfg.get("intervalo_segundos", 1))
    limite_total = int(cfg.get("max_consultas_por_execucao", 30))
    limite_itens = int(cfg.get("max_itens_por_consulta", 10))
    motor = cfg["rotas"]["indexacao_buscador"]["motor"]

    perfis = [p for p in cfg["perfis_monitorados"] if p.get("ativa")]
    cursor_arquivo = ROOT / "estado/cursor_redes_indireta.json"
    cursor = load_json(cursor_arquivo).get("proxima", 0) if cursor_arquivo.exists() else 0

    combinacoes = [(p, t) for p in perfis for t in cfg["termos"]]
    if not combinacoes:
        relatorio["status"] = "sem_perfis_ativos"
        write_json(ROOT / "estado/ultima_redes_indireta.json", relatorio)
        return relatorio

    selecionadas = [combinacoes[(cursor + i) % len(combinacoes)]
                    for i in range(min(limite_total, len(combinacoes)))]

    for perfil, termo in selecionadas:
        relatorio["consultas"] += 1
        consulta = cfg["modelo_consulta"].format(dominio=perfil["dominio_rede"],
                                                 handle=perfil["handle"], termo=termo)
        url = motor.format(consulta=quote(consulta))
        try:
            resultados = _consultar_rss(url, limite_itens)
        except (HTTPError, URLError, OSError, ValueError, ET.ParseError) as exc:
            relatorio["falhas"].append({"perfil": perfil["id"], "erro": type(exc).__name__})
            time.sleep(intervalo)
            continue

        for titulo, link, descricao in resultados:
            texto = f"{titulo} {descricao}"
            if not TERMOS_EDITAL.search(texto):
                continue
            if urlsplit(link).hostname != perfil["dominio_rede"] and not (urlsplit(link).hostname or "").endswith("." + perfil["dominio_rede"]):
                continue
            if has_prompt_injection(texto):
                append_jsonl(ROOT / "estado/quarentena.jsonl",
                             {"origem": "redes_indireta", "perfil": perfil["id"], "url": link, "em": now_iso()})
                continue
            oid = novo_id("social|" + link)
            if oid in conhecidas:
                continue
            conhecidas[oid] = {
                "id": oid, "status": "pista_social_indireta",
                "titulo": titulo[:300], "url": link,
                "fonte_id": perfil["emissor_id"], "fonte_nome": perfil["nome"],
                "territorio": perfil.get("territorio") or "BR", "uf": perfil.get("uf"),
                "nivel": perfil.get("nivel"), "rede": perfil["rede"],
                "tipo_fonte": "rede_social_indireta", "forma_divulgacao": "rede_social_oficial",
                "confianca": "pista", "coletado_em": now_iso(),
                "evidencia": texto[:500], "hash_evidencia": sha256(texto.encode()),
                "consulta_origem": consulta,
                "identidade_oficial": perfil.get("evidencia_identidade"),
                "limitacao": ("texto de indexação pública; a imagem do post não é acessada e "
                              "seu conteúdo não é lido — pista exige confirmação em URL oficial"),
                "acao_requerida": "scripts/confirmar_pista.py",
            }
            relatorio["pistas_novas"] += 1
        time.sleep(intervalo)

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text("".join(json.dumps(x, ensure_ascii=False, separators=(",", ":")) + "\n"
                             for x in sorted(conhecidas.values(), key=lambda v: v["id"])), encoding="utf-8")
    write_json(cursor_arquivo, {"proxima": (cursor + len(selecionadas)) % len(combinacoes),
                                "total_combinacoes": len(combinacoes)})
    relatorio["pistas_acumuladas"] = len(conhecidas)
    write_json(ROOT / "estado/ultima_redes_indireta.json", relatorio)
    append_jsonl(ROOT / "estado/auditoria.jsonl", {"evento": "redes_indireta", **{k: v for k, v in relatorio.items() if k != "falhas"}})
    return relatorio

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
