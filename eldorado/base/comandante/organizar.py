# ruff: noqa: E501 — as tabelas de palavras da fórmula (as áreas, a natureza, os objetos) ficam numa linha cada, para a leitura
"""O Comandante organiza os livros do Cartório (a etapa C6; titular, 25/10/2026: "não existem 5 mil livros e nem devem ter
parâmetros diferentes em locais diferentes do site").

A FÓRMULA. Cada livro recebe um código que diz o que a oportunidade É:
    LOCAL · ÁREA · NATUREZA · MODALIDADE · OBJETO          ex.: GO-GOIANIA·CUL·PUB·FOM·EVE
  LOCAL     pela regra de território validada pela titular (a mesma do portão e da auditoria):
            GO-<MUNICÍPIO> (município de Goiás), GO (o estado de Goiás), <UF>-CAP (a capital de outro estado),
            <UF> (outro estado), BR (nacional), INT (internacional); município de outro estado fora das capitais: eliminado.
  ÁREA      SAU saúde · ASS assistência social · CUL cultura · ESP esporte · EDU educação · AMB meio ambiente ·
            DHU direitos humanos e cidadania · CRI criança e adolescente · IDO pessoa idosa · PCD pessoa com deficiência ·
            CTI ciência, tecnologia e inovação · ECO trabalho, renda e economia · GER várias áreas ou geral
  NATUREZA  PUB pública · PRI privada
  MODALIDADE  a FORMA do recurso: FOM fomento a projetos · PAR parceria (termo de colaboração ou fomento, convênio) · PRE prêmio ·
            BOL bolsa · DOA doação ou patrocínio · INC incentivo fiscal · JUD destinação judicial ou do Ministério Público ·
            EMD emenda parlamentar · CRE credenciamento ou cadastro
  OBJETO    o que o recurso PERMITE FAZER (o benefício direto; titular, 25/10/2026): PRJ executar um projeto · INS fortalecimento
            institucional e custeio da organização · GES gerir e executar um serviço ou programa público · EQP adquirir ou
            receber bens e equipamentos · OBR obra, reforma ou infraestrutura · EVE realizar um evento · CAP formação e
            capacitação de pessoas · PES pesquisa, estudo ou inovação · ESP usar um espaço público · SER prestar serviços ao
            órgão · ATE apoio técnico, mentoria ou aceleração · LIV prêmio de uso livre · ? sem informação
A fonte de cada característica: o item certificado no documento oficial (o território, a área, a esfera, a modalidade, o
objeto); na falta dele, as palavras do título e do órgão. A validação diz, para cada parte, de onde ela veio.

O DESEMPATE (só entre livros com o mesmo código e o mesmo nome): o site oficial (sites diferentes, oportunidades
diferentes); o ano e o número (no mesmo ano, números diferentes são chamadas diferentes; anos diferentes são edições da
mesma oportunidade, e a mais recente fica com as anteriores); por fim, o prazo.
"""
from __future__ import annotations

import re
import sqlite3
import unicodedata
from collections import Counter, defaultdict
from typing import Any
from urllib.parse import urlsplit

RANK_SELO = {"sem": 0, "bronze": 1, "prata": 2, "ouro": 3}
AREAS = {
    "IDO": r"\bidos[oa]s?\b|pessoa idosa|terceira idade|envelhec|fundo (municipal |estadual |nacional )?do idoso",
    "CRI": r"crianc|adolescen|infan(cia|til)|\bfia\b|fundo (municipal |estadual )?(dos )?direitos da crianc|primeira infancia|juventude|jovens?\b",
    "PCD": r"deficien|\bpcd\b|acessibilidade|autis|\btea\b|surd|cegu",
    "SAU": r"\bsaude\b|hospital|oncolog|cancer|\bsus\b|pronon|pronas|medic|doenca|dependencia quimica|saude mental|vacin",
    "ASS": r"assistencia social|socioassistencial|\bsuas\b|vulnerab|fome|seguranca alimentar|populacao de rua|acolhimento|\bcmas\b|\bfmas\b",
    "CUL": r"cultur|\barte|artist|audiovisual|cinema|musica|teatro|danca|circo|patrimonio|literatur|livro e leitura|festival|aldir blanc|\bpnab\b|rouanet|museu",
    "ESP": r"esporte|esportiv|paradesport|atleta|futebol|olimpi|lei de incentivo ao esporte",
    "EDU": r"educac|escola|ensino|alfabetiz|pedagog|estudant",
    "AMB": r"ambient|clima|sustentab|florest|\bagua\b|bioma|amazon|cerrado|residuo|recicla|biodivers|conservac|animal",
    "DHU": r"direitos humanos|mulher|genero|igualdade racial|racism|negr[oa]s?\b|lgbt|indigena|quilombol|povos (e comunidades )?tradiciona|cidadania|democraci|violencia",
    "CTI": r"ciencia|tecnolog|inovac|pesquisa|startup|centelha|\bfap[a-z]*\b|\bcnpq\b|\bfinep\b",
    "ECO": r"trabalho e renda|empreend|economia (solidaria|criativa)|geracao de renda|agricultura familiar|cooperativ|microcredito|desenvolvimento (economico|local|regional)",
}
NATUREZA_PUB = r"prefeitura|secretaria|ministerio|governo|fundo (municipal|estadual|nacional|federal)|tribunal|ministerio publico|\bmp[a-z]{0,2}\b|\bmpt\b|camara|assembleia|senado|congresso|universidade federal|instituto federal|\bifg?o?\b|\bbndes\b|\bcaixa\b|banco do brasil|petrobras|correios|eletrobras|\bfunarte\b|\bancine\b|\bcnpq\b|\bfinep\b|\bfap[a-z]*\b|conselho (municipal|estadual|nacional)|\bunesco\b|\bonu\b|nacoes unidas|uniao europeia|embaixada|\bbid\b|banco mundial|\.gov\b|\.gov\.br|\.leg\.br|\.jus\.br|\.mp\.br"
MODALIDADES = [   # a forma do recurso; a parceria (termo de fomento ou colaboração) antes do prêmio, da bolsa e do credenciamento
    ("JUD", r"prestac(ao|oes) pecuniar|\btac\b|termo de ajustamento|penas? (pecuniar|alternativ)|destinac(ao|oes) (de )?(recursos|valores) (judicia|do mp|do ministerio)|reversao|reversoes|transac(ao|oes) penal|\bmpt\b"),
    ("EMD", r"emenda(s)? parlamentar|emendas? (individua|de bancada)"),
    ("INC", r"incentivo fiscal|lei de incentivo|deducao|imposto de renda|renuncia fiscal|destinac(ao|oes) (do |de )?(ir|imposto)|\bfia\b|fundo do idoso|\bpronon\b|\bpronas\b"),
    ("PAR", r"termo de (colaborac|fomento|execucao cultural)|acordo de cooperac|convenio|\bmrosc\b|parceria"),
    ("PRE", r"premio|premiac|concurso|reconhecimento"),
    ("BOL", r"\bbolsas?\b|residencia (artistica|cientifica|tecnologica)|intercambio"),
    ("CRE", r"credenciamento|cadastr|habilitac|chamamento para (o )?cadastro|banco de projetos|chamada para inscricao de entidades"),
    ("DOA", r"doac(ao|oes)|patrocin|apoio empresarial|investimento social|responsabilidade social"),
    ("FOM", r"edital|chamada|chamamento|selec(ao|iona)|apoio (a|financeiro)|fomento|financiamento|projetos?"),
]
AREA_CERT = {"saude": "SAU", "assistencia": "ASS", "cultura": "CUL", "esporte": "ESP", "educacao": "EDU", "meio ambiente": "AMB", "idoso": "IDO",
             "crianca": "CRI", "deficiencia": "PCD", "direitos humanos": "DHU", "ciencia": "CTI", "tecnologia": "CTI", "inclusao": "DHU"}
NUMERO = re.compile(r"\b(?:n[ºo°.]?|numero|edital)\s*(\d{1,4})(?:\s*/\s*(20\d\d))?", re.I)
ANO = re.compile(r"\b(20[12]\d|2030)\b")
VAZIAS = re.compile(r"\b(edital|chamada|chamamento|publica|publico|selecao|processo|seletivo|n[ºo°]|numero|de|da|do|das|dos|e|para|a|o|em|"
                    r"\d+|20\d\d|brasil|nacional|inscricoes?|abertas?|aberto|edicao|\d+a|\d+o|segunda|terceira|primeira)\b")


def sem_acento(t: str | None) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", (t or "").lower()) if unicodedata.category(c) != "Mn")


def slug(t: str | None, n: int = 12) -> str:
    return re.sub(r"[^A-Z0-9]", "", sem_acento(t).upper())[:n] or "?"


def local(abrangencia: str, municipio: str | None, uf: str | None) -> str | None:
    """O LOCAL pelo território; None para o município de outro estado fora das capitais (eliminado)."""
    uf = (uf or "").upper()
    return {"municipal_go": f"GO-{slug(municipio)}", "estadual_go": "GO", "capital_outro_estado": f"{uf if len(uf) == 2 else '??'}-CAP",
            "estadual_outro_estado": uf if len(uf) == 2 and uf not in ("BR", "IN") else "UF?", "nacional": "BR", "internacional": "INT",
            "municipal_fora_go": None}.get(abrangencia, "?")


def area(texto: str, cert_area: str | None) -> str:
    c = sem_acento(cert_area)
    if c:
        achadas = {v for k, v in AREA_CERT.items() if k in c}
        if len(achadas) == 1:
            return achadas.pop()
    t = sem_acento(texto)
    pontos = Counter({a: len(re.findall(rx, t)) for a, rx in AREAS.items()})
    pontos = Counter({a: n for a, n in pontos.items() if n})
    if not pontos:
        return "GER"
    (a1, n1), *resto = pontos.most_common()
    return "GER" if len(pontos) >= 4 and resto and resto[0][1] == n1 else a1


def natureza(texto: str, esfera: str | None) -> str:
    e = sem_acento(esfera)
    if "privad" in e:
        return "PRI"
    if any(x in e for x in ("federal", "estadual", "municipal", "public")):
        return "PUB"
    return "PUB" if re.search(NATUREZA_PUB, sem_acento(texto)) else "PRI"


def modalidade(texto: str, certificada: str | None) -> str:
    t = sem_acento(f"{certificada or ''} {texto}")
    return next((o for o, rx in MODALIDADES if re.search(rx, t)), "FOM")


OBJETOS = [   # o que o recurso permite fazer (a ordem: do mais específico ao mais geral)
    ("ESP", r"uso (do|de) espaco|cessao de (uso de )?(espaco|sala|imovel|teatro|auditorio)|pauta (do|de) (teatro|espaco)|ocupac(ao|oes) (do|de|artistica)"),
    ("SER", r"prestac(ao|oes) de servicos|contratac(ao|oes) de (servicos|artistas|pareceristas)|credenciamento de (pareceristas|artistas|oficineiros|pessoas)|parecerista"),
    ("GES", r"gerenciamento|gestao (compartilhada|do|da|de servic)|operacionaliza|execuc(ao|oes) (do|de) (programa|servico)|servicos? socioassistenciais|acolhimento institucional|cogestao"),
    ("EQP", r"aquisic(ao|oes) de (bens|equipamentos|veiculos|materiais)|equipamentos?|veiculos?|motocultivador|mobiliario|bens (e valores|moveis|duraveis)|recebimento de bens|kits?\b|cessao de uso de (bens|maquinas|motocultivad)"),
    ("OBR", r"\bobras?\b|reforma|construc(ao|oes)|ampliac(ao|oes)|infraestrutura|moradia|habitac|saneamento|cisterna"),
    ("INS", r"fortalecimento institucional|desenvolvimento institucional|custeio|manutenc(ao|oes) (da|das) (entidade|organizac|instituic)|despesas (correntes|administrativas)|apoio institucional|sustentabilidade (financeira|institucional)"),
    ("EVE", r"\bevento|festival|\bfeira\b|mostra\b|apresentac(ao|oes)|espetacul|circulac(ao|oes)|temporada|programac(ao|oes) (cultural|artistica)|exposic"),
    ("PES", r"pesquisa|estudos?\b|inovac|desenvolvimento (tecnologico|de solucoes|de produtos)|startup|prova de conceito|laboratorio"),
    ("CAP", r"formac(ao|oes)|capacitac|curso|oficina|qualificac|treinamento|acoes formativas|ensino|aprendiz"),
    ("ATE", r"mentoria|acelerac|incubac|assessoria|apoio tecnico|consultoria|orientac(ao|oes) (dos|aos|tecnica)"),
    ("LIV", r"premio em dinheiro|premiac(ao|oes)|reconhecimento|premiar"),
    ("PRJ", r"\bprojetos?\b|\bac(ao|oes)\b|\batividades\b|\biniciativas\b|\bpropostas\b"),
]


def objeto(texto: str, certificado: str | None) -> tuple[str, str]:
    """(o objeto, a base): o item Objeto certificado no documento oficial vence; na falta, o título e o tema. O certificado
    que não descreve benefício nenhum (um trecho errado do documento) não conta, e a base o diz."""
    if certificado and not next((o for o, rx in OBJETOS if re.search(rx, sem_acento(certificado))), None):
        o = next((o for o, rx in OBJETOS if re.search(rx, sem_acento(texto))), None)
        return (o, "título (o objeto certificado não descreve benefício)") if o else ("?", "o objeto certificado não descreve benefício")
    for base, t in (("certificado", certificado), ("título", texto)):
        t = sem_acento(t)
        if not t.strip():
            continue
        o = next((o for o, rx in OBJETOS if re.search(rx, t)), None)
        if o:
            return o, base
    return "?", "sem informação"


NAO_OPORTUNIDADE = [   # a validação: o livro pode não ser uma oportunidade (vai a revisar, não é excluído pelo título)
    ("sem título real", r"^(op|l|achado)-[0-9a-f]{6,}$|^\s*$"),
    ("parte de um edital (anexo, declaração, formulário)", r"^\s*anexo\b|\banexo [ivx\d]+\b|declarac(ao|oes) (de|pessoa|etnico)|formulario|modelo de|\((docx|pdf|xlsx)\)"),
    ("andamento de um edital (resultado, retificação, prorrogação, errata, convocação)", r"^\s*(divulgad[oa] )?resultado|retificac|prorrogac|errata|homologac|^\s*convocac"),
    ("notícia ou evento sem oportunidade", r"mega-?sena|loteria|acumula|apresenta seu trabalho|\bshow\b|palestra|webinar|seminario|inaugura"),
]


def validar(titulo: str | None) -> str:
    t = sem_acento(titulo)
    return next((nome for nome, rx in NAO_OPORTUNIDADE if re.search(rx, t)), "oportunidade")


def nome_chave(titulo: str | None) -> str:
    """O nome sem o número, o ano e as palavras de forma (o que fica é o nome da oportunidade)."""
    t = sem_acento(titulo)
    t = re.sub(r"\b([a-z]+)(\d+)\b", lambda m: f" {m.group(1)}x{'i' * min(int(m.group(2)) if m.group(2).isdigit() and len(m.group(2)) < 4 else 0, 20)}x ", t)
    t = re.sub(r"[^a-z ]", " ", t)
    t = re.sub(r"\s+", " ", VAZIAS.sub(" ", t)).strip()
    return t[:80]


LUGARES = r"\b(goias|goiania|brasil|brasileir[oa]s?|nacional|estadual|municipal|federal|municipio|prefeitura|estado|governo|aviso|convocacao|resultado|inscricoes|abre|abertas?|publicad[oa]|diario|oficial|edital|chamamento|chamada|publico|publica|selecao|programa|projetos?)\b"


def proprio(nome: str) -> bool:
    """O nome tem palavras próprias (tirando as de forma e os lugares, sobram ao menos duas palavras de 4 letras)."""
    return len([w for w in re.sub(LUGARES, " ", nome).split() if len(w) >= 4]) >= 2


def _republicadores() -> set[str]:
    import json
    from pathlib import Path
    try:
        d = json.loads(Path("config/missao/republicadores.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    return {h for k in ("noticia", "agregador", "rede_social", "buscador", "plataforma_inscricao") for h in d.get(k, []) if isinstance(h, str)}


def sites_compativeis(a: str, b: str, rep: set[str]) -> bool:
    """O desempate pelo site: o mesmo site, um lado sem site, ou um lado republicador; dois oficiais diferentes não se unem."""
    if not a or not b or a == b:
        return True
    return any(a == r or a.endswith("." + r) or b == r or b.endswith("." + r) for r in rep)


def host(*links: str | None) -> str:
    for u in links:
        h = (urlsplit(u or "").hostname or "").removeprefix("www.")
        if h:
            return h
    return ""


def classificar(con: sqlite3.Connection) -> list[dict[str, Any]]:
    """Todos os livros vivos, com o código, o nome, o ano, o número, o site e o prazo."""
    from ..cartorio.auditoria import territorio
    con.row_factory = sqlite3.Row
    certs: dict[str, dict[str, dict]] = defaultdict(dict)
    for c in con.execute("SELECT livro_id, item, valor FROM certidao WHERE situacao = 'comprovado'"):
        certs[c["livro_id"]][c["item"]] = {"valor": c["valor"]}
    saida = []
    for lv in con.execute("SELECT l.*, d.inscricao_fim, d.area AS d_area, d.esfera AS d_esfera, d.modalidade AS d_modalidade, p.fase FROM livro l "
                          "LEFT JOIN livro_dados d ON d.livro_id = l.id LEFT JOIN passaporte p ON p.livro_id = l.id "
                          "WHERE l.situacao NOT IN ('excluido', 'unido')"):
        lv = dict(lv)
        cs = certs.get(lv["id"], {})
        abr, municipio = territorio(lv, cs)
        texto = " ".join(str(x or "") for x in (lv["titulo"], lv["orgao"], lv["tema"], (cs.get("Objeto") or {}).get("valor"), lv["link_oficial"]))
        loc = local(abr, municipio, lv["uf"])
        ar = area(texto, (cs.get("Área de atuação") or {}).get("valor") or lv["d_area"])
        nat = natureza(f"{lv['orgao'] or ''} {lv['link_oficial'] or ''} {lv['titulo'] or ''}", (cs.get("Esfera") or {}).get("valor") or lv["d_esfera"])
        mod_cert = (cs.get("Modalidade") or {}).get("valor")
        mod = modalidade(texto, mod_cert or lv["d_modalidade"])
        obj, base_obj = objeto(f"{lv['titulo'] or ''} {lv['tema'] or ''}", (cs.get("Objeto") or {}).get("valor"))
        tit = lv["titulo"] or ""
        num = NUMERO.search(sem_acento(tit))
        anos = [int(a) for a in ANO.findall(f"{tit} {lv['inscricao_fim'] or ''}")]
        saida.append({"id": lv["id"], "titulo": tit, "abrangencia": abr, "municipio": municipio, "local": loc, "area": ar, "natureza": nat,
                      "modalidade": mod, "objeto": obj, "codigo": f"{loc}·{ar}·{nat}·{mod}·{obj}" if loc else None, "validacao": validar(tit),
                      "base": {"local": "território certificado" if cs.get("Território") else "título, órgão e site",
                               "area": "certificada" if cs.get("Área de atuação") or lv["d_area"] else "título",
                               "natureza": "certificada" if cs.get("Esfera") or lv["d_esfera"] else "órgão e site",
                               "modalidade": "certificada" if mod_cert or lv["d_modalidade"] else "título", "objeto": base_obj}, "nome": nome_chave(tit), "ano": max(anos) if anos else None,
                      "numero": num.group(1).lstrip("0") if num else None, "site": host(lv["link_oficial"], lv["link_divulgacao"]),
                      "prazo": lv["inscricao_fim"], "fase": lv["fase"], "situacao": lv["situacao"], "selo": lv["selo_livro"], "estrela": lv["estrela"],
                      "itens": len(cs)})
    return saida


def _principal(grupo: list[dict[str, Any]]) -> dict[str, Any]:
    """O livro que fica: o do Farol primeiro; depois a edição mais recente, o mais certificado e o mais antigo no sistema."""
    return max(grupo, key=lambda x: (x["fase"] == "farol", x["ano"] or 0, int(x["numero"]) if (x["numero"] or "").isdigit() else 0,
                                     _ordinal(x["titulo"]), x["prazo"] or "", x["itens"], -len(x["id"])))


def _ordinal(titulo: str | None) -> int:
    """A edição pelo ordinal do título (o 12º edital é mais novo que o 11º)."""
    m = re.search(r"\b(\d{1,3})\s*[ºª°o]\s*(?:edital|edic|chamada)", sem_acento(titulo).replace("ª", "a"))
    return int(m.group(1)) if m else 0


def organizar(livros: list[dict[str, Any]]) -> dict[str, Any]:
    """As decisões: os eliminados (município de outro estado), as uniões e os códigos.
    A identidade do edital é o nome próprio com o ano e o número; o local do código separa os de lugares diferentes; o site
    desempata (com os republicadores). No mesmo ano, números diferentes são chamadas diferentes; anos diferentes de uma
    oportunidade sem número são edições, e a mais recente fica com as anteriores."""
    rep = _republicadores()
    eliminar = [x for x in livros if x["local"] is None]
    vivos = [x for x in livros if x["local"] is not None]
    genericos = {"BR", "?", "UF?"}
    grupos: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for x in vivos:
        if not proprio(x["nome"]):
            continue                                                # o nome genérico não identifica: só o local e o site o separam
        loc = x["local"] if x["local"] not in genericos else "*"
        grupos[(x["nome"], x["numero"] or "", x["ano"] if x["numero"] else "")].append({**x, "_loc": loc})
    unir: list[tuple[str, str, str]] = []
    for (nome, numero, _ano), g in grupos.items():
        if len(g) < 2:
            continue
        especificos = {x["_loc"] for x in g} - {"*"}
        if len(especificos) > 1:
            continue                                                # lugares diferentes: oportunidades diferentes
        # o desempate pelo site: cada conjunto de sites compatíveis é uma oportunidade
        conjuntos: list[list[dict[str, Any]]] = []
        for x in sorted(g, key=lambda y: (y["site"] == "", y["site"])):
            for c in conjuntos:
                if all(sites_compativeis(x["site"], y["site"], rep) for y in c):
                    c.append(x)
                    break
            else:
                conjuntos.append([x])
        for c in conjuntos:
            if len(c) < 2:
                continue
            fica = _principal(c)
            for x in c:
                if x["id"] == fica["id"] or (x["fase"] == "farol" and fica["fase"] == "farol"):
                    continue
                if numero:
                    motivo = f"o mesmo edital (nº {numero}{'/' + str(x['ano']) if x['ano'] else ''})"
                elif x["ano"] and fica["ano"] and x["ano"] < fica["ano"]:
                    motivo = f"edição anterior ({x['ano']}) da mesma oportunidade"
                else:
                    motivo = "a mesma oportunidade"
                unir.append((fica["id"], x["id"], f"{motivo} · «{nome[:60]}» · {x['site'] or 'sem site'} → {fica['site'] or 'sem site'}"))
    unidos = {u for _f, u, _m in unir}
    return {"eliminar": eliminar, "unir": unir, "restantes": [x for x in vivos if x["id"] not in unidos]}


def codigo_do_grupo(fica: dict[str, Any], outros: list[dict[str, Any]]) -> str:
    """O código do livro que fica, com a informação de todas as cópias (a área, a modalidade e o objeto mais específicos)."""
    todos = [fica, *outros]
    area_ = next((x["area"] for x in todos if x["area"] != "GER"), "GER")
    mod = next((x["modalidade"] for x in todos if x["modalidade"] != "FOM"), "FOM")
    obj = next((x["objeto"] for x in todos if x["objeto"] not in ("?", "PRJ")), next((x["objeto"] for x in todos if x["objeto"] != "?"), "?"))
    loc = next((x["local"] for x in todos if x["local"] not in ("BR", "?", "UF?")), fica["local"])
    return f"{loc}·{area_}·{fica['natureza']}·{mod}·{obj}"


def no_organizar_livros(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem (o Comandante, C6): o código de cada livro, as uniões e as eliminações, a cada passagem."""
    from datetime import datetime, timezone
    from pathlib import Path

    from ..cartorio.identidade import unir
    p = Path(parametros.get("dados", "dados")) / "biblioteca.db"
    if not p.exists():
        return []
    con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    try:
        livros = classificar(con)
        dec = organizar(livros)
        por_id = {x["id"]: x for x in livros}
        outros: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for fica, unido, motivo in dec["unir"]:
            unir(con, contexto.diario, fica, unido, f"o Comandante organizou o Cartório: {motivo}")
            outros[fica].append(por_id[unido])
        agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
        for x in dec["eliminar"]:
            contexto.diario.emitir("livro.excluido_logicamente", "comandante", {
                "id": x["id"], "atualizado_em": agora,
                "justificativa_exclusao": f"município de outro estado, fora das capitais ({x['municipio'] or '?'}): a Biblioteca não guarda (regra da titular)"})
        con.row_factory = None
        atuais = dict(con.execute("SELECT livro_id, codigo FROM livro_dados"))
        gravados = 0
        for x in dec["restantes"]:
            cod = codigo_do_grupo(x, outros.get(x["id"], []))
            if atuais.get(x["id"]) != cod:
                contexto.diario.emitir("livro.codigo", "comandante", {"livro_id": x["id"], "codigo": cod})
                gravados += 1
    finally:
        con.close()
    return [{"livros": len(livros), "unidos": len(dec["unir"]), "eliminados": len(dec["eliminar"]), "codigos_gravados": gravados,
             "depois": len(dec["restantes"])}]

def parecer(livros: list[dict[str, Any]], dec: dict[str, Any]) -> dict[str, Any]:
    r = dec["restantes"]
    def nivel(x: dict) -> str:
        return {"municipal_go": "cidade de Goiás", "estadual_go": "estado de Goiás", "capital_outro_estado": "capital de outro estado",
                "estadual_outro_estado": "outro estado", "nacional": "nacional", "internacional": "internacional"}.get(x["abrangencia"], "indeterminado")
    return {"antes": len(livros), "eliminados": len(dec["eliminar"]), "unidos": len(dec["unir"]), "depois": len(r),
            "por_nivel": Counter(nivel(x) for x in r).most_common(), "por_area": Counter(x["area"] for x in r).most_common(),
            "por_natureza": Counter(x["natureza"] for x in r).most_common(), "por_modalidade": Counter(x["modalidade"] for x in r).most_common(),
            "por_objeto": Counter(x["objeto"] for x in r).most_common(), "por_validacao": Counter(x["validacao"] for x in r).most_common(),
            "codigos_distintos": len({x["codigo"] for x in r}),
            "edicoes_unidas": sum(1 for _f, _u, m in dec["unir"] if m.startswith("edição anterior"))}
