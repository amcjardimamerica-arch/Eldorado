"""DESCARTE PELAS ESTANTES E MELHORIA DO MOTOR DE ORIGEM (titular, 02/10/2026).

As Estantes de Investigação Bronze e Prata podem encaminhar a oportunidade para o DESCARTE. Cada descarte:
  1. marca o livro DESCARTADO (nada é apagado; fica no livro-razão);
  2. descobre o(s) MOTOR(ES) que indicaram a oportunidade (índice do Espião, chave do livro, canal dos registros da base);
  3. grava a RESTRIÇÃO aprendida desse motor (config/restricoes_aprendidas.json): o endereço canônico e a assinatura do
     título — para o motor NÃO OBTER DE NOVO aquele dado, que passa a ser RUÍDO (o motor conta como ruído filtrado);
  4. vira exemplo NEGATIVO (ruído) para a rede neural.
Pedidos de descarte chegam de fora (estado/esteira/descartar.json: [{"livro", "motivo", "por"}]). O sistema PROPÕE o
descarte dos livros parados na estante há 30 dias ou mais sem informação nova, mas não descarta sozinho.
Saída: docs/dados/descartes.json
"""
from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "biblioteca_alexandria/fontes/motores.json"
PEDIDOS = ROOT / "estado/esteira/descartar.json"
RESTR = ROOT / "config/restricoes_aprendidas.json"
SAIDA = ROOT / "docs/dados/descartes.json"
ESTANTES = ("investigacao_bronze", "investigacao_prata")
VAZIAS = set("de da do das dos e a o as os para por com em no na nos nas um uma ao aos à às edital chamamento público publico nº n".split())


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return padrao


def assinatura(titulo) -> str:
    """As 8 primeiras palavras significativas do título, sem acento e sem números — o 'jeito' daquele ruído."""
    t = unicodedata.normalize("NFKD", str(titulo or "")).encode("ascii", "ignore").decode().lower()
    ps = [p for p in re.findall(r"[a-z]{3,}", t) if p not in VAZIAS]
    return " ".join(ps[:8])


_CACHE: dict = {}


def restricoes() -> dict:
    """Em memória enquanto o arquivo não muda (a linha consulta 35 mil vezes por ciclo)."""
    try:
        mt = RESTR.stat().st_mtime
    except OSError:
        mt = None
    if _CACHE.get("arq") != str(RESTR) or _CACHE.get("mt") != mt:
        _CACHE.update({"arq": str(RESTR), "mt": mt, "R": _j(RESTR, {"versao": 1, "regra": __doc__.split("Pedidos")[0].strip(), "itens": []})})
    return _CACHE["R"]


def e_ruido(reg: dict, motor: str | None = None, R: dict | None = None) -> dict | None:
    """O registro bate com uma restrição aprendida do motor? (endereço canônico ou assinatura do título)"""
    from .integridade import url_canonica
    R = R or restricoes(); m = motor or reg.get("fonte_id")
    if not R.get("itens"):
        return None
    u = url_canonica(reg.get("url")); a = assinatura(reg.get("titulo"))
    for it in R.get("itens") or []:
        if it.get("motor") not in (m, "*"):
            continue
        if (it.get("url") and it["url"] == u) or (it.get("assinatura") and len(it["assinatura"].split()) >= 4 and it["assinatura"] == a):
            return it
    return None


def motores_de_origem(x: dict) -> list[str]:
    from .integridade import url_canonica
    ms = set((x.get("indexacao") or {}).get("motores") or []) | set((x.get("chave_acionamento") or {}).get("motores") or [])
    urls = {url_canonica(u) for u in [x.get("pagina")] + [h.get("pagina_oficial") for h in (x.get("historico") or []) if isinstance(h, dict)] if u}
    base = ROOT / "dados/oportunidades/oportunidades.jsonl"
    if base.exists() and urls:
        with base.open(encoding="utf-8") as fh:
            for l in fh:
                try:
                    r = json.loads(l)
                except ValueError:
                    continue
                if url_canonica(r.get("url")) in urls and r.get("fonte_id"):
                    ms.add(r["fonte_id"])
    return sorted(ms) or ["*"]


def descartar(x: dict, motivo: str, por: str, R: dict, hoje: str) -> list[dict]:
    from .integridade import url_canonica
    x["qualificacao"] = {**(x.get("qualificacao") or {}), "veredito": "DESCARTADA", "motivo": motivo, "por": por, "em": hoje,
                         "veio_da_estante": (x.get("esteira") or {}).get("estante")}
    x.setdefault("esteira", {})["estante"] = "descartada"
    novas = []
    urls = [url_canonica(u) for u in [x.get("pagina")] + [h.get("pagina_oficial") for h in (x.get("historico") or []) if isinstance(h, dict)] if u]
    for m in motores_de_origem(x):
        for u in dict.fromkeys(urls):
            novas.append({"motor": m, "url": u, "assinatura": assinatura(x.get("nome_classificado") or x.get("programa")),
                          "motivo": motivo, "livro": x.get("id"), "titulo": str(x.get("nome_classificado") or x.get("programa"))[:160], "em": hoje, "por": por})
    chaves = {(i.get("motor"), i.get("url"), i.get("assinatura")) for i in R["itens"]}
    novas = [n for n in novas if (n["motor"], n["url"], n["assinatura"]) not in chaves]
    R["itens"] += novas
    return novas


def run(hoje: str | None = None, gravar: bool = True) -> dict:
    hoje = hoje or date.today().isoformat()
    C = _j(CAT, {}); por_id = {x.get("id"): x for x in C.get("motores") or []}
    R = restricoes(); pedidos = _j(PEDIDOS, []); feitos, recusados, novas = [], [], []
    for p in pedidos if isinstance(pedidos, list) else []:
        x = por_id.get(p.get("livro"))
        if not x:
            recusados.append({**p, "por_que": "livro não encontrado"}); continue
        if (x.get("esteira") or {}).get("estante") not in ESTANTES:
            recusados.append({**p, "por_que": f"só se descarta pelas Estantes de Investigação (está em {(x.get('esteira') or {}).get('estante')})"}); continue
        n = descartar(x, p.get("motivo") or "descartado pela estante", p.get("por") or "titular", R, hoje)
        feitos.append({"livro": x["id"], "nome": x.get("nome_classificado"), "restricoes_novas": len(n)}); novas += n
    propostos = []
    for x in C.get("motores") or []:
        e = x.get("esteira") or {}
        if e.get("estante") in ESTANTES:
            ult = max([str(h.get("em") or "") for h in (e.get("historico") or []) if isinstance(h, dict)] + [str(e.get("avaliado_em") or "")])
            try:
                parado = (date.fromisoformat(hoje) - date.fromisoformat(ult[:10])).days
            except ValueError:
                parado = 0
            if parado >= 30:
                propostos.append({"livro": x["id"], "nome": x.get("nome_classificado"), "estante": e["estante"], "parado_ha_dias": parado})
    R["atualizado_em"] = hoje
    out = {"em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "regra": __doc__.split("Saída")[0].strip(), "hoje": len(feitos),
           "descartados_hoje": feitos, "recusados": recusados, "propostos_para_descarte": propostos[:200], "restricoes_ativas": len(R["itens"]),
           "restricoes_por_motor": dict(Counter(i["motor"] for i in R["itens"])),
           "descartados_total": sum(1 for x in C.get("motores") or [] if (x.get("qualificacao") or {}).get("veredito") == "DESCARTADA")}
    if gravar:
        if feitos:
            CAT.write_text(json.dumps(C, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
            RESTR.write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
            PEDIDOS.write_text("[]", encoding="utf-8")              # pedido atendido sai da fila (fica no livro-razão)
        SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return {k: out[k] for k in ("hoje", "restricoes_ativas", "descartados_total")} | {"propostos": len(propostos), "recusados": len(recusados)}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=1))
