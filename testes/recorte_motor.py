"""O motor como era, dentro da organização dos 43 motores (titular, 09/11/2026 — R50).

Os testes das páginas reais gravadas (testes/paginas/<motor>/) conferem as fontes que cada motor tinha. Na organização
dos 43 motores as fontes mudaram de lugar (a marca «veio do motor <id>») e os motores ganharam locais novos (a marca
«local novo»). O recorte devolve o motor com as fontes e os alvos que eram dele — onde quer que estejam agora — com o
léxico próprio dessas fontes, e o resto da configuração (acesso, leitura, programa, legislação) do motor de hoje.
"""
from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

PASTA = Path("eldorado/motores/canal/config")
HDR = re.compile(r"^\s*(\[\[?)\s*([A-Za-z0-9_.\-]+)\s*(\]\]?)\s*(#.*)?$")
VEIO = re.compile(r"veio do motor ([\w\-]+)")


def dono(antigo: str, pasta: Path = PASTA) -> Path:
    """O arquivo do motor (o próprio, ou o que o reúne pelos nomes anteriores)."""
    if (pasta / f"{antigo}.toml").exists():
        return pasta / f"{antigo}.toml"
    for p in sorted(pasta.glob("*.toml")):
        if antigo in tomllib.loads(p.read_text(encoding="utf-8"))["motor"].get("nomes_anteriores", []):
            return p
    raise FileNotFoundError(antigo)


def _blocos(texto: str) -> list[tuple[str | None, list[str], list[str]]]:
    """(seção, linhas, comentários logo antes do cabeçalho)."""
    brutos, nome, cur = [], None, []
    for ln in texto.split("\n"):
        m = HDR.match(ln)
        if m:
            top = m.group(2).split(".")[0]
            if nome in ("fonte", "alvo") and top == nome and "." in m.group(2):
                cur.append(ln)
                continue
            brutos.append([nome, cur])
            nome, cur = top, [ln]
        else:
            cur.append(ln)
    brutos.append([nome, cur])
    out = []
    for i, (nome, ls) in enumerate(brutos):
        antes = []
        if i:
            prev = brutos[i - 1][1]
            while prev and (prev[-1].strip().startswith("#") or not prev[-1].strip()):
                antes.insert(0, prev.pop())
        out.append((nome, ls, antes))
    return out


def _marca(antes: list[str], ls: list[str]) -> tuple[str | None, bool]:
    """(o motor de onde a fonte veio, se é um local novo de 09/11)."""
    texto = "\n".join(antes + ls[:2])
    m = VEIO.search(texto)
    return (m.group(1) if m else None), ("local novo (" in texto or "EM OBSERVAÇÃO" in texto)


def _valor(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, list):
        return "[" + ", ".join(_valor(x) for x in v) + "]"
    return "{ " + ", ".join(f"{k} = {_valor(x)}" for k, x in v.items()) + " }"


def recorte(antigo: str, pasta: Path = PASTA) -> str:
    """O texto TOML do motor com as fontes e os alvos que eram dele."""
    p = dono(antigo, pasta)
    proprio = p.stem == antigo
    fontes, alvos, motor, outras, lexico = [], [], [], [], None
    for arq in sorted(pasta.glob("*.toml")):
        for nome, ls, antes in _blocos(arq.read_text(encoding="utf-8")):
            if nome in ("fonte", "alvo"):
                veio, novo = _marca(antes, ls)
                if not (veio == antigo or (arq == p and proprio and veio is None and not novo)):
                    continue
                d = tomllib.loads("\n".join(ls))
                lx = (d.get(nome) or [{}])[0].get("lexico") if nome == "fonte" else None
                if lx is not None and lexico is None:
                    lexico = lx
                (fontes if nome == "fonte" else alvos).append([x for x in ls if not re.match(r"\s*lexico\s*=", x)])
            elif arq != p or nome is None:
                continue
            elif nome == "motor":
                motor = [re.sub(r"^id\s*=.*$", f'id = "{antigo}"', x) for x in ls]
            elif nome in ("programa", "legislacao", "normas", "extracao"):
                veio, _ = _marca(antes, [])
                if veio is None or veio == antigo:
                    outras.append(ls)
            elif not (nome == "lexico" and False):
                outras.append(ls)
    linhas = motor + [""]
    for b in fontes + alvos + outras:
        linhas += b + [""]
    texto = "\n".join(linhas) + "\n"
    if lexico is not None:
        texto = re.sub(r"(?ms)^\[lexico\]\n.*?(?=^\[|\Z)", "", texto)
        texto += "\n[lexico]\n" + "\n".join(f"{k} = {_valor(v)}" for k, v in lexico.items()) + "\n"
    return texto
