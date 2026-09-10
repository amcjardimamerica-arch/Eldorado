"""FLUXO DE VERIFICAÇÃO DO EDITAL — do motor à confirmação, com uma etapa honesta de espera.

O que este módulo resolve: o motor descobre o edital, mas nem sempre consegue
confirmá-lo. Antes, esses registros ficavam para sempre em "possível/em
verificação", sem que ninguém soubesse *o que* faltava nem *quem* poderia
resolver. Agora cada registro tem uma etapa nomeada e, quando o robô esgota o
que pode fazer, ele diz isso — e passa a tarefa adiante.

  1 DESCOBERTO ................ o motor viu o registro (título, órgão, vetor)
  2 EM COLETA .................. o robô está tentando obter o documento
  3 AGUARDANDO AÇÃO EXTERNA .... o robô esgotou o que consegue fazer sozinho;
                                 falta uma leitura no navegador do titular
  4 VERIFICADO ................. objeto, prazo e página oficial confirmados
  5 CLASSIFICADO ............... com parecer e selo (conformidade/inconformidade)

O motivo de parada é sempre escrito: portal recusa IP estrangeiro, PDF é
imagem, edital não publicou cronograma, site exige navegador, e assim por
diante. É esse motivo que vira a instrução da rodada externa.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json

ETAPAS = {1: "descoberto", 2: "em coleta", 3: "aguardando ação externa", 4: "verificado", 5: "classificado"}

# por que o robô parou — e o que a ação externa precisa fazer
MOTIVOS = {
    "ip_estrangeiro": ("o portal recusa o robô do GitHub (IP fora do Brasil)",
                       "abrir no navegador do titular, com IP brasileiro"),
    "pdf_imagem": ("o PDF anexado é digitalização sem camada de texto",
                   "rodar OCR no navegador (tesseract + pdf.js) ou pedir o arquivo ao órgão"),
    "sem_cronograma": ("o próprio edital não publicou cronograma",
                       "confirmar com o órgão; se não houver data, o campo fica nulo em definitivo"),
    "exige_navegador": ("a página monta o conteúdo por JavaScript e não entrega nada ao robô",
                        "abrir no navegador, que executa o script"),
    "so_vetor": ("só existe o anúncio no PNCP/diário; o site do órgão não foi localizado",
                 "procurar o site oficial do órgão e localizar o edital"),
    "portal_fora": ("o portal do órgão não respondeu",
                    "tentar de novo mais tarde ou pedir o documento por e-mail/LAI"),
    "formato_fechado": ("o arquivo está em formato proprietário (.doc binário, .rar, RTF)",
                        "abrir localmente e transcrever o objeto e o cronograma"),
}


def _motivo_de_parada(e: dict, ex: dict) -> str | None:
    """Deduz por que o robô não conseguiu confirmar — sempre com base no que ficou registrado."""
    erros = " ".join(str(x) for x in (ex.get("erros") or []))
    obs = " ".join(str((ex.get("verificacao_externa") or {}).get("observacao") or "") for _ in (1,))
    alvo = f"{erros} {obs} {(ex.get('mini_parecer') or '')}"
    if re.search(r"imagem|digitaliza|sem camada de texto|ocr", alvo, re.I):
        return "pdf_imagem"
    if re.search(r"n[ãa]o (traz|publicou) cronograma|sem cronograma|coluna de datas", alvo, re.I):
        return "sem_cronograma"
    if re.search(r"javascript|aplica[çc][ãa]o js|exige navegador|renderiza", alvo, re.I):
        return "exige_navegador"
    if re.search(r"\.doc\b|\.rar\b|rtf|formato n[ãa]o extra", alvo, re.I):
        return "formato_fechado"
    if re.search(r"fora do ar|n[ãa]o respondeu|timeout|conex[ãa]o", alvo, re.I):
        return "portal_fora"
    dom = (e.get("url") or "") + " " + (ex.get("site_institucional") or "")
    if re.search(r"tjgo\.jus\.br|goiania\.go\.gov\.br|goias\.gov\.br|mpgo\.mp\.br|goiania\.go\.leg\.br", dom, re.I):
        return "ip_estrangeiro"
    if re.search(r"pncp\.gov\.br|queridodiario|diariooficial|in\.gov\.br", e.get("url") or ""):
        return "so_vetor"
    return None


def etapa_de_verificacao(e: dict, ex: dict | None = None, analise: dict | None = None) -> dict:
    """Etapa do registro no fluxo de verificação, com o motivo da parada quando houver."""
    ex = ex or {}
    if analise:
        return {"etapa_verificacao": 5, "rotulo": ETAPAS[5], "selo": analise.get("selo"),
                "por": analise.get("por"), "em": (analise.get("em") or "")[:10]}
    itens = ex.get("itens") or {}
    tem_prazo = bool(itens.get("Prazo de inscrição") or e.get("fim"))
    tem_objeto = bool(itens.get("Objeto") or e.get("objeto"))
    pag = ex.get("pagina_divulgacao") or e.get("pagina_divulgacao")
    tem_site = bool(pag) and not re.search(r"pncp\.gov|queridodiario|in\.gov\.br|diariooficial|observatorio3setor|captadores\.org", str(pag), re.I)
    if tem_prazo and tem_objeto and tem_site:
        return {"etapa_verificacao": 4, "rotulo": ETAPAS[4]}
    tentou = bool(ex.get("tentativas") or ex.get("fontes") or ex.get("erros"))
    motivo = _motivo_de_parada(e, ex)
    if motivo or (tentou and not tem_prazo):
        m = motivo or "so_vetor"
        desc, acao = MOTIVOS[m]
        return {"etapa_verificacao": 3, "rotulo": ETAPAS[3], "motivo": m, "motivo_texto": desc,
                "acao_externa": acao,
                "falta": [k for k, v in (("objeto", tem_objeto), ("prazo", tem_prazo), ("página oficial", tem_site)) if not v]}
    if tentou:
        return {"etapa_verificacao": 2, "rotulo": ETAPAS[2]}
    return {"etapa_verificacao": 1, "rotulo": ETAPAS[1]}


def run() -> dict:
    """Percorre o universo e produz o painel do fluxo + a fila da ação externa."""
    from .fonte_edital import EXTRAIDOS
    dados = load_json(ROOT / "docs/dashboard-dados.json")
    an = load_json(ROOT / "dados/editais/analises.json") if (ROOT / "dados/editais/analises.json").exists() else {}
    universo = list(dados.get("editais") or [])
    ab = ROOT / "docs/dados/abertas.json"
    if ab.exists():
        try:
            from .compacto import expandir
            vistos = {x["id"] for x in universo}
            universo += [o for o in expandir(load_json(ab)) if o.get("id") not in vistos]
        except Exception:
            pass
    universo = [e for e in universo if e.get("tipo_registro") in ("edital", "regra_anual")]
    por_etapa: dict = {}
    externa = []
    for e in universo:
        arq = EXTRAIDOS / f"{e['id']}.json"
        ex = load_json(arq) if arq.exists() else {}
        r = etapa_de_verificacao(e, ex, an.get(e["id"]))
        por_etapa.setdefault(r["etapa_verificacao"], []).append(e["id"])
        if r["etapa_verificacao"] == 3:
            externa.append({"id": e["id"], "titulo": (e.get("titulo") or "")[:120], "uf": e.get("uf"),
                            "motivo": r["motivo"], "motivo_texto": r["motivo_texto"], "acao": r["acao_externa"],
                            "falta": r["falta"], "link": e.get("pagina_divulgacao") or e.get("url")})
    ordem = {"ip_estrangeiro": 0, "so_vetor": 1, "exige_navegador": 2, "pdf_imagem": 3,
             "portal_fora": 4, "formato_fechado": 5, "sem_cronograma": 6}
    externa.sort(key=lambda x: (ordem.get(x["motivo"], 9), str(x.get("uf") or "")))
    res = {"em": now_iso(), "etapas": ETAPAS,
           "totais": {ETAPAS[k]: len(v) for k, v in sorted(por_etapa.items())},
           "aguardando_acao_externa": {"total": len(externa),
                                       "por_motivo": {m: sum(1 for x in externa if x["motivo"] == m) for m in ordem if any(x["motivo"] == m for x in externa)},
                                       "itens": externa[:400]},
           "regra": "o robô faz o que consegue; quando esgota, o registro fica em 'aguardando ação externa' com o motivo escrito "
                    "e a instrução da rodada no navegador. A verificação manual devolve o arquivo pela conversa e o sistema inteiro se atualiza."}
    write_json(ROOT / "estado/fluxo_verificacao.json", res)
    write_json(ROOT / "docs/dados/fluxo_verificacao.json", res)
    return {k: v for k, v in res.items() if k not in ("etapas",)} | {"aguardando_acao_externa": {k: v for k, v in res["aguardando_acao_externa"].items() if k != "itens"}}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
