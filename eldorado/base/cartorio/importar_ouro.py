"""16/11/2026 (titular): a importação dos LIVROS DE OURO — o resultado da validação de todos os livros no edital, pelos 20
agentes do Claude no Chrome (lotes ouro-2026-11-15-parte-1 a 3). Cada arquivo em verificacao/ouro/ traz os vereditos e os
livros que voltam à análise externa (sem fonte localizada, sem validação no edital, não verificados).

  - valido, encerrada e descartar (o expurgo): pelo importador da análise externa (os itens com trecho, as dispensas, as
    edições anteriores, o arquivo das encerradas, a exclusão lógica; o catálogo, R44, nunca sai; o descarte de um livro do
    Farol fica para a titular);
  - mecanismo (lei de incentivo, emenda, fundo, programa permanente): entra como válido, marcado mecanismo;
  - unir: a união completa ao livro indicado (identidade.unir);
  - o código de ouro: ABRANGÊNCIA-OBJETO-AÇÃO-NNNN, com o número de série seguinte de cada combinação; o número e o ano do
    edital (a subclassificação interna) e a classificação ficam no livro (livro.ouro);
  - os livros de volta: à análise externa, para a próxima passada do Chrome (não é descarte: não perdem dados).

A conferência: vereditos + livros de volta = o total da parte, sem livro repetido (a cobertura que a R41 exige)."""
from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PASTA = Path("verificacao/ouro")


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def converter(v: dict[str, Any]) -> dict[str, Any] | None:
    """O veredito de ouro no formato do importador da análise externa (None: tratado à parte, como a união)."""
    d = v.get("decisao")
    if d == "unir":
        return None
    dec = {"valido": "valido", "mecanismo": "valido", "encerrada": "encerrada", "descartar": "descartar"}.get(d)
    if not dec:
        return None
    motivo = v.get("motivo_expurgo") or v.get("descarte_categoria") or v.get("motivo_reclassificacao") or v.get("parecer") or ""
    if d == "mecanismo":
        motivo = f"mecanismo permanente (não é edital): {v.get('parecer') or ''}"
    # os agentes nem sempre seguiram o mesmo formato: a página como texto, a edição como objeto — normalizados aqui
    itens = []
    for i in v.get("itens") or []:
        if not (isinstance(i, dict) and i.get("item") and i.get("trecho")):
            continue
        pg = i.get("pagina")
        pg = int(pg) if isinstance(pg, int) or (isinstance(pg, str) and pg.strip().isdigit()) else None
        itens.append({"item": str(i["item"]), "valor": str(i.get("valor") or ""), "trecho": str(i["trecho"]), "pagina": pg,
                      "url": (str(i["url"]) if i.get("url") else None)})
    dispensas = [{"item": str(x["item"]), "justificativa": str(x["justificativa"])} for x in v.get("dispensas") or []
                 if isinstance(x, dict) and x.get("item") and x.get("justificativa")]
    edicoes = []
    for e in v.get("edicoes_anteriores") or []:
        t = e.get("abertura") or e.get("data") if isinstance(e, dict) else e
        if isinstance(t, str) and re.fullmatch(r"\d{4}-\d{2}(-\d{2})?", t.strip()):
            edicoes.append(t.strip())
    return {"livro_id": v["livro_id"], "decisao": dec, "motivo": str(motivo)[:1000], "como_encontrou": v.get("como_encontrou"),
            "itens": itens, "dispensas": dispensas, "aprendizado": v.get("aprendizado"), "link_original": v.get("link_original"),
            "edicoes_anteriores": edicoes}


def _proximo_serial(con: sqlite3.Connection, prefixo: str, usados: dict[str, int]) -> int:
    if prefixo not in usados:
        mx = 0
        try:
            for (c,) in con.execute("SELECT codigo_ouro FROM livro_dados WHERE codigo_ouro LIKE ?", (prefixo + "-%",)):
                m = re.search(r"-(\d{4})$", c or "")
                if m:
                    mx = max(mx, int(m.group(1)))
        except sqlite3.Error:
            pass
        usados[prefixo] = mx
    usados[prefixo] += 1
    return usados[prefixo]


def prefixo(cod: dict[str, Any] | None) -> str | None:
    """ABRANGÊNCIA-OBJETO[-AÇÃO], conferido (abrangência e objeto obrigatórios; a ação só AU, AP ou AQ)."""
    if not cod:
        return None
    a, o, ac = str(cod.get("abrangencia") or "").strip().upper(), str(cod.get("objeto") or "").strip().upper(), str(cod.get("acao") or "").strip().upper()
    if not re.fullmatch(r"[A-Z]{3}\.[A-Z]{2}|[A-Z]{2}|BR|INT|VAR\.[A-Z]{2}", a) or not re.fullmatch(r"[A-Z]\d{2}", o):
        return None
    return f"{a}-{o}" + (f"-{ac}" if ac in ("AU", "AP", "AQ") else "")


def importar_arquivo(caminho: Path, con: sqlite3.Connection, diario, usados: dict[str, int] | None = None) -> dict[str, Any]:
    """usados: os números de série já dados nesta passagem (compartilhados entre os arquivos: os eventos só chegam ao banco
    depois, e as partes importadas juntas repetiriam os números)."""
    from .analise_externa import importar, levar
    from .cartorio import Cartorio
    from .identidade import unir
    pac = json.loads(Path(caminho).read_text(encoding="utf-8"))
    V, volta, total = pac["vereditos"], pac.get("retorno") or [], int(pac.get("total_lote") or 0)
    ids = [v["livro_id"] for v in V] + [r["livro_id"] for r in volta]
    if total and (len(ids) != total or len(set(ids)) != total):
        return {"recusado": f"{pac.get('lote')}: {len(V)} vereditos + {len(volta)} de volta = {len(ids)} ({len(set(ids))} distintos), o lote tem {total}"}
    convertidos = [c for c in (converter(v) for v in V) if c]
    res = importar(json.dumps({"lote": pac.get("lote"), "lote_gerado_em": pac.get("lote_gerado_em"), "vereditos": convertidos}, ensure_ascii=False),
                   con, diario, exigir_completo=False)
    recusados = {r["livro"]: r.get("recusado") for r in res if r.get("recusado") and r.get("livro")}
    existe = {r[0]: r[1] for r in con.execute("SELECT id, situacao FROM livro")}
    unidos = 0
    for v in V:
        if v.get("decisao") == "unir" and v.get("unir_em") and v["unir_em"] != v["livro_id"] and existe.get(v["unir_em"]) not in (None, "excluido", "unido") \
                and existe.get(v["livro_id"]) not in (None, "excluido", "unido"):
            motivo = f"o mesmo edital e a mesma edição (Claude no Chrome, {pac.get('lote')}): {v.get('parecer') or ''}"
            unir(con, diario, v["unir_em"], v["livro_id"], motivo[:500])
            unidos += 1
    usados = {} if usados is None else usados
    codigos = 0
    for v in V:
        if v.get("decisao") not in ("valido", "encerrada", "mecanismo") or v["livro_id"] in recusados:
            continue
        pre = prefixo(v.get("codigo"))
        ed = v.get("edital") or {}
        cat = {"objeto_nome": (v.get("codigo") or {}).get("objeto_nome"), "acao": (v.get("codigo") or {}).get("acao"),
               "tipo": "mecanismo" if v.get("decisao") == "mecanismo" else "edital", "titulo_oficial": v.get("titulo_oficial"),
               "parecer": v.get("parecer"), "validar_proxima_vez": v.get("validar_proxima_vez"), "recorrencia": v.get("recorrencia"),
               "estrela_proposta": v.get("estrela_proposta"), "faltaram": v.get("faltaram"), "catalogo": v.get("catalogo"),
               "edital_identificacao": ed.get("identificacao"), "edital_observacao": ed.get("observacao"), "lote": pac.get("lote")}
        dados = {"livro_id": v["livro_id"], "edital_numero": (str(ed.get("numero") or "").strip() or None),
                 "edital_ano": ed.get("ano") if isinstance(ed.get("ano"), int) else None, "catalogo_ouro": json.dumps(cat, ensure_ascii=False)[:20000]}
        if pre:
            cod = f"{pre}-{_proximo_serial(con, pre, usados):04d}"
            dados.update({"codigo_ouro": cod, "codigo": cod})
        diario.emitir("livro.ouro", "chrome", dados)
        codigos += bool(pre)
    cart = Cartorio(con, None, diario)
    de_volta = 0
    for r in volta:
        if existe.get(r["livro_id"]) in (None, "excluido", "unido"):
            continue
        if levar(cart, r["livro_id"], "analise externa", f"de volta ao Claude no Chrome ({pac.get('lote')}): {r.get('motivo') or ''}"[:300], "ouro"):
            de_volta += 1
    return {"lote": pac.get("lote"), "vereditos": len(V), "importados": len(convertidos) - len(recusados), "recusados": len(recusados),
            "para_a_titular": [k for k, m in recusados.items() if m and "Farol" in m][:200], "unidos": unidos, "codigos_de_ouro": codigos,
            "de_volta_ao_chrome": de_volta, "em": _agora()}


def importar_pasta(con: sqlite3.Connection, diario, pasta: Path = PASTA) -> list[dict[str, Any]]:
    """Os arquivos pendentes de verificacao/ouro/ (cada um uma vez: depois vai a importados/, com o relatório ao lado)."""
    saida = []
    if not pasta.exists():
        return saida
    feitos = pasta / "importados"
    usados: dict[str, int] = {}
    for arq in sorted(pasta.glob("ouro-*.json")):
        # 16/11/2026 (C-13): a parte que já tem relatório não é importada de novo — a gravação leva os arquivos novos, mas não
        # a remoção do original, e ele voltava a cada execução (4.725 vereditos para 1.575 livros, 3 vezes no mesmo dia)
        if (feitos / (arq.stem + "-relatorio.json")).exists():
            continue
        r = importar_arquivo(arq, con, diario, usados)
        saida.append(r)
        if "recusado" not in r:
            feitos.mkdir(exist_ok=True)
            arq.rename(feitos / arq.name)
            (feitos / (arq.stem + "-relatorio.json")).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    return saida
