"""A fábrica de motores: executa a orientação de design (eldorado/motores/skills/criar-motor/SKILL.md).

ficha    o que o estudo da titular definiu para o motor e o aprendizado do Eldorado0 (só para aprender)
criar    o esqueleto da configuração: identidade, finalidade, nomes anteriores, alvos, aprendizado e métrica
         preenchidos; as rotas candidatas comentadas, para decidir depois da sondagem
validar  o que a orientação exige: aceito pelo registro, conforme o estudo, ao menos duas rotas e métrica
"""
from __future__ import annotations

import json
import tomllib
from pathlib import Path
from urllib.parse import urlsplit

CONFIG = Path(__file__).parent / "config"
ESTUDO = Path("config/motores_previstos.json")


def estudo(caminho: Path = ESTUDO) -> dict[str, dict]:
    return {m["id"]: m for m in json.loads(caminho.read_text(encoding="utf-8"))["motores"]}


def ficha(mid: str, caminho: Path = ESTUDO) -> str:
    m = estudo(caminho)[mid]
    a = m.get("aprendizado_eldorado0") or {}
    linhas = [f"# {m['id']} — {m['nome']}", f"categoria: {m['categoria']} ({m['categoria_nome']}) · no estudo: {m['tipo_no_estudo']}",
              f"finalidade: {m['finalidade'] or '(o estudo não escreveu: defina em uma frase)'}",
              f"situação no sistema: {m['situacao']} {('· ' + m['observacao']) if m['observacao'] else ''}", "",
              f"aprendizado do Eldorado0: {a.get('leituras')} leituras, {a.get('com_resultado')} com resultado",
              f"  domínios: {', '.join(a.get('dominios') or []) or '—'}", f"  bloqueados: {', '.join(a.get('bloqueados') or []) or '—'}",
              f"  robots proíbe: {', '.join(a.get('robots_proibe') or []) or '—'}"]
    linhas += [f"  melhoria: {x}" for x in a.get("melhorias") or []] + [f"  lição: {x[:200]}" for x in (a.get("licoes") or [])[:8]]
    linhas += [f"  rota conhecida: {x}" for x in (a.get("rotas_conhecidas") or [])[:8]]
    linhas += ["", f"motores reunidos ({len(m['agrega'])}):"] + [f"  {g['id']} — {g['nome']} · leituras {g.get('leituras')}, com resultado "
                                                                    f"{g.get('com_resultado')} · bloqueados {', '.join(g.get('bloqueados') or []) or '—'}"
                                                                    for g in m["agrega"]]
    linhas += ["", f"alvos ({len(m['alvos'])}):"] + [f"  {t['id']} — {t['nome']} · {', '.join(t.get('enderecos') or [])[:160]}" for t in m["alvos"]]
    return "\n".join(linhas)


def _q(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def esqueleto(mid: str, caminho: Path = ESTUDO) -> str:
    m = estudo(caminho)[mid]
    a = m.get("aprendizado_eldorado0") or {}
    so_alvos = not (a.get("rotas_conhecidas") or [g for g in m["agrega"] if g.get("rotas_conhecidas")])
    anteriores = [g["id"] for g in m["agrega"]]
    t = [f"# {m['nome']} — criado pela orientação eldorado/motores/skills/criar-motor/SKILL.md (a partir do estudo da titular, 19/10/2026).",
         "# Rotas candidatas comentadas: só entra a que respondeu na sondagem (eldorado sondar).", "", "[motor]", f"id = {_q(m['id'])}",
         f"nome = {_q(m['nome'])}", f"categoria = {_q(m['categoria_nome'])}", f"categoria_estudo = {_q(m['categoria'])}",
         f"finalidade = {_q(m['finalidade'] or 'DEFINIR EM UMA FRASE')}", f"tipo_finalidade = {_q('recorrencia' if so_alvos and m['alvos'] else 'descoberta')}",
         f"nomes_anteriores = {json.dumps(anteriores, ensure_ascii=False)}", "", "# ---- rotas candidatas (do aprendizado; confirmar na sondagem):"]
    candidatas = list(dict.fromkeys((a.get("rotas_conhecidas") or []) + [r for g in m["agrega"] for r in g.get("rotas_conhecidas") or []]))
    for r in candidatas[:12]:
        t += ["# [[fonte]]", f"# nome = {_q(urlsplit(str(r)).netloc or str(r))}", f"# url = {_q(str(r))}",
              "# tipo = \"pagina\"   # api | wordpress | ckan | feed | mapa | pagina", "#"]
    for al in m["alvos"]:
        t += ["", "[[alvo]]", f"id = {_q(al['id'])}", f"nome = {_q(al['nome'])}", f"enderecos = {json.dumps(al.get('enderecos') or [], ensure_ascii=False)}"]
        if al.get("orgao"):
            t.append(f"orgao = {_q(al['orgao'])}")
    bloq = list(dict.fromkeys((a.get("bloqueados") or []) + [b for g in m["agrega"] for b in g.get("bloqueados") or []]))
    licoes = [x for x in (a.get("melhorias") or []) + [li for li in (a.get("licoes") or []) if not li.startswith(("dominios:", "bloqueios_registrados:"))]][:10]
    t += ["", "[acesso]", f"degraus = {json.dumps(['api', 'leve'] + (['local'] if bloq else []))}", "", "[leitura]", "paginas_dos_achados = true",
          "seguir_oficial = true", "", "[lexico]", "termos = []   # o léxico PRÓPRIO da fonte (o comum da missão é herdado)", "vetos = []", "",
          "[aprendizado]", f"licoes = {json.dumps(licoes, ensure_ascii=False)}", f"bloqueios_conhecidos = {json.dumps(bloq, ensure_ascii=False)}",
          "alternativas_para_bloqueio = []", "rotas_que_falharam = []", "", "[metrica]", "cadencia_h = 24", "periodo_dias = 14", ""]
    return "\n".join(t)


def criar(mid: str, pasta: Path = CONFIG, caminho: Path = ESTUDO) -> Path:
    destino = pasta / f"{mid}.toml"
    if destino.exists():
        raise FileExistsError(f"{destino} já existe: um motor existente se amplia, não se recria")
    destino.write_text(esqueleto(mid, caminho), encoding="utf-8")
    return destino


def validar(mid: str, pasta: Path = CONFIG, caminho: Path = ESTUDO) -> list[tuple[str, bool, str]]:
    from .motor import Configuracao
    r: list[tuple[str, bool, str]] = []
    p = pasta / f"{mid}.toml"
    try:
        d = tomllib.loads(p.read_text(encoding="utf-8"))
        cfg = Configuracao(**d)
        r.append(("aceito pelo registro", True, "finalidade e rota presentes"))
    except Exception as e:  # noqa: BLE001 — o relatório da validação mostra qualquer recusa
        return [("aceito pelo registro", False, str(e)[:300])]
    es = estudo(caminho)
    r.append(("conforme o estudo (id)", cfg.motor.id in es and cfg.motor.id == p.stem, cfg.motor.id))
    cat_ok = cfg.motor.id in es and cfg.motor.categoria_estudo == es[cfg.motor.id]["categoria"]
    r.append(("conforme o estudo (categoria)", cat_ok, str(cfg.motor.categoria_estudo)))
    hosts = {urlsplit(f.url).hostname for f in cfg.fonte} | {urlsplit(u).hostname for al in cfg.alvo for u in al.enderecos}
    if cfg.programa:
        hosts |= {urlsplit(u).hostname for u in cfg.programa.documentos}
    r.append(("ao menos duas rotas", len(hosts - {None}) >= 2 or len(cfg.fonte) + len(cfg.alvo) >= 2, f"{len(cfg.fonte)} fonte(s), {len(cfg.alvo)} alvo(s)"))
    r.append(("alvos do estudo", {a["id"] for a in es.get(cfg.motor.id, {}).get("alvos", [])} <= {a.id for a in cfg.alvo},
              f"{len(cfg.alvo)} de {len(es.get(cfg.motor.id, {}).get('alvos', []))}"))
    r.append(("métrica", cfg.metrica.cadencia_h > 0, f"cadência {cfg.metrica.cadencia_h} h"))
    outros = {x: o.stem for o in pasta.glob("*.toml") if o != p for x in tomllib.loads(o.read_text(encoding="utf-8"))["motor"].get("nomes_anteriores", [])}
    conflito = [x for x in cfg.motor.nomes_anteriores if x in outros]
    r.append(("nomes anteriores sem conflito", not conflito, ", ".join(conflito) or "ok"))
    return r


def enderecos(mid: str, pasta: Path = CONFIG) -> list[str]:
    from .motor import Configuracao
    cfg = Configuracao(**tomllib.loads((pasta / f"{mid}.toml").read_text(encoding="utf-8")))
    return [f.url for f in cfg.fonte] + [u for al in cfg.alvo for u in al.enderecos] + (cfg.programa.documentos if cfg.programa else [])
