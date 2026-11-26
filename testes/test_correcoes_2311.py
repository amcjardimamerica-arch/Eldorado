"""Manutenção de 23/11/2026 — as correções do relatório (C-01 a C-10)."""
import json
import re
from pathlib import Path


def _config(tmp_path):
    s = Path("config/eldorado.toml").read_text(encoding="utf-8")
    s = re.sub(r'(?m)^dados\s*=.*$', f'dados = "{tmp_path / "dados"}"', s)
    s = re.sub(r'(?m)^eventos\s*=.*$', f'eventos = "{tmp_path / "eventos"}"', s)
    (tmp_path / "eldorado.toml").write_text(s, encoding="utf-8")
    (tmp_path / "dados").mkdir()
    return tmp_path / "eldorado.toml"


def _lei(diario, n):
    diario.emitir("lei.registrada", "teste", {"id": f"L{n}", "esfera": "federal", "numero": f"Lei {n}", "ementa": "x", "situacao": "vigente",
                                              "link_oficial": None, "atualizada_em": "2026-11-23"})


def _aplicar(comandos, cfg):
    import pytest
    import typer
    with pytest.raises(typer.Exit) as fim:
        comandos.aplicar(cfg)
    assert fim.value.exit_code == 0                         # nenhum evento recusado


def test_a_execucao_restaura_os_bancos_da_anterior_e_aplica_so_os_eventos_novos(tmp_path):
    """C-01: com os bancos e a marca dados/aplicados.json da execução anterior, o aplicar lê só os arquivos novos."""
    from eldorado.base.nucleo import comandos
    cfg = _config(tmp_path)
    from eldorado.base.nucleo.eventos import Diario
    _lei(Diario(tmp_path / "eventos", "execucao-a"), 1)
    _aplicar(comandos, cfg)                                 # a «execução anterior»: aplica e marca
    marca = json.loads((tmp_path / "dados" / "aplicados.json").read_text(encoding="utf-8"))
    assert any("execucao-a" in k for k in marca["arquivos"])
    _lei(Diario(tmp_path / "eventos", "execucao-b"), 2)
    lidos = []
    import eldorado.base.nucleo.eventos as ev
    ler_original = ev.ler

    def espia(raiz, **k):
        for x in ler_original(raiz, **k):
            lidos.append(x)
            yield x
    comandos_ler = getattr(comandos, "ler", None)
    try:
        comandos.ler = espia
        _aplicar(comandos, cfg)                             # a execução seguinte, com os bancos e a marca guardados
    finally:
        if comandos_ler is not None:
            comandos.ler = comandos_ler
    assert [x.dados["id"] for x in lidos] == ["L2"]         # só o arquivo novo


def test_o_fluxo_restaura_a_guarda_antes_de_iniciar_e_salva_sempre():
    """C-01: o YAML tem o passo de restaurar antes de «eldorado iniciar» e o de salvar com if: always()."""
    import yaml
    passos = yaml.safe_load(Path(".github/workflows/eldorado.yml").read_text(encoding="utf-8"))["jobs"]["passagem"]["steps"]
    nomes = [p.get("uses", "") + "|" + p.get("run", "") for p in passos]
    restaura = next(i for i, n in enumerate(nomes) if "actions/cache/restore" in n)
    inicia = next(i for i, n in enumerate(nomes) if "eldorado iniciar" in n)
    assert restaura < inicia
    fim = [p for p in passos if "actions/cache/save" in p.get("uses", "") and p.get("with", {}).get("key", "").endswith("-fim")]
    assert fim and fim[0].get("if") == "always()" and "dados/aplicados.json" in fim[0]["with"]["path"]
    assert sum("actions/cache/save" in p.get("uses", "") for p in passos) == 6               # 5 blocos de hora e o fim


def test_a_avaliacao_herdada_sem_porque_ganha_o_motivo_e_nao_derruba_o_ranking(tmp_path):
    """23/11/2026: na produção, a empresa com a ficha do Eldorado0 (coluna que o banco de amostra não tem) e a avaliação
    herdada sem «porque» derrubava o ranking — a trava caía no portão das regras e o sistema parou desde a madrugada de 23/11."""
    import shutil
    import sqlite3

    from eldorado.base.painel.dados import _molde
    from eldorado.base.painel.ranking import montar
    shutil.copy("dados/biblioteca.db", tmp_path / "b.db")
    con = sqlite3.connect(tmp_path / "b.db")
    if "ficha" not in {r[1] for r in con.execute("PRAGMA table_info(empresa)")}:
        con.execute("ALTER TABLE empresa ADD COLUMN ficha TEXT")
    cnpj = con.execute("SELECT cnpj FROM empresa LIMIT 1").fetchone()[0]
    con.execute("UPDATE empresa SET ficha = ? WHERE cnpj = ?",
                (json.dumps({"eldorado0": {"pontos_lista": 999, "pontuacao": {"base": 90}, "nivel": "ouro"}}), cnpj))
    con.commit()
    r = montar(con, _molde)
    e = next(x for x in r["empresas"] if x["pontos_lista"] == 999)                     # a empresa da ficha herdada
    assert "Eldorado0" in e["pontuacao"]["porque"]
    assert all(x["pontuacao"]["porque"] for x in r["empresas"])


def test_todo_passo_antes_do_laco_tem_limite_de_tempo():
    """C-02: uma execução ficou 11 h sem passagem — todo passo antes do laço tem timeout-minutes."""
    import yaml
    passos = yaml.safe_load(Path(".github/workflows/eldorado.yml").read_text(encoding="utf-8"))["jobs"]["passagem"]["steps"]
    i_laco = next(i for i, p in enumerate(passos) if p.get("name", "").startswith("Funcionamento permanente"))
    sem = [p.get("name") for p in passos[:i_laco] if "run" in p and "timeout-minutes" not in p
           and not p.get("name", "").startswith(("A hora do começo", "Conferir a guarda"))]
    assert sem == [], f"passos sem limite de tempo: {sem}"
    reaplicar = next(p for p in passos if p.get("name") == "Reaplicar os eventos pendentes")
    assert "45" in str(reaplicar["timeout-minutes"]) and "240" in str(reaplicar["timeout-minutes"])   # com e sem a guarda


def test_o_vigia_cancela_e_religa_o_ciclo_travado():
    """C-02: o vigia só religava sem ciclo nenhum; o ciclo travado (gravação e execução há mais de 90 min) é cancelado e
    religado — e a remontagem sem guarda (Reaplicar, até 240 min) não é travamento."""
    import yaml
    run = yaml.safe_load(Path(".github/workflows/vigia.yml").read_text(encoding="utf-8"))["jobs"]["vigiar"]["steps"][0]["run"]
    assert '[ "$idade" -gt 90 ] && [ "$idade_ciclo" -gt 90 ]' in run and 'gh run cancel "$run_id"' in run
    assert '"Reaplicar os eventos pendentes"*)' in run and "o passo em curso" in run


def _painel():
    import yaml
    return yaml.safe_load(Path(".github/workflows/painel.yml").read_text(encoding="utf-8"))["jobs"]["publicar"]["steps"]


def test_a_chave_da_guarda_do_painel_nao_expira_por_semana_nem_por_codigo():
    """C-03: a chave mudava a cada semana e a cada mudança de código — na segunda-feira a guarda zerou e o site parou."""
    texto = Path(".github/workflows/painel.yml").read_text(encoding="utf-8")
    assert "hashFiles(" not in texto and "semana.outputs" not in texto
    rest = next(p for p in _painel() if "actions/cache/restore" in p.get("uses", ""))
    assert rest["with"]["key"] == "painel-bancos-${{ github.run_id }}"
    assert rest["with"]["restore-keys"].split() == ["eldorado-bancos-", "painel-bancos-"]     # a guarda do ciclo primeiro


def test_o_site_publica_com_a_sala_da_producao_quando_a_aplicacao_nao_termina():
    """C-03: a aplicação que não cabe no tempo não impede a publicação — os livros voltam à guarda (coerentes, sem números
    misturados) e a tela avisa a hora deles; a Sala é a medida pela produção."""
    import inspect

    from eldorado.base.painel import dados
    passos = _painel()
    nomes = [p.get("name", "") for p in passos]
    ap = passos[nomes.index("Os eventos mais recentes no banco (o estado de agora)")]
    assert ap.get("continue-on-error") is True and ap.get("timeout-minutes") == 12
    volta = next(p for p in passos if "ELDORADO_LIVROS_DE" in p.get("run", ""))
    assert "steps.aplicar.outcome != 'success'" in volta["if"] and "/tmp/guarda_antes/biblioteca.db" in volta["run"]
    gera = next(p for p in passos if p.get("name", "").startswith("Gerar o site"))
    assert "if" not in gera                                                                   # publica sempre
    assert 'os.environ.get("ELDORADO_LIVROS_DE")' in inspect.getsource(dados.gerar)


def _aplicar_eventos(tmp_path, emitir):
    import sqlite3

    import typer

    from eldorado.base.nucleo import comandos
    from eldorado.base.nucleo.eventos import Diario
    cfg = _config(tmp_path)
    emitir(Diario(tmp_path / "eventos", "teste"))
    try:
        comandos.aplicar(cfg)
    except typer.Exit:
        pass
    return sqlite3.connect(tmp_path / "dados" / "cerebro.db")


def test_a_ia_pendente_para_na_terceira_tentativa_e_nao_gera_evento_recusado(tmp_path):
    """C-04: a quarta tentativa «ia pendente» era recusada pelo banco (1 a 3) e abria alarme — a pendência para na terceira
    (a abordagem passa a contar como tentada) e o evento antigo com a quarta é dispensado, sem alarme."""
    import inspect

    from eldorado.motores.pilotos import interceptador
    fonte = inspect.getsource(interceptador)
    assert 'if ferr.startswith("ia pendente") and self._numero(lv.id, ferr) >= 3:' in fonte and "if numero > 3:" in fonte

    def emitir(d):
        d.emitir("tentativa.registrada", "interceptador", {"livro_id": "L1", "fase": "preparacao", "ferramenta": "ia pendente · abordagem 2",
                                                           "numero": 4, "em": "2026-11-23T10:00:00+00:00", "resultado": "{}", "proxima_em": None})
    cer = _aplicar_eventos(tmp_path, emitir)
    assert cer.execute("SELECT COUNT(*) FROM alarme WHERE mensagem LIKE 'evento recusado (tentativa.registrada%'").fetchone()[0] == 0


def test_recusas_iguais_do_gravador_sao_uma_causa_so_na_sala(tmp_path):
    """C-04: 48 recusas iguais abriam 48 alarmes (o código do evento na causa) — a mesma causa tem um alarme só."""
    def emitir(d):
        for ano in (2024, 2025, 2026):
            d.emitir("incentivo.registrado", "teste", {"cnpj": "1", "lei": "LEI-QUE-NAO-EXISTE", "ano": ano, "valor": None, "comprovado": 1,
                                                        "fonte": "x", "em": "2026-11-23T10:00:00+00:00"})
    cer = _aplicar_eventos(tmp_path, emitir)
    assert cer.execute("SELECT COUNT(*) FROM alarme WHERE fechado_em IS NULL AND mensagem LIKE 'evento recusado (incentivo.registrado%'").fetchone()[0] == 1


def test_o_laco_sai_limpo_no_actions_depois_de_gravar(monkeypatch):
    """26/11/2026: o bloco do laço, já concluído e gravado, abortava na saída (código 134) com uma linha de execução em
    segundo plano viva — no GitHub Actions a saída é direta; fora dele (os testes), nada muda."""
    import inspect

    from eldorado.base.nucleo import comandos
    monkeypatch.delenv("ELDORADO_SAIDA_DIRETA", raising=False)
    assert comandos._sair_limpo() is None                                     # sem a variável (os testes): segue normal
    import yaml
    passos = yaml.safe_load(Path(".github/workflows/eldorado.yml").read_text(encoding="utf-8"))["jobs"]["passagem"]["steps"]
    blocos = [p for p in passos if "eldorado permanente" in str(p.get("run", ""))]
    assert blocos and all(b["env"].get("ELDORADO_SAIDA_DIRETA") == "1" for b in blocos)
    fonte = inspect.getsource(comandos.permanente)
    assert fonte.index("gravar_agora(esperar=True)") < fonte.index("_sair_limpo()")   # sai só depois de gravar


def test_o_no_originais_respeita_o_orcamento_mesmo_com_lei_que_nao_responde():
    """C-06: uma passagem ficou 2 h 55 presa no nó «originais» — a lei que não responde fica para a próxima passagem."""
    import sqlite3
    import time
    from datetime import datetime, timezone

    from eldorado.base.cartorio.leis import acompanhar
    b = sqlite3.connect(":memory:")
    b.execute("CREATE TABLE lei(id TEXT, esfera TEXT, numero TEXT, ementa TEXT, situacao TEXT, link_oficial TEXT, atualizada_em TEXT)")
    b.executemany("INSERT INTO lei VALUES (?, 'federal', ?, 'x', 'vigente', ?, '2026-10-22')", [(f"L{i}", f"Lei {i}", f"https://x/{i}") for i in range(4)])

    def lenta(url):
        time.sleep(30)                                   # a lei que nunca responde
    t0 = time.monotonic()
    r = acompanhar(b, _D(), lenta, datetime(2026, 11, 23, tzinfo=timezone.utc), orcamento_s=2, limite_lei_s=0.5)
    assert time.monotonic() - t0 < 4 and r["conferidas"] == 0 and r["adiadas"] == 4


class _D:
    def __init__(self):
        self.ev = []

    def emitir(self, tipo, origem, dados):
        self.ev.append(tipo)


def test_erro_do_leitor_de_audio_nao_derruba_o_voo_do_espiao(tmp_path):
    """C-07: o erro de um leitor (o mesmo TypeError do av) não encerra o voo — a pista é pulada e o erro fica na missão."""
    import json
    import random

    from eldorado.motores.descoberta.pistas import Pista
    from eldorado.motores.pilotos.espiao import Espiao

    def leitor_quebrado(url):
        raise TypeError("open() got an unexpected keyword argument 'metadata_errors'")
    pistas = [Pista(titulo="Edital de chamamento para OSC", link="https://exemplo.org/edital.mp4", origem="busca")]
    e = Espiao(tmp_path / "c.db", lambda q: (pistas, ["searxng: 1 pista(s)"]), leitor_quebrado, rnd=random.Random(1))
    m = e.missao()                                                             # não levanta
    motivos = json.loads(e.con.execute("SELECT motivos FROM espiao_missao ORDER BY id DESC LIMIT 1").fetchone()[0])
    assert m is not None and any("erro do leitor (TypeError" in k for k in motivos)


def test_item_sem_id_e_separado_e_nao_derruba_o_decidir_rede():
    """C-09: um item sem id (o {"leis": …} que o nó dos originais punha na saída) derrubava o decidir_rede — o item inválido
    é separado, com alarme, e os demais seguem; e o nó dos originais não põe mais nada além de achados na saída."""
    import inspect
    from types import SimpleNamespace

    from eldorado.base.cerebro import encaminhamento
    from eldorado.base.cerebro.pertinencia import no_decidir

    class Diario:
        def __init__(self):
            self.ev = []

        def emitir(self, tipo, origem, dados):
            self.ev.append((tipo, dados))
            return SimpleNamespace(id="x")
    d = Diario()
    saida = no_decidir([{"leis": {"conferidas": 1}}], {"missao": "eldorado.base.missao.oportunidades:MissaoOportunidades"},
                       SimpleNamespace(diario=d))
    assert saida == [] and any(t == "alarme.aberto" and "item inválido separado" in x["mensagem"] for t, x in d.ev)
    fonte = inspect.getsource(encaminhamento.no_originais)
    assert 'saida.append({"leis"' not in fonte and 'saida.append({"tempos"' not in fonte
