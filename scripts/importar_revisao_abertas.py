#!/usr/bin/env python3
"""IMPORTA a revisão das oportunidades abertas (prompts PARTE 1/2/3, 10/10/2026) para o sistema.

Entrada: uma pasta com `resultado_ABERTAS_<parte>_<lote>.json` (formato dos prompts, mesmo das certidões).
Saídas:
  1. biblioteca_alexandria/livros/_acervo/editais/vereditos_revisao.json — o veredito humano por id (ruido, fora_perfil, encerrada, duplicata,
     ouro/prata/bronze/pendente), que o saneamento (src/saneamento_motores.py) aplica ANTES de qualquer regra automática;
  2. estado/cartorio/certidoes.json — certidão `estrela:<id>` com os itens certificados (valor + trecho + documento +
     página) das vigentes e pendentes. Item que o Cartório já tinha certificado é mantido; os novos se somam.
     Dispensa sem justificativa de "não se aplica" é RECUSADA (regra permanente de 04/10, src/criterio_selos.py);
  3. biblioteca_alexandria/livros/_acervo/editais/derivadas_revisao.json — oportunidades novas achadas na revisão (`novo-…`), como pista com fonte
     oficial, para o motor da área confirmar e gravar.

USO (na raiz do repositório):
    python scripts/importar_revisao_abertas.py biblioteca_alexandria/livros/_acervo/revisoes/abertas_p1_go_2026_10_10 --verificar   # só confere
    python scripts/importar_revisao_abertas.py biblioteca_alexandria/livros/_acervo/revisoes/abertas_p1_go_2026_10_10               # importa
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

VEREDITOS = ROOT / "biblioteca_alexandria/livros/_acervo/editais/vereditos_revisao.json"
DERIVADAS = ROOT / "biblioteca_alexandria/livros/_acervo/editais/derivadas_revisao.json"
# 10/10 (implantação): as certidões da revisão humana vão para um arquivo PRÓPRIO, que o Cartório incorpora a cada
# execução (a revisão humana prevalece). Gravar direto em estado/cartorio/certidoes.json se perdia: o fluxo do
# Cartório regrava esse arquivo de hora em hora.
CERTIDOES = ROOT / "estado/cartorio/certidoes_manuais.json"
VIGENTES = ("ouro", "prata", "bronze", "pendente", "validacao_manual")
# 11/10/2026 (titular): "não consta" pode ser DISPENSA JUSTIFICADA (documentos oficiais lidos e a informação não existe
# neles), mas nunca para o núcleo — objeto, prazo de inscrição e território precisam estar certificados. "Não lido"
# (bloqueio, erro, robots) nunca é dispensa nem conta para o ouro.
NUCLEO = ("Objeto", "Prazo de inscrição", "Território")


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


# 16/10/2026 (titular): só DOCUMENTO OFICIAL certifica. O link de PUBLICAÇÃO (agregador, notícia, buscador, rede social,
# indexador de diários) é só referência — item comprovado por ele é recusado.
PUBLICACAO = re.compile(r"(?i)capitaai|captadores|prosas\.com|observatorio3setor|editaisdobrasil|queridodiario|google\.|bing\.|"
                        r"duckduckgo|facebook\.|instagram\.|linkedin\.|twitter\.|x\.com|youtube\.|g1\.globo|uol\.com|"
                        r"terra\.com|abcr\.org")
# notícia/blog SÓ é publicação fora do domínio oficial (17/10: a notícia no próprio site da prefeitura é fonte oficial)
NOTICIA_FORA = re.compile(r"(?i)/noticias?/|/blog/")
OFICIAL_PUBLICO = re.compile(r"(?i)\.(gov|leg|jus|mp|def|tc)\.br\b|pncp\.gov\.br")


def _dom(u) -> str:
    m = re.match(r"https?://([^/]+)", str(u or "")); return (m.group(1).lower().removeprefix("www.") if m else "")


_MOTOR: dict = {}


def _motor_de(rid: str) -> str | None:
    """O motor de origem da oportunidade (repositório: origem e ids de origem)."""
    if not _MOTOR:
        try:
            regs = json.loads((ROOT / "biblioteca_alexandria/livros/_vistas/repositorio_unico.json").read_text(encoding="utf-8")).get("registros") or []
        except Exception:  # noqa: BLE001
            regs = []
        for r in regs:
            m = re.sub(r"^motor\s+", "", str(r.get("origem") or "")).strip() or None
            for i in [r.get("id"), *(r.get("ids_origem") or [])]:
                if i:
                    _MOTOR[str(i)] = m
        _MOTOR.setdefault("__carregado__", "1")
    return _MOTOR.get(str(rid))


def documento_oficial(doc, link_oficial=None) -> bool:
    if not str(doc or "").startswith("http") or PUBLICACAO.search(str(doc)):
        return False
    d, o = _dom(doc), _dom(link_oficial)
    mesmo_dominio = bool(o and (d == o or d.endswith("." + o) or o.endswith("." + d)))
    if NOTICIA_FORA.search(str(doc)) and not mesmo_dominio and not OFICIAL_PUBLICO.search(str(doc)):
        return False
    return bool(OFICIAL_PUBLICO.search(str(doc)) or mesmo_dominio)


def _item_ok(v, link_oficial=None) -> bool:
    if isinstance(v, dict) and not documento_oficial(v.get("documento"), link_oficial or v.get("link_oficial")):
        return False
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
        if _item_ok(v, x.get("site_oficial") or x.get("link_documento")):
            itens[k] = {"valor": str(v["valor"]), "trecho": str(v["trecho"]), "pagina": v.get("pagina"),
                        "documento": v["documento"], "metodo": v.get("metodo") or "revisão manual (leitura do documento oficial)"}
        else:
            avisos.append(f"{x['id']}: item {k} sem valor/trecho/documento/página — ignorado")
    for k, v in (x.get("dispensas") or {}).items():
        motivo = str((v or {}).get("motivo") or (v or {}).get("valor") or "")
        lidos = [d for d in ((v or {}).get("documentos_lidos") or []) if str(d).startswith("http")]
        if k in DOZE and k not in itens and dispensa_valida(motivo) and (v or {}).get("trecho"):
            disp[k] = {"motivo": motivo, "trecho": v["trecho"], "pagina": v.get("pagina"), "documento": v.get("documento")}
        elif k in DOZE and k not in itens and k not in NUCLEO and (v or {}).get("tipo") == "nao_consta" and lidos:
            disp[k] = {"motivo": f"não consta nos documentos oficiais lidos ({len(lidos)})" + (f": {motivo}" if motivo else ""),
                       "tipo": "nao_consta", "documentos_lidos": lidos[:10]}
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


def importar(pasta: Path, origem: str, gravar: bool = True, externa: bool = False) -> dict:
    regs = ler_lotes(pasta)
    av_externa = cobrar_resolucao(regs) if externa else []     # busca externa: arquivar, eliminar ou completar
    if externa and gravar:
        av_externa += gravar_aprendizado(regs, origem)
    if not regs:
        raise SystemExit(f"nenhum resultado_ABERTAS_*.json em {pasta}")
    ver = json.loads(VEREDITOS.read_text(encoding="utf-8")) if VEREDITOS.exists() else {"vereditos": {}}
    der = json.loads(DERIVADAS.read_text(encoding="utf-8")) if DERIVADAS.exists() else {"derivadas": {}}
    sys.path.insert(0, str(ROOT)); from src import livro_arquivo as _LA
    base = _LA.ler_arquivo(CERTIDOES, None) or {"certidoes": {}}
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
                                 "motivo": str(x.get("parecer") or "")[:300], "origem": origem, "em": _agora(),
                                 "motor": _motor_de(rid)}   # 17/10: RASTRO — o motor que trouxe a oportunidade
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
           "resolucao_incompleta_da_busca_externa": av_externa,
           "avisos": avisos[:50], "gravado": gravar}
    if gravar:
        VEREDITOS.parent.mkdir(parents=True, exist_ok=True)
        VEREDITOS.write_text(json.dumps(ver, ensure_ascii=False, indent=1), encoding="utf-8")
        DERIVADAS.write_text(json.dumps(der, ensure_ascii=False, indent=1), encoding="utf-8")
        CERTIDOES.parent.mkdir(parents=True, exist_ok=True)
        base["em"] = _agora()
        _LA.guardar_lote([(CERTIDOES, base)])                    # 16/10: no livro
    return rel


RESOLUCOES_EXTERNAS = ("ouro", "encerrada", "ruido", "fora_perfil", "duplicata", "validacao_manual")


def cobrar_resolucao(regs: dict) -> list[str]:
    """11/10 (titular): toda busca EXTERNA termina em arquivar (encerrada, com o prazo comprovado), eliminar (ruído/fora do
    perfil, com motivo) ou completar (ouro 12/12). Parcial volta à fila como 'validacao_manual: resolução incompleta'."""
    avisos = []
    for rid, x in regs.items():
        v = x.get("veredito")
        incompleta = None
        if v not in RESOLUCOES_EXTERNAS:
            incompleta = f"veredito '{v}' não é resolução"
        elif v == "encerrada" and not ((x.get("prazo") or {}).get("fim") and (x.get("prazo") or {}).get("trecho")):
            incompleta = "arquivar exige o prazo de inscrição comprovado (fim + trecho do documento oficial)"
        elif v in ("ruido", "fora_perfil") and not str(x.get("parecer") or x.get("motivo") or "").strip():
            incompleta = "eliminar exige o motivo"
        if incompleta:
            x["veredito"] = "validacao_manual"; x["parecer"] = f"resolução incompleta da busca externa — {incompleta}. " + str(x.get("parecer") or "")
            avisos.append(f"{rid}: {incompleta}")
    return avisos


def gravar_aprendizado(regs: dict, origem: str) -> list[str]:
    """11/10 (titular): cada verificação externa deixa um RELATÓRIO DE APRENDIZADO — vai para o livro da oportunidade
    (onde o edital estava, que rota funcionou, por que os robôs não acharam) e para as melhorias dos motores."""
    apr_p = ROOT / "estado/biblioteca/aprendizados_externos.json"; mel_p = ROOT / "docs/dados/melhorias_motores_externas.json"
    apr = (json.loads(apr_p.read_text(encoding="utf-8")) if apr_p.exists() else {}).get("aprendizados") or {}
    mel = json.loads(mel_p.read_text(encoding="utf-8")) if mel_p.exists() else {"melhorias": []}
    av = []
    for rid, x in regs.items():
        a = x.get("aprendizado") or {}
        if not a:
            av.append(f"{rid}: sem relatório de aprendizado"); continue
        apr[rid] = {"em": _agora(), "origem": origem, "veredito": x.get("veredito"), **{k: a.get(k) for k in
                    ("onde_estava", "rota_que_funcionou", "por_que_os_robos_nao_acharam", "sugestao_para_o_motor", "padrao_do_endereco")}}
        if a.get("sugestao_para_o_motor"):
            mel["melhorias"].append({"oportunidade": rid, "em": _agora(), "origem": origem, "motor": x.get("fonte") or x.get("origem"),
                                     "sugestao": a["sugestao_para_o_motor"], "por_que": a.get("por_que_os_robos_nao_acharam"), "onde_estava": a.get("onde_estava")})
    apr_p.parent.mkdir(parents=True, exist_ok=True)
    apr_p.write_text(json.dumps({"regra": "relatório de aprendizado de cada verificação externa (vai para o livro)", "aprendizados": apr}, ensure_ascii=False, indent=1), encoding="utf-8")
    mel["melhorias"] = mel["melhorias"][-500:]; mel_p.parent.mkdir(parents=True, exist_ok=True)
    mel_p.write_text(json.dumps(mel, ensure_ascii=False, indent=1), encoding="utf-8")
    return av


def main(argv: list[str]) -> None:
    args = [a for a in argv if not a.startswith("--")]
    pasta = Path(args[0]) if args else ROOT / "biblioteca_alexandria/livros/_acervo/revisoes/abertas_p1_go_2026_10_10"
    origem = next((a.split("=", 1)[1] for a in argv if a.startswith("--origem=")), pasta.name)
    print(json.dumps(importar(pasta if pasta.is_absolute() else ROOT / pasta, origem, gravar="--verificar" not in argv,
                              externa="--externa" in argv),
                     ensure_ascii=False, indent=2))


def atualizar_ja() -> dict:
    """16/10 (titular): o resultado do Chrome aparece NA HORA — repositório, fluxo e pendências do Cartório refeitos."""
    out = {}
    for nome, f in (("repositorio", lambda: __import__("src.repositorio_unico", fromlist=["x"]).construir(gravar=True)),
                    ("fluxo", lambda: __import__("src.fluxo_oportunidades", fromlist=["x"]).sincronizar_com_repositorio()),   # 17/10: rápido
                    ("pendencias", lambda: __import__("src.cartorio", fromlist=["x"]).pendencias()),
                    ("sala", lambda: __import__("src.sala_controle", fromlist=["x"]).run())):   # 17/10: a página inicial lê a sala
        try:
            r = f(); out[nome] = "ok" if not isinstance(r, dict) else {k: v for k, v in r.items() if not isinstance(v, (list, dict))}
        except Exception as e:  # noqa: BLE001
            out[nome] = f"falhou: {e}"
    return out



if __name__ == "__main__":
    main(sys.argv[1:])
    if "--verificar" not in sys.argv and "--sem-atualizar" not in sys.argv:   # no fechamento, a passagem refaz em seguida
        print(json.dumps({"atualizado_na_hora": atualizar_ja()}, ensure_ascii=False))
