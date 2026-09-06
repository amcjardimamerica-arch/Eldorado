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


def ranking(categoria: str) -> list[dict]:
    """categoria: 'destinacao_tributaria' ou 'patrocinio_privado'."""
    base = _base_empresas(); gife = _gife(); patr = _patrocinios_observados()
    icms = {}
    for e in base:
        pos = [d.get("icms_posicao") for d in (e.get("anos") or {}).values() if d.get("icms_posicao")]
        if pos:
            icms[_norm(e["nome"])] = {"posicao": min(pos), "cnpj": e.get("cnpj"), "nome": e["nome"], "anos": sorted((e.get("anos") or {}).keys())}
    # lista oficial completa dos maiores contribuintes do ICMS de Goiás (299 por ano)
    lst = ROOT / "dados/empresas/go/contribuintes_icms.json"
    if lst.exists():
        for ano, bloco in sorted((load_json(lst).get("anos") or {}).items(), reverse=True):
            for emp in bloco.get("empresas", []):
                k = _norm(emp["nome"])
                if k and (k not in icms or emp["posicao"] < icms[k]["posicao"]):
                    icms[k] = {"posicao": emp["posicao"], "cnpj": emp.get("cnpj"), "nome": emp["nome"], "anos": [ano],
                               "setor": emp.get("setor"), "municipio": emp.get("municipio_lista")}
    itens = []
    fonte_lista = CONHECIDAS_FISCAL if categoria == "destinacao_tributaria" else CONHECIDAS_PATROCINIO
    for reg in fonte_lista:
        nome = reg[0]; n = _norm(nome)
        casa_icms = next((v for k, v in icms.items() if n in k or k in n), None)
        no_gife = any(n in g or g in n for g in gife)
        obs = next((v for k, v in patr.items() if n in k or k in n), None)
        pontos, por = 0, []
        if casa_icms:
            p = 40 if casa_icms["posicao"] <= 20 else 30 if casa_icms["posicao"] <= 100 else 20
            pontos += p; por.append(f"{p}: {casa_icms['posicao']}º maior contribuinte do ICMS de Goiás (lista oficial)")
        if no_gife:
            pontos += 15; por.append("15: organização mapeada em fonte GIFE (investimento social)")
        if obs:
            pontos += 20; por.append(f"20: patrocínio observado pelo motor ({len(obs)} achado(s) na imprensa de Goiás)")
        if categoria == "destinacao_tributaria":
            pontos += 20; por.append("20: programa de investimento social conhecido publicamente (instituto/fundação própria) — a confirmar na fonte")
            if len(reg) > 4 and reg[4]:
                pontos += min(10, 3 * len(reg[4])); por.append(f"{min(10, 3*len(reg[4]))}: usa {len(reg[4])} mecanismo(s) de incentivo ({', '.join(reg[4])})")
        else:
            pontos += 15; por.append("15: histórico público de patrocínio de eventos/cultura/esporte — a confirmar na fonte")
            if re.search(r"goi|sagres|anhanguera|popular|sebrae|fieg|sesc|fecom|equatorial|saneago|comigo|bretas|flamboyant|buriti|passeio", n):
                pontos += 25; por.append("25: base ou atuação em Goiás (aproximação local pesa no patrocínio)")
        item = {"nome": nome, "pontos": min(100, pontos), "por": por,
                "cnpj": (casa_icms or {}).get("cnpj"), "icms_goias": (casa_icms or {}).get("posicao"), "gife": no_gife,
                "observado_pelo_motor": obs or None}
        if categoria == "destinacao_tributaria":
            item.update({"programa": reg[1], "apoia": reg[2], "via_de_entrada": reg[3], "incentivos": reg[4],
                         "condicao": "só destina quem apura pelo LUCRO REAL e tem imposto devido; confirmar antes de propor"})
        else:
            item.update({"apoia": reg[1], "via_de_entrada": reg[2],
                         "condicao": "verba de marketing: proposta com contrapartida de marca, público e mídia estimada"})
        itens.append(item)
    # completa com as empresas da base de Goiás que não estão nas listas conhecidas
    conhecidos = {_norm(i["nome"]) for i in itens}
    for k, v in sorted(icms.items(), key=lambda kv: kv[1]["posicao"]):
        if len(itens) >= 100:
            break
        if any(k in c or c in k for c in conhecidos):
            continue
        p = 35 if v["posicao"] <= 20 else 28 if v["posicao"] <= 100 else 22
        itens.append({"nome": v["nome"], "pontos": p, "cnpj": v["cnpj"], "icms_goias": v["posicao"], "gife": False, "observado_pelo_motor": None,
                      "setor": v.get("setor"), "municipio": v.get("municipio"),
                      "por": [f"{p}: {v['posicao']}º maior contribuinte do ICMS de Goiás (lista oficial) — porte e imposto compatíveis",
                              "0: programa de investimento social não identificado ainda — investigar o site institucional"],
                      "apoia": "a investigar no site institucional", "via_de_entrada": "site institucional / relações institucionais",
                      "programa": None, "incentivos": None,
                      "condicao": ("confirmar apuração pelo Lucro Real antes de propor destinação" if categoria == "destinacao_tributaria"
                                   else "confirmar existência de verba de patrocínio regional")})
    itens.sort(key=lambda x: (-x["pontos"], x["nome"]))
    for i, x in enumerate(itens[:100], 1):
        x["posicao"] = i
    return itens[:100]


def run() -> dict:
    DESTINO.mkdir(parents=True, exist_ok=True)
    saida = {}
    for cat, rot in (("destinacao_tributaria", "Destinação tributária (incentivo fiscal)"), ("patrocinio_privado", "Patrocínio privado (marketing)")):
        lista = ranking(cat)
        ficha = {"categoria": cat, "rotulo": rot, "gerado_em": now_iso(), "total": len(lista),
                 "metodo": "pontuação 0–100 por evidência: posição no ICMS de Goiás (lista oficial), presença em fonte GIFE, patrocínio observado pelo motor na imprensa de Goiás, "
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
