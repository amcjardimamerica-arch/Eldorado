"""Carga histórica única de cinco anos — FRACIONADA MÊS A MÊS, como pedido na
especificação: cada janela mensal é consumida uma única vez, com cursor
persistente e repetição automática apenas das janelas que falharam.

Camadas por janela: PNCP (API oficial) e Querido Diário (diários municipais).
Camada complementar anual: busca `site:domínio_oficial` por financiador
catalogado (config/retrospectivo.json). O marcador estado/bootstrap_cinco_anos.json
só é gravado quando TODAS as janelas foram consumidas com sucesso."""
from __future__ import annotations

import json
from datetime import date, datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

from .coletores_api import _salvar, coletar_pncp, coletar_querido_diario
from .nucleo import (ROOT, canonical_url, load_json, now_iso, novo_id, sha256, slug,
                     validate_public_https, write_json)

MARCADOR = ROOT / "estado/bootstrap_cinco_anos.json"
CURSOR = ROOT / "estado/cursor_carga_historica.json"

def host_allowed(url: str, domain: str) -> bool:
    host = urlsplit(url).hostname or ""
    return host == domain or host.endswith("." + domain)

def _janelas_mensais(anos: int) -> list[tuple[str, date, date]]:
    hoje = date.today()
    janelas = []
    ano, mes = hoje.year - anos, hoje.month
    while (ano, mes) <= (hoje.year, hoje.month):
        inicio = date(ano, mes, 1)
        fim = (date(ano + 1, 1, 1) if mes == 12 else date(ano, mes + 1, 1))
        fim = min(fim, hoje)
        janelas.append((f"{ano:04d}-{mes:02d}", inicio, fim))
        ano, mes = (ano + 1, 1) if mes == 12 else (ano, mes + 1)
    return janelas

def _dominios_por_ano(cfg: dict, existentes: dict, ano: int, limite_consultas: int) -> tuple[int, int]:
    """Camada complementar: RSS de busca restrito ao domínio oficial do financiador."""
    novas = erros = consultas = 0
    for financiador in cfg["financiadores"]:
        if not financiador.get("ativa") or not financiador.get("dominio_oficial"): continue
        nome, dominio = financiador["nome"], financiador["dominio_oficial"]
        for template in cfg["consultas_base"]:
            if consultas >= limite_consultas: return novas, erros
            consultas += 1
            consulta = template.format(nome=nome, ano=ano, dominio=dominio)
            url = cfg["motor"].format(consulta=quote(consulta))
            try:
                validate_public_https(url, urlsplit(url).hostname)
                req = Request(url, headers={"User-Agent": "Eldorado-OSC/3.0 contato-via-repositorio"})
                with urlopen(req, timeout=20) as resposta:
                    dados = resposta.read(2_000_001)
                if len(dados) > 2_000_000: raise ValueError("resposta excede limite")
                raiz = ET.fromstring(dados)
                for node in raiz.findall(".//item")[:10]:
                    titulo = (node.findtext("title") or "").strip()
                    link = canonical_url(node.findtext("link") or "")
                    if not titulo or urlsplit(link).scheme != "https" or not host_allowed(link, dominio): continue
                    oid = novo_id(link)
                    if oid in existentes: continue
                    existentes[oid] = {
                        "id": oid, "status": "descoberta_nao_verificada", "titulo": titulo[:300], "url": link,
                        "fonte_id": slug(nome), "fonte_nome": nome, "territorio": "BR",
                        "tipo_fonte": "busca_retroativa_dominio_catalogado", "confianca": "pista",
                        "coletado_em": now_iso(), "ano_pesquisado": ano, "dominio_autorizado": dominio,
                        "consulta_origem": consulta, "prazo_texto": None,
                        "evidencia": titulo[:500], "hash_evidencia": sha256(titulo.encode()),
                    }
                    novas += 1
            except (HTTPError, URLError, OSError, ValueError, ET.ParseError):
                erros += 1
    return novas, erros

def run() -> dict:
    if MARCADOR.exists():
        return {"status": "levantamento_inicial_ja_concluido", "executado_em": now_iso()}
    cfg = load_json(ROOT / "config/retrospectivo.json")
    escopo = load_json(ROOT / "config/escopo.json")
    janelas = _janelas_mensais(int(cfg.get("janela_anos", 5)))
    cursor = load_json(CURSOR) if CURSOR.exists() else {"concluidas": [], "falhas": {}}
    concluidas = set(cursor.get("concluidas", []))
    pendentes = [j for j in janelas if j[0] not in concluidas]
    limite = int(cfg.get("max_janelas_por_execucao", 12))
    relatorio = {"executado_em": now_iso(), "janelas_totais": len(janelas), "janelas_ja_concluidas": len(concluidas),
                 "janelas_nesta_execucao": 0, "novas": 0, "falhas": []}
    for rotulo, inicio, fim in pendentes[:limite]:
        relatorio["janelas_nesta_execucao"] += 1
        novos, falhas = [], []
        a, f = coletar_pncp(inicio, fim, escopo); novos += a; falhas += f
        a, f = coletar_querido_diario(inicio, fim, escopo); novos += a; falhas += f
        parcial = {"novas": 0}
        _salvar(novos, parcial)
        relatorio["novas"] += parcial["novas"]
        if falhas:
            cursor.setdefault("falhas", {})[rotulo] = falhas
            relatorio["falhas"].append({"janela": rotulo, "camadas": falhas})
        else:
            concluidas.add(rotulo)
            cursor.get("falhas", {}).pop(rotulo, None)
    # camada complementar por domínio oficial: um ano por execução, ciclando
    ano_atual = datetime.now(timezone.utc).year
    anos = list(range(ano_atual - int(cfg.get("janela_anos", 5)) + 1, ano_atual + 1))
    indice_ano = int(cursor.get("proximo_ano_dominios", 0)) % len(anos)
    from .nucleo import carregar_oportunidades, gravar_oportunidades
    existentes = carregar_oportunidades()
    novas_dom, erros_dom = _dominios_por_ano(cfg, existentes, anos[indice_ano], int(cfg.get("max_consultas_por_execucao", 60)))
    gravar_oportunidades(existentes)
    cursor["proximo_ano_dominios"] = indice_ano + 1
    relatorio["dominios_ano_pesquisado"] = anos[indice_ano]
    relatorio["dominios_novas"] = novas_dom
    relatorio["dominios_falhas"] = erros_dom
    relatorio["novas"] += novas_dom
    cursor["concluidas"] = sorted(concluidas)
    write_json(CURSOR, cursor)
    if len(concluidas) == len(janelas) and cursor.get("proximo_ano_dominios", 0) >= len(anos):
        write_json(MARCADOR, {"concluido_em": now_iso(), "janelas": len(janelas), "anos_dominios": len(anos)})
        relatorio["status"] = "levantamento_inicial_concluido"
    else:
        relatorio["status"] = "em_andamento"
        relatorio["janelas_restantes"] = len(janelas) - len(concluidas)
    write_json(ROOT / "estado/ultima_carga_historica.json", relatorio)
    return relatorio

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
