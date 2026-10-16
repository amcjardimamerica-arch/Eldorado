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


ID_LONGO = re.compile(r"^[0-9a-f]{16,}$")


def chave_curta(identificador) -> str:
    """A identidade de um registro: os oito primeiros caracteres do id.

    `novo_id` devolve vinte caracteres, mas a base de oportunidades e as bases
    de verificação nunca combinaram como guardá-los: umas gravam a chave
    inteira, outras só os oito primeiros. O mesmo edital passava então a existir
    duas vezes, uma por grafia — o Instituto Impactarte, o Osório/RS e mais
    cinco chegaram assim à fila de pesquisa de 23/09/2026, sem que a
    deduplicação por objeto os alcançasse: os textos vinham de rotas diferentes
    e não batiam entre si.

    Toda leitura de base passa por aqui, e as duas grafias voltam a ser o mesmo
    registro. Só id hexadecimal é truncado; chave escrita à mão
    (`planaltina-esporte-2026`) fica inteira, porque oito caracteres dela não
    identificam coisa nenhuma.

    Truncar só é seguro enquanto nenhum prefixo de oito caracteres servir a dois
    ids diferentes. Em 23/09/2026 não havia um único caso em mais de dezessete
    mil registros, e há teste cobrando que continue assim.
    """
    bruto = "" if identificador is None else str(identificador).strip()
    return bruto[:8] if ID_LONGO.match(bruto) else bruto

def merge_registro(anterior: dict | None, novo: dict) -> dict:
    """Funde uma observação nova com o registro existente sem destruir trabalho
    humano: status protegido nunca regride e campos preservados permanecem."""
    if not anterior:
        try:                                             # 14/10 (titular): o motor descarta municipal de outro estado (fora das capitais)
            from .regra_abrangencia import filtro as _abr
            if _abr(novo.get("fonte_id") or novo.get("fonte_nome"), novo):
                novo["_descartado_na_coleta"] = True
        except Exception:  # noqa: BLE001
            pass
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

def _migrado() -> bool:
    return (ROOT / "estado/livros_migracao.json").exists()


def achados_linhas() -> list[str]:
    """16/10/2026 (titular, etapa 3): leitura ÚNICA dos achados dos motores — dos LIVROS depois da migração
    (estado/livros_migracao.json), da base antiga antes dela. Mesmo formato: uma linha JSON por achado."""
    if _migrado():
        from .banco_livros import achados
        return [json.dumps(x, ensure_ascii=False, separators=(",", ":")) for x in achados()]
    return [l for l in DB_OPORTUNIDADES.read_text(encoding="utf-8").splitlines() if l.strip()] if DB_OPORTUNIDADES.exists() else []


def carregar_oportunidades() -> dict:
    registros = {}
    for linha in achados_linhas():
        item = json.loads(linha)
        registros[item["id"]] = item
    return registros

def gravar_oportunidades(registros: dict) -> None:
    if _migrado():                                    # 16/10 (etapa 3): depois da migração, os LIVROS são a base
        from .banco_livros import sincronizar_achados
        sincronizar_achados(registros)
        return
    DB_OPORTUNIDADES.parent.mkdir(parents=True, exist_ok=True)
    corpo = "".join(
        json.dumps(x, ensure_ascii=False, separators=(",", ":")) + "\n"
        for x in sorted(registros.values(), key=lambda v: v["id"]) if not x.get("_descartado_na_coleta")
    )
    DB_OPORTUNIDADES.write_text(corpo, encoding="utf-8")

def _proibido(path) -> bool:
    """16/10/2026 (titular): TRAVA NO NÚCLEO — caminho cujo conteúdo só pode existir nos livros (só no Eldorado)."""
    try:
        from .livro_arquivo import _rel, proibido
        return proibido(_rel(path))
    except Exception:  # noqa: BLE001
        return False


def load_json(path: Path):
    path = Path(path)
    if not path.exists() and _proibido(path):         # já absorvido: montado a partir dos livros
        from .livro_arquivo import carregar
        v = carregar(path, None)
        if v is not None:
            return v
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, value) -> None:
    path = Path(path)
    if _proibido(path):                                # 16/10: grava NO LIVRO; o arquivo não chega a existir
        from .livro_arquivo import guardar_lote
        guardar_lote([(path, value)])
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_jsonl(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")


def resolver_redirecionamento(url: str) -> str:
    """O ENDEREÇO REAL, NÃO O DO BUSCADOR (24/09). Resultado de busca vem embrulhado num
    redirecionamento — DuckDuckGo (`duckduckgo.com/l?uddg=…`), Bing (`bing.com/ck/a?u=a1<base64>`),
    Google (`google.com/url?q=…`). Gravado assim, o link não abre para ninguém: o motor 23 tinha
    24 registros com o embrulho e nenhum com o destino. Aqui se tira o destino do embrulho."""
    import base64
    from urllib.parse import parse_qs, unquote, urlsplit
    u = str(url or "").strip()
    if u.startswith("//"):
        u = "https:" + u
    try:
        p = urlsplit(u)
        host = (p.hostname or "").lower()
        q = parse_qs(p.query)
        if host.endswith("duckduckgo.com") and q.get("uddg"):
            return unquote(q["uddg"][0])
        if host.endswith("bing.com") and q.get("u"):
            b = q["u"][0]
            if b.startswith("a1"):
                b = b[2:]
                b += "=" * (-len(b) % 4)
                return base64.urlsafe_b64decode(b).decode("utf-8", "ignore")
            return unquote(b)
        if host.endswith("google.com") and p.path.startswith("/url") and (q.get("q") or q.get("url")):
            return unquote((q.get("q") or q.get("url"))[0])
    except Exception:
        pass
    return u
