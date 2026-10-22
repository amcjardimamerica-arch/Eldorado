"""Os contratos do Eldorado.

A base só conversa com os módulos (motores, pilotos, ferramentas, etapas, missão) por estes contratos.
Nenhum módulo importa outro módulo diretamente. Trocar um motor, o banco ou a missão não muda a base.

As estruturas de dados são `msgspec.Struct`: rápidas, tipadas e serializáveis nos eventos.
"""
from __future__ import annotations

import abc
import inspect
from typing import Any, ClassVar, Iterable

import msgspec

# ---------------------------------------------------------------- estruturas que circulam entre as partes

class Linhagem(msgspec.Struct, frozen=True, omit_defaults=True):
    """De onde um dado veio: o livro e o achado de origem (a história do livro, conceito do n8n)."""
    livro: str | None = None
    achado: str | None = None


class Achado(msgspec.Struct, kw_only=True, omit_defaults=True):
    """O que um motor entrega: exatamente os dados necessários, os dois links e a prova. Nunca um binário."""
    id: str
    motor: str
    encontrado_em: str
    link_divulgacao: str
    dados: dict[str, Any]
    link_oficial: str | None = None
    titulo: str | None = None
    publicado_em: str | None = None
    documento_sha256: str | None = None
    drive_id: str | None = None
    veio_de_copia_arquivada: bool = False
    pista: bool = False


class Plano(msgspec.Struct, kw_only=True, omit_defaults=True):
    """O que a Regência entrega a um motor ao acioná-lo."""
    passagem: str
    janela_inicio: str
    janela_fim: str
    alvos: list[str] = []
    tempo_maximo_s: int = 600
    paralelismo_maximo: int = 1


class Retorno(msgspec.Struct, kw_only=True, omit_defaults=True):
    """O que a Pertinência devolve ao motor sobre um achado (para ele aprender)."""
    achado: str
    decisao: str            # 'aceito' ou 'barrado'
    motivo: str | None = None
    livro: str | None = None


class Saude(msgspec.Struct, kw_only=True, omit_defaults=True):
    ok: bool
    mensagem: str = ""
    detalhes: dict[str, Any] = {}


class Descricao(msgspec.Struct, kw_only=True, omit_defaults=True):
    """A identidade de um módulo, lida pelo registro e mostrada na Sala."""
    id: str
    tipo: str                # 'motor', 'piloto', 'ferramenta', 'etapa', 'missao'
    parte: str               # 'BASE', 'MOTORES', 'BANCO'
    finalidade: str
    metrica: str
    versao: str = "0.1.0"
    componente: str | None = None


# ---------------------------------------------------------------- interfaces dos módulos

class Modulo(abc.ABC):
    """Todo módulo se descreve e informa a sua saúde."""
    tipo: ClassVar[str] = "modulo"

    @abc.abstractmethod
    def descrever(self) -> Descricao: ...

    @abc.abstractmethod
    def saude(self) -> Saude: ...


class Motor(Modulo):
    """Um motor de busca: uma fonte, uma finalidade. Escreve só por eventos (motor.execucao, achado.entregue)."""
    tipo = "motor"

    @abc.abstractmethod
    def planejar(self, plano: Plano) -> list[str]:
        """Recebe a janela e os alvos e devolve, em ordem, o que vai ler nesta passagem."""

    @abc.abstractmethod
    def buscar(self, plano: Plano) -> Iterable[Achado]:
        """Lê as fontes e entrega os achados, um a um."""

    @abc.abstractmethod
    def aprender(self, retornos: list[Retorno]) -> None:
        """Recebe o que a Pertinência decidiu sobre os seus achados e ajusta o seu aprendizado."""

    @abc.abstractmethod
    def painel(self) -> dict[str, Any]:
        """O que o motor faz e o que aprendeu nas últimas passagens."""


class Piloto(Motor):
    """Um motor livre com IA; o provedor de IA é trocável."""
    tipo = "piloto"

    @abc.abstractmethod
    def provedor(self) -> str: ...


class Ferramenta(Modulo):
    """Uma ferramenta compartilhada (acesso, leitura, descoberta): declara o que resolve."""
    tipo = "ferramenta"
    categoria: ClassVar[str] = ""          # 'acesso', 'leitura', 'descoberta'
    resolve: ClassVar[tuple[str, ...]] = ()

    @abc.abstractmethod
    def aplicar(self, entrada: Any, **opcoes: Any) -> Any: ...


class Etapa(Modulo):
    """Uma etapa do workflow: entrada validada pela Regência, saída medida pela Pertinência."""
    tipo = "etapa"

    @abc.abstractmethod
    def executar(self, livros: list[str]) -> list[str]:
        """Trabalha os livros recebidos e devolve os que devem seguir."""


class Missao(Modulo):
    """A finalidade trocável: o que é um livro, os itens, o portão, a chave e o destino."""
    tipo = "missao"

    @abc.abstractmethod
    def itens(self) -> list[dict[str, str]]: ...

    @abc.abstractmethod
    def chave(self, achado: Achado) -> str: ...

    @abc.abstractmethod
    def portao(self, achado: Achado) -> tuple[bool, str]:
        """Decide se o achado é oportunidade desta missão, e por quê."""


# ---------------------------------------------------------------- conferência do contrato

CONTRATOS: dict[str, type[Modulo]] = {"motor": Motor, "piloto": Piloto, "ferramenta": Ferramenta, "etapa": Etapa, "missao": Missao}


class ContratoVioladoErro(Exception):
    pass


def verificar_contrato(modulo: Modulo) -> Descricao:
    """Confere que o módulo cumpre o contrato do seu tipo e se descreve por inteiro. Usado pelo registro e pelos testes."""
    if not isinstance(modulo, Modulo):
        raise ContratoVioladoErro(f"{type(modulo).__name__} não é um módulo do Eldorado")
    contrato = CONTRATOS.get(modulo.tipo)
    if contrato is None or not isinstance(modulo, contrato):
        raise ContratoVioladoErro(f"{type(modulo).__name__}: tipo '{modulo.tipo}' sem contrato correspondente")
    abertos = [n for n, m in inspect.getmembers(type(modulo)) if getattr(m, "__isabstractmethod__", False)]
    if abertos:
        raise ContratoVioladoErro(f"{type(modulo).__name__}: métodos do contrato sem implementação: {', '.join(abertos)}")
    d = modulo.descrever()
    if not isinstance(d, Descricao):
        raise ContratoVioladoErro(f"{type(modulo).__name__}: descrever() deve devolver Descricao")
    faltando = [c for c in ("id", "finalidade", "metrica", "parte") if not getattr(d, c)]
    if faltando:
        raise ContratoVioladoErro(f"{d.id or type(modulo).__name__}: descrição incompleta ({', '.join(faltando)})")
    if d.tipo != modulo.tipo:
        raise ContratoVioladoErro(f"{d.id}: a descrição diz '{d.tipo}', mas o módulo é '{modulo.tipo}'")
    return d
