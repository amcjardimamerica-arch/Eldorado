"""N-02 (manutenção de 25/11/2026; titular autorizou a regravação única em 25/11/2026): a certidão apontava para o
documento pelo NÚMERO do banco (documento_id, sequencial), uma chave que só vale num banco.

Desde a guarda dos bancos (C-01 de 23/11) a produção não é mais remontada dos eventos: a numeração da produção e a de
qualquer remontagem divergem. Numa remontagem, 1.214 certidões de 24 e 25/11 apontavam para um documento que não existe
(recusadas) e 754 para um documento que existe mas pode ser outro.

Daqui para frente os emissores gravam a assinatura (documento_sha256), que é a mesma em qualquer banco. Para as certidões
já gravadas com o número, a correção é uma TABELA DE TRADUÇÃO (o «upcasting» dos eventos): o comando
`eldorado corrigir-certidoes`, rodado na produção, grava em correcoes/certidoes_sha256.json, para cada evento afetado,
a assinatura do documento que a produção tem para aquele número. O gravador lê a tabela e aplica o evento pela
assinatura. Na produção nada muda (o evento já foi aplicado, com o documento certo); numa remontagem, a certidão
passa a apontar para o mesmo documento da produção. Nenhum evento é reescrito, nenhuma certidão é duplicada (R35).
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ARQUIVO = Path("correcoes/certidoes_sha256.json")
DESDE_PADRAO = "2026-11-23"          # a guarda dos bancos (C-01): antes dela a numeração da produção era reproduzível
CONCLUIR_DEPOIS_H = 24               # 24 h sem certidão nova com o número: a correção dos emissores já está em produção

_cache: dict[str, Any] = {"mtime": None, "caminho": None, "mapa": {}}


def mapa(caminho: Path | None = None) -> dict[str, str]:
    """A tabela evento → assinatura (lida uma vez; relida se o arquivo mudar)."""
    p = Path(caminho or ARQUIVO)
    try:
        mt = p.stat().st_mtime
    except OSError:
        return {}
    if _cache["caminho"] != str(p) or _cache["mtime"] != mt:
        try:
            _cache["mapa"] = dict(json.loads(p.read_text(encoding="utf-8")).get("eventos") or {})
        except (OSError, ValueError):
            _cache["mapa"] = {}
        _cache["mtime"], _cache["caminho"] = mt, str(p)
    return _cache["mapa"]


def corrigir(tipo: str, evento_id: str, dados: dict[str, Any], caminho: Path | None = None) -> dict[str, Any]:
    """O evento pela assinatura do documento, quando a tabela tem a tradução dele (só certidao.gravada)."""
    if tipo != "certidao.gravada" or dados.get("documento_sha256") or not isinstance(dados.get("documento_id"), int):
        return dados
    sha = mapa(caminho).get(evento_id)
    if not sha:
        return dados
    d = {k: v for k, v in dados.items() if k != "documento_id"}
    d["documento_sha256"] = sha
    return d


def _arquivos(pasta: Path, desde: str) -> list[Path]:
    out = []
    for a in sorted(Path(pasta).rglob("*.jsonl")):
        partes = a.relative_to(pasta).parts
        if len(partes) >= 4 and all(x.isdigit() for x in partes[:3]) and "-".join(partes[:3]) >= desde:
            out.append(a)
    return out


def gerar(biblioteca: str | Path, eventos: str | Path = "eventos", desde: str = DESDE_PADRAO, caminho: Path | None = None,
          agora: datetime | None = None) -> dict[str, Any]:
    """Uma vez, na produção: a tradução de cada certidao.gravada com número (sem assinatura) desde `desde`.

    Incremental e idempotente: o que já está na tabela não é refeito. Conclui sozinha quando a última certidão com número
    tem mais de 24 h (os emissores já gravam a assinatura) — daí em diante não lê mais nada."""
    p = Path(caminho or ARQUIVO)
    atual = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    if atual.get("concluida_em"):
        return {"concluida_em": atual["concluida_em"], "eventos": len(atual.get("eventos") or {}), "novos": 0}
    traduz: dict[str, str] = dict(atual.get("eventos") or {})
    sem_documento: dict[str, int] = dict(atual.get("sem_documento") or {})
    con = sqlite3.connect(f"file:{Path(biblioteca)}?mode=ro", uri=True)
    novos, ultimo = 0, None
    try:
        for a in _arquivos(Path(eventos), desde):
            for ln in a.read_bytes().splitlines():
                if b'"certidao.gravada"' not in ln:
                    continue
                ev = json.loads(ln)
                d = ev.get("dados") or {}
                if ev.get("tipo") != "certidao.gravada" or d.get("documento_sha256") or not isinstance(d.get("documento_id"), int):
                    continue
                ultimo = max(ultimo or "", ev.get("em") or "")
                if ev["id"] in traduz or ev["id"] in sem_documento:
                    continue
                r = con.execute("SELECT sha256 FROM documento WHERE id = ?", (d["documento_id"],)).fetchone()
                if r and r[0]:
                    traduz[ev["id"]] = r[0]
                    novos += 1
                else:
                    sem_documento[ev["id"]] = d["documento_id"]
    finally:
        con.close()
    momento = agora or datetime.now(timezone.utc)
    saida: dict[str, Any] = {"o_que_e": "N-02 (25/11/2026): a assinatura do documento de cada certidão gravada com o número do banco "
                             "(a tradução que o gravador usa numa remontagem; a produção não muda)",
                             "desde": desde, "gerada_em": momento.isoformat(timespec="seconds"), "ultima_certidao_com_numero": ultimo,
                             "eventos": traduz, "sem_documento": sem_documento}
    if ultimo is None or datetime.fromisoformat(ultimo.replace("Z", "+00:00")) < momento - timedelta(hours=CONCLUIR_DEPOIS_H):
        saida["concluida_em"] = momento.isoformat(timespec="seconds")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(saida, ensure_ascii=False, indent=0, sort_keys=True), encoding="utf-8")
    _cache["mtime"] = None
    return {"eventos": len(traduz), "novos": novos, "sem_documento": len(sem_documento), "concluida_em": saida.get("concluida_em")}
