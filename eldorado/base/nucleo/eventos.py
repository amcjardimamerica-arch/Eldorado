"""Os eventos: a única forma de escrita do Eldorado.

Cada módulo trabalha e grava eventos; só o gravador aplica os eventos aos bancos. O catálogo diz, para cada tipo,
em qual banco e tabela ele é aplicado e com qual operação. Um tipo fora do catálogo é recusado na criação.

O diário guarda os eventos de cada execução num arquivo que só recebe acréscimos (eventos/AAAA/MM/DD/<execução>.jsonl).
"""

from __future__ import annotations

import os
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator

import msgspec

from .contratos import Linhagem

VERSAO_CATALOGO = 1


class Evento(msgspec.Struct, kw_only=True, omit_defaults=True):
    id: str
    tipo: str
    modulo: str
    em: str
    dados: dict[str, Any]
    linhagem: Linhagem = Linhagem()
    versao: int = VERSAO_CATALOGO


@dataclass(frozen=True)
class Alvo:
    banco: str  # 'biblioteca', 'especial', 'cerebro'
    tabela: str
    operacao: str  # 'inserir', 'inserir_se_novo', 'atualizar', 'inserir_ou_atualizar', 'pagina', 'expandir'
    chave: tuple[str, ...] = ()  # colunas que identificam a linha (atualizar e inserir_ou_atualizar)
    mapa: Callable[[dict[str, Any]], dict[str, Any]] | None = field(default=None, compare=False)


def _rotulo(d: dict[str, Any]) -> dict[str, Any]:
    return {"referencia": d["livro_id"], "origem": d["origem"], "decisao": d["decisao"], "em": d["em"]}


def _decisao_no_achado(d: dict[str, Any]) -> dict[str, Any]:
    return {"id": d["referencia"], "decisao": d["decisao"], "motivo": d.get("motivo")}


def _passaporte(d: dict[str, Any]) -> dict[str, Any]:
    return {"livro_id": d["livro_id"], "fase": d["para"], "entrou_em": d["em"]}


def _resumo(x: Any) -> Any:
    """O resumo de uma entrada ou saída de passo: quantos itens e os identificadores; nunca o conteúdo (titular, 24/10/2026:
    o Cérebro jamais guarda livros; o conteúdo fica só no diário da execução, que é o que a retomada lê)."""
    if not isinstance(x, list):
        return None
    ids = [str(i.get("id") or i.get("livro") or i.get("livro_id") or "")[:60] for i in x if isinstance(i, dict)]
    r = {"itens": len(x), "ids": [i for i in ids if i][:20]}
    falhas = [i for i in x if isinstance(i, dict) and i.get("erro")]  # da falha: só a mensagem e os arquivos do erro (o monitoramento)
    if falhas:
        r["erro"] = str(falhas[0]["erro"])[:300]
        r["arquivos_do_erro"] = [str(a) for a in (falhas[0].get("arquivos_do_erro") or [])][:12]
    return r


def _passo(d: dict[str, Any]) -> dict[str, Any]:
    # 30/10/2026: a entrada já vem resumida no evento ({"itens": n}); os eventos antigos trazem a lista inteira
    ent = d.get("entrada")
    return {**d, "entrada": ent if isinstance(ent, dict) else _resumo(ent), "saida": _resumo(d.get("saida"))}


def _so(*colunas: str) -> Callable[[dict[str, Any]], dict[str, Any]]:
    return lambda d: {c: d[c] for c in colunas if c in d}


B, C = "biblioteca", "cerebro"
E = B  # as empresas vivem na Biblioteca (titular, 24/10/2026)
CATALOGO: dict[str, tuple[Alvo, ...]] = {
    # Regência, fluxo e medição (cerebro.db)
    "plano.criado": (Alvo(C, "plano", "inserir"),),
    "acionamento.feito": (Alvo(C, "acionamento", "inserir"),),
    "execucao.iniciada": (Alvo(C, "execucao", "inserir"),),
    "execucao.concluida": (Alvo(C, "execucao", "atualizar", ("id",), _so("id", "fim", "estado")),),
    "execucao.retomada": (Alvo(C, "execucao", "atualizar", ("id",), _so("id", "estado")),),
    "execucao.passo": (Alvo(C, "execucao_passo", "inserir", mapa=_passo),),  # só o resumo: o Cérebro não guarda livros
    "chamada.recibo": (Alvo(C, "recibo", "inserir"),),
    "motor.execucao": (Alvo(C, "execucao_motor", "inserir"),),
    # o aprendizado dos motores, entregue ao Cérebro (nenhum motor tem banco; titular, 24/10/2026)
    "motor.entregue": (Alvo(C, "motor_entregue", "inserir_se_novo"),),
    "motor.fonte": (Alvo(C, "motor_fonte", "inserir_ou_atualizar", ("motor", "nome")),),
    "motor.assinatura": (Alvo(C, "motor_assinatura", "inserir_ou_atualizar", ("motor", "fonte")),),
    "motor.mapa": (Alvo(C, "motor_mapa_dominio", "inserir_ou_atualizar", ("motor", "dominio")),),
    "motor.alvo": (Alvo(C, "motor_alvo_mudanca", "inserir_se_novo"),),
    "motor.retorno": (Alvo(C, "motor_retorno", "inserir_se_novo"),),
    "documento.relido": (Alvo(C, "releitura", "inserir_ou_atualizar", ("documento_id",)),),  # a tentativa da releitura (aprendizado)
    # o aprendizado do Espião, pelos eventos (24/10/2026: a sala não via as missões gravadas direto no arquivo)
    "espiao.familia": (Alvo(C, "espiao_familia", "inserir_ou_atualizar", ("nome",)),),
    "espiao.consulta": (Alvo(C, "espiao_consulta", "inserir_ou_atualizar", ("texto",)),),
    "espiao.missao": (Alvo(C, "espiao_missao", "inserir"),),
    "espiao.rota": (Alvo(C, "espiao_rota", "inserir_ou_atualizar", ("nome",)),),
    "sala.medida": (Alvo(C, "sala_medicao", "inserir_ou_atualizar", ("chave",)),),  # a sala como parâmetro do funcionamento
    "arquivos.medidos": (Alvo(C, "medicao_arquivos", "inserir_ou_atualizar", ("chave",)),),  # o monitoramento de cada arquivo
    # 29/10/2026: o nível "etapa" (o medidor de memória por etapa, implantado às 08:57) vira "componente": o banco só aceita
    # arquivo, componente, parte, sistema e motor; sem isso os eventos já gravados seriam recusados para sempre
    "medicao.registrada": (
        Alvo(
            C,
            "medicao",
            "inserir_ou_atualizar",
            ("marcador", "nivel", "em"),
            lambda d: {**d, "nivel": "componente"} if d.get("nivel") == "etapa" else d,
        ),
    ),
    "maquina.leitura": (Alvo(C, "maquina", "inserir_se_novo"),),
    "cobertura.dia": (Alvo(C, "cobertura_dia", "inserir_ou_atualizar", ("dia",)),),
    "agenda.definida": (Alvo(C, "agenda", "inserir_ou_atualizar", ("modulo", "janela_inicio")),),
    "dominio.aprendido": (Alvo(C, "dominio", "inserir_ou_atualizar", ("dominio",)),),
    "modulo.registrado": (Alvo(C, "modulo", "inserir_ou_atualizar", ("id",)),),
    "workflow.versao": (Alvo(C, "workflow", "inserir_ou_atualizar", ("id", "versao")),),
    "alarme.aberto": (Alvo(C, "alarme", "inserir"),),
    "alarme.fechado": (Alvo(C, "alarme", "atualizar", ("id",), _so("id", "fechado_em")),),
    # o Comandante e o Aprendizado (25/10/2026): a execução e o aprendizado no Arquivo do Cérebro
    "comandante.decidiu": (Alvo(C, "comandante_decisao", "inserir"),),
    "comandante.avaliada": (Alvo(C, "comandante_decisao", "atualizar", ("id",), _so("id", "resultado", "recompensa", "avaliada_em")),),
    "parametro.definido": (Alvo(C, "parametro", "inserir_se_novo"),),
    "conferencia.agendada": (Alvo(C, "conferencia", "inserir"),),
    "conferencia.feita": (Alvo(C, "conferencia", "atualizar", ("id",), _so("id", "estado", "conferida_em")),),
    "skill.registrada": (Alvo(C, "skill", "inserir_se_novo"),),
    "skill.atualizada": (Alvo(C, "skill", "atualizar", ("nome",), _so("nome", "descricao", "caminho", "versao", "atualizada_em")),),
    "skill.usada": (Alvo(C, "skill", "atualizar", ("nome",), _so("nome", "usos", "sucessos", "falhas", "ultimo_uso")),),
    "skill.estado": (Alvo(C, "skill", "atualizar", ("nome",), _so("nome", "estado", "atualizada_em")),),
    "grafo.ligado": (Alvo(C, "grafo_aresta", "inserir_ou_atualizar", ("origem", "destino", "tipo")),),
    "memoria.registrada": (Alvo(C, "memoria", "inserir"),),
    "memoria.expirada": (Alvo(C, "memoria", "apagar", ("tabela", "ref")),),
    "memoria.ponteiro": (Alvo(C, "memoria_ponteiro", "inserir_ou_atualizar", ("tabela",)),),
    "regra.registrada": (Alvo(C, "regra", "inserir_se_novo"),),  # idempotente: a regra já registrada não se repete (25/10/2026)
    "regra.substituida": (Alvo(C, "regra", "atualizar", ("id",), _so("id", "vigente", "substituida_por")),),
    "modelo.treinado": (Alvo(C, "modelo", "inserir"),),
    "aprendizado.registrado": (Alvo(C, "aprendizado_temporario", "inserir"),),
    "aprendizado.promovido": (Alvo(C, "aprendizado_permanente", "inserir"),),
    "aprendizado.arquivado": (Alvo(C, "aprendizado_permanente", "atualizar", ("id",), _so("id", "arquivado")),),
    "aprendizado.usado": (Alvo(C, "aprendizado_temporario", "atualizar", ("id",), _so("id", "usos", "resultado")),),
    "aprendizado.expirado": (Alvo(C, "aprendizado_temporario", "apagar", ("id",)),),
    # Pertinência: a decisão fica no Cérebro e no próprio achado
    "pertinencia.decidida": (Alvo(C, "decisao_pertinencia", "inserir"), Alvo(B, "achado", "atualizar", ("id",), _decisao_no_achado)),
    # Coleta e Cartório (biblioteca.db)
    "achado.entregue": (Alvo(B, "achado", "inserir_se_novo"),),
    "documento.registrado": (Alvo(B, "documento", "inserir_ou_atualizar", ("sha256",)),),
    "pagina.gravada": (Alvo(B, "pagina", "pagina"),),
    "livro.criado": (Alvo(B, "livro", "inserir"),),
    "livro.vinculado": (Alvo(B, "achado", "atualizar", ("id",), lambda d: {"id": d["achado_id"], "livro_id": d["livro_id"]}),),
    "livro.unido": (Alvo(B, "uniao", "inserir_se_novo"),),  # idempotente: o mesmo par unido de novo não é erro (25/10/2026)
    "livro.situacao": (Alvo(B, "livro", "atualizar", ("id",), _so("id", "situacao", "atualizado_em")),),
    "livro.links": (Alvo(B, "livro", "atualizar", ("id",), _so("id", "link_divulgacao", "link_oficial", "atualizado_em")),),
    "livro.passagem": (Alvo(B, "passagem", "inserir"), Alvo(B, "passaporte", "inserir_ou_atualizar", ("livro_id",), _passaporte)),
    "livro.excluido_logicamente": (
        Alvo(
            B,
            "livro",
            "atualizar",
            ("id",),
            lambda d: {
                "id": d["id"],
                "situacao": "excluido",
                "justificativa_exclusao": d.get("justificativa_exclusao"),
                "atualizado_em": d["atualizado_em"],
            },
        ),
    ),
    "tentativa.registrada": (Alvo(B, "tentativa", "inserir"),),
    "certidao.gravada": (Alvo(B, "certidao", "inserir"),),
    "certidao.contestada": (Alvo(B, "certidao", "atualizar", ("id",), _so("id", "situacao")),),
    "livro.legislacao": (Alvo(B, "livro_lei", "inserir_ou_atualizar", ("livro_id", "lei_id")),),
    "livro.decupado": (Alvo(B, "livro_dados", "inserir_ou_atualizar", ("livro_id",)),),
    "livro.origem": (Alvo(B, "livro_dados", "atualizar", ("livro_id",), _so("livro_id", "origem", "origem_motivo")),),
    "livro.escada": (Alvo(B, "livro_dados", "atualizar", ("livro_id",), _so("livro_id", "escada")),),
    "livro.esfera": (Alvo(B, "livro_dados", "atualizar", ("livro_id",), _so("livro_id", "esfera")),),
    "livro.base": (
        Alvo(B, "livro_dados", "atualizar", ("livro_id",), _so("livro_id", "base_classe", "base_buscar", "base_tentativas", "base_ultima")),
    ),
    "livro.codigo": (Alvo(B, "livro_dados", "atualizar", ("livro_id",), _so("livro_id", "codigo")),),  # o código da oportunidade
    "livro.prazo": (Alvo(B, "livro_dados", "atualizar", ("livro_id",), _so("livro_id", "situacao_prazo")),),  # o prazo pela passagem do tempo
    "selo.calculado": (Alvo(B, "livro", "atualizar", ("id",), _so("id", "estrela", "selo_livro", "informacoes_validadas", "atualizado_em")),),
    "relatorio.etapa": (Alvo(B, "relatorio_etapa", "inserir"),),
    "analise.rede": (Alvo(B, "analise_rede", "inserir"),),
    "veredito.gravado": (Alvo(B, "veredito", "inserir"), Alvo(C, "rotulo", "inserir_ou_atualizar", ("referencia", "origem", "em"), _rotulo)),
    "previsao.calculada": (Alvo(B, "previsao", "inserir_ou_atualizar", ("livro_id",)),),
    "alerta.preditivo": (Alvo(B, "previsao", "atualizar", ("livro_id",), _so("livro_id", "alerta_em")),),
    "transferencia.feita": (Alvo(B, "transferencia", "inserir"),),
    "lei.registrada": (Alvo(B, "lei", "inserir_ou_atualizar", ("id",)),),
    # as empresas e os incentivos (na Biblioteca, biblioteca.db)
    "empresa.registrada": (Alvo(E, "empresa", "inserir_ou_atualizar", ("cnpj",)),),
    "incentivo.registrado": (Alvo(E, "incentivo", "inserir"),),
    "ranking.calculado": (Alvo(E, "ranking", "inserir"),),
    "oportunidade_empresa.registrada": (Alvo(E, "oportunidade_empresa", "inserir_ou_atualizar", ("id",)),),
    "vinculo_livro.registrado": (Alvo(E, "vinculo_livro", "inserir_ou_atualizar", ("cnpj", "livro_id", "papel")),),
    "aprofundamento.registrado": (Alvo(E, "aprofundamento", "inserir"),),
    # Migração do Eldorado0 (temporária): um lote de eventos dentro de um evento
    "importacao.lote": (Alvo("*", "*", "expandir"),),
}


class EventoInvalido(Exception):
    pass


_contador = 0
_trava = threading.Lock()


def novo_id() -> str:
    """Identificador que preserva a ordem de criação (nanossegundos + contador + sufixo aleatório)."""
    global _contador
    with _trava:
        _contador = (_contador + 1) % 1_000_000
        n = _contador
    return f"{time.time_ns():020d}-{n:06d}-{uuid.uuid4().hex[:8]}"


def agora() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def criar(tipo: str, modulo: str, dados: dict[str, Any], linhagem: Linhagem | None = None) -> Evento:
    if tipo not in CATALOGO:
        raise EventoInvalido(f"tipo de evento fora do catálogo: {tipo}")
    if not modulo:
        raise EventoInvalido("todo evento precisa do módulo que o emitiu")
    if not isinstance(dados, dict):
        raise EventoInvalido("os dados do evento devem ser um dicionário")
    return Evento(id=novo_id(), tipo=tipo, modulo=modulo, em=agora(), dados=dados, linhagem=linhagem or Linhagem())


def _converter(obj: Any) -> Any:
    """Números de bibliotecas numéricas (NumPy e afins) viram números comuns; o resto é erro (nunca descartado)."""
    item = getattr(obj, "item", None)
    if callable(item):
        return item()
    raise NotImplementedError(f"tipo não serializável no evento: {type(obj).__name__}")


_enc = msgspec.json.Encoder(enc_hook=_converter)
_dec = msgspec.json.Decoder(Evento)


RELEEM = {"importacao-eldorado0"}  # os diários de nome fixo que relêem o próprio histórico (ficam num arquivo só)
PARTE_MAX = 60 * 1024 * 1024  # 29/10/2026: acima disso, o diário abre a parte seguinte (<execução>-2.jsonl…): o GitHub
# recusa arquivo acima de 100 MB, e a gravação inteira caía (o Espião de 25/10 chegou a 99,9 MB)


class Diario:
    """Os eventos de uma execução, num arquivo que só recebe acréscimos (dividido em partes de até 60 MB)."""

    def __init__(self, pasta: str | Path, execucao: str | None = None):
        """Abre o diário de uma execução. Se a execução já tem diário (retomada), continua no mesmo arquivo."""
        self.pasta = Path(pasta)
        self.execucao = execucao or novo_id()
        # 29/10/2026: o diário de NOME FIXO (o Espião, o Interceptador, o Comandante, a máquina…) só escreve: vai para o
        # arquivo do dia (antes ficava no do primeiro dia em que foi criado: o do Espião de 25/10 chegou a 99,9 MB) e troca
        # de arquivo na virada do dia. O de execução (a passagem, que relê para retomar) e a importação seguem como antes.
        self.por_dia = bool(execucao) and not execucao[:1].isdigit() and execucao not in RELEEM
        self._dia = datetime.now(timezone.utc).date()
        existente = None
        if self.por_dia:
            hoje = self.pasta / f"{self._dia:%Y}" / f"{self._dia:%m}" / f"{self._dia:%d}" / f"{self.execucao}.jsonl"
            existente = hoje if hoje.exists() else None
        elif execucao and self.pasta.exists():
            existente = next(self.pasta.rglob(f"{self.execucao}.jsonl"), None)
        if existente:
            partes = sorted(existente.parent.glob(f"{self.execucao}-[0-9]*.jsonl"), key=lambda a: int(a.stem.rsplit("-", 1)[1]))
            self.arquivo = partes[-1] if partes else existente
        else:
            d = datetime.now(timezone.utc)
            self.arquivo = self.pasta / f"{d:%Y}" / f"{d:%m}" / f"{d:%d}" / f"{self.execucao}.jsonl"
        self.arquivo.parent.mkdir(parents=True, exist_ok=True)
        self._trava = threading.Lock()

    def _partes(self) -> list[Path]:
        base = self.arquivo.parent / f"{self.execucao}.jsonl"
        extras = sorted(self.arquivo.parent.glob(f"{self.execucao}-[0-9]*.jsonl"), key=lambda a: int(a.stem.rsplit("-", 1)[1]))
        return [a for a in [base, *extras] if a.exists()]

    def eventos(self) -> list[Evento]:
        """Os eventos já gravados nesta execução (todas as partes), na ordem."""
        evs = [_dec.decode(linha) for a in self._partes() for linha in a.read_bytes().splitlines() if linha.strip()]
        return sorted(evs, key=lambda e: e.id)

    def gravar(self, evento: Evento) -> Evento:
        linha = _enc.encode(evento) + b"\n"
        with self._trava:
            if self.por_dia and datetime.now(timezone.utc).date() != self._dia:  # a virada do dia: o arquivo do novo dia
                self._dia = datetime.now(timezone.utc).date()
                self.arquivo = self.pasta / f"{self._dia:%Y}" / f"{self._dia:%m}" / f"{self._dia:%d}" / f"{self.execucao}.jsonl"
                self.arquivo.parent.mkdir(parents=True, exist_ok=True)
            if self.arquivo.exists() and self.arquivo.stat().st_size + len(linha) > PARTE_MAX:
                n = len(self._partes()) + 1
                self.arquivo = self.arquivo.parent / f"{self.execucao}-{n}.jsonl"
        with self._trava, open(self.arquivo, "ab") as f:
            f.write(linha)
            f.flush()
            os.fsync(f.fileno())
        return evento

    def emitir(self, tipo: str, modulo: str, dados: dict[str, Any], linhagem: Linhagem | None = None) -> Evento:
        return self.gravar(criar(tipo, modulo, dados, linhagem))


def ler(pasta: str | Path, desde: float | None = None) -> Iterator[Evento]:
    """Lê os eventos da pasta, na ordem de criação. Linha corrompida levanta EventoInvalido (nunca é ignorada).
    desde (29/10/2026): só os arquivos modificados a partir desse instante (a aplicação dentro da passagem lia o histórico
    inteiro — ~600 mil eventos — em cada etapa de aplicar: a memória ia de 1,1 GB a 2,9 GB numa etapa)."""
    arquivos = sorted(a for a in Path(pasta).rglob("*.jsonl") if desde is None or a.stat().st_mtime >= desde)
    eventos: list[Evento] = []
    for a in arquivos:
        for n, linha in enumerate(a.read_bytes().splitlines(), 1):
            if not linha.strip():
                continue
            try:
                ev = _dec.decode(linha)
            except msgspec.DecodeError as e:
                raise EventoInvalido(f"{a.name}, linha {n}: {e}") from e
            if ev.tipo not in CATALOGO:
                raise EventoInvalido(f"{a.name}, linha {n}: tipo fora do catálogo: {ev.tipo}")
            eventos.append(ev)
    eventos.sort(key=lambda e: e.id)
    return iter(eventos)


_JA_EMITIDOS: dict[tuple[str, str], tuple[str, float]] = {}
_TRAVA_EMITIDOS = threading.Lock()


def emitir_se_mudou(
    diario: "Diario",
    tipo: str,
    modulo: str,
    chave: str,
    dados: dict[str, Any],
    renovar_s: float = 6 * 3600,
    ignorar: tuple[str, ...] = ("em", "criado_em"),
    chave_extra: str = "",
) -> bool:
    """29/10/2026 (titular: o banco não foi feito para regravar): grava o evento só quando o conteúdo mudou (ou a cada 6 h,
    como confirmação). O histórico crescia 35 MB por dia, ~80% de telemetria repetida a cada passagem (os mesmos 45 módulos
    recadastrados, as mesmas ~200 medições, as mesmas regras, a mesma memória); o dado dos livros é menos de 2 MB/dia."""
    import hashlib
    import time as _t

    conteudo = {k: v for k, v in dados.items() if k not in ignorar} | {"_faixa": chave_extra}
    h = hashlib.sha1(_enc.encode(conteudo)).hexdigest()
    k = (tipo, str(chave))
    agora_m = _t.monotonic()
    with _TRAVA_EMITIDOS:
        antes = _JA_EMITIDOS.get(k)
        if antes and antes[0] == h and agora_m - antes[1] < renovar_s:
            return False
        _JA_EMITIDOS[k] = (h, agora_m)
    diario.emitir(tipo, modulo, dados)
    return True
