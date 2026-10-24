"""O teste-mestre das regras da titular (config/regras_titular.json): nenhuma regra sem trava, nenhuma trava inexistente,
e a regra com prazo vencido é revista. Se alguém tirar uma trava ou apagar o teste, a bateria falha."""
import json
import re
from pathlib import Path

REGISTRO = json.loads(Path("config/regras_titular.json").read_text(encoding="utf-8"))


def test_toda_regra_tem_data_texto_e_trava():
    sem = [r["id"] for r in REGISTRO["regras"] if r.get("situacao") != "processo" and not r.get("travas")]
    assert not sem, f"regra sem trava: {sem}"
    for r in REGISTRO["regras"]:
        assert re.fullmatch(r"R\d{2}", r["id"]) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", r["data"]) and len(r["regra"]) > 20, r["id"]
    ids = [r["id"] for r in REGISTRO["regras"]]
    assert len(ids) == len(set(ids))


def test_toda_trava_existe():
    faltam = []
    for r in REGISTRO["regras"]:
        for t in r.get("travas", []):
            arq, _, func = t.partition("::")
            p = Path(arq)
            if not p.exists() or not re.search(rf"^def {re.escape(func)}\(", p.read_text(encoding="utf-8"), re.M):
                faltam.append(f"{r['id']}: {t}")
    assert not faltam, f"trava inexistente: {faltam}"


def test_regra_com_prazo_vencido_e_revista():
    """A regra com prazo (como a R01, até a eliminação do Eldorado0) falha na data, para ser revista e não esquecida."""
    from datetime import date
    vencidas = [f"{r['id']} (venceu em {r['expira_em']}: {r.get('condicao', '')})" for r in REGISTRO["regras"]
                if r.get("expira_em") and date.fromisoformat(r["expira_em"]) < date.today()]
    assert not vencidas, f"regra vencida: a titular decide a remoção ou a prorrogação: {vencidas}"
