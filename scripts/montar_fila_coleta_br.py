"""Fila de coleta dos 3 anos — livros do Brasil (nacional). Reconstruída do catálogo biblioteca_alexandria/fontes/motores.json
(03/10/2026): a fila oficial (dados/coleta_3_anos/fila_br.json do módulo selo_livros) não estava no GitHub quando esta sessão
rodou. Os ids são os do catálogo; se a fila oficial existir, ela manda e este arquivo serve só de conferência."""
import json, collections, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "biblioteca_alexandria/fontes/motores.json"
SAIDA = ROOT / "dados/coleta_3_anos/fila_br.json"
ORDEM_TIPO = ["edital", "oportunidade_mapeada", "fundo", "incentivo_fiscal", "doacao_patrocinio", "destinacao_judicial", "emenda", "outro",
              "repositorio_de_oportunidade"]


def bloco(m):
    uf = (m.get("uf") or "").upper(); n = m.get("nivel")
    if n == "internacional" or m.get("tipo") == "grant":
        return "INT"
    if uf == "GO" or "Goiás" in (m.get("orgao") or ""):
        return "GO"
    return "BR" if uf in ("", "BR") else "OUTROS"


def anos_anteriores(m):
    anos = set()
    for h in (m.get("historico") or []):
        for k in ("publicado_em", "inicio", "fim", "ano"):
            mm = re.match(r"(20\d{2})", str(h.get(k) or ""))
            if mm and 2023 <= int(mm.group(1)) <= 2025:
                anos.add(mm.group(1))
    return sorted(anos)


def main():
    ms = json.loads(CAT.read_text(encoding="utf-8"))["motores"]
    fila = []
    for m in ms:
        if bloco(m) != "BR":
            continue
        ant = anos_anteriores(m)
        fila.append({"id": m["id"], "nome": (m.get("programa") or m.get("nome") or "")[:200], "orgao": m.get("orgao"), "tipo": m.get("tipo"),
                     "familia": m.get("familia"), "pagina": m.get("pagina"), "anos_anteriores_no_catalogo": ant,
                     "selo_estimado": "prata" if ant else "bronze",
                     "falta": "edição anterior a 2026 provada em página oficial com data de inscrição" if not ant else "segundo ano / página oficial"})
    fila.sort(key=lambda x: (ORDEM_TIPO.index(x["tipo"]) if x["tipo"] in ORDEM_TIPO else 99, x["selo_estimado"] != "bronze", x["nome"]))
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps({"gerado_em": "2026-10-03", "origem": "reconstruída do catálogo (a fila oficial não estava no GitHub)",
                                 "total": len(fila), "por_tipo": dict(collections.Counter(x["tipo"] for x in fila)), "fila": fila},
                                ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(fila), dict(collections.Counter(x["tipo"] for x in fila)))


if __name__ == "__main__":
    main()
