"""Degrau 9: o computador da titular, quando o próprio site bloqueia o acesso remoto.

A ponte é uma pasta de pedidos e respostas (sincronizada com o computador da titular, onde o Claude no Chrome ou o
navegador local atende). O pedido não espera: o degrau devolve "pendente", o motor registra e segue; na próxima
passagem, a resposta já está na pasta e é lida aqui. O domínio fica marcado como "exige o computador local".
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .escada import Pendente, Resposta


class DegrauLocal:
    nome = "9 · computador da titular"
    pesado = False

    def __init__(self, pasta: str | Path):
        self.pasta = Path(pasta)
        (self.pasta / "pedidos").mkdir(parents=True, exist_ok=True)
        (self.pasta / "respostas").mkdir(parents=True, exist_ok=True)

    @staticmethod
    def chave(url: str) -> str:
        return hashlib.sha256(url.encode()).hexdigest()[:24]

    def buscar(self, url: str, tempo_limite: float) -> Resposta:
        k = self.chave(url)
        resposta, conteudo = self.pasta / "respostas" / f"{k}.json", self.pasta / "respostas" / f"{k}.bin"
        if resposta.exists() and conteudo.exists():
            meta = json.loads(resposta.read_text(encoding="utf-8"))
            r = Resposta(meta.get("url", url), int(meta.get("status", 200)), conteudo.read_bytes(), meta.get("tipo", ""))
            r.alertas.append(f"lido pelo computador local em {meta.get('em')}")
            return r
        pedido = self.pasta / "pedidos" / f"{k}.json"
        if not pedido.exists():
            pedido.write_text(json.dumps({"url": url, "pedido_em": datetime.now(timezone.utc).isoformat()}, ensure_ascii=False), encoding="utf-8")
        raise Pendente(f"pedido entregue ao computador local ({k})")
