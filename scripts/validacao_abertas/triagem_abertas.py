"""Triagem das oportunidades abertas sem ouro, na ordem de prioridade da esteira: Goiás → Brasil → internacional → outros estados;
dentro do grupo, nota da rede (maior primeiro) e prazo mais próximo."""
import json,re
from pathlib import Path
R=Path(__file__).resolve().parents[1]
d=json.load(open(R/'docs/dados/fluxo_oportunidades.json'))
rede=json.load(open(R/'docs/dados/rede_neural.json'))['fila_de_validacao']
nota={x['url']:x['nota'] for x in rede}
fi={x['id'] for x in json.load(open(R/'dados/coleta_3_anos/fila_int.json'))}
ITENS=["Objeto","Prazo de inscrição","Resultado","Prazo de recurso","Valor","Órgão / financiador","Território","Esfera","Requisitos","Anexos","Destinação","Área de atuação"]
HOJE='2026-10-03'
rows=[]
for uf,l in d['itens_por_uf'].items():
    for x in l:
        if x.get('selo')=='ouro':continue
        ck=x.get('checklist') or {}
        esf=str((ck.get('Esfera') or {}).get('v') or '').lower()
        if x.get('opressor') in fi or 'internacional' in esf: g='3-INT'
        elif uf=='GO': g='1-GO'
        elif uf=='__nac__': g='2-BR'
        else: g='4-OUTROS'
        feitos=[k for k in ITENS if (ck.get(k) or {}).get('s') in('ok','val','disp')]
        rows.append({'id':x['id'],'grupo':g,'uf':None if uf=='__nac__' else uf,'titulo':x['titulo'],'orgao':x.get('orgao'),'url':x.get('url'),'link_oficial':x.get('link_oficial'),
          'inicio':x.get('inicio'),'fim':x.get('fim'),'tipo':x.get('tipo'),'regime':x.get('regime'),'selo':x.get('selo'),'objeto':x.get('objeto'),
          'validacao':(x.get('validacao') or {}).get('decisao'),'validacao_motivo':(x.get('validacao') or {}).get('motivo'),
          'nota_rede':nota.get(x.get('url')),'itens_feitos':feitos,'itens_faltam':[k for k in ITENS if k not in feitos],
          'checklist':{k:ck.get(k) for k in ITENS if ck.get(k)},'opressor':x.get('opressor')})
rows.sort(key=lambda r:(r['grupo'],-(r['nota_rede'] or 0),r['fim'] or '9999'))
for i,r in enumerate(rows,1): r['ordem']=i
out=R/'dados/validacao_abertas/entrada_triagem.json'
json.dump(rows,open(out,'w'),ensure_ascii=False,indent=1)
from collections import Counter
print(len(rows),Counter(r['grupo'] for r in rows),Counter((r['grupo'],r['tipo']) for r in rows).most_common(12))
print(Counter(r['validacao'] for r in rows))
