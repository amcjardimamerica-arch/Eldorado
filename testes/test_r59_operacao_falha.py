"""17/11/2026 (titular, R59): operação é a condição do sistema funcionando; falha é o impedimento. Fila e dado parado à espera
do Claude no Chrome ou da titular são indicadores de operação — aparecem com cor própria, pedem só o ciente e não pintam a
etapa, a Regência nem o índice de saúde."""
import json
import shutil
from pathlib import Path

from eldorado.base.painel.sala import OPERACAO, efetivo


def _sala(tmp_path):
    from eldorado.base.painel import vivo
    raiz = tmp_path / "sv"
    (raiz / "dados").mkdir(parents=True)
    for n in ("biblioteca", "cerebro"):
        shutil.copy(f"dados/{n}.db", raiz / "dados" / f"{n}.db")
    for d in ("config", "eldorado", "eventos", "workflows", "scripts", ".github", "skills", "verificacao", "estudos", "ponte", "testes"):
        if Path(d).exists():
            (raiz / d).symlink_to(Path(d).resolve())
    vivo.medir_e_gravar(raiz, ciclo=7)
    return json.loads((raiz / "painel_vivo/sala_controle.json").read_text(encoding="utf-8"))


def test_todo_instrumento_tem_a_classe_declarada(tmp_path):
    s = _sala(tmp_path)
    inst = s["instrumentos"]
    assert inst and all(x.get("classe") in ("operacao", "falha") for x in (inst.values() if isinstance(inst, dict) else inst))
    assert {"ve_para_o_chrome", "de_decisoes", "es_expurgo", "fa_fecham_7d", "ab_link_oficial"} <= OPERACAO


def test_fila_do_chrome_acima_do_limite_nao_tira_a_etapa_externa_do_verde():
    assert efetivo({"classe": "operacao", "estado": "amarelo"}) == "verde"
    assert efetivo({"classe": "operacao", "estado": "vermelho"}) == "verde"


def test_instrumento_de_falha_amarelo_tira_a_etapa_do_verde():
    assert efetivo({"classe": "falha", "estado": "amarelo"}) == "amarelo"
    assert efetivo({"classe": "falha", "estado": "vermelho"}) == "vermelho"
