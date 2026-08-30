"""Ficha HTML por edital — uma página por oportunidade analisada.

Cada análise produz um arquivo estático em `docs/editais/<id>.html` contendo:
dados do edital, fonte e URL primária, evidência com hash, prazo e urgência,
conformidade com os padrões oficiais (o que foi atendido e o que ficou
pendente) e o histórico de aprendizado do financiador quando existir.

Sem IA e sem tokens: tudo é montado a partir do registro já coletado. O que a
fonte não disse aparece como pendência declarada, nunca como texto inventado.

A carga histórica de cinco anos NÃO chama este módulo — ela é levantamento de
padrão, não análise de oportunidade viva.
"""
from __future__ import annotations

import html
import json

from .nucleo import ROOT, carregar_oportunidades, load_json, now_iso, write_json

PASTA = ROOT / "docs/editais"

ESTILO = """<style>
:root{--gold:#f5c451;--navy:#081426;--ink:#eaf1f8;--muted:#9eb0c5;--ok:#47d7ac;--bad:#ff7373;--warn:#ffb547}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 10% 0,#173a5f,var(--navy) 42%);color:var(--ink);font:15px/1.55 system-ui,sans-serif}
main{max-width:900px;margin:auto;padding:24px}h1{color:var(--gold);font-size:clamp(21px,3.6vw,32px);margin:.3em 0}
h2{margin-top:28px;font-size:18px;border-bottom:1px solid #244766;padding-bottom:6px}
.card{background:#0d223b;border:1px solid #244766;border-radius:14px;padding:16px;margin:12px 0}
.meta{color:var(--muted);font-size:13px}a{color:#8ed5ff;word-break:break-word}
.tag{display:inline-block;border:1px solid #3a607e;border-radius:20px;padding:3px 10px;margin:4px 4px 0 0;font-size:13px}
.ok{color:var(--ok)}.bad{color:var(--bad)}.warn{color:var(--warn)}
table{width:100%;border-collapse:collapse;margin-top:8px}td,th{text-align:left;padding:7px 6px;border-bottom:1px solid #1d3a57;vertical-align:top;font-size:14px}
blockquote{margin:8px 0;padding:10px 14px;background:#0a1b2f;border-left:3px solid #3a607e;border-radius:0 8px 8px 0;font-size:14px}
th{color:var(--muted);font-weight:600;width:34%}
.barra{height:9px;background:#0a1b2f;border-radius:6px;overflow:hidden;border:1px solid #2b4c6b}
.barra>i{display:block;height:100%;background:var(--gold)}
ul{margin:6px 0;padding-left:20px}li{margin:3px 0}
footer{color:var(--muted);padding:30px 0;font-size:13px}
.aviso{border-left:3px solid var(--warn);padding-left:12px}
</style>"""

def _e(valor) -> str:
    return html.escape(str(valor if valor not in (None, "") else "—"), quote=True)

def _situacao_prazo(item: dict) -> tuple[str, str]:
    dias = item.get("prazo_dias_restantes")
    situacao = item.get("prazo_situacao") or "sem_prazo_identificado"
    if situacao == "encerrado":
        return "bad", "Prazo mencionado já encerrado"
    if dias is None:
        return "meta", "Prazo não identificado na fonte — conferir no edital"
    if dias <= 7:
        return "bad", f"Faltam {dias} dia(s)"
    if dias <= 30:
        return "warn", f"Faltam {dias} dia(s)"
    return "ok", f"Faltam {dias} dia(s)"

def render(item: dict, aprendizado: dict | None = None) -> str:
    q = item.get("qualidade") or {}
    classe_prazo, texto_prazo = _situacao_prazo(item)
    atendidos = q.get("conteudo_atendido", []) + q.get("oficialidade_atendida", [])
    pendentes = q.get("conteudo_pendente", []) + q.get("oficialidade_pendente", [])
    nota = q.get("nota", 0)

    linhas_tabela = [
        ("Fonte", _e(item.get("fonte_nome"))),
        ("Território", _e(item.get("territorio"))),
        ("Tipo de fonte", _e(item.get("tipo_fonte"))),
        ("Nível de confiança", _e(item.get("confianca"))),
        ("Situação no funil", _e(item.get("status"))),
        ("Data de publicação", _e(item.get("data_publicacao"))),
        ("Prazo mencionado", _e(item.get("prazo_texto"))),
        ("Ano de referência", _e(item.get("ano_referencia"))),
        ("Coletado em", _e(item.get("coletado_em"))),
        ("Hash da evidência", f"<code class=meta>{_e(item.get('hash_evidencia'))}</code>"),
    ]
    tabela = "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in linhas_tabela)

    bloco_atendidos = "".join(
        f"<li class=ok>{_e(x['rotulo'])} <span class=meta>— localizado por “{_e(x.get('evidencia_termo'))}”</span></li>"
        for x in atendidos) or "<li class=meta>Nenhum item confirmado no texto capturado.</li>"
    bloco_pendentes = "".join(f"<li class=warn>{_e(x['rotulo'])}</li>" for x in pendentes) \
        or "<li class=ok>Nenhuma pendência de conformidade.</li>"

    bloco_aprendizado = ""
    if aprendizado:
        padroes = aprendizado.get("padroes_confirmados") or []
        previsao = aprendizado.get("previsao_janela")
        partes = []
        if padroes:
            partes.append("<p class=meta>Requisitos recorrentes deste financiador (2+ ocorrências validadas):</p><ul>"
                          + "".join(f"<li>{_e(p['requisito'])}: {_e(p['valor'])} <span class=meta>({p['ocorrencias']}x)</span></li>"
                                    for p in padroes[:10]) + "</ul>")
        if previsao:
            partes.append(f"<p>Janela provável de publicação: <strong>{_e(', '.join(previsao.get('janela_provavel', [])))}</strong> "
                          f"<span class=meta>(hipótese por recorrência em {_e(previsao.get('anos_de_base'))})</span></p>")
        if partes:
            bloco_aprendizado = f"<h2>Aprendizado acumulado</h2><div class=card>{''.join(partes)}</div>"

    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_e(item.get('titulo'))[:90]} · Eldorado</title>{ESTILO}</head><body><main>
<div class=meta><a href="../index.html">← painel</a> · ficha de edital</div>
<h1>{_e(item.get('titulo'))}</h1>
<p><a href="{_e(item.get('url'))}" target=_blank rel="noopener noreferrer">{_e(item.get('url'))}</a></p>
<span class="tag {classe_prazo}">{_e(texto_prazo)}</span>
<span class=tag>conformidade: {nota}/100 — {_e(q.get('classe'))}</span>
<span class=tag>{_e(item.get('status'))}</span>

<h2>Conformidade com os padrões de edital oficial</h2>
<div class=card>
<div class=barra><i style="width:{max(0, min(100, nota))}%"></i></div>
<p class=meta>Base do checklist: Lei 13.019/2014, art. 24, §1º (conteúdo mínimo do chamamento público) e sinais de oficialidade do ato. Verificação automática sobre o texto capturado.</p>
<p><strong>Atendido</strong></p><ul>{bloco_atendidos}</ul>
<p><strong>Pendente de confirmação no edital</strong></p><ul>{bloco_pendentes}</ul>
</div>

<h2>Dados do registro</h2>
<div class=card><table>{tabela}</table></div>

<h2>Evidência capturada</h2>
<div class=card><p class=meta>Trecho literal que motivou a captura, preservado sem edição:</p>
<blockquote>{_e(item.get('evidencia'))}</blockquote></div>
{bloco_aprendizado}

<h2>Como usar esta ficha</h2>
<div class="card aviso">
<p>Este documento é <strong>resultado de coleta automatizada</strong>. Prazo, valor, requisitos e vigência
precisam ser conferidos na página primária antes de qualquer decisão ou submissão. Itens marcados como
pendentes significam apenas que <em>não foram localizados no texto capturado</em> — podem existir no edital completo.</p>
</div>
<footer>Gerado automaticamente em {_e(now_iso())} · Eldorado · Farol de Alexandria</footer>
</main></body></html>"""

def run() -> dict:
    registros = carregar_oportunidades()
    PASTA.mkdir(parents=True, exist_ok=True)
    indice, gerados = [], 0
    for item in sorted(registros.values(), key=lambda x: (x.get("prazo_dias_restantes") is None,
                                                          x.get("prazo_dias_restantes", 9999))):
        if item.get("status") in {"quarentena_prompt_injection", "descartada"}:
            continue
        aprendizado = None
        caminho_ap = ROOT / "dados/financiadores" / (item.get("fonte_id") or "") / "aprendizado.json"
        if caminho_ap.exists():
            try:
                aprendizado = load_json(caminho_ap)
            except (json.JSONDecodeError, OSError):
                aprendizado = None
        (PASTA / f"{item['id']}.html").write_text(render(item, aprendizado), encoding="utf-8")
        gerados += 1
        indice.append({
            "id": item["id"], "titulo": item.get("titulo"), "url": item.get("url"),
            "ficha": f"editais/{item['id']}.html", "fonte_nome": item.get("fonte_nome"),
            "territorio": item.get("territorio"), "status": item.get("status"),
            "nota_conformidade": (item.get("qualidade") or {}).get("nota"),
            "classe_conformidade": (item.get("qualidade") or {}).get("classe"),
            "prazo_situacao": item.get("prazo_situacao"), "dias_restantes": item.get("prazo_dias_restantes"),
        })
    write_json(ROOT / "docs/fichas.json", {"gerado_em": now_iso(), "total": gerados, "fichas": indice})
    return {"fichas_geradas": gerados, "gerado_em": now_iso()}

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
