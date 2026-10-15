"""DIAGNÓSTICO ÚNICO DO SISTEMA (titular, 14/10/2026) — backend; nada de página, quadro ou apresentação.

Quando a titular pede "Analise o sistema", o Claude roda:
    python -m src.diagnostico_sistema              # só diagnostica
    python -m src.diagnostico_sistema --corrigir   # diagnostica, corrige em sequência e diagnostica de novo
e lê estado/diagnostico_sistema.md (resumo) e estado/diagnostico_sistema.json (completo).

O que reúne num só lugar:
  1. SISTEMAS   motores (status, cadência, auditoria), maestro, rede neural, Cartório, Pilotos (Interceptador e
                Espião), saúde (arquivos, frescor, coerência, fluxos do GitHub), auditoria cega, sala de controle
  2. OPORTUNIDADES, uma a uma (repositório único, abertas): tem livro? o livro existe no catálogo? está validada?
                tem site oficial e prazo? aparece na tela (fluxo) e na ficha? decisão da titular aplicada?
  3. INTEGRAÇÃO repositório × tela × fichas × catálogo de livros × decisões × indicadores: mesmos ids, mesmas
                contagens, todos em dia
  4. PROBLEMAS  cada um com gravidade e a CORREÇÃO que se aplica
  5. WORKFLOW   (15/10) comando único, retentativa, leitura parcial, curadoria, validação por exceção, auditorias, legislativo
  6. DECISÕES   (15/10) em cada etapa, o que o Eldorado decidiu × a regra que deveria valer (correto/incorreto)
  7. CICLOS     (15/10) janela desde a análise anterior, correções implantadas, resolvidos/persistem/novos/sem correção;
                a próxima janela começa na implantação das correções (estado/analise_ciclos.json)

Correções (--corrigir), uma etapa depois da outra (nada em paralelo), com as rotinas que o sistema já tem:
  decisões da titular → livros (criar/vincular) → repositório único → tela das oportunidades → fichas →
  sala de controle → saúde
Problemas que não têm correção automática (motor em falha, fluxo do GitHub falhando, item sem site oficial) ficam
listados com a ação recomendada, para a análise do Claude e do conselho.
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAIDA = ROOT / "estado/diagnostico_sistema.json"
RESUMO = ROOT / "estado/diagnostico_sistema.md"
D = ROOT / "docs/dados"
FRESCOR_H = {"repositorio": 3, "fluxo": 3, "fichas": 3, "sala_controle": 3, "status_motores": 8, "maestro": 3, "rede_neural": 26, "saude": 26}


def _j(p: Path, padrao=None):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao if padrao is not None else {}


def _idade_h(ts) -> float | None:
    try:
        t = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        t = t if t.tzinfo else t.replace(tzinfo=timezone.utc)
        return round((datetime.now(timezone.utc) - t).total_seconds() / 3600, 1)
    except Exception:  # noqa: BLE001
        return None


def _problema(lista, codigo, gravidade, texto, correcao=None, quantidade=None, exemplos=None):
    lista.append({"codigo": codigo, "gravidade": gravidade, "texto": texto, "correcao": correcao,
                  "quantidade": quantidade, "exemplos": (exemplos or [])[:8]})


def sistemas(P: list) -> dict:
    st, ma, rn = _j(D / "status_motores.json"), _j(D / "maestro.json"), _j(D / "rede_neural.json")
    ca, it, es = _j(D / "cartorio.json"), _j(D / "interceptador.json"), _j(D / "espiao_avaliacao.json")
    sa, sc = _j(D / "saude.json"), _j(D / "sala_controle.json")
    am, ac = _j(ROOT / "estado/auditoria_motores.json"), _j(ROOT / "estado/auditoria_cega.json")
    mot = st.get("motores") or []
    vermelhos = [{"id": m.get("id"), "nome": m.get("nome"), "resultado": m.get("resultado")} for m in mot if m.get("luz") == "vermelho"]
    atencao = [{"id": m.get("id"), "nome": m.get("nome"), "resultado": m.get("resultado")} for m in mot if m.get("luz") == "verde" and "atenção" in str(m.get("resultado"))]
    for m in vermelhos:
        _problema(P, "motor_em_falha", "alta", f"motor em falha: {m['nome']} — {m['resultado']}", "investigar o motor (sem correção automática)")
    vc = rn.get("validacao_cruzada") or {}
    if vc.get("auc") is not None and vc["auc"] < 0.8:
        _problema(P, "rede_neural_fraca", "media", f"rede neural com discernimento abaixo do normal (AUC {vc['auc']})", "retreinar com mais decisões rotuladas")
    for a in sa.get("alertas") or []:
        _problema(P, f"saude_{a.get('area')}", "media", f"saúde · {a.get('area')}: {a.get('texto')}",
                  "refazer tela e indicadores" if a.get("area") in ("coerência", "frescor") else "ver o fluxo/arquivo indicado")
    fluxos = sc.get("fluxos") or []
    return {
        "motores": {"total": len(mot), "funcionando": sum(1 for m in mot if m.get("luz") == "verde"), "em_falha": len(vermelhos),
                    "inativos": sum(1 for m in mot if m.get("luz") == "cinza"), "em_falha_lista": vermelhos, "leitura_parcial": atencao,
                    "status_em": st.get("gerado_em"), "auditoria": {k: am.get(k) for k in ("em", "total", "por_estado")}},
        "maestro": {k: ma.get(k) for k in ("em", "planejados", "cobertura_percentual", "cobertura", "dia_fechado")}
                   | {"esgotaram_tentativas": len(ma.get("esgotaram_tentativas") or []) if isinstance(ma.get("esgotaram_tentativas"), list) else ma.get("esgotaram_tentativas"),
                      "a_disparar": len(ma.get("a_disparar") or []) if isinstance(ma.get("a_disparar"), list) else ma.get("a_disparar")},
        "rede_neural": {"em": rn.get("em"), "modelo_treinado_em": rn.get("modelo_treinado_em"), "rotulados": rn.get("rotulados"),
                        "validacao_cruzada": vc, "pendentes_provaveis_reais": rn.get("pendentes_provaveis_reais")},
        "cartorio": {"em": ca.get("em"), "resumo": ca.get("resumo")},
        "pilotos": {"interceptador": {"estado": it.get("estado"), "ultimo_voo": it.get("ultimo_voo") or it.get("em"), "contagem": it.get("contagem")},
                    "espiao": {"em": es.get("em"), "voos": es.get("voos"), "empresas_novas": es.get("empresas_novas")}},
        "saude": {"em": sa.get("em"), "alertas": sa.get("alertas") or []},
        "auditoria_cega": {k: ac.get(k) for k in ("em", "taxa_de_perda", "sem_nada_na_base")},
        "fluxos_github": {"total": len(fluxos), "com_falha": [f.get("nome") for f in fluxos if f.get("conclusao") == "failure"]},
        "sala_controle": {"em": sc.get("em"), "indice_saude": sc.get("indice_saude"), "contagem": sc.get("contagem")},
    }


def oportunidades(P: list, hoje: str) -> dict:
    R = (_j(ROOT / "dados/oportunidades/repositorio_unico.json", {}).get("registros") or [])
    abertas = [r for r in R if r.get("estado") != "fechada" and not r.get("arquivada")]
    cat = {m.get("id"): m for m in (_j(ROOT / "biblioteca_alexandria/fontes/motores.json", {}).get("motores") or [])}
    fl = {x.get("id") for v in (_j(D / "fluxo_oportunidades.json", {}).get("itens_por_uf") or {}).values() for x in v}
    fichas = _j(D / "fichas_oportunidades.json", {}); fid = set((fichas.get("fichas") or {}).keys()) | set((fichas.get("alias") or {}).keys())
    idx = (_j(ROOT / "estado/opressores_indice.json", {}).get("indice") or {})
    sem_livro_regra = Counter()
    sem_livro, livro_inexistente, sem_site, sem_prazo, vencida, fora_tela, sem_ficha = [], [], [], [], [], [], []
    estados = Counter(); faltam = Counter()
    for r in abertas:
        estados[r.get("estado")] += 1
        nome = f"{(r.get('titulo') or '')[:70]} [{r['id']}]"
        if not r.get("livro"):
            regra = next(((idx.get(i) or {}).get("dispensa") for i in [r["id"], *(r.get("ids_origem") or [])] if (idx.get(i) or {}).get("dispensa")), None) or r.get("motivo_sem_livro")
            if regra:
                sem_livro_regra[str(regra)[:90]] += 1          # sem livro por regra registrada: não é problema
            else:
                sem_livro.append(nome)
        elif r["livro"] not in cat:
            livro_inexistente.append(nome)
        if not r.get("link_oficial"):
            sem_site.append(nome)
        if not r.get("fim") and r.get("regime") != "fluxo_continuo":
            sem_prazo.append(nome)
        elif r.get("fim") and str(r["fim"]) < hoje:
            vencida.append(nome)
        ids = {r["id"], *(r.get("ids_origem") or [])}
        if not ids & fl:
            fora_tela.append(nome)
        if not ids & fid:
            sem_ficha.append(nome)
        for k in r.get("faltam") or []:
            faltam[k] += 1
    n = len(abertas)
    if sem_livro:
        _problema(P, "oportunidade_sem_livro", "alta", f"{len(sem_livro)} de {n} oportunidades abertas sem livro e sem regra que justifique", "criar/vincular livros", len(sem_livro), sem_livro)
    if livro_inexistente:
        _problema(P, "livro_inexistente", "alta", f"{len(livro_inexistente)} oportunidades apontam para livro que não existe no catálogo",
                  "criar/vincular livros e refazer o repositório", len(livro_inexistente), livro_inexistente)
    if vencida:
        _problema(P, "prazo_vencido_aberta", "alta", f"{len(vencida)} oportunidades com prazo vencido ainda contadas como abertas", "refazer o repositório", len(vencida), vencida)
    if fora_tela:
        _problema(P, "fora_da_tela", "alta", f"{len(fora_tela)} abertas no repositório que não aparecem na tela de oportunidades", "refazer a tela", len(fora_tela), fora_tela)
    if sem_ficha:
        _problema(P, "sem_ficha", "media", f"{len(sem_ficha)} abertas sem ficha (janela de detalhe)", "refazer as fichas", len(sem_ficha), sem_ficha)
    if sem_site:
        _problema(P, "sem_site_oficial", "media", f"{len(sem_site)} abertas ainda sem site oficial", "Cartório/Interceptador (sem correção automática imediata)", len(sem_site), sem_site)
    if sem_prazo:
        _problema(P, "sem_prazo", "baixa", f"{len(sem_prazo)} abertas sem prazo de inscrição conhecido", "Cartório/Interceptador (sem correção automática imediata)", len(sem_prazo), sem_prazo)
    # 14/10 (titular): só Goiás tem oportunidades e livros municipais
    try:
        from .repositorio_unico import municipal_fora_de_goias
        uf_ag = {str(x.get("id")): x.get("uf") for x in ((_j(ROOT / "estado/agregadores/itens.json", {}) or {}).get("itens") or []) if x.get("uf")}
        mun_ab = [f"{(r.get('titulo') or '')[:70]} [{r['id']}]" for r in abertas
                  if municipal_fora_de_goias(r, next((uf_ag[i] for i in [r["id"], *(r.get("ids_origem") or [])] if i in uf_ag), None))]
    except Exception:  # noqa: BLE001
        mun_ab = []
    try:
        from .curadoria_biblioteca import fora_da_abrangencia
        prot = {r.get("livro") for r in abertas if r.get("livro")}
        mun_lv = [f"{x.get('nome_classificado') or x.get('programa') or x['id']} [{x['id']}]" for x in cat.values() if fora_da_abrangencia(x) and x["id"] not in prot]
    except Exception:  # noqa: BLE001
        mun_lv = []
    Qt = (_j(ROOT / "config/testes_quarentena.json", {}) or {}).get("modulos") or {}
    reais = [f"{k}: {v.get('motivo')}" for k, v in Qt.items() if v.get("categoria") == "defeito real a corrigir"]
    if reais:
        _problema(P, "teste_em_quarentena_defeito", "alta", f"{len(reais)} módulos de teste em quarentena por DEFEITO REAL", "corrigir o código e tirar da quarentena (sem correção automática)", len(reais), reais)
    outros = [f"{k} ({v.get('categoria')})" for k, v in Qt.items() if v.get("categoria") != "defeito real a corrigir"]
    if outros:
        _problema(P, "teste_em_quarentena", "baixa", f"{len(outros)} módulos de teste em quarentena (envelhecidos)", "atualizar o teste à regra atual (sem correção automática)", len(outros), outros)
    if mun_ab:
        _problema(P, "municipal_de_outro_estado_aberta", "alta", f"{len(mun_ab)} oportunidades municipais de outros estados ainda abertas (só Goiás tem municipais)",
                  "refazer o repositório", len(mun_ab), mun_ab)
    if mun_lv:
        _problema(P, "livro_municipal_de_outro_estado", "media", f"{len(mun_lv)} livros municipais de outros estados no catálogo (só Goiás tem livros municipais)",
                  "refazer a tela", len(mun_lv), mun_lv)
    return {"abertas": n, "por_estado": dict(estados), "municipais_de_outro_estado_abertas": len(mun_ab), "livros_municipais_de_outro_estado": len(mun_lv), "validadas": estados.get("validada", 0),
            "percentual_validadas": round(100 * estados.get("validada", 0) / n, 1) if n else None,
            "com_livro": n - len(sem_livro) - sum(sem_livro_regra.values()), "sem_livro": len(sem_livro),
            "sem_livro_por_regra": sum(sem_livro_regra.values()), "sem_livro_por_regra_motivos": dict(sem_livro_regra.most_common(6)),
            "livro_inexistente": len(livro_inexistente),
            "sem_site_oficial": len(sem_site), "sem_prazo": len(sem_prazo), "prazo_vencido": len(vencida),
            "fora_da_tela": len(fora_tela), "sem_ficha": len(sem_ficha), "itens_que_mais_faltam": dict(faltam.most_common(12))}


def integracao(P: list, op: dict) -> dict:
    rr = _j(D / "repositorio_resumo.json"); fl = _j(D / "fluxo_oportunidades.json"); fi = _j(D / "fichas_oportunidades.json")
    sc = _j(D / "sala_controle.json"); ma = _j(D / "maestro.json"); rn = _j(D / "rede_neural.json"); st = _j(D / "status_motores.json"); sa = _j(D / "saude.json")
    n_tela = sum(len(v) for v in (fl.get("itens_por_uf") or {}).values())
    sc_ab = next((i.get("valor") for i in (sc.get("instrumentos") or []) if i.get("id") == "es_abertas"), None)
    contagens = {"repositorio_abertas": rr.get("abertas"), "diagnostico_abertas": op["abertas"], "tela_cartoes": n_tela,
                 "fichas": fi.get("total"), "sala_controle_abertas": sc_ab}
    if rr.get("abertas") is not None and n_tela and abs(int(rr["abertas"]) - n_tela) > 0:
        _problema(P, "tela_diverge_do_repositorio", "alta", f"tela mostra {n_tela} oportunidades e o repositório conta {rr['abertas']}", "refazer a tela")
    if sc_ab is not None and rr.get("abertas") is not None and sc_ab != rr["abertas"]:
        _problema(P, "indicadores_desatualizados", "media", f"sala de controle conta {sc_ab} abertas e o repositório {rr['abertas']}", "refazer a sala de controle")
    frescor = {"repositorio": rr.get("em"), "fluxo": fl.get("gerado_em") or fl.get("em"), "fichas": fi.get("em"), "sala_controle": sc.get("em"),
               "status_motores": st.get("gerado_em"), "maestro": ma.get("em"), "rede_neural": rn.get("em"), "saude": sa.get("em")}
    idade = {k: _idade_h(v) for k, v in frescor.items()}
    for k, h in idade.items():
        if h is None or h > FRESCOR_H[k]:
            _problema(P, f"atrasado_{k}", "media", f"{k} sem atualização há {h if h is not None else '?'} h (limite {FRESCOR_H[k]} h)",
                      {"repositorio": "refazer o repositório", "fluxo": "refazer a tela", "fichas": "refazer as fichas", "sala_controle": "refazer a sala de controle",
                       "saude": "refazer a saúde"}.get(k, "ver o fluxo que gera este dado"))
    dec = _j(ROOT / "estado/decisoes_editais.json", {}); dec = dec.get("decisoes") if isinstance(dec.get("decisoes"), dict) else {}
    R = {r["id"]: r for r in (_j(ROOT / "dados/oportunidades/repositorio_unico.json", {}).get("registros") or [])}
    nao_aplicadas = [k for k, v in dec.items() if v.get("estado") in ("descartado", "inscrito") and k in R and not R[k].get("arquivada") and R[k].get("estado") != "fechada"]
    if nao_aplicadas:
        _problema(P, "decisao_nao_aplicada", "alta", f"{len(nao_aplicadas)} decisões da titular ainda não aplicadas no repositório", "aplicar as decisões", len(nao_aplicadas), nao_aplicadas)
    return {"contagens": contagens, "idade_horas": idade, "decisoes_da_titular": len(dec), "decisoes_nao_aplicadas": len(nao_aplicadas)}


# ── 14/10 (2ª versão): parâmetros de TUDO que roda, finalidade de cada sistema e conferência da sala de controle ─────
REPO = "amcjardimamerica-arch/Eldorado"
MARCAS_FALHA = ("falhou", "falha:", "Traceback", "Error:", "REGISTRO FALHOU")


def _gh(caminho: str, bruto: bool = False):
    import os, urllib.request
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not tok:
        return None
    class _SemSeguir(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None
    try:
        req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/{caminho}", headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"})
        try:
            with urllib.request.build_opener(_SemSeguir).open(req, timeout=40) as r:
                corpo = r.read()
        except urllib.error.HTTPError as e:            # registros: o GitHub redireciona ao armazenamento, que recusa a credencial
            if e.code in (301, 302, 303, 307, 308) and e.headers.get("Location"):
                with urllib.request.urlopen(e.headers["Location"], timeout=60) as r:
                    corpo = r.read()
            else:
                return None
        return corpo.decode("utf-8", "replace") if bruto else json.loads(corpo)
    except Exception:  # noqa: BLE001
        return None


def _cadencia_h(texto_yml: str) -> float | None:
    """Cadência esperada do fluxo, pelos crons do próprio arquivo (o menor intervalo entre disparos)."""
    import re
    crons = re.findall(r'cron:\s*"([^"]+)"', texto_yml)
    if not crons:
        return None
    menor = 24 * 7.0
    for c in crons:
        mi, ho, dm, me, ds = (c.split() + ["*"] * 5)[:5]
        if ho.startswith("*/"):
            menor = min(menor, float(ho[2:]))
        elif "," in ho:
            hs = sorted(int(h) for h in ho.split(",") if h.isdigit()); gaps = [b - a for a, b in zip(hs, hs[1:])] + [24 - hs[-1] + hs[0]]
            menor = min(menor, float(min(gaps)))
        elif mi.startswith("*/"):
            menor = min(menor, float(mi[2:]) / 60)
        elif ho == "*":
            menor = min(menor, 1.0)
        elif ds not in ("*", "") or dm not in ("*", ""):
            menor = min(menor, 24 * 7.0 if ds not in ("*", "") and "-" not in ds and "," not in ds else 24.0)
        else:
            menor = min(menor, 24.0)
    return menor


def execucao(P: list) -> dict:
    """Cada fluxo do GitHub: cadência esperada, última execução, taxa de sucesso; e as falhas SILENCIOSAS (etapas que
    rodam com '|| echo falhou' e não derrubam o fluxo) lidas nos registros das execuções mais recentes."""
    import re
    fluxos = []
    por_arq = {}
    for y in sorted((ROOT / ".github/workflows").glob("*.yml")):       # execuções POR fluxo (os frequentes não escondem os raros)
        por_arq[y.name] = (_gh(f"actions/workflows/{y.name}/runs?per_page=10") or {}).get("workflow_runs") or []
    runs = [r for v in por_arq.values() for r in v]
    for y in sorted((ROOT / ".github/workflows").glob("*.yml")):
        t = y.read_text(encoding="utf-8"); nome = (re.search(r"^name:\s*(.+)$", t, re.M) or [None, y.stem])[1]
        cad = _cadencia_h(t); R = por_arq.get(y.name, [])
        conc = [x.get("conclusion") for x in R if x.get("status") == "completed"]
        taxa = round(100 * sum(1 for c in conc if c == "success") / len(conc)) if conc else None
        ult = R[0] if R else {}
        idade = _idade_h(ult.get("created_at")) if ult else None
        estado = "sem_dados" if not runs else "falha" if conc[:3] and all(c == "failure" for c in conc[:3]) else \
                 "atrasado" if cad and (idade is None or idade > cad * 3 + 6) else "atencao" if taxa is not None and taxa < 80 else "ok" if R else ("manual" if not cad else "nunca_rodou")
        fluxos.append({"arquivo": y.name, "nome": nome, "cadencia_h": cad, "ultima": ult.get("created_at"), "idade_h": idade,
                       "ultima_conclusao": ult.get("conclusion"), "sucesso_pct": taxa, "execucoes_vistas": len(R), "estado": estado})
        if estado == "falha":
            _problema(P, "fluxo_falhando", "alta", f"fluxo '{nome}' falhou nas últimas execuções ({taxa}% de sucesso)", "investigar o fluxo (sem correção automática)")
        elif estado == "atrasado":
            _problema(P, "fluxo_atrasado", "media", f"fluxo '{nome}' sem rodar há {idade} h (cadência {cad} h)", "investigar o agendamento (sem correção automática)")
    silenciosas = {}; lidos = 0
    # 15/10 (ciclo 6): sem o analise-sistema.yml — o log dele contém o próprio relatório ("falhou", "falha:") e a análise
    # acusava a si mesma; os erros reais da análise aparecem nos testes dela e no veredito
    # o fluxo 30 (Cartório) passou a ser só manual: o Cartório roda DENTRO do comando (os erros dele estão no log do 22)
    for arq in ("motores-da-vez.yml", "motor-agregadores.yml", "monitoramento-diario.yml"):
        ult = next((x for x in por_arq.get(arq, []) if x.get("status") == "completed"), None)
        if not ult:
            continue
        jobs = (_gh(f"actions/runs/{ult['id']}/jobs") or {}).get("jobs") or []
        for j in jobs[:2]:
            log = _gh(f"actions/jobs/{j['id']}/logs", bruto=True) or ""
            lidos += bool(log)
            linhas = sorted({re.sub(r"^\S+Z\s+", "", l).strip()[:160] for l in log.splitlines()
                             if any(m in l for m in MARCAS_FALHA) and "|| echo" not in l and "echo \"" not in l and "grep" not in l})
            if linhas:
                silenciosas[arq] = linhas[:15]
    for arq, L in silenciosas.items():
        _problema(P, "falha_silenciosa", "alta", f"{len(L)} etapa(s) falharam em silêncio na última execução de {arq}: " + " | ".join(L[:3]),
                  "investigar a etapa (sem correção automática)", len(L), L)
    if runs and not lidos:
        _problema(P, "registros_nao_lidos", "baixa", "os registros das execuções não puderam ser lidos: falhas silenciosas não conferidas", "rodar a análise pelo fluxo 36 (sem correção automática)")
    return {"fluxos": fluxos, "falhas_silenciosas": silenciosas, "registros_lidos": lidos, "sem_token": not runs,
            "resumo": dict(Counter(f["estado"] for f in fluxos))}


def _pct(v):
    return None if v is None else max(0, min(100, round(v)))


def finalidade(s: dict, o: dict, i: dict, e: dict) -> dict:
    """Cada sistema contra a META da sua finalidade (0–100%). 100% = atinge o que foi projetado."""
    m = s["motores"]; vc = s["rede_neural"]["validacao_cruzada"]; n = o["abertas"] or 1
    aplic = n - o["sem_livro_por_regra"]
    fl = e.get("fluxos") or []; fl_ag = [f for f in fl if f["cadencia_h"]]
    cart = (s["cartorio"].get("resumo") or {}).get("pct_certificado_12")
    itens = [
        ("Motores", "todo motor ativo lê dentro da sua cadência", _pct(100 * m["funcionando"] / max(1, m["total"] - m["inativos"]))),
        ("Maestro", "cobertura completa do dia planejado", _pct(s["maestro"].get("cobertura_percentual"))),
        ("Rede neural", "discernimento (AUC) de pelo menos 0,85", _pct(100 * min(1, (vc.get("auc") or 0) / 0.85)) if vc.get("auc") else None),
        ("Biblioteca", "toda oportunidade aberta aplicável com livro existente", _pct(100 * (aplic - o["sem_livro"] - o["livro_inexistente"]) / max(1, aplic))),
        ("Validação", "toda oportunidade aberta validada", _pct(100 * o["validadas"] / n)),
        ("Site oficial", "toda aberta com site oficial", _pct(100 * (n - o["sem_site_oficial"]) / n)),
        ("Prazo", "toda aberta com prazo (ou fluxo contínuo)", _pct(100 * (n - o["sem_prazo"]) / n)),
        ("Cartório", "12 de 12 itens certificados na fonte oficial", _pct(100 * cart) if isinstance(cart, (int, float)) else None),
        ("Tela e fichas", "tudo que está aberto aparece na tela e tem ficha", _pct(100 * (n - max(o["fora_da_tela"], o["sem_ficha"])) / n)),
        ("Integração", "mesmas contagens e dados em dia em todos os sistemas", _pct(100 - 20 * sum(1 for v in i["idade_horas"].values() if v is None or v > 26) - (0 if len({v for v in i["contagens"].values() if v is not None and v != i["contagens"].get("fichas")}) <= 1 else 30))),
        ("Fluxos automáticos", "todo fluxo agendado roda na cadência e sem falha", _pct(100 * sum(1 for f in fl_ag if f["estado"] == "ok") / len(fl_ag)) if fl_ag and not e.get("sem_token") else None),
        ("Execução sem falha silenciosa", "nenhuma etapa falha em silêncio", None if e.get("sem_token") or not e.get("registros_lidos") else (100 if not e.get("falhas_silenciosas") else _pct(100 - 10 * sum(len(v) for v in e["falhas_silenciosas"].values())))),
    ]
    L = [{"sistema": a, "finalidade": b, "atingido_pct": c, "estado": "sem_dados" if c is None else "ok" if c >= 95 else "atencao" if c >= 70 else "falha"} for a, b, c in itens]
    val = [x["atingido_pct"] for x in L if x["atingido_pct"] is not None]
    return {"sistemas": L, "indice_geral_pct": round(sum(val) / len(val)) if val else None}


def conferir_sala(P: list, s: dict, o: dict) -> dict:
    """A sala de controle mostra o que deveria? Recalcula cada indicador na fonte e compara; aponta lacunas e melhorias."""
    sc = _j(D / "sala_controle.json"); I = {x.get("id"): x for x in sc.get("instrumentos") or []}
    rr = _j(D / "repositorio_resumo.json"); st = s["motores"]; rn = s["rede_neural"]["validacao_cruzada"]; ma = s["maestro"]
    esperado = {"es_abertas": rr.get("abertas"), "rn_auc": rn.get("auc"), "rn_precisao": rn.get("precisao"), "rn_revocacao": rn.get("revocacao"),
                "rn_brier": rn.get("brier"), "ma_cobertura": ma.get("cobertura_percentual"),
                "mo_saude": round(100 * st["funcionando"] / (st["funcionando"] + st["em_falha"])) if (st["funcionando"] + st["em_falha"]) else None,
                "es_livros": round(100 * ((rr.get("cruzamento") or {}).get("com_livro") or 0) / rr["abertas"]) if rr.get("abertas") else None}
    divergencias, sem_leitura, incoerentes = [], [], []
    for k, v in esperado.items():
        x = I.get(k)
        if not x:
            divergencias.append({"indicador": k, "problema": "não existe na sala"}); continue
        if v is not None and x.get("valor") is not None and abs(float(x["valor"]) - float(v)) > max(0.011, abs(float(v)) * 0.02):
            divergencias.append({"indicador": x.get("nome"), "sala": x.get("valor"), "fonte": v})
    for x in I.values():
        if x.get("valor") is None:
            sem_leitura.append(x.get("nome"))
        f = x.get("faixa") or {}; v = x.get("valor")
        if isinstance(v, (int, float)) and f:
            a = f.get("alarme") or [None, None]; nrm = f.get("normal") or [None, None]
            em_alarme = (a[0] is not None and v < a[0]) or (a[1] is not None and v > a[1])
            fora_normal = (nrm[0] is not None and v < nrm[0]) or (nrm[1] is not None and v > nrm[1])
            if em_alarme and x.get("estado") not in ("vermelho",) and "parado" not in str(x.get("motivo")):
                incoerentes.append(f"{x.get('nome')}: valor em alarme e estado {x.get('estado')}")
            elif not fora_normal and not em_alarme and x.get("estado") == "amarelo" and "registro de" not in str(x.get("motivo")):
                incoerentes.append(f"{x.get('nome')}: valor normal e estado amarelo")
    idade = _idade_h(sc.get("em"))
    faltam = []
    if not any("decis" in str(x.get("nome", "")).lower() for x in I.values()):
        faltam.append("decisões da titular (descartadas/inscritas aguardando aplicação e livros sinalizados para o Claude)")
    if not any("ficha" in str(x.get("nome", "")).lower() for x in I.values()):
        faltam.append("fichas das oportunidades (cobertura da janela de detalhe)")
    if not any("aliment" in str(x.get("nome", "")).lower() for x in I.values()):
        faltam.append("alimentação externa diária (enviada, itens, hash confirmado)")
    if not any("diagn" in str(x.get("nome", "")).lower() for x in I.values()):
        faltam.append("diagnóstico único (problemas por gravidade e índice de cumprimento da finalidade)")
    if not any("valida" in str(x.get("nome", "")).lower() for x in I.values()):
        faltam.append("percentual de oportunidades validadas (hoje só aparece o total de abertas)")
    for d in divergencias:
        _problema(P, "sala_diverge_da_fonte", "media", f"sala de controle: {d}", "refazer a sala de controle")
    for t in incoerentes:
        _problema(P, "sala_estado_incoerente", "baixa", f"sala de controle: {t}", "rever a regra do indicador (sem correção automática)")
    if idade is None or idade > 3:
        _problema(P, "sala_desatualizada", "media", f"sala de controle sem atualização há {idade} h", "refazer a sala de controle")
    return {"idade_h": idade, "indicadores": len(I), "divergencias": divergencias, "sem_leitura": sem_leitura,
            "estados_incoerentes": incoerentes, "sugestoes_de_apresentacao": faltam}


def diagnosticar() -> dict:
    hoje = date.today().isoformat(); P: list = []
    s = sistemas(P); o = oportunidades(P, hoje); i = integracao(P, o); e = execucao(P); sala = conferir_sala(P, s, o)
    fin = finalidade(s, o, i, e)
    # 15/10/2026 (titular): WORKFLOW da estrutura nova e DECISÕES do Eldorado em cada etapa (src/analise_ciclos.py)
    from . import analise_ciclos as AC
    try:
        wf = AC.workflow(P, _problema)
    except Exception as ex:  # noqa: BLE001
        wf = {"erro": f"{type(ex).__name__}: {str(ex)[:200]}"}
    try:
        dec = AC.decisoes(P, _problema)
    except Exception as ex:  # noqa: BLE001
        dec = [{"etapa": "erro", "decisao": "conferência das decisões", "regra": "", "conferidos": 0, "incorretos": 0,
                "veredito": f"não conferido: {type(ex).__name__}: {str(ex)[:160]}", "exemplos": []}]
    ordem = {"alta": 0, "media": 1, "baixa": 2}
    P.sort(key=lambda p: (ordem.get(p["gravidade"], 3), p["codigo"]))
    return {"em": datetime.now(timezone.utc).replace(microsecond=0).isoformat(), "finalidade": fin, "sistemas": s, "oportunidades": o, "integracao": i,
            "execucao": e, "sala_de_controle": sala, "workflow": wf, "decisoes": dec,
            "problemas": P, "contagem_problemas": dict(Counter(p["gravidade"] for p in P)),
            "corrigiveis": sorted({p["correcao"] for p in P if p["correcao"] and not any(t in p["correcao"] for t in ("sem correção", "investigar", "ver o", "retreinar"))})}


# ── correções, em sequência (uma etapa depois da outra) ─────────────────────────────────────────────────────────────
def _etapa(nome: str, fn, log: list) -> None:
    t = time.time()
    try:
        r = fn(); log.append({"etapa": nome, "ok": True, "segundos": round(time.time() - t, 1), "resultado": str(r)[:300]})
    except Exception as e:  # noqa: BLE001
        log.append({"etapa": nome, "ok": False, "segundos": round(time.time() - t, 1), "erro": f"{type(e).__name__}: {str(e)[:300]}"})


def corrigir(diag: dict) -> list:
    precisa = set(diag.get("corrigiveis") or [])
    if not precisa:
        return []
    log: list = []
    if "aplicar as decisões" in precisa:
        from . import decisoes_titular; _etapa("decisões da titular → livros e repositório", decisoes_titular.run, log)
    if precisa & {"criar/vincular livros", "criar/vincular livros e refazer o repositório"}:
        from . import opressores_repositorio; _etapa("livros: criar ou vincular para cada oportunidade", opressores_repositorio.sincronizar, log)
    from . import repositorio_unico
    _etapa("repositório único", lambda: repositorio_unico.construir(gravar=True), log)
    if precisa & {"refazer a tela", "refazer tela e indicadores", "refazer o repositório", "criar/vincular livros", "criar/vincular livros e refazer o repositório", "aplicar as decisões"}:
        from . import fluxo_oportunidades; _etapa("tela das oportunidades (fluxo completo)", fluxo_oportunidades.atualizar_mapa, log)
    from . import fichas_oportunidades, sala_controle, saude
    _etapa("fichas das oportunidades", fichas_oportunidades.run, log)
    _etapa("sala de controle", sala_controle.run, log)
    _etapa("saúde do sistema", saude.checar, log)
    return log


def resumo_md(antes: dict, depois: dict | None, log: list) -> str:
    d = depois or antes; o, s, i = d["oportunidades"], d["sistemas"], d["integracao"]
    L = [f"# Diagnóstico do sistema · {d['em'][:16].replace('T', ' ')} UTC", ""]
    if depois:
        L += [f"Correções aplicadas: {sum(1 for x in log if x['ok'])} de {len(log)} etapas · problemas antes {len(antes['problemas'])} → depois {len(depois['problemas'])}", ""]
        L += [f"- {'ok ' if x['ok'] else 'ERRO'} {x['etapa']} ({x['segundos']} s)" + ("" if x["ok"] else f" — {x['erro']}") for x in log] + [""]
    fz = d.get("finalidade") or {}
    L += [f"## Cumprimento da finalidade · índice geral {fz.get('indice_geral_pct')}%"] + \
         [f"- {x['sistema']}: {x['atingido_pct'] if x['atingido_pct'] is not None else '—'}% ({x['estado']}) — {x['finalidade']}" for x in fz.get("sistemas") or []] + [""]
    ex = d.get("execucao") or {}
    L += [f"## Execução · fluxos: {ex.get('resumo')}" + (" · SEM TOKEN: fluxos e falhas silenciosas não lidos" if ex.get("sem_token") else "")] + \
         [f"- {f['nome']}: {f['estado']} · última {str(f['ultima'] or '—')[:16]} · sucesso {f['sucesso_pct']}% · cadência {f['cadencia_h']} h"
          for f in ex.get("fluxos") or [] if f["estado"] not in ("ok", "manual")] + \
         [f"- falha silenciosa em {k}: " + " | ".join(v[:4]) for k, v in (ex.get("falhas_silenciosas") or {}).items()] + [""]
    sl = d.get("sala_de_controle") or {}
    L += [f"## Sala de controle · {sl.get('indicadores')} indicadores · atualizada há {sl.get('idade_h')} h",
          f"- divergências com a fonte: {sl.get('divergencias') or 'nenhuma'}", f"- sem leitura: {sl.get('sem_leitura') or 'nenhum'}",
          f"- estados incoerentes: {sl.get('estados_incoerentes') or 'nenhum'}", f"- sugestões de apresentação: {sl.get('sugestoes_de_apresentacao') or 'nenhuma'}", ""]
    L += ["## Oportunidades", f"- abertas: {o['abertas']} · validadas: {o['validadas']} ({o['percentual_validadas']}%) · por estado: {o['por_estado']}",
          f"- com livro: {o['com_livro']} · sem livro (problema): {o['sem_livro']} · sem livro por regra: {o['sem_livro_por_regra']} {o['sem_livro_por_regra_motivos']} · livro inexistente: {o['livro_inexistente']}",
          f"- sem site oficial: {o['sem_site_oficial']} · sem prazo: {o['sem_prazo']} · prazo vencido ainda aberta: {o['prazo_vencido']}",
          f"- fora da tela: {o['fora_da_tela']} · sem ficha: {o['sem_ficha']}", f"- itens que mais faltam: {o['itens_que_mais_faltam']}", "",
          "## Sistemas", f"- motores: {s['motores']['funcionando']} funcionando · {s['motores']['em_falha']} em falha · {s['motores']['inativos']} inativos · {len(s['motores']['leitura_parcial'])} com leitura parcial",
          *[f"  - em falha: {m['nome']} — {m['resultado']}" for m in s["motores"]["em_falha_lista"]],
          f"- maestro: cobertura {s['maestro'].get('cobertura_percentual')}% · esgotados {s['maestro'].get('esgotaram_tentativas')}",
          f"- rede neural: AUC {s['rede_neural']['validacao_cruzada'].get('auc')} · rotulados {s['rede_neural'].get('rotulados')} · treinada em {s['rede_neural'].get('modelo_treinado_em')}",
          f"- Cartório: {(s['cartorio'].get('resumo') or {}).get('pct_certificado_12')} certificado · fluxos do GitHub com falha: {s['fluxos_github']['com_falha']}",
          f"- saúde: {len(s['saude']['alertas'])} alerta(s) · índice da sala de controle: {s['sala_controle'].get('indice_saude')}", "",
          "## Integração", f"- contagens: {i['contagens']}", f"- idade (h): {i['idade_horas']}",
          f"- decisões da titular: {i['decisoes_da_titular']} · não aplicadas: {i['decisoes_nao_aplicadas']}", "",
          f"## Problemas ({len(d['problemas'])})"]
    L += [f"- [{p['gravidade']}] {p['texto']}" + (f" → {p['correcao']}" if p["correcao"] else "") for p in d["problemas"]]
    return "\n".join(L) + "\n"


def run(corrigir_: bool = False, ciclo_: bool = False) -> dict:
    anterior = _j(SAIDA, {})                         # 15/10: base do 1º ciclo de análise
    antes = diagnosticar(); log = []; depois = None
    if corrigir_:
        log = corrigir(antes)
        depois = diagnosticar() if log else None
    final = depois or antes
    res = {**final, "corrigido": bool(log), "correcoes": log, "antes": {"problemas": len(antes["problemas"]), "contagem": antes["contagem_problemas"]} if depois else None}
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    # 15/10/2026 (titular): CICLO DE ANÁLISE — janela desde a análise anterior, correções implantadas nela e comparação
    from . import analise_ciclos as AC
    ciclo = None
    if ciclo_:                                       # só o "Analise o sistema" (fluxo 36) abre um ciclo; o comando único não
        try:
            ciclo = AC.registrar_ciclo(final, log, _gh, anterior)
        except Exception as ex:  # noqa: BLE001
            print(f"ciclo de análise não registrado: {type(ex).__name__}: {ex}", file=sys.stderr)
    res["ciclo_de_analise"] = ciclo
    SAIDA.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    RESUMO.write_text(resumo_md(antes, depois, log) + "\n" + AC.resumo_md(final, ciclo), encoding="utf-8")
    return {"problemas": len(final["problemas"]), "por_gravidade": final["contagem_problemas"], "corrigido": bool(log),
            "abertas": final["oportunidades"]["abertas"], "sem_livro": final["oportunidades"]["sem_livro"]}


if __name__ == "__main__":
    print(json.dumps(run("--corrigir" in sys.argv, "--ciclo" in sys.argv), ensure_ascii=False))
