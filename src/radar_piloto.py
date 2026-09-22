"""RADAR DE CAPTAÇÃO — o que o Piloto descobre vira empresa no ranking.

Cada alvo confirmado pelo Piloto (empresa, instituto, fundação, programa) entra em
dados/empresas/radar_piloto.json com um MARCADOR de pesquisa, igual ao selo das
oportunidades:

  a_pesquisar ...... descoberta com site oficial, mas falta o resto (ESG, editais
                     anteriores, como pleitear). Vai para o pacote do Claude externo.
  em_pesquisa ...... o Claude pegou para investigar
  concluido ........ pesquisa feita: sabe-se o que financia, como e quando

O arquivo alimenta o ranking de empresas e o painel. Quem decide a mudança de marcador
é sempre quem pesquisou — o Piloto só cria com 'a_pesquisar'.
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

from .nucleo import ROOT, load_json, now_iso, write_json

RADAR = ROOT / "dados/empresas/radar_piloto.json"
PUB = ROOT / "docs/dados/radar_piloto.json"
MARCADORES = ("a_pesquisar", "em_pesquisa", "concluido")


def _chave(nome: str, url: str | None = None) -> str:
    if url:
        h = (urlsplit(url).hostname or "").replace("www.", "")
        if h:
            return h
    return re.sub(r"[^a-z0-9]", "", (nome or "").lower())[:40]


def radar() -> dict:
    return load_json(RADAR) if RADAR.exists() else {"versao": 1, "atualizado_em": None, "empresas": {}}


def registrar(alvo: dict, angulo: str = "", motor: str = "") -> dict | None:
    """Um achado confirmado do Piloto vira (ou atualiza) uma empresa no radar."""
    nome = (alvo.get("titulo") or "").strip()
    url = alvo.get("url")
    if not nome or not url:
        return None
    r = radar()
    k = _chave(nome, url)
    e = r["empresas"].get(k)
    if e:
        e["vezes_vista"] = e.get("vezes_vista", 1) + 1
        e["ultima_vez"] = date.today().isoformat()
        for campo, valor in (("trecho", alvo.get("trecho")), ("porque", alvo.get("porque"))):
            if valor and not e.get(campo):
                e[campo] = valor[:200]
        if angulo and angulo not in e.setdefault("angulos", []):
            e["angulos"].append(angulo)
    else:
        nivel = {"esg_relatorio_go": "regional", "patrocinador_de_entidade": "regional", "lucro_real_go": "regional",
                 "agro_industria_go": "regional", "energia_saneamento_go": "regional", "cooperativa_sistema_s": "regional",
                 "internacional_br": "internacional", "multinacional_no_brasil": "internacional"}.get(angulo, "nacional")
        r["empresas"][k] = {
            "nome": nome[:120], "site": url, "dominio": (urlsplit(url).hostname or "").replace("www.", ""),
            "descoberto_em": date.today().isoformat(), "ultima_vez": date.today().isoformat(), "vezes_vista": 1,
            "por": "piloto", "motor": motor, "angulos": [angulo] if angulo else [], "nivel": nivel,
            "trecho": (alvo.get("trecho") or "")[:200], "porque": (alvo.get("porque") or "")[:200],
            "consulta": (alvo.get("consulta") or "")[:120],
            "marcador": "a_pesquisar",
            "a_descobrir": ["relatório ESG e o que declara financiar", "editais anteriores (indicam recorrência)",
                            "edital aberto hoje", "como pleitear (contato, formulário, e-mail)", "valores típicos de apoio",
                            "se aceita OSC de Goiás"],
            "esg": {"tem_relatorio": None, "declara_investimento_social": None, "areas": []},
            "editais": {"anteriores": [], "abertos": []},
            "potencial": None}
    r["atualizado_em"] = now_iso()
    write_json(RADAR, r)
    return r["empresas"][k]


def marcar(chave: str, marcador: str, por: str = "claude", dados: dict | None = None) -> dict:
    """Muda o marcador e guarda o que a pesquisa trouxe."""
    if marcador not in MARCADORES:
        return {"erro": f"marcador inválido: {marcador}"}
    r = radar()
    e = r["empresas"].get(chave)
    if not e:
        return {"erro": f"{chave} não está no radar"}
    e["marcador"] = marcador
    e.setdefault("historico", []).append({"em": now_iso()[:16], "marcador": marcador, "por": por})
    if dados:
        for campo in ("esg", "editais", "potencial", "como_pleitear", "contato", "valores", "aceita_go"):
            if campo in dados:
                e[campo] = dados[campo]
        if marcador == "concluido":
            e["pesquisado_em"] = date.today().isoformat(); e["pesquisado_por"] = por
            e["a_descobrir"] = [x for x in e.get("a_descobrir", []) if not dados.get("cobre_tudo")]
    r["atualizado_em"] = now_iso()
    write_json(RADAR, r)
    return e


def publicar() -> dict:
    """Fragmento para o painel + integração ao ranking de empresas."""
    r = radar()
    emp = r.get("empresas", {})
    por_marcador = {m: sum(1 for e in emp.values() if e.get("marcador") == m) for m in MARCADORES}
    lista = sorted(emp.items(), key=lambda kv: (kv[1].get("marcador") != "a_pesquisar", -(kv[1].get("vezes_vista") or 0), kv[1]["nome"]))
    saida = {"em": now_iso(), "total": len(emp), "por_marcador": por_marcador,
             "regra": "descoberta do Piloto entra como 'a pesquisar'; o Claude externo investiga e conclui",
             "empresas": [{"chave": k, **{c: v.get(c) for c in ("nome", "site", "nivel", "marcador", "descoberto_em", "vezes_vista", "motor", "angulos", "porque", "potencial")},
                           "falta": len(v.get("a_descobrir") or []) if v.get("marcador") != "concluido" else 0}
                          for k, v in lista[:200]]}
    write_json(PUB, saida)
    # o ranking oficial tem 100 posições ordenadas por pontuação e não é alterado pelo Piloto.
    # As descobertas viram uma LISTA PRÓPRIA — "Radar", que o painel mostra ao lado do ranking —
    # e só entram no ranking depois que o Claude concluir a pesquisa e houver o que pontuar.
    rk = ROOT / "biblioteca_alexandria/empresas/radar_captacao.json"
    prontas = [e for e in emp.values() if e.get("marcador") == "concluido"]
    write_json(rk, {"gerado_em": now_iso(), "regra": "descobertas do Piloto; entram no ranking oficial quando a pesquisa concluir e houver pontuação",
                    "total": len(emp), "concluidas": len(prontas),
                    "empresas": [{"nome": e["nome"], "site": e.get("site"), "nivel": e.get("nivel"), "marcador": e.get("marcador"),
                                  "descoberto_em": e.get("descoberto_em"), "sinais": e.get("angulos") or [],
                                  "esg": e.get("esg"), "editais": e.get("editais"), "potencial": e.get("potencial"),
                                  "leitura": (e.get("porque") or "")[:140]} for e in emp.values()]})
    saida["radar_captacao"] = str(rk.relative_to(ROOT))
    return {k: v for k, v in saida.items() if k != "empresas"}


def para_o_claude(limite: int = 40) -> list[dict]:
    """A fila que vai para o pacote do Claude externo."""
    r = radar()
    return [{"chave": k, "nome": e["nome"], "site": e["site"], "nivel": e.get("nivel"),
             "porque": e.get("porque"), "a_descobrir": e.get("a_descobrir")}
            for k, e in r.get("empresas", {}).items() if e.get("marcador") == "a_pesquisar"][:limite]


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "fila":
        print(json.dumps(para_o_claude(), ensure_ascii=False, indent=1))
    else:
        print(json.dumps(publicar(), ensure_ascii=False, indent=1))
