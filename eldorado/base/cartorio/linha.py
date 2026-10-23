"""A linha de produção do Cartório (do Eldorado0, titular, 09/10/2026): os motores descobrem; o Cartório certifica.

Todo livro com qualquer um dos 12 itens em falta entra na fila. A cada batimento, cada livro recebe UMA tentativa, com a
abordagem seguinte da ordem do seu balcão; a fila anda até o tempo do batimento acabar e continua no próximo, até esgotar.

Balcões por selo (o livro passa sozinho ao seguinte quando sobe de selo):
  sem estrela → bronze   foco: o site oficial, o objeto, o prazo de inscrição e o território
  bronze → prata         foco: o valor e os requisitos
  prata → ouro           foco: os demais itens e as dispensas

As 10 abordagens (uma diferente a cada tentativa; sem material para aquele livro, é pulada e não gasta tentativa):
   1 documento na mão          o link oficial e os documentos ligados direto a ele
   2 anexos completos          todos os arquivos do processo (PNCP) e todos os documentos da página oficial
   3 página oficial e citados  o site do órgão mais fundo (até 8 páginas ou documentos a mais)
   4 biblioteca de sites       os sites oficiais já conhecidos do mesmo órgão (de outros livros)
   5 mídia do WordPress        o número do edital na biblioteca de mídia do site oficial
   6 mapa do site              o sitemap do domínio oficial, filtrado por edital e número
   7 releitura                 relê os documentos oficiais já guardados, com as regras de hoje
   8 ponte do titular          refaz pelo computador da titular o que o site recusou à nuvem
   9 leitura profunda          os documentos inteiros, com as tabelas (cronogramas)
  10 busca no domínio          a metabusca restrita ao domínio oficial, pelo número e pelo título
Os itens se acumulam entre as tentativas (a certidão nunca perde o que já achou). Depois da 10ª, o livro passa à
Investigação (o piloto Interceptador). Só grava eventos.
"""
from __future__ import annotations

import json
import re
import sqlite3
import time
from dataclasses import dataclass
from datetime import date
from typing import Any, Callable, Iterator
from urllib.parse import quote, urlsplit

import zstandard

from ...motores.acesso.escada import Bloqueado, Escada, Indisponivel, Pendente
from ...motores.descoberta import fonte_oficial
from ...motores.leitura import leitores
from ...motores.leitura.pdf import LeitorPDF
from ..missao import itens as I
from ..nucleo.eventos import Diario, agora
from . import site_oficial
from .certificacao import Certificacao, Pagina
from .passaporte import Passaporte

ABORDAGENS = {1: "documento na mão", 2: "anexos completos", 3: "página oficial e citados", 4: "biblioteca de sites",
              5: "mídia do WordPress", 6: "mapa do site", 7: "releitura", 8: "ponte do titular", 9: "leitura profunda", 10: "busca no domínio"}
ORDEM = {"sem estrela": [1, 4, 3, 10, 6, 5, 8, 2, 9, 7], "bronze": [1, 2, 3, 9, 7, 4, 10, 6, 5, 8], "prata": [1, 2, 9, 7, 3, 4, 10, 6, 5, 8]}
FOCO = {"sem estrela": I.BRONZE, "bronze": ("Valor", "Requisitos"), "prata": tuple(i for i in I.DOZE if i not in I.PRATA)}
MAXIMO = 10
NUMERO = re.compile(r"n[º°o.]*\s*0*(\d{1,4})\s*[/_-]\s*(20\d\d)", re.I)
PNCP = re.compile(r"pncp\.gov\.br/app/editais/(\d{14})/(\d{4})/(\d+)")
CHAVE = re.compile(r"(?i)edital|chamamento|chamada|sele[çc][ãa]o|regulamento|anexo|credenciamento|pr[êe]mio")
_dz = zstandard.ZstdDecompressor()
SQL_GUARDADOS = ("SELECT p.documento_id, p.numero, p.texto_zstd FROM pagina p JOIN certidao c ON c.documento_id = p.documento_id "
                 "WHERE c.livro_id=? GROUP BY p.documento_id, p.numero")


@dataclass
class Livro:
    id: str
    titulo: str
    orgao: str | None
    link_oficial: str | None
    link_divulgacao: str | None
    estrela: str
    fim: str | None
    certidoes: dict[str, dict]
    tentadas: set[int]

    @property
    def balcao(self) -> str:
        return {"ouro": "prata"}.get(self.estrela, self.estrela if self.estrela in ("bronze", "prata") else "sem estrela")

    @property
    def faltam(self) -> list[str]:
        return I.faltando({k: v for k, v in self.certidoes.items() if I.resolvido(v)})

    @property
    def numero(self) -> str | None:
        m = NUMERO.search(self.titulo or "")
        return f"{int(m.group(1))}/{m.group(2)}" if m else None


def fila(con: sqlite3.Connection, hoje: str) -> list[Livro]:
    """Os livros com itens em falta: as abertas que fecham antes primeiro; depois os que estão mais perto do ouro."""
    con.row_factory = sqlite3.Row
    tentadas: dict[str, set[int]] = {}
    for r in con.execute("SELECT livro_id, ferramenta FROM tentativa WHERE fase='certificacao' AND ferramenta LIKE 'abordagem %'"):
        tentadas.setdefault(r["livro_id"], set()).add(int(r["ferramenta"].split()[1]))
    certs: dict[str, list[dict]] = {}
    for c in con.execute("SELECT * FROM certidao WHERE situacao IN ('comprovado','dispensado')"):
        certs.setdefault(c["livro_id"], []).append(dict(c))
    saida = []
    for r in con.execute("SELECT l.id, l.titulo, l.orgao, l.link_oficial, l.link_divulgacao, l.estrela, d.inscricao_fim FROM livro l "
                         "JOIN livro_dados d ON d.livro_id = l.id WHERE l.situacao <> 'excluido' AND d.validacao <> 'expurgado' "
                         "AND l.id NOT IN (SELECT livro_unido FROM uniao)"):
        lv = Livro(r["id"], r["titulo"] or "", r["orgao"], r["link_oficial"], r["link_divulgacao"], r["estrela"] or "sem", r["inscricao_fim"],
                   I.melhor(certs.get(r["id"], [])), tentadas.get(r["id"], set()))
        if lv.faltam and len(lv.tentadas) < MAXIMO:
            saida.append(lv)
    return sorted(saida, key=lambda x: (0 if (x.fim and x.fim >= hoje) else 1, x.fim or "9999", len(x.faltam)))


class Linha:
    def __init__(self, biblioteca: sqlite3.Connection, diario: Diario, escada: Escada, ponte: Escada | None = None,
                 metabusca: Callable[[str], list[str]] | None = None, ano: int | None = None):
        self.con, self.diario, self.escada, self.ponte, self.metabusca = biblioteca, diario, escada, ponte, metabusca
        self.leitura = leitores.padrao()
        self.profunda = leitores.padrao()
        self.profunda.registrar(LeitorPDF(tabelas="todas"))
        self.certificacao = Certificacao(diario)
        self.passaporte = Passaporte(biblioteca, diario, maximo=MAXIMO)
        self.ano = ano or date.today().year
        self._conhecidos: dict[str, set[str]] | None = None

    # ------------------------------------------------------------------ leitura dos documentos
    def _ler(self, url: str, profunda: bool = False, escada: Escada | None = None) -> tuple[str, leitores.Leitura, bytes] | None:
        try:
            r = (escada or self.escada).buscar(url)
            return url, (self.profunda if profunda else self.leitura).ler(r.conteudo, url), r.conteudo
        except (Bloqueado, Indisponivel, Pendente, leitores.SemLeitor):
            return None

    def _documentos_da_pagina(self, url: str, titulo: str, limite: int) -> Iterator[str]:
        lido = self._ler(url)
        if lido is None or lido[1].tipo != "html":
            return
        for c in fonte_oficial.candidatos(lido[2], url, titulo, limite=limite):
            yield c["url"]

    # ------------------------------------------------------------------ as 10 abordagens (cada uma devolve os endereços a ler)
    def _a1(self, lv: Livro) -> list[str]:
        base = [u for u in (lv.link_oficial,) if u]
        return base + (list(self._documentos_da_pagina(lv.link_oficial, lv.titulo, 2)) if lv.link_oficial else [])

    def _a2(self, lv: Livro) -> list[str]:
        m = PNCP.search(lv.link_oficial or "")
        if m:
            try:
                url = f"https://pncp.gov.br/pncp-api/v1/orgaos/{m.group(1)}/compras/{m.group(2)}/{m.group(3)}/arquivos"
                arquivos = json.loads(self.escada.buscar(url).conteudo)
                return [a.get("url") or a.get("uri") for a in arquivos if isinstance(a, dict) and (a.get("url") or a.get("uri"))][:8]
            except (Bloqueado, Indisponivel, Pendente, ValueError):
                return []
        return list(self._documentos_da_pagina(lv.link_oficial, lv.titulo, 8)) if lv.link_oficial else []

    def _a3(self, lv: Livro) -> list[str]:
        if not lv.link_oficial:
            return []
        lido = self._ler(lv.link_oficial)
        if lido is None or lido[1].tipo != "html":
            return []
        dom = urlsplit(lv.link_oficial).hostname
        paginas = [u for u in lido[1].links if urlsplit(u).hostname == dom and CHAVE.search(u) and u != lv.link_oficial][:4]
        docs: list[str] = []
        for p in paginas:
            docs += list(self._documentos_da_pagina(p, lv.titulo, 2))
        return (paginas + docs)[:8]

    def _a4(self, lv: Livro) -> list[str]:
        if not lv.orgao:
            return []
        if self._conhecidos is None:
            self._conhecidos = {}
            for o, link in self.con.execute("SELECT orgao, link_oficial FROM livro WHERE link_oficial IS NOT NULL AND orgao IS NOT NULL"):
                self._conhecidos.setdefault(o.lower(), set()).add(f"{urlsplit(link).scheme}://{urlsplit(link).netloc}")
        sites = sorted(self._conhecidos.get(lv.orgao.lower(), set()) - {f"{urlsplit(lv.link_oficial or '').scheme}://{urlsplit(lv.link_oficial or '').netloc}"})
        out: list[str] = []
        for s in sites[:3]:
            out += list(self._documentos_da_pagina(s, lv.titulo, 3))
        return out[:6]

    def _a5(self, lv: Livro) -> list[str]:
        if not (lv.link_oficial and lv.numero):
            return []
        u = urlsplit(lv.link_oficial)
        base = f"{u.scheme}://{u.netloc}" + ("/" + u.path.strip("/").split("/")[0] if u.path.strip("/") and "goias.gov.br" in u.netloc else "")
        try:
            itens = json.loads(self.escada.buscar(f"{base}/wp-json/wp/v2/media?search={quote(lv.numero.split('/')[0])}&per_page=10").conteudo)
        except (Bloqueado, Indisponivel, Pendente, ValueError):
            return []
        return [i["source_url"] for i in itens if isinstance(i, dict) and str(i.get("mime_type") or "").endswith("pdf") and i.get("source_url")][:3]

    def _a6(self, lv: Livro) -> list[str]:
        if not lv.link_oficial:
            return []
        from ...motores.descoberta import estrutura_site
        u = urlsplit(lv.link_oficial)
        try:
            pistas = estrutura_site.mapa_do_site(self.escada.buscar, f"{u.scheme}://{u.netloc}/sitemap.xml", limite=3000)
        except Exception:  # noqa: BLE001 — sem mapa do site, a abordagem não tem material (é pulada)
            return []
        num = (lv.numero or "").split("/")[0]
        return [p.link for p in pistas if CHAVE.search(p.link) and (not num or num in p.link)][:4]

    def _a7(self, lv: Livro) -> list[str]:
        return ["__guardados__"] if self.con.execute("SELECT 1 FROM certidao WHERE livro_id=? AND pagina IS NOT NULL LIMIT 1", (lv.id,)).fetchone() else []

    def _a8(self, lv: Livro) -> list[str]:
        return [lv.link_oficial] if (self.ponte and lv.link_oficial) else []

    def _a9(self, lv: Livro) -> list[str]:
        return [u for u in (lv.link_oficial,) if u and re.search(r"(?i)\.(pdf|docx?|xlsx?)($|\?)", u)]

    def _a10(self, lv: Livro) -> list[str]:
        if not (self.metabusca and lv.link_oficial):
            return []
        dom = urlsplit(lv.link_oficial).hostname
        return [u for u in self.metabusca(f"site:{dom} {lv.numero or ''} {lv.titulo[:80]}") if urlsplit(u).hostname == dom][:4]

    # ------------------------------------------------------------------ uma tentativa
    def tentar(self, lv: Livro) -> dict[str, Any]:
        """Uma tentativa: a primeira abordagem da ordem do balcão que ainda não foi tentada e que tem material."""
        for n in ORDEM[lv.balcao]:
            if n in lv.tentadas:
                continue
            urls = getattr(self, f"_a{n}")(lv)
            if not urls:
                continue                                            # sem material: pulada, não gasta tentativa
            novos = self._aplicar(lv, n, urls)
            self.diario.emitir("tentativa.registrada", "cartorio", {
                "livro_id": lv.id, "fase": "certificacao", "ferramenta": f"abordagem {n}", "numero": 1, "em": agora(),
                "resultado": json.dumps({"abordagem": ABORDAGENS[n], "balcao": lv.balcao, "documentos": len(urls), "itens_novos": sorted(novos)},
                                        ensure_ascii=False), "proxima_em": None})
            lv.tentadas.add(n)
            return {"livro": lv.id, "abordagem": n, "itens_novos": sorted(novos)}
        if len(lv.tentadas) < MAXIMO:
            for n in ORDEM[lv.balcao]:                              # o que sobrou sem material conta como tentado
                lv.tentadas.add(n)
        self._encaminhar(lv)
        return {"livro": lv.id, "abordagem": None, "itens_novos": [], "encaminhado": True}

    def _aplicar(self, lv: Livro, n: int, urls: list[str]) -> list[str]:
        resolvidos = {k for k, v in lv.certidoes.items() if I.resolvido(v)}
        paginas: list[Pagina] = []
        oficial = None
        if urls == ["__guardados__"]:                               # releitura: os documentos já guardados
            for did, num, t in self.con.execute(SQL_GUARDADOS, (lv.id,)):

                paginas.append(Pagina(did, num, _dz.decompress(t).decode("utf-8", errors="replace")))
        else:
            for u in urls:
                lido = self._ler(u, profunda=(n == 9), escada=self.ponte if n == 8 else None)
                if lido is None:
                    continue
                url, leitura, _ = lido
                self.diario.emitir("documento.registrado", "cartorio", {"url": url, "sha256": leitura.sha256, "tipo": leitura.tipo,
                                                                        "paginas": len(leitura.paginas), "obtido_em": agora(), "oficial": 1,
                                                                        "leitor": leitura.leitor})
                for p in leitura.paginas:
                    self.diario.emitir("pagina.gravada", "cartorio", {"documento_sha256": leitura.sha256, "numero": p.numero, "texto": p.texto})
                paginas += [Pagina(leitura.sha256, p.numero, p.texto) for p in leitura.paginas]
                oficial = oficial or (url if site_oficial.eh_fonte(url) else None)
        novas = self.certificacao.certificar(lv.id, paginas, resolvidos)
        for item, c in novas.items():
            lv.certidoes[item] = c
        if oficial and not lv.link_oficial:
            self.diario.emitir("livro.links", "cartorio",
                               {"id": lv.id, "link_divulgacao": lv.link_divulgacao, "link_oficial": oficial, "atualizado_em": agora()})
        if novas:                                                   # só a estrela (o selo do livro vem do histórico de edições)
            resolvidas = {k: v for k, v in lv.certidoes.items() if I.resolvido(v)}
            self.diario.emitir("selo.calculado", "cartorio", {"id": lv.id, "estrela": I.nivel(resolvidas), "informacoes_validadas": len(resolvidas),
                                                              "atualizado_em": agora()})
        return list(novas)

    def _encaminhar(self, lv: Livro) -> None:
        """Depois das 10 abordagens: à Investigação (o Interceptador), com a Regência autorizando a passagem."""
        if self.passaporte.fase(lv.id) == "certificacao":
            self.passaporte._tentativas[(lv.id, "certificacao", "linha")] = MAXIMO
            ok, _ = self.passaporte.mover(lv.id, "investigacao", f"10 abordagens do Cartório sem completar: faltam {', '.join(lv.faltam)}")
            if ok:
                self.diario.emitir("relatorio.etapa", "cartorio", {"livro_id": lv.id, "fase": "certificacao", "analise": "interna", "em": agora(),
                                                                   "gerou": "linha de produção esgotada (10 abordagens)", "aprendeu": None,
                                                                   "faltou": ", ".join(lv.faltam)})

    def andar(self, orcamento_s: float, hoje: str | None = None) -> list[dict[str, Any]]:
        """A fila anda até o tempo do batimento acabar: uma tentativa por livro; o resto continua no próximo batimento."""
        inicio, saida = time.monotonic(), []
        for lv in fila(self.con, hoje or date.today().isoformat()):
            if time.monotonic() - inicio > orcamento_s:
                break
            saida.append(self.tentar(lv))
        return saida


def no_linha(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem: a linha de produção anda durante o orçamento de tempo do batimento."""
    from pathlib import Path

    from ...motores.acesso.api import DegrauAPI
    from ...motores.acesso.leve import DegrauLeve
    from ...motores.acesso.local import DegrauLocal
    p = Path(parametros.get("dados", "dados")) / "biblioteca.db"
    if not p.exists():
        return []
    con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    try:
        escada = Escada([DegrauAPI(), DegrauLeve()], intervalo_padrao=float(parametros.get("intervalo_s", 1.0)), tentativas=1, tempo_limite=25)
        ponte = Escada([DegrauLocal(parametros.get("ponte", "dados/ponte"))], intervalo_padrao=0) if parametros.get("ponte") else None
        r = Linha(con, contexto.diario, escada, ponte).andar(float(parametros.get("orcamento_s", 300)))
    finally:
        con.close()
    return [{"tentativas": len(r), "itens_novos": sum(len(x["itens_novos"]) for x in r), "encaminhados": sum(1 for x in r if x.get("encaminhado"))}]
