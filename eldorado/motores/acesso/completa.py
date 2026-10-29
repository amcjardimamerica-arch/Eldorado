"""A escada completa (os 7 degraus) para quem não é motor: os pilotos e a releitura (o parecer do conselho, 24/10/2026: os
pilotos acessavam a internet só com 2 degraus, enquanto os motores usam os 7; a regra R05)."""
from __future__ import annotations

from .escada import Escada

ORDEM = ("api", "leve", "ponte", "lightpanda", "patchright", "camoufox", "arquivo", "local")   # a ponte BR (25/10/2026)


def escada_completa(intervalo_s: float = 1.0, tentativas: int = 1, tempo_limite: float = 25, ponte: str = "dados/ponte",
                    degraus: tuple[str, ...] = ORDEM, diario=None, dados=None) -> Escada:
    from .api import DegrauAPI
    from .arquivo_web import DegrauArquivo
    from .leve import DegrauLeve
    from .local import DegrauLocal
    from .navegador import DegrauLightpanda, DegrauNavegador
    mapa = {"api": DegrauAPI, "leve": DegrauLeve, "lightpanda": DegrauLightpanda, "patchright": lambda: DegrauNavegador("patchright"),
            "camoufox": lambda: DegrauNavegador("camoufox"), "arquivo": DegrauArquivo, "local": lambda: DegrauLocal(ponte)}
    from .ponte_br import DegrauPonteBR
    mapa["ponte"] = DegrauPonteBR
    lista = []
    for d in degraus:
        try:
            lista.append(mapa[d]())
        except Exception:  # noqa: BLE001 — o degrau que não pode ser montado aqui é pulado (o mesmo critério do motor)
            pass
    e = Escada(lista, diario=diario, intervalo_padrao=intervalo_s, tentativas=tentativas, tempo_limite=tempo_limite)
    if dados is not None:                       # 29/10/2026: com a memória do que já foi aprendido (e o diário, para aprender)
        from .escada import ler_aprendido

        e.semear(ler_aprendido(dados))
    return e
