"""REPOSITÓRIO ÚNICO DE OPORTUNIDADES (titular, 11/10/2026).

UM registro por oportunidade, num ÚNICO lugar, independente do motor que a trouxe. Junta todas as origens — caixa dos
motores (abertas.json), fluxo (agregadores, Interceptador, Espião, oportunidades novas da revisão), vereditos da revisão
humana e do Chrome, certidões do Cartório (automáticas e manuais) e livros da Biblioteca. Duplicatas (revisão humana ou
regra M1 do saneamento) viram um registro só, com todos os ids de origem.

Cada registro leva:
  · ESTADO       validada · em_verificacao · validacao_manual (vermelho) · fechada (ruído, encerrada, fora do perfil,
                 duplicata, prazo vencido)
  · ESTANTE      sem_livro · bronze · prata · ouro — CLASSIFICADOR do livro da oportunidade (não separa os dados)
  · ITENS        os 12, cada um com a PROVA na fonte (valor + trecho + documento + página) ou dispensa justificada;
                 o que o motor leu sem prova fica como "não comprovado" — nenhum dado é criado
  · PRÓXIMO PASSO  decidido pela rede neural (aplica-se a OSC? prioridade) e pela skill da origem
                 (config/skills_extracao_origem.json); o Chrome é EXCEÇÃO — só depois das 10 abordagens do Cartório
Todos os painéis e filas derivam DESTE repositório (o mesmo universo): a tela inicial, a fila do Cartório e os lotes
do Chrome. A auditoria confere que os números batem.
Saída: dados/oportunidades/repositorio_unico.json e docs/dados/repositorio_resumo.json.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAIDA = ROOT / "dados/oportunidades/repositorio_unico.json"
RESUMO = ROOT / "docs/dados/repositorio_resumo.json"
DOZE = ["Objeto", "Prazo de inscrição", "Resultado", "Prazo de recurso", "Valor", "Órgão / financiador", "Território",
        "Esfera", "Requisitos", "Anexos", "Destinação", "Área de atuação"]
FECHADAS = ("ruido", "encerrada", "fora_perfil", "duplicata")
LIMIAR_OSC = 0.12            # rede neural: abaixo disso, sem prova e sem prazo → dispensa sugerida (não se aplica a OSC)


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao


def _agora() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _caixa() -> list[dict]:
    ab = _j(ROOT / "docs/dados/abertas.json", {})
    if not ab.get("campos"):
        return []
    cp, dc = ab["campos"], ab.get("dic") or {}
    def v(l, c):
        x = l[cp.index(c)]; return dc[c][x] if c in dc and isinstance(x, int) and x < len(dc[c]) else x
    out = []
    for l in ab["linhas"]:
        r = {c: v(l, c) for c in cp}
        if r.get("situacao") in ("aberta", "possivel") and r.get("tipo_registro") != "duplicata":
            out.append({"id": str(r["id"]), "titulo": r.get("titulo"), "url": r.get("url"), "fim": r.get("fim"), "orgao": r.get("orgao"),
                        "uf": r.get("uf"), "nivel": r.get("nivel"), "origem": "motor " + str(r.get("fonte_nome") or ""), "prazo_texto": r.get("prazo_texto"),
                        "_fonte": "caixa dos motores"})
    return out


def _fluxo() -> list[dict]:
    fl = _j(ROOT / "docs/dados/fluxo_oportunidades.json", {})
    return [{**x, "id": str(x["id"]), "_fonte": "fluxo"} for L in (fl.get("itens_por_uf") or {}).values() for x in L]


CHAMAMENTO = re.compile(r"(?i)edita(l|is)|chamamento|chamada|sele[çc][ãa]o|inscri[çc][õo]es|regulamento|pr[êe]mio|concurso|"
                        r"credenciamento|resid[êe]ncia|residency|open call|convocat[óo]ria|call for|grants?|bolsas?|fundo|"
                        r"programa de (acelera|apoio|fomento)|apoio a projetos|mecenas|festival|mostra|seleciona")
# ação JÁ REALIZADA pela empresa (doação feita, patrocínio dado, entrega) — não é oportunidade sem chamamento
REALIZADA = re.compile(r"(?i)\b(doa[çc](ão|ões)|doou|doam|entreg(a|ou|am)|transforma|benefici(a|ou|ará)|inaugur|patrocin(ou|a)\b|"
                       r"apoiou|arrecad|distribu(i|iu)|cobertores|cestas b[áa]sicas|campanha de doa)")


def _privada(r: dict) -> bool:
    """Registro da ramificação PRIVADA: Espião, agregadores de editais ou motores de empresas/incentivos/patrocínio."""
    o = str(r.get("origem") or "").lower()
    return bool(re.search(r"espi[ãa]o|agregador|patroc|incentiv|gife|empresa|salic|rouanet", o))


_MUN = re.compile(r"(?i)\bmunic[íi]pio d[eoa]s? |prefeitura (municipal )?d[eoa]s? |c[âa]mara municipal|secretaria municipal|"
                  r"fundo municipal|funda[çc][ãa]o cultural de|conselho municipal|\bmunicipal de ")
_DOM_UF = re.compile(r"https?://(?:www\.)?[\w.-]*?\.([a-z]{2})\.(?:gov|leg)\.br")
_ESTADOS = [("acre", "AC"), ("alagoas", "AL"), ("amap[aá]", "AP"), ("amazonas", "AM"), ("bahia", "BA"), ("cear[aá]", "CE"), ("esp[ií]rito santo", "ES"),
            ("maranh[aã]o", "MA"), ("mato grosso do sul", "MS"), ("minas gerais", "MG"), ("par[aá]", "PA"), ("para[ií]ba", "PB"), ("paran[aá]", "PR"),
            ("pernambuco", "PE"), ("piau[ií]", "PI"), ("rio de janeiro", "RJ"), ("rio grande do norte", "RN"), ("rio grande do sul", "RS"),
            ("rond[oô]nia", "RO"), ("roraima", "RR"), ("santa catarina", "SC"), ("s[aã]o paulo", "SP"), ("sergipe", "SE"), ("tocantins", "TO"),
            ("goi[aá]s", "GO"), ("distrito federal", "DF")]
UFS = {"AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"}


def municipal_fora_de_goias(r: dict, uf_agregador: str | None = None) -> str | None:
    """Identifica oportunidade MUNICIPAL de fora de Goiás (UF determinada e diferente de GO). 14/10/2026 (titular): roda a
    CADA rodada — só Goiás tem oportunidades municipais; de outros estados, só estaduais (e nacionais/internacionais).
    A municipal de outro estado é DESCARTADA do sistema (estado fechada: sai das abertas, da tela, das filas e não ganha
    livro). Sem UF determinada, fica (há municípios homônimos)."""
    t = f"{r.get('titulo') or ''} {r.get('orgao') or ''}"
    municipal = str(r.get("nivel") or "").lower() == "municipal" or bool(_MUN.search(t))
    if not municipal or str(r.get("nivel") or "").lower() in ("estadual", "federal", "internacional"):
        return None
    uf = str(r.get("uf") or uf_agregador or "").upper()
    if uf not in UFS:
        m = _DOM_UF.search(f"{r.get('link_oficial') or ''} {r.get('url') or ''}")
        uf = m.group(1).upper() if m and m.group(1).upper() in UFS else ""
    if uf not in UFS:                                  # nome do estado por extenso no endereço ou no título (um só)
        txt = re.sub(r"[-_/]", " ", f"{r.get('url') or ''} {r.get('link_oficial') or ''} {r.get('titulo') or ''}".lower())
        achados = {sig for nome, sig in _ESTADOS if re.search(rf"\b{nome}\b", txt)}
        if len(achados) == 1:
            uf = achados.pop()
    if uf and uf != "GO":
        return f"arquivada: municipal fora de Goiás ({uf}) — o livro fica guardado na Biblioteca"
    return None


def _oficial(url: str) -> bool:
    """A régua única do Cartório: agregador, notícia e republicador são só pista, nunca fonte."""
    try:
        from .cartorio_leitura import regua
        return bool(regua(str(url or ""))[0])
    except Exception:  # noqa: BLE001
        return False


def _skill(origem: str) -> str:
    o = str(origem or "").lower()
    for chave, k in (("pncp", "pncp"), ("querido", "querido_diario"), ("agregador", "agregador"), ("interceptador", "interceptador"),
                     ("espião", "espiao"), ("espiao", "espiao"), ("diário oficial", "diario_oficial"), ("dou", "diario_oficial"),
                     ("revisão", "revisao")):
        if chave in o:
            return k
    return "site_oficial"


def _nota(reg: dict) -> float | None:
    try:
        from .rede_neural import nota
        return nota({"titulo": reg.get("titulo"), "evidencia": reg.get("objeto") or "", "url": reg.get("url"), "origem": reg.get("origem")})
    except Exception:  # noqa: BLE001
        return None


def construir(gravar: bool = True, hoje: str | None = None) -> dict:
    hoje = hoje or date.today().isoformat()
    V = (_j(ROOT / "dados/editais/vereditos_revisao.json", {}) or {}).get("vereditos") or {}
    certs = dict((_j(ROOT / "estado/cartorio/certidoes.json", {}) or {}).get("certidoes") or {})
    for k, m in ((_j(ROOT / "estado/cartorio/certidoes_manuais.json", {}) or {}).get("certidoes") or {}).items():
        a = certs.get(k) or {}
        certs[k] = {**a, **m, "itens": {**(a.get("itens") or {}), **(m.get("itens") or {})}, "dispensas": {**(a.get("dispensas") or {}), **(m.get("dispensas") or {})}}
    livros = {}
    for m in (_j(ROOT / "biblioteca_alexandria/fontes/motores.json", {}) or {}).get("motores") or []:
        for h in m.get("historico") or []:
            if isinstance(h, dict) and h.get("id"):
                livros.setdefault(str(h["id"]), m)
    skills = (_j(ROOT / "config/skills_extracao_origem.json", {}) or {}).get("skills") or {}
    # 11/10 (titular): arquivamento ÚNICO — só as municipais de fora de GO abertas em 11/10 (lista fixa); as novas entram normalmente
    from .decisoes_titular import decisoes as _decisoes
    _DEC = _decisoes()
    uf_ag = {str(x.get("id")): x.get("uf") for x in ((_j(ROOT / "estado/agregadores/itens.json", {}) or {}).get("itens") or []) if x.get("uf")}
    _foto = _j(ROOT / "dados/oportunidades/arquivamento_municipais_2026-10-11.json", {}) or {}
    _arq_ids = {i: f"arquivada em 11/10/2026: municipal fora de Goiás ({o.get('uf')}) — o livro fica guardado"
                for o in (_foto.get("oportunidades") or []) for i in [o["id"], *(o.get("ids_origem") or [])]}
    # 11/10: o criador de livros já concluiu, para algumas, que não são seleção para OSC — o repositório usa o motivo
    disp_livro = {k: (v or {}).get("dispensa") for k, v in ((_j(ROOT / "estado/opressores_indice.json", {}) or {}).get("indice") or {}).items() if (v or {}).get("dispensa")}

    # 1 · todas as origens num só conjunto, com o id canônico (duplicatas fundidas)
    brutos = _fluxo() + _caixa()
    try:
        from .opressores_repositorio import canonica_por_revisao
        canon = canonica_por_revisao()
    except Exception:  # noqa: BLE001
        canon = {}
    try:
        from .saneamento_motores import agrupar_duplicatas
        for d, inf in (agrupar_duplicatas(brutos) or {}).items():
            c = (inf or {}).get("canonico") if isinstance(inf, dict) else inf
            if c and str(c) != str(d):
                canon.setdefault(str(d), str(c))
    except Exception:  # noqa: BLE001
        pass
    reg: dict[str, dict] = {}
    for b in brutos:
        cid = canon.get(b["id"], b["id"])
        r = reg.setdefault(cid, {"id": cid, "ids_origem": [], "fontes": [], "titulo": None, "url": None, "link_oficial": None, "fim": None,
                                 "inicio": None, "orgao": None, "uf": None, "origem": None, "checklist": {}})
        if b["id"] not in r["ids_origem"]:
            r["ids_origem"].append(b["id"])
        f = f"{b['_fonte']}: {b.get('origem') or ''}".strip(": ")
        if f not in r["fontes"]:
            r["fontes"].append(f)
        for k in ("titulo", "url", "link_oficial", "fim", "inicio", "orgao", "uf", "origem", "objeto", "prazo_texto", "nivel"):
            if not r.get(k) and b.get(k):
                r[k] = b[k]
        for k, v in (b.get("checklist") or {}).items():
            r["checklist"].setdefault(k, v)

    # 2 · estado, prova dos 12 itens, estante, próximo passo (rede neural + skill da origem)
    from .criterio_selos import nivel, dispensa_valida
    out = []
    for cid, r in reg.items():
        ver = None
        for i in [cid] + r["ids_origem"]:
            if (V.get(i) or {}).get("veredito"):
                ver = V[i]; break
        c = {}
        for i in [cid] + r["ids_origem"]:
            ci = certs.get(f"estrela:{i}")
            if ci:
                c = {**ci, "itens": {**(c.get("itens") or {}), **(ci.get("itens") or {})}, "dispensas": {**(c.get("dispensas") or {}), **(ci.get("dispensas") or {})},
                     "link_oficial": c.get("link_oficial") or ci.get("link_oficial"), "tentativa": max(int(c.get("tentativa") or 0), int(ci.get("tentativa") or 0)),
                     "esgotada": c.get("esgotada") or ci.get("esgotada"), "encaminhado": c.get("encaminhado") or ci.get("encaminhado")}
        inv = {}
        for i in [cid] + r["ids_origem"]:                     # 11/10: o que o INTERCEPTADOR comprovou volta ao banco
            _ex = _j(ROOT / "dados/editais/extraidos" / f"{i}.json", {})
            if (_ex.get("investigacao_ia") or {}).get("campos"):
                inv = _ex["investigacao_ia"]["campos"]; break
        itens = {}
        for k in DOZE:
            it = (c.get("itens") or {}).get(k); dp = (c.get("dispensas") or {}).get(k); ck = r["checklist"].get(k) or {}
            iv = inv.get(k) or {}
            if not it and str(iv.get("comprovado")) == "True" and iv.get("trecho") and iv.get("fonte"):
                if _oficial(iv["fonte"]):
                    it = {"valor": iv.get("valor"), "trecho": iv.get("trecho"), "documento": iv.get("fonte"), "pagina": iv.get("pagina"), "por": "Interceptador"}
                elif not (ck.get("s") in ("ok", "val", "dt") and ck.get("v")):
                    ck = {"s": "ok", "v": f"{str(iv.get('valor') or '')[:80]} (Interceptador leu em agregador: {str(iv['fonte'])[:60]})"}
            if it and (it.get("trecho") or it.get("valor")):
                itens[k] = {"estado": "comprovado", "valor": it.get("valor"), "trecho": it.get("trecho"), "documento": it.get("documento"), "pagina": it.get("pagina")}
            elif dp and dispensa_valida(dp.get("motivo") or ""):
                itens[k] = {"estado": "dispensado", "motivo": dp.get("motivo"), "documentos_lidos": dp.get("documentos_lidos")}
            elif ck.get("s") in ("ok", "val", "dt") and ck.get("v"):
                itens[k] = {"estado": "nao_comprovado", "valor": ck.get("v"), "nota": "lido pelo motor; falta a prova no documento oficial"}
            else:
                itens[k] = {"estado": "falta"}
        prova = {k: {"s": "ok", "v": str(v.get("valor") or "comprovado na fonte")} if v["estado"] == "comprovado" else {"s": "disp", "v": v.get("motivo") or ""} if v["estado"] == "dispensado" else {"s": "falta"}
                 for k, v in itens.items()}
        selo = nivel(prova)
        link = c.get("link_oficial") or r.get("link_oficial")
        fim = r.get("fim") or (((c.get("itens") or {}).get("Prazo de inscrição") or {}).get("fim"))
        v = (ver or {}).get("veredito")
        _mun = next((_arq_ids[i] for i in [cid] + r["ids_origem"] if i in _arq_ids), None)   # só a lista fixa de 11/10
        if not _mun:                       # 12/10 (titular): decidida no painel (inscrita ou descartada) sai das abertas; o livro fica
            from .decisoes_titular import marca_no_repositorio
            _mun = marca_no_repositorio([cid] + r["ids_origem"], _DEC)
        _fora = municipal_fora_de_goias(r, next((uf_ag[i] for i in [cid] + r["ids_origem"] if i in uf_ag), None))
        if v in FECHADAS:
            estado, motivo = "fechada", f"veredito: {v}"
        elif _fora:                                        # 14/10 (titular): só Goiás tem oportunidades municipais
            _uf = (re.search(r"\(([A-Z]{2})\)", _fora) or [None, "?"])[1]
            estado, motivo = "fechada", f"descartada: oportunidade municipal de outro estado ({_uf}) — só Goiás tem oportunidades municipais"
        elif fim and str(fim)[:10] < hoje:
            estado, motivo = "fechada", "prazo vencido"
        elif selo == "ouro" and link:                       # prova completa na fonte supera qualquer marcação anterior
            estado, motivo = "validada", "12/12 com prova na fonte ou dispensa justificada"
        elif v == "validacao_manual":
            estado, motivo = "validacao_manual", str((ver or {}).get("motivo") or "")[:200]
        elif v == "ouro" or (r.get("confirmada") and link and all(itens[k]["estado"] == "comprovado" for k in ("Objeto", "Prazo de inscrição"))):
            # Dr. Otávio: "confirmada" pelo motor só vale com objeto e prazo COMPROVADOS no documento oficial
            estado, motivo = "validada", "ouro na revisão" if v == "ouro" else "objeto e prazo comprovados no documento oficial + site oficial"
        else:
            estado, motivo = "em_verificacao", ""
        lv = livros.get(cid) or next((livros[i] for i in r["ids_origem"] if i in livros), None)
        # 11/10 (titular): a BIBLIOTECA direciona a busca — editais anteriores do livro e páginas onde o órgão publica
        anteriores = [h for h in ((lv or {}).get("historico") or []) if isinstance(h, dict) and str(h.get("id")) not in [cid] + r["ids_origem"]]
        onde = list(dict.fromkeys(u for u in [link, (lv or {}).get("pagina_aprendida"), (lv or {}).get("pagina"), ((lv or {}).get("parametros") or {}).get("fonte_oficial")]
                                  + [h.get("pagina_oficial") or h.get("url") for h in anteriores[-5:]] if u))[:8]
        estante = "sem_livro" if not lv else (selo if selo in ("ouro", "prata", "bronze") else "bronze")
        sk = _skill(r.get("origem"))
        sem_livro = next((disp_livro[i] for i in [cid] + r["ids_origem"] if i in disp_livro), None) if not lv else None
        faltam = [k for k, x in itens.items() if x["estado"] in ("falta", "nao_comprovado")]
        nt = _nota(r) if estado == "em_verificacao" else None
        if estado != "em_verificacao":
            passo = {"fechada": "nenhum (fechada)", "validada": "acompanhar o prazo", "validacao_manual": "validação manual pela titular"}[estado]
        elif (_privada(r) and REALIZADA.search(f"{r.get('titulo') or ''} {r.get('objeto') or ''}")
              and not CHAMAMENTO.search(f"{r.get('titulo') or ''} {r.get('objeto') or ''}") and not any(x["estado"] == "comprovado" for x in itens.values())):
            passo = "dispensar: empresa sem chamamento (doação, patrocínio ou ação já realizada não é oportunidade) — confirmar na fonte"
        elif sem_livro and re.match(r"(?i)n[ãa]o [ée] sele[çc][ãa]o aberta|empresa sem edital", sem_livro):
            passo = f"dispensar: {sem_livro[:120]} — confirmar na fonte"
        elif nt is not None and nt < LIMIAR_OSC and not fim and not any(x["estado"] == "comprovado" for x in itens.values()):
            passo = f"dispensar: a rede neural indica que não se aplica a OSC (nota {nt}) — confirmar na fonte"
        elif not link and not onde:
            passo = "Interceptador: achar o site oficial (sem pista no livro nem certidão — pesquisa na web é a rota)"
        elif not link and int(c.get("tentativa") or 0) >= 2:
            passo = f"Interceptador: achar o site oficial (o Cartório não achou em {int(c.get('tentativa') or 0)} abordagens; buscar em: {', '.join(onde[:2]) or 'livro sem página'})"
        elif link and int(c.get("tentativa") or 0) >= 5 and len(faltam) > 2 and _parado_ha(cid, hoje) <= 7:
            passo = f"Interceptador: completar {len(faltam)} item(ns) a partir do site oficial certificado"
        elif not link:
            passo = f"Cartório: achar o site oficial ({sk}: {(skills.get(sk) or {}).get('como', '')[:90]})"
        elif int(c.get("tentativa") or 0) >= 5 and _parado_ha(cid, hoje) > 7:
            passo = "Busca externa (Claude/Chrome): 5+ abordagens do Cartório sem resolver e parada há mais de 7 dias"
        elif int(c.get("tentativa") or 0) < 10 and not c.get("esgotada"):
            passo = f"Cartório: abordagem {int(c.get('tentativa') or 0) + 1} de 10 para {len(faltam)} item(ns) ({sk})"
        else:
            passo = "Busca externa (Claude/Chrome): as 10 abordagens do Cartório se esgotaram"
        urg = 0 if (fim and str(fim)[:10] >= hoje) else 1
        pronta = estado == "validada" and bool(lv) and bool(fim and str(fim)[:10] >= hoje)
        etapa, ferramenta = _etapa(estado, passo, bool(lv), pronta)
        out.append({"id": cid, "ids_origem": r["ids_origem"], "fontes": r["fontes"], "titulo": str(r.get("titulo") or "")[:220], "url": r.get("url"),
                    "link_oficial": link, "orgao": r.get("orgao"), "uf": r.get("uf"), "fim": fim, "origem": r.get("origem"), "skill": sk,
                    "estado": estado, "motivo_estado": motivo, "estante": estante, "livro": (lv or {}).get("id"), "motivo_sem_livro": sem_livro, "selo_dos_itens": selo or "sem_selo",
                    "itens": itens, "faltam": faltam, "cartorio": {"tentativas": int(c.get("tentativa") or 0), "esgotada": bool(c.get("esgotada"))},
                    "arquivada": _mun,            # 11/10: SÓ contador e telas — motores, Cartório e Interceptador seguem
                    "nota_rede": nt, "proximo_passo": passo, "etapa": etapa, "ferramenta": ferramenta, "pronta_para_farol": pronta,
                    "livro_historico": {"editais_anteriores": len(anteriores), "ultimos": [{"id": h.get("id"), "titulo": str(h.get("titulo") or "")[:120], "fim": h.get("fim"),
                                        "pagina": h.get("pagina_oficial") or h.get("url")} for h in anteriores[-3:]]}, "onde_buscar": onde, "prioridade": (urg, str(fim or "9999"), -(nt or 0))})
    ant = {x["id"]: x for x in (_j(SAIDA, {}).get("registros") or [])}       # Prof. Caio: ninguém parado sem dono
    for x in out:
        a = ant.get(x["id"]) or {}
        mesmo = a.get("proximo_passo", "").split(" (")[0] == x["proximo_passo"].split(" (")[0] and a.get("estado") == x["estado"]
        x["no_passo_desde"] = a.get("no_passo_desde") if (mesmo and a.get("no_passo_desde")) else hoje
        dias = (date.fromisoformat(hoje) - date.fromisoformat(x["no_passo_desde"][:10])).days
        x["estagnado"] = x["estado"] == "em_verificacao" and dias > 3
        if x["estagnado"]:
            x["prioridade"] = (0,) + tuple(x["prioridade"][1:])
    out.sort(key=lambda x: (x["estado"] != "em_verificacao", x["prioridade"]))
    for x in out:
        x["prioridade"] = list(x["prioridade"])
    resumo = resumir(out)
    resumo["auditoria"] = auditar(resumo)
    if gravar:
        SAIDA.parent.mkdir(parents=True, exist_ok=True)
        SAIDA.write_text(json.dumps({"em": _agora(), "regra": (__doc__ or "").split("\n\n")[0], "total": len(out), "registros": out}, ensure_ascii=False, indent=1), encoding="utf-8")
        RESUMO.parent.mkdir(parents=True, exist_ok=True)
        RESUMO.write_text(json.dumps(resumo, ensure_ascii=False, indent=1), encoding="utf-8")
    return resumo


ETAPAS = {1: "acionamento do motor (maestro, agenda e rede neural)", 2: "coleta pelo motor ou Piloto", 3: "repositório único (sem duplicatas)",
          4: "pertinência a OSC (rede neural e saneamento)", 5: "livro na Biblioteca (criado ou vinculado)", 6: "site oficial (Cartório e Interceptador)",
          7: "certificação dos 12 itens na fonte (Cartório e Interceptador)", 8: "verificação externa definitiva (Claude, exceção)", 9: "pronta para o Farol de Alexandria"}


def _etapa(estado: str, passo: str, tem_livro: bool, pronta: bool) -> tuple[str, str]:
    """A etapa da esteira mestre e a ferramenta que age agora (sem passo parado sem dono)."""
    if estado == "fechada":
        return "fim: fechada (arquivada ou eliminada)", "Biblioteca (livro guardado)"
    if pronta:
        return f"9 · {ETAPAS[9]}", "Farol de Alexandria (preparação da proposta)"
    if passo.startswith("dispensar"):
        return f"4 · {ETAPAS[4]}", "saneamento + rede neural (confirmar na fonte e dispensar)"
    if passo.startswith(("Busca externa", "validação manual")):
        return f"8 · {ETAPAS[8]}", "Claude (busca externa) ou titular (vermelho)"
    if estado == "validada" and not tem_livro:
        return f"5 · {ETAPAS[5]}", "criador de livros (opressores_repositorio)"
    if estado == "validada":
        return f"9 · {ETAPAS[9]} (aguarda prazo vigente)", "acompanhamento do prazo"
    if "achar o site oficial" in passo:
        return f"6 · {ETAPAS[6]}", "Interceptador" if passo.startswith("Interceptador") else "Cartório"
    return f"7 · {ETAPAS[7]}", "Interceptador" if passo.startswith("Interceptador") else "Cartório"


_ANT: dict = {}


def _parado_ha(cid: str, hoje: str) -> int:
    """Dias no mesmo passo, pelo repositório anterior (Prof. Caio)."""
    if "m" not in _ANT:
        _ANT["m"] = {x["id"]: x.get("no_passo_desde") for x in (_j(SAIDA, {}).get("registros") or [])}
    d = _ANT["m"].get(cid)
    try:
        return (date.fromisoformat(hoje) - date.fromisoformat(str(d)[:10])).days if d else 0
    except ValueError:
        return 0


def resumir(out: list[dict]) -> dict:
    # 11/10 (titular): as ARQUIVADAS (municipais de fora de GO) saem do contador e das telas, mas seguem nas filas dos
    # motores, do Cartório e do Interceptador e o livro continua vigiado
    ab = [x for x in out if x["estado"] != "fechada" and not x.get("arquivada")]
    passo = Counter(re.sub(r"\s*\(.*$|\s+\d+ de 10.*$|: a rede.*$|: as 10.*$", "", x["proximo_passo"]) for x in ab)
    return {"em": _agora(), "regra": "um registro por oportunidade, num único lugar; abertas = validadas + em verificação + validação manual",
            "registros": len(out), "abertas": len(ab),
            "validadas": sum(1 for x in ab if x["estado"] == "validada"), "em_verificacao": sum(1 for x in ab if x["estado"] == "em_verificacao"),
            "validacao_manual": sum(1 for x in ab if x["estado"] == "validacao_manual"), "fechadas": sum(1 for x in out if x["estado"] == "fechada"),
            "arquivadas_municipais_fora_de_goias": sum(1 for x in out if x.get("arquivada")),
            "estantes": dict(Counter(x["estante"] for x in ab)), "proximo_passo": dict(passo.most_common()),
            "por_origem": dict(Counter(x["skill"] for x in ab if x["estado"] == "em_verificacao")),
            "itens_em_verificacao": dict(Counter(st for x in ab if x["estado"] == "em_verificacao" for st in (i["estado"] for i in x["itens"].values()))),
            "fila_chrome": sum(1 for x in ab if x["proximo_passo"].startswith("Busca externa")),
            "fila_interceptador": sum(1 for x in ab if x["proximo_passo"].startswith("Interceptador")),
            "prontas_para_o_farol": sum(1 for x in ab if x.get("pronta_para_farol")),
            "por_etapa": dict(Counter(str(x.get("etapa", "")).split(" (")[0] for x in ab).most_common()),
            "fila_busca_externa": sum(1 for x in ab if x["proximo_passo"].startswith("Busca externa")),
            "cruzamento": {"com_certidao": sum(1 for x in ab if any(i["estado"] in ("comprovado", "dispensado") for i in x["itens"].values())),
                           "com_livro": sum(1 for x in ab if x["livro"]), "com_livro_de_editais_anteriores": sum(1 for x in ab if x["livro_historico"]["editais_anteriores"]),
                           "em_verificacao_com_onde_buscar_do_livro": sum(1 for x in ab if x["estado"] == "em_verificacao" and x["livro_historico"]["editais_anteriores"])},
            "dispensa_sugerida": sum(1 for x in ab if x["proximo_passo"].startswith("dispensar")),
            "motivo_sem_livro": dict(Counter(re.sub(r"[:(].*$", "", x.get("motivo_sem_livro") or "sem motivo registrado (o criador cria na próxima rodada)").strip()
                                             for x in ab if x["estante"] == "sem_livro"))}


def auditar(resumo: dict) -> dict:
    """Dra. Irene: todos os painéis e filas contam o MESMO universo? Divergência vira alerta no resumo."""
    alertas = []
    fl = (_j(ROOT / "docs/dados/fluxo_oportunidades.json", {}) or {}).get("parametro") or {}
    if fl and fl.get("abertas") not in (None, resumo["abertas"]):
        alertas.append(f"tela inicial (fluxo) conta {fl.get('abertas')} abertas; o repositório conta {resumo['abertas']} — a tela passa a ler o repositório")
    cart = ((_j(ROOT / "docs/dados/cartorio.json", {}) or {}).get("linha_de_producao") or {}).get("fila_oportunidades")
    if cart is not None and cart > resumo["abertas"]:
        alertas.append(f"fila do Cartório ({cart}) maior que as abertas do repositório ({resumo['abertas']}) — o Cartório passa a ler a fila do repositório")
    lote = ROOT / "dados/revisoes/fila_chrome_atual/lote.json"
    if lote.exists():
        n = len((_j(lote, {}) or {}).get("registros") or [])
        if n != resumo["fila_chrome"]:
            alertas.append(f"lote do Chrome com {n} registros; a fila do Chrome no repositório tem {resumo['fila_chrome']}")
    return {"ok": not alertas, "alertas": alertas, "regra": "um único universo: tela, Cartório e Chrome derivam do repositório"}


def fila(passo_prefixo: str) -> list[dict]:
    """Uma fila derivada do repositório (Cartório, Chrome…) — o mesmo universo da tela inicial."""
    return [x for x in (_j(SAIDA, {}).get("registros") or []) if x["estado"] == "em_verificacao" and x["proximo_passo"].startswith(passo_prefixo)]


REGRA_EXTERNA = ("Toda busca externa termina em UMA de três resoluções: (1) ARQUIVAR — o prazo de inscrição venceu (comprovado no "
                 "documento oficial): veredito 'encerrada'; o livro é atualizado com a edição e guardado; (2) ELIMINAR — não se aplica a "
                 "associações/OSC: veredito 'ruido' ou 'fora_perfil', com o motivo; (3) COMPLETAR — os 12 itens comprovados na fonte ou "
                 "com dispensa justificada (expressa: o edital diz que não se aplica; não consta: o edital não fala, com os documentos "
                 "lidos): veredito 'ouro'. 'validacao_manual' só se o documento oficial não pôde ser lido por nenhuma das 8 rotas. "
                 "Resultado parcial (prata, bronze, pendente) não é aceito: volta à fila como resolução incompleta.")


if __name__ == "__main__":
    print(json.dumps(construir(), ensure_ascii=False, indent=1))
