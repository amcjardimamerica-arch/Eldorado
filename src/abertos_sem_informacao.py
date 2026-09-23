"""Editais em aberto que ainda estão sem informação — a fila de pesquisa.

O QUE ESTA ROTINA RESPONDE

"Quais editais estão em aberto e sem informação?" — a pergunta que decide o
trabalho de captação de cada semana. Em aberto quer dizer que ainda pode render
inscrição: prazo aberto, ou prazo que ninguém confirmou ainda. Sem informação
quer dizer que falta pelo menos uma das três exigências do titular:

    OBJETO · PRAZO DE INSCRIÇÃO · PÁGINA OFICIAL DO EDITAL

A página oficial é a do órgão ou do patrocinador. O endereço onde a oportunidade
foi encontrada não conta: PNCP, Querido Diário, Diário Oficial, portal de notícia
e plataforma privada de licitação servem para descobrir o número do processo e o
nome do órgão, nunca para confirmar prazo. Quem decide isso, endereço por
endereço, é a tabela de rotas (`config/rotas_de_coleta.json`).

POR QUE ESTE MÓDULO EXISTE

A inspeção de 10/09/2026 encontrou o trabalho de verificação e o sistema em dois
mundos separados: `docs/dados/verificacao_467_2026-09-09.json` — 468 registros,
339 prazos confirmados em documento oficial, 231 validados um por um — não era
lido por nenhum módulo, nenhum painel e nenhum workflow. Era arquivo órfão. Ao
mesmo tempo, o monitor de prazos lia apenas a base de oportunidades, que é quase
toda de edições de diário sem prazo, e por isso enxergava ZERO prazos em 17 mil
registros.

Esta rotina une as duas bases. Onde houver verificação, ela vence: prazo
confirmado em documento do órgão vale mais que campo vazio de API.

EDIÇÃO DE DIÁRIO NÃO É EDITAL

A base de oportunidades é hoje quase toda formada por edições inteiras de diário
oficial municipal — 17 mil registros cujo título é "Diário Oficial de X — data" e
onde apenas um termo de busca apareceu. Não são editais: são publicações onde
pode haver um edital dentro. Tratá-las como fila de pesquisa produz dezessete mil
linhas que ninguém consegue trabalhar, e foi o que encheu o painel de "abertas".

Elas ficam num bloco próprio, contadas, com o destino certo: extração do ato de
dentro da edição — descobrir o nome do órgão e o número do processo, e então
cadastrar a fonte oficial. A mesma regra que o módulo de enquadramento já usa.

O QUE FICA DE FORA, E POR QUÊ

Registro reprovado pelo objeto não entra na fila. Não é edital de fomento a
organização da sociedade civil — é contratação, compra, credenciamento de
prestador, resultado de edital já julgado ou parceria já celebrada. Buscar o
prazo de algo que não é oportunidade é trabalho que não produz decisão. O motivo
da reprovação fica registrado no resumo, para que a exclusão seja auditável.

Nada aqui inventa data. Campo sem confirmação sai nulo, com o que falta nomeado.
"""
from __future__ import annotations

import csv
import json
import re
from datetime import date

from .inconformidade import avaliar
from .nucleo import (ROOT, carregar_oportunidades, chave_curta, load_json, now_iso,
                     write_json)
from .rotas_coleta import exige_navegador, ritmo_de, rota_de, serve_como_fonte

SAIDA_JSON = ROOT / "docs/dados/abertos_sem_informacao.json"
SAIDA_CSV = ROOT / "docs/dados/abertos_sem_informacao.csv"
CARIMBO = ROOT / "estado/abertos_sem_informacao.json"

# Bases de verificação lidas além da base de oportunidades. A primeira que
# tiver o registro vence — estão em ordem de confiança.
BASES_VERIFICADAS = (
    # A mais recente vence. O fechamento de 23/09/2026 foi lido pelo NAVEGADOR
    # LOCAL do titular — unica rota que alcancou o PNCP naquele dia — e corrigiu
    # a chave de Osorio/RS, que na base apontava para um registro inexistente.
    ROOT / "docs/dados/verificacao_fechamento_2026-09-23.json",
    ROOT / "docs/dados/verificacao_63_2026-09-15.json",
    ROOT / "docs/dados/verificacao_467_2026-09-09.json",
    ROOT / "docs/dados/nao_verificados.json",
)

# Objeto com até este número de palavras não permite veredito: Curitiba/DER-PR
# trazia "CHAMAMENTO PUBLICO RESIDUOS SOLIDOS" — quatro palavras — e o edital de
# 75 páginas mostrou doação de bens móveis, oportunidade aberta.
OBJETO_CURTO_MAX_PALAVRAS = 5

# Prazo que fecha dentro desta janela entra como urgente.
DIAS_URGENTE = 30

# Edição inteira de diário, sem ato identificado dentro dela. Mesmo padrão que
# src/enquadramento.py já usa, para que os dois módulos contem a mesma coisa.
EDICAO_DE_DIARIO = re.compile(r"Di[áa]rio Oficial de .+\d{4}-\d{2}-\d{2}")

# Mecanismo permanente nao e edital sem prazo: e mecanismo que NAO TEM prazo por
# natureza — emenda parlamentar, destinacao de bens da Receita Federal, penas
# pecuniarias, Rouanet, cadastro de proponente em fluxo continuo. Entravam na
# fila como "falta prazo" e nunca saiam, porque a informacao que se cobrava
# deles nao existe. O que eles tem e PORTA DE ENTRADA, e o campo certo e
# `como_se_habilita`.
MECANISMO_PERMANENTE = re.compile(
    r"fluxo\s+cont[íi]nuo|mecanismo\s+permanente|a\s+qualquer\s+tempo|"
    r"emenda\s+parlamentar|penas?\s+pecuni[áa]ria|presta[çc][õo]es\s+pecuni[áa]rias|"
    r"(?:destina|doa)[çc][ãa]o\s+de\s+mercadorias|cadastro\s+de\s+proponente|"
    r"janela\s+or[çc]ament[áa]ria", re.I)


def e_mecanismo_permanente(registro: dict) -> bool:
    """Tem porta de entrada, nao prazo. Cobrar prazo dele e cobrar o que nao existe."""
    campos = " ".join(_texto(registro.get(c)) for c in ("objeto", "titulo", "observacao"))
    return bool(MECANISMO_PERMANENTE.search(campos))


def _e_edicao_de_diario(registro: dict) -> bool:
    titulo = _texto(registro.get("titulo"))
    tem_ato = bool(_texto(registro.get("objeto")) or _texto(registro.get("fim")))
    return bool(EDICAO_DE_DIARIO.match(titulo)) and not tem_ato

REGRA = ("em aberto = prazo aberto ou prazo ainda não confirmado. Sem informação = falta objeto, "
         "prazo de inscrição ou página oficial do órgão/patrocinador. O endereço onde a oportunidade "
         "foi encontrada não é página oficial: PNCP, diário e portal de notícia servem para descobrir "
         "o processo e o órgão, nunca para confirmar prazo. Nenhuma data é estimada.")


def _texto(valor) -> str:
    return str(valor or "").strip()


def _celula(valor, limite: int = 300) -> str:
    """Uma célula de CSV: sem quebra de linha e sem o separador."""
    texto = _texto(valor).replace("\r", " ").replace("\n", " ").replace(";", ",")
    return re.sub(r"\s+", " ", texto)[:limite]


def _chave_de_duplicata(texto) -> str:
    """Objeto normalizado: minúsculas, sem pontuação, 300 caracteres."""
    return re.sub(r"\W+", " ", _texto(texto).lower()).strip()[:300]


def _palavras(texto: str) -> int:
    return len(texto.split())


def _data(valor) -> date | None:
    bruto = _texto(valor)[:10]
    try:
        return date.fromisoformat(bruto)
    except ValueError:
        return None


def _situacao(fim: str | None, hoje: date) -> str:
    """Sem data final confirmada não há prazo para decidir captação.

    Janela de um dia e janela maior que três anos não são tratadas aqui: quem as
    marca é a verificação, e o motivo fica escrito na observação do registro.
    """
    vencimento = _data(fim)
    if vencimento is None:
        return "sem_prazo_confirmado"
    return "encerrado" if vencimento < hoje else "aberto"


def _verificadas() -> dict:
    """Índice das bases verificadas, pela chave curta de oito caracteres."""
    indice = {}
    for caminho in BASES_VERIFICADAS:
        if not caminho.exists():
            continue
        try:
            dados = load_json(caminho)
        except (OSError, json.JSONDecodeError):
            continue
        itens = dados.get("itens")
        if isinstance(itens, dict):
            registros = [(chave_curta(chave), valor) for chave, valor in itens.items()]
        elif isinstance(itens, list):
            registros = [(chave_curta(x.get("id")), x) for x in itens]
        else:
            continue
        for chave, valor in registros:
            if chave and chave not in indice:
                valor = dict(valor)
                valor["_origem_verificacao"] = caminho.name
                indice[chave] = valor
    return indice


# Portais que divulgam sem serem o órgão. A página de divulgação NUNCA é a
# página oficial do edital; o arquivo que o próprio órgão anexou lá, sim — foi a
# regra afinada pelo titular em 08/09/2026, com a origem declarada.
_DIVULGADORES = re.compile(
    r"(pncp\.gov\.br|queridodiario|in\.gov\.br|diariooficial|diario-oficial|"
    r"observatorio3setor|observatoriodoterceirosetor|captadores\.org|bussolasocial|prosas\.com|"
    r"portaldecompraspublicas|bllcompras|licitamaisbrasil|bnccompras|licitanet|licitardigital|"
    r"ammlicita|m2atecnologia|sigep\.com|sai\.io\.org\.br)", re.I)
_ARQUIVO_DO_ORGAO_NO_PNCP = re.compile(r"pncp\.gov\.br[^ ]*/arquivos/", re.I)


def e_pagina_oficial(url: str) -> tuple[bool, str]:
    """A página oficial do edital é a do órgão ou do patrocinador — e só ela.

    Regra mais estrita que `serve_como_fonte`, e a diferença é proposital:
    aquela responde "por esta rota dá para coletar?"; esta responde "este é o
    endereço onde o edital foi oficialmente publicado?". A página de divulgação
    do PNCP passa na primeira e reprova na segunda. A única exceção é o arquivo
    que o próprio órgão anexou ao registro do PNCP, que é documento do órgão.
    """
    url = _texto(url)
    if not url:
        return False, "nenhum endereço capturado"
    if _ARQUIVO_DO_ORGAO_NO_PNCP.search(url):
        return True, "arquivo do próprio órgão anexado ao PNCP (origem declarada)"
    if _DIVULGADORES.search(url):
        serve, motivo = serve_como_fonte(url)
        if not serve:
            return False, motivo
        return False, ("portal de divulgação, não é a página oficial do edital: serve para descobrir "
                       "o número do processo e o nome do órgão, e a partir daí a fonte é o site do órgão")
    serve, motivo = serve_como_fonte(url)
    return (True, "site do próprio órgão ou patrocinador") if serve else (False, motivo)


def _pagina_oficial(candidatos: list[str]) -> tuple[str | None, str]:
    """Primeiro endereço que é, de fato, página oficial do edital.

    Devolve o endereço e o motivo. Se nenhum serve, devolve None e o motivo da
    recusa do primeiro candidato — é o que o titular precisa ler para saber por
    onde procurar.
    """
    primeiro_motivo = "nenhum endereço capturado"
    for url in candidatos:
        url = _texto(url)
        if not url:
            continue
        oficial, motivo = e_pagina_oficial(url)
        if oficial:
            return url, motivo
        if primeiro_motivo == "nenhum endereço capturado":
            primeiro_motivo = motivo
    return None, primeiro_motivo


def _como_pesquisar(registro: dict) -> dict:
    """Por onde se busca o que falta neste registro."""
    url = _texto(registro.get("url")) or _texto(registro.get("pagina_oficial"))
    rota = rota_de(url) if url else None
    return {
        "endereco_capturado": url or None,
        "familia_de_rota": (rota or {}).get("familia"),
        "exige_navegador_do_titular": exige_navegador(url) if url else False,
        "ritmo": ritmo_de(url) if url else None,
        "erro_conhecido": (rota or {}).get("erro_conhecido"),
    }


def _unificar(hoje: date) -> list[dict]:
    verificadas = _verificadas()
    unificados: dict[str, dict] = {}

    def _somar(chave: str, dados: dict) -> None:
        if chave in unificados:
            unificados[chave].update({k: v for k, v in dados.items() if v not in (None, "", [])})
        else:
            unificados[chave] = dados

    # 1) base de oportunidades coletadas
    for item in carregar_oportunidades().values():
        chave = chave_curta(item.get("id"))
        if not chave:
            continue
        _somar(chave, {
            "id": item.get("id"), "id_curto": chave,
            "titulo": item.get("titulo"), "objeto": item.get("objeto"),
            "url": item.get("url"), "fonte_nome": item.get("fonte_nome"),
            "uf": item.get("uf"), "municipio": item.get("municipio"),
            "nivel": item.get("nivel"), "status": item.get("status"),
            "prazo_texto": item.get("prazo_texto"),
            "origem": "oportunidades",
        })

    # 2) bases verificadas — vencem onde houver conflito
    for chave, v in verificadas.items():
        registro = unificados.get(chave, {"id": chave, "id_curto": chave, "origem": "verificacao"})
        registro.update({
            "id_curto": chave,
            "objeto": _texto(v.get("objeto")) or registro.get("objeto"),
            "titulo": registro.get("titulo") or v.get("titulo") or v.get("edital"),
            "inicio": v.get("inicio"), "fim": v.get("fim"),
            "pagina_oficial": v.get("pagina_oficial") or v.get("link_capturado"),
            "orgao": v.get("orgao"), "edital": v.get("edital"),
            "uf": v.get("uf") or registro.get("uf"),
            "municipio": v.get("municipio") or registro.get("municipio"),
            "veredito": v.get("veredito"), "familia": v.get("familia"),
            "observacao": v.get("observacao"),
            "validacao": v.get("validacao"),
            "verificado_em": v.get("_origem_verificacao"),
            "origem": "verificacao" if registro.get("origem") != "oportunidades" else "ambas",
        })
        unificados[chave] = registro
    return list(unificados.values())


def _veredito(registro: dict) -> tuple[str, str | None]:
    """Veredito do registro: o da verificação quando existir, senão o do módulo de objeto."""
    if registro.get("veredito"):
        return registro["veredito"], registro.get("familia")
    texto = " ".join(_texto(registro.get(c)) for c in ("titulo", "objeto"))
    if not texto.strip():
        return "sem_objeto", None
    parecer = avaliar(texto[:4000])
    if not parecer.get("ok"):
        return "reprovado", parecer.get("familia")
    return ("atencao" if parecer.get("atencao") else "aprovado"), None


def _prioridade(situacao: str, dias: int | None, veredito: str) -> tuple[int, str]:
    if situacao == "aberto" and dias is not None and dias <= DIAS_URGENTE:
        return 1, "fecha em até 30 dias — pesquisar hoje"
    if situacao == "aberto":
        return 2, "prazo aberto — pesquisar nesta semana"
    if veredito == "aprovado":
        return 3, "objeto compatível e prazo não confirmado — pode estar aberto"
    if veredito == "atencao":
        return 4, "enquadramento a confirmar e prazo não confirmado"
    return 5, "sem objeto para decidir — precisa do documento"


def colapsar_permanentes(permanentes: list) -> list:
    """Uma porta de entrada aparece uma vez, com todos os endereços que tem.

    O BNDES foi capturado duas vezes em cada uma das suas duas portas, e o
    Instituto Impactarte duas vezes em dois domínios diferentes — `.com.br` e
    `.org.br`. São rotas de coleta distintas chegando ao mesmo lugar, e a
    deduplicação por objeto não as alcançava: ela roda sobre a fila, e mecanismo
    permanente sai da fila antes.

    O endereço divergente não é descartado. Quando a mesma porta chega por dois
    domínios, os dois ficam listados em `portas` e a porta é marcada para
    conferência — qual dos dois é o site do patrocinador é pergunta que só a
    leitura responde, e inventar a resposta aqui seria pior que registrar a
    dúvida.
    """
    reunidos: dict[tuple, dict] = {}
    for item in permanentes:
        chave = (_chave_de_duplicata(item.get("titulo") or item.get("objeto")),
                 _texto(item.get("orgao")).lower())
        porta = item.get("pagina_oficial")
        if chave in reunidos and chave[0]:
            alvo = reunidos[chave]
            alvo["capturado_como"].append(item.get("id"))
            if porta and porta not in alvo["portas"]:
                alvo["portas"].append(porta)
            continue
        item = dict(item)
        item["portas"] = [porta] if porta else []
        item["capturado_como"] = [item.get("id")]
        reunidos[chave] = item
    saida = []
    for item in reunidos.values():
        if len(item["portas"]) > 1:
            item["conferir_porta"] = ("a mesma porta chegou por endereços diferentes: "
                                      "confirmar qual é o do patrocinador antes de usar")
        saida.append(item)
    return saida


# Reprovação por prazo vencido não é reprovação por objeto. A verificação de
# 15/09/2026 fechou 27 registros porque a janela já tinha passado — natureza de
# fomento legítima, só fora do tempo — e o contador os somava junto com os que
# não são edital de fomento a OSC. Somados, davam ao titular a leitura errada de
# que o motor derruba por objeto quatro vezes mais do que derruba de fato.
REPROVACAO_TEMPORAL = re.compile(
    r"prazo\s+encerrad|j[áa]\s+julgad|homologa|adjudica|vencid|encerrado\s+em", re.I)


def motivo_da_reprovacao(familia) -> str:
    """Separa a reprovação temporal da reprovação por objeto."""
    return ("reprovado_por_prazo_vencido" if REPROVACAO_TEMPORAL.search(_texto(familia))
            else "reprovado_por_objeto")


def run(hoje: date | None = None) -> dict:
    hoje = hoje or date.today()
    fila, descartados = [], {"reprovado_por_objeto": 0, "reprovado_por_prazo_vencido": 0,
                             "encerrado": 0, "completo": 0,
                             "edicao_de_diario_sem_ato": 0, "mecanismo_permanente": 0}
    familias_descartadas: dict[str, int] = {}
    diarios_por_uf: dict[str, int] = {}
    permanentes: list = []

    for registro in _unificar(hoje):
        if _e_edicao_de_diario(registro):
            descartados["edicao_de_diario_sem_ato"] += 1
            uf = _texto(registro.get("uf")) or "sem UF"
            diarios_por_uf[uf] = diarios_por_uf.get(uf, 0) + 1
            continue
        veredito, familia = _veredito(registro)
        if veredito != "reprovado" and e_mecanismo_permanente(registro):
            descartados["mecanismo_permanente"] += 1
            permanentes.append({
                "id": registro.get("id") or registro.get("id_curto"),
                "titulo": registro.get("titulo"), "orgao": registro.get("orgao"),
                "uf": registro.get("uf"), "objeto": _texto(registro.get("objeto"))[:400] or None,
                "pagina_oficial": registro.get("pagina_oficial") or registro.get("url"),
                "observacao": _texto(registro.get("observacao"))[:600] or None,
            })
            continue
        if veredito == "reprovado":
            descartados[motivo_da_reprovacao(familia)] += 1
            familias_descartadas[familia or "sem familia"] = \
                familias_descartadas.get(familia or "sem familia", 0) + 1
            continue

        situacao = _situacao(registro.get("fim"), hoje)
        if situacao == "encerrado":
            descartados["encerrado"] += 1
            continue

        objeto = _texto(registro.get("objeto")) or _texto(registro.get("titulo"))
        pagina, motivo_pagina = _pagina_oficial([
            registro.get("pagina_oficial"), registro.get("url"),
        ])

        faltam = []
        if not objeto or _palavras(objeto) <= OBJETO_CURTO_MAX_PALAVRAS:
            faltam.append("objeto")
        if situacao != "aberto":
            faltam.append("prazo de inscrição")
        if not pagina:
            faltam.append("página oficial")
        if not faltam:
            descartados["completo"] += 1
            continue

        vencimento = _data(registro.get("fim"))
        dias = (vencimento - hoje).days if vencimento else None
        ordem, motivo = _prioridade(situacao, dias, veredito)
        fila.append({
            "id": registro.get("id") or registro.get("id_curto"),
            "id_curto": registro.get("id_curto"),
            "prioridade": ordem, "motivo_da_prioridade": motivo,
            "situacao": situacao, "fim": registro.get("fim"), "dias_restantes": dias,
            "veredito": veredito, "familia": familia,
            "titulo": registro.get("titulo"), "objeto": objeto or None,
            "orgao": registro.get("orgao"), "uf": registro.get("uf"),
            "municipio": registro.get("municipio"),
            "fonte_nome": registro.get("fonte_nome"),
            "pagina_oficial": pagina,
            "motivo_sem_pagina_oficial": None if pagina else motivo_pagina,
            "faltam": faltam,
            "como_pesquisar": _como_pesquisar(registro),
            "origem": registro.get("origem"),
            "validado_individualmente": bool(registro.get("validacao")),
            # o que a validação individual já apurou. Evita reabrir trabalho
            # feito: em Curitiba/DER-PR o objeto tem quatro palavras, mas o
            # documento já foi lido e diz doação de bens móveis inservíveis.
            "achado_da_validacao": ((registro.get("validacao") or {}).get("achado") or None),
            "proximo_passo_da_validacao": ((registro.get("validacao") or {}).get("proximo_passo") or None),
        })

    fila.sort(key=lambda x: (x["prioridade"], x["dias_restantes"] if x["dias_restantes"] is not None else 9999,
                             x["id_curto"] or ""))

    # Deduplicação: o mesmo edital aparece mais de uma vez quando foi capturado
    # por rotas diferentes. Conta-se oportunidade, não linha — o Instituto Lojas
    # Renner aparecia cinco vezes na base de 09/09.
    vistos: dict[tuple, dict] = {}
    duplicados = 0
    for item in fila:
        chave = (_chave_de_duplicata(item.get("objeto") or item.get("titulo")),
                 _texto(item.get("orgao")).lower())
        if chave in vistos and chave[0]:
            vistos[chave].setdefault("ocorrencias", []).append(item["id"])
            duplicados += 1
            continue
        vistos[chave] = item
    fila = list(vistos.values())

    permanentes = colapsar_permanentes(permanentes)

    resumo = {
        "total": len(fila),
        "por_prioridade": {},
        "por_situacao": {},
        "falta_objeto": sum(1 for x in fila if "objeto" in x["faltam"]),
        "falta_prazo": sum(1 for x in fila if "prazo de inscrição" in x["faltam"]),
        "falta_pagina_oficial": sum(1 for x in fila if "página oficial" in x["faltam"]),
        "urgentes": sum(1 for x in fila if x["prioridade"] == 1),
        "exigem_navegador_do_titular": sum(1 for x in fila
                                           if x["como_pesquisar"]["exige_navegador_do_titular"]),
        "ja_validados_individualmente": sum(1 for x in fila if x["validado_individualmente"]),
        "duplicados_colapsados": duplicados,
        "descartados": descartados,
        "familias_descartadas": dict(sorted(familias_descartadas.items(), key=lambda i: -i[1])),
        "mecanismos_permanentes": {
            "total": len(permanentes),
            "capturas": descartados["mecanismo_permanente"],
            "destino": ("nao tem prazo por natureza: o que eles tem e porta de entrada. Ficam em lista "
                        "propria, com o campo como_se_habilita no lugar do prazo, e nunca mais aparecem "
                        "como 'falta prazo'."),
            "itens": permanentes,
        },
        "edicoes_de_diario_sem_ato": {
            "total": descartados["edicao_de_diario_sem_ato"],
            "destino": ("extrair o ato de dentro da edição para descobrir o nome do órgão e o número "
                        "do processo, e então cadastrar a fonte oficial. Diário nunca é fonte de prazo."),
            "por_uf": dict(sorted(diarios_por_uf.items(), key=lambda i: -i[1])[:12]),
        },
    }
    for x in fila:
        resumo["por_prioridade"][str(x["prioridade"])] = resumo["por_prioridade"].get(str(x["prioridade"]), 0) + 1
        resumo["por_situacao"][x["situacao"]] = resumo["por_situacao"].get(x["situacao"], 0) + 1

    pacote = {"gerado_em": now_iso(), "referencia": hoje.isoformat(),
              "regra": REGRA, "resumo": resumo, "itens": fila}
    write_json(SAIDA_JSON, pacote)

    SAIDA_CSV.parent.mkdir(parents=True, exist_ok=True)
    with SAIDA_CSV.open("w", newline="", encoding="utf-8-sig") as fh:
        colunas = ["prioridade", "situacao", "fim", "dias_restantes", "veredito", "uf", "municipio",
                   "orgao", "titulo", "faltam", "pagina_oficial", "motivo_sem_pagina_oficial",
                   "familia_de_rota", "exige_navegador", "id"]
        escritor = csv.DictWriter(fh, fieldnames=colunas, delimiter=";")
        escritor.writeheader()
        for x in fila:
            escritor.writerow({
                "prioridade": x["prioridade"], "situacao": x["situacao"],
                "fim": x["fim"] or "",
                "dias_restantes": "" if x["dias_restantes"] is None else x["dias_restantes"],
                "veredito": x["veredito"], "uf": _celula(x["uf"], 4),
                "municipio": _celula(x["municipio"], 60),
                "orgao": _celula(x["orgao"], 120),
                "titulo": _celula(x["titulo"], 300),
                "faltam": ", ".join(x["faltam"]),
                "pagina_oficial": _celula(x["pagina_oficial"], 300),
                "motivo_sem_pagina_oficial": _celula(x["motivo_sem_pagina_oficial"], 200),
                "familia_de_rota": _celula(x["como_pesquisar"]["familia_de_rota"], 60),
                "exige_navegador": "sim" if x["como_pesquisar"]["exige_navegador_do_titular"] else "nao",
                "id": _celula(x["id"], 40),
            })

    write_json(CARIMBO, {"executado_em": now_iso(), "referencia": hoje.isoformat(),
                         "total": len(fila), "urgentes": resumo["urgentes"],
                         "saida": str(SAIDA_JSON.relative_to(ROOT))})
    return resumo


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
