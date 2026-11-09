"""O motor genérico de canal: um motor é uma CONFIGURAÇÃO (um arquivo TOML), sem código próprio.

A cada passagem, para cada fonte: acessa pela escada; vigia (página sem mudança não é relida); descobre as pistas pela
forma da fonte; pré-filtra pelo léxico; não entrega de novo; lê o documento oficial (texto literal, nunca o binário);
entrega o achado; e aprende com o retorno da Pertinência. Uma fonte com problema nunca derruba o motor: vira registro.
"""
from __future__ import annotations

import hashlib
import re
import tomllib
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Literal
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ...base.nucleo.contratos import Achado, Descricao, Motor, Plano, Retorno, Saude
from ..acesso.api import DegrauAPI
from ..acesso.arquivo_web import DegrauArquivo
from ..acesso.escada import Bloqueado, Escada, Indisponivel, Pendente
from ..acesso.leve import DegrauLeve
from ..acesso.local import DegrauLocal
from ..acesso.navegador import DegrauLightpanda, DegrauNavegador
from ..descoberta import arquivos_web, dados_abertos, estrutura_site, vigilancia
from ..descoberta.metabusca import Metabusca
from ..descoberta.pistas import Pista
from ..leitura import leitores
from ..leitura.pdf import LeitorPDF
from .estado import EstadoMotor

DOCUMENTO = re.compile(r"(?i)(?:\.(pdf|docx?|xlsx?|ods|odt|pptx|zip|7z|rar)|/pdf/?)(?:$|\?)")   # 08/11: ".../123/pdf" (APIs de legislação)
VISTA_PLONE = re.compile(r"(?i)(\.(?:pdf|docx?|xlsx?|ods|odt|pptx))/view/?$")   # 08/11/2026: "arquivo.pdf/view" → "arquivo.pdf"
# 08/11/2026 (parecer dos motores): o texto de link que não diz o que é ("Clique aqui e leia o edital", "Saiba mais sobre
# ...", "Doacao de bens.PDF") não é título de oportunidade. Na página, o link genérico é menu ou chamada de notícia e sai na
# entrada; no documento (PDF), o título vem da primeira linha do próprio documento que diz o que ele é.
TITULO_GENERICO = re.compile(r"(?i)^\s*(clique|clicando|leia|saiba|veja|confira|acesse|acessar|baixe|baixar|download|"
                             r"mais informa|ver mais|ler mais|aqui\b|link\b|anexo\s*[ivx\d]*\s*$|"
                             r"[\w ._-]{1,160}\.(pdf|docx?|odt|xlsx?)\s*$)")
NOME_DE_ARQUIVO = re.compile(r"(?i)^\s*[\w ._-]{1,160}\.(pdf|docx?|odt|xlsx?)\s*$")   # o título é o nome do arquivo: o link se lê
LINHA_DE_TITULO = re.compile(r"(?i)\b(edital|chamamento|chamada p[úu]blica|sele[çc][ãa]o|aviso|pr[êe]mio|doa[çc][ãa]o|credenciamento|"
                             r"cadastr|destina[çc][ãa]o)\b")


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CfgMotor(_Base):
    id: str
    nome: str
    categoria: str
    finalidade: str
    canal: Literal["api", "diario", "paginas", "portal"] = "paginas"
    uf: str | None = None
    orgao: str | None = None
    # a reorganização da titular (19/10/2026): a categoria do estudo e os nomes que o motor já teve ou os motores que ele
    # reúne; o histórico desses nomes é lido como do próprio motor (o motor leva o aprendizado dos que reúne)
    categoria_estudo: Literal["EXE", "JUD", "LEG", "POR", "IA"] | None = None
    tipo_finalidade: Literal["descoberta", "recorrencia"] = "descoberta"   # oportunidades novas, ou as edições de programas conhecidos
    destino: Literal["biblioteca", "especial"] = "biblioteca"   # especial: o motor entrega empresas e incentivos (a base Especial)
    nomes_anteriores: list[str] = Field(default_factory=list)
    # 09/11/2026 (titular, a organização dos 43 motores, R50): a posição do motor (1 a 43, a ordem de config/motores_previstos.json)
    # e o grupo (Diários oficiais, Legislativo, Judiciário, Ministério Público, Tribunais de Contas, Executivo municipal...)
    numero: int | None = Field(None, ge=1, le=99)
    grupo: str | None = None


class CfgPaginacao(_Base):
    inicio: int = 1
    maximo: int = Field(50, ge=1, le=1000)    # 27/10/2026: até o fim real (o total ou a página vazia), não 5 páginas
    total: str | None = None                  # onde está o total de páginas na resposta (jmespath)


class CfgElo(_Base):
    """Um elo da leitura em cadeia (descoberta/cadeia.py)."""
    formato: Literal["json", "html", "atos", "linhas"]
    itens: str = ""                         # jmespath (json), seletor CSS (html) ou o padrão dos cabeçalhos (atos; vazio = o padrão)
    campos: dict[str, str] = Field(default_factory=dict)
    url: str | None = None
    filtro: dict[str, str] = Field(default_factory=dict)
    limite: int = Field(5000, ge=1, le=20000)   # 27/10/2026: o diário lido até a última matéria (antes, 300)
    corpo: dict[str, str] = Field(default_factory=dict)


class CfgPistaCadeia(_Base):
    """Como os campos do último elo viram a pista: modelos com {campo}."""
    titulo: str
    link: str
    resumo: str | None = None
    texto: str | None = None             # o texto do ato já lido (o motor não baixa de novo o documento inteiro)


class CfgFonte(_Base):
    """Uma fonte. No endereço: {hoje:%Y%m%d}, {hoje-1:%d-%m-%Y}, {hoje+500:%Y%m%d}, {pagina} e cada chave de `valores`
    (uma consulta por combinação de valores)."""
    nome: str
    url: str
    tipo: Literal["pagina", "feed", "mapa", "wordpress", "ckan", "api", "metabusca", "wayback", "siconv", "cadeia"] = "pagina"
    seletor: str | None = None
    termos: str | None = None
    caminhos: dict[str, str] = Field(default_factory=dict)
    valores: dict[str, list[str | int]] = Field(default_factory=dict)
    paginacao: CfgPaginacao | None = None
    json_em: str | None = None                # o seletor EXATO do JSON dentro de uma página HTML
    exige_brasil: bool = False
    papel: Literal["principal", "alternativa"] = "principal"   # todo motor tem ao menos duas rotas: a principal e a alternativa
    cadeia: list[CfgElo] = Field(default_factory=list)          # tipo "cadeia": os elos, do primeiro (o endereço da fonte) ao último
    especial: dict[str, Any] = Field(default_factory=dict)      # destino especial: o mapa desta fonte (vale sobre o do motor)
    pista: CfgPistaCadeia | None = None
    # 08/11/2026: o filtro da fonte (campo → expressão): só seguem as pistas cujos campos casam — titulo, resumo, link ou
    # qualquer dado do item (orgao, uf, municipio, dono...). Ex.: o dono institucional de uma oportunidade do Mapa da Cultura.
    filtro: dict[str, str] = Field(default_factory=dict)
    # 09/11/2026 (R50, os motores reunidos): o destino e o léxico DESTA fonte, que valem sobre os do motor — o motor que reúne
    # outros mantém o filtro de cada fonte (o léxico do motor de origem) e a base de empresas (destino especial) dentro de
    # um motor da Biblioteca (o motor-gife reunido nos institutos empresariais)
    destino: Literal["biblioteca", "especial"] | None = None
    lexico: CfgLexico | None = None


class CfgAcesso(_Base):
    # o motor padrão: a escada completa (ela só sobe quando o degrau de baixo falha; ter todos não custa nada quando tudo
    # funciona e salva a leitura quando o site bloqueia ou só existe com script)
    degraus: list[Literal["api", "leve", "lightpanda", "patchright", "camoufox", "arquivo", "local"]] = [
        "api", "leve", "lightpanda", "patchright", "camoufox", "arquivo", "local"]
    intervalo_s: float = 1.0
    espera_seletor: str | None = None
    tentativas: int = Field(2, ge=1, le=3)
    # o tempo máximo de uma leitura do motor (24/10/2026: o motor das prefeituras levava mais de 19 min e segurava a
    # passagem inteira): passado o tempo, ele para entre uma fonte e outra e continua na próxima passagem (as fontes
    # lidas há mais tempo vêm primeiro)
    tempo_maximo_s: float = Field(1200, ge=30)   # 27/10/2026: 20 min por acionamento (+5 de folga na Regência)


class CfgLeitura(_Base):
    documentos: bool = True
    seguir_oficial: bool = False              # na página de divulgação, achar e ler o documento oficial do edital
    paginas_dos_achados: bool = False         # a página do achado como documento oficial (ex.: a íntegra da matéria do DOU)
    tabelas: Literal["nao", "uteis", "todas"] = "uteis"
    max_documentos: int = Field(20, ge=0, le=500)


class CfgLexico(_Base):
    """termos: no título e no resumo (basta um); vetos: só no título; salvos: título que nunca é vetado.
    Um item com o prefixo "re:" é uma expressão; a comparação é sempre sem acento e sem distinguir maiúsculas."""
    termos: list[str] = Field(default_factory=list)
    vetos: list[str] = Field(default_factory=list)
    salvos: list[str] = Field(default_factory=list)
    termos_em: Literal["tudo", "titulo"] = "tudo"   # "titulo": em sites de notícias, o título de um edital diz que é edital
    # 08/11/2026 (parecer dos motores): os filtros de ENTRADA, antes de qualquer leitura ou entrega.
    # idade_maxima_dias: a pista com data conhecida (a publicação do WordPress, o lastmod do mapa do site, o feed, a data da
    # API) mais velha que isto não entra (o mapa do site reabria o acervo de anos; sem data, a pista entra).
    idade_maxima_dias: int | None = Field(None, ge=1, le=3650)
    # territorio: "goias" aplica na entrada a mesma regra territorial do portão (R27: a municipal PÚBLICA de cidade de outro
    # estado que não é capital não entra); "livre" não filtra (as privadas e as nacionais ficam sempre).
    territorio: Literal["livre", "goias"] = "livre"


CfgFonte.model_rebuild()        # 09/11/2026: o léxico por fonte (CfgLexico é declarado depois de CfgFonte)


class CfgNormas(_Base):
    """Seguir, na página de legislação, os links das normas mais recentes (onde estão de fato os prazos e limites)."""
    padrao: str = "resolucao|instrucao normativa|portaria|decreto"
    excluir: str = "aprovad|resultado|homolog|habilitad|governanca|diario[ _-]?oficial|\\bdoe\\b|edicao|_pag_"
    maximo: int = Field(3, ge=1, le=10)


class CfgExtracao(_Base):
    """A análise própria do motor: para cada item, as expressões que reconhecem o valor no SEU tipo de texto (o primeiro
    grupo é o valor; sem grupo, o trecho todo). nao_certificar: os itens que a extração genérica não deve tentar nesse
    tipo de fonte (no texto de uma lei, a "data do resultado" seria a data da própria lei)."""
    itens: dict[str, list[str]] = Field(default_factory=dict)
    nao_certificar: list[str] = Field(default_factory=list)


class CfgAlvo(_Base):
    """Um ponto de captação vigiado pelo motor do seu canal (estudo da titular, 19/10/2026): lido na janela prevista da
    próxima edição. A previsão é aprendida pelo próprio motor (os meses em que o alvo mudou); a configurada vale antes."""
    id: str
    nome: str
    enderecos: list[str] = Field(min_length=1)       # o primeiro que funciona é a rota; os outros, as alternativas
    orgao: str | None = None
    previsao_meses: list[int] = Field(default_factory=list)
    seletor: str | None = None                        # a região do conteúdo (portais grandes: os menus não entram)


class CfgCanivete(_Base):
    """O motor padrão (titular, 23/10/2026): toda a caixa de ferramentas do plano ligada por padrão; um motor desliga o que
    não fizer sentido nele. As habilidades de leitura (OCR, leitor universal, navegador) estão na escada e na leitura;
    estas enriquecem cada achado (leitura/enriquecer.py)."""
    ligado: bool = True
    idioma: bool = True
    publicacao: bool = True
    datas: bool = True
    valores: bool = True
    metadados: bool = True
    texto_principal: bool = True
    arquivar: bool = True                   # arquivar no Wayback a página da oportunidade com prazo (a prova guardada)
    arquivar_por_execucao: int = Field(3, ge=0, le=20)
    ponte_br: bool = True                   # a ponte da HostGator (o IP brasileiro): na escada, depois dos degraus da nuvem
    # 08/11/2026 (R49): a segunda etapa de cada local — as subpáginas novas do domínio (o mapa do site; sem ele, o feed)
    subpaginas: bool = True
    subpaginas_janela_dias: int = Field(3, ge=1, le=30)
    subpaginas_por_dominio: int = Field(10, ge=1, le=50)

    def habilidades(self) -> tuple[str, ...]:
        return tuple(h for h in ("idioma", "publicacao", "datas", "valores", "metadados", "texto_principal") if getattr(self, h))


class CfgAprendizado(_Base):
    """O aprendizado mora dentro do motor (nunca no sistema); só o próprio motor (ou a titular) o altera."""
    licoes: list[str] = Field(default_factory=list)
    bloqueios_conhecidos: list[str] = Field(default_factory=list)
    alternativas_para_bloqueio: list[str] = Field(default_factory=list)
    rotas_que_falharam: list[str] = Field(default_factory=list)


class CfgMetrica(_Base):
    """A métrica da finalidade: ATINGE se leu dentro da cadência e entregou ao menos um achado aceito no período; NÃO
    ATINGE se ficou sem leitura além do dobro da cadência ou se todos os achados foram barrados."""
    cadencia_h: float = Field(24, gt=0)
    periodo_dias: int = Field(14, ge=1)
    # a fonte esporádica (25/10/2026): a finalidade é a vigilância sem erro (a fonte que só abre chamadas poucas vezes ao ano)
    esporadica: bool = False


class CfgPrograma(_Base):
    """A oportunidade é o próprio programa (incentivo fiscal, fundo, mecanismo permanente): o livro é relido sempre que
    a página oficial (a legislação, a norma vigente) muda, e o Cartório recertifica os itens a partir do texto oficial."""
    titulo: str
    orgao: str
    link_divulgacao: str
    link_oficial: str
    documentos: list[str]
    modalidade: str | None = None
    normas: CfgNormas | None = None
    extracao: "CfgExtracao | None" = None           # as regras de extração do texto das normas do programa (não valem para as outras fontes)


class CfgLegislacao(_Base):
    """As leis que regem o que o motor encontra (identificadores dos livros de leis da Biblioteca)."""
    leis: list[str] = Field(default_factory=list)
    notas: str | None = None


class Configuracao(_Base):
    motor: CfgMotor
    fonte: list[CfgFonte] = Field(default_factory=list)
    acesso: CfgAcesso = CfgAcesso()
    leitura: CfgLeitura = CfgLeitura()
    lexico: CfgLexico = CfgLexico()
    programa: CfgPrograma | None = None
    legislacao: CfgLegislacao = CfgLegislacao()
    extracao: CfgExtracao = CfgExtracao()
    alvo: list[CfgAlvo] = Field(default_factory=list)
    especial: dict[str, Any] = Field(default_factory=dict)   # destino especial: o mapa dos campos da empresa e do incentivo ({campo})
    canivete: CfgCanivete = CfgCanivete()
    aprendizado: CfgAprendizado = CfgAprendizado()
    metrica: CfgMetrica = CfgMetrica()
    alvos: dict[str, Any] = Field(default_factory=dict)
    metas: dict[str, Any] = Field(default_factory=dict)
    agenda: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _aceitavel(self) -> "Configuracao":
        """O registro recusa motor sem finalidade ou sem nenhuma rota (fonte, alvo ou programa)."""
        if not self.motor.finalidade.strip():
            raise ValueError("motor sem finalidade")
        if not (self.fonte or self.alvo or self.programa):
            raise ValueError("motor sem nenhuma rota (fonte, alvo ou programa)")
        return self


DATA_MODELO = re.compile(r"\{hoje(?P<d>[+-]\d+)?(?::(?P<f>[^}]+))?\}")


def hoje_local() -> date:
    """A data de hoje no fuso do Brasil (as edições e os prazos são do horário de Brasília)."""
    return datetime.now(ZoneInfo("America/Sao_Paulo")).date()


def preencher(modelo: str, hoje: date, valores: dict[str, Any] | None = None) -> str:
    """{hoje:%Y%m%d}, {hoje-1:%d-%m-%Y}, {hoje+500:%Y%m%d} e as chaves de `valores` ({pagina}, {mod}...)."""
    t = DATA_MODELO.sub(lambda m: (hoje + timedelta(days=int(m.group("d") or 0))).strftime(m.group("f") or "%Y-%m-%d"), modelo)
    for k, v in (valores or {}).items():
        t = t.replace("{" + k + "}", str(v))
    return t


def _agora() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _para_data(data: Any) -> date | None:
    """A data de uma pista (ISO, aaaa/mm/dd, dd/mm/aaaa, aaaammdd ou a do e-mail/RSS); desconhecida: None."""
    if not data:
        return None
    s = str(data).strip()
    try:
        if re.match(r"\d{4}[-/]\d{2}[-/]\d{2}", s):
            return date(int(s[:4]), int(s[5:7]), int(s[8:10]))
        if re.match(r"\d{2}/\d{2}/\d{4}", s):
            return date(int(s[6:10]), int(s[3:5]), int(s[:2]))
        if re.fullmatch(r"\d{8}(\d{6})?", s):
            return date(int(s[:4]), int(s[4:6]), int(s[6:8]))
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(s).date()
    except (ValueError, TypeError, IndexError):
        return None


def _idade_dias(data: Any) -> int | None:
    """A idade, em dias, de uma data de pista; desconhecida: None."""
    d = _para_data(data)
    return (hoje_local() - d).days if d else None


def _data_iso(data: Any) -> str | None:
    """08/11/2026: a data de publicação do achado sempre em ISO (aaaa-mm-dd). Antes ia o começo do texto da fonte
    ("Mon, 03 No", "05/11/2026", "2026/08/27"), e o Cartório perdia a edição (o ano é lido dos 4 primeiros caracteres)."""
    d = _para_data(data)
    return d.isoformat() if d else None


_MESES = {m: i for i, m in enumerate(("janeiro", "fevereiro", "marco", "abril", "maio", "junho", "julho", "agosto", "setembro",
                                        "outubro", "novembro", "dezembro"), 1)}


def _data_da_pagina(html: bytes | str | None, url: str) -> str | None:
    """08/11/2026: a data de publicação da página de divulgação (htmldate, a mesma do canivete), para a pista que veio sem
    data (as listas de links e as buscas HTML não trazem a data da notícia)."""
    if not html:
        return None
    try:
        from ..leitura.enriquecer import publicacao
        return publicacao(html.decode("utf-8", errors="replace") if isinstance(html, bytes) else html, url)
    except Exception:  # noqa: BLE001 — sem a data, a pista segue como antes
        return None


_MES_CURTO = {"jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6, "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12}


def _prazo_no_titulo(titulo: str) -> date | None:
    """O prazo que o próprio título declara ("até 22 de out. de 2026", "até o dia 5 de novembro de 2026", "até 30/11/2026");
    sem prazo no título: None."""
    s = _sem_acento(titulo)
    m = re.search(r"ate (?:o dia )?(\d{1,2})o? de ([a-z]{3})[a-z]*\.? de (\d{4})\b", s) or \
        re.search(r"ate (?:o dia )?(\d{1,2})/(\d{1,2})/(\d{4})\b", s)
    if not m:
        return None
    try:
        mes = int(m.group(2)) if m.group(2).isdigit() else _MES_CURTO.get(m.group(2))
        return date(int(m.group(3)), mes, int(m.group(1))) if mes else None
    except ValueError:
        return None


def _variantes_do_endereco(link: str) -> list[str]:
    """O endereço e as formas equivalentes: com e sem www., com e sem a barra final, http e https (o próprio primeiro)."""
    m = re.match(r"(?i)^(https?)://(www\.)?([^/?#]+)(.*)$", link or "")
    if not m:
        return [link]
    resto = m.group(4)
    sem_barra = resto.rstrip("/") if resto not in ("", "/") else resto
    com_barra = (resto + "/") if resto and not resto.endswith("/") and "?" not in resto and "#" not in resto else resto
    restos = {resto, sem_barra, com_barra}
    saida = [link]
    for esquema in ("https", "http"):
        for www in ("www.", ""):
            for r in restos:
                v = f"{esquema}://{www}{m.group(3)}{r}"
                if v not in saida:
                    saida.append(v)
    return saida


def _datar_pela_pagina(pista: Pista, html: bytes | str | None) -> None:
    """Dá à pista sem data a data de publicação lida na página. Não vale para o alvo vigiado: a data do portal não é a data
    de uma edição (viraria edição falsa no selo e na previsão do Cartório)."""
    if pista.data or str(pista.origem or "").startswith("alvo "):
        return
    data = _data_da_pagina(html, pista.link)
    if data:
        pista.data, pista.extra = data, {**(pista.extra or {}), "data_lida_na_pagina": True}


def _cita_data_recente(texto: str, limite_dias: int) -> bool:
    """O texto cita uma data dentro da janela (ou futura: o prazo de inscrição)? A trava contra a data errada da página:
    a notícia antiga só cita datas antigas; a página nova (ou republicada) cita o prazo de agora."""
    hoje = hoje_local()
    s = _sem_acento(texto or "")[:200000]
    for m in re.finditer(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b|\b(\d{1,2})o? de (" + "|".join(_MESES) + r") de (\d{4})\b", s, re.I):
        try:
            d = date(int(m.group(3)), int(m.group(2)), int(m.group(1))) if m.group(1) else \
                date(int(m.group(6)), _MESES[m.group(5).lower()], int(m.group(4)))
        except ValueError:
            continue
        if -3 * 366 <= (hoje - d).days <= limite_dias:
            return True
    return False


def _prefeitura_de_outro_estado(url: str) -> bool:
    """O endereço de prefeitura/câmara de outro estado que não é capital (cidade.uf.gov.br / cidade.uf.leg.br)."""
    m = re.match(r"https?://(?:www\.)?([\w-]+)\.([a-z]{2})\.(?:gov|leg)\.br", url or "", re.I)
    if not m or m.group(2).lower() in ("go", "df"):
        return False
    from ...base.missao.regras_portao import _CAPITAIS_SEM_ESPACO, uf_por_municipio
    cidade = m.group(1).lower()
    if re.sub(r"[^a-z]", "", cidade) in _CAPITAIS_SEM_ESPACO:
        return False
    # só quando o nome do subdomínio é de fato um município daquela UF (detran.rj.gov.br é órgão estadual: fica)
    return (uf_por_municipio(f"município de {cidade.replace('-', ' ')}") or "").upper() == m.group(2).upper()


def _titulo_do_documento(documento: dict | None) -> str | None:
    """A primeira linha do documento que diz o que ele é (edital, chamamento, aviso...), para o achado de título genérico."""
    if not documento:
        return None
    for pagina in documento.get("paginas") or []:
        for linha in str(pagina).splitlines()[:80]:
            linha = re.sub(r"\s+", " ", linha).strip(" -–:•")
            if 12 <= len(linha) <= 220 and LINHA_DE_TITULO.search(linha):
                return linha
    return None


def _sem_acento(t: str) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFKD", t.lower()) if not unicodedata.combining(c))


class MotorCanal(Motor):
    def __init__(self, configuracao: str | Path, dados: str | Path = "dados/motores", ponte: str | Path = "dados/ponte",
                 lightpanda: str | None = None, mirror_wayback: str | None = None):
        self.caminho = Path(configuracao)
        self.cfg = Configuracao(**tomllib.loads(self.caminho.read_text(encoding="utf-8")))
        self.estado = EstadoMotor(dados, self.cfg.motor.id, especial=self.cfg.motor.destino == "especial")   # o aprendizado, no Cérebro
        self.relatorio: list[str] = []
        self.escada = Escada(self._degraus(ponte, lightpanda, mirror_wayback), intervalo_padrao=self.cfg.acesso.intervalo_s,
                             tentativas=self.cfg.acesso.tentativas)
        self.leitura = leitores.padrao()
        from ..leitura.ocr import disponivel as ocr_disponivel
        self.leitura.registrar(LeitorPDF(tabelas=self.cfg.leitura.tabelas, ocr=ocr_disponivel()))
        self.relatorio: list[str] = []

    def _degraus(self, ponte, lightpanda, mirror):
        mapa = {"api": lambda: DegrauAPI(), "leve": lambda: DegrauLeve(),
                "lightpanda": lambda: DegrauLightpanda(binario=lightpanda, espera_seletor=self.cfg.acesso.espera_seletor),
                "patchright": lambda: DegrauNavegador("patchright", self.cfg.acesso.espera_seletor),
                "camoufox": lambda: DegrauNavegador("camoufox", self.cfg.acesso.espera_seletor),
                "arquivo": lambda: DegrauArquivo(mirror) if mirror else DegrauArquivo(), "local": lambda: DegrauLocal(ponte)}
        from ..acesso.ponte_br import DegrauPonteBR
        mapa["ponte"] = DegrauPonteBR
        nomes = list(self.cfg.acesso.degraus)
        if self.cfg.canivete.ponte_br and "ponte" not in nomes:      # a ponte no canivete (25/10/2026): depois da nuvem
            pesados = [nomes.index(d) for d in ("lightpanda", "patchright", "camoufox", "arquivo", "local") if d in nomes]
            nomes.insert(min(pesados) if pesados else len(nomes), "ponte")   # antes do primeiro degrau pesado
        degraus = []
        for d in nomes:
            try:
                degraus.append(mapa[d]())
            except Exception as e:  # noqa: BLE001 — o degrau que não pode ser montado aqui (o navegador ausente) é pulado
                self.relatorio.append(f"degrau {d} indisponível neste ambiente: {type(e).__name__}")
        return degraus

    # ------------------------------------------------------------------ contrato
    def descrever(self) -> Descricao:
        m = self.cfg.motor
        return Descricao(id=m.id, tipo="motor", parte="MOTORES", componente=f"Motores · {m.categoria}", finalidade=m.finalidade,
                         metrica="as 6 metas de qualidade (frescor, bloqueio, rendimento, precisão, cobertura dos alvos, prova)")

    def saude(self) -> Saude:
        return Saude(ok=bool(self.cfg.fonte), mensagem=f"{len(self.cfg.fonte)} fonte(s); degraus {', '.join(self.cfg.acesso.degraus)}")

    def planejar(self, plano: Plano) -> list[str]:
        return [f.nome for f in self.cfg.fonte] + list(plano.alvos)

    def painel(self) -> dict[str, Any]:
        return {**self.estado.painel(), "ultimo_relatorio": self.relatorio, "degraus_aprendidos": self.escada.aprendido}

    def aprender(self, retornos: list[Retorno]) -> None:
        for r in retornos:
            self.estado.retorno(r.achado, getattr(r, "fonte", None), r.decisao, r.motivo, _agora())

    # ------------------------------------------------------------------ busca
    def buscar(self, plano: Plano) -> Iterable[Achado]:
        self.relatorio = []
        if self.cfg.programa:
            achado = self._programa()
            if achado:
                yield achado
        import time as _t
        inicio_leitura = _t.monotonic()
        # as fontes lidas há mais tempo primeiro: o motor que parou pelo tempo máximo continua de onde parou
        fontes = sorted(self.cfg.fonte, key=lambda f: str(self.estado._fonte(f.nome).get("ultima") or ""))
        self.incompleto = False                  # 27/10/2026: o trabalho do dia não terminou; o Comandante aciona de novo
        self._barradas_na_entrada: dict[str, int] = {}
        for fonte in fontes:
            if _t.monotonic() - inicio_leitura > self.cfg.acesso.tempo_maximo_s:
                self.relatorio.append(f"tempo máximo ({self.cfg.acesso.tempo_maximo_s:.0f} s): as fontes restantes ficam para o próximo acionamento")
                self.incompleto = True
                return
            self._lexico_fonte = fonte.lexico                     # 09/11/2026 (R50): o léxico desta fonte, quando ela tem o próprio
            if self._lida_hoje(fonte.nome):                      # R49: cada local uma vez por dia
                self.relatorio.append(f"{fonte.nome}: já lida hoje (R49: uma leitura por dia em cada local)")
                continue
            try:
                pistas = self._descobrir(fonte)
            except Pendente as e:
                self.relatorio.append(f"{fonte.nome}: entregue ao computador local ({e})")
                self.estado.leitura(fonte.nome, _agora(), erro=f"pendente no computador local: {str(e)[:260]}")
                continue
            except (Bloqueado, Indisponivel, ValueError) as e:
                self.relatorio.append(f"{fonte.nome}: não lida ({e})")
                self.estado.leitura(fonte.nome, _agora(), erro=str(e)[:300])
                continue
            except Exception as e:  # noqa: BLE001 — uma fonte nunca derruba o motor (24/10/2026: as prefeituras caíram por um site)
                self.relatorio.append(f"{fonte.nome}: erro inesperado ({type(e).__name__}: {str(e)[:200]})")
                self.estado.leitura(fonte.nome, _agora(), erro=f"{type(e).__name__}: {str(e)[:250]}")
                continue
            if pistas is None:
                self.relatorio.append(f"{fonte.nome}: sem mudança desde a última leitura")
                self.estado.leitura(fonte.nome, _agora(), sem_mudanca=True)
                continue
            entregues = 0
            if (fonte.destino or self.cfg.motor.destino) == "especial":     # 09/11/2026 (R50): o destino da fonte vale sobre o do motor
                for pista in pistas:
                    a = self._registro_especial(fonte, pista)
                    if a is not None:
                        entregues += 1
                        yield a
                self.estado.leitura(fonte.nome, _agora(), achados=entregues)
                self.relatorio.append(f"{fonte.nome}: {len(pistas)} registro(s), {entregues} para a base Especial")
                continue
            proprios = {self.cfg.programa.link_divulgacao.rstrip("/"), self.cfg.programa.link_oficial.rstrip("/")} if self.cfg.programa else set()
            parou = False
            for pista in pistas:
                if _t.monotonic() - inicio_leitura > self.cfg.acesso.tempo_maximo_s:
                    # 27/10/2026: o tempo dentro de uma fonte grande (o diário): a fonte não é dada como lida e volta primeiro
                    self.relatorio.append(f"{fonte.nome}: tempo máximo no meio da fonte; o restante fica para o próximo acionamento")
                    self.incompleto, parou = True, True
                    break
                if pista.link.rstrip("/") in proprios:
                    continue                                        # o próprio programa já é entregue pela seção programa
                if not self._passa_entrada(pista) or self._ja_entregue(pista.link):
                    continue
                try:
                    achado = self._achado(fonte, pista, entregues)
                except Exception as e:  # noqa: BLE001 — um achado nunca derruba o motor: registrado, segue para o próximo
                    self.relatorio.append(f"{fonte.nome}: o achado {pista.link[:120]} falhou ({type(e).__name__}: {str(e)[:150]})")
                    continue
                if achado is None:
                    continue
                entregues += 1
                self.estado.marcar_entregue(pista.link, _agora(), achado.id, fonte.nome)
                yield achado
            if parou:
                return                                              # a fonte pela metade não é dada como lida: volta primeiro
            self.estado.leitura(fonte.nome, _agora(), achados=entregues)
            self.relatorio.append(f"{fonte.nome}: {len(pistas)} pista(s), {entregues} achado(s)")
        self._lexico_fonte = None                                # os alvos e as subpáginas: o léxico do motor
        yield from self._alvos()
        yield from self._subpaginas()
        if self._barradas_na_entrada:
            self.relatorio.append("barradas na entrada: " + "; ".join(f"{k} ({v})" for k, v in sorted(self._barradas_na_entrada.items(), key=lambda x: -x[1])))

    def _registro_especial(self, fonte: CfgFonte, pista: Pista) -> Achado | None:
        """Destino especial: a empresa e o incentivo, pelo mapa [especial] (modelos com os campos do item)."""
        from ..descoberta.cadeia import formatar
        item = (pista.extra or {}).get("_item") or {}
        def campo(v):
            return formatar(v, item).strip() if isinstance(v, str) else v
        mapa = fonte.especial or self.cfg.especial
        dados = {k: campo(v) for k, v in mapa.items() if k != "incentivo"}
        if isinstance(mapa.get("incentivo"), dict):
            dados["incentivo"] = {k: campo(v) for k, v in mapa["incentivo"].items()}
        if not dados.get("cnpj"):
            return None
        m = self.cfg.motor
        return Achado(id=f"{m.id}-{hashlib.sha256((dados['cnpj'] + fonte.nome).encode()).hexdigest()[:16]}", motor=m.id, encontrado_em=_agora()[:10],
                      link_divulgacao=fonte.url if fonte.url.startswith("http") else pista.link, link_oficial=pista.link or None,
                      titulo=str(dados.get("razao_social") or dados["cnpj"])[:200], dados={"especial": dados, "fonte": fonte.nome})

    def _na_janela(self, alvo: CfgAlvo, mes: int) -> bool:
        """A janela prevista da próxima edição: os meses configurados, ou os aprendidos (com 3 ou mais mudanças), com um
        mês de folga de cada lado; sem previsão, o alvo é lido sempre."""
        meses = set(alvo.previsao_meses) or (set(self.estado.meses_do_alvo(alvo.id)) if len(self.estado.meses_do_alvo(alvo.id)) >= 3 else set())
        return not meses or any(((mes - m) % 12) in (0, 1, 11) for m in meses)

    def _alvos(self) -> Iterable[Achado]:
        """Os pontos de captação vigiados: na janela, a primeira rota que funciona; mudou, registra o mês (a previsão se
        aprende) e entrega os links que passam no léxico, ou a própria página do alvo."""
        mes = int(_agora()[5:7])
        for alvo in self.cfg.alvo:
            # 08/11/2026: com o território de Goiás (R27), o alvo que é município de outro estado (não capital) não é lido —
            # os alvos "espalhados" do PNCP vigiavam prefeituras do RS, MT, CE, SE... (16 erros "fora da abrangência")
            if self.cfg.lexico.territorio == "goias":
                from ...base.missao.regras_portao import municipal_fora_de_goias
                if municipal_fora_de_goias({"titulo": alvo.nome, "orgao": alvo.orgao or "", "url": alvo.enderecos[0], "uf": None}) \
                        or _prefeitura_de_outro_estado(alvo.enderecos[0]):
                    self.relatorio.append(f"alvo {alvo.nome}: fora do território (município de outro estado, R27) — não lido")
                    continue
            if self._lida_hoje(f"alvo · {alvo.id}"):                 # R49: cada local uma vez por dia
                self.relatorio.append(f"alvo {alvo.nome}: já lido hoje (R49)")
                continue
            if not self._na_janela(alvo, mes):                     # R49 (titular, 08/11/2026): a janela prevista não impede a
                self.relatorio.append(f"alvo {alvo.nome}: fora da janela prevista — lido assim mesmo (R49)")   # leitura diária
            for n, url in enumerate(alvo.enderecos):
                fonte = CfgFonte(nome=f"alvo · {alvo.id}", url=url, tipo="pagina", papel="principal" if n == 0 else "alternativa", seletor=alvo.seletor)
                try:
                    pistas = self._descobrir(fonte)
                except (Bloqueado, Indisponivel, Pendente, ValueError) as e:
                    self.estado.leitura(fonte.nome, _agora(), erro=f"{url}: {str(e)[:250]}")
                    continue                                        # a próxima rota do alvo
                except Exception as e:  # noqa: BLE001 — um alvo nunca derruba o motor
                    self.estado.leitura(fonte.nome, _agora(), erro=f"{url}: {type(e).__name__}: {str(e)[:220]}")
                    self.relatorio.append(f"alvo {alvo.nome}: erro inesperado ({type(e).__name__})")
                    continue
                if pistas is None:
                    self.estado.leitura(fonte.nome, _agora(), sem_mudanca=True)
                    self.relatorio.append(f"alvo {alvo.nome}: sem mudança")
                    break
                self.estado.mudanca_do_alvo(alvo.id, _agora())
                entregues = 0
                # 08/11/2026: sem léxico próprio (termos), o alvo entrega só a própria página quando ela muda: colher todos os
                # links de um portal sem léxico entregava os menus inteiros (o Transferegov: 524 páginas institucionais)
                if not self.cfg.lexico.termos:
                    pistas = []
                for pista in pistas:
                    if self._passa_entrada(pista) and not self._ja_entregue(pista.link):
                        a = self._achado(fonte, pista, entregues)
                        if a is not None:
                            entregues += 1
                            self.estado.marcar_entregue(pista.link, _agora(), a.id, fonte.nome)
                            yield a
                if not entregues and not self.estado.ja_entregue(f"{url}#{_agora()[:7]}"):
                    a = self._achado(fonte, Pista(titulo=alvo.nome, link=url, origem=f"alvo {alvo.id} mudou"), 0)
                    if a is not None:
                        entregues += 1
                        self.estado.marcar_entregue(f"{url}#{_agora()[:7]}", _agora(), a.id, fonte.nome)
                        yield a
                self.estado.leitura(fonte.nome, _agora(), achados=entregues)
                self.relatorio.append(f"alvo {alvo.nome}: mudou ({entregues} achado(s))")
                break

    def _programa(self) -> Achado | None:
        """O livro do programa: entregue de novo só quando o texto oficial muda (nova norma, novo prazo)."""
        pr, m = self.cfg.programa, self.cfg.motor
        textos, alertas, origens, injecoes = [], [], [], []
        for i, url in enumerate(pr.documentos):
            try:
                bruto = self.escada.buscar(url).conteudo
                lido = self.leitura.ler(bruto, url)
                textos.append(lido.texto)
                origens.append(url)
                injecoes.append(lido.dados.get("injecao"))
            except (Bloqueado, Indisponivel, Pendente, leitores.SemLeitor) as e:
                alertas.append(f"{url}: {str(e)[:150]}")
                continue
            if i == 0 and pr.normas:                                   # as normas mais recentes da página de legislação
                from ..descoberta import fonte_oficial
                for n in fonte_oficial.normas_recentes(bruto, url, pr.normas.padrao, pr.normas.maximo, pr.normas.excluir):
                    try:
                        lido_n = self.leitura.ler(self.escada.buscar(n["url"]).conteudo, n["url"])
                        textos.append(lido_n.texto)
                        origens.append(n["url"])
                        injecoes.append(lido_n.dados.get("injecao"))
                    except (Bloqueado, Indisponivel, Pendente, leitores.SemLeitor) as e:
                        alertas.append(f"norma {n['texto'][:60]}: {str(e)[:120]}")
        if not textos:
            self.relatorio.append(f"programa: nenhum documento oficial lido ({'; '.join(alertas)})")
            self.estado.leitura("programa", _agora(), erro="; ".join(alertas)[:300])
            return None
        sha = hashlib.sha256("\n".join(re.sub(r"\s+", " ", t) for t in textos).encode()).hexdigest()
        chave = f"programa:{sha[:24]}"
        if self.estado.ja_entregue(chave):
            self.relatorio.append("programa: o texto oficial não mudou")
            self.estado.leitura("programa", _agora(), sem_mudanca=True)
            return None
        aid = f"{m.id}-programa-{sha[:12]}"
        self.estado.marcar_entregue(chave, _agora(), aid, "programa")
        self.estado.leitura("programa", _agora(), achados=1)
        self.relatorio.append(f"programa: texto oficial novo ou alterado ({len(textos)} documento(s))" + (f"; {len(alertas)} não lido(s)" if alertas else ""))
        return Achado(id=aid, motor=m.id, encontrado_em=_agora()[:10], link_divulgacao=pr.link_divulgacao, link_oficial=pr.link_oficial, titulo=pr.titulo,
                      dados={"uf": m.uf, "orgao": pr.orgao, "modalidade": pr.modalidade, "leis": self.cfg.legislacao.leis, "fonte": "programa",
                             "origem": "programa (legislação e norma vigente)", "documentos_lidos": origens,
                             **self._extrair(textos, pr.extracao)},
                      documento={"url": pr.link_oficial, "sha256": sha, "tipo": "html", "leitor": "programa (páginas oficiais)", "oficial": False,
                                 "paginas": textos, "alertas": alertas, "injecao": next((x for x in injecoes if x), None)})

    def _descobrir(self, f: CfgFonte) -> list[Pista] | None:
        pistas = self._descobrir_bruto(f)
        if pistas is None or not f.filtro:
            return pistas
        def campo(p: Pista, nome: str) -> str:
            return str({"titulo": p.titulo, "resumo": p.resumo, "link": p.link, "data": p.data}.get(nome) or (p.extra or {}).get(nome) or "")
        ficam = [p for p in pistas if all(re.search(rx, campo(p, nome), re.I) for nome, rx in f.filtro.items())]
        if len(ficam) < len(pistas):
            barradas = self.__dict__.setdefault("_barradas_na_entrada", {})
            barradas["filtro da fonte"] = barradas.get("filtro da fonte", 0) + len(pistas) - len(ficam)
        return ficam

    def _descobrir_bruto(self, f: CfgFonte) -> list[Pista] | None:
        buscar = self.escada.buscar
        if f.tipo in ("pagina", "feed", "mapa", "wordpress", "ckan") and "{hoje" in f.url:     # os modelos de data no endereço
            f = f.model_copy(update={"url": preencher(f.url, hoje_local())})
        if f.tipo == "pagina":
            r = buscar(f.url)
            ass = vigilancia.assinatura(r.conteudo, f.seletor)
            if not vigilancia.mudou(self.estado.assinatura(f.nome), ass):
                return None
            pistas = estrutura_site.links(lambda _u, r=r: r, f.url, seletor=f.seletor)
            self.estado.gravar_assinatura(f.nome, ass, _agora())
            return pistas
        if f.tipo == "feed":
            return estrutura_site.feed(buscar, f.url)
        if f.tipo == "mapa":
            return estrutura_site.mapa_do_site(buscar, f.url)
        if f.tipo == "wordpress":
            return estrutura_site.wordpress(buscar, f.url, f.termos)
        if f.tipo == "ckan":
            return dados_abertos.ckan(buscar, f.url, f.termos or "")
        if f.tipo == "api":
            return self._api(f)
        if f.tipo == "cadeia":
            return self._cadeia(f)
        if f.tipo == "siconv":
            return dados_abertos.siconv_programas(buscar, f.url, hoje_local().isoformat())
        if f.tipo == "wayback":
            from ..acesso.escada import dominio
            return arquivos_web.indice_wayback(buscar, dominio(f.url))
        pistas, relato = Metabusca(buscar, searxng=f.url or None).consultar(f.termos or "")
        self.relatorio.extend(f"{f.nome}: {x}" for x in relato)
        return pistas

    def _cadeia(self, f: CfgFonte) -> list[Pista] | None:
        """A leitura em cadeia: os itens do último elo viram pistas; sem nada novo desde a última leitura, None."""
        import hashlib

        from ..descoberta.cadeia import Elo, formatar, percorrer
        if not f.cadeia or f.pista is None:
            raise ValueError("fonte em cadeia sem elos ou sem o modelo da pista")
        relato: list[str] = []
        itens = percorrer(self.escada.buscar, preencher(f.url, hoje_local()), [Elo(**e.model_dump()) for e in f.cadeia], relato)
        self.relatorio.extend(f"{f.nome}: {x}" for x in relato[:10])
        pistas = [Pista(titulo=formatar(f.pista.titulo, i), link=formatar(f.pista.link, i), origem=f.nome,
                        data=str(i["data"]) if i.get("data") else None,   # 08/11/2026: a idade e a publicação também na cadeia
                        resumo=formatar(f.pista.resumo, i) if f.pista.resumo else None,
                        extra={**({"documento_texto": formatar(f.pista.texto, i)} if f.pista.texto else {}),
                               **{k: i[k] for k in ("orgao", "edicao", "data", "protocolo", "caminho", "localidade",   # 08/11: e o prazo,
                                                    "uf", "municipio", "cidade", "inicio", "fim", "valor") if i.get(k)},   # o lugar e o valor
                               **({"_item": {k: v for k, v in i.items() if k != "texto"}} if (f.destino or self.cfg.motor.destino) == "especial" else {})})
                  for i in itens]
        pistas = [p for p in pistas if p.titulo.strip() and p.link.startswith("http")]
        ass = hashlib.sha256("\n".join(sorted(p.link for p in pistas)).encode()).hexdigest()
        if pistas and ass == self.estado.assinatura(f.nome):
            return None
        self.estado.gravar_assinatura(f.nome, ass, _agora())
        return pistas

    def _api(self, f: CfgFonte) -> list[Pista]:
        """Uma consulta por combinação de valores, com paginação; a primeira falha de uma combinação não derruba as outras."""
        import itertools

        import jmespath
        hoje = hoje_local()
        chaves = list(f.valores)
        pistas: list[Pista] = []
        erros: list[str] = []
        for combinacao in itertools.product(*(f.valores[k] for k in chaves)) if chaves else [()]:
            vals = {k: preencher(str(v), hoje) for k, v in zip(chaves, combinacao, strict=True)}
            paginas = range(f.paginacao.inicio, f.paginacao.inicio + f.paginacao.maximo) if f.paginacao else [None]
            for pg in paginas:
                url = preencher(f.url, hoje, {**vals, **({"pagina": pg} if pg is not None else {})})
                try:
                    doc = dados_abertos.carregar_json(self.escada.buscar, url, f.json_em)
                except (Bloqueado, ValueError) as e:
                    curtos = {k: (str(v)[:30] + "…" if len(str(v)) > 30 else v) for k, v in vals.items()}
                    erros.append(f"{type(e).__name__}: {str(e)[:220]} · {url.split('?')[0]} {curtos}")   # o motivo primeiro
                    break
                novas = dados_abertos.pistas_da_api(doc, f.caminhos, f"{f.nome}")
                pistas += novas
                total = jmespath.search(f.paginacao.total, doc) if f.paginacao and f.paginacao.total else None
                if not novas or pg is None or (total is not None and pg >= int(total)):
                    break
        if erros:
            self.relatorio.extend(f"{f.nome}: {e}" for e in erros[:10])
        if erros and not pistas:
            raise Bloqueado("; ".join(erros[:3]))
        return pistas

    @staticmethod
    def _casa(texto: str, itens: list[str]) -> bool:
        for x in itens:
            if x.startswith("re:"):
                if re.search(_sem_acento(x[3:]), texto, re.I):
                    return True
            elif _sem_acento(x) in texto:
                return True
        return False

    def _extrair(self, paginas: list[str], ex: "CfgExtracao | None" = None) -> dict[str, Any]:
        """A extração própria do motor: o primeiro trecho, na ordem das páginas, que casa com a expressão de cada item."""
        ex = ex or self.cfg.extracao
        itens: dict[str, dict] = {}
        for item, padroes in ex.itens.items():
            for n, texto in enumerate(paginas, 1):
                t = re.sub(r"[ \t]+", " ", leitores.sem_ligaduras(texto))
                achou = next((m for rx in padroes if (m := re.search(rx, t, re.I | re.S))), None)
                if achou:
                    valor = re.sub(r"\s+", " ", achou.group(1) if achou.lastindex else achou.group(0)).strip(" .;:,–-")
                    trecho = re.sub(r"\s+", " ", t[max(0, achou.start() - 80):achou.end() + 80]).strip()
                    itens[item] = {"valor": valor[:300], "trecho": trecho[:500], "pagina": n}
                    break
        # o item que o motor declara como seu nunca vai para a extração genérica, mesmo quando a dele não encontra
        nao = sorted(set(ex.nao_certificar) | set(ex.itens))
        return {k: v for k, v in (("itens", itens), ("nao_certificar", nao)) if v}

    def vigiar_original(self, livro: dict[str, Any], intervalo_dias: float = 7, maximo: int = 10) -> list[Achado]:
        """O mapa do site ORIGINAL do livro (a origem confirmada), pedido pela rede neural (titular, 23/10/2026): as URLs
        novas que têm a ver com o livro (a próxima oportunidade, os arquivos, os dados). O motor guarda o que já viu de cada
        domínio (nunca o livro); na primeira visita, a base: só o que for relevante e recente; cada domínio, no máximo uma
        vez por intervalo."""
        from datetime import datetime, timedelta, timezone

        from ..descoberta import mapa_original as M
        link = livro.get("link_oficial")
        if not link:
            return []
        raiz = M.base(link)
        dominio = raiz.split("//", 1)[-1]
        antes = self.estado.mapa_verificado_em(dominio)
        if antes and datetime.fromisoformat(antes) > datetime.now(timezone.utc) - timedelta(days=intervalo_dias):
            return []
        pistas = M.urls(self.escada.buscar, raiz)
        vistas = self.estado.mapa_visto(dominio)
        primeira = not vistas
        palavras = M.palavras_proprias(f"{livro.get('titulo') or ''} {livro.get('programa') or ''}")
        numero = livro.get("numero")
        entregar: list[tuple[Pista, str]] = []
        for p in pistas:
            if p.link in vistas or p.link.rstrip("/") == link.rstrip("/"):
                continue
            motivo = M.relevancia(p.link, palavras, numero)
            if motivo and (not primeira or M.recente(p)):
                entregar.append((p, motivo))
        self.estado.marcar_mapa(dominio, [p.link for p in pistas], _agora())
        self.relatorio.append(f"mapa do site original {dominio}: {len(pistas)} URL(s), {len(entregar)} nova(s) do livro"
                              f"{' (primeira visita: a base)' if primeira else ''}")
        achados = []
        m = self.cfg.motor
        for p, motivo in entregar[:maximo]:
            documento = None
            try:
                r = self.escada.buscar(p.link)
                lido = self.leitura.ler(r.conteudo, p.link)
                documento = {"url": p.link, "sha256": lido.sha256, "tipo": lido.tipo, "leitor": lido.leitor, "oficial": False,
                             "paginas": [x.texto for x in lido.paginas], "alertas": lido.alertas, "injecao": lido.dados.get("injecao")}
            except (Bloqueado, Indisponivel, Pendente, leitores.SemLeitor) as e:
                self.relatorio.append(f"mapa do site original: {p.link} não lido ({str(e)[:120]})")
            achados.append(Achado(id=f"{m.id}-mapa-{hashlib.sha256(p.link.encode()).hexdigest()[:16]}", motor=m.id, encontrado_em=_agora()[:10],
                                  link_divulgacao=p.link, link_oficial=p.link, titulo=livro.get("titulo") or p.titulo,
                                  dados={"livro_id": livro["id"], "origem": "mapa do site original", "motivo": motivo, "modificado_em": p.data},
                                  documento=documento))
        return achados

    def pesquisar(self, livro: dict[str, Any]) -> Achado | None:
        """A pesquisa focada pedida pela rede neural (fase 3 do Cartório): o motor da oportunidade relê a divulgação e o
        oficial do livro, segue até o documento e aplica a sua extração própria. A informação vai direto ao livro."""
        import msgspec
        link = livro.get("link_oficial") or livro.get("link_divulgacao")
        if not link:
            return None
        leitura = self.cfg.leitura.model_copy(update={"documentos": True, "paginas_dos_achados": True, "seguir_oficial": True,
                                                       "max_documentos": max(1, self.cfg.leitura.max_documentos)})
        original, self.cfg = self.cfg, self.cfg.model_copy(update={"leitura": leitura})
        try:
            fonte = CfgFonte(nome="pesquisa focada", url=livro.get("link_divulgacao") or link)
            a = self._achado(fonte, Pista(titulo=livro.get("titulo") or "", link=link, origem="pesquisa focada pedida pela rede neural"), 0)
        finally:
            self.cfg = original
        if a is None or not a.documento:
            return None
        return msgspec.structs.replace(a, id=f"{self.cfg.motor.id}-pesquisa-{livro['id']}-{_agora()[:10]}",
                                       dados={**(a.dados or {}), "livro_id": livro["id"], "origem": "pesquisa focada pedida pela rede neural"})

    def _seguir_oficial(self, pista: Pista) -> tuple[str, str, dict] | None:
        """Da página de divulgação ao documento oficial: (oficial, divulgação, documento lido) ou None."""
        from ..descoberta import fonte_oficial
        try:
            pagina = self.escada.buscar(pista.link)
            _datar_pela_pagina(pista, pagina.conteudo)                # 08/11/2026: a data lida na própria divulgação
            cands = fonte_oficial.candidatos(pagina.conteudo, pista.link, pista.titulo)
        except (Bloqueado, Indisponivel, Pendente) as e:
            self.relatorio.append(f"seguir até o oficial: divulgação não lida ({pista.link}: {str(e)[:120]})")
            return None
        for c in cands:
            try:
                r = self.escada.buscar(c["url"])
                lido = self.leitura.ler(r.conteudo, c["url"])
            except (Bloqueado, Indisponivel, Pendente, leitores.SemLeitor) as e:
                self.relatorio.append(f"seguir até o oficial: {c['url']} não lido ({str(e)[:120]})")
                continue
            doc = {"url": c["url"], "sha256": lido.sha256, "tipo": lido.tipo, "leitor": lido.leitor, "oficial": not r.copia_arquivada,
                   "paginas": [p.texto for p in lido.paginas], "alertas": lido.alertas + [f"achado a partir da divulgação ({c['pontos']} pontos)"],
                   "injecao": lido.dados.get("injecao")}
            return c["url"], pista.link, doc
        return None

    def _lida_hoje(self, nome: str) -> bool:
        """R49 (titular, 08/11/2026): o local lido HOJE (no dia de Brasília) sem erro não se lê de novo no mesmo dia; com erro
        (bloqueio, pendente no computador local), tenta de novo."""
        import os
        if os.environ.get("ELDORADO_FORCAR") == "1":                # o acionamento à mão (a titular força a leitura) vale sempre
            return False
        f = self.estado._fonte(nome)
        ultima = f.get("ultima")
        if not ultima or f.get("situacao") == "erro":
            return False
        try:
            dia = datetime.fromisoformat(str(ultima)).astimezone(ZoneInfo("America/Sao_Paulo")).date()
        except ValueError:
            return False
        return dia == hoje_local()

    def _subpaginas(self) -> Iterable[Achado]:
        """R49: a segunda etapa de cada local — as subpáginas novas do domínio de cada fonte e de cada alvo, uma vez por dia
        (descoberta/subpaginas.py). As que o léxico aceita viram achado como qualquer pista."""
        cv = self.cfg.canivete
        if not cv.subpaginas:
            return
        from urllib.parse import urlsplit

        from ..descoberta import subpaginas as S
        def base(u: str) -> str:
            s = urlsplit(preencher(u, hoje_local()) if "{hoje" in u else u)
            return f"{s.scheme}://{s.netloc}".lower() if s.netloc else ""

        com_mapa = {base(f.url) for f in self.cfg.fonte if f.tipo == "mapa" and f.url}
        bases = [base(f.url) for f in self.cfg.fonte if f.tipo in ("pagina", "feed", "wordpress") and f.url]
        for a in self.cfg.alvo:
            if not a.enderecos:
                continue
            if self.cfg.lexico.territorio == "goias":              # o alvo fora do território (R27) não tem a segunda etapa
                from ...base.missao.regras_portao import municipal_fora_de_goias
                if municipal_fora_de_goias({"titulo": a.nome, "orgao": a.orgao or "", "url": a.enderecos[0], "uf": None}) \
                        or _prefeitura_de_outro_estado(a.enderecos[0]):
                    continue
            bases.append(base(a.enderecos[0]))
        vistos: set[str] = set()
        unicas = []
        for b in bases:                                            # o mesmo domínio com e sem www. é um só
            chave = (urlsplit(b).hostname or "").removeprefix("www.")
            if b and chave not in vistos and b not in com_mapa and not S.SEM_DOMINIO.search(urlsplit(b).hostname or ""):
                vistos.add(chave)
                unicas.append(b)
        bases = unicas

        def ler(url: str) -> bytes | None:
            try:
                return self.escada.buscar(url).conteudo
            except Exception:  # noqa: BLE001 — o mapa ou o feed que não abre só não dá a segunda etapa
                return None

        for raiz in bases:
            host = urlsplit(raiz).netloc
            nome = f"subpáginas · {host}"
            if self._lida_hoje(nome):
                continue
            try:
                vistas = self.estado.mapa_visto(host)
                pistas, memorizar, rota = S.novas(ler, raiz, hoje_local(), vistas, cv.subpaginas_janela_dias)
            except Exception as e:  # noqa: BLE001 — a segunda etapa nunca derruba o motor
                self.estado.leitura(nome, _agora(), erro=f"{type(e).__name__}: {str(e)[:200]}")
                continue
            if memorizar:
                self.estado.marcar_mapa(host, memorizar, _agora())
            entregues = 0
            for pista in pistas:
                idade = _idade_dias(pista.data)
                if idade is not None and idade > cv.subpaginas_janela_dias:
                    continue
                if entregues >= cv.subpaginas_por_dominio:
                    break
                if not self._passa_entrada(pista) or self._ja_entregue(pista.link):
                    continue
                fonte = CfgFonte(nome=nome, url=raiz + "/", tipo="mapa", papel="alternativa")
                try:
                    a = self._achado(fonte, pista, entregues)
                except Exception as e:  # noqa: BLE001
                    self.relatorio.append(f"{nome}: o achado {pista.link[:100]} falhou ({type(e).__name__})")
                    continue
                if a is not None:
                    entregues += 1
                    self.estado.marcar_entregue(pista.link, _agora(), a.id, nome)
                    yield a
            self.estado.leitura(nome, _agora(), achados=entregues, sem_mudanca=not pistas)
            self.relatorio.append(f"{nome}: {rota}; {len(pistas)} página(s) nova(s), {entregues} achado(s)")

    def _ja_entregue(self, link: str) -> bool:
        """08/11/2026 (parecer): o mesmo edital pelo RSS (www.) e pela página (sem www., com ou sem a barra final) entrava duas
        vezes. Confere o endereço e as variantes dele no registro de entregues (o registro não muda: compatível com o que já
        foi entregue)."""
        return any(self.estado.ja_entregue(v) for v in _variantes_do_endereco(link))

    def _lx(self) -> CfgLexico:
        """09/11/2026 (R50): o léxico em uso — o da fonte que está sendo lida, quando ela tem o próprio, ou o do motor."""
        return getattr(self, "_lexico_fonte", None) or self.cfg.lexico

    def _velha_pela_pagina(self, pista: Pista, documento: dict | None) -> bool:
        """08/11/2026 (parecer): a idade também depois da leitura, quando a pista veio sem data e a data foi lida na página
        (a notícia de 2019 achada pela busca HTML). Não vale para o alvo vigiado (o portal muda e a data dele é a do
        portal) nem quando o texto cita uma data dentro da janela (o prazo de agora): a data da página pode estar errada."""
        lx = self._lx()
        extra = pista.extra or {}
        if not (lx.idade_maxima_dias and extra.get("data_lida_na_pagina") and pista.data) or str(pista.origem or "").startswith("alvo "):
            return False
        idade = _idade_dias(pista.data)
        if idade is None or idade <= lx.idade_maxima_dias:
            return False
        if documento and _cita_data_recente("\n".join(documento.get("paginas") or []), lx.idade_maxima_dias):
            return False
        motivo = f"publicada há mais de {lx.idade_maxima_dias} dias (data lida na página)"
        if not hasattr(self, "_barradas_na_entrada"):
            self._barradas_na_entrada = {}
        self._barradas_na_entrada[motivo] = self._barradas_na_entrada.get(motivo, 0) + 1
        return True

    def _passa_entrada(self, pista: Pista) -> bool:
        """O filtro de entrada (08/11/2026): o léxico, o título genérico de link, a idade e o território. A pista que não passa
        não é lida nem entregue (o motivo vai ao relatório, contado por fonte)."""
        motivo = self._motivo_entrada(pista)
        if motivo:
            if not hasattr(self, "_barradas_na_entrada"):
                self._barradas_na_entrada = {}
            self._barradas_na_entrada[motivo] = self._barradas_na_entrada.get(motivo, 0) + 1
            return False
        return True

    def _motivo_entrada(self, pista: Pista) -> str | None:
        if not self._passa_lexico(pista.titulo, pista.resumo or ""):
            return "léxico"
        if TITULO_GENERICO.search(pista.titulo or "") and not NOME_DE_ARQUIVO.search(pista.titulo or "") and not DOCUMENTO.search(pista.link or ""):
            return "título genérico de link (menu ou chamada de notícia)"
        if (pista.extra or {}).get("situacao") == "encerrada":    # 08/11/2026: o rótulo ao lado do link ("Encerrado")
            return "situação encerrada no item da lista"
        lx = self._lx()
        if lx.idade_maxima_dias:
            # sem a data da fonte, a data no começo do título ("05/12/2023 | EDITAL ...", comum nas tabelas das prefeituras)
            inicio = re.match(r"\s*(\d{2}/\d{2}/\d{4})", pista.titulo or "")
            idade = _idade_dias(pista.data or (inicio.group(1) if inicio else None))
            if idade is not None and idade > lx.idade_maxima_dias:
                return f"publicada há mais de {lx.idade_maxima_dias} dias"
            fim = _prazo_no_titulo(pista.titulo or "")             # 08/11/2026: "… até 22 de out. de 2026" (os agregadores)
            if fim is not None and fim < hoje_local():
                return "prazo de inscrição vencido (no título)"
        if lx.territorio == "goias":
            from ...base.missao.regras_portao import municipal_fora_de_goias
            orgao = str((pista.extra or {}).get("orgao") or "")
            uf = str((pista.extra or {}).get("uf") or "").upper() or None     # 08/11: a UF do item, quando a fonte traz
            r = {"titulo": f"{pista.titulo} {(pista.resumo or '')[:300]}", "orgao": orgao, "url": pista.link, "uf": uf}
            if municipal_fora_de_goias(r):
                return "município de outro estado (não capital)"
        return None

    def _passa_lexico(self, titulo: str, resumo: str = "") -> bool:
        lx = self._lx()
        t, tudo = _sem_acento(titulo), _sem_acento(f"{titulo} {resumo}")
        if lx.termos and not self._casa(t if lx.termos_em == "titulo" else tudo, lx.termos):
            return False
        return not (lx.vetos and self._casa(t, lx.vetos) and not self._casa(t, lx.salvos))

    def _achado(self, fonte: CfgFonte, pista: Pista, n: int) -> Achado | None:
        degrau_lista = getattr(self.escada, "ultimo_degrau", None)
        r = None
        documento = None
        # o link encontrado é a DIVULGAÇÃO; a origem é só o candidato da busca cega (seguir_oficial), decidida por livro depois
        oficial, divulgacao = None, pista.link
        # 08/11/2026: o "arquivo.pdf/view" do Plone (gov.br, MPT) é a página de exibição; o arquivo é o endereço sem o /view
        doc_link = VISTA_PLONE.sub(r"\1", pista.link)
        ler = (self.cfg.leitura.documentos and DOCUMENTO.search(doc_link)) or (self.cfg.leitura.paginas_dos_achados and not DOCUMENTO.search(doc_link))
        texto_do_ato = (pista.extra or {}).get("documento_texto")
        html_bruto = None
        if texto_do_ato:                                            # o ato já recortado do documento oficial: é o próprio documento
            from ...base.nucleo.seguranca import injecao
            documento = {"url": pista.link, "sha256": hashlib.sha256(texto_do_ato.encode()).hexdigest(), "tipo": "ato", "leitor": "atos",
                         "oficial": False, "paginas": [texto_do_ato], "alertas": [], "injecao": injecao(texto_do_ato)}   # o ato como publicado
            ler = False
        if self.cfg.leitura.seguir_oficial and not texto_do_ato and not DOCUMENTO.search(doc_link) and n < self.cfg.leitura.max_documentos:
            achado_oficial = self._seguir_oficial(pista)
            if achado_oficial:
                oficial, divulgacao, documento = achado_oficial
                ler = False
        if ler and n < self.cfg.leitura.max_documentos:
            try:
                r = self.escada.buscar(doc_link)
                lido = self.leitura.ler(r.conteudo, doc_link)
            except (Bloqueado, Indisponivel, Pendente, leitores.SemLeitor) as e:
                # o achado não se perde por causa do documento: ele segue sem o documento, que é lido depois (Fase 8)
                self.relatorio.append(f"{fonte.nome}: documento não lido, achado entregue sem ele ({pista.link}: {str(e)[:200]})")
                r = lido = None
            if lido is not None:
                documento = {"url": doc_link, "sha256": lido.sha256, "tipo": lido.tipo, "leitor": lido.leitor, "oficial": False,
                             "paginas": [p.texto for p in lido.paginas], "alertas": lido.alertas, "injecao": lido.dados.get("injecao")}
                if lido.tipo in ("html", "pagina") and r is not None:
                    html_bruto = r.conteudo.decode("utf-8", errors="replace")
                    _datar_pela_pagina(pista, html_bruto)             # 08/11/2026: a data lida na própria página
        if self._velha_pela_pagina(pista, documento):
            return None
        canivete = self._canivete(documento, texto_do_ato, html_bruto, pista.link)
        escada = {"motor": self.cfg.motor.id, "fonte": fonte.nome, "degrau": (r.degrau if ler and r is not None else None) or degrau_lista}
        m = self.cfg.motor
        chave = hashlib.sha256(pista.link.encode()).hexdigest()[:16]
        titulo = pista.titulo
        if TITULO_GENERICO.search(titulo or "") or (pista.extra or {}).get("titulo_do_endereco"):   # 08/11: do próprio documento
            titulo = _titulo_do_documento(documento) or titulo
        return Achado(id=f"{m.id}-{chave}", motor=m.id, encontrado_em=_agora()[:10], link_divulgacao=divulgacao, link_oficial=oficial,
                      titulo=titulo[:300], publicado_em=_data_iso(pista.data),
                      dados={"uf": m.uf, "orgao": m.orgao, **{k: v for k, v in pista.extra.items() if k != "documento_texto"}, "fonte": fonte.nome,
                             "origem": pista.origem,
                             **(self._extrair(documento["paginas"]) if documento and self.cfg.extracao.itens else {}),
                             **({"leis": self.cfg.legislacao.leis} if self.cfg.legislacao.leis else {}),
                             **({"resumo": pista.resumo} if pista.resumo else {}),
                             **({"canivete": canivete} if canivete else {}), "escada": escada}, documento=documento)

    def _canivete(self, documento: dict | None, texto_do_ato: str | None, html: str | None, url: str) -> dict | None:
        """O enriquecimento do achado (o motor padrão): idioma, publicação, datas, valores, metadados e o texto principal;
        o texto principal substitui o da página no documento (sem menus e rodapés), em vez de se repetir nos dados."""
        if not self.cfg.canivete.ligado:
            return None
        from ..leitura.enriquecer import enriquecer
        texto = "\n".join(documento["paginas"]) if documento else (texto_do_ato or "")
        if not texto and not html:
            return None
        r = enriquecer(texto, html, url, self.cfg.canivete.habilidades())
        feitos = getattr(self, "_arquivados", 0)
        import os
        if (self.cfg.canivete.arquivar and os.environ.get("ELDORADO_ARQUIVAR", "sim") != "nao" and feitos < self.cfg.canivete.arquivar_por_execucao
                and any(d.get("prazo") for d in r.get("datas", []))):
            self._arquivados = feitos + 1
            try:
                from ..descoberta.arquivos_web import arquivar
                copia = arquivar(url)
                if copia:
                    r["arquivo_wayback"] = copia
            except Exception as e:  # noqa: BLE001 — arquivar é um extra: a falha fica registrada, o achado segue
                r.setdefault("falhas", []).append(f"arquivar: {type(e).__name__}")
        principal = r.pop("texto_principal", None)
        if principal and documento and documento.get("tipo") in ("html", "pagina"):
            documento["paginas"] = [principal]
            documento["alertas"] = [*documento.get("alertas", []), "texto principal (trafilatura)"]
        return r or None


def apelidos(pasta: str | Path = Path(__file__).parent / "config") -> dict[str, str]:
    """Cada nome anterior (ou motor reunido) → o motor de hoje, a partir das configurações."""
    import tomllib
    mapa: dict[str, str] = {}
    for p in Path(pasta).glob("*.toml"):
        m = tomllib.loads(p.read_text(encoding="utf-8")).get("motor", {})
        for antigo in m.get("nomes_anteriores", []):
            mapa[antigo] = m["id"]
    return mapa
