"""A escada de acesso, degrau por degrau, contra um servidor local que imita os sites reais."""
import json
import os
from pathlib import Path

import pytest
from servidor_local import criar_servidor

from eldorado.base.nucleo.eventos import ler
from eldorado.motores.acesso.api import DegrauAPI
from eldorado.motores.acesso.arquivo_web import DegrauArquivo
from eldorado.motores.acesso.escada import Bloqueado, Escada, Indisponivel, Pendente, Resposta, avaliar, ler_robots
from eldorado.motores.acesso.leve import DegrauLeve
from eldorado.motores.acesso.local import DegrauLocal
from eldorado.motores.acesso.navegador import DegrauLightpanda, DegrauNavegador
from eldorado.motores.acesso.rotas_alternativas import DegrauTor


@pytest.fixture(scope="module")
def site():
    srv, estado = criar_servidor()
    yield f"http://127.0.0.1:{estado.porta}", estado
    srv.shutdown()


def escada(degraus, **kw):
    esperas = []
    return Escada(degraus, intervalo_padrao=0, dormir=esperas.append, **kw), esperas


def test_degrau_1_api(site):
    url, _ = site
    e, _ = escada([DegrauAPI(), DegrauLeve()])
    r = e.buscar(f"{url}/api.json")
    assert json.loads(r.conteudo)["editais"][0]["titulo"] == "Edital 1" and r.degrau.startswith("1 ·")


def test_sobe_de_degrau_e_aprende_o_dominio(site, diario, tmp_path):
    url, estado = site
    e, _ = escada([DegrauAPI(), DegrauLeve()], diario=diario)
    r = e.buscar(f"{url}/so-navegador.html")
    assert r.degrau.startswith("2 ·") and any("bloqueado (status 403)" in a for a in r.alertas)
    antes = estado.acessos[("/so-navegador.html", "outro")]
    e.buscar(f"{url}/so-navegador.html")
    assert estado.acessos[("/so-navegador.html", "outro")] == antes                    # aprendido: não tentou o degrau 1 de novo
    eventos = [x for x in ler(tmp_path / "eventos") if x.tipo == "dominio.aprendido"]
    assert eventos and eventos[0].dados["degrau_que_funciona"] == 1


def test_falha_passageira_repete_no_mesmo_degrau(site):
    url, _ = site
    e, esperas = escada([DegrauAPI()], tentativas=3)
    r = e.buscar(f"{url}/instavel.html")
    assert r.status == 200 and len(esperas) >= 2                                       # duas esperas antes de dar certo


def test_fonte_fora_do_ar_vai_a_copia_arquivada(site):
    url, _ = site
    e, _ = escada([DegrauAPI(), DegrauLeve(), DegrauArquivo(base=url)], tentativas=1)
    r = e.buscar("http://127.0.0.1:9/edital.html")                                     # porta 9: ninguém responde
    assert r.copia_arquivada and b"Copia arquivada" in r.conteudo and r.degrau.startswith("6 ·")


def test_captcha_vai_ao_computador_da_titular(site, tmp_path, diario):
    url, _ = site
    local = DegrauLocal(tmp_path / "ponte")
    e, _ = escada([DegrauAPI(), DegrauLeve(), local], diario=diario)
    with pytest.raises(Pendente):
        e.buscar(f"{url}/captcha.html")
    pedidos = list((tmp_path / "ponte/pedidos").glob("*.json"))
    assert len(pedidos) == 1 and json.loads(pedidos[0].read_text())["url"] == f"{url}/captcha.html"
    k = DegrauLocal.chave(f"{url}/captcha.html")                                       # o computador local atende
    (tmp_path / f"ponte/respostas/{k}.bin").write_bytes(b"<html><body>" + b"Edital lido pelo computador local. " * 5 + b"</body></html>")
    (tmp_path / f"ponte/respostas/{k}.json").write_text(json.dumps({"status": 200, "tipo": "text/html", "em": "2026-10-22T10:00"}))
    r = e.buscar(f"{url}/captcha.html")
    assert b"computador local" in r.conteudo and r.degrau.startswith("9 ·")
    aprendido = [x.dados for x in ler(tmp_path / "eventos") if x.tipo == "dominio.aprendido"]
    assert aprendido[0]["exige_local"] == 1


def test_robots_e_so_informacao(site):
    url, _ = site
    e, esperas = escada([DegrauAPI()])
    info = ler_robots(e, f"{url}/restrito/pagina.html", lambda u: DegrauAPI().buscar(u, 5).conteudo.decode())
    assert info["espera"] == 2 and info["robots_proibiria"] is True
    e.buscar(f"{url}/restrito/pagina.html")                                            # sem trava: leu mesmo assim
    e.buscar(f"{url}/ok.html")
    assert esperas and max(esperas) > 1.5                                              # mas respeitou a espera pedida


def test_governador_segura_os_degraus_pesados(site):
    url, _ = site

    class Ocupado:
        def pode_iniciar(self, *a):
            return False
    e, _ = escada([DegrauAPI(), DegrauLightpanda(binario="/nao/existe")], governador=Ocupado())
    with pytest.raises(Bloqueado, match="adiado pelo governador"):
        e.buscar(f"{url}/captcha.html")


def test_degrau_indisponivel_e_pulado_com_aviso(site):
    url, _ = site
    e, _ = escada([DegrauNavegador("camoufox"), DegrauLightpanda(binario="/nao/existe"), DegrauAPI()])
    r = e.buscar(f"{url}/ok.html")
    assert r.degrau.startswith("1 ·") and sum("indisponivel" in a for a in r.alertas) == 2
    with pytest.raises(Indisponivel):
        DegrauTor(porta=1)


LIGHTPANDA = os.environ.get("ELDORADO_LIGHTPANDA") or ("/home/claude/fase6/lightpanda" if Path("/home/claude/fase6/lightpanda").exists() else None)


@pytest.mark.skipif(not LIGHTPANDA, reason="binário do Lightpanda ausente nesta máquina (não vai para o Git)")
def test_lightpanda_le_a_pagina_que_so_existe_com_javascript(site):
    url, _ = site
    e, _ = escada([DegrauAPI(), DegrauLightpanda(binario=LIGHTPANDA, espera_seletor='body[data-pronto="1"]')])
    r = e.buscar(f"{url}/js.html")
    assert r.degrau.startswith("3 ·") and r.conteudo.count(b"Edital de chamamento") == 50
    assert any("quase vazia" in a for a in r.alertas)                                  # o degrau 1 viu a página vazia e subiu


def test_avaliacao_das_respostas():
    ok = Resposta("u", 200, b"<html><body>" + b"texto de verdade " * 10 + b"</body></html>", "text/html")
    avaliar(ok)
    dados_em_json = b'<html><body><script id="params" type="application/json">{"jsonArray": [{"title": "Edital de chamamento"}]}</script></body></html>'
    avaliar(Resposta("u", 200, dados_em_json, "text/html"))                       # os dados embutidos são conteúdo (DOU)
    for r in (Resposta("u", 403, b"x"), Resposta("u", 429, b"x"), Resposta("u", 200, b"<html>captcha</html>"),
              Resposta("u", 503, b"<html>Just a moment...</html>"),
              Resposta("u", 200, b"<!doctype html><html><body><script>" + b"var x=1;" * 500 + b"</script></body></html>", "text/html")):
        with pytest.raises(Bloqueado):
            avaliar(r)


def test_cabecalhos_so_em_ascii():
    from eldorado.motores.acesso.api import AGENTE
    AGENTE.encode("ascii")
