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
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import msgspec
import zstandard

from ..missao import itens as I
from ..nucleo.contratos import Achado, Missao
from ..nucleo.eventos import Diario, agora
from ..nucleo.registro import instanciar
from . import auditoria, origem, selos
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

    def _edicoes(self, livro: str, atual: Achado | None) -> list[selos.Edicao]:
        anos: dict[int, selos.Edicao] = {}
        linhas: list[tuple[str | None, str | None, str | None]] = []
        if self.con is not None:
            linhas = [tuple(r) for r in self.con.execute("SELECT publicado_em, encontrado_em, link_oficial FROM achado WHERE livro_id=?", (livro,))]
        if atual is not None:
            linhas.append((atual.publicado_em, atual.encontrado_em, atual.link_oficial))
        orgao_livro = self._livro(livro, atual).get("orgao") or ""
        for pub, enc, oficial in linhas:
            data = pub or enc
            if data and str(data)[:4].isdigit():
                ano = int(str(data)[:4])
                e = selos.Edicao(ano, bool(oficial and origem.evidencia(oficial, orgao_livro)), bool(pub))   # a origem confirmada pela evidência
                anos[ano] = max(anos.get(ano, e), e, key=lambda x: (x.pagina_oficial, x.data))
        return list(anos.values())

    def _origem(self, livro: str, a: Achado) -> str | None:
        """A divulgação sempre; o link de origem candidato (a busca cega do motor) sem nunca trocar um confirmado; e a origem
        do livro decidida com a evidência do próprio livro (titular, 23/10/2026). Devolve o link confirmado, se houver."""
        atual_link, atual_origem, validado = None, None, False
        if self.con is not None:
            r = self.con.execute("SELECT l.link_oficial, d.origem, d.livro_id FROM livro l LEFT JOIN livro_dados d ON d.livro_id = l.id WHERE l.id = ?",
                                 (livro,)).fetchone()
            if r:
                atual_link, atual_origem, validado = r[0], r[1], r[2] is not None
        link = atual_link if (atual_origem == origem.CONFIRMADO and atual_link) else (a.link_oficial or atual_link)
        self.diario.emitir("livro.links", "cartorio", {"id": livro, "link_divulgacao": a.link_divulgacao, "link_oficial": link, "atualizado_em": agora()})
        certs = self._certidoes(livro)
        orgao = (certs.get("Órgão / financiador") or {}).get("valor") or self._livro(livro, a).get("orgao") or (a.dados or {}).get("orgao")
        cls, motivo = origem.classificar(link, orgao, (a.dados or {}).get("localidade"),
                                         confirmado_antes=(atual_origem == origem.CONFIRMADO and link == atual_link))
        if validado:                                                # no livro novo, a validação (auditoria) registra a origem no mesmo ciclo
            self.diario.emitir("livro.origem", "cartorio", {"livro_id": livro, "origem": cls, "origem_motivo": motivo[:300]})
        return link if cls == origem.CONFIRMADO else None

    def _livro(self, livro: str, a: Achado | None) -> dict[str, Any]:
        r = None
        if self.con is not None:
            self.con.row_factory = sqlite3.Row
            r = self.con.execute("SELECT titulo, orgao, uf, link_oficial, selo_livro FROM livro WHERE id=?", (livro,)).fetchone()
        if r:
            return dict(r)
        if a is None:
            return {"titulo": None, "orgao": None, "uf": None, "link_oficial": None, "selo_livro": None}
        return {"titulo": a.titulo, "orgao": (a.dados or {}).get("orgao"), "uf": (a.dados or {}).get("uf"), "link_oficial": a.link_oficial, "selo_livro": None}

    def processar(self, achados: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """A linha de produção: a informação recebida passa pelas etapas na ordem, sem pular nenhuma; cada etapa
        concluída deixa o seu relatório no livro. O Cartório valida e armazena; não busca e não decide quem age."""
        saida = []
        for bruto in achados:
            a = msgspec.convert({k: v for k, v in bruto.items() if not k.startswith("_")}, Achado)
            # ETAPA 1 · recepção: liga a informação a um livro (a pedida pela rede para um livro vai direto a ele)
            pedido = (a.dados or {}).get("livro_id")
            if pedido and self.passaporte.fase(pedido) is not None:
                livro, novo, como = pedido, False, f"informação adicional pedida pela rede ({a.motor})"
                self.diario.emitir("livro.vinculado", "cartorio", {"achado_id": a.id, "livro_id": livro})
            else:
                livro, novo, como = self.indice.resolver(a)
            fase = self.passaporte.fase(livro)
            antes = I.faltando({k: v for k, v in self._certidoes(livro).items() if I.resolvido(v)})
            if fase in (None, "arquivo"):                          # livro novo, ou nova oportunidade de um livro arquivado
                self.passaporte.mover(livro, "recepcao", "livro novo" if fase is None else "nova oportunidade para o livro arquivado",
                                      {"gerou": f"nova oportunidade recebida de {a.motor}: {a.titulo[:120]}"} if fase else None)
                fase = "recepcao"
            if fase == "recepcao":
                self.passaporte.mover(livro, "certificacao", "etapa 2: certificar e classificar",
                                      {"gerou": f"informação de {a.motor} ligada ao livro ({como})",
                                       "faltou": None if a.link_oficial else "a origem (só a divulgação): a rede aprofunda"})
                fase = "certificacao"
            elif fase in ("preparacao", "analise externa"):
                self.passaporte.mover(livro, "validacao", f"etapa 4: validar a informação adicional ({a.motor})",
                                      {"gerou": f"pedido atendido por {a.motor}: {como}", "faltou": ", ".join(antes) or None,
                                       "analise": "externa" if fase == "analise externa" else "interna"})
                fase = "validacao"
            oficial = self._origem(livro, a)
            for lei in (a.dados or {}).get("leis") or []:                # a legislação que rege o programa
                if self.con is not None and self.con.execute("SELECT 1 FROM lei WHERE id=?", (lei,)).fetchone() is None:
                    self.diario.emitir("alarme.aberto", "cartorio", {"gravidade": "baixa", "modulo": a.motor, "aberto_em": agora(),
                                                                     "mensagem": f"lei {lei} citada pelo motor não está na Biblioteca"})
                    continue
                self.diario.emitir("livro.legislacao", "cartorio", {"livro_id": livro, "lei_id": lei, "papel": "rege o programa", "em": agora()})
            # ETAPA 2 (ou 4) · certificar e classificar: a estrela é da oportunidade aberta; o selo do livro, do histórico
            certidoes = self._certidoes(livro)
            sha = (a.dados or {}).get("documento_sha256") or a.documento_sha256 or (a.documento or {}).get("sha256")
            resolvidos = {k for k, c in certidoes.items() if I.resolvido(c)}
            novas = self._do_motor(livro, a, resolvidos)                           # a extração própria do motor, primeiro
            pular = resolvidos | set(novas) | set((a.dados or {}).get("nao_certificar") or [])
            novas.update(self.certificacao.certificar(livro, self._paginas(sha), pular))
            certidoes.update(novas)
            dados_livro = self._livro(livro, a)
            situacao = auditoria.prazo({k: v for k, v in certidoes.items() if I.resolvido(v)}, dados_livro, date.fromisoformat(agora()[:10]))
            estrela, selo = selos.calcular(self.diario, livro, certidoes, self._edicoes(livro, a), self.ano, situacao, dados_livro.get("selo_livro"))
            faltam = I.faltando({k: v for k, v in certidoes.items() if I.resolvido(v)})
            relatorio = {"gerou": f"{len(novas)} item(ns) certificado(s) ({', '.join(sorted(novas)) or 'nenhum'}); prazo {situacao}; estrela {estrela}; "
                                  f"selo do livro {selo}", "faltou": ", ".join(faltam) or None,
                         "aprendeu": None if oficial else "a origem ainda não confirmada: a rede aprofunda (Interceptador e Chrome)"}
            if fase in ("certificacao", "validacao"):
                if situacao == "encerrada":
                    self.passaporte.mover(livro, "arquivo", "oportunidade arquivada: a estrela virou o selo do livro; aguarda nova oportunidade", relatorio)
                elif not faltam:
                    self.passaporte.mover(livro, "farol", "estrela de ouro com prazo em aberto: ao Farol (a segunda metade do sistema)", relatorio)
                else:
                    self.passaporte.mover(livro, "preparacao", f"etapa 3: o pedido à rede neural — faltam {', '.join(faltam)}", relatorio)
            elif fase == "farol" and situacao == "encerrada":
                self.passaporte.mover(livro, "arquivo", "a oportunidade encerrou: a estrela virou o selo do livro", relatorio)
            saida.append({"livro": livro, "novo": novo, "como": como, "estrela": estrela, "selo_livro": selo, "faltam": faltam, "prazo": situacao,
                          "etapa": self.passaporte.fase(livro), "_linhagem": {"livro": livro, "achado": a.id}})
        return saida


    def revalidar(self, livro: str, extras: dict[str, dict], gerou: str, analise: str = "externa") -> dict[str, Any]:
        """A validação depois da análise externa (etapa 5 → 4): as certidões e dispensas que o veredito trouxe, junto com
        as do livro; ouro com prazo aberto → Farol; encerrada → arquivo; faltando, volta à etapa 5, à espera."""
        if self.passaporte.fase(livro) == "analise externa":
            self.passaporte.mover(livro, "validacao", "etapa 4: validar o veredito da análise externa", {"gerou": gerou, "analise": analise})
        certidoes = {**self._certidoes(livro), **extras}
        validas = {k: v for k, v in certidoes.items() if I.resolvido(v)}
        dados_livro = self._livro(livro, None)
        situacao = auditoria.prazo(validas, dados_livro, date.fromisoformat(agora()[:10]))
        estrela, selo = selos.calcular(self.diario, livro, certidoes, self._edicoes(livro, None), self.ano, situacao, dados_livro.get("selo_livro"))
        faltam = I.faltando(validas)
        rel = {"gerou": f"validado após a análise externa: prazo {situacao}; estrela {estrela}; selo do livro {selo}", "faltou": ", ".join(faltam) or None}
        if self.passaporte.fase(livro) == "validacao":
            if situacao == "encerrada":
                self.passaporte.mover(livro, "arquivo", "oportunidade arquivada: a estrela virou o selo do livro", rel)
            elif not faltam:
                self.passaporte.mover(livro, "farol", "estrela de ouro com prazo em aberto: ao Farol", rel)
            else:
                self.passaporte.mover(livro, "analise externa", f"ainda faltam {', '.join(faltam)}: aguarda novo veredito", rel)
        return {"livro": livro, "estrela": estrela, "selo_livro": selo, "prazo": situacao, "faltam": faltam, "etapa": self.passaporte.fase(livro)}


def no_cartorio(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    p = Path(parametros.get("dados", "dados")) / "biblioteca.db"
    con = sqlite3.connect(f"file:{p}?mode=ro", uri=True) if p.exists() else None
    try:
        missao = instanciar(parametros.get("missao", "eldorado.base.missao.oportunidades:MissaoOportunidades"), parametros.get("missao_parametros"))
        return Cartorio(con, missao, contexto.diario).processar(itens)
    finally:
        if con is not None:
            con.close()
