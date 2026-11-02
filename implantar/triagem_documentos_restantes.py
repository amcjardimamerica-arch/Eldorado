"""Triagem dos documentos sem uso que sobraram da opção A (titular, 02/11/2026) — prepara a opção B.

Meta da titular: a Biblioteca só com documentos e dados reais e utilizáveis, sem falso positivo nem informação inútil.
Apagar às cegas perderia oportunidades reais que nunca viraram livro (falso negativo). Cada documento cai em um grupo:
  B1 lixo_comprovado  — o link é de um achado já descartado (registro no Cérebro) ou é página de listagem/tag/categoria/busca,
                        resultado, extrato, notícia de ato encerrado: o próprio sistema já decidiu que não é oportunidade.
  B2 conferir_chrome  — trabalho do interceptador (Claude no Chrome) ou URL com sinal de oportunidade vigente
                        (edital/chamada/seleção/fomento + 2026/2027): só sai com veredito do Claude no Chrome, e o que for
                        real vira livro.
  B3 sem_sinal        — o resto: lido pelo sistema, sem livro, sem achado e sem sinal de oportunidade.
Gera verificacao/expurgo/triagem-restantes-<data>.json e .csv. Não altera nada.
Expurgar um grupo:  python implantar/triagem_documentos_restantes.py --expurgar B1 [--executar]   (depois: eldorado aplicar)
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from expurgo_claude_2026_11_02 import avaliar  # noqa: E402

LISTAGEM = re.compile(r"/(tags?|categor(y|ia)s?|busca|search|page/\d+|arquivo|archive|noticias/?$|editais/?$)(/|\?|$)|[?&](s|q|page)=", re.I)
ENCERRADO = re.compile(r"resultado|homologa|extrato|ratifica|dispensa|inexigibil|aditivo|termo-de-(fomento|colabora)|"
                       r"prorroga|errata|convoca[cç][aã]o-para-assinatura|habilitad", re.I)
OPORTUNIDADE = re.compile(r"edital|chamada|chamamento|sele[cç][aã]o|inscri|fomento|premio|prêmio|grant|fellowship|bolsa|"
                          r"call|funding|financiamento|captacao|captação|apoio", re.I)
VIGENTE = re.compile(r"2026|2027")


def grupo(url: str, leitor: str, descartados: set[str]) -> str:
    if url in descartados or LISTAGEM.search(url) or (ENCERRADO.search(url) and not VIGENTE.search(url)):
        return "B1"
    if "interceptador" in (leitor or "") or (OPORTUNIDADE.search(url) and VIGENTE.search(url)):
        return "B2"
    if ENCERRADO.search(url):
        return "B1"
    return "B3"


def triar(dados: str = "dados") -> list[dict]:
    bib = sqlite3.connect(f"file:{Path(dados) / 'biblioteca.db'}?mode=ro", uri=True)
    cer = sqlite3.connect(f"file:{Path(dados) / 'cerebro.db'}?mode=ro", uri=True)
    try:
        descartados = {r[0] for r in cer.execute("SELECT link FROM achado_descartado WHERE link IS NOT NULL")}
        _, ids, _ = avaliar(bib, 2, "restantes")
        out = []
        for i in range(0, len(ids), 900):
            lote = ids[i:i + 900]
            for d, url, tipo, leitor, obtido, oficial in bib.execute(
                    f"SELECT id, url, tipo, leitor, obtido_em, oficial FROM documento WHERE id IN ({','.join('?' * len(lote))})", lote):
                out.append({"id": d, "grupo": grupo(url, leitor, descartados), "url": url, "tipo": tipo, "leitor": leitor,
                            "obtido_em": obtido, "oficial": oficial})
        return sorted(out, key=lambda x: (x["grupo"], x["url"]))
    finally:
        bib.close(); cer.close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dados", default="dados")
    ap.add_argument("--eventos", default="eventos")
    ap.add_argument("--expurgar", choices=["B1", "B2", "B3"])
    ap.add_argument("--executar", action="store_true")
    a = ap.parse_args()
    docs = triar(a.dados)
    print("documentos restantes:", len(docs), dict(sorted(Counter(d["grupo"] for d in docs).items())))
    if not a.expurgar:
        dia = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        base = Path("verificacao/expurgo"); base.mkdir(parents=True, exist_ok=True)
        (base / f"triagem-restantes-{dia}.json").write_text(json.dumps(docs, ensure_ascii=False, indent=1), encoding="utf-8")
        with open(base / f"triagem-restantes-{dia}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(docs[0]) if docs else ["id"]); w.writeheader(); w.writerows(docs)
        print(f"triagem gravada em {base}/triagem-restantes-{dia}.json/.csv — nada foi alterado")
        return 0
    alvo = [d["id"] for d in docs if d["grupo"] == a.expurgar]
    if a.expurgar == "B2":
        print("B2 só sai com veredito do Claude no Chrome (o que for real vira livro). Recusado.")
        return 1
    print(f"{a.expurgar}: {len(alvo)} documentos a expurgar")
    if not a.executar:
        print("PRÉVIA — nada foi alterado. Rode com --executar e depois `eldorado aplicar`.")
        return 0
    from eldorado.base.cartorio.expurgo_claude import registrar
    from eldorado.base.nucleo.eventos import Diario
    dia = Diario(a.eventos, "expurgo-claude")
    for d in alvo:
        dia.emitir("documento.descartado", "expurgo-claude", {"documento_id": d})
    arq = registrar({"documentos_sem_uso": len(alvo), "grupo_triagem": a.expurgar},
                    f"expurgo da triagem {a.expurgar} (titular, 02/11/2026): documentos sem uso sem sinal de oportunidade real")
    print(f"eventos emitidos; registro: {arq}. Agora: eldorado aplicar")
    return 0


if __name__ == "__main__":
    sys.exit(main())
