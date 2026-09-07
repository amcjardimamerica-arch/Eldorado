"""PARAMETRIZAÇÃO DAS OPORTUNIDADES SEM PRAZO — uma ficha por oportunidade.

Mesmo método aplicado às 260 fontes, agora sobre cada oportunidade concreta que
está aberta/possível e ainda não tem prazo confirmado:

  • os 14 itens, com o que já se sabe, o que a norma prevê e o que falta;
  • os documentos exigidos (Lei 13.019/2014) conforme o rito inferido;
  • a faixa de valor quando o rito ou a fonte a fixa;
  • os critérios de pontuação do rito (ou a marcação de recurso não competitivo);
  • a análise preditiva e — o ponto central aqui — o CAMINHO DE CONFIRMAÇÃO do
    prazo: onde procurar, o que procurar e o que fazer se a fonte não abrir.

Escopo (regra do titular de 07/09): entram as nacionais (sem restrição
geográfica), as estaduais e as municipais das 50 maiores cidades de cada estado.
As demais ficam fora, para aprovação manual em rosa.

Saída: biblioteca_alexandria/oportunidades_sem_prazo/<id>/ficha.json
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json
from .parametros import DOCS_MROSC, ITENS_14, PERFIL_TIPO, documentos, preditiva, _faixa, _texto_faixa

DESTINO = ROOT / "biblioteca_alexandria/oportunidades_sem_prazo"
FILA = ROOT / "estado/fila_verificacao.json"

RITO_POR_TEXTO = [
    (r"chamamento p[úu]blico|termo de (fomento|colabora)|parceria com (osc|organiza)", "edital"),
    (r"credenciamento|qualifica[çc][ãa]o de pessoa", "edital"),
    (r"emenda parlamentar|indica[çc][ãa]o parlamentar", "emenda"),
    (r"rouanet|incentivo (fiscal|[àa] cultura)|goyazes|pronac|lei do esporte|lie\b", "incentivo_fiscal"),
    (r"fundo (municipal|estadual|nacional)|fmdca|fmas|fia\b|fundo da (crian|pessoa idosa)", "fundo"),
    (r"presta[çc][õo]es pecuni[áa]rias|execu[çc][ãa]o penal|minist[ée]rio p[úu]blico|vara de", "destinacao_judicial"),
    (r"doa[çc][ãa]o|patroc[íi]nio|destina[çc][ãa]o de bens|mercadorias apreendidas", "doacao_patrocinio"),
    (r"edital|sele[çc][ãa]o p[úu]blica|pr[êe]mio|concurso", "edital"),
]
AREA_POR_TEXTO = [
    (r"cultur|arte|m[úu]sica|teatro|audiovisual|patrim[ôo]nio|pnab|aldir blanc", "cultura"),
    (r"esporte|desportiv|atleta", "esporte"),
    (r"sa[úu]de|hospital|SUS|m[ée]dic", "saude"),
    (r"crian[çc]a|adolescente|infanto|cmdca|fia\b", "crianca_adolescente"),
    (r"idos|terceira idade|cmi\b", "pessoa_idosa"),
    (r"assist[êe]ncia social|socioassistenc|suas|cras|creas|seguran[çc]a alimentar|fome", "assistencia_social"),
    (r"educa[çc][ãa]o|escola|ensino|bolsa", "educacao"),
    (r"ambient|sustentab|res[íi]duo|reciclag|clima", "meio_ambiente"),
    (r"direitos humanos|mulher|racial|lgbt|defici[êe]ncia", "direitos_humanos"),
]


def _infere(texto: str, regras: list, padrao: str) -> tuple[str, str | None]:
    alvo = (texto or "").lower()
    for rx, v in regras:
        if re.search(rx, alvo, re.I):
            return v, f"inferido do texto da oportunidade ('{rx.split('|')[0]}')"
    return padrao, "não inferível do texto — a confirmar no edital"


def caminho_de_confirmacao(item: dict, rito: str) -> dict:
    """Onde e como confirmar o prazo desta oportunidade — o que a IA (ou o titular)
    deve fazer, nesta ordem."""
    passos = []
    oficial = item.get("link_oficial")
    anuncio = item.get("link_anuncio")
    vetor = item.get("anuncio_e_vetor")
    if oficial:
        passos.append({"ordem": 1, "onde": oficial, "o_que": "abrir a página oficial do órgão e localizar o edital pelo número/ano; ler o item 'DAS INSCRIÇÕES' (início e fim) e 'DO CRONOGRAMA'"})
    if vetor and anuncio:
        passos.append({"ordem": len(passos) + 1, "onde": anuncio,
                       "o_que": "o anúncio no PNCP/diário serve só para obter o número do processo, o CNPJ do órgão e a data de publicação — nunca como fonte do prazo"})
    if item.get("escopo") == "municipal" and item.get("cidade") and item.get("uf"):
        cid = re.sub(r"[^a-z]", "", item["cidade"].lower().replace("ã", "a").replace("é", "e"))
        passos.append({"ordem": len(passos) + 1, "onde": f"https://www.{cid}.{item['uf'].lower()}.gov.br",
                       "o_que": "site institucional provável da prefeitura (padrão dos portais municipais): procurar 'Editais', 'Licitações', 'Chamamentos' ou 'Transparência'"})
    if rito == "emenda":
        passos.append({"ordem": len(passos) + 1, "onde": "gabinete parlamentar / plataforma de transferências",
                       "o_que": "emenda não tem edital: confirmar a janela de indicação (out–nov) e a habilitação da entidade na plataforma"})
    if rito == "incentivo_fiscal":
        passos.append({"ordem": len(passos) + 1, "onde": "sistema do programa (Salic, Goyazes, LIE)",
                       "o_que": "confirmar a janela anual de propostas e o teto do exercício"})
    passos.append({"ordem": len(passos) + 1, "onde": "contato direto com o órgão",
                   "o_que": "se nenhuma fonte abrir: pedido pela Lei de Acesso à Informação ou telefone da ouvidoria, registrando data e protocolo"})
    return {"passos": passos, "prazo_confirmado_quando": "o edital (PDF ou página oficial) declarar a data-limite de inscrição; até lá o item fica 'não comprovado'",
            "aviso": "nenhuma data pode ser afirmada a partir do anúncio em vetor de divulgação"}


def ficha(item: dict) -> dict:
    texto = f"{item.get('titulo') or ''} {item.get('fonte') or ''}"
    rito, rito_origem = _infere(texto, RITO_POR_TEXTO, "edital")
    area, area_origem = _infere(texto, AREA_POR_TEXTO, item.get("area") or "outros")
    perfil = PERFIL_TIPO.get(rito, PERFIL_TIPO["outro"])
    nivel = {"nacional": "federal", "estadual": "estadual", "municipal": "municipal"}.get(item.get("escopo"), "municipal")
    fonte_falsa = {"id": item["id"], "programa": item.get("titulo") or "", "orgao": item.get("fonte") or "", "nivel": nivel,
                   "area": area, "tipo": rito, "uf": item.get("uf"), "sites": [x for x in (item.get("link_oficial"),) if x]}
    val = _faixa(fonte_falsa, {})
    docs = documentos(fonte_falsa)
    faltam = set(item.get("faltam") or ITENS_14)
    itens14 = []
    for i in ITENS_14:
        if i in perfil["itens_nao_exigidos"]:
            itens14.append({"item": i, "situacao": "nao_exigido", "valor": None, "motivo": perfil.get("motivo_nao_exigidos", "não se aplica a este rito")})
            continue
        prev = {"Objeto": item.get("titulo"), "Prazo de inscrição": None if item.get("sem_prazo") else "confirmado no cadastro",
                "Resultado": "publicação pelo órgão no mesmo veículo do edital", "Prazo de recurso": perfil["recurso"],
                "Valor": _texto_faixa(val), "Órgão / financiador": item.get("fonte"),
                "Território": item.get("cidade") and f"{item['cidade']}/{item.get('uf')}" or (item.get("uf") or "Brasil"),
                "Esfera": nivel, "Requisitos": "OSC regular, com experiência na área e tempo mínimo de existência",
                "Anexos": "edital, plano de trabalho, declarações e planilha orçamentária",
                "Destinação": f"projetos de {area.replace('_', ' ')}", "Área de atuação": area,
                "Requisitos de habilitação": perfil["rito"],
                "Critérios de pontuação": "; ".join(f"{c} ({p})" for c, p in perfil["pontuacao"]) or perfil["base_pontuacao"]}[i]
        conhecido = i in ("Objeto", "Órgão / financiador", "Território", "Esfera", "Área de atuação") and prev
        itens14.append({"item": i, "situacao": "obtido" if conhecido and i not in faltam else ("a_confirmar" if i == "Prazo de inscrição" else "previsto"),
                        "valor": prev, "origem": ("cadastro da oportunidade" if conhecido else "previsão pelo rito inferido")})
    return {
        "id": item["id"], "titulo": item.get("titulo"), "orgao": item.get("fonte"), "uf": item.get("uf"), "cidade": item.get("cidade"),
        "escopo": item.get("escopo"), "modo": item.get("modo"), "situacao": item.get("situacao"),
        "rito_inferido": rito, "rito_origem": rito_origem, "area_inferida": area, "area_origem": area_origem,
        "competitivo": perfil["competitivo"], "itens_14": itens14,
        "documentos": docs, "documentos_resumo": {"obrigatorios": [d["documento"] for d in docs if d["situacao"] == "obrigatorio"],
                                                  "nao_exigidos": [d["documento"] for d in docs if d["situacao"] == "nao_exigido"]},
        "valores": val,
        "pontuacao": {"competitivo": perfil["competitivo"], "base": perfil["base_pontuacao"],
                      "criterios": [{"criterio": c, "peso": p} for c, p in perfil["pontuacao"]] or None},
        "preditiva": preditiva(fonte_falsa, {}),
        "confirmacao_do_prazo": caminho_de_confirmacao(item, rito),
        "estado": "sem prazo confirmado — marcado para verificação" if item.get("sem_prazo") else "prazo no cadastro, itens incompletos",
        "parametrizado_em": now_iso(), "versao": 1,
        "aviso": "ficha derivada do cadastro e do rito inferido; nada aqui substitui o edital. Prazo só é afirmado após leitura na fonte oficial.",
    }


def run(inicio: int = 0, quantidade: int = 100) -> dict:
    if not FILA.exists():
        return {"erro": "fila de verificação ainda não gerada"}
    itens = load_json(FILA)["itens"]
    DESTINO.mkdir(parents=True, exist_ok=True)
    feitas, erros = 0, []
    for it in itens[inicio:inicio + quantidade]:
        try:
            f = ficha(it)
            pasta = DESTINO / it["id"]; pasta.mkdir(parents=True, exist_ok=True)
            write_json(pasta / "ficha.json", f)
            feitas += 1
        except Exception as exc:
            erros.append({"id": it.get("id"), "erro": f"{type(exc).__name__}: {exc}"})
    total = len([x for x in DESTINO.glob("*/ficha.json") if not x.parent.name.startswith("_")])
    write_json(DESTINO / "indice.json", {"gerado_em": now_iso(), "total_fichas": total, "fila": len(itens),
                                         "regra": "uma ficha por oportunidade sem prazo, no mesmo método das 260 fontes"})
    return {"parametrizadas_agora": feitas, "erros": erros[:3], "total_fichas": total, "fila": len(itens)}


if __name__ == "__main__":
    import sys
    ini = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    qtd = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    print(json.dumps(run(ini, qtd), ensure_ascii=False, indent=2))
