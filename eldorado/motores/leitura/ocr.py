"""O OCR (reserva, extra 'ocr'): RapidOCR, leve; só para o PDF digitalizado e as imagens.

Não faz parte da instalação obrigatória (traz o OpenCV, 16 pacotes). Sem ele, as páginas digitalizadas ficam
marcadas e o alerta diz que aguardam OCR; nada é descartado.
"""
from __future__ import annotations

from .leitores import Leitura, Pagina, Registro, sha256


class OCRIndisponivel(Exception):
    pass


class OCRDemorou(Exception):
    """17/11/2026 (manutenção): o OCR passou do tempo da página — a leitura segue sem ela (a página fica «aguardando OCR»)."""


# 17/11/2026 (manutenção): o OCR com tempo limite — uma leitura de OCR que não termina prendia a passagem e travou a
# Qualidade (o motor dos estaduais de Goiás preso no OCR de um PDF por mais de 45 min)
OCR_PAGINA_S, OCR_DOCUMENTO_S = 30.0, 60.0


class OCR:
    """O OCR do plano: o RapidOCR (leve, ONNX) e, de reserva, o Tesseract com português (tesserocr)."""

    def __init__(self):
        self.nome, self._motor, self._tess = None, None, None
        try:
            from rapidocr import RapidOCR
            self._motor, self.nome = RapidOCR(), "RapidOCR"
        except Exception:  # noqa: BLE001 — sem o RapidOCR, a reserva
            try:
                import tesserocr
                self._tess, self.nome = tesserocr, "Tesseract (por)"
            except ImportError as e:
                raise OCRIndisponivel("OCR desligado: instale o extra 'ocr' (RapidOCR) ou o Tesseract (tesserocr)") from e

    def texto(self, imagem: bytes, limite_s: float = OCR_PAGINA_S) -> str:
        if self._motor is not None:
            import threading
            saida: dict = {}

            def _ler():
                try:
                    saida["r"] = self._motor(imagem)
                except Exception as e:  # noqa: BLE001
                    saida["e"] = e
            t = threading.Thread(target=_ler, daemon=True)     # a leitura que passar do tempo segue sozinha, sem prender ninguém
            t.start()
            t.join(limite_s)
            if t.is_alive():
                raise OCRDemorou(f"o OCR passou de {limite_s:.0f} s na página")
            if "e" in saida:
                raise saida["e"]
            return "\n".join(getattr(saida.get("r"), "txts", None) or [])
        import io

        from PIL import Image
        return self._tess.image_to_text(Image.open(io.BytesIO(imagem)), lang="por")


_OCR: OCR | None | bool = False


def disponivel() -> OCR | None:
    """O OCR instalado (um só por processo), ou None."""
    global _OCR
    if _OCR is False:
        try:
            _OCR = OCR()
        except OCRIndisponivel:
            _OCR = None
    return _OCR


class LeitorImagem:
    nome = "imagem (OCR)"
    tipos = ("imagem",)

    def __init__(self, ocr: OCR):
        self.ocr = ocr

    def ler(self, conteudo: bytes, nome: str | None, registro: Registro) -> Leitura:
        try:
            texto = self.ocr.texto(conteudo)
        except Exception as e:  # noqa: BLE001 — 26/10/2026: a imagem que não abre (truncada, corrompida) é "sem leitor", não um erro solto
            from .leitores import SemLeitor
            raise SemLeitor(f"a imagem não pôde ser lida pelo OCR: {type(e).__name__}: {str(e)[:120]}") from e
        return Leitura(tipo="imagem", leitor=self.nome, sha256=sha256(conteudo), paginas=[Pagina(1, texto)])
