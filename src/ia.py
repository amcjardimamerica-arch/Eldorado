"""Adaptador único de IA (Anthropic), biblioteca-padrão apenas.

Princípios: (1) IA só em etapa essencial; (2) o modelo é escolhido POR TAREFA
em config/ia.json (env sobrepõe o padrão); (3) sem credencial => erro limpo
`SemCredencial`, nunca simulação; (4) todo uso é auditado em estado/ia_uso.jsonl;
(5) nenhum dado proibido (config ia.json → dados_proibidos) sai do repositório."""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request

from .nucleo import ROOT, append_jsonl, load_json, now_iso

API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"

class SemCredencial(RuntimeError):
    pass

def _cfg() -> dict:
    return load_json(ROOT / "config/ia.json")

def credencial() -> str | None:
    cfg = _cfg()
    return os.getenv(cfg.get("segredo_provedor_env", "FAROL_AI_API_KEY")) or os.getenv("ANTHROPIC_API_KEY")

def modelo_para(tarefa: str) -> str:
    m = _cfg()["modelos"][tarefa]
    return os.getenv(m["env"]) or m["padrao"]

def verificar_pacote_seguro(objeto) -> None:
    proibidos = set(_cfg().get("dados_proibidos", []))
    def caminhar(x):
        if isinstance(x, dict):
            chaves = {str(k).lower() for k in x}
            expostas = chaves & proibidos
            if expostas:
                raise ValueError(f"pacote contém dados proibidos: {sorted(expostas)}")
            for v in x.values(): caminhar(v)
        elif isinstance(x, list):
            for v in x: caminhar(v)
    caminhar(objeto)

FERRAMENTAS = {   # 02/10: ferramentas do servidor (nomes conferidos no SDK oficial anthropic 1.11.0)
    "web_search": {"type": "web_search_20260318", "name": "web_search", "max_uses": 5},
    "web_fetch": {"type": "web_fetch_20260318", "name": "web_fetch", "max_uses": 5},
}


def esforco_para(tarefa: str) -> str | None:
    m = _cfg()["modelos"].get(tarefa)
    return (m.get("esforco") if isinstance(m, dict) else None) or None


def _post(chave: str, corpo: dict) -> dict:
    req = urllib.request.Request(API_URL, data=json.dumps(corpo).encode(), method="POST", headers={
        "x-api-key": chave, "anthropic-version": API_VERSION, "content-type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read(20_000_000).decode("utf-8"))


def chamar(tarefa: str, sistema: str, usuario: str, max_tokens: int | None = None,
           ferramentas: list[str] | None = None, esforco: str | None = None) -> str:
    """Chamada única ao modelo da TAREFA. 02/10: aceita ESFORÇO (output_config.effort: low…max, por tarefa em
    config/ia.json) e FERRAMENTAS do servidor (busca e leitura na web). Pausa no meio da busca (pause_turn) continua
    de onde parou (até 4 vezes). Sem credencial: SemCredencial — nunca simulação."""
    chave = credencial()
    if not chave:
        raise SemCredencial("credencial de IA ausente (defina FAROL_AI_API_KEY em GitHub Actions Secrets ou no computador do titular)")
    cfg = _cfg()
    modelo = modelo_para(tarefa)
    esforco = esforco or esforco_para(tarefa)
    corpo = {"model": modelo, "max_tokens": int(max_tokens or cfg["limites"].get("max_tokens_saida", 8000)), "system": sistema,
             "messages": [{"role": "user", "content": usuario}]}
    if esforco:
        corpo["output_config"] = {"effort": esforco}
    if ferramentas:
        corpo["tools"] = [FERRAMENTAS[f] for f in ferramentas if f in FERRAMENTAS]
    sem_esforco = False
    blocos, uso_total, buscas = [], {"input_tokens": 0, "output_tokens": 0}, 0
    for _ in range(5):
        try:
            dados = _post(chave, corpo)
        except urllib.error.HTTPError as e:   # modelo que não aceita o esforço: repete uma vez sem ele (registrado)
            txt = e.read().decode("utf-8", "ignore") if hasattr(e, "read") else ""
            if e.code == 400 and "output_config" in corpo and ("effort" in txt or "output_config" in txt) and not sem_esforco:
                corpo.pop("output_config"); sem_esforco = True
                continue
            raise
        conteudo = dados.get("content", [])
        blocos += conteudo
        u = dados.get("usage", {}) or {}
        uso_total["input_tokens"] += int(u.get("input_tokens") or 0); uso_total["output_tokens"] += int(u.get("output_tokens") or 0)
        buscas += sum(1 for b in conteudo if b.get("type") == "server_tool_use")
        if dados.get("stop_reason") != "pause_turn":
            break
        corpo["messages"] = corpo["messages"] + [{"role": "assistant", "content": conteudo}]
    texto = "".join(b.get("text", "") for b in blocos if b.get("type") == "text")
    append_jsonl(ROOT / "estado/ia_uso.jsonl", {
        "em": now_iso(), "tarefa": tarefa, "modelo": modelo, "esforco": None if sem_esforco else esforco, "ferramentas": ferramentas or [],
        "usos_de_ferramenta": buscas, "tokens_entrada": uso_total["input_tokens"], "tokens_saida": uso_total["output_tokens"],
        "chars_entrada": len(sistema) + len(usuario), "chars_saida": len(texto),
    })
    return texto

_JSON_BLOCO = re.compile(r"\{.*\}", re.S)

def extrair_json(texto: str):
    """Aceita resposta com ou sem cercas de código; devolve o primeiro objeto JSON."""
    limpo = texto.strip()
    limpo = re.sub(r"^```(?:json)?\s*|\s*```$", "", limpo, flags=re.S)
    try:
        return json.loads(limpo)
    except json.JSONDecodeError:
        m = _JSON_BLOCO.search(texto)
        if not m:
            raise ValueError("resposta da IA não contém JSON")
        return json.loads(m.group(0))
