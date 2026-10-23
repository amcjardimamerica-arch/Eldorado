"""A certificação: cada item no texto oficial, com o valor, o trecho e a página.

Primeira versão, por padrões de texto; a leitura avançada (Fase 5) e o Interceptador (Fase 8) a completam.
Regras: só o texto literal das páginas é prova; o trecho é guardado com a página; um item já comprovado não é
recertificado; dispensa só com justificativa válida (nunca para o núcleo); nada é sobrescrito.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from ..missao import itens as I
from ..nucleo.eventos import Diario, agora

MES = r"(?:janeiro|fevereiro|março|marco|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)"
DATA = (r"(\d{1,2}/\d{1,2}(?:/\d{2,4})?|\d{4}-\d{2}-\d{2}|\d{1,2}º?\s+de\s+" + MES + r"(?:\s+de\s+\d{4})?)")
HORA = r"(?:(?:às?|as|das?)\s*\d{1,2}\s*h\s*\d{0,2}(?:min)?\s*(?:do dia\s*)?)?"
DATA2 = DATA + r"\s*(?:,|e|a|até|ate|à|-|–|\s)\s*" + HORA + DATA
F = re.I | re.S
PADROES: dict[str, list[re.Pattern]] = {
    "Objeto": [re.compile(r"(?:tem (?:por|como) (?:objeto|objetivo|finalidade)(?: central| geral| principal)?|(?:do |o )?objeto(?: d[oa] (?:presente )?(?:edital|chamamento|chamada))?\s*[:–-]|"
                          r"objetivo(?: geral| central)?\s*[:–-]|(?:visa|visando|destina-se|destinado) (?:a |à )?)\s*(.{15,300}?)(?:[.;]\s|$)", F),
               re.compile(r"\b((?:selecionar|sele[çc][ãa]o de|apoiar|premiar|fomentar|financiar) (?:projetos|propostas|organiza[çc][õo]es|iniciativas|redes|"
                          r"entidades|a[çc][õo]es|osc|pont[õo]es|grupos|coletivos).{10,250}?)(?:[.;]\s|$)", F),
               re.compile(r"\b((?:concurso|pr[êe]mio|edital|chamada|chamamento)[^.;\n]{0,40}?(?:cultural|de projetos|de apoio|de fomento|p[úu]blic[oa])[^.;\n]{15,200})", F)],
    "Prazo de inscrição": [re.compile(r"(?:inscri[çc]|propostas?|prazo)[^\n]{0,80}?(?:encerrad[ao]s?|se encerr(?:ou|a)|encerrou-se|encerra-se|termina) em\s*" + DATA, F),
                           re.compile(r"(?:inscri[çc]|propostas?|candidaturas?|recebimento|submiss)[^\n]{0,200}?" + HORA + r"do dia\s*" + DATA + r"[^\n]{0,30}?até\s*" + HORA + r"(?:o dia\s*)?" + DATA, F),
                           re.compile(DATA + r"\s*(?:,\s*)?" + HORA + r"até o dia\s*" + HORA + DATA, F),re.compile(r"(?:inscri[çc]|propostas?|candidaturas?|cadastro|submiss[ãa]o|envio)[^\n]{0,200}?do dia\s*" + DATA + r"[^\n]{0,20}?até o dia\s*" + DATA, F),
                           re.compile(r"data(?: e hora)? (?:final|limite|de encerramento)[^\n]{0,40}?(?:das |de )?(?:propostas|inscri[çc][õo]es|envio)[^\n]{0,60}?" + DATA, F),
                           re.compile(r"(?:abertura|encerramento)\w*propostas?[^\n]{0,60}?" + DATA + r"[^\n]{0,40}?" + DATA, F),re.compile(r"(?:inscri[çc]|propostas?|candidaturas?|cadastro|solicita[çc][õo]es)[^\n]{0,120}?(?:de |entre |per[íi]odo:?\s*)?" + DATA2, F),
                           re.compile(r"(?:inscri[çc]|propostas?|candidaturas?|cadastro|solicita[çc][õo]es|recebimento)[^\n]{0,120}?(?:até|ate|a partir de|prazo[^\n]{0,30}?)\s*(?:às? \d{1,2}h\d{0,2}\s*(?:do dia )?)?" + DATA, F),
                           re.compile(r"(?:apresentar|enviar|encaminhar)[^\n]{0,80}?até\s*(?:às? \d{1,2}h\d{0,2}\s*(?:do dia )?)?" + DATA, F)],
    "Resultado": [re.compile(r"resultado(?:s)? (?:final|preliminar|provis[óo]rio|definitivo|da sele[çc][ãa]o)?[^\n]{0,80}?" + DATA, F)],
    "Prazo de recurso": [re.compile(r"recursos?[^\n]{0,100}?(\d{1,2} ?(?:\([a-zç ]+\))? ?dias? (?:[úu]teis|corridos)?)", F),
                         re.compile(r"(?:interposi[çc][ãa]o|apresenta[çc][ãa]o)(?: d[eo]s?)? recursos?[^\n]{0,80}?(?:até\s*)?" + DATA, F)],
    "Valor": [re.compile(r"(R\$ ?\d{1,3}(?:\.\d{3})*(?:,\d{2})?(?: ?(?:mil|milh(?:ão|ões|ao|oes)))?)", re.I)],
    "Órgão / financiador": [re.compile(r"((?:Secretaria|Prefeitura|Funda[çc][ãa]o|Minist[ée]rio|Instituto|Fundo|Governo|Ag[êe]ncia|Banco)"
                                       r"(?: (?:de|do|da|dos|das|Municipal|Estadual|Nacional|[A-ZÀ-Ú][\wÀ-ú-]+)){1,8})")],
    "Território": [re.compile(r"((?:Estado|Munic[íi]pio) d[eoa] [A-ZÀ-Ú][\wÀ-ú]+(?: [A-ZÀ-Ú][\wÀ-ú]+){0,3}|todo o territ[óo]rio nacional|"
                              r"em todo o (?:pa[íi]s|Brasil)|\bGoi[áa]s\b|\bGoiânia\b)", re.I)],
    "Esfera": [re.compile(r"\b(municipal|estadual|federal|nacional|internacional|privada)\b", re.I)],
    "Requisitos": [re.compile(r"(?:poder[ãa]o participar|quem pode participar\??|requisitos?(?: para| de)? (?:participa|inscri|habilita)[^:]{0,30}|s[ãa]o eleg[íi]veis|"
                              r"condi[çc][õo]es de participa[çc][ãa]o|poder[áa] (?:se inscrever|participar|concorrer))\s*[:–-]?\s*(.{15,300}?)(?:[.;]\s|$)", F),
                   re.compile(r"\b((?:possuam|possuir|estar habilitad[ao]|estejam? (?:regularmente )?(?:constitu[íi]d|cadastrad|habilitad)|constitu[íi]das? h[áa]|"
                              r"no m[íi]nimo \d+ \(?[a-z]*\)? anos? de (?:exist[êe]ncia|atua[çc][ãa]o|funcionamento)).{10,250}?)(?:[.;]\s|$)", F)],
    "Anexos": [re.compile(r"(anexo\s+[IVXL\d]+\b[^.;\n]{0,80})", re.I)],
    "Modalidade": [re.compile(r"\b(termo de fomento|termo de colabora[çc][ãa]o|termo de execu[çc][ãa]o cultural|termo de parceria|termo de compromisso(?: cultural)?|"
                              r"acordo de coopera[çc][ãa]o|conv[êe]nios?|pr[êe]mios?|premia[çc][ãa]o|bolsas?|patroc[íi]nio|emenda parlamentar|subven[çc][ãa]o|"
                              r"chamada de projetos|fomento à execu[çc][ãa]o de a[çc][õo]es culturais|apoio financeiro|doa[çc][ãa]o|credenciamento)\b", re.I)],
    "Área de atuação": [re.compile(r"\b(cultura|esporte|sa[úu]de|educa[çc][ãa]o|assist[êe]ncia social|meio ambiente|direitos humanos|"
                                   r"inclus[ãa]o|crian[çc]as? e adolescentes|idosos?|seguran[çc]a alimentar|habita[çc][ãa]o|ci[êe]ncia|"
                                   r"socioambiental|clima|bioeconomia|agroecol[óo]gic\w*|audiovisual|patrim[ôo]nio|juventude|mulheres|igualdade)\b", re.I)],
}
ESFERA_POR_ORGAO = [
    (re.compile(r"minist[ée]rio|governo federal|\buni[ãa]o\b|\bfnde\b|\bcnpq\b|\bcapes\b|\bfinep\b|\bbndes\b|\.gov\.br\b(?!/)|\bfederal\b", re.I), "federal"),
    (re.compile(r"secretaria de estado|governo d[eo] estado|\bestadual\b|assembleia legislativa", re.I), "estadual"),
    (re.compile(r"prefeitura|munic[íi]pio|\bmunicipal\b|c[âa]mara municipal", re.I), "municipal"),
    (re.compile(r"funda[çc][ãa]o|instituto|\bltda\b|\bs\.?a\.?\b|empresa|associa[çc][ãa]o|banco do brasil|\bong\b", re.I), "privada"),
]


def esfera_pelo_orgao(texto: str) -> tuple[str, str] | None:
    """A esfera quase nunca está escrita: é deduzida do órgão (com o trecho que a sustenta)."""
    for rx, esfera in ESFERA_POR_ORGAO:
        m = rx.search(texto)
        if m:
            return esfera, texto[max(0, m.start() - 60):m.end() + 60]
    return None


@dataclass
class Pagina:
    documento_id: int | str          # o número do documento no banco, ou a assinatura (documento ainda em registro)
    numero: int
    texto: str


def localizar(item: str, paginas: list[Pagina]) -> dict | None:
    """O primeiro trecho, na ordem das páginas, que comprova o item."""
    r = _localizar(item, paginas)
    if r is None and item == "Esfera":
        for p in paginas:
            e = esfera_pelo_orgao(p.texto)
            if e:
                return {"valor": e[0], "trecho": re.sub(r"\s+", " ", e[1]).strip()[:500], "pagina": p.numero, "documento_id": p.documento_id}
    return r


def para_busca(texto: str) -> str:
    """Junta números que a extração do PDF quebrou ("09 / 10 /202 6" → "09/10/2026"). Só para a busca: o trecho guardado é o original."""
    t = re.sub(r"(\d)\s*/\s*(\d)", r"\1/\2", texto)
    t = re.sub(r"\b(\d{3})\s(\d)\b", r"\1\2", t)
    return re.sub(r"[ \t]+", " ", t)


def _localizar(item: str, paginas: list[Pagina]) -> dict | None:
    for p in paginas:
        busca = para_busca(p.texto)
        for rx in PADROES[item]:
            m = rx.search(busca)
            if m:
                valor = re.sub(r"\s+", " ", m.group(m.lastindex or 0)).strip(" .;:–-")
                ini, fim = max(0, m.start() - 60), min(len(busca), m.end() + 60)
                trecho = re.sub(r"\s+", " ", busca[ini:fim]).strip()
                if len(valor) >= 3:
                    doc = {"documento_sha256": p.documento_id} if isinstance(p.documento_id, str) else {"documento_id": p.documento_id}
                    return {"valor": valor[:300], "trecho": trecho[:500], "pagina": p.numero, **doc}
    return None


class Certificacao:
    def __init__(self, diario: Diario):
        self.diario = diario

    def certificar(self, livro: str, paginas: list[Pagina], ja_resolvidos: set[str] = frozenset()) -> dict[str, dict]:
        novas: dict[str, dict] = {}
        for item in I.DOZE:
            if item in ja_resolvidos:
                continue
            achado = localizar(item, paginas)
            if achado:
                c = {"livro_id": livro, "item": item, "fase": "certificacao", "situacao": "comprovado", "em": agora(), **achado}
                self.diario.emitir("certidao.gravada", "certificacao", c)
                novas[item] = c
        return novas

    def dispensar(self, livro: str, item: str, justificativa: str) -> dict | None:
        if not I.dispensa_valida(item, justificativa):
            return None
        c = {"livro_id": livro, "item": item, "fase": "certificacao", "situacao": "dispensado", "justificativa": justificativa, "em": agora()}
        self.diario.emitir("certidao.gravada", "certificacao", c)
        return c
