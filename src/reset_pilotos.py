"""RESET DAS MISSÕES DOS PILOTOS.

1) Reset de 01/10 (titular) — `run()`, idempotente, roda a cada pouso: missão com data anterior a RESET já está no
   histórico arquivado (estado/pilotos/historico/) e sai do estado de trabalho.

2) CONTAGEM SEMANAL (titular, 09/10) — `zerar_se_preciso(piloto)`, chamado PELO PRÓPRIO PILOTO no início de cada voo.
   O reset manual de 08/10 foi desfeito pelos próprios voos: um voo que decolou antes do reset levava a cópia antiga do
   diário, acrescentava a sua missão e, no pouso, gravava tudo por cima. Agora:
   - toda segunda-feira à 0h de Brasília (ou quando a titular pedir, em estado/pilotos/zerar_contagem.json) começa uma
     contagem nova;
   - cada arquivo de contagem leva o carimbo da contagem a que pertence ("contagem" / "_contagem" no voos.json);
   - no início do voo, o Piloto confere o carimbo; se for de contagem anterior, guarda os números antigos em
     estado/pilotos/historico/contagem_semanal/ e zera missões, abates e voos por dia;
   - um voo antigo que pousar depois e gravar números velhos por cima leva junto o carimbo velho — e o voo seguinte
     zera de novo. O carimbo viaja com os números, então eles não conseguem mais "ressuscitar".
   Arquivos: Espião → estado/piloto/bordo.json e estado/piloto/voos.json; Interceptador → estado/interceptador/bordo.json
   e docs/dados/interceptador.json. Os painéis e o aprendizado (a cada 100 buscas) contam só a partir de
   `inicio_contagem()`.
"""
from __future__ import annotations

import json
import lzma
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESET = "2026-10-01T14:01:07+00:00"
BRASILIA = timezone(timedelta(hours=-3), "Brasília")   # sem horário de verão desde 2019 (Decreto 9.772/2019)
PEDIDO = ROOT / "estado/pilotos/zerar_contagem.json"
HIST_SEMANAL = ROOT / "estado/pilotos/historico/contagem_semanal"
ARQUIVOS = {
    "espiao": ("estado/piloto/bordo.json", "estado/piloto/voos.json"),
    "interceptador": ("estado/interceptador/bordo.json", "docs/dados/interceptador.json"),
}


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return padrao


def _w(p: Path, v) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(v, ensure_ascii=False, indent=1), encoding="utf-8")


def _iso(d: datetime) -> str:
    return d.astimezone(timezone.utc).isoformat(timespec="seconds")


def _agora(agora: datetime | None = None) -> datetime:
    return (agora or datetime.now(timezone.utc)).astimezone(timezone.utc)


def _parse(s) -> datetime | None:
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def inicio_semana(agora: datetime | None = None) -> datetime:
    """Segunda-feira 0h (Brasília) da semana corrente, em UTC."""
    br = _agora(agora).astimezone(BRASILIA)
    seg = (br - timedelta(days=br.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    return seg.astimezone(timezone.utc)


def pedido_em() -> str | None:
    d = _parse((_j(PEDIDO, {}) or {}).get("pedido_em"))
    return _iso(d) if d else None


def inicio_contagem(agora: datetime | None = None) -> str:
    """Início da contagem em vigor: a segunda-feira 0h mais recente ou o último pedido da titular, o que vier depois.
    Pedido com data futura é ignorado até chegar a hora."""
    ini = inicio_semana(agora)
    p = _parse(pedido_em())
    if p and ini < p <= _agora(agora):
        ini = p
    return _iso(ini)


def pedir(motivo: str = "pedido da titular", agora: datetime | None = None) -> dict:
    """Pedido de zeramento fora da segunda-feira. Os dois Pilotos o cumprem no início do próximo voo."""
    d = {"pedido_em": _iso(_agora(agora)), "motivo": motivo,
         "regra": "Os Pilotos zeram missões, abates e voos por dia no início do próximo voo; os números antigos ficam em "
                  "estado/pilotos/historico/contagem_semanal/."}
    _w(PEDIDO, d)
    return d


def _carimbo(dados, chave: str) -> str | None:
    return ((dados or {}).get(chave) or {}).get("desde") if isinstance(dados, dict) else None


def situacao(agora: datetime | None = None) -> dict:
    ini = inicio_contagem(agora)
    out = {"inicio_contagem": ini, "pedido_em": pedido_em(), "pilotos": {}}
    for piloto, arqs in ARQUIVOS.items():
        out["pilotos"][piloto] = {a: _carimbo(_j(ROOT / a, {}), "_contagem" if a.endswith("voos.json") else "contagem") for a in arqs}
    return out


def zerar_se_preciso(piloto: str, agora: datetime | None = None) -> dict:
    """Chamado pelo Piloto no INÍCIO do voo. Zera os arquivos de contagem que não carregam o carimbo da contagem em
    vigor; antes, guarda os números antigos. Idempotente: com o carimbo certo, não faz nada."""
    if piloto not in ARQUIVOS:
        raise ValueError(f"piloto desconhecido: {piloto}")
    ini = inicio_contagem(agora); agora_iso = _iso(_agora(agora))
    motivo = "pedido da titular" if ini == pedido_em() else "segunda-feira 0h (Brasília)"
    carimbo = {"desde": ini, "zerada_em": agora_iso, "motivo": motivo}
    antigos, zerados = {}, []
    for a in ARQUIVOS[piloto]:
        p = ROOT / a
        chave = "_contagem" if a.endswith("voos.json") else "contagem"
        dados = _j(p, None)
        c = _carimbo(dados, chave)
        if c and c >= ini:
            continue
        if dados is not None:
            antigos[a] = dados
        zerados.append(a)
    if not zerados:
        return {"piloto": piloto, "zerou": False, "inicio_contagem": ini}
    arquivo_hist = None
    if antigos:
        de = sorted({_carimbo(v, "_contagem" if k.endswith("voos.json") else "contagem") or "sem-carimbo" for k, v in antigos.items()})[0]
        HIST_SEMANAL.mkdir(parents=True, exist_ok=True)
        nome = f"{piloto}_{de[:10] if de[:1].isdigit() else de}_ate_{agora_iso[:19].replace(':', '')}.json.xz"
        arquivo_hist = HIST_SEMANAL / nome
        conteudo = {"piloto": piloto, "contagem_de": de, "guardado_em": agora_iso, "nova_contagem_desde": ini, "motivo": motivo,
                    "resumo": _resumo(antigos), "arquivos": antigos}
        arquivo_hist.write_bytes(lzma.compress(json.dumps(conteudo, ensure_ascii=False).encode("utf-8")))
    for a in zerados:
        p = ROOT / a
        dados = _j(p, {}) or {}
        _w(p, _zerado(a, dados if isinstance(dados, dict) else {}, carimbo))
    return {"piloto": piloto, "zerou": True, "arquivos": zerados, "inicio_contagem": ini, "motivo": motivo,
            "numeros_antigos_em": str(arquivo_hist.relative_to(ROOT)) if arquivo_hist else None, "resumo_antigo": _resumo(antigos)}


def _resumo(antigos: dict) -> dict:
    r = {}
    for a, d in antigos.items():
        if not isinstance(d, dict):
            continue
        if a.endswith("voos.json"):
            r[a] = {"voos": sum(v for k, v in d.items() if not k.startswith("_") and isinstance(v, int)),
                    "dias": len([k for k in d if not k.startswith("_")])}
        elif a.startswith("docs/"):
            r[a] = {k: v for k, v in (d.get("acumulado") or {}).items() if isinstance(v, (int, float))}
        else:
            r[a] = {"missoes": len(d.get("missoes") or []), "total_abates": d.get("total_abates", 0)}
    return r


def _zerado(arquivo: str, d: dict, carimbo: dict) -> dict:
    if arquivo.endswith("voos.json"):
        return {"_contagem": carimbo}
    if arquivo == "estado/piloto/bordo.json":
        fora = {"missao_atual", "missoes", "abates", "total_abates", "iniciado_em", "contagem_reiniciada_em", "contagem"}
        return {**{k: v for k, v in d.items() if k not in fora}, "missao_atual": None, "missoes": [], "abates": {}, "total_abates": 0,
                "iniciado_em": carimbo["desde"], "contagem": carimbo}
    if arquivo == "estado/interceptador/bordo.json":
        return {**{k: v for k, v in d.items() if k not in ("missoes", "abates", "total_abates", "contagem")},
                "abates": {}, "missoes": [], "total_abates": 0, "contagem": carimbo}
    # docs/dados/interceptador.json: descrição e fila ficam; números e missões zeram (o pouso recalcula na janela)
    ac = {k: (0 if isinstance(v, (int, float)) else ({} if isinstance(v, dict) else None)) for k, v in (d.get("acumulado") or {}).items()}
    return {**{k: v for k, v in d.items() if k not in ("acumulado", "missoes", "contagem", "erro_publicacao")},
            "acumulado": ac, "missoes": [], "contagem": carimbo}


def run() -> dict:
    n_av = n_arq = n_voo = 0
    D = ROOT / "estado/piloto/aprendizados/avaliacoes"
    for f in D.glob("*.json") if D.exists() else []:
        if str(_j(f, {}).get("em") or "") < RESET:
            f.unlink(); n_av += 1
    for f in D.glob("arquivo-*.jsonl.xz") if D.exists() else []:
        try:
            fica = [l for l in lzma.decompress(f.read_bytes()).decode().splitlines() if l.strip() and str((json.loads(l).get("avaliacao") or {}).get("em") or "") >= RESET]
        except Exception:
            fica = []
        f.write_bytes(lzma.compress(("\n".join(fica) + "\n").encode())) if fica else f.unlink(); n_arq += 1
    B = ROOT / "estado/piloto/bordo.json"; b = _j(B, {})
    if b.get("missoes"):
        antes = len(b["missoes"]); b["missoes"] = [m for m in b["missoes"] if str(m.get("inicio") or m.get("fim") or "") >= RESET]
        if len(b["missoes"]) != antes:
            B.write_text(json.dumps(b, ensure_ascii=False, indent=1), encoding="utf-8")
    for f in (ROOT / "estado/interceptador/relatorios").glob("*.json"):
        d = _j(f, {}); vs = d.get("voos") or []
        novos = [v for v in vs if str(v.get("em") or v.get("inicio") or "") >= RESET]
        if len(novos) != len(vs):
            n_voo += len(vs) - len(novos)
            if novos:
                d["voos"] = novos; f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
            else:
                f.unlink()
    return {"avaliacoes_antigas_retiradas": n_av, "arquivos_mensais_filtrados": n_arq, "voos_antigos_retirados": n_voo}


if __name__ == "__main__":
    # python -m src.reset_pilotos            → limpeza de 01/10 (pouso)
    # python -m src.reset_pilotos --pedir    → pedido da titular: os Pilotos zeram no próximo voo
    # python -m src.reset_pilotos --situacao → carimbos e início da contagem em vigor
    if "--pedir" in sys.argv:
        print(json.dumps(pedir(" ".join(a for a in sys.argv[1:] if a != "--pedir") or "pedido da titular"), ensure_ascii=False))
    elif "--situacao" in sys.argv:
        print(json.dumps(situacao(), ensure_ascii=False, indent=1))
    else:
        print(json.dumps(run(), ensure_ascii=False))
