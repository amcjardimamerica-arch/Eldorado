"""A SALA DE CONTROLE DA PRODUÇÃO (titular, 10/11/2026 — R53).

«A sala de controle deve ser a do próprio sistema, que roda tudo, e não uma imagem ou dados que não sejam os do próprio
sistema funcionando; nenhum espelho ou réplica deve ser medido. A sala de controle deve ser atualizada a cada 15 minutos
no máximo.»

Antes, o fluxo Painel remontava uma CÓPIA dos bancos a partir do repositório (2,4 milhões de eventos reaplicados a cada
publicação) e media a Sala e o mapa dos arquivos nessa cópia: um evento que só a cópia recusava acendia vermelho na Sala, e a
Sala mostrava o estado da cópia, não o da produção. Agora:

  1. a PRODUÇÃO (o «eldorado permanente», que roda as passagens e os pilotos) mede a Sala nos seus próprios bancos num
     relógio próprio, a cada 5 minutos (o limite da titular é 15), e o mapa dos arquivos a cada 15 — independente da
     duração da passagem;
  2. grava a medição em painel_vivo/ (sala_controle.json e mapa_arquivos.json), com a origem: a execução, o ciclo, a hora;
  3. a gravação envia ao repositório e aciona a publicação do painel (scripts/gravar.sh);
  4. o Painel publica a medição COMO ESTÁ, sem recalcular nada (eldorado/base/painel/dados.py, publicar); sem medição da
     produção, a Sala diz isso — nunca troca por outra fonte.

Cada medição traz também «o que mudou» desde a anterior (os instrumentos que mudaram de cor, os alarmes abertos e
fechados), para a titular ver a melhoria acontecer.
"""
from __future__ import annotations

import json
import os
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

PASTA = "painel_vivo"
INTERVALO_MAX_MIN = 15      # R53: a titular — no máximo a cada 15 minutos
INTERVALO_MIN = 5           # o relógio da produção: a Sala a cada 5 minutos (mede em ~7 s; R09: a sala no menor tempo possível)
MAPA_A_CADA = 3             # o mapa dos arquivos a cada 3 medições da Sala (15 min): é o arquivo grande (≈270 kB)
ATRASO_ATENCAO_MIN = 30     # a página avisa a medição velha (medida + gravada + publicada passa de 15 min por pouco)
ATRASO_ALARME_MIN = 60
ARQ_SALA, ARQ_MAPA = "sala_controle.json", "mapa_arquivos.json"


def _agora() -> datetime:
    return datetime.now(timezone.utc)


def _mapa(raiz: Path, cer: sqlite3.Connection) -> dict[str, Any]:
    """O mapa REAL dos arquivos, medido AGORA nos bancos da produção."""
    from ..cerebro.mapa_arquivos import finalidade, medir
    from ..cerebro.mapa_arquivos import montar as montar_mapa

    m = montar_mapa()
    med = medir(raiz / "dados", m)
    for n in m["nos"]:
        n["f"] = finalidade(n["id"])
        n.update(med["arquivos"].get(n["id"], {"p": "c", "c": "c", "m": "sem medição"}))
    proprias = [n["id"] for n in m["nos"] if n.get("c") in ("a", "r") and not n.get("h")]
    return {"gerado_em": med["em"], "medido_em": med["em"], "nos": m["nos"], "arestas": m["arestas"], "linhas": med.get("linhas", {}),
            "causas": {"proprias": len(proprias), "herdadas": sum(1 for n in m["nos"] if n.get("h")), "lista_proprias": proprias[:60]}}


def montar(raiz: Path = Path("."), com_mapa: bool = True) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """A Sala (o mesmo conteúdo que o site publicava) e o mapa dos arquivos, medidos nos bancos desta máquina."""
    from .dados import Sistema, _molde, _motores
    from .pilotos import montar as pilotos_montar
    from .sala import montar as sala_montar

    sis = Sistema(raiz)
    try:
        _status, _descricao, sala = _motores(sis)
        sc = _molde(ARQ_SALA)
        sc["detalhes"].update(sala)
        medido = sala_montar(sis.bib, sis.cer, raiz, sc["detalhes"].get("motores") or [])
        detalhes = {**sc["detalhes"], **medido.pop("detalhes")}
        sc.update(medido)
        sc["detalhes"] = detalhes
        _arq, status_pilotos = pilotos_montar(sis.bib, sis.cer, _molde)
        for st in status_pilotos.values():
            st["ultima_leitura"] = st.get("ultima")
        for m in sc["detalhes"].get("motores") or []:
            if m.get("id") in status_pilotos:
                m.update(status_pilotos[m["id"]])
        mapa = _mapa(raiz, sis.cer) if com_mapa else None
    finally:
        for c in (sis.bib, sis.cer, sis.esp):
            if c is not None:
                c.close()
    return sc, mapa


def _estados(sc: dict | None) -> dict[str, tuple[str, str, Any]]:
    return {i["id"]: (i.get("nome") or i["id"], i.get("estado") or "cinza", i.get("valor")) for i in (sc or {}).get("instrumentos") or []}


def _alarmes(sc: dict | None) -> dict[str, str]:
    return {a["id"]: a.get("nome") or a["id"] for a in (sc or {}).get("anunciadores") or [] if a.get("id")}


ORDEM = {"vermelho": 0, "amarelo": 1, "cinza": 2, "verde": 3}


def mudancas(anterior: dict | None, atual: dict) -> dict[str, Any]:
    """O que mudou desde a medição anterior: os instrumentos que mudaram de cor (melhoraram ou pioraram), os alarmes
    acesos e apagados e o índice de saúde."""
    if not anterior:
        return {"desde": None, "resumo": "primeira medição da Sala pela produção", "melhoraram": [], "pioraram": [],
                "alarmes_apagados": 0, "alarmes_acesos": 0, "indice": [None, atual.get("indice_saude")]}
    ea, eb = _estados(anterior), _estados(atual)
    melhor, pior = [], []
    for k, (nome, est, val) in eb.items():
        if k not in ea or ea[k][1] == est:
            continue
        item = {"id": k, "nome": nome, "antes": ea[k][1], "agora": est, "valor_antes": ea[k][2], "valor": val}
        (melhor if ORDEM.get(est, 2) > ORDEM.get(ea[k][1], 2) else pior).append(item)
    aa, ab = _alarmes(anterior), _alarmes(atual)
    apagados, acesos = [aa[k] for k in aa if k not in ab], [ab[k] for k in ab if k not in aa]
    i0, i1 = anterior.get("indice_saude"), atual.get("indice_saude")
    partes = []
    if i0 is not None and i1 is not None and i0 != i1:
        partes.append(f"índice de saúde {i0} → {i1}")
    if melhor:
        partes.append(f"{len(melhor)} instrumento(s) melhoraram")
    if pior:
        partes.append(f"{len(pior)} pioraram")
    if apagados:
        partes.append(f"{len(apagados)} alarme(s) apagado(s)")
    if acesos:
        partes.append(f"{len(acesos)} aceso(s)")
    return {"desde": anterior.get("em"), "resumo": "; ".join(partes) or "sem mudança de estado desde a medição anterior",
            "melhoraram": melhor[:20], "pioraram": pior[:20], "alarmes_apagados": len(apagados), "alarmes_acesos": len(acesos),
            "apagados": apagados[:10], "acesos": acesos[:10], "indice": [i0, i1]}


def ler(raiz: Path = Path(".")) -> dict[str, Any] | None:
    """A última medição da produção gravada em painel_vivo/ (ou None)."""
    pasta = Path(raiz) / PASTA
    try:
        sala = json.loads((pasta / ARQ_SALA).read_text(encoding="utf-8"))
        mapa = json.loads((pasta / ARQ_MAPA).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if (sala.get("fonte") or {}).get("origem") != "produção" or (mapa.get("fonte") or {}).get("origem") != "produção":
        return None
    return {"sala": sala, "mapa": mapa}


def _gravar(caminho: Path, dados: dict) -> None:
    tmp = caminho.with_suffix(".tmp")
    tmp.write_text(json.dumps(dados, ensure_ascii=False, separators=(",", ":"), default=str), encoding="utf-8")
    os.replace(tmp, caminho)                    # atômico: a gravação nunca leva um arquivo pela metade


def medir_e_gravar(raiz: Path = Path("."), ciclo: int | None = None, diario=None, com_mapa: bool = True) -> dict[str, Any]:
    """A produção mede a Sala (e, a cada 15 minutos, o mapa) nos próprios bancos e grava em painel_vivo/ (R53)."""
    raiz = Path(raiz)
    t0 = time.monotonic()
    anterior = ler(raiz)
    if anterior is None or not (raiz / PASTA / ARQ_MAPA).exists():
        com_mapa = True                                   # a primeira medição leva o mapa junto
    sc, mapa = montar(raiz, com_mapa)
    agora = _agora()
    fonte = {
        "origem": "produção",
        "como": "medida pelo próprio sistema em funcionamento (o eldorado permanente), nos bancos que ele usa",
        "medido_em": sc.get("em") or agora.isoformat(timespec="seconds"),
        "execucao": os.environ.get("GITHUB_RUN_ID"),
        "tentativa": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "ciclo": ciclo,
        "intervalo_min": INTERVALO_MIN,
        "intervalo_max_min": INTERVALO_MAX_MIN,
        "mapa_medido": mapa is not None,
        "proxima_ate": (agora + timedelta(minutes=INTERVALO_MIN)).isoformat(timespec="seconds"),
        "duracao_s": round(time.monotonic() - t0, 1),
    }
    sc["fonte"] = fonte
    sc["mudancas"] = mudancas((anterior or {}).get("sala"), sc)
    pasta = raiz / PASTA
    pasta.mkdir(exist_ok=True)
    _gravar(pasta / ARQ_SALA, sc)
    if mapa is not None:
        mapa["fonte"] = dict(fonte)
        _gravar(pasta / ARQ_MAPA, mapa)
    if diario is not None:
        try:   # a mesma medição no Cérebro (a Regência e a releitura agem pelo que a Sala mostra, R20)
            texto = json.dumps({k: sc.get(k) for k in ("em", "indice_saude", "contagem", "instrumentos", "compartimentos", "detalhes", "maquina")},
                               ensure_ascii=False, separators=(",", ":"), default=str)
            for chave in ("atual", "dia-" + str(sc.get("em") or agora.isoformat())[:10]):
                diario.emitir("sala.medida", "sala", {"chave": chave, "em": sc.get("em") or agora.isoformat(timespec="seconds"), "dados": texto})
        except Exception:  # noqa: BLE001 — a medição publicada não depende do registro no Cérebro
            pass
    return {"indice_saude": sc.get("indice_saude"), "contagem": sc.get("contagem"), "mudancas": sc["mudancas"]["resumo"],
            "duracao_s": fonte["duracao_s"], "arquivos": [str(pasta / ARQ_SALA), str(pasta / ARQ_MAPA)]}


def aguardando(motivo: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Sem medição da produção: a Sala diz isso, cinza, sem nenhum número de outra fonte (R53)."""
    from .dados import _molde

    agora = _agora().isoformat(timespec="seconds")
    sc = _molde(ARQ_SALA)
    sc.update({"em": None, "gerado_em": agora, "indice_saude": None, "contagem": {"verde": 0, "amarelo": 0, "vermelho": 0, "cinza": 0},
               "fonte": {"origem": "aguardando a produção", "motivo": motivo}})
    mapa = {"gerado_em": agora, "medido_em": None, "nos": [], "arestas": [], "linhas": {},
            "fonte": {"origem": "aguardando a produção", "motivo": motivo}}
    return sc, mapa


def publicar(raiz: Path = Path("."), agora: datetime | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    """O que o site publica: a medição da produção, como está, com a idade dela na hora da publicação (R53)."""
    agora = agora or _agora()
    viva = ler(raiz)
    if viva is None:
        return aguardando("a produção ainda não gravou a medição da Sala (painel_vivo/); ela mede a cada 15 minutos no máximo")
    sc, mapa = viva["sala"], viva["mapa"]
    try:
        medido = datetime.fromisoformat(str(sc["fonte"]["medido_em"]).replace("Z", "+00:00"))
        idade = round((agora - medido).total_seconds() / 60, 1)
    except (KeyError, ValueError, TypeError):
        idade = None
    est = "verde" if idade is not None and idade <= ATRASO_ATENCAO_MIN else "amarelo" if idade is not None and idade <= ATRASO_ALARME_MIN else "vermelho"
    for x in (sc, mapa):
        x["fonte"].update({"publicado_em": agora.isoformat(timespec="seconds"), "idade_min_na_publicacao": idade, "estado_idade": est})
    return sc, mapa
