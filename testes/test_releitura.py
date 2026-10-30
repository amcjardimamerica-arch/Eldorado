"""A releitura dos documentos herdados sem texto (24/10/2026): o texto vai para o próprio documento herdado; a tentativa,
para o aprendizado do Cérebro."""


PAGINA = "<html><body><main><h1>Edital de Fomento 2026</h1><p>As inscrições vão até 30/11/2026. Valor total de R$ 500 mil.</p></main></body></html>"


def test_o_documento_herdado_ganha_o_texto(tmp_path):
    """R35 (titular, 30/10/2026): a releitura dos documentos herdados está DESLIGADA — ela só guardava o texto dos sites
    (4.926 documentos sem livro, 72 milhões de caracteres); o documento herdado fica só com o endereço."""
    from eldorado.base.cartorio import releitura

    assert releitura.escolher(None, None, 50) == []
