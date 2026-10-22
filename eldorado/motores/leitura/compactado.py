"""Arquivos ZIP, 7Z e RAR: abre e entrega cada arquivo interno ao leitor do seu tipo.

Limites (contra arquivos maliciosos que esgotariam a máquina): até 200 arquivos, até 200 MB descompactados no total,
até 2 níveis de compactado dentro de compactado. O que passa do limite é alertado, nunca lido às cegas.
"""
from __future__ import annotations

import io
import zipfile

from .leitores import Leitura, Registro, SemLeitor, detectar_tipo, sha256

MAX_ARQUIVOS = 200
MAX_BYTES = 200 * 1024 * 1024
MAX_PROFUNDIDADE = 2


class LeitorCompactado:
    nome = "compactado (zipfile, py7zr, rarfile)"
    tipos = ("zip", "7z", "rar")

    def _membros(self, conteudo: bytes, tipo: str):
        if tipo == "zip":
            z = zipfile.ZipFile(io.BytesIO(conteudo))
            return [(i.filename, i.file_size, (lambda n=i.filename: z.read(n))) for i in z.infolist() if not i.is_dir()]
        if tipo == "7z":
            import py7zr
            from py7zr.io import BytesIOFactory
            with py7zr.SevenZipFile(io.BytesIO(conteudo)) as z:
                infos = [(i.filename, i.uncompressed or 0) for i in z.list() if not i.is_directory]
            cache: dict[str, bytes] = {}

            def ler7(nome: str) -> bytes:
                if not cache:                          # o 7Z é comprimido em bloco: lê tudo de uma vez, dentro do limite
                    fabrica = BytesIOFactory(limit=MAX_BYTES)
                    with py7zr.SevenZipFile(io.BytesIO(conteudo)) as z2:
                        z2.extract(targets=[n for n, _ in infos], factory=fabrica)
                    cache.update({n: b.read() for n, b in fabrica.products.items()})
                return cache[nome]
            return [(n, t, (lambda n=n: ler7(n))) for n, t in infos]
        import rarfile
        z = rarfile.RarFile(io.BytesIO(conteudo))
        return [(i.filename, i.file_size, (lambda n=i.filename: z.read(n))) for i in z.infolist() if not i.is_dir()]

    def ler(self, conteudo: bytes, nome: str | None, registro: Registro) -> Leitura:
        tipo = detectar_tipo(conteudo, nome)
        r = Leitura(tipo=tipo, leitor=self.nome, sha256=sha256(conteudo))
        if registro.profundidade >= MAX_PROFUNDIDADE:
            r.alertas.append(f"compactado dentro de compactado além de {MAX_PROFUNDIDADE} níveis: não aberto")
            return r
        try:
            membros = self._membros(conteudo, tipo)
        except Exception as e:  # noqa: BLE001 — arquivo corrompido ou extrator ausente: alerta, nunca silêncio
            r.alertas.append(f"{tipo} não aberto: {type(e).__name__}: {e}")
            return r
        if len(membros) > MAX_ARQUIVOS:
            r.alertas.append(f"{len(membros)} arquivos: só os {MAX_ARQUIVOS} primeiros lidos")
            membros = membros[:MAX_ARQUIVOS]
        total = sum(t for _, t, _ in membros)
        if total > MAX_BYTES:
            r.alertas.append(f"{total // 1024 // 1024} MB descompactados (limite {MAX_BYTES // 1024 // 1024} MB): não aberto")
            return r
        for nome_interno, _, ler in membros:
            try:
                r.internos.append((nome_interno, registro.ler(ler(), nome_interno, registro.profundidade + 1)))
            except SemLeitor as e:
                r.alertas.append(str(e))
        r.dados["arquivos"] = [n for n, _, _ in membros]
        return r
