"""MISSÃO REGULAR — reconhecimento do terceiro setor e de quem o financia.

A pergunta desta missão não é "que edital está aberto". É: **quem pagou por aquilo?**

Toda atividade do terceiro setor que acontece teve alguém financiando: uma oficina numa
associação, um festival de uma ONG, a reforma de uma APAE, o ônibus de um projeto esportivo.
Esse alguém quase nunca publicou edital — patrocinou, doou, destinou imposto ou aplicou verba
de marketing. E por isso **nenhum dos 29 motores o encontra**: motor lê edital publicado, e
aqui não houve publicação nenhuma.

O caminho da missão:

    1. ENTIDADE      achar sites de associações, ONGs, fundações, institutos, APAEs
    2. ATIVIDADE     o que elas fizeram — projeto, evento, obra, oficina
    3. FINANCIADOR   quem pagou, e por qual via
    4. CATÁLOGO      a empresa entra no radar; a via entra como tipo de fonte
    5. PLANO DE VOO  cada descoberta vira alvo de investigação nos voos seguintes

A imprensa entra como fonte de primeira ordem, não de apoio: matéria de jornal sobre um
projeto social quase sempre nomeia o patrocinador, porque o patrocinador exige que nomeie.
É o rastro mais confiável que existe de dinheiro privado em causa social.
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

from .nucleo import ROOT, load_json, now_iso, write_json

ALVOS = ROOT / "estado/piloto/reconhecimento.json"
PUB = ROOT / "docs/dados/reconhecimento.json"

# Onde as entidades e as matérias vivem. Cada frente rende um tipo de rastro diferente.
FRENTES = {
    "entidade": {
        "rotulo": "site de entidade do terceiro setor",
        "procurar": ["associação de moradores", "ONG", "instituto social", "fundação",
                     "APAE", "casa de apoio", "projeto social", "obra social", "entidade filantrópica"],
        "onde_olhar": ["apoiadores", "parceiros", "quem nos apoia", "transparência",
                       "prestação de contas", "relatório anual", "nossos projetos"],
        "rende": "lista de patrocinadores declarada pela própria entidade"},
    "imprensa": {
        "rotulo": "imprensa e divulgação",
        "procurar": ["jornal", "portal de notícias", "rádio", "TV", "assessoria",
                     "agência de notícias", "blog local"],
        "onde_olhar": ["matéria sobre projeto social", "inauguração", "entrega de",
                       "patrocinado por", "com apoio de", "realização"],
        "rende": "o nome do patrocinador, que a matéria cita por exigência dele"},
    "evento": {
        "rotulo": "agenda e evento social",
        "procurar": ["festival", "feira", "campanha", "arrecadação", "gincana",
                     "torneio", "mostra cultural", "bazar beneficente"],
        "onde_olhar": ["cartaz", "programação", "realização", "patrocínio", "apoio institucional"],
        "rende": "a empresa que paga a cota de patrocínio do evento"},
    "prestacao": {
        "rotulo": "prestação de contas e transparência",
        "procurar": ["balanço social", "relatório de atividades", "demonstrativo",
                     "prestação de contas", "parecer do conselho fiscal"],
        "onde_olhar": ["receitas", "doações recebidas", "convênios", "origem dos recursos"],
        "rende": "o valor e a origem, que é o dado mais difícil de conseguir"},
}

# As vias pelas quais o dinheiro chegou. A via muda a porta pela qual se pede.
VIAS = {
    "patrocinio": ["patrocínio", "patrocinado por", "patrocinador", "cota de patrocínio"],
    "doacao": ["doação", "doou", "doado por", "campanha de arrecadação"],
    # os nomes por extenso importam: a matéria escreve "Fundo da Criança e do Adolescente",
    # não "FIA" — e sem isso o repasse era classificado como patrocínio comum
    "incentivo_fiscal": ["lei de incentivo", "rouanet", "lei do esporte", "lei federal de incentivo",
                         "fia", "fundo da criança", "fundo da crianca", "fundo do idoso",
                         "fundo municipal", "pronon", "pronas", "incentivo fiscal", "dedução",
                         "deducao", "renúncia fiscal", "abatimento no imposto"],
    "marketing_social": ["ação de marketing", "responsabilidade social", "voluntariado corporativo",
                         "dia do voluntário", "ativação"],
    "convenio": ["convênio", "termo de fomento", "termo de colaboração", "parceria com o poder público"],
}

# O QUE NÃO É EMPRESA. "com recursos da Lei de Incentivo ao Esporte" credita a LEI, não quem
# pagou — e a lei entrando como empresa poluiria o radar com nomes que não se pode procurar.
NAO_E_EMPRESA = re.compile(
    r"^(lei|leis|art|artigo|decreto|portaria|edital|programa|fundo|minist[ée]rio|secretaria|"
    r"prefeitura|munic[íi]pio|estado|uni[ãa]o|governo|c[âa]mara|assembleia|conselho|"
    r"emenda|termo|convocat[óo]ria|chamamento|projeto|associa[çc][ãa]o|ong)\b", re.I)

IGNORAR = re.compile(r"(facebook|instagram|twitter|youtube|linkedin|tiktok|whatsapp|"
                     r"google|gov\.br|\.gov\.|pncp|queridodiario|wikipedia)", re.I)


def _e_ensaio_url(u: str) -> bool:
    """DOMÍNIO DE ENSAIO NÃO ENTRA (24/09). As 27 empresas fictícias do banco de provas voltaram ao
    radar por uma execução antiga que devolveu o arquivo velho, e a integração levou lixo ('GGFM&')
    à lista de empresas. A barreira passa a ser por domínio: o que só foi visto em site de teste
    é inventado, não importa por onde tenha entrado."""
    try:
        import json as _j
        ens = _j.load(open(ROOT / "config/dominios_de_ensaio.json"))["dominios"]
    except Exception:
        ens = ["x.org", "jornaldacidade.com.br", "portalregional.com.br", "ongsemearfuturo.org.br", "festivalsolidario.com.br"]
    h = (urlsplit(str(u or "")).hostname or "").lower().replace("www.", "")
    return any(h == d or h.endswith("." + d) for d in ens)


def _nome_valido(nome: str) -> bool:
    n = str(nome or "").strip()
    return len(re.sub(r"[^A-Za-zÀ-ú]", "", n)) >= 4 and not re.search(r"[&/|]$", n)


GENERICOS = {"escola", "fundacao", "fundação", "instituto", "associacao", "associação", "projeto", "projetos", "programa",
             "secretaria", "prefeitura", "governo", "ministerio", "ministério", "empresa", "empresas", "entidade", "grupo"}
FICTICIAS = {"agroluz alimentos", "construtora meridiano", "instituto bandeirante", "supermercado cerrado", "fundacao vale verde",
             "fundação vale verde", "cooperativa central", "mineradora serra azul", "energisa goias", "energisa goiás", "banco meridiano",
             "rede bom preco", "rede bom preço", "seguradora goias vida", "seguradora goiás vida", "frigorifico boi forte",
             "frigorífico boi forte", "escritorio andrade arquitetura", "escritório andrade arquitetura", "moveis planalto",
             "móveis planalto", "cimento araguaia", "distribuidora planalto", "usina sao bento", "usina são bento"}


def _item_valido(it: dict) -> bool:
    nome = str(it.get("empresa") or "").strip()
    n = nome.lower()
    if not _nome_valido(nome) or n in FICTICIAS or n.startswith("teste ") or n in GENERICOS:
        return False
    if len(nome.split()[-1]) == 1:                               # "Projetos O": resíduo de extração
        return False
    onde = it.get("onde_foi_vista") or []
    return not (onde and all(_e_ensaio_url(u) for u in onde))


def alvos() -> dict:
    """LIMPEZA NA LEITURA (25/09). Cada voo grava por cima a versão inteira do radar que tinha na cópia dele;
    uma limpeza feita no arquivo era desfeita pelo voo que estava no ar, e todos os seguintes herdavam — as
    empresas fictícias do banco de provas e 8 'Teste Reconhecimento' ficaram o dia 25 inteiro. Agora quem
    abre o radar recebe só o que é válido, e todo voo que o grava já grava limpo: a sujeira se desfaz sozinha."""
    d = load_json(ALVOS) if ALVOS.exists() else {"em": None, "itens": {}, "plano": []}
    d["itens"] = {k: v for k, v in (d.get("itens") or {}).items() if isinstance(v, dict) and _item_valido(v)}
    d["plano"] = [p for p in (d.get("plano") or []) if p.get("alvo") in d["itens"]]
    return d


def _chave(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(s or "").lower())[:40]


def ler_rastros(texto: str, url: str) -> list[dict]:
    """De uma página de entidade ou de uma matéria, tirar QUEM PAGOU e POR QUAL VIA.

    Procura o padrão que o português usa para creditar quem financia: 'patrocínio de X',
    'com apoio da Y', 'realização Z'. É o mesmo padrão em site de ONG e em matéria de jornal.
    """
    achados, vistos = [], set()
    t = re.sub(r"\s+", " ", texto or "")
    # O português credita quem paga de meia dúzia de formas, e todas terminam apontando um
    # nome próprio. "doação de 200 cestas feita pelo Mercado X" quebra o padrão ingênuo:
    # por isso a forma "feita por" entra separada da forma "doação de".
    # O português credita quem paga de meia dúzia de formas, e todas apontam um nome próprio.
    # O NOME vai em bloco sensível a maiúscula (?-i:...): com re.I a classe [A-ZÀ-Ú] aceitava
    # minúscula e a captura engolia a frase inteira — "Agroluz Alimentos e contou com" —,
    # comendo o crédito do patrocinador seguinte.
    # O PONTO SÓ VALE DENTRO DE ABREVIATURA. Com "." livre na classe, "Meridiano. A" virava
    # um nome só, a captura passava do fim da frase e a janela ia buscar a via na frase
    # seguinte — quatro empresas viraram "incentivo fiscal" por contágio do vizinho.
    # Agora o ponto só entra se a letra seguinte for maiúscula: "S.A" sim, "Meridiano. A" não.
    # a sigla continua depois do ponto: "Alfa S.A" é um nome só, "Meridiano. A" não é
    _P = r"[A-ZÀ-Ú][\w&\-]*(?:\.[A-ZÀ-Ú][\w&\-]*)*"
    NOME = rf"(?-i:({_P}(?: {_P}){{0,4}}))"
    CREDITO = (r"patroc[íi]nio d[eoa]s?|patrocinad[oa]s? p[eo]l[oa]s?|"
               # "teve apoio do X" também credita: sem esta forma, metade dos apoios escapava
               r"(?:contou )?(?:com |teve |tem )?[oa]?s? ?apoios? d[eoa]s?|"
               r"apoio institucional d[eoa]s?|"
               r"realiza[çc][ãa]o d[eoa]s?|viabilizad[oa] p[eo]l[oa]s?|"
               r"doa[çc][ãa]o d[eoa]s?|doad[oa]s? p[eo]l[oa]s?|"
               r"(?:foi )?(?:feit[oa]|entregue|custead[oa]|bancad[oa])s? p[eo]l[oa]s?|"
               r"financiad[oa] p[eo]l[oa]s?|recursos d[eoa]s?")
    padrao = re.compile(rf"({CREDITO})\s+{NOME}", re.I)
    for m in padrao.finditer(t):
        # o padrão já decide onde o nome acaba: cortar no primeiro ponto aqui destruiria a
        # sigla ("Alfa S.A" virava "Alfa S")
        nome = m.group(2)
        nome = re.sub(r"\s+(e|para|que|com|no|na|em|durante|através|atraves)\b.*$", "", nome).strip(" .,;")
        # com re.I a captura aceita minúscula: exige-se que comece por maiúscula de verdade
        if not nome[:1].isupper():
            continue
        if NAO_E_EMPRESA.search(nome) or len(nome) < 3 or _chave(nome) in vistos:
            continue
        i = m.start()
        # A JANELA PARA NO PONTO FINAL. Mesmo curta, ela atravessava a fronteira da frase:
        # "apoio da Construtora Meridiano. A quadra foi viabilizada [...] com recursos da Lei
        # de Incentivo" fazia a Construtora virar incentivo fiscal por contágio do vizinho.
        # Cada crédito é uma frase, e a via tem de sair de dentro dela.
        ini = t.rfind(".", max(0, i - 120), i) + 1
        fim = t.find(".", m.end())
        fim = (fim if fim != -1 else len(t))
        volta = t[max(ini, i - 120):min(fim + 1, m.end() + 130)].lower()
        # a ordem importa: quem cita lei de incentivo está dizendo COMO pagou, e isso vence
        # a palavra "patrocínio", que aparece em quase toda matéria
        via = next((k for k in ("incentivo_fiscal", "convenio", "doacao", "marketing_social", "patrocinio")
                    if any(p in volta for p in VIAS[k])), "patrocinio")
        vistos.add(_chave(nome))
        achados.append({"empresa": nome[:80], "via": via,
                        "trecho": re.sub(r"\s+", " ", t[max(0, i - 90):i + 150]).strip()[:200],
                        "onde_vi": url[:160]})
    return achados[:25]


def registrar(rastro: dict, frente: str, nivel: str = "regional") -> dict:
    """A empresa vira alvo de investigação, e o alvo entra no plano dos próximos voos."""
    _r = rastro if isinstance(rastro, dict) else {}
    if _e_ensaio_url(_r.get("url") or _r.get("onde") or _r.get("pagina") or "") or not _nome_valido(_r.get("empresa") or _r.get("nome") or ""):
        return None
    ALVOS.parent.mkdir(parents=True, exist_ok=True)
    d = alvos()
    k = _chave(rastro.get("empresa"))
    if not k:
        return {}
    it = d["itens"].get(k) or {"descoberto_em": date.today().isoformat(), "vezes_vista": 0,
                               "vias": [], "onde_foi_vista": [], "estado": "a_investigar"}
    it.update({"empresa": rastro["empresa"], "nivel": nivel, "frente": frente,
               "ultima_vez": date.today().isoformat()})
    it["vezes_vista"] += 1
    if rastro.get("via") and rastro["via"] not in it["vias"]:
        it["vias"].append(rastro["via"])
    if rastro.get("onde_vi") and rastro["onde_vi"] not in it["onde_foi_vista"]:
        it["onde_foi_vista"] = (it["onde_foi_vista"] + [rastro["onde_vi"]])[:8]
    if rastro.get("trecho") and not it.get("prova"):
        it["prova"] = rastro["trecho"]
    # o que falta saber para transformar isto em pedido
    it["a_investigar"] = ["site oficial da empresa", "se tem instituto ou fundação",
                          "se publica relatório ESG", "se já destinou por lei de incentivo",
                          "quem decide o patrocínio", "faixa de valor praticada"]
    it["pontos"] = (10 * len(it["vias"]) + 5 * min(4, it["vezes_vista"])
                    + (8 if "incentivo_fiscal" in it["vias"] else 0)
                    + (6 if nivel in ("local", "regional") else 0))
    d["itens"][k] = it
    # PLANO DE VOO: cada descoberta pede um voo de investigação
    plano = d.setdefault("plano", [])
    if not any(x.get("alvo") == k for x in plano):
        plano.insert(0, {"alvo": k, "empresa": it["empresa"], "criado_em": date.today().isoformat(),
                         "pergunta": f"O que {it['empresa']} financia no terceiro setor, por qual via, "
                                     f"e por onde se pede?",
                         "porque": f"vista {it['vezes_vista']}x em {frente} — "
                                   f"{', '.join(it['vias'])}"})
        d["plano"] = plano[:60]
    d["em"] = now_iso()
    write_json(ALVOS, d)
    return it


def proximo_do_plano() -> dict | None:
    """O próximo alvo a investigar — é isto que altera o plano de voo seguinte."""
    d = alvos()
    for x in (d.get("plano") or []):
        it = (d.get("itens") or {}).get(x["alvo"]) or {}
        if it.get("estado") == "a_investigar":
            return {**x, **it}
    return None


def marcar(chave: str, estado: str, achado: dict | None = None) -> dict:
    d = alvos()
    it = (d.get("itens") or {}).get(chave)
    if not it:
        return {}
    it["estado"] = estado
    it["investigado_em"] = date.today().isoformat()
    if achado:
        it.update({k: v for k, v in achado.items() if v})
    write_json(ALVOS, d)
    return it


def publicar() -> dict:
    try:
        alimentar_listas_de_empresas()
    except Exception:
        pass
    d = alvos()
    its = d.get("itens") or {}
    por_via, por_frente, por_estado = {}, {}, {}
    for v in its.values():
        for x in (v.get("vias") or []):
            por_via[x] = por_via.get(x, 0) + 1
        por_frente[v.get("frente", "?")] = por_frente.get(v.get("frente", "?"), 0) + 1
        por_estado[v.get("estado", "?")] = por_estado.get(v.get("estado", "?"), 0) + 1
    saida = {"em": now_iso(), "total": len(its),
             "pergunta": "quem pagou pelas atividades do terceiro setor que já aconteceram",
             "porque_os_motores_nao_acham": "não houve edital publicado: houve patrocínio, doação, "
                                            "destinação de imposto ou verba de marketing",
             "por_via": por_via, "por_frente": por_frente, "por_estado": por_estado,
             "frentes": {k: v["rotulo"] for k, v in FRENTES.items()},
             "vias": list(VIAS),
             "no_plano_de_voo": len([x for x in (d.get("plano") or [])
                                     if (its.get(x["alvo"]) or {}).get("estado") == "a_investigar"]),
             "empresas": sorted(({"chave": k, **{c: v.get(c) for c in
                                  ("empresa", "vias", "frente", "nivel", "estado", "pontos",
                                   "vezes_vista", "prova", "onde_foi_vista")}} for k, v in its.items()),
                                key=lambda x: -(x.get("pontos") or 0))[:120]}
    write_json(PUB, saida)
    return {k: v for k, v in saida.items() if k != "empresas"}


if __name__ == "__main__":
    print(json.dumps(publicar(), ensure_ascii=False, indent=1))


def alimentar_listas_de_empresas() -> dict:
    """AS EMPRESAS DA MISSÃO 2 ENTRAM NA LISTA DE EMPRESAS (titular, 24/09). Até aqui o ranking
    excluía as descobertas do Piloto de propósito. Agora cada empresa reconhecida entra na lista
    que a via indica — patrocínio, doação e marketing social vão para 'doação e patrocínio';
    incentivo fiscal vai para 'destinação tributária'; quem tem as duas vias entra nas duas — com
    a origem e as evidências gravadas, para o ranking avaliá-la pelos mesmos critérios."""
    import re as _re
    a = alvos()
    destino = {"patrocinio_privado": ROOT / "biblioteca_alexandria/empresas/ranking_patrocinio_privado.json",
               "destinacao_tributaria": ROOT / "biblioteca_alexandria/empresas/ranking_destinacao_tributaria.json"}
    fiscal = _re.compile(r"incentivo|rouanet|lie|pronon|pronas|fia|idoso|icms|isen[cç]", _re.I)
    social = _re.compile(r"patroc|doa[cç]|marketing|apoio|convenio|conv[êe]nio", _re.I)
    contagem = {k: 0 for k in destino}
    for cat, arq in destino.items():
        d = load_json(arq) if arq.exists() else {"empresas": []}
        chaves = {_re.sub(r"[^a-z0-9]", "", str(e.get("nome") or "").lower())[:40] for e in d.get("empresas", [])}
        for k, it in (a.get("itens") or {}).items():
            vias = " ".join(str(v) for v in (it.get("vias") or [it.get("via")]) if v)
            quer = fiscal.search(vias) if cat == "destinacao_tributaria" else social.search(vias)
            if not quer:
                continue
            ch = _re.sub(r"[^a-z0-9]", "", str(it.get("empresa") or "").lower())[:40]
            if not ch or ch in chaves or not _nome_valido(it.get("empresa")):
                continue
            if all(_e_ensaio_url(u) for u in (it.get("onde_foi_vista") or ["x.org"])):
                continue
            chaves.add(ch); contagem[cat] += 1
            d.setdefault("empresas", []).append({
                "nome": it.get("empresa"), "origem": "reconhecimento do Piloto (missão 2)",
                "vias": it.get("vias") or [it.get("via")], "onde_foi_vista": (it.get("onde_foi_vista") or [])[:5],
                "evidencias": (it.get("evidencias") or [])[:3], "primeira_vez": it.get("primeira_vez"),
                "nota": "entrou pela missão de reconhecimento; classificada pelos mesmos critérios das demais"})
        write_json(arq, d)
    return contagem
