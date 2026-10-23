"""Os testes com respostas HTTP gravadas (plano C: vcrpy): a escada de acesso sobre a resposta real das edições do Diário
de Goiás (gravada em 23/10/2026), em cassete, sem servidor e sem internet."""
import json
from pathlib import Path

import pytest

vcr = pytest.importorskip("vcr")

URL = "https://diariooficial.abc.go.gov.br/apifront/portal/edicoes/edicoes_from_data/2026-10-22.json"


def cassete(pasta: Path) -> Path:
    idx = json.loads(Path("testes/paginas/do-goias/indice.json").read_text(encoding="utf-8"))
    corpo = (Path("testes/paginas/do-goias") / idx[URL]["arquivo"]).read_text(encoding="utf-8")
    import yaml
    c = pasta / "edicoes.yaml"
    c.write_text(yaml.safe_dump({"version": 1, "interactions": [{
        "request": {"method": "GET", "uri": URL, "body": None, "headers": {}},
        "response": {"status": {"code": 200, "message": "OK"}, "headers": {"Content-Type": ["application/json; charset=UTF-8"]},
                     "body": {"string": corpo}, "http_version": "HTTP/1.1"}}]}, allow_unicode=True), encoding="utf-8")
    return c


def test_a_escada_sobre_a_resposta_real_gravada(tmp_path):
    from eldorado.motores.acesso.api import DegrauAPI
    from eldorado.motores.acesso.escada import Escada
    with vcr.use_cassette(str(cassete(tmp_path)), record_mode="none", match_on=["method", "uri"]):
        r = Escada([DegrauAPI()], intervalo_padrao=0, tentativas=1).buscar(URL)
    d = json.loads(r.conteudo)
    assert d["itens"][0]["id"] == 7417 and d["itens"][0]["paginas"] == 57 and r.degrau.startswith("1 · API")
