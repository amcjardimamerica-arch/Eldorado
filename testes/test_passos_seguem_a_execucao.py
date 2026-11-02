"""02/11/2026 (titular: "evento recusado (execucao.passo…)" voltando à Sala): a telemetria de uma passagem (operacao/) subia
ao repositório antes do execucao.iniciada (retido no histórico enquanto a passagem não termina, pela R09); o Painel remontava
o Cérebro a partir do repositório e recusava os passos (FOREIGN KEY). Agora os passos seguem a execução."""

import gzip
import json
import subprocess
from pathlib import Path

from eldorado.base.nucleo.eventos import Diario, pasta_operacao

SCRIPT = Path("scripts/gravar.sh").resolve()


def _completo(raiz: Path, arquivo: str) -> bool:
    texto = SCRIPT.read_text(encoding="utf-8")
    funcao = texto[texto.index("completo() {") : texto.index("LISTA=$(mktemp)")]
    r = subprocess.run(["bash", "-c", funcao + f'\ncompleto "{arquivo}"'], cwd=raiz)
    return r.returncode == 0


def _linha(tipo: str) -> str:
    return json.dumps({"id": "x", "tipo": tipo, "dados": {}}) + "\n"


def test_os_passos_so_sobem_com_a_execucao_terminada(tmp_path):
    ex = "01793613463162884423-017199-5bed8764"
    ev = tmp_path / "eventos/2026/11/02" / f"{ex}.jsonl"
    op = tmp_path / "operacao/2026/11/02" / f"{ex}.jsonl"
    ev.parent.mkdir(parents=True)
    op.parent.mkdir(parents=True)
    ev.write_text(_linha("execucao.iniciada"))
    op.write_text(_linha("execucao.passo") * 3)
    alvo = f"operacao/2026/11/02/{ex}.jsonl"
    assert not _completo(tmp_path, alvo)  # em andamento: os passos esperam
    ontem = tmp_path / "eventos/2026/11/01" / f"{ex}.jsonl"  # a execução que atravessou o dia
    ontem.parent.mkdir(parents=True)
    ontem.write_text(_linha("execucao.iniciada"))
    ev.write_text(_linha("workflow.versao"))
    assert not _completo(tmp_path, alvo)
    ev.write_text(_linha("execucao.concluida"))
    assert _completo(tmp_path, alvo)  # terminada: sobem juntos
    sozinho = tmp_path / "operacao/2026/11/02/medicoes-avulsas.jsonl"  # a telemetria sem execução: sobe
    sozinho.write_text(_linha("medicao.registrada"))
    assert _completo(tmp_path, "operacao/2026/11/02/medicoes-avulsas.jsonl")


def test_a_retomada_le_os_passos_compactados(tmp_path):
    pasta = tmp_path / "eventos"
    d = Diario(pasta, "exec-9")
    d.emitir("execucao.passo", "executor", {"execucao": "exec-9", "passo": 0, "no": "_entrada", "estado": "concluido", "saida": []})
    arq = next(pasta_operacao(pasta).rglob("exec-9.jsonl"))
    ontem = pasta_operacao(pasta) / "2026" / "01" / "01" / "exec-9.jsonl.gz"
    ontem.parent.mkdir(parents=True)
    ontem.write_bytes(gzip.compress(arq.read_bytes().replace(b'"passo":0', b'"passo":7')))
    passos = sorted(e.dados["passo"] for e in d.eventos() if e.tipo == "execucao.passo")
    assert passos == [0, 7]


def test_o_passo_antes_da_execucao_nao_vira_alarme():
    fonte = Path("eldorado/base/nucleo/gravador.py").read_text(encoding="utf-8")
    assert 'if ev.tipo == "execucao.passo" and "FOREIGN KEY" in motivo:' in fonte
