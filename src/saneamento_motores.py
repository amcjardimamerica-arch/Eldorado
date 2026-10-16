"""SANEAMENTO DOS MOTORES (10/10/2026) — regras determinísticas aprendidas na revisão da Parte 1 (Goiás).

O QUE A REVISÃO MOSTROU (338 registros de Goiás lidos no documento oficial, 10/10/2026):
  * só 11 eram oportunidade vigente certificada (3,3%); 246 ruído, 44 encerradas, 29 fora do perfil, 8 duplicatas;
  * `fim` vazio em 62 de 71 oportunidades; as 12 encerradas já estavam vencidas no dia da coleta;
  * o selo "validada" acertou 1 de 8 (validava prazo vencido);
  * 8 edições inteiras de diário gravadas como "edital"; 7 empresas de fora gravadas com UF = GO;
  * o prazo do REGISTRO do PNCP (16/09/2027) não era o do EDITAL (17/10/2025) em Pirenópolis.

AS REGRAS (cada uma com o código do relatório docs/pareceres/saneamento-motores-p1-go-2026-10-10.md):
  M1  duplicata / peça de edital (anexo, minuta, alteração de cronograma) — liga ao edital-mãe;
  M3  não-oportunidade (home, índice, ouvidoria, notícia de resultado, extrato de termo já celebrado, redes sociais);
  M4  prazo extraído do texto do motor SÓ para encerrar (nunca para abrir); edição de diário antiga sem ato = encerrada;
  M5  UF/nível pelo território do edital, não pelo motor (empresa de fora não vira GO);
  M6  prazo do registro PNCP distante da publicação (> 400 dias) = suspeito, conferir no edital;
  M7  (em dashboard_dados.selo_validacao) "validada" exige prazo VIGENTE;
  M8  fora do perfil de OSC (credenciamento de serviço de saúde, linha de crédito, PMI);
  M12 tipo_registro = edicao_diario quando o registro é a edição inteira do diário;
  M13 painel de qualidade por motor (estado/qualidade_motores.json).

REGRA DE OURO: nada é apagado. "Descartar" = sair da caixa de abertas com o MOTIVO gravado e reversível.
A revisão humana (biblioteca_alexandria/livros/_acervo/editais/vereditos_revisao.json) vence qualquer regra automática.
Biblioteca-padrão apenas.
"""
from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config/saneamento_motores.json"
VEREDITOS = ROOT / "biblioteca_alexandria/livros/_acervo/editais/vereditos_revisao.json"
ESTADO = ROOT / "estado/saneamento_motores.json"
PAINEL = ROOT / "estado/qualidade_motores.json"

_CACHE: dict = {}


def cfg() -> dict:
    if "cfg" not in _CACHE:
        _CACHE["cfg"] = json.loads(CFG.read_text(encoding="utf-8")) if CFG.exists() else {}
    return _CACHE["cfg"]


def vereditos() -> dict:
    """Revisão humana por id (chave curta de 8 ou id inteiro) → {veredito, duplicata_de, reclassificar, fim, motivo}."""
    if "ver" not in _CACHE:
        bruto = json.loads(VEREDITOS.read_text(encoding="utf-8")).get("vereditos", {}) if VEREDITOS.exists() else {}
        _CACHE["ver"] = {**bruto, **{k[:8]: v for k, v in bruto.items() if re.fullmatch(r"[0-9a-f]{16,}", k)}}
    return _CACHE["ver"]


def limpar_cache() -> None:
    _CACHE.clear()


def _norm(t) -> str:
    t = re.sub(r"[\u2012-\u2015\u2212]", "-", str(t or "")).replace("ª", "a").replace("º", "o").replace("°", "o")
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", t).strip()


def _casa(rx: str, texto: str):
    """Casa a regex no texto cru (com acentos) e no texto normalizado (sem acentos) — as regras são escritas com acento."""
    if not rx:
        return None
    return re.search(rx, str(texto or ""), re.I) or re.search(_norm(rx), _norm(texto), re.I)


def _host(url: str) -> str:
    try:
        h = (urlsplit(str(url or "")).hostname or "").lower()
    except ValueError:
        return ""
    return h[4:] if h.startswith("www.") else h


def _texto(r: dict) -> str:
    return " ".join(str(r.get(k) or "") for k in ("titulo", "objeto", "evidencia", "url"))


# ── M1 · URL CANÔNICA, CHAVE DO EDITAL E DUPLICATAS ─────────────────────────────────────────────────────────────────
def url_canonica(url: str) -> str:
    """Sem embrulho de buscador, sem parâmetros de rastreio, sem fragmento, sem barra final, host minúsculo sem www."""
    try:
        from .nucleo import resolver_redirecionamento
        url = resolver_redirecionamento(url)
    except Exception:  # noqa: BLE001
        pass
    try:
        p = urlsplit(str(url or "").strip())
    except ValueError:
        return str(url or "")
    tira = set(cfg().get("M1_dedupe", {}).get("remover_parametros", []))
    q = urlencode([(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if k not in tira and not k.startswith("utm_")])
    host = (p.netloc or "").lower()
    host = host[4:] if host.startswith("www.") else host
    return urlunsplit(("https" if p.scheme in ("http", "https") else p.scheme, host, p.path.rstrip("/") or "/", q, ""))


_NUM = re.compile(r"(?:edital|chamamento|chamada|aviso|credenciamento|premia[çc][ãa]o|sele[çc][ãa]o)[^0-9\n]{0,40}?n?[º°o.]?\s*0*(\d{1,4})\s*[/\-]\s*(20\d\d)", re.I)


def numero_edital(texto: str) -> tuple[int, int] | None:
    m = _NUM.search(str(texto or ""))
    return (int(m.group(1)), int(m.group(2))) if m else None


def _orgao_chave(r: dict) -> str:
    """O emissor: o município/órgão citado no título ('Prefeitura de X — ...') ou o caminho do site oficial."""
    t = _norm(r.get("titulo"))
    m = re.match(r"(?:prefeitura (?:municipal )?de )?([a-z ]{3,40}?)\s+-\s+", t)
    if m and not re.search(r"edital|chamamento|aviso|diario", m.group(1)):
        return m.group(1).strip()
    if r.get("municipio"):
        return _norm(r["municipio"])
    u = urlsplit(url_canonica(r.get("url") or ""))
    seg = [s for s in u.path.split("/") if s][:1]
    if seg and u.netloc.endswith("goias.gov.br"):
        return f"{u.netloc}/{seg[0]}"
    # o domínio só identifica o emissor quando é o site oficial de UM órgão; agregador, DOU, PNCP e diário reúnem
    # editais de muitos emissores — "nº 3/2026" ali não identifica edital nenhum (devolve vazio = não deduplica por número)
    if re.search(r"\.(gov|leg|jus|mp)\.br$", u.netloc) and not re.search(r"(^|\.)(in|pncp)\.gov\.br$|diario|dom\.", u.netloc):
        return u.netloc
    return ""


_STOP = {"de", "da", "do", "das", "dos", "e", "a", "o", "para", "com", "r", "mil", "em", "no", "na", "prefeitura", "municipal", "lanca", "abre"}


def _tokens(t: str) -> set:
    return {w for w in re.findall(r"[a-z0-9]+", _norm(t)) if w not in _STOP and (len(w) > 1 or w.isdigit())}


def eh_peca_de_edital(titulo: str) -> bool:
    return bool(_casa(cfg().get("M1_dedupe", {}).get("pecas_de_edital"), str(titulo or "").strip()))


def agrupar_duplicatas(registros: list[dict]) -> dict:
    """id → {canonico, motivo}. Mesmo edital (emissor + número/ano), mesma URL canônica, ou mesma notícia no mesmo site
    (contenção de palavras ≥ 0,8 quando NENHUM dos dois tem número — números diferentes nunca se fundem)."""
    out: dict = {}
    vistos_url: dict = {}
    vistos_reg: dict = {}
    por_chave: dict = {}
    por_host: dict = defaultdict(list)
    lim = float(cfg().get("M1_dedupe", {}).get("contencao_minima_sem_numero", 0.8))
    for r in sorted(registros, key=lambda x: (eh_peca_de_edital(x.get("titulo") or ""), str(x.get("coletado_em") or ""), x["id"])):
        rid = r["id"]
        uc = url_canonica(r.get("url") or "")
        titulo = r.get("titulo") or ""
        if eh_edicao_diario(r):                                    # edição inteira: só a MESMA edição é duplicata
            if uc in vistos_url and eh_edicao_diario(vistos_reg[vistos_url[uc]]):
                out[rid] = {"canonico": vistos_url[uc], "motivo": "M1: mesma edição do diário"}
            vistos_url.setdefault(uc, rid); vistos_reg[rid] = r
            continue
        vistos_reg[rid] = r
        if r.get("numero_controle_pncp"):                          # PNCP: o número de controle é a identidade
            k = ("pncp", str(r["numero_controle_pncp"]))
            if k in por_chave:
                out[rid] = {"canonico": por_chave[k], "motivo": "M1: mesmo número de controle PNCP"}
            por_chave.setdefault(k, rid)
            continue
        if uc in vistos_url and not re.search(r"queridodiario|/visualizacoes/", uc):
            out[rid] = {"canonico": vistos_url[uc], "motivo": "M1: mesma URL canônica (sem parâmetros de rastreio)"}
            continue
        vistos_url.setdefault(uc, rid)
        num = numero_edital(titulo)
        org = _orgao_chave(r)
        if num and org:
            k = (org, *num)
            if k in por_chave:
                out[rid] = {"canonico": por_chave[k], "motivo": f"M1: mesmo edital nº {num[0]}/{num[1]} de {org}"}
                continue
            por_chave[k] = rid
        elif not num:
            tk = _tokens(titulo)
            h = urlsplit(uc).netloc
            if "pncp.gov.br" in h:
                continue
            for outro_id, outro_tk in por_host[h][-300:]:
                menor = min(len(tk), len(outro_tk))
                dig, dig_o = {w for w in tk if re.search(r"\d", w)}, {w for w in outro_tk if re.search(r"\d", w)}
                pequeno, grande = (dig, dig_o) if len(tk) <= len(outro_tk) else (dig_o, dig)
                if menor >= 5 and pequeno <= grande and len(tk & outro_tk) / menor >= lim:   # número que não bate = outro ato
                    out[rid] = {"canonico": outro_id, "motivo": "M1: mesma notícia/página do edital no mesmo site"}
                    break
            else:
                por_host[h].append((rid, tk))
    return out


# ── M3 · NÃO É OPORTUNIDADE ─────────────────────────────────────────────────────────────────────────────────────────
def nao_oportunidade(r: dict) -> str | None:
    c = cfg().get("M3_nao_oportunidade", {})
    url = str(r.get("url") or "")
    host = _host(url)
    titulo = _norm(r.get("titulo"))
    titulo_limpo = re.sub(r"^\d{1,2}:\d{2}\s+", "", titulo)
    for d in c.get("dominios", []):
        if host == d or host.endswith("." + d):
            return f"M3: rede social/vídeo ({d}) é só pista, não é oportunidade"
    for rx in c.get("url", []):
        if re.search(rx, url, re.I):
            return f"M3: página que não é edital ({rx})"
    for rx in c.get("titulo_exato", []):
        if re.fullmatch(_norm(rx), titulo_limpo.strip(" .-—()0123456789")) or re.fullmatch(_norm(rx), titulo_limpo):
            return "M3: página-índice ou institucional (título genérico) — vira fonte monitorada"
    cru = re.sub(r"^\s*\d{1,2}:\d{2}\s+", "", str(r.get("titulo") or "")).strip()
    for rx in c.get("titulo", []):
        if _casa(rx, cru):
            return f"M3: não é abertura de seleção ({rx.strip('^ ')})"
    palavras = c.get("palavras_de_edital") or "edital"
    caminho = urlsplit(url).path or "/"
    publico = bool(re.search(r"\.gov\.br$|\.leg\.br$|\.jus\.br$|\.mp\.br$", host))
    if not publico and not _casa(palavras, titulo):
        if caminho in ("", "/") or re.search(c.get("institucional_sem_edital") or r"$^", caminho, re.I):
            return "M3: página institucional de empresa/instituto sem edital — vira fonte monitorada"
    return None


# ── M4 · PRAZO (só para ENCERRAR) ───────────────────────────────────────────────────────────────────────────────────
def extrair_fim(texto: str) -> str | None:
    """Data-limite explícita no texto do motor ('inscrições até dd/mm/aaaa', 'de dd/mm/aaaa a dd/mm/aaaa'). Usada SÓ
    para reconhecer prazo VENCIDO — nunca para declarar uma oportunidade aberta (isso é trabalho do Cartório)."""
    for rx in cfg().get("M4_prazo", {}).get("padroes", []):
        for m in re.finditer(rx, str(texto or ""), re.I):
            d, mes, a = (int(x) for x in m.groups()[-3:])
            try:
                return date(a, mes, d).isoformat()
            except ValueError:
                continue
    return None


# ── M5 · TERRITÓRIO ─────────────────────────────────────────────────────────────────────────────────────────────────
def territorio_corrigido(r: dict) -> dict | None:
    """Devolve {uf, nivel, territorio, motivo} quando a UF gravada pelo motor contradiz o território do edital."""
    c = cfg().get("M5_territorio", {})
    host = _host(r.get("url"))
    if not host:
        return None
    if re.search(c.get("dominios_go") or r"$^", host):
        return None if r.get("uf") == "GO" else {"uf": "GO", "motivo": "M5: domínio oficial de Goiás"}
    if host in set(c.get("dominios_federais", [])):
        if r.get("uf") == "GO" or r.get("nivel") in (None, "", "privada", "municipal", "estadual"):
            return {"uf": None, "nivel": "federal", "territorio": "BR", "motivo": f"M5: órgão federal ({host}) — abrangência nacional"}
        return None
    if r.get("uf") == "GO" and r.get("nivel") in set(c.get("niveis_sujeitos", [])) \
            and not re.search(r"\.gov\.br$|\.leg\.br$|\.jus\.br$", host) \
            and not re.search(c.get("mencao_goias") or r"$^", _norm(_texto(r))):
        return {"uf": None, "territorio": "BR", "motivo": "M5: site de empresa/instituto sem menção a Goiás — a UF do motor não vale para o edital"}
    return None


# ── M6 · PRAZO DO REGISTRO PNCP ─────────────────────────────────────────────────────────────────────────────────────
def prazo_pncp_suspeito(r: dict) -> bool:
    if "pncp" not in str(r.get("fonte_id") or "") + str(r.get("url") or ""):
        return False
    fim, pub = str(r.get("fim") or "")[:10], str(r.get("data_publicacao") or r.get("abertura_propostas") or "")[:10]
    try:
        dias = (date.fromisoformat(fim) - date.fromisoformat(pub)).days
    except ValueError:
        return False
    return dias > int(cfg().get("M6_pncp", {}).get("dias_max_publicacao_ate_fim", 400))


# ── M8 · PERFIL ─────────────────────────────────────────────────────────────────────────────────────────────────────
def fora_do_perfil(r: dict) -> str | None:
    rx = cfg().get("M8_perfil", {}).get("fora_perfil")
    m = _casa(rx, f"{r.get('titulo') or ''} {r.get('objeto') or ''} {r.get('url') or ''}")
    return f"M8: fora do perfil de OSC («{m.group(0)}»)" if m else None


# ── M12 · TIPO DO REGISTRO ──────────────────────────────────────────────────────────────────────────────────────────
def eh_edicao_diario(r: dict) -> bool:
    c = cfg().get("M12_tipo_registro", {})
    if r.get("tipo_registro") == "edicao_diario":
        return True
    host = _host(r.get("url"))
    if not any(h in host for h in c.get("hosts_diario", [])) and r.get("tipo_fonte") != "diario_oficial_municipal":
        return False
    return bool(_casa(c.get("titulo_edicao"), r.get("titulo")))


# ── O REGISTRO SANEADO ──────────────────────────────────────────────────────────────────────────────────────────────
def ato_no_trecho(texto: str) -> tuple[bool, str]:
    """M14 (titular, 10/10/2026): o trecho encontrado na edição do diário mostra um ATO de abertura para o terceiro
    setor? (abertura + destinatário, e não é ato posterior). Devolve (passa?, motivo)."""
    c = cfg().get("M14_edicao_sem_ato") or {}
    t = re.sub(r"\s+", " ", str(texto or ""))
    if not t.strip():
        return False, "sem trecho do ato"
    if c.get("posterior") and re.search(c["posterior"], t, re.I):
        return False, "ato posterior (resultado, homologação, extrato, aditivo)"
    if not re.search(c.get("abertura") or r"$^", t, re.I):
        return False, "o trecho não mostra ato de abertura (edital, chamamento, seleção, inscrições)"
    if not re.search(c.get("destinatario") or r"$^", t, re.I):
        return False, "o trecho não mostra destinatário do terceiro setor"
    return True, ""


def sanear_registro(r: dict, hoje: date | None = None, duplicatas: dict | None = None) -> dict:
    """Diagnóstico de UM registro. Devolve:
       descartar: motivo | None   (sai da caixa de abertas; gravado e reversível)
       ajustes:   campos a sobrepor na linha de abertas (uf, nivel, territorio, tipo_registro, situacao, duplicata_de)
       alertas:   avisos para quem lê (prazo PNCP suspeito, prazo extraído etc.)
       regras:    códigos das regras que agiram."""
    hoje = hoje or date.today()
    h = hoje.isoformat()
    out = {"descartar": None, "ajustes": {}, "alertas": [], "regras": []}
    rid = str(r.get("id") or "")
    hum = vereditos().get(rid) or vereditos().get(rid[:8])
    if hum:                                                          # revisão humana vence
        v = hum.get("veredito")
        out["regras"].append("revisao_humana")
        rec = {k: x for k, x in (hum.get("reclassificar") or {}).items() if x}
        if v in ("ruido", "fora_perfil"):
            out["descartar"] = f"revisão humana ({hum.get('origem') or 'leitura do documento oficial'}): {v}"
        elif v == "validacao_manual":                               # 11/10 (titular): VERMELHO — validação/exclusão manual
            out["ajustes"].update({"selo_validacao": "validacao_manual",
                                   "motivo_tipo": ("VALIDAÇÃO MANUAL: o edital não pôde ser lido pelo Chrome — " + str(hum.get("motivo") or ""))[:300]})
        elif v == "duplicata":
            out["ajustes"].update({"tipo_registro": "duplicata", "duplicata_de": hum.get("duplicata_de"),
                                   "motivo_tipo": "revisão humana: mesmo edital de outro registro"})
        elif v == "encerrada":
            out["ajustes"].update({"situacao": "encerrada"})
            if hum.get("fim"):
                out["ajustes"]["fim"] = hum["fim"]
        for k in ("uf", "nivel"):
            if k in rec:
                out["ajustes"][k] = rec[k]
        if rec.get("tipo_registro") and "tipo_registro" not in out["ajustes"]:
            out["ajustes"]["tipo_registro"] = rec["tipo_registro"]
        if hum.get("fim") and v in ("ouro", "prata", "bronze", "pendente"):
            out["ajustes"]["fim"] = hum["fim"]
            if v != "pendente":                                          # prazo lido no documento oficial pela revisão
                out["ajustes"]["situacao"] = "aberta" if str(hum["fim"])[:10] >= h else "encerrada"
        return out
    motivo = nao_oportunidade(r)
    if motivo:
        out["descartar"] = motivo; out["regras"].append("M3")
        return out
    # M15 (titular, 11/10/2026): SÓ para oportunidade SEM nenhuma informação de prazo — sem validação há mais de
    # 30 dias na fila → arquivada (sai da caixa, com motivo). Com prazo de inscrição delimitado (no campo ou no texto,
    # vigente ou vencido), a regra NÃO se aplica: o próprio prazo decide (aberta até ele; depois, encerrada).
    _entrou = str(r.get("descoberto_em") or r.get("coletado_em") or "")[:10]
    _dias = int((cfg().get("M15_fila") or {}).get("dias_sem_validacao", 30))
    _tem_prazo = bool(r.get("fim") or r.get("inicio") or re.search(r"\d{1,2}[/.]\d{1,2}|\d{4}-\d{2}-\d{2}|\d{1,2}\s+de\s+[a-zç]+", str(r.get("prazo_texto") or ""), re.I))
    try:
        if _entrou and not _tem_prazo and not r.get("validado") and (hoje - date.fromisoformat(_entrou)).days > _dias:
            out["descartar"] = f"M15: {_dias} dias na fila sem validação (entrou em {_entrou}) — arquivada"; out["regras"].append("M15")
            return out
    except ValueError:
        pass
    motivo = fora_do_perfil(r)
    if motivo:
        out["descartar"] = motivo; out["regras"].append("M8")
        return out
    if eh_peca_de_edital(r.get("titulo") or ""):
        out["ajustes"].update({"tipo_registro": "duplicata", "motivo_tipo": "M1: peça de edital (anexo/minuta/alteração) — vale o edital-mãe"})
        out["regras"].append("M1")
    if duplicatas and rid in duplicatas:
        out["ajustes"].update({"tipo_registro": "duplicata", "duplicata_de": duplicatas[rid]["canonico"], "motivo_tipo": duplicatas[rid]["motivo"]})
        out["regras"].append("M1")
    if eh_edicao_diario(r) and out["ajustes"].get("tipo_registro") != "duplicata":
        out["ajustes"]["tipo_registro"] = "edicao_diario"
        out["ajustes"]["motivo_tipo"] = "M12: edição inteira do diário — o que conta é o ATO dentro dela"
        out["regras"].append("M12")
        # M14 (titular, 10/10/2026): sem ato no trecho, a edição não compreende o léxico/critério — ELIMINADA da caixa
        _ext = ROOT / "dados/editais/extraidos" / f"{rid}.json"
        if not r.get("fim") and not _ext.exists():
            _ok, _porque = ato_no_trecho(r.get("evidencia") or "")
            if not _ok:
                out["descartar"] = f"M14: edição de diário eliminada no motor — {_porque}"
                out["regras"].append("M14")
                return out
        pub = str(r.get("data_publicacao") or "")[:10]
        lim = int(cfg().get("M4_prazo", {}).get("edicao_diario_dias_max_sem_ato", 120))
        try:
            if pub and not r.get("fim") and (hoje - date.fromisoformat(pub)).days > lim:
                out["ajustes"]["situacao"] = "encerrada"
                out["alertas"].append(f"M4: edição de {pub} (mais de {lim} dias) sem ato com prazo — vai para o histórico")
                out["regras"].append("M4")
        except ValueError:
            pass
    t = territorio_corrigido(r)
    if t:
        out["alertas"].append(t.pop("motivo")); out["ajustes"].update(t); out["regras"].append("M5")
    if not r.get("fim"):
        f = extrair_fim(f"{r.get('titulo') or ''} {r.get('evidencia') or ''} {r.get('prazo_texto') or ''}")
        if f and f < h:
            out["ajustes"].update({"situacao": "encerrada", "fim": f})
            out["alertas"].append(f"M4: prazo {f} lido no texto do motor já venceu")
            out["regras"].append("M4")
    if prazo_pncp_suspeito(r):
        out["alertas"].append("M6: prazo do registro PNCP muito distante da publicação — conferir o cronograma no arquivo do edital")
        out["ajustes"]["prazo_pncp_suspeito"] = True
        if out["ajustes"].get("situacao") != "encerrada":
            out["ajustes"]["situacao"] = "possivel"
        out["regras"].append("M6")
    return out


def sanear_abertas(registros: list[dict], hoje: date | None = None) -> tuple[list[dict], dict]:
    """Aplica as regras a uma lista de registros (formato da base). Devolve (registros mantidos com ajustes aplicados,
    relatório com descartes e contagens). Os ajustes vão em `saneamento` dentro de cada registro."""
    hoje = hoje or date.today()
    dups = agrupar_duplicatas(registros)
    mantidos, descartes = [], []
    for r in registros:
        s = sanear_registro(r, hoje, dups)
        if s["descartar"]:
            descartes.append({"id": r.get("id"), "titulo": str(r.get("titulo") or "")[:140], "url": r.get("url"),
                              "fonte_nome": r.get("fonte_nome"), "motivo": s["descartar"]})
            continue
        mantidos.append({**r, **s["ajustes"], "saneamento": {"regras": s["regras"], "alertas": s["alertas"]}} if s["regras"] else r)
    return mantidos, {"descartes": descartes, "duplicatas": dups}


# ── M13 · PAINEL DE QUALIDADE POR MOTOR ─────────────────────────────────────────────────────────────────────────────
def painel_qualidade(registros: list[dict], mantidos: list[dict], descartes: list[dict], hoje: date | None = None) -> dict:
    hoje = hoje or date.today()
    h = hoje.isoformat()
    por = defaultdict(Counter)
    for r in registros:
        f = r.get("fonte_nome") or r.get("fonte_id") or "?"
        por[f]["trouxe"] += 1
        por[f]["fim_vazio"] += not r.get("fim")
        por[f]["valor_vazio"] += not r.get("valor_texto")
    for d in descartes:
        f = d.get("fonte_nome") or "?"
        por[f]["descartados"] += 1
        por[f]["fora_perfil" if "M8" in d["motivo"] or "fora_perfil" in d["motivo"] else "ruido"] += 1
    for r in mantidos:
        f = r.get("fonte_nome") or r.get("fonte_id") or "?"
        if r.get("tipo_registro") == "duplicata":
            por[f]["duplicatas"] += 1
        elif r.get("situacao") == "encerrada" or (r.get("fim") and str(r["fim"])[:10] < h):
            por[f]["encerradas"] += 1
        elif r.get("tipo_registro") == "edicao_diario":
            por[f]["edicoes_diario"] += 1
        else:
            por[f]["candidatas"] += 1
        if "M5" in ((r.get("saneamento") or {}).get("regras") or []):
            por[f]["uf_corrigida"] += 1
    lim = float(cfg().get("M13_painel", {}).get("rebaixar_abaixo_de_precisao", 0.05))
    motores = []
    for f, c in sorted(por.items(), key=lambda kv: -kv[1]["trouxe"]):
        n = c["trouxe"] or 1
        motores.append({"motor": f, **dict(c), "aproveitamento": round(c["candidatas"] / n, 3),
                        "ruido_pct": round((c["ruido"] + c["fora_perfil"]) / n, 3), "duplicata_pct": round(c["duplicatas"] / n, 3),
                        "fim_vazio_pct": round(c["fim_vazio"] / n, 3),
                        "alerta": ("abaixo do mínimo — candidato a 'fonte monitorada'" if c["trouxe"] >= 3 and c["candidatas"] / n < lim else None)})
    return {"em": h, "regra": "M13 — medido a cada geração de abertas.json; candidatas = não descartadas, não duplicatas, não encerradas",
            "parametros_minimos": {"aproveitamento": ">= 0,15", "duplicata_pct": "< 0,05", "ruido_pct": "< 0,10", "fim_vazio_pct": "< 0,05"},
            "motores": motores}


def gravar_estado(rel: dict, painel: dict) -> None:
    ESTADO.parent.mkdir(parents=True, exist_ok=True)
    ESTADO.write_text(json.dumps({"em": painel.get("em"), "versao": cfg().get("versao"), "descartes": rel["descartes"],
                                  "duplicatas": rel["duplicatas"]}, ensure_ascii=False, indent=1), encoding="utf-8")
    PAINEL.write_text(json.dumps(painel, ensure_ascii=False, indent=1), encoding="utf-8")
