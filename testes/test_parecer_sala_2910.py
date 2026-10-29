"""29/10/2026 (titular): o parecer da Sala de Controle. A gravação sem cópia do repositório (nada era gravado desde 28/10
15:18), o diário em partes, a eficiência por item, o próximo passo, a linha do tempo, a cor dos fluxos, a medição por
evidência, a matriz de dispensas no Interceptador e a comparação R01."""

import json
import subprocess
import tempfile
from pathlib import Path

from eldorado.base.nucleo import eventos as EV


def test_a_gravacao_sem_copia_do_repositorio_e_sem_arquivo_acima_do_limite():
    g = Path("scripts/gravar.sh").read_text(encoding="utf-8")
    assert "git worktree add" not in g and "git commit-tree" in g and "git read-tree" in g
    assert "LIMITE=$((95 * 1024 * 1024))" in g and "::error::gravação" in g
    with tempfile.TemporaryDirectory() as d:
        run = lambda *a, cwd=d: subprocess.run(list(a), cwd=cwd, capture_output=True, text=True, check=False)  # noqa: E731
        run("git", "init", "-q", "--bare", "-b", "main", "remoto.git")
        run("git", "clone", "-q", "remoto.git", "semente")
        s = Path(d, "semente")
        for k, v in (("user.email", "a@b"), ("user.name", "a")):
            run("git", "config", k, v, cwd=s)
        run("git", "checkout", "-q", "-b", "main", cwd=s)
        (s / "eventos/2026/10/28").mkdir(parents=True)
        (s / "eventos/2026/10/28/velho.jsonl").write_text("{}\n")
        (s / "codigo.py").write_text("codigo\n")
        run("git", "add", "-A", cwd=s)
        run("git", "commit", "-qm", "base", cwd=s)
        run("git", "push", "-q", "origin", "main", cwd=s)
        run("git", "clone", "-q", "--depth", "1", f"file://{d}/remoto.git", "ciclo")
        c = Path(d, "ciclo")
        (c / ".inicio_ciclo").write_text("")
        import os
        import time

        time.sleep(1)
        (c / "eventos/2026/10/29").mkdir(parents=True)
        (c / "eventos/2026/10/29/passagem.jsonl").write_text('{"tipo":"execucao.iniciada"}\n{"tipo":"execucao.concluida"}\n')
        (c / "eventos/2026/10/29/metade.jsonl").write_text('{"tipo":"execucao.iniciada"}\n')
        with open(c / "eventos/2026/10/29/enorme.jsonl", "wb") as f:
            f.truncate(96 * 1024 * 1024)
        (c / "codigo.py").write_text("mudado\n")
        r = subprocess.run(
            ["bash", str(Path("scripts/gravar.sh").resolve()), "false"],
            cwd=c,
            capture_output=True,
            text=True,
            env={**os.environ, "GITHUB_TOKEN": ""},
            check=False,
        )
        assert r.returncode == 0, r.stdout + r.stderr
        assert "::error::gravação: arquivo acima de 95 MB" in r.stdout
        run("git", "clone", "-q", "remoto.git", "conferir")
        k = Path(d, "conferir")
        assert (k / "eventos/2026/10/29/passagem.jsonl").exists() and not (k / "eventos/2026/10/29/metade.jsonl").exists()
        assert not (k / "eventos/2026/10/29/enorme.jsonl").exists() and (k / "codigo.py").read_text() == "codigo\n"


def test_o_diario_se_divide_em_partes():
    antes = EV.PARTE_MAX
    try:
        EV.PARTE_MAX = 400
        with tempfile.TemporaryDirectory() as d:
            di = EV.Diario(d, "espiao")
            for i in range(5):
                di.emitir("alarme.fechado", "t", {"id": f"a{i}", "em": "2026-10-29T00:00:00+00:00", "motivo": "x" * 40})
            assert len(list(Path(d).rglob("espiao*.jsonl"))) > 1
            assert len(EV.Diario(d, "espiao").eventos()) == 5 and sum(1 for _ in EV.ler(d)) == 5
    finally:
        EV.PARTE_MAX = antes


def test_a_sala_le_os_campos_certos():
    p = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    s = Path("eldorado/base/painel/sala.py").read_text(encoding="utf-8")
    assert '"cartorio_itens": _eficiencia_itens(bib, AB)' in s and '"proximo_passo": _proximo_passo(bib, AB)' in s
    assert '"comparacao_r01": _comparacao_r01(cer, agora)' in s and "motores = _motores_com_luz(mods, cer, agora)" in s
    assert "const R=D.rede_entregou||{}" in p and "const q=t.quando||t.em, nm=t.nome||t.evento" in p
    assert 'f.situacao==="completed"?f.conclusao:(f.ultima_conclusao||null)' in p
    assert "motores.acesso.escada" not in s  # a publicação do painel instala só o básico (o tenacity quebrava o site)


def test_a_medicao_por_evidencia():
    from eldorado.base.cerebro.medicao import Medicao

    m = Medicao.do_arquivo("config/arquivos.json")
    r = m.calcular([], 0, {"scripts/gravar.sh": (False, "última gravação: FALHOU"), "config/comparacao.toml": (True, "ok")})
    assert r["arquivos"]["scripts/gravar.sh"]["ponto"] == "r" and r["arquivos"]["config/comparacao.toml"]["ponto"] == "v"


def test_a_matriz_de_dispensas_no_interceptador():
    from eldorado.motores.pilotos import interceptador as IN

    assert IN.regime_de("Edital em fluxo contínuo de credenciamento", None) == "fluxo_continuo"
    assert IN.regime_de("Emenda parlamentar 2026", None) == "emenda_parlamentar"
    assert IN.regime_de("Edital 20/2026 da Secult-GO", None) == "chamamento_publico"
    assert "Prazo de inscrição" in IN._dispensaveis("fluxo_continuo") and not IN._dispensaveis("chamamento_publico")


def test_a_comparacao_r01_le_o_arquivo():
    import sqlite3
    from datetime import datetime, timezone

    from eldorado.base.painel.sala import _comparacao_r01

    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE execucao_motor (motor TEXT, inicio TEXT, achados INTEGER)")
    c.executemany(
        "INSERT INTO execucao_motor VALUES (?,?,?)", [("pncp", "2026-10-22T21:00:00+00:00", 30), ("pncp-api", "2026-10-25T10:00:00+00:00", 10)]
    )
    r = _comparacao_r01(c, datetime(2026, 10, 29, tzinfo=timezone.utc))
    assert r["dias"] == 14 and r["motores"]["pncp-api"]["situacao"] == "pior"
    assert json.dumps(r)


def test_a_escada_aprende_e_lembra_pelo_codigo_canonico():
    """29/10/2026: a escada não registrava o degrau (a tabela dominio vazia, o degrau máximo em branco em 357 execuções):
    grava o código canônico do degrau que funcionou e outra escada (outra lista) começa por ele."""
    from eldorado.motores.acesso.escada import Bloqueado, Escada, Resposta

    html = ("<html><body>" + "<p>Edital de chamamento público com inscrições abertas para organizações.</p>" * 30 + "</body></html>").encode()

    class D:
        pesado = False

        def __init__(self, nome, abre):
            self.nome, self.abre, self.usos = nome, abre, 0

        def buscar(self, url, tempo_limite=30):
            self.usos += 1
            if not self.abre:
                raise Bloqueado("bloqueado")
            return Resposta(url=url, status=200, conteudo=html, tipo="text/html")

    with tempfile.TemporaryDirectory() as d:
        di = EV.Diario(d, "t")
        e1 = Escada(
            [D("1 · API", False), D("4 · Patchright", False), D("5 · Camoufox", True)],
            diario=di,
            intervalo_padrao=0,
            tentativas=1,
            dormir=lambda s: None,
        )
        e1.buscar("https://site.gov.br/a")
        ev = [x for x in EV.ler(d) if x.tipo == "dominio.aprendido"]
        assert ev and ev[0].dados["degrau_que_funciona"] == 5 and e1.degrau_maximo() == 5
        outra = [D("2 · leve", False), D("5 · Camoufox", True)]
        e2 = Escada(outra, intervalo_padrao=0, tentativas=1, dormir=lambda s: None)
        assert e2.semear({"site.gov.br": 5}) == 1
        e2.buscar("https://site.gov.br/b")
        assert outra[0].usos == 0 and outra[1].usos == 1
    r = Path("eldorado/base/cerebro/regencia.py").read_text(encoding="utf-8")
    assert "motor.escada.semear(ler_aprendido(" in r and '"degrau_maximo": esc_.degrau_maximo()' in r
    assert "diario=contexto.diario, dados=dados" in Path("eldorado/base/cerebro/encaminhamento.py").read_text(encoding="utf-8")


def test_as_vagas_pela_media_do_minuto(monkeypatch):
    """29/10/2026: a ociosidade pela média do último minuto (a amostra de 0,3 s pegava os picos do Espião e zerava a
    contagem: o Interceptador ficava com 1 vaga, com o processador entre 0% e 26%); a IA do Interceptador com 150 s."""
    from eldorado.base.cerebro import governador as G
    from eldorado.base.comandante import pilotos as P

    def simular(padrao, passos=110):
        P._amostras.clear()
        P._ocio["desde"] = None
        seq = iter(padrao * 100)
        monkeypatch.setattr(G, "cpu_sem_ia", lambda *a: next(seq))
        t = [5000.0]
        monkeypatch.setattr(P.time, "monotonic", lambda: t[0])
        out = []
        for _ in range(passos):
            out.append(P.vagas_por_ociosidade())
            t[0] += 10
        return out

    r = simular([0.1, 0.23, 0.02, 0.26, 0.0, 0.9])  # a produção: um pico do Espião por minuto
    assert 3 in r and r[-1] == 5
    assert set(simular([0.7, 0.8, 0.6, 0.9, 0.75, 0.65])) == {1}
    P._amostras.clear()  # não deixa amostras do relógio simulado para os outros testes
    P._ocio["desde"] = None
    assert "tempo_limite=150.0" in Path("eldorado/base/cerebro/pilotos_permanentes.py").read_text(encoding="utf-8")


def test_o_diario_de_nome_fixo_vai_para_o_dia():
    """29/10/2026: o diário de nome fixo (só escreve) vai para o arquivo do dia e troca na virada; o de execução e a
    importação (que relêem) seguem num arquivo só."""
    import datetime as dt

    with tempfile.TemporaryDirectory() as d:
        velho = Path(d, "2026", "10", "25")
        velho.mkdir(parents=True)
        (velho / "espiao.jsonl").write_text("")
        di = EV.Diario(d, "espiao")
        hoje = dt.datetime.now(dt.timezone.utc).date()
        assert di.arquivo == Path(d, f"{hoje:%Y}", f"{hoje:%m}", f"{hoje:%d}", "espiao.jsonl")
        di._dia = hoje - dt.timedelta(days=1)
        di.emitir("alarme.fechado", "t", {"id": "a", "em": "2026-10-29T00:00:00+00:00", "motivo": "x"})
        assert di._dia == hoje
        assert not EV.Diario(d, "01793146543196472744-003468-6eaf31ee").por_dia and not EV.Diario(d, "importacao-eldorado0").por_dia


def test_os_achados_orfaos_voltam_a_decisao():
    """29/10/2026 (titular: todos os dados de livros devem ser gravados nos livros): o achado do piloto gravado e sem
    decisão (a passagem interrompida levou a decisão: 334 pendentes desde 24/10) volta à Pertinência; aceito, segue ao
    Cartório (o nó validar), que o liga ao livro."""
    import sqlite3
    import tomllib

    from eldorado.base.cerebro.pertinencia import pendentes_sem_decisao

    with tempfile.TemporaryDirectory() as d:
        c = sqlite3.connect(Path(d, "biblioteca.db"))
        c.execute(
            "CREATE TABLE achado (id TEXT, motor TEXT, encontrado_em TEXT, link_divulgacao TEXT, link_oficial TEXT, titulo TEXT, "
            "publicado_em TEXT, dados TEXT, veio_de_copia_arquivada INTEGER, pista INTEGER, decisao TEXT)"
        )
        c.executemany(
            "INSERT INTO achado VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            [
                (
                    "interceptador-L-1-1",
                    "interceptador",
                    "2026-10-27",
                    "https://x.gov.br/a",
                    None,
                    "Edital 1",
                    None,
                    '{"livro_id": "L-1"}',
                    0,
                    0,
                    "pendente",
                ),
                ("espiao-2", "espiao", "2026-10-28", "https://y.org/b", None, "Edital 2", None, "{}", 0, 0, "aceito"),
            ],
        )
        c.commit()
        c.close()
        r = pendentes_sem_decisao(Path(d), 10)
        assert [x["id"] for x in r] == ["interceptador-L-1-1"] and r[0]["dados"]["livro_id"] == "L-1"
    w = tomllib.loads(Path("workflows/passagem.toml").read_text(encoding="utf-8"))
    no = next(n for n in w["no"] if n["id"] == "decidir_rede")
    assert no["parametros"].get("recuperar_pendentes") == 150
    assert any(c["de"] == "decidir_rede" and c["para"] == "validar" for c in w["conexao"])


def test_o_espiao_da_a_vez_ao_interceptador():
    """29/10/2026 (titular: a opção 2): com livros na fila do Interceptador, o Espião espaça as missões (30 s entre elas)."""
    from eldorado.base.cerebro import pilotos_permanentes as PP

    s = Path("eldorado/base/cerebro/pilotos_permanentes.py").read_text(encoding="utf-8")
    assert PP.ESPACO_ESPIAO_S == 30 and "INTERCEPTADOR_COM_FILA.set()" in s and "INTERCEPTADOR_COM_FILA.clear()" in s
    i = s.index("def voar_espiao(")
    assert "if INTERCEPTADOR_COM_FILA.is_set():" in s[i:] and "parar.wait(ESPACO_ESPIAO_S)" in s[i:]
