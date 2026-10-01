"""LIVROS DE LEIS (titular, 01/10) — parametrizam o Farol de Alexandria.

Cada lei ou norma da Biblioteca (biblioteca_alexandria/leis/<tema>/<tipo>/*.json) vira um livro com o que ela é e O QUE
ELA PARAMETRIZA: as áreas e os tipos de oportunidade que regula e os livros de oportunidade sob ela (Goiás primeiro).
Só dados — nenhum arquivo anexado (o texto integral, quando há, continua no acervo e é citado pelo caminho).
Saída compacta: biblioteca_alexandria/livros/leis.json · resumo para o painel: docs/dados/livros_leis.json
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEIS = ROOT / "biblioteca_alexandria/leis"
CAT = ROOT / "biblioteca_alexandria/fontes/motores.json"
SAIDA = ROOT / "biblioteca_alexandria/livros/leis.json"
PAINEL = ROOT / "docs/dados/livros_leis.json"
# tema da lei → o que ela parametriza no Farol (áreas e tipos de oportunidade dos livros)
PARAMETRIZA = {
    "parcerias_e_fomento": {"areas": "*", "tipos": ["Chamamento público", "Edital", "Credenciamento", "Fundo", "Emenda", "Doação/patrocínio"],
                            "regra": "MROSC: chamamento, termos de colaboração e fomento, emendas e doações a OSC"},
    "assistencia_social": {"areas": ["Assistência social", "Pessoa idosa", "Criança e adolescente"], "tipos": "*", "regra": "SUAS, CEBAS e fundos de assistência"},
    "crianca_adolescente": {"areas": ["Criança e adolescente"], "tipos": "*", "regra": "ECA e Fundos da Infância e da Adolescência"},
    "pessoa_idosa": {"areas": ["Pessoa idosa"], "tipos": "*", "regra": "Estatuto e Fundos da Pessoa Idosa"},
    "cultura": {"areas": ["Cultura"], "tipos": "*", "regra": "Rouanet, PNAB, Goyazes e fomento cultural"},
    "esporte": {"areas": ["Esporte"], "tipos": "*", "regra": "Lei de Incentivo ao Esporte"},
    "saude": {"areas": ["Saúde"], "tipos": "*", "regra": "PRONON, PRONAS/PCD e saúde filantrópica"},
    "incentivos_fiscais": {"areas": "*", "tipos": ["Incentivo fiscal", "Fundo"], "regra": "dedução de imposto de renda e ICMS para destinação"},
    "tributario": {"areas": "*", "tipos": ["Incentivo fiscal", "Fundo"], "regra": "destinação tributária"},
    "destinacao_judicial": {"areas": "*", "tipos": ["Destinação judicial"], "regra": "prestação pecuniária, transação penal e TAC"},
    "gestao_e_controle": {"areas": "*", "tipos": ["Chamamento público", "Edital", "Fundo", "Emenda", "Credenciamento"],
                          "regra": "prestação de contas, controle e transparência das parcerias"},
    "constituicao_e_direitos": {"areas": "*", "tipos": "*", "regra": "fundamento constitucional e direitos que as políticas sociais concretizam"},
    "geral": {"areas": "*", "tipos": "*", "regra": "referência geral para associações"},
    "eleitoral": {"areas": "*", "tipos": "*", "regra": "calendário eleitoral (defesos que suspendem transferências e programas)"},
}


def _cabe(livro: dict, p: dict) -> bool:
    a, t = p.get("areas"), p.get("tipos")
    return (a == "*" or livro.get("objeto_area") in a) and (t == "*" or livro.get("tipo_objeto") in t)


def montar() -> dict:
    cat = json.loads(CAT.read_text(encoding="utf-8")).get("motores", []) if CAT.exists() else []
    livros = []
    for f in sorted(LEIS.glob("**/*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        tema = str(d.get("tema") or (f.parent.parent.name if f.parent.parent != LEIS else f.parent.name) or "geral")
        if tema not in PARAMETRIZA:
            tema = f.relative_to(LEIS).parts[0] if f.relative_to(LEIS).parts[0] in PARAMETRIZA else "geral"
        p = PARAMETRIZA.get(tema) or PARAMETRIZA.get(f.parent.parent.name) or {"areas": "*", "tipos": [], "regra": "referência geral"}
        rel = [x for x in cat if _cabe(x, p)]
        rel.sort(key=lambda x: (x.get("geo") != "GO", x.get("geo") != "BR", x.get("geo") != "INT", str(x.get("nome_classificado"))))
        texto = d.get("arquivo_texto")
        livros.append({"id": d.get("id") or f.stem, "nome": d.get("titulo") or f.stem, "esfera": d.get("esfera"), "tipo": d.get("tipo"), "tema": tema,
                       "url_oficial": d.get("url_oficial"), "situacao": d.get("status"), "conferir_em": d.get("conferir_em"),
                       "texto_no_acervo": texto if texto and texto != "None" else None,
                       "parametriza": {"regra": p["regra"], "areas": p["areas"], "tipos": p["tipos"]},
                       "livros_de_oportunidade": len(rel), "em_goias": sum(1 for x in rel if x.get("geo") == "GO"),
                       "exemplos": [x.get("id") for x in rel[:12]]})
    out = {"gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "regra": __doc__.split("Saída")[0].strip(), "livros": livros}
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    PAINEL.write_text(json.dumps({"gerado_em": out["gerado_em"], "total": len(livros), "livros": livros}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {"livros_de_leis": len(livros), "por_tema": dict(Counter(x["tema"] for x in livros)), "sem_oportunidade": sum(1 for x in livros if not x["livros_de_oportunidade"])}


if __name__ == "__main__":
    print(json.dumps(montar(), ensure_ascii=False, indent=1))
