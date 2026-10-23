"""O Cartório (titular, 22/10/2026): o ORGANIZADOR. Ele não busca nada: é onde o livro recebe informação nova, é
certificado e classificado (o selo do livro, pelo histórico; a estrela, pela oportunidade aberta) e fica na fase em
que está. Quem age é a rede neural, que aciona o motor da oportunidade ou o Interceptador.

As 5 fases: 1 recepção (liga a informação a um livro); 2 certificação (certifica e classifica); 3 preparação (o pedido
do que falta, para a rede neural); 4 validação (valida a informação adicional e atualiza); 5 análise externa (o Claude no
Chrome, que pode dispensar um item, com o aprendizado). Com todas as informações (estrela de ouro), na fase 2 ou 4,
o livro vai ao Farol, a segunda metade do sistema.

"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import msgspec
import zstandard

from ..missao import itens as I
from ..nucleo.contratos import Achado, Missao
from ..nucleo.eventos import Diario, agora
from ..nucleo.registro import instanciar
from . import selos, site_oficial
from .certificacao import Certificacao, Pagina
from .indice import Indice
from .passaporte import Passaporte

_dz = zstandard.ZstdDecompressor()


class Cartorio:
    def __init__(self, biblioteca: sqlite3.Connection | None, missao: Missao, diario: Diario, ano_atual: int | None = None):
        self.con, self.diario = biblioteca, diario
        self.indice = Indice(biblioteca, missao, diario)
        self.passaporte = Passaporte(biblioteca, diario)
        self.certificacao = Certificacao(diario)
        self.ano = ano_atual or datetime.now(timezone.utc).year

    def _do_motor(self, livro: str, a: Achado, resolvidos: set[str]) -> dict[str, dict]:
        """Os itens que o motor extraiu com as suas próprias regras (com o valor, o trecho e a página)."""
        novas: dict[str, dict] = {}
        for item, x in ((a.dados or {}).get("itens") or {}).items():
            if item in resolvidos or item not in I.DOZE or not x.get("valor"):
                continue
            c = {"livro_id": livro, "item": item, "valor": str(x["valor"])[:300], "trecho": str(x.get("trecho") or "")[:500], "pagina": x.get("pagina"),
                 "fase": "certificacao", "situacao": "comprovado", "em": agora()}
            self.diario.emitir("certidao.gravada", "cartorio", c)
            novas[item] = c
        return novas

    def _paginas(self, sha256: str | None) -> list[Pagina]:
        if not sha256 or self.con is None:
            return []
        r = self.con.execute("SELECT id FROM documento WHERE sha256=?", (sha256,)).fetchone()
        if not r:
            return []
        return [Pagina(r[0], n, _dz.decompress(t).decode("utf-8")) for n, t in
                self.con.execute("SELECT numero, texto_zstd FROM pagina WHERE documento_id=? ORDER BY numero", (r[0],))]

    def _certidoes(self, livro: str) -> dict[str, dict]:
        if self.con is None:
            return {}
        self.con.row_factory = sqlite3.Row
        return I.melhor([dict(c) for c in self.con.execute("SELECT * FROM certidao WHERE livro_id=? AND situacao IN ('comprovado','dispensado')", (livro,))])

    def _edicoes(self, livro: str, atual: Achado) -> list[selos.Edicao]:
        anos: dict[int, selos.Edicao] = {}
        linhas: list[tuple[str | None, str | None, str | None]] = []
        if self.con is not None:
            linhas = [tuple(r) for r in self.con.execute("SELECT publicado_em, encontrado_em, link_oficial FROM achado WHERE livro_id=?", (livro,))]
        linhas.append((atual.publicado_em, atual.encontrado_em, atual.link_oficial))
        for pub, enc, oficial in linhas:
            data = pub or enc
            if data and str(data)[:4].isdigit():
                ano = int(str(data)[:4])
                e = selos.Edicao(ano, bool(oficial and site_oficial.eh_fonte(oficial)), bool(pub))
                anos[ano] = max(anos.get(ano, e), e, key=lambda x: (x.pagina_oficial, x.data))
        return list(anos.values())

    def processar(self, achados: list[dict[str, Any]]) -> list[dict[str, Any]]:
        saida = []
        for bruto in achados:
            a = msgspec.convert({k: v for k, v in bruto.items() if not k.startswith("_")}, Achado)
            # FASE 1 · recepção: liga a informação a um livro (a pedida pela rede para um livro vai direto a ele)
            pedido = (a.dados or {}).get("livro_id")
            if pedido and self.passaporte.fase(pedido) is not None:
                livro, novo, como = pedido, False, f"informação adicional pedida pela rede ({a.motor})"
                self.diario.emitir("livro.vinculado", "cartorio", {"achado_id": a.id, "livro_id": livro})
            else:
                livro, novo, como = self.indice.resolver(a)
            fase = self.passaporte.fase(livro)
            if fase is None:
                self.passaporte.mover(livro, "recepcao", "livro novo (fase 1)")
                fase = "recepcao"
            if fase == "recepcao":
                self.passaporte.mover(livro, "certificacao", "fase 2: certificar e classificar")
                fase = "certificacao"
            elif fase in ("preparacao", "analise externa"):
                self.passaporte.mover(livro, "validacao", f"fase 4: validar a informação adicional ({a.motor})")
                fase = "validacao"
            oficial = site_oficial.escolher([a.link_oficial, a.link_divulgacao])
            if oficial:
                self.diario.emitir("livro.links", "cartorio", {"id": livro, "link_divulgacao": a.link_divulgacao, "link_oficial": oficial,
                                                               "atualizado_em": agora()})
            for lei in (a.dados or {}).get("leis") or []:                # a legislação que rege o programa
                if self.con is not None and self.con.execute("SELECT 1 FROM lei WHERE id=?", (lei,)).fetchone() is None:
                    self.diario.emitir("alarme.aberto", "cartorio", {"gravidade": "baixa", "modulo": a.motor, "aberto_em": agora(),
                                                                     "mensagem": f"lei {lei} citada pelo motor não está na Biblioteca"})
                    continue
                self.diario.emitir("livro.legislacao", "cartorio", {"livro_id": livro, "lei_id": lei, "papel": "rege o programa", "em": agora()})
            certidoes = self._certidoes(livro)
            sha = (a.dados or {}).get("documento_sha256") or a.documento_sha256 or (a.documento or {}).get("sha256")
            resolvidos = {k for k, c in certidoes.items() if I.resolvido(c)}
            novas = self._do_motor(livro, a, resolvidos)                           # a extração própria do motor, primeiro
            pular = resolvidos | set(novas) | set((a.dados or {}).get("nao_certificar") or [])
            novas.update(self.certificacao.certificar(livro, self._paginas(sha), pular))
            certidoes.update(novas)
            estrela, selo = selos.calcular(self.diario, livro, certidoes, self._edicoes(livro, a), self.ano)
            faltam = I.faltando(certidoes)
            self.diario.emitir("relatorio.etapa", "cartorio", {
                "livro_id": livro, "fase": fase, "em": agora(), "analise": "interna",
                "gerou": f"{len(novas)} item(ns) certificado(s); estrela {estrela}; selo do livro {selo}; {como}",
                "aprendeu": None if oficial else "só pistas: falta o link oficial", "faltou": ", ".join(faltam) or None})
            # o Cartório não busca: com todas as informações, ao Farol; senão, à fase 3, com o pedido para a rede neural
            if fase in ("certificacao", "validacao"):
                if not faltam:
                    self.passaporte.mover(livro, "farol", "todas as informações: estrela de ouro (a segunda metade do sistema)")
                else:
                    self.passaporte.mover(livro, "preparacao", f"fase 3: pedido à rede neural — faltam {', '.join(faltam)}")
            saida.append({"livro": livro, "novo": novo, "como": como, "estrela": estrela, "selo_livro": selo, "faltam": faltam,
                          "_linhagem": {"livro": livro, "achado": a.id}})
        return saida


def no_cartorio(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    p = Path(parametros.get("dados", "dados")) / "biblioteca.db"
    con = sqlite3.connect(f"file:{p}?mode=ro", uri=True) if p.exists() else None
    try:
        missao = instanciar(parametros.get("missao", "eldorado.base.missao.oportunidades:MissaoOportunidades"), parametros.get("missao_parametros"))
        return Cartorio(con, missao, contexto.diario).processar(itens)
    finally:
        if con is not None:
            con.close()
