"""Resumo humano da execução (para GITHUB_STEP_SUMMARY) + decisão de alerta.

O sistema não pode falhar em silêncio: quando mais da metade das fontes falha,
quando três execuções seguidas não trazem nenhuma novidade, ou quando uma
etapa inteira quebra, este módulo grava estado/alerta.json — e o workflow abre
uma issue com o conteúdo."""
from __future__ import annotations

import json

from .nucleo import ROOT, load_json, now_iso, write_json

def _ler(caminho: str) -> dict:
    p = ROOT / caminho
    return load_json(p) if p.exists() else {}

def run() -> dict:
    coleta = _ler("estado/ultima_execucao.json")
    apis = _ler("estado/ultima_coleta_api.json")
    capilar = _ler("estado/ultima_capilaridade.json")
    assistida = _ler("estado/ultima_verificacao_assistida.json")
    farol_ia = _ler("estado/ultimo_farol_ia.json")
    diario = _ler("estado/ultima_execucao_diaria.json")
    novas = int(coleta.get("novas", 0)) + int(apis.get("novas", 0))
    streak = _ler("estado/streak_sem_novidades.json")
    seguidas = 0 if novas > 0 else int(streak.get("execucoes_seguidas", 0)) + 1
    write_json(ROOT / "estado/streak_sem_novidades.json", {"execucoes_seguidas": seguidas, "atualizado_em": now_iso()})

    total = int(coleta.get("fontes_total", 0)); falhas = int(coleta.get("fontes_falha", 0))
    etapas_com_erro = [nome for nome, r in (diario.get("etapas") or {}).items() if isinstance(r, dict) and r.get("erro")]
    motivos = []
    if total and falhas * 2 > total:
        motivos.append(f"{falhas} de {total} fontes automáticas falharam nesta varredura.")
    if seguidas >= 3:
        motivos.append(f"{seguidas} execuções seguidas sem nenhuma oportunidade nova — verificar fontes e filtros.")
    if etapas_com_erro:
        motivos.append("Etapas com erro na execução: " + ", ".join(etapas_com_erro) + ".")

    linhas = ["# Eldorado — resumo da execução", "",
              f"- Fontes automáticas: **{coleta.get('fontes_ok', 0)}/{total}** ok · {falhas} falhas · {coleta.get('fontes_fora_escopo', 0)} fora do escopo · {coleta.get('fontes_api', 0)} via API",
              f"- Oportunidades novas: **{novas}** (varredura {coleta.get('novas', 0)} + APIs {apis.get('novas', 0)}) · atualizadas: {coleta.get('atualizadas', 0)} · quarentena: {coleta.get('quarentena', 0)}",
              f"- Capilaridade (pistas de imprensa): {capilar.get('pistas_novas', '–')} novas em {capilar.get('consultas', '–')} consultas",
              f"- Verificação assistida: {assistida.get('promovidas', '–')} promovidas de {assistida.get('avaliadas', '–')} avaliadas",
              f"- Farol IA: {farol_ia.get('casos_processados', 0)} caso(s) — {farol_ia.get('com_documentos', 0)} com documentos, {farol_ia.get('sem_chances', 0)} sem chances"
              + (f" · **{farol_ia['status']}**" if farol_ia.get("status") else ""), ""]
    if motivos:
        linhas += ["## ⚠ Atenção", *[f"- {m}" for m in motivos], ""]
    resumo = "\n".join(linhas)

    if motivos:
        write_json(ROOT / "estado/alerta.json", {"abrir_issue": True, "titulo": f"Alerta de operação — {now_iso()[:10]}",
                                                 "corpo": resumo, "gerado_em": now_iso()})
    else:
        alerta = ROOT / "estado/alerta.json"
        if alerta.exists(): write_json(alerta, {"abrir_issue": False, "gerado_em": now_iso()})
    print(resumo)
    return {"alerta": bool(motivos), "novas": novas, "streak_sem_novidades": seguidas}

if __name__ == "__main__":
    run()
