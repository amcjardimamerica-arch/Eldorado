"""C-08 da manutenção de 23/11 (pendente em 25/11, P-03) — R61, as decisões da titular de 18/11/2026 sobre o cadastro das
financiadoras: (1) atuação em Goiás só a DECLARADA em projeto ou programa (filial, fábrica, loja e ICMS não contam);
(2) a empresa fica no estado da SEDE e a atuação por estado é filtro próprio, por projeto; (3) a nota é da empresa, pelo
CNPJ da MATRIZ; (4) fundos e ONGs ficam no cadastro com o tipo Fundação ou Fundo; (5) as pessoas físicas saem;
(6) empresa nova só com uma condição de entrada; (7) indicadores de empresas não entram na Sala como operação."""
from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

import pytest
from conftest import AGORA, ev

from eldorado.base.especial import pesquisa_empresas as P

PASTA = Path("verificacao/empresas")


def _empresa(cnpj, nome="Empresa X", uf="SP"):
    return ev("empresa.registrada", cnpj=cnpj, razao_social=nome, uf=uf, descoberta_por="importacao", descoberta_em=AGORA, atualizada_em=AGORA)


def test_unidade_ou_icms_em_goias_nao_e_atuacao_declarada():
    so_filial = {"atuacao_goias": "COMPROVADA — filial ativa em Trindade/GO (BrasilAPI)", "projetos_em_goias": "não encontrado",
                 "unidades_em_goias": "Trindade"}
    so_icms = {"atuacao_goias": "COMPROVADA — contribuinte de ICMS em Goiás", "projetos_em_goias": "Goyazes: não consta como empresa incentivadora"}
    com_projeto = {"atuacao_goias": "COMPROVADA", "projetos_em_goias": "Programa Goyazes 2025 (1 projeto) — Festival X"}
    for campos in (so_filial, so_icms):
        d = P.atuacao_declarada(campos)
        assert not any(x["uf"] == "GO" for x in d)
        assert P.atuacao_goias(campos, d).startswith("SEM ATUAÇÃO DECLARADA")
    d = P.atuacao_declarada(com_projeto, "https://goias.gov.br")
    assert d[0]["uf"] == "GO" and d[0]["ano"] == 2025 and P.atuacao_goias(com_projeto, d).startswith("COMPROVADA")
    assert P.pontos({"atuacao_goias": P.atuacao_goias(so_filial, [])}, 0) < P.pontos({"atuacao_goias": P.atuacao_goias(com_projeto, d)}, 0)


def test_a_empresa_fica_no_estado_da_sede_e_a_nota_e_da_matriz():
    sit = "ATIVA; matriz 03380763000101 (São Paulo/SP) e filial 03380763001507 (Trindade/GO)"
    assert P.sede_uf({"situacao_cadastral": sit}, "GO") == "SP"
    assert P.sede_uf({"situacao_cadastral": "Correção: UF do cadastro 'BR' deve ser RJ."}, "BR") == "RJ"
    assert P.matriz("03380763001507") == "03380763000101" and P.matriz("07.358.761/0004-01") == "07358761000169"


def test_fundos_e_fundacoes_ficam_no_cadastro_com_o_tipo():
    assert P.tipo_da("Fundação Odebrecht", {}) == "Fundação" and P.tipo_da("Instituto Cosan", {}) == "Fundação"
    assert P.tipo_da("Fundo Brasil de Direitos Humanos", {}) == "Fundo" and P.tipo_da("Gerdau Aços Longos S.A.", {}) == "Empresa"


def test_pessoa_fisica_nao_fica_no_cadastro_de_empresas(bancos, diario, gravador):
    """R61 (5) com a R35 (titular, 25/11/2026: exclusão lógica): a pessoa física sai de tudo o que lê o cadastro, a linha fica."""
    from eldorado.base.especial.ativas import ativas
    gravador.aplicar([_empresa("E0:123", "Fulano de Tal", "GO"), _empresa("12345678000195", "Empresa Y", "GO")])
    con = bancos["biblioteca"]
    assert P.retirar_pessoas_fisicas(con, diario, AGORA) == 1
    r = gravador.aplicar([e for e in diario.eventos() if e.tipo == "empresa.retirada"])
    assert not r.recusados
    ativas_ = [c for (c,) in con.execute(f"SELECT cnpj FROM empresa WHERE {ativas(con)}")]
    assert ativas_ == ["12345678000195"]
    assert con.execute("SELECT excluida_em FROM empresa WHERE cnpj = 'E0:123'").fetchone()[0]          # a linha fica (R35)
    assert P.retirar_pessoas_fisicas(con, diario, AGORA) == 0                                             # uma vez só
    # só a pessoa física: o evento com CNPJ é recusado, e a empresa nunca se apaga
    r = gravador.aplicar([ev("empresa.retirada", cnpj="12345678000195", motivo="x", em=AGORA)])
    assert r.recusados
    with pytest.raises(sqlite3.IntegrityError, match="empresa não se apaga"):
        con.execute("DELETE FROM empresa WHERE cnpj = 'E0:123'")
    # nenhum leitor do cadastro esquece o filtro
    for arq in ("eldorado/base/painel/dados.py", "eldorado/base/painel/ranking.py", "eldorado/base/painel/legado.py",
                "eldorado/base/cerebro/pilotos.py", "eldorado/base/cartorio/vinculo_empresa.py", "eldorado/motores/pilotos/interceptador.py",
                "eldorado/base/especial/pesquisa_empresas.py"):
        assert "ativas" in Path(arq).read_text(encoding="utf-8"), arq


def test_registro_sem_cnpj_fica_a_identificar_e_empresa_nova_so_com_condicao(tmp_path, bancos, diario, gravador):
    gravador.aplicar([_empresa("11222333000181", "Já Cadastrada")])
    pac = {"pesquisa": "teste", "empresas": [
        {"cnpjs": [], "razao_no_sistema": "Sem CNPJ Ltda", "campos": {}},
        {"cnpjs": ["99888777000100"], "razao_no_sistema": "Pequena Ltda", "campos": {"situacao_cadastral": "ATIVA"}},
        {"cnpjs": ["55444333000299"], "razao_no_sistema": "Grande S.A.", "campos": {"situacao_cadastral": "ATIVA; lucro real; 2.300 empregados",
                                                                                    "projetos_em_goias": "não encontrado"}},
        {"cnpjs": ["11222333000505"], "razao_no_sistema": "Filial da Já Cadastrada", "campos": {}}]}
    arq = tmp_path / "pesquisa-x.json"
    arq.write_text(json.dumps(pac), encoding="utf-8")
    r = P.importar_arquivo(arq, bancos["biblioteca"], diario, AGORA)
    assert r["a_identificar"] == 2 and r["novas_no_cadastro"] == 1 and r["empresas"] == 2
    novas = [e.dados for e in diario.eventos() if e.tipo == "empresa.registrada"]
    assert [x["cnpj"] for x in novas] == [P.matriz("55444333000299")]          # a chave é a matriz, nunca «nome:…»
    perfis = [e.dados["cnpj"] for e in diario.eventos() if e.tipo == "empresa.perfil"]
    assert "11222333000181" in perfis                                             # a filial ligou à matriz cadastrada
    assert not any(str(c).startswith("nome:") for c in perfis)
    rel = gravador.aplicar(diario.eventos())
    assert not rel.recusados, rel.recusados
    assert bancos["biblioteca"].execute("SELECT COUNT(*) FROM empresa_a_identificar").fetchone()[0] == 2


def test_o_importador_para_quando_quase_toda_a_pesquisa_seria_nova(tmp_path, bancos, diario, gravador):
    """Critério de aceite 2 da C-08: «se vierem 825, parar: o importador não reconheceu o cadastro»."""
    gravador.aplicar([_empresa(f"{i:08d}000100") for i in range(1001)])
    pac = {"pesquisa": "teste", "empresas": [{"cnpjs": [f"9{i:07d}000100"], "razao_no_sistema": f"X{i}", "campos": {}} for i in range(10)]}
    arq = tmp_path / "pesquisa-y.json"
    arq.write_text(json.dumps(pac), encoding="utf-8")
    r = P.importar_arquivo(arq, bancos["biblioteca"], diario, AGORA)
    assert r.get("parado") and not [e for e in diario.eventos() if e.tipo.startswith("empresa.")]


def test_a_pesquisa_ja_importada_nao_chega_marcada_como_importada():
    """Os três arquivos de 18/11 chegaram dentro de importados/, com os relatórios de um ensaio: a produção os pulava."""
    # 26/11/2026: depois que a produção importa pela R61, o relatório dela está no repositório (e a trava, que só aceitava
    # a ausência, derrubou o portão). O que se protege é o mesmo: nenhum relatório de ENSAIO antigo marcando a pesquisa como
    # importada — se houver relatório, é o da importação pela R61 (com a atuação declarada separada da unidade em Goiás)
    import json
    pesquisas = sorted(PASTA.glob("pesquisa-*.json"))
    assert len(pesquisas) == 3
    for arq in pesquisas:
        rel = PASTA / "importados" / (arq.stem + "-relatorio.json")
        if rel.exists():
            r = json.loads(rel.read_text(encoding="utf-8"))
            assert "goias_declarada" in r and "goias_so_unidade" in r, f"{rel.name} não é da importação pela R61"


def test_indicadores_de_empresas_nao_entram_na_sala_como_operacao():
    s = Path("eldorado/base/painel/sala.py").read_text(encoding="utf-8")
    instrumentos = re.findall(r'I\("([a-z_0-9]+)"', s)
    assert instrumentos and not [i for i in instrumentos if "empresa" in i or i.startswith(("em_", "rk_"))]


def test_as_sete_decisoes_estao_no_registro():
    reg = {r["id"]: r for r in json.loads(Path("config/regras_titular.json").read_text(encoding="utf-8"))["regras"]}
    r61 = reg["R61"]
    assert r61["data"] == "2026-11-18" and "pessoa" in r61["regra"].lower() and "matriz" in r61["regra"].lower()
