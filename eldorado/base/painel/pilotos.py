"""Os pilotos no site, ligados aos dados (titular, 25/10/2026: sem leitura na página inicial e na sala de controle).

A página inicial lia o desenho herdado do Eldorado0 (espiao.json, espiao_ao_vivo.json, interceptador.json,
interceptador_ao_vivo.json, esquadrilha.json, achados_pilotos.json), que o gerador não preenchia; e a sala procurava a
leitura dos pilotos entre as execuções dos motores. Agora: o Espião pelas suas missões, famílias de consulta e achados
(no Cérebro e na Biblioteca); o Interceptador pelas tentativas do plano de voo e pelos achados.
"""

from __future__ import annotations

import json
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from ..missao import itens as I


def _json(t: str | None) -> dict:
    try:
        return json.loads(t or "{}") or {}
    except ValueError:
        return {}


def _idade_min(em: str | None, agora: datetime) -> float | None:
    if not em:
        return None
    try:
        q = datetime.fromisoformat(str(em).replace("Z", "+00:00"))
    except ValueError:
        return None
    if q.tzinfo is None:
        q = q.replace(tzinfo=timezone.utc)
    return (agora - q).total_seconds() / 60


def montar(bib: sqlite3.Connection, cer: sqlite3.Connection, molde, agora: datetime | None = None) -> tuple[dict[str, dict], dict[str, dict]]:
    """Os arquivos dos pilotos e a leitura de cada um para a lista dos motores da sala."""
    agora = agora or datetime.now(timezone.utc)
    iso, hoje = agora.isoformat(timespec="seconds"), agora.date().isoformat()
    h24 = (agora - timedelta(hours=24)).isoformat()
    fmt_ant = bib.row_factory
    bib.row_factory = None
    titulos = dict(bib.execute("SELECT id, titulo FROM livro"))
    estrela = dict(bib.execute("SELECT id, estrela FROM livro"))
    # ---- o Espião
    try:
        missoes = [
            dict(zip(("id", "em", "familia", "consulta", "resultados", "candidatos", "achados", "motivos", "bloqueada"), r, strict=False))
            for r in cer.execute(
                "SELECT id, em, familia, consulta, resultados, candidatos, achados, motivos, bloqueada FROM espiao_missao ORDER BY em"
            )
        ]
        familias = cer.execute("SELECT nome, a, b, usos, achados FROM espiao_familia").fetchall()
        consultas = cer.execute("SELECT texto, familia, usos, achados, ultima FROM espiao_consulta").fetchall()
    except sqlite3.Error:
        missoes, familias, consultas = [], [], []
    ach = defaultdict(list)
    for mot, aid, em, tit, link, lid, dec in bib.execute(
        "SELECT motor, id, encontrado_em, titulo, link_divulgacao, livro_id, decisao FROM achado "
        "WHERE motor IN ('espiao', 'interceptador') ORDER BY encontrado_em"
    ):
        ach[mot].append({"id": aid, "em": em, "titulo": tit or titulos.get(lid) or "", "link": link, "livro": lid, "decisao": dec})
    sinais = {}
    try:  # o sinal de vida de cada piloto (25/10/2026)
        for marcador, em, motivo in cer.execute("SELECT marcador, MAX(em), motivo FROM medicao WHERE marcador LIKE 'piloto:%' GROUP BY marcador"):
            sinais[marcador.split(":", 1)[1]] = (em, motivo)
    except sqlite3.Error:
        pass
    ult_m = max([missoes[-1]["em"] if missoes else "", (sinais.get("espiao") or ("", ""))[0]]) or None
    m_hoje = [m for m in missoes if (m["em"] or "") >= hoje]
    e = molde("espiao.json")
    e.update(
        {
            "em": iso,
            "papel": "a busca aberta no terceiro setor, orientada pelo Cérebro (o canivete de busca)",
            "modelo": "o canivete de busca (o buscador próprio, o DDGS por seis motores, o Marginalia, o Querido Diário e o PNCP)",
            "estado": "em voo" if (_idade_min(ult_m, agora) or 1e9) < 15 else ("no pátio" if ult_m else "aguardando a primeira missão"),
        }
    )
    e["ultimo_voo"] = {
        "voo_do_dia": len(m_hoje),
        "em": ult_m,
        "missoes": len(m_hoje),
        "abates": sum(m["achados"] or 0 for m in m_hoje),
        "propostas": sum(m["candidatos"] or 0 for m in m_hoje),
    }
    e["aprendizado"] = {
        "buscas_que_funcionam": [c[0] for c in sorted(consultas, key=lambda c: -(c[3] or 0)) if (c[3] or 0) > 0][:10],
        "buscas_que_falham": [c[0] for c in consultas if (c[2] or 0) >= 2 and not c[3]][:10],
        "rendimento_por_tipo": {f[0]: {"usos": f[3], "achados": f[4], "taxa": round((f[4] or 0) / f[3], 3) if f[3] else None} for f in familias},
        "em": ult_m,
    }
    e["fila"] = {
        "consultas de descoberta (rodízio)": len(consultas),
        "apostas do briefing por voo": len(familias),
        "indícios entregues ao Interceptador": len(ach["espiao"]),
    }
    e["acumulado"] = {
        **e.get("acumulado", {}),
        "missoes": len(missoes),
        "com_resultado": sum(1 for m in missoes if (m["resultados"] or 0) > 0),
        "nada_no_crivo": sum(1 for m in missoes if (m["resultados"] or 0) > 0 and not m["achados"]),
        "busca_sem_resposta": sum(1 for m in missoes if not m["resultados"]),
        "achados": len(ach["espiao"]),
        "abates": sum(1 for a in ach["espiao"] if a["decisao"] == "aceito"),
        "estrelas_de_ouro": sum(1 for a in ach["espiao"] if estrela.get(a["livro"]) == "ouro"),
        "indicios_entregues_ao_interceptador": len(ach["espiao"]),
    }

    def missao_quadro(m):  # a missão no formato do quadro do Espião (25/10/2026)
        return {
            "em": m["em"],
            "segundos": None,
            "modo": m["familia"],
            "missao": m["familia"],
            "de": "piloto-aberto",
            "alvo": m["consulta"],
            "qualidade": "com resultado" if m["achados"] else ("nada no crivo" if m["resultados"] else "busca sem resposta"),
            "achados": m["achados"] or 0,
            "abates": m["achados"] or 0,
            "inicio": m["em"],
            "fim": m["em"],
            "avaliacao": f"{m['achados']} achado(s)" if m["achados"] else ("nada passou no crivo" if m["resultados"] else "a busca não respondeu"),
            "licao": f"{m['resultados'] or 0} resultado(s), {m['candidatos'] or 0} candidato(s)",
            "encontrou": [],
        }

    e["missoes"] = [missao_quadro(m) for m in reversed(missoes[-20:])]
    e["acumulado"]["tempo_medio_min"] = None
    ev = {
        "estado": "em_voo" if (_idade_min(ult_m, agora) or 1e9) < 25 else ("pousou" if ult_m else "aguardando"),
        "atualizado_em": ult_m or iso,
        "inicio": ult_m,
        "fim": ult_m,
        "voo_do_dia": len(m_hoje),
        "etapa": (sinais.get("espiao") or ("", "missão de busca"))[1],
        "missao_atual": None,
        "plano": [{"ordem": k, "missao": f[0], "alvo": f"{f[3] or 0} usos, {f[4] or 0} achados"} for k, f in enumerate(familias[:6], 1)],
        "concluidas": [missao_quadro(m) for m in m_hoje][-6:],
        "anteriores": [
            {
                "inicio": m["em"],
                "fim": m["em"],
                "consulta": m["consulta"],
                "familia": m["familia"],
                "resultados": m["resultados"],
                "achados": m["achados"],
                "bloqueada": bool(m["bloqueada"]),
            }
            for m in reversed(missoes[-12:])
        ],
        "resultado": {"resultados": missoes[-1]["resultados"], "achados": missoes[-1]["achados"]} if missoes else {},
        "passos": [],
    }
    # ---- o Interceptador
    tents = []
    for lid, ferr, em, res in bib.execute(
        "SELECT livro_id, ferramenta, em, resultado FROM tentativa WHERE ferramenta LIKE 'abordagem %' ORDER BY em"
    ):
        r = _json(res)
        tents.append(
            {
                "livro": lid,
                "n": ferr.split()[-1],
                "em": em,
                "nome": r.get("ferramenta") or r.get("abordagem"),
                "para": r.get("para") or [],
                "material": not r.get("sem material"),
                "erro": r.get("erro"),
            }
        )
    certs = defaultdict(list)
    alvo_ids = {t["livro"] for t in tents}
    for c in bib.execute("SELECT livro_id, item, valor, situacao, fase, justificativa, trecho, pagina, id, em FROM certidao"):
        if c[0] in alvo_ids:
            certs[c[0]].append(
                dict(zip(("livro_id", "item", "valor", "situacao", "fase", "justificativa", "trecho", "pagina", "id", "em"), c, strict=False))
            )

    def cobertura(lid: str) -> tuple[int, int]:
        m = I.melhor(certs.get(lid, []))
        ok = [k for k in I.DOZE if I.resolvido(m.get(k))]
        return sum(1 for k in ok if m[k].get("situacao") == "comprovado"), sum(1 for k in ok if m[k].get("situacao") == "dispensado")

    por_livro: dict[str, list] = defaultdict(list)
    for t in tents:
        por_livro[t["livro"]].append(t)
    ordem_livros = sorted(por_livro, key=lambda lid: por_livro[lid][-1]["em"] or "")
    ult_t = max([tents[-1]["em"] if tents else "", (sinais.get("interceptador") or ("", ""))[0]]) or None
    recentes = [lid for lid in ordem_livros if (por_livro[lid][-1]["em"] or "") >= h24]
    cob = {lid: cobertura(lid) for lid in ordem_livros}
    i_ = molde("interceptador.json")
    i_.update(
        {
            "em": iso,
            "papel": "investiga um livro por vez, com o plano de voo pelos itens que faltam (orientado pelo Cérebro)",
            "modelo": "o plano de voo e o canivete (a escada completa, a leitura completa dos PDFs, o OCR das imagens, a busca)",
            "estado": "em voo" if (_idade_min(ult_t, agora) or 1e9) < 20 else ("no pátio" if ult_t else "aguardando o primeiro voo"),
            "ultimo_voo": ult_t or "",
        }
    )
    fila_n = bib.execute(
        "SELECT COUNT(*) FROM livro l JOIN passaporte p ON p.livro_id = l.id JOIN livro_dados d ON d.livro_id = l.id "
        "WHERE p.fase = 'preparacao' AND d.situacao_prazo = 'aberta' AND l.estrela <> 'ouro' "
        "AND l.situacao NOT IN ('excluido', 'unido')"
    ).fetchone()[0]
    i_["fila"] = {
        "editais novos dos motores": bib.execute("SELECT COUNT(*) FROM passaporte WHERE fase = 'preparacao'").fetchone()[0],
        "indícios do Espião": len(ach["espiao"]),
        "abertos com itens em falta": fila_n,
        "empresas sem ficha": 0,
    }
    i_["resumo"] = {
        "interceptados": len(recentes),
        "media_itens": round(sum(sum(cob[x]) for x in recentes) / len(recentes), 1) if recentes else 0,
        "com_prazo_confirmado": sum(1 for x in recentes if I.resolvido(I.melhor(certs.get(x, [])).get("Prazo de inscrição"))),
        "completos": sum(1 for x in recentes if sum(cob[x]) == 12),
    }
    i_["acumulado"] = {
        **i_.get("acumulado", {}),
        "interceptados": len(ordem_livros),
        "missoes": len(tents),
        "validadas": sum(1 for t in tents if t["material"]),
        "parciais": sum(1 for lid in ordem_livros if 0 < sum(cob[lid]) < 12),
        "insuficientes": sum(1 for lid in ordem_livros if sum(cob[lid]) == 0),
        "estrelas_de_ouro": sum(1 for lid in ordem_livros if estrela.get(lid) == "ouro"),
        "achados": len(ach["interceptador"]),
    }
    i_["editais"] = [
        {
            "id": lid,
            "titulo": titulos.get(lid, lid),
            "comprovados": cob[lid][0],
            "dispensados": cob[lid][1],
            "passos": len(por_livro[lid]),
            "com_material": sum(1 for t in por_livro[lid] if t["material"]),
        }
        for lid in reversed(ordem_livros[-12:])
    ]

    def missao_livro(lid):
        ps = por_livro[lid]
        com = [p for p in ps if p["material"]]
        try:
            seg = (datetime.fromisoformat(ps[-1]["em"]) - datetime.fromisoformat(ps[0]["em"])).total_seconds()
        except (TypeError, ValueError):
            seg = None
        comp, disp = cob[lid]
        return {
            "em": ps[-1]["em"],
            "segundos": seg,
            "modo": "plano de voo",
            "de": "piloto-interceptador",
            "alvo": titulos.get(lid, lid),
            "tipo": "edital",
            "qualidade": "validada" if comp + disp == 12 else "parcial" if comp + disp else "insuficiente",
            "comprovados": comp,
            "dispensados": disp,
            "total": 12,
            "avaliacao": f"{len(com)} de {len(ps)} passos com material",
            "justificativa": "; ".join(sorted({i for p in ps for i in (p["para"] or [])}))[:300],
            "encontrou": [p["nome"] for p in com if p["nome"]][:6],
            "nao_resolvidos": [],
            "rotas": [p["nome"] for p in ps if p["nome"]][:10],
        }

    i_["missoes"] = [missao_livro(lid) for lid in reversed(ordem_livros[-20:])]
    duracoes = [m["segundos"] for m in i_["missoes"] if m["segundos"]]
    i_["acumulado"]["tempo_medio_min"] = round(sum(duracoes) / len(duracoes) / 60, 1) if duracoes else None
    ult_livro = ordem_livros[-1] if ordem_livros else None
    iv = {
        "estado": "em_voo" if (_idade_min(ult_t, agora) or 1e9) < 25 else ("pousou" if ult_t else "aguardando"),
        "atualizado_em": ult_t or iso,
        "detalhe": (sinais.get("interceptador") or ("", "o próximo livro da fila (um por vez)"))[1],
    }
    if ult_livro:
        passos = por_livro[ult_livro]
        iv.update(
            {
                "inicio": passos[0]["em"],
                "fim": passos[-1]["em"],
                "etapa": passos[-1]["nome"] or f"abordagem {passos[-1]['n']}",
                "alvo": {"titulo": titulos.get(ult_livro, ult_livro), "modo": "plano de voo", "de": ult_livro},
                "resultado": {
                    "qualidade": "completo" if sum(cob[ult_livro]) == 12 else "parcial" if sum(cob[ult_livro]) else "sem itens ainda",
                    "comprovados": cob[ult_livro][0],
                    "dispensados": cob[ult_livro][1],
                    "total": 12,
                },
                "passos": [
                    {"abordagem": p["n"], "nome": p["nome"], "para": p["para"], "material": p["material"], "em": p["em"]} for p in passos[-10:]
                ],
                "parecer": f"{sum(1 for p in passos if p['material'])} de {len(passos)} passos com material",
            }
        )
    # ---- a esquadrilha, os achados por dia e a leitura de cada piloto para a sala
    ultimas = sorted(
        [
            {
                "motor": "piloto-aberto",
                "tipo": "cacar_oportunidade",
                "inicio": m["em"],
                "fim": m["em"],
                "achados": m["achados"] or 0,
                "alvo": m["consulta"],
            }
            for m in missoes[-12:]
        ]
        + [
            {
                "motor": "piloto-interceptador",
                "tipo": "afiar_motor",
                "inicio": por_livro[lid][0]["em"],
                "fim": por_livro[lid][-1]["em"],
                "achados": sum(1 for t in por_livro[lid] if t["material"]),
                "alvo": titulos.get(lid, lid),
            }
            for lid in ordem_livros[-12:]
        ],
        key=lambda x: x["fim"] or "",
        reverse=True,
    )[:16]
    q = molde("esquadrilha.json")
    q.update(
        {
            "em": iso,
            "missao_atual": None,
            "ultimas": ultimas,
            "abates": {
                "piloto-aberto": {"total": len(ach["espiao"]), "hoje": sum(1 for a in ach["espiao"] if (a["em"] or "") >= hoje)},
                "piloto-interceptador": {"total": len(ach["interceptador"]), "hoje": sum(1 for a in ach["interceptador"] if (a["em"] or "") >= hoje)},
            },
            "total_abates": len(ach["espiao"]) + len(ach["interceptador"]),
        }
    )
    por_dia = {"espiao": defaultdict(list), "interceptador": defaultdict(list)}
    for p in ("espiao", "interceptador"):
        for a in ach[p]:
            por_dia[p][(a["em"] or "")[:10]].append({"titulo": a["titulo"], "link": a["link"], "livro": a["livro"], "decisao": a["decisao"]})
    ap = {"em": iso, "espiao": dict(por_dia["espiao"]), "interceptador": dict(por_dia["interceptador"])}
    bib.row_factory = fmt_ant

    def leitura(ult: str | None, txt: str) -> dict:
        idade = _idade_min(ult, agora)
        return {
            "luz": "verde" if idade is not None and idade < 24 * 60 else "amarelo" if idade is not None and idade < 48 * 60 else "cinza",
            "ultima": ult,
            "resultado": txt,
        }

    status = {
        "piloto-aberto": leitura(ult_m, f"{len(m_hoje)} missões hoje · {len(missoes)} no total · {len(ach['espiao'])} achados"),
        "piloto-interceptador": leitura(
            ult_t, f"{len(recentes)} livros investigados em 24 h · {len(tents)} passos do plano de voo · {len(ach['interceptador'])} achados"
        ),
    }
    return (
        {
            "espiao.json": e,
            "espiao_ao_vivo.json": ev,
            "interceptador.json": i_,
            "interceptador_ao_vivo.json": iv,
            "esquadrilha.json": q,
            "achados_pilotos.json": ap,
        },
        status,
    )
