"""Adaptador único de IA (Anthropic), biblioteca-padrão apenas.

Princípios: (1) IA só em etapa essencial; (2) o modelo é escolhido POR TAREFA
em config/ia.json (env sobrepõe o padrão); (3) sem credencial => erro limpo
`SemCredencial`, nunca simulação; (4) todo uso é auditado em estado/ia_uso.jsonl;
(5) nenhum dado proibido (config ia.json → dados_proibidos) sai do repositório."""
from __future__ import annotations

import json
import os
import re
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

def chamar(tarefa: str, sistema: str, usuario: str, max_tokens: int | None = None) -> str:
    chave = credencial()
    if not chave:
        raise SemCredencial("credencial de IA ausente (defina FAROL_AI_API_KEY em GitHub Actions Secrets)")
    cfg = _cfg()
    modelo = modelo_para(tarefa)
    corpo = json.dumps({
        "model": modelo,
        "max_tokens": int(max_tokens or cfg["limites"].get("max_tokens_saida", 8000)),
        "system": sistema,
        "messages": [{"role": "user", "content": usuario}],
    }).encode()
    req = urllib.request.Request(API_URL, data=corpo, method="POST", headers={
        "x-api-key": chave, "anthropic-version": API_VERSION, "content-type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=300) as resp:
        dados = json.loads(resp.read(20_000_000).decode("utf-8"))
    texto = "".join(b.get("text", "") for b in dados.get("content", []) if b.get("type") == "text")
    uso = dados.get("usage", {})
    append_jsonl(ROOT / "estado/ia_uso.jsonl", {
        "em": now_iso(), "tarefa": tarefa, "modelo": modelo,
        "tokens_entrada": uso.get("input_tokens"), "tokens_saida": uso.get("output_tokens"),
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
