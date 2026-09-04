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


def extrair_contribuintes(texto: str, ano: int | None = None) -> list[dict]:
    """Extrai linhas 'posição — nome — CNPJ — valor' de um texto (HTML ou PDF) de
    lista de maiores contribuintes. Tolerante: nome é obrigatório; CNPJ e valor
    entram quando existem."""
    saida, vistos = [], set()
    for linha in re.split(r"[\r\n]+|(?<=\))\s{2,}", texto):
        l = re.sub(r"\s+", " ", linha).strip()
        if len(l) < 6 or len(l) > 400:
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
        if re.search(r"^(pos|posi[çc][ãa]o|ranking|contribuinte|raz[ãa]o social|cnpj|valor|total|fonte|secretaria)\b", nome, re.I):
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
    print(json.dumps(run(), ensure_ascii=False, indent=2))
