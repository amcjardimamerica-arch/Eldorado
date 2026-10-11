"""MEDIÇÃO DE USO DOS ARQUIVOS (titular, 11/10/2026) — config/uso_arquivos.json.

Para cada arquivo versionado fora do banco de dados e do código:
  · CITADO: algum código (src/, scripts/), fluxo (.github/workflows/) ou o painel (docs/dashboard.html) cita o caminho,
    o nome (ou o prefixo do nome, para arquivos com data) ou a pasta que é lida por varredura (glob/iterdir/listdir);
  · ÚLTIMA MUDANÇA: a assinatura (SHA-1) de cada arquivo fica em estado/uso_arquivos.json com a data em que mudou.
ALERTA de verificação: não citado E sem mudança há mais de `dias_sem_uso` (30). Saída para o painel e a revisão:
docs/dados/uso_arquivos.json (resumo + lista de alertas + não citados ainda dentro do prazo).
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config/uso_arquivos.json"
ESTADO = ROOT / "estado/uso_arquivos.json"
SAIDA = ROOT / "docs/dados/uso_arquivos.json"


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao


def _corpus() -> tuple[str, set]:
    textos, pastas_varridas = [], set()
    alvos = list((ROOT / "src").rglob("*.py")) + list((ROOT / "scripts").rglob("*.py")) + list((ROOT / ".github/workflows").glob("*.yml"))
    alvos.append(ROOT / "docs/dashboard.html")
    for a in alvos:
        if "__pycache__" in a.parts:
            continue
        try:
            t = a.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        textos.append(t)
        if re.search(r"\.glob\(|\.rglob\(|iterdir\(|listdir\(|ls-files", t):
            pastas_varridas |= set(re.findall(r"[\"']((?:dados|estado|docs|entrada_manual|catalogo_captacao)/[\w./-]+?)/?[\"']", t))
    return "\n".join(textos), pastas_varridas


def citado(caminho: str, corpus: str, varridas: set) -> str | None:
    """Por onde o arquivo é citado (ou None)."""
    if caminho in corpus:
        return "caminho citado no código"
    nome = caminho.rsplit("/", 1)[-1]
    if len(nome) > 6 and nome in corpus:
        return "nome citado no código"
    pref = re.split(r"\d{4}-\d{2}-\d{2}|\d{8}", nome)[0]
    if pref != nome and len(pref) >= 6 and pref in corpus:
        return "prefixo do nome (arquivo com data) citado no código"
    pasta = caminho.rsplit("/", 1)[0] if "/" in caminho else ""
    while pasta:
        if pasta in varridas:
            return f"pasta lida por varredura ({pasta})"
        pasta = pasta.rsplit("/", 1)[0] if "/" in pasta else ""
    return None


def medir(hoje: str | None = None, gravar: bool = True) -> dict:
    hoje = hoje or date.today().isoformat()
    cfg = _j(CFG, {})
    banco = tuple(cfg.get("banco_de_dados") or [])
    fora = tuple(cfg.get("fora_da_medicao") or [])
    lim = int(cfg.get("dias_sem_uso", 30))
    arquivos = [f for f in subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True).stdout.split("\0") if f]
    est = _j(ESTADO, {}).get("arquivos") or {}
    corpus, varridas = _corpus()
    novo, alertas, nao_citados, em_uso, mb, monitorados = {}, [], [], 0, 0.0, 0
    for f in arquivos:
        p = ROOT / f
        if not p.is_file() or f.startswith(banco) or f.startswith(fora):
            continue
        monitorados += 1
        por = citado(f, corpus, varridas)
        if por:                                       # citado: em uso — não precisa guardar assinatura nem data
            em_uso += 1
            continue
        h = hashlib.sha1(p.read_bytes()).hexdigest()[:16]
        ant = est.get(f) or {}
        desde = ant.get("desde") if ant.get("h") == h and ant.get("desde") else hoje
        novo[f] = {"h": h, "desde": desde}
        dias = (date.fromisoformat(hoje) - date.fromisoformat(desde)).days
        tam = p.stat().st_size
        if dias <= lim:
            em_uso += 1
            nao_citados.append({"arquivo": f, "dias_sem_mudar": dias, "kb": tam // 1024})
            continue
        alertas.append({"arquivo": f, "dias_sem_uso": dias, "kb": tam // 1024, "motivo": f"não citado por código, fluxo ou painel e sem mudança há {dias} dias"})
        mb += tam / 1048576
    alertas.sort(key=lambda x: -x["kb"])
    res = {"em": hoje, "regra": cfg.get("regra"), "monitorados": monitorados, "em_uso": em_uso, "alertas": len(alertas),
           "mb_em_alerta": round(mb, 1), "nao_citados_dentro_do_prazo": len(nao_citados),
           "lista_alertas": alertas[:300], "lista_nao_citados": sorted(nao_citados, key=lambda x: -x["kb"])[:300]}
    if gravar:
        ESTADO.parent.mkdir(parents=True, exist_ok=True)
        ESTADO.write_text(json.dumps({"em": hoje, "arquivos": novo}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        SAIDA.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    return res


if __name__ == "__main__":
    r = medir()
    print(json.dumps({k: v for k, v in r.items() if not k.startswith("lista")}, ensure_ascii=False, indent=1))
