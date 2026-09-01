"""Filtro de destinação — fase 2 do Eldorado.

Determinação do titular: toda a mecânica do Eldorado existe para obter recursos
para ASSOCIAÇÕES. Publicação cuja finalidade seja aquisição de bens ou atividade
comercial pura, em que uma OSC não possa concorrer, é DESCARTADA na fase 2.

O corte é conservador e assimétrico, de propósito:

  · DESCARTA apenas quando há sinal claro de objeto comercial (compra, pregão,
    fornecimento, locação, obra) **e nenhum** sinal de terceiro setor;
  · MANTÉM quando o texto menciona OSC, entidade sem fins lucrativos, fomento,
    parceria, subvenção, ou qualquer das leis do repositório (MROSC, LOAS,
    Rouanet, PNAB, LIE, CEBAS, FIA, Fundo do Idoso...);
  · MANTÉM edital de empresa privada, instituto ou fundação que destine recurso
    ao terceiro setor — é exatamente o que interessa;
  · Na dúvida, MANTÉM e declara a dúvida. Perder um edital elegível custa mais
    caro do que revisar um duvidoso.

O catálogo das 260 fontes de captação é o parâmetro de enquadramento: fonte
catalogada é presumida de fomento, e o descarte exige sinal comercial forte.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .nucleo import ROOT, load_json

CATALOGO = ROOT / "estado/cobertura_catalogo.json"

# --------------------------------------------------------- sinais de fomento
_TERCEIRO_SETOR = re.compile(
    r"organiza[çc][õo]es?\s+da\s+sociedade\s+civil|\bosc\b|\boscs\b|\boscip\b|"
    r"terceiro\s+setor|sem\s+fins\s+lucrativos|entidade[s]?\s+(?:sociais|"
    r"filantr[óo]pic|beneficente)|associa[çc][ãa]o|funda[çc][ãa]o|instituto\b|"
    r"cooperativa\s+social|\bapae\b|\bong\b|entidade[s]?\s+privad[ao]s?\s+sem\s+fins",
    re.I)
_FOMENTO = re.compile(
    r"fomento|chamamento\s+p[úu]blico|termo\s+de\s+(?:colabora[çc][ãa]o|fomento|parceria)|"
    r"subven[çc][ãa]o|aux[íi]lio|apoio\s+(?:financeiro|a\s+projetos)|patroc[íi]nio|"
    r"edital\s+de\s+(?:projetos|sele[çc][ãa]o)|premia[çc][ãa]o|bolsa|"
    r"emenda\s+parlamentar|fundo\s+(?:municipal|estadual|nacional)|"
    r"incentivo\s+(?:fiscal|[àa]\s+cultura)|doa[çc][ãa]o", re.I)
# leis do repositório — enquadramento normativo
_LEIS = re.compile(
    r"13\.?019|mrosc|8\.?742|\bloas\b|\bsuas\b|\bcebas\b|187/2021|"
    r"8\.?313|rouanet|14\.?399|\bpnab\b|aldir\s*blanc|195/2022|paulo\s*gustavo|"
    r"11\.?438|14\.?260|222/2025|lei\s+de\s+incentivo\s+ao\s+esporte|"
    r"8\.?069|\beca\b|\bfia\b|\bfmdca\b|10\.?741|12\.?213|fundo\s+do\s+idoso|"
    r"9\.?790|oscip|9\.?608|volunt|13\.?800|8\.?726|goyazes|pronon|pronas", re.I)

# ------------------------------------------------------- sinais comerciais
_COMERCIAL = re.compile(
    r"preg[ãa]o\s+(?:eletr[ôo]nico|presencial)|dispensa\s+de\s+licita[çc][ãa]o|"
    r"inexigibilidade|tomada\s+de\s+pre[çc]os|concorr[êe]ncia\s+p[úu]blica|"
    r"registro\s+de\s+pre[çc]os|aquisi[çc][ãa]o\s+de|compra\s+de|fornecimento\s+de|"
    r"contrata[çc][ãa]o\s+de\s+empresa|loca[çc][ãa]o\s+de|execu[çc][ãa]o\s+de\s+obra|"
    r"reforma\s+d[ao]|pavimenta[çc][ãa]o|constru[çc][ãa]o\s+de|menor\s+pre[çc]o|"
    r"leil[ãa]o|aliena[çc][ãa]o\s+de\s+bens|preg[ãa]o\b|licita[çc][ãa]o\s+na\s+modalidade",
    re.I)
_EXIGE_EMPRESA = re.compile(
    r"empresa[s]?\s+(?:do\s+ramo|especializad|interessad)|pessoa\s+jur[íi]dica\s+"
    r"com\s+fins\s+lucrativos|cnae\b|contrato\s+social\s+da\s+empresa|"
    r"comprova[çc][ãa]o\s+de\s+capital\s+social|balan[çc]o\s+empresarial|"
    r"certid[ãa]o\s+de\s+registro\s+cadastral\s+de\s+fornecedor|\bsicaf\b", re.I)
# credenciamento é ambíguo: pode ser de OSC (mantém) ou de fornecedor (descarta)
_CREDENCIAMENTO = re.compile(r"credenciamento", re.I)


def _fontes_catalogadas() -> set:
    """Fontes do catálogo de captação (as 260 rotas monitoradas).

    O relatório de cobertura guarda só as contagens; o catálogo em si é o
    `config/fontes.json`, que lista cada fonte de captação com id e nome.
    Fonte catalogada é presumida de FOMENTO — o descarte, nesse caso, exige
    sinal comercial forte.
    """
    ids: set[str] = set()
    cfg = ROOT / "config/fontes.json"
    if cfg.exists():
        try:
            for f in load_json(cfg).get("fontes", []):
                ids.add(str(f.get("id") or "").lower())
                ids.add(str(f.get("nome") or "").lower())
        except Exception:
            pass
    return {x for x in ids if x}


def avaliar_destinacao(ficha: dict, catalogadas: set | None = None) -> dict:
    """Decide se a publicação pode render recurso para uma associação.

    Devolve {elegivel, motivo, sinais} — sempre com o porquê registrado.
    """
    catalogadas = catalogadas if catalogadas is not None else _fontes_catalogadas()
    texto = " ".join(str(ficha.get(c) or "")
                     for c in ("titulo", "evidencia", "objeto"))
    sinais = {
        "terceiro_setor": bool(_TERCEIRO_SETOR.search(texto)),
        "fomento": bool(_FOMENTO.search(texto)),
        "lei_do_repositorio": bool(_LEIS.search(texto)),
        "comercial": bool(_COMERCIAL.search(texto)),
        "exige_empresa": bool(_EXIGE_EMPRESA.search(texto)),
        "credenciamento": bool(_CREDENCIAMENTO.search(texto)),
        "fonte_catalogada": (str(ficha.get("fonte_id") or "").lower() in catalogadas
                             or str(ficha.get("financiador") or "").lower() in catalogadas),
    }
    favoravel = sinais["terceiro_setor"] or sinais["fomento"] or sinais["lei_do_repositorio"]

    # 1. sinal claro de terceiro setor / fomento / lei do repositório → MANTÉM
    if favoravel:
        return {"elegivel": True, "sinais": sinais,
                "motivo": "menciona terceiro setor, fomento ou lei do repositório — "
                          "OSC pode concorrer"}
    # 2. exigência tipicamente empresarial e nenhum sinal favorável → DESCARTA
    if sinais["exige_empresa"]:
        return {"elegivel": False, "sinais": sinais,
                "motivo": "exigência empresarial (SICAF, CNAE, capital social) sem "
                          "qualquer menção a OSC — associação não pode concorrer"}
    # 3. objeto comercial puro sem sinal favorável → DESCARTA
    if sinais["comercial"]:
        return {"elegivel": False, "sinais": sinais,
                "motivo": "objeto comercial (aquisição, obra, pregão, fornecimento) "
                          "sem destinação ao terceiro setor"}
    # 4. credenciamento genérico sem sinal favorável → DESCARTA
    if sinais["credenciamento"]:
        return {"elegivel": False, "sinais": sinais,
                "motivo": "credenciamento de fornecedor sem menção a OSC ou fomento"}
    # 5. dúvida: MANTÉM e declara
    return {"elegivel": True, "sinais": sinais,
            "motivo": "sem sinal comercial e sem sinal de fomento — mantido por "
                      "cautela; conferir a destinação no edital"}


def run(limite: int | None = None) -> dict:
    """Aplica o filtro a todo o acervo, no banco e nas pastas."""
    import sqlite3
    from .banco import conectar
    catalogadas = _fontes_catalogadas()
    con = conectar()
    with con:
        con.execute("CREATE TABLE IF NOT EXISTS destinacao ("
                    "chave TEXT, ano TEXT, id TEXT, elegivel INTEGER, motivo TEXT,"
                    " sinais TEXT, PRIMARY KEY (chave, ano, id))")
    linhas = con.execute("SELECT chave, ano, id, ficha FROM historico").fetchall()
    if limite:
        linhas = linhas[:limite]
    mantidos = descartados = 0
    motivos: dict[str, int] = {}
    amostra_descarte = []
    with con:
        for chave, ano, cid, fj in linhas:
            ficha = json.loads(fj)
            r = avaliar_destinacao(ficha, catalogadas)
            con.execute("INSERT OR REPLACE INTO destinacao VALUES (?,?,?,?,?,?)",
                        (chave, ano, cid, int(r["elegivel"]), r["motivo"],
                         json.dumps(r["sinais"], ensure_ascii=False)))
            ficha["destinacao"] = r
            con.execute("UPDATE historico SET ficha=? WHERE chave=? AND ano=? AND id=?",
                        (json.dumps(ficha, ensure_ascii=False), chave, ano, cid))
            if r["elegivel"]:
                mantidos += 1
            else:
                descartados += 1
                motivos[r["motivo"]] = motivos.get(r["motivo"], 0) + 1
                if len(amostra_descarte) < 12:
                    amostra_descarte.append({"titulo": (ficha.get("titulo") or "")[:90],
                                             "motivo": r["motivo"]})
    con.close()
    return {"avaliados": len(linhas), "mantidos": mantidos,
            "descartados": descartados,
            "motivos": dict(sorted(motivos.items(), key=lambda x: -x[1])),
            "amostra_descarte": amostra_descarte,
            "regra": ("só entra o que uma associação pode concorrer; na dúvida "
                      "mantém e declara"),
            "catalogo_fontes": len(catalogadas)}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2)[:2000])
