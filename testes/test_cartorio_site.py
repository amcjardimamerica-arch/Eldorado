"""O Cartório no site ligado aos dados (titular, 25/10/2026: a página estava estática)."""

import shutil
import sqlite3
from pathlib import Path

from eldorado.base.painel.cartorio import montar


def test_o_cartorio_tem_os_mostradores_e_a_ficha_de_cada_livro(tmp_path):
    shutil.copy("dados/biblioteca.db", tmp_path / "b.db")
    from eldorado.banco.biblioteca.esquema import abrir

    abrir(tmp_path / "b.db").close()
    c, fichas = montar(sqlite3.connect(tmp_path / "b.db"), None)
    m = c["mostradores"]
    assert [e["id"] for e in m["etapas"]] == ["recepcao", "certificacao", "preparacao", "validacao", "analise externa"]
    assert [e["degrau"] for e in m["escada"]][:8] == ["1", "2", "P", "3", "4", "5", "6", "7"]  # a ponte BR depois da nuvem
    assert c["certidoes"] and len(fichas) == len(c["certidoes"])  # uma ficha por livro
    f = next(iter(fichas.values()))
    assert {"relatorio", "parecer", "repasse", "orientacao", "itens", "etapa", "degrau"} <= set(f)
    assert Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8").count("car-m-etapas") >= 2


def test_o_classificador_do_cartorio_e_a_janela_da_decisao():
    """26/10/2026 (titular): os dois medidores do Cartório (a escada e as 5 etapas com a classificação em dois ramos, no
    modo coletivo ou individual) e o 'Para a sua decisão' só numa janela da tela inicial, não inserido nas páginas."""
    from pathlib import Path

    p = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    assert 'id="c2-escada"' in p and 'id="c2-fluxo"' in p and 'id="c2-q"' in p  # os dois medidores e a busca
    assert "Fica no Eldorado" in p and "Vai ao Farol" in p and "6. A classificação" in p  # a etapa 6 com dois ramos
    assert "width:100vw;margin-left:calc(50% - 50vw)" in p  # de margem a margem
    assert 'id="c2-gaveta"' in p and "function dica(" in p and "function particulas(" in p  # a gaveta, a dica e o fluxo vivo
    assert 'fetch("dados/cartorio/"+encodeURIComponent(id)' in p  # a trajetória do livro
    assert 'id="v-relatorio-titular"' not in p and 'id="dec-janela"' in p  # a janela, não uma seção
    assert 'sessionStorage.getItem("eldorado-decisao")' in p and "naInicial()" in p  # só na inicial, uma vez por visita


def test_os_fluxos_e_o_tempo_na_etapa_no_cartorio():
    from eldorado.base.painel.cartorio import _fluxos

    ps = {
        "L1": [
            {"de": None, "para": "recepcao", "em": "2026-10-26T10:00:00+00:00"},
            {"de": "recepcao", "para": "certificacao", "em": "2026-10-20T10:00:00+00:00"},
        ]
    }
    f = _fluxos(ps, "2026-10-26T12:00:00+00:00")
    assert {"de": "chegada", "para": "recepcao", "sete_dias": 1, "um_dia": 1} in f and {
        "de": "recepcao",
        "para": "certificacao",
        "sete_dias": 1,
        "um_dia": 0,
    } in f


def test_o_painel_o_que_o_cartorio_ja_sabe():
    """26/10/2026 (titular): os 12 itens, as abordagens (com os itens de fato certificados) e os balcões num painel só, de
    margem a margem, com a dica, a gaveta e os avisos; os blocos antigos fora da tela."""
    from pathlib import Path

    p = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    assert 'id="cl3"' in p and 'id="s3-itens"' in p and 'id="s3-ab"' in p and 'id="s3-ba"' in p
    assert "Material não é item" in p and "O pior balcão" in p and "O item mais fraco nas abertas" in p
    i = p.index('id="car-cards"')
    assert '<div hidden style="display:none">' in p[i - 200 : i]  # os blocos antigos fora da tela
    assert 'value="abertas"' in p  # a gaveta: as abertas primeiro


def test_as_abordagens_medem_os_itens_de_fato_certificados(bancos):
    from eldorado.base.painel.cartorio import montar

    b = bancos["biblioteca"]
    b.execute(
        "INSERT INTO livro(id, missao, chave, titulo, estrela, selo_livro, informacoes_validadas, situacao, criado_em, atualizado_em) "
        "VALUES ('L', 'oportunidades', 'k', 'Edital', 'sem', 'sem', 0, 'em trabalho', '2026-10-26T10:00:00+00:00', '2026-10-26T10:00:00+00:00')"
    )
    b.execute("INSERT INTO passaporte(livro_id, fase, entrou_em) VALUES ('L', 'preparacao', '2026-10-26T10:00:00+00:00')")
    b.execute("INSERT INTO livro_dados(livro_id, validacao, validado_em) VALUES ('L', 'aprovado', '2026-10-26T10:00:00+00:00')")
    b.execute(
        "INSERT INTO tentativa(livro_id, fase, ferramenta, numero, em, resultado) VALUES ('L', 'preparacao', 'abordagem 1', 1, "
        "'2026-10-26T11:00:00+00:00', '{\"abordagem\": \"documento na mão\"}')"
    )
    b.execute(
        "INSERT INTO certidao(livro_id, item, valor, situacao, fase, em) VALUES ('L', 'Objeto', 'x', 'comprovado', 'preparacao', '2026-10-26T12:00:00+00:00')"
    )
    b.commit()
    principal, _ = montar(b, bancos["cerebro"], None, "2026-10-26T13:00:00+00:00")
    a = principal["por_abordagem"]["1"]
    assert a["itens"] == 1 and a["por_item"] == {"Objeto": 1} and a["livros"] == 1 and a["livros_ids"] == ["L"]


def test_os_livros_por_area_e_o_par_abordagens_balcoes():
    """26/10/2026 (titular): sem o cabeçalho antigo; as certidões por área em duas colunas, com os filtros de antes, os 12
    quadradinhos e o cartão aberto (os 12 itens com o trecho e a página); as abordagens e os balcões lado a lado."""
    from pathlib import Path

    p = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    i = p.index("<h1>Cartório de fontes oficiais</h1>")
    assert '<div hidden style="display:none">' in p[i - 40 : i]  # o cabeçalho antigo fora da tela
    assert 'id="cl4"' in p and 'id="a4-nav"' in p and "#cl4 .col2{display:grid;grid-template-columns:1fr 1fr" in p
    for f in ("a4-q", "a4-tipo", "a4-balcao", "a4-sit", "a4-ord", "a4-ab"):  # os filtros de antes, e mais
        assert f'id="{f}"' in p
    assert "Ver a trajetória na esteira" in p and "it12" in p  # o cartão aberto
    assert '<div class="duo"><div class="pn ab">' in p and "#cl3 .duo{display:grid;grid-template-columns:1.25fr 1fr" in p


def test_o_quadro_motores_de_busca_tem_os_motores_do_sistema():
    """26/10/2026 (titular): o quadro 'Motores de Busca' (formato do Eldorado0) mostra todos os motores do sistema, com o
    calendário do mês, o funcionamento e o rendimento; os números do topo vêm do sistema."""
    import json
    from pathlib import Path

    p = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    assert "os 260 pontos de captação" not in p
    s = Path("eldorado/base/painel/dados.py").read_text(encoding="utf-8")
    assert 'mo["oficiais"] = _motores_de_busca(sis)' in s and '"completos":' in s and '"media_camadas":' in s
    for campo in ('"dias": dias', '"ultima_leitura":', '"situacao": situacao', '"rendimento":', '"descricao":', '"rank": i'):
        assert campo in s, campo
    previstos = json.loads(Path("config/motores_previstos.json").read_text(encoding="utf-8"))["motores"]
    assert len(previstos) >= 45  # todos os motores entram na lista


def test_a_pagina_inicial_calendario_por_tema_e_os_quadros_em_sequencia():
    """27/10/2026 (titular): o calendário (até 10 prazos por tema, os que terminam antes primeiro) na metade esquerda; o
    FAROL e a Fila prioritária à direita; as Novas oportunidades absorvidas pelo calendário."""
    from pathlib import Path

    p = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    assert "gc-tema" in p and "const POR_TEMA=10;" in p
    assert ".coluna-direita{display:flex;flex-direction:column;gap:0}" in p  # o FAROL e a Fila, sem espaço
    i, j, k = p.index("Calendário de Editais</h3>"), p.index('<div class="painel-tit farol">'), p.index("Fila prioritári")
    assert i < j < k
    assert '<div hidden style="display:none"><div class="novas" id="fi-novas">' in p
    assert 'ghDispatch("arquivar.yml"' in p  # o Arquivar grava na Biblioteca


def test_o_lago_dos_prazos():
    """28/10/2026 (titular): o calendário do Eldorado com o giroscópio Serpentes de Jade à esquerda, em 3/5 da tela (embutido,
    sem servidor externo, sempre na versão nova; o mouse não o move; ao passar o mouse numa oportunidade, o mostrador da
    esfera mostra o prazo dela); sem a gaiola; o giroscópio mais rápido; as serpentes no enquadramento; os raios centrados
    na esfera; à direita, em 40%, o quadro claro e sem rolagem própria (o objeto acompanha a página) (os dias em colunas, o nome dentro da faixa): as 10 que vencem primeiro por área."""
    from pathlib import Path

    p = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    g = Path("eldorado/base/painel/pagina/giroscopio/giroscopio.html").read_text(encoding="utf-8")
    assert '<div id="sj"><canvas class="estrelas" id="sj-estrelas"' in p and 'src="giroscopio/giroscopio.html?v=20261030d"' in p   # 29/10/2026: o céu estrelado
    assert "grid-template-columns:minmax(0,6fr) minmax(0,4fr)" in p and "#sj .palco{position:sticky;top:8px;height:calc(100vh - 16px)" in p
    assert "--c-fundo:#F7F4EC" in p and 'class="rolagem"' not in p and "overflow:clip" in p  # o quadro claro, sem rolagem própria  # 3/5 e 2/5
    assert "#sj .raios,#sj .raios2,#sj .halo{position:absolute;left:50%;top:50%" in p  # no centro da esfera (deslocada 6%, 29/10/2026)
    bloco = p[p.index('<div id="sj">') : p.index("</nav>", p.index('<div id="sj">'))]
    assert bloco.count('class="grupo"') == 3 and 'data-ir="farol:f-biblioteca"' in bloco
    assert 'tipo:"prazos"' in p and 'tipo:"selecionar"' in p and "g[a].slice(0,10)" in p and "const CANON=" in p
    assert "z-index:2;pointer-events:none}" in p  # o mouse não move o objeto
    assert "cdn.jsdelivr.net" not in g and 'src="three.min.js"' in g and "controls.enableZoom = false;" in g
    assert "TorusGeometry(GR * 1.12" not in g and "a1 += dt * (0.44" in g and "controls.enabled = false;" in g and "rmax: 2.9" in g
    for f in ("three.min.js", "OrbitControls.js", "RoomEnvironment.js"):
        assert Path("eldorado/base/painel/pagina/giroscopio", f).exists()


def test_o_radar_ao_lado_do_farol():
    """28/10/2026 (titular): na página inicial, o ELDORADO — Radar de recursos ocupa a metade esquerda, ao lado do FAROL;
    o calendário abaixo do Radar e a Fila prioritária abaixo do FAROL."""
    from pathlib import Path

    p = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    i = p.index('<div class="faixa-larga">')
    seg = p[i:]
    esq, radar, cal, dir_, farol = (
        seg.index(x)
        for x in (
            '<div class="coluna-esquerda">',
            "painel-tit eldorado",
            "Calendário de Editais</h3>",
            '<div class="coluna-direita">',
            '<div class="painel-tit farol">',
        )
    )
    assert esq < radar < cal < dir_ < farol



def test_o_calendario_dias_na_esfera_objeto_enquadrado_e_inicio_sem_menu():
    """29/10/2026 (titular): a esfera central mostra só os dias que faltam; o objeto 3D preenche o palco, com o limite no
    objeto e no espaço das serpentes (sem enquadrar com o palco oculto); o Início do calendário é só o botão principal."""
    g = Path("eldorado/base/painel/pagina/giroscopio/giroscopio.html").read_text(encoding="utf-8")
    assert "a estrela de pouco brilho com os dias que faltam por cima" in g and "x.fillText(v.status.txt" not in g
    # 29/10/2026 (titular): no lugar da esfera, a estrela (sem a cúpula de vidro), sempre por cima dos anéis; o céu noturno
    # 30/10/2026 (titular): a forma ESFÉRICA mantida (a esfera-estrela âmbar, com o brilho discreto rente à superfície);
    # o número por cima; o objeto no tamanho anterior (sem o desconto do deslocamento); o céu denso e cintilante
    # 30/10/2026 (titular): uma ESTRELA sem dúvida — branco-azulada, emitindo luz (sem sombra), o escurecimento de borda, a
    # coroa de frente para a câmera com os raios só do lado de fora; o objeto no maior tamanho com o mostrador inteiro
    assert "planet.visible = true;" in g and "float limbo = " in g and "const coroa = new T.Sprite(" in g
    # 30/10/2026 (titular): o limite é o mostrador de data em QUALQUER posição em volta do anel; o objeto centralizado
    assert "const RAIO_LIMITE = 2.08 + 0.86 + 0.95 / 2 + 0.085;" in g and "const DESLOCAMENTO = 0;" in g
    # 30/10/2026 (titular): o número NA superfície (a película virada para a câmera, a 1/4 da largura: a frente da esfera),
    # respeitando a profundidade — os anéis e as serpentes passam na frente dele
    assert "shell.visible = true;" in g and "estrela.visible = false;" in g and "FRENTE = W * 0.25" in g and "P.tex.needsUpdate = true;" in g
    assert "depthTest: false, toneMapped: false" in g and "drawEstrela(x, S)" not in g and "* (1 - 2 * DESLOCAMENTO)" not in g
    assert "g.add(new T.Mesh(new T.SphereGeometry(GR * 1.07, 48, 24), M.glass));" not in g
    p_ = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    assert 'id="sj-estrelas"' in p_ and "(function ceu(){" in p_ and "prefers-reduced-motion: reduce" in p_ and "#sj .raios,#sj .raios2{display:none}" in p_
    assert "RMAX_SERPENTES = 2.9" in g and "RAIO_LIMITE / Math.sin(meia)" in g and "o palco oculto (largura zero)" in g
    p = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    assert '<button type="button" id="sj-inicio">Início</button>' in p and 'data-ir="eldorado:neural">Sala de controle</button></div></div>\n    <div class="grupo"><button type="button" aria-haspopup="true">Eldorado' not in p
