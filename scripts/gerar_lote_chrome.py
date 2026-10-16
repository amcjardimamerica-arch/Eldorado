"""LOTE DO CHROME — EXCEÇÃO (titular, 11/10/2026; Dr. Fábio, conselho da arquitetura).

Só entram oportunidades do REPOSITÓRIO ÚNICO (o mesmo universo da tela inicial) cujo próximo passo é o Chrome, isto é,
depois das 10 abordagens do Cartório na fonte. Cada registro leva os itens já comprovados (não refazer) e os que faltam.
O lote só é gravado se o total bater com a fila do Chrome do repositório — sem isso, recusa (não repete o erro de
11/10, quando os lotes saíram de outro conjunto). Saída: biblioteca_alexandria/livros/_acervo/revisoes/fila_chrome_atual/lote_<N>.json (até 150 por lote).
"""
import json
import sys
from datetime import date
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import repositorio_unico as R  # noqa: E402


def gerar(tamanho: int = 150) -> dict:
    # 16/10 (titular): o lote sai das PENDÊNCIAS DO CARTÓRIO (ponto central do que falta); o mesmo universo do repositório
    pend = json.loads((ROOT / "docs/dados/cartorio_pendencias.json").read_text(encoding="utf-8"))
    alvo = {o["id"] for o in pend.get("oportunidades") or [] if o.get("proximo_passo") == "Claude no Chrome"}
    regs = (json.loads(R.SAIDA.read_text(encoding="utf-8")) if R.SAIDA.exists() else {}).get("registros") or []
    fila = [x for x in regs if x["id"] in alvo]
    if len(fila) != len(alvo):
        raise SystemExit(f"RECUSADO: {len(alvo)} pendências para o Chrome, {len(fila)} no repositório. Reconstrua o repositório.")
    pasta = ROOT / "biblioteca_alexandria/livros/_acervo/revisoes/fila_chrome_atual"; pasta.mkdir(parents=True, exist_ok=True)
    for f in pasta.glob("lote_*.json"):
        f.unlink()
    lotes = [fila[i:i + tamanho] for i in range(0, len(fila), tamanho)]
    for n, L in enumerate(lotes, 1):
        regs = [{"id": x["id"], "ids_origem": x["ids_origem"], "titulo": x["titulo"], "url_registro": x["url"], "site_oficial_certificado": x["link_oficial"],
                 "orgao": x["orgao"], "uf": x["uf"], "fim_conhecido": x["fim"], "origem": x["origem"],
                 "itens_ja_certificados": {k: v for k, v in x["itens"].items() if v["estado"] in ("comprovado", "dispensado")},
                 "itens_a_buscar": x["faltam"], "tentativas_do_cartorio": x["cartorio"]["tentativas"],
                 # 11/10: a situação de cada um dos 12 e ONDE BUSCAR (editais anteriores e páginas do livro na Biblioteca)
                 "situacao_dos_12": {k: {"comprovado": "comprovado (não refazer)", "dispensado": "dispensado com justificativa (não refazer)",
                                         "nao_comprovado": f"a completar: o motor leu '{str(v.get('valor') or '')[:60]}', falta a prova no documento oficial",
                                         "falta": "a completar: buscar no documento oficial; se o edital não fala, dispensa 'nao_consta' com os documentos lidos"}[v["estado"]]
                                     for k, v in x["itens"].items()},
                 "onde_buscar": x.get("onde_buscar") or [], "livro": x.get("livro"), "editais_anteriores_do_livro": (x.get("livro_historico") or {}).get("ultimos") or []} for x in L]
        (pasta / f"lote_{n}.json").write_text(json.dumps({"gerado_em": date.today().isoformat(), "lote": n, "de": len(lotes), "total": len(regs),
                                                          "regra_de_resolucao": R.REGRA_EXTERNA,
                                                          "universo": "repositório único — próximo passo: Chrome (exceção)", "registros": regs}, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"fila_chrome": len(fila), "lotes": len(lotes), "conferido_com_o_resumo": True}


if __name__ == "__main__":
    print(json.dumps(gerar(), ensure_ascii=False))
