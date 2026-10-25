"""O mapa dos arquivos da sala de controle (titular, 25/10/2026: "veja se os arquivos novos e fluxos estão descritos no
mapa"): todo arquivo das pastas do sistema está no mapa, com a finalidade descrita e alcançado pela produção."""
from pathlib import Path

from eldorado.base.cerebro.mapa_arquivos import finalidade, montar

PASTAS = [("eldorado", "*.py"), ("config", "*.*"), ("workflows", "*.toml"), (".github/workflows", "*.yml"), ("skills", "*/SKILL.md"),
          ("estudos", "*.py"), ("ponte", "*.php")]


def test_todo_arquivo_do_sistema_esta_no_mapa_com_finalidade():
    m = montar()
    nos = {n["id"]: n for n in m["nos"]}
    arquivos = [p.as_posix() for pasta, padrao in PASTAS for p in Path(pasta).rglob(padrao) if "__pycache__" not in p.parts]
    fora = [a for a in arquivos if a not in nos]
    sem = [a for a in arquivos if a in nos and not finalidade(a).strip()]
    assert not fora, f"fora do mapa: {fora[:8]}"
    assert not sem, f"sem a finalidade descrita: {sem[:8]}"
    for novo in ("eldorado/base/comandante/escolher.py", "eldorado/base/aprendizado/curador.py", "skills/espiao-missao/SKILL.md",
                 "config/cargos.toml", "ponte/ponte.php"):
        assert nos[novo]["alcancado"], novo
