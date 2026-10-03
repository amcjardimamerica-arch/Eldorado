# ADENDO 2 — leitura pelo navegador (Brasil) — prevalece sobre o ADENDO 1

Você recebeu um ID de aba do Chrome (tabId) exclusivo. Use SÓ essa aba (ferramentas mcp__claude-in-chrome__navigate e mcp__claude-in-chrome__javascript_tool; não use computer/cliques, não abra outras abas, NUNCA navegue direto para URL de arquivo .txt/.pdf/.zip/.doc — isso baixa arquivo no computador do titular; leia arquivos SEMPRE por fetch() dentro do javascript_tool).
WebFetch continua disponível para páginas HTML comuns.

## A) PNCP (link pncp.gov.br/app/editais/<cnpj>/<ano>/<seq>)
1. Uma vez: navegue a aba para https://pncp.gov.br/api/consulta/swagger-ui/index.html
2. No javascript_tool, defina (uma vez por página) e use:
```js
window.P = window.P || (async ()=>{ const m=await import('https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.0.379/pdf.min.mjs'); m.GlobalWorkerOptions.workerSrc='https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.0.379/pdf.worker.min.mjs'; return m; })();
window.sleep=ms=>new Promise(r=>setTimeout(r,ms));
window.pdfTexto=async (url,maxPag=40)=>{ const pdfjs=await P; const b=await fetch(url).then(r=>r.arrayBuffer()); const d=await pdfjs.getDocument({data:b}).promise; let t=''; for(let i=1;i<=Math.min(d.numPages,maxPag);i++){const p=await d.getPage(i); t+=(await p.getTextContent()).items.map(x=>x.str).join(' ')+'\n';} return t.replace(/\s+/g,' '); };
window.janelas=(t,rx=/(inscri[çc][õo]es|prazo|recurso|resultado|valor|R\$|habilita|requisito|document|anexo|poder[aã]o participar|objeto|vig[êe]ncia|organiza[çc][õo]es da sociedade civil|OSC)/gi,larg=260,max=14)=>{const o=[];let m,ult=-1e9;while((m=rx.exec(t))&&o.length<max){if(m.index-ult<larg)continue;ult=m.index;o.push(t.slice(Math.max(0,m.index-80),m.index+larg));}return o;};
window.pncp=async (cnpj,ano,seq)=>{ const c=await fetch(`/api/consulta/v1/orgaos/${cnpj}/compras/${ano}/${seq}`).then(r=>r.ok?r.json():{erro:r.status}); await sleep(1200);
  const a=await fetch(`/api/pncp/v1/orgaos/${cnpj}/compras/${ano}/${seq}/arquivos`).then(r=>r.ok?r.json():[]); await sleep(1200);
  const ed=(a||[]).find(x=>/edital/i.test(x.tipoDocumentoNome||x.titulo||''))||(a||[])[0]; let tx='';
  if(ed){ try{ tx=await pdfTexto(ed.url);}catch(e){tx='ERRO PDF '+e;} }
  return {compra:{objeto:c.objetoCompra,orgao:c.orgaoEntidade?.razaoSocial,unidade:c.unidadeOrgao?.nomeUnidade,municipio:c.unidadeOrgao?.municipioNome,uf:c.unidadeOrgao?.ufSigla,modalidade:c.modalidadeNome,valor:c.valorTotalEstimado,abertura:c.dataAberturaProposta,encerramento:c.dataEncerramentoProposta,situacao:c.situacaoCompraNome,amparo:c.amparoLegal?.nome,info:(c.informacaoComplementar||'').slice(0,400),link_origem:c.linkSistemaOrigem,erro:c.erro},
    arquivos:(a||[]).map(x=>x.titulo+' | '+x.url).slice(0,12), edital_inicio:tx.slice(0,1500), janelas:janelas(tx)}; };
```
3. Para cada item: `await pncp('CNPJ',ANO,SEQ)` (um item por chamada do javascript_tool; o retorno já é enxuto). Se vier 429, `await sleep(20000)` e tente uma vez.
A fonte oficial vale como "PNCP — documento do próprio órgão" (o PDF do edital publicado pelo órgão). O link do edital no PNCP: https://pncp.gov.br/app/editais/<cnpj>/<ano>/<seq>.

## B) Querido Diário (link data.queridodiario.ok.org.br/....pdf)
1. Navegue a aba para https://data.queridodiario.ok.org.br/robots.txt (mesma origem dos diários).
2. Leia o texto do diário trocando .pdf por .txt via fetch relativo e recorte em volta do assunto:
```js
window.qd=async (url,termos)=>{ const p=new URL(url).pathname.replace(/\.pdf$/,'.txt'); const t=(await fetch(p).then(r=>r.text())).replace(/\s+/g,' '); const rx=new RegExp(termos,'gi'); const o=[];let m,ult=-1e9; while((m=rx.exec(t))&&o.length<8){ if(m.index-ult<1500)continue; ult=m.index; o.push(t.slice(Math.max(0,m.index-300),m.index+1500)); } return {tamanho:t.length, trechos:o}; };
```
   ex.: `await qd(URL, 'chamamento|credenciamento|edital n')` (ajuste os termos ao título do item).
   O diário oficial do ente é fonte oficial ("Diário Oficial de <município> via Querido Diário").

## C) Busca na web (para achar o site oficial e o histórico 2023–2025)
Navegue a aba para `https://www.google.com/search?q=<termos codificados>&hl=pt-BR` e leia os resultados com:
```js
[...document.querySelectorAll('a h3')].slice(0,8).map(h=>h.innerText+' | '+h.closest('a').href)
```
No máximo 2 buscas por oportunidade. Se aparecer captcha/"tráfego incomum", PARE de buscar no Google (não tente resolver) e siga sem busca.
Depois abra o resultado oficial com WebFetch (HTML) ou, se for PDF do PNCP/diário, pelos métodos A/B. Páginas de prefeituras brasileiras que recusam WebFetch podem ser lidas navegando a aba até a página HTML (nunca a um arquivo) e usando `document.body.innerText.slice(0,6000)` no javascript_tool.

## Ritmo
Itens em sequência, um por vez. Seja enxuto: o objetivo é fechar os 12 itens (ou a dispensa fundamentada), a decisão, a iniciativa e o histórico de 3 anos.
