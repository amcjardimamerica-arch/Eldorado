"""Vigilância de prazos — determinística, sem IA e sem tokens.

Lê o prazo textual extraído da fonte (`prazo_texto`), calcula os dias corridos
restantes e classifica cada oportunidade em faixas de urgência definidas em
`config/padroes_edital.json` → prazos.alerta_dias.

Nada aqui substitui a leitura do edital: o prazo capturado é sempre rotulado
como *mencionado na fonte, exige conferência*. Prazos vencidos não somem — o
histórico alimenta o aprendizado de janelas recorrentes.

Saídas: `estado/prazos.json` (consumido pelo painel, pelas fichas HTML e pelo
resumo de execução) e marcação `alerta_prazo` em `estado/alerta_prazos.json`
quando algo entra na faixa crítica.

AS BASES VERIFICADAS TAMBÉM ENTRAM — correção de 12/09/2026. Até aqui este
módulo lia apenas a base de oportunidades coletadas, que hoje é quase toda
formada por edições de diário oficial sem prazo nenhum. O resultado medido na
inspeção de 10/09: **zero prazos encontrados em 17.493 registros**, `abrir_issue`
em falso desde 03/09, e o passo "Abrir issue de prazos a vencer" do workflow
nunca disparando — enquanto a verificação tinha 339 prazos confirmados em
documento oficial e 55 editais abertos, em um arquivo que nenhum módulo lia.

O vigia de prazos estava cego, e não por falha: por estar olhando para a base
errada. Agora lê as duas, e o prazo confirmado em documento do órgão vence.
"""
from __future__ import annotations

import json
import re
from datetime import date, datetime

from .nucleo import (ROOT, carregar_oportunidades, chave_curta, load_json, now_iso,
                     write_json)

_DATA_BR = re.compile(r"(\d{1,2})/(\d{1,2})/(20\d{2})")
_DATA_ISO = re.compile(r"(20\d{2})-(\d{2})-(\d{2})")

# Bases em que a data final já foi confirmada em fonte oficial, registro por
# registro. Em ordem de confiança: a primeira que tiver o registro vence.
BASES_VERIFICADAS = (
    # A mais recente vence. O fechamento de 23/09/2026 foi lido pelo NAVEGADOR
    # LOCAL do titular — unica rota que alcancou o PNCP naquele dia — e corrigiu
    # a chave de Osorio/RS, que na base apontava para um registro inexistente.
    ROOT / "docs/dados/verificacao_fechamento_2026-09-23.json",
    ROOT / "docs/dados/verificacao_63_2026-09-15.json",
    ROOT / "docs/dados/verificacao_467_2026-09-09.json",
    ROOT / "docs/dados/nao_verificados.json",
)


def _linhas_verificadas(hoje: date, faixas: list[int], ja_vistos: set) -> list[dict]:
    """Prazos confirmados nas bases de verificação, prontos para o alarme."""
    linhas = []
    vistos_por_objeto: set = set()
    for caminho in BASES_VERIFICADAS:
        if not caminho.exists():
            continue
        try:
            itens = load_json(caminho).get("itens")
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(itens, dict):
            registros = [(chave_curta(c), v) for c, v in itens.items()]
        elif isinstance(itens, list):
            registros = [(chave_curta(x.get("id")), x) for x in itens]
        else:
            continue
        for chave, item in registros:
            if not chave or chave in ja_vistos:
                continue
            # registro reprovado pelo objeto não é oportunidade: não vai ao alarme
            if item.get("veredito") == "reprovado":
                continue
            prazo = item.get("fim") or (item.get("prazo_atual") or {}).get("fim")
            achado = _DATA_ISO.search(str(prazo or ""))
            if not achado:
                continue
            try:
                vencimento = date(*(int(g) for g in achado.groups()))
            except ValueError:
                continue
            dias = (vencimento - hoje).days
            # o mesmo edital entra uma vez so: o Instituto Lojas Renner aparecia
            # cinco vezes na base de 09/09, capturado por rotas diferentes
            assinatura = (re.sub(r"\W+", " ", str(item.get("objeto") or item.get("titulo") or "").lower()).strip()[:200],
                          str(item.get("orgao") or "").lower(), vencimento.isoformat())
            if assinatura[0] and assinatura in vistos_por_objeto:
                continue
            vistos_por_objeto.add(assinatura)
            ja_vistos.add(chave)
            linhas.append({
                "id": chave, "titulo": item.get("objeto") or item.get("titulo") or item.get("edital"),
                "url": item.get("pagina_oficial") or item.get("link_capturado"),
                "fonte_nome": item.get("orgao") or item.get("edital") or item.get("fonte_nome"),
                "territorio": item.get("uf"), "status": item.get("veredito"),
                "vencimento": vencimento.isoformat(), "dias_restantes": dias,
                "situacao": classificar(dias, faixas),
                "observacao": ("prazo confirmado na verificação individual — "
                               f"origem: {caminho.name}"),
            })
    return linhas

def data_do_prazo(item: dict) -> date | None:
    """Extrai a data do prazo sem inventar: só converte o que está escrito."""
    for campo in ("prazo_final", "prazo_texto"):
        bruto = str(item.get(campo) or "")
        achado = _DATA_BR.search(bruto)
        if achado:
            dia, mes, ano = (int(g) for g in achado.groups())
            try:
                return date(ano, mes, dia)
            except ValueError:
                continue
        achado = _DATA_ISO.search(bruto)
        if achado:
            ano, mes, dia = (int(g) for g in achado.groups())
            try:
                return date(ano, mes, dia)
            except ValueError:
                continue
    return None

def classificar(dias: int | None, faixas: list[int]) -> str:
    if dias is None:
        return "sem_prazo_identificado"
    if dias < 0:
        return "encerrado"
    for limite in sorted(faixas):
        if dias <= limite:
            return f"faltam_{limite}_dias_ou_menos"
    return "em_aberto"

def run(hoje: date | None = None) -> dict:
    cfg = load_json(ROOT / "config/padroes_edital.json")["prazos"]
    faixas = cfg["alerta_dias"]
    hoje = hoje or date.today()
    registros = carregar_oportunidades()
    linhas = []
    for item in registros.values():
        vencimento = data_do_prazo(item)
        dias = (vencimento - hoje).days if vencimento else None
        situacao = classificar(dias, faixas)
        item["prazo_situacao"] = situacao
        item["prazo_dias_restantes"] = dias
        if vencimento:
            linhas.append({
                "id": item["id"], "titulo": item.get("titulo"), "url": item.get("url"),
                "fonte_nome": item.get("fonte_nome"), "territorio": item.get("territorio"),
                "status": item.get("status"), "vencimento": vencimento.isoformat(),
                "dias_restantes": dias, "situacao": situacao,
                "observacao": "prazo mencionado na fonte — conferir no edital antes de qualquer decisão",
            })
    # So se evita repetir o que JA VIROU LINHA de prazo. Usar todos os ids da base
    # de oportunidades como vistos apagaria justamente os prazos confirmados dos
    # registros que existem nas duas bases — e e la que estao as oportunidades.
    linhas += _linhas_verificadas(hoje, faixas, {chave_curta(x["id"]) for x in linhas})
    linhas.sort(key=lambda x: x["dias_restantes"])
    criticos = [x for x in linhas if x["dias_restantes"] is not None and 0 <= x["dias_restantes"] <= max(faixas)]
    relatorio = {
        "gerado_em": now_iso(), "referencia": hoje.isoformat(),
        "com_prazo": len(linhas), "criticos": len(criticos),
        "encerrados": sum(1 for x in linhas if x["situacao"] == "encerrado"),
        "sem_prazo": sum(1 for x in registros.values() if x.get("prazo_situacao") == "sem_prazo_identificado"),
        "faixas_alerta": faixas, "itens": linhas[:500],
    }
    write_json(ROOT / "estado/prazos.json", relatorio)

    if criticos:
        corpo = ["Oportunidades com prazo próximo do encerramento (data mencionada na fonte, conferir no edital):", ""]
        corpo += [f"- **{x['dias_restantes']} dia(s)** — [{x['titulo']}]({x['url']}) · {x['fonte_nome']}" for x in criticos[:40]]
        write_json(ROOT / "estado/alerta_prazos.json", {
            "abrir_issue": True, "titulo": f"Prazos a vencer — {hoje.isoformat()}",
            "corpo": "\n".join(corpo), "quantidade": len(criticos), "gerado_em": now_iso(),
        })
    else:
        write_json(ROOT / "estado/alerta_prazos.json", {"abrir_issue": False, "gerado_em": now_iso()})

    from .nucleo import gravar_oportunidades
    gravar_oportunidades(registros)
    return {k: v for k, v in relatorio.items() if k != "itens"}

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
