"""O PILOTO — curador da Biblioteca de Alexandria, rodando no GitHub Actions.

Duas funções neste módulo:

  benchmark ..... roda cada modelo candidato, UM POR VEZ, contra o GABARITO (os 531 editais
                  validados pelo titular em 09/09 e 15/09) e mede: acerto na classificação,
                  prazos inventados (eliminatório), tokens/s, memória. Grava
                  (sem benchmark desde 24/09: o ocupante é empossado pelo titular e avaliado em voo real).

  ciclo ......... o dia a dia: (1) ENTENDER — lê a Biblioteca inteira (editais, leis, fontes,
                  empresas, rotas) e mantém um catálogo compacto do que sabe; (2) CURAR —
                  classifica, extrai com trecho literal, marca duplicatas; (3) AFIAR — orienta
                  os motores (URL, termo, cadência) e expande rotas a partir de cada validado;
                  (4) MINERAR — quando não há trabalho pendente, gera um PROMPT DIFERENTE de
                  busca (empresas de Lucro Real em Goiás, patrocinadores de eventos, destinação
                  de incentivo fiscal) e registra o resultado da forma mais curta possível, mesmo
                  quando negativo, para não repetir o caminho; (5) ANUNCIAR — relatório do dia.

Regra que nunca muda: o Piloto PROPÕE, a validação determinística DECIDE. Prazo, valor,
objeto e página só entram com trecho literal presente no texto. Tudo leva origem=piloto.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from datetime import timedelta, date
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json
from .ia_local import IALocal, t_classificar_objeto, t_extrair_objeto_prazo, t_propor_lexico, t_diagnosticar_rota, t_catalogar_achado, _trecho_existe, _norm

CFG_P = ROOT / "config/piloto.json"
PASTA = ROOT / "estado/piloto"
PASTA.mkdir(parents=True, exist_ok=True)

# DUAS LISTAS QUE NÃO CONVERSAVAM. O benchmark lia esta lista, fixa no código, enquanto o
# banco de reserva do cargo vivia em config/cargo_piloto.json — com nomes diferentes. Por isso
# o Qwen3-1.7B, o Llama-3.2-1B e o Phi-3.5-mini estavam no banco de reserva desde 21/09 e
# NUNCA foram medidos: o benchmark simplesmente não sabia que existiam. A lista passa a ser
# uma só, lida do arquivo do cargo, com o ocupante junto para servir de régua.
def _candidatos() -> list[dict]:
    from .nucleo import load_json as _lj
    arq = ROOT / "config/cargo_piloto.json"
    if not arq.exists():
        return []
    c = _lj(arq)
    saida, vistos = [], set()
    for m in ([c.get("ocupante_atual") or {}] + list(c.get("banco_de_reserva") or [])):
        i = m.get("id")
        if not i or i in vistos or not m.get("url"):
            continue
        vistos.add(i)
        saida.append({"id": i, "nome": m.get("nome"), "url": m["url"],
                      "arquivo": m.get("arquivo") or m["url"].rsplit("/", 1)[-1],
                      "gb": m.get("gb"), "licenca": m.get("licenca"),
                      "e_ocupante": m is (c.get("ocupante_atual") or {}),
                      "nota": m.get("porque") or m.get("nota")})
    return saida


CANDIDATOS = _candidatos()
MAPA_VEREDITO = {"fomento_osc": "aprovado", "atencao": "atencao"}      # famílias de inconformidade → reprovado
# métricas que importam para o Piloto: FALSO POSITIVO (reprovado→aprovado) é o erro caro; FALSO NEGATIVO (aprovado→reprovado) perde oportunidade


def cfg() -> dict:
    c = load_json(CFG_P) if CFG_P.exists() else {"modelo_vencedor": None, "orcamento": {"minutos_por_ciclo": 300, "registros_por_ciclo": 150}}
    try:                                            # o cargo manda: o ocupante atual é quem roda
        from .cargo_piloto import ocupante
        o = ocupante(); c["modelo_vencedor"] = o["id"]; c["arquivo"] = o["arquivo"]; c["url"] = o["url"]; c["ocupante"] = o["nome"]
    except Exception:
        pass
    return c


# ─────────────────────────────────────────────────────────────── gabarito

def _servidor(modelo: Path, porta: int = 8081) -> subprocess.Popen | None:
    motor = os.environ.get("LLAMA_SERVER") or str(ROOT / "ia_local/motor/llama-server")
    if not Path(motor).exists():
        return None
    env = dict(os.environ, LD_LIBRARY_PATH=str(Path(motor).parent))
    log = open(PASTA / f"servidor-{modelo.stem[:30]}.log", "w")
    def _sobe(args):
        pr = subprocess.Popen([motor, "-m", str(modelo), "--port", str(porta), "--host", "127.0.0.1", "-c", "4096", "-t", str(os.cpu_count() or 4), *args],
                              stdout=log, stderr=subprocess.STDOUT, env=env)
        for _ in range(300):                                   # até 5 min: um 7B leva mais de 2 min para carregar no CPU
            if pr.poll() is not None:
                return None                                    # morreu: tentar a próxima variante
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{porta}/health", timeout=2) as r:
                    if r.status == 200:
                        return pr
            except Exception:
                time.sleep(1)
        pr.kill(); return None
    # 1ª tentativa com o template do arquivo (--jinja); 2ª sem, para modelos cujo template recusa 'system' (Gemma)
    return _sobe(["--jinja"]) or _sobe([])




def entender() -> dict:
    """Catálogo compacto do que a Biblioteca contém — o Piloto só orienta o que conhece."""
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


# ─────────────────────────────────────────────────────────────── aprendizado / bloqueios
def aprender(tarefa: str, tentou: str, impediu: str, aprendeu: str, nivel: int | None = None) -> None:
    """Todo bloqueio ou hipótese descartada vira UMA LINHA — o Claude lê a cada 3 dias."""
    with open(PASTA / "aprendizado.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"d": now_iso()[:16], "n": nivel, "t": tarefa, "tentou": tentou[:160], "impediu": impediu[:160], "aprendeu": aprendeu[:200]}, ensure_ascii=False) + "\n")


def fila_nivel1() -> list[str]:
    """Editais que precisam de complementação: novos sem análise, incompletos, não verificados."""
    an = load_json(ROOT / "dados/editais/analises.json") if (ROOT / "dados/editais/analises.json").exists() else {}
    dados = load_json(ROOT / "docs/dashboard-dados.json")
    ids = []
    for e in dados.get("editais") or []:
        if e.get("tipo_registro") not in ("edital", "regra_anual"):
            continue
        a = an.get(e["id"]) or {}
        if not a or a.get("selo") == "analise_incompleta" or e.get("selo_validacao") == "nao_verificada":
            ids.append(e["id"])
    return ids


def nivel2_classificar(ia: IALocal, limite: int = 30) -> dict:
    """NÍVEL 2 (escopo de 22/09): apenas CLASSIFICAR e pontuar a oportunidade — requisitos,
    critérios e a quem se destina. A elaboração de projeto e de documentos SAIU do cargo."""
    an = load_json(ROOT / "dados/editais/analises.json") if (ROOT / "dados/editais/analises.json").exists() else {}
    dados = load_json(ROOT / "docs/dashboard-dados.json")
    from .fonte_edital import EXTRAIDOS
    from .cargo_piloto import licoes_para_o_prompt, registrar_erro
    feitos = []
    for e in [x for x in dados.get("editais") or [] if (an.get(x["id"]) or {}).get("selo") == "conformidade"][:limite]:
        ex = load_json(EXTRAIDOS / f"{e['id']}.json") if (EXTRAIDOS / f"{e['id']}.json").exists() else {}
        if ex.get("classificacao_piloto"):
            continue
        r = ia.perguntar(f"{licoes_para_o_prompt()}\n\nEDITAL: {e.get('titulo')}\nOBJETO: {str((ex.get('itens') or {}).get('Objeto'))[:900]}\nREQUISITOS: {json.dumps(ex.get('requisitos') or (ex.get('itens') or {}).get('Requisitos'), ensure_ascii=False)[:900]}",
                         '{"quem_pode_concorrer": "...", "exige_tempo_minimo_de_existencia": "anos ou null", "exige_certificacao": [...], "criterios_de_pontuacao": [{"criterio":..., "peso":...}], "area": "...", "territorio": "..."}')
        if not r or not isinstance(r, dict) or "quem_pode_concorrer" not in r:
            registrar_erro("fora_do_esquema", e.get("titulo") or e["id"], "JSON do esquema", "resposta inválida"); continue
        ex["classificacao_piloto"] = {**r, "em": now_iso(), "origem": "piloto", "status": "proposta — validar pelo Claude"}
        write_json(EXTRAIDOS / f"{e['id']}.json", ex); feitos.append(e["id"])
    return {"classificados": len(feitos), "itens": feitos[:20], "nota": "só classificação; projeto e documentos não são do cargo"}


# ─────────────────────────────────────────────────────────────── ciclo (missões sorteadas)
def _titulos_conhecidos() -> set[str]:
    dados = load_json(ROOT / "docs/dashboard-dados.json")
    из = set()
    for e in dados.get("editais") or []:
        из.add(re.sub(r"[^a-z0-9 ]", "", (e.get("titulo") or "").lower())[:60])
    return из


MOTOR29 = ROOT / "config/motor_piloto.json"


def _angulo_do_dia() -> dict:
    """Sorteia o ângulo de ataque do motor 29, pulando os que estão na memória negativa."""
    import random as _r
    m = load_json(MOTOR29)
    secos = {x["id"] for x in (m.get("memoria_negativa") or {}).get("itens", [])}
    b = load_json(ROOT / "estado/piloto/bordo.json") if (ROOT / "estado/piloto/bordo.json").exists() else {}
    recentes = {x.get("alvo") for x in (b.get("missoes") or [])[:8]}
    fila = [a for a in m["angulos_de_ataque"] if a["id"] not in secos and a["id"] not in recentes] or \
           [a for a in m["angulos_de_ataque"] if a["id"] not in secos] or m["angulos_de_ataque"]
    return _r.Random(f"{date.today()}-{len(b.get('missoes') or [])}").choice(fila)


def missao_motor29(ia: IALocal, conhecidos: set[str]) -> tuple[str, list[dict], str]:
    """MOTOR 29 — o Piloto cria a consulta, BUSCA NA INTERNET e lê o que achou.
    (Antes ele respondia de memória e vinha sempre seco: o modelo local não tem rede.)"""
    from .piloto_busca import caçar
    m = load_json(MOTOR29); ang = _angulo_do_dia()
    ach, licao, consultas = caçar(ia, ang, conhecidos)
    novos = sum(1 for a in ach if a.get("novo"))
    if novos == 0:
        neg = m.setdefault("memoria_negativa", {"itens": []})
        it = next((x for x in neg["itens"] if x["id"] == ang["id"]), None)
        if it: it["secas"] = it.get("secas", 1) + 1
        else: neg["itens"].append({"id": ang["id"], "secas": 1, "desde": date.today().isoformat()})
        neg["itens"] = [x for x in neg["itens"] if x.get("secas", 0) >= 3]
    else:
        for a in [x for x in ach if x["novo"]]:
            for w in re.findall(r"[a-zà-ú]{5,}", (a["titulo"] + " " + (a.get("porque") or "")).lower()):
                if w in {t_.lower() for t_ in m["lexico_camada1_positivos"]}:
                    continue
                prop = m["aprendizado"].setdefault("termos_propostos", [])
                e = next((x for x in prop if x["termo"] == w), None)
                if e: e["vezes"] = e.get("vezes", 1) + 1
                elif len(w) > 5: prop.append({"termo": w, "vezes": 1, "angulo": ang["id"], "em": date.today().isoformat(), "status": "a confirmar pelo Claude"})
        m["aprendizado"]["termos_propostos"] = [x for x in m["aprendizado"]["termos_propostos"] if x.get("vezes", 0) >= 2][:60]
    m.setdefault("consultas_usadas", []).insert(0, {"em": now_iso()[:16], "angulo": ang["id"], "consultas": consultas, "achados": len(ach), "novos": novos})
    m["consultas_usadas"] = m["consultas_usadas"][:40]
    write_json(MOTOR29, m)
    return ang["id"], ach[:12], licao


def missao_cacar_motor(ia: IALocal, motor_id: str, conhecidos: set[str]) -> tuple[str, list[dict], str]:
    """Caça nos motores 26/27/28 com busca real, a partir do perfil declarado do motor."""
    from .piloto_busca import caçar
    rotas = (load_json(ROOT / "config/rotas_motores.json").get("motores") or {}).get(motor_id, {})
    perguntas = {
        "empresas-incentivadas": "Que empresas de Goiás publicam edital ou seleção de projetos com recursos de incentivo fiscal (Rouanet, FIA, Idoso, Esporte, PRONAS) e em que página oficial?",
        "motor-gife": "Que grandes contribuintes de ICMS de Goiás (Lucro Real) têm instituto, fundação ou programa que apoia projetos de organizações sem fins lucrativos? Qual o site oficial?",
        "motor-patrocinio": "Que empresas patrocinam eventos culturais, esportivos e comunitários em Goiânia e no interior de Goiás, e onde anunciam como pedir patrocínio?"}
    ang = {"id": f"cacar-{motor_id}", "pergunta": perguntas.get(motor_id) or (rotas.get("perfil") or motor_id)}
    ach, licao, _ = caçar(ia, ang, conhecidos, max_consultas=2, max_paginas=3)
    return ang["id"], ach, licao


def missao_cacar(ia: IALocal, conhecidos: set[str]) -> tuple[str, list[dict], str]:
    """Caça oportunidade que o sistema NÃO conhece. Abate = título inédito com onde procurar."""
    from .cargo_piloto import licoes_para_o_prompt
    from .piloto import PROMPTS_MINERACAO
    b = load_json(ROOT / "estado/piloto/bordo.json") if (ROOT / "estado/piloto/bordo.json").exists() else {}
    feitos = {m.get("alvo") for m in (b.get("missoes") or [])[:10]}
    chave, prompt = next(((k, p) for k, p in PROMPTS_MINERACAO if k not in feitos), PROMPTS_MINERACAO[0])
    r = ia.perguntar((licoes_para_o_prompt() + "\n\n" if licoes_para_o_prompt() else "") + prompt,
                     "lista JSON de objetos com os campos nome/empresa/fundo, onde_procurar (url ou termo) e uf quando houver")
    itens = r if isinstance(r, list) else ((r or {}).get("itens") or (r or {}).get("resultado") or [])
    ach = []
    for x in itens if isinstance(itens, list) else []:
        onde = str((x or {}).get("onde_procurar") or "")
        titulo = str((x or {}).get("empresa") or (x or {}).get("fundo") or (x or {}).get("mecanismo") or (x or {}).get("nome") or "")[:110]
        if not titulo or not onde or len(onde) < 8:
            continue
        chave_t = re.sub(r"[^a-z0-9 ]", "", titulo.lower())[:60]
        ach.append({"titulo": titulo, "onde": onde[:140], "url": onde if onde.startswith("http") else None,
                    "uf": (x or {}).get("uf"), "novo": chave_t not in conhecidos})
    licao = "caminho sem retorno — registrado para não repetir" if not ach else f"{sum(1 for a in ach if a['novo'])} alvo(s) inédito(s)"
    return chave, ach[:12], licao


def missao_afiar(ia: IALocal, motor_id: str) -> tuple[str, list[dict], str]:
    """Olha o que o motor leu e propõe como ele acha mais da próxima vez."""
    rotas = (load_json(ROOT / "config/rotas_motores.json").get("motores") or {}).get(motor_id, {})
    esq = (load_json(ROOT / "estado/esquadra.json").get("sensores") or {}).get(motor_id, {})
    p = t_diagnosticar_rota(ia, {"id": motor_id, "nome": rotas.get("perfil") or motor_id, "perfil": rotas.get("perfil"),
                                 "rotas": rotas.get("rotas"), "diagnostico": esq.get("diagnostico"), "lexico": rotas.get("lexico_camada1") or []})
    if not p or not p.get("valido"):
        return motor_id, [], "sem proposta aproveitável nesta passagem"
    ach = [{"titulo": f"{x['tipo']}: {str(x['valor'])[:80]}", "onde": x.get("porque", "")[:120], "url": x["valor"] if x["tipo"] == "url" else None, "novo": False}
           for x in p["tentar"] if x.get("valido")]
    rot_p = ROOT / "estado/rotas_sugeridas_ia.json"; rot = load_json(rot_p) if rot_p.exists() else {"sugestoes": []}
    rot["sugestoes"].append({**p, "em": now_iso(), "status": "a_confirmar_pelo_titular", "origem": "piloto"})
    write_json(rot_p, rot)
    return motor_id, ach, (p.get("causa_provavel") or "")[:150]


def missao_local(ia: IALocal, motor_id: str, conhecidos: set[str]) -> tuple[str, list[dict], str]:
    """Procura um LOCAL novo de publicação para a família daquele motor."""
    rotas = (load_json(ROOT / "config/rotas_motores.json").get("motores") or {}).get(motor_id, {})
    r = ia.perguntar(f"PERFIL DO MOTOR: {rotas.get('perfil')}\nROTAS QUE JÁ CONHEÇO: {[x.get('nome') for x in (rotas.get('rotas') or [])]}\n"
                     "Que OUTROS lugares publicam o mesmo tipo de oportunidade no Brasil e que não estão na lista? Órgãos vizinhos, plataformas, boletins, conselhos.",
                     '[{"local": "nome", "onde_procurar": "url ou termo de busca", "porque": "uma frase"}]')
    itens = r if isinstance(r, list) else ((r or {}).get("itens") or [])
    ach = []
    for x in itens if isinstance(itens, list) else []:
        onde = str((x or {}).get("onde_procurar") or ""); nome = str((x or {}).get("local") or "")[:100]
        if nome and len(onde) > 8:
            ach.append({"titulo": nome, "onde": onde[:140], "url": onde if onde.startswith("http") else None,
                        "novo": re.sub(r"[^a-z0-9 ]", "", nome.lower())[:60] not in conhecidos})
    return motor_id, ach[:8], f"{len(ach)} local(is) candidato(s)"


def _contar_voo() -> int:
    arq = PASTA / "voos.json"
    d = load_json(arq) if arq.exists() else {}
    hoje = date.today().isoformat()
    d[hoje] = int(d.get(hoje, 0)) + 1
    d = {k: v for k, v in sorted(d.items())[-14:]}
    write_json(arq, d)
    return d[hoje]



def escolher_rumo(ia: IALocal, ent: dict) -> dict:
    """ANTES de voar, o Piloto lê a Biblioteca e decide ONDE procurar — não sorteia no vazio.
    Ele olha o que já tem, o que falta, o que rendeu e o que veio seco, e propõe o rumo do voo."""
    m = load_json(MOTOR29)
    b = load_json(ROOT / "estado/piloto/bordo.json") if (ROOT / "estado/piloto/bordo.json").exists() else {}
    rad = load_json(ROOT / "dados/empresas/radar_piloto.json") if (ROOT / "dados/empresas/radar_piloto.json").exists() else {}
    ultimas = [{"angulo": x.get("alvo"), "abates": x.get("abates", 0)} for x in (b.get("missoes") or [])[:12]]
    secos = [x["id"] for x in (m.get("memoria_negativa") or {}).get("itens", [])]
    setores_ja = sorted({(e.get("angulos") or ["?"])[0] for e in (rad.get("empresas") or {}).values()})
    r = ia.perguntar(
        "VOCÊ É O PILOTO do Eldorado. Antes de sair para o voo, olhe o que a casa já tem e decida ONDE procurar recurso novo.\n\n"
        f"BIBLIOTECA HOJE: {json.dumps({k: (v.get('total') if isinstance(v, dict) else v) for k, v in ent.items() if k != 'acervo_compacto'}, ensure_ascii=False)}\n"
        f"ÚLTIMOS VOOS (ângulo → alvos novos): {json.dumps(ultimas, ensure_ascii=False)}\n"
        f"ÂNGULOS QUE VIERAM SECOS: {secos}\n"
        f"SETORES JÁ NO RADAR: {setores_ja[:20]}\n\n"
        "Onde há recurso que ainda não mapeamos? Pense em quem PAGA: empresa que deduz imposto, que patrocina evento, "
        "que tem instituto, que publica relatório ESG, que aparece como apoiadora no site de outra entidade. "
        "Proponha o rumo deste voo — setor, região e tipo de fonte — e diga por quê.",
        '{"rumo": "uma frase", "setor": "...", "regiao": "GO|Centro-Oeste|BR|internacional", '
        '"tipo_de_fonte": "empresa|instituto|fundacao|cooperativa|multinacional|programa_publico", '
        '"pergunta_de_busca": "a pergunta que o voo deve responder", "porque": "uma frase"}')
    if not r or not r.get("pergunta_de_busca"):
        return {}
    rumo = {"id": "rumo-" + re.sub(r"[^a-z0-9]+", "-", str(r.get("setor") or "livre").lower())[:28],
            "pergunta": str(r["pergunta_de_busca"])[:400], "nivel": {"GO": "regional", "Centro-Oeste": "regional",
            "BR": "nacional", "internacional": "internacional"}.get(str(r.get("regiao")), "nacional"),
            "alvo": r.get("tipo_de_fonte") or "empresa", "rumo": r.get("rumo"), "porque": r.get("porque"), "origem": "rumo_do_piloto"}
    m.setdefault("rumos_escolhidos", []).insert(0, {**rumo, "em": now_iso()[:16]})
    m["rumos_escolhidos"] = m["rumos_escolhidos"][:40]
    write_json(MOTOR29, m)
    return rumo



def missao_resgate(ia, alvo: dict, conhecidos: set[str]) -> tuple[str, list[dict], str]:
    """MISSÃO ESPECIAL: completar um edital que os outros motores acharam pela metade.
    Tem prioridade sobre qualquer exploração — de nada adianta descobrir mais um edital
    se os que já temos não têm prazo, documento nem página oficial."""
    from .missao_especial import plano_de_voo, registrar_resgate
    from .piloto_busca import buscar, ler_pagina

    plano = plano_de_voo(ia, alvo)                     # o Piloto decide como achar o que falta
    consultas = plano["consultas_sugeridas"] or [
        f"{alvo.get('titulo','')[:70]} {alvo.get('orgao') or ''} edital página oficial".strip()]
    achados, dados, paginas = [], {}, 0

    # PRIMEIRO O SITE DO ÓRGÃO, DEPOIS O BUSCADOR (23/09). Em 24 horas, 30 de 32 resgates
    # falharam por não achar a página oficial — e não é de espantar: o chamamento de um
    # município está no portal dele, não no índice de um buscador. Se sabemos o órgão,
    # lemos o site dele por dentro, que ninguém bloqueia e onde o documento realmente está.
    # VETOR NÃO É FONTE: PNCP e diários são onde o edital foi ANUNCIADO, e os motores já
    # os leem todo dia. Ler o sitemap deles é repetir trabalho e não acha o documento.
    VETOR_DOM = ("pncp.gov.br", "in.gov.br", "queridodiario.ok.org.br", "diariooficial")
    from .piloto_busca import buscar_na_fonte
    candidatos = []
    for campo in ("pagina_oficial", "site", "url"):
        u = alvo.get(campo)
        if u and str(u).startswith("http"):
            from urllib.parse import urlsplit
            h = (urlsplit(str(u)).hostname or "").replace("www.", "")
            if h and h not in candidatos and not any(v in h for v in VETOR_DOM):
                candidatos.append(h)
    termos = [w for w in re.findall(r"[a-zà-ú0-9]{5,}", str(alvo.get("titulo") or "").lower())][:6]
    termos += ["edital", "chamamento", "chamada", "selecao", "seleção", "inscricoes", "inscrições"]
    for dom in candidatos[:2]:
        try:
            for it in buscar_na_fonte(dom, termos, teto=12):
                texto = ler_pagina(it["url"])
                if len(texto) < 300:
                    continue
                paginas += 1
                r = ia.perguntar(
                    f"PROCURO ESTE EDITAL: {alvo.get('titulo')}\nPÁGINA DO PRÓPRIO ÓRGÃO: {it['url']}\n"
                    f"TEXTO: {texto[:3000]}\n\nÉ este edital? Extraia só o que estiver escrito.",
                    '{"e_este_edital": true|false, "prazo": "AAAA-MM-DD ou null", "quem_pode": "... ou null", '
                    '"documentos": ["..."], "valor": "... ou null", "como_inscrever": "... ou null", '
                    '"trecho": "frase literal"}')
                if r and r.get("e_este_edital") and r.get("trecho"):
                    tr = re.sub(r"\s+", " ", str(r["trecho"]).lower())[:45]
                    if tr and tr in re.sub(r"\s+", " ", texto.lower()):
                        dados = {"pagina_oficial": it["url"],
                                 "prazo": r.get("prazo") if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(r.get("prazo") or "")) else None,
                                 "quem_pode": r.get("quem_pode"), "documentos": r.get("documentos") or [],
                                 "valor": r.get("valor"), "como_inscrever": r.get("como_inscrever")}
                        achados.append({"titulo": alvo.get("titulo", "")[:110], "onde": it["url"], "url": it["url"],
                                        "trecho": str(r["trecho"])[:180], "porque": "resgate pelo site do próprio órgão",
                                        "situacao": "aberta" if (dados["prazo"] or "") >= date.today().isoformat() else
                                                    ("arquivada" if dados["prazo"] else "sem_prazo_na_pagina"),
                                        "prazo": dados["prazo"], "documentos": dados["documentos"],
                                        "confirmado_na_pagina": True, "novo": False, "resgate": True,
                                        "via": "site do órgão"})
                        break
        except Exception:
            pass
        if dados:
            break
    # o buscador vira segunda via: só entra se o site do órgão não resolveu
    for c in (consultas[:3] if not dados else []):
        for b in buscar(c, maximo=6):
            if paginas >= 5:
                break
            texto = ler_pagina(b["url"])
            if len(texto) < 300:
                continue
            paginas += 1
            r = ia.perguntar(
                f"PROCURO ESTE EDITAL: {alvo.get('titulo')}\nÓRGÃO: {alvo.get('orgao') or '?'}\n"
                f"FALTA SABER: {alvo.get('falta')}\n\nPÁGINA: {b['url']}\nTEXTO: {texto[:3500]}\n\n"
                "Esta página é do edital que procuro? Se for, extraia SÓ o que estiver escrito nela. "
                "Não invente data nem documento: o que não estiver na página, deixe null.",
                '{"e_este_edital": true|false, "prazo": "AAAA-MM-DD ou null", "quem_pode": "... ou null", '
                '"documentos": ["..."] , "valor": "... ou null", "como_inscrever": "... ou null", '
                '"trecho": "frase literal que comprova ser este edital"}')
            if not (r and r.get("e_este_edital") and r.get("trecho")):
                continue
            tr = re.sub(r"\s+", " ", str(r["trecho"]).lower())[:45]
            if tr and tr not in re.sub(r"\s+", " ", texto.lower()):
                continue                               # trecho inventado: não aceito
            dados = {"pagina_oficial": b["url"],
                     "prazo": r.get("prazo") if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(r.get("prazo") or "")) else None,
                     "quem_pode": r.get("quem_pode"), "documentos": r.get("documentos") or [],
                     "valor": r.get("valor"), "como_inscrever": r.get("como_inscrever")}
            achados.append({"titulo": alvo.get("titulo", "")[:110], "onde": b["url"], "url": b["url"],
                            "trecho": str(r["trecho"])[:180], "porque": "resgate de edital incompleto",
                            "situacao": "aberta" if (dados["prazo"] or "") >= date.today().isoformat() else
                                        ("arquivada" if dados["prazo"] else "sem_prazo_na_pagina"),
                            "prazo": dados["prazo"], "documentos": dados["documentos"],
                            "confirmado_na_pagina": True, "novo": False, "resgate": True})
            break
        if dados:
            break
    it = registrar_resgate(alvo["id"], dados, bool(dados))
    faltava = len(alvo.get("falta") or [])
    resta = len((it or {}).get("falta") or [])
    via = (achados[0].get("via") if achados else None) or "buscador"
    licao = (f"resgate '{alvo.get('titulo','')[:40]}' [{via}]: {paginas} página(s) lida(s) — "
             + (f"completou {faltava - resta} de {faltava} dado(s); estado {it.get('estado')}" if dados
                else "não achei a página oficial"))
    return f"resgate:{alvo['id']}", achados, licao


def missao_prospeccao(ia, angulo: dict, conhecidos: set[str]) -> tuple[str, list[dict], str]:
    """MISSÃO DE EXPANSÃO: descobrir LUGARES novos, não editais.

    O Piloto procura o rastro (quem patrocina alguém), acha a empresa, e valida no site DELA
    o que ela oferece — sem buscador, lendo as trilhas do próprio site. A fonte validada entra
    no catálogo; se tiver edital próprio, vira motor e sai da lista de voo para sempre."""
    from .piloto_busca import buscar, ler_pagina
    from .prospeccao import (catalogar_patrocinadores, validar_empresa, registrar,
                             incorporar, publicar as pub_prosp, NIVEIS)
    from .cobertura import ja_coberto

    nivel = angulo.get("nivel") if angulo.get("nivel") in NIVEIS else "federal"
    r = ia.perguntar(
        f"MISSÃO DE EXPANSÃO — nível {nivel} ({NIVEIS[nivel]['rotulo']}).\n"
        f"OBJETIVO: {angulo.get('pergunta')}\n"
        f"ONDE COSTUMA ESTAR: {', '.join(NIVEIS[nivel]['onde_procurar'])}\n\n"
        "Não procure editais. Procure PÁGINAS QUE LISTAM APOIADORES: 'nossos parceiros', "
        "'quem nos apoia', 'patrocinadores', 'apoio', no site de associações, ONGs, hospitais "
        "filantrópicos, festivais e projetos culturais. É ali que as empresas que financiam "
        "terceiro setor se declaram.",
        '{"consultas": ["consulta 1", "consulta 2"]}')
    consultas = [c for c in ((r or {}).get("consultas") or []) if isinstance(c, str)][:2] or \
                [f"\"nossos parceiros\" OR \"quem nos apoia\" associação {NIVEIS[nivel]['rotulo']}"]

    novas, validadas, motores, paginas, rotas_novas = [], 0, [], 0, []
    for c in consultas:
        for b in buscar(c, maximo=5):
            if paginas >= 4:
                break
            html = ler_pagina(b["url"], limite=20000)
            if len(html) < 400:
                continue
            paginas += 1
            for emp in catalogar_patrocinadores(html, b["url"])[:6]:
                if ja_coberto(emp["site"])[0]:
                    continue
                v = validar_empresa(emp["dominio"])
                it = registrar(emp, v, nivel=nivel, angulo=angulo.get("id", ""))
                if v.get("tem_programa"):
                    validadas += 1
                    novas.append({"titulo": f"{emp['nome']} — {', '.join(it.get('tipos') or [])}",
                                  "onde": emp["site"], "url": emp["site"],
                                  "trecho": next(iter(v["tipos"].values()), {}).get("trecho", "")[:180],
                                  "porque": f"fonte nova de recurso ({nivel})", "novo": True,
                                  "confirmado_na_pagina": True, "fonte_nova": True})
                if v.get("tem_programa"):
                    # a fonte validada desencadeia tudo: motor (próprio ou engordando o do tipo),
                    # ficha na Biblioteca e entrada no ranking de empresas
                    inc = incorporar(emp["dominio"])
                    enc = inc.get("encaminhamento") or {}
                    if enc.get("motor_criado"):
                        motores.append(enc["motor_criado"])
                    rotas_novas.extend(g["motor"] for g in (enc.get("rotas_acrescentadas") or []))
    pub_prosp()
    licao = (f"expansão {nivel}: {paginas} página(s) de apoiadores lida(s) → {validadas} empresa(s) com programa"
             + (f" → {len(motores)} motor(es) novo(s): {', '.join(motores)}" if motores else "")
             + (f" → {len(rotas_novas)} rota(s) nova(s) em {', '.join(sorted(set(rotas_novas)))}" if rotas_novas else "")
             + ("" if (motores or rotas_novas) else " → nada a acrescentar aos motores"))
    return f"expansao:{nivel}", novas, licao


CONSULTAS_PROSPECCAO = [
    "patrocínio empresa Goiânia projeto social {ano}", "apoio institucional Goiás instituto empresa edital {ano}",
    "investimento social privado Goiás empresas", "empresas goianas responsabilidade social ESG relatório {ano}",
    "patrocinadores festival Goiânia {ano}", "lei de incentivo ao esporte patrocinador Goiás {ano}",
    "Lei Rouanet incentivador Goiânia empresa {ano}", "fundação empresarial Goiás edital projetos {ano}",
    "doação empresa hospital Goiânia PRONON {ano}", "instituto empresarial Centro-Oeste chamada projetos {ano}",
]


def missao_aposta(brief: dict, ordem: int) -> tuple[str, list[dict], str]:
    """A APOSTA VIRA MISSÃO (26/09): o briefing apostava ('programa de doação de multinacional com inscrição
    local') e as mãos faziam sempre o mesmo. Agora a pergunta de pesquisa do briefing vira consulta no buscador,
    as primeiras páginas são lidas, e o que parece edital/programa vira CANDIDATA para o Interceptador; empresa
    que patrocina ou doa vai ao radar."""
    from .piloto_busca import buscar, ler_pagina
    from .reconhecimento import ler_rastros, registrar
    from .nucleo import load_json as _lj, write_json as _wj
    q = str(brief.get("pergunta_de_pesquisa") or "").strip()
    ap = brief.get("aposta") if isinstance(brief.get("aposta"), dict) else {}
    if not q and ap.get("onde"):
        q = f"{ap['onde']} edital inscrições organizações sociedade civil"
    if not q:
        return "sem aposta", [], "aposta · o briefing não trouxe pergunta de pesquisa"
    q = re.sub(r"\s+", " ", q)[:120] + ("" if ordem == 1 else " Goiás")
    res = buscar(q, maximo=8) or []
    ach, cand = [], []
    arq = ROOT / "estado/piloto/candidatas_do_catalogo.json"
    C = _lj(arq) if arq.exists() else {"candidatas": []}
    ja = {x.get("url") for x in C.get("candidatas") or []}
    for r in res[:5]:
        url = r.get("url") or ""; titulo = (r.get("titulo") or "")[:160]
        texto = ler_pagina(url, limite=9000) or ""
        if re.search(r"edital|inscri[cç][õo]es|chamada|chamamento|programa de doa|patroc[ií]nio|apoio a projetos|sele[cç][aã]o de projetos", (titulo + " " + texto[:3000]).lower()) \
                and url.startswith("http") and url not in ja and not re.search(r"duckduckgo|bing\.|google\.|wikipedia", url):
            cand.append({"url": url, "titulo": titulo or url, "visto_em": "aposta do briefing", "enquadramento": "A VERIFICAR",
                         "descoberto_em": date.today().isoformat(), "origem": "aposta do Piloto - Espião", "aposta": ap.get("onde")})
            ach.append({"titulo": titulo, "url": url, "novo": True})
        for rs in ler_rastros(texto, url):
            it = registrar(rs, "aposta_do_briefing", 1)
            if it:
                ach.append({"titulo": it.get("empresa"), "empresa": it.get("empresa"), "via": rs.get("via"), "url": url, "novo": True})
    if cand:
        C["candidatas"] = (C.get("candidatas") or []) + cand; C["em"] = date.today().isoformat(); _wj(arq, C)
    return q, ach, f"aposta · '{q[:70]}': {len(res)} resultado(s), {len(cand)} candidata(s) nova(s), {len([a for a in ach if a.get('empresa')])} empresa(s)"


def missao_prospectar(ordem: int) -> tuple[str, list[dict], str]:
    """BUSCA ATIVA DE EMPRESAS (titular, 24/09): consultas criativas que rodam em rodízio; das páginas
    devolvidas, lê as primeiras e extrai quem patrocina, apoia ou doa. Empresa já na base de incentivos
    não conta como descoberta."""
    from datetime import date as _d
    from .piloto_busca import buscar, ler_pagina
    from .reconhecimento import ler_rastros, registrar
    from .catalogo_terceiro_setor import empresas_ja_conhecidas
    q = CONSULTAS_PROSPECCAO[(int(time.time() // 600) + ordem) % len(CONSULTAS_PROSPECCAO)].format(ano=_d.today().year)
    res = buscar(q, maximo=8) or []
    conhecidas = empresas_ja_conhecidas()
    ach = []
    for r in res[:4]:
        texto = ler_pagina(r.get("url") or "", limite=9000)
        for rs in ler_rastros(texto or "", r.get("url") or ""):
            it = registrar(rs, "busca_ativa", 1)
            if it and re.sub(r"[^a-z0-9]", "", str(it.get("empresa") or "").lower())[:40] not in conhecidas:
                ach.append({"titulo": it.get("empresa"), "empresa": it.get("empresa"), "via": rs.get("via"), "url": r.get("url"), "novo": True})
    return q, ach, f"busca ativa · '{q}': {len(res)} resultado(s), {len(ach)} empresa(s) nova(s)"


def missao_catalogar(site: dict) -> tuple[str, list[dict], str]:
    """Visita um site especializado do terceiro setor: páginas para entidades, empresas presentes, ESG."""
    from .piloto_busca import ler_pagina
    from .catalogo_terceiro_setor import catalogar
    import urllib.request
    from html.parser import HTMLParser
    class _L(HTMLParser):
        def __init__(self): super().__init__(); self.links = []; self._h = None; self._t = []
        def handle_starttag(self, tag, attrs):
            if tag == "a": self._h = dict(attrs).get("href"); self._t = []
        def handle_data(self, d):
            if self._h is not None: self._t.append(d)
        def handle_endtag(self, tag):
            if tag == "a" and self._h: self.links.append((self._h, " ".join(self._t).strip()[:120])); self._h = None
    texto = ler_pagina(site["url"], limite=12000)
    links = []
    try:
        req = urllib.request.Request(site["url"], headers={"User-Agent": "Mozilla/5.0 (Eldorado)"})
        with urllib.request.urlopen(req, timeout=20) as r:
            html = r.read(600_000).decode("utf-8", "ignore")
        p = _L(); p.feed(html); links = p.links
    except Exception:
        pass
    if not texto and not links:
        from .catalogo_terceiro_setor import falhou
        falhou(site)                                     # sai da vez; na 3ª falha seguida, sai do rodízio
        return site["nome"], [], f"catálogo · {site['nome']}: página não respondeu"
    reg = catalogar(site, texto or "", links)
    ach = [{"titulo": e.get("empresa"), "empresa": e.get("empresa"), "via": e.get("via"), "url": site["url"], "novo": True}
           for e in reg.get("empresas") or []]
    return site["nome"], ach, (f"catálogo · {site['nome']}: {len(reg.get('paginas_para_entidades') or [])} página(s) para entidades, "
                              f"{len(ach)} empresa(s), ESG {'declarado' if (reg.get('esg') or {}).get('declarado') else 'não declarado'}")


def missao_reconhecimento(ia, rumo: dict, conhecidos: set[str]) -> tuple[str, list[dict], str]:
    """MISSÃO REGULAR — reconhecimento do terceiro setor e de quem o financia.

    Não procura edital: procura ATIVIDADE JÁ FEITA e pergunta quem pagou. Oficina numa
    associação, festival de uma ONG, reforma de uma APAE — tudo isso teve financiador, e
    quase nunca houve edital. Por isso nenhum dos 29 motores acha: motor lê edital publicado.
    A imprensa é fonte de primeira ordem aqui, porque a matéria nomeia o patrocinador — ele
    exige que nomeie.
    """
    from .piloto_busca import buscar, ler_pagina
    from .reconhecimento import (ler_rastros, registrar, proximo_do_plano, publicar as pub_rec,
                                 FRENTES, marcar)
    from .cobertura import ja_coberto

    # 1 · O PLANO DE VOO MANDA: se há alvo a investigar de um voo anterior, ele vem primeiro
    pendente = proximo_do_plano()
    if pendente:
        anda = f"investigar {pendente['empresa']}"
        consultas = [f"{pendente['empresa']} instituto OR fundação OR patrocínio projeto social",
                     f"{pendente['empresa']} responsabilidade social relatório"]
        frente = "investigacao"
    else:
        frente = (rumo.get("frente") if rumo.get("frente") in FRENTES else
                  ("imprensa" if (rumo.get("ordem") or 0) % 2 else "entidade"))
        f = FRENTES[frente]
        r = ia.perguntar(
            f"MISSÃO DE RECONHECIMENTO — {f['rotulo']}.\n"
            f"PROCURO: atividade do terceiro setor que JÁ ACONTECEU e quem pagou por ela.\n"
            f"ONDE COSTUMA ESTAR: {', '.join(f['procurar'])}\n"
            f"O QUE LER NA PÁGINA: {', '.join(f['onde_olhar'])}\n\n"
            "Escreva consultas que levem a PÁGINAS DE ENTIDADE do terceiro setor ou a MATÉRIAS "
            "sobre projetos sociais realizados, onde o patrocinador seja citado. Não procure "
            "edital: procure o que já foi feito e quem bancou.",
            '{"consultas": ["consulta 1", "consulta 2"]}')
        consultas = [c for c in ((r or {}).get("consultas") or []) if isinstance(c, str)][:2] or [
            f"\"projeto social\" \"com o apoio\" {f['procurar'][0]} Goiás"]
        anda = f"reconhecimento · {f['rotulo']}"

    achados, paginas, empresas = [], 0, 0
    for c in consultas[:2]:
        for b in buscar(c, maximo=5):
            if paginas >= 4:
                break
            if ja_coberto(b["url"])[0]:
                continue
            texto = ler_pagina(b["url"])
            if len(texto) < 400:
                continue
            paginas += 1
            for ra in ler_rastros(texto, b["url"]):
                it = registrar(ra, frente, rumo.get("nivel") or "regional")
                if not it:
                    continue
                empresas += 1
                achados.append({"titulo": f"{ra['empresa']} — {ra['via']}", "onde": b["url"],
                                "url": b["url"], "trecho": ra["trecho"][:180],
                                "porque": f"financiou atividade do terceiro setor ({ra['via']})",
                                "novo": True, "confirmado_na_pagina": True,
                                "reconhecimento": True, "via": ra["via"]})
    if pendente and paginas:
        marcar(pendente["alvo"], "investigado")
    pub_rec()
    licao = (f"{anda}: {paginas} página(s) lida(s) → {empresas} financiador(es) identificado(s)"
             + (f" — entram no plano dos próximos voos" if empresas else " — nenhum rastro"))
    return f"reconhecimento:{frente}", achados, licao


def ciclo(porta: int | None = None) -> dict:
    """VOO DO PILOTO: missões sorteadas, uma de cada vez, com diário de bordo."""
    from .esquadrilha import sortear, abrir_missao, fechar_missao, resumo
    from .cargo_piloto import ocupante
    c = cfg(); hoje = date.today().isoformat(); t0 = time.time()
    orc = c.get("orcamento", {}); par = (load_json(ROOT / "config/cargo_piloto.json") or {}).get("parametros", {})
    ent = entender()
    ia = IALocal(porta=porta) if porta else IALocal()
    rel = {"em": now_iso(), "modelo": c.get("modelo_vencedor"), "ocupante": ocupante().get("nome"),
           "entendimento": {k: (v.get("total") if isinstance(v, dict) else v) for k, v in ent.items() if k != "acervo_compacto"},
           "missoes": [], "abates": 0, "propostas": 0}
    if not ia.disponivel():
        rel["nota"] = "o avião não decolou: servidor do modelo fora do ar neste job"
        write_json(PASTA / f"relatorio-{hoje}.json", rel); return rel
    conhecidos = _titulos_conhecidos()
    # O VOO DURA O QUE A TAREFA EXIGIR. Isto não é uma meta de tempo: é o TETO de segurança
    # para não estourar os 30 minutos do job. Um voo pode durar 1 minuto — se a fila de
    # resgate estiver vazia e o rumo render rápido — ou ir até o teto. O que não pode é
    # ficar parado: acabou o trabalho, o voo encerra e o próximo decola em 3 segundos.
    teto_s = int(orc.get("teto_minutos", orc.get("minutos_por_ciclo", 25))) * 60
    os.environ["ELDORADO_FIM_DO_VOO"] = str(time.time() + teto_s)     # o único limite: todos leem daqui
    rel["voo_do_dia"] = _contar_voo()
    from .briefing_piloto import escrever as _brief, fechar as _fechar
    brief = _brief(ia)                                # RELATÓRIO DE CONTEXTO: lê o banco e os voos anteriores
    rel["briefing"] = {k: brief.get(k) for k in ("diagnostico", "aposta", "pergunta_de_pesquisa", "nivel")}
    rumo = {"id": "briefing-" + re.sub(r"[^a-z0-9]+", "-", str((brief.get("aposta") or {}).get("onde") or "livre").lower())[:28],
            "pergunta": brief["pergunta_de_pesquisa"], "nivel": brief.get("nivel") or "nacional",
            "alvo": "empresa", "porque": (brief.get("aposta") or {}).get("porque"), "origem": "briefing"}
    if rumo:
        rel["rumo"] = {k: rumo[k] for k in ("rumo", "nivel", "alvo", "porque") if k in rumo}
    plano = []
    # PILOTO - ESPIÃO (titular, 26/09): missão única de DESCOBERTA — sites, empresas e possíveis fontes de recurso.
    # O resgate (comprovar prazo e página oficial) passou ao Piloto - Interceptador, que tem fila e arquivos
    # próprios; o Espião não toca na fila de resgate. O que ele descobre vira candidata para o Interceptador.
    rel["papel"] = "Piloto - Espião"; rel["resgates_na_fila"] = 0; rel["resgates_fora_dos_30_dias"] = 0
    # 1) A APOSTA DO BRIEFING VIRA MISSÃO — duas buscas (nacional e Goiás) antes de tudo
    if brief.get("pergunta_de_pesquisa") or (isinstance(brief.get("aposta"), dict) and brief["aposta"].get("onde")):
        for o in (1, 2):
            plano.append({"tipo": "aposta", "motor": "piloto-aberto", "ordem": len(plano) + 1, "alvo_id": f"aposta-{o}",
                          "_alvo": {"titulo": f"aposta do briefing ({'nacional' if o == 1 else 'Goiás'})"}, "_brief": brief, "_ordem": o})
    # 2) catálogo e busca ativa até PREENCHER O VOO (o tempo é o único limite; sem isto o voo pousava aos 3 min)
    from .catalogo_terceiro_setor import proximo_site as _proximo_site
    vagas = int(par.get("missoes_por_voo", 7)) - len(plano)
    while vagas > 0:
        site = _proximo_site({x.get("_site", {}).get("url") for x in plano if x.get("_site")} | {x.get("_site", {}).get("_chave") for x in plano if x.get("_site")})
        if not site or any(x.get("_site", {}).get("url") == site["url"] for x in plano):
            break
        plano.append({"tipo": "catalogar", "motor": "piloto-aberto", "ordem": len(plano) + 1,
                      "alvo_id": site["url"], "_site": site, "_alvo": {"titulo": site["nome"]}})
        vagas -= 1
        if vagas > 0:                                   # proativo: a cada site, uma busca ativa de empresas
            plano.append({"tipo": "prospectar", "motor": "piloto-aberto", "ordem": len(plano) + 1,
                          "alvo_id": f"prospeccao-{len(plano)}", "_alvo": {"titulo": "busca ativa de empresas"}})
            vagas -= 1
    # POSIÇÃO AO VIVO: o painel só é republicado a cada 6 h; a posição vai por um ramo
    # próprio, lido direto pelo navegador, para o avião aparecer onde o trabalho está AGORA
    from .posicao_piloto import anunciar as _anunciar, pousar as _pousar_pos, registro as _reg_pos
    # OS ACHADOS DO VOO, EM LISTA. Cada missão guarda só a CONTAGEM em rel["missoes"] ("achados":
    # len(ach)), e o pouso somava len() dessa contagem. Com zero achados, '0 or []' escondia o
    # defeito; com UM achado, o voo quebrava no pouso — e perdia relatório, aprendizado do
    # briefing, radar e anúncio de pouso. Em 24/09, os voos que falhavam eram justamente os
    # que tinham encontrado alguma coisa.
    _todos_ach: list[dict] = []
    for m in plano:
        if time.time() - t0 > teto_s:
            rel["encerrou_por"] = "teto de tempo"
            break
        abrir_missao(m, m.get("motor") or "")
        _anunciar(m, voo=rel.get("voo_do_dia"), de=len(plano))
        try:
            if m["tipo"] == "resgate":
                alvo, ach, licao = missao_resgate(ia, m["_alvo"], conhecidos)
            elif m["tipo"] == "catalogar":
                alvo, ach, licao = missao_catalogar(m["_site"])
            elif m["tipo"] == "prospectar":
                alvo, ach, licao = missao_prospectar(m["ordem"])
            elif m["tipo"] == "aposta":
                alvo, ach, licao = missao_aposta(m["_brief"], m["_ordem"])
            elif m.get("motor") == "piloto-aberto":
                # MISSÃO 2 — reconhecimento: o que os motores não acham porque não houve edital
                alvo, ach, licao = missao_reconhecimento(ia, {**(rumo or {}), "ordem": m["ordem"]}, conhecidos)
            elif False:
                _ang = rumo if rumo else {}
                if (_ang.get("alvo") in ("rastro", "site", "empresa")) or (m["ordem"] % 2 == 0):
                    alvo, ach, licao = missao_prospeccao(ia, {**_ang, "nivel": _ang.get("nivel") or "federal"}, conhecidos)
                else:
                    alvo, ach, licao = missao_motor29(ia, conhecidos)
            elif m["tipo"] == "cacar_oportunidade":
                alvo, ach, licao = missao_cacar_motor(ia, m["motor"], conhecidos)
            elif m["tipo"] == "afiar_motor":
                alvo, ach, licao = missao_afiar(ia, m["motor"])
            else:
                alvo, ach, licao = missao_local(ia, m["motor"], conhecidos)
        except Exception as ex_:
            aprender("missao", m["tipo"], f"{type(ex_).__name__}: {ex_}", "revisar prompt/esquema", None)
            alvo, ach, licao = m.get("motor") or "", [], f"falhou: {type(ex_).__name__}"
        reg = fechar_missao(licao, ach, licao)
        rel["missoes"].append({"tipo": m["tipo"], "motor": m.get("motor"), "alvo": alvo, "achados": len(ach), "abates": reg["abates"], "licao": licao[:90]})
        _todos_ach.extend(a for a in (ach or []) if isinstance(a, dict))
        rel["abates"] += reg["abates"]; rel["propostas"] += len(ach)
        from .radar_piloto import registrar as _radar
        from .aprendizados_piloto import avaliar as _avaliar, ja_tratado as _ja
        ach = [a for a in ach if not _ja(a.get("url") or a.get("titulo"))]   # não se volta no que já foi abordado
        from .cobertura import ja_coberto as _cob
        from .aprendizados_piloto import quarentenar as _quar
        _sobra = []
        for _a in ach:                                   # o que um motor já vigia não é trabalho do Piloto
            _c, _mid = _cob(_a.get("url") or "")
            if _c:
                _quar(_a, "ja_coberto_por_motor", f"{m.get('motor')}/{m['tipo']} → motor {_mid}")
            else:
                _sobra.append(_a)
        ach = _sobra
        _r = _avaliar(ia, {**m, "licao": licao}, ach)
        rel.setdefault("avaliacoes", []).append(_r["avaliacao"])
        ach = _r["uteis"]                                   # só o que serve entra no sistema
        for a in [x for x in ach if x.get("novo")]:
            with open(PASTA / "alvos_novos.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps({"d": hoje, "motor": m.get("motor"), "titulo": a["titulo"], "onde": a.get("onde") or a.get("url"), "uf": a.get("uf")}, ensure_ascii=False) + "\n")
            _radar(a, alvo, m.get("motor") or "")          # entra no radar de captação como 'a pesquisar' 
    from .missao_especial import devolver_a_fila as _devolver
    _atendidos = {str(m.get("alvo", "")).replace("resgate:", "") for m in (rel.get("missoes") or []) if m.get("tipo") == "resgate"}
    for _m in plano:
        if _m["tipo"] == "resgate" and _m["alvo_id"] not in _atendidos:
            _devolver(_m["alvo_id"], tentado=False)                      # reservado e não atendido volta a aguardar
    from .piloto_ao_vivo import marcar as _vivo2, montar as _vivo_montar
    _vivo2("pousou", detalhe=f"{len(_todos_ach)} achado(s)")
    _pousar_pos(f"voo {rel.get('voo_do_dia')} pousou")
    rel["posicao_ao_vivo"] = _reg_pos()                 # prova de que o anúncio chegou (ou não)
    rel.setdefault("encerrou_por", "tarefa concluída")   # o normal: acabou o que havia para fazer
    rel["minutos_de_voo"] = round((time.time() - t0) / 60, 1)
    from .radar_piloto import publicar as _pub_radar
    rel["radar"] = _pub_radar()
    _todos = _todos_ach
    _fechar(brief, _todos, abertas=sum(1 for a in _todos if a.get("situacao") == "aberta"),
            arquivadas=sum(1 for a in _todos if a.get("situacao") == "arquivada"))
    rel["minutos"] = round((time.time() - t0) / 60, 1)
    rel["bordo"] = resumo()
    rel["ao_vivo"] = _vivo_montar()
    from .aprendizados_piloto import publicar as _pub_apr
    rel["aprendizados"] = _pub_apr()
    from .prospeccao import publicar as _pub_pro
    rel["prospeccao"] = _pub_pro()
    from .reconhecimento import publicar as _pub_rec
    rel["reconhecimento"] = _pub_rec()
    rel["anuncio"] = (f"Esquadrilha {hoje} ({rel['ocupante']}): {len(rel['missoes'])} missão(ões) — "
                      f"{rel['abates']} alvo(s) novo(s) abatido(s), {rel['propostas']} proposta(s) ao todo, {rel['minutos']} min de voo.")
    write_json(PASTA / f"relatorio-{hoje}.json", rel)
    try:
        from .catalogo_terceiro_setor import candidatas_do_catalogo
        rel["candidatas_entregues_ao_interceptador"] = candidatas_do_catalogo()
        from .fontes_novas import agregar_do_catalogo
        rel["fontes_novas_para_os_motores"] = agregar_do_catalogo()
        from .para_claude import montar as _para_claude
        rel["para_o_claude"] = _para_claude()
    except Exception as ex:
        rel["candidatas_entregues_ao_interceptador"] = f"falhou: {type(ex).__name__}"
    write_json(ROOT / "docs/dados/piloto.json", rel)
    return rel


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
