"""Depois do importador, para QUALQUER lote: 'ouro' que não fecha 12/12 com prova completa (núcleo comprovado, PDF com
página) vira validacao_manual com o motivo; o vermelho sem as 8 rotas registradas ganha o aviso 'refazer no Chrome'.
Uso: python scripts/ajustar_ouro_sem_prova.py <pasta dos resultados> <origem>"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import importar_revisao_abertas as I


def ajustar(pasta: Path, origem: str) -> dict:
    v = json.loads(I.VEREDITOS.read_text(encoding="utf-8")); V = v["vereditos"]; aj = {"ouro_recusado": [], "vermelho_sem_8_rotas": []}
    for f in sorted(pasta.glob("resultado_ABERTAS_*.json")):
        d = json.loads(f.read_text(encoding="utf-8")); d = d.get("resultado", d) if isinstance(d, dict) and "resultado" in d else d
        for k, x in d.items():
            if k not in V or (V[k].get("origem") != origem):
                continue
            if x.get("veredito") == "ouro":
                cert, av = I.certidao_de({"id": k, **x}, "chk")
                if len(cert["itens"]) + len(cert["dispensas"]) < 12 or not all(c in cert["itens"] for c in I.NUCLEO):
                    falt = [c for c in I.DOZE if c not in cert["itens"] and c not in cert["dispensas"]]
                    V[k].update(veredito="validacao_manual", motivo=f"ouro recusado na importação: sem prova completa de {', '.join(falt)}")
                    aj["ouro_recusado"].append(k)
            elif x.get("veredito") == "validacao_manual":
                if len({t.get("rota") for t in (x.get("tentativas") or [])}) < 8:
                    V[k]["motivo"] = ("menos de 8 rotas registradas — refazer no Chrome. " + str(x.get("parecer") or ""))[:400]; aj["vermelho_sem_8_rotas"].append(k)
                else:
                    V[k]["motivo"] = str(x.get("parecer") or V[k].get("motivo") or "")[:400]
    I.VEREDITOS.write_text(json.dumps(v, ensure_ascii=False, indent=1), encoding="utf-8")
    return {k: len(v_) for k, v_ in aj.items()}


if __name__ == "__main__":
    print(json.dumps(ajustar(Path(sys.argv[1]), sys.argv[2]), ensure_ascii=False))
