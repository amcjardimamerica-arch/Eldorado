"""R35 — a leitura efêmera (titular, 30/10/2026: "não deve existir cópia de nenhum site; o sistema não é repositório de sites
nem de arquivos; os dados são uma trava absoluta").

O texto lido de um site serve ao Cartório para certificar e sai do banco em seguida: ficam o texto da oportunidade (os dados
do livro e as certidões, com o trecho literal do edital) e os endereços (o documento: o site oficial e o de divulgação).
Depois de cada passagem, a leitura com mais de 2 h é expurgada do banco (o evento leitura.expurgada) e o diário efêmero com
mais de 6 h é apagado.
"""

from __future__ import annotations

import sqlite3
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ..nucleo.eventos import Diario, pasta_efemera

# R35 — as EXCEÇÕES da titular (30/10/2026: "as empresas e as propostas legislativas devem ser mantidas na Biblioteca"): os
# achados dos motores legislativos ficam mesmo sem livro (e os documentos deles); as empresas, os incentivos e as leis nunca
# são alcançados pelo descarte (que só toca achado e documento)
MOTORES_LEGISLATIVOS = ("alego-pl", "camara-goiania-pl", "congresso-nacional")
HORAS_NO_BANCO = 2
HORAS_NO_DIARIO = 6


def expurgar(banco: str | Path, eventos: str | Path, horas: float = HORAS_NO_BANCO, execucao: str = "expurgo-leituras") -> dict[str, int]:
    """Expurga do banco a leitura dos documentos lidos há mais de `horas` (horas=0: todas) e apaga o diário efêmero vencido."""
    corte = (datetime.now(timezone.utc) - timedelta(hours=horas)).isoformat()
    con = sqlite3.connect(f"file:{Path(banco)}?mode=ro", uri=True)
    try:
        docs = [
            r[0]
            for r in con.execute(
                "SELECT DISTINCT p.documento_id FROM pagina p JOIN documento d ON d.id = p.documento_id WHERE COALESCE(d.obtido_em, '') < ?", (corte,)
            )
        ]
    finally:
        con.close()
    # R35 (titular: "não exclua nenhum livro, apenas os dados que não são livros"): o achado que não virou livro e o documento
    # que nenhum livro usa saem da Biblioteca (o registro do descarte, sem conteúdo, fica no Cérebro: o aprendizado)
    con = sqlite3.connect(f"file:{Path(banco)}?mode=ro", uri=True)
    try:
        sem_livro = con.execute(
            "SELECT id, motor, encontrado_em, decisao, motivo, COALESCE(link_oficial, link_divulgacao) FROM achado "
            "WHERE livro_id IS NULL AND decisao <> 'pendente' AND COALESCE(encontrado_em, '') < ? "
            f"AND motor NOT IN ({','.join('?' * len(MOTORES_LEGISLATIVOS))})",
            (corte[:10], *MOTORES_LEGISLATIVOS),
        ).fetchall()
        usados = {
            r[0]
            for r in con.execute(
                "SELECT documento_id FROM certidao WHERE documento_id IS NOT NULL UNION "
                "SELECT documento_id FROM achado WHERE documento_id IS NOT NULL AND (livro_id IS NOT NULL OR motor IN "
                f"({','.join('?' * len(MOTORES_LEGISLATIVOS))}))",
                MOTORES_LEGISLATIVOS,
            )
        }
        sem_uso = [r[0] for r in con.execute("SELECT id FROM documento WHERE COALESCE(obtido_em, '') < ?", (corte,)) if r[0] not in usados]
    finally:
        con.close()
    if docs or sem_livro or sem_uso:
        dia = Diario(eventos, execucao)
        agora_ = datetime.now(timezone.utc).isoformat()
        for doc in docs:
            dia.emitir("leitura.expurgada", "leitura-efemera", {"documento_id": doc, "motivo": "R35: a leitura do site não fica guardada"})
        for i, m, enc, dec, mot, link in sem_livro:
            dia.emitir(
                "achado.descartado",
                "leitura-efemera",
                {"id": i, "motor": m, "encontrado_em": enc, "decisao": dec, "motivo": (mot or "")[:300], "link": link, "descartado_em": agora_},
            )
        for doc in sem_uso:
            dia.emitir("documento.descartado", "leitura-efemera", {"documento_id": doc})
    apagados = 0
    ef = pasta_efemera(eventos)
    if ef.exists():
        limite = time.time() - HORAS_NO_DIARIO * 3600
        for a in ef.rglob("*.jsonl"):
            if a.stat().st_mtime < limite:
                a.unlink(missing_ok=True)
                apagados += 1
    # o resíduo da transição: a leitura de site que um código antigo gravou no histórico nas últimas 48 h sai dele
    limpos = 0
    corte_h = time.time() - 48 * 3600
    for a in Path(eventos).rglob("*.jsonl"):
        if a.stat().st_mtime < corte_h:
            continue
        linhas = a.read_bytes().splitlines(keepends=True)
        fica = [x for x in linhas if b'"tipo":"pagina.gravada"' not in x[:200]]
        if len(fica) != len(linhas):
            a.write_bytes(b"".join(fica))
            limpos += len(linhas) - len(fica)
    return {
        "documentos": len(docs),
        "achados_descartados": len(sem_livro),
        "documentos_descartados": len(sem_uso),
        "diarios_apagados": apagados,
        "leituras_tiradas_do_historico": limpos,
    }
