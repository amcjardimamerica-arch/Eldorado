"""O leitor de áudio e vídeo (plano C: faster-whisper): transcreve em português as transmissões e os vídeos que anunciam
editais (lives de secretarias, audiências). Modelo pequeno, em CPU (int8); carregado só no primeiro uso."""
from __future__ import annotations

import tempfile

from .leitores import Leitura, Pagina, Registro, SemLeitor, sha256


class LeitorAudio:
    nome = "áudio e vídeo (faster-whisper)"
    tipos = ("audio",)

    def __init__(self, modelo: str = "small"):
        try:
            import faster_whisper  # noqa: F401
        except ImportError as e:
            raise SemLeitor("leitor de áudio desligado: instale o faster-whisper") from e
        self.modelo, self._m = modelo, None

    def ler(self, conteudo: bytes, nome: str | None, registro: Registro) -> Leitura:
        from faster_whisper import WhisperModel
        if self._m is None:
            self._m = WhisperModel(self.modelo, device="cpu", compute_type="int8")
        with tempfile.NamedTemporaryFile(suffix=".media") as f:
            f.write(conteudo)
            f.flush()
            segmentos, _ = self._m.transcribe(f.name, language="pt", vad_filter=True)
            texto = " ".join(s.text.strip() for s in segmentos)
        partes = [texto[i:i + 3000] for i in range(0, len(texto), 3000)] or [""]
        return Leitura(tipo="audio", leitor=self.nome, sha256=sha256(conteudo), paginas=[Pagina(n + 1, t) for n, t in enumerate(partes)],
                       alertas=["transcrição automática (faster-whisper): conferir os trechos"])
