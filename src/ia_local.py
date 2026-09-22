"""IA LOCAL — cliente do llama-server e as cinco tarefas de ORGANIZAÇÃO.

A IA local propõe; o sistema valida; só então grava. Cada tarefa tem um esquema JSON fixo
e uma regra de aceitação. Prazo, valor, objeto e página oficial só entram no registro se a
proposta trouxer o TRECHO LITERAL do texto que os sustenta — e o trecho tem de existir no
texto de fato (verificado por comparação normalizada). Sem trecho, a proposta é descartada e
o motivo fica anotado.

Tarefas (config/ia_local.json → tarefas_permitidas):
  classificar_objeto ..... família do registro (fomento_osc, servico_ao_orgao, …) + confiança + trecho
  extrair_objeto_prazo ... objeto e prazo de um texto já coletado, com trechos literais
  propor_lexico .......... termos positivos/vetos a partir de um lote de títulos, com exemplos
  diagnosticar_rota ...... por que um motor "lê sem achar" e o que tentar (URL/termo), a partir do diagnóstico
  catalogar_achado ....... resumo de uma linha do achado do dia, por motor

Uso:
  python -m src.ia_local ciclo      # roda as tarefas do dia, grava estado/ia_local/propostas-<data>.json
  python -m src.ia_local aplicar    # aplica o que passou na validação (léxico candidato, rotas sugeridas, classificação proposta)
  python -m src.ia_local status
"""
from __future__ import annotations

import json
import re
import unicodedata
import urllib.request
from datetime import date
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json

CFG = load_json(ROOT / "config/ia_local.json")
PASTA = ROOT / "estado/ia_local"
FAMILIAS = set(CFG["validacao"]["familias_validas"])

SISTEMA = ("Você organiza dados de editais de fomento para organizações da sociedade civil no Brasil. "
           "Responda SOMENTE com JSON válido no esquema pedido, sem texto fora do JSON. "
           "Nunca invente: se a informação não estiver no texto, use null. "
           "Quando citar prazo, valor, objeto ou página, copie o TRECHO LITERAL do texto que sustenta.")


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", (s or "").lower()).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", s)).strip()


def _trecho_existe(trecho: str | None, texto: str) -> bool:
    if not trecho or len(trecho) < 8:
        return False
    return _norm(trecho)[:60] in _norm(texto)


# ─────────────────────────────────────────────────────────────── cliente
class IALocal:
    def __init__(self, host: str | None = None, porta: int | None = None, timeout: float | None = None, transporte=None):
        s = CFG["servidor"]
        self.url = f"http://{host or s['host']}:{porta or s['porta']}/v1/chat/completions"
        self.timeout = timeout or CFG["limites"]["tempo_maximo_s"]
        self._transporte = transporte           # injetável nos testes: fn(payload)->dict
        self.modelo = "desconhecido"

    def disponivel(self) -> bool:
        if self._transporte:
            return True
        try:
            with urllib.request.urlopen(self.url.replace("/v1/chat/completions", "/health"), timeout=3) as r:
                return r.status == 200
        except Exception:
            return False

    def perguntar(self, prompt: str, esquema_hint: str) -> dict | None:
        # Gemma não aceita a role 'system': o sistema vai dentro da mensagem do usuário
        if getattr(self, "sem_system", False):
            msgs = [{"role": "user", "content": SISTEMA + " Esquema: " + esquema_hint + "\n\n" + prompt[:6000]}]
        else:
            msgs = [{"role": "system", "content": SISTEMA + " Esquema: " + esquema_hint}, {"role": "user", "content": prompt[:6000]}]
        payload = {"messages": msgs,
                   "temperature": CFG["limites"]["temperatura"], "max_tokens": CFG["limites"]["tokens_resposta"],
                   "response_format": {"type": "json_object"}}
        try:
            if self._transporte:
                data = self._transporte(payload)
            else:
                req = urllib.request.Request(self.url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    data = json.loads(r.read().decode("utf-8"))
            self.modelo = data.get("model") or self.modelo
            txt = data["choices"][0]["message"]["content"]
            txt = re.sub(r"^```(?:json)?|```$", "", txt.strip(), flags=re.M).strip()
            return json.loads(txt)
        except Exception:
            return None


# ─────────────────────────────────────────────────────────────── tarefas
def t_classificar_objeto(ia: IALocal, e: dict, texto: str) -> dict | None:
    """DUAS PERGUNTAS BINÁRIAS (21/09) em vez de três classes — modelos pequenos acertam
    mais respondendo sim/não do que escolhendo entre categorias ambíguas:
      (1) é uma chamada ABERTA que repassa recurso a organização sem fins lucrativos?
      (2) há SINAL DE VETO? (resultado de edital já julgado, seleção/credenciamento de
          empresa ou prestador, qualificação como OS, órgão buscando patrocinador,
          parceria já celebrada, licitação de compra)
    Veredito derivado: veto → reprovado; fomento e sem veto → aprovado; o resto → atenção."""
    try:
        from .cargo_sindico import licoes_para_o_prompt
        licoes = licoes_para_o_prompt()
    except Exception:
        licoes = ""
    r = ia.perguntar((licoes + "\n\n" if licoes else "") + f"TÍTULO: {e.get('titulo')}\nTEXTO: {texto[:2500]}",
                     '{"e_fomento_a_osc": true|false, "trecho_fomento": "frase literal ou null", '
                     '"sinal_de_veto": null | "resultado_de_edital" | "empresa_ou_mercado" | "servico_ao_orgao" | "qualificacao_os" | "busca_patrocinador" | "parceria_celebrada" | "nao_edital", '
                     '"trecho_veto": "frase literal ou null", "confianca": 0..1}')
    if not r or not isinstance(r, dict) or "e_fomento_a_osc" not in r:
        return None
    veto = r.get("sinal_de_veto") if r.get("sinal_de_veto") in FAMILIAS else None
    fomento = bool(r.get("e_fomento_a_osc"))
    familia = veto or ("fomento_osc" if fomento else "atencao")
    trecho = r.get("trecho_veto") if veto else r.get("trecho_fomento")
    ok = _trecho_existe(trecho, f"{e.get('titulo')} {texto}") if (veto or fomento) else True
    conf = float(r.get("confianca") or 0)
    return {"tarefa": "classificar_objeto", "id": e["id"], "familia": familia, "confianca": conf, "trecho": trecho,
            "motivo": ("veto: " + veto) if veto else ("fomento a OSC" if fomento else "sem sinal claro — atenção"),
            "perguntas": {"e_fomento_a_osc": fomento, "sinal_de_veto": veto},
            "valido": ok and conf >= 0.6, "invalido_por": None if ok else "trecho não encontrado no texto"}


def t_extrair_objeto_prazo(ia: IALocal, e: dict, texto: str) -> dict | None:
    r = ia.perguntar(f"TEXTO DO EDITAL: {texto[:5000]}",
                     '{"objeto": "frase do item DO OBJETO ou null", "objeto_trecho": "literal", "inicio": "AAAA-MM-DD ou null", "fim": "AAAA-MM-DD ou null", "prazo_trecho": "literal com a data", "pagina_oficial": "url ou null"}')
    if not r:
        return None
    obj_ok = bool(r.get("objeto")) and _trecho_existe(r.get("objeto_trecho") or r.get("objeto"), texto)
    fim_ok = bool(r.get("fim")) and re.match(r"^\d{4}-\d{2}-\d{2}$", str(r.get("fim") or "")) and _trecho_existe(r.get("prazo_trecho"), texto)
    return {"tarefa": "extrair_objeto_prazo", "id": e["id"], "objeto": r.get("objeto") if obj_ok else None, "inicio": r.get("inicio") if fim_ok else None,
            "fim": r.get("fim") if fim_ok else None, "trechos": {"objeto": r.get("objeto_trecho"), "prazo": r.get("prazo_trecho")},
            "valido": bool(obj_ok or fim_ok), "invalido_por": None if (obj_ok or fim_ok) else "nenhum campo com trecho literal no texto"}


def t_propor_lexico(ia: IALocal, aprovados: list[str], reprovados: list[str]) -> dict | None:
    r = ia.perguntar("TÍTULOS APROVADOS (são fomento a OSC):\n- " + "\n- ".join(aprovados[:40]) + "\n\nTÍTULOS REPROVADOS (não são):\n- " + "\n- ".join(reprovados[:40]),
                     '{"positivos": [{"termo": "...", "exemplo": "título aprovado que o contém"}], "vetos": [{"termo": "...", "exemplo": "título reprovado que o contém"}]}')
    if not r:
        return None
    ap_n = [_norm(x) for x in aprovados]; rp_n = [_norm(x) for x in reprovados]
    pos = [x for x in (r.get("positivos") or []) if x.get("termo") and any(_norm(x["termo"]) in t for t in ap_n) and not any(_norm(x["termo"]) in t for t in rp_n)]
    vet = [x for x in (r.get("vetos") or []) if x.get("termo") and any(_norm(x["termo"]) in t for t in rp_n) and not any(_norm(x["termo"]) in t for t in ap_n)]
    return {"tarefa": "propor_lexico", "positivos": pos[:20], "vetos": vet[:20], "valido": bool(pos or vet),
            "descartados": len((r.get("positivos") or [])) + len((r.get("vetos") or [])) - len(pos) - len(vet)}


def t_diagnosticar_rota(ia: IALocal, motor: dict) -> dict | None:
    r = ia.perguntar(f"MOTOR: {motor.get('nome')}\nPERFIL: {motor.get('perfil')}\nROTAS: {json.dumps(motor.get('rotas'), ensure_ascii=False)[:1200]}\nDIAGNÓSTICO DA ÚLTIMA LEITURA: {json.dumps(motor.get('diagnostico'), ensure_ascii=False)[:1200]}\nLÉXICO CAMADA 1: {motor.get('lexico')[:20]}",
                     '{"causa_provavel": "uma frase", "tentar": [{"tipo": "url|termo|cadencia", "valor": "...", "porque": "..."}], "confianca": 0..1}')
    if not r or not r.get("tentar"):
        return None
    tentar = [x for x in r["tentar"] if x.get("tipo") in ("url", "termo", "cadencia") and x.get("valor")]
    for x in tentar:
        if x["tipo"] == "url" and not re.match(r"^https?://[\w.-]+\.[a-z]{2,}", str(x["valor"])):
            x["valido"] = False; x["invalido_por"] = "URL malformada"
        else:
            x["valido"] = True
    return {"tarefa": "diagnosticar_rota", "motor": motor["id"], "causa_provavel": r.get("causa_provavel"), "tentar": tentar[:5],
            "confianca": float(r.get("confianca") or 0), "valido": any(x["valido"] for x in tentar)}


def t_catalogar_achado(ia: IALocal, dia: str, motores: dict) -> dict | None:
    r = ia.perguntar(f"DIA: {dia}\nACHADOS POR MOTOR: {json.dumps({m: [x['titulo'] for x in l][:8] for m, l in motores.items()}, ensure_ascii=False)[:3000]}",
                     '{"resumo": "uma linha em português com o que apareceu de relevante", "destaques": [{"titulo": "...", "porque": "..."}]}')
    if not r or not r.get("resumo"):
        return None
    return {"tarefa": "catalogar_achado", "dia": dia, "resumo": str(r["resumo"])[:240], "destaques": (r.get("destaques") or [])[:3], "valido": True}


# ─────────────────────────────────────────────────────────────── ciclo
def ciclo(ia: IALocal | None = None, limite: int | None = None) -> dict:
    ia = ia or IALocal()
    hoje = date.today().isoformat()
    saida = PASTA / f"propostas-{hoje}.json"
    if not ia.disponivel():
        res = {"em": now_iso(), "disponivel": False, "nota": "servidor local não está de pé — rode ia_local/iniciar (bat|sh)"}
        PASTA.mkdir(parents=True, exist_ok=True); write_json(saida, res); return res
    limite = limite or CFG["limites"]["itens_por_ciclo"]
    from .fonte_edital import EXTRAIDOS
    import gzip
    an = load_json(ROOT / "dados/editais/analises.json") if (ROOT / "dados/editais/analises.json").exists() else {}
    dados = load_json(ROOT / "docs/dashboard-dados.json")
    universo = {e["id"]: e for e in (dados.get("editais") or [])}
    propostas = []
    # 1) registros em "análise incompleta" com texto disponível → classificar e extrair
    alvo = [eid for eid, a in an.items() if a.get("selo") == "analise_incompleta" and eid in universo][:limite]
    for eid in alvo:
        e = universo[eid]; tx = ROOT / "dados/editais/textos" / f"{eid}.txt.gz"
        texto = gzip.open(tx, "rt", encoding="utf-8").read() if tx.exists() else (e.get("objeto") or "")
        if len(texto) < 60:
            continue
        for fn in (t_classificar_objeto, t_extrair_objeto_prazo):
            p = fn(ia, e, texto)
            if p: propostas.append(p)
    # 2) léxico a partir de títulos validados
    ap = [universo[k].get("titulo") for k, a in an.items() if a.get("selo") == "conformidade" and k in universo][:40]
    rp = [universo[k].get("titulo") for k, a in an.items() if a.get("selo") == "inconformidade" and k in universo][:40]
    if ap and rp:
        p = t_propor_lexico(ia, [x for x in ap if x], [x for x in rp if x])
        if p: propostas.append(p)
    # 3) motores "lendo sem achar" → diagnóstico
    aud = load_json(ROOT / "estado/auditoria_motores.json") if (ROOT / "estado/auditoria_motores.json").exists() else {}
    rotas = load_json(ROOT / "config/rotas_motores.json").get("motores", {}) if (ROOT / "config/rotas_motores.json").exists() else {}
    esq = load_json(ROOT / "estado/esquadra.json").get("sensores", {}) if (ROOT / "estado/esquadra.json").exists() else {}
    for m in [x for x in aud.get("itens", []) if x["estado"] == "LENDO SEM ACHAR"][:8]:
        rm = rotas.get(m["id"], {})
        p = t_diagnosticar_rota(ia, {"id": m["id"], "nome": m["nome"], "perfil": rm.get("perfil"), "rotas": rm.get("rotas"),
                                     "diagnostico": (esq.get(m["id"]) or {}).get("diagnostico"), "lexico": rm.get("lexico_camada1") or []})
        if p: propostas.append(p)
    # 4) catalogar o achado do dia
    ach = load_json(ROOT / "docs/dados/achados_dia.json") if (ROOT / "docs/dados/achados_dia.json").exists() else {}
    d = (ach.get("dias") or {}).get(hoje)
    if d and d.get("total"):
        p = t_catalogar_achado(ia, hoje, d["motores"])
        if p: propostas.append(p)
    res = {"em": now_iso(), "disponivel": True, "modelo": ia.modelo, "total": len(propostas),
           "validas": sum(1 for p in propostas if p.get("valido")), "invalidas": sum(1 for p in propostas if not p.get("valido")),
           "por_tarefa": {t: sum(1 for p in propostas if p["tarefa"] == t) for t in CFG["tarefas_permitidas"]},
           "origem": CFG["validacao"]["origem"], "propostas": propostas}
    PASTA.mkdir(parents=True, exist_ok=True); write_json(saida, res)
    return {k: v for k, v in res.items() if k != "propostas"}


def aplicar(dia: str | None = None) -> dict:
    """Aplica só o que passou na validação: léxico → candidatos; rotas → sugestões; classificação → proposta no registro."""
    dia = dia or date.today().isoformat()
    arq = PASTA / f"propostas-{dia}.json"
    if not arq.exists():
        return {"aplicadas": 0, "nota": "sem propostas para o dia"}
    props = [p for p in load_json(arq).get("propostas", []) if p.get("valido")]
    from .fonte_edital import EXTRAIDOS
    n = {"classificacao": 0, "extracao": 0, "lexico": 0, "rotas": 0, "catalogo": 0}
    lex_p = ROOT / "config/lexico_aprendido.json"; lex = load_json(lex_p) if lex_p.exists() else {"positivos": {}, "vetos": {}, "candidatos": {}}
    rot_p = ROOT / "estado/rotas_sugeridas_ia.json"; rot = load_json(rot_p) if rot_p.exists() else {"sugestoes": []}
    cat_p = ROOT / "estado/catalogo_achados_ia.json"; cat = load_json(cat_p) if cat_p.exists() else {"dias": {}}
    for p in props:
        if p["tarefa"] in ("classificar_objeto", "extrair_objeto_prazo"):
            fp = EXTRAIDOS / f"{p['id']}.json"; ex = load_json(fp) if fp.exists() else {"edital_id": p["id"], "itens": {}}
            ex.setdefault("propostas_ia_local", []).append({**{k: v for k, v in p.items() if k != "id"}, "em": now_iso(), "origem": CFG["validacao"]["origem"]})
            if p["tarefa"] == "extrair_objeto_prazo":
                # entra como PROPOSTA no registro (campo próprio), nunca sobrescreve o que o titular ou o robô confirmou
                ex.setdefault("proposta_ia", {}).update({k: p[k] for k in ("objeto", "inicio", "fim") if p.get(k)})
                n["extracao"] += 1
            else:
                n["classificacao"] += 1
            write_json(fp, ex)
        elif p["tarefa"] == "propor_lexico":
            for x in p["positivos"]:
                lex.setdefault("candidatos", {}).setdefault(_norm(x["termo"]), {"tipo": "positivo", "origem": "ia_local", "exemplo": x.get("exemplo")})
            for x in p["vetos"]:
                lex.setdefault("candidatos", {}).setdefault(_norm(x["termo"]), {"tipo": "veto", "origem": "ia_local", "exemplo": x.get("exemplo")})
            n["lexico"] += len(p["positivos"]) + len(p["vetos"])
        elif p["tarefa"] == "diagnosticar_rota":
            rot["sugestoes"].append({**p, "em": now_iso(), "status": "a_confirmar_pelo_titular"}); n["rotas"] += 1
        elif p["tarefa"] == "catalogar_achado":
            cat["dias"][p["dia"]] = {"resumo": p["resumo"], "destaques": p["destaques"], "origem": "ia_local"}; n["catalogo"] += 1
    write_json(lex_p, lex); write_json(rot_p, rot); write_json(cat_p, cat)
    return {"dia": dia, "aplicadas": sum(n.values()), **n,
            "regra": "propostas entram como candidatos/sugestões/propostas — nunca sobrescrevem dado confirmado; a promoção do léxico segue a estatística do aprendizado"}


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "ciclo":
        print(json.dumps(ciclo(), ensure_ascii=False, indent=2))
    elif cmd == "aplicar":
        print(json.dumps(aplicar(), ensure_ascii=False, indent=2))
    else:
        ia = IALocal(); print(json.dumps({"servidor": ia.url, "disponivel": ia.disponivel(), "modelo_configurado": CFG["modelos"]["principal"]["nome"]}, ensure_ascii=False, indent=2))
