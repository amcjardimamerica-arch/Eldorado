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
    """Monta DUAS listas independentes. A mesma empresa pode estar nas duas, com posição
    própria em cada — o que a qualifica para direcionar imposto não é o que a qualifica
    para doar do próprio caixa."""
    from .potencial_fiscal import estimar
    from .programas_sociais import programas_de
    from .ranking_duplo import avaliar_fiscal, avaliar_doadora, CRITERIOS_FISCAL, CRITERIOS_DOADORA
    base = _base_cadastral()

    # As descobertas do Piloto NÃO entram aqui: esta tela lê apenas os dois rankings
    # qualificados. Fonte recém-achada fica no posto do Piloto até ser classificada.
    def _carregar(cat: str) -> list[dict]:
        arq = ROOT / f"biblioteca_alexandria/empresas/ranking_{cat}.json"
        if not arq.exists():
            return []
        saida, vistos = [], set()
        for e in load_json(arq).get("empresas", []):
            chave = re.sub(r"[^a-z0-9]", "", str(e.get("nome") or "").lower())[:40]
            if not chave or chave in vistos:          # duplicata DENTRO da mesma lista
                continue
            vistos.add(chave)
            saida.append({**e, "_chave": chave})
        return saida

    listas = {}
    for cat, rot, avaliar in (("destinacao_tributaria", "destinação tributária", avaliar_fiscal),
                              ("patrocinio_privado", "doação e patrocínio", avaliar_doadora)):
        itens = _carregar(cat)
        for e in itens:
            e["origem"] = rot
            e["cadastro"] = _cadastro_de(e, base)
            e["potencial"] = estimar(e["cadastro"])
            e["programas"] = programas_de(e)
            e["avaliacao"] = avaliar(e)
            e["pontos_lista"] = e["avaliacao"]["pontos"]
        # ordem PRÓPRIA da lista: a nota daquela finalidade, não uma nota geral
        itens.sort(key=lambda x: (-x["pontos_lista"], -(x.get("pontos") or 0), x["nome"]))
        for n, e in enumerate(itens, 1):
            e["n_na_lista"] = n
            # a posição já não é única: cada lista tem a sua 1ª. O uid identifica a linha
            e["uid"] = f"{cat}:{n}"
            e["faixa"] = "A" if n <= 25 else "B" if n <= 60 else "C"
        listas[cat] = itens

    # quem está nas duas listas ganha a marca, com a posição em cada uma
    por_nome = {}
    for cat, itens in listas.items():
        for e in itens:
            por_nome.setdefault(e["_chave"], {})[cat] = e["n_na_lista"]
    nas_duas = {k: v for k, v in por_nome.items() if len(v) == 2}
    for cat, itens in listas.items():
        for e in itens:
            if e["_chave"] in nas_duas:
                outra = next(c for c in nas_duas[e["_chave"]] if c != cat)
                e["tambem_em"] = {"lista": outra, "posicao": nas_duas[e["_chave"]][outra]}

    todas = [e for itens in listas.values() for e in itens]
    res = {"gerado_em": now_iso(), "por_pagina": POR_PAGINA,
           "regra": "duas listas independentes, com pontuação própria; a mesma empresa pode estar nas duas",
           "listas": {cat: {"rotulo": ("destinação tributária" if cat == "destinacao_tributaria" else "doação e patrocínio"),
                            "total": len(itens),
                            "paginas": [{"n": i // POR_PAGINA + 1, "de": i + 1,
                                         "ate": min(i + POR_PAGINA, len(itens))}
                                        for i in range(0, len(itens), POR_PAGINA)],
                            "criterios": [{"chave": c[0], "peso": c[1], "rotulo": c[2], "porque": c[3]}
                                          for c in (CRITERIOS_FISCAL if cat == "destinacao_tributaria" else CRITERIOS_DOADORA)],
                            "teto": sum(c[1] for c in (CRITERIOS_FISCAL if cat == "destinacao_tributaria" else CRITERIOS_DOADORA)),
                            "confianca_media": round(sum(e["avaliacao"]["confianca"] for e in itens) / len(itens), 2) if itens else 0,
                            "criterios_sem_dado": sorted({f["rotulo"] for e in itens for f in e["avaliacao"]["falta_levantar"]})}
                      for cat, itens in listas.items()},
           "total": len(todas), "nas_duas_listas": len(nas_duas),
           "com_cnpj": sum(1 for e in todas if e["cadastro"].get("cnpj")),
           "com_cnae": sum(1 for e in todas if e["cadastro"].get("cnae_principal")),
           "com_qsa": sum(1 for e in todas if e["cadastro"].get("qsa")),
           "com_contato": sum(1 for e in todas if e["cadastro"].get("telefone") or e["cadastro"].get("email")),
           "com_site": sum(1 for e in todas if e.get("site")),
           "com_programa": sum(1 for e in todas if e.get("programas")),
           "com_potencial": sum(1 for e in todas if (e.get("potencial") or {}).get("apurou")),
           "por_origem": {("destinação tributária" if c == "destinacao_tributaria" else "doação e patrocínio"): len(i)
                          for c, i in listas.items()},
           "empresas": todas}
    write_json(SAIDA, res)
    return {k: v for k, v in res.items() if k != "empresas"}


if __name__ == "__main__":
    print(json.dumps(montar(), ensure_ascii=False, indent=2))
