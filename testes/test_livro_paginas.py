"""02/11/2026 (titular): o livro da oportunidade aprovado no canvas — capa (faixas na cor da estrela; sem estrela, sem
valores), página 1 (dados), 2 (placar, escada, esteira, tentativas), 3 (diário por data, hora de cada registro, o fim de
cada análise do Chrome, legislação e previsão) e 4 (a anterior em laranja, com o parecer) — montado com a história completa."""
from pathlib import Path

P = Path("eldorado/base/painel/pagina")


def test_o_design_esta_dentro_do_livro_3d():
    """o objeto continua sendo o livro 3D da titular: as páginas aprovadas viram as texturas dele (nada o substitui)"""
    h = (P / "dashboard.html").read_text(encoding="utf-8")
    assert '<script src="livro-paginas.js"></script>' in h and 'href="livro-paginas.css"' in h
    assert "window.LivroPaginas.conteudo3D(o)" in h and "window.LivroPopup.abrir(c||conteudo(o||{}))" in h
    j = (P / "livro-paginas.js").read_text(encoding="utf-8")
    assert "window.abrirLivro3D =" not in j and "lp2-visor" not in j and "conteudo3D" in j and "dados/cartorio/" in j
    t = (P / "livro3d.js").read_text(encoding="utf-8")
    assert "if (pg.imagem) c.getContext('2d').drawImage(pg.imagem" in t and "if (cont.capaImagem)" in t


def test_as_regras_das_paginas():
    j = (P / "livro-paginas.js").read_text(encoding="utf-8")
    assert '["ouro", "prata", "bronze"].includes(s)' in j and "lp2-orn" in j          # a capa: metal da estrela ou só o ornamento
    assert "Etapa atual" in j and "Nesta etapa" in j and "Tentativas" in j and "o que cada degrau conseguiu" in j
    assert "Eliminou a oportunidade." in j and "Arquivou a oportunidade." in j and "Inseriu os dados na oportunidade." in j
    assert "Legislação aplicável" in j and "Próxima previsão" in j and "Parecer sobre a oportunidade anterior" in j
    c = (P / "livro-paginas.css").read_text(encoding="utf-8")
    assert "--band:#D17600" in c                                                        # a versão passada no laranja da logomarca
