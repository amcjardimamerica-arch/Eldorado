"""Pertinência ao terceiro setor — o filtro que toda oportunidade atravessa.

Regra do titular: só entra no monitoramento, nas fontes com edital aberto e
no banco o que uma associação, ONG ou entidade do terceiro setor pode
aproveitar — captação de recursos, premiação, capacitação, ou qualquer coisa
que envolva o terceiro setor. Edital voltado a empresas (fornecimento,
credenciamento de prestadores, pregão, registro de preços, obras, concurso
público) é desqualificado e ELIMINADO da base.

Combina os dois filtros já existentes, na ordem certa:
  1. léxico do terceiro setor (`lexico.casar`) — o texto fala de OSC/edital de
     fomento? Se não fala nem de entidade nem de instrumento, sai;
  2. destinação (`destinacao.avaliar_destinacao`) — natureza do recurso;
     empresa/comercial sai, prêmio/capacitação para OSC fica.
E acrescenta o veto explícito a termos empresariais fortes que nem o léxico
nem a destinação pegam sozinhos ("credenciamento de farmácia", "prestação de
serviços de ...", "aquisição").
"""
from __future__ import annotations

import json
import re

from .destinacao import avaliar_destinacao
from .lexico import casar
from .nucleo import ROOT, carregar_oportunidades, now_iso, write_json

_EMPRESA = re.compile(
    r"credenciamento\s+(?:e\s+a?\s*contrata[çc][ãa]o\s+)?de\s+(farm[áa]cia|drogaria|cl[íi]nica|laborat[óo]rio|leiloeir|prestador|"
    r"fornecedor|empresa|pessoas?\s+(?:f[íi]sicas?\s+e\s+)?jur[íi]dicas?|operador|profissionais?\s+(?:aut[ôo]nom|de\s+sa[úu]de)|"
    r"m[ée]dic|dentist|psic[óo]log|leil)|"
    r"credenciamento\s+de\s+pessoa\s+f[íi]sica|comodato|operador\s+de\s+m[áa]quina|"
    r"pessoas?\s+jur[íi]dicas?[^.]{0,25}?para\s+(?:a\s+)?(?:presta|fornec|execu|realiza)|"
    r"(?:prestador|contrata[çc][ãa]o|credenciamento)[^.]{0,45}?pessoas?\s+jur[íi]dica|"
    r"cotas?\s+de\s+patroc[íi]nio\s+de\s+empresas|patroc[íi]nio\s+de\s+empresas\s+\(pessoa|"
    r"presta[çc][ãa]o\s+de\s+servi[çc]os?\s+de\s+(?!assist[êe]ncia|acolhimento|prote[çc][ãa]o)|"
    r"aquisi[çc][ãa]o\s+de|fornecimento\s+de|registro\s+de\s+pre[çc]os|menor\s+pre[çc]o|"
    r"preg[ãa]o|tomada\s+de\s+pre[çc]os|concorr[êe]ncia\s+p[úu]blica\s+n|licita[çc][ãa]o|contrata[çc][ãa]o\s+de\s+empresa|"
    r"execu[çc][ãa]o\s+de\s+obra|pavimenta|concurso\s+p[úu]blico\s+para\s+provimento|processo\s+seletivo\s+simplificado|"
    r"leil[ãa]o|aliena[çc][ãa]o\s+de\s+bens|loca[çc][ãa]o\s+de\s+(im[óo]vel|ve[íi]culo)|manuten[çc][ãa]o\s+de", re.I)
_TERCEIRO_SETOR_FORTE = re.compile(
    r"organiza[çc][õo]es?\s+da\s+sociedade\s+civil|\bOSCs?\b|sem\s+fins\s+lucrativos|termo\s+de\s+(fomento|colabora)|"
    r"13\.?019|entidades?\s+(social|assistencial|filantr|benefic|sem\s+fins)|associa[çc][õo]es?\s+(de\s+moradores|comunit|de\s+bairro|sem\s+fins|civil)|"
    r"funda[çc][ãa]o\s+privada|\bONGs?\b|projetos?\s+(sociais|culturais|esportivos)|fomento\s+(a|de|à)\s+projetos|"
    r"premia[çc][ãa]o|pr[êe]mio|capacita[çc][ãa]o\s+(de|para)\s+(entidades|organiza|gestores|conselheiros)", re.I)


_VETO_ABSOLUTO = re.compile(
    r"(?:credenciamento|contrata[çc][ãa]o|cadastramento)[^.]{0,60}?pessoas?\s+jur[íi]dicas?[^.]{0,30}?para\s+(?:a\s+)?(?:presta|fornec|execu|realiza)|"
    r"credenciamento\s+(?:e\s+a?\s*contrata[çc][ãa]o\s+)?de\s+(?:farm[áa]cia|drogaria|cl[íi]nica|laborat[óo]rio|leiloeir|empresa)|"
    r"preg[ãa]o|registro\s+de\s+pre[çc]os|menor\s+pre[çc]o|comodato|cotas?\s+de\s+patroc[íi]nio\s+de\s+empresas", re.I)
_OSC_EXPLICITA = re.compile(r"sem\s+fins\s+lucrativos|organiza[çc][õo]es?\s+da\s+sociedade\s+civil|\bOSCs?\b|13\.?019|termo\s+de\s+(fomento|colabora)", re.I)


def pertinente(item: dict) -> dict:
    """Veredito único: {'ok': bool, 'motivo': str, 'natureza': str|None}."""
    texto = f'{item.get("titulo") or ""} {item.get("objeto") or ""} {(item.get("evidencia") or "")[:600]}'
    # documento enviado pelo titular é fonte máxima: nunca se descarta
    if item.get("origem") == "alimentacao_manual" or item.get("sem_edital") or item.get("janela_confirmada"):
        return {"ok": True, "motivo": "fonte do titular / regra anual", "natureza": "recurso"}
    # veto absoluto: contratar/credenciar pessoa jurídica para prestar ou fornecer
    # é edital de empresa, mesmo que o texto fale de cultura ou projetos
    if _VETO_ABSOLUTO.search(texto) and not _OSC_EXPLICITA.search(texto):
        return {"ok": False, "motivo": "credenciamento/contratação de pessoa jurídica ou certame de preço — edital para empresas", "natureza": None}
    forte = bool(_TERCEIRO_SETOR_FORTE.search(texto))
    if _EMPRESA.search(texto) and not forte:
        return {"ok": False, "motivo": "edital voltado a empresas/fornecedores — fora do terceiro setor", "natureza": None}
    lx = casar(texto)
    if not lx["candidato"] and not forte:
        return {"ok": False, "motivo": "sem pertinência com associações, ONGs ou entidades do terceiro setor", "natureza": None}
    dest = avaliar_destinacao(item)
    if dest.get("elegivel") is False:
        return {"ok": False, "motivo": dest.get("motivo") or "destinação incompatível", "natureza": dest.get("natureza")}
    return {"ok": True, "motivo": dest.get("motivo") or "pertinente ao terceiro setor", "natureza": dest.get("natureza") or "recurso"}


def limpar_base() -> dict:
    """Aplica o filtro à base de oportunidades: o que não é do terceiro setor
    sai do JSONL (fica só um registro do descarte para auditoria)."""
    db = ROOT / "dados/oportunidades/oportunidades.jsonl"
    itens = carregar_oportunidades()
    mantidos, descartados = {}, []
    for oid, it in itens.items():
        v = pertinente(it)
        if v["ok"]:
            it["pertinencia"] = {"ok": True, "motivo": v["motivo"], "em": now_iso()}
            mantidos[oid] = it
        else:
            descartados.append({"id": oid, "titulo": (it.get("titulo") or "")[:120],
                                "fonte": it.get("fonte_nome"), "motivo": v["motivo"]})
    db.parent.mkdir(parents=True, exist_ok=True)
    db.write_text("".join(json.dumps(x, ensure_ascii=False, separators=(",", ":")) + "\n"
                          for x in sorted(mantidos.values(), key=lambda v: v["id"])), encoding="utf-8")
    # campanhas de completude dos descartados também saem
    from . import completude as _comp
    est = _comp._estado()
    antes = len(est.get("campanhas", {}))
    for d in descartados:
        est.get("campanhas", {}).pop(d["id"], None)
    _comp._salvar(est) if hasattr(_comp, "_salvar") else write_json(_comp.ESTADO, est)
    rel = {"em": now_iso(), "mantidos": len(mantidos), "descartados": len(descartados),
           "campanhas_removidas": antes - len(est.get("campanhas", {})),
           "amostra_descartados": descartados[:40],
           "regra": "só oportunidades aproveitáveis por associações/OSCs ficam na base; editais para empresas são eliminados"}
    write_json(ROOT / "estado/pertinencia.json", rel)
    return rel


if __name__ == "__main__":
    print(json.dumps(limpar_base(), ensure_ascii=False, indent=2)[:2000])
