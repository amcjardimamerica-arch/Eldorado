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
    """29/10/2026: a média do último minuto do processador TOTAL (com a IA) governa as vagas (a regra dos 85%); a IA do
    Interceptador com 150 s; a métrica de cada missão (os itens do checklist obtidos) e o quadro das vagas."""
    from eldorado.base.cerebro import governador as G
    from eldorado.base.cerebro.pilotos_permanentes import _itens_do_achado
    from eldorado.base.comandante import pilotos as P

    P._amostras.clear()
    P._ctrl.update(vagas=1, ultimo_ajuste=0.0)
    seq = iter([0.1, 0.9, 0.1, 0.1, 0.9, 0.1] * 50)  # picos de 90% no meio: a média do minuto (~37%) segue abaixo de 78%
    monkeypatch.setattr(G, "cpu_total", lambda *a: next(seq))
    t = [5000.0]
    monkeypatch.setattr(P.time, "monotonic", lambda: t[0])
    out = []
    for _ in range(60):
        out.append(P.vagas_por_ociosidade())
        t[0] += 20
    assert out[-1] == 8
    P._amostras.clear()
    P._ctrl.update(vagas=1, ultimo_ajuste=0.0)
    assert "tempo_limite=150.0" in Path("eldorado/base/cerebro/pilotos_permanentes.py").read_text(encoding="utf-8")
    assert _itens_do_achado({"dados": {"itens": "{'Objeto': {'valor': 'x'}, 'Valor': {'valor': 'y'}}"}}) == {"Objeto", "Valor"}
    s = Path("eldorado/base/cerebro/pilotos_permanentes.py").read_text(encoding="utf-8")
    assert '"marcador": "missao:interceptador"' in s and '"marcador": "pilotos:vagas"' in s and "PARALELOS_INTERCEPTADOR = 8" in s
    sala = Path("eldorado/base/painel/sala.py").read_text(encoding="utf-8")
    assert '"pi_missoes"' in sala and '"pi_vagas"' in sala


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


def test_o_prazo_da_ia_vale_no_pedido_validado():
    """29/10/2026: o caminho validado (pydantic-ai) ignorava o prazo do cargo e repetia o pedido (375 s registrados): o
    prazo vai ao pedido e há no máximo uma nova tentativa."""
    s = Path("eldorado/base/nucleo/ia.py").read_text(encoding="utf-8")
    assert "system_prompt=SISTEMA, retries=1)" in s and 'model_settings={"timeout": float(getattr(ia, "tempo_limite", 240.0))}' in s


def test_a_escada_nao_prende_no_pendente_e_o_local_nao_sobe():
    """29/10/2026: o "pendente" (o computador da titular) era anotado como o degrau que funciona e, com a memória
    persistente, o SearXNG e os buscadores iam para sempre à fila: o Espião voltava vazio desde as 05:00."""
    from eldorado.motores.acesso.escada import Bloqueado, Escada, Pendente, Resposta

    html = ("<html><body>" + "<p>Resultado de busca com editais e chamamentos públicos para organizações.</p>" * 30 + "</body></html>").encode()

    class D:
        pesado = False

        def __init__(self, nome, modo):
            self.nome, self.modo, self.usos = nome, modo, 0

        def buscar(self, url, tempo_limite=30):
            self.usos += 1
            if self.modo == "bloq":
                raise Bloqueado("x")
            if self.modo == "pend":
                raise Pendente("fila")
            return Resposta(url=url, status=200, conteudo=html, tipo="text/html")

    e = Escada([D("1 · API", "bloq"), D("9 · local", "pend")], intervalo_padrao=0, tentativas=1, dormir=lambda s: None)
    for _ in range(2):
        try:
            e.buscar("https://www.bing.com/search?q=x")
        except Pendente:
            pass
    assert e.aprendido == {} and e.semear({"bing.com": 9}) == 0
    loc = [D("1 · API", "bloq"), D("2 · leve", "ok"), D("9 · local", "pend")]
    Escada(loc, intervalo_padrao=0, tentativas=1, dormir=lambda s: None).buscar("http://127.0.0.1:8888/search?q=x")
    assert loc[1].usos == 1 and loc[2].usos == 0


def test_so_grava_o_que_muda_e_a_copia_dos_livros():
    """29/10/2026: o histórico crescia 35 MB/dia, ~80% telemetria repetida; a cópia dos livros a cada 3 dias, só os
    que mudaram; a IA com 4 vagas (eram 7, 3 sem uso); os pilotos sem o Camoufox; a etapa 8 sem falso alarme."""
    from datetime import datetime, timedelta, timezone

    from eldorado.banco.copia_livros import INTERVALO

    with tempfile.TemporaryDirectory() as d:
        di = EV.Diario(d, "01793999999999999999-000001-aaaaaaaa")
        for i in range(4):
            EV.emitir_se_mudou(di, "alarme.fechado", "t", "chave-teste", {"id": "a", "em": f"2026-10-29T0{i}:00:00+00:00", "motivo": "igual"})
        EV.emitir_se_mudou(di, "alarme.fechado", "t", "chave-teste", {"id": "a", "em": "2026-10-29T05:00:00+00:00", "motivo": "mudou"})
        assert len(list(EV.ler(d))) == 2
    assert INTERVALO == timedelta(days=3)
    assert "-c 24576 -np 4" in Path(".github/workflows/eldorado.yml").read_text(encoding="utf-8")
    assert "eldorado copia-livros" in Path(".github/workflows/eldorado.yml").read_text(encoding="utf-8")
    from eldorado.motores.acesso.completa import ORDEM

    assert "camoufox" not in ORDEM and "patchright" in ORDEM
    import re as _re

    assert _re.search(r'"cinza",\s+# 29/10/2026: informativo', Path("eldorado/base/painel/sala.py").read_text(encoding="utf-8"))
    assert datetime.now(timezone.utc)


def test_a_passagem_aplica_so_o_que_e_novo():
    """29/10/2026: cada etapa de aplicar lia o histórico inteiro (~600 mil eventos): a memória ia de 1,1 GB a 2,9 GB numa
    etapa (o medidor por etapa mostrou). Agora só os arquivos modificados desde a aplicação anterior."""
    import os
    import time

    with tempfile.TemporaryDirectory() as d:
        velho = EV.Diario(d, "01793999999999999999-000001-aaaaaaaa")
        velho.emitir("alarme.fechado", "t", {"id": "a", "em": "2026-10-29T00:00:00+00:00", "motivo": "x"})
        os.utime(velho.arquivo, (time.time() - 3600, time.time() - 3600))
        novo = EV.Diario(d, "01793999999999999999-000002-bbbbbbbb")
        novo.emitir("alarme.fechado", "t", {"id": "b", "em": "2026-10-29T00:00:00+00:00", "motivo": "x"})
        assert len(list(EV.ler(d))) == 2 and len(list(EV.ler(d, time.time() - 60))) == 1
    s = Path("eldorado/base/fluxo/nos.py").read_text(encoding="utf-8")
    assert "desde - 60 if desde is not None else None" in s and "_APLICADO_DESDE = inicio" in s


def test_o_veredito_vale_para_o_livro_que_mudou_de_etapa():
    """29/10/2026 (titular: todo dado de livro é gravado no livro): o veredito do Chrome vale para o livro que voltou à
    preparação e, válido, para o que chegou ao Farol (7 de 40 eram recusados); o descarte de um livro do Farol fica para
    a titular; a gravação tira do repositório o veredito já importado (senão seria importado de novo)."""
    s = Path("eldorado/base/cartorio/analise_externa.py").read_text(encoding="utf-8")
    assert 'if fase not in ("analise externa", "preparacao", "farol", "validacao", "arquivo"):' in s
    assert 'if fase == "farol" and v.decisao == "descartar":' in s
    g = Path("scripts/gravar.sh").read_text(encoding="utf-8")
    assert 'git ls-files "verificacao/vereditos/*.json"' in g and 'grep -v "/importados/"' in g
    assert '[ ! -e "$RAIZ/verificacao/vereditos/importados/$(basename "$f")" ]' in g   # 30/10/2026: só o já importado sai
    assert 'git ls-files "verificacao/lotes/*.json"' in g                                         # o lote apagado sai do repositório


def test_os_lotes_sem_retorno_pelos_dados_e_o_registro_do_importado():
    """29/10/2026: 'lote sem retorno' pelos DADOS (o livro com veredito do Chrome teve retorno), não pelo nome do arquivo;
    o arquivo importado ganha a hora da importação (senão o registro em importados/ não chegava ao repositório); o lote
    diário com até 100 livros (a fila chegou a 232 com lotes de 40)."""
    s = Path("eldorado/base/painel/sala.py").read_text(encoding="utf-8")
    assert "esperam -= vereditados" in s and "if (conteudo.get(st, set()) & esperam) - mais_novos:" in s
    a = Path("eldorado/base/cartorio/analise_externa.py").read_text(encoding="utf-8")
    assert '_os.utime(pasta / "vereditos" / "importados" / arq.name)' in a and "maximo: int | None = None" in a


def test_a_prevencao_vigia_quarentena_e_tendencias():
    """29/10/2026 (titular: evitar que ocorra de novo): o vigia de fora do ciclo (a gravação parada, o ciclo caído, a fila
    presa), a Qualidade de volta a ser sinal (a quarentena das travas da rede, só na Qualidade) e os alarmes de tendência
    (achados órfãos, o crescimento da operação no histórico, a memória por etapa)."""
    import yaml

    v = yaml.safe_load(Path(".github/workflows/vigia.yml").read_text(encoding="utf-8"))
    assert v[True]["schedule"][0]["cron"] == "*/30 * * * *"
    corpo = Path(".github/workflows/vigia.yml").read_text(encoding="utf-8")
    assert '"$idade" -gt 45' in corpo and "gh workflow run eldorado.yml" in corpo and '"$ia" -gt 55' in corpo
    assert "ELDORADO_QUARENTENA_REDE=1 pytest" in Path(".github/workflows/qualidade.yml").read_text(encoding="utf-8")
    import conftest

    assert len(conftest.QUARENTENA_REDE) == 6
    s = Path("eldorado/base/painel/sala.py").read_text(encoding="utf-8")
    for i in ('"es_orfaos"', '"hi_crescimento"', '"ma_memoria_etapa"'):
        assert i in s and i in Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")


def test_os_lotes_do_dia_cobrem_a_fila_inteira():
    """29/10/2026: a fila inteira vai ao Chrome (substituída pela especificação da titular: o lote do dia regerado quando a
    fila muda, o limite em config/cartorio.toml e as partes de 50; as travas em testes/test_lote.py)."""
    s = Path("eldorado/base/cartorio/analise_externa.py").read_text(encoding="utf-8")
    assert "def atualizar_lote_do_dia(" in s and "def gerar_lotes_do_dia(" not in s


def test_o_ciclo_traz_os_vereditos_novos_do_repositorio():
    """29/10/2026: o ciclo em andamento não via o veredito enviado depois que ele partiu (só ao ser religado; a
    implantação agora pula o religamento quando o ciclo já tem o código). A cada passagem, a análise externa traz os
    vereditos novos da pasta de entrada do repositório (os já importados ficam de fora)."""
    s = Path("eldorado/base/cartorio/analise_externa.py").read_text(encoding="utf-8")
    assert "trazer_vereditos_novos(pasta)" in s and '"git", "show", f"origin/main:{n}"' in s
    assert '(pasta / "vereditos" / "importados" / nome).exists()' in s


def test_o_mostrador_desobstruido_e_a_memoria_para_o_interceptador():
    """29/10/2026 (titular): o objeto 3D deslocado à direita (o mostrador do início do prazo inteiro à vista) com os raios
    alinhados à esfera; a memória liberada para o Interceptador (a vaga parada devolve o contexto; as vagas não retreinam
    a rede; a memória volta ao sistema depois da passagem); o reabastecimento contínuo da fila da Preparação."""
    g = Path("eldorado/base/painel/pagina/giroscopio/giroscopio.html").read_text(encoding="utf-8")
    p = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    assert "const DESLOCAMENTO = 0.12;" in g and "camera.setViewOffset(w_, h_, -DESLOCAMENTO * w_, 0, w_, h_)" in g   # 30/10/2026: 12% (o objeto maior com o mostrador inteiro)
    assert "left:calc(50% + 12%)" in p
    s = Path("eldorado/base/cerebro/pilotos_permanentes.py").read_text(encoding="utf-8")
    assert "time.monotonic() - vaga.parada_desde > 120" in s and "rede_atual(dados_, max_idade_s=86400)" in s
    assert "livres = paralelos_agora() - pedidos.unfinished_tasks" in s
    from eldorado.base.cerebro.governador import liberar_memoria

    assert liberar_memoria() >= 0
    assert "liberar_memoria()" in Path("eldorado/base/nucleo/comandos.py").read_text(encoding="utf-8")
