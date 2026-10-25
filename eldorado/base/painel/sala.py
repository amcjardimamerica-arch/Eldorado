"""A sala de controle (o plano: base/painel/sala.py): cada mostrador ligado ao dado MEDIDO pelo sistema (titular,
24/10/2026: nenhum mostrador zerado por falta de ligação). Os 39 instrumentos das 9 etapas, o caminho do dado, os
compartimentos, as contagens, o índice de saúde, os alarmes abertos, os fluxos automáticos, a linha do tempo e o
histórico, calculados da Biblioteca, do Cérebro, do mapa dos arquivos e dos fluxos do GitHub. O que o sistema ainda
não mede fica cinza, dizendo isso (nunca um zero inventado).
"""

from __future__ import annotations

import json
import os
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ETAPAS = {
    "regencia": ["rg_regencia", "ma_cobertura", "ma_esgotados", "dg_finalidade"],
    "coleta": ["mo_saude", "mo_cadencia", "mo_retentativa", "mo_fora_da_fila", "es_coleta"],
    "certificacao": ["ca_12", "fl_fila", "es_curadoria", "es_parcial"],
    "investigacao": ["pi_interceptador", "pi_espiao", "pi_piloto", "de_decisoes"],
    "externa": ["ve_para_o_chrome", "ve_bloqueadas", "ve_completas", "ve_importado", "al_externa"],
    "repositorio": ["es_abertas", "es_banco_unico"],
    "biblioteca": ["es_livros", "es_vigilancia", "em_rankings", "hi_uso", "hi_frio"],
    "aprendizado": ["rn_auc", "rn_precisao", "rn_revocacao", "rn_brier", "rn_treino"],
    "farol": ["es_validadas", "es_fichas"],
}
ORDEM = {"vermelho": 0, "amarelo": 1, "cinza": 2, "verde": 3}


def _idade_h(quando: str | None, agora: datetime) -> float | None:
    if not quando:
        return None
    try:
        q = datetime.fromisoformat(str(quando).replace("Z", "+00:00"))
    except ValueError:
        q = datetime.fromisoformat(str(quando)[:10]).replace(tzinfo=timezone.utc)
    if q.tzinfo is None:
        q = q.replace(tzinfo=timezone.utc)
    return round((agora - q).total_seconds() / 3600, 1)


def _faixa(v: float | None, verde, amarelo, maior_melhor: bool = True) -> str:
    if v is None:
        return "cinza"
    if maior_melhor:
        return "verde" if v >= verde else "amarelo" if v >= amarelo else "vermelho"
    return "verde" if v <= verde else "amarelo" if v <= amarelo else "vermelho"


def _github(agora: datetime) -> list[dict[str, Any]]:
    """Os fluxos automáticos (o sistema nervoso): a última execução de cada fluxo do GitHub."""
    token, repo = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"), os.environ.get("GITHUB_REPOSITORY")
    if not (token and repo):
        return []
    import urllib.request

    try:
        req = urllib.request.Request(f"https://api.github.com/repos/{repo}/actions/runs?per_page=60", headers={"Authorization": f"Bearer {token}"})
        runs = json.loads(urllib.request.urlopen(req, timeout=20).read())["workflow_runs"]
    except Exception:  # noqa: BLE001 — sem a API, os fluxos ficam sem leitura (cinza)
        return []
    vistos, saida = set(), []
    for r in runs:
        if r["name"] in vistos:
            continue
        vistos.add(r["name"])
        saida.append(
            {
                "nome": r["name"],
                "conclusao": r.get("conclusion"),
                "situacao": r.get("status"),
                "idade_h": _idade_h(r.get("updated_at"), agora),
                "quando": r.get("updated_at"),
                "evento": r.get("event"),
                "url": r.get("html_url"),
            }
        )
    return saida


def montar(
    bib: sqlite3.Connection, cer: sqlite3.Connection, raiz: Path, motores: list[dict[str, Any]], agora: datetime | None = None
) -> dict[str, Any]:
    agora = agora or datetime.now(timezone.utc)
    iso = agora.isoformat(timespec="seconds")
    h24, h48 = (agora - timedelta(hours=24)).isoformat(), (agora - timedelta(hours=48)).isoformat()
    hoje = agora.date().isoformat()
    q = lambda con, sql, *a: con.execute(sql, a).fetchone()[0]  # noqa: E731
    inst: dict[str, dict[str, Any]] = {}

    def I(id_, nome, valor, estado, motivo, quando=None, escala=None, faixa=None, efeito=None, cadencia_h=None):  # noqa: E743
        inst[id_] = {
            "id": id_,
            "nome": nome,
            "valor": valor,
            "estado": estado,
            "motivo": motivo,
            "quando": quando,
            "idade_h": _idade_h(quando, agora),
            "cadencia_h": cadencia_h,
            **({"escala": escala} if escala else {}),
            **({"faixa": faixa} if faixa else {}),
            **({"efeito": efeito} if efeito else {}),
        }

    # ---- os dados comuns
    reg = [m["id"] for m in motores if not str(m["id"]).startswith("piloto")]  # os pilotos são medidos à parte (Espião e Interceptador)
    ult = {m: (i, e) for m, i, e in cer.execute("SELECT motor, MAX(inicio), erro FROM execucao_motor GROUP BY motor")}
    lidos24 = [m for m in reg if (ult.get(m) or (None,))[0] and ult[m][0] >= h24]
    ok24 = [m for m in lidos24 if not ult[m][1]]
    com_erro = [m for m in reg if ult.get(m) and ult[m][1]]
    ultima_leitura = max((v[0] for v in ult.values() if v[0]), default=None)
    agenda = {r[0] for r in cer.execute("SELECT DISTINCT modulo FROM agenda")}
    AB = "FROM livro l JOIN livro_dados d ON d.livro_id = l.id WHERE d.situacao_prazo = 'aberta' AND l.situacao NOT IN ('excluido', 'unido')"
    abertas = q(bib, f"SELECT COUNT(*) {AB}")
    estrelas = Counter(dict(bib.execute(f"SELECT COALESCE(l.estrela, 'sem'), COUNT(*) {AB} GROUP BY 1").fetchall()))
    validadas = estrelas.get("prata", 0) + estrelas.get("ouro", 0)
    revisar = q(bib, f"SELECT COUNT(*) {AB} AND d.validacao = 'revisar'")
    fases = Counter(dict(bib.execute("SELECT fase, COUNT(*) FROM passaporte GROUP BY fase").fetchall()))
    # ---- 01 Regência
    n = len(reg) or 1
    cobertura = round(100 * len(lidos24) / n)
    I(
        "ma_cobertura",
        "Cobertura do dia (motores lidos em 24 h)",
        cobertura,
        _faixa(cobertura, 90, 60),
        f"{len(lidos24)} de {len(reg)} motores leram nas últimas 24 h",
        ultima_leitura,
        [0, 100],
        {"normal": [90, None], "alarme": [60, None]},
        cadencia_h=24,
    )
    esgot = [m for m in reg if not ((ult.get(m) or (None,))[0] and ult[m][0] >= h48 and not ult[m][1])]
    I(
        "ma_esgotados",
        "Motores sem leitura completa em 48 h",
        len(esgot),
        _faixa(len(esgot), 0, 5, False),
        ("sem leitura completa: " + ", ".join(esgot[:8]) + ("…" if len(esgot) > 8 else ""))
        if esgot
        else "todos os motores com leitura completa em 48 h",
        ultima_leitura,
    )
    fin = round(100 * validadas / abertas) if abertas else None
    I(
        "dg_finalidade",
        "Finalidade do sistema (abertas com prazo e link original)",
        fin,
        _faixa(fin, 60, 30),
        f"{validadas} de {abertas} oportunidades abertas com o prazo e o link original (estrela prata ou ouro)",
        iso,
        [0, 100],
        {"normal": [60, None], "alarme": [30, None]},
    )
    # ---- 02 Coleta
    I(
        "mo_saude",
        "Motores funcionando (leram sem erro em 24 h)",
        len(ok24),
        _faixa(len(ok24) / n, 0.9, 0.6),
        f"{len(ok24)} de {len(reg)} motores leram sem erro em 24 h",
        ultima_leitura,
        [0, len(reg)],
        {"normal": [round(0.9 * n), None], "alarme": [round(0.6 * n), None]},
        cadencia_h=24,
    )
    fora_cad = [m for m in reg if m not in lidos24]
    I(
        "mo_cadencia",
        "Motores fora da cadência (sem leitura em 24 h)",
        len(fora_cad),
        _faixa(len(fora_cad), 0, 5, False),
        ("fora da cadência: " + ", ".join(fora_cad[:8])) if fora_cad else "todos leram dentro da cadência",
        ultima_leitura,
    )
    I(
        "mo_retentativa",
        "Motores aguardando nova tentativa (última leitura com erro)",
        len(com_erro),
        _faixa(len(com_erro), 0, 3, False),
        ("com erro na última leitura: " + ", ".join(com_erro[:8])) if com_erro else "nenhum motor com erro na última leitura",
        ultima_leitura,
    )
    fora_fila = [m for m in reg if m not in agenda]
    I(
        "mo_fora_da_fila",
        "Motores registrados fora da agenda",
        len(fora_fila),
        _faixa(len(fora_fila), 0, 3, False),
        ("fora da agenda: " + ", ".join(fora_fila[:8])) if fora_fila else "todo motor registrado está na agenda",
        iso,
    )
    col = q(bib, "SELECT COUNT(*) FROM achado WHERE encontrado_em >= ?", (agora - timedelta(days=1)).date().isoformat())
    ultimo_achado = q(bib, "SELECT MAX(encontrado_em) FROM achado")
    I(
        "es_coleta",
        "Achados coletados (hoje e ontem)",
        col,
        "verde" if col else "amarelo",
        f"{col} achados entregues pelos motores desde ontem",
        ultimo_achado,
    )
    # ---- 03 Certificação
    comp = q(
        bib,
        f"SELECT COUNT(DISTINCT c.livro_id || '|' || c.item) FROM certidao c WHERE c.situacao = 'comprovado' AND c.livro_id IN (SELECT l.id {AB})",
    )
    pct = round(100 * comp / (abertas * 12)) if abertas else None
    ultima_cert = q(bib, "SELECT MAX(em) FROM certidao")
    I(
        "ca_12",
        "Itens certificados nas abertas (dos 12)",
        pct,
        _faixa(pct, 70, 40),
        f"{comp} de {abertas * 12} itens das abertas comprovados no documento",
        ultima_cert,
        [0, 100],
        {"normal": [70, None], "alarme": [40, None]},
    )
    I("fl_fila", "Livros na preparação", fases.get("preparacao", 0), "verde", "os livros que o Cartório está completando", ultima_cert)
    conf = q(bib, "SELECT COUNT(*) FROM livro_dados WHERE origem = 'confirmado'")
    I(
        "es_curadoria",
        "Links originais confirmados",
        conf,
        "verde" if conf else "amarelo",
        f"{conf} livros com a origem confirmada (o link original)",
        iso,
    )
    # os documentos sem texto (24/10/2026): a leitura ATUAL (os do sistema novo) e a lacuna da migração (os herdados,
    # relidos pela releitura) medidas em separado; vermelho só com falha da leitura atual ou a releitura travada
    sem = "NOT EXISTS (SELECT 1 FROM pagina p WHERE p.documento_id = d.id)"
    herd = "d.obtido_em LIKE '2026-10-22T18:58%'"
    parciais = q(bib, f"SELECT COUNT(*) FROM documento d WHERE {sem}")
    herd_sem = q(bib, f"SELECT COUNT(*) FROM documento d WHERE {herd} AND {sem}")
    novos = q(bib, f"SELECT COUNT(*) FROM documento d WHERE NOT ({herd}) OR d.obtido_em IS NULL")
    novos_sem = parciais - herd_sem
    try:
        relidos = q(cer, "SELECT COUNT(*) FROM releitura WHERE resultado LIKE 'relido%'")
        relidos_24h = q(cer, "SELECT COUNT(*) FROM releitura WHERE resultado LIKE 'relido%' AND ultima >= ?", h24)
        tentados_24h = q(cer, "SELECT COUNT(*) FROM releitura WHERE ultima >= ?", h24)
        indisponiveis = q(cer, "SELECT COUNT(*) FROM releitura WHERE tentativas >= 3 AND resultado NOT LIKE 'relido%'")
        ult_rel = q(cer, "SELECT MAX(ultima) FROM releitura")
    except sqlite3.Error:
        relidos = relidos_24h = tentados_24h = indisponiveis = 0
        ult_rel = None
    if novos and novos_sem / novos > 0.05:
        est_p = "vermelho"
    elif herd_sem - indisponiveis > 0 and tentados_24h and not relidos_24h:
        est_p = "vermelho"  # a releitura tentou e não conseguiu nada em 24 h
    elif herd_sem - indisponiveis > 0:
        est_p = "amarelo"  # em correção: a fila dos herdados
    else:
        est_p = "verde"
    I(
        "es_parcial",
        "Documentos sem texto lido",
        parciais,
        est_p,
        f"a leitura atual: {novos_sem} de {novos} documentos novos sem texto; a migração: {herd_sem} herdados sem texto em correção "
        f"(relidos: {relidos}, {relidos_24h} nas últimas 24 h; indisponíveis de vez: {indisponiveis})",
        ult_rel or iso,
    )
    # ---- 04 Investigação
    fila_i = q(bib, f"SELECT COUNT(*) {AB} AND l.estrela <> 'ouro' AND l.id IN (SELECT livro_id FROM passaporte WHERE fase = 'preparacao')")
    I(
        "pi_interceptador",
        "Na fila do Interceptador (abertas sem ouro na preparação)",
        fila_i,
        "verde",
        "o que falta nas abertas, para o Interceptador buscar",
        iso,
    )
    try:
        miss = q(cer, "SELECT COUNT(*) FROM espiao_missao WHERE em >= ?", h24)
        ult_m = q(cer, "SELECT MAX(em) FROM espiao_missao")
        I(
            "pi_espiao",
            "Missões do Espião em 24 h",
            miss,
            "verde" if miss else "vermelho",
            f"{miss} missões nas últimas 24 h (mínimo garantido: uma a cada 6 h)" if miss else "nenhuma missão em 24 h",
            ult_m,
            cadencia_h=6,
        )
    except sqlite3.Error:
        I("pi_espiao", "Missões do Espião em 24 h", None, "cinza", "o aprendizado do Espião ainda não está no Cérebro", None)
    voos = q(bib, "SELECT COUNT(*) FROM tentativa WHERE em >= ? AND ferramenta LIKE 'abordagem%'", h24)
    I(
        "pi_piloto",
        "Tentativas do Interceptador em 24 h",
        voos,
        "verde" if voos else "amarelo",
        f"{voos} abordagens do Interceptador nas últimas 24 h",
        q(bib, "SELECT MAX(em) FROM tentativa"),
    )
    ext = fases.get("analise externa", 0)
    I("de_decisoes", "Livros aguardando o Claude no Chrome", ext, _faixa(ext, 40, 100, False), f"{ext} livros na análise externa", iso)
    # ---- 05 Verificação externa
    I("ve_para_o_chrome", "Livros no lote do Chrome", ext, "verde" if ext <= 40 else "amarelo", f"{ext} livros esperando o Claude no Chrome", iso)
    lotes = sorted((raiz / "verificacao" / "lotes").glob("*.json")) if (raiz / "verificacao" / "lotes").exists() else []
    importados = (
        {p.stem for p in (raiz / "verificacao" / "vereditos" / "importados").glob("*.json")}
        if (raiz / "verificacao" / "vereditos" / "importados").exists()
        else set()
    )
    sem_retorno = [p.stem for p in lotes if not any(p.stem.split("lote-")[-1] in x for x in importados)]
    I(
        "ve_bloqueadas",
        "Lotes sem retorno do Chrome",
        len(sem_retorno),
        _faixa(len(sem_retorno), 1, 3, False),
        ("sem retorno: " + ", ".join(sem_retorno[-5:])) if sem_retorno else "todo lote teve retorno",
        iso,
    )
    chrome = q(bib, "SELECT COUNT(*) FROM veredito WHERE origem LIKE '%chrome%' OR origem LIKE '%externa%'")
    ult_v = q(bib, "SELECT MAX(em) FROM veredito WHERE origem LIKE '%chrome%' OR origem LIKE '%externa%'")
    I("ve_completas", "Vereditos do Chrome", chrome, "verde" if chrome else "cinza", f"{chrome} vereditos importados da análise externa", ult_v)
    idade_v = _idade_h(ult_v, agora)
    I(
        "ve_importado",
        "Último veredito importado (horas)",
        idade_v,
        _faixa(idade_v, 72, 168, False) if idade_v is not None else "cinza",
        "nenhum veredito importado ainda" if idade_v is None else f"último veredito há {idade_v:.0f} h",
        ult_v,
    )
    ult_lote = lotes[-1].stem if lotes else None
    idade_l = _idade_h(datetime.fromtimestamp(lotes[-1].stat().st_mtime, timezone.utc).isoformat(), agora) if lotes else None
    I(
        "al_externa",
        "Alimentação externa (o último lote)",
        idade_l,
        _faixa(idade_l, 48, 120, False) if idade_l is not None else "cinza",
        f"último lote: {ult_lote}" if ult_lote else "nenhum lote gerado",
        None if not lotes else datetime.fromtimestamp(lotes[-1].stat().st_mtime, timezone.utc).isoformat(),
    )
    # ---- 06 Repositório
    I(
        "es_abertas",
        "Oportunidades abertas",
        abertas,
        "verde" if abertas else "amarelo",
        f"{abertas} oportunidades com o prazo aberto",
        iso,
        efeito=f"{validadas} validadas · {estrelas.get('bronze', 0) + estrelas.get('sem', 0)} em verificação · {revisar} validação manual",
    )
    paralelos = sorted(p.relative_to(raiz).as_posix() for p in (raiz / "dados").rglob("*.db") if p.name not in ("biblioteca.db", "cerebro.db"))
    I(
        "es_banco_unico",
        "Bancos fora dos livros (paralelos)",
        len(paralelos),
        "verde" if not paralelos else "vermelho",
        ("bancos paralelos: " + ", ".join(paralelos[:6]) + ("…" if len(paralelos) > 6 else "")) if paralelos else "só a Biblioteca e o Cérebro",
        iso,
    )
    # ---- 07 Biblioteca
    livros = q(bib, "SELECT COUNT(*) FROM livro WHERE situacao NOT IN ('excluido', 'unido')")
    I(
        "es_livros",
        "Livros na Biblioteca",
        livros,
        "verde",
        f"{livros} livros (cada oportunidade com o seu)",
        q(bib, "SELECT MAX(atualizado_em) FROM livro"),
    )
    I(
        "es_vigilancia",
        "Livros vigiados pelo site original",
        conf,
        "verde" if conf else "amarelo",
        "os livros com a origem confirmada, vigiados pelo mapa do site original",
        iso,
    )
    emp = q(bib, "SELECT COUNT(*) FROM empresa") if bib.execute("SELECT 1 FROM sqlite_master WHERE name = 'empresa'").fetchone() else 0
    I("em_rankings", "Empresas na Biblioteca", emp, "verde" if emp else "cinza", f"{emp} empresas com incentivos registrados", iso)
    try:
        from ..cerebro.mapa_arquivos import AGUARDAM_DECISAO
        from ..cerebro.mapa_arquivos import montar as mapa

        parados = [x["id"] for x in mapa()["nos"] if not x["alcancado"] and x["id"] in AGUARDAM_DECISAO]   # os por desenho já estão decididos
        I(
            "hi_uso",
            "Arquivos fora do funcionamento",
            len(parados),
            "verde" if not parados else "amarelo",
            "aguardando a decisão da titular: " + ", ".join(parados) if parados else "nenhum arquivo fora do funcionamento sem decisão",
            iso,
        )
    except Exception as e:  # noqa: BLE001
        I("hi_uso", "Arquivos fora do funcionamento", None, "cinza", f"o mapa dos arquivos não foi lido: {type(e).__name__}", None)
    I(
        "hi_frio",
        "Livros no arquivo (encerradas, preservadas)",
        fases.get("arquivo", 0),
        "verde",
        "as oportunidades encerradas, arquivadas mantendo os livros",
        iso,
    )
    # ---- 08 Pertinência e aprendizado
    m = cer.execute(
        "SELECT treinado_em, discernimento, precisao, revocacao FROM modelo WHERE arquivo = 'rede:oportunidade' ORDER BY treinado_em DESC LIMIT 1"
    ).fetchone()
    if m:
        t, auc, pre, rev = m
        I(
            "rn_auc",
            "Discernimento da rede (oportunidade)",
            auc,
            _faixa(auc, 0.85, 0.7),
            f"área sob a curva ROC: {auc}",
            t,
            [0, 1],
            {"normal": [0.85, None], "alarme": [0.7, None]},
        )
        I(
            "rn_precisao",
            "Precisão da rede",
            pre,
            _faixa(pre, 0.85, 0.7),
            f"precisão: {pre}",
            t,
            [0, 1],
            {"normal": [0.85, None], "alarme": [0.7, None]},
        )
        I(
            "rn_revocacao",
            "Revocação da rede",
            rev,
            _faixa(rev, 0.85, 0.7),
            f"revocação: {rev}",
            t,
            [0, 1],
            {"normal": [0.85, None], "alarme": [0.7, None]},
        )
        idade_t = _idade_h(t, agora)
        I("rn_treino", "Idade do modelo (horas)", idade_t, _faixa(idade_t, 24, 72, False), f"treinado há {idade_t:.0f} h", t)
    else:
        for k, nome in (
            ("rn_auc", "Discernimento da rede"),
            ("rn_precisao", "Precisão da rede"),
            ("rn_revocacao", "Revocação da rede"),
            ("rn_treino", "Idade do modelo"),
        ):
            I(k, nome, None, "cinza", "a rede ainda não registrou um modelo treinado", None)
    try:
        b_ = cer.execute("SELECT treinado_em, brier FROM modelo WHERE arquivo = 'rede:oportunidade' AND brier IS NOT NULL "
                         "ORDER BY treinado_em DESC LIMIT 1").fetchone()
    except sqlite3.Error:
        b_ = None
    if b_:
        I("rn_brier", "Erro de calibração da rede", b_[1], _faixa(b_[1], 0.15, 0.25, False),
          f"erro de Brier {b_[1]:.3f} (0 = probabilidades perfeitas; até 0,15 bem calibrada)", b_[0], [0, 0.5],
          {"normal": [None, 0.15], "alarme": [None, 0.25]})
    else:
        I("rn_brier", "Erro de calibração da rede", None, "cinza", "aguardando o primeiro treino com a calibração (o nó da rede, a cada passagem)", None)
    # ---- 09 Farol
    I("es_validadas", "Livros na etapa Farol", fases.get("farol", 0), "verde", "os livros finalizados, liberados pela Regência", iso)
    transf = q(bib, "SELECT COUNT(DISTINCT livro_id) FROM transferencia")
    I(
        "es_fichas",
        "Livros transferidos ao Farol",
        transf,
        "verde" if transf else "amarelo",
        f"{transf} livros no formato estável (eldorado.livro/1)",
        q(bib, "SELECT MAX(em) FROM transferencia"),
    )
    # ---- os compartimentos e a Regência
    comp_ = []
    for et, ids in ETAPAS.items():
        if et == "regencia":
            continue
        est = min((inst[i]["estado"] for i in ids if i in inst), key=lambda k: ORDEM[k], default="cinza")
        comp_.append({"id": et, "estado": est})
    cumpridos = [c["id"] for c in comp_ if c["estado"] == "verde"]
    em_falha = [c["id"] for c in comp_ if c["estado"] == "vermelho"]
    I(
        "rg_regencia",
        "Compartimentos cumpridos",
        len(cumpridos),
        _faixa(len(cumpridos), 7, 4),
        f"{len(cumpridos)} de {len(comp_)} etapas no verde" + (f"; em falha: {', '.join(em_falha)}" if em_falha else ""),
        iso,
        [0, len(comp_)],
        {"normal": [7, None], "alarme": [4, None]},
    )
    est_reg = min((inst[i]["estado"] for i in ETAPAS["regencia"]), key=lambda k: ORDEM[k])
    comp_.insert(0, {"id": "regencia", "estado": est_reg})
    luz = {"verde": "verde", "vermelho": "vermelho", "amarelo": "amarelo"}
    for c in comp_:
        if c["id"] == "coleta":
            c["estrelas"] = [{"nome": x.get("nome"), "estado": luz.get(x.get("luz"), "cinza"), "resultado": x.get("resultado")} for x in motores]
    contagem = Counter(i["estado"] for i in inst.values())
    medidos = sum(contagem[k] for k in ("verde", "amarelo", "vermelho"))
    indice = round(100 * (contagem["verde"] + 0.5 * contagem["amarelo"]) / medidos) if medidos else 0
    # ---- o caminho do dado
    criados = q(bib, "SELECT COUNT(*) FROM livro WHERE criado_em >= ?", h24)
    mimico = [
        {"etapa": "Coleta", "valor": col},
        {"etapa": "Distintas", "valor": criados},
        {"etapa": "Abertas", "valor": abertas},
        {"etapa": "Com livro", "valor": livros},
        {"etapa": "Cartório", "valor": fases.get("preparacao", 0)},
        {"etapa": "Interceptador", "valor": fila_i},
        {"etapa": "Verificação externa", "valor": ext},
        {"etapa": "Prontas para o Farol", "valor": fases.get("farol", 0)},
    ]
    # ---- os alarmes abertos, a linha do tempo e o histórico
    niv = {"alta": "vermelho", "critica": "vermelho", "crítica": "vermelho", "media": "amarelo", "média": "amarelo"}
    # os alarmes abertos: agrupados pelo que falhou (a mensagem), com a contagem; o de um nó que voltou a concluir depois da
    # falha aparece resolvido (não aceso)
    import re as _re

    volta = dict(cer.execute("SELECT no, MAX(em) FROM execucao_passo WHERE estado = 'concluido' GROUP BY no").fetchall())
    grupos: dict[str, dict[str, Any]] = {}
    for id_, grav, mod, msg, quando, _rep in cer.execute(
        "SELECT id, gravidade, modulo, mensagem, aberto_em, repeticoes FROM alarme WHERE fechado_em IS NULL AND aberto_em >= ? ORDER BY aberto_em",
        (h24,),
    ):
        m_no = _re.search(r"o nó ([a-z_]+) falhou", msg or "")
        resolvido = bool(m_no and volta.get(m_no.group(1), "") > (quando or ""))
        chave = _re.sub(r"\d+", "#", (msg or mod or "")[:90])
        g = grupos.setdefault(
            chave,
            {
                "id": f"al-{id_}",
                "nome": (msg or mod or "")[:70],
                "nivel": niv.get(grav, "amarelo"),
                "motivo": (msg or "")[:240],
                "repeticoes": 0,
                "abertos": 0,
                "modulo": mod,
            },
        )
        g["repeticoes"] += 1
        g["abertos"] += int(not resolvido)
        g["quando"] = quando
    anunc = []
    for g in grupos.values():
        if g["repeticoes"] > 1:
            g["nome"] = f"{g['nome']} (×{g['repeticoes']})"
        if not g["abertos"]:
            g["nivel"], g["motivo"] = "verde", "resolvido: o nó voltou a concluir depois da falha · " + g["motivo"]
        anunc.append(g)
    linha = [
        {"em": r[1], "evento": f"{r[0]}: {r[2]}"} for r in cer.execute("SELECT workflow, inicio, estado FROM execucao ORDER BY inicio DESC LIMIT 30")
    ]
    hist: dict[str, Counter] = defaultdict(Counter)
    for d, e in cer.execute("SELECT substr(inicio, 1, 10), estado FROM execucao WHERE inicio >= ?", ((agora - timedelta(days=14)).isoformat(),)):
        hist[d]["concluidas" if e == "concluida" else "falhas" if e == "falhou" else "outras"] += 1
    detalhes = {
        "fora_da_cadencia": fora_cad,
        "com_erro": com_erro,
        "maestro": [{"id": m_, "cobertura": "lido" if m_ in lidos24 else "pendente"} for m_ in reg],
        "estantes": {k: estrelas.get(k, 0) for k in ("ouro", "prata", "bronze", "sem")},
        "por_etapa": dict(fases),
        "por_origem": dict(bib.execute(f"SELECT COALESCE(d.origem, 'sem'), COUNT(*) {AB} GROUP BY 1").fetchall()),
        "interceptador_fila": {"abertos com itens em falta": fila_i},
        "cartorio_itens": dict(
            bib.execute(
                f"SELECT c.item, COUNT(DISTINCT c.livro_id) FROM certidao c WHERE c.situacao = 'comprovado' AND c.livro_id IN (SELECT l.id {AB}) GROUP BY 1"
            ).fetchall()
        ),
    }
    # ---- a máquina (o servidor do GitHub onde o sistema roda): a última leitura e as últimas 3 horas
    maq: dict[str, Any] = {"alvo": 0.85}
    try:
        cols = [r[1] for r in cer.execute("PRAGMA table_info(maquina)")]
        ult_m = cer.execute("SELECT * FROM maquina ORDER BY em DESC LIMIT 1").fetchone()
        if ult_m:
            maq.update(
                {
                    c: ult_m[i]
                    for i, c in enumerate(cols)
                    if c in ("em", "processador", "memoria", "disco", "paralelismo", "nucleos", "memoria_total_mb", "disco_total_gb", "gpu")
                }
            )
            maq["idade_h"] = _idade_h(maq.get("em"), agora)
            maq["serie"] = [
                {"em": e, "p": p_, "m": m_}
                for e, p_, m_ in cer.execute(
                    "SELECT em, processador, memoria FROM maquina WHERE em >= ? ORDER BY em", ((agora - timedelta(hours=3)).isoformat(),)
                )
            ]
            serie_h = [max(x["p"] or 0, x["m"] or 0) for x in maq["serie"] if x["em"] >= (agora - timedelta(hours=1)).isoformat()]
            maq["uso_medio_1h"] = round(sum(serie_h) / len(serie_h), 3) if serie_h else None

        def ins(id_, nome, frac, normal, alarme, motivo):
            v = None if frac is None else round(100 * frac, 1)
            if v is None:
                est = "cinza"
            elif (alarme[0] is not None and v < alarme[0]) or (alarme[1] is not None and v > alarme[1]):
                est = "vermelho"
            elif (normal[0] is not None and v < normal[0]) or (normal[1] is not None and v > normal[1]):
                est = "amarelo"
            else:
                est = "verde"
            return {
                "id": id_,
                "nome": nome,
                "valor": v,
                "escala": [0, 100],
                "unidade": "%",
                "faixa": {"normal": normal, "alarme": alarme},
                "estado": est,
                "motivo": motivo,
                "quando": maq.get("em"),
            }

        # a rede do servidor (titular, 25/10/2026): a taxa pela diferença entre as duas últimas leituras (os bytes recebidos e
        # enviados são acumulados); o relógio mostra o uso em relação a 1 Gbit/s (125 MB/s)
        rede_frac, rede_motivo = None, "sem duas leituras da rede ainda"
        try:
            duas = cer.execute("SELECT em, rede_entrada, rede_saida FROM maquina WHERE rede_entrada IS NOT NULL ORDER BY em DESC LIMIT 2").fetchall()
            if len(duas) == 2:
                dt = (datetime.fromisoformat(duas[0][0]) - datetime.fromisoformat(duas[1][0])).total_seconds()
                if dt > 0 and duas[0][1] >= duas[1][1]:
                    ent, sai = (duas[0][1] - duas[1][1]) / dt, (duas[0][2] - duas[1][2]) / dt
                    rede_frac = min(1.0, (ent + sai) / 125e6)
                    rede_motivo = f"↓ {ent / 1e6:.2f} MB/s · ↑ {sai / 1e6:.2f} MB/s (média dos últimos {dt / 60:.0f} min; capacidade 1 Gbit/s)"
                    maq["rede"] = {"entrada_mb_s": round(ent / 1e6, 3), "saida_mb_s": round(sai / 1e6, 3)}
        except (sqlite3.Error, ValueError, TypeError):
            pass
        maq["instrumentos"] = [
            ins(
                "sv_processador",
                "Processador",
                maq.get("processador"),
                [None, 85],                                # a titular (25/10/2026): verde até 85%, laranja de 86% a 90%,
                [None, 90],                                # vermelho de 91% a 100%
                f"{maq.get('nucleos') or '?'} núcleos · verde até 85% · laranja de 86% a 90% · vermelho acima de 90%",
            ),
            ins(
                "sv_memoria", "Memória", maq.get("memoria"), [None, 85], [None, 95], f"{(maq.get('memoria_total_mb') or 0) / 1024:.1f} GB no servidor"
            ),
            ins("sv_disco", "Disco", maq.get("disco"), [None, 85], [None, 95], f"{maq.get('disco_total_gb') or '?'} GB no servidor"),
            ins("sv_gpu", "GPU", None, [None, None], [None, None], maq.get("gpu") or "o servidor do GitHub não tem placa de vídeo"),
            ins("sv_rede", "Rede", rede_frac, [None, 70], [None, 90], rede_motivo),
        ]
    except sqlite3.Error:
        pass
    return {
        "em": iso,
        "maquina": maq,
        "regra": "cada mostrador ligado ao dado medido pelo sistema (titular, 24/10/2026)",
        "indice_saude": indice,
        "instrumentos": list(inst.values()),
        "compartimentos": comp_,
        "regencia": {"cumpridos": len(cumpridos), "em_falha": len(em_falha)},
        "contagem": {k: contagem.get(k, 0) for k in ("verde", "amarelo", "vermelho", "cinza")},
        "anunciadores": anunc,
        "mimico": mimico,
        "linha_do_tempo": linha,
        "fluxos": _github(agora),
        "historico": [{"dia": d, **dict(v)} for d, v in sorted(hist.items())],
        "detalhes": detalhes,
        "hoje": hoje,
    }


def no_medir_sala(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem (o início): a sala de controle medida (no máximo a cada 15 min) e gravada no aprendizado do Cérebro;
    a Regência e a releitura agem pelo que ela mostra (titular, 24/10/2026: a sala é o parâmetro do funcionamento)."""
    import tomllib

    dados = Path(parametros.get("dados", "dados"))
    if not ((dados / "biblioteca.db").exists() and (dados / "cerebro.db").exists()):
        return [{"sala": "sem os bancos nesta pasta"}]
    agora = datetime.now(timezone.utc)
    cer = sqlite3.connect(f"file:{dados / 'cerebro.db'}?mode=ro", uri=True)
    bib = sqlite3.connect(f"file:{dados / 'biblioteca.db'}?mode=ro", uri=True)
    try:
        tem = cer.execute("SELECT 1 FROM sqlite_master WHERE name = 'sala_medicao'").fetchone()
        ultima = cer.execute("SELECT em FROM sala_medicao WHERE chave = 'atual'").fetchone() if tem else None
        if ultima and datetime.fromisoformat(ultima[0]) > agora - timedelta(minutes=int(parametros.get("intervalo_min", 15))):
            return [{"sala": "em dia"}]
        mods = tomllib.loads(Path(parametros.get("modulos", "config/modulos.toml")).read_text(encoding="utf-8")).get("modulo", [])
        motores = [
            {"id": Path((m.get("parametros") or {}).get("configuracao", "")).stem, "nome": "", "luz": ""}
            for m in mods
            if (m.get("parametros") or {}).get("configuracao")
        ]
        r = montar(bib, cer, Path(parametros.get("raiz", ".")), motores, agora)
    finally:
        cer.close()
        bib.close()
    texto = json.dumps(
        {k: r[k] for k in ("em", "indice_saude", "contagem", "instrumentos", "compartimentos", "detalhes", "maquina")},
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    )
    for chave in ("atual", "dia-" + r["em"][:10]):
        contexto.diario.emitir("sala.medida", "sala", {"chave": chave, "em": r["em"], "dados": texto})
    return [{"indice_saude": r["indice_saude"], "contagem": r["contagem"], "fora_da_cadencia": len(r["detalhes"]["fora_da_cadencia"])}]


def ler_sala(dados: Path) -> dict[str, Any] | None:
    """A última medição da sala gravada no Cérebro (ou None)."""
    try:
        cer = sqlite3.connect(f"file:{dados / 'cerebro.db'}?mode=ro", uri=True)
        try:
            r = cer.execute("SELECT dados FROM sala_medicao WHERE chave = 'atual'").fetchone()
        finally:
            cer.close()
        return json.loads(r[0]) if r else None
    except (sqlite3.Error, ValueError):
        return None
