"""As bibliotecas do plano, em camadas independentes (scripts/instalar.sh): o núcleo é obrigatório; cada grupo do plano
é tentado sozinho, e o grupo que falhar é instalado pacote por pacote; cada pacote que não instalar vira aviso com o
nome. Assim, um pacote que não instala nunca derruba os outros (o defeito de 23/10/2026: um bloco só, nada instalado)."""
import subprocess
import sys
import time
import tomllib

NUCLEO = ["leitura", "acesso", "descoberta", "metabusca", "navegador"]
GRUPOS = ["ocr", "universal", "idioma", "leitura_completa", "base", "banco", "motores"]


def instalar(alvo: list[str], tempo: int) -> bool:
    cmd = ["uv", "pip", "install", "--system", "-q", *alvo]
    try:
        return subprocess.run(cmd, timeout=tempo, capture_output=True, text=True).returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        cmd = [sys.executable, "-m", "pip", "install", "-q", *alvo]
        try:
            return subprocess.run(cmd, timeout=tempo, capture_output=True, text=True).returncode == 0
        except subprocess.TimeoutExpired:
            return False


def main() -> int:
    extras = tomllib.load(open("pyproject.toml", "rb"))["project"]["optional-dependencies"]
    t = time.time()
    if not instalar(["-e", f".[{','.join(NUCLEO)}]"], 900):
        print("::error::o núcleo do Eldorado não instalou (leitura, acesso, descoberta, metabusca, navegador)")
        return 1
    tempos = [f"núcleo={int(time.time() - t)}s"]
    falharam = []
    for g in GRUPOS:
        t = time.time()
        if instalar([*extras[g]], 600):
            tempos.append(f"{g}={int(time.time() - t)}s")
            continue
        for pacote in extras[g]:                      # o grupo falhou: um por um, para achar o culpado
            if not instalar([pacote], 300):
                falharam.append(pacote)
                print(f"::warning::pacote do plano não instalou: {pacote} (grupo {g})")
    print(f"::notice::bibliotecas: grupos {' '.join(tempos)}; {len(falharam)} pacote(s) não instalaram" + (f": {', '.join(falharam)}" if falharam else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
