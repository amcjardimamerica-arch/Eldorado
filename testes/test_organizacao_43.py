"""R50 — a organização dos 43 motores (titular, 09/11/2026): 41 regulares e 2 pilotos, na ordem e nos grupos da titular;
os extintos reunidos (o histórico passa ao motor que os reúne); os três Tribunais de Contas; o Prosas só com o site do
Prosas; a fonte de destino especial (a base de empresas) dentro de um motor da Biblioteca."""
from __future__ import annotations

import json
import tomllib
from pathlib import Path
from urllib.parse import urlsplit

PASTA = Path("eldorado/motores/canal/config")
ESTUDO = json.loads(Path("config/motores_previstos.json").read_text(encoding="utf-8"))
ORDEM = ["do-goiania", "novo-diarios-municipais-go", "do-goias", "dou", "camara-goiania-pl", "alego-pl", "congresso-nacional",
         "judiciario-tjgo", "judiciario-cnj", "dj-trf1-go", "mpgo-destinacao", "mptgo-destinacao", "mpu-destinacao", "tcm-go", "tce-go", "tcu",
         "prefeitura-goiania", "prefeituras-rm-goiania", "prefeituras-50-go", "estaduais-go-gov", "governo-federal", "site-transferegov", "pncp-api",
         "sistema-s", "novo-bancos-publicos", "empresas-editais-incentivados", "novo-fundacoes-institutos", "fundacoes-nacionais", "novo-internacional",
         "gife", "site-abcr", "site-observatorio-terceiro-setor", "site-rede-filantropia", "site-idis", "site-capitaai", "site-prosas",
         "editais-do-brasil", "bussola-social", "plataforma-mapas-culturais", "site-farol-cultural", "site-editais-culturais",
         "piloto-aberto", "piloto-interceptador"]
# R51 (titular, 09/11/2026): um motor por site de divulgação — os 18 sites achados viram os motores 44 a 61 (o Mapa das OSC
# volta a ter motor próprio: sai dos nomes anteriores do Prosas)
NOVOS_R51 = ["site-capta", "site-alteditais", "site-licitario", "site-editalong", "site-escola-aberta-3setor", "site-vagas-terceiro-setor", "site-i3s", "site-conjunta", "site-rit", "site-radar-editais", "site-utarget", "site-exitos", "site-mapa-osc", "site-agente-cultural", "site-radar-editais-culturais", "site-editais-de-cultura", "site-editaisculturais-com", "site-fundingcalls"]
EXTINTOS = {"cnpq-extensao": "governo-federal", "site-funarte": "governo-federal", "salic": "governo-federal", "motor-gife": "novo-fundacoes-institutos",
            "site-rede-comua": "fundacoes-nacionais", "site-fundo-baoba": "fundacoes-nacionais", "site-fundo-casa": "fundacoes-nacionais",
            "site-cese": "fundacoes-nacionais", "site-fundo-brasil": "fundacoes-nacionais", "site-brazilfoundation": "fundacoes-nacionais",
            "site-undef": "novo-internacional", "site-mapas-culturais": "plataforma-mapas-culturais",
            "outros-agregadores": "editais-do-brasil"}


def _cfg(mid: str) -> dict:
    return tomllib.loads((PASTA / f"{mid}.toml").read_text(encoding="utf-8"))


def test_os_43_motores_na_ordem_da_titular():
    m = ESTUDO["motores"]
    assert [x["id"] for x in m] == ORDEM + NOVOS_R51 and [x["numero"] for x in m] == list(range(1, 62))   # R51: 44 a 61
    assert {p.stem for p in PASTA.glob("*.toml")} == set(ORDEM[:41]) | set(NOVOS_R51)       # 59 regulares, um arquivo cada
    for i, mid in enumerate(ORDEM[:41], 1):
        c = _cfg(mid)["motor"]
        assert c["id"] == mid and c["numero"] == i and c["grupo"] == m[i - 1]["grupo"], mid
    modulos = Path("config/modulos.toml").read_text(encoding="utf-8")
    assert all(f"config/{mid}.toml" in modulos for mid in ORDEM[:41])


def test_cada_extinto_reunido_em_um_so_motor():
    donos: dict[str, list[str]] = {}
    for p in PASTA.glob("*.toml"):
        for a in tomllib.loads(p.read_text(encoding="utf-8"))["motor"].get("nomes_anteriores", []):
            donos.setdefault(a, []).append(p.stem)
    for x, para in EXTINTOS.items():
        assert not (PASTA / f"{x}.toml").exists(), x
        assert donos.get(x) == [para], f"{x} deve estar só em {para}: {donos.get(x)}"
    for arq in ("config/modulos.toml", "config/agenda.toml"):
        t = Path(arq).read_text(encoding="utf-8")
        assert not [x for x in EXTINTOS if f'"{x}"' in t or f"/{x}.toml" in t], arq


def test_os_grupos_e_os_tres_tribunais_de_contas():
    grupos = list(dict.fromkeys(x["grupo"] for x in ESTUDO["motores"]))
    assert grupos == ["Diários oficiais", "Legislativo", "Judiciário", "Ministério Público", "Tribunais de Contas", "Executivo municipal",
                      "Executivo estadual", "Executivo federal", "Sistema S e bancos públicos", "Leis de incentivo fiscal",
                      "Editais de empresas privadas", "Editais de fundações", "Sites de divulgação — terceiro setor",
                      "Sites de divulgação — cultura", "Ferramentas transversais", "Sites de divulgação — internacional"]   # R51
    for mid, dom in (("tcm-go", "tcmgo.tc.br"), ("tce-go", "tce.go.gov.br"), ("tcu", "tcu.gov.br")):
        c = _cfg(mid)
        assert c["motor"]["grupo"] == "Tribunais de Contas" and any(dom in f["url"] for f in c["fonte"]), mid
    # as secretarias de cada esfera num motor da esfera; o município pelo mapa do site completo
    gyn = _cfg("prefeitura-goiania")
    assert any(f["tipo"] == "mapa" for f in gyn["fonte"]) and sum("goiania.go.gov.br/secretaria/" in f["url"] for f in gyn["fonte"]) >= 15


def test_o_prosas_so_com_o_site_do_prosas():
    c = _cfg("site-prosas")
    hosts = {urlsplit(u).hostname for u in [f["url"] for f in c["fonte"] if f["url"]] + [e for a in c.get("alvo", []) for e in a["enderecos"]]}
    assert hosts and all(h and h.endswith("prosas.com.br") for h in hosts), hosts


def test_a_fonte_com_destino_especial_vai_a_base_especial(tmp_path):
    """O motor-gife reunido num motor da Biblioteca: a fonte de empresas leva destino = "especial" e entrega à base Especial."""
    from eldorado.motores.canal.motor import Configuracao
    c = Configuracao(**_cfg("novo-fundacoes-institutos"))
    assert c.motor.destino == "biblioteca"
    esp = [f for f in c.fonte if f.destino == "especial"]
    assert len(esp) >= 5 and all(f.especial.get("cnpj") for f in esp)
