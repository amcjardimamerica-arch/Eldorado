"""O leitor de PDF: o texto literal por página (com o expurgo seguro), as tabelas e as páginas que precisam de OCR.

PyMuPDF 1.28.2 (267 a 285 páginas/s medido com a versão fixada; 10 mil páginas em cerca de 0,6 min). Reserva:
pypdfium2, quando o PyMuPDF não abre o arquivo. Página digitalizada (quase sem texto e com imagem) é marcada para OCR;
se o OCR estiver ligado, é lida por ele.

As tabelas: o texto delas já está no texto literal. A ESTRUTURA (linhas e colunas) custa cerca de 0,1 s por página
(medido: 9 a 12 páginas/s), então é sob demanda: tabelas="nao" (padrão, na leitura de todo documento), "uteis" (só nas
páginas com cronograma, valores, etapas ou prazos, para os documentos oficiais que viraram livro) ou "todas".
"""
from __future__ import annotations

import re

import pymupdf

from . import expurgo
from .leitores import Leitura, Pagina, Registro, sha256

MIN_CARACTERES = 25
TABELA_UTIL = re.compile(r"(?i)cronograma|R\$\s*\d|\betapas?\b|\bprazos?\b|inscri[çc]|valor (?:total|global|m[áa]ximo)|resultado")


class LeitorPDF:
    nome = "pdf (PyMuPDF)"
    tipos = ("pdf",)

    def __init__(self, tabelas: str = "nao", ocr=None):
        if tabelas not in ("nao", "uteis", "todas"):
            raise ValueError("tabelas: 'nao', 'uteis' ou 'todas'")
        self.tabelas = tabelas
        self.ocr = ocr

    def ler(self, conteudo: bytes, nome: str | None, registro: Registro) -> Leitura:
        r = Leitura(tipo="pdf", leitor=self.nome, sha256=sha256(conteudo))
        try:
            doc = pymupdf.open(stream=conteudo, filetype="pdf")
        except Exception as e:  # noqa: BLE001 — arquivo que o PyMuPDF não abre vai à reserva, com alerta
            r.alertas.append(f"PyMuPDF não abriu ({type(e).__name__}); lido pela reserva pypdfium2")
            return self._reserva(conteudo, r)
        if doc.needs_pass and not doc.authenticate(""):
            r.alertas.append("PDF protegido por senha: não lido")
            return r
        paginas = []
        com_imagem: set[int] = set()
        for pg in doc:
            h = pg.rect.height or 1
            blocos = [expurgo.Bloco(b[1], b[3], b[4]) for b in pg.get_text("blocks") if b[6] == 0]
            paginas.append((h, blocos))
            if pg.get_images():
                com_imagem.add(pg.number + 1)
            for ln in pg.get_links():
                if ln.get("uri"):
                    r.links.append(ln["uri"])
            if self.tabelas == "todas" or (self.tabelas == "uteis" and TABELA_UTIL.search(" ".join(b.texto for b in blocos))):
                try:
                    for t in pg.find_tables().tables:
                        r.tabelas.append([[str(c or "").strip() for c in linha] for linha in t.extract()])
                except Exception as e:  # noqa: BLE001 — a falha da tabela não perde o texto, mas fica registrada
                    r.alertas.append(f"tabela da página {pg.number + 1} não lida: {type(e).__name__}")
        for i, (texto, removidos) in enumerate(expurgo.aplicar(paginas), 1):
            r.paginas.append(Pagina(i, texto, removidos))
            if i in com_imagem and len(texto.strip()) < MIN_CARACTERES:
                r.precisa_ocr.append(i)                # escaneada: só sobrava o carimbo de impressão (cabeçalho e rodapé)
        try:                                           # a classificação do plano (pdf-inspector): texto, escaneado ou misto
            import pdf_inspector
            c = pdf_inspector.classify_pdf_bytes(conteudo)
            r.dados["pdf_tipo"] = str(c.pdf_type)
            r.dados["pdf_confianca"] = float(c.confidence)
            for n in getattr(c, "pages_needing_ocr", None) or []:
                if n not in r.precisa_ocr and 1 <= n <= len(r.paginas) and len(r.paginas[n - 1].texto.strip()) < 80:
                    r.precisa_ocr.append(n)
        except Exception:  # noqa: BLE001 — sem a biblioteca, segue a detecção própria
            pass
        if r.precisa_ocr and self.ocr is None:         # sem OCR: a extração com layout de reserva (pdf-inspector, markdown)
            try:
                import pdf_inspector
                md = pdf_inspector.extract_pages_markdown_bytes(conteudo, pages=list(r.precisa_ocr))
                for item in md or []:
                    n, texto = getattr(item, "page", None), getattr(item, "markdown", None) or getattr(item, "text", "")
                    if n and texto and len(texto.strip()) > 80 and 1 <= n <= len(r.paginas):
                        r.paginas[n - 1] = Pagina(n, texto)
                        r.precisa_ocr.remove(n)
            except Exception:  # noqa: BLE001
                pass
        if r.precisa_ocr and self.ocr is not None:
            for n in r.precisa_ocr:
                img = doc[n - 1].get_pixmap(dpi=200).tobytes("png")
                r.paginas[n - 1] = Pagina(n, self.ocr.texto(img))
            r.alertas.append(f"{len(r.precisa_ocr)} página(s) lida(s) por OCR")
        elif r.precisa_ocr:
            r.alertas.append(f"{len(r.precisa_ocr)} página(s) digitalizada(s) aguardando OCR (extra 'ocr' desligado)")
        r.dados["paginas"] = doc.page_count
        return r

    @staticmethod
    def _reserva(conteudo: bytes, r: Leitura) -> Leitura:
        import pypdfium2 as pdfium
        try:
            doc = pdfium.PdfDocument(conteudo)
        except Exception as e:  # noqa: BLE001 — ilegível também na reserva: leitura vazia com o alerta, nunca silêncio
            r.alertas.append(f"PDF ilegível também na reserva pypdfium2 ({type(e).__name__})")
            return r
        for i in range(len(doc)):
            r.paginas.append(Pagina(i + 1, doc[i].get_textpage().get_text_range()))
        r.leitor = "pdf (pypdfium2, reserva)"
        return r
