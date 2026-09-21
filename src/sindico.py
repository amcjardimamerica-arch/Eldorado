"""O SÍNDICO — curador da Biblioteca de Alexandria, rodando no GitHub Actions.

Duas funções neste módulo:

  benchmark ..... roda cada modelo candidato, UM POR VEZ, contra o GABARITO (os 531 editais
                  validados pelo titular em 09/09 e 15/09) e mede: acerto na classificação,
                  prazos inventados (eliminatório), tokens/s, memória. Grava
                  estado/sindico/benchmark.json e fixa o vencedor em config/sindico.json.

  ciclo ......... o dia a dia: (1) ENTENDER — lê a Biblioteca inteira (editais, leis, fontes,
                  empresas, rotas) e mantém um catálogo compacto do que sabe; (2) CURAR —
                  classifica, extrai com trecho literal, marca duplicatas; (3) AFIAR — orienta
                  os motores (URL, termo, cadência) e expande rotas a partir de cada validado;
                  (4) MINERAR — quando não há trabalho pendente, gera um PROMPT DIFERENTE de
                  busca (empresas de Lucro Real em Goiás, patrocinadores de eventos, destinação
                  de incentivo fiscal) e registra o resultado da forma mais curta possível, mesmo
                  quando negativo, para não repetir o caminho; (5) ANUNCIAR — relatório do dia.

Regra que nunca muda: o síndico PROPÕE, a validação determinística DECIDE. Prazo, valor,
objeto e página só entram com trecho literal presente no texto. Tudo leva origem=sindico.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json
from .ia_local import IALocal, t_classificar_objeto, t_extrair_objeto_prazo, t_propor_lexico, t_diagnosticar_rota, t_catalogar_achado, _trecho_existe, _norm

CFG_P = ROOT / "config/sindico.json"
PASTA = ROOT / "estado/sindico"
PASTA.mkdir(parents=True, exist_ok=True)

CANDIDATOS = [
    {"id": "qwen2.5-3b", "nome": "Qwen2.5-3B-Instruct", "arquivo": "qwen2.5-3b-instruct-q4_k_m.gguf", "gb": 2.0, "licenca": "Apache-2.0",
     "url": "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf"},
    {"id": "qwen2.5-7b", "nome": "Qwen2.5-7B-Instruct", "arquivo": "qwen2.5-7b-instruct-q4_k_m.gguf", "gb": 4.7, "licenca": "Apache-2.0",
     "url": "https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/resolve/main/qwen2.5-7b-instruct-q4_k_m.gguf"},
    {"id": "gemma-2-2b", "nome": "Gemma-2-2B-it", "arquivo": "gemma-2-2b-it-Q4_K_M.gguf", "gb": 1.6, "licenca": "Gemma",
     "url": "https://huggingface.co/bartowski/gemma-2-2b-it-GGUF/resolve/main/gemma-2-2b-it-Q4_K_M.gguf"},
    {"id": "llama-3.2-3b", "nome": "Llama-3.2-3B-Instruct", "arquivo": "Llama-3.2-3B-Instruct-Q4_K_M.gguf", "gb": 2.0, "licenca": "Llama-3.2-Community",
     "url": "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf"},
]
MAPA_VEREDITO = {"fomento_osc": "aprovado", "atencao": "atencao"}      # famílias de inconformidade → reprovado


def cfg() -> dict:
    return load_json(CFG_P) if CFG_P.exists() else {"modelo_vencedor": None, "orcamento": {"minutos_por_ciclo": 300, "registros_por_ciclo": 150}}


# ─────────────────────────────────────────────────────────────── gabarito
def gabarito(limite: int | None = None) -> list[dict]:
    """Os editais validados pelo titular, com o texto disponível, em ordem estável."""
    from .fonte_edital import EXTRAIDOS
    import gzip
    itens = {}
    for arq in ("docs/dados/verificacao_467_2026-09-09.json", "docs/dados/verificacao_63_2026-09-15.json"):
        p = ROOT / arq
        if p.exists():
            for k, v in (load_json(p).get("itens") or {}).items():
                if v.get("veredito") in ("aprovado", "atencao", "reprovado"):
                    itens[k] = v
    out = []
    for eid, v in sorted(itens.items()):
        tx = ROOT / "dados/editais/textos" / f"{eid}.txt.gz"
        texto = gzip.open(tx, "rt", encoding="utf-8").read()[:5000] if tx.exists() else ""
        objeto = v.get("objeto") or ""
        if len(texto) < 60 and len(objeto) < 40:
            continue
        out.append({"id": eid, "titulo": objeto[:160] or (v.get("edital") or eid), "texto": texto or objeto,
                    "veredito": v["veredito"], "fim": v.get("fim"), "familia": v.get("familia")})
    return out[:limite] if limite else out


def _servidor(modelo: Path, porta: int = 8081) -> subprocess.Popen | None:
    motor = os.environ.get("LLAMA_SERVER") or str(ROOT / "ia_local/motor/llama-server")
    if not Path(motor).exists():
        return None
    env = dict(os.environ, LD_LIBRARY_PATH=str(Path(motor).parent))
    p = subprocess.Popen([motor, "-m", str(modelo), "--port", str(porta), "--host", "127.0.0.1", "-c", "4096", "--jinja", "-t", str(os.cpu_count() or 4)],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
    for _ in range(120):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{porta}/health", timeout=2) as r:
                if r.status == 200:
                    return p
        except Exception:
            time.sleep(1)
    p.kill(); return None


def avaliar_modelo(cand: dict, itens: list[dict], porta: int = 8081) -> dict:
    """Um modelo, todo o gabarito. Eliminatório: qualquer prazo inventado."""
    modelo = ROOT / "ia_local/modelos" / cand["arquivo"]
    if not modelo.exists():
        return {**cand, "erro": "modelo não disponível no runner", "elegivel": False}
    t0 = time.time(); srv = _servidor(modelo, porta)
    if not srv:
        return {**cand, "erro": "servidor não subiu", "elegivel": False}
    ia = IALocal(porta=porta, timeout=60)
    acertos = total = prazos_ok = prazos_inventados = tokens = 0
    confusao: dict = {}
    t_inf = 0.0
    try:
        for it in itens:
            t1 = time.time()
            p = t_classificar_objeto(ia, {"id": it["id"], "titulo": it["titulo"]}, it["texto"])
            t_inf += time.time() - t1
            if p:
                pred = MAPA_VEREDITO.get(p["familia"], "reprovado")
                esperado = it["veredito"]
                total += 1
                if pred == esperado or (esperado == "atencao" and pred == "aprovado"):
                    acertos += 1
                confusao[f"{esperado}->{pred}"] = confusao.get(f"{esperado}->{pred}", 0) + 1
                tokens += 120
            if it.get("fim") and len(it["texto"]) > 200:
                t1 = time.time()
                q = t_extrair_objeto_prazo(ia, {"id": it["id"]}, it["texto"])
                t_inf += time.time() - t1; tokens += 160
                if q and q.get("fim"):
                    if q["fim"] == it["fim"]:
                        prazos_ok += 1
                    elif not _trecho_existe((q.get("trechos") or {}).get("prazo"), it["texto"]):
                        prazos_inventados += 1                      # data sem trecho: INVENTADA
    finally:
        srv.kill()
    dur = time.time() - t0
    return {**cand, "itens": total, "acerto": round(acertos / total, 3) if total else 0, "confusao": confusao,
            "prazos_confirmados": prazos_ok, "prazos_inventados": prazos_inventados,
            "tokens_por_s": round(tokens / t_inf, 1) if t_inf else None, "minutos": round(dur / 60, 1),
            "elegivel": prazos_inventados == 0 and total > 0}


def benchmark(limite: int | None = None) -> dict:
    itens = gabarito(limite)
    res = {"em": now_iso(), "gabarito": len(itens), "runner": {"cpus": os.cpu_count(), "publico": True},
           "regra": "acerto na classificação contra o veredito do titular; QUALQUER prazo inventado (data sem trecho literal) elimina; desempate por tokens/s",
           "candidatos": []}
    for c in CANDIDATOS:
        r = avaliar_modelo(c, itens); res["candidatos"].append(r)
        write_json(PASTA / "benchmark.json", res)                    # parcial a cada modelo
    eleg = [c for c in res["candidatos"] if c.get("elegivel")]
    eleg.sort(key=lambda c: (-c["acerto"], -(c.get("tokens_por_s") or 0)))
    res["vencedor"] = eleg[0]["id"] if eleg else None
    res["motivo"] = (f"{eleg[0]['nome']}: acerto {eleg[0]['acerto']}, 0 prazos inventados, {eleg[0].get('tokens_por_s')} tok/s"
                     if eleg else "nenhum candidato elegível (todos inventaram prazo ou não subiram)")
    write_json(PASTA / "benchmark.json", res)
    if eleg:
        c = cfg(); c.update({"modelo_vencedor": eleg[0]["id"], "arquivo": eleg[0]["arquivo"], "url": eleg[0]["url"], "eleito_em": now_iso(), "benchmark": res["motivo"]})
        write_json(CFG_P, c)
    return {k: v for k, v in res.items() if k != "candidatos"} | {"resumo": [{k: c.get(k) for k in ("id", "acerto", "prazos_inventados", "tokens_por_s", "minutos", "elegivel", "erro")} for c in res["candidatos"]]}


# ─────────────────────────────────────────────────────────────── entender
def entender() -> dict:
    """Catálogo compacto do que a Biblioteca contém — o síndico só orienta o que conhece."""
    from collections import Counter
    dados = load_json(ROOT / "docs/dashboard-dados.json")
    an = load_json(ROOT / "dados/editais/analises.json") if (ROOT / "dados/editais/analises.json").exists() else {}
    cat = load_json(ROOT / "config/fontes_captacao_260.json").get("fontes", [])
    leis = load_json(ROOT / "biblioteca/leis/catalogo.json").get("itens", []) if (ROOT / "biblioteca/leis/catalogo.json").exists() else []
    rotas = load_json(ROOT / "config/rotas_motores.json").get("motores", {}) if (ROOT / "config/rotas_motores.json").exists() else {}
    emp = load_json(ROOT / "config/rotas_empresas.json") if (ROOT / "config/rotas_empresas.json").exists() else {}
    eds = dados.get("editais") or []
    ent = {"em": now_iso(),
           "editais": {"total": len(eds), "por_tipo": dict(Counter(e.get("tipo_registro") for e in eds).most_common()),
                       "por_uf": dict(Counter(e.get("uf") or "BR" for e in eds).most_common(10)), "por_area": dict(Counter(e.get("area") for e in eds).most_common(8))},
           "analises": {"total": len(an), "por_selo": dict(Counter(v.get("selo") for v in an.values()))},
           "fontes": {"total": len(cat), "por_nivel": dict(Counter(f.get("nivel") for f in cat)), "goias": sum(1 for f in cat if f.get("uf") == "GO")},
           "leis": {"total": len(leis), "titulos": [l.get("titulo", "")[:60] for l in leis[:30]]},
           "motores": {"total": len(rotas), "rotas": sum(len(m.get("rotas") or []) for m in rotas.values())},
           "empresas": {"total": emp.get("total_empresas"), "rotas": sum(len(r.get("rotas") or []) for r in emp.get("empresas") or [])},
           "acervo_compacto": load_json(ROOT / "estado/acervo_compacto.json") if (ROOT / "estado/acervo_compacto.json").exists() else None}
    write_json(PASTA / "catalogo_entendimento.json", ent)
    return ent


# ─────────────────────────────────────────────────────────────── minerar
PROMPTS_MINERACAO = [
    ("empresas_lucro_real_go", "Liste empresas de Goiás com regime de LUCRO REAL (grandes contribuintes de ICMS, capital acima de R$ 50 mi) que têm instituto, fundação ou programa de investimento social, e onde cada uma publica editais ou seleciona projetos. Responda em JSON: [{\"empresa\":..., \"pista\":..., \"onde_procurar\": url ou termo de busca}]"),
    ("patrocinadores_eventos_go", "Que empresas costumam patrocinar eventos culturais, esportivos e educacionais em Goiânia e Goiás (festivais, corridas, feiras, festas de bairro)? Para cada uma, onde a decisão de patrocínio é anunciada (site, imprensa, edital). JSON: [{\"empresa\":..., \"tipo_evento\":..., \"onde_procurar\":...}]"),
    ("incentivo_fiscal_destinacao", "Que mecanismos de renúncia fiscal (Lei Rouanet, FIA, Fundo do Idoso, Lei do Esporte, PRONAS/PRONON, ICMS estadual de Goiás) têm editais ou chamadas de empresas para escolher projetos? Onde essas chamadas são publicadas? JSON: [{\"mecanismo\":..., \"quem_publica\":..., \"onde_procurar\":...}]"),
    ("fundos_conselhos_go", "Quais fundos públicos com conselho em Goiás e Goiânia (FIA, Idoso, FMAS, FUNJUVE, Meio Ambiente, Cultura) publicam editais ou resoluções de repasse a entidades, e em que página? JSON: [{\"fundo\":..., \"orgao\":..., \"onde_procurar\":...}]"),
    ("vizinhos_de_financiador", "Dado um financiador que publicou edital para OSC, que órgãos ou empresas VIZINHOS costumam publicar o mesmo tipo de chamada (prefeitura ao lado, secretaria irmã, instituto da mesma empresa)? JSON: [{\"financiador_origem\":..., \"vizinho\":..., \"onde_procurar\":...}]"),
]


def minerar(ia: IALocal, ja_feitos: set[str]) -> dict:
    """Sem trabalho pendente = gatilho de um PROMPT DIFERENTE. Resultado sempre registrado, curto, mesmo negativo."""
    for chave, prompt in PROMPTS_MINERACAO:
        if chave in ja_feitos:
            continue
        r = ia.perguntar(prompt, "lista JSON de objetos com o campo onde_procurar")
        itens = r if isinstance(r, list) else (r.get("itens") or r.get("resultado") or []) if isinstance(r, dict) else []
        validos = []
        for x in itens if isinstance(itens, list) else []:
            onde = str((x or {}).get("onde_procurar") or "")
            if onde and (onde.startswith("http") or len(onde) > 8):
                validos.append({k: str(v)[:120] for k, v in x.items() if k in ("empresa", "fundo", "mecanismo", "vizinho", "financiador_origem", "pista", "tipo_evento", "quem_publica", "orgao", "onde_procurar")})
        return {"prompt": chave, "pistas": validos[:15], "negativo": not validos,
                "aprendizado": ("sem pistas úteis — caminho registrado para não repetir" if not validos else f"{len(validos)} pista(s) a confirmar pelos motores"),
                "status": "a_confirmar"}
    return {"prompt": None, "negativo": True, "aprendizado": "todos os prompts de mineração já rodaram hoje"}


# ─────────────────────────────────────────────────────────────── ciclo
def ciclo(porta: int | None = None) -> dict:
    c = cfg()
    hoje = date.today().isoformat()
    t0 = time.time(); orc = c.get("orcamento", {})
    ent = entender()
    ia = IALocal(porta=porta) if porta else IALocal()
    rel = {"em": now_iso(), "modelo": c.get("modelo_vencedor"), "entendimento": {k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items() if kk in ("total",)}) for k, v in ent.items() if k != "acervo_compacto"},
           "curadoria": None, "afiar": None, "mineracao": [], "descobertas": [], "ocioso_s": 0}
    if not ia.disponivel():
        rel["nota"] = "servidor do modelo não está de pé neste job"; write_json(PASTA / f"relatorio-{hoje}.json", rel); return rel
    # 1) CURAR + AFIAR: usa o ciclo do ia_local (mesmas tarefas e validação)
    from .ia_local import ciclo as ciclo_ia, aplicar as aplicar_ia
    r1 = ciclo_ia(ia, limite=int(orc.get("registros_por_ciclo", 150)))
    r2 = aplicar_ia()
    rel["curadoria"] = {k: r1.get(k) for k in ("total", "validas", "invalidas", "por_tarefa")}
    rel["afiar"] = r2
    # 2) MINERAR até o orçamento de tempo: sem ociosidade
    feitos: set[str] = set()
    limite_s = int(orc.get("minutos_por_ciclo", 300)) * 60
    while time.time() - t0 < limite_s and len(feitos) < len(PROMPTS_MINERACAO):
        m = minerar(ia, feitos)
        if not m.get("prompt"):
            break
        feitos.add(m["prompt"]); rel["mineracao"].append(m)
        if not m["negativo"]:
            rel["descobertas"].extend(m["pistas"])
    # 3) memória curta: pistas negativas ficam num arquivo só, em uma linha cada
    mem_p = PASTA / "memoria_mineracao.jsonl"
    with open(mem_p, "a", encoding="utf-8") as fh:
        for m in rel["mineracao"]:
            fh.write(json.dumps({"d": hoje, "p": m["prompt"], "n": len(m.get("pistas") or []), "neg": m["negativo"]}, ensure_ascii=False) + "\n")
    # pistas positivas viram sugestões de rota a confirmar
    if rel["descobertas"]:
        rot_p = ROOT / "estado/rotas_sugeridas_ia.json"; rot = load_json(rot_p) if rot_p.exists() else {"sugestoes": []}
        for d in rel["descobertas"]:
            rot["sugestoes"].append({"tarefa": "mineracao_sindico", **d, "em": now_iso(), "status": "a_confirmar_pelo_titular", "origem": "sindico"})
        write_json(rot_p, rot)
    rel["minutos"] = round((time.time() - t0) / 60, 1)
    rel["anuncio"] = (f"Síndico {hoje}: {rel['curadoria']['validas'] if rel['curadoria'] else 0} propostas válidas de curadoria, "
                      f"{len(rel['descobertas'])} pista(s) mineradas em {len(rel['mineracao'])} prompt(s), {rel['minutos']} min de trabalho.")
    write_json(PASTA / f"relatorio-{hoje}.json", rel)
    write_json(ROOT / "docs/dados/sindico.json", {k: v for k, v in rel.items() if k != "mineracao"} | {"prompts_rodados": [m["prompt"] for m in rel["mineracao"]]})
    return {k: v for k, v in rel.items() if k not in ("mineracao", "descobertas")} | {"descobertas": len(rel["descobertas"])}


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "entender"
    if cmd == "benchmark":
        lim = int(sys.argv[2]) if len(sys.argv) > 2 else None
        print(json.dumps(benchmark(lim), ensure_ascii=False, indent=2))
    elif cmd == "ciclo":
        print(json.dumps(ciclo(), ensure_ascii=False, indent=2))
    elif cmd == "gabarito":
        g = gabarito(); print(json.dumps({"itens": len(g), "com_texto": sum(1 for x in g if len(x["texto"]) > 200)}, ensure_ascii=False))
    else:
        print(json.dumps(entender(), ensure_ascii=False, indent=2)[:2000])
