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
from . import origem
from .certificacao import esfera_pelo_orgao

MUNICIPAL = re.compile(r"(?i)prefeitura|munic[íi]pio|\bmunicipal\b|c[âa]mara (?:municipal|de vereadores)|secretaria municipal")
NACIONAL = re.compile(r"(?i)\bnacional\b|todo o (?:brasil|pa[íi]s|territ[óo]rio nacional)|minist[ée]rio|governo federal|\bfederal\b")
INTERNACIONAL = re.compile(r"(?i)internacional|international|\bglobal\b|embaixada|\bonu\b|unesco|unicef|\bpnud\b|\bbid\b|banco mundial")
CIDADE = re.compile(r"(?i)(?:prefeitura|munic[íi]pio|c[âa]mara municipal)(?: municipal)? (?:de |do |da )([A-ZÀ-Ú][\wÀ-ú' ]{2,40}?)(?=[\s,.;:/()—–-]|$)")
HISTORICO = re.compile(r"(?i)edital de ano anterior|fase de resultado")   # temporal: num LIVRO (o programa), é histórico, não expurgo
SEM_VALOR = re.compile(r"(?i)n[ãa]o h[áa] valor|sem valor|vari[áa]vel|conforme|a definir|n[ãa]o se aplica|isen|sem repasse|sem contrapartida|"
                       r"n[ãa]o onerosa|US\$|U\$|€|EUR\b|USD\b|libras?|ienes?|euros?|d[óo]lares")
CONTINUO = re.compile(r"(?i)fluxo cont[íi]nuo|perman(?:ente|entemente)|sem prazo de encerramento|em aberto|o ano (?:todo|inteiro)|ao longo de todo")
ENCERRADO = re.compile(r"(?i)sem reabertura de prazo|n[ãa]o implica reabertura|inscri[çc][õo]es encerradas|prazo encerrado|recursos? esgotad|limites? esgotad")
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


NOME = r"[A-ZÀ-Ú][\wÀ-ú'’]+(?:\s+(?:d[aeo]s?\s+)?[A-ZÀ-Ú][\wÀ-ú'’]+){0,4}"
CIDADE_UF = re.compile(rf"({NOME})\s*(?:/|\(|[-–]\s)\s*([A-Z]{{2}})\b")
ORGAO_MUNICIPAL = re.compile(r"(?i)(?:funda[çc][ãa]o cultural|secretaria municipal de [\wÀ-ú ]{3,40}?|prefeitura(?: municipal)?|munic[íi]pio|"
                             r"c[âa]mara municipal|fundo municipal de [\wÀ-ú ]{3,40}?)"
                             r" (?:de |do |da )([A-ZÀ-Ú][\wÀ-ú'’]+(?:\s+(?:d[aeo]s?\s+)?[A-ZÀ-Ú][\wÀ-ú'’]+){0,4})")


def _norm(t: str) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFKD", t.lower()) if not unicodedata.combining(c)).strip()


def _municipios() -> dict[str, list[str]]:
    if not hasattr(_municipios, "m"):
        from pathlib import Path
        raiz = Path(__file__).resolve().parents[3] / "config/missao"
        _municipios.m = json.loads((raiz / "municipios_brasil.json").read_text(encoding="utf-8"))["municipios"]
        t = json.loads((raiz / "territorio_goias.json").read_text(encoding="utf-8"))
        _municipios.capitais = {_norm(v["capital"]): uf for uf, v in t["outros_estados"].items() if v.get("capital")} | {"goiania": "GO"}
    return _municipios.m


FEDERAL = re.compile(r"(?i)\bibama\b|icmbio|minist[ée]rio|governo federal|fundo nacional|\bsesai\b|\bdsei\b|funai|universidade federal|"
                     r"instituto federal|\bbndes\b|caixa econ[ôo]mica|banco do brasil|petrobras|\bfiocruz\b|\bembrapa\b|\btrt\s?\d+|\btrf\s?\d|"
                     r"justi[çc]a federal|comando da aeron[áa]utica|\bex[ée]rcito\b|\bmarinha\b|for[çc]a a[ée]rea|\bdcta\b")


ORGAO_MUNICIPAL_FORTE = re.compile(r"(?i)prefeitura|secretaria municipal|c[âa]mara municipal|fundo municipal|funda[çc][ãa]o cultural de")
ESTADUAL = re.compile(r"(?i)secretaria de estado|governo do estado|assembleia legislativa|tribunal de justi[çc]a|\btj[a-z]{2}\b|"
                      r"minist[ée]rio p[úu]blico|\bmp[a-z]{2}\b|defensoria p[úu]blica")
SIGLA_ESTADUAL = re.compile(r"\b[A-Z]{3,7}-(?:AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO)\b")
LOCAL_PUBLICO = re.compile(r"(?i)prefeitura|municipal|c[âa]mara|di[áa]rio|\bpnab\b|aldir blanc|paulo gustavo|chamamento|credenciamento|\bvara\b|comarca|"
                           r"funda[çc][ãa]o cultural")


def cidade_e_uf(texto: str) -> tuple[str, str] | None:
    """O município nomeado no texto e a sua UF, conferidos na lista oficial: "Cidade/UF", "Cidade (UF)", "Cidade – UF", ou um
    órgão municipal nomeado ("Fundação Cultural de X") quando o nome existe numa só UF."""
    m = _municipios()
    texto = texto or ""
    externo = FEDERAL.search(texto) or ESTADUAL.search(texto) or SIGLA_ESTADUAL.search(texto)
    if externo and not ORGAO_MUNICIPAL_FORTE.search(texto):
        return None                                                 # órgão federal ou estadual: a cidade citada é só o local
    for nome, uf in CIDADE_UF.findall(texto) if LOCAL_PUBLICO.search(texto) else []:   # "Cidade/UF" só com sinal de ato público local
        partes = nome.split()
        for i in range(len(partes)):                                # o nome pode vir depois de outras palavras
            cand = _norm(" ".join(partes[i:]))
            if uf in m.get(cand, []):
                return " ".join(partes[i:]), uf
    for nome in ORGAO_MUNICIPAL.findall(texto or ""):
        partes = nome.split()
        for j in range(len(partes), 0, -1):
            ufs = m.get(_norm(" ".join(partes[:j])), [])
            if len(ufs) == 1:
                return " ".join(partes[:j]), ufs[0]
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
    # a evidência do município vence a UF de origem, e vem de QUEM PUBLICA (título e órgão), nunca da descrição do território
    nomeada = cidade_e_uf(f"{livro.get('titulo') or ''} {livro.get('orgao') or ''}")
    if nomeada:
        nome, uf_cidade = nomeada
        _municipios()
        if uf_cidade == "GO":
            return "municipal_go", nome
        if _municipios.capitais.get(_norm(nome)) == uf_cidade:
            return "capital_outro_estado", nome
        return "municipal_fora_go", nome
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
    if item == "Prazo de inscrição" and not N.datas(v, date(2026, 10, 22)) and not CONTINUO.search(v) and not ENCERRADO.search(v):
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


def prazo(certidoes: dict[str, dict], livro: dict[str, Any], hoje: date) -> str:
    """A situação do prazo da oportunidade atual: aberta, encerrada ou sem prazo (a ferramenta de validação)."""
    motivo = portao.motivo({"titulo": livro.get("titulo"), "orgao": livro.get("orgao"), "uf": livro.get("uf"), "url": livro.get("link_oficial")},
                           hoje.isoformat())
    texto = _primeiro(certidoes, "Prazo de inscrição") or ""
    historico = bool(motivo and HISTORICO.search(motivo)) or bool(ENCERRADO.search(texto))
    insc = N.datas(texto, hoje)
    return _situacao(historico, bool(CONTINUO.search(texto)), insc[-1] if insc else None, hoje)


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
        validadas = {c["item"]: c for c in todas.get(lv["id"], []) if c.get("fase") in I.FASES_VALIDADAS}
        boas = []
        for c in todas.get(lv["id"], []):
            if c["situacao"] == "comprovado":
                m = conferir_certidao(c["item"], c["valor"])
                v = validadas.get(c["item"])
                if not m and v is not None and c.get("fase") not in I.FASES_VALIDADAS and _norm(str(v.get("valor"))) != _norm(str(c.get("valor"))):
                    m = "conflita com a certidão validada"                 # a automática nunca supera a validada
                if m:
                    contestadas.append(f"{c['item']}: {m} ({(c['valor'] or '')[:50]})")
                    c["_contestar"] = m
                    continue
            boas.append(c)
        validas = I.melhor(boas)
        conflitos = sorted({c["item"] for c in boas if c["item"] in I.CRITICOS and c.get("fase") in I.FASES_VALIDADAS
                            and _norm(str(c.get("valor"))) != _norm(str((validas.get(c["item"]) or {}).get("valor")))})
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
            if conflitos:
                motivos.append(f"certidões validadas que se contradizem em: {', '.join(conflitos)} (herdadas do Eldorado0)")
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
        historico = historico or bool(ENCERRADO.search(_primeiro(validas, "Prazo de inscrição") or ""))   # a norma diz que não reabre
        link = lv["link_oficial"]
        antes = con.execute("SELECT origem FROM livro_dados WHERE livro_id = ?", (lv["id"],)).fetchone()
        org_cert = _primeiro(validas, "Órgão / financiador") or lv["orgao"]
        cls_origem, motivo_origem = origem.classificar(link, org_cert, municipio, confirmado_antes=bool(antes and antes[0] == origem.CONFIRMADO))
        dados = {"livro_id": lv["id"], "abrangencia": abr, "municipio": municipio, "uf": lv["uf"],
                 "esfera": esfera(_primeiro(validas, "Esfera")) or esfera((esfera_pelo_orgao(lv["orgao"] or "") or (None,))[0]),
                 "inscricao_inicio": min(insc).isoformat() if len(insc) > 1 else None, "inscricao_fim": fim.isoformat() if fim else None,
                 "resultado_em": max(res).isoformat() if res else None, "recurso_dias": int(rec.group(1)) if rec else None,
                 "valor_min": min(vals) if vals else None, "valor_max": max(vals) if vals else None,
                 "modalidade": (_primeiro(validas, "Modalidade") or "")[:120] or None,
                 "area": (_primeiro(validas, "Área de atuação") or lv["tema"] or "")[:120] or None,
                 "situacao_prazo": _situacao(historico, continuo, fim, hoje),
                 "link_oficial_tipo": "ausente" if not link else ("republicador" if origem.eh_republicador(link) else "fonte"),   # indício, não decide
                 "origem": cls_origem, "origem_motivo": motivo_origem[:300], "escada": escada_do_livro(con, lv["id"]),
                 "validacao": validacao, "motivos": json.dumps(motivos + [f"certidão contestada — {x}" for x in contestadas], ensure_ascii=False),
                 "validado_em": agora()}
        resolvidas = {k: v for k, v in validas.items() if I.resolvido(v)}
        estrela_regua = I.nivel(resolvidas, cls_origem == origem.CONFIRMADO) if dados["situacao_prazo"] != "encerrada" else "sem"
        r = Resultado(lv["id"], lv["titulo"], validacao, abr, motivos, contestadas, lv["estrela"], estrela_regua, dados)
        r.dados["_contestar"] = [(c["id"], c["_contestar"]) for c in todas.get(lv["id"], []) if c.get("_contestar")]
        r.dados["_ja_excluido"] = lv["situacao"] == "excluido"
        yield r


def aplicar(resultados: list[Resultado], diario: Diario) -> None:
    for r in resultados:
        contestar = r.dados.pop("_contestar")
        ja_excluido = r.dados.pop("_ja_excluido")
        for cid, _ in contestar:
            diario.emitir("certidao.contestada", "auditoria", {"id": cid, "situacao": "contestado"})
        # a mesma hora na validação e nas mudanças que ela causa: senão o livro parece alterado depois de validado e é
        # auditado de novo a cada ciclo (o defeito intermitente de 23/10/2026)
        t = r.dados.get("validado_em") or agora()
        r.dados["validado_em"] = t
        if r.estrela_depois != r.estrela_antes:
            diario.emitir("selo.calculado", "auditoria", {"id": r.livro, "estrela": r.estrela_depois, "atualizado_em": t})
        if r.validacao == "expurgado" and not ja_excluido:
            justificativa = f"validação de 22/10/2026: {'; '.join(r.motivos)}"
            diario.emitir("livro.excluido_logicamente", "auditoria", {"id": r.livro, "justificativa_exclusao": justificativa, "atualizado_em": t})
        diario.emitir("livro.decupado", "auditoria", r.dados)
        diario.emitir("relatorio.etapa", "auditoria", {"livro_id": r.livro, "fase": "validacao", "analise": "interna", "em": agora(),
                                                       "gerou": f"{r.validacao}; território {r.abrangencia}; estrela {r.estrela_antes} → {r.estrela_depois}; "
                                                                f"{len(contestar)} certidão(ões) contestada(s)",
                                                       "aprendeu": None, "faltou": "; ".join(r.motivos) or None})


LINHA = ("certificacao", "preparacao", "validacao", "analise externa", "farol")


def arquivar_encerrados(con: sqlite3.Connection, diario: Diario, hoje: date) -> int:
    """A validação pelo tempo: o livro na linha cuja oportunidade encerrou vai ao arquivo, com o relatório da etapa; a
    estrela vira o selo do livro (estrela de ouro → livro de ouro) e a estrela volta a "sem", aguardando a próxima."""
    from .passaporte import Passaporte
    from .selos import RANK
    con.row_factory = sqlite3.Row
    certs: dict[str, list[dict]] = {}
    for c in con.execute("SELECT * FROM certidao WHERE situacao IN ('comprovado','dispensado')"):
        certs.setdefault(c["livro_id"], []).append(dict(c))
    passaporte, n = Passaporte(con, diario, maximo=10), 0
    for lv in con.execute(f"SELECT l.*, p.fase FROM livro l JOIN passaporte p ON p.livro_id = l.id WHERE p.fase IN ({','.join('?' * len(LINHA))})", LINHA):
        validas = {k: v for k, v in I.melhor(certs.get(lv["id"], [])).items() if I.resolvido(v)}
        if prazo(validas, dict(lv), hoje) != "encerrada":
            continue
        selo = max((lv["selo_livro"] or "sem", lv["estrela"] or "sem"), key=RANK.get)
        ok, _ = passaporte.mover(lv["id"], "arquivo", "o prazo encerrou: a oportunidade foi arquivada",
                                 {"gerou": f"oportunidade arquivada; a estrela {lv['estrela']} virou o selo do livro ({selo}); aguarda nova oportunidade",
                                  "faltou": ", ".join(I.faltando(validas)) or None})
        if ok:
            diario.emitir("selo.calculado", "auditoria", {"id": lv["id"], "estrela": "sem", "selo_livro": selo, "informacoes_validadas": len(validas),
                                                          "atualizado_em": agora()})
            n += 1
    return n


def escada_do_livro(con: sqlite3.Connection, lid: str) -> str:
    """A escada no livro (titular, 24/10/2026): o motor e o degrau de acesso que obtiveram a oportunidade (o achado mais
    recente que os registra); os livros de antes do registro dizem isso, e os migrados do Eldorado0 também."""
    achados = list(con.execute("SELECT motor, dados FROM achado WHERE livro_id = ? ORDER BY encontrado_em DESC", (lid,)))
    for motor, dados in achados:
        e = (json.loads(dados or "{}") or {}).get("escada")
        if isinstance(e, dict) and e.get("degrau"):
            return f"{e.get('motor') or motor} · degrau {e['degrau']}"
    if achados:
        return f"{achados[0][0]} · degrau não registrado (achado anterior a 24/10/2026)"
    return "livro migrado do Eldorado0 · sem registro da escada"


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
        arquivados = arquivar_encerrados(con, contexto.diario, date.today())
    finally:
        con.close()
    aplicar(res, contexto.diario)
    return [{"auditados": len(res), "expurgados": sum(r.validacao == "expurgado" for r in res), "revisar": sum(r.validacao == "revisar" for r in res),
             "arquivados": arquivados}]
