"""A reanálise da Sala (11/11/2026): o que o pacote de 10/11 deixou com problema ou piorou, e as correções.

  1. a leitura tolerante do mapa do site ficou SEM TETO: o índice de www.in.gov.br tem 370 mapas internos — o DOU ficou preso
     além do orçamento da coleta em todas as passagens, o nó «acionar» foi de 12 s para 28 min e a passagem de 6 para 32 min;
  2. com as passagens longas, a execução passou das 6 h do GitHub, foi cancelada e a continuação não foi acionada: o sistema
     parou;
  3. a Sala medida pela produção chegava ao site com 15 a 25 min: o Painel reaplicava o histórico inteiro (10 min) a cada
     publicação;
  4. o motor preso virava também «adiado pelo governador», com o motivo errado, e cada porcentagem contava como uma causa."""
import json
import re
from pathlib import Path

import yaml
from conftest import livro


class _R:
    def __init__(self, conteudo):
        self.conteudo = conteudo


def _indice(n, com_data=False):
    itens = b"".join(b"<sitemap><loc>https://x.br/s%d.xml</loc>%s</sitemap>" % (i, (b"<lastmod>2026-%02d-01</lastmod>" % (1 + i % 12)) if com_data else b"")
                     for i in range(n))
    return b'<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + itens + b"</sitemapindex>"


# ------------------------------------------------------------------------------------------------ 1. o teto do mapa do site
def test_o_mapa_do_site_tem_teto():
    from eldorado.motores.descoberta.estrutura_site import MAPAS_INTERNOS, ORCAMENTO_MAPA_S, mapa_do_site

    pedidos = []

    def buscar(u):
        pedidos.append(u)
        return _R(_indice(370) if u.endswith("sitemap.xml") else b"<urlset><url><loc>https://x.br/p/%d</loc></url></urlset>" % len(pedidos))

    pistas = mapa_do_site(buscar, "https://x.br/sitemap.xml")
    assert len(pedidos) == 1 + MAPAS_INTERNOS <= 9 and len(pistas) == MAPAS_INTERNOS           # o índice de 370 mapas: 8 abertos
    # o orçamento de tempo: cada busca leva 25 s → para depois de passar de 60 s
    pedidos.clear()
    relogio = {"t": 0.0}

    def lento(u):
        relogio["t"] += 25
        return buscar(u)

    mapa_do_site(lento, "https://x.br/sitemap.xml", relogio=lambda: relogio["t"])
    assert len(pedidos) <= 1 + 3 and ORCAMENTO_MAPA_S <= 60
    # os mapas internos de modificação mais recente primeiro
    pedidos.clear()
    mapa_do_site(lambda u: (pedidos.append(u), _R(_indice(24, True) if u.endswith("sitemap.xml") else b"<urlset></urlset>"))[1], "https://x.br/sitemap.xml",
                 mapas_internos=2)
    assert pedidos[1:] == ["https://x.br/s11.xml", "https://x.br/s23.xml"]                     # os dois de dezembro
    # duas falhas seguidas encerram a leitura (não sobe a escada 370 vezes)
    pedidos.clear()

    def falha(u):
        pedidos.append(u)
        if u.endswith("sitemap.xml"):
            return _R(_indice(50))
        raise OSError("bloqueado")

    assert mapa_do_site(falha, "https://x.br/sitemap.xml") == [] and len(pedidos) == 3


# ------------------------------------------------------------------------------------------------ 2. o ciclo nunca chega às 6 h
def test_o_ciclo_para_antes_do_limite_do_github():
    from eldorado.base.nucleo.comandos import cabe_outra_passagem

    assert cabe_outra_passagem(0, [], 100)                                                    # sem histórico, segue
    assert not cabe_outra_passagem(0, [1800, 1900], 600)                                      # não cabe no que resta do laço
    # a execução #381: 327 min de laço + 17 de instalação = 344 min; a passagem seguinte (32 min) não cabia
    assert not cabe_outra_passagem(344 * 60, [1900], 6000, 345, 25, inicio_job_s=0)
    assert not cabe_outra_passagem(300 * 60, [1900], 6000, 345, 25, inicio_job_s=0)           # 300 + 32 + 25 > 345
    assert cabe_outra_passagem(280 * 60, [1900], 6000, 345, 25, inicio_job_s=0)               # 280 + 32 + 25 <= 345
    e = yaml.safe_load(Path(".github/workflows/eldorado.yml").read_text(encoding="utf-8"))
    passos = e["jobs"]["passagem"]["steps"]
    nomes = [p.get("name", "") for p in passos]
    i_perm = next(i for i, n in enumerate(nomes) if n.startswith("Funcionamento permanente"))
    i_cont = [i for i, n in enumerate(nomes) if n.startswith("Continuar")]
    assert i_cont == [i_perm + 1]                                                             # a continuação logo depois do laço, uma só
    assert "cancelled" in passos[i_cont[0]]["if"] and "eldorado.yml/dispatches" in passos[i_cont[0]]["run"]
    assert all(i_cont[0] < i for i, n in enumerate(nomes) if n.startswith(("A manutenção", "Gravar no repositório", "A cópia")))
    assert "ELDORADO_INICIO_JOB" in passos[0]["run"]
    m = re.search(r"--limite-min (\d+) .*--limite-job-min (\d+) --reserva-final-min (\d+)", passos[i_perm]["run"])
    assert m and int(m.group(1)) <= 300 and int(m.group(2)) <= 345 and int(m.group(3)) >= 20   # o GitHub cancela aos 360 min
    c = Path("eldorado/base/nucleo/comandos.py").read_text(encoding="utf-8")
    assert "cabe_outra_passagem(time.time(), duracoes" in c


# ------------------------------------------------------------------------------------------------ 3. só os eventos novos
def test_a_reaplicacao_pula_os_arquivos_ja_aplicados(bancos, tmp_path):
    from eldorado.base.nucleo.eventos import Diario, MarcaAplicados, ler
    from eldorado.base.nucleo.gravador import Gravador

    pasta = tmp_path / "ev"
    d1 = Diario(pasta, "um")
    d1.emitir("livro.criado", "t", livro(id="L1", chave="k1").dados)

    def aplicar():
        m = MarcaAplicados(tmp_path, bancos)
        r = Gravador(bancos).aplicar(ler(pasta, pular=m.ja, origem=m.origem, lidos=m.lidos))
        m.gravar(r.recusados)
        return r, m

    r, m = aplicar()
    assert r.aplicados == 1 and m.pulados == 0 and (tmp_path / "aplicados.json").exists()
    r, m = aplicar()
    assert r.aplicados == 0 and r.repetidos == 0 and m.pulados == 1 and not m.lidos           # nada relido
    d1.emitir("livro.criado", "t", livro(id="L2", chave="k2").dados)                           # o arquivo cresceu: é relido
    r, m = aplicar()
    assert r.aplicados == 1 and r.repetidos == 1
    # o arquivo com evento recusado não é marcado (é relido na próxima vez)
    Diario(pasta, "dois").emitir("livro.criado", "t", livro(id="L3", chave="k1").dados)        # a chave repetida: recusado
    r, m = aplicar()
    assert len(r.recusados) == 1
    marcados = json.loads((tmp_path / "aplicados.json").read_text())["arquivos"]
    assert len(marcados) == 1 and not any("dois" in a for a in marcados)
    # a marca só vale junto do banco em que foi feita: com outro banco (vazio), tudo é reaplicado
    from eldorado.banco.biblioteca import esquema as bib
    from eldorado.banco.cerebro_db import esquema as cer
    (tmp_path / "outro").mkdir()
    b2 = bib.abrir(tmp_path / "outro" / "biblioteca.db")
    novos = {"biblioteca": b2, "especial": b2, "cerebro": cer.abrir(tmp_path / "outro" / "cerebro.db")}
    try:
        m2 = MarcaAplicados(tmp_path, novos)
        assert m2.ja == {}
    finally:
        for c in {id(x): x for x in novos.values()}.values():
            c.close()


def test_o_painel_guarda_os_bancos_entre_as_publicacoes(tmp_path):
    import os
    import subprocess

    texto = Path(".github/workflows/painel.yml").read_text(encoding="utf-8")
    p = yaml.safe_load(texto)
    passos = p["jobs"]["publicar"]["steps"]
    usa = lambda prefixo: next(s for s in passos if str(s.get("uses", "")).startswith(prefixo))   # noqa: E731
    repoe, guarda = usa("actions/cache/restore@"), usa("actions/cache/save@")
    for s in (repoe, guarda):
        assert all(a in s["with"]["path"] for a in ("dados/biblioteca.db", "dados/cerebro.db", "dados/aplicados.json"))
        # a chave muda com QUALQUER mudança do código e a cada semana (aí remonta do zero, como antes)
        assert "hashFiles('eldorado/**/*.py')" in s["with"]["key"] and "semana" in s["with"]["key"] and "github.run_id" in s["with"]["key"]
    i = {n: passos.index(s) for n, s in (("repoe", repoe), ("guarda", guarda))}
    i_vereditos = next(k for k, s in enumerate(passos) if "eldorado vereditos" in str(s.get("run", "")))
    i_aplicar = next(k for k, s in enumerate(passos) if str(s.get("run", "")).startswith("eldorado aplicar"))
    i_site = next(k for k, s in enumerate(passos) if "eldorado site" in str(s.get("run", "")))
    assert i["repoe"] < i_vereditos < i_aplicar < i["guarda"] < i_site                  # guarda logo depois de aplicar, antes do site
    assert re.search(r"eldorado aplicar \|\|", texto) and "wal_checkpoint" in texto
    assert guarda["if"] == "steps.guarda.outputs.renovar == 'true'" and guarda.get("continue-on-error") is True
    assert "MarcaAplicados(dados, bancos)" in Path("eldorado/base/nucleo/comandos.py").read_text(encoding="utf-8")
    assert "dados/aplicados.json" in Path(".gitignore").read_text(encoding="utf-8")     # a marca nunca vai ao repositório
    # a decisão de renovar a guarda: a cada 30 min, e nunca com um veredito que o ciclo ainda não importou
    decide = next(s for s in passos if s.get("id") == "guarda")["run"]
    from datetime import datetime, timedelta, timezone

    def renovar(idade_min, pendente):
        raiz = tmp_path / f"r{idade_min}{pendente}"
        (raiz / "dados").mkdir(parents=True)
        (raiz / "verificacao/vereditos/importados").mkdir(parents=True)
        (raiz / "verificacao/vereditos/importados/velho.json").write_text("{}")
        if idade_min is not None:
            em = (datetime.now(timezone.utc) - timedelta(minutes=idade_min)).isoformat()
            (raiz / "dados/aplicados.json").write_text(json.dumps({"em": em}))
        if pendente:
            (raiz / "verificacao/vereditos/novo.json").write_text("{}")
        saida = raiz / "saida"
        subprocess.run(["bash", "-c", decide], cwd=raiz, env={**os.environ, "GITHUB_OUTPUT": str(saida)}, check=True)
        return saida.read_text().strip()

    assert renovar(None, False) == "renovar=true"                                       # sem a guarda: guarda a primeira
    assert renovar(5, False) == "renovar=false" and renovar(45, False) == "renovar=true"
    assert renovar(45, True) == "renovar=false"                                         # o veredito só desta publicação não entra


# ------------------------------------------------------------------------------------------------ 4. a Sala no site em 15 min
def test_a_sala_e_enviada_logo_depois_de_medida_e_avisa_quando_religa(tmp_path):
    from eldorado.base.painel import vivo

    c = Path("eldorado/base/nucleo/comandos.py").read_text(encoding="utf-8")
    bloco = c[c.index("def sala_viva()"):c.index("threading.Thread(target=sala_viva")]
    assert bloco.index("medir_e_gravar(") < bloco.index("gravar_agora()")                     # mede e envia na hora
    assert "marcar_religando(" in c and c.index("marcar_religando(Path") < c.index("gravar_agora(esperar=True)  # tudo o que terminou")
    (tmp_path / "painel_vivo").mkdir()
    (tmp_path / "painel_vivo/sala_controle.json").write_text(json.dumps({"em": "2026-11-11T08:40:31+00:00", "fonte": {"origem": "produção",
                                                                          "medido_em": "2026-11-11T08:40:31+00:00"}}))
    assert vivo.marcar_religando(tmp_path, "troca de ciclo")
    f = json.loads((tmp_path / "painel_vivo/sala_controle.json").read_text())["fonte"]
    assert f["origem"] == "produção" and f["religando_desde"] and f["religando_motivo"] == "troca de ciclo" and f["religando_espera_min"] == 45
    assert not vivo.marcar_religando(tmp_path / "nada")
    pagina = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    assert "A produção está religando" in pagina and "A produção está PARADA" in pagina and "religando_desde" in pagina


# ------------------------------------------------------------------------------------------------ 5. os alarmes do motor preso
def test_o_motor_preso_nao_vira_adiado_e_a_causa_e_uma_so():
    from eldorado.base.painel.sala import _causa

    a = "motor adiado pelo governador: carga 46% (processador 1%, memória 46%): a memória sem folga até 85%"
    b = "motor adiado pelo governador: carga 57% (processador 17%, memória 57%): a memória sem folga até 85%"
    assert _causa(a) == _causa(b) and _causa(a) != _causa("motor(es) preso(s) além do orçamento da coleta")
    s = Path("eldorado/base/painel/sala.py").read_text(encoding="utf-8")
    assert "_al = len({_causa(msg_ or m_) for m_, msg_ in _linhas_al})" in s and "chave = _causa(msg or mod)" in s   # a mesma chave
    r = Path("eldorado/base/cerebro/regencia.py").read_text(encoding="utf-8")
    assert 'if m in getattr(r, "presos", set()):\n                continue' in r and "self.presos = " in r


# ------------------------------------------------------------------------------------------------ 6. o domínio pendente
def test_o_dominio_pendente_nao_sobe_a_escada_a_cada_fonte(tmp_path, monkeypatch):
    """Em 10/11 o motor das prefeituras gastou 9,2 h em acionamentos de 20 min que não leram nenhuma fonte: cada fonte de
    Luziânia (o site só abre no Brasil) subia a escada inteira (~7 min) para terminar pendente no computador da titular."""
    import pytest

    from eldorado.base.nucleo.eventos import Diario, ler
    from eldorado.motores.acesso.escada import RESUBIR_PENDENTE_H, Bloqueado, Escada, Pendente, Resposta, ler_pendentes

    monkeypatch.delenv("ELDORADO_FORCAR", raising=False)

    class D:
        pesado = False

        def __init__(self, nome, faz):
            self.nome, self.faz, self.chamado = nome, faz, 0

        def buscar(self, url, tempo_limite):
            self.chamado += 1
            return self.faz(url)

    def bloq(u):
        raise Bloqueado("403")

    resposta = {}

    def computador(u):
        if u in resposta:
            return Resposta(u, 200, resposta[u], "text/html")
        raise Pendente("pedido entregue ao computador local (x)")

    api, ponte, local = D("1 · api", bloq), D("P · ponte BR (HostGator)", bloq), D("9 · computador da titular", computador)
    diario = Diario(tmp_path / "ev", "t")
    hora = {"t": 1_800_000_000.0}
    e = Escada([api, ponte, local], diario=diario, intervalo_padrao=0)
    e.relogio = lambda: hora["t"]
    with pytest.raises(Pendente) as x:                                   # a primeira fonte do domínio: a escada inteira
        e.buscar("https://acesso.luziania.go.gov.br/a")
    assert "antes:" in str(x.value) and api.chamado == 1 and ponte.chamado == 1 and local.chamado == 1
    hora["t"] += 60
    with pytest.raises(Pendente) as x:                                   # a segunda: direto ao computador da titular
        e.buscar("https://acesso.luziania.go.gov.br/b")
    assert "já entregue" in str(x.value) and api.chamado == 1 and ponte.chamado == 1 and local.chamado == 2
    assert len([v for v in ler(tmp_path / "ev") if v.tipo == "dominio.aprendido"]) == 1     # a hora da subida não é renovada
    with pytest.raises(Pendente):                                        # outro domínio sobe a escada normalmente
        e.buscar("https://outro.go.gov.br/a")
    assert api.chamado == 2
    with pytest.raises(Bloqueado):                                       # o formulário (POST) não usa o atalho
        e.buscar("https://acesso.luziania.go.gov.br/c", corpo={"q": "x"})
    monkeypatch.setenv("ELDORADO_FORCAR", "1")                           # o acionamento à mão da titular sobe sempre
    with pytest.raises(Pendente) as x:
        e.buscar("https://acesso.luziania.go.gov.br/a")
    assert "antes:" in str(x.value) and api.chamado == 3
    monkeypatch.delenv("ELDORADO_FORCAR")
    hora["t"] += RESUBIR_PENDENTE_H * 3600 + 1                           # passado o prazo, a escada inteira de novo
    antes = api.chamado
    with pytest.raises(Pendente) as x:
        e.buscar("https://acesso.luziania.go.gov.br/a")
    assert "antes:" in str(x.value) and api.chamado == antes + 1 and RESUBIR_PENDENTE_H <= 12
    # a resposta do computador da titular chegou: é lida pelo atalho e o domínio deixa de ser pendente
    resposta["https://acesso.luziania.go.gov.br/a"] = b"<html><body>" + b"<p>Edital de chamamento publico com inscricoes abertas.</p>" * 30 + b"</body></html>"
    r = e.buscar("https://acesso.luziania.go.gov.br/a")
    assert r.degrau.startswith("9 ·") and api.chamado == antes + 1 and "acesso.luziania.go.gov.br" not in e.pendente_desde
    # a memória vem do Cérebro (a tabela dominio): outra escada, noutro acionamento, não sobe de novo
    from eldorado.banco.cerebro_db import esquema as cer

    (tmp_path / "dados").mkdir()
    c = cer.abrir(tmp_path / "dados" / "cerebro.db")
    c.execute("INSERT INTO dominio (dominio, degrau_que_funciona, bloqueios, exige_local, ultimo_bloqueio) VALUES "
              "('pendente.go.gov.br', NULL, 2, 1, '2026-11-11T08:29:32+00:00'), ('aberto.go.gov.br', 2, 0, 0, NULL)")
    c.commit()
    c.close()
    memoria = ler_pendentes(tmp_path / "dados")
    assert set(memoria) == {"pendente.go.gov.br"}
    api2, local2 = D("1 · api", bloq), D("9 · computador da titular", computador)
    e2 = Escada([api2, local2], intervalo_padrao=0)
    e2.relogio = lambda: memoria["pendente.go.gov.br"] + 3600
    assert e2.semear_pendentes(memoria) == 1
    with pytest.raises(Pendente):
        e2.buscar("https://pendente.go.gov.br/x")
    assert api2.chamado == 0 and local2.chamado == 1
    assert "semear_pendentes(ler_pendentes(" in Path("eldorado/base/cerebro/regencia.py").read_text(encoding="utf-8")
