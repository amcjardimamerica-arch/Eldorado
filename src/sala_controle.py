"""SALA DE CONTROLE DA REDE NEURAL (titular, 11/10/2026) — docs/prompts/PROMPT-SALA-DE-CONTROLE-REDE-NEURAL-2026-10-11.md

Cada função da rede neural, do maestro e da esteira vira um INSTRUMENTO com quatro respostas: o que faz · quando foi
acionado · o que mudou (efeito) · como está (resultado, com faixa normal e faixa de alarme). Só dado real: cada
instrumento lê um registro do sistema; sem registro, "sem leitura". Estado:
  verde    acionado dentro da cadência e valor na faixa normal
  amarelo  valor fora da faixa normal, ou registro além da cadência (até 3×)
  vermelho valor em faixa de alarme, ou registro parado há mais de 3× a cadência
  cinza    sem leitura
Saídas: docs/dados/sala_controle.json (o painel) e estado/sala_controle_historico.json (as últimas 96 passagens).
Roda em toda passagem do fluxo 22 (agenda + maestro + rede neural), logo depois do maestro.
"""
from __future__ import annotations

import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAIDA = ROOT / "docs/dados/sala_controle.json"
HIST = ROOT / "estado/sala_controle_historico.json"
D = ROOT / "docs/dados"


def _j(p: Path, padrao=None):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao if padrao is not None else {}


def _horas(ts: str | None, agora: datetime) -> float | None:
    if not ts:
        return None
    try:
        t = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone.utc)
        return round((agora - t).total_seconds() / 3600, 2)
    except ValueError:
        return None


def _estado(idade: float | None, cad: float, valor, faixa: dict | None) -> tuple[str, str]:
    """(estado, motivo)."""
    if idade is None and valor is None:
        return "cinza", "sem leitura"
    if idade is not None and idade > 3 * cad:
        return "vermelho", f"parado há {idade:.0f} h (cadência {cad:g} h)"
    if faixa and isinstance(valor, (int, float)):
        a, n = faixa.get("alarme"), faixa.get("normal")
        if a and ((a[0] is not None and valor < a[0]) or (a[1] is not None and valor > a[1])):
            return "vermelho", "valor em faixa de alarme"
        if n and ((n[0] is not None and valor < n[0]) or (n[1] is not None and valor > n[1])):
            return "amarelo", "valor fora da faixa normal"
    if idade is not None and idade > cad:
        return "amarelo", f"registro de {idade:.0f} h (cadência {cad:g} h)"
    return "verde", "dentro da cadência e da faixa normal"


def _instr(lst: list, agora: datetime, **k):
    idade = _horas(k.get("quando"), agora)
    est, mot = _estado(idade, k.get("cadencia_h", 2), k.get("valor"), k.get("faixa"))
    lst.append({**k, "idade_h": idade, "estado": est, "motivo": mot})


def _fluxos(agora: datetime) -> list[dict]:
    """Última execução de cada fluxo do GitHub Actions (quando há token no ambiente)."""
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    rep = os.environ.get("GITHUB_REPOSITORY", "amcjardimamerica-arch/Eldorado")
    if not tok:
        return []
    try:
        req = urllib.request.Request(f"https://api.github.com/repos/{rep}/actions/runs?per_page=100",
                                     headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"})
        runs = json.loads(urllib.request.urlopen(req, timeout=20).read()).get("workflow_runs") or []
    except Exception:  # noqa: BLE001
        return []
    por_nome: dict[str, list] = {}
    for r in runs:
        por_nome.setdefault(r.get("name"), []).append(r)
    out = []
    for nome, L in por_nome.items():
        r = L[0]
        out.append({"nome": nome, "quando": r.get("created_at"), "situacao": r.get("status"), "conclusao": r.get("conclusion"),
                    "idade_h": _horas(r.get("created_at"), agora), "url": r.get("html_url"), "evento": r.get("event"),
                    "duracao_min": round((datetime.fromisoformat(r["updated_at"].replace("Z", "+00:00")) - datetime.fromisoformat(r["created_at"].replace("Z", "+00:00"))).total_seconds() / 60, 1)
                                   if r.get("updated_at") and r.get("created_at") else None,
                    "ultimas": [{"quando": x.get("created_at"), "situacao": x.get("status"), "conclusao": x.get("conclusion"), "url": x.get("html_url")} for x in L[:6]]})
    return sorted(out, key=lambda x: x["nome"] or "")


def montar(agora: datetime | None = None) -> dict:
    agora = agora or datetime.now(timezone.utc)
    rn, ma = _j(D / "rede_neural.json"), _j(D / "maestro.json")
    st, li = _j(D / "status_motores.json"), _j(D / "linha_producao.json")
    rp, ca = _j(D / "repositorio_resumo.json"), _j(D / "cartorio.json")
    it, es = _j(D / "interceptador.json"), _j(D / "espiao_avaliacao.json")
    pi, al = _j(D / "piloto.json"), _j(D / "alerta_motores.json")
    op, us = _j(ROOT / "estado/opressores.json"), _j(D / "uso_arquivos.json")
    ei = _j(ROOT / "biblioteca_alexandria/empresas/indice.json")
    _fr = _j(ROOT / "biblioteca_alexandria/arquivo_frio/manifesto.json", [])
    fr = _fr if isinstance(_fr, list) else (_fr.get("pacotes") or _fr.get("conjuntos") or [])
    esg = ma.get("esgotaram_tentativas"); n_esg = len(esg) if isinstance(esg, list) else esg
    vc = rn.get("validacao_cruzada") or {}
    I: list[dict] = []

    # ── NÚCLEO · rede neural
    _instr(I, agora, id="rn_auc", sub="Núcleo · rede neural", nome="Discernimento (AUC)", valor=vc.get("auc"), unidade="", escala=[0.5, 1],
           faixa={"normal": [0.8, None], "alarme": [0.7, None]}, quando=rn.get("em"), cadencia_h=2,
           faz="Separa oportunidade real de ruído; 1 é perfeito, 0,5 é sorte.",
           efeito=f"{rn.get('rotulados', 0)} decisões humanas e do Chrome usadas para aprender ({rn.get('positivos', 0)} oportunidades reais)",
           resultado=f"AUC {vc.get('auc')} em validação cruzada de 5 partes")
    _instr(I, agora, id="rn_precisao", sub="Núcleo · rede neural", nome="Precisão", valor=vc.get("precisao"), unidade="", escala=[0, 1],
           faixa={"normal": [0.7, None], "alarme": [0.5, None]}, quando=rn.get("em"), cadencia_h=2,
           faz="Das que a rede aponta como reais, quantas são reais.", efeito="ordena a fila de validação e dá a nota dos livros",
           resultado=f"precisão {vc.get('precisao')}")
    _instr(I, agora, id="rn_revocacao", sub="Núcleo · rede neural", nome="Revocação", valor=vc.get("revocacao"), unidade="", escala=[0, 1],
           faixa={"normal": [0.6, None], "alarme": [0.4, None]}, quando=rn.get("em"), cadencia_h=2,
           faz="Das oportunidades reais, quantas a rede encontra.", efeito="evita que oportunidade boa fique no fim da fila",
           resultado=f"revocação {vc.get('revocacao')}")
    _instr(I, agora, id="rn_brier", sub="Núcleo · rede neural", nome="Erro de calibração (Brier)", valor=vc.get("brier"), unidade="", escala=[0, 0.5],
           faixa={"normal": [None, 0.2], "alarme": [None, 0.3]}, quando=rn.get("em"), cadencia_h=2,
           faz="Quão bem a nota (0–1) corresponde à realidade; quanto menor, melhor.", efeito="a nota da rede vira prioridade no Cartório",
           resultado=f"Brier {vc.get('brier')}")
    idade_modelo = _horas(rn.get("modelo_treinado_em"), agora)
    _instr(I, agora, id="rn_treino", sub="Núcleo · rede neural", nome="Idade do modelo", valor=round(idade_modelo / 24, 1) if idade_modelo is not None else None,
           unidade="dias", escala=[0, 14], faixa={"normal": [None, 7], "alarme": [None, 10]}, quando=rn.get("modelo_treinado_em"), cadencia_h=24 * 7,
           faz="Retreina quando há 5% mais decisões ou passou uma semana.", efeito=f"modelo treinado em {str(rn.get('modelo_treinado_em'))[:16]}",
           resultado=f"{rn.get('pendentes_provaveis_reais', 0)} pendentes prováveis reais · fila de validação {len(rn['fila_de_validacao']) if isinstance(rn.get('fila_de_validacao'), list) else rn.get('fila_de_validacao', 0)}")

    # ── REGÊNCIA · maestro
    cob = ma.get("cobertura") or {}
    _instr(I, agora, id="ma_cobertura", sub="Regência · maestro", nome="Cobertura do dia", valor=ma.get("cobertura_percentual"), unidade="%", escala=[0, 100],
           faixa={"normal": [60, None], "alarme": [30, None]}, quando=ma.get("em"), cadencia_h=2,
           faz="Planeja quais motores rodam hoje e mede se leram o dia inteiro.",
           efeito=f"{ma.get('planejados', 0)} motores planejados · {len(ma['a_disparar']) if isinstance(ma.get('a_disparar'), list) else ma.get('a_disparar', 0)} a disparar de novo",
           resultado=f"completos {cob.get('completa', 0)} · parciais {cob.get('parcial', 0)} · aguardando horário {cob.get('aguardando_horario', 0)} · coleta local {cob.get('pendente_local', 0)}")
    _instr(I, agora, id="ma_esgotados", sub="Regência · maestro", nome="Motores sem leitura completa após 3 tentativas", valor=n_esg,
           unidade="motores", escala=[0, max(10, (ma.get("planejados") or 0) // 2)], faixa={"normal": [None, 10], "alarme": [None, 30]}, quando=ma.get("em"), cadencia_h=2,
           faz="Dispara de novo pendentes e parciais, até 3 vezes por dia.", efeito="o que esgota fica registrado para correção do motor",
           resultado=f"{n_esg or 0} esgotaram · dia {'fechado' if ma.get('dia_fechado') else 'aberto'}" + (f": {', '.join(esg[:8])}…" if isinstance(esg, list) and esg else ""))

    # ── MOTORES · status
    cg = st.get("contagem") or {}
    tot_m = (cg.get("verde") or 0) + (cg.get("vermelho") or 0)
    _instr(I, agora, id="mo_saude", sub="Motores", nome="Motores funcionando", valor=round(100 * (cg.get("verde") or 0) / tot_m) if tot_m else None,
           unidade="%", escala=[0, 100], faixa={"normal": [85, None], "alarme": [60, None]}, quando=st.get("gerado_em"), cadencia_h=6,
           faz="Confere se cada motor leu nas últimas 26 horas.", efeito=f"{cg.get('verde', 0)} funcionando · {cg.get('vermelho', 0)} em falha",
           resultado=", ".join(m.get("nome") or m.get("id") for m in (st.get("motores") or []) if m.get("luz") == "vermelho")[:300] or "nenhum em falha")
    _instr(I, agora, id="mo_cadencia", sub="Motores", nome="Motores regulares fora da cadência", valor=al.get("em_alerta"), unidade="motores", escala=[0, 10],
           faixa={"normal": [None, 2], "alarme": [None, 5]}, quando=al.get("em"), cadencia_h=26,
           faz="Todo motor regular tem de ler dentro da sua cadência.", efeito=f"{al.get('funcionando', 0)} de {al.get('total', 0)} dentro da cadência",
           resultado=", ".join(str(a.get("motor") or a.get("id") or a) for a in (al.get("alertas") or []))[:300] or "nenhum alerta")

    # ── ESTEIRA · coleta, repositório, livros
    fu = li.get("funil") or {}
    _instr(I, agora, id="es_coleta", sub="Esteira", nome="Coletado pelos motores", valor=fu.get("coletados"), unidade="registros", escala=None, quando=li.get("em"), cadencia_h=2,
           faz="Junta tudo o que os motores e Pilotos trouxeram e separa as oportunidades distintas.",
           efeito=f"{fu.get('oportunidades_distintas', 0)} oportunidades distintas · {fu.get('entidades_em_2_ou_mais_canais', 0)} vistas em 2+ canais",
           resultado=" · ".join(f"{k.lower()} {v}" for k, v in (fu.get("etapas") or {}).items()))
    _instr(I, agora, id="es_abertas", sub="Esteira", nome="Oportunidades abertas", valor=rp.get("abertas"), unidade="abertas", escala=None, quando=rp.get("em"), cadencia_h=2,
           faz="O repositório único: um registro por oportunidade, a mesma contagem em todas as telas.",
           efeito=f"validadas {rp.get('validadas', 0)} · em verificação {rp.get('em_verificacao', 0)} · validação manual {rp.get('validacao_manual', 0)}",
           resultado=f"arquivadas (municipais de fora de GO, 11/10) {rp.get('arquivadas_municipais_fora_de_goias', 0)} · prontas para o Farol {rp.get('prontas_para_o_farol', 0)}")
    cz = rp.get("cruzamento") or {}
    pct_livro = round(100 * (cz.get("com_livro") or 0) / rp["abertas"]) if rp.get("abertas") else None
    _instr(I, agora, id="es_livros", sub="Esteira", nome="Abertas com livro na Biblioteca", valor=pct_livro, unidade="%", escala=[0, 100],
           faixa={"normal": [85, None], "alarme": [60, None]}, quando=rp.get("em"), cadencia_h=2,
           faz="Cada oportunidade aberta ganha um livro (criado ou vinculado) que guia a busca.",
           efeito=f"{cz.get('com_livro', 0)} com livro · {cz.get('com_livro_de_editais_anteriores', 0)} com editais anteriores",
           resultado=f"{cz.get('em_verificacao_com_onde_buscar_do_livro', 0)} em verificação já sabem onde buscar pelo livro")
    mon = op.get("monitoramento") or {}
    _instr(I, agora, id="es_vigilancia", sub="Esteira", nome="Livros vigiados pelo próprio motor", valor=len(op.get("ligados") or {}) or None, unidade="livros", escala=None,
           quando=mon.get("em") or None, cadencia_h=26,
           faz="Liga o livro com edital aberto, prestes a abrir ou de fluxo contínuo, com pesquisa focada.",
           efeito=(f"abertos {mon.get('abertos')} · prestes a abrir {mon.get('prestes_a_abrir')} · contínuos {mon.get('fluxo_continuo')}" if mon
                   else "o resumo da regra de 11/10 ainda não foi gravado"),
           resultado=f"{len(op.get('ligados') or {})} livros ligados")

    # ── CERTIFICAÇÃO · Cartório
    rs = ca.get("resumo") or {}
    _instr(I, agora, id="ca_12", sub="Certificação", nome="Itens certificados na fonte oficial", valor=round(100 * (rs.get("pct_certificado_12") or 0)) if rs else None,
           unidade="%", escala=[0, 100], faixa={"normal": [60, None], "alarme": [30, None]}, quando=ca.get("em"), cadencia_h=3,
           faz="Acha o documento oficial e certifica cada um dos 12 itens com trecho e página.",
           efeito=f"{rs.get('certidoes_12_de_12', 0)} certidões completas (12 de 12) · {rs.get('certidoes_sem_item_faltando', 0)} sem item faltando",
           resultado=f"certificados {rs.get('pontos_certificados', 0)} · dispensados {rs.get('pontos_dispensados', 0)} · faltam {rs.get('pontos_faltam', 0)}")

    # ── PILOTOS
    _instr(I, agora, id="pi_interceptador", sub="Pilotos", nome="Interceptador", valor=rp.get("fila_interceptador"), unidade="na fila", escala=None,
           quando=it.get("ultimo_voo") or it.get("em"), cadencia_h=2,
           faz="Pesquisa na web o que o Cartório não alcança, guiado pelo banco.",
           efeito=f"estado: {it.get('estado') or '—'} · modelo {it.get('modelo') or '—'}",
           resultado=json.dumps(it.get("contagem") or {}, ensure_ascii=False)[:200])
    _instr(I, agora, id="pi_espiao", sub="Pilotos", nome="Espião", valor=es.get("empresas_novas"), unidade="empresas novas", escala=None, quando=es.get("em"), cadencia_h=3,
           faz="Descobre editais de empresas e chamadas internacionais; alimenta o banco de empresas.",
           efeito=f"{es.get('voos', 0)} voos · {es.get('candidatas_privadas_internacionais', 0)} candidatas privadas e internacionais",
           resultado=f"próxima avaliação em {es.get('proxima_avaliacao_em_voos', '—')} voos")
    _instr(I, agora, id="pi_piloto", sub="Pilotos", nome="Piloto (voos do dia)", valor=pi.get("voo_do_dia"), unidade="voos", escala=None, quando=pi.get("em"), cadencia_h=3,
           faz="Voa as missões do dia com a IA local e registra o que aprendeu.", efeito=f"abates {pi.get('abates', 0)} · propostas {pi.get('propostas', 0)}",
           resultado=f"ocupante {pi.get('ocupante') or '—'}")

    # ── EMPRESAS e HIGIENE
    tt = ei.get("totais") or {}
    _instr(I, agora, id="em_rankings", sub="Empresas", nome="Rankings de empresas", valor=sum(v for v in tt.values() if isinstance(v, int)) or None, unidade="empresas",
           escala=None, quando=ei.get("gerado_em"), cadencia_h=26, faz="Destinação tributária e doação/patrocínio, refeitos todo dia.",
           efeito=" · ".join(f"{k.replace('_', ' ')} {v}" for k, v in tt.items()), resultado="lista de doação e patrocínio alimentada pelo Espião e por chamamentos")
    _instr(I, agora, id="hi_uso", sub="Higiene", nome="Arquivos sem uso há 30 dias", valor=us.get("alertas"), unidade="arquivos", escala=[0, 50],
           faixa={"normal": [None, 0], "alarme": [None, 50]}, quando=us.get("em"), cadencia_h=26,
           faz="Mede o uso dos arquivos (fora o banco de dados) e alerta o que não é usado.",
           efeito=f"{us.get('monitorados', 0)} arquivos medidos · {us.get('nao_citados_dentro_do_prazo', 0)} não citados, dentro do prazo",
           resultado=f"{us.get('mb_em_alerta', 0)} MB em alerta")
    _instr(I, agora, id="hi_frio", sub="Higiene", nome="Pacotes no arquivo frio", valor=len(fr) or None, unidade="pacotes", escala=None,
           quando=(fr[-1].get("criado_em") or fr[-1].get("em") or None) if fr else None, cadencia_h=24 * 8,
           faz="Guarda sem perda, fora do repositório, o que é grande e de uso esporádico.",
           efeito=f"{sum(int(x.get('arquivos') or 0) for x in fr)} arquivos guardados",
           resultado=f"{sum(int(x.get('bytes_originais') or 0) for x in fr) // 1048576} MB fora do repositório")

    # ── índice de saúde, anunciadores, mímico, linha do tempo
    peso = {"verde": 100, "amarelo": 60, "vermelho": 15}
    validos = [x for x in I if x["estado"] in peso]
    indice = round(sum(peso[x["estado"]] for x in validos) / len(validos)) if validos else None
    anunc = [{"id": x["id"], "nome": x["nome"], "sub": x["sub"], "nivel": x["estado"], "motivo": x["motivo"]} for x in I if x["estado"] in ("amarelo", "vermelho", "cinza")]
    if not mon:
        anunc.append({"id": "es_vigilancia_resumo", "nome": "Resumo da vigilância dos livros ausente", "sub": "Esteira", "nivel": "amarelo",
                      "motivo": "a regra de fontes monitoradas (11/10) ainda não gravou abertos, prestes a abrir e contínuos"})
    fluxos = _fluxos(agora)
    for f in fluxos:
        if f.get("conclusao") == "failure":
            anunc.append({"id": f"fl_{f['nome']}", "nome": f"Fluxo com falha: {f['nome']}", "sub": "Fluxos", "nivel": "vermelho", "motivo": f"última execução falhou ({str(f['quando'])[:16]})"})
    mimico = [{"etapa": "Coleta", "valor": fu.get("coletados")}, {"etapa": "Distintas", "valor": fu.get("oportunidades_distintas")},
              {"etapa": "Abertas", "valor": rp.get("abertas")}, {"etapa": "Com livro", "valor": cz.get("com_livro")},
              {"etapa": "Cartório", "valor": rs.get("certidoes_sem_item_faltando")}, {"etapa": "Interceptador", "valor": rp.get("fila_interceptador")},
              {"etapa": "Verificação externa", "valor": rp.get("fila_busca_externa")}, {"etapa": "Prontas para o Farol", "valor": rp.get("prontas_para_o_farol")}]
    tempo = sorted(({"id": x["id"], "quando": x["quando"], "nome": x["nome"], "sub": x["sub"], "estado": x["estado"], "efeito": x.get("efeito"), "resultado": x.get("resultado")}
                    for x in I if x.get("quando")), key=lambda e: str(e["quando"]), reverse=True)
    # 11/10 (v3, constelação): o detalhe de cada etapa — cada motor vira uma estrela no fundo da página
    detalhes = {
        "motores": [{"id": m.get("id"), "nome": m.get("nome"), "luz": m.get("luz"), "ultima_leitura": m.get("ultima_leitura"),
                     "resultado": m.get("resultado_do_dia") or m.get("resultado")} for m in (st.get("motores") or [])],
        "maestro": [{"motor": x.get("motor"), "prioridade": x.get("prioridade"), "diagnostico": x.get("diagnostico"), "cobertura": x.get("cobertura"),
                     "tentativas": x.get("tentativas_hoje"), "coleta": x.get("coleta"), "abertura_proxima": x.get("livros_com_abertura_proxima")}
                    for x in (ma.get("plano") or [])][:160],
        "cartorio_itens": ca.get("por_item") or {},
        "reprocessar": (fu.get("fila_de_reprocessamento") or {}),
        "proximo_passo": rp.get("proximo_passo") or {}, "por_etapa": rp.get("por_etapa") or {}, "estantes": rp.get("estantes") or {},
        "por_origem": rp.get("por_origem") or {},
        "interceptador_fila": it.get("fila") or {},
        "interceptador_missoes": [{"em": m.get("em"), "alvo": str(m.get("alvo") or "")[:140], "modo": m.get("modo"), "resultado": str(m.get("resultado") or m.get("qualidade") or "")[:140]}
                                  for m in (it.get("missoes") or [])[:10]],
        "espiao_familias": {k: {"usos": v.get("usos"), "achados": v.get("achados"), "empresas": v.get("empresas")} for k, v in (es.get("familias") or {}).items()},
        "espiao_modalidades": es.get("empresas_por_modalidade") or {},
    }
    res = {"em": agora.replace(microsecond=0).isoformat(), "regra": __doc__.split("\n")[0], "indice_saude": indice, "detalhes": detalhes,
           "contagem": {e: sum(1 for x in I if x["estado"] == e) for e in ("verde", "amarelo", "vermelho", "cinza")},
           "instrumentos": I, "anunciadores": anunc, "mimico": mimico, "linha_do_tempo": tempo[:40], "fluxos": fluxos}
    return res


def run() -> dict:
    res = montar()
    h = _j(HIST, {"passagens": []})
    h["passagens"] = (h.get("passagens") or [])[-95:] + [{"em": res["em"], "indice": res["indice_saude"],
                                                           "v": {x["id"]: x["valor"] for x in res["instrumentos"] if isinstance(x.get("valor"), (int, float))}}]
    HIST.parent.mkdir(parents=True, exist_ok=True)
    HIST.write_text(json.dumps(h, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    res["historico"] = h["passagens"]
    SAIDA.write_text(json.dumps(res, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {"indice_saude": res["indice_saude"], "contagem": res["contagem"], "anunciadores": len(res["anunciadores"]), "instrumentos": len(res["instrumentos"])}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=1))
