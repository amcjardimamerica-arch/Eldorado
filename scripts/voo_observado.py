#!/usr/bin/env python3
"""VOO OBSERVADO — dez voos com um avaliador a bordo.

Isto é um BANCO DE PROVAS, não produção. A diferença importa e está declarada em cada linha
do relatório: aqui o contêiner não alcança buscador nenhum e não há modelo local rodando.
O que o banco faz é exercitar o CÓDIGO REAL de decisão — briefing, escolha de rumo, missão
de resgate, prospecção, avaliação, aprendizado — com os DADOS REAIS do sistema, substituindo
apenas o que o ambiente não pode fornecer, e anotando cada substituição.

A pergunta que o banco responde: **onde cada voo para, e por quê?**

Duas condições de cabine, cinco voos cada:

    voos 1 a 5    modelo MUDO — a realidade de hoje (12% de resposta)
    voos 6 a 10   modelo RESPONDENDO — para isolar o que o modelo contribui

Comparar as duas metades diz quanto do fracasso é do modelo e quanto é de arquitetura.
"""
from __future__ import annotations

import json
import random
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.nucleo import load_json  # noqa: E402

DIARIO: list[dict] = []
T0 = time.time()


def anota(voo: int, etapa: str, decisao: str, detalhe: str = "", ok: bool | None = None,
          impedimento: str = "") -> None:
    """O avaliador anota. Cada linha é uma decisão observada, não um resumo."""
    DIARIO.append({"voo": voo, "t": round(time.time() - T0, 2), "etapa": etapa,
                   "decisao": decisao, "detalhe": detalhe[:220], "ok": ok,
                   "impedimento": impedimento})
    marca = "  " if ok is None else ("✓ " if ok else "✗ ")
    imp = f"   [banco: {impedimento}]" if impedimento else ""
    print(f"  {marca}{etapa:<22} {decisao}{(' — ' + detalhe[:90]) if detalhe else ''}{imp}")


class IAMuda:
    """O ocupante de hoje: responde a 12% dos pedidos."""
    nome = "mudo (Llama-3.2-3B como está)"

    def __init__(self, semente: int):
        self.r = random.Random(semente)
        self.pedidos = self.respostas = 0

    def perguntar(self, p, esquema=None):
        self.pedidos += 1
        if self.r.random() < 0.12:
            self.respostas += 1
            return _resposta_plausivel(p, esquema)
        return None


class IAFalante:
    """O ocupante que o cargo exige: responde sempre, com JSON válido."""
    nome = "respondendo (hipótese de um reserva que cumpre o critério)"

    def __init__(self, semente: int):
        self.r = random.Random(semente)
        self.pedidos = self.respostas = 0

    def perguntar(self, p, esquema=None):
        self.pedidos += 1
        self.respostas += 1
        return _resposta_plausivel(p, esquema, self.r)


def _resposta_plausivel(p: str, esquema=None, r: random.Random | None = None):
    """Resposta no formato que o código espera. Conteúdo verossímil, nunca dado real."""
    r = r or random.Random(0)
    t = (p or "").lower()
    if "prestes a decolar" in t or "biblioteca hoje" in t.replace("_", " "):
        m = load_json(RAIZ / "config/motor_piloto.json")
        a = r.choice(m.get("angulos_de_ataque") or [{"id": "x", "pergunta": "onde há recurso?", "nivel": "nacional"}])
        return {"diagnostico": "o acervo é quase todo fonte pública",
                "aposta": {"onde": a["id"], "porque": "setor com caixa e pouco procurado", "confianca": "media"},
                "pergunta_de_pesquisa": a["pergunta"], "o_que_procurar": ["site oficial"],
                "nivel": a.get("nivel", "nacional")}
    if "missão especial" in t or "resgate de edital" in t:
        return {"consultas": [f"edital página oficial {r.randint(1, 99)}"],
                "onde_provavelmente_esta": "portal do órgão", "o_que_ler_na_pagina": ["prazo"]}
    if "procuro este edital" in t:
        return {"e_este_edital": False}
    if "páginas que listam apoiadores" in t or "missão de expansão" in t:
        return {"consultas": ["\"nossos parceiros\" associação Goiás"]}
    if "serve" in t and "achados" in t:
        return {"itens": [], "o_que_melhorar_no_motor": "filtrar por 'chamamento' antes de abrir"}
    if "consultas" in str(esquema or ""):
        return {"consultas": ["consulta de banco de provas"]}
    return None


# PÁGINAS DE BANCO. Textos verossímeis no formato em que as coisas realmente aparecem: uma
# matéria de jornal local, uma página de apoiadores de ONG, um cartaz de evento, um balanço.
# Nenhum dado real de empresa — o que se testa é a LEITURA, não o conteúdo.
PAGINAS = [
 ("imprensa", "https://jornaldacidade.com.br/oficina-musica",
  "A Associação Jardim Feliz inaugurou ontem sua oficina de música, que atende 120 crianças "
  "do bairro. O projeto teve patrocínio da Agroluz Alimentos e contou com o apoio da "
  "Construtora Meridiano. A reforma da quadra foi viabilizada pelo Instituto Bandeirante, com "
  "recursos da Lei de Incentivo ao Esporte. A doação dos instrumentos foi feita pelo "
  "Supermercado Cerrado."),
 ("entidade", "https://ongsemearfuturo.org.br/parceiros",
  "Quem caminha conosco. Nossas atividades em 2025 só foram possíveis graças ao apoio de "
  "parceiros. Realização da Fundação Vale Verde. Com o apoio da Cooperativa Central do "
  "Cerrado e da Transportadora Rio Claro. O programa de alfabetização é financiado pela "
  "Mineradora Serra Azul através do Fundo da Criança e do Adolescente."),
 ("evento", "https://festivalsolidario.com.br/programacao",
  "12º Festival Solidário — programação completa. Patrocínio da Energisa Goiás e da "
  "Distribuidora Planalto. Apoio institucional do Banco Meridiano. A praça de alimentação tem "
  "realização da Rede Bom Preço. Cotas de patrocínio ainda disponíveis para a edição de 2026."),
 ("prestacao", "https://institutoraizes.org.br/transparencia",
  "Demonstrativo de receitas 2025. Doações de pessoas jurídicas: R$ 480.000,00. Entre os "
  "doadores, destaque para a Indústria Química Pantanal e a Usina São Bento. O projeto de "
  "capacitação foi custeado pela Seguradora Goiás Vida. Convênio com a Fundação Bradesco "
  "para material didático."),
 ("imprensa", "https://portalregional.com.br/apae-reforma",
  "A APAE de Anápolis entregou nesta semana o novo bloco de atendimento. A obra foi bancada "
  "pela Frigorífico Boi Forte, com projeto doado pelo Escritório Andrade Arquitetura. O "
  "mobiliário teve doação da Móveis Planalto. A entidade informa que a manutenção anual é "
  "financiada pela Cimento Araguaia através do Fundo do Idoso."),
]


def voo(n: int, ia) -> dict:
    """Um voo completo, anotado etapa a etapa, nas DUAS missões como o titular definiu."""
    from src.briefing_piloto import escrever as brief, fechar as fecha_brief
    from src.missao_especial import montar_fila, proximo, PARA_O_CLAUDE, _e_pncp
    from src.cobertura import ja_coberto, mapa
    from src.reconhecimento import ler_rastros, registrar, proximo_do_plano, marcar, publicar as pub_rec

    print(f"\n── VOO {n:02d} · cabine: {ia.nome}")
    res = {"voo": n, "cabine": ia.nome, "etapas": 0, "financiadores": 0, "parou_em": None}

    # 1 · BRIEFING
    b = brief(ia)
    mudo = bool(b.get("modelo_mudo"))
    anota(n, "briefing", "rumo definido" if not mudo else "modelo mudo → rumo sorteado",
          f"{(b.get('aposta') or {}).get('onde')} · {b.get('nivel')}", ok=not mudo)
    res["rumo"] = (b.get("aposta") or {}).get("onde")
    res["etapas"] += 1

    # 2 · MISSÃO 1 — especial. PNCP não é dele.
    r = montar_fila()
    fila = r.get("na_fila", 0)
    anota(n, "missão 1 · triagem", f"{fila} alvo(s) para o Piloto · {r.get('para_o_claude', 0)} ao Claude",
          "PNCP é dado genérico: quem analisa é o Claude, por fora", ok=True)
    res["etapas"] += 1
    alvo = proximo()
    if alvo:
        assert not _e_pncp(alvo), "PNCP vazou para a fila do Piloto"
        anota(n, "missão 1 · resgate", f"reservou «{str(alvo.get('titulo'))[:40]}»",
              "uma única vez: se não achar, passa ao Claude", ok=True)
        res["etapas"] += 1
    else:
        anota(n, "missão 1 · resgate", "nada a resgatar",
              "o acervo é todo PNCP e já foi entregue — o voo inteiro vai para a missão 2", ok=True)

    # 3 · MISSÃO 2 — reconhecimento. O plano de voo manda primeiro.
    pend = proximo_do_plano()
    if pend:
        anota(n, "missão 2 · plano", f"investigar {pend['empresa']}",
              f"descoberto antes · {', '.join(pend.get('vias') or [])}", ok=True)
        res["investigando"] = pend["empresa"]
    else:
        anota(n, "missão 2 · plano", "plano vazio → frente nova",
              "primeira passada: ainda não há financiador a investigar", ok=True)
    res["etapas"] += 1

    frente, url, texto = PAGINAS[(n - 1) % len(PAGINAS)]
    coberto, por = ja_coberto(url)
    anota(n, "missão 2 · crivo", "página aceita" if not coberto else f"descartada ({por})",
          f"{frente} · {url[:52]}", ok=not coberto)
    res["etapas"] += 1

    rastros = ler_rastros(texto, url)
    vias = sorted({x["via"] for x in rastros})
    anota(n, "missão 2 · leitura", f"{len(rastros)} financiador(es)",
          f"vias: {', '.join(vias)}" if vias else "nenhum rastro", ok=bool(rastros),
          impedimento="página do banco: sem rede para buscar a real")
    for x in rastros:
        it = registrar(x, frente, "regional")
        if it:
            res["financiadores"] += 1
    if pend and rastros:
        marcar(pend["alvo"], "investigado")
    res["etapas"] += 1

    pub = pub_rec()
    anota(n, "missão 2 · catálogo", f"{pub['total']} no radar · {pub['no_plano_de_voo']} a investigar",
          f"por via: {pub['por_via']}", ok=True)
    res["no_radar"] = pub["total"]
    res["no_plano"] = pub["no_plano_de_voo"]
    res["etapas"] += 1

    # 4 · APRENDIZADO
    from src.aprendizados_piloto import avaliar
    a = avaliar(ia, {"motor": "sindico-aberto", "tipo": "reconhecimento",
                     "licao": f"{frente}: {len(rastros)} financiador(es)"},
                [{"titulo": x["empresa"], "url": url, "trecho": x["trecho"],
                  "confirmado_na_pagina": True} for x in rastros])
    anota(n, "aprendizado", f"efetividade {a['avaliacao'].get('efetividade')}",
          a["avaliacao"].get("explicacao") or "", ok=True)
    res["etapas"] += 1

    if not res["financiadores"]:
        res["parou_em"] = "leitura sem rastro"
    fecha_brief(b, [])
    res["pedidos_ao_modelo"] = ia.pedidos
    res["respostas_do_modelo"] = ia.respostas
    return res


def main() -> int:
    import os
    import tempfile
    tmp = tempfile.mkdtemp(prefix="voo-observado-")
    os.environ["ELDORADO_APRENDIZADOS"] = tmp        # o banco não suja a base de produção
    # nem o radar: em 23/09 as empresas das páginas do banco (todas fictícias) entraram no
    # radar real, e o plano de voo passou a mandar o Piloto investigar empresas inexistentes
    import src.reconhecimento as R, src.briefing_piloto as BP
    R.ALVOS, R.PUB = Path(tmp) / "reconhecimento.json", Path(tmp) / "reconhecimento_pub.json"
    BP.PASTA = Path(tmp) / "briefings"
    import importlib
    import src.aprendizados_piloto as A
    importlib.reload(A)

    print("=" * 78)
    print("BANCO DE PROVAS · 10 VOOS OBSERVADOS")
    print("Código e dados reais. Sem rede e sem modelo local — cada substituição é anotada.")
    print("=" * 78)

    voos = []
    for i in range(1, 11):
        ia = IAMuda(i) if i <= 5 else IAFalante(i)
        voos.append(voo(i, ia))

    mudos = [v for v in voos if v["voo"] <= 5]
    falantes = [v for v in voos if v["voo"] > 5]
    rel = {
        "em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "natureza": "banco de provas: código e dados reais, sem rede e sem modelo local",
        "voos": voos, "diario": DIARIO,
        "comparacao": {
            "com_modelo_mudo": {"voos": len(mudos),
                                "rumos_distintos": len({v["rumo"] for v in mudos}),
                                "etapas_medias": round(sum(v["etapas"] for v in mudos) / len(mudos), 1)},
            "com_modelo_respondendo": {"voos": len(falantes),
                                       "rumos_distintos": len({v["rumo"] for v in falantes}),
                                       "etapas_medias": round(sum(v["etapas"] for v in falantes) / len(falantes), 1)},
        },
        "onde_pararam": {},
        "radar": {"financiadores": sum(v["financiadores"] for v in voos),
                  "no_radar_ao_final": voos[-1].get("no_radar"),
                  "no_plano_ao_final": voos[-1].get("no_plano")},
    }
    for v in voos:
        rel["onde_pararam"][v["parou_em"] or "concluiu"] = rel["onde_pararam"].get(v["parou_em"] or "concluiu", 0) + 1

    saida = RAIZ / "estado/piloto/voo_observado_2026-09-23.json"
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")

    print("\n" + "=" * 78)
    print("RESUMO")
    print(f"  rumos distintos — modelo mudo: {rel['comparacao']['com_modelo_mudo']['rumos_distintos']}/5"
          f" · modelo respondendo: {rel['comparacao']['com_modelo_respondendo']['rumos_distintos']}/5")
    print(f"  onde os voos pararam: {rel['onde_pararam']}")
    print(f"  radar: {rel['radar']['financiadores']} financiador(es) registrados · "
          f"{rel['radar']['no_radar_ao_final']} no radar · {rel['radar']['no_plano_ao_final']} a investigar")
    print(f"  diário: {len(DIARIO)} decisões anotadas → {saida.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
