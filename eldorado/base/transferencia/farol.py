"""A transferência ao Farol (etapa 08 do plano): o único ponto de comunicação com a segunda metade do sistema.

Depois da validação, a Regência libera o livro (a passagem para a etapa Farol); aqui ele é exportado num formato estável
(eldorado.livro/1): a identidade, os itens com as provas, as dispensas, os vereditos, os dois links e a origem, o
passaporte, os relatórios de cada etapa, a previsão e os achados. Um arquivo por livro e um manifesto, em
transferencia/farol/. O livro que mudou depois da última transferência vai de novo (uma versão nova; nada se
sobrescreve). O Farol só lê: nunca escreve no Eldorado.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FORMATO = "eldorado.livro/1"


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def para_transferir(con: sqlite3.Connection) -> list[str]:
    """Os livros liberados ao Farol ainda não transferidos, ou alterados depois da última transferência."""
    sql = ("SELECT l.id FROM livro l JOIN passaporte p ON p.livro_id = l.id WHERE p.fase = 'farol' AND l.situacao <> 'excluido' "
           "AND (NOT EXISTS (SELECT 1 FROM transferencia t WHERE t.livro_id = l.id) "
           "OR l.atualizado_em > (SELECT MAX(t.em) FROM transferencia t WHERE t.livro_id = l.id)) ORDER BY l.id")
    return [r[0] for r in con.execute(sql)]


def pacote(con: sqlite3.Connection, lid: str) -> dict[str, Any]:
    con.row_factory = sqlite3.Row

    def linhas(sql: str) -> list[dict[str, Any]]:
        return [dict(r) for r in con.execute(sql, (lid,))]
    lv = dict(con.execute("SELECT * FROM livro WHERE id = ?", (lid,)).fetchone())
    dados = con.execute("SELECT * FROM livro_dados WHERE livro_id = ?", (lid,)).fetchone()
    certs = linhas("SELECT c.item, c.valor, c.situacao, c.fase, c.trecho, c.pagina, c.justificativa, c.em, d.url AS documento "
                   "FROM certidao c LEFT JOIN documento d ON d.id = c.documento_id WHERE c.livro_id = ? ORDER BY c.em")
    prev = con.execute("SELECT * FROM previsao WHERE livro_id = ?", (lid,)).fetchone()
    return {
        "formato": FORMATO, "transferido_em": _agora(),
        "livro": {k: lv.get(k) for k in ("id", "missao", "chave", "titulo", "orgao", "uf", "tema", "estrela", "selo_livro", "informacoes_validadas",
                                         "situacao", "criado_em", "atualizado_em")},
        "links": {"divulgacao": lv.get("link_divulgacao"), "oficial": lv.get("link_oficial"),
                  "origem": dados["origem"] if dados else None, "origem_motivo": dados["origem_motivo"] if dados else None},
        "dados": dict(dados) if dados else None,
        "itens": [c for c in certs if c["situacao"] == "comprovado"],
        "dispensas": [c for c in certs if c["situacao"] == "dispensado"],
        "vereditos": linhas("SELECT origem, decisao, em FROM veredito WHERE livro_id = ? ORDER BY em"),
        "passaporte": linhas("SELECT de, para, em, autorizado_por FROM passagem WHERE livro_id = ? ORDER BY em"),
        "relatorios": linhas("SELECT fase, gerou, aprendeu, faltou, analise, em FROM relatorio_etapa WHERE livro_id = ? ORDER BY em"),
        "previsao": dict(prev) if prev else None,
        "achados": linhas("SELECT motor, encontrado_em, publicado_em, link_divulgacao, link_oficial FROM achado WHERE livro_id = ? ORDER BY encontrado_em"),
    }


def transferir(con: sqlite3.Connection, diario, destino: Path = Path("transferencia/farol"), limite: int = 500) -> dict[str, Any]:
    """Exporta os livros liberados; registra cada transferência no livro (o evento transferencia.feita)."""
    destino.mkdir(parents=True, exist_ok=True)
    feitos = []
    for lid in para_transferir(con)[:limite]:
        p = pacote(con, lid)
        nome = f"{lid}.json"
        (destino / nome).write_text(json.dumps(p, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
        diario.emitir("transferencia.feita", "farol", {"livro_id": lid, "em": p["transferido_em"], "versao_formato": FORMATO})
        diario.emitir("relatorio.etapa", "farol", {"livro_id": lid, "fase": "farol", "gerou": f"transferido ao Farol ({FORMATO})",
                                                    "aprendeu": None, "faltou": None, "analise": "interna", "em": p["transferido_em"]})
        feitos.append({"livro": lid, "titulo": p["livro"]["titulo"], "arquivo": nome})
    manifesto = {"formato": FORMATO, "em": _agora(), "livros": sorted(f.name[:-5] for f in destino.glob("*.json") if f.name != "manifesto.json")}
    (destino / "manifesto.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"transferidos": len(feitos), "no_farol": len(manifesto["livros"]), "livros": feitos[:20]}


def no_farol(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem: transfere ao Farol os livros que a Regência liberou (e os que mudaram desde a última vez)."""
    p = Path(parametros.get("dados", "dados")) / "biblioteca.db"
    if not p.exists():
        return []
    con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    try:
        return [transferir(con, contexto.diario, Path(parametros.get("destino", "transferencia/farol")))]
    finally:
        con.close()
