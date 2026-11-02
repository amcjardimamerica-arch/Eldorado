"""Fase B do expurgo (titular, 02/11/2026): a Biblioteca só com documentos e dados reais e utilizáveis.

Depois da opção A e do B1, cada documento sem uso que sobrou cai em UM destino:
  vincular  — o endereço é da mesma oportunidade de UM livro ativo (mesmo número de oportunidade do Mapa da Cultura,
              mesmo processo do PNCP, mesmo arquivo do Drive, ou a mesma pasta específica do edital): vira achado aceito do
              livro (documento passa a ter uso). Pasta ligada a mais de um livro é ambígua: não vincula.
  chrome    — sinal de oportunidade no endereço sem ano passado (edital, chamada, chamamento, oportunidade, prêmio, bolsa,
              grant…), ou do ano corrente (2026/2027): o Claude no Chrome decide, agrupado por oportunidade. O que for
              real e vigente vira achado novo (passa pela Pertinência e pelo Cartório); o resto sai.
  expurgar  — sem livro, sem achado, sem certidão, sem sinal de oportunidade e de ano passado ou sem ano: sai.
Os documentos não têm mais texto (a leitura efêmera saiu pela R35): a decisão é pelo endereço e pelo vínculo.

  python implantar/fase_b_documentos_2026_11_02.py classificar            # grava a classificação e o lote do Chrome
  python implantar/fase_b_documentos_2026_11_02.py executar               # vincula e expurga (depois: eldorado aplicar)
  python implantar/fase_b_documentos_2026_11_02.py importar <veredito>    # o veredito do Chrome (depois: eldorado aplicar)
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).parent))
from expurgo_claude_2026_11_02 import avaliar  # noqa: E402

DADOS, EVENTOS, SAIDA = Path("dados"), Path("eventos"), Path("verificacao/expurgo")
PARTE = 100
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


def _bib(ro: bool = True) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{DADOS / 'biblioteca.db'}?mode=ro", uri=True)


def classificar() -> dict:
    bib, cer = _bib(), sqlite3.connect(f"file:{DADOS / 'cerebro.db'}?mode=ro", uri=True)
    try:
        descartados = {r[0] for r in cer.execute("SELECT link FROM achado_descartado WHERE link IS NOT NULL")}
        livros = defaultdict(set)
        ativos = "situacao NOT IN ('excluido', 'unido')"
        for i, o, d in bib.execute(f"SELECT id, link_oficial, link_divulgacao FROM livro WHERE {ativos}"):
            for u in (o, d):
                if (k := chave(u)):
                    livros[k].add(i)
        for i, u in bib.execute(f"SELECT a.livro_id, d.url FROM achado a JOIN documento d ON d.id = a.documento_id "
                                f"JOIN livro l ON l.id = a.livro_id WHERE l.{ativos}"):
            if (k := chave(u)):
                livros[k].add(i)
        _, ids, _ = avaliar(bib, 2, "restantes")
        docs = []
        for n in range(0, len(ids), 900):
            lote = ids[n:n + 900]
            docs += bib.execute(f"SELECT id, url, tipo, leitor, sha256 FROM documento WHERE id IN ({','.join('?' * len(lote))})",
                                lote).fetchall()
    finally:
        bib.close(); cer.close()
    saida = {"vincular": [], "chrome": [], "expurgar": []}
    for i, url, tipo, leitor, sha in docs:
        k = chave(url)
        doc = {"id": i, "url": url, "tipo": tipo, "leitor": leitor, "sha256": sha}
        if k and len(livros.get(k, ())) == 1:
            saida["vincular"].append({**doc, "livro_id": next(iter(livros[k]))})
        elif lixo_comprovado(url, descartados):
            saida["expurgar"].append(doc)
        elif "interceptador" in (leitor or "") or tem_sinal(url) or CORRENTE.search(url):
            saida["chrome"].append({**doc, "grupo": k or re.sub(r"#.*", "", url)})
        else:
            saida["expurgar"].append(doc)
    return saida


def _grupos(chrome: list[dict]) -> list[dict]:
    g = defaultdict(list)
    for d in chrome:
        g[d["grupo"]].append(d)
    out = []
    for k, ds in sorted(g.items()):
        gid = "G-" + hashlib.sha1(k.encode()).hexdigest()[:12]
        out.append({"grupo": gid, "chave": k, "documentos": [{"documento_id": d["id"], "url": d["url"]} for d in ds]})
    return out


INSTRUCOES = (
    "Para cada GRUPO (uma oportunidade e os seus documentos), abra os endereços e decida pela FONTE OFICIAL: "
    "'oportunidade' só se for edital/chamada/prêmio/bolsa/fomento REAL, com inscrição aberta ou prevista (não encerrada), "
    "para organizações da sociedade civil, pessoas da cultura ou projetos sociais; informe titulo, orgao, link_oficial "
    "(a página ou o PDF do órgão), prazo_inscricao (AAAA-MM-DD) e o trecho literal que comprova o prazo. "
    "'vincular' se a oportunidade já for um livro do Eldorado (informe livro_id). 'descartar' em todo o resto (notícia, "
    "resultado, encerrada, licitação/compra, credenciamento, vaga de emprego/estágio, página institucional, link quebrado), "
    "com o motivo. Nunca invente: sem comprovação na fonte, 'descartar'.")


def gravar_classificacao(c: dict) -> list[Path]:
    dia = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    SAIDA.mkdir(parents=True, exist_ok=True)
    resumo = {k: len(v) for k, v in c.items()}
    (SAIDA / f"fase-b-classificacao-{dia}.json").write_text(json.dumps({"resumo": resumo, **c}, ensure_ascii=False, indent=1),
                                                              encoding="utf-8")
    grupos = _grupos(c["chrome"])
    arquivos = []
    for n in range(0, len(grupos), PARTE):
        p = SAIDA / f"lote-chrome-documentos-{dia}-parte-{n // PARTE + 1:02d}.json"
        p.write_text(json.dumps({"lote": p.stem, "criado_em": datetime.now(timezone.utc).isoformat(), "instrucoes": INSTRUCOES,
                                 "formato_do_veredito": {"vereditos": [{"grupo": "G-…", "decisao": "oportunidade | vincular | descartar",
                                                                        "motivo": "…", "titulo": "…", "orgao": "…",
                                                                        "link_oficial": "…", "prazo_inscricao": "AAAA-MM-DD",
                                                                        "trecho": "…", "livro_id": "…"}]},
                                 "grupos": grupos[n:n + PARTE]}, ensure_ascii=False, indent=1), encoding="utf-8")
        arquivos.append(p)
    print(f"classificação: {resumo} · grupos no Chrome: {len(grupos)} em {len(arquivos)} parte(s)")
    return arquivos


def _diario():
    from eldorado.base.nucleo.eventos import Diario
    return Diario(str(EVENTOS), "expurgo-claude")


def _vinculo(dia, doc_id: int, sha: str, url: str, livro: str, como: str) -> None:
    hoje = datetime.now(timezone.utc).isoformat()
    dia.emitir("achado.entregue", "expurgo-claude", {
        "id": f"vinculo-documento-{doc_id}", "motor": MOTOR, "encontrado_em": hoje[:10], "link_divulgacao": url,
        "link_oficial": url, "livro_id": livro, "decisao": "aceito", "motivo": como, "documento_sha256": sha,
        "dados": {"livro_id": livro, "abordagem": "anexos completos"}})


def executar() -> int:
    from eldorado.base.cartorio.expurgo_claude import registrar
    c = classificar()
    dia = _diario()
    for d in c["vincular"]:
        _vinculo(dia, d["id"], d["sha256"], d["url"], d["livro_id"],
                 "fase B (02/11/2026): documento da mesma oportunidade do livro (mesmo número, processo ou pasta do edital)")
    for d in c["expurgar"]:
        dia.emitir("documento.descartado", "expurgo-claude", {"documento_id": d["id"]})
    arq = registrar({"documentos_vinculados_a_livro": len(c["vincular"]), "documentos_sem_uso": len(c["expurgar"]),
                     "documentos_para_o_chrome": len(c["chrome"])},
                    "fase B (titular, 02/11/2026): vinculados os documentos de livro ativo; expurgados os sem livro, sem achado e "
                    "sem sinal de oportunidade vigente; os com sinal seguem ao Claude no Chrome")
    print(f"vinculados {len(c['vincular'])} · expurgados {len(c['expurgar'])} · no Chrome {len(c['chrome'])} · registro {arq}")
    return 0


def importar(arquivo: Path) -> int:
    """O veredito do Chrome: oportunidade → achado novo; vincular → achado do livro; descartar → o documento sai."""
    ret = json.loads(arquivo.read_text(encoding="utf-8"))
    grupos = {}
    for p in sorted(SAIDA.glob("lote-chrome-documentos-*-parte-*.json")):
        for g in json.loads(p.read_text(encoding="utf-8"))["grupos"]:
            grupos[g["grupo"]] = g
    bib = _bib()
    sha = {r[0]: (r[1], r[2]) for r in bib.execute("SELECT id, sha256, url FROM documento")}
    livros = {r[0] for r in bib.execute("SELECT id FROM livro WHERE situacao NOT IN ('excluido', 'unido')")}
    bib.close()
    dia, conta, hoje = _diario(), Counter(), datetime.now(timezone.utc).date().isoformat()
    for v in ret.get("vereditos", []):
        g = grupos.get(v.get("grupo"))
        if g is None:
            conta["grupo desconhecido"] += 1
            continue
        docs = [d for d in g["documentos"] if d["documento_id"] in sha]
        dec = v.get("decisao")
        if dec == "descartar" or (dec == "oportunidade" and not (v.get("link_oficial") and v.get("trecho"))):
            for d in docs:
                dia.emitir("documento.descartado", "expurgo-claude", {"documento_id": d["documento_id"]})
            conta["descartar" if dec == "descartar" else "oportunidade sem comprovação → descartar"] += 1
        elif dec == "vincular" and v.get("livro_id") in livros:
            for d in docs:
                _vinculo(dia, d["documento_id"], sha[d["documento_id"]][0], d["url"], v["livro_id"],
                         f"fase B (Chrome): {v.get('motivo') or 'documento do livro'}"[:300])
            conta["vincular"] += 1
        elif dec == "oportunidade":
            d0 = docs[0] if docs else None
            dia.emitir("achado.entregue", MOTOR, {
                "id": f"chrome-{v['grupo']}", "motor": MOTOR, "encontrado_em": hoje,
                "link_divulgacao": d0["url"] if d0 else v["link_oficial"], "link_oficial": v["link_oficial"],
                "titulo": (v.get("titulo") or "")[:300] or None,
                "dados": {"orgao": v.get("orgao"), "origem": "fase B do expurgo (Claude no Chrome, 02/11/2026)",
                          "itens": {"Prazo de inscrição": {"valor": v.get("prazo_inscricao"), "trecho": v.get("trecho"),
                                                           "fonte": v["link_oficial"]}}},
                **({"documento_sha256": sha[d0["documento_id"]][0]} if d0 else {})})
            conta["oportunidade"] += 1
        else:
            conta["recusado (decisão inválida ou livro inexistente)"] += 1
    print(dict(conta), "· aplique com: eldorado aplicar")
    return 0


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "classificar"
    if cmd == "classificar":
        gravar_classificacao(classificar())
        return 0
    if cmd == "executar":
        return executar()
    if cmd == "importar" and len(sys.argv) > 2:
        return importar(Path(sys.argv[2]))
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
