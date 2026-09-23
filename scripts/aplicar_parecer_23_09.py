#!/usr/bin/env python3
"""APLICAR A ATUALIZAÇÃO DO PARECER — 23/09/2026.

O pacote traz três blocos, e cada um tem um destino diferente. A diferença entre eles é o que
evita que o trabalho de reverificação se perca na próxima rodada:

    ATUALIZAR   19 registros reconfirmados HOJE na fonte. O prazo e o alcance passam a valer,
                com a data da confirmação gravada. Sem isso o sistema reverifica amanhã o que
                foi verificado hoje.

    EXCLUIR    409 reprovados por objeto — não são edital de fomento a OSC. Saem da fila e do
                painel, mas NÃO somem: ficam marcados com o motivo, porque um registro que
                desaparece sem rastro volta pela mesma porta na próxima varredura.

    REBAIXAR   238 fora da abrangência aprovada (nacional + GO + Goiânia). Não são erro: são
                editais legítimos de outros municípios. Saem da fila, ficam no acervo, e
                voltam sozinhos se a abrangência mudar.

Nada é apagado do disco. Marcar é reversível; apagar não é, e quem apaga perde a capacidade
de explicar por que aquele registro não está mais lá.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

PACOTE = Path("/home/claude/parecer/PARECER-OPORTUNIDADES-2026-09-23/ATUALIZACAO-SISTEMA-2026-09-23.json")
OPORT = RAIZ / "biblioteca_alexandria/oportunidades"
REGISTRO = RAIZ / "estado/parecer_23_09_aplicado.json"


# O ACERVO VIVE EM DOIS LUGARES, e a primeira tentativa achou só 26% dos registros por
# procurar num deles. As fichas da Biblioteca são a vitrine; o acervo de trabalho, com a
# análise e a marcação de cada edital, está em dados/editais. Marcar só a vitrine deixaria
# o registro vivo onde o motor lê — e ele voltaria na varredura seguinte.
ANALISES = RAIZ / "dados/editais/analises.json"
MARCACOES = RAIZ / "dados/editais/marcacoes_ia.json"
EXTRAIDOS = RAIZ / "dados/editais/extraidos"


def indexar() -> dict[str, Path]:
    """id → ficha da Biblioteca. São 19 mil; varrer uma vez e guardar o mapa."""
    mapa = {}
    for f in OPORT.glob("*/*/ficha.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if d.get("id"):
            mapa[d["id"]] = f
    return mapa


def aplicar(seco: bool = False) -> dict:
    p = json.loads(PACOTE.read_text(encoding="utf-8"))
    mapa = indexar()
    an = json.loads(ANALISES.read_text(encoding="utf-8")) if ANALISES.exists() else {}
    mc = json.loads(MARCACOES.read_text(encoding="utf-8")) if MARCACOES.exists() else {}
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    res = {"em": agora, "seco": seco, "fonte": PACOTE.name,
           "regra": p.get("regra"), "abrangencia": p.get("abrangencia_aprovada"),
           "atualizados": 0, "excluidos": 0, "rebaixados": 0,
           "nao_encontrados": {"atualizar": [], "excluir": [], "rebaixar": []}}

    def salvar(f: Path, d: dict):
        if not seco:
            f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")

    def marcar(cid: str, campos: dict) -> bool:
        """Marca nos DOIS acervos: a ficha da Biblioteca, se houver, e o registro de trabalho.
        Basta existir num deles para o registro contar como alcançado."""
        tocou = False
        f = mapa.get(cid)
        if f:
            d = json.loads(f.read_text(encoding="utf-8"))
            d.update(campos)
            salvar(f, d)
            tocou = True
        for base in (an, mc):
            if cid in base and isinstance(base[cid], dict):
                base[cid].update(campos)
                tocou = True
        e = EXTRAIDOS / f"{cid}.json"
        if e.exists():
            try:
                d = json.loads(e.read_text(encoding="utf-8"))
                d.update(campos)
                if not seco:
                    e.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
                tocou = True
            except Exception:
                pass
        return tocou

    # 1 · ATUALIZAR — o que foi reconfirmado na fonte hoje
    for cid, novo in (p.get("atualizar") or {}).items():
        campos = {k: v for k, v in novo.items() if v is not None}
        campos["reverificado_em"] = novo.get("fim_confirmado_em") or agora[:10]
        campos["reverificado_por"] = "parecer de oportunidades 23/09 — leitura da fonte"
        if marcar(cid, campos):
            res["atualizados"] += 1
        else:
            res["nao_encontrados"]["atualizar"].append(cid)

    # 2 · EXCLUIR — reprovado por objeto. Marcado, não apagado.
    for cid, info in (p.get("excluir") or {}).items():
        if marcar(cid, {"fora_do_objeto": True, "ativo": False,
                        "excluido_em": agora[:10], "excluido_porque": info.get("motivo"),
                        "familia_do_objeto": info.get("familia"),
                        "excluido_por": "parecer de oportunidades 23/09",
                        "reversivel": "marcado, não apagado: some da fila e do painel, fica no acervo"}):
            res["excluidos"] += 1
        else:
            res["nao_encontrados"]["excluir"].append(cid)

    # 3 · REBAIXAR — fora da abrangência. Legítimo, só não é nosso.
    for cid, info in (p.get("rebaixar") or {}).items():
        if marcar(cid, {"alcance": "fora_de_abrangencia", "ativo": False,
                        "rebaixado_em": agora[:10], "rebaixado_porque": info.get("motivo"),
                        "uf_do_edital": info.get("uf"),
                        "volta_se": "a abrangência aprovada passar a incluir esta UF ou município"}):
            res["rebaixados"] += 1
        else:
            res["nao_encontrados"]["rebaixar"].append(cid)

    res["nao_encontrados_total"] = sum(len(v) for v in res["nao_encontrados"].values())
    if not seco:
        ANALISES.write_text(json.dumps(an, ensure_ascii=False, indent=1), encoding="utf-8")
        MARCACOES.write_text(json.dumps(mc, ensure_ascii=False, indent=1), encoding="utf-8")
        REGISTRO.parent.mkdir(parents=True, exist_ok=True)
        REGISTRO.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    return res


if __name__ == "__main__":
    r = aplicar(seco="--seco" in sys.argv)
    print(json.dumps({k: v for k, v in r.items() if k != "nao_encontrados"},
                     ensure_ascii=False, indent=1))
    if r["nao_encontrados_total"]:
        print(f"\n{r['nao_encontrados_total']} id(s) do pacote não existem no acervo:")
        for bloco, ids in r["nao_encontrados"].items():
            if ids:
                print(f"  {bloco}: {len(ids)} — {', '.join(ids[:4])}{'...' if len(ids) > 4 else ''}")
