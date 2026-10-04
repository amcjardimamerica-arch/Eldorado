import json,glob,datetime
from collections import Counter
R='/home/claude/Eldorado2/'
ITENS=["Objeto","Prazo de inscrição","Resultado","Prazo de recurso","Valor","Órgão / financiador","Território","Esfera","Requisitos","Anexos","Destinação","Área de atuação"]
tri={r['id']:r for r in json.load(open(R+'dados/validacao_abertas/entrada_triagem.json'))}
S=[]
for f in sorted(glob.glob(R+'dados/validacao_abertas/saida/*.json')): S+=json.load(open(f))
def s(x): 
    if isinstance(x,dict):
        r=x.get('resposta') or x.get('elegivel') or ''
        rest='; '.join(f"{k}: {v}" for k,v in x.items() if k not in('resposta','elegivel') and v)
        return (str(r)+(': ' if r and rest else '')+rest) if (r or rest) else json.dumps(x,ensure_ascii=False)
    if isinstance(x,list): return '; '.join(map(str,x))
    return '' if x is None else str(x)
out=[]
for x in S:
    t=tri[x['id']]
    it=x.get('itens') or {}
    for k in ITENS:
        if k not in it or not isinstance(it[k],dict) or it[k].get('estado') not in('confirmado','nao_informado','dispensado','nao_lido'):
            it[k]={'estado':'nao_lido','motivo':'não preenchido pelo validador'}
    c=Counter(it[k]['estado'] for k in ITENS)
    sem_leitura=(c['nao_lido']==12) or not x.get('pagina_oficial')
    base='sem fonte oficial lida' if sem_leitura else ('leitura parcial' if c['nao_lido'] else 'leitura completa dos 12 pontos')
    if x['veredito']=='nao_e_oportunidade_osc' and c['nao_lido']>=5 and not (x.get('pagina_oficial') or '').startswith('http'): base='classificado pelo título (sem leitura)'
    # selo final
    prop=x.get('selo_proposto')
    if not x.get('pagina_oficial'): selo='bronze'
    elif prop=='ouro' and c['nao_lido']==0 and c['nao_informado']<=3 and x.get('fim') and x['veredito'] in('aberta_valida','aberta_fora_abrangencia'): selo='ouro'
    else: selo='prata'
    out.append({'ordem':t['ordem'],'id':x['id'],'grupo':t['grupo'],'uf':t['uf'],'titulo':t['titulo'],'orgao':t['orgao'],'selo_sistema':t['selo'],
      'veredito':x['veredito'],'selo_validado':selo,'selo_proposto_validador':prop,'base_leitura':base,'pagina_oficial':x.get('pagina_oficial'),'inicio':x.get('inicio'),'fim':x.get('fim'),
      'elegibilidade_amc':s(x.get('elegibilidade_amc')),'elig':(lambda e:'sim' if e.startswith('sim') else 'parcial' if e.startswith('parcial') else 'nao_avaliada' if 'nao_avaliada' in e or 'não avaliada' in e else 'nao')(s(x.get('elegibilidade_amc')).strip().lower()),'parecer':s(x.get('parecer')),'proximo_passo':s(x.get('proximo_passo')),'riscos':s(x.get('riscos')),'observacoes':s(x.get('observacoes')),
      'injecao_detectada':bool(x.get('injecao_detectada')),'itens':it,'contagem_itens':dict(c),'nota_rede':t.get('nota_rede')})
out.sort(key=lambda r:r['ordem'])
json.dump(out,open(R+'dados/validacao_abertas/consolidado.json','w'),ensure_ascii=False,indent=1)
print(len(out),Counter(r['veredito'] for r in out),Counter(r['selo_validado'] for r in out),Counter(r['base_leitura'] for r in out))
print(Counter((r['grupo'],r['veredito']) for r in out))
print(Counter(r['elegibilidade_amc'][:10].lower() for r in out if r['veredito'] in('aberta_valida','aberta_fora_abrangencia')).most_common(10))
