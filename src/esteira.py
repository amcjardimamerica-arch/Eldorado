"""ESTEIRA METÓDICA DE SELOS (titular, 02/10/2026) — config/esteira.json

  BRONZE  oportunidade identificada; o SITE OFICIAL ainda não foi confirmado. O Interceptador, no computador do titular,
          com Sonnet 5.5 (esforço baixo), reprocessa até 2 vezes; sem confirmação → Estante de Investigação Bronze.
  PRATA   site oficial confirmado; falta validar o edital, o PRAZO e os 12 DADOS (ou a dispensa deles). Opus 5.5 (esforço
          baixo) analisa até 2 vezes; sem validação → Estante de Investigação Prata.
  OURO    edital, condições e prazos completos → pronto para o Farol de Alexandria.

Confirmação do site oficial: (a) o Interceptador confirmou (esta esteira ou estudo comprovado anterior) ou (b) o endereço é
de domínio público (.gov.br, .leg.br, .jus.br, .mp.br, pncp.gov.br) e o classificador não o trata como republicador.
A rede neural ordena as filas (nota maior e prazo mais próximo primeiro) e a nota de cada etapa fica no histórico do selo.
Informação nova de um motor reabre o livro de uma estante (tentativas voltam a zero). O aprendizado fica no livro.
Fila de trabalho do computador do titular: docs/dados/esteira.json › filas · resultados: estado/esteira/resultados_local.jsonl
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config/esteira.json"
CAT = ROOT / "biblioteca_alexandria/fontes/motores.json"
RESULTADOS = ROOT / "estado/esteira/resultados_local.jsonl"
APLICADOS = ROOT / "estado/esteira/aplicados.json"
SAIDA = ROOT / "docs/dados/esteira.json"
DOMINIO_PUBLICO = re.compile(r"\.(gov|leg|jus|mp)\.br(/|$)|(^|//)(www\.)?pncp\.gov\.br")
DATA = re.compile(r"\b(\d{2}/\d{2}/20\d\d|20\d\d-\d{2}-\d{2})\b")


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return padrao


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def candidatos(x: dict) -> list[str]:
    us = [(x.get("esteira") or {}).get("site_oficial"), x.get("pagina")] + \
         [h.get("pagina_oficial") for h in (x.get("historico") or []) if isinstance(h, dict)]
    return [u for u in dict.fromkeys(u for u in us if u and str(u).startswith("http"))]


def site_confirmado(x: dict) -> tuple[bool, str | None, str]:
    """(confirmado, url, como)."""
    e = x.get("esteira") or {}
    if e.get("site_oficial") and e.get("site_confirmado_por"):
        return True, e["site_oficial"], e["site_confirmado_por"]
    if x.get("comprovado") or (x.get("interceptador") or {}).get("comprovado"):
        return True, x.get("pagina"), "Interceptador (estudo comprovado)"
    try:
        from .sites_oficiais import e_republicador
    except Exception:  # noqa: BLE001
        e_republicador = lambda u: False   # noqa: E731
    for u in candidatos(x):
        if DOMINIO_PUBLICO.search(str(u).lower()) and not e_republicador(u):
            return True, u, "domínio público oficial"
    return False, (candidatos(x) or [None])[0], "não confirmado"


def doze_dados(x: dict, cfg: dict) -> tuple[list[str], list[str]]:
    """(resolvidos, faltando) — resolvido = valor no livro ou dispensa registrada."""
    ck = (x.get("livro") or {}).get("checklist") or {}
    disp = {}
    for fonte in ((x.get("parametros") or {}).get("checklist"), (x.get("parametros") or {}).get("itens"), x.get("checklist12")):
        if isinstance(fonte, dict):
            for k, v in fonte.items():
                if isinstance(v, dict) and v.get("s") in ("ok", "disp", "val", "ref"):
                    disp[k] = v
    res, falta = [], []
    for item in cfg.get("doze_dados") or []:
        v = ck.get(item)
        (res if (isinstance(v, dict) and str(v.get("v") or "").strip()) or item in disp else falta).append(item)
    return res, falta


def prazo_definido(x: dict) -> bool:
    if x.get("regime_inscricao") == "contínuo" or str(x.get("regime_prazo") or "").startswith("permanente"):
        return True
    if any(h.get("fim") for h in (x.get("historico") or []) if isinstance(h, dict)):
        return True
    v = (((x.get("livro") or {}).get("checklist") or {}).get("Prazo de inscrição") or {}).get("v")
    return bool(v and DATA.search(str(v)))


def assinatura(x: dict) -> str:
    """Muda quando um motor traz informação nova ao livro (reabre a estante)."""
    h = [(d.get("pagina_oficial"), d.get("fim"), d.get("publicado_em")) for d in (x.get("historico") or []) if isinstance(d, dict)]
    ck = sorted(((k, (v or {}).get("v")) for k, v in ((x.get("livro") or {}).get("checklist") or {}).items()), key=str)
    return hashlib.sha1(json.dumps([h, ck], ensure_ascii=False, default=str).encode()).hexdigest()[:12]


def avaliar(x: dict, cfg: dict) -> dict:
    ok, url, como = site_confirmado(x)
    res, falta = doze_dados(x, cfg)
    pz = prazo_definido(x)
    nivel = "bronze" if not ok else ("ouro" if pz and not falta else "prata")
    return {"nivel": nivel, "site_oficial": url, "site_confirmado_por": como if ok else None, "prazo_definido": pz,
            "doze_resolvidos": len(res), "doze_faltando": falta}


def atualizar_livro(x: dict, cfg: dict, hoje: str) -> dict:
    e = x.setdefault("esteira", {})
    a = avaliar(x, cfg)
    sig = assinatura(x)
    if e.get("assinatura") and e["assinatura"] != sig and e.get("estante", "").startswith("investigacao"):
        e["tentativas_bronze"] = 0; e["tentativas_prata"] = 0                 # informação nova reabre a estante
        e.setdefault("historico", []).append({"em": hoje, "evento": "reaberto: informação nova de um motor"})
    e["assinatura"] = sig
    ant = e.get("selo")
    lim_b, lim_p = int(cfg["bronze"]["tentativas"]), int(cfg["prata"]["tentativas"])
    if a["nivel"] == "bronze":
        estante = "investigacao_bronze" if int(e.get("tentativas_bronze") or 0) >= lim_b else "fila_bronze"
    elif a["nivel"] == "prata":
        estante = "investigacao_prata" if int(e.get("tentativas_prata") or 0) >= lim_p else "fila_prata"
    else:
        estante = "farol"
    e.update({"selo": a["nivel"], "estante": estante, "prazo_definido": a["prazo_definido"], "doze_resolvidos": a["doze_resolvidos"],
              "doze_faltando": a["doze_faltando"], "avaliado_em": hoje})
    if a["site_confirmado_por"] and not e.get("site_confirmado_por"):
        e["site_oficial"], e["site_confirmado_por"] = a["site_oficial"], a["site_confirmado_por"]
    if ant != a["nivel"]:
        e.setdefault("historico", []).append({"em": hoje, "de": ant or "—", "para": a["nivel"], "nota_rede": x.get("nota_rede")})
        e["historico"] = e["historico"][-30:]
    return e


def aplicar_resultados(C: dict, cfg: dict, hoje: str) -> dict:
    """Aplica o que voltou do computador do titular (bronze: site oficial; prata: edital, prazos, 12 dados)."""
    if not RESULTADOS.exists():
        return {"aplicados": 0}
    feito = _j(APLICADOS, {"linhas": 0}); linhas = RESULTADOS.read_text(encoding="utf-8").splitlines()
    por_id = {x.get("id"): x for x in C.get("motores") or []}
    n = Counter()
    for l in linhas[int(feito.get("linhas") or 0):]:
        try:
            r = json.loads(l)
        except ValueError:
            continue
        x = por_id.get(r.get("livro"))
        if not x:
            continue
        e = x.setdefault("esteira", {})
        # 03/10 (titular): EDIÇÕES ANTERIORES trazidas pela verificação dos livros — alimentam a análise preditiva
        # (meses e valores em que o programa abriu). Entram no histórico sem repetir (mesma página e mesmo fim).
        for ed in (r.get("edicoes") or [])[:30]:
            if not isinstance(ed, dict) or not (ed.get("fim") or ed.get("inicio") or ed.get("ano")):
                continue
            chave = (str(ed.get("pagina_oficial") or ""), str(ed.get("fim") or ""), str(ed.get("ano") or ""))
            if any((str(h.get("pagina_oficial") or ""), str(h.get("fim") or ""), str(h.get("ano") or "")) == chave
                   for h in x.get("historico") or [] if isinstance(h, dict)):
                continue
            x.setdefault("historico", []).append({"id": "ver-" + hashlib.sha1(json.dumps(chave).encode()).hexdigest()[:8],
                                                  "titulo": str(ed.get("titulo") or x.get("programa") or "")[:200], "ano": ed.get("ano"),
                                                  "inicio": ed.get("inicio"), "fim": ed.get("fim"), "valor": ed.get("valor"),
                                                  "pagina_oficial": ed.get("pagina_oficial"), "origem": "verificação dos livros", "visto_em": hoje})
            n["edicoes_incluidas"] += 1
        if r.get("aprendizado"):
            e.setdefault("aprendizado", []).append({"em": r.get("em") or hoje, "etapa": r.get("etapa"), "modelo": r.get("modelo"),
                                                    "o_que_aprendeu": str(r["aprendizado"])[:600], "fontes": (r.get("fontes") or [])[:5]})
            e["aprendizado"] = e["aprendizado"][-20:]
        if r.get("etapa") == "bronze":
            if r.get("site_oficial") and r.get("confirmado_localmente"):
                e["site_oficial"] = r["site_oficial"]; e["site_confirmado_por"] = f"Interceptador local ({r.get('modelo')})"
                if r.get("url_edital"):
                    e["url_edital"] = r["url_edital"]
                n["bronze_confirmados"] += 1
            else:
                e["tentativas_bronze"] = int(e.get("tentativas_bronze") or 0) + 1; n["bronze_sem_sucesso"] += 1
        elif r.get("etapa") == "prata":
            ck = x.setdefault("livro", {}).setdefault("checklist", {})
            for item, v in (r.get("doze") or {}).items():
                if item in (cfg.get("doze_dados") or []) and str(v or "").strip():
                    ck[item] = {"v": str(v)[:300], "de": f"esteira prata ({r.get('modelo')})", "em": hoje}
            for item, motivo in (r.get("dispensas") or {}).items():
                x.setdefault("checklist12", {})[item] = {"s": "disp", "v": str(motivo)[:200], "de": "esteira prata"}
            if r.get("prazo_inscricao_fim"):
                x.setdefault("historico", []).append({"id": "prata-" + hashlib.sha1(str(r.get("url_edital")).encode()).hexdigest()[:8],
                                                      "titulo": x.get("programa"), "fim": r["prazo_inscricao_fim"], "inicio": r.get("prazo_inscricao_inicio"),
                                                      "pagina_oficial": r.get("url_edital") or e.get("site_oficial"), "origem": "esteira prata", "visto_em": hoje})
            if not r.get("edital_validado"):
                e["tentativas_prata"] = int(e.get("tentativas_prata") or 0) + 1; n["prata_sem_validacao"] += 1
            else:
                n["prata_validados"] += 1
    APLICADOS.parent.mkdir(parents=True, exist_ok=True)
    APLICADOS.write_text(json.dumps({"linhas": len(linhas), "em": _agora()}), encoding="utf-8")
    return {"aplicados": sum(n.values()), **n}


def filas(livros: list[dict], cfg: dict) -> dict:
    def ordem(x):
        fim = min([h.get("fim") for h in (x.get("historico") or []) if isinstance(h, dict) and h.get("fim") and h["fim"] >= date.today().isoformat()] or ["9999"])
        grupo = {"GO": 0, "BR": 1, "INT": 2}.get(x.get("geo"), 3)      # 02/10 (titular): Goiás → Brasil → internacional → outros
        return (grupo, -(x.get("nota_rede") or 0), fim)
    out = {}
    for etapa in ("bronze", "prata"):
        xs = sorted([x for x in livros if (x.get("esteira") or {}).get("estante") == f"fila_{etapa}"], key=ordem)[:int(cfg[etapa]["por_dia"])]
        out[etapa] = [{"livro": x["id"], "nome": x.get("nome_classificado") or x.get("programa"), "programa": x.get("programa"),
                       "orgao": x.get("orgao"), "uf": x.get("geo"), "candidatos": candidatos(x)[:5],
                       "site_oficial": (x.get("esteira") or {}).get("site_oficial"), "url_edital": (x.get("esteira") or {}).get("url_edital"),
                       "doze_faltando": (x.get("esteira") or {}).get("doze_faltando"), "nota_rede": x.get("nota_rede"),
                       "tentativa": int((x.get("esteira") or {}).get(f"tentativas_{etapa}") or 0) + 1,
                       "termos": ((x.get("chave_acionamento") or {}).get("termos") or [])[:4]} for x in xs]
    return out


def run(hoje: str | None = None, gravar: bool = True) -> dict:
    hoje = hoje or date.today().isoformat()
    cfg = _j(CFG, {}); C = _j(CAT, {})
    aplicado = aplicar_resultados(C, cfg, hoje) if gravar else {}
    livros = [x for x in C.get("motores") or [] if x.get("papel") != "fonte_de_busca"
              and (x.get("qualificacao") or {}).get("veredito") not in ("NÃO APLICA", "DESCARTADA")]
    for x in livros:
        atualizar_livro(x, cfg, hoje)
    cont = Counter((x["esteira"]["selo"], x["esteira"]["estante"]) for x in livros)
    F = filas(livros, cfg)
    out = {"em": _agora(), "regra": __doc__.split("Confirmação")[0].strip(),
           "selos": dict(Counter(x["esteira"]["selo"] for x in livros)),
           "estantes": {k: sum(v for (s, e), v in cont.items() if e == k) for k in ("fila_bronze", "investigacao_bronze", "fila_prata", "investigacao_prata", "farol")},
           "resultados_aplicados": aplicado, "filas": F,
           "ouro": [{"livro": x["id"], "nome": x.get("nome_classificado")} for x in livros if x["esteira"]["selo"] == "ouro"][:200]}
    if gravar:
        CAT.write_text(json.dumps(C, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"selos": out["selos"], "estantes": out["estantes"], "resultados_aplicados": aplicado}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=1))
