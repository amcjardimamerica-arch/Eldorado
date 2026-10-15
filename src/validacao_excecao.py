"""VALIDAÇÃO POR EXCEÇÃO (titular, 15/10/2026) — etapa 7 do comando único: o que tem os 12 itens comprovados no
documento oficial segue para o Farol sem fila humana; a conferência humana fica só com as exceções.

Candidata: certidão do Cartório com link oficial e nenhum item faltando (12 de 12 certificados ou dispensados no
documento). TRAVA: a passagem automática só é ligada quando a avaliação do Cartório contra o gabarito humano
(estado/cartorio/avaliacao/resultado.json) mostra acerto geral ≥ REGUA_PCT — antes disso a lista é produzida e as
candidatas vão à frente da fila humana, mas nada é validado sozinho.
Saídas: estado/comando/validacao_excecao.json (sempre) e, com a trava aberta,
dados/oportunidades/validacao_mapa/validacao_0001-excecao.json (mesmo formato da validação, decisão "valida").
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CERT = ROOT / "estado/cartorio/certidoes.json"
AVAL = ROOT / "estado/cartorio/avaliacao/resultado.json"
SAIDA = ROOT / "estado/comando/validacao_excecao.json"
VALIDACAO = ROOT / "dados/oportunidades/validacao_mapa/validacao_0001-excecao.json"
REGUA_PCT = 85.0


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao


def candidatas() -> list[dict]:
    C = (_j(CERT, {}) or {}).get("certidoes") or {}
    out = []
    for k, c in C.items():
        if not isinstance(c, dict) or not c.get("link_oficial") or c.get("ainda_faltam"):
            continue
        out.append({"id": str(k).split(":", 1)[-1], "chave": k, "titulo": str(c.get("titulo") or "")[:200], "url": c.get("link_oficial"),
                    "tipo": c.get("tipo"), "certificado_em": c.get("em")})
    return out


def run() -> dict:
    aval = _j(AVAL, {}) or {}
    acerto = ((aval.get("geral") or {}).get("acerto_pct"))
    aberta = isinstance(acerto, (int, float)) and acerto >= REGUA_PCT
    cs = candidatas()
    agora = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    res = {"em": agora, "regua_pct": REGUA_PCT, "acerto_do_cartorio_pct": acerto, "trava_aberta": aberta, "candidatas": len(cs),
           "acao": ("validadas por exceção e enviadas ao Farol" if aberta else
                    f"trava fechada: acerto do Cartório {acerto}% < {REGUA_PCT}% — candidatas vão à frente da conferência humana"),
           "itens": cs}
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    if aberta and cs:
        VALIDACAO.parent.mkdir(parents=True, exist_ok=True)
        VALIDACAO.write_text(json.dumps({"regra": __doc__.split("Saídas:")[0].strip(), "gerado_em": agora,
                                         "itens": [{"id": c["id"], "titulo": c["titulo"], "url": c["url"], "decisao": "valida",
                                                    "motivo": "validação por exceção: 12 de 12 itens comprovados no documento oficial"} for c in cs]},
                                        ensure_ascii=False, indent=1), encoding="utf-8")
    return {k: res[k] for k in ("trava_aberta", "acerto_do_cartorio_pct", "candidatas", "acao")}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False))
