"""FICHA DA OPORTUNIDADE (titular, 12/10/2026) — docs/prompts/PROMPT-FICHA-DA-OPORTUNIDADE-2026-10-12.md

Para cada oportunidade aberta (repositório único), junta o que a janela do painel mostra ao clicar no cartão:
  achado    · qual motor/sensor ou agregador encontrou, a fonte, as datas e o TRECHO que indica ser oportunidade
  esteira   · etapa, próximo passo, desde quando, os 12 itens (conhecidos, dispensados, faltando), onde buscar
  sistemas  · o que cada sistema já averiguou (motores, rede neural, Cartório, Interceptador, validação/Chrome,
              verificação externa), com data e resultado, e o que ainda falta
  livro     · tudo o que o livro da oportunidade guarda (edições, previsão, regime, acionamento, diagnóstico…)
Saída: docs/dados/fichas_oportunidades.json ({"fichas": {id: ficha}, "alias": {id_origem: id}}).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAIDA = ROOT / "docs/dados/fichas_oportunidades.json"
REP = ROOT / "biblioteca_alexandria/livros/_vistas/repositorio_unico.json"
COLETA = ROOT / "dados/oportunidades/oportunidades.jsonl"
AGREG = ROOT / "estado/agregadores/itens.json"
CATALOGO = ROOT / "biblioteca_alexandria/fontes/motores.json"
FLUXO = ROOT / "docs/dados/fluxo_oportunidades.json"


def _j(p: Path, padrao=None):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao if padrao is not None else {}


def _curto(v, n=400):
    return (str(v)[:n] + "…") if v is not None and len(str(v)) > n else v


def _coleta(ids: set) -> dict:
    out = {}
    if not COLETA.exists() or not ids:
        return out
    with COLETA.open(encoding="utf-8") as f:
        for linha in f:
            if '"id"' not in linha:
                continue
            try:
                x = json.loads(linha)
            except ValueError:
                continue
            if x.get("id") in ids:
                out[x["id"]] = x
    return out


DECISAO = {"valida": "válida", "valida_fora_abrangencia": "válida, mas fora da abrangência da associação", "invalida": "inválida",
           "encerrada": "encerrada", "nao_e_oportunidade": "não é oportunidade", "duplicada": "duplicada", "ilegivel": "não foi possível ler"}


def _livro(L: dict | None) -> dict | None:
    if not L:
        return None
    hist = []
    for h in (L.get("historico") or [])[-8:]:
        if isinstance(h, dict):
            hist.append({k: _curto(h.get(k), 160) for k in ("titulo", "ano", "inicio", "fim", "pagina_oficial", "url", "situacao", "registrado_em") if h.get(k)})
    ins = (L.get("livro") or {}).get("inscricao") or {}
    return {
        "id": L.get("id"), "nome": L.get("nome_classificado") or L.get("programa") or L.get("rotulo"), "orgao": L.get("orgao"),
        "rotulo": L.get("rotulo"), "criado_em": L.get("criado_em"), "ultima_leitura": L.get("ultima_leitura"),
        "selo_livro": L.get("selo_livro"), "esteira": L.get("esteira"), "edicoes": L.get("edicoes"), "janelas": L.get("janelas"),
        "historico": hist, "previsao": L.get("previsao"), "regime_inscricao": L.get("regime_inscricao"),
        "janelas_inscricao": ins.get("janelas"), "mes_tipico": ins.get("mes_tipico"),
        "acionamento": L.get("chave_acionamento"), "diagnostico": L.get("diagnostico"), "validacao": L.get("validacao"),
        "vigilancia": L.get("proximidade"), "pagina": L.get("pagina"), "paginas": (L.get("paginas") or [])[:6],
        "abrangencia": L.get("abrangencia"), "publico": L.get("publico"), "tipo_objeto": L.get("tipo_objeto"),
        "livros_juntados": L.get("ids_juntados"), "observacao_coleta": _curto((L.get("livro_coleta") or {}).get("observacao"), 500),
        "revisao_exclusao": L.get("revisao_exclusao"), "inscricao_realizada": L.get("inscricao_realizada"),
    }


def montar() -> dict:
    R = (_j(REP, {}).get("registros") or [])
    abertas = [r for r in R if r.get("estado") != "fechada"]
    # 16/10/2026 (titular, etapa 2): as fichas leem dos LIVROS — fluxo, achado bruto de cada motor e agregador ficam no
    # livro; os arquivos antigos só como reserva enquanto o livro ainda não tem a seção
    from . import banco_livros as BL
    ids_origem = {i for r in abertas for i in [r["id"], *(r.get("ids_origem") or [])]}
    fl = BL.secoes_dos_livros("brutos:fluxo") or {x.get("id"): x for v in ((_j(FLUXO, {}) or {}).get("itens_por_uf") or {}).values() for x in v}
    col = {i: x for i, x in BL.secoes_dos_livros("coleta").items() if i in ids_origem} or _coleta(ids_origem)
    ag = BL.secoes_dos_livros("agregador") or {str(x.get("id")): x for x in ((__import__("src.livro_arquivo", fromlist=["x"]).ler_arquivo(AGREG, {}) or {}).get("itens") or [])}
    cat = {m.get("id"): m for m in ((_j(CATALOGO, {}) or {}).get("motores") or [])}
    cur = {x.get("id"): x for x in ((_j(ROOT / "estado/curadoria_links.json", {}) or {}).get("itens") or [])}   # 15/10: curadoria
    fichas, alias = {}, {}
    for r in abertas:
        f = fl.get(r["id"]) or next((fl[i] for i in (r.get("ids_origem") or []) if i in fl), {}) or {}
        achados = []
        for i in [*(r.get("ids_origem") or []), r["id"]]:
            c, a = col.get(i), ag.get(i)
            if c:
                achados.append({"id": i, "motor": c.get("sensor") or c.get("tipo_fonte"), "fonte": c.get("fonte_nome"), "tipo_fonte": c.get("tipo_fonte"),
                                "descoberto_em": c.get("descoberto_em"), "coletado_em": c.get("coletado_em"), "publicado_em": c.get("data_publicacao"),
                                "trecho": _curto(c.get("evidencia"), 600), "prazo_texto": c.get("prazo_texto"), "valor_texto": c.get("valor_texto"), "url": c.get("url")})
            elif a:
                achados.append({"id": i, "motor": f"agregadores · {a.get('fonte') or a.get('motor')}", "fonte": a.get("fonte"), "tipo_fonte": "agregador",
                                "descoberto_em": a.get("primeiro_visto"), "coletado_em": a.get("visto_em"), "publicado_em": a.get("publicado"),
                                "trecho": _curto(a.get("titulo") if len(str(a.get("perfil") or "")) < 40 else a.get("perfil"), 600), "prazo_texto": a.get("prazo"), "valor_texto": a.get("valor"),
                                "url": a.get("link_oficial") or a.get("pagina_agregador")})
        if not achados and (r.get("origem") or r.get("fontes")):
            achados.append({"id": r["id"], "motor": r.get("origem"), "fonte": ", ".join(r.get("fontes") or [])[:200], "trecho": None})
        itens = r.get("itens") or {}
        ins = f.get("inspecao") or {}
        sistemas = [
            {"sistema": "Motores (coleta)", "quando": min((x.get("descoberto_em") or x.get("coletado_em") or "9") for x in achados) if achados else None,
             "resultado": f"{len(achados)} achado(s): " + "; ".join(str(x.get('motor') or '—') for x in achados[:4])},
            {"sistema": "Rede neural", "quando": None, "resultado": f"nota {r.get('nota_rede')} (chance de ser oportunidade real)" if r.get("nota_rede") is not None else "sem nota"},
            {"sistema": "Cartório", "quando": (r.get("cartorio") or {}).get("em"),
             "resultado": (f"{(r.get('cartorio') or {}).get('tentativas', 0)} tentativa(s)" + (" · esgotada" if (r.get("cartorio") or {}).get("esgotada") else ""))},
            {"sistema": "Interceptador", "quando": ins.get("em"),
             "resultado": (f"{ins.get('qualidade')} · {ins.get('comprovados')} itens comprovados · prazo {ins.get('prazo') or '—'}" if ins else "ainda não estudou")},
            {"sistema": "Validação individual / Chrome", "quando": (f.get("validacao") or {}).get("em") if isinstance(f.get("validacao"), dict) else None,
             "resultado": (f"{DECISAO.get((f.get('validacao') or {}).get('decisao'), str((f.get('validacao') or {}).get('decisao')).replace('_', ' '))} — {_curto((f.get('validacao') or {}).get('motivo'), 260)}" if isinstance(f.get("validacao"), dict) and f.get("validacao") else "não validada individualmente")},
        ]
        L = _livro(cat.get(r.get("livro")))
        fichas[r["id"]] = {
            "id": r["id"], "titulo": r.get("titulo"), "orgao": r.get("orgao"), "uf": r.get("uf"), "url": r.get("url"),
            # 15/10/2026 (titular): DOIS LINKS — onde foi achada (acesso) e onde foi publicada (oficial, só se aprovado na
            # curadoria); o mesmo só quando captada direto no local oficial — e o TRECHO exato da oportunidade
            "link_acesso": (cur.get(r["id"]) or {}).get("link_acesso") or r.get("url"),
            "link_oficial": (cur.get(r["id"]) or {}).get("link_oficial") if r["id"] in cur else r.get("link_oficial"),
            "curadoria_link_oficial": {k: (cur.get(r["id"]) or {}).get(k) for k in ("curadoria", "classe_do_link_oficial", "falham", "proximo_passo",
                                                                                   "captada_direto_na_fonte_oficial", "link_oficial_proposto")} if r["id"] in cur else None,
            "trecho_da_oportunidade": (cur.get(r["id"]) or {}).get("trecho"),
            "estado": r.get("estado"), "arquivada": r.get("arquivada"), "fim": r.get("fim"),
            "achado": achados,
            "esteira": {"etapa": r.get("etapa"), "proximo_passo": r.get("proximo_passo"), "no_passo_desde": r.get("no_passo_desde"), "estagnado": r.get("estagnado"),
                        "ferramenta": r.get("ferramenta"), "estante": r.get("estante"), "prioridade": r.get("prioridade"), "pronta_para_farol": r.get("pronta_para_farol"),
                        "onde_buscar": (r.get("onde_buscar") or [])[:6], "faltam": r.get("faltam") or [],
                        "itens": {k: {"estado": v.get("estado"), "valor": _curto(v.get("valor"), 220), "trecho": _curto(v.get("trecho"), 260)} for k, v in itens.items() if isinstance(v, dict)}},
            "sistemas": sistemas,
            "livro": L, "livro_motivo_sem": r.get("motivo_sem_livro"),
        }
        for i in r.get("ids_origem") or []:
            alias[i] = r["id"]
    return {"em": datetime.now(timezone.utc).replace(microsecond=0).isoformat(), "total": len(fichas), "fichas": fichas, "alias": alias}


def run() -> dict:
    res = montar()
    SAIDA.write_text(json.dumps(res, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {"fichas": res["total"], "kb": SAIDA.stat().st_size // 1024}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False))
