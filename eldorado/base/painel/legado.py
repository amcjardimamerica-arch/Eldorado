"""Os arquivos do painel que o gerador nunca preenchia (titular, 25/10/2026: "pedi para consertar diversas vezes os motores
e os mostradores deles do site continuam sem funcionamento").

O painel herdou do Eldorado0 33 arquivos de dados; 19 saíam com a estrutura vazia. Este módulo liga os dos motores e dos
pilotos ao que o sistema mede: a lista dos motores com a leitura de cada um (a mesma da sala), as missões e o plano de
voo dos pilotos, os achados aceitos, os alarmes abertos e as empresas. A trava test_nenhum_arquivo_do_site_vazio impede
que um arquivo lido pelo site volte a sair vazio.
"""

from __future__ import annotations

import json
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta, timezone


def _idade_h(iso: str | None, agora: datetime) -> float | None:
    if not iso:
        return None
    try:
        q = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
    except ValueError:
        return None
    if q.tzinfo is None:
        q = q.replace(tzinfo=timezone.utc)
    return (agora - q).total_seconds() / 3600


def montar(
    bib: sqlite3.Connection, cer: sqlite3.Connection, motores: list[dict], pilotos: dict[str, dict], molde, agora: datetime | None = None
) -> dict[str, dict]:
    agora = agora or datetime.now(timezone.utc)
    iso, hoje = agora.isoformat(timespec="seconds"), agora.date().isoformat()
    fmt = bib.row_factory
    bib.row_factory = None
    try:
        return _montar(bib, cer, motores, pilotos, molde, agora, iso, hoje)
    finally:
        bib.row_factory = fmt


def _montar(bib, cer, motores, pilotos, molde, agora, iso, hoje) -> dict[str, dict]:
    saida: dict[str, dict] = {}
    aceitos = defaultdict(list)
    for mot, em, tit, link, lid in bib.execute(
        "SELECT motor, encontrado_em, titulo, link_divulgacao, livro_id FROM achado "
        "WHERE decisao = 'aceito' AND encontrado_em >= ? ORDER BY encontrado_em",
        ((agora - timedelta(days=31)).date().isoformat(),),
    ):
        aceitos[mot].append({"em": em, "titulo": tit, "link": link, "livro": lid})
    try:
        execucoes = defaultdict(list)
        for mot, ini, erro in cer.execute(
            "SELECT motor, inicio, erro FROM execucao_motor WHERE inicio >= ?", (agora.replace(day=1).date().isoformat(),)
        ):
            execucoes[mot].append((ini, erro))
    except sqlite3.Error:
        execucoes = defaultdict(list)
    # ---- o alerta, a auditoria e a validação do mês dos motores
    alertas, ok, itens, por_estado = [], [], [], defaultdict(int)
    for m in motores:
        mid, luz = m.get("id"), m.get("luz")
        ult = m.get("ultima_leitura") or m.get("ultima")
        idade = _idade_h(ult, agora)
        ach14 = [a for a in aceitos.get(mid, []) if (a["em"] or "") >= (agora - timedelta(days=14)).date().isoformat()]
        if str(mid).startswith("piloto"):
            estado = "FUNCIONANDO" if luz == "verde" else "PARADO"
        elif ult is None:
            estado = "NUNCA RODOU"
        elif luz == "vermelho" and "bloque" in str(m.get("resultado", "")).lower():
            estado = "BLOQUEADO"
        elif idade is not None and idade > 48:
            estado = "PARADO"
        elif ach14:
            estado = "FUNCIONANDO"
        else:
            estado = "LENDO SEM ACHAR"
        por_estado[estado] += 1
        item = {
            "id": mid,
            "motor": mid,
            "nome": m.get("nome"),
            "estado": estado,
            "luz": luz,
            "ultima_leitura": ult,
            "resultado": m.get("resultado"),
            "achados_14_dias": len(ach14),
            "motivo": m.get("resultado"),
        }
        itens.append(item)
        (ok if luz == "verde" else alertas).append({**item, "alerta": None if luz == "verde" else (m.get("resultado") or "sem leitura recente")})
    a = molde("alerta_motores.json")
    a.update(
        {
            "em": iso,
            "data": hoje,
            "total": len(motores),
            "funcionando": len(ok),
            "em_alerta": len(alertas),
            "alertas": alertas,
            "ok": ok,
            "bloqueio_conhecido": [i for i in itens if i["estado"] == "BLOQUEADO"],
            "regra": "a leitura de cada motor (a mesma da sala de controle): verde = leu na cadência sem erro",
        }
    )
    saida["alerta_motores.json"] = a
    au = molde("auditoria_motores.json")
    au.update(
        {
            "em": iso,
            "cadencia_dias": 1,
            "total": len(itens),
            "por_estado": {k: por_estado.get(k, 0) for k in ("BLOQUEADO", "PARADO", "NUNCA RODOU", "LENDO SEM ACHAR", "FUNCIONANDO")},
            "correcoes_de_hoje": [],
            "itens": itens,
        }
    )
    saida["auditoria_motores.json"] = au
    dias_no_mes = agora.day
    val = {}
    for m in motores:
        mid = m.get("id")
        dias = sorted({(i or "")[:10] for i, _e in execucoes.get(mid, [])})
        erros = sum(1 for _i, e in execucoes.get(mid, []) if e)
        val[mid] = {
            "nome": m.get("nome"),
            "dias_executados": len(dias),
            "dias_no_periodo": dias_no_mes,
            "execucoes": len(execucoes.get(mid, [])),
            "com_erro": erros,
            "achados_aceitos": len(aceitos.get(mid, [])),
            "situacao": "integro" if len(dias) >= max(1, dias_no_mes - 2) and not erros else "com lacunas" if dias else "não executou",
        }
    v = molde("validacao_motores_mes.json")
    v.update(
        {
            "em": iso,
            "mes": hoje[:7],
            "ate": hoje,
            "dias_no_periodo": dias_no_mes,
            "motores": val,
            "resumo": {
                "integros": sum(1 for x in val.values() if x["situacao"] == "integro"),
                "com_lacunas": sum(1 for x in val.values() if x["situacao"] == "com lacunas"),
                "nao_executaram": sum(1 for x in val.values() if x["situacao"] == "não executou"),
            },
            "pergunta": "cada motor rodou todos os dias do mês, sem erro?",
        }
    )
    saida["validacao_motores_mes.json"] = v
    # ---- a saúde (os alarmes abertos)
    try:
        abertos = [
            {"modulo": mo, "mensagem": me, "gravidade": g, "aberto_em": em}
            for mo, me, g, em in cer.execute(
                "SELECT modulo, mensagem, gravidade, aberto_em FROM alarme WHERE fechado_em IS NULL ORDER BY aberto_em DESC LIMIT 60"
            )
        ]
    except sqlite3.Error:
        abertos = []
    s_ = molde("saude.json")
    s_.update({"em": iso, "alertas": abertos, "ok": [{"modulo": i["id"], "mensagem": i["resultado"]} for i in itens if i["luz"] == "verde"]})
    saida["saude.json"] = s_
    # ---- os pilotos: ao vivo, a posição, os briefings, os resgates e o radar
    ult_p = max(pilotos.values(), key=lambda x: x.get("ultima") or "", default={})
    quem = next((k for k, x in pilotos.items() if x is ult_p), "piloto-interceptador")
    idade_min = (_idade_h(ult_p.get("ultima"), agora) or 1e9) * 60
    pv = molde("piloto_ao_vivo.json")
    pv.update(
        {
            "motor": "ligado" if idade_min < 20 else "parado",              # o quadro do Espião lê ligado/parado (25/10/2026)
            "motor_frase": f"{quem}: {ult_p.get('resultado', '')}",
            "em": iso,
            "sinal_em": ult_p.get("ultima") or "",
            "minutos_sem_sinal": int(idade_min) if idade_min < 1e8 else -1,
            "estado": "em voo" if idade_min < 20 else "no pátio",
            "frase": "os pilotos voam de forma permanente durante o ciclo (o Interceptador um livro por vez; o Espião missão após missão)",
            "proximo_voo": "contínuo",
            "sem_sinal_a_partir_de_min": 60,
            "missao_atual": None,   # a missão em curso vem na posição (piloto_posicao.json) e na esquadrilha
            "voos_hoje": sum(1 for x in pilotos.values() if (x.get("ultima") or "") >= hoje),
        }
    )
    saida["piloto_ao_vivo.json"] = pv
    # 26/10/2026: a posição e o voo no formato que o painel lê (o avião decola sobre o motor do piloto)
    def _sinais(marcador: str, n: int = 40) -> list[tuple[str, str]]:
        try:
            return list(cer.execute("SELECT em, motivo FROM medicao WHERE marcador = ? ORDER BY em DESC LIMIT ?", (marcador, n)))
        except sqlite3.Error:
            return []
    esp = [(em, m) for em, m in _sinais("piloto:espiao") if str(m).startswith("em voo")]
    e_idade = (_idade_h(esp[0][0], agora) or 1e9) * 60 if esp else 1e9
    saida["piloto_posicao.json"] = (
        {"estado": "em_voo", "atualizado_em": esp[0][0], "validade_s": 480,
         "missao": {"motor": "piloto-aberto", "tipo": "reconhecimento", "alvo_titulo": str(esp[0][1]).removeprefix("em voo: ").split(" (autorizada")[0],
                    "ordem": sum(1 for em, _m in esp if em[:10] == esp[0][0][:10]), "de": None}}
        if e_idade < 8 else {"estado": "patio", "atualizado_em": esp[0][0] if esp else iso, "missao": None})
    itc = [(em, m) for em, m in _sinais("piloto:interceptador") if str(m).startswith("em voo")]
    i_idade = (_idade_h(itc[0][0], agora) or 1e9) * 60 if itc else 1e9
    alvo = str(itc[0][1]).split("): ", 1)[-1] if itc else ""
    saida["interceptador_ao_vivo.json"] = {
        "estado": "em_voo" if i_idade < 25 else "patio", "atualizado_em": itc[0][0] if itc else iso, "inicio": itc[0][0] if itc else None,
        "fim": None if i_idade < 25 else (itc[0][0] if itc else None), "etapa": "o plano de voo (os itens que faltam)",
        "alvo": {"titulo": alvo} if alvo else None, "passos": None, "detalhe": str(itc[0][1]) if itc else "",
        "resultado": {}, "parecer": None,
        "voos_em_24h": sum(1 for em, _m in itc if (_idade_h(em, agora) or 1e9) < 24),
    }
    try:
        missoes = cer.execute("SELECT em, familia, consulta, resultados, achados FROM espiao_missao ORDER BY em DESC LIMIT 80").fetchall()
    except sqlite3.Error:
        missoes = []
    b = molde("briefings_piloto.json")
    b.update(
        {
            "em": iso,
            "total": len(missoes),
            "voos": [{"em": em, "familia": f, "consulta": c, "resultados": r, "achados": a_} for em, f, c, r, a_ in missoes],
        }
    )
    saida["briefings_piloto.json"] = b
    fila = (
        bib.execute(
            "SELECT l.id, l.titulo, p.desde FROM livro l JOIN passaporte p ON p.livro_id = l.id WHERE p.fase = 'analise externa' "
            "AND l.situacao NOT IN ('excluido', 'unido') ORDER BY p.desde DESC LIMIT 200"
        ).fetchall()
        if _tem(bib, "passaporte", "desde")
        else bib.execute(
            "SELECT l.id, l.titulo, NULL FROM livro l JOIN passaporte p ON p.livro_id = l.id WHERE p.fase = 'analise externa' "
            "AND l.situacao NOT IN ('excluido', 'unido') LIMIT 200"
        ).fetchall()
    )
    resgatados = bib.execute(
        "SELECT COUNT(DISTINCT livro_id) FROM passagem WHERE de = 'analise externa' AND para IN ('farol', 'validacao', 'preparacao')"
    ).fetchone()[0]
    rg = molde("resgates_piloto.json")
    rg.update(
        {
            "em": iso,
            "total": len(fila) + resgatados,
            "por_estado": {"resgatado": resgatados, "aguardando": len(fila)},
            "regra": "o livro que o Interceptador esgotou vai ao Claude no Chrome; o resgate é a volta dele com informação nova",
            "fila": [{"livro": i, "titulo": t, "desde": d} for i, t, d in fila],
        }
    )
    saida["resgates_piloto.json"] = rg
    try:
        emp = bib.execute(
            "SELECT cnpj, razao_social, nome_fantasia, uf, site FROM empresa WHERE uf = 'GO' AND (site IS NULL OR site = '') "
            "ORDER BY razao_social LIMIT 300"
        ).fetchall()
        n_go = bib.execute("SELECT COUNT(*) FROM empresa WHERE uf = 'GO'").fetchone()[0]
    except sqlite3.Error:
        emp, n_go = [], 0
    rd = molde("radar_piloto.json")
    rd.update(
        {
            "em": iso,
            "total": n_go,
            "por_marcador": {"a_pesquisar": len(emp), "em_pesquisa": 0, "concluido": max(0, n_go - len(emp))},
            "regra": "as empresas de Goiás sem o site levantado: o Espião pesquisa o contato e o programa social",
            "empresas": [{"cnpj": c, "nome": f or r, "uf": u, "marcador": "a_pesquisar"} for c, r, f, u, _s in emp],
        }
    )
    saida["radar_piloto.json"] = rd
    # ---- os motores manuais (os que dependem da ponte ou do computador da titular) e os achados do dia
    mm = molde("motores_manuais.json")
    mm.update(
        {
            "em": iso,
            "regra": "os motores cujos sites recusam a nuvem: lidos pela ponte BR (HostGator) ou pelo computador da titular",
            "desligados": {i["id"]: {"motivo": i["resultado"], "estado": i["estado"]} for i in itens if i["estado"] in ("BLOQUEADO", "NUNCA RODOU")},
            "historico": [],
        }
    )
    saida["motores_manuais.json"] = mm
    dias, primeira, vistos = defaultdict(list), {}, defaultdict(int)
    for mot, lista in aceitos.items():
        for x in lista:
            d = (x["em"] or "")[:10]
            dias[d].append({"titulo": x["titulo"], "motor": mot, "link": x["link"], "livro": x["livro"]})
            if x["livro"]:
                vistos[x["livro"]] += 1
                primeira.setdefault(x["livro"], d)
    ad = molde("achados_dia.json")
    ad.update(
        {
            "em": iso,
            "regra": "os achados aceitos de cada dia (os últimos 31 dias), por motor",
            "dias": dict(sorted(dias.items(), reverse=True)),
            "primeira_data": primeira,
            "reapresentados": {k: v for k, v in vistos.items() if v > 1},
            "total_unicos": len(vistos),
            "total_reapresentacoes": sum(v - 1 for v in vistos.values() if v > 1),
        }
    )
    saida["achados_dia.json"] = ad
    return saida


def _tem(con: sqlite3.Connection, tabela: str, coluna: str) -> bool:
    return coluna in {r[1] for r in con.execute(f"PRAGMA table_info({tabela})")}


__all__ = ["montar", "json"]
