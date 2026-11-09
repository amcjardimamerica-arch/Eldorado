"""08/11/2026 — ferramentas da passada completa no Chrome (estudo Claude × motores, 30 dias).

O que uma pessoa lê no item da lista e o motor não lia: o título quando o link diz "abrir/salvar", o rótulo de situação
("Inscrições abertas"/"Encerrado"), o prazo numa linha com início e fim; o JSON com aviso do PHP antes; e os registros
dentro de um campo já lido (a busca de texto completo do Diário Oficial de Goiás).
"""
from __future__ import annotations

from types import SimpleNamespace

from eldorado.motores.descoberta import cadeia, estrutura_site
from eldorado.motores.descoberta.pistas import Pista


def _buscar(html: str):
    return lambda url, *a, **k: SimpleNamespace(conteudo=html.encode("utf-8"), url=url)


def test_titulo_da_linha_quando_o_link_diz_abrir_salvar():
    html = ("<table><tr><th>Região</th><th>Data</th></tr><tr><td>GOIÂNIA</td><td>27/10/2026</td><td>094312.2026</td>"
            "<td><a href='/edital?arq=1'>abrir/salvar</a></td></tr></table>")
    p = estrutura_site.links(_buscar(html), "https://www.prt18.mpt.mp.br/servicos/editais")[0]
    assert "GOIÂNIA" in p.titulo and "094312.2026" in p.titulo
    assert p.data == "2026-10-27"


def test_titulo_do_cartao_quando_o_link_diz_saiba_mais():
    html = "<div class='card'><h3>Edital Encantando Comunidades</h3><p>Apoio a OSC</p><a href='/edital-x'>Saiba mais</a></div>"
    p = estrutura_site.links(_buscar(html), "https://www.institutolojasrenner.org.br/editais-abertos/")[0]
    assert p.titulo == "Edital Encantando Comunidades"


def test_situacao_aberta_e_encerrada_no_item():
    html = ("<ul><li><a href='/e20'>Ocupa Goiás Brasilidades</a> Inscrições abertas</li>"
            "<li><a href='/e02'>Manutenção Continuada de Grupos</a> Habilitação para Pagamento</li></ul>")
    p = estrutura_site.links(_buscar(html), "https://goias.gov.br/cultura/pnab/edital-2026-pnab/")
    assert p[0].extra.get("situacao") == "aberta"
    assert p[1].extra.get("situacao") == "encerrada"


def test_prazo_na_linha_com_inicio_e_fim():
    html = ("<table><tr><td>32/2026</td><td>06/11/2026</td><td>Chamamento Público</td><td>Cultura</td>"
            "<td>Início 06/11/2026</td><td>Fim 11/11/2026</td><td><a href='/ato/32'>Edital de chamamento</a></td></tr></table>")
    p = estrutura_site.links(_buscar(html), "https://acessoainformacao.valparaisodegoias.go.gov.br/cidadao/atos_adm/mp/id=3")[0]
    assert p.data == "2026-11-11"


def test_uma_data_so_continua_valendo():
    html = "<ul><li>03/11/2026 — <a href='/n1'>Edital de fomento</a></li></ul>"
    assert estrutura_site.links(_buscar(html), "https://x.go.gov.br/")[0].data == "2026-11-03"


def test_json_com_aviso_do_php_antes():
    lixo = b"<br />\n<b>Warning</b>: Undefined index in /var/www/x.php<br />\n[{\"id\": 1}]"
    assert estrutura_site.json_tolerante(lixo) == [{"id": 1}]
    assert estrutura_site.json_tolerante(b'{"a": 2}') == {"a": 2}


def test_cadeia_linhas_dentro_de_um_campo_ja_lido():
    corpo = (b'{"hits":{"hits":[{"_id":"7430_62","_source":{"conteudo":"Protocolo 1 AVISO DE CHAMAMENTO P\\u00daBLICO N\\u00ba01/2026 '
             b'O MUNIC\\u00cdPIO DE SANTO ANTONIO DO DESCOBERTO torna p\\u00fablico a abertura para sele\\u00e7\\u00e3o de 04 projetos '
             b'de Ponto de Cultura. Protocolo 2 AVISO DE CHAMAMENTO P\\u00daBLICO PARA CREDENCIAMENTO DE PESSOAS JUR\\u00cdDICAS"}}]}}')
    elos = [cadeia.Elo(formato="json", itens="hits.hits", campos={"id": "_id", "conteudo": "_source.conteudo"}),
            cadeia.Elo(formato="linhas", itens=r"(?i)(?P<titulo>aviso de chamamento p[uú]blico[^.]{0,160})",
                       campos={"de": "conteudo"}, filtro={"titulo": r"^(?!.*credenciamento de pessoas)"})]
    itens = cadeia.percorrer(lambda u, *a: SimpleNamespace(conteudo=corpo), "https://diariooficial.abc.go.gov.br/busca", elos)
    assert len(itens) == 1
    assert "SANTO ANTONIO DO DESCOBERTO" in itens[0]["titulo"] and itens[0]["id"] == "7430_62"
    assert "conteudo" not in itens[0]


def test_o_motor_barra_a_situacao_encerrada(tmp_path):
    from pathlib import Path

    from eldorado.motores.canal.motor import MotorCanal
    cfg = Path(__file__).resolve().parents[1] / "eldorado/motores/canal/config/estaduais-go-gov.toml"
    m = MotorCanal(cfg, dados=tmp_path / "m", ponte=tmp_path / "p")
    p = Pista(titulo="Edital PNAB nº 03/2026 Manutenção Continuada de Espaços de Cultura", link="https://goias.gov.br/cultura/e3",
              origem="links da página", extra={"situacao": "encerrada"})
    assert m._motivo_entrada(p) == "situação encerrada no item da lista"
