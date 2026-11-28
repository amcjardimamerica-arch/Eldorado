"""Manutenção da Sala de controle (26/11/2026): o Painel que não publicava e os alarmes de causas já corrigidas que ficavam
acesos para sempre (78 na Sala, de 22 a 25/11)."""
import sqlite3
from pathlib import Path

import yaml

from eldorado.base.nucleo.eventos import criar


def _alarme(modulo, msg, em):
    return criar("alarme.aberto", "t", {"gravidade": "alta", "modulo": modulo, "mensagem": msg, "aberto_em": em})


def _abertos(c):
    return {m for (m,) in c.execute("SELECT mensagem FROM alarme WHERE fechado_em IS NULL")}


def test_a_publicacao_do_painel_espera_o_artefato_e_tenta_de_novo():
    """O deploy-pages rodava logo depois do envio e ainda não via o artefato («Found 0 artifacts»): o site pronto não
    publicava. A publicação espera o artefato aparecer na lista e, se falhar mesmo assim, tenta uma segunda vez."""
    texto = Path(".github/workflows/painel.yml").read_text(encoding="utf-8")
    job = yaml.safe_load(texto)["jobs"]["publicar"]
    passos = job["steps"]
    ids = {p.get("id"): i for i, p in enumerate(passos) if p.get("id")}
    envio = next(i for i, p in enumerate(passos) if str(p.get("uses", "")).startswith("actions/upload-pages-artifact@"))
    espera = next(i for i, p in enumerate(passos) if "/actions/runs/${{ github.run_id }}/artifacts" in str(p.get("run", "")))
    assert envio < espera < ids["publicacao"] < ids["publicacao2"]
    assert '"github-pages"' in passos[espera]["run"] and "GH_TOKEN" in passos[espera]["env"]
    assert passos[ids["publicacao"]].get("continue-on-error") is True                       # a primeira falha não encerra
    segunda = passos[ids["publicacao2"]]
    assert str(segunda["uses"]).startswith("actions/deploy-pages@") and segunda["if"] == "steps.publicacao.outcome == 'failure'"
    assert "continue-on-error" not in segunda                                                  # a segunda que falha aparece
    url = job["environment"]["url"]
    assert "steps.publicacao.outputs.page_url" in url and "steps.publicacao2.outputs.page_url" in url
    assert "actions: read" in texto                                                            # a lista de artefatos exige


def test_o_alarme_do_voo_do_espiao_fecha_quando_ele_volta_a_pousar():
    """O voo permanente do Espião que caiu em 22/11 (TypeError «metadata_errors», código que não existe mais) ficava aceso;
    fecha quando o Espião pousou de um voo depois do alarme. Sem pouso depois, segue aceso."""
    from eldorado.base.cerebro.revisao_alarmes import revisar

    c = sqlite3.connect(":memory:")
    c.executescript("CREATE TABLE execucao_passo(no TEXT, estado TEXT, em TEXT); CREATE TABLE medicao(marcador TEXT, em TEXT, motivo TEXT);"
                    "CREATE TABLE alarme(id INTEGER, modulo TEXT, mensagem TEXT, aberto_em TEXT, fechado_em TEXT);")
    c.executemany("INSERT INTO alarme VALUES (?,?,?,?,NULL)", [
        (1, "piloto:espiao", "o voo permanente do Espião falhou: TypeError: open() got an unexpected keyword argument 'metadata_errors'",
         "2026-11-22T20:28:36+00:00"),
        (2, "piloto:espiao", "o voo permanente do Espião falhou: ValueError: x", "2026-11-25T10:00:00+00:00")])
    c.executemany("INSERT INTO medicao VALUES ('piloto:espiao', ?, ?)", [
        ("2026-11-23T08:00:00+00:00", "pousou: 2 achado(s)"),
        ("2026-11-25T11:00:00+00:00", "em voo: a família x (autorizada pelo Comandante)")])   # em voo não é pouso
    assert [a for a, _ in revisar(c)] == [1]


def test_as_recusas_da_ia_pendente_de_antes_da_c04_fecham_e_as_novas_seguem_acesas(gravador, bancos):
    """As 76 recusas «tentativa fora de 1 a 3» de 23 a 25/11 são a marca do defeito «ia pendente» (C-04): o evento nunca volta
    a ser aplicado, então o alarme não fechava. Fecham as abertas antes da correção chegar à produção; uma recusa igual
    depois dela segue acesa (qualquer outra tentativa fora de 1 a 3 segue recusada com alarme)."""
    from eldorado.base.nucleo.gravador import C04_EM_PRODUCAO

    motivo = "biblioteca.tentativa: IntegrityError: CHECK constraint failed: numero BETWEEN 1 AND 3"
    antes = f"evento recusado (tentativa.registrada, 01795471329116979508-000639-bd22ab73): {motivo}"
    depois = f"evento recusado (tentativa.registrada, 01795999999999999999-000001-aaaaaaaa): {motivo}"
    outra = "evento recusado (livro.criado, y): biblioteca.livro: IntegrityError: CHECK constraint failed: situacao"
    assert gravador.aplicar([_alarme("gravador", antes, "2026-11-23T22:04:16+00:00"),
                             _alarme("gravador", outra, "2026-11-23T22:04:16+00:00"),
                             _alarme("gravador", depois, "2026-11-26T10:00:00+00:00")]).ok
    assert "2026-11-26T10:00:00+00:00" > C04_EM_PRODUCAO > "2026-11-25T18:50:31+00:00"     # a última das 76 é de antes
    abertos = _abertos(bancos["cerebro"])
    assert antes not in abertos and depois in abertos and outra in abertos


def test_expirar_a_memoria_que_ja_saiu_nao_abre_alarme(gravador, bancos):
    """A expiração pedida duas vezes (duas passagens leem a mesma fotografia) achava a linha já apagada e abria um alarme
    vermelho «linha não encontrada em memoria». O que se queria já aconteceu: é dispensada, e o alarme antigo fecha."""
    velho = ("evento recusado (memoria.expirada, 01795617371895001671-001607-689124cb): cerebro.memoria: ValueError: "
             "linha não encontrada em memoria")
    r = gravador.aplicar([_alarme("gravador", velho, "2026-11-25T14:40:14+00:00"),
                          criar("memoria.expirada", "aprendizado", {"tabela": "livro", "ref": "L-que-nao-esta-na-memoria"})])
    assert not [x for x in r.recusados if x[1] == "memoria.expirada"] and r.dispensados >= 1
    assert not [m for m in _abertos(bancos["cerebro"]) if "memoria" in m]
