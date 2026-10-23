"""O mapa do site ORIGINAL (titular, 23/10/2026): com o histórico do livro, ele tem um site de divulgação e um site
original (a origem confirmada). No original, o mapa do site mostra as URLs novas onde podem estar a próxima
oportunidade, os seus arquivos e os seus dados.

Os mapas do domínio vêm do robots.txt (linhas "Sitemap:"), de /sitemap.xml, /sitemap_index.xml e /wp-sitemap.xml
(WordPress). A relevância para o livro: o número do edital na URL é evidência forte; senão, ao menos duas palavras
próprias do título (palavras de setor não contam); um arquivo (PDF, planilha, documento) com uma palavra própria conta.
"""
from __future__ import annotations

import re
import unicodedata
from datetime import date, timedelta
from typing import Callable
from urllib.parse import urlsplit

from .estrutura_site import mapa_do_site
from .pistas import Pista

ARQUIVO = re.compile(r"(?i)\.(pdf|docx?|xlsx?|odt|ods|csv|zip|rar)(\?|$)")
CANDIDATOS = ("/sitemap.xml", "/sitemap_index.xml", "/wp-sitemap.xml")
COMUNS = {"edital", "editais", "chamada", "chamamento", "publico", "publica", "selecao", "projetos", "programa", "inscricoes", "abertas",
          "aberto", "oportunidade", "noticias", "noticia", "pagina", "arquivos", "uploads", "content", "sites", "default", "index", "portal",
          "governo", "secretaria", "municipal", "estadual", "federal", "brasil", "goias", "resultado", "termo", "fomento", "organizacoes",
          "sociedade", "civil", "fundo", "premio", "concurso", "cultura", "cultural", "social", "saude", "esporte", "educacao"}


def _sem(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", "".join(c for c in unicodedata.normalize("NFKD", (t or "").lower()) if not unicodedata.combining(c))).strip()


def base(url: str) -> str:
    u = urlsplit(url)
    return f"{u.scheme}://{u.netloc}"


def mapas(buscar: Callable[[str], object], raiz: str) -> list[str]:
    achados: list[str] = []
    try:
        robots = buscar(f"{raiz}/robots.txt").conteudo.decode("utf-8", errors="replace")
        achados += [m.strip() for m in re.findall(r"(?im)^\s*sitemap:\s*(\S+)", robots)]
    except Exception:  # noqa: BLE001 — sem robots.txt, os endereços de costume
        pass
    return list(dict.fromkeys(achados + [raiz + c for c in CANDIDATOS]))


def urls(buscar: Callable[[str], object], raiz: str, limite: int = 5000) -> list[Pista]:
    """Todas as URLs dos mapas do domínio: o leitor completo do plano (ultimate-sitemap-parser, pela escada) e, de reserva,
    o leitor próprio (os mapas que não abrem são pulados)."""
    vistas: dict[str, Pista] = {}
    try:
        from .estrutura_site import mapa_completo
        for p in mapa_completo(buscar, raiz, limite=limite):
            vistas.setdefault(p.link, p)
        if vistas:
            return list(vistas.values())[:limite]
    except Exception:  # noqa: BLE001 — sem a biblioteca, ou o leitor completo falhou: o próprio
        pass
    for m in mapas(buscar, raiz):
        try:
            for p in mapa_do_site(buscar, m, limite=limite):
                vistas.setdefault(p.link, p)
        except Exception:  # noqa: BLE001 — um mapa que não abre (404, XML inválido) não derruba os outros
            continue
        if len(vistas) >= limite:
            break
    return list(vistas.values())[:limite]


def palavras_proprias(texto: str) -> set[str]:
    return {p for p in _sem(texto).split() if len(p) >= 5 and p not in COMUNS and not p.isdigit()}


def relevancia(url: str, palavras: set[str], numero: str | None) -> str | None:
    """O motivo de a URL ter a ver com o livro, ou None."""
    caminho = _sem(urlsplit(url).path)
    if numero:
        n, ano = (numero.split("/") + [""])[:2]
        if re.search(rf"\b0*{n}\b.*\b{ano}\b|\b{ano}\b.*\b0*{n}\b", caminho) if ano else re.search(rf"\b0*{n}\b", caminho):
            return f"o número do edital ({numero}) na URL"
    comuns = sorted(p for p in palavras if p in caminho)
    if len(comuns) >= 2:
        return f"palavras do livro na URL ({', '.join(comuns[:4])})"
    if comuns and ARQUIVO.search(url):
        return f"arquivo com palavra do livro ({comuns[0]})"
    return None


def recente(p: Pista, dias: int = 90, hoje: date | None = None) -> bool:
    if not p.data:
        return False
    try:
        return date.fromisoformat(str(p.data)[:10]) >= (hoje or date.today()) - timedelta(days=dias)
    except ValueError:
        return False
