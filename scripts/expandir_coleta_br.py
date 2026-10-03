"""Expande as edições provadas por programa (âncora) para cada livro do Brasil e estima o selo — 03/10/2026.

Entrada : dados/coleta_3_anos/ancoras_br.json, dados/coleta_3_anos/anchor_out/<âncora>.json, dados/coleta_3_anos/fila_br.json
Saída   : dados/coleta_3_anos/entrada/br_2026-10-03.json   (formato do prompt original: id do livro → edições)
          dados/coleta_3_anos/resultado_br_2026-10-03.json (selo estimado por livro, famílias, janelas, pendências)
Regras do selo (as do relatório SELO-DOS-LIVROS):
  ouro   = mesma família de programa em 2 ou mais anos distintos dentro de 03/10/2023–03/10/2026, com ao menos uma edição anterior a 2026
           provada em página oficial com data de inscrição e trecho LITERAL (prova "literal");
  prata  = há edição anterior a 2026, mas só com prova por resumo, sem data completa, ou em um único ano;
  bronze = nenhuma edição anterior a 2026 provada.
Edição de programa que não é para OSC (pessoa física, escola, universitário) não conta."""
import json, re, collections, unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "dados/coleta_3_anos"
HOJE = date(2026, 10, 3)
INI = date(2023, 10, 3)
NAO_OSC = ("cooperar para transformar", "mestras e mestres", "já é", "black stem", "marielle franco", "inspirar", "liga steam", "campus mobile")
# Âncoras que juntam programas diferentes: o livro só recebe as edições do PROGRAMA a que ele se refere (regex no nome do livro →
# trecho do programa/título da edição). Âncora que não está aqui vale por inteiro para todos os seus livros.
MATCH = {
    "fundo-ecos": [(r"ecos", r"fundo ecos"), (r"cargill", r"cargill"), (r"arena|paps|\bpas\b", r"salvador arena"), (r"maria em", r"maria em")],
    "bndes": [(r"periferias", r"periferias")],
    "funarte": [(r"mestras|mestres", r"mestras"), (r"difus|pixinguinha", r"difus")],
    "minc-editais": [(r"micsul", r"micsul"), (r"biblioteca comunit", r"biblioteca"), (r"pont[õo]es|cultura viva", r"cultura viva")],
    "pronon-pronas": [(r"pronon", r"pronon"), (r"pronas", r"pronas")],
    "mdhc-chamamentos": [(r"mdhc - editais de direitos humanos|mdhc / conanda", r".")],
    "mds": [(r"cozinha", r"cozinha")],
    "bnb": [(r"banco do nordeste", r".")],
    "fundo-brasil": [(r"edital geral|vozes por direitos|democracia e direitos|fortalecendo direitos", r"edital geral")],
    "rouanet-editais-minc": [], "mapa-cultural": [], "fapesp-pesquisa": [], "receita-justica": [], "fnma-clima": [],
}
NAO_MAPEADO = {"fnca": [("curadoria-010", "mdhc-chamamentos")]}
STOP = {"projeto", "projetos", "programa", "edital", "editais", "fundo", "fundação", "instituto", "ministério", "nacional", "oportunidade",
        "chamamento", "chamada", "público", "pública", "social", "sociais", "brasil", "ações", "apoio", "para", "entidades"}


def norm(s):
    return unicodedata.normalize("NFKD", (s or "").lower()).encode("ascii", "ignore").decode()


def toks(s):
    return {w[:5] for w in re.findall(r"[a-zà-ú]{5,}", norm(s)) if w not in {norm(x) for x in STOP}}


def d(s):
    try:
        return date.fromisoformat(s) if s else None
    except ValueError:
        return None


def ano_da(e):
    a = d(e.get("abertura")) or d(e.get("encerramento"))
    return a.year if a else (int(e["ano"]) if str(e.get("ano") or "").isdigit() else None)


def valida(e):
    """Dentro da janela de 3 anos e com página oficial + trecho."""
    if not (e.get("pagina_oficial") and e.get("trecho")):
        return False
    ab, en = d(e.get("abertura")), d(e.get("encerramento"))
    if en and en < INI:
        return False
    if ab and ab > HOJE:
        return False
    return bool(ab or en)


def osc(e):
    t = norm((e.get("programa") or "") + " " + (e.get("titulo") or ""))
    return not any(norm(x) in t for x in NAO_OSC)


def familia(anc, e):
    p = e.get("programa") or "unico"
    t = norm(e.get("titulo"))
    if anc == "fundo-ecos" and p in ("Fundação Cargill", "Fundação Salvador Arena"):
        for k in ("semeia", "nutrindo", "paps", "pas"):
            if re.search(r"\b" + k + r"\b", t) or (k == "paps" and "projetos sociais" in t) or (k == "pas" and "alimentacao saudavel" in t):
                return f"{p}|{k}"
    if anc == "mdhc-chamamentos":
        return "SNDCA/CONANDA"
    return p


def selo(anc, eds):
    eds = [e for e in eds if valida(e) and osc(e)]
    fam = collections.defaultdict(list)
    for e in eds:
        fam[familia(anc, e)].append(e)
    melhor, motivo = "bronze", "nenhuma edição anterior a 2026 provada em página oficial"
    anos_total = sorted({ano_da(e) for e in eds if ano_da(e)})
    for f, L in fam.items():
        anos = {ano_da(e) for e in L if ano_da(e)}
        ant = [e for e in L if (ano_da(e) or 9999) < 2026]
        forte = [e for e in ant if e.get("prova") == "literal"]
        if len(anos) >= 2 and forte:
            return "ouro", f"{f}: edições em {sorted(anos)} com prova literal", anos_total
        if ant:
            melhor = "prata"
            motivo = (f"{f}: edição anterior a 2026 só com prova por resumo (conferir o trecho)" if len(anos) >= 2 and not forte
                      else f"{f}: edição anterior a 2026 em um só ano ({sorted(anos)})")
    return melhor, motivo, anos_total


def casa(anc, book, e):
    if anc not in MATCH:
        return True
    nome = norm(book["nome"]); alvo = norm((e.get("programa") or "") + " " + (e.get("titulo") or ""))
    return any(re.search(norm(rb), nome) and re.search(norm(re_e), alvo) for rb, re_e in MATCH[anc])


def main():
    anc = json.loads((D / "ancoras_br.json").read_text(encoding="utf-8"))["ancoras"]
    fila = {x["id"]: x for x in json.loads((D / "fila_br.json").read_text(encoding="utf-8"))["fila"]}
    entrada, res, janelas = {}, {}, []
    cobertos = set()
    for a in anc:
        p = D / "anchor_out" / f"{a['ancora']}.json"
        if not p.exists():
            continue
        out = json.loads(p.read_text(encoding="utf-8"))
        eds = [e for e in (out.get("edicoes") or []) if valida(e)]
        for bid in a["livros"]:
            b = fila.get(bid)
            if not b:
                continue
            cobertos.add(bid)
            mine = [e for e in eds if casa(a["ancora"], b, e)]
            s, mot, anos = selo(a["ancora"], mine)
            entrada[bid] = {"edicoes": [{k: e.get(k) for k in ("ano", "titulo", "abertura", "encerramento", "pagina_oficial", "valor", "trecho")}
                                         | {"programa": e.get("programa"), "prova": e.get("prova") or "resumo_webfetch", "publico_osc": osc(e)} for e in mine],
                            "observacao": (out.get("observacao") or "")[:400] + (" | não verificado: " + "; ".join((out.get("nao_verificado") or [])[:3])[:400] if not mine else ""),
                            "ancora": a["ancora"]}
            res[bid] = {"nome": b["nome"], "ancora": a["ancora"], "selo_estimado": s, "motivo": mot, "anos_com_edicao": anos, "edicoes": len(mine)}
        for e in eds:
            en, ab = d(e.get("encerramento")), d(e.get("abertura"))
            if osc(e) and en and en >= HOJE:
                janelas.append({"ancora": a["ancora"], "programa": e.get("programa") or a["nome"], "titulo": e.get("titulo"), "abertura": e.get("abertura"),
                                "encerramento": e.get("encerramento"), "pagina_oficial": e.get("pagina_oficial"), "tipo": "aberta agora"})
    # livro de uma âncora que recebe também as edições de outra (mesmo promotor): curadoria-010 (MDHC/CONANDA) × chamamentos SNDCA/CONANDA
    ext = json.loads((D / "anchor_out/mdhc-chamamentos.json").read_text(encoding="utf-8"))
    eds_m = [e for e in ext.get("edicoes", []) if valida(e)]
    if "curadoria-010" in fila and eds_m:
        sl, mot, anos = selo("mdhc-chamamentos", eds_m)
        entrada["curadoria-010"] = {"edicoes": [{k: e.get(k) for k in ("ano", "titulo", "abertura", "encerramento", "pagina_oficial", "valor", "trecho")}
                                                | {"programa": e.get("programa"), "prova": e.get("prova") or "resumo_webfetch", "publico_osc": True} for e in eds_m],
                                    "observacao": "edições do chamamento SNDCA/CONANDA (MDHC)", "ancora": "mdhc-chamamentos"}
        res["curadoria-010"] = {"nome": fila["curadoria-010"]["nome"], "ancora": "mdhc-chamamentos", "selo_estimado": sl, "motivo": mot, "anos_com_edicao": anos, "edicoes": len(eds_m)}
    (D / "entrada").mkdir(exist_ok=True)
    (D / "entrada/br_2026-10-03.json").write_text(json.dumps(entrada, ensure_ascii=False, indent=1), encoding="utf-8")
    resto = [bid for bid in fila if bid not in cobertos]
    def cat(x):
        t = norm(x["nome"] + " " + (x.get("orgao") or ""))
        if re.search(r"municipi|prefeitura|consorcio|camara municipal|secretaria municipal|fundo municipal", t): return "municipal (pertence a Demais estados / Goiás; fora do Brasil nacional)"
        if re.search(r"credenciamento|credenciar", t): return "credenciamento (contratação de artistas/prestadores; sem programa recorrente de OSC)"
        if re.search(r"iberescena|ibermusicas|ibermedia|iberarquivos|dgartes|res artis|fondation|fellowship|convocatoria|protocolo luso", t): return "internacional / ibero-americano (vai para o prompt INT)"
        if re.search(r"observatorio|abcr|captadores|bussola|prosas|capitaai|piloto|espiao|duckduckgo", t): return "notícia ou agregador (serve para achar edição, não é o programa)"
        return "outros (notícia, edital isolado ou página institucional) — pesquisar na próxima passagem"
    triagem = collections.defaultdict(list)
    for bid in resto:
        triagem[cat(fila[bid])].append(bid)
    (D / "triagem_sem_ancora_br_2026-10-03.json").write_text(json.dumps({k: {"total": len(v), "ids": v} for k, v in triagem.items()}, ensure_ascii=False, indent=1), encoding="utf-8")
    print({k: len(v) for k, v in triagem.items()})
    por_selo = collections.Counter(v["selo_estimado"] for v in res.values())
    (D / "resultado_br_2026-10-03.json").write_text(json.dumps({
        "gerado_em": "2026-10-03", "livros_na_fila": len(fila), "livros_com_ancora": len(res), "livros_sem_ancora": len(resto),
        "selos_estimados_dos_livros_com_ancora": dict(por_selo), "janelas_abertas": sorted(janelas, key=lambda x: x["encerramento"]),
        "livros": res, "sem_ancora_ids": resto,
        "nota": "selo ESTIMADO por este script; o selo oficial é calculado por `python -m src.selo_livros` quando o módulo estiver no repositório"},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(res), dict(por_selo), len(resto), len(janelas))


if __name__ == "__main__":
    main()
