"""Expurgo avaliado pelo Claude (02/11/2026) — etapa 03 Certificação, indicador 'Último expurgo (feito pelo Claude)'.

Avaliação feita sobre a Biblioteca do Git de 02/11/2026 08:55 (candidatos: 4169 documentos sem uso, 1249 achados sem livro):
- ACHADOS sem livro (1249): todos com decisão 'barrado' pelo portão (extratos de termo de doação do DOU, credenciamentos de
  prestadores do PNCP, editais de anos anteriores, municípios fora do escopo, 'sem título'). Nenhum é pendente nem legislativo
  (as exceções R35 ficam). SAEM: o registro do descarte (motor, link, motivo) fica no Cérebro (achado_descartado).
- DOCUMENTOS sem uso (4169): quase todos herdados do Eldorado0 sem texto ('Eldorado0 (sem o texto)'), sem certidão e sem
  achado. EXCEÇÃO da avaliação: FICAM os documentos cujo endereço é o site oficial ou o de divulgação de um livro ativo
  (1073 endereços na avaliação) — são o endereço da oportunidade, não cópia de site.
ESCOPO DOS DOCUMENTOS (titular, 02/11/2026): na Biblioteca viva só 519 dos 4171 documentos sem uso eram do Eldorado0; os
demais (páginas, PDFs, 'documento na mão' do interceptador) não foram avaliados. --documentos eldorado0 (opção A, padrão)
expurga só os do Eldorado0 sem texto; --documentos restantes (opção B) os demais, depois da revisão; --documentos nenhum
só os achados.
O script recalcula tudo na Biblioteca VIVA no momento da execução (os números podem mudar), mostra a prévia e só emite os
eventos com --executar. Depois: `eldorado aplicar`. O gravador ainda confere de novo (só apaga achado sem livro e documento
sem certidão/achado).
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from eldorado.base.cartorio.expurgo_claude import registrar
from eldorado.base.cartorio.leitura_efemera import MOTORES_LEGISLATIVOS
from eldorado.base.nucleo.eventos import Diario

MOTIVO = ("avaliação do Claude (02/11/2026): achados barrados pelo portão sem livro e documentos sem uso herdados do Eldorado0; "
          "mantidos os documentos que são o endereço (site oficial/divulgação) de livro ativo")


ELDORADO0 = "Eldorado0 (sem o texto)"


def avaliar(bib: sqlite3.Connection, horas: float, escopo: str = "eldorado0") -> tuple[list, list[int], int]:
    corte = (datetime.now(timezone.utc) - timedelta(hours=horas)).isoformat()
    leg = ",".join("?" * len(MOTORES_LEGISLATIVOS))
    achados = bib.execute(
        "SELECT id, motor, encontrado_em, decisao, motivo, COALESCE(link_oficial, link_divulgacao) FROM achado "
        f"WHERE livro_id IS NULL AND decisao NOT IN ('pendente') AND COALESCE(encontrado_em,'') < ? AND motor NOT IN ({leg})",
        (corte[:10], *MOTORES_LEGISLATIVOS)).fetchall()
    usados = {r[0] for r in bib.execute(
        "SELECT documento_id FROM certidao WHERE documento_id IS NOT NULL UNION "
        "SELECT documento_id FROM achado WHERE documento_id IS NOT NULL")}
    enderecos = set()
    for r in bib.execute("SELECT link_oficial, link_divulgacao FROM livro WHERE situacao NOT IN ('excluido','unido')"):
        enderecos.update(x for x in r if x)
    docs, mantidos = [], 0
    for i, url, leitor in bib.execute("SELECT id, url, leitor FROM documento WHERE COALESCE(obtido_em,'') < ?", (corte,)):
        if i in usados:
            continue
        if url in enderecos:
            mantidos += 1
            continue
        if escopo == "nenhum" or (escopo == "eldorado0") != (leitor == ELDORADO0):
            continue
        docs.append(i)
    return achados, docs, mantidos


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dados", default="dados")
    ap.add_argument("--eventos", default="eventos")
    ap.add_argument("--horas", type=float, default=2)
    ap.add_argument("--executar", action="store_true")
    ap.add_argument("--documentos", choices=["eldorado0", "restantes", "nenhum"], default="eldorado0")
    a = ap.parse_args()
    bib = sqlite3.connect(f"file:{Path(a.dados) / 'biblioteca.db'}?mode=ro", uri=True)
    try:
        achados, docs, mantidos = avaliar(bib, a.horas, a.documentos)
    finally:
        bib.close()
    decisoes = {}
    for x in achados:
        decisoes[x[3]] = decisoes.get(x[3], 0) + 1
    print(f"achados sem livro a expurgar: {len(achados)} {decisoes}")
    print(f"documentos sem uso a expurgar ({a.documentos}): {len(docs)} · mantidos por serem endereço de livro ativo: {mantidos}")
    if not a.executar:
        print("PRÉVIA — nada foi alterado. Rode de novo com --executar e depois `eldorado aplicar`.")
        return 0
    dia = Diario(a.eventos, "expurgo-claude")
    agora = datetime.now(timezone.utc).isoformat()
    for i, m, enc, dec, mot, link in achados:
        dia.emitir("achado.descartado", "expurgo-claude", {"id": i, "motor": m, "encontrado_em": enc, "decisao": dec,
                                                          "motivo": (mot or "")[:300], "link": link, "descartado_em": agora})
    for d in docs:
        dia.emitir("documento.descartado", "expurgo-claude", {"documento_id": d})
    arq = registrar({"achados_sem_livro": len(achados), "documentos_sem_uso": len(docs),
                     "documentos_mantidos_endereco_de_livro": mantidos,
                     "escopo_documentos": a.documentos}, MOTIVO)
    print(f"eventos emitidos; registro: {arq}. Agora: eldorado aplicar")
    return 0


if __name__ == "__main__":
    sys.exit(main())
