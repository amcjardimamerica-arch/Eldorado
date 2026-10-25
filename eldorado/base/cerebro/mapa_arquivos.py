"""O mapa REAL dos arquivos do sistema (titular, 24/10/2026: nada decorativo nem exemplificativo).

Os nós são todos os arquivos do sistema (o código, as configurações, os workflows, os motores um a um, os dois bancos), e
as ligações são extraídas do que a produção executa:
  importa     a importação no código (a árvore de cada arquivo, com as importações relativas resolvidas)
  aciona      os fluxos do GitHub chamando os comandos (eldorado <comando>) e os scripts
  fluxo       os nós dos workflows internos (passagem.toml), na ordem em que rodam
  configura   o registro dos módulos (modulos.toml) ligando cada motor ao motor genérico
  grava       os eventos que o arquivo emite e o banco que eles gravam (o catálogo do gravador)
  le          as tabelas que o arquivo lê (a consulta SQL), e o banco delas
A validação de cada arquivo: se é ALCANÇADO a partir do que a produção executa (os fluxos do GitHub), se tem teste, e
(o monitoramento) se rodou sem erro e se cumpre a finalidade.
"""
from __future__ import annotations

import ast
import re
import tomllib
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parents[3]
BANCOS = {"biblioteca": "dados/biblioteca.db", "cerebro": "dados/cerebro.db"}


def _parte(p: str) -> tuple[str, str]:
    """A parte (BASE, MOTORES, BANCO) e o componente (a pasta; cada motor é o seu próprio componente)."""
    if p.startswith("dados/"):
        return "BANCO", "bancos"
    if p.startswith("eldorado/banco/"):
        return "BANCO", p.split("/")[2].removesuffix(".py")
    if p.startswith("eldorado/motores/canal/config/"):
        return "MOTORES", "motor " + Path(p).stem
    if p.startswith("eldorado/motores/"):
        return "MOTORES", p.split("/")[2].removesuffix(".py")
    if p.startswith("eldorado/base/"):
        return "BASE", p.split("/")[2].removesuffix(".py")
    if p.startswith(".github/") or p.startswith("scripts/"):
        return "BASE", "produção (fluxos e scripts)"
    if p.startswith("workflows/"):
        return "BASE", "workflows internos"
    return "BASE", "configuração"


def _modulo_para_arquivo(mod: str) -> str | None:
    base = RAIZ / mod.replace(".", "/")
    for c in (base.with_suffix(".py"), base / "__init__.py"):
        if c.exists():
            return c.relative_to(RAIZ).as_posix()
    return None


def _importacoes(arq: Path) -> set[str]:
    pacote = ".".join(arq.relative_to(RAIZ).with_suffix("").parts[:-1])
    try:
        arvore = ast.parse(arq.read_text(encoding="utf-8"))
    except SyntaxError:
        return set()
    alvos = set()
    for n in ast.walk(arvore):
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name.startswith("eldorado"):
                    alvos.add(a.name)
        elif isinstance(n, ast.ImportFrom):
            if n.level:
                partes = pacote.split(".")
                base = ".".join(partes[: len(partes) - n.level + 1])
                mod = f"{base}.{n.module}" if n.module else base
            else:
                mod = n.module or ""
            if not mod.startswith("eldorado"):
                continue
            alvos.add(mod)
            for a in n.names:                                    # from x import modulo
                alvos.add(f"{mod}.{a.name}")
    saida = set()
    for m in alvos:
        f = _modulo_para_arquivo(m)
        if f and f != arq.relative_to(RAIZ).as_posix():
            saida.add(f)
    return saida


def montar() -> dict[str, Any]:
    from ..nucleo.eventos import CATALOGO
    nos: dict[str, dict[str, Any]] = {}
    arestas: set[tuple[str, str, str, str]] = set()

    def no(p: str, **extra) -> None:
        if p not in nos:
            parte, comp = _parte(p)
            nos[p] = {"id": p, "parte": parte, "componente": comp, **extra}

    def liga(a: str, b: str, tipo: str, rotulo: str = "") -> None:
        if a != b:
            no(a)
            no(b)
            arestas.add((a, b, tipo, rotulo))
    codigo = sorted(p for p in (RAIZ / "eldorado").rglob("*.py") if "__pycache__" not in p.parts)
    for p in codigo:
        no(p.relative_to(RAIZ).as_posix())
    for p in codigo:
        r = p.relative_to(RAIZ).as_posix()
        for alvo in _importacoes(p):
            liga(r, alvo, "importa")
    # o banco: os eventos que cada arquivo emite (o gravador grava no banco do catálogo) e as tabelas que ele lê
    tabela_banco: dict[str, str] = {}
    for b, f in BANCOS.items():
        esq = RAIZ / ("eldorado/banco/biblioteca/esquema.py" if b == "biblioteca" else "eldorado/banco/cerebro_db/esquema.py")
        for t in re.findall(r"CREATE (?:VIRTUAL )?TABLE (?:IF NOT EXISTS )?([a-z_]+)", esq.read_text(encoding="utf-8")):
            tabela_banco.setdefault(t, f)
        for t in [x for x in re.findall(r"CREATE TABLE IF NOT EXISTS ([a-z_]+)", (RAIZ / "eldorado/motores/canal/estado.py").read_text(encoding="utf-8"))]:
            tabela_banco.setdefault(t, BANCOS["cerebro"])
        no(f, tabelas=[])
        liga(esq.relative_to(RAIZ).as_posix(), f, "define", "o esquema")
    for t, f in tabela_banco.items():
        nos[f].setdefault("tabelas", []).append(t)
    emissao = re.compile(r"""(?:emitir|_entregar)\(\s*["']([a-z_]+\.[a-z_.]+)["']""")
    leitura = re.compile(r"\b(?:FROM|JOIN|INTO|UPDATE)\s+([a-z_]+)\b")
    for p in codigo:
        r, txt = p.relative_to(RAIZ).as_posix(), p.read_text(encoding="utf-8")
        for tipo in sorted(set(emissao.findall(txt))):
            for alvo in CATALOGO.get(tipo, ()):
                liga(r, BANCOS.get(alvo.banco, BANCOS["biblioteca"]), "grava", tipo)
        lidas = {t for t in leitura.findall(txt) if t in tabela_banco}
        for t in sorted(lidas):
            if r not in ("eldorado/base/nucleo/gravador.py",):
                liga(r, tabela_banco[t], "le", t)
    liga("eldorado/base/nucleo/gravador.py", BANCOS["biblioteca"], "grava", "todo evento do catálogo")
    liga("eldorado/base/nucleo/gravador.py", BANCOS["cerebro"], "grava", "todo evento do catálogo")
    # os workflows internos: cada nó aponta para a função que roda, na ordem
    for wf in sorted((RAIZ / "workflows").glob("*.toml")):
        w = wf.relative_to(RAIZ).as_posix()
        no(w)
        anterior = None
        for n in tomllib.loads(wf.read_text(encoding="utf-8")).get("no", []):
            mod = n["tipo"].split(":")[0]
            f = _modulo_para_arquivo(mod)
            if not f:
                continue
            liga(w, f, "fluxo", n["id"])
            if anterior and anterior[0] != f:
                liga(anterior[0], f, "sequencia", f"{anterior[1]} → {n['id']}")
            anterior = (f, n["id"])
    # o registro dos módulos: cada motor (a sua configuração) ligado ao motor genérico
    mod_toml = RAIZ / "config/modulos.toml"
    liga("config/modulos.toml", "eldorado/base/nucleo/registro.py", "configura", "os módulos registrados")
    for m in tomllib.loads(mod_toml.read_text(encoding="utf-8")).get("modulo", []):
        f = _modulo_para_arquivo(m["classe"].split(":")[0])
        cfg = (m.get("parametros") or {}).get("configuracao")
        if f:
            liga("config/modulos.toml", f, "configura", m["classe"].split(":")[1])
        if cfg and f:
            liga("config/modulos.toml", cfg, "configura", Path(cfg).stem)
            liga(cfg, f, "configura", "a configuração do motor")
    for p in sorted((RAIZ / "eldorado/motores/canal/config").glob("*.toml")):
        no(p.relative_to(RAIZ).as_posix())
    for c in sorted((RAIZ / "config").glob("*.*")):
        no(c.relative_to(RAIZ).as_posix())
    # a produção: os fluxos do GitHub chamando os comandos e os scripts
    cmd = re.compile(r"\beldorado ([a-z][a-z-]+)")
    for y in sorted((RAIZ / ".github/workflows").glob("*.yml")):
        ry, txt = y.relative_to(RAIZ).as_posix(), y.read_text(encoding="utf-8")
        no(ry, entrada=True)
        for c in sorted(set(cmd.findall(txt))):
            liga(ry, "eldorado/base/nucleo/comandos.py", "aciona", f"eldorado {c}")
        for s in sorted(set(re.findall(r"scripts/[a-z_]+\.(?:sh|py)", txt))):
            liga(ry, s, "aciona", s)
            if s == "scripts/instalar.sh":
                liga(s, "scripts/instalar_bibliotecas.py", "aciona", "as bibliotecas")
        for c in sorted(set(re.findall(r"config/[a-z_]+\.(?:toml|json)", txt))):
            if (RAIZ / c).exists():
                liga(ry, c, "le", "configuração")
        if "workflows/" in txt or "permanente" in txt:
            liga(ry, "workflows/passagem.toml", "aciona", "a passagem")
    for s in sorted((RAIZ / "scripts").glob("*.*")):
        no(s.relative_to(RAIZ).as_posix())
    # as referências pelo nome ("eldorado.x.y:Classe"), nos parâmetros dos workflows, nas configurações e no código
    ref = re.compile(r"""["'](eldorado(?:\.[a-z_]+)+):[A-Za-z_]+["']""")
    for p in [*codigo, *(RAIZ / "workflows").glob("*.toml"), *(RAIZ / "config").glob("*.toml")]:
        for mod in set(ref.findall(p.read_text(encoding="utf-8"))):
            f = _modulo_para_arquivo(mod)
            if f:
                liga(p.relative_to(RAIZ).as_posix(), f, "configura", "carregado pelo nome")
    # comandos e arquivos lidos por caminho literal (config/..., workflows/...)
    lit = re.compile(r"""["'](config/[a-z_]+\.(?:toml|json|txt)|workflows/[a-z_]+\.toml)["']""")
    for p in codigo:
        for c in set(lit.findall(p.read_text(encoding="utf-8"))):
            if (RAIZ / c).exists():
                liga(p.relative_to(RAIZ).as_posix(), c, "le", "configuração")
    # alcançável a partir da produção
    adj: dict[str, set[str]] = defaultdict(set)
    for a, b, tipo, _ in arestas:
        if tipo in ("importa", "aciona", "fluxo", "configura", "sequencia"):
            adj[a].add(b)
        if tipo == "le" and b.startswith(("config/", "workflows/")) or (tipo == "le" and a.startswith(".github/")):
            adj[a].add(b)
    vistos, fila = set(), deque(p for p, n in nos.items() if n.get("entrada"))
    while fila:
        x = fila.popleft()
        if x in vistos:
            continue
        vistos.add(x)
        fila.extend(adj.get(x, ()))
    for p in list(vistos):                                        # o pacote de um arquivo alcançado também é
        d = Path(p).parent
        while str(d) not in (".", ""):
            if (RAIZ / d / "__init__.py").exists():
                vistos.add((d / "__init__.py").as_posix())
            d = d.parent
    testados = set()
    for t in (RAIZ / "testes").glob("test_*.py"):
        testados |= _importacoes(t)
    for p, n in nos.items():
        n["alcancado"] = p in vistos or p.startswith("dados/")
        n["testado"] = p in testados
        n["existe"] = (RAIZ / p).exists()
    return {"nos": sorted(nos.values(), key=lambda n: (n["parte"], n["componente"], n["id"])),
            "arestas": [{"de": a, "para": b, "tipo": t, "rotulo": r} for a, b, t, r in sorted(arestas)]}


# ------------------------------------------------------------------ o monitoramento de cada arquivo
PIOR = {"r": 3, "a": 2, "c": 1, "v": 0}


def medir(dados: Path = Path("dados"), mapa: dict[str, Any] | None = None) -> dict[str, Any]:
    """O ponto (rodou sem erro quando chamado), o círculo (a finalidade) e as ligações de cada arquivo, nas últimas 24 h,
    pelo que o sistema registrou (os passos dos workflows, as execuções dos motores, os achados aceitos, os bancos)."""
    import json
    import sqlite3
    from datetime import datetime, timedelta, timezone
    mapa = mapa or montar()
    agora = datetime.now(timezone.utc)
    h24, d14, h48 = ((agora - timedelta(hours=h)).isoformat() for h in (24, 24 * 14, 48))
    cer = sqlite3.connect(f"file:{dados / 'cerebro.db'}?mode=ro", uri=True)
    bib = sqlite3.connect(f"file:{dados / 'biblioteca.db'}?mode=ro", uri=True)
    nos = {n["id"]: n for n in mapa["nos"]}
    arquivo_do_no = {a["rotulo"]: a["para"] for a in mapa["arestas"] if a["tipo"] == "fluxo"}
    ponto: dict[str, str] = {}
    circ: dict[str, str] = {}
    motivo: dict[str, str] = {}
    # os nós dos workflows: o resultado de cada passo nas últimas 24 h
    por_no: dict[str, list[tuple[str, str | None]]] = defaultdict(list)
    # os últimos 50 passos de cada nó (responde em minutos; a janela de 24 h deixava uma falha corrigida vermelha por um dia)
    for no_id, estado, saida, em_ in cer.execute("SELECT no, estado, saida, em FROM (SELECT no, estado, saida, em, ROW_NUMBER() OVER "
                                            "(PARTITION BY no ORDER BY em DESC) AS k FROM execucao_passo WHERE estado IN ('concluido', 'falhou')) "
                                            "WHERE k <= 10"):   # o comportamento recente (25/10/2026: a janela de 50 contava falhas corrigidas por dias)
        por_no[no_id].append((estado, saida, em_))
    vermelhos_do_erro: dict[str, str] = {}
    for no_id in list(por_no):                                    # o comportamento das últimas 24 h (até 10 passos); sem passo
        recentes = [x for x in por_no[no_id] if (x[2] or "") >= h24]    # recente, o histórico
        if recentes:
            por_no[no_id] = recentes
    for no_id, lst in por_no.items():
        f = arquivo_do_no.get(no_id)
        ok = sum(1 for e, _s, _em in lst if e == "concluido")
        falhas = [s for e, s, _em in lst if e == "falhou"]
        total = ok + len(falhas)
        for s in falhas:
            try:
                d = json.loads(s or "{}") or {}
            except ValueError:
                d = {}
            for a in (d.get("arquivos_do_erro") or []):
                vermelhos_do_erro.setdefault(a, f"no rastro de um erro do nó {no_id}: {str(d.get('erro') or '')[:120]}")
        if f and total:
            taxa = ok / total
            c = "v" if taxa >= .95 else "a" if taxa >= .8 else "r"
            if PIOR[c] >= PIOR.get(circ.get(f, "v"), 0):
                circ[f] = c
                motivo[f] = f"nó {no_id}: {ok} dos últimos {total} passos concluídos"
            if falhas and not ponto.get(f) == "r":
                ponto[f] = "r" if falhas and not ok else ponto.get(f, "v")
            ponto.setdefault(f, "v")
    for a, m in vermelhos_do_erro.items():
        ponto[a], motivo[a] = "r", m
    passagem_ok = any(e == "concluido" for lst in por_no.values() for e, _s, _em in lst)
    # os motores: a execução (ponto) e a finalidade (círculo)
    ult = {m: (i, e) for m, i, e in cer.execute("SELECT motor, MAX(inicio), erro FROM execucao_motor GROUP BY motor")}
    # a finalidade de cada motor pela métrica da SUA configuração (o período, a cadência e o destino)
    cfg_motor: dict[str, dict] = {}
    for c in (RAIZ / "eldorado/motores/canal/config").glob("*.toml"):
        try:
            d_ = tomllib.loads(c.read_text(encoding="utf-8"))
            cfg_motor[c.stem] = {"periodo": int(d_.get("metrica", {}).get("periodo_dias", 14)), "cadencia": float(d_.get("metrica", {}).get("cadencia_h", 24)),
                                 "destino": d_.get("motor", {}).get("destino", "biblioteca"), "esporadica": bool(d_.get("metrica", {}).get("esporadica"))}
        except (tomllib.TOMLDecodeError, ValueError):
            pass
    ultimo_aceito = dict(bib.execute("SELECT motor, MAX(encontrado_em) FROM achado WHERE decisao = 'aceito' GROUP BY motor").fetchall())
    try:
        ultimo_incentivo = bib.execute("SELECT MAX(em) FROM incentivo").fetchone()[0]       # as empresas: o destino especial
    except sqlite3.Error:
        ultimo_incentivo = None
    for n in mapa["nos"]:
        if not n["componente"].startswith("motor "):
            continue
        mid, p = n["componente"][6:], n["id"]
        i, e = ult.get(mid, (None, None))
        cm = cfg_motor.get(mid, {"periodo": 14, "cadencia": 24, "destino": "biblioteca"})
        janela_leitura = (agora - timedelta(hours=cm["cadencia"])).isoformat()
        desde = (agora - timedelta(days=cm["periodo"])).date().isoformat()
        entrega = ultimo_incentivo if cm["destino"] == "especial" else ultimo_aceito.get(mid)
        atingiu = bool(entrega) and str(entrega)[:10] >= desde
        o_que = "empresa ou incentivo registrado" if cm["destino"] == "especial" else "achado aceito"
        if i is None:
            ponto[p], circ[p], motivo[p] = "c", "r", "o motor nunca leu"
        else:
            ponto[p] = "r" if e and i >= h24 else ("v" if i >= h48 else "c")
            leu = i >= janela_leitura
            circ[p] = "v" if leu and (atingiu or (cm.get("esporadica") and not e)) else "a" if (leu or atingiu) else "r"
            fim = f"{o_que} em {cm['periodo']} dias" if atingiu else f"sem {o_que} em {cm['periodo']} dias (último: {str(entrega or 'nenhum')[:10]})"
            if leu and not atingiu and cm.get("esporadica") and not e:
                fim = "fonte esporádica: a vigilância sem erro cumpre a finalidade (a fonte não tem chamada aberta agora)"
            erro_txt = f" com erro: {str(e)[:100]}" if e else ""
            motivo[p] = f"última leitura {i[:16]} ({'dentro' if leu else 'fora'} da cadência de {cm['cadencia']:.0f} h){erro_txt}; {fim}"
    # os bancos: a integridade e a gravação recente
    for f, con in (("dados/biblioteca.db", bib), ("dados/cerebro.db", cer)):
        integro = con.execute("PRAGMA quick_check").fetchone()[0] == "ok"
        ultimo = con.execute("SELECT MAX(aplicado_em) FROM evento_aplicado").fetchone()[0] or ""
        ponto[f] = "v" if integro else "r"
        circ[f] = "v" if integro and ultimo >= h24 else "a" if integro else "r"
        motivo[f] = f"integridade {'ok' if integro else 'com problema'}; última gravação {ultimo[:16] or 'nenhuma'}"
    cer.close()
    bib.close()
    # os demais: o ponto pelo alcance (rodou indiretamente quando a passagem rodou); o círculo, o pior de quem o usa
    usado_por: dict[str, set[str]] = defaultdict(set)
    for a in mapa["arestas"]:
        if a["tipo"] in ("importa", "configura", "fluxo", "aciona"):
            usado_por[a["para"]].add(a["de"])
    for p, n in nos.items():
        if p in ponto:
            continue
        if not n["alcancado"]:
            ponto[p], motivo[p] = "c", "fora do funcionamento: nenhum fluxo da produção o alcança"
        else:
            ponto[p] = "v" if passagem_ok else "c"
            motivo.setdefault(p, "rodou com a passagem (alcançado pela produção)" if passagem_ok else "nenhuma passagem concluída em 24 h")
    # o círculo das bibliotecas: vermelho só pelo próprio erro (no rastro); verde se algum usuário cumpre a finalidade;
    # âmbar se todos os que o usam estão em falha (antes: o pior de quem usa, o que espalhava a falha de um nó por tudo)
    for p in vermelhos_do_erro:
        circ.setdefault(p, "r")
    for _ in range(6):
        for p in nos:
            if p in circ:
                continue
            herd = [circ[u] for u in usado_por.get(p, ()) if u in circ]
            if herd:
                circ[p] = "v" if "v" in herd else "a" if any(h in ("a", "r") for h in herd) else "c"
    # os fluxos do GitHub (a raiz da herança): a última execução concluída (sucesso ou falha; as interrompidas pela
    # implantação não contam)
    for p, (c_, m_) in _fluxos_github(nos).items():
        ponto.setdefault(p, "v")
        circ[p], motivo[p] = c_, m_
    # as configurações: a finalidade é ser válida (e é lida por quem a usa)
    for p in nos:
        if p.startswith(("config/", "workflows/")) and p not in circ and nos[p]["alcancado"]:
            ok = _valida(RAIZ / p)
            circ[p], motivo[p] = ("v", "configuração válida, lida pela produção") if ok else ("r", "configuração inválida (não abre)")
    # os parados por desenho: a finalidade é não rodar; os que aguardam a decisão da titular ficam em atenção, com o parecer
    for p, m_ in POR_DESENHO.items():
        if p in nos:
            ponto[p], circ[p], motivo[p] = "v", "v", m_
    for p, m_ in AGUARDAM_DECISAO.items():
        if p in nos:
            ponto[p], circ[p], motivo[p] = "c", "a", m_
    for _ in range(6):                                           # a herança de novo, com a raiz dos fluxos
        for p in nos:
            if p in circ:
                continue
            herd = [circ[u] for u in usado_por.get(p, ()) if u in circ]
            if herd:
                circ[p] = "v" if "v" in herd else "a" if any(h in ("a", "r") for h in herd) else "c"
    for p in sorted(nos, key=lambda x: -x.count("/")):            # os pacotes: pelos seus módulos e subpacotes (de baixo para cima)
        if p.endswith("__init__.py") and circ.get(p, "c") == "c":
            pasta = p.rsplit("/", 1)[0] + "/"
            irmaos = [circ.get(q) for q in nos if q.startswith(pasta) and q != p and ("/" not in q[len(pasta):]
                                                                                 or q[len(pasta):].count("/") == 1 and q.endswith("/__init__.py"))]
            if irmaos:
                circ[p] = "v" if "v" in irmaos else "a" if any(h in ("a", "r") for h in irmaos) else "c"
                motivo.setdefault(p, "o pacote: pelos seus módulos")
    for p in nos:
        circ.setdefault(p, "c")
    linhas = {f"{a['de']}>{a['para']}": ("r" if "r" in (ponto.get(a["de"]), ponto.get(a["para"])) else
                                         "v" if ponto.get(a["de"]) == ponto.get(a["para"]) == "v" else "c") for a in mapa["arestas"]}
    return {"em": agora.isoformat(timespec="seconds"),
            "arquivos": {p: {"p": ponto[p], "c": circ[p], "m": motivo.get(p, "")} for p in nos},
            "linhas": {k: v for k, v in linhas.items() if v != "v"}}


POR_DESENHO = {
    "eldorado/base/motor_modelo/__init__.py": "o motor modelo não roda por desenho: é o molde de todo motor novo",
    "eldorado/motores/acesso/rotas_alternativas.py": "o Tor, desligado por desenho no plano (não roda)",
}
AGUARDAM_DECISAO = {
    "eldorado/base/cerebro/regras.py": "fica (titular, 25/10/2026): a detecção de contradições entre regras ainda não foi substituída",
    "config/regras.toml": "fica (titular, 25/10/2026): 15 decisões da titular que ainda não estão no registro das regras",
    "config/comparacao.toml": "fica (titular, 25/10/2026): a comprovação de cobertura antes de eliminar o Eldorado0 ainda não foi feita",
}


def _valida(p: Path) -> bool:
    try:
        t = p.read_text(encoding="utf-8")
        if p.suffix == ".toml":
            tomllib.loads(t)
        elif p.suffix == ".json":
            import json as _j
            _j.loads(t)
        return True
    except Exception:  # noqa: BLE001
        return False


def _fluxos_github(nos: dict) -> dict[str, tuple[str, str]]:
    """A última execução concluída de cada fluxo do GitHub (pela chave de leitura da produção); sem a chave, nada."""
    import json as _j
    import os
    import urllib.request
    token, repo = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"), os.environ.get("GITHUB_REPOSITORY")
    if not (token and repo):
        return {}
    try:
        req = urllib.request.Request(f"https://api.github.com/repos/{repo}/actions/runs?per_page=100", headers={"Authorization": f"Bearer {token}"})
        runs = _j.loads(urllib.request.urlopen(req, timeout=20).read())["workflow_runs"]
    except Exception:  # noqa: BLE001
        return {}
    saida: dict[str, tuple[str, str]] = {}
    for r in runs:
        p = r.get("path") or ""
        if p in nos and p not in saida and r.get("status") == "completed" and r.get("conclusion") in ("success", "failure"):
            ok = r["conclusion"] == "success"
            saida[p] = ("v" if ok else "r", f"a última execução ({r.get('updated_at', '')[:16]}): {'sucesso' if ok else 'falhou'}")
    for p in nos:
        if p.startswith(".github/workflows/") and p not in saida:
            saida[p] = ("v", "fluxo sob demanda: sem execução concluída recente (nada a corrigir)")
    return saida


def no_medir_arquivos(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem: a medição de cada arquivo (no máximo a cada 10 minutos), gravada no aprendizado do Cérebro."""
    import json
    import sqlite3
    from datetime import datetime, timedelta, timezone
    dados = Path(parametros.get("dados", "dados"))
    if not ((dados / "cerebro.db").exists() and (dados / "biblioteca.db").exists()):
        return [{"medicao": "sem os bancos nesta pasta"}]               # a medição nunca derruba a passagem
    cer = sqlite3.connect(f"file:{dados / 'cerebro.db'}?mode=ro", uri=True)
    try:
        tem = cer.execute("SELECT 1 FROM sqlite_master WHERE name = 'medicao_arquivos'").fetchone()
        ultima = cer.execute("SELECT em FROM medicao_arquivos WHERE chave = 'atual'").fetchone() if tem else None
    finally:
        cer.close()
    if ultima and datetime.fromisoformat(ultima[0]) > datetime.now(timezone.utc) - timedelta(minutes=int(parametros.get("intervalo_min", 10))):
        return [{"medicao": "em dia"}]
    r = medir(dados)
    texto = json.dumps(r, ensure_ascii=False, separators=(",", ":"))
    for chave in ("atual", "dia-" + r["em"][:10]):
        contexto.diario.emitir("arquivos.medidos", "medicao", {"chave": chave, "em": r["em"], "dados": texto})
    cont = defaultdict(int)
    for v in r["arquivos"].values():
        cont[v["p"]] += 1
    return [{"medidos": len(r["arquivos"]), "pontos": dict(cont)}]


def finalidade(p: str) -> str:
    """A finalidade tirada do próprio arquivo: a descrição no início do código, a finalidade da configuração do motor, ou o
    comentário de abertura da configuração."""
    f = RAIZ / p
    if not f.exists() or f.suffix == ".db":
        return {"dados/biblioteca.db": "A Biblioteca: os livros e as empresas (o banco relacional único dos livros).",
                "dados/cerebro.db": "O Cérebro: o banco de aprendizado (nunca livros)."}.get(p, "")
    txt = f.read_text(encoding="utf-8", errors="replace")
    if f.name == "__init__.py":
        return f"O pacote {f.parent.relative_to(RAIZ).as_posix()}: reúne os arquivos da pasta."
    if f.suffix == ".json":
        import json as _j
        try:
            d = _j.loads(txt)
        except ValueError:
            return ""
        return str(d.get("o_que_e") or d.get("descricao") or {"config/arquivos.json": "O catálogo dos arquivos do sistema (o inventário).",
                   "config/motores_previstos.json": "O estudo da titular: os 47 motores, os alvos e o aprendizado do Eldorado0."}.get(p, ""))[:400]
    if f.suffix == ".py":
        try:
            d = ast.get_docstring(ast.parse(txt)) or ""
        except SyntaxError:
            d = ""
        return re.sub(r"\s+", " ", d.split("\n\n")[0])[:400]
    if p.startswith("eldorado/motores/canal/config/"):
        try:
            m = tomllib.loads(txt).get("motor", {})
            return f"{m.get('nome', '')}: {m.get('finalidade', '')}"[:400]
        except tomllib.TOMLDecodeError:
            return ""
    linhas = [x.lstrip("#").strip() for x in txt.splitlines()[:6] if x.strip().startswith("#") or x.strip().startswith("name:")]
    return " ".join(x for x in linhas if x)[:400]
