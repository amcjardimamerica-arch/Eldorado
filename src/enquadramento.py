"""ENQUADRAMENTO — Farol de Alexandria, fases 3 e 4.

Regra inicial do titular: (1) quais associações existem no banco; (2) quais
editais estão abertos; (3) usar a IA mais eficiente para obter as informações
que faltam nos 12 itens de cada edital aberto; (4) avaliar o enquadramento de
cada associação — chances de êxito e pontuação estimada — com o Farol de
aderência.

Ferramentas que esta parte oferece ao painel (tudo determinístico aqui; a IA
complementa quando há credencial):
  • fila de investigação por IA — o que falta em cada edital e o que a IA
    obteve (modelo, itens, custo em tokens);
  • aderência 0–100 por par associação × edital (área, território, documentos,
    tempo de existência, itens comprovados) e Farol (verde/amarelo/vermelho);
  • simulador de pontuação — critérios do edital (extraídos ou estimados) ×
    perfil da associação, com "o que sobe a nota";
  • checklist de documentos — exigidos × válidos × pendentes, com vencimentos;
  • cronograma reverso — do prazo final para trás: protocolo, revisão do
    conselho, rascunho, coleta de documentos;
  • ranking de êxito — os editais que valem a inscrição hoje, por associação.

Estado: dados/associacoes/<id>/farol/<edital_id>.json (parecer por edital,
lido pelo cruzamento do painel) e estado/enquadramento.json (fila e resumo).
"""
from __future__ import annotations

import glob
import json
import os
import re
from datetime import date, timedelta
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json
from .completude_biblioteca import ITENS

ESTADO = ROOT / "estado/enquadramento.json"
DOC_ROTULO = {"estatuto": "Estatuto social registrado", "ata_eleicao": "Ata de eleição da diretoria", "cnpj": "Cartão CNPJ ativo",
              "certidao_federal": "Certidão negativa federal (RFB/PGFN)", "certidao_estadual": "Certidão negativa estadual", "certidao_municipal": "Certidão negativa municipal",
              "cndt": "CNDT (débitos trabalhistas)", "crf_fgts": "CRF do FGTS", "comprovante_endereco": "Comprovante de endereço da sede",
              "rg_cpf_dirigente": "RG e CPF do dirigente", "plano_de_trabalho": "Plano de trabalho", "certificacao_utilidade_publica": "Título de utilidade pública",
              "relatorio_atividades": "Relatório de atividades", "conta_bancaria": "Conta bancária específica", "cebas": "CEBAS", "inscricao_conselho": "Inscrição no conselho de política (CMAS/CMDCA/CMI)"}
VALIDADE_DIAS = {"certidao_federal": 180, "certidao_estadual": 90, "certidao_municipal": 90, "cndt": 180, "crf_fgts": 30}


def associacoes() -> list[dict]:
    saida = []
    for fp in sorted(glob.glob(str(ROOT / "dados/associacoes/*/perfil*.json"))):
        if "EXEMPLO" in fp:
            continue
        a = load_json(Path(fp)); a["_pasta"] = Path(fp).parent.name; saida.append(a)
    return saida


def editais_abertos(dados: dict) -> list[dict]:
    return [e for e in dados.get("editais", []) if e.get("situacao_inscricao") in ("aberta", "possivel")]


COMPLEMENTOS = ROOT / "dados/editais/complementos"


def complementos(e: dict) -> dict:
    """Informações faltantes que o titular subiu à mão para este edital
    (dados/editais/complementos/<id>/*.json ou *.md): viram itens comprovados
    com fonte 'complemento manual'."""
    pasta = COMPLEMENTOS / e["id"]
    saida = {}
    if not pasta.exists():
        return saida
    for f in sorted(pasta.glob("*")):
        if f.suffix == ".json":
            try:
                for k, v in load_json(f).items():
                    if v not in (None, ""): saida[k] = {"valor": v, "fonte": f.name}
            except Exception:
                pass
        elif f.suffix in (".md", ".txt"):
            txt = f.read_text(encoding="utf-8", errors="replace")
            for item in ITENS:
                m = re.search(rf"(?im)^\s*[-*]?\s*{re.escape(item)}\s*[:—-]\s*(.+)$", txt)
                if m: saida[item] = {"valor": m.group(1).strip()[:300], "fonte": f.name}
    return saida


def abrangencia(a: dict) -> dict:
    arq = ROOT / "dados/associacoes" / a["_pasta"] / "abrangencia.json"
    base = {"nacional": True, "estados": [], "municipios_aprovados": [], "municipios_candidatos": []}
    if arq.exists():
        base.update({k: v for k, v in load_json(arq).items() if k in base})
    # cidades candidatas: as 50 maiores do estado entram automaticamente (rosa até aprovação)
    mm = ROOT / "config/municipios_maiores.json"
    maiores = load_json(mm).get("maiores", {}) if mm.exists() else {}
    for uf in base["estados"]:
        for c in maiores.get(uf, []):
            k = f"{uf}/{c}"
            if k not in base["municipios_candidatos"] and k not in base["municipios_aprovados"]: base["municipios_candidatos"].append(k)
    # a atuação do perfil também vale
    for t in (a.get("territorios") or []):
        partes = t.split("/")
        if len(partes) == 1 and partes[0] != "BR" and partes[0] not in base["estados"]: base["estados"].append(partes[0])
        if len(partes) >= 2 and "/".join(partes[:2]) not in base["municipios_aprovados"]: base["municipios_aprovados"].append("/".join(partes[:2]))
    return base


def _cidade_de(e: dict) -> str | None:
    """Cidade do edital: campo municipio; 'Diário Oficial de X (UF)'; 'PREFEITURA
    MUNICIPAL DE X'; 'Município de X'; 'Prefeitura de X' no título/fonte/objeto."""
    if e.get("municipio"):
        return e["municipio"]
    alvo = " ".join(str(e.get(k) or "") for k in ("titulo", "fonte_nome", "objeto"))
    for rx in (r"Di[áa]rio Oficial de ([^()—\-]+?)\s*\(", r"PREFEITURA (?:MUNICIPAL )?D[EA] ([A-ZÀ-Ú][A-ZÀ-Úa-zà-ú' ]{2,40}?)(?:\s*[-–—/(]|\s+TORNA|\s+GO\b|\s*$|,)",
               r"MUNIC[ÍI]PIO DE ([A-ZÀ-Ú][A-ZÀ-Úa-zà-ú' ]{2,40}?)(?:\s*[-–—/(,]|\s+[A-Z]{2}\b|\s*$)", r"Prefeitura (?:Municipal )?de ([A-ZÀ-Ú][\wà-ú' ]{2,40}?)(?:\s*[-–—/(,]|\s*$)", r"C[âa]mara Municipal de ([A-ZÀ-Ú][\wà-ú' ]{2,40}?)(?:\s*[-–—/(,]|\s*$)"):
        m = re.search(rx, alvo)
        if m:
            return m.group(1).strip().title().replace(" De ", " de ").replace(" Do ", " do ").replace(" Da ", " da ")
    return None


def filtro_geografico(a: dict, e: dict) -> bool:
    """Regra do titular: nacional vale para todo o Brasil; estadual pega editais
    do estado (inclusive regionais que o contenham); municipal só as cidades
    aprovadas. Editais de cidades CANDIDATAS (50 maiores) não passam — ficam em
    rosa choque para aprovação manual (ver candidato_aprovacao)."""
    ab = abrangencia(a)
    uf = e.get("uf")
    if not uf:
        return bool(ab["nacional"]) and (e.get("abrangencia") == "nacional" or e.get("nivel") == "federal" or e.get("nivel") is None)
    ufs = {uf} | set(e.get("ufs") or [])
    if not (ufs & set(ab["estados"])):
        return False
    cidade = _cidade_de(e)
    if e.get("nivel") in ("estadual", "federal", "regional") or (not cidade and e.get("abrangencia") in ("estadual", "regional")):
        return True
    if not cidade:
        return True                                   # edital do estado sem cidade identificada: vale para o estado
    return f"{uf}/{cidade}" in ab["municipios_aprovados"] or e.get("nivel") is None and cidade.lower() in {c.split("/")[-1].lower() for c in ab["municipios_aprovados"]}


def candidato_aprovacao(a: dict, e: dict) -> bool:
    """Edital de cidade candidata (não aprovada) do estado da associação."""
    ab = abrangencia(a); uf = e.get("uf"); cidade = _cidade_de(e)
    if not uf or not cidade or uf not in ab["estados"]:
        return False
    chave = f"{uf}/{cidade}"
    return chave in ab["municipios_candidatos"] and chave not in ab["municipios_aprovados"]


def extraido(e: dict) -> dict:
    from .fonte_edital import EXTRAIDOS
    arq = EXTRAIDOS / f"{e['id']}.json"
    return load_json(arq) if arq.exists() else {}


def itens_faltantes(e: dict) -> list[str]:
    ex = extraido(e)
    if ex.get("itens") is not None and ex.get("tentativas") is not None:
        comp = complementos(e); disp = ex.get("dispensaveis") or {}
        return [i for i in (ex.get("faltam") or []) if i not in comp and i not in disp]
    return _itens_faltantes_basico(e)


def _itens_faltantes_basico(e: dict) -> list[str]:
    itens = ((e.get("requisitos_condicoes_valores") or {}).get("itens") or (e.get("detalhes") or {}).get("itens_11") or [])
    if not itens:
        # sem grade: deduz dos campos
        tem = {"Objeto": bool(e.get("objeto")), "Prazo de inscrição": bool(e.get("fim")), "Órgão / financiador": bool(e.get("fonte_nome")),
               "Território": bool(e.get("uf") or e.get("abrangencia") == "nacional"), "Esfera": e.get("nivel") in ("federal", "estadual", "municipal"),
               "Área de atuação": e.get("area") not in (None, "outros"), "Valor": bool(e.get("valor_texto")),
               "Requisitos": bool((e.get("detalhes") or {}).get("documentos_exigidos")), "Anexos": bool(e.get("anexos"))}
        comp = complementos(e)
        return [i for i in ITENS if not tem.get(i) and i not in comp]
    faltam = [i["item"] for i in itens if not i.get("comprovado")]
    comp = complementos(e)
    return [i for i in faltam if i not in comp]


# ───────────────────────── IA: completar os 12 itens do edital aberto ─────────────────────────
def prompt_itens(e: dict, faltam: list[str]) -> str:
    return (f"Edital: {e.get('titulo')}\nÓrgão: {e.get('fonte_nome')} — {e.get('uf') or 'Brasil'} ({e.get('nivel')}).\nURL: {e.get('url')}\n"
            f"Evidência já obtida: {(e.get('objeto') or e.get('resumo') or '')[:400]}\n"
            f"Faltam EXATAMENTE estes itens: {', '.join(faltam)}.\n"
            "Abra a publicação oficial (e anexos) e devolva SOMENTE JSON: {\"itens\": {<item>: <valor textual ou null>}, "
            "\"criterios_pontuacao\": [{\"criterio\": <texto>, \"peso\": <número ou null>}], \"documentos_exigidos\": [<lista>], "
            "\"fonte\": <URL onde leu>}. Não invente: sem fonte, null.")


def prompt_enquadramento(a: dict, e: dict, itens: dict, criterios: list[dict]) -> str:
    return (f"Associação: {a.get('nome')} — áreas {', '.join(a.get('areas') or [])}; território {', '.join(a.get('territorios') or [])}; "
            f"{a.get('anos_existencia')} anos; documentos válidos: {', '.join(a.get('documentos_validos') or []) or 'nenhum informado'}; "
            f"experiências: {json.dumps(a.get('experiencias') or [], ensure_ascii=False)[:600]}.\n"
            f"Edital: {e.get('titulo')} — itens: {json.dumps(itens, ensure_ascii=False)[:1200]} — critérios: {json.dumps(criterios, ensure_ascii=False)[:600]}.\n"
            "Como conselho de sete lentes (extremamente pessimista → extremamente otimista, neutro decide): avalie o ENQUADRAMENTO da associação, "
            "as CHANCES DE ÊXITO (0–100) e a PONTUAÇÃO ESTIMADA pelos critérios, e diga o que faltaria para subir a nota. "
            "Devolva SOMENTE JSON: {\"aderencia\": <0-100>, \"chances\": <0-100>, \"pontuacao_estimada\": <texto>, \"lentes\": {<lente>: <frase>}, "
            "\"decisao\": <texto>, \"para_subir\": [<ações>], \"riscos\": [<textos>]}.")


def _chamar(modelo: str, prompt: str, max_tokens: int = 1400, web: bool = False, tarefa: str | None = None) -> dict:
    from .opressores import _chamar as _c
    return _c(modelo, prompt, max_tokens, web=web, tarefa=tarefa)


# ───────────────────────── avaliação determinística (piso) ─────────────────────────
def aderencia(a: dict, e: dict) -> dict:
    areas = set(a.get("areas") or []); terr = [t.upper() for t in (a.get("territorios") or [])]
    docs = set(a.get("documentos_validos") or []); anos = a.get("anos_existencia") or 0
    pts, por, subir = 0, [], []
    if e.get("area") in areas: pts += 35; por.append("área compatível")
    elif e.get("area") == "outros": pts += 15; por.append("área do edital não classificada")
    else: subir.append(f"edital de {e.get('area')} — a associação não atua nessa área")
    uf = e.get("uf")
    if (uf and uf in terr) or (not uf and e.get("abrangencia") == "nacional"): pts += 20; por.append("território compatível")
    elif uf: return {"nota": 0, "farol": "vermelho", "por": [f"território {uf} fora da atuação"], "para_subir": [], "elegivel": False}
    req = set((e.get("detalhes") or {}).get("documentos_exigidos") or [])
    if req:
        ok = len(req & docs) / len(req); pts += round(25 * ok); por.append(f"documentos {len(req & docs)}/{len(req)}")
        for d in sorted(req - docs): subir.append(f"obter {DOC_ROTULO.get(d, d)}")
    else:
        pts += 10; por.append("requisitos não extraídos (piso)")
    if anos >= 3: pts += 10; por.append(f"{anos} anos de existência")
    else: subir.append("edital pode exigir 3 anos de existência")
    faltam = itens_faltantes(e)
    comp = 12 - len(faltam); pts += round(10 * comp / 12); por.append(f"{comp}/12 itens comprovados")
    if faltam: subir.append(f"completar {len(faltam)} item(ns): {', '.join(faltam[:4])}{'…' if len(faltam) > 4 else ''}")
    nota = min(100, pts)
    return {"nota": nota, "farol": "verde" if nota >= 70 else "amarelo" if nota >= 45 else "vermelho", "por": por, "para_subir": subir, "elegivel": True}


def checklist(a: dict, e: dict) -> list[dict]:
    docs = a.get("documentos_validos") or []; pend = a.get("documentos_pendentes") or []
    validade = a.get("documentos_validade") or {}
    req = (e.get("detalhes") or {}).get("documentos_exigidos") or list(DOC_ROTULO)[:8]
    saida = []
    for d in req:
        v = validade.get(d); dias = None
        if v:
            try: dias = (date.fromisoformat(v[:10]) - date.today()).days
            except ValueError: pass
        elif d in VALIDADE_DIAS and d in docs: dias = None
        saida.append({"documento": d, "rotulo": DOC_ROTULO.get(d, d.replace("_", " ")),
                      "status": "válido" if d in docs and (dias is None or dias > 0) else "vencido" if d in docs else "pendente" if d in pend else "faltante",
                      "vence_em_dias": dias, "renovacao_dias": VALIDADE_DIAS.get(d)})
    return saida


def cronograma_reverso(e: dict, hoje: date) -> list[dict]:
    if not e.get("fim"):
        return []
    fim = date.fromisoformat(e["fim"][:10])
    marcos = [("Protocolo da inscrição", 1), ("Revisão final do conselho (7 lentes)", 3), ("Plano de trabalho e orçamento fechados", 7),
              ("Documentos e certidões reunidos", 12), ("Rascunho do projeto", 18), ("Decisão de concorrer", 21)]
    saida = []
    for nome, d in marcos:
        data = fim - timedelta(days=d)
        saida.append({"marco": nome, "data": data.isoformat(), "atrasado": data < hoje, "dias_para": (data - hoje).days})
    return saida


def simulador_pontuacao(a: dict, e: dict, criterios: list[dict] | None) -> dict:
    crit = criterios or [{"criterio": "Experiência da entidade na área", "peso": 30}, {"criterio": "Qualidade técnica do projeto", "peso": 30},
                         {"criterio": "Capacidade de execução e equipe", "peso": 20}, {"criterio": "Orçamento e contrapartida", "peso": 10}, {"criterio": "Território e público beneficiado", "peso": 10}]
    exp = len(a.get("experiencias") or []); cap = a.get("capacidade_execucao") or {}
    est, dicas = 0, []
    for c in crit:
        p = c.get("peso") or 0; nome = (c.get("criterio") or "").lower()
        if "experi" in nome: f = min(1, 0.4 + 0.15 * exp); dicas.append("anexar relatórios/atestados de projetos anteriores") if exp < 3 else None
        elif "capacid" in nome or "equipe" in nome: f = 0.7 if cap else 0.4; dicas.append("descrever equipe e estrutura no plano") if not cap else None
        elif "orçament" in nome or "contrapart" in nome: f = 0.6; dicas.append("detalhar orçamento por rubrica e contrapartida")
        elif "territ" in nome or "públic" in nome: f = 0.8 if (e.get("uf") in [t.upper() for t in (a.get("territorios") or [])]) else 0.5
        else: f = 0.6; dicas.append("projeto com metas, indicadores e cronograma físico-financeiro")
        est += p * f
    total = sum((c.get("peso") or 0) for c in crit) or 100
    return {"criterios": crit, "estimativa": round(100 * est / total), "origem_criterios": "edital" if criterios else "estimados (padrão de chamamentos)", "para_subir": [d for d in dicas if d][:5]}


DOCS_MROSC = ["estatuto", "ata_eleicao", "cnpj", "comprovante_endereco", "certidao_federal", "certidao_estadual", "certidao_municipal", "cndt", "crf_fgts",
              "relatorio_atividades", "plano_de_trabalho", "inscricao_conselho", "declaracao_nao_vedacao", "declaracao_conta_bancaria", "rg_cpf_dirigente"]


def parametros_da_fonte(e: dict) -> dict:
    """Ficha parametrizada da fonte (as 260): documentos, critérios e preditiva."""
    base = ROOT / "biblioteca_alexandria/fontes"
    for fid in (e.get("fonte_captacao_id"), e.get("fonte_id")):
        if fid and (base / str(fid) / "parametros.json").exists():
            return load_json(base / str(fid) / "parametros.json")
    # casamento por programa/órgão quando o edital não traz o id do catálogo
    cache = getattr(parametros_da_fonte, "_idx", None)
    if cache is None:
        cache = []
        for arq in base.glob("*/parametros.json"):
            f = load_json(arq)
            PARAR = {"edital", "editais", "programa", "municipal", "estadual", "federal", "projetos", "projeto", "publico", "público", "publica", "pública",
                     "entidade", "entidades", "secretaria", "nacional", "fomento", "termo", "termos", "apoio", "social", "sociais", "cultura", "cultural",
                     "parceria", "parcerias", "chamada", "chamamento", "recursos", "fundo", "fundos", "goias", "goiás", "goiania", "goiânia"}
            prog = {x for x in re.findall(r"[a-zà-ú]{5,}", f["programa"].lower()) if x not in PARAR}
            org = {x for x in re.findall(r"[a-zà-ú]{5,}", (f["orgao"] or "").lower()) if x not in PARAR}
            cache.append((prog, org, f))
        parametros_da_fonte._idx = cache
    alvo = f"{e.get('programa') or ''} {e.get('titulo') or ''} {e.get('fonte_nome') or ''} {e.get('orgao') or ''}".lower()
    APELIDOS = [(r"rouanet|pronac|salic", "captacao-036"), (r"lei de incentivo ao esporte|\blie\b", "captacao-040"),
                (r"goyazes", None), (r"mercadorias apreendidas|receita federal", None)]
    for rx, fid in APELIDOS:
        if fid and re.search(rx, alvo) and (base / fid / "parametros.json").exists():
            return load_json(base / fid / "parametros.json")
    melhor, nota = None, 0
    for prog, org, f in cache:
        np_ = sum(1 for t in prog if t in alvo)
        no = sum(1 for t in org if t in alvo)
        # exige casamento distintivo do PROGRAMA (o órgão sozinho não decide o rito)
        if np_ < max(1, min(2, len(prog))):
            continue
        n = np_ * 2 + no
        if n > nota:
            melhor, nota = f, n
    return melhor or {}


def _documentos_submissao(e: dict, f: dict) -> dict:
    """Tudo o que a inscrição exige: os documentos lidos do edital quando existem;
    senão o conjunto padrão de habilitação (Lei 13.019/2014, arts. 33-34 e
    Decreto 8.726/2016) até a IA extrair o rol do edital."""
    do_edital = list(f.get("documentos_exigidos_ia") or [])
    req = f.get("requisitos") or []
    if do_edital:
        return {"origem": "edital (extraído da fonte oficial)", "documentos": do_edital, "requisitos": req}
    par = parametros_da_fonte(e)
    if par:
        return {"origem": f"parametrização da fonte ({par['programa'][:60]}) — Lei 13.019/2014 e rito {par['tipo_recurso']}",
                "documentos": par["documentos_resumo"]["obrigatorios"], "nao_exigidos": par["documentos_resumo"]["nao_exigidos"],
                "requisitos": req or (par.get("exigencias_observadas") or [])}
    return {"origem": "padrão MROSC (Lei 13.019/2014, arts. 33–34) — até a IA extrair o rol do edital", "documentos": DOCS_MROSC, "requisitos": req}


def _quadro_ia(ex: dict, par: dict) -> dict:
    """Luzes por modelo: verde buscou e obteve; amarelo buscou e nada novo; vermelho não buscou/falhou."""
    cfg = load_json(ROOT / "config/ia.json") if (ROOT / "config/ia.json").exists() else {}
    mods = cfg.get("modelos") or {}
    ordem = [("Haiku 4.5", mods.get("busca_nivel_1", "claude-haiku-4-5")), ("Sonnet 5", mods.get("busca_nivel_2", "claude-sonnet-5")),
             ("Opus 5", mods.get("busca_nivel_3", "claude-opus-5"))]
    q = []
    for rot, mid in ordem:
        ts = [t for t in (ex.get("tentativas") or []) if t.get("modelo") == mid]
        if not ts: q.append({"modelo": rot, "sinal": "vermelho", "detalhe": "não buscou"})
        else:
            u = ts[-1]; q.append({"modelo": rot, "sinal": u.get("sinal") or ("verde" if u.get("itens_obtidos") else "amarelo" if u.get("status") == "respondeu" else "vermelho"),
                                  "detalhe": f"{u.get('status')} · {u.get('itens_obtidos', 0)} item(ns)"})
    ia = par.get("ia")
    q.append({"modelo": "Fable 5.1 (análise)", "sinal": "verde" if ia else "vermelho", "detalhe": "parecer emitido" if ia else (par.get("ia_status") or "não analisou")})
    return {"luzes": q, "papel": "Haiku → Sonnet → Opus buscam; Fable analisa"}


def _para_inscricao(a: dict, exigidos: list[str], faltam: list[str]) -> dict:
    """O que falta, objetivamente, para ter os documentos preenchidos e prontos
    na tela Documentos: documentos exigidos que a associação não tem válidos +
    itens do edital ainda não compreendidos."""
    pasta = ROOT / "dados/associacoes" / a["_pasta"] / "documentos"
    cert = load_json(pasta / "certidoes.json").get("certidoes", {}) if (pasta / "certidoes.json").exists() else {}
    regs = load_json(pasta / "registrados.json").get("registrados", {}) if (pasta / "registrados.json").exists() else {}
    tem = set(cert) | set(regs) | set(a.get("documentos_validos") or [])
    falta_docs = [d for d in exigidos if d not in tem]
    return {"documentos_faltantes": falta_docs, "documentos_prontos": [d for d in exigidos if d in tem], "itens_faltantes": faltam,
            "modelos_a_preencher": [d for d in exigidos if d in ("plano_de_trabalho", "declaracoes", "orcamento", "cronograma")],
            "pronto": not falta_docs and not faltam}


# ───────────────────────── execução ─────────────────────────
def run(limite_ia: int = 8) -> dict:
    hoje = date.today()
    dd = ROOT / "docs/dashboard-dados.json"
    if not dd.exists():
        return {"erro": "painel ainda não gerado"}
    dados = load_json(dd)
    cfg = load_json(ROOT / "config/ia.json") if (ROOT / "config/ia.json").exists() else {}
    modelo_itens = ((cfg.get("escalada_busca") or {}).get("cadeia") or [{"modelo": "claude-sonnet-4-5"}])[min(1, len((cfg.get("escalada_busca") or {}).get("cadeia") or [1]) - 1)]["modelo"]
    modelo_forte = (cfg.get("modelos") or {}).get("conselho_recursos", "claude-fable-5-1")
    est = load_json(ESTADO) if ESTADO.exists() else {"fila": {}, "execucoes": []}
    assoc = associacoes(); abertos = editais_abertos(dados)
    n_ia = 0; resumo = {"associacoes": len(assoc), "editais_abertos": len(abertos), "ia_itens": 0, "ia_enquadramento": 0, "em": now_iso()}
    compat = [e for e in abertos if any(filtro_geografico(a, e) for a in assoc)]     # filtro geográfico ANTES da IA
    from .fonte_edital import investigar
    mods = cfg.get("modelos") or {}
    modelos_extracao = [mods.get("busca_nivel_1", "claude-haiku-4-5"), mods.get("busca_nivel_2", "claude-sonnet-5"), mods.get("busca_nivel_3", "claude-opus-5")]
    modelo_forte = mods.get("analise_edital", modelo_forte)
    n_inv = 0
    for e in sorted(compat, key=lambda x: (x.get("situacao_inscricao") != "aberta", x.get("uf") != "GO", x.get("fim") or "9")):
        f = est["fila"].setdefault(e["id"], {"titulo": (e.get("titulo") or "")[:120], "faltam": [], "tentativas": []})
        ex = extraido(e)
        # INVESTIGAÇÃO IMEDIATA na fonte original (PNCP → arquivos oficiais / site institucional → PDF → texto compacto → extração → IA barata → reforço)
        if (not ex or not ex.get("completo")) and n_inv < limite_ia and not any(t.get("em", "")[:10] == hoje.isoformat() for t in (ex.get("tentativas") or [])):
            ex = investigar(e, _chamar, modelos_extracao); n_inv += 1
        elif not ex:
            ex = investigar(e, lambda *a, **k: {"status": "adiado"}, [], rede=False)      # sem rede/IA: semente + conhecimento do regramento, já
            resumo["ia_itens"] += sum(1 for t in ex.get("tentativas", []) if t.get("em", "")[:10] == hoje.isoformat())
        faltam = itens_faltantes(e); f["faltam"] = faltam
        f["tentativas"] = ex.get("tentativas") or f.get("tentativas") or []
        f["itens_ia"] = {k: v for k, v in (ex.get("itens") or {}).items() if "IA" in str((ex.get("fontes_itens") or {}).get(k, ""))}
        f["itens"] = ex.get("itens") or {}; f["fontes_itens"] = ex.get("fontes_itens") or {}
        f["fonte_original"] = {"site_institucional": ex.get("site_institucional"), "fontes": ex.get("fontes"), "kb": ex.get("kb_compacto"), "erros": (ex.get("erros") or [])[:4]}
        f["regras"] = ex.get("regras"); f["requisitos"] = ex.get("requisitos"); f["pontuacao_texto"] = ex.get("pontuacao_texto")
        if ex.get("pontuacao"): f["criterios_pontuacao"] = ex["pontuacao"]
        if ex.get("documentos_exigidos"): f["documentos_exigidos_ia"] = ex["documentos_exigidos"]
        if ex.get("anexos"): f["anexos"] = ex["anexos"]
        # o edital passa a ter os documentos exigidos conhecidos (alimenta aderência e checklist)
        if f.get("documentos_exigidos_ia"):
            e.setdefault("detalhes", {})["documentos_exigidos"] = f["documentos_exigidos_ia"]
        if f.get("anexos"):
            e.setdefault("detalhes", {})["anexos"] = f["anexos"]
        # enquadramento por associação (piso determinístico + IA forte para os melhores)
        for a in assoc:
            ad = aderencia(a, e)
            pasta = ROOT / "dados/associacoes" / a["_pasta"] / "farol"; pasta.mkdir(parents=True, exist_ok=True)
            fp = pasta / f"{e['id']}.json"
            par = load_json(fp) if fp.exists() else {}
            par.update({"edital_id": e["id"], "associacao": a.get("id") or a["_pasta"], "titulo": e.get("titulo"), "atualizado_em": now_iso(),
                        "aderencia_deterministica": ad, "checklist": checklist(a, e), "cronograma": cronograma_reverso(e, hoje),
                        "simulador": simulador_pontuacao(a, e, f.get("criterios_pontuacao"))})
            if ad["elegivel"] and ad["nota"] >= 45 and not par.get("ia") and n_ia < limite_ia and e.get("situacao_inscricao") == "aberta":
                r = _chamar(modelo_forte, prompt_enquadramento(a, e, f.get("itens") or {}, f.get("criterios_pontuacao") or []), 1600, web=False, tarefa=f"edital:{e['id']}"); n_ia += 1
                if r.get("status") == "respondeu":
                    par["ia"] = {k: r.get(k) for k in ("aderencia", "chances", "pontuacao_estimada", "lentes", "decisao", "para_subir", "riscos")}
                    par["ia"]["modelo"] = modelo_forte; par["ia"]["em"] = now_iso(); par["aderencia"] = r.get("aderencia"); resumo["ia_enquadramento"] += 1
                else:
                    par["ia_status"] = r.get("status")
            par.setdefault("aderencia", ad["nota"])
            write_json(fp, par)
    # ESQUELETO por associação: só os editais que passam no filtro geográfico
    for a in assoc:
        dec_p = ROOT / "dados/associacoes" / a["_pasta"] / "decisoes_editais.json"
        dec = load_json(dec_p) if dec_p.exists() else {}
        arq_p = ROOT / "dados/editais/arquivados.json"; arquivados = load_json(arq_p) if arq_p.exists() else {}
        inc_p = ROOT / "dados/associacoes" / a["_pasta"] / "incluidos_editais.json"
        incluidos = set((load_json(inc_p).get("editais") or [])) if inc_p.exists() else set()
        geo = [e for e in abertos if e["id"] not in arquivados and (filtro_geografico(a, e) or e["id"] in incluidos) and dec.get(e["id"]) != "dispensado"]
        cand = [e for e in abertos if not filtro_geografico(a, e) and candidato_aprovacao(a, e)]
        lista = []
        for e in geo:
            fp = ROOT / "dados/associacoes" / a["_pasta"] / "farol" / f"{e['id']}.json"
            par = load_json(fp) if fp.exists() else {}
            ad = par.get("aderencia_deterministica") or aderencia(a, e)
            faltam = itens_faltantes(e); comp = complementos(e); f = est["fila"].get(e["id"], {})
            anexos = (e.get("detalhes") or {}).get("anexos") or e.get("anexos") or []
            lista.append({"id": e["id"], "titulo": e.get("titulo"), "area": e.get("area"), "uf": e.get("uf"), "situacao": e.get("situacao_inscricao"),
                          "inicio": e.get("inicio"), "fim": e.get("fim"), "url": e.get("url"), "fonte": e.get("fonte_nome"),
                          "nota": (par.get("ia") or {}).get("aderencia") or ad["nota"], "farol": ad["farol"], "por": ad["por"], "para_subir": ad["para_subir"],
                          "ia": par.get("ia"), "ia_status": par.get("ia_status"),
                          "faltam": faltam, "complementados": sorted(comp), "itens_ia": sorted((f.get("itens_ia") or {}).keys()),
                          "fila": {"tentativas": len(f.get("tentativas") or []), "status": ((f.get("tentativas") or [{}])[-1]).get("status")},
                          "cronograma": par.get("cronograma") or cronograma_reverso(e, hoje), "simulador": par.get("simulador") or simulador_pontuacao(a, e, f.get("criterios_pontuacao")),
                          "modelos_documentos": [x for x in anexos if isinstance(x, dict)][:8],
                          "itens": [{"item": i, "valor": (f.get("itens") or {}).get(i) or (comp.get(i) or {}).get("valor"), "fonte": (f.get("fontes_itens") or {}).get(i) or ("complemento manual" if i in comp else None),
                                     "dispensavel": ((extraido(e) or {}).get("dispensaveis") or {}).get(i)}
                                    for i in ("Objeto", "Prazo de inscrição", "Resultado", "Prazo de recurso", "Valor", "Órgão / financiador", "Território", "Esfera", "Requisitos", "Anexos", "Destinação", "Área de atuação")],
                          "regras": f.get("regras"), "requisitos": f.get("requisitos"), "pontuacao": f.get("criterios_pontuacao"), "pontuacao_texto": f.get("pontuacao_texto"),
                          "fonte_original": f.get("fonte_original"),
                          "documentos_exigidos": f.get("documentos_exigidos_ia") or [],
                          "documentos_submissao": _documentos_submissao(e, f),
                          "para_inscricao": _para_inscricao(a, f.get("documentos_exigidos_ia") or [], faltam),
                          "relatorio_ia": (extraido(e) or {}).get("relatorio"), "mini_parecer": (extraido(e) or {}).get("mini_parecer"),
                          "parametros": (lambda pr: {"tipo_recurso": pr.get("tipo_recurso"), "competitivo": pr.get("competitivo"), "rito": pr.get("rito"),
                                                     "pontuacao": pr.get("pontuacao"), "valores": pr.get("valores"), "preditiva": pr.get("preditiva"),
                                                     "historico": pr.get("historico_5_anos")} if pr else None)(parametros_da_fonte(e)),
                          "historico_5_anos": (extraido(e) or {}).get("historico_5_anos"), "documentos_pdf": (extraido(e) or {}).get("documentos_pdf"), "condicoes": (extraido(e) or {}).get("condicoes"),
                          "decisao": dec.get(e["id"]), "pagina_divulgacao": (extraido(e) or {}).get("pagina_divulgacao") or (extraido(e) or {}).get("site_institucional"),
                          "quadro_ia": _quadro_ia(extraido(e) or {}, par), "valor": (f.get("itens") or {}).get("Valor") or e.get("valor_texto"), "orgao": (f.get("itens") or {}).get("Órgão / financiador") or e.get("fonte_nome"),
                          "subir": f"https://github.com/amcjardimamerica-arch/Eldorado/new/main/dados/editais/complementos/{e['id']}?filename=complemento.md&value="
                                   + __import__("urllib.parse").parse.quote("\n".join(f"- {i}: " for i in faltam) or "- (nada falta)")})
        lista.sort(key=lambda x: (x["situacao"] != "aberta", -x["nota"]))
        write_json(ROOT / "dados/associacoes" / a["_pasta"] / "enquadramento.json",
                   {"associacao": a.get("id"), "nome": a.get("nome"), "territorios": a.get("territorios"), "areas": a.get("areas"), "gerado_em": now_iso(),
                    "editais_abertos_total": len(abertos), "compativeis_geograficamente": len(geo), "abrangencia": abrangencia(a),
                    "candidatos_aprovacao": [{"id": e["id"], "titulo": e.get("titulo"), "cidade": _cidade_de(e), "uf": e.get("uf"), "area": e.get("area"), "fim": e.get("fim"), "url": e.get("url"), "situacao": e.get("situacao_inscricao")} for e in cand[:60]],
                    "por_nivel": {"nacional": sum(1 for e in geo if not e.get("uf")), "estadual": sum(1 for e in geo if e.get("uf") and (e.get("nivel") in ("estadual", "regional") or not _cidade_de(e))), "municipal": sum(1 for e in geo if e.get("uf") and _cidade_de(e) and e.get("nivel") not in ("estadual", "regional"))},
                    "filtro": "atuação geográfica do edital ⊆ atuação da associação (UF ou nacional)", "editais": lista})
    est["execucoes"] = (est.get("execucoes") or [])[-30:] + [resumo]
    write_json(ESTADO, est)
    return resumo


# ───────────────────────── operação por AGENTE CLAUDE (sem API) ─────────────────────────
PACOTE = ROOT / "estado/pacote_agente.md"
RESPOSTAS = ROOT / "dados/editais/respostas_agente"


def historico_5_anos(nome: str) -> dict:
    """Recorrência do recurso nos últimos 5 anos no acervo (por financiador/título)."""
    from .banco import conectar
    import re as _re
    toks = [x for x in _re.findall(r"[a-zà-ú]{5,}", (nome or "").lower()) if x not in ("edital", "programa", "chamamento", "público", "publico", "seleção", "selecao")][:3]
    if not toks:
        return {"ocorrencias": 0}
    try:
        con = conectar()
        rows = con.execute("SELECT data_publicacao, titulo, financiador, url FROM historico WHERE data_publicacao >= date('now','-5 years') ORDER BY data_publicacao DESC LIMIT 20000").fetchall()
    except Exception:
        return {"ocorrencias": 0, "erro": "banco indisponível"}
    hits = [r for r in rows if sum(1 for t in toks if t in ((r[1] or "") + " " + (r[2] or "")).lower()) >= min(2, len(toks))]
    por_ano = {}
    for r in hits:
        por_ano[(r[0] or "")[:4]] = por_ano.get((r[0] or "")[:4], 0) + 1
    return {"ocorrencias": len(hits), "por_ano": dict(sorted(por_ano.items())), "ultimas": [{"data": r[0], "titulo": (r[1] or "")[:100], "url": r[3]} for r in hits[:5]], "termos": toks}


FILA_VERIF = ROOT / "estado/fila_verificacao.json"


def _mapa_maiores() -> dict:
    arq = ROOT / "config/municipios_maiores.json"
    m = load_json(arq).get("maiores", {}) if arq.exists() else {}
    import unicodedata
    def n(s): return re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode())
    return {uf: {n(c): c for c in cid} for uf, cid in m.items()}


def classificar_geografia(e: dict, maiores: dict) -> dict:
    """Regra do titular (07/09): (a) oportunidade sem UF/região definida é NACIONAL,
    sem restrição geográfica — prioridade máxima; (b) com UF, só entra se a cidade
    for uma das 50 maiores do estado (ou se for estadual/regional, sem cidade);
    (c) cidade fora das 50 maiores fica em ROSA para aprovação manual."""
    import unicodedata
    def n(s): return re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", (s or "").lower()).encode("ascii", "ignore").decode())
    uf = e.get("uf")
    if not uf or e.get("abrangencia") == "nacional" or e.get("nivel") == "federal":
        return {"escopo": "nacional", "prioridade_geo": 0, "motivo": "sem restrição geográfica declarada — vale para todo o Brasil"}
    cidade = _cidade_de(e)
    if not cidade:
        return {"escopo": "estadual", "prioridade_geo": 1, "uf": uf, "motivo": f"abrangência estadual em {uf} (sem cidade identificada)"}
    lista = maiores.get(uf, {})
    chave = n(cidade)
    achou = next((v for k, v in lista.items() if k == chave or (len(chave) > 5 and (chave in k or k in chave))), None)
    if achou:
        return {"escopo": "municipal", "prioridade_geo": 2, "uf": uf, "cidade": achou, "entre_50_maiores": True,
                "motivo": f"{achou}/{uf} está entre as 50 maiores do estado"}
    return {"escopo": "municipal_fora", "prioridade_geo": 9, "uf": uf, "cidade": cidade, "entre_50_maiores": False,
            "motivo": f"{cidade}/{uf} não está entre as 50 maiores do estado — fica em rosa para aprovação manual"}


def fila_verificacao() -> dict:
    """Todo edital aberto/possível cujas informações NÃO estão completas: o que falta,
    o link oficial para validação e a prioridade. É esta fila que a IA de domingo
    executa — e que a varredura imediata percorre."""
    from .fonte_edital import EXTRAIDOS
    VETOR_RX = re.compile(r"pncp\.gov\.br|queridodiario|in\.gov\.br|diariooficial|portaldecompraspublicas|licitamaisbrasil", re.I)
    dados = load_json(ROOT / "docs/dashboard-dados.json")
    universo = list(editais_abertos(dados))
    ab = ROOT / "docs/dados/abertas.json"
    if ab.exists():
        try:
            from .compacto import expandir
            vistos = {e["id"] for e in universo}
            universo += [{**o, "situacao_inscricao": o.get("situacao") or "possivel"} for o in expandir(load_json(ab)) if o.get("id") not in vistos]
        except Exception:
            pass
    arq = load_json(ROOT / "dados/editais/arquivados.json") if (ROOT / "dados/editais/arquivados.json").exists() else {}
    itens = []
    edicoes_brutas = 0
    reprovados_objeto: list = []
    maiores = _mapa_maiores()
    fora_das_50 = []
    for e in universo:
        if e["id"] in arq:
            continue
        # edição inteira de diário sem ato identificado: fica para a extração de edições (fase 2), não para a IA
        if re.match(r"Di[áa]rio Oficial de .+\d{4}-\d{2}-\d{2}", e.get("titulo") or "") and not (e.get("objeto") or e.get("fim")):
            edicoes_brutas += 1; continue
        # filtro de objeto (src/inconformidade.py): o que não é chamada aberta de fomento sai da fila
        from .inconformidade import avaliar as _avaliar_objeto
        _av = _avaliar_objeto(f"{e.get('titulo') or ''} {e.get('objeto') or ''}")
        if not _av["ok"]:
            reprovados_objeto.append({"id": e["id"], "titulo": (e.get("titulo") or "")[:110], "familia": _av["familia"], "motivo": _av["motivo"]})
            continue
        geo = classificar_geografia(e, maiores)
        if geo["escopo"] == "municipal_fora":
            fora_das_50.append({"id": e["id"], "titulo": (e.get("titulo") or "")[:120], "uf": e.get("uf"), "cidade": geo.get("cidade"),
                                "motivo": geo["motivo"], "url": e.get("url")})
            continue                                   # depuração: sai da fila; volta em rosa quando o titular aprovar a cidade
        ex = load_json(EXTRAIDOS / f"{e['id']}.json") if (EXTRAIDOS / f"{e['id']}.json").exists() else {}
        faltam = ex.get("faltam") if ex else None
        ciclo = e.get("ciclo") or {}
        sem_prazo = not (e.get("fim") or ((ciclo.get("inscricao") or {}).get("fim")))
        completo = bool(ex.get("completo"))
        if completo and not sem_prazo:
            continue
        oficial = ex.get("pagina_divulgacao") or ex.get("site_institucional")
        if not oficial and e.get("url") and not VETOR_RX.search(e["url"]):
            oficial = e["url"]
        motivo = ("sem prazo de inscrição confirmado" if sem_prazo else "informações incompletas")
        # prioridade: nacionais (sem restrição geográfica) primeiro, depois Goiás, depois os demais
        base_prio = 0 if geo["escopo"] == "nacional" else (0 if e.get("uf") == "GO" else 2)
        prio = base_prio + (0 if sem_prazo else 1)
        itens.append({"id": e["id"], "titulo": (e.get("titulo") or "")[:140], "uf": e.get("uf"), "area": e.get("area"),
                      "fonte": e.get("fonte_nome") or e.get("orgao"), "situacao": e.get("situacao_inscricao") or e.get("situacao"),
                      "sem_prazo": sem_prazo, "faltam": faltam if faltam is not None else list(ITENS),
                      "link_oficial": oficial, "link_anuncio": e.get("url"),
                      "anuncio_e_vetor": bool(e.get("url") and VETOR_RX.search(e["url"])),
                      "motivo": motivo, "prioridade": prio, "ja_investigado": bool(ex),
                      "escopo": geo["escopo"], "cidade": geo.get("cidade"), "geo_motivo": geo["motivo"]})
    # MODO por regra do titular: Goiás e nacionais = automação completa (12 itens, parecer, selo);
    # demais estados = verificação LEVE: objeto, início e fim das inscrições e o link oficial do edital, para avaliação manual
    ITENS_LEVES = ["Objeto", "Início das inscrições", "Prazo de inscrição", "Página oficial do edital"]
    for x in itens:
        x["modo"] = "completo" if (x["escopo"] == "nacional" or x.get("uf") == "GO") else "leve"
        if x["modo"] == "leve":
            x["faltam"] = [i for i in ITENS_LEVES if i not in (("Objeto",) if not x["sem_prazo"] else ())]
            x["instrucao"] = "verificação leve: confirmar objeto, prazo de inscrição (início/fim) e a página oficial onde o edital está; o restante fica para avaliação manual do titular"
        else:
            x["instrucao"] = "automação completa: 12 itens, requisitos, documentos, pontuação, parecer e selo"
    itens.sort(key=lambda x: (x["prioridade"], -len(x["faltam"] or []), str(x.get("uf") or "")))
    # MARCAÇÃO persistente: cada edital sem prazo final fica marcado, com data e contagem de vezes que a IA o viu
    marc_p = ROOT / "dados/editais/marcacoes_ia.json"
    marc = load_json(marc_p) if marc_p.exists() else {}
    vivos = set()
    for x in itens:
        if not x["sem_prazo"] and x["ja_investigado"]:
            continue
        vivos.add(x["id"])
        m = marc.get(x["id"]) or {"desde": now_iso()[:10], "vezes_vistas": 0}
        m.update({"titulo": x["titulo"], "uf": x["uf"], "modo": x["modo"], "motivo": x["motivo"], "faltam": x["faltam"],
                  "link_oficial": x["link_oficial"], "link_anuncio": x["link_anuncio"], "ultima_marcacao": now_iso()[:10]})
        marc[x["id"]] = m
    for k in list(marc):
        if k not in vivos:
            marc[k]["resolvido_em"] = marc[k].get("resolvido_em") or now_iso()[:10]
    write_json(marc_p, marc)
    MINIMAS = ["Objeto", "Prazo de inscrição", "Página oficial do edital"]
    for x in itens:
        ex = load_json(EXTRAIDOS / f"{x['id']}.json") if (EXTRAIDOS / f"{x['id']}.json").exists() else {}
        it = ex.get("itens") or {}
        tem = {"Objeto": bool(it.get("Objeto")), "Prazo de inscrição": bool(it.get("Prazo de inscrição")) or not x["sem_prazo"],
               "Página oficial do edital": bool(ex.get("pagina_divulgacao") or x.get("link_oficial"))}
        x["minimas"] = {"exigidas": MINIMAS, "tem": [k for k, v in tem.items() if v], "faltam": [k for k, v in tem.items() if not v],
                        "completa": all(tem.values())}
        x["selo_validacao"] = "validada" if all(tem.values()) else "nao_verificada"
    res = {"gerado_em": now_iso(), "total": len(itens),
           "selos": {"validadas": sum(1 for x in itens if x.get("selo_validacao") == "validada"),
                     "nao_verificadas": sum(1 for x in itens if x.get("selo_validacao") != "validada"),
                     "regra": "VALIDADA (verde) exige objeto + prazo de inscrição + site oficial que divulga; sem qualquer um deles o selo é NÃO VERIFICADA (amarelo) e o item entra na verificação semanal da IA externa"},
           "informacoes_minimas": {"regra": "toda oportunidade precisa de OBJETO, PRAZO DE INSCRIÇÃO e PÁGINA OFICIAL DO EDITAL (site do órgão/patrocinador, nunca o vetor onde foi encontrada)",
                                   "completas": sum(1 for x in itens if x["minimas"]["completa"]),
                                   "incompletas": sum(1 for x in itens if not x["minimas"]["completa"]),
                                   "falta_objeto": sum(1 for x in itens if "Objeto" in x["minimas"]["faltam"]),
                                   "falta_prazo": sum(1 for x in itens if "Prazo de inscrição" in x["minimas"]["faltam"]),
                                   "falta_pagina": sum(1 for x in itens if "Página oficial do edital" in x["minimas"]["faltam"])}, "sem_prazo": sum(1 for x in itens if x["sem_prazo"]),
           "goias_ou_nacional": sum(1 for x in itens if x["prioridade"] == 0),
           "nunca_investigados": sum(1 for x in itens if not x["ja_investigado"]),
           "edicoes_de_diario_sem_ato": edicoes_brutas,
           "por_uf": {u: sum(1 for x in itens if (x.get("uf") or "BR") == u) for u in sorted({(x.get("uf") or "BR") for x in itens})},
           "reprovados_por_objeto": {"total": len(reprovados_objeto), "por_familia": {k: sum(1 for x in reprovados_objeto if x["familia"] == k) for k in sorted({x["familia"] for x in reprovados_objeto})},
                                     "itens": reprovados_objeto[:300],
                                     "regra": "filtro de objeto (inconformidade.py): não é chamada aberta que repasse recurso a entidade — sai da fila e não vira alerta"},
           "fora_das_50_maiores": {"total": len(fora_das_50), "itens": fora_das_50[:400],
                                   "regra": "excluídas da fila por não estarem entre as 50 maiores cidades do estado; voltam em ROSA quando o titular aprovar a cidade"},
           "escopo": {k: sum(1 for x in itens if x["escopo"] == k) for k in ("nacional", "estadual", "municipal")},
           "modo": {"completo": sum(1 for x in itens if x["modo"] == "completo"), "leve": sum(1 for x in itens if x["modo"] == "leve")},
           "marcados_para_ia": len(vivos),
           "regra": "a IA de domingo executa esta fila na ordem; a varredura imediata percorre os mesmos itens e emite parecer de cada um",
           "itens": itens[:2000]}
    write_json(FILA_VERIF, res)
    write_json(ROOT / "docs/dados/fila_verificacao.json", res)
    return {k: v for k, v in res.items() if k != "itens"}


def pacote(limite: int = 6) -> dict:
    """Monta um pacote compacto com os editais pendentes (texto guardado, itens
    que faltam, associação) para um agente Claude — este chat ou o Claude Code
    na conta do titular — analisar SEM API: o agente lê o pacote, escreve um JSON
    por edital em dados/editais/respostas_agente/<id>.json e roda 'ingerir'."""
    from .fonte_edital import texto_guardado
    dados = load_json(ROOT / "docs/dashboard-dados.json")
    assoc = associacoes()
    an_p = ROOT / "dados/editais/analises.json"; analisados = load_json(an_p) if an_p.exists() else {}
    # universo: tudo o que está em Oportunidades Abertas › Em andamento — núcleo + base ampla — com atuação nacional, GO ou município de GO
    universo = list(editais_abertos(dados))
    ab = ROOT / "docs/dados/abertas.json"
    if ab.exists():
        try:
            from .compacto import expandir
            vistos = {e["id"] for e in universo}
            for o in expandir(load_json(ab)):
                if o.get("id") in vistos: continue
                if o.get("uf") == "GO" or (not o.get("uf") and o.get("abrangencia") == "nacional"):
                    universo.append({**o, "situacao_inscricao": o.get("situacao") or "possivel", "detalhes": {}})
        except Exception:
            pass
    pend = []
    edicoes_brutas = 0
    arq_p = ROOT / "dados/editais/arquivados.json"; arquivados = load_json(arq_p) if arq_p.exists() else {}
    for e in universo:
        if e["id"] in arquivados:
            continue                                          # exclusão manual em Oportunidades Abertas: sai do sistema inteiro
        if e["id"] in analisados and (analisados[e["id"]].get("completo") or analisados[e["id"]].get("selo") == "inconformidade"):
            continue
        # edições INTEIRAS de diário (Querido Diário) sem edital identificado não são analisáveis: só o título da edição existe.
        # Elas ficam na Bússola e entram no Enquadramento quando a extração de edições (fase 2) identificar o ato.
        if re.match(r"Di[áa]rio Oficial de .+\d{4}-\d{2}-\d{2}", e.get("titulo") or "") and not (e.get("objeto") or e.get("fim") or texto_guardado(e)):
            edicoes_brutas += 1; continue
        # regra do titular: Brasil inteiro (nacionais) e Goiás entram na análise, independentemente da associação
        if e.get("uf") and e.get("uf") != "GO":
            continue
        ex = extraido(e)
        if ex.get("completo") and any((ROOT / "dados/associacoes" / a["_pasta"] / "farol" / f"{e['id']}.json").exists() and load_json(ROOT / "dados/associacoes" / a["_pasta"] / "farol" / f"{e['id']}.json").get("ia") for a in assoc):
            continue
        pend.append((e, ex))                                  # regra: Brasil inteiro (nacionais) + Goiás; sem filtro por associação
    pend.sort(key=lambda x: (x[0].get("situacao_inscricao") != "aberta", x[0].get("uf") != "GO", -(len(x[1].get("itens") or {})), str(x[0].get("fim") or "9")))
    resumo_universo = {"universo": len(universo), "pendentes": len(pend), "ja_analisados": sum(1 for e in universo if e["id"] in analisados), "edicoes_de_diario_sem_ato": edicoes_brutas}
    L = ["# Pacote para o agente Claude — Enquadramento (Farol de Alexandria)\n",
         "Regras: (1) use SÓ o texto abaixo e o conhecimento do sistema; busque na internet apenas se o texto não trouxer o item; (2) nunca invente — sem base, null; "
         "(3) PNCP e diários são vetores: a fonte é o site do órgão publicador — informe-o em `pagina_divulgacao`; (4) escreva UM arquivo JSON por edital em "
         "`dados/editais/respostas_agente/<id>.json` com o formato indicado; depois rode `python -m src.enquadramento ingerir`.\n",
         "Formato: {\"itens\": {<item>: <valor|null>}, \"regras\": <texto>, \"requisitos\": [..], \"pontuacao\": [{\"criterio\":..,\"peso\":..}], \"documentos_exigidos\": [..], "
         "\"anexos\": [{\"nome\":..,\"url\":..}], \"pagina_divulgacao\": <url do órgão|null>, \"mini_parecer\": <3-5 frases>, "
         "\"enquadramento\": {<id_associacao>: {\"aderencia\": 0-100, \"chances\": 0-100, \"pontuacao_estimada\": <texto>, \"decisao\": <texto>, \"para_subir\": [..], \"riscos\": [..]}}, "
         "\"conformidade\": true|false (true = aproveitável em Goiás/Brasil pelas associações; false = sem aproveitamento → vai para Arquivados), \"motivo_conformidade\": <frase>}\n",
         f"Associações: " + "; ".join(f"{a.get('id')} — {a.get('nome')} · áreas {', '.join(a.get('areas') or [])} · atuação {', '.join(a.get('territorios') or [])} · {a.get('anos_existencia')} anos" for a in assoc) + "\n"]
    marc_p = ROOT / "dados/editais/marcacoes_ia.json"; marc = load_json(marc_p) if marc_p.exists() else {}
    L.append("\nMARCAÇÕES: os editais abaixo marcados como LEVE pertencem a outros estados — devolva SÓ objeto, início/fim das inscrições e a página oficial "
             "(`itens` com essas chaves e `pagina_divulgacao`); não faça parecer nem enquadramento. Os COMPLETOS (Goiás e nacionais) recebem tudo.\n")
    for e, ex in pend[:limite]:
        texto = texto_guardado(e)
        mm = marc.get(e["id"]) or {}
        if mm:
            mm["vezes_vistas"] = mm.get("vezes_vistas", 0) + 1; marc[e["id"]] = mm
        modo = "completo" if (e.get("uf") == "GO" or not e.get("uf") or e.get("abrangencia") == "nacional" or e.get("nivel") == "federal") else "leve"
        L.append(f"\n---\n## {e['id']} — {e.get('titulo')}\n")
        L.append(f"MODO: {modo.upper()}" + (f" · marcado desde {mm.get('desde')} · visto pela IA {mm.get('vezes_vistas')}× · motivo: {mm.get('motivo')}" if mm else "") + "\n")
        L.append(f"Fonte (vetor): {e.get('fonte_nome')} · UF {e.get('uf') or 'BR'} · nível {e.get('nivel')} · situação {e.get('situacao_inscricao')} · fim {e.get('fim')}\n")
        L.append("Itens já obtidos: " + (", ".join(f"{k}: {str(v)[:80]}" for k, v in (ex.get('itens') or {}).items()) or "nenhum") + "\n")
        L.append("Itens que FALTAM: " + ", ".join(ex.get("faltam") or list(ITENS)) + "\n")
        L.append(f"Anúncio: {e.get('url')}\nSite institucional conhecido: {ex.get('site_institucional') or 'não localizado'}\n")
        L.append("Texto do edital (compacto):\n```\n" + (texto[:12000] if texto else "(sem texto — localizar o edital no site do órgão)") + "\n```\n")
    PACOTE.write_text("\n".join(L), encoding="utf-8")
    if marc:
        write_json(marc_p, marc)
    return {"pacote": str(PACOTE.relative_to(ROOT)), "editais": len(pend[:limite]), "pendentes_total": len(pend), **resumo_universo}


def ingerir() -> dict:
    """Lê as respostas do agente e grava como se a IA da API tivesse respondido:
    itens/regras/documentos no extraído do edital, parecer por associação no Farol."""
    from .fonte_edital import EXTRAIDOS
    RESPOSTAS.mkdir(parents=True, exist_ok=True)
    n = 0
    for arq in sorted(RESPOSTAS.glob("*.json")):
        try:
            r = load_json(arq)
        except Exception:
            continue
        eid = arq.stem
        ex_p = EXTRAIDOS / f"{eid}.json"; ex = load_json(ex_p) if ex_p.exists() else {"edital_id": eid, "tentativas": [], "itens": {}, "fontes_itens": {}}
        itens = dict(ex.get("itens") or {}); fontes = dict(ex.get("fontes_itens") or {}); novos = 0
        disp = dict(ex.get("dispensaveis") or {})
        for k, v in (r.get("itens") or {}).items():
            if isinstance(v, dict) and v.get("dispensavel"):
                disp[k] = v.get("motivo") or "dispensado pela análise"; itens.pop(k, None); novos += 1; continue
            if v in (None, ""):
                continue
            anterior = (fontes.get(k) or "")
            # a leitura do agente prevalece sobre a semente do cadastro do motor
            if not itens.get(k) or anterior.startswith("cadastro do edital") or anterior.startswith("PNCP"):
                itens[k] = v; fontes[k] = "agente Claude (conta do titular) sobre o texto do edital"; novos += 1
        for k, m in (r.get("dispensaveis") or {}).items():
            disp[k] = m or "dispensado pela análise"
        for k in ("regras", "requisitos", "pontuacao", "documentos_exigidos", "anexos", "pagina_divulgacao", "mini_parecer", "historico_5_anos", "documentos_pdf", "condicoes"):
            if r.get(k) not in (None, "", []): ex[k] = r[k]
        ex["dispensaveis"] = disp
        alvo = list(ITENS); faltam = [i for i in alvo if not itens.get(i) and i not in disp]
        ex["tentativas"] = (ex.get("tentativas") or []) + [{"em": now_iso(), "modelo": "agente-claude", "status": "respondeu", "itens_obtidos": novos, "sinal": "verde" if novos else "amarelo"}]
        ex.update({"itens": itens, "fontes_itens": fontes, "faltam": faltam, "completo": not faltam, "atualizado_em": now_iso()})
        write_json(ex_p, ex)
        for aid, par in (r.get("enquadramento") or {}).items():
            for a in associacoes():
                if (a.get("id") or a["_pasta"]) == aid:
                    fp = ROOT / "dados/associacoes" / a["_pasta"] / "farol" / f"{eid}.json"; fp.parent.mkdir(parents=True, exist_ok=True)
                    cur = load_json(fp) if fp.exists() else {"edital_id": eid, "associacao": aid}
                    cur["ia"] = {**par, "modelo": "agente-claude (conta do titular)", "em": now_iso()}; cur["aderencia"] = par.get("aderencia", cur.get("aderencia"))
                    write_json(fp, cur)
        # SELO DE ANÁLISE: conformidade (aproveitável em Goiás/Brasil) ou inconformidade (sem aproveitamento) → arquivado
        an_p = ROOT / "dados/editais/analises.json"; an = load_json(an_p) if an_p.exists() else {}
        conf = r.get("conformidade")
        if conf is None:
            enq = r.get("enquadramento") or {}
            conf = any((v or {}).get("aderencia", 0) >= 45 for v in enq.values()) if enq else None
        # 14 verificações: 12 itens (obtidos ou dispensados com motivo) + requisitos/condições compreendidos + documentos de inscrição conhecidos
        analise_completa = (not faltam) and bool(ex.get("requisitos") or ex.get("regras")) and bool(ex.get("documentos_exigidos"))
        if conf and not analise_completa:
            selo = "analise_incompleta"           # só há Conformidade com análise completa
        else:
            selo = ("conformidade" if conf else "inconformidade") if conf is not None else "analisado"
        an[eid] = {"selo": selo, "em": now_iso(), "motivo": r.get("motivo_conformidade") or (r.get("mini_parecer") or "")[:200],
                   "completo": analise_completa, "verificacoes": {"itens_12": not faltam, "dispensados": sorted(disp), "requisitos_condicoes": bool(ex.get("requisitos") or ex.get("regras")), "documentos": bool(ex.get("documentos_exigidos"))},
                   "por": "agente Claude (conta do titular)"}
        write_json(an_p, an)
        arq.rename(arq.with_suffix(".json.ingerido")); n += 1
    return {"ingeridos": n}


def ingerir_navegador() -> dict:
    """Incorpora o JSON simples produzido pela extensão do Claude no navegador:
    {"<id>": {"objeto","inicio","fim","pagina_oficial","observacao"}}.
    Só grava o que veio da fonte oficial — descarta vetores e veículos."""
    from .fonte_edital import EXTRAIDOS
    VET = re.compile(r"pncp\.gov|queridodiario|in\.gov\.br|diariooficial|observatorio3setor|captadores\.org|bussolasocial|prosas\.com", re.I)
    pasta = ROOT / "dados/editais/coleta_navegador"
    if not pasta.exists():
        return {"ingeridos": 0, "nota": "pasta dados/editais/coleta_navegador não existe"}
    n, recusados = 0, []
    for arq in sorted(pasta.glob("*.json")):
        try:
            dados = load_json(arq)
        except Exception:
            continue
        for eid, v in (dados.items() if isinstance(dados, dict) else []):
            if not isinstance(v, dict):
                continue
            pag = (v.get("pagina_oficial") or "").strip()
            if pag and VET.search(pag) and not re.search(r"pncp\.gov[^ ]*/arquivos/", pag, re.I):
                recusados.append({"id": eid, "motivo": "página informada é vetor/veículo, não a fonte oficial", "url": pag}); pag = ""
            fp = EXTRAIDOS / f"{eid}.json"
            reg = load_json(fp) if fp.exists() else {"edital_id": eid, "tentativas": [], "itens": {}, "fontes_itens": {}}
            itens = dict(reg.get("itens") or {}); fontes = dict(reg.get("fontes_itens") or {})
            if v.get("objeto"): itens["Objeto"] = str(v["objeto"])[:400]; fontes["Objeto"] = "coleta pelo navegador (titular) — página oficial"
            if v.get("fim"): itens["Prazo de inscrição"] = str(v["fim"])[:40]; fontes["Prazo de inscrição"] = "coleta pelo navegador (titular) — edital"
            if v.get("inicio"): itens["Início das inscrições"] = str(v["inicio"])[:40]
            if pag: reg["pagina_divulgacao"] = pag
            if v.get("observacao"): reg.setdefault("observacoes", []).append({"em": now_iso()[:10], "texto": str(v["observacao"])[:300]})
            faltam = [i for i in ITENS if not itens.get(i)]
            reg.update({"itens": itens, "fontes_itens": fontes, "faltam": faltam, "completo": not faltam, "atualizado_em": now_iso()})
            reg["tentativas"] = (reg.get("tentativas") or []) + [{"em": now_iso(), "modelo": "navegador-titular", "status": "respondeu",
                                                                  "itens_obtidos": sum(1 for k in ("objeto", "fim", "inicio") if v.get(k)), "sinal": "verde"}]
            write_json(fp, reg); n += 1
        arq.rename(arq.with_suffix(".json.ingerido"))
    return {"ingeridos": n, "recusados": recusados[:10]}


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "pacote":
        print(json.dumps(pacote(int(sys.argv[2]) if len(sys.argv) > 2 else 6), ensure_ascii=False, indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "fila":
        print(json.dumps(fila_verificacao(), ensure_ascii=False, indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "ingerir_navegador":
        print(json.dumps(ingerir_navegador(), ensure_ascii=False, indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "ingerir":
        print(json.dumps(ingerir(), ensure_ascii=False, indent=2))
    else:
        print(json.dumps(run(), ensure_ascii=False, indent=2))
