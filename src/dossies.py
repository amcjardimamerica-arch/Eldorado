from __future__ import annotations

import json
from collections import Counter
from .nucleo import ROOT, load_json, slug, write_json

FIELDS=("id","status","titulo","url","coletado_em","ano_referencia","ano_pesquisado","prazo_texto","confianca","hash_evidencia")

def run() -> int:
    db=ROOT/"dados/oportunidades/oportunidades.jsonl"; groups={}
    if not db.exists(): return 0
    sources={x["id"]:x for x in load_json(ROOT/"config/fontes.json")["fontes"]}
    for line in db.read_text(encoding="utf-8").splitlines():
        if line.strip():
            item=json.loads(line); groups.setdefault(item["fonte_id"],[]).append(item)
    for fid,items in groups.items():
        source=sources.get(fid,{})
        is_donor=source.get("tipo") in {"empresa","empresa_publica","fundacao_empresarial"}
        base="doadores" if is_donor else "financiadores"
        folder=ROOT/"dados"/base/slug(fid); folder.mkdir(parents=True,exist_ok=True)
        compact={"schema":list(FIELDS),"linhas":[[x.get(key) for key in FIELDS] for x in items]}
        write_json(folder/"eventos.compacto.json",compact)
        verified=[x for x in items if x.get("status") in {"verificada_primaria","verificada_dupla","elegivel","em_preparacao","submetida","selecionada","em_execucao","prestacao_de_contas","encerrada"}]
        clues=[x for x in items if x not in verified]
        years=Counter(str(x.get("ano_pesquisado") or x.get("ano_referencia") or (x.get("coletado_em") or "")[:4]) for x in items)
        lines=[f"# {items[0].get('fonte_nome',fid)}","",f"- Classe: `{base}`",f"- Fonte: `{fid}`",f"- Eventos verificados: {len(verified)}",f"- Pistas aguardando confirmação: {len(clues)}",f"- Distribuição por ano pesquisado/coletado: {dict(sorted(years.items()))}","","## Padrões","","Nenhum padrão é afirmado automaticamente sem ao menos duas ocorrências independentes verificadas e revisão humana.","","## Eventos e pistas","" ]
        lines += [f"- [{x['titulo']}]({x['url']}) — coletado em {x['coletado_em']}" for x in items[-50:]]
        (folder/"dossie.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    return len(groups)

if __name__ == "__main__": print(run())
