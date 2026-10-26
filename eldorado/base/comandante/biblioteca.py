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
from urllib.parse import urlsplit

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


# o pré-voo da base (26/10/2026): o que se completa SEM a IA, antes do plano de voo do Interceptador
ESFERA = [  # a esfera pelo órgão, só quando ele não deixa dúvida (a ordem importa)
    (
        "internacional",
        r"\bonu\b|nacoes unidas|unesco|unicef|\bpnud\b|embaixada|consulado|uniao europeia|\bbid\b|banco mundial|organizacao dos estados",
    ),
    (
        "federal",
        r"ministerio(?! publico (do estado|de goias|estadual))|governo federal|universidade federal|instituto federal|\bcnpq\b|\bfinep\b|\bbndes\b|"
        r"caixa economica|\bfunarte\b|\bancine\b|\bmpf\b|\bmpt\b|justica federal|\btrf ?\d|\btrt ?\d|\bfnde\b|\bcapes\b|\bibama\b|\bicmbio\b|petrobras",
    ),
    (
        "estadual",
        r"secretaria de estado|governo do estado|governo de goias|assembleia legislativa|tribunal de justica|ministerio publico do estado|"
        r"ministerio publico de goias|\bmpgo\b|\bfapeg\b|fundacao de amparo a pesquisa",
    ),
    ("municipal", r"prefeitura|camara municipal|secretaria municipal|fundo municipal|conselho municipal"),
    (
        "privada",
        r"\binstituto\b|\bfundacao\b|\bassociacao\b|\bltda\b|\bs\.a\.|\bempresa\b|\bitau\b|bradesco|santander|natura\b|\bvale\b|ambev|coca-cola",
    ),
]


def esfera_pelo_orgao(orgao: str | None) -> str | None:
    from .organizar import sem_acento

    t = sem_acento(orgao)
    if not t.strip():
        return None
    return next((e for e, rx in ESFERA if re.search(rx, t)), None)


def esfera_pelo_site(link: str | None) -> str | None:
    """A esfera pelo domínio do SITE OFICIAL (o de divulgação pode ser um jornal): os domínios do governo dizem a esfera."""
    h = (urlsplit(link or "").hostname or "").lower().removeprefix("www.")
    if not h:
        return None
    if h in ("gov.br", "leg.br"):  # o portal federal (gov.br/<órgão>) e o Congresso
        return "federal"
    partes = h.split(".")
    ufs = {
        "ac",
        "al",
        "ap",
        "am",
        "ba",
        "ce",
        "df",
        "es",
        "go",
        "ma",
        "mt",
        "ms",
        "mg",
        "pa",
        "pb",
        "pr",
        "pe",
        "pi",
        "rj",
        "rn",
        "rs",
        "ro",
        "rr",
        "sc",
        "sp",
        "se",
        "to",
    }
    if h.endswith((".gov.br", ".leg.br", ".jus.br", ".mp.br")):
        suf, resto = partes[-2], partes[:-2]
        if suf == "jus":
            return "estadual" if resto and re.fullmatch(r"tj[a-z]{2}|tre-?[a-z]{2}", resto[-1]) else "federal"
        if suf == "mp":
            return "federal" if resto and resto[-1] in ("mpf", "mpt", "mpm", "mpdft") else "estadual"
        if resto and resto[-1] in ufs:  # <x>.<uf>.gov.br: o estado ou, se <x> é um município, o município
            if len(resto) >= 2 and resto[-2].replace("-", "") in _municipios_sem_espaco():
                return "municipal"
            return "estadual"
        return "federal" if suf in ("gov", "leg") else None
    if re.search(r"\b(unesco|unicef|undp|worldbank|iadb|europa)\b", h.replace(".", " ")):
        return "internacional"
    if h.endswith((".org.br", ".com.br", ".com", ".org", ".net")):
        return "privada"
    return None


_MUNIS: set[str] = set()


def _municipios_sem_espaco() -> set[str]:
    if not _MUNIS:
        try:
            m = json.loads(Path("config/missao/municipios_brasil.json").read_text(encoding="utf-8"))["municipios"]
            _MUNIS.update(k.replace(" ", "").replace("-", "") for k in m)
        except (OSError, ValueError, KeyError):
            pass
    return _MUNIS


def prevoo(diario, interceptador, livro, base: dict[str, Any]) -> list[str]:
    """O que se completa sem a IA: o site oficial (o documento oficial na página que divulgou) e a esfera (pelo órgão).
    Devolve o que foi completado."""
    from ...motores.descoberta import fonte_oficial
    from ..nucleo.eventos import agora as _agora

    feito = []
    if "site oficial" in base["buscar"] and livro.link_divulgacao:
        lido = interceptador._ler(livro.link_divulgacao)
        if lido is not None:
            # o documento no mesmo site também vale (quando quem divulga é o próprio órgão); só a própria página não
            cands = [c for c in fonte_oficial.candidatos(lido[2], lido[0], livro.titulo or "", limite=3) if c["url"] != livro.link_divulgacao]
            if cands:
                c = cands[0]
                diario.emitir(
                    "livro.links",
                    "comandante",
                    {"id": livro.id, "link_divulgacao": livro.link_divulgacao, "link_oficial": c["url"], "atualizado_em": _agora()},
                )
                diario.emitir(
                    "livro.origem",
                    "comandante",
                    {
                        "livro_id": livro.id,
                        "origem": "candidato",
                        "origem_motivo": f"o documento oficial achado na página que divulgou ({c['pontos']} pontos; sem IA)",
                    },
                )
                feito.append("site oficial")
    if "esfera" in base["buscar"]:
        e = esfera_pelo_orgao(livro.orgao) or esfera_pelo_site(livro.link_oficial)
        if e:
            diario.emitir("livro.esfera", "comandante", {"livro_id": livro.id, "esfera": e})
            feito.append("esfera")
    return feito


CARENCIA_DIAS = 3  # o livro recém-criado tem 3 dias para a certificação antes da regra do expurgo


def expurgar(con: sqlite3.Connection, diario, agora: datetime | None = None) -> dict[str, int]:
    """A regra da titular (26/10/2026), a cada passagem:
    - EXCLUIR o livro público sem selo (nenhuma edição conhecida) e sem estrela, com o prazo não aberto;
    - EXCLUIR o município de outro estado fora das capitais (o público);
    - UNIR os livros com o mesmo código e o mesmo nome (fica o de melhor selo, estrela e prazo);
    - as oportunidades de EMPRESAS (privadas) ficam todas; a tabela das empresas nunca é tocada; nunca um livro do Farol.
    A exclusão é lógica (nada se apaga), com a justificativa."""
    from ..cartorio.identidade import unir
    from .organizar import RANK_SELO, classificar, proprio

    agora = agora or datetime.now(timezone.utc)
    limite = (agora - timedelta(days=CARENCIA_DIAS)).isoformat()
    livros = classificar(con)
    con.row_factory = None
    info = {
        i: (s, e, p, c)
        for i, s, e, p, c in con.execute(
            "SELECT l.id, l.selo_livro, l.estrela, d.situacao_prazo, l.criado_em FROM livro l JOIN livro_dados d ON d.livro_id = l.id"
        )
    }
    conta = {"unidos": 0, "excluidos_sem_dados": 0, "excluidos_municipio": 0}
    grupos: dict[tuple, list[dict[str, Any]]] = {}
    for x in livros:
        if x["codigo"] and proprio(x["nome"]):
            grupos.setdefault((x["codigo"], x["nome"], x["numero"] or "", x["ano"] if x["numero"] else ""), []).append(x)
    unidos = set()
    for g in grupos.values():
        if len(g) < 2:
            continue

        def peso(y):
            s_, e_, p_, _c = info.get(y["id"], ("sem", "sem", None, ""))
            return (y["fase"] == "farol", p_ == "aberta", RANK_SELO.get(e_, 0), RANK_SELO.get(s_, 0), y["itens"])

        fica = max(g, key=peso)
        for y in g:
            if y["id"] != fica["id"] and y["fase"] != "farol":
                unir(con, diario, fica["id"], y["id"], f"o mesmo código ({y['codigo']}) e o mesmo nome (regra da titular, 26/10/2026)")
                unidos.add(y["id"])
                conta["unidos"] += 1
    iso = agora.isoformat(timespec="seconds")
    for x in livros:
        if x["id"] in unidos or x["fase"] == "farol" or x["natureza"] == "PRI":
            continue  # as oportunidades de empresas ficam todas
        s_, e_, p_, criado = info.get(x["id"], ("sem", "sem", None, iso))
        if (criado or iso) > limite:
            continue  # a carência do livro recém-criado
        if x["local"] is None:
            motivo, chave = f"município de outro estado, fora das capitais ({x['municipio'] or '?'})", "excluidos_municipio"
        elif s_ == "sem" and e_ == "sem" and p_ != "aberta":
            motivo, chave = "sem dados para o selo (nenhuma edição conhecida), sem estrela e sem prazo aberto", "excluidos_sem_dados"
        else:
            continue
        diario.emitir(
            "livro.excluido_logicamente",
            "comandante",
            {"id": x["id"], "atualizado_em": iso, "justificativa_exclusao": f"{motivo} (regra da titular, 26/10/2026)"},
        )
        conta[chave] += 1
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
        r = atualizar(con, contexto.diario)
        return [{**r, **expurgar(con, contexto.diario)}]
    finally:
        con.close()
