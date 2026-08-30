"""Relatório da varredura — emitido às segundas e quartas, após a busca.

Três partes, num único HTML datado em `docs/relatorios/<data>.html`:

**Parte 1 — Editais abertos no período.** Uma caixa por edital, individualizada.
Se o mesmo programa publicou vários editais (a PNAB/Aldir Blanc é o caso
clássico), cada um aparece na sua própria caixa, com nome da lei, modalidade
(objeto ou atividade a executar) e a contagem de prazo de início e fim.

**Parte 2 — Calendário anual.** Doze meses, mostrando o período de cada edital
e programa, incluindo os de abertura mensal ou fluxo contínuo e a janela de
articulação de emendas parlamentares em outubro e novembro.

**Parte 3 — Emendas parlamentares.** Área que **só abre em outubro e novembro**.
Lista parlamentares com mandato no ano, gabinete, resultado eleitoral e as
bandeiras medidas por atuação registrada. Emenda **não aciona o Farol**: a área
informa e direciona, sem gerar plano de trabalho.

Sem IA e sem tokens.
"""
from __future__ import annotations

import html
import json
from collections import defaultdict
from datetime import date, datetime

from . import parlamentares as mod_parlamentares
from .programas import caracterizar
from .nucleo import ROOT, carregar_oportunidades, load_json, now_iso, write_json

PASTA = ROOT / "docs/relatorios"
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
         "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]

def _e(v) -> str:
    return html.escape(str(v if v not in (None, "", []) else "—"), quote=True)

def _dia(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        return datetime.strptime(iso[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return iso

def _situacao(inicio: str | None, fim: str | None, hoje: date) -> dict:
    """Situação da janela de inscrição, sem inferir data que a fonte não deu."""
    d_ini = d_fim = None
    for bruto, destino in ((inicio, "ini"), (fim, "fim")):
        if bruto:
            try:
                valor = datetime.strptime(str(bruto)[:10], "%Y-%m-%d").date()
            except ValueError:
                valor = None
            if destino == "ini":
                d_ini = valor
            else:
                d_fim = valor
    if d_fim and d_fim < hoje:
        return {"estado": "encerrado", "classe": "bad", "rotulo": f"Encerrado em {_dia(fim)}",
                "dias_para_fim": (d_fim - hoje).days, "dias_para_inicio": None}
    if d_ini and d_ini > hoje:
        faltam = (d_ini - hoje).days
        return {"estado": "a_abrir", "classe": "warn", "rotulo": f"Abre em {faltam} dia(s)",
                "dias_para_inicio": faltam, "dias_para_fim": (d_fim - hoje).days if d_fim else None}
    if d_fim:
        faltam = (d_fim - hoje).days
        classe = "bad" if faltam <= 7 else "warn" if faltam <= 30 else "ok"
        return {"estado": "aberto", "classe": classe, "rotulo": f"Aberto — faltam {faltam} dia(s)",
                "dias_para_fim": faltam, "dias_para_inicio": None}
    return {"estado": "sem_prazo", "classe": "meta",
            "rotulo": "Sem data de encerramento na fonte — conferir no edital",
            "dias_para_fim": None, "dias_para_inicio": None}

def coletar(hoje: date | None = None, desde_dias: int = 7) -> dict:
    hoje = hoje or date.today()
    registros = list(carregar_oportunidades().values())
    cfg_prog = load_json(ROOT / "config/programas.json")
    editais = []
    for item in registros:
        if item.get("status") in {"quarentena_prompt_injection", "descartada"}:
            continue
        carac = item.get("caracterizacao") or caracterizar(item, cfg_prog)
        periodo = carac.get("periodo") or {}
        situacao = _situacao(periodo.get("inicio"), periodo.get("fim"), hoje)
        editais.append({
            "id": item["id"], "titulo": item.get("titulo"), "url": item.get("url"),
            "fonte_nome": item.get("fonte_nome"), "territorio": item.get("territorio"),
            "nivel": item.get("nivel"), "status": item.get("status"),
            "confianca": item.get("confianca"),
            "programa": carac.get("programa"), "programa_id": carac.get("programa_id"),
            "lei": carac.get("lei"), "modalidade": carac.get("modalidade"),
            "origem_modalidade": carac.get("origem"), "fluxo": carac.get("fluxo", "edital"),
            "alerta_programa": carac.get("alerta"), "aciona_farol": carac.get("aciona_farol", True),
            "inicio": periodo.get("inicio"), "fim": periodo.get("fim"),
            "inicio_declarado": periodo.get("inicio_declarado"), "fim_declarado": periodo.get("fim_declarado"),
            "situacao": situacao,
            "nota_conformidade": (item.get("qualidade") or {}).get("nota"),
            "ficha": f"../editais/{item['id']}.html",
            "coletado_em": item.get("coletado_em"),
        })
    abertos = [e for e in editais if e["situacao"]["estado"] in {"aberto", "a_abrir", "sem_prazo"}]
    abertos.sort(key=lambda e: (e["situacao"]["dias_para_fim"] is None,
                                e["situacao"]["dias_para_fim"] if e["situacao"]["dias_para_fim"] is not None else 9999))
    return {"gerado_em": now_iso(), "referencia": hoje.isoformat(),
            "total_base": len(editais), "abertos": abertos,
            "encerrados_no_periodo": [e for e in editais if e["situacao"]["estado"] == "encerrado"],
            "janela_busca_dias": desde_dias}

def _calendario(abertos: list[dict], cfg_prog: dict, ano: int) -> list[dict]:
    """Doze meses com o que ocupa cada um: editais datados, fluxo contínuo e emendas."""
    por_mes = defaultdict(list)
    for edital in abertos:
        for campo, marca in (("inicio", "abertura"), ("fim", "encerramento")):
            bruto = edital.get(campo)
            if not bruto:
                continue
            try:
                data = datetime.strptime(str(bruto)[:10], "%Y-%m-%d").date()
            except ValueError:
                continue
            if data.year != ano:
                continue
            por_mes[data.month].append({
                "tipo": marca, "titulo": edital["titulo"][:90], "programa": edital["programa"],
                "dia": data.day, "id": edital["id"],
            })
    janelas = cfg_prog["janelas_recorrentes"]
    continuos = [p for p in cfg_prog["programas"]
                 if p["id"] in janelas["fluxo_continuo_mensal"]["programas"]]
    meses_emenda = set(janelas["emendas_parlamentares"]["meses"])

    calendario = []
    for numero in range(1, 13):
        itens = sorted(por_mes.get(numero, []), key=lambda x: x["dia"])
        calendario.append({
            "mes": numero, "nome": MESES[numero - 1], "itens": itens,
            "fluxo_continuo": [{"programa": p["nome"], "lei": p["lei"]} for p in continuos],
            "emendas": numero in meses_emenda,
            "rotulo_emendas": janelas["emendas_parlamentares"]["rotulo"] if numero in meses_emenda else None,
        })
    return calendario

# ------------------------------ render ------------------------------

ESTILO = """<style>
:root{--gold:#f5c451;--navy:#081426;--ink:#eaf1f8;--muted:#9eb0c5;--ok:#47d7ac;--bad:#ff7373;--warn:#ffb547;--line:#244766}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 10% 0,#173a5f,var(--navy) 42%);color:var(--ink);font:15px/1.55 system-ui,sans-serif}
main{max-width:1120px;margin:auto;padding:24px}
h1{color:var(--gold);font-size:clamp(23px,4vw,36px);margin:.2em 0}
h2{margin-top:36px;font-size:21px;border-bottom:1px solid var(--line);padding-bottom:7px}
h3{font-size:16px;margin:0 0 6px}
.meta{color:var(--muted);font-size:13px}a{color:#8ed5ff;word-break:break-word}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
.card{background:#0d223b;border:1px solid var(--line);border-radius:14px;padding:16px}
.metric{font-size:28px;color:var(--gold);font-weight:800}
.editais{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:14px;margin-top:14px}
.edital{background:#0d223b;border:1px solid var(--line);border-left:4px solid var(--gold);border-radius:12px;padding:15px;display:flex;flex-direction:column}
.edital.bad{border-left-color:var(--bad)}.edital.warn{border-left-color:var(--warn)}.edital.ok{border-left-color:var(--ok)}
.edital.meta{border-left-color:#3a607e}
.linha{display:flex;justify-content:space-between;gap:10px;font-size:13.5px;padding:4px 0;border-bottom:1px dashed #1d3a57}
.linha b{color:var(--muted);font-weight:600}
.contagem{margin-top:auto;padding-top:12px;font-size:14px}
.tag{display:inline-block;border:1px solid #3a607e;border-radius:20px;padding:2px 9px;margin:4px 4px 0 0;font-size:12px}
.ok{color:var(--ok)}.bad{color:var(--bad)}.warn{color:var(--warn)}
.cal{display:grid;grid-template-columns:repeat(auto-fit,minmax(165px,1fr));gap:10px}
.mes{background:#0d223b;border:1px solid var(--line);border-radius:12px;padding:12px;min-height:120px}
.mes.emenda{border-color:var(--gold);background:#12294a}
.mes h4{margin:0 0 8px;font-size:14px;color:var(--gold);text-transform:capitalize}
.ev{font-size:12px;padding:3px 0;border-bottom:1px dashed #1d3a57}
.fechado{border:1px dashed #3a607e;border-radius:14px;padding:20px;text-align:center;background:#0a1b2f}
table{width:100%;border-collapse:collapse;font-size:14px;margin-top:8px}
td,th{text-align:left;padding:7px 6px;border-bottom:1px solid #1d3a57;vertical-align:top}
th{color:var(--muted);font-weight:600}
.aviso{border-left:3px solid var(--warn);padding-left:12px}
footer{color:var(--muted);padding:32px 0;font-size:13px}
</style>"""

def _caixa_edital(e: dict) -> str:
    s = e["situacao"]
    if s["estado"] == "aberto" and s["dias_para_fim"] is not None:
        contagem = (f"<div class='contagem {s['classe']}'><strong>Faltam {s['dias_para_fim']} dia(s)</strong> "
                    f"<span class=meta>para encerrar ({_dia(e['fim'])})</span></div>")
    elif s["estado"] == "a_abrir":
        extra = f" · encerra em {_dia(e['fim'])}" if e["fim"] else ""
        contagem = (f"<div class='contagem warn'><strong>Abre em {s['dias_para_inicio']} dia(s)</strong> "
                    f"<span class=meta>({_dia(e['inicio'])}{extra})</span></div>")
    elif s["estado"] == "encerrado":
        contagem = f"<div class='contagem bad'><strong>Encerrado</strong> <span class=meta>em {_dia(e['fim'])}</span></div>"
    else:
        contagem = ("<div class='contagem meta'>Sem data de encerramento na fonte — "
                    "<strong>conferir no edital</strong></div>")

    alerta = f"<div class=meta style='color:var(--warn)'>⚠ {_e(e['alerta_programa'])}</div>" if e.get("alerta_programa") else ""
    fluxo = ("<span class=tag>fluxo contínuo</span>" if e.get("fluxo") == "invertido" else "")
    sem_farol = ("<span class='tag warn'>não aciona o Farol</span>" if not e.get("aciona_farol") else "")
    modalidade = e.get("modalidade") or "não localizada no texto capturado — conferir o edital"

    return f"""<article class="edital {s['classe']}">
<h3><a href="{_e(e['url'])}" target=_blank rel="noopener noreferrer">{_e(e['titulo'])}</a></h3>
<div class=meta>{_e(e['fonte_nome'])} · {_e(e['territorio'])}</div>
<div style="margin:9px 0 2px">
<span class=tag>{_e(e['programa'])}</span>{fluxo}{sem_farol}
{f"<span class=tag>conformidade {e['nota_conformidade']}/100</span>" if e.get("nota_conformidade") is not None else ""}
</div>{alerta}
<div class=linha><b>Lei de regência</b><span>{_e(e['lei'])}</span></div>
<div class=linha><b>Modalidade / objeto</b><span>{_e(modalidade)}</span></div>
<div class=linha><b>Início</b><span>{_dia(e['inicio'])}{'' if e.get('inicio_declarado') else ' <span class=meta>(publicação)</span>'}</span></div>
<div class=linha><b>Encerramento</b><span>{_dia(e['fim'])}</span></div>
<div class=linha><b>Situação no funil</b><span>{_e(e['status'])}</span></div>
{contagem}
<div style="margin-top:9px"><a class=meta href="{_e(e['ficha'])}">ficha completa do edital →</a></div>
</article>"""

def _render_parte3(dados_parl: dict, aberto: bool, cfg: dict, hoje: date) -> str:
    janela = cfg["janela_de_exibicao"]
    if not aberto:
        proximo = date(hoje.year if hoje.month < 10 else hoje.year + 1, 10, 1)
        return f"""<div class=fechado>
<h3 style="color:var(--gold)">Área de emendas parlamentares — fechada</h3>
<p class=meta>{_e(janela['rotulo'])}.<br>
Reabre em <strong>{_dia(proximo.isoformat())}</strong>.</p>
<p class=meta>{_e(cfg['motivo_nao_acionar'])}</p></div>"""

    lista = dados_parl.get("parlamentares") or []
    pendencias = dados_parl.get("pendencias") or []
    eleicao = dados_parl.get("resultado_eleicao") or {}

    if not lista:
        linhas = ("<tr><td colspan=5 class=meta>Nenhum parlamentar carregado. "
                  "A área não exibe nome, gabinete ou votação sem carga de fonte oficial.</td></tr>")
    else:
        def _linha(p: dict) -> str:
            gab = p.get("gabinete") or {}
            local = _e(gab.get("sala"))
            if gab.get("predio"):
                local += " · prédio " + _e(gab.get("predio"))
            bandeiras = "".join(
                "<span class=tag>" + _e(b.get("tema")) + " (" + _e(b.get("ocorrencias")) + ")</span>"
                for b in (p.get("bandeiras") or [])) or "<span class=meta>sem bandeira medida</span>"
            return (f"<tr><td><strong>{_e(p.get('nome'))}</strong>"
                    f"<div class=meta>{_e(p.get('partido'))} · {_e(p.get('uf'))} · {_e(p.get('esfera'))}</div></td>"
                    f"<td class=meta>{local}</td><td>{bandeiras}</td>"
                    f"<td class=meta>{_e(p.get('resultado_eleicao') or 'não carregado')}</td>"
                    f"<td class=meta>{_e(p.get('situacao'))}</td></tr>")
        linhas = "".join(_linha(p) for p in lista)

    bloco_pendencias = "".join(
        f"<li>{_e(x.get('casa') or x.get('esfera'))}: {_e(x.get('motivo'))}"
        + (f" — <a href='{_e(x['consulta_humana'])}' target=_blank rel='noopener noreferrer'>consulta oficial</a>"
           if x.get("consulta_humana") else "") + "</li>"
        for x in pendencias) or "<li class=meta>Sem pendências registradas.</li>"

    return f"""<div class="card aviso" style="margin-bottom:14px">
<strong>Esta área não aciona o Farol de Alexandria.</strong>
<p class=meta style="margin:6px 0 0">{_e(cfg['motivo_nao_acionar'])}
Nenhum caso é aberto e nenhum plano de trabalho é gerado aqui sem solicitação expressa.</p></div>

<div class=card><table>
<tr><th>Parlamentar</th><th>Gabinete</th><th>Bandeiras medidas por atuação</th><th>Resultado eleitoral</th><th>Situação</th></tr>
{linhas}</table>
<p class=meta>Bandeira é contagem de atuação registrada (proposições e comissões), não opinião atribuída ao parlamentar.
Tema com uma só ocorrência é ruído e não vira bandeira.</p></div>

<div class=card><strong>Pendências de carga</strong><ul>{bloco_pendencias}</ul>
<p class=meta>Resultado eleitoral: <strong>{_e(eleicao.get('status', 'não carregado'))}</strong>.
{_e(eleicao.get('motivo'))}
{f"<a href='{_e(eleicao.get('fonte_indicada'))}' target=_blank rel='noopener noreferrer'>fonte oficial</a>" if eleicao.get('fonte_indicada') else ''}</p></div>"""

def render(dados: dict, calendario: list[dict], dados_parl: dict, cfg_parl: dict,
           hoje: date, emendas_aberta: bool, forcado: bool) -> str:
    abertos = dados["abertos"]
    por_programa = defaultdict(list)
    for e in abertos:
        por_programa[e["programa"]].append(e)

    blocos = []
    for programa, itens in sorted(por_programa.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        titulo_grupo = (f"<h3 style='margin-top:22px;color:var(--gold)'>{_e(programa)} "
                        f"<span class=meta>— {len(itens)} edital(is) individualizado(s)</span></h3>"
                        if len(itens) > 1 else f"<h3 style='margin-top:22px;color:var(--gold)'>{_e(programa)}</h3>")
        blocos.append(titulo_grupo + "<div class=editais>" + "".join(_caixa_edital(e) for e in itens) + "</div>")
    corpo_editais = "".join(blocos) or "<div class=card>Nenhum edital aberto nesta varredura.</div>"

    cal_html = "".join(
        f"""<div class="mes{' emenda' if m['emendas'] else ''}"><h4>{m['nome']}</h4>
{''.join(f"<div class=ev><strong>{x['dia']:02d}</strong> {'abre' if x['tipo']=='abertura' else 'encerra'} · {_e(x['titulo'][:44])}</div>" for x in m['itens'])
 or '<div class="ev meta">sem data registrada</div>'}
{f"<div class=ev style='color:var(--gold);border:none;margin-top:6px'><strong>Emendas parlamentares</strong><div class=meta>articulação e indicação</div></div>" if m['emendas'] else ''}
</div>""" for m in calendario)

    continuos = calendario[0]["fluxo_continuo"]
    continuos_html = "".join(f"<li>{_e(c['programa'])} <span class=meta>— {_e(c['lei'])}</span></li>"
                             for c in continuos) or "<li class=meta>nenhum</li>"

    parte3 = _render_parte3(dados_parl, emendas_aberta, cfg_parl, hoje)
    aviso_forcado = ("<p class=meta style='color:var(--warn)'>⚠ Área aberta fora da janela de outubro e novembro, "
                     "a pedido — os dados valem para consulta, não para articulação em curso.</p>" if forcado else "")

    encerrados = dados.get("encerrados_no_periodo") or []

    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Relatório da varredura · {_dia(dados['referencia'])} · Eldorado</title>{ESTILO}</head><body><main>
<div class=meta><a href="../index.html">← painel</a> · <a href="../relatorio-amplitude.html">relatório de amplitude</a></div>
<h1>Relatório da varredura — {_dia(dados['referencia'])}</h1>
<p class=meta>Emitido após a busca de segunda e quarta-feira. Gerado em {_e(dados['gerado_em'])}.
Dados automatizados exigem conferência na fonte primária antes de qualquer decisão.</p>

<section class=cards>
<div class=card><div class=metric>{len(abertos)}</div><div class=meta>editais em aberto</div></div>
<div class=card><div class=metric>{len(por_programa)}</div><div class=meta>programas distintos</div></div>
<div class=card><div class=metric>{sum(1 for e in abertos if (e['situacao']['dias_para_fim'] or 999) <= 7)}</div><div class=meta>encerram em até 7 dias</div></div>
<div class=card><div class=metric>{len(encerrados)}</div><div class=meta>encerrados</div></div>
<div class=card><div class=metric>{dados['total_base']}</div><div class=meta>registros na base</div></div>
</section>

<h2>1. Editais abertos no período</h2>
<p class=meta>Cada edital tem sua própria caixa. Quando o mesmo programa publica vários editais — como acontece
na PNAB/Aldir Blanc — cada um aparece individualizado, com sua lei, sua modalidade e sua própria contagem de prazo.</p>
{corpo_editais}

<h2>2. Calendário do ano</h2>
<p class=meta>Período de cada edital e programa ao longo de {calendario and datetime.now().year}.
Meses destacados em dourado concentram a articulação de emendas parlamentares.</p>
<div class=cal>{cal_html}</div>
<div class=card style="margin-top:14px"><strong>Programas de fluxo contínuo ou janela mensal</strong>
<ul>{continuos_html}</ul>
<p class=meta>Nesses programas não há data única de encerramento: a habilitação do projeto é analisada por lote,
e a captação depende de empresa incentivadora.</p></div>

<h2>3. Emendas parlamentares</h2>
{aviso_forcado}
{parte3}

<footer>Eldorado · Farol de Alexandria — relatório gerado sem consumo de tokens.
Prazo, valor, requisitos e vigência exigem conferência na fonte primária.</footer>
</main></body></html>"""

def run(hoje: date | None = None, forcar_emendas: bool = False) -> dict:
    hoje = hoje or date.today()
    cfg_prog = load_json(ROOT / "config/programas.json")
    cfg_parl = load_json(ROOT / "config/parlamentares.json")
    dados = coletar(hoje)
    calendario = _calendario(dados["abertos"], cfg_prog, hoje.year)
    na_janela = hoje.month in cfg_parl["janela_de_exibicao"]["meses"]
    aberta = na_janela or (forcar_emendas and cfg_parl["janela_de_exibicao"].get("permitir_forcar", False))
    dados_parl = mod_parlamentares.carregar_do_disco(hoje.year) if aberta else {}

    PASTA.mkdir(parents=True, exist_ok=True)
    arquivo = PASTA / f"{hoje.isoformat()}.html"
    arquivo.write_text(render(dados, calendario, dados_parl, cfg_parl, hoje, aberta,
                              forcado=aberta and not na_janela), encoding="utf-8")

    historico = sorted(p.name for p in PASTA.glob("*.html") if p.name != "index.html")
    (PASTA / "index.html").write_text(
        "<!doctype html><meta charset=utf-8><title>Relatórios da varredura</title>"
        f"{ESTILO}<main><h1>Relatórios da varredura</h1><div class=card><ul>"
        + "".join(f"<li><a href='{h}'>{h[:-5]}</a></li>" for h in reversed(historico))
        + "</ul></div></main>", encoding="utf-8")

    resumo = {"gerado_em": now_iso(), "referencia": hoje.isoformat(),
              "arquivo": f"relatorios/{hoje.isoformat()}.html",
              "editais_abertos": len(dados["abertos"]),
              "programas_distintos": len({e["programa"] for e in dados["abertos"]}),
              "encerram_em_7_dias": sum(1 for e in dados["abertos"] if (e["situacao"]["dias_para_fim"] or 999) <= 7),
              "area_emendas_aberta": aberta, "emendas_acionam_farol": False}
    write_json(ROOT / "estado/ultimo_relatorio_busca.json", resumo)
    write_json(ROOT / "docs/relatorio-busca.json",
               {**resumo, "abertos": dados["abertos"], "calendario": calendario})
    return resumo

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
