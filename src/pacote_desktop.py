"""PACOTE PARA O CLAUDE DESKTOP — o que o robô não conseguiu, o computador do titular termina.

Quando o titular abre o Claude no computador dele, a sessão lê estado/pacote_desktop.md e:
  1. roda os MOTORES que não executaram ou aguardam coleta local (IP brasileiro);
  2. complementa as OPORTUNIDADES parciais (sem objeto, prazo ou página oficial),
     lendo o edital na fonte e devolvendo o JSON no formato de coleta_navegador;
  3. valida com o modelo mais forte disponível (Opus 5) o que ficou em "atenção".

O pacote é gerado a cada saída do CI e fica sempre atual. A sessão do Desktop não
precisa perguntar nada: o arquivo diz o que fazer, em que ordem e em que formato devolver.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json


def montar() -> dict:
    hoje = date.today().isoformat()
    alerta = load_json(ROOT / "estado/alerta_motores.json") if (ROOT / "estado/alerta_motores.json").exists() else {}
    fluxo = load_json(ROOT / "estado/fluxo_verificacao.json") if (ROOT / "estado/fluxo_verificacao.json").exists() else {}
    fila = load_json(ROOT / "estado/fila_verificacao.json") if (ROOT / "estado/fila_verificacao.json").exists() else {}
    rotas = load_json(ROOT / "config/rotas_motores.json") if (ROOT / "config/rotas_motores.json").exists() else {}
    motores = [a for a in (alerta.get("alertas") or [])]
    locais = [a for a in motores if "coleta local" in a["problema"]]
    outros = [a for a in motores if "coleta local" not in a["problema"]]
    externa = (fluxo.get("aguardando_acao_externa") or {}).get("itens") or []
    parciais = [x for x in (fila.get("itens") or []) if x.get("selo_validacao") != "validada" and x.get("modo") == "completo"][:40]
    L = [f"# Pacote para o Claude Desktop — {hoje}", "",
         "Você está no computador do titular, com IP brasileiro, navegador e o repositório Eldorado clonado. Use o modelo mais forte disponível (Opus 5) para validar. Trabalhe nesta ordem, sem pular etapa, e devolva os arquivos no formato indicado. Nunca estime datas; quando não houver base, escreva o motivo.",
         "", "## Etapa 1 — motores que aguardam coleta local (portais que recusam IP estrangeiro)", ""]
    if locais:
        L.append("Rode uma vez, na raiz do repositório:"); L.append(""); L.append("```"); L.append("python scripts/coleta_brasil.py"); L.append("```"); L.append("")
        L.append("Ele lê com o seu IP e envia ao repositório. Motores atendidos:")
        for a in locais:
            m = (rotas.get("motores") or {}).get(a["id"]) or {}
            L.append(f"- **{a['nome']}** — rotas: " + "; ".join(r["nome"] for r in (m.get("rotas") or [])[:3]))
    else:
        L.append("Nenhum motor aguardando coleta local hoje.")
    L += ["", "## Etapa 2 — motores em alerta (não leram, falharam ou passaram da cadência)", ""]
    if outros:
        for a in outros:
            m = (rotas.get("motores") or {}).get(a["id"]) or {}
            L.append(f"- **{a['nome']}** — {a['problema']}. Ação: {a['acao']}.")
            for r in (m.get("rotas") or [])[:3]:
                if r.get("url") and str(r["url"]).startswith("http"):
                    L.append(f"    - abrir {r['url']} e procurar: {', '.join((m.get('lexico_camada1') or [])[:6])}")
        L.append(""); L.append("Para cada rota aberta, liste os editais publicados nos últimos 30 dias que casem com o léxico e que ainda não estejam em `dados/editais/`. Devolva em `dados/editais/coleta_navegador/<data>-motores.json` no formato `{\"<id ou novo>\": {\"objeto\":..., \"inicio\":..., \"fim\":..., \"pagina_oficial\":..., \"observacao\":...}}`.")
    else:
        L.append("Nenhum motor em alerta.")
    L += ["", f"## Etapa 3 — oportunidades aguardando ação externa ({len(externa)})", ""]
    for x in externa[:40]:
        L.append(f"- `{x['id']}` — {x['titulo'][:90]} · **{x['motivo_texto']}** → {x['acao']}" + (f" · link: {x['link']}" if x.get("link") else ""))
    L += ["", f"## Etapa 4 — oportunidades parciais do modo completo, para validar com Opus 5 ({len(parciais)})", "",
          "Para cada uma, abra a página oficial (nunca PNCP, diário ou portal de notícia; exceção: o arquivo do edital do órgão hospedado no PNCP, em `/arquivos/`), extraia OBJETO, PRAZO (início e fim) e URL oficial, e dê o veredito: aprovado (chamada aberta de fomento a OSC), atenção (serve, mas o enquadramento exige conferência) ou reprovado (com a família: resultado de edital, seleção de empresa, serviço ao órgão, qualificação como OS, órgão buscando patrocinador, parceria já celebrada).", ""]
    for x in parciais:
        L.append(f"- `{x['id']}` — {x['titulo'][:90]} · falta: {', '.join(x['minimas']['faltam'])}" + (f" · {x['link_oficial']}" if x.get("link_oficial") else ""))
    L += ["", "## Etapa 4½ — IA local (organização automática, sem gastar Claude)", "",
          "Se a pasta `ia_local/` ainda não existe: `python scripts/ia_local_instalar.py` (uma vez, ~2 GB; `--leve` para 1 GB).",
          "Suba o servidor local (`ia_local/iniciar.bat` ou `.sh`, deixe a janela aberta) e rode:", "", "```",
          "python -m src.ia_local ciclo      # classifica os incompletos, extrai objeto/prazo com trecho literal, propõe léxico, diagnostica motores 'lendo sem achar'",
          "python -m src.ia_local aplicar    # grava só o que passou na validação — como PROPOSTA, nunca sobrescrevendo dado confirmado", "```", "",
          "As sugestões de rota ficam em `estado/rotas_sugeridas_ia.json` com status 'a confirmar pelo titular'; as extrações entram em `proposta_ia` no registro para o Opus 5 validar na Etapa 4.",
          "", "## Etapa 5 — fechar o ciclo", "",
          "```", "python -m src.enquadramento ingerir_navegador", "python -m src.enquadramento", "python -m src.enquadramento fila",
          "python -m src.alerta_motores", "python -m src.auditoria_motores", "python -m src.dashboard_dados",
          "python -m unittest tests.test_system  # só siga com tudo verde",
          "python scripts/verificar_privacidade.py", "git add -A && git commit -m \"desktop: complementacao <data>\" && git pull --rebase origin main && git push", "```", "",
          "## Resumo final que você deve me dar", "",
          "Quantos motores voltaram a ler, quantas oportunidades foram completadas, quantas não eram editais, quais sites não abriram — e o que ficou para o titular decidir."]
    texto = "\n".join(L)
    (ROOT / "estado/pacote_desktop.md").write_text(texto, encoding="utf-8")
    (ROOT / "docs/dados/pacote_desktop.md").write_text(texto, encoding="utf-8")
    res = {"em": now_iso(), "motores_coleta_local": len(locais), "motores_em_alerta": len(outros),
           "oportunidades_acao_externa": len(externa), "oportunidades_parciais": len(parciais), "arquivo": "estado/pacote_desktop.md"}
    write_json(ROOT / "estado/pacote_desktop.json", res)
    return res


if __name__ == "__main__":
    print(json.dumps(montar(), ensure_ascii=False, indent=2))
