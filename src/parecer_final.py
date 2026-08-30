"""Libera o pacote do parecer final somente após sete respostas independentes."""
from __future__ import annotations
import json
import sys
from pathlib import Path
from .nucleo import has_prompt_injection, load_json, now_iso, write_json

REQUIRED={"achados_beneficos","achados_prejudiciais","requisitos","pontuacao_comprovada","pontuacao_potencial","riscos","documentos_faltantes","recomendacao"}

def prepare(case_root):
    case_root=Path(case_root)
    manifest=load_json(case_root/"conselho/manifesto.json"); responses=[]
    for index,item in enumerate(manifest["conselheiros"],1):
        path=case_root/"conselho"/f"{index:02d}_{item['ponto_de_vista']}"/"resposta.json"
        if not path.exists(): return {"status":"aguardando_respostas","recebidas":len(responses),"necessarias":7}
        raw=path.read_text(encoding="utf-8")
        if has_prompt_injection(raw): raise ValueError(f"resposta {index} em quarentena")
        data=json.loads(raw)
        if not REQUIRED <= set(data): raise ValueError(f"resposta {index} incompleta")
        responses.append({"ponto_de_vista":item["ponto_de_vista"],"personalidade_id":item["personalidade"]["id"],"analise":data})
    payload={"liberado_em":now_iso(),"modelo_final_env":"FAROL_FINAL_MODEL","instrucao":"Atue como especialista sênior em captação, execução e prestação de contas. Resolva divergências com base em evidência, recalcule os requisitos, não invente fatos e produza o plano final, o manual do presidente e a matriz de prestação de contas.","respostas_independentes":responses}
    write_json(case_root/"parecer_final/pacote_liberado.json",payload); return {"status":"liberado","respostas":7}

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("uso: python -m src.parecer_final dados/associacoes/SLUG/farol/casos/ID")
    print(json.dumps(prepare(Path(sys.argv[1])),ensure_ascii=False,indent=2))
