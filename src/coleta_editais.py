"""COLETA DIRIGIDA — baixa o documento do edital na FONTE OFICIAL.

Percorre a fila de verificação (modo completo: nacionais e Goiás), abre o link
oficial de cada oportunidade — nunca o vetor de divulgação nem a página do
veículo — e guarda o texto compacto para a análise ler. Só isso: não interpreta,
não infere prazo. O que não abrir fica registrado com o motivo.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json
from .fonte_edital import obter_texto, EXTRAIDOS, TEXTOS

VEICULO = re.compile(r"observatorio3setor|captadores\.org|bussolasocial|prosas\.com|mapaosc|filantropia\.ong|gife\.org|pncp\.gov|queridodiario|in\.gov\.br|diariooficial", re.I)


def run(limite: int = 25, modo: str = "completo") -> dict:
    fila = ROOT / "estado/fila_verificacao.json"
    if not fila.exists():
        return {"erro": "fila não gerada"}
    itens = [x for x in load_json(fila)["itens"] if x.get("modo") == modo]
    feitos, sem_texto, ja = [], [], 0
    for it in itens:
        if len(feitos) + len(sem_texto) >= limite:
            break
        if (TEXTOS / f"{it['id']}.txt.gz").exists():
            ja += 1; continue
        alvo = it.get("link_oficial")
        if not alvo or VEICULO.search(alvo):
            sem_texto.append({"id": it["id"], "titulo": it["titulo"][:80], "motivo": "sem link oficial fora de vetor/veículo — a fonte precisa ser localizada"})
            continue
        e = {"id": it["id"], "titulo": it["titulo"], "url": alvo, "fonte_nome": it.get("fonte"), "uf": it.get("uf")}
        try:
            ob = obter_texto(e, maximo_pdfs=3)
        except Exception as exc:
            sem_texto.append({"id": it["id"], "titulo": it["titulo"][:80], "motivo": f"{type(exc).__name__} ao abrir {alvo[:60]}"}); continue
        if ob.get("texto"):
            arq = EXTRAIDOS / f"{it['id']}.json"
            reg = load_json(arq) if arq.exists() else {"edital_id": it["id"], "titulo": it["titulo"], "tentativas": []}
            reg.update({k: ob[k] for k in ("arquivo", "kb_compacto", "fontes", "site_institucional", "pagina_divulgacao", "erros", "anexos") if k in ob})
            reg["coletado_em"] = now_iso(); write_json(arq, reg)
            feitos.append({"id": it["id"], "titulo": it["titulo"][:80], "kb": ob["kb_compacto"], "arquivos": len(ob.get("fontes") or [])})
        else:
            sem_texto.append({"id": it["id"], "titulo": it["titulo"][:80], "motivo": "; ".join((ob.get("erros") or ["fonte não entregou documento"])[:2])})
    res = {"em": now_iso(), "modo": modo, "com_texto_agora": len(feitos), "sem_texto": len(sem_texto), "ja_tinham": ja,
           "obtidos": feitos, "falhas": sem_texto[:40],
           "regra": "só a fonte oficial: vetores (PNCP, diários) e veículos (portais de notícia do terceiro setor) nunca são guardados como edital"}
    write_json(ROOT / "estado/coleta_editais.json", res)
    return {k: v for k, v in res.items() if k not in ("obtidos", "falhas")}


if __name__ == "__main__":
    import sys
    print(json.dumps(run(int(sys.argv[1]) if len(sys.argv) > 1 else 25), ensure_ascii=False, indent=2))
