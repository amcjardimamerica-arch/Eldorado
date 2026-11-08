"""TRAVA do contrato dos eventos (07/11/2026): nenhum módulo emite um evento que o banco recusaria.

Origem: os alertas recorrentes "evento recusado (medicao.registrada, …): CHECK constraint failed: nivel IN (…)" na Sala
— nivel="etapa" (29/10/2026) e nivel="aprendizado" do ciclo dos pilotos (06/11/2026: 390 eventos, 322 alarmes, e o
ciclo rodando a cada passagem porque a marca dele nunca chegava ao banco). Esta trava pega o erro no envio.
"""
from __future__ import annotations

import ast
import json
import sqlite3
from pathlib import Path

import pytest

from eldorado.base.nucleo import contrato_eventos as C
from eldorado.base.nucleo.eventos import CATALOGO, NIVEIS_MEDICAO, Diario, criar

RAIZ = Path(__file__).resolve().parent.parent


def _chamadas_emitir():
    """Toda chamada X.emitir("tipo", modulo, {...}) do sistema, com os valores literais do dicionário."""
    for arq in sorted((RAIZ / "eldorado").rglob("*.py")):
        try:
            arvore = ast.parse(arq.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for no in ast.walk(arvore):
            if not (isinstance(no, ast.Call) and isinstance(no.func, ast.Attribute) and no.func.attr in ("emitir", "emitir_se_mudou")):
                continue
            args = list(no.args)
            if no.func.attr == "emitir_se_mudou":
                args = args[1:]   # emitir_se_mudou(diario, tipo, modulo, chave, dados)
            if not args or not isinstance(args[0], ast.Constant) or not isinstance(args[0].value, str):
                continue
            tipo = args[0].value
            dic = next((a for a in args[1:] if isinstance(a, ast.Dict)), None)
            if dic is None:
                continue
            literais = {k.value: v.value for k, v in zip(dic.keys, dic.values, strict=False)
                        if isinstance(k, ast.Constant) and isinstance(v, ast.Constant)}
            if literais:
                yield f"{arq.relative_to(RAIZ)}:{no.lineno}", tipo, literais


def test_toda_emissao_literal_respeita_o_banco():
    erros = []
    for onde, tipo, literais in _chamadas_emitir():
        if tipo not in CATALOGO:
            continue
        for alvo in CATALOGO[tipo]:
            cols = set(C._colunas(alvo.banco, alvo.tabela))
            for campo, valor in literais.items():
                if campo not in cols or valor is None:
                    continue
                permitidos = C.valores_permitidos(alvo.banco, alvo.tabela, campo)
                if permitidos is not None and str(valor) not in permitidos:
                    erros.append(f"{onde}: {tipo} com {campo}={valor!r}; o banco ({alvo.banco}.{alvo.tabela}) aceita {sorted(permitidos)}")
    assert not erros, "eventos que o banco recusaria:\n" + "\n".join(erros)


def test_a_lista_de_niveis_e_a_do_esquema():
    assert C.valores_permitidos("cerebro", "medicao", "nivel") == set(NIVEIS_MEDICAO)


def test_o_contrato_barra_o_evento_na_emissao(tmp_path, monkeypatch):
    monkeypatch.setenv("ELDORADO_CONTRATO_EVENTOS", "estrito")
    d = Diario(tmp_path / "eventos")
    with pytest.raises(C.EventoForaDoContrato, match="nivel"):
        d.emitir("medicao.registrada", "ciclo-pilotos", {"marcador": "ciclo:espiao", "nivel": "aprendizado", "em": "2026-11-07T00:00:00+00:00",
                                                         "valor": 1})
    d.emitir("medicao.registrada", "ciclo-pilotos", {"marcador": "ciclo:espiao", "nivel": "componente", "em": "2026-11-07T00:00:00+00:00",
                                                     "valor": 1})


def test_fora_do_modo_estrito_o_evento_segue_gravado(tmp_path, monkeypatch):
    monkeypatch.setenv("ELDORADO_CONTRATO_EVENTOS", "")
    d = Diario(tmp_path / "eventos")
    ev = d.emitir("medicao.registrada", "x", {"marcador": "m", "nivel": "outro", "em": "2026-11-07T00:00:00+00:00", "valor": 1})
    assert ev.tipo == "medicao.registrada"   # o dado não se perde; o catálogo o grava como "componente"


def test_o_legado_ja_gravado_entra_e_o_ciclo_le_a_sua_marca(gravador, bancos):
    """Os 390 eventos de 06–07/11 (nivel="aprendizado") entram no Cérebro na remontagem; com a marca no banco, o ciclo
    dos pilotos deixa de rodar a cada passagem e a orientação dele (fatores e preferência) passa a valer."""
    from eldorado.base.cerebro import ciclo_pilotos

    orient = {"fatores": {"internacional_espanhol": 1.4}}
    ev = criar("medicao.registrada", "ciclo-pilotos", {"marcador": "ciclo:espiao", "nivel": "aprendizado", "em": "2026-11-06T23:00:39+00:00",
                                                       "valor": 12321, "motivo": json.dumps(orient)})
    r = gravador.aplicar([ev])
    assert not r.recusados
    cer: sqlite3.Connection = bancos["cerebro"]
    assert ciclo_pilotos.ultimo(cer, "espiao")[0] == 12321
    assert ciclo_pilotos.fator_familia(cer, "internacional_espanhol") == 1.4


def test_o_ciclo_dos_pilotos_emite_o_nivel_do_banco():
    fonte = (RAIZ / "eldorado/base/cerebro/ciclo_pilotos.py").read_text(encoding="utf-8")
    assert '"nivel": "aprendizado"' not in fonte
