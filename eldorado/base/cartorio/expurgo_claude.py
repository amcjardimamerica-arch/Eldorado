"""O expurgo é do Claude, nunca do sistema (titular, 01/11/2026: "somente o Claude apaga livros e faz expurgos, o
sistema não faz"; "faça a avaliação antes de expurgar"). O sistema só INDICA os candidatos (a Sala, "o último expurgo");
o Claude avalia e, aprovado, executa por aqui: os eventos do expurgo e o registro em expurgos/<data>.json."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .leitura_efemera import MOTORES_LEGISLATIVOS
from .migrados import sql_migrado

PASTA = Path("expurgos")
LOTES_MIGRADOS = Path("verificacao/migrados")


def candidatos(bib: sqlite3.Connection, horas: float = 2) -> dict[str, Any]:
    """Os candidatos ao expurgo (só a indicação; nada sai daqui)."""
    corte = (datetime.now(timezone.utc) - timedelta(hours=horas)).isoformat()
    usados = ("SELECT documento_id FROM certidao WHERE documento_id IS NOT NULL UNION SELECT documento_id FROM achado "
              "WHERE documento_id IS NOT NULL")
    # o documento que é o ENDEREÇO de um livro ativo (o site oficial ou o de divulgação) não é "sem uso": R35 manda guardar os
    # endereços (avaliação do Claude, 02/11/2026); antes ele ficava indicado para sempre e a Sala nunca saía do amarelo
    enderecos = ("SELECT link_oficial FROM livro WHERE situacao NOT IN ('excluido', 'unido') AND link_oficial IS NOT NULL UNION "
                 "SELECT link_divulgacao FROM livro WHERE situacao NOT IN ('excluido', 'unido') AND link_divulgacao IS NOT NULL")
    tem_livro = bib.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'livro'").fetchone() is not None
    filtro = f"AND url NOT IN ({enderecos})" if tem_livro else ""
    docs = bib.execute(f"SELECT COUNT(*) FROM documento WHERE COALESCE(obtido_em, '') < ? AND id NOT IN ({usados}) {filtro}",
                       (corte,)).fetchone()[0]
    leg = ",".join("?" * len(MOTORES_LEGISLATIVOS))
    ach = bib.execute(f"SELECT COUNT(*) FROM achado WHERE livro_id IS NULL AND decisao <> 'pendente' AND COALESCE(encontrado_em, '') < ? "
                      f"AND motor NOT IN ({leg})", (corte[:10], *MOTORES_LEGISLATIVOS)).fetchone()[0]
    pend = 0
    for f in sorted(LOTES_MIGRADOS.glob("parte-*.json")) if LOTES_MIGRADOS.exists() else []:
        try:
            pend += sum(1 for x in json.loads(f.read_text(encoding="utf-8")).get("itens", []) if not x.get("veredito"))
        except (OSError, ValueError):
            pass
    return {"documentos_sem_uso": docs, "achados_sem_livro": ach, "migrados_no_chrome": pend, "total": docs + ach + pend}


def ultimo() -> dict[str, Any] | None:
    """O último expurgo registrado (o mais recente em expurgos/)."""
    regs = sorted(PASTA.glob("*.json")) if PASTA.exists() else []
    if not regs:
        return None
    try:
        return json.loads(regs[-1].read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def registrar(o_que: dict[str, int], motivo: str, por: str = "Claude", quando: str | None = None) -> Path:
    """O registro de um expurgo feito pelo Claude (data, o que saiu e por quê)."""
    quando = quando or datetime.now(timezone.utc).isoformat()
    PASTA.mkdir(exist_ok=True)
    arq = PASTA / f"{quando[:19].replace(':', '')}.json"
    arq.write_text(json.dumps({"em": quando, "por": por, "motivo": motivo, "saiu": o_que}, ensure_ascii=False, indent=1), encoding="utf-8")
    return arq


def migrados_sem_data(bib: sqlite3.Connection, hoje: str) -> list[dict[str, Any]]:
    """Os migrados fora do prazo aberto e sem nenhuma data: a avaliação pelo Chrome (não servem à preditiva sem data)."""
    bib.row_factory = sqlite3.Row
    r = [dict(x) for x in bib.execute(
        "SELECT l.id, l.titulo, l.orgao, l.uf, l.link_oficial, l.link_divulgacao, l.situacao FROM livro l JOIN livro_dados d ON d.livro_id = l.id "
        f"WHERE l.situacao NOT IN ('excluido', 'unido') AND {sql_migrado()} AND d.inscricao_inicio IS NULL AND d.inscricao_fim IS NULL "
        "AND COALESCE(d.situacao_prazo, '') <> 'aberta' ORDER BY l.id")]
    bib.row_factory = None
    return r
