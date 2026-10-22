"""O motor genérico de canal: um motor é uma CONFIGURAÇÃO (um arquivo TOML), sem código próprio.

A cada passagem, para cada fonte: acessa pela escada; vigia (página sem mudança não é relida); descobre as pistas pela
forma da fonte; pré-filtra pelo léxico; não entrega de novo; lê o documento oficial (texto literal, nunca o binário);
entrega o achado; e aprende com o retorno da Pertinência. Uma fonte com problema nunca derruba o motor: vira registro.
"""
from __future__ import annotations

import hashlib
import re
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Literal

from pydantic import BaseModel, ConfigDict, Field

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


class CfgFonte(_Base):
    nome: str
    url: str
    tipo: Literal["pagina", "feed", "mapa", "wordpress", "ckan", "api", "metabusca", "wayback"] = "pagina"
    seletor: str | None = None
    termos: str | None = None
    caminhos: dict[str, str] = Field(default_factory=dict)
    exige_brasil: bool = False


class CfgAcesso(_Base):
    degraus: list[Literal["api", "leve", "lightpanda", "patchright", "camoufox", "arquivo", "local"]] = ["api", "leve"]
    intervalo_s: float = 1.0
    espera_seletor: str | None = None
    tentativas: int = Field(2, ge=1, le=3)


class CfgLeitura(_Base):
    documentos: bool = True
    tabelas: Literal["nao", "uteis", "todas"] = "uteis"
    max_documentos: int = Field(20, ge=0, le=500)


class CfgLexico(_Base):
    termos: list[str] = Field(default_factory=list)
    vetos: list[str] = Field(default_factory=list)


class Configuracao(_Base):
    motor: CfgMotor
    fonte: list[CfgFonte]
    acesso: CfgAcesso = CfgAcesso()
    leitura: CfgLeitura = CfgLeitura()
    lexico: CfgLexico = CfgLexico()
    alvos: dict[str, Any] = Field(default_factory=dict)
    metas: dict[str, Any] = Field(default_factory=dict)
    agenda: dict[str, Any] = Field(default_factory=dict)


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
            for pista in pistas:
                if not self._passa_lexico(f"{pista.titulo} {pista.resumo or ''}") or self.estado.ja_entregue(pista.link):
                    continue
                achado = self._achado(fonte, pista, entregues)
                if achado is None:
                    continue
                entregues += 1
                self.estado.marcar_entregue(pista.link, _agora(), achado.id, fonte.nome)
                yield achado
            self.estado.leitura(fonte.nome, _agora(), achados=entregues)
            self.relatorio.append(f"{fonte.nome}: {len(pistas)} pista(s), {entregues} achado(s)")

    def _descobrir(self, f: CfgFonte) -> list[Pista] | None:
        buscar = self.escada.buscar
        if f.tipo == "pagina":
            r = buscar(f.url)
            ass = vigilancia.assinatura(r.conteudo, f.seletor)
            if not vigilancia.mudou(self.estado.assinatura(f.nome), ass):
                return None
            pistas = estrutura_site.links(lambda _u, r=r: r, f.url)
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
            return dados_abertos.api_oficial(buscar, f.url, f.caminhos)
        if f.tipo == "wayback":
            from ..acesso.escada import dominio
            return arquivos_web.indice_wayback(buscar, dominio(f.url))
        pistas, relato = Metabusca(buscar, searxng=f.url or None).consultar(f.termos or "")
        self.relatorio.extend(f"{f.nome}: {x}" for x in relato)
        return pistas

    def _passa_lexico(self, texto: str) -> bool:
        t = _sem_acento(texto)
        termos = [_sem_acento(x) for x in self.cfg.lexico.termos]
        if termos and not any(x in t for x in termos):
            return False
        return not any(_sem_acento(v) in t for v in self.cfg.lexico.vetos)

    def _achado(self, fonte: CfgFonte, pista: Pista, n: int) -> Achado | None:
        documento = None
        if self.cfg.leitura.documentos and DOCUMENTO.search(pista.link) and n < self.cfg.leitura.max_documentos:
            try:
                r = self.escada.buscar(pista.link)
                lido = self.leitura.ler(r.conteudo, pista.link)
            except (Bloqueado, Indisponivel, Pendente, leitores.SemLeitor) as e:
                self.relatorio.append(f"{fonte.nome}: documento não lido ({pista.link}: {e})")
                return None
            documento = {"url": pista.link, "sha256": lido.sha256, "tipo": lido.tipo, "leitor": lido.leitor, "oficial": not r.copia_arquivada,
                         "paginas": [p.texto for p in lido.paginas], "alertas": lido.alertas}
        m = self.cfg.motor
        chave = hashlib.sha256(pista.link.encode()).hexdigest()[:16]
        return Achado(id=f"{m.id}-{chave}", motor=m.id, encontrado_em=_agora()[:10], link_divulgacao=fonte.url, link_oficial=pista.link,
                      titulo=pista.titulo[:300], publicado_em=(pista.data or None) and str(pista.data)[:10],
                      dados={"uf": m.uf, "orgao": m.orgao, "fonte": fonte.nome, "origem": pista.origem}, documento=documento)
