"""DOCUMENTOS — Farol de Alexandria › Documentos.

Uma pasta por associação, com três camadas:
  • DOSSIÊ — dados resumidos da entidade (razão social, CNPJ, fundação, sede,
    governança e mandato, afinidades/áreas, atuação geográfica, contato,
    capacidades) — a base para preencher automaticamente os documentos de cada
    edital (fase 4);
  • CERTIDÕES — checklist por entidade, atualizado no 1º dia de cada mês: as que
    saem automaticamente (CRF/FGTS) o sistema tenta emitir; as demais têm o
    link de emissão pronto com o CNPJ e o botão "enviar certidão" no painel; toda
    certidão com mais de 90 dias é EXCLUÍDA (arquivo e registro);
  • REGISTRADOS — estatuto e atas: sem validade, enviados manualmente por
    documento; um novo substitui o anterior (só o mais recente fica).

Regras de honestidade e privacidade: a emissão automática só é afirmada quando o
PDF foi realmente obtido; datas de emissão são lidas do próprio PDF; o
repositório é público — certidões trazem só CNPJ e razão social, mas estatutos e
atas costumam trazer CPF de dirigentes, por isso a pasta dos registrados exige a
versão SEM dados pessoais ou repositório privado (aviso no painel).

Arquivos:
  dados/associacoes/<id>/documentos/certidoes.json        registro das certidões
  dados/associacoes/<id>/documentos/certidoes/*.pdf        PDFs (≤ 90 dias)
  dados/associacoes/<id>/documentos/registrados/*.pdf      estatuto/ata (o mais recente por tipo)
  dados/associacoes/<id>/documentos/dossie.json + parecer.md
"""
from __future__ import annotations

import glob
import hashlib
import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json

CERTIDOES = [
    {"tipo": "certidao_federal", "rotulo": "Certidão Negativa de Débitos Federais (RFB/PGFN)", "validade_dias": 180, "automatica": False,
     "emissao": "https://solucoes.receita.fazenda.gov.br/Servicos/certidaointernet/PJ/Emitir?Ni={cnpj_digits}", "orgao": "Receita Federal / PGFN"},
    {"tipo": "cndt", "rotulo": "CNDT — Certidão Negativa de Débitos Trabalhistas", "validade_dias": 180, "automatica": False,
     "emissao": "https://cndt-certidao.tst.jus.br/inicio.faces", "orgao": "TST"},
    {"tipo": "crf_fgts", "rotulo": "CRF — Certificado de Regularidade do FGTS", "validade_dias": 30, "automatica": True,
     "emissao": "https://consulta-crf.caixa.gov.br/consultacrf/pages/consultaEmpregador.jsf", "orgao": "Caixa"},
    {"tipo": "certidao_estadual", "rotulo": "Certidão Negativa Estadual (Economia-GO)", "validade_dias": 90, "automatica": False,
     "emissao": "https://www.sefaz.go.gov.br/Certidao/Emissao/default.asp", "orgao": "Economia-GO"},
    {"tipo": "certidao_municipal", "rotulo": "Certidão Negativa Municipal (Goiânia)", "validade_dias": 90, "automatica": False,
     "emissao": "https://www.goiania.go.gov.br/sing/certidao-negativa/", "orgao": "Prefeitura de Goiânia"},
]
REGISTRADOS = [
    {"tipo": "estatuto", "rotulo": "Estatuto social registrado (versão consolidada)"},
    {"tipo": "ata_eleicao", "rotulo": "Ata de eleição e posse da diretoria vigente"},
    {"tipo": "ata_assembleia", "rotulo": "Ata da última assembleia geral"},
    {"tipo": "cartao_cnpj", "rotulo": "Comprovante de inscrição CNPJ"},
    {"tipo": "comprovante_endereco", "rotulo": "Comprovante de endereço da sede"},
    {"tipo": "utilidade_publica", "rotulo": "Título/lei de utilidade pública (quando houver)"},
]
LIMITE_DIAS = 90
REPO = "amcjardimamerica-arch/Eldorado"


def _pasta(a: dict) -> Path:
    return ROOT / "dados/associacoes" / a["_pasta"] / "documentos"


def associacoes() -> list[dict]:
    saida = []
    for fp in sorted(glob.glob(str(ROOT / "dados/associacoes/*/perfil*.json"))):
        if "EXEMPLO" in fp:
            continue
        a = load_json(Path(fp)); a["_pasta"] = Path(fp).parent.name; saida.append(a)
    return saida


def _data_do_pdf(caminho: Path) -> str | None:
    """Lê a data de emissão do próprio PDF (nunca a data do upload)."""
    try:
        from pypdf import PdfReader
        txt = " ".join((p.extract_text() or "") for p in PdfReader(str(caminho)).pages[:3])
    except Exception:
        return None
    m = re.search(r"(emitid[ao]|emiss[ãa]o|expedi[çc][ãa]o|data)[^0-9]{0,40}(\d{2})/(\d{2})/(\d{4})", txt, re.I)
    if m:
        return f"{m.group(4)}-{m.group(3)}-{m.group(2)}"
    m = re.search(r"(\d{2})/(\d{2})/(20\d{2})", txt)
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None


def _tipo_do_arquivo(nome: str) -> str | None:
    n = nome.lower()
    for c in CERTIDOES:
        if c["tipo"].replace("_", "") in n.replace("_", "").replace("-", "") or any(k in n for k in {"certidao_federal": ("federal", "rfb", "pgfn", "conjunta"), "cndt": ("cndt", "trabalhista"),
                "crf_fgts": ("crf", "fgts"), "certidao_estadual": ("estadual", "sefaz", "economia"), "certidao_municipal": ("municipal", "prefeitura", "iss")}[c["tipo"]]):
            return c["tipo"]
    return None


def tentar_crf_fgts(cnpj: str) -> dict:
    """Tenta obter o CRF automaticamente. A consulta pública da Caixa passou a
    exigir interação (captcha/sessão); o sistema só registra 'emitida' quando o
    PDF realmente veio — senão devolve o motivo e o link para emissão manual."""
    import urllib.request
    url = "https://consulta-crf.caixa.gov.br/consultacrf/pages/consultaEmpregador.jsf"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 Eldorado-OSC/1.0", "From": "contato-via-repositorio"})
        with urllib.request.urlopen(req, timeout=20) as r:
            html = r.read(400_000).decode("utf-8", "replace")
        if "captcha" in html.lower() or "recaptcha" in html.lower():
            return {"obtida": False, "motivo": "a consulta da Caixa exige captcha — emissão manual (30 s) pelo link", "http": r.status}
        return {"obtida": False, "motivo": "página respondeu, mas a emissão exige sessão interativa — emissão manual pelo link", "http": r.status}
    except Exception as exc:
        return {"obtida": False, "motivo": f"sem resposta da Caixa ({type(exc).__name__}) — emissão manual pelo link"}


def atualizar_certidoes(a: dict, hoje: date) -> dict:
    """1º do mês (ou sob demanda): lê os PDFs enviados, registra datas, tenta as
    automáticas, EXCLUI o que passou de 90 dias."""
    pasta = _pasta(a); pc = pasta / "certidoes"; pc.mkdir(parents=True, exist_ok=True)
    reg_p = pasta / "certidoes.json"
    reg = load_json(reg_p) if reg_p.exists() else {"associacao": a.get("id"), "certidoes": {}, "atualizacoes": []}
    cnpj = a.get("cnpj") or ""; dig = re.sub(r"\D", "", cnpj)
    excluidas, lidas = [], 0
    for pdf in sorted(pc.glob("*.pdf")):
        tipo = _tipo_do_arquivo(pdf.name)
        emitida = _data_do_pdf(pdf) or datetime.fromtimestamp(pdf.stat().st_mtime).date().isoformat()
        idade = (hoje - date.fromisoformat(emitida)).days
        if idade > LIMITE_DIAS:
            pdf.unlink(missing_ok=True); excluidas.append({"arquivo": pdf.name, "emitida_em": emitida, "idade_dias": idade}); continue
        if tipo:
            lidas += 1
            atual = reg["certidoes"].get(tipo)
            if not atual or (atual.get("emitida_em") or "") < emitida:
                if atual and atual.get("arquivo") and atual["arquivo"] != pdf.name and (pc / atual["arquivo"]).exists():
                    (pc / atual["arquivo"]).unlink(missing_ok=True)         # a mais nova substitui a anterior
                reg["certidoes"][tipo] = {"arquivo": pdf.name, "emitida_em": emitida, "origem": "manual (enviada pelo titular)",
                                          "sha256": hashlib.sha256(pdf.read_bytes()).hexdigest()[:16], "registrada_em": now_iso()}
    for tipo, c in list(reg["certidoes"].items()):
        if c.get("emitida_em") and (hoje - date.fromisoformat(c["emitida_em"][:10])).days > LIMITE_DIAS:
            excluidas.append({"arquivo": c.get("arquivo"), "emitida_em": c["emitida_em"], "idade_dias": (hoje - date.fromisoformat(c["emitida_em"][:10])).days})
            if c.get("arquivo"): (pc / c["arquivo"]).unlink(missing_ok=True)
            del reg["certidoes"][tipo]
    tent = {}
    for c in CERTIDOES:
        if c["automatica"] and dig:
            tent[c["tipo"]] = tentar_crf_fgts(cnpj)
    reg["atualizacoes"] = (reg.get("atualizacoes") or [])[-24:] + [{"em": now_iso(), "lidas": lidas, "excluidas": excluidas, "automaticas": tent}]
    write_json(reg_p, reg)
    return {"lidas": lidas, "excluidas": len(excluidas), "automaticas": tent}


def atualizar_registrados(a: dict) -> dict:
    """Estatuto/atas: sem validade; só o mais recente por tipo permanece."""
    pasta = _pasta(a); pr = pasta / "registrados"; pr.mkdir(parents=True, exist_ok=True)
    reg = {}
    for pdf in sorted(pr.glob("*.*"), key=lambda p: p.stat().st_mtime):
        n = pdf.name.lower()
        tipo = next((r["tipo"] for r in REGISTRADOS if r["tipo"].replace("_", "") in n.replace("_", "").replace("-", "")
                     or any(k in n for k in {"estatuto": ("estatuto",), "ata_eleicao": ("eleicao", "eleição", "posse"), "ata_assembleia": ("assembleia",),
                                             "cartao_cnpj": ("cnpj",), "comprovante_endereco": ("endereco", "endereço"), "utilidade_publica": ("utilidade", "lei")}.get(r["tipo"], ()))), None)
        if not tipo:
            continue
        ant = reg.get(tipo)
        if ant and (pr / ant["arquivo"]).exists() and ant["arquivo"] != pdf.name:
            (pr / ant["arquivo"]).unlink(missing_ok=True)                    # o novo substitui e o anterior sai
        reg[tipo] = {"arquivo": pdf.name, "enviado_em": datetime.fromtimestamp(pdf.stat().st_mtime).date().isoformat(),
                     "sha256": hashlib.sha256(pdf.read_bytes()).hexdigest()[:16]}
    write_json(pasta / "registrados.json", {"associacao": a.get("id"), "registrados": reg, "atualizado_em": now_iso()})
    return {"tipos": list(reg)}


def dossie(a: dict, hoje: date) -> dict:
    """Dados resumidos e completos para preencher documentos de qualquer edital."""
    pasta = _pasta(a)
    cert = load_json(pasta / "certidoes.json").get("certidoes", {}) if (pasta / "certidoes.json").exists() else {}
    regs = load_json(pasta / "registrados.json").get("registrados", {}) if (pasta / "registrados.json").exists() else {}
    cap = load_json(Path(glob.glob(str(ROOT / "dados/associacoes" / a["_pasta"] / "conhecimento/capacidades.json"))[0])) if glob.glob(str(ROOT / "dados/associacoes" / a["_pasta"] / "conhecimento/capacidades.json")) else {}
    dig = re.sub(r"\D", "", a.get("cnpj") or "")
    checklist = []
    for c in CERTIDOES:
        r = cert.get(c["tipo"]); status = "faltante"; vence = None; dias = None
        if r:
            venc = date.fromisoformat(r["emitida_em"][:10]) + timedelta(days=min(c["validade_dias"], LIMITE_DIAS))
            dias = (venc - hoje).days; vence = venc.isoformat(); status = "válida" if dias > 0 else "vencida"
        checklist.append({**{k: c[k] for k in ("tipo", "rotulo", "validade_dias", "automatica", "orgao")}, "status": status, "emitida_em": (r or {}).get("emitida_em"),
                          "vence_em": vence, "dias": dias, "arquivo": (r or {}).get("arquivo"), "emissao": c["emissao"].format(cnpj_digits=dig),
                          "alerta": bool(dias is not None and dias <= 15)})
    registrados = [{**r, "status": "enviado" if r["tipo"] in regs else "faltante", **(regs.get(r["tipo"]) or {})} for r in REGISTRADOS]
    dir_ = a.get("diretoria") or {}
    d = {
        "id": a.get("id"), "razao_social": a.get("nome"), "cnpj": a.get("cnpj"), "natureza_juridica": a.get("natureza_juridica"),
        "fundada_em": a.get("fundada_em"), "abertura_cnpj_em": a.get("abertura_cnpj_em"), "anos_existencia": a.get("anos_existencia"),
        "sede": a.get("endereco") or {"logradouro": None, "bairro": "Jardim América" if "jardim-america" in a["_pasta"] else None, "municipio": "Goiânia" if "GO/Goiânia" in (a.get("territorios") or []) else None, "uf": "GO" if "GO" in (a.get("territorios") or []) else None, "status": "a confirmar no comprovante de endereço"},
        "contato": a.get("contato_institucional") or {},
        "governanca": {"cargos": (cap.get("governanca") or []), "diretoria": dir_.get("membros") or [], "mandato": dir_.get("mandato") or {"inicio": None, "fim": None, "status": "pendente — informar na ata de eleição"}},
        "afinidades": a.get("areas") or [], "atuacao_geografica": a.get("territorios") or [], "cnaes": a.get("cnaes") or [],
        "certificacoes": a.get("certificacoes") or [], "certificacoes_a_confirmar": a.get("certificacoes_alegadas_pendentes_verificacao") or [],
        "experiencias": a.get("experiencias") or [], "capacidades": {k: cap.get(k) for k in ("infraestrutura_alegada", "metodos", "forcas", "riscos") if k in cap},
        "certidoes": checklist, "registrados": registrados,
        "prontidao": {"certidoes_validas": sum(1 for c in checklist if c["status"] == "válida"), "certidoes_total": len(checklist),
                      "registrados_enviados": sum(1 for r in registrados if r["status"] == "enviado"), "registrados_total": len(registrados)},
        "upload": {"certidoes": f"https://github.com/{REPO}/upload/main/dados/associacoes/{a['_pasta']}/documentos/certidoes",
                   "registrados": f"https://github.com/{REPO}/upload/main/dados/associacoes/{a['_pasta']}/documentos/registrados",
                   "aviso": "o repositório é público: certidões trazem só CNPJ e razão social; em estatuto/ata, envie a versão SEM CPF/RG dos dirigentes ou torne o repositório privado"},
        "gerado_em": now_iso(),
    }
    return d


def parecer_md(d: dict) -> str:
    L = []
    L.append(f"# Parecer institucional — {d['razao_social']}\n")
    L.append(f"**CNPJ** {d['cnpj']} · **natureza** {d.get('natureza_juridica','').replace('_',' ')} · fundada em {d.get('fundada_em') or '—'} · CNPJ desde {d.get('abertura_cnpj_em') or '—'} · **{d.get('anos_existencia')} anos**\n")
    s = d["sede"]; L.append(f"**Sede:** {s.get('logradouro') or '—'}, {s.get('bairro') or '—'}, {s.get('municipio') or '—'}/{s.get('uf') or '—'} ({s.get('status','')})\n")
    g = d["governanca"]; L.append(f"**Governança:** {', '.join(g['cargos']) or '—'} · **mandato:** {g['mandato'].get('inicio') or '—'} → {g['mandato'].get('fim') or '—'} ({g['mandato'].get('status','')})\n")
    if g["diretoria"]: L.append("**Diretoria:** " + "; ".join(f"{m.get('cargo')}: {m.get('nome')}" for m in g["diretoria"]) + "\n")
    L.append("## Afinidades e enquadramento\n")
    L.append("**Áreas de atuação (afinidades para editais):** " + ", ".join(d["afinidades"]) + "\n")
    L.append("**Atuação geográfica:** " + ", ".join(d["atuacao_geografica"]) + "\n")
    L.append("**CNAEs:** " + ", ".join(d["cnaes"]) + " · **certificações:** " + (", ".join(d["certificacoes"]) or "nenhuma comprovada") + (f" · a confirmar: {', '.join(d['certificacoes_a_confirmar'])}" if d["certificacoes_a_confirmar"] else "") + "\n")
    L.append("**Experiências:** " + ", ".join(d["experiencias"]) + "\n")
    L.append("## Checklist de documentos — pronto para qualquer projeto\n")
    for c in d["certidoes"]:
        L.append(f"- [{'x' if c['status']=='válida' else ' '}] {c['rotulo']} — {c['status']}" + (f", emitida em {c['emitida_em']}, vence em {c['vence_em']}" if c.get("emitida_em") else f" — emitir: {c['emissao']}"))
    for r in d["registrados"]:
        L.append(f"- [{'x' if r['status']=='enviado' else ' '}] {r['rotulo']} — {r['status']}" + (f" ({r.get('arquivo')})" if r.get("arquivo") else ""))
    p = d["prontidao"]; L.append(f"\n**Prontidão documental:** {p['certidoes_validas']}/{p['certidoes_total']} certidões válidas · {p['registrados_enviados']}/{p['registrados_total']} registrados enviados.\n")
    L.append(f"_Gerado em {d['gerado_em'][:16]} — dados autodeclarados não recebem pontuação documental até a evidência ser anexada._\n")
    return "\n".join(L)


def run(hoje: date | None = None) -> dict:
    hoje = hoje or date.today()
    saida = []
    for a in associacoes():
        c = atualizar_certidoes(a, hoje); r = atualizar_registrados(a)
        d = dossie(a, hoje); pasta = _pasta(a)
        write_json(pasta / "dossie.json", d); (pasta / "parecer.md").write_text(parecer_md(d), encoding="utf-8")
        saida.append({"associacao": a.get("id"), **c, "registrados": r["tipos"], "prontidao": d["prontidao"]})
    return {"em": now_iso(), "associacoes": saida}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
