"""A releitura dos documentos herdados sem texto (24/10/2026): a migração do Eldorado0 registrou 4.873 documentos com o
endereço e o tipo, mas sem o texto das páginas. A cada passagem, alguns são relidos pela escada e pela leitura completa
(PDF, OCR, páginas, planilhas), primeiro os dos livros abertos, e o texto é gravado no PRÓPRIO documento herdado. A
tentativa fica no aprendizado do Cérebro (no máximo 3, uma por dia), para não reler o mesmo a cada passagem.
"""

from __future__ import annotations

import sqlite3
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def escolher(bib: sqlite3.Connection, cer: sqlite3.Connection, limite: int) -> list[tuple[int, str, str]]:
    ontem = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    tentados = {r[0] for r in cer.execute("SELECT documento_id FROM releitura WHERE tentativas >= 3 OR ultima >= ?", (ontem,))}
    sql = (
        "SELECT d.id, d.url, d.sha256, MAX(CASE WHEN ld.situacao_prazo = 'aberta' THEN 1 ELSE 0 END) AS aberta FROM documento d "
        "LEFT JOIN certidao c ON c.documento_id = d.id LEFT JOIN livro_dados ld ON ld.livro_id = c.livro_id "
        "WHERE NOT EXISTS (SELECT 1 FROM pagina p WHERE p.documento_id = d.id) AND d.url LIKE 'http%' "
        "GROUP BY d.id ORDER BY aberta DESC, d.id DESC"
    )
    saida = []
    for did, url, sha, _ in bib.execute(sql):
        if did not in tentados:
            saida.append((did, url, sha))
            if len(saida) >= limite:
                break
    return saida


def reler(dados: Path, diario, limite: int = 15, orcamento_s: float = 90) -> dict[str, int]:
    from ...motores.acesso.api import DegrauAPI
    from ...motores.acesso.escada import Escada
    from ...motores.acesso.leve import DegrauLeve
    from ...motores.leitura import leitores

    bib = sqlite3.connect(f"file:{dados / 'biblioteca.db'}?mode=ro", uri=True)
    cer = sqlite3.connect(f"file:{dados / 'cerebro.db'}?mode=ro", uri=True)
    try:
        if not cer.execute("SELECT 1 FROM sqlite_master WHERE name = 'releitura'").fetchone():
            return {"relidos": 0, "motivo": "o Cérebro ainda sem a tabela da releitura"}
        fila = escolher(bib, cer, limite)
        anteriores = {r[0]: r[1] for r in cer.execute("SELECT documento_id, tentativas FROM releitura")}
    finally:
        bib.close()
        cer.close()
    escada, registro = Escada([DegrauAPI(), DegrauLeve()], intervalo_padrao=1.0, tentativas=1, tempo_limite=30), leitores.padrao()
    inicio, rel = time.monotonic(), {"escolhidos": len(fila), "relidos": 0, "paginas": 0, "falhas": 0}
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for did, url, sha in fila:
        if time.monotonic() - inicio > orcamento_s:
            break
        resultado = "sem texto"
        try:
            r = escada.buscar(url)
            lido = registro.ler(r.conteudo, url.rsplit("/", 1)[-1])
            paginas = [p.texto for p in lido.paginas if (p.texto or "").strip()]
            if paginas:
                diario.emitir(
                    "documento.registrado",
                    "releitura",
                    {
                        "url": url,
                        "sha256": sha,
                        "tipo": lido.tipo,
                        "paginas": len(paginas),
                        "leitor": lido.leitor,
                        "versao_leitor": None,
                        "obtido_em": agora,
                    },
                )
                for i, texto in enumerate(paginas, 1):
                    diario.emitir("pagina.gravada", "releitura", {"documento_id": did, "documento_sha256": sha, "numero": i, "texto": texto})
                rel["relidos"] += 1
                rel["paginas"] += len(paginas)
                resultado = f"relido: {len(paginas)} páginas ({lido.leitor})"
        except Exception as e:  # noqa: BLE001 — a falha fica no aprendizado; tenta de novo amanhã (até 3 vezes)
            rel["falhas"] += 1
            resultado = f"falhou: {type(e).__name__}: {str(e)[:120]}"
        diario.emitir(
            "documento.relido", "releitura", {"documento_id": did, "tentativas": anteriores.get(did, 0) + 1, "ultima": agora, "resultado": resultado}
        )
    return rel


def no_reler(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem: a releitura de alguns documentos herdados sem texto (com orçamento de tempo)."""
    dados = Path(parametros.get("dados", "dados"))
    if not ((dados / "biblioteca.db").exists() and (dados / "cerebro.db").exists()):
        return [{"relidos": 0, "motivo": "sem os bancos nesta pasta"}]
    return [reler(dados, contexto.diario, int(parametros.get("limite", 15)), float(parametros.get("orcamento_s", 90)))]
