"""A curadoria de fontes que a regeneração não pode apagar.

O PROBLEMA QUE ESTE MÓDULO RESOLVE

`src/fontes260.py` reconstrói `config/fontes_captacao_260.json` a partir de
`estado/rotas_monitoramento.json` a cada regeneração de dados. Toda correção de
endereço feita à mão, toda fonte nova confirmada e toda armadilha registrada
eram gravadas nesse arquivo — e sumiam na regeneração seguinte, sem aviso e sem
rastro. Em 09/09/2026 o catálogo em produção tinha voltado a 260 fontes e ZERO
armadilhas, e o motor voltou a procurar o BNDES Periferias na busca do Diário
Oficial da União, onde a chamada não está.

Perder curadoria é pior que não tê-la: o sistema volta a errar exatamente onde
já havia aprendido, e ninguém percebe porque o arquivo continua parecendo certo.

A SOLUÇÃO

A curadoria mora em `config/curadoria_fontes.json`, que a regeneração NUNCA
escreve, e é reaplicada no fim de `fontes260.run()`. Regenerar deixou de ser
destrutivo: o que foi conferido à mão sobrevive a qualquer número de rodadas.

Três tipos de regra, todas idempotentes:
  regras         — corrigem o endereço de fontes que já existem, por id ou por
                   critério (uf, área, nível, trecho do nome do programa)
  fontes_novas   — fontes confirmadas que o relatório das 260 não conhecia
  armadilhas     — endereços que NÃO servem como fonte de prazo, com o motivo
                   medido, para que nenhuma rodada futura os reintroduza
"""
from __future__ import annotations

import json
from pathlib import Path

from .nucleo import ROOT

ARQUIVO = ROOT / "config/curadoria_fontes.json"
VAZIA = {"versao": 1, "regras": [], "fontes_novas": [], "armadilhas": []}


def carregar(caminho: Path | None = None) -> dict:
    caminho = caminho or ARQUIVO
    if not caminho.exists():
        return dict(VAZIA)
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    for chave in ("regras", "fontes_novas", "armadilhas"):
        dados.setdefault(chave, [])
    return dados


def gravar(dados: dict, caminho: Path | None = None) -> None:
    caminho = caminho or ARQUIVO
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _host(url: str) -> str:
    return url.split("//", 1)[-1].split("/", 1)[0]


def _casa(fonte: dict, quando: dict) -> bool:
    """A fonte atende ao critério da regra?

    Silêncio no critério significa 'qualquer valor'. `programa_contem` casa se
    QUALQUER dos trechos aparecer no nome do programa, em minúsculas.
    """
    if not quando:
        return False
    for campo in ("id", "uf", "area", "nivel", "tipo"):
        if campo in quando and fonte.get(campo) != quando[campo]:
            return False
    trechos = quando.get("programa_contem")
    if trechos:
        programa = (fonte.get("programa") or "").lower()
        if not any(t.lower() in programa for t in trechos):
            return False
    return True


def _sites(fonte: dict, topo: list, fim: list) -> int:
    atual = list(fonte.get("sites") or [])
    novos_topo = [u for u in topo if u not in atual]
    novos_fim = [u for u in fim if u not in atual and u not in novos_topo]
    if not novos_topo and not novos_fim:
        return 0
    fonte["sites"] = novos_topo + atual + novos_fim
    dominios = list(fonte.get("dominios") or [])
    for url in novos_topo + novos_fim:
        h = _host(url)
        if h not in dominios:
            dominios.append(h)
    fonte["dominios"] = dominios
    return len(novos_topo) + len(novos_fim)


def aplicar(pacote: dict, curadoria: dict | None = None) -> dict:
    """Reaplica a curadoria sobre um pacote de fontes recém-gerado.

    Devolve o relatório do que foi reaplicado. Não remove nada: só coloca o
    endereço conferido no topo, acrescenta o que falta e devolve as armadilhas.
    """
    cur = curadoria if curadoria is not None else carregar()
    fontes = pacote.setdefault("fontes", [])
    rel = {"fontes_corrigidas": [], "sites_reaplicados": 0,
           "fontes_novas": [], "armadilhas": 0}

    for regra in cur.get("regras", []):
        quando = regra.get("quando") or {}
        alvo = [f for f in fontes if _casa(f, quando)]
        if not alvo and quando.get("id"):
            rel.setdefault("regras_sem_alvo", []).append(quando["id"])
        for fonte in alvo:
            n = _sites(fonte, regra.get("sites_no_topo") or [],
                       regra.get("sites_acrescentar") or [])
            if regra.get("verificado_em"):
                fonte["verificado_em"] = regra["verificado_em"]
            if regra.get("nota") and not fonte.get("nota"):
                fonte["nota"] = regra["nota"]
            if n:
                rel["sites_reaplicados"] += n
                rel["fontes_corrigidas"].append(fonte["id"])

    programas = {f.get("programa") for f in fontes}
    ids = {f.get("id") for f in fontes}
    for nova in cur.get("fontes_novas", []):
        if nova.get("programa") in programas:
            continue
        registro = dict(nova)
        if registro.get("id") in ids or not registro.get("id"):
            raise ValueError(
                f"fonte curada sem id estável ou com id repetido: {registro.get('programa')!r}. "
                "O id tem de ser estável entre regenerações — use o prefixo 'curadoria-'.")
        registro.setdefault("padrao", {"natureza": registro.get("tipo"),
                                       "canal": "site_oficial",
                                       "confianca_rota": "primaria"})
        registro.setdefault("confianca_site", "confirmada")
        registro.setdefault("dominios", [_host(s) for s in registro.get("sites") or []])
        registro.setdefault("goias", (registro.get("uf") == "GO"))
        fontes.append(registro)
        ids.add(registro["id"])
        programas.add(registro.get("programa"))
        rel["fontes_novas"].append(registro["id"])

    if cur.get("armadilhas"):
        armadilhas = list(pacote.get("armadilhas") or [])
        urls = {a.get("url") for a in armadilhas}
        for arm in cur["armadilhas"]:
            if arm.get("url") not in urls:
                armadilhas.append(dict(arm))
                urls.add(arm.get("url"))
        pacote["armadilhas"] = armadilhas
        rel["armadilhas"] = len(armadilhas)

    resumo = pacote.setdefault("resumo", {})
    resumo["total"] = len(fontes)
    resumo["curadoria_reaplicada_em"] = cur.get("atualizada_em")
    resumo["armadilhas"] = len(pacote.get("armadilhas") or [])
    return rel


def registrar(regras=None, fontes_novas=None, armadilhas=None, atualizada_em=None,
              caminho: Path | None = None) -> dict:
    """Acrescenta curadoria ao arquivo, sem duplicar. Rodar quantas vezes quiser.

    A chave de identidade é: `quando` para regra, `programa` para fonte nova e
    `url` para armadilha. Id de fonte nova é atribuído aqui e nunca muda.
    """
    cur = carregar(caminho)
    novo = {"regras": 0, "fontes_novas": 0, "armadilhas": 0}

    for regra in regras or []:
        iguais = [r for r in cur["regras"] if r.get("quando") == regra.get("quando")]
        if iguais:
            alvo = iguais[0]
            for campo in ("sites_no_topo", "sites_acrescentar"):
                atual = alvo.setdefault(campo, [])
                for url in regra.get(campo) or []:
                    if url not in atual:
                        atual.append(url)
                        novo["regras"] += 1
            for campo in ("verificado_em", "motivo", "nota"):
                if regra.get(campo):
                    alvo[campo] = regra[campo]
        else:
            cur["regras"].append(dict(regra))
            novo["regras"] += 1

    existentes = {f.get("programa") for f in cur["fontes_novas"]}
    usados = {f.get("id") for f in cur["fontes_novas"]}
    prox = 1
    for nova in fontes_novas or []:
        if nova.get("programa") in existentes:
            continue
        registro = dict(nova)
        if not registro.get("id"):
            while f"curadoria-{prox:03d}" in usados:
                prox += 1
            registro["id"] = f"curadoria-{prox:03d}"
        usados.add(registro["id"])
        existentes.add(registro.get("programa"))
        cur["fontes_novas"].append(registro)
        novo["fontes_novas"] += 1

    urls = {a.get("url") for a in cur["armadilhas"]}
    for arm in armadilhas or []:
        if arm.get("url") not in urls:
            cur["armadilhas"].append(dict(arm))
            urls.add(arm.get("url"))
            novo["armadilhas"] += 1

    if atualizada_em:
        cur["atualizada_em"] = atualizada_em
    cur.setdefault("regra", (
        "esta é a curadoria que a regeneração de dados NÃO pode apagar. "
        "src/fontes260.py a reaplica no fim de cada regeneração. Endereço aqui "
        "só entra depois de conferido em fonte oficial, com a data da conferência."))
    gravar(cur, caminho)
    return novo
