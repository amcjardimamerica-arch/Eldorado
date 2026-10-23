"""Os motores reais da Fase 7, cada um com o próprio arquivo de configuração, contra respostas no formato de cada API."""
import io
import json
import re
import zipfile
from datetime import date, timedelta
from pathlib import Path

import pytest
from servidor_local import criar_servidor

from eldorado.motores.canal.motor import MotorCanal

CONFIG = Path("eldorado/motores/canal/config")
HOJE = date.today()
FUTURO = (HOJE + timedelta(days=30)).isoformat()


def dou_html():
    materias = [
        {"artType": "Aviso", "title": "EDITAL DE CHAMAMENTO PÚBLICO Nº 3/2026", "urlTitle": "edital-de-chamamento-3-2026", "pubDate": "22/10/2026",
         "content": "seleção de organizações da sociedade civil para termo de fomento", "hierarchyStr": "Ministério da Cultura/Secretaria", "pubName": "DO3"},
        {"artType": "Extrato de Contrato", "title": "EXTRATO DE CONTRATO Nº 10/2026", "urlTitle": "extrato-10", "pubDate": "22/10/2026",
         "content": "contratação de serviços para organizações da sociedade civil", "hierarchyStr": "Ministério X", "pubName": "DO3"},
        {"artType": "Aviso de Licitação", "title": "PREGÃO ELETRÔNICO Nº 5/2026", "urlTitle": "pregao-5", "pubDate": "22/10/2026",
         "content": "aquisição de materiais", "hierarchyStr": "Ministério Y", "pubName": "DO3"},
        {"artType": "Edital", "title": "EDITAL Nº 4/2026 — PRÊMIO CULTURA VIVA", "urlTitle": "premio-cultura-viva", "pubDate": "22/10/2026",
         "content": "premiação de pontos de cultura; o prêmio não se submete à lei de licitação", "hierarchyStr": "Ministério da Cultura", "pubName": "DO3"},
        {"artType": "Portaria", "title": "PORTARIA Nº 1", "urlTitle": "portaria-1", "pubDate": "22/10/2026", "content": "nomeia servidor", "hierarchyStr": "Ministério Z",
         "pubName": "DO1"}]
    return (f'<html><body><script id="_br_com_seatecnologia_in_buscadou_BuscaDouPortlet_params" type="application/json">{{"jsonArray":[]}}</script>'
            f'<script id="params" type="application/json">{json.dumps({"jsonArray": materias}, ensure_ascii=False)}</script></body></html>').encode()


def pncp(pagina):
    item = lambda n: {"orgaoEntidade": {"cnpj": "01409580000138", "razaoSocial": "SECRETARIA DE ESTADO DA CULTURA"}, "anoCompra": 2026, "sequencialCompra": n,  # noqa: E731
                      "objetoCompra": f"Credenciamento de organizações da sociedade civil para projetos culturais {n}", "dataPublicacaoPncp": "2026-10-20T10:00:00",
                      "dataEncerramentoProposta": f"{FUTURO}T23:59:00", "unidadeOrgao": {"ufSigla": "GO", "municipioNome": "Goiânia"}, "modalidadeNome": "Credenciamento"}
    ruido = dict(item(90 + pagina), objetoCompra="CREDENCIAMENTO PARA A PRESTAÇÃO DE SERVIÇO DE TRANSPORTE ESCOLAR")
    return json.dumps({"data": [item(pagina), ruido], "totalPaginas": 2}).encode()


def siconv_zip():
    linhas = ["COD_PROGRAMA;NOME_PROGRAMA;DESC_ORGAO_SUP_PROGRAMA;SIT_PROGRAMA;DT_PROG_INI_RECEB_PROP;DT_PROG_FIM_RECEB_PROP;NATUREZA_JURIDICA_PROGRAMA;UF_PROGRAMA",
              f"111;Fortalecimento de OSC;Ministério das Mulheres;DISPONIBILIZADO;2026-10-01;{FUTURO};Entidades Privadas Sem Fins Lucrativos;GO",
              f"222;Obras municipais;Ministério das Cidades;DISPONIBILIZADO;2026-10-01;{FUTURO};Administração Pública Municipal;GO",
              "333;Programa encerrado;Ministério X;DISPONIBILIZADO;2026-01-01;2026-02-01;Entidades Privadas Sem Fins Lucrativos;GO"]
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("siconv_programa.csv", "\n".join(linhas).encode("latin-1"))
    return b.getvalue()


ROTAS = {
    "/leiturajornal": (200, dou_html(), "text/html; charset=utf-8"),
    "/web/dou/-/edital-de-chamamento-3-2026": (200, ("<html><body><div class='texto-dou'>" + "O Ministério da Cultura torna público o chamamento. " * 6
                                                     + "</div></body></html>").encode(), "text/html"),
    "/api/consulta/v1/contratacoes/proposta": (200, None, "application/json"),
    "/api/opportunity/find": (200, json.dumps([{"id": 999, "name": "Vaga para arte-educador(a) em oficinas", "registrationTo": {"date": f"{FUTURO} 23:59:00.000000"}},
                                               {"id": 4321, "name": "Edital de Fomento à Cultura Viva 2026", "shortDescription": "pontos de cultura",
                                                "registrationFrom": {"date": "2026-10-01 00:00:00.000000"}, "registrationTo": {"date": f"{FUTURO} 23:59:00.000000"}}]).encode(),
                              "application/json"),
    "/cultura/wp-json/wp/v2/posts": (200, json.dumps([{"title": {"rendered": "Secult abre edital de chamamento para festivais &#8211; 2026"}, "link": "{base}/cultura/edital-festivais",
                                                       "date": "2026-10-20T10:00:00", "excerpt": {"rendered": "<p>inscrições abertas</p>"}},
                                                      {"title": {"rendered": "EDITAL PREGÃO ELETRÔNICO Nº 05/2026"}, "link": "{base}/cultura/pregao", "date": "2026-10-19T10:00:00"},
                                                      {"title": {"rendered": "Resultado final do edital de 2025"}, "link": "{base}/cultura/resultado", "date": "2026-10-19T10:00:00"}]).encode(),
                                     "application/json"),
    "/social/wp-json/wp/v2/posts": (200, b"[]", "application/json"),
    "/cultura/edital-festivais": (200, ("<html><body>" + "Edital de chamamento para festivais culturais em Goiás. " * 6 + "</body></html>").encode(), "text/html"),
    "/api/gazettes": (200, json.dumps({"total_gazettes": 1, "gazettes": [{"territory_name": "Goiânia", "state_code": "GO", "date": "2026-10-20",
                                                                     "url": "https://qd/goiania-2026-10-20.pdf",
                                                                     "excerpts": ["EDITAL DE CHAMAMENTO PÚBLICO para organizações da sociedade civil — Secretaria Municipal de Cultura"]}]}).encode(),
                  "application/json"),
    "/downloads/dadosgov/siconv_programa.zip": (200, siconv_zip(), "application/zip"),
}


@pytest.fixture(scope="module")
def api():
    paginas = {"n": 0}

    def pncp_resp():
        paginas["n"] += 1
        return pncp(paginas["n"])
    rotas = dict(ROTAS)
    rotas["/api/consulta/v1/contratacoes/proposta"] = (200, pncp_resp, "application/json")
    srv, estado = criar_servidor(rotas)
    base = f"http://127.0.0.1:{estado.porta}"
    for k, (st, corpo, tipo) in list(rotas.items()):
        if isinstance(corpo, bytes):
            rotas[k] = (st, corpo.replace(b"{base}", base.encode()), tipo)
    yield base, paginas, rotas
    srv.shutdown()


def motor(nome, base, tmp_path):
    texto = (CONFIG / f"{nome}.toml").read_text(encoding="utf-8")
    texto = re.sub(r"https://(?:www\.in\.gov\.br|pncp\.gov\.br|mapa\.cultura\.gov\.br|goias\.gov\.br|queridodiario\.ok\.org\.br|api-publica\.transferegov\.gestao\.gov\.br)",
                   base, texto)
    texto = texto.replace('intervalo_s = 1.0', 'intervalo_s = 0')
    (tmp_path / f"{nome}.toml").write_text(texto + ("\n" if "[acesso]" in texto else ""), encoding="utf-8")
    m = MotorCanal(tmp_path / f"{nome}.toml", dados=tmp_path / "motores", ponte=tmp_path / "ponte")
    m.escada.intervalo_padrao = 0
    return m


def test_dou_le_o_bloco_certo_e_filtra_como_o_eldorado0(api, tmp_path):
    base, _, _ = api
    achados = list(motor("dou", base, tmp_path).buscar(None))
    assert [a.titulo for a in achados] == ["Aviso — EDITAL DE CHAMAMENTO PÚBLICO Nº 3/2026", "Edital — EDITAL Nº 4/2026 — PRÊMIO CULTURA VIVA"]
    # extrato e pregão vetados pelo título; a portaria não tem termo; o prêmio passa (o veto não olha o resumo)
    a = achados[0]
    assert a.link_oficial == f"{base}/web/dou/-/edital-de-chamamento-3-2026" and a.dados["orgao"] == "Ministério da Cultura/Secretaria"
    assert a.documento and "torna público o chamamento" in a.documento["paginas"][0]                   # a íntegra lida como documento


def test_pncp_pagina_e_traz_os_dados_de_cada_item(api, tmp_path):
    base, paginas, _ = api
    paginas["n"] = 0
    achados = list(motor("pncp-api", base, tmp_path).buscar(None))
    assert paginas["n"] == 8                                                                     # 4 modalidades × 2 páginas
    assert len(achados) == 8 and not any("TRANSPORTE ESCOLAR" in a.titulo for a in achados)      # sem sinal de OSC: barrado
    a = achados[0]
    assert "/app/editais/01409580000138/2026/" in a.link_oficial
    assert (a.dados["uf"], a.dados["municipio"], a.dados["fim"][:10], a.dados["orgao"]) == ("GO", "Goiânia", FUTURO, "SECRETARIA DE ESTADO DA CULTURA")


def test_mapa_da_cultura(api, tmp_path):
    base, _, _ = api
    achados = list(motor("plataforma-mapas-culturais", base, tmp_path).buscar(None))
    assert len(achados) == 1                                                                     # a vaga de arte-educador foi vetada
    a = achados[0]
    assert a.link_oficial.endswith("/oportunidade/4321") and a.dados["fim"].startswith(FUTURO) and a.dados["resumo"] == "pontos de cultura"


def test_wordpress_de_goias(api, tmp_path):
    base, _, _ = api
    achados = list(motor("estaduais-go-gov", base, tmp_path).buscar(None))
    assert [a.titulo for a in achados] == ["Secult abre edital de chamamento para festivais – 2026"]    # pregão e resultado vetados; HTML decodificado
    assert achados[0].dados["uf"] == "GO" and "festivais culturais" in achados[0].documento["paginas"][0]


def test_querido_diario(api, tmp_path):
    base, _, _ = api
    a = list(motor("novo-diarios-municipais-go", base, tmp_path).buscar(None))[0]
    assert (a.dados["municipio"], a.dados["uf"], a.dados["nivel"]) == ("Goiânia", "GO", "municipal") and "CHAMAMENTO" in a.titulo and a.documento is None


def test_transferegov(api, tmp_path):
    base, _, _ = api
    achados = list(motor("site-transferegov", base, tmp_path).buscar(None))
    assert [a.titulo for a in achados] == ["Fortalecimento de OSC (programa 111)"]                     # público e encerrado ficaram de fora
    assert (achados[0].dados["fim"], achados[0].dados["orgao"], achados[0].dados["uf"]) == (FUTURO, "Ministério das Mulheres", "GO")


def test_todos_os_motores_e_a_agenda():
    from eldorado.base.fluxo.agenda import carregar
    from eldorado.base.nucleo.registro import carregar as registro
    ids = registro("config/modulos.toml").ids()
    assert sorted(ids) == sorted(p.stem for p in CONFIG.glob("*.toml"))
    assert sorted(r.modulo for r in carregar("config/agenda.toml").regras) == sorted(ids)


def test_acionar_todos_os_motores_a_mao(tmp_path, diario):
    from datetime import datetime, timezone

    from eldorado.base.cerebro.governador import Governador, Leitura
    from eldorado.base.cerebro.regencia import Regencia
    from eldorado.base.fluxo.agenda import carregar
    from eldorado.base.nucleo.registro import carregar as registro
    reg = registro("config/modulos.toml")
    r = Regencia(carregar("config/agenda.toml"), Governador(lambda: Leitura(0.1, 0.1, 0.3)), reg, diario)
    madrugada = datetime(2026, 10, 23, 5, 0, tzinfo=timezone.utc)                     # 02:00 em Brasília: ninguém na agenda
    assert r.planejar(madrugada)["motores"] == []
    plano = r.planejar(madrugada, forcar=True)
    assert sorted(m["modulo"] for m in plano["motores"]) == sorted(reg.ids()) and plano["motores"][0]["motivo"] == "acionado à mão"
