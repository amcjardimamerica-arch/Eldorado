"""Fluxo em 5 passos — Eldorado × Farol de Alexandria.

Estrutura oficial do procedimento (determinação do titular, 01/09/2026):

  1 DESCOBRIR   (Eldorado)  mapear oportunidades e fontes de recursos
  2 CONFIRMAR   (Eldorado)  verificar elegibilidade, requisitos, documentos
                            necessários e anexos — verificação dupla
  3 ENQUADRAR   (integração) entregar os dados à Biblioteca de Alexandria e
                            acionar o Farol: cruzar requisitos do edital com as
                            associações, com IA no modelo adequado a cada
                            tarefa; análise de aderência e viabilidade apoiada
                            no HISTÓRICO do edital (quem venceu antes e por quê)
  4 DECIDIR     (Farol)     escolher automaticamente as entidades com chances
                            reais, criar a pasta do edital dentro da entidade e
                            separar todos os documentos exigidos — sem criar
                            nenhuma informação nova
  5 PREPARAR    (Farol)     preencher os documentos na pasta da associação,
                            deixá-los prontos para download e, faltando dado,
                            emitir NOTA TÉCNICA com o que falta e como obter,
                            conforme o edital

Regra transversal: nada é inventado. Dado ausente vira pendência declarada.
As etapas 4 e 5 são automáticas — não dependem de ação do titular.
"""
from __future__ import annotations

import json
import re
import shutil
from datetime import date
from pathlib import Path

from .biblioteca import ASSOCIACOES, OPORTUNIDADES, pasta_edital_da_associacao
from .nucleo import ROOT, load_json, now_iso, slug, write_json

def _rel(caminho: Path) -> str:
    """Caminho relativo à raiz quando possível; absoluto fora dela (testes)."""
    try:
        return str(caminho.relative_to(ROOT))
    except ValueError:
        return str(caminho)


ETAPAS = (
    (1, "Descobrir", "Eldorado", "mapear oportunidades e fontes de recursos"),
    (2, "Confirmar", "Eldorado", "elegibilidade, requisitos, documentos e anexos"),
    (3, "Enquadrar", "Eldorado + Farol", "Biblioteca alimentada e IA cruza requisitos"),
    (4, "Decidir", "Farol", "entidades com chances reais e documentos separados"),
    (5, "Preparar", "Farol", "documentos preenchidos, prontos para download"),
)

# Documentos habitualmente exigidos — usados apenas para RECONHECER menções no
# texto do edital, nunca para presumir exigência que o edital não fez.
_DOCS = {
    "estatuto_social": r"estatuto\s+social|estatuto\s+da\s+entidade",
    "ata_de_posse": r"ata\s+de\s+(posse|elei[çc][ãa]o)",
    "cnpj": r"\bcnpj\b|cart[ãa]o\s+cnpj|comprovante\s+de\s+inscri[çc][ãa]o",
    "certidao_federal": r"certid[ãa]o[^.\n]{0,50}(federal|receita\s+federal|d[íi]vida\s+ativa\s+da\s+uni[ãa]o)",
    "certidao_estadual": r"certid[ãa]o[^.\n]{0,40}estadual",
    "certidao_municipal": r"certid[ãa]o[^.\n]{0,40}municipal",
    "certidao_fgts": r"\bfgts\b|certificado\s+de\s+regularidade\s+do\s+fgts",
    "certidao_trabalhista": r"cndt|certid[ãa]o[^.\n]{0,30}trabalhista",
    "balanco_patrimonial": r"balan[çc]o\s+patrimonial|demonstra[çc][õo]es\s+cont[áa]beis",
    "plano_de_trabalho": r"plano\s+de\s+trabalho",
    "planilha_orcamentaria": r"planilha\s+or[çc]ament[áa]ria|or[çc]amento\s+detalhado",
    "declaracao_nao_impedimento": r"declara[çc][ãa]o[^.\n]{0,50}(impedimento|n[ãa]o\s+incorre)",
    "comprovante_endereco": r"comprovante\s+de\s+endere[çc]o|comprova[çc][ãa]o\s+de\s+sede",
    "inscricao_conselho": r"inscri[çc][ãa]o\s+no\s+conselho|cmas|cmdca",
    "certificacao_cebas": r"\bcebas\b",
}

# Onde obter cada documento — orientação objetiva para a nota técnica
_ONDE_OBTER = {
    "estatuto_social": "cópia registrada em cartório de registro civil de pessoas jurídicas",
    "ata_de_posse": "ata da última eleição/posse registrada em cartório",
    "cnpj": "comprovante de inscrição e situação cadastral no site da Receita Federal",
    "certidao_federal": "Certidão Negativa de Débitos Federais e Dívida Ativa da União (Receita Federal/PGFN)",
    "certidao_estadual": "certidão negativa da Secretaria da Fazenda do estado da sede",
    "certidao_municipal": "certidão negativa de tributos municipais na prefeitura da sede",
    "certidao_fgts": "Certificado de Regularidade do FGTS (CRF) na Caixa Econômica Federal",
    "certidao_trabalhista": "Certidão Negativa de Débitos Trabalhistas (CNDT) no TST",
    "balanco_patrimonial": "balanço do último exercício assinado pelo contador responsável",
    "plano_de_trabalho": "preencher o modelo do próprio edital (anexo preservado na Biblioteca)",
    "planilha_orcamentaria": "preencher a planilha do edital com memória de cálculo e pesquisa de preços",
    "declaracao_nao_impedimento": "assinar o modelo de declaração do edital",
    "comprovante_endereco": "conta de consumo em nome da entidade ou contrato de comodato da sede",
    "inscricao_conselho": "certidão de inscrição no conselho municipal da área (CMAS/CMDCA)",
    "certificacao_cebas": "certificado CEBAS vigente ou protocolo de renovação no ministério competente",
}


def documentos_exigidos(texto: str) -> list[str]:
    """Só o que o edital efetivamente menciona."""
    return [chave for chave, padrao in _DOCS.items()
            if re.search(padrao, texto, re.I)]


def documentos_da_associacao(assoc_slug: str) -> dict[str, Path]:
    """Documentos institucionais já disponíveis, pelo nome do arquivo."""
    pasta = ASSOCIACOES / assoc_slug / "documentos"
    achados: dict[str, Path] = {}
    if not pasta.exists():
        return achados
    for arq in pasta.glob("*"):
        if not arq.is_file():
            continue
        nome = slug(arq.stem).replace("-", "_")
        for chave in _DOCS:
            if chave in nome or nome in chave:
                achados[chave] = arq
    return achados


def _previa_documentos(assoc_slug: str, exigidos: list[str]) -> dict:
    """O que a entidade já tem e o que falta — antes de decidir."""
    disponiveis = documentos_da_associacao(assoc_slug)
    faltantes = [{"documento": d,
                  "como_obter": _ONDE_OBTER.get(d, "conferir a exigência no edital")}
                 for d in exigidos if d not in disponiveis]
    perfil_p = ASSOCIACOES / assoc_slug / "perfil_publico.json"
    perfil = load_json(perfil_p) if perfil_p.exists() else {}
    completo = bool(perfil.get("nome") and perfil.get("territorios")
                    and perfil.get("anos_existencia") is not None)
    return {"faltantes": faltantes, "perfil_completo": completo}


def _area_aderente(assoc_slug: str, texto: str) -> bool:
    perfil_p = ASSOCIACOES / assoc_slug / "perfil_publico.json"
    if not perfil_p.exists():
        return False
    areas = load_json(perfil_p).get("areas") or []
    return any(re.search(a.replace("_", "[ _]"), texto, re.I) for a in areas)


# ------------------------------------------------------------------ etapa 4
def decidir(chave: str, ano: str, hoje: date | None = None) -> dict:
    """Etapa 4 — DECIDIR (automática).

    Escolhe as entidades com chances reais a partir do parecer da etapa 3,
    cria a pasta do edital dentro de cada entidade escolhida e separa nela
    todos os documentos exigidos pelo edital. Nada de novo é inventado: o que
    a entidade não tem entra como pendência.
    """
    hoje = hoje or date.today()
    ficha_p = OPORTUNIDADES / chave / ano / "ficha.json"
    if not ficha_p.exists():
        raise FileNotFoundError(f"edital fora da Biblioteca: {chave}/{ano}")
    ficha = load_json(ficha_p)
    texto = (ficha_p.parent / "edital.txt").read_text(encoding="utf-8", errors="ignore")
    exigidos = documentos_exigidos(texto)

    from . import farol_parecer as _fp
    parecer_p = _fp.PARECERES / chave / ano / "parecer.json"
    parecer = load_json(parecer_p) if parecer_p.exists() else {}
    avaliacoes = parecer.get("portao") or []
    if not avaliacoes:
        parecer = _fp.gerar(chave, ano)
        avaliacoes = parecer.get("portao") or []

    # ---- ETAPA 3: conselho de 7 lentes delibera ANTES e corrobora a decisão
    from .conselho_edital import deliberar_com_ia
    from .farol_parecer import trechos_relevantes
    historico = (load_json(OPORTUNIDADES / "indice.json")
                 if (OPORTUNIDADES / "indice.json").exists() else {})
    trechos = trechos_relevantes(texto, 8000)
    edital_ctx = {"chave": chave, "ano": ano, "titulo": ficha.get("titulo"),
                  "fonte_nome": ficha.get("fonte_nome"), "inicio": ficha.get("inicio"),
                  "fim": ficha.get("fim"), "valor_texto": ficha.get("valor_texto")}

    escolhidas, descartadas, conselhos = [], [], {}
    for av in avaliacoes:
        prevs = _previa_documentos(av["slug"], exigidos)
        ctx_conselho = {
            "documentos_faltantes": prevs["faltantes"],
            "historico_ocorrencias": len([r for r in historico.get("editais", [])
                                          if r.get("financiador") == ficha.get("fonte_nome")]),
            "modelos": len(list((OPORTUNIDADES / chave / ano / "modelos").glob("*.pdf")))
                       if (OPORTUNIDADES / chave / ano / "modelos").exists() else 0,
            "area_aderente": _area_aderente(av["slug"], texto),
            "perfil_completo": prevs["perfil_completo"],
        }
        conselho = deliberar_com_ia(edital_ctx, av, ctx_conselho,
                                    trechos, historico.get("exigencias_mais_cobradas"))
        conselhos[av["slug"]] = conselho
        av["_conselho"] = conselho
        # o voto do neutro é VINCULANTE
        if conselho["decisao"] != "concorrer":
            descartadas.append({
                "associacao": av["associacao"], "slug": av["slug"],
                "decisao_conselho": conselho["decisao"],
                "motivo": conselho["fundamento"],
                "conselheiro_neutro": conselho["conselheiros"]["neutro"]})
            continue
        escolhidas.append(av)

    preparadas = []
    for av in escolhidas:
        destino = pasta_edital_da_associacao(av["slug"], ficha.get("titulo") or chave)
        (destino / "modelos").mkdir(parents=True, exist_ok=True)
        # separa os modelos do edital (documentos a preencher)
        modelos_orig = OPORTUNIDADES / chave / ano / "modelos"
        copiados = []
        if modelos_orig.exists():
            for pdf in sorted(modelos_orig.glob("*.pdf")):
                alvo = destino / "modelos" / pdf.name
                shutil.copyfile(pdf, alvo)
                copiados.append(pdf.name)
        # separa os documentos institucionais que a entidade já tem
        disponiveis = documentos_da_associacao(av["slug"])
        (destino / "documentos").mkdir(exist_ok=True)
        anexados, faltantes = [], []
        for chave_doc in exigidos:
            origem = disponiveis.get(chave_doc)
            if origem:
                alvo = destino / "documentos" / origem.name
                shutil.copyfile(origem, alvo)
                anexados.append({"documento": chave_doc, "arquivo": origem.name})
            else:
                faltantes.append({"documento": chave_doc,
                                  "como_obter": _ONDE_OBTER.get(chave_doc,
                                                "conferir a exigência no edital")})
        dossie = {
            "edital": {"chave": chave, "ano": ano, "titulo": ficha.get("titulo"),
                       "fonte": ficha.get("fonte_nome"), "fim": ficha.get("fim")},
            "associacao": {"nome": av["associacao"], "slug": av["slug"]},
            "decidido_em": now_iso(), "decisao": "concorrer",
            "base_da_decisao": {"atende": av.get("atende", []),
                                "alertas": av.get("alertas", []),
                                "recomendacao_parecer": parecer.get("recomendacao"),
                                "conselho": {
                                    "decisao": av["_conselho"]["decisao"],
                                    "fundamento": av["_conselho"]["fundamento"],
                                    "modo": av["_conselho"]["modo"],
                                    "conselheiros": av["_conselho"]["conselheiros"]}},
            "parametros_de_qualidade": av["_conselho"]["parametros_de_qualidade"],
            "mitigacao_de_riscos": av["_conselho"]["mitigacao_de_riscos"],
            "documentos_exigidos": exigidos,
            "documentos_anexados": anexados,
            "documentos_faltantes": faltantes,
            "modelos_para_preencher": copiados,
            "nota": "nenhuma informação foi criada; o que falta está declarado",
        }
        write_json(destino / "dossie.json", dossie)
        preparadas.append({"associacao": av["associacao"], "slug": av["slug"],
                           "pasta": _rel(destino),
                           "exigidos": len(exigidos), "anexados": len(anexados),
                           "faltantes": len(faltantes), "modelos": len(copiados)})

    resultado = {"etapa": 4, "edital": f"{chave}/{ano}", "executado_em": now_iso(),
                 "escolhidas": preparadas, "descartadas": descartadas,
                 "documentos_exigidos": exigidos,
                 "corroboracao": {"etapa": 3, "instrumento": "conselho de 7 lentes",
                                  "voto_vinculante": "neutro",
                                  "por_associacao": {s: {"decisao": c["decisao"],
                                                         "modo": c["modo"]}
                                                     for s, c in conselhos.items()}}}
    write_json(OPORTUNIDADES / chave / ano / "conselho.json",
               {"edital": f"{chave}/{ano}", "executado_em": now_iso(),
                "deliberacoes": conselhos})
    write_json(OPORTUNIDADES / chave / ano / "decisao.json", resultado)
    return resultado


# ------------------------------------------------------------------ etapa 5
def _valores_da_associacao(slug_assoc: str) -> dict:
    """Somente dados do perfil público — nada sensível entra aqui."""
    perfil_p = ASSOCIACOES / slug_assoc / "perfil_publico.json"
    if not perfil_p.exists():
        return {}
    p = load_json(perfil_p)
    return {"nome_entidade": p.get("nome"), "nome": p.get("nome"),
            "razao_social": p.get("nome"),
            "municipio": (p.get("territorios") or [None])[0],
            "areas_atuacao": ", ".join(p.get("areas") or []),
            "anos_existencia": p.get("anos_existencia"),
            "natureza_juridica": p.get("natureza_juridica")}


def preparar(chave: str, ano: str) -> dict:
    """Etapa 5 — PREPARAR (automática).

    Preenche os modelos DENTRO da pasta da associação e emite a nota técnica
    final com os dados que faltaram e como obtê-los conforme o edital.
    """
    decisao_p = OPORTUNIDADES / chave / ano / "decisao.json"
    if not decisao_p.exists():
        raise FileNotFoundError("etapa 4 (Decidir) ainda não executada")
    decisao = load_json(decisao_p)
    ficha = load_json(OPORTUNIDADES / chave / ano / "ficha.json")
    from .farol_docs import preencher_modelo

    saidas = []
    for esc in decisao["escolhidas"]:
        pasta = Path(esc["pasta"])
        if not pasta.is_absolute():
            pasta = ROOT / pasta
        valores = _valores_da_associacao(esc["slug"])
        dossie = load_json(pasta / "dossie.json")
        preenchidos, nao_preenchiveis, campos_sem_dado = [], [], []
        for pdf in sorted((pasta / "modelos").glob("*.pdf")):
            destino = pasta / "preenchidos" / pdf.name
            try:
                rel = preencher_modelo(pdf, valores, destino)
                preenchidos.append({"arquivo": destino.name,
                                    "campos": rel["preenchidos"]})
                campos_sem_dado += rel["campos_sem_dado"]
            except ValueError:
                nao_preenchiveis.append(
                    {"arquivo": pdf.name,
                     "motivo": "modelo sem campos de formulário — preencher "
                               "manualmente sobre o PDF original, sem recriar"})
            except RuntimeError as exc:
                nao_preenchiveis.append({"arquivo": pdf.name, "motivo": str(exc)})

        faltantes = dossie.get("documentos_faltantes", [])
        linhas = [
            f'# Nota técnica — {ficha.get("titulo") or chave}', "",
            f'**Associação:** {esc["associacao"]}  ',
            f'**Fonte:** {ficha.get("fonte_nome") or "—"}  ',
            f'**Prazo final de inscrição:** {ficha.get("fim") or "não declarado na fonte"}  ',
            f'**Emitida em:** {now_iso()}', "",
            "## Documentos prontos para envio", "",
        ]
        linhas += ([f'- `{p["arquivo"]}` — campos preenchidos: '
                    f'{", ".join(p["campos"]) or "nenhum campo automático"}'
                    for p in preenchidos] or ["- nenhum modelo preenchível localizado"])
        if dossie.get("documentos_anexados"):
            linhas += ["", "## Documentos institucionais anexados", ""]
            linhas += [f'- {d["documento"].replace("_", " ")} — `{d["arquivo"]}`'
                       for d in dossie["documentos_anexados"]]
        if faltantes:
            linhas += ["", "## Falta providenciar", "",
                       "Os itens abaixo são exigidos pelo edital e não estão na "
                       "pasta da associação. Nada foi criado no lugar deles.", ""]
            linhas += [f'- **{f["documento"].replace("_", " ")}** — {f["como_obter"]}'
                       for f in faltantes]
        if nao_preenchiveis:
            linhas += ["", "## Modelos de preenchimento manual", ""]
            linhas += [f'- `{n["arquivo"]}` — {n["motivo"]}' for n in nao_preenchiveis]
        if campos_sem_dado:
            linhas += ["", "## Campos sem dado no cadastro público", "",
                       "Preencher à mão sobre o PDF (dados sensíveis não ficam no "
                       "repositório público):", ""]
            linhas += [f"- {c}" for c in sorted(set(campos_sem_dado))[:30]]
        conselho = (dossie.get("base_da_decisao") or {}).get("conselho") or {}
        if conselho:
            linhas += ["", "## Deliberação do conselho (etapa 3)", "",
                       f'**Decisão:** {str(conselho.get("decisao","")).upper()}  ',
                       f'**Fundamento:** {conselho.get("fundamento","")}  ',
                       f'**Voto ponderador:** {(conselho.get("conselheiros") or {}).get("neutro","—")}  ',
                       f'**Modo:** {conselho.get("modo","")}', ""]
        if dossie.get("parametros_de_qualidade"):
            linhas += ["### Parâmetros de qualidade", ""]
            linhas += [f"- {x}" for x in dossie["parametros_de_qualidade"]]
        if dossie.get("mitigacao_de_riscos"):
            linhas += ["", "### Mitigação de riscos", ""]
            linhas += [f'- **{m["risco"]}** → {m["acao"]}'
                       for m in dossie["mitigacao_de_riscos"]]
        linhas += ["", "---", "",
                   "Documento gerado automaticamente pelo Farol de Alexandria a "
                   "partir do texto do edital e do cadastro da associação. "
                   "Nenhuma informação foi inventada; conferir na fonte primária "
                   "antes do protocolo."]
        (pasta / "NOTA-TECNICA.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")

        saidas.append({"associacao": esc["associacao"], "slug": esc["slug"],
                       "pasta": esc["pasta"],
                       "preenchidos": len(preenchidos),
                       "manuais": len(nao_preenchiveis),
                       "faltantes": len(faltantes),
                       "pronto_para_download": bool(preenchidos),
                       "nota_tecnica": "NOTA-TECNICA.md"})

    resultado = {"etapa": 5, "edital": f"{chave}/{ano}",
                 "executado_em": now_iso(), "associacoes": saidas}
    write_json(OPORTUNIDADES / chave / ano / "preparacao.json", resultado)
    return resultado


def run(limite: int = 5) -> dict:
    """Executa as etapas 4 e 5 para os editais completos e ainda não decididos."""
    feitos, erros = [], []
    if not OPORTUNIDADES.exists():
        return {"executado_em": now_iso(), "processados": 0,
                "nota": "Biblioteca ainda sem editais completos"}
    for ficha in sorted(OPORTUNIDADES.glob("*/*/ficha.json"))[:limite]:
        chave, ano = ficha.parent.parent.name, ficha.parent.name
        try:
            d = decidir(chave, ano)
            p = preparar(chave, ano)
            feitos.append({"edital": f"{chave}/{ano}",
                           "escolhidas": len(d["escolhidas"]),
                           "descartadas": len(d["descartadas"]),
                           "preparadas": len(p["associacoes"])})
        except Exception as exc:
            erros.append({"edital": f"{chave}/{ano}",
                          "erro": f"{type(exc).__name__}: {exc}"})
    return {"executado_em": now_iso(), "processados": len(feitos),
            "detalhe": feitos, "erros": erros}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
