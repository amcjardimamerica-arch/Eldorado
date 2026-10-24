"""O governador de carga: mantém a máquina abaixo do limite (85%).

Decide ANTES de iniciar cada tarefa, e não depois de travar:
- a carga atual (o maior entre processador e memória) mais o custo estimado da tarefa deve ficar no limite;
- o disco é espaço, não carga: acima do limite abre alarme; acima de 95% nada novo começa (sem espaço para gravar);
- o custo de cada módulo é aprendido dos recibos (processador e memória medidos em cada chamada);
- tarefas pesadas (navegadores, OCR, leitor universal) só começam com folga para elas.
A medição é feita por um medidor trocável (psutil na máquina real; simulado nos testes).
"""
from __future__ import annotations

import math
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Protocol

import psutil

from ..nucleo.eventos import Diario, agora

CUSTO_PADRAO = {"leve": 0.05, "pesado": 0.25}      # fração da máquina, até o módulo ter recibos próprios


@dataclass(frozen=True)
class Leitura:
    processador: float      # frações de 0 a 1
    memoria: float
    disco: float

    @property
    def carga(self) -> float:
        """O que decide se uma tarefa começa: processador e memória (o disco é espaço, tratado à parte)."""
        return max(self.processador, self.memoria)


class Medidor(Protocol):
    def __call__(self) -> Leitura: ...


def medidor_psutil(caminho_disco: str = ".") -> Callable[[], Leitura]:
    psutil.cpu_percent(interval=None)                 # a primeira leitura do psutil é sempre 0; descartada
    def medir() -> Leitura:
        return Leitura(processador=psutil.cpu_percent(interval=0.2) / 100, memoria=psutil.virtual_memory().percent / 100,
                       disco=psutil.disk_usage(caminho_disco).percent / 100)
    return medir


@dataclass
class Governador:
    medidor: Callable[[], Leitura]
    limite: float = 0.85
    disco_critico: float = 0.95
    # os motores esperam a rede a maior parte do tempo: quem limita é a carga medida (o alvo de 85%), não os núcleos
    paralelismo_maximo: int = max(4, 4 * (os.cpu_count() or 1))
    diario: Diario | None = None
    custos: dict[str, float] = field(default_factory=dict)      # módulo → fração da máquina, aprendida dos recibos
    ultima: Leitura | None = None

    def custo(self, modulo: str | None, peso: str = "leve") -> float:
        return self.custos.get(modulo or "", CUSTO_PADRAO[peso]) if modulo else CUSTO_PADRAO[peso]

    def aprender_custo(self, modulo: str, cpu_ms: int, duracao_ms: int, memoria_pico_kb: int | None) -> float:
        """Custo de um módulo pelos recibos: a fração de processador usada na chamada, ou de memória, a maior das duas."""
        nucleos = psutil.cpu_count() or 1
        frac_cpu = (cpu_ms / max(duracao_ms, 1)) / nucleos
        frac_mem = ((memoria_pico_kb or 0) * 1024) / psutil.virtual_memory().total
        novo = min(1.0, max(frac_cpu, frac_mem, 0.01))
        antigo = self.custos.get(modulo)
        self.custos[modulo] = novo if antigo is None else round(0.7 * antigo + 0.3 * novo, 4)     # média que esquece devagar
        return self.custos[modulo]

    def ler(self) -> Leitura:
        self.ultima = self.medidor()
        return self.ultima

    def pode_iniciar(self, modulo: str | None = None, peso: str = "leve") -> bool:
        leitura = self.ler()
        if leitura.disco >= self.disco_critico:
            return False
        return leitura.carga + self.custo(modulo, peso) <= self.limite

    def motivo(self) -> str:
        leitura = self.ultima
        if leitura is None:
            return "sem leitura"
        if leitura.disco >= self.disco_critico:
            return f"disco {leitura.disco:.0%} ocupado: sem espaço seguro para gravar"
        return f"carga {leitura.carga:.0%} (processador {leitura.processador:.0%}, memória {leitura.memoria:.0%}) sem folga até {self.limite:.0%}"

    def alertas(self) -> list[str]:
        leitura = self.ultima or self.ler()
        a = []
        if leitura.disco >= self.limite:
            a.append(f"disco {leitura.disco:.0%} ocupado (acima de {self.limite:.0%})")
        if leitura.carga >= self.limite:
            a.append(f"carga {leitura.carga:.0%} acima de {self.limite:.0%}")
        return a

    def paralelismo(self, modulo: str | None = None, peso: str = "leve") -> int:
        leitura = self.ler()
        folga = self.limite - leitura.carga
        if folga <= 0 or leitura.disco >= self.disco_critico:
            return 0
        return max(0, min(self.paralelismo_maximo, math.floor(folga / self.custo(modulo, peso) + 1e-9)))

    def registrar(self, tamanhos: dict[str, int] | None = None, paralelismo: int | None = None) -> dict:
        """Grava a leitura da máquina (para o mostrador): uso, paralelismo e o tamanho de cada parte."""
        leitura = self.ultima or self.ler()
        rede = psutil.net_io_counters()
        import shutil
        import subprocess
        gpu = "não há placa de vídeo neste servidor"
        if shutil.which("nvidia-smi"):
            try:
                gpu = subprocess.run(["nvidia-smi", "--query-gpu=name,utilization.gpu,memory.used,memory.total", "--format=csv,noheader"],
                                     capture_output=True, text=True, timeout=10).stdout.strip()[:200] or gpu
            except Exception:  # noqa: BLE001
                pass
        dados = {"em": agora(), "processador": leitura.processador, "memoria": leitura.memoria, "disco": leitura.disco,
                 "rede_entrada": float(rede.bytes_recv), "rede_saida": float(rede.bytes_sent), "paralelismo": paralelismo,
                 "nucleos": psutil.cpu_count() or 1, "memoria_total_mb": psutil.virtual_memory().total // 2**20,
                 "disco_total_gb": round(psutil.disk_usage(".").total / 2**30, 1), "gpu": gpu}
        for parte, tamanho in (tamanhos or {}).items():
            dados[f"tamanho_{parte}"] = tamanho
        if self.diario:
            self.diario.emitir("maquina.leitura", "governador", dados)
            for alerta in self.alertas():
                self.diario.emitir("alarme.aberto", "governador", {"gravidade": "media", "modulo": "governador", "mensagem": alerta, "aberto_em": agora()})
        return dados


def tamanho(caminho: str | Path) -> int:
    p = Path(caminho)
    if p.is_file():
        return p.stat().st_size
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file()) if p.exists() else 0
