"""Perfil do livro de Goiás sem selo ouro: site oficial + os 12 itens consolidados do histórico já coletado.

Não lê edições: usa só o que já foi comprovado (leitura das edições anteriores, parâmetros do histórico, catálogo).
Lacuna = pendência explícita com motivo; nada é inventado.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

ITENS = ["Objeto", "Prazo de inscrição", "Resultado", "Prazo de recurso", "Valor", "Órgão / financiador",
         "Território", "Esfera", "Requisitos", "Anexos", "Destinação", "Área de atuação"]

# Portais oficiais conferidos em 03/10/2026 (título e órgão da página) — ver relatório.
_GOIAS = {
    "cultura": ("https://goias.gov.br/cultura/", "Secretaria de Estado da Cultura (Secult-GO)"),
    "social": ("https://goias.gov.br/social/", "Secretaria de Desenvolvimento Social (Goiás Social)"),
    "esporte": ("https://goias.gov.br/esporte/", "Secretaria de Estado de Esporte e Lazer"),
    "turismo": ("https://goias.gov.br/turismo/", "Goiás Turismo (Agência Estadual de Turismo)"),
    "seguranca": ("https://goias.gov.br/seguranca/", "Secretaria de Segurança Pública"),
    "fapeg": ("https://goias.gov.br/fapeg/", "FAPEG"),
    "meioambiente": ("https://goias.gov.br/meioambiente/", "SEMAD"),
}
_MUN = {  # portais municipais com título conferido no navegador em 03/10/2026
    "goiania.go.gov.br": "Prefeitura de Goiânia", "anapolis.go.gov.br": "Prefeitura de Anápolis",
    "cidadeocidental.go.gov.br": "Prefeitura de Cidade Ocidental", "goiatuba.go.gov.br": "Prefeitura de Goiatuba",
    "itaberai.go.gov.br": "Prefeitura de Itaberaí", "senadorcanedo.go.gov.br": "Prefeitura de Senador Canedo",
    "planaltina.go.gov.br": "Prefeitura Municipal de Planaltina", "alvoradadonorte.go.gov.br": "Prefeitura Municipal de Alvorada do Norte",
    "morrinhos.go.gov.br": "Prefeitura Municipal de Morrinhos", "goianesia.go.gov.br": "Prefeitura de Goianésia",
    "novaamerica.go.gov.br": "Prefeitura Municipal de Nova América", "cantodaprimavera.cultura.go.gov.br": "Plataforma cultural Canto da Primavera (cultura.go.gov.br)",
    "acessoainformacao.cavalcante.go.gov.br": "Prefeitura de Cavalcante", "acessoainformacao.goiatuba.go.gov.br": "Prefeitura de Goiatuba",
}


def site_oficial(x: dict) -> dict:
    nome = f"{x.get('programa') or ''} {x.get('nome_classificado') or ''}"
    pag = str(x.get("pagina") or "")
    u = urlparse(pag)
    host = u.netloc.removeprefix("www.")
    if host == "goias.gov.br":
        seg = u.path.strip("/").split("/")[0]
        if seg in _GOIAS:
            url, org = _GOIAS[seg]
            if seg == "cultura":
                if re.search(r"pnab|aldir|fica\b", nome, re.I):
                    url = "https://goias.gov.br/cultura/pnab/"
                elif re.search(r"fundo de arte|fac\b", nome, re.I):
                    url = "https://goias.gov.br/cultura/fundo-de-arte-e-cultura/"
            return {"url": url, "orgao_site": org, "tipo": "portal oficial do órgão", "verificado": "2026-10-03", "pagina_do_livro": pag}
    if host == "diariooficial.abc.go.gov.br" and "goiatuba" in str(x.get("municipio") or "").lower():
        host, pag = "goiatuba.go.gov.br", pag
    if host in _MUN:
        return {"url": f"https://{host}/", "orgao_site": _MUN[host], "tipo": "portal oficial do município", "verificado": "2026-10-03", "pagina_do_livro": pag}
    if host == "pncp.gov.br":
        return {"url": pag, "orgao_site": x.get("orgao"), "tipo": "PNCP (portal oficial de contratações; o município não tem página própria do edital)", "verificado": "2026-10-03 (página do edital já registrada)", "pagina_do_livro": pag}
    if host.endswith(".go.gov.br") or host.endswith(".gov.br") or host.endswith(".go.gov.br".replace(".go", "")):
        return {"url": f"https://{u.netloc}/", "orgao_site": x.get("orgao"), "tipo": "portal oficial (domínio .gov.br do órgão)", "verificado": "domínio .gov.br; título não conferido nesta rodada", "pagina_do_livro": pag}
    if pag:
        return {"url": pag, "orgao_site": x.get("orgao"), "tipo": "página registrada do livro (não foi possível confirmar portal próprio)", "verificado": "não", "pagina_do_livro": pag}
    return {"url": None, "orgao_site": x.get("orgao"), "tipo": "sem página registrada", "verificado": "não", "pagina_do_livro": None}


def itens_do_livro(x: dict, eds: list[dict], derivado, situacao: str, motivo: str) -> dict:
    """Consolida os 12 itens: edição mais recente com dado confirmado > parâmetros do histórico > catálogo > pendência explícita."""
    hist = [h for h in (x.get("historico") or []) if isinstance(h.get("parametros"), dict)]
    hist.sort(key=lambda h: str(h.get("publicado_em") or h.get("inicio") or ""), reverse=True)
    out = {}
    for k in ITENS:
        r = None
        for e in sorted(eds, key=lambda e: e.get("mes") or "", reverse=True):
            v = (e.get("itens") or e.get("_status") or {}).get(k) or {}
            if v.get("estado") == "confirmado" and v.get("valor"):
                r = {"estado": "confirmado", "valor": v["valor"], "origem": f"edição {e.get('mes')} (já coletada)"}
                break
        if not r:
            for h in hist:
                v = h["parametros"].get(k)
                if v:
                    r = {"estado": "confirmado", "valor": str(v), "origem": f"estudo do histórico ({h.get('ano') or '?'})"}
                    break
        if not r:
            d = derivado(k, x)
            if d:
                r = {"estado": "catalogo", "valor": d["valor"], "origem": d.get("fonte") or "catálogo do livro"}
        if not r:
            r = _fallback(k, x)
        if not r:
            if situacao.startswith("dispensa_individual"):
                r = {"estado": "dispensa_individual", "valor": None, "origem": motivo}
            else:
                r = {"estado": "pendente", "valor": None,
                     "origem": "não consta nos dados já coletados das edições anteriores; fica no edital/ata do órgão (não lido por decisão da titular nesta rodada)"}
        out[k] = r
    return out


def _fallback(k: str, x: dict) -> dict | None:
    if k == "Território":
        v = x.get("municipio") or ("Goiás" if (x.get("geo") or x.get("uf")) in ("GO", "Goiás") else None)
        if v:
            return {"estado": "catalogo", "valor": str(v), "origem": "catálogo do livro (município/UF)"}
    if k == "Objeto" and (x.get("programa") or x.get("nome_classificado")):
        return {"estado": "catalogo", "valor": str(x.get("programa") or x.get("nome_classificado"))[:200], "origem": "nome do livro (título do programa)"}
    if k == "Prazo de inscrição":
        pd = x.get("proxima_data") or {}
        if pd.get("inicio") or pd.get("fim"):
            return {"estado": "confirmado", "valor": f"{pd.get('inicio') or '?'} a {pd.get('fim') or '?'}", "origem": "janela mais recente registrada no livro"}
        js = (x.get("livro") or {}).get("inscricao", {}).get("janelas") or []
        if js:
            j = js[-1]
            return {"estado": "confirmado", "valor": f"{j.get('inicio') or '?'} a {j.get('fim') or '?'}", "origem": "janela de inscrição registrada no livro"}
    if k == "Órgão / financiador" and x.get("orgao"):
        return {"estado": "catalogo", "valor": str(x["orgao"]), "origem": "catálogo do livro"}
    return None
