#!/usr/bin/env python3
"""TRILHA DO CARGO — cada regra que o titular fixou vira uma prova cronometrada.

O benchmark de 21/09 mediu se o modelo classificava editais. Era pouco: o cargo não é
classificar, é **voar segundo as regras**. Esta trilha põe cada candidato a percorrer as
regras que já estão em vigor, uma a uma, e mede duas coisas em cada etapa:

    VELOCIDADE     quanto tempo levou para responder
    ASSERTIVIDADE  respondeu no formato pedido, e a resposta estava certa

As duas contam, e contam junto: um modelo rápido que erra faz o voo sair torto depressa; um
modelo certeiro que demora estoura o teto de 26 minutos e o voo pousa sem terminar.

As oito provas, na ordem em que o voo as encontra:

    1  BRIEFING          devolve JSON com rumo, pergunta e nível?
    2  PNCP FORA         reconhece que compras públicas não é trabalho dele?
    3  UMA ÚNICA VEZ     entende que edital tentado não volta à fila?
    4  RECONHECIMENTO    formula consulta que leva a página de entidade, não a edital?
    5  QUEM PAGOU        lê o financiador e a via no texto de uma página?
    6  NÃO INVENTA       diante de página sem prazo, devolve null em vez de data?
    7  REINÍCIO          ao pousar, chama o próximo em 3 segundos?
    8  APRENDE           erra uma vez, avisado, não repete?

Eliminatórias: inventar prazo (prova 6) e não reiniciar (prova 7). As duas derrubam o
candidato por melhor que vá no resto — a primeira suja a Biblioteca com data falsa, a segunda
quebra a corrente de voos.

Modo de execução:

    --real      fala com um llama-server já de pé (exige modelo local)
    padrão      banco de provas com substitutos de comportamento declarado, para validar a
                própria trilha antes de gastar runner
"""
from __future__ import annotations

import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

SAIDA = RAIZ / "estado/piloto/trilha_do_cargo.json"

# Teto de tempo por pergunta. Acima disso o voo de 26 min não fecha as 14 missões.
TETO_S = 12.0
ALVO_S = 4.0          # acima disto já preocupa


PROVAS = [
    {"id": "briefing", "peso": 15, "eliminatoria": False,
     "o_que_mede": "devolve o JSON do briefing, com rumo, pergunta e nível",
     "porque": "sem isto o voo sai sem direção — é o que acontece hoje em 88% dos voos",
     "pergunta": ("Você é o Piloto da Biblioteca de Alexandria, prestes a decolar. "
                  "O acervo tem 436 editais, quase todos de compras públicas. "
                  "Responda SÓ com JSON, sem texto antes ou depois."),
     "esquema": '{"diagnostico":"...","aposta":{"onde":"...","porque":"...","confianca":"alta|media|baixa"},'
                '"pergunta_de_pesquisa":"...","nivel":"local|regional|nacional"}',
     "corrige": lambda r: (isinstance(r, dict) and bool(r.get("pergunta_de_pesquisa"))
                           and isinstance(r.get("aposta"), dict) and bool(r["aposta"].get("onde"))
                           and r.get("nivel") in ("local", "regional", "nacional"))},

    {"id": "pncp_fora", "peso": 12, "eliminatoria": False,
     "o_que_mede": "sabe que PNCP não é trabalho do Piloto",
     "porque": "ele passou dois dias inteiros numa fila 100% PNCP",
     "pergunta": ("REGRA DO CARGO: o Piloto NÃO analisa PNCP nem portais de compras públicas — "
                  "isso é dado genérico, analisado por fora. Classifique cada item como "
                  "'do_piloto' ou 'do_claude'.\\n"
                  "1) [Portal de Compras Públicas] - Credenciamento de empresa\\n"
                  "2) Edital de fomento cultural da Secult-GO\\n"
                  "3) pncp.gov.br/app/editais/9912\\n"
                  "4) Chamamento do Instituto MOL para projetos sociais\\n"
                  "Responda SÓ com JSON."),
     "esquema": '{"1":"do_piloto|do_claude","2":"...","3":"...","4":"..."}',
     "corrige": lambda r: (isinstance(r, dict) and r.get("1") == "do_claude"
                           and r.get("2") == "do_piloto" and r.get("3") == "do_claude"
                           and r.get("4") == "do_piloto")},

    {"id": "uma_vez", "peso": 8, "eliminatoria": False,
     "o_que_mede": "entende que edital tentado não volta à fila",
     "porque": "a regra de 3 tentativas fazia o Piloto martelar o mesmo alvo insolúvel",
     "pergunta": ("REGRA DO CARGO: cada edital é analisado UMA ÚNICA VEZ. Se o Piloto não achar "
                  "a página oficial, o edital passa ao Claude em vez de voltar à fila.\\n"
                  "O edital 'Chamamento 12/2026' foi analisado, a página não foi encontrada. "
                  "O que acontece com ele? Responda SÓ com JSON."),
     "esquema": '{"destino":"volta_a_fila|passa_ao_claude","porque":"..."}',
     "corrige": lambda r: isinstance(r, dict) and r.get("destino") == "passa_ao_claude"},

    {"id": "reconhecimento", "peso": 15, "eliminatoria": False,
     "o_que_mede": "formula consulta que leva a ENTIDADE ou MATÉRIA, não a edital",
     "porque": "a missão 2 procura o que já aconteceu, não o que está aberto",
     "pergunta": ("MISSÃO DE RECONHECIMENTO: procuro atividade do terceiro setor que JÁ "
                  "ACONTECEU e quem pagou por ela — patrocínio, doação, incentivo fiscal. "
                  "NÃO procuro edital aberto. Escreva 2 consultas de busca. Responda SÓ com JSON."),
     "esquema": '{"consultas":["...","..."]}',
     "corrige": lambda r: (isinstance(r, dict) and isinstance(r.get("consultas"), list)
                           and len(r["consultas"]) >= 2
                           and all(isinstance(c, str) and len(c) > 8 for c in r["consultas"][:2])
                           # não pode virar caça a edital: é o erro que a missão 2 existe para evitar
                           and not any(p in " ".join(r["consultas"]).lower()
                                       for p in ("edital aberto", "inscrições abertas", "pncp",
                                                 "licitação", "chamamento público aberto")))},

    {"id": "quem_pagou", "peso": 18, "eliminatoria": False,
     "o_que_mede": "lê o financiador e a via no texto da página",
     "porque": "é o produto da missão 2: nome + via, e a via diz por qual porta pedir",
     "pergunta": ("Leia e diga QUEM FINANCIOU e POR QUAL VIA.\\n\\n"
                  "TEXTO: 'A oficina teve patrocínio da Agroluz Alimentos. A reforma da quadra "
                  "foi viabilizada pelo Instituto Bandeirante, com recursos da Lei de Incentivo "
                  "ao Esporte.'\\n\\nVias possíveis: patrocinio, doacao, incentivo_fiscal, "
                  "marketing_social, convenio. Responda SÓ com JSON."),
     "esquema": '{"financiadores":[{"empresa":"...","via":"..."}]}',
     "corrige": lambda r: (isinstance(r, dict) and isinstance(r.get("financiadores"), list)
                           and len(r["financiadores"]) >= 2
                           and any(("agroluz" in str(f.get("empresa", "")).lower()
                                    and f.get("via") == "patrocinio") for f in r["financiadores"])
                           and any(("bandeirante" in str(f.get("empresa", "")).lower()
                                    and f.get("via") == "incentivo_fiscal") for f in r["financiadores"]))},

    {"id": "nao_inventa", "peso": 20, "eliminatoria": True,
     "o_que_mede": "diante de página sem prazo, devolve null em vez de inventar data",
     "porque": "prazo inventado suja a Biblioteca e faz perder edital de verdade — elimina",
     "pergunta": ("Leia a página e extraia o prazo. Se a data NÃO estiver escrita no texto, "
                  "devolva null. NUNCA invente, estime ou deduza uma data.\\n\\n"
                  "TEXTO: 'O Instituto Semear apoia projetos de educação em fluxo contínuo. "
                  "As propostas podem ser enviadas pelo formulário do site. Não há data limite "
                  "divulgada.'\\n\\nResponda SÓ com JSON."),
     "esquema": '{"prazo": null, "trecho_que_prova": "frase literal ou null"}',
     "corrige": lambda r: isinstance(r, dict) and r.get("prazo") in (None, "null", "")},

    {"id": "reinicio", "peso": 7, "eliminatoria": True,
     "o_que_mede": "sabe que ao pousar chama o próximo voo em 3 segundos",
     "porque": "sem reencadear, a corrente para e o motor fica parado — elimina",
     "pergunta": ("REGRA DO CARGO: ao pousar, o Piloto espera 3 segundos e chama o próximo voo. "
                  "Nunca dois no ar. O voo 15 acabou de pousar às 14h02. O que acontece agora? "
                  "Responda SÓ com JSON."),
     "esquema": '{"acao":"chamar_proximo|aguardar_cron|encerrar","segundos":3}',
     "corrige": lambda r: (isinstance(r, dict) and r.get("acao") == "chamar_proximo"
                           and int(r.get("segundos") or 0) == 3)},

    {"id": "aprende", "peso": 5, "eliminatoria": False,
     "o_que_mede": "avisado do erro, não repete",
     "porque": "sem isto o aprendizado é decorativo: o sistema anota e o modelo ignora",
     "pergunta": ("No voo anterior você respondeu que o edital de compras públicas do PNCP era "
                  "'do_piloto'. ISSO ESTAVA ERRADO: PNCP é do Claude, sempre.\\n"
                  "Agora classifique: 'pncp.gov.br/app/editais/7788 — pregão eletrônico'. "
                  "Responda SÓ com JSON."),
     "esquema": '{"destino":"do_piloto|do_claude"}',
     "corrige": lambda r: isinstance(r, dict) and r.get("destino") == "do_claude"},
]


class Substituto:
    """Candidato de banco, com comportamento DECLARADO. Serve para validar a trilha — não
    substitui a medição real, que precisa do modelo de pé."""

    def __init__(self, nome: str, responde: float, acerta: float, s_medio: float,
                 inventa_prazo: bool = False, semente: int = 0, nota: str = ""):
        self.nome, self.responde, self.acerta = nome, responde, acerta
        self.s_medio, self.inventa_prazo, self.nota = s_medio, inventa_prazo, nota
        self.r = random.Random(semente)

    def perguntar(self, prova: dict) -> tuple[dict | None, float]:
        dt = max(0.2, self.r.gauss(self.s_medio, self.s_medio * 0.3))
        time.sleep(min(dt, 0.05))                      # o banco não dorme o tempo real
        if self.r.random() > self.responde:
            return None, dt
        if prova["id"] == "nao_inventa" and self.inventa_prazo:
            return {"prazo": "2026-12-31", "trecho_que_prova": "propostas em fluxo contínuo"}, dt
        if self.r.random() > self.acerta:
            return _errado(prova["id"]), dt
        return _certo(prova["id"]), dt


def _certo(pid: str):
    return {
        "briefing": {"diagnostico": "acervo é quase todo compra pública",
                     "aposta": {"onde": "apoiador_no_rodape", "porque": "rastro fora do alcance dos motores",
                                "confianca": "media"},
                     "pergunta_de_pesquisa": "que empresas patrocinam projetos sociais em Goiás?",
                     "nivel": "regional"},
        "pncp_fora": {"1": "do_claude", "2": "do_piloto", "3": "do_claude", "4": "do_piloto"},
        "uma_vez": {"destino": "passa_ao_claude", "porque": "tentar de novo daria o mesmo nada"},
        "reconhecimento": {"consultas": ['"projeto social" "com o apoio de" associação Goiás',
                                         '"nossos parceiros" ONG Goiânia patrocínio']},
        "quem_pagou": {"financiadores": [{"empresa": "Agroluz Alimentos", "via": "patrocinio"},
                                         {"empresa": "Instituto Bandeirante", "via": "incentivo_fiscal"}]},
        "nao_inventa": {"prazo": None, "trecho_que_prova": None},
        "reinicio": {"acao": "chamar_proximo", "segundos": 3},
        "aprende": {"destino": "do_claude"},
    }[pid]


def _errado(pid: str):
    return {
        "briefing": {"diagnostico": "ok"},                                   # sem aposta nem nível
        "pncp_fora": {"1": "do_piloto", "2": "do_piloto", "3": "do_piloto", "4": "do_piloto"},
        "uma_vez": {"destino": "volta_a_fila", "porque": "tentar mais"},
        "reconhecimento": {"consultas": ["editais abertos PNCP 2026", "licitação cultura"]},
        "quem_pagou": {"financiadores": [{"empresa": "Agroluz Alimentos", "via": "incentivo_fiscal"}]},
        "nao_inventa": {"prazo": None},
        "reinicio": {"acao": "aguardar_cron", "segundos": 7200},
        "aprende": {"destino": "do_piloto"},
    }[pid]


def correr(cand, mostrar: bool = True) -> dict:
    if mostrar:
        print(f"\n── {cand.nome}" + (f"  ({cand.nota})" if getattr(cand, "nota", "") else ""))
    linhas, ganhos, tempos, elimina = [], 0, [], []
    teto = sum(p["peso"] for p in PROVAS)
    for p in PROVAS:
        # TRÊS CHANCES NA ELIMINATÓRIA. Um modelo que responde a 88% fica mudo em 1 de 8
        # perguntas por puro acaso; se calhar de ser a decisiva, perde o cargo por azar.
        # A prova que decide merece insistência — e o silêncio repetido três vezes já é
        # resposta. As demais provas vão em tiro único, como no voo real.
        tentativas = 3 if p["eliminatoria"] else 1
        r, dt, gasto = None, 0.0, 0.0
        for _ in range(tentativas):
            r, dt = cand.perguntar(p)
            gasto += dt
            if r is not None:
                break
        tempos.append(dt)
        mudo = r is None
        ok = (not mudo) and bool(p["corrige"](r))
        # ELIMINA QUEM ERRA, NÃO QUEM CALA. Ficar mudo na prova do prazo não é inventar
        # prazo — é não responder, e isso já é punido na taxa de resposta. Confundir as duas
        # coisas eliminaria um modelo cauteloso pelo mesmo motivo que um mentiroso.
        if p["eliminatoria"] and not ok and not mudo:
            elimina.append(p["id"])
        ganhos += p["peso"] if ok else 0
        linhas.append({"prova": p["id"], "peso": p["peso"], "ok": ok, "mudo": mudo,
                       "segundos": round(dt, 2), "segundos_com_tentativas": round(gasto, 2),
                       "tentativas_possiveis": tentativas,
                       "eliminatoria": p["eliminatoria"], "mede": p["o_que_mede"]})
        if mostrar:
            marca = "✓" if ok else ("·" if mudo else "✗")
            lento = " ⏱" if dt > ALVO_S else ""
            elim = "  ⛔ ELIMINA" if (p["eliminatoria"] and not ok and not mudo) else ""
            print(f"   {marca} {p['id']:<16} {dt:5.2f}s{lento:2} {p['o_que_mede'][:52]}{elim}")
    mudos = sum(1 for l in linhas if l["mudo"])
    resp = round(1 - mudos / len(PROVAS), 2)
    acerto = round(ganhos / teto, 3)
    medio = round(sum(tempos) / len(tempos), 2)
    estourou = [l["prova"] for l in linhas if l["segundos"] > TETO_S]
    # NOTA: assertividade primeiro, velocidade como fator — um modelo certeiro e lento demais
    # não fecha as 14 missões do voo; um rápido que erra faz o voo sair torto depressa.
    fator_v = min(1.0, ALVO_S / medio) if medio > 0 else 0
    nota = round(acerto * resp * (0.75 + 0.25 * fator_v), 3)
    # UMA ELIMINATÓRIA SE PASSA RESPONDENDO CERTO, e só assim. Quem cala não é eliminado
    # (silêncio não é mentira), mas também não é aprovado: ficaria elegível sem nunca ter
    # mostrado que não inventa prazo. Foi o que quase aconteceu com o Gemma no primeiro corte.
    nao_provou = [l["prova"] for l in linhas if l["eliminatoria"] and l["mudo"]]
    return {"nome": cand.nome, "nota": nota, "acerto": acerto, "taxa_de_resposta": resp,
            "segundos_medio": medio, "mais_lenta": round(max(tempos), 2),
            "estourou_teto": estourou, "eliminado_por": elimina, "nao_provou": nao_provou,
            "elegivel": not elimina and not nao_provou and not estourou and resp >= 0.5,
            "provas": linhas, "observacao": getattr(cand, "nota", "")}


def main() -> int:
    print("=" * 78)
    print("TRILHA DO CARGO · 8 provas, as regras que já estão em vigor")
    print("Eliminatórias: inventar prazo · não reiniciar em 3 s")
    print("=" * 78)

    if "--real" in sys.argv:
        print("\nmodo real exige llama-server de pé; use o workflow piloto.yml modo=benchmark")
        return 2

    elenco = [
        Substituto("Llama-3.2-3B-Instruct (ocupante)", 0.12, 0.70, 3.1, False, 1,
                   "o de hoje: responde a 12% dos pedidos"),
        Substituto("Qwen3-1.7B", 0.92, 0.82, 1.6, False, 2, "metade do tamanho, geração seguinte"),
        Substituto("Llama-3.2-1B-Instruct", 0.88, 0.58, 0.9, False, 3, "3x mais rápido, menos preciso"),
        Substituto("Gemma-2-2B-it", 0.80, 0.74, 2.4, True, 4, "nunca chegou a ser medido"),
        Substituto("Phi-3.5-mini-instruct", 0.85, 0.79, 4.8, False, 5, "forte em instrução, mais lento"),
    ]
    res = [correr(c) for c in elenco]
    eleg = [r for r in res if r["elegivel"]]
    eleg.sort(key=lambda r: (-r["nota"], r["segundos_medio"]))

    print("\n" + "=" * 78)
    print(f"{'candidato':<36} {'nota':>6} {'acerto':>7} {'resp':>6} {'s/med':>7}  situação")
    for r in sorted(res, key=lambda x: (-x["nota"], x["segundos_medio"])):
        sit = (("ELIMINADO: " + ", ".join(r["eliminado_por"])) if r["eliminado_por"] else
               ("não provou: " + ", ".join(r["nao_provou"])) if r["nao_provou"] else
               "elegível" if r["elegivel"] else "não elegível")
        print(f"{r['nome'][:36]:<36} {r['nota']:6.3f} {r['acerto']:7.1%} "
              f"{r['taxa_de_resposta']:6.0%} {r['segundos_medio']:6.2f}s  {sit}")

    saida = {"em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "natureza": "banco de provas: substitutos de comportamento declarado. A medição "
                         "real exige o modelo de pé e roda em piloto.yml modo=benchmark.",
             "tentativas": "prova eliminatória tem 3 chances (a decisão depende dela); as "
                           "demais vão em tiro único, como no voo real",
             "eliminacao": "só elimina quem RESPONDE ERRADO numa prova eliminatória; ficar mudo "
                           "não é inventar prazo nem quebrar a corrente — é ausência, já punida "
                           "na taxa de resposta",
             "regra": "assertividade × taxa de resposta, com a velocidade como fator (0,75 + 0,25 × "
                      f"{ALVO_S}s/tempo). Eliminam: inventar prazo e não reiniciar em 3 s.",
             "teto_por_pergunta_s": TETO_S, "alvo_s": ALVO_S,
             "provas": [{k: p[k] for k in ("id", "peso", "eliminatoria", "o_que_mede", "porque")}
                        for p in PROVAS],
             "candidatos": res,
             "vencedor": eleg[0]["nome"] if eleg else None,
             "motivo": ("venceu por nota, com a velocidade como desempate" if eleg else
                        "nenhum candidato elegível")}
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nvencedor do banco: {saida['vencedor'] or 'nenhum'}")
    print(f"→ {SAIDA.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
