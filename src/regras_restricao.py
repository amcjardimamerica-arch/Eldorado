"""Regras de restrição DOS LIVROS (parecer das 238 oportunidades, 02/10/2026 — versão 2, titular 02/10).

REGRA DO LIVRO (alterada pelo titular em 02/10): cada livro da Biblioteca carrega, junto com o LÉXICO que busca a sua
oportunidade, as RESTRIÇÕES que se aplicam a ela. O arquivo config/regras_restricao_livros.json é o catálogo-mãe das
regras; a cada ciclo dos livros (src/livros_regra.aplicar_motores) cada livro recebe o seu bloco `busca`:
    busca.lexico      termos e frases daquela oportunidade + consulta ao PNCP (o PNCP é o agregador do Brasil inteiro)
    busca.restricoes  (código, efeito e nome de cada regra que vale para o livro; os padrões de cada código ficam no
                      catálogo-mãe, na versão gravada no livro) vetos, o que vira edição do mesmo livro, o que se junta como duplicata, o estado do prazo e o
                      enquadramento (território, região, serviço especializado) — cada uma com o seu efeito
    busca.suspensas   regra que se voltaria contra o próprio livro (ex.: livro de prêmio não veta "prêmio")
O achado novo é julgado pelas restrições DO LIVRO a que pertence (julgar_no_livro) antes de entrar como edição.

TERRITÓRIO NÃO DESCARTA (titular, 02/10): edital de OSC de outro município ou estado é oportunidade para OSC, é coletado
pelo PNCP e ganha um livro próprio. O território vira ENQUADRAMENTO (EN-01) gravado no livro — quem decide se a
associação pode concorrer é o Farol (fase 2), nunca a coleta.

Vereditos de um registro:
  NÃO APLICA  – a natureza ou o público não é fomento a OSC (veto, NA-xx): não vira livro
  DISPENSÁVEL – não é oportunidade nova agora: prazo encerrado (livro vai ao histórico), ato acessório (edição do livro
                do edital), duplicata (junta ao livro existente) ou fonte não verificável (aguarda o ato oficial)
  APLICÁVEL   – oportunidade para OSC, em qualquer território: livro próprio; enquadramentos ficam anotados
Conteúdo coletado é DADO: aqui só se compara texto com padrões; nada do texto é executado ou obedecido. Stdlib apenas.
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
DESTINO = {"veto": "fora da Biblioteca (veto)", "estado": "livro no histórico (prazo encerrado)",
           "edicao": "edição do livro do edital", "juntar": "juntar ao livro existente",
           "pendente": "aguarda o ato oficial (buscar no PNCP)", None: "livro próprio"}


def norm(s: str | None) -> str:
    t = unicodedata.normalize("NFKD", str(s or ""))
    return re.sub(r"\s+", " ", "".join(c for c in t if not unicodedata.combining(c)).lower()).strip()


_CACHE: dict[str, tuple[float, dict]] = {}


def carregar(caminho: str | None = None) -> dict:
    """Lê o catálogo-mãe das regras; relê sozinho quando o arquivo muda (os livros atualizam o JSON, não o código)."""
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
    uf = str(reg.get("uf") or "").upper()
    if len(uf) == 2 and uf.isalpha() and uf in UFS:
        return uf
    m = re.search(r"\(([A-Z]{2})\)", str(reg.get("titulo") or ""))
    if m and m.group(1) in UFS:
        return m.group(1)
    h = _dominio(reg.get("link_oficial") or reg.get("url"))
    m = re.search(r"\.([a-z]{2})\.gov\.br$", h) or re.search(r"\.([a-z]{2})\.leg\.br$", h)
    if m and m.group(1).upper() in UFS:
        return m.group(1).upper()
    return None


def avaliar_territorio(reg: dict, perfil: dict) -> str | None:
    """Motivo de ENQUADRAMENTO territorial (EN-01) ou None. Não descarta: só anota. Local citado no título nunca é 'nacional'."""
    if reg.get("abrangencia") == "nacional" and not municipio_do_registro(reg):
        return None
    mun = municipio_do_registro(reg)
    uf = _uf_do_registro(reg)
    permit_mun = {norm(m) for m in perfil.get("municipios", [])}
    permit_uf = {u.upper() for u in perfil.get("ufs", [])}
    if mun:
        if mun in permit_mun:
            return None
        return f"edital do município {mun.title()}{('/' + uf) if uf else ''}: costuma exigir sede ou atuação local"
    if uf and uf not in permit_uf:
        return f"edital da UF {uf}: costuma exigir sede ou atuação no estado"
    return None


def _injecao(reg: dict) -> bool:
    try:
        from .nucleo import INJECTION_PATTERNS
    except ImportError:  # uso fora do pacote
        return False
    t = " ".join(str(reg.get(k) or "") for k in ("titulo", "objeto", "descricao"))
    return any(rx.search(t) for rx in INJECTION_PATTERNS)


def _casa_padrao(r: dict, txt: str, mod: str = "") -> str | None:
    """Padrão de uma regra 'padrao' que casa no texto (fortes ignoram exceções; os comuns cedem às exceções)."""
    m = next((p for p in r.get("padroes_fortes", []) if re.search(p, txt)), None)
    if not m:
        m = next((p for p in r.get("padroes", []) if re.search(p, txt)), None)
        if m and any(re.search(e, txt) for e in r.get("exceto", [])):
            m = None
    if not m and r.get("modalidade_padrao") and mod and re.search(r["modalidade_padrao"], mod) \
            and not any(re.search(e, txt) for e in r.get("exceto", [])):      # a modalidade também cede às exceções (OSC, termo de fomento)
        m = "modalidade " + mod
    return m


def avaliar(reg: dict, perfil: dict | None = None, hoje: str | None = None) -> dict:
    """Retorna {veredito, regra, regras, motivos, efeito, destino, enquadramento, aptidao, pendencias, revisao_humana,
    quarentena}. `reg` aceita: titulo, objeto, descricao, url|link_oficial, uf, abrangencia ('nacional'),
    fim|prazo (AAAA-MM-DD), modalidade e situacao (texto do PNCP).
    Enquadramento (EN-xx: território, região, serviço especializado) NUNCA muda o veredito — fica anotado no livro.
    `revisao_humana` = há veto/dispensa num registro sem enquadramento contra a associação (pode ser dela: conferir)."""
    cfg = carregar()
    perfil = perfil or cfg["perfil_de_referencia"]
    hoje = hoje or date.today().isoformat()
    txt = _texto(reg)
    dom = _dominio(reg.get("link_oficial") or reg.get("url"))
    mod = norm(reg.get("modalidade"))
    sit = norm(reg.get("situacao"))
    disparou: list[tuple[str, str]] = []
    enq: list[dict] = []
    terr = avaliar_territorio(reg, perfil)
    efeito = {r["id"]: r.get("efeito_no_livro") for r in cfg["regras"]}
    for r in cfg["regras"]:
        alvo = None
        if r["tipo"] == "territorio":
            alvo = terr
        elif r["tipo"] == "prazo":
            fim = str(reg.get("fim") or reg.get("prazo") or "")[:10]
            if sit and re.search(r"revogad|suspens|cancelad|anulad|deserta|fracassad", sit):
                alvo = f"situação {sit}"
            elif re.fullmatch(r"\d{4}-\d{2}-\d{2}", fim) and fim < hoje:
                alvo = f"prazo {fim} já passou"
        elif r["tipo"] == "dominio":
            if dom and any(dom == d or dom.endswith("." + d) for d in r["dominios"]):
                alvo = f"{r.get('motivo_dominio', 'fonte indireta/agregador')}: {dom}"
            else:
                p = next((p for p in r.get("padroes", []) if re.search(p, txt)), None)
                if p:
                    alvo = f"guia/agregador «{p}»"
        elif r["tipo"] == "padrao":
            m = _casa_padrao(r, txt, mod)
            if m:
                alvo = f"padrão «{m}»"
        # tipo "duplicata": tratado em marcar_duplicatas()/avaliar_lote() (precisa da lista inteira)
        if not alvo:
            continue
        if efeito[r["id"]] == "enquadramento":
            enq.append({"id": r["id"], "motivo": alvo})
        else:
            disparou.append((r["id"], alvo))
    pend = []
    if terr is None and not reg.get("abrangencia") == "nacional" and not municipio_do_registro(reg) and not _uf_do_registro(reg):
        pend.append("território indeterminado")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(reg.get("fim") or reg.get("prazo") or "")[:10]):
        pend.append("prazo não confirmado")
    if not (reg.get("link_oficial") or reg.get("url")):
        pend.append("sem fonte oficial")
    quarentena = _injecao(reg)
    aptidao = "apta" if not enq else "restrita: " + "; ".join(e["motivo"] for e in enq)
    base = {"pendencias": pend, "quarentena": quarentena, "enquadramento": enq, "aptidao": aptidao}
    if not disparou:
        return {**base, "veredito": "APLICÁVEL", "regra": "AP-00", "regras": [e["id"] for e in enq], "efeito": None,
                "destino": DESTINO[None], "revisao_humana": False,
                "motivos": ["oportunidade para OSC — livro próprio; confirmar objeto, prazo e página oficial antes de protocolar"]
                           + [e["motivo"] for e in enq]}
    ordem = {r["id"]: k for k, r in enumerate(cfg["regras"])}
    veredito = {r["id"]: r["veredito"] for r in cfg["regras"]}
    ids = sorted([i for i, _ in disparou], key=lambda i: ordem[i])
    prim = min(ids, key=lambda i: (ORDEM_VEREDITO[veredito[i]], ordem[i]))
    return {**base, "veredito": veredito[prim], "regra": prim, "regras": ids + [e["id"] for e in enq], "efeito": efeito[prim],
            "destino": DESTINO.get(efeito[prim], DESTINO[None]), "revisao_humana": not enq,
            "motivos": [m for _, m in disparou] + [e["motivo"] for e in enq]}


def chave_duplicata(reg: dict) -> str | None:
    """Chave forte da oportunidade: PNCP cnpj/ano/seq. Sem chave forte: None — títulos parecidos do mesmo
    diário/município e links repetidos NÃO provam duplicata (links repetidos são sinal de link errado: ver links_suspeitos)."""
    u = " ".join(str(reg.get(k) or "") for k in ("link_oficial", "url", "pagina"))
    m = re.search(r"(?:editais|orgaos)/(\d{14})/(?:compras/)?(\d{4})/(\d+)", u)
    if m:
        return "pncp:" + "/".join(m.groups())
    return None


def marcar_duplicatas(regs: list[dict]) -> dict[int, int]:
    """{posição do duplicado: posição do primeiro} — o primeiro fica, os demais juntam-se ao livro dele (DI-08)."""
    vistos: dict[str, int] = {}
    dup: dict[int, int] = {}
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
    """Avalia uma lista aplicando também DI-08 (duplicata): o primeiro registro fica, os demais juntam-se ao livro dele."""
    res = [avaliar(r, perfil, hoje) for r in regs]
    for i, j in marcar_duplicatas(regs).items():
        res[i]["regras"] = sorted(set(res[i]["regras"]) | {"DI-08"})
        res[i]["motivos"] = res[i]["motivos"] + [f"duplicata do registro {j}"]
        if res[i]["veredito"] == "APLICÁVEL":
            res[i]["veredito"], res[i]["regra"], res[i]["efeito"], res[i]["destino"] = "DISPENSÁVEL", "DI-08", "juntar", DESTINO["juntar"]
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


# ───────────────────── o bloco `busca` de cada livro: léxico + restrições ─────────────────────
_NUM = re.compile(r"(?i)(?<![\d/])(\d{1,4})\s*/\s*(?:[a-z]{2,8}\s*/\s*)?(20\d\d)(?![\d/])")   # nº 2/2026, 28/SECULT/2026 — data dd/mm/aaaa não


def _ident_livro(x: dict) -> str:
    """O que o livro É (nome, órgão, classificação) — base do léxico e da regra 'não se volta contra o próprio livro'."""
    return norm(" ".join(str(x.get(k) or "") for k in ("programa", "orgao", "nome_classificado", "rotulo")))


def _hist(x: dict) -> list[dict]:
    return [h for h in (x.get("historico") or []) if isinstance(h, dict)]


def _historico_texto(x: dict, n: int = 3) -> str:
    return norm(" ".join(str(h.get("titulo") or "") for h in _hist(x)[-n:]))


def _municipio_livro(x: dict) -> tuple[str | None, str | None]:
    mun = x.get("municipio")
    uf = next((u for u in (str(x.get("uf") or "").upper(), str(x.get("geo") or "").upper()[:2]) if u in UFS), None)
    if isinstance(mun, str) and "/" in mun:                         # formato do catálogo: "SP/Andradina"
        a, b = mun.split("/", 1)
        if a.upper() in UFS:
            uf, mun = a.upper(), b
    if not mun:
        mun = municipio_do_registro({"titulo": x.get("programa"), "objeto": " ".join(str(h.get("titulo") or "") for h in _hist(x)[-2:])})
    return (norm(mun) if mun else None), (uf if uf in UFS else None)


def chave_pncp_do_livro(x: dict) -> str | None:
    lx = ((x.get("busca") or {}).get("lexico") or {}).get("pncp") or {}
    if lx.get("chave"):
        return lx["chave"]
    for u in [x.get("pagina")] + list(x.get("paginas") or []) + [h.get("pagina_oficial") for h in _hist(x)]:
        k = chave_duplicata({"url": u})
        if k:
            return k
    return None


def lexico_do_livro(x: dict, cfg: dict | None = None) -> dict:
    """Léxico que busca ESTA oportunidade: termos distintivos do nome/órgão, número do edital, município e a consulta
    que o motor do PNCP faz para achar (ou reencontrar) o ato. Preserva o léxico próprio que o livro já tinha."""
    cfg = cfg or carregar()
    L = cfg.get("lexico_dos_livros") or {}
    gen = set(L.get("genericos") or [])
    ident = norm(" ".join(str(x.get(k) or "") for k in ("programa", "orgao")))   # rótulo e lugar do nome não são léxico
    toks: list[str] = []
    for t in re.findall(r"[a-z]{5,}", ident + " " + _historico_texto(x, 2)):
        if t not in gen and t not in toks:
            toks.append(t)
    mun, uf = _municipio_livro(x)
    nums = sorted({f"{int(a)}/{b}" for a, b in _NUM.findall(" ".join(str(x.get(k) or "") for k in ("programa", "nome_classificado"))
                                                         + " " + " ".join(str(h.get("titulo") or "") for h in _hist(x)[-3:]))})
    nome = re.sub(r"\s+", " ", str(x.get("programa") or "")).strip()[:90]
    proprio = [t for t in (x.get("lexico_proprio") or (((x.get("busca") or {}).get("lexico") or {}).get("proprio")) or []) if t]
    forte = next((t for t in toks if not mun or t not in mun.split()), None)
    consulta = " ".join(w for w in ((mun or ""), forte or "") if w).strip() or None
    return {"termos": toks[: int(L.get("max_termos", 20))], "frases": [f for f in [nome] + [f"edital {n}" for n in nums] if f],
            "numeros": nums, "municipio": mun, "uf": uf, "proprio": proprio[:30],
            "pncp": {"chave": chave_pncp_do_livro(x), "consulta": consulta, "ufs": uf}}


def restricoes_do_livro(x: dict, cfg: dict | None = None, perfil: dict | None = None) -> tuple[list[dict], list[dict]]:
    """(restrições do livro, regras suspensas). Cada restrição leva o efeito e os padrões, para o livro ser autossuficiente."""
    cfg = cfg or carregar()
    perfil = perfil or cfg["perfil_de_referencia"]
    ident = _ident_livro(x)
    out: list[dict] = []
    susp: list[dict] = []
    for r in cfg["regras"]:
        ef = r.get("efeito_no_livro")
        if r["tipo"] == "padrao" and ef == "veto":
            m = _casa_padrao({k: v for k, v in r.items() if k != "modalidade_padrao"}, ident)
            if m:                                   # a regra se voltaria contra o próprio livro
                susp.append({"id": r["id"], "motivo": f"o próprio livro casa «{m}» — a regra não se volta contra ele"})
                continue
            out.append({"id": r["id"], "efeito": ef})      # padrões e nome: catálogo-mãe, na versão gravada no livro
        elif ef == "edicao":
            out.append({"id": r["id"], "efeito": ef})
        elif ef == "juntar":
            out.append({"id": r["id"], "efeito": ef, "chave": chave_pncp_do_livro(x), "pagina": x.get("pagina")})
        elif ef == "estado":
            fims = sorted(str(h.get("fim")) for h in _hist(x) if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(h.get("fim") or "")))
            out.append({"id": r["id"], "efeito": ef, "ultimo_fim": fims[-1] if fims else None})
        elif ef == "pendente":
            dom = _dominio(x.get("pagina"))
            if dom and any(dom == d or dom.endswith("." + d) for d in r.get("dominios", [])):
                out.append({"id": r["id"], "efeito": ef, "motivo": f"página do livro é espelho/agregador ({dom}): localizar o ato no PNCP ou no site oficial"})
        elif ef == "enquadramento":
            if r["tipo"] == "territorio":
                mun, uf = _municipio_livro(x)
                motivo = None
                if x.get("geo") not in ("BR", "INT") and x.get("abrangencia") != "nacional":
                    if mun and mun not in {norm(m) for m in perfil.get("municipios", [])}:
                        nome = str(x.get("municipio") or "").split("/")[-1] or mun.title()
                        nome = nome.title() if nome.isupper() else nome
                        motivo = f"livro do município {nome}{'/' + uf if uf else ''}: costuma exigir sede ou atuação local"
                    elif not mun and uf and uf not in {u.upper() for u in perfil.get("ufs", [])}:
                        motivo = f"livro da UF {uf}: costuma exigir sede ou atuação no estado"
                if motivo:
                    out.append({"id": r["id"], "efeito": ef, "motivo": motivo})
            else:
                m = _casa_padrao(r, ident + " " + _historico_texto(x, 2))
                if m:
                    out.append({"id": r["id"], "efeito": ef, "motivo": f"padrão «{m}»"})
    return out, susp


def bloco_do_livro(x: dict, hoje: str | None = None, cfg: dict | None = None) -> dict:
    """O bloco `busca` gravado no livro: léxico + restrições + regras suspensas + aptidão da associação de referência."""
    cfg = cfg or carregar()
    restr, susp = restricoes_do_livro(x, cfg)
    enq = [r for r in restr if r["efeito"] == "enquadramento"]
    return {"versao_regras": cfg.get("versao"), "atualizado_em": hoje or date.today().isoformat(),
            "lexico": lexico_do_livro(x, cfg), "restricoes": restr, "suspensas": susp,
            "revisao_curadoria": [f"{r['id']}: {r['motivo']}" for r in susp],     # o próprio livro casa um veto: a curadoria confere
            "aptidao": {"associacao": cfg["perfil_de_referencia"].get("associacao"),
                        "situacao": "apta" if not enq else "restrita", "motivos": [r["motivo"] for r in enq],
                        "nota": "enquadramento não exclui o livro: a fase 2 (Farol) decide por associação"}}


def aplicar_aos_livros(livros: list[dict], hoje: str | None = None) -> dict:
    """Grava/atualiza o bloco `busca` em cada livro. Só regrava quando a versão das regras ou o léxico mudou."""
    cfg = carregar()
    hoje = hoje or date.today().isoformat()
    pncp = _pncp_achados()
    novos = atualizados = com_restricao = restritos = 0
    falhas = 0
    for x in livros:
        if not isinstance(x, dict):
            continue
        ant = json.loads(json.dumps(x.get("busca") or {}))    # cópia funda: a chave PNCP nova conta como mudança
        if x.get("id") in pncp and not ((x.get("busca") or {}).get("lexico") or {}).get("pncp", {}).get("chave"):
            x.setdefault("busca", {}).setdefault("lexico", {}).setdefault("pncp", {})["chave"] = pncp[x["id"]]
        try:
            novo = bloco_do_livro(x, hoje, cfg)
        except Exception:  # noqa: BLE001 — um livro malformado não impede os outros
            falhas += 1
            continue
        sem_data = lambda b: {k: v for k, v in b.items() if k != "atualizado_em"}
        if not ant:
            novos += 1
        elif sem_data(ant) != sem_data(novo):
            atualizados += 1
        else:
            novo["atualizado_em"] = ant.get("atualizado_em") or hoje
        x["busca"] = novo
        _qualificar(x, hoje)                       # 02/10 (titular): identificado primeiro, qualificado depois — nunca apagado
        com_restricao += bool(novo["restricoes"])
        restritos += novo["aptidao"]["situacao"] == "restrita"
    return {"livros": len(livros), "blocos_novos": novos, "blocos_atualizados": atualizados, "livros_com_falha": falhas,
            "com_restricoes": com_restricao, "restritos_para_a_associacao": restritos, "versao_regras": cfg.get("versao")}


# 02/10 (conferência): veto de PÚBLICO ou de PRÊMIO com sinal de OSC no texto não é "não aplica" — fica EM REVISÃO
SINAL_OSC_REVISAO = re.compile(r"pontos? (?:e pontoes )?de cultura|\bpnab\b|aldir blanc|coletivos?|iniciativas?|\boscs?\b|"
                               r"organizac(?:ao|oes) da sociedade|entidades?|associac(?:ao|oes)|fundo (?:municipal|estadual|da crianca|do idoso)|"
                               r"projetos? (?:sociais|culturais|comunitarios)|biodiversidade|sem fins")
REVISAVEIS = {"NA-05", "NA-06"}


def qualificacao_do_veto(regra: str | None, texto: str, motivo: str = "", hoje: str = "") -> dict:
    """NÃO APLICA (o livro fica, marcado, sem ativação) ou EM REVISÃO (veto duvidoso: o livro segue ativo e vai à curadoria)."""
    if regra in REVISAVEIS and SINAL_OSC_REVISAO.search(norm(texto)):
        return {"veredito": "EM REVISÃO", "regra": regra, "motivo": (motivo or "")[:240], "origem": "automática", "em": hoje,
                "acao": "veto de público ou prêmio com sinal de OSC no texto — conferir na curadoria (o livro segue ativo)"}
    return {"veredito": "NÃO APLICA", "regra": regra, "motivo": (motivo or "")[:240], "origem": "automática", "em": hoje,
            "acao": "identificado e mantido; arquivar manualmente se confirmado"}


def _qualificar(x: dict, hoje: str) -> None:
    """Marca o livro que cai num veto (NÃO APLICA) — sem apagá-lo. A qualificação MANUAL (curadoria) nunca é sobrescrita;
    a automática é refeita a cada ciclo (some quando a regra deixa de valer)."""
    q = x.get("qualificacao") or {}
    if q.get("manual"):
        return
    try:
        ck = ((x.get("livro") or {}).get("checklist") or {}).get("Objeto") or {}
        av = avaliar({"titulo": x.get("programa") or x.get("nome_classificado"), "objeto": ck.get("v") if isinstance(ck, dict) else None,
                      "url": x.get("pagina"), "uf": x.get("geo") if x.get("geo") not in ("BR", "INT") else None})
    except Exception:  # noqa: BLE001
        return
    if av.get("veredito") == "NÃO APLICA" and not x.get("excecao_abrangencia"):
        txt = f"{x.get('programa') or ''} {x.get('nome_classificado') or ''} {(ck.get('v') if isinstance(ck, dict) else '') or ''}"
        x["qualificacao"] = qualificacao_do_veto(av.get("regra"), txt, str(av.get("motivo") or ""), q.get("em") or hoje)
    elif q.get("origem") == "automática":
        x.pop("qualificacao", None)


def _pncp_achados() -> dict[str, str]:
    """{id do livro: chave pncp} encontrados pela Fonte C do motor 04 (estado/pncp_osc.json › livros_pncp)."""
    p = ROOT / "estado/pncp_osc.json"
    try:
        return {k: v for k, v in (json.loads(p.read_text(encoding="utf-8")).get("livros_pncp") or {}).items() if v}
    except (OSError, ValueError):
        return {}


def julgar_no_livro(achado: dict, livro: dict) -> dict:
    """Julga um achado que pertence a um livro pelas restrições DO PRÓPRIO livro.
    → {efeito: 'veto'|'edicao'|'juntar'|'aceita', regra, motivo, termos (léxico do livro que casou)}."""
    b = livro.get("busca") or bloco_do_livro(livro)
    mae = {r["id"]: r for r in carregar()["regras"]}
    pad = lambda r: {**mae.get(r["id"], {}), **r}       # o livro diz QUAIS restrições valem; o catálogo-mãe dá os padrões
    txt = _texto(achado)
    mod = norm(achado.get("modalidade"))
    lx = b.get("lexico") or {}
    termos = [t for t in (lx.get("termos") or []) + (lx.get("proprio") or []) if norm(t) and norm(t) in txt]
    for r in b.get("restricoes") or []:
        if r["efeito"] == "veto":
            m = _casa_padrao(pad(r), txt, mod)
            if m:
                return {"efeito": "veto", "regra": r["id"], "motivo": f"padrão «{m}»", "termos": termos}
    k = chave_duplicata(achado)
    for r in b.get("restricoes") or []:
        if r["efeito"] == "juntar" and k and r.get("chave") == k:
            return {"efeito": "juntar", "regra": r["id"], "motivo": f"mesma chave {k}", "termos": termos}
        if r["efeito"] == "edicao" and _casa_padrao(pad(r), txt):
            return {"efeito": "edicao", "regra": r["id"], "motivo": "ato acessório do edital do livro", "termos": termos}
    return {"efeito": "aceita", "regra": None, "motivo": "nova informação do livro", "termos": termos}
