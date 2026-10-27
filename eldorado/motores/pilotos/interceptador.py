"""O PILOTO INTERCEPTADOR (do Eldorado0, titular, 26/09/2026): "o Espião descobre; o Interceptador comprova".

Acionado pela REDE NEURAL para os livros na fase 3 do Cartório (preparação), quando falta informação. Ele não certifica
nada: busca, na fonte oficial, os documentos que podem trazer o que falta e ENTREGA a informação nova ao livro; o Cartório
a valida na fase 4. A cada acionamento, uma abordagem diferente (da ordem do balcão do livro), no máximo 10 por livro;
abordagem sem material é pulada. Esgotadas as abordagens, a rede passa o livro à análise externa (fase 5).

As 10 abordagens (da linha de produção do Cartório do Eldorado0):
   1 documento na mão          o link oficial e os documentos ligados direto a ele
   2 anexos completos          todos os arquivos do processo (PNCP) e todos os documentos da página oficial
   3 página oficial e citados  o site do órgão mais fundo (até 8 páginas ou documentos a mais)
   4 biblioteca de sites       os sites oficiais já conhecidos do mesmo órgão (de outros livros)
   5 mídia do WordPress        o número do edital na biblioteca de mídia do site oficial
   6 mapa do site              o sitemap do domínio oficial, filtrado por edital e número
   7 cópia arquivada           a última cópia do link oficial na Wayback (o site mudou ou saiu do ar)
   8 ponte do titular          refaz pelo computador da titular o que o site recusou à nuvem
   9 leitura profunda          os documentos inteiros, com as tabelas (cronogramas)
  10 busca no domínio          a metabusca restrita ao domínio oficial, pelo número e pelo título
A IA (a comprovação item a item com o trecho literal) entra sobre estes mesmos documentos.
"""
from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass
from typing import Any, Callable, Iterator
from urllib.parse import quote, urlsplit

import zstandard

from ...base.cartorio import origem
from ...base.missao import itens as I
from ...base.nucleo.contratos import Achado
from ...base.nucleo.eventos import Diario, agora
from ..acesso.escada import Bloqueado, Escada, Indisponivel, Passageiro, Pendente
from ..descoberta import fonte_oficial
from ..leitura import leitores
from ..leitura.pdf import LeitorPDF

ABORDAGENS = {1: "documento na mão", 2: "anexos completos", 3: "página oficial e citados", 4: "biblioteca de sites",
              5: "mídia do WordPress", 6: "mapa do site", 7: "cópia arquivada", 8: "ponte do titular", 9: "leitura profunda", 10: "busca no domínio",
              11: "secretaria do município"}
ORDEM = {"sem estrela": [1, 11, 4, 3, 10, 6, 5, 8, 2, 9, 7], "bronze": [1, 11, 2, 3, 9, 7, 4, 10, 6, 5, 8], "prata": [1, 11, 2, 9, 7, 3, 4, 10, 6, 5, 8]}
FOCO = {"sem estrela": I.BRONZE, "bronze": ("Valor", "Requisitos"), "prata": tuple(i for i in I.DOZE if i not in I.PRATA)}
MAXIMO = 10
# o plano de voo (titular, 25/10/2026): para cada item que falta, as abordagens mais certeiras do canivete, em ordem
PLANO_POR_ITEM = {
    "Prazo de inscrição": (1, 9, 3, 6, 7, 10, 11), "Resultado": (1, 9, 3, 6, 10, 7), "Prazo de recurso": (9, 1, 3, 6, 10),
    "Valor": (9, 1, 2, 5, 3, 10), "Requisitos": (9, 2, 1, 5, 3), "Anexos": (2, 1, 5, 3, 6), "Modalidade": (9, 1, 2, 3),
    "Objeto": (1, 9, 3, 10, 11, 4), "Órgão / financiador": (1, 3, 4, 11, 10), "Território": (1, 11, 3, 10, 4),
    "Esfera": (1, 3, 4, 11), "Área de atuação": (1, 3, 10, 9)}
FERRAMENTAS = {1: "a página oficial e os documentos dela", 2: "os arquivos do edital (PNCP)", 3: "as páginas do mesmo site",
               4: "os sites conhecidos do órgão", 5: "as mídias do WordPress", 6: "o mapa do site", 7: "a cópia arquivada (Wayback)",
               8: "a ponte do titular", 9: "a leitura completa dos documentos (PDF, tabelas e OCR das imagens)", 10: "a busca no domínio",
               11: "a secretaria do município"}
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
    municipio: str | None = None          # o município do livro (a secretaria do município é onde o diário costuma apontar)
    uf: str | None = None

    @property
    def balcao(self) -> str:
        return {"ouro": "prata"}.get(self.estrela, self.estrela if self.estrela in ("bronze", "prata") else "sem estrela")

    @property
    def faltam(self) -> list[str]:
        return I.faltando({k: v for k, v in self.certidoes.items() if I.resolvido(v)})

    @property
    def base(self) -> str | None:
        """A página de partida das abordagens: o link oficial ou, na falta dele, o de divulgação (24/10/2026: 1.975 livros
        da fila sem link oficial ficavam fora do Interceptador)."""
        return self.link_oficial or self.link_divulgacao

    @property
    def numero(self) -> str | None:
        m = NUMERO.search(self.titulo or "")
        return f"{int(m.group(1))}/{m.group(2)}" if m else None


def fila(con: sqlite3.Connection, hoje: str) -> list[Livro]:
    """Os livros na fase 3 (preparação), na ordem do Cartório: as abertas que fecham antes; depois os mais perto do ouro."""
    con.row_factory = sqlite3.Row
    tentadas: dict[str, set[int]] = {}
    for r in con.execute("SELECT livro_id, ferramenta FROM tentativa WHERE fase='preparacao' AND ferramenta LIKE 'abordagem %'"):
        tentadas.setdefault(r["livro_id"], set()).add(int(r["ferramenta"].split()[1]))
    certs: dict[str, list[dict]] = {}
    for c in con.execute("SELECT * FROM certidao WHERE situacao IN ('comprovado','dispensado')"):
        certs.setdefault(c["livro_id"], []).append(dict(c))
    saida = []
    for r in con.execute("SELECT l.id, l.titulo, l.orgao, l.link_oficial, l.link_divulgacao, l.estrela, d.inscricao_fim, d.municipio, l.uf FROM livro l "
                         "JOIN livro_dados d ON d.livro_id = l.id JOIN passaporte p ON p.livro_id = l.id WHERE p.fase = 'preparacao' "
                         "AND l.situacao NOT IN ('excluido', 'unido') AND d.validacao <> 'expurgado' AND l.id NOT IN (SELECT livro_unido FROM uniao)"):
        lv = Livro(r["id"], r["titulo"] or "", r["orgao"], r["link_oficial"], r["link_divulgacao"], r["estrela"] or "sem", r["inscricao_fim"],
                   I.melhor(certs.get(r["id"], [])), tentadas.get(r["id"], set()), r["municipio"], r["uf"])
        if lv.faltam:
            saida.append(lv)
    return sorted(saida, key=lambda x: (0 if (x.fim and x.fim >= hoje) else 1, x.fim or "9999", len(x.faltam)))


def carregar(con: sqlite3.Connection, ids: list[str]) -> list[Livro]:
    """Os livros pelo identificador, em qualquer fase (a validação das oportunidades antigas, 25/10/2026)."""
    if not ids:
        return []
    con.row_factory = sqlite3.Row
    marc = ",".join("?" * len(ids))
    tentadas: dict[str, set[int]] = {}
    for r in con.execute(f"SELECT livro_id, ferramenta FROM tentativa WHERE ferramenta LIKE 'abordagem %' AND livro_id IN ({marc})", ids):
        tentadas.setdefault(r["livro_id"], set()).add(int(r["ferramenta"].split()[1]))
    certs: dict[str, list[dict]] = {}
    for c in con.execute(f"SELECT * FROM certidao WHERE situacao IN ('comprovado','dispensado') AND livro_id IN ({marc})", ids):
        certs.setdefault(c["livro_id"], []).append(dict(c))
    por_id = {}
    for r in con.execute(f"SELECT l.id, l.titulo, l.orgao, l.link_oficial, l.link_divulgacao, l.estrela, d.inscricao_fim, d.municipio, l.uf FROM livro l "
                         f"JOIN livro_dados d ON d.livro_id = l.id WHERE l.id IN ({marc})", ids):
        por_id[r["id"]] = Livro(r["id"], r["titulo"] or "", r["orgao"], r["link_oficial"], r["link_divulgacao"], r["estrela"] or "sem", r["inscricao_fim"],
                                I.melhor(certs.get(r["id"], [])), tentadas.get(r["id"], set()), r["municipio"], r["uf"])
    return [por_id[i] for i in ids if i in por_id]


VEZ_DA_IA = __import__("threading").BoundedSemaphore(1)   # quantos voos usam a IA ao mesmo tempo (27/10/2026: 1; a passagem também precisa dela)


class Interceptador:
    def __init__(self, biblioteca: sqlite3.Connection, diario: Diario, escada: Escada, ponte: Escada | None = None,
                 metabusca: Callable[[str], list[str]] | None = None, arquivo: str = "https://web.archive.org", ia=None):
        self.con, self.diario, self.escada, self.ponte, self.metabusca, self.arquivo = biblioteca, diario, escada, ponte, metabusca, arquivo
        self.ia = ia                                                # o modelo local (nucleo/ia.py); sem ele, as abordagens seguem sem IA
        self.leitura = leitores.padrao()
        self.profunda = leitores.padrao()
        self.profunda.registrar(LeitorPDF(tabelas="todas"))
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
        base = [u for u in (lv.base,) if u]
        return base + (list(self._documentos_da_pagina(lv.base, lv.titulo, 2)) if lv.base else [])

    def _a2(self, lv: Livro) -> list[str]:
        m = PNCP.search(lv.base or "")
        if m:
            try:
                url = f"https://pncp.gov.br/pncp-api/v1/orgaos/{m.group(1)}/compras/{m.group(2)}/{m.group(3)}/arquivos"
                arquivos = json.loads(self.escada.buscar(url).conteudo)
                return [a.get("url") or a.get("uri") for a in arquivos if isinstance(a, dict) and (a.get("url") or a.get("uri"))][:8]
            except (Bloqueado, Indisponivel, Pendente, ValueError):
                return []
        return list(self._documentos_da_pagina(lv.base, lv.titulo, 8)) if lv.base else []

    def _a3(self, lv: Livro) -> list[str]:
        if not lv.base:
            return []
        lido = self._ler(lv.base)
        if lido is None or lido[1].tipo != "html":
            return []
        dom = urlsplit(lv.base).hostname
        paginas = [u for u in lido[1].links if urlsplit(u).hostname == dom and CHAVE.search(u) and u != lv.base][:4]
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
        sites = sorted(self._conhecidos.get(lv.orgao.lower(), set()) - {f"{urlsplit(lv.base or '').scheme}://{urlsplit(lv.base or '').netloc}"})
        out: list[str] = []
        for s in sites[:3]:
            out += list(self._documentos_da_pagina(s, lv.titulo, 3))
        return out[:6]

    def _a5(self, lv: Livro) -> list[str]:
        if not (lv.base and lv.numero):
            return []
        u = urlsplit(lv.base)
        base = f"{u.scheme}://{u.netloc}" + ("/" + u.path.strip("/").split("/")[0] if u.path.strip("/") and "goias.gov.br" in u.netloc else "")
        try:
            itens = json.loads(self.escada.buscar(f"{base}/wp-json/wp/v2/media?search={quote(lv.numero.split('/')[0])}&per_page=10").conteudo)
        except (Bloqueado, Indisponivel, Pendente, ValueError):
            return []
        return [i["source_url"] for i in itens if isinstance(i, dict) and str(i.get("mime_type") or "").endswith("pdf") and i.get("source_url")][:3]

    def _a6(self, lv: Livro) -> list[str]:
        if not lv.base:
            return []
        from ...motores.descoberta import estrutura_site
        u = urlsplit(lv.base)
        try:
            pistas = estrutura_site.mapa_do_site(self.escada.buscar, f"{u.scheme}://{u.netloc}/sitemap.xml", limite=3000)
        except Exception:  # noqa: BLE001 — sem mapa do site, a abordagem não tem material (é pulada)
            return []
        num = (lv.numero or "").split("/")[0]
        return [p.link for p in pistas if CHAVE.search(p.link) and (not num or num in p.link)][:4]

    def _a7(self, lv: Livro) -> list[str]:
        if not lv.base:
            return []
        from ..acesso.arquivo_web import DegrauArquivo
        try:
            r = DegrauArquivo(self.arquivo).buscar(lv.base, 25)
        except (Bloqueado, Indisponivel, Pendente, Passageiro):           # a falha de rede no Wayback (24/10/2026: derrubava o nó)
            try:                                            # a segunda cópia arquivada: o Common Crawl (cdx_toolkit)
                import cdx_toolkit
                obj = next(iter(cdx_toolkit.CDXFetcher(source="cc").iter(lv.base, limit=1, filter=["status:200"])), None)
                if obj is None:
                    return []
                r = type("Copia", (), {"conteudo": obj.content, "status": 200, "tipo": obj.data.get("mime") or "text/html"})()
            except Exception:  # noqa: BLE001 — sem a biblioteca ou sem cópia
                return []
        self._copias = {**getattr(self, "_copias", {}), lv.base: r}
        return [lv.base] if r.status == 200 else []

    def _a11(self, lv: Livro) -> list[str]:
        """A secretaria do município (titular, 23/10/2026): o diário divulga; a oportunidade original costuma estar no site
        da prefeitura. Do município do livro (ou do órgão do ato) ao site <município>.<uf>.gov.br, e a busca da oportunidade
        lá, pelo número do edital ou pelas palavras do título, na API do WordPress."""
        import unicodedata
        nome = lv.municipio
        if not nome:
            m = re.search(r"(?:munic[ií]pio|municipal|prefeitura)(?: municipal)? (?:de |do |da )([A-ZÀ-Úa-zà-ú' ]{3,40})", f"{lv.orgao or ''} {lv.titulo}")
            nome = m.group(1).strip() if m else None
        if not nome:
            return []
        slug = re.sub(r"[^a-z]", "", "".join(c for c in unicodedata.normalize("NFKD", nome.lower()) if not unicodedata.combining(c)))
        uf = (lv.uf or "go").lower() if (lv.uf or "GO").upper() != "BR" else "go"
        termo = lv.numero.split("/")[0] if lv.numero else " ".join(w for w in re.findall(r"[A-Za-zÀ-ú]{5,}", lv.titulo)[:3])
        for base in (f"https://www.{slug}.{uf}.gov.br", f"https://{slug}.{uf}.gov.br"):
            try:
                itens = json.loads(self.escada.buscar(f"{base}/wp-json/wp/v2/posts?search={quote(termo)}&per_page=5&_fields=link,title").conteudo)
            except (Bloqueado, Indisponivel, Pendente, ValueError):
                continue
            links = [i["link"] for i in itens if isinstance(i, dict) and i.get("link")]
            if links:
                return links[:3]
        return []

    def _a8(self, lv: Livro) -> list[str]:
        return [lv.base] if (self.ponte and lv.base) else []

    def _a9(self, lv: Livro) -> list[str]:
        return [u for u in (lv.base,) if u and re.search(r"(?i)\.(pdf|docx?|xlsx?)($|\?)", u)]

    def _a10(self, lv: Livro) -> list[str]:
        if not (self.metabusca and lv.base):
            return []
        dom = urlsplit(lv.base).hostname
        return [u for u in self.metabusca(f"site:{dom} {lv.numero or ''} {lv.titulo[:80]}") if urlsplit(u).hostname == dom][:4]

    # ------------------------------------------------------------------ uma investigação
    def plano_de_voo(self, lv: Livro, preferencia: list[int] | None = None) -> list[tuple[int, list[str]]]:
        """O plano de voo do livro: as abordagens pelos itens que faltam (cada uma com os itens que ela busca), as mais
        certeiras primeiro; as já tentadas ficam de fora."""
        pontos: dict[int, float] = {}
        para: dict[int, list[str]] = {}
        for item in lv.faltam:
            for pos, n in enumerate(PLANO_POR_ITEM.get(item, ORDEM[lv.balcao])):
                if n in lv.tentadas or (n == 8 and not self.ponte):
                    continue
                pontos[n] = pontos.get(n, 0) + 1 / (1 + pos)
                para.setdefault(n, []).append(item)
        for pos, n in enumerate(preferencia or []):                  # a preferência aprendida pela rede (o Cérebro orienta)
            if n in pontos:
                pontos[n] += 0.3 / (1 + pos)
        return [(n, para[n]) for n in sorted(pontos, key=lambda k: -pontos[k])]

    def voar(self, lv: Livro, ate: float | None = None, tempo_livro_s: float = 180, maximo_achados: int = 4,
             preferencia: list[int] | None = None) -> dict[str, Any]:
        """Um livro por vez, pelo plano de voo, até achar o que falta ou esgotar o plano (com tempo máximo por livro):
        cada passo registrado com os itens que buscou; o material de cada passo vira um achado para o livro."""
        import time as _t
        limite = _t.monotonic() + tempo_livro_s if ate is None else min(ate, _t.monotonic() + tempo_livro_s)
        plano, achados = self.plano_de_voo(lv, preferencia), []
        for n, itens in plano:
            if _t.monotonic() > limite:
                return {"livro": lv.id, "achados": achados, "esgotado": False, "adiado": True, "plano": plano}
            r = self.investigar(lv, [n], limite, para=itens)
            if r.get("achado") is not None:
                achados.append(r["achado"])
                if len(achados) >= maximo_achados:
                    break
        restante = [n for n, _ in self.plano_de_voo(lv)]
        return {"livro": lv.id, "achados": achados, "esgotado": not restante and not achados, "adiado": False, "plano": plano}

    def investigar(self, lv: Livro, ordem: list[int] | None = None, ate: float | None = None, para: list[str] | None = None) -> dict[str, Any]:
        """Uma investigação: a primeira abordagem da ordem do balcão ainda não tentada e com material. Entrega um achado
        para o livro (o Cartório valida na fase 4); sem nenhuma abordagem restante, avisa que esgotou. Toda abordagem
        tentada fica registrada, inclusive a sem material (24/10/2026: invisível, o mesmo livro recomeçava a cada passagem);
        'ate' é o prazo (o orçamento da passagem), conferido entre uma abordagem e outra: o livro interrompido continua
        na passagem seguinte."""
        import time as _t
        for n in ordem or ORDEM[lv.balcao]:
            if n in lv.tentadas:
                continue
            if ate is not None and _t.monotonic() > ate:
                return {"livro": lv.id, "abordagem": None, "achado": None, "esgotado": False, "adiado": True}
            erro = None
            try:
                urls = getattr(self, f"_a{n}")(lv)
            except Exception as e:  # noqa: BLE001 — uma abordagem que falha é pulada: nunca derruba a investigação nem o nó (R18)
                urls, erro = [], f"{type(e).__name__}: {str(e)[:120]}"
            if not urls:
                self.diario.emitir("tentativa.registrada", "interceptador", {
                    "livro_id": lv.id, "fase": "preparacao", "ferramenta": f"abordagem {n}", "numero": 1, "em": agora(),
                    "resultado": json.dumps({"abordagem": ABORDAGENS[n], "ferramenta": FERRAMENTAS.get(n), "para": para, "balcao": lv.balcao,
                                             "sem material": True, "erro": erro, "faltam": lv.faltam}, ensure_ascii=False), "proxima_em": None})
                lv.tentadas.add(n)
                continue
            achado = self._achado(lv, n, urls)
            self.diario.emitir("tentativa.registrada", "interceptador", {
                "livro_id": lv.id, "fase": "preparacao", "ferramenta": f"abordagem {n}", "numero": 1, "em": agora(),
                "resultado": json.dumps({"abordagem": ABORDAGENS[n], "ferramenta": FERRAMENTAS.get(n), "para": para, "balcao": lv.balcao,
                                         "enderecos": len(urls), "faltam": lv.faltam,
                                         "documentos": len((achado.documento or {}).get("paginas") or []) if achado else 0,
                                         "ia": (achado.dados or {}).get("ia") if achado else None}, ensure_ascii=False),
                "proxima_em": None})
            lv.tentadas.add(n)
            return {"livro": lv.id, "abordagem": n, "achado": achado, "esgotado": False}
        return {"livro": lv.id, "abordagem": None, "achado": None, "esgotado": True}

    def _achado(self, lv: Livro, n: int, urls: list[str]) -> Achado | None:
        paginas, oficial, alertas, injecao = [], None, [], None
        for u in urls:
            if n == 7 and u in getattr(self, "_copias", {}):
                r = self._copias[u]
                try:
                    leitura = self.leitura.ler(r.conteudo, u)
                except leitores.SemLeitor:
                    continue
            else:
                lido = self._ler(u, profunda=(n == 9), escada=self.ponte if n == 8 else None)
                if lido is None:
                    continue
                u, leitura, _ = lido
            paginas += [p.texto for p in leitura.paginas]
            alertas += leitura.alertas
            injecao = injecao or leitura.dados.get("injecao")
            oficial = oficial or (u if origem.evidencia(u, lv.orgao) else None)      # a origem pela evidência do livro, não pelo domínio
        if not paginas:
            return None
        itens_ia, ia_rel = {}, None
        if self.ia is not None and not injecao and lv.faltam:       # a IA propõe; o sistema valida (o trecho tem de existir no texto)
            from ...base.nucleo.ia import SemIA, comprovar
            # 26/10/2026: no máximo 2 voos usam a IA ao mesmo tempo (com as 5 vagas pedindo juntas, cada pedido levava os 4
            # minutos inteiros e os voos ficavam presos); sem a vez em 90 s, a abordagem segue sem a IA (o Cartório certifica
            # pelo próprio documento) e o livro volta à fila
            if VEZ_DA_IA.acquire(timeout=90):
                try:
                    itens_ia, uso = comprovar(self.ia, lv.faltam, paginas, lv.titulo, I.DOZE)
                    ia_rel = {"segundos": uso.segundos, "propostas": uso.propostas, "aceitas": uso.aceitas, "recusas": uso.recusas[:6]}
                except SemIA as e:
                    ia_rel = {"indisponivel": str(e)[:200]}
                finally:
                    VEZ_DA_IA.release()
            else:
                ia_rel = {"adiada": "a IA ocupada por outros voos; a abordagem seguiu sem a IA"}
        sha = __import__("hashlib").sha256("\n".join(paginas).encode()).hexdigest()
        return Achado(id=f"interceptador-{lv.id}-{n}", motor="interceptador", encontrado_em=agora()[:10],
                      link_divulgacao=lv.link_divulgacao or lv.link_oficial or urls[0], link_oficial=oficial or lv.link_oficial, titulo=lv.titulo,
                      dados={"livro_id": lv.id, "orgao": lv.orgao, "abordagem": ABORDAGENS[n], **({"itens": itens_ia} if itens_ia else {}),
                             **({"ia": ia_rel} if ia_rel else {})},
                      documento={"url": oficial or urls[0], "sha256": sha, "tipo": "investigacao", "leitor": f"interceptador · {ABORDAGENS[n]}",
                                 "oficial": bool(oficial), "paginas": paginas, "alertas": alertas[:10], "injecao": injecao})
