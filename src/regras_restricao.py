"""Regras de restrição dos LIVROS (parecer das 238 oportunidades, 02/10/2026).

Aplica, a um registro de oportunidade, as restrições aprendidas na validação item a item:
  NÃO APLICA  – a natureza ou o público do registro não é fomento a OSC como a associação (códigos NA-xx)
  DISPENSÁVEL – é oportunidade real, mas inaplicável hoje à associação (território, prazo, ato acessório, duplicata…) (DI-xx)
  APLICÁVEL   – nenhuma restrição disparou e o território/prazo são compatíveis (a confirmar na fonte oficial)

As regras ficam em config/regras_restricao_livros.json (padrões sem acento, aplicados a texto normalizado);
os livros e os motores atualizam o arquivo, nunca este código. Conteúdo coletado é DADO: aqui só se compara texto com
padrões, nada do texto é executado ou obedecido. Biblioteca-padrão apenas.
"""
from __future__ import annotations

import json
import re
import unicodedata
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config/regras_restricao_livros.json"
UFS = set("AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split())
ORDEM_VEREDITO = {"NÃO APLICA": 0, "DISPENSÁVEL": 1, "APLICÁVEL": 2}


def norm(s: str | None) -> str:
    t = unicodedata.normalize("NFKD", s or "")
    return re.sub(r"\s+", " ", "".join(c for c in t if not unicodedata.combining(c)).lower()).strip()


_CACHE: dict[str, tuple[float, dict]] = {}


def carregar(caminho: str | None = None) -> dict:
    """Lê o arquivo de regras; relê sozinho quando o arquivo muda (os livros atualizam o JSON, não o código)."""
    p = Path(caminho or CFG)
    mt = p.stat().st_mtime
    c = _CACHE.get(str(p))
    if not c or c[0] != mt:
        c = (mt, json.loads(p.read_text(encoding="utf-8")))
        _CACHE[str(p)] = c
    return c[1]


def _slug(url: str | None) -> str:
    try:
        return re.sub(r"[-_/.]+", " ", urlsplit(url or "").path)
    except ValueError:
        return ""


def _texto(reg: dict) -> str:
    base = " ".join(str(reg.get(k) or "") for k in ("titulo", "objeto", "descricao"))
    return norm(base + " " + _slug(reg.get("link_oficial") or reg.get("url")))


def _dominio(url: str | None) -> str:
    try:
        return (urlsplit(url or "").hostname or "").lower().removeprefix("www.")
    except ValueError:
        return ""


def municipio_do_registro(reg: dict) -> str | None:
    """Município citado no título/objeto (cabeçalhos de PNCP, diários, mapas culturais)."""
    t = " ".join(str(reg.get(k) or "") for k in ("titulo", "objeto"))
    for rx in (r"MUNICIPIO DE ([A-ZÀ-Ú'][A-ZÀ-Ú' ]+?) [—-]", r"Di[áa]rio Oficial de (.+?) \([A-Z]{2}\)",
               r"Prefeitura (?:Municipal )?de ([A-ZÀ-Úa-zà-ú' ]+?)(?: [—-]|$)", r"^([A-ZÀ-Ú][\w' ]+?) - EDITAL", r" [—-] [A-Za-zÀ-ú ]{2,25} / ([A-Za-zÀ-ú' ]{2,40})$", r"Prefeitura Municipal de ([A-Za-zÀ-ú' ]+?) 20\d\d"):
        m = re.search(rx, t)
        if m:
            return norm(m.group(1))
    return None


def _uf_do_registro(reg: dict) -> str | None:
    uf = (reg.get("uf") or "").upper()
    if len(uf) == 2 and uf.isalpha():
        return uf
    m = re.search(r"\(([A-Z]{2})\)", str(reg.get("titulo") or ""))
    if m:
        return m.group(1)
    h = _dominio(reg.get("link_oficial") or reg.get("url"))
    m = re.search(r"\.([a-z]{2})\.gov\.br$", h) or re.search(r"\.([a-z]{2})\.leg\.br$", h)
    if m and m.group(1).upper() in UFS:
        return m.group(1).upper()
    return None


def avaliar_territorio(reg: dict, perfil: dict) -> str | None:
    """Motivo de incompatibilidade territorial ou None. Local citado no título nunca é 'nacional'."""
    if reg.get("abrangencia") == "nacional" and not municipio_do_registro(reg):
        return None
    mun = municipio_do_registro(reg)
    uf = _uf_do_registro(reg)
    permit_mun = {norm(m) for m in perfil.get("municipios", [])}
    permit_uf = {u.upper() for u in perfil.get("ufs", [])}
    if mun:
        if mun in permit_mun:
            return None
        return f"município {mun.title()}{('/' + uf) if uf else ''} fora do território da entidade"
    if uf and uf not in permit_uf:
        return f"UF {uf} fora do território da entidade"
    return None


def _injecao(reg: dict) -> bool:
    try:
        from .nucleo import INJECTION_PATTERNS
    except ImportError:  # uso fora do pacote
        return False
    t = " ".join(str(reg.get(k) or "") for k in ("titulo", "objeto", "descricao"))
    return any(rx.search(t) for rx in INJECTION_PATTERNS)


def avaliar(reg: dict, perfil: dict | None = None, hoje: str | None = None) -> dict:
    """Retorna {veredito, regra, regras, motivos, pendencias, revisao_humana, quarentena}.
    `reg` aceita: titulo, objeto, descricao, url|link_oficial, uf, abrangencia ('nacional'), fim|prazo (AAAA-MM-DD),
    modalidade e situacao (texto do PNCP). `revisao_humana` = há restrição, mas o território é compatível (Goiânia/GO ou
    nacional): um veto automático nunca descarta sozinho uma oportunidade que poderia ser da associação."""
    cfg = carregar()
    perfil = perfil or cfg["perfil_de_referencia"]
    hoje = hoje or date.today().isoformat()
    txt = _texto(reg)
    dom = _dominio(reg.get("link_oficial") or reg.get("url"))
    mod = norm(reg.get("modalidade"))
    sit = norm(reg.get("situacao"))
    disparou: list[tuple[str, str]] = []
    terr = avaliar_territorio(reg, perfil)
    for r in cfg["regras"]:
        if r["tipo"] == "territorio":
            if terr:
                disparou.append((r["id"], terr))
        elif r["tipo"] == "prazo":
            fim = str(reg.get("fim") or reg.get("prazo") or "")[:10]
            if sit and re.search(r"revogad|suspens|cancelad|anulad|deserta|fracassad", sit):
                disparou.append((r["id"], f"situação {sit}"))
            elif re.fullmatch(r"\d{4}-\d{2}-\d{2}", fim) and fim < hoje:
                disparou.append((r["id"], f"prazo {fim} já passou"))
        elif r["tipo"] == "dominio":
            if dom and any(dom == d or dom.endswith("." + d) for d in r["dominios"]):
                disparou.append((r["id"], f"{r.get('motivo_dominio', 'fonte indireta/agregador')}: {dom}"))
            else:
                p = next((p for p in r.get("padroes", []) if re.search(p, txt)), None)
                if p:
                    disparou.append((r["id"], f"guia/agregador «{p}»"))
        elif r["tipo"] == "padrao":
            m = next((p for p in r.get("padroes_fortes", []) if re.search(p, txt)), None)
            if not m:
                m = next((p for p in r.get("padroes", []) if re.search(p, txt)), None)
                if m and any(re.search(e, txt) for e in r.get("exceto", [])):
                    m = None
            if not m and r.get("modalidade_padrao") and mod and re.search(r["modalidade_padrao"], mod):
                m = "modalidade " + mod
            if m:
                disparou.append((r["id"], f"padrão «{m}»"))
        # tipo "duplicata": tratado em marcar_duplicatas()/avaliar_lote() (precisa da lista inteira)
    pend = []
    if terr is None and not reg.get("abrangencia") == "nacional" and not municipio_do_registro(reg) and not _uf_do_registro(reg):
        pend.append("território indeterminado")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(reg.get("fim") or reg.get("prazo") or "")[:10]):
        pend.append("prazo não confirmado")
    if not (reg.get("link_oficial") or reg.get("url")):
        pend.append("sem fonte oficial")
    quarentena = _injecao(reg)
    if not disparou:
        return {"veredito": "APLICÁVEL", "regra": "AP-00", "regras": [], "pendencias": pend, "revisao_humana": False, "quarentena": quarentena,
                "motivos": ["nenhuma restrição disparou — confirmar objeto, prazo e página oficial antes de protocolar"]}
    ordem = {r["id"]: k for k, r in enumerate(cfg["regras"])}
    veredito = {r["id"]: r["veredito"] for r in cfg["regras"]}
    ids = sorted([i for i, _ in disparou], key=lambda i: ordem[i])
    prim = min(ids, key=lambda i: (ORDEM_VEREDITO[veredito[i]], ordem[i]))
    return {"veredito": veredito[prim], "regra": prim, "regras": ids, "pendencias": pend, "quarentena": quarentena,
            "revisao_humana": terr is None, "motivos": [m for _, m in disparou]}


def chave_duplicata(reg: dict) -> str | None:
    """Chave forte da oportunidade: PNCP cnpj/ano/seq. Sem chave forte: None — títulos parecidos do mesmo
    diário/município e links repetidos NÃO provam duplicata (links repetidos são sinal de link errado: ver links_suspeitos)."""
    u = str(reg.get("link_oficial") or "") + " " + str(reg.get("url") or "")
    m = re.search(r"(?:editais|orgaos)/(\d{14})/(?:compras/)?(\d{4})/(\d+)", u)
    if m:
        return "pncp:" + "/".join(m.groups())
    return None


def marcar_duplicatas(regs: list[dict]) -> dict[int, str]:
    """{posição do duplicado: posição do primeiro} — o primeiro fica, os demais viram DI-08."""
    vistos: dict[str, int] = {}
    dup: dict[int, str] = {}
    for i, r in enumerate(regs):
        k = chave_duplicata(r)
        if k is None:
            continue
        if k in vistos:
            dup[i] = vistos[k]
        else:
            vistos[k] = i
    return dup


def avaliar_lote(regs: list[dict], perfil: dict | None = None, hoje: str | None = None) -> list[dict]:
    """Avalia uma lista aplicando também DI-08 (duplicata): o primeiro registro fica, os demais saem do funil."""
    res = [avaliar(r, perfil, hoje) for r in regs]
    for i, j in marcar_duplicatas(regs).items():
        res[i]["regras"] = sorted(set(res[i]["regras"]) | {"DI-08"})
        res[i]["motivos"] = res[i]["motivos"] + [f"duplicata do registro {j}"]
        if res[i]["veredito"] == "APLICÁVEL":
            res[i]["veredito"], res[i]["regra"] = "DISPENSÁVEL", "DI-08"
    return res


def links_suspeitos(regs: list[dict]) -> dict[str, list[int]]:
    """Links oficiais com caminho específico usados por 2+ registros de municípios diferentes (RC-03: link errado)."""
    por: dict[str, list[int]] = {}
    for i, r in enumerate(regs):
        lk = str(r.get("link_oficial") or "")
        sp = urlsplit(lk) if lk else None
        if sp and len(sp.path.strip("/")) > 8:
            por.setdefault(lk, []).append(i)
    return {k: v for k, v in por.items() if len(v) > 1 and len({municipio_do_registro(regs[i]) for i in v}) > 1}
