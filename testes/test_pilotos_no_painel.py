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
    monkeypatch.setattr(PP, "_contexto", lambda dados, diario: (dados, Con(), None, None))
    monkeypatch.setattr(PP, "paralelos_agora", lambda: 5)
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
    while time.time() < fim and sum(len(v) for v in usados.values()) < 5:
        time.sleep(0.1)
    time.sleep(0.5)
    parar.set()
    assert len(usados) == 5  # as 5 vagas voaram
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

    assert I.VEZ_DA_IA._initial_value == 2
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
