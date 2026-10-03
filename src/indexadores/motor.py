"""A rodada dos motores indexadores: quem roda agora, por qual rota, com que orçamento — e o que vira indício.

Uma rodada (6 por dia na nuvem; mais as da coleta local no Brasil):
  1. carrega o catálogo (config/indexadores.json) e o estado de cada site;
  2. decide a ROTA de cada site (escada nuvem → ponte → assistida, com volta semanal à rota mais barata);
  3. escolhe os sites DEVIDOS (cadência do site vencida ou trabalho pendente da rodada anterior), P1 primeiro;
  4. lê cada um com o leitor da sua metodologia, dentro do orçamento de requisições e de tempo — o que não couber
     fica para a próxima rodada, com o cursor guardado ("rodar várias vezes por dia até obter todos");
  5. junta os indícios pela chave comum (link oficial; sem ele, título + prazo): o mesmo edital visto em vários
     indexadores é UM indício com várias fontes;
  6. grava o acervo, a entrada do fluxo (estado/agregadores/itens.json), a fila da coleta assistida, os ângulos de
     busca do Piloto, o diário de cada família e o painel.
"""
from __future__ import annotations

import json
import os
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit

from . import extracao as X
from . import ponte as _ponte
from .leitores import LEITORES
from .rede import Rede

ROOT = Path(__file__).resolve().parents[2]
CATALOGO = ROOT / "config/indexadores.json"
SENSORES = ROOT / "config/sensores.json"
PASTA = ROOT / "estado/indexadores"
ESTADO = PASTA / "estado.json"
ACERVO = PASTA / "indicios.json"
CRIADOS = PASTA / "motores_criados.json"        # 02/10: motores criados pelo robô (somados ao catálogo ao carregar)
FILA = PASTA / "fila_assistida.json"
DIARIO = PASTA / "diario.json"
ANGULOS = PASTA / "angulos_piloto.json"
FLUXO = ROOT / "estado/agregadores/itens.json"
PAINEL = ROOT / "docs/dados/indexadores.json"
DELTAS_BRASIL = ROOT / "entrada_manual/indexadores/deltas"     # rodadas feitas no computador do titular (um arquivo por rodada)
ESQUADRA = ROOT / "estado/esquadra.json"
BRT = timezone(timedelta(hours=-3))
PRIO = {"P1": 0, "P2": 1, "P3": 2}
APLICA_BR = re.compile(r"brasil|brazil|am[eé]rica latina|latin america|latam|south america|am[eé]rica do sul|global|worldwide|"
                       r"international|internacional|any country|all countries|todos os pa[ií]ses|open to all|sul global|global south|"
                       r"developing countries|pa[ií]ses em desenvolvimento|ibero|lusofon|portuguese[- ]speaking|cplp", re.I)


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return padrao


def _gravar(p: Path, v, indent: int | None = 1) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(v, ensure_ascii=False, indent=indent) + "\n", encoding="utf-8")
    tmp.replace(p)


def agora_utc() -> datetime:
    return datetime.now(timezone.utc)


# ------------------------------------------------------------------ catálogo e rotas
def catalogo() -> dict:
    """O catálogo editado (config/indexadores.json) + os motores que o robô criou (estado/indexadores/motores_criados.json)."""
    cat = _j(CATALOGO, {"sites": [], "motores": {}, "limites": {}})
    cri = _j(CRIADOS, {"sites": []})
    ids = {s["id"] for s in cat.get("sites") or []}
    for s in cri.get("sites") or []:
        if s.get("tipo") == "instancia_mapas_culturais":   # instância nova entra no motor Mapas Culturais
            mc = next((x for x in cat.get("sites") or [] if x.get("leitor") == "mapas_culturais"), None)
            if mc is not None and s["host"] not in {i.get("host") for i in mc.get("instancias") or []}:
                mc.setdefault("instancias", []).append({"host": s["host"], "uf": None, "nome": s["host"], "confirmada": False, "criada_automaticamente": True})
            continue
        if s.get("id") not in ids:
            cat.setdefault("sites", []).append(s)
            cat.setdefault("motores", {})[s["motor"]] = {"nome": f"{s['nome']} — editais (motor criado automaticamente, em observação)", "local": s["nome"],
                "finalidade": "fonte oficial que apareceu em indícios sem ter motor", "fonte": (s.get("listas") or [None])[0],
                "metodo": "listagem HTML genérica", "criado_automaticamente": True, "criado_em": s.get("criado_em")}
    return cat


MOTORES_PRAZO_DO_TEXTO = ("site-observatorio-terceiro-setor", "site-abcr", "site-funarte", "site-rede-comua", "site-fundo-baoba")


def corrigir_prazos_do_ano_seguinte(gravar: bool = True, acervo: dict | None = None) -> int:
    """03/10 (estudo dos motores 01–39): o leitor antigo empurrava 'até 2 de setembro' (sem ano) para o PRÓXIMO ano a
    partir de hoje. Nos motores que leem o prazo do texto (26, 28, 29, 31, 32), o prazo do ano seguinte num post de
    2026 volta para 2026 quando a data cabe depois da publicação. Idempotente; os outros motores não mudam."""
    A = acervo if acervo is not None else _j(ACERVO, {"itens": {}}); cat = catalogo()
    sm = {s["id"]: s.get("motor") for s in cat.get("sites") or []}
    n = 0
    for x in (A.get("itens") or {}).values():
        pz, pub = str(x.get("prazo") or ""), str(x.get("publicado") or "")[:10]
        if len(pz) < 10 or len(pub) < 10 or sm.get(x.get("fonte")) not in MOTORES_PRAZO_DO_TEXTO:
            continue
        if int(pz[:4]) != int(pub[:4]) + 1:
            continue
        try:
            y = date(int(pub[:4]), int(pz[5:7]), int(pz[8:10])).isoformat()
        except ValueError:
            continue
        if y >= pub:
            x["prazo_antes_da_correcao"] = pz; x["prazo"] = y; n += 1
    if n and gravar and acervo is None:
        _gravar(ACERVO, A)
    return n


def registrar_motores_que_faltam(hoje: date, gravar: bool = True) -> list[dict]:
    """Depois da rodada: domínio oficial sem motor, visto em 2+ indícios, vira motor (em observação). Um por vez, sem repetir."""
    cri = _j(CRIADOS, {"sites": []})
    ja = {s["id"] for s in cri.get("sites") or []}
    novos = [dict(m, criado_em=hoje.isoformat()) for m in motores_que_faltam(_j(ACERVO, {"itens": {}}), catalogo()) if m["id"] not in ja]
    if novos and gravar:
        cri["sites"] = (cri.get("sites") or []) + novos
        cri["regra"] = "02/10/2026 (titular): quando a oportunidade não tem motor, ele é criado — leitor de listagem genérico, em observação até render indício."
        _gravar(CRIADOS, cri)
    return novos


def hosts_exige_brasil() -> set[str]:
    return set((_j(SENSORES, {}).get("exige_brasil") or {}).get("dominios") or [])


def _host(site: dict) -> str:
    u = site.get("url") or (site.get("listas") or [""])[0]
    return (urlsplit(u).hostname or "").lower()


def rota_efetiva(site: dict, st: dict, hoje: date, exige: set[str], lim: dict) -> tuple[str, str]:
    """(rota, motivo). Rotas: nuvem | ponte | assistida | delegado."""
    if site.get("leitor") == "delegado":
        return "delegado", f"lido pelo motor {site.get('delegado_a')}"
    if site.get("leitor") == "assistido" or site.get("rota") == "assistida":
        return "assistida", {"robots": "o robots.txt proíbe robôs", "javascript": "a página só abre com JavaScript",
                             "bloqueio_http": "o site recusa leitura automática", "rota_a_levantar": "a rota ainda precisa ser levantada",
                             "repete_prosas": "a página repete o widget do Prosas"}.get(site.get("motivo"), site.get("motivo") or "coleta assistida")
    base = site.get("rota", "nuvem")
    if base == "nuvem" and _host(site) in exige:
        base = "ponte"
    esc = st.get("rota")
    if esc and esc != base:
        desde = st.get("rota_desde") or hoje.isoformat()
        espera = 30 if esc == "assistida_robots" else int(lim.get("dias_para_tentar_rota_mais_barata", 7))
        if (hoje - date.fromisoformat(desde[:10])).days >= espera:
            return base, f"nova tentativa pela rota {base} (escalado para {esc} em {desde[:10]})"
        return ("assistida" if esc == "assistida_robots" else esc), st.get("rota_motivo") or f"escalado para {esc}"
    return base, ("o portal recusa IP estrangeiro (config/sensores.json → exige_brasil)" if base == "ponte" and site.get("rota", "nuvem") == "nuvem"
                  else site.get("nota") or "")


def devido(site: dict, st: dict, agora: datetime) -> bool:
    if st.get("pendente"):
        return True
    ult = st.get("ultima")
    if not ult:
        return True
    try:
        u = datetime.fromisoformat(ult)
    except ValueError:
        return True
    return agora - u >= timedelta(hours=float(site.get("cadencia_horas") or 6)) - timedelta(minutes=20)


def _escalar(site: dict, st: dict, res: dict, rota: str, hoje: date, lim: dict) -> None:
    """Escada de rotas a partir do resultado da leitura."""
    tipos = [f.get("tipo") for f in res.get("falhas") or []]
    leu = res.get("lidas", 0) > 0
    if "robots" in tipos and not leu:
        st.update(rota="assistida_robots", rota_desde=hoje.isoformat(), rota_motivo="o robots.txt proíbe robôs — coleta assistida")
        return
    if leu:
        st["falhas_seguidas"] = 0
        if st.get("rota") and rota == site.get("rota", "nuvem"):
            st.pop("rota", None); st.pop("rota_desde", None); st.pop("rota_motivo", None)      # a rota barata voltou a funcionar
        return
    if "ponte_indisponivel" in tipos:
        st.setdefault("aguardando_ponte_desde", hoje.isoformat())
        return
    if not tipos or "orcamento" in tipos:
        return
    st["falhas_seguidas"] = int(st.get("falhas_seguidas") or 0) + 1
    if rota == "nuvem" and any(t in ("geo", "rede", "waf") for t in tipos) and st["falhas_seguidas"] >= int(lim.get("falhas_para_ponte", 2)):
        st.update(rota="ponte", rota_desde=hoje.isoformat(), falhas_seguidas=0,
                  rota_motivo=f"{st.get('falhas_seguidas_total', 0) + int(lim.get('falhas_para_ponte', 2))} falhas pela nuvem ({', '.join(sorted(set(tipos)))}) — ponte Brasil")
    elif rota == "ponte" and any(t in ("geo", "waf", "http") for t in tipos) and st["falhas_seguidas"] >= int(lim.get("falhas_para_assistida", 3)):
        st.update(rota="assistida", rota_desde=hoje.isoformat(), falhas_seguidas=0,
                  rota_motivo=f"bloqueado também pelo IP brasileiro ({', '.join(sorted(set(tipos)))}) — coleta assistida no navegador")


# ------------------------------------------------------------------ acervo de indícios
def _fundir(acervo: dict, novos: list[dict], hoje: str) -> tuple[int, int]:
    itens, chaves = acervo.setdefault("itens", {}), acervo.setdefault("chaves", {})
    n_novos = n_atual = 0
    for it in novos:
        ks = X.chaves(it)
        k = ks[0]
        alvo = next((chaves[x] for x in ks if chaves.get(x) in itens), None) or (it["id"] if it["id"] in itens else None)
        if alvo and alvo in itens:
            a = itens[alvo]
            for campo, v in it.items():
                if campo in ("id", "primeiro_visto", "fontes", "paginas"):
                    continue
                if v not in (None, "", []) and (a.get(campo) in (None, "", []) or campo in ("visto_em", "prazo", "perfil", "perfil_motivo", "rota")):
                    a[campo] = v
            a["fontes"] = sorted(set(a.get("fontes") or [a.get("fonte")]) | {it["fonte"]})
            pags = list(dict.fromkeys((a.get("paginas") or [a.get("pagina_agregador")]) + [it.get("pagina_agregador")]))
            a["paginas"] = [p for p in pags if p][:8]
            for x in ks + X.chaves(a):
                chaves[x] = alvo
            n_atual += 1
        else:
            it = dict(it)
            it["primeiro_visto"] = hoje
            it["fontes"] = [it["fonte"]]
            it["paginas"] = [it.get("pagina_agregador")]
            itens[it["id"]] = it
            for x in ks:
                chaves[x] = it["id"]
            n_novos += 1
    return n_novos, n_atual


def _podar_acervo(acervo: dict, hoje: date, lim: dict) -> int:
    corte_enc = (hoje - timedelta(days=int(lim.get("dias_guardar_encerrados", 30)))).isoformat()
    corte_sem = (hoje - timedelta(days=90)).isoformat()
    itens = acervo.get("itens") or {}
    fora = [i for i, x in itens.items() if (x.get("prazo") and x["prazo"] < corte_enc) or (not x.get("prazo") and (x.get("visto_em") or "") < corte_sem)]
    for i in fora:
        del itens[i]
    validos = set(itens)
    acervo["chaves"] = {k: v for k, v in (acervo.get("chaves") or {}).items() if v in validos}
    return len(fora)


def aplica_brasil(x: dict, sites: dict) -> bool:
    if (x.get("pais") or "BR") == "BR":
        return True
    if any((sites.get(f) or {}).get("internacional") for f in x.get("fontes") or [x.get("fonte")]):
        return True                                     # indexador já filtrado para o Brasil (fundsforNGOs tag Brasil, IAF)
    return bool(APLICA_BR.search(f"{x.get('titulo') or ''} {x.get('resumo') or ''}"))


ORDEM_PADRAO = ("GO", "BR", "internacional", "outros_estados")


def grupo_territorial(x: dict, sites: dict | None = None) -> str:
    """Decisão do titular (02/10/2026): Goiás → Brasil (abrangência nacional) → internacional → outros estados.
    Internacional: país diferente do Brasil, ou país em branco vindo de indexador internacional (fundsforNGOs, IAF,
    embaixadas) — o leitor deixa o país em branco quando a fonte é estrangeira."""
    uf = (x.get("uf") or "").upper()
    if uf == "GO":
        return "GO"
    pais = x.get("pais")
    if pais and pais != "BR":
        return "internacional"
    if not pais and any((sites or {}).get(f, {}).get("internacional") for f in x.get("fontes") or [x.get("fonte")]):
        return "internacional"
    return "BR" if uf in ("", "BR") else "outros_estados"


def por_grupo(entrada: list[dict], sites: dict | None = None) -> dict:
    out = {g: 0 for g in ORDEM_PADRAO}
    for x in entrada:
        g = grupo_territorial(x, sites)
        out[g] = out.get(g, 0) + 1
    return out


def entrada_do_fluxo(acervo: dict, sites: dict, hoje: date, lim: dict) -> tuple[list[dict], dict]:
    """O que segue para o fluxo das oportunidades. Fica de fora (e continua no acervo, auditável): prazo vencido,
    público claramente fora do perfil de OSC, quarentena e chamada estrangeira que não se aplica ao Brasil."""
    h = hoje.isoformat()
    corte_sem = (hoje - timedelta(days=int(lim.get("dias_sem_prazo_no_fluxo", 60)))).isoformat()
    motivos = {"prazo_vencido": 0, "fora_do_perfil": 0, "quarentena": 0, "nao_se_aplica_ao_brasil": 0, "sem_prazo_antigo": 0, "acima_do_limite": 0}
    vivos = []
    for x in (acervo.get("itens") or {}).values():
        if x.get("prazo") and x["prazo"] < h:
            motivos["prazo_vencido"] += 1; continue
        if not x.get("prazo") and (x.get("publicado") or x.get("primeiro_visto") or h) < corte_sem:
            motivos["sem_prazo_antigo"] += 1; continue
        if x.get("quarentena"):
            motivos["quarentena"] += 1; continue
        if x.get("perfil") == "fora":
            motivos["fora_do_perfil"] += 1; continue
        if not aplica_brasil(x, sites):
            motivos["nao_se_aplica_ao_brasil"] += 1; continue
        vivos.append(x)
    ordem = {g: i for i, g in enumerate(lim.get("ordem_do_fluxo") or ORDEM_PADRAO)}
    vivos.sort(key=lambda x: (ordem.get(grupo_territorial(x, sites), len(ordem)), x.get("prazo") or "9999", x.get("id") or ""))
    mx = int(lim.get("indicios_no_fluxo_max", 1000))
    motivos["acima_do_limite"] = max(0, len(vivos) - mx)
    campos = ("id", "fonte", "titulo", "pagina_agregador", "link_oficial", "prazo", "uf", "visto_em", "primeiro_visto", "publicado",
              "financiador", "valor", "areas", "pais", "motor", "fontes", "perfil", "tipo", "rota")
    return [{k: x.get(k) for k in campos if x.get(k) not in (None, "", [])} for x in vivos[:mx]], motivos


# ------------------------------------------------------------------ fila assistida e ângulos do Piloto
def montar_fila(cat: dict, est: dict, rotas: dict, hoje: date, acervo: dict | None = None) -> dict:
    sites = {s["id"]: s for s in cat.get("sites") or []}
    pt = cat.get("ponte") or {}
    dias = int(pt.get("dias_sem_leitura_para_navegador", 3))
    computador = pt.get("escolha") == "computador_do_titular"
    indiretos: dict = {}
    for x in ((acervo or {}).get("itens") or {}).values():
        if x.get("rota_indireta_de"):
            indiretos[x["rota_indireta_de"]] = indiretos.get(x["rota_indireta_de"], 0) + 1
    itens = []
    for sid, (rota, motivo) in rotas.items():
        s, st = sites[sid], (est.get("sites") or {}).get(sid) or {}
        espera = st.get("aguardando_ponte_desde")
        esperando = rota == "ponte" and espera and (hoje - date.fromisoformat(espera)).days >= dias
        if rota != "assistida" and not esperando:
            continue
        if s.get("mesmo_que"):
            continue
        cap = (est.get("capturas") or {}).get(sid) or {}
        como = ("levantar a rota: abrir o site, achar a página de editais e registrá-la no catálogo"
                if s.get("motivo") == "rota_a_levantar" else
                "abrir a página e clicar no botão 'Capturar indícios' (docs/coleta-assistida.html), depois enviar o arquivo")
        if rota == "assistida":
            mot = motivo
        elif computador:
            mot = (f"o computador do titular não lê este site desde {espera} (computador desligado ou coleta parada): "
                   "leia pelo navegador enquanto isso")
        else:
            mot = f"aguardando a ponte Brasil desde {espera}: leia pelo navegador enquanto isso"
        itens.append({"id": sid, "nome": s.get("nome"), "abrir": s.get("url") or (s.get("listas") or [None])[0],
                      "motivo": mot, "como": como, "prioridade": s.get("prioridade", "P3"), "rota_indireta": s.get("rota_indireta"),
                      "caminhos_indiretos": s.get("caminhos_indiretos"), "cobertos_pela_rota_indireta": indiretos.get(sid, 0),
                      "ultima_captura": cap.get("em"), "itens_ultima_captura": cap.get("itens")})
    itens.sort(key=lambda x: (PRIO.get(x["prioridade"], 3), x.get("ultima_captura") or ""))
    return {"em": agora_utc().isoformat(timespec="seconds"),
            "regra": "sites que o robô não pode ler (robots.txt, JavaScript, bloqueio que nem o IP brasileiro passa) ou cuja rota ainda "
                     "precisa ser levantada. O titular — ou o Claude no Chrome — abre cada página e captura o que ela mostra; o arquivo vai "
                     "para entrada_manual/indexadores/ e vira indício na próxima rodada. Enquanto isso, a rota indireta e o Piloto cobrem.",
            "itens": itens}


def angulos_piloto(cat: dict, rotas: dict) -> list[dict]:
    out = []
    for s in cat.get("sites") or []:
        if rotas.get(s["id"], ("",))[0] == "assistida" and s.get("angulo_piloto"):
            out.append({"id": f"idx-{s['id']}", "nivel": "internacional" if s.get("internacional") else "nacional", "alvo": "plataforma",
                        "pergunta": s["angulo_piloto"], "origem": "motores indexadores — site fechado a robôs"})
    return out


# ------------------------------------------------------------------ diário (calendário do painel)
def _registrar_dia(diario: dict, motor: str, hoje: str, novos: int, falhas: int, sites_ok: int, exemplo: dict | None) -> None:
    d = diario.setdefault(motor, {}).setdefault(hoje, {"achados": 0, "falhas": 0, "rodadas": 0})
    d["achados"] = int(d.get("achados") or 0) + novos
    d["falhas"] = falhas
    d["rodadas"] = int(d.get("rodadas") or 0) + 1
    d["cor"] = "vermelho" if (falhas and not sites_ok) else ("amarelo" if d["achados"] else "azul")
    if exemplo and novos:
        d["trecho"], d["url"] = X.limpar(exemplo.get("titulo"), 160), exemplo.get("link_oficial") or exemplo.get("pagina_agregador")
    corte = (date.fromisoformat(hoje) - timedelta(days=45)).isoformat()
    for k in [k for k in diario[motor] if k < corte]:
        del diario[motor][k]


# ------------------------------------------------------------------ a rodada
def registrar_leitura(st: dict, res: dict, site: dict, desde: str | None, extra: int, agora: datetime) -> dict:
    """02/10 (titular): registro COMPACTO de cada leitura — hash do que foi lido, quantidade, cobertura das datas de
    publicação e lacuna. Lacuna = a leitura não chegou até a data da anterior e esgotou as páginas permitidas: a próxima
    volta mais páginas (até 10 a mais). Guarda só as 30 últimas; o texto útil (título, datas, link) fica no acervo."""
    import hashlib
    itens = res.get("itens") or []
    datas = sorted(d for d in (str(x.get("publicado") or "")[:10] for x in itens) if len(d) == 10)
    h = hashlib.sha1("\n".join(sorted(str(x.get("chave") or x.get("id")) for x in itens)).encode()).hexdigest()[:12]
    paginas = int(site.get("paginas_retroativas") or 1)
    lacuna = bool(desde and datas and datas[0] > desde and int(res.get("lidas") or 0) >= paginas and not res.get("delegado"))
    st["paginas_extra"] = min(extra + 1, 10) if lacuna else 0
    reg = {"em": agora.isoformat(timespec="seconds"), "h": h, "n": len(itens), "de": datas[0] if datas else None,
           "ate": datas[-1] if datas else None, "desde": desde, "lacuna": lacuna, "paginas": int(res.get("lidas") or 0)}
    st["leituras"] = (list(st.get("leituras") or []) + [reg])[-30:]
    return reg


def motores_que_faltam(acervo: dict, cat: dict, minimo: int = 2) -> list[dict]:
    """02/10 (titular): indício cujo SITE OFICIAL não tem motor, visto em `minimo` indícios ou mais, gera um motor novo
    (leitor genérico de listagem, em observação). Nunca para domínio proibido, de buscador ou já coberto."""
    from collections import Counter
    try:
        from ..indexacao_livros import mapa_dominios, host, GENERICOS
        M = mapa_dominios()
    except Exception:  # noqa: BLE001
        return []
    def _todas_urls(o):                               # QUALQUER endereço do site (ex.: as instâncias do Mapas Culturais)
        if isinstance(o, dict):
            return [u for v in o.values() for u in _todas_urls(v)]
        if isinstance(o, list):
            return [u for v in o for u in _todas_urls(v)]
        return [o] if isinstance(o, str) and o.startswith("http") else []
    ja = {str(i.get("host") or "").lower().removeprefix("www.") for x in cat.get("sites") or [] for i in x.get("instancias") or []}
    ja |= {host(u) for x in (cat.get("sites") or []) + [d for d in cat.get("descartados") or [] if isinstance(d, dict)] for u in _todas_urls(x)}
    cont, exemplo = Counter(), {}
    for x in (acervo.get("itens") or {}).values():
        u = x.get("link_oficial")
        d = host(u) if u else ""
        if not d or d in GENERICOS or d in ja or any(d == k or d.endswith("." + k) for k in M) or X._republicador(u):
            continue
        if x.get("perfil") == "fora" or not (d.endswith(".br") or x.get("pais") == "BR"):
            continue                                  # só o que se aplica a OSC no Brasil vira motor
        cont[d] += 1; exemplo.setdefault(d, u)
    out = []
    for d, n in cont.most_common(10):
        if n >= minimo:
            _p = urlsplit(exemplo[d]); _seg = [x for x in _p.path.split("/") if x]
            base = f"{_p.scheme}://{_p.netloc}/" + ("/".join(_seg[:-1]) + "/" if len(_seg) > 1 else "")   # a LISTAGEM (pasta de cima)
            if "/oportunidade/" in exemplo[d]:            # é uma instância do Mapas Culturais: ALIMENTA o motor existente
                out.append({"id": "instancia-" + re.sub(r"[^a-z0-9]+", "-", d)[:40].strip("-"), "tipo": "instancia_mapas_culturais",
                            "host": d, "nome": d, "motor": "site-mapas-culturais", "indicios_que_motivaram": n, "listas": [base]})
                continue
            out.append({"id": "auto-" + re.sub(r"[^a-z0-9]+", "-", d)[:40].strip("-"), "nome": d, "motor": "site-auto-" + re.sub(r"[^a-z0-9]+", "-", d)[:40].strip("-"),
                        "leitor": "html_listagem", "listas": [base], "cadencia_horas": 24, "prioridade": "baixa", "rota": "nuvem",
                        "paginas_retroativas": 1, "criado_automaticamente": True, "situacao": "em observação", "indicios_que_motivaram": n})
    return out


def rodada(motores: list[str] | None = None, sites: list[str] | None = None, rota: str | None = None,
           agora: datetime | None = None, rede: Rede | None = None, gravar: bool = True, forcar: bool = False,
           extra: dict | None = None, delta_em: Path | None = None) -> dict:
    """Lê os sites devidos e devolve o resumo. O que a rodada produziu (itens, estado dos sites lidos, diário) vira um
    DELTA que é aplicado sobre os arquivos do repositório — na nuvem, o fluxo reaplica o mesmo delta sobre o main mais
    recente antes de gravar, para não apagar o que a coleta no Brasil ou a coleta assistida gravaram no meio tempo."""
    cat = catalogo()
    lim = cat.get("limites") or {}
    agora = agora or agora_utc()
    hoje = agora.astimezone(BRT).date()
    est = _j(ESTADO, {"sites": {}})
    est.setdefault("sites", {})
    exige = hosts_exige_brasil()
    local = _ponte.local_brasil()
    rota = rota or ("ponte" if local else "nuvem")
    ag = cat.get("agente") or {}
    robots, http_cache = dict(est.get("robots") or {}), dict(est.get("http_cache") or {})
    rede = rede or Rede(token=ag.get("token_robots", "EldoradoIndexadores"), user_agent=ag.get("user_agent", "EldoradoIndexadores/1.0"),
                        pausa_padrao=float(lim.get("pausa_padrao_s", 1.5)), timeout=int(lim.get("timeout_s", 25)),
                        bytes_max=int(lim.get("bytes_max", 4_000_000)), orcamento=int(lim.get("requisicoes_por_rodada", 700)),
                        tempo_max=float(lim.get("tempo_max_rodada_s", 1500)), local_brasil=local,
                        robots_cache=robots, http_cache=http_cache)
    ctx_base = {"hoje": hoje, "limites": lim, "estado_motores": _j(ESQUADRA, {})}
    por_id = {s["id"]: s for s in cat.get("sites") or []}
    rotas = {sid: rota_efetiva(s, est["sites"].get(sid) or {}, hoje, exige, lim) for sid, s in por_id.items()}
    delta = {"versao": 1, "em": agora.isoformat(timespec="seconds"), "hoje": hoje.isoformat(), "rota": rota, "local_brasil": local,
             "itens": list((extra or {}).get("itens") or []), "sites": {}, "diario": {},
             "importados": dict((extra or {}).get("importados") or {}), "capturas": dict((extra or {}).get("capturas") or {})}

    def elegivel(sid):
        r = rotas[sid][0]
        if r == "assistida":
            return False
        if r == "delegado":
            return True
        if rota == "ponte":                          # coleta no Brasil: só o que precisa de IP brasileiro
            return r == "ponte"
        return r == "nuvem" or (r == "ponte" and _ponte.configurada())
    if rota == "nuvem" and not _ponte.configurada():
        for sid, (r, _m) in rotas.items():           # sem ponte na nuvem: o site espera a coleta no Brasil (e, após 3 dias, o navegador)
            if r == "ponte" and not (est["sites"].get(sid) or {}).get("aguardando_ponte_desde"):
                delta["sites"][sid] = dict(est["sites"].get(sid) or {}, aguardando_ponte_desde=hoje.isoformat())
    fila = [s for sid, s in por_id.items() if elegivel(sid) and (not motores or s.get("motor") in motores)
            and (not sites or sid in sites) and (forcar or devido(s, est["sites"].get(sid) or {}, agora))]
    fila.sort(key=lambda s: (PRIO.get(s.get("prioridade"), 3), 0 if not (est["sites"].get(s["id"]) or {}).get("ultima") else 1,
                             (est["sites"].get(s["id"]) or {}).get("ultima") or ""))
    resumo = {"em": delta["em"], "rota_da_execucao": rota, "local_brasil": local, "ponte_configurada": _ponte.configurada(),
              "sites": {}, "lidos": 0}
    por_motor: dict = {}
    for s in fila:
        sid = s["id"]
        st = dict(est["sites"].get(sid) or {})
        r_site, _motivo = rotas[sid]
        if rede.esgotado():
            st["pendente"] = True
            delta["sites"][sid] = st
            resumo["sites"][sid] = {"adiado": "orçamento da rodada esgotado"}
            continue
        ctx = dict(ctx_base, via=("ponte" if r_site == "ponte" else "direta"), rota=r_site)
        # 02/10 (titular): LEITURA A PARTIR DA ÚLTIMA LEITURA — se a anterior deixou lacuna, esta volta mais páginas
        s_ef = dict(s)
        _extra = int(st.get("paginas_extra") or 0)
        if _extra:
            s_ef["paginas_retroativas"] = int(s.get("paginas_retroativas") or 1) + _extra
        _desde = str(st.get("ultima") or "")[:10] or None
        try:
            res = LEITORES[s["leitor"]](s_ef, rede, st, ctx)
        except Exception as e:                       # um site quebrado não derruba a rodada
            res = {"itens": [], "falhas": [{"url": s.get("url"), "tipo": "erro", "detalhe": f"{type(e).__name__}: {str(e)[:160]}"}], "lidas": 0, "diag": {}}
        if not res.get("delegado"):
            _escalar(s, st, res, r_site, hoje, lim)
        st.update(ultima=agora.isoformat(timespec="seconds"), pendente=bool(res.get("pendente")), lidas_ultima=res.get("lidas", 0),
                  itens_ultima=len(res.get("itens") or []), falhas_ultima=(res.get("falhas") or [])[:5],
                  diag=res.get("diag") or {}, rota_ultima=r_site)
        if res.get("lidas"):
            st.pop("aguardando_ponte_desde", None)
        registrar_leitura(st, res, s_ef, _desde, _extra, agora)
        delta["sites"][sid] = st
        delta["itens"].extend(res.get("itens") or [])
        resumo["lidos"] += 1
        resumo["sites"][sid] = {"rota": r_site, "lidas": res.get("lidas", 0), "itens": len(res.get("itens") or []),
                                "falhas": [f"{f.get('tipo')}: {f.get('detalhe')}" for f in (res.get("falhas") or [])[:3]],
                                "pendente": bool(res.get("pendente"))}
        m = por_motor.setdefault(s.get("motor"), {"itens": [], "falhas": 0, "ok": 0})
        m["itens"].extend(x["id"] for x in res.get("itens") or [])
        if res.get("falhas") and not res.get("lidas") and not res.get("delegado"):
            m["falhas"] += 1
        elif res.get("lidas") or res.get("delegado"):
            m["ok"] += 1
    delta["diario"] = {mid: {"itens": m["itens"], "falhas": m["falhas"], "ok": m["ok"]} for mid, m in por_motor.items()}
    if rota == "ponte" or local:
        # o delta do computador vira arquivo no git: leva só o cache dos sites que ele leu
        hosts = {(urlsplit(u).hostname or "").lower() for s in fila
                 for u in [s.get("url"), s.get("pagina")] + list(s.get("listas") or []) if u}
        robots = {h: v for h, v in robots.items() if h in hosts}
        http_cache = {u: v for u, v in http_cache.items() if (urlsplit(u).hostname or "").lower() in hosts}
        delta["ultima_coleta_brasil"] = {"em": delta["em"], "sites": len(fila)}
    delta["robots"], delta["http_cache"] = robots, http_cache
    resumo["requisicoes"] = rede.usadas
    if delta_em:
        _gravar(Path(delta_em), delta, indent=None)
    resumo.update(aplicar(delta, gravar=gravar))
    try:                                             # 02/10: oportunidade sem motor → o motor é criado
        resumo["motores_criados"] = [m["motor"] for m in registrar_motores_que_faltam(hoje, gravar=gravar)]
    except Exception as e:  # noqa: BLE001 — nunca derruba a rodada
        resumo["motores_criados"] = f"falhou: {type(e).__name__}"
    return resumo


def aplicar(delta: dict, gravar: bool = True) -> dict:
    """Aplica o delta de uma rodada sobre os arquivos ATUAIS do repositório e regrava as saídas."""
    cat = catalogo()
    lim = cat.get("limites") or {}
    hoje = date.fromisoformat(delta.get("hoje") or agora_utc().astimezone(BRT).date().isoformat())
    est = _j(ESTADO, {"sites": {}})
    est.setdefault("sites", {})
    for sid, st in (delta.get("sites") or {}).items():
        est["sites"][sid] = st
    est.setdefault("robots", {}).update(delta.get("robots") or {})
    hc = est.setdefault("http_cache", {}); hc.update(delta.get("http_cache") or {})
    if len(hc) > 3000:
        for k in list(hc)[: len(hc) - 3000]:
            del hc[k]
    est.setdefault("importados", {}).update(delta.get("importados") or {})
    est.setdefault("capturas", {}).update(delta.get("capturas") or {})
    if delta.get("ultima_coleta_brasil"):
        est["ultima_coleta_brasil"] = delta["ultima_coleta_brasil"]
    acervo = _j(ACERVO, {"itens": {}, "chaves": {}})
    if not acervo.get("itens"):
        _migrar_antigo(acervo, hoje)
    ids_antes = set(acervo.get("itens") or {})
    n, a = _fundir(acervo, delta.get("itens") or [], hoje.isoformat())
    diario = _j(DIARIO, {})
    for mid, d in (delta.get("diario") or {}).items():
        novos = [i for i in dict.fromkeys(d.get("itens") or []) if i not in ids_antes]
        ex = next((acervo["itens"].get(i) for i in novos if (acervo["itens"].get(i) or {}).get("link_oficial")), None) or \
            (acervo["itens"].get(novos[0]) if novos else None)
        _registrar_dia(diario, mid, hoje.isoformat(), len(novos), int(d.get("falhas") or 0), int(d.get("ok") or 0), ex)
    podados = _podar_acervo(acervo, hoje, lim)
    por_id = {s["id"]: s for s in cat.get("sites") or []}
    exige = hosts_exige_brasil()
    rotas = {sid: rota_efetiva(s, est["sites"].get(sid) or {}, hoje, exige, lim) for sid, s in por_id.items()}
    entrada, fora = entrada_do_fluxo(acervo, por_id, hoje, lim)
    if gravar:
        est["em"] = delta.get("em") or agora_utc().isoformat(timespec="seconds")
        try:                                         # 03/10: os prazos do ano seguinte saem ANTES de gravar (o fluxo 16
            corrigir_prazos_do_ano_seguinte(acervo=acervo)   # reaplica o delta sobre o main — correção fora daqui se perdia)
        except Exception:  # noqa: BLE001
            pass
        _gravar(ESTADO, est)
        _gravar(ACERVO, acervo)
        _gravar(DIARIO, diario)
        _gravar(FILA, montar_fila(cat, est, rotas, hoje, acervo))
        _gravar(ANGULOS, {"em": est["em"], "angulos": angulos_piloto(cat, rotas)})
        _gravar(FLUXO, {"em": est["em"], "regra": "INDÍCIOS dos motores indexadores (config/indexadores.json): link da fonte oficial quando o "
                                                  "indexador o traz; o prazo é pista até a fonte oficial confirmar.",
                        "ordem_do_fluxo": list(lim.get("ordem_do_fluxo") or ORDEM_PADRAO), "limite": int(lim.get("indicios_no_fluxo_max", 1000)),
                        "por_grupo": por_grupo(entrada, por_id), "por_fonte": _por_fonte(entrada), "fora_do_fluxo": fora, "itens": entrada})
        _gravar(PAINEL, painel(cat, est, acervo, rotas, entrada, hoje), indent=None)
    return {"novos": n, "atualizados": a, "podados": podados, "no_fluxo": len(entrada), "por_grupo": por_grupo(entrada, por_id),
            "fora_do_fluxo": fora, "acervo": len(acervo.get("itens") or {})}


def deltas_do_brasil() -> list[Path]:
    return sorted(DELTAS_BRASIL.glob("*.json")) if DELTAS_BRASIL.exists() else []


def aplicar_deltas_do_brasil(remover: bool = False, gravar: bool = True) -> dict:
    """Ponte pelo computador do titular (decisão de 02/10/2026): cada rodada feita lá é enviada como um ARQUIVO NOVO de
    delta em entrada_manual/indexadores/deltas/ — arquivo novo nunca conflita no git. O fluxo 16 aplica esses deltas,
    em ordem, sobre o main mais novo (antes do delta da própria nuvem) e os apaga no mesmo commit."""
    feitos, recusados = [], []
    for arq in deltas_do_brasil():
        try:
            d = json.loads(arq.read_text(encoding="utf-8"))
            if d.get("versao") != 1 or not isinstance(d.get("sites"), dict) or not isinstance(d.get("itens"), list):
                raise ValueError("formato de delta desconhecido")
            if d.get("rota") != "ponte":
                raise ValueError("não é delta da coleta no Brasil")
        except Exception as e:
            recusados.append({"arquivo": arq.name, "motivo": f"{type(e).__name__}: {str(e)[:120]}"})
        else:
            aplicar(d, gravar=gravar)
            feitos.append(arq.name)
        if remover:
            arq.unlink()
    return {"aplicados": feitos, "recusados": recusados}


def _migrar_antigo(acervo: dict, hoje: date) -> None:
    """Primeira rodada: os itens do antigo motor de agregadores (CapitaAI, Farol, IDIS) entram no acervo com o mesmo
    id e a data em que foram vistos pela primeira vez — validações já registradas continuam valendo."""
    antigo = _j(FLUXO, {}) or {}
    nomes = {"capitaai": "site-capitaai", "farolcultural": "site-farol-cultural", "idis": "site-idis"}   # 02/10: motores por site
    velhos = []
    for x in antigo.get("itens") or []:
        if x.get("motor") or not x.get("id"):
            continue
        it = dict(x, motor=nomes.get(x.get("fonte")), pais=x.get("pais") or "BR", rota="nuvem",
                  perfil=X.perfil(x.get("titulo") or "")[0], areas=["cultura"] if x.get("fonte") == "farolcultural" else [])
        it["chave"] = X.chave(it)
        velhos.append(it)
    _fundir(acervo, velhos, hoje.isoformat())
    for x in velhos:
        a = acervo["itens"].get(x["id"])
        if a and x.get("primeiro_visto"):
            a["primeiro_visto"] = x["primeiro_visto"]


def _por_fonte(entrada: list[dict]) -> dict:
    out: dict = {}
    for x in entrada:
        for f in x.get("fontes") or [x.get("fonte")]:
            d = out.setdefault(f, {"lidos": 0, "com_link_oficial": 0, "com_prazo": 0})
            d["lidos"] += 1
            d["com_link_oficial"] += 1 if x.get("link_oficial") else 0
            d["com_prazo"] += 1 if x.get("prazo") else 0
    return out


# ------------------------------------------------------------------ painel
def painel(cat: dict, est: dict, acervo: dict, rotas: dict, entrada: list[dict], hoje: date) -> dict:
    no_fluxo: dict = {}
    for x in entrada:
        for f in x.get("fontes") or [x.get("fonte")]:
            no_fluxo[f] = no_fluxo.get(f, 0) + 1
    ativos: dict = {}
    for x in (acervo.get("itens") or {}).values():
        for f in x.get("fontes") or [x.get("fonte")]:
            ativos[f] = ativos.get(f, 0) + 1
    sites = []
    for s in cat.get("sites") or []:
        st = (est.get("sites") or {}).get(s["id"]) or {}
        r, motivo = rotas.get(s["id"], ("nuvem", ""))
        sites.append({"id": s["id"], "nome": s.get("nome"), "motor": s.get("motor"), "leitor": s.get("leitor"), "url": s.get("pagina") or s.get("url") or (s.get("listas") or [None])[0],
                      "rota": r, "rota_motivo": motivo, "prioridade": s.get("prioridade"), "cadencia_horas": s.get("cadencia_horas"),
                      "ultima": st.get("ultima"), "lidas_ultima": st.get("lidas_ultima"), "novos_ultima": st.get("novos_ultima"),
                      "falhas_ultima": [f"{f.get('tipo')}: {f.get('detalhe')}" for f in (st.get("falhas_ultima") or [])][:3],
                      "pendente": st.get("pendente"), "indicios_no_acervo": ativos.get(s["id"], 0), "indicios_no_fluxo": no_fluxo.get(s["id"], 0),
                      "legado": s.get("legado"), "delegado_a": s.get("delegado_a"), "diag": st.get("diag")})
    motores = []
    for mid, m in (cat.get("motores") or {}).items():
        ss = [x for x in sites if x["motor"] == mid]
        ult = max((x["ultima"] for x in ss if x.get("ultima")), default=None)
        motores.append({"id": mid, "nome": m.get("nome"), "metodo": m.get("metodo"), "horarios_brt": m.get("horarios_brt"),
                        "reune": m.get("reune"), "delega": m.get("delega"), "sites": len(ss), "ultima_leitura": ult,
                        "indicios_no_fluxo": sum(x["indicios_no_fluxo"] for x in ss),
                        "com_falha": sum(1 for x in ss if x["falhas_ultima"] and not x.get("lidas_ultima"))})
    # 02/10: um motor por site — a rota (nuvem, ponte, assistida) e as últimas leituras vêm do próprio site
    por_mid = {m["id"]: m for m in motores}
    for x in sites:
        m = por_mid.get(x["motor"])
        if m is not None:
            m.setdefault("rotas", []).append(x["rota"])
            m["leituras"] = (((est.get("sites") or {}).get(x["id"]) or {}).get("leituras") or [])[-5:]
            m["local"] = (cat.get("motores") or {}).get(x["motor"], {}).get("local")
            m["finalidade"] = (cat.get("motores") or {}).get(x["motor"], {}).get("finalidade")
    return {"em": est.get("em"), "regra": cat.get("regra"), "motores": motores, "sites": sites,
            "ponte": {"escolha": (cat.get("ponte") or {}).get("escolha"), "configurada": _ponte.configurada(),
                      "ultima_coleta_brasil": est.get("ultima_coleta_brasil"),
                      "sites_na_ponte": sorted(sid for sid, (r, _m) in rotas.items() if r == "ponte")},
            "decisoes_do_titular": cat.get("decisoes_do_titular"),
            "acervo": len(acervo.get("itens") or {}), "no_fluxo": len(entrada),
            "por_grupo": por_grupo(entrada, {s["id"]: s for s in cat.get("sites") or []}),
            "ordem_do_fluxo": list((cat.get("limites") or {}).get("ordem_do_fluxo") or ORDEM_PADRAO),
            "descartados": cat.get("descartados"), "fila_assistida": montar_fila(cat, est, rotas, hoje, acervo)["itens"]}
