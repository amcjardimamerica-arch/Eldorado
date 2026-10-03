"""REDE NEURAL DA LINHA DE PRODUÇÃO (titular, 02/10/2026) — Python puro, sem dependência nova, sem GPU.

O que faz: estima a probabilidade de um registro ser OPORTUNIDADE REAL para OSC. É APOIO, nunca filtro (identificar
primeiro, qualificar depois): ordena a fila de validação, dá a nota dos livros e aponta rótulos suspeitos.

Arquitetura: rede de 1 camada oculta (ReLU) sobre entradas esparsas; saída sigmoide; Adam; pesos por classe.
Entradas (técnicas de referência no GitHub):
  · TEXTO — palavras e pares de palavras do título e da evidência, por *feature hashing* (2^13 posições);
  · SUPERVISÃO FRACA (snorkel-team/snorkel) — as regras atuais do sistema viram "rotuladores": veredito e regra de
    restrição dos livros (regras_restricao.avaliar), sinais de OSC, de abertura e de prazo, link oficial, família do canal;
  · CORROBORAÇÃO — quantos canais viram a mesma entidade (linha_producao).
Rótulos: as decisões da validação individual (válida/arquivada = 1; descartada = 0; pendente = sem rótulo).
Avaliação: validação cruzada em 5 partes (AUC, precisão, revocação, Brier) contra a linha de base das regras sozinhas.
RÓTULOS SUSPEITOS (cleanlab/cleanlab, *confident learning*): decisão que a rede, fora da amostra, contradiz com mais de
90% de confiança vai à revisão. APRENDIZADO ATIVO (argilla-io/argilla): os pendentes de maior incerteza vêm primeiro.
Modelo: estado/rede_neural/modelo.json.gz · relatório: docs/dados/rede_neural.json
"""
from __future__ import annotations

import gzip
import json
import math
import random
import re
import zlib
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODELO = ROOT / "estado/rede_neural/modelo.json.gz"
SAIDA = ROOT / "docs/dados/rede_neural.json"
DIM, OCULTA = 2 ** 13, 16
POSITIVAS = ("valida", "arquivada")
# 02/10 (conferência): descarte por CÓPIA, DUPLICATA ou ENCERRAMENTO é oportunidade real repetida ou fechada — positivo
COPIA = re.compile(r"c[oó]pia|duplicat|mesma oportunidade|repeti|item principal|encerrad|minuta do mesmo|ja registrad|já registrad")
OSC = re.compile(r"organizac(ao|oes) da sociedade civil|\boscs?\b|termo de (fomento|colaboracao)|entidades? (sem fins|socioassist|filantrop)|"
                 r"associac(ao|oes)|cooperativas?|pontos? de cultura|coletivos?|13\.?019|mrosc")
ABRE = re.compile(r"inscric(ao|oes)|chamamento|selec(ao|iona)|edital|premio|credenciamento|recebe propostas|propostas")
PRAZO = re.compile(r"\bate \d{1,2}[/ ]|\d{2}/\d{2}/20\d\d|prazo")


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return padrao


def _h(s: str) -> int:
    return zlib.crc32(s.encode()) % DIM


def entradas(reg: dict) -> list[int]:
    """Índices ativos (esparsos) do registro — texto + rotuladores fracos + estrutura."""
    from .linha_producao import sem, familia, canal_canonico
    t = sem(f"{reg.get('titulo') or ''} {str(reg.get('evidencia') or reg.get('objeto') or '')[:500]}")
    ws = re.findall(r"[a-z0-9]{3,}", t)
    f = {f"w:{w}" for w in ws} | {f"b:{a}_{b}" for a, b in zip(ws, ws[1:])}
    try:
        from .regras_restricao import avaliar
        av = avaliar({"titulo": reg.get("titulo"), "objeto": reg.get("evidencia") or reg.get("objeto"), "url": reg.get("url"), "uf": reg.get("uf")})
        f |= {f"lf:veredito={av.get('veredito')}", f"lf:regra={av.get('regra')}"} | {f"lf:en={e.get('id')}" for e in (av.get("enquadramento") or [])}
    except Exception:  # noqa: BLE001
        pass
    u = str(reg.get("url") or "").lower()
    canal = canal_canonico(reg.get("fonte_id") or reg.get("sensor") or reg.get("origem"))
    f |= {f"lf:osc={bool(OSC.search(t))}", f"lf:abre={bool(ABRE.search(t))}", f"lf:prazo={bool(reg.get('fim') or PRAZO.search(t))}",
          f"url:gov={'.gov.br' in u or '.leg.br' in u or '.jus.br' in u or '.mp.br' in u}", f"url:pdf={u.endswith('.pdf')}",
          f"url:busca={'duckduckgo' in u or 'google.' in u}", f"canal:{canal}", f"familia:{familia(canal)}",
          f"corrob:{min(3, int(reg.get('_canais') or 1))}", "vies"}
    try:                                       # 02/10: sinais de integridade da leitura também são entrada
        from .integridade import verificar
        f |= {f"int:{x['codigo']}" for x in verificar(reg)}
    except Exception:  # noqa: BLE001
        pass
    return sorted({_h(x) for x in f})


class Rede:
    def __init__(self, semente: int = 7):
        rnd = random.Random(semente); e = math.sqrt(2.0 / 60)
        self.W1 = {}; self._rnd = rnd; self._e = e
        self.b1 = [0.0] * OCULTA; self.W2 = [rnd.gauss(0, math.sqrt(1.0 / OCULTA)) for _ in range(OCULTA)]; self.b2 = 0.0
        self.m, self.v, self.t = {}, {}, 0

    def _linha(self, i):
        if i not in self.W1:
            self.W1[i] = [self._rnd.gauss(0, self._e) for _ in range(OCULTA)]
        return self.W1[i]

    T = 1.0                                   # temperatura da calibração (ajustada na validação cruzada)

    def logito(self, x: list[int]) -> float:
        h = list(self.b1)
        for i in x:
            w = self.W1.get(i)
            if w:
                for k in range(OCULTA):
                    h[k] += w[k]
        return self.b2 + sum(self.W2[k] * h[k] for k in range(OCULTA) if h[k] > 0)

    def prever(self, x: list[int]) -> float:
        z = self.logito(x) / (self.T or 1.0)
        return 1.0 / (1.0 + math.exp(-max(-30.0, min(30.0, z))))

    def _prever_antigo(self, x: list[int]) -> float:
        h = list(self.b1)
        for i in x:
            w = self.W1.get(i)
            if w:
                for k in range(OCULTA):
                    h[k] += w[k]
        z = self.b2 + sum(self.W2[k] * h[k] for k in range(OCULTA) if h[k] > 0)
        return 1.0 / (1.0 + math.exp(-max(-30.0, min(30.0, z))))

    def treinar(self, X, y, epocas=20, lr=0.01, l2=1e-4, peso_pos=1.0, semente=7):
        rnd = random.Random(semente); ordem = list(range(len(X)))
        b1, b2 = 0.9, 0.999
        def adam(chave, g):
            m = self.m.get(chave, 0.0) * b1 + (1 - b1) * g; v = self.v.get(chave, 0.0) * b2 + (1 - b2) * g * g
            self.m[chave], self.v[chave] = m, v
            return lr * (m / (1 - b1 ** self.t)) / (math.sqrt(v / (1 - b2 ** self.t)) + 1e-8)
        for _ in range(epocas):
            rnd.shuffle(ordem)
            for n in ordem:
                x, alvo = X[n], y[n]; self.t += 1
                h = list(self.b1)
                for i in x:
                    w = self._linha(i)
                    for k in range(OCULTA):
                        h[k] += w[k]
                z = self.b2 + sum(self.W2[k] * h[k] for k in range(OCULTA) if h[k] > 0)
                p = 1.0 / (1.0 + math.exp(-max(-30.0, min(30.0, z))))
                g = (p - alvo) * (peso_pos if alvo == 1 else 1.0)
                gh = [g * self.W2[k] if h[k] > 0 else 0.0 for k in range(OCULTA)]
                for k in range(OCULTA):
                    if h[k] > 0:
                        self.W2[k] -= adam(("w2", k), g * h[k] + l2 * self.W2[k])
                    if gh[k]:
                        self.b1[k] -= adam(("b1", k), gh[k])
                self.b2 -= adam(("b2",), g)
                for i in x:
                    w = self.W1[i]
                    for k in range(OCULTA):
                        if gh[k]:
                            w[k] -= adam((i, k), gh[k] + l2 * w[k])
        return self

    def salvar(self, p: Path, meta: dict):
        p.parent.mkdir(parents=True, exist_ok=True)
        d = {"dim": DIM, "oculta": OCULTA, "b1": self.b1, "W2": self.W2, "b2": self.b2, "T": self.T, "meta": meta,
             "W1": {str(i): [round(v, 5) for v in w] for i, w in self.W1.items()}}
        with gzip.open(p, "wt", encoding="utf-8") as f:
            json.dump(d, f, separators=(",", ":"))

    @classmethod
    def carregar(cls, p: Path) -> "Rede | None":
        try:
            with gzip.open(p, "rt", encoding="utf-8") as f:
                d = json.load(f)
        except Exception:  # noqa: BLE001
            return None
        r = cls(); r.b1, r.W2, r.b2 = d["b1"], d["W2"], d["b2"]; r.T = d.get("T", 1.0); r.W1 = {int(k): v for k, v in d["W1"].items()}
        return r


def auc(y, p) -> float:
    pos = [s for s, t in zip(p, y) if t == 1]; neg = [s for s, t in zip(p, y) if t == 0]
    if not pos or not neg:
        return float("nan")
    ordem = sorted(range(len(p)), key=lambda i: p[i]); rk = [0.0] * len(p)
    i = 0
    while i < len(ordem):
        j = i
        while j + 1 < len(ordem) and p[ordem[j + 1]] == p[ordem[i]]:
            j += 1
        for k in range(i, j + 1):
            rk[ordem[k]] = (i + j) / 2 + 1
        i = j + 1
    sp = sum(rk[i] for i in range(len(p)) if y[i] == 1)
    return (sp - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def _metricas(y, p, lim=0.5) -> dict:
    tp = sum(1 for a, b in zip(y, p) if a == 1 and b >= lim); fp = sum(1 for a, b in zip(y, p) if a == 0 and b >= lim)
    fn = sum(1 for a, b in zip(y, p) if a == 1 and b < lim)
    return {"auc": round(auc(y, p), 3), "precisao": round(tp / max(1, tp + fp), 3), "revocacao": round(tp / max(1, tp + fn), 3),
            "brier": round(sum((a - b) ** 2 for a, b in zip(y, p)) / max(1, len(y)), 4)}


def dados_rotulados() -> tuple[list[dict], list[int], list[dict]]:
    """(registros rotulados, rótulos, pendentes) — da validação individual, enriquecidos com a base pela URL."""
    import glob as _g
    base = {}
    bp = ROOT / "dados/oportunidades/oportunidades.jsonl"
    if bp.exists():
        for l in bp.open(encoding="utf-8"):
            if l.strip():
                r = json.loads(l); base.setdefault(str(r.get("url") or "").split("#")[0].rstrip("/").lower(), r)
    # 03/10 (titular): a decisão MAIS RECENTE vence e "pendente" nunca bloqueia uma decisão real. Antes os arquivos eram
    # lidos em ordem alfabética e a primeira decisão vencia — a validação automática (validacao_0000, quase tudo
    # "pendente") vinha primeiro e as decisões humanas de 02/10 (352 na fonte oficial) eram ignoradas.
    decisoes: dict[str, tuple[dict, dict]] = {}
    for f in sorted(_g.glob(str(ROOT / "dados/oportunidades/validacao_mapa/validacao_*.json")), reverse=True):
        for d in (_j(Path(f), {}).get("itens") or []):
            u = str(d.get("url") or "").split("#")[0].rstrip("/").lower()
            chave = u or str(d.get("titulo"))
            ja = decisoes.get(chave)
            if ja and not (str(ja[1].get("decisao") or "") == "pendente" and str(d.get("decisao") or "") != "pendente"):
                continue
            decisoes[chave] = ({**(base.get(u) or {}), **{k: d.get(k) for k in ("titulo", "url") if d.get(k)}}, d)
    regs, y, pend, vistos = [], [], [], set(decisoes)
    for r, d in decisoes.values():
        dec = str(d.get("decisao") or "")
        if dec.startswith(POSITIVAS):
            regs.append(r); y.append(1)
        elif dec == "descartada":
            regs.append(r); y.append(1 if COPIA.search(str(d.get("motivo") or d.get("razao") or "").lower()) else 0)
        elif dec == "pendente":
            pend.append({**r, "_decisao": dec})
    for it in (_j(ROOT / "config/restricoes_aprendidas.json", {}).get("itens") or []):   # 02/10: descartes das estantes = ruído
        u = str(it.get("url") or "").lower(); chave = u or str(it.get("titulo"))
        if chave and chave not in vistos:
            vistos.add(chave); regs.append({**(base.get(u) or {}), "titulo": it.get("titulo"), "url": it.get("url")}); y.append(0)
    return regs, y, pend


AUC_MINIMA = 0.80                            # a nota só é usada se a rede separar bem fora da amostra
L2 = 1e-3                                    # regularização mais forte: não decorar nomes de programas


def run(treinar: bool = True, epocas: int = 10) -> dict:
    regs, y, pend = dados_rotulados()
    X = [entradas(r) for r in regs]
    peso = max(1.0, (len(y) - sum(y)) / max(1, sum(y)))
    out = {"em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "regra": __doc__.split("Modelo:")[0].strip(),
           "rotulados": len(y), "positivos": sum(y), "pendentes": len(pend)}
    # validação cruzada (5 partes) — a rede contra as regras sozinhas
    rnd = random.Random(11); idx = list(range(len(X))); rnd.shuffle(idx); dobras = [idx[i::5] for i in range(5)]
    oof = [0.0] * len(X); zs = [0.0] * len(X)
    if treinar and len(X) >= 50:
        for d in dobras:
            teste = set(d); tr = [i for i in idx if i not in teste]
            r = Rede().treinar([X[i] for i in tr], [y[i] for i in tr], epocas=epocas, peso_pos=peso, l2=L2)
            for i in d:
                zs[i] = r.logito(X[i])
        # calibração por temperatura: a escala dos logitos que minimiza a perda logarítmica fora da amostra
        def perda(T):
            return sum(-math.log(max(1e-9, (1 / (1 + math.exp(-max(-30, min(30, z / T))))) if t else 1 - 1 / (1 + math.exp(-max(-30, min(30, z / T))))))
                       for z, t in zip(zs, y)) / len(y)
        T = min((0.5 + 0.25 * k for k in range(40)), key=perda)
        oof = [1 / (1 + math.exp(-max(-30, min(30, z / T)))) for z in zs]
        out["calibracao"] = {"temperatura": T, "perda_log_antes": round(perda(1.0), 4), "perda_log_depois": round(perda(T), 4)}
        out["validacao_cruzada"] = _metricas(y, oof)
        try:
            from .regras_restricao import avaliar
            base_reg = [0.0 if avaliar({"titulo": r.get("titulo"), "url": r.get("url"), "uf": r.get("uf")}).get("veredito") == "NÃO APLICA" else 1.0 for r in regs]
            out["linha_de_base_regras"] = _metricas(y, base_reg)
        except Exception:  # noqa: BLE001
            pass
        out["rotulos_suspeitos"] = sorted([{"titulo": str(regs[i].get("titulo"))[:140], "url": regs[i].get("url"), "decisao": "real" if y[i] else "descartada",
                                            "rede": round(oof[i], 3)} for i in range(len(X)) if (y[i] == 0 and oof[i] > 0.9) or (y[i] == 1 and oof[i] < 0.1)],
                                          key=lambda z: -abs(z["rede"] - (1 if z["decisao"] == "real" else 0)))[:40]
        if out["validacao_cruzada"]["auc"] >= AUC_MINIMA:
            rede = Rede().treinar(X, y, epocas=epocas, peso_pos=peso, l2=L2); rede.T = T
            rede.salvar(MODELO, {"treinada_em": out["em"], "rotulados": len(y), "metricas": out["validacao_cruzada"]})
        else:                                  # trava de qualidade: treino pior não substitui o modelo em uso
            out["aviso"] = f"AUC fora da amostra {out['validacao_cruzada']['auc']} < {AUC_MINIMA}: o modelo anterior foi mantido"
            rede = Rede.carregar(MODELO)
    else:
        rede = Rede.carregar(MODELO)
        try:                                   # sem retreino: as métricas do modelo em uso
            with gzip.open(MODELO, "rt", encoding="utf-8") as f:
                meta = json.load(f).get("meta") or {}
            out["validacao_cruzada"] = meta.get("metricas"); out["modelo_treinado_em"] = meta.get("treinada_em")
        except Exception:  # noqa: BLE001
            pass
    if rede:
        ps = [(rede.prever(entradas(r)), r) for r in pend]
        out["fila_de_validacao"] = [{"titulo": str(r.get("titulo"))[:140], "url": r.get("url"), "nota": round(p, 3), "incerteza": round(1 - abs(2 * p - 1), 3)}
                                    for p, r in sorted(ps, key=lambda z: -(1 - abs(2 * z[0] - 1)))][:60]
        out["pendentes_provaveis_reais"] = sum(1 for p, _ in ps if p >= 0.5)
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def avaliar(reg: dict) -> dict:
    """02/10 (titular): a rede como MAESTRO — antes da nota, a integridade da leitura.
    inconclusiva (algo bloqueia): sem nota, com o motivo e a ação · com_ressalva: nota puxada para o meio
    (a leitura tem defeito, a confiança cai) · confiável: a nota da rede."""
    from .integridade import verificar, situacao
    flags = verificar(reg); sit = situacao(flags)
    if sit == "inconclusiva":
        return {"nota": None, "situacao": sit, "sinais": flags}
    n = nota(reg)
    if n is not None and sit == "com_ressalva":
        n = round(0.5 + (n - 0.5) * 0.5, 3)
    return {"nota": n, "situacao": sit, "sinais": flags}


def nota(reg: dict) -> float | None:
    """A nota da rede para um registro ou livro (0–1), se houver modelo treinado."""
    r = getattr(nota, "_rede", None) or Rede.carregar(MODELO)
    nota._rede = r
    return round(r.prever(entradas(reg)), 3) if r else None


def anotar_livros() -> int:
    """Cada livro recebe a nota da rede (0–1): apoio para priorizar, nunca para excluir."""
    rede = Rede.carregar(MODELO)
    if not rede:
        return 0
    cat = ROOT / "biblioteca_alexandria/fontes/motores.json"; C = _j(cat, {}); n = 0
    for x in C.get("motores") or []:
        if x.get("papel") == "fonte_de_busca":
            continue
        ck = ((x.get("livro") or {}).get("checklist") or {}).get("Objeto") or {}
        reg = {"titulo": x.get("programa") or x.get("nome_classificado"), "evidencia": ck.get("v") if isinstance(ck, dict) else None,
               "url": x.get("pagina"), "uf": x.get("geo"), "fonte_id": (x.get("chave_acionamento") or {}).get("motores", [None])[0] if (x.get("chave_acionamento") or {}).get("motores") else None}
        x["nota_rede"] = round(rede.prever(entradas(reg)), 3); n += 1
    cat.write_text(json.dumps(C, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return n


def precisa_treinar(dias: int = 7, crescimento: float = 0.05) -> bool:
    """Retreina a cada `dias` OU quando os rótulos cresceram `crescimento` (5%) desde o último treino — 03/10: 403
    decisões humanas novas ficaram dias sem ensinar a rede porque a regra era só de calendário."""
    try:
        with gzip.open(MODELO, "rt", encoding="utf-8") as f:
            meta = json.load(f)["meta"]
        from datetime import date, timedelta
        if meta["treinada_em"][:10] < (date.today() - timedelta(days=dias)).isoformat():
            return True
        antes = int(meta.get("rotulados") or 0)
        if not antes:
            return True
        return len(dados_rotulados()[1]) >= antes * (1 + crescimento)
    except Exception:  # noqa: BLE001
        return True


if __name__ == "__main__":
    o = run()
    print(json.dumps({k: o.get(k) for k in ("rotulados", "positivos", "pendentes", "validacao_cruzada", "linha_de_base_regras", "pendentes_provaveis_reais")},
                     ensure_ascii=False, indent=1))
