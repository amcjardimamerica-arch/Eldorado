"""O motor-gife e a base Especial: as empresas e os incentivos, das páginas reais gravadas (23/10/2026)."""
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

import pytest
from conftest import AGORA, ev

from eldorado.base.especial.registro import Registro, cnpj_valido, resolver_cnpj
from eldorado.base.nucleo.eventos import ler
from eldorado.motores.canal.motor import MotorCanal

PASTA = Path("testes/paginas/motor-gife")
INDICE = json.loads((PASTA / "indice.json").read_text(encoding="utf-8"))
PAGINA = PASTA / next(x["arquivo"] for u, x in INDICE.items() if u.endswith("os-maiores-contribuintes-do-icms/") and x.get("arquivo"))
PDF = PASTA / next(x["arquivo"] for u, x in INDICE.items() if u.endswith("2025_CPF_Anon.pdf") and x.get("arquivo"))
SALIC = PASTA / next(x["arquivo"] for u, x in INDICE.items() if "juridica" in u and "offset=0" in u and x.get("arquivo"))


@pytest.fixture(scope="module")
def fontes():
    base = {}

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            u = urlsplit(self.path)
            if u.path.endswith("os-maiores-contribuintes-do-icms/"):
                corpo, tipo = PAGINA.read_bytes().replace(b"https://goias.gov.br", base["url"].encode()), "text/html"
            elif u.path.endswith("2025_CPF_Anon.pdf"):
                corpo, tipo = PDF.read_bytes(), "application/pdf"
            elif "incentivadores" in u.path and "offset=0" in u.query:
                corpo, tipo = SALIC.read_bytes(), "application/json"
            else:
                corpo, tipo = None, None
            self.send_response(200 if corpo else 404)
            self.send_header("Content-Type", tipo or "text/plain")
            self.end_headers()
            self.wfile.write(corpo or b"")
    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    base["url"] = f"http://127.0.0.1:{srv.server_address[1]}"
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield base["url"]
    srv.shutdown()


def achados(base, tmp_path):
    texto = Path("eldorado/motores/canal/config/motor-gife.toml").read_text(encoding="utf-8")
    texto = texto.replace("https://goias.gov.br", base).replace("https://api.salic.cultura.gov.br", base)
    texto = texto.replace('degraus = ["api", "leve", "local"]', 'degraus = ["api"]').replace('degraus = ["api", "leve"]', 'degraus = ["api"]')
    (tmp_path / "g.toml").write_text(texto, encoding="utf-8")
    m = MotorCanal(tmp_path / "g.toml", dados=tmp_path / "motores", ponte=tmp_path / "p")
    m.escada.intervalo_padrao = 0
    return list(m.buscar(None))


def test_cnpj():
    assert cnpj_valido("00080671000100") and cnpj_valido("33000167000101") and not cnpj_valido("00080671000199") and not cnpj_valido("11111111111111")
    assert resolver_cnpj(None, "1234") == (None, "sem CNPJ")


def test_empresas_e_incentivos_na_base_especial(fontes, tmp_path, gravador, bancos, diario):
    lista = achados(fontes, tmp_path)
    assert len(lista) >= 590 and all(a.dados.get("especial") for a in lista)                    # 499 do ICMS e 100 do Salic
    assert gravador.aplicar([ev("empresa.registrada", cnpj="33000167000101", razao_social="PETROLEO BRASILEIRO S A PETROBRAS", uf="BR",
                                descoberta_por="importacao", descoberta_em=AGORA, atualizada_em=AGORA)]).ok
    reg = Registro(bancos["especial"], diario)
    r = [reg.registrar(a.dados["especial"], "motor-gife", a.dados["fonte"]) for a in lista]
    assert gravador.aplicar(list(ler(tmp_path / "eventos"))).ok
    e = bancos["especial"]
    assert e.execute("SELECT COUNT(*) FROM empresa").fetchone()[0] >= 550
    assert [tuple(x) for x in e.execute("SELECT lei, ano FROM incentivo WHERE cnpj = '33000167000101'")] == [("ICMS", 2025)]      # raiz casada
    assert e.execute("SELECT valor FROM incentivo WHERE cnpj = '00080671000100' AND lei LIKE 'Rouanet%'").fetchone()[0] == 820000.0     # Caramuru
    assert sum(1 for x in r if x["registrado"]) >= 590
    antes = e.execute("SELECT COUNT(*) FROM incentivo").fetchone()[0]
    for a in lista[:50]:
        reg.registrar(a.dados["especial"], "motor-gife", a.dados["fonte"])
    assert gravador.aplicar(list(ler(tmp_path / "eventos"))).ok
    assert e.execute("SELECT COUNT(*) FROM incentivo").fetchone()[0] == antes                     # a mesma fonte não duplica
    assert reg.registrar({"cnpj": "***169471**", "tipo_pessoa": "fisica"}, "m", "f")["registrado"] is False


def test_a_regencia_desvia_para_a_base_especial(diario, tmp_path):
    from eldorado.base.cerebro.governador import Governador, Leitura
    from eldorado.base.cerebro.regencia import Regencia
    from eldorado.base.fluxo.agenda import Agenda
    from eldorado.base.nucleo.contratos import Achado
    from eldorado.base.nucleo.registro import Registro as Modulos

    class M:
        def descrever(self):
            from eldorado.base.nucleo.contratos import Descricao
            return Descricao(id="motor-gife", nome="g", tipo="motor", versao="1")

        def buscar(self, plano):
            yield Achado(id="g1", motor="motor-gife", encontrado_em="2026-10-23", link_divulgacao="https://x", titulo="CARAMURU ALIMENTOS",
                         dados={"especial": {"cnpj": "00080671000100", "razao_social": "CARAMURU ALIMENTOS", "incentivo": {"lei": "Rouanet", "valor": "1"}},
                                "fonte": "Salic"})
    mods = Modulos()
    mods._modulos = {"motor-gife": M()} if hasattr(mods, "_modulos") else None
    if mods._modulos is None:
        pytest.skip("registro de módulos sem injeção direta")
    r = Regencia(Agenda([]), Governador(lambda: Leitura(0.1, 0.1, 0.3)), mods, diario)
    lista, _ = r.acionar({"motores": [{"modulo": "motor-gife", "janela_inicio": "x", "janela_fim": "y", "motivo": "teste"}], "passagem": "p1"})
    tipos = [e.tipo for e in ler(tmp_path / "eventos")]
    assert lista == [] and "achado.entregue" not in tipos and "empresa.registrada" in tipos and "incentivo.registrado" in tipos
