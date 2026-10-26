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
