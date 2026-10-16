"""Ajustes da importação dos lotes A, B e C (Chrome, 11/10/2026), reproduzíveis depois do importador:
- 'ouro' que não fecha 12/12 com prova completa (núcleo certificado, PDF com página) → validacao_manual, com o motivo;
- vermelho do lote C (lido SEM as ferramentas do Chrome: PDF do PNCP/diário ilegível no leitor web) e vermelho com
  menos de 8 rotas registradas → motivo 'refazer no Chrome';
- lista biblioteca_alexandria/livros/_acervo/revisoes/fila_chrome_2026_10_11/refazer_no_chrome.json com esses registros."""
import collections, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import importar_revisao_abertas as I

PASTA = ROOT / "biblioteca_alexandria/livros/_acervo/revisoes/fila_chrome_2026_10_11"


def main() -> dict:
    v = json.loads(I.VEREDITOS.read_text(encoding="utf-8")); V = v["vereditos"]; aj = collections.Counter(); refazer = []
    for L in "ABC":
        d = json.loads((PASTA / f"resultados/resultado_ABERTAS_CHROME-LOTE-{L}_2026-10-11.json").read_text(encoding="utf-8"))
        lote = {r["id"]: r for r in json.loads((PASTA / f"lote_{L}.json").read_text(encoding="utf-8"))["registros"]}
        for k, x in d.items():
            if k not in V:
                continue
            if x.get("veredito") == "ouro":
                cert, av = I.certidao_de({"id": k, **x}, "chk")
                if len(cert["itens"]) + len(cert["dispensas"]) < 12 or not all(c in cert["itens"] for c in I.NUCLEO):
                    itens = ", ".join(a.split("item ")[1].split(" sem")[0] for a in av if "item " in a)
                    V[k].update(veredito="validacao_manual", motivo=f"ouro recusado na importação: prova incompleta ({itens}: página do PDF ausente) — o Cartório certifica ao ler o PDF")
                    aj["ouro → vermelho (prova incompleta)"] += 1; refazer.append({**lote.get(k, {}), "motivo_refazer": V[k]["motivo"], "lote_origem": L})
            elif x.get("veredito") == "validacao_manual":
                rotas = len({t.get("rota") for t in (x.get("tentativas") or [])})
                if L == "C":
                    V[k]["motivo"] = ("lote C lido sem as ferramentas do Chrome (leitor web: PDF do PNCP/diário chega ilegível) — refazer no Chrome. " + str(x.get("parecer") or ""))[:400]
                    aj["vermelho do lote C (sem Chrome)"] += 1; refazer.append({**lote.get(k, {}), "motivo_refazer": "lido sem o Chrome", "lote_origem": L})
                elif rotas < 8:
                    V[k]["motivo"] = (f"só {rotas} das 8 rotas registradas — refazer no Chrome. " + str(x.get("parecer") or ""))[:400]
                    aj["vermelho com menos de 8 rotas"] += 1; refazer.append({**lote.get(k, {}), "motivo_refazer": f"{rotas} de 8 rotas", "lote_origem": L})
                else:
                    V[k]["motivo"] = str(x.get("parecer") or V[k].get("motivo") or "")[:400]
    I.VEREDITOS.write_text(json.dumps(v, ensure_ascii=False, indent=1), encoding="utf-8")
    (PASTA / "refazer_no_chrome.json").write_text(json.dumps({"gerado_em": "2026-10-11", "total": len(refazer), "registros": refazer,
        "regra": "vermelhos que não esgotaram as 8 rotas no Chrome: refazer no Claude no Chrome"}, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"ajustes": dict(aj), "refazer_no_chrome": len(refazer)}


if __name__ == "__main__":
    print(json.dumps(main(), ensure_ascii=False))
