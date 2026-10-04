import json,glob,sys
from collections import Counter
ITENS=["Objeto","Prazo de inscrição","Resultado","Prazo de recurso","Valor","Órgão / financiador","Território","Esfera","Requisitos","Anexos","Destinação","Área de atuação"]
base='/home/claude/Eldorado2/dados/validacao_abertas/'
ok=True;tot=Counter()
for f in sorted(glob.glob(base+'saida/*.json')):
    n=f.split('/')[-1][:-5]
    lote=json.load(open(base+f'lotes/{n}.json')); s=json.load(open(f))
    ids=[x['id'] for x in lote]; sid=[x.get('id') for x in s]
    prob=[]
    if ids!=sid: prob.append(f'ids divergentes {len(ids)} vs {len(sid)}')
    for x in s:
        it=x.get('itens') or {}
        for k in ITENS:
            e=(it.get(k) or {}).get('estado')
            if e not in('confirmado','nao_informado','dispensado','nao_lido'): prob.append((x.get('id'),k,e))
        if x.get('selo_proposto')=='ouro':
            if any((it.get(k) or {}).get('estado')=='nao_lido' for k in ITENS) or not x.get('pagina_oficial') or not x.get('fim'): prob.append((x['id'],'ouro sem requisitos'))
        tot[(x.get('veredito'),x.get('selo_proposto'))]+=1
    print(n,len(s),'problemas:',prob[:6],len(prob))
print(sorted(tot.items(),key=str))
