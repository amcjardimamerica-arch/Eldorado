"""Arquivamento na Biblioteca de Alexandria.

Determinação do titular: quando um edital é REMOVIDO DA ANÁLISE — descartado
pelo parecer ou encerrado após a inscrição — suas informações não se perdem:
são arquivadas na Biblioteca, na pasta do respectivo edital e do ANO em que
aconteceu, para compor o histórico que alimenta a leitura de padrões.

Entra na pasta `biblioteca_alexandria/oportunidades/<chave>/<ANO>/`:
  arquivamento.json   motivo, data, decisão e quem decidiu
  historico.jsonl     uma linha por movimento (trilha append-only)

Nada é apagado: o texto do edital, os modelos e a ficha permanecem, porque é
justamente esse acervo que responde "o que costuma ser cobrado" nos próximos.

Entrada: `estado/decisoes_editais.json`, exportado pelo painel (botões
«Inscrição realizada» e «Descartar») e versionado no repositório.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from .biblioteca import OPORTUNIDADES
from .nucleo import ROOT, load_json, now_iso, write_json

DECISOES = ROOT / "estado/decisoes_editais.json"

MOTIVOS = {
    "inscrito": "inscrição realizada — acompanhamento de resultado e recurso",
    "descartado": "removido da análise — edital descartado",
    "encerrado": "prazo encerrado sem inscrição",
}


def _chave_ano(edital_id: str, dados_painel: dict | None = None) -> tuple[str, str] | None:
    """Localiza a pasta do edital na Biblioteca a partir do id."""
    for ficha in OPORTUNIDADES.glob("*/*/ficha.json"):
        try:
            if load_json(ficha).get("id") == edital_id:
                return ficha.parent.parent.name, ficha.parent.name
        except Exception:
            continue
    return None


def arquivar(edital_id: str, estado: str, titulo: str = "",
             observacao: str = "", quando: date | None = None) -> dict:
    """Arquiva as informações do edital na sua pasta/ano da Biblioteca."""
    quando = quando or date.today()
    alvo = _chave_ano(edital_id)
    if alvo is None:
        return {"edital_id": edital_id, "arquivado": False,
                "motivo": "edital ainda não consta da Biblioteca (sem verificação "
                          "dupla concluída); decisão registrada apenas no painel"}
    chave, ano = alvo
    pasta = OPORTUNIDADES / chave / ano
    registro = {"edital_id": edital_id, "titulo": titulo, "estado": estado,
                "motivo": MOTIVOS.get(estado, estado),
                "observacao": observacao or None,
                "arquivado_em": now_iso(), "ano_do_evento": ano}
    anterior = load_json(pasta / "arquivamento.json") if (pasta / "arquivamento.json").exists() else {}
    write_json(pasta / "arquivamento.json", {**anterior, **registro})
    with (pasta / "historico.jsonl").open("a", encoding="utf-8") as h:
        h.write(json.dumps(registro, ensure_ascii=False) + "\n")
    return {**registro, "arquivado": True,
            "pasta": str(pasta.relative_to(ROOT))}


def run() -> dict:
    """Processa as decisões exportadas do painel."""
    if not DECISOES.exists():
        return {"executado_em": now_iso(), "arquivados": 0,
                "nota": "nenhuma decisão exportada ainda"}
    dados = load_json(DECISOES)
    feitos, pendentes = [], []
    for eid, dec in (dados.get("decisoes") or {}).items():
        estado = dec.get("estado")
        if estado not in ("inscrito", "descartado", "encerrado"):
            continue
        r = arquivar(eid, estado, dec.get("titulo", ""), dec.get("observacao", ""))
        (feitos if r.get("arquivado") else pendentes).append(r)
    return {"executado_em": now_iso(), "arquivados": len(feitos),
            "pendentes": len(pendentes), "detalhe": feitos[:20],
            "nao_arquivados": pendentes[:20]}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
