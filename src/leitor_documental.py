"""LEITOR DOCUMENTAL — os 12 itens saem do edital, não da notícia (titular, 03/10/2026).

Notícia é indício. Este módulo (1) monta a fila de livros de Goiás que ainda não têm base documental, (2) valida o
resultado dos agentes de navegador (Claude no Chrome) que abrem o site oficial e os arquivos do edital, e (3) aplica o que
passou na validação: edições com documento oficial em dados/coleta_3_anos/entrada/, pareceres e dispensas por livro em
dados/coleta_3_anos/ouro/pareceres_go.json e regimes permanentes documentados em ouro_regime.json.

Resultado do agente (entrada_manual/leitor_documental/resultado_<familia>.json): ver config/leitor_documental.json e
skills/comum/leitor_documental/SKILL.md. Item sem trecho literal e sem documento oficial NÃO conta (vira indício).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config/leitor_documental.json"
ENTRADA_AGENTE = ROOT / "entrada_manual/leitor_documental"
SAIDA = ROOT / "dados/coleta_3_anos"
PARECERES = SAIDA / "ouro/pareceres_go.json"
REGIME = SAIDA / "ouro/ouro_regime.json"
EDICOES = SAIDA / "entrada/go_zz_documental.json"
_DOC = re.compile(r"\.(pdf|docx?|odt|xlsx?)(\?|#|$)|/wp-content/uploads/|/download/|/arquivos?/|/anexos?/|/api/", re.I)


def cfg() -> dict:
    return json.loads(CFG.read_text(encoding="utf-8"))


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return padrao


def fila_go() -> list[dict]:
    """Livros de Goiás sem ouro, com o que já se sabe e o que falta (entrada dos agentes)."""
    res = _j(ROOT / "docs/dados/relatorios_livros.json", {}).get("livros") or []
    out = []
    for l in res:
        if l.get("bloco") != "GO" or l.get("selo") == "ouro":
            continue
        r = _j(SAIDA / f"relatorios/{l['id']}.json", {})
        out.append({"id": l["id"], "livro": l.get("livro"), "orgao": r.get("orgao"), "situacao": l.get("situacao"),
                    "edicoes_conhecidas": [{"mes": e["mes"], "pagina_oficial": e.get("pagina_oficial")} for e in r.get("edicoes") or []],
                    "falta": "edições de anos distintos com documento oficial e os 12 itens lidos no edital"})
    return out


def validar_livro(v: dict) -> tuple[dict, list[str]]:
    """Separa o que vale (documento oficial + trecho literal) do que é só indício. Devolve (livro limpo, rejeições)."""
    c = cfg(); rej: list[str] = []
    ok_tipos = set(c["fontes_validas"]); itens_ok = set(c["itens"])
    ver = v.get("veredito")
    if ver not in c["veredito"]:
        rej.append(f"veredito inválido: {ver}")
    ed_ok = []
    for e in v.get("edicoes") or []:
        docs = [d for d in e.get("documentos") or [] if d.get("url") and d.get("tipo") in ok_tipos]
        ano = str(e.get("ano") or str(e.get("inicio") or "")[:4])
        if not docs or not re.fullmatch(r"20\d{2}", ano):
            rej.append(f"edição {e.get('mes') or ano} sem documento oficial ou sem ano: só indício"); continue
        urls = {d["url"] for d in docs}
        itens, ind = {}, {}
        for k, it in (e.get("itens") or {}).items():
            if k not in itens_ok:
                continue
            if isinstance(it, dict) and it.get("valor") and len(str(it.get("trecho") or "")) >= 12 and it.get("documento") in urls:
                itens[k] = {"estado": "confirmado", "valor": str(it["valor"])[:400], "trecho": str(it["trecho"])[:300],
                            "fonte": f"documento: {it['documento']}" + (f", p. {it['pagina']}" if it.get("pagina") else "")}
            else:
                ind[k] = it
        if ind:
            rej.append(f"edição {e.get('mes') or ano}: itens sem trecho/documento viram indício: {', '.join(ind)}")
        princ = next((d["url"] for d in docs if d["tipo"] == "edital"), docs[0]["url"])
        ed_ok.append({"ano": ano, "titulo": str(e.get("titulo") or "")[:200], "abertura": e.get("inicio"), "encerramento": e.get("fim"),
                      "pagina_oficial": princ, "valor": (itens.get("Valor") or {}).get("valor"), "trecho": (e.get("titulo") or "")[:200],
                      "itens12": itens, "documentos": [d["url"] for d in docs]})
    if ver == "ouro" and len({e["ano"] for e in ed_ok}) < 2:
        rej.append("veredito ouro sem edições em 2 anos distintos com documento oficial: rebaixado para pendente"); ver = "pendente"
    if ver == "ouro_regime" and not (v.get("base_legal") and len(ed_ok) + len(v.get("evidencias_regime") or []) >= 2):
        rej.append("ouro_regime exige base legal e ao menos 2 evidências de anos distintos: rebaixado para pendente"); ver = "pendente"
    if ver == "inaplicavel" and not (v.get("motivo_inaplicavel") and len(str(v["motivo_inaplicavel"])) >= 30):
        rej.append("inaplicável sem justificativa/prova: rebaixado para pendente"); ver = "pendente"
    if ver == "edicao_unica" and not (v.get("busca_realizada") and len(str(v["busca_realizada"])) >= 40 and ed_ok):
        rej.append("edicao_unica exige a edição lida no documento e o relato da busca por outros anos: rebaixado para pendente"); ver = "pendente"
    if not str(v.get("parecer") or "").strip():
        rej.append("sem parecer")
    return {**{k: v.get(k) for k in ("livro_mae", "site_oficial", "base_legal", "evidencias_regime", "motivo_inaplicavel", "tipo_inaplicavel",
                                   "itens_dispensados", "itens_pendentes", "parecer", "busca_realizada")}, "veredito": ver, "edicoes": ed_ok}, rej


def aplicar(arquivos: list[Path] | None = None) -> dict:
    """Valida os resultados dos agentes e grava edições, pareceres e regimes (idempotente: o que está nos arquivos substitui)."""
    arquivos = arquivos or sorted(ENTRADA_AGENTE.glob("resultado_*.json"))
    pareceres, regimes, edicoes, rejeicoes = {}, {}, {}, {}
    for a in arquivos:
        for lid, v in (_j(a, {}) or {}).items():
            if not isinstance(v, dict):
                continue
            limpo, rej = validar_livro(v)
            pareceres[lid] = limpo | {"fonte_resultado": a.name}
            if rej:
                rejeicoes[lid] = rej
            if limpo["edicoes"]:
                edicoes[lid] = {"edicoes": limpo["edicoes"]}
            if limpo["veredito"] == "ouro_regime":
                regimes[lid] = {"base_legal": limpo["base_legal"], "evidencias": limpo.get("evidencias_regime") or [], "parecer": limpo["parecer"]}
    PARECERES.parent.mkdir(parents=True, exist_ok=True)
    PARECERES.write_text(json.dumps(pareceres, ensure_ascii=False, indent=1), encoding="utf-8")
    REGIME.write_text(json.dumps(regimes, ensure_ascii=False, indent=1), encoding="utf-8")
    EDICOES.write_text(json.dumps(edicoes, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"livros": len(pareceres), "com_edicoes": len(edicoes), "regimes": len(regimes), "rejeicoes": len(rejeicoes)}


def pareceres() -> dict:
    return _j(PARECERES, {})


def regimes() -> dict:
    return _j(REGIME, {})
