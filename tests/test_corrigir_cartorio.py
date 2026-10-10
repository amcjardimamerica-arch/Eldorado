import importlib.util, pathlib
R = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("cc", R / "scripts/corrigir_cartorio.py")
cc = importlib.util.module_from_spec(spec); spec.loader.exec_module(cc)
FIX = R / "tests/fixtures/cartorio_pagina_antes.html"

def test_patch_aplica_tudo_e_e_idempotente():
    novo, ap, au = cc.aplicar_em_texto(FIX.read_text(encoding="utf-8"))
    assert not au and len(ap) == len(cc.PATCHES)
    assert cc.MARCA in novo and "já constava antes do Cartório · sem certidão" in novo
    assert cc.aplicar_em_texto(novo) == (novo, [], [])

def test_patch_em_template_python_com_chaves_duplicadas():
    t = FIX.read_text(encoding="utf-8").replace("{", "{{").replace("}", "}}")
    novo, ap, au = cc.aplicar_em_texto(t)
    assert not au

def test_um_verde_de_um_pedido_nao_e_100_por_cento_dos_12():
    c = {"itens": {"Objeto": {}}, "dispensas": {}, "faltavam": ["Objeto"], "resolvidos": ["Objeto"]}
    b = cc.cobertura(c)
    assert b["certificados"] == 1 and b["ja_constavam"] == 11
    assert b["pct_certificado_12"] == round(1 / 12, 4) and b["pct_cobertura_12"] == 1.0

def test_enriquecer_resumo():
    d = {"certidoes": [{"itens": {k: {} for k in cc.DOZE}, "dispensas": {}, "faltavam": cc.DOZE, "link_oficial": "x"}]}
    cc.enriquecer_dados(d)
    assert d["resumo"]["certidoes_12_de_12"] == 1 and d["resumo"]["pct_certificado_12"] == 1.0
