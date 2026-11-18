"""18/11/2026 (titular): a pesquisa das empresas financiadoras pelo Claude no Chrome (825 empresas em 3 grupos) entra no
sistema. Cada arquivo em verificacao/empresas/ é importado uma vez (o relatório em importados/ impede a repetição):

  - a empresa é encontrada no cadastro pelo CNPJ, pela raiz do CNPJ (a filial liga à matriz) ou pela razão social; a que não
    estiver no cadastro entra nele (descoberta pela titular), para nenhum dado se perder;
  - o perfil (empresa_perfil): os 36 campos da pesquisa, as fontes, as buscas e o que não foi encontrado — a empresa sem
    atuação em Goiás fica registrada «SEM ATUAÇÃO», como a titular pediu;
  - o cadastro corrigido: o site oficial, a razão social atual e a UF, quando a pesquisa os conferiu;
  - os incentivos confirmados que ainda não constavam (uma linha por lei; a tabela não aceita regravar);
  - o aprofundamento: a pesquisa feita, com a primeira fonte.

Depois, a classificação: a pontuação de financiadora de cada empresa pesquisada (o ranking), uma vez por dia."""
from __future__ import annotations

import json
import re
import sqlite3
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

PASTA = Path("verificacao/empresas")
CAMPOS = ["situacao_cadastral", "site_oficial", "grupo_economico", "unidades_em_goias", "atua_em_goiania", "pagina_esg", "instituto_ou_fundacao",
          "politica_investimento_social", "programas_proprios", "o_que_financiam", "quem_pode_participar", "valor_por_projeto",
          "recorrencia_mes_abertura", "datas_edicoes_anteriores", "situacao_hoje", "leis_confirmadas", "anos_destinou", "valor_destinado_por_ano",
          "projetos_em_goias", "como_escolhe_projetos", "mes_decide_destinacao", "patrocinio_direto", "doacao_de_bens", "relatorio_sustentabilidade",
          "valor_investimento_social", "temas_e_publico", "territorios_prioritarios", "canal_para_projeto", "area_responsavel",
          "obrigacoes_que_geram_recurso", "risco_ou_cuidado", "atuacao_goias", "melhor_caminho_de_entrada", "melhor_mes_para_procurar",
          "parecer_resumido", "buscas_sem_atuacao"]
LEIS = (("FIA", r"\bfia\b|inf[âa]ncia|crian[çc]a e (do )?adolescente|fundo (municipal |estadual |nacional )?da crian"),
        ("Idoso", r"idos[oa]"), ("Esporte", r"esporte|\blie\b|222/2025|11\.438"), ("Rouanet", r"rouanet|8\.313|pronac"),
        ("Pronas", r"pronas"), ("Pronon", r"pronon"), ("Goyazes", r"goyazes"), ("ICMS", r"\bicms\b|protege"),
        ("PAT", r"\bpat\b|alimenta[çc][ãa]o do trabalhador"))
NEGA = re.compile(r"(?i)^\s*(n[ãa]o\b|nenhum|sem\b|n/?d\b|—|-\s*$)")


def _norm(t: str | None) -> str:
    t = unicodedata.normalize("NFKD", str(t or "")).encode("ascii", "ignore").decode().lower()
    t = re.sub(r"\b(s\.?a\.?|ltda\.?|eireli|me|epp|cia)\b", " ", t)
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", t).split())


def _tem(v: str | None) -> bool:
    return bool(v) and not NEGA.search(v)


def _url(v: str | None) -> str | None:
    """O site oficial: o endereço completo ou o domínio (o grupo 1 traz «equatorialenergia.com.br»); o «a confirmar» não entra."""
    if not _tem(v) or re.search(r"(?i)a confirmar|n[ãa]o encontrad|n[ãa]o localizad", (v or "")[:80]):
        return None
    m = re.search(r"https?://[^\s)\];,]+", v or "")
    if m:
        return m.group(0).rstrip(".")
    m = re.match(r"\s*((?:[a-z0-9-]+\.)+[a-z]{2,})(/[^\s;,)]*)?", (v or "").lower())
    return f"https://{m.group(1)}{m.group(2) or ''}".rstrip(".") if m else None


def _uf_corrigida(situacao: str | None) -> str | None:
    m = re.search(r"(?i)UF do cadastro\s*['\"«]?\w*['\"»]?\s*deve ser\s*([A-Z]{2})\b", situacao or "")
    return m.group(1) if m else None


CONFIRMA = re.compile(r"(?i)confirmad[oa]s?\b")
NEGA_CONFIRMA = re.compile(r"(?i)n[ãa]o\s+(re)?(confirmad|conferid|verificad|localizad)|sem confirma")


def _leis(texto: str | None) -> list[str]:
    """Só as leis de um trecho que diz «confirmada» sem negação — «não reconfirmado no Salic», «não verificado» e «citada» não
    contam (o grupo 2 repetia as leis que o próprio sistema já tinha, sem reconfirmar)."""
    if not _tem(texto):
        return []
    saida: list[str] = []
    for trecho in re.split(r"[;.\n]|\)\s*,", texto or ""):
        if not CONFIRMA.search(trecho) or NEGA_CONFIRMA.search(trecho):
            continue
        t = trecho.lower()
        saida += [lei for lei, rx in LEIS if re.search(rx, t) and lei not in saida]
    return saida


def _ano(texto: str | None) -> int | None:
    anos = [int(a) for a in re.findall(r"\b(20[0-3]\d)\b", texto or "")]
    return max(anos) if anos else None


def _resolver(rec: dict, cad: dict, por_raiz: dict, por_nome: dict) -> str | None:
    for c in rec.get("cnpjs") or []:
        if c in cad:
            return c
    for c in rec.get("cnpjs") or []:
        if c[:8] in por_raiz:
            return por_raiz[c[:8]]
    for n in (rec.get("razao_conferida"), rec.get("razao_no_sistema")):
        if _norm(n) in por_nome:
            return por_nome[_norm(n)]
    return None


def _juntar(antes: dict, novo: dict, grupo: str) -> dict:
    """A mesma empresa pesquisada duas vezes (a Cencosud no grupo 1 e o «Grupo Bretas / Cencosud» no grupo 3): o campo vazio
    recebe o do outro; textos diferentes ficam os dois, cada um com o seu grupo — nenhuma pesquisa apaga a outra."""
    saida = dict(antes)
    for k, v in novo.items():
        if k in ("cnpj", "pesquisado_em") or not v:
            continue
        a = saida.get(k)
        saida[k] = v if not a else a if v in a else f"{a} | {grupo}: {v}"[:8000]
    return saida


def importar_arquivo(caminho: Path, con: sqlite3.Connection, diario, agora: str, perfis: dict | None = None) -> dict[str, Any]:
    perfis = {} if perfis is None else perfis
    pac = json.loads(Path(caminho).read_text(encoding="utf-8"))
    cad = {r[0]: (r[1], r[2], r[3]) for r in con.execute("SELECT cnpj, razao_social, uf, site FROM empresa")}
    por_raiz = {c[:8]: c for c in cad}
    por_nome = {}
    for c, (rs, _uf, _site) in cad.items():
        por_nome.setdefault(_norm(rs), c)
    for c, nf in con.execute("SELECT cnpj, nome_fantasia FROM empresa WHERE nome_fantasia IS NOT NULL"):
        por_nome.setdefault(_norm(nf), c)
    ja_lei = {(r[0], r[1]) for r in con.execute("SELECT cnpj, lei FROM incentivo")}
    conta = {"empresas": 0, "novas_no_cadastro": 0, "sites": 0, "razoes_corrigidas": 0, "ufs_corrigidas": 0, "incentivos_novos": 0, "sem_cnpj": 0}
    for rec in pac["empresas"]:
        campos = rec.get("campos") or {}
        cnpj = _resolver(rec, cad, por_raiz, por_nome)
        nome = rec.get("razao_conferida") or rec.get("razao_no_sistema") or ""
        if not cnpj:
            cnpj = (rec.get("cnpjs") or [None])[0] or ("nome:" + _norm(nome).replace(" ", "-")[:80])
            conta["sem_cnpj"] += cnpj.startswith("nome:")
            nova = {"cnpj": cnpj, "razao_social": nome[:200] or cnpj, "nome_fantasia": None, "uf": _uf_corrigida(campos.get("situacao_cadastral")),
                    "site": _url(campos.get("site_oficial")), "descoberta_por": "titular", "descoberta_em": agora, "atualizada_em": agora}
            diario.emitir("empresa.registrada", "pesquisa-empresas", nova)
            cad[cnpj] = (nome, None, None)
            conta["novas_no_cadastro"] += 1
        else:
            rs, uf, site = cad[cnpj]
            corr = {"cnpj": cnpj, "atualizada_em": agora}
            novo_site, nova_uf = _url(campos.get("site_oficial")), _uf_corrigida(campos.get("situacao_cadastral"))
            if novo_site and not site:
                corr["site"] = novo_site
                conta["sites"] += 1
            if nova_uf and nova_uf != uf:
                corr["uf"] = nova_uf
                conta["ufs_corrigidas"] += 1
            if rec.get("razao_conferida") and _norm(rec["razao_conferida"]) != _norm(rs) and len(rec["razao_conferida"]) > 3:
                corr["razao_social"] = rec["razao_conferida"][:200]
                conta["razoes_corrigidas"] += 1
            if len(corr) > 2:
                diario.emitir("empresa.corrigida", "pesquisa-empresas", corr)
        perfil = {"cnpj": cnpj, **{k: (str(campos.get(k))[:4000] if campos.get(k) else None) for k in CAMPOS},
                  "fontes": json.dumps(rec.get("fontes"), ensure_ascii=False)[:20000] if rec.get("fontes") else None,
                  "buscas": json.dumps(rec.get("buscas"), ensure_ascii=False)[:20000] if rec.get("buscas") else None,
                  "nao_encontrados": json.dumps(rec.get("nao_encontrados"), ensure_ascii=False)[:8000] if rec.get("nao_encontrados") else None,
                  "pesquisa": pac.get("pesquisa") or "", "pesquisado_em": agora}
        if cnpj in perfis:                                    # a mesma empresa em dois grupos: junta, não sobrescreve
            perfil = _juntar(perfis[cnpj], perfil, pac.get("pesquisa") or "")
        perfis[cnpj] = perfil
        diario.emitir("empresa.perfil", "pesquisa-empresas", perfil)
        for lei in _leis(campos.get("leis_confirmadas")):
            if (cnpj, lei) in ja_lei:
                continue
            inc = {"cnpj": cnpj, "lei": lei, "ano": _ano(campos.get("anos_destinou")), "valor": None, "comprovado": 1,
                   "fonte": f"pesquisa da empresa no Claude no Chrome ({pac.get('pesquisa')})", "em": agora}
            diario.emitir("incentivo.registrado", "pesquisa-empresas", inc)
            ja_lei.add((cnpj, lei))
            conta["incentivos_novos"] += 1
        fonte = rec.get("fontes")
        fonte = (fonte[0] if isinstance(fonte, list) and fonte else fonte if isinstance(fonte, str) else None)
        fonte_txt = json.dumps(fonte, ensure_ascii=False) if fonte and not isinstance(fonte, str) else fonte
        apr = {"cnpj": cnpj, "piloto": "chrome", "o_que": "pesquisa da empresa financiadora",
               "achou": (campos.get("parecer_resumido") or campos.get("atuacao_goias") or "")[:2000], "fonte": fonte_txt, "em": agora}
        diario.emitir("aprofundamento.registrado", "pesquisa-empresas", apr)
        conta["empresas"] += 1
    return {"arquivo": Path(caminho).name, **conta, "em": agora}


def pontos(perfil: dict, leis: int) -> float:
    """A pontuação de financiadora (o ranking): a atuação em Goiás, as leis, os programas, o canal e o risco."""
    p = 0.0
    if str(perfil.get("atuacao_goias") or "").strip().upper().startswith("COMPROVADA"):
        p += 30
    if re.match(r"(?i)\s*sim", perfil.get("atua_em_goiania") or ""):
        p += 15
    p += min(40, 10 * leis)
    for campo, v in (("programas_proprios", 15), ("projetos_em_goias", 15), ("instituto_ou_fundacao", 10)):
        if _tem(perfil.get(campo)):
            p += v
    if re.search(r"https?://|@", perfil.get("canal_para_projeto") or ""):
        p += 10
    if re.search(r"R\$\s*\d", perfil.get("valor_investimento_social") or ""):
        p += 5
    if re.search(r"(?i)san[çc][ãa]o|recupera[çc][ãa]o judicial|fal[êe]ncia|inid[ôo]ne", perfil.get("risco_ou_cuidado") or ""):
        p -= 20
    return p


def classificar(con: sqlite3.Connection, diario, agora: str) -> int:
    """O ranking das empresas pesquisadas — uma vez por dia (critério «financiadora»)."""
    try:
        ult = con.execute("SELECT MAX(calculado_em) FROM ranking WHERE criterio = 'financiadora'").fetchone()[0]
        if ult and datetime.fromisoformat(agora) - datetime.fromisoformat(ult) < timedelta(hours=24):
            return 0
        con.row_factory = sqlite3.Row
        perfis = [dict(r) for r in con.execute("SELECT * FROM empresa_perfil")]
        con.row_factory = None
        leis: dict[str, int] = {}
        for c, n in con.execute("SELECT cnpj, COUNT(DISTINCT lei) FROM incentivo GROUP BY cnpj"):
            leis[c] = n
    except sqlite3.Error:
        return 0
    ordem = sorted(perfis, key=lambda p: -pontos(p, leis.get(p["cnpj"], 0)))
    for pos, p in enumerate(ordem, 1):
        diario.emitir("ranking.calculado", "pesquisa-empresas", {"cnpj": p["cnpj"], "criterio": "financiadora", "posicao": pos,
                                                                  "pontos": pontos(p, leis.get(p["cnpj"], 0)), "calculado_em": agora})
    return len(ordem)


def importar_pasta(con: sqlite3.Connection, diario, pasta: Path = PASTA) -> dict[str, Any]:
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    feitos, saida, perfis = pasta / "importados", [], {}
    if pasta.exists():
        for arq in sorted(pasta.glob("pesquisa-*.json")):
            if (feitos / (arq.stem + "-relatorio.json")).exists():       # importado uma vez (a lição da C-13)
                continue
            r = importar_arquivo(arq, con, diario, agora, perfis)
            saida.append(r)
            feitos.mkdir(exist_ok=True)
            arq.rename(feitos / arq.name)
            (feitos / (arq.stem + "-relatorio.json")).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"importados": saida, "ranking": classificar(con, diario, agora)}
