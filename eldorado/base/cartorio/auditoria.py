"""A auditoria de cada livro: a validação individual e a decupagem dos dados em colunas (livro_dados).

Para cada livro: o portão da missão (é oportunidade?); o território (município de Goiás, estadual de Goiás, capital de
outro estado, estadual de outro estado, nacional, internacional; o município de outro estado fora das capitais sai);
a identidade; cada certidão pelo formato do seu item; e a situação do prazo. Expurgo é exclusão lógica (nada se apaga,
regra de 20/10): o livro sai de uso com a justificativa e continua guardado. Certidão inválida é contestada (não se
apaga) e a estrela é recalculada sem ela. Prazo encerrado não é expurgo: o livro é o programa, e o histórico serve à
previsão. Só grava eventos.
"""
from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Iterator

from ...motores.leitura import normalizar as N
from ..missao import itens as I
from ..missao import portao
from ..missao import regras_portao as R
from ..nucleo.eventos import Diario, agora
from . import site_oficial
from .certificacao import esfera_pelo_orgao

MUNICIPAL = re.compile(r"(?i)prefeitura|munic[íi]pio|\bmunicipal\b|c[âa]mara (?:municipal|de vereadores)|secretaria municipal")
NACIONAL = re.compile(r"(?i)\bnacional\b|todo o (?:brasil|pa[íi]s|territ[óo]rio nacional)|minist[ée]rio|governo federal|\bfederal\b")
INTERNACIONAL = re.compile(r"(?i)internacional|international|\bglobal\b|embaixada|\bonu\b|unesco|unicef|\bpnud\b|\bbid\b|banco mundial")
CIDADE = re.compile(r"(?i)(?:prefeitura|munic[íi]pio|c[âa]mara municipal)(?: municipal)? (?:de |do |da )([A-ZÀ-Ú][\wÀ-ú' ]{2,40}?)(?=[\s,.;:/()—–-]|$)")
HISTORICO = re.compile(r"(?i)edital de ano anterior|fase de resultado")   # temporal: num LIVRO (o programa), é histórico, não expurgo
SEM_VALOR = re.compile(r"(?i)n[ãa]o h[áa] valor|sem valor|vari[áa]vel|conforme|a definir|n[ãa]o se aplica|isen|sem repasse|sem contrapartida|"
                       r"n[ãa]o onerosa|US\$|U\$|€|EUR\b|USD\b|libras?|ienes?|euros?|d[óo]lares")
CONTINUO = re.compile(r"(?i)fluxo cont[íi]nuo|perman(?:ente|entemente)|sem prazo de encerramento|em aberto|o ano (?:todo|inteiro)|ao longo de todo")
RELATIVO = re.compile(r"(?i)\d+\s*(?:\([a-zç ]+\))?\s*dias")
ESFERAS = [(re.compile(r"(?i)internac"), "internacional"), (re.compile(r"(?i)feder|uni[ãa]o|nacional"), "federal"),
           (re.compile(r"(?i)estad"), "estadual"), (re.compile(r"(?i)munic"), "municipal"),
           (re.compile(r"(?i)priv|ong|empresa|funda[çc]|institut|associa|terceiro setor|sociedade civil"), "privada")]


@dataclass
class Resultado:
    livro: str
    titulo: str
    validacao: str
    abrangencia: str
    motivos: list[str] = field(default_factory=list)
    contestadas: list[str] = field(default_factory=list)
    estrela_antes: str = ""
    estrela_depois: str = ""
    dados: dict[str, Any] = field(default_factory=dict)


def esfera(texto: str | None) -> str | None:
    for rx, nome in ESFERAS:
        if texto and rx.search(texto):
            return nome
    return None


def territorio(livro: dict[str, Any], certidoes: dict[str, dict]) -> tuple[str, str | None]:
    """(abrangência, município) pelas regras do portão, já validadas pela titular."""
    uf = (livro.get("uf") or "").upper()
    terr = (certidoes.get("Território") or {}).get("valor") or ""
    texto = f"{livro.get('titulo') or ''} {livro.get('orgao') or ''} {terr}"
    item = {"titulo": livro.get("titulo"), "orgao": livro.get("orgao"), "uf": uf if len(uf) == 2 and uf not in ("BR", "IN") else None,
            "url": livro.get("link_oficial"), "link_oficial": livro.get("link_oficial")}
    cidade = CIDADE.search(texto)
    municipio = cidade.group(1).strip() if cidade else None
    if uf == "IN" or (not uf and INTERNACIONAL.search(texto)):
        return "internacional", None
    if R.municipal_fora_de_goias(item):
        return "municipal_fora_go", municipio
    if uf == "GO" or (not uf and R._municipio_goiano(texto)):
        return ("municipal_go" if MUNICIPAL.search(texto) or R._municipio_goiano(texto) else "estadual_go"), municipio
    if uf == "BR":
        return "nacional", None
    if len(uf) == 2:
        if MUNICIPAL.search(texto) and (R.capital_citada(texto) or R.capital_citada(f"{texto} {livro.get('link_oficial') or ''}")):
            return "capital_outro_estado", municipio
        return "estadual_outro_estado", None                      # sem cidade verificada não se elimina: estadual (17/10)
    if NACIONAL.search(texto):
        return "nacional", None
    link = str(livro.get("link_oficial") or "")
    host = (re.match(r"https?://([^/]+)", link) or [None, ""])[1].lower()
    estado = re.search(r"\.([a-z]{2})\.(?:gov|leg|jus|mp|def)\.br$", host)
    if estado:                                                  # a UF pelo endereço do site oficial
        uf_end = estado.group(1).upper()
        if R.municipal_fora_de_goias({**item, "uf": uf_end}):
            return "municipal_fora_go", municipio
        municipal = R.municipio_pelo_endereco(link)
        if uf_end == "GO":
            return ("municipal_go" if municipal else "estadual_go"), municipio
        return ("capital_outro_estado" if municipal else "estadual_outro_estado"), municipio
    if host.endswith(".gov.br") or host == "gov.br":
        return "nacional", None
    return "indeterminado", municipio


def conferir_certidao(item: str, valor: str | None) -> str | None:
    """O motivo de contestar a certidão pelo formato do seu item; None se ela serve."""
    v = (valor or "").strip()
    if len(v) < 3:
        return "valor vazio"
    if item == "Prazo de inscrição" and not N.datas(v, date(2026, 10, 22)) and not CONTINUO.search(v):
        return "não tem data"
    if item == "Resultado" and not N.datas(v, date(2026, 10, 22)) and not RELATIVO.search(v):
        return "não tem data nem prazo"
    if item == "Valor":
        nums = N.valores(v)
        if not nums and not SEM_VALOR.search(v):
            return "não tem valor em reais"
        if nums and max(nums) < 100:
            return f"valor implausível ({max(nums):.0f} reais)"
    if item == "Prazo de recurso" and not re.search(r"\d", v):
        return "não tem prazo"
    if item == "Esfera" and esfera(v) is None:
        return "esfera não reconhecida"
    return None


def _situacao(historico: bool, continuo: bool, fim: date | None, hoje: date) -> str:
    if historico and (not fim or fim < hoje):
        return "encerrada"
    if not fim:
        return "aberta" if continuo else "sem prazo"
    return "aberta" if fim >= hoje else "encerrada"


def _primeiro(certidoes: dict[str, dict], item: str) -> str | None:
    c = certidoes.get(item)
    return c.get("valor") if c else None


def pendentes(con: sqlite3.Connection) -> set[str]:
    """Os livros sem a validação, ou alterados depois dela."""
    return {r[0] for r in con.execute("SELECT l.id FROM livro l LEFT JOIN livro_dados d ON d.livro_id = l.id "
                                      "WHERE d.livro_id IS NULL OR l.atualizado_em > d.validado_em")}


def auditar(con: sqlite3.Connection, hoje: date, somente: set[str] | None = None) -> Iterator[Resultado]:
    con.row_factory = sqlite3.Row
    livros = [dict(r) for r in con.execute("SELECT * FROM livro ORDER BY id") if somente is None or r["id"] in somente]
    todas: dict[str, list[dict]] = {}
    for c in con.execute("SELECT * FROM certidao WHERE situacao IN ('comprovado','dispensado') ORDER BY id"):
        todas.setdefault(c["livro_id"], []).append(dict(c))
    for lv in livros:
        motivos: list[str] = []
        contestadas: list[str] = []
        validas: dict[str, dict] = {}
        for c in todas.get(lv["id"], []):
            if c["situacao"] == "comprovado":
                m = conferir_certidao(c["item"], c["valor"])
                if m:
                    contestadas.append(f"{c['item']}: {m} ({(c['valor'] or '')[:50]})")
                    c["_contestar"] = m
                    continue
            validas[c["item"]] = c                                  # a mais recente válida de cada item
        abr, municipio = territorio(lv, validas)
        motivo_portao = portao.motivo({"titulo": lv["titulo"], "orgao": lv["orgao"], "uf": lv["uf"], "url": lv["link_oficial"]}, hoje.isoformat())
        sem_titulo = not lv["titulo"] or lv["titulo"] == lv["id"]
        if lv["situacao"] == "excluido":
            validacao = "expurgado"
            motivos.append(f"já excluído na migração: {lv['justificativa_exclusao']}")
        elif motivo_portao and motivo_portao != "sem título" and not HISTORICO.search(motivo_portao):
            validacao = "expurgado"
            motivos.append(f"não é oportunidade da missão: {motivo_portao}")
        elif abr == "municipal_fora_go":
            validacao = "expurgado"
            motivos.append("município de outro estado, fora das capitais")
        else:
            validacao = "aprovado"
            if sem_titulo:
                motivos.append("sem título real (o título é o identificador)")
            if abr == "indeterminado":
                motivos.append("território indeterminado (sem cidade verificada não se elimina)")
            if any(not m.startswith("edição anterior") for m in motivos):
                validacao = "revisar"
        historico = bool(motivo_portao and HISTORICO.search(motivo_portao)) and validacao != "expurgado"
        if historico:
            motivos.append(f"edição anterior, mantida como histórico do programa ({motivo_portao})")
        insc = N.datas(_primeiro(validas, "Prazo de inscrição") or "", hoje)
        res = N.datas(_primeiro(validas, "Resultado") or "", hoje)
        vals = N.valores(_primeiro(validas, "Valor") or "")
        rec = re.search(r"(\d+)\s*(?:\([a-zç ]+\))?\s*dias", _primeiro(validas, "Prazo de recurso") or "")
        fim = max(insc) if insc else None
        continuo = bool(CONTINUO.search(_primeiro(validas, "Prazo de inscrição") or ""))
        link = lv["link_oficial"]
        dados = {"livro_id": lv["id"], "abrangencia": abr, "municipio": municipio, "uf": lv["uf"],
                 "esfera": esfera(_primeiro(validas, "Esfera")) or esfera((esfera_pelo_orgao(lv["orgao"] or "") or (None,))[0]),
                 "inscricao_inicio": min(insc).isoformat() if len(insc) > 1 else None, "inscricao_fim": fim.isoformat() if fim else None,
                 "resultado_em": max(res).isoformat() if res else None, "recurso_dias": int(rec.group(1)) if rec else None,
                 "valor_min": min(vals) if vals else None, "valor_max": max(vals) if vals else None,
                 "modalidade": (_primeiro(validas, "Modalidade") or "")[:120] or None,
                 "area": (_primeiro(validas, "Área de atuação") or lv["tema"] or "")[:120] or None,
                 "situacao_prazo": _situacao(historico, continuo, fim, hoje),
                 "link_oficial_tipo": "ausente" if not link else ("republicador" if site_oficial.eh_republicador(link) else "fonte"),
                 "validacao": validacao, "motivos": json.dumps(motivos + [f"certidão contestada — {x}" for x in contestadas], ensure_ascii=False),
                 "validado_em": agora()}
        resolvidas = {k: v for k, v in validas.items() if I.resolvido(v)}
        r = Resultado(lv["id"], lv["titulo"], validacao, abr, motivos, contestadas, lv["estrela"], I.nivel(resolvidas), dados)
        r.dados["_contestar"] = [(c["id"], c["_contestar"]) for c in todas.get(lv["id"], []) if c.get("_contestar")]
        r.dados["_ja_excluido"] = lv["situacao"] == "excluido"
        yield r


def aplicar(resultados: list[Resultado], diario: Diario) -> None:
    for r in resultados:
        contestar = r.dados.pop("_contestar")
        ja_excluido = r.dados.pop("_ja_excluido")
        for cid, _ in contestar:
            diario.emitir("certidao.contestada", "auditoria", {"id": cid, "situacao": "contestado"})
        diario.emitir("livro.decupado", "auditoria", r.dados)
        if r.estrela_depois != r.estrela_antes:
            diario.emitir("selo.calculado", "auditoria", {"id": r.livro, "estrela": r.estrela_depois, "atualizado_em": agora()})
        if r.validacao == "expurgado" and not ja_excluido:
            justificativa = f"validação de 22/10/2026: {'; '.join(r.motivos)}"
            diario.emitir("livro.excluido_logicamente", "auditoria", {"id": r.livro, "justificativa_exclusao": justificativa, "atualizado_em": agora()})
        diario.emitir("relatorio.etapa", "auditoria", {"livro_id": r.livro, "fase": "validacao", "analise": "interna", "em": agora(),
                                                       "gerou": f"{r.validacao}; território {r.abrangencia}; estrela {r.estrela_antes} → {r.estrela_depois}; "
                                                                f"{len(contestar)} certidão(ões) contestada(s)",
                                                       "aprendeu": None, "faltou": "; ".join(r.motivos) or None})


def no_auditar(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem: valida e decupa os livros novos ou alterados (a automação só exclui logicamente)."""
    from pathlib import Path
    p = Path(parametros.get("dados", "dados")) / "biblioteca.db"
    if not p.exists():
        return []
    con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    try:
        alvo = pendentes(con)
        res = list(auditar(con, date.today(), alvo)) if alvo else []
    finally:
        con.close()
    aplicar(res, contexto.diario)
    return [{"auditados": len(res), "expurgados": sum(r.validacao == "expurgado" for r in res), "revisar": sum(r.validacao == "revisar" for r in res)}]
