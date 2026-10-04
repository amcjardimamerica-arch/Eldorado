"""Triagem dos livros de Goiás sem ouro: destino de cada um (escopo, regime, inaplicável) e fila por família de pesquisa."""
import json, re, collections, urllib.parse as U
L = json.load(open('docs/dados/relatorios_livros.json'))['livros']
M = {m['id']: m for m in json.load(open('biblioteca_alexandria/fontes/motores.json'))['motores']}
ESC = ('validado_parcial', 'serie_indicada_ordinal', 'verificado_sem_serie', 'serie_confirmada_sem_datas')
INAP = {'arquivar': 'ruido', 'ruido_diario': 'ruido', 'ruido_portal': 'ruido', 'fora_escopo_compra': 'fora_perfil_compra',
        'fora_escopo_contratacao': 'fora_perfil_contratacao', 'ato_derivado': 'derivado', 'ciclo_unico': 'ciclo_unico'}
REGIME = ('fundo', 'emenda', 'mp', 'judicial', 'estrutural', 'indice', 'regime_incentivo_fiscal')
def familia(m):
    o = (m.get('orgao') or '') + ' ' + (m.get('programa') or ''); p = m.get('pagina') or ''; h = U.urlparse(p).netloc
    if 'goiania.go.gov.br' in h or re.search(r'goi[âa]nia', o, re.I) and not re.search(r'diário|aparecida', o, re.I): return 'goiania'
    if re.search(r'secult|cultura|fundo de arte|pnab|fica', o, re.I) or '/cultura/' in p: return 'secult_go'
    if h.endswith('.go.gov.br') and h not in ('goias.gov.br',) or re.search(r'prefeitura|munic[íi]pio|fundo municipal', o, re.I): return 'municipios'
    if 'pncp' in h: return 'municipios'
    return 'estado_outros'
out = collections.defaultdict(list); tri = {}
for l in L:
    if l['bloco'] != 'GO' or l['selo'] == 'ouro': continue
    sit = l['situacao']; cod = sit.split(':')[1] if ':' in sit else sit
    m = M[l['id']]
    if cod in INAP: tri[l['id']] = {'destino': 'inaplicavel', 'tipo': INAP[cod], 'codigo': cod}; continue
    if cod == 'fora_escopo_perfil':
        tri[l['id']] = {'destino': 'revisar', 'tipo': 'fora_perfil', 'codigo': cod}; fam = familia(m)
    elif cod in REGIME:
        tri[l['id']] = {'destino': 'regime', 'tipo': cod, 'codigo': cod}; fam = 'regimes'
    elif cod == 'validado_parcial' or sit in ESC:
        tri[l['id']] = {'destino': 'escopo', 'tipo': sit, 'codigo': cod}; fam = familia(m)
    else:
        tri[l['id']] = {'destino': 'revisar', 'tipo': sit, 'codigo': cod}; fam = familia(m)
    out[fam].append(l['id'])
json.dump(tri, open('dados/coleta_3_anos/ouro/triagem_inicial.json', 'w'), ensure_ascii=False, indent=1)
for f, ids in out.items():
    tr = []
    for i in ids:
        m = M[i]; r = json.load(open(f'dados/coleta_3_anos/relatorios/{i}.json'))
        tr.append({'id': i, 'livro': r['livro'], 'orgao': m.get('orgao'), 'pagina': m.get('pagina'), 'triagem': tri[i]['destino'], 'situacao': r['validacao']['situacao'],
                   'motivo_atual': r['validacao']['motivo'][:300],
                   'edicoes_ja_comprovadas': [{'mes': e['mes'], 'titulo': e['titulo'][:90], 'pagina_oficial': e['pagina_oficial']} for e in r['edicoes']],
                   'paginas_do_historico': sorted({h.get('pagina_oficial') for h in (m.get('historico') or []) if h.get('pagina_oficial')})[:6]})
    json.dump(tr, open(f'dados/coleta_3_anos/ouro/trabalho_{f}.json', 'w'), ensure_ascii=False, indent=1)
print({f: len(v) for f, v in out.items()}, collections.Counter(t['destino'] for t in tri.values()))
