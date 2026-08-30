from __future__ import annotations

import hashlib
import ipaddress
import json
import re
import socket
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib import robotparser
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]

INJECTION_PATTERNS = [
    re.compile(p, re.I) for p in (
        # inglês
        r"ignore .{0,40}(instruction|prompt|message)",
        r"disregard (all|any|the|previous|prior)",
        r"system prompt",
        r"prompt injection",
        r"reveal (the )?(prompt|secret|token)",
        r"you are (chatgpt|claude|an ai)",
        # português — o conteúdo coletado é brasileiro
        r"ignore\s+(todas\s+)?(as\s+)?(instru[çc]|regras|mensagens)",
        r"desconsidere\s+(tudo|todas|as\s+instru[çc]|o\s+prompt)",
        r"esque[çc]a\s+(tudo|todas|as\s+instru[çc])",
        r"revele\s+(o\s+)?(prompt|segredo|token|senha|chave)",
        r"voc[êe]\s+[ée]\s+(o\s+)?(chatgpt|claude|gemini|uma\s+ia|um\s+modelo)",
        r"novo\s+prompt\s+d[oe]\s+sistema",
        r"aja\s+como\s+se\s+(n[ãa]o\s+houvesse|as\s+regras)",
    )
]

# Estados definidos por revisão humana (ou verificação assistida auditada).
# A recoleta automática NUNCA rebaixa um destes estados nem apaga campos humanos.
STATUS_PROTEGIDOS = {
    "verificada_primaria", "verificada_dupla", "elegivel", "inelegivel",
    "em_preparacao", "submetida", "selecionada", "nao_selecionada",
    "em_execucao", "prestacao_de_contas", "encerrada", "descartada",
}
CAMPOS_PRESERVADOS = (
    "requisitos", "requisitos_validados", "requisitos_fonte", "notas",
    "verificado_em", "verificado_por", "descoberto_em",
)

def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def slug(text: str) -> str:
    clean = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", clean).strip("-")[:90] or "sem-nome"

def canonical_url(url: str) -> str:
    p = urlsplit(url.strip())
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/") or "/", p.query, ""))

def validate_public_https(url: str, allowed_host: str | None = None) -> None:
    p = urlsplit(url)
    if p.scheme != "https" or not p.hostname or p.username or p.password:
        raise ValueError("URL deve ser HTTPS e não pode conter credenciais")
    if allowed_host and not (p.hostname == allowed_host or p.hostname.endswith("." + allowed_host)):
        raise ValueError("redirecionamento para domínio não autorizado")
    for info in socket.getaddrinfo(p.hostname, 443, type=socket.SOCK_STREAM):
        ip = ipaddress.ip_address(info[4][0])
        if not ip.is_global:
            raise ValueError("endereço local, reservado ou privado bloqueado")

def has_prompt_injection(text: str) -> bool:
    sample = text[:250_000]
    return any(p.search(sample) for p in INJECTION_PATTERNS)

def novo_id(url: str) -> str:
    """Identificador global por URL canônica: o mesmo edital visto por fontes
    diferentes recebe o mesmo id (deduplicação entre fontes)."""
    return sha256(("opp|" + canonical_url(url)).encode())[:20]

def merge_registro(anterior: dict | None, novo: dict) -> dict:
    """Funde uma observação nova com o registro existente sem destruir trabalho
    humano: status protegido nunca regride e campos preservados permanecem."""
    if not anterior:
        novo.setdefault("descoberto_em", novo.get("coletado_em"))
        novo["fontes_observadas"] = sorted({f for f in [novo.get("fonte_id")] if f})
        return novo
    m = {**anterior, **novo}
    if anterior.get("status") in STATUS_PROTEGIDOS:
        m["status"] = anterior["status"]
    for campo in CAMPOS_PRESERVADOS:
        if anterior.get(campo) is not None:
            m[campo] = anterior[campo]
    m["descoberto_em"] = anterior.get("descoberto_em") or anterior.get("coletado_em") or novo.get("coletado_em")
    fontes = {*(anterior.get("fontes_observadas") or []), anterior.get("fonte_id"), novo.get("fonte_id")}
    m["fontes_observadas"] = sorted(f for f in fontes if f)
    return m

_ROBOTS_CACHE: dict = {}

def robots_permite(url: str, agente: str) -> bool:
    """Consulta e respeita o robots.txt do host (cache por execução).
    Falha na leitura do robots => permite, registrando comportamento padrão."""
    host = urlsplit(url).hostname or ""
    if host not in _ROBOTS_CACHE:
        parser = robotparser.RobotFileParser()
        try:
            req = Request(f"https://{host}/robots.txt", headers={"User-Agent": agente})
            with urlopen(req, timeout=10) as resp:
                parser.parse(resp.read(200_000).decode("utf-8", "ignore").splitlines())
        except Exception:
            parser = None
        _ROBOTS_CACHE[host] = parser
    parser = _ROBOTS_CACHE[host]
    return True if parser is None else parser.can_fetch(agente, url)

_TAGS_INUTEIS = re.compile(r"(?is)<(script|style|noscript|svg|nav|footer)[^>]*>.*?</\1>")
_TAG = re.compile(r"(?s)<[^>]+>")

def html_para_texto(html_bruto: str, limite: int = 120_000) -> str:
    """Conversão simples HTML->texto (biblioteca-padrão) para leitura de editais."""
    import html as _html
    texto = _TAGS_INUTEIS.sub(" ", html_bruto)
    texto = _TAG.sub(" ", texto)
    texto = _html.unescape(texto)
    texto = re.sub(r"[ \t\r\f\v]+", " ", texto)
    texto = re.sub(r"\n\s*\n+", "\n\n", texto)
    return texto.strip()[:limite]

DB_OPORTUNIDADES = ROOT / "dados/oportunidades/oportunidades.jsonl"

def carregar_oportunidades() -> dict:
    registros = {}
    if DB_OPORTUNIDADES.exists():
        for linha in DB_OPORTUNIDADES.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                item = json.loads(linha)
                registros[item["id"]] = item
    return registros

def gravar_oportunidades(registros: dict) -> None:
    DB_OPORTUNIDADES.parent.mkdir(parents=True, exist_ok=True)
    corpo = "".join(
        json.dumps(x, ensure_ascii=False, separators=(",", ":")) + "\n"
        for x in sorted(registros.values(), key=lambda v: v["id"])
    )
    DB_OPORTUNIDADES.write_text(corpo, encoding="utf-8")

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_jsonl(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")
