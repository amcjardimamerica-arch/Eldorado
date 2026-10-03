"""MOTOR 04 — PNCP para organizações da sociedade civil (versão 2, 01/10/2026).

Parecer do conselho: docs/pareceres/motor-04-pncp.md. O que o motor antigo fazia e por que rendia zero:

1. O sensor genérico lia só as 3 primeiras das 11 URLs configuradas (`paginas_por_sensor` = 3): credenciamento de
   Goiás, páginas 1 e 2, e concurso de Goiás. Modalidade 10, Brasil e páginas seguintes nunca eram lidas.
2. Cada item virava "Credenciamento — órgão — objeto" e passava pela camada 1 com vetos como "com ou sem fins
   lucrativos", "prestação de serviços" e "aquisição" — que aparecem justamente nos chamamentos de OSC.
3. A "descoberta de listagem" seguia o link /app/editais/… (página de aplicação, sem conteúdo no HTML) como se
   fosse listagem: 4 leituras inúteis por execução e o diagnóstico "página institucional".
4. A API devolve 429 (limite de requisições) quando chamada em sequência rápida; o sensor contava como falha
   genérica e o dia ficava vermelho sem causa (07, 09, 14–17, 21 e 22/09).
5. Em paralelo, o coletor `src/coletores_api.py` gravava na base registros do PNCP de TODO o país, sem prazo
   (0 de 215 com data de encerramento), 206 fora de Goiás e muitos de 2024 — e o painel somava esses 215 ao motor.

Como funciona agora (sem IA, sem tokens, biblioteca-padrão):
  Fonte A — propostas abertas: /api/consulta/v1/contratacoes/proposta, por UF (Goiás) e modalidade (credenciamento,
            concurso, manifestação de interesse, pré-qualificação). Traz o objeto, a informação complementar e a
            DATA OFICIAL de encerramento das propostas — o prazo deixa de depender de expressão regular.
  Fonte B — busca do portal: /api/search/ com status "recebendo proposta", consultas dirigidas ao terceiro setor,
            em Goiás e nos órgãos FEDERAIS do país inteiro (MinC, MDS, Caixa, Correios…).
  → cada item é classificado (finalidade do PNCP em `src/pncp_terceiro_setor.py` + vetos e regimes do motor 03):
    OPORTUNIDADE · ACOMPANHAR · RUÍDO, sempre com o motivo escrito;
  → para cada OPORTUNIDADE, a lista de arquivos do órgão no PNCP dá o PDF do edital (documento oficial).

O PNCP é VETOR de descoberta: a URL do registro é a página do edital no PNCP e `url_documento` é o arquivo que o
próprio órgão anexou. Conteúdo coletado é DADO: injeção → quarentena; o que a API não diz fica `null`.
"""
from __future__ import annotations

import json
import os
import re
import time
from datetime import date, timedelta
from urllib.parse import urlencode

from . import atos_diario as atos
from . import diario_uniao as du
from . import pncp_terceiro_setor as pts
from .nucleo import (ROOT, append_jsonl, has_prompt_injection, load_json, now_iso, sha256,
                     validate_public_https, write_json)

MOTOR_ID = "pncp-api"
CFG = ROOT / "config/pncp_osc.json"
ESTADO = ROOT / "estado/pncp_osc.json"
QUARENTENA = ROOT / "estado/quarentena.jsonl"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 Eldorado-OSC/1.0"
BASE = "https://pncp.gov.br"
MODALIDADES = {1: "Leilão eletrônico", 2: "Diálogo competitivo", 3: "Concurso", 4: "Concorrência eletrônica",
               5: "Concorrência presencial", 6: "Pregão eletrônico", 7: "Pregão presencial", 8: "Dispensa",
               9: "Inexigibilidade", 10: "Manifestação de interesse", 11: "Pré-qualificação", 12: "Credenciamento",
               13: "Leilão presencial"}


class LimiteRequisicoes(RuntimeError):
    """HTTP 429 do PNCP — não é bloqueio: é ritmo. Espera e tenta de novo."""


_PRAZO = {"ate": None}          # prazo da execução inteira (o passo dos sensores tem tempo limite para todos os motores)


def _hoje_real() -> date:
    # 03/10 (teste do motor 15): o dia é o de Brasília — em UTC a passagem das 19h53+ virava o dia seguinte
    from datetime import datetime, timezone
    return datetime.now(timezone(timedelta(hours=-3))).date()


def _tempo_esgotado() -> bool:
    return _PRAZO["ate"] is not None and time.monotonic() > _PRAZO["ate"]


def _cfg() -> dict:
    return load_json(CFG) if CFG.exists() else {}


def _N(t) -> str:
    return atos.sem_acento(str(t or "")).upper()


def _get_json(url: str, timeout: int = 45, max_bytes: int = 8_000_000):
    """JSON da API. 204 (sem conteúdo) → None; 429 → LimiteRequisicoes; acima do limite → erro, nunca corte."""
    from urllib.error import HTTPError
    from urllib.request import Request, urlopen
    validate_public_https(url)
    req = Request(url, headers={"User-Agent": UA, "Accept": "application/json", "Accept-Language": "pt-BR,pt;q=0.9"})
    try:
        with urlopen(req, timeout=timeout) as r:
            if getattr(r, "status", 200) == 204:
                return None
            dados = r.read(max_bytes + 1)
    except HTTPError as exc:
        if exc.code == 429:
            raise LimiteRequisicoes("HTTP 429 — limite de requisições do PNCP") from exc
        raise
    if len(dados) > max_bytes:
        raise ValueError(f"resposta maior que {max_bytes // 1_000_000} MB")
    return json.loads(dados.decode("utf-8", "replace")) if dados.strip() else None


def _erro(exc: Exception) -> str:
    code = getattr(exc, "code", None)
    nome = type(exc).__name__
    causa = ("limite de requisições (HTTP 429) — ritmo, não bloqueio" if isinstance(exc, LimiteRequisicoes) else
             "bloqueio (HTTP 403)" if code == 403 else
             "tempo esgotado" if "Timeout" in nome or "timed out" in str(exc) else
             "endereço não resolve (DNS)" if nome == "gaierror" else
             f"HTTP {code}" if code else nome)
    return f"{causa}: {str(exc)[:90]}"


def _get(url: str, cfg: dict, tentativas: int | None = None):
    """Com o ritmo do PNCP: pausa entre chamadas; 429 espera e repete (até `tentativas_429`)."""
    ritmo = cfg.get("ritmo", {})
    tentativas = max(1, int(tentativas or ritmo.get("tentativas_429", 4)))
    ultimo = None
    for i in range(tentativas):
        if _tempo_esgotado():
            raise RuntimeError("prazo da execução esgotado — o restante fica para a próxima passagem")
        try:
            j = _get_json(url)
            time.sleep(float(ritmo.get("pausa_segundos", 1.5)))
            return j
        except LimiteRequisicoes as exc:
            ultimo = exc
            if i < tentativas - 1:
                time.sleep(float(ritmo.get("espera_429_segundos", 20)) * (i + 1))
        except Exception as exc:  # noqa: BLE001 — vira diagnóstico, nunca silêncio
            ultimo = exc
            if getattr(exc, "code", None) in (400, 403, 404) or isinstance(exc, ValueError):
                break
            if i < tentativas - 1:
                time.sleep(3 * (i + 1))
    raise RuntimeError(_erro(ultimo))


# ─────────────────────────── normalização dos itens ───────────────────────────
def _dia(s) -> str | None:
    m = re.match(r"(\d{4}-\d{2}-\d{2})", str(s or ""))
    return m.group(1) if m else None


def url_edital(cnpj: str, ano, seq) -> str:
    return f"{BASE}/app/editais/{cnpj}/{ano}/{int(seq)}"


def item_da_api(it: dict, fonte: str = "A") -> dict | None:
    """Item de /contratacoes/proposta ou /publicacao → forma comum."""
    org, uni = it.get("orgaoEntidade") or {}, it.get("unidadeOrgao") or {}
    cnpj = re.sub(r"\D", "", str(org.get("cnpj") or ""))
    ano, seq = it.get("anoCompra"), it.get("sequencialCompra")
    if not (cnpj and ano and seq):
        return None
    return {"controle": it.get("numeroControlePNCP") or f"{cnpj}-1-{int(seq):06d}/{ano}", "cnpj": cnpj, "ano": int(ano),
            "seq": int(seq), "titulo": (it.get("processo") and f"Processo {it.get('processo')}") or None,
            "objeto": (it.get("objetoCompra") or "").strip(), "info": (it.get("informacaoComplementar") or "").strip(),
            "orgao": (org.get("razaoSocial") or "").strip(), "unidade": (uni.get("nomeUnidade") or "").strip(),
            "uf": (uni.get("ufSigla") or "").upper() or None, "municipio": uni.get("municipioNome"),
            "esfera": org.get("esferaId"), "modalidade": it.get("modalidadeNome") or MODALIDADES.get(it.get("modalidadeId")),
            "modalidade_id": it.get("modalidadeId"), "abertura": _dia(it.get("dataAberturaProposta")),
            "encerramento": _dia(it.get("dataEncerramentoProposta")), "publicado": _dia(it.get("dataPublicacaoPncp")),
            "valor": it.get("valorTotalEstimado"), "amparo": ((it.get("amparoLegal") or {}).get("nome")),
            "url": url_edital(cnpj, ano, seq), "fonte": fonte}


def item_da_busca(x: dict, fonte: str = "B") -> dict | None:
    """Item de /api/search/ → forma comum (a busca já diz o município, a UF e a esfera)."""
    cnpj = re.sub(r"\D", "", str(x.get("orgao_cnpj") or ""))
    ano, seq = x.get("ano"), x.get("numero_sequencial")
    if not (cnpj and ano and seq):
        return None
    return {"controle": x.get("numero_controle_pncp") or f"{cnpj}-1-{int(seq):06d}/{ano}", "cnpj": cnpj, "ano": int(ano),
            "seq": int(seq), "titulo": (x.get("title") or "").strip() or None, "objeto": (x.get("description") or "").strip(),
            "info": (x.get("informacao_complementar") or "").strip(), "orgao": (x.get("orgao_nome") or "").strip(),
            "unidade": (x.get("unidade_nome") or "").strip(), "uf": (x.get("uf") or "").upper() or None,
            "municipio": x.get("municipio_nome"), "esfera": x.get("esfera_id"), "modalidade": x.get("modalidade_licitacao_nome"),
            "modalidade_id": int(x["modalidade_licitacao_id"]) if str(x.get("modalidade_licitacao_id") or "").isdigit() else None,
            "abertura": _dia(x.get("data_inicio_recebimento_propostas") or x.get("data_inicio_vigencia")),
            "encerramento": _dia(x.get("data_fim_recebimento_propostas") or x.get("data_fim_vigencia")),
            "publicado": _dia(x.get("data_publicacao_pncp") or x.get("createdAt")),
            "valor": x.get("valor_total_estimado") or x.get("valor_global"), "amparo": x.get("amparo_legal_nome"),
            "url": url_edital(cnpj, ano, seq), "fonte": fonte}


# ─────────────────────────── fontes ───────────────────────────
def fonte_a(hoje: date, cfg: dict, diag: dict) -> list[dict]:
    """Propostas abertas em Goiás (e nas UFs configuradas), por modalidade, com a data oficial de encerramento."""
    a = cfg.get("fonte_a", {})
    F = diag["fontes"]["A"]
    horizonte = (hoje + timedelta(days=int(a.get("horizonte_dias", 500)))).strftime("%Y%m%d")
    out = []
    seguidas, limite = 0, int(cfg.get("falhas_seguidas_para_abortar_fonte", 3))
    lista = cfg.get("_ufs_da_execucao") or a.get("ufs") or ["GO"]
    F["ufs_lidas"] = []
    for uf in lista:
        if cfg.get("_fim_fonte_a") and time.monotonic() > cfg["_fim_fonte_a"]:
            break                                   # 02/10: o resto dos estados fica para a próxima execução (rodízio)
        F["ufs_lidas"].append(uf)
        for mod in a.get("modalidades") or [12, 3, 10, 11]:
            # 03/10 (teste do motor 15): MG tem 53 páginas de credenciamento e SP 21; o teto de 20 cortava o resto sem
            # aviso. Agora cada UF/modalidade continua de onde parou (cursor) e o que faltar conta como leitura parcial
            cur = cfg.setdefault("_cursor_a", {}); chave_c = f"{uf}|{mod}"
            ini = int(cur.get(chave_c) or 1); ult, total = ini - 1, 0
            for pg in range(ini, ini + int(a.get("max_paginas", 20))):
                if seguidas >= limite:
                    break
                q = urlencode({"dataFinal": horizonte, "codigoModalidadeContratacao": mod, "uf": uf, "pagina": pg,
                               "tamanhoPagina": int(a.get("tamanho_pagina", 50))})
                try:
                    j = _get(f"{BASE}/api/consulta/v1/contratacoes/proposta?{q}", cfg)
                except RuntimeError as exc:
                    F["falhas"].append(f"{uf}/{MODALIDADES.get(mod, mod)} p{pg}: {exc}"); seguidas += 1; break
                seguidas = 0
                F["consultas"] += 1
                j = j if isinstance(j, dict) else {}
                for it in j.get("data") or []:
                    try:
                        m = item_da_api(it, "A")
                    except (TypeError, ValueError, AttributeError):
                        F["descartados"] = F.get("descartados", 0) + 1; continue
                    if m:
                        out.append(m)
                try:
                    total = int(j.get("totalPaginas") or 0)
                except (TypeError, ValueError):
                    total = 0
                ult = pg
                if pg >= total:
                    break
            if total and ult < total:
                cur[chave_c] = ult + 1
                F["cortados"] = F.get("cortados", 0) + (total - ult)
                F.setdefault("paginas_pendentes", []).append(f"{uf}/{MODALIDADES.get(mod, mod)}: páginas {ult + 1}–{total}")
            else:
                cur.pop(chave_c, None)
    F["itens"] = len(out)
    return out


def fonte_b(hoje: date, cfg: dict, diag: dict, vistos: set) -> list[dict]:
    """Busca do portal, só editais recebendo proposta: Goiás e órgãos federais do país inteiro."""
    b = cfg.get("fonte_b", {})
    if not b.get("usar", True):
        return []
    F = diag["fontes"]["B"]
    out = []
    seguidas, limite = 0, int(cfg.get("falhas_seguidas_para_abortar_fonte", 3))
    for escopo in b.get("escopos") or [{"ufs": "GO"}, {"esferas": "F"}]:
        for consulta in b.get("consultas") or []:
            for pg in range(1, int(b.get("max_paginas", 2)) + 1):
                if seguidas >= limite:
                    break
                q = urlencode({"q": consulta, "tipos_documento": "edital", "ordenacao": "-data", "pagina": pg,
                               "tam_pagina": int(b.get("tam_pagina", 100)), "status": "recebendo_proposta", **escopo})
                try:
                    j = _get(f"{BASE}/api/search/?{q}", cfg)
                except RuntimeError as exc:
                    F["falhas"].append(f"{consulta[:30]} {escopo}: {exc}"); seguidas += 1; break
                seguidas = 0
                F["consultas"] += 1
                j = j if isinstance(j, dict) else {}
                itens = j.get("items") or []
                for x in itens:
                    try:
                        m = item_da_busca(x, "B")
                    except (TypeError, ValueError, AttributeError):
                        F["descartados"] = F.get("descartados", 0) + 1; continue
                    if m and m["controle"] not in vistos:            # o que a Fonte A já trouxe entra igual: soma a fonte
                        vistos.add(m["controle"]); out.append(m)
                try:
                    total = int(j.get("total") or 0)
                except (TypeError, ValueError):
                    total = 0
                if not itens or pg * int(b.get("tam_pagina", 100)) >= total:
                    break
    F["itens"] = len(out)
    return out


def _livros_a_localizar(cfg: dict) -> list[dict]:
    """Livros cuja oportunidade ainda não tem chave no PNCP (consulta gravada no próprio livro, src/regras_restricao) e os
    registros do parecer das 238 que aguardam o ato oficial (dados/oportunidades/livros_parecer_238.json › aguardar)."""
    out = []
    try:
        ms = load_json(ROOT / "biblioteca_alexandria/fontes/motores.json").get("motores") or []
    except Exception:  # noqa: BLE001
        ms = []
    for x in ms:
        lx = (x.get("busca") or {}).get("lexico") or {}
        pn = lx.get("pncp") or {}
        if pn.get("consulta") and not pn.get("chave") and lx.get("municipio"):
            out.append({"id": x["id"], "consulta": pn["consulta"], "uf": pn.get("ufs"), "municipio": lx["municipio"],
                        "numeros": lx.get("numeros") or [], "termos": lx.get("termos") or []})
    try:
        sem = load_json(ROOT / "dados/oportunidades/livros_parecer_238.json").get("aguardar") or []
    except Exception:  # noqa: BLE001
        sem = []
    for e in sem:
        if e.get("consulta") and e.get("municipio"):
            out.append({"id": "semente-" + str(e.get("registro")), "consulta": e["consulta"], "uf": e.get("uf"), "municipio": e["municipio"],
                        "numeros": e.get("numeros") or [], "termos": e.get("termos") or []})
    return out


def fonte_c(hoje: date, cfg: dict, diag: dict, vistos: set, est: dict) -> list[dict]:
    """02/10 (titular): o PNCP é o agregador dos editais de OSC do Brasil inteiro. Fonte C procura, com o LÉXICO DE CADA
    LIVRO, o ato no PNCP dos livros que ainda não têm chave (ex.: edital de outro município achado em diário oficial).
    Casa só no mesmo município (e no número do edital, quando o livro tem número); grava {livro: chave} em
    estado/pncp_osc.json › livros_pncp, que o ciclo dos livros leva ao livro."""
    c = cfg.get("fonte_c") or {}
    if not c.get("usar", True):
        return []
    F = diag["fontes"].setdefault("C", {"falhas": [], "consultas": 0, "itens": 0, "localizados": 0})
    fila = _livros_a_localizar(cfg)
    achados = est.setdefault("livros_pncp", {})
    sem = est.setdefault("livros_sem_pncp", {})
    reler = (hoje - timedelta(days=int(c.get("reler_sem_registro_dias", 7)))).isoformat()
    fila = [l for l in fila if l["id"] not in achados and str(sem.get(l["id"]) or "") <= reler]
    if not fila:
        return []
    k = int(est.get("cursor_fonte_c") or 0) % len(fila)
    fila = (fila[k:] + fila[:k])[: int(c.get("max_livros_por_execucao", 10))]
    est["cursor_fonte_c"] = k + len(fila)
    out = []
    for l in fila:
        if _tempo_esgotado():
            break
        q = urlencode({"q": l["consulta"], "tipos_documento": "edital", "ordenacao": "-data", "pagina": 1,
                       "tam_pagina": int(c.get("tam_pagina", 100)), **({"ufs": l["uf"]} if l.get("uf") else {})})
        try:
            j = _get(f"{BASE}/api/search/?{q}", cfg)
        except RuntimeError as exc:
            F["falhas"].append(f"livro {l['id']}: {exc}"); continue
        F["consultas"] += 1
        melhor = None
        termos = [_N(t) for t in l.get("termos") or [] if t and _N(t) not in _N(l["municipio"]).split()]
        for x in (j.get("items") if isinstance(j, dict) else None) or []:
            if _N(x.get("municipio_nome")) != _N(l["municipio"]):
                continue
            m = item_da_busca(x, "C")
            if not m:
                continue
            T = _N(" ".join(str(m.get(k) or "") for k in ("titulo", "objeto", "info")))
            if not _OSC_FORTE.search(T) and not re.search(r"\bPNAB\b|ALDIR BLANC|TERMO DE EXECUCAO CULTURAL|AGENTES? CULTURA", T):
                continue                                   # revisão 02/10: só ato de OSC/fomento (não leiloeiro, compra, monitor)
            num = any(re.search(rf"(?<![\d/])0*{int(n.split('/')[0])}\s*/\s*{n.split('/')[1]}(?![\d/])", T) for n in l["numeros"])
            if l["numeros"] and not num:
                continue                                   # o livro tem número: só o mesmo número serve
            casados = sum(1 for t in termos if t in T)
            if not l["numeros"] and casados < 2:
                continue                                   # sem número: exige dois termos distintivos do livro
            if classificar_item(m, hoje, TODAS_UFS)["veredito"] == "RUIDO":
                continue                                   # o classificador do motor 04 tem a palavra final
            nota = 10 * num + casados
            if not melhor or nota > melhor[0]:
                melhor = (nota, m)
        if melhor:
            achados[l["id"]] = f"pncp:{melhor[1]['cnpj']}/{melhor[1]['ano']}/{melhor[1]['seq']}"
            F["localizados"] += 1; sem.pop(l["id"], None)
            if melhor[1]["controle"] not in vistos:
                vistos.add(melhor[1]["controle"]); out.append(melhor[1])
        else:
            sem[l["id"]] = hoje.isoformat()          # não está no PNCP (MROSC não obriga): tenta de novo em 7 dias
    est["livros_pncp"] = achados
    F["itens"] = len(out)
    return out


def documento_oficial(m: dict, cfg: dict) -> str | None:
    """O PDF que o órgão anexou no PNCP (vale como documento oficial): prefere o que se chama "edital"."""
    try:
        arqs = _get(f"{BASE}/pncp-api/v1/orgaos/{m['cnpj']}/compras/{m['ano']}/{m['seq']}/arquivos", cfg, tentativas=2) or []
    except RuntimeError:
        return None
    ativos = [a for a in arqs if isinstance(a, dict) and a.get("statusAtivo", True) and (a.get("url") or a.get("uri"))]
    if not ativos:
        return None
    melhor = next((a for a in ativos if re.search(r"EDITAL", _N(a.get("titulo")) + " " + _N(a.get("tipoDocumentoNome")))), ativos[0])
    u = melhor.get("url") or melhor.get("uri")
    return re.sub(r"^https://pncp\.gov\.br:\d+/", f"{BASE}/", u)       # a API devolve a porta interna (50439)


# ─────────────────────────── classificação ───────────────────────────
VETOS_PNCP = [
    ("contratacao_de_empresa", re.compile(r"CONTRATACAO DA EMPRESA|\b[A-Z][A-Z ]{3,60} LTDA\b|\bEIRELI\b|SOCIEDADE EMPRESARIA"),
     "contratação de empresa determinada — não é seleção de OSC", False),
    ("conselho_profissional", re.compile(r"^CONS(?:ELHO)?\.? (?:REG(?:IONAL)?|FEDERAL)\b|^CONSELHO REG"),
     "conselho profissional (autarquia de fiscalização) — chamamentos locais, fora do escopo da associação", False),
    ("credenciamento_servico", re.compile(
        r"CREDENCIAMENTO (?:PARA (?:A )?CONTRATACAO|PARA PROFISSIONA|D[EOA]S? (?:PESSOAS? (?:FISICAS?|JURIDICAS?)|INSTITUICOES PRIVADAS|"
        r"ENTIDADES PUBLICAS|PRESTADORES|PROFISSIONAIS|CLINICAS|LABORATORIOS|HOSPITAIS|LEILOEIROS|EMPRESAS|MEDIC|ORGANIZACOES CIVIS DE SAUDE))"),
     "credenciamento de prestador para contrato de serviço (Lei 14.133, art. 79) — não é fomento a OSC", "mrosc"),
    ("saude_complementar", re.compile(r"COMPLEMENTAR (?:AO|DO|DE) (?:SUS|SISTEMA UNICO)|SERVICOS? (?:DE SAUDE|MEDICOS|ODONTOLOGICOS|HOSPITALARES|"
                                      r"DE ENFERMAGEM|AMBULATORIAIS|LABORATORIAIS)|PROCEDIMENTOS (?:MEDICOS|CIRURGICOS|AMBULATORIAIS)|"
                                      r"EXAMES (?:DE|LABORATORIAIS|DE IMAGEM)|CONSULTAS (?:MEDICAS|ESPECIALIZADAS|ODONTOLOGICAS)|PLANTOES|"
                                      r"PROFISSIONA(?:L|IS) DE SAUDE|ULTRASSONOGRAF|ENFERMEIR|FISIOTERAPEUT|VETERINARI|MEDICINA DO TRABALHO|"
                                      r"PERICIA MEDICA"),
     "serviço de saúde contratado (rede complementar do SUS) — contrato de prestação, não fomento", "mrosc"),
    ("organizacao_social", re.compile(r"QUALIFICACAO (?:DE (?:ENTIDADES|PESSOAS JURIDICAS)[^.]{0,80})?COMO ORGANIZAC(?:AO|OES) SOCIA|"
                                      r"CONTRATO DE GESTAO|QUALIFICACAO DE PESSOAS JURIDICAS"),
     "qualificação de Organização Social / contrato de gestão — não é edital MROSC para associação", False),
    ("servico_ao_orgao", re.compile(r"LAVAGEM D|LOCACAO DE (?:VEICULO|MAQUINA|EQUIPAMENTO|IMOVE)|TRANSPORTE (?:ESCOLAR|DE PACIENTES)|"
                                    r"FORNECIMENTO DE|AQUISICAO DE|REGISTRO DE PRECOS|AGENCIAMENTO|SERVICOS FUNERARIOS|COMBUSTIVE|"
                                    r"HOSPEDAGEM|ALIMENTACAO (?:PARA|DOS) SERVIDORES|LEILOEIRO|SERVICOS DE PUBLICIDADE|AGENCIA DE PUBLICIDADE|CONSIGNA|"
                                    r"PROCESSAMENTO DE DADOS|TROFEU|MATERIAIS (?:E ACESSORIOS )?ESPORTIVOS|UNIFORMES"),
     "serviço, compra ou locação para o próprio órgão — não é fomento a OSC", True),
    ("inovacao_competicao", re.compile(r"PROJETOS INOVADORES|SANDBOX|AMBIENTE REGULATORIO|STARTUPS?\b|HACKATHON|HACKATUR|"
                                       r"SELECAO DE PARTICIPANTES|CONCURSO ACADEMICO|TRABALHOS ACADEMICOS"),
     "inovação, startup ou competição de participantes — não é recurso para associação", False),
]
# modalidades de CONTRATAÇÃO (preço, compra, contrato direto): só entram com instrumento MROSC explícito
MODALIDADE_CONTRATACAO = re.compile(r"PREGAO|CONCORRENCIA|LEILAO|DISPENSA|INEXIGIBILIDADE|DIALOGO COMPETITIVO")
_ENTIDADE_PRESTADORA = re.compile(r"(?:ENTIDADES|INSTITUICOES) (?:DE ASSISTENCIA SOCIAL|PRIVADAS SEM FINS|FILANTROPICAS|SEM FINS|"
                                  r"DE LONGA PERMANENCIA)|\bILPI\b|"
                                  r"INSTITUICOES PRIVADAS,? (?:COM OU )?SEM FINS")
_MROSC_FORTE = re.compile(r"13\.019|TERMO DE (?:FOMENTO|COLABORACAO)|MROSC|ACORDO DE COOPERACAO|TERMO DE EXECUCAO CULTURAL")
_OSC_FORTE = re.compile(r"13\.019|TERMO DE (?:FOMENTO|COLABORACAO)|ORGANIZAC(?:AO|OES) DA SOCIEDADE CIVIL|\bOSCS?\b|MROSC|"
                        r"ASSOCIAC(?:AO|OES) (?:DE )?ESTUDANT|GREMIOS? ESTUDANT|CENTROS? ACADEMIC|\bILPIS?\b|LONGA PERMANENCIA|"   # 02/10: também são OSC
                        r"COOPERATIVAS? (?:E|OU|/)? ?ASSOCIAC(?:AO|OES) DE CATADORES|ASSOCIAC(?:AO|OES) DE CATADORES|"
                        r"ACORDO DE COOPERACAO|ENTIDADES? (?:SOCIOASSISTENCIA|DE ASSISTENCIA SOCIAL)|\bCMAS\b|\bCMDCA\b|PNAB|"
                        r"ALDIR BLANC|PAULO GUSTAVO|AGENTES? CULTURA|PONTOS? DE CULTURA")


def _vetos():
    """Os vetos do PNCP vêm antes; depois os do motor 03 que fazem sentido aqui (bolsa, imóvel, apoio ao órgão…).
    No PNCP o "concurso" é modalidade de prêmio (Lei 14.133, art. 30): só o concurso PÚBLICO DE PROVAS é seleção de pessoal."""
    acad = next(v for v in du.VETOS_BR if v[0] == "selecao_academica")
    acad_pncp = ("selecao_academica", re.compile(acad[1].pattern.replace("CONCURSO PUBLICO|",
                                                                         "CONCURSO PUBLICO (?:DE PROVAS|PARA (?:PROVIMENTO|O CARGO|CARGOS))|")),
                 acad[2], acad[3])
    usar = {"selecao_pessoas", "apoio_ao_orgao", "imovel", "empresas_servicos", "credenciamento_prestadores",
            "empresas_credenciamento", "pesquisa_contratada", "selecao_familias", "participacao_publica", "consulta_publica",
            "pesquisa_clinica", "empreendedorismo"}
    _base = VETOS_PNCP + [acad_pncp] + [v for v in du.VETOS_BR if v[0] in usar]
    # 02/10: vetos do Brasil inteiro (falsos positivos da primeira leitura nacional) — config/pncp_osc.json › vetos_nacionais
    extra = [(v[0], re.compile(v[1]), v[2], bool(v[3] if len(v) > 3 else False)) for v in (_cfg().get("vetos_nacionais") or [])]
    return extra + list(_base)


TODAS_UFS = ["GO", "DF", "AC", "AL", "AP", "AM", "BA", "CE", "ES", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS",
             "RO", "RR", "SC", "SP", "SE", "TO"]


def territorio(m: dict, ufs: list[str]) -> tuple[str, str, str | None]:
    """(nível, território, aviso). Municipal/estadual fora das UFs configuradas → "fora"."""
    uf = m.get("uf")
    if m.get("esfera") == "F":
        if uf and uf not in set(ufs) | {"DF"}:
            return "federal", "BR", f"órgão federal sediado em {uf} — conferir se a seleção é nacional"
        return "federal", "BR", None
    if uf and uf not in ufs:
        return ("municipal" if m.get("esfera") == "M" else "estadual"), "fora", None
    if m.get("esfera") == "M" or (m.get("esfera") not in ("E", "D") and m.get("municipio")):
        return "municipal", f"{uf}/{m.get('municipio')}" if m.get("municipio") else (uf or "BR"), None
    return "estadual", uf or "BR", None


def classificar_item(m: dict, hoje: date, ufs: list[str] | None = None) -> dict:
    """Um edital do PNCP → OPORTUNIDADE · ACOMPANHAR · RUÍDO, com o motivo escrito.

    1. território (Goiás ou órgão federal) · 2. vetos (empresa, prestador, SUS, OS, serviço ao órgão, bolsa…)
    3. sinal de terceiro setor (classificador de finalidade do PNCP + regimes do motor 03) · 4. prazo oficial."""
    ufs = ufs or ["GO"]
    texto = " ".join(x for x in (m.get("titulo"), m.get("objeto"), m.get("info")) if x)
    T = _N(texto)
    nivel, terr, aviso = territorio(m, ufs)
    base = {"nivel": nivel, "territorio": terr, "fim": m.get("encerramento"), "regime": None, "finalidade": None,
            "pertinencia": "nula", "motivos": [], "sinais": []}
    if terr == "fora":
        return {**base, "veredito": "RUIDO", "motivos": [f"{m.get('orgao') or 'órgão'} ({m.get('uf')}) — fora do território da associação"]}
    forte, mrosc = bool(_OSC_FORTE.search(T)), bool(_MROSC_FORTE.search(T))
    O = _N(m.get("orgao"))
    for nome, rx, motivo, cede in _vetos():
        alvo = O if nome == "conselho_profissional" else T
        cedeu = (cede == "mrosc" and mrosc) or (cede is True and forte)
        if rx.search(alvo) and not cedeu:
            if nome in ("credenciamento_servico", "saude_complementar") and _ENTIDADE_PRESTADORA.search(T) \
                    and not re.search(r"EMPRESAS? ESPECIALIZADA|PROFISSIONA(?:L|IS)|PESSOAS? FISICA", T):
                # 02/10 (titular): ILPI, acolhimento e outras OSC prestadoras também são OSC — a oportunidade é mapeada
                # (identificar primeiro); o enquadramento fica anotado e a decisão de concorrer é do Farol, por associação
                return {**base, "veredito": "OPORTUNIDADE", "regime": "credenciamento_de_entidade",
                        "enquadramento": "EN-03 — credenciamento de OSC para prestar serviço (contratação pela Lei 14.133, não fomento MROSC)",
                        "motivos": ["credenciamento de entidade sem fins lucrativos para prestar serviço (acolhimento, ILPI, saúde) — "
                                    "oportunidade para a OSC que presta o serviço; enquadramento técnico anotado"]}
            return {**base, "veredito": "RUIDO", "regime": nome, "motivos": [motivo]}
    fin = pts.classificar(m.get("objeto") or "", " ".join(x for x in (m.get("titulo"), m.get("info")) if x))
    extra = next((nome for nome, rx in du.REGIMES_BR if rx.search(T)), None)
    if re.search(r"CATADOR|RECICLA", T) and extra in (None, "doacao_bens"):
        extra = "coleta_seletiva_solidaria"              # "doação dos recicláveis" é coleta solidária, não doação de bens
    if MODALIDADE_CONTRATACAO.search(_N(m.get("modalidade"))) and not mrosc and extra != "aprendizagem_esfl":
        return {**base, "veredito": "RUIDO", "regime": "contratacao_publica",
                "motivos": [f"modalidade de contratação ({m.get('modalidade')}) sem instrumento MROSC — compra ou contrato, não seleção de OSC"]}
    if extra in du.REGIMES_LOCAIS and not re.search(r"ENTIDADES?|ASSOCIAC|COOPERATIVA|INSTITUIC(?:AO|OES)[^.]{0,30}SEM FINS|OSC", T):
        extra = None                                     # doação/coleta sem entidade como destinatária
    if not fin["terceiro_setor"] and not extra and not forte and "CREDENCIAMENTO" in T and _ENTIDADE_PRESTADORA.search(T):
        return {**base, "veredito": "OPORTUNIDADE", "regime": "credenciamento_de_entidade",   # 02/10 (titular): mapeada, com enquadramento
                "enquadramento": "EN-03 — credenciamento de OSC para prestar serviço (contratação pela Lei 14.133, não fomento MROSC)",
                "motivos": ["credenciamento de entidade sem fins lucrativos para prestar serviço (acolhimento, ILPI, saúde) — "
                            "oportunidade para a OSC que presta o serviço; enquadramento técnico anotado"]}
    if not fin["terceiro_setor"] and not extra and not forte:
        return {**base, "veredito": "RUIDO", "regime": "contratacao_publica",
                "motivos": [f"{fin['finalidade']} — {fin['porque']}"]}
    regime = (extra or {"parceria com OSC (MROSC)": "mrosc", "fomento ou prêmio cultural": "pnab_cultura",
                        "fundo ou conselho de direitos": "fundo_conselho", "seleção de entidade sem fins lucrativos": "entidade_sem_fins",
                        "fomento a projeto": "fomento"}.get(fin["finalidade"]) or "mrosc")
    base.update({"regime": regime, "finalidade": fin["finalidade"] if fin["terceiro_setor"] else (extra or "parceria com OSC"),
                 "pertinencia": fin["pertinencia"] if fin["terceiro_setor"] else "media",
                 "sinais": sorted((fin.get("sinais") or {}).get("positivo", {}).keys())})
    fim = m.get("encerramento")
    velho = bool(m.get("publicado")) and m["publicado"] < (hoje - timedelta(days=60)).isoformat()
    if regime in du.REGIMES_LOCAIS and m.get("uf") and m.get("uf") not in set(ufs) | {"DF"}:
        return {**base, "veredito": "RUIDO", "motivos": [f"doação ou coleta com entrega física em {m.get('uf')} — fora de Goiás e do DF"]}
    if fim and fim < hoje.isoformat():
        return {**base, "veredito": "ACOMPANHAR", "motivos": [f"seleção de interesse, mas as propostas encerraram em {fim}"]}
    if not fim and velho:
        return {**base, "veredito": "ACOMPANHAR",
                "motivos": [f"seleção de interesse publicada em {m['publicado']} sem data de encerramento no PNCP — conferir no edital"]}
    if aviso:
        return {**base, "veredito": "ACOMPANHAR", "motivos": [aviso]}
    mot = f"seleção aberta para OSC ({base['finalidade']})" + (f", propostas até {fim}" if fim else ", sem data de encerramento no PNCP — conferir no edital")
    return {**base, "veredito": "OPORTUNIDADE", "motivos": [mot]}


def _registro(c: dict, m: dict) -> dict:
    ev = atos.mascarar_pii(re.sub(r"\s+", " ", " ".join(x for x in (m.get("titulo"), m.get("objeto"), m.get("info")) if x)))[:700]
    orgao = m.get("orgao") or "órgão público"
    return {
        "id": sha256(f"pncp|{m['controle']}".encode())[:20], "status": "capturada",
        "titulo": f"{orgao} — {(m.get('objeto') or m.get('titulo') or '')[:220]}"[:300], "url": m["url"],
        "url_documento": m.get("url_documento"), "fonte_id": MOTOR_ID, "fonte_nome": f"PNCP — {orgao}"[:120],
        "territorio": c["territorio"], "uf": m.get("uf"), "nivel": c["nivel"],
        "municipio": f"{m['uf']}/{m['municipio']}" if m.get("uf") and m.get("municipio") else None,
        "tipo_fonte": "api_oficial_pncp", "confianca": "primaria", "forma_divulgacao": "pncp",
        "coletado_em": now_iso(), "data_publicacao": m.get("publicado"), "abertura_propostas": m.get("abertura"),
        "fim": c["fim"], "prazo_texto": c["fim"], "valor_texto": (f"R$ {m['valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                                                              if isinstance(m.get("valor"), (int, float)) and m["valor"] else None),
        "objeto": (m.get("objeto") or "")[:600] or None, "orgao": orgao, "unidade": m.get("unidade") or None,
        "numero_controle_pncp": m["controle"], "modalidade_pncp": m.get("modalidade"), "amparo_legal": m.get("amparo"),
        "regime": c["regime"], "finalidade_pncp": c["finalidade"], "pertinencia_pncp": c["pertinencia"],
        "evidencia": ev, "hash_evidencia": sha256(ev.encode()), "fontes_observadas": [m["fonte"]],
        "classificacao_ato": {k: c[k] for k in ("veredito", "regime", "motivos", "sinais")} | {"tipo": "abertura"},
        "sensor": MOTOR_ID, "forca_lexica": 3,
    }


def classificar_lote(itens: list[dict], hoje: date, ufs: list[str] | None = None) -> tuple[dict, dict, dict]:
    """→ ({id: OPORTUNIDADE}, {id: ACOMPANHAR}, contagens) — um registro por número de controle do PNCP."""
    oport, acomp = {}, {}
    cont = {"OPORTUNIDADE": 0, "ACOMPANHAR": 0, "RUIDO": 0, "quarentena": 0}
    vistos: dict[str, dict] = {}
    for m in itens:                                           # A e B podem trazer o mesmo edital: A tem o prazo oficial
        ant = vistos.get(m["controle"])
        if ant:
            ant["fontes"] = sorted(set(ant["fontes"]) | {m["fonte"]})
            for k in ("encerramento", "info", "abertura", "valor", "publicado"):
                ant[k] = ant.get(k) or m.get(k)
            continue
        vistos[m["controle"]] = dict(m, fontes=[m["fonte"]])
    for m in vistos.values():
        bruto = " ".join(str(m.get(k) or "") for k in ("titulo", "objeto", "info"))
        if has_prompt_injection(bruto):
            append_jsonl(QUARENTENA, {"origem": MOTOR_ID, "url": m.get("url"), "em": now_iso(), "hash": sha256(bruto.encode())[:16]})
            cont["quarentena"] += 1; continue
        c = classificar_item(m, hoje, ufs)
        cont[c["veredito"]] += 1
        if c["veredito"] == "RUIDO":
            continue
        r = _registro(c, m)
        r["fontes_observadas"] = m["fontes"]
        (oport if c["veredito"] == "OPORTUNIDADE" else acomp)[r["id"]] = r
    return oport, acomp, cont


# ─────────────────────────── o motor ───────────────────────────
def ler_motor(sensor: dict | None = None, hoje: date | None = None, limites: dict | None = None) -> dict:
    """Leitura do motor 04 com a mesma saída de `sensores.ler`."""
    pedido = hoje or (sensor or {}).get("_data")
    hoje = _hoje_real() if pedido is None else pedido
    if pedido is not None and pedido < _hoje_real():
        # o PNCP é lido pelo que está ABERTO hoje: não há "edição" de um dia passado para reler
        return {"sensor": MOTOR_ID, "achados": [], "falhas": [], "saude": [], "lido_em": now_iso(),
                "diagnostico": {"paginas_lidas": 0, "links_total": 0, "links_candidatos": 0, "descobertas": [], "pdf_links": 0,
                                "motivo_zero": "o motor 04 lê as propostas abertas de hoje; dia passado não é relido", "retroativo": True}}
    cfg = _cfg()
    ufs = list((cfg.get("fonte_a") or {}).get("ufs") or ["GO"])
    _PRAZO["ate"] = time.monotonic() + float(cfg.get("prazo_total_segundos", 420))
    est = load_json(ESTADO) if ESTADO.exists() else {}
    if "*" in ufs:                                  # 02/10 (titular): Brasil inteiro — Goiás e DF primeiro, depois rodízio
        ab = cfg.get("abrangencia") or {}
        prio = [u for u in ab.get("prioridade") or ["GO", "DF"] if u in TODAS_UFS]
        resto = [u for u in TODAS_UFS if u not in prio]
        k = int(est.get("rodizio_ufs") or 0) % len(resto)
        cfg["_ufs_da_execucao"] = prio + resto[k:] + resto[:k]
        cfg["_fim_fonte_a"] = time.monotonic() + float(cfg.get("prazo_total_segundos", 420)) * float(ab.get("parte_do_tempo_fonte_a", 0.65))
        ufs = list(TODAS_UFS)                       # o classificador não descarta nenhum estado
    diag = {"paginas_lidas": 0, "links_total": 0, "links_candidatos": 0, "descobertas": [], "pdf_links": 0, "motivo_zero": None,
            "versao": "motor-04 v2 (01/10/2026)",
            "fontes": {"A": {"falhas": [], "consultas": 0, "itens": 0}, "B": {"falhas": [], "consultas": 0, "itens": 0}}}
    itens = []
    cfg["_cursor_a"] = dict(est.get("cursor_fonte_a") or {})
    try:
        itens += fonte_a(hoje, cfg, diag)
    except Exception as exc:  # noqa: BLE001 — uma fonte nunca derruba a outra
        diag["fontes"]["A"]["falhas"].append(f"etapa: {_erro(exc)}")
    if cfg.get("_ufs_da_execucao"):
        lidas = [u for u in diag["fontes"]["A"].get("ufs_lidas") or [] if u not in ("GO", "DF")]
        est["rodizio_ufs"] = int(est.get("rodizio_ufs") or 0) + max(0, len(lidas) - 1)
        diag["rodizio"] = {"ufs_lidas": diag["fontes"]["A"].get("ufs_lidas"), "proxima_comeca_em": None}
        # 03/10: estados lidos no DIA (3 passagens). Faltando algum, o maestro vê leitura parcial e dispara de novo
        dia = est.get("ufs_do_dia") or {}
        if dia.get("data") != hoje.isoformat():
            dia = {"data": hoje.isoformat(), "ufs": []}
        dia["ufs"] = sorted(set(dia["ufs"]) | set(diag["fontes"]["A"].get("ufs_lidas") or []))
        est["ufs_do_dia"] = dia
        faltam = [u for u in TODAS_UFS if u not in dia["ufs"]]
        diag["rodizio"]["faltam_no_dia"] = faltam
        if faltam:
            diag["paginas_nao_lidas"] = [f"propostas abertas — {u}" for u in faltam]
    est["cursor_fonte_a"] = cfg.get("_cursor_a") or {}
    if diag["fontes"]["A"].get("cortados"):
        diag["cortados"] = diag["fontes"]["A"]["cortados"]
    try:
        itens += fonte_b(hoje, cfg, diag, set())
    except Exception as exc:  # noqa: BLE001
        diag["fontes"]["B"]["falhas"].append(f"etapa: {_erro(exc)}")
    try:                                            # 02/10: Fonte C — o léxico de cada livro procura o ato no PNCP
        itens += fonte_c(hoje, cfg, diag, {x["controle"] for x in itens}, est)
    except Exception as exc:  # noqa: BLE001
        diag["fontes"].setdefault("C", {"falhas": []})["falhas"].append(f"etapa: {_erro(exc)}")
    oport, acomp, cont = classificar_lote(itens, hoje, ufs)
    # documento oficial (PDF do edital anexado pelo órgão) para as oportunidades novas
    docs = est.setdefault("documentos", {})
    novos = [r for r in oport.values() if not docs.get(r["numero_controle_pncp"])][: int(cfg.get("max_documentos_por_execucao", 25))]
    por_controle = {x["controle"]: x for x in itens}
    for r in novos:
        u = documento_oficial(por_controle[r["numero_controle_pncp"]], cfg)
        if u:                                             # falhou (429, rede)? tenta de novo na próxima passagem
            docs[r["numero_controle_pncp"]] = u
    for r in oport.values():
        r["url_documento"] = docs.get(r["numero_controle_pncp"])
    A, B = diag["fontes"]["A"], diag["fontes"]["B"]
    diag.update({"vereditos": cont, "paginas_lidas": A["consultas"] + B["consultas"], "links_total": len(itens),
                 "links_candidatos": cont["OPORTUNIDADE"] + cont["ACOMPANHAR"]})
    leu = A["consultas"] > 0 or B["consultas"] > 0
    d0 = hoje.isoformat()
    hist = est.setdefault("historico", {})
    hist[d0] = {"consultas_A": A["consultas"], "consultas_B": B["consultas"], "itens": len(itens), **cont,
                "falhou": not leu}
    seq, d = 0, hoje
    for _ in range(30):
        h = hist.get(d.isoformat())
        if not h or not h.get("falhou"):
            break
        seq += 1; d -= timedelta(days=1)
    if seq >= 2:
        diag["alerta"] = f"{seq} dias seguidos sem resposta da API do PNCP — " + (A["falhas"] + B["falhas"] + ["sem causa"])[0]
    corte = (hoje - timedelta(days=120)).isoformat()
    est["acompanhar"] = sorted(({k: a.get(k) for k in ("id", "titulo", "url", "data_publicacao", "fim", "orgao", "regime", "territorio")}
                                | {"motivo": a["classificacao_ato"]["motivos"][0]} for a in acomp.values()),
                               key=lambda a: str(a.get("data_publicacao") or ""), reverse=True)[:300]
    est["abertas"] = sorted(({k: r.get(k) for k in ("id", "titulo", "url", "url_documento", "fim", "orgao", "territorio", "regime")}
                             for r in oport.values()), key=lambda r: str(r.get("fim") or "9999"))
    est["documentos"] = {k: v for k, v in docs.items() if v and k in {r["numero_controle_pncp"] for r in oport.values()}}
    est["ultima"] = {"em": now_iso(), "data": d0, "vereditos": cont, "falhas": (A["falhas"] + B["falhas"])[:10]}
    est["historico"] = {k: v for k, v in hist.items() if k >= corte}
    write_json(ESTADO, est)
    _PRAZO["ate"] = None
    falhas = [{"url": BASE + "/api/consulta", "erro": "pncp", "code": None, "waf": None, "causa": f} for f in (A["falhas"] + B["falhas"])[:6]]
    saude = ([{"url": BASE + "/api/consulta/v1/contratacoes/proposta", "http": 200, "bytes": A["itens"]}] if A["consultas"] else []) + \
            ([{"url": BASE + "/api/search/", "http": 200, "bytes": B["itens"]}] if B["consultas"] else [])
    if not oport:
        diag["motivo_zero"] = (f"{len(itens)} editais recebendo proposta lidos (A {A['itens']} · B {B['itens']}): nenhuma seleção "
                               f"aberta para OSC · {cont['ACOMPANHAR']} a acompanhar · {cont['RUIDO']} ruído"
                               if leu else "a API do PNCP não respondeu: " + (falhas[0]["causa"] if falhas else "sem leitura"))
    return {"sensor": MOTOR_ID, "achados": sorted(oport.values(), key=lambda r: str(r.get("fim") or "9999")), "falhas": falhas,
            "saude": saude, "diagnostico": diag, "lido_em": now_iso()}


def atos_para_painel(limite: int = 12) -> list[dict]:
    est = load_json(ESTADO) if ESTADO.exists() else {}
    return (est.get("acompanhar") or [])[:limite]


if __name__ == "__main__":
    print(json.dumps(ler_motor()["diagnostico"], ensure_ascii=False, indent=2))
