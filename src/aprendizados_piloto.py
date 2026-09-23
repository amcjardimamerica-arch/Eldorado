"""APRENDIZADOS DO PILOTO — o que não deu certo fica aqui, fora do sistema.

Regra de ouro: **só informação correta entra na Biblioteca**. Insucesso não se apaga nem se
mistura ao acervo — vai para a pasta própria do Piloto, onde serve de base para melhorar e
não contamina o que é bom.

    estado/piloto/aprendizados/
        avaliacoes/     o julgamento de cada missão: serviu? por quê não?
        quarentena/     achados sem efetividade, com o motivo do descarte
        licoes.json     o que o Piloto aprendeu, em forma de regra
        tratados.json   editais que o Piloto já abordou — não se volta neles
        melhorias.json  o que ele sugere para os motores de busca

Depois de cada missão o Piloto julga o que trouxe e, quando não trouxe nada, **diz o motivo
do insucesso**. A cada 3 dias o Claude lê tudo isso, aplica as correções e limpa o que ficou.
"""
from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta, timezone
import pathlib
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json

# A BASE PODE SER REDIRECIONADA. Sem isto os testes escreviam na base de produção: em 23/09
# havia 568 avaliações para 60 missões reais, e as estatísticas não valiam nada. Os testes
# apontam ELDORADO_APRENDIZADOS para uma pasta temporária e a base real fica intocada.
import os as _os
PASTA = pathlib.Path(_os.environ["ELDORADO_APRENDIZADOS"]) if _os.environ.get("ELDORADO_APRENDIZADOS") \
        else ROOT / "estado/piloto/aprendizados"
AVAL = PASTA / "avaliacoes"
QUAR = PASTA / "quarentena"
LICOES = PASTA / "licoes.json"
TRATADOS = PASTA / "tratados.json"
MELHORIAS = PASTA / "melhorias.json"
PUB = ROOT / "docs/dados/aprendizados_piloto.json"

# MOTORES DE ENSAIO: nomes usados pelos testes. Nada que venha deles entra na base real —
# em 23/09 as estatísticas apareceram com 26 missões de 'm-teste', 'm-seco' e 'm-repete',
# que não existem, e qualquer leitura daquela base estava errada.
ENSAIO = ("m-teste", "m-seco", "m-repete", "teste", "lab", "lab-motor", "ensaio-motor", "m-")

def _e_ensaio(motor: str) -> bool:
    m = str(motor or "").lower()
    return m in ENSAIO or m.startswith("m-teste") or m.startswith("m-seco") or m.startswith("m-repete")


MOTIVOS = {
    "busca_vazia": "o buscador não devolveu nada (bloqueio ou rede)",
    "nada_no_crivo": "vieram resultados, mas nenhum era oportunidade de verdade",
    "pagina_nao_confirma": "a página aberta não confirmou o que o resultado prometia",
    "fora_do_objeto": "o que veio não serve à finalidade da associação",
    "sem_prazo": "não há data escrita na página — não dá para saber se está aberto",
    "ja_conhecido": "já estava no acervo",
    "fonte_sem_mapa": "o site não publica sitemap nem listagem legível",
    "modelo_mudo": "o modelo local não respondeu ao pedido",
    "ja_coberto_por_motor": "a fonte já é lida todo dia por um motor — não é trabalho do Piloto",
}


def _garantir() -> None:
    for d in (PASTA, AVAL, QUAR):
        d.mkdir(parents=True, exist_ok=True)


def tratados() -> dict:
    return load_json(TRATADOS) if TRATADOS.exists() else {"itens": {}}


def ja_tratado(chave: str) -> bool:
    """O Piloto não volta ao que já abordou — a avaliação daquilo é do Claude."""
    return str(chave) in (tratados().get("itens") or {})


def marcar_tratado(chave: str, titulo: str, desfecho: str, motivo: str = "") -> None:
    _garantir()
    d = tratados()
    d.setdefault("itens", {})[str(chave)] = {
        "titulo": (titulo or "")[:120], "desfecho": desfecho, "motivo": motivo,
        "em": date.today().isoformat(),
        "entregue_ao_claude": desfecho != "aproveitado",
        "nota": "o Piloto não volta neste; quem avalia agora é o Claude"}
    d["em"] = now_iso()
    write_json(TRATADOS, d)


def quarentenar(achado: dict, motivo: str, missao: str = "") -> None:
    """Achado sem efetividade sai do caminho do sistema e fica guardado como matéria de estudo."""
    _garantir()
    arq = QUAR / f"{date.today().isoformat()}.jsonl"
    with open(arq, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"em": now_iso()[:19], "missao": missao, "motivo": motivo,
                             "explicacao": MOTIVOS.get(motivo, motivo),
                             "titulo": (achado.get("titulo") or "")[:120], "url": achado.get("url"),
                             "trecho": (achado.get("trecho") or "")[:140]}, ensure_ascii=False) + "\n")


def avaliar(ia, missao: dict, achados: list[dict]) -> dict:
    """Depois de cada missão: o que veio serve? Se não veio nada, por quê? E o que melhorar
    no motor que foi usado?"""
    _garantir()
    motor = missao.get("motor") or missao.get("alvo") or "?"
    licao = missao.get("licao") or ""
    uteis, descartados = [], []

    if achados:
        r = ia.perguntar(
            f"MOTOR USADO: {motor}\nMISSÃO: {missao.get('tipo')}\n"
            f"ACHADOS:\n{json.dumps([{'n': i, 'titulo': a.get('titulo'), 'url': a.get('url'), 'trecho': (a.get('trecho') or '')[:140]} for i, a in enumerate(achados[:10])], ensure_ascii=False)}\n\n"
            "Somos uma associação de moradores que atua em assistência social e cultura e procura "
            "RECURSO: edital, patrocínio, doação de empresa, incentivo fiscal.\n"
            "Para cada achado diga se SERVE (é recurso a que podemos concorrer) ou NÃO SERVE, e por quê. "
            "Seja severo: um achado que não dá para transformar em inscrição não serve.",
            '{"itens": [{"n": 0, "serve": true, "porque": "uma frase"}], '
            '"o_que_melhorar_no_motor": "uma sugestão concreta para este motor achar melhor"}')
        julg = {int(x.get("n", -1)): x for x in ((r or {}).get("itens") or []) if isinstance(x, dict)}
        for i, a in enumerate(achados[:10]):
            j = julg.get(i) or {}
            if j.get("serve"):
                uteis.append({**a, "porque_serve": str(j.get("porque") or "")[:140]})
            else:
                motivo = "fora_do_objeto" if j else "nada_no_crivo"
                descartados.append({**a, "porque_nao": str(j.get("porque") or MOTIVOS[motivo])[:140]})
                quarentenar(a, motivo, f"{motor}/{missao.get('tipo')}")
        sugestao = str((r or {}).get("o_que_melhorar_no_motor") or "")[:220]
    else:
        sugestao = ""

    motivo = _motivo_do_insucesso(licao, achados, uteis)
    if _e_ensaio(motor):                      # missão de ensaio não entra na base
        return {"avaliacao": {"motor": motor, "ensaio": True, "uteis": len(uteis),
                              "nota": "missão de ensaio — não gravada na base"}, "uteis": uteis}
    av = {"em": now_iso(), "motor": motor, "missao": missao.get("tipo"), "alvo": missao.get("alvo"),
          "achados": len(achados), "uteis": len(uteis), "descartados": len(descartados),
          "efetividade": round(len(uteis) / len(achados), 2) if achados else 0.0,
          "motivo_do_insucesso": motivo if not uteis else None,
          "explicacao": MOTIVOS.get(motivo, motivo) if not uteis else None,
          "melhoria_sugerida": sugestao, "licao_do_voo": licao[:200]}
    write_json(AVAL / f"{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{re.sub(r'[^a-z0-9]+', '-', motor.lower())[:24]}.json", av)

    for a in uteis + descartados:                    # abordado é abordado: não se volta nele
        marcar_tratado(a.get("url") or a.get("titulo"), a.get("titulo") or "",
                       "aproveitado" if a in uteis else "descartado",
                       a.get("porque_serve") or a.get("porque_nao") or "")
    if sugestao:
        _guardar_melhoria(motor, sugestao, av["efetividade"])
    if not uteis:
        _guardar_licao(motor, motivo, missao.get("tipo") or "")
    return {"avaliacao": av, "uteis": uteis}


def _motivo_do_insucesso(licao: str, achados: list, uteis: list) -> str:
    l = (licao or "").lower()
    if uteis:
        return ""
    if "não devolveu resultado" in l or "nao devolveu" in l:
        return "busca_vazia"
    if "nenhum passou no crivo" in l:
        return "nada_no_crivo"
    if "não achei a página oficial" in l:
        return "pagina_nao_confirma"
    if "modelo" in l and ("mudo" in l or "não respondeu" in l):
        return "modelo_mudo"
    if achados and not uteis:
        return "fora_do_objeto"
    return "nada_no_crivo"


def _guardar_licao(motor: str, motivo: str, tipo: str) -> None:
    if _e_ensaio(motor):
        return
    d = load_json(LICOES) if LICOES.exists() else {"itens": {}}
    k = f"{motor}|{motivo}"
    it = d.setdefault("itens", {}).setdefault(k, {"motor": motor, "motivo": motivo, "vezes": 0, "tipos": []})
    it["vezes"] += 1
    it["ultima"] = date.today().isoformat()
    if tipo and tipo not in it["tipos"]:
        it["tipos"].append(tipo)
    it["explicacao"] = MOTIVOS.get(motivo, motivo)
    if it["vezes"] >= 3:
        it["regra"] = f"o motor '{motor}' falha por {MOTIVOS.get(motivo, motivo)} há {it['vezes']} vezes — precisa de correção, não de mais tentativas"
    d["em"] = now_iso()
    write_json(LICOES, d)


def _guardar_melhoria(motor: str, sugestao: str, efetividade: float) -> None:
    if _e_ensaio(motor):
        return
    d = load_json(MELHORIAS) if MELHORIAS.exists() else {"itens": []}
    d.setdefault("itens", []).insert(0, {"motor": motor, "sugestao": sugestao,
                                         "efetividade_na_hora": efetividade, "em": now_iso()[:16],
                                         "aplicada": False})
    d["itens"] = d["itens"][:120]
    d["em"] = now_iso()
    write_json(MELHORIAS, d)


def faxina(dias: int = 3) -> dict:
    """A cada 3 dias: quarentena velha sai, lições viram regra, o sistema fica só com o que presta."""
    _garantir()
    corte = (date.today() - timedelta(days=dias)).isoformat()
    apagados, guardados = 0, 0
    for arq in sorted(QUAR.glob("*.jsonl")):
        if arq.stem < corte:
            guardados += sum(1 for _ in open(arq, encoding="utf-8"))
            arq.unlink()
            apagados += 1
    velhas = [a for a in sorted(AVAL.glob("*.json")) if a.stem[:8] < corte.replace("-", "")]
    resumo_velhas = {}
    for a in velhas:
        v = load_json(a)
        k = v.get("motivo_do_insucesso") or "com_resultado"
        resumo_velhas[k] = resumo_velhas.get(k, 0) + 1
        a.unlink()
    d = load_json(LICOES) if LICOES.exists() else {"itens": {}}
    d["ultima_faxina"] = {"em": now_iso(), "dias": dias, "arquivos_de_quarentena_apagados": apagados,
                          "achados_descartados_removidos": guardados,
                          "avaliacoes_resumidas": resumo_velhas}
    write_json(LICOES, d)
    publicar()
    return d["ultima_faxina"]


def publicar() -> dict:
    _garantir()
    lic = load_json(LICOES) if LICOES.exists() else {"itens": {}}
    mel = load_json(MELHORIAS) if MELHORIAS.exists() else {"itens": []}
    trat = tratados().get("itens") or {}
    avs = [load_json(a) for a in sorted(AVAL.glob("*.json"), reverse=True)[:40]]
    por_motor: dict[str, dict] = {}
    for v in avs:
        m = por_motor.setdefault(v.get("motor") or "?", {"missoes": 0, "achados": 0, "uteis": 0, "motivos": {}})
        m["missoes"] += 1
        m["achados"] += v.get("achados") or 0
        m["uteis"] += v.get("uteis") or 0
        if v.get("motivo_do_insucesso"):
            m["motivos"][v["motivo_do_insucesso"]] = m["motivos"].get(v["motivo_do_insucesso"], 0) + 1
    for m in por_motor.values():
        m["efetividade"] = round(m["uteis"] / m["achados"], 2) if m["achados"] else 0.0
    saida = {"em": now_iso(),
             "regra": "só informação correta entra na Biblioteca; insucesso fica na pasta do Piloto",
             "por_motor": por_motor,
             "licoes": sorted((lic.get("itens") or {}).values(), key=lambda x: -x.get("vezes", 0))[:20],
             "melhorias_pendentes": [x for x in (mel.get("itens") or []) if not x.get("aplicada")][:20],
             "editais_tratados": len(trat),
             "entregues_ao_claude": sum(1 for v in trat.values() if v.get("entregue_ao_claude")),
             "ultima_faxina": lic.get("ultima_faxina")}
    write_json(PUB, saida)
    return {k: v for k, v in saida.items() if k not in ("licoes", "melhorias_pendentes")}


if __name__ == "__main__":
    import sys
    print(json.dumps(faxina() if "faxina" in sys.argv else publicar(), ensure_ascii=False, indent=1))
