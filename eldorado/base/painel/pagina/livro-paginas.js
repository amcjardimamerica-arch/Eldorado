/* O LIVRO DA OPORTUNIDADE (titular, 02/11/2026): a capa e as 4 páginas aprovadas no canvas, montadas com a história
   completa do livro (dados/cartorio/<id>.json → historia). As páginas viram as texturas do livro 3D da titular (a capa e, ao virar,
   1 | 2 e 3 | 4). Sem botões que levem a outras páginas: o livro traz a informação completa. */
(function () {
  "use strict";
  const E = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const DOZE = ["Objeto", "Prazo de inscrição", "Resultado", "Prazo de recurso", "Valor", "Órgão / financiador", "Território", "Esfera", "Requisitos", "Anexos", "Modalidade", "Área de atuação"];
  const CURTO = { "Prazo de inscrição": "Prazo", "Prazo de recurso": "Recurso", "Órgão / financiador": "Órgão", "Área de atuação": "Área" };
  const MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"];
  const FASES = [["recepcao", "Recepção"], ["certificacao", "Certificação"], ["preparacao", "Preparação"], ["validacao", "Validação"], ["analise externa", "Análise ext."], ["farol", "Farol"], ["arquivo", "Arquivo"]];
  const DEGRAUS = [["1", "API oficial"], ["2", "pedido leve"], ["P", "ponte BR"], ["3", "nav. leve"], ["4", "Patchright"], ["5", "Camoufox"], ["6", "arquivo"], ["7", "local"]];
  const META_H = 72;   // a meta de horas por etapa (o traço da esteira); a definir pela titular
  let LOGO = "logo-amc.png";   // vira imagem de dados antes do desenho (o html2canvas não espera a imagem externa)
  const logoDados = async () => { if (LOGO.startsWith("data:")) return; try { const b = await (await fetch("logo-amc.png")).blob();
    LOGO = await new Promise(r => { const fr = new FileReader(); fr.onload = () => r(fr.result); fr.onerror = () => r("logo-amc.png"); fr.readAsDataURL(b); }); } catch (e) {} };

  const d = v => v ? new Date(String(v).length <= 10 ? v + "T12:00:00" : v) : null;
  const dm = v => { const x = d(v); return x ? String(x.getDate()).padStart(2, "0") + "/" + String(x.getMonth() + 1).padStart(2, "0") : ""; };
  const dmy = v => { const x = d(v); return x ? dm(v) + "/" + x.getFullYear() : ""; };
  const hm = v => { const x = d(v); return x ? String(x.getHours()).padStart(2, "0") + ":" + String(x.getMinutes()).padStart(2, "0") : ""; };
  const dia = v => { const x = d(v); return x ? x.getDate() + " de " + MESES[x.getMonth()] + " de " + x.getFullYear() : ""; };
  const reais = v => { v = Number(v || 0); if (!v) return ""; const f = (n, s) => (Number.isInteger(n) ? n : n.toFixed(1).replace(".", ",")) + s;
    return v >= 1e9 ? "R$ " + f(+(v / 1e9).toFixed(1), " bi") : v >= 1e6 ? "R$ " + f(+(v / 1e6).toFixed(1), " milhões") : v >= 1e3 ? "R$ " + f(Math.round(v / 1e3), " mil") : "R$ " + v; };
  const horas = h => h == null ? "—" : h < 1 ? "&lt;1 h" : Math.round(h) + " h";
  const curto = u => String(u || "").replace(/^https?:\/\//, "").replace(/^www\./, "");
  const abr = a => ({ nacional: "Nacional", estadual_go: "Estadual (GO)", municipal_go: "Municipal (GO)", estadual_outro_estado: "Estadual (outro estado)",
    capital_outro_estado: "Capital de outro estado", municipal_fora_go: "Municipal (fora de GO)", internacional: "Internacional", indeterminado: "Indeterminada" }[a] || a || "—");

  // ---- os 12 itens: a melhor certidão de cada um (comprovado > dispensado > contestado)
  function itens(certs) {
    const peso = { comprovado: 3, dispensado: 2, contestado: 1 }, m = {};
    (certs || []).forEach(c => { const a = m[c.item]; if (!a || (peso[c.situacao] || 0) > (peso[a.situacao] || 0)) m[c.item] = c; });
    return m;
  }
  const est = c => !c ? ["nr", "○", "não encontrado"] : c.situacao === "comprovado" ? ["ok", "✓", c.valor] : c.situacao === "dispensado" ? ["di", "⊘", "dispensado"] : ["ab", "!", "em aberto"];

  // o título da capa cabe sempre acima do valor e da data (o tamanho cai com o comprimento; acima de 120 letras, corta)
  const cortaTit = t => { t = String(t || "").trim(); return t.length > 120 ? t.slice(0, 117).replace(/\s+\S*$/, "") + "…" : t; };
  const tamTit = t => { const n = cortaTit(t).length; return n <= 45 ? 46 : n <= 70 ? 40 : n <= 95 ? 34 : 30; };
  // ---- a capa (modelo E): as faixas na cor da estrela; sem estrela, só o ornamento
  function capa(H) {
    const L = H.livro || {}, D = H.dados || {}, s = L.estrela;
    const metal = ["ouro", "prata", "bronze"].includes(s) ? s : null;
    const valor = reais(D.valor_max || D.valor_min) || "—", fim = dmy(D.inscricao_fim) || "—";
    return `<div class="lp2-capa"><div class="lp2-moldura${metal ? "" : " so"}">
      <div class="lp2-placa"><img src="${LOGO}" alt="A.M.C. Jardim América"></div>
      <h1 class="lp2-tit" style="font-size:${tamTit(L.titulo)}px">${E(cortaTit(L.titulo))}</h1>
      ${metal ? `<div class="lp2-faixas"><div class="lp2-faixa ${metal}"><div class="lab">Valor</div><div class="num">${E(valor)}</div></div>
        <div class="lp2-faixa ${metal}"><div class="lab">Inscrição até</div><div class="num">${E(fim)}</div></div></div>`
        : `<div class="lp2-orn"><i></i><b></b><i></i></div>`}
    </div></div>`;
  }

  // ---- página 1 (e a 4, com a paleta laranja): faixa, ficha 3×3 e mosaico 3×4
  function ficha(H, opc) {
    const L = H.livro || {}, D = H.dados || {}, it = itens(H.certidoes), docs = H.documentos || [];
    const motores = (H.motores || []).slice().sort((a, b) => (a === H.motor_que_gerou ? -1 : b === H.motor_que_gerou ? 1 : 0));
    const edital = D.link_oficial_tipo === "fonte" || docs.some(x => x.oficial) ? "encontrado" : "não encontrado";
    const drive = docs.some(x => x.drive_id) ? "no Drive" : "não enviado";
    const v = k => (it[k] && it[k].situacao === "comprovado") ? it[k].valor : "";
    const uf = D.uf || L.uf, estado = uf === "BR" ? "Nacional (BR)" : (uf || "—");
    const resol = DOZE.filter(k => it[k] && it[k].situacao !== "contestado").length;
    const tiles = DOZE.map(k => { const [c, i, t] = est(it[k]); return `<div class="t t${c}"><span class="cap ${c}">${i} ${E(CURTO[k] || k)}</span><span class="tv">${E(String(t || "").slice(0, 70))}</span></div>`; }).join("");
    const cel = (cap, val, x) => `<div class="cel"><div class="cap">${cap}</div><div class="v ${x || ""}">${E(val || "—")}</div></div>`;
    return `<div class="lp2-pg${opc && opc.passada ? " passada" : ""}">
      <div class="lp2-band"><div class="lin"><span class="cap ac">${opc && opc.passada ? "4 · Oportunidade anterior" : "1 · Dados do livro"}</span><span class="cap cl">${E(L.id)}</span></div>
        <h2>${E(cortaTit(L.titulo) || "—")}</h2>
        <div class="chips"><span class="chip cheio">Estrela ${E(L.estrela || "sem")}</span><span class="chip">Livro ${L.selo_livro && L.selo_livro !== "sem" ? E(L.selo_livro) : "sem selo"}</span></div></div>
      <div class="lp2-corpo">
        <div class="grade">${cel("Área", D.area || L.tema)}${cel("Estado", estado)}${cel("Limite", dmy(D.inscricao_fim), "fort")}
          ${cel("Órgão", L.orgao || v("Órgão / financiador"))}${cel("Esfera", D.esfera || v("Esfera"))}${cel("Abrangência", abr(D.abrangencia))}
          ${cel("Motores", motores.length ? motores.length + (H.motor_que_gerou ? " · " + H.motor_que_gerou.replace(/^site-/, "") + " gerou" : "") : "—")}${cel("Edital", edital)}${cel("Drive", drive, drive === "no Drive" ? "" : "ab")}</div>
        <div class="v cz">${motores.length ? "Motores: " + E(motores.join(", ")) : "Motores: —"}</div>
        <div class="v"><span class="cap">Divulgação </span>${E(curto(L.link_divulgacao).slice(0, 90) || "—")}</div>
        <div class="v"><span class="cap">Oficial </span>${E(curto(L.link_oficial) || "—")}</div>
        <div class="lin"><span class="cap fort">Checklist dos 12 itens</span><span class="cap fort">${resol} de 12</span></div>
        <div class="mosaico">${tiles}</div>
        ${opc && opc.parecer ? `<div class="quadro"><div class="cap">Parecer sobre a oportunidade anterior</div><div class="v">${opc.parecer}</div></div>` : ""}
      </div></div>`;
  }

  // ---- página 2: placar, escada, esteira e tentativas
  function tempos(H) {
    const ps = (H.passagens || []).slice().sort((a, b) => String(a.em).localeCompare(String(b.em))), t = {};
    ps.forEach((p, i) => { const fim = i + 1 < ps.length ? d(ps[i + 1].em) : new Date(); t[p.para] = (t[p.para] || 0) + Math.max(0, (fim - d(p.em)) / 36e5); });
    return t;
  }
  function tentativas(H) {
    const out = (H.tentativas || []).map(x => { let r = {}; try { r = JSON.parse(x.resultado || "{}"); } catch (e) { r = {}; }
      const motor = /^motor/.test(x.ferramenta || ""), nome = motor ? String(x.ferramenta).replace(/^motor\s*/, "") : (r.abordagem ? String(x.ferramenta || "").replace(/^abordagem\s*/, "") + " · " + r.abordagem : x.ferramenta);
      const res = r["sem material"] ? "sem material" : (r.trouxe ? "trouxe" : (r.material || r.enderecos) ? "com material" : "sem material");
      return { em: x.em, quem: motor ? "Motor" : "Interceptador", cls: "vi", txt: nome + " · " + res }; });
    (H.vereditos || []).filter(v => /chrome|externa/.test(v.origem || "")).forEach(v => out.push({ em: v.em, quem: "Claude Chrome", cls: "tl", txt: v.decisao + " · " + String(v.motivo || "").slice(0, 70) }));
    return out.sort((a, b) => String(a.em).localeCompare(String(b.em)));
  }
  function etapas(H, f) {
    const P = H.passaporte || {}, t = tempos(H), it = itens(H.certidoes), D = H.dados || {};
    const chrome = (H.vereditos || []).filter(v => /chrome|externa/.test(v.origem || "")).length, nt = (H.tentativas || []).length;
    const resol = DOZE.filter(k => it[k] && it[k].situacao !== "contestado").length;
    const fase = (FASES.find(x => x[0] === P.fase) || [P.fase, P.fase || "—"])[1];
    const agora = P.entrou_em ? (new Date() - d(P.entrou_em)) / 36e5 : null;
    // a escada: o que cada degrau conseguiu (o degrau do livro e o de cada achado)
    const cod = s => { const m = String(s || "").match(/degrau\s+([0-9P])/i) || String(s || "").match(/^\s*([0-9P])\s*·/); return m ? m[1].toUpperCase() : null; };
    const obt = {};
    (H.achados || []).forEach(a => { const c = a.escada && cod(a.escada.degrau); if (c) (obt[c] = obt[c] || []).push(dm(a.encontrado_em) + " · " + (a.escada.motor || a.motor) + (a.escada.fonte ? " · " + a.escada.fonte : "") + " → " + (a.decisao === "aceito" ? "achado aceito" : a.decisao || "achado")); });
    const cl = cod(D.escada); if (cl) (obt[cl] = obt[cl] || []).push("último acesso do livro · " + String(D.escada).split("·")[0].trim());
    const maior = Math.max(-1, ...Object.keys(obt).map(k => DEGRAUS.findIndex(x => x[0] === k)));
    const esc = DEGRAUS.map(([c, n], i) => { const ok = obt[c]; return `<div class="deg ${ok ? "ok" : "nao"}" style="margin-left:${i * 13}px"><span class="v ${ok ? "tl fort" : "cz"}">${c} · ${n}</span><span class="v ${ok ? "" : "cz"}">${ok ? E(ok.join(" · ").slice(0, 150)) : i > maior ? "não precisou" : "sem registro neste livro"}</span></div>`; }).join("");
    const linhas = FASES.filter(([k]) => k !== "arquivo" || t[k] != null).map(([k, n]) => { const h = t[k], atual = k === P.fase, w = h == null ? 0 : Math.max(1, Math.min(100, h / 120 * 100));
      const cor = atual ? "#E8952B" : h != null && h > META_H ? "#7B6CE0" : "#14A88C";
      return `<div class="esteira"><span class="v ${atual ? "am fort" : ""}">${n}${atual ? " ● agora" : h != null ? " ✓" : ""}</span><div class="trilho"><div style="width:${w}%;background:${cor}"></div><i class="meta"></i></div><span class="m ${atual ? "am" : h != null && h > META_H ? "vi" : "tl"}">${h == null ? "—" : horas(h)}</span></div>`; }).join("");
    const tl = tentativas(H).slice(-8).map(x => `<div class="v">${dm(x.em)} ${hm(x.em)}</div><div class="v ${x.cls} fort">${E(x.quem)}</div><div class="v">${E(x.txt)}</div>`).join("");
    return `<div class="lp2-pg branco"><div class="lp2-corpo">
      <div class="lin"><span class="cap">2 · Etapas cumpridas na coleta</span><span class="cap am">${E(fase)}${agora != null ? " · " + horas(agora) : ""}</span></div>
      <div class="placar"><div class="card"><div class="cap">Etapa atual</div><div class="m am g">${E(fase)}</div></div><div class="card"><div class="cap">Nesta etapa</div><div class="m g">${horas(agora)}</div></div>
        <div class="card"><div class="cap">Itens</div><div class="m g">${resol}/12</div></div><div class="card"><div class="cap">Tentativas</div><div class="m g">${nt} + ${chrome}</div></div></div>
      <div class="cap">Escada de acesso · o que cada degrau conseguiu</div><div class="escada">${esc}</div>
      <div class="cap">Esteira · horas gastas e meta (traço = ${META_H} h)</div><div class="esteiras">${linhas}</div>
      <div class="card tent"><div class="cap">Relatório de tentativas · Interceptador ${nt} · Chrome ${chrome}</div><div class="tab3">${tl || '<div class="v cz">nenhuma tentativa registrada</div>'}</div></div>
    </div></div>`;
  }

  // ---- página 3: o diário (datas centralizadas, hora de cada registro) e as duas peças
  const FIM_CHROME = dec => /descart/.test(dec) ? "Eliminou a oportunidade." : /encerrad|arquiv/.test(dec) ? "Arquivou a oportunidade." : /pendente/.test(dec) ? "Análise pendente." : "Inseriu os dados na oportunidade.";
  function diario(H) {
    const ent = [];
    const autorFase = { recepcao: ["Cartório", "car", "CA"], certificacao: ["Cartório", "car", "CA"], validacao: ["Cartório", "car", "CA"], preparacao: ["Rede neural", "cer", "RN"], farol: ["Farol", "cer", "FA"], arquivo: ["Cartório", "car", "CA"] };
    (H.relatorios || []).forEach(r => { const a = autorFase[r.fase]; if (!a) return; ent.push({ em: r.em, a, txt: (r.gerou || "") + (r.faltou ? " · faltou: " + r.faltou : "") }); });
    tentativas(H).filter(x => x.quem !== "Claude Chrome").forEach(x => ent.push({ em: x.em, a: x.quem === "Motor" ? ["Motor de origem", "mot", "MO"] : ["Interceptador", "int", "IN"], txt: x.txt }));
    (H.vereditos || []).forEach(v => { const ch = /chrome|externa/.test(v.origem || ""); ent.push({ em: v.em, a: ch ? ["Claude no Chrome", "chrome", "CC"] : ["Titular", "cmd", "TI"], txt: (v.decisao || "") + ": " + (v.motivo || ""), fim: ch ? FIM_CHROME(v.decisao || "") : null }); });
    (H.unioes || []).forEach(u => ent.push({ em: u.em, a: ["Comandante", "cmd", "CO"], txt: "Uniu " + u.livro_unido + ": " + (u.motivo || "") }));
    ent.sort((x, y) => String(x.em).localeCompare(String(y.em)));
    const ult = ent.slice(-9), antes = ent.length - ult.length;
    let html = antes > 0 ? `<div class="v cz centro">${antes} registro(s) anterior(es) no histórico</div>` : "", diaAtual = "";
    ult.forEach(x => { const dd = dia(x.em); if (dd !== diaAtual) { diaAtual = dd; html += `<div class="dia">${E(dd)}</div>`; }
      html += `<div class="ent${x.a[1] === "chrome" ? " ch" : ""}"><div class="av ${x.a[1]}">${x.a[2]}</div><div><div class="cap${x.a[1] === "chrome" ? " tl" : ""}">${E(x.a[0])} · ${hm(x.em)}</div><div class="v">${E(String(x.txt).slice(0, 220))}</div>${x.fim ? `<div class="v fort tl">${E(x.fim)}</div>` : ""}</div></div>`; });
    const leis = H.leis || [], prev = (H.previsoes || []).filter(p => p.proxima_abertura_prevista).slice(-1)[0];
    return `<div class="lp2-pg"><div class="lp2-corpo">
      <div class="cap">3 · Decisões sobre o livro</div>
      <div class="janela"><div class="barra"><span class="cap ac">Diário · quem escreveu</span><span class="cap cl">${ent.length} registros</span></div><div class="reg">${html || '<div class="v cz centro">sem registros</div>'}</div></div>
      <div class="pecas"><div class="peca"><span class="ic">§</span><div><div class="cap ac">Legislação aplicável</div><div class="v claro fort">${leis.length ? E(leis.map(l => l.lei_id + (l.papel ? " (" + l.papel + ")" : "")).join("; ").slice(0, 90)) : "Nenhuma lei ligada"}</div></div></div>
        <div class="peca"><span class="ic">↻</span><div><div class="cap ac">Próxima previsão</div><div class="v claro fort">${prev ? E(dmy(prev.proxima_abertura_prevista) + (prev.confianca != null ? " · confiança " + Math.round(prev.confianca * 100) + "%" : "")) : "Sem previsão"}</div></div></div></div>
    </div></div>`;
  }

  // ---- página 4: a oportunidade anterior (mesmo padrão da 1, em laranja) com o parecer
  function anterior(H) {
    const A = (H.anteriores || [])[0];
    if (!A) return ficha({ livro: { id: "", titulo: "Sem oportunidade anterior registrada" }, dados: {}, certidoes: [], documentos: [], motores: [] },
      { passada: true, parecer: "Este livro não tem oportunidade anterior registrada. Quando uma edição for arquivada, os dados dela aparecem aqui e a análise preditiva passa a prever a próxima abertura." });
    const u = A.uniao || {}, it = itens(A.certidoes), n = DOZE.filter(k => it[k] && it[k].situacao !== "contestado").length;
    const par = `Registro anterior «${E(A.livro.titulo)}», criado em ${E(dmy(A.livro.criado_em))}, com estrela ${E(A.livro.estrela || "sem")} e ${n} de 12 itens resolvidos. ` +
      (u.em ? `Unido a este livro em ${E(dmy(u.em))}: ${E(String(u.motivo || "").slice(0, 160))}.` : "");
    return ficha({ livro: A.livro, dados: A.dados || {}, certidoes: A.certidoes, documentos: [], motores: [] }, { passada: true, parecer: par });
  }

  // ---- o livro 3D: as páginas desenhadas aqui viram as texturas do livro 3D (a capa e as 4 páginas)
  // o desenho acontece num quadro isolado e leve (só o estilo do livro, as fontes e o html2canvas): o html2canvas copia o
  // documento inteiro a cada desenho, e o painel tem mais de 850 KB de página
  let quadro = null;
  const FONTES = "https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Nunito+Sans:opsz,wght@6..12,400;6..12,600;6..12,800&family=Saira+Semi+Condensed:wght@400;600;700&display=swap";
  function moldura() {
    if (quadro) return quadro;
    quadro = new Promise((ok, erro) => { const f = document.createElement("iframe"); f.setAttribute("aria-hidden", "true"); f.tabIndex = -1;
      f.style.cssText = "position:fixed;left:-20000px;top:0;width:1500px;height:1000px;border:0;visibility:hidden";
      f.srcdoc = '<!doctype html><html><head><meta charset="utf-8"><base href="' + E(location.href) + '"><link rel="stylesheet" href="livro-paginas.css"><link rel="stylesheet" href="' + FONTES + '">' +
        '<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"><\/script></head><body style="margin:0"></body></html>';
      f.onload = async () => { if (!f.contentWindow.html2canvas) { quadro = null; f.remove(); return erro(new Error("html2canvas")); } try { await f.contentDocument.fonts.ready; } catch (e) {} ok(f); };
      document.body.appendChild(f); });
    return quadro;
  }
  async function desenhar(html) {
    const f = await moldura(), d = f.contentDocument, caixa = d.createElement("div");
    caixa.className = "lp2-tex"; caixa.style.cssText = "position:absolute;left:0;top:0"; caixa.innerHTML = html; d.body.appendChild(caixa);
    try { await Promise.all([...caixa.querySelectorAll("img")].map(im => im.complete ? 0 : new Promise(r => { im.onload = im.onerror = r; })));
      try { await d.fonts.ready; } catch (e) {}
      return await f.contentWindow.html2canvas(caixa.firstElementChild, { scale: 2.3, backgroundColor: null, logging: false }); }
    finally { caixa.remove(); }
  }
  async function ficheiro(o) {
    const ids = [o && o.id, o && o.livro_vinculado && (o.livro_vinculado.id || o.livro_vinculado), o && o.livro_id].filter(x => typeof x === "string" && x);
    for (const id of ids) { try { const r = await fetch("dados/cartorio/" + encodeURIComponent(id.replace(/[^A-Za-z0-9_.-]/g, "_")) + ".json?v=" + Date.now()); if (r.ok) { const f = await r.json(); if (f && f.historia) return f; } } catch (e) {} }
    return o && o.historia ? o : null;
  }
  const texto = el => (el.textContent || "").replace(/\s+/g, " ").trim().slice(0, 900);
  async function conteudo3D(o) {
    const f = await ficheiro(o); if (!f) return null;
    const H = f.historia, L = H.livro || {}, D = H.dados || {};
    await logoDados();
    const htmls = [capa(H), ficha(H), etapas(H, f), diario(H), anterior(H)], img = [];
    for (const h of htmls) img.push(await desenhar(h));
    const ler = h => { const d = document.createElement("div"); d.innerHTML = h; return texto(d); };
    return { titulo: L.titulo, capaImagem: img[0],
      capa: { numero: L.id || "", titulo: L.titulo || "", periodo: D.inscricao_fim ? "Inscrições até " + dmy(D.inscricao_fim) : "", prazo: "", resumo: "", selo: "A.M.C. Jardim América", data: new Date().toISOString() },
      paginas: img.slice(1).map((c, i) => ({ imagem: c, texto: ler(htmls[i + 1]) })) };
  }
  window.LivroPaginas = { conteudo3D, _paginas: H => [capa(H), ficha(H), etapas(H, {}), diario(H), anterior(H)] };
})();
