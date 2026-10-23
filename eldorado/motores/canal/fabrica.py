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


MODELO = Path(__file__).resolve().parents[2] / "base" / "motor_modelo" / "modelo.toml"


def esqueleto(mid: str, caminho: Path = ESTUDO) -> str:
    """O motor novo a partir do MOTOR MODELO (eldorado/base/motor_modelo/modelo.toml): a cópia, com os marcadores
    preenchidos pelo estudo (a identidade, os alvos, o aprendizado) e as rotas candidatas comentadas, para a sondagem."""
    m = estudo(caminho)[mid]
    a = m.get("aprendizado_eldorado0") or {}
    so_alvos = not (a.get("rotas_conhecidas") or [g for g in m["agrega"] if g.get("rotas_conhecidas")])
    candidatas = list(dict.fromkeys((a.get("rotas_conhecidas") or []) + [r for g in m["agrega"] for r in g.get("rotas_conhecidas") or []]))
    rotas = ["# ---- rotas candidatas (do aprendizado; confirmar na sondagem):"]
    for r in candidatas[:12]:
        rotas += ["# [[fonte]]", f"# nome = {_q(urlsplit(str(r)).netloc or str(r))}", f"# url = {_q(str(r))}",
                  "# tipo = \"pagina\"   # api | wordpress | ckan | feed | mapa | pagina", "#"]
    alvos = []
    for al in m["alvos"]:
        alvos += ["[[alvo]]", f"id = {_q(al['id'])}", f"nome = {_q(al['nome'])}", f"enderecos = {json.dumps(al.get('enderecos') or [], ensure_ascii=False)}"]
        if al.get("orgao"):
            alvos.append(f"orgao = {_q(al['orgao'])}")
        alvos.append("")
    bloq = list(dict.fromkeys((a.get("bloqueados") or []) + [b for g in m["agrega"] for b in g.get("bloqueados") or []]))
    licoes = [x for x in (a.get("melhorias") or []) + [li for li in (a.get("licoes") or []) if not li.startswith(("dominios:", "bloqueios_registrados:"))]][:10]
    def dentro(v: str) -> str:                      # o valor dentro de aspas já existentes no modelo
        return json.dumps(v, ensure_ascii=False)[1:-1]
    texto = MODELO.read_text(encoding="utf-8")
    trocas = {"«id»": dentro(m["id"]), "«nome»": dentro(m["nome"]), "«categoria»": dentro(m["categoria_nome"]),
              "«categoria_estudo»": dentro(m["categoria"]), "«finalidade»": dentro(m["finalidade"] or "DEFINIR EM UMA FRASE"),
              "«tipo_finalidade»": "recorrencia" if so_alvos and m["alvos"] else "descoberta",
              "«nomes_anteriores»": json.dumps([g["id"] for g in m["agrega"]], ensure_ascii=False),
              "«licoes»": json.dumps(licoes, ensure_ascii=False), "«bloqueios»": json.dumps(bloq, ensure_ascii=False),
              "# «rotas_candidatas»": "\n".join(rotas), "# «alvos»": "\n".join(alvos)}
    for k, v in trocas.items():
        texto = texto.replace(k, v)
    cabeca = (f"# {m['nome']} — criado a partir do MOTOR MODELO (eldorado/base/motor_modelo/modelo.toml) e do estudo da titular.\n"
              "# Decida as rotas pela sondagem (eldorado gravar), ligue ou desligue as ferramentas e valide: eldorado motor validar.\n")
    return cabeca + texto.split("\n[motor]", 1)[1].join(["\n[motor]", ""]) if "\n[motor]" in texto else cabeca + texto


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
