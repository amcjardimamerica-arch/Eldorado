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
    "traga o valor com o TRECHO LITERAL do documento da oportunidade original, a página e o endereço; informe em 'link_original' o "
    "endereço da oportunidade original (o site do órgão ou do financiador; o livro pode ter só a divulgação); ou a DISPENSA, com a justificativa de que o "
    "requisito não existe naquele edital (escrita como 'não se aplica a este edital porque…' ou 'não há recurso previsto…'; objeto, "
    "órgão, esfera, território e prazo de inscrição nunca se dispensam). Se o livro não for uma oportunidade válida para a missão, "
    "decida 'descartar' com o motivo. "
    "A BASE DO LIVRO (titular, 25/10/2026): todo livro precisa de cinco dados: o site oficial, o site que divulgou, o prazo de "
    "inscrição, a esfera e a área de atuação; a lista 'buscar' de cada livro diz quais faltam. Traga-os com o trecho de prova. "
    "Se não conseguir validar a oportunidade com esses dados, ou se o livro não for uma oportunidade (um anexo, um resultado, "
    "uma notícia), decida 'descartar': o livro não validado é excluído. "
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
    link_original: str | None = None          # a oportunidade original, confirmada pelo Chrome (a divulgação fica como estava)


class Retorno(msgspec.Struct):
    vereditos: list[Veredito]
    lote: str | None = None


def gerar_lote(con: sqlite3.Connection, hoje: date, maximo: int = 100) -> dict[str, Any]:   # 29/10/2026: 100 (eram 40; a fila chegou a 232)
    con.row_factory = sqlite3.Row
    livros = []
    tem_base = "base_buscar" in {r[1] for r in con.execute("PRAGMA table_info(livro_dados)")}
    extra = ", d.base_buscar, d.base_classe" if tem_base else ""
    for lv in con.execute(f"SELECT l.*, d.inscricao_fim, d.situacao_prazo{extra} FROM livro l JOIN passaporte p ON p.livro_id = l.id "
                          "LEFT JOIN livro_dados d ON d.livro_id = l.id WHERE p.fase = 'analise externa' AND l.situacao NOT IN ('excluido', 'unido') "
                          "ORDER BY (d.situacao_prazo = 'aberta') DESC, d.inscricao_fim"):
        certs = I.melhor([dict(c) for c in con.execute("SELECT * FROM certidao WHERE livro_id=? AND situacao IN ('comprovado','dispensado')", (lv["id"],))])
        validas = {k: v for k, v in certs.items() if I.resolvido(v)}
        livros.append({"livro_id": lv["id"], "titulo": lv["titulo"], "orgao": lv["orgao"], "uf": lv["uf"], "link_oficial": lv["link_oficial"],
                       "link_divulgacao": lv["link_divulgacao"], "estrela": lv["estrela"], "selo_livro": lv["selo_livro"],
                       "prazo": lv["situacao_prazo"], "fim_inscricao": lv["inscricao_fim"],
                       "certidoes": [{"item": k, "valor": v["valor"], "trecho": v.get("trecho"), "pagina": v.get("pagina")}
                                     for k, v in sorted(validas.items())],
                       "faltam": I.faltando(validas),
                       # a base do livro (25/10/2026): os dados que o Interceptador não achou em 2 tentativas
                       "buscar": json.loads(lv["base_buscar"] or "[]") if tem_base else [], "classe": lv["base_classe"] if tem_base else None})
        if len(livros) >= maximo:
            break
    return {"lote": f"lote-{hoje.isoformat()}", "gerado_em": agora(), "instrucoes": INSTRUCOES, "itens_validos": list(I.DOZE),
            "formato_do_veredito": {"vereditos": [{"livro_id": "…", "decisao": "valido | descartar", "motivo": "…", "como_encontrou": "…",
                                                   "itens": [{"item": "…", "valor": "…", "trecho": "…", "pagina": 1, "url": "…"}],
                                                   "dispensas": [{"item": "…", "justificativa": "…"}], "aprendizado": "…"}]},
            "livros": livros}


def gerar_lotes_do_dia(con: sqlite3.Connection, pasta_lotes: Path, hoje: date, por_parte: int = 100, reenviar_dias: int = 3) -> list[str]:
    """29/10/2026 (titular: 186 livros na análise externa e o Chrome dizia que tinha terminado): o lote diário era UM, com
    40 livros, os de prazo aberto primeiro; os 'sem prazo' ficavam sempre no fim e 180 livros NUNCA foram ao Chrome. Agora
    o dia cobre a fila inteira, em partes de até 100 (lote-AAAA-MM-DD-1, -2…): todo livro esperando que nunca foi a um lote
    e não tem veredito, e o enviado há mais de 3 dias que não voltou."""
    if list(pasta_lotes.glob(f"lote-{hoje.isoformat()}*.json")):
        return []
    todos = gerar_lote(con, hoje, maximo=100000)
    enviados: dict[str, date] = {}
    for f in pasta_lotes.glob("lote-*.json"):
        try:
            d = date.fromisoformat(f.stem[5:15])
            for x in json.loads(f.read_text(encoding="utf-8")).get("livros", []):
                enviados[x["livro_id"]] = max(enviados.get(x["livro_id"], d), d)
        except (ValueError, OSError):
            continue
    vered = {r[0] for r in con.execute("SELECT DISTINCT livro_id FROM veredito WHERE origem LIKE '%chrome%' OR origem LIKE '%externa%'")}
    fila = [x for x in todos["livros"] if x["livro_id"] not in vered
            and (x["livro_id"] not in enviados or (hoje - enviados[x["livro_id"]]).days > reenviar_dias)]
    nomes = []
    pasta_lotes.mkdir(parents=True, exist_ok=True)
    for n, i in enumerate(range(0, len(fila), por_parte), 1):
        nome = f"lote-{hoje.isoformat()}-{n}"
        (pasta_lotes / f"{nome}.json").write_text(json.dumps({**{k: v for k, v in todos.items() if k != "livros"}, "lote": nome,
                                                              "livros": fila[i:i + por_parte]}, ensure_ascii=False, indent=1), encoding="utf-8")
        nomes.append(nome)
    return nomes


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
        # 29/10/2026 (titular: todo dado de livro é gravado no livro): o veredito vale também para o livro que voltou à
        # preparação (a aberta volta à fila a cada 24 h) e, quando válido, para o que já chegou ao Farol (o trabalho do
        # Chrome se perdia: 7 de 40 recusados no lote de 29/10, com 16 itens comprovados). O descarte de um livro do
        # Farol não é aplicado sozinho: fica para a titular.
        # e (29/10/2026, os remanescentes de 23 a 28/10) para o livro já ARQUIVADO: o válido grava os itens e o veredito no
        # registro da edição encerrada (a revalidação não o tira do arquivo); o descarte o exclui (não era oportunidade)
        if fase not in ("analise externa", "preparacao", "farol", "validacao", "arquivo"):
            saida.append({"livro": v.livro_id, "recusado": f"o livro está na etapa {fase}: o veredito não se aplica"})
            continue
        if fase == "farol" and v.decisao == "descartar":
            saida.append({"livro": v.livro_id, "recusado": "o livro está no Farol: o descarte pelo Chrome precisa da decisão da titular",
                          "para_a_titular": v.motivo})
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
        if v.link_original and v.link_original.startswith("http"):    # a origem confirmada pela análise externa
            diario.emitir("livro.links", "chrome", {"id": v.livro_id, "link_divulgacao": con.execute("SELECT link_divulgacao FROM livro WHERE id = ?",
                                                                                                      (v.livro_id,)).fetchone()[0],
                                                    "link_oficial": v.link_original, "atualizado_em": agora()})
            diario.emitir("livro.origem", "chrome", {"livro_id": v.livro_id, "origem": "confirmado",
                                                     "origem_motivo": "confirmado pela análise externa (Chrome)"})
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


def trazer_vereditos_novos(pasta: Path) -> list[str]:
    """29/10/2026: o ciclo em andamento não via os vereditos enviados ao repositório depois que ele partiu (só os importava
    ao ser religado, e a implantação agora pula o religamento quando o ciclo já tem o código). A cada passagem, os
    vereditos novos da pasta de entrada no repositório vêm para a pasta local (os já importados ficam de fora)."""
    import subprocess

    trazidos: list[str] = []
    try:
        if subprocess.run(["git", "fetch", "-q", "origin", "main"], capture_output=True, timeout=60).returncode != 0:
            return trazidos
        nomes = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", f"{pasta.as_posix()}/vereditos/"],
                               capture_output=True, text=True, timeout=30).stdout.split()
        for n in nomes:
            nome = Path(n).name
            if not nome.endswith(".json") or (pasta / "vereditos" / nome).exists() or (pasta / "vereditos" / "importados" / nome).exists():
                continue
            corpo = subprocess.run(["git", "show", f"origin/main:{n}"], capture_output=True, timeout=60)
            if corpo.returncode == 0 and corpo.stdout:
                (pasta / "vereditos" / nome).write_bytes(corpo.stdout)
                trazidos.append(nome)
    except (OSError, subprocess.SubprocessError):
        pass
    return trazidos


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
        trazer_vereditos_novos(pasta)
        for arq in sorted((pasta / "vereditos").glob("*.json")):
            try:
                resultado["importados"] += len(importar(arq.read_bytes(), con, contexto.diario))
                arq.rename(pasta / "vereditos" / "importados" / arq.name)
                # 29/10/2026: o arquivo movido ganha a hora da importação (a gravação só leva o que mudou desde o início do
                # ciclo; com a data antiga, o registro em importados/ não chegava ao repositório)
                import os as _os

                _os.utime(pasta / "vereditos" / "importados" / arq.name)
            except msgspec.ValidationError as e:
                contexto.diario.emitir("alarme.aberto", "analise externa", {"gravidade": "media", "modulo": "analise externa", "aberto_em": agora(),
                                                                            "mensagem": f"veredito {arq.name} fora do formato: {str(e)[:200]}"})
        hoje = date.today()
        resultado["lote"] = gerar_lotes_do_dia(con, pasta / "lotes", hoje) or None
    finally:
        con.close()
    return [resultado]
