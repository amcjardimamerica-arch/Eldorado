"""Motor de empresas com afinidade com o terceiro setor — por estado (GO ativo).

Segue os parâmetros do titular (config/empresas.json):
  • só MATRIZES, CNPJ ativo, capital social > R$ 10 mi (exatamente 10 mi não atende);
  • Lucro Real em três categorias — confirmado / altamente provável / não confirmado —
    nunca deduzido só pelo tamanho;
  • histórico de 5 anos de destinações (Rouanet via SALIC, LIE, PRONON/PRONAS) e
    doações; ESG; instituto/fundação; decisores;
  • score 0–100 com os pesos do titular e classes de prioridade;
  • nada inventado: sem fonte → "não confirmado" / "não divulgado".

Fontes automatizáveis hoje:
  1. lista oficial dos MAIORES CONTRIBUINTES DO ICMS de Goiás (Economia-GO) — nomes e,
     quando divulgados, CNPJ e valor, por ano;
  2. dados públicos de CNPJ da Receita Federal (espelhos minhareceita/brasilapi):
     matriz, situação, capital, CNAE, porte, QSA, endereço, opção pelo Simples;
  3. incentivadores da Lei Rouanet (API SALIC do MinC) por CNPJ — projeto, ano, valor;
  4. listas da Lei de Incentivo ao Esporte e PRONON/PRONAS (páginas oficiais).
IRPJ pago é sigilo fiscal: só existe quando a empresa publica demonstrações — o
motor registra "não divulgado publicamente" e usa Lucro Real + capital + histórico
como proxies. ICMS pago vem da lista de maiores contribuintes quando o valor é
divulgado; senão, a posição no ranking.

Saída: biblioteca_alexandria/empresas/<uf>.json (completo) e fragmento compacto
para o painel (docs/dados/empresas.json).
"""
from __future__ import annotations

import json
import re
import time
from datetime import date, datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from .nucleo import ROOT, load_json, now_iso, write_json

CFG = ROOT / "config/empresas.json"
PASTA = ROOT / "dados/empresas"
BIB = ROOT / "biblioteca_alexandria/empresas"
UA = {"User-Agent": "Eldorado-OSC/1.0 contato-via-repositorio", "Accept": "text/html,application/json,application/pdf;q=0.8,*/*;q=0.2"}
CNPJ_RX = re.compile(r"\b(\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2})\b")
VALOR_RX = re.compile(r"R\$\s?([\d\.]+,\d{2})|(\d{1,3}(?:\.\d{3}){2,},\d{2})")


def _cfg() -> dict:
    return load_json(CFG)


def _get(url: str, timeout: int = 25, binario: bool = False):
    req = Request(url, headers=UA)
    with urlopen(req, timeout=timeout) as r:
        dados = r.read(12_000_000)
        return dados if binario else dados.decode("utf-8", "replace")


def so_digitos(c: str) -> str:
    return re.sub(r"\D", "", c or "")


def cnpj_fmt(c: str) -> str:
    d = so_digitos(c)
    return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}" if len(d) == 14 else c


# ───────────────────────── 1. maiores contribuintes do ICMS ─────────────────────────
class _Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []; self.texto = []; self._h = None; self._t = []
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._h = dict(attrs).get("href"); self._t = []
    def handle_data(self, d):
        self.texto.append(d)
        if self._h is not None:
            self._t.append(d)
    def handle_endtag(self, tag):
        if tag == "a" and self._h is not None:
            self.links.append((self._h, " ".join(self._t).strip())); self._h = None


def _texto_pdf(dados: bytes) -> str:
    try:
        from pypdf import PdfReader
        import io
        return "\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(dados)).pages[:80])
    except Exception:
        return ""


def cnpj_matriz_da_raiz(raiz: str) -> str | None:
    """A matriz é sempre o estabelecimento 0001: calcula os dígitos verificadores."""
    d = so_digitos(raiz)
    if len(d) != 8:
        return None
    base = d + "0001"
    def dv(nums, pesos):
        s = sum(int(n) * p for n, p in zip(nums, pesos)); r = s % 11
        return "0" if r < 2 else str(11 - r)
    d1 = dv(base, [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]); d2 = dv(base + d1, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    return cnpj_fmt(base + d1 + d2)


# formato da lista oficial de Goiás: "1º 33000167 PETROLEO BRASILEIRO S A PETROBRAS DIVERSOS BR COMBUSTÍVEL"
_UFS = "AC|AL|AM|AP|BA|BR|CE|DF|ES|GO|MA|MG|MS|MT|PA|PB|PE|PI|PR|RJ|RN|RO|RR|RS|SC|SE|SP|TO"
_LINHA_GO = re.compile(r"^(\d{1,3})\s*[ºª°.]?\s+(\d{8})\s+(.+)\s+(" + _UFS + r")\s+([A-ZÀ-Ú][^\n]{2,60})$")
_SUFIXO_EMP = re.compile(r"^(S\.?A\.?|S/A|LTDA\.?|EIRELI|ME|EPP|CIA\.?|COM\.?|IND\.?|COMERCIO|INDUSTRIA|DISTRIBUIDORA|ATACADISTA|SERVICOS|PARTICIPACOES|HOLDING|BRASIL|.*[0-9/.&].*)$", re.I)
_PREF_MUN = {"APARECIDA", "SENADOR", "RIO", "SANTO", "SANTA", "SAO", "SÃO", "BOM", "NOVA", "NOVO", "CIDADE", "PORTO", "MONTE", "SANTA", "PIRES", "SAO", "BELA", "ALTO", "CAMPO", "PADRE", "SAO"}


def _separa_nome_municipio(miolo: str):
    """'... S/A GOIANIA' → ('... S/A','Goiânia'); 'LTDA. APARECIDA DE GOIANIA' →
    município com prefixo composto; 'PETROBRAS DIVERSOS' → 'Diversos'."""
    toks = miolo.split()
    if toks and toks[-1].upper() == "DIVERSOS":
        return " ".join(toks[:-1]), "Diversos (vários estabelecimentos)"
    # 1 palavra alfabética que não seja sufixo empresarial
    if not toks or _SUFIXO_EMP.match(toks[-1]):
        return miolo, None
    mun = [toks[-1]]; i = len(toks) - 2
    # prefixos compostos: APARECIDA DE GOIANIA, SENADOR CANEDO, RIO VERDE, SAO LUIS DE MONTES BELOS…
    while i >= 0 and len(mun) < 5:
        w = toks[i].upper()
        if w in ("DE", "DO", "DA", "DOS", "DAS") and i - 1 >= 0 and toks[i - 1].upper() in _PREF_MUN:
            mun[:0] = [toks[i - 1], toks[i]]; i -= 2; continue
        if w in _PREF_MUN:
            mun.insert(0, toks[i]); i -= 1; continue
        break
    return " ".join(toks[:i + 1]), " ".join(mun).title()


def extrair_contribuintes(texto: str, ano: int | None = None) -> list[dict]:
    """Extrai linhas 'posição — nome — CNPJ — valor' de um texto (HTML ou PDF) de
    lista de maiores contribuintes. Tolerante: nome é obrigatório; CNPJ e valor
    entram quando existem."""
    saida, vistos = [], set()
    for linha in re.split(r"[\r\n]+|(?<=\))\s{2,}", texto):
        l = re.sub(r"\s+", " ", linha).strip()
        if len(l) < 6 or len(l) > 400:
            continue
        mg = _LINHA_GO.match(l)
        if mg:
            pos, raiz, miolo, uf, setor = mg.groups()
            nome, mun = _separa_nome_municipio(miolo)
            mun = mun or "não informado na lista"
            chave = raiz
            if chave in vistos:
                continue
            vistos.add(chave)
            saida.append({"posicao": int(pos), "nome": nome.strip()[:160], "cnpj": cnpj_matriz_da_raiz(raiz), "cnpj_raiz": raiz,
                          "municipio_lista": mun,
                          "uf_lista": uf, "setor": setor.strip().title(), "icms_valor_texto": None, "ano": ano,
                          "nota": "CNPJ da matriz calculado a partir da raiz publicada (estabelecimento 0001)"})
            continue
        m_cnpj = CNPJ_RX.search(l)
        m_val = VALOR_RX.search(l)
        m_pos = re.match(r"^(\d{1,3})[ºª°.\-–)]?\s+(.*)", l)
        nome = None
        if m_pos:
            resto = m_pos.group(2)
            nome = CNPJ_RX.split(resto)[0] if m_cnpj else VALOR_RX.split(resto)[0]
            nome = re.sub(r"^[\-–|;:.)\s]+|[\-–|;:]+$", "", (nome or "").strip()).strip()
        elif m_cnpj:
            nome = re.sub(r"[\-–|;:]+$", "", l[:m_cnpj.start()].strip()).strip()
        if not nome or len(nome) < 4 or not re.search(r"[A-Za-zÀ-ú]{3}", nome):
            continue
        if re.search(r"^(pos|posi[çc][ãa]o|ranking|contribuinte|raz[ãa]o social|cnpj|valor|total|fonte|secretaria|maiores contribuintes|de janeiro|de fevereiro|de mar[çc]o|de abril|de maio|de junho|de julho|de agosto|de setembro|de outubro|de novembro|de dezembro)\b", nome, re.I):
            continue
        chave = so_digitos(m_cnpj.group(1)) if m_cnpj else nome.upper()
        if chave in vistos:
            continue
        vistos.add(chave)
        saida.append({"posicao": int(m_pos.group(1)) if m_pos else None, "nome": nome[:160],
                      "cnpj": cnpj_fmt(m_cnpj.group(1)) if m_cnpj else None,
                      "icms_valor_texto": (m_val.group(0) if m_val else None), "ano": ano})
    return saida


def coletar_maiores_contribuintes(uf: str) -> dict:
    """Lê a página oficial e seus anexos (PDF) e guarda a lista por ano em
    dados/empresas/<uf>/contribuintes_icms.json. Nunca inventa: se a página não
    trouxer a lista, registra o motivo."""
    est = _cfg()["estados"][uf]
    fonte = est["maiores_contribuintes_icms"]
    destino = PASTA / uf.lower() / "contribuintes_icms.json"
    atual = load_json(destino) if destino.exists() else {"uf": uf, "fonte": fonte["fonte"], "url": fonte["url"], "anos": {}, "leituras": []}
    leitura = {"em": now_iso(), "url": fonte["url"]}
    try:
        html = _get(fonte["url"])
        p = _Links(); p.feed(html)
        texto = " ".join(p.texto)
        achados = extrair_contribuintes(texto)
        anexos = [(urljoin(fonte["url"], h), t) for h, t in p.links
                  if h and (h.lower().endswith(".pdf") or re.search(r"contribuint|ranking|maiores", (t or "") + h, re.I))]
        leitura["anexos_encontrados"] = len(anexos)
        lidos = 0
        for href, rot in anexos[:6]:
            ano = (re.search(r"20\d{2}", rot + href) or [None])[0] if re.search(r"20\d{2}", rot + href) else None
            try:
                if href.lower().endswith(".pdf"):
                    dados = _get(href, binario=True)
                    txt = _texto_pdf(dados)
                else:
                    txt = " ".join(_Links().texto) if False else re.sub(r"<[^>]+>", " ", _get(href))
                itens = extrair_contribuintes(txt, int(ano) if ano else None)
                if itens:
                    chave = ano or str(date.today().year)
                    atual["anos"][chave] = {"origem": href, "rotulo": rot, "lido_em": now_iso(), "empresas": itens[:300]}
                    lidos += 1
            except Exception as exc:
                leitura.setdefault("falhas", []).append({"url": href, "erro": type(exc).__name__})
            time.sleep(0.6)
        if achados and not lidos:
            atual["anos"][str(date.today().year)] = {"origem": fonte["url"], "rotulo": "página", "lido_em": now_iso(), "empresas": achados[:300]}
        leitura.update({"http": 200, "empresas_na_pagina": len(achados), "anexos_lidos": lidos})
    except Exception as exc:
        leitura.update({"erro": type(exc).__name__})
    atual["leituras"] = (atual.get("leituras") or [])[-30:] + [leitura]
    write_json(destino, atual)
    return {"uf": uf, "anos": sorted(atual["anos"]), "leitura": leitura}


# ───────────────────────── 2. cadastro RFB (espelhos públicos) ─────────────────────────
def cadastro_cnpj(cnpj: str) -> dict | None:
    d = so_digitos(cnpj)
    if len(d) != 14:
        return None
    cache = PASTA / "cadastro" / f"{d}.json"
    cfg = _cfg()["cadastro"]
    if cache.exists():
        c = load_json(cache)
        try:
            if datetime.fromisoformat(c["_consultado_em"][:19]) > datetime.utcnow() - timedelta(days=cfg["cache_dias"]):
                return c
        except Exception:
            pass
    for api in (cfg["api_primaria"], cfg["api_secundaria"]):
        try:
            js = json.loads(_get(api.format(cnpj=d), timeout=20))
            reg = _normaliza_cadastro(js, api)
            reg["_consultado_em"] = now_iso()
            write_json(cache, reg)
            return reg
        except Exception:
            continue
    return None


def _normaliza_cadastro(js: dict, fonte: str) -> dict:
    g = lambda *ks: next((js[k] for k in ks if k in js and js[k] not in (None, "")), None)
    qsa = js.get("qsa") or []
    return {
        "cnpj": cnpj_fmt(str(g("cnpj") or "")), "razao_social": g("razao_social", "nome"), "nome_fantasia": g("nome_fantasia", "fantasia"),
        "matriz": (g("identificador_matriz_filial") in (1, "1", "MATRIZ")) or (g("descricao_identificador_matriz_filial", "tipo") in ("MATRIZ",)),
        "situacao": g("descricao_situacao_cadastral", "situacao_cadastral", "situacao"),
        "abertura": g("data_inicio_atividade", "abertura"),
        "natureza_juridica": g("natureza_juridica"), "cnae_principal": g("cnae_fiscal_descricao", "atividade_principal"),
        "cnae_codigo": str(g("cnae_fiscal") or ""), "capital_social": float(g("capital_social") or 0) or None,
        "porte": g("porte", "descricao_porte"), "municipio": g("municipio"), "uf": g("uf"), "bairro": g("bairro"),
        "logradouro": g("logradouro"), "cep": g("cep"), "telefone": g("ddd_telefone_1", "telefone"), "email": g("email"),
        "opcao_simples": g("opcao_pelo_simples"), "opcao_mei": g("opcao_pelo_mei"),
        "qsa": [{"nome": q.get("nome_socio") or q.get("nome"), "qualificacao": q.get("qualificacao_socio") or q.get("qual"),
                 "entrada": q.get("data_entrada_sociedade")} for q in qsa[:30]],
        "fonte_cadastro": fonte.split("/")[2],
    }


# ───────────────────────── 3. histórico de destinações (5 anos) ─────────────────────────
def destinacoes_rouanet(cnpj: str, anos: int = 5) -> dict:
    """Incentivadores da Lei Rouanet (API SALIC) — por CNPJ, com projeto, ano e valor."""
    d = so_digitos(cnpj)
    cache = PASTA / "destinacoes" / f"{d}_rouanet.json"
    if cache.exists():
        return load_json(cache)
    saida = {"fonte": "SALIC/MinC", "consultado_em": now_iso(), "itens": [], "status": "sem_registro"}
    try:
        js = json.loads(_get(_cfg()["destinacoes"]["rouanet_salic"]["api"].format(cnpj=d), timeout=25))
        emb = (js.get("_embedded") or {}).get("incentivadores") or js.get("incentivadores") or []
        corte = date.today().year - anos
        for it in emb:
            ano = it.get("ano") or (str(it.get("data_recibo") or "")[:4] or None)
            try:
                if ano and int(ano) < corte:
                    continue
            except ValueError:
                pass
            saida["itens"].append({"programa": "Lei Rouanet", "ano": ano, "projeto": it.get("nome_projeto") or it.get("PRONAC"),
                                   "pronac": it.get("PRONAC"), "valor": it.get("valor") or it.get("total_doado"),
                                   "uf_projeto": it.get("UF"), "fonte": "SALIC", "url": "https://salic.cultura.gov.br"})
        saida["status"] = "com_registro" if saida["itens"] else "sem_registro"
    except Exception as exc:
        saida["status"] = f"falha: {type(exc).__name__}"
    write_json(cache, saida)
    return saida


# ───────────────────────── 4. classificações ─────────────────────────
def classificar_lucro_real(cad: dict, hist: list[dict]) -> dict:
    cfg = _cfg()["lucro_real"]
    if cad.get("opcao_simples") in (True, "SIM", "S"):
        return {"classe": "nao_confirmado", "motivo": "optante do Simples Nacional — não é Lucro Real", "fonte": cad.get("fonte_cadastro")}
    cn = (cad.get("cnae_codigo") or "")[:2]
    if cn in cfg["cnaes_obrigados"]:
        return {"classe": "altamente_provavel", "motivo": f"CNAE {cn} (Seção K — financeiro/seguros) obrigado ao Lucro Real (Lei 9.718/98, art. 14)", "fonte": "RFB + norma"}
    # destinou por Rouanet/LIE/PRONON → só pessoas jurídicas do Lucro Real podem — confirmação objetiva
    if any(h.get("programa") in ("Lei Rouanet", "Lei de Incentivo ao Esporte", "PRONON", "PRONAS/PCD") for h in hist):
        return {"classe": "confirmado", "motivo": "destinou por incentivo fiscal federal (exclusivo de PJ no Lucro Real) — fonte oficial do programa",
                "fonte": "SALIC/MinC ou Ministério do Esporte"}
    if (cad.get("porte") or "").upper().startswith("DEMAIS") and (cad.get("capital_social") or 0) > 50_000_000 and not cad.get("opcao_simples"):
        return {"classe": "altamente_provavel", "motivo": "porte 'demais' + capital social acima de R$ 50 mi, fora do Simples", "fonte": cad.get("fonte_cadastro")}
    return {"classe": "nao_confirmado", "motivo": "sem elemento objetivo de regime; não deduzido pelo tamanho", "fonte": None}


def score_empresa(cad: dict, hist: list[dict], lucro: dict, extras: dict | None = None) -> dict:
    p = _cfg()["score"]; extras = extras or {}
    pts, memoria = 0, []
    if lucro["classe"] == "confirmado":
        pts += p["lucro_real_confirmado"]; memoria.append(f"Lucro Real confirmado +{p['lucro_real_confirmado']}")
    elif lucro["classe"] == "altamente_provavel":
        pts += p["lucro_real_confirmado"] // 2; memoria.append(f"Lucro Real altamente provável +{p['lucro_real_confirmado'] // 2}")
    fiscais = [h for h in hist if h.get("programa") in ("Lei Rouanet", "Lei de Incentivo ao Esporte", "PRONON", "PRONAS/PCD", "FIA", "Fundo do Idoso")]
    if fiscais:
        v = min(p["historico_destinacao_fiscal"], 8 + 4 * len({h.get("ano") for h in fiscais}))
        pts += v; memoria.append(f"destinação fiscal em {len({h.get('ano') for h in fiscais})} ano(s) +{v}")
    cap = cad.get("capital_social") or 0
    if cap > 10_000_000:
        v = 4 if cap <= 50_000_000 else 7 if cap <= 500_000_000 else p["capital_social"]
        pts += v; memoria.append(f"capital social R$ {cap:,.0f} +{v}".replace(",", "."))
    if extras.get("doacoes"):
        pts += p["historico_doacoes"]; memoria.append(f"histórico de doações +{p['historico_doacoes']}")
    if extras.get("esg") == "forte":
        pts += p["esg_estruturado"]; memoria.append("ESG estruturado +10")
    elif extras.get("esg") == "moderado":
        pts += 5; memoria.append("ESG moderado +5")
    if extras.get("atuacao_social"):
        pts += p["atuacao_social"]; memoria.append("atuação social +10")
    if extras.get("instituto_fundacao"):
        pts += p["instituto_ou_fundacao"]; memoria.append("instituto/fundação +5")
    if extras.get("distancia_km") is not None:
        v = p["proximidade_territorial"] if extras["distancia_km"] <= 15 else 2 if extras["distancia_km"] <= 60 else 0
        pts += v; memoria.append(f"proximidade {extras['distancia_km']:.0f} km +{v}")
    if extras.get("decisor"):
        pts += p["decisor_localizado"]; memoria.append("decisor localizado +5")
    if extras.get("compatibilidade"):
        pts += p["compatibilidade_projetos"]; memoria.append("compatibilidade +5")
    pts = min(100, pts)
    classe = next(v for k, v in sorted(p["classes"].items(), key=lambda kv: -int(kv[0])) if pts >= int(k))
    return {"score": pts, "classe": classe, "memoria": memoria}


def potencial_destinacao(hist: list[dict], lucro: dict) -> dict:
    """Potencial de destinação tributária por mecanismo (cultura/esporte/FIA…):
    'já destina' quando há registro nos 5 anos; 'apto' quando Lucro Real
    confirmado/provável; 'não confirmado' nos demais."""
    def grau(programas):
        if any(h.get("programa") in programas for h in hist):
            return "ja_destina"
        return "apto" if lucro["classe"] in ("confirmado", "altamente_provavel") else "nao_confirmado"
    return {"cultura": grau(("Lei Rouanet",)), "esporte": grau(("Lei de Incentivo ao Esporte",)),
            "fia_idoso": grau(("FIA", "Fundo do Idoso")), "saude": grau(("PRONON", "PRONAS/PCD"))}


# ───────────────────────── 4b. GIFE, site institucional, área potencial, predição ─────────────────────────
def coletar_gife() -> dict:
    """Associados do GIFE (investidores sociais privados) — lista pública."""
    cfg = _cfg()["gife"]; destino = PASTA / "gife_associados.json"
    atual = load_json(destino) if destino.exists() else {"fonte": cfg["fonte"], "url": cfg["url"], "associados": [], "leituras": []}
    leitura = {"em": now_iso()}
    try:
        html = _get(cfg["url"])
        p = _Links(); p.feed(html)
        nomes = []
        MENU = re.compile(r"^(investimento social|transpar|not[íi]cias|associados gife|especial|quem somos|contato|home|blog|agenda|eventos|publica|sobre|redegife)", re.I)
        for h, rot in p.links:
            r = re.sub(r"\s+", " ", rot or "").strip()
            r = re.sub(r"\s+[a-z0-9\-]{6,}(\s+[A-ZÀ-Ú].*)?$", lambda m: (m.group(1) or ""), r).strip()   # remove o slug colado ao nome
            if 4 <= len(r) <= 90 and not MENU.search(r) and re.search(r"instituto|funda[çc][ãa]o|associa[çc][ãa]o|grupo|s\.a\.|ltda|bank|banco|holding|companhia|\bs/a\b|movimento|centro|rede", r, re.I):
                nomes.append({"nome": r, "url": urljoin(cfg["url"], h) if h else None})
        # e itens de lista/cards sem link
        for m in re.finditer(r">([^<>]{4,90}(?:Instituto|Funda[çc][ãa]o|Associa[çc][ãa]o)[^<>]{0,60})<", html):
            nomes.append({"nome": re.sub(r"\s+", " ", m.group(1)).strip(), "url": None})
        vistos, lista = set(), []
        for n in nomes:
            k = n["nome"].upper()
            if k not in vistos:
                vistos.add(k); lista.append(n)
        if lista:
            atual["associados"] = lista; atual["lido_em"] = now_iso()
        leitura.update({"http": 200, "associados": len(lista)})
    except Exception as exc:
        leitura["erro"] = type(exc).__name__
    atual["leituras"] = (atual.get("leituras") or [])[-20:] + [leitura]
    write_json(destino, atual)
    return {"associados": len(atual.get("associados", [])), "leitura": leitura}


def gife_casa(nome: str, fantasia: str | None, gife: list[dict]) -> dict | None:
    toks = lambda s: {t for t in re.findall(r"[a-zà-ú]{4,}", (s or "").lower()) if t not in ("ltda", "instituto", "fundação", "fundacao", "grupo", "brasil", "associação", "associacao")}
    alvo = toks(nome) | toks(fantasia)
    for g in gife:
        if len(alvo & toks(g["nome"])) >= 2 and toks(g["nome"]):     # dois termos em comum (decisão do conselho)
            return g
    return None


LEXICO_SITE = re.compile(r"patroc[íi]nio|edital|chamada|inscri[çc][õo]es|doa[çc][ãa]o|instituto|funda[çc][ãa]o|responsabilidade social|"
                         r"investimento social|volunt[áa]ri|sustentabilidade|ESG|terceiro setor|OSC|projeto social|comunidade|"
                         r"Rouanet|incentivo ao esporte|FIA|fundo da crian[çc]a|fundo do idoso|PRONON|PRONAS", re.I)


def varrer_site(cad: dict) -> dict:
    """Site institucional (inferido do e-mail corporativo do cadastro): lê a home e
    páginas de sustentabilidade/notícias/instituto e recorta os trechos que falam
    de patrocínio, edital, doação, instituto/fundação, ESG."""
    email = (cad or {}).get("email") or ""
    dom = email.split("@")[-1].lower().strip() if "@" in email else None
    if not dom or any(x in dom for x in ("gmail", "hotmail", "outlook", "yahoo", "uol", "terra", "bol.")):
        return {"status": "sem_site_institucional_inferivel", "dominio": dom}
    base = f"https://www.{dom}" if not dom.startswith("www.") else f"https://{dom}"
    achados, lidas, falhas = [], 0, 0
    for path in ("", "/sustentabilidade", "/responsabilidade-social", "/instituto", "/noticias", "/esg", "/patrocinios", "/editais"):
        try:
            html = _get(base + path, timeout=15)
            lidas += 1
            txt = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S)
            txt = re.sub(r"<[^>]+>", " ", txt); txt = re.sub(r"\s+", " ", txt)
            for m in LEXICO_SITE.finditer(txt):
                tr = txt[max(0, m.start() - 90): m.end() + 110].strip()
                achados.append({"pagina": base + path, "termo": m.group(0), "trecho": tr})
                if len(achados) >= 40:
                    break
        except Exception:
            falhas += 1
        time.sleep(0.4)
        if lidas + falhas >= 5:
            break
    termos = sorted({a["termo"].lower() for a in achados})
    return {"status": "lido" if lidas else "sem_resposta", "site": base, "paginas_lidas": lidas, "falhas": falhas,
            "termos": termos, "achados": achados[:25], "em": now_iso(),
            "sinais": {"patrocinio": any("patroc" in t for t in termos), "edital": any(t.startswith(("edital", "chamada", "inscri")) for t in termos),
                       "instituto_fundacao": any(t.startswith(("instituto", "funda")) for t in termos), "esg": any(t in ("esg", "sustentabilidade") for t in termos)}}


def area_potencial(cad: dict) -> dict:
    tab = _cfg()["area_potencial_por_cnae"]
    cn = (cad or {}).get("cnae_codigo") or ""
    reg = tab.get(cn[:2]) or tab["default"]
    return {"cnae_divisao": cn[:2] or None, "areas": reg["areas"], "proposta_de_valor": reg["proposta"]}


def predicao(lucro: dict, hist: list[dict], site: dict | None, gife: dict | None, elegivel) -> dict:
    """Análise preditiva simples e explicável: quem JÁ DOOU × quem TEM POTENCIAL."""
    if hist:
        return {"classe": "ja_doou", "probabilidade": "alta", "base": f"{len(hist)} destinação(ões) registrada(s) em fonte oficial nos últimos 5 anos"}
    sinais = []
    if gife: sinais.append("registrada em fonte GIFE (a confirmar)")
    if site and site.get("sinais", {}).get("instituto_fundacao"): sinais.append("instituto/fundação no site")
    if site and site.get("sinais", {}).get("patrocinio"): sinais.append("patrocínio anunciado no site")
    if site and site.get("sinais", {}).get("edital"): sinais.append("edital/chamada no site")
    if lucro["classe"] in ("confirmado", "altamente_provavel"): sinais.append("Lucro Real (destinação incentivada possível)")
    n = len(sinais)
    if elegivel is False:
        return {"classe": "fora_das_regras", "probabilidade": "baixa", "base": "inelegível pelas regras do titular", "sinais": sinais}
    if n >= 3: return {"classe": "potencial_alto", "probabilidade": "alta", "base": "; ".join(sinais), "sinais": sinais}
    if n >= 1: return {"classe": "potencial_medio", "probabilidade": "média", "base": "; ".join(sinais), "sinais": sinais}
    return {"classe": "potencial_baixo", "probabilidade": "baixa", "base": "sem sinal público de investimento social; abordar por doação direta", "sinais": []}


def _slug(s: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:70] or "empresa"


def run_por_ano(uf: str = "GO") -> dict:
    """Pesquisa de 5 anos, UM ANO POR VEZ: o próximo só começa quando o anterior
    está concluído. Cada ano: lista do ICMS do ano → cadastros (25/saída) →
    destinações do ano (SALIC) → site institucional (15/saída) → pasta na
    Biblioteca (empresas/<uf>/<ano>/<empresa>/ficha.json)."""
    cfg = _cfg(); anos = cfg["pesquisa_por_ano"]["anos"]
    cur_p = ROOT / "estado/empresas_cursor.json"
    cur = load_json(cur_p) if cur_p.exists() else {}
    c = cur.setdefault(uf, {"ano_atual": anos[0], "concluidos": [], "eventos": []})
    coletar_maiores_contribuintes(uf); coletar_gife()
    lista = load_json(PASTA / uf.lower() / "contribuintes_icms.json")
    gife = load_json(PASTA / "gife_associados.json").get("associados", []) if (PASTA / "gife_associados.json").exists() else []
    ano = c["ano_atual"]
    bloco = lista.get("anos", {}).get(str(ano))
    rel = {"uf": uf, "ano": ano, "em": now_iso()}
    if not bloco:
        # sem lista para o ano: tenta o mais próximo já lido; se nada, registra e para
        disponiveis = sorted(lista.get("anos", {}))
        rel["situacao"] = f"lista do ICMS de {ano} ainda não obtida (anos lidos: {disponiveis or 'nenhum'})"
        if not disponiveis:
            c["eventos"] = (c["eventos"] or [])[-40:] + [rel]; write_json(cur_p, cur); return rel
        bloco = lista["anos"][disponiveis[-1]]; rel["lista_usada"] = disponiveis[-1]
    pasta_ano = BIB / uf.lower() / str(ano); pasta_ano.mkdir(parents=True, exist_ok=True)
    n_cad = n_site = 0; feitos = 0
    for it in bloco.get("empresas", []):
        slug = _slug(it["nome"]); fp = pasta_ano / slug / "ficha.json"
        ficha = load_json(fp) if fp.exists() else {"ano": ano, "uf": uf, "nome_lista": it["nome"], "cnpj": it.get("cnpj"), "icms_posicao": it.get("posicao"), "icms_valor_texto": it.get("icms_valor_texto")}
        if it.get("cnpj") and not ficha.get("cadastro") and n_cad < cfg["pesquisa_por_ano"]["por_saida_cadastros"]:
            ficha["cadastro"] = cadastro_cnpj(it["cnpj"]); n_cad += 1
            if ficha["cadastro"]:
                todas = destinacoes_rouanet(it["cnpj"]).get("itens", [])
                ficha["destinacoes_ano"] = [h for h in todas if str(h.get("ano")) == str(ano)]
                ficha["destinacoes_5_anos"] = todas
        if ficha.get("cadastro") and "site" not in ficha and n_site < cfg["pesquisa_por_ano"]["por_saida_sites"]:
            ficha["site"] = varrer_site(ficha["cadastro"]); n_site += 1
        cad = ficha.get("cadastro") or {}; hist = ficha.get("destinacoes_5_anos", [])
        ficha["gife"] = gife_casa(cad.get("razao_social") or it["nome"], cad.get("nome_fantasia"), gife)
        ficha["lucro_real"] = classificar_lucro_real(cad, hist)
        eleg = None; motivos = []
        if cad:
            eleg = True
            if not cad.get("matriz"): eleg = False; motivos.append("não é matriz")
            if (cad.get("situacao") or "").upper() not in ("ATIVA", "02", "2"): eleg = False; motivos.append(f"situação {cad.get('situacao')}")
            if (cad.get("capital_social") or 0) <= cfg["regras_do_titular"]["capital_social_minimo_exclusivo"]: eleg = False; motivos.append("capital ≤ R$ 10 mi")
        ficha["elegivel"] = eleg; ficha["motivos"] = motivos
        ficha["area_potencial"] = area_potencial(cad)
        ficha["predicao"] = predicao(ficha["lucro_real"], hist, ficha.get("site"), ficha["gife"], eleg)
        sc = score_empresa(cad, hist, ficha["lucro_real"], {"compatibilidade": bool(hist), "instituto_fundacao": bool(ficha["gife"]) or bool((ficha.get("site") or {}).get("sinais", {}).get("instituto_fundacao")),
                                                             "esg": "moderado" if (ficha.get("site") or {}).get("sinais", {}).get("esg") else None,
                                                             "atuacao_social": bool((ficha.get("site") or {}).get("sinais", {}).get("patrocinio"))})
        ficha["score"] = sc["score"]; ficha["classe"] = sc["classe"]; ficha["memoria_score"] = sc["memoria"]
        ficha["atualizado_em"] = now_iso()
        write_json(fp, ficha)
        if (not it.get("cnpj")) or (ficha.get("cadastro") is not None and "site" in ficha) or ficha.get("cadastro") is None and it.get("cnpj") and n_cad >= cfg["pesquisa_por_ano"]["por_saida_cadastros"] and fp.exists():
            pass
        if (not it.get("cnpj")) or ("cadastro" in ficha and ("site" in ficha or not ficha.get("cadastro"))):
            feitos += 1
    total = len(bloco.get("empresas", []))
    rel.update({"empresas_no_ano": total, "concluidas": feitos, "cadastros_nesta_saida": n_cad, "sites_nesta_saida": n_site})
    if total and feitos >= total:
        c["concluidos"].append(ano)
        prox = [a for a in anos if a not in c["concluidos"]]
        c["ano_atual"] = prox[0] if prox else ano
        rel["situacao"] = f"ano {ano} concluído; próximo: {c['ano_atual'] if prox else 'todos concluídos'}"
    else:
        rel["situacao"] = f"ano {ano} em curso: {feitos}/{total} empresas concluídas"
    c["eventos"] = (c["eventos"] or [])[-40:] + [rel]
    write_json(cur_p, cur)
    # índice do ano e análise preditiva consolidada
    fichas = [load_json(f) for f in sorted(pasta_ano.glob("*/ficha.json"))]
    ja = [f for f in fichas if f.get("predicao", {}).get("classe") == "ja_doou"]
    alto = [f for f in fichas if f.get("predicao", {}).get("classe") == "potencial_alto"]
    medio = [f for f in fichas if f.get("predicao", {}).get("classe") == "potencial_medio"]
    write_json(pasta_ano / "indice.json", {"uf": uf, "ano": ano, "gerado_em": now_iso(), "total": len(fichas),
        "ja_doaram": [{"nome": f.get("cadastro", {}).get("razao_social") or f["nome_lista"], "cnpj": f.get("cnpj"), "destinacoes": len(f.get("destinacoes_5_anos", [])), "score": f.get("score")} for f in ja],
        "potencial_alto": [{"nome": f.get("cadastro", {}).get("razao_social") or f["nome_lista"], "cnpj": f.get("cnpj"), "sinais": f["predicao"].get("sinais"), "score": f.get("score")} for f in alto],
        "potencial_medio": len(medio), "areas_potenciais": _conta_areas(fichas)})
    write_json(BIB / uf.lower() / "analise_preditiva.json", _preditiva(uf, anos, cfg))
    return rel


def _conta_areas(fichas):
    c = {}
    for f in fichas:
        for a in (f.get("area_potencial") or {}).get("areas", []):
            c[a] = c.get(a, 0) + 1
    return dict(sorted(c.items(), key=lambda kv: -kv[1]))


def _preditiva(uf, anos, cfg) -> dict:
    """Consolida os anos: quem já doou (fonte oficial) × quem tem potencial, por área."""
    por_cnpj = {}
    for ano in anos:
        for fp in (BIB / uf.lower() / str(ano)).glob("*/ficha.json"):
            f = load_json(fp); k = so_digitos(f.get("cnpj") or "") or _slug(f["nome_lista"])
            e = por_cnpj.setdefault(k, {"nome": (f.get("cadastro") or {}).get("razao_social") or f["nome_lista"], "cnpj": f.get("cnpj"), "anos_na_lista": [],
                                        "destinacoes": [], "predicao": None, "score": 0, "area_potencial": f.get("area_potencial"), "lucro_real": f.get("lucro_real", {}).get("classe")})
            e["anos_na_lista"].append(ano); e["destinacoes"] = f.get("destinacoes_5_anos") or e["destinacoes"]
            e["predicao"] = f.get("predicao") or e["predicao"]; e["score"] = max(e["score"], f.get("score") or 0)
    lst = list(por_cnpj.values())
    return {"uf": uf, "gerado_em": now_iso(), "empresas": len(lst),
            "ja_doaram": sorted([e for e in lst if (e["predicao"] or {}).get("classe") == "ja_doou"], key=lambda e: -e["score"]),
            "potencial_alto": sorted([e for e in lst if (e["predicao"] or {}).get("classe") == "potencial_alto"], key=lambda e: -e["score"]),
            "potencial_medio": sorted([e for e in lst if (e["predicao"] or {}).get("classe") == "potencial_medio"], key=lambda e: -e["score"])[:60],
            "recorrentes": sorted([e for e in lst if len(e["anos_na_lista"]) >= 3], key=lambda e: -len(e["anos_na_lista"]))[:60],
            "parametros": {"ja_doou": "destinação registrada em fonte oficial (SALIC/LIE/PRONON) nos últimos 5 anos",
                           "potencial_alto": "≥3 sinais: GIFE, instituto/fundação, patrocínio ou edital no site, Lucro Real",
                           "potencial_medio": "1–2 sinais", "potencial_baixo": "nenhum sinal público", "fora_das_regras": "inelegível (filial, inativa, capital ≤ 10 mi)"}}


# ───────────────────────── 4c. BASE AGREGÁVEL (um registro por CNPJ) e REGIME SEMANAL ─────────────────────────
BASE = PASTA / "base_empresas.jsonl.gz"     # compacto; um registro por CNPJ; anos como deltas
PARC_RX = re.compile(r"parceir|apoiad|patrocin|mantenedor|colaborador|doador|investidor social|amig[oa]s d[ao]", re.I)
EMPRESA_RX = re.compile(r"\b([A-ZÀ-Ú][A-Za-zÀ-ú0-9&\.\-]{2,}(?:\s+(?:[A-ZÀ-Ú][A-Za-zÀ-ú0-9&\.\-]{1,}|d[aeo]s?|e|&)){0,5}\s+(?:S\.?A\.?|S/A|LTDA\.?|Ltda\.?|Eireli|Holding|Group|Grupo|Cia\.?|Companhia|Banco|Instituto|Funda[çc][ãa]o))\b")


def carregar_base() -> dict[str, dict]:
    import gzip
    if not BASE.exists():
        return {}
    with gzip.open(BASE, "rt", encoding="utf-8") as gz:
        return {r["chave"]: r for r in (json.loads(l) for l in gz if l.strip())}


def salvar_base(base: dict[str, dict]) -> dict:
    import gzip
    BASE.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(BASE, "wt", encoding="utf-8", compresslevel=6) as gz:
        for k in sorted(base):
            gz.write(json.dumps(base[k], ensure_ascii=False, separators=(",", ":")) + "\n")
    return {"empresas": len(base), "kb": round(BASE.stat().st_size / 1024, 1)}


def _chave(cnpj: str | None, nome: str) -> str:
    return so_digitos(cnpj) if cnpj and len(so_digitos(cnpj)) == 14 else "n:" + re.sub(r"\W+", "", (nome or "").upper())[:60]


def agregar(base: dict, chave: str, nome: str, cnpj: str | None, ano: int | None, **campos) -> dict:
    """Agrega sem duplicar: o núcleo da empresa uma vez; por ano só o delta
    (posição no ICMS, destinações do ano, sinais do site)."""
    e = base.setdefault(chave, {"chave": chave, "nome": nome, "cnpj": cnpj, "criado_em": now_iso(), "anos": {}, "origens": []})
    if cnpj and not e.get("cnpj"):
        e["cnpj"] = cnpj
    for k in ("origem",):
        if campos.get(k) and campos[k] not in e["origens"]:
            e["origens"].append(campos[k])
    for k in ("cadastro", "lucro_real", "elegivel", "motivos", "area_potencial", "gife", "site", "parcerias", "score", "classe", "memoria_score", "predicao", "prioridade_previa"):
        if k in campos and campos[k] is not None:
            e[k] = campos[k]
    if ano:
        a = e["anos"].setdefault(str(ano), {})
        for k in ("icms_posicao", "icms_valor_texto", "destinacoes", "sinais_site"):
            if k in campos and campos[k] is not None:
                a[k] = campos[k]
    e["atualizado_em"] = now_iso()
    return e


def varrer_parcerias(uf: str, base: dict, limite_paginas: int = 30) -> dict:
    """Procura, em sites de associações do estado e de entidades empresariais
    (Sebrae, FIEG, ACIEG, Fecomércio, CDL, Adial), declarações de parceria/apoio/
    patrocínio e nomes de empresas. Cada achado traz a URL. Também alimenta o
    conjunto de empresas 'relevantes no estado' para escolher as novas."""
    est = _cfg()["estados"][uf]["parcerias_e_relevancia"]
    urls = [(x["nome"], x["url"], x["tipo"]) for x in est["entidades_empresariais"]]
    # sites de OSCs do estado presentes na base de oportunidades (plataformas/portais, não diários)
    try:
        from .nucleo import carregar_oportunidades
        vistos = set()
        for o in carregar_oportunidades().values():
            u = o.get("url") or ""
            if o.get("uf") == uf and u.startswith("https://") and not re.search(r"querido|pncp|\.gov\.br|\.jus\.br|\.leg\.br|\.mp\.br|in\.gov", u):
                dom = re.sub(r"^https://(www\.)?", "", u).split("/")[0]
                if dom not in vistos and len(vistos) < 40:
                    vistos.add(dom); urls.append((o.get("fonte_nome") or dom, "https://" + dom, "osc"))
    except Exception:
        pass
    destino = PASTA / uf.lower() / "parcerias_declaradas.json"
    atual = load_json(destino) if destino.exists() else {"uf": uf, "achados": [], "relevantes": [], "leituras": []}
    achados, relevantes, lidas = [], {}, 0
    for nome, url, tipo in urls:
        paginas = [url] + ([url.rstrip("/") + pth for pth in est["associacoes_do_terceiro_setor"]["paginas"]] if tipo == "osc" else [url.rstrip("/") + "/associados", url.rstrip("/") + "/parceiros"])
        for pg in paginas[:4]:
            if lidas >= limite_paginas:
                break
            try:
                html = _get(pg, timeout=15); lidas += 1
                txt = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S)
                txt = re.sub(r"<[^>]+>", " ", txt); txt = re.sub(r"\s+", " ", txt)
                for m in EMPRESA_RX.finditer(txt):
                    emp = m.group(1).strip()
                    ctx = txt[max(0, m.start() - 120): m.end() + 60]
                    if PARC_RX.search(ctx):
                        achados.append({"empresa": emp, "declarante": nome, "tipo_declarante": tipo, "url": pg, "trecho": ctx.strip()[:220], "em": now_iso()})
                    relevantes[emp.upper()] = relevantes.get(emp.upper(), 0) + 1
            except Exception:
                continue
            time.sleep(0.4)
    if achados or relevantes:
        atual["achados"] = (atual.get("achados") or [])[-400:] + achados
        rel = {r["nome"].upper(): r for r in atual.get("relevantes", [])}
        for n, c in relevantes.items():
            rel.setdefault(n.upper(), {"nome": n, "mencoes": 0})["mencoes"] += c
        atual["relevantes"] = sorted(rel.values(), key=lambda r: -r["mencoes"])[:300]
    atual["leituras"] = (atual.get("leituras") or [])[-20:] + [{"em": now_iso(), "paginas_lidas": lidas, "achados": len(achados), "fontes": len(urls)}]
    write_json(destino, atual)
    # cruza com a base: parceria declarada entra na empresa
    for a in achados:
        for k, e in base.items():
            if _toks_nome(a["empresa"]) and len(_toks_nome(a["empresa"]) & _toks_nome(e["nome"])) >= 2:
                e.setdefault("parcerias", [])
                if not any(p["url"] == a["url"] and p["declarante"] == a["declarante"] for p in e["parcerias"]):
                    e["parcerias"].append({k2: a[k2] for k2 in ("declarante", "tipo_declarante", "url", "trecho", "em")})
    return {"paginas_lidas": lidas, "achados": len(achados), "relevantes": len(atual["relevantes"])}


def _toks_nome(s: str) -> set:
    return {t for t in re.findall(r"[a-zà-ú0-9]{4,}", (s or "").lower()) if t not in ("ltda", "grupo", "brasil", "holding", "companhia", "instituto", "fundação", "fundacao")}


def prioridade_previa(nome: str, cnpj: str | None, icms_pos: int | None, gife: list, parcerias: dict, cad: dict | None) -> dict:
    """Pontuação prévia para ESCOLHER as novas da semana — por potencial de
    captação e apoio ao terceiro setor, nunca ao acaso."""
    pts, por = 0, []
    if icms_pos:
        v = 30 if icms_pos <= 20 else 22 if icms_pos <= 50 else 15 if icms_pos <= 100 else 8
        pts += v; por.append(f"{icms_pos}º no ICMS +{v}")
    if gife_casa(nome, None, gife):
        pts += 15; por.append("registrada em fonte GIFE (correspondência por nome, a confirmar) +15")
    ach = [a for a in parcerias.get("achados", []) if len(_toks_nome(a["empresa"]) & _toks_nome(nome)) >= 2]
    if ach:
        pts += 20; por.append(f"parceria declarada por {ach[0]['declarante']} +20")
    rel = [r for r in parcerias.get("relevantes", []) if len(_toks_nome(r["nome"]) & _toks_nome(nome)) >= 2]
    if rel:
        pts += 10; por.append("citada por Sebrae/entidades empresariais +10")
    if cad:
        ap = area_potencial(cad)
        if ap["cnae_divisao"] in ("64", "65", "47", "10", "46", "35", "21", "86"):
            pts += 10; por.append("setor com afinidade com o terceiro setor +10")
        if (cad.get("capital_social") or 0) > 10_000_000:
            pts += 5; por.append("capital > R$ 10 mi +5")
    return {"pontos": pts, "por": por}


def run_semanal(uf: str = "GO", minimo_novas: int | None = None) -> dict:
    """Domingo: (1) reavalia toda a base; (2) agrega ≥5 novas por potencial, com 5 anos de histórico."""
    cfg = _cfg(); minimo_novas = minimo_novas or cfg["semanal"]["minimo_novas_por_semana"]
    anos = cfg["pesquisa_por_ano"]["anos"]
    base = carregar_base()
    col = coletar_maiores_contribuintes(uf); coletar_gife()
    lista = load_json(PASTA / uf.lower() / "contribuintes_icms.json")
    gife = load_json(PASTA / "gife_associados.json").get("associados", []) if (PASTA / "gife_associados.json").exists() else []
    parc = varrer_parcerias(uf, base)
    parcerias = load_json(PASTA / uf.lower() / "parcerias_declaradas.json")
    rel = {"uf": uf, "em": now_iso(), "base_antes": len(base), "leitura_icms": col["leitura"], "parcerias": parc}
    # (1) REAVALIAÇÃO PERMANENTE da base
    reav = 0
    for k, e in list(base.items()):
        if e.get("cnpj"):
            cad = cadastro_cnpj(e["cnpj"]) or e.get("cadastro")       # cache de 90 dias: só consulta se expirou
            hist = destinacoes_rouanet(e["cnpj"]).get("itens", []) if cad else []
            # SALIC: força atualização semanal do cache
            (PASTA / "destinacoes" / f"{so_digitos(e['cnpj'])}_rouanet.json").unlink(missing_ok=True)
            hist = destinacoes_rouanet(e["cnpj"]).get("itens", []) if cad else hist
            site = varrer_site(cad) if cad and (not e.get("site") or (e["site"].get("em", "") < (date.today() - timedelta(days=30)).isoformat())) else e.get("site")
            lucro = classificar_lucro_real(cad or {}, hist)
            eleg, motivos = _elegibilidade(cad, cfg)
            g = gife_casa((cad or {}).get("razao_social") or e["nome"], (cad or {}).get("nome_fantasia"), gife)
            sc = score_empresa(cad or {}, hist, lucro, {"compatibilidade": bool(hist), "instituto_fundacao": bool(g), "esg": "moderado" if (site or {}).get("sinais", {}).get("esg") else None,
                                                        "atuacao_social": bool((site or {}).get("sinais", {}).get("patrocinio")) or bool(e.get("parcerias")), "doacoes": bool(e.get("parcerias"))})
            for h in hist:
                if h.get("ano"):
                    agregar(base, k, e["nome"], e["cnpj"], int(str(h["ano"])[:4]) if str(h["ano"])[:4].isdigit() else None,
                            destinacoes=[x for x in hist if str(x.get("ano")) == str(h["ano"])])
            agregar(base, k, (cad or {}).get("razao_social") or e["nome"], e["cnpj"], None, cadastro=cad, lucro_real=lucro, elegivel=eleg, motivos=motivos,
                    area_potencial=area_potencial(cad), gife=g, site=site, score=sc["score"], classe=sc["classe"], memoria_score=sc["memoria"],
                    predicao=predicao(lucro, hist, site, g, eleg))
            reav += 1
    rel["reavaliadas"] = reav
    # (2) NOVAS DA SEMANA — por potencial, nunca ao acaso
    candidatos = {}
    for ano, bloco in sorted(lista.get("anos", {}).items()):
        for it in bloco.get("empresas", []):
            k = _chave(it.get("cnpj"), it["nome"])
            if k in base:
                continue
            c = candidatos.setdefault(k, {"nome": it["nome"], "cnpj": it.get("cnpj"), "icms": {}, "origem": "maiores contribuintes ICMS"})
            c["icms"][ano] = it.get("posicao")
    for g in gife:
        k = _chave(None, g["nome"])
        if k not in base and not any(len(_toks_nome(c["nome"]) & _toks_nome(g["nome"])) >= 2 for c in candidatos.values()):
            candidatos.setdefault(k, {"nome": g["nome"], "cnpj": None, "icms": {}, "origem": "GIFE"})
    for r in parcerias.get("relevantes", [])[:100]:
        k = _chave(None, r["nome"])
        if k not in base and not any(len(_toks_nome(c["nome"]) & _toks_nome(r["nome"])) >= 2 for c in candidatos.values()):
            candidatos.setdefault(k, {"nome": r["nome"], "cnpj": None, "icms": {}, "origem": "Sebrae/entidades empresariais"})
    for k, c in candidatos.items():
        pos = min((p for p in c["icms"].values() if p), default=None)
        c["prioridade"] = prioridade_previa(c["nome"], c["cnpj"], pos, gife, parcerias, None)
    ordem = sorted(candidatos.values(), key=lambda c: -c["prioridade"]["pontos"])
    novas = 0
    for c in ordem:
        if novas >= minimo_novas:
            break
        k = _chave(c["cnpj"], c["nome"])
        cad = cadastro_cnpj(c["cnpj"]) if c.get("cnpj") else None
        hist = destinacoes_rouanet(c["cnpj"]).get("itens", []) if cad else []
        site = varrer_site(cad) if cad else None
        lucro = classificar_lucro_real(cad or {}, hist); eleg, motivos = _elegibilidade(cad, cfg)
        g = gife_casa((cad or {}).get("razao_social") or c["nome"], (cad or {}).get("nome_fantasia"), gife)
        sc = score_empresa(cad or {}, hist, lucro, {"compatibilidade": bool(hist), "instituto_fundacao": bool(g), "atuacao_social": bool((site or {}).get("sinais", {}).get("patrocinio"))})
        for ano, pos in c["icms"].items():
            agregar(base, k, c["nome"], c["cnpj"], int(ano), icms_posicao=pos, origem=c["origem"])
        for h in hist:
            a = str(h.get("ano") or "")[:4]
            if a.isdigit():
                agregar(base, k, c["nome"], c["cnpj"], int(a), destinacoes=[x for x in hist if str(x.get("ano") or "")[:4] == a])
        agregar(base, k, (cad or {}).get("razao_social") or c["nome"], c["cnpj"], None, origem=c["origem"], cadastro=cad, lucro_real=lucro, elegivel=eleg, motivos=motivos,
                area_potencial=area_potencial(cad), gife=g, site=site, score=sc["score"], classe=sc["classe"], memoria_score=sc["memoria"],
                predicao=predicao(lucro, hist, site, g, eleg), prioridade_previa=c["prioridade"])
        novas += 1
    rel["novas_agregadas"] = novas; rel["candidatos_restantes"] = max(0, len(ordem) - novas)
    rel["top_candidatos_proxima_semana"] = [{"nome": c["nome"], "pontos": c["prioridade"]["pontos"], "por": c["prioridade"]["por"]} for c in ordem[novas:novas + 5]]
    rel["base"] = salvar_base(base)
    # Biblioteca: pastas por ano com o delta de cada empresa + índice e preditiva
    for k, e in base.items():
        for ano, delta in e.get("anos", {}).items():
            pasta = BIB / uf.lower() / ano / _slug(e["nome"]); pasta.mkdir(parents=True, exist_ok=True)
            write_json(pasta / "ano.json", {"chave": k, "nome": e["nome"], "cnpj": e.get("cnpj"), "ano": ano, **delta, "ver_registro_completo": "dados/empresas/base_empresas.jsonl.gz"})
    write_json(BIB / uf.lower() / "analise_preditiva.json", _preditiva_base(uf, base))
    write_json(BIB / uf.lower() / f"{uf.lower()}.json", _saida_painel(uf, base, lista, col))
    (ROOT / "estado/empresas_semanal.jsonl").parent.mkdir(parents=True, exist_ok=True)
    with (ROOT / "estado/empresas_semanal.jsonl").open("a", encoding="utf-8") as h:
        h.write(json.dumps({k2: v for k2, v in rel.items() if k2 != "leitura_icms"}, ensure_ascii=False) + "\n")
    return rel


def _elegibilidade(cad, cfg):
    if not cad:
        return None, []
    eleg, motivos = True, []
    if not cad.get("matriz"): eleg = False; motivos.append("não é matriz")
    if (cad.get("situacao") or "").upper() not in ("ATIVA", "02", "2"): eleg = False; motivos.append(f"situação {cad.get('situacao')}")
    if (cad.get("capital_social") or 0) <= cfg["regras_do_titular"]["capital_social_minimo_exclusivo"]: eleg = False; motivos.append("capital ≤ R$ 10 mi")
    return eleg, motivos


def _preditiva_base(uf, base):
    lst = list(base.values())
    f = lambda cl: sorted([{"nome": e["nome"], "cnpj": e.get("cnpj"), "score": e.get("score", 0), "anos": sorted(e.get("anos", {})), "predicao": e.get("predicao"), "area_potencial": e.get("area_potencial"), "parcerias": len(e.get("parcerias", []))}
                           for e in lst if (e.get("predicao") or {}).get("classe") == cl], key=lambda x: -x["score"])
    return {"uf": uf, "gerado_em": now_iso(), "empresas": len(lst), "ja_doaram": f("ja_doou"), "potencial_alto": f("potencial_alto"), "potencial_medio": f("potencial_medio")[:80],
            "com_parceria_declarada": sorted([{"nome": e["nome"], "parcerias": e["parcerias"]} for e in lst if e.get("parcerias")], key=lambda x: -len(x["parcerias"]))[:80],
            "areas_potenciais": _conta_areas(lst)}


def _saida_painel(uf, base, lista, col):
    emps = []
    for k, e in base.items():
        cad = e.get("cadastro") or {}; anos = e.get("anos", {})
        icms = {a: {"posicao": d.get("icms_posicao"), "valor_texto": d.get("icms_valor_texto")} for a, d in anos.items() if "icms_posicao" in d}
        hist = [x for a, d in anos.items() for x in d.get("destinacoes", [])]
        rec = sorted(icms.items())[-1][1] if icms else {}
        emps.append({"id": k, "uf": uf, "nome": e["nome"], "nome_fantasia": cad.get("nome_fantasia"), "cnpj": e.get("cnpj"), "municipio": cad.get("municipio"), "cnae": cad.get("cnae_principal"),
                     "capital_social": cad.get("capital_social"), "porte": cad.get("porte"), "matriz": cad.get("matriz"), "situacao": cad.get("situacao"), "abertura": cad.get("abertura"),
                     "icms": icms, "icms_posicao_recente": rec.get("posicao"), "icms_valor_recente": rec.get("valor_texto"),
                     "irpj": "não divulgado publicamente (sigilo fiscal)", "lucro_real": e.get("lucro_real") or {"classe": "nao_confirmado", "motivo": "cadastro não obtido"},
                     "destinacoes_5_anos": hist, "potencial_destinacao": potencial_destinacao(hist, e.get("lucro_real") or {"classe": "nao_confirmado"}),
                     "score": e.get("score", 0), "classe": e.get("classe", "Prospecção Secundária"), "memoria_score": e.get("memoria_score", []),
                     "elegivel": e.get("elegivel"), "motivos_inelegibilidade": e.get("motivos", []), "cadastro_obtido": bool(cad), "qsa": cad.get("qsa", [])[:12],
                     "predicao": e.get("predicao"), "area_potencial": e.get("area_potencial"), "parcerias": e.get("parcerias", []), "gife": e.get("gife"), "origens": e.get("origens", []),
                     "fontes": [{"tipo": "maiores contribuintes ICMS", "url": lista.get("url")}] + ([{"tipo": "cadastro RFB (espelho público)", "url": f"https://minhareceita.org/{so_digitos(e['cnpj'])}"}] if cad and e.get("cnpj") else [])
                              + ([{"tipo": "SALIC/MinC", "url": "https://salic.cultura.gov.br"}] if hist else []) + [{"tipo": "parceria declarada", "url": p["url"]} for p in e.get("parcerias", [])[:3]]})
    emps.sort(key=lambda x: (-(x["score"]), x["icms_posicao_recente"] or 9999))
    return {"uf": uf, "gerado_em": now_iso(), "fonte_icms": lista.get("fonte"), "anos_lidos": sorted(lista.get("anos", {})), "ultima_leitura": col["leitura"],
            "total": len(emps), "com_cadastro": sum(1 for x in emps if x["cadastro_obtido"]), "elegiveis": sum(1 for x in emps if x["elegivel"]), "empresas": emps}


# ───────────────────────── 5. saída ─────────────────────────
def run(uf: str | None = None, limite_cadastros: int | None = None) -> dict:
    cfg = _cfg()
    ativos = [u for u, e in cfg["estados"].items() if e.get("ativo")] if not uf else [uf]
    resumo = {"executado_em": now_iso(), "estados": {}}
    for u in ativos:
        col = coletar_maiores_contribuintes(u)
        lista = load_json(PASTA / u.lower() / "contribuintes_icms.json")
        # consolida empresas de todos os anos (identidade por CNPJ ou nome)
        emp: dict[str, dict] = {}
        for ano, bloco in sorted(lista.get("anos", {}).items()):
            for it in bloco.get("empresas", []):
                k = so_digitos(it["cnpj"]) if it.get("cnpj") else re.sub(r"\W+", "", it["nome"].upper())
                e = emp.setdefault(k, {"nome_lista": it["nome"], "cnpj": it.get("cnpj"), "icms": {}, "uf": u})
                e["icms"][ano] = {"posicao": it.get("posicao"), "valor_texto": it.get("icms_valor_texto")}
        # enriquecimento por saída (rate limit)
        n = 0; cap_saida = limite_cadastros if limite_cadastros is not None else cfg["cadastro"]["por_saida"]
        saida = []
        for k, e in emp.items():
            cad = None; hist = []
            if e.get("cnpj") and n < cap_saida:
                cad = cadastro_cnpj(e["cnpj"]); n += 1
                if cad:
                    hist = destinacoes_rouanet(e["cnpj"]).get("itens", [])
            elif e.get("cnpj"):
                c = PASTA / "cadastro" / f"{so_digitos(e['cnpj'])}.json"
                cad = load_json(c) if c.exists() else None
                r = PASTA / "destinacoes" / f"{so_digitos(e['cnpj'])}_rouanet.json"
                hist = load_json(r).get("itens", []) if r.exists() else []
            elegivel, motivos = True, []
            if cad:
                if not cad.get("matriz"):
                    elegivel = False; motivos.append("estabelecimento não é matriz")
                if (cad.get("situacao") or "").upper() not in ("ATIVA", "02", "2"):
                    elegivel = False; motivos.append(f"situação cadastral: {cad.get('situacao')}")
                if (cad.get("capital_social") or 0) <= cfg["regras_do_titular"]["capital_social_minimo_exclusivo"]:
                    elegivel = False; motivos.append("capital social não superior a R$ 10 mi")
                if (cad.get("uf") or u) != u:
                    elegivel = False; motivos.append(f"matriz em outra UF ({cad.get('uf')})")
            lucro = classificar_lucro_real(cad or {}, hist)
            sc = score_empresa(cad or {}, hist, lucro, {"compatibilidade": bool(hist)})
            saida.append({
                "id": k, "uf": u, "nome": (cad or {}).get("razao_social") or e["nome_lista"], "nome_fantasia": (cad or {}).get("nome_fantasia"),
                "cnpj": e.get("cnpj"), "municipio": (cad or {}).get("municipio"), "cnae": (cad or {}).get("cnae_principal"),
                "capital_social": (cad or {}).get("capital_social"), "porte": (cad or {}).get("porte"), "matriz": (cad or {}).get("matriz"),
                "situacao": (cad or {}).get("situacao"), "abertura": (cad or {}).get("abertura"),
                "icms": e["icms"], "icms_posicao_recente": (sorted(e["icms"].items())[-1][1].get("posicao") if e["icms"] else None),
                "icms_valor_recente": (sorted(e["icms"].items())[-1][1].get("valor_texto") if e["icms"] else None),
                "irpj": "não divulgado publicamente (sigilo fiscal)" if not (cad or {}).get("irpj_publicado") else (cad or {}).get("irpj_publicado"),
                "lucro_real": lucro, "destinacoes_5_anos": hist, "potencial_destinacao": potencial_destinacao(hist, lucro),
                "score": sc["score"], "classe": sc["classe"], "memoria_score": sc["memoria"],
                "elegivel": elegivel if cad else None, "motivos_inelegibilidade": motivos,
                "cadastro_obtido": bool(cad), "qsa": (cad or {}).get("qsa", [])[:12],
                "fontes": [{"tipo": "maiores contribuintes ICMS", "url": lista.get("url")}]
                          + ([{"tipo": "cadastro RFB (espelho público)", "url": f"https://minhareceita.org/{so_digitos(e['cnpj'])}"}] if cad else [])
                          + ([{"tipo": "SALIC/MinC", "url": "https://salic.cultura.gov.br"}] if hist else []),
            })
        saida.sort(key=lambda x: (-(x["score"]), x["icms_posicao_recente"] or 9999))
        BIB.mkdir(parents=True, exist_ok=True)
        write_json(BIB / f"{u.lower()}.json", {"uf": u, "gerado_em": now_iso(), "fonte_icms": lista.get("fonte"), "anos_lidos": sorted(lista.get("anos", {})),
                                                "ultima_leitura": col["leitura"], "total": len(saida), "com_cadastro": sum(1 for x in saida if x["cadastro_obtido"]),
                                                "elegiveis": sum(1 for x in saida if x["elegivel"]), "empresas": saida})
        resumo["estados"][u] = {"listadas": len(saida), "cadastros_consultados_nesta_saida": n, "anos": sorted(lista.get("anos", {})), "leitura": col["leitura"]}
    return resumo


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "semanal":
        print(json.dumps(run_semanal(sys.argv[2] if len(sys.argv) > 2 else "GO"), ensure_ascii=False, indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "por-ano":
        print(json.dumps(run_por_ano(sys.argv[2] if len(sys.argv) > 2 else "GO"), ensure_ascii=False, indent=2))
    else:
        print(json.dumps(run(), ensure_ascii=False, indent=2))
