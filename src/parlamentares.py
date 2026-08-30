"""Parlamentares com mandato — carga a partir de fonte oficial, sem invenção.

Área de emendas do relatório. Regra dura deste módulo: **nenhum nome, gabinete,
partido, votação ou bandeira é escrito de memória ou deduzido.** Tudo vem de
fonte oficial identificada, com data de consulta e URL registradas. Enquanto a
carga não acontece, a área aparece como *aguardando carga oficial* — nunca com
dado provisório que pareça verdadeiro.

Fontes por esfera (configuradas em `config/parlamentares.json`):

- **Federal** — API de dados abertos da Câmara dos Deputados: deputados em
  exercício, gabinete, partido, UF, e as proposições e comissões de cada um,
  que é de onde saem as *bandeiras* (temas efetivamente defendidos no mandato,
  medidos por atuação registrada, não por opinião).
- **Estadual e municipal** — ALEGO e Câmara de Goiânia. Quando não houver API
  aberta, a carga fica pendente e o relatório declara a pendência com o link
  oficial para consulta humana.
- **Resultado eleitoral** — dados abertos do TSE. Sem carga, o campo permanece
  nulo e visivelmente marcado como não carregado.

Emendas **não acionam o Farol de Alexandria**: dependem de articulação e
viabilidade política. Este módulo informa e direciona; não abre caso nem gera
plano de trabalho. Sem IA e sem tokens.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import date
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .nucleo import ROOT, load_json, now_iso, validate_public_https, write_json

BASE = ROOT / "dados/parlamentares"

def _buscar(url: str, timeout: int = 30) -> dict:
    validate_public_https(url)
    req = Request(url, headers={"User-Agent": "Eldorado-OSC/3.0 contato-via-repositorio",
                                "Accept": "application/json"})
    with urlopen(req, timeout=timeout) as resposta:
        bruto = resposta.read(8_000_001)
    if len(bruto) > 8_000_000:
        raise ValueError("resposta excede limite")
    return json.loads(bruto.decode("utf-8", "replace"))

def _bandeiras(temas: list[str], cfg: dict) -> list[dict]:
    """Bandeiras = temas com atuação registrada, medidos por frequência.

    Não é opinião sobre o parlamentar: é contagem do que ele efetivamente
    apresentou ou relatou. Tema com uma única ocorrência é ruído e não vira
    bandeira, pelo mesmo princípio dos padrões de financiador.
    """
    minimo = int(cfg.get("min_ocorrencias_bandeira", 2))
    contagem = Counter(t for t in temas if t)
    return [{"tema": tema, "ocorrencias": n, "base": "proposicoes_e_comissoes_registradas"}
            for tema, n in contagem.most_common(12) if n >= minimo]

def carregar_federais(cfg: dict, ano: int) -> tuple[list[dict], list[dict]]:
    """Deputados federais em exercício pela API oficial da Câmara."""
    fonte = cfg["fontes"]["camara_federal"]
    if not fonte.get("ativa"):
        return [], [{"esfera": "federal", "motivo": "fonte desativada na configuração"}]
    saida, falhas = [], []
    ufs = cfg.get("ufs_de_interesse") or ["GO"]
    for uf in ufs:
        url = f"{fonte['base']}/deputados?" + urlencode({"siglaUf": uf, "ordem": "ASC",
                                                         "ordenarPor": "nome", "itens": 100})
        try:
            dados = _buscar(url)
        except (HTTPError, URLError, OSError, ValueError, json.JSONDecodeError) as exc:
            falhas.append({"esfera": "federal", "uf": uf, "erro": type(exc).__name__})
            continue
        for deputado in dados.get("dados", []) or []:
            registro = {
                "id": f"fed-{deputado.get('id')}", "esfera": "federal",
                "nome": deputado.get("nome"), "partido": deputado.get("siglaPartido"),
                "uf": deputado.get("siglaUf"), "ano_mandato": ano,
                "url_oficial": deputado.get("uri"),
                "gabinete": None, "bandeiras": [], "resultado_eleicao": None,
                "fonte": fonte["nome"], "consultado_em": now_iso(),
            }
            try:
                detalhe = _buscar(f"{fonte['base']}/deputados/{deputado.get('id')}").get("dados", {})
                gab = (detalhe.get("ultimoStatus") or {}).get("gabinete") or {}
                registro["gabinete"] = {
                    "predio": gab.get("predio"), "sala": gab.get("sala"), "andar": gab.get("andar"),
                    "telefone": gab.get("telefone"), "email": gab.get("email"),
                }
                registro["situacao"] = (detalhe.get("ultimoStatus") or {}).get("situacao")
            except (HTTPError, URLError, OSError, ValueError, json.JSONDecodeError):
                falhas.append({"esfera": "federal", "deputado": deputado.get("nome"), "erro": "detalhe_indisponivel"})
            try:
                props = _buscar(f"{fonte['base']}/deputados/{deputado.get('id')}/ocorrencias"
                                if False else
                                f"{fonte['base']}/proposicoes?" + urlencode(
                                    {"idDeputadoAutor": deputado.get("id"), "itens": 100,
                                     "ano": ano, "ordem": "DESC", "ordenarPor": "id"}))
                temas = []
                for proposicao in props.get("dados", []) or []:
                    ementa = (proposicao.get("ementa") or "").lower()
                    for tema, palavras in cfg["temas"].items():
                        if any(p in ementa for p in palavras):
                            temas.append(tema)
                registro["bandeiras"] = _bandeiras(temas, cfg)
            except (HTTPError, URLError, OSError, ValueError, json.JSONDecodeError):
                falhas.append({"esfera": "federal", "deputado": deputado.get("nome"), "erro": "proposicoes_indisponiveis"})
            saida.append(registro)
    return saida, falhas

def run(ano: int | None = None) -> dict:
    cfg = load_json(ROOT / "config/parlamentares.json")
    ano = ano or date.today().year
    relatorio = {"executado_em": now_iso(), "ano": ano, "carregados": 0,
                 "por_esfera": {}, "pendencias": [], "falhas": []}

    federais, falhas = carregar_federais(cfg, ano)
    relatorio["falhas"] += falhas
    todos = list(federais)
    relatorio["por_esfera"]["federal"] = len(federais)

    for chave in ("assembleia_goias", "camara_goiania"):
        fonte = cfg["fontes"].get(chave, {})
        if fonte.get("ativa") and fonte.get("base"):
            continue
        relatorio["pendencias"].append({
            "esfera": fonte.get("esfera", chave), "casa": fonte.get("nome", chave),
            "motivo": fonte.get("motivo_pendencia", "sem API aberta configurada"),
            "consulta_humana": fonte.get("url_consulta_humana"),
            "acao": "carga manual assistida ou configuração de endpoint oficial",
        })
        relatorio["por_esfera"][fonte.get("esfera", chave)] = 0

    BASE.mkdir(parents=True, exist_ok=True)
    write_json(BASE / f"{ano}.json", {
        "ano": ano, "gerado_em": now_iso(), "total": len(todos), "parlamentares": todos,
        "pendencias": relatorio["pendencias"],
        "regra": ("nenhum nome, gabinete, partido, votação ou bandeira é escrito de memória; "
                  "campo sem carga oficial permanece nulo e declarado"),
        "resultado_eleicao": {
            "status": "nao_carregado",
            "fonte_indicada": cfg["fontes"]["tse"]["url_consulta_humana"],
            "motivo": cfg["fontes"]["tse"].get("motivo_pendencia"),
        },
    })
    relatorio["carregados"] = len(todos)
    write_json(ROOT / "estado/ultima_carga_parlamentares.json", relatorio)
    return relatorio

def carregar_do_disco(ano: int) -> dict:
    caminho = BASE / f"{ano}.json"
    if not caminho.exists():
        return {"ano": ano, "total": 0, "parlamentares": [], "status": "aguardando_carga_oficial",
                "pendencias": [{"motivo": "nenhuma carga executada para este ano"}]}
    return load_json(caminho)

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
