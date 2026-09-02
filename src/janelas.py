"""Janelas especiais — de hipótese a oportunidade confirmada.

O defeito que o titular apontou: a Lei Rouanet estava com inscrições abertas e
o calendário não a mostrava. Causa: a janela era "hipótese, a confirmar", e a
única via de confirmação era a extração automática — que nunca tinha rodado.
O sistema não tinha porta para a confirmação mais autorizada que existe: a do
próprio titular, que sabe que a janela está aberta.

Agora há duas vias, ambas registradas com evidência:
  · `titular`  — o titular confirma, com data (config/janelas_confirmadas.json)
  · `sensor`   — o sensor da fonte encontra na página oficial texto de
                 inscrições abertas (verificação automática, no CI)

Janela confirmada para o ano vira OPORTUNIDADE ABERTA: entra no calendário do
mês corrente com barra de inscrição, no Radar como identificada, e a ficha
diz por qual via foi confirmada. No ano seguinte volta a hipótese até nova
confirmação — nada fica confirmado por inércia.
"""
from __future__ import annotations

import json
import re
from datetime import date

from .lexico import casar
from .nucleo import ROOT, load_json, now_iso, write_json

ESPECIAIS = ROOT / "config/previsoes_especiais.json"
CONFIRMADAS = ROOT / "config/janelas_confirmadas.json"
ESTADO = ROOT / "estado/janelas_verificadas.json"

_ABERTA = re.compile(
    r"inscri[çc][õo]es\s+(?:abertas|at[ée]|prorrogadas)|prazo\s+(?:de\s+inscri[çc][ãa]o\s+)?"
    r"(?:at[ée]|prorrogado)|per[íi]odo\s+de\s+inscri[çc][ãa]o|apresenta[çc][ãa]o\s+de\s+propostas?\s+at[ée]|"
    r"submiss[ãa]o\s+de\s+projetos", re.I)
_DATA = re.compile(r"\b(\d{1,2})/(\d{1,2})/(20\d{2})\b")


def _regras() -> dict[str, dict]:
    if not ESPECIAIS.exists():
        return {}
    return {r["id"]: r for r in load_json(ESPECIAIS).get("regras", [])}


def confirmacoes(ano: int) -> dict[str, dict]:
    """Confirmações válidas para o ano: do titular (config) + do sensor (estado)."""
    saida: dict[str, dict] = {}
    if CONFIRMADAS.exists():
        for c in load_json(CONFIRMADAS).get("confirmacoes", []):
            if c.get("ano") == ano:
                saida[c["id"]] = {**c, "via": "titular"}
    if ESTADO.exists():
        for k, v in load_json(ESTADO).get("verificadas", {}).items():
            if v.get("ano") == ano and v.get("aberta"):
                saida.setdefault(k, {}).update({**v, "via": (saida.get(k, {}).get("via") or "sensor")})
                if saida[k].get("via") == "titular":
                    saida[k]["via"] = "titular + sensor"
    return saida


def verificar_por_sensor(hoje: date | None = None) -> dict:
    """Abre a página oficial de cada janela especial e procura evidência textual
    de inscrições abertas. Roda no CI (a rede daqui não alcança). Nunca
    confirma sem texto: registra 'sem evidência' e segue."""
    from .sensores import _abrir
    hoje = hoje or date.today()
    est = load_json(ESTADO) if ESTADO.exists() else {"verificadas": {}}
    for rid, r in _regras().items():
        url = r.get("fonte_confirmacao")
        reg = {"ano": hoje.year, "verificado_em": now_iso(), "url": url}
        try:
            html, final, status = _abrir(url)
            texto = re.sub(r"<[^>]+>", " ", html)
            texto = re.sub(r"\s+", " ", texto)
            m = _ABERTA.search(texto)
            if m:
                trecho = texto[max(0, m.start() - 120): m.end() + 220]
                datas = _DATA.findall(trecho)
                reg.update({"aberta": True, "evidencia": trecho[:400],
                            "datas_no_trecho": ["/".join(d) for d in datas][:4],
                            "http": status})
            else:
                reg.update({"aberta": False, "http": status,
                            "motivo": "página respondeu, sem texto de inscrições abertas"})
        except Exception as exc:
            reg.update({"aberta": False, "motivo": f"falha de acesso: {type(exc).__name__}"})
        est["verificadas"][rid] = reg
    est["atualizado_em"] = now_iso()
    write_json(ESTADO, est)
    return est


def encerramentos(ano: int) -> dict[str, dict]:
    if not CONFIRMADAS.exists():
        return {}
    return {x["id"]: x for x in load_json(CONFIRMADAS).get("encerramentos", []) if x.get("ano") == ano}


def oportunidades(hoje: date | None = None) -> list[dict]:
    """Janelas CONFIRMADAS para o ano corrente, como oportunidades abertas."""
    hoje = hoje or date.today()
    conf = confirmacoes(hoje.year)
    saida = []
    enc = encerramentos(hoje.year)
    for rid, r in _regras().items():
        c = conf.get(rid)
        if not c or rid in enc:
            continue
        j = c.get("janela") or {"inicio": f'{hoje.year}-{r["inicio_mes_dia"]}',
                                "fim": f'{hoje.year}-{r["fim_mes_dia"]}'}
        inicio, fim = j["inicio"], j["fim"]
        estado = ("aberto" if inicio <= hoje.isoformat() <= fim
                  else "a_abrir" if hoje.isoformat() < inicio else "encerrado")
        oid = f"janela-{rid}-{hoje.year}"
        saida.append({
            "id": oid, "protocolo": oid,
            "titulo": f'{r["nome"]} — inscrições {hoje.year}',
            "url": c.get("url_inscricao") or r.get("fonte_confirmacao"),
            "fonte_id": rid, "fonte_nome": r.get("orgao"),
            "territorio": r.get("uf") or "BR", "uf": r.get("uf"),
            "uf_exibicao": r.get("uf") or "Brasil",
            "abrangencia": "nacional" if not r.get("uf") else "estadual",
            "nivel": r["nivel"], "status": "verificada_janela_confirmada",
            "area": r["area"], "programa": r["nome"], "lei": r.get("lei"),
            "objeto": (f'Janela anual de inscrição de propostas. '
                       f'Modalidades: {", ".join(r.get("modalidades", [])) or "—"}. '
                       f'Confirmada para {hoje.year} por: {c["via"]}.'),
            "inicio": inicio, "fim": fim, "datas": "ambas",
            "publicado_em": None, "prazo_prorrogado": False,
            "estado_export": estado, "sem_edital": False,
            "janela_confirmada": {"via": c["via"], "em": c.get("confirmado_em") or c.get("verificado_em"),
                                  "evidencia": c.get("evidencia"),
                                  "verificacao_automatica": c.get("verificacao_automatica")
                                  or ("confirmada pelo sensor" if "sensor" in c["via"] else None)},
            "resumo": f'Confirmada por {c["via"]} em {c.get("confirmado_em") or c.get("verificado_em")}. {r["base"]}',
            "valor_texto": None,
            "verificacao_dupla": {"fonte": True, "conteudo": "sensor" in c["via"],
                                  "criterio": "janela anual confirmada para o ano"},
            "etapa": 2, "etapa_nome": "Confirmar",
            "anexos_modelo": [], "anexos": [],
            "ciclo": {"inscricao": {"inicio": inicio, "fim": fim, "projetado": False},
                      "resultado": None, "recurso": None, "fim_do_ciclo": fim},
            "marcos": [{"tipo": "abertura", "data": inicio, "projetado": False},
                       {"tipo": "encerramento", "data": fim, "projetado": False}],
            "destinacao": {"elegivel": True, "natureza": "recurso",
                           "motivo": "incentivo à cultura destinado a proponentes, inclusive OSCs"},
            "confirmacao": "confirmado_documental" if "sensor" in c["via"] else "confirmado_pelo_titular",
            "detalhes": {"qualificacao": {"nota": None, "classe": "janela anual"},
                         "documentos_exigidos": [], "pontuacao": [], "atendidos": [],
                         "pendencias": ([] if "sensor" in c["via"] else
                                        ["verificação automática na página oficial ainda pendente — "
                                         "o sensor confere na próxima saída"]),
                         "evidencia": c.get("evidencia") or r["base"],
                         "coletado_em": hoje.isoformat(), "lacuna": None},
            "ficha": "",
        })
    return saida


if __name__ == "__main__":
    print(json.dumps([{k: o[k] for k in ("id", "estado_export", "inicio", "fim")}
                      for o in oportunidades()], ensure_ascii=False, indent=2))
