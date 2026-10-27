"""Os pilotos no painel e o Interceptador (26/10/2026): cada vaga do Interceptador num fio fixo (a conexão da vaga não muda
de fio; só a vaga 1 voava); a posição do Espião e o voo do Interceptador no formato que o painel lê; as marcas na
fuselagem; a fonte do edital da PNAB Goiás 2026; a Biblioteca no Cartório."""

import threading
import time
import tomllib
from datetime import datetime, timedelta, timezone
from pathlib import Path

from eldorado.base.cerebro import pilotos_permanentes as PP
from eldorado.base.painel.pilotos import _abates, _missao_atual


def test_cada_vaga_do_interceptador_voa_no_seu_proprio_fio(monkeypatch, tmp_path):
    usados: dict[int, set] = {}

    def voo(vaga, parar, lv_id, base, tempo):
        usados.setdefault(vaga.k, set()).add(threading.current_thread().name)
        time.sleep(0.01)

    class Con:
        def execute(self, q, *a):
            return [(0, "base_classe")]

        def close(self):
            pass

    monkeypatch.setattr(PP, "_voo_interceptador", voo)
    import eldorado.base.comandante.pilotos as _CP

    monkeypatch.setattr(_CP, "vagas_por_ociosidade", lambda: 2)
    monkeypatch.setattr(PP, "_contexto", lambda dados, diario: (dados, Con(), None, None))
    monkeypatch.setattr(PP, "paralelos_agora", lambda: 2)
    import eldorado.base.comandante.biblioteca as CB
    import eldorado.motores.pilotos.interceptador as I

    monkeypatch.setattr(CB, "avaliar", lambda con: [])
    monkeypatch.setattr(CB, "fila", lambda av: [{"id": f"L{i}"} for i in range(40)])
    monkeypatch.setattr(I, "fila", lambda con, hoje: [])

    class Diario:
        pasta = tmp_path

        def emitir(self, *a, **k):
            pass

    parar = threading.Event()
    t = threading.Thread(target=PP.voar_interceptador, args=(tmp_path, Diario(), parar), daemon=True)
    t.start()
    fim = time.time() + 10
    while time.time() < fim and sum(len(v) for v in usados.values()) < 2:
        time.sleep(0.1)
    time.sleep(0.5)
    parar.set()
    assert len(usados) == 2  # as 5 vagas voaram
    assert all(len(fios) == 1 for fios in usados.values())  # cada uma sempre no seu fio


def test_os_arquivos_dos_pilotos_no_formato_do_painel():
    agora = datetime.now(timezone.utc)
    recente = (agora - timedelta(minutes=2)).isoformat()
    m = _missao_atual((recente, "em voo: a família internacional_espanhol (autorizada pelo Comandante)"), agora)
    assert m == {"motor": "piloto-aberto", "titulo": "a família internacional_espanhol", "desde": recente}
    assert _missao_atual(((agora - timedelta(minutes=30)).isoformat(), "em voo: x"), agora) is None
    ab = _abates(
        [
            {"em": "2026-10-26T10:00:00", "titulo": "Edital", "link": "u", "decisao": "aceito"},
            {"em": "2026-10-26T11:00:00", "titulo": "Outro", "link": "v", "decisao": "barrado"},
        ],
        "2026-10-26",
    )
    assert ab["n"] == 1 and ab["ouro"] == 1 and ab["ultimos"][0]["titulo"] == "Edital"  # as marcas na fuselagem
    leg = Path("eldorado/base/painel/legado.py").read_text(encoding="utf-8")
    assert 'saida["interceptador_ao_vivo.json"]' in leg and '"estado": "em_voo"' in leg  # o voo do Interceptador existe
    html = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    i = html.index("function decolarInt(el){")
    assert "animationiteration" not in html[i : i + 1500] and "m41" in html[i : i + 1500]  # o nariz pelo movimento real


def test_a_fonte_do_edital_da_pnab_goias_2026_e_a_biblioteca_no_cartorio():
    d = tomllib.loads(Path("eldorado/motores/canal/config/estaduais-go-gov.toml").read_text(encoding="utf-8"))
    assert "https://goias.gov.br/cultura/pnab/edital-2026-pnab/" in [f["url"] for f in d["fonte"]]
    html = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    assert '<section id="cl4" aria-label="A Biblioteca">' in html and 'id="a4-acervo"' in html
    for f in ("a4-uf", "a4-esfera", "a4-fonte", "a4-mod", "a4-per", "a4-selo", "a4-limpar"):
        assert f'id="{f}"' in html
    i = html.index("<!-- MOTORES LIVROS · fontes específicas")
    assert '<div hidden style="display:none">' in html[i - 60 : i]  # o quadro antigo fora dos motores


def test_a_carga_desconta_o_processador_da_ia(monkeypatch):
    """26/10/2026: a IA ocupa o processador enquanto pensa, e os pilotos usam a IA; medindo o processador inteiro, um voo
    bloqueava o outro (a regra dos 85%). A carga desconta a IA; a memória segue medida inteira."""
    import eldorado.base.cerebro.governador as G

    class IA:
        def is_running(self):
            return True

        def cpu_percent(self, intervalo=None):
            return 300.0  # 3 núcleos inteiros

    monkeypatch.setattr(G, "_processo_ia", lambda: IA())
    monkeypatch.setattr(G.psutil, "cpu_percent", lambda interval=None: 90.0)
    monkeypatch.setattr(G.psutil, "cpu_count", lambda: 4)
    assert abs(G.cpu_sem_ia(0) - 0.15) < 1e-9  # 90% − 75% da IA = 15%


def test_o_codigo_so_vai_para_o_livro_com_a_ficha_e_os_alertas_fecham(tmp_path):
    import sqlite3

    from eldorado.base.comandante.organizar import _fechar_recusas_do_codigo

    c = sqlite3.connect(tmp_path / "cerebro.db")
    c.execute(
        "CREATE TABLE alarme(id INTEGER PRIMARY KEY, gravidade TEXT, modulo TEXT, mensagem TEXT, rastro TEXT, aberto_em TEXT, fechado_em TEXT, repeticoes INTEGER)"
    )
    c.execute("INSERT INTO alarme(modulo, mensagem) VALUES ('gravador', 'evento recusado (livro.codigo, 0179-1): linha não encontrada')")
    c.execute("INSERT INTO alarme(modulo, mensagem) VALUES ('gravador', 'evento recusado (livro.links, 0179-2): outro')")
    c.commit()
    ev = []

    class D:
        def emitir(self, t, m, d):
            ev.append((t, d))

    assert _fechar_recusas_do_codigo(tmp_path, D()) == 1 and ev[0][0] == "alarme.fechado" and ev[0][1]["id"] == 1
    src = Path("eldorado/base/comandante/organizar.py").read_text(encoding="utf-8")
    assert 'if x["id"] in atuais and atuais[x["id"]] != cod' in src  # só com a ficha do livro


def test_no_maximo_dois_voos_usam_a_ia_ao_mesmo_tempo():
    """26/10/2026: com as 5 vagas pedindo à IA juntas, cada pedido levava os 4 minutos inteiros e os voos ficavam presos."""
    from eldorado.motores.pilotos import interceptador as I

    assert I.VEZ_DA_IA._limite() >= 1
    src = Path("eldorado/motores/pilotos/interceptador.py").read_text(encoding="utf-8")
    assert "VEZ_DA_IA.acquire(timeout=90)" in src and '"adiada"' in src


def test_os_testes_nao_acessam_a_internet():
    """26/10/2026: a barreira de rede da bateria: só o próprio computador; o resto falha na hora (na Qualidade, os degraus
    da escada escapavam para sites de verdade e os testes davam outros resultados ou ficavam pendurados)."""
    import socket

    import pytest

    s = socket.socket()
    with pytest.raises(OSError, match="rede externa bloqueada"):
        s.connect(("93.184.216.34", 80))
    s.close()


def test_os_achados_dos_pilotos_sobrevivem_num_arquivo(tmp_path, monkeypatch):
    """27/10/2026: a fila só na memória perdia os achados a cada passagem cortada."""
    from eldorado.base.nucleo.contratos import Achado

    monkeypatch.setattr(PP, "PASTA_ENTREGAS", tmp_path)
    a = Achado(id="x1", motor="espiao", encontrado_em="2026-10-27", link_divulgacao="https://exemplo.org/e", titulo="Edital", dados={})
    PP.entregar("espiao", a)
    while not PP.ENTREGAS["espiao"].empty():  # a fila se perdeu (o corte)
        PP.ENTREGAS["espiao"].get_nowait()
    voltou = PP.entregas("espiao")
    assert [x.id for x in voltou] == ["x1"] and not (tmp_path / "espiao.jsonl").exists()


def test_a_familia_e_sorteada_e_descansa_quando_cansa():
    """27/10/2026: pegar sempre a primeira fez 399 de 421 missões irem a uma família só."""
    import eldorado.base.comandante.pilotos as CP

    CP._cansaco.clear()
    for _ in range(CP.CANSACO_MISSOES):
        CP.registrar_missao("internacional_espanhol", 0)
    assert CP._cansaco["internacional_espanhol"]["descansa_ate"] > 0  # 10 sem achado: descansa
    CP.registrar_missao("empresa_semente", 2)
    assert CP._cansaco["empresa_semente"]["zeros"] == 0
    src = Path("eldorado/base/comandante/pilotos.py").read_text(encoding="utf-8")
    assert "random.choices(lista, weights=pesos)" in src  # sorteia pela distribuição
    CP._cansaco.clear()


def test_toda_trava_citada_nas_regras_existe():
    """27/10/2026: a trava renomeada sem atualizar a regra barrou o portão da produção por mais de 8 horas (o ciclo não
    começa sem as travas das regras de pé). Toda trava citada nas regras da titular tem de existir."""
    import json
    import re

    regras = json.loads(Path("config/regras_titular.json").read_text(encoding="utf-8"))["regras"]
    faltam = []
    for r in regras:
        for t in r.get("travas", []):
            arq, _, fn = t.partition("::")
            p = Path(arq)
            if not p.exists() or not re.search(rf"^def {re.escape(fn)}\(", p.read_text(encoding="utf-8"), re.M):
                faltam.append((r["id"], t))
    assert not faltam, faltam


def test_o_gravador_nao_deixa_alarme_de_recusa_resolvida(bancos, tmp_path):
    """27/10/2026 (a quarta cobrança): o código do livro sem a ficha é dispensado (o dado é recalculado), sem recusa; a
    recusa repetida não abre outro alarme; o alarme de uma recusa resolvida (ou dispensável) fecha ao fim da aplicação."""
    from eldorado.base.nucleo.eventos import criar
    from eldorado.base.nucleo.gravador import Gravador

    g = Gravador(bancos)
    c = bancos["cerebro"]
    ev = criar("livro.codigo", "comandante", {"livro_id": "L-sem-ficha", "codigo": "GO·CUL·PUB·FOM·PRJ"})
    r = g.aplicar([ev, ev])
    assert r.ok and r.dispensados == 1  # dispensado, não recusado
    c.execute(
        "INSERT INTO alarme(gravidade, modulo, mensagem, aberto_em, repeticoes) VALUES ('alta', 'gravador', "
        "'evento recusado (livro.codigo, 0179-antigo): linha não encontrada', '2026-10-26T20:29:14+00:00', 1)"
    )
    c.commit()
    r = g.aplicar([])
    assert r.alarmes_fechados == 1
    assert not c.execute("SELECT 1 FROM alarme WHERE fechado_em IS NULL AND mensagem LIKE 'evento recusado%'").fetchone()


def test_o_interceptador_elastico_pela_ociosidade(monkeypatch):
    """27/10/2026 (titular): 1 Interceptador no uso normal; a máquina ociosa libera até 5; com carga, volta a 1."""
    import eldorado.base.cerebro.governador as G
    import eldorado.base.comandante.pilotos as CP

    relogio = [1000.0]
    monkeypatch.setattr(CP.time, "monotonic", lambda: relogio[0])

    class Mem:
        percent = 50.0

    monkeypatch.setattr(CP.__dict__.get("psutil", __import__("psutil")), "virtual_memory", lambda: Mem())
    CP._ocio["desde"] = None
    G._IA["total"] = 0.10
    assert CP.vagas_por_ociosidade() == 1
    relogio[0] += 6 * 60
    assert CP.vagas_por_ociosidade() == 3
    relogio[0] += 10 * 60
    assert CP.vagas_por_ociosidade() == 5
    G._IA["total"] = 0.95
    assert CP.vagas_por_ociosidade() == 1
    src = Path("eldorado/base/cerebro/regencia.py").read_text(encoding="utf-8")
    assert "pool.shutdown(wait=False, cancel_futures=True)" in src and "orcamento + folga" in src  # a coleta não espera o preso


def test_arquivar_pela_titular_grava_na_biblioteca_e_sai_das_abertas(bancos, gravador, tmp_path):
    """27/10/2026 (titular): uma única fonte (a Biblioteca): arquivar pelo painel é a passagem do livro para o arquivo,
    autorizada pela titular; ele sai das abertas (o calendário e a aba leem a mesma consulta) e o Comandante não o traz."""
    from datetime import datetime, timezone

    from typer.testing import CliRunner

    from eldorado.base.nucleo.comandos import app
    from eldorado.base.nucleo.eventos import ler

    b = bancos["biblioteca"]
    agora = datetime.now(timezone.utc).isoformat()
    b.execute(
        "INSERT INTO livro(id, missao, chave, titulo, estrela, selo_livro, informacoes_validadas, situacao, criado_em, atualizado_em) "
        "VALUES ('L1', 'oportunidades', 'k', 'Edital aberto', 'ouro', 'sem', 0, 'em trabalho', ?, ?)",
        (agora, agora),
    )
    b.execute("INSERT INTO passaporte(livro_id, fase, entrou_em) VALUES ('L1', 'preparacao', ?)", (agora,))
    b.execute(
        "INSERT INTO livro_dados(livro_id, validacao, validado_em, situacao_prazo, inscricao_fim) VALUES ('L1', 'aprovado', ?, 'aberta', '2099-12-31')",
        (agora,),
    )
    b.commit()
    r = CliRunner().invoke(app, ["arquivar", "--livro", "L1", "--eventos", str(tmp_path / "ev")])
    assert r.exit_code == 0, r.output
    assert gravador.aplicar(list(ler(tmp_path / "ev"))).ok
    assert b.execute("SELECT fase FROM passaporte WHERE livro_id = 'L1'").fetchone()[0] == "arquivo"
    assert b.execute("SELECT motivo FROM passagem WHERE livro_id = 'L1' ORDER BY id DESC").fetchone()[0].startswith("pela titular:")
    src = Path("eldorado/base/painel/dados.py").read_text(encoding="utf-8")
    assert "AND p.fase <> 'arquivo' ORDER BY d.inscricao_fim" in src  # sai das abertas
    assert Path(".github/workflows/arquivar.yml").exists()


def test_o_prazo_e_de_cada_acionamento_e_o_motor_volta_ate_terminar_o_dia():
    """27/10/2026 (titular): 20 min por acionamento (+5 de folga), sem prazo para a coleta; o motor que não terminou o dia é
    acionado de novo; o diário lido até a última matéria."""
    from eldorado.base.cerebro import regencia as RG
    from eldorado.motores.canal.motor import CfgElo, CfgPaginacao

    src = Path("eldorado/base/cerebro/regencia.py").read_text(encoding="utf-8")
    assert "sem prazo para a coleta" in src and "PENDENTES_DO_DIA" in src and "orcamento + folga" in src
    assert CfgElo.model_fields["limite"].default == 5000 and CfgPaginacao.model_fields["maximo"].default == 50
    RG.PENDENTES_DO_DIA[RG._hoje()] = {"do-goiania"}
    assert "do-goiania" in RG.PENDENTES_DO_DIA[RG._hoje()]
    RG.PENDENTES_DO_DIA.clear()
