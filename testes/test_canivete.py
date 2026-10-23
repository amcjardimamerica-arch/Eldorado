"""O motor padrão (titular, 23/10/2026): o canivete enriquece cada achado com o que o texto e a página dizem."""
import pytest

from eldorado.motores.leitura.enriquecer import enriquecer

HTML = """<html><head><title>Edital</title><meta property="article:published_time" content="2026-10-10T09:00:00-03:00"/>
<script type="application/ld+json">{"@context":"https://schema.org","@type":"Event","name":"Edital de Fomento Cultural 2026",
"startDate":"2026-10-10","endDate":"2026-11-30","organizer":{"@type":"Organization","name":"Secretaria de Cultura"}}</script></head>
<body><nav>Início | Notícias | Contato | Ouvidoria | Transparência</nav><main><h1>Edital de Fomento Cultural 2026</h1>
<p>A Secretaria de Cultura torna público o edital de fomento a projetos culturais de organizações da sociedade civil. O valor
total é de R$ 1,5 milhão, com até R$ 50.000,00 por projeto. As inscrições vão de 10/10/2026 até 30/11/2026, pelo portal.
O resultado preliminar será divulgado em 15/12/2026, com prazo de recurso de cinco dias.</p></main>
<footer>Rua X, 100 · Goiânia · Todos os direitos reservados</footer></body></html>"""


def test_o_canivete_extrai_idioma_datas_valores_metadados_e_publicacao():
    for m in ("lingua", "datefinder", "extruct", "htmldate"):
        pytest.importorskip(m)
    r = enriquecer(None, HTML, "https://cultura.go.gov.br/edital")
    assert r["idioma"] == "pt"
    assert r["publicacao"] == "2026-10-10"
    prazos = [d for d in r["datas"] if d["prazo"]]
    assert {"2026-11-30", "2026-12-15"} <= {d["data"] for d in prazos}
    assert {1_500_000.0, 50_000.0} <= {v["valor"] for v in r["valores"]}
    assert any(m.get("@type") == "Event" and m.get("endDate") == "2026-11-30" for m in r["metadados"])
    assert "texto_principal" in r and "Ouvidoria" not in r["texto_principal"]           # sem o menu


def test_habilidade_desligada_e_texto_sem_html():
    r = enriquecer("Inscrições até 30/11/2026. Valor de R$ 10 mil.", None, None, ligadas=("valores",))
    assert [v["valor"] for v in r["valores"]] == [10_000.0] and "datas" not in r
