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
    "regencia": ["rg_regencia", "ma_cobertura", "ma_esgotados", "dg_finalidade", "ma_memoria_etapa"],
    "coleta": ["mo_saude", "mo_sinais", "mo_cadencia", "mo_retentativa", "mo_fora_da_fila", "es_coleta"],
    "certificacao": ["ca_12", "fl_fila", "es_curadoria", "es_parcial"],
    "investigacao": ["pi_interceptador", "pi_espiao", "pi_piloto", "pi_missoes", "pi_vagas"],
    # 04/11/2026 (titular): a verificação externa e o expurgo são da etapa 5 (antes acendiam também as etapas 3 e 4)
    "externa": ["ve_para_o_chrome", "de_decisoes", "es_expurgo", "ve_bloqueadas", "ve_completas", "ve_importado", "al_externa"],
    "repositorio": ["es_abertas", "es_banco_unico", "hi_crescimento"],
    "biblioteca": ["es_livros", "es_vigilancia", "em_rankings", "hi_uso", "hi_frio", "es_orfaos"],
    "aprendizado": ["rn_auc", "rn_precisao", "rn_revocacao", "rn_brier", "rn_treino", "cm_comparacao", "cm_decisoes"],
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


# 02/11/2026 (titular): o expurgo e a pesquisa pelo Claude no Chrome só alertam acima de 50 itens ou quando o pendente
# mais antigo passa de 168 horas (1 semana)
LIMITE_CLAUDE_ITENS, LIMITE_CLAUDE_HORAS = 50, 168


def _alerta_claude(itens: int | None, idade_h: float | None) -> str:
    if itens is None:
        return "cinza"
    return "amarelo" if itens > LIMITE_CLAUDE_ITENS or (itens and idade_h is not None and idade_h > LIMITE_CLAUDE_HORAS) else "verde"


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
    # 29/10/2026: com a última execução, o resultado da última TERMINADA (o ciclo está sempre em execução, por desenho)
    terminada: dict[str, str | None] = {}
    for r in runs:
        if r.get("status") == "completed" and r["name"] not in terminada:
            terminada[r["name"]] = r.get("conclusion")
    vistos, saida = set(), []
    for r in runs:
        if r["name"] in vistos:
            continue
        vistos.add(r["name"])
        saida.append(
            {
                "nome": r["name"],
                "conclusao": r.get("conclusion"),
                "ultima_conclusao": terminada.get(r["name"]),
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
        # 06/11/2026 (parecer de teste do site, R45): sem régua (faixa), o instrumento não é verde — fica cinza, «sem régua»
        # (33 de 45 saíam verdes por padrão e nunca acenderiam); a cadência é a da publicação do painel (15 min) quando o
        # instrumento não tem a sua; «o que faz», «resultado» e «efeito» sempre preenchidos; as contagens como inteiros
        if faixa is None and estado == "verde":
            estado, motivo = "cinza", f"{motivo} · sem régua: falta a faixa do normal e do alarme"
        if isinstance(valor, float) and valor.is_integer():
            valor = int(valor)
        inst[id_] = {
            "id": id_,
            "nome": nome,
            "valor": valor,
            "estado": estado,
            "motivo": motivo,
            "faz": f"mede: {nome}",
            "resultado": motivo,
            "quando": quando,
            "idade_h": _idade_h(quando, agora),
            "cadencia_h": cadencia_h if cadencia_h is not None else 0.25,
            **({"escala": escala} if escala else {}),
            **({"faixa": faixa} if faixa else {}),
            "efeito": efeito or motivo,
        }

    # ---- os dados comuns
    reg = [m["id"] for m in motores if not str(m["id"]).startswith("piloto")]  # os pilotos são medidos à parte (Espião e Interceptador)
    ult = {m: (i, e) for m, i, e in cer.execute("SELECT motor, MAX(inicio), erro FROM execucao_motor GROUP BY motor")}
    lidos24 = [m for m in reg if (ult.get(m) or (None,))[0] and ult[m][0] >= h24]
    ok24 = [m for m in lidos24 if not ult[m][1]]
    com_erro = [m for m in reg if ult.get(m) and ult[m][1]]
    ultima_leitura = max((v[0] for v in ult.values() if v[0]), default=None)
    agenda = {r[0] for r in cer.execute("SELECT DISTINCT modulo FROM agenda")}
    # R46 (06/11/2026, parecer de teste do site): a régua única — a Sala contava as abertas também no arquivo (230 contra
    # 209 do Início) e as validadas pela estrela; agora tudo vem de eldorado/base/cartorio/regua.py
    from ..cartorio.regua import regua as _regua
    RG = _regua(bib)
    AB = ("FROM livro l JOIN livro_dados d ON d.livro_id = l.id JOIN passaporte p_ab ON p_ab.livro_id = l.id "
          "WHERE d.situacao_prazo = 'aberta' AND l.situacao NOT IN ('excluido', 'unido') AND p_ab.fase <> 'arquivo'")
    abertas = RG["abertas"]
    estrelas = Counter(RG["estrelas"])
    validadas = RG["validadas"]
    com_estrela = estrelas.get("prata", 0) + estrelas.get("ouro", 0)        # a Finalidade: as abertas com prazo e link original
    # uma única contagem no site inteiro (25/10/2026): só os livros vivos (a sala contava também os unidos e os excluídos)
    fases = Counter(
        dict(
            bib.execute(
                "SELECT p.fase, COUNT(*) FROM passaporte p JOIN livro l ON l.id = p.livro_id "
                "WHERE l.situacao NOT IN ('excluido', 'unido') GROUP BY p.fase"
            ).fetchall()
        )
    )
    # ---- 01 Regência
    n = len(reg) or 1
    cobertura = round(100 * len(lidos24) / n)
    I(
        "ma_cobertura",
        "Cobertura do dia (motores que leram em 24 h — a perda está em «Motores com sinal de perda»)",
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
      faixa={"normal": [None, 0], "alarme": [None, 5]},

    )
    fin = round(100 * com_estrela / abertas) if abertas else None
    I(
        "dg_finalidade",
        "Finalidade do sistema (abertas com prazo e link original)",
        fin,
        _faixa(fin, 60, 30),
        f"{com_estrela} de {abertas} oportunidades abertas com o prazo e o link original (estrela prata ou ouro)",
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
    # 05/11/2026 (titular): os SINAIS de perda de cada motor, além de «leu sem erro»
    from ..cerebro.sinais_motores import sinais as _sinais
    _com_sinal = []
    for _m in reg:
        _s = _sinais(cer, _m)
        if _s["luz"] in ("amarelo", "vermelho"):
            _com_sinal.append(f"{_m}: {'; '.join(_s['sinais'])[:140]}")
    I("mo_sinais", "Motores com sinal de perda (fonte pendente ou abandonada, sem novidade há 7 dias, nunca entregou)", len(_com_sinal),
      "verde" if not _com_sinal else ("vermelho" if len(_com_sinal) > n // 2 else "amarelo"),
      (f"{len(_com_sinal)} de {len(reg)} motores: " + " | ".join(_com_sinal))[:900] if _com_sinal else "nenhum motor com sinal de perda",
      ultima_leitura, [0, len(reg)], {"normal": [None, 0], "alarme": [None, n // 2]})
    fora_cad = [m for m in reg if m not in lidos24]
    I(
        "mo_cadencia",
        "Motores fora da cadência (sem leitura em 24 h)",
        len(fora_cad),
        _faixa(len(fora_cad), 0, 5, False),
        ("fora da cadência: " + ", ".join(fora_cad[:8])) if fora_cad else "todos leram dentro da cadência",
        ultima_leitura,
      faixa={"normal": [None, 0], "alarme": [None, 5]},

    )
    I(
        "mo_retentativa",
        "Motores aguardando nova tentativa (última leitura com erro)",
        len(com_erro),
        _faixa(len(com_erro), 0, 3, False),
        ("com erro na última leitura: " + ", ".join(com_erro[:8])) if com_erro else "nenhum motor com erro na última leitura",
        ultima_leitura,
      faixa={"normal": [None, 0], "alarme": [None, 3]},

    )
    fora_fila = [m for m in reg if m not in agenda]
    I(
        "mo_fora_da_fila",
        "Motores registrados fora da agenda",
        len(fora_fila),
        _faixa(len(fora_fila), 0, 3, False),
        ("fora da agenda: " + ", ".join(fora_fila[:8])) if fora_fila else "todo motor registrado está na agenda",
        iso,
      faixa={"normal": [None, 0], "alarme": [None, 3]},

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
      faixa={"regra": "verde quando há valor; atenção quando zero"},

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
      faixa={"regra": "verde quando há valor; atenção quando zero"},

    )
    # os documentos sem texto lido (01/11/2026, titular: o alerta "8.704 documentos sem texto lido"). Antes contava os
    # documentos SEM PÁGINA no banco; desde a R35 a leitura sai do banco de propósito depois de certificada, e todo documento
    # lido passava a contar (o alerta media a regra funcionando). Agora conta a LEITURA que não extraiu texto (zero páginas,
    # o registro que fica no documento): a leitura atual (o sistema novo) e os herdados do sistema anterior, separados
    lidos = "d.leitor IS NOT NULL AND d.leitor <> ''"
    herd = "d.leitor LIKE 'Eldorado0%'"
    zero = "COALESCE(d.paginas, 0) = 0"
    novos = q(bib, f"SELECT COUNT(*) FROM documento d WHERE {lidos} AND NOT ({herd})")
    novos_sem = q(bib, f"SELECT COUNT(*) FROM documento d WHERE {lidos} AND NOT ({herd}) AND {zero}")
    herd_sem = q(bib, f"SELECT COUNT(*) FROM documento d WHERE {herd} AND {zero}")
    herd_livro = q(bib, f"SELECT COUNT(DISTINCT d.id) FROM documento d JOIN certidao c ON c.documento_id = d.id JOIN livro l ON l.id = c.livro_id "
                        f"WHERE {herd} AND {zero} AND l.situacao NOT IN ('excluido', 'unido')")
    nunca = q(bib, f"SELECT COUNT(*) FROM documento d WHERE NOT ({lidos})")
    expurgados = q(bib, f"SELECT COUNT(*) FROM documento d WHERE {lidos} AND NOT {zero} AND NOT EXISTS (SELECT 1 FROM pagina p WHERE p.documento_id = d.id)")
    if novos and novos_sem / novos > 0.05:
        est_p = "vermelho"   # a leitura atual falhando
    elif novos_sem or nunca:
        est_p = "amarelo"
    else:
        est_p = "verde"
    I(
        "es_parcial",
        "Documentos sem texto lido",
        novos_sem + nunca,
        est_p,
        f"a leitura atual: {novos_sem} de {novos} documentos lidos sem texto extraído; {nunca} ainda sem leitura · "
        f"{expurgados} lidos e certificados, com a leitura já fora do banco (R35, o esperado) · os herdados do sistema anterior "
        f"vieram sem o texto: {herd_sem} (usados por {herd_livro} livro(s) ativo(s), com a certidão herdada)",
        iso,
        faixa={"regra": "falha acima de 5% dos documentos novos sem texto; atenção com algum sem texto; verde sem nenhum"},
    )
    # o último expurgo (01/11/2026, titular): o expurgo é do Claude, nunca do sistema; a Sala mostra o último e o que está
    # indicado para avaliação (os documentos sem uso, os achados sem livro e os migrados aguardando o Chrome). Nunca vermelho
    try:
        from ..cartorio.expurgo_claude import candidatos as _cand
        from ..cartorio.expurgo_claude import ultimo as _ult

        cd, ul = _cand(bib), _ult()
        I(
            "es_expurgo",
            "Último expurgo (feito pelo Claude)",
            cd["total"],
            _alerta_claude(cd["total"], _idade_h((ul or {}).get("em"), agora) if ul else None),
            (f"o último: {ul['em'][:10]} ({ul.get('motivo', '')[:80]}) · " if ul else "nenhum expurgo registrado · ")
            + f"para o Claude no Chrome validar o expurgo (R39): {cd['livros_para_expurgo']} livro(s) sem estrela na verificação externa"
            f" e {cd['migrados_no_chrome']} migrados · sem alerta: {cd.get('na_preparacao', 0)} na preparação (coordenação do Comandante), "
            f"{cd['documentos_sem_uso']} documentos e {cd['achados_sem_livro']} achados sem livro (manutenção do sistema, R36) · "
            f"alerta acima de {LIMITE_CLAUDE_ITENS} itens ou com o último expurgo há mais de {LIMITE_CLAUDE_HORAS} h",
            (ul or {}).get("em") or iso,
      faixa={"regra": "atenção acima de 50 itens ou com o mais antigo há mais de 168 h"},

        )
    except Exception:  # noqa: BLE001
        pass
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
      faixa={"regra": "verde quando há valor; falha quando zero"},

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
      faixa={"regra": "verde quando há valor; atenção quando zero"},

    )
    ext = fases.get("analise externa", 0)
    _mais_antigo = q(bib, "SELECT MIN(p.entrou_em) FROM passaporte p JOIN livro l ON l.id = p.livro_id "
                          "WHERE p.fase = 'analise externa' AND l.situacao NOT IN ('excluido', 'unido')")
    _idade_ext = _idade_h(_mais_antigo, agora) if _mais_antigo else None
    I("de_decisoes", "Livros aguardando o Claude no Chrome", ext, _alerta_claude(ext, _idade_ext),
      f"{ext} livros na análise externa" + (f"; o mais antigo há {round(_idade_ext)} h" if _idade_ext is not None else "")
      + f" — alerta acima de {LIMITE_CLAUDE_ITENS} livros ou com algum há mais de {LIMITE_CLAUDE_HORAS} h", iso,
      faixa={"regra": "atenção acima de 50 itens ou com o mais antigo há mais de 168 h"})
    # ---- 05 Verificação externa
    # 29/10/2026 (titular): o total na fila e as partes do lote do dia; verde até 50, amarelo até 200, vermelho acima
    _hoje_lote = agora.date().isoformat()
    _pasta_lotes = raiz / "verificacao" / "lotes"
    partes_dia = len(list(_pasta_lotes.glob(f"lote-{_hoje_lote}-parte-*.json"))) if _pasta_lotes.exists() else 0
    tem_dia = (_pasta_lotes / f"lote-{_hoje_lote}.json").exists() if _pasta_lotes.exists() else False
    I(
        "ve_para_o_chrome",
        "Livros na fila do Chrome (e as partes do lote do dia)",
        ext,
        _alerta_claude(ext, _idade_ext),   # 04/11/2026: a regra da titular (50 itens ou 168 h), como «aguardando o Chrome»
        f"{ext} livros na fila do Claude no Chrome · lote do dia: "
        + (f"{partes_dia} parte(s) de até 50" if partes_dia else ("1 arquivo" if tem_dia else "ainda não gerado")),
        iso,
      faixa={"regra": "atenção acima de 50 itens ou com o mais antigo há mais de 168 h"},

    )
    lotes = sorted((raiz / "verificacao" / "lotes").glob("*.json")) if (raiz / "verificacao" / "lotes").exists() else []
    importados = (
        {p.stem for p in (raiz / "verificacao" / "vereditos" / "importados").glob("*.json")}
        if (raiz / "verificacao" / "vereditos" / "importados").exists()
        else set()
    )
    sem_retorno = [p.stem for p in lotes if not any(p.stem.split("lote-")[-1] in x for x in importados)]
    # 26/10/2026: o lote só fica pendente se tiver livro que ainda espera o Chrome e que não está num lote mais novo
    # (os lotes se sobrepõem: o de cada dia repete os pendentes do anterior)
    try:
        esperam = {
            r[0]
            for r in bib.execute(
                "SELECT p.livro_id FROM passaporte p JOIN livro l ON l.id = p.livro_id "
                "WHERE p.fase = 'analise externa' AND l.situacao NOT IN ('excluido', 'unido')"
            )
        }
        conteudo = {p.stem: {x.get("livro_id") for x in json.loads(p.read_text(encoding="utf-8")).get("livros", [])} for p in lotes}
        # 29/10/2026: pelos DADOS, não pelo nome do arquivo: o livro com veredito do Chrome já teve retorno (o arquivo dos
        # remanescentes de 23 a 28/10 não tem as datas no nome, e os lotes seguiam "sem retorno" depois de importados)
        vereditados = {r[0] for r in bib.execute("SELECT DISTINCT livro_id FROM veredito WHERE origem LIKE '%chrome%' OR origem LIKE '%externa%'")}
        esperam -= vereditados
        mais_novos: set = set()
        pendentes = []
        for st in reversed([p.stem for p in lotes]):
            if (conteudo.get(st, set()) & esperam) - mais_novos:
                pendentes.append(st)
            mais_novos |= conteudo.get(st, set())
        sem_retorno = sorted(pendentes)
    except (ValueError, OSError, sqlite3.Error):
        pass
    I(
        "ve_bloqueadas",
        "Lotes sem retorno do Chrome",
        len(sem_retorno),
        _faixa(len(sem_retorno), 1, 3, False),
        ("sem retorno: " + ", ".join(sem_retorno[-5:])) if sem_retorno else "todo lote teve retorno",
        iso,
      faixa={"normal": [None, 1], "alarme": [None, 3]},

    )
    chrome = q(bib, "SELECT COUNT(*) FROM veredito WHERE origem LIKE '%chrome%' OR origem LIKE '%externa%'")
    ult_v = q(bib, "SELECT MAX(em) FROM veredito WHERE origem LIKE '%chrome%' OR origem LIKE '%externa%'")
    I("ve_completas", "Vereditos do Chrome", chrome, "verde" if chrome else "cinza", f"{chrome} vereditos importados da análise externa", ult_v,
      faixa={"regra": "verde quando há valor; sem leitura (cinza) quando zero"})
    idade_v = _idade_h(ult_v, agora)
    I(
        "ve_importado",
        "Último veredito importado (horas)",
        idade_v,
        _faixa(idade_v, 72, 168, False) if idade_v is not None else "cinza",
        "nenhum veredito importado ainda" if idade_v is None else f"último veredito há {idade_v:.0f} h",
        ult_v,
      faixa={"normal": [None, 72], "alarme": [None, 168]},

    )
    # ---- 29/10/2026 (titular): as missões do Interceptador e as vagas (a regra dos 85% do processador total)
    try:
        ms = cer.execute("SELECT valor FROM medicao WHERE marcador = 'missao:interceptador' AND em >= ?", (h24,)).fetchall()
    except sqlite3.Error:
        ms = []
    nm, it = len(ms), int(sum((r[0] or 0) for r in ms))
    vazias = sum(1 for r in ms if not r[0])
    # 01/11/2026 (titular): a causa, não só a média — o que aconteceu com cada tentativa das últimas 24 h
    causa = {"sem material": 0, "sem a vez da IA": 0, "IA com tempo estourado": 0, "IA rodou": 0, "itens pelos extratores": 0}
    try:
        for (res,) in bib.execute("SELECT resultado FROM tentativa WHERE ferramenta LIKE 'abordagem %' AND em >= ?", (h24,)):
            try:
                r = json.loads(res or "{}")
            except ValueError:
                continue
            ia_ = r.get("ia") or {}
            if r.get("sem material"):
                causa["sem material"] += 1
            elif "adiada" in ia_:
                causa["sem a vez da IA"] += 1
            elif "indisponivel" in ia_:
                causa["IA com tempo estourado"] += 1
            elif "propostas" in ia_:
                causa["IA rodou"] += 1
            causa["itens pelos extratores"] += len(ia_.get("extratores") or [])
    except sqlite3.Error:
        pass
    causas_txt = "; as tentativas: " + ", ".join(f"{k} {v}" for k, v in causa.items())
    I(
        "pi_missoes",
        "Missões do Interceptador (24 h): itens do checklist obtidos",
        it if nm else None,
        "cinza" if not nm else _faixa(it / nm, 1.5, 0.5),
        "ainda sem missão registrada"
        if not nm
        else f"{nm} missões, {it} itens do checklist obtidos (média {it / nm:.1f} por missão); {vazias} voltaram sem item{causas_txt}",
        iso,
      faixa={"normal": [1.5, None], "alarme": [0.5, None]},

    )
    try:
        vq = cer.execute("SELECT valor, motivo, em FROM medicao WHERE marcador = 'pilotos:vagas' ORDER BY em DESC LIMIT 1").fetchone()
    except sqlite3.Error:
        vq = None
    I(
        "pi_vagas",
        "Interceptadores agora (em voo / vagas liberadas)",
        vq[0] if vq else None,
        "cinza" if not vq else "verde",
        "ainda sem o quadro das vagas" if not vq else str(vq[1]),
        vq[2] if vq else iso,
      faixa={"regra": "verde quando há registro; cinza sem medida"},

    )
    # ---- 29/10/2026: os ALARMES DE TENDÊNCIA (a degradação lenta aparece antes de virar problema)
    orfaos = q(bib, "SELECT COUNT(*) FROM achado WHERE decisao = 'pendente' AND encontrado_em < ?", hoje)
    I(
        "es_orfaos",
        "Achados sem decisão de dias anteriores",
        orfaos,
        _faixa(orfaos, 0, 49, False),
        "nenhum achado órfão" if not orfaos else f"{orfaos} achado(s) sem decisão desde antes de hoje (a informação ainda não chegou ao livro)",
        iso,
      faixa={"normal": [None, 0], "alarme": [None, 49]},

    )
    ontem = (agora - timedelta(days=1)).date()
    pasta_ontem = raiz / "eventos" / f"{ontem:%Y}" / f"{ontem:%m}" / f"{ontem:%d}"
    mb_ontem = mb_paginas = None
    if pasta_ontem.exists():
        total = paginas = 0
        for f in pasta_ontem.glob("*.jsonl"):
            with open(f, "rb") as h:
                for linha in h:
                    total += len(linha)
                    if b'"tipo":"pagina.gravada"' in linha[:200]:
                        paginas += len(linha)
        mb_ontem, mb_paginas = round((total - paginas) / 1048576, 1), round(paginas / 1048576, 1)
    I(
        "hi_crescimento",
        "Crescimento da operação no histórico (MB no dia anterior, sem o texto das páginas)",
        mb_ontem,
        _faixa(mb_ontem, 40, 80, False),   # 01/11/2026 (titular): o limite maior; a telemetria foi para o Cérebro
        "sem a pasta do dia anterior"
        if mb_ontem is None
        else f"{mb_ontem} MB de operação em {ontem:%d/%m} (mais {mb_paginas} MB de texto das páginas dos livros, o dado que deve crescer)",
        iso,
      faixa={"normal": [None, 40], "alarme": [None, 80]},

    )
    try:
        mem_e = cer.execute("SELECT marcador, MAX(valor) FROM medicao WHERE marcador LIKE 'memoria:%' AND em >= ?", (h24,)).fetchone()
    except sqlite3.Error:
        mem_e = None
    mem_v = mem_e[1] if mem_e and mem_e[1] is not None else None
    I(
        "ma_memoria_etapa",
        "Memória do processo por etapa (pico em 24 h, MB)",
        mem_v,
        _faixa(mem_v, 4500, 6000, False),
        "o medidor por etapa ainda não registrou" if mem_v is None else f"pico de {mem_v:.0f} MB depois da etapa {str(mem_e[0])[8:]}",
        iso,
      faixa={"normal": [None, 4500], "alarme": [None, 6000]},

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
      faixa={"normal": [None, 48], "alarme": [None, 120]},

    )
    # ---- 06 Repositório
    I(
        "es_abertas",
        "Oportunidades abertas",
        abertas,
        "verde" if abertas else "amarelo",
        f"{abertas} oportunidades com o prazo aberto",
        iso,
        efeito=f"{validadas} validadas (no Farol) · {RG['em_verificacao']} em verificação (na esteira) · {RG['com_data']} com data-limite",
      faixa={"regra": "verde quando há valor; atenção quando zero"},

    )
    paralelos = sorted(p.relative_to(raiz).as_posix() for p in (raiz / "dados").rglob("*.db") if p.name not in ("biblioteca.db", "cerebro.db"))
    I(
        "es_banco_unico",
        "Bancos fora dos livros (paralelos)",
        len(paralelos),
        "verde" if not paralelos else "vermelho",
        ("bancos paralelos: " + ", ".join(paralelos[:6]) + ("…" if len(paralelos) > 6 else "")) if paralelos else "só a Biblioteca e o Cérebro",
        iso,
      faixa={"regra": "verde quando não há nenhum; falha quando há algum"},

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
      faixa={"regra": "verde quando há valor; atenção quando zero"},

    )
    emp = q(bib, "SELECT COUNT(*) FROM empresa") if bib.execute("SELECT 1 FROM sqlite_master WHERE name = 'empresa'").fetchone() else 0
    I("em_rankings", "Empresas na Biblioteca", emp, "verde" if emp else "cinza", f"{emp} empresas com incentivos registrados", iso,
      faixa={"regra": "verde quando há valor; sem leitura (cinza) quando zero"})
    try:
        from ..cerebro.mapa_arquivos import AGUARDAM_DECISAO
        from ..cerebro.mapa_arquivos import montar as mapa

        parados = [x["id"] for x in mapa()["nos"] if not x["alcancado"] and x["id"] in AGUARDAM_DECISAO]  # os por desenho já estão decididos
        I(
            "hi_uso",
            "Arquivos fora do funcionamento",
            len(parados),
            "verde" if not parados else "amarelo",
            "ficam por decisão da titular, com a função aguardando a migração: " + ", ".join(parados)
            if parados
            else "nenhum arquivo fora do funcionamento",
            iso,
      faixa={"regra": "verde quando não há nenhum; atenção quando há algum"},

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
            _faixa(auc, 0.85, 0.7) if auc is not None else "cinza",   # 02/11/2026: a rede de livros em uso; volta a ser medida
            f"área sob a curva ROC: {auc} — prequencial sobre LIVROS (cada livro uma vez, o veredito final do Chrome ou da titular, "
            f"ou a chegada ao Farol); a nota de cada livro pendente informa a Sala e o Comandante",
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
        I("rn_treino", "Idade do modelo (horas)", idade_t, _faixa(idade_t, 24, 72, False), f"treinado há {idade_t:.0f} h", t,
      faixa={"normal": [None, 24], "alarme": [None, 72]})
    else:
        for k, nome in (
            ("rn_auc", "Discernimento da rede"),
            ("rn_precisao", "Precisão da rede"),
            ("rn_revocacao", "Revocação da rede"),
            ("rn_treino", "Idade do modelo"),
        ):
            I(k, nome, None, "cinza", "a rede ainda não registrou um modelo treinado", None)
    try:
        b_ = cer.execute(
            "SELECT treinado_em, brier FROM modelo WHERE arquivo = 'rede:oportunidade' AND brier IS NOT NULL ORDER BY treinado_em DESC LIMIT 1"
        ).fetchone()
    except sqlite3.Error:
        b_ = None
    if b_:
        I(
            "rn_brier",
            "Erro de calibração da rede",
            b_[1],
            _faixa(b_[1], 0.15, 0.25, False),
            f"erro de Brier {b_[1]:.3f} (0 = probabilidades perfeitas; até 0,15 bem calibrada)",
            b_[0],
            [0, 0.5],
            {"normal": [None, 0.15], "alarme": [None, 0.25]},
        )
    else:
        I(
            "rn_brier",
            "Erro de calibração da rede",
            None,
            "cinza",
            "aguardando o primeiro treino com a calibração (o nó da rede, a cada passagem)",
            None,
        )
    # ---- o Comandante (a fase 2, 25/10/2026): as decisões dele, em paralelo, e o rendimento contra a ordem fixa
    try:
        from ..aprendizado.avaliar import comparacao

        cmp_ = comparacao(bib, cer)
        n24 = cer.execute("SELECT COUNT(*) FROM comandante_decisao WHERE em >= ?", (h24,)).fetchone()[0]
    except (sqlite3.Error, ImportError):
        cmp_, n24 = {"comandante": None, "ordem_fixa": None, "decisoes": 0}, None
    I(
        "cm_decisoes",
        "Decisões do Comandante em 24 h",
        n24,
        "cinza" if n24 is None else ("verde" if n24 else "amarelo"),
        "cada decisão com o motivo e a nota, registrada no Arquivo do Cérebro (em paralelo com a ordem fixa)"
        if n24 is not None
        else "o Cérebro ainda não está na versão 10",
        iso,
        None,
        {"normal": [1, None], "alarme": [0, None]},
    )
    if cmp_["comandante"] is not None and cmp_["ordem_fixa"] is not None:
        dif = round(100 * (cmp_["comandante"] - cmp_["ordem_fixa"]), 1)
        I(
            "cm_comparacao",
            "O Comandante contra a ordem fixa",
            dif,
            _faixa(dif, 0, -5),
            f"as escolhas do Comandante renderam {cmp_['comandante']:.0%} (achado aceito no dia), a ordem fixa {cmp_['ordem_fixa']:.0%} "
            f"({cmp_['decisoes']} decisões avaliadas em 7 dias)",
            iso,
            [-50, 50],
            {"normal": [0, None], "alarme": [-5, None]},
        )
    else:
        I(
            "cm_comparacao",
            "O Comandante contra a ordem fixa",
            None,
            "cinza",
            "aguardando as primeiras decisões avaliadas (o Aprendizado avalia no dia seguinte)",
            None,
        )
    # ---- 09 Farol
    I("es_validadas", "Validadas (abertas no Farol)", validadas, "verde",
      f"{validadas} abertas no Farol (R46); {RG['farol_total']} livros no Farol ao todo, com os de prazo vencido", iso)
    transf = q(bib, "SELECT COUNT(DISTINCT livro_id) FROM transferencia")
    I(
        "es_fichas",
        "Livros transferidos ao Farol",
        transf,
        "verde" if transf else "amarelo",
        f"{transf} livros no formato estável (eldorado.livro/1)",
        q(bib, "SELECT MAX(em) FROM transferencia"),
      faixa={"regra": "verde quando há valor; atenção quando zero"},

    )
    # ---- os compartimentos e a Regência
    comp_ = []
    for et, ids in ETAPAS.items():
        if et == "regencia":
            continue
        est = min((inst[i]["estado"] for i in ids if i in inst), key=lambda k: ORDEM[k], default="cinza")
        # 30/10/2026: a etapa em alerta diz o MOTIVO (os indicadores que o causam)
        mot = "; ".join(f"{inst[i]['nome']}: {inst[i]['motivo']}" for i in ids if i in inst and inst[i]["estado"] in ("amarelo", "vermelho"))
        comp_.append({"id": et, "estado": est, "motivo": mot})
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
    comp_.insert(
        0,
        {
            "id": "regencia",
            "estado": est_reg,
            "motivo": "; ".join(
                f"{inst[i]['nome']}: {inst[i]['motivo']}" for i in ETAPAS["regencia"] if inst[i]["estado"] in ("amarelo", "vermelho")
            ),
        },
    )
    luz = {"verde": "verde", "vermelho": "vermelho", "amarelo": "amarelo"}
    for c in comp_:
        if c["id"] == "coleta":
            c["estrelas"] = [_estrela(x, luz, cer, agora) for x in motores]
    contagem = Counter(i["estado"] for i in inst.values())
    medidos = sum(contagem[k] for k in ("verde", "amarelo", "vermelho"))
    indice = round(100 * (contagem["verde"] + 0.5 * contagem["amarelo"]) / medidos) if medidos else 0
    # ---- o caminho do dado
    criados = q(bib, "SELECT COUNT(*) FROM livro WHERE criado_em >= ?", h24)
    # 06/11/2026 (parecer): cada caixa diz a sua janela — a coleta e os livros novos são das últimas 24 h; o resto é o
    # estoque de agora, pela régua única (antes «Distintas» de 24 h ficava ao lado do estoque, e «Cartório» era só a preparação)
    mimico = [
        {"etapa": "Coleta (24 h)", "valor": col, "janela": "24 h"},
        {"etapa": "Livros novos (24 h)", "valor": criados, "janela": "24 h"},
        {"etapa": "Abertas (agora)", "valor": abertas, "janela": "agora"},
        {"etapa": "Livros vivos (agora)", "valor": livros, "janela": "agora"},
        {"etapa": "Esteira do Cartório (agora)", "valor": RG["esteira"], "janela": "agora"},
        {"etapa": "Fila do Interceptador (agora)", "valor": fila_i, "janela": "agora"},
        {"etapa": "Verificação externa (agora)", "valor": ext, "janela": "agora"},
        {"etapa": "Validadas no Farol (agora)", "valor": validadas, "janela": "agora"},
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
    # 27/10/2026: a linha do tempo com o que o sistema de fato fez (a tabela das execuções de workflow quase não é preenchida
    # pela passagem permanente): as etapas e as passagens, as decisões do Comandante, os voos dos pilotos
    linha = [
        {"em": r[1], "evento": f"{r[0]}: {r[2]}"} for r in cer.execute("SELECT workflow, inicio, estado FROM execucao ORDER BY inicio DESC LIMIT 30")
    ]
    try:
        for mk, em, mo in cer.execute(
            "SELECT marcador, em, motivo FROM medicao WHERE marcador IN ('passagem', 'piloto:espiao', 'piloto:interceptador') "
            "AND (marcador = 'passagem' OR motivo LIKE 'em voo%' OR motivo LIKE 'pousou%') ORDER BY em DESC LIMIT 80"
        ):
            quem = {"passagem": "Passagem", "piloto:espiao": "Espião", "piloto:interceptador": "Interceptador"}[mk]
            linha.append({"em": em, "evento": f"{quem}: {mo}"})
        tabs = {r[0] for r in cer.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
        if "comandante_decisao" in tabs:
            cols = {r[1] for r in cer.execute("PRAGMA table_info(comandante_decisao)")}
            alvo = "alvo" if "alvo" in cols else "NULL"
            for em, etapa, acao, a_ in cer.execute(f"SELECT em, etapa, acao, {alvo} FROM comandante_decisao ORDER BY em DESC LIMIT 40"):
                linha.append({"em": em, "evento": f"Comandante · {etapa}: {acao}{(' — ' + str(a_)[:60]) if a_ else ''}"})
    except sqlite3.Error:
        pass
    linha = sorted(linha, key=lambda x: str(x["em"] or ""), reverse=True)[:60]
    hist: dict[str, Counter] = defaultdict(Counter)
    for d, e in cer.execute("SELECT substr(inicio, 1, 10), estado FROM execucao WHERE inicio >= ?", ((agora - timedelta(days=14)).isoformat(),)):
        hist[d]["concluidas" if e == "concluida" else "falhas" if e == "falhou" else "outras"] += 1
    detalhes = {
        "fora_da_cadencia": fora_cad,
        "com_erro": com_erro,
        "maestro": _maestro(cer, reg, lidos24, agora),
        "interceptador_missoes": _missoes_interceptador(cer),
        "espiao_familias": _familias_espiao(cer),
        "reprocessar": _reprocessar(bib, cer, hoje),
        "estantes": {k: estrelas.get(k, 0) for k in ("ouro", "prata", "bronze", "sem")},
        "por_etapa": dict(fases),
        "por_origem": dict(bib.execute(f"SELECT COALESCE(d.origem, 'sem'), COUNT(*) {AB} GROUP BY 1").fetchall()),
        "interceptador_fila": {"abertos com itens em falta": fila_i},
        "cartorio_itens": _eficiencia_itens(bib, AB),
        "proximo_passo": _proximo_passo(bib, AB),
        "rede_entregou": _rede_entregou(bib, cer, AB),
        "comparacao_r01": _comparacao_r01(cer, agora),
        "escada": _escada_em_uso(cer, h48),
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
            try:   # 04/11/2026: os processos que mais ocupam a memória (a última leitura que os trouxe)
                pr = cer.execute("SELECT processos FROM maquina WHERE processos IS NOT NULL ORDER BY em DESC LIMIT 1").fetchone()
                maq["processos"] = json.loads(pr[0]) if pr and pr[0] else []
            except (sqlite3.Error, ValueError):
                maq["processos"] = []
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
                [None, 85],  # a titular (25/10/2026): verde até 85%, laranja de 86% a 90%,
                [None, 90],  # vermelho de 91% a 100%
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


def _estrela(x: dict[str, Any], luz: dict[str, str], cer: sqlite3.Connection, agora: datetime) -> dict[str, Any]:
    """30/10/2026 (titular, pedida 5 vezes): a estrela do PILOTO pela atividade dele (o sinal 'em voo' nas últimas 2 h), não
    pelo registro de execução dos motores, onde os pilotos nunca escrevem ('construído; ainda sem execução registrada')."""
    nome = str(x.get("nome") or "")
    if nome.lower().startswith("piloto"):
        marc = "piloto:espiao" if "espi" in nome.lower() else "piloto:interceptador"
        try:
            r = cer.execute("SELECT em, motivo FROM medicao WHERE marcador = ? ORDER BY em DESC LIMIT 1", (marc,)).fetchone()
        except sqlite3.Error:
            r = None
        idade = _idade_h(r[0], agora) if r else None
        if r and idade is not None and idade <= 2:
            return {"nome": nome, "estado": "verde", "resultado": f"em atividade: {str(r[1])[:120]} (há {idade * 60:.0f} min)"}
        return {
            "nome": nome,
            "estado": "amarelo" if r else "cinza",
            "resultado": f"último sinal há {idade:.0f} h" if r and idade is not None else "sem sinal de voo",
        }
    return {"nome": nome, "estado": luz.get(x.get("luz"), "cinza"), "resultado": x.get("resultado")}


def _maestro(cer: sqlite3.Connection, reg, lidos24, agora: datetime) -> list[dict[str, Any]]:
    """30/10/2026: o plano do maestro com os campos que a página lê (o motor, a cobertura e as tentativas do dia)."""
    try:
        tent = dict(cer.execute("SELECT motor, COUNT(*) FROM execucao_motor WHERE inicio >= ? GROUP BY 1", (agora.date().isoformat(),)).fetchall())
    except sqlite3.Error:
        tent = {}
    return [{"id": m_, "motor": m_, "cobertura": "completa" if m_ in lidos24 else "pendente", "tentativas": tent.get(m_, 0)} for m_ in reg]


def _missoes_interceptador(cer: sqlite3.Connection, n: int = 30) -> list[dict[str, Any]]:
    """30/10/2026: as últimas missões do Interceptador, com os itens do checklist obtidos (a métrica de cada missão)."""
    import re as _re

    out = []
    try:
        for em, valor, mot in cer.execute(
            "SELECT em, valor, motivo FROM medicao WHERE marcador = 'missao:interceptador' ORDER BY em DESC LIMIT ?", (n,)
        ):
            partes = str(mot).split(" · ")
            m = _re.match(r"\d+ de \d+", str(mot))
            out.append(
                {
                    "em": em,
                    "alvo": partes[-1] if len(partes) > 2 else str(mot)[:80],
                    "modo": (m.group(0) + " itens") if m else "",
                    "resultado": str(mot)[:200],
                    "itens": valor,
                }
            )
    except sqlite3.Error:
        pass
    return out


def _familias_espiao(cer: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    """30/10/2026: as famílias de busca do Espião (os voos e os achados de cada uma)."""
    try:
        return {n: {"usos": u or 0, "achados": a or 0, "empresas": 0} for n, u, a in cer.execute("SELECT nome, usos, achados FROM espiao_familia")}
    except sqlite3.Error:
        return {}


def _reprocessar(bib: sqlite3.Connection, cer: sqlite3.Connection, hoje: str) -> dict[str, int]:
    """30/10/2026: a fila de reprocessamento (o que volta a ser trabalhado)."""
    out: dict[str, int] = {}
    consultas = [
        (
            "livros de volta à análise externa (já com veredito, faltam itens)",
            bib,
            "SELECT COUNT(DISTINCT p.livro_id) FROM passaporte p JOIN veredito v ON v.livro_id = p.livro_id JOIN livro l ON l.id = p.livro_id "
            "WHERE p.fase = 'analise externa' AND l.situacao NOT IN ('excluido', 'unido')",
            (),
        ),
        ("achados sem decisão de dias anteriores", bib, "SELECT COUNT(*) FROM achado WHERE decisao = 'pendente' AND encontrado_em < ?", (hoje,)),
        (
            "livros esperando o Chrome",
            bib,
            "SELECT COUNT(*) FROM passaporte p JOIN livro l ON l.id = p.livro_id WHERE p.fase = 'analise externa' AND l.situacao NOT IN ('excluido', 'unido')",
            (),
        ),
        ("documentos herdados ainda para reler", cer, "SELECT COUNT(*) FROM releitura WHERE COALESCE(resultado, '') NOT LIKE 'relido%' AND tentativas < 3", ()),
    ]
    for nome, con, sql, par in consultas:
        try:
            out[nome] = int(con.execute(sql, par).fetchone()[0] or 0)
        except sqlite3.Error:
            continue
    return out


def _comparacao_r01(cer: sqlite3.Connection, agora: datetime, caminho: str = "config/comparacao.toml") -> dict[str, Any]:
    """29/10/2026 (a regra R01, config/comparacao.toml): cada motor novo contra os de origem no Eldorado0, pela média de
    achados por execução (o novo desde o início da comparação; a origem, o histórico migrado antes dele). Antes nenhum
    código lia o arquivo: a comparação nunca acontecia."""
    import tomllib

    try:
        cfg = tomllib.loads(Path(caminho).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"erro": "sem o arquivo da comparação"}
    inicio, dias = str(cfg.get("inicio", "2026-10-23")), int(cfg.get("dias", 14))
    minimo = int(cfg.get("minimo_dias_origem", 3))
    dia = max(0, (agora.date() - datetime.fromisoformat(inicio).date()).days)

    def media(motores: list[str], depois: bool) -> tuple[float | None, int]:
        """02/11/2026: achados por DIA com execução (o novo roda várias vezes ao dia; o Eldorado0 rodava uma) e os dias."""
        if not motores:
            return None, 0
        ph = ",".join("?" * len(motores))
        cond = "inicio >= ?" if depois else "inicio < ?"
        rows = cer.execute(
            f"SELECT substr(inicio, 1, 10), COALESCE(SUM(achados), 0) FROM execucao_motor WHERE motor IN ({ph}) AND {cond} "
            "GROUP BY substr(inicio, 1, 10)", [*motores, inicio]).fetchall()
        return (round(sum(r[1] for r in rows) / len(rows), 2) if rows else None), len(rows)

    try:  # os nomes antigos (no histórico migrado) de cada motor novo: os apelidos do sistema
        from ...motores.canal.motor import apelidos

        antigos: dict[str, set[str]] = {}
        for velho, atual in apelidos().items():
            antigos.setdefault(atual, set()).add(velho)
    except Exception:  # noqa: BLE001 — sem os apelidos, só os nomes do arquivo
        antigos = {}
    out = {}
    for novo, origem in (cfg.get("motores") or {}).items():
        mn, nn = media([novo], True)
        nomes = set(origem) | {v for o in [novo, *origem] for v in antigos.get(o, set())} if origem else set()
        mo, no = media(sorted(nomes), False)
        if mn is None or mo is None:
            sit = "sem dados" if origem else "sem comparação (a origem não existe)"
        elif no < minimo:
            sit = f"sem base de comparação (a origem migrada tem {no} dia(s); mínimo {minimo})"
        else:
            sit = "igual ou melhor" if mn >= mo else "pior"
        out[novo] = {"novo_por_dia": mn, "dias_novo": nn, "origem_por_dia": mo, "dias_origem": no, "situacao": sit}
    piores = [k for k, v in out.items() if v["situacao"] == "pior"]
    return {
        "dia": min(dia, dias),
        "dias": dias,
        "termina": (datetime.fromisoformat(inicio) + timedelta(days=dias)).date().isoformat(),
        "motores": out,
        "piores": piores,
    }


def _escada_em_uso(cer: sqlite3.Connection, desde: str) -> dict[str, int]:
    """29/10/2026: os degraus da escada de acesso em uso: quantos sites precisam de cada um (o que a escada aprendeu) e o
    degrau mais alto de cada execução de motor nas últimas 48 h (a resposta a "o Camoufox está sendo usado?")."""
    # os nomes locais (a publicação do painel instala só o básico: importar a escada puxaria o tenacity e quebrava o site)
    NOMES_CANONICOS = {
        1: "API",
        2: "requisição leve",
        10: "ponte BR",
        3: "Lightpanda",
        4: "Patchright",
        5: "Camoufox",
        6: "Wayback",
        7: "Tor",
        8: "leitor público",
        9: "computador da titular",
    }
    out: dict[str, int] = {}
    try:
        for cod, n in cer.execute("SELECT degrau_que_funciona, COUNT(*) FROM dominio GROUP BY 1"):
            out["sites que exigem o computador da titular" if cod is None else f"sites que abrem no {NOMES_CANONICOS.get(cod, cod)}"] = n
        for cod, n in cer.execute(
            "SELECT degrau_maximo, COUNT(*) FROM execucao_motor WHERE inicio >= ? AND degrau_maximo IS NOT NULL GROUP BY 1", (desde,)
        ):
            out[f"execuções que subiram até o {NOMES_CANONICOS.get(cod, cod)}"] = n
        sem = cer.execute("SELECT COUNT(*) FROM execucao_motor WHERE inicio >= ? AND degrau_maximo IS NULL", (desde,)).fetchone()[0]
        if sem:
            out["execuções sem o registro do degrau"] = sem
    except sqlite3.Error:
        pass
    return out


def _eficiencia_itens(bib: sqlite3.Connection, AB: str) -> dict[str, dict[str, Any]]:
    """29/10/2026: a eficiência de cada um dos 12 itens nas abertas (a página lê eficiência, obtidos, dispensados e
    faltavam; antes ia só a contagem e a Sala mostrava 0%)."""
    total = bib.execute(f"SELECT COUNT(*) {AB}").fetchone()[0] or 0
    con = Counter()
    dis = Counter()
    for item, sit, n in bib.execute(
        f"SELECT c.item, c.situacao, COUNT(DISTINCT c.livro_id) FROM certidao c WHERE c.situacao IN ('comprovado', 'dispensado') "
        f"AND c.livro_id IN (SELECT l.id {AB}) GROUP BY 1, 2"
    ):
        (con if sit == "comprovado" else dis)[item] += n
    out = {}
    for item in sorted(set(con) | set(dis)):
        ob, di = con[item], dis[item]
        out[item] = {
            "obtidos": ob,
            "dispensados": di,
            "faltavam": max(0, total - ob - di),
            "total": total,
            "eficiencia": round((ob + di) / total, 4) if total else 0,
        }
    return out


def _proximo_passo(bib: sqlite3.Connection, AB: str) -> dict[str, int]:
    """29/10/2026: o próximo passo de cada inscrição aberta, contado pelos dados (antes vinha de um molde, todo em zero)."""
    de = "FROM livro l JOIN livro_dados d ON d.livro_id = l.id"
    junta = AB.replace(de, de + " JOIN passaporte p ON p.livro_id = l.id")
    cols = {r[1] for r in bib.execute("PRAGMA table_info(livro_dados)")}
    buscar = "d.base_buscar" if "base_buscar" in cols else "''"
    base = f"SELECT l.id, l.estrela, l.link_oficial, d.validacao, {buscar} AS base_buscar, p.fase {junta}"

    def n(cond: str) -> int:
        try:
            return bib.execute(f"SELECT COUNT(*) FROM ({base}) x WHERE {cond}").fetchone()[0]
        except sqlite3.Error:
            return 0

    return {
        "Interceptador: completar os itens": n("x.fase IN ('recepcao', 'preparacao') AND COALESCE(x.estrela, 'sem') <> 'ouro'"),
        "Interceptador: achar o site oficial": n("COALESCE(x.link_oficial, '') = '' OR x.base_buscar LIKE '%site oficial%'"),
        "Chrome: análise externa": n("x.fase = 'analise externa'"),
        "Validação manual pela titular": n("x.validacao = 'revisar'"),
        "Farol: enquadrar": n("x.fase = 'farol'"),
        "Acompanhar o prazo (completas)": n("COALESCE(x.estrela, 'sem') = 'ouro' AND x.fase <> 'farol'"),
    }


def _rede_entregou(bib: sqlite3.Connection, cer: sqlite3.Connection, AB: str) -> dict[str, Any]:
    """29/10/2026: o que a rede de pertinência entregou: as notas dadas aos pendentes (a análise da rede) e as decisões
    usadas no último treino."""
    try:
        m = cer.execute("SELECT versao, treinado_em FROM modelo WHERE arquivo = 'rede:oportunidade' ORDER BY treinado_em DESC LIMIT 1").fetchone()
    except sqlite3.Error:
        m = None
    decisoes = None
    if m:
        partes = str(m[0]).split("-")
        decisoes = int(partes[1]) if len(partes) > 1 and partes[1].isdigit() else None
    try:
        notas = bib.execute(
            "SELECT COUNT(DISTINCT livro_id), SUM(nota >= 0.5) FROM (SELECT livro_id, nota FROM analise_rede "
            "WHERE id IN (SELECT MAX(id) FROM analise_rede GROUP BY livro_id))"
        ).fetchone()
    except sqlite3.Error:
        notas = (0, 0)
    return {
        "pendentes_avaliados": notas[0] or 0,
        "pendentes_provaveis_reais": notas[1] or 0,
        "decisoes_no_treino": decisoes,
        "treinado_em": m[1] if m else None,
        "aviso": "a rede julga os livros pendentes (retreinada só com livros em 02/11/2026); a nota informa, não decide",
    }


def _motores_com_luz(mods: list[dict[str, Any]], cer: sqlite3.Connection, agora: datetime) -> list[dict[str, Any]]:
    """29/10/2026: as estrelas da Coleta na medição da produção: o nome do motor e a luz pela última leitura registrada
    (verde: leu nas últimas 26 h sem erro; amarelo: leu com erro ou faz mais de 26 h; vermelho: falhou; cinza: nunca leu).
    Antes iam com o nome e o estado vazios, e a Regência via todas as estrelas cinzentas."""
    out = []
    for m in mods:
        cfg = (m.get("parametros") or {}).get("configuracao")
        if not cfg:
            continue
        mid = Path(cfg).stem
        try:
            r = cer.execute("SELECT ponto, motivo, em FROM medicao WHERE marcador = ? ORDER BY em DESC LIMIT 1", (mid,)).fetchone()
        except sqlite3.Error:
            r = None
        if not r:
            luz, res = "cinza", "sem leitura registrada"
        else:
            idade = _idade_h(r[2], agora)
            motivo = str(r[1] or "")
            luz = {"r": "vermelho", "a": "amarelo"}.get(str(r[0]), "amarelo" if (idade or 99) > 26 else "verde")
            res = motivo[:160]
        out.append({"id": mid, "nome": m.get("nome") or mid, "luz": luz, "resultado": res})
    return out


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
        motores = _motores_com_luz(mods, cer, agora)
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
