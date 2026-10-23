"""A etapa 5 do Cartório: a ANÁLISE EXTERNA pelo Claude no Chrome (titular, 22/10/2026).

O Cartório prepara o LOTE (os livros na etapa 5, as abertas primeiro, cada um com os links, as certidões com trecho e
página, e o que falta) e importa o VEREDITO que volta do Chrome: por livro, válido ou descartar; os itens encontrados
(com o trecho literal, a página e o endereço); as dispensas (com a justificativa: o requisito não existe naquele edital);
e o aprendizado. O Cartório valida e armazena; o livro segue na linha (ouro com prazo aberto → Farol; encerrada →
arquivo; faltando, aguarda novo veredito).

Pastas: verificacao/lotes/ (o que vai ao Chrome) e verificacao/vereditos/ (o que volta; importado, vai a importados/).
"""
from __future__ import annotations

import json
import sqlite3
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import msgspec

from ..missao import itens as I
from ..nucleo.eventos import Diario, agora

INSTRUCOES = (
    "Para cada livro: abra o link oficial (e, se preciso, a divulgação). Confira cada certidão na fonte. Para cada item que falta, "
    "traga o valor com o TRECHO LITERAL do documento oficial, a página e o endereço; ou a DISPENSA, com a justificativa de que o "
    "requisito não existe naquele edital (escrita como 'não se aplica a este edital porque…' ou 'não há recurso previsto…'; objeto, "
    "órgão, esfera, território e prazo de inscrição nunca se dispensam). Se o livro não for uma oportunidade válida para a missão, "
    "decida 'descartar' com o motivo. "
    "Registre em 'aprendizado' o que o sistema deveria ter feito para achar sozinho (onde estava a informação, que caminho funcionou).")


class ItemEncontrado(msgspec.Struct):
    item: str
    valor: str
    trecho: str
    pagina: int | None = None
    url: str | None = None


class Dispensa(msgspec.Struct):
    item: str
    justificativa: str


class Veredito(msgspec.Struct):
    livro_id: str
    decisao: str                                   # "valido" ou "descartar"
    motivo: str | None = None
    como_encontrou: str | None = None
    itens: list[ItemEncontrado] = []
    dispensas: list[Dispensa] = []
    aprendizado: str | None = None


class Retorno(msgspec.Struct):
    vereditos: list[Veredito]
    lote: str | None = None


def gerar_lote(con: sqlite3.Connection, hoje: date, maximo: int = 40) -> dict[str, Any]:
    con.row_factory = sqlite3.Row
    livros = []
    for lv in con.execute("SELECT l.*, d.inscricao_fim, d.situacao_prazo FROM livro l JOIN passaporte p ON p.livro_id = l.id "
                          "LEFT JOIN livro_dados d ON d.livro_id = l.id WHERE p.fase = 'analise externa' AND l.situacao <> 'excluido' "
                          "ORDER BY (d.situacao_prazo = 'aberta') DESC, d.inscricao_fim"):
        certs = I.melhor([dict(c) for c in con.execute("SELECT * FROM certidao WHERE livro_id=? AND situacao IN ('comprovado','dispensado')", (lv["id"],))])
        validas = {k: v for k, v in certs.items() if I.resolvido(v)}
        livros.append({"livro_id": lv["id"], "titulo": lv["titulo"], "orgao": lv["orgao"], "uf": lv["uf"], "link_oficial": lv["link_oficial"],
                       "link_divulgacao": lv["link_divulgacao"], "estrela": lv["estrela"], "selo_livro": lv["selo_livro"],
                       "prazo": lv["situacao_prazo"], "fim_inscricao": lv["inscricao_fim"],
                       "certidoes": [{"item": k, "valor": v["valor"], "trecho": v.get("trecho"), "pagina": v.get("pagina")}
                                     for k, v in sorted(validas.items())],
                       "faltam": I.faltando(validas)})
        if len(livros) >= maximo:
            break
    return {"lote": f"lote-{hoje.isoformat()}", "gerado_em": agora(), "instrucoes": INSTRUCOES, "itens_validos": list(I.DOZE),
            "formato_do_veredito": {"vereditos": [{"livro_id": "…", "decisao": "valido | descartar", "motivo": "…", "como_encontrou": "…",
                                                   "itens": [{"item": "…", "valor": "…", "trecho": "…", "pagina": 1, "url": "…"}],
                                                   "dispensas": [{"item": "…", "justificativa": "…"}], "aprendizado": "…"}]},
            "livros": livros}


def importar(retorno: bytes | str, con: sqlite3.Connection, diario: Diario) -> list[dict[str, Any]]:
    """Valida e armazena o veredito do Chrome; o livro segue na linha. Item fora dos 12, sem trecho ou de livro fora da
    etapa 5 é recusado com o motivo (nada entra sem prova)."""
    from .cartorio import Cartorio
    from .passaporte import Passaporte
    r = msgspec.json.decode(retorno, type=Retorno)
    cartorio = Cartorio(con, None, diario)
    saida = []
    for v in r.vereditos:
        fase = Passaporte(con, diario).fase(v.livro_id)
        if fase != "analise externa":
            saida.append({"livro": v.livro_id, "recusado": f"o livro está na etapa {fase}, não na análise externa"})
            continue
        diario.emitir("veredito.gravado", "chrome", {"livro_id": v.livro_id, "origem": "chrome", "decisao": v.decisao, "motivo": v.motivo,
                                                     "como_encontrou": v.como_encontrou, "em": agora()})
        if v.aprendizado:
            diario.emitir("aprendizado.registrado", "chrome", {"modulo": "analise externa", "o_que": v.aprendizado[:2000],
                                                               "evidencia": f"veredito do Chrome para {v.livro_id} ({r.lote or 'sem lote'})",
                                                               "criado_em": agora(), "expira_em": (date.today() + timedelta(days=29)).isoformat()})
        if v.decisao == "descartar":
            diario.emitir("livro.excluido_logicamente", "chrome", {"id": v.livro_id, "atualizado_em": agora(),
                                                                   "justificativa_exclusao": f"descartado na análise externa: {v.motivo or 'sem motivo'}"})
            saida.append({"livro": v.livro_id, "descartado": True})
            continue
        extras, recusas = {}, []
        for it in v.itens:
            if it.item not in I.DOZE or not it.trecho.strip():
                recusas.append(f"{it.item}: fora dos 12 itens ou sem trecho")
                continue
            c = {"livro_id": v.livro_id, "item": it.item, "valor": it.valor[:300], "trecho": it.trecho[:500], "pagina": it.pagina,
                 "fase": "verificacao externa", "situacao": "comprovado", "em": agora()}
            diario.emitir("certidao.gravada", "chrome", c)
            extras[it.item] = c
        for d in v.dispensas:
            if d.item not in I.DOZE or not I.dispensa_valida(d.item, d.justificativa):
                recusas.append(f"dispensa de {d.item}: recusada (o núcleo nunca se dispensa; a justificativa precisa dizer que o item "
                               f"não se aplica a este edital, com ao menos 20 caracteres)")
                continue
            c = {"livro_id": v.livro_id, "item": d.item, "valor": None, "fase": "verificacao externa", "situacao": "dispensado",
                 "justificativa": d.justificativa[:500], "em": agora()}
            diario.emitir("certidao.gravada", "chrome", c)
            extras[d.item] = c
        gerou = f"veredito do Chrome: {len(extras)} item(ns) ou dispensa(s)" + (f"; recusados: {'; '.join(recusas)}" if recusas else "")
        saida.append(cartorio.revalidar(v.livro_id, extras, gerou) | {"recusas": recusas})
    return saida


def no_analise_externa(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem: importa os vereditos novos do Chrome e prepara o lote do dia (se houver livros na etapa 5)."""
    p = Path(parametros.get("dados", "dados")) / "biblioteca.db"
    pasta = Path(parametros.get("pasta", "verificacao"))
    if not p.exists():
        return []
    con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    resultado = {"importados": 0, "lote": None}
    try:
        (pasta / "vereditos" / "importados").mkdir(parents=True, exist_ok=True)
        for arq in sorted((pasta / "vereditos").glob("*.json")):
            try:
                resultado["importados"] += len(importar(arq.read_bytes(), con, contexto.diario))
                arq.rename(pasta / "vereditos" / "importados" / arq.name)
            except msgspec.ValidationError as e:
                contexto.diario.emitir("alarme.aberto", "analise externa", {"gravidade": "media", "modulo": "analise externa", "aberto_em": agora(),
                                                                            "mensagem": f"veredito {arq.name} fora do formato: {str(e)[:200]}"})
        hoje = date.today()
        destino = pasta / "lotes" / f"lote-{hoje.isoformat()}.json"
        if not destino.exists():
            lote = gerar_lote(con, hoje)
            if lote["livros"]:
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_text(json.dumps(lote, ensure_ascii=False, indent=1), encoding="utf-8")
                resultado["lote"] = destino.name
    finally:
        con.close()
    return [resultado]
