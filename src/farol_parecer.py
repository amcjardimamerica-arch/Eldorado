"""Farol de Alexandria · Parecer com IA — "o que é preciso para vencer".

Acionado pelo botão **Aprimorar análise com IA** de cada edital em aberto.
Produz um parecer detalhado: o que o edital exige, o que falta na associação,
se há enquadramento no banco, e a recomendação (concorrer / regularizar /
descartar). Nunca inventa: o que não está no texto vira ALERTA de dado
faltante para o titular providenciar.

Economia de tokens — modelo adequado a cada tarefa (config/ia.json):
  extração de requisitos ....... modelo rápido e barato (haiku)
  análise de aderência ......... modelo intermediário (sonnet)
  parecer final ................ modelo forte, só no fecho (opus/fable)

O envio é sempre o PACOTE MÍNIMO: trechos do edital que casam com requisito,
perfil público da associação (sem dado pessoal) e o índice de recorrências da
Biblioteca — nunca o edital inteiro nem documentos da associação.

Sem credencial (FAROL_AI_API_KEY), o módulo entrega a PARTE DETERMINÍSTICA do
parecer — exigências detectadas, portão de elegibilidade, prazos e alertas —
e declara que a leitura estratégica aguarda credencial. Jamais simula IA.
"""
from __future__ import annotations

import json
import os
import re
import urllib.request
from datetime import date
from pathlib import Path

from .biblioteca import ASSOCIACOES, OPORTUNIDADES
from .nucleo import ROOT, load_json, now_iso, sha256, slug, write_json

CFG_IA = ROOT / "config/ia.json"
PARECERES = ROOT / "biblioteca_alexandria/pareceres"
USO = ROOT / "estado/ia_uso.jsonl"

_TRECHO = re.compile(
    r"[^.\n]{0,120}(?:exig|requisit|habilita|documenta[çc][ãa]o|ser[áa]\s+"
    r"(?:vedad|permitid)|poder[ãa]o?\s+(?:participar|concorrer)|crit[ée]rio|"
    r"pontua[çc][ãa]o|contrapartida|prazo|inabilit)[^.\n]{0,180}[.\n]", re.I)


def _cfg() -> dict:
    """Reaproveita config/ia.json (formato com env + padrão por papel)."""
    bruto = load_json(CFG_IA) if CFG_IA.exists() else {}
    m = bruto.get("modelos", {})
    def escolher(chave, alternativa):
        spec = m.get(chave) or m.get(alternativa) or {}
        if isinstance(spec, str):
            return spec
        return os.environ.get(spec.get("env", ""), "") or spec.get("padrao") or alternativa
    return {"modelos": {"extracao": escolher("extracao_requisitos", "claude-haiku-4-5"),
                        "analise": escolher("conselheiros", "claude-sonnet-4-5"),
                        "parecer": escolher("parecer_final", "claude-fable-5")},
            "max_chars_edital": bruto.get("max_chars_edital", 60000),
            "max_pareceres_por_execucao": bruto.get("max_pareceres_por_execucao", 2)}


def _chave() -> str | None:
    return os.environ.get("FAROL_AI_API_KEY") or None


def _chamar(modelo: str, sistema: str, prompt: str, max_tokens: int = 1400) -> str:
    chave = _chave()
    if not chave:
        raise RuntimeError("FAROL_AI_API_KEY ausente")
    corpo = json.dumps({"model": modelo, "max_tokens": max_tokens,
                        "system": sistema,
                        "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=corpo,
        headers={"content-type": "application/json", "x-api-key": chave,
                 "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req, timeout=120) as r:
        dados = json.loads(r.read())
    texto = "".join(b.get("text", "") for b in dados.get("content", []))
    with USO.open("a", encoding="utf-8") as h:
        h.write(json.dumps({"em": now_iso(), "modelo": modelo,
                            "uso": dados.get("usage", {})}, ensure_ascii=False) + "\n")
    return texto.strip()


# --------------------------------------------------------------- determinístico
def trechos_relevantes(texto: str, limite: int) -> list[str]:
    """Pacote mínimo: só as frases que tratam de exigência, critério ou prazo."""
    vistos, saida, total = set(), [], 0
    for m in _TRECHO.finditer(texto):
        t = " ".join(m.group(0).split())
        h = sha256(t.lower().encode())[:12]
        if h in vistos or len(t) < 40:
            continue
        vistos.add(h)
        if total + len(t) > limite:
            break
        saida.append(t)
        total += len(t)
    return saida


def portao_deterministico(perfil: dict, texto: str) -> dict:
    """Elegibilidade objetiva antes de gastar token: o que o texto exige e o
    que o perfil comprova. Lacuna nunca vira suposição — vira alerta."""
    exige = {
        "cebas": bool(re.search(r"\bcebas\b", texto, re.I)),
        "cneas": bool(re.search(r"\bcneas\b", texto, re.I)),
        "inscricao_conselho": bool(re.search(r"inscri[çc][ãa]o\s+no\s+conselho", texto, re.I)),
        # aceita "dois anos", "dois (2) anos", "2 (dois) anos", "03 anos"
        "tempo_minimo": bool(re.search(
            r"\b(?:um|dois|tr[êe]s|quatro|cinco|\d{1,2})\s*(?:\([^)]{0,12}\)\s*)?anos?\b",
            texto, re.I)),
        "plano_de_trabalho": bool(re.search(r"plano\s+de\s+trabalho", texto, re.I)),
        "contrapartida": bool(re.search(r"contrapartida", texto, re.I)),
    }
    tem = {c.lower() for c in (perfil.get("certificacoes") or [])}
    atende, faltam, alertas = [], [], []
    for req, exigido in exige.items():
        if not exigido:
            continue
        if req in ("cebas", "cneas") and req in tem:
            atende.append(req)
        elif req in ("cebas", "cneas"):
            faltam.append(req)
        elif req == "tempo_minimo":
            anos = perfil.get("anos_existencia")
            if anos is None:
                alertas.append("tempo de existência não consta do perfil público")
            elif anos < 2:
                faltam.append("tempo mínimo de existência")
            else:
                atende.append("tempo mínimo de existência")
        else:
            alertas.append(f"{req.replace('_', ' ')}: exigido no edital — confirmar")
    return {"exigencias_detectadas": [k for k, v in exige.items() if v],
            "atende": atende, "faltam": faltam, "alertas": alertas,
            "bloqueio_objetivo": bool(faltam)}


# ------------------------------------------------------------------- parecer
def gerar(chave_edital: str, ano: str, assoc_slug: str | None = None) -> dict:
    """Parecer de um edital. Devolve a parte determinística sempre; a leitura
    estratégica só quando há credencial."""
    ficha_path = OPORTUNIDADES / chave_edital / ano / "ficha.json"
    if not ficha_path.exists():
        raise FileNotFoundError(f"edital não está na Biblioteca: {chave_edital}/{ano}")
    ficha = load_json(ficha_path)
    texto = (ficha_path.parent / "edital.txt").read_text(encoding="utf-8", errors="ignore")

    assocs = []
    idx = ASSOCIACOES / "indice.json"
    if idx.exists():
        assocs = load_json(idx).get("associacoes", [])
    if assoc_slug:
        assocs = [a for a in assocs if a["slug"] == assoc_slug]

    cfg = _cfg()
    trechos = trechos_relevantes(texto, cfg.get("max_chars_edital", 60000) // 4)
    historico = {}
    if (OPORTUNIDADES / "indice.json").exists():
        i = load_json(OPORTUNIDADES / "indice.json")
        historico = {"exigencias_mais_cobradas": i.get("exigencias_mais_cobradas", [])[:12],
                     "recorrencias": i.get("recorrencias", [])[:8]}

    avaliacoes = []
    for a in assocs:
        perfil_path = ASSOCIACOES / a["slug"] / "perfil_publico.json"
        perfil = load_json(perfil_path) if perfil_path.exists() else {}
        avaliacoes.append({"associacao": a["nome"], "slug": a["slug"],
                           **portao_deterministico(perfil, texto)})

    parecer = {
        "edital": {"chave": chave_edital, "ano": ano, "titulo": ficha.get("titulo"),
                   "fonte": ficha.get("fonte_nome"), "inicio": ficha.get("inicio"),
                   "fim": ficha.get("fim"), "modelos": ficha.get("modelos", [])},
        "gerado_em": now_iso(),
        "portao": avaliacoes,
        "trechos_analisados": len(trechos),
        "historico_consultado": historico,
        "ia": None,
        "recomendacao": None,
        "alertas": sorted({al for av in avaliacoes for al in av["alertas"]}),
    }

    if not _chave():
        parecer["ia"] = {"status": "aguardando credencial FAROL_AI_API_KEY",
                         "nota": ("análise determinística concluída; a leitura "
                                  "estratégica com IA roda assim que a credencial "
                                  "for configurada — nada é simulado")}
        bloqueado = all(av["bloqueio_objetivo"] for av in avaliacoes) if avaliacoes else False
        parecer["recomendacao"] = ("descartar — requisito eliminatório não atendido"
                                   if bloqueado else "aguardando análise de IA")
    else:
        modelos = cfg["modelos"]
        sistema = ("Você analisa editais para organizações da sociedade civil no Brasil. "
                   "Responda SOMENTE com base nos trechos fornecidos. Nunca invente "
                   "exigência, valor, prazo ou critério: o que não constar deve ser "
                   "listado como dado faltante. Escreva em português do Brasil.")
        req = _chamar(modelos["extracao"], sistema,
                      "Extraia os REQUISITOS e CRITÉRIOS DE PONTUAÇÃO destes trechos "
                      "de edital, em JSON com as chaves requisitos[], pontuacao[], "
                      "documentos[] e faltantes[]. Só JSON.\n\n" + "\n".join(trechos),
                      max_tokens=1600)
        analise = _chamar(modelos["analise"], sistema,
                          "Com os requisitos extraídos e o portão determinístico já "
                          "calculado, avalie a aderência de cada associação e o que "
                          "precisa ser providenciado.\n\nREQUISITOS:\n" + req[:6000] +
                          "\n\nPORTÃO:\n" + json.dumps(avaliacoes, ensure_ascii=False) +
                          "\n\nHISTÓRICO DE RECORRÊNCIAS:\n" +
                          json.dumps(historico, ensure_ascii=False)[:3000],
                          max_tokens=1800)
        final = _chamar(modelos["parecer"], sistema,
                        "Redija o parecer final ao presidente da associação, em "
                        "português simples: (1) o que este edital exige para vencer; "
                        "(2) há enquadramento de alguma associação do banco? (3) o que "
                        "falta providenciar, em lista objetiva; (4) recomendação: "
                        "CONCORRER, REGULARIZAR ANTES ou DESCARTAR, com o motivo.\n\n"
                        + analise[:8000], max_tokens=2000)
        parecer["ia"] = {"status": "concluído", "requisitos": req,
                         "analise": analise, "parecer": final,
                         "modelos": modelos}
        m = re.search(r"\b(CONCORRER|REGULARIZAR ANTES|DESCARTAR)\b", final.upper())
        parecer["recomendacao"] = m.group(1).lower() if m else "ver parecer"

    destino = PARECERES / chave_edital / ano
    write_json(destino / "parecer.json", parecer)
    if parecer.get("ia", {}).get("parecer"):
        (destino / "parecer.md").write_text(parecer["ia"]["parecer"], encoding="utf-8")
    return parecer


def fila_de_pedidos() -> list[dict]:
    """Pedidos do botão 'Aprimorar análise com IA' (arquivo versionado)."""
    f = ROOT / "estado/pedidos_parecer.json"
    return load_json(f).get("pedidos", []) if f.exists() else []


def run(limite: int | None = None) -> dict:
    cfg = _cfg()
    limite = limite or cfg.get("max_pareceres_por_execucao", 2)
    feitos, erros = [], []
    for pedido in fila_de_pedidos()[:limite]:
        try:
            p = gerar(pedido["chave"], pedido["ano"], pedido.get("associacao"))
            feitos.append({"chave": pedido["chave"], "ano": pedido["ano"],
                           "recomendacao": p["recomendacao"]})
        except Exception as exc:
            erros.append({"pedido": pedido, "erro": f"{type(exc).__name__}: {exc}"})
    return {"executado_em": now_iso(), "pareceres": feitos, "erros": erros,
            "credencial": bool(_chave())}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
