"""Emendas parlamentares — três fontes anuais de recurso, SEM edital.

Regra do titular: emenda parlamentar não tem edital e a oportunidade existe em
TODOS os parlamentares com mandato. A captação acontece de **01/10 a 30/11 de
todos os anos**, nas três esferas: Goiânia (vereadores), Goiás (deputados
estaduais) e federal (deputados federais e senadores).

Cada tipo vira **uma única linha** no Calendário de Editais, carregando o
levantamento completo dos parlamentares: gabinete, endereço, telefone, e-mail,
partido, votação que os elegeu, situação do mandato e link do perfil.

Fluxo próprio, mais curto que o do edital:
  fase 1  a oportunidade nasce da regra anual (não depende de descoberta)
  fase 2  levantamento de gabinetes, parlamentares e mandatos eleitos
  fase 3  aprovação AUTOMÁTICA para todas as associações cadastradas —
          não há requisito eliminatório de edital a cumprir
  fase 5  ofícios e projetos por associação, com plano de trabalho completo,
          no padrão dos ofícios do Drive da entidade

Nenhum dado de parlamentar é inventado: sem resposta da fonte oficial, o
levantamento fica declarado como pendente e a linha diz isso.
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .nucleo import ROOT, load_json, now_iso, slug, write_json

CFG = ROOT / "config/emendas.json"
ESTADO = ROOT / "estado/emendas"
BIBLIOTECA = ROOT / "biblioteca_alexandria/emendas"


def _cfg() -> dict:
    return load_json(CFG)


def janela(ano: int, cfg: dict | None = None) -> tuple[str, str]:
    """Janela fixa de captação do ano: 01/10 a 30/11."""
    j = (cfg or _cfg())["janela"]
    return f"{ano}-{j['inicio_mes_dia']}", f"{ano}-{j['fim_mes_dia']}"


def _get(url: str, timeout: int = 25) -> dict | list:
    req = Request(url, headers={"User-Agent": "Eldorado-OSC/1.0 emendas",
                                "Accept": "application/json"})
    with urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


# ------------------------------------------------------- coleta por esfera
def coletar_federais() -> tuple[list[dict], list[dict]]:
    """Deputados federais (API da Câmara) e senadores (API do Senado)."""
    achados, falhas = [], []
    try:
        dados = _get("https://dadosabertos.camara.leg.br/api/v2/deputados"
                     "?ordem=ASC&ordenarPor=nome&itens=600")
        for d in dados.get("dados", []):
            det = {}
            try:
                det = (_get(d["uri"]).get("dados") or {})
            except Exception:
                pass
            gab = (det.get("ultimoStatus") or {}).get("gabinete") or {}
            achados.append({
                "nome_parlamentar": d.get("nome"),
                "nome_civil": det.get("nomeCivil"),
                "partido": d.get("siglaPartido"), "uf": d.get("siglaUf"),
                "cargo": "Deputado(a) Federal", "casa": "Câmara dos Deputados",
                "gabinete": (f'Gabinete {gab.get("nome")} — sala {gab.get("sala")}, '
                             f'prédio {gab.get("predio")}, andar {gab.get("andar")}'
                             if gab.get("nome") else None),
                "endereco": ("Praça dos Três Poderes, Câmara dos Deputados, "
                             "Brasília/DF, CEP 70160-900" if gab.get("nome") else None),
                "telefone": gab.get("telefone"), "email": gab.get("email"),
                "situacao_mandato": (det.get("ultimoStatus") or {}).get("situacao"),
                "legislatura": (det.get("ultimoStatus") or {}).get("idLegislatura"),
                "url_perfil": d.get("uri"), "foto": d.get("urlFoto"),
                "votacao_eleicao": None,
                "lacuna_votacao": "votação nominal não vem nesta API — consultar TSE",
            })
    except (HTTPError, URLError, OSError, ValueError) as exc:
        falhas.append({"fonte": "camara", "erro": type(exc).__name__})
    try:
        dados = _get("https://legis.senado.leg.br/dadosabertos/senador/lista/atual.json")
        lista = (((dados.get("ListaParlamentarEmExercicio") or {})
                  .get("Parlamentares") or {}).get("Parlamentar") or [])
        for s in lista:
            ident = s.get("IdentificacaoParlamentar") or {}
            mand = s.get("Mandato") or {}
            achados.append({
                "nome_parlamentar": ident.get("NomeParlamentar"),
                "nome_civil": ident.get("NomeCompletoParlamentar"),
                "partido": ident.get("SiglaPartidoParlamentar"),
                "uf": ident.get("UfParlamentar"),
                "cargo": "Senador(a)", "casa": "Senado Federal",
                "gabinete": (s.get("Telefones") or {}) and None,
                "endereco": "Praça dos Três Poderes, Senado Federal, Brasília/DF, CEP 70165-900",
                "telefone": None, "email": ident.get("EmailParlamentar"),
                "situacao_mandato": (mand.get("DescricaoParticipacao")
                                     or "Em exercício"),
                "legislatura": (mand.get("PrimeiraLegislaturaDoMandato") or {}).get("NumeroLegislatura"),
                "url_perfil": ident.get("UrlPaginaParlamentar"),
                "foto": ident.get("UrlFotoParlamentar"),
                "votacao_eleicao": None,
                "lacuna_votacao": "votação nominal não vem nesta API — consultar TSE",
            })
    except (HTTPError, URLError, OSError, ValueError) as exc:
        falhas.append({"fonte": "senado", "erro": type(exc).__name__})
    return achados, falhas


def coletar_catalogo_local(tipo_id: str) -> list[dict]:
    """Casas sem API aberta (ALEGO e Câmara de Goiânia) usam catálogo mantido
    no repositório: `config/parlamentares/<tipo>.json`. Enquanto não existir,
    a lacuna é declarada — nada é preenchido por suposição."""
    arq = ROOT / "config/parlamentares" / f"{tipo_id}.json"
    if not arq.exists():
        return []
    try:
        return load_json(arq).get("parlamentares", [])
    except Exception:
        return []


def levantar(tipo: dict) -> dict:
    """FASE 2 — levantamento de parlamentares, gabinetes e mandatos."""
    if tipo["id"] == "emenda-federal":
        parlamentares, falhas = coletar_federais()
        origem = "APIs oficiais da Câmara dos Deputados e do Senado Federal"
    else:
        parlamentares, falhas = coletar_catalogo_local(tipo["id"]), []
        origem = f'catálogo local (casa sem API aberta): config/parlamentares/{tipo["id"]}.json'
    completos = sum(1 for p in parlamentares
                    if p.get("gabinete") and (p.get("telefone") or p.get("email")))
    pendencias = []
    if not parlamentares:
        pendencias.append(f'levantamento pendente — {tipo["casa"]} não respondeu ou '
                          "não há catálogo local; nenhum parlamentar foi inventado")
    if parlamentares and completos < len(parlamentares):
        pendencias.append(f'{len(parlamentares)-completos} parlamentar(es) sem '
                          "gabinete ou contato completo — confirmar na casa")
    if parlamentares and not any(p.get("votacao_eleicao") for p in parlamentares):
        pendencias.append("votação de eleição não consta das APIs legislativas — "
                          "consultar o TSE (fonte configurada)")
    return {"tipo_id": tipo["id"], "parlamentares": parlamentares,
            "total": len(parlamentares), "com_contato_completo": completos,
            "origem_dos_dados": origem, "falhas": falhas,
            "pendencias": pendencias, "levantado_em": now_iso(),
            "fase": 2 if parlamentares else 1}


# ------------------------------------------------------- oportunidade anual
def oportunidade(tipo: dict, ano: int, lev: dict, hoje: date) -> dict:
    """Uma linha por tipo de emenda, com o ciclo do ano e o levantamento."""
    inicio, fim = janela(ano)
    estado = ("aberto" if inicio <= hoje.isoformat() <= fim
              else "a_abrir" if hoje.isoformat() < inicio else "encerrado")
    oid = f'{tipo["id"]}-{ano}'
    return {
        "id": oid, "protocolo": oid,
        "titulo": f'{tipo["nome"]} — captação {ano}',
        "url": tipo.get("fonte_dados"),
        "fonte_id": tipo["id"], "fonte_nome": tipo["casa"],
        "territorio": tipo["territorio"], "uf": tipo.get("uf"),
        "abrangencia": "nacional" if tipo["esfera"] == "federal" else "estadual",
        "nivel": tipo["esfera"], "status": "verificada_regra_anual",
        "area": tipo.get("area", "outros"),
        "programa": "Emenda parlamentar", "lei": tipo["lei"],
        "objeto": (f'Captação de emenda parlamentar junto aos {tipo["cargo"]}s '
                   f'com mandato. Não há edital: a solicitação é feita por ofício '
                   f'e projeto a cada gabinete, entre 01/10 e 30/11 de {ano}.'),
        "inicio": inicio, "fim": fim, "datas": "ambas",
        "publicado_em": None, "prazo_prorrogado": False,
        "estado_export": estado, "sem_edital": True,
        "resumo": (f'{lev["total"]} parlamentar(es) com mandato levantado(s) — '
                   f'{lev["com_contato_completo"]} com gabinete e contato completos'),
        "valor_texto": None,
        "verificacao_dupla": {"fonte": True, "conteudo": bool(lev["parlamentares"]),
                              "criterio": "regra anual + levantamento de mandatos"},
        "etapa": 5 if lev["parlamentares"] else 2,
        "etapa_nome": "Preparar" if lev["parlamentares"] else "Confirmar",
        "anexos_modelo": [], "anexos": [],
        "parlamentares": lev["parlamentares"],
        "levantamento": {k: lev[k] for k in
                         ("total", "com_contato_completo", "origem_dos_dados",
                          "pendencias", "levantado_em")},
        "ciclo": {"inscricao": {"inicio": inicio, "fim": fim, "projetado": False},
                  "resultado": None, "recurso": None, "fim_do_ciclo": fim},
        "marcos": [{"tipo": "abertura", "data": inicio, "projetado": False},
                   {"tipo": "encerramento", "data": fim, "projetado": False}],
        "destinacao": {"elegivel": True,
                       "motivo": "emenda parlamentar destina recurso a OSC por "
                                 "ofício e projeto — sem certame comercial"},
        "confirmacao": "confirmado_documental" if lev["parlamentares"] else "pendente",
        "detalhes": {
            "qualificacao": {"nota": None, "classe": "regra anual"},
            "documentos_exigidos": ["oficio_ao_gabinete", "projeto_tecnico",
                                    "plano_de_trabalho", "estatuto_social",
                                    "ata_de_posse", "cnpj", "certidoes_regularidade"],
            "pontuacao": [], "atendidos": [],
            "pendencias": lev["pendencias"],
            "evidencia": (f'Regra anual: emendas parlamentares são captadas de '
                          f'01/10 a 30/11. Fonte dos dados: {lev["origem_dos_dados"]}.'),
            "coletado_em": hoje.isoformat(), "lacuna": None,
        },
        "ficha": "",
    }


def run(ano: int | None = None, hoje: date | None = None) -> dict:
    """Executa as fases 1 e 2 das três emendas e grava na Biblioteca."""
    hoje = hoje or date.today()
    ano = ano or hoje.year
    cfg = _cfg()
    ESTADO.mkdir(parents=True, exist_ok=True)
    saida = []
    for tipo in cfg["tipos"]:
        lev = levantar(tipo)
        op = oportunidade(tipo, ano, lev, hoje)
        write_json(ESTADO / f'{tipo["id"]}-{ano}.json', op)
        pasta = BIBLIOTECA / tipo["id"] / str(ano)
        write_json(pasta / "levantamento.json", lev)
        write_json(pasta / "oportunidade.json",
                   {k: v for k, v in op.items() if k != "parlamentares"})
        saida.append({"tipo": tipo["id"], "parlamentares": lev["total"],
                      "fase": op["etapa"], "estado": op["estado_export"],
                      "pendencias": len(lev["pendencias"])})
    resumo = {"executado_em": now_iso(), "ano": ano,
              "janela": {"inicio": janela(ano, cfg)[0], "fim": janela(ano, cfg)[1]},
              "tipos": saida,
              "nota": ("três fontes anuais sem edital; a oportunidade existe em "
                       "todos os parlamentares com mandato")}
    write_json(ESTADO / "resumo.json", resumo)
    return resumo


def oportunidades_do_painel(hoje: date | None = None) -> list[dict]:
    """As três linhas para o painel (calendário, radar e fontes)."""
    hoje = hoje or date.today()
    saida = []
    if not ESTADO.exists():
        return saida
    for arq in sorted(ESTADO.glob("emenda-*.json")):
        try:
            saida.append(load_json(arq))
        except Exception:
            continue
    return saida


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
