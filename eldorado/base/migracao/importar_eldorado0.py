"""A migração do Eldorado0 (temporária, 30 dias): livros, certidões, documentos, vereditos, selos, leis, empresas e
o aprendizado dos motores, em eventos aplicados pelo gravador.

- Eventos com identidades deterministas (eldorado0-000001…): rodar de novo não duplica nada.
- CPF removido de todo texto importado, sem máscara e sem menção.
- Nada inventado: o que falta vira lacuna no relatório. Tudo o que é lido é contado na origem, para a conferência.
- Duas identidades com a mesma chave não são fundidas: os dois livros entram e a união é registrada.
- Os pedaços do acervo do Eldorado0 são "achatados": cada um é um mapa caminho → {"dado": valor}.
"""
from __future__ import annotations

import ast
import json
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

from ...motores.leitura.leitores import remover_cpf
from ..missao import itens as I
from ..missao.chave import chave as chave_missao
from ..nucleo.eventos import Evento, Linhagem
from ..nucleo.eventos import agora as _agora

FASE = "eldorado0"


@dataclass
class Relatorio:
    origem: Counter = field(default_factory=Counter)
    lacunas: Counter = field(default_factory=Counter)
    exemplos_lacuna: dict[str, list[str]] = field(default_factory=dict)

    def lacuna(self, tipo: str, ref: str) -> None:
        self.lacunas[tipo] += 1
        self.exemplos_lacuna.setdefault(tipo, [])
        if len(self.exemplos_lacuna[tipo]) < 5:
            self.exemplos_lacuna[tipo].append(ref)


class Importador:
    def __init__(self, raiz: str | Path):
        self.raiz = Path(raiz)
        self.r = Relatorio()
        self._n = 0
        self._chaves: dict[str, str] = {}
        self._docs: dict[str, str] = {}                                # URL → assinatura do documento importado

    # ------------------------------------------------------------------ utilidades
    def _ev(self, tipo: str, dados: dict[str, Any], livro: str | None = None) -> Evento:
        self._n += 1
        return Evento(id=f"eldorado0-{self._n:07d}", tipo=tipo, modulo="migracao", em="2026-10-22T00:00:00+00:00", dados=dados,
                      linhagem=Linhagem(livro=livro))

    def _txt(self, v: Any, limite: int = 2000) -> str | None:
        if v is None:
            return None
        return remover_cpf(str(v))[:limite]

    @staticmethod
    def _dados(peca: dict) -> Iterator[Any]:
        for v in peca.values():
            yield v.get("dado") if isinstance(v, dict) and "dado" in v else v

    def _catalogo(self) -> dict[str, dict]:
        p = self.raiz / "biblioteca_alexandria/fontes/motores.json"
        return {m["id"]: m for m in json.loads(p.read_text(encoding="utf-8"))["motores"]} if p.exists() else {}

    def _selos_antigos(self) -> dict[str, str]:
        p = self.raiz / "docs/dados/selos_livros.json"
        if not p.exists():
            return {}
        lv = json.loads(p.read_text(encoding="utf-8")).get("livros")
        if isinstance(lv, dict):
            return {k: (v.get("selo") if isinstance(v, dict) else v) for k, v in lv.items() if v}
        if isinstance(lv, list):
            return {x["id"]: x.get("selo") for x in lv if isinstance(x, dict) and x.get("id")}
        return {}

    # ------------------------------------------------------------------ livros
    def eventos(self) -> Iterator[Evento]:
        cat = self._catalogo()
        selos = self._selos_antigos()
        pasta = self.raiz / "biblioteca_alexandria/livros"
        vistos: set[str] = set()
        for f in sorted(pasta.glob("*.json")):
            if f.stem in ("_indice", "_origens", "leis"):
                continue
            d = json.loads(f.read_text(encoding="utf-8"))
            lid = d.get("id") or f.stem
            vistos.add(lid)
            self.r.origem["livros (arquivos)"] += 1
            yield from self._livro(lid, d.get("acervo") or {}, cat.get(lid), selos.get(lid), excluido=None)
        for lid, c in cat.items():                                          # catálogo sem arquivo: só a identidade
            if lid not in vistos:
                self.r.origem["livros (só no catálogo)"] += 1
                vistos.add(lid)
                yield from self._livro(lid, {}, c, selos.get(lid), excluido=None)
        for f in sorted((pasta / "_arquivados").glob("*.json")):
            a = json.loads(f.read_text(encoding="utf-8"))
            info = a.get("livro")
            if isinstance(info, str):
                try:
                    info = ast.literal_eval(info)                           # o registro foi gravado como dicionário do Python
                except (ValueError, SyntaxError):
                    info = {}
            lid = (info or {}).get("id") or f.stem
            self.r.origem["livros arquivados"] += 1
            if lid in vistos:
                self.r.lacuna("arquivado que também está ativo (mantido o ativo)", lid)
                continue
            vistos.add(lid)
            yield from self._livro(lid, {}, info or {}, None, excluido=f"arquivado no Eldorado0 em {str(a.get('arquivado_em'))[:10]}: {a.get('motivo')}")
        yield from self._leis()
        yield from self._empresas()

    def _identidade(self, lid: str, acervo: dict, cat: dict | None) -> dict[str, Any]:
        ide = {"titulo": None, "orgao": None, "uf": None, "link_oficial": None, "tema": None}
        if cat:
            ide.update(titulo=cat.get("nome_classificado") or cat.get("programa"), orgao=cat.get("orgao"), uf=cat.get("uf") or cat.get("geo"),
                       link_oficial=cat.get("pagina"), tema=cat.get("area"))
        for k, peca in acervo.items():
            if k.startswith("estado/cartorio/certidoes"):
                for dado in self._dados(peca):
                    if isinstance(dado, dict):
                        for campo in ("titulo", "orgao", "uf", "link_oficial"):
                            ide[campo] = ide[campo] or dado.get(campo)
            elif "pareceres" in k:
                for dado in self._dados(peca):
                    if isinstance(dado, dict) and dado.get("livro") == lid:
                        ide["titulo"] = ide["titulo"] or dado.get("livro_nome") or dado.get("titulo")
                        ide["orgao"] = ide["orgao"] or dado.get("orgao")
                        ide["uf"] = ide["uf"] or dado.get("uf")
                        ide["link_oficial"] = ide["link_oficial"] or dado.get("fonte_oficial")
        if not ide["titulo"] or not ide["orgao"]:                          # qualquer pedaço que se identifique como este livro
            for peca in acervo.values():
                for dado in self._dados(peca):
                    if isinstance(dado, dict) and lid in (dado.get("id"), dado.get("livro")):
                        ide["titulo"] = ide["titulo"] or dado.get("nome_classificado") or dado.get("programa") or dado.get("nome") or dado.get("titulo")
                        ide["orgao"] = ide["orgao"] or dado.get("orgao")
                        ide["uf"] = ide["uf"] or dado.get("uf") or dado.get("geo")
                        ide["link_oficial"] = ide["link_oficial"] or dado.get("pagina") or dado.get("link_oficial")
                if ide["titulo"] and ide["orgao"]:
                    break
        return ide

    def _livro(self, lid: str, acervo: dict, cat: dict | None, selo_antigo: str | None, excluido: str | None) -> Iterator[Evento]:
        ide = self._identidade(lid, acervo, cat)
        if not ide["titulo"]:
            self.r.lacuna("livro sem título em nenhuma fonte (título = identificador)", lid)
        titulo = self._txt(ide["titulo"] or lid, 300)
        uf = str(ide["uf"] or "")[:2].upper() or None
        ch = chave_missao(titulo, ide["orgao"], uf)
        unido_a = None
        if ch in self._chaves:
            unido_a = self._chaves[ch]
            ch = f"{ch}#{lid}"
        else:
            self._chaves[ch] = lid
        link = ide["link_oficial"] if isinstance(ide["link_oficial"], str) and ide["link_oficial"].startswith("http") else None
        situacao = "excluido" if excluido else "em trabalho"
        yield self._ev("livro.criado", {"id": lid, "missao": "oportunidades", "chave": ch, "titulo": titulo, "tema": ide["tema"], "orgao": self._txt(ide["orgao"], 300),
                                        "uf": uf, "link_divulgacao": link, "link_oficial": link, "estrela": "sem", "selo_livro": "sem", "informacoes_validadas": 0,
                                        "situacao": situacao, "justificativa_exclusao": self._txt(excluido, 500), "criado_em": _agora(), "atualizado_em": _agora()}, lid)
        if unido_a:
            self.r.origem["uniões (mesma chave)"] += 1
            yield self._ev("livro.unido", {"livro_que_fica": unido_a, "livro_unido": lid, "em": _agora(), "motivo": "mesma chave na migração do Eldorado0"}, lid)
        if not excluido:
            yield self._ev("livro.passagem", {"livro_id": lid, "de": None, "para": "certificacao", "em": _agora(), "autorizado_por": "regencia",
                                              "motivo": "migração do Eldorado0"}, lid)
        certidoes: dict[str, dict] = {}
        n_cert = n_ver = 0
        for k, peca in acervo.items():
            if k.startswith("estado/cartorio/certidoes"):
                for dado in self._dados(peca):
                    if not isinstance(dado, dict):
                        continue
                    for doc in dado.get("documentos") or []:
                        yield from self._documento(doc)
                    for item, c in (dado.get("itens") or {}).items():
                        if item not in I.DOZE or not isinstance(c, dict):
                            continue
                        ev = self._certidao(lid, item, c)
                        if ev is None:
                            continue
                        chave_c = (item, ev.dados.get("valor"), ev.dados.get("trecho"))
                        if chave_c in {(x["item"], x.get("valor"), x.get("trecho")) for x in certidoes.values() if x["item"] == item}:
                            continue
                        certidoes[f"{item}#{n_cert}"] = ev.dados
                        n_cert += 1
                        yield ev
            elif "pareceres" in k:
                for dado in self._dados(peca):
                    if isinstance(dado, dict) and dado.get("decisao") and dado.get("livro") in (lid, None):
                        n_ver += 1
                        yield self._ev("veredito.gravado", {"livro_id": lid, "origem": "chrome", "decisao": self._txt(dado["decisao"], 100),
                                                            "motivo": self._txt(dado.get("motivo"), 1000), "como_encontrou": self._txt(dado.get("estudo"), 300),
                                                            "em": str(dado.get("data") or _agora())[:25]}, lid)
        self.r.origem["certidões"] += n_cert
        self.r.origem["vereditos"] += n_ver
        resolvidas = {c["item"]: c for c in certidoes.values() if I.resolvido(c)}
        yield self._ev("selo.calculado", {"id": lid, "estrela": I.nivel(resolvidas), "selo_livro": selo_antigo if selo_antigo in ("bronze", "prata", "ouro") else "sem",
                                          "informacoes_validadas": len(resolvidas), "atualizado_em": _agora()}, lid)
        yield self._ev("relatorio.etapa", {"livro_id": lid, "fase": "migracao", "analise": "externa", "em": _agora(),
                                           "gerou": f"importado do Eldorado0: {n_cert} certidão(ões), {n_ver} veredito(s); selo antigo: {selo_antigo or 'nenhum'}",
                                           "aprendeu": None, "faltou": ", ".join(I.faltando(resolvidas)) or None}, lid)

    def _documento(self, doc: dict) -> Iterator[Evento]:
        url = doc.get("url")
        if not url or url in self._docs:
            return
        sha = f"eldorado0:{doc.get('sha1') or re.sub(r'[^0-9a-z]', '', url.lower())[-40:]}"
        if sha in self._docs.values():
            sha = f"{sha}:{len(self._docs)}"                               # assinaturas antigas curtas podem coincidir
        self._docs[url] = sha
        self.r.origem["documentos"] += 1
        yield self._ev("documento.registrado", {"url": url, "sha256": sha, "tipo": doc.get("tipo"), "paginas": doc.get("paginas") if isinstance(doc.get("paginas"), int) else None,
                                                "obtido_em": _agora(), "oficial": int(bool(doc.get("oficial"))), "leitor": "Eldorado0 (sem o texto)", "versao_leitor": None})

    def _certidao(self, lid: str, item: str, c: dict) -> Evento | None:
        valor = self._txt(c.get("valor") or c.get("v"), 1000)
        status = c.get("status") or c.get("s")
        just = self._txt(" ".join(str(c.get(k) or "") for k in ("justificativa", "j", "motivo", "porque", "fundamento")).strip() or None, 1000)
        if status in ("disp", "dispensado") or str(valor or "").lower().startswith("dispensad"):
            situacao = "dispensado" if I.dispensa_valida(item, just or valor) else "pendente"
            just = just or valor
        else:
            situacao = "comprovado" if valor and I.resolvido({"item": item, "situacao": "comprovado", "valor": valor}) else "pendente"
        if situacao == "pendente" and not valor:
            return None
        pagina = c.get("pagina")
        pagina = int(pagina) if str(pagina or "").isdigit() else None
        doc = c.get("documento")
        dados = {"livro_id": lid, "item": item, "valor": valor, "pagina": pagina, "trecho": self._txt(c.get("trecho"), 2000), "fase": FASE,
                 "situacao": situacao, "justificativa": just if situacao == "dispensado" else None, "em": _agora()}
        if isinstance(doc, str) and doc in self._docs:
            dados["documento_sha256"] = self._docs[doc]                      # a certidão aponta para o documento de onde veio
        return self._ev("certidao.gravada", dados, lid)

    # ------------------------------------------------------------------ leis e empresas
    def _leis(self) -> Iterator[Evento]:
        p = self.raiz / "biblioteca_alexandria/livros/leis.json"
        if not p.exists():
            return
        vistas: set[str] = set()
        for lei in json.loads(p.read_text(encoding="utf-8")).get("livros", []):
            self.r.origem["leis (registros)"] += 1
            if lei["id"] in vistas:
                self.r.lacuna("lei repetida no Eldorado0 (mantida uma)", lei["id"])
                continue
            vistas.add(lei["id"])
            self.r.origem["leis"] += 1
            yield self._ev("lei.registrada", {"id": lei["id"], "esfera": lei.get("esfera"), "numero": lei.get("numero"), "ementa": self._txt(lei.get("nome"), 500),
                                              "situacao": lei.get("situacao"), "link_oficial": lei.get("url_oficial"), "atualizada_em": _agora()})

    def _empresas(self) -> Iterator[Evento]:
        vistas: set[str] = set()
        p = self.raiz / "docs/dados/empresas.json"
        if p.exists():
            for uf, bloco in (json.loads(p.read_text(encoding="utf-8")).get("estados") or {}).items():
                lista = bloco.get("empresas") if isinstance(bloco, dict) else bloco
                for e in lista if isinstance(lista, list) else []:
                    cnpj = re.sub(r"\D", "", str(e.get("cnpj") or ""))
                    if len(cnpj) != 14 and re.fullmatch(r"\d{14}", str(e.get("id") or "")):
                        cnpj = str(e["id"])                                   # o CNPJ guardado no identificador
                    self.r.origem["empresas (registros)"] += 1
                    if len(cnpj) != 14:
                        self.r.lacuna("registro sem CNPJ (não é empresa identificada: título, órgão ou associação)", str(e.get("nome")))
                        continue
                    if cnpj in vistas:
                        continue
                    vistas.add(cnpj)
                    yield self._ev("empresa.registrada", {"cnpj": cnpj, "razao_social": self._txt(e.get("nome"), 300), "nome_fantasia": self._txt(e.get("nome_fantasia"), 300),
                                                          "uf": uf, "porte": e.get("porte"), "atividade_principal": self._txt(e.get("cnae"), 300),
                                                          "descoberta_por": "importacao", "descoberta_em": _agora(), "atualizada_em": _agora()})
        p = self.raiz / "docs/dados/incentivos_verificados.json"
        if p.exists():
            for e in json.loads(p.read_text(encoding="utf-8")).get("empresas", []):
                cnpj = re.sub(r"\D", "", str(e.get("cnpj") or ""))
                if len(cnpj) != 14:
                    continue
                if cnpj not in vistas:
                    vistas.add(cnpj)
                    self.r.origem["empresas (registros)"] += 1
                    yield self._ev("empresa.registrada", {"cnpj": cnpj, "razao_social": self._txt(e.get("nome"), 300), "descoberta_por": "importacao",
                                                          "descoberta_em": _agora(), "atualizada_em": _agora()})
                confirmados = set(e.get("confirmados") or [])
                rouanet = e.get("rouanet_5_anos") if isinstance(e.get("rouanet_5_anos"), dict) else {}
                fatos = {"Rouanet": rouanet or None, "Goyazes": e.get("goyazes"), "PAT": e.get("pat")}
                for lei in sorted(confirmados | {k for k, v in fatos.items() if v}):
                    anos = rouanet.get("anos") if lei == "Rouanet" else None
                    self.r.origem["incentivos (registros)"] += 1
                    yield self._ev("incentivo.registrado", {"cnpj": cnpj, "lei": lei if lei in ("FIA", "Idoso", "Esporte", "Rouanet", "Pronas", "Pronon", "Goyazes", "ICMS", "PAT") else "outra",
                                                            "ano": int(max(anos)) if anos else None, "valor": rouanet.get("valor") if lei == "Rouanet" else None,
                                                            "comprovado": int(lei in confirmados),
                                                            "fonte": self._txt(f"Eldorado0 (verificado em {e.get('verificado_em') or 'data não registrada'}): {json.dumps(fatos.get(lei), ensure_ascii=False)}", 500),
                                                            "em": str(e.get("verificado_em") or _agora())})
        self.r.origem["empresas (CNPJ únicos)"] = len(vistas)


def aprendizado(imp: Importador, arquivo: str | Path) -> Iterator[Evento]:
    """O aprendizado dos motores do Eldorado0 (APRENDIZADO-ELDORADO.json): um aprendizado permanente por motor no Cérebro."""
    d = json.loads(Path(arquivo).read_text(encoding="utf-8"))
    for m in d.get("motores", []):
        h = (m.get("historico_de_erros_e_aprendizado") or {})
        licoes = list(h.get("licoes_do_historico") or [])
        rotas = m.get("rotas") or m.get("aprendizado") or {}
        if not licoes and not rotas:
            imp.r.lacuna("motor sem aprendizado registrado", m.get("id", "?"))
            continue
        imp.r.origem["aprendizados de motores"] += 1
        destino = (h.get("destino_no_novo_eldorado") or {}).get("motor_novo")
        o_que = imp._txt(" ".join(licoes) or json.dumps(rotas, ensure_ascii=False), 8000)
        yield imp._ev("aprendizado.promovido", {"modulo": m.get("id"), "o_que": o_que, "promovido_em": _agora(), "origem_temporario": None,
                                                "medicao_que_provou": f"histórico do Eldorado0 (01/10 a 22/10/2026); destino: {destino or 'a definir'}",
                                                "arquivado": 0})


def lotes(eventos: Iterator[Evento], tamanho: int = 500) -> Iterator[list[Evento]]:
    lote: list[Evento] = []
    for e in eventos:
        lote.append(e)
        if len(lote) >= tamanho:
            yield lote
            lote = []
    if lote:
        yield lote


def conferir(imp: Importador, bancos: dict) -> list[tuple[str, int, int, bool]]:
    """As contagens da origem contra as do banco: (o quê, origem, banco, bate?)."""
    o = imp.r.origem
    b, e = bancos["biblioteca"], bancos["especial"]
    n = lambda con, sql: con.execute(sql).fetchone()[0]  # noqa: E731
    arquivados_importados = o["livros arquivados"] - imp.r.lacunas["arquivado que também está ativo (mantido o ativo)"]
    livros = o["livros (arquivos)"] + o["livros (só no catálogo)"] + arquivados_importados
    linhas = [
        ("livros", livros, n(b, "SELECT COUNT(*) FROM livro")),
        ("livros excluídos (arquivados)", arquivados_importados, n(b, "SELECT COUNT(*) FROM livro WHERE situacao='excluido'")),
        ("passagens (livros não excluídos)", livros - arquivados_importados, n(b, "SELECT COUNT(*) FROM passagem")),
        ("livros com a estrela calculada", livros, n(b, "SELECT COUNT(*) FROM livro WHERE estrela IS NOT NULL")),
        ("uniões (mesma chave)", o["uniões (mesma chave)"], n(b, "SELECT COUNT(*) FROM uniao")),
        ("documentos", o["documentos"], n(b, "SELECT COUNT(*) FROM documento")),
        ("certidões", o["certidões"], n(b, "SELECT COUNT(*) FROM certidao")),
        ("vereditos", o["vereditos"], n(b, "SELECT COUNT(*) FROM veredito")),
        ("leis", o["leis"], n(b, "SELECT COUNT(*) FROM lei")),
        ("aprendizados de motores", o["aprendizados de motores"], n(bancos["cerebro"], "SELECT COUNT(*) FROM aprendizado_permanente")),
        ("empresas (CNPJ únicos)", o["empresas (CNPJ únicos)"], n(e, "SELECT COUNT(*) FROM empresa")),
        ("incentivos", o["incentivos (registros)"], n(e, "SELECT COUNT(*) FROM incentivo")),
    ]
    return [(q, a, c, a == c) for q, a, c in linhas]


def amostra(raiz: str | Path, bancos: dict, tamanho: int = 25, semente: int = 7) -> list[tuple[str, str, bool]]:
    """Livros sorteados, relidos direto da origem e comparados campo a campo com o banco."""
    import random
    imp = Importador(raiz)
    pasta = Path(raiz) / "biblioteca_alexandria/livros"
    arqs = sorted(f for f in pasta.glob("*.json") if not f.stem.startswith("_") and f.stem != "leis")
    cat = imp._catalogo()
    saida = []
    for f in random.Random(semente).sample(arqs, min(tamanho, len(arqs))):
        d = json.loads(f.read_text(encoding="utf-8"))
        lid = d.get("id") or f.stem
        evs = list(imp._livro(lid, d.get("acervo") or {}, cat.get(lid), None, None))
        criado = next(x.dados for x in evs if x.tipo == "livro.criado")
        esperado = (criado["titulo"], criado["uf"], sum(x.tipo == "certidao.gravada" for x in evs), sum(x.tipo == "veredito.gravado" for x in evs))
        b = bancos["biblioteca"]
        linha = b.execute("SELECT titulo, uf FROM livro WHERE id=?", (lid,)).fetchone()
        real = (linha[0], linha[1], b.execute("SELECT COUNT(*) FROM certidao WHERE livro_id=?", (lid,)).fetchone()[0],
                b.execute("SELECT COUNT(*) FROM veredito WHERE livro_id=?", (lid,)).fetchone()[0]) if linha else None
        saida.append((lid, f"esperado {esperado[2]} certidões e {esperado[3]} vereditos", real == esperado))
    return saida
