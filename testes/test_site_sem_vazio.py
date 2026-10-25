"""Nenhum quadro do site vazio (titular, 25/10/2026: "pedi para consertar diversas vezes os motores e os mostradores deles do
site continuam sem funcionamento": 19 dos 33 arquivos lidos pelo site saíam com a estrutura vazia do Eldorado0)."""
import json
import shutil
from pathlib import Path

LIGADOS = ["alerta_motores.json", "auditoria_motores.json", "validacao_motores_mes.json", "saude.json", "status_motores.json",
           "achados_motores.json", "descricao_motores.json", "achados_dia.json", "motores_manuais.json",
           "espiao.json", "espiao_ao_vivo.json", "interceptador.json", "interceptador_ao_vivo.json", "esquadrilha.json", "achados_pilotos.json",
           "piloto_ao_vivo.json", "piloto_posicao.json", "briefings_piloto.json", "resgates_piloto.json", "radar_piloto.json",
           "cartorio.json", "ranking_apoiadores.json", "sala_controle.json", "fluxo_oportunidades.json", "mapa_arquivos.json"]


def test_nenhum_arquivo_do_site_vazio(tmp_path):
    raiz = tmp_path / "sv"
    (raiz / "dados").mkdir(parents=True)
    for n in ("biblioteca", "cerebro"):
        shutil.copy(f"dados/{n}.db", raiz / "dados" / f"{n}.db")
    for d in ("config", "eldorado", "eventos", "workflows", "scripts", ".github"):
        (raiz / d).symlink_to(Path(d).resolve())
    from eldorado.base.painel.dados import gerar
    gerar(raiz / "site", raiz)
    molde = Path("eldorado/base/painel/molde")
    for f in LIGADOS:
        p = raiz / "site" / "dados" / f
        assert p.exists(), f"{f}: o site recebe 404"
        d = json.loads(p.read_text(encoding="utf-8"))
        assert d.get("em") or d.get("gerado_em") or d.get("atualizado_em"), f"{f}: sem a hora da geração (vazio)"
        if (molde / f).exists():
            assert d != json.loads((molde / f).read_text(encoding="utf-8")), f"{f}: igual à estrutura vazia"
    pilotos = [m for m in json.loads((raiz / "site/dados/sala_controle.json").read_text())["detalhes"]["motores"] if str(m["id"]).startswith("piloto")]
    assert pilotos and all(m.get("ultima_leitura") for m in pilotos)                    # a hora dos pilotos no campo dos motores
    mapa = json.loads((raiz / "site/dados/mapa_arquivos.json").read_text())
    assert mapa["medido_em"] and mapa["medido_em"][:10] == mapa["gerado_em"][:10]       # medido na hora, com o código atual
