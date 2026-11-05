"""R45 (titular, 05/11/2026): nenhum indicador positivo sem a leitura real — o Mapa dos arquivos."""
from pathlib import Path

S = Path("eldorado/base/cerebro/mapa_arquivos.py").read_text(encoding="utf-8")


def test_o_motor_com_sinal_nao_e_verde_no_mapa():
    assert "from .sinais_motores import sinais as _sinais" in S and 'sg["luz"] in ("amarelo", "vermelho")' in S


def test_a_heranca_e_as_ligacoes_sem_falso_verde():
    assert 'circ[p] = "v" if all(h == "v" for h in herd)' in S and '"v" if "v" in herd' not in S
    assert "def _lig(x: str, y: str)" in S and 'ponto[p] = "v" if (passagem_ok and usuarios_ok) else "c"' in S
