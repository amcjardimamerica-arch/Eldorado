"""IMPORTA A VERIFICAÇÃO DOS LIVROS PRATA E BRONZE (titular, 03/10/2026).

O verificador (com navegador, no IP do titular) trabalha um bloco por vez (docs/verificacao-livros/blocos/) e devolve
um arquivo resultados_<bloco>.jsonl — uma linha por livro. Este script CONFERE cada linha e a entrega à esteira
(estado/esteira/resultados_local.jsonl), que promove o selo (bronze → prata → ouro) e inclui as edições anteriores no
histórico (análise preditiva). Também guarda cada verificação como parecer do livro (dados/oportunidades/pareceres_livros/).
Uso: python3 scripts/importar_verificacao_livros.py <arquivo.jsonl> [mais arquivos...]
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
RESULTADOS = ROOT / "estado/esteira/resultados_local.jsonl"
PARECERES = ROOT / "dados/oportunidades/pareceres_livros"
AGREGADORES = re.compile(r"capitaai|prosas\.com|observatorio3setor|captadores\.org|editaisculturais|bit\.ly|google\.|facebook\.|instagram\.", re.I)
CAMPOS = {"livro", "etapa", "site_oficial", "url_edital", "confirmado_localmente", "edital_validado", "prazo_inscricao_inicio",
          "prazo_inscricao_fim", "doze", "dispensas", "edicoes", "decisao", "motivo", "fontes", "aprendizado", "modelo", "em"}


def conferir(r: dict, catalogo: set[str]) -> list[str]:
    from src.nucleo import has_prompt_injection
    erros = []
    if r.get("livro") not in catalogo:
        erros.append("livro inexistente")
    if r.get("etapa") not in ("bronze", "prata"):
        erros.append("etapa deve ser bronze ou prata")
    for k in ("site_oficial", "url_edital"):
        u = r.get(k)
        if u and (not str(u).startswith("https://") or AGREGADORES.search(str(u))):
            erros.append(f"{k} precisa ser endereço oficial em https (não agregador)")
    for ed in r.get("edicoes") or []:
        if ed.get("pagina_oficial") and AGREGADORES.search(str(ed["pagina_oficial"])):
            erros.append("edição com página de agregador")
    from src.criterio_selos import dispensa_valida
    for k, m in (r.get("dispensas") or {}).items():                       # 04/10: dispensa sem justificativa de não aplicabilidade
        if not dispensa_valida(m):
            erros.append(f"dispensa de '{k}' sem justificativa de que não se aplica (\"não informado\" é falta)")
    texto = json.dumps({k: v for k, v in r.items() if k in ("motivo", "aprendizado", "doze", "dispensas")}, ensure_ascii=False)
    if has_prompt_injection(texto):
        erros.append("texto com instrução dirigida a robô (possível injeção) — recusado")
    return erros


def run(arquivos: list[str]) -> dict:
    C = json.loads((ROOT / "biblioteca_alexandria/fontes/motores.json").read_text(encoding="utf-8"))
    ids = {x.get("id") for x in C.get("motores") or []}
    nomes = {x.get("id"): x for x in C.get("motores") or []}
    aceitos, recusados, pareceres = [], [], []
    for a in arquivos:
        for i, l in enumerate(Path(a).read_text(encoding="utf-8").splitlines(), 1):
            if not l.strip():
                continue
            try:
                r = json.loads(l)
            except ValueError:
                recusados.append({"arquivo": a, "linha": i, "erros": ["JSON inválido"]}); continue
            r = {k: v for k, v in r.items() if k in CAMPOS}
            erros = conferir(r, ids)
            if erros:
                recusados.append({"arquivo": a, "linha": i, "livro": r.get("livro"), "erros": erros}); continue
            r.setdefault("em", date.today().isoformat()); r.setdefault("modelo", "verificação dos livros (navegador do titular)")
            aceitos.append(r)
            x = nomes[r["livro"]]
            pareceres.append({"id": f"ver-{r['livro']}-{r['em']}", "titulo": x.get("programa"), "data": r["em"], "livro": r["livro"],
                              "livro_nome": x.get("nome_classificado"), "uf": x.get("uf"), "orgao": x.get("orgao"),
                              "bloco": f"{x.get('geo') or x.get('uf')} · {x.get('objeto_area') or 'Geral'}",
                              "estudo": "verificação dos livros prata e bronze (03/10)", "decisao": r.get("decisao") or f"verificado_{r['etapa']}",
                              "motivo": r.get("motivo"), "fonte_oficial": r.get("url_edital") or r.get("site_oficial")})
    if aceitos:
        RESULTADOS.parent.mkdir(parents=True, exist_ok=True)
        with RESULTADOS.open("a", encoding="utf-8") as f:
            for r in aceitos:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        PARECERES.mkdir(parents=True, exist_ok=True)
        arq = PARECERES / f"pareceres_{date.today().isoformat()}-verificacao-livros.json"
        ant = json.loads(arq.read_text(encoding="utf-8")).get("pareceres", []) if arq.exists() else []
        vistos = {p["id"] for p in ant}
        todos = ant + [p for p in pareceres if p["id"] not in vistos]
        arq.write_text(json.dumps({"gerado_em": date.today().isoformat(), "regra": __doc__.split("Uso:")[0].strip(), "total": len(todos),
                                   "pareceres": todos}, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"aceitos": len(aceitos), "recusados": recusados}


if __name__ == "__main__":
    r = run(sys.argv[1:])
    print(f"aceitos: {r['aceitos']} · recusados: {len(r['recusados'])}")
    for x in r["recusados"][:20]:
        print("  recusado:", x)
