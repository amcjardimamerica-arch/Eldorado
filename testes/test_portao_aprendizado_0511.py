"""05/11/2026 (verificação externa, grupos 2 e 3): os aprendizados na entrada — página institucional do governo e
chamada para pesquisador são barradas; o edital publicado no gov.br e a chamada para OSC passam."""
import json
from pathlib import Path

from eldorado.base.missao.regras_portao import nao_e_oportunidade as n


def test_pagina_institucional_do_governo_barrada():
    assert "institucional" in n({"titulo": "Acesso à Informação", "url": "https://www.gov.br/cultura/pt-br/acesso-a-informacao/x"})
    assert "institucional" in n({"titulo": "PNCP", "url": "https://pncp.gov.br/app/editais"})
    assert n({"titulo": "Edital nº 12/2026 — Fomento a OSC", "url": "https://www.gov.br/cultura/pt-br/assuntos/noticias/edital-12"}) is None


def test_chamada_para_pesquisador_barrada_e_para_osc_passa():
    assert "pesquisador" in n({"titulo": "Chamada CNPq 30/2026 — Bolsas de produtividade em pesquisa", "url": "https://cnpq.br/c"})
    assert n({"titulo": "Chamada pública para OSC — extensão com associações", "url": "https://fapeg.go.gov.br/c"}) is None


def test_replicadores_novos():
    d = json.loads(Path("config/missao/republicadores.json").read_text(encoding="utf-8"))
    assert {"developmentaid.org", "fundsforngos.org", "opportunitiesfeed.com"} <= set(d["agregador"])
