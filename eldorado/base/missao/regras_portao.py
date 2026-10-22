"""As regras do portão da missão das oportunidades — aproveitadas do Eldorado0, com fidelidade.

Lógica validada pela titular ao longo de semanas (decisões datadas nos comentários), reunida de três módulos do
Eldorado0 (repositorio_unico.py, regra_abrangencia.py, pncp_osc.py): só as 36 definições que o portão usa, extraídas
pela árvore de sintaxe, na mesma forma. Duas mudanças de princípio:
  1. nenhum erro engolido: a leitura dos dados do território não devolve vazio em silêncio, e a UF do PNCP não ignora falha;
  2. nenhum arquivo do Eldorado0 é lido: os dados do território vivem em config/missao/.
Régua: os casos reais validados pela titular (testes/test_missao.py) devem dar 100%.
"""
# ruff: noqa: E501, E741, E731, B008, C901   (código aproveitado do Eldorado0, preservado na forma original)
from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

# — repositorio_unico.py · ROOT
ROOT = Path(__file__).resolve().parents[3]          # a raiz do repositório

# — repositorio_unico.py · _MUN
_MUN = re.compile(r"(?i)\bmunic[íi]pio d[eoa]s? |prefeitura (municipal )?d[eoa]s? |c[âa]mara municipal|secretaria municipal|"
                  r"fundo municipal|funda[çc][ãa]o cultural de|conselho municipal|\bmunicipal de ")

# — repositorio_unico.py · _DOM_UF
_DOM_UF = re.compile(r"https?://(?:www\.)?[\w.-]*?\.([a-z]{2})\.(?:gov|leg)\.br")

# — repositorio_unico.py · _ESTADOS
_ESTADOS = [("acre", "AC"), ("alagoas", "AL"), ("amap[aá]", "AP"), ("amazonas", "AM"), ("bahia", "BA"), ("cear[aá]", "CE"), ("esp[ií]rito santo", "ES"),
            ("maranh[aã]o", "MA"), ("mato grosso do sul", "MS"), ("minas gerais", "MG"), ("par[aá]", "PA"), ("para[ií]ba", "PB"), ("paran[aá]", "PR"),
            ("pernambuco", "PE"), ("piau[ií]", "PI"), ("rio de janeiro", "RJ"), ("rio grande do norte", "RN"), ("rio grande do sul", "RS"),
            ("rond[oô]nia", "RO"), ("roraima", "RR"), ("santa catarina", "SC"), ("s[aã]o paulo", "SP"), ("sergipe", "SE"), ("tocantins", "TO"),
            ("goi[aá]s", "GO"), ("distrito federal", "DF")]

# — repositorio_unico.py · UFS
UFS = {"AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"}

# — repositorio_unico.py · _MUN_GO
_MUN_GO: list = []

# — repositorio_unico.py · NAO_OPORTUNIDADE
NAO_OPORTUNIDADE = [
    (re.compile(r"(?i)\bvagas? de (?:est[áa]gio|emprego|trabalho)|abre vaga|processo seletivo (?:simplificado )?para (?:contrata|vaga)"), "vaga de emprego ou estágio — não é recurso para a associação"),
    (re.compile(r"(?i)credenciamento de (?:pessoas? jur[íi]dicas?|prestadores?|profissionais|cl[íi]nicas|laborat|m[ée]dic|empresas|farm[áa]cias)"), "credenciamento de prestadores — não é fomento a OSC"),
    (re.compile(r"(?i)\banuncia \d+ (?:novos?|selecionad|aprovad|vencedor)|\bresultado (?:final|definitivo) d[oa]s? (?:selecionad|aprovad)|\bconhe[çc]a os (?:selecionad|vencedor)"), "notícia de resultado — a seleção já aconteceu"),
    (re.compile(r"(?i)^\s*\d+ (?:editais|oportunidades|chamadas|programas)\b|\b\d+ editais (?:ambientais|culturais|abertos|com inscri)"), "lista de vários editais — cada edital precisa entrar separado"),
    (re.compile(r"(?i)\bminuta (?:de |do )?edital|\bconsulta p[úu]blica\b|\baudi[êe]ncia p[úu]blica\b"), "minuta ou consulta pública — o edital ainda não foi aberto"),
    # 15/10 (ciclo 4, validação de 20 pelo Claude)
    (re.compile(r"(?i)^\s*(?:convocatorias|editais|oportunidades|chamadas|programas|portal de (?:projetos|editais|oportunidades))\b(?!\s*n[ºo°])"), "página de listagem — cada oportunidade precisa entrar separada"),
    (re.compile(r"(?i)(?:\bpara|[-–])\s*escolas (?:municipais|p[úu]blicas|estaduais)"), "público que não é associação (escolas públicas)"),
    (re.compile(r"(?i)\bvoluntariado\b(?!.*\b(?:apoio|fomento|recurso|financ))|seja ?um ?volunt|cadastro de volunt|credenciamento de volunt"), "voluntariado — não é recurso para a associação"),
    (re.compile(r"(?i)notifica[çc][ãa]o de lan[çc]amento|\bIPTU\b|d[íi]vida ativa|lan[çc]amento tribut"), "ato tributário — não é oportunidade"),
    # 15/10 (ciclo 5, validação de 20 pelo Claude)
    (re.compile(r"(?i)vagas? (?:para|da|de) (?:a )?sociedade civil (?:em|no|na) (?:comit|conselho|f[óo]rum|c[âa]mara)|elei[çc][ãa]o (?:de|dos) conselheiros|composi[çc][ãa]o do conselho"), "vaga de representação em comitê ou conselho — não é recurso"),
    (re.compile(r"(?i)\b(?:firma|assina|celebra|renova)m? (?:parceria|conv[êe]nio|acordo|termo|contrato)"), "notícia de parceria já firmada — não é seleção aberta"),
    (re.compile(r"(?i)^\s*comit[êe] gestor\b"), "página institucional de comitê — não é edital"),
    (re.compile(r"(?i)subven[çc][ãa]o econ[ôo]mica|\btecnova\b"), "subvenção econômica — público são empresas, não associações"),
    # 15/10 (ciclo 6, validação de 20 pelo Claude)
    (re.compile(r"(?i)banco de talentos|cadastro de curr[íi]culos?|\bquiz\b|\benquete\b|pesquisa de satisfa[çc][ãa]o"), "cadastro de pessoas, quiz ou enquete — não é edital"),
    (re.compile(r"(?i)profissionais aut[ôo]nomos|credenciamento de pessoas? f[íi]sicas?\b(?!\s+e\s+(?:pessoas?\s+)?jur[íi]dicas?)|aluguel social|benef[íi]cio (?:às|as|para|a) fam[íi]lias|aux[íi]lio (?:às|as|para) fam[íi]lias"), "público são pessoas físicas ou famílias — não associações"),
    (re.compile(r"(?i)divulga[çc][ãa]o (?:do resultado )?prorrogada|prorroga[çc][ãa]o d[ao] (?:divulga[çc][ãa]o|resultado)|apresenta[çc][ãa]o final|cerim[ôo]nia de (?:premia|entrega)|"
                r"\bs[ãa]o indicad[oa]s\b|\bforam selecionad|premia[çc][ãa]o dos vencedores"), "fase de resultado — a inscrição já terminou"),
    # 15/10 (ciclo 7)
    (re.compile(r"(?i)\bgobierno (?:estatal|municipal)\b|\bayuntamiento\b|\bmunicipalidad de\b"), "governo local estrangeiro — não se aplica a associação brasileira"),
]

# — repositorio_unico.py · AGREGADOR_HOST
AGREGADOR_HOST = re.compile(r"(?i)https?://(?:www\.)?(?:capitaai|captadores)\.[a-z.]+(/[^?#]*)?")

# — repositorio_unico.py · PAGINA_DE_AGREGADOR
PAGINA_DE_AGREGADOR = re.compile(r"(?i)https?://(?:www\.)?(?:capitaai|captadores|editaisdobrasil|farolcultural|observatorio3setor|prosas)\.[a-z.]+/(?:planos|precos|preços|sobre|assin|login|cadastro|contato|quem-somos)?/?(?:\?|$)")

# — repositorio_unico.py · OS_CONTRATO_DE_GESTAO
OS_CONTRATO_DE_GESTAO = re.compile(r"Organiza[çc](?:[ãa]o|[õo]es) Sociais?\b|"     # maiúsculas: a figura jurídica OS
                                   r"(?i:contrato de gest[ãa]o)|qualifica[çc][ãa]o como (?:os\b|organiza)|"
                                   r"organiza[çc](?:[ãa]o|[õo]es) sociais?\b(?! civil)[^.]{0,80}\b(?:gest[ãa]o|gerenciamento|administra[çc][ãa]o) d[eoa]s? "
                                   r"(?:unidade|hospital|museu|equipamento|policl[íi]nica|upa|caps)")

# — repositorio_unico.py · ANO_ANTERIOR
ANO_ANTERIOR = re.compile(r"\b(20(?:1\d|2[0-4]))\b")

# — repositorio_unico.py · PERMITE_CREDENCIAMENTO
PERMITE_CREDENCIAMENTO = re.compile(r"(?i)organiza[çc](?:[ãa]o|[õo]es) da sociedade civil|\boscs?\b|sem fins lucrativos|entidades? (?:socioassist|filantr)|associa[çc]")

# — repositorio_unico.py · SAUDE_SERVICO
SAUDE_SERVICO = re.compile(r"(?i)fundo municipal de sa[úu]de|secretaria (?:municipal |estadual )?de sa[úu]de|\bSUS\b|servi[çc]os (?:de sa[úu]de|m[ée]dic|hospitalar|ambulatori)|complementa[çc][ãa]o (?:da rede|dos servi)")

# — repositorio_unico.py · LEGISLATIVO_ABERTAS
LEGISLATIVO_ABERTAS = re.compile(r"(?i)lei or[çc]ament[áa]ria|\bLOA\b|projeto de lei|utilidade p[úu]blica")

# — repositorio_unico.py · _ROTULO_ESTADUAL
_ROTULO_ESTADUAL = re.compile(r"^(?:www|portal|cultura|saude|educacao|esporte|fazenda|governo|casacivil|planejamento|transparencia|diariooficial|doe|"
                              r"imprensaoficial|procultura|sistemas|editais|servicos|agencia\w*|detran|al|tce|tj|mp|defensoria|fap\w*|se\w{1,6}|"
                              r"social|turismo|meioambiente|ambiente|agricultura|ciencia|ct|inovacao|desenvolvimento|economia|seguranca|justica|"
                              r"mulher|direitoshumanos|assistencia|trabalho|juventude|idoso|esportes|lazer|infraestrutura|obras|comunicacao|ses|sema|semad|dpe)$")

# — repositorio_unico.py · _MUN_POR_UF
_MUN_POR_UF: dict = {}

# — repositorio_unico.py · _CAPITAIS_SEM_ESPACO
_CAPITAIS_SEM_ESPACO = {"riobranco", "maceio", "macapa", "manaus", "salvador", "fortaleza", "brasilia", "vitoria", "goiania", "saoluis",
                        "cuiaba", "campogrande", "belohorizonte", "belem", "joaopessoa", "curitiba", "recife", "teresina", "riodejaneiro",
                        "natal", "portoalegre", "portovelho", "boavista", "florianopolis", "saopaulo", "aracaju", "palmas", "rio", "bh", "poa"}

# — repositorio_unico.py · _MUN_BR
_MUN_BR: dict = {}

# — repositorio_unico.py · _CIDADE_NOMEADA
_CIDADE_NOMEADA = re.compile(r"(?i)\b(?:munic[íi]pio|prefeitura(?:\s+municipal)?|c[âa]mara\s+municipal|fundo\s+municipal[\wÀ-ú ]{0,40}?|"
                             r"secretaria\s+municipal[\wÀ-ú ]{0,40}?|di[áa]rio\s+oficial)\s+d[eoa]s?\s+([A-ZÀ-Úa-zà-ú][\wÀ-ú'\- ]{2,40})")

# — repositorio_unico.py · _MUN_POR_ROTULO
_MUN_POR_ROTULO: dict = {}

# — regra_abrangencia.py · ROOT
ROOT = Path(__file__).resolve().parents[3]          # a raiz do repositório

# — pncp_osc.py · CAPITAIS_N
CAPITAIS_N = {"RIO BRANCO", "MACEIO", "MACAPA", "MANAUS", "SALVADOR", "FORTALEZA", "BRASILIA", "VITORIA", "GOIANIA", "SAO LUIS",
              "CUIABA", "CAMPO GRANDE", "BELO HORIZONTE", "BELEM", "JOAO PESSOA", "CURITIBA", "RECIFE", "TERESINA", "RIO DE JANEIRO",
              "NATAL", "PORTO ALEGRE", "PORTO VELHO", "BOA VISTA", "FLORIANOPOLIS", "SAO PAULO", "ARACAJU", "PALMAS"}

# — pncp_osc.py · COMPRA
COMPRA = re.compile(r"\bPREGAO\b|\bCONCORRENCIA\b|\bLEILAO\b|REGISTRO DE PRECOS?|\bAQUISICAO DE\b|\bFORNECIMENTO DE\b|"
                    r"CONTRATACAO DE EMPRESA|EMPRESAS? ESPECIALIZADAS?|MENOR PRECO|\bME/EPP\b|MICROEMPRESAS?|"
                    r"EVENTUAIS E FUTURAS CONTRATACOES|CONTRATAC(?:AO|OES) DE SERVICOS?")

# — pncp_osc.py · PNAE
PNAE = re.compile(r"GENEROS ALIMENTICIOS|AGRICULTURA FAMILIAR|AGRICULTORES? FAMILIAR|\bPNAE\b|ALIMENTACAO ESCOLAR")


# — repositorio_unico.py · _j
def _j(p, padrao=None):
    """Lê um arquivo de dados da missão. Sem o arquivo, o portão não funciona: o erro sobe (nunca devolve vazio em silêncio)."""
    return json.loads(Path(p).read_text(encoding="utf-8"))


# — repositorio_unico.py · _municipio_goiano
def _municipio_goiano(texto: str) -> bool:
    """Cita, como 'município/prefeitura de X' ou 'X/GO', um dos 246 municípios de Goiás (config/territorio_goias.json)?"""
    import unicodedata
    if not _MUN_GO:
        T = _j(ROOT / "config/missao/territorio_goias.json", {}) or {}
        sem = lambda s: "".join(c for c in unicodedata.normalize("NFKD", s.lower()) if not unicodedata.combining(c))
        _MUN_GO.extend(sorted({sem(m) for m in (T.get("municipios") or []) if len(m) > 3}, key=len, reverse=True) or ["-"])
    t = "".join(c for c in unicodedata.normalize("NFKD", texto.lower()) if not unicodedata.combining(c))
    return any(re.search(rf"\b(?:municipio|prefeitura|camara)(?: municipal)? de {re.escape(m)}\b|\b{re.escape(m)}\s*[-/(]\s*go\b", t) for m in _MUN_GO if m != "-")


# — repositorio_unico.py · nao_e_oportunidade
def nao_e_oportunidade(r: dict) -> str | None:
    t = f"{r.get('titulo') or ''} {r.get('objeto') or ''} {re.sub(r'[-_/.]', ' ', str(r.get('url') or ''))}"
    if LEGISLATIVO_ABERTAS.search(t) and not re.search(r"(?i)emenda parlamentar.{0,60}capta[çc][ãa]o", t):   # 16/10: emenda em captação é oportunidade
        return "ato legislativo — vai ao acompanhamento legislativo (Oportunidades Abertas › Legislativo)"
    tit = str(r.get("titulo") or "")
    _ag = AGREGADOR_HOST.match(str(r.get("url") or ""))
    if PAGINA_DE_AGREGADOR.search(str(r.get("url") or "")) or (_ag and not re.search(r"(?i)capta|edita|oportunidad|chamad|premi|fomento|noticia|/20\d\d/", _ag.group(1) or "")):
        return "página institucional ou comercial do agregador — não é oportunidade"   # 15/10 (ciclo 7): só captação/edital vale
    # 17/10/2026 (titular, portão com casos reais): ruído que a migração mostrou passando pelo portão
    if not re.search(r"(?i)sociedade civil|\bosc\b|organiza[çc][õo]es? da sociedade|associa[çc][õo]es|cooperativas? de catadores|entidades? sem fins", t):
        if re.search(r"(?i)prospec[çc][ãa]o (do mercado )?imobili|im[óo]vel para loca[çc][ãa]o|loca[çc][ãa]o de im[óo]vel", t):
            return "prospecção/locação de imóvel — compra pública, não é fomento"
        if re.search(r"(?i)credenciamento de (pessoa jur[íi]dica|empresas?)|cadastrar empresas|empresas? (especializadas?|sediadas)", t):
            return "credenciamento/cadastro de empresas — não é fomento a OSC"
        if re.search(r"(?i)aquisi[çc][ãa]o de g[êe]neros|g[êe]neros aliment[íi]cios", t):
            return "aquisição de gêneros — compra pública"
        if re.search(r"(?i)m[ãa]o de obra|torneiro|soldador|presta[çc][ãa]o de servi[çc]os de (administra|gerenciamento|limpeza|vigil)", t):
            return "contratação de serviço/mão de obra — não é fomento"
        if re.search(r"(?i)concess[ãa]o de incentivos? (fiscais? )?(a|para) empresas|empresas para concess[ãa]o de incentivo", t):
            return "incentivo a empresas — não é para associação"
    if re.search(r"(?i)^\s*presta[çc][ãa]o de contas\b", tit):
        return "prestação de contas — não é oportunidade"
    # 17/10/2026 (amostra dos 744 achados fora dos livros): EXTRATO de parceria já firmada e ato de execução não são
    # oportunidade — o DOU publicava centenas como "achado"
    if re.search(r"(?i)\bextrato (?:de |do |da )?(?:termo|contrato|conv[eê]nio|compromisso|doa[çc][ãa]o|distrato|prorroga|"
                 r"apostilamento|rescis|aditiv|acordo|parceria|autoriza)|\bextrato_aditivo|\bdistrato\b|prorroga[çc][ãa]o de of[íi]cio|"
                 r"^\W*termo aditivo\b|apostilamento", tit):
        return "extrato/ato de execução de parceria já firmada — não é oportunidade"
    if re.search(r"(?i)\bextratos? (?:de |do |da |dos |das )?(?:fomento|colabora[çc][ãa]o|termos?\b)|parceria celebrada|"
                 r"dispensa de chamamento|inexigibilidade|resultado de julgamento|^\W*(?:\S+ — )?(?:aviso de )?retifica[çc][ãa]o\W*$|"
                 r"aviso de prorroga[çc][ãa]o\W*$", tit):
        return "extrato/resultado/dispensa de parceria — ato de execução, não é oportunidade"
    if re.search(r"(?i)convoca[çc][ãa]o (?:de|para) assembl|assembleia geral (?:ordin|extraordin)|edital de convoca[çc][ãa]o de assembl|"
                 r"\bbazar\b", tit):
        return "assembleia/bazar — não é oportunidade"
    if OS_CONTRATO_DE_GESTAO.search(t) and not re.search(r"(?i)sociedade civil|\bosc", tit):   # 16/10: só OS de verdade
        return "Organização Social (contrato de gestão) — acompanhar, não é oportunidade da associação"
    if "credenciamento" in t.lower() and SAUDE_SERVICO.search(f"{t} {r.get('orgao') or ''}") and not re.search(r"(?i)sociedade civil|\bosc", tit):
        return "credenciamento de prestadores — não é fomento a OSC"
    if not r.get("fim") and ANO_ANTERIOR.search(tit) and not re.search(r"\b202[6-9]\b", tit):
        return "edital de ano anterior, sem prazo vigente"
    for rx, motivo in NAO_OPORTUNIDADE:
        if rx.search(tit if "listagem" in motivo else t):
            if "credenciamento" in motivo and PERMITE_CREDENCIAMENTO.search(t) and not SAUDE_SERVICO.search(t):
                continue                                   # credenciamento de OSC para parceria vale; serviço de saúde, não
            return motivo
    return None


# — repositorio_unico.py · municipio_pelo_endereco
def municipio_pelo_endereco(url: str) -> bool:
    """16/10/2026: o rótulo do endereço só indica município quando É um município daquele estado (lista do IBGE) —
    'mapacultural.pe.gov.br' é a plataforma ESTADUAL de Pernambuco, não um município."""
    m = re.search(r"https?://(?:[\w-]+\.)*?([\w-]+)\.([a-z]{2})\.(?:gov|leg)\.br", str(url or ""))
    if not (m and m.group(2).upper() in UFS) or _ROTULO_ESTADUAL.match(m.group(1)):
        return False
    if not _MUN_POR_UF:
        for nome, ufs in ((_j(ROOT / "config/missao/municipios_brasil.json", {}) or {}).get("municipios") or {}).items():
            for u in ufs:
                _MUN_POR_UF.setdefault(u, set()).add(re.sub(r"[^a-z]", "", nome))
        _MUN_POR_UF.setdefault("-", set())
    return re.sub(r"[^a-z]", "", m.group(1).lower()) in _MUN_POR_UF.get(m.group(2).upper(), set())


# — repositorio_unico.py · uf_por_municipio
def uf_por_municipio(texto: str) -> str | None:
    """15/10 (ciclo 4): UF pelo NOME do município (lista do IBGE) quando o texto diz 'Prefeitura/Município/Câmara/Diário
    Oficial de X' ou 'X (UF)'; homônimos em mais de um estado não decidem (fica sem UF)."""
    import unicodedata
    sem = lambda s: "".join(c for c in unicodedata.normalize("NFD", str(s or "").lower()) if unicodedata.category(c) != "Mn")
    t = sem(texto)
    m = re.search(r"\(([a-z]{2})\)", t)
    if m and m.group(1).upper() in UFS and re.search(r"(?i)prefeitura|munic[íi]pio|di[áa]rio oficial de|c[âa]mara", texto):
        return m.group(1).upper()
    if not _MUN_BR:
        _MUN_BR.update((_j(ROOT / "config/missao/municipios_brasil.json", {}) or {}).get("municipios") or {"-": []})
    _ed = re.match(r"\s*edital (?:de |do |da )?([a-z' -]{3,40}?) 20\d\d\b", t)          # 15/10 (ciclo 7): "Edital Itagibá 2026"
    if _ed:
        if not _MUN_BR:
            _MUN_BR.update((_j(ROOT / "config/missao/municipios_brasil.json", {}) or {}).get("municipios") or {"-": []})
        _u = _MUN_BR.get(_ed.group(1).strip())
        if _u and len(_u) == 1:
            return _u[0]
    for mm in re.finditer(r"(?:prefeitura(?: municipal)?|municipio|camara municipal|diario oficial|fundo municipal de [a-z ]{3,30}?) de ([a-z' -]{3,40})", t):
        nome = mm.group(1).strip()
        for k in range(len(nome.split()), 0, -1):          # o nome mais longo que existir na lista
            cand = " ".join(nome.split()[:k])
            ufs = _MUN_BR.get(cand)
            if ufs:
                return ufs[0] if len(ufs) == 1 else None
    return None


# — repositorio_unico.py · municipal_fora_de_goias
def municipal_fora_de_goias(r: dict, uf_agregador: str | None = None) -> str | None:
    """Identifica oportunidade MUNICIPAL de fora de Goiás (UF determinada e diferente de GO). 14/10/2026 (titular): roda a
    CADA rodada — só Goiás tem oportunidades municipais; de outros estados, só estaduais (e nacionais/internacionais).
    A municipal de outro estado é DESCARTADA do sistema (estado fechada: sai das abertas, da tela, das filas e não ganha
    livro). Sem UF determinada, fica (há municípios homônimos)."""
    t = f"{r.get('titulo') or ''} {r.get('orgao') or ''}"
    _do = re.search(r"(?i)di[áa]rio oficial d[eoa] ([\wÀ-ú' -]{3,40}?) \(([A-Z]{2})\)", t)   # 17/10: "Diário Oficial de X (UF)"
    if _do and _do.group(2).upper() not in ("GO", "DF") and \
            re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", _do.group(1)).encode("ascii", "ignore").decode().lower()) not in _CAPITAIS_SEM_ESPACO:
        return f"município de outro estado ({_do.group(2).upper()}, não capital)"
    # 16/10/2026: órgão ESTADUAL nunca é municipal (a menos que o texto traga a prefeitura); o DF inteiro é a capital
    if re.search(r"(?i)secretaria (?:de|da) estado|governo d[eo] estado|governo de (?!munic)|do estado d[eo]|\bestadual\b|"
                 r"\bsecult[- ](?:[a-z]{2})\b|assembleia legislativa|tribunal de justi[çc]a|minist[ée]rio p[úu]blico", t) \
            and not re.search(r"(?i)prefeitura|munic[íi]pio d[eoa]|c[âa]mara municipal|secretaria municipal|fundo municipal", t):
        return None
    if str(r.get("uf") or "").upper() == "DF" or re.search(r"(?i)\bdistrito federal\b|\bbras[íi]lia\b", t):
        return None
    municipal = str(r.get("nivel") or "").lower() == "municipal" or bool(_MUN.search(t)) or \
        any(municipio_pelo_endereco(u) for u in (r.get("url"), r.get("link_oficial")))   # 15/10: pelo endereço
    if not municipal or str(r.get("nivel") or "").lower() in ("estadual", "federal", "internacional"):
        return None
    if _municipio_goiano(f"{r.get('orgao') or ''} {r.get('titulo') or ''}"):
        return None                                    # 14/10: cita um dos 246 municípios de Goiás → é de Goiás (fica)# 14/10 (titular): municipais das CAPITAIS de outros estados ficam
    if capital_citada(f"{r.get('orgao') or ''} {r.get('titulo') or ''} {r.get('url') or ''}"):
        return None
    for _u in (r.get("url"), r.get("link_oficial")):     # 16/10: a capital também pelo ENDEREÇO (palmas.to.gov.br)
        _m = re.search(r"https?://(?:[\w-]+\.)*?([\w-]+)\.([a-z]{2})\.(?:gov|leg)\.br", str(_u or ""))
        if _m and re.sub(r"[^a-z]", "", _m.group(1)) in _CAPITAIS_SEM_ESPACO:
            return None
    uf = str(r.get("uf") or uf_agregador or "").upper()
    if uf == "BR":                                     # 17/10: "BR" é nacional, não é estado
        uf = ""
    if uf not in UFS:
        uf = uf_por_municipio(f"{r.get('titulo') or ''} {r.get('orgao') or ''}") or uf
    if uf not in UFS:
        m = _DOM_UF.search(f"{r.get('link_oficial') or ''} {r.get('url') or ''}")
        uf = m.group(1).upper() if m and m.group(1).upper() in UFS else ""
    if uf not in UFS:                                  # nome do estado por extenso no endereço ou no título (um só)
        txt = re.sub(r"[-_/]", " ", f"{r.get('url') or ''} {r.get('link_oficial') or ''} {r.get('titulo') or ''}".lower())
        achados = {sig for nome, sig in _ESTADOS if nome not in ("para", "pará", "acre") and re.search(rf"\b{nome}\b", txt)}   # 14/10: "para" é preposição
        if len(achados) == 1:
            uf = achados.pop()
    if uf and uf != "GO":
        # 17/10/2026 (titular): SEM CIDADE VERIFICADA NÃO SE ELIMINA — deve ser estadual. Só sai quando o município é
        # NOMEADO (no texto ou no endereço do site oficial); "Chamamento Público nº 005/2026 (BA)" sem cidade fica.
        _cid = cidade_verificada(r)
        if not _cid:
            return None
        if _cid not in ("nomeado no texto",) and _municipio_goiano(f"município de {_cid}"):
            return None                                # a cidade nomeada é de Goiás: fica
        return f"arquivada: municipal fora de Goiás ({uf}) — o livro fica guardado na Biblioteca"
    return None


# — repositorio_unico.py · cidade_verificada
def cidade_verificada(r: dict) -> str | None:
    """O nome do município, quando o texto ou o endereço do site oficial o NOMEIA; senão None (não se elimina)."""
    t = f"{r.get('titulo') or ''} {r.get('orgao') or ''}"
    m = _CIDADE_NOMEADA.search(t)
    if m:
        nome = re.split(r"\s+[-—–(|:,]|\s+-\s+|\s{2,}", m.group(1).strip())[0].strip()
        if len(re.sub(r"[^A-Za-zÀ-ú]", "", nome)) >= 3 and not re.match(r"(?i)(?:estado|uni[ãa]o|governo|munic|prefeitura)\b", nome):
            return nome
    if uf_por_municipio(t):                            # cita pelo nome um município conhecido
        return "nomeado no texto"
    # PELO ENDEREÇO DO SITE OFICIAL: a parte do domínio é o NOME de um município daquela UF (lista do IBGE) — juatuba.mg.gov.br
    # é a Prefeitura de Juatuba; fapesc.sc.gov.br não (FAPESC não é município). Não vale para fonte/entidade nacional
    # (ABCR, Querido Diário, associação, instituto, fundação): a página guardada no livro dela é só exemplo.
    if re.search(r"(?i)querido di[áa]rio|\babcr\b|associa[çc][ãa]o|instituto|funda[çc][ãa]o|— oportunidades", t) and not _MUN.search(t):
        return None
    if not _MUN_BR:
        _MUN_BR.update((_j(ROOT / "config/missao/municipios_brasil.json", {}) or {}).get("municipios") or {"-": []})
    import unicodedata as _ud
    _sem = lambda x: re.sub(r"[^a-z]", "", _ud.normalize("NFKD", str(x)).encode("ascii", "ignore").decode().lower())  # noqa: E731
    for u in (r.get("url"), r.get("link_oficial")):
        _m = re.search(r"https?://(?:[\w-]+\.)*?([a-z-]{3,})\.([a-z]{2})\.(?:gov|leg)\.br", str(u or ""))
        if not _m or _m.group(2) == "go":
            continue
        rot, ufd = _sem(_m.group(1)), _m.group(2).upper()
        if not _MUN_POR_ROTULO:
            for nome, ufs in _MUN_BR.items():
                _MUN_POR_ROTULO.setdefault(_sem(nome), []).append((nome, set(ufs if isinstance(ufs, list) else [ufs])))
        for nome, ufs in _MUN_POR_ROTULO.get(rot, []):
            if ufd in ufs:
                return nome
    return None


# — regra_abrangencia.py · _sem
def _sem(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", str(s or "").lower()) if not unicodedata.combining(c))


# — regra_abrangencia.py · _capitais
@lru_cache(maxsize=1)
def _capitais() -> dict:
    T = json.loads((ROOT / "config/missao/territorio_goias.json").read_text(encoding="utf-8"))
    return {_sem(v["capital"]): uf for uf, v in (T.get("outros_estados") or {}).items() if v.get("capital")}


# — regra_abrangencia.py · capital_citada
def capital_citada(texto: str) -> str | None:
    """UF da capital de outro estado citada como município ('prefeitura/município/câmara/diário oficial de X' ou
    'X/UF', 'X (UF)', 'X - UF'); None se não houver."""
    t = _sem(texto)
    for cap, uf in _capitais().items():
        c = re.escape(cap)
        if re.search(rf"\b(?:prefeitura|municipio|camara|diario oficial|secretaria municipal [a-z ]{{0,40}})(?: municipal)? (?:de |do |da )?{c}\b", t) \
                or re.search(rf"\b{c}\s*(?:[-/(—–]\s*){uf.lower()}\b", t) \
                or re.search(rf"\b(?:secretaria|fundacao|fundo|instituto|agencia) municipal\b.{{0,80}}\b{c}\b|\b{c}\b.{{0,40}}\bmunicipal\b", t):
            return uf                                  # 16/10: "Secretaria Municipal de Cultura — São Paulo", "MUNICIPIO DE CURITIBA"
            return uf
    return None


# — atos_diario.py · sem_acento
def sem_acento(t: str) -> str:
    t = unicodedata.normalize("NFKD", t or "")
    return "".join(c for c in t if not unicodedata.combining(c))


# — pncp_osc.py · _N
def _N(t) -> str:
    return sem_acento(str(t or "")).upper()


# — pncp_osc.py · portao_associacao
def portao_associacao(m: dict, T: str) -> str | None:
    """15/10/2026 (titular): o motivo de RUÍDO quando a publicação não é captação de recursos para associação."""
    T = T.replace("CREDECIAMENTO", "CREDENCIAMENTO")
    if re.search(r"CONTRATACAO DE VAGAS|CONTRATAC(?:AO|OES) ONEROSA(?! DE ASSOCIAC)", T) and \
            not re.search(r"ACOLHIMENTO|LONGA PERMANENCIA|\bILPIS?\b|COMUNIDADES? TERAPEUTIC", T):   # ILPI: a regra própria decide
        return "contratação de vagas ou serviço (contrato) — não é captação de recursos para associação"
    if re.search(r"\bESTUDANTES?\b|\bALUNOS?\b|ENSAIOS? FOTOGRAFIC|FOTOGRAFOS?|PARLAMENTO JOVEM|PARLAMENTO EM ACAO", T) \
            and not re.search(r"ORGANIZAC(?:AO|OES) DA SOCIEDADE CIVIL|\bOSCS?\b|ASSOCIAC(?:AO|OES)|ENTIDADES?|GREMIOS?", T):
        return "seleção para pessoas físicas (estudantes, fotógrafos) — não é captação para associação"
    mod = _N(m.get("modalidade"))
    # 15/10 (expurgo): parceria com OSC também é publicada no PNCP como dispensa/inexigibilidade e cita "serviços" —
    # com sinal FORTE de MROSC, os vetos de modalidade, compra e PNAE não se aplicam (território e pessoa física, sim)
    osc_forte = bool(re.search(r"13\.?019|TERMO DE (?:FOMENTO|COLABORACAO)|ORGANIZAC(?:AO|OES) DA SOCIEDADE CIVIL|\bOSCS?\b|MROSC|"
                               r"TERMO DE EXECUCAO CULTURAL", T))
    if not osc_forte and re.search(r"PREGAO|CONCORRENCIA|LEILAO|DIALOGO COMPETITIVO|\bDISPENSA\b", mod):
        return f"modalidade de compra ({m.get('modalidade')}) — licitação, não captação de recursos para associação"
    if not osc_forte and COMPRA.search(T) and not re.search(r"DOACAO|TERMO DE (?:FOMENTO|COLABORACAO)|PREMIO|PREMIACAO", T):
        return "compra, fornecimento ou contratação de empresa — licitação, não captação de recursos para associação"
    if re.search(r"JORNALIS|PREMIO DE COMUNICACAO|PREMIO DE REPORTAGEM|TRABALHOS ACADEMICOS|MONOGRAFIAS?|SERVIDORES PUBLICOS", T) \
            and not re.search(r"ORGANIZAC(?:AO|OES) DA SOCIEDADE CIVIL|\bOSCS?\b|ASSOCIAC(?:AO|OES)|ENTIDADES?", T):
        return "prêmio ou seleção para pessoas físicas (jornalistas, pesquisadores, servidores) — não é captação para associação"
    if PNAE.search(T) and not osc_forte and not re.search(r"(?:AUTORIZACAO|CESSAO|PERMISSAO|CONCESSAO) DE USO", T):
        return "compra da agricultura familiar (PNAE) — não é captação de recursos para associação"
    uf_ = str(m.get("uf") or "").upper()
    mun_ = _N(m.get("municipio")) or (lambda mo: mo.group(1).strip() if mo else "")(
        re.search(r"(?:MUNICIPIO|PREFEITURA MUNICIPAL|CAMARA MUNICIPAL|FUNDO MUNICIPAL DE [A-Z ]{3,40}?) DE ([A-Z ]{3,40})", _N(m.get("orgao"))))
    goias_ou_capital = uf_ == "GO" or mun_ in CAPITAIS_N
    if re.search(r"CREDENCIAMENTO|CONTRATACAO DE VAGAS", T) and re.search(r"ACOLHIMENTO|LONGA PERMANENCIA|\bILPIS?\b|COMUNIDADES? TERAPEUTIC", T) \
            and not re.search(r"EMPRESAS? ESPECIALIZADA|PESSOAS? FISICA|PROFISSIONA(?:L|IS) D", T):
        # 15/10/2026 (titular): ILPI, acolhimento e comunidade terapêutica FICAM — só em Goiás e nas capitais
        return None if goias_ou_capital else "credenciamento de ILPI/acolhimento/comunidade terapêutica fora de Goiás e das capitais"
    if "CREDENCIAMENTO" in T and re.search(r"PRESTACAO DE SERVICOS?|ATENDIMENTO (?:A|DE|AOS?)|VAGAS?|SERVICOS? DE SAUDE|SERVICOS? MEDIC|RESIDENCIA", T) \
            and not re.search(r"TERMO DE (?:FOMENTO|COLABORACAO)|13\.019|DOACAO|PREMIO|PREMIACAO|RECICLA|CATADOR", T):
        return "credenciamento de entidade para prestar serviço remunerado (contrato, Lei 14.133) — não é captação de recursos"
    uf, mun = str(m.get("uf") or "").upper(), _N(m.get("municipio"))
    if not mun:                                          # "MUNICIPIO DE NAZARENO" no nome do órgão
        mo = re.search(r"(?:MUNICIPIO|PREFEITURA MUNICIPAL|CAMARA MUNICIPAL|FUNDO MUNICIPAL DE [A-Z ]{3,40}?) DE ([A-Z ]{3,40})", _N(m.get("orgao")))
        mun = mo.group(1).strip() if mo else ""
    municipal = m.get("esfera") == "M" or bool(re.search(r"MUNICIPIO|PREFEITURA|FUNDO MUNICIPAL|CAMARA MUNICIPAL|SECRETARIA MUNICIPAL|"
                                                          r"CONSORCIO (?:INTER)?MUNICIPAL|CONSORCIO MULTIFINALITARIO|CONSORCIO PUBLICO", _N(m.get("orgao"))))
    if municipal and uf and uf != "GO" and mun not in CAPITAIS_N:
        return f"município de outro estado ({mun.title() or '?'}/{uf}) — municipais só de Goiás e das capitais"
    return None


# — pncp_osc.py · veredito_por_titulo
def veredito_por_titulo(titulo: str, url: str = "", uf: str | None = None, fim: str | None = None) -> str | None:
    """15/10/2026: o MESMO portão para registros antigos do PNCP (só título, órgão e UF): devolve o motivo de ruído."""
    orgao, _, obj = str(titulo or "").partition(" — ")
    uf = uf or uf_por_municipio(orgao)
    mo = re.search(r"(?:MUNICIPIO|PREFEITURA MUNICIPAL|CAMARA MUNICIPAL|FUNDO MUNICIPAL DE [A-Z ]{3,40}?) DE ([A-Z ]{3,40})", _N(orgao))
    m = {"titulo": titulo, "objeto": obj or titulo, "orgao": orgao, "uf": uf, "municipio": mo.group(1).title() if mo else None,
         "esfera": "M" if re.search(r"MUNICIP|PREFEIT|CAMARA MUNICIPAL|CONSORCIO", _N(orgao)) else None, "encerramento": fim}
    return portao_associacao(m, _N(f"{titulo}"))
