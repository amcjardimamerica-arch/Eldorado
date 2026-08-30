"""Geração do pacote final de um caso do Farol.

Regra do titular: documentos de SUBMISSÃO não carregam orientações nem
qualquer referência a IA — saem prontos, em nome da entidade. Toda orientação
vai para o documento do presidente, objetiva e resumida. Documentos com
pendências ([PREENCHER]) não entram em `submissao/`: ficam em `rascunhos/` e
as pendências são listadas ao presidente."""
from __future__ import annotations

import re
from pathlib import Path

from .nucleo import now_iso

REFERENCIAS_IA = re.compile(
    r"(?i)(intelig[êe]ncia artificial|claude|chatgpt|gpt-?\d|openai|anthropic|"
    r"modelo de linguagem|\bllm\b|assistente virtual|gerado automaticamente|rascunho t[ée]cnico)"
)
# acrônimos apenas em maiúsculas, para não confundir com o verbo "ia"
ACRONIMOS_IA = re.compile(r"(?<![A-Za-zÀ-ÿ])(IA|AI)(?![A-Za-zÀ-ÿ])")
PENDENCIA = re.compile(r"\[(?:PREENCHER|TRANSCREVER|M\d|I\d)[^\]]*\]")

def avaliar_limpeza(texto: str) -> list[str]:
    problemas = []
    achado = REFERENCIAS_IA.search(texto) or ACRONIMOS_IA.search(texto)
    if achado:
        problemas.append(f"referência vedada no texto: “{achado.group(0)}”")
    pendencias = PENDENCIA.findall(texto)
    if pendencias:
        problemas.append(f"{len(pendencias)} campo(s) pendente(s) de preenchimento")
    return problemas

def _unico(path: Path) -> Path:
    """Nunca sobrescrever: se já existe, versiona com sufixo numérico."""
    if not path.exists():
        return path
    for n in range(2, 100):
        alternativa = path.with_name(f"{path.stem}_v{n}{path.suffix}")
        if not alternativa.exists():
            return alternativa
    raise ValueError(f"versões demais para {path.name}")

def gerar(case_root: Path, documentos: dict[str, str]) -> dict:
    """documentos: {nome_arquivo.md: conteúdo}. Devolve manifesto do que foi
    aceito em submissao/ e do que ficou em rascunhos/ com os motivos."""
    submissao = case_root / "submissao"; rascunhos = case_root / "rascunhos"
    manifesto = {"gerado_em": now_iso(), "prontos": [], "rascunhos": []}
    for nome, conteudo in documentos.items():
        conteudo = conteudo.strip() + "\n"
        problemas = avaliar_limpeza(conteudo)
        destino_dir = submissao if not problemas else rascunhos
        destino_dir.mkdir(parents=True, exist_ok=True)
        destino = _unico(destino_dir / nome)
        destino.write_text(conteudo, encoding="utf-8")
        registro = {"arquivo": str(destino.relative_to(case_root))}
        if problemas:
            registro["pendencias"] = problemas
            manifesto["rascunhos"].append(registro)
        else:
            manifesto["prontos"].append(registro)
    return manifesto

def render_parecer_conselho(consolidado: dict, decisao: dict) -> str:
    linhas = ["# Parecer do Conselho", "",
              f'- Decisão: **{decisao.get("decisao", "?").replace("_", " ")}**',
              f'- Data: {now_iso()}', ""]
    for motivo in decisao.get("motivos", [])[:6]:
        linhas.append(f"- {motivo}")
    linhas += ["", "## As sete lentes", ""]
    for c in consolidado.get("conselheiros", []):
        linhas.append(f'### {c["ponto_de_vista"].replace("_", " ")} — {c["personalidade"]}')
        if c.get("vantagens"):
            linhas.append("Vantagens: " + "; ".join(str(v) for v in c["vantagens"][:4]) + ".")
        if c.get("desvantagens"):
            linhas.append("Desvantagens: " + "; ".join(str(v) for v in c["desvantagens"][:4]) + ".")
        if c.get("recomendacao"):
            linhas.append(f'Recomendação desta lente: {c["recomendacao"]}.')
        linhas.append("")
    return "\n".join(linhas)

def render_pacote_presidente(profile: dict, opp: dict, decisao: dict, manifesto: dict, prazo: str | None) -> str:
    decisao_txt = decisao.get("decisao", "?").replace("_", " ")
    linhas = [f'# Ao Presidente — {opp.get("titulo", "")[:120]}', "",
              f'**Decisão do conselho: {decisao_txt}.**', ""]
    if decisao.get("motivos"):
        linhas.append("Por quê: " + " ".join(str(m) for m in decisao["motivos"][:4]))
        linhas.append("")
    if prazo:
        linhas += [f"**Prazo do edital: {prazo}.**", ""]
    if decisao.get("condicoes"):
        linhas.append("## Condições para participar")
        linhas += [f"- {c}" for c in decisao["condicoes"][:8]] + [""]
    if manifesto.get("prontos"):
        linhas.append("## Documentos prontos para conferir e assinar")
        linhas += [f'- {d["arquivo"]}' for d in manifesto["prontos"]] + [""]
    if manifesto.get("rascunhos"):
        linhas.append("## Pendências antes da submissão")
        for d in manifesto["rascunhos"]:
            linhas.append(f'- {d["arquivo"]}: ' + "; ".join(d.get("pendencias", [])))
        linhas.append("")
    if decisao.get("orientacoes_presidente"):
        linhas.append("## Orientações")
        linhas += [f"- {o}" for o in decisao["orientacoes_presidente"][:10]] + [""]
    linhas += ["## Regras de ouro",
               "- Conferir a versão vigente do edital e retificações na fonte oficial antes de assinar.",
               "- Nenhuma declaração sem prova arquivada; despesa nasce ligada a meta, rubrica e evidência.",
               "- Este pacote é preparatório: a decisão final e as assinaturas são da diretoria.", ""]
    return "\n".join(linhas)
