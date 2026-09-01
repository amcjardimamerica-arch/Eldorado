"""Biblioteca de Alexandria — o banco de dados do Farol.

Determinação do titular (01/09/2026): todo o banco passa a se chamar
Biblioteca de Alexandria, com três acervos:

  biblioteca_alexandria/
    leis/<tema>/<tipo>/            normas aplicáveis, separadas por tema e
                                   por tipo de informação legal
    oportunidades/<chave>/<ANO>/   histórico de editais e oportunidades
                                   anteriores — base para apurar o que é
                                   cobrado, recorrências e critérios de
                                   aprovação
    associacoes/<slug>/            uma subpasta por associação
      documentos/                  documentos institucionais
      editais/<nome-do-edital>/    documentos PREENCHIDOS daquele edital
                                   concorrido (ficam disponíveis para
                                   download na Biblioteca do Farol)

Divisão de trabalho: o **Eldorado** alimenta a Biblioteca (identifica, extrai,
converte o edital para texto e fraciona os anexos-modelo em PDF); o **Farol**
lê a Biblioteca, analisa com IA e devolve parecer, prazos e documentos.

Economia de armazenamento: o texto do edital é guardado como .txt; PDF só
permanece quando é documento-modelo preenchível.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, sha256, slug, write_json

RAIZ = ROOT / "biblioteca_alexandria"
LEIS = RAIZ / "leis"
OPORTUNIDADES = RAIZ / "oportunidades"
ASSOCIACOES = RAIZ / "associacoes"

# Temas do acervo jurídico (o tipo da norma vira a subpasta)
# Ordem importa: o primeiro tema cujo padrão casar vence. Os padrões usam
# fronteira de palavra — "proteção de dados" não pode casar com "ECA".
TEMAS = (
    ("gestao_e_controle", r"licita|transpar|prote[çc][ãa]o\s+de\s+dados|protecao_dados|"
                          r"lgpd|controle|presta[çc][ãa]o\s+de\s+contas|13\.?709|14\.?133|12\.?527"),
    ("assistencia_social", r"assistenc|assistênc|socioassisten|\bsuas\b|\bcebas\b|"
                           r"\bcneas\b|\bloas\b|\bcnas\b|8\.?742"),
    ("crianca_adolescente", r"crian[çc]a|adolescente|\beca\b|\bcmdca\b|conanda|"
                            r"\bfia\b|\bfmdca\b|8\.?069"),
    ("pessoa_idosa", r"idosa|idoso|10\.?741|12\.?213"),
    ("cultura", r"cultur|rouanet|\bpnab\b|aldir|paulo\s*gustavo|goyazes|8\.?313|14\.?399|195/2022"),
    ("esporte", r"esporte|desporto|pel[ée]|\blie\b|11\.?438|14\.?260|222/2025|9\.?615"),
    ("saude", r"\bsa[úu]de\b|pronon|pronas|\bsus\b"),
    ("educacao", r"educa[çc]|ensino|fundeb"),
    ("meio_ambiente", r"ambient|res[íi]duos|reciclagem|clima|amaz[ôo]nia"),
    ("parcerias_e_fomento", r"parceri|mrosc|fomento|conv[êe]nio|emenda|fundo|"
                            r"13\.?019|13\.?800|8\.?726"),
    ("constituicao_e_direitos", r"constitui|direitos|volunt|qualifica|oscip|9\.?790|9\.?608"),
)
_TEMAS_RE = [(tema, re.compile(padrao, re.I)) for tema, padrao in TEMAS]


def tema_da_norma(item: dict) -> str:
    alvo = " ".join(str(item.get(c) or "")
                    for c in ("titulo", "tipo", "assunto", "id"))
    for tema, rx in _TEMAS_RE:
        if rx.search(alvo):
            return tema
    return "geral"


# ------------------------------------------------------------------ acervo 1
def montar_leis() -> dict:
    """Espelha o catálogo jurídico em pastas por tema e tipo."""
    catalogo = load_json(ROOT / "biblioteca/leis/catalogo.json")
    itens = catalogo.get("itens", [])
    indice: dict[str, list] = defaultdict(list)
    for item in itens:
        tema = tema_da_norma(item)
        tipo = slug(str(item.get("tipo") or "norma"))
        pasta = LEIS / tema / tipo
        pasta.mkdir(parents=True, exist_ok=True)
        ficha = dict(item)
        ficha["tema"] = tema
        ficha["arquivo_texto"] = None       # texto consolidado entra quando obtido
        ficha["conferir_em"] = item.get("fonte_oficial") or item.get("url")
        write_json(pasta / f'{slug(item["id"])}.json', ficha)
        indice[tema].append({"id": item["id"], "titulo": item.get("titulo"),
                             "tipo": item.get("tipo"), "esfera": item.get("esfera"),
                             "status": item.get("status"),
                             "caminho": str((pasta / f'{slug(item["id"])}.json')
                                            .relative_to(ROOT))})
    resumo = {"atualizado_em": now_iso(), "total": len(itens),
              "temas": {t: len(v) for t, v in sorted(indice.items())},
              "por_tema": dict(sorted(indice.items()))}
    write_json(LEIS / "indice.json", resumo)
    return resumo


# ------------------------------------------------------------------ acervo 2
def _texto_do_edital(pasta: Path) -> str:
    arq = pasta / "edital.txt"
    return arq.read_text(encoding="utf-8", errors="ignore") if arq.exists() else ""


_EXIGENCIA = re.compile(
    r"(cnpj|estatuto|ata\s+de\s+posse|certid[ãa]o[^.\n]{0,60}|balan[çc]o|"
    r"cebas|cneas|cmdca|inscri[çc][ãa]o\s+no\s+conselho|regularidade\s+fiscal|"
    r"fgts|inss|plano\s+de\s+trabalho|contrapartida|tempo\s+m[íi]nimo[^.\n]{0,40}|"
    r"experi[êe]ncia\s+m[íi]nima[^.\n]{0,40}|dois\s+anos|tr[êe]s\s+anos)", re.I)


def indexar_oportunidades() -> dict:
    """Consolida o histórico de editais e apura recorrências.

    A apuração aqui é DETERMINÍSTICA (contagem de exigências e de janelas por
    financiador). A leitura de padrões de aprovação — quais entidades vencem e
    por quê — é tarefa da IA, que recebe este índice pronto e enxuto, para não
    gastar tokens relendo os editais inteiros.
    """
    origem = ROOT / "dados/farol/editais"
    OPORTUNIDADES.mkdir(parents=True, exist_ok=True)
    registros, exig_global = [], Counter()
    por_financiador: dict[str, list] = defaultdict(list)

    if origem.exists():
        for dj in sorted(origem.glob("*/*/dados.json")):
            d = load_json(dj)
            pasta_destino = OPORTUNIDADES / d["chave"] / d["ano"]
            pasta_destino.mkdir(parents=True, exist_ok=True)
            texto = _texto_do_edital(dj.parent)
            if texto:
                (pasta_destino / "edital.txt").write_text(texto, encoding="utf-8")
            anexos = []
            for a in d.get("anexos_modelo", []):
                orig = dj.parent / "anexos" / a["arquivo"]
                if orig.exists():
                    destino = pasta_destino / "modelos" / a["arquivo"]
                    destino.parent.mkdir(parents=True, exist_ok=True)
                    destino.write_bytes(orig.read_bytes())
                    anexos.append(a["arquivo"])
            exigencias = sorted({m.group(0).lower().strip()
                                 for m in _EXIGENCIA.finditer(texto)})[:40]
            exig_global.update(exigencias)
            ficha = {**d, "exigencias_detectadas": exigencias,
                     "modelos": anexos, "texto_bytes": len(texto.encode()),
                     "indexado_em": now_iso()}
            write_json(pasta_destino / "ficha.json", ficha)
            registros.append({"chave": d["chave"], "ano": d["ano"],
                              "titulo": d.get("titulo"),
                              "financiador": d.get("fonte_nome"),
                              "territorio": d.get("territorio"),
                              "inicio": d.get("inicio"), "fim": d.get("fim"),
                              "exigencias": exigencias, "modelos": anexos})
            por_financiador[d.get("fonte_nome") or "—"].append(
                {"ano": d["ano"], "fim": d.get("fim"), "chave": d["chave"]})

    # recorrência: mesmo mês de encerramento em 2+ anos = janela provável
    recorrencias = []
    for fin, evs in por_financiador.items():
        meses = Counter(e["fim"][5:7] for e in evs if e.get("fim"))
        for mes, n in meses.items():
            if n >= 2:
                recorrencias.append({"financiador": fin, "mes": mes, "ocorrencias": n,
                                     "leitura": "janela recorrente — hipótese a confirmar"})
    indice = {"atualizado_em": now_iso(), "total": len(registros),
              "financiadores": len(por_financiador),
              "exigencias_mais_cobradas": [{"exigencia": e, "ocorrencias": n}
                                           for e, n in exig_global.most_common(25)],
              "recorrencias": sorted(recorrencias,
                                     key=lambda r: -r["ocorrencias"])[:30],
              "editais": registros,
              "nota": ("contagens determinísticas; padrões de aprovação e critérios "
                       "de vitória são apurados pela IA a partir deste índice")}
    write_json(OPORTUNIDADES / "indice.json", indice)
    return indice


# ------------------------------------------------------------------ acervo 3
def montar_associacoes() -> dict:
    """Uma subpasta por associação, com documentos e a pasta de cada edital
    concorrido (onde ficam os documentos PREENCHIDOS, para download)."""
    base = ROOT / "dados/associacoes"
    ASSOCIACOES.mkdir(parents=True, exist_ok=True)
    saida = []
    if base.exists():
        for assoc in sorted(p for p in base.glob("*") if p.is_dir()):
            if assoc.name.upper() == "EXEMPLO":
                continue
            destino = ASSOCIACOES / assoc.name
            (destino / "documentos").mkdir(parents=True, exist_ok=True)
            (destino / "editais").mkdir(parents=True, exist_ok=True)
            nome = assoc.name
            perfil = assoc / "perfil_publico.json"
            if perfil.exists():
                try:
                    dados = load_json(perfil)
                    nome = dados.get("nome") or nome
                    write_json(destino / "perfil_publico.json", dados)
                except Exception:
                    pass
            concorridos = []
            for pasta_ed in sorted((destino / "editais").glob("*/")):
                arquivos = sorted(p.name for p in pasta_ed.glob("*")
                                  if p.is_file() and p.suffix.lower() == ".pdf")
                concorridos.append({"edital": pasta_ed.name,
                                    "documentos_preenchidos": arquivos,
                                    "para_download": bool(arquivos)})
            saida.append({"slug": assoc.name, "nome": nome,
                          "editais_concorridos": concorridos,
                          "caminho": str(destino.relative_to(ROOT))})
    indice = {"atualizado_em": now_iso(), "total": len(saida), "associacoes": saida,
              "nota": ("documentos preenchidos ficam na pasta do edital concorrido "
                       "dentro da associação e são baixados pela Biblioteca do Farol")}
    write_json(ASSOCIACOES / "indice.json", indice)
    return indice


def pasta_edital_da_associacao(assoc_slug: str, titulo_edital: str) -> Path:
    """Pasta onde os documentos PREENCHIDOS daquele edital são guardados."""
    destino = ASSOCIACOES / assoc_slug / "editais" / slug(titulo_edital)[:70]
    destino.mkdir(parents=True, exist_ok=True)
    return destino


def run() -> dict:
    RAIZ.mkdir(parents=True, exist_ok=True)
    resumo = {"executado_em": now_iso(),
              "leis": montar_leis(),
              "oportunidades": indexar_oportunidades(),
              "associacoes": montar_associacoes()}
    write_json(RAIZ / "indice.json", {
        "biblioteca": "Biblioteca de Alexandria",
        "atualizado_em": resumo["executado_em"],
        "acervos": {"leis": resumo["leis"]["total"],
                    "oportunidades": resumo["oportunidades"]["total"],
                    "associacoes": resumo["associacoes"]["total"]},
        "estrutura": {"leis": "leis/<tema>/<tipo>/",
                      "oportunidades": "oportunidades/<chave>/<ano>/",
                      "associacoes": "associacoes/<slug>/editais/<edital>/"},
        "alimentacao": "Eldorado alimenta; Farol analisa com IA",
    })
    return resumo


if __name__ == "__main__":
    r = run()
    print(json.dumps({k: (v if not isinstance(v, dict) else
                          {kk: vv for kk, vv in v.items() if not isinstance(vv, list)})
                      for k, v in r.items()}, ensure_ascii=False, indent=2))
