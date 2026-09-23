"""AS OITO CORREÇÕES DE MOTOR — parecer de 23/09/2026.

Cada uma nasceu de um erro medido, e cada uma traz o teste que comprova a correção. A ordem é
de retorno: a primeira sozinha corta 85,8% do trabalho de verificação.

    M1  abrangência ANTES da verificação, não depois
    M2  patrocinador nacional com edital territorial
    M3  requisito de habilitação como campo de primeira classe
    M4  porte do proponente: quem pode ser proponente e quem entra como executor
    M5  um registro, vários editais
    M6  mecanismo permanente não é edital sem prazo
    M7  hora, não só dia
    M8  ano eleitoral como restrição de mecanismo

O fio comum entre elas: o sistema vinha decidindo pelo QUE A FONTE É, e precisa decidir pelo
QUE O EDITAL DIZ. Uma fonte nacional pode publicar edital de um município só; um edital de
fomento pode exigir doutorado; um portal pode anunciar cinco editais num registro.
"""
from __future__ import annotations

import re
from datetime import date

from .nucleo import ROOT, load_json

# A abrangência que o titular aprovou. Tudo em M1 e M2 depende dela.
ABRANGENCIA = {"nacional": True, "estados": ["GO"], "municipios": ["GO/Goiania"]}

UF_TODAS = ("AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO").split()


def _sem_acento(s: str) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", str(s or "").lower())
                   if unicodedata.category(c) != "Mn")


# ── M1 · abrangência antes da verificação ───────────────────────────────────────────
def alcance(e: dict) -> tuple[str, str]:
    """Onde este edital alcança? Chamado LOGO APÓS a triagem de objeto e ANTES de verificar.

    O sistema verificava 695 registros para descobrir na fase 2 que 8 serviam. Perguntar
    'isto é nosso?' antes de gastar uma requisição corta 85,8% do trabalho — e não perde
    nada, porque o que está fora da abrangência estaria fora no fim de qualquer jeito.
    """
    uf = str(e.get("uf") or "").upper()[:2]
    texto = _sem_acento(" ".join(str(e.get(c) or "") for c in ("titulo", "objeto", "orgao", "fonte_nome")))
    if uf == "GO" or "goiania" in texto or "goias" in texto:
        return "dentro", f"Goiás ou Goiânia{f' (UF {uf})' if uf else ''}"
    if uf and uf in UF_TODAS:
        return "fora", f"edital de {uf}: proponente precisa ter sede ou atuação lá"
    nac = any(p in texto for p in ("nacional", "todo o pais", "todo o territorio", "federal",
                                   "âmbito nacional", "ambito nacional"))
    territorio, onde = territorio_do_objeto(e)          # M2: nacional pode ser territorial
    if territorio:
        return "fora", f"fonte nacional, mas a chamada é fechada a {onde}"
    if nac:
        return "dentro", "alcance nacional"
    return "indefinido", "sem UF declarada e sem marca de alcance nacional"


# ── M2 · patrocinador nacional com edital territorial ───────────────────────────────
REGIOES = {
    "litoral do parana": "PR", "litoral paranaense": "PR", "baixada santista": "SP",
    "vale do ribeira": "SP", "sertao pernambucano": "PE", "reconcavo baiano": "BA",
    "vale do jequitinhonha": "MG", "regiao dos lagos": "RJ", "zona da mata": "MG",
    "serra gaucha": "RS", "oeste catarinense": "SC", "agreste": "PE", "cariri": "CE",
    "amazonia legal": "AM", "pantanal": "MS", "semiarido": "BA",
}


def territorio_do_objeto(e: dict) -> tuple[bool, str]:
    """O Funbio é fonte nacional e suas chamadas 07 e 08/2026 são fechadas ao litoral do
    Paraná. O filtro aprovou pela FONTE e errou pelo OBJETO. Aqui se lê o objeto."""
    texto = _sem_acento(" ".join(str(e.get(c) or "") for c in ("titulo", "objeto", "resumo")))
    for regiao, uf in REGIOES.items():
        if regiao in texto and uf not in ABRANGENCIA["estados"]:
            return True, f"{regiao} ({uf})"
    # "municípios de X, Y e Z" numa fonte nacional também fecha o território
    m = re.search(r"municipios? d[eoa]s? ([a-z\s,]{6,90})", texto)
    if m and not any(g in m.group(1) for g in ("goiania", "goias")):
        nomeados = [x.strip() for x in re.split(r",| e ", m.group(1)) if len(x.strip()) > 3][:4]
        if nomeados:
            return True, "municípios nomeados: " + ", ".join(nomeados)
    for uf in UF_TODAS:
        if uf in ABRANGENCIA["estados"]:
            continue
        if re.search(rf"\b(estado d[eoa] )?{uf}\b", str(e.get("objeto") or ""), re.I) and \
           re.search(r"exclusiv|somente|apenas|restrit", texto):
            return True, f"restrito a {uf}"
    return False, ""


# ── M3 · requisito de habilitação como campo de primeira classe ─────────────────────
# São eliminatórios ANTES do mérito: não adianta o projeto ser bom se o coordenador não tem
# doutorado. Em 09 e 15/09 o sistema chamou o FME de "a maior oportunidade aberta" sem ver
# essa linha do edital.
REQUISITOS = {
    "doutorado": (r"doutorad[oa]", "coordenador precisa ter diploma de doutorado"),
    "mestrado": (r"mestrad[oa]", "coordenador precisa ter mestrado"),
    "registro_cmdca": (r"registro no cmdca|inscri[çc][ãa]o no cmdca|conselho municipal dos direitos",
                       "registro no CMDCA do município"),
    "conselho_educacao": (r"conselho municipal de educa", "inscrição no Conselho Municipal de Educação"),
    "varias_regioes": (r"cinco regi[õo]es|5 regi[õo]es|todas as regi[õo]es do pa[íi]s",
                       "execução em cinco regiões do país"),
    "tempo_minimo": (r"(\d+)\s*\(?\w*\)?\s*anos? de (exist[êe]ncia|funcionamento|atua)",
                     "tempo mínimo de existência"),
    "certificacao": (r"cebas|utilidade p[úu]blica federal|oscip", "certificação específica"),
    "sede_no_municipio": (r"sede no munic[íi]pio|sediada no munic[íi]pio", "sede no município do edital"),
    "transferegov": (r"transferegov|plataforma \+brasil", "cadastro no Transferegov"),
}

# O que a AMC Jardim América tem. O que não está aqui é barreira até prova em contrário.
PERFIL_AMC = {"tempo_minimo", "sede_no_municipio"}


def requisitos_de_habilitacao(texto: str) -> list[dict]:
    t = str(texto or "")
    achados = []
    for chave, (padrao, rotulo) in REQUISITOS.items():
        if re.search(padrao, t, re.I):
            achados.append({"chave": chave, "requisito": rotulo,
                            "atendido_pela_amc": chave in PERFIL_AMC,
                            "eliminatorio": chave not in PERFIL_AMC})
    return achados


def elegivel(e: dict) -> tuple[bool, list[str]]:
    reqs = requisitos_de_habilitacao(" ".join(str(e.get(c) or "") for c in
                                              ("objeto", "resumo", "requisitos", "titulo")))
    barreiras = [r["requisito"] for r in reqs if r["eliminatorio"]]
    return (not barreiras), barreiras


# ── M4 · porte do proponente ────────────────────────────────────────────────────────
FAIXA_AMC = (500_000, 3_000_000)          # onde a AMC cabe, como executora


def papel_possivel(e: dict) -> dict:
    """O BNDES Periferias exige projeto de R$ 20 milhões. A AMC não é proponente: é
    organização de base no subprojeto. A ação recomendada muda por inteiro — não é
    'inscrever-se', é 'procurar quem vai propor'."""
    texto = " ".join(str(e.get(c) or "") for c in ("objeto", "resumo", "valor", "titulo"))
    minimo = None
    for m in re.finditer(r"R\$\s?([\d\.]+)\s*(milh|mil\b)?", texto, re.I):
        try:
            n = float(m.group(1).replace(".", ""))
        except ValueError:
            continue
        if (m.group(2) or "").lower().startswith("milh"):
            n *= 1_000_000
        minimo = n if minimo is None else min(minimo, n)
    if minimo is None:
        return {"papel": "proponente", "porque": "sem valor mínimo declarado"}
    if minimo > FAIXA_AMC[1]:
        return {"papel": "organizacao_de_base", "valor_minimo": minimo,
                "porque": f"projeto mínimo de R$ {minimo:,.0f} está acima da faixa da associação",
                "acao": "entrar como organização de base no subprojeto, não se inscrever"}
    return {"papel": "proponente", "valor_minimo": minimo, "acao": "inscrever-se"}


# ── M5 · um registro, vários editais ────────────────────────────────────────────────
def desdobrar(e: dict) -> list[dict]:
    """Porto Feliz/SP: um registro do PNCP com cinco editais PNAB, cinco inscrições
    separadas. Contar como um faz perder quatro."""
    anexos = e.get("anexos") or e.get("modelos") or []
    numeros, vistos = [], set()
    for a in anexos:
        nome = a.get("nome") if isinstance(a, dict) else str(a)
        m = re.search(r"edital\D{0,6}(\d{1,3})[/\-](\d{4})", str(nome), re.I)
        if m:
            n = f"{m.group(1)}/{m.group(2)}"
            if n not in vistos:
                vistos.add(n)
                numeros.append((n, nome))
    if len(numeros) < 2:
        return [e]
    return [{**e, "id": f"{e.get('id')}-{i+1}", "numero_do_edital": n,
             "titulo": f"{e.get('titulo','')} — Edital {n}"[:170],
             "desdobrado_de": e.get("id"), "anexo": nome}
            for i, (n, nome) in enumerate(numeros)]


# ── M6 · mecanismo permanente ───────────────────────────────────────────────────────
PERMANENTES = ("receita federal", "pena pecuniaria", "presta[çc][ãa]o pecuniaria", "impactarte",
               "emenda parlamentar", "fluxo continuo", "fluxo cont[íi]nuo", "permanente",
               "a qualquer tempo", "sem prazo de encerramento")


def e_permanente(e: dict) -> tuple[bool, str]:
    """Prazo nulo por NATUREZA, não por falta de verificação. Hoje esses entram na fila de
    pesquisa e nunca saem, porque ninguém vai achar uma data que não existe."""
    texto = _sem_acento(" ".join(str(e.get(c) or "") for c in ("titulo", "objeto", "orgao", "resumo")))
    for p in PERMANENTES:
        if re.search(_sem_acento(p), texto):
            return True, f"mecanismo permanente ({p}): habilita-se a qualquer tempo"
    return False, ""


def classificar_prazo(e: dict) -> dict:
    perm, porque = e_permanente(e)
    if perm:
        return {"classe": "mecanismo_permanente", "prazo": None, "porque": porque,
                "como_se_habilita": e.get("como_se_habilita") or "a levantar na fonte",
                "sai_da_fila_de_prazo": True}
    return {"classe": "edital_com_prazo", "prazo": e.get("fim"), "sai_da_fila_de_prazo": False}


# ── M7 · hora, não só dia ───────────────────────────────────────────────────────────
def hora_de_encerramento(texto: str) -> str | None:
    """Ipu/CE encerra às 17h; Guaíra às 17h; o FME às 23h59. Guardar só a data faz o painel
    dizer 'hoje' quando já passou."""
    m = re.search(r"at[ée]\s+(?:as\s+)?(\d{1,2})\s*[h:]\s*(\d{2})?", str(texto or ""), re.I)
    if not m:
        return None
    h = int(m.group(1))
    return f"{h:02d}:{int(m.group(2) or 0):02d}" if 0 <= h <= 23 else None


# ── M8 · ano eleitoral como restrição ───────────────────────────────────────────────
def restricao_eleitoral(e: dict, hoje: date | None = None) -> dict | None:
    """A Receita Federal veda entrega de mercadorias a OSC em ano eleitoral. Já havia a
    armadilha do portal de Goiás, que suspende notícias. É o mesmo fenômeno em duas formas:
    a habilitação continua valendo, a entrega é que para."""
    texto = _sem_acento(" ".join(str(e.get(c) or "") for c in ("titulo", "objeto", "orgao", "resumo")))
    if not any(p in texto for p in ("receita federal", "mercadoria apreendida", "bem apreendido",
                                    "doacao de mercadoria")):
        return None
    ano = (hoje or date.today()).year
    eleitoral = ano % 2 == 0
    return {"restricao": "ano eleitoral", "em_vigor": eleitoral,
            "o_que_para": "a entrega das mercadorias",
            "o_que_continua": "a habilitação, que deve ser feita agora",
            "recomendacao": ("habilitar agora, entrega suspensa até o fim do período eleitoral"
                             if eleitoral else "sem restrição neste ano")}


def avaliar(e: dict) -> dict:
    """As oito correções aplicadas de uma vez, na ordem em que o motor as encontra."""
    alc, porque_alc = alcance(e)                                   # M1 + M2
    eleg, barreiras = elegivel(e)                                  # M3
    papel = papel_possivel(e)                                      # M4
    prazo = classificar_prazo(e)                                   # M6
    texto = " ".join(str(e.get(c) or "") for c in ("objeto", "resumo", "titulo"))
    return {"alcance": alc, "alcance_porque": porque_alc,
            "verificar": alc == "dentro",                          # M1: só verifica o que serve
            "elegivel": eleg, "barreiras": barreiras,
            "papel": papel, "prazo": prazo,
            "hora_de_encerramento": hora_de_encerramento(texto),   # M7
            "restricao_eleitoral": restricao_eleitoral(e),         # M8
            "desdobra_em": len(desdobrar(e))}                      # M5
