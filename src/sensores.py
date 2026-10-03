"""Esquadra de sensores — um por fonte, independentes e coordenados.

Doutrina do titular: cada fonte de recurso tem seu próprio sensor, que sabe
tudo sobre ela — passado (dossiê), presente (última leitura) e futuro
(previsão). Diários oficiais, Diário da Justiça, legislativos e APIs rodam
todos os dias; sites de fonte rodam em rodízio por dia da semana; quando há
previsão de edital para a fonte no mês, o sensor passa a rodar diariamente.

Como fica leve:
  · um único arquivo de estado para toda a esquadra (`estado/esquadra.json`),
    compacto; nenhum sensor cria arquivo próprio;
  · o léxico é compilado uma vez e compartilhado; zero IA na triagem;
  · cada sensor lê no máximo 3 páginas e 60 links por página, com pausa;
  · achados entram na base JSONL deduplicados por URL canônica; o restante
    é contagem.
  · a IA (modelo mais barato) só é chamada pela busca ativa, e só quando a
    leitura determinística não acha.

Executar: `python -m src.sensores` (o coordenador decide quem sai hoje).
"""
from __future__ import annotations

import json
import os
import re
import time
import zlib
from datetime import date, timedelta
from html.parser import HTMLParser
from urllib.parse import quote, urljoin, urlsplit
from .nucleo import resolver_redirecionamento

from .destinacao import avaliar_destinacao
from .lexico import casar
from .nucleo import (ROOT, append_jsonl, canonical_url, carregar_oportunidades, load_json,
                     now_iso, sha256, validate_public_https, write_json)

CFG = ROOT / "config/sensores.json"
F260 = ROOT / "config/fontes_captacao_260.json"
INVEST = ROOT / "config/investigacao.json"
PREV = ROOT / "biblioteca_alexandria/previsoes/previsoes.json"
ESTADO = ROOT / "estado/esquadra.json"
DIARIO = ROOT / "estado/esquadra_diario.json"        # 30 dias por sensor: cor + trecho
ATIVACAO = ROOT / "estado/ativacao_fontes.json"      # fontes específicas ativas hoje (época/menção)


def cor_do_dia(r: dict) -> str:
    """cinza: não executado · vermelho: falha/inoperante · azul: funcionou sem
    oportunidade · amarelo: achou, mas faltam camadas · verde: 11 camadas."""
    if r.get("falhas") and not r.get("saude"):
        return "vermelho"
    if not r.get("achados"):
        return "azul"
    if any((a.get("confirmacao") or {}).get("nivel_confirmacao") == "completo" for a in r["achados"]):
        return "verde"
    return "amarelo"


def registrar_dia(sensor_id: str, hoje: date, r: dict) -> None:
    d = load_json(DIARIO) if DIARIO.exists() else {"sensores": {}}
    s = d["sensores"].setdefault(sensor_id, {})
    melhor = max(r.get("achados") or [], key=lambda a: a.get("forca_lexica", 0), default=None)
    s[hoje.isoformat()] = {
        "cor": cor_do_dia(r), "achados": len(r.get("achados") or []),
        "falhas": len(r.get("falhas") or []),
        "http": ((r.get("saude") or [{}])[0]).get("http"),
        "trecho": ((melhor or {}).get("titulo") or "")[:160] if melhor else None,
        "url": (melhor or {}).get("url"),
    }
    # janela móvel: só os últimos 45 dias ficam
    corte = (hoje - timedelta(days=45)).isoformat()
    for k in [k for k in s if k < corte]:
        del s[k]
    d["atualizado_em"] = now_iso()
    write_json(DIARIO, d)
DB = ROOT / "dados/oportunidades/oportunidades.jsonl"

_FIM = re.compile(r"(?:at[ée]|prazo|encerra\w*|inscri[çc][õo]es[^.]{0,30}?at[ée])\D{0,25}(\d{1,2}/\d{1,2}/20\d{2})", re.I)
_VALOR = re.compile(r"R\$\s?[\d.]{1,12},\d{2}|R\$\s?[\d.]{3,12}", re.I)
_AGREG = re.compile(r"queridodiario|pncp\.gov|compras|licitanet", re.I)


def _sites_empresas_go(limite: int = 22) -> list[str]:
    """Sites institucionais das empresas da base (maiores contribuintes do ICMS de
    GO), inferidos do e-mail corporativo do cadastro RFB; ordem = posição no ICMS."""
    import gzip
    b = ROOT / "dados/empresas/base_empresas.jsonl.gz"
    if not b.exists():
        return []
    saida, vistos = [], set()
    regs = []
    with gzip.open(b, "rt", encoding="utf-8") as gz:
        for l in gz:
            if l.strip():
                regs.append(json.loads(l))
    def pos(e):
        ps = [d.get("icms_posicao") for d in (e.get("anos") or {}).values() if d.get("icms_posicao")]
        return min(ps) if ps else 999
    for e in sorted(regs, key=pos):
        email = ((e.get("cadastro") or {}).get("email") or "").lower()
        dom = email.split("@")[-1].strip() if "@" in email else None
        if not dom or any(x in dom for x in ("gmail", "hotmail", "outlook", "yahoo", "uol.", "terra.", "bol.")) or dom in vistos:
            continue
        vistos.add(dom); saida.append(f"https://www.{dom}" if not dom.startswith("www.") else f"https://{dom}")
        if len(saida) >= limite:
            break
    return saida


# ------------------------------------------------------------------ registro
def registro() -> list[dict]:
    """Toda a esquadra: especiais + um sensor por fonte das 260 + portais."""
    cfg = load_json(CFG)
    sens = [dict(s, origem="especial") for s in cfg["sensores_especiais"]]
    # motor de destinação tributária: sites das PRÓPRIAS empresas maiores contribuintes do ICMS de GO
    for s in sens:
        if s.get("urls_dinamicas") == "base_empresas_go":
            s["urls"] = list(s.get("urls") or []) + _sites_empresas_go(limite=max(0, int(s.get("max_paginas") or 24) - len(s.get("urls") or [])))
    vistos = {u for s in sens for u in s["urls"]}
    por_url: dict[str, dict] = {}
    if F260.exists():
        for f in load_json(F260).get("fontes", []):
            if f["confianca_site"] == "pendente":
                continue
            urls = [u for u in f["sites"] if u not in vistos and not _AGREG.search(u)]
            if not urls:
                # site já coberto por outro motor: este ponto passa a ser atendido por ele
                for u in f["sites"]:
                    if u in por_url:
                        por_url[u].setdefault("fontes_260", []).append(f["id"])
                        break
                continue
            vistos.update(urls)
            tipo = {"internacional": "internacional", "privada": "privada"}.get(
                f["nivel"], "site_oficial")
            s = {"id": f"f260-{f['id']}", "nome": f["programa"], "tipo": tipo,
                 "nivel": f["nivel"], "uf": f.get("uf"), "territorio": f.get("uf") or "BR",
                 "urls": urls[:2], "busca": None, "confianca": f["confianca_site"],
                 "orgao": f.get("orgao"), "area": f.get("area"), "goias": f.get("goias"),
                 "fonte_260": f["id"], "fontes_260": [f["id"]], "origem": "fontes_260"}
            sens.append(s)
            for u in urls:
                por_url[u] = s
    if INVEST.exists():
        for p in load_json(INVEST).get("fontes", []):
            if not p.get("ativa", True):
                continue
            # AUDITORIA 20/09: uma plataforma é MOTOR REGULAR (todo dia). Antes, se a URL já
            # constava entre os 260 pontos, a plataforma era descartada e ficava "sem leitura
            # ainda" para sempre — foi o caso de Prosas, Mapa das OSC, SALIC e Secult-GO,
            # numerados no painel como motores 8, 11, 14 e 16 sem nunca ter rodado.
            vistos.add(p["url"])
            sens.append({"id": f"plat-{p['id']}", "nome": p["nome"], "tipo": "plataforma",
                         "nivel": "privada", "uf": None, "territorio": p.get("territorio", "BR"),
                         "urls": [p["url"]], "busca": None, "confianca": "confirmada",
                         "origem": "investigacao"})
    # MOTOR DE RECORRÊNCIA (20/09): revisita a página oficial de cada oportunidade validada
    rec = ROOT / "estado/rotas_recorrencia.json"
    if rec.exists():
        from datetime import date as _date
        hoje_iso = _date.today().isoformat()
        rotas = [r for r in (load_json(rec).get("rotas") or []) if (r.get("proxima_leitura") or hoje_iso) <= hoje_iso]
        if rotas:
            sens.append({"id": "recorrencia", "nome": "Motor de Recorrência — revisita as oportunidades identificadas", "tipo": "recorrencia",
                         "nivel": "misto", "uf": None, "territorio": "BR", "urls": [r["url"] for r in rotas[:40]], "busca": None,
                         "confianca": "confirmada", "origem": "finalidade_motores", "max_paginas": 40,
                         "lexico_proprio": ["retificação", "prorrogação", "errata", "resultado", "homologação", "classificados", "recurso", "suspensão", "revogação", "novo edital", "inscrições", "cronograma"],
                         "rotas_recorrencia": [{"edital_id": r["edital_id"], "url": r["url"]} for r in rotas[:40]]})
    return sens


def _previsoes_ativas(hoje: date) -> set[str]:
    """Órgãos com previsão de edital no mês corrente → sensor escala para diário."""
    if not PREV.exists():
        return set()
    mes = hoje.isoformat()[:7]
    ativos = set()
    for p in load_json(PREV).get("itens", []):
        if p["inicio"][:7] <= mes <= p["fim"][:7]:
            ativos.add(re.sub(r"\W+", " ", (p.get("orgao") or "").lower()).strip())
    return ativos


def _casa_previsao(sensor: dict, ativos: set[str]) -> bool:
    alvo = re.sub(r"\W+", " ", f'{sensor.get("orgao") or ""} {sensor["nome"]}'.lower())
    toks = [t for t in alvo.split() if len(t) > 4]
    return any(sum(1 for t in toks if t in a) >= 2 for a in ativos) if toks else False


def escala_do_dia(hoje: date | None = None) -> dict:
    """Quem sai hoje: diários/justiça/legislativo/API sempre; sites em rodízio
    por dia da semana; escalada para diário quando há previsão no mês."""
    hoje = hoje or date.today()
    cfg = load_json(CFG)
    diarios = set(cfg["cadencia"]["diaria"])
    ativos = _previsoes_ativas(hoje)
    # motores desligados pelo titular no painel (tonel azul) não saem
    ma = ROOT / "config/motores_ativos.json"
    desligados = set(load_json(ma).get("inativos", [])) if ma.exists() else set()
    dia = hoje.weekday()
    saem, ficam = [], []
    ativas = set((load_json(ATIVACAO).get("ativas") or {}).keys()) if ATIVACAO.exists() else set()
    for s in registro():
        motivo = None
        if s["id"] in desligados or desligados & set(s.get("fontes_260") or []):
            ficam.append(dict(s, desligado_pelo_titular=True)); continue
        if s["tipo"] in diarios or s["tipo"] in ("plataforma", "recorrencia"):
            motivo = "motor regular e geral — todo dia"
        elif s.get("fontes_260") and (set(s["fontes_260"]) & ativas):
            motivo = "fonte específica ATIVA: época prevista ou menção em local oficial"
        elif cfg["cadencia"].get("escalada_por_previsao") and _casa_previsao(s, ativos):
            motivo = "escalada: previsão de edital neste mês"
        elif not s.get("fontes_260") and zlib.crc32(s["id"].encode()) % 7 == dia:
            motivo = f"rodízio semanal (dia {dia})"
        (saem if motivo else ficam).append({**s, "motivo": motivo} if motivo else s)
    lim = cfg["limites"]["sensores_por_execucao"]
    # AUDITORIA 20/09: os motores REGULARES (diários, plataformas, API, legislativo, justiça,
    # empresas) nunca podem ser cortados pelo limite — antes a ordenação "Goiás primeiro"
    # empurrava as plataformas nacionais para o fim e o corte de 40 as deixou 14 dias sem
    # rodar (ABCR, GIFE, Observatório, Prosas). O limite vale só para os 260 pontos.
    regulares = [s for s in saem if not s.get("fontes_260")]
    pontos = [s for s in saem if s.get("fontes_260")]
    pontos.sort(key=lambda s: (not s.get("goias"), s["id"]))            # entre os pontos, Goiás primeiro
    sobra = max(0, lim - len(regulares))
    saem = regulares + pontos[:sobra]
    saem.sort(key=lambda s: (s["tipo"] not in diarios, s.get("fontes_260") is not None, not s.get("goias"), s["id"]))
    cortados = max(0, len(pontos) - sobra)
    return {"data": hoje.isoformat(), "saem": saem, "ficam": len(ficam) + cortados,
            "total": len(saem) + len(ficam) + cortados, "previsoes_ativas": len(ativos),
            "regulares_garantidos": len(regulares), "pontos_cortados_pelo_limite": cortados}


# ------------------------------------------------------------------- leitura
class _Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []; self.texto = []; self._h = None; self._t = []
    def handle_starttag(self, tag, attrs):
        if tag == "a": self._h = dict(attrs).get("href"); self._t = []
    def handle_data(self, data):
        self.texto.append(data)
        if self._h is not None: self._t.append(data)
    def handle_endtag(self, tag):
        if tag == "a" and self._h is not None:
            self.links.append((self._h, " ".join(self._t).strip())); self._h = None


def _abrir(url: str, timeout: int = 12, max_bytes: int = 2_500_000) -> tuple[str, str, int]:
    from urllib.request import Request, urlopen
    if not url.startswith("file://"):
        validate_public_https(url, urlsplit(url).hostname)
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 Eldorado-OSC/1.0", "From": "contato-via-repositorio", "Accept-Language": "pt-BR,pt;q=0.9",
                                "Accept": "text/html,application/rss+xml,application/json;q=0.9,*/*;q=0.5"})
    with urlopen(req, timeout=timeout) as r:
        return r.read(max_bytes).decode("utf-8", "replace"), r.geturl(), getattr(r, "status", 200) or 200


def _local_conhecido(sensor: dict) -> list[str]:
    """Fonte das 260 com parametrização: lê primeiro a página onde o último edital
    saiu de fato (nunca o vetor)."""
    sid = sensor.get("id") or ""
    fid = sensor.get("fonte_id") or (sid[5:] if sid.startswith("f260-") else None)
    if not fid:
        return []
    arq = ROOT / "biblioteca_alexandria/fontes" / fid / "parametros.json"
    if not arq.exists():
        return []
    lp = (load_json(arq).get("local_publicacao") or {})
    return [u for u in (lp.get("pagina_de_publicacao"), lp.get("url_ultimo_edital")) if u]


def _paginas(sensor: dict, hoje: date | None = None) -> list[str]:
    """URLs a ler: fixas; por termo quando o portal tem busca; por DATA do dia
    quando o diário publica por edição (DOU: leiturajornal?data=DD-MM-AAAA)."""
    hoje = hoje or sensor.get("_data") or date.today()      # retroativo: a edição de outro dia
    saida = list(_local_conhecido(sensor))
    for u in sensor["urls"]:
        if "{data8}" in u or "{data8-3}" in u:
            from datetime import timedelta as _td
            saida.append(u.replace("{data8-3}", (hoje - _td(days=3)).strftime("%Y%m%d")).replace("{data8}", hoje.strftime("%Y%m%d")))
        elif "{dataiso}" in u:
            saida.append(u.replace("{dataiso}", hoje.isoformat()))
        elif "{data}" in u:
            saida.append(u.replace("{data}", hoje.strftime("%d-%m-%Y")))
        elif "{termo}" in u:
            saida += [u.replace("{termo}", quote(t)) for t in sensor.get("termos_busca", [])[:4]]
        else:
            saida.append(u)
    # 20/09: o motor de editais de EMPRESAS lê os sites/páginas de RSE das empresas mapeadas pelos motores 27/28
    if sensor.get("id") == "plat-empresas-editais-incentivados":
        try:
            from .empresas_rotas import rotas_para_sensor
            for u in rotas_para_sensor(40):
                if u not in saida:
                    saida.append(u)
        except Exception:
            pass
    # 20/09: as ROTAS ALTERNATIVAS declaradas (diário + secretaria + conselho…) entram DEPOIS das
    # páginas próprias do motor, para nunca deslocá-las do limite de leitura
    for r in rotas_alternativas(sensor):
        if r.get("exige_brasil") and os.environ.get("GITHUB_ACTIONS") and not os.environ.get("ELDORADO_LOCAL_BR"):
            continue
        if r["url"] not in saida:
            saida.append(r["url"])
    return saida


_LEX_ESP: dict = {}
ROTAS_MOTORES = ROOT / "config/rotas_motores.json"
_ROTAS: dict = {}


def _rotas_cfg() -> dict:
    global _ROTAS
    if not _ROTAS and ROTAS_MOTORES.exists():
        _ROTAS = load_json(ROTAS_MOTORES)
    return _ROTAS


def lexico_camada1(sensor: dict) -> tuple[list[str], list[str]]:
    """CAMADA 1 — direcionamento (20/09): corre nos rótulos dos links e decide QUAIS páginas
    abrir. Termos do perfil do motor + termos gerais; vetos do motor + vetos gerais.
    Aplicada ANTES do léxico de contexto, para gastar leitura só no que tem cara de edital."""
    cfg = _rotas_cfg(); m = (cfg.get("motores") or {}).get(sensor.get("id")) or {}
    termos = [x.lower() for x in (m.get("lexico_camada1") or [])] + [x.lower() for x in (cfg.get("camada_1_geral") or [])]
    vetos = [x.lower() for x in (m.get("veto_camada1") or [])] + [x.lower() for x in (cfg.get("camada_1_veto") or [])]
    # 20/09: o LÉXICO APRENDIDO (config/lexico_aprendido.json) soma-se à camada 1 de todo motor de descoberta
    try:
        from .aprendizado_lexico import termos_aprendidos
        ap_pos, ap_veto = termos_aprendidos()
        termos += [x for x in ap_pos if x not in termos]
        vetos += [x for x in ap_veto if x not in vetos]
    except Exception:
        pass
    # 02/10 (titular): LÉXICO TEMPORÁRIO DOS LIVROS — na janela de ativação (30 dias antes da abertura prevista até o
    # encerramento), a chave de acionamento do livro compõe o léxico da camada 1 dos motores do seu índice
    try:
        from .chaves_livros import termos_temporarios
        termos += [x for x in termos_temporarios(sensor.get("id")) if x not in termos]
    except Exception:
        pass
    return termos, vetos


def lexico_camada2(sensor: dict) -> list[str]:
    """CAMADA 2 — contexto: corre no TEXTO do documento e confirma se é oportunidade."""
    m = ((_rotas_cfg().get("motores") or {}).get(sensor.get("id")) or {})
    return [x.lower() for x in (m.get("lexico_camada2") or [])]


def rotas_alternativas(sensor: dict) -> list[dict]:
    """Rotas onde o mesmo recurso divulga (≥2 por motor). O sensor lê TODAS as que não exigem
    Brasil quando roda no GitHub; as que exigem ficam para a coleta local."""
    m = ((_rotas_cfg().get("motores") or {}).get(sensor.get("id")) or {})
    return [r for r in (m.get("rotas") or []) if r.get("url") and str(r["url"]).startswith("http")]


def casa_camada1(rotulo: str, termos: list[str], vetos: list[str]) -> dict:
    r = (rotulo or "").lower()
    veto = [v for v in vetos if v in r]
    if veto:
        return {"passa": False, "veto": veto[:3], "termos": []}
    hit = [x for x in termos if x in r]
    return {"passa": bool(hit), "veto": [], "termos": hit[:5]}


def lexico_especifico(sensor: dict) -> list[str]:
    """2ª etapa (livros de oportunidades da Biblioteca): termos ESPECÍFICOS do recurso — o léxico
    próprio do regramento quando existe, senão os termos distintivos do
    programa. Casam de forma cirúrgica, onde o léxico geral seria vago."""
    if sensor.get("lexico_proprio"):                 # sensores especiais com léxico próprio (ex.: editais incentivados)
        return list(sensor["lexico_proprio"])[:30]
    lx = (sensor.get("busca") or {}).get("lexico") or {}
    if lx.get("termos") or lx.get("proprio"):        # 02/10: o livro carrega o léxico que busca a sua oportunidade
        return list(dict.fromkeys(list(lx.get("proprio") or []) + list(lx.get("termos") or [])))[:30]
    if not sensor.get("fontes_260"):
        return []
    genericos = {"edital", "editais", "projeto", "projetos", "apoio", "cultura", "cultural", "esporte", "fomento",
                 "programa", "municipal", "estadual", "federal", "goiás", "goiania", "goiânia", "secretaria",
                 "destinação", "destinacao", "doação", "doacao", "incentivo", "fiscal", "nacional", "estado",
                 "recursos", "captação", "entidades", "social", "sociais", "pessoa", "física", "fisica", "jurídica"}
    if not _LEX_ESP:
        rg = ROOT / "config/regramentos.json"
        if rg.exists():
            for r in load_json(rg).get("regramentos", []):
                toks = {t for t in re.findall(r"[a-zà-ú]{5,}", r["fonte"].lower()) if t not in genericos}
                _LEX_ESP[r["id"]] = {"toks": toks, "lex": r.get("lexico_proprio", [])}
    nome = (sensor.get("nome") or "").lower()
    ntoks = {t for t in re.findall(r"[a-zà-ú]{5,}", nome) if t not in genericos}
    # UM regramento só: o de maior sobreposição de termos distintivos (mín. 1 termo forte)
    melhor, nota = None, 0
    for rid, r in _LEX_ESP.items():
        n = len(ntoks & r["toks"])
        if n > nota:
            melhor, nota = r, n
    termos = list(melhor["lex"]) if melhor else []
    termos += sorted(ntoks)
    return sorted(set(termos))[:24]


def casa_especifico(texto: str, termos: list[str]) -> list[str]:
    import unicodedata as _u
    sa = lambda t: "".join(c for c in _u.normalize("NFKD", str(t or "").lower()) if not _u.combining(c))
    tl = sa(texto)                                    # 02/10: o léxico do livro vem sem acento — compara os dois sem acento
    return [t for t in termos if sa(t) in tl]


def reprogramar_recorrencia(sensor: dict, resultado: dict) -> None:
    """Após a leitura do motor de recorrência, cada rota lida ganha a próxima data pela sua cadência."""
    if sensor.get("id") != "recorrencia":
        return
    arq = ROOT / "estado/rotas_recorrencia.json"
    if not arq.exists():
        return
    d = load_json(arq); lidas = {r["url"] for r in (sensor.get("rotas_recorrencia") or [])}
    hoje = date.today()
    for r in d.get("rotas", []):
        if r["url"] in lidas:
            r["ultima_leitura"] = hoje.isoformat()
            r["proxima_leitura"] = (hoje + timedelta(days=int(r.get("cadencia_dias") or 7))).isoformat()
    write_json(arq, d)


def ler(sensor: dict, limites: dict | None = None, pausa: float | None = None, data: date | None = None) -> dict:
    """Uma leitura do sensor: páginas → links → léxico → destinação → achados.
    livros de oportunidades da Biblioteca (fontes_260) também casam pelo léxico ESPECÍFICO."""
    if data:
        sensor = dict(sensor, _data=data)
    # MOTOR 01 (parecer de 01/10/2026): o Diário de Goiânia é lido pelo TEXTO das edições
    # (Querido Diário na nuvem + PDF oficial na coleta local), recortado em atos — não pelo rótulo dos links
    if sensor.get("id") == "do-goiania":
        from .diario_goiania import ler_motor
        return ler_motor(sensor, data, limites)
    # MOTOR 02 (parecer de 01/10/2026): o Diário do Estado é lido pela estrutura aberta do portal
    # (busca, sumário por órgão, texto de cada matéria) + API dos sites das secretarias
    if sensor.get("id") == "do-goias":
        from .diario_goias import ler_motor as ler_motor_go
        return ler_motor_go(sensor, data, limites)
    # MOTOR 03 (parecer de 01/10/2026): o DOU é lido pela Leitura do Jornal INTEIRA (DO1 + DO3 + extras, sem o corte
    # de 2,5 MB que zerava a Seção 3) e pela íntegra das matérias de interesse, com o classificador comum
    # MOTOR — OPORTUNIDADES ESTADUAIS GOVERNAMENTAIS (titular, 02/10/2026): todos os órgãos do Executivo de Goiás, um por
    # vez, em camadas (onde publicam · histórico de 5 anos · oportunidades · monitoramento) — agrega os motores 09, 14-17
    if sensor.get("id") == "plat-estaduais-go-gov":
        from .estaduais_go import ler_motor as ler_motor_est
        return ler_motor_est(sensor, data, limites)
    # MOTOR 08 v2 (parecer complementar de 02/10/2026): as 25 maiores prefeituras de Goiás lidas onde publicam — diário
    # AGM, API do WordPress, Querido Diário (domínio novo) e portais próprios —, com status honesto por cidade e por rota
    if sensor.get("id") == "plat-prefeituras-50-go":
        from .prefeituras_25_go import ler_motor as ler_motor_pref
        return ler_motor_pref(sensor, data, limites)
    if sensor.get("id") == "dou":
        from .diario_uniao import ler_motor as ler_motor_br
        return ler_motor_br(sensor, data, limites)
    # MOTOR 04 (parecer de 01/10/2026): o PNCP é lido pelas propostas ABERTAS (data oficial de encerramento) e pela
    # busca do portal, com o classificador de finalidade e os vetos federais — não pelo rótulo dos itens
    if sensor.get("id") == "pncp-api":
        from .pncp_osc import ler_motor as ler_motor_pncp
        return ler_motor_pncp(sensor, data, limites)
    # MOTOR 05 (parecer de 01/10/2026): a Câmara de Goiânia é lida pelo SUAP (processos legislativos, com autor, setor e
    # documentos), pela tramitação dos processos da própria associação e pelas notícias do portal — não pela home
    if sensor.get("id") == "camara-goiania-pl":
        from .camara_goiania import ler_motor as ler_motor_cmg
        return ler_motor_cmg(sensor, data, limites)
    # MOTOR DO CONGRESSO (parecer de 02/10/2026): CMO (prazo oficial das emendas ao PLOA), APIs da Câmara e do Senado
    # (regras e recursos para entidades), notícias e convocações das Casas — o par federal dos motores 05 e 06
    if sensor.get("id") == "congresso-nacional":
        from .congresso_nacional import ler_motor as ler_motor_cn
        return ler_motor_cn(sensor, data, limites)
    # MOTOR DO JUDICIÁRIO — CNJ e TJGO (parecer de 02/10/2026): reúne dje-tjgo e cnj-destinacoes. RSS da Agência de Notícias do
    # TJGO + notícia + PDF do edital da comarca (no computador do titular), busca do CNJ (nuvem), PNCP cruzado e Banco de Projetos
    if sensor.get("id") in ("mpgo-destinacao", "mptgo-destinacao", "mpu-destinacao"):   # 02/10: MP separado em três
        from .ministerios_publicos import ler_parte as ler_parte_mp
        return ler_parte_mp(sensor["id"], sensor, data, limites)
    if sensor.get("id") == "plat-mp-destinacoes-reparacao":     # 02/10: motor 12 — lê pela estrutura de cada fonte (estudo ao vivo)
        from .ministerios_publicos import ler_motor as ler_motor_mp
        return ler_motor_mp(sensor, data, limites)
    if sensor.get("id") in ("judiciario-tjgo", "judiciario-cnj"):     # 02/10: o Judiciário separado em TJ-GO e CNJ
        from .judiciario_go import ler_parte as ler_parte_jud
        return ler_parte_jud(sensor["id"], sensor, data, limites)
    if sensor.get("id") == "judiciario-cnj-tjgo":
        from .judiciario_go import ler_motor as ler_motor_jud
        return ler_motor_jud(sensor, data, limites)
    # MOTOR 22 (parecer de 01/10/2026): o GIFE é lido pela API da seleção de editais (um item por bloco "título +
    # prazo + Inscreva-se") e pela Capta, para onde a seleção aponta — não pela home institucional nem pelos associados
    # MOTOR 16 (03/10/2026): Lei Rouanet pela regra da janela (IN MinC 29/2026, art. 5º) e pela API do SALIC — não pelas
    # páginas institucionais do Ministério
    if sensor.get("id") == "plat-salic":
        from .rouanet_salic import ler_motor as ler_motor_salic
        return ler_motor_salic(sensor, data, limites)
    if sensor.get("id") == "plat-gife":
        from .gife_editais import ler_motor as ler_motor_gife
        return ler_motor_gife(sensor, data, limites)
    lim = limites or load_json(CFG)["limites"]
    pausa = lim["pausa_segundos"] if pausa is None else pausa
    achados, falhas, saude = [], [], []
    # portais que exigem IP do Brasil: no GitHub não se tenta; na coleta local (ELDORADO_LOCAL_BR=1) lê-se normalmente
    exige = set((load_json(CFG).get("exige_brasil") or {}).get("dominios") or [])
    if os.environ.get("GITHUB_ACTIONS") and not os.environ.get("ELDORADO_LOCAL_BR"):
        todas = _paginas(sensor)
        hosts = {urlsplit(u).hostname for u in todas}
        # 20/09: se há rotas alternativas fora do Brasil-only, lê ESSAS e deixa as outras para a coleta local
        alternativas = [u for u in todas if urlsplit(u).hostname not in exige]
        if alternativas and hosts & exige:
            sensor = dict(sensor, urls=alternativas, _rotas_pendentes_local=[u for u in todas if urlsplit(u).hostname in exige])
            hosts = {urlsplit(u).hostname for u in alternativas}
        if hosts and hosts <= exige:
            return {"sensor": sensor["id"], "achados": [], "falhas": [], "saude": [], "lido_em": now_iso(),
                    "pulado_exige_brasil": True,
                    "diagnostico": {"paginas_lidas": 0, "links_total": 0, "links_candidatos": 0, "descobertas": [], "pdf_links": 0,
                                    "motivo_zero": "aguardando coleta local (Brasil): este portal recusa IP estrangeiro; é lido quando o titular roda scripts/coleta_brasil.py na sua máquina", "exige_brasil": True}}
    especifico = lexico_especifico(sensor)
    c1_termos, c1_vetos = lexico_camada1(sensor)
    diag = {"paginas_lidas": 0, "links_total": 0, "links_candidatos": 0, "descobertas": [], "pdf_links": 0, "motivo_zero": None,
            "camada1_vetados": 0, "camada1_direcionados": 0}
    if sensor.get("_rotas_pendentes_local"):        # 03/10: a parte Brasil-only da fonte ficou para a coleta local — não é leitura completa
        diag["rotas_pendentes_local"] = list(sensor["_rotas_pendentes_local"])
    n_pag = int(sensor.get("max_paginas") or lim["paginas_por_sensor"])
    fila = list(_paginas(sensor)[:n_pag])
    lidas: set = set()
    while fila and diag["paginas_lidas"] < n_pag + 4:
        url = fila.pop(0)
        if url in lidas:
            continue
        lidas.add(url)
        try:
            tmo = lim.get("timeout_segundos", 12) if sensor.get("tipo") != "api" else max(30, lim.get("timeout_segundos", 12))
            html, final, status = _abrir(url, timeout=tmo, max_bytes=lim["bytes_por_pagina"])
            saude.append({"url": url, "http": status, "bytes": len(html)}); diag["paginas_lidas"] += 1
        except Exception as exc:
            code = getattr(exc, "code", None); hdrs = getattr(exc, "headers", None)
            servidor = (hdrs.get("Server") or hdrs.get("server") or "") if hdrs else ""
            waf = "Cloudflare" if (hdrs and (hdrs.get("cf-ray") or "cloudflare" in servidor.lower())) else "Akamai" if (hdrs and (hdrs.get("x-akamai-request-id") or "akamai" in servidor.lower())) else \
                  "Imperva/Incapsula" if (hdrs and hdrs.get("x-iinfo")) else "BIG-IP/F5" if "big-ip" in servidor.lower() else None
            causa = ("bloqueio de robô pelo WAF " + waf) if waf and code in (403, 429, 503) else \
                    ("acesso negado (403) sem WAF identificado — padrão de bloqueio geográfico/IP de datacenter" if code == 403 else
                     "endereço não resolve (DNS) — URL errada ou domínio desativado" if type(exc).__name__ == "gaierror" else
                     "conexão recusada/derrubada — filtro de rede ou IP estrangeiro" if type(exc).__name__ in ("URLError", "RemoteDisconnected", "ConnectionResetError") else
                     "tempo esgotado — servidor lento ou filtrando o IP" if "Timeout" in type(exc).__name__ else
                     f"HTTP {code}" if code else type(exc).__name__)
            falhas.append({"url": url, "erro": type(exc).__name__, "code": code, "waf": waf, "causa": causa})
            try:
                from .alternativas import registrar_bloqueio
                registrar_bloqueio(url, type(exc).__name__, sensor.get("nome", ""))
            except Exception:
                pass
            continue
        p = _Links()
        # API JSON (PNCP): itens viram links para a página pública do edital
        if html.lstrip().startswith(("{", "[")) and "comunicaapi.pje.jus.br" in url:
            # DJEN (CNJ): comunicações do TJGO do dia — texto vira rótulo; link para a comunicação
            try:
                js = json.loads(html); itens = js.get("items") or js.get("content") or []
                for it in itens[:300]:
                    txt = re.sub(r"<[^>]+>", " ", str(it.get("texto") or "")); txt = re.sub(r"\s+", " ", txt).strip()
                    if len(txt) < 20: continue
                    rot = (it.get("tipoComunicacao") or "Comunicação") + " — " + (it.get("nomeOrgao") or "") + " — " + txt[:240]
                    p.links.append((it.get("link") or f"https://comunica.pje.jus.br/consulta?siglaTribunal=TJGO", rot)); p.texto.append(" " + txt[:400] + " ")
                diag["djen_itens"] = len(itens)
            except Exception:
                pass
        elif html.lstrip().startswith(("{", "[")) and "pncp" in url:
            try:
                js = json.loads(html); itens = js.get("data") if isinstance(js, dict) else js
                for it in (itens or [])[:200]:
                    org = (it.get("orgaoEntidade") or {}); cnpj = re.sub(r"\D", "", str(org.get("cnpj") or ""))
                    ano = it.get("anoCompra"); seq = it.get("sequencialCompra")
                    rot = f"{it.get('modalidadeNome') or 'Chamamento'} — {org.get('razaoSocial') or ''} — {(it.get('objetoCompra') or '')[:220]}"
                    link = f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{seq}" if cnpj and ano and seq else it.get("linkSistemaOrigem") or url
                    p.links.append((link, rot)); p.texto.append(" " + rot + f" · encerramento {it.get('dataEncerramentoProposta') or ''} · UF {((it.get('unidadeOrgao') or {}).get('ufSigla') or '')} ")
            except Exception:
                pass
        else:
            p.feed(html)
        # DOU (leiturajornal): as matérias do dia vêm num JSON embutido, não em <a>;
        # cada matéria vira um link para a íntegra em /web/dou/-/<urlTitle>
        mj = (re.search(r'<script[^>]*id="params"[^>]*>(.*?)</script>', html, re.S)
              or re.search(r'<script[^>]*id="_pesquisa_params"[^>]*>(.*?)</script>', html, re.S)
              or re.search(r'var\s+params\s*=\s*(\{.*?\});', html, re.S)
              or re.search(r'"jsonArray"\s*:\s*(\[.*?\])\s*[,}]', html, re.S))
        if "in.gov.br" in url:
            diag["dou_json_encontrado"] = bool(mj)
        if mj and "in.gov.br" in url:
            try:
                bruto = json.loads(mj.group(1))
                dados_dou = {"jsonArray": bruto} if isinstance(bruto, list) else bruto
                diag["dou_json_materias"] = len(dados_dou.get("jsonArray") or [])
                diag["dou_json_encontrado"] = True
                for mat in (dados_dou.get("jsonArray") or [])[:600]:
                    tit = (mat.get("title") or "").strip(); slug_ = mat.get("urlTitle")
                    if tit and slug_:
                        p.links.append((f"https://www.in.gov.br/web/dou/-/{slug_}", tit))
                        p.texto.append(" " + tit + " " + (mat.get("content") or "")[:300] + " ")
            except Exception:
                pass
        corpo = re.sub(r"\s+", " ", " ".join(p.texto))
        diag["links_total"] += len(p.links)
        diag["pdf_links"] += sum(1 for h, _ in p.links if h and h.lower().endswith(".pdf"))
        # DESCOBERTA DA LISTAGEM: se a página não traz editais mas aponta para
        # 'editais / licitações / chamamentos / edições / diário / publicações',
        # segue esses links (até 4) — a home costuma ser só institucional
        if url in _paginas(sensor)[:n_pag] and len(diag["descobertas"]) < (8 if n_pag > 6 else 4):
            for h, r in p.links:
                rl = (r or "").lower(); hl = (h or "").lower()
                if h and re.search(r"edita|licita|chamament|credenciament|edi[çc][õo]es|di[áa]rio|publica[çc][õo]es|transpar[êe]ncia|jornal|ver todas|mais not", rl + " " + hl) \
                        and not re.search(r"\.(jpg|png|css|js)$|mailto:|javascript:|#$", hl):
                    u2 = canonical_url(resolver_redirecionamento(urljoin(final, h)))   # destino real, não o embrulho do buscador
                    if urlsplit(u2).scheme in ("https", "file") and u2 not in lidas and u2 not in fila and len(diag["descobertas"]) < 4:
                        fila.append(u2); diag["descobertas"].append({"de": url, "para": u2, "rotulo": (r or "")[:60]})
        for href, rot in p.links[:lim["links_por_pagina"] * 3]:
            if not rot or len(rot) < 10:
                continue
            diag["links_candidatos"] += 1
            # CAMADA 1 (direcionamento): veto elimina; acerto direciona. Só depois o léxico geral.
            c1 = casa_camada1(rot, c1_termos, c1_vetos) if c1_termos else {"passa": None, "veto": [], "termos": []}
            if c1["veto"]:
                diag["camada1_vetados"] += 1
                continue
            lx = casar(rot)
            esp = casa_especifico(rot, especifico) if especifico else []
            if c1["passa"]:
                diag["camada1_direcionados"] += 1
                lx["candidato"] = True
            if not lx["candidato"] and not esp:
                continue
            lx["termos"]["especificos"] = esp
            u = canonical_url(resolver_redirecionamento(urljoin(final, href)))   # destino real, não o embrulho do buscador
            if urlsplit(u).scheme not in ("https", "file"):
                continue
            # contexto: o rótulo e o que vem DEPOIS dele, até o próximo item —
            # olhar para trás fazia um item herdar prazo/valor do vizinho
            i = corpo.find(rot[:40])
            ctx = corpo[i: i + 320] if i >= 0 else rot
            prox = ctx.find(" ", len(rot) + 1)
            nxt = re.search(r"(?:Resolu[çc][ãa]o|Edital|Projeto de Lei|Preg[ãa]o|Aviso|Portaria)\s+(?:n[ºo]|d[ao])",
                            ctx[len(rot):])
            if nxt:
                ctx = ctx[: len(rot) + nxt.start()]
            dest = avaliar_destinacao({"titulo": rot, "evidencia": ctx, "fonte_id": sensor["id"]})
            if not dest["elegivel"]:
                continue
            from .pertinencia import pertinente as _pert
            if not _pert({"titulo": rot, "evidencia": ctx})["ok"]:
                continue
            fim = _FIM.search(ctx); val = _VALOR.search(ctx)
            achados.append({
                "id": sha256(("sens|" + u).encode())[:20], "status": "capturada",
                "titulo": rot[:300], "url": u, "fonte_id": sensor["id"],
                "fonte_nome": sensor["nome"], "territorio": sensor.get("territorio") or "BR",
                "uf": sensor.get("uf"), "nivel": sensor.get("nivel"),
                "tipo_fonte": f"sensor_{sensor['tipo']}", "confianca": "primaria"
                if sensor["tipo"] in ("diario_oficial", "api", "site_oficial") else "secundaria",
                "coletado_em": now_iso(), "prazo_texto": fim.group(1) if fim else None,
                "valor_texto": val.group(0) if val else None,
                "evidencia": ctx[:500], "hash_evidencia": sha256(ctx.encode()),
                "lexico": lx["termos"], "forca_lexica": lx["forca"],
                "destinacao": dest, "sensor": sensor["id"],
            })
            if len(achados) >= lim["links_por_pagina"]:
                break
        if pausa: time.sleep(pausa)
    unicos = {a["id"]: a for a in achados}
    # DIAGNÓSTICO INDIVIDUAL — por que este motor rendeu (ou não)
    if not unicos:
        if saude and not falhas:
            if diag["links_total"] == 0 and diag["pdf_links"] == 0:
                diag["motivo_zero"] = "página respondeu mas não tem links (conteúdo carregado por script ou vazio) — precisa de API/RSS ou leitura do HTML renderizado"
            elif diag["pdf_links"] and diag["links_candidatos"] < 5:
                diag["motivo_zero"] = "os editais estão dentro de PDFs (edições inteiras) — a leitura do rótulo não alcança; entra a extração de edição"
            elif diag["descobertas"]:
                diag["motivo_zero"] = f"página institucional; seguiu {len(diag['descobertas'])} listagem(ns) e nenhum rótulo casou com o léxico do terceiro setor hoje"
            else:
                diag["motivo_zero"] = "página respondeu com links, mas nenhum rótulo casou com o léxico do terceiro setor hoje — pode não haver edital publicado"
        elif falhas and not saude:
            erros = {f["erro"] for f in falhas}
            diag["motivo_zero"] = ("endereço não resolve (DNS) — URL errada" if "gaierror" in erros else
                                   "o portal recusa acesso automatizado (HTTP 403/404) — escada de alternativas" if "HTTPError" in erros else
                                   "tempo esgotado / conexão recusada" if erros & {"timeout", "URLError", "TimeoutError"} else f"falha: {', '.join(sorted(erros))}")
        elif falhas and saude:
            diag["motivo_zero"] = "parte das páginas respondeu e parte falhou; nenhum edital reconhecido nas que responderam"
    return {"sensor": sensor["id"], "achados": list(unicos.values()),
            "falhas": falhas, "saude": saude, "diagnostico": diag, "lido_em": now_iso()}


# --------------------------------------------------------------- coordenador
def run(hoje: date | None = None, limite: int | None = None, pausa: float | None = None) -> dict:
    # 03/10 (teste do motor 09): o dia é o de Brasília — em UTC, a passagem das 23h41 de 02/10 virava "03/10 lido" no calendário
    hoje = hoje or __import__("datetime").datetime.now(__import__("datetime").timezone(timedelta(hours=-3))).date()
    escala = escala_do_dia(hoje)
    # ATIVAÇÃO MANUAL: o titular seleciona pontos no painel e o workflow recebe
    # os ids em MOTORES_FONTES — só esses motores saem, fora da escala
    import os
    pedidos = {x.strip() for x in os.environ.get("MOTORES_FONTES", "").split(",") if x.strip()}
    # BLOCO DA HORA (config/horarios.json): 00h diários · 01h justiça/legislativo ·
    # 02h plataformas/API · 04h livros de oportunidades da Biblioteca ativos. Fora do bloco, o motor
    # espera a sua hora — nada de sobrecarga.
    bloco = os.environ.get("MOTORES_BLOCO", "completo")
    hz = ROOT / "config/horarios.json"
    tipos_bloco = None
    if bloco == "regulares":
        escala["saem"] = [s for s in escala["saem"] if not s.get("fontes_260")] + \
            [{**s, "motivo": "bloco regulares: teste de todos os motores"} for s in registro()
             if not s.get("fontes_260") and s["id"] not in {x["id"] for x in escala["saem"]}]
        escala["bloco"] = bloco
    elif bloco not in ("completo", "manual") and hz.exists():
        for b in load_json(hz).get("blocos", []):
            if b["bloco"] == bloco:
                tipos_bloco = set(b["tipos"])
        if tipos_bloco is not None:
            escala["saem"] = [s for s in escala["saem"] if s["tipo"] in tipos_bloco]
            escala["bloco"] = bloco
    if pedidos:
        todos = registro()
        saem = [dict(s, motivo="ativação manual pelo titular") for s in todos
                if s["id"] in pedidos or pedidos & set(s.get("fontes_260") or [])]
        # 03/10: na ORDEM do pedido (o fluxo 22 manda os motores numerados do painel primeiro)
        _ordem = [x.strip() for x in os.environ.get("MOTORES_FONTES", "").split(",") if x.strip()]
        saem.sort(key=lambda s: _ordem.index(s["id"]) if s["id"] in _ordem else len(_ordem))
        escala = {"data": hoje.isoformat(), "saem": saem, "ficam": len(todos) - len(saem),
                  "total": len(todos), "previsoes_ativas": escala["previsoes_ativas"],
                  "manual": sorted(pedidos)}
    est = load_json(ESTADO) if ESTADO.exists() else {"sensores": {}}
    sens = est["sensores"]
    existentes = carregar_oportunidades()
    novos = total_ach = 0
    por_tipo: dict[str, dict] = {}
    # 02/10: PARADA GRACIOSA e REGISTRO A CADA MOTOR. O passo do fluxo tem limite de tempo; quando estourava, o processo
    # era morto antes de gravar a esquadra (gravada só no fim) e as leituras do registro se perdiam — de 03h01 a 14h de
    # 02/10 nenhuma varredura manual ficou registrada. Agora: não se começa um motor que não cabe no tempo restante
    # (estimativa = duração da leitura anterior dele); o adiado volta pelo maestro; a esquadra é gravada após cada motor.
    import time as _t
    _ini = _t.monotonic(); _prazo = float(os.environ.get("SENSORES_PRAZO_S", "1380"))
    try:
        from .descartes import restricoes as _restricoes
        _RESTR = _restricoes()
    except Exception:  # noqa: BLE001
        _RESTR = {"itens": []}
    executados, adiados = 0, []
    for s in escala["saem"][: (limite or len(escala["saem"]))]:
        _est = float((sens.get(s["id"]) or {}).get("duracao_s") or 60)
        if executados and _t.monotonic() - _ini + _est > _prazo:
            adiados.append(s["id"])
            continue
        _t0 = _t.monotonic()
        r = ler(s, pausa=pausa)
        # 03/10 (teste dos motores 01–21): um leitor que devolve resultado sem 'lido_em' derrubava o passo inteiro
        # (KeyError às 19:10 de 02/10) e nenhuma leitura seguinte era registrada. Agora o resultado é completado.
        r = r if isinstance(r, dict) else {}
        r.setdefault("sensor", s["id"]); r.setdefault("achados", []); r.setdefault("falhas", []); r.setdefault("saude", [])
        if not r.get("lido_em"):
            r["lido_em"] = now_iso()
        executados += 1
        reg = sens.setdefault(s["id"], {"nome": s["nome"], "tipo": s["tipo"], "leituras": 0,
                                        "achados_total": 0, "vazias_seguidas": 0})
        reg["duracao_s"] = round(_t.monotonic() - _t0)
        reg.update({"ultima": r["lido_em"], "motivo": s.get("motivo") or f"bloco {escala.get('bloco') or 'manual'}",
                    "leituras": reg["leituras"] + 1,
                    "achados_ultima": len(r["achados"]),
                    "achados_total": reg["achados_total"] + len(r["achados"]),
                    "falhas_ultima": len(r["falhas"]),
                    "saude": (r["saude"] or r["falhas"])[:2],
                    "vazias_seguidas": 0 if r["achados"] else reg["vazias_seguidas"] + 1})
        # três leituras vazias com página respondendo = URL provavelmente é home, não listagem
        reg["alerta"] = ("trocar URL: 3 leituras sem achados com página respondendo"
                         if reg["vazias_seguidas"] >= 3 and r["saude"] and not r["falhas"] else None)
        registrar_dia(s["id"], hoje, r)
        est["sensores"].setdefault(s["id"], {})["diagnostico"] = r.get("diagnostico")
        for a in r["achados"]:
            total_ach += 1
            try:                                         # 02/10: restrição aprendida com um descarte — é ruído
                from .descartes import e_ruido
                if e_ruido(a, s["id"], _RESTR):
                    reg["ruido_filtrado"] = int(reg.get("ruido_filtrado") or 0) + 1
                    continue
            except Exception:  # noqa: BLE001
                pass
            if a["id"] not in existentes:
                try:                                     # 02/10: data original da publicação + data da consulta
                    from .integridade import completar_datas
                    completar_datas(a)
                except Exception:  # noqa: BLE001
                    pass
                append_jsonl(DB, a); existentes[a["id"]] = a; novos += 1
        t = por_tipo.setdefault(s["tipo"], {"sensores": 0, "achados": 0, "falhas": 0})
        t["sensores"] += 1; t["achados"] += len(r["achados"]); t["falhas"] += len(r["falhas"])
        write_json(ESTADO, est)                                  # registro gravado a cada motor (sobrevive ao limite de tempo)
        print(f"  {s['id']}: {len(r['achados'])} achado(s), {len(r['falhas'])} falha(s), {reg['duracao_s']} s", flush=True)
    est["ultima_execucao"] = {"data": hoje.isoformat(), "em": now_iso(),
                              "manual": escala.get("manual"), "bloco": escala.get("bloco", bloco),
                              "sensores_executados": executados, "adiados_por_tempo": adiados,
                              "duracao_s": round(_t.monotonic() - _ini),
                              "em_espera": escala["ficam"], "total_esquadra": escala["total"],
                              "previsoes_ativas": escala["previsoes_ativas"],
                              "achados": total_ach, "novos_na_base": novos, "por_tipo": por_tipo}
    write_json(ESTADO, est)
    return est["ultima_execucao"]


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
