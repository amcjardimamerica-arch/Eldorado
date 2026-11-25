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


# R61 (titular, 18/11/2026; implantado em 25/11/2026 — C-08 de 23/11): as decisões que mudam a importação
UFS = {"AC": "acre", "AL": "alagoas", "AP": "amapa", "AM": "amazonas", "BA": "bahia", "CE": "ceara", "DF": "distrito federal",
       "ES": "espirito santo", "GO": "goias", "MA": "maranhao", "MT": "mato grosso", "MS": "mato grosso do sul", "MG": "minas gerais",
       "PA": "para", "PB": "paraiba", "PR": "parana", "PE": "pernambuco", "PI": "piaui", "RJ": "rio de janeiro", "RN": "rio grande do norte",
       "RS": "rio grande do sul", "RO": "rondonia", "RR": "roraima", "SC": "santa catarina", "SP": "sao paulo", "SE": "sergipe", "TO": "tocantins"}
PROJETO = re.compile(r"(?i)projet|program|edital|patroc[íi]n|apoi|institut|funda[çc][ãa]o|fomento|goyazes|salic|pronac|"
                     r"lei de incentivo|doa[çc]|investimento social|a[çc][ãa]o social|parceria|pr[êe]mio|bolsa")
NAO_ACHOU = re.compile(r"(?i)n[ãa]o (encontrad|localizad|identificad|h[áa]|declarad|comprovad|consta|aparece|figura|achad)|nenhum|"
                       r"sem (projeto|registro|atua)")


def _ufs(texto: str | None) -> list[str]:
    t = _norm(texto)
    achou = [uf for uf, nome in UFS.items() if re.search(rf"\b{nome}\b", t)]
    achou += [uf for uf in re.findall(r"(?:/|-|\b)([A-Z]{2})\b", texto or "") if uf in UFS and uf not in achou]
    return achou


def atuacao_declarada(campos: dict, fonte: str | None = None) -> list[dict]:
    """R61 (1, 2): a atuação por estado é a DECLARADA em projeto ou programa — filial, fábrica, loja, unidade e ICMS não
    contam. Cada entrada: o estado, o projeto (o trecho), o ano e a fonte (a base do filtro por estado e do mapa)."""
    saida: list[dict] = []
    proj = str(campos.get("projetos_em_goias") or "")
    # cada trecho vale sozinho: «Goyazes: não consta como empresa incentivadora» é a pesquisa dizendo que NÃO há projeto
    trechos = [t.strip() for t in re.split(r"[;|\n]", proj) if t.strip()]
    com_projeto = [t for t in trechos if PROJETO.search(t) and not NAO_ACHOU.search(t) and not re.match(r"(?i)n[ãa]o\b", t)]
    if _tem(proj) and com_projeto:
        saida.append({"uf": "GO", "projeto": "; ".join(com_projeto)[:300], "ano": _ano(proj), "fonte": fonte})
    terr = str(campos.get("territorios_prioritarios") or "")
    if _tem(terr):
        for trecho in re.split(r"[;\n]|\.\s", terr):
            if NAO_ACHOU.search(trecho) or not trecho.strip():
                continue
            for uf in _ufs(trecho):
                if uf == "GO" and any(x["uf"] == "GO" for x in saida):
                    continue
                if uf == "GO" and not PROJETO.search(trecho + " " + proj):
                    continue
                saida.append({"uf": uf, "projeto": trecho.strip()[:300], "ano": _ano(trecho), "fonte": fonte})
    return saida


def atuacao_goias(campos: dict, declarada: list[dict]) -> str:
    """R61 (1): «COMPROVADA» só com projeto ou programa em Goiás; a unidade, a filial, a sede ou o ICMS viram «SEM ATUAÇÃO
    DECLARADA» (o texto da pesquisa fica, para a titular ver o que foi achado)."""
    original = str(campos.get("atuacao_goias") or "").strip()
    go = next((x for x in declarada if x["uf"] == "GO"), None)
    if go:
        return f"COMPROVADA — projeto/programa em Goiás: {go['projeto']}"[:4000]
    return (f"SEM ATUAÇÃO DECLARADA — a pesquisa achou: {original}" if original else "SEM ATUAÇÃO DECLARADA")[:4000]


def sede_uf(campos: dict, uf_cadastro: str | None) -> str | None:
    """R61 (2): a empresa fica ligada ao estado da SEDE (matriz), não ao da filial."""
    sit = str(campos.get("situacao_cadastral") or "")
    corr = _uf_corrigida(sit)
    if corr:
        return corr
    m = re.search(r"(?i)(?:sede|matriz)[^;.]{0,60}?[/\-–]\s?([A-Z]{2})\b", sit)
    if m and m.group(1).upper() in UFS:
        return m.group(1).upper()
    return uf_cadastro if uf_cadastro in UFS else None


def tipo_da(nome: str | None, campos: dict) -> str:
    """R61 (4): fundos internacionais e ONGs ficam no cadastro, com o tipo no filtro — Fundação ou Fundo."""
    t = f"{nome or ''} {campos.get('situacao_cadastral') or ''}"
    if re.search(r"(?i)\bfundo\b|\bfund\b|foundation fund|trust fund", t):
        return "Fundo"
    if re.search(r"(?i)funda[çc][ãa]o|foundation|instituto|associa[çc][ãa]o|\bong\b|organiza[çc][ãa]o da sociedade civil|\boscip?\b", nome or ""):
        return "Fundação"
    return "Empresa"


def _dv_cnpj(base12: str) -> str:
    def dv(n: str) -> str:
        pesos = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2] if len(n) == 12 else [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        r = sum(int(a) * b for a, b in zip(n, pesos, strict=True)) % 11
        return "0" if r < 2 else str(11 - r)
    d1 = dv(base12)
    return d1 + dv(base12 + d1)


def matriz(cnpj: str) -> str:
    """R61 (3): a nota é da empresa, pelo CNPJ da MATRIZ (a raiz + 0001 + os dígitos verificadores)."""
    c = re.sub(r"\D", "", cnpj or "")
    if len(c) < 8:
        return cnpj
    base = c[:8] + "0001"
    return base + _dv_cnpj(base)


def pode_entrar(campos: dict, leis: list[str], financiadoras: set[str], nome: str | None) -> str | None:
    """R61 (6): a empresa NOVA só entra no cadastro com uma condição — lucro real; 100 ou mais empregados; lista oficial
    (a lei de incentivo confirmada); financiadora de livro; ou grupo de empresa já cadastrada (essa já se liga pela raiz do
    CNPJ e nem chega aqui). Devolve o motivo, ou None."""
    texto = " ".join(str(campos.get(k) or "") for k in ("situacao_cadastral", "grupo_economico", "obrigacoes_que_geram_recurso"))
    if re.search(r"(?i)lucro real", texto):
        return "lucro real"
    m = re.search(r"(?i)(\d[\d.]{1,8})\s*(?:\+\s*)?(?:empregad|funcion[áa]ri|colaborador)", texto)
    if m and int(m.group(1).replace(".", "")) >= 100:
        return "100 ou mais empregados"
    if leis:
        return "lista oficial (lei de incentivo confirmada)"
    if nome and _norm(nome) in financiadoras:
        return "financiadora de livro"
    return None


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


def _financiadoras(con: sqlite3.Connection) -> set[str]:
    """Os nomes dos financiadores dos livros (o órgão da esfera privada ou internacional e o financiador do catálogo de ouro)."""
    try:
        from ..cartorio.vinculo_empresa import PRIVADAS, _financiador
        return {_norm(n) for o, cat, esf in con.execute("SELECT l.orgao, d.catalogo_ouro, d.esfera FROM livro l JOIN livro_dados d ON d.livro_id = l.id")
                if (esf or "") in PRIVADAS for n in [_financiador(o, cat)] if n}
    except (sqlite3.Error, ImportError):
        return set()


LIMITE_NOVAS = 0.5   # C-08: mais da metade da pesquisa «nova no cadastro» é sinal de que o importador não reconheceu o cadastro


def importar_arquivo(caminho: Path, con: sqlite3.Connection, diario, agora: str, perfis: dict | None = None) -> dict[str, Any]:
    perfis = {} if perfis is None else perfis
    pac = json.loads(Path(caminho).read_text(encoding="utf-8"))
    from .ativas import ativas
    cad = {r[0]: (r[1], r[2], r[3]) for r in con.execute(f"SELECT cnpj, razao_social, uf, site FROM empresa WHERE {ativas(con)}")}
    por_raiz: dict[str, str] = {}
    for c in sorted(cad, key=lambda x: (x[8:12] != "0001", x)):   # a raiz liga à MATRIZ quando ela está no cadastro (R61, 3)
        if re.fullmatch(r"\d{8}(\d{6})?", c):
            por_raiz.setdefault(c[:8], c)
    por_nome = {}
    for c, (rs, _uf, _site) in cad.items():
        por_nome.setdefault(_norm(rs), c)
    for c, nf in con.execute(f"SELECT cnpj, nome_fantasia FROM empresa WHERE nome_fantasia IS NOT NULL AND {ativas(con)}"):
        por_nome.setdefault(_norm(nf), c)
    ja_lei = {(r[0], r[1]) for r in con.execute("SELECT cnpj, lei FROM incentivo")}
    financiadoras = _financiadoras(con)
    conta = {"empresas": 0, "novas_no_cadastro": 0, "sites": 0, "razoes_corrigidas": 0, "ufs_corrigidas": 0, "incentivos_novos": 0,
             "sem_cnpj": 0, "a_identificar": 0, "fora_do_filtro_de_entrada": 0, "goias_declarada": 0, "goias_so_unidade": 0}
    # C-08: a conferência antes de gravar — com o cadastro cheio, a pesquisa quase toda «nova» é o importador sem o cadastro
    if len(cad) > 1000:
        novas = sum(1 for rec in pac["empresas"] if not _resolver(rec, cad, por_raiz, por_nome))
        if novas > LIMITE_NOVAS * max(1, len(pac["empresas"])):
            return {"arquivo": Path(caminho).name, **conta, "parado": f"{novas} de {len(pac['empresas'])} seriam novas no cadastro "
                    f"({len(cad)} empresas): o importador não reconheceu o cadastro — nada foi gravado", "em": agora}
    for rec in pac["empresas"]:
        campos = rec.get("campos") or {}
        cnpj = _resolver(rec, cad, por_raiz, por_nome)
        nome = rec.get("razao_conferida") or rec.get("razao_no_sistema") or ""
        fonte = rec.get("fontes")
        fonte = (fonte[0] if isinstance(fonte, list) and fonte else fonte if isinstance(fonte, str) else None)
        fonte_txt = json.dumps(fonte, ensure_ascii=False) if fonte and not isinstance(fonte, str) else fonte
        leis = _leis(campos.get("leis_confirmadas"))
        if not cnpj:
            cnpjs = [re.sub(r"\D", "", c) for c in rec.get("cnpjs") or [] if len(re.sub(r"\D", "", c)) >= 8]
            motivo = None if not cnpjs else pode_entrar(campos, leis, financiadoras, nome)
            if not cnpjs or motivo is None:
                # R61 (3, 6): sem CNPJ não entra com «nome:…»; fora do filtro de entrada não entra — fica «a identificar»
                diario.emitir("empresa.a_identificar", "pesquisa-empresas", {
                    "nome": (nome or "sem nome")[:200], "cnpjs": json.dumps(cnpjs) if cnpjs else None, "pesquisa": pac.get("pesquisa") or "",
                    "motivo": "sem CNPJ" if not cnpjs else "fora do filtro de entrada (lucro real, 100+ empregados, lista oficial, "
                                                           "financiadora de livro ou grupo já cadastrado)",
                    "dados": json.dumps({"campos": campos, "fontes": rec.get("fontes")}, ensure_ascii=False)[:20000], "em": agora})
                conta["a_identificar"] += 1
                conta["sem_cnpj" if not cnpjs else "fora_do_filtro_de_entrada"] += 1
                continue
            cnpj = matriz(cnpjs[0])                               # R61 (3): a chave é o CNPJ da matriz
            nova = {"cnpj": cnpj, "razao_social": nome[:200] or cnpj, "nome_fantasia": None, "uf": sede_uf(campos, None),
                    "site": _url(campos.get("site_oficial")), "tipo": tipo_da(nome, campos), "descoberta_por": "titular",
                    "descoberta_em": agora, "atualizada_em": agora}
            diario.emitir("empresa.registrada", "pesquisa-empresas", nova)
            cad[cnpj] = (nome, nova["uf"], nova["site"])
            por_raiz.setdefault(cnpj[:8], cnpj)
            conta["novas_no_cadastro"] += 1
            uf_cad = nova["uf"]
        else:
            rs, uf, site = cad[cnpj]
            uf_cad = uf
            corr = {"cnpj": cnpj, "atualizada_em": agora, "tipo": tipo_da(nome or rs, campos)}
            novo_site, nova_uf = _url(campos.get("site_oficial")), sede_uf(campos, None)
            if novo_site and not site:
                corr["site"] = novo_site
                conta["sites"] += 1
            if nova_uf and nova_uf != uf:
                corr["uf"] = nova_uf                              # R61 (2): o estado da sede
                conta["ufs_corrigidas"] += 1
            if rec.get("razao_conferida") and _norm(rec["razao_conferida"]) != _norm(rs) and len(rec["razao_conferida"]) > 3:
                corr["razao_social"] = rec["razao_conferida"][:200]
                conta["razoes_corrigidas"] += 1
            diario.emitir("empresa.corrigida", "pesquisa-empresas", corr)
        declarada = atuacao_declarada(campos, fonte_txt)
        campos = {**campos, "atuacao_goias": atuacao_goias(campos, declarada)}
        if any(x["uf"] == "GO" for x in declarada):
            conta["goias_declarada"] += 1
        elif str((rec.get("campos") or {}).get("atuacao_goias") or "").upper().startswith("COMPROVADA"):
            conta["goias_so_unidade"] += 1                        # era «COMPROVADA» só por unidade, sede ou ICMS
        perfil = {"cnpj": cnpj, **{k: (str(campos.get(k))[:4000] if campos.get(k) else None) for k in CAMPOS},
                  "sede_uf": sede_uf(campos, uf_cad), "atuacao_declarada": json.dumps(declarada, ensure_ascii=False) if declarada else None,
                  "fontes": json.dumps(rec.get("fontes"), ensure_ascii=False)[:20000] if rec.get("fontes") else None,
                  "buscas": json.dumps(rec.get("buscas"), ensure_ascii=False)[:20000] if rec.get("buscas") else None,
                  "nao_encontrados": json.dumps(rec.get("nao_encontrados"), ensure_ascii=False)[:8000] if rec.get("nao_encontrados") else None,
                  "pesquisa": pac.get("pesquisa") or "", "pesquisado_em": agora}
        if cnpj in perfis:                                    # a mesma empresa em dois grupos: junta, não sobrescreve
            perfil = _juntar(perfis[cnpj], perfil, pac.get("pesquisa") or "")
        perfis[cnpj] = perfil
        diario.emitir("empresa.perfil", "pesquisa-empresas", perfil)
        for lei in leis:
            if (cnpj, lei) in ja_lei:
                continue
            inc = {"cnpj": cnpj, "lei": lei, "ano": _ano(campos.get("anos_destinou")), "valor": None, "comprovado": 1,
                   "fonte": f"pesquisa da empresa no Claude no Chrome ({pac.get('pesquisa')})", "em": agora}
            diario.emitir("incentivo.registrado", "pesquisa-empresas", inc)
            ja_lei.add((cnpj, lei))
            conta["incentivos_novos"] += 1
        apr = {"cnpj": cnpj, "piloto": "chrome", "o_que": "pesquisa da empresa financiadora",
               "achou": (campos.get("parecer_resumido") or campos.get("atuacao_goias") or "")[:2000], "fonte": fonte_txt, "em": agora}
        diario.emitir("aprofundamento.registrado", "pesquisa-empresas", apr)
        conta["empresas"] += 1
    return {"arquivo": Path(caminho).name, **conta, "em": agora}


def retirar_pessoas_fisicas(con: sqlite3.Connection, diario, agora: str) -> int:
    """R61 (5, titular, 18/11/2026): as pessoas físicas saem do cadastro de empresas — o identificador interno «E0:» (sem
    CNPJ) — por EXCLUSÃO LÓGICA (titular, 25/11/2026): a linha fica (R35) e nada mais a lê; o evento recusa outra chave."""
    try:
        from .ativas import ativas
        pf = [r[0] for r in con.execute(f"SELECT cnpj FROM empresa WHERE cnpj LIKE 'E0:%' AND {ativas(con)}")]
    except sqlite3.Error:
        return 0
    for c in pf:
        diario.emitir("empresa.retirada", "pesquisa-empresas", {"cnpj": c, "motivo": "pessoa física: sai do cadastro de empresas "
                                                                                     "(titular, 18/11/2026 — R61)", "em": agora})
    return len(pf)


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
    retiradas = retirar_pessoas_fisicas(con, diario, agora)
    if pasta.exists():
        for arq in sorted(pasta.glob("pesquisa-*.json")):
            if (feitos / (arq.stem + "-relatorio.json")).exists():       # importado uma vez (a lição da C-13)
                continue
            r = importar_arquivo(arq, con, diario, agora, perfis)
            saida.append(r)
            if r.get("parado"):                                          # C-08: a conferência parou — o arquivo fica para revisão
                diario.emitir("alarme.aberto", "pesquisa-empresas", {"gravidade": "alta", "modulo": "pesquisa-empresas", "aberto_em": agora,
                                                                    "mensagem": f"a pesquisa {arq.name} não foi importada: {r['parado']}"})
                continue
            feitos.mkdir(exist_ok=True)
            arq.rename(feitos / arq.name)
            (feitos / (arq.stem + "-relatorio.json")).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"importados": saida, "pessoas_fisicas_retiradas": retiradas, "ranking": classificar(con, diario, agora)}
