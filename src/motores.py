"""Motores de Busca — os 260 pontos de captação, um motor por ponto.

O titular quer ver, na Bússola, todos os 260 pontos agregados por TIPO e
segmentados por território: Rouanet é nacional; a Aldir Blanc tem um bloco
estadual (todos os editais do Estado) e um municipal (todos os de Goiânia).
Com filtro de estado e de quais editais buscar. Cada ponto mostra as 11
camadas (Objeto, Prazo de inscrição, Resultado, Prazo de recurso, Valor,
Órgão/financiador, Território, Esfera, Requisitos, Anexos, Destinação), o link
da página de publicação e a validação do conteúdo pelo motor — e um
diagnóstico quando faltam camadas: o que falta, a causa e a ação.

Este módulo monta o fragmento `docs/dados/motores.json` (compacto). O botão
"Ativar motor" no painel gera o pedido com os pontos selecionados; a execução
real acontece no GitHub Actions (workflow_dispatch com o campo `fontes`), que
lê o pedido e roda só os motores escolhidos.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import date

from .nucleo import ROOT, load_json, now_iso, slug, write_json

CAMADAS = ("Objeto", "Prazo de inscrição", "Resultado", "Prazo de recurso", "Valor",
           "Órgão / financiador", "Território", "Esfera", "Requisitos", "Anexos", "Destinação")

_FAMILIAS = [
    (r"pnab|aldir", "PNAB / Aldir Blanc"), (r"rouanet|pronac", "Lei Rouanet"),
    (r"goyazes", "Lei Goyazes"), (r"incentivo ao esporte|\blie\b", "Lei de Incentivo ao Esporte"),
    (r"emenda", "Emendas parlamentares"), (r"fmdca|cmdca|crian", "Fundo da Criança (FMDCA/FIA)"),
    (r"fmas|cmas|assist", "Assistência social (FMAS/FEAS)"), (r"idos", "Fundo do Idoso"),
    (r"pronon|pronas", "PRONON / PRONAS"), (r"tjgo|vara|justi[çc]a|cnj|presta[çc][ãa]o", "Destinação judicial"),
    (r"mpgo|mpf|minist[ée]rio p[úu]blico|\btac\b", "Ministério Público"),
    (r"receita federal|apreendid", "Receita Federal (doação)"), (r"sebrae", "Sebrae"),
    (r"bndes|amaz[ôo]nia", "BNDES"),
    (r"funda[çc][ãa]o|instituto|grupo|coca|natura|ita[úu]|bradesco|telef[ôo]nica|vale|claro|renner|neoenergia|sabin|sicoob|unibanco|votorantim|localiza|arcelor", "Fundações e institutos privados"),
    (r"unesco|unicef|banco mundial|\bbid\b|usaid|pnud|ford|open society|gates|skoll|echoing|rockefeller|oak|google|meta|microsoft|europ|climate|gef", "Internacionais"),
]


def familia(programa: str) -> str:
    p = (programa or "").lower()
    for rx, nome in _FAMILIAS:
        if re.search(rx, p):
            return nome
    return "Outros programas"


def segmento(f: dict) -> str:
    """Nacional / Estadual GO / Municipal Goiânia / Privado / Internacional."""
    n = f.get("nivel")
    if n == "federal":
        return "Nacional"
    if n == "estadual":
        return f'Estadual {f.get("uf") or ""}'.strip()
    if n == "municipal":
        return "Municipal Goiânia" if (f.get("goias") or (f.get("uf") == "GO")) else "Municipal"
    if n == "internacional":
        return "Internacional"
    return "Privado"


def _ultimo_edital_da_fonte(fonte: dict, con) -> dict | None:
    """O edital mais recente do acervo ligado ao órgão desta fonte."""
    toks = [t for t in re.findall(r"[a-zà-ú]{5,}", (fonte.get("orgao") or "").lower())
            if t not in ("secretaria", "municipal", "estadual", "federal", "governo", "estado", "goiás", "goiania", "goiânia", "programa", "fundo")]
    if not toks:
        return None
    rows = con.execute("SELECT ficha FROM historico ORDER BY data_publicacao DESC LIMIT 6000").fetchall()
    for (fj,) in rows:
        f = json.loads(fj)
        alvo = f'{f.get("financiador","")} {f.get("titulo","")}'.lower()
        if sum(1 for t in toks if t in alvo) >= max(1, min(2, len(toks))):
            return f
    return None


def camadas_da_fonte(fonte: dict, edital: dict | None) -> list[dict]:
    """As 11 camadas com o valor real (ou lacuna) — a partir do último edital."""
    itens = ((edital or {}).get("requisitos_condicoes_valores") or {}).get("itens") or []
    por_nome = {i["item"]: i for i in itens}
    saida = []
    for c in CAMADAS:
        i = por_nome.get(c)
        if i:
            saida.append({"camada": c, "ok": bool(i["comprovado"]), "valor": (i.get("valor") or "")[:120]})
        elif c == "Órgão / financiador":
            saida.append({"camada": c, "ok": True, "valor": fonte.get("orgao")})
        elif c == "Território":
            saida.append({"camada": c, "ok": True, "valor": fonte.get("uf") or "Brasil"})
        elif c == "Esfera":
            saida.append({"camada": c, "ok": fonte.get("nivel") in ("federal", "estadual", "municipal"), "valor": fonte.get("nivel")})
        else:
            saida.append({"camada": c, "ok": False, "valor": None})
    return saida


def diagnostico(fonte: dict, camadas: list[dict], sensor: dict | None, bloqueio: dict | None) -> dict:
    faltam = [c["camada"] for c in camadas if not c["ok"]]
    if not faltam:
        return {"estado": "completo", "faltam": [], "causa": None, "acao": "motor pode parar"}
    if not fonte.get("sites"):
        causa, acao = "sem página de publicação conhecida", "localizar por IA (degrau 4) ou LAI"
    elif bloqueio:
        causa = f'página bloqueada ({", ".join(bloqueio.get("erros", {}))}) em {bloqueio.get("bloqueios")} tentativa(s)'
        acao = "descer a escada: espelho institucional → Wayback → agregador → IA"
    elif not sensor:
        causa, acao = "motor ainda não saiu com rede", "aguarda a primeira saída no GitHub Actions"
    elif sensor.get("achados_total", 0) == 0:
        causa = "página respondeu mas sem edital reconhecido pelo léxico"
        acao = ("trocar URL para a listagem de editais" if sensor.get("vazias_seguidas", 0) >= 3
                else "continuar leitura diária; conferir se a URL é listagem")
    else:
        causa = "edital encontrado, mas o texto integral ainda não foi extraído"
        acao = "campanha de completude / extração do ato"
    return {"estado": "incompleto", "faltam": faltam, "causa": causa, "acao": acao,
            "obtidas": len(camadas) - len(faltam), "total": len(camadas)}


def run() -> dict:
    fontes = load_json(ROOT / "config/fontes_captacao_260.json").get("fontes", [])
    esq = load_json(ROOT / "estado/esquadra.json").get("sensores", {}) if (ROOT / "estado/esquadra.json").exists() else {}
    blq = load_json(ROOT / "estado/bloqueios.json").get("dominios", {}) if (ROOT / "estado/bloqueios.json").exists() else {}
    prazos = {p["programa"]: p for p in load_json(ROOT / "biblioteca_alexandria/fontes/parecer_prazos.json").get("lista", [])} \
        if (ROOT / "biblioteca_alexandria/fontes/parecer_prazos.json").exists() else {}
    try:
        from .banco import conectar
        con = conectar()
    except Exception:
        con = None
    from urllib.parse import urlsplit
    # qual motor (sensor) atende cada fonte — vários pontos compartilham o mesmo site
    motor_da_fonte = {}
    try:
        from .sensores import registro
        for s in registro():
            for fid in s.get("fontes_260") or []:
                motor_da_fonte[fid] = s["id"]
    except Exception:
        pass
    motores = []
    for f in fontes:
        edital = _ultimo_edital_da_fonte(f, con) if con else None
        cam = camadas_da_fonte(f, edital)
        sid = motor_da_fonte.get(f["id"], f"f260-{f['id']}")
        s = esq.get(sid)
        dom = urlsplit(f["sites"][0]).hostname if f.get("sites") else None
        b = blq.get(dom) if dom else None
        pz = prazos.get(f["programa"], {})
        validacao = ("bloqueada" if b else "não lida ainda" if not s else
                     "lida, edital encontrado" if s.get("achados_total") else "lida, sem edital reconhecido")
        motores.append({
            "id": f["id"], "programa": f["programa"], "orgao": f.get("orgao"), "motor": sid,
            "familia": familia(f["programa"]), "segmento": segmento(f),
            "tipo": f["tipo"], "nivel": f["nivel"], "uf": f.get("uf") or ("BR" if f["nivel"] == "federal" else None),
            "goias": bool(f.get("goias")),
            "pagina": f["sites"][0] if f.get("sites") else None,
            "paginas": f.get("sites", [])[:3], "confianca_pagina": f.get("confianca_site"),
            "validacao": validacao,
            "ultima_leitura": (s or {}).get("ultima"), "achados": (s or {}).get("achados_total", 0),
            "http": ((s or {}).get("saude") or [{}])[0].get("http") if s else None,
            "regime_prazo": pz.get("regime_de_prazo"), "certeza_prazo": pz.get("certeza"),
            "proxima_data": pz.get("proxima_data"),
            "ultimo_edital": ({"titulo": (edital.get("titulo") or "")[:100], "url": edital.get("url"),
                               "publicado": edital.get("data_publicacao")} if edital else None),
            "camadas": cam, "obtidas": sum(1 for c in cam if c["ok"]),
            "diagnostico": diagnostico(f, cam, s, b),
        })
    if con:
        con.close()
    # plataformas indicadas pelo titular (Prosas etc.): rodando de forma satisfatória?
    plataformas = []
    inv = load_json(ROOT / "config/investigacao.json").get("fontes", []) if (ROOT / "config/investigacao.json").exists() else []
    for p in inv:
        s = esq.get(f"plat-{p['id']}")
        b = blq.get(urlsplit(p["url"]).hostname)
        plataformas.append({"id": p["id"], "nome": p["nome"], "url": p["url"],
                            "ultima_leitura": (s or {}).get("ultima"), "achados": (s or {}).get("achados_total", 0),
                            "leituras": (s or {}).get("leituras", 0),
                            "situacao": ("bloqueada" if b else "sem leitura ainda" if not s else
                                         "satisfatória — obtendo editais" if s.get("achados_total") else
                                         "lendo, sem editais reconhecidos")})
    # diários e locais oficiais
    esp = load_json(ROOT / "config/sensores.json").get("sensores_especiais", [])
    oficiais = []
    for e in esp:
        s = esq.get(e["id"]); b = blq.get(urlsplit(e["urls"][0]).hostname)
        oficiais.append({"id": e["id"], "nome": e["nome"], "tipo": e["tipo"], "url": e["urls"][0],
                         "ultima_leitura": (s or {}).get("ultima"), "achados": (s or {}).get("achados_total", 0),
                         "situacao": ("bloqueado" if b else "sem leitura ainda" if not s else
                                      "ativo — captando" if s.get("achados_total") else "ativo, sem achados")})
    motores.sort(key=lambda m: (not m["goias"], m["familia"], m["segmento"], m["programa"]))
    resumo = {
        "gerado_em": now_iso(), "total": len(motores),
        "por_familia": dict(Counter(m["familia"] for m in motores).most_common()),
        "por_segmento": dict(Counter(m["segmento"] for m in motores)),
        "completos": sum(1 for m in motores if m["diagnostico"]["estado"] == "completo"),
        "media_camadas": round(sum(m["obtidas"] for m in motores) / len(motores), 2) if motores else 0,
        "plataformas": plataformas, "oficiais": oficiais,
        "camadas": list(CAMADAS),
    }
    write_json(ROOT / "biblioteca_alexandria/fontes/motores.json", {**resumo, "motores": motores})
    from .compacto import compactar
    pasta = ROOT / "docs/dados"; pasta.mkdir(parents=True, exist_ok=True)
    leve = [{k: m[k] for k in ("id", "programa", "orgao", "familia", "segmento", "tipo", "nivel", "uf", "goias",
                              "pagina", "confianca_pagina", "validacao", "ultima_leitura", "achados", "http",
                              "regime_prazo", "certeza_prazo", "obtidas")}
            | {"camadas_ok": "".join("1" if c["ok"] else "0" for c in m["camadas"]),
               "faltam": "|".join(m["diagnostico"]["faltam"]),
               "causa": m["diagnostico"]["causa"], "acao": m["diagnostico"]["acao"],
               "ultimo_titulo": (m["ultimo_edital"] or {}).get("titulo"),
               "ultimo_url": (m["ultimo_edital"] or {}).get("url"),
               "proxima": json.dumps(m["proxima_data"], ensure_ascii=False) if m["proxima_data"] else None}
            for m in motores]
    pac = compactar(leve)
    pac["resumo"] = {k: v for k, v in resumo.items() if k not in ("plataformas", "oficiais")}
    pac["plataformas"] = plataformas; pac["oficiais"] = oficiais
    (pasta / "motores.json").write_text(json.dumps(pac, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {k: v for k, v in resumo.items() if k not in ("plataformas", "oficiais", "camadas")}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
