"""Conformidade de edital oficial — determinística, sem IA e sem tokens.

Cada registro coletado é medido contra `config/padroes_edital.json`:

1. **Obrigatórios do registro** — falta de qualquer um reprova o registro.
2. **Conteúdo mínimo do edital** (base: Lei 13.019/2014, art. 24, §1º) — objeto,
   prazo, valor, critérios, habilitação, instrumento e contrapartida.
3. **Sinais de oficialidade** — domínio catalogado, numeração do ato, data de
   publicação, órgão emissor e anexos.

O que não está no texto vira **pendência declarada**, nunca preenchimento
automático. A nota é explicável: cada ponto informa o termo que o sustentou.
"""
from __future__ import annotations

import json
import re

from .nucleo import ROOT, load_json, now_iso, write_json

def _cfg() -> dict:
    return load_json(ROOT / "config/padroes_edital.json")

def _texto_do_registro(item: dict) -> str:
    partes = [str(item.get(c) or "") for c in ("titulo", "evidencia", "texto_primario", "resumo_fonte")]
    return " ".join(partes).lower()

def _achou(texto: str, termos: list[str]) -> str | None:
    for termo in termos:
        if termo.lower() in texto:
            return termo
    return None

def avaliar(item: dict, cfg: dict | None = None) -> dict:
    """Avalia um registro. Devolve nota 0–100, itens atendidos e pendências."""
    cfg = cfg or _cfg()
    texto = _texto_do_registro(item)
    faltando_obrigatorio = []
    for regra in cfg["obrigatorios_registro"]:
        valor = item.get(regra["campo"])
        if regra["campo"] == "titulo":
            ok = bool(valor) and len(str(valor).strip()) >= 10
        else:
            ok = bool(valor)
        if not ok:
            faltando_obrigatorio.append(regra["campo"])

    conteudo, pendencias_conteudo, nota_conteudo, peso_conteudo = [], [], 0, 0
    for regra in cfg["conteudo_minimo_edital"]:
        peso_conteudo += regra["peso"]
        termo = _achou(texto, regra["termos"])
        if termo:
            nota_conteudo += regra["peso"]
            conteudo.append({"id": regra["id"], "rotulo": regra["rotulo"], "evidencia_termo": termo})
        else:
            pendencias_conteudo.append({"id": regra["id"], "rotulo": regra["rotulo"]})

    oficialidade, pendencias_oficial, nota_oficial, peso_oficial = [], [], 0, 0
    for regra in cfg["sinais_de_oficialidade"]:
        peso_oficial += regra["peso"]
        ok, evidencia = False, None
        if regra["id"] == "dominio_oficial":
            ok = bool(item.get("url", "").startswith("https://")) and bool(item.get("fonte_id"))
            evidencia = item.get("fonte_id")
        elif regra["id"] == "identificacao_do_ato":
            achado = re.search(regra["regex"], texto, re.I)
            ok, evidencia = bool(achado), achado.group(0)[:80] if achado else None
        elif regra["id"] == "data_publicacao":
            ok = bool(item.get("data_publicacao") or item.get("ano_referencia"))
            evidencia = item.get("data_publicacao") or item.get("ano_referencia")
        elif regra["id"] == "orgao_emissor":
            ok = bool(item.get("fonte_nome"))
            evidencia = item.get("fonte_nome")
        else:
            evidencia = _achou(texto, regra.get("termos", []))
            ok = bool(evidencia)
        if ok:
            nota_oficial += regra["peso"]
            oficialidade.append({"id": regra["id"], "rotulo": regra["rotulo"], "evidencia_termo": evidencia})
        else:
            pendencias_oficial.append({"id": regra["id"], "rotulo": regra["rotulo"]})

    nota = round((nota_conteudo / peso_conteudo * 60) + (nota_oficial / peso_oficial * 40)) if peso_conteudo and peso_oficial else 0
    faixas = cfg["faixas_qualidade"]
    if faltando_obrigatorio:
        classe, nota = "reprovado", 0
    elif nota >= faixas["completo"]:
        classe = "completo"
    elif nota >= faixas["suficiente"]:
        classe = "suficiente"
    elif nota >= faixas["insuficiente"]:
        classe = "insuficiente"
    else:
        classe = "apenas_indicio"
    return {
        "nota": nota,
        "classe": classe,
        "obrigatorios_faltando": faltando_obrigatorio,
        "conteudo_atendido": conteudo,
        "conteudo_pendente": pendencias_conteudo,
        "oficialidade_atendida": oficialidade,
        "oficialidade_pendente": pendencias_oficial,
        "avaliado_em": now_iso(),
        "regra": "Nota = 60% conteúdo mínimo (Lei 13.019/2014, art. 24, §1º) + 40% sinais de oficialidade. Pendência é lacuna declarada, nunca preenchida por inferência.",
    }

def run() -> dict:
    from .nucleo import carregar_oportunidades, gravar_oportunidades
    cfg = _cfg()
    registros = carregar_oportunidades()
    resumo = {"executado_em": now_iso(), "avaliados": 0, "por_classe": {}, "nota_media": 0}
    soma = 0
    for item in registros.values():
        resultado = avaliar(item, cfg)
        item["qualidade"] = resultado
        resumo["avaliados"] += 1
        resumo["por_classe"][resultado["classe"]] = resumo["por_classe"].get(resultado["classe"], 0) + 1
        soma += resultado["nota"]
    resumo["nota_media"] = round(soma / resumo["avaliados"], 1) if resumo["avaliados"] else 0
    gravar_oportunidades(registros)
    write_json(ROOT / "estado/qualidade.json", resumo)
    return resumo

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
