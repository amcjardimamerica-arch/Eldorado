"""LOTE DO CHROME — EXCEÇÃO (titular, 11/10/2026; Dr. Fábio, conselho da arquitetura).

Só entram oportunidades do REPOSITÓRIO ÚNICO (o mesmo universo da tela inicial) cujo próximo passo é o Chrome, isto é,
depois das 10 abordagens do Cartório na fonte. Cada registro leva os itens já comprovados (não refazer) e os que faltam.
O lote só é gravado se o total bater com a fila do Chrome do repositório — sem isso, recusa (não repete o erro de
11/10, quando os lotes saíram de outro conjunto). Saída: dados/revisoes/fila_chrome_atual/lote_<N>.json (até 150 por lote).
"""
import json
import sys
from datetime import date
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import repositorio_unico as R  # noqa: E402


def gerar(tamanho: int = 150) -> dict:
    fila = R.fila("Chrome")
    resumo = json.loads(R.RESUMO.read_text(encoding="utf-8")) if R.RESUMO.exists() else {}
    if len(fila) != int(resumo.get("fila_chrome", -1)):
        raise SystemExit(f"RECUSADO: a fila ({len(fila)}) não bate com o resumo do repositório ({resumo.get('fila_chrome')}). Reconstrua o repositório.")
    pasta = ROOT / "dados/revisoes/fila_chrome_atual"; pasta.mkdir(parents=True, exist_ok=True)
    for f in pasta.glob("lote_*.json"):
        f.unlink()
    lotes = [fila[i:i + tamanho] for i in range(0, len(fila), tamanho)]
    for n, L in enumerate(lotes, 1):
        regs = [{"id": x["id"], "ids_origem": x["ids_origem"], "titulo": x["titulo"], "url_registro": x["url"], "site_oficial_certificado": x["link_oficial"],
                 "orgao": x["orgao"], "uf": x["uf"], "fim_conhecido": x["fim"], "origem": x["origem"],
                 "itens_ja_certificados": {k: v for k, v in x["itens"].items() if v["estado"] in ("comprovado", "dispensado")},
                 "itens_a_buscar": x["faltam"], "tentativas_do_cartorio": x["cartorio"]["tentativas"]} for x in L]
        (pasta / f"lote_{n}.json").write_text(json.dumps({"gerado_em": date.today().isoformat(), "lote": n, "de": len(lotes), "total": len(regs),
                                                          "universo": "repositório único — próximo passo: Chrome (exceção)", "registros": regs}, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"fila_chrome": len(fila), "lotes": len(lotes), "conferido_com_o_resumo": True}


if __name__ == "__main__":
    print(json.dumps(gerar(), ensure_ascii=False))
