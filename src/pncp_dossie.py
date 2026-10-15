"""DOSSIÊ DO PNCP — 12 de 12 com informação confirmada, ou descarte justificado (titular, 15/10/2026).

O PNCP é o portal das CONTRATAÇÕES da Lei 14.133/2021; parceria com associação (Lei 13.019) só aparece nele "de carona"
(credenciamento, concurso, inexigibilidade). É de onde vem a maior parte dos registros e do ruído. Este módulo trata
cada compra do PNCP como um dossiê e usa TODAS as ferramentas, em ordem, até fechar os 12 itens:

  PORTÕES (antes de gastar trabalho)
    1. situação da compra no PNCP     revogada, anulada, suspensa, deserta, fracassada → fecha, com o motivo
    2. prazo                          período de propostas encerrado → fecha
    3. território                     esfera municipal fora de Goiás e fora das capitais → descarta
    4. pertinência para associação    amparo legal (Lei 13.019 / 14.903 = sim) + classificador do terceiro setor
                                      (finalidade e público); contratação comum, prestador, empresa, pessoa física → descarta

  FONTES (cada item vem de informação CONFIRMADA, com trecho e documento; a primeira que confirmar fica)
    1. metadados oficiais da compra    esfera, órgão, objeto, período de propostas, valor, município/UF
    2. arquivos publicados pelo órgão  edital primeiro, depois termo de referência e anexos (Cartório lê cada um)
    3. lista de arquivos               o item Anexos é a própria lista publicada
    4. site oficial                    o sistema de origem da compra (linkSistemaOrigem)
    5. Interceptador                   o que ainda faltar vai à frente da fila do Interceptador (nível 0)

  DISPENSA — só JUSTIFICADA: o próprio documento declara que o item não existe (confirmada), ou, depois de consultadas
  TODAS as fontes, o regime do recurso (config/dispensas_por_regime.json) diz que o item não existe nele; a dispensa
  registra o regime e as fontes consultadas. Hipótese sem as fontes esgotadas não conta.

  RESULTADO por dossiê: completo (12/12) · em trabalho (fonte seguinte) · fechado/descartado (motivo). Sem trabalho
  parcial no Farol: só o completo segue. Saídas: estado/pncp/dossies.json · estado/pncp/para_interceptador.json ·
  certidões do Cartório (estado/cartorio/certidoes.json, chave estrela:<id>).
"""
from __future__ import annotations

import json
import re
import time
from datetime import date, datetime, timezone
from pathlib import Path

from . import cartorio_leitura as L
from .nucleo import ROOT

DIR = ROOT / "estado/pncp"
DOSSIES = DIR / "dossies.json"
PARA_INTERCEPTADOR = DIR / "para_interceptador.json"
CERT = ROOT / "estado/cartorio/certidoes.json"
REPO = ROOT / "dados/oportunidades/repositorio_unico.json"
DOZE = L.DOZE
FECHADA = re.compile(r"(?i)revogad|anulad|suspens|desert|fracassad|cancelad")
AMPARO_OSC = re.compile(r"13\.?019|14\.?903|mrosc|sociedade civil", re.I)
CAPITAIS = {"Rio Branco", "Maceió", "Macapá", "Manaus", "Salvador", "Fortaleza", "Brasília", "Vitória", "Goiânia", "São Luís",
            "Cuiabá", "Campo Grande", "Belo Horizonte", "Belém", "João Pessoa", "Curitiba", "Recife", "Teresina", "Rio de Janeiro",
            "Natal", "Porto Alegre", "Porto Velho", "Boa Vista", "Florianópolis", "São Paulo", "Aracaju", "Palmas"}


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao


def _agora() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sem(s) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", str(s or "").lower()) if unicodedata.category(c) != "Mn")


def _get_json(rede, url: str):
    raw, _t, err = rede.get(url)
    if err or not raw:
        return None, err or "vazio"
    try:
        return json.loads(raw.decode("utf-8", "replace")), None
    except ValueError:
        return None, "resposta sem JSON"


# ── PORTÕES ────────────────────────────────────────────────────────────────────────────────────────────────────────
def portoes(meta: dict, titulo: str, hoje: str) -> tuple[str | None, str | None, dict]:
    """(estado de fechamento ou None, motivo, pertinência)."""
    from .pncp_terceiro_setor import classificar
    sit = str(meta.get("situacaoCompraNome") or "")
    if FECHADA.search(sit):
        return "fechada", f"compra {sit.lower()} no PNCP", {}
    fim = str(meta.get("dataEncerramentoProposta") or "")[:10]
    if fim and fim < hoje:
        return "fechada", f"período de propostas encerrado em {fim} (PNCP)", {}
    oe, uo = meta.get("orgaoEntidade") or {}, meta.get("unidadeOrgao") or {}
    if str(oe.get("esferaId") or "").upper() == "M" and str(uo.get("ufSigla") or "").upper() != "GO" and \
            _sem(uo.get("municipioNome")) not in {_sem(c) for c in CAPITAIS}:
        return "descartada", f"municipal de outro estado ({uo.get('municipioNome')}/{uo.get('ufSigla')}) — só Goiás e capitais", {}
    # 15/10 (titular): o MESMO portão do motor — compra, contrato de serviço, PNAE, pessoa física, município de outro estado
    from .pncp_osc import portao_associacao, _N
    _m = {"modalidade": meta.get("modalidadeNome"), "orgao": oe.get("razaoSocial"), "uf": uo.get("ufSigla"), "esfera": oe.get("esferaId"),
          "municipio": uo.get("municipioNome")}
    _porta = portao_associacao(_m, _N(" ".join(str(x or "") for x in (titulo, meta.get("objetoCompra"), meta.get("informacaoComplementar")))))
    if _porta:
        return "descartada", f"não é captação de recursos para associação: {_porta}", {}
    amparo = " ".join(str((meta.get("amparoLegal") or {}).get(k) or "") for k in ("nome", "descricao"))
    texto = " ".join(str(x or "") for x in (meta.get("objetoCompra"), meta.get("informacaoComplementar")))
    cls = classificar(texto, titulo)
    pert = {"amparo_legal": amparo.strip() or None, "modalidade": meta.get("modalidadeNome"), "finalidade": cls.get("finalidade"),
            "pertinencia": cls.get("pertinencia"), "porque": cls.get("porque")}
    if AMPARO_OSC.search(amparo):
        pert["porque"] = f"amparo legal de parceria com OSC ({amparo.strip()[:80]})"
        return None, None, pert
    if not cls.get("terceiro_setor"):
        return "descartada", f"não se aplica a associação: {cls.get('finalidade')} — {cls.get('porque')}"[:300], pert
    return None, None, pert


# ── FONTES ─────────────────────────────────────────────────────────────────────────────────────────────────────────
def _juntar(ex: dict, novo: dict, fonte: str, fontes: list) -> list[str]:
    ganhos = []
    for k, v in (novo.get("pontos") or {}).items():
        if k not in ex["pontos"]:
            ex["pontos"][k] = {**v, "fonte": fonte}; ganhos.append(k)
    for k, d in (novo.get("dispensas") or {}).items():                    # dispensa CONFIRMADA: o documento declara
        if k not in ex["pontos"] and k not in ex["dispensas"]:
            ex["dispensas"][k] = {**d, "tipo": "confirmada pelo documento", "fonte": fonte}
    fontes.append({"fonte": fonte, "itens_novos": ganhos})
    return ganhos


def ordem_dos_arquivos(lista: list[dict]) -> list[dict]:
    def peso(a):
        t = _sem(f"{a.get('tipoDocumentoNome')} {a.get('titulo')}")
        return 0 if "edital" in t else 1 if "termo de referencia" in t else 2 if "anexo" in t else 3
    return sorted([a for a in lista if isinstance(a, dict) and a.get("statusAtivo") is not False], key=peso)


def dossie(r: dict, rede, hoje: str, max_arquivos: int = 6) -> dict:
    url = r.get("link_oficial") if L.url_meta_pncp(r.get("link_oficial")) else r.get("url")
    api = L.url_meta_pncp(url) or L.url_meta_pncp(r.get("url"))
    out = {"id": r["id"], "titulo": r.get("titulo"), "api": api, "em": _agora(), "fontes": []}
    meta, err = _get_json(rede, api) if api else (None, "sem compra do PNCP identificável")
    if not meta:
        out.update({"status": "em trabalho", "proximo": f"metadados do PNCP indisponíveis ({err}) — nova tentativa em 30 min"}); return out
    estado, motivo, pert = portoes(meta, str(r.get("titulo") or ""), hoje)
    out["pertinencia"] = pert
    if estado:
        out.update({"status": estado, "motivo": motivo}); return out
    ex = {"pontos": {}, "dispensas": {}}
    _juntar(ex, {"pontos": L.pontos_pncp(meta, api)}, "metadados oficiais do PNCP", out["fontes"])
    m = L.PNCP_COMPRA.search(api)
    base = f"https://pncp.gov.br/pncp-api/v1/orgaos/{m.group(1)}/compras/{m.group(2)}/{m.group(3)}"
    arquivos, _e = _get_json(rede, f"{base}/arquivos")
    arquivos = ordem_dos_arquivos(arquivos if isinstance(arquivos, list) else [])
    if arquivos:
        nomes = "; ".join(f"{a.get('tipoDocumentoNome') or 'Arquivo'}: {a.get('titulo') or ''}".strip(": ") for a in arquivos)[:600]
        _juntar(ex, {"pontos": {"Anexos": {"valor": nomes, "trecho": f"arquivos publicados no PNCP: {nomes}", "pagina": None,
                                           "documento": f"{base}/arquivos", "metodo": "lista de arquivos do PNCP"}}}, "lista de arquivos do PNCP", out["fontes"])
    titulo, orgao = str(r.get("titulo") or ""), str(r.get("orgao") or "")
    for a in arquivos[:max_arquivos]:
        if len(ex["pontos"]) + len(ex["dispensas"]) >= len(DOZE):
            break
        au = str(a.get("url") or a.get("uri") or "")
        raw, tipo, err = rede.get(au) if au else (None, "", "sem endereço")
        if not raw:
            out["fontes"].append({"fonte": f"arquivo {a.get('tipoDocumentoNome')}", "erro": err}); continue
        lido = L.paginas(raw, tipo, 60)
        if lido.get("ok"):
            _juntar(ex, L.extrair(lido["paginas"], au, titulo, orgao), f"{a.get('tipoDocumentoNome') or 'arquivo'} ({au})", out["fontes"])
        else:
            out["fontes"].append({"fonte": f"arquivo {a.get('tipoDocumentoNome')}", "erro": lido.get("motivo")})
    origem = str(meta.get("linkSistemaOrigem") or "")
    if origem.startswith("http") and len(ex["pontos"]) + len(ex["dispensas"]) < len(DOZE):
        raw, tipo, err = rede.get(origem)
        lido = L.paginas(raw, tipo, 20) if raw else {}
        if lido.get("ok"):
            _juntar(ex, L.extrair(lido["paginas"], origem, titulo, orgao), f"site oficial de origem ({origem})", out["fontes"])
        else:
            out["fontes"].append({"fonte": "site oficial de origem", "erro": err or lido.get("motivo")})
    faltam = [k for k in DOZE if k not in ex["pontos"] and k not in ex["dispensas"]]
    if faltam:                                                  # DISPENSA JUSTIFICADA: só com as fontes esgotadas
        from . import dispensas_itens as DI
        reg, _porque = DI.regime(None, titulo, str(meta.get("objetoCompra") or ""), str(meta.get("informacaoComplementar") or ""))
        mz = DI.matriz()
        disp = ((mz.get("regimes") or {}).get(reg) or {}).get("itens") or {}
        situ = mz.get("situacoes") or {}
        consultadas = [f["fonte"] for f in out["fontes"]]
        for k in list(faltam):
            cod = disp.get(k) if isinstance(disp.get(k), str) else (disp.get(k) or {}).get("situacao") if isinstance(disp.get(k), dict) else None
            if cod in ("nao_se_aplica", "dispensa_provavel"):          # "exigível" nunca é dispensado
                _pq = (disp.get(k) or {}).get("porque") if isinstance(disp.get(k), dict) else None
                ex["dispensas"][k] = {"motivo": (_pq or f"{situ.get(cod, cod)} ({(mz.get('regimes') or {}).get(reg, {}).get('nome', reg)})")[:300],
                                      "tipo": "justificada (fontes esgotadas)", "regime": reg, "fontes_consultadas": consultadas}
                faltam.remove(k)
    out.update({"itens": ex["pontos"], "dispensas": ex["dispensas"], "faltam": faltam,
                "status": "completo" if not faltam else "em trabalho",
                "proximo": None if not faltam else f"Interceptador: confirmar {', '.join(faltam)} na fonte oficial"})
    return out


# ── EXECUÇÃO E INTEGRAÇÃO ──────────────────────────────────────────────────────────────────────────────────────────
def gravar_certidao(certs: dict, d: dict) -> None:
    if d.get("status") not in ("completo", "em trabalho") or not d.get("itens"):
        return
    k = f"estrela:{d['id']}"
    c = certs.get(k) or {"titulo": d.get("titulo"), "tipo": "estrela", "itens": {}, "dispensas": {}, "documentos": []}
    for item, v in d["itens"].items():
        if item not in (c.get("itens") or {}):
            c.setdefault("itens", {})[item] = v
    for item, v in (d.get("dispensas") or {}).items():
        if item not in (c.get("itens") or {}):
            c.setdefault("dispensas", {})[item] = v
    c["ainda_faltam"] = [x for x in DOZE if x not in c["itens"] and x not in (c.get("dispensas") or {})]
    c["leitura"] = "total" if not c["ainda_faltam"] else "parcial"
    c.setdefault("link_oficial", d.get("api"))
    c["em"] = d["em"]; c["dossie_pncp"] = True
    certs[k] = c


def run(limite: int = 60, segundos: int = 1200) -> dict:
    from .cartorio import Rede
    hoje = date.today().isoformat()
    regs = (_j(REPO, {}) or {}).get("registros") or []
    alvos = [r for r in regs if r.get("estado") != "fechada" and not r.get("arquivada")
             and (L.url_meta_pncp(r.get("url")) or L.url_meta_pncp(r.get("link_oficial")))]
    D = _j(DOSSIES, {"dossies": {}}); ant = D.setdefault("dossies", {})
    alvos.sort(key=lambda r: ((ant.get(r["id"]) or {}).get("status") == "completo", str((ant.get(r["id"]) or {}).get("em") or "")))
    rede, t0, feitos = Rede(pausa=0.4), time.time(), 0
    certs_doc = _j(CERT, {"certidoes": {}}); certs = certs_doc.setdefault("certidoes", {})
    for r in alvos[:limite]:
        if time.time() - t0 > segundos:
            break
        if (ant.get(r["id"]) or {}).get("status") == "completo":
            continue
        d = dossie(r, rede, hoje)
        ant[r["id"]] = d; feitos += 1
        gravar_certidao(certs, d)
    from collections import Counter
    st = Counter(d.get("status") for d in ant.values())
    D.update({"em": _agora(), "regra": __doc__.split("RESULTADO por dossiê")[0].strip()[:1500], "resumo": dict(st),
              "completos_pct": round(100 * st.get("completo", 0) / max(1, st.get("completo", 0) + st.get("em trabalho", 0)), 1)})
    DIR.mkdir(parents=True, exist_ok=True)
    DOSSIES.write_text(json.dumps(D, ensure_ascii=False, indent=1), encoding="utf-8")
    fila = [{"id": i, "titulo": d.get("titulo"), "url": d.get("api"), "faltam": d.get("faltam"), "desde": d.get("em")}
            for i, d in ant.items() if d.get("status") == "em trabalho" and d.get("faltam")]
    PARA_INTERCEPTADOR.write_text(json.dumps({"em": _agora(), "itens": fila}, ensure_ascii=False, indent=1), encoding="utf-8")
    CERT.write_text(json.dumps(certs_doc, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"feitos_agora": feitos, "alvos": len(alvos), "resumo": dict(st), "completos_pct": D["completos_pct"], "para_interceptador": len(fila)}


if __name__ == "__main__":
    import sys
    print(json.dumps(run(int(sys.argv[1]) if len(sys.argv) > 1 else 60), ensure_ascii=False))
