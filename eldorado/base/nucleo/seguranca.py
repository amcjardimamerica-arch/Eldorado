"""A segurança dos textos lidos: os padrões de injeção de instruções (prompt injection).

Uma página pode esconder frases para manipular quem a lê com IA ("ignore as instruções anteriores", "você agora é...").
O texto continua íntegro, como publicado (regra dos dados públicos); a leitura recebe a marca e o trecho, e a
Pertinência reprova automaticamente o achado (reprovação prevista nos padrões de edital do Eldorado0).
"""
from __future__ import annotations

import re
import unicodedata

PADROES = [
    r"ignor[ea]\w*\s+(?:todas?\s+)?(?:as\s+|os\s+)?(?:instru[çc][õo]es|orienta[çc][õo]es|regras|comandos)\s+(?:anteriores|acima|pr[ée]vias)",
    r"desconsider[ea]\w*\s+(?:todas?\s+)?(?:as\s+)?(?:instru[çc][õo]es|regras)\s+(?:anteriores|acima)",
    r"ignore\s+(?:all\s+)?(?:the\s+)?(?:previous|prior|above)\s+(?:instructions|prompts?|rules)",
    r"disregard\s+(?:all\s+)?(?:the\s+)?(?:previous|prior|above)\s+(?:instructions|rules)",
    r"voc[êe]\s+(?:agora\s+)?[ée]\s+(?:um|uma)\s+(?:assistente|ia|modelo|chatbot)\s+(?:sem|que\s+n[ãa]o)",
    r"you\s+are\s+now\s+(?:a|an|in)\s+", r"\bact\s+as\s+(?:a|an)\s+(?:unrestricted|jailbroken|dan)\b", r"\bjailbreak\b",
    r"(?:revele|mostre|reveal|print|show)\s+(?:o\s+|seu\s+|your\s+|the\s+)?(?:prompt\s+do\s+sistema|system\s+prompt|instru[çc][õo]es\s+internas)",
    r"<\|im_start\|>|<\|im_end\|>|<\|system\|>|\[/?INST\]|<<SYS>>|###\s*(?:system|instruction)\s*:",
    r"(?:new|novas?)\s+(?:system\s+)?(?:instructions|instru[çc][õo]es)\s*:",
]
RX = re.compile("|".join(f"(?:{p})" for p in PADROES), re.I)


def _sem_acento(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c))


def injecao(texto: str) -> str | None:
    """O trecho com o padrão de injeção, ou None. Procura no texto como está e sem acentos."""
    for t in (texto or "", _sem_acento(texto or "")):
        m = RX.search(t)
        if m:
            return re.sub(r"\s+", " ", t[max(0, m.start() - 60):m.end() + 60]).strip()
    return None
