"""09/11/2026 (titular): o cartão de cada etapa em três linhas (os relógios, os números, o último sinal), o relógio só com a
faixa do bom e do ruim, o Comandante contra a ordem fixa no lugar da idade do modelo, e o «ciente» do Farol e das lições."""
import sqlite3
from pathlib import Path

from eldorado.base.painel import sala


def _sala():
    b = sqlite3.connect("file:dados/biblioteca.db?mode=ro", uri=True)
    c = sqlite3.connect("file:dados/cerebro.db?mode=ro", uri=True)
    return sala.montar(b, c, Path("."), [])


def test_relogio_so_com_bom_e_ruim_e_a_etapa_8():
    d = _sala()
    for x in d["instrumentos"]:
        if x.get("relogio"):
            f = x["faixa"]
            assert any(isinstance(v, (int, float)) for k in ("normal", "alarme") for v in (f.get(k) or []))
            assert x["escala"][1] > x["escala"][0]
    ap = sala.ETAPAS["aprendizado"]
    assert ap.index("cm_comparacao") < ap.index("rn_treino") and "cm_comparacao" in sala.RELOGIOS["aprendizado"]
    assert sala.RELOGIOS["regencia"] == ["rg_regencia", "ma_cobertura", "dg_finalidade"]


def test_o_farol_tem_o_ciente_e_as_licoes_nos_alertas():
    d = _sala()
    f = next(x for x in d["instrumentos"] if x["id"] == "fa_fecham_7d")
    assert "ids" in f and "novos" in f and f["valor"] == len(f["ids"])
    for x in d["instrumentos"]:
        if x["id"] in sala.ETAPAS["investigacao"] and x["estado"] in ("amarelo", "vermelho"):
            assert x.get("licao") and x["licao"]["chave"].startswith(x["id"] + ":")
    h = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    assert '<div class="medidas">${medidas(et)}${pulso(et)}</div>' in h and "med-rel" in h and "med-num" in h
    assert 'ghDispatch("ciente.yml"' in h and Path(".github/workflows/ciente.yml").exists()


def test_os_relogios_que_existiam_continuam():
    """09/11/2026 (titular: «mantenha os que existiam antes»): todo instrumento com escala própria continua relógio — a
    etapa 8 com os seis (discernimento, precisão, revocação, Brier, o Comandante contra a ordem fixa e as decisões)."""
    d = _sala()
    for x in d["instrumentos"]:
        e = x.get("escala")
        if e and e[1] > e[0] and isinstance(x.get("valor"), (int, float)):
            assert x.get("relogio"), x["id"]
    assert {"rn_auc", "rn_precisao", "rn_revocacao", "rn_brier", "cm_comparacao", "cm_decisoes"} <= set(sala.RELOGIOS["aprendizado"])
