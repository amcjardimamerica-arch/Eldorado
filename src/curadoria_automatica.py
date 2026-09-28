"""CURADORIA AUTOMÁTICA (titular, 28/09) — nenhuma oportunidade fica no mapa sem decisão.

O que chega depois da validação individual (motores, Espião, Interceptador) é decidido aqui, pelas regras abaixo,
e gravado no MESMO formato da validação, em dados/oportunidades/validacao_mapa/validacao_0000-automatica.json.
O nome faz este arquivo ser lido PRIMEIRO: qualquer decisão humana ou do Claude, para o mesmo item, prevalece.
Depois, src.validacao_mapa leva cada decisão ao arquivo da Biblioteca, ao preditivo e aos opressores.

  ENCERRADA   → Biblioteca (arquivo + preditivo)   prazo vencido, ou só anos passados no título/endereço
  DESCARTADA  → sai do sistema                     não serve a entidade do terceiro setor: fundo patrimonial ou
                                                   organização (quem RECEBE doação, não chamada aberta), vaga de
                                                   emprego/estágio, concurso de servidores, licitação/compra,
                                                   regras aprendidas pela validação (config/filtros_motores.json)
  PENDENTE    → fica como possível, sem confirmação   o resto: a análise do Claude decide
  (o que já tem objeto, prazo aberto e link oficial não recebe decisão automática: aparece como confirmado)
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARQ = ROOT / "dados/oportunidades/validacao_mapa/validacao_0000-automatica.json"
FLUXO = ROOT / "docs/dados/fluxo_oportunidades.json"

CHAMADA = re.compile(r"edital|chamad|chamamento|pr[eê]mio|sele[cç][aã]o|inscri[cç]|convocat|apoio a projetos|financiamento|credenciamento", re.I)
NAO_SERVE = [
    (re.compile(r"fundo patrimonial|associa[cç][aã]o gestora|endowment", re.I), "fundo patrimonial ou gestora: recebe doações, não é chamada aberta para entidades"),
    (re.compile(r"\bcontrata\b|vaga[s]? de|oportunidade de emprego|est[aá]gio|trainee|processo seletivo simplificado|concurso p[uú]blico", re.I), "vaga de emprego, estágio ou concurso de servidores — não é recurso para entidade"),
    (re.compile(r"preg[aã]o|licita[cç][aã]o|tomada de pre[cç]os|aquisi[cç][aã]o de|registro de pre[cç]os|contrata[cç][aã]o de empresa", re.I), "compra ou licitação (Lei 14.133) — não é parceria com entidade"),
    (re.compile(r"jornalismo investigativo|bolsa de doutorado|bolsa de mestrado|p[oó]s-doutorado", re.I), "direcionado a jornalistas ou pesquisadores, não a entidades do terceiro setor"),
]


def _anos(s: str) -> list[int]:
    return [int(a) for a in re.findall(r"(?<!\d)(20[12]\d)(?!\d)", s or "")]


def decidir(x: dict) -> dict | None:
    hoje = date.today()
    tit, url = str(x.get("titulo") or ""), str(x.get("url") or "")
    if x.get("confirmada"):
        return None                                     # tem o mínimo: aparece como confirmada, sem decisão automática
    if x.get("fim") and x["fim"] < hoje.isoformat():
        return {"decisao": "arquivada_encerrada", "motivo": f"prazo encerrado em {x['fim']}", "regra": "prazo_vencido"}
    anos = _anos(tit + " " + url)
    if anos and max(anos) < hoje.year:
        return {"decisao": "arquivada_encerrada", "motivo": f"edição de {max(anos)} (só anos passados no título/endereço)", "regra": "ano_passado"}
    for rx, motivo in NAO_SERVE:
        if rx.search(tit):
            return {"decisao": "descartada", "motivo": motivo, "regra": "nao_serve_terceiro_setor"}
    try:
        from .validacao_mapa import dispensa
        d = dispensa(str(x.get("origem") or ""), {"titulo": tit, "url": url})
        if d and d.get("decisao") in ("descartada", "arquivada_encerrada"):
            return {"decisao": d["decisao"], "motivo": d.get("motivo") or "regra aprendida na validação", "regra": d.get("regra") or "regra_aprendida"}
    except Exception:
        pass
    if x.get("tipo") == "empresa/instituto" and not CHAMADA.search(tit + " " + url):
        return {"decisao": "descartada", "motivo": "nome de organização, sem chamada, edital ou prêmio identificável", "regra": "sem_chamada"}
    return {"decisao": "pendente", "motivo": "triagem automática: sem prazo e site oficial confirmados — aguardando a análise do Claude", "regra": "pendente_auto"}


def run() -> dict:
    F = json.loads(FLUXO.read_text(encoding="utf-8"))
    atual = json.loads(ARQ.read_text(encoding="utf-8")) if ARQ.exists() else {"regra": __doc__.strip(), "itens": []}
    por_id = {r["id"]: r for r in atual.get("itens", [])}
    cont = {}
    for uf, itens in (F.get("itens_por_uf") or {}).items():
        for x in itens:
            if x.get("validacao") or not x.get("id"):
                continue                                 # já decidido (validação ou decisão anterior)
            d = decidir(x)
            if not d:
                continue
            por_id[x["id"]] = {"id": x["id"], "titulo": x.get("titulo"), "orgao": x.get("orgao"), "uf": None if uf == "__nac__" else uf,
                               "tipo": x.get("tipo"), "origem": x.get("origem"), "url": x.get("url"), "publicado_em": x.get("publicado_em"),
                               "prazo": x.get("fim"), "decisao": d["decisao"], "motivo": d["motivo"], "via": "curadoria automática",
                               "regra_aprendida": d["regra"], "validado_em": date.today().isoformat(),
                               "recomendacao_motor": "dispensar na origem" if d["decisao"] == "descartada" else None}
            cont[d["decisao"]] = cont.get(d["decisao"], 0) + 1
    atual["itens"] = list(por_id.values()); atual["gerado_em"] = date.today().isoformat()
    ARQ.parent.mkdir(parents=True, exist_ok=True)
    ARQ.write_text(json.dumps(atual, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"novas_decisoes": cont, "total_automaticas": len(por_id)}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False))
