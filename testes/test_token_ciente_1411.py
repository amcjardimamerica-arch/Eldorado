"""R56 (titular, 14/11/2026: «reiniciei o token 3 vezes e não aceitou»): o token do GitHub na página da Sala."""
import re
import subprocess
from pathlib import Path

PAG = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
T = "github_pat_11ABCDEFG0123456789_abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUV"


def _extrair(texto: str) -> str:
    fn = re.search(r"window\.ghExtrair=(function\(texto\)\{.*?\});", PAG).group(1)
    js = f"const f={fn};process.stdout.write(f({texto!r}.replace(/\\\\n/g,'\\n')))"
    return subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout


def test_o_token_colado_como_veio_e_aproveitado_inteiro():
    for colado in (T, f" {T} ", f'"{T}"', f"`{T}`", f"Token: {T}", f"{T[:40]}\\n{T[40:]}"):
        assert _extrair(colado) == T, colado
    assert _extrair("não é token") == ""


def test_a_mensagem_pelo_motivo_e_o_token_so_some_no_401():
    assert "token inválido ou vencido: gere outro" in PAG and "o token não tem a permissão Actions: Read and write" in PAG
    assert "o token não alcança o repositório Eldorado" in PAG
    i = PAG.index("window.ghDispatch=async function")
    corpo = PAG[i:PAG.index("window.mtImediato", i)]
    assert 'if(r.status===401){ try{ localStorage.removeItem("eldorado_gh_token")' in corpo and "r.status===403){ try{ localStorage.removeItem" not in corpo


def test_o_token_e_conferido_antes_de_guardar_e_ha_o_botao_de_trocar():
    i = PAG.index("window.ghToken=async function")
    corpo = PAG[i:PAG.index("window.ghTrocarToken", i)]
    assert corpo.index("await ghConferir(t)") < corpo.index('localStorage.setItem("eldorado_gh_token",t)')
    assert "actions/workflows/ciente.yml" in PAG and "api.github.com/user" in PAG and "github-authentication-token-expiration" in PAG
    assert "ghTrocarToken()" in PAG and "como gerar o token" in PAG
