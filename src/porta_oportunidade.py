"""PORTÃO DE OPORTUNIDADE NO MOTOR (titular, 16/10/2026).

"Cada motor lê o que for relevante e extrai SOMENTE o que for oportunidade de fato, criando ou vinculando um livro."
Antes de qualquer gravação, cada achado passa por aqui. O que não é oportunidade é só CONTADO, nunca guardado.
Critérios (os mesmos já usados no resto do sistema, num lugar só):
  · sem título                                         → não é registro de oportunidade
  · não é oportunidade (licitação, listagem, resultado, vaga, pessoa física, ato tributário, ... — repositório único)
  · portão do PNCP (compra, contrato de serviço, município de outro estado, ...)       quando o achado é do PNCP
  · prazo de inscrição já encerrado                    → não serve à associação
"""
from __future__ import annotations

import re
from datetime import date


def motivo_para_nao_guardar(a: dict, hoje: str | None = None) -> str | None:
    hoje = hoje or date.today().isoformat()
    titulo = str(a.get("titulo") or a.get("nome") or "").strip()
    if len(titulo) < 6:
        return "sem título"
    try:
        from .repositorio_unico import nao_e_oportunidade
        m = nao_e_oportunidade({**a, "titulo": titulo})
        if m:
            return m
    except Exception:  # noqa: BLE001
        pass
    try:                                                   # 16/10: em outros estados, só estaduais e capitais
        from .repositorio_unico import municipal_fora_de_goias
        m = municipal_fora_de_goias({**a, "titulo": titulo})
        if m:
            return "município de outro estado (não capital)"
    except Exception:  # noqa: BLE001
        pass
    url = f"{a.get('url') or ''} {a.get('link_oficial') or ''}"
    if "pncp.gov.br" in url:
        try:
            from .pncp_osc import veredito_por_titulo
            m = veredito_por_titulo(titulo, str(a.get("url") or ""), a.get("uf"), a.get("fim"))
            if m:
                return f"PNCP — {m}"
        except Exception:  # noqa: BLE001
            pass
    fim = str(a.get("fim") or a.get("prazo_fim") or "")[:10]
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", fim) and fim < hoje:
        return f"prazo encerrado em {fim}"
    return None
