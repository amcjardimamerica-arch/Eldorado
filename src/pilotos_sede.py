"""SEDE DOS PILOTOS — nuvem ou Brasil, com troca automática (parecer dos pilotos, 02/10/2026).

O problema medido: no servidor do GitHub (IP de datacenter nos EUA) o DuckDuckGo entrega 2 buscas por máquina e
bloqueia, e boa parte dos sites de prefeituras e do TJGO recusa o IP. Os pilotos ficavam "voando" com 2 buscas boas e o
resto pelo Google Notícias — e o Interceptador escolhia página oficial de outro estado.

A solução sem custo: os MESMOS pilotos, com o MESMO modelo local (Qwen3-8B, llama.cpp), rodando numa máquina com IP
brasileiro — o computador do titular (quando ligado) ou uma VM gratuita no Brasil (Oracle Cloud Always Free, São Paulo
ou Vinhedo, 24 h). Quem roda no Brasil grava um BATIMENTO em `estado/sede_pilotos.json` a cada voo; enquanto o
batimento estiver fresco, a nuvem não decola (não há dois pilotos no mesmo alvo); se o batimento parar (computador
desligado, VM caiu), a nuvem volta sozinha no próximo horário de segurança. Ninguém precisa trocar nada à mão.

Os dois escritores nunca apagam o trabalho um do outro: o estado do Interceptador é MESCLADO (por alvo, vence o mais
recente; voos e relatórios somados), em vez de substituído.

    python -m src.pilotos_sede nuvem-deve-voar interceptador     # na nuvem: grava voar=true|false em GITHUB_OUTPUT
    python -m src.pilotos_sede batimento --maquina vm --pilotos interceptador,espiao
    python -m src.pilotos_sede mesclar-interceptador /tmp/copia/interceptador
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config/pilotos_sede.json"
BATIMENTO = ROOT / "estado/sede_pilotos.json"
INTERCEPTADOR = ROOT / "estado/interceptador"


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao


def _w(p: Path, d) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def _agora() -> datetime:
    return datetime.now(timezone.utc)


def cfg() -> dict:
    return _j(CFG, {}) or {}


def batimento(maquina: str, pilotos: list[str], estado: str = "voando", detalhe: dict | None = None, agora: datetime | None = None) -> dict:
    d = {"em": (agora or _agora()).isoformat(timespec="seconds"), "maquina": maquina, "pilotos": pilotos, "estado": estado,
         "detalhe": detalhe or {}}
    _w(BATIMENTO, d)
    return d


def brasil_ativo(piloto: str, agora: datetime | None = None) -> tuple[bool, str]:
    b = _j(BATIMENTO, {}) or {}
    if not b.get("em"):
        return False, "nenhuma máquina no Brasil registrou batimento"
    if b.get("estado") == "encerrado":
        return False, f"a máquina do Brasil ({b.get('maquina')}) encerrou em {b['em']}"
    if piloto not in (b.get("pilotos") or []):
        return False, f"a máquina do Brasil não roda o {piloto}"
    try:
        idade = ((agora or _agora()) - datetime.fromisoformat(b["em"])).total_seconds() / 60
    except ValueError:
        return False, "batimento ilegível"
    lim = float(cfg().get("minutos_batimento", 45))
    if idade > lim:
        return False, f"o batimento do Brasil ({b.get('maquina')}) parou há {idade:.0f} min (limite {lim:.0f}) — a nuvem reassume"
    return True, f"{piloto} voando no Brasil ({b.get('maquina')}), batimento há {idade:.0f} min"


def nuvem_deve_voar(piloto: str, agora: datetime | None = None) -> tuple[bool, str]:
    sede = (cfg().get("sede") or "automatica").lower()
    if sede == "nuvem":
        return True, "sede fixada na nuvem pelo titular"
    ativo, motivo = brasil_ativo(piloto, agora)
    if ativo:
        return False, motivo
    return True, motivo


# ─────────────────────────── mescla do estado do Interceptador ───────────────────────────
def _mesclar_estado(meu: dict, deles: dict) -> dict:
    """feitos: por alvo, vence o mais recente; rodadas: união pela data e alvo, as 60 mais novas."""
    f = dict(deles.get("feitos") or {})
    for k, v in (meu.get("feitos") or {}).items():
        if str((v or {}).get("em") or "") >= str((f.get(k) or {}).get("em") or ""):
            f[k] = v
    vistos, rod = set(), []
    for r in sorted((deles.get("rodadas") or []) + (meu.get("rodadas") or []), key=lambda r: str(r.get("em") or "")):
        ch = (r.get("em"), r.get("id"))
        if ch not in vistos:
            vistos.add(ch); rod.append(r)
    return {**deles, **{k: v for k, v in meu.items() if k not in ("feitos", "rodadas")}, "feitos": f, "rodadas": rod[-60:]}


def _mesclar_relatorio(meu: dict, deles: dict) -> dict:
    vistos, voos = set(), []
    for v in sorted((deles.get("voos") or []) + (meu.get("voos") or []), key=lambda v: str(v.get("em") or "")):
        ch = (v.get("em"), v.get("id"))
        if ch not in vistos:
            vistos.add(ch); voos.append(v)
    return {**deles, **meu, "voos": voos}


def _mesclar_dict(meu, deles):
    if isinstance(meu, dict) and isinstance(deles, dict):
        out = dict(deles)
        for k, v in meu.items():
            out[k] = _mesclar_dict(v, deles.get(k)) if k in deles else v
        return out
    return meu


def mesclar_interceptador(copia: Path, destino: Path | None = None) -> dict:
    """Leva a cópia de um voo (pasta estado/interceptador de outra máquina) para o estado atual SEM apagar o que a
    outra máquina gravou no meio tempo."""
    destino = destino or INTERCEPTADOR
    destino.mkdir(parents=True, exist_ok=True)
    feito = {"arquivos": 0}
    for arq in sorted(Path(copia).rglob("*")):
        if arq.is_dir():
            continue
        rel = arq.relative_to(copia)
        alvo = destino / rel
        meu = _j(arq, None)
        if alvo.exists() and meu is not None:
            deles = _j(alvo, None)
            if rel.as_posix() == "estado.json":
                meu = _mesclar_estado(meu, deles or {})
            elif rel.parts[0] == "relatorios":
                meu = _mesclar_relatorio(meu, deles or {})
            elif isinstance(meu, dict) and isinstance(deles, dict) and rel.as_posix() != "bordo.json":
                meu = _mesclar_dict(meu, deles)
            _w(alvo, meu)
        else:
            alvo.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(arq, alvo)
        feito["arquivos"] += 1
    # o aguardando.json some quando a cópia não o tem (o voo achou alvo)
    if not (Path(copia) / "aguardando.json").exists() and (destino / "aguardando.json").exists():
        (destino / "aguardando.json").unlink()
    return feito


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m src.pilotos_sede")
    ap.add_argument("acao", choices=["nuvem-deve-voar", "batimento", "encerrar", "mesclar-interceptador", "status"])
    ap.add_argument("alvo", nargs="?")
    ap.add_argument("--maquina", default="computador")
    ap.add_argument("--pilotos", default="interceptador,espiao")
    a = ap.parse_args(argv)
    if a.acao == "nuvem-deve-voar":
        voar, motivo = nuvem_deve_voar(a.alvo or "interceptador")
        print(("VOAR na nuvem: " if voar else "EM TERRA na nuvem: ") + motivo)
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as fh:
                fh.write(f"voar={'true' if voar else 'false'}\n")
        return 0
    if a.acao == "batimento":
        print(json.dumps(batimento(a.maquina, [x for x in a.pilotos.split(",") if x]), ensure_ascii=False))
        return 0
    if a.acao == "encerrar":
        print(json.dumps(batimento(a.maquina, [x for x in a.pilotos.split(",") if x], estado="encerrado"), ensure_ascii=False))
        return 0
    if a.acao == "mesclar-interceptador":
        print(json.dumps(mesclar_interceptador(Path(a.alvo)), ensure_ascii=False))
        return 0
    print(json.dumps({"batimento": _j(BATIMENTO, {}), "interceptador": nuvem_deve_voar("interceptador"),
                      "espiao": nuvem_deve_voar("espiao")}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
