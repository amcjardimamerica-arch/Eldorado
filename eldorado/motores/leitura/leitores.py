"""O registro dos leitores: o canivete suíço da leitura.

- O tipo do arquivo é detectado pelo CONTEÚDO (os primeiros bytes e a estrutura interna), não pelo nome.
- Cada leitor declara os tipos que lê; um leitor novo entra registrando-se, sem mudar nenhum outro arquivo.
- Todo leitor entrega o mesmo formato (Leitura): o texto literal por página, os links, as tabelas, os dados
  estruturados, os alertas e as páginas que precisam de OCR.
- Tipo sem leitor: vai à reserva (o leitor universal, quando ligado) ou é erro claro (nunca silêncio).
- O texto é mantido íntegro, como publicado na fonte (titular, 22/10/2026): o sistema capta só dados públicos e não
  filtra, anonimiza nem exclui dado algum; a responsabilidade pelo que foi publicado é da fonte.
"""
from __future__ import annotations

import hashlib
import io
import json
import zipfile
from dataclasses import dataclass, field
from typing import Any, Protocol

from charset_normalizer import from_bytes


@dataclass
class Pagina:
    numero: int
    texto: str
    expurgado: int = 0                 # caracteres retirados pelo expurgo seguro (cabeçalho e rodapé repetidos)


@dataclass
class Leitura:
    tipo: str
    leitor: str
    sha256: str
    paginas: list[Pagina] = field(default_factory=list)
    links: list[str] = field(default_factory=list)
    tabelas: list[list[list[str]]] = field(default_factory=list)
    dados: dict[str, Any] = field(default_factory=dict)
    alertas: list[str] = field(default_factory=list)
    precisa_ocr: list[int] = field(default_factory=list)
    internos: list[tuple[str, "Leitura"]] = field(default_factory=list)

    @property
    def texto(self) -> str:
        return "\n\n".join(p.texto for p in self.paginas)


LIGADURAS = {0xFB00: "ff", 0xFB01: "fi", 0xFB02: "fl", 0xFB03: "ffi", 0xFB04: "ffl", 0xFB05: "st", 0xFB06: "st"}


def sem_ligaduras(texto: str) -> str:
    """As ligaduras tipográficas dos PDF ("ﬁ" de "beneﬁcio") viram as letras: a mesma palavra, como publicada."""
    return texto.translate(LIGADURAS)


class SemLeitor(Exception):
    pass


class Leitor(Protocol):
    nome: str
    tipos: tuple[str, ...]

    def ler(self, conteudo: bytes, nome: str | None, registro: "Registro") -> Leitura: ...


def decodificar(conteudo: bytes) -> str:
    """Bytes em texto, com a codificação certa (páginas antigas em latin-1, windows-1252...)."""
    try:
        return conteudo.decode("utf-8")
    except UnicodeDecodeError:
        pass
    try:                                         # documentos brasileiros: windows-1252 cobre o latin-1 do português
        return conteudo.decode("cp1252")
    except UnicodeDecodeError:
        melhor = from_bytes(conteudo).best()
        return str(melhor) if melhor else conteudo.decode("latin-1")


def detectar_tipo(conteudo: bytes, nome: str | None = None) -> str:
    c = conteudo[:8]
    nome = (nome or "").lower()
    if c.startswith(b"%PDF"):
        return "pdf"
    if c.startswith(b"PK\x03\x04"):
        try:
            with zipfile.ZipFile(io.BytesIO(conteudo)) as z:
                nomes = set(z.namelist())
                if "word/document.xml" in nomes:
                    return "docx"
                if "xl/workbook.xml" in nomes:
                    return "xlsx"
                if "ppt/presentation.xml" in nomes:
                    return "pptx"
                if "mimetype" in nomes:
                    m = z.read("mimetype").decode(errors="ignore")
                    if "opendocument.text" in m:
                        return "odt"
                    if "opendocument.spreadsheet" in m:
                        return "ods"
        except zipfile.BadZipFile:
            return "desconhecido"
        return "zip"
    if c.startswith(b"7z\xbc\xaf\x27\x1c"):
        return "7z"
    if c.startswith(b"Rar!"):
        return "rar"
    if c.startswith(b"\xd0\xcf\x11\xe0"):
        return "xls" if nome.endswith((".xls", ".xlt")) or not nome.endswith(".doc") else "doc"
    if c.startswith((b"\x89PNG", b"\xff\xd8\xff", b"GIF8", b"II*\x00", b"MM\x00*")) or (c[:4] == b"RIFF" and conteudo[8:12] == b"WEBP"):
        return "imagem"
    inicio = decodificar(conteudo[:4096]).lstrip("\ufeff \t\r\n").lower()
    if inicio.startswith(("<!doctype html", "<html")) or "<body" in inicio[:2000] or "<head" in inicio[:2000]:
        return "html"
    if inicio.startswith(("<?xml", "<rss", "<feed", "<urlset", "<sitemapindex")):
        return "xml"
    if inicio.startswith(("{", "[")):
        try:
            json.loads(decodificar(conteudo))
            return "json"
        except ValueError:
            pass
    if nome.endswith((".csv", ".tsv")):
        return "csv"
    return "texto"


class Registro:
    def __init__(self, universal: Leitor | None = None):
        self._por_tipo: dict[str, Leitor] = {}
        self.universal = universal
        self.profundidade = 0                 # quantos compactados dentro de compactados estão sendo lidos

    def registrar(self, leitor: Leitor) -> None:
        for t in leitor.tipos:
            self._por_tipo[t] = leitor

    def tipos(self) -> list[str]:
        return sorted(self._por_tipo)

    def ler(self, conteudo: bytes, nome: str | None = None, profundidade: int = 0) -> Leitura:
        tipo = detectar_tipo(conteudo, nome)
        leitor = self._por_tipo.get(tipo)
        if leitor is None:
            if self.universal is None:
                raise SemLeitor(f"nenhum leitor para o tipo '{tipo}' ({nome or 'sem nome'})")
            leitor = self.universal
        anterior, self.profundidade = self.profundidade, profundidade
        try:
            r = leitor.ler(conteudo, nome, self)
        finally:
            self.profundidade = anterior
        r.tipo = tipo
        for p in r.paginas:
            p.texto = sem_ligaduras(p.texto)
        from ...base.nucleo.seguranca import injecao
        trecho = next((t for p in r.paginas if (t := injecao(p.texto))), None)
        if trecho:                                                  # o texto fica íntegro; a leitura recebe a marca
            r.dados["injecao"] = trecho
            r.alertas.append(f"padrão de injeção de instruções: “{trecho[:160]}”")
        return r


def sha256(conteudo: bytes) -> str:
    return hashlib.sha256(conteudo).hexdigest()


def padrao() -> Registro:
    """O registro com todos os leitores obrigatórios (o OCR e o universal entram quando instalados e ligados)."""
    from . import compactado, documento, pagina, pdf, planilha
    r = Registro()
    leitores = (pagina.LeitorPagina(), pagina.LeitorTexto(), pdf.LeitorPDF(), planilha.LeitorPlanilha(), documento.LeitorDocumento(),
                compactado.LeitorCompactado())
    for leitor in leitores:
        r.registrar(leitor)
    return r
