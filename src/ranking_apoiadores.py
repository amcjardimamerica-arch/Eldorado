"""RANKING DE APOIADORES — ampliado, pontuado e paginado de 100 em 100.

Junta três origens numa lista só, ordenada por pontuação:
  • as 100 da destinação tributária (base ICMS/Lucro Real)
  • as 100 do patrocínio privado
  • tudo o que o Piloto descobre no radar de captação

Cada empresa carrega, quando houver: site, CNPJ, CNAE principal e secundários, quadro
societário (QSA), contatos (telefone, e-mail), porte, situação e o que sustenta a
pontuação. Os dados cadastrais vêm do que já está guardado em dados/empresas/ (cadastro
da Receita coletado pelo motor de empresas) e do radar; o que faltar fica marcado como
"a completar", nunca inventado.

Saída: docs/dados/ranking_apoiadores.json — páginas de 100, com o total real.
"""
from __future__ import annotations

import gzip
import json
import re
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json

SAIDA = ROOT / "docs/dados/ranking_apoiadores.json"
POR_PAGINA = 100


def _so_digitos(s: str) -> str:
    return re.sub(r"\D", "", s or "")


def _base_cadastral() -> dict:
    """CNPJ → cadastro (Receita) do que o motor de empresas já coletou."""
    arq = ROOT / "dados/empresas/base_empresas.jsonl.gz"
    if not arq.exists():
        return {}
    out = {}
    for l in gzip.open(arq, "rt", encoding="utf-8"):
        if not l.strip():
            continue
        try:
            e = json.loads(l)
        except Exception:
            continue
        c = _so_digitos(e.get("cnpj") or "")
        if c:
            out[c] = e
    return out


def _cadastro_de(e: dict, base: dict) -> dict:
    """Extrai site, CNPJ, CNAEs, QSA e contatos do que existe; o que falta fica None."""
    cnpj = _so_digitos(e.get("cnpj") or "")
    b = base.get(cnpj) or {}
    cad = (b.get("cadastro") or {}) if isinstance(b.get("cadastro"), dict) else {}
    site = e.get("site")
    if not site:
        s = b.get("site")
        if isinstance(s, dict) and s.get("dominio"):
            site = "https://" + str(s["dominio"])
        elif isinstance(s, str) and "." in s:
            site = s if s.startswith("http") else "https://" + s
    cnae_p = cad.get("cnae_principal") or cad.get("cnae_fiscal_descricao") or cad.get("atividade_principal") or None
    if isinstance(cnae_p, list) and cnae_p:
        cnae_p = (cnae_p[0] or {}).get("text") or (cnae_p[0] or {}).get("descricao")
    cnae_cod = cad.get("cnae_codigo")
    secund = cad.get("cnaes_secundarios") or cad.get("atividades_secundarias") or []
    if isinstance(secund, list):
        secund = [(x.get("descricao") or x.get("text") or str(x))[:70] for x in secund if x][:6]
    qsa = cad.get("qsa") or cad.get("socios") or []
    if isinstance(qsa, list):
        qsa = [{"nome": (s.get("nome") or s.get("nome_socio") or "")[:60],
                "qualificacao": (s.get("qualificacao") or s.get("qual") or s.get("qualificacao_socio") or "")[:50]}
               for s in qsa if isinstance(s, dict)][:8]
    tel = cad.get("telefone") or cad.get("ddd_telefone_1") or None
    email = cad.get("email") or None
    falta = [k for k, v in (("site", site), ("cnpj", cnpj), ("cnae", cnae_p), ("qsa", qsa), ("contato", tel or email)) if not v]
    return {"site": site, "cnpj": e.get("cnpj") or (cad.get("cnpj") if cad else None),
            "razao_social": cad.get("razao_social"), "nome_fantasia": cad.get("nome_fantasia"),
            "cnae_principal": cnae_p, "cnae_codigo": cnae_cod, "cnaes_secundarios": secund, "qsa": qsa,
            "natureza_juridica": cad.get("natureza_juridica"), "endereco": " ".join(str(cad.get(x) or "") for x in ("logradouro", "bairro")).strip() or None,
            "telefone": tel, "email": email,
            "municipio": cad.get("municipio"), "uf": cad.get("uf") or e.get("uf"),
            "porte": cad.get("porte") or cad.get("codigo_porte"), "situacao": cad.get("descricao_situacao_cadastral") or cad.get("situacao"),
            "capital_social": cad.get("capital_social"), "abertura": cad.get("data_inicio_atividade") or cad.get("abertura"),
            "a_completar": falta}


def montar() -> dict:
    base = _base_cadastral()
    itens, vistos = [], set()

    def _add(nome, pontos, origem, extra):
        chave = re.sub(r"[^a-z0-9]", "", (nome or "").lower())[:40]
        if not chave or chave in vistos:
            return
        vistos.add(chave)
        itens.append({"nome": nome[:120], "pontos": pontos or 0, "origem": origem, **extra})

    for cat, rot in (("destinacao_tributaria", "destinação tributária"), ("patrocinio_privado", "patrocínio privado")):
        arq = ROOT / f"biblioteca_alexandria/empresas/ranking_{cat}.json"
        if not arq.exists():
            continue
        for e in load_json(arq).get("empresas", []):
            _add(e.get("nome"), e.get("pontos"), rot,
                 {"por": e.get("por") or [], "cnpj": e.get("cnpj"), "icms_goias": e.get("icms_goias"),
                  "programa": e.get("programa"), "apoia": e.get("apoia"), "via_de_entrada": e.get("via_de_entrada"),
                  "incentivos": e.get("incentivos"), "classe": e.get("classe"), "site": e.get("site")})
    rad = load_json(ROOT / "dados/empresas/radar_piloto.json") if (ROOT / "dados/empresas/radar_piloto.json").exists() else {}
    for e in (rad.get("empresas") or {}).values():
        # descoberta do Piloto pontua pelo que se sabe: sinal declarado, ESG, edital visto, recorrência
        p = 4 + 3 * len(e.get("angulos") or []) + (6 if (e.get("esg") or {}).get("tem_relatorio") else 0) \
            + (8 if (e.get("editais") or {}).get("abertos") else 0) + (5 if (e.get("editais") or {}).get("anteriores") else 0) \
            + (2 * min(3, (e.get("vezes_vista") or 1) - 1)) + (6 if e.get("marcador") == "concluido" else 0)
        _add(e.get("nome"), p, "radar do Piloto",
             {"por": [f"descoberto pelo Piloto ({', '.join(e.get('angulos') or [])})"], "site": e.get("site"),
              "marcador_pesquisa": e.get("marcador"), "nivel": e.get("nivel"), "esg": e.get("esg"),
              "editais": e.get("editais"), "leitura": (e.get("porque") or "")[:140], "classe": "radar"})
    fon = ROOT / "estado/piloto/fontes_descobertas.json"
    if fon.exists():
        for dom, e in (load_json(fon).get("itens") or {}).items():
            if not e.get("tipos"):
                continue
            # pontuação da prospecção: tipo de recurso vale mais que menção solta
            p = (5 * len(e["tipos"]) + (12 if "edital_proprio" in e["tipos"] else 0)
                 + (8 if "incentivo_fiscal" in e["tipos"] else 0)
                 + (5 if e.get("nivel") in ("local", "estadual") else 0)
                 + min(6, 2 * ((e.get("vezes_vista") or 1) - 1)))
            _add(e.get("nome") or dom, p, "prospecção do Piloto",
                 {"por": [f"{t}: {(e.get('validacao') or {}).get('tipos', {}).get(t, {}).get('pagina', '')}"
                          for t in e["tipos"]],
                  "site": e.get("site"), "nivel": e.get("nivel"), "tipos_de_recurso": e["tipos"],
                  "portas": e.get("portas"), "virou_motor": e.get("motor"),
                  "ficha": e.get("na_biblioteca"), "classe": "prospecção",
                  "leitura": f"descoberta pelo Piloto em {e.get('descoberto_em')}: oferece {', '.join(e['tipos'])}"})
    for e in itens:
        e.update({"cadastro": _cadastro_de(e, base)})
        if not e.get("site"):
            e["site"] = e["cadastro"].get("site")
    itens.sort(key=lambda x: (-(x.get("pontos") or 0), x["nome"]))
    for i, e in enumerate(itens, 1):
        e["posicao"] = i
        e["faixa"] = "A" if i <= 50 else "B" if i <= 150 else "C" if i <= 300 else "D"
    paginas = [{"de": i + 1, "ate": min(i + POR_PAGINA, len(itens))} for i in range(0, len(itens), POR_PAGINA)]
    res = {"gerado_em": now_iso(), "total": len(itens), "por_pagina": POR_PAGINA, "paginas": paginas,
           "regra": "uma lista só, ordenada por pontuação: destinação tributária + patrocínio privado + radar do Piloto; "
                    "os dados cadastrais (CNPJ, CNAE, QSA, contatos) vêm do que já foi coletado — o que falta fica em 'a_completar', nunca inventado",
           "com_cnpj": sum(1 for e in itens if e["cadastro"].get("cnpj")),
           "com_cnae": sum(1 for e in itens if e["cadastro"].get("cnae_principal")),
           "com_qsa": sum(1 for e in itens if e["cadastro"].get("qsa")),
           "com_contato": sum(1 for e in itens if e["cadastro"].get("telefone") or e["cadastro"].get("email")),
           "com_site": sum(1 for e in itens if e.get("site")),
           "por_origem": {o: sum(1 for e in itens if e["origem"] == o) for o in {e["origem"] for e in itens}},
           "empresas": itens}
    write_json(SAIDA, res)
    return {k: v for k, v in res.items() if k != "empresas"}


if __name__ == "__main__":
    print(json.dumps(montar(), ensure_ascii=False, indent=2))
