"""A MANUTENÇÃO DO EXPURGO a cada passagem (titular, 02/11/2026 — R36): a informação coletada que NÃO virou livro e foi
investigada sem êxito é liberada pelo próprio sistema; ao menor sinal de oportunidade, vai ao Claude no Chrome.

  - o livro nunca é apagado (a trava continua); o que sai é só a leitura sem livro;
  - ACHADO sem livro barrado pelo portão (o sistema já decidiu que não é oportunidade) de dias anteriores → descartado,
    com o registro no Cérebro (achado_descartado); os motores legislativos ficam (R35);
  - DOCUMENTO sem uso há mais de 2 h (sem certidão, sem achado, não é o endereço de livro ativo):
      vincular  — mesma oportunidade de UM livro ativo (mesmo número, processo, arquivo ou pasta do edital) → achado do livro;
      chrome    — sinal de oportunidade no endereço sem ano passado, ou do ano corrente → lote do Claude no Chrome
                  (verificacao/expurgo/lote-chrome-documentos-<dia>-auto.json); nada sai sem o veredito;
      descartar — lixo comprovado (link já descartado, listagem, ato encerrado de ano passado) ou sem nenhum sinal → sai;
  - o veredito do Chrome sobre os documentos (verificacao/expurgo/vereditos/*.json) é importado aqui e vai a importados/;
  - cada passagem que liberar algo grava o registro em expurgos/ (por: sistema).
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from .leitura_efemera import MOTORES_LEGISLATIVOS

MOTOR = "analise-externa"
GENERICO = re.compile(r"/(wp-content|sites/default/files|uploads|files|arquivos|documentos|downloads|media|storage|apifront|"
                      r"portal|edicoes|jsp|visualiza|publicacoes[_-]ver[_-]conteudo|wps|wcm|noticias|news|blog|tag|categoria|"
                      r"20\d\d|acesso-a-informacao|licitacoes-e-contratos)(/|$)", re.I)
SINAL = re.compile(r"edital|editais|chamada|chamamento|oportunidade|opportunity|sele[cç][aã]o|selecao|inscri|premio|pr[eê]mio|"
                   r"fellowship|grant|bolsa|convocat|fomento|financiamento|patroc|apoio|incentivo|lei-rouanet|pnab|aldir", re.I)
PASSADO = re.compile(r"(?<!\d)(19\d\d|20(0\d|1\d|2[0-5]))(?!\d)")
CORRENTE = re.compile(r"(?<!\d)202[67](?!\d)")
LISTAGEM = re.compile(r"/(tags?|categor(y|ia)s?|busca|search|page/\d+|arquivo|archive|noticias/?$|editais/?$)(/|\?|$)|[?&](s|q|page)=", re.I)
ENCERRADO = re.compile(r"resultado|homologa|extrato|ratifica|dispensa|inexigibil|aditivo|termo-de-(fomento|colabora)|"
                       r"prorroga|errata|convoca[cç][aã]o-para-assinatura|habilitad", re.I)
ATIVOS = "situacao NOT IN ('excluido', 'unido')"


def chave(url: str | None) -> str | None:
    """A identidade da oportunidade no endereço (None quando o endereço não identifica uma só)."""
    if not url:
        return None
    u = urlsplit(url)
    host, p = u.netloc.lower().removeprefix("www."), u.path
    m = re.search(r"/(opportunity|oportunidade|projeto|editais|edital)/((?!(?:19|20)\d\d(?:/|$))\d{3,})", p, re.I)
    if m:
        return f"{host}/{m.group(1).lower()}/{m.group(2)}"
    m = re.search(r"(\d{14}-\d-\d{6}/\d{4})", url)
    if m:
        return "pncp/" + m.group(1)
    m = re.search(r"drive\.google\.com/(?:file/d/|open\?id=)([\w-]{20,})", url)
    if m:
        return "drive/" + m.group(1)
    d = p.rsplit("/", 1)[0].rstrip("/")
    ult = d.rsplit("/", 1)[-1]
    if GENERICO.search(d + "/") or d.count("/") < 2 or ult.count("-") < 2 or re.fullmatch(r"\d{4}-\d\d-\d\d", ult):
        return None
    return host + d.lower()


def tem_sinal(url: str) -> bool:
    return bool(SINAL.search(url)) and not PASSADO.search(url)


def lixo_comprovado(url: str, descartados: set[str]) -> bool:
    return url in descartados or bool(LISTAGEM.search(url)) or bool(ENCERRADO.search(url) and PASSADO.search(url))


def destino(url: str, leitor: str | None, descartados: set[str], livros_da_chave: set[str]) -> str:
    """Para onde vai um documento sem uso: vincular, chrome ou descartar (a regra R36)."""
    if len(livros_da_chave) == 1:
        return "vincular"
    if lixo_comprovado(url, descartados):
        return "descartar"
    if "interceptador" in (leitor or "") or tem_sinal(url) or CORRENTE.search(url):
        return "chrome"
    return "descartar"


def _ja_no_chrome(pasta: Path) -> set[int]:
    ids: set[int] = set()
    for p in pasta.glob("lote-chrome-documentos-*.json"):
        try:
            for g in json.loads(p.read_text(encoding="utf-8")).get("grupos", []):
                ids |= {d["documento_id"] for d in g.get("documentos", [])}
        except (OSError, ValueError, KeyError):
            continue
    return ids


def avaliar(bib: sqlite3.Connection, cer: sqlite3.Connection | None, pasta: Path, horas: float = 2) -> dict[str, list]:
    agora = datetime.now(timezone.utc)
    corte = (agora - timedelta(hours=horas)).isoformat()
    leg = ",".join("?" * len(MOTORES_LEGISLATIVOS))
    achados = bib.execute(
        "SELECT id, motor, encontrado_em, decisao, motivo, COALESCE(link_oficial, link_divulgacao) FROM achado "
        f"WHERE livro_id IS NULL AND decisao = 'barrado' AND COALESCE(encontrado_em, '') < ? AND motor NOT IN ({leg})",
        (corte[:10], *MOTORES_LEGISLATIVOS)).fetchall()
    descartados: set[str] = set()
    if cer is not None:
        try:
            descartados = {r[0] for r in cer.execute("SELECT link FROM achado_descartado WHERE link IS NOT NULL")}
        except sqlite3.Error:
            pass
    descartados |= {a[5] for a in achados if a[5]}
    livros: dict[str, set[str]] = defaultdict(set)
    enderecos: set[str] = set()
    for i, o, d in bib.execute(f"SELECT id, link_oficial, link_divulgacao FROM livro WHERE {ATIVOS}"):
        for u in (o, d):
            if u:
                enderecos.add(u)
            if (k := chave(u)):
                livros[k].add(i)
    for i, u in bib.execute(f"SELECT a.livro_id, d.url FROM achado a JOIN documento d ON d.id = a.documento_id "
                            f"JOIN livro l ON l.id = a.livro_id WHERE l.{ATIVOS}"):
        if (k := chave(u)):
            livros[k].add(i)
    usados = {r[0] for r in bib.execute("SELECT documento_id FROM certidao WHERE documento_id IS NOT NULL UNION "
                                        "SELECT documento_id FROM achado WHERE documento_id IS NOT NULL")}
    no_chrome = _ja_no_chrome(pasta)
    out: dict[str, list] = {"achados": list(achados), "vincular": [], "chrome": [], "descartar": []}
    for i, url, leitor, sha in bib.execute("SELECT id, url, leitor, sha256 FROM documento WHERE COALESCE(obtido_em, '') < ?", (corte,)):
        if i in usados or url in enderecos or i in no_chrome:
            continue
        k = chave(url)
        dest = destino(url, leitor, descartados, livros.get(k, set()) if k else set())
        doc = {"id": i, "url": url, "leitor": leitor, "sha256": sha, "grupo": k or re.sub(r"#.*", "", url or "")}
        if dest == "vincular":
            doc["livro_id"] = next(iter(livros[k]))
        out[dest].append(doc)
    return out


def _vinculo(diario, doc: dict, livro: str, como: str) -> None:
    hoje = datetime.now(timezone.utc).date().isoformat()
    diario.emitir("achado.entregue", "expurgo-sistema", {
        "id": f"vinculo-documento-{doc['id']}", "motor": MOTOR, "encontrado_em": hoje, "link_divulgacao": doc["url"],
        "link_oficial": doc["url"], "livro_id": livro, "decisao": "aceito", "motivo": como[:300], "documento_sha256": doc["sha256"],
        "dados": {"livro_id": livro, "abordagem": "anexos completos"}})


def _lote_chrome(pasta: Path, docs: list[dict]) -> Path | None:
    if not docs:
        return None
    from ..cartorio import manutencao_expurgo as _m  # noqa: F401 (o mesmo módulo; as instruções ficam junto do lote)
    dia = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    arq = pasta / f"lote-chrome-documentos-{dia}-auto.json"
    atual = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {"lote": arq.stem, "instrucoes": INSTRUCOES,
                                                                              "formato_do_veredito": FORMATO, "grupos": []}
    atual["instrucoes"], atual["lote"], atual["formato_do_veredito"] = INSTRUCOES, arq.stem, FORMATO   # R41: a instrução de agora
    grupos = {g["grupo"]: g for g in atual["grupos"]}
    for d in docs:
        gid = "G-" + hashlib.sha1(d["grupo"].encode()).hexdigest()[:12]
        g = grupos.setdefault(gid, {"grupo": gid, "chave": d["grupo"], "documentos": []})
        if all(x["documento_id"] != d["id"] for x in g["documentos"]):
            g["documentos"].append({"documento_id": d["id"], "url": d["url"]})
    atual["grupos"] = sorted(grupos.values(), key=lambda g: g["chave"])
    atual["atualizado_em"] = datetime.now(timezone.utc).isoformat()
    pasta.mkdir(parents=True, exist_ok=True)
    arq.write_text(json.dumps(atual, ensure_ascii=False, indent=1), encoding="utf-8")
    return arq


INSTRUCOES = (
    "ENTREGA COMPLETA E TOTAL (R41): entregue um veredito decisivo para CADA grupo deste lote, num único arquivo, com o 'lote' "
    "copiado deste arquivo; não entregue parcial — o sistema recusa por inteiro o veredito que não cobre todos os grupos. "
    "Para cada GRUPO (uma oportunidade e os seus documentos), abra os endereços e decida pela FONTE OFICIAL: "
    "'oportunidade' só se for edital/chamada/prêmio/bolsa/fomento REAL, com inscrição aberta ou prevista (não encerrada); "
    "informe titulo, orgao, link_oficial, prazo_inscricao (AAAA-MM-DD) e o trecho literal que comprova o prazo. "
    "'vincular' se a oportunidade já for um livro do Eldorado (informe livro_id). 'descartar' em todo o resto, com o motivo. "
    "Nunca invente: sem comprovação na fonte, 'descartar'.")
FORMATO = {"lote": "<o nome deste arquivo>", "vereditos": [{"grupo": "G-…", "decisao": "oportunidade | vincular | descartar", "motivo": "…", "titulo": "…",
                          "orgao": "…", "link_oficial": "…", "prazo_inscricao": "AAAA-MM-DD", "trecho": "…", "livro_id": "…"}]}


def importar_veredito(ret: dict, bib: sqlite3.Connection, pasta: Path, diario, exigir_completo: bool = True) -> dict[str, int]:
    """O veredito do Chrome sobre os grupos de documentos: oportunidade → achado novo; vincular → achado do livro; descartar → sai."""
    # R41 (titular, 03/11/2026): o veredito cobre TODOS os grupos do lote que diz ser, ou nada entra
    nome = str(ret.get("lote") or "")
    arq_lote = pasta / f"{Path(nome).stem}.json" if nome else None
    if not arq_lote or not arq_lote.exists():
        diario.emitir("alarme.aberto", "expurgo-sistema", {"gravidade": "media", "modulo": "expurgo", "aberto_em": datetime.now(timezone.utc).isoformat(),
                                                          "mensagem": "veredito de documentos recusado (R41): sem o 'lote' do arquivo de origem"})
        return {"recusado (R41)": 1}
    do_lote = {g["grupo"] for g in json.loads(arq_lote.read_text(encoding="utf-8")).get("grupos", [])}
    feitos = {v.get("grupo") for v in ret.get("vereditos", []) if str(v.get("decisao") or "").lower() in ("oportunidade", "vincular", "descartar")}
    if exigir_completo and do_lote - feitos:
        diario.emitir("alarme.aberto", "expurgo-sistema", {"gravidade": "media", "modulo": "expurgo", "aberto_em": datetime.now(timezone.utc).isoformat(),
                                                          "mensagem": f"veredito de documentos recusado (R41, nada parcial): {len(feitos & do_lote)} de "
                                                                      f"{len(do_lote)} grupos do {nome}"})
        return {"recusado (R41): grupos sem veredito": len(do_lote - feitos)}
    grupos: dict[str, dict] = {}
    for p in pasta.glob("lote-chrome-documentos-*.json"):
        try:
            for g in json.loads(p.read_text(encoding="utf-8")).get("grupos", []):
                grupos[g["grupo"]] = g
        except (OSError, ValueError, KeyError):
            continue
    sha = {r[0]: r[1] for r in bib.execute("SELECT id, sha256 FROM documento")}
    livros = {r[0] for r in bib.execute(f"SELECT id FROM livro WHERE {ATIVOS}")}
    # 05/11/2026: o livro que o Chrome indicou pode ter sido unido ou expurgado entre a leitura e a importação — o vínculo
    # segue a união até o livro que ficou; o documento de um livro expurgado sai junto (antes: 583 vereditos recusados)
    uniao = {u: f for f, u in bib.execute("SELECT livro_que_fica, livro_unido FROM uniao")}
    expurgados = {r[0] for r in bib.execute("SELECT id FROM livro WHERE situacao = 'excluido'")}

    def _destino(lid):
        vistos = set()
        while lid in uniao and lid not in vistos:
            vistos.add(lid)
            lid = uniao[lid]
        return lid
    conta: dict[str, int] = defaultdict(int)
    hoje = datetime.now(timezone.utc).date().isoformat()
    for v in ret.get("vereditos", []):
        g = grupos.get(v.get("grupo"))
        if g is None:
            conta["grupo desconhecido"] += 1
            continue
        docs = [{"id": d["documento_id"], "url": d["url"], "sha256": sha[d["documento_id"]]} for d in g["documentos"] if d["documento_id"] in sha]
        dec = v.get("decisao")
        if dec == "descartar" or (dec == "oportunidade" and not (v.get("link_oficial") and v.get("trecho"))):
            for d in docs:
                diario.emitir("documento.descartado", "expurgo-sistema", {"documento_id": d["id"]})
            conta["descartar"] += 1
        elif dec == "vincular" and _destino(v.get("livro_id")) in livros:
            for d in docs:
                _vinculo(diario, d, _destino(v["livro_id"]), f"Chrome: {v.get('motivo') or 'documento do livro'}")
            conta["vincular"] += 1
        elif dec == "vincular" and _destino(v.get("livro_id")) in expurgados:
            for d in docs:
                diario.emitir("documento.descartado", "expurgo-sistema", {"documento_id": d["id"]})
            conta["descartar (o livro foi expurgado)"] += 1
        elif dec == "oportunidade":
            d0 = docs[0] if docs else None
            diario.emitir("achado.entregue", MOTOR, {
                "id": f"chrome-{v['grupo']}", "motor": MOTOR, "encontrado_em": hoje,
                "link_divulgacao": d0["url"] if d0 else v["link_oficial"], "link_oficial": v["link_oficial"],
                "titulo": (v.get("titulo") or "")[:300] or None,
                "dados": {"orgao": v.get("orgao"), "origem": "documento sem uso conferido pelo Claude no Chrome",
                          "itens": {"Prazo de inscrição": {"valor": v.get("prazo_inscricao"), "trecho": v.get("trecho"), "fonte": v["link_oficial"]}}},
                **({"documento_sha256": d0["sha256"]} if d0 else {})})
            conta["oportunidade"] += 1
        else:
            conta["recusado"] += 1
    return dict(conta)


def executar(bib: sqlite3.Connection, cer: sqlite3.Connection | None, diario, pasta: Path = Path("verificacao/expurgo"),
             registrar_em: Path | None = None) -> dict[str, Any]:
    """Uma passagem da manutenção: importa os vereditos, libera o invalidado, vincula e manda o sinal ao Chrome."""
    res: dict[str, Any] = {}
    entrada = pasta / "vereditos"
    if entrada.exists():
        (entrada / "importados").mkdir(exist_ok=True)
        for arq in sorted(entrada.glob("*.json")):
            try:
                res[arq.name] = importar_veredito(json.loads(arq.read_text(encoding="utf-8")), bib, pasta, diario)
                arq.rename(entrada / "importados" / arq.name)
            except (OSError, ValueError) as e:
                res[arq.name] = {"erro": str(e)[:200]}
    a = avaliar(bib, cer, pasta)
    agora = datetime.now(timezone.utc).isoformat()
    for i, m, enc, dec, mot, link in a["achados"]:
        diario.emitir("achado.descartado", "expurgo-sistema", {"id": i, "motor": m, "encontrado_em": enc, "decisao": dec,
                                                               "motivo": (mot or "")[:300], "link": link, "descartado_em": agora})
    for d in a["descartar"]:
        diario.emitir("documento.descartado", "expurgo-sistema", {"documento_id": d["id"]})
    for d in a["vincular"]:
        _vinculo(diario, d, d["livro_id"], "manutenção (R36): documento da mesma oportunidade do livro")
    lote = _lote_chrome(pasta, a["chrome"])
    res.update(achados_descartados=len(a["achados"]), documentos_descartados=len(a["descartar"]),
               documentos_vinculados=len(a["vincular"]), documentos_ao_chrome=len(a["chrome"]), lote=str(lote) if lote else None)
    if a["achados"] or a["descartar"]:
        from .expurgo_claude import registrar
        registrar({"achados_sem_livro": len(a["achados"]), "documentos_sem_uso": len(a["descartar"]),
                   "documentos_vinculados_a_livro": len(a["vincular"]), "documentos_para_o_chrome": len(a["chrome"])},
                  "manutenção do sistema (R36): leituras sem livro investigadas sem êxito liberadas; o sinal de oportunidade vai ao Chrome",
                  por="sistema")
    return res


def no_manutencao_expurgo(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem (R36): a manutenção do expurgo a cada passagem."""
    dados = Path(parametros.get("dados", "dados"))
    if not (dados / "biblioteca.db").exists():
        return []
    bib = sqlite3.connect(f"file:{dados / 'biblioteca.db'}?mode=ro", uri=True)
    cer = sqlite3.connect(f"file:{dados / 'cerebro.db'}?mode=ro", uri=True) if (dados / "cerebro.db").exists() else None
    try:
        res = executar(bib, cer, contexto.diario, Path(parametros.get("pasta", "verificacao/expurgo")))
    finally:
        bib.close()
        if cer is not None:
            cer.close()
    return [{"manutencao_expurgo": res}]
