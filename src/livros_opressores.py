"""MOTORES OPRESSORES = LIVROS ESPECIALIZADOS DA BIBLIOTECA (titular, 29/09).

Cada motor opressor é um LIVRO sobre UMA oportunidade: escrito com o que se sabe e atualizado a cada informação nova
(edição nova, estudo do Interceptador, prazo confirmado). Nenhum livro se mistura com outro — cada um é distinto por:
  ÁREA GEOGRÁFICA   INT (internacional) · BR (nacional) · UF (estadual) · UF/município (municipal)
  OBJETO            área temática: Cultura, Esporte, Saúde, Educação, Assistência social, Criança e adolescente, …
  TIPO DO OBJETO    Edital · Chamamento público · Prêmio · Credenciamento · Fundo · Incentivo fiscal · Doação/patrocínio
                    · Emenda · Programa contínuo · Grant internacional · Destinação judicial
  PÚBLICO           a quem se destina (OSC, artistas e produtores, crianças e adolescentes, pessoas idosas, …)
  INSCRIÇÃO         regime (anual · contínuo · eventual · sem registro), janelas por ano, mês típico, aberta agora, próxima
Nome classificado:  "GO - Cultura · Edital — <programa>"   (geografia - objeto · tipo — programa)

CURADORIA: (1) livro com edições de estados diferentes é SEPARADO — cada estado ganha o seu livro; (2) livros com a
mesma assinatura (geografia, objeto, tipo, financiador, programa) são JUNTADOS; (3) cada mudança entra no registro de
atualizações do livro. Roda no ciclo completo do mapa (monitoramento e cada pouso do Interceptador); a classificação
também roda no gerador dos motores (src/motores.py), para os motores originais.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "biblioteca_alexandria/fontes/motores.json"
LIG = ROOT / "estado/opressores.json"
UFS = "AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split()
OBJETOS = [("Emendas", r"emenda parlamentar"),
           ("Pessoa idosa", r"\bidos[oa]s?\b|envelhec|longevid|pessoa idosa"),
           ("Cultura", r"cultur|art[ií]st|\barte\b|artes|pnab|aldir|rouanet|goyazes|cinema|audiovis|m[uú]sica|teatro|dan[cç]a|patrim[oô]nio|museu|leitura|festival|circo|artesan"),
           ("Esporte", r"esport|atleta|lazer|olimp|paral[ií]mp|futebol|jogos"),
           ("Saúde", r"sa[uú]de|hospital|pronon|pronas|oncol|m[eé]dic|defici[eê]ncia|reabilita|autis"),
           ("Criança e adolescente", r"crian[cç]a|adolesc|inf[aâ]ncia|\bfia\b|juventude|jovens|\beca\b|cmdca|fmdca|conanda|socioeducativ|creche"),
           ("Assistência social", r"assist[eê]ncia social|socioassistencial|vulnerab|filantr[oó]p|pobreza|fome|alimentar|nutricional|suas\b|cras|creas|acolhimento|popula[cç][aã]o de rua|feas|fmas"),
           ("Meio ambiente", r"ambient|clima|sustent|floresta|[aá]gua|amaz[oô]n|biodivers|res[ií]duo|reciclag|energ"),
           ("Educação", r"educa|escola|ensino|alfabetiz|bolsa|capacita|forma[cç][aã]o profissional"),
           ("Direitos humanos", r"direitos humanos|mulher|g[eê]nero|racial|lgbt|ind[ií]gena|quilombol"),
           ("Desenvolvimento social", r"desenvolvimento (social|comunit)|gera[cç][aã]o de renda|empreendedor|inclus[aã]o produtiva|economia solid")]
AREA_CANON = {"cultura": "Cultura", "esporte": "Esporte", "saude": "Saúde", "educacao": "Educação", "assistencia_social": "Assistência social",
              "crianca_adolescente": "Criança e adolescente", "pessoa_idosa": "Pessoa idosa", "meio_ambiente": "Meio ambiente",
              "seguranca_alimentar": "Assistência social", "direitos_humanos": "Direitos humanos"}
TIPOS = [("Emenda", r"emenda parlamentar"), ("Prêmio", r"pr[eê]mio"), ("Credenciamento", r"credenciament"),
         ("Chamamento público", r"chamamento|termo de (colabora|fomento)|marco regulat[oó]rio|mrosc"),
         ("Incentivo fiscal", r"rouanet|incentivo (fiscal|ao esporte)|pronon|pronas|lei de incentivo|goyazes|icms|dedu[cç][aã]o"),
         ("Fundo", r"\bfundo\b|\bfia\b|fundo do idoso|fmdca|feas|fmas|fundos? (municipal|estadual)"),
         ("Destinação judicial", r"presta[cç][aã]o pecuni[aá]ria|penas? pecuni[aá]ria|transa[cç][aã]o penal|\btac\b|minist[eé]rio p[uú]blico|mpgo|mpt\b"),
         ("Doação/patrocínio", r"doa[cç][aã]o|patroc[ií]nio|patrocina|investimento social|apoio institucional"),
         ("Edital", r"edital|chamada|sele[cç][aã]o|inscri|convocat")]
TIPO_CANON = {"edital": "Edital", "fundo": "Fundo", "incentivo_fiscal": "Incentivo fiscal", "doacao_patrocinio": "Doação/patrocínio",
              "emenda": "Emenda", "destinacao_judicial": "Destinação judicial", "grant": "Grant internacional"}
PUBLICOS = [("OSC e associações", r"organiza[cç][õo]es da sociedade civil|\bosc\b|associa[cç][õo]es|entidades|ongs?\b|terceiro setor|sem fins lucrativos"),
            ("Artistas e produtores culturais", r"artist|produtor(es)? cultur|agentes culturais|coletivos"),
            ("Crianças e adolescentes", r"crian[cç]a|adolesc|juventude|jovens|socioeducativ"), ("Pessoas idosas", r"\bidos[oa]s?\b|pessoa idosa"),
            ("Pessoas com deficiência", r"defici[eê]ncia|pcd|autis"), ("Mulheres", r"mulher"),
            ("Povos e comunidades tradicionais", r"ind[ií]gena|quilombol|tradicionais|ribeirinh"),
            ("Pesquisadores e instituições de ensino", r"pesquisador|universidad|institui[cç][õo]es de ensino|cient[ií]fic"),
            ("Municípios e gestores públicos", r"munic[ií]pios|prefeituras|gestores p[uú]blicos"),
            ("Atletas e entidades esportivas", r"atleta|clube|federa[cç][aã]o esportiva")]


def _sem(t) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", str(t or "").lower()) if not unicodedata.combining(c))


def _titulos(x: dict) -> str:
    return f"{x.get('programa') or ''} " + " ".join(str(e.get("titulo") or "") for e in (x.get("historico") or [])[-5:])


def geografia(x: dict) -> dict:
    from .opressores_repositorio import internacional
    if x.get("internacional") or internacional(x):
        return {"codigo": "INT", "abrangencia": "internacional", "uf": None, "municipio": None}
    ufs = [h.get("uf") for h in (x.get("historico") or []) if h.get("uf") in UFS]
    uf = x.get("uf") if x.get("uf") in UFS else (Counter(ufs).most_common(1)[0][0] if ufs else None)
    mun = None
    m = re.search(r"(?:Prefeitura (?:Municipal )?de|Munic[ií]pio de|Di[aá]rio Oficial de|C[aâ]mara (?:Municipal )?de)\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÀ-ú']+(?:\s+(?:d[aeo]s?\s+)?[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÀ-ú']+){0,3})", _titulos(x))
    if m and not re.search(r"(?i)^goi[aá]s$|estad|outros|programa|uni[aã]o|brasil", m.group(1)):
        mun = m.group(1).strip()
    if uf:
        return {"codigo": uf, "abrangencia": "municipal" if mun else "estadual", "uf": uf, "municipio": mun}
    return {"codigo": "BR", "abrangencia": "nacional", "uf": None, "municipio": None}


def _primeiro(padroes, *fontes):
    for f in fontes:
        t = _sem(f)
        for nome, rx in padroes:
            if t and re.search(_sem(rx), t):
                return nome
    return None


def objeto(x: dict) -> str:
    # 29/09: o TÍTULO manda — "Fundo Municipal do Idoso" não é criança só porque o grupo do catálogo cita a infância
    return (_primeiro(OBJETOS, f"{x.get('programa') or ''} {x.get('orgao') or ''}", _titulos(x))
            or AREA_CANON.get(str(x.get("area_atuacao") or ""))
            or _primeiro(OBJETOS, f"{x.get('segmento') or ''} {x.get('familia') or ''}") or "Geral")


def tipo_objeto(x: dict) -> str:
    if x.get("internacional"):
        return "Grant internacional"
    t = _primeiro(TIPOS, f"{x.get('programa') or ''} {x.get('orgao') or ''}", _titulos(x))
    if t:
        return t
    if x.get("regime_prazo") == "permanente_fluxo_continuo":
        return "Programa contínuo"
    return TIPO_CANON.get(str(x.get("tipo") or ""), "Edital")


def publico(x: dict) -> list[str]:
    t = _sem(_titulos(x))
    return [n for n, rx in PUBLICOS if re.search(_sem(rx), t)] or ["OSC e associações"]


def inscricao(x: dict) -> dict:
    hoje = date.today().isoformat()
    jan = sorted({(str(h.get("fim"))[:4], h.get("inicio"), h.get("fim")) for h in (x.get("historico") or []) if h.get("fim")}, key=lambda j: str(j[2]))
    janelas = [{"ano": a, "inicio": i, "fim": f} for a, i, f in jan][-8:]
    pd = x.get("proxima_data") or {}
    if pd.get("fim") and not any(j["fim"] == pd.get("fim") for j in janelas):
        janelas.append({"ano": str(pd["fim"])[:4], "inicio": pd.get("inicio"), "fim": pd.get("fim")})
    anos = {j["ano"] for j in janelas}
    rp = x.get("regime_prazo")
    regime = ("contínuo" if rp == "permanente_fluxo_continuo" else "anual" if rp == "permanente_com_janela_anual" or len(anos) >= 2
              else "eventual" if janelas else "sem registro")
    meses = Counter(str(j["fim"])[5:7] for j in janelas if j.get("fim"))
    aberta = regime == "contínuo" or any((not j.get("inicio") or j["inicio"] <= hoje) and str(j["fim"]) >= hoje for j in janelas)
    return {"regime": regime, "janelas": janelas, "mes_tipico": meses.most_common(1)[0][0] if meses else None, "aberta_agora": aberta,
            "proxima": (x.get("previsao") or {}).get("proxima_janela")}


def _prog_curto(x: dict) -> str:
    p = re.sub(r"\s+", " ", str(x.get("programa") or x.get("id")))
    p = re.sub(r"(?i)^(di[aá]rio oficial de [^—-]+[—-]\s*)", "", p)
    # 29/09: aberturas copiadas do texto do edital não são nome ("1.1 Este Edital tem por objeto a …")
    p = re.sub(r"^\s*\d+(\.\d+)*\s*[-–.)]?\s*", "", p)
    p = re.sub(r"(?i)^(este|o presente) edital (tem por|tem como) (objeto|finalidade)( a| o)?\s*|^o objeto deste edital (é|e) (a|o)?\s*", "", p)
    p = re.sub(r"(?i)^o munic[ií]pio de ([^,]+),.*?(torna p[uú]blico|comunica|informa)?\s*(que\s+)?", r"Município de \1 — ", p)
    if len(re.findall(r"[A-ZÁÉÍÓÚÂÊÔÃÕÇ]", p)) > 0.6 * max(1, len(re.findall(r"[A-Za-zÀ-ú]", p))):
        p = p.capitalize()                                # CAIXA ALTA vira leitura normal
    p = p[:1].upper() + p[1:]
    return p[:70] + ("…" if len(p) > 70 else "")


def classificar(x: dict) -> dict:
    """Escreve (ou reescreve) as páginas de classificação do livro. Não mexe no histórico."""
    g = geografia(x); ob = objeto(x); tp = tipo_objeto(x); ins = inscricao(x)
    geo = g["codigo"] + (f"/{g['municipio']}" if g.get("municipio") else "")
    x.update({"geo": g["codigo"], "municipio": g.get("municipio"), "abrangencia": g["abrangencia"], "objeto_area": ob, "tipo_objeto": tp,
              "publico": publico(x), "regime_inscricao": ins["regime"], "aberta_agora": ins["aberta_agora"], "janelas": len(ins["janelas"]),
              "nome_classificado": f"{geo} - {ob} · {tp} — {_prog_curto(x)}"})
    x["livro"] = {"geografia": g, "objeto": ob, "tipo_do_objeto": tp, "publico": x["publico"], "inscricao": ins,
                  "edicoes": len(x.get("historico") or []), "financiador": x.get("orgao") or None, "pagina": x.get("pagina"),
                  "atualizacoes": (x.get("livro") or {}).get("atualizacoes") or []}
    return x


def _assinatura(x: dict) -> str:
    from .opressores_repositorio import chave
    return "|".join([x.get("geo") or "", x.get("municipio") or "", x.get("objeto_area") or "", x.get("tipo_objeto") or "",
                     chave(x.get("programa") or "", x.get("orgao") or "")])


def _anota(x: dict, o_que: str) -> None:
    lv = x.setdefault("livro", {}); at = lv.setdefault("atualizacoes", [])
    at.append({"em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "o_que": o_que}); lv["atualizacoes"] = at[-20:]


def curar() -> dict:
    C = json.loads(CAT.read_text(encoding="utf-8")); L = json.loads(LIG.read_text(encoding="utf-8")) if LIG.exists() else {"ligados": {}}
    ms = C.get("motores") or []; st = Counter(); novos = []
    for x in ms:                                         # 1) SEPARAR edições de estados diferentes
        por_uf = {}
        for h in x.get("historico") or []:
            por_uf.setdefault(h.get("uf") or "", []).append(h)
        ufs = [u for u in por_uf if u]
        if len(ufs) > 1:
            dom = Counter({u: len(por_uf[u]) for u in ufs}).most_common(1)[0][0]
            x["historico"] = por_uf[dom] + por_uf.get("", []); x["uf"] = dom
            for u in ufs:
                if u == dom:
                    continue
                h0 = por_uf[u]
                n = {k: v for k, v in x.items() if k not in ("historico", "livro", "atual", "proxima_data", "previsao")}
                n.update({"id": "op-" + hashlib.sha1(f"{x['id']}|{u}".encode()).hexdigest()[:12], "uf": u, "historico": h0,
                          "pagina": h0[-1].get("pagina_oficial") or x.get("pagina"), "criado_em": date.today().isoformat(),
                          "motivo_status": f"separado de {x['id']}: edições de {u} não se misturam com as de {dom}"})
                _anota(n, f"livro criado ao separar as edições de {u} do livro {x['id']}"); novos.append(n); st["separados"] += 1
            _anota(x, f"edições de outros estados ({', '.join(u for u in ufs if u != dom)}) separadas em livros próprios")
    ms += novos
    for x in ms:                                         # 2) CLASSIFICAR e registrar mudanças
        antes = (x.get("nome_classificado"), (x.get("livro") or {}).get("edicoes"))
        classificar(x)
        if antes != (x["nome_classificado"], x["livro"]["edicoes"]):
            _anota(x, "classificação escrita" if not antes[0] else ("nova edição registrada" if antes[1] != x["livro"]["edicoes"] else "classificação atualizada"))
            st["atualizados"] += 1
    lig = L.get("ligados") or {}; por_ass, fica = {}, []    # 3) JUNTAR mesma assinatura
    # 30/09: opressor PESQUISADO (12 parâmetros) é sempre o sobrevivente e nunca é absorvido por outro
    for x in sorted(ms, key=lambda y: (not y.get("parametros"), y.get("id") not in lig, -len(y.get("historico") or []))):
        a = _assinatura(x)
        if a in por_ass and x.get("tipo") == "repositorio_de_oportunidade" and not x.get("parametros"):
            alvo = por_ass[a]; ids = {h.get("id") for h in alvo.get("historico") or []}
            alvo.setdefault("historico", []).extend(h for h in x.get("historico") or [] if h.get("id") not in ids)
            classificar(alvo); _anota(alvo, f"juntado com {x['id']} (mesma geografia, objeto, tipo e programa)")
            lig.pop(x["id"], None); st["juntados"] += 1
            continue
        por_ass[a] = x; fica.append(x)
    C["motores"] = fica
    C["livros"] = {"regra": __doc__.split("CURADORIA:")[0].strip(), "em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   "por_geografia": Counter(x.get("geo") for x in fica).most_common(), "por_objeto": Counter(x.get("objeto_area") for x in fica).most_common(),
                   "por_tipo": Counter(x.get("tipo_objeto") for x in fica).most_common()}
    CAT.write_text(json.dumps(C, ensure_ascii=False, indent=1), encoding="utf-8")
    L["ligados"] = lig; LIG.write_text(json.dumps(L, ensure_ascii=False, indent=1), encoding="utf-8")
    return {**st, "livros": len(fica)}


if __name__ == "__main__":
    print(json.dumps(curar(), ensure_ascii=False, indent=1))
