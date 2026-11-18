"""18/11/2026 (titular): a pesquisa das 825 empresas financiadoras entra no sistema — o perfil, o cadastro corrigido, os
incentivos confirmados, o aprofundamento e a classificação."""
import json
import sqlite3

from eldorado.base.especial import pesquisa_empresas as P


class _D:
    def __init__(self):
        self.ev = []

    def emitir(self, tipo, origem, dados):
        self.ev.append((tipo, dados))


def _campos(**k):
    return {c: k.get(c) for c in P.CAMPOS}


def test_so_a_lei_confirmada_vira_incentivo_e_o_site_aceita_o_dominio():
    assert P._leis("Goyazes (confirmado); Rouanet pelo sistema") == ["Goyazes"]
    assert P._leis("Rouanet, Goyazes (registro do sistema; não reconfirmado no Salic)") == []
    assert P._leis("não confirmadas (sistema: Esporte, PAT)") == []
    assert P._leis("Rouanet confirmada no Salic (R$ 1.821.696,36); Lei do Esporte citada. Pronas: não verificado.") == ["Rouanet"]
    assert P._url("equatorialenergia.com.br") == "https://equatorialenergia.com.br"
    assert P._url("vitamedic.ind.br (a confirmar)") is None and P._url("não encontrado (site próprio não localizado)") is None


def test_a_importacao_corrige_o_cadastro_junta_a_mesma_empresa_e_acontece_uma_vez(tmp_path):
    c = sqlite3.connect(":memory:")
    c.executescript("CREATE TABLE empresa(cnpj TEXT, razao_social TEXT, nome_fantasia TEXT, uf TEXT, site TEXT);"
                    "CREATE TABLE incentivo(cnpj TEXT, lei TEXT); CREATE TABLE ranking(criterio TEXT, calculado_em TEXT);"
                    "INSERT INTO empresa VALUES ('39346861000161', 'CENCOSUD BRASIL COMERCIAL LTDA', 'Bretas', 'GO', NULL);"
                    "INSERT INTO incentivo VALUES ('39346861000161', 'ICMS');")
    g1 = {"pesquisa": "grupo 1", "empresas": [{"cnpjs": ["39346861000161"], "razao_conferida": "CENCOSUD BRASIL COMERCIAL LTDA",
                                                 "campos": _campos(site_oficial="cencosud.com.br", leis_confirmadas="Goyazes (confirmado)",
                                                                   atuacao_goias="COMPROVADA — lojas em Goiânia")}]}
    g3 = {"pesquisa": "grupo 3", "empresas": [{"cnpjs": ["39346861000161"], "razao_conferida": "Grupo Bretas / Cencosud",
                                                 "campos": _campos(canal_para_projeto="https://cencosud.com.br/contato", atuacao_goias="COMPROVADA")},
                                                {"cnpjs": ["12345678000199"], "razao_conferida": "Empresa Nova LTDA",
                                                 "campos": _campos(atuacao_goias="SEM ATUAÇÃO em Goiás")}]}
    pasta = tmp_path / "empresas"
    pasta.mkdir()
    (pasta / "pesquisa-g1.json").write_text(json.dumps(g1), encoding="utf-8")
    (pasta / "pesquisa-g3.json").write_text(json.dumps(g3), encoding="utf-8")
    d = _D()
    r = P.importar_pasta(c, d, pasta)
    tipos = [t for t, _ in d.ev]
    assert [x["novas_no_cadastro"] for x in r["importados"]] == [0, 1] and tipos.count("incentivo.registrado") == 1
    perfil = [x for t, x in d.ev if t == "empresa.perfil" and x["cnpj"] == "39346861000161"][-1]
    assert perfil["canal_para_projeto"] and perfil["site_oficial"] == "cencosud.com.br"            # as duas pesquisas juntas
    assert any(t == "empresa.corrigida" and x.get("site") == "https://cencosud.com.br" for t, x in d.ev)
    d2 = _D()
    assert P.importar_pasta(c, d2, pasta)["importados"] == []                                    # importado uma vez


def test_a_classificacao_poe_a_financiadora_de_goias_na_frente():
    goias = _campos(atuacao_goias="COMPROVADA", atua_em_goiania="sim", programas_proprios="Edital X", canal_para_projeto="https://x.com/c")
    fora = _campos(atuacao_goias="SEM ATUAÇÃO")
    risco = _campos(atuacao_goias="COMPROVADA", risco_ou_cuidado="recuperação judicial em 2025")
    assert P.pontos(goias, 2) > P.pontos(risco, 2) > P.pontos(fora, 0)
