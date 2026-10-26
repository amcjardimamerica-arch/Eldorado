"""O Comandante atualiza a Biblioteca e valida as oportunidades antigas (titular, 25/10/2026).

A BASE de um livro são cinco dados: o site oficial, o site que divulgou, o prazo de inscrição, a esfera e a área de
atuação (sem eles não há análise preditiva). A cada passagem, o Comandante avalia cada livro e grava a classe e o que buscar:
  base completa · aberta incompleta (completar primeiro) · recuperável (faltam 1 ou 2 e há o site) · sem base ·
  não é oportunidade (vai direto ao Chrome confirmar).
A coleta: o Interceptador busca o que falta, 5 livros em paralelo, cada livro no máximo 2 TENTATIVAS com pelo menos
30 MINUTOS entre elas; depois da 2ª sem completar, o livro vai ao Claude no Chrome, com a lista do que buscar. O Chrome
valida ou descarta; o descartado é excluído (exclusão lógica, com a justificativa: nada se apaga)."""

from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

TENTATIVAS = 2
INTERVALO_MIN = 30
PRIORIDADE = {"aberta incompleta": 0, "recuperável": 1, "sem base": 2}
URL = re.compile(r"^https?://[^\s/]+\.[a-z]{2,}", re.I)
CONTINUO = re.compile(r"cont[ií]nu|permanente|aberto o ano|a qualquer tempo", re.I)
DADOS = ("site oficial", "site de divulgação", "prazo de inscrição", "esfera", "área de atuação")


def avaliar(con: sqlite3.Connection) -> list[dict[str, Any]]:
    """A classe e o que buscar de cada livro vivo (pelos dados gravados no livro, não pelo que se deduz do título)."""
    from .organizar import validar

    con.row_factory = sqlite3.Row
    cert: dict[str, dict[str, str]] = {}
    for c in con.execute("SELECT livro_id, item, valor FROM certidao WHERE situacao IN ('comprovado', 'dispensado')"):
        cert.setdefault(c["livro_id"], {})[c["item"]] = c["valor"] or ""
    saida = []
    for r in con.execute(
        "SELECT l.id, l.titulo, l.link_oficial, l.link_divulgacao, d.inscricao_fim, d.situacao_prazo, d.esfera, d.area, "
        "d.base_classe, d.base_buscar, d.base_tentativas, d.base_ultima, p.fase FROM livro l JOIN livro_dados d ON d.livro_id = l.id "
        "JOIN passaporte p ON p.livro_id = l.id WHERE l.situacao NOT IN ('excluido', 'unido')"
    ):
        cs = cert.get(r["id"], {})
        tem = {
            "site oficial": bool(r["link_oficial"] and URL.match(r["link_oficial"])),
            "site de divulgação": bool(r["link_divulgacao"] and URL.match(r["link_divulgacao"])),
            "prazo de inscrição": bool(r["inscricao_fim"]) or bool(CONTINUO.search(cs.get("Prazo de inscrição", ""))),
            "esfera": bool(r["esfera"] or cs.get("Esfera")),
            "área de atuação": bool(r["area"] or cs.get("Área de atuação")),
        }
        buscar = [d for d in DADOS if not tem[d]]
        if validar(r["titulo"]) != "oportunidade":
            classe = "não é oportunidade"
        elif not buscar:
            classe = "base completa"
        elif r["situacao_prazo"] == "aberta":
            classe = "aberta incompleta"
        elif len(buscar) <= 2 and (tem["site oficial"] or tem["site de divulgação"]):
            classe = "recuperável"
        else:
            classe = "sem base"
        saida.append(
            {
                "id": r["id"],
                "titulo": r["titulo"],
                "classe": classe,
                "buscar": buscar,
                "fase": r["fase"],
                "tentativas": r["base_tentativas"] or 0,
                "ultima": r["base_ultima"],
                "antes": (r["base_classe"], r["base_buscar"]),
                "prazo": r["situacao_prazo"],
                "fim": r["inscricao_fim"],
            }
        )
    return saida


def fila(livros: list[dict[str, Any]], agora: datetime | None = None, maximo: int = 50) -> list[dict[str, Any]]:
    """Os livros a completar agora: menos de 2 tentativas e a última há pelo menos 30 minutos; as abertas primeiro."""
    agora = agora or datetime.now(timezone.utc)
    limite = (agora - timedelta(minutes=INTERVALO_MIN)).isoformat()
    prontos = [
        x
        for x in livros
        if x["classe"] in PRIORIDADE
        and x["fase"] not in ("analise externa", "farol")
        and x["tentativas"] < TENTATIVAS
        and (not x["ultima"] or x["ultima"] <= limite)
    ]
    return sorted(prontos, key=lambda x: (PRIORIDADE[x["classe"]], x["tentativas"], len(x["buscar"]), x["fim"] or "9999"))[:maximo]


def registrar_tentativa(diario, livro: dict[str, Any], agora: datetime | None = None) -> None:
    agora = agora or datetime.now(timezone.utc)
    diario.emitir(
        "livro.base",
        "comandante",
        {
            "livro_id": livro["id"],
            "base_classe": livro["classe"],
            "base_buscar": json.dumps(livro["buscar"], ensure_ascii=False),
            "base_tentativas": livro["tentativas"] + 1,
            "base_ultima": agora.isoformat(timespec="seconds"),
        },
    )


def ao_chrome(con: sqlite3.Connection, diario, livro: dict[str, Any], motivo: str) -> bool:
    """O livro vai à análise externa (o Claude no Chrome), com a lista do que buscar; o arquivo também (as antigas)."""
    from ..cartorio.passaporte import Passaporte

    ok, _m = Passaporte(con, diario, maximo=10).mover(
        livro["id"], "analise externa", f"{motivo}: buscar {', '.join(livro['buscar']) or 'a confirmação'}"
    )
    return ok


def atualizar(con: sqlite3.Connection, diario, agora: datetime | None = None) -> dict[str, int]:
    """A atualização da Biblioteca pelo Comandante: a classe e o que buscar de cada livro; os esgotados e os que não são
    oportunidade vão ao Chrome."""
    agora = agora or datetime.now(timezone.utc)
    conta = {"avaliados": 0, "gravados": 0, "ao_chrome": 0}
    for x in avaliar(con):
        conta["avaliados"] += 1
        buscar = json.dumps(x["buscar"], ensure_ascii=False)
        if (x["classe"], buscar) != x["antes"]:
            diario.emitir(
                "livro.base",
                "comandante",
                {
                    "livro_id": x["id"],
                    "base_classe": x["classe"],
                    "base_buscar": buscar,
                    "base_tentativas": x["tentativas"],
                    "base_ultima": x["ultima"],
                },
            )
            conta["gravados"] += 1
        if x["fase"] in ("analise externa", "farol"):
            continue
        if x["classe"] == "não é oportunidade":
            conta["ao_chrome"] += ao_chrome(con, diario, x, "pode não ser uma oportunidade (o título é de anexo, andamento ou notícia)")
        elif x["classe"] in PRIORIDADE and x["tentativas"] >= TENTATIVAS:
            conta["ao_chrome"] += ao_chrome(con, diario, x, f"{TENTATIVAS} tentativas do Interceptador sem completar a base")
    return conta


def no_atualizar_biblioteca(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem (o Comandante, C6): a base de cada livro, a fila de completar e o encaminhamento ao Chrome."""
    p = Path(parametros.get("dados", "dados")) / "biblioteca.db"
    if not p.exists():
        return []
    con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    try:
        if "base_classe" not in {r[1] for r in con.execute("PRAGMA table_info(livro_dados)")}:
            return [{"motivo": "a Biblioteca ainda não está na versão 13"}]
        return [atualizar(con, contexto.diario)]
    finally:
        con.close()
