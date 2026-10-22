"""O OCR (reserva, extra 'ocr'): RapidOCR, leve; só para o PDF digitalizado e as imagens.

Não faz parte da instalação obrigatória (traz o OpenCV, 16 pacotes). Sem ele, as páginas digitalizadas ficam
marcadas e o alerta diz que aguardam OCR; nada é descartado.
"""
from __future__ import annotations

from .leitores import Leitura, Pagina, Registro, sha256


class OCRIndisponivel(Exception):
    pass


class OCR:
    def __init__(self):
        try:
            from rapidocr import RapidOCR
        except ImportError as e:
            raise OCRIndisponivel("OCR desligado: instale o extra 'ocr' (pip install eldorado[ocr])") from e
        self._motor = RapidOCR()

    def texto(self, imagem: bytes) -> str:
        r = self._motor(imagem)
        return "\n".join(getattr(r, "txts", None) or [])


class LeitorImagem:
    nome = "imagem (OCR)"
    tipos = ("imagem",)

    def __init__(self, ocr: OCR):
        self.ocr = ocr

    def ler(self, conteudo: bytes, nome: str | None, registro: Registro) -> Leitura:
        return Leitura(tipo="imagem", leitor=self.nome, sha256=sha256(conteudo), paginas=[Pagina(1, self.ocr.texto(conteudo))])
