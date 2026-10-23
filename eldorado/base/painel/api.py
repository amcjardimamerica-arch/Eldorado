"""A API do sistema (plano C: FastAPI, com respostas em orjson): a leitura do sistema para o painel novo e para quem
precisar consultar, sem mexer em nada. Os mesmos dados do site, pelo mesmo leitor (painel/dados.py: o Sistema).

    eldorado api --porta 8000
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import ORJSONResponse


def criar_app(raiz: Path = Path(".")) -> FastAPI:
    from .dados import Sistema, _motores
    app = FastAPI(title="Eldorado", description="A leitura do sistema: motores, livros, certidões e oportunidades", default_response_class=ORJSONResponse)

    def sis() -> Sistema:
        return Sistema(raiz)

    @app.get("/saude")
    def saude() -> dict[str, Any]:
        s = sis()
        ultima = s.cer.execute("SELECT MAX(inicio) FROM execucao_motor").fetchone()[0]
        return {"esquema": s.bib.execute("PRAGMA user_version").fetchone()[0],
                "livros": s.bib.execute("SELECT COUNT(*) FROM livro WHERE situacao <> 'excluido'").fetchone()[0],
                "por_etapa": dict(s.bib.execute("SELECT fase, COUNT(*) FROM passaporte GROUP BY fase").fetchall()), "ultima_execucao": ultima}

    @app.get("/motores")
    def motores() -> list[dict[str, Any]]:
        status, _, _ = _motores(sis())
        return [{"id": m["id"], "nome": m["nome"], "luz": m["luz"], "resultado": m["resultado"], "ultima_leitura": m["ultima_leitura"]} for m in status]

    @app.get("/motores/{mid}")
    def motor(mid: str) -> dict[str, Any]:
        s = sis()
        status, descricao, _ = _motores(s)
        st = next((m for m in status if m["id"] == mid), None)
        if st is None:
            raise HTTPException(404, "motor desconhecido")
        return {**st, "descricao": descricao.get(mid), "configuracao": s.configs.get(mid)}

    @app.get("/livros")
    def livros(q: str | None = None, etapa: str | None = None, limite: int = 50) -> list[dict[str, Any]]:
        s = sis()
        sql = ("SELECT l.id, l.titulo, l.orgao, l.uf, l.estrela, l.link_divulgacao, l.link_oficial, p.fase FROM livro l "
               "JOIN passaporte p ON p.livro_id = l.id WHERE l.situacao <> 'excluido'")
        args: list[Any] = []
        if q:
            sql += " AND (l.titulo LIKE ? OR l.orgao LIKE ?)"
            args += [f"%{q}%", f"%{q}%"]
        if etapa:
            sql += " AND p.fase = ?"
            args.append(etapa)
        return [dict(r) for r in s.bib.execute(sql + " ORDER BY l.atualizado_em DESC LIMIT ?", (*args, min(limite, 500)))]

    @app.get("/livros/{lid}")
    def livro(lid: str) -> dict[str, Any]:
        s = sis()
        lv = s.bib.execute("SELECT * FROM livro WHERE id = ?", (lid,)).fetchone()
        if lv is None:
            raise HTTPException(404, "livro desconhecido")
        dados = s.bib.execute("SELECT * FROM livro_dados WHERE livro_id = ?", (lid,)).fetchone()
        certs = [dict(r) for r in s.bib.execute("SELECT item, valor, situacao, fase, trecho, em FROM certidao WHERE livro_id = ? ORDER BY em", (lid,))]
        historia = [dict(r) for r in s.bib.execute("SELECT de, para, em, autorizado_por FROM passagem WHERE livro_id = ? ORDER BY em", (lid,))]
        sql = "SELECT id, motor, titulo, link_divulgacao, link_oficial, encontrado_em, decisao, dados FROM achado WHERE livro_id = ? ORDER BY encontrado_em"
        achados = [{**dict(r), "dados": json.loads(r["dados"] or "{}")} for r in s.bib.execute(sql, (lid,))]
        return {"livro": dict(lv), "dados": dict(dados) if dados else None, "certidoes": certs, "historia": historia, "achados": achados}

    @app.get("/abertas")
    def abertas() -> list[dict[str, Any]]:
        return [{k: r[k] for k in ("id", "titulo", "orgao", "uf", "inscricao_fim", "link_oficial", "link_divulgacao", "fase", "origem")}
                for r in sis().livros_abertos()]

    return app


def servir(porta: int = 8000, raiz: Path = Path(".")) -> None:
    import uvicorn
    uvicorn.run(criar_app(raiz), host="127.0.0.1", port=porta)

