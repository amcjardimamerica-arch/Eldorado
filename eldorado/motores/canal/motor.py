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

DOCUMENTO = re.compile(r"(?i)\.(pdf|docx?|xlsx?|ods|odt|pptx|zip|7z|rar)(?:$|\?)")


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


class CfgPaginacao(_Base):
    inicio: int = 1
    maximo: int = Field(5, ge=1, le=100)
    total: str | None = None                  # onde está o total de páginas na resposta (jmespath)


class CfgElo(_Base):
    """Um elo da leitura em cadeia (descoberta/cadeia.py)."""
    formato: Literal["json", "html", "atos", "linhas"]
    itens: str = ""                         # jmespath (json), seletor CSS (html) ou o padrão dos cabeçalhos (atos; vazio = o padrão)
    campos: dict[str, str] = Field(default_factory=dict)
    url: str | None = None
    filtro: dict[str, str] = Field(default_factory=dict)
    limite: int = Field(300, ge=1, le=5000)


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


class CfgAcesso(_Base):
    degraus: list[Literal["api", "leve", "lightpanda", "patchright", "camoufox", "arquivo", "local"]] = ["api", "leve"]
    intervalo_s: float = 1.0
    espera_seletor: str | None = None
    tentativas: int = Field(2, ge=1, le=3)


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


def _sem_acento(t: str) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFKD", t.lower()) if not unicodedata.combining(c))


class MotorCanal(Motor):
    def __init__(self, configuracao: str | Path, dados: str | Path = "dados/motores", ponte: str | Path = "dados/ponte",
                 lightpanda: str | None = None, mirror_wayback: str | None = None):
        self.caminho = Path(configuracao)
        self.cfg = Configuracao(**tomllib.loads(self.caminho.read_text(encoding="utf-8")))
        self.estado = EstadoMotor(Path(dados) / f"{self.cfg.motor.id}.db")
        self.escada = Escada(self._degraus(ponte, lightpanda, mirror_wayback), intervalo_padrao=self.cfg.acesso.intervalo_s,
                             tentativas=self.cfg.acesso.tentativas)
        self.leitura = leitores.padrao()
        self.leitura.registrar(LeitorPDF(tabelas=self.cfg.leitura.tabelas))
        self.relatorio: list[str] = []

    def _degraus(self, ponte, lightpanda, mirror):
        mapa = {"api": lambda: DegrauAPI(), "leve": lambda: DegrauLeve(),
                "lightpanda": lambda: DegrauLightpanda(binario=lightpanda, espera_seletor=self.cfg.acesso.espera_seletor),
                "patchright": lambda: DegrauNavegador("patchright", self.cfg.acesso.espera_seletor),
                "camoufox": lambda: DegrauNavegador("camoufox", self.cfg.acesso.espera_seletor),
                "arquivo": lambda: DegrauArquivo(mirror) if mirror else DegrauArquivo(), "local": lambda: DegrauLocal(ponte)}
        return [mapa[d]() for d in self.cfg.acesso.degraus]

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
            self.estado.retorno(r.achado, None, r.decisao, r.motivo, _agora())

    # ------------------------------------------------------------------ busca
    def buscar(self, plano: Plano) -> Iterable[Achado]:
        self.relatorio = []
        if self.cfg.programa:
            achado = self._programa()
            if achado:
                yield achado
        for fonte in self.cfg.fonte:
            try:
                pistas = self._descobrir(fonte)
            except Pendente as e:
                self.relatorio.append(f"{fonte.nome}: entregue ao computador local ({e})")
                self.estado.leitura(fonte.nome, _agora(), erro="pendente no computador local")
                continue
            except (Bloqueado, Indisponivel, ValueError) as e:
                self.relatorio.append(f"{fonte.nome}: não lida ({e})")
                self.estado.leitura(fonte.nome, _agora(), erro=str(e)[:300])
                continue
            if pistas is None:
                self.relatorio.append(f"{fonte.nome}: sem mudança desde a última leitura")
                self.estado.leitura(fonte.nome, _agora(), sem_mudanca=True)
                continue
            entregues = 0
            if self.cfg.motor.destino == "especial":
                for pista in pistas:
                    a = self._registro_especial(fonte, pista)
                    if a is not None:
                        entregues += 1
                        yield a
                self.estado.leitura(fonte.nome, _agora(), achados=entregues)
                self.relatorio.append(f"{fonte.nome}: {len(pistas)} registro(s), {entregues} para a base Especial")
                continue
            proprios = {self.cfg.programa.link_divulgacao.rstrip("/"), self.cfg.programa.link_oficial.rstrip("/")} if self.cfg.programa else set()
            for pista in pistas:
                if pista.link.rstrip("/") in proprios:
                    continue                                        # o próprio programa já é entregue pela seção programa
                if not self._passa_lexico(pista.titulo, pista.resumo or "") or self.estado.ja_entregue(pista.link):
                    continue
                achado = self._achado(fonte, pista, entregues)
                if achado is None:
                    continue
                entregues += 1
                self.estado.marcar_entregue(pista.link, _agora(), achado.id, fonte.nome)
                yield achado
            self.estado.leitura(fonte.nome, _agora(), achados=entregues)
            self.relatorio.append(f"{fonte.nome}: {len(pistas)} pista(s), {entregues} achado(s)")
        yield from self._alvos()

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
            if not self._na_janela(alvo, mes):
                self.relatorio.append(f"alvo {alvo.nome}: fora da janela prevista")
                continue
            for n, url in enumerate(alvo.enderecos):
                fonte = CfgFonte(nome=f"alvo · {alvo.id}", url=url, tipo="pagina", papel="principal" if n == 0 else "alternativa")
                try:
                    pistas = self._descobrir(fonte)
                except (Bloqueado, Indisponivel, Pendente, ValueError) as e:
                    self.estado.leitura(fonte.nome, _agora(), erro=f"{url}: {str(e)[:250]}")
                    continue                                        # a próxima rota do alvo
                if pistas is None:
                    self.estado.leitura(fonte.nome, _agora(), sem_mudanca=True)
                    self.relatorio.append(f"alvo {alvo.nome}: sem mudança")
                    break
                self.estado.mudanca_do_alvo(alvo.id, _agora())
                entregues = 0
                for pista in pistas:
                    if self._passa_lexico(pista.titulo, pista.resumo or "") and not self.estado.ja_entregue(pista.link):
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
                        resumo=formatar(f.pista.resumo, i) if f.pista.resumo else None,
                        extra={**({"documento_texto": formatar(f.pista.texto, i)} if f.pista.texto else {}),
                               **{k: i[k] for k in ("orgao", "edicao", "data", "protocolo", "caminho", "localidade") if i.get(k)},
                               **({"_item": {k: v for k, v in i.items() if k != "texto"}} if self.cfg.motor.destino == "especial" else {})})
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
        return msgspec.structs.replace(a, id=f"{self.cfg.id}-pesquisa-{livro['id']}-{_agora()[:10]}",
                                       dados={**(a.dados or {}), "livro_id": livro["id"], "origem": "pesquisa focada pedida pela rede neural"})

    def _seguir_oficial(self, pista: Pista) -> tuple[str, str, dict] | None:
        """Da página de divulgação ao documento oficial: (oficial, divulgação, documento lido) ou None."""
        from ..descoberta import fonte_oficial
        try:
            pagina = self.escada.buscar(pista.link)
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

    def _passa_lexico(self, titulo: str, resumo: str = "") -> bool:
        lx = self.cfg.lexico
        t, tudo = _sem_acento(titulo), _sem_acento(f"{titulo} {resumo}")
        if lx.termos and not self._casa(t if lx.termos_em == "titulo" else tudo, lx.termos):
            return False
        return not (lx.vetos and self._casa(t, lx.vetos) and not self._casa(t, lx.salvos))

    def _achado(self, fonte: CfgFonte, pista: Pista, n: int) -> Achado | None:
        documento = None
        # o link encontrado é a DIVULGAÇÃO; a origem é só o candidato da busca cega (seguir_oficial), decidida por livro depois
        oficial, divulgacao = None, pista.link
        ler = (self.cfg.leitura.documentos and DOCUMENTO.search(pista.link)) or (self.cfg.leitura.paginas_dos_achados and not DOCUMENTO.search(pista.link))
        texto_do_ato = (pista.extra or {}).get("documento_texto")
        if texto_do_ato:                                            # o ato já recortado do documento oficial: é o próprio documento
            from ...base.nucleo.seguranca import injecao
            documento = {"url": pista.link, "sha256": hashlib.sha256(texto_do_ato.encode()).hexdigest(), "tipo": "ato", "leitor": "atos",
                         "oficial": False, "paginas": [texto_do_ato], "alertas": [], "injecao": injecao(texto_do_ato)}   # o ato como publicado
            ler = False
        if self.cfg.leitura.seguir_oficial and not texto_do_ato and not DOCUMENTO.search(pista.link) and n < self.cfg.leitura.max_documentos:
            achado_oficial = self._seguir_oficial(pista)
            if achado_oficial:
                oficial, divulgacao, documento = achado_oficial
                ler = False
        if ler and n < self.cfg.leitura.max_documentos:
            try:
                r = self.escada.buscar(pista.link)
                lido = self.leitura.ler(r.conteudo, pista.link)
            except (Bloqueado, Indisponivel, Pendente, leitores.SemLeitor) as e:
                # o achado não se perde por causa do documento: ele segue sem o documento, que é lido depois (Fase 8)
                self.relatorio.append(f"{fonte.nome}: documento não lido, achado entregue sem ele ({pista.link}: {str(e)[:200]})")
                r = lido = None
            if lido is not None:
                documento = {"url": pista.link, "sha256": lido.sha256, "tipo": lido.tipo, "leitor": lido.leitor, "oficial": False,
                             "paginas": [p.texto for p in lido.paginas], "alertas": lido.alertas, "injecao": lido.dados.get("injecao")}
        m = self.cfg.motor
        chave = hashlib.sha256(pista.link.encode()).hexdigest()[:16]
        return Achado(id=f"{m.id}-{chave}", motor=m.id, encontrado_em=_agora()[:10], link_divulgacao=divulgacao, link_oficial=oficial,
                      titulo=pista.titulo[:300], publicado_em=(pista.data or None) and str(pista.data)[:10],
                      dados={"uf": m.uf, "orgao": m.orgao, **{k: v for k, v in pista.extra.items() if k != "documento_texto"}, "fonte": fonte.nome,
                             "origem": pista.origem,
                             **(self._extrair(documento["paginas"]) if documento and self.cfg.extracao.itens else {}),
                             **({"leis": self.cfg.legislacao.leis} if self.cfg.legislacao.leis else {}),
                             **({"resumo": pista.resumo} if pista.resumo else {})}, documento=documento)


def apelidos(pasta: str | Path = Path(__file__).parent / "config") -> dict[str, str]:
    """Cada nome anterior (ou motor reunido) → o motor de hoje, a partir das configurações."""
    import tomllib
    mapa: dict[str, str] = {}
    for p in Path(pasta).glob("*.toml"):
        m = tomllib.loads(p.read_text(encoding="utf-8")).get("motor", {})
        for antigo in m.get("nomes_anteriores", []):
            mapa[antigo] = m["id"]
    return mapa
