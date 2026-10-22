"""A auditoria de cada livro (validação individual e decupagem) e a migração do esquema da Biblioteca (1 → 2)."""
import sqlite3
from datetime import date

from conftest import AGORA, ev

from eldorado.banco.biblioteca import esquema as bib
from eldorado.base.cartorio.auditoria import aplicar, auditar, conferir_certidao, territorio
from eldorado.base.nucleo.eventos import ler

HOJE = date(2026, 10, 22)


def livro(i, titulo, uf=None, orgao=None, link=None):
    return ev("livro.criado", id=i, missao="oportunidades", chave=f"k-{i}", titulo=titulo, uf=uf, orgao=orgao, link_oficial=link, estrela="ouro",
              selo_livro="sem", informacoes_validadas=0, situacao="em trabalho", criado_em=AGORA, atualizado_em=AGORA)


def certidao(livro_id, item, valor):
    return ev("certidao.gravada", livro_id=livro_id, item=item, valor=valor, fase="eldorado0", situacao="comprovado", em=AGORA)


def test_migracao_do_esquema_da_versao_1_a_atual_sem_perder_dados(tmp_path):
    p = tmp_path / "b.db"
    con = sqlite3.connect(p)
    con.executescript(bib.DDL)
    con.execute("PRAGMA user_version=1")
    con.execute("INSERT INTO livro(id, missao, chave, titulo, estrela, selo_livro, informacoes_validadas, situacao, criado_em, atualizado_em) "
                "VALUES ('L1','oportunidades','k','t','sem','sem',0,'em trabalho','x','x')")
    con.commit()
    con.close()
    c = bib.abrir(p)
    assert c.execute("PRAGMA user_version").fetchone()[0] == bib.VERSAO == 3 and c.execute("SELECT COUNT(*) FROM livro").fetchone()[0] == 1
    assert c.execute("SELECT COUNT(*) FROM sqlite_master WHERE name IN ('livro_dados','expurgo_externo')").fetchone()[0] == 2


def test_territorio():
    T = lambda **k: territorio(k, {})[0]  # noqa: E731
    assert T(titulo="Edital de cultura", orgao="Prefeitura de Anápolis", uf="GO") == "municipal_go"
    assert T(titulo="Edital de fomento", orgao="Secretaria de Estado da Cultura", uf="GO") == "estadual_go"
    assert T(titulo="Chamamento — Prefeitura Municipal de Curitiba", orgao="Prefeitura de Curitiba", uf="PR") == "capital_outro_estado"
    assert T(titulo="Edital — Prefeitura de Campinas", orgao="Prefeitura de Campinas", uf="SP") == "municipal_fora_go"
    assert T(titulo="Edital do Governo de Minas", orgao="Secretaria de Estado", uf="MG") == "estadual_outro_estado"
    assert T(titulo="Programa nacional", uf="BR") == "nacional" and T(titulo="Global fund", uf="IN") == "internacional"
    assert T(titulo="Edital X", link_oficial="https://cultura.go.gov.br/e") == "estadual_go"                       # pelo endereço do site
    assert T(titulo="Edital Y", link_oficial="https://www.gov.br/cultura/e") == "nacional"
    assert T(titulo="Edital Z") == "indeterminado"


def test_conferencia_de_cada_certidao():
    assert conferir_certidao("Prazo de inscrição", "até 20/08/2026") is None
    assert conferir_certidao("Prazo de inscrição", "fluxo contínuo, sem prazo de encerramento") is None
    assert conferir_certidao("Prazo de inscrição", "a definir") == "não tem data"
    assert conferir_certidao("Resultado", "30 (trinta) dias após a inscrição") is None
    assert conferir_certidao("Resultado", "00.0.00") == "não tem data nem prazo"
    assert conferir_certidao("Valor", "R$ 25.105,28") is None and conferir_certidao("Valor", "US$ 5.000 a 20.000/ano") is None
    assert conferir_certidao("Valor", "Sem repasse financeiro: cessão não onerosa") is None
    assert conferir_certidao("Valor", "R$ 20").startswith("valor implausível")
    assert conferir_certidao("Esfera", "privada (organização não governamental)") is None and conferir_certidao("Esfera", "xyz") == "esfera não reconhecida"


def test_auditoria_expurga_mantem_historico_contesta_e_decupa(gravador, bancos, diario, tmp_path):
    assert gravador.aplicar([
        livro("ok", "Edital de fomento cultural para organizações da sociedade civil", "GO", "Secretaria de Estado da Cultura", "https://cultura.go.gov.br/e"),
        livro("fora", "Edital de cultura — Prefeitura de Campinas", "SP", "Prefeitura de Campinas"),
        livro("extrato", "Ministério do Esporte — EXTRATO DE TERMO DE FOMENTO — execução do projeto", "BR", "Ministério do Esporte"),
        livro("antigo", "Lei Paulo Gustavo — Edital nº 12/2023 — cultura", "GO", "Secretaria de Estado da Cultura"),
        livro("semtit", "semtit"),
        certidao("ok", "Prazo de inscrição", "22.10.2026 a 30.11.2026"), certidao("ok", "Valor", "R$ 100 mil a R$ 800 mil"),
        certidao("ok", "Resultado", "00.0.00"), certidao("ok", "Esfera", "estadual"), certidao("ok", "Objeto", "fomento a projetos culturais"),
        certidao("ok", "Território", "Estado de Goiás"),
    ]).ok
    res = {r.livro: r for r in auditar(bancos["biblioteca"], HOJE)}
    assert res["ok"].validacao == "aprovado" and res["ok"].abrangencia == "estadual_go"
    assert res["fora"].validacao == "expurgado" and res["extrato"].validacao == "expurgado"
    assert res["antigo"].validacao == "aprovado" and res["antigo"].dados["situacao_prazo"] == "encerrada"        # histórico do programa
    assert res["semtit"].validacao == "revisar"
    d = res["ok"].dados
    assert (d["inscricao_inicio"], d["inscricao_fim"], d["situacao_prazo"], d["valor_min"], d["valor_max"], d["esfera"]) == (
        "2026-10-22", "2026-11-30", "aberta", 100000.0, 800000.0, "estadual")
    assert res["ok"].contestadas and res["ok"].contestadas[0].startswith("Resultado")
    aplicar(list(res.values()), diario)
    assert gravador.aplicar(list(ler(tmp_path / "eventos"))).ok
    b = bancos["biblioteca"]
    assert {r[0] for r in b.execute("SELECT id FROM livro WHERE situacao='excluido'")} == {"fora", "extrato"}
    assert b.execute("SELECT justificativa_exclusao FROM livro WHERE id='fora'").fetchone()[0].startswith("validação de 22/10/2026")
    assert b.execute("SELECT situacao FROM certidao WHERE item='Resultado'").fetchone()[0] == "contestado"
    assert b.execute("SELECT COUNT(*) FROM livro_dados").fetchone()[0] == 5
    assert b.execute("SELECT estrela FROM livro WHERE id='ok'").fetchone()[0] == "bronze"                             # recalculada sem a contestada


def test_so_os_livros_novos_ou_alterados_sao_auditados(gravador, bancos, diario, tmp_path):
    from eldorado.base.cartorio.auditoria import pendentes
    assert gravador.aplicar([livro("a", "Edital de fomento cultural para organizações da sociedade civil", "GO", "Secretaria de Estado da Cultura"),
                             livro("b", "Chamamento público para organizações da sociedade civil", "GO", "Secretaria de Estado da Cultura")]).ok
    assert pendentes(bancos["biblioteca"]) == {"a", "b"}
    aplicar(list(auditar(bancos["biblioteca"], HOJE)), diario)
    assert gravador.aplicar(list(ler(tmp_path / "eventos"))).ok
    assert pendentes(bancos["biblioteca"]) == set()
    assert gravador.aplicar([ev("livro.situacao", id="a", situacao="em trabalho", atualizado_em="2999-01-01T00:00:00+00:00")]).ok
    assert pendentes(bancos["biblioteca"]) == {"a"}                                                  # alterado depois da validação
