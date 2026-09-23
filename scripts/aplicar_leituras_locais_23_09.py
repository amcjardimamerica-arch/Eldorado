#!/usr/bin/env python3
"""AS 14 LEITURAS DO NAVEGADOR LOCAL — 23/09/2026.

O pacote de fechamento trouxe o arquivo com as leituras, mas copiá-lo para `docs/dados` não
faz nada por si: o motor não lê aquele arquivo, lê os registros. Enquanto a leitura não
descer até eles, o sistema continua com o prazo velho — e a próxima varredura reverifica o
que o titular já verificou à mão.

O que desce daqui:

    prazo com HORA      Formosa encerrou 22/07 às 16h45, não "em 22/07". A diferença decide
                        se um edital ainda está aberto na tarde do último dia.
    página oficial      o arquivo que o PRÓPRIO ÓRGÃO anexou, não a página de divulgação do
                        PNCP. Divulgação serve para descobrir o processo, nunca para
                        confirmar prazo.
    chave corrigida     Osório apontava para um registro inexistente (HTTP 400). A chave
                        verdadeira veio da busca oficial.
    dois registros novos  Planaltina/GO Esporte 2026 e Cultura 2025, que nenhuma rodada
                        anterior tinha capturado.

Nada é estimado: campo sem confirmação fica nulo, com o motivo escrito.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.nucleo import chave_curta  # noqa: E402

LEITURAS = RAIZ / "docs/dados/verificacao_fechamento_2026-09-23.json"
ANALISES = RAIZ / "dados/editais/analises.json"
EXTRAIDOS = RAIZ / "dados/editais/extraidos"
OPORT = RAIZ / "biblioteca_alexandria/oportunidades"
REGISTRO = RAIZ / "estado/leituras_locais_23_09_aplicadas.json"

# O que a leitura traz e o registro deve passar a ter.
CAMPOS = ("objeto", "inicio", "fim", "hora_encerramento", "pagina_oficial", "chave_pncp",
          "orgao", "uf", "situacao", "observacao", "anexos", "titulo")


def aplicar(seco: bool = False) -> dict:
    v = json.loads(LEITURAS.read_text(encoding="utf-8"))["itens"]
    an = json.loads(ANALISES.read_text(encoding="utf-8"))
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # índice por chave curta: as bases nunca combinaram como guardar o id, e é por isso que
    # a chave_curta existe. Sem ela, metade destas leituras não acharia o registro.
    idx_an = {chave_curta(k): k for k in an}
    fichas = {}
    for f in OPORT.glob("*/*/ficha.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if d.get("id"):
            fichas[chave_curta(d["id"])] = f

    res = {"em": agora, "seco": seco, "aplicadas": 0, "novos": [], "onde": {},
           "corrigiu_chave": [], "com_hora": 0}

    for cid, leitura in v.items():
        c = chave_curta(cid)
        campos = {k: leitura[k] for k in CAMPOS if leitura.get(k) not in (None, "")}
        campos.update({
            "verificado_em": "2026-09-23",
            "verificado_por": "navegador local do titular — API oficial de consulta do PNCP",
            "fonte_do_prazo": ("arquivo anexado pelo próprio órgão" if leitura.get("pagina_oficial")
                               else "não confirmado"),
            "divulgacao_nao_vale": "a página de divulgação do PNCP serve para descobrir o "
                                   "processo e o órgão, nunca para confirmar prazo"})
        if leitura.get("hora_encerramento"):
            res["com_hora"] += 1
        tocou = []

        # A CHAVE ERRADA VIVE EM VÁRIOS ARQUIVOS. Osório apontava para 88866396000155/2026/122,
        # que devolve HTTP 400 — registro inexistente. Trocar só numa base deixaria as outras
        # apontando para o vazio, e a próxima varredura voltaria a usar a errada.
        velha = None
        obs = str(leitura.get("observacao") or "")
        if "CHAVE CORRIGIDA" in obs:
            import re as _re
            m = _re.search(r"apontava (?:para )?(\d{14}/\d{4}/\d+)", obs)
            velha = m.group(1) if m else None
            if velha:
                campos["chave_pncp_anterior"] = velha
                campos["porque_mudou"] = ("a chave anterior devolvia HTTP 400: registro inexistente. "
                                          "A verdadeira veio da busca oficial do PNCP")
                res["corrigiu_chave"].append(c)
                for arq in (ANALISES, RAIZ / "dados/editais/marcacoes_ia.json"):
                    if arq.exists() and not seco:
                        bruto = arq.read_text(encoding="utf-8")
                        if velha in bruto:
                            arq.write_text(bruto.replace(velha, str(leitura.get("chave_pncp") or "")),
                                           encoding="utf-8")

        chave_an = idx_an.get(c)
        if chave_an:
            an[chave_an].update(campos)
            tocou.append("analises")
        else:
            # REGISTRO NOVO NASCE COM O ESQUEMA DO ACERVO. Um registro sem 'selo' e sem
            # 'verificacoes' existe no arquivo mas nenhuma rotina que percorre o acervo
            # consegue lê-lo — e quebra as que esperam o campo.
            verif = {"objeto": bool(leitura.get("objeto")),
                     "prazo": bool(leitura.get("fim")),
                     "site_oficial": bool(leitura.get("pagina_oficial"))}
            completo = all(verif.values())
            an[cid] = {**campos,
                       "selo": "conformidade" if completo else "analise_incompleta",
                       "em": agora, "completo": completo, "verificacoes": verif,
                       "por": "leitura no navegador local do titular (23/09/2026)",
                       "modelo": "leitura direta na fonte, sem modelo",
                       "motivo": (f"{'aprovado' if completo else 'incompleto'} · "
                                  f"{leitura.get('situacao') or 'encerrado'}"),
                       "origem": "leitura local 23/09: registro novo, nenhuma rodada anterior "
                                 "o havia capturado",
                       "ativo": True}
            res["novos"].append(cid)
            tocou.append("analises(novo)")

        for nome in (cid, c):
            e = EXTRAIDOS / f"{nome}.json"
            if e.exists():
                try:
                    d = json.loads(e.read_text(encoding="utf-8"))
                    d.update(campos)
                    if not seco:
                        e.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
                    tocou.append("extraidos")
                except Exception:
                    pass
                break

        f = fichas.get(c)
        if f:
            d = json.loads(f.read_text(encoding="utf-8"))
            d.update(campos)
            if not seco:
                f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
            tocou.append("ficha")

        res["onde"][c] = tocou
        res["aplicadas"] += 1

    if not seco:
        ANALISES.write_text(json.dumps(an, ensure_ascii=False, indent=1), encoding="utf-8")
        REGISTRO.parent.mkdir(parents=True, exist_ok=True)
        REGISTRO.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    return res


if __name__ == "__main__":
    r = aplicar(seco="--seco" in sys.argv)
    print(f"leituras aplicadas: {r['aplicadas']} · com hora exata: {r['com_hora']}")
    print(f"registros novos: {len(r['novos'])} — {', '.join(r['novos'])}")
    print(f"chave corrigida: {', '.join(r['corrigiu_chave']) or 'nenhuma'}")
    fora = [c for c, t in r["onde"].items() if not t]
    if fora:
        print(f"sem destino: {', '.join(fora)}")
