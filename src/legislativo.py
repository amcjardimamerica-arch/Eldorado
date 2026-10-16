"""ACOMPANHAMENTO LEGISLATIVO (titular, 15/10/2026).

Eldorado › Oportunidades Abertas › Legislativo: os projetos de lei, as declarações de utilidade pública e o orçamento
(LOA/emendas) que estão sendo apresentados na Câmara de Goiânia, na ALEGO e no Congresso. Ato legislativo NÃO é
oportunidade e NÃO gera livro: é acompanhado — cada mudança de situação (apresentado, em pauta, votação, aprovado,
sancionado) entra na linha do tempo da proposição.

Fontes (o que os motores 04, 05 e Congresso já coletam):
  biblioteca_alexandria/livros/especiais/legislativo/camara_goiania.json          utilidade pública (com a situação na pauta) e itens a acompanhar
  biblioteca_alexandria/livros/especiais/empresas/financiadores/<motor>/eventos  pistas dos motores legislativos (notícias e proposições)
  biblioteca_alexandria/livros/especiais/legislativo/legislativo_entrada.json      atos desviados dos livros (livros_regra.registrar_achados)
Saídas: biblioteca_alexandria/livros/especiais/legislativo/legislativo.json (histórico, com movimentações) e docs/dados/legislativo.json (painel).
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ESTADO = ROOT / "biblioteca_alexandria/livros/especiais/legislativo/legislativo.json"
ENTRADA = ROOT / "biblioteca_alexandria/livros/especiais/legislativo/legislativo_entrada.json"
PAINEL = ROOT / "docs/dados/legislativo.json"
CAMARA = ROOT / "biblioteca_alexandria/livros/especiais/legislativo/camara_goiania.json"
MOTORES = {"camara-goiania-pl": "Câmara Municipal de Goiânia", "alego-pl": "Assembleia Legislativa de Goiás (ALEGO)",
           "congresso-nacional": "Congresso Nacional"}
CASA_POR_HOST = (("goiania.go.leg.br", "camara-goiania-pl"), ("camaragyn", "camara-goiania-pl"), ("al.go.leg.br", "alego-pl"),
                 ("camara.leg.br", "congresso-nacional"), ("senado.leg.br", "congresso-nacional"), ("congressonacional.leg.br", "congresso-nacional"))
PROPOSICAO = re.compile(r"\b(projeto de lei(?: complementar| ordin[áa]ria)?|PLO?A?|PLC|PL|proposi[çc][ãa]o|projeto de resolu[çc][ãa]o|"
                        r"projeto de decreto legislativo|emenda (?:impositiva|parlamentar|à lei org[âa]nica|constitucional))\s*(?:n[ºo°.]*\s*)?(\d{1,5})\s*/\s*(\d{2,4})", re.I)
UTILIDADE = re.compile(r"utilidade p[úu]blica", re.I)
ORCAMENTO = re.compile(r"lei or[çc]ament[áa]ria|\bLOA\b|\bPLOA\b|\bLDO\b|emendas? (?:impositivas?|parlamentar(?:es)?|individuais?)|or[çc]amento de 20\d\d", re.I)
LEGISLATIVO = re.compile(r"projeto de lei|utilidade p[úu]blica|proposi[çc]|lei or[çc]ament|\bLOA\b|\bLDO\b|emenda|plen[áa]rio|vota[çc][ãa]o|"
                         r"san[çc][ãa]o|sancionad|aprovad[oa] em|tramita", re.I)
SITUACAO = ((r"sancionad|promulgad|virou lei|lei n[ºo°]", "sancionado / promulgado"), (r"vetad", "vetado"),
            (r"aprovad[oa] em (?:segunda|2[ªa]|[úu]nica)|aprovad[oa] em definitivo|reda[çc][ãa]o final", "aprovado em definitivo"),
            (r"aprovad[oa]", "aprovado em votação"), (r"segunda vota[çc]", "em pauta — segunda votação"),
            (r"primeira vota[çc]|1[ªa] vota[çc]", "em pauta — primeira votação"), (r"em pauta|pauta d", "em pauta"),
            (r"comiss[ãa]o|CCJ|parecer", "em comissão"), (r"arquivad|retirad", "arquivado / retirado"),
            (r"apresentad|protocolad|come[çc]a a tramitar|lido em plen", "apresentado"))


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao


def _agora() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _n(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", str(s or "").lower()) if unicodedata.category(c) != "Mn")


def casa_de(url: str = "", motor: str | None = None) -> str | None:
    if motor in MOTORES:
        return motor
    u = str(url or "").lower()
    return next((m for h, m in CASA_POR_HOST if h in u), None)


def tipo_de(texto: str) -> str:
    if UTILIDADE.search(texto or ""):
        return "Utilidade pública"
    if ORCAMENTO.search(texto or ""):
        return "Orçamento (LOA / emendas)"
    if PROPOSICAO.search(texto or "") or re.search(r"projeto de lei", texto or "", re.I):
        return "Projeto de lei"
    return "Outro ato legislativo"


def situacao_de(texto: str) -> str | None:
    for rx, nome in SITUACAO:
        if re.search(rx, texto or "", re.I):
            return nome
    return None


def numero_de(texto: str) -> str | None:
    m = PROPOSICAO.search(texto or "")
    if not m:
        return None
    sigla = "PL" if re.match(r"projeto de lei|PL", m.group(1), re.I) else m.group(1).strip().upper()[:30]
    ano = m.group(3) if len(m.group(3)) == 4 else "20" + m.group(3)
    return f"{sigla} {int(m.group(2))}/{ano}"


def e_legislativo(achado: dict, origem: str = "") -> bool:
    """O achado é ato legislativo (não vira livro)? Motor legislativo, ou casa legislativa + texto de proposição."""
    if str(achado.get("fonte_id") or achado.get("motor") or "") in MOTORES:
        return True
    if any(n in str(origem or "") for n in ("Câmara Municipal", "Assembleia Legislativa", "Congresso Nacional", "ALEGO")):
        return True
    txt = f"{achado.get('titulo') or ''} {achado.get('objeto') or ''}"
    return bool(casa_de(str(achado.get("url") or ""))) and bool(LEGISLATIVO.search(txt))


def receber(achado: dict, origem: str = "") -> None:
    """Desvio dos livros: o ato legislativo entra na fila do acompanhamento."""
    fila = _j(ENTRADA, {"itens": []})
    url = str(achado.get("url") or achado.get("pagina_oficial") or "")
    if any(x.get("url") == url and x.get("titulo") == achado.get("titulo") for x in fila["itens"]):
        return
    fila["itens"].append({"titulo": str(achado.get("titulo") or "")[:300], "url": url, "motor": achado.get("fonte_id") or achado.get("motor"),
                          "origem": str(origem)[:120], "data": achado.get("publicado_em") or achado.get("data_publicacao"), "recebido_em": _agora()})
    fila["itens"] = fila["itens"][-2000:]
    ENTRADA.parent.mkdir(parents=True, exist_ok=True)
    ENTRADA.write_text(json.dumps(fila, ensure_ascii=False, indent=1), encoding="utf-8")


def _chave(casa: str | None, numero: str | None, titulo: str, url: str) -> str:
    base = f"{casa}|{numero}" if numero else f"{casa}|{_n(titulo)[:120]}|{url}"
    return hashlib.sha1(base.encode()).hexdigest()[:16]


def _eventos(motor: str) -> list[dict]:
    d = _j(ROOT / f"biblioteca_alexandria/livros/especiais/empresas/financiadores/{motor}/eventos.compacto.json", {})
    sc = d.get("schema") or []
    return [dict(zip(sc, ln)) for ln in d.get("linhas") or []] if sc else []


def coletar() -> list[dict]:
    """Observações de hoje: cada uma vira (ou movimenta) uma proposição."""
    obs = []
    cam = _j(CAMARA, {})
    for u in cam.get("utilidade_publica") or []:
        proj = u.get("projeto") or u.get("processo") or ""
        obs.append({"casa": "camara-goiania-pl", "tipo": "Utilidade pública", "numero": numero_de(proj),
                    "titulo": f"Declara de utilidade pública: {u.get('entidade') or '—'}", "entidade": u.get("entidade"),
                    "autor": u.get("autor"), "apresentado_em": u.get("criado"), "situacao": u.get("situacao") or "apresentado",
                    "setor": u.get("setor"), "url": u.get("url"), "data": _data_da_situacao(u.get("situacao")) or u.get("criado")})
    for a in cam.get("acompanhar") or []:
        t = str(a.get("titulo") or "").replace("Câmara de Goiânia — ", "")
        obs.append({"casa": "camara-goiania-pl", "tipo": "Orçamento (LOA / emendas)" if a.get("categoria") == "orcamento_emendas" else tipo_de(t),
                    "numero": numero_de(t), "titulo": t, "autor": a.get("autor"), "situacao": a.get("situacao") or situacao_de(t) or "em acompanhamento",
                    "url": a.get("url"), "data": a.get("data_publicacao"), "motivo": a.get("motivo")})
    for motor in MOTORES:
        for e in _eventos(motor):
            t = re.sub(r"^\s*\d{1,2}:\d{2}\s+", "", re.sub(r"\s+", " ", str(e.get("titulo") or ""))).strip()
            if not LEGISLATIVO.search(t):
                continue
            obs.append({"casa": motor, "tipo": tipo_de(t), "numero": numero_de(t), "titulo": t[:300], "situacao": situacao_de(t) or "noticiado",
                        "url": e.get("url"), "data": str(e.get("coletado_em") or "")[:10]})
    for x in _j(ENTRADA, {"itens": []}).get("itens") or []:
        t = x.get("titulo") or ""
        obs.append({"casa": casa_de(x.get("url"), x.get("motor")) or "outra", "tipo": tipo_de(t), "numero": numero_de(t), "titulo": t,
                    "situacao": situacao_de(t) or "apresentado", "url": x.get("url"), "data": str(x.get("data") or x.get("recebido_em") or "")[:10]})
    return [o for o in obs if o.get("titulo")]


def _data_da_situacao(s) -> str | None:
    m = re.search(r"(20\d{2}-\d{2}-\d{2})", str(s or ""))
    return m.group(1) if m else None


def atualizar(gravar: bool = True) -> dict:
    E = _j(ESTADO, {"itens": {}})
    I = E.setdefault("itens", {})
    hoje = _agora()
    novas = movs = 0
    for o in sorted(coletar(), key=lambda x: str(x.get("data") or "")):
        k = _chave(o["casa"], o.get("numero"), o["titulo"], str(o.get("url") or ""))
        p = I.get(k)
        if not p:
            p = I[k] = {"id": k, "casa": o["casa"], "casa_nome": MOTORES.get(o["casa"], o["casa"]), "tipo": o["tipo"], "numero": o.get("numero"),
                        "titulo": o["titulo"], "entidade": o.get("entidade"), "autor": o.get("autor"), "apresentado_em": o.get("apresentado_em"),
                        "url": o.get("url"), "motivo": o.get("motivo"), "primeiro_registro": hoje, "movimentacoes": [], "gera_livro": False}
            novas += 1
        for c in ("autor", "entidade", "apresentado_em", "motivo"):
            if o.get(c) and not p.get(c):
                p[c] = o[c]
        ult = p["movimentacoes"][-1] if p["movimentacoes"] else None
        if not ult or ult.get("situacao") != o["situacao"]:
            p["movimentacoes"].append({"data": o.get("data") or hoje[:10], "situacao": o["situacao"], "setor": o.get("setor"),
                                       "url": o.get("url"), "visto_em": hoje})
            movs += 1
        p["situacao"] = p["movimentacoes"][-1]["situacao"]
        p["ultima_movimentacao"] = max(str(m.get("data") or "") for m in p["movimentacoes"])
    E["atualizado_em"] = hoje
    E["regra"] = "ato legislativo é acompanhado, não vira oportunidade nem livro (titular, 15/10/2026)"
    itens = sorted(I.values(), key=lambda x: str(x.get("ultima_movimentacao") or ""), reverse=True)
    painel = {"atualizado_em": hoje, "regra": E["regra"], "total": len(itens),
              "por_casa": _conta(itens, "casa_nome"), "por_tipo": _conta(itens, "tipo"), "itens": itens[:400]}
    if gravar:
        ESTADO.parent.mkdir(parents=True, exist_ok=True)
        ESTADO.write_text(json.dumps(E, ensure_ascii=False, indent=1), encoding="utf-8")
        PAINEL.parent.mkdir(parents=True, exist_ok=True)
        PAINEL.write_text(json.dumps(painel, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {"proposicoes": len(itens), "novas": novas, "movimentacoes_novas": movs, "por_tipo": painel["por_tipo"]}


def _conta(itens: list[dict], campo: str) -> dict:
    out: dict = {}
    for x in itens:
        out[x.get(campo) or "—"] = out.get(x.get(campo) or "—", 0) + 1
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


if __name__ == "__main__":
    print(json.dumps(atualizar(), ensure_ascii=False))
