"""O Cartório no site, ligado aos dados (titular, 25/10/2026: a página estava estática).

O arquivo principal (dados/cartorio.json): os dois mostradores da primeira linha (os livros em cada uma das 5 etapas do
Cartório e os degraus da escada em que cada livro foi obtido), os cartões, a linha de produção, as abordagens do
Interceptador, a eficiência por item, os balcões, as safras e a lista dos livros. A ficha de cada livro
(dados/cartorio/<id>.json): os 12 itens com o trecho, os dois mostradores do livro, o relatório de cada etapa, o parecer
do Cérebro, o repasse para a próxima etapa e a orientação do que fazer para obter a oportunidade.
"""

from __future__ import annotations

import json
import re
import sqlite3
from collections import Counter, defaultdict
from datetime import date, datetime
from typing import Any

ETAPAS = [
    ("recepcao", "Recepção"),
    ("certificacao", "Certificação"),
    ("preparacao", "Preparação"),
    ("validacao", "Validação"),
    ("analise externa", "Análise externa"),
]
SAIDAS = [("farol", "Farol"), ("arquivo", "Arquivo")]
DEGRAUS = [
    ("1", "API oficial"),
    ("2", "pedido leve"),
    ("3", "navegador leve"),
    ("4", "navegador (Patchright)"),
    ("5", "navegador (Camoufox)"),
    ("6", "cópia arquivada"),
    ("7", "computador local"),
]
DOZE = [
    "Objeto",
    "Prazo de inscrição",
    "Resultado",
    "Prazo de recurso",
    "Valor",
    "Órgão / financiador",
    "Território",
    "Esfera",
    "Requisitos",
    "Anexos",
    "Modalidade",
    "Área de atuação",
]
ESTAGIO = {"sem": "sem_estrela", None: "sem_estrela", "bronze": "bronze", "prata": "prata", "ouro": "ouro"}
REPASSE = {
    "recepcao": "Certificação: o Cartório lê o achado e certifica os 12 itens no documento",
    "certificacao": "Preparação (se faltam itens) ou Validação (se o essencial está certificado)",
    "preparacao": "Validação, depois que o Interceptador trouxer o que falta (pelo plano de voo)",
    "validacao": "Farol (ouro e prazo aberto), Preparação (se ainda faltam itens) ou Análise externa (esgotado)",
    "analise externa": "Farol ou Arquivo, depois do veredito do Claude no Chrome",
    "farol": "a decisão no Farol de Alexandria (preparar a proposta)",
    "arquivo": "nenhum: encerrada (o livro fica no arquivo)",
}


def _degrau(escada: str | None) -> str | None:
    m = re.search(r"degrau (\d)", escada or "")
    return m.group(1) if m else None


def _dias(fim: str | None, hoje: str) -> int | None:
    try:
        return (date.fromisoformat(fim[:10]) - date.fromisoformat(hoje)).days if fim else None
    except ValueError:
        return None


def montar(bib: sqlite3.Connection, cer: sqlite3.Connection | None, rede=None, agora: str | None = None) -> tuple[dict[str, Any], dict[str, dict]]:
    agora = agora or datetime.now().astimezone().isoformat(timespec="seconds")
    hoje = agora[:10]
    formato_anterior = bib.row_factory                       # a conexão é compartilhada com o gerador: o formato volta ao fim
    bib.row_factory = sqlite3.Row
    livros = bib.execute(
        "SELECT l.id, l.titulo, l.orgao, l.uf, l.estrela, l.link_oficial, l.link_divulgacao, l.criado_em, p.fase, d.inscricao_fim, "
        "d.situacao_prazo, d.escada, d.origem, d.validacao, "
        + ("d.codigo" if "codigo" in {r[1] for r in bib.execute("PRAGMA table_info(livro_dados)")} else "NULL AS codigo")
        + " FROM livro l JOIN passaporte p ON p.livro_id = l.id LEFT JOIN livro_dados d ON d.livro_id = l.id "
        "WHERE l.situacao NOT IN ('excluido', 'unido')"
    ).fetchall()
    certs: dict[str, list[dict]] = defaultdict(list)
    for c in bib.execute("SELECT livro_id, item, valor, situacao, fase, justificativa, trecho, pagina, documento_id, id, em FROM certidao"):
        certs[c["livro_id"]].append(dict(c))
    passagens: dict[str, list[dict]] = defaultdict(list)
    for p in bib.execute("SELECT livro_id, de, para, em, autorizado_por, motivo FROM passagem ORDER BY id"):
        passagens[p["livro_id"]].append(dict(p))
    tentativas: dict[str, list[dict]] = defaultdict(list)
    for t in bib.execute("SELECT livro_id, ferramenta, em, resultado FROM tentativa ORDER BY em"):
        tentativas[t["livro_id"]].append(dict(t))
    motor_do_livro = dict(bib.execute("SELECT livro_id, MIN(motor) FROM achado WHERE livro_id IS NOT NULL GROUP BY livro_id").fetchall())
    docs = {r["id"]: dict(r) for r in bib.execute("SELECT id, url, tipo, paginas, oficial FROM documento")}
    bib.row_factory = formato_anterior
    from ..missao import itens as I

    categoria = _categorias()
    etapas = Counter(lv["fase"] for lv in livros)
    escada = Counter(_degrau(lv["escada"]) or "sem registro" for lv in livros)
    por_item = {k: {"faltavam": 0, "obtidos": 0, "dispensados": 0} for k in DOZE}
    abord: dict[str, dict] = {}
    for _lid, ts in tentativas.items():
        for t in ts:
            if not str(t["ferramenta"]).startswith("abordagem"):
                continue
            n = t["ferramenta"].split()[-1]
            try:
                r = json.loads(t["resultado"] or "{}")
            except ValueError:
                r = {}
            a = abord.setdefault(n, {"nome": r.get("abordagem") or f"abordagem {n}", "vezes": 0, "renderam": 0, "itens": 0, "links_oficiais": 0})
            a["vezes"] += 1
            a["renderam"] += int(not r.get("sem material"))
    for a in abord.values():
        a["taxa_de_acerto"] = round(a["renderam"] / a["vezes"], 3) if a["vezes"] else None
    lista, fichas = [], {}
    balcoes: dict[str, dict] = defaultdict(lambda: {"certidoes": 0, "com_link": 0, "resolvidos": 0, "faltavam": 0})
    safras: dict[str, dict] = defaultdict(lambda: {"certidoes": 0, "com_link": 0, "resolvidos": 0, "faltavam": 0})
    for lv in livros:
        m = I.melhor(certs.get(lv["id"], []))
        validas = {k: v for k, v in m.items() if I.resolvido(v)}
        itens = {k: v.get("valor") for k, v in validas.items() if v.get("situacao") == "comprovado"}
        disp = {k: v.get("justificativa") or "dispensado" for k, v in validas.items() if v.get("situacao") == "dispensado"}
        faltam = [k for k in DOZE if k not in validas]
        for k in DOZE:
            if k in itens:
                por_item[k]["obtidos"] += 1
            elif k in disp:
                por_item[k]["dispensados"] += 1
            por_item[k]["faltavam"] += 1
        bal = categoria.get(motor_do_livro.get(lv["id"]) or "", "outros")
        for agg in (balcoes[bal], safras[(lv["criado_em"] or "")[:7] or "?"]):
            agg["certidoes"] += 1
            agg["com_link"] += int(bool(lv["link_oficial"]))
            agg["resolvidos"] += len(validas)
            agg["faltavam"] += 12
        deg = _degrau(lv["escada"])
        lista.append(
            {
                "id": lv["id"],
                "titulo": lv["titulo"],
                "orgao": lv["orgao"],
                "uf": lv["uf"],
                "codigo": lv["codigo"],
                "etapa": lv["fase"],
                "estrela": lv["estrela"],
                "estagio": ESTAGIO.get(lv["estrela"], "sem_estrela"),
                "tipo": "estrela" if lv["estrela"] not in (None, "sem") else "livro",
                "balcao": bal,
                "prazo": lv["inscricao_fim"],
                "aberta": lv["situacao_prazo"] == "aberta",
                "link_oficial": lv["link_oficial"],
                "degrau": deg,
                "itens": {k: 1 for k in itens},
                "dispensas": {k: 1 for k in disp},
                "faltavam": faltam,
                "encaminhado": {"preparacao": "interceptador", "analise externa": "chrome"}.get(lv["fase"], ""),
            }
        )
        fichas[lv["id"]] = _ficha(
            lv, validas, itens, disp, faltam, passagens.get(lv["id"], []), tentativas.get(lv["id"], []), certs.get(lv["id"], []), docs, rede, hoje
        )
    for agg in (*balcoes.values(), *safras.values()):
        agg["taxa_link_oficial"] = round(agg["com_link"] / agg["certidoes"], 3) if agg["certidoes"] else None
        agg["eficiencia"] = round(agg["resolvidos"] / agg["faltavam"], 3) if agg["faltavam"] else None
    estrelas = Counter(lv["estrela"] or "sem" for lv in livros)
    comprovados_24h = sum(1 for cs in certs.values() for c in cs if c["situacao"] == "comprovado" and (c["em"] or "") >= hoje)
    principal = {
        "em": agora,
        "regra": "o Cartório ligado à Biblioteca e ao Cérebro (titular, 25/10/2026)",
        "mostradores": {
            "etapas": [{"id": k, "nome": n, "livros": etapas.get(k, 0)} for k, n in ETAPAS],
            "saidas": [{"id": k, "nome": n, "livros": etapas.get(k, 0)} for k, n in SAIDAS],
            "escada": [{"degrau": k, "nome": n, "livros": escada.get(k, 0)} for k, n in DEGRAUS]
            + [{"degrau": "sem registro", "nome": "sem registro do degrau (achados anteriores a 24/10)", "livros": escada.get("sem registro", 0)}],
        },
        "resumo": {
            "certidoes": len(lista),
            "nesta_execucao": comprovados_24h,
            "com_link_oficial": sum(1 for x in lista if x["link_oficial"]),
            "taxa_link_oficial": round(sum(1 for x in lista if x["link_oficial"]) / len(lista), 3) if lista else None,
            "para_o_interceptador": etapas.get("preparacao", 0),
            "para_o_chrome": etapas.get("analise externa", 0),
        },
        "linha_de_producao": {
            "na_linha_por_tipo": {"estrela": {k: estrelas.get(k, 0) for k in ("bronze", "prata")} | {"sem_estrela": estrelas.get("sem", 0)}},
            "fila_oportunidades": sum(1 for x in lista if x["aberta"]),
            "fila_livros": len(lista),
            "balcoes": {
                "sem_estrela": {"foco": ["Prazo de inscrição", "Objeto", "Órgão / financiador"]},
                "bronze": {"foco": ["Valor", "Requisitos"]},
                "prata": {"foco": ["Resultado", "Prazo de recurso", "Anexos"]},
            },
        },
        "por_balcao_selo": {"ouro": {"certidoes": estrelas.get("ouro", 0)}},
        "por_abordagem": dict(sorted(abord.items(), key=lambda kv: int(kv[0]) if kv[0].isdigit() else 99)),
        "por_item": por_item,
        "por_balcao": dict(balcoes),
        "por_safra": dict(sorted(safras.items(), reverse=True)[:8]),
        "por_versao": {},
        "cinza_conferidos": {
            "certificados": sum(1 for cs in certs.values() for c in cs if c["situacao"] == "pendente"),
            "conferidos": 0,
            "certidoes": 0,
        },
        "gabarito": {
            "orgaos_com_gabarito": len({lv["orgao"] for lv in livros if lv["orgao"] and lv["origem"] == "confirmado"}),
            "itens_achados_pelo_gabarito": {},
        },
        "certidoes": sorted(lista, key=lambda x: (not x["aberta"], x["prazo"] or "9999")),
    }
    return principal, fichas


def _categorias() -> dict[str, str]:
    import tomllib
    from pathlib import Path

    saida = {}
    for p in Path("eldorado/motores/canal/config").glob("*.toml"):
        try:
            saida[p.stem] = tomllib.loads(p.read_text(encoding="utf-8")).get("motor", {}).get("categoria", "outros")
        except tomllib.TOMLDecodeError:
            pass
    saida.update({"interceptador": "Pilotos", "espiao": "Pilotos"})
    return saida


def _ficha(lv, validas, itens, disp, faltam, passagens, tentativas, certs, docs, rede, hoje) -> dict[str, Any]:
    dias = _dias(lv["inscricao_fim"], hoje)
    fase = lv["fase"]
    # o relatório de cada etapa: as passagens do livro, agrupadas pela etapa de onde ele saiu
    relatorio = [{"de": p["de"], "para": p["para"], "em": p["em"], "por": p["autorizado_por"], "motivo": p["motivo"]} for p in passagens]
    # o parecer do Cérebro
    nota = None
    if rede is not None:
        try:
            nota = round(rede.nota_oportunidade({"titulo": lv["titulo"], "orgao": lv["orgao"], "link_oficial": lv["link_oficial"]}), 3)
        except Exception:  # noqa: BLE001
            nota = None
    leitura = []
    if lv["situacao_prazo"] == "aberta":
        leitura.append(f"oportunidade aberta{f', faltam {dias} dias para o fim da inscrição' if dias is not None else ''}")
    elif lv["situacao_prazo"] == "encerrada":
        leitura.append("prazo encerrado: o livro fica como histórico do programa (a próxima edição é vigiada)")
    if faltam:
        leitura.append(f"faltam {len(faltam)} dos 12 itens: {', '.join(faltam[:6])}{'…' if len(faltam) > 6 else ''}")
    leitura.append("o site oficial está confirmado" if lv["origem"] == "confirmado" else "o site oficial ainda não está confirmado")
    parecer = {
        "nota_oportunidade": nota,
        "leitura": leitura,
        "decisao": {
            "recepcao": "certificar",
            "certificacao": "classificar e certificar",
            "preparacao": "investigar o que falta (o Interceptador)",
            "validacao": "validar as certidões",
            "analise externa": "aguardar o veredito do Claude no Chrome",
            "farol": "transferido ao Farol",
            "arquivo": "arquivado",
        }.get(fase, fase),
    }
    # a orientação do que fazer para obter a oportunidade
    orient = []
    if lv["situacao_prazo"] == "aberta":
        if dias is not None:
            orient.append(f"Inscrever-se até {lv['inscricao_fim'][8:10]}/{lv['inscricao_fim'][5:7]}/{lv['inscricao_fim'][:4]} ({dias} dias).")
        if lv["link_oficial"]:
            orient.append(f"Ler o edital no site oficial: {lv['link_oficial']}")
        if itens.get("Requisitos"):
            orient.append(f"Conferir os requisitos: {str(itens['Requisitos'])[:220]}")
        if itens.get("Valor"):
            orient.append(f"Valor previsto: {str(itens['Valor'])[:120]}")
        if itens.get("Anexos"):
            orient.append(f"Preparar os anexos: {str(itens['Anexos'])[:180]}")
        if faltam:
            orient.append(f"Antes de decidir, confirmar no edital: {', '.join(faltam[:5])}.")
        if lv["estrela"] == "ouro":
            orient.append("Livro completo (ouro): pronto para a decisão no Farol e a preparação da proposta.")
    else:
        orient.append("Sem inscrição aberta agora: acompanhar a próxima edição (a previsão do sistema avisa 30 dias antes).")
    tent = []
    for t in tentativas:
        try:
            r = json.loads(t["resultado"] or "{}")
        except ValueError:
            r = {}
        tent.append(
            {
                "ferramenta": t["ferramenta"],
                "em": t["em"],
                "nome": r.get("ferramenta") or r.get("abordagem"),
                "para": r.get("para"),
                "material": not r.get("sem material"),
                "erro": r.get("erro"),
            }
        )
    dids = {c["documento_id"] for c in certs if c.get("documento_id")}
    return {
        "id": lv["id"],
        "titulo": lv["titulo"],
        "codigo": lv["codigo"],
        "etapa": fase,
        "degrau": _degrau(lv["escada"]),
        "escada": lv["escada"],
        "estrela": lv["estrela"],
        "prazo": lv["inscricao_fim"],
        "situacao_prazo": lv["situacao_prazo"],
        "link_oficial": lv["link_oficial"],
        "link_divulgacao": lv["link_divulgacao"],
        "itens": {
            k: {
                "valor": v.get("valor"),
                "trecho": (v.get("trecho") or "")[:300],
                "pagina": v.get("pagina"),
                "fase": v.get("fase"),
                "situacao": v.get("situacao"),
                "justificativa": v.get("justificativa"),
            }
            for k, v in validas.items()
        },
        "faltam": faltam,
        "relatorio": relatorio,
        "parecer": parecer,
        "repasse": REPASSE.get(fase, ""),
        "orientacao": orient,
        "tentativas": tent[-30:],
        "documentos": [docs[d] for d in sorted(dids) if d in docs][:20],
    }
