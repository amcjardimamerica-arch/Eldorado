"""BIBLIOTECA DE EMPRESAS — quem destina recurso para entidades, e como chegar.

Duas listas, cada uma com as 100 melhores empresas para a A.M.C. (Goiás):

  • DESTINAÇÃO TRIBUTÁRIA — empresas que abatem imposto ao apoiar projetos
    (Rouanet/LIE/FIA/Idoso/PRONON no IRPJ do Lucro Real; Goyazes no ICMS de
    Goiás). Só interessa quem apura pelo LUCRO REAL e tem imposto a destinar.
  • PATROCÍNIO PRIVADO — empresas que patrocinam eventos, festivais, esporte e
    ações comunitárias com verba de marketing, sem benefício fiscal.

Fontes de pontuação, todas verificáveis:
  1. lista oficial dos maiores contribuintes do ICMS de Goiás (Economia-GO);
  2. base do sistema (cadastro RFB, porte, natureza, sede em Goiás);
  3. presença no GIFE (organizações de investimento social mapeadas);
  4. achados do Motor Patrocínio Privado (imprensa e eventos de Goiás);
  5. programas de investimento social conhecidos publicamente (instituto ou
     fundação própria, edital recorrente) — marcados como "a confirmar", porque
     conhecimento público não é evidência primária.

Nada aqui afirma que a empresa vai apoiar: o ranking ordena PROBABILIDADE e
diz o caminho (o que ela apoia, por onde entra o pedido, quando procurar).
"""
from __future__ import annotations

import gzip
import json
import re
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json

DESTINO = ROOT / "biblioteca_alexandria/empresas"
BASE = ROOT / "dados/empresas/base_empresas.jsonl.gz"

# ── Programas de investimento social conhecidos publicamente (a confirmar na fonte) ──
# (nome, instituto/programa, o que apoia, via de entrada, incentivo fiscal usado)
CONHECIDAS_FISCAL = [
    ("Itaú Unibanco", "Itaú Social / Itaú Cultural", "educação, cultura, leitura", "editais próprios e Rouanet", ["Rouanet", "FIA", "LIE"]),
    ("Bradesco", "Fundação Bradesco", "educação básica e formação", "programa próprio e Rouanet", ["Rouanet", "FIA"]),
    ("Banco do Brasil", "Fundação Banco do Brasil / patrocínios BB", "tecnologia social, cultura, esporte", "editais FBB e patrocínio BB", ["Rouanet", "LIE"]),
    ("Caixa Econômica Federal", "Patrocínios Caixa", "cultura, esporte, projetos sociais", "edital anual de patrocínio", ["Rouanet", "LIE"]),
    ("Petrobras", "Petrobras Socioambiental", "socioambiental, cultura", "seleção pública anual", ["Rouanet"]),
    ("Vale", "Instituto Cultural Vale / Fundação Vale", "cultura, território, educação", "editais próprios", ["Rouanet", "LIE", "FIA"]),
    ("Ambev", "Instituto Ambev / VOA", "água, empreendedorismo, gestão de OSC", "programa VOA e editais", ["Rouanet", "FIA"]),
    ("Natura", "Instituto Natura / Natura Musical", "educação e música", "edital Natura Musical", ["Rouanet"]),
    ("Gerdau", "Instituto Gerdau", "educação e comunidades", "edital e aporte direto", ["Rouanet", "FIA", "LIE"]),
    ("Suzano", "Fundação Suzano", "educação e desenvolvimento local", "programa próprio", ["Rouanet", "FIA"]),
    ("Klabin", "Instituto Klabin", "educação, cultura, meio ambiente", "editais locais", ["Rouanet", "LIE"]),
    ("JBS", "Fundo JBS pela Amazônia / JBS Fazer o Bem Faz Bem", "desenvolvimento local, saúde", "chamadas próprias", ["Rouanet", "PRONON", "FIA"]),
    ("BRF", "Instituto BRF", "segurança alimentar e comunidades", "editais próprios", ["FIA", "Idoso", "Rouanet"]),
    ("Raízen", "Fundação Raízen", "educação e comunidades canavieiras", "programa próprio", ["Rouanet", "LIE"]),
    ("Cargill", "Fundação Cargill", "alimentação e nutrição", "editais próprios", ["FIA", "Rouanet"]),
    ("Volkswagen", "Fundação Grupo Volkswagen", "educação e voluntariado", "editais próprios", ["Rouanet", "LIE", "FIA"]),
    ("Telefônica Vivo", "Fundação Telefônica Vivo", "educação e tecnologia", "editais próprios", ["Rouanet", "FIA"]),
    ("Santander", "Santander Universidades / Amigo de Valor", "educação e infância", "programa Amigo de Valor (FIA)", ["FIA", "Rouanet"]),
    ("Localiza", "Instituto Localiza", "mobilidade e juventude", "editais e destinação", ["FIA", "Rouanet"]),
    ("Unimed", "Institutos Unimed regionais", "saúde e prevenção", "aporte local e PRONON", ["PRONON", "FIA"]),
    ("Sicoob", "Instituto Sicoob", "cooperativismo e comunidades", "editais e destinação local", ["FIA", "Idoso", "Rouanet"]),
    ("Sicredi", "Fundação Sicredi", "educação cooperativa", "aporte local", ["FIA", "Idoso"]),
    ("CCR", "Instituto CCR", "mobilidade, cultura, cidadania", "editais próprios", ["Rouanet", "LIE", "FIA"]),
    ("Eletrobras", "Patrocínios Eletrobras", "cultura, energia, meio ambiente", "edital de patrocínio", ["Rouanet", "LIE"]),
    ("Correios", "Patrocínios Correios", "cultura e esporte", "edital de patrocínio", ["Rouanet", "LIE"]),
    ("Sabin", "Instituto Sabin", "saúde, infância, meio ambiente", "editais e destinação", ["FIA", "Idoso", "PRONON"]),
    ("Mosaic Fertilizantes", "Instituto Mosaic", "alimentação e desenvolvimento local", "editais próprios", ["FIA", "Rouanet"]),
    ("Votorantim", "Instituto Votorantim", "gestão pública e desenvolvimento local", "programa próprio", ["Rouanet", "FIA", "Idoso"]),
    ("Alcoa", "Instituto Alcoa", "educação e comunidades", "editais próprios", ["FIA", "Rouanet"]),
    ("Arcelor Mittal", "Fundação ArcelorMittal", "educação e cultura", "editais próprios", ["Rouanet", "LIE", "FIA"]),
    ("Coca-Cola Brasil", "Instituto Coca-Cola Brasil", "juventude e empregabilidade", "programa Coletivo", ["Rouanet", "FIA"]),
    ("Ipiranga", "Patrocínios Ipiranga", "cultura e mobilidade", "aporte via Rouanet", ["Rouanet"]),
    ("Braskem", "Programa social Braskem", "educação e território", "editais locais", ["Rouanet", "FIA"]),
    ("Nestlé", "Nestlé pela Criança", "nutrição e infância", "programa próprio", ["FIA", "Rouanet"]),
    ("Carrefour", "Instituto Carrefour", "combate à fome e diversidade", "editais próprios", ["FIA", "Idoso"]),
    ("Assaí", "Instituto Assaí", "segurança alimentar e pequenos negócios", "editais próprios", ["FIA", "Idoso"]),
    ("Magazine Luiza", "Fundação Magalu", "educação e diversidade", "editais próprios", ["FIA", "Rouanet"]),
    ("Renner", "Instituto Lojas Renner", "autonomia econômica de mulheres", "edital anual", ["FIA", "Rouanet"]),
    ("Riachuelo", "Instituto Guararapes", "educação e cultura", "aporte local", ["Rouanet", "FIA"]),
    ("Grupo Boticário", "Fundação Grupo Boticário", "meio ambiente e biodiversidade", "editais próprios", ["Rouanet", "FIA"]),
    ("BTG Pactual", "BTG Pactual Social", "educação e saúde", "aporte direto", ["FIA", "PRONON"]),
    ("XP", "Instituto XP", "educação financeira", "editais próprios", ["FIA", "Rouanet"]),
    ("Nubank", "Nubank Mais Perto", "educação financeira e empreendedorismo", "programa próprio", ["FIA"]),
    ("Stone", "Instituto Stone", "empreendedorismo e educação", "aporte direto", ["FIA"]),
    ("Rede D'Or", "Instituto Rede D'Or", "saúde", "PRONON e aporte", ["PRONON", "PRONAS"]),
    ("Hapvida", "Instituto Hapvida", "saúde e prevenção", "PRONON e aporte", ["PRONON"]),
    ("Dasa", "Instituto Dasa", "saúde e diagnóstico", "PRONON", ["PRONON"]),
    ("Fleury", "Instituto Fleury", "saúde", "PRONON", ["PRONON"]),
    ("Marisa", "Instituto Marisa", "mulheres e infância", "aporte direto", ["FIA"]),
    ("Grupo Mateus", "programa social próprio", "alimentação e comunidades", "aporte local", ["FIA", "Idoso"]),
]
CONHECIDAS_PATROCINIO = [
    ("Ambev", "eventos, festivais e esporte", "marketing regional e Zé Delivery"),
    ("Coca-Cola", "festivais, música e esporte", "marketing regional"),
    ("Heineken", "música e festivais", "marketing de marca"),
    ("Itaú", "festivais, corridas e cultura", "patrocínio institucional"),
    ("Bradesco", "esporte e corridas de rua", "patrocínio institucional"),
    ("Banco do Brasil", "CCBB, música e esporte", "patrocínio e Rouanet"),
    ("Caixa", "esporte olímpico e cultura", "patrocínio institucional"),
    ("Vivo", "música e tecnologia", "marketing"),
    ("Claro", "música, festivais e esporte", "marketing"),
    ("TIM", "festivais e música", "marketing"),
    ("Equatorial Energia", "eventos comunitários e cultura em Goiás", "patrocínio regional"),
    ("Saneago", "eventos e ações socioambientais em Goiás", "patrocínio regional"),
    ("Grupo Bretas / Cencosud", "eventos comunitários em Goiás", "marketing regional"),
    ("Supermercados Carrefour", "eventos e feiras", "marketing regional"),
    ("Assaí Atacadista", "feiras e eventos comunitários", "marketing regional"),
    ("Havan", "eventos e esporte regional", "marketing"),
    ("Localiza", "esporte e corridas", "marketing"),
    ("Unimed Goiânia", "corridas, esporte e saúde", "patrocínio regional"),
    ("Hospital Israelita Albert Einstein", "saúde e ciência", "patrocínio institucional"),
    ("Cervejaria Petrópolis", "festivais e eventos", "marketing"),
    ("Grupo Petrópolis", "eventos regionais", "marketing"),
    ("Coca-Cola Femsa", "eventos regionais", "marketing"),
    ("Sicoob", "eventos cooperativos e comunitários em Goiás", "patrocínio regional"),
    ("Sicredi", "eventos comunitários", "patrocínio regional"),
    ("Sebrae Goiás", "feiras, capacitação e empreendedorismo", "parceria institucional"),
    ("Fieg / Sesi / Senai Goiás", "esporte, cultura e educação em Goiás", "parceria institucional"),
    ("Sesc Goiás", "cultura, esporte e lazer", "parceria institucional"),
    ("Fecomércio Goiás", "eventos do comércio e cultura", "parceria institucional"),
    ("Grupo Jaime Câmara", "eventos culturais e mídia em Goiás", "permuta de mídia e patrocínio"),
    ("TV Anhanguera", "eventos e campanhas em Goiás", "permuta de mídia"),
    ("Rádio Sagres", "eventos e campanhas em Goiás", "permuta de mídia"),
    ("Jornal O Popular", "eventos culturais em Goiás", "permuta de mídia"),
    ("Mais Goiás", "eventos e campanhas", "permuta de mídia"),
    ("Curta Mais", "eventos culturais de Goiânia", "permuta de mídia"),
    ("Flamboyant Shopping", "eventos culturais e comunitários", "patrocínio regional"),
    ("Passeio das Águas Shopping", "eventos comunitários", "patrocínio regional"),
    ("Buriti Shopping", "eventos comunitários", "patrocínio regional"),
    ("Goiânia Shopping", "eventos culturais", "patrocínio regional"),
    ("Construtora Dinâmica", "eventos e ações de bairro em Goiânia", "patrocínio local"),
    ("Terral Empreendimentos", "eventos culturais em Goiânia", "patrocínio local"),
    ("Brasal", "eventos regionais", "marketing"),
    ("Cervejaria Ambev Goiás", "festivais goianos", "marketing regional"),
    ("Grupo Big / Atacadão", "feiras e eventos", "marketing regional"),
    ("Drogasil / RD Saúde", "saúde e campanhas comunitárias", "marketing"),
    ("Hospital do Coração Anis Rassi", "saúde e eventos", "patrocínio local"),
    ("Faculdade Estácio Goiás", "eventos culturais e educacionais", "patrocínio local"),
    ("PUC Goiás", "eventos culturais e extensão", "parceria institucional"),
    ("Unip / Unigoiás", "eventos e extensão", "parceria institucional"),
    ("Cooperativa Comigo", "eventos rurais e comunitários", "patrocínio regional"),
    ("Frigorífico Minerva", "eventos regionais", "marketing"),
]


def _base_empresas() -> list[dict]:
    if not BASE.exists():
        return []
    with gzip.open(BASE, "rt", encoding="utf-8") as gz:
        return [json.loads(l) for l in gz if l.strip()]


def _norm(s: str) -> str:
    import unicodedata
    return re.sub(r"[^a-z0-9 ]", "", unicodedata.normalize("NFKD", (s or "").lower()).encode("ascii", "ignore").decode())


def _gife() -> set[str]:
    arq = ROOT / "dados/empresas/gife_associados.json"
    if not arq.exists():
        return set()
    return {_norm(a["nome"]) for a in load_json(arq).get("associados", [])}


def _patrocinios_observados() -> dict:
    arq = ROOT / "dados/empresas/go/patrocinios.json"
    if not arq.exists():
        return {}
    saida = {}
    for a in load_json(arq).get("achados", []):
        saida.setdefault(_norm(a.get("empresa", "")), []).append({"evento": a.get("evento"), "fonte": a.get("fonte"), "url": a.get("url"), "em": a.get("em")})
    return saida


SETOR_AFINIDADE = {
    "Comunicação": (18, "mídia: patrocina eventos e troca por espaço publicitário — a via mais barata para a OSC"),
    "Comércio Varejista": (14, "varejo: marca voltada ao consumidor local, patrocina eventos de bairro e campanhas"),
    "Indústria": (12, "indústria: costuma ter Lucro Real e política de investimento social no território onde opera"),
    "Comércio Atacadista E Distribuidor": (10, "atacado: apoio pontual e doação de produto (segurança alimentar)"),
    "Combustível": (10, "combustível: Lucro Real quase certo; patrocínio esportivo e cultural"),
    "Produção Agropecuária": (8, "agro: apoio a projetos rurais e cooperativas; menos afeito a edital urbano"),
    "Prestação De Serviço": (8, "serviços: apoio institucional e voluntariado corporativo"),
    "Energia Elétrica": (16, "concessionária: obrigada a programas de eficiência e responsabilidade social no estado"),
    "Saneamento": (16, "concessionária estadual: programas socioambientais próprios"),
}
MUNICIPIOS_GO = {"Goiania", "Aparecida De Goiania", "Anapolis", "Catalao", "Itumbiara", "Senador Canedo", "Rio Verde", "Jatai",
                 "Trindade", "Luziania", "Formosa", "Caldas Novas", "Goianesia", "Mineiros", "Cristalina", "Inhumas", "Quirinopolis"}


def _mencoes_no_acervo(nomes: list[str]) -> dict:
    """Quantas vezes cada empresa aparece no acervo de 16 mil editais/atos —
    como financiadora, patrocinadora ou citada em ato de destinação."""
    try:
        from .banco import conectar
        con = conectar()
        rows = con.execute("SELECT titulo, financiador, url, data_publicacao FROM historico "
                           "WHERE data_publicacao >= date('now','-5 years') LIMIT 40000").fetchall()
    except Exception:
        return {}
    idx = {}
    chaves = {n: [x for x in _norm(n).split() if len(x) > 3][:2] for n in nomes}
    for r in rows:
        alvo = _norm((r[0] or "") + " " + (r[1] or ""))
        for n, toks in chaves.items():
            if toks and all(t in alvo for t in toks):
                d = idx.setdefault(n, {"mencoes": 0, "anos": set(), "exemplos": []})
                d["mencoes"] += 1; d["anos"].add((r[3] or "")[:4])
                if len(d["exemplos"]) < 3:
                    d["exemplos"].append({"titulo": (r[0] or "")[:90], "data": r[3], "url": r[2]})
    return {n: {**v, "anos": sorted(v["anos"])} for n, v in idx.items()}


def ranking(categoria: str) -> list[dict]:
    """RANKING REGIONAL DE GOIÁS. Base: a lista oficial dos maiores contribuintes do
    ICMS de Goiás (300 por ano), cruzada com dez sinais verificáveis. Nada nacional:
    só quem paga imposto e opera em Goiás entra."""
    base = _base_empresas(); gife = _gife(); patr = _patrocinios_observados()
    lst = ROOT / "dados/empresas/go/contribuintes_icms.json"
    anos = (load_json(lst).get("anos") or {}) if lst.exists() else {}
    emp: dict[str, dict] = {}
    for ano, bloco in sorted(anos.items()):
        for e in bloco.get("empresas", []):
            k = _norm(e["nome"])
            if not k:
                continue
            d = emp.setdefault(k, {"nome": e["nome"], "cnpj": e.get("cnpj"), "setor": e.get("setor"), "municipio": e.get("municipio_lista"), "posicoes": {}})
            d["posicoes"][ano] = e["posicao"]
            d["setor"] = d["setor"] or e.get("setor"); d["municipio"] = d["municipio"] or e.get("municipio_lista")
    # cadastro da Receita quando o motor já leu (capital, natureza, porte)
    cad = {_norm(e["nome"]): (e.get("cadastro") or {}) for e in base if e.get("cadastro")}
    mencoes = _mencoes_no_acervo([d["nome"] for d in emp.values()])
    itens = []
    for k, d in emp.items():
        pos = sorted(d["posicoes"].items())
        atual = pos[-1][1]; melhor = min(p for _, p in pos)
        pontos, sinais = 0, []
        # 1. porte tributário (posição no ICMS)
        p1 = 30 if atual <= 20 else 24 if atual <= 50 else 18 if atual <= 100 else 12 if atual <= 200 else 8
        pontos += p1; sinais.append({"sinal": "porte tributário", "pontos": p1, "evidencia": f"{atual}º maior contribuinte do ICMS de Goiás em {pos[-1][0]} (melhor posição: {melhor}º)", "fonte": "lista oficial Economia-GO"})
        # 2. recorrência na lista (estabilidade = imposto constante para destinar)
        if len(pos) >= 2:
            pontos += 10; sinais.append({"sinal": "recorrência", "pontos": 10, "evidencia": f"presente na lista em {len(pos)} anos ({', '.join(a for a, _ in pos)})", "fonte": "lista oficial Economia-GO"})
        # 3. trajetória (subiu de posição = crescimento)
        if len(pos) >= 2 and pos[-1][1] < pos[0][1]:
            pontos += 5; sinais.append({"sinal": "trajetória", "pontos": 5, "evidencia": f"subiu do {pos[0][1]}º para o {pos[-1][1]}º — faturamento e imposto crescendo", "fonte": "comparação entre anos da lista"})
        # 4. sede/operação em município de Goiás (proximidade decide patrocínio local)
        mun = (d.get("municipio") or "")
        if mun in MUNICIPIOS_GO:
            p4 = 12 if mun in ("Goiania", "Aparecida De Goiania") else 8
            pontos += p4; sinais.append({"sinal": "proximidade", "pontos": p4, "evidencia": f"estabelecimento em {mun}/GO — decisão de patrocínio costuma ser local", "fonte": "lista oficial"})
        elif "Diversos" in mun:
            pontos += 4; sinais.append({"sinal": "capilaridade", "pontos": 4, "evidencia": "vários estabelecimentos no estado — decisão pode ser regional ou nacional", "fonte": "lista oficial"})
        # 5. setor e afinidade com o terceiro setor
        af = SETOR_AFINIDADE.get(d.get("setor") or "")
        if af:
            pontos += af[0]; sinais.append({"sinal": "afinidade setorial", "pontos": af[0], "evidencia": af[1], "fonte": "setor declarado na lista oficial"})
        # 6. investimento social mapeado (GIFE)
        if any(k in g or g in k for g in gife):
            pontos += 15; sinais.append({"sinal": "investimento social mapeado", "pontos": 15, "evidencia": "organização mapeada em fonte GIFE", "fonte": "portal GIFE"})
        # 7. programa conhecido publicamente (instituto/fundação)
        conhecida = next((c for c in (CONHECIDAS_FISCAL if categoria == "destinacao_tributaria" else CONHECIDAS_PATROCINIO) if _norm(c[0]) in k or k in _norm(c[0])), None)
        if conhecida:
            pontos += 14; sinais.append({"sinal": "programa próprio", "pontos": 14, "evidencia": f"{conhecida[1]} — apoia {conhecida[2]}" if categoria == "destinacao_tributaria" else f"patrocina {conhecida[1]}", "fonte": "conhecimento público — a confirmar no site institucional"})
        # 8. patrocínio observado pelo motor na imprensa de Goiás
        obs = next((v for kk, v in patr.items() if kk and (kk in k or k in kk)), None)
        if obs:
            pontos += 16; sinais.append({"sinal": "patrocínio observado", "pontos": 16, "evidencia": f"{len(obs)} achado(s) do Motor Patrocínio Privado: " + "; ".join((o.get("evento") or "")[:50] for o in obs[:2]), "fonte": "imprensa e eventos de Goiás"})
        # 9. já endereçou edital/ato no acervo (aparece como financiador ou citada)
        men = mencoes.get(d["nome"])
        if men:
            p9 = min(14, 4 + 2 * men["mencoes"])
            pontos += p9; sinais.append({"sinal": "editais já endereçados", "pontos": p9, "evidencia": f"{men['mencoes']} ocorrência(s) no acervo ({', '.join(men['anos'])}): " + "; ".join(x["titulo"][:60] for x in men["exemplos"][:2]), "fonte": "acervo do sistema (16 mil atos)"})
        # 10. cadastro da Receita lido (capital e natureza confirmam Lucro Real provável)
        c = cad.get(k)
        if c:
            cap = c.get("capital_social") or 0
            p10 = 8 if cap and float(cap) >= 10_000_000 else 4
            pontos += p10; sinais.append({"sinal": "cadastro confirmado", "pontos": p10,
                                          "evidencia": f"CNPJ ativo, {c.get('natureza_juridica') or 'natureza a confirmar'}, capital {('R$ %s' % f'{float(cap):,.2f}').replace(',', '@').replace('.', ',').replace('@', '.') if cap else 'não informado'}",
                                          "fonte": "dados públicos do CNPJ (Receita Federal)"})
        if categoria == "destinacao_tributaria":
            condicao = "só destina quem apura pelo LUCRO REAL e tem IRPJ/CSLL devido; o ICMS destinado ao Goyazes independe do regime"
            via = (conhecida[3] if conhecida else "relações institucionais / responsabilidade social no site da empresa")
            incentivos = (conhecida[4] if conhecida else ["Goyazes (ICMS-GO)", "Rouanet", "FIA", "Idoso"])
        else:
            condicao = "verba de marketing: a proposta precisa de contrapartida de marca, público estimado e plano de mídia"
            via = (conhecida[2] if conhecida else "marketing / comunicação institucional")
            incentivos = None
        classe, leitura = _classe(min(100, pontos))
        itens.append({"nome": d["nome"], "cnpj": d.get("cnpj"), "setor": d.get("setor"), "municipio": d.get("municipio"),
                      "icms_goias": atual, "icms_melhor": melhor, "anos_na_lista": [a for a, _ in pos],
                      "pontos": min(100, pontos), "classe": classe, "leitura": leitura, "sinais": sinais,
                      "por": [f"{s['pontos']}: {s['sinal']} — {s['evidencia'][:110]}" for s in sinais],
                      "programa": (conhecida[1] if conhecida and categoria == "destinacao_tributaria" else None),
                      "apoia": (conhecida[2] if conhecida and categoria == "destinacao_tributaria" else (conhecida[1] if conhecida else None)),
                      "via_de_entrada": via, "incentivos": incentivos, "condicao": condicao,
                      "gife": any(k in g or g in k for g in gife), "observado_pelo_motor": obs or None,
                      "mencoes_acervo": men,
                      "proximo_passo": ("confirmar regime (Lucro Real) e falar com relações institucionais" if categoria == "destinacao_tributaria" and pontos >= 50
                                        else "apresentar projeto com contrapartida de marca ao marketing" if categoria != "destinacao_tributaria" and pontos >= 50
                                        else "investigar o site institucional atrás de programa social ou edital")})
    itens.sort(key=lambda x: (-x["pontos"], x["icms_goias"]))
    for i, x in enumerate(itens[:100], 1):
        x["posicao"] = i
    return itens[:100]


def _classe(p: int) -> tuple[str, str]:
    if p >= 70: return "A", "alta probabilidade: evidências múltiplas e verificáveis — abordar já"
    if p >= 50: return "B", "probabilidade média: há porte e sinais; confirmar programa e interlocutor"
    if p >= 35: return "C", "probabilidade a construir: porte compatível, sem programa identificado — investigar o site"
    return "D", "sem evidência suficiente: manter em observação"


def run() -> dict:
    DESTINO.mkdir(parents=True, exist_ok=True)
    saida = {}
    for cat, rot in (("destinacao_tributaria", "Destinação tributária (incentivo fiscal)"), ("patrocinio_privado", "Patrocínio privado (marketing)")):
        lista = ranking(cat)
        ficha = {"categoria": cat, "rotulo": rot + " — Goiás", "escopo": "regional: apenas empresas da lista oficial dos maiores contribuintes do ICMS de Goiás",
                 "gerado_em": now_iso(), "total": len(lista), "classes": {c: sum(1 for e in lista if e["classe"] == c) for c in "ABCD"},
                 "sinais": ["porte tributário (posição no ICMS-GO)", "recorrência na lista", "trajetória de posição", "proximidade (município)",
                            "afinidade setorial", "investimento social mapeado (GIFE)", "programa próprio conhecido", "patrocínio observado pelo motor",
                            "editais já endereçados (acervo)", "cadastro da Receita confirmado"],
                 "metodo": "pontuação 0–100 por dez sinais verificáveis: posição no ICMS de Goiás (lista oficial), presença em fonte GIFE, patrocínio observado pelo motor na imprensa de Goiás, "
                           "programa de investimento social conhecido publicamente (a confirmar) e mecanismos de incentivo usados. Conhecimento público é hipótese, não evidência primária.",
                 "empresas": lista}
        write_json(DESTINO / f"ranking_{cat}.json", ficha)
        write_json(ROOT / "docs/dados" / f"ranking_{cat}.json", ficha)
        saida[cat] = len(lista)
    write_json(DESTINO / "indice.json", {"gerado_em": now_iso(), "rankings": list(saida), "totais": saida,
                                         "nota": "biblioteca de empresas: quem destina recurso a entidades, por que e por onde entrar"})
    return saida


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
