"""Regramento de cada fonte — a inteligência ANTES da busca.

Doutrina do titular: não basta busca cega em diários e sites. Cada fonte tem
uma regra (lei, decreto, IN, resolução, portaria, ato, regulamento privado)
que diz quem pode pedir, como, quando e onde se publica. O Eldorado precisa
conhecê-la antes de procurar o edital, e aprender com cada edital encontrado.

Este módulo, por fonte:
  1. baixa o texto oficial das normas marcadas `a_baixar` (roda no CI; aqui a
     rede não alcança) e o guarda na Biblioteca;
  2. extrai do texto a REGRA DE CALENDÁRIO ("de 1º de fevereiro a 30 de
     novembro", "entre X e Y") — só assim uma janela vira `verificado_no_texto`;
  3. cruza com o histórico (últimos editais, meses, duração, exigências);
  4. reúne o conselho de 7 lentes sobre a fonte e grava o PARECER na pasta dela;
  5. entrega ao motor de busca o léxico próprio e os locais de divulgação.

Nada é presumido — e ausência não é aceita: o que não foi obtido vira alvo
com prazo (dentro do mês) e escalada (sensor → IA barata → IA forte).
"""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import date
from urllib.parse import urlsplit

from .nucleo import ROOT, load_json, now_iso, sha256, slug, write_json

CFG = ROOT / "config/regramentos.json"
NORMAS = ROOT / "biblioteca_alexandria/leis/normas_das_fontes"
FONTES = ROOT / "biblioteca_alexandria/fontes"
ESTADO = ROOT / "estado/regramentos.json"

_MESES = {"janeiro": 1, "fevereiro": 2, "março": 3, "marco": 3, "abril": 4, "maio": 5, "junho": 6,
          "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12}
_JANELA = [
    re.compile(r"(?:de|entre)\s+(\d{1,2})[ºo°]?\s+de\s+(\w+)\s+(?:a|e|at[ée])\s+(\d{1,2})[ºo°]?\s+de\s+(\w+)", re.I),
    re.compile(r"(\d{1,2})/(\d{1,2})\s+(?:a|at[ée])\s+(\d{1,2})/(\d{1,2})"),
]
_PRAZO_CTX = re.compile(r"(?:per[íi]odo|prazo|apresenta[çc][ãa]o\s+de\s+propostas?|inscri[çc][õo]es|"
                        r"submiss[ãa]o)[^.]{0,220}", re.I)


def _cfg() -> dict:
    return load_json(CFG)


def _abrir(url: str) -> str | None:
    from .nucleo import validate_public_https
    from urllib.request import Request, urlopen
    try:
        validate_public_https(url, urlsplit(url).hostname)
        req = Request(url, headers={"User-Agent": "Eldorado-OSC/1.0 regramentos",
                                    "Accept": "text/html,application/pdf;q=0.9,*/*;q=0.5"})
        with urlopen(req, timeout=40) as r:
            dados = r.read(20_000_000)
            ctype = r.headers.get_content_type()
    except Exception:
        return None
    if "pdf" in ctype or dados[:5] == b"%PDF-":
        try:
            import io
            from pypdf import PdfReader
            return "\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(dados)).pages)
        except Exception:
            return None
    html = dados.decode("utf-8", "replace")
    texto = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    texto = re.sub(r"<[^>]+>", " ", texto)
    return re.sub(r"[ \t]+", " ", texto)


def extrair_calendario(texto: str) -> list[dict]:
    """Regras de calendário no texto, sempre com o trecho que as sustenta."""
    achados = []
    for ctx in _PRAZO_CTX.finditer(texto or ""):
        trecho = ctx.group(0)
        m = _JANELA[0].search(trecho)
        if m and m.group(2).lower() in _MESES and m.group(4).lower() in _MESES:
            achados.append({"inicio_mes_dia": f"{_MESES[m.group(2).lower()]:02d}-{int(m.group(1)):02d}",
                            "fim_mes_dia": f"{_MESES[m.group(4).lower()]:02d}-{int(m.group(3)):02d}",
                            "trecho": re.sub(r"\s+", " ", trecho)[:260]})
            continue
        m = _JANELA[1].search(trecho)
        if m:
            achados.append({"inicio_mes_dia": f"{int(m.group(2)):02d}-{int(m.group(1)):02d}",
                            "fim_mes_dia": f"{int(m.group(4)):02d}-{int(m.group(3)):02d}",
                            "trecho": re.sub(r"\s+", " ", trecho)[:260]})
    vistos, unicos = set(), []
    for a in achados:
        k = (a["inicio_mes_dia"], a["fim_mes_dia"])
        if k not in vistos:
            vistos.add(k); unicos.append(a)
    return unicos[:5]


def baixar_normas(regramento: dict) -> list[dict]:
    """Baixa as normas 'a_baixar'; guarda o texto; extrai o calendário."""
    saida = []
    pasta = NORMAS / slug(regramento["id"])
    pasta.mkdir(parents=True, exist_ok=True)
    for n in regramento.get("normas", []):
        reg = dict(n)
        if n.get("status") == "texto_no_repositorio" or not n.get("url"):
            saida.append(reg); continue
        texto = _abrir(n["url"])
        if not texto or len(texto) < 500:
            reg["status"] = "a_baixar"
            reg["ultima_tentativa"] = now_iso()
            reg["motivo"] = "sem resposta ou página sem texto (rede/portal)"
        else:
            arq = pasta / (slug(n["ref"])[:60] + ".txt")
            arq.write_text(f'{n["ref"]}\nFonte: {n["url"]}\nBaixado em: {now_iso()}\n\n{texto}', encoding="utf-8")
            reg.update({"status": "texto_no_repositorio", "arquivo": str(arq.relative_to(ROOT)),
                        "hash": sha256(texto.encode()), "baixado_em": now_iso(),
                        "calendario_no_texto": extrair_calendario(texto)})
        saida.append(reg)
    return saida


def _historico_da_fonte(regramento: dict) -> dict:
    """Últimos editais e comportamento observado da fonte."""
    try:
        from .banco import conectar
        con = conectar()
    except Exception:
        return {"editais": 0}
    toks = [t for t in re.findall(r"[a-zà-ú]{5,}", regramento["fonte"].lower())
            if t not in ("programa", "fundo", "municipal", "estadual", "federal", "recursos")][:4]
    rows = con.execute("SELECT titulo, data_publicacao, inicio, fim, exigencias, uf FROM historico "
                       "ORDER BY data_publicacao DESC").fetchall()
    con.close()
    casos = [r for r in rows if toks and sum(1 for t in toks if t in (r[0] or "").lower()) >= max(1, len(toks) - 1)]
    meses = Counter((r[3] or r[2] or r[1] or "")[5:7] for r in casos if (r[3] or r[2] or r[1]))
    exig = Counter(e for r in casos for e in json.loads(r[4] or "[]"))
    return {"editais": len(casos),
            "ultimo": ({"titulo": casos[0][0][:120], "publicado": casos[0][1], "fim": casos[0][3]} if casos else None),
            "meses_observados": dict(meses.most_common(6)),
            "exigencias_frequentes": [e for e, _ in exig.most_common(8)],
            "com_prazo_real": sum(1 for r in casos if r[3])}


def parecer_do_conselho(reg: dict, normas: list[dict], hist: dict, hoje: date) -> dict:
    """Sete lentes sobre a fonte; o neutro define a estratégia de busca."""
    from .conselho_edital import PONTOS_DE_VISTA, ROTULOS, sorteia_conselheiros
    cal = [c for n in normas for c in (n.get("calendario_no_texto") or [])]
    normas_lidas = sum(1 for n in normas if n.get("status") == "texto_no_repositorio")
    pend = [n["ref"] for n in normas if n.get("status") != "texto_no_repositorio"]
    cons = sorteia_conselheiros(f'{reg["id"]}|regramento')
    L = {}
    L["extremamente_pessimista"] = [
        (f'{len(pend)} norma(s) ainda não lida(s): {", ".join(pend[:2])} — sem o texto, o calendário é chute' if pend
         else "todas as normas lidas; falta só a confirmação do edital do ano"),
        ("nenhum edital desta fonte no acervo: comportamento desconhecido" if not hist["editais"]
         else f'{hist["editais"]} edital(is) no acervo, mas só {hist["com_prazo_real"]} com prazo real')]
    L["pessimista"] = [("página oficial é institucional, não listagem — o sensor pode ler e não achar nada"
                        if not reg.get("sistema_de_inscricao") else "há sistema de inscrição: o prazo pode estar só dentro dele"),
                       f'divulgação regular: {reg["divulgacao"]["regular"]} — cada canal precisa de sensor próprio']
    L["levemente_pessimista"] = [f'período esperado: {reg["divulgacao"]["periodo_esperado"]}' + (" — extraído do texto" if cal else " — AINDA NÃO extraído do texto")]
    L["levemente_otimista"] = [f'léxico próprio com {len(reg.get("lexico_proprio", []))} termos direciona a leitura',
                               f'tipo: {reg["tipo_recurso"]} · permanência: {reg["permanencia"]}']
    L["otimista"] = [(f'calendário no texto da norma: {cal[0]["inicio_mes_dia"]} a {cal[0]["fim_mes_dia"]}' if cal
                      else f'{normas_lidas} norma(s) já no repositório para orientar requisitos'),
                     (f'exigências recorrentes conhecidas: {", ".join(hist["exigencias_frequentes"][:4])}'
                      if hist["exigencias_frequentes"] else "quem pode: " + reg.get("quem_pode", "—"))]
    L["extremamente_otimista"] = ["fonte com regra escrita: uma vez lida, o sistema sabe quando e onde procurar todo ano",
                                  f'último edital: {hist["ultimo"]["titulo"][:70]}' if hist.get("ultimo") else "primeira leitura cria o padrão"]
    # neutro: estratégia de busca desta fonte
    onde = [reg.get("pagina_oficial")] + ([reg["sistema_de_inscricao"]] if reg.get("sistema_de_inscricao") else [])
    estrategia = {
        "onde_procurar_primeiro": [u for u in onde if u],
        "canal_regular": reg["divulgacao"]["regular"],
        "quando": (f'{cal[0]["inicio_mes_dia"]} a {cal[0]["fim_mes_dia"]} (verificado no texto)' if cal
                   else reg["divulgacao"]["periodo_esperado"] + " (a verificar)"),
        "lexico": reg.get("lexico_proprio", []),
        "cadencia": "diária enquanto houver pendência; para ao completar os 11 itens ou quando três leituras seguidas dos locais oficiais nada trazem",
        "escalada": ["sensor determinístico", "IA barata com busca (haiku)", "IA intermediária (sonnet)", "IA forte só para o parecer final"],
        "pendencias": ([f'baixar e ler: {p}' for p in pend] + ([] if cal or reg["tipo_recurso"] == "emenda" else ["extrair a regra de calendário do texto"])),
        "prazo_para_completar": "dentro do mês corrente",
    }
    L["neutro"] = [f'estratégia: {estrategia["quando"]} · procurar em {len(estrategia["onde_procurar_primeiro"])} local(is) oficial(is)',
                   f'{len(estrategia["pendencias"])} pendência(s) para o mês']
    return {"fonte": reg["fonte"], "id": reg["id"], "gerado_em": now_iso(),
            "conselheiros": cons,
            "lentes": {pv: {"rotulo": ROTULOS[pv], "conselheiro": cons[pv], "achados": L[pv]} for pv in PONTOS_DE_VISTA},
            "classificacao": {"tipo_recurso": reg["tipo_recurso"], "permanencia": reg["permanencia"],
                              "base_legal": [n["ref"] for n in normas], "normas_lidas": normas_lidas,
                              "normas_pendentes": pend, "calendario_verificado": bool(cal),
                              "calendario": cal[:2], "divulgacao": reg["divulgacao"],
                              "quem_pode": reg.get("quem_pode")},
            "historico": hist, "estrategia_de_busca": estrategia,
            "nota": "nada presumido; pendências viram alvo do motor com escalada e prazo no mês"}


def run(hoje: date | None = None, baixar: bool = True) -> dict:
    hoje = hoje or date.today()
    cfg = _cfg()
    est = load_json(ESTADO) if ESTADO.exists() else {"fontes": {}}
    resumo = {"fontes": 0, "normas_lidas": 0, "normas_pendentes": 0, "calendarios_verificados": 0}
    for reg in cfg["regramentos"]:
        normas = baixar_normas(reg) if baixar else reg.get("normas", [])
        hist = _historico_da_fonte(reg)
        par = parecer_do_conselho(reg, normas, hist, hoje)
        pasta = FONTES / slug(reg["id"])
        pasta.mkdir(parents=True, exist_ok=True)
        write_json(pasta / "regramento.json", {**reg, "normas": normas, "atualizado_em": now_iso()})
        write_json(pasta / "parecer_conselho.json", par)
        est["fontes"][reg["id"]] = {"normas_lidas": par["classificacao"]["normas_lidas"],
                                    "pendentes": par["classificacao"]["normas_pendentes"],
                                    "calendario_verificado": par["classificacao"]["calendario_verificado"],
                                    "em": now_iso()}
        resumo["fontes"] += 1
        resumo["normas_lidas"] += par["classificacao"]["normas_lidas"]
        resumo["normas_pendentes"] += len(par["classificacao"]["normas_pendentes"])
        resumo["calendarios_verificados"] += bool(par["classificacao"]["calendario_verificado"])
    est["atualizado_em"] = now_iso()
    write_json(ESTADO, est)
    return {**resumo, "executado_em": now_iso()}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
