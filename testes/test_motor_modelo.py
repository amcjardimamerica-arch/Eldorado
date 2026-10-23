"""O motor modelo (titular, 23/10/2026): a fórmula dos motores; contém toda ferramenta do sistema; não roda nem aparece."""
import json
import re
import tomllib
import typing
from pathlib import Path

from eldorado.motores.canal import motor as M

MODELO = Path("eldorado/base/motor_modelo/modelo.toml")


def test_o_modelo_contem_toda_ferramenta_da_configuracao():
    """Ferramenta nova sem estar no modelo: esta trava falha (a regra da titular)."""
    texto = MODELO.read_text(encoding="utf-8")
    faltam = []
    for nome in [n for n in dir(M) if n.startswith("Cfg")] + ["Configuracao"]:
        for campo in getattr(M, nome).model_fields:
            if not re.search(rf"(^|\W){re.escape(campo)}\s*=|\[{re.escape(campo)}\]|\[\[{re.escape(campo)}\]\]|\[\w+\.{re.escape(campo)}\]", texto, re.M):
                faltam.append(f"{nome}.{campo}")
    opcoes = {"tipo de rota": typing.get_args(M.CfgFonte.model_fields["tipo"].annotation),
              "formato de elo": typing.get_args(M.CfgElo.model_fields["formato"].annotation),
              "degrau": typing.get_args(typing.get_args(M.CfgAcesso.model_fields["degraus"].annotation)[0])}
    for o, valores in opcoes.items():
        faltam += [f"{o} {v}" for v in valores if not re.search(rf"\b{v}\b", texto)]
    faltam += [f"canivete {h}" for h in M.CfgCanivete().habilidades() if f"{h} = " not in texto]
    assert not faltam, f"acrescente ao motor modelo: {faltam}"


def test_um_motor_criado_do_modelo_e_aceito(tmp_path):
    from eldorado.motores.canal.fabrica import criar, validar
    p = criar("do-goias", pasta=tmp_path)
    d = tomllib.loads(p.read_text(encoding="utf-8"))
    assert d["motor"]["id"] == "do-goias" and d["acesso"]["degraus"][-1] == "local" and d["canivete"]["ligado"] is True
    assert "«" not in p.read_text(encoding="utf-8")                                              # nenhum marcador sobrou
    assert dict((n, ok) for n, ok, _ in validar("do-goias", pasta=tmp_path))["aceito pelo registro"]


def test_o_modelo_nao_e_um_motor_do_sistema():
    assert not (Path("eldorado/motores/canal/config") / "modelo.toml").exists()
    assert "motor_modelo" not in Path("config/modulos.toml").read_text(encoding="utf-8")
    ids = {m["id"] for m in json.loads(Path("config/motores_previstos.json").read_text(encoding="utf-8"))["motores"]}
    assert "modelo" not in ids and "«id»" not in ids
