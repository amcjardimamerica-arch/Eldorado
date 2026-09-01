"""Catalogação histórica — 5 anos, mês a mês, para a Biblioteca de Alexandria.

Determinação do titular: a Biblioteca deve nascer com histórico vasto. Esta
rotina percorre a base coletada **mês a mês, separadamente**, aplicando apenas
as FASES 1 e 2 (descobrir e confirmar) — editais antigos não precisam de
análise de aderência. Cada mês é processado de forma isolada, com relatório
próprio de erros, para testar todo o processo de checagem.

O que cada registro recebe:
  · classificação (tipo real, área, nível, UF, programa, financiador)
  · extração do que o texto realmente traz: datas, valores, exigências
  · detecção de resultado/homologação e de VENCEDORES quando publicados
  · estado do prazo (encerrado / aberto / indeterminado)

Regra dura: nada é inventado. Quando o texto não traz vencedor ou critério de
escolha, isso fica registrado como lacuna — e entra na fila de busca, nunca
como suposição.

Saída por edital: `biblioteca_alexandria/oportunidades/<chave>/<ANO>/ficha.json`
e o índice consolidado. Registros que são notícia ou página de navegação não
viram edital: ficam no índice de descartados, com o motivo.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from .biblioteca import OPORTUNIDADES
from .nucleo import ROOT, carregar_oportunidades, load_json, now_iso, slug, write_json

RELATORIOS = ROOT / "estado/catalogacao"

# ------------------------------------------------------------------ padrões
_EH_EDITAL = re.compile(
    r"edital|chamada\s+p[úu]blica|chamamento|sele[çc][ãa]o\s+p[úu]blica|"
    r"credenciamento|concurso\s+de\s+projetos|pr[êe]mio|fomento|"
    r"chamada\s+de\s+propostas|termo\s+de\s+fomento|termo\s+de\s+colabora[çc][ãa]o", re.I)
_EH_RUIDO = re.compile(
    r"^(p[áa]gina|in[íi]cio|home|not[íi]cias?|sistemas?|agência\s+de\s+not|"
    r"acesso\s+[àa]\s+informa|fale\s+conosco|mapa\s+do\s+site)\b", re.I)

_DATA_ISO = re.compile(r"\b(20\d{2})-(\d{2})-(\d{2})\b")
_DATA_BR = re.compile(r"\b(\d{1,2})/(\d{1,2})/(20\d{2})\b")
_VALOR = re.compile(r"R\$\s?([\d.]{1,15},\d{2}|\d[\d.]{2,12})", re.I)
_FIM = re.compile(r"(?:at[ée]|prazo\s+final|encerra\w*|inscri[çc][õo]es[^.]{0,40}?at[ée])"
                  r"\D{0,30}(\d{1,2}/\d{1,2}/20\d{2})", re.I)
_INICIO = re.compile(r"(?:a\s+partir\s+de|abertura|in[íi]cio\s+d?as?\s+inscri[çc][õo]es)"
                     r"\D{0,30}(\d{1,2}/\d{1,2}/20\d{2})", re.I)
_RESULTADO = re.compile(r"homologa\w*|resultado\s+(?:final|preliminar)|"
                        r"classifica\w*\s+final|adjudica\w*", re.I)
# Vencedor: o verbo de homologação abre o trecho; a VALIDAÇÃO do nome é feita
# em `_nome_de_entidade`, porque frase genérica ("sociedade civil para a
# execução de...") não identifica ninguém e não pode virar vencedor.
_VENCEDOR = re.compile(
    r"(?:homologa\w*|adjudica\w*|vencedor\w*|declara\w*\s+habilitad\w*|"
    r"classificad\w*\s+em\s+1[\u00bao\u00b0]?)([^.;\n]{5,150})", re.I)
_TIPO_ENTIDADE = re.compile(
    r"\b(associa[\u00e7c][\u00e3a]o|instituto|funda[\u00e7c][\u00e3a]o|centro|sociedade|"
    r"cooperativa|organiza[\u00e7c][\u00e3a]o|casa|lar|obra|grupo|apae|ong)\b", re.I)
_GENERICO = re.compile(
    r"\b(para|que|cuja|conforme|referente|visando|considerando|execu[\u00e7c][\u00e3a]o|"
    r"composi[\u00e7c][\u00e3a]o|presta\w*\s+servi|interessad|civil\s*$|"
    r"civil\s+organizada|osc[\u2019\']?s?\b)", re.I)


def _nome_de_entidade(trecho: str) -> str | None:
    """Extrai o nome próprio da entidade vencedora, ou None se for frase vaga."""
    m = _TIPO_ENTIDADE.search(trecho)
    if not m:
        return None
    cauda = trecho[m.start():].strip(" .,:;-\u2014")
    # corta na primeira conjunção/preposição que denuncia frase genérica
    # "Organização da Sociedade Civil" é categoria jurídica, não nome de entidade
    cauda = re.sub(r"^(organiza[çc][ãa]o|entidade)\s+d[ae]\s+sociedade\s+civil\b",
                   "", cauda, flags=re.I).strip(" .,:;-—")
    if not _TIPO_ENTIDADE.search(cauda):
        return None
    corte = _GENERICO.search(cauda)
    nome = (cauda[:corte.start()] if corte else cauda).strip(" .,:;-\u2014")
    nome = re.sub(r"\s+", " ", nome)
    palavras = nome.split()
    if len(palavras) < 3:                       # "Associação" sozinha não serve
        return None
    proprio = sum(1 for w in palavras[1:] if w[:1].isupper() or w.isupper())
    if proprio < 2:                             # precisa de nome próprio de fato
        return None
    return nome[:80]


_CRITERIO = re.compile(
    r"(?:crit[\u00e9e]rios?\s+de\s+(?:julgamento|sele[\u00e7c][\u00e3a]o|avalia[\u00e7c][\u00e3a]o|desempate)|"
    r"maior\s+(?:pontua[\u00e7c][\u00e3a]o|nota)|melhor\s+(?:t[\u00e9e]cnica|proposta)|"
    r"menor\s+pre[\u00e7c]o|t[\u00e9e]cnica\s+e\s+pre[\u00e7c]o)[^.\n]{5,140}", re.I)

_EXIGENCIA = re.compile(
    r"(cnpj|estatuto|ata\s+de\s+posse|certid[ãa]o[^.\n]{0,45}|balan[çc]o|cebas|cneas|"
    r"inscri[çc][ãa]o\s+no\s+conselho|regularidade\s+fiscal|fgts|cndt|"
    r"plano\s+de\s+trabalho|contrapartida|dois\s+anos|tr[êe]s\s+anos)", re.I)

AREAS = (
    ("saude", r"sa[úu]de|hospital|ubs|aten[çc][ãa]o\s+b[áa]sica|m[ée]dic"),
    ("educacao", r"educa[çc]|escola|ensino|creche|alfabetiza"),
    ("cultura", r"cultur|art[íi]stic|m[úu]sic|teatr|audiovisual|carnaval|literat|patrim[ôo]nio"),
    ("esporte", r"esport|desport|atleta|gin[áa]stic|futebol"),
    ("assistencia_social", r"assistenc|socioassisten|acolhiment|vulnerab|\bsuas\b|cras|creas"),
    ("crianca_adolescente", r"crian[çc]a|adolescente|\beca\b|cmdca|juventude"),
    ("pessoa_idosa", r"idos[ao]|terceira\s+idade|longevi"),
    ("meio_ambiente", r"ambient|res[íi]duo|reciclag|sustentab|arboriza|clima"),
    ("infraestrutura", r"pavimenta|ilumina[çc][ãa]o|obra|saneament|drenagem|reforma"),
    ("direitos_humanos", r"direitos\s+humanos|igualdade|racial|mulher|lgbt|defici[êe]nc"),
    ("seguranca_alimentar", r"alimenta[çc][ãa]o|merenda|cesta|nutri[çc]|agricultura\s+familiar"),
)

UFS = ("AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO").split()


# --------------------------------------------------------------- utilidades
def _texto(reg: dict) -> str:
    return " ".join(str(reg.get(c) or "") for c in ("titulo", "evidencia"))


def _iso(br: str) -> str | None:
    m = _DATA_BR.fullmatch(br.strip())
    if not m:
        return None
    d, mth, y = m.groups()
    try:
        return date(int(y), int(mth), int(d)).isoformat()
    except ValueError:
        return None


def data_do_evento(reg: dict) -> str:
    """Data real do acontecimento: a do diário no título, ou o período/coleta."""
    m = _DATA_ISO.search(reg.get("titulo", ""))
    if m:
        return m.group(0)
    p = (reg.get("caracterizacao") or {}).get("periodo") or {}
    return str(p.get("inicio") or reg.get("coletado_em") or "")[:10]


def classificar(reg: dict) -> dict:
    """Fase 1+2 sobre o material já coletado: o que este registro é."""
    txt = _texto(reg)
    ruido = bool(_EH_RUIDO.match(reg.get("titulo", "").strip()))
    eh_edital = bool(_EH_EDITAL.search(txt)) and not ruido
    area = next((a for a, rx in AREAS if re.search(rx, txt, re.I)), "outros")
    territorio = str(reg.get("territorio") or "")
    uf = territorio.split("/")[0].strip().upper()
    uf = uf if uf in UFS else None
    if not uf:
        m = re.search(r"\b([A-Z]{2})\b\s*\)|/([A-Z]{2})\b", reg.get("titulo", ""))
        cand = (m.group(1) or m.group(2)).upper() if m else None
        uf = cand if cand in UFS else None
    nivel = reg.get("nivel") or ((reg.get("caracterizacao") or {}).get("esfera"))
    if not nivel:
        tf = str(reg.get("tipo_fonte") or "")
        nivel = ("municipal" if "municipal" in tf else
                 "federal" if "federal" in tf or "pncp" in tf else None)
    return {"eh_edital": eh_edital, "ruido": ruido, "area": area,
            "uf": uf, "nivel": nivel,
            "programa": (reg.get("caracterizacao") or {}).get("programa_id"),
            "financiador": reg.get("fonte_nome")}


def extrair(reg: dict, hoje: date) -> dict:
    """Só o que o texto realmente traz. Ausência vira lacuna declarada."""
    txt = _texto(reg)
    lacunas = []
    fim = _iso(reg.get("prazo_texto") or "") or (
        _iso(_FIM.search(txt).group(1)) if _FIM.search(txt) else None)
    inicio = _iso(_INICIO.search(txt).group(1)) if _INICIO.search(txt) else None
    valores = [v for v in _VALOR.findall(txt)][:3]
    exigencias = sorted({m.group(0).lower().strip() for m in _EXIGENCIA.finditer(txt)})[:25]

    tem_resultado = bool(_RESULTADO.search(txt))
    vencedores = sorted({n for m in _VENCEDOR.finditer(txt)
                         if (n := _nome_de_entidade(m.group(1)))})[:6]
    criterios = sorted({re.sub(r"\s+", " ", m.group(0)).strip()
                        for m in _CRITERIO.finditer(txt)})[:4]
    if tem_resultado and not vencedores:
        lacunas.append("publicação menciona resultado/homologação, mas a evidência "
                       "coletada não nomeia o vencedor — buscar o ato integral")
    if not tem_resultado:
        lacunas.append("sem publicação de resultado na evidência: vencedor e fator "
                       "decisivo desconhecidos")
    if not criterios:
        lacunas.append("critério de julgamento não consta da evidência")
    if not fim:
        lacunas.append("prazo final não declarado na evidência")
    if not exigencias:
        lacunas.append("requisitos não detalhados na evidência (título de diário "
                       "costuma trazer só a ementa)")

    estado = ("encerrado" if fim and fim < hoje.isoformat()
              else "aberto" if fim else "indeterminado")
    return {"inicio": inicio, "fim": fim, "estado_prazo": estado,
            "valores_citados": valores, "exigencias_detectadas": exigencias,
            "tem_resultado_publicado": tem_resultado,
            "vencedores_identificados": vencedores,
            "criterios_de_julgamento": criterios,
            "lacunas": lacunas}


def chave_ano(reg: dict, classe: dict, dt: str) -> tuple[str, str]:
    titulo = reg.get("titulo") or ""
    m = re.search(r"\b(?:edital|chamamento|chamada|sele[çc][ãa]o)\D{0,20}?"
                  r"(\d{1,4})\s*/\s*(20\d{2})", titulo, re.I)
    ano = (m.group(2) if m else (dt[:4] or str(date.today().year)))
    base = (f'{reg.get("fonte_id","fonte")}-edital-{m.group(1)}' if m
            else f'{reg.get("fonte_id","fonte")}-{slug(titulo)[:44]}')
    return slug(base)[:80], ano


# ------------------------------------------------------------ mês a mês
def catalogar_mes(mes: str, registros: list[dict], hoje: date) -> dict:
    """Processa UM mês isoladamente, com checagem e relatório de erros."""
    gravados, descartados, erros = 0, [], []
    resumo = {"areas": Counter(), "estados": Counter(), "com_resultado": 0,
              "com_vencedor": 0, "com_prazo": 0}
    for reg in registros:
        try:
            classe = classificar(reg)
            if not classe["eh_edital"]:
                descartados.append({"id": reg["id"], "titulo": reg.get("titulo", "")[:90],
                                    "motivo": "ruído de portal" if classe["ruido"]
                                              else "sem vocabulário de edital"})
                continue
            dados = extrair(reg, hoje)
            dt = data_do_evento(reg)
            chave, ano = chave_ano(reg, classe, dt)
            pasta = OPORTUNIDADES / chave / ano
            pasta.mkdir(parents=True, exist_ok=True)
            ficha = {
                "id": reg["id"], "chave": chave, "ano": ano,
                "titulo": reg.get("titulo"), "url": reg.get("url"),
                "fonte_id": reg.get("fonte_id"), "fonte_nome": reg.get("fonte_nome"),
                "territorio": reg.get("territorio"), "tipo_fonte": reg.get("tipo_fonte"),
                "data_publicacao": dt, "mes_referencia": mes,
                "origem": "catalogacao_historica_5_anos",
                "fases_aplicadas": [1, 2],
                **classe, **dados,
                "evidencia": str(reg.get("evidencia") or "")[:1200],
                "hash_evidencia": reg.get("hash_evidencia"),
                "catalogado_em": now_iso(),
                "nota": ("catalogação histórica: fases 1 e 2. Requisitos e "
                         "vencedores só constam quando publicados na evidência."),
            }
            # preserva histórico do mesmo edital em anos diferentes
            existente = pasta / "ficha.json"
            if existente.exists():
                antiga = load_json(existente)
                if antiga.get("id") != ficha["id"]:
                    with (pasta / "ocorrencias.jsonl").open("a", encoding="utf-8") as h:
                        h.write(json.dumps(ficha, ensure_ascii=False) + "\n")
                    gravados += 1
                    continue
            write_json(existente, ficha)
            gravados += 1
            resumo["areas"][classe["area"]] += 1
            resumo["estados"][dados["estado_prazo"]] += 1
            resumo["com_resultado"] += bool(dados["tem_resultado_publicado"])
            resumo["com_vencedor"] += bool(dados["vencedores_identificados"])
            resumo["com_prazo"] += bool(dados["fim"])
        except Exception as exc:
            erros.append({"id": reg.get("id"), "erro": f"{type(exc).__name__}: {exc}"})
    rel = {"mes": mes, "recebidos": len(registros), "catalogados": gravados,
           "descartados": len(descartados), "erros": len(erros),
           "resumo": {k: (dict(v) if isinstance(v, Counter) else v)
                      for k, v in resumo.items()},
           "amostra_descartes": descartados[:5], "detalhe_erros": erros[:5],
           "executado_em": now_iso()}
    RELATORIOS.mkdir(parents=True, exist_ok=True)
    write_json(RELATORIOS / f"{mes}.json", rel)
    return rel


def run(anos: int = 5, hoje: date | None = None, limite_meses: int | None = None) -> dict:
    """Varredura histórica completa, mês a mês, dos últimos `anos` anos."""
    hoje = hoje or date.today()
    corte = date(hoje.year - anos, hoje.month, 1).isoformat()[:7]
    por_mes: dict[str, list] = defaultdict(list)
    for reg in carregar_oportunidades().values():
        if reg.get("status") in {"quarentena_prompt_injection", "descartada"}:
            continue
        mes = data_do_evento(reg)[:7]
        if mes and mes >= corte:
            por_mes[mes].append(reg)

    meses = sorted(por_mes)
    if limite_meses:
        meses = meses[:limite_meses]
    relatorios = [catalogar_mes(m, por_mes[m], hoje) for m in meses]
    total = {
        "executado_em": now_iso(), "janela": f"{corte} → {hoje.isoformat()[:7]}",
        "meses_processados": len(relatorios),
        "recebidos": sum(r["recebidos"] for r in relatorios),
        "catalogados": sum(r["catalogados"] for r in relatorios),
        "descartados": sum(r["descartados"] for r in relatorios),
        "erros": sum(r["erros"] for r in relatorios),
        "meses": [{k: r[k] for k in ("mes", "recebidos", "catalogados",
                                     "descartados", "erros")} for r in relatorios],
    }
    write_json(RELATORIOS / "consolidado.json", total)
    return total


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2)[:3000])
