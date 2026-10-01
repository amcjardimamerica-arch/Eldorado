"""MOTOR 02 — Diário Oficial do Estado de Goiás (versão 2, 01/10/2026).

Parecer do conselho: docs/pareceres/motor-02-diario-goias.md. O que o motor antigo fazia e por que rendia pouco:

1. Lia o RÓTULO dos links da home e do "portal" do Diário (17 KB, sem edital). Os caminhos que tentou em 03/09
   (`/portal/edicoes`, `/portal/visualizacoes/pesquisa`) deram erro HTTP — e o host foi marcado como "exige
   Brasil". De 06 a 20/09 o motor foi PULADO todos os dias (nenhuma página lida) e o painel pintou "azul,
   funcionou sem oportunidade".
2. Desde 21/09 lia só as páginas das secretarias e trazia os MESMOS 11 itens todo dia (111 "achados" = 10
   registros), quase todos de jan–abr/2026, com prazo vencido, anexos e páginas de listagem.

O Diário de Goiás tem estrutura aberta (levantada em 01/10/2026 com IP brasileiro):
  · edições do dia ......... /apifront/portal/edicoes/edicoes_from_data/AAAA-MM-DD.json   (normal + suplemento)
  · sumário por órgão ...... /portal/visualizacoes/view_html_diario/{id}   (≈250 matérias; caminho órgão › tipo)
  · texto da matéria ....... /apifront/portal/edicoes/publicacoes_ver_conteudo/{materia}/{id}
  · busca de texto completo  /busca/busca/buscar/query/{pagina}/di:AAAA-MM-DD/df:AAAA-MM-DD/?1=1&q=…

Como funciona agora (sem IA, sem tokens, biblioteca-padrão):
  Fonte A — busca: consultas dirigidas, janela de 7 dias, paginação; a página achada é recortada em matérias
            pelo carimbo "Protocolo NNNNNN" (pega também as PREFEITURAS que publicam no Diário do Estado).
  Fonte B — edição do dia: edições (normal + suplemento) → sumário → texto integral SÓ das matérias cujo título
            ou órgão toca o terceiro setor.
  Fonte C — secretarias: a API pública do WordPress de cada pasta (cultura, social, esporte…), por data.
  → cada matéria é classificada por `src/atos_diario.py` (OPORTUNIDADE · ACOMPANHAR · RUÍDO, com o motivo)
  → o mesmo edital visto em fontes diferentes vira um registro só, com todas as fontes observadas.

Conteúdo coletado é DADO: injeção → quarentena; CPF → [CPF]; o que o texto não diz fica `null`.
"""
from __future__ import annotations

import html as _html
import json
import os
import re
import time
from datetime import date, timedelta
from urllib.parse import quote, urlencode

from . import atos_diario as atos
from .nucleo import (ROOT, append_jsonl, has_prompt_injection, load_json, now_iso, sha256,
                     validate_public_https, write_json)

MOTOR_ID = "do-goias"
CFG = ROOT / "config/diario_goias.json"
ESTADO = ROOT / "estado/diario_goias.json"
QUARENTENA = ROOT / "estado/quarentena.jsonl"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 Eldorado-OSC/1.0"
BASE = "https://diariooficial.abc.go.gov.br"
GOIAS = "https://goias.gov.br"

# títulos/caminhos que valem abrir o texto (Fonte B). O classificador decide depois; aqui só não se perde nada.
INTERESSE_TITULO = re.compile(
    r"CHAMAMENTO|CHAMADA PUBLICA|TERMO DE FOMENTO|TERMO DE COLABORA|13\.019|SOCIEDADE CIVIL|\bOSCS?\b|CEDCA|\bFIA\b|"
    r"\bCEAS\b|\bFEAS\b|IDOSO|PESSOA IDOSA|PNAB|ALDIR BLANC|PAULO GUSTAVO|GOYAZES|FUNDO DE ARTE|ARTE E CULTURA|"
    r"COFINANCIAMENTO|GOIAS SOCIAL|EMENDA|SUBVENC|SEM FINS LUCRATIVOS|ENTIDADES|FILANTROP|INEXIGIBILIDADE DE CHAMAMENTO|"
    r"DISPENSA DE CHAMAMENTO|PROGRAMACAO DE EMENDA|PREMIO|EDITAL DE SELECAO|PROJETOS CULTURAIS")
ORGAO_SOCIAL = re.compile(r"CULTURA|DESENVOLVIMENTO SOCIAL|ESPORTE|VOLUNTARIAS|OVG|DIREITOS HUMANOS|IGUALDADE|"
                          r"CONSELHO ESTADUAL|RETOMADA|MULHER")
TIPO_TITULO = re.compile(r"EDITAL|AVISO|RESULTADO|HOMOLOG|EXTRATO|TERMO|RESOLU|CONVENIO|CHAMAD|RETIFICA|ERRATA|PORTARIA")
SECAO_VETO = re.compile(r"Benefícios Previdenciários|Empresas Privadas|Certidões|Citações|Intimações|Notificações")


def _cfg() -> dict:
    return load_json(CFG) if CFG.exists() else {}


def _em_nuvem() -> bool:
    return bool(os.environ.get("GITHUB_ACTIONS")) and not os.environ.get("ELDORADO_LOCAL_BR")


def _get(url: str, timeout: int = 40, max_bytes: int = 6_000_000, aceitar: str = "*/*") -> bytes:
    from urllib.request import Request, urlopen
    validate_public_https(url)
    req = Request(url, headers={"User-Agent": UA, "Accept": aceitar, "Accept-Language": "pt-BR,pt;q=0.9"})
    with urlopen(req, timeout=timeout) as r:
        dados = r.read(max_bytes + 1)
    if len(dados) > max_bytes:
        raise ValueError("resposta excede limite")
    return dados


def _erro(exc: Exception) -> str:
    code = getattr(exc, "code", None)
    nome = type(exc).__name__
    causa = ("bloqueio (HTTP 403) — o portal recusou este endereço" if code == 403 else
             "tempo esgotado" if "Timeout" in nome or "timed out" in str(exc) else
             "endereço não resolve (DNS)" if nome == "gaierror" else
             f"HTTP {code}" if code else nome)
    return f"{causa}: {str(exc)[:90]}"


def _get_json(url: str, tentativas: int = 3, **kw) -> dict:
    ultimo = None
    for i in range(tentativas):
        try:
            return json.loads(_get(url, aceitar="application/json", **kw).decode("utf-8", "replace"))
        except Exception as exc:  # noqa: BLE001 — vira diagnóstico, nunca silêncio
            ultimo = exc
            if getattr(exc, "code", None) == 403:
                break                                    # bloqueio não melhora com nova tentativa
            time.sleep(min(15, 2.5 * (2 ** i)))
    raise RuntimeError(_erro(ultimo))


def texto_de_html(h: str) -> str:
    h = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", h or "")
    h = re.sub(r"(?i)<br\s*/?>|</(p|div|tr|li|h\d)>", "\n", h)
    t = _html.unescape(re.sub(r"<[^>]+>", " ", h))
    t = re.sub(r"[ \t ]+", " ", t)
    return re.sub(r"\n\s*\n+", "\n", t).strip()


# ─────────────────────────── sumário da edição (Fonte B) ───────────────────────────
_TOKENS = re.compile(r'<li\b|</li>|<span class="folder">(.*?)</span>|'
                     r'<a class="linkMateria"\s+identificador="(\d+)"[^>]*>(.*?)</a>', re.S | re.I)


def materias_do_sumario(h: str) -> list[dict]:
    """[{mid, titulo, caminho}] — o caminho é a árvore do sumário: PODER EXECUTIVO › … › órgão › Atos › Editais.
    O HTML do portal tem atributos colados (`pagina=""data-id=`), por isso tokens e não HTMLParser."""
    out, pilha, nivel = [], [], 0
    for m in _TOKENS.finditer(h or ""):
        tok = m.group(0)
        if tok.lower().startswith("<li"):
            nivel += 1
        elif tok.lower() == "</li>":
            if pilha and pilha[-1][0] == nivel:
                pilha.pop()
            nivel -= 1
        elif m.group(1) is not None:
            pilha.append((nivel, _html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()))
        elif m.group(2):
            tit = _html.unescape(re.sub(r"<[^>]+>", "", m.group(3) or "")).strip()
            out.append({"mid": m.group(2), "titulo": re.sub(r"^#\d+\s*-\s*", "", tit),
                        "caminho": " › ".join(l for _, l in pilha)})
    return out


def interessa(titulo: str, caminho: str) -> bool:
    T, P = atos.sem_acento(titulo).upper(), atos.sem_acento(caminho).upper()
    if SECAO_VETO.search(caminho or "") and not re.search(r"CHAMAMENTO|FOMENTO|COLABORA", T):
        return False
    folha = P.split("›")[-1]
    return bool(INTERESSE_TITULO.search(T) or INTERESSE_TITULO.search(folha) or (ORGAO_SOCIAL.search(P) and TIPO_TITULO.search(T)))


def url_materia(edicao_id, mid) -> str:
    return f"{BASE}/portal/visualizacoes/html/{edicao_id}/#e:{edicao_id}/#m:{mid}"


def fonte_b(hoje: date, cfg: dict, diag: dict, proc: dict) -> list[dict]:
    """Edições dos últimos N dias ainda não processadas → matérias de interesse com texto integral."""
    b = cfg.get("fonte_b", {})
    dias = int(b.get("janela_dias", 3)); lim = int(b.get("max_materias_por_edicao", 60))
    out = []
    for k in range(dias):
        d = (hoje - timedelta(days=k)).isoformat()
        try:
            j = _get_json(f"{BASE}/apifront/portal/edicoes/edicoes_from_data/{d}.json")
        except RuntimeError as exc:
            diag["fontes"]["B"]["falhas"].append(f"{d}: {exc}"); continue
        for it in j.get("itens") or []:
            ed = str(it.get("id"))
            if not ed or ed in proc:
                continue
            try:
                mats = materias_do_sumario(_get(f"{BASE}/portal/visualizacoes/view_html_diario/{ed}").decode("utf-8", "replace"))
            except Exception as exc:  # noqa: BLE001
                diag["fontes"]["B"]["falhas"].append(f"sumário {ed}: {_erro(exc)}"); continue
            diag["fontes"]["B"]["edicoes"] += 1; diag["fontes"]["B"]["materias_no_sumario"] += len(mats)
            sel = [m for m in mats if interessa(m["titulo"], m["caminho"])][:lim]
            for m in sel:
                try:
                    tx = texto_de_html(_get(f"{BASE}/apifront/portal/edicoes/publicacoes_ver_conteudo/{m['mid']}/{ed}").decode("utf-8", "replace"))
                except Exception as exc:  # noqa: BLE001
                    diag["fontes"]["B"]["falhas"].append(f"matéria {m['mid']}: {_erro(exc)}"); continue
                out.append({**m, "texto": tx, "data": d, "edicao": ed, "suplemento": bool(it.get("suplemento")),
                            "url": url_materia(ed, m["mid"]), "fonte": "B"})
                time.sleep(float(b.get("pausa_segundos", 0.3)))
            proc[ed] = {"data": d, "materias": len(mats), "abertas": len(sel), "em": now_iso()}
    diag["fontes"]["B"]["materias_lidas"] = len(out)
    return out


def url_busca(consulta: str, de: str, ate: str, pagina: int = 0) -> str:
    return f"{BASE}/busca/busca/buscar/query/{pagina}/di:{de}/df:{ate}/?1=1&q={quote(consulta)}"


def fonte_a(hoje: date, cfg: dict, diag: dict) -> list[dict]:
    """Busca de texto completo: cada página achada é recortada em matérias pelo carimbo 'Protocolo'."""
    a = cfg.get("fonte_a", {})
    de = (hoje - timedelta(days=int(a.get("janela_dias", 7)))).isoformat(); ate = hoje.isoformat()
    paginas, out, vistas = int(a.get("max_paginas", 5)), [], set()
    for q in a.get("consultas") or []:
        for pg in range(paginas):
            try:
                j = _get_json(url_busca(q, de, ate, pg))
            except RuntimeError as exc:
                diag["fontes"]["A"]["falhas"].append(f"{q[:30]} p{pg}: {exc}"); break
            hits = ((j.get("hits") or {}).get("hits")) or []
            diag["fontes"]["A"]["consultas"] += 1
            for h in hits:
                src = h.get("_source") or {}
                chave = f"{src.get('diario_id')}|{src.get('pagina')}"
                if chave in vistas:
                    continue
                vistas.add(chave)
                marcas = [re.sub(r"<[^>]+>", "", x)[:60] for x in ((h.get("highlight") or {}).get("conteudo") or [])]
                for seg in atos.segmentar_pagina(src.get("conteudo") or ""):
                    if not atos.sem_acento(seg).upper() or not INTERESSE_TITULO.search(atos.sem_acento(seg).upper()):
                        continue
                    out.append({"mid": None, "titulo": None, "caminho": None, "texto": seg, "data": str(src.get("data") or "")[:10],
                                "edicao": str(src.get("diario_id")), "pagina": src.get("pagina"), "marcas": marcas[:2],
                                "url": f"{BASE}/portal/visualizacoes/pdf/{src.get('diario_id')}/#e:{src.get('diario_id')}",
                                "fonte": "A"})
            if len(hits) < 10:
                break
            time.sleep(float(a.get("pausa_segundos", 0.5)))
    diag["fontes"]["A"]["paginas_achadas"] = len(vistas); diag["fontes"]["A"]["materias_lidas"] = len(out)
    return out


def fonte_c(hoje: date, cfg: dict, diag: dict) -> list[dict]:
    """Sites das secretarias (WordPress do Governo de Goiás): posts dos últimos dias com termos de seleção."""
    c = cfg.get("fonte_c", {})
    depois = (hoje - timedelta(days=int(c.get("janela_dias", 10)))).isoformat() + "T00:00:00"
    out, vistos = [], set()
    for site in c.get("sites") or []:
        for termo in c.get("termos") or []:
            url = f"{GOIAS}/{site}/wp-json/wp/v2/posts?" + urlencode(
                {"per_page": 20, "after": depois, "search": termo, "_fields": "id,date,link,title,content"})
            try:
                posts = _get_json(url, tentativas=2)
            except RuntimeError as exc:
                diag["fontes"]["C"]["falhas"].append(f"{site}/{termo}: {exc}"); continue
            diag["fontes"]["C"]["consultas"] += 1
            for p in posts if isinstance(posts, list) else []:
                link = p.get("link")
                if not link or link in vistos:
                    continue
                vistos.add(link)
                tit = texto_de_html((p.get("title") or {}).get("rendered") or "")
                tx = texto_de_html((p.get("content") or {}).get("rendered") or "")
                out.append({"mid": None, "titulo": tit, "caminho": f"Site oficial › {site}", "texto": tx[:12000],
                            "data": str(p.get("date") or "")[:10], "edicao": None, "url": link, "fonte": "C"})
    diag["fontes"]["C"]["materias_lidas"] = len(out)
    return out


# ─────────────────────────── o motor ───────────────────────────
def _registro(ato: dict, m: dict) -> dict:
    nivel, terr = atos.territorio_do_caminho(m.get("caminho"))
    if (ato.get("orgao") or "").startswith("Prefeitura de "):
        nivel, terr = "municipal", "GO/" + ato["orgao"][len("Prefeitura de "):]
    elif (ato.get("orgao") or "").startswith("Prefeitura"):
        nivel = "municipal"                      # município não identificado no trecho: território fica GO, sem inventar
    ev = atos.mascarar_pii(re.sub(r"\s+", " ", ((m.get("titulo") or "") + " " + (m.get("texto") or ""))))[:700]
    titulo = " — ".join(x for x in [ato["orgao"] or "Governo de Goiás",
                                     (m.get("titulo") or (f"Edital nº {ato['numero']}" if ato["numero"] else ato["cabecalho"][:90]))[:140],
                                     (ato["objeto"] or "")[:120] if not m.get("titulo") else None] if x)
    return {
        "id": sha256(f"dogo|{atos.chave_ato(ato['orgao'], ato['numero'], m.get('titulo') or ato['cabecalho'], m.get('data'))}".encode())[:20],
        "status": "capturada", "titulo": titulo[:300], "url": m.get("url"), "fonte_id": MOTOR_ID,
        "fonte_nome": "Diário Oficial do Estado de Goiás" if m["fonte"] in ("A", "B") else "Site oficial do Governo de Goiás",
        "territorio": terr, "uf": "GO", "nivel": nivel, "tipo_fonte": "sensor_diario_oficial", "confianca": "primaria",
        "forma_divulgacao": "diario_oficial_estado" if m["fonte"] in ("A", "B") else "site_oficial",
        "coletado_em": now_iso(), "data_publicacao": m.get("data") or None, "edicao_id": m.get("edicao"),
        "pagina": m.get("pagina"), "numero_edital": ato["numero"], "prazo_texto": ato["prazo_texto"], "fim": ato["fim"],
        "valor_texto": (ato["valores"] or [None])[0], "objeto": ato["objeto"], "orgao": ato["orgao"], "regime": ato["regime"],
        "caminho_sumario": m.get("caminho"), "evidencia": ev, "hash_evidencia": sha256(ev.encode()),
        "fontes_observadas": [m["fonte"]],
        "classificacao_ato": {k: ato[k] for k in ("veredito", "tipo", "regime", "publico", "motivos", "sinais")},
        "sensor": MOTOR_ID, "forca_lexica": 3,
    }


def classificar_lote(materias: list[dict], hoje: date) -> tuple[dict, dict]:
    """→ ({id: registro OPORTUNIDADE}, {id: ato ACOMPANHAR}), já deduplicados entre fontes; e as contagens."""
    oport, acomp, cont = {}, {}, {"OPORTUNIDADE": 0, "ACOMPANHAR": 0, "RUIDO": 0, "quarentena": 0}
    andamento = set()
    for m in materias:
        bruto = (m.get("titulo") or "") + "\n" + (m.get("texto") or "")
        if has_prompt_injection(bruto):
            append_jsonl(QUARENTENA, {"origem": MOTOR_ID, "url": m.get("url"), "em": now_iso(), "hash": sha256(bruto.encode())[:16]})
            cont["quarentena"] += 1; continue
        ato = atos.classificar(m.get("texto") or "", hoje, m.get("data"), titulo=m.get("titulo"), caminho=m.get("caminho"))
        cont[ato["veredito"]] += 1
        if ato["veredito"] == "RUIDO":
            continue
        reg = _registro(ato, m)
        alvo = oport if ato["veredito"] == "OPORTUNIDADE" else acomp
        if reg["id"] in alvo:                                    # mesmo edital, outra fonte → soma a fonte
            ant = alvo[reg["id"]]
            ant["fontes_observadas"] = sorted(set(ant["fontes_observadas"]) | {m["fonte"]})
            if m["fonte"] == "B" and ant.get("url", "").find("/visualizacoes/html/") < 0:
                ant["url"] = reg["url"]                          # a matéria do sumário é o endereço mais preciso
            ant["fim"] = ant.get("fim") or reg["fim"]
            continue
        alvo[reg["id"]] = reg
        if ato["tipo"] == "andamento":
            andamento.add(reg["id"])
    # o mesmo edital tem prazo vencido ou resultado publicado em outra fonte → não está mais aberto
    for i in list(oport):
        a = acomp.get(i)
        if not a:
            continue
        vencido = bool(a.get("fim")) and a["fim"] < hoje.isoformat()
        if vencido or i in andamento:
            r = oport.pop(i)
            r["classificacao_ato"]["veredito"] = "ACOMPANHAR"
            r["classificacao_ato"]["motivos"] = [("prazo escrito em outra publicação já passou (" + a["fim"] + ")") if vencido
                                                 else "a seleção já tem resultado publicado — inscrições encerradas"]
            r["fontes_observadas"] = sorted(set(r["fontes_observadas"]) | set(a.get("fontes_observadas") or []))
            acomp[i] = r
            cont["OPORTUNIDADE"] -= 1; cont["ACOMPANHAR"] += 1
    return oport, acomp, cont


def ler_motor(sensor: dict | None = None, hoje: date | None = None, limites: dict | None = None) -> dict:
    """Leitura do motor 02 com a mesma saída de `sensores.ler`."""
    hoje = hoje or (sensor or {}).get("_data") or date.today()
    cfg = _cfg()
    est = load_json(ESTADO) if ESTADO.exists() else {}
    proc = est.setdefault("edicoes_processadas", {})
    diag = {"paginas_lidas": 0, "links_total": 0, "links_candidatos": 0, "descobertas": [], "pdf_links": 0, "motivo_zero": None,
            "versao": "motor-02 v2 (01/10/2026)", "nuvem": _em_nuvem(),
            "fontes": {k: {"falhas": [], "materias_lidas": 0} for k in "ABC"}}
    diag["fontes"]["A"].update({"consultas": 0, "paginas_achadas": 0})
    diag["fontes"]["B"].update({"edicoes": 0, "materias_no_sumario": 0})
    diag["fontes"]["C"].update({"consultas": 0})
    materias = []
    for nome, fn in (("B", lambda: fonte_b(hoje, cfg, diag, proc)), ("A", lambda: fonte_a(hoje, cfg, diag)),
                     ("C", lambda: fonte_c(hoje, cfg, diag))):
        try:
            materias += fn()
        except Exception as exc:  # noqa: BLE001 — uma fonte nunca derruba as outras
            diag["fontes"][nome]["falhas"].append(f"etapa: {_erro(exc)}")
    oport, acomp, cont = classificar_lote(materias, hoje)
    diag["vereditos"] = cont
    diag["paginas_lidas"] = sum(diag["fontes"][k]["materias_lidas"] for k in "ABC")
    leu_diario = diag["fontes"]["A"]["materias_lidas"] + diag["fontes"]["B"]["edicoes"] > 0 or diag["fontes"]["A"]["consultas"] > 0
    # alarme: dias úteis seguidos sem ler o Diário
    seq = int(est.get("dias_uteis_sem_diario", 0))
    if hoje.weekday() < 5:
        seq = 0 if leu_diario else seq + 1
    est["dias_uteis_sem_diario"] = seq
    if seq >= 3:
        diag["alerta"] = (f"{seq} dias úteis seguidos sem ler o Diário do Estado — "
                          + ("o portal recusa a nuvem: rodar a coleta local (scripts/coleta_brasil.py)" if _em_nuvem() else "conferir a rede"))
    diag["fonte_do_dia"] = {k: ("leu" if diag["fontes"][k]["materias_lidas"] or (k == "B" and diag["fontes"]["B"]["edicoes"]) or
                                (k == "A" and diag["fontes"]["A"]["consultas"]) or (k == "C" and diag["fontes"]["C"]["consultas"])
                                else "falhou" if diag["fontes"][k]["falhas"] else "sem leitura") for k in "ABC"}
    corte = (hoje - timedelta(days=120)).isoformat()
    novos = [{k: a[k] for k in ("id", "titulo", "url", "data_publicacao", "fim", "orgao", "regime", "objeto", "valor_texto",
                                "fontes_observadas", "territorio")} | {"motivo": a["classificacao_ato"]["motivos"][0],
                                                                      "tipo": a["classificacao_ato"]["tipo"]}
             for a in acomp.values()]
    ids = {a["id"] for a in novos}
    est["acompanhar"] = (novos + [a for a in est.get("acompanhar", []) if a["id"] not in ids
                                  and (a.get("data_publicacao") or "") >= corte])[:400]
    est["edicoes_processadas"] = {k: v for k, v in proc.items() if (v.get("data") or "") >= corte}
    est["ultima"] = {"em": now_iso(), "data": hoje.isoformat(), "vereditos": cont, "fonte_do_dia": diag["fonte_do_dia"],
                     "falhas": sum((diag["fontes"][k]["falhas"] for k in "ABC"), [])[:10]}
    hist = est.setdefault("historico", {}); hist[hoje.isoformat()] = {"fontes": diag["fonte_do_dia"], **cont}
    est["historico"] = {k: v for k, v in hist.items() if k >= corte}
    write_json(ESTADO, est)
    falhas = []
    if not materias and any(diag["fontes"][k]["falhas"] for k in "ABC"):
        primeira = next(f for k in "ABC" for f in diag["fontes"][k]["falhas"])
        falhas.append({"url": BASE, "erro": "leitura", "code": None, "waf": None, "causa": primeira})
    if not oport:
        diag["motivo_zero"] = (f"{len(materias)} matéria(s) lida(s) (A {diag['fontes']['A']['materias_lidas']} · "
                               f"B {diag['fontes']['B']['materias_lidas']} · C {diag['fontes']['C']['materias_lidas']}): nenhuma "
                               f"seleção aberta para OSC hoje · {cont['ACOMPANHAR']} a acompanhar · {cont['RUIDO']} ruído"
                               if materias else "nenhuma fonte respondeu: " + (falhas[0]["causa"] if falhas else "sem leitura"))
    return {"sensor": MOTOR_ID, "achados": list(oport.values()), "falhas": falhas,
            "saude": [{"url": BASE, "http": 200, "bytes": len(materias)}] if materias else [],
            "diagnostico": diag, "lido_em": now_iso()}


def atos_para_painel(limite: int = 12) -> list[dict]:
    est = load_json(ESTADO) if ESTADO.exists() else {}
    return sorted(est.get("acompanhar", []), key=lambda a: str(a.get("data_publicacao") or ""), reverse=True)[:limite]


if __name__ == "__main__":
    print(json.dumps(ler_motor()["diagnostico"], ensure_ascii=False, indent=2))
