"""O inventário do sistema (titular, 22/10/2026): todo arquivo, do primeiro ao último no caminho do funcionamento, com a
finalidade, as ligações (de quem depende, quem o usa, quem o aciona), os eventos que grava, os testes que o cobrem e a
situação. Gerado a partir do próprio código, da passagem e da configuração; é o catálogo que a medição lê
(config/arquivos.json) e a base do monitoramento em tempo real. Os arquivos previstos no projeto e ainda não
construídos entram na posição em que vão funcionar, marcados "a construir".
"""
from __future__ import annotations

import ast
import json
import re
import tomllib
from pathlib import Path
from typing import Any

# o caminho do funcionamento: (etapa, regra do caminho)
ETAPAS = [
    ("01 Operação: o que acorda o sistema", [r"^\.github/workflows/eldorado\.yml$", r"^scripts/", r"nucleo/comandos\.py$"]),
    ("02 Núcleo: contratos, eventos e gravação", [r"base/nucleo/(?!comandos|inventario)"]),
    ("03 Bancos", [r"^eldorado/banco/"]),
    ("04 Execução: workflow, executor, fila e governador", [r"base/fluxo/", r"cerebro/governador\.py$", r"^workflows/"]),
    ("05 Cérebro decide: fila do sistema e acionamento", [r"cerebro/(decisao|fila|regencia)\.py$", r"^config/(agenda|modulos)\.toml$"]),
    ("06 Coleta: os motores e o canivete suíço", [r"^eldorado/motores/(canal|acesso|leitura|descoberta)/", r"^config/motores_previstos\.toml$"]),
    ("07 Pertinência e missão", [r"cerebro/pertinencia\.py$", r"base/missao/", r"^config/missao/"]),
    ("08 Cartório · etapas 1 e 2 (recepção e certificação)", [r"cartorio/(indice|passaporte|site_oficial|certificacao|selos|cartorio)\.py$"]),
    ("09 Cartório · validação (auditoria e arquivo)", [r"cartorio/auditoria\.py$"]),
    ("10 Cartório · etapa 3 (a rede neural encaminha)", [r"cerebro/encaminhamento\.py$", r"motores/pilotos/"]),
    ("11 Cartório · etapa 5 (análise externa)", [r"cartorio/analise_externa\.py$", r"base/verificacao/"]),
    ("12 Farol e transferência", [r"base/transferencia/"]),
    ("13 Aprender e medir", [r"cerebro/(aprendizado|completude|medicao|rede|regras|inventario)\.py$"]),
    ("14 Análise e painel", [r"base/analise/", r"base/painel/"]),
    ("15 Originais e Drive", [r"banco/(fotografia|originais)"]),
    ("16 Migração do Eldorado0 (temporária)", [r"base/migracao/"]),
]
SUBSTITUIDOS = {   # previstos no projeto; a função já existe em outro arquivo
    "eldorado/base/investigacao/investigacao.py": "eldorado/base/cerebro/encaminhamento.py e eldorado/motores/pilotos/interceptador.py",
    "eldorado/base/verificacao/verificacao.py": "eldorado/base/cartorio/analise_externa.py",
    "eldorado/base/verificacao/lote.py": "eldorado/base/cartorio/analise_externa.py",
    "eldorado/base/verificacao/importacao.py": "eldorado/base/cartorio/analise_externa.py",
    "eldorado/base/verificacao/relatorio_faltas.py": "eldorado/base/cartorio/analise_externa.py (o que falta vai no lote)",
    "eldorado/base/cartorio/linha.py": "eldorado/motores/pilotos/interceptador.py (a linha de produção virou o Interceptador)",
    ".github/workflows/passagem.yml": ".github/workflows/eldorado.yml (funcionamento permanente)",
    ".github/workflows/pilotos.yml": ".github/workflows/eldorado.yml (os pilotos rodam dentro do funcionamento permanente)",
}
DESLIGADOS_POR_DESENHO = {"eldorado/motores/leitura/universal.py": "reserva para tipos sem leitor (liga-se na configuração)",
                          "eldorado/motores/acesso/rotas_alternativas.py": "degraus de reserva (Tor e leitor público), até o teste real"}


def _etapa(caminho: str) -> str:
    for nome, regras in ETAPAS:
        if any(re.search(r, caminho) for r in regras):
            return nome
    return "17 Outros"


def _modulo(p: Path) -> str:
    return ".".join(p.with_suffix("").parts).replace(".__init__", "")


def analisar(raiz: Path) -> dict[str, dict[str, Any]]:
    arqs = sorted(p.relative_to(raiz) for p in (raiz / "eldorado").rglob("*.py") if "__pycache__" not in p.parts)
    por_mod = {_modulo(p): str(p) for p in arqs}
    info: dict[str, dict[str, Any]] = {}
    for p in arqs:
        s = (raiz / p).read_text(encoding="utf-8")
        t = ast.parse(s)
        deps: set[str] = set()
        for n in ast.walk(t):
            if isinstance(n, ast.ImportFrom):
                base = _modulo(p).split(".")
                if p.name != "__init__.py":
                    base = base[:-1]
                alvo = ".".join(base[:len(base) - n.level + 1] + ([n.module] if n.module else [])) if n.level else (n.module or "")
                for a in n.names:
                    for c in (f"{alvo}.{a.name}", alvo):
                        if c in por_mod and por_mod[c] != str(p):
                            deps.add(por_mod[c])
                            break
        info[str(p)] = {"arquivo": str(p), "linhas": len(s.splitlines()), "finalidade": ((ast.get_docstring(t) or "").strip().split("\n") or [""])[0][:200],
                        "depende_de": sorted(deps), "eventos": sorted(set(re.findall(r'emitir\(\s*"([a-z_]+\.[a-z_]+)"', s))), "acionado_por": []}
    for k, v in info.items():
        v["usado_por"] = sorted(o for o, w in info.items() if k in w["depende_de"])
    testes = {t.name: t.read_text(encoding="utf-8") for t in sorted((raiz / "testes").glob("test_*.py"))}
    for k, v in info.items():
        m = _modulo(Path(k))
        v["testes"] = [n for n, s in testes.items() if m in s]
    arq = lambda mod: mod.replace(".", "/") + ".py"  # noqa: E731
    wf = tomllib.loads((raiz / "workflows/passagem.toml").read_text(encoding="utf-8"))
    for i, n in enumerate(wf["no"], 1):
        alvo = arq(n["tipo"].split(":")[0])
        if alvo in info:
            info[alvo]["acionado_por"].append(f"passagem, nó {i} «{n['id']}»")
        for val in (n.get("parametros") or {}).values():
            if isinstance(val, str) and val.startswith("eldorado.") and ":" in val and arq(val.split(":")[0]) in info:
                info[arq(val.split(":")[0])]["acionado_por"].append(f"passagem, nó «{n['id']}» (parâmetro)")
    for m in tomllib.loads((raiz / "config/modulos.toml").read_text(encoding="utf-8")).get("modulo", []):
        alvo = arq(m["classe"].split(":")[0])
        if alvo in info:
            info[alvo]["acionado_por"].append(f"config/modulos.toml ({Path(m['parametros']['configuracao']).stem})")
    info["eldorado/base/nucleo/comandos.py"]["acionado_por"].append(".github/workflows/eldorado.yml (eldorado permanente)")
    for v in info.values():
        v["acionado_por"] = sorted(set(v["acionado_por"]))
        if v["arquivo"].endswith("__init__.py"):
            v["situacao"] = "pacote"
        elif v["arquivo"] in DESLIGADOS_POR_DESENHO:
            v["situacao"] = "desligado por desenho"
            v["observacao"] = DESLIGADOS_POR_DESENHO[v["arquivo"]]
        elif not v["usado_por"] and not v["acionado_por"]:
            v["situacao"] = "desligado (ninguém o usa nem o aciona)"
        else:
            v["situacao"] = "em funcionamento"
    return info


def _ordenar(itens: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Na ordem das etapas; dentro de cada etapa, cada arquivo depois daqueles de que depende."""
    saida: list[dict[str, Any]] = []
    for nome, _ in ETAPAS + [("17 Outros", [])]:
        grupo = {x["arquivo"]: x for x in itens if x["etapa"] == nome}
        feitos: set[str] = set()
        while grupo:
            prontos = sorted(k for k, x in grupo.items() if not (set(x.get("depende_de", [])) & (set(grupo) - {k})))
            for k in prontos or [sorted(grupo)[0]]:
                saida.append(grupo.pop(k))
                feitos.add(k)
    for i, x in enumerate(saida, 1):
        x["ordem"] = i
    return saida


def gerar(raiz: str | Path = ".") -> dict[str, Any]:
    raiz = Path(raiz)
    info = analisar(raiz)
    anterior = {a["arquivo"]: a for a in json.loads((raiz / "config/arquivos.json").read_text(encoding="utf-8")).get("arquivos", [])} \
        if (raiz / "config/arquivos.json").exists() else {}
    itens = []
    for k, v in info.items():
        a = anterior.get(k, {})
        itens.append({**v, "etapa": _etapa(k), "parte": a.get("parte") or ("MOTORES" if "/motores/" in k else "BANCO" if "/banco/" in k else "BASE"),
                      "componente": a.get("componente") or _etapa(k)[3:], "ligacoes": v["depende_de"], "critico": bool(a.get("critico")),
                      "metrica": a.get("metrica") or "testes verdes e uso registrado"})
    for k in (".github/workflows/eldorado.yml", ".github/workflows/painel.yml", "scripts/gravar.sh", "workflows/passagem.toml", "config/agenda.toml",
              "config/modulos.toml", "config/motores_previstos.toml"):
        if (raiz / k).exists():
            itens.append({"arquivo": k, "etapa": _etapa(k), "parte": "OPERACAO", "componente": "Operação e configuração", "ligacoes": [], "critico": True,
                          "metrica": "o sistema roda sem intervenção", "finalidade": "", "depende_de": [], "usado_por": [], "acionado_por": [],
                          "eventos": [], "testes": [], "linhas": len((raiz / k).read_text(encoding="utf-8").splitlines()), "situacao": "em funcionamento"})
    for k, a in anterior.items():                                   # previstos no projeto e ainda não construídos
        if k not in info and not (raiz / k).exists() and not k.endswith("/") and not any(x["arquivo"] == k for x in itens):
            situacao = f"substituído por {SUBSTITUIDOS[k]}" if k in SUBSTITUIDOS else "a construir"
            itens.append({**a, "arquivo": k, "etapa": _etapa(k), "situacao": situacao, "depende_de": [], "usado_por": [], "acionado_por": [],
                          "eventos": [], "testes": [], "linhas": 0, "finalidade": a.get("finalidade") or a.get("metrica", "")})
    motores = tomllib.loads((raiz / "config/motores_previstos.toml").read_text(encoding="utf-8"))["motor"] \
        if (raiz / "config/motores_previstos.toml").exists() else []
    return {"versao": 2, "arquivos": _ordenar(itens), "motores": motores}


def mapa(cat: dict[str, Any]) -> str:
    import collections
    linhas = ["# Mapa do sistema Eldorado", "", "Gerado pelo comando `eldorado inventario` a partir do código, da passagem e da configuração. "
              "É o catálogo da medição e a base do monitoramento em tempo real.", ""]
    sit = collections.Counter(a["situacao"] for a in cat["arquivos"])
    linhas += ["## Situação dos arquivos", "", "| Situação | Arquivos |", "|---|---|"] + [f"| {k} | {v} |" for k, v in sit.most_common()] + [""]
    etapa = None
    for a in cat["arquivos"]:
        if a["etapa"] != etapa:
            etapa = a["etapa"]
            linhas += ["", f"## {etapa}", "", "| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |",
                       "|---|---|---|---|---|---|---|"]
        uso = "; ".join(a.get("acionado_por") or []) or ", ".join(Path(x).stem for x in a.get("usado_por") or [])
        linhas.append(f"| {a['ordem']} | `{a['arquivo']}` | {a.get('finalidade', '')[:110]} | {a['situacao']} | "
                      f"{', '.join(Path(x).stem for x in a.get('depende_de') or [])} | {uso[:120]} | {len(a.get('testes') or [])} |")
    m = cat["motores"]
    linhas += ["", "## Os 47 motores (45 regulares e 2 pilotos)", "", "| # | Tipo | Motor (Eldorado0) | Nome | Motor novo | Situação | Observação |",
               "|---|---|---|---|---|---|---|"]
    linhas += [f"| {i} | {x['tipo']} | {x['id']} | {x['nome']} | {x['motor_novo'] or '—'} | {x['situacao']} | {x['observacao']} |" for i, x in enumerate(m, 1)]
    return "\n".join(linhas) + "\n"
