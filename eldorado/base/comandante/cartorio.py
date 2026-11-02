"""O COMANDANTE DO CARTÓRIO (titular, 02/11/2026 — R37 e R38).

Nenhuma parte do Eldorado é linha de produção. O Cartório está sob o comando do Comandante, que analisa cada uma das 5
etapas, faz o Cartório certificar os itens e coordena cada livro entre elas — e entrega ao Farol ou ao arquivo tudo o que
os motores (inclusive o Espião) geram. O que é automático são só as escadas dos motores: dentro de cada etapa, buscam a
oportunidade de cada livro até os 12 itens.

O que o Comandante decide, a cada passagem:
  - O DESTINO de cada livro na preparação: prazo encerrado → arquivo; completo (12 itens comprovados ou dispensados) ou
    sem mais nada a buscar → validação (que decide Farol, arquivo ou Chrome); prazo aberto SEM link oficial → Claude no
    Chrome (que acha o edital oficial); sem prazo e sem link oficial → aguarda os motores, sem gastar busca.
  - O TRABALHO do Interceptador e do Chrome: só os livros com o link oficial e com item faltando (nada de buscar o que não
    tem link oficial nem o que já está completo).
  - A ORDEM: Goiás → Brasil (nacional) → internacional → outras capitais e estados; dentro de cada um, as abertas que
    fecham antes.
  - O DOCUMENTO OFICIAL perseguido: o edital, com todas as regras da oportunidade; no regime de incentivo fiscal por lei
    (Rouanet, Goyazes, fundos da criança e do idoso…) não há edital comum: a lei e o chamamento são o documento oficial.
  - As BUSCAS do Espião seguem a mesma ordem de território.
"""
from __future__ import annotations

import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Any

from ..missao import itens as I
from ..nucleo.registro import instanciar

ORDEM_TERRITORIO = ("Goiás", "Brasil", "internacional", "outras capitais e estados")


def territorio(abrangencia: str | None, uf: str | None = None) -> int:
    """0 Goiás · 1 Brasil (nacional) · 2 internacional · 3 outras capitais, estados e municípios."""
    a, u = (abrangencia or "").lower(), (uf or "").upper()
    if a in ("estadual_go", "municipal_go") or u == "GO":
        return 0
    if a == "nacional" or u == "BR":
        return 1
    if a == "internacional":
        return 2
    return 3


def chave_de_busca(abrangencia: str | None, uf: str | None, fim: str | None, hoje: str, faltam: int = 0) -> tuple:
    aberta = bool(fim and fim >= hoje)
    return (territorio(abrangencia, uf), 0 if aberta else 1, fim or "9999", faltam)


def pode_buscar(link_oficial: str | None, completo: bool) -> tuple[bool, str]:
    if completo:
        return False, "completo: nada a buscar"
    if not link_oficial:
        return False, "sem link oficial: a escada não tem o que perseguir"
    return True, "com link oficial e item faltando"


def documento_oficial(regime: str | None) -> str:
    return "a lei e o chamamento" if regime == "incentivo_fiscal" else "o edital, com todas as regras da oportunidade"


def peso_espiao(familia: str) -> float:
    """A ordem de território nas buscas do Espião: Goiás primeiro, depois o Brasil, depois o internacional."""
    f = familia.lower()
    if "goias" in f:
        return 1.6
    if "internacional" in f or f.startswith(("en_", "es_", "fr_", "de_", "it_")) or len(f) == 2:
        return 0.8
    return 1.0


def candidatos(con: sqlite3.Connection, hoje: str) -> dict[str, list[str]]:
    from ...motores.pilotos.interceptador import fila
    na_fila = {lv.id for lv in fila(con, hoje)}
    con.row_factory = None
    certs: dict[str, set[str]] = {}
    for lid, it in con.execute("SELECT livro_id, item FROM certidao WHERE situacao IN ('comprovado', 'dispensado')"):
        certs.setdefault(lid, set()).add(it)
    out: dict[str, list[str]] = {"encerrados": [], "completos": [], "sem_o_que_buscar": [], "ao_chrome_sem_link": [], "aguardam_motores": []}
    for lid, fim, oficial in con.execute(
            "SELECT l.id, d.inscricao_fim, l.link_oficial FROM passaporte p JOIN livro l ON l.id = p.livro_id "
            "JOIN livro_dados d ON d.livro_id = l.id WHERE p.fase = 'preparacao' AND l.situacao NOT IN ('excluido', 'unido') "
            "AND COALESCE(d.validacao, '') <> 'expurgado' AND l.id NOT IN (SELECT livro_unido FROM uniao)"):
        if fim and fim < hoje:
            out["encerrados"].append(lid)
        elif set(I.DOZE) <= certs.get(lid, set()):
            out["completos"].append(lid)
        elif not oficial:
            out["ao_chrome_sem_link" if fim else "aguardam_motores"].append(lid)
        elif lid not in na_fila:
            out["sem_o_que_buscar"].append(lid)
    return out


def comandar(con: sqlite3.Connection, diario, missao, hoje: str | None = None) -> dict[str, Any]:
    """Uma passagem do Comandante sobre o Cartório: o destino de cada livro parado na preparação."""
    from ..cartorio.cartorio import Cartorio
    hoje = hoje or date.today().isoformat()
    c = candidatos(con, hoje)
    cart = Cartorio(con, missao, diario)
    destino: dict[str, int] = {}
    conta = lambda k, ok: destino.__setitem__(k, destino.get(k, 0) + int(ok))  # noqa: E731
    for lid in c["encerrados"]:
        ok, _ = cart.passaporte.mover(lid, "arquivo", "o Comandante arquivou: o prazo encerrou na preparação",
                                      {"gerou": "prazo encerrado", "analise": "interna"})
        conta("arquivo", ok)
    for lid in c["ao_chrome_sem_link"]:
        ok, _ = cart.passaporte.mover(lid, "analise externa", "o Comandante enviou ao Claude no Chrome: prazo aberto sem link oficial (achar o edital oficial)",
                                      {"gerou": "sem link oficial: a escada não tem o que perseguir", "analise": "interna"})
        conta("analise externa", ok)
    for chave, motivo in (("completos", "completo: os 12 itens resolvidos"), ("sem_o_que_buscar", "nada mais a buscar pela escada")):
        for lid in c[chave]:
            ok, _ = cart.passaporte.mover(lid, "validacao", f"o Comandante levou à validação: {motivo}", {"gerou": motivo, "analise": "interna"})
            if ok:
                r = cart.revalidar(lid, {}, f"{motivo}: validado por ordem do Comandante", analise="interna")
                conta(r["etapa"] or "?", True)
    res = {k: len(v) for k, v in c.items()} | {"destino": destino}
    diario.emitir("medicao.registrada", "comandante", {"marcador": "comandante:cartorio", "nivel": "componente", "em": datetime.now().astimezone().isoformat(),
                                                       "valor": float(sum(len(v) for k, v in c.items() if k != "aguardam_motores")), "motivo": str(res)[:500]})
    return res


def no_comandar_cartorio(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem (o Comandante): o comando do Cartório — o destino de cada livro e o trabalho de cada etapa."""
    p = Path(parametros.get("dados", "dados")) / "biblioteca.db"
    if not p.exists():
        return []
    con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    try:
        missao = instanciar(parametros.get("missao", "eldorado.base.missao.oportunidades:MissaoOportunidades"), parametros.get("missao_parametros"))
        return [{"comandante_cartorio": comandar(con, contexto.diario, missao)}]
    finally:
        con.close()
