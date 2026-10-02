"""LINHA DE PRODUÇÃO DE INFORMAÇÃO (titular, 02/10/2026).

Cada canal (motor ou Piloto) só COLETA. As etapas seguintes são comuns e nada é eliminado:
  (02/10: os nomes BRONZE/PRATA/OURO passaram a ser só os SELOS da esteira — src/esteira.py; aqui as etapas são:)
  COLETADO    o registro coletado, como chegou (base dados/oportunidades/oportunidades.jsonl)
  CONSOLIDADO canal canônico + contrato de dados conferido + ENTIDADE resolvida entre canais (a mesma oportunidade vista
              em vários canais vira uma entidade só, e o número de canais é a CORROBORAÇÃO)
  EM_LIVRO    a entidade chegou ao mapa ou a um livro da Biblioteca
  QUALIFICADO o livro recebeu veredito (APLICÁVEL / EM REVISÃO / NÃO APLICA) — arquivamento só manual
Registro que viola o contrato vai à FILA DE REPROCESSAMENTO (nunca ao lixo) com o plano de correção.
O LIVRO-RAZÃO (estado/linha/razao-AAAA-MM.jsonl.gz) guarda só acréscimos: cada mudança de etapa, com data e motivo.
Saída: docs/dados/linha_producao.json (funil, canais, contribuição exclusiva, corroboração, fila de reprocessamento).
"""
from __future__ import annotations

import gzip
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config/linha_producao.json"
BASE = ROOT / "dados/oportunidades/oportunidades.jsonl"
INDICE = ROOT / "estado/linha/indice.json.gz"   # compactado: o repositório já é grande
SAIDA = ROOT / "docs/dados/linha_producao.json"
VAZIAS = set("de da do das dos e a o em para com por no na nos nas um uma ao aos as os que sobre edital editais chamamento publico "
             "publica selecao processo municipio prefeitura secretaria estado governo diario oficial aviso".split())
PNCP_CHAVE = re.compile(r"pncp\.gov\.br/app/editais/(\d{14})/(\d{4})/(\d+)")


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return padrao


def sem(t) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", str(t or "").lower()) if not unicodedata.combining(c))


def termos(t) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9]{4,}", sem(t)) if w not in VAZIAS and not w.isdigit()]


def canal_canonico(fonte: str | None, cfg: dict | None = None) -> str:
    cfg = cfg or _j(CFG, {})
    f = str(fonte or "desconhecido").strip()
    return (cfg.get("canais_alias") or {}).get(f, f)


def familia(canal: str, cfg: dict | None = None) -> str:
    cfg = cfg or _j(CFG, {})
    for k, v in (cfg.get("familias") or {}).items():
        if re.search(v["padrao"], canal):
            return k
    return "outros"


def contrato(reg: dict, cfg: dict) -> str | None:
    """None = contrato cumprido; senão, o motivo (o registro vai à fila de reprocessamento, não ao lixo)."""
    c = cfg.get("contratos") or {}
    for campo in c.get("obrigatorios") or []:
        if not str(reg.get(campo) or "").strip():
            return f"sem {campo}"
    if len(str(reg.get("titulo") or "").strip()) < int(c.get("titulo_minimo", 8)):
        return "título curto demais"
    if not str(reg.get("url")).startswith("http"):
        return "URL inválida"
    if c.get("url_de_busca") and re.search(c["url_de_busca"], str(reg.get("url"))):
        return "URL de buscador (falta o site oficial)"
    return None


class _Uniao:
    def __init__(self):
        self.p = {}

    def acha(self, a):
        self.p.setdefault(a, a)
        while self.p[a] != a:
            self.p[a] = self.p[self.p[a]]
            a = self.p[a]
        return a

    def une(self, a, b):
        ra, rb = self.acha(a), self.acha(b)
        if ra != rb:
            self.p[max(ra, rb)] = min(ra, rb)


def resolver_entidades(regs: list[dict], cfg: dict) -> dict[str, str]:
    """{id do registro: id da entidade}. Blocagem por (UF, termos raros) + semelhança de termos + chave PNCP/URL."""
    try:
        from rapidfuzz import fuzz
        sim = lambda a, b: fuzz.token_set_ratio(a, b)
    except Exception:  # noqa: BLE001 — sem rapidfuzz: Jaccard dos termos
        sim = lambda a, b: 100.0 * len(set(a.split()) & set(b.split())) / max(1, len(set(a.split()) | set(b.split())))
    rc = cfg.get("resolucao_de_entidades") or {}
    lim, nraros = float(rc.get("limiar_semelhanca", 90)), int(rc.get("termos_raros_por_bloco", 2))
    df = Counter(w for r in regs for w in set(termos(r.get("titulo"))))
    U = _Uniao(); blocos = defaultdict(list); por_url, por_pncp = {}, {}
    for r in regs:
        rid = r["id"]; U.acha(rid)
        u = str(r.get("url") or "").split("#")[0].rstrip("/").lower()
        if u:
            if u in por_url:
                U.une(rid, por_url[u])
            else:
                por_url[u] = rid
        m = PNCP_CHAVE.search(str(r.get("url") or "") + " " + str(r.get("evidencia") or ""))
        if m:
            k = "/".join(m.groups())
            if k in por_pncp:
                U.une(rid, por_pncp[k])
            else:
                por_pncp[k] = rid
        ts = termos(r.get("titulo"))
        raros = sorted(set(ts), key=lambda w: (df[w], w))[:nraros]
        if len(raros) == nraros:
            blocos[(str(r.get("uf") or ""), tuple(sorted(raros)))].append((rid, " ".join(ts)))
    for itens in blocos.values():
        if len(itens) > 400:            # bloco grande demais = termos pouco distintivos; não compara tudo com tudo
            continue
        for i in range(len(itens)):
            for j in range(i + 1, len(itens)):
                if sim(itens[i][1], itens[j][1]) >= lim:
                    U.une(itens[i][0], itens[j][0])
    return {r["id"]: U.acha(r["id"]) for r in regs}


def _livros_e_mapa() -> tuple[dict[str, dict], set[str]]:
    C = _j(ROOT / "biblioteca_alexandria/fontes/motores.json", {})
    por_url = {}
    for x in C.get("motores") or []:
        for u in [x.get("pagina")] + [h.get("pagina_oficial") for h in (x.get("historico") or []) if isinstance(h, dict)]:
            if u:
                por_url[str(u).split("#")[0].rstrip("/").lower()] = x
    F = _j(ROOT / "docs/dados/fluxo_oportunidades.json", {})
    mapa = {str(i.get("url") or "").split("#")[0].rstrip("/").lower() for v in (F.get("itens_por_uf") or {}).values() for i in v}
    return por_url, mapa


def _registrar(eventos: list[dict]) -> None:
    if not eventos:
        return
    p = ROOT / f"estado/linha/razao-{date.today():%Y-%m}.jsonl.gz"
    p.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(p, "at", encoding="utf-8") as f:           # só acréscimo: nada é reescrito nem apagado
        for e in eventos:
            f.write(json.dumps(e, ensure_ascii=False, separators=(",", ":")) + "\n")


def run(regs: list[dict] | None = None, gravar: bool = True) -> dict:
    cfg = _j(CFG, {})
    if regs is None:
        regs = [json.loads(l) for l in BASE.open(encoding="utf-8") if l.strip()] if BASE.exists() else []
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    idx = {}
    if gravar and INDICE.exists():
        try:
            with gzip.open(INDICE, "rt", encoding="utf-8") as f:
                idx = json.load(f)
        except Exception:  # noqa: BLE001
            idx = {}
    livros, mapa = _livros_e_mapa()
    for r in regs:
        r["_canal"] = canal_canonico(r.get("fonte_id") or r.get("sensor"), cfg)
    ok = [r for r in regs if not contrato(r, cfg)]
    ent = resolver_entidades(ok, cfg)
    canais_da_ent = defaultdict(set)
    for r in ok:
        canais_da_ent[ent[r["id"]]].add(r["_canal"])
    eventos, fila, etapas = [], Counter(), Counter()
    for r in regs:
        motivo = contrato(r, cfg)
        u = str(r.get("url") or "").split("#")[0].rstrip("/").lower()
        if motivo:
            etapa = "REPROCESSAR"; fila[motivo] += 1
        else:
            lv = livros.get(u)
            etapa = ("QUALIFICADO" if lv and (lv.get("qualificacao") or {}).get("veredito") else
                     "EM_LIVRO" if lv or u in mapa else "CONSOLIDADO")
        etapas[etapa] += 1
        ant = idx.get(r["id"])
        if ant != etapa:
            eventos.append({"em": agora, "id": r["id"], "de": ant or "—", "para": etapa, "canal": r["_canal"],
                            **({"motivo": motivo} if motivo else {}), **({"entidade": ent.get(r["id"])} if r["id"] in ent else {})})
            idx[r["id"]] = etapa
    # contribuição de cada canal: entidades que SÓ ele trouxe, corroboradas e validadas como oportunidade real
    import glob as _g
    validas = set()
    for f in _g.glob(str(ROOT / "dados/oportunidades/validacao_mapa/validacao_*.json")):
        for d in (_j(Path(f), {}).get("itens") or []):
            if str(d.get("decisao") or "").startswith(("valida", "arquivada")):
                validas.add(str(d.get("url") or "").split("#")[0].rstrip("/").lower())
    por_canal = defaultdict(lambda: {"registros": 0, "entidades": set(), "exclusivas": 0, "corroboradas": 0, "validadas": set()})
    for r in ok:
        e = ent[r["id"]]; c = por_canal[r["_canal"]]
        c["registros"] += 1; c["entidades"].add(e)
        if str(r.get("url") or "").split("#")[0].rstrip("/").lower() in validas:
            c["validadas"].add(e)
    for e, cs in canais_da_ent.items():
        for c in cs:
            if len(cs) == 1:
                por_canal[c]["exclusivas"] += 1
            else:
                por_canal[c]["corroboradas"] += 1
    canais = sorted([{"canal": k, "familia": familia(k, cfg), "registros": v["registros"], "entidades": len(v["entidades"]),
                      "exclusivas": v["exclusivas"], "corroboradas": v["corroboradas"], "validadas_como_reais": len(v["validadas"])}
                     for k, v in por_canal.items()], key=lambda c: (-c["validadas_como_reais"], -c["entidades"]))
    n_ent = len(canais_da_ent)
    out = {"em": agora, "regra": __doc__.split("Saída")[0].strip(),
           "funil": {"coletados": len(regs), "oportunidades_distintas": n_ent, "entidades_em_2_ou_mais_canais": sum(1 for v in canais_da_ent.values() if len(v) > 1),
                     "etapas": dict(etapas), "fila_de_reprocessamento": dict(fila)},
           "canais": canais, "familias": dict(Counter(c["familia"] for c in canais)),
           "corroboradas": sorted([{"entidade": e, "canais": sorted(cs)} for e, cs in canais_da_ent.items() if len(cs) > 1],
                                  key=lambda z: -len(z["canais"]))[:40],
           "eventos_no_livro_razao": len(eventos)}
    if gravar:
        _registrar(eventos)
        INDICE.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(INDICE, "wt", encoding="utf-8") as f:
            json.dump(idx, f, ensure_ascii=False, separators=(",", ":"))
        SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    o = run()
    print(json.dumps({"funil": o["funil"], "canais": o["canais"][:12]}, ensure_ascii=False, indent=1))
