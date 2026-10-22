"""A configuração da plataforma, validada na carga.

Uma única fonte (config/eldorado.toml), com valores padrão seguros. Nenhum endereço fica fixo no código
(lição da troca de nome do repositório no Eldorado0). Configuração inválida impede a passagem.
"""
from __future__ import annotations

import tomllib
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid")      # chave desconhecida é erro (evita configuração escrita errada)


class Caminhos(_Base):
    dados: str = "dados"                 # onde ficam os bancos (fora do Git)
    eventos: str = "eventos"             # os diários de eventos de cada execução
    fotografias: str = "fotografias"     # as cópias comprimidas dos bancos
    estado_motores: str = "dados/motores"


class Limites(_Base):
    carga_maxima: float = Field(0.85, gt=0, le=1)       # o governador mantém a máquina abaixo disto
    tentativas_por_ferramenta: int = Field(3, ge=1, le=3)
    espera_entre_tentativas_h: list[int] = [6, 24]
    retencao_temporario_dias: int = Field(30, ge=1, le=30)


class Missao(_Base):
    ativa: str = "oportunidades"


class Config(_Base):
    nome: str = "Eldorado"
    missao: Missao = Missao()
    caminhos: Caminhos = Caminhos()
    limites: Limites = Limites()

    @field_validator("nome")
    @classmethod
    def _nome(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("o nome não pode ser vazio")
        return v

    def caminho(self, raiz: Path, qual: str) -> Path:
        return (raiz / getattr(self.caminhos, qual)).resolve()


class ConfiguracaoInvalida(Exception):
    pass


def carregar(arquivo: str | Path = "config/eldorado.toml") -> Config:
    """Carrega e valida. Arquivo ausente usa os padrões; arquivo inválido levanta ConfiguracaoInvalida."""
    p = Path(arquivo)
    if not p.exists():
        return Config()
    try:
        dados = tomllib.loads(p.read_text(encoding="utf-8"))
        return Config(**dados)
    except Exception as e:  # noqa: BLE001 — qualquer erro de leitura ou validação para a passagem
        raise ConfiguracaoInvalida(f"{p}: {e}") from e
