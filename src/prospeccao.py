"""PROSPECÇÃO DE FONTES — a missão do Piloto quando não há resgate a fazer.

A ideia que muda tudo: **o Piloto não caça editais, caça LUGARES onde editais nascem.**

Um edital achado serve uma vez. Uma fonte nova, catalogada e promovida a motor, passa a ser
lida todo dia para sempre — sem buscador, sem bloqueio, sem depender de voo. Por isso cada
voo de prospecção tem de terminar com o acervo tendo MAIS LUGARES para olhar do que tinha
antes. O Piloto descobre; o motor colhe.

O caminho de uma fonte, do achado à colheita:

    1. RASTRO      alguém patrocina algo — o logo no rodapé de um site de ONG, o nome numa
                   agenda de evento, a citação numa ata de conselho
    2. EMPRESA     de que empresa é aquele rastro, e qual o site oficial dela
    3. VALIDAÇÃO   o site da empresa tem programa para terceiro setor? de que tipo?
    4. CATÁLOGO    entra no radar com o tipo de recurso e o nível de alcance
    5. MOTOR       se a empresa tem página de editais que se repete, vira motor próprio,
                   e a partir daí o Piloto não precisa mais voltar lá

A validação no passo 3 não usa buscador: lê o site da própria empresa pelo mapa dele
(sitemap), que ninguém bloqueia. É lento e certeiro, o oposto de raspar buscador.
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

from .nucleo import ROOT, load_json, now_iso, write_json

FONTES = ROOT / "estado/piloto/fontes_descobertas.json"
PUB = ROOT / "docs/dados/prospeccao.json"

# Os seis tipos de recurso que uma empresa pode oferecer. Cada um tem porta de entrada
# diferente, e é por isso que classificar importa: pedir patrocínio a quem só faz doação
# via instituto é perder o pedido.
TIPOS = {
    "incentivo_fiscal": {
        "rotulo": "direcionamento de incentivo ou dedução fiscal",
        "pistas": ["incentivo fiscal", "dedução fiscal", "lei rouanet", "lei de incentivo", "fumcad",
                   "fia", "fundo do idoso", "pronas", "pronon", "lei do esporte", "imposto de renda devido",
                   "destinação de imposto", "renúncia fiscal"],
        "porta": "o pedido vai ao setor fiscal ou contábil, não ao marketing — é dinheiro que a empresa deve ao fisco"},
    "patrocinio": {
        "rotulo": "patrocínio de projeto ou evento",
        "pistas": ["patrocínio", "patrocinador", "apoio a projetos", "apoio cultural", "naming",
                   "cota de patrocínio", "proposta de patrocínio"],
        "porta": "marketing ou comunicação; costuma ter calendário e formulário próprios"},
    "edital_proprio": {
        "rotulo": "edital ou chamada pública da própria empresa",
        "pistas": ["edital", "chamada pública", "seleção de projetos", "inscrições abertas",
                   "regulamento", "edições anteriores", "projetos selecionados", "submissão de projetos"],
        "porta": "inscrição direta quando abre — é o tipo que mais vale virar motor"},
    "instituto_fundacao": {
        "rotulo": "instituto ou fundação própria",
        "pistas": ["instituto", "fundação", "braço social", "investimento social privado",
                   "nosso instituto", "fundacao"],
        "porta": "tem governança própria e às vezes edital separado do da empresa"},
    "esg": {
        "rotulo": "programa ESG ou de sustentabilidade",
        "pistas": ["esg", "sustentabilidade", "responsabilidade social", "relatório de sustentabilidade",
                   "impacto social", "ods", "agenda 2030", "relatório anual", "investimento social"],
        "porta": "o relatório diz quanto e onde investiram — é o melhor termômetro antes de pedir"},
    "doacao": {
        "rotulo": "doação direta ou voluntariado",
        "pistas": ["doação", "doar", "campanha solidária", "voluntariado", "matching", "arrecadação",
                   "parcerias sociais", "quero doar"],
        "porta": "menor valor, mas a porta mais fácil e a que abre relacionamento"},
}

NIVEIS = {
    "local": {"rotulo": "Goiânia e região metropolitana",
              "onde_procurar": ["site de entidade local", "agenda de evento na cidade", "ata de conselho municipal",
                                "jornal de bairro", "associação comercial"],
              "vantagem": "a empresa conhece o território e o pedido tem rosto"},
    "estadual": {"rotulo": "Goiás",
                 "onde_procurar": ["federação da indústria", "cooperativa estadual", "grande contribuinte de ICMS",
                                   "agroindústria", "concessionária de serviço público"],
                 "vantagem": "há incentivo fiscal estadual e o alcance justifica o porte do projeto"},
    "federal": {"rotulo": "Brasil",
                "onde_procurar": ["instituto empresarial nacional", "banco", "varejo", "seguradora",
                                  "empresa com relatório ESG publicado"],
                "vantagem": "valores maiores e editais com calendário previsível"},
    "internacional": {"rotulo": "fora do Brasil, aceitando OSC brasileira",
                      "onde_procurar": ["fundação estrangeira", "embaixada", "agência de cooperação",
                                        "programa global de multinacional", "matching grant"],
                      "vantagem": "pouca concorrência brasileira porque quase ninguém procura"},
}

# Caminhos que quase toda empresa usa para essas páginas — testados direto no site dela
# TRILHAS — os caminhos que empresas usam para estas páginas. Quanto mais larga a lista,
# menos fonte escapa. Vão em português e inglês (multinacional publica em inglês), com e sem
# hífen, no singular e no plural, e com os prefixos de seção mais comuns (/institucional,
# /quem-somos, /sobre, /ri para relações com investidores, onde mora o relatório anual).
_RAIZ = ["", "/institucional", "/quem-somos", "/sobre", "/sobre-nos", "/a-empresa", "/ri",
         "/relacoes-com-investidores", "/pt-br", "/pt", "/br"]
_FOLHA = [
    # responsabilidade social e ESG
    "/sustentabilidade", "/esg", "/responsabilidade-social", "/responsabilidade-socioambiental",
    "/impacto-social", "/impacto", "/investimento-social", "/investimento-social-privado",
    "/cidadania", "/cidadania-corporativa", "/compromisso-social", "/acao-social", "/acoes-sociais",
    "/sustainability", "/social-impact", "/corporate-responsibility", "/csr", "/community",
    # instituto, fundação e braço social
    "/instituto", "/fundacao", "/nosso-instituto", "/instituto-social", "/foundation",
    # editais, chamadas e seleção
    "/editais", "/edital", "/chamadas", "/chamada-publica", "/selecao-de-projetos", "/inscricoes",
    "/projetos-apoiados", "/projetos-selecionados", "/edicoes-anteriores", "/como-participar",
    "/submissao", "/regulamento", "/grants", "/apply", "/call-for-proposals",
    # patrocínio e apoio
    "/patrocinio", "/patrocinios", "/apoio-a-projetos", "/apoio-cultural", "/proposta-de-patrocinio",
    "/seja-patrocinador", "/parcerias", "/parceiros", "/sponsorship", "/partnerships",
    # incentivo fiscal
    "/incentivo-fiscal", "/incentivos-fiscais", "/lei-de-incentivo", "/lei-rouanet",
    "/renuncia-fiscal", "/destinacao-de-imposto", "/imposto-de-renda",
    # doação e voluntariado
    "/doacoes", "/doacao", "/doe", "/quero-doar", "/voluntariado", "/seja-voluntario",
    "/campanhas", "/donate", "/volunteering",
    # documentos onde o número aparece
    "/relatorios", "/relatorio-anual", "/relatorio-de-sustentabilidade", "/relatorio-social",
    "/balanco-social", "/transparencia", "/publicacoes", "/reports", "/annual-report",
    # a porta de entrada, quando existe
    "/contato", "/fale-conosco", "/imprensa", "/noticias", "/blog",
]
TRILHAS = _FOLHA + [r + f for r in _RAIZ[1:6] for f in
                    ("/sustentabilidade", "/esg", "/responsabilidade-social", "/instituto",
                     "/editais", "/patrocinio", "/doacoes", "/relatorios")]

# Para onde cada tipo de recurso manda a fonte. Uma empresa que so tem ESG nao merece motor
# proprio — mas ENGORDA o motor que ja vigia esse tipo de coisa, virando mais uma rota dele.
MOTOR_DO_TIPO = {
    "incentivo_fiscal": "empresas-incentivadas",
    "patrocinio": "motor-patrocinio",
    "doacao": "motor-patrocinio",
    "esg": "motor-gife",
    "instituto_fundacao": "motor-gife",
    "edital_proprio": None,      # este ganha motor proprio: tem pagina que se repete
}

# Os domínios são ancorados no início do host (depois de // ou de um ponto). Sem isso, o
# padrão do Twitter ("x.com") casava dentro de "bancox.com.br" e descartava a empresa.
IGNORAR = re.compile(
    r"^(mailto:|tel:|javascript:)"
    r"|(?://|\.)(facebook|instagram|twitter|x|linkedin|youtube|youtu|tiktok|whatsapp|wa|"
    r"google|maps|goo|bit|wordpress|w3|schema|gravatar|gstatic)\.[a-z.]{2,8}(/|$)"
    r"|(?://|\.)gov\.br(/|$)|\.gov\.[a-z]{2}(/|$)", re.I)


def fontes() -> dict:
    return load_json(FONTES) if FONTES.exists() else {"em": None, "itens": {}}


def _dominio(url: str) -> str:
    return (urlsplit(str(url or "")).hostname or "").replace("www.", "").lower()


def catalogar_patrocinadores(html: str, origem: str) -> list[dict]:
    """PASSO 1 e 2: de um site de outra entidade, tirar quem a patrocina.

    Rodapés de ONG, página de 'nossos apoiadores', 'parceiros', 'quem nos apoia' — é ali que
    as empresas que já financiam terceiro setor se declaram, e nenhum motor procura ali.
    """
    achados, vistos = [], set()
    orig_dom = _dominio(origem)
    # a pista mais forte: link externo perto de palavra de apoio
    for m in re.finditer(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html or "", re.I | re.S):
        url, dentro = m.group(1), m.group(2)
        if not url.startswith("http") or IGNORAR.search(url):
            continue
        dom = _dominio(url)
        if not dom or dom == orig_dom or dom in vistos:
            continue
        # o contexto ao redor do link diz se é apoiador ou link qualquer
        volta = (html[max(0, m.start() - 600):m.start()] or "").lower()
        if not re.search(r"(apoiador|apoio|patroc|parceir|mantenedor|quem nos apoia|realiza(ção|cao)|"
                         r"nossos parceiros|financiador)", volta):
            continue
        nome = re.sub(r"<[^>]+>", " ", dentro)
        nome = re.sub(r"\s+", " ", nome).strip()
        if not nome:
            alt = re.search(r'alt=["\']([^"\']{3,60})["\']', dentro, re.I)
            nome = alt.group(1).strip() if alt else dom.split(".")[0].title()
        vistos.add(dom)
        achados.append({"nome": nome[:80], "dominio": dom, "site": f"https://{dom}",
                        "rastro": "declarado como apoiador", "onde_vi": origem[:140]})
    return achados[:40]


def validar_empresa(dominio: str, ler=None, tempo: float = 15) -> dict:
    """PASSO 3: o site da própria empresa diz o que ela oferece — sem passar por buscador.

    Abre as trilhas comuns e lê o que encontrar, classificando pelos seis tipos. Só afirma o
    que estiver escrito: cada tipo encontrado guarda a página e o trecho que o comprova.
    """
    if ler is None:
        from .piloto_busca import ler_pagina as ler
    encontrados, paginas = {}, []
    for trilha in TRILHAS:
        url = f"https://{dominio}{trilha}"
        try:
            txt = ler(url, tempo=tempo)
        except Exception:
            continue
        if not txt or len(txt) < 250:
            continue
        baixo = txt.lower()
        paginas.append(url)
        for tipo, d in TIPOS.items():
            for pista in d["pistas"]:
                if pista in baixo:
                    i = baixo.index(pista)
                    trecho = re.sub(r"\s+", " ", txt[max(0, i - 90):i + 150]).strip()
                    atual = encontrados.get(tipo)
                    if not atual:
                        encontrados[tipo] = {"pagina": url, "pista": pista, "trecho": trecho[:200]}
                    break
        if len(paginas) >= 6:
            break
    return {"dominio": dominio, "validado_em": date.today().isoformat(),
            "paginas_lidas": paginas, "tipos": encontrados,
            "tem_programa": bool(encontrados),
            "vira_motor": "edital_proprio" in encontrados,
            "porque_nao": None if encontrados else "nenhuma das trilhas do site menciona apoio a terceiro setor"}


def registrar(empresa: dict, validacao: dict | None = None, nivel: str = "federal", angulo: str = "") -> dict:
    """PASSO 4: entra no catálogo, com o tipo de recurso e o nível de alcance."""
    FONTES.parent.mkdir(parents=True, exist_ok=True)
    d = fontes()
    k = empresa.get("dominio") or _dominio(empresa.get("site", ""))
    if not k:
        return {}
    it = d["itens"].get(k) or {"descoberto_em": date.today().isoformat(), "vezes_vista": 0,
                               "rastros": [], "estado": "descoberta"}
    it.update({"nome": empresa.get("nome", k)[:90], "dominio": k, "site": empresa.get("site") or f"https://{k}",
               "nivel": nivel if nivel in NIVEIS else "federal", "ultima_vez": date.today().isoformat()})
    it["vezes_vista"] += 1
    if empresa.get("onde_vi") and empresa["onde_vi"] not in it["rastros"]:
        it["rastros"] = (it["rastros"] + [empresa["onde_vi"]])[:6]
    if angulo:
        it["angulo"] = angulo
    if validacao:
        it["validacao"] = validacao
        it["tipos"] = sorted(validacao.get("tipos", {}))
        it["estado"] = "validada" if validacao.get("tem_programa") else "sem_programa"
        it["vira_motor"] = validacao.get("vira_motor", False)
        it["portas"] = [TIPOS[t]["porta"] for t in it["tipos"] if t in TIPOS]
    it["pontos"] = (len(it.get("tipos") or []) * 5
                    + (10 if it.get("vira_motor") else 0)
                    + (6 if "incentivo_fiscal" in (it.get("tipos") or []) else 0)
                    + (4 if it.get("nivel") in ("local", "estadual") else 0)
                    + min(6, 2 * (it["vezes_vista"] - 1)))
    d["itens"][k] = it
    d["em"] = now_iso()
    write_json(FONTES, d)
    return it


def promover_a_motor(dominio: str) -> dict:
    """PASSO 5: fonte com edital próprio vira MOTOR — e o Piloto não volta mais lá.

    É aqui que o trabalho do Piloto vira patrimônio: o motor lê aquilo todo dia, de graça,
    sem buscador. Uma fonte promovida rende para sempre; um edital achado rende uma vez.
    """
    d = fontes()
    it = d["itens"].get(dominio)
    if not it or not it.get("vira_motor"):
        return {"erro": "fonte não tem edital próprio comprovado; não vira motor"}
    cfg = load_json(ROOT / "config/rotas_motores.json")
    motores = cfg.get("motores") or cfg
    mid = "fonte-" + re.sub(r"[^a-z0-9]+", "-", dominio.split(".")[0])[:26]
    if mid in motores:
        return {"ja_existe": mid}
    v = it.get("validacao") or {}
    pagina = (v.get("tipos", {}).get("edital_proprio") or {}).get("pagina") or it["site"]
    motores[mid] = {
        "nome": f"{it['nome']} — editais próprios",
        "perfil": "empresa/instituto descoberto pelo Piloto",
        "rotas": [{"url": pagina, "tipo": "pagina"}, {"url": it["site"], "tipo": "raiz"}],
        "lexico_camada1": ["edital", "chamada pública", "seleção de projetos", "inscrições",
                           "regulamento", "patrocínio", "apoio a projetos"],
        "lexico_camada2": ["organizações da sociedade civil", "sem fins lucrativos", "projeto social",
                           "assistência social", "cultura"],
        "origem": "prospecção do Piloto", "nivel": it.get("nivel"),
        "tipos_de_recurso": it.get("tipos"), "criado_em": date.today().isoformat(),
        "nota": "descoberto pelo Piloto e promovido a motor: a partir daqui é colheita diária, não voo"}
    cfg["motores"] = motores
    write_json(ROOT / "config/rotas_motores.json", cfg)
    it["estado"] = "promovida_a_motor"
    it["motor"] = mid
    it["promovida_em"] = date.today().isoformat()
    write_json(FONTES, d)
    return {"motor_criado": mid, "rota": pagina}


def agregar_a_motor(dominio: str) -> dict:
    """A fonte que não tem edital próprio ENGORDA o motor que já vigia aquele tipo de recurso.

    Uma empresa com relatório ESG não merece motor só dela — mas vira mais uma rota do motor
    que lê ESG todo dia. É assim que a descoberta de hoje vira colheita de amanhã sem inchar
    o sistema com motores de uma página só.
    """
    d = fontes()
    it = d["itens"].get(dominio)
    if not it:
        return {"erro": "fonte desconhecida"}
    cfg = load_json(ROOT / "config/rotas_motores.json")
    motores = cfg.get("motores") or cfg
    v = it.get("validacao") or {}
    ganhos, termos_novos = [], set()
    for tipo in (it.get("tipos") or []):
        mid = MOTOR_DO_TIPO.get(tipo)
        if not mid or mid not in motores:
            continue
        mc = motores[mid]
        pagina = (v.get("tipos", {}).get(tipo) or {}).get("pagina") or it["site"]
        rotas = mc.setdefault("rotas", [])
        if any((r.get("url") if isinstance(r, dict) else r) == pagina for r in rotas):
            continue
        rotas.append({"url": pagina, "tipo": "pagina", "origem": f"prospecção do Piloto ({tipo})",
                      "empresa": it["nome"], "nivel": it.get("nivel"), "desde": date.today().isoformat()})
        mc["rotas_do_piloto"] = mc.get("rotas_do_piloto", 0) + 1
        ganhos.append({"motor": mid, "tipo": tipo, "rota": pagina})
        # o que a página usou para se identificar vira termo candidato do motor
        pista = (v.get("tipos", {}).get(tipo) or {}).get("pista")
        if pista and pista not in (mc.get("lexico_camada1") or []):
            termos_novos.add((mid, pista))
    for mid, termo in termos_novos:
        motores[mid].setdefault("lexico_candidatos", [])
        if termo not in motores[mid]["lexico_candidatos"]:
            motores[mid]["lexico_candidatos"].append(termo)
    if ganhos:
        cfg["motores"] = motores
        write_json(ROOT / "config/rotas_motores.json", cfg)
        it["agregada_a"] = [g["motor"] for g in ganhos]
        it["estado"] = "agregada_a_motor" if it.get("estado") != "promovida_a_motor" else it["estado"]
        write_json(FONTES, d)
    return {"rotas_acrescentadas": ganhos, "termos_candidatos": sorted({t for _, t in termos_novos})}


def encaminhar(dominio: str) -> dict:
    """Decide o destino da fonte: motor próprio se tem edital, senão engorda o motor do tipo."""
    it = fontes()["itens"].get(dominio) or {}
    if it.get("vira_motor"):
        r = promover_a_motor(dominio)
        r.update(agregar_a_motor(dominio))          # e ainda engorda os motores dos outros tipos
        return r
    return agregar_a_motor(dominio)


def para_biblioteca(dominio: str) -> dict:
    """Empresa validada entra na Biblioteca de Alexandria como ficha própria.

    A Biblioteca guarda oportunidades; uma empresa com programa É uma oportunidade — só que
    de porta aberta o ano inteiro em vez de prazo fechado. A ficha traz o que se sabe e o que
    falta descobrir, para quando o relatório completo da empresa for montado.
    """
    it = fontes()["itens"].get(dominio)
    if not it or not it.get("tipos"):
        return {}
    pasta = (ROOT / "biblioteca_alexandria/empresas/fichas" /
             re.sub(r"[^a-z0-9-]", "-", dominio.replace(".", "-"))[:60])
    pasta.mkdir(parents=True, exist_ok=True)
    v = it.get("validacao") or {}
    ficha = {
        "nome": it["nome"], "site": it["site"], "dominio": dominio, "nivel": it.get("nivel"),
        "descoberta_em": it.get("descoberto_em"), "descoberta_por": "Piloto (prospecção)",
        "como_foi_achada": it.get("rastros"),
        "o_que_oferece": [{"tipo": tp, "rotulo": TIPOS[tp]["rotulo"], "porta_de_entrada": TIPOS[tp]["porta"],
                           "pagina": (v.get("tipos", {}).get(tp) or {}).get("pagina"),
                           "prova": (v.get("tipos", {}).get(tp) or {}).get("trecho")}
                          for tp in it["tipos"] if tp in TIPOS],
        "pontos": it.get("pontos"), "virou_motor": it.get("motor"),
        "a_descobrir": ["quem decide (nome e cargo)", "projetos já apoiados e valores",
                        "contato direto do responsável", "calendário de abertura",
                        "se aceita OSC de Goiás", "exigências documentais"],
        "nota": "ficha aberta: o relatório completo da empresa entra aqui quando o titular enviar o material",
        "em": now_iso()}
    write_json(pasta / "ficha.json", ficha)
    it["na_biblioteca"] = str(pasta.relative_to(ROOT))
    d = fontes(); d["itens"][dominio] = it; write_json(FONTES, d)
    return {"ficha": it["na_biblioteca"], "tipos": it["tipos"]}


def incorporar(dominio: str) -> dict:
    """Tudo o que uma fonte validada desencadeia, de uma vez: motor, Biblioteca e ranking."""
    r = {"encaminhamento": encaminhar(dominio), "biblioteca": para_biblioteca(dominio)}
    try:
        from .ranking_apoiadores import montar
        r["ranking"] = montar()
    except Exception as e:
        r["ranking"] = {"erro": str(e)[:80]}
    return r


def publicar() -> dict:
    d = fontes()
    its = d.get("itens") or {}
    por_estado, por_nivel, por_tipo = {}, {}, {}
    for v in its.values():
        por_estado[v.get("estado", "?")] = por_estado.get(v.get("estado", "?"), 0) + 1
        por_nivel[v.get("nivel", "?")] = por_nivel.get(v.get("nivel", "?"), 0) + 1
        for t in (v.get("tipos") or []):
            por_tipo[t] = por_tipo.get(t, 0) + 1
    hoje = date.today().isoformat()
    saida = {"em": now_iso(), "total": len(its),
             "descobertas_hoje": sum(1 for v in its.values() if v.get("descoberto_em") == hoje),
             "promovidas_a_motor": sum(1 for v in its.values() if v.get("estado") == "promovida_a_motor"),
             "por_estado": por_estado, "por_nivel": por_nivel, "por_tipo": por_tipo,
             "meta": "cada dia o sistema tem de terminar com mais lugares para olhar do que começou",
             "tipos": {k: v["rotulo"] for k, v in TIPOS.items()},
             "niveis": {k: v["rotulo"] for k, v in NIVEIS.items()},
             "fontes": sorted(({"dominio": k, **{c: v.get(c) for c in
                                ("nome", "site", "nivel", "estado", "tipos", "pontos", "vira_motor",
                                 "motor", "rastros", "portas")}} for k, v in its.items()),
                              key=lambda x: -(x.get("pontos") or 0))[:150]}
    write_json(PUB, saida)
    return {k: v for k, v in saida.items() if k != "fontes"}


if __name__ == "__main__":
    print(json.dumps(publicar(), ensure_ascii=False, indent=1))
