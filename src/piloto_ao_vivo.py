"""O PILOTO AO VIVO — o que ele está fazendo NESTE momento.

O painel não pode ser enfeite. Esta é a fonte que ele lê para dizer, com honestidade:

  • está voando agora? em que motor, atrás de quê, desde quando
  • o que encontrou neste voo e nos anteriores
  • ou está parado — e há quanto tempo, com o botão para acionar

A regra que mantém o painel honesto: TUDO aqui tem carimbo de hora. O painel compara esse
carimbo com o relógio de quem olha. Se o último sinal é velho, ele não finge que o Piloto
está voando: diz que está parado e oferece o acionamento. Um painel que mostra "em voo"
quando ninguém voa é pior do que um painel vazio.
"""
from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json

VIVO = ROOT / "docs/dados/piloto_ao_vivo.json"
BORDO = ROOT / "estado/piloto/bordo.json"
SEM_SINAL_MIN = 35          # um voo cabe em 26 min; passou disso sem sinal, a corrente quebrou


def _min_desde(iso: str | None) -> float | None:
    if not iso:
        return None
    try:
        t = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
        if not t.tzinfo:
            t = t.replace(tzinfo=timezone.utc)
        return round((datetime.now(timezone.utc) - t).total_seconds() / 60, 1)
    except Exception:
        return None


def marcar(evento: str, **campos) -> dict:
    """Chamado a cada passo do voo: decolou, entrou num motor, achou, pousou."""
    d = load_json(VIVO) if VIVO.exists() else {}
    d.update({"evento": evento, "em": now_iso(), **campos})
    d.setdefault("historico", [])
    d["historico"] = ([{"evento": evento, "em": now_iso()[:19],
                        "motor": campos.get("motor"), "detalhe": campos.get("detalhe")}]
                      + d["historico"])[:20]
    write_json(VIVO, d)
    return d


def montar() -> dict:
    """A fotografia completa, com tudo datado para o painel julgar por conta própria."""
    b = load_json(BORDO) if BORDO.exists() else {}
    atual = b.get("missao_atual")
    ms = b.get("missoes") or []
    ultima = ms[0] if ms else None
    voos = load_json(ROOT / "estado/piloto/voos.json") if (ROOT / "estado/piloto/voos.json").exists() else {}
    fila = load_json(ROOT / "estado/piloto/fila_resgate.json") if (ROOT / "estado/piloto/fila_resgate.json").exists() else {}
    its = (fila.get("itens") or {}).values()
    brief = load_json(ROOT / "docs/dados/briefings_piloto.json") if (ROOT / "docs/dados/briefings_piloto.json").exists() else {}
    bv = (brief.get("voos") or [{}])[0]

    sinal = (atual or {}).get("inicio") or (ultima or {}).get("fim") or b.get("em")
    idade = _min_desde(sinal)
    # O MOTOR E O VOO SÃO COISAS DIFERENTES, e confundi-los era a origem da disparidade:
    # o painel dizia "em terra" com 16 voos no dia, porque lia a missão, que só existe
    # enquanto o processo roda. O motor está LIGADO enquanto a corrente de voos se
    # reencadeia; o voo é o que acontece dentro de cada elo dessa corrente.
    pausado = (ROOT / "estado/piloto_pausado").exists()
    motor = "desligado" if pausado else ("parado" if (idade is None or idade > SEM_SINAL_MIN) else "ligado")
    if atual and idade is not None and idade <= 30:
        estado, frase = "em_voo", (f"voando no motor {atual.get('motor')}" if atual.get("motor")
                                   else "decolando — escolhendo o rumo")
    elif motor == "ligado":
        estado, frase = "entre_voos", "entre um voo e outro — o próximo decola em segundos"
    else:
        estado, frase = "parado", "a corrente de voos parou"

    achados_voo = [a for m in ms[:8] for a in (m.get("alvos") or [])][:8]
    d = {
        "motor": motor,
        "motor_frase": {"ligado": "a corrente de voos está ativa: cada voo chama o seguinte",
                        "parado": f"sem sinal há {idade if idade is not None else '—'} min — ninguém reencadeou",
                        "desligado": "em terra por ordem do titular (estado/piloto_pausado)"}[motor],
        "em": now_iso(), "sinal_em": sinal, "minutos_sem_sinal": idade,
        "estado": "pausado_pelo_titular" if pausado else estado,
        "frase": "em terra por ordem do titular" if pausado else frase,
        "proximo_voo": ("em segundos, assim que o atual pousar" if motor == "ligado"
                        else "só quando o titular acionar"),
        "sem_sinal_a_partir_de_min": SEM_SINAL_MIN,
        "missao_atual": atual and {"tipo": atual.get("tipo"), "motor": atual.get("motor"),
                                   "alvo": atual.get("alvo"), "inicio": atual.get("inicio"),
                                   "ha_minutos": _min_desde(atual.get("inicio"))},
        "ultima_missao": ultima and {"tipo": ultima.get("tipo"), "motor": ultima.get("motor"),
                                     "fim": ultima.get("fim"), "ha_minutos": _min_desde(ultima.get("fim")),
                                     "achados": ultima.get("achados"), "licao": ultima.get("licao")},
        "voos_hoje": int(voos.get(date.today().isoformat(), 0)),
        "missoes_registradas": len(ms),
        "missoes_com_achado": sum(1 for m in ms if (m.get("achados") or 0) > 0),
        "achados_recentes": achados_voo,
        "total_abates": b.get("total_abates", 0),
        "resgate": {"aguardando": sum(1 for x in its if x.get("estado") == "aguardando"),
                    "resgatados": sum(1 for x in its if x.get("estado") == "resgatado"),
                    "sem_sucesso": sum(1 for x in its if x.get("estado") == "sem_sucesso")},
        "plano_do_voo": {"aposta": bv.get("aposta"), "pergunta": bv.get("pergunta"),
                         "resultado": bv.get("resultado")},
        "pode_acionar": estado == "parado" and not pausado,
        "como_acionar": "Actions → 07 · Piloto → Run workflow (modo: ciclo)",
    }
    write_json(VIVO, d)
    return d


if __name__ == "__main__":
    print(json.dumps(montar(), ensure_ascii=False, indent=1))
