"""Fase 2 · CONFIRMAR aplicada ao acervo catalogado.

A fase 1 identificou e classificou. Esta fase confere, item a item, o que a
evidência coletada **efetivamente comprova** — e o que apenas menciona sem
provar. Nada é buscado na rede aqui: é a conferência documental do material já
capturado, que decide o nível de confirmação de cada edital.

Níveis de confirmação:
  · `confirmado_documental` — objeto, prazo e ao menos um requisito constam do
    texto capturado; serve de referência sem ressalva
  · `parcial` — parte dos elementos consta; o que falta é declarado
  · `pendente` — só a ementa; entra na fila de busca do ato/edital integral

Cada edital recebe um checklist com o resultado de cada verificação e o motivo.
Regra dura: item não comprovado é registrado como não comprovado — jamais
presumido.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import date

from .biblioteca import OPORTUNIDADES
from .nucleo import ROOT, load_json, now_iso, write_json

SAIDA = ROOT / "estado/confirmacao"

_OBJETO = re.compile(
    r"\bobjeto\b|\bfinalidade\b|\bdestina\w*\s+a\b|\bvisa\b|para\s+(?:a\s+)?"
    r"(?:execu[çc][ãa]o|realiza[çc][ãa]o|contrata[çc][ãa]o|presta[çc][ãa]o)", re.I)
_ANEXO = re.compile(r"\banexos?\b|\bmodelos?\b|\bformul[áa]rios?\b|\bap[êe]ndice\b", re.I)
_VALOR = re.compile(r"R\$\s?[\d.]{3,}", re.I)
_ORGAO = re.compile(
    r"prefeitura|munic[íi]pio|secretaria|minist[ée]rio|funda[çc][ãa]o|instituto|"
    r"governo|conselho|fundo\b", re.I)
_INSCRICAO = re.compile(r"inscri[çc][õo]es|protocolo|entrega\s+d[ao]s?\s+(?:envelope|proposta)|"
                        r"habilita[çc][ãa]o", re.I)


def conferir(ficha: dict) -> dict:
    """Checklist da fase 2 sobre uma ficha já catalogada."""
    texto = " ".join(str(ficha.get(c) or "") for c in ("titulo", "evidencia"))
    itens = {
        "objeto_identificado": bool(_OBJETO.search(texto)),
        "orgao_identificado": bool(_ORGAO.search(texto)) or bool(ficha.get("financiador")),
        "prazo_publicado": bool(ficha.get("fim")),
        "periodo_completo": bool(ficha.get("inicio") and ficha.get("fim")),
        "requisitos_no_texto": bool(ficha.get("exigencias_detectadas")),
        "valor_publicado": bool(ficha.get("valores_citados")) or bool(_VALOR.search(texto)),
        "anexos_mencionados": bool(_ANEXO.search(texto)),
        "forma_de_inscricao": bool(_INSCRICAO.search(texto)),
        "territorio_definido": bool(ficha.get("uf")),
        "esfera_definida": ficha.get("nivel") in ("federal", "estadual", "municipal"),
        "url_primaria": bool(ficha.get("url")),
        "evidencia_hasheada": bool(ficha.get("hash_evidencia")),
    }
    # REGRA DO TITULAR: o MÍNIMO aceitável é prazo + objeto. Abaixo disso o
    # edital não serve para decidir nada. Acima, a busca continua até a
    # totalidade — o nível diz exatamente onde parou.
    MINIMO = ("objeto_identificado", "prazo_publicado")
    tem_minimo = all(itens[k] for k in MINIMO)
    total_ok = sum(1 for v in itens.values() if v)
    if total_ok == len(itens):
        nivel = "completo"
    elif tem_minimo and itens["requisitos_no_texto"] and itens["orgao_identificado"]:
        nivel = "confirmado_documental"
    elif tem_minimo:
        nivel = "minimo_util"          # dá para decidir concorrer; falta detalhe
    elif itens["objeto_identificado"] or itens["prazo_publicado"]:
        nivel = "parcial"
    else:
        nivel = "pendente"

    nao_comprovados = [k for k, v in itens.items() if not v]
    motivos = {
        "objeto_identificado": "objeto do certame não descrito na evidência",
        "prazo_publicado": "prazo final não publicado no trecho capturado",
        "periodo_completo": "abertura das inscrições não declarada",
        "requisitos_no_texto": "requisitos não detalhados (ementa de diário)",
        "valor_publicado": "valor não publicado na evidência",
        "anexos_mencionados": "edital não menciona anexos no trecho capturado",
        "forma_de_inscricao": "forma de inscrição/protocolo não descrita",
        "territorio_definido": "UF não identificada no registro",
        "orgao_identificado": "órgão promotor não identificado",
        "esfera_definida": "esfera não classificada",
        "url_primaria": "sem URL primária",
        "evidencia_hasheada": "evidência sem hash",
    }
    # o que buscar em seguida, na ordem que mais aproxima da totalidade
    ordem = ("prazo_publicado", "objeto_identificado", "requisitos_no_texto",
             "periodo_completo", "valor_publicado", "anexos_mencionados",
             "forma_de_inscricao")
    proximos = [k for k in ordem if not itens[k]][:3]
    return {
        "nivel_confirmacao": nivel,
        "tem_minimo": tem_minimo,
        "itens_ok": total_ok, "itens_total": len(itens),
        "completude_pct": round(total_ok / len(itens) * 100),
        "proximo_alvo": proximos,
        "continuar_busca": nivel != "completo",
        "itens": itens,
        "comprovados": [k for k, v in itens.items() if v],
        "nao_comprovados": [{"item": k, "motivo": motivos.get(k, k)}
                            for k in nao_comprovados],
        "precisa_ato_integral": nivel not in ("completo", "confirmado_documental"),
        "conferido_em": now_iso(),
        "nota": ("conferência documental do material capturado; item não "
                 "comprovado nunca é presumido"),
    }


def run(limite: int | None = None) -> dict:
    """Aplica a fase 2 a todo o acervo — em pasta e no banco."""
    from .banco import conectar
    con = conectar()
    linhas = con.execute("SELECT chave, ano, id, ficha FROM historico").fetchall()
    if limite:
        linhas = linhas[:limite]
    niveis: Counter = Counter()
    pendentes = []
    atualizados = 0
    with con:
        con.execute("CREATE TABLE IF NOT EXISTS confirmacao ("
                    "chave TEXT, ano TEXT, id TEXT, nivel TEXT, itens TEXT, "
                    "nao_comprovados TEXT, precisa_ato_integral INTEGER, "
                    "PRIMARY KEY (chave, ano, id))")
        for chave, ano, cid, fj in linhas:
            ficha = json.loads(fj)
            conf = conferir(ficha)
            niveis[conf["nivel_confirmacao"]] += 1
            con.execute("INSERT OR REPLACE INTO confirmacao VALUES (?,?,?,?,?,?,?)",
                        (chave, ano, cid, conf["nivel_confirmacao"],
                         json.dumps(conf["itens"], ensure_ascii=False),
                         json.dumps(conf["nao_comprovados"], ensure_ascii=False),
                         int(conf["precisa_ato_integral"])))
            ficha["confirmacao"] = conf
            con.execute("UPDATE historico SET ficha=? WHERE chave=? AND ano=? AND id=?",
                        (json.dumps(ficha, ensure_ascii=False), chave, ano, cid))
            atualizados += 1
            if conf["precisa_ato_integral"] and len(pendentes) < 300:
                pendentes.append({"chave": chave, "ano": ano, "url": ficha.get("url"),
                                  "faltam": [n["item"] for n in conf["nao_comprovados"][:4]]})
            # a pasta, quando existe, também recebe o checklist
            pasta = OPORTUNIDADES / chave / ano
            if (pasta / "ficha.json").exists():
                write_json(pasta / "confirmacao.json", conf)
    con.close()
    resumo = {"executado_em": now_iso(), "conferidos": atualizados,
              "por_nivel": dict(niveis),
              "com_minimo_util": niveis.get("minimo_util", 0) + niveis.get("confirmado_documental", 0) + niveis.get("completo", 0),
              "meta": "mínimo = prazo + objeto; a busca segue até a totalidade dos 12 itens",
              "fila_ato_integral": len(pendentes),
              "amostra_fila": pendentes[:20],
              "nota": ("fase 2 documental: confirma o que a evidência prova. "
                       "O que exige o edital integral entra na fila da campanha "
                       "de completude (30 dias) do Eldorado.")}
    SAIDA.mkdir(parents=True, exist_ok=True)
    write_json(SAIDA / "resumo.json", resumo)
    write_json(SAIDA / "fila_ato_integral.json",
               {"gerado_em": now_iso(), "total": len(pendentes), "itens": pendentes})
    return resumo


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2)[:1800])
