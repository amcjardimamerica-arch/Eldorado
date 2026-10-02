"""REGRA DOS LIVROS PARA OS MOTORES E O ESPIÃO (titular, 01/10).

MOTORES REGULARES (todos): cada oportunidade que um motor encontra é comparada com a Biblioteca.
  · já tem livro  → o livro RECEBE as informações básicas dos 12 itens do checklist (preenche o que faltava; atualiza o
                    que mudou), com a data e o motor de origem;
  · não tem livro → o livro é CRIADO (pelo repositório, no mesmo ciclo).
  Depois, o parâmetro LOCAIS DE BUSCA é recalculado: quantos livros, páginas e domínios a Biblioteca cobre e quantos
  livros cada motor criou ou atualizou no dia (docs/dados/locais_de_busca.json e o cabeçalho do catálogo).
PILOTO - ESPIÃO: busca o que NÃO está nos livros; cada achado novo vira um livro na hora (o que já existe só recebe a
  informação nova). Empresa encontrada vai ao ranking de empresas, na aba que se aplicar (Destinação Tributária e/ou
  Doação e patrocínio), marcada 'a verificar' até o Interceptador confirmar.
LÉXICO E RESTRIÇÕES EM CADA LIVRO (titular, 02/10): a cada ciclo, cada livro recebe o bloco `busca` — o léxico que busca
  a SUA oportunidade (termos, número do edital, município, consulta ao PNCP) e as restrições que se aplicam a ela (vetos,
  ato acessório = edição do livro, duplicata = junta, prazo = estado, território/região/especialidade = enquadramento).
  Achado de um livro é julgado pelas restrições DO livro; achado novo com veto (NÃO APLICA) não vira livro (fica registrado
  em `vetados_pelas_restricoes`). Território NÃO impede livro: edital de OSC de outro município é coletado pelo PNCP e ganha
  livro próprio, com o território anotado como enquadramento (src/regras_restricao.py).
SEMENTE DO PARECER DAS 238 (02/10): dados/oportunidades/livros_parecer_238.json — as oportunidades para OSC validadas no
  parecer entram como livros (ou atualizam o livro existente) no primeiro ciclo; idempotente.
Só dados — nenhum arquivo é anexado a um livro.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "biblioteca_alexandria/fontes/motores.json"
FLUXO = ROOT / "docs/dados/fluxo_oportunidades.json"
SEMENTE = ROOT / "dados/oportunidades/livros_parecer_238.json"
INDICE = ROOT / "estado/opressores_indice.json"
LOCAIS = ROOT / "docs/dados/locais_de_busca.json"
DOZE = ["Objeto", "Prazo de inscrição", "Resultado", "Prazo de recurso", "Valor", "Órgão / financiador", "Território", "Esfera",
        "Requisitos", "Anexos", "Destinação", "Área de atuação"]


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return padrao


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _valor(v) -> str:
    if isinstance(v, dict):
        v = v.get("v") or v.get("valor") or v.get("trecho") or ""
    return re.sub(r"\s+", " ", str(v or "")).strip()[:200]


def anotar_checklist(livro: dict, checklist: dict, origem: str, edicao: dict | None = None) -> int:
    """Leva ao livro as informações básicas dos 12 itens. Devolve quantos itens mudaram.
    02/10 (titular): HISTÓRICO DOS PARÂMETROS — cada mudança fica registrada na linha do tempo do livro (o que era, o que
    passou a ser, quando e por qual motor), e os parâmetros que a EDIÇÃO trouxe ficam gravados na própria edição."""
    lv = livro.setdefault("livro", {}); ck = lv.setdefault("checklist", {}); mud = 0
    mudancas = {}
    for item in DOZE:
        novo = _valor((checklist or {}).get(item))
        if not novo:
            continue
        atual = (ck.get(item) or {}).get("v")
        if atual != novo:
            mudancas[item] = {"antes": atual, "agora": novo} if atual else {"agora": novo}
            ck[item] = {"v": novo, "de": origem[:60], "em": date.today().isoformat()}; mud += 1
    params = {i: _valor((checklist or {}).get(i)) for i in DOZE if _valor((checklist or {}).get(i))}
    if edicao and params:                      # os parâmetros que ESTA edição trouxe, na própria edição
        ref = edicao.get("id"); tit = str(edicao.get("titulo") or "")[:120]
        for h in livro.get("historico") or []:
            if (ref and h.get("id") == ref) or (not ref and tit and str(h.get("titulo") or "")[:120] == tit):
                h["parametros"] = params; h["parametros_em"] = date.today().isoformat(); break
    if mudancas:                               # linha do tempo dos parâmetros (últimas 40 mudanças)
        hp = lv.setdefault("historico_parametros", [])
        hp.append({"em": date.today().isoformat(), "de": origem[:60], **({"edicao": str((edicao or {}).get("titulo") or "")[:120]} if edicao else {}),
                   "mudou": mudancas})
        lv["historico_parametros"] = hp[-40:]
    if mud:
        lv["checklist_itens"] = sum(1 for i in DOZE if (ck.get(i) or {}).get("v"))
        at = lv.setdefault("atualizacoes", [])
        at.append({"em": _agora(), "o_que": f"{mud} item(ns) do checklist atualizado(s) por {origem[:60]}"}); lv["atualizacoes"] = at[-8:]
    return mud


def _checklist_de(it: dict) -> dict:
    """Checklist básico de um achado que não veio com checklist pronto (ex.: Espião)."""
    return {"Objeto": it.get("objeto") or it.get("titulo"), "Prazo de inscrição": " a ".join(x for x in (it.get("inicio"), it.get("fim") or it.get("prazo")) if x),
            "Valor": it.get("valor"), "Órgão / financiador": it.get("orgao") or it.get("empresa"), "Território": it.get("uf"),
            "Anexos": it.get("url") or it.get("link_oficial"), "Área de atuação": it.get("area") or it.get("tema")}


def aplicar_motores() -> dict:
    """Todos os motores regulares: oportunidade com livro → o livro recebe o checklist; locais de busca recalculados."""
    C = _j(CAT, {}); ms = C.get("motores") or []
    por_id = {x.get("id"): x for x in ms}
    idx = (_j(INDICE, {}) or {}).get("indice") or {}
    F = _j(FLUXO, {})
    hoje = date.today().isoformat()
    atual, criado = Counter(), Counter()
    for uf, itens in (F.get("itens_por_uf") or {}).items():
        for it in itens:
            oid = (idx.get(it.get("id")) or {}).get("opressor")
            x = por_id.get(oid)
            if not x:
                continue
            origem = str(it.get("origem") or "motor")
            if "pncp" in origem.lower() or "pncp.gov.br" in str(it.get("url") or ""):
                from .livros_opressores import classificar as _cl
                _corrigir_territorio(x, {"uf": it.get("uf"), "municipio": it.get("municipio")}, _cl)   # RC-01: PNCP diz a UF
            if str(x.get("criado_em") or "") == hoje:
                criado[origem] += 1
            if anotar_checklist(x, it.get("checklist") or {}, origem, edicao={"id": it.get("id"), "titulo": it.get("titulo")}):
                atual[origem] += 1
    # 02/10: semente do parecer das 238 + léxico e restrições gravados em CADA livro
    try:
        C["semente_238"] = _aplicar_semente(C)
        ms = C.get("motores") or []
    except Exception as exc:  # noqa: BLE001 — a semente nunca derruba o ciclo dos livros
        C["semente_238"] = {"erro": str(exc)[:200]}
    try:
        from .regras_restricao import aplicar_aos_livros
        C["restricoes_dos_livros"] = aplicar_aos_livros(ms, hoje)
    except Exception as exc:  # noqa: BLE001
        C["restricoes_dos_livros"] = {"erro": str(exc)[:200]}
    hosts = {(urlsplit(str(x.get("pagina") or "")).hostname or "").lower().removeprefix("www.") for x in ms if x.get("pagina")}
    hosts.discard("")
    locais = {"em": _agora(), "regra": __doc__.split("PILOTO - ESPIÃO")[0].strip(),
              "livros": len(ms), "livros_com_pagina": sum(1 for x in ms if x.get("pagina")), "dominios_distintos": len(hosts),
              "por_geografia": dict(Counter(str(x.get("geo") or "—") for x in ms).most_common()),
              "hoje": {"livros_criados_por_motor": dict(criado.most_common()), "livros_atualizados_por_motor": dict(atual.most_common())}}
    C["locais_de_busca"] = {k: locais[k] for k in ("em", "livros", "livros_com_pagina", "dominios_distintos")}
    CAT.write_text(json.dumps(C, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    LOCAIS.write_text(json.dumps(locais, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"livros_atualizados": sum(atual.values()), "livros_criados_hoje": sum(criado.values()), "locais_de_busca": locais["livros"],
            "dominios": locais["dominios_distintos"]}


def _corrigir_territorio(x: dict, a: dict, reclassificar) -> None:
    """RC-01 (02/10): livro de edital municipal/estadual não pode ficar 'BR - nacional' quando o achado diz a UF."""
    uf = str(a.get("uf") or "").upper()
    mun = str(a.get("municipio") or "")
    if "/" in mun and mun.split("/")[0].upper() in _UFS:
        uf = uf if uf in _UFS else mun.split("/")[0].upper()
    if uf not in _UFS or x.get("internacional") or x.get("geo") not in (None, "", "BR") or x.get("uf") in _UFS:
        return
    x["uf"] = uf
    for h in x.get("historico") or []:
        h.setdefault("uf", uf)
    if reclassificar:
        reclassificar(x)


_UFS = set("AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split())


def _aplicar_semente(C: dict) -> dict:
    """Leva ao catálogo as oportunidades do parecer das 238 marcadas `criar_livro`/`atualizar_livro` (uma vez por versão)."""
    sem = _j(SEMENTE, {})
    if not sem or C.get("semente_238", {}).get("versao") == sem.get("versao"):
        return C.get("semente_238") or {}
    acoes = [e for e in sem.get("itens") or [] if e.get("acao") in ("criar_livro", "atualizar_livro")]
    r = registrar_achados([{**e, "excecao_abrangencia": sem.get("excecao_abrangencia")} for e in acoes], "Parecer 238 (02/10)",
                          catalogo=C, gravar=False)
    return {"versao": sem.get("versao"), "aplicada_em": _agora(), **r}


def registrar_achados(achados: list[dict], origem: str, catalogo: dict | None = None, gravar: bool = True) -> dict:
    """Achado que não está nos livros vira um livro novo; o que já existe recebe a informação nova e, se for outra
    publicação, ENTRA COMO EDIÇÃO no histórico do livro (alimenta a previsão). Usado pelo Espião e pelo motor estadual."""
    from .opressores_repositorio import chave, internacional
    from .livros_opressores import classificar
    from .regras_restricao import avaliar, julgar_no_livro, bloco_do_livro
    C = catalogo if catalogo is not None else _j(CAT, {}); ms = C.setdefault("motores", [])
    vetados = C.setdefault("vetados_pelas_restricoes", [])
    pendentes = C.setdefault("pendentes_das_restricoes", [])
    vistos_veto = {(v.get("url"), v.get("regra")) for v in vetados} | {(v.get("url"), v.get("regra")) for v in pendentes}
    n_vetos = n_pend = 0
    from .nucleo import has_prompt_injection
    from .curadoria_biblioteca import editais_distintos

    def _anotar(lista, livro, tit, url, regra):           # 02/10: o vetado/pendente fica registrado uma vez (nada se perde)
        if (url, regra) in vistos_veto:
            return 0
        vistos_veto.add((url, regra))
        lista.append({"em": _agora(), "livro": livro, "titulo": tit[:160], "url": url, "regra": regra, "origem": origem})
        return 1
    por_chave = {}
    for x in ms:
        por_chave.setdefault(chave(x.get("programa") or "", x.get("orgao") or ""), x)
        por_chave.setdefault(chave(x.get("programa") or ""), x)
    criados = atualizados = 0
    ids = {x.get("id") for x in ms}
    por_id = {x.get("id"): x for x in ms}               # 02/10: o achado pode dizer o livro (semente do parecer)
    por_url = {}
    for x in ms:
        for u in [x.get("pagina")] + [h.get("pagina_oficial") for h in (x.get("historico") or []) if isinstance(h, dict)]:
            if u:
                por_url.setdefault(str(u).rstrip("/"), x)
    # 01/10: o que a validação individual já DESCARTOU não volta como livro
    import glob as _g
    descartados = set()
    for f in _g.glob(str(ROOT / "dados/oportunidades/validacao_mapa/validacao_*.json")):
        for d in (_j(Path(f), {}).get("itens") or []):
            if d.get("decisao") == "descartada":
                descartados.add(chave(d.get("titulo") or "")); descartados.add(str(d.get("url") or "").rstrip("/"))
    for a in achados or []:
        tit = str(a.get("titulo") or a.get("nome") or "").strip()
        url = str(a.get("url") or a.get("onde") or "")
        if len(tit) < 8 or not url.startswith("http"):
            continue
        k = chave(tit, a.get("orgao") or a.get("empresa") or "")
        if not a.get("livro") and (chave(tit) in descartados or url.rstrip("/") in descartados):
            continue                                  # (o item da semente que aponta o livro não é barrado pela validação antiga)
        if has_prompt_injection(f"{tit} {a.get('objeto') or ''}"):
            n_vetos += _anotar(vetados, None, tit, url, "quarentena")   # texto coletado é dado: com injeção, não vira livro nem prompt
            continue
        from .regras_restricao import chave_duplicata, chave_pncp_do_livro
        kp = chave_duplicata({"url": url})
        x = por_id.get(a.get("livro"))
        if not x:
            x = por_chave.get(k) or por_chave.get(chave(tit)) or por_url.get(url.rstrip("/"))
            if x and kp and chave_pncp_do_livro(x) not in (None, kp):
                x = None                              # 02/10: outro número no PNCP = outro edital = outro livro
            if x and editais_distintos({"programa": tit}, x):
                x = None                              # 02/10: outro número/valor/objeto/cidade = outro edital = outro livro
        if not x and kp:                              # 02/10: mesma chave PNCP = mesmo livro (DI-08)
            x = next((y for y in ms if chave_pncp_do_livro(y) == kp), None)
        if x:
            j = julgar_no_livro({"titulo": tit, "objeto": a.get("objeto"), "url": url, "modalidade": a.get("modalidade")}, x)
            if j["efeito"] == "veto":                  # 02/10 (titular): IDENTIFICAR primeiro, QUALIFICAR depois — a informação
                n_vetos += _anotar(vetados, x.get("id"), tit, url, j["regra"])   # entra no histórico do livro, marcada
                hist = x.setdefault("historico", [])
                if not any(str(h.get("pagina_oficial") or "").rstrip("/") == url.rstrip("/") for h in hist):
                    hist.append({"id": "pub-" + hashlib.sha1(url.encode()).hexdigest()[:10], "titulo": tit[:200], "pagina_oficial": url,
                                 "origem": origem, "visto_em": date.today().isoformat(),
                                 "qualificacao": {"veredito": "NÃO APLICA", "regra": j["regra"], "acao": "arquivar manualmente se confirmado"}})
                    atualizados += 1
                continue
            if a.get("excecao_abrangencia") and not x.get("excecao_abrangencia"):
                x["excecao_abrangencia"] = a["excecao_abrangencia"]
            try:
                _corrigir_territorio(x, a, classificar)
            except Exception:  # noqa: BLE001
                pass
            hist = x.setdefault("historico", [])
            if not any(str(h.get("pagina_oficial") or "").rstrip("/") == url.rstrip("/") for h in hist):
                hist.append({k: v for k, v in {"id": "pub-" + hashlib.sha1(url.encode()).hexdigest()[:10], "titulo": tit[:200],
                             "publicado_em": a.get("publicado_em"), "fim": a.get("prazo") if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(a.get("prazo") or "")) else None,
                             "uf": a.get("uf"), "pagina_oficial": url, "origem": origem, "visto_em": date.today().isoformat()}.items() if v})
                hist.sort(key=lambda h: str(h.get("fim") or h.get("publicado_em") or ""))
                atualizados += 1
            if anotar_checklist(x, _checklist_de(a), origem, edicao={"titulo": tit}):
                atualizados += 1
            continue
        av = avaliar({"titulo": tit, "objeto": a.get("objeto"), "url": url, "uf": a.get("uf"), "modalidade": a.get("modalidade"),
                      "fim": a.get("prazo") if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(a.get("prazo") or "")) else None})
        qualif = None
        if av["veredito"] == "NÃO APLICA" and not a.get("excecao_abrangencia"):
            # 02/10 (titular): nada é eliminado de início — o achado vira livro, QUALIFICADO como não aplicável; o
            # arquivamento é manual (curadoria). Fica também anotado em vetados_pelas_restricoes, para a conferência.
            n_vetos += _anotar(vetados, None, tit, url, av["regra"])
            from .regras_restricao import qualificacao_do_veto
            qualif = qualificacao_do_veto(av["regra"], f"{tit} {a.get('objeto') or ''}", str(av.get("motivo") or ""), date.today().isoformat())
        if av.get("efeito") == "edicao" and not a.get("excecao_abrangencia"):
            n_pend += _anotar(pendentes, None, tit, url, av["regra"])   # errata/resultado sem o livro do edital: espera o livro
            continue
        lid = "op-" + hashlib.sha1((("espiao|" if origem == "Piloto - Espião" else origem + "|") + k + (("|" + kp) if kp else "")).encode()).hexdigest()[:12]
        if lid in ids:
            continue
        x = {"id": lid, "programa": tit[:200], "orgao": a.get("orgao") or a.get("empresa") or "", "motor": "repositorio",
             "tipo": "repositorio_de_oportunidade", "familia": "Oportunidade com seleção", "uf": a.get("uf"), "pagina": url,
             "ativa": True, "validacao": "não lida ainda", "criado_em": date.today().isoformat(),
             "motivo_status": f"livro criado por {origem} (oportunidade que não estava na Biblioteca)",
             "historico": [{"id": lid, "titulo": tit[:200], "fim": a.get("prazo") if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(a.get("prazo") or "")) else None,
                            "uf": a.get("uf"), "pagina_oficial": url, "origem": origem, "publicado_em": a.get("publicado_em"), "visto_em": date.today().isoformat()}]}
        if internacional(x):
            x["internacional"] = True
        if a.get("excecao_abrangencia"):
            x["excecao_abrangencia"] = a["excecao_abrangencia"]
        try:
            _corrigir_territorio(x, a, None)
        except Exception:  # noqa: BLE001
            pass
        classificar(x); anotar_checklist(x, _checklist_de(a), origem)
        if qualif:
            x["qualificacao"] = qualif
            if qualif["veredito"] == "NÃO APLICA":
                x["ativa"] = False
        x["busca"] = bloco_do_livro(x)
        ms.append(x); por_chave[k] = x; ids.add(lid); por_id[lid] = x; por_url[url.rstrip("/")] = x; criados += 1
    C["vetados_pelas_restricoes"] = vetados[-300:]
    C["pendentes_das_restricoes"] = pendentes[-300:]
    if gravar and (criados or atualizados or n_vetos or n_pend):
        CAT.write_text(json.dumps(C, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {"livros_novos": criados, "livros_atualizados": atualizados, "vetados_pelas_restricoes": n_vetos, "pendentes_das_restricoes": n_pend}



def registrar_achados_do_espiao(achados: list[dict]) -> dict:
    return registrar_achados(achados, "Piloto - Espião")

if __name__ == "__main__":
    print(json.dumps(aplicar_motores(), ensure_ascii=False, indent=1))
