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
        for k in ("titulo", "url", "link_oficial", "fim", "inicio", "orgao", "uf", "origem", "objeto", "prazo_texto"):
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
        itens = {}
        for k in DOZE:
            it = (c.get("itens") or {}).get(k); dp = (c.get("dispensas") or {}).get(k); ck = r["checklist"].get(k) or {}
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
        if v in FECHADAS:
            estado, motivo = "fechada", f"veredito: {v}"
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
        onde = list(dict.fromkeys(u for u in [link, (lv or {}).get("pagina"), ((lv or {}).get("parametros") or {}).get("fonte_oficial")]
                                  + [h.get("pagina_oficial") or h.get("url") for h in anteriores[-5:]] if u))[:8]
        estante = "sem_livro" if not lv else (selo if selo in ("ouro", "prata", "bronze") else "bronze")
        sk = _skill(r.get("origem"))
        sem_livro = next((disp_livro[i] for i in [cid] + r["ids_origem"] if i in disp_livro), None) if not lv else None
        faltam = [k for k, x in itens.items() if x["estado"] in ("falta", "nao_comprovado")]
        nt = _nota(r) if estado == "em_verificacao" else None
        if estado != "em_verificacao":
            passo = {"fechada": "nenhum (fechada)", "validada": "acompanhar o prazo", "validacao_manual": "validação manual pela titular"}[estado]
        elif sem_livro and re.match(r"(?i)n[ãa]o [ée] sele[çc][ãa]o aberta|empresa sem edital", sem_livro):
            passo = f"dispensar: {sem_livro[:120]} — confirmar na fonte"
        elif nt is not None and nt < LIMIAR_OSC and not fim and not any(x["estado"] == "comprovado" for x in itens.values()):
            passo = f"dispensar: a rede neural indica que não se aplica a OSC (nota {nt}) — confirmar na fonte"
        elif not link:
            passo = f"Cartório: achar o site oficial ({sk}: {(skills.get(sk) or {}).get('como', '')[:90]})"
        elif int(c.get("tentativa") or 0) >= 5 and _parado_ha(cid, hoje) > 7:
            passo = "Busca externa (Claude/Chrome): 5+ abordagens do Cartório sem resolver e parada há mais de 7 dias"
        elif int(c.get("tentativa") or 0) < 10 and not c.get("esgotada"):
            passo = f"Cartório: abordagem {int(c.get('tentativa') or 0) + 1} de 10 para {len(faltam)} item(ns) ({sk})"
        else:
            passo = "Busca externa (Claude/Chrome): as 10 abordagens do Cartório se esgotaram"
        urg = 0 if (fim and str(fim)[:10] >= hoje) else 1
        out.append({"id": cid, "ids_origem": r["ids_origem"], "fontes": r["fontes"], "titulo": str(r.get("titulo") or "")[:220], "url": r.get("url"),
                    "link_oficial": link, "orgao": r.get("orgao"), "uf": r.get("uf"), "fim": fim, "origem": r.get("origem"), "skill": sk,
                    "estado": estado, "motivo_estado": motivo, "estante": estante, "livro": (lv or {}).get("id"), "motivo_sem_livro": sem_livro, "selo_dos_itens": selo or "sem_selo",
                    "itens": itens, "faltam": faltam, "cartorio": {"tentativas": int(c.get("tentativa") or 0), "esgotada": bool(c.get("esgotada"))},
                    "nota_rede": nt, "proximo_passo": passo,
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
    ab = [x for x in out if x["estado"] != "fechada"]
    passo = Counter(re.sub(r"\s*\(.*$|\s+\d+ de 10.*$|: a rede.*$|: as 10.*$", "", x["proximo_passo"]) for x in ab)
    return {"em": _agora(), "regra": "um registro por oportunidade, num único lugar; abertas = validadas + em verificação + validação manual",
            "registros": len(out), "abertas": len(ab),
            "validadas": sum(1 for x in ab if x["estado"] == "validada"), "em_verificacao": sum(1 for x in ab if x["estado"] == "em_verificacao"),
            "validacao_manual": sum(1 for x in ab if x["estado"] == "validacao_manual"), "fechadas": sum(1 for x in out if x["estado"] == "fechada"),
            "estantes": dict(Counter(x["estante"] for x in ab)), "proximo_passo": dict(passo.most_common()),
            "por_origem": dict(Counter(x["skill"] for x in ab if x["estado"] == "em_verificacao")),
            "itens_em_verificacao": dict(Counter(st for x in ab if x["estado"] == "em_verificacao" for st in (i["estado"] for i in x["itens"].values()))),
            "fila_chrome": sum(1 for x in ab if x["proximo_passo"].startswith("Busca externa")),
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
