#!/usr/bin/env python3
"""IMPORTA a revisão das oportunidades abertas (prompts PARTE 1/2/3, 10/10/2026) para o sistema.

Entrada: uma pasta com `resultado_ABERTAS_<parte>_<lote>.json` (formato dos prompts, mesmo das certidões).
Saídas:
  1. dados/editais/vereditos_revisao.json — o veredito humano por id (ruido, fora_perfil, encerrada, duplicata,
     ouro/prata/bronze/pendente), que o saneamento (src/saneamento_motores.py) aplica ANTES de qualquer regra automática;
  2. estado/cartorio/certidoes.json — certidão `estrela:<id>` com os itens certificados (valor + trecho + documento +
     página) das vigentes e pendentes. Item que o Cartório já tinha certificado é mantido; os novos se somam.
     Dispensa sem justificativa de "não se aplica" é RECUSADA (regra permanente de 04/10, src/criterio_selos.py);
  3. dados/editais/derivadas_revisao.json — oportunidades novas achadas na revisão (`novo-…`), como pista com fonte
     oficial, para o motor da área confirmar e gravar.

USO (na raiz do repositório):
    python scripts/importar_revisao_abertas.py dados/revisoes/abertas_p1_go_2026_10_10 --verificar   # só confere
    python scripts/importar_revisao_abertas.py dados/revisoes/abertas_p1_go_2026_10_10               # importa
É idempotente: rodar de novo não duplica nada.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.criterio_selos import DOZE, dispensa_valida, nivel  # noqa: E402

VEREDITOS = ROOT / "dados/editais/vereditos_revisao.json"
DERIVADAS = ROOT / "dados/editais/derivadas_revisao.json"
# 10/10 (implantação): as certidões da revisão humana vão para um arquivo PRÓPRIO, que o Cartório incorpora a cada
# execução (a revisão humana prevalece). Gravar direto em estado/cartorio/certidoes.json se perdia: o fluxo do
# Cartório regrava esse arquivo de hora em hora.
CERTIDOES = ROOT / "estado/cartorio/certidoes_manuais.json"
VIGENTES = ("ouro", "prata", "bronze", "pendente")


def _agora() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ler_lotes(pasta: Path) -> dict:
    regs: dict = {}
    for arq in sorted(pasta.glob("resultado_ABERTAS_*.json")):
        corpo = json.loads(arq.read_text(encoding="utf-8"))
        if isinstance(corpo, list):
            itens = corpo
        elif any(k in corpo for k in ("resultados", "itens", "registros", "resultado")):   # "resultado": formato da Parte 2
            itens = corpo.get("resultados") or corpo.get("itens") or corpo.get("registros") or corpo.get("resultado") or []
        else:                                                        # formato dos lotes: {id: registro}
            itens = corpo
        if isinstance(itens, dict):
            itens = [{"id": k, **v} for k, v in itens.items() if isinstance(v, dict)]
        for x in itens:
            if x.get("id"):
                regs[str(x["id"])] = {**x, "_lote": arq.name}
    return regs


def _item_ok(v) -> bool:
    """Valor + trecho literal + documento; a PÁGINA é exigida só de PDF (página de site/HTML não tem número de página —
    a mesma regra do Cartório). 10/10: sem isso, itens certificados em páginas oficiais das Partes 2 e 3 eram ignorados."""
    if not (isinstance(v, dict) and all(str(v.get(k) or "").strip() for k in ("valor", "trecho", "documento"))):
        return False
    doc = str(v.get("documento") or "").lower().split("?")[0]
    eh_pdf = doc.endswith(".pdf") or "pdf" in str(v.get("metodo") or "").lower()
    return v.get("pagina") not in (None, "") or not eh_pdf


def certidao_de(x: dict, origem: str) -> tuple[dict, list[str]]:
    avisos, itens, disp = [], {}, {}
    for k, v in (x.get("itens") or {}).items():
        if k not in DOZE:
            avisos.append(f"{x['id']}: item fora dos 12 ignorado ({k})"); continue
        if _item_ok(v):
            itens[k] = {"valor": str(v["valor"]), "trecho": str(v["trecho"]), "pagina": v["pagina"],
                        "documento": v["documento"], "metodo": v.get("metodo") or "revisão manual (leitura do documento oficial)"}
        else:
            avisos.append(f"{x['id']}: item {k} sem valor/trecho/documento/página — ignorado")
    for k, v in (x.get("dispensas") or {}).items():
        motivo = str((v or {}).get("motivo") or (v or {}).get("valor") or "")
        if k in DOZE and k not in itens and dispensa_valida(motivo) and (v or {}).get("trecho"):
            disp[k] = {"motivo": motivo, "trecho": v["trecho"], "pagina": v.get("pagina"), "documento": v.get("documento")}
        elif k in DOZE:
            avisos.append(f"{x['id']}: dispensa de {k} recusada (sem justificativa de que não se aplica)")
    ck = {k: {"s": "ok", "v": itens[k]["valor"][:90]} for k in itens} | {k: {"s": "disp", "v": disp[k]["motivo"][:160]} for k in disp}
    faltam = [k for k in DOZE if k not in itens and k not in disp]
    link = x.get("site_oficial") or x.get("link_documento")
    if x.get("link_documento") and re.search(r"pncp\.gov\.br/app/|queridodiario|in\.gov\.br|/visualizacoes/", str(link or "")):
        link = x["link_documento"]                                  # página de portal não é fonte: vale o arquivo do edital
    prazo = (x.get("prazo") or {}).get("fim")
    cert = {"id": x["id"], "tipo": "estrela", "titulo": str(x.get("parecer") or "")[:200], "balcao": "revisão",
            "em": _agora(), "versao": f"revisão manual ({origem})", "link_oficial": link, "degrau": 0,
            "como": "revisão manual: leitura do documento oficial no Chrome da titular", "regua": "documento oficial lido por inteiro",
            "documentos": [{"url": d if isinstance(d, str) else d.get("url"), "oficial": "documento oficial lido na revisão"}
                           for d in (x.get("documentos") or [])][:12],
            "itens": itens, "dispensas": disp, "fim": prazo, "prazo": prazo,
            "faltavam": faltam + [k for k in DOZE if k not in faltam], "resolvidos": [k for k in DOZE if k not in faltam],
            "ainda_faltam": faltam, "eficiencia": round((12 - len(faltam)) / 12, 3),
            "abordagens": [{"n": 1, "nome": f"revisão manual ({origem})", "em": _agora(), "ganhou": sorted(itens) + sorted(disp)}],
            "tentativa": 1, "origem": f"revisão {origem}", "alertas": list(x.get("alertas") or [])[:8],
            "encaminhado": None if (link and not faltam) else
            f"Interceptador: {len(faltam)} item(ns) não estão no documento oficial lido na revisão",
            "selo_depois": nivel(ck), "veredito_revisao": x.get("veredito")}
    return cert, avisos


def importar(pasta: Path, origem: str, gravar: bool = True) -> dict:
    regs = ler_lotes(pasta)
    if not regs:
        raise SystemExit(f"nenhum resultado_ABERTAS_*.json em {pasta}")
    ver = json.loads(VEREDITOS.read_text(encoding="utf-8")) if VEREDITOS.exists() else {"vereditos": {}}
    der = json.loads(DERIVADAS.read_text(encoding="utf-8")) if DERIVADAS.exists() else {"derivadas": {}}
    base = json.loads(CERTIDOES.read_text(encoding="utf-8")) if CERTIDOES.exists() else {"certidoes": {}}
    certs = base.setdefault("certidoes", {})
    avisos, n_cert, n_ver, n_der, selos = [], 0, 0, 0, {}
    for rid, x in regs.items():
        v = x.get("veredito") or "pendente"
        if rid.startswith(("novo-", "der-")) or x.get("novo") is True:             # der-/novo: derivadas da Parte 3
            der["derivadas"][rid] = {"veredito": v, "site_oficial": x.get("site_oficial"), "link_documento": x.get("link_documento"),
                                     "parecer": x.get("parecer"), "itens": x.get("itens"), "pendentes": x.get("pendentes"),
                                     "reclassificar": x.get("reclassificar"), "origem": origem, "em": _agora(),
                                     "prazo": x.get("prazo"), "dispensas": x.get("dispensas"), "derivada_de": x.get("derivada_de")}
            n_der += 1
            if v in VIGENTES or v in ("pendente", "nao_disponivel"):    # 10/10: a derivada também ganha certidão (estrela:<id>)
                cert, av = certidao_de(x, origem)
                avisos += av
                if cert.get("itens") or cert.get("dispensas"):
                    certs[f"estrela:{rid}"] = {**(certs.get(f"estrela:{rid}") or {}), **cert}
                    n_cert += 1
                    selos[cert.get("selo_depois") or "sem_estrela"] = selos.get(cert.get("selo_depois") or "sem_estrela", 0) + 1
            continue
        ver["vereditos"][rid] = {"veredito": v, "duplicata_de": x.get("duplicata_de") or None,
                                 "reclassificar": {k: y for k, y in (x.get("reclassificar") or {}).items() if y},
                                 "fim": (x.get("prazo") or {}).get("fim"), "veredito_edicao": x.get("veredito_edicao") or None,
                                 "motivo": str(x.get("parecer") or "")[:300], "origem": origem, "em": _agora()}
        n_ver += 1
        if v in VIGENTES:
            cert, av = certidao_de(x, origem)
            avisos += av
            chave = f"estrela:{rid}"
            ant = certs.get(chave)
            if ant:                                                  # o que o Cartório já certificou fica; o novo se soma
                cert["itens"] = {**cert["itens"], **(ant.get("itens") or {})}
                cert["dispensas"] = {k: d for k, d in {**cert["dispensas"], **(ant.get("dispensas") or {})}.items() if k not in cert["itens"]}
                cert["abordagens"] = list(ant.get("abordagens") or []) + cert["abordagens"]
                cert["tentativa"] = len(cert["abordagens"])
                cert["link_oficial"] = ant.get("link_oficial") or cert["link_oficial"]
                ck = {k: {"s": "ok", "v": str(i["valor"])[:90]} for k, i in cert["itens"].items()} | \
                     {k: {"s": "disp", "v": str(d.get("motivo"))[:160]} for k, d in cert["dispensas"].items()}
                cert["selo_depois"] = nivel(ck)
                cert["ainda_faltam"] = [k for k in DOZE if k not in ck]
                cert["selo_antes"] = ant.get("selo_antes", ant.get("selo_depois"))
            certs[chave] = cert
            n_cert += 1
            selos[cert["selo_depois"] or "sem_estrela"] = selos.get(cert["selo_depois"] or "sem_estrela", 0) + 1
    ver.update({"regra": "Veredito da revisão humana (leitura do documento oficial). Aplicado pelo saneamento antes de qualquer regra automática.",
                "em": _agora()})
    rel = {"lidos": len(regs), "vereditos": n_ver, "certidoes": n_cert, "derivadas": n_der, "selos_das_certidoes": selos,
           "avisos": avisos[:50], "gravado": gravar}
    if gravar:
        VEREDITOS.parent.mkdir(parents=True, exist_ok=True)
        VEREDITOS.write_text(json.dumps(ver, ensure_ascii=False, indent=1), encoding="utf-8")
        DERIVADAS.write_text(json.dumps(der, ensure_ascii=False, indent=1), encoding="utf-8")
        CERTIDOES.parent.mkdir(parents=True, exist_ok=True)
        base["em"] = _agora()
        CERTIDOES.write_text(json.dumps(base, ensure_ascii=False, indent=1), encoding="utf-8")
    return rel


def main(argv: list[str]) -> None:
    args = [a for a in argv if not a.startswith("--")]
    pasta = Path(args[0]) if args else ROOT / "dados/revisoes/abertas_p1_go_2026_10_10"
    origem = next((a.split("=", 1)[1] for a in argv if a.startswith("--origem=")), pasta.name)
    print(json.dumps(importar(pasta if pasta.is_absolute() else ROOT / pasta, origem, gravar="--verificar" not in argv),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(sys.argv[1:])
