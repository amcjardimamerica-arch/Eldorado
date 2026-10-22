"""A migração do Eldorado0, com um Eldorado0 em miniatura nos mesmos formatos reais (pedaços achatados do acervo)."""
import json
import shutil

from typer.testing import CliRunner

from eldorado.base.fluxo.nos import abrir_bancos
from eldorado.base.migracao.importar_eldorado0 import Importador, aprendizado, conferir, lotes
from eldorado.base.nucleo.comandos import app
from eldorado.base.nucleo.gravador import Gravador


def peca(**caminhos):
    return {c: {"dado": v, "absorvido_em": "2026-10-16T00:00:00+00:00"} for c, v in caminhos.items()}


def montar(raiz):
    L = raiz / "biblioteca_alexandria/livros"
    (L / "_arquivados").mkdir(parents=True)
    (raiz / "biblioteca_alexandria/fontes").mkdir(parents=True)
    (raiz / "docs/dados").mkdir(parents=True)
    certidao = {"id": "captacao-001", "titulo": "PNAB Goiânia — Audiovisual", "uf": "GO", "orgao": "Secult Goiânia", "link_oficial": "https://goiania.go.gov.br/e.pdf",
                "documentos": [{"url": "https://goiania.go.gov.br/e.pdf", "sha1": "5811b308", "tipo": "pdf", "paginas": 36, "oficial": "sim"}],
                "itens": {"Objeto": {"valor": "fomento a projetos audiovisuais", "trecho": "tem por objeto o fomento a projetos audiovisuais", "pagina": "2",
                                     "documento": "https://goiania.go.gov.br/e.pdf"},
                          "Valor": {"valor": "R$ 300.000,00", "trecho": "Responsável: CPF 123.456.789-09; total R$ 300.000,00", "pagina": "5"},
                          "Prazo de recurso": {"status": "disp", "valor": "dispensado", "justificativa": "não se aplica: prêmio sem etapa de recurso"},
                          "Resultado": {"valor": "não informado"}}}
    parecer = {"id": "ver-captacao-001", "livro": "captacao-001", "decisao": "verificado_prata", "motivo": "11 de 12", "data": "2026-10-15"}
    (L / "captacao-001.json").write_text(json.dumps({"id": "captacao-001", "acervo": {
        "estado/cartorio/certidoes.json": peca(**{"/certidoes|livro:captacao-001": certidao}),
        "dados/oportunidades/pareceres_livros/p.json": peca(**{"/pareceres|1": parecer, "/pareceres|2": {**parecer, "id": "ver-2"}})}}))
    (L / "op-sem-catalogo.json").write_text(json.dumps({"id": "op-sem-catalogo", "acervo": {
        "dados/coleta_3_anos/fila_go.json": peca(**{"/itens|7": {"id": "op-sem-catalogo", "nome": "Emenda municipal para entidade", "orgao": "ALEGO"}})}}))
    (L / "op-duplicado.json").write_text(json.dumps({"id": "op-duplicado", "acervo": {}}))
    (L / "op-sem-titulo.json").write_text(json.dumps({"id": "op-sem-titulo", "acervo": {"x.json": peca(**{"/a": 1})}}))
    (L / "_indice.json").write_text(json.dumps({"livros": []}))
    (L / "leis.json").write_text(json.dumps({"livros": [{"id": "lei-1", "nome": "Lei 1", "esfera": "federal"}, {"id": "lei-1", "nome": "Lei 1", "esfera": "federal"}]}))
    (L / "_arquivados/op-velho.json").write_text(json.dumps({"arquivado_em": "2026-10-18T00:00:00", "motivo": "fora da abrangência",
                                                             "livro": "{'id': 'op-velho', 'programa': 'Edital antigo de Curitiba', 'orgao': 'Prefeitura', 'uf': 'PR'}"}))
    (L / "_arquivados/captacao-001.json").write_text(json.dumps({"motivo": "unido", "livro": "{'id': 'captacao-001'}"}))
    cat = {"motores": [{"id": "captacao-001", "nome_classificado": "PNAB Goiânia — Audiovisual", "orgao": "Secult Goiânia", "uf": "GO", "pagina": "https://goiania.go.gov.br/e.pdf"},
                       {"id": "op-duplicado", "programa": "PNAB Goiânia — Audiovisual", "orgao": "Secult Goiânia", "uf": "GO"},
                       {"id": "so-catalogo", "programa": "Fundo estadual do idoso", "orgao": "SEDS", "uf": "GO"}]}
    (raiz / "biblioteca_alexandria/fontes/motores.json").write_text(json.dumps(cat))
    (raiz / "docs/dados/empresas.json").write_text(json.dumps({"estados": {"GO": {"empresas": [
        {"id": "92754738000162", "nome": "Empresa A", "cnpj": None}, {"id": "n:EDITAL", "nome": "Aberta seleção de projetos", "cnpj": None}]}}}))
    (raiz / "docs/dados/incentivos_verificados.json").write_text(json.dumps({"empresas": [
        {"nome": "Empresa B", "cnpj": "07526557000100", "confirmados": ["Rouanet"], "rouanet_5_anos": {"valor": 41700.0, "anos": ["2024"]}, "pat": "inscrita"}]}))


def test_migracao_confere_mantem_o_texto_integro_e_e_idempotente(tmp_path):
    montar(tmp_path)
    b = abrir_bancos(tmp_path / "dados")
    try:
        imp = Importador(tmp_path)
        g = Gravador(b)
        r = [g.aplicar(lote) for lote in lotes(imp.eventos(), 7)]
        assert all(x.ok for x in r)
        tabela = conferir(imp, b)
        assert all(ok for *_, ok in tabela), [t for t in tabela if not t[3]]
        bib = b["biblioteca"]
        assert {x[0] for x in bib.execute("SELECT id FROM livro")} == {"captacao-001", "op-sem-catalogo", "op-duplicado", "op-sem-titulo", "so-catalogo", "op-velho"}
        assert bib.execute("SELECT titulo FROM livro WHERE id='op-sem-catalogo'").fetchone()[0] == "Emenda municipal para entidade"
        assert bib.execute("SELECT situacao, justificativa_exclusao FROM livro WHERE id='op-velho'").fetchone()[1].startswith("arquivado no Eldorado0")
        assert tuple(bib.execute("SELECT livro_que_fica, livro_unido FROM uniao").fetchone()) == ("captacao-001", "op-duplicado")    # unidos, não fundidos
        trecho = bib.execute("SELECT trecho FROM certidao WHERE item='Valor'").fetchone()[0]
        assert trecho == "Responsável: CPF 123.456.789-09; total R$ 300.000,00"                 # íntegro, como estava na fonte
        assert dict(bib.execute("SELECT item, situacao FROM certidao WHERE livro_id='captacao-001'").fetchall()) == {
            "Objeto": "comprovado", "Valor": "comprovado", "Prazo de recurso": "dispensado", "Resultado": "pendente"}              # "não informado" é falta
        assert bib.execute("SELECT informacoes_validadas FROM livro WHERE id='captacao-001'").fetchone()[0] == 3                 # o pendente não conta
        assert bib.execute("SELECT d.url FROM certidao c JOIN documento d ON d.id = c.documento_id WHERE c.item='Objeto'").fetchone()[0].endswith("/e.pdf")
        assert bib.execute("SELECT COUNT(*) FROM veredito").fetchone()[0] == 2 and b["cerebro"].execute("SELECT COUNT(*) FROM rotulo").fetchone()[0] == 1
        assert {k for k in imp.r.lacunas} >= {"livro sem título em nenhuma fonte (título = identificador)", "lei repetida no Eldorado0 (mantida uma)",
                                              "arquivado que também está ativo (mantido o ativo)", "registro sem CNPJ (não é empresa identificada: título, órgão ou associação)"}
        assert {x[0] for x in b["especial"].execute("SELECT cnpj FROM empresa")} == {"92754738000162", "07526557000100"}
        assert [tuple(x) for x in b["especial"].execute("SELECT lei, comprovado FROM incentivo ORDER BY lei")] == [("PAT", 0), ("Rouanet", 1)]
        segunda = Importador(tmp_path)
        assert sum(g.aplicar(lote).aplicados for lote in lotes(segunda.eventos(), 50)) == 0                                        # idempotente
    finally:
        for c in b.values():
            c.close()


def test_aprendizado_dos_motores(tmp_path, gravador, bancos):
    arq = tmp_path / "ap.json"
    arq.write_text(json.dumps({"motores": [{"id": "do-goias", "historico_de_erros_e_aprendizado": {"licoes_do_historico": ["21 dias verdes."],
                                                                                                   "destino_no_novo_eldorado": {"motor_novo": "do-goias"}}},
                                           {"id": "vazio"}]}))
    imp = Importador(tmp_path)
    assert gravador.aplicar(list(aprendizado(imp, arq))).ok
    assert bancos["cerebro"].execute("SELECT modulo, o_que FROM aprendizado_permanente").fetchone()[:] == ("do-goias", "21 dias verdes.")
    assert imp.r.lacunas["motor sem aprendizado registrado"] == 1


def test_comando_migrar_sai_com_sucesso_quando_tudo_confere(tmp_path):
    origem = tmp_path / "eldorado0"
    origem.mkdir()
    montar(origem)
    (tmp_path / "config").mkdir()
    shutil.copy("config/eldorado.toml", tmp_path / "config")
    r = CliRunner().invoke(app, ["migrar", str(origem), "--config", str(tmp_path / "config/eldorado.toml")])
    assert r.exit_code == 0, r.output
    assert "DIVERGE" not in r.output and "amostra campo a campo" in r.output
