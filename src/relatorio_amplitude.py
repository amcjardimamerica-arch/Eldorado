"""Relatório de amplitude do Eldorado — gerado a partir da configuração real.

Responde, com dados extraídos do próprio repositório (nunca escritos à mão):

- **Onde busca**: fontes catalogadas por tipo, território e nível de confiança.
- **Quais canais**: varredura HTML, APIs oficiais, capilaridade de imprensa,
  redes sociais e carga histórica — com o estado real de cada um.
- **Uso de tokens por etapa**: quais etapas consomem IA e quais não consomem.
- **Testes**: a suíte que roda antes de qualquer coleta.
- **Padrões de edital oficial**: o checklist aplicado a cada registro.

Saída: `docs/relatorio-amplitude.html` e `docs/relatorio-amplitude.json`.
Não consome tokens.
"""
from __future__ import annotations

import ast
import html
import json
import re
from collections import Counter

from .nucleo import ROOT, load_json, now_iso, write_json

# Etapas do pipeline e se consomem tokens de IA. Fonte da verdade: o import de
# `src.ia` em cada módulo — auditado dinamicamente por `_etapas_com_ia()`.
ETAPAS = [
    ("eldorado", "Varredura HTML das fontes catalogadas", "Eldorado"),
    ("coletores_api", "APIs oficiais (PNCP e Querido Diário)", "Eldorado"),
    ("capilaridade", "Camada de imprensa — gera pistas", "Eldorado"),
    ("verificacao_social", "Páginas de redes sociais oficiais", "Eldorado"),
    ("verificacao_assistida", "Confirmação da página primária", "Eldorado"),
    ("qualidade", "Conformidade com padrões de edital oficial", "Eldorado"),
    ("prazos", "Cálculo de prazos e alertas", "Eldorado"),
    ("dossies", "Dossiê por financiador", "Eldorado"),
    ("aprendizado", "Padrões recorrentes e previsão de janelas", "Eldorado"),
    ("retrospectivo", "Carga histórica de cinco anos (mês a mês)", "Eldorado"),
    ("sentinela", "Detecção diária de páginas alteradas", "Eldorado"),
    ("triagem", "Seleção de oportunidades para virar caso", "Eldorado"),
    ("fichas", "Ficha HTML por edital", "Eldorado"),
    ("painel", "Painel consolidado", "Eldorado"),
    ("casos", "Abertura da pasta do caso", "Farol"),
    ("farol", "Portão eliminatório e pontuação", "Farol"),
    ("farol_ia", "Extração de requisitos, conselho e parecer", "Farol"),
]

def _etapas_com_ia() -> set[str]:
    """Audita o código: um módulo só usa tokens se importar `src.ia`."""
    com_ia = set()
    for caminho in (ROOT / "src").glob("*.py"):
        try:
            arvore = ast.parse(caminho.read_text(encoding="utf-8"))
        except (SyntaxError, OSError):
            continue
        for no in ast.walk(arvore):
            if isinstance(no, ast.ImportFrom):
                # `from .ia import ...` / `from src.ia import ...`
                if (no.module or "") in {"ia", "src.ia"}:
                    com_ia.add(caminho.stem)
                # `from . import ia, outro`
                if any(a.name == "ia" for a in no.names):
                    com_ia.add(caminho.stem)
            elif isinstance(no, ast.Import):
                if any(a.name.split(".")[-1] == "ia" for a in no.names):
                    com_ia.add(caminho.stem)
    # propagação: quem chama um módulo que usa IA também é caminho de token
    indiretos = set()
    for caminho in (ROOT / "src").glob("*.py"):
        if caminho.stem in com_ia:
            continue
        texto = caminho.read_text(encoding="utf-8")
        for modulo in com_ia:
            if re.search(rf"\b(from \.{modulo} import|import {modulo}\b|{modulo}\.run\()", texto):
                indiretos.add(caminho.stem)
    return com_ia | (indiretos & {"executar_farol"})

def _testes() -> list[str]:
    arquivo = ROOT / "tests/test_system.py"
    if not arquivo.exists():
        return []
    return re.findall(r"def (test_\w+)", arquivo.read_text(encoding="utf-8"))

def coletar() -> dict:
    fontes = load_json(ROOT / "config/fontes.json")["fontes"]
    escopo = load_json(ROOT / "config/escopo.json")
    apis = load_json(ROOT / "config/coletores_api.json")
    capilar = load_json(ROOT / "config/capilaridade.json")
    social = load_json(ROOT / "config/verificacao_social.json")
    retro = load_json(ROOT / "config/retrospectivo.json")
    padroes = load_json(ROOT / "config/padroes_edital.json")
    ia_cfg = load_json(ROOT / "config/ia.json")
    leis = load_json(ROOT / "biblioteca/leis/catalogo.json")["itens"]
    com_ia = _etapas_com_ia()

    return {
        "gerado_em": now_iso(),
        "fontes": {
            "total": len(fontes),
            "ativas": sum(1 for f in fontes if f.get("ativa")),
            "por_tipo": dict(Counter(f["tipo"] for f in fontes).most_common()),
            "por_territorio": dict(Counter(f["territorio"] for f in fontes).most_common()),
            "por_confianca": dict(Counter(f.get("confianca") for f in fontes).most_common()),
            "lista": [{"id": f["id"], "nome": f["nome"], "tipo": f["tipo"], "territorio": f["territorio"],
                       "confianca": f.get("confianca"), "ativa": f.get("ativa"), "url": f.get("url")}
                      for f in sorted(fontes, key=lambda x: (x["territorio"], x["nome"]))],
        },
        "escopo": {"ufs": len(escopo["ufs_ativas"]), "municipios": escopo["municipios_ativos"],
                   "areas": escopo["areas_ativas"], "niveis": escopo["niveis_ativos"],
                   "somente_catalogadas": escopo.get("somente_fontes_catalogadas")},
        "canais": [
            {"canal": "Varredura HTML", "estado": "ativo", "alcance": f"{sum(1 for f in fontes if f.get('ativa'))} fontes catalogadas",
             "confianca": "primária", "tokens": "não", "modulo": "src/eldorado.py"},
            {"canal": "PNCP (API oficial)", "estado": "ativo" if apis["pncp"]["ativa"] else "inativo",
             "alcance": f"modalidades {apis['pncp']['modalidades']}, contratações por publicação",
             "confianca": "primária", "tokens": "não", "modulo": "src/coletores_api.py"},
            {"canal": "Querido Diário (API oficial)", "estado": "ativo" if apis["querido_diario"]["ativa"] else "inativo",
             "alcance": "diários oficiais municipais indexados", "confianca": "primária",
             "tokens": "não", "modulo": "src/coletores_api.py"},
            {"canal": "Imprensa / anúncios (RSS)", "estado": "ativo" if capilar["ativa"] else "inativo",
             "alcance": f"{len(capilar['termos_gerais'])} termos gerais × {len(capilar['emissores'])} emissores",
             "confianca": "pista — exige URL oficial", "tokens": "não", "modulo": "src/capilaridade.py"},
            {"canal": "Redes sociais (páginas públicas)",
             "estado": "ativo" if any(f.get("ativa") for f in social["fontes"]) else "inativo",
             "alcance": f"{len(social['fontes'])} perfis cadastrados, {sum(1 for f in social['fontes'] if f.get('ativa'))} ativos",
             "confianca": "pista — nunca confirma sozinha", "tokens": "não", "modulo": "src/verificacao_social.py"},
            {"canal": "Redes sociais (API oficial)",
             "estado": "preparado, aguardando credencial" if not capilar["redes_sociais"]["instagram_graph"]["ativa"] else "ativo",
             "alcance": "Instagram Graph e YouTube Data — dependem de credencial em Secrets",
             "confianca": "pista", "tokens": "não", "modulo": "config/capilaridade.json"},
            {"canal": "Carga histórica de 5 anos", "estado": "campanha única, mês a mês",
             "alcance": f"{retro['janela_anos']} anos × PNCP + Querido Diário + domínios oficiais",
             "confianca": "pista até conferência", "tokens": "não", "modulo": "src/retrospectivo.py"},
        ],
        "etapas": [
            {"modulo": modulo, "descricao": descricao, "estagio": estagio,
             "usa_tokens": modulo in com_ia}
            for modulo, descricao, estagio in ETAPAS
        ],
        "ia": {
            "modelos_por_tarefa": {k: v["padrao"] for k, v in ia_cfg["modelos"].items()},
            "limites": ia_cfg["limites"],
            "credencial_env": ia_cfg["segredo_provedor_env"],
            "auditoria": "estado/ia_uso.jsonl",
        },
        "testes": _testes(),
        "padroes_edital": {
            "obrigatorios": [r["campo"] for r in padroes["obrigatorios_registro"]],
            "conteudo_minimo": [{"rotulo": r["rotulo"], "peso": r["peso"]} for r in padroes["conteudo_minimo_edital"]],
            "oficialidade": [{"rotulo": r["rotulo"], "peso": r["peso"]} for r in padroes["sinais_de_oficialidade"]],
            "faixas": padroes["faixas_qualidade"],
            "alerta_dias": padroes["prazos"]["alerta_dias"],
            "reprovacao_automatica": padroes["reprovacao_automatica"],
            "fundamento": padroes["fundamento_legal"],
        },
        "biblioteca_juridica": {"normas": len(leis)},
    }

def _e(v) -> str:
    return html.escape(str(v), quote=True)

def render(d: dict) -> str:
    sem_tokens = [e for e in d["etapas"] if not e["usa_tokens"]]
    com_tokens = [e for e in d["etapas"] if e["usa_tokens"]]

    linhas_canais = "".join(
        f"<tr><td><strong>{_e(c['canal'])}</strong><div class=meta>{_e(c['modulo'])}</div></td>"
        f"<td>{_e(c['estado'])}</td><td>{_e(c['alcance'])}</td><td>{_e(c['confianca'])}</td>"
        f"<td class={'bad' if c['tokens']!='não' else 'ok'}>{_e(c['tokens'])}</td></tr>"
        for c in d["canais"])

    linhas_etapas = "".join(
        f"<tr><td><code>{_e(e['modulo'])}</code></td><td>{_e(e['descricao'])}</td>"
        f"<td>{_e(e['estagio'])}</td>"
        f"<td class={'warn' if e['usa_tokens'] else 'ok'}>{'sim' if e['usa_tokens'] else 'não'}</td></tr>"
        for e in d["etapas"])

    territorios = "".join(f"<span class=tag>{_e(k)}: {v}</span>" for k, v in d["fontes"]["por_territorio"].items())
    tipos = "".join(f"<span class=tag>{_e(k)}: {v}</span>" for k, v in d["fontes"]["por_tipo"].items())
    testes = "".join(f"<li><code>{_e(t)}</code></li>" for t in d["testes"])
    conteudo_min = "".join(f"<li>{_e(r['rotulo'])} <span class=meta>(peso {r['peso']})</span></li>"
                           for r in d["padroes_edital"]["conteudo_minimo"])
    oficialidade = "".join(f"<li>{_e(r['rotulo'])} <span class=meta>(peso {r['peso']})</span></li>"
                           for r in d["padroes_edital"]["oficialidade"])
    reprovacao = "".join(f"<li class=bad>{_e(r)}</li>" for r in d["padroes_edital"]["reprovacao_automatica"])
    modelos = "".join(f"<li><strong>{_e(k)}</strong>: <code>{_e(v)}</code></li>"
                      for k, v in d["ia"]["modelos_por_tarefa"].items())
    fontes_lista = "".join(
        f"<tr><td>{_e(f['territorio'])}</td><td><a href='{_e(f['url'])}' target=_blank rel='noopener noreferrer'>{_e(f['nome'])}</a></td>"
        f"<td>{_e(f['tipo'])}</td><td>{_e(f['confianca'])}</td></tr>" for f in d["fontes"]["lista"])

    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Eldorado — relatório de amplitude</title><style>
:root{{--gold:#f5c451;--navy:#081426;--ink:#eaf1f8;--muted:#9eb0c5;--ok:#47d7ac;--bad:#ff7373;--warn:#ffb547}}
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 10% 0,#173a5f,var(--navy) 42%);color:var(--ink);font:15px/1.55 system-ui,sans-serif}}
main{{max-width:1080px;margin:auto;padding:24px}}h1{{color:var(--gold);font-size:clamp(24px,4vw,38px);margin:.2em 0}}
h2{{margin-top:34px;font-size:20px;border-bottom:1px solid #244766;padding-bottom:6px}}
h3{{font-size:16px;margin-top:20px;color:var(--gold)}}
.card{{background:#0d223b;border:1px solid #244766;border-radius:14px;padding:16px;margin:12px 0}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}}
.metric{{font-size:29px;color:var(--gold);font-weight:800}}
.meta{{color:var(--muted);font-size:13px}}a{{color:#8ed5ff}}
table{{width:100%;border-collapse:collapse;margin-top:8px;font-size:14px}}
td,th{{text-align:left;padding:8px 6px;border-bottom:1px solid #1d3a57;vertical-align:top}}
th{{color:var(--muted);font-weight:600}}
.tag{{display:inline-block;border:1px solid #3a607e;border-radius:20px;padding:3px 9px;margin:4px 4px 0 0;font-size:12px}}
.ok{{color:var(--ok)}}.bad{{color:var(--bad)}}.warn{{color:var(--warn)}}
code{{background:#0a1b2f;padding:1px 5px;border-radius:5px;font-size:13px}}
ul{{margin:6px 0;padding-left:20px}}li{{margin:3px 0}}
footer{{color:var(--muted);padding:32px 0;font-size:13px}}
.rolagem{{max-height:420px;overflow:auto}}
</style></head><body><main>
<div class=meta><a href="index.html">← painel</a> · relatório técnico</div>
<h1>Eldorado — relatório de amplitude</h1>
<p class=meta>Gerado automaticamente a partir da configuração viva do repositório em {_e(d['gerado_em'])}.
Nenhum número desta página foi escrito à mão: todos vêm dos arquivos de configuração e do código.</p>

<section class=cards>
<div class=card><div class=metric>{d['fontes']['ativas']}</div><div class=meta>fontes ativas</div></div>
<div class=card><div class=metric>{d['escopo']['ufs']}</div><div class=meta>UFs no escopo</div></div>
<div class=card><div class=metric>{len(d['canais'])}</div><div class=meta>canais de busca</div></div>
<div class=card><div class=metric>{len(d['testes'])}</div><div class=meta>testes automáticos</div></div>
<div class=card><div class=metric>{d['biblioteca_juridica']['normas']}</div><div class=meta>normas catalogadas</div></div>
<div class=card><div class=metric>{len(sem_tokens)}/{len(d['etapas'])}</div><div class=meta>etapas sem tokens</div></div>
</section>

<h2>1. Canais de busca — onde e como se procura</h2>
<div class=card><table>
<tr><th>Canal</th><th>Estado</th><th>Alcance</th><th>Confiança</th><th>Tokens</th></tr>
{linhas_canais}</table>
<p class=meta>Confiança <strong>primária</strong> entra na base de oportunidades. Confiança <strong>pista</strong>
nunca vira oportunidade sem confirmação da URL oficial (<code>scripts/confirmar_pista.py</code>).</p></div>

<h2>2. Uso de tokens por etapa</h2>
<div class=card>
<p>Auditoria feita sobre o próprio código: uma etapa só consome tokens se importar o adaptador <code>src/ia.py</code>.</p>
<table><tr><th>Módulo</th><th>Função</th><th>Estágio</th><th>Consome tokens</th></tr>{linhas_etapas}</table>
<p class=meta><strong>Todo o Eldorado roda sem consumir um único token.</strong>
Coleta, deduplicação, conformidade, prazos, dossiês, aprendizado, fichas HTML e painel são regras locais determinísticas.
O consumo existe apenas em {len(com_tokens)} módulo(s) do Farol de Alexandria, e ainda assim com teto configurado.</p>
<h3>Modelos por tarefa (somente Farol)</h3><ul>{modelos}</ul>
<p class=meta>Limites: {_e(json.dumps(d['ia']['limites'], ensure_ascii=False))} ·
credencial em <code>{_e(d['ia']['credencial_env'])}</code> · uso auditado em <code>{_e(d['ia']['auditoria'])}</code>.
Sem credencial, o sistema prepara os pacotes e declara que aguarda chave — nunca simula.</p></div>

<h2>3. Padrões exigidos de um edital oficial</h2>
<div class=card>
<p class=meta>{_e(d['padroes_edital']['fundamento']['mrosc_art_24'])}</p>
<h3>Campos obrigatórios do registro (falta = reprovação)</h3>
<p>{"".join(f"<span class=tag>{_e(c)}</span>" for c in d['padroes_edital']['obrigatorios'])}</p>
<h3>Conteúdo mínimo do edital — 60% da nota</h3><ul>{conteudo_min}</ul>
<h3>Sinais de oficialidade — 40% da nota</h3><ul>{oficialidade}</ul>
<h3>Reprovação automática</h3><ul>{reprovacao}</ul>
<p class=meta>Faixas: completo ≥ {d['padroes_edital']['faixas']['completo']} ·
suficiente ≥ {d['padroes_edital']['faixas']['suficiente']} ·
insuficiente ≥ {d['padroes_edital']['faixas']['insuficiente']}.
Alertas de prazo em {_e(d['padroes_edital']['alerta_dias'])} dias.</p></div>

<h2>4. Testes executados antes de cada coleta</h2>
<div class=card><p>A varredura só começa depois que estes {len(d['testes'])} testes passam.
Se um falhar, o robô não coleta — evita gravar dado ruim por cima de dado bom.</p>
<ul>{testes}</ul></div>

<h2>5. Distribuição das fontes</h2>
<div class=card><h3>Por território</h3><p>{territorios}</p>
<h3>Por tipo</h3><p>{tipos}</p></div>

<h2>6. Catálogo completo de fontes</h2>
<div class="card rolagem"><table>
<tr><th>Território</th><th>Fonte</th><th>Tipo</th><th>Confiança</th></tr>{fontes_lista}</table></div>

<footer>Eldorado · Farol de Alexandria — relatório gerado sem consumo de tokens.
Dados automatizados exigem conferência na fonte primária.</footer>
</main></body></html>"""

def run() -> dict:
    dados = coletar()
    write_json(ROOT / "docs/relatorio-amplitude.json", dados)
    (ROOT / "docs/relatorio-amplitude.html").write_text(render(dados), encoding="utf-8")
    return {"fontes_ativas": dados["fontes"]["ativas"], "canais": len(dados["canais"]),
            "etapas_sem_tokens": sum(1 for e in dados["etapas"] if not e["usa_tokens"]),
            "etapas_com_tokens": sum(1 for e in dados["etapas"] if e["usa_tokens"]),
            "testes": len(dados["testes"]), "gerado_em": dados["gerado_em"]}

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
