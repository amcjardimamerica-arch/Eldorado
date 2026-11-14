"""R54 (titular, 14/11/2026): as correções do parecer dos motores da Bússola sem sinal verde."""
import json
import tomllib
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from eldorado.motores.acesso.escada import Pendente
from eldorado.motores.acesso.local import DegrauLocal
from eldorado.motores.descoberta import estrutura_site
from eldorado.motores.descoberta.dados_abertos import lista_js

CFG = Path("eldorado/motores/canal/config")


def _cfg(m):
    return tomllib.loads((CFG / f"{m}.toml").read_text(encoding="utf-8"))


def test_o_wordpress_com_resumo_vazio_nao_quebra_a_leitura():
    assert estrutura_site._texto({"rendered": None}) == "" and estrutura_site._texto({"rendered": "<p>ok</p>"}) == "ok"


def test_a_lista_javascript_da_pagina():
    html = """<script>const UPDATED = '2026-11-14';
    const EDITAIS = [
      // um comentário, com 'aspas' e um endereço https://x.y
      {n:'PNAB Aparecida de Goiânia, Edital 01/2026', local:'GO · Aparecida de Goiânia', prazo:'2026-12-10', link:'https://a.go.gov.br/edital?x=1', cat:['música']},
      {n:"Fundo \\"X\\"", local:'Nacional', prazo:null, link:'https://b.org/', /* outro */ },
    ];</script>"""
    L = lista_js(html, "EDITAIS")
    assert len(L) == 2 and L[0]["link"] == "https://a.go.gov.br/edital?x=1" and L[1]["n"] == 'Fundo "X"' and L[1]["prazo"] is None
    with pytest.raises(ValueError):
        lista_js(html, "NAO_EXISTE")


def test_a_resposta_do_computador_local_vence_em_24_horas(tmp_path):
    c = DegrauLocal(tmp_path)
    url = "https://www.tjgo.jus.br/noticias"
    k = c.chave(url)
    def guardar(em):
        (tmp_path / "respostas" / f"{k}.json").write_text(json.dumps({"url": url, "status": 200, "em": em.isoformat()}))
        (tmp_path / "respostas" / f"{k}.bin").write_bytes(b"<html>ok</html>")
    guardar(datetime.now(timezone.utc) - timedelta(hours=2))
    assert c.buscar(url, 10).status == 200
    guardar(datetime(2026, 10, 29, tzinfo=timezone.utc))                 # a cópia de 29/10: vencida, o pedido é refeito
    with pytest.raises(Pendente):
        c.buscar(url, 10)
    assert (tmp_path / "pedidos" / f"{k}.json").exists()


def test_os_enderecos_do_parecer():
    urls = {m: {f["url"] for f in _cfg(m)["fonte"]} for m in ("mpgo-destinacao", "prefeitura-goiania", "fundacoes-nacionais", "novo-internacional",
                                                            "judiciario-tjgo", "dj-trf1-go", "prefeituras-rm-goiania", "tcm-go")}
    assert "https://www.mpgo.mp.br/portal/noticias" in urls["mpgo-destinacao"] and "https://www.goiania.go.gov.br/procon/" in urls["prefeitura-goiania"]
    assert "https://abong.org.br/wp-sitemap.xml" in urls["fundacoes-nacionais"] and "https://echoinggreen.org/fellowship/" in urls["novo-internacional"]
    assert not {"https://www.tjgo.jus.br/files/2026/", "https://projudi.tjgo.jus.br/ConsultaPublicacao"} & urls["judiciario-tjgo"]
    assert "https://www.jfgo.jus.br/sjgo" not in urls["dj-trf1-go"] and "https://eventos.aparecida.go.gov.br/" not in urls["prefeituras-rm-goiania"]
    assert any("jfgo.jus.br" in r for r in _cfg("dj-trf1-go")["aprendizado"]["rotas_que_falharam"])      # para ninguém recolocar
    for m in ("site-radar-editais", "site-radar-editais-culturais", "site-editaisculturais-com"):
        assert not any("wp-json" in f["url"] for f in _cfg(m)["fonte"])
    novas = {m: [f for f in _cfg(m)["fonte"] if f["tipo"] == "api"] for m in ("site-agente-cultural", "site-editaisculturais-com", "site-radar-editais-culturais")}
    assert all(novas.values()) and novas["site-radar-editais-culturais"][0]["json_em"] == "js:EDITAIS"


def test_o_sesc_e_a_ponte():
    lic = [f for f in _cfg("sistema-s")["fonte"] if f["nome"] == "Sesc Goiás — licitações e chamamentos"][0]
    assert lic["lexico"]["vetos"] and "preg" in lic["lexico"]["vetos"][0]
    ponte = Path("config/ponte_dominios.txt").read_text(encoding="utf-8")
    assert all(d in ponte for d in ("sescgo.com.br", "go.senac.br", "atosoficiais.com.br", "go.equatorialenergia.com.br",
                                    "portaldoincentivo.com.br", "alcoa.com", "brasil.diplo.de"))
    assert "dados/ponte/pedidos" in Path("scripts/gravar.sh").read_text(encoding="utf-8")
