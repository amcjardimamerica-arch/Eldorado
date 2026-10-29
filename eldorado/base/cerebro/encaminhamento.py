"""A rede neural na fase 3 do Cartório (titular, 22/10/2026): quem age é a rede, não o Cartório.

Para cada livro na preparação (fase 3), na ordem do Cartório (as abertas que fecham antes primeiro), a rede decide:
  1. o MOTOR DA OPORTUNIDADE (o que trouxe o livro), uma pesquisa focada, uma vez por livro;
  2. o INTERCEPTADOR, uma abordagem por batimento (até as 10);
  3. esgotados os dois, a ANÁLISE EXTERNA (fase 5, o Claude no Chrome).
A informação nova volta ao livro como achado e passa pela Pertinência e pelo Cartório (fase 4, validação). O trabalho
anda pelo orçamento de tempo do batimento e continua no seguinte, até esgotar.
"""
from __future__ import annotations

import json
import sqlite3
import time
from datetime import date
from pathlib import Path
from typing import Any

import msgspec

from ..cartorio.passaporte import Passaporte
from ..nucleo.eventos import agora
from ..nucleo.registro import carregar as carregar_registro
from .livros_motores import ja_pesquisado, motores_do_livro  # noqa: E402,F401 — comuns (sem a importação circular)
from .regencia import _sem_paginas, achado_para_evento


def _canivete(a):
    """O canivete de cada achado (o mesmo dos motores: o idioma, a publicação, as datas de prazo com o trecho, os valores
    em reais e os metadados), aplicado aos achados dos pilotos. Nunca impede a entrega."""
    try:
        from ...motores.leitura.enriquecer import enriquecer
        doc = a.documento or {}
        texto = "\n".join(doc.get("paginas") or []) or (a.dados or {}).get("resumo") or ""
        if not texto or (a.dados or {}).get("canivete"):
            return a
        r = enriquecer(texto, None, a.link_oficial or a.link_divulgacao)
        r.pop("texto_principal", None)
        return msgspec.structs.replace(a, dados={**(a.dados or {}), "canivete": r}) if r else a
    except Exception:  # noqa: BLE001
        return a


class Encaminhamento:
    def __init__(self, biblioteca: sqlite3.Connection, diario, registro, interceptador, rede=None):
        self.con, self.diario, self.registro, self.interceptador, self.rede = biblioteca, diario, registro, interceptador, rede
        self.passaporte = Passaporte(biblioteca, diario, maximo=10)

    def _entregar(self, a, quem: str) -> dict[str, Any]:
        a = _canivete(a)                                            # o canivete suíço dos motores, também nos pilotos (25/10/2026)
        doc = a.documento or {}
        self.diario.emitir("documento.registrado", quem, {"url": doc["url"], "sha256": doc["sha256"], "tipo": doc.get("tipo"),
             "paginas": len(doc.get("paginas") or []), "obtido_em": agora(), "oficial": int(bool(doc.get("oficial"))), "leitor": doc.get("leitor")})
        for i, texto in enumerate(doc.get("paginas") or [], 1):
            self.diario.emitir("pagina.gravada", quem, {"documento_sha256": doc["sha256"], "numero": i, "texto": texto})
        self.diario.emitir("achado.entregue", quem, achado_para_evento(a))
        return _sem_paginas(msgspec.to_builtins(a)) | {"documento": _sem_paginas(doc)}

    def encaminhar(self, lv, ate: float | None = None) -> tuple[str, dict[str, Any] | None]:
        """Uma decisão da rede para um livro: quem age agora, e a informação nova (se veio)."""
        from ...motores.pilotos.interceptador import ORDEM
        vivo = {"link_oficial": lv.link_oficial, "estrela": lv.estrela, "faltam": lv.faltam}
        motores = [m for m in motores_do_livro(self.con, lv.id) if m in self.registro.ids() and not ja_pesquisado(self.con, lv.id, m)]
        abordagens = [n for n in ORDEM[lv.balcao] if n not in lv.tentadas]
        if self.rede is not None:                                   # a rede escolhe a ação de maior nota; a ordem do balcão desempata
            pos = {n: i for i, n in enumerate(ORDEM[lv.balcao])}
            abordagens.sort(key=lambda n: (-round(self.rede.nota_acao(f"abordagem {n}", vivo), 2), pos[n]))
            if motores and abordagens and self.rede.nota_acao("motor", vivo) < self.rede.nota_acao(f"abordagem {abordagens[0]}", vivo) - 0.1:
                motores = []                                        # a rede prefere o Interceptador agora (o motor fica para depois)
        for motor in motores:
            if True:
                m = self.registro.obter(motor)
                a = m.pesquisar({"id": lv.id, "titulo": lv.titulo, "link_oficial": lv.link_oficial, "link_divulgacao": lv.link_divulgacao}) \
                    if hasattr(m, "pesquisar") else None
                self.diario.emitir("tentativa.registrada", "rede", {"livro_id": lv.id, "fase": "preparacao", "ferramenta": f"motor {motor}", "numero": 1,
                                                                    "em": agora(), "resultado": json.dumps({"trouxe": bool(a), "faltam": lv.faltam}),
                                                                    "proxima_em": None})
                return f"motor {motor}", (self._entregar(a, motor) if a else None)
        r = self.interceptador.voar(lv, ate, preferencia=abordagens if self.rede is not None else None)   # o plano de voo
        entregues = [self._entregar(a, "interceptador") for a in r["achados"]]
        if r.get("adiado"):
            return "interceptador · adiado (o orçamento da passagem)", entregues or None
        if r["esgotado"]:
            self.passaporte._tentativas[(lv.id, "preparacao", "rede")] = 0
            self.passaporte.mover(lv.id, "analise externa", "fase 5: a rede esgotou o motor da oportunidade e as abordagens do Interceptador")
            return "analise externa", None
        return f"interceptador · plano de voo ({len(r['plano'])} passos, {len(entregues)} achados)", entregues or None

    def andar(self, orcamento_s: float, hoje: str | None = None, livros: list | None = None) -> tuple[list[dict[str, Any]], dict[str, int]]:
        from ...motores.pilotos.interceptador import fila
        inicio, achados, contagem = time.monotonic(), [], {}
        if livros is None:
            livros = self.ordenar(fila(self.con, hoje or date.today().isoformat()), hoje)
        for lv in livros:
            if time.monotonic() - inicio > orcamento_s:
                break
            quem, a = self.encaminhar(lv, inicio + orcamento_s)
            contagem[quem.split(" ·")[0].split(" ")[0]] = contagem.get(quem.split(" ·")[0].split(" ")[0], 0) + 1
            if isinstance(a, list):
                achados += a
            elif a:
                achados.append(a)
        return achados, contagem

    def ordenar(self, livros: list, hoje: str | None = None) -> list:
        if self.rede is not None:                                   # dentro da mesma urgência, os mais promissores primeiro
            hj = hoje or date.today().isoformat()
            livros.sort(key=lambda x: (0 if (x.fim and x.fim >= hj) else 1, x.fim or "9999",
                                       -round(self.rede.nota_oportunidade({"titulo": x.titulo, "orgao": x.orgao, "link_oficial": x.link_oficial}), 2)))
        return livros


def _contexto_pilotos(parametros: dict[str, Any], contexto):
    """O que os três nós dos pilotos usam: a Biblioteca (só leitura), a escada COMPLETA, o registro dos motores e a rede."""
    from ...motores.acesso.completa import escada_completa
    dados = Path(parametros.get("dados", "dados"))
    con = sqlite3.connect(f"file:{dados / 'biblioteca.db'}?mode=ro", uri=True)
    escada = escada_completa(float(parametros.get("intervalo_s", 1.0)), tentativas=1, tempo_limite=25, diario=contexto.diario, dados=dados)
    registro = carregar_registro(parametros.get("modulos", "config/modulos.toml"), contexto.diario)
    return dados, con, escada, registro


def no_encaminhar(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem: o Interceptador — a rede neural encaminha os livros da fase 3 e devolve a informação nova (para a
    Pertinência). O parecer do conselho (24/10/2026): o Espião e os sites originais em nós próprios (no_espiao, no_originais);
    a rede treinada é a mesma do nó da rede (guardada por 15 min), sem treino duplicado."""
    if not (Path(parametros.get("dados", "dados")) / "biblioteca.db").exists():
        return []
    from .pilotos_permanentes import ATIVO, entregas
    if ATIVO.is_set():                                            # os voos permanentes: o nó entrega o que eles trouxeram
        return entregas("interceptador")
    from ...motores.pilotos.interceptador import Interceptador
    from ..nucleo.ia import IA
    from .rede import rede_atual
    dados, con, escada, registro = _contexto_pilotos(parametros, contexto)
    try:
        ia = IA(cargo_nome="interceptador", tempo_limite=150.0)
        rede = rede_atual(dados)
        from ...motores.acesso.completa import escada_completa
        from ...motores.descoberta.metabusca import Metabusca
        from ...motores.pilotos.interceptador import fila
        livros = Encaminhamento(con, contexto.diario, registro, None, rede).ordenar(fila(con, date.today().isoformat()))
        # um livro por vez, com o plano de voo (a titular, 25/10/2026): o Interceptador fica com o livro até achar o que falta
        n = 1                                                     # um livro por vez (a titular, 25/10/2026: a assertividade)
        orcamento = float(parametros.get("orcamento_s", 300))

        def trabalhador(parte: list) -> list:
            c_w = sqlite3.connect(f"file:{dados / 'biblioteca.db'}?mode=ro", uri=True)
            try:
                esc = escada_completa(float(parametros.get("intervalo_s", 1.0)), tentativas=1, tempo_limite=25, diario=contexto.diario, dados=dados)
                mb = Metabusca(buscar=esc.buscar)

                def buscar_links(q: str) -> list[str]:
                    try:
                        return [p.link for p in mb.consultar(q, limite=10)[0]]
                    except Exception:  # noqa: BLE001
                        return []
                enc = Encaminhamento(c_w, contexto.diario, registro, Interceptador(c_w, contexto.diario, esc, metabusca=buscar_links,
                                                                                  ia=ia if ia.disponivel() else None), rede)
                return enc.andar(orcamento, livros=parte)[0]
            finally:
                c_w.close()
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=n) as pool:
            partes = [livros[i::n] for i in range(n)]
            return [a for r in pool.map(trabalhador, partes) for a in r]
    finally:
        con.close()


def no_espiao(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem: o Espião — o Cérebro decide as missões (na ociosidade e o mínimo garantido) e ele age."""
    if not (Path(parametros.get("dados", "dados")) / "biblioteca.db").exists():
        return []
    from .pilotos_permanentes import ATIVO, entregas
    if ATIVO.is_set():                                            # os voos permanentes: o nó entrega o que eles trouxeram
        return entregas("espiao")
    from .fila import fila_do_sistema
    from .pilotos import missoes
    dados, con, escada, registro = _contexto_pilotos(parametros, contexto)
    try:
        ociosidade = not fila_do_sistema(dados, Path(parametros.get("config", "config")))["motores_devidos"]
        do_espiao, _ = missoes(dados, con, escada, ociosidade, float(parametros.get("orcamento_pilotos_s", 180)), diario=contexto.diario)
        enc = Encaminhamento(con, contexto.diario, registro, None)
        return [enc._entregar(a, "espiao") for a in do_espiao]
    finally:
        con.close()


def no_originais(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem: a vigilância dos sites originais dos livros (o mapa do site, pelo motor de cada livro)."""
    if not (Path(parametros.get("dados", "dados")) / "biblioteca.db").exists():
        return []
    from .originais import vigiar
    dados, con, escada, registro = _contexto_pilotos(parametros, contexto)
    try:
        dos_originais, _ = vigiar(con, registro, float(parametros.get("orcamento_originais_s", 120)), contexto.diario)
        enc = Encaminhamento(con, contexto.diario, registro, None)
        return [enc._entregar(a, a.motor) for a in dos_originais]
    finally:
        con.close()
