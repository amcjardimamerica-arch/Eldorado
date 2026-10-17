"""TRAVA DOS LIVROS (titular, 17/10/2026): um livro criado NÃO pode ser apagado pelo sistema nem sobrescrito —
apenas receber informação nova.

Referência: o que está GRAVADO no repositório (git HEAD). Roda antes de cada gravação (fechamento do comando e todos os
fluxos que gravam livros) e reconcilia o que mudou desde a última gravação:

1. NENHUM LIVRO SOME. Livro que sai do catálogo por UNIÃO REGISTRADA (o que fica tem o id dele em "juntados") é
   guardado INTEIRO em biblioteca_alexandria/livros/_arquivados/<id>.json, para sempre. Sem união registrada, VOLTA.
2. NADA É SOBRESCRITO NO CONTEÚDO. Campo que sumiu volta; listas e dicionários só ganham itens (o retirado volta); valor
   que mudou fica com o novo e o anterior é guardado no próprio livro em "_anteriores", com a data.
3. CAMPOS OPERACIONAIS (situação, selo, leituras, próxima data, diagnóstico…) mudam normalmente: são o estado do
   momento, não informação do livro.
4. Os ARQUIVOS de cada livro (biblioteca_alexandria/livros/<id>.json) seguem as mesmas regras; arquivo apagado volta.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT_REL = "biblioteca_alexandria/fontes/motores.json"
LIVROS_REL = "biblioteca_alexandria/livros"
ARQUIVADOS = ROOT / LIVROS_REL / "_arquivados"
REGISTRO = ROOT / "estado/trava_livros.json"

# estado do momento — muda livremente (não é informação do livro)
OPERACIONAIS = {
    "estado", "situacao", "status", "selo", "estrela", "ativa", "validacao", "ultima_leitura", "http", "motivo_status",
    "em_epoca", "proximidade", "confianca_pagina", "camadas", "diagnostico", "achados", "obtidas", "proxima_data",
    "previsao", "atual", "atualizado_em", "em", "versao", "regime_prazo", "certeza_prazo", "nota", "pontuacao",
    "ultimo_edital", "fila", "tentativas", "ultima_tentativa", "proxima_tentativa", "_anteriores", "restaurado_em",
    "restaurado_de", "segmento", "familia", "goias", "nivel", "contagem", "resumo", "ligado", "ligados", "cursor",
}
MAX_ANTERIORES = 10


def _agora() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _git(*a: str) -> str | None:
    r = subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def _vazio(v) -> bool:
    return v is None or v == "" or v == [] or v == {}


def _chave_item(x) -> str:
    if isinstance(x, dict) and x.get("id") is not None:
        return f"id:{x.get('id')}"
    return json.dumps(x, ensure_ascii=False, sort_keys=True)


def reconciliar(antes: dict, depois: dict, st: dict, nivel: int = 0) -> dict:
    """O 'depois' só pode GANHAR em relação ao 'antes' (nos campos de conteúdo)."""
    for k, va in antes.items():
        if nivel == 0 and k in OPERACIONAIS:
            continue
        if k not in depois or (_vazio(depois.get(k)) and not _vazio(va)):
            depois[k] = va; st["campos_devolvidos"] += 1
            continue
        vd = depois[k]
        if isinstance(va, list) and isinstance(vd, list):
            tem = {_chave_item(x) for x in vd}
            falta = [x for x in va if _chave_item(x) not in tem]
            if falta:
                depois[k] = falta + vd if k in ("historico",) else vd + falta
                st["itens_devolvidos"] += len(falta)
        elif isinstance(va, dict) and isinstance(vd, dict):
            for kk, vv in va.items():
                if kk not in vd:
                    vd[kk] = vv; st["itens_devolvidos"] += 1
        elif va != vd and not _vazio(va) and nivel == 0:
            ant = depois.setdefault("_anteriores", {}).setdefault(k, [])
            if not ant or ant[-1].get("valor") != va:
                ant.append({"valor": va, "ate": _agora()})
                del ant[:-MAX_ANTERIORES]
                st["valores_preservados"] += 1
    return depois


def _juntados(livros: list[dict]) -> set[str]:
    out = set()
    for lv in livros:
        for j in lv.get("juntados") or []:
            out.add(str(j.get("id") if isinstance(j, dict) else j))
    return out


def _arquivar(lv: dict, motivo: str) -> None:
    ARQUIVADOS.mkdir(parents=True, exist_ok=True)
    p = ARQUIVADOS / f"{lv.get('id')}.json"
    if not p.exists():
        p.write_text(json.dumps({"arquivado_em": _agora(), "motivo": motivo, "livro": lv}, ensure_ascii=False), encoding="utf-8")


def aplicar(ref: str = "HEAD", gravar: bool = True) -> dict:
    st = {"livros_devolvidos": 0, "livros_arquivados_por_uniao": 0, "campos_devolvidos": 0, "itens_devolvidos": 0,
          "valores_preservados": 0, "arquivos_devolvidos": 0, "arquivos_reconciliados": 0}
    # 1-3. CATÁLOGO
    raw = _git("show", f"{ref}:{CAT_REL}")
    cat_p = ROOT / CAT_REL
    if raw and cat_p.exists():
        A = {x.get("id"): x for x in json.loads(raw).get("motores") or [] if x.get("id")}
        D = json.loads(cat_p.read_text(encoding="utf-8"))
        L = D.setdefault("motores", [])
        por_id = {x.get("id"): x for x in L if x.get("id")}
        unidos = _juntados(L)
        for i, la in A.items():
            if i in por_id:
                reconciliar(la, por_id[i], st)
            elif str(i) in unidos:
                _arquivar(la, "unido a outro livro (registrado em 'juntados')"); st["livros_arquivados_por_uniao"] += 1
            else:
                L.append(la); st["livros_devolvidos"] += 1
        if gravar and any(st[k] for k in ("livros_devolvidos", "campos_devolvidos", "itens_devolvidos", "valores_preservados")):
            cat_p.write_text(json.dumps(D, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    # 4. ARQUIVOS DE CADA LIVRO (só os que mudaram desde a gravação)
    dif = _git("diff", "--name-status", ref, "--", LIVROS_REL) or ""
    for linha in dif.splitlines():
        partes = linha.split("\t")
        if len(partes) < 2:
            continue
        estado_git, rel = partes[0], partes[-1]
        nome = Path(rel).name
        if "/" in rel[len(LIVROS_REL) + 1:] or not nome.endswith(".json") or nome.startswith("_"):
            continue                                       # só os livros (não índices, vistas, acervo)
        antigo = _git("show", f"{ref}:{rel}")
        if not antigo:
            continue
        p = ROOT / rel
        if estado_git.startswith("D") or not p.exists():
            if gravar:
                p.parent.mkdir(parents=True, exist_ok=True); p.write_text(antigo, encoding="utf-8")
            st["arquivos_devolvidos"] += 1
            continue
        try:
            a, d = json.loads(antigo), json.loads(p.read_text(encoding="utf-8"))
        except ValueError:
            if gravar:
                p.write_text(antigo, encoding="utf-8")
            st["arquivos_devolvidos"] += 1
            continue
        if isinstance(a, dict) and isinstance(d, dict):
            antes = json.dumps(d, sort_keys=True)
            reconciliar(a, d, st)
            if json.dumps(d, sort_keys=True) != antes:
                st["arquivos_reconciliados"] += 1
                if gravar:
                    p.write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    if gravar and any(st.values()):
        try:
            R = json.loads(REGISTRO.read_text(encoding="utf-8")) if REGISTRO.exists() else {"ocorrencias": []}
        except ValueError:
            R = {"ocorrencias": []}
        R["ocorrencias"] = (R.get("ocorrencias") or [])[-99:] + [{"em": _agora(), **st}]
        REGISTRO.parent.mkdir(parents=True, exist_ok=True)
        REGISTRO.write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
    return st


if __name__ == "__main__":
    print(json.dumps(aplicar(gravar="--simular" not in sys.argv), ensure_ascii=False))
