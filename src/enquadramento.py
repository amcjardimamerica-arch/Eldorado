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
        comp = complementos(e)
        return [i for i in (ex.get("faltam") or []) if i not in comp]
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


def _documentos_submissao(e: dict, f: dict) -> dict:
    """Tudo o que a inscrição exige: os documentos lidos do edital quando existem;
    senão o conjunto padrão de habilitação (Lei 13.019/2014, arts. 33-34 e
    Decreto 8.726/2016) até a IA extrair o rol do edital."""
    do_edital = list(f.get("documentos_exigidos_ia") or [])
    req = f.get("requisitos") or []
    if do_edital:
        return {"origem": "edital (extraído da fonte oficial)", "documentos": do_edital, "requisitos": req}
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
        geo = [e for e in abertos if filtro_geografico(a, e) and dec.get(e["id"]) != "dispensado"]
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
                          "itens": [{"item": i, "valor": (f.get("itens") or {}).get(i) or (comp.get(i) or {}).get("valor"), "fonte": (f.get("fontes_itens") or {}).get(i) or ("complemento manual" if i in comp else None)}
                                    for i in ("Objeto", "Prazo de inscrição", "Resultado", "Prazo de recurso", "Valor", "Órgão / financiador", "Território", "Esfera", "Requisitos", "Anexos", "Destinação", "Área de atuação")],
                          "regras": f.get("regras"), "requisitos": f.get("requisitos"), "pontuacao": f.get("criterios_pontuacao"), "pontuacao_texto": f.get("pontuacao_texto"),
                          "fonte_original": f.get("fonte_original"),
                          "documentos_exigidos": f.get("documentos_exigidos_ia") or [],
                          "documentos_submissao": _documentos_submissao(e, f),
                          "para_inscricao": _para_inscricao(a, f.get("documentos_exigidos_ia") or [], faltam),
                          "relatorio_ia": (extraido(e) or {}).get("relatorio"), "mini_parecer": (extraido(e) or {}).get("mini_parecer"),
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


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
