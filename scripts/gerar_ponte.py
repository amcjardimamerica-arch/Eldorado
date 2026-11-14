"""14/11/2026 (R56, S6): gera a lista DOMINIOS do ponte/ponte.php a partir de config/ponte_dominios.txt (os sites que recusam
a nuvem, lidos direto pela ponte) e config/ponte_base.txt (os que a ponte já atendia). Uso: python scripts/gerar_ponte.py"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def dominios() -> list[str]:
    sys.path.insert(0, str(RAIZ))
    from eldorado.motores.acesso.ponte_br import dominios_da_ponte
    return dominios_da_ponte()


def gerar(php: str) -> str:
    corpo = "const DOMINIOS = [\n" + "".join(f"    '{d}',\n" for d in dominios())
    return re.sub(r"const DOMINIOS = \[\n.*?\n\];", lambda _m: corpo + "];", php, count=1, flags=re.S)


if __name__ == "__main__":
    p = RAIZ / "ponte" / "ponte.php"
    atual = p.read_text(encoding="utf-8")
    novo = gerar(atual)
    if "--conferir" in sys.argv:                     # a Qualidade: o ponte.php tem de estar igual à lista do sistema
        if novo != atual:
            sys.exit("ponte.php fora de sincronia com config/ponte_dominios.txt e config/ponte_base.txt: rode python scripts/gerar_ponte.py")
        print(f"ponte.php em sincronia: {len(dominios())} domínios", file=sys.stderr)
    else:
        p.write_text(novo, encoding="utf-8")
        print(f"ponte.php: {len(dominios())} domínios", file=sys.stderr)
