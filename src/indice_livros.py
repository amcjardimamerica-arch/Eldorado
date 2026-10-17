"""ÍNDICE DOS LIVROS (titular, 16/10/2026) — encontra o livro de uma oportunidade nova pelos dados que caracterizam o
programa, e não só pelo link: assim a NOVA EDIÇÃO de um programa cai no livro dele e o edital atual soma às informações
anteriores (o edital atual sempre vale). Só no Eldorado.

Identidade de cada livro: nome do programa (sem ano, número e palavras genéricas), órgão, esfera, UF, município,
modalidade, tipo e área do recurso, e os domínios dos sites. Uma oportunidade é ligada a um livro quando:
  · o NOME do programa coincide (≥ 50% das palavras significativas em comum); E
  · o ÓRGÃO ou o DOMÍNIO coincidem; E
  · não há CONFLITO DE LOCAL (UF ou município diferentes impedem a ligação).
Esfera, modalidade, tipo e área REFORÇAM a escolha entre candidatos parecidos. Índice: biblioteca_alexandria/livros/_indice.json
"""
from __future__ import annotations

import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit

from .nucleo import ROOT

CAT = ROOT / "biblioteca_alexandria/fontes/motores.json"
INDICE = ROOT / "biblioteca_alexandria/livros/_indice.json"
GENERICAS = set("""de da do das dos e a o as os em no na nos nas para por com sem ao aos um uma edital editais chamamento chamada
publico publica publicos selecao aviso processo seletivo programa projeto projetos inscricao inscricoes abertas aberto
n no nro numero ano anual edicao premio premios fomento apoio concurso credenciamento secretaria municipal estadual estado
governo prefeitura fundo fundacao instituto federal nacional ministerio""".split())
_MUN = {}


def _sem(s) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", str(s or "").lower()) if unicodedata.category(c) != "Mn")


def palavras(s) -> set:
    t = re.sub(r"\b(?:19|20)\d{2}\b|\b\d+[/.-]?\d*\b", " ", _sem(s))
    return {w for w in re.findall(r"[a-z]{3,}", t) if w not in GENERICAS}


def programa(titulo, orgao=None) -> set:
    """O nome do PROGRAMA: a parte do título depois do órgão ('Órgão — título'); sem ano, número e genéricas."""
    t = str(titulo or "")
    if " — " in t:
        cab, resto = t.split(" — ", 1)
        pc = palavras(cab)
        instituicao = re.search(r"\b(ministerio|secretaria|prefeitura|governo|fundacao|instituto|tribunal|municipio|camara|conselho|fundo)\b", _sem(cab))
        if instituicao or (pc and pc <= palavras(orgao)):  # a parte antes do travessão É o órgão
            t = resto
    return palavras(t)


def _dominio(u) -> str | None:
    h = (urlsplit(str(u or "")).hostname or "").removeprefix("www.")
    return h if h and not re.search(r"(?:capitaai|captadores|editaisdobrasil|prosas|observatorio3setor|pncp\.gov|gov\.br$)", h) else None


def _modalidade(lv: dict) -> str | None:
    for c in ((lv.get("oportunidade") or {}).get("checklist12") or {}, (lv.get("livro") or {}).get("checklist") or {}, lv.get("checklist12") or {}):
        v = c.get("Modalidade") if isinstance(c, dict) else None
        v = v.get("valor") if isinstance(v, dict) else v
        if isinstance(v, str) and v:
            return v
    return None


def entrada(lv: dict) -> dict:
    links = [lv.get("pagina"), lv.get("site_oficial"), *(lv.get("paginas") if isinstance(lv.get("paginas"), list) else [])]
    return {"id": lv.get("id"), "programa": sorted(programa(lv.get("programa"), lv.get("orgao"))), "orgao": sorted(palavras(lv.get("orgao"))),
            "esfera": _sem(lv.get("esfera") or lv.get("abrangencia")) or None, "uf": (str(lv.get("uf") or "").upper() or None),
            "municipio": _sem(lv.get("municipio")) or None, "modalidade": _modalidade(lv), "tipo": _sem(lv.get("tipo_objeto")) or None,
            "area": _sem(lv.get("objeto_area") or lv.get("area_atuacao")) or None,
            "dominios": sorted({d for d in (_dominio(u) for u in links if isinstance(u, str)) if d}),
            "cidade_diario": (lambda m: m.group(1).strip() if m else None)(re.search(r"diario oficial d[eoa] ([a-z ]+?)(?: \(|$| \d)", _sem(lv.get("programa"))))}


def construir(gravar: bool = True) -> dict:
    L = (json.loads(CAT.read_text(encoding="utf-8")) if CAT.exists() else {}).get("motores") or []
    E = [entrada(lv) for lv in L if lv.get("id")]
    if gravar:
        INDICE.parent.mkdir(parents=True, exist_ok=True)
        INDICE.write_text(json.dumps({"livros": E}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {"livros": len(E)}


class Indice:
    def __init__(self, entradas: list[dict]):
        self.E = entradas
        self.por_palavra = defaultdict(set); self.por_dominio = defaultdict(set)
        for i, e in enumerate(entradas):
            for w in e["programa"]:
                self.por_palavra[w].add(i)
            for d in e["dominios"]:
                self.por_dominio[d].add(i)

    @classmethod
    def carregar(cls) -> "Indice":
        if not INDICE.exists():
            construir()
        return cls(json.loads(INDICE.read_text(encoding="utf-8")).get("livros") or [])

    def encontrar(self, op: dict, excluir: str | None = None) -> tuple[str | None, float, list[str]]:
        prog = programa(op.get("titulo") or op.get("programa"), op.get("orgao"))
        org = palavras(op.get("orgao"))
        dom = {d for d in (_dominio(op.get(k)) for k in ("url", "link_oficial")) if d}
        uf = str(op.get("uf") or "").upper() or None
        mun = _sem(op.get("municipio")) or None
        cands = set()
        for w in prog:
            cands |= self.por_palavra.get(w, set())
        for d in dom:
            cands |= self.por_dominio.get(d, set())
        melhor = (None, 0.0, [])
        for i in cands:
            e = self.E[i]; P = set(e["programa"])
            if excluir and e["id"] == excluir:
                continue
            if not prog or not P:
                continue
            comuns = prog & P
            j = len(comuns) / len(prog | P)
            if j < 0.75 or len(comuns) < 3:                # 16/10: 75% e 3 palavras — a 50% juntava 'Fundo Estadual' com 'Fundo
                continue                                   # Nacional' e 'PNAB Audiovisual' com 'PNAB Música'
            _c1 = re.search(r"diario oficial d[eoa] ([a-z ]+?)(?: \(|$| \d)", _sem(op.get("titulo") or op.get("programa")))
            _c2 = re.search(r"diario oficial d[eoa] ([a-z ]+?)(?: \(|$| \d)", " ".join(e["programa"]))
            if _c1 and e.get("cidade_diario") and _c1.group(1).strip() != e["cidade_diario"]:
                continue                                   # diário oficial de outra cidade
            org_ok = bool(org and e["orgao"] and len(org & set(e["orgao"])) / max(1, len(org | set(e["orgao"]))) >= 0.5)
            dom_ok = bool(dom & set(e["dominios"]))
            if not (org_ok or dom_ok):
                continue
            if uf and e["uf"] and uf not in ("BR",) and e["uf"] not in ("BR",) and uf != e["uf"]:
                continue                                   # conflito de local: outro estado
            if mun and e["municipio"] and mun != e["municipio"]:
                continue                                   # conflito de local: outro município
            s = 4 * j + 2 * org_ok + 1 * dom_ok
            mot = [f"programa {round(j * 100)}%", "órgão" if org_ok else "domínio"]
            if mun and e["municipio"] and mun == e["municipio"]:
                s += 1; mot.append("cidade")                # 17/10: mesma cidade pontua (não só veta)
            elif uf and e["uf"] and uf == e["uf"]:
                s += 0.5; mot.append("uf")
            for campo, peso in (("esfera", 0.5), ("modalidade", 1), ("tipo", 0.5), ("area", 0.5)):
                v = _sem(op.get(campo)) if campo != "esfera" else _sem(op.get("esfera") or op.get("nivel"))
                if v and e.get(campo) and _sem(e[campo]) == v:
                    s += peso; mot.append(campo)
            if s > melhor[1]:
                melhor = (e["id"], round(s, 2), mot)
        return melhor
