"""MISSÕES ESPECIAIS — resgate de edital incompleto.

Os outros 28 motores acham editais o tempo todo, mas muitos chegam pela metade: o título
está lá, a página oficial não; o prazo não foi lido; ninguém sabe que documentos anexar.
Sem isso o edital não serve para nada — não dá para decidir se vale concorrer.

Este módulo monta a FILA DE RESGATE: todo edital do acervo a que falte informação mínima
entra aqui, e o Piloto atende essa fila ANTES de sair explorando. Resgatar um edital que já
temos vale mais do que descobrir um que ainda não sabemos usar.

O MÍNIMO que um edital precisa ter para o sistema trabalhar com ele:
    página oficial · prazo de inscrição · quem pode concorrer · documentos exigidos ·
    valor ou faixa de valor · como se inscreve

O que o Piloto completa vai para a ficha do edital na Biblioteca de Alexandria.
"""
from __future__ import annotations

import json
import re
from datetime import date, timedelta
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json

FILA = ROOT / "estado/piloto/fila_resgate.json"
PARA_O_CLAUDE = ROOT / "estado/piloto/fila_do_claude.json"

# O PNCP NÃO É TRABALHO DO PILOTO. São dados genéricos de compras públicas: quem os analisa é
# o Claude, por fora, com acesso à máquina do titular. Em 23/09 a fila do Piloto tinha 57
# alvos e TODOS eram PNCP — ele passou dois dias inteiros no que não lhe cabe.
PNCP = re.compile(r"pncp|portal de compras|compras\.gov|comprasnet", re.I)


def _e_pncp(e: dict) -> bool:
    return bool(PNCP.search(" ".join(str(e.get(c) or "") for c in
                                     ("origem", "pagina_oficial", "url", "titulo", "orgao", "fonte"))))
PUB = ROOT / "docs/dados/resgates_piloto.json"
MINIMO = ("pagina_oficial", "prazo", "quem_pode", "documentos", "valor", "como_inscrever")
PESO = {"pagina_oficial": 5, "prazo": 5, "documentos": 3, "como_inscrever": 3, "quem_pode": 2, "valor": 2}


def _falta(e: dict) -> list[str]:
    """O que impede este edital de ser usado."""
    f = []
    if not (e.get("pagina_oficial") or e.get("url") or e.get("onde")):
        f.append("pagina_oficial")
    if not (e.get("prazo") or e.get("fim") or e.get("inscricoes_ate")):
        f.append("prazo")
    if not (e.get("quem_pode") or e.get("publico")):
        f.append("quem_pode")
    if not (e.get("documentos") or e.get("anexos")):
        f.append("documentos")
    if not (e.get("valor") or e.get("valor_total") or e.get("faixa")):
        f.append("valor")
    if not (e.get("como_inscrever") or e.get("onde_inscrever") or e.get("inscricao")):
        f.append("como_inscrever")
    return f


# A associação é de assistência social e cultura. Um credenciamento de leiloeiros ou um
# cadastro de profissionais de saúde é edital incompleto, sim — mas nao serve para nada aqui.
# Sem este filtro, 25 das 60 missoes foram gastas resgatando papel que nunca seria usado.
SERVE = ("assistência social", "assistencia social", "cultura", "cultural", "esporte", "lazer",
         "criança", "crianca", "adolescente", "idoso", "juventude", "pessoa com deficiência",
         "organização da sociedade civil", "organizacao da sociedade civil", "osc", "terceiro setor",
         "fomento", "colaboração", "colaboracao", "parceria", "mrosc", "chamamento público de projetos",
         "seleção de projetos", "selecao de projetos", "subvenção", "subvencao", "emenda",
         "oficina", "capacitação", "capacitacao", "inclusão", "inclusao", "vulnerabilidade",
         "convivência", "convivencia", "socioeducativ", "socioassistencial", "cras", "creas",
         "patrocínio", "patrocinio", "edital de apoio", "prêmio", "premio")
NAO_SERVE = ("aquisicao de genero", "aquisicao de material", "aquisicao de equipamento",
             "generos alimenticios", "leiloeiro", "profissionais de saúde", "profissionais de saude", "médico", "medico",
             "medicamento", "insumo hospitalar", "órtese", "ortese", "prótese", "protese",
             "locação de veículo", "locacao de veiculo", "combustível", "combustivel",
             "obra", "pavimentação", "pavimentacao", "reforma predial", "merenda", "gênero alimentício",
             "genero alimenticio", "material de expediente", "coleta de lixo", "engenharia",
             "estabelecimento de saúde", "estabelecimento de saude", "laboratório", "laboratorio",
             "exames", "consulta médica", "consulta medica", "transporte escolar", "vigilância", "vigilancia")


def _sem_acento(s: str) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", str(s or "").lower())
                   if unicodedata.category(c) != "Mn")


# CREDENCIAMENTO NÃO É CAPTAÇÃO. A entidade se cadastra para PRESTAR serviço ao município e
# ser paga por isso — é habilitação de fornecedor, com outro rito, outro contrato e outra
# finalidade. No banco de provas de 23/09, 53 dos 60 alvos da fila eram credenciamento: o
# Piloto gastava quase todo o esforço de resgate em papel que nunca viraria fomento.
# Fica de fora, salvo quando o texto também fala de fomento, colaboração ou apoio a projeto.
CREDENCIAMENTO = ("credenciamento", "credenciar", "cadastramento de prestador",
                  "habilitacao de fornecedor", "chamamento para credenciamento")
# A exceção tem de ser o OBJETO do edital, não uma palavra de passagem: "credenciamento de
# empresa especializada em captação de patrocínio" mencionava patrocínio e não era fomento.
# Só termos que nomeiam o instrumento de repasse abrem exceção ao veto de credenciamento.
FOMENTO_MESMO = ("termo de fomento", "termo de colaboracao", "subvencao social",
                 "selecao de projeto", "apoio a projeto", "emenda parlamentar",
                 "fomento a projeto", "chamamento publico de projeto")


def _relevante(e: dict) -> tuple[bool, str]:
    """Este edital serve à nossa associação? Devolve (serve, por quê).

    O casamento ignora acento e plural: em 23/09 a fila tinha "AQUISIÇÃO EXCLUSIVA DE GÊNEROS
    ALIMENTÍCIOS" porque a lista dizia "gênero alimentício", no singular e com acento.
    """
    txt = _sem_acento(" ".join(str(e.get(c) or "") for c in ("titulo", "objeto", "orgao", "familia")))
    for n in NAO_SERVE:
        raiz = _sem_acento(n).rstrip("s")          # "generos alimenticios" casa com "genero alimenticio"
        if raiz and raiz in txt:
            return False, f"fora do nosso objeto ({n})"
    if any(c in txt for c in CREDENCIAMENTO) and not any(f in txt for f in FOMENTO_MESMO):
        return False, "credenciamento: habilitação para prestar serviço, não captação"
    achou = [s for s in SERVE if _sem_acento(s).rstrip("s") in txt]
    if achou:
        return True, "serve: " + ", ".join(achou[:3])
    return False, "não diz respeito a projeto de OSC"


def _urgencia(e: dict, falta: list[str]) -> int:
    """Quanto este resgate importa. Falta grave pesa mais; edital de Goiás e recente pesa mais."""
    p = sum(PESO.get(x, 1) for x in falta)
    if (e.get("uf") or "").upper() == "GO":
        p += 6
    if str(e.get("prazo") or e.get("fim") or "") >= date.today().isoformat():
        p += 8                                        # ainda dá tempo de concorrer: prioridade máxima
    if (e.get("veredito") or "") in ("aprovado", "atencao"):
        p += 4
    if (e.get("familia") or "") in ("cultura", "assistencia", "esporte", "terceiro_setor"):
        p += 3
    return p


def _acervo() -> list[dict]:
    """Os editais que o sistema já conhece, venham de onde vierem."""
    saida = []
    base = sorted((ROOT / "dados/editais").glob("*-eldorado-*-completo.json"), reverse=True)
    if base:
        itens = load_json(base[0]).get("itens") or {}
        for k, e in (itens.items() if isinstance(itens, dict) else enumerate(itens)):
            saida.append({"id": str(k), "titulo": (e.get("objeto") or "")[:130], "uf": e.get("uf"),
                          "orgao": e.get("orgao"), "pagina_oficial": e.get("pagina_oficial"),
                          "prazo": e.get("fim"), "veredito": e.get("veredito"), "familia": e.get("familia"),
                          "origem": "acervo PNCP/motores", **{c: e.get(c) for c in ("quem_pode", "documentos", "valor", "como_inscrever") if e.get(c)}})
    ach = ROOT / "docs/dados/achados_dia.json"
    if ach.exists():
        d = load_json(ach)
        for e in (d.get("itens") or d.get("achados") or [])[:400]:
            saida.append({"id": "achado-" + re.sub(r"[^a-z0-9]", "", str(e.get("titulo", "")).lower())[:30],
                          "titulo": (e.get("titulo") or "")[:130], "uf": e.get("uf"),
                          "pagina_oficial": e.get("url") or e.get("onde"), "prazo": e.get("prazo"),
                          "origem": f"motor {e.get('motor') or '?'}"})
    return saida


def montar_fila(limite: int = 60) -> dict:
    """Varre o acervo e separa o que está incompleto, do mais urgente ao menos."""
    ja = load_json(FILA) if FILA.exists() else {}
    descartados: dict[str, int] = {}
    para_claude: dict[str, dict] = {}
    feitos = {k for k, v in (ja.get("itens") or {}).items() if v.get("estado") == "resgatado"}
    tentados = {k: v.get("tentativas", 0) for k, v in (ja.get("itens") or {}).items()}
    itens = {}
    for e in _acervo():
        # UMA ÚNICA VEZ. Cada edital é analisado uma vez pelo Piloto; se não achou, passa ao
        # Claude em vez de voltar à fila. Tentar de novo com o mesmo método daria o mesmo nada.
        if e["id"] in feitos or tentados.get(e["id"], 0) >= 1:
            continue
        f = _falta(e)
        if not f or not e.get("titulo"):
            continue
        if _e_pncp(e):
            para_claude[e["id"]] = {"titulo": (e.get("titulo") or "")[:130], "orgao": e.get("orgao"),
                                    "uf": e.get("uf"), "falta": _falta(e),
                                    "porque": "PNCP: dado genérico de compras públicas — análise externa do Claude"}
            continue
        serve, porque = _relevante(e)
        if not serve:
            descartados[porque[:40]] = descartados.get(porque[:40], 0) + 1
            continue
        itens[e["id"]] = {**e, "falta": f, "urgencia": _urgencia(e, f), "serve_porque": porque,
                          "estado": "aguardando", "tentativas": tentados.get(e["id"], 0)}
    # OPORTUNIDADES QUE O PRÓPRIO PILOTO ACHOU (25/09): as páginas de edital descobertas nos sites do terceiro
    # setor entram na fila de resgate — é aqui que ele confirma prazo e página oficial. A data de descoberta
    # vale como publicação recente: são anúncios lidos na semana, não arquivo.
    cc = ROOT / "estado/piloto/candidatas_do_catalogo.json"
    for c in ((load_json(cc) or {}).get("candidatas") or []) if cc.exists() else []:
        cid = "cat-" + __import__("hashlib").sha1(c["url"].encode()).hexdigest()[:12]
        if cid in feitos or tentados.get(cid, 0) >= 1:
            continue
        itens[cid] = {"id": cid, "titulo": c["titulo"], "url": c["url"], "orgao": c.get("visto_em"), "uf": None,
                      "descoberto_em": c.get("descoberto_em"), "enquadramento": c.get("enquadramento"),
                      "falta": ["prazo", "pagina_oficial"], "urgencia": 90, "serve_porque": c.get("como_se_enquadra"),
                      "estado": "aguardando", "tentativas": 0, "origem": "catálogo do Piloto"}
    ordenada = dict(sorted(itens.items(), key=lambda kv: -kv[1]["urgencia"])[:limite])
    d = {"em": now_iso(), "total_incompletos": len(itens), "na_fila": len(ordenada),
         "descartados_por_nao_servirem": descartados,
         "regra": "o Piloto atende esta fila ANTES de explorar: completar um edital que já temos vale mais que achar outro pela metade",
         "itens": {**{k: v for k, v in (ja.get("itens") or {}).items() if v.get("estado") == "resgatado"}, **ordenada}}
    write_json(FILA, d)
    write_json(PARA_O_CLAUDE, {
        "em": now_iso(), "total": len(para_claude),
        "regra": "o Piloto não toca PNCP: dado genérico de compras públicas. Quem analisa é o "
                 "Claude por fora, com acesso à máquina do titular (Claude Desktop).",
        "itens": para_claude})
    d["para_o_claude"] = len(para_claude)
    return {k: v for k, v in d.items() if k != "itens"}


def proximo(reservar: bool = True) -> dict | None:
    """O edital mais urgente à espera de resgate. Por padrão RESERVA o item (grava
    'em_resgate' no arquivo), senão a próxima chamada devolveria o mesmo de novo — foi
    assim que o voo saía com um resgate só em vez dos seis."""
    if not FILA.exists():
        montar_fila()
    d = load_json(FILA)
    pend = [(k, v) for k, v in (d.get("itens") or {}).items() if v.get("estado") == "aguardando"]
    if not pend:
        return None
    # A FILA PRECISA ANDAR. No banco de provas de 23/09, os 10 voos reservaram o MESMO alvo:
    # max() por urgência devolve sempre o primeiro do empate, e quem falha volta a "aguardando"
    # com a mesma urgência. O Piloto martelava um edital insolúvel e os outros 59 esperavam.
    # Agora quem já foi tentado cai na ordem, e o empate é desfeito por quem esperou mais.
    def _ordem(kv):
        _k, _v = kv
        return (-(_v.get("urgencia", 0) - 7 * _v.get("tentativas", 0)),
                _v.get("ultima_tentativa") or "", _k)
    k, v = min(pend, key=_ordem)
    if reservar:
        d["itens"][k]["estado"] = "em_resgate"
        write_json(FILA, d)
    return {"id": k, **v}


def plano_de_voo(ia, alvo: dict) -> dict:
    """O briefing da missão especial: o Piloto decide COMO achar o que falta neste edital."""
    r = ia.perguntar(
        "MISSÃO ESPECIAL — RESGATE DE EDITAL. Um edital já está no nosso acervo, mas incompleto, "
        "e sem esses dados ele não serve para decidir se vale concorrer.\n\n"
        f"EDITAL: {alvo.get('titulo')}\n"
        f"ÓRGÃO/FONTE: {alvo.get('orgao') or alvo.get('origem')}\n"
        f"UF: {alvo.get('uf') or '?'}\n"
        f"JÁ TEMOS: {json.dumps({k: v for k, v in alvo.items() if k in MINIMO and v}, ensure_ascii=False)}\n"
        f"FALTA: {alvo.get('falta')}\n\n"
        "Escreva consultas de busca que levem à PÁGINA OFICIAL deste edital específico (não a notícia sobre ele): "
        "o site do órgão, o portal onde foi publicado, o PDF do edital, a página de inscrições. "
        "Use o nome do órgão e o número ou nome do edital nas consultas.",
        '{"consultas": ["consulta 1", "consulta 2", "consulta 3"], '
        '"onde_provavelmente_esta": "site ou portal onde isto costuma ser publicado", '
        '"o_que_ler_na_pagina": ["prazo", "documentos exigidos", "..."]}')
    return {"id": "resgate-" + str(alvo.get("id"))[:28],
            "pergunta": f"Onde está a página oficial de: {alvo.get('titulo')} ({alvo.get('orgao') or ''})? "
                        f"Preciso de {', '.join(alvo.get('falta') or [])}.",
            "consultas_sugeridas": [c for c in ((r or {}).get("consultas") or []) if isinstance(c, str)][:3],
            "onde_procurar": (r or {}).get("onde_provavelmente_esta"),
            "o_que_ler": (r or {}).get("o_que_ler_na_pagina") or list(alvo.get("falta") or []),
            "nivel": "resgate", "alvo": "edital", "origem": "missao_especial", "edital": alvo}


def devolver_a_fila(alvo_id: str, tentado: bool = False) -> None:
    """Item reservado volta a aguardar. Se chegou a ser tentado, a tentativa fica contada —
    senão ele volta ao topo e é reservado de novo no voo seguinte, para sempre."""
    if not FILA.exists():
        return
    d = load_json(FILA)
    it = (d.get("itens") or {}).get(alvo_id)
    if it and it.get("estado") == "em_resgate":
        it["estado"] = "aguardando"
        if tentado:
            it["tentativas"] = it.get("tentativas", 0) + 1
            it["ultima_tentativa"] = now_iso()[:16]
        write_json(FILA, d)


def registrar_resgate(alvo_id: str, dados: dict, achou: bool) -> dict:
    d = load_json(FILA) if FILA.exists() else {"itens": {}}
    it = (d.get("itens") or {}).get(alvo_id)
    if not it:
        return {}
    it["tentativas"] = it.get("tentativas", 0) + 1
    it["ultima_tentativa"] = now_iso()[:16]
    # PRAZO IMPLAUSÍVEL NÃO ENTRA (26/09): um edital sendo resgatado como aberto não pode ter prazo de anos atrás —
    # o 4B gravou 2014-08-04 no Bondinho, a data da matéria, literal na página mas não o prazo.
    if achou and dados.get("prazo"):
        try:
            if date.fromisoformat(str(dados["prazo"])[:10]) < date.today() - timedelta(days=60):
                it["observacao_prazo"] = f"prazo {dados['prazo']} rejeitado: no passado distante — data da página, não do edital"
                dados = {k: v for k, v in dados.items() if k != "prazo"}
        except ValueError:
            dados = {k: v for k, v in dados.items() if k != "prazo"}
    if achou:
        faltava = list(it.get("falta") or [])
        it.update({k: v for k, v in dados.items() if v})
        # item vindo do catálogo não tem objeto nem órgão por natureza: o que falta é medido contra o que
        # faltava (prazo e página oficial), não contra a ficha completa — daí o "completou -1 de 2"
        it["falta"] = [f for f in _falta(it) if f in faltava] if it.get("origem") == "catálogo do Piloto" else _falta(it)
        it["estado"] = "resgatado" if not it["falta"] else "parcial"
        it["resgatado_em"] = now_iso()[:16]
        if it["estado"] == "resgatado":
            _para_biblioteca(alvo_id, it)
    else:
        it["estado"] = "entregue_ao_claude"
        it["porque"] = "o Piloto analisou uma vez e não achou a página oficial — passa ao Claude"
    d["em"] = now_iso()
    write_json(FILA, d)
    publicar()
    return it


def _para_biblioteca(alvo_id: str, it: dict) -> None:
    """Edital completo vira ficha na Biblioteca de Alexandria."""
    pasta = ROOT / "biblioteca_alexandria/oportunidades" / re.sub(r"[^a-z0-9-]", "-", str(it.get("titulo", ""))[:60].lower()).strip("-") / str(date.today().year)
    pasta.mkdir(parents=True, exist_ok=True)
    write_json(pasta / "ficha.json", {
        "titulo": it.get("titulo"), "orgao": it.get("orgao"), "uf": it.get("uf"),
        "pagina_oficial": it.get("pagina_oficial"), "prazo": it.get("prazo"),
        "quem_pode": it.get("quem_pode"), "documentos": it.get("documentos"),
        "valor": it.get("valor"), "como_inscrever": it.get("como_inscrever"),
        "situacao": "aberta" if str(it.get("prazo") or "") >= date.today().isoformat() else "arquivada",
        "completado_por": "Piloto (missão especial de resgate)", "em": now_iso(), "id_fila": alvo_id})


def publicar() -> dict:
    d = load_json(FILA) if FILA.exists() else {"itens": {}}
    its = d.get("itens") or {}
    por = {}
    for v in its.values():
        por[v.get("estado") or "?"] = por.get(v.get("estado") or "?", 0) + 1
    saida = {"em": now_iso(), "total": len(its), "por_estado": por,
             "regra": "missão especial tem prioridade sobre exploração",
             "fila": [{"id": k, "titulo": v.get("titulo"), "uf": v.get("uf"), "orgao": v.get("orgao"),
                       "falta": v.get("falta"), "urgencia": v.get("urgencia"), "estado": v.get("estado"),
                       "tentativas": v.get("tentativas"), "pagina_oficial": v.get("pagina_oficial")}
                      for k, v in sorted(its.items(), key=lambda kv: (kv[1].get("estado") != "aguardando", -(kv[1].get("urgencia") or 0)))[:60]]}
    write_json(PUB, saida)
    return {k: v for k, v in saida.items() if k != "fila"}


if __name__ == "__main__":
    print(json.dumps({**montar_fila(), **publicar()}, ensure_ascii=False, indent=1))
