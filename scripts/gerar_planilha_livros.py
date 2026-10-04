import json, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
C=json.load(open("/tmp/catnow.json"))["motores"]; DOZE=json.load(open("config/esteira.json"))["doze_dados"]
P=json.load(open("/tmp/perdas48.json")); A={x["id"]:x for x in json.load(open("/tmp/cat48.json"))["motores"]}
F=Font(name="Arial",size=10); FB=Font(name="Arial",size=10,bold=True,color="FFFFFF"); AZ=Font(name="Arial",size=10,color="0000FF")
CAB=PatternFill("solid",fgColor="1F4E78"); CABU=PatternFill("solid",fgColor="2E75B6"); ENT=PatternFill("solid",fgColor="DDEBF7")
def t(v,n=400): return None if v in (None,"",[],{}) else (str(v)[:n] if not isinstance(v,(int,float)) else v)
wb=Workbook(); L=wb.active; L.title="Leia-me"
txt=["ELDORADO — Livros da Biblioteca (fonte de atualização do sistema) · 04/10/2026",
"Cada linha da aba Livros é um livro (a memória de um programa: edições, prazos, valores, condições). As colunas cinza-escuro são o que o sistema sabe hoje.",
"PREENCHER: só as colunas de cabeçalho AZUL e fundo azul-claro (a partir de 'ATUALIZAR — veredito'), texto em azul. Uma linha por livro; não altere as colunas do sistema.",
"Meta: deixar cada livro em OURO — série de edições em 2 anos distintos com documento oficial (edital, regulamento, cronograma, ata), ou regime permanente documentado — ou declará-lo INAPLICÁVEL com prova.",
"Regra do leitor documental: notícia é indício; cada item vale só com valor + trecho literal + documento (URL do arquivo) + página.",
"Veredito: ouro | ouro_regime | inaplicavel | pendente. Edição: ano, início e fim da inscrição (AAAA-MM-DD) e o documento.",
"Aba 'Perdas 48h': livros que sumiram e dados perdidos nas últimas 48 h, com os valores de antes — restaurar ou confirmar a exclusão.",
"Exemplo de preenchimento na linha 3 da aba Livros (exemplo — apague antes de importar)."]
for i,x in enumerate(txt,1): L.cell(i,1,x).font=Font(name="Arial",size=11 if i>1 else 13,bold=(i==1))
L.column_dimensions["A"].width=160
S=wb.create_sheet("Livros")
base=["id","nome","programa","órgão","UF","geo","município","esfera","área","família","tipo","público","iniciativa","página atual","site oficial (esteira)",
 "selo do livro","via do selo","estrela (esteira)","estante","nota da rede","nº edições","anos das edições","última edição — início","última edição — fim","última edição — página",
 "próxima data prevista","regime do prazo","certeza do prazo","12 resolvidos","12 faltando"]
for k in DOZE: base+=[f"{k} — situação",f"{k} — valor"]
base+=["pareceres (último)","coleta — classificação/observação","decisão anterior (validação)"]
upd=["ATUALIZAR — veredito","ATUALIZAR — site oficial confirmado","ATUALIZAR — edição A: ano","ATUALIZAR — edição A: início","ATUALIZAR — edição A: fim","ATUALIZAR — edição A: documento",
 "ATUALIZAR — edição B: ano","ATUALIZAR — edição B: início","ATUALIZAR — edição B: fim","ATUALIZAR — edição B: documento","ATUALIZAR — itens preenchidos (item: valor | trecho | documento | página)",
 "ATUALIZAR — itens dispensados (item: motivo)","ATUALIZAR — inaplicável: tipo e prova","ATUALIZAR — observação"]
cols=base+upd
for j,h in enumerate(cols,1):
    c=S.cell(1,j,h); c.font=FB; c.fill=CABU if h.startswith("ATUALIZAR") else CAB; c.alignment=Alignment(wrap_text=True,vertical="top")
ex=["(exemplo)","Edital PNAB — Goiânia","PNAB",None,"GO","GO","Goiânia"]+[None]*(len(base)-7)
exu=["ouro","https://www.goiania.go.gov.br/secult/","2025","2025-03-24","2025-04-25","https://.../edital-2025.pdf","2026","2026-03-10","2026-04-10","https://.../edital-2026.pdf",
     "Valor: R$ 50.000 | 'o valor total é de R$ 50.000' | https://.../edital-2026.pdf | 3","Prazo de recurso: o edital não prevê recurso",None,"lido no edital"]
for j,v in enumerate(ex+exu,1):
    c=S.cell(2,j,v); c.font=AZ if j>len(base) else Font(name="Arial",size=10,italic=True,color="808080")
for i,x in enumerate(C,3):
    e=x.get("esteira") or {}; sl=x.get("selo_livro") or {}; lv=x.get("livro") or {}; ck=lv.get("checklist") or {}; c12=x.get("checklist12") or {}
    hs=sorted([h for h in x.get("historico") or [] if isinstance(h,dict)],key=lambda h:str(h.get("fim") or h.get("inicio") or h.get("ano") or ""))
    u=hs[-1] if hs else {}; anos=sorted({str(h.get("ano") or str(h.get("fim") or h.get("inicio") or "")[:4]) for h in hs if (h.get("ano") or h.get("fim") or h.get("inicio"))})
    pv=sl.get("previsao") or x.get("preditivo") or {}
    linha=[x.get("id"),x.get("nome_classificado"),x.get("programa"),x.get("orgao"),x.get("uf"),x.get("geo"),x.get("municipio"),x.get("esfera"),x.get("objeto_area") or x.get("area_atuacao"),
           x.get("familia"),x.get("tipo") or x.get("tipo_objeto"),x.get("publico"),lv.get("iniciativa") or x.get("iniciativa"),x.get("pagina"),e.get("site_oficial"),
           sl.get("selo"),sl.get("via"),e.get("selo"),e.get("estante"),x.get("nota_rede"),len(hs),", ".join(a for a in anos if a),u.get("inicio"),u.get("fim"),u.get("pagina_oficial"),
           x.get("proxima_data") or (pv.get("proxima_janela") if isinstance(pv,dict) else None),x.get("regime_prazo"),x.get("certeza_prazo"),e.get("doze_resolvidos"),", ".join(e.get("doze_faltando") or [])]
    for k in DOZE:
        v=ck.get(k) or {}; d=c12.get(k)
        vv=str(v.get("v") or "")
        sit=("dispensado" if (d or vv.lower().startswith("dispensad")) else (f"informado ({v.get('de')}, {v.get('em')})" if vv else None)) if (v or d) else None
        linha+=[sit,(d if isinstance(d,str) else (vv or None)) if (v or d) else None]
    par=(lv.get("pareceres") or [])[-1:] or [{}]
    linha+=[t((par[0].get("decisao") or "")+" — "+(par[0].get("motivo") or "") if par[0] else None,500),t(x.get("livro_coleta") or x.get("coleta"),500),t((x.get("validacao") or {}).get("decisao") if isinstance(x.get("validacao"),dict) else x.get("validacao"))]
    for j,v in enumerate(linha,1): S.cell(i,j,t(v)).font=F
    for j in range(len(base)+1,len(cols)+1):
        c=S.cell(i,j); c.fill=ENT; c.font=AZ
S.freeze_panes="C2"; S.auto_filter.ref=f"A1:{get_column_letter(len(cols))}{len(C)+2}"
for j in range(1,len(cols)+1): S.column_dimensions[get_column_letter(j)].width=14 if j>2 else (18 if j==1 else 40)
PZ=wb.create_sheet("Perdas 48h"); h=["tipo","id","nome (48 h atrás)","órgão","UF","página","site oficial (48 h atrás)","selo (48 h atrás)","citado por outro livro?","ATUALIZAR — restaurar ou confirmar exclusão"]
for j,v in enumerate(h,1): c=PZ.cell(1,j,v); c.font=FB; c.fill=CABU if v.startswith("ATUALIZAR") else CAB
r=2
for i in P["sumiram"]:
    a=A[i]; vals=["livro sumiu",i,a.get("nome_classificado") or a.get("programa"),a.get("orgao"),a.get("uf"),a.get("pagina"),(a.get("esteira") or {}).get("site_oficial"),(a.get("selo_livro") or {}).get("selo"),"sim" if i in P["absorvidos"] else "não"]
    for j,v in enumerate(vals,1): PZ.cell(r,j,t(v)).font=F
    PZ.cell(r,10).fill=ENT; r+=1
for k,ids in P["perdas"].items():
    for i in ids:
        a=A[i]; vals=[k,i,a.get("nome_classificado") or a.get("programa"),a.get("orgao"),a.get("uf"),a.get("pagina"),(a.get("esteira") or {}).get("site_oficial"),(a.get("selo_livro") or {}).get("selo"),"—"]
        for j,v in enumerate(vals,1): PZ.cell(r,j,t(v)).font=F
        PZ.cell(r,10).fill=ENT; r+=1
for j,w in enumerate([22,20,45,30,6,45,45,10,12,30],1): PZ.column_dimensions[get_column_letter(j)].width=w
R=wb.create_sheet("Resumo"); n=len(C)+2
R["A1"]="Selo do livro por região (fórmulas sobre a aba Livros)"; R["A1"].font=Font(name="Arial",size=12,bold=True)
geo_col=get_column_letter(cols.index("geo")+1); selo_col=get_column_letter(cols.index("selo do livro")+1)
R.append([]); R.append(["região","ouro","prata","bronze","sem selo","total"])
for g in ["GO","BR","INT"]:
    rr=R.max_row+1; R.append([g]+[f'=COUNTIFS(Livros!${geo_col}$3:${geo_col}${n},"{g}",Livros!${selo_col}$3:${selo_col}${n},"{s}")' for s in ("ouro","prata","bronze")]+[f'=COUNTIFS(Livros!${geo_col}$3:${geo_col}${n},"{g}",Livros!${selo_col}$3:${selo_col}${n},"")',f"=SUM(B{rr}:E{rr})"])
rr=R.max_row+1; R.append(["todos"]+[f'=COUNTIF(Livros!${selo_col}$3:${selo_col}${n},"{s}")' for s in ("ouro","prata","bronze")]+[f'=COUNTBLANK(Livros!${selo_col}$3:${selo_col}${n})',f"=SUM(B{rr}:E{rr})"])
R.append([]); R.append(["Fonte: catálogo da Biblioteca (main, 04/10/2026), antes da aplicação do leitor documental de Goiás. 'outros estados' = total − GO − BR − INT."])
for row in R.iter_rows():
    for c in row: c.font=Font(name="Arial",size=10,bold=(c.row==3))
R.column_dimensions["A"].width=16
wb.save(sys.argv[1]); print("linhas de livros:",len(C),"· colunas:",len(cols),"· perdas listadas:",r-2)
