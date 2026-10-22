"""O formato comum das cinco formas de descoberta: a pista (título, link, data, de onde veio)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

Buscar = Callable[[str], Any]          # a busca da escada de acesso: url → Resposta (nunca fazer requisição por fora dela)


@dataclass
class Pista:
    titulo: str
    link: str
    origem: str
    data: str | None = None
    resumo: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)
